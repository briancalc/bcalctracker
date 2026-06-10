# guiform/range_form.py

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from guiform import custom_dialogs as messagebox
import subprocess
from typing import Optional, Callable, Dict, Any

from guiform.constants import (
    COLOR_BG_FRAME, COLOR_LABEL, COLOR_ERROR_TEXT,
    FONT_FAMILY, LABEL_FONT_SIZE, UNIT_FONT_SIZE, TITLE_FONT_SIZE,
    MAIN_CONTAINER_PADDING, BUTTON_PADX
)
from data_loaders import RANGE_RESULTS
from database import db_manager


class RangeForm:


    def __init__(self, parent, on_save: Callable[[Dict[str, Any]], None], session_data: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.on_save = on_save
        self.is_edit_mode = session_data is not None
        self.session_data = session_data or {}

        # Window Setup
        self.top = ttk.Toplevel(parent)
        self.top.title("Bcalc Firearm Management - Range Session")
        self.top.geometry("850x700")
        self.top.transient(parent)

        # Variables - Session Details
        self.config_id_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.location_var = tk.StringVar()

        # Variables - Performance & Condition Data
        self.rounds_var = tk.StringVar()
        self.target_range_var = tk.StringVar()
        self.wind_speed_var = tk.StringVar()
        self.vel_avg_var = tk.StringVar()
        self.moa_avg_var = tk.StringVar()
        self.wind_angle_var = tk.StringVar()
        self.vel_max_var = tk.StringVar()
        self.moa_best_var = tk.StringVar()
        self.temperature_var = tk.StringVar()
        self.vel_std_dev_var = tk.StringVar()
        self.moa_std_dev_var = tk.StringVar()
        self.humidity_var = tk.StringVar()
        self.vel_ext_spread_var = tk.StringVar()
        self.moa_ext_spread_var = tk.StringVar()
        self.rating_var = tk.StringVar()

        # Variables - Photo & Notes
        self.photo_path_var = tk.StringVar()
        self.notes_var = tk.StringVar()

        # Load Configurations for Dropdown
        self.config_options = []
        self._load_configurations()

        # Pre-fill if editing
        if self.is_edit_mode:

            config_id = self.session_data.get('configuration_id')
            if config_id:
                for cid, display in self.config_options:
                    if cid == config_id:
                        self.config_id_var.set(display)
                        break

            self.date_var.set(self.session_data.get('date', ''))
            self.location_var.set(self.session_data.get('location', ''))
            self.rounds_var.set(str(self.session_data.get('rounds_fired', '')) if self.session_data.get('rounds_fired') is not None else '')
            self.target_range_var.set(str(self.session_data.get('target_range', '')) if self.session_data.get('target_range') is not None else '')
            self.wind_speed_var.set(str(self.session_data.get('wind_speed', '')) if self.session_data.get('wind_speed') is not None else '')
            self.wind_angle_var.set(str(self.session_data.get('wind_angle', '')) if self.session_data.get('wind_angle') is not None else '')
            self.temperature_var.set(str(self.session_data.get('temperature', '')) if self.session_data.get('temperature') is not None else '')
            self.humidity_var.set(str(self.session_data.get('humidity', '')) if self.session_data.get('humidity') is not None else '')
            self.vel_avg_var.set(str(self.session_data.get('vel_avg', '')) if self.session_data.get('vel_avg') is not None else '')
            self.vel_max_var.set(str(self.session_data.get('vel_max', '')) if self.session_data.get('vel_max') is not None else '')
            self.vel_std_dev_var.set(str(self.session_data.get('vel_std_dev', '')) if self.session_data.get('vel_std_dev') is not None else '')
            self.vel_ext_spread_var.set(str(self.session_data.get('vel_ext_spread', '')) if self.session_data.get('vel_ext_spread') is not None else '')
            self.moa_avg_var.set(str(self.session_data.get('moa_avg', '')) if self.session_data.get('moa_avg') is not None else '')
            self.moa_best_var.set(str(self.session_data.get('moa_best', '')) if self.session_data.get('moa_best') is not None else '')
            self.moa_std_dev_var.set(str(self.session_data.get('moa_std_dev', '')) if self.session_data.get('moa_std_dev') is not None else '')
            self.moa_ext_spread_var.set(str(self.session_data.get('moa_ext_spread', '')) if self.session_data.get('moa_ext_spread') is not None else '')
            self.rating_var.set(self.session_data.get('rating', ''))
            self.photo_path_var.set(self.session_data.get('photo_path', ''))
            self.notes_var.set(self.session_data.get('notes', ''))

        self._build_ui()

    def _load_configurations(self) -> None:
        """Fetch all configurations and format them for the dropdown."""
        try:
            configs = db_manager.get_all_configurations()
            # Format: "Firearm Name | Optic Mfg | Ammo Mfg | Caliber"
            for c in configs:
                fname = c.get('firearm_name', 'Unknown')
                omfg = c.get('optic_mfg') or 'None'
                amfg = c.get('ammo_mfg') or 'None'
                caliber = c.get('caliber') or 'Unknown'

                display_str = f"{fname} | {omfg} | {amfg} | {caliber}"
                self.config_options.append((c['id'], display_str))
        except Exception as e:
            print(f"Error loading configurations: {e}")
            self.config_options = []

    def _on_entry_backspace(self, event):
        """Custom handler for Backspace."""
        widget = event.widget

        if isinstance(widget, ttk.Combobox) and widget.cget('state') == 'readonly':
            return 'break'
        current_text = widget.get()
        cursor_pos = widget.index(tk.INSERT)
        if cursor_pos > 0:
            new_text = current_text[:cursor_pos-1] + current_text[cursor_pos:]
            widget.delete(0, tk.END)
            widget.insert(0, new_text)
            widget.icursor(cursor_pos - 1)
        return 'break'

    def _on_entry_delete(self, event):
        """Custom handler for Delete."""
        widget = event.widget

        if isinstance(widget, ttk.Combobox) and widget.cget('state') == 'readonly':
            return 'break'
        current_text = widget.get()
        cursor_pos = widget.index(tk.INSERT)
        if cursor_pos < len(current_text):
            new_text = current_text[:cursor_pos] + current_text[cursor_pos+1:]
            widget.delete(0, tk.END)
            widget.insert(0, new_text)
            widget.icursor(cursor_pos)
        return 'break'

    def _bind_entry_keys(self, widget) -> None:
        """Bind Backspace and Delete."""
        widget.bind('<BackSpace>', self._on_entry_backspace)
        widget.bind('<Delete>', self._on_entry_delete)

    def _build_ui(self) -> None:

        main_frame = ttk.Frame(self.top, padding=MAIN_CONTAINER_PADDING)
        main_frame.pack(fill=BOTH, expand=True)

        # Header
        title_text = "Edit Range Session" if self.is_edit_mode else "Add New Range Session"
        ttk.Label(main_frame, text=title_text, font=(FONT_FAMILY, TITLE_FONT_SIZE, "bold"),
                  foreground=COLOR_ERROR_TEXT).pack(pady=(0, 15))

        # --- Section 1: Session Details ---
        section1 = ttk.LabelFrame(main_frame, text="Session Details")
        section1.pack(fill=X, pady=10, padx=10)
        section1.grid_columnconfigure(1, weight=1)
        section1.grid_columnconfigure(3, weight=1)

        # Row 0: Configuration
        ttk.Label(section1, text="Configuration:", font=(FONT_FAMILY, LABEL_FONT_SIZE, "bold")).grid(
            row=0, column=0, sticky=W, pady=6, padx=(5, 15))

        if self.config_options:
            combo = ttk.Combobox(section1, textvariable=self.config_id_var,
                                 values=[opt[1] for opt in self.config_options],
                                 width=60, state="readonly")
            if not self.is_edit_mode and self.config_options:
                combo.current(0)
        else:
            combo = ttk.Entry(section1, textvariable=self.config_id_var, width=60, state="disabled")
            combo.insert(0, "No configurations available")

        combo.grid(row=0, column=1, columnspan=3, sticky=E+W, pady=6, padx=(0, 5))

        self._bind_entry_keys(combo)

        # Row 1: Date, Location
        self._create_row(section1, "Date (YYYY-MM-DD):", self.date_var, 1, 0)
        self._create_row(section1, "Location:", self.location_var, 1, 1)

        # --- Section 2: Performance & Condition Data ---
        section2 = ttk.LabelFrame(main_frame, text="Performance & Condition Data")
        section2.pack(fill=X, pady=10, padx=10)
        section2.grid_columnconfigure(1, weight=1)
        section2.grid_columnconfigure(3, weight=1)
        section2.grid_columnconfigure(5, weight=1)

        # Row 1: Rounds Fired, Target Range, Wind Speed
        self._create_row(section2, "Rounds Fired:", self.rounds_var, 0, 0)
        self._create_row(section2, "Target Range:", self.target_range_var, 0, 1)
        self._create_row(section2, "Wind Speed:", self.wind_speed_var, 0, 2)

        # Row 2: Avg Muzzle Velocity, Avg MOA, Wind Direction
        self._create_row(section2, "Avg Muzzle Vel:", self.vel_avg_var, 1, 0)
        self._create_row(section2, "Avg MOA:", self.moa_avg_var, 1, 1)
        self._create_row(section2, "Wind Dir (0-359):", self.wind_angle_var, 1, 2)

        # Row 3: Highest Muzzle Velocity, Best MOA, Temperature
        self._create_row(section2, "Max Muzzle Vel:", self.vel_max_var, 2, 0)
        self._create_row(section2, "Best MOA:", self.moa_best_var, 2, 1)
        self._create_row(section2, "Temperature:", self.temperature_var, 2, 2)

        # Row 4: Std Dev Muzzle Velocity, Std Dev MOA, Humidity
        self._create_row(section2, "Std Dev Vel:", self.vel_std_dev_var, 3, 0)
        self._create_row(section2, "Std Dev MOA:", self.moa_std_dev_var, 3, 1)
        self._create_row(section2, "Humidity:", self.humidity_var, 3, 2)

        # Row 5: Ext Spread Muzzle Velocity, Ext Spread MOA, Rating (Combo)
        self._create_row(section2, "Ext Spread Vel:", self.vel_ext_spread_var, 4, 0)
        self._create_row(section2, "Ext Spread MOA:", self.moa_ext_spread_var, 4, 1)

        # Rating Combobox
        col_label = 2 * 2
        col_entry = 2 * 2 + 1
        ttk.Label(section2, text="Rating:", font=(FONT_FAMILY, LABEL_FONT_SIZE, "bold")).grid(
            row=4, column=col_label, sticky=W, pady=6, padx=(5, 15))

        rating_combo = ttk.Combobox(section2, textvariable=self.rating_var, values=RANGE_RESULTS,
                                    width=25, state="readonly")
        if not self.is_edit_mode and RANGE_RESULTS:
            rating_combo.current(0)
        rating_combo.grid(row=4, column=col_entry, sticky=E+W, pady=6, padx=(0, 5))

        self._bind_entry_keys(rating_combo)

        # --- Section 3: Photo & Notes ---
        section3 = ttk.LabelFrame(main_frame, text="Photo & Notes")
        section3.pack(fill=X, pady=10, padx=10)
        section3.grid_columnconfigure(1, weight=1)

        # Row 0: Photo Path + Browse Button
        ttk.Label(section3, text="Target Photo:", font=(FONT_FAMILY, LABEL_FONT_SIZE, "bold")).grid(
            row=0, column=0, sticky=W, pady=6, padx=(5, 15))

        photo_entry = ttk.Entry(section3, textvariable=self.photo_path_var, width=40, state="readonly")
        photo_entry.grid(row=0, column=1, sticky=E+W, pady=6, padx=(0, 5))

        self._bind_entry_keys(photo_entry)

        browse_btn = ttk.Button(section3, text="Browse...", width=10, command=self._browse_photo)
        browse_btn.grid(row=0, column=2, sticky=W, pady=6, padx=(0, 5))

        # Row 1: Notes
        self._create_row(section3, "Notes:", self.notes_var, 1, 0)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Save", bootstyle="primary", command=self._save).pack(side=LEFT, padx=BUTTON_PADX)
        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.top.destroy).pack(side=LEFT, padx=BUTTON_PADX)

        # Focus
        try:
            if hasattr(self, 'date_var'):
                # Find the date entry widget roughly
                pass
        except:
            pass

        self.top.bind("<Escape>", lambda e: self.top.destroy())
        self.top.bind("<Control-s>", lambda e: self._save())

    def _create_row(self, parent: ttk.Frame, label: str, var: tk.StringVar, row: int, col: int) -> tk.Widget:

        col_label = col * 2
        col_entry = col * 2 + 1

        ttk.Label(parent, text=label, font=(FONT_FAMILY, LABEL_FONT_SIZE, "bold")).grid(
            row=row, column=col_label, sticky=W, pady=6, padx=(5, 15))

        entry = ttk.Entry(parent, textvariable=var, width=25)
        entry.grid(row=row, column=col_entry, sticky=E+W, pady=6, padx=(0, 5))
        self._bind_entry_keys(entry)
        return entry

    def _browse_photo(self) -> None:


        try:
            result = subprocess.run(
                ['zenity', '--file-selection', '--title=Select Target Photo',
                 '--file-filter=Image files | *.jpg *.jpeg *.png *.bmp *.gif',
                 '--file-filter=All files | *'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                filepath = result.stdout.strip()
                self.photo_path_var.set(filepath)
            return
        except FileNotFoundError:
            pass  # zenity not installed, try tkinter fallback
        except Exception as e:
            print(f"Zenity failed: {e}")

        # Fallback to tkinter
        try:
            filetypes = [
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
            filepath = filedialog.askopenfilename(
                title="Select Target Photo",
                filetypes=filetypes
            )
            if filepath:
                self.photo_path_var.set(filepath)
        except Exception as e:
            messagebox.showerror(
                self.top,
                "Error",
                f"File dialog failed. Please ensure zenity is installed:\n\n"
                f"sudo dnf install zenity\n\n"
                f"Technical error: {type(e).__name__}"
            )

    def _validate_numeric(self, value: str, field_name: str, allow_empty: bool = True) -> Optional[float]:
        """Validate numeric input."""
        value = value.strip()
        if not value:
            if allow_empty:
                return None
            raise ValueError(f"{field_name} is required.")
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{field_name} must be a valid number.")

    def _validate_ranged(self, value: str, field_name: str, min_val: float, max_val: float, allow_empty: bool = True) -> Optional[float]:
        """Validate numeric input within a specific range."""
        value = value.strip()
        if not value:
            if allow_empty:
                return None
            raise ValueError(f"{field_name} is required.")
        try:
            num = float(value)
        except ValueError:
            raise ValueError(f"{field_name} must be a valid number.")
        if num < min_val or num > max_val:
            raise ValueError(f"{field_name} must be between {min_val} and {max_val}.")
        return num

    def _save(self) -> None:
        # Collect Data
        selected_config_display = self.config_id_var.get()
        date_val = self.date_var.get().strip()
        location_val = self.location_var.get().strip()
        rounds_str = self.rounds_var.get().strip()
        target_range_str = self.target_range_var.get().strip()
        wind_speed_str = self.wind_speed_var.get().strip()
        wind_angle_str = self.wind_angle_var.get().strip()
        temperature_str = self.temperature_var.get().strip()
        humidity_str = self.humidity_var.get().strip()
        vel_avg_str = self.vel_avg_var.get().strip()
        vel_max_str = self.vel_max_var.get().strip()
        vel_std_dev_str = self.vel_std_dev_var.get().strip()
        vel_ext_spread_str = self.vel_ext_spread_var.get().strip()
        moa_avg_str = self.moa_avg_var.get().strip()
        moa_best_str = self.moa_best_var.get().strip()
        moa_std_dev_str = self.moa_std_dev_var.get().strip()
        moa_ext_spread_str = self.moa_ext_spread_var.get().strip()
        rating_val = self.rating_var.get().strip()
        photo_val = self.photo_path_var.get().strip()
        notes_val = self.notes_var.get().strip()

        # Validation - Required Fields
        if not selected_config_display:
            messagebox.showwarning(self.top,"Validation Error", "Configuration is required.")
            return
        if not date_val:
            messagebox.showwarning(self.top,"Validation Error", "Date is required.")
            return

        # Find Config ID
        config_id = None
        for cid, display in self.config_options:
            if display == selected_config_display:
                config_id = cid
                break

        if not config_id:
            messagebox.showerror(self.top,"Error", "Selected configuration not found in database.")
            return

        # Numeric Validation with Ranges
        try:
            rounds = self._validate_numeric(rounds_str, "Rounds Fired", allow_empty=True)
            target_range = self._validate_ranged(target_range_str, "Target Range", 0, 800)
            wind_speed = self._validate_ranged(wind_speed_str, "Wind Speed", 0, 50)
            wind_angle = self._validate_ranged(wind_angle_str, "Wind Direction", 0, 359)
            temperature = self._validate_ranged(temperature_str, "Temperature", -30, 130)
            humidity = self._validate_ranged(humidity_str, "Humidity", 0, 100)
            vel_avg = self._validate_ranged(vel_avg_str, "Avg Muzzle Velocity", 100, 5000)
            vel_max = self._validate_ranged(vel_max_str, "Max Muzzle Velocity", 100, 5000)
            vel_std_dev = self._validate_ranged(vel_std_dev_str, "Std Dev Velocity", 0, 100)
            vel_ext_spread = self._validate_ranged(vel_ext_spread_str, "Ext Spread Velocity", 0, 200)
            moa_avg = self._validate_numeric(moa_avg_str, "Avg MOA", allow_empty=True)
            moa_best = self._validate_numeric(moa_best_str, "Best MOA", allow_empty=True)
            moa_std_dev = self._validate_numeric(moa_std_dev_str, "Std Dev MOA", allow_empty=True)
            moa_ext_spread = self._validate_numeric(moa_ext_spread_str, "Ext Spread MOA", allow_empty=True)
        except ValueError as e:
            messagebox.showwarning(self.top,"Validation Error", str(e))
            return

        data = {
            'configuration_id': config_id,
            'date': date_val,
            'location': location_val,
            'rounds_fired': int(rounds) if rounds is not None else None,
            'target_range': target_range,
            'wind_speed': wind_speed,
            'wind_angle': wind_angle,
            'temperature': temperature,
            'humidity': humidity,
            'vel_avg': vel_avg,
            'vel_max': vel_max,
            'vel_std_dev': vel_std_dev,
            'vel_ext_spread': vel_ext_spread,
            'moa_avg': moa_avg,
            'moa_best': moa_best,
            'moa_std_dev': moa_std_dev,
            'moa_ext_spread': moa_ext_spread,
            'rating': rating_val,
            'photo_path': photo_val,
            'notes': notes_val
        }

        try:
            if self.is_edit_mode:
                if 'id' not in self.session_data:
                    messagebox.showerror(self.top,"Error", "Cannot edit: Session ID missing.")
                    return
                db_manager.update_range_session(self.session_data['id'], data)
                messagebox.showinfo(self.top,"Success", "Session updated successfully.")
            else:
                new_id = db_manager.add_range_session(data)
                data['id'] = new_id
                messagebox.showinfo(self.top,"Success", "Session added successfully.")

            if self.on_save:
                self.on_save(data)
            self.top.destroy()

        except Exception as e:
            messagebox.showerror(self.top,"Database Error", f"Failed to save: {e}")

    def destroy(self):
        self.top.destroy()
