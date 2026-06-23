from database import pick_session
from cli import print_message
from memory import trim_memory

def load_session(persona, system_message):

    existing_session = pick_session(persona["name"]) if persona and persona.get("name") else None

    if existing_session:
        messages = [system_message] + [
            msg for msg in existing_session["messages"]
            if not msg["role"] == "system" and not msg.get("is_summary")
        ]
        print(f"Resuming session from {existing_session['created_at'].strftime('%Y-%m-%d %H:%M')}.\n")

        for msg in messages:
            # Don't print system messages when resuming a session
            if msg.get("role") == "system":
                continue
            print_message(msg["role"], persona["name"], msg["content"])
            if msg.get("role") == "assistant":
                print()
    else:
        messages = [system_message]
        first_msg = persona.get("opening_prompt", "Introduce yourself and start the conversation.")
        print_message("assistant", persona["name"], first_msg)
        print()
        messages.append({"role": "assistant", "content": first_msg})
    full_messages = messages 
    messages = trim_memory(messages, system_message) if len(messages) > 15 else messages
    return messages, existing_session, full_messages
