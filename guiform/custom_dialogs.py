# guiform/custom_dialogs.py

"""
Custom dialog boxes without system icons.
"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class CustomDialog:


    def __init__(self, parent, title: str, message: str, dialog_type: str = "info"):

        self.result = None
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.resizable(False, False)

        # Determine colors based on type
        colors = {
            "info": {"bg": "#E3F2FD", "fg": "#1976D2"},
            "warning": {"bg": "#FFF3E0", "fg": "#F57C00"},
            "error": {"bg": "#FFEBEE", "fg": "#D32F2F"}
        }
        color = colors.get(dialog_type, colors["info"])

        # Main frame with colored background
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=BOTH, expand=True)

        # Message label
        msg_label = ttk.Label(
            main_frame,
            text=message,
            wraplength=350,
            justify=tk.LEFT,
            font=("Roboto", 12)
        )
        msg_label.pack(pady=30, padx=20, fill=BOTH, expand=True)

        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        ttk.Button(
            btn_frame,
            text="OK",
            bootstyle="primary",
            command=self._ok_click
        ).pack()

        # Center the dialog
        self.dialog.update_idletasks()
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.dialog.geometry(f"+{x}+{y}")

    def _ok_click(self):
        self.dialog.destroy()

    def show(self):

        self.dialog.wait_window()


class YesNoDialog:


    def __init__(self, parent, title: str, message: str):

        self.result = False
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.resizable(False, False)

        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=BOTH, expand=True)

        # Message label
        msg_label = ttk.Label(
            main_frame,
            text=message,
            wraplength=350,
            justify=tk.LEFT,
            font=("Roboto", 12)
        )
        msg_label.pack(pady=30, padx=20, fill=BOTH, expand=True)

        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        ttk.Button(
            btn_frame,
            text="Yes",
            bootstyle="primary",
            command=self._yes_click
        ).pack(side=LEFT, padx=5)
        ttk.Button(
            btn_frame,
            text="No",
            bootstyle="secondary",
            command=self._no_click
        ).pack(side=LEFT, padx=5)

        # Center the dialog
        self.dialog.update_idletasks()
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.dialog.geometry(f"+{x}+{y}")

    def _yes_click(self):
        self.result = True
        self.dialog.destroy()

    def _no_click(self):
        self.result = False
        self.dialog.destroy()

    def show(self):
        """Block until dialog is closed and return result."""
        self.dialog.wait_window()
        return self.result


class BackupListDialog:
    """Dialog for selecting a backup file to restore."""

    def __init__(self, parent, title: str, backup_list: list):
        """
        Initialize backup selection dialog.

        Args:
            parent: Parent window
            title: Dialog title
            backup_list: List of tuples (backup_path_object, filename_str, info_str)
        """
        self.result = None
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("550x350")
        self.dialog.transient(parent)
        self.dialog.resizable(False, False)

        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # Instructions label
        instr_label = ttk.Label(
            main_frame,
            text="Select a backup to restore from:",
            wraplength=500,
            justify=tk.LEFT,
            font=("Roboto", 11)
        )
        instr_label.pack(anchor=tk.W, pady=(0, 10), fill=tk.X)

        # Listbox frame with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=BOTH, expand=True, pady=(0, 15))

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_frame,
            font=("Roboto", 10),
            yscrollcommand=scrollbar.set,
            height=12,
            relief="flat",
            borderwidth=1,
            highlightthickness=0
        )
        self.listbox.pack(side=tk.LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Populate listbox with single-line entries
        self.backup_data = []
        for backup_path, filename, info in backup_list:
            display_text = f"{filename}  •  {info}"
            self.listbox.insert(tk.END, display_text)
            self.backup_data.append(backup_path)

        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Restore",
            bootstyle="primary",
            command=self._restore_click
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Cancel",
            bootstyle="secondary",
            command=self._cancel_click
        ).pack(side=LEFT, padx=5)

        # Center the dialog
        self.dialog.update_idletasks()
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 275
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 175
        self.dialog.geometry(f"+{x}+{y}")

    def _restore_click(self):
        selection = self.listbox.curselection()
        if selection:
            self.result = self.backup_data[selection[0]]
        self.dialog.destroy()

    def _cancel_click(self):
        self.result = None
        self.dialog.destroy()

    def show(self):
        """Block until dialog is closed and return selected backup path or None."""
        self.dialog.wait_window()
        return self.result


def showinfo(parent, title: str, message: str):
    CustomDialog(parent, title, message, "info").show()


def showwarning(parent, title: str, message: str):
    CustomDialog(parent, title, message, "warning").show()


def showerror(parent, title: str, message: str):
    CustomDialog(parent, title, message, "error").show()


def askyesno(parent, title: str, message: str):
    return YesNoDialog(parent, title, message).show()

def show_long_message(parent, title: str, message: str):

    try:
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("500x400")
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        text_widget = tk.Text(
            main_frame,
            wrap=tk.WORD,
            font=("Roboto", 12),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=5,
            pady=5
        )
        text_widget.pack(side=tk.LEFT, fill=BOTH, expand=True)

        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)

        # Add scrollbar if content is long
        num_lines = int(text_widget.index('end-1c').split('.')[0])
        if num_lines > 15:
            scrollbar = ttk.Scrollbar(main_frame, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)

        close_btn = ttk.Button(dialog, text="Close", command=dialog.destroy)
        close_btn.pack(pady=(0, 15))

        dialog.transient(parent)
        dialog.grab_set()
        dialog.wait_window()

    except Exception as e:
        print(f"[ERROR] show_long_message failed: {e}")
