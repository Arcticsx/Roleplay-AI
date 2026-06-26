# Loads a session from the DB (or starts a new one) and returns the message list

from database import pick_session, cursor
from memory import trim_memory


def load_session(persona, system_message):

    # Try to resume an existing session
    existing_session = (
        pick_session(persona["name"])
        if persona and persona.get("name")
        else None
    )

    if existing_session:
        session_id = existing_session["id"]

        # Load all messages for this session
        cursor.execute("""
            SELECT id, sender, content
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
        """, (session_id,))

        rows = cursor.fetchall()

        # Rebuild message history
        messages = [system_message]

        for row in rows:
            # Skip old system messages if any exist
            if role[1] == "system":
                continue

            messages.append({
                "id": row[0],
                "role": role,
                "content": row[2]
            })

    else:
        # Start new session
        first_msg = persona.get(
            "opening_prompt",
            "Introduce yourself and start the conversation."
        )
        messages = [
            system_message,
            {"role": "assistant", "content": first_msg}
        ]

    # Full history before trimming
    full_messages = messages.copy()

    # Trim memory if needed
    if len(messages) > 15:
        messages = trim_memory(messages, system_message)

    return messages, existing_session, full_messages