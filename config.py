# config.py

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

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "datadb"
#BACKUP_DIR = DATA_DIR / "backups"
DB_PATH = DATA_DIR / "firearms.db"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
#BACKUP_DIR.mkdir(exist_ok=True)

# Business Logic Defaults

PERFORMANCE_RATINGS = ["Bad", "Adequate", "Good", "Great"]

