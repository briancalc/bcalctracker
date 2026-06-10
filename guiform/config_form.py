# guiform/config_form.py
"""
Handles linking a Firearm, Optic, and Ammo Record.
"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from guiform import custom_dialogs as messagebox
from typing import Optional, Callable, Dict, Any

from guiform.constants import (
    COLOR_BG_FRAME, COLOR_LABEL, COLOR_ERROR_TEXT,
    FONT_FAMILY, LABEL_FONT_SIZE, UNIT_FONT_SIZE, TITLE_FONT_SIZE,
    MAIN_CONTAINER_PADDING, BUTTON_PADX
)
from database import db_manager
#from data_loaders import RANGE_RESULTS

class ConfigForm:
    """Modal dialog for creating or editing a configuration."""

    def __init__(self, parent, on_save: Callable[[Dict[str, Any]], None], config_data: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.on_save = on_save
        self.is_edit_mode = config_data is not None
        self.config_data = config_data or {}

        # Window Setup
        self.top = ttk.Toplevel(parent)
        self.top.title("Bcalc Firearm Management")
        self.top.geometry("800x550")
        self.top.transient(parent)

        # Variables
        self.firearm_var = tk.StringVar()
        self.optic_var = tk.StringVar()
        self.ammo_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        #self.performance_var = tk.StringVar()

        # Data Lists
        self.firearms_list = []
        self.optics_list = []
        self.ammo_list = []

        # Load Data
        self._load_data()

        # Pre-fill if editing
        if self.is_edit_mode:

            fire_id = self.config_data.get('firearm_id')
            for f in self.firearms_list:
                if f['id'] == fire_id:
                    self.firearm_var.set(f"{f['firearm_type']} | {f['mfg']} | {f['name']}")
                    break

            # Optic
            if self.config_data.get('optic_id'):
                optic_id = self.config_data.get('optic_id')
                for o in self.optics_list:
                    if o['id'] == optic_id:
                        self.optic_var.set(f"{o['mfg']} | {o['optic_type']} | {o.get('model', '')}")
                        break
            else:
                self.optic_var.set("None")

            # Ammo
            if self.config_data.get('ammo_id'):
                ammo_id = self.config_data.get('ammo_id')
                for a in self.ammo_list:
                    if a['id'] == ammo_id:
                        grains = str(a.get('grains', ''))
                        self.ammo_var.set(f"{a['caliber']} | {a['mfg']} | {grains} | {a.get('ammo_name', '')}")
                        break
            else:
                self.ammo_var.set("None")

            self.notes_var.set(self.config_data.get('config_notes', ''))


        self._build_ui()

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

    def _load_data(self) -> None:

        try:
            # Firearms (Required)
            self.firearms_list = db_manager.get_active_firearms()

            # Optics (Optional)
            self.optics_list = db_manager.get_all_optics()

            # Ammo (Optional)
            self.ammo_list = db_manager.get_all_ammo()
        except Exception as e:
            messagebox.showerror(self.top,"Database Error", f"Failed to load data: {e}")
            self.top.destroy()

    def _build_ui(self) -> None:
        """Construct the form layout."""
        main_frame = ttk.Frame(self.top, padding=MAIN_CONTAINER_PADDING)
        main_frame.pack(fill=BOTH, expand=True)

        # Header
        title_text = "Edit Configuration" if self.is_edit_mode else "Add New Configuration"
        ttk.Label(main_frame, text=title_text, font=(FONT_FAMILY, TITLE_FONT_SIZE, "bold"),
                  foreground=COLOR_ERROR_TEXT).pack(pady=(0, 15))

        # --- Section 1: Loadout Details ---
        section1 = ttk.LabelFrame(main_frame, text="Select Components")
        section1.pack(fill=X, pady=10, padx=10)
        section1.grid_columnconfigure(1, weight=1)

        # Row 0: Firearm (Required)
        self._create_row(section1, "Firearm:", self.firearm_var, 0, 0,
                         is_combo=True, values=self._get_firearm_options())

        # Row 1: Optic (Optional)
        self._create_row(section1, "Optic:", self.optic_var, 1, 0,
                         is_combo=True, values=self._get_optic_options())

        # Row 2: Ammo (Optional)
        self._create_row(section1, "Ammo Record:", self.ammo_var, 2, 0,
                         is_combo=True, values=self._get_ammo_options())

        # --- Section 2: Notes ---
        section2 = ttk.LabelFrame(main_frame, text="Configuration Notes")
        section2.pack(fill=X, pady=10, padx=10)

        notes_entry = ttk.Entry(section2, textvariable=self.notes_var, width=60)
        notes_entry.pack(fill=X, padx=5, pady=5)
        self._bind_entry_keys(notes_entry)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Save", bootstyle="primary", command=self._save).pack(side=LEFT, padx=BUTTON_PADX)
        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.top.destroy).pack(side=LEFT, padx=BUTTON_PADX)

        # Focus on first field
        try:
            if hasattr(self, 'firearm_entry'):
                self.firearm_entry.focus_set()
        except:
            pass

        # Keyboard shortcuts
        self.top.bind("<Escape>", lambda e: self.top.destroy())
        self.top.bind("<Control-s>", lambda e: self._save())

    def _get_firearm_options(self) -> list:
        """Return list of 'Type | Mfg | Name' for dropdown."""
        return [f"{f['firearm_type']} | {f['mfg']} | {f['name']}" for f in self.firearms_list]

    def _get_optic_options(self) -> list:
        """Return list with 'None' + 'Mfg | Type | Model'."""
        opts = ["None"]
        opts.extend([f"{o['mfg']} | {o['optic_type']} | {o.get('model', '')}" for o in self.optics_list])
        return opts

    def _get_ammo_options(self) -> list:
        """Return list with 'None' + 'Caliber | Mfg | Grains | Name'."""
        opts = ["None"]
        opts.extend([f"{a['caliber']} | {a['mfg']} | {a.get('grains', '')} | {a.get('ammo_name', '')}" for a in self.ammo_list])
        return opts

    def _create_row(self, parent: ttk.Frame, label: str, var: tk.StringVar, row: int, col: int,
                    is_combo: bool = False, values: list = None) -> tk.Widget:
        """Create a standard combo row."""
        col_label = col * 2
        col_entry = col * 2 + 1

        ttk.Label(parent, text=label, font=(FONT_FAMILY, LABEL_FONT_SIZE, "bold")).grid(
            row=row, column=col_label, sticky=W, pady=6, padx=(5, 15)
        )

        if is_combo and values:
            entry = ttk.Combobox(parent, textvariable=var, values=values, width=50, state="readonly")
            # Only set default index if the variable is empty (i.e., new record)
            if not var.get():
                entry.current(0)
        else:
            entry = ttk.Entry(parent, textvariable=var, width=50)

        entry.grid(row=row, column=col_entry, sticky=E+W, pady=6, padx=(0, 5))
        self._bind_entry_keys(entry)
        if row == 0 and col == 0:
            self.firearm_entry = entry

        return entry

    def _save(self) -> None:
        # Get selected display strings
        fire_str = self.firearm_var.get()
        optic_str = self.optic_var.get()
        ammo_str = self.ammo_var.get()

        # 1. Validate Firearm (Required)
        if not fire_str or fire_str == "None":
            messagebox.showwarning(self.top,"Validation Error", "A Firearm is required.")
            return

        # Find Firearm ID
        fire_id = None
        for f in self.firearms_list:
            if f"{f['firearm_type']} | {f['mfg']} | {f['name']}" == fire_str:
                fire_id = f['id']
                break

        if not fire_id:
            messagebox.showerror(self.top,"Error", "Selected firearm not found.")
            return

        # 2. Resolve Optic ID (Optional)
        optic_id = None
        if optic_str and optic_str != "None":
            for o in self.optics_list:
                if f"{o['mfg']} | {o['optic_type']} | {o.get('model', '')}" == optic_str:
                    optic_id = o['id']
                    break

        # 3. Resolve Ammo ID (Optional)
        ammo_id = None
        if ammo_str and ammo_str != "None":
            for a in self.ammo_list:
                grains = str(a.get('grains', ''))
                if f"{a['caliber']} | {a['mfg']} | {grains} | {a.get('ammo_name', '')}" == ammo_str:
                    ammo_id = a['id']
                    break

        # Prepare Data
        data = {
            'firearm_id': fire_id,
            'optic_id': optic_id,
            'ammo_id': ammo_id,
            #'performance_rating': self.performance_var.get().strip() or None,
            'config_notes': self.notes_var.get().strip()
        }

        # 4. CHECK FOR DUPLICATES
        if not self.is_edit_mode:

            try:

                query = """
                    SELECT id FROM configurations
                    WHERE firearm_id = ?
                    AND (optic_id IS ? OR optic_id = ?)
                    AND (ammo_id IS ? OR ammo_id = ?)
                """

                all_configs = db_manager.get_all_configurations()
                for c in all_configs:
                    c_fire = c.get('firearm_id')
                    c_optic = c.get('optic_id')
                    c_ammo = c.get('ammo_id')

                    # Check match
                    if c_fire == fire_id and c_optic == optic_id and c_ammo == ammo_id:

                        response = messagebox.askyesno(
                            self.top,
                            "Duplicate Configuration",
                            "This configuration (Firearm + Optic + Ammo) already exists.\n\n"
                            "Do you want to UPDATE the existing record?\n"
                            "(Click 'No' to cancel)."
                        )
                        if response:

                            self.is_edit_mode = True
                            self.config_data = c

                            break
                        else:

                            return
            except Exception as e:
                messagebox.showerror(self.top,"Database Error", f"Error checking for duplicates: {e}")
                return

        # 5. SAVE (Either New or Update)
        try:
            if self.is_edit_mode:

                if 'id' not in self.config_data:

                     pass

                db_manager.update_configuration(self.config_data['id'], data)
                messagebox.showinfo(self.top,"Success", "Configuration updated successfully.")
            else:
                new_id = db_manager.add_configuration(data)
                data['id'] = new_id
                messagebox.showinfo(self.top,"Success", "Configuration added successfully.")

            if self.on_save:
                self.on_save(data)
            self.top.destroy()

        except Exception as e:
            messagebox.showerror(self.top,"Database Error", f"Failed to save: {e}")

    def destroy(self):
        self.top.destroy()
