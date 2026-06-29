import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "chatbot.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database tables and handle schema migration."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Create sessions table with both persona (old) and persona_key (new)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                persona TEXT NOT NULL,               -- kept for compatibility
                persona_key TEXT NOT NULL,           -- new column
                persona_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # For existing databases that might lack persona_key
        cursor.execute("PRAGMA table_info(sessions)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'persona_key' not in columns:
            cursor.execute("ALTER TABLE sessions ADD COLUMN persona_key TEXT")
            # Copy data from old 'persona' to 'persona_key'
            if 'persona' in columns:
                cursor.execute("UPDATE sessions SET persona_key = persona")
            else:
                # If 'persona' doesn't exist, we need to set a default – unlikely.
                pass

        # Create messages and context tables (unchanged)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                sender TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                sender TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)


def get_sessions(conn, persona_key: str):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, persona_key, created_at, updated_at
        FROM sessions
        WHERE persona_key = ?
        ORDER BY updated_at DESC
        LIMIT 5
    """, (persona_key,))
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def get_recent_sessions(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.*,
            p.name AS persona_name,
            p.avatar AS persona_avatar,
            m.content AS last_user_message
        FROM sessions s
        LEFT JOIN personalities p ON p.key = s.persona_key
        LEFT JOIN messages m ON m.id = (
            SELECT id FROM messages
            WHERE session_id = s.id
            AND sender = 'user'
            ORDER BY id DESC
            LIMIT 1
        )
        ORDER BY s.updated_at DESC
        LIMIT 10
    """)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def get_session_by_index(conn, persona_key, index: int, persona_id=None):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, persona_key, persona_id, created_at, updated_at
        FROM sessions
        WHERE persona_key = ?
        ORDER BY updated_at DESC
        LIMIT 1 OFFSET ?
    """, (persona_key, index))
    row = cursor.fetchone()
    return dict(row) if row else None


def load_session(conn, persona, system_message, session=None):
    cursor = conn.cursor()
    if session:
        session_id = session["id"]
        cursor.execute("""
            SELECT id, sender, content FROM messages
            WHERE session_id = ? ORDER BY id ASC
        """, (session_id,))
        rows = cursor.fetchall()

        cursor.execute("""
            SELECT id, sender, content FROM context
            WHERE session_id = ? ORDER BY id ASC
        """, (session_id,))
        context_rows = cursor.fetchall()

        full_messages = [system_message]
        for row in rows:
            if row["sender"] == "system":
                continue
            full_messages.append({"id": row["id"], "role": row["sender"], "content": row["content"]})

        context = [system_message]
        for row in context_rows:
            if row["sender"] == "system":
                continue
            context.append({"id": row["id"], "role": row["sender"], "content": row["content"]})
    else:
        first_msg = persona.get("opening_prompt", "Introduce yourself and start the conversation.")
        full_messages = [system_message, {"role": "assistant", "content": first_msg}]
        context = [system_message.copy(), {"role": "assistant", "content": first_msg}]

    return context, full_messages


def save_session(conn, persona_key, messages=None, context=None, session_id=None):
    cursor = conn.cursor()
    if messages is None:
        messages = []
    if context is None:
        context = []

    non_system_messages = [m for m in messages if m.get("role") != "system"]
    non_system_context = [m for m in context if m.get("role") != "system"]

    if not non_system_messages and not non_system_context:
        return None

    now = datetime.now().isoformat()

    if session_id:
        # Update both persona and persona_key to keep old column satisfied
        cursor.execute(
            "UPDATE sessions SET persona=?, persona_key=?, updated_at=? WHERE id=?",
            (persona_key, persona_key, now, session_id)
        )
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM context WHERE session_id = ?", (session_id,))
    else:
        # Insert both persona and persona_key
        cursor.execute(
            "INSERT INTO sessions(persona, persona_key, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (persona_key, persona_key, now, now)
        )
        session_id = cursor.lastrowid

    for msg in non_system_messages:
        role = msg.get("role")
        content = msg.get("content")
        if not isinstance(role, str) or not isinstance(content, str):
            continue
        cursor.execute(
            "INSERT INTO messages(session_id, sender, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )

    for msg in non_system_context:
        role = msg.get("role")
        content = msg.get("content")
        if not isinstance(role, str) or not isinstance(content, str):
            continue
        cursor.execute(
            "INSERT INTO context(session_id, sender, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )

    print(f"Session {session_id} saved.")
    return session_id


def delete_session(conn, session_id):
    if not session_id:
        return False
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM context WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    return True