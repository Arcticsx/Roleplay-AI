import sqlite3
from datetime import datetime
from pathlib import Path
from memory import trim_memory
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

# Create tables once at startup
def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                persona TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
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

# All functions now accept conn as first parameter
def get_sessions(conn, persona_name):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, persona, created_at, updated_at
        FROM sessions WHERE persona = ?
        ORDER BY updated_at DESC LIMIT 5
    """, (persona_name,))
    return [dict(row) for row in cursor.fetchall()]

def get_session_by_index(conn, persona_name, index: int):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, persona, created_at, updated_at
        FROM sessions WHERE persona=?
        ORDER BY updated_at DESC LIMIT 1 OFFSET ?
    """, (persona_name, index))
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

def save_session(conn, persona_name, messages, context, session_id=None):
    cursor = conn.cursor()
    non_system_messages = [m for m in messages if m.get("role") != "system"]
    non_system_context = [m for m in context if m.get("role") != "system"]

    if not non_system_messages and not non_system_context:
        return None

    now = datetime.now().isoformat()

    if session_id:
        cursor.execute("UPDATE sessions SET persona=?, updated_at=? WHERE id=?", (persona_name, now, session_id))
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM context WHERE session_id = ?", (session_id,))
    else:
        cursor.execute("INSERT INTO sessions(persona, created_at, updated_at) VALUES (?, ?, ?)", (persona_name, now, now))
        session_id = cursor.lastrowid

    for msg in non_system_messages:
        role = msg.get("role")
        content = msg.get("content")
        if not isinstance(role, str) or not isinstance(content, str):
            continue
        cursor.execute("INSERT INTO messages(session_id, sender, content) VALUES (?, ?, ?)", (session_id, role, content))

    for msg in non_system_context:
        role = msg.get("role")
        content = msg.get("content")
        if not isinstance(role, str) or not isinstance(content, str):
            continue
        cursor.execute("INSERT INTO context(session_id, sender, content) VALUES (?, ?, ?)", (session_id, role, content))

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