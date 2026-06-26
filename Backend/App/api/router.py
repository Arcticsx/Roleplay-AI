from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from personalities import get_personalities, create_personality, pick_personality
from database import save_session, load_session, get_session_by_index, get_sessions
from response import get_response
from memory import trim_memory
from config import textPrompt

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
@app.get("/sessions/{persona_name}")
def list_sessions(persona_name: str):
    """Get the last 5 sessions for a persona."""
    sessions = get_sessions(persona_name)
    if not sessions:
        return {"sessions": [], "message": "No previous sessions found."}
    return {"sessions": sessions}


class PickSessionRequest(BaseModel):
    persona_name: str
    index: int | None = None  # None = start new session

@app.post("/sessions/pick")
def pick_session_endpoint(body: PickSessionRequest):
    """Pick a session by index, or pass null index to start a new one."""
    if body.index is None:
        return {"session": None, "new": True}

    session = get_session_by_index(body.persona_name, body.index - 1)  # 1-based
    if not session:
        return {"session": None, "new": True, "warning": "Index out of range, starting new session."}

    return {"session": session, "new": False}

class SessionData(BaseModel):
    id: int
    persona: str
    created_at: str
    updated_at: str

class LoadSessionRequest(BaseModel):
    persona_key: str
    session: SessionData | None = None  # pass null to start fresh
    

@app.post("/sessions/load")
def load(body: LoadSessionRequest):
    personalities = get_personalities()
    persona = personalities.get(body.persona_key)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found.")

    template = f"{persona.get('system','')}\n\n{textPrompt}\n\nScenario: {persona.get('Scenario','')}"
    system_message = {"role": "system", "content": template}

    # Convert Pydantic model to dict if session exists
    session_dict = body.session.model_dump() if body.session else None
    messages, full_messages = load_session(persona, system_message, session_dict)
    
    # Remove id field from messages for clean response
    clean = [{k: v for k, v in m.items() if k != "id"} for m in messages]

    return {
        "session": session_dict,
        "messages": clean,
        "full_messages": full_messages,
        "resumed": body.session is not None
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
    session_id = save_session(persona["name"], body.full_messages, body.session_id)
    return {"saved": True, "session_id": session_id}

    
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
