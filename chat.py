from memory import trim_memory
from personalities import pick_personality
from config import textPrompt
from database import save_session
from session_manager import load_session
from cli import header, print_message, prompt_input, info
from response import get_response

def run():
    
    persona = pick_personality()
    header(f"Now chatting with {persona['name']}")
    print("Type 'Exit' to quit.\n")


    template = f"{persona.get('system','')}\n\n{textPrompt}\n\nScenario: {persona.get('Scenario','')}"
    system_message = {
        "role": "system",
        "content": template
    }

    messages, existing_session, full_messages = load_session(persona, system_message)

    initial_user_count = sum(1 for m in messages if m.get("role") == "user")
    # Only trim after this many new messages have been added in this run
    TRIM_INTERVAL = 5
    messages_since_trim = 0
    # runtime flag: becomes True when the user sends a message during this run
    user_sent = False

    actual_messages = full_messages  # Keep a full record of messages for saving
    
    
    while True:
        user_input = prompt_input("You:")
        if user_input == 'Exit':
            # If we received any user messages during this run, save the session.
            # Fall back to the original count-based check for safety.
            if user_sent or sum(1 for m in messages if m.get("role") == "user") > initial_user_count:
                if existing_session:
                    save_session(persona["name"], actual_messages, existing_session.get("_id"))
                else:
                    save_session(persona["name"], actual_messages)
            else:
                info("No new user messages — session not saved.")
            print("Exiting...")
            return

        messages.append({
            "role": "user",
            "content": user_input
        })
        user_sent = True
        messages_since_trim += 1


        assistant_msg = get_response(messages)
        print_message("assistant", persona["name"], assistant_msg)
        print()

        messages.append({
            "role": "assistant",
            "content": assistant_msg
        })
        messages_since_trim += 1

        # Trim only once every TRIM_INTERVAL messages to reduce calls
        if messages_since_trim >= TRIM_INTERVAL:
            actual_messages.extend(messages)
            messages = trim_memory(messages, system_message)
            messages_since_trim = 0