# auth.py

import bcrypt
from pathlib import Path
from config import DATA_DIR

AUTH_FILE = DATA_DIR / ".auth"

def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def save_master_password(password: str):
    """Save hashed master password to auth file."""
    AUTH_FILE.parent.mkdir(exist_ok=True)
    hashed = hash_password(password)
    AUTH_FILE.write_text(hashed)

def load_master_password() -> str | None:
    """Load hashed master password from auth file."""
    if AUTH_FILE.exists():
        return AUTH_FILE.read_text()
    return None

def authenticate(password: str) -> bool:
    """Authenticate user against stored password."""
    stored = load_master_password()
    if not stored:
        return False
    return verify_password(password, stored)

def setup_first_time(password: str):
    """Setup master password on first run."""
    save_master_password(password)
