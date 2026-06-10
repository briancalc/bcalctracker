# data_loaders.py

import csv
from pathlib import Path

# Define paths relative to script directory
SCRIPT_DIR = Path(__file__).parent
DATA_MENU_DIR = SCRIPT_DIR / 'datamenu'

CSV_FILES = {
    'calibers': DATA_MENU_DIR / 'calibers.csv',
    'ammo_mfg': DATA_MENU_DIR / 'ammomfg.csv',
    'firearm_mfg': DATA_MENU_DIR / 'firearmmfg.csv',
    'optics_mfg': DATA_MENU_DIR / 'opticsmfg.csv',
    'firearm_types': DATA_MENU_DIR / 'firearmtype.csv',
    'optic_types': DATA_MENU_DIR / 'optictype.csv',
    'ammo_types': DATA_MENU_DIR / 'ammotype.csv',
    'ammo_use_cases': DATA_MENU_DIR / 'ammouse.csv',
    'range_results': DATA_MENU_DIR / 'rangeresults.csv',
    # New CSV files for Ammo Form expansion
    'shot_sizes': DATA_MENU_DIR / 'shotsize.csv',
    'projectile_types': DATA_MENU_DIR / 'projectiletype.csv',
    'brass_mfg': DATA_MENU_DIR / 'brassmfg.csv',
    'hull_mfg': DATA_MENU_DIR / 'hullwadmfg.csv',
    'wad_mfg': DATA_MENU_DIR / 'hullwadmfg.csv',
    'powder_mfg': DATA_MENU_DIR / 'powdermfg.csv',
    'primer_mfg': DATA_MENU_DIR / 'primermfg.csv',
    'primer_types': DATA_MENU_DIR / 'primertype.csv',
    'crimp_types': DATA_MENU_DIR / 'crimptype.csv',
    'bullet_mfg': DATA_MENU_DIR / 'bulletmfg.csv',
    'drag_functions': DATA_MENU_DIR / 'dragfunc.csv',
}

def load_csv_list(filename_key: str) -> list:

    filepath = CSV_FILES.get(filename_key)
    if not filepath:
        print(f"Error: No path defined for key '{filename_key}'")
        return []

    if not filepath.exists():
        print(f"Warning: {filename_key} file not found at {filepath}")
        return []

    values = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row and row[0].strip():
                    values.append(row[0].strip())
    except Exception as e:
        print(f"Error loading {filename_key}: {e}")

    return values

# Pre-load for convenience
# Manufacturers & Calibers
CALIBERS = load_csv_list('calibers')
AMMO_MFG = load_csv_list('ammo_mfg')
FIREARM_MFG = load_csv_list('firearm_mfg')
OPTICS_MFG = load_csv_list('optics_mfg')

# Types
FIREARM_TYPES = load_csv_list('firearm_types')
OPTIC_TYPES = load_csv_list('optic_types')
AMMO_TYPES = load_csv_list('ammo_types')
RANGE_RESULTS = load_csv_list('range_results')

# Use Cases
AMMO_USE_CASES = load_csv_list('ammo_use_cases')

# --- NEW: Reloading & Shotgun Data Lists ---
SHOT_SIZES = load_csv_list('shot_sizes')
PROJECTILE_TYPES = load_csv_list('projectile_types')
BRASS_MFG = load_csv_list('brass_mfg')
HULL_MFG = load_csv_list('hull_mfg')
WAD_MFG = load_csv_list('wad_mfg')
POWDER_MFG = load_csv_list('powder_mfg')
PRIMER_MFG = load_csv_list('primer_mfg')
PRIMER_TYPES = load_csv_list('primer_types')
CRIMP_TYPES = load_csv_list('crimp_types')
BULLET_MFG = load_csv_list('bullet_mfg')
DRAG_FUNCTIONS = load_csv_list('drag_functions')

# Fallbacks if CSVs are missing (prevents empty lists crashing UI)
if not FIREARM_TYPES:
    FIREARM_TYPES = ["Rifle", "Handgun", "Shotgun", "Revolver", "Other"]
