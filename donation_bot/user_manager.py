import json
import os

USERS_FILE = "allowed_users.json"
OWNER_ID = 0  # To be replaced with the owner's Telegram ID

def set_owner(owner_id):
    """Sets the owner ID."""
    global OWNER_ID
    OWNER_ID = owner_id

def get_allowed_users():
    """Returns a list of allowed user IDs."""
    if not os.path.exists(USERS_FILE):
        return [OWNER_ID] if OWNER_ID else []

    with open(USERS_FILE, "r") as f:
        return json.load(f)

def add_user(user_id):
    """Adds a user to the allowed list."""
    allowed_users = get_allowed_users()
    if user_id not in allowed_users:
        allowed_users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(allowed_users, f)
        return True
    return False

def is_user_allowed(user_id):
    """Checks if a user is allowed."""
    return user_id in get_allowed_users()

def is_owner(user_id):
    """Checks if a user is the owner."""
    return user_id == OWNER_ID
