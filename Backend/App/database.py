# Handles all MongoDB operations for sessions
import sys
from datetime import datetime
from cli import prompt_input, print_sessions, success, info
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)

conn = sqlite3.connect(BASE_DIR/"data/chatbot.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
""")
conn.commit()
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




def save_session(persona_name, messages, session_id=None):
    if not messages:
        info("No messages to save.")
        return

    now = datetime.now().isoformat()

    if session_id:
        # Update existing session
        cursor.execute("""
            UPDATE sessions
            SET persona=?, updated_at=?
            WHERE id=?
        """, (persona_name, now, session_id))
        
        # Delete all existing messages for this session to avoid order issues
        cursor.execute("""
            DELETE FROM messages WHERE session_id = ?
        """, (session_id,))

    else:
        # Create new session
        cursor.execute("""
            INSERT INTO sessions(persona, created_at, updated_at)
            VALUES (?, ?, ?)
        """, (persona_name, now, now))

        session_id = cursor.lastrowid

    # Insert all messages in order (skipping system messages)
    for msg in messages:
        # Skip system messages
        if msg.get("role") == "system":
            continue

        # Insert message in order
        cursor.execute("""
            INSERT INTO messages(session_id, sender, content)
            VALUES (?, ?, ?)
        """, (
            session_id,
            msg["role"],
            msg["content"]
        ))

    conn.commit()
    success("Session saved.")
                       
                       

def get_sessions(persona_name):
    cursor.execute("""
        SELECT id, persona, created_at, updated_at
        FROM sessions
        WHERE persona = ?
        ORDER BY updated_at DESC
        LIMIT 5
    """, (persona_name,))

    rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "persona": row[1],
            "created_at": row[2],
            "updated_at": row[3]
        }
        for row in rows
    ]

def pick_session(persona_name):
    sessions = get_sessions(persona_name)

    if not sessions:
        return None

    print_sessions(sessions)
    while True:
        try:
            choice = prompt_input("Enter number, N for new session, or Exit to quit:").strip().lower()

            if not choice:
                print("Input cannot be empty. Please try again.")
                continue

            if choice == "exit":
                print("Exiting program. Goodbye!")
                sys.exit(0)

            if choice == "n":
                return None

            index = int(choice) - 1
            if 0 <= index < len(sessions):
                return sessions[index]
            else:
                print(f"Please enter a number between 1 and {len(sessions)}.")

        except ValueError:
            print("Invalid input. Enter a number, N, or Exit.")
        except (KeyboardInterrupt, EOFError):
            print("\nInput cancelled.")
            return None
