# user_manager.py
import json
import os
from typing import Dict, Optional

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")


def load_users() -> Dict[str, int]:
    """Load users from users.json. Returns dict of {username: high_score}."""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        return data
    except (json.JSONDecodeError, IOError):
        return {}


def save_users(users: Dict[str, int]):
    """Save users dict to users.json."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def create_user(username: str) -> bool:
    """Create a new user. Returns False if username already exists."""
    users = load_users()
    if username in users:
        return False
    users[username] = 0
    save_users(users)
    return True


def update_high_score(username: str, score: int) -> bool:
    """Update user's high score if the new score is higher. Returns True if updated."""
    users = load_users()
    if username not in users:
        return False
    if score > users[username]:
        users[username] = score
        save_users(users)
        return True
    return False


def get_high_score(username: str) -> int:
    """Get the high score for a user."""
    users = load_users()
    return users.get(username, 0)


def has_users() -> bool:
    """Check if there are any existing users."""
    return len(load_users()) > 0
