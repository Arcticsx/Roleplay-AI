from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from personalities import get_personalities, create_personality, pick_personality
from session_manager import load_session
from database import save_session
from response import get_response
from memory import trim_memory
from config import textPrompt

app = FastAPI()


#------------------PERSONALITIES----------------------

@app.get("/personalities")
def list_personalities():
    return get_personalities()

class CreatePersonaRequest(BaseModel):
    name: str
    system: str
    scenario: str
    opening_prompt: str
    
@app.post("/personalities", status_code=201)
def create_persona(body:CreatePersonaRequest):
    return create_personality(
        body.name, body.system,body.scenario, body.opening_prompt
    )

class PickPersonaRequest(BaseModel):
    choice: str

@app.post("/personalities/pick")
def pick_persona(body: PickPersonaRequest):
    result = pick_personality(body.choice)
    if result is None:
        raise HTTPException(
            status_code=400,
            detail="No personalities exist or choice was 'n'. POST /personalities to create one."
        )
    return result


#------------------SESSIONS----------------------

class LoadSessionRequest(BaseModel):
    persona_key: str

@app.post("/sessions/load")
def load(body: LoadSessionRequest):
    personalities = get_personalities()
    persona = personalities.get(body.persona_key)
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found.")
    
    template = f"{persona.get('system','')}\n\n{textPrompt}\n\nScenario: {persona.get('Scenario','')}"
    system_message = {"role": "system", "content": template}

    messages, existing_session, full_messages = load_session(persona, system_message)

    clean = [{k: v for k, v in m.items() if k != "id"} for m in messages]

    return {
        "session_id": existing_session["id"] if existing_session else None,
        "messages": clean,
        "full_messages": full_messages,
        "resumed": existing_session is not None
    }
    
# ── Chat ───────────────────────────────────────────────────

class ChatRequest(BaseModel):
    persona_key: str
    messages: list[dict]        
    full_messages: list[dict]   
    session_id: int | None = None
    user_input: str

@app.post("/chat")
def chat(body: ChatRequest):
    personalities = get_personalities()
    persona = personalities.get(body.persona_key)
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found.")
    
    template = f"{persona.get('system','')}\n\n{textPrompt}\n\nScenario: {persona.get('Scenario','')}"
    system_message = {"role": "system", "content": template}

    messages = body.messages + [{"role": "user", "content": body.user_input}]

    try:
        assistant_msg = get_response(messages)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    
    messages.append({"role": "assistant", "content": assistant_msg})
    messages = trim_memory(messages, system_message)

    # Update full history
    msg_id = max((m.get("id", 0) for m in body.full_messages), default=0)
    full_messages = body.full_messages + [
        {"id": msg_id + 1, "role": "user",      "content": body.user_input},
        {"id": msg_id + 2, "role": "assistant",  "content": assistant_msg},
    ]

    return {
        "assistant_message": assistant_msg,
        "messages": messages,
        "full_messages": full_messages,
    }

class SaveSessionRequest(BaseModel):
    persona_key: str
    full_messages: list[dict]
    session_id: int | None = None

@app.post("/sessions/save")
def save(body: SaveSessionRequest):
    personalities = get_personalities()
    persona = personalities.get(body.persona_key)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found.")
    save_session(persona["name"], body.full_messages, body.session_id)
    return {"saved": True}
