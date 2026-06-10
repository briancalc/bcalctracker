# guiform/firearm_form.py

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from guiform import custom_dialogs as messagebox
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import re
import subprocess
import os

from guiform.constants import (
    COLOR_BG_FRAME, COLOR_LABEL, COLOR_ERROR_TEXT,
    FONT_FAMILY, LABEL_FONT_SIZE, UNIT_FONT_SIZE, TITLE_FONT_SIZE,
    MAIN_CONTAINER_PADDING, BUTTON_PADX
)
from data_loaders import FIREARM_MFG, CALIBERS, FIREARM_TYPES
from database import db_manager

class FirearmForm:
    """Modal dialog for adding or editing a firearm."""

    def __init__(self, parent, on_save: Callable[[Dict[str, Any]], None], firearm_data: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.on_save = on_save
        self.is_edit_mode = firearm_data is not None
        self.firearm_data = firearm_data or {}

        # Flag to track if user has manually edited the serial field
        self._serial_manually_edited = False

        # 1. Window Title
        self.top = ttk.Toplevel(parent)
        self.top.title("Bcalc Firearm Management")
        self.top.geometry("1100x720")
        self.top.transient(parent)

        # Variables
        self.name_var = tk.StringVar()
        self.mfg_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.serial_var = tk.StringVar()
        self.caliber_primary_var = tk.StringVar()
        self.caliber_secondary_var = tk.StringVar()
        self.barrel_len_var = tk.StringVar()
        self.purch_date_var = tk.StringVar()
        self.purch_loc_var = tk.StringVar()
        self.purch_price_var = tk.StringVar()
        self.sold_date_var = tk.StringVar()
        self.sold_buyer_var = tk.StringVar()
        self.sold_price_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        self.photo_path_var = tk.StringVar()
        self.is_sold_var = tk.BooleanVar(value=False)

        # Pre-fill if editing
        if self.is_edit_mode:
            self.name_var.set(self.firearm_data.get('name', ''))
            self.mfg_var.set(self.firearm_data.get('mfg', ''))
            self.type_var.set(self.firearm_data.get('firearm_type', ''))
            self.serial_var.set(self.firearm_data.get('serial_number', ''))
            self.caliber_primary_var.set(self.firearm_data.get('caliber_primary', ''))
            self.caliber_secondary_var.set(self.firearm_data.get('caliber_secondary', ''))
            self.barrel_len_var.set(str(self.firearm_data.get('barrel_length', '')))

            purch_date = self.firearm_data.get('purchase_date', '')
            self.purch_date_var.set(purch_date if purch_date else "")

            self.purch_loc_var.set(self.firearm_data.get('purchase_location', ''))
            self.purch_price_var.set(str(self.firearm_data.get('purchase_price', '')))
            self.notes_var.set(self.firearm_data.get('notes', ''))
            self.photo_path_var.set(self.firearm_data.get('photo_path', ''))

            if self.firearm_data.get('sold_date'):
                self.is_sold_var.set(True)
                sold_date = self.firearm_data.get('sold_date', '')
                self.sold_date_var.set(sold_date if sold_date else "")
                self.sold_buyer_var.set(self.firearm_data.get('sold_buyer', ''))
                self.sold_price_var.set(str(self.firearm_data.get('sold_price', '')))
        else:

            self._serial_manually_edited = False

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

    def _on_name_changed(self, event=None):

        if not self.is_edit_mode and not self._serial_manually_edited:
            name = self.name_var.get().strip()
            self.serial_var.set(name)

    def _on_serial_focus_in(self, event=None):

        self._serial_manually_edited = True

    def _build_ui(self) -> None:
        # Main Frame (Directly in TopLevel)
        main_frame = ttk.Frame(self.top, padding=MAIN_CONTAINER_PADDING)
        main_frame.pack(fill=BOTH, expand=True)

        title_text = "Edit Firearm" if self.is_edit_mode else "Add New Firearm"
        ttk.Label(main_frame, text=title_text, font=(FONT_FAMILY, TITLE_FONT_SIZE, "bold"),
                  foreground=COLOR_ERROR_TEXT).pack(pady=(0, 15))

        # --- Section 1: Basic Info ---
        section1 = ttk.LabelFrame(main_frame, text="Basic Information")
        section1.pack(fill=X, pady=10, padx=10)
        section1.grid_columnconfigure(1, weight=1)
        section1.grid_columnconfigure(3, weight=1)

        self.name_entry = self._create_row(section1, "Firearm Name:", self.name_var, 0, 0)

        # Bind the Name Entry to auto-fill Serial
        self.name_entry.bind("<KeyRelease>", self._on_name_changed)

        self._create_row(section1, "Manufacturer:", self.mfg_var, 0, 1, is_combo=True, values=FIREARM_MFG)
        self._create_row(section1, "Type:", self.type_var, 1, 0, is_combo=True, values=FIREARM_TYPES)

        # Create Serial Row and bind FocusIn to stop auto-filling
        self.serial_entry = self._create_row(section1, "Serial #:", self.serial_var, 1, 1)
        self.serial_entry.bind("<FocusIn>", self._on_serial_focus_in)

        self._create_row(section1, "Caliber Primary:", self.caliber_primary_var, 2, 0, is_combo=True, values=CALIBERS)

        # CHANGE (2): Secondary Caliber - Default to blank
        self._create_row(section1, "Caliber Secondary:", self.caliber_secondary_var, 2, 1, is_combo=True, values=CALIBERS, default_blank=True)

        self._create_row(section1, "Barrel Length (in):", self.barrel_len_var, 3, 0)

        # --- Section 2: Purchase Info ---

        section2 = ttk.LabelFrame(main_frame, text="Purchase Details (optional)")
        section2.pack(fill=X, pady=10, padx=10)
        section2.grid_columnconfigure(1, weight=1)
        section2.grid_columnconfigure(3, weight=1)

        self._create_row(section2, "Purchase Date:", self.purch_date_var, 0, 0, is_date=True)
        self._create_row(section2, "Purchase Location:", self.purch_loc_var, 0, 1)

        # CHANGE (4): Currency validation
        self._create_row(section2, "Purchase Cost:", self.purch_price_var, 1, 0, is_currency=True)

        # --- Section 3: Sold Status ---
        section3 = ttk.LabelFrame(main_frame, text="Sold Status")
        section3.pack(fill=X, pady=10, padx=10)
        section3.grid_columnconfigure(1, weight=1)
        section3.grid_columnconfigure(3, weight=1)

        chk_sold = ttk.Checkbutton(section3, text="Mark as Sold", variable=self.is_sold_var, command=self._toggle_sold_fields)
        chk_sold.grid(row=0, column=0, columnspan=4, sticky=W, pady=5, padx=5)

        self.sold_frame = ttk.Frame(section3)
        self.sold_frame.grid(row=1, column=0, columnspan=4, sticky=E+W, pady=5, padx=5)
        self.sold_frame.grid_columnconfigure(1, weight=1)
        self.sold_frame.grid_columnconfigure(3, weight=1)
        self.sold_frame.grid_remove()

        self._create_row(self.sold_frame, "Sold Date:", self.sold_date_var, 0, 0, is_date=True)
        self._create_row(self.sold_frame, "Sold Buyer:", self.sold_buyer_var, 0, 1)
        self._create_row(self.sold_frame, "Sold Price:", self.sold_price_var, 1, 0, is_currency=True)

        # --- Section 4: Photo & Notes ---
        section4 = ttk.LabelFrame(main_frame, text="Photo & Notes")
        section4.pack(fill=X, pady=10, padx=10)
        section4.grid_columnconfigure(1, weight=1)

        # Row 0: Photo Path + Browse Button
        ttk.Label(section4, text="Firearm Photo:", font=(FONT_FAMILY, LABEL_FONT_SIZE, "bold")).grid(
            row=0, column=0, sticky=W, pady=6, padx=(5, 15))

        photo_entry = ttk.Entry(section4, textvariable=self.photo_path_var, width=40, state="readonly")
        photo_entry.grid(row=0, column=1, sticky=E+W, pady=6, padx=(0, 5))

        self._bind_entry_keys(photo_entry)

        browse_btn = ttk.Button(section4, text="Browse...", width=10, command=self._browse_photo)
        browse_btn.grid(row=0, column=2, sticky=W, pady=6, padx=(0, 5))

        # Row 1: Notes
        self._create_row(section4, "Notes:", self.notes_var, 1, 0)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Save", bootstyle="primary", command=self._save).pack(side=LEFT, padx=BUTTON_PADX)
        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.top.destroy).pack(side=LEFT, padx=BUTTON_PADX)

        # Focus on name field
        try:
            if hasattr(self, 'name_entry'):
                self.name_entry.focus_set()
        except:
            pass

        # Keyboard shortcuts
        self.top.bind("<Escape>", lambda e: self.top.destroy())
        self.top.bind("<Control-s>", lambda e: self._save())

    def _create_row(self, parent: ttk.Frame, label: str, var: tk.StringVar, row: int, col: int,
                is_combo: bool = False, values: list = None, is_date: bool = False,
                is_currency: bool = False, default_blank: bool = False) -> tk.Widget:
        col_label = col * 2
        col_entry = col * 2 + 1

        label_text = label

        ttk.Label(parent, text=label_text, font=(FONT_FAMILY, LABEL_FONT_SIZE, "bold")).grid(
            row=row, column=col_label, sticky=W, pady=6, padx=(5, 15)
        )

        if is_combo and values:
            entry = ttk.Combobox(parent, textvariable=var, values=values, width=40, state="readonly")

            if default_blank:

                var.set("")
            elif not var.get():
                #only set default index if the box is blank (new record)
                entry.current(0)

        else:
            entry = ttk.Entry(parent, textvariable=var, width=40)

        entry.grid(row=row, column=col_entry, sticky=E+W, pady=6, padx=(0, 5))

        self._bind_entry_keys(entry)

        if is_date:
            self._setup_date_placeholder(entry, var)

        if is_currency:
            self._setup_currency_format(entry, var)

        return entry

    def _setup_currency_format(self, entry: ttk.Entry, var: tk.StringVar) -> None:

        pass

    def _setup_date_placeholder(self, entry: ttk.Entry, var: tk.StringVar) -> None:
        """Set up placeholder text behavior for date entries."""
        def on_focus_in(event):
            if entry.get().strip() == "":
                entry.insert(0, "YYYY-MM-DD")
                entry.config(foreground="gray")

        def on_focus_out(event):
            if entry.get().strip() == "YYYY-MM-DD":
                entry.delete(0, "end")
                entry.config(foreground="black")
            elif entry.get().strip():
                entry.config(foreground="black")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        # Show placeholder on init if empty
        if not var.get():
            entry.insert(0, "YYYY-MM-DD")
            entry.config(foreground="gray")

    def _validate_date(self, date_string: str, field_name: str) -> Optional[str]:
        date_string = date_string.strip()
        if not date_string or date_string == "YYYY-MM-DD":
            return None
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return date_string
        except ValueError:
            raise ValueError(f"{field_name} must be in YYYY-MM-DD format (e.g., 2026-05-28) or left blank.")

    def _validate_numeric(self, value: str, field_name: str, allow_negative: bool = False, min_val: float = None, max_val: float = None) -> Optional[float]:
        value = value.strip()
        if not value:
            return None

        try:
            num = float(value)
            if not allow_negative and num < 0:
                raise ValueError(f"{field_name} cannot be negative.")

            # CHANGE (1): Range validation
            if min_val is not None and num < min_val:
                raise ValueError(f"{field_name} must be at least {min_val}.")
            if max_val is not None and num > max_val:
                raise ValueError(f"{field_name} cannot exceed {max_val}.")

            return num
        except ValueError:
            raise ValueError(f"{field_name} must be a valid number.")

    def _validate_currency(self, value: str, field_name: str) -> Optional[float]:
        """Validate currency format (e.g., 123.45, 100, $50.00)."""
        value = value.strip()
        if not value:
            return None

        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.]', '', value)

        if not cleaned:
            return None

        try:
            num = float(cleaned)
            if num < 0:
                raise ValueError(f"{field_name} cannot be negative.")
            return num
        except ValueError:
            raise ValueError(f"{field_name} must be a valid currency amount (e.g., 123.45).")

    def _toggle_sold_fields(self) -> None:
        if self.is_sold_var.get():
            self.sold_frame.grid()
        else:
            self.sold_frame.grid_remove()

    def _browse_photo(self) -> None:

        try:
            result = subprocess.run(
                ['zenity', '--file-selection', '--title=Select Firearm Photo',
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
                title="Select Firearm Photo",
                filetypes=filetypes
            )
            if filepath:
                self.photo_path_var.set(filepath)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"File dialog failed. Please ensure zenity is installed:\n\n"
                f"sudo dnf install zenity\n\n"
                f"Technical error: {type(e).__name__}"
            )


    def _save(self) -> None:
        name = self.name_var.get().strip()
        mfg = self.mfg_var.get().strip()
        f_type = self.type_var.get().strip()
        serial = self.serial_var.get().strip()

        if not name or not mfg or not f_type or not serial:
            messagebox.showwarning(self.top,"Validation Error", "Firearm Name, Manufacturer, Type, and Serial Number are required.")
            return

        # Check for duplicate serial number (only when adding new)
        if not self.is_edit_mode:
            existing = db_manager.get_firearm_by_serial(serial)
            if existing:
                messagebox.showwarning(self.top,"Duplicate Error", f"A firearm with serial '{serial}' already exists.")
                return

        # Validate dates
        try:
            purch_date = self._validate_date(self.purch_date_var.get(), "Purchase Date")
            sold_date = self._validate_date(self.sold_date_var.get(), "Sold Date")
        except ValueError as e:
            messagebox.showwarning(self.top,"Validation Error", str(e))
            return

        # Validate numeric fields
        try:

            barrel_len = self._validate_numeric(self.barrel_len_var.get(), "Barrel Length", min_val=0.1, max_val=40.0)


            purch_price = self._validate_currency(self.purch_price_var.get(), "Purchase Price")
            sold_price = self._validate_currency(self.sold_price_var.get(), "Sold Price")
        except ValueError as e:
            messagebox.showwarning(self.top,"Validation Error", str(e))
            return


        cal_sec = self.caliber_secondary_var.get().strip()
        if not cal_sec:
            cal_sec = None

        data = {
            'name': name,
            'mfg': mfg,
            'firearm_type': f_type,
            'serial_number': serial,
            'caliber_primary': self.caliber_primary_var.get(),
            'caliber_secondary': cal_sec,
            'barrel_length': barrel_len,
            'purchase_date': purch_date,
            'purchase_location': self.purch_loc_var.get().strip(),
            'purchase_price': purch_price,
            'notes': self.notes_var.get().strip(),
            'photo_path': self.photo_path_var.get().strip()
        }

        if self.is_sold_var.get():
            if not sold_date:
                messagebox.showwarning(self.top,"Validation Error", "Sold Date is required if marked as sold.")
                return
            data['sold_date'] = sold_date
            data['sold_buyer'] = self.sold_buyer_var.get().strip()
            data['sold_price'] = sold_price
        else:
            data['sold_date'] = None
            data['sold_buyer'] = None
            data['sold_price'] = None

        try:
            if self.is_edit_mode:
                current = db_manager.get_firearm_by_id(self.firearm_data['id'])
                if current and current.get('sold_date'):
                    messagebox.showerror(self.top,"Error", "Cannot update a firearm that has been sold.")
                    return
                db_manager.update_firearm(self.firearm_data['id'], data)
                messagebox.showinfo(self.top, "Success", "Firearm added.")
            else:
                new_id = db_manager.add_firearm(data)
                data['id'] = new_id
                messagebox.showinfo(self.top, "Success", "Firearm added.")

            if self.on_save:
                self.on_save(data)
            self.top.destroy()

        except Exception as e:
            messagebox.showerror(self.top,"Database Error", f"Failed to save: {e}")

    def destroy(self):
        self.top.destroy()
