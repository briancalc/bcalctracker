 # database.py

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from config import DB_PATH


class DatabaseManager:
    """Manages the encrypted database connection and operations."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> bool:
        """Establish a connection to the standard SQLite database."""
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] Connecting to: {self.db_path}")
            print(f"[DEBUG] File exists before connect: {self.db_path.exists()}")

            # Connect (Standard SQLite)
            self.conn = sqlite3.connect(str(self.db_path))
            cursor = self.conn.cursor()
            print("[DEBUG] Connection object created.")

            # Enable Foreign Keys immediately
            cursor.execute("PRAGMA foreign_keys = ON")

            # Check if tables exist to decide between creation or migration
            if not self._table_exists(cursor, 'firearms'):
                print("[DEBUG] No tables found. Creating schema...")
                self._create_schema(cursor)
                self.conn.commit()
                print("[DEBUG] Schema created.")
            else:
                print("[DEBUG] Schema exists.")
                # Run migrations if table exists but might be old
                print("[DEBUG] Checking for migrations...")
                self._run_migrations(cursor)
                self.conn.commit()
                print("[DEBUG] Migrations complete.")

            print("[DEBUG] SUCCESS: Database connected.")
            return True

        except Exception as e:
            print(f"[DEBUG] CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            if self.conn:
                self.close()
            return False

            # Create Schema if new
            if not self._table_exists(cursor, 'firearms'):
                print("[DEBUG] No tables found. Creating schema...")
                self._create_schema(cursor)
                self.conn.commit()
                print("[DEBUG] Schema created.")
            else:
                print("[DEBUG] Schema exists.")
                # Run migrations if table exists but might be old
                print("[DEBUG] Checking for migrations...")
                self._run_migrations(cursor)
                self.conn.commit()
                print("[DEBUG] Migrations complete.")

            cursor.execute("PRAGMA foreign_keys = ON")
            self._password = password
            print("[DEBUG] SUCCESS: Database connected.")
            return True

        except Exception as e:
            print(f"[DEBUG] CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            if self.conn:
                self.close()
            return False

    def _table_exists(self, cursor, table_name: str) -> bool:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None

    def _column_exists(self, cursor, table_name: str, column_name: str) -> bool:
        """Check if a specific column exists in a table."""
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns

#===================================================
    def _run_migrations(self, cursor: sqlite3.Cursor) -> None:
            """Run database migrations to add new columns if they don't exist."""
            migrations = [
                # --- Configurations ---
                ('configurations', 'firearm_id', 'INTEGER NOT NULL'),
                ('configurations', 'optic_id', 'INTEGER'),
                ('configurations', 'ammo_id', 'INTEGER'),
                ('configurations', 'config_notes', 'TEXT'),
                ('configurations', 'created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),

                # --- Firearms ---
                ('firearms', 'name', 'TEXT'),
                ('firearms', 'mfg', 'TEXT NOT NULL'),
                ('firearms', 'firearm_type', 'TEXT NOT NULL'),
                ('firearms', 'serial_number', 'TEXT UNIQUE'),
                ('firearms', 'caliber_primary', 'TEXT'),
                ('firearms', 'caliber_secondary', 'TEXT'),
                ('firearms', 'barrel_length', 'REAL'),
                ('firearms', 'purchase_date', 'TEXT'),
                ('firearms', 'purchase_location', 'TEXT'),
                ('firearms', 'purchase_price', 'REAL'),
                ('firearms', 'sold_date', 'TEXT'),
                ('firearms', 'sold_buyer', 'TEXT'),
                ('firearms', 'sold_price', 'REAL'),
                ('firearms', 'notes', 'TEXT'),
                ('firearms', 'photo_path', 'TEXT'),
                ('firearms', 'created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('firearms', 'updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),

                # --- Optics ---
                ('optics', 'mfg', 'TEXT NOT NULL'),
                ('optics', 'optic_type', 'TEXT NOT NULL'),
                ('optics', 'model', 'TEXT'),
                ('optics', 'notes', 'TEXT'),
                ('optics', 'created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),

                # --- Ammo Loads ---
                ('ammo_loads', 'mfg', 'TEXT NOT NULL'),
                ('ammo_loads', 'caliber', 'TEXT NOT NULL'),
                ('ammo_loads', 'ammo_name', 'TEXT'),
                ('ammo_loads', 'use_case', 'TEXT'),
                ('ammo_loads', 'grains', 'REAL'),
                ('ammo_loads', 'bullet_name', 'TEXT'),
                ('ammo_loads', 'bullet_mfg', 'TEXT'),
                ('ammo_loads', 'drag_function', 'TEXT'),
                ('ammo_loads', 'ballistic_coeff', 'REAL'),
                ('ammo_loads', 'do_not_rebuy', 'INTEGER DEFAULT 0'),
                ('ammo_loads', 'notes', 'TEXT'),
                ('ammo_loads', 'projectile_type', 'TEXT'),
                ('ammo_loads', 'shot_size', 'TEXT'),
                ('ammo_loads', 'pellet_count', 'INTEGER'),
                ('ammo_loads', 'brass_mfg', 'TEXT'),
                ('ammo_loads', 'hull_mfg', 'TEXT'),
                ('ammo_loads', 'wad_mfg', 'TEXT'),
                ('ammo_loads', 'powder_mfg', 'TEXT'),
                ('ammo_loads', 'powder_name', 'TEXT'),
                ('ammo_loads', 'powder_lot', 'TEXT'),
                ('ammo_loads', 'powder_grains', 'REAL'),
                ('ammo_loads', 'primer_mfg', 'TEXT'),
                ('ammo_loads', 'primer_type', 'TEXT'),
                ('ammo_loads', 'primer_lot', 'TEXT'),
                ('ammo_loads', 'case_weight', 'REAL'),
                ('ammo_loads', 'overall_length', 'REAL'),
                ('ammo_loads', 'cbto', 'REAL'),
                ('ammo_loads', 'crimp_type', 'TEXT'),
                ('ammo_loads', 'date_loaded', 'TEXT'),
                ('ammo_loads', 'batch_quantity', 'INTEGER'),
                ('ammo_loads', 'created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('ammo_loads', 'updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),

                # --- Range Sessions ---
                ('range_sessions', 'configuration_id', 'INTEGER NOT NULL'),
                ('range_sessions', 'date', 'TEXT NOT NULL'),
                ('range_sessions', 'location', 'TEXT'),
                ('range_sessions', 'rounds_fired', 'INTEGER DEFAULT 0'),
                ('range_sessions', 'target_range', 'REAL'),
                ('range_sessions', 'wind_speed', 'REAL'),
                ('range_sessions', 'wind_angle', 'REAL'),
                ('range_sessions', 'temperature', 'REAL'),
                ('range_sessions', 'humidity', 'REAL'),
                ('range_sessions', 'vel_avg', 'REAL'),
                ('range_sessions', 'vel_max', 'REAL'),
                ('range_sessions', 'vel_std_dev', 'REAL'),
                ('range_sessions', 'vel_ext_spread', 'REAL'),
                ('range_sessions', 'moa_avg', 'REAL'),
                ('range_sessions', 'moa_best', 'REAL'),
                ('range_sessions', 'moa_std_dev', 'REAL'),
                ('range_sessions', 'moa_ext_spread', 'REAL'),
                ('range_sessions', 'rating', 'TEXT'),
                ('range_sessions', 'photo_path', 'TEXT'),
                ('range_sessions', 'notes', 'TEXT'),
                ('range_sessions', 'created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ]

            for table, column, col_type in migrations:
                if self._table_exists(cursor, table) and not self._column_exists(cursor, table, column):
                    print(f"[DEBUG] Migrating: Adding column '{column}' to '{table}'...")
                    try:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                        print(f"[DEBUG] Successfully added {column}.")
                    except Exception as e:
                        print(f"[ERROR] Failed to add {column} to {table}: {e}")




#==========================================================
    def _create_schema(self, cursor: sqlite3.Cursor) -> None:
        """Create the database schema."""

        # 1. Firearms Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS firearms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            mfg TEXT NOT NULL,
            firearm_type TEXT NOT NULL,
            serial_number TEXT UNIQUE,
            caliber_primary TEXT,
            caliber_secondary TEXT,
            barrel_length REAL,
            purchase_date TEXT,
            purchase_location TEXT,
            purchase_price REAL,
            sold_date TEXT,
            sold_buyer TEXT,
            sold_price REAL,
            notes TEXT,
            photo_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 2. Optics Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS optics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mfg TEXT NOT NULL,
            optic_type TEXT NOT NULL,
            model TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 3. Ammo Loads Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ammo_loads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mfg TEXT NOT NULL,
            caliber TEXT NOT NULL,
            ammo_name TEXT,
            use_case TEXT,
            grains REAL,
            bullet_name TEXT,
            bullet_mfg TEXT,
            drag_function TEXT,
            ballistic_coeff REAL,
            do_not_rebuy INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            projectile_type TEXT,
            shot_size TEXT,
            pellet_count INTEGER,
            brass_mfg TEXT,
            hull_mfg TEXT,
            wad_mfg TEXT,
            powder_mfg TEXT,
            powder_name TEXT,
            powder_lot TEXT,
            powder_grains REAL,
            primer_mfg TEXT,
            primer_type TEXT,
            primer_lot TEXT,
            case_weight REAL,
            overall_length REAL,
            cbto REAL,
            crimp_type TEXT,
            date_loaded TEXT,
            batch_quantity INTEGER
        )
        """)

        # 4. Configurations Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firearm_id INTEGER NOT NULL,
            optic_id INTEGER,
            ammo_id INTEGER,
            config_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (firearm_id) REFERENCES firearms(id) ON DELETE CASCADE,
            FOREIGN KEY (optic_id) REFERENCES optics(id) ON DELETE SET NULL,
            FOREIGN KEY (ammo_id) REFERENCES ammo_loads(id) ON DELETE SET NULL
        )
        """)


        # 5. Range Sessions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS range_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            configuration_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            location TEXT,
            rounds_fired INTEGER DEFAULT 0,

            -- Environmental Data
            target_range REAL,
            wind_speed REAL,
            wind_angle REAL,
            temperature REAL,
            humidity REAL,

            -- Velocity Data (Imperial: FPS)
            vel_avg REAL,
            vel_max REAL,
            vel_std_dev REAL,
            vel_ext_spread REAL,

            -- MOA Data
            moa_avg REAL,
            moa_best REAL,
            moa_std_dev REAL,
            moa_ext_spread REAL,

            -- Metadata
            rating TEXT,
            photo_path TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (configuration_id) REFERENCES configurations(id) ON DELETE CASCADE
        )
        """)

    # --- Generic Query Helpers ---

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        if not self.conn:
            raise RuntimeError("Database not connected.")
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def execute_write(self, query: str, params: tuple = ()) -> int:
        if not self.conn:
            raise RuntimeError("Database not connected.")
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    # --- CRUD: Firearms ---

    def add_firearm(self, data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO firearms (name, mfg, firearm_type, serial_number, caliber_primary, caliber_secondary,
                              barrel_length, purchase_date, purchase_location, purchase_price,
                              sold_date, sold_buyer, sold_price, notes, photo_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get('name'), data.get('mfg'), data.get('firearm_type'), data.get('serial_number'),
            data.get('caliber_primary'), data.get('caliber_secondary'), data.get('barrel_length'),
            data.get('purchase_date'), data.get('purchase_location'), data.get('purchase_price'),
            data.get('sold_date'), data.get('sold_buyer'), data.get('sold_price'), data.get('notes'), data.get('photo_path')
        )
        return self.execute_write(query, params)

    def get_all_firearms(self) -> List[Dict[str, Any]]:
        return self.execute_query("SELECT * FROM firearms ORDER BY mfg, firearm_type")

    def get_active_firearms(self) -> List[Dict[str, Any]]:
        """Returns firearms that are NOT sold."""
        return self.execute_query("SELECT * FROM firearms WHERE sold_date IS NULL ORDER BY mfg, firearm_type")

    def get_firearm_by_id(self, firearm_id: int) -> Optional[Dict[str, Any]]:
        result = self.execute_query("SELECT * FROM firearms WHERE id = ?", (firearm_id,))
        return result[0] if result else None

    def get_firearm_by_serial(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Find a firearm by serial number."""
        result = self.execute_query(
            "SELECT * FROM firearms WHERE serial_number = ?",
            (serial_number,)
        )
        return result[0] if result else None

    def update_firearm(self, firearm_id: int, data: Dict[str, Any]) -> bool:
        # Prevent updating sold firearms
        current = self.get_firearm_by_id(firearm_id)
        if current and current.get('sold_date'):
            return False

        fields = []
        params = []
        for key, value in data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                params.append(value)

        if not fields:
            return False
        params.append(firearm_id)
        query = f"UPDATE firearms SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        return self.execute_write(query, tuple(params)) > 0

    def mark_as_sold(self, firearm_id: int, data: Dict[str, Any]) -> bool:
        """Marks a firearm as sold with date, buyer, price."""
        fields = ["sold_date = ?", "sold_buyer = ?", "sold_price = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [data.get('sold_date'), data.get('sold_buyer'), data.get('sold_price'), firearm_id]
        query = f"UPDATE firearms SET {', '.join(fields)} WHERE id = ?"
        return self.execute_write(query, tuple(params)) > 0

    def delete_firearm(self, firearm_id: int) -> bool:
        return self.execute_write("DELETE FROM firearms WHERE id = ?", (firearm_id,)) > 0

    def count_firearms(self) -> int:
        result = self.execute_query("SELECT COUNT(*) as count FROM firearms")
        return result[0]['count'] if result else 0

    # --- CRUD: Optics ---

    def add_optic(self, data: Dict[str, Any]) -> int:
        query = "INSERT INTO optics (mfg, optic_type, model, notes) VALUES (?, ?, ?, ?)"
        params = (data.get('mfg'), data.get('optic_type'), data.get('model'), data.get('notes'))
        return self.execute_write(query, params)

    def get_all_optics(self) -> List[Dict[str, Any]]:
        return self.execute_query("SELECT * FROM optics ORDER BY mfg, optic_type, model")

    def get_optic_by_id(self, optic_id: int) -> Optional[Dict[str, Any]]:
        result = self.execute_query("SELECT * FROM optics WHERE id = ?", (optic_id,))
        return result[0] if result else None

    def update_optic(self, optic_id: int, data: Dict[str, Any]) -> bool:
        fields = []
        params = []
        for key, value in data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                params.append(value)
        if not fields: return False
        params.append(optic_id)
        query = f"UPDATE optics SET {', '.join(fields)} WHERE id = ?"
        return self.execute_write(query, tuple(params)) > 0

    def delete_optic(self, optic_id: int) -> bool:
        return self.execute_write("DELETE FROM optics WHERE id = ?", (optic_id,)) > 0

    def count_optics(self) -> int:
        result = self.execute_query("SELECT COUNT(*) as count FROM optics")
        return result[0]['count'] if result else 0

    # --- CRUD: Ammo Loads ---
    def add_ammo(self, data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO ammo_loads (
            mfg, caliber, ammo_name, use_case, grains, bullet_name, bullet_mfg, do_not_rebuy, notes,
            projectile_type, shot_size, pellet_count, drag_function, ballistic_coeff,
            brass_mfg, hull_mfg, wad_mfg,
            powder_mfg, powder_name, powder_lot, powder_grains,
            primer_mfg, primer_type, primer_lot,
            case_weight, overall_length, cbto, crimp_type, date_loaded, batch_quantity
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Helper to safely get value, defaulting to None if missing
        def get_val(key):
            return data.get(key)

        params = (
            get_val('mfg'),
            get_val('caliber'),
            get_val('ammo_name'),
            get_val('use_case'),
            get_val('grains'),
            get_val('bullet_name'),
            get_val('bullet_mfg'),
            1 if data.get('do_not_rebuy') else 0,
            get_val('notes'),
            get_val('projectile_type'),
            get_val('shot_size'),
            get_val('pellet_count'),
            get_val('drag_function'),
            get_val('ballistic_coeff'),
            get_val('brass_mfg'),
            get_val('hull_mfg'),
            get_val('wad_mfg'),
            get_val('powder_mfg'),
            get_val('powder_name'),
            get_val('powder_lot'),
            get_val('powder_grains'),
            get_val('primer_mfg'),
            get_val('primer_type'),
            get_val('primer_lot'),
            get_val('case_weight'),
            get_val('overall_length'),
            get_val('cbto'),
            get_val('crimp_type'),
            get_val('date_loaded'),
            get_val('batch_quantity')
        )
        return self.execute_write(query, params)

    def get_all_ammo(self) -> List[Dict[str, Any]]:
        return self.execute_query("SELECT * FROM ammo_loads ORDER BY mfg, caliber")

    def get_ammo_by_id(self, ammo_id: int) -> Optional[Dict[str, Any]]:
        result = self.execute_query("SELECT * FROM ammo_loads WHERE id = ?", (ammo_id,))
        return result[0] if result else None

    def update_ammo(self, ammo_id: int, data: Dict[str, Any]) -> bool:
        fields = []
        params = []
        for key, value in data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                params.append(value)
        if not fields: return False
        params.append(ammo_id)
        query = f"UPDATE ammo_loads SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        return self.execute_write(query, tuple(params)) > 0

    def delete_ammo(self, ammo_id: int) -> bool:
        return self.execute_write("DELETE FROM ammo_loads WHERE id = ?", (ammo_id,)) > 0

    def count_ammo(self) -> int:
        result = self.execute_query("SELECT COUNT(*) as count FROM ammo_loads")
        return result[0]['count'] if result else 0

    # --- CRUD: Configurations ---

    def add_configuration(self, data: Dict[str, Any]) -> int:
        query = "INSERT INTO configurations (firearm_id, optic_id, ammo_id, config_notes) VALUES (?, ?, ?, ?)"
        params = (
            data.get('firearm_id'),
            data.get('optic_id'),
            data.get('ammo_id'),
            data.get('config_notes')
        )
        return self.execute_write(query, params)

    def update_configuration(self, config_id: int, data: Dict[str, Any]) -> bool:
        fields = []
        params = []
        for key, value in data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                params.append(value)
        if not fields: return False
        params.append(config_id)
        query = f"UPDATE configurations SET {', '.join(fields)} WHERE id = ?"
        return self.execute_write(query, tuple(params)) > 0

    def get_all_configurations(self) -> List[Dict[str, Any]]:
        return self.execute_query("""
            SELECT c.*,
                   f.name as firearm_name, f.mfg as firearm_mfg, f.firearm_type as firearm_type, f.serial_number as firearm_serial,
                   o.mfg as optic_mfg, o.optic_type as optic_type, o.model as optic_model,
                   a.mfg as ammo_mfg, a.caliber as caliber, a.ammo_name as ammo_name, a.use_case as use_case, a.grains as grains, a.bullet_name as bullet_name,
                   AVG(
                       CASE rs.rating
                           WHEN 'bad' THEN 1
                           WHEN 'poor' THEN 2
                           WHEN 'OK' THEN 3
                           WHEN 'good' THEN 4
                           WHEN 'very good' THEN 5
                           WHEN 'excellent' THEN 6
                           ELSE NULL
                       END
                   ) as avg_rating_score
            FROM configurations c
            LEFT JOIN firearms f ON c.firearm_id = f.id
            LEFT JOIN optics o ON c.optic_id = o.id
            LEFT JOIN ammo_loads a ON c.ammo_id = a.id
            LEFT JOIN range_sessions rs ON c.id = rs.configuration_id
            GROUP BY c.id
            ORDER BY f.mfg, f.firearm_type
        """)

    def get_configuration_by_id(self, config_id: int) -> Optional[Dict[str, Any]]:
        result = self.execute_query("SELECT * FROM configurations WHERE id = ?", (config_id,))
        return result[0] if result else None

    def delete_configuration(self, config_id: int) -> bool:
        return self.execute_write("DELETE FROM configurations WHERE id = ?", (config_id,)) > 0

    # --- CRUD: Range Sessions ---

    def add_range_session(self, data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO range_sessions (
            configuration_id, date, location, rounds_fired,
            target_range, wind_speed, wind_angle, temperature, humidity,
            vel_avg, vel_max, vel_std_dev, vel_ext_spread,
            moa_avg, moa_best, moa_std_dev, moa_ext_spread,
            rating, photo_path, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get('configuration_id'),
            data.get('date'),
            data.get('location'),
            data.get('rounds_fired'),
            data.get('target_range'),
            data.get('wind_speed'),
            data.get('wind_angle'),
            data.get('temperature'),
            data.get('humidity'),
            data.get('vel_avg'),
            data.get('vel_max'),
            data.get('vel_std_dev'),
            data.get('vel_ext_spread'),
            data.get('moa_avg'),
            data.get('moa_best'),
            data.get('moa_std_dev'),
            data.get('moa_ext_spread'),
            data.get('rating'),
            data.get('photo_path'),
            data.get('notes')
        )
        return self.execute_write(query, params)

    def update_range_session(self, session_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing range session."""
        fields = []
        params = []
        for key, value in data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                params.append(value)

        if not fields:
            return False

        params.append(session_id)
        query = f"UPDATE range_sessions SET {', '.join(fields)} WHERE id = ?"
        return self.execute_write(query, tuple(params)) > 0

    def get_all_range_sessions(self) -> List[Dict[str, Any]]:
        return self.execute_query("""
            SELECT rs.*,
                   f.name as firearm_name, f.mfg as firearm_mfg, f.firearm_type as firearm_type,
                   o.mfg as optic_mfg, o.model as optic_model,
                   a.mfg as ammo_mfg, a.caliber as caliber, a.ammo_name as ammo_name
            FROM range_sessions rs
            LEFT JOIN configurations c ON rs.configuration_id = c.id
            LEFT JOIN firearms f ON c.firearm_id = f.id
            LEFT JOIN optics o ON c.optic_id = o.id
            LEFT JOIN ammo_loads a ON c.ammo_id = a.id
            ORDER BY rs.date DESC
        """)

    def get_sessions_for_configuration(self, config_id: int) -> List[Dict[str, Any]]:
        return self.execute_query(
            "SELECT * FROM range_sessions WHERE configuration_id = ? ORDER BY date DESC",
            (config_id,)
        )

    def get_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get a single range session by ID."""
        result = self.execute_query("SELECT * FROM range_sessions WHERE id = ?", (session_id,))
        return result[0] if result else None

    def delete_range_session(self, session_id: int) -> bool:
        """Delete a range session."""
        return self.execute_write("DELETE FROM range_sessions WHERE id = ?", (session_id,)) > 0

    def get_total_rounds_for_configuration(self, config_id: int) -> int:
        result = self.execute_query(
            "SELECT SUM(rounds_fired) as total FROM range_sessions WHERE configuration_id = ?",
            (config_id,)
        )
        return result[0]['total'] if result and result[0]['total'] else 0

    def count_range_sessions(self) -> int:
        result = self.execute_query("SELECT COUNT(*) as count FROM range_sessions")
        return result[0]['count'] if result else 0

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None




    #=====================================================================
    # REPORTS & ANALYTICS
    def get_accuracy_leaderboard(self, min_rounds=20):
        """
        Returns a list of configurations ranked by Avg MOA, filtered by minimum rounds.
        Returns: List of dicts containing config details, ammo info, and stats.
        """
        query = """
            SELECT
                c.id as config_id,
                f.name as firearm_name,
                f.firearm_type,
                f.mfg as firearm_mfg,
                COALESCE(o.mfg, 'None') as optic_mfg,
                COALESCE(o.optic_type, 'None') as optic_type,
                COALESCE(o.model, 'None') as optic_model,
                COALESCE(a.mfg, 'None') as ammo_mfg,
                COALESCE(a.caliber, 'None') as ammo_caliber,
                COALESCE(a.ammo_name, 'None') as ammo_name,
                SUM(rs.rounds_fired) as total_rounds,
                AVG(rs.moa_avg) as avg_moa,
                AVG(rs.moa_std_dev) as avg_std_dev
            FROM range_sessions rs
            JOIN configurations c ON rs.configuration_id = c.id
            JOIN firearms f ON c.firearm_id = f.id
            LEFT JOIN optics o ON c.optic_id = o.id
            LEFT JOIN ammo_loads a ON c.ammo_id = a.id
            GROUP BY c.id
            HAVING SUM(rs.rounds_fired) >= ?
            ORDER BY avg_moa ASC
        """

        try:
            cursor = self.conn.execute(query, (min_rounds,))
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    'config_id': row[0],
                    'firearm_name': row[1],
                    'firearm_type': row[2],
                    'firearm_mfg': row[3],
                    'optic_mfg': row[4],
                    'optic_type': row[5],
                    'optic_model': row[6],
                    'ammo_mfg': row[7],
                    'ammo_caliber': row[8],
                    'ammo_name': row[9],
                    'total_rounds': row[10],
                    'avg_moa': row[11],
                    'avg_std_dev': row[12]
                })
            return results
        except Exception as e:
            print(f"Error fetching accuracy leaderboard: {e}")
            return []

    def get_firearm_performance_summary(self, firearm_id: int):
        """
        Returns total rounds and the top ammo for a specific firearm.
        Top Ammo is determined by highest average rating (min 10 rounds).
        Returns: {'total_rounds': int, 'top_ammo': dict or None}
        """
        # 1. Get Total Rounds
        total_query = """
            SELECT SUM(rs.rounds_fired) as total
            FROM range_sessions rs
            JOIN configurations c ON rs.configuration_id = c.id
            WHERE c.firearm_id = ?
        """
        total_result = self.execute_query(total_query, (firearm_id,))
        total_rounds = total_result[0]['total'] if total_result and total_result[0]['total'] else 0

        # 2. Get Top Ammo
        top_ammo_query = """
            SELECT a.id, a.mfg, a.ammo_name, a.caliber,
                   AVG(
                       CASE rs.rating
                           WHEN 'bad' THEN 1
                           WHEN 'poor' THEN 2
                           WHEN 'OK' THEN 3
                           WHEN 'good' THEN 4
                           WHEN 'very good' THEN 5
                           WHEN 'excellent' THEN 6
                           ELSE NULL
                       END
                   ) as avg_score,
                   SUM(rs.rounds_fired) as total_rounds
            FROM range_sessions rs
            JOIN configurations c ON rs.configuration_id = c.id
            JOIN ammo_loads a ON c.ammo_id = a.id
            WHERE c.firearm_id = ?
            GROUP BY a.id
            HAVING SUM(rs.rounds_fired) >= 10
            ORDER BY avg_score DESC, total_rounds DESC
            LIMIT 1
        """
        top_ammo_result = self.execute_query(top_ammo_query, (firearm_id,))

        top_ammo = None
        if top_ammo_result:
            row = top_ammo_result[0]
            # Convert score back to text
            score = row['avg_score']
            rating_text = "No Rating"
            if score:
                if score < 1.5: rating_text = "Bad"
                elif score < 2.5: rating_text = "Poor"
                elif score < 3.5: rating_text = "OK"
                elif score < 4.5: rating_text = "Good"
                elif score < 5.5: rating_text = "Very Good"
                else: rating_text = "Excellent"

            top_ammo = {
                'mfg': row['mfg'],
                'name': row['ammo_name'],
                'caliber': row['caliber'],
                'rating': rating_text,
                'score': score,
                'rounds': row['total_rounds']
            }

        return {'total_rounds': total_rounds, 'top_ammo': top_ammo}

    def get_top_configs_for_caliber(self, caliber: str):
        """
        Returns top 3 configurations for a specific caliber.
        Ordered by Avg Rating (desc), then Total Rounds (desc).
        Min 10 rounds required.
        Returns: List of dicts with config details and stats.
        """
        query = """
            SELECT c.id, f.name as firearm_name, f.mfg as firearm_mfg,
                   o.mfg as optic_mfg, o.model as optic_model,
                   a.mfg as ammo_mfg, a.ammo_name as ammo_name,
                   AVG(
                       CASE rs.rating
                           WHEN 'bad' THEN 1
                           WHEN 'poor' THEN 2
                           WHEN 'OK' THEN 3
                           WHEN 'good' THEN 4
                           WHEN 'very good' THEN 5
                           WHEN 'excellent' THEN 6
                           ELSE NULL
                       END
                   ) as avg_score,
                   SUM(rs.rounds_fired) as total_rounds
            FROM range_sessions rs
            JOIN configurations c ON rs.configuration_id = c.id
            JOIN firearms f ON c.firearm_id = f.id
            LEFT JOIN optics o ON c.optic_id = o.id
            JOIN ammo_loads a ON c.ammo_id = a.id
            WHERE a.caliber = ?
            GROUP BY c.id
            HAVING SUM(rs.rounds_fired) >= 10
            ORDER BY avg_score DESC, total_rounds DESC
            LIMIT 3
        """
        results = self.execute_query(query, (caliber,))

        formatted_results = []
        for row in results:
            score = row['avg_score']
            rating_text = "No Rating"
            if score:
                if score < 1.5: rating_text = "Bad"
                elif score < 2.5: rating_text = "Poor"
                elif score < 3.5: rating_text = "OK"
                elif score < 4.5: rating_text = "Good"
                elif score < 5.5: rating_text = "Very Good"
                else: rating_text = "Excellent"

            formatted_results.append({
                'firearm': f"{row['firearm_mfg']} {row['firearm_name']}",
                'optic': f"{row['optic_mfg']} {row['optic_model']}" if row['optic_mfg'] else "None",
                'ammo': f"{row['ammo_mfg']} {row['ammo_name']}",
                'rating': rating_text,
                'score': score,
                'rounds': row['total_rounds']
            })

        return formatted_results

    def get_configuration_stats(self, config_id: int):
        """
        Returns Avg Velocity and Avg MOA for a specific configuration.
        Returns: {'avg_vel': float, 'avg_moa': float, 'sessions': int}
        """
        query = """
            SELECT AVG(rs.vel_avg) as avg_vel,
                   AVG(rs.moa_avg) as avg_moa,
                   COUNT(rs.id) as session_count
            FROM range_sessions rs
            WHERE rs.configuration_id = ?
        """
        result = self.execute_query(query, (config_id,))

        if result and result[0]:
            row = result[0]
            return {
                'avg_vel': row['avg_vel'],
                'avg_moa': row['avg_moa'],
                'sessions': row['session_count']
            }
        return {'avg_vel': None, 'avg_moa': None, 'sessions': 0}

    def get_top_firearms_for_ammo(self, ammo_mfg: str, caliber: str):
        """
        Returns top 3 firearms using a specific Ammo Mfg and Caliber.
        Ordered by Avg Rating (desc), then Total Rounds (desc).
        Min 10 rounds required.
        Returns: List of dicts with firearm details and stats.
        """
        query = """
            SELECT f.id, f.name as firearm_name, f.mfg as firearm_mfg,
                   AVG(
                       CASE rs.rating
                           WHEN 'bad' THEN 1
                           WHEN 'poor' THEN 2
                           WHEN 'OK' THEN 3
                           WHEN 'good' THEN 4
                           WHEN 'very good' THEN 5
                           WHEN 'excellent' THEN 6
                           ELSE NULL
                       END
                   ) as avg_score,
                   SUM(rs.rounds_fired) as total_rounds
            FROM range_sessions rs
            JOIN configurations c ON rs.configuration_id = c.id
            JOIN firearms f ON c.firearm_id = f.id
            JOIN ammo_loads a ON c.ammo_id = a.id
            WHERE a.mfg = ? AND a.caliber = ?
            GROUP BY f.id
            HAVING SUM(rs.rounds_fired) >= 10
            ORDER BY avg_score DESC, total_rounds DESC
            LIMIT 3
        """
        results = self.execute_query(query, (ammo_mfg, caliber))

        formatted_results = []
        for row in results:
            score = row['avg_score']
            rating_text = "No Rating"
            if score:
                if score < 1.5: rating_text = "Bad"
                elif score < 2.5: rating_text = "Poor"
                elif score < 3.5: rating_text = "OK"
                elif score < 4.5: rating_text = "Good"
                elif score < 5.5: rating_text = "Very Good"
                else: rating_text = "Excellent"

            formatted_results.append({
                'firearm': f"{row['firearm_mfg']} {row['firearm_name']}",
                'rating': rating_text,
                'score': score,
                'rounds': row['total_rounds']
            })

        return formatted_results


# Global instance
db_manager = DatabaseManager()
