import sqlite3
from datetime import datetime
from pathlib import Path
from memory import trim_memory


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure data folder exists
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "chatbot.db"

# Database connection
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


# Create tables
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

conn.commit()


def get_sessions(persona_name):
    """
    Return last 5 sessions for a persona
    """
    cursor.execute("""
        SELECT id, persona, created_at, updated_at
        FROM sessions
        WHERE persona = ?
        ORDER BY updated_at DESC
        LIMIT 5
    """, (persona_name,))

    return [
        {
            "id": row["id"],
            "persona": row["persona"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
        for row in cursor.fetchall()
    ]


def get_session_by_index(persona_name, index=0):
    """
    Get session by position in latest sessions list
    index=0 → latest session
    """
    sessions = get_sessions(persona_name)

    if not sessions:
        return None

    if 0 <= index < len(sessions):
        return sessions[index]

    return None


def pick_session(persona_name):
    """
    Pick latest session automatically
    """
    return get_session_by_index(persona_name, 0)


def load_session(persona, system_message):
    """
    Load existing session or create new conversation
    """

    existing_session = (
        pick_session(persona["name"])
        if persona and persona.get("name")
        else None
    )

    if existing_session:
        session_id = existing_session["id"]

        cursor.execute("""
            SELECT id, sender, content
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
        """, (session_id,))

        rows = cursor.fetchall()

        messages = [system_message]

        for row in rows:
            # Ignore accidental old system messages
            if row["sender"] == "system":
                continue

            messages.append({
                "id": row["id"],
                "role": row["sender"],
                "content": row["content"]
            })

    else:
        first_msg = (
            persona.get(
                "opening_prompt",
                "Introduce yourself and start the conversation."
            )
            if persona
            else "Introduce yourself and start the conversation."
        )

        messages = [
            system_message,
            {
                "role": "assistant",
                "content": first_msg
            }
        ]

    # Keep full history
    full_messages = messages.copy()

    # Trim if too long
    if len(messages) > 15:
        messages = trim_memory(messages, system_message)

    return messages, existing_session, full_messages


def save_session(persona_name, messages, session_id=None):
    """
    Save/update session and messages
    """

    if not messages:
        return None

    now = datetime.now().isoformat()

    if session_id:
        # Update existing session
        cursor.execute("""
            UPDATE sessions
            SET persona=?, updated_at=?
            WHERE id=?
        """, (persona_name, now, session_id))

        # Replace messages
        cursor.execute("""
            DELETE FROM messages
            WHERE session_id=?
        """, (session_id,))

    else:
        # Create new session
        cursor.execute("""
            INSERT INTO sessions
            (persona, created_at, updated_at)
            VALUES (?, ?, ?)
        """, (persona_name, now, now))

        session_id = cursor.lastrowid

    # Save messages
    for msg in messages:
        if msg.get("role") == "system":
            continue

        cursor.execute("""
            INSERT INTO messages
            (session_id, sender, content)
            VALUES (?, ?, ?)
        """, (
            session_id,
            msg["role"],
            msg["content"]
        ))

    conn.commit()

    return session_id


def close_db():
    """
    Close database connection safely
    """
    conn.close()