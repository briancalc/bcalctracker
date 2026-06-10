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

# --- PATH LOGIC UPDATE START ---

# Determine Base Directory
if hasattr(sys, '_MEIPASS'):
    # Running as PyInstaller Executable
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Running as Python Script
    BASE_DIR = Path(__file__).parent.resolve()

# Define ASSET_DIR for Read-Only files (CSVs, Icons)
ASSET_DIR = BASE_DIR

# Define USER_DATA_DIR for Writable files (Database, Backups)
USER_HOME = Path.home()
USER_DATA_ROOT = USER_HOME / ".bcalctracker"
DATA_DIR = USER_DATA_ROOT
BACKUP_DIR = USER_DATA_ROOT / "backups"

# Define Database Path
DB_PATH = DATA_DIR / "firearms.db"

# Ensure directories exist (creates ~/.bcalctracker if missing)
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# --- PATH LOGIC UPDATE END ---

# Business Logic Defaults
PERFORMANCE_RATINGS = ["Bad", "Adequate", "Good", "Great"]

