# guiform/ammo_form.py
"""
User input for creating or updating ammo load records.
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

from data_loaders import (
    AMMO_MFG, CALIBERS, AMMO_USE_CASES,
    SHOT_SIZES, PROJECTILE_TYPES, BRASS_MFG, HULL_MFG, WAD_MFG,
    POWDER_MFG, PRIMER_MFG, PRIMER_TYPES, CRIMP_TYPES, BULLET_MFG,
    DRAG_FUNCTIONS
)
from database import db_manager


class AmmoForm:
    """Modal dialog for adding or editing an ammo load."""

    def __init__(self, parent, on_save: Callable[[Dict[str, Any]], None],
                 ammo_data: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.on_save = on_save
        self.is_edit_mode = ammo_data is not None
        self.ammo_data = ammo_data or {}

        self.top = ttk.Toplevel(parent)
        self.top.title("Bcalc Firearm Management")
        self.top.geometry("950x1000")
        self.top.transient(parent)

        # --- Variables: Basic Info ---
        self.mfg_var = tk.StringVar()
        self.caliber_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.use_var = tk.StringVar()
        self.grains_var = tk.StringVar()
        self.bullet_name_var = tk.StringVar()
        self.projectile_type_var = tk.StringVar()
        self.shot_size_var = tk.StringVar()
        self.pellet_count_var = tk.StringVar()
        self.do_not_rebuy_var = tk.BooleanVar(value=False)
        self.drag_func_var = tk.StringVar()
        self.bc_var = tk.StringVar()

        # --- Variables: Reloading Components ---
        self.brass_mfg_var = tk.StringVar()
        self.hull_mfg_var = tk.StringVar()
        self.wad_mfg_var = tk.StringVar()
        self.bullet_mfg_var = tk.StringVar()
        self.powder_mfg_var = tk.StringVar()
        self.powder_name_var = tk.StringVar()
        self.powder_lot_var = tk.StringVar()
        self.powder_grains_var = tk.StringVar()
        self.primer_mfg_var = tk.StringVar()
        self.primer_type_var = tk.StringVar()
        self.primer_lot_var = tk.StringVar()
        self.crimp_type_var = tk.StringVar()

        # --- Variables: Measurements & Batch ---
        self.case_weight_var = tk.StringVar()
        self.overall_length_var = tk.StringVar()
        self.cbto_var = tk.StringVar()
        self.date_loaded_var = tk.StringVar()
        self.batch_qty_var = tk.StringVar()

        # --- Variables: Notes ---
        self.notes_var = tk.StringVar()

        # Pre-fill if editing
        if self.is_edit_mode:
            self.mfg_var.set(self.ammo_data.get('mfg', ''))
            self.caliber_var.set(self.ammo_data.get('caliber', ''))
            self.name_var.set(self.ammo_data.get('ammo_name', ''))
            self.use_var.set(self.ammo_data.get('use_case', ''))
            self.bullet_name_var.set(self.ammo_data.get('bullet_name', ''))
            self.projectile_type_var.set(self.ammo_data.get('projectile_type', ''))
            self.shot_size_var.set(self.ammo_data.get('shot_size', ''))
            self.crimp_type_var.set(self.ammo_data.get('crimp_type', ''))
            self.drag_func_var.set(self.ammo_data.get('drag_function', ''))
            self.bc_var.set(str(self.ammo_data.get('ballistic_coeff', '')) if self.ammo_data.get('ballistic_coeff') is not None else '')
            self.date_loaded_var.set(self.ammo_data.get('date_loaded', ''))
            self.notes_var.set(self.ammo_data.get('notes', ''))

            # Reloading text fields
            self.brass_mfg_var.set(self.ammo_data.get('brass_mfg', ''))
            self.hull_mfg_var.set(self.ammo_data.get('hull_mfg', ''))
            self.wad_mfg_var.set(self.ammo_data.get('wad_mfg', ''))
            self.bullet_mfg_var.set(self.ammo_data.get('bullet_mfg', ''))
            self.powder_mfg_var.set(self.ammo_data.get('powder_mfg', ''))
            self.powder_name_var.set(self.ammo_data.get('powder_name', ''))
            self.powder_lot_var.set(self.ammo_data.get('powder_lot', ''))
            self.primer_mfg_var.set(self.ammo_data.get('primer_mfg', ''))
            self.primer_type_var.set(self.ammo_data.get('primer_type', ''))
            self.primer_lot_var.set(self.ammo_data.get('primer_lot', ''))

            # Numeric fields (guard against None -> "None" string)
            for attr, key in [
                ('grains_var', 'grains'),
                ('pellet_count_var', 'pellet_count'),
                ('powder_grains_var', 'powder_grains'),
                ('case_weight_var', 'case_weight'),
                ('overall_length_var', 'overall_length'),
                ('cbto_var', 'cbto'),
                ('batch_qty_var', 'batch_quantity'),
            ]:
                val = self.ammo_data.get(key)
                getattr(self, attr).set(str(val) if val is not None else '')

            if self.ammo_data.get('do_not_rebuy'):
                self.do_not_rebuy_var.set(True)

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
        """Bind Backspace and Delete to prevent window closure."""
        widget.bind('<BackSpace>', self._on_entry_backspace)
        widget.bind('<Delete>', self._on_entry_delete)



    def _build_ui(self) -> None:
        """Construct the form layout."""
        main_frame = ttk.Frame(self.top, padding=MAIN_CONTAINER_PADDING)
        main_frame.pack(fill=BOTH, expand=True)

        title_text = "Edit Ammo Record" if self.is_edit_mode else "Add New Ammo Record"
        ttk.Label(main_frame, text=title_text,
                  font=(FONT_FAMILY, TITLE_FONT_SIZE, "bold"),
                  foreground=COLOR_ERROR_TEXT).pack(pady=(0, 15))

        # --- Section 1: Basic Information ---
        s1 = ttk.LabelFrame(main_frame, text="Basic Information")
        s1.pack(fill=X, pady=10, padx=10)
        s1.grid_columnconfigure(1, weight=1)
        s1.grid_columnconfigure(3, weight=1)

        # Row 0: Manufacturer, Caliber
        self._create_row(s1, "Manufacturer:", self.mfg_var, 0, 0,
                         is_combo=True, values=AMMO_MFG)
        self._create_row(s1, "Caliber/ Gauge:", self.caliber_var, 0, 1,
                         is_combo=True, values=CALIBERS)

        # Row 1: Grains, Projectile Type
        self._create_row(s1, "Grains (Proj.):", self.grains_var, 1, 0)
        self._create_row(s1, "Projectile Type:", self.projectile_type_var, 1, 1,
                         is_combo=True, values=PROJECTILE_TYPES)

        # Row 2: Shot Size, # of Pellets
        self._create_row(s1, "Shot Size:", self.shot_size_var, 2, 0,
                         is_combo=True, values=SHOT_SIZES)
        self._create_row(s1, "# of Pellets:", self.pellet_count_var, 2, 1)

        # Row 3: Ammo Box Name, Use Case
        self._create_row(s1, "Ammo Box Name:", self.name_var, 3, 0)
        self._create_row(s1, "Use Case:", self.use_var, 3, 1,
                         is_combo=True, values=AMMO_USE_CASES)

        # Row 4: Drag Function, Ballistic Coefficient
        self._create_row(s1, "Drag Function:", self.drag_func_var, 4, 0,
                         is_combo=True, values=DRAG_FUNCTIONS)
        self._create_row(s1, "Ballistic Coeff:", self.bc_var, 4, 1)

        # Row 5: Do Not Rebuy Checkbox
        chk_frame = ttk.Frame(s1)
        chk_frame.grid(row=5, column=0, columnspan=4, sticky=W, pady=6, padx=(5, 5))
        ttk.Checkbutton(chk_frame, text="Do Not Rebuy (Poor Performance)",
                        variable=self.do_not_rebuy_var).pack(side=LEFT)

        # --- Section 2: Reloading Components ---
        s2 = ttk.LabelFrame(main_frame, text="Reloading Components (Optional)")
        s2.pack(fill=X, pady=10, padx=10)
        s2.grid_columnconfigure(1, weight=1)
        s2.grid_columnconfigure(3, weight=1)

        # Row 0: Bullet Mfg, Powder Mfg
        self._create_row(s2, "Bullet Mfg:", self.bullet_mfg_var, 0, 0,
                         is_combo=True, values=BULLET_MFG)
        self._create_row(s2, "Powder Mfg:", self.powder_mfg_var, 0, 1,
                         is_combo=True, values=POWDER_MFG)

        # Row 1: Bullet Name, Powder Name
        self._create_row(s2, "Bullet Name:", self.bullet_name_var, 1, 0)
        self._create_row(s2, "Powder Name:", self.powder_name_var, 1, 1)

        # Row 2: Brass Mfg, Powder Lot
        self._create_row(s2, "Brass Mfg:", self.brass_mfg_var, 2, 0,
                         is_combo=True, values=BRASS_MFG)
        self._create_row(s2, "Powder Lot:", self.powder_lot_var, 2, 1)

        # Row 3: Case Weight, Powder Grains
        self._create_row(s2, "Case Weight:", self.case_weight_var, 3, 0)
        self._create_row(s2, "Powder Grains:", self.powder_grains_var, 3, 1)

        # Row 4: Overall Length, Primer Mfg
        self._create_row(s2, "Overall Length:", self.overall_length_var, 4, 0)
        self._create_row(s2, "Primer Mfg:", self.primer_mfg_var, 4, 1,
                         is_combo=True, values=PRIMER_MFG)

        # Row 5: CBTO, Primer Type
        self._create_row(s2, "CBTO:", self.cbto_var, 5, 0)
        self._create_row(s2, "Primer Type:", self.primer_type_var, 5, 1,
                         is_combo=True, values=PRIMER_TYPES)

        # Row 6: Crimp Type, Primer Lot
        self._create_row(s2, "Crimp Type:", self.crimp_type_var, 6, 0,
                         is_combo=True, values=CRIMP_TYPES)
        self._create_row(s2, "Primer Lot:", self.primer_lot_var, 6, 1)

        # Row 7: Hull Mfg, Wad Mfg
        self._create_row(s2, "Hull Mfg:", self.hull_mfg_var, 7, 0,
                         is_combo=True, values=HULL_MFG)
        self._create_row(s2, "Wad Mfg:", self.wad_mfg_var, 7, 1,
                         is_combo=True, values=WAD_MFG)

        # --- Section 3: Batch Stamps ---
        s3 = ttk.LabelFrame(main_frame, text="Batch Stamps")
        s3.pack(fill=X, pady=10, padx=10)
        s3.grid_columnconfigure(1, weight=1)
        s3.grid_columnconfigure(3, weight=1)

        # Row 0: Batch Quantity, Date Loaded
        self._create_row(s3, "Batch Quantity:", self.batch_qty_var, 0, 0)
        self._create_row(s3, "Date Loaded (YYYY-MM-DD):", self.date_loaded_var, 0, 1)

        # --- Section 4: Notes ---
        s4 = ttk.LabelFrame(main_frame, text="Notes")
        s4.pack(fill=X, pady=10, padx=10)
        notes_entry = ttk.Entry(s4, textvariable=self.notes_var, width=60)
        notes_entry.pack(fill=X, padx=5, pady=5)
        self._bind_entry_keys(notes_entry)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Save", bootstyle="primary",
                   command=self._save).pack(side=LEFT, padx=BUTTON_PADX)
        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary",
                   command=self.top.destroy).pack(side=LEFT, padx=BUTTON_PADX)

        # Focus
        try:
            if hasattr(self, 'mfg_entry'):
                self.mfg_entry.focus_set()
        except Exception:
            pass

        self.top.bind("<Escape>", lambda e: self.top.destroy())
        self.top.bind("<Control-s>", lambda e: self._save())

    def _create_row(self, parent: ttk.Frame, label: str, var: tk.StringVar,
                    row: int, col: int, is_combo: bool = False,
                    values: list = None) -> tk.Widget:

        col_label = col * 2
        col_entry = col * 2 + 1

        ttk.Label(parent, text=label,
                  font=(FONT_FAMILY, LABEL_FONT_SIZE, "bold")).grid(
            row=row, column=col_label, sticky=W, pady=6, padx=(5, 15))

        if is_combo and values:
            entry = ttk.Combobox(parent, textvariable=var, values=values,
                                 width=40, state="readonly")
            if not var.get():
                entry.current(0)
        else:
            entry = ttk.Entry(parent, textvariable=var, width=40)

        entry.grid(row=row, column=col_entry, sticky=E + W, pady=6, padx=(0, 5))

        self._bind_entry_keys(entry)

        if row == 0 and col == 0:
            self.mfg_entry = entry

        return entry

    def _validate_numeric(self, value: str, field_name: str,
                          min_val: float = None, max_val: float = None,
                          allow_empty: bool = True) -> Optional[float]:

        value = value.strip()
        if not value:
            if allow_empty:
                return None
            raise ValueError(f"{field_name} is required.")
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                raise ValueError(f"{field_name} must be at least {min_val}.")
            if max_val is not None and num > max_val:
                raise ValueError(f"{field_name} cannot exceed {max_val}.")
            return num
        except ValueError as e:
            if "must be" in str(e) or "cannot exceed" in str(e):
                raise e
            raise ValueError(f"{field_name} must be a valid number.")

    def _save(self) -> None:
        # Collect Basic Info
        mfg = self.mfg_var.get().strip()
        caliber = self.caliber_var.get().strip()
        name = self.name_var.get().strip()
        use = self.use_var.get().strip()
        grains_str = self.grains_var.get().strip()
        bullet_name = self.bullet_name_var.get().strip()
        projectile_type = self.projectile_type_var.get().strip()
        shot_size = self.shot_size_var.get().strip()
        pellet_count_str = self.pellet_count_var.get().strip()

        # Collect Reloading
        brass_mfg = self.brass_mfg_var.get().strip()
        hull_mfg = self.hull_mfg_var.get().strip()
        wad_mfg = self.wad_mfg_var.get().strip()
        bullet_mfg = self.bullet_mfg_var.get().strip()
        powder_mfg = self.powder_mfg_var.get().strip()
        powder_name = self.powder_name_var.get().strip()
        powder_lot = self.powder_lot_var.get().strip()
        powder_grains_str = self.powder_grains_var.get().strip()
        primer_mfg = self.primer_mfg_var.get().strip()
        primer_type = self.primer_type_var.get().strip()
        primer_lot = self.primer_lot_var.get().strip()
        crimp_type = self.crimp_type_var.get().strip()

        # Collect Measurements
        case_weight_str = self.case_weight_var.get().strip()
        overall_length_str = self.overall_length_var.get().strip()
        cbto_str = self.cbto_var.get().strip()
        date_loaded = self.date_loaded_var.get().strip()
        batch_qty_str = self.batch_qty_var.get().strip()
        notes = self.notes_var.get().strip()

        # Required Fields Validation
        if not mfg or not caliber:
            messagebox.showwarning(self.top,"Validation Error", "Manufacturer and Caliber are required.")
            return

        # Numeric Validations
        try:
            grains = self._validate_numeric(grains_str, "Grains", allow_empty=True)
            pellet_count = self._validate_numeric(pellet_count_str, "Pellet Count", allow_empty=True)
            powder_grains = self._validate_numeric(powder_grains_str, "Powder Grains", allow_empty=True)
            case_weight = self._validate_numeric(case_weight_str, "Case Weight", allow_empty=True)
            overall_length = self._validate_numeric(overall_length_str, "Overall Length", allow_empty=True)
            cbto = self._validate_numeric(cbto_str, "CBTO", allow_empty=True)
            batch_qty = self._validate_numeric(batch_qty_str, "Batch Quantity", allow_empty=True)
            bc_val = self._validate_numeric(self.bc_var.get().strip(), "Ballistic Coefficient", allow_empty=True, min_val=0.0, max_val=2.0)
        except ValueError as e:
            messagebox.showwarning(self.top,"Validation Error", str(e))
            return

        # Build the data dictionary
        data = {
            'mfg': mfg,
            'caliber': caliber,
            'ammo_name': name,
            'use_case': use,
            'grains': grains,
            'bullet_name': bullet_name,
            'bullet_mfg': bullet_mfg,
            'projectile_type': projectile_type,
            'shot_size': shot_size,
            'pellet_count': int(pellet_count) if pellet_count is not None else None,
            'do_not_rebuy': self.do_not_rebuy_var.get(),
            'brass_mfg': brass_mfg,
            'hull_mfg': hull_mfg,
            'wad_mfg': wad_mfg,
            'powder_mfg': powder_mfg,
            'powder_name': powder_name,
            'powder_lot': powder_lot,
            'powder_grains': powder_grains,
            'primer_mfg': primer_mfg,
            'primer_type': primer_type,
            'primer_lot': primer_lot,
            'crimp_type': crimp_type,
            'drag_function': self.drag_func_var.get().strip(),
            'case_weight': case_weight,
            'overall_length': overall_length,
            'cbto': cbto,
            'ballistic_coeff': bc_val,
            'date_loaded': date_loaded,
            'batch_quantity': int(batch_qty) if batch_qty is not None else None,
            'notes': notes
        }

        try:
            if self.is_edit_mode:
                db_manager.update_ammo(self.ammo_data['id'], data)
                messagebox.showinfo(self.top,"Success", "Ammo updated successfully.")
            else:
                new_id = db_manager.add_ammo(data)
                data['id'] = new_id
                messagebox.showinfo(self.top,"Success", "Ammo added successfully.")

            if self.on_save:
                self.on_save(data)
            self.top.destroy()

        except Exception as e:
            messagebox.showerror(self.top,"Database Error", f"Failed to save: {e}")

    def destroy(self):
        self.top.destroy()