if not OPTIC_TYPES:
    OPTIC_TYPES = ["Red Dot", "Holographic", "Scopes (Fixed Power)", "Scopes (Variable Power)", "Iron Sights", "Night Vision", "Other"]
if not AMMO_TYPES:
    AMMO_TYPES = ["Hunting", "Target", "Self-Defense", "Competition", "Long-Range Precision", "Training", "Other"]
if not AMMO_USE_CASES:
    AMMO_USE_CASES = ["Hunting", "Target", "Self-Defense", "Competition", "Long-Range Precision", "Training", "Other"]
if not RANGE_RESULTS:
    RANGE_RESULTS = ["unknown", "bad", "poor", "OK", "good", "very good", "excellent"]

# New Fallbacks (with "n/a" as first option)
if not SHOT_SIZES:
    SHOT_SIZES = ["n/a", "#9", "#8", "#7½", "#6", "#5", "#4", "00 Buck", "Slug"]
if not PROJECTILE_TYPES:
    PROJECTILE_TYPES = ["n/a", "FMJ", "JHP", "SP", "BT", "Tracer", "Slug", "Buckshot", "Birdshot"]
if not BRASS_MFG:
    BRASS_MFG = ["n/a", "Winchester", "Federal", "Lapua", "Starline", "Remington", "CCI"]
if not HULL_MFG:
    HULL_MFG = ["n/a", "Remington", "Winchester", "Federal", "Cheddite", "Rio"]
if not WAD_MFG:
    WAD_MFG = ["n/a", "Claybuster", "Redfield", "Wad-Guard", "Federal", "Remington"]
if not POWDER_MFG:
    POWDER_MFG = ["n/a", "Hodgdon", "Vihtavuori", "Alliant", "IMR", "Accurate", "Ramshot"]
if not PRIMER_MFG:
    PRIMER_MFG = ["n/a", "CCI", "Federal", "Winchester", "Remington", "SR"]
if not PRIMER_TYPES:
    PRIMER_TYPES = ["n/a", "Small Rifle", "Large Rifle", "Small Pistol", "Large Pistol", "Small Magnum", "Large Magnum"]
if not CRIMP_TYPES:
    CRIMP_TYPES = ["n/a", "Roll", "Taper", "Factory", "None"]
if not BULLET_MFG:
    BULLET_MFG = ["n/a", "Sierra", "Hornady", "Barnes", "Berger", "Nosler", "Speer"]
if not DRAG_FUNCTIONS:
    DRAG_FUNCTIONS = ["n/a", "G1", "G7"]



if __name__ == "__main__":
    print(f"Calibers: {len(CALIBERS)}")
    print(f"Ammo MFG: {len(AMMO_MFG)}")
    print(f"Firearm MFG: {len(FIREARM_MFG)}")
    print(f"Optics MFG: {len(OPTICS_MFG)}")
    print(f"Firearm Types: {len(FIREARM_TYPES)}")
    print(f"Optic Types: {len(OPTIC_TYPES)}")
    print(f"Ammo Types: {len(AMMO_TYPES)}")
    print(f"Ammo Use Cases: {len(AMMO_USE_CASES)}")

    # New prints for verification
    print(f"Shot Sizes: {len(SHOT_SIZES)}")
    print(f"Projectile Types: {len(PROJECTILE_TYPES)}")
    print(f"Brass MFG: {len(BRASS_MFG)}")
    print(f"Hull MFG: {len(HULL_MFG)}")
    print(f"Wad MFG: {len(WAD_MFG)}")
    print(f"Powder MFG: {len(POWDER_MFG)}")
    print(f"Primer MFG: {len(PRIMER_MFG)}")
    print(f"Primer Types: {len(PRIMER_TYPES)}")
    print(f"Crimp Types: {len(CRIMP_TYPES)}")
    print(f"Bullet MFG: {len(BULLET_MFG)}")
    print(f"Drag Functions: {len(DRAG_FUNCTIONS)}")
