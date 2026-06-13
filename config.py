# bcalctracker/config.py

import sys
from pathlib import Path

# 1. Import GUI Styling Constants
from guiform.constants import (
    COLOR_BG_FRAME, COLOR_LABEL, COLOR_WHITE, COLOR_GRAY,
    COLOR_ERROR_BG, COLOR_ERROR_TEXT, COLOR_UNIT,
    FONT_FAMILY, LABEL_FONT_SIZE, UNIT_FONT_SIZE,
    TITLE_FONT_SIZE, BUTTON_FONT_SIZE, LOGIN_WINDOW_WIDTH, LOGIN_WINDOW_HEIGHT,
    MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT,
    LOGIN_MAIN_PADDING, MAIN_CONTAINER_PADDING, TAB_PADDING,
    LOGIN_ICON_SIZE, BUTTON_PADX
)

# 2. Import Dynamic Dropdown Data
from data_loaders import (
    CALIBERS, AMMO_MFG, FIREARM_MFG, OPTICS_MFG,
    FIREARM_TYPES, OPTIC_TYPES, AMMO_TYPES, AMMO_USE_CASES
)

# Application Info
APP_NAME = "Bcalc Firearm Management"
VERSION = "v1.0"

# --- UPDATED PATH LOGIC ---

def get_app_root():
    """Get the root directory of the application."""
    # Check if running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Bundle mode: __file__ might be the temp extractor, but sys.executable is the EXE
        application_path = sys.executable
    else:
        # Normal dev mode: script is in the project folder
        application_path = __file__

    return Path(application_path).resolve().parent

# 1. Define Project Root
PROJECT_ROOT = get_app_root()

# 2. Define Data Directory INSIDE the project root
# This creates: <Project Folder>/datadb/
DATA_DIR = PROJECT_ROOT / "datadb"

# 3. Define Backup Directory INSIDE the project root
BACKUP_DIR = PROJECT_ROOT / "backups"

# 4. Define Database Path
DB_PATH = DATA_DIR / "firearms.db"

# 5. Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

print(f"[DEBUG] App Root: {PROJECT_ROOT}")
print(f"[DEBUG] Data Dir: {DATA_DIR}")
print(f"[DEBUG] DB Path: {DB_PATH}")

# Business Logic Defaults
PERFORMANCE_RATINGS = ["Bad", "Adequate", "Good", "Great"]
