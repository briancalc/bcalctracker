#login.py
#Login Screen for Firearm Management

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import os
import logging
from typing import Callable, Optional

from guiform.constants import (
    COLOR_BG_FRAME, COLOR_LABEL, COLOR_WHITE, COLOR_ERROR_BG, COLOR_ERROR_TEXT, COLOR_UNIT,
    FONT_FAMILY, LABEL_FONT_SIZE, UNIT_FONT_SIZE, TITLE_FONT_SIZE, BUTTON_FONT_SIZE,
    LOGIN_WINDOW_WIDTH, LOGIN_WINDOW_HEIGHT, LOGIN_MAIN_PADDING, LOGIN_ICON_SIZE, BUTTON_PADX
)

logger = logging.getLogger(__name__)


class LoginWindow:
    """Login/Setup window for master password authentication."""

    def __init__(self, root: ttk.Frame, on_success: Optional[Callable[[str], None]] = None) -> None:

        self.root = root
        self.on_success = on_success
        self.password_var = tk.StringVar()
        self.confirm_var = tk.StringVar()
        self.error_msg = tk.StringVar()
        self.icon_photo = None
        self.password_entry: Optional[ttk.Entry] = None
        self.confirm_entry: Optional[ttk.Entry] = None

        # Prevent rapid submissions
        self._processing = False

        from auth import load_master_password
        self.is_setup_mode = load_master_password() is None

        # Configure root frame
        if hasattr(self.root, 'geometry'):
            self.root.title("Bcalc Firearm Management")
            self.root.geometry(f"{LOGIN_WINDOW_WIDTH}x{LOGIN_WINDOW_HEIGHT}")
            self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use("litera")
        self._setup_styles(style)

        # Main Frame
        self.main_frame = ttk.Frame(root, padding=LOGIN_MAIN_PADDING, style="CustomFrame.TFrame")
        self.main_frame.pack(fill=BOTH, expand=True)

        # Add Icon
        self._add_icon_right(self.main_frame)

        # Title and Subtitle
        if self.is_setup_mode:
            ttk.Label(self.main_frame, text="Welcome!", style="Title.TLabel").pack(pady=(0, 5))
            ttk.Label(self.main_frame, text="Password should be at least 8 characters.", style="CustomLabel.TLabel").pack(pady=(0, 10))
        else:
            ttk.Label(self.main_frame, text="Bcalc Firearm Mgmt Login", style="Title.TLabel").pack(pady=(0, 5))

        # Password Entry
        self.password_entry = self._create_password_row("Password:", self.password_var)

        # Confirm Entry
        if self.is_setup_mode:
            self.confirm_entry = self._create_password_row("Confirm Password:", self.confirm_var)

        # Bind Enter key
        if self.is_setup_mode:
            self.password_entry.bind('<Return>', lambda e: self._handle_setup())
            if self.confirm_entry:
                self.confirm_entry.bind('<Return>', lambda e: self._handle_setup())
        else:
            self.password_entry.bind('<Return>', lambda e: self._handle_login())

        # Error Message Label
        self.error_label = ttk.Label(
            self.main_frame,
            textvariable=self.error_msg,
            foreground=COLOR_ERROR_TEXT,
            background=COLOR_BG_FRAME,
            font=(FONT_FAMILY, UNIT_FONT_SIZE)
        )
        self.error_label.pack(pady=(5, 0))

        # Buttons
        btn_frame = ttk.Frame(self.main_frame, style="CustomFrame.TFrame")
        btn_frame.pack(pady=(10, 0))

        if self.is_setup_mode:
            ttk.Button(btn_frame, text="Create Password", bootstyle="primary", command=self._handle_setup, width=15).pack(side=LEFT, padx=BUTTON_PADX)
        else:
            ttk.Button(btn_frame, text="Unlock", bootstyle="primary", command=self._handle_login, width=15).pack(side=LEFT, padx=BUTTON_PADX)

        ttk.Button(btn_frame, text="Exit", bootstyle="secondary", command=self._handle_exit, width=15).pack(side=LEFT, padx=BUTTON_PADX)

        if self.password_entry:
            self.password_entry.focus_set()

    def _add_icon_right(self, parent: ttk.Frame) -> None:

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "bcalctrackicon.png")

        if not os.path.exists(icon_path):
            logger.warning(f"Icon file not found: {icon_path}")
            return

        try:
            from PIL import Image, ImageTk
            img = Image.open(icon_path)
            img.thumbnail((LOGIN_ICON_SIZE, LOGIN_ICON_SIZE), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.icon_photo = photo

            icon_container = ttk.Frame(parent, style="CustomFrame.TFrame")
            icon_container.pack(side=RIGHT, fill=Y, padx=(10, 0))
            ttk.Label(icon_container, image=photo, background=COLOR_BG_FRAME).pack(pady=5)
        except ImportError:
            logger.warning("PIL not installed; skipping icon display")
        except Exception as e:
            logger.error(f"Failed to load icon: {e}", exc_info=True)

    def _setup_styles(self, style: ttk.Style) -> None:
        """Define custom styles."""
        style.configure("TEntry", font=(FONT_FAMILY, LABEL_FONT_SIZE))
        style.configure("TButton", font=(FONT_FAMILY, BUTTON_FONT_SIZE))
        style.configure("TLabel", font=(FONT_FAMILY, LABEL_FONT_SIZE))
        style.configure("CustomFrame.TFrame", background=COLOR_BG_FRAME)
        style.configure("CustomLabel.TLabel", foreground=COLOR_LABEL, background=COLOR_BG_FRAME, font=(FONT_FAMILY, LABEL_FONT_SIZE))
        style.configure("Title.TLabel", foreground=COLOR_ERROR_TEXT, background=COLOR_BG_FRAME, font=(FONT_FAMILY, TITLE_FONT_SIZE, "bold"))
        style.configure("White.TEntry", fieldbackground=COLOR_WHITE, foreground="black", font=(FONT_FAMILY, LABEL_FONT_SIZE))
        style.configure("Error.TEntry", fieldbackground=COLOR_ERROR_BG, foreground="black", font=(FONT_FAMILY, UNIT_FONT_SIZE))
        style.configure(
            "SmallGray.TButton",
            font=(FONT_FAMILY, 9),
            foreground=COLOR_UNIT,
            background=COLOR_BG_FRAME,
            borderwidth=0,
            relief="flat",
            padding=0,
            focuscolor="none",
            activebackground=COLOR_BG_FRAME,
            activeforeground=COLOR_UNIT
        )

    def _create_password_row(self, label_text: str, var: tk.StringVar) -> ttk.Entry:
        """Create a password entry row with show/hide toggle."""
        ttk.Label(self.main_frame, text=label_text, style="CustomLabel.TLabel").pack(anchor="w", pady=(5, 0))
        entry_frame = ttk.Frame(self.main_frame, style="CustomFrame.TFrame")
        entry_frame.pack(fill="x", pady=(2, 0))

        entry = ttk.Entry(entry_frame, textvariable=var, show="*", style="White.TEntry", width=18)
        entry.pack(side="left", padx=(0, 5))

        entry.bind('<BackSpace>', self._on_entry_backspace)
        entry.bind('<Delete>', self._on_entry_delete)

        toggle_btn = ttk.Button(entry_frame, text="show", style="SmallGray.TButton",
                                command=lambda: self._toggle_password(var, entry, toggle_btn))
        toggle_btn.pack(side="left")

        return entry


    def _toggle_password(self, var: tk.StringVar, entry: ttk.Entry, btn: ttk.Button) -> None:
        """Toggle password visibility."""
        try:
            if entry.cget('show') == "*":
                entry.config(show="")
                btn.config(text="Hide")
            else:
                entry.config(show="*")
                btn.config(text="show")
        except:
            pass


    def _on_entry_backspace(self, event):
        widget = event.widget
        current_text = widget.get()
        cursor_pos = widget.index(tk.INSERT)
        if cursor_pos > 0:
            new_text = current_text[:cursor_pos-1] + current_text[cursor_pos:]
            widget.delete(0, tk.END)
            widget.insert(0, new_text)
            widget.icursor(cursor_pos - 1)
        return 'break'

    def _on_entry_delete(self, event):
        widget = event.widget
        current_text = widget.get()
        cursor_pos = widget.index(tk.INSERT)
        if cursor_pos < len(current_text):
            new_text = current_text[:cursor_pos] + current_text[cursor_pos+1:]
            widget.delete(0, tk.END)
            widget.insert(0, new_text)
            widget.icursor(cursor_pos)
        return 'break'

    def _reset_password_fields(self) -> None:
        """Reset password field styles and error messages."""
        try:
            if self.password_entry:
                self.password_entry.config(style="White.TEntry")
            if self.confirm_entry:
                self.confirm_entry.config(style="White.TEntry")
            self.error_msg.set("")
        except:
            pass

    def _show_password_error(self, message: str, fields: Optional[list] = None) -> None:
        """Display password error with field highlighting."""
        try:
            self.error_msg.set(message)
            target_fields = fields if fields is not None else ([self.password_entry] if self.password_entry else [])
            for field in target_fields:
                if field:
                    field.config(style="Error.TEntry")
        except:
            pass

    def _handle_setup(self) -> None:
        # Prevent double submissions
        if self._processing:
            return

        self._processing = True
        self.root.after(500, lambda: setattr(self, '_processing', False))

        try:
            pwd = self.password_var.get().strip()
            confirm = self.confirm_var.get().strip()
            self._reset_password_fields()

            if not pwd:
                self._show_password_error("Password cannot be empty.")
                return

            if len(pwd) < 8:
                self._show_password_error("Must be at least 8 characters.")
                return

            if pwd != confirm:
                self._show_password_error("Passwords do not match.", [self.password_entry, self.confirm_entry])
                return

            from auth import setup_first_time
            setup_first_time(pwd)
            messagebox.showinfo("Success", "Password created!\nOK to continue")

            if self.on_success:
                self.on_success(pwd)
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            self._show_password_error(f"Setup error: {str(e)}")

    def _handle_login(self) -> None:
        # Prevent double submissions
        if self._processing:
            return

        self._processing = True
        self.root.after(500, lambda: setattr(self, '_processing', False))

        try:
            pwd = self.password_var.get().strip()
            self._reset_password_fields()

            if not pwd:
                self._show_password_error("Password required.")
                return

            from auth import authenticate
            if authenticate(pwd):
                if self.on_success:
                    self.on_success(pwd)
            else:
                self._show_password_error("Invalid password.")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            self._show_password_error("Authentication error.")

    def _handle_exit(self) -> None:
        """Exit the application."""
        self.root.quit()

    def cleanup(self) -> None:
        """Clean up resources before closing login window."""
        if self.icon_photo:
            self.icon_photo = None
