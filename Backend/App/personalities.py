from database import get_db
from config import textPrompt


def init_personalities_db():
    with get_db() as conn:
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


def get_personalities():
    with get_db() as conn:
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


def create_personality(name, description, system, scenario, opening_prompt, avatar=None):
    with get_db() as conn:
        cursor = conn.cursor()
        personalities = get_personalities()
        keys = [int(p["key"]) for p in personalities.values() if isinstance(p.get("key"), str) and p["key"].isdigit()]
        next_key = str(max(keys) + 1) if keys else "1"

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
            next_key, name, description or '', system,
            scenario, opening_prompt, avatar or ''
        ))

    return new_persona


def update_personality(key, name, description, system, scenario, opening_prompt, avatar=None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key FROM personalities WHERE key = ?", (key,))
        if not cursor.fetchone():
            return None

        cursor.execute("""
            UPDATE personalities
            SET name=?, description=?, system=?, scenario=?, opening_prompt=?, avatar=?
            WHERE key=?
        """, (name, description or '', system, scenario, opening_prompt, avatar or '', key))

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
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personalities WHERE key = ?", (key,))
        return cursor.rowcount > 0


def pick_personality(choice: str):
    personalities = get_personalities()
    if not personalities or choice.lower() == "n":
        return None

    normalized = {str(k): v for k, v in personalities.items()}
    if choice not in normalized:
        return list(personalities.values())[0]

    return normalized[choice]