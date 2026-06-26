# Manages persona selection and creation
from database import conn
from config import textPrompt

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS personalities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    system TEXT,
    scenario TEXT,
    opening_prompt TEXT,
    avatar TEXT
)
""")

cursor.execute("PRAGMA table_info(personalities)")
column_names = [row[1] for row in cursor.fetchall()]
if 'description' not in column_names:
    cursor.execute("ALTER TABLE personalities ADD COLUMN description TEXT")
if 'avatar' not in column_names:
    cursor.execute("ALTER TABLE personalities ADD COLUMN avatar TEXT")

conn.commit()



def get_personalities():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT key, name, description, system, scenario, opening_prompt, avatar
        FROM personalities
    """)
    results = cursor.fetchall()

    return {
        row["key"]: {
            "key": row["key"],
            "name": row["name"],
            "description": row["description"] or '',
            "system": row["system"],
            "Scenario": row["scenario"],
            "opening_prompt": row["opening_prompt"],
            "avatar": row["avatar"] or ''
        }
        for row in results
    }


def create_personality(name: str, description: str | None, system: str, scenario: str, opening_prompt: str, avatar: str | None = None):
    cursor = conn.cursor()
    personalities = get_personalities()
    keys = []
    for persona in personalities.values():
        key = persona.get("key")
        if isinstance(key, str) and key.isdigit():
            keys.append(int(key))

    next_key = str(max(keys) + 1) if keys else "1"  # auto-increment key

    new_persona = {
        "key": next_key,
        "name": name,
        "description": description or '',
        "system": system,
        "Scenario": scenario,
        "opening_prompt": opening_prompt,
        "avatar": avatar or ''
    }

    cursor.execute("""
        INSERT INTO personalities
        (key, name, description, system, scenario, opening_prompt, avatar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        new_persona["key"],
        new_persona["name"],
        new_persona["description"],
        new_persona["system"],
        new_persona["Scenario"],
        new_persona["opening_prompt"],
        new_persona["avatar"]
    ))
    conn.commit()
    return new_persona


def update_personality(key: str, name: str, description: str | None, system: str, scenario: str, opening_prompt: str, avatar: str | None = None):
    cursor = conn.cursor()
    cursor.execute("SELECT key FROM personalities WHERE key = ?", (key,))
    if not cursor.fetchone():
        return None

    cursor.execute("""
        UPDATE personalities
        SET name = ?, description = ?, system = ?, scenario = ?, opening_prompt = ?, avatar = ?
        WHERE key = ?
    """, (
        name,
        description or '',
        system,
        scenario,
        opening_prompt,
        avatar or '',
        key
    ))
    conn.commit()

    return {
        "key": key,
        "name": name,
        "description": description or '',
        "system": system,
        "Scenario": scenario,
        "opening_prompt": opening_prompt,
        "avatar": avatar or ''
    }


def delete_personality(key: str):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM personalities WHERE key = ?", (key,))
    conn.commit()
    return cursor.rowcount > 0


def pick_personality(choice: str):
    # List available personas and let the user choose or create a new one
    personalities = get_personalities()
    
    if not personalities:
        return None

    if choice.lower() == "n":
        return None
    
    normalized = {str(k): v for k, v in personalities.items()}


    if choice not in personalities:
        return list(personalities.values())[0]


    return normalized[choice] 