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

# --- RESTORED PATH LOGIC ---

# 1. Define Project Root (Where starttracker.py lives)
SCRIPT_DIR = Path(__file__).resolve().parent

# 2. Define Data Directory INSIDE the project root
# This creates: <Project Folder>/datadb/
DATA_DIR = SCRIPT_DIR / "datadb"

# 3. Define Backup Directory INSIDE the project root
# This creates: <Project Folder>/backups/
BACKUP_DIR = SCRIPT_DIR / "backups"

# 4. Define Database Path
DB_PATH = DATA_DIR / "firearms.db"

# 5. Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Business Logic Defaults
PERFORMANCE_RATINGS = ["Bad", "Adequate", "Good", "Great"]
