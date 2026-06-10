# guiform/optic_form.py

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Optional, Callable, Dict, Any

from guiform.constants import (
    COLOR_BG_FRAME, COLOR_LABEL, COLOR_ERROR_TEXT,
    FONT_FAMILY, LABEL_FONT_SIZE, UNIT_FONT_SIZE, TITLE_FONT_SIZE,
    MAIN_CONTAINER_PADDING, BUTTON_PADX
)
from guiform import custom_dialogs as messagebox
from data_loaders import OPTICS_MFG, OPTIC_TYPES
from database import db_manager

class OpticForm:


    def __init__(self, parent, on_save: Callable[[Dict[str, Any]], None], optic_data: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.on_save = on_save
        self.is_edit_mode = optic_data is not None
        self.optic_data = optic_data or {}

        # Window Setup
        self.top = ttk.Toplevel(parent)
        self.top.title("Bcalc Firearm Management")
        self.top.geometry("900x500") # Slightly smaller than Firearm form
        self.top.transient(parent)

        # Variables
        self.mfg_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.notes_var = tk.StringVar()

        # Pre-fill if editing
        if self.is_edit_mode:
            self.mfg_var.set(self.optic_data.get('mfg', ''))
            self.type_var.set(self.optic_data.get('optic_type', ''))
            self.model_var.set(self.optic_data.get('model', ''))
            self.notes_var.set(self.optic_data.get('notes', ''))

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

    def _build_ui(self) -> None:

        main_frame = ttk.Frame(self.top, padding=MAIN_CONTAINER_PADDING)
        main_frame.pack(fill=BOTH, expand=True)

        # Header: Red
        title_text = "Edit Optic" if self.is_edit_mode else "Add New Optic"
        ttk.Label(main_frame, text=title_text, font=(FONT_FAMILY, TITLE_FONT_SIZE, "bold"),
                  foreground=COLOR_ERROR_TEXT).pack(pady=(0, 15))

        # --- Section 1: Basic Info ---
        section1 = ttk.LabelFrame(main_frame, text="Optic Details")
        section1.pack(fill=X, pady=10, padx=10)
        section1.grid_columnconfigure(1, weight=1)
        section1.grid_columnconfigure(3, weight=1)

        self._create_row(section1, "Manufacturer:", self.mfg_var, 0, 0, is_combo=True, values=OPTICS_MFG)
        self._create_row(section1, "Type:", self.type_var, 0, 1, is_combo=True, values=OPTIC_TYPES)
        self._create_row(section1, "Model:", self.model_var, 1, 0)
        # Empty row to balance grid or add future fields
        self._create_row(section1, "", tk.StringVar(), 1, 1)

        # --- Section 2: Notes ---
        section2 = ttk.LabelFrame(main_frame, text="Notes")
        section2.pack(fill=X, pady=10, padx=10)

        notes_entry = ttk.Entry(section2, textvariable=self.notes_var, width=60)
        notes_entry.pack(fill=X, padx=5, pady=5)
        self._bind_entry_keys(notes_entry)

        # Buttons: Below Notes
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Save", bootstyle="primary", command=self._save).pack(side=LEFT, padx=BUTTON_PADX)
        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.top.destroy).pack(side=LEFT, padx=BUTTON_PADX)

        self.mfg_entry.focus_set()

    def _create_row(self, parent: ttk.Frame, label: str, var: tk.StringVar, row: int, col: int, is_combo: bool = False, values: list = None) -> None:

        if not label:
            return

        col_label = col * 2
        col_entry = col * 2 + 1

        ttk.Label(parent, text=label, font=(FONT_FAMILY, LABEL_FONT_SIZE, "bold")).grid(
            row=row, column=col_label, sticky=W, pady=6, padx=(5, 15)
        )

        if is_combo and values:
            entry = ttk.Combobox(parent, textvariable=var, values=values, width=40, state="readonly")
            #only set default index if the box is empty (new record)
            if not var.get():
                entry.current(0)
        else:
            entry = ttk.Entry(parent, textvariable=var, width=40)

        entry.grid(row=row, column=col_entry, sticky=E+W, pady=6, padx=(0, 5))

        # Bind Backspace/Delete to prevent window closure
        self._bind_entry_keys(entry)

        if row == 0 and col == 0:
            self.mfg_entry = entry

    def _save(self) -> None:
        mfg = self.mfg_var.get().strip()
        f_type = self.type_var.get().strip()
        model = self.model_var.get().strip()

        if not mfg or not f_type or not model:
            messagebox.showwarning(self.top, "Validation Error", "Manufacturer, Type, and Model are required.")
            return

        data = {
            'mfg': mfg,
            'optic_type': f_type,
            'model': model,
            'notes': self.notes_var.get().strip()
        }

        try:
            if self.is_edit_mode:
                db_manager.update_optic(self.optic_data['id'], data)
                messagebox.showinfo(self.top, "Success", "Optic updated successfully.")
            else:
                new_id = db_manager.add_optic(data)
                data['id'] = new_id
                messagebox.showinfo(self.top, "Success", "Optic added successfully.")

            if self.on_save:
                self.on_save(data)
            self.top.destroy()

        except Exception as e:
            messagebox.showerror(self.top, "Database Error", f"Failed to save: {e}")

    def destroy(self):
        self.top.destroy()
