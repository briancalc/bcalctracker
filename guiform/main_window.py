# guiform/main_window.py


import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from guiform import custom_dialogs as messagebox
from PIL import Image, ImageTk
import sys
import os

# Import Database Manager
from database import db_manager

from pathlib import Path
from backup_restore import BackupManager

# Import Form Dialogs
from guiform.firearm_form import FirearmForm
from guiform.optic_form import OpticForm
from guiform.ammo_form import AmmoForm
from guiform.config_form import ConfigForm
from guiform.range_form import RangeForm

from guiform.constants import (
    COLOR_BG_FRAME, COLOR_LABEL, COLOR_WHITE, COLOR_GRAY,
    COLOR_ERROR_BG, COLOR_ERROR_TEXT, COLOR_UNIT,
    FONT_FAMILY, LABEL_FONT_SIZE, UNIT_FONT_SIZE, TITLE_FONT_SIZE, BUTTON_FONT_SIZE,
    MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT, MAIN_CONTAINER_PADDING, TAB_PADDING
)


class MainWindow:
    """Main application window with tabbed interface for firearm management."""

    def __init__(self, root, password: str):
        self.root = root
        self.password = password

        self._reports_refresh_timer = None

        # Get the actual Tk root window and resize it
        actual_root = self.root.winfo_toplevel()
        actual_root.title("Bcalc Firearm Management")
        actual_root.geometry(f"{MAIN_WINDOW_WIDTH}x{MAIN_WINDOW_HEIGHT}")
        actual_root.resizable(True, True)

        # Load the quail icon
        self.quail_icon = None
        self._load_quail_icon()

        # Initialize Styles
        self.style = ttk.Style()
        self.style.theme_use("litera")
        self._setup_custom_styles()

        # Initialize Database Connection FIRST
        try:
            if not db_manager.connect(password):
                messagebox.showerror(self.root, "Database Error", "Failed to unlock database. Incorrect password or corrupted file.")
                self.root.quit()
                return
        except Exception as e:
            messagebox.showerror(self.root,"Database Error", f"Database connection failed: {e}")
            self.root.quit()
            return

        # Build the UI AFTER database is connected
        self.create_widgets()

    def _load_quail_icon(self) -> None:

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "bcalcnotepadicon.png")

            if not os.path.exists(icon_path):
                print(f"Warning: Icon file not found at {icon_path}")
                self.quail_icon = None
                return

            icon_image = Image.open(icon_path)
            original_width, original_height = icon_image.size
            new_height = int(original_height * 0.30)
            new_width = int(original_width * (new_height / original_height))

            resized_image = icon_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.quail_icon = ImageTk.PhotoImage(resized_image)

        except Exception as e:
            print(f"Warning: Could not load quail icon: {e}")
            self.quail_icon = None

    def _setup_custom_styles(self) -> None:

        self.style.configure("TFrame", background=COLOR_BG_FRAME)
        self.style.configure("TLabel", font=(FONT_FAMILY, LABEL_FONT_SIZE),
                           background=COLOR_BG_FRAME, foreground=COLOR_LABEL)
        self.style.configure("Title.TLabel", font=(FONT_FAMILY, TITLE_FONT_SIZE, "bold"),
                           foreground=COLOR_ERROR_TEXT, background=COLOR_BG_FRAME)
        self.style.configure("TButton", font=(FONT_FAMILY, BUTTON_FONT_SIZE))
        self.style.configure("TNotebook.Tab", font=(FONT_FAMILY, 11, "bold"), padding=[15, 8])
        self.style.configure("TEntry", font=(FONT_FAMILY, LABEL_FONT_SIZE))
        self.style.configure("TCombobox", font=(FONT_FAMILY, LABEL_FONT_SIZE))

    def _convert_rating_score_to_text(self, score):
        """Convert numeric avg_rating_score (1.0-6.0) to text."""
        if score is None:
            return "No Rating"
        try:
            val = float(score)
            if val < 1.5:
                return "Bad"
            elif val < 2.5:
                return "Poor"
            elif val < 3.5:
                return "OK"
            elif val < 4.5:
                return "Good"
            elif val < 5.5:
                return "Very Good"
            else:
                return "Excellent"
        except (ValueError, TypeError):
            return "No Rating"

    def create_widgets(self) -> None:
        """Create the main layout with Notebook (Tabs)."""
        main_container = ttk.Frame(self.root, padding=MAIN_CONTAINER_PADDING)
        main_container.pack(fill=BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=X, pady=(0, 10))

        # Hamburger Menu Button (Upper Left)
        menu_btn = ttk.Button(
            header_frame,
            text="\u2261",
            width=3,
            command=lambda: self.toggle_hamburger_menu(menu_btn),
            style="TButton"
        )
        menu_btn.pack(side=LEFT, padx=(10, 5))

        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=LEFT, padx=(30, 0))

        ttk.Label(title_frame, text="Bcalc Firearm Management Application", style="Title.TLabel").pack()

        if self.quail_icon:
            icon_label = ttk.Label(header_frame, image=self.quail_icon)
            icon_label.image = self.quail_icon
            icon_label.pack(side=RIGHT, padx=(15, 0))

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=BOTH, expand=True)

        self.notebook.bind('<<NotebookTabChanged>>', self._handle_reports_tab_switch)

        # --- TAB 1: Configurations ---
        self.tab_configurations = ttk.Frame(self.notebook, padding=TAB_PADDING)
        self.notebook.add(self.tab_configurations, text="Configurations")
        self._setup_configurations_tab()

        # --- TAB 2: Firearms ---
        self.tab_firearms = ttk.Frame(self.notebook, padding=TAB_PADDING)
        self.notebook.add(self.tab_firearms, text="Firearms")
        self._setup_firearms_tab()

        # --- TAB 3: Optics ---
        self.tab_optics = ttk.Frame(self.notebook, padding=TAB_PADDING)
        self.notebook.add(self.tab_optics, text="Optics")
        self._setup_optics_tab()

        # --- TAB 4: Ammo ---
        self.tab_ammo = ttk.Frame(self.notebook, padding=TAB_PADDING)
        self.notebook.add(self.tab_ammo, text="Ammo")
        self._setup_ammo_tab()

        # --- TAB 5: Range Log ---
        self.tab_range = ttk.Frame(self.notebook, padding=TAB_PADDING)
        self.notebook.add(self.tab_range, text="Range Log")
        self._setup_range_tab()

        # --- TAB 6: Reports ---
        self.tab_reports = ttk.Frame(self.notebook, padding=TAB_PADDING)
        self.notebook.add(self.tab_reports, text="Reports")
        self._setup_reports_tab()

#=====================================
    def toggle_hamburger_menu(self, menu_btn) -> None:
        """Toggle the hamburger menu popup."""
        if not hasattr(self, '_hamburger_menu'):
            self._hamburger_menu = tk.Menu(self.root, tearoff=0,
                                           background=COLOR_BG_FRAME,
                                           foreground=COLOR_LABEL,
                                           font=(FONT_FAMILY, LABEL_FONT_SIZE),
                                           borderwidth=0,
                                           relief="flat",
                                           activebackground=COLOR_GRAY)

            # --- Text Definitions ---
            help_text = "1. Add a firearm record with as much data as you'd like.\n\n2. Optional:  add optic and ammunition.\n\n3. Create a configuration which consists of a firearm and optic (optional) and ammuntion (optional).  Firearms can be associated with multiple optic and/or ammunition records and vice versa.\n\n4. Enter range session information.  Key field is the configuration.\n\n5. Report tab tracks various data.\n\n**Don't misplace your password as no recovery option.**"
            about_text = (
                "1. What is this?\n"
                "The Bcalc Firearm Management App v1.0 is an open-source firearm, optics, and ammunition tracker with no cloud-based services or subscriptions.\n\n"
                "You can enter multiple configurations of firearms, optics, and ammunition.  For each configuration, you can track range session performance and conditions.  Data reports such as rounds per firearm and top configurations by caliber are available.\n"
                "An internet connection is not required once installed.\n"
                "No user data is collected or transmitted.\n\n"
               "2. Who is this for?\n"
                "Hunters and hobbyists who prefer to use open-source applications. "
                " It’s easy to track your firearm performance with different ammunition, whether purchased or hand-load.\n\n"
                "3. Why?\n"
                "I'm not a software developer.  The goal was to continue my python learning progress while producing something useful, at least for me. This application is offered for educational and entertainment purposes."
            )
            credits_text = "Bcalc Firearms Management\n\nCreated by Brian Calc."
            license_text = "GNU General Public License (GPL) Version 3."

            # Helper to close menu and show dialog
            def close_and_show(title, msg):
                if hasattr(self, '_hamburger_menu'):
                    try:
                        self._hamburger_menu.unpost()
                    except:
                        pass
                # Use show_long_message for longer content
                messagebox.show_long_message(self.root, title, msg)

            # --- Menu Items ---
            self._hamburger_menu.add_command(label="Backup Database", command=self._backup_database)
            self._hamburger_menu.add_command(label="Restore Database", command=self._restore_database)
            self._hamburger_menu.add_separator()
            self._hamburger_menu.add_command(label="User Guide", command=lambda: close_and_show("User Guide", help_text))
            self._hamburger_menu.add_command(label="About", command=lambda: close_and_show("About", about_text))
            self._hamburger_menu.add_command(label="Credits", command=lambda: close_and_show("Credits", credits_text))
            self._hamburger_menu.add_command(label="License", command=lambda: close_and_show("License", license_text))
            self._hamburger_menu.add_separator()
            self._hamburger_menu.add_command(label="Exit", command=self.root.quit)

        # Toggle visibility
        if getattr(menu_btn, '_menu_open', False):
            self._hamburger_menu.unpost()
            menu_btn._menu_open = False
        else:
            menu_btn.update_idletasks()

            x_pos = menu_btn.winfo_rootx()
            y_pos = menu_btn.winfo_rooty() + menu_btn.winfo_height()


            if y_pos + 200 > self.root.winfo_screenheight():
                y_pos = menu_btn.winfo_rooty() - 200

            self._hamburger_menu.post(x_pos, y_pos)
            menu_btn._menu_open = True

    def _backup_database(self) -> None:
        """Handle backup database action."""
        try:
            # Close menu
            if hasattr(self, '_hamburger_menu'):
                try:
                    self._hamburger_menu.unpost()
                except:
                    pass

            # Verify database connection and password
            if db_manager.conn is None:
                print("[ERROR] No active database connection")
                messagebox.showerror(self.root, "Error", "No active database connection. Please connect to the database first.")
                return

            if db_manager._password is None:
                print("[ERROR] Database password not available")
                messagebox.showerror(self.root, "Error", "Database password not available.")
                return

            password = db_manager._password

            # Use the SAME datadb path as the database manager
            # db_manager.db_path is the .db file, so .parent gives us the datadb folder
            datadb_path = db_manager.db_path.parent

            print(f"[DEBUG] Starting backup process...")
            print(f"[DEBUG] Datadb path: {datadb_path}")

            backup_mgr = BackupManager(datadb_path)
            success, message = backup_mgr.create_backup(password)

            if success:
                print(f"[DEBUG] Backup successful")
                messagebox.showinfo(self.root, "Backup Successful", message)
            else:
                print(f"[ERROR] Backup failed: {message}")
                messagebox.showerror(self.root, "Backup Failed", message)

        except Exception as e:
            error_msg = f"Backup error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(self.root, "Error", error_msg)

    def _restore_database(self) -> None:
        """Handle restore database action."""
        try:
            # Close menu
            if hasattr(self, '_hamburger_menu'):
                try:
                    self._hamburger_menu.unpost()
                except:
                    pass

            print("[DEBUG] Starting restore process...")

            # Use the SAME datadb path as the database manager
            datadb_path = db_manager.db_path.parent

            print(f"[DEBUG] Datadb path: {datadb_path}")

            backup_mgr = BackupManager(datadb_path)
            backups = backup_mgr.list_backups()

            if not backups:
                print("[WARNING] No backups found")
                messagebox.showwarning(self.root, "No Backups", "No backups found. Please create a backup first.")
                return

            # Build list for dialog
            backup_list = []
            for backup in backups:
                filename, info = backup_mgr.get_backup_info(backup)
                backup_list.append((backup, filename, info))

            print(f"[DEBUG] Showing backup selection dialog with {len(backup_list)} backups")

            # Show backup selection dialog
            from guiform.custom_dialogs import BackupListDialog
            selected_backup = BackupListDialog(self.root, "Restore from Backup", backup_list).show()

            if not selected_backup:
                print("[DEBUG] Restore cancelled by user")
                return

            # Show confirmation warning 
            confirm_msg = "Warning: Will overwrite current database!\n\nContinue?"

            if not messagebox.askyesno(self.root, "Confirm Restore", confirm_msg):
                print("[DEBUG] Restore cancelled by user confirmation")
                return

            # Verify database connection and password
            if db_manager.conn is None:
                print("[ERROR] No active database connection")
                messagebox.showerror(self.root, "Error", "No active database connection.")
                return

            if db_manager._password is None:
                print("[ERROR] Database password not available")
                messagebox.showerror(self.root, "Error", "Database password not available.")
                return

            password = db_manager._password

            # Perform restore
            print(f"[DEBUG] Restoring from: {selected_backup}")
            success, message = backup_mgr.restore_backup(selected_backup, password)

            if success:
                print("[DEBUG] Restore successful - restarting application")
                messagebox.showinfo(self.root, "Restore Successful", message)
                # CRITICAL: Release any lingering modal grabs to ensure OK button appears
                self.root.update()
                self.root.grab_release()

                #messagebox.showinfo(self.root, "Restore Successful", message)

                # Close database connection
                self.cleanup()

                # Restart application automatically
                print("[DEBUG] Executing application restart...")

                # Ensure we have the correct script path to avoid interactive mode
                script_path = sys.argv[0]
                if not script_path or script_path == '-':
                    script_path = __file__ if '__file__' in globals() else 'starttracker.py'

                # Re-execute the script
                os.execv(sys.executable, [sys.executable, script_path] + sys.argv[1:])

            else:
                print(f"[ERROR] Restore failed: {message}")
                messagebox.showerror(self.root, "Restore Failed", message)

        except Exception as e:
            error_msg = f"Restore error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(self.root, "Error", error_msg)


#================================
    # Reports Tab Auto-Refresh Logic
    def _handle_reports_tab_switch(self, event) -> None:

        selected_tab = self.notebook.select()

        # Check if Reports tab is selected
        if selected_tab == str(self.tab_reports):
            # Cancel any existing pending refresh
            if self._reports_refresh_timer is not None:
                self.root.after_cancel(self._reports_refresh_timer)

            # Schedule new refresh after 100ms delay
            self._reports_refresh_timer = self.root.after(100, self._refresh_reports_content)

    def _refresh_reports_content(self) -> None:

        # Clear the timer reference
        self._reports_refresh_timer = None

        # Re-populate all dropdowns
        self._populate_dropdowns()

        # Re-run update logic for sections that have active selections
        if self.sec1_firearm_var.get():
            self._update_section1()
        if self.sec2_caliber_var.get():
            self._update_section2()
        if self.sec3_config_var.get():
            self._update_section3()
        if self.sec4_mfg_var.get() and self.sec4_caliber_var.get():
            self._update_section4()

#=============================================================
    # --- TAB 1: Configurations ---
    def _setup_configurations_tab(self) -> None:

        self.config_tree = None
        try:
            configs = db_manager.get_all_configurations()
            if not configs:
                lbl = ttk.Label(self.tab_configurations, text="No configurations in database.", font=(FONT_FAMILY, 12))
                lbl.pack(pady=20)
            else:
                # Define columns: Firearm, Optic, Ammo, Rating, Sys Id
                columns = ("Firearm", "Optic", "Ammo", "Avg Rating", "Sys Id")
                self.config_tree = ttk.Treeview(self.tab_configurations, columns=columns, height=15, selectmode="browse")
                self.config_tree.column("#0", width=0, stretch=False)

                # Configure Data Columns
                for col in columns:
                    self.config_tree.heading(col, text=col, anchor=W)

                    if col == "Sys Id":
                        width = 40
                    elif col == "Rating":
                        width = 90
                    elif col == "Optic":
                        width = 250
                    elif col == "Ammo":
                        width = 375
                    else: # Firearm
                        width = 300
                    self.config_tree.column(col, width=width, anchor=W)

                for c in configs:

                    # Firearm: Type | Mfg | Name
                    fire_str = f"{c.get('firearm_type', '')} {c.get('firearm_mfg', '')} {c.get('firearm_name', '')}"

                    # Optic: Mfg | Type | Model (or "None")
                    if c.get('optic_mfg'):
                        optic_str = f"{c.get('optic_mfg')} {c.get('optic_type', '')} {c.get('optic_model', '')}"
                    else:
                        optic_str = "None"

                    # Ammo: Caliber | Mfg | Grains | Name (or "None")
                    if c.get('ammo_mfg'):
                        grains = str(c.get('grains', '') or '')
                        ammo_str = f"{c.get('caliber', '')} {c.get('ammo_mfg')} {c.get('grains')} {c.get('ammo_name', '')}"
                    else:
                        ammo_str = "None"

                    avg_score = c.get('avg_rating_score')
                    rating_str = self._convert_rating_score_to_text(avg_score)

                    # Values: Firearm, Optic, Ammo, Rating, Sys Id, Hidden Notes, Hidden ID
                    values_tuple = (
                        fire_str,
                        optic_str,
                        ammo_str,
                        rating_str,
                        str(c['id']),
                        c.get('config_notes', ''),
                        c['id']
                    )

                    # Text column (#0) shows the Notes
                    self.config_tree.insert("", "end", text=c.get('config_notes', ''), values=values_tuple)

                self.config_tree.pack(fill=BOTH, expand=True, pady=10)
                self.config_tree.bind("<Double-1>", self._on_config_double_click)

        except Exception as e:
            lbl = ttk.Label(self.tab_configurations, text=f"Error: {e}", font=(FONT_FAMILY, 11), foreground="red")
            lbl.pack(pady=20)

        btn_frame = ttk.Frame(self.tab_configurations)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Configuration", bootstyle="primary", command=self._open_add_config).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", bootstyle="secondary", command=self._edit_config).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", bootstyle="danger", command=self._delete_config).pack(side=LEFT, padx=5)

    def _open_add_config(self):
        def on_save(data): self._refresh_config_list()
        ConfigForm(self.tab_configurations, on_save=on_save, config_data=None)

    def _edit_config(self):
        if not self.config_tree: return
        sel = self.config_tree.selection()
        if not sel: return messagebox.showwarning(self.root,"Selection", "Select a configuration.")

        item = self.config_tree.item(sel[0])

        config_id = int(str(item['values'][6]))

        # Fetch the full configuration data
        target = db_manager.get_configuration_by_id(config_id)
        if not target:
            return messagebox.showerror(self.root,"Error", "Configuration not found.")

        # CHECK: Is the linked firearm sold?
        firearm_id = target.get('firearm_id')
        firearm_data = db_manager.get_firearm_by_id(firearm_id)

        if firearm_data and firearm_data.get('sold_date'):
            return messagebox.showwarning(self.root,"Locked",
                "Cannot edit this configuration because the linked firearm has been sold.\n\n"
                "Historical data is read-only.")

        # If not sold, proceed to edit
        def on_save(data): self._refresh_config_list()
        ConfigForm(self.tab_configurations, on_save=on_save, config_data=target)

    def _delete_config(self):
        if not self.config_tree: return
        sel = self.config_tree.selection()
        if not sel: return messagebox.showwarning(self.root,"Selection", "Select a configuration.")

        item = self.config_tree.item(sel[0])
        config_id = int(str(item['values'][6]))

        # Fetch the full configuration data to check the firearm status
        target = db_manager.get_configuration_by_id(config_id)
        if not target:
            return messagebox.showerror(self.root,"Error", "Configuration not found.")

        # CHECK: Is the linked firearm sold?
        firearm_id = target.get('firearm_id')
        firearm_data = db_manager.get_firearm_by_id(firearm_id)

        if firearm_data and firearm_data.get('sold_date'):
            return messagebox.showwarning(self.root,"Locked",
                "Cannot delete this configuration because the linked firearm has been sold.\n\n"
                "Historical data must be preserved.")

        # If not sold, proceed with confirmation
        if messagebox.askyesno(self.root,"Confirm", "Delete this configuration?"):
            db_manager.delete_configuration(config_id)
            self._refresh_config_list()

    def _refresh_config_list(self):
        """Refresh the configuration list with new detailed formats."""
        if self.config_tree is None:
            for widget in self.tab_configurations.winfo_children():
                widget.destroy()
            self._setup_configurations_tab()
            return

        # Clear existing rows
        for item in self.config_tree.get_children():
            self.config_tree.delete(item)

        configs = db_manager.get_all_configurations()

        for c in configs:

            # Firearm: Type | Mfg | Name
            fire_str = f"{c.get('firearm_type', '')} | {c.get('firearm_mfg', '')} | {c.get('firearm_name', '')}"

            # Optic: Mfg | Type | Model (or "None")
            if c.get('optic_mfg'):
                optic_str = f"{c.get('optic_mfg')} | {c.get('optic_type', '')} | {c.get('optic_model', '')}"
            else:
                optic_str = "None"

            # Ammo: Caliber | Mfg | Grains | Name (or "None")
            if c.get('ammo_mfg'):
                grains = str(c.get('grains', '') or '')
                ammo_str = f"{c.get('caliber', '')} | {c.get('ammo_mfg')} | {c.get('grains')} | {c.get('ammo_name', '')}"
            else:
                ammo_str = "None"

            avg_score = c.get('avg_rating_score')
            rating_str = self._convert_rating_score_to_text(avg_score)

            # Values: Firearm, Optic, Ammo, Rating, Sys Id, Hidden Notes, Hidden ID
            values_tuple = (
                fire_str,
                optic_str,
                ammo_str,
                rating_str,
                str(c['id']),
                c.get('config_notes', ''),
                c['id']
            )

            # Text column (#0) shows the Notes
            self.config_tree.insert("", "end", text=c.get('config_notes', ''), values=values_tuple)

    def _on_config_double_click(self, event): self._edit_config()


#=============================================================
    # --- TAB 2: Firearms ---
    def _setup_firearms_tab(self) -> None:

        self.firearm_tree = None
        try:
            firearms = db_manager.get_active_firearms()
            if not firearms:
                lbl = ttk.Label(self.tab_firearms, text="No active firearms in database.", font=(FONT_FAMILY, 12))
                lbl.pack(pady=20)
            else:
                columns = ("Name", "Type", "Manufacturer", "Caliber", "Barrel", "Sys Id")

                self.firearm_tree = ttk.Treeview(self.tab_firearms, columns=columns, height=15, selectmode="browse")

                # Hide column #0
                self.firearm_tree.column("#0", width=0, stretch=False)

                for col in columns:
                    self.firearm_tree.heading(col, text=col, anchor=W)
                    if col == "Sys Id":
                        width = 60
                    elif col == "Name":
                        width = 225
                    elif col == "Type":
                        width = 175
                    elif col == "Manufacturer":
                        width = 250
                    elif col == "Barrel":
                        width = 100
                    else:  # Caliber
                        width = 150
                    self.firearm_tree.column(col, width=width, stretch=False, anchor=W)

                for f in firearms:
                    name_display = f.get('name', '')
                    self.firearm_tree.insert("", "end", text="",
                                values=(
                                    name_display,
                                    f.get('firearm_type', ''),
                                    f.get('mfg', ''),
                                    f.get('caliber_primary', ''),
                                    f.get('barrel_length', ''),
                                    str(f['id'])
                                ))

                self.firearm_tree.pack(fill=BOTH, expand=True, pady=10)
                self.firearm_tree.bind("<Double-1>", self._on_firearm_double_click)

        except Exception as e:
            lbl = ttk.Label(self.tab_firearms, text=f"Error: {e}", font=(FONT_FAMILY, 11), foreground="red")
            lbl.pack(pady=20)

        btn_frame = ttk.Frame(self.tab_firearms)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Firearm", bootstyle="primary", command=self._open_add_firearm).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", bootstyle="secondary", command=self._edit_firearm).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", bootstyle="danger", command=self._delete_firearm).pack(side=LEFT, padx=5)

    def _open_add_firearm(self):
        def on_save(data): self._refresh_firearm_list()
        FirearmForm(self.tab_firearms, on_save=on_save, firearm_data=None)

    def _edit_firearm(self):
        if not self.firearm_tree: return
        sel = self.firearm_tree.selection()
        if not sel: return messagebox.showwarning(self.root,"Selection", "Select a firearm.")

        item = self.firearm_tree.item(sel[0])
        firearm_id = int(str(item['values'][5]))

        target = db_manager.get_firearm_by_id(firearm_id)

        if target:
            def on_save(data): self._refresh_firearm_list()
            FirearmForm(self.tab_firearms, on_save=on_save, firearm_data=target)

    def _delete_firearm(self):
        if not self.firearm_tree: return
        sel = self.firearm_tree.selection()
        if not sel: return messagebox.showwarning(self.root,"Selection", "Select a firearm.")

        if messagebox.askyesno(self.root,"Confirm", "Delete this firearm?"):
            item = self.firearm_tree.item(sel[0])
            firearm_id = int(str(item['values'][5]))

            db_manager.delete_firearm(firearm_id)
            self._refresh_firearm_list()

    def _refresh_firearm_list(self):

        if self.firearm_tree is None:
            for widget in self.tab_firearms.winfo_children():
                widget.destroy()
            self._setup_firearms_tab()
            return

        for item in self.firearm_tree.get_children():
            self.firearm_tree.delete(item)

        firearms = db_manager.get_active_firearms()

        for f in firearms:
            name_display = f.get('name', '')
            self.firearm_tree.insert("", "end", text="",
                                values=(
                                    name_display,
                                    f.get('firearm_type', ''),
                                    f.get('mfg', ''),
                                    f.get('caliber_primary', ''),
                                    f.get('barrel_length', ''),
                                    str(f['id'])
                                ))

    def _on_firearm_double_click(self, event): self._edit_firearm()

    # --- TAB 3: Optics ---
    def _setup_optics_tab(self) -> None:

        self.optic_tree = None
        try:
            optics = db_manager.get_all_optics()
            if not optics:
                lbl = ttk.Label(self.tab_optics, text="No optics in database.", font=(FONT_FAMILY, 12))
                lbl.pack(pady=20)
            else:
                columns = ("Manufacturer", "Type", "Model", "Sys Id")

                self.optic_tree = ttk.Treeview(self.tab_optics, columns=columns, height=15, selectmode="browse")

                # Hide the default #0 column
                self.optic_tree.column("#0", width=0, stretch=False)

                for col in columns:
                    self.optic_tree.heading(col, text=col, anchor=W)
                    if col == "Sys Id":
                        width = 60
                    elif col == "Type":
                        width = 150
                    elif col == "Model":
                        width = 150
                    else:
                        width = 200
                    self.optic_tree.column(col, width=width, anchor=W)

                for o in optics:
                    values_tuple = (
                        o['mfg'],
                        o.get('optic_type', ''),
                        o.get('model', ''),
                        str(o['id'])
                    )
                    self.optic_tree.insert("", "end", values=values_tuple)

                self.optic_tree.pack(fill=BOTH, expand=True, pady=10)
                self.optic_tree.bind("<Double-1>", self._on_optic_double_click)

        except Exception as e:
            lbl = ttk.Label(self.tab_optics, text=f"Error: {e}", font=(FONT_FAMILY, 11), foreground="red")
            lbl.pack(pady=20)

        btn_frame = ttk.Frame(self.tab_optics)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Optics", bootstyle="primary", command=self._open_add_optic).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", bootstyle="secondary", command=self._edit_optic).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", bootstyle="danger", command=self._delete_optic).pack(side=LEFT, padx=5)

    def _open_add_optic(self):
        def on_save(data): self._refresh_optic_list()
        OpticForm(self.tab_optics, on_save=on_save, optic_data=None)

    def _edit_optic(self):
        if not self.optic_tree: return
        sel = self.optic_tree.selection()
        if not sel: return messagebox.showwarning(self.root,"Selection", "Select an optic.")

        item = self.optic_tree.item(sel[0])
        optic_id = int(str(item['values'][3]))

        target = db_manager.get_optic_by_id(optic_id)

        if target:
            def on_save(data): self._refresh_optic_list()
            OpticForm(self.tab_optics, on_save=on_save, optic_data=target)

    def _delete_optic(self):
        if not self.optic_tree: return
        sel = self.optic_tree.selection()
        if not sel: return messagebox.showwarning(self.root,"Selection", "Select an optic.")

        if messagebox.askyesno(self.root,"Confirm", "Delete this optic?"):
            item = self.optic_tree.item(sel[0])
            optic_id = int(str(item['values'][3]))

            db_manager.delete_optic(optic_id)
            self._refresh_optic_list()

    def _refresh_optic_list(self):
        """Refresh the optic list. Rebuilds tab if tree is None."""
        if self.optic_tree is None:
            for widget in self.tab_optics.winfo_children():
                widget.destroy()
            self._setup_optics_tab()
            return

        for item in self.optic_tree.get_children():
            self.optic_tree.delete(item)

        optics = db_manager.get_all_optics()

        for o in optics:
            values_tuple = (
                o['mfg'],
                o.get('optic_type', ''),
                o.get('model', ''),
                str(o['id'])
            )
            self.optic_tree.insert("", "end", values=values_tuple)

    def _on_optic_double_click(self, event): self._edit_optic()



#=============================================================
    # --- TAB 4: Ammo ---
    def _setup_ammo_tab(self) -> None:

        self.ammo_tree = None
        try:
            ammo_loads = db_manager.get_all_ammo()
            if not ammo_loads:
                lbl = ttk.Label(self.tab_ammo, text="No ammo records in database.", font=(FONT_FAMILY, 12))
                lbl.pack(pady=20)
            else:
                columns = ("Manufacturer", "Caliber", "Projectile Weight", "Ammo Description", "Sys Id")

                self.ammo_tree = ttk.Treeview(self.tab_ammo, columns=columns, height=15, selectmode="browse")

                # Hide the default #0 column
                self.ammo_tree.column("#0", width=0, stretch=False)

                for col in columns:
                    self.ammo_tree.heading(col, text=col, anchor=W)
                    if col == "Sys Id":
                        width = 60
                    elif col == "Caliber":
                        width = 120
                    elif col == "Projectile Weight":
                        width = 150
                    elif col == "Ammo Description":
                        width = 250
                    else:  # Manufacturer
                        width = 150
                    self.ammo_tree.column(col, width=width, anchor=W)

                for a in ammo_loads:
                    # Column 3: Projectile Info logic
                    grains_val = a.get('grains')
                    shot_size_val = a.get('shot_size', '')
                    pellet_count_val = a.get('pellet_count')

                    if grains_val is not None and grains_val != '':
                        proj_info = f"{grains_val} gr"
                    elif shot_size_val and shot_size_val != 'n/a':
                        if pellet_count_val and pellet_count_val != 0:
                            proj_info = f"{shot_size_val} ({int(pellet_count_val)})"
                        else:
                            proj_info = shot_size_val
                    else:
                        proj_info = "Not Entered"

                    # Column 4: Name/ID logic
                    ammo_name_val = a.get('ammo_name', '')
                    bullet_name_val = a.get('bullet_name', '')
                    if ammo_name_val and ammo_name_val != 'n/a':
                        name_id = ammo_name_val
                    elif bullet_name_val and bullet_name_val != 'n/a':
                        name_id = bullet_name_val
                    else:
                        name_id = "Not Entered"

                    values_tuple = (
                        a['mfg'],
                        a.get('caliber', ''),
                        proj_info,
                        name_id,
                        str(a['id']),
                        a.get('do_not_rebuy', 0)
                    )
                    self.ammo_tree.insert("", "end", values=values_tuple)

                # Apply tags for Do Not Rebuy
                self.ammo_tree.tag_configure("bad_ammo", foreground="#FFCDD2")
                for child in self.ammo_tree.get_children():
                    values = self.ammo_tree.item(child)['values']
                    if len(values) > 5 and values[5]:
                        self.ammo_tree.item(child, tags=("bad_ammo",))

                self.ammo_tree.pack(fill=BOTH, expand=True, pady=10)
                self.ammo_tree.bind("<Double-1>", self._on_ammo_double_click)

        except Exception as e:
            lbl = ttk.Label(self.tab_ammo, text=f"Error: {e}", font=(FONT_FAMILY, 11), foreground="red")
            lbl.pack(pady=20)

        btn_frame = ttk.Frame(self.tab_ammo)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Ammo", bootstyle="primary", command=self._open_add_ammo).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", bootstyle="secondary", command=self._edit_ammo).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", bootstyle="danger", command=self._delete_ammo).pack(side=LEFT, padx=5)

    def _open_add_ammo(self):
        def on_save(data): self._refresh_ammo_list()
        AmmoForm(self.tab_ammo, on_save=on_save, ammo_data=None)

    def _edit_ammo(self):
        if not self.ammo_tree: return
        sel = self.ammo_tree.selection()
        if not sel: return messagebox.showwarning(self.root,"Selection", "Select an ammo record.")

        item = self.ammo_tree.item(sel[0])
        ammo_id = int(str(item['values'][4]))

        target = db_manager.get_ammo_by_id(ammo_id)

        if target:
            def on_save(data): self._refresh_ammo_list()
            AmmoForm(self.tab_ammo, on_save=on_save, ammo_data=target)

    def _delete_ammo(self):
        if not self.ammo_tree: return
        sel = self.ammo_tree.selection()
        if not sel: return messagebox.showwarning(self.root,"Selection", "Select an ammo record.")

        if messagebox.askyesno(self.root,"Confirm", "Delete this ammo record?"):
            item = self.ammo_tree.item(sel[0])
            ammo_id = int(str(item['values'][4]))

            db_manager.delete_ammo(ammo_id)
            self._refresh_ammo_list()

    def _refresh_ammo_list(self):
        """Refresh the ammo list. Rebuilds tab if tree is None."""
        if self.ammo_tree is None:
            for widget in self.tab_ammo.winfo_children():
                widget.destroy()
            self._setup_ammo_tab()
            return

        for item in self.ammo_tree.get_children():
            self.ammo_tree.delete(item)

        ammo_loads = db_manager.get_all_ammo()

        for a in ammo_loads:
            # Column 3: Projectile Info logic
            grains_val = a.get('grains')
            shot_size_val = a.get('shot_size', '')
            pellet_count_val = a.get('pellet_count')

            if grains_val is not None and grains_val != '':
                proj_info = f"{grains_val} gr"
            elif shot_size_val and shot_size_val != 'n/a':
                if pellet_count_val and pellet_count_val != 0:
                    proj_info = f"{shot_size_val} ({int(pellet_count_val)})"
                else:
                    proj_info = shot_size_val
            else:
                proj_info = "Not Entered"

            # Column 4: Name/ID logic
            ammo_name_val = a.get('ammo_name', '')
            bullet_name_val = a.get('bullet_name', '')
            if ammo_name_val and ammo_name_val != 'n/a':
                name_id = ammo_name_val
            elif bullet_name_val and bullet_name_val != 'n/a':
                name_id = bullet_name_val
            else:
                name_id = "Not Entered"

            values_tuple = (
                a['mfg'],
                a.get('caliber', ''),
                proj_info,
                name_id,
                str(a['id']),
                a.get('do_not_rebuy', 0)
            )
            self.ammo_tree.insert("", "end", values=values_tuple)

        # Apply tags for Do Not Rebuy
        self.ammo_tree.tag_configure("bad_ammo", foreground="#FFCDD2")
        for child in self.ammo_tree.get_children():
            values = self.ammo_tree.item(child)['values']
            if len(values) > 5 and values[5]:
                self.ammo_tree.item(child, tags=("bad_ammo",))

    def _on_ammo_double_click(self, event): self._edit_ammo()

#=============================================================
    # --- TAB 5: Range Log ---
    def _setup_range_tab(self) -> None:

        self.range_tree = None
        try:
            sessions = db_manager.get_all_range_sessions()
            if not sessions:
                lbl = ttk.Label(self.tab_range, text="No range sessions in database.", font=(FONT_FAMILY, 12))
                lbl.pack(pady=20)
            else:

                columns = ("Configuration", "Date", "Rounds", "Avg Velocity", "Avg MOA", "Rating", "Sys Id")

                self.range_tree = ttk.Treeview(self.tab_range, columns=columns, height=15, selectmode="browse")

                # Hide the default #0 column
                self.range_tree.column("#0", width=0, stretch=False)

                for col in columns:
                    self.range_tree.heading(col, text=col, anchor=W)
                    # Set widths
                    if col == "Sys Id":
                        width = 60
                    elif col == "Date":
                        width = 120
                    elif col == "Rounds":
                        width = 60
                    elif col == "Avg Velocity":
                        width = 90
                    elif col == "Avg MOA":
                        width = 75
                    elif col == "Rating":
                        width = 80
                    else:  # Configuration
                        width = 350
                    self.range_tree.column(col, width=width, anchor=W)

                for s in sessions:
                    values_tuple = self._build_range_row(s)
                    self.range_tree.insert("", "end", values=values_tuple)

                self.range_tree.pack(fill=BOTH, expand=True, pady=10)
                self.range_tree.bind("<Double-1>", self._on_range_double_click)

        except Exception as e:
            lbl = ttk.Label(self.tab_range, text=f"Error: {e}", font=(FONT_FAMILY, 11), foreground="red")
            lbl.pack(pady=20)

        btn_frame = ttk.Frame(self.tab_range)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Session", bootstyle="primary", command=self._open_add_range).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", bootstyle="secondary", command=self._edit_range).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", bootstyle="danger", command=self._delete_range).pack(side=LEFT, padx=5)

    def _open_add_range(self):
        def on_save(data):
            self._refresh_range_list()
            self._refresh_config_list()  # Refresh Configs too
        RangeForm(self.tab_range, on_save=on_save, session_data=None)

    def _edit_range(self):
        if not self.range_tree: return
        sel = self.range_tree.selection()
        if not sel: return messagebox.showwarning(self.root,"Selection", "Select a session.")

        item = self.range_tree.item(sel[0])
        session_id = int(str(item['values'][6]))

        target = db_manager.get_session_by_id(session_id)
        if not target:
            return messagebox.showerror(self.root,"Error", "Session not found.")

        def on_save(data):
            self._refresh_range_list()
            self._refresh_config_list()
        RangeForm(self.tab_range, on_save=on_save, session_data=target)

    def _delete_range(self):
        if not self.range_tree: return
        sel = self.range_tree.selection()
        if not sel: return messagebox.showwarning(self.root,"Selection", "Select a session.")

        if messagebox.askyesno(self.root,"Confirm", "Delete this session?"):
            item = self.range_tree.item(sel[0])
            session_id = int(str(item['values'][6]))
            db_manager.delete_range_session(session_id)
            self._refresh_range_list()

    def _build_range_row(self, s) -> tuple:

        fname = s.get('firearm_name') or 'Unknown'
        omfg = s.get('optic_mfg') or 'None'
        amfg = s.get('ammo_mfg') or 'None'
        caliber = s.get('caliber') or 'Unknown'

        config_str = f"{fname} | {omfg} | {amfg} {caliber}"
        date_str = s.get('date', '')

        # Rounds
        rounds = s.get('rounds_fired', 0)
        rounds_str = str(rounds) if rounds is not None else "0"

        # Avg Velocity
        vel_avg = s.get('vel_avg')
        vel_avg_str = f"{int(vel_avg)}" if vel_avg is not None else ""

        # Avg MOA
        moa_avg = s.get('moa_avg')
        moa_avg_str = f"{moa_avg:.2f}" if moa_avg is not None else ""

        # Rating
        rating_str = s.get('rating', '')

        return (
            config_str,
            date_str,
            rounds_str,
            vel_avg_str,
            moa_avg_str,
            rating_str,
            str(s['id'])
        )

    def _refresh_range_list(self):

        if self.range_tree is None:
            for widget in self.tab_range.winfo_children():
                widget.destroy()
            self._setup_range_tab()
            return

        for item in self.range_tree.get_children():
            self.range_tree.delete(item)

        sessions = db_manager.get_all_range_sessions()

        for s in sessions:
            values_tuple = self._build_range_row(s)
            self.range_tree.insert("", "end", values=values_tuple)

    def _on_range_double_click(self, event): self._edit_range()

#=============================================================
    # --- TAB 6: Reports
    def _setup_reports_tab(self) -> None:

        # Main Container
        main_frame = ttk.Frame(self.tab_reports, padding=MAIN_CONTAINER_PADDING)
        main_frame.pack(fill=BOTH, expand=True)

        # Configure Treeview style to remove borders/lines
        style = ttk.Style()
        style.configure('Treeview', borderwidth=0, relief="flat")
        style.configure('Treeview.Heading', borderwidth=0, relief="flat")

        # Configure grid weights for EQUAL sizing (uniform forces same width)
        main_frame.grid_rowconfigure(0, weight=1, uniform="rows")
        main_frame.grid_rowconfigure(1, weight=1, uniform="rows")
        main_frame.grid_columnconfigure(0, weight=1, uniform="cols")
        main_frame.grid_columnconfigure(1, weight=1, uniform="cols")

        # ==========================================
        # SECTION 1: Upper Left (Firearm Round Stats)
        # ==========================================
        sec1_frame = ttk.LabelFrame(main_frame, text="Firearm Round Stats")
        sec1_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Controls
        ctrl_frame = ttk.Frame(sec1_frame)
        ctrl_frame.pack(fill=X, pady=5)
        ttk.Label(ctrl_frame, text="Select Firearm:").pack(side=LEFT)
        self.sec1_firearm_var = tk.StringVar()
        self.sec1_firearm_combo = ttk.Combobox(ctrl_frame, textvariable=self.sec1_firearm_var, state="readonly", width=40)
        self.sec1_firearm_combo.pack(side=LEFT, padx=5)
        self.sec1_firearm_combo.bind('<<ComboboxSelected>>', lambda e: self._update_section1())

        # Display Area
        self.sec1_lbl_total = ttk.Label(sec1_frame, text="Total Rounds: --", font=(FONT_FAMILY, 11))
        self.sec1_lbl_total.pack(anchor=W, pady=(10, 5))

        self.sec1_lbl_top_ammo = ttk.Label(sec1_frame, text="Top Ammo: --", font=(FONT_FAMILY, 11))
        self.sec1_lbl_top_ammo.pack(anchor=W, pady=(0, 5))

        # ==========================================
        # SECTION 2: Upper Right (Top Configs by Caliber)
        # ==========================================
        sec2_frame = ttk.LabelFrame(main_frame, text="Top Configurations by Caliber")
        sec2_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Controls
        ctrl_frame2 = ttk.Frame(sec2_frame)
        ctrl_frame2.pack(fill=X, pady=5)
        ttk.Label(ctrl_frame2, text="Select Caliber:").pack(side=LEFT)
        self.sec2_caliber_var = tk.StringVar()
        self.sec2_caliber_combo = ttk.Combobox(ctrl_frame2, textvariable=self.sec2_caliber_var, state="readonly", width=20)
        self.sec2_caliber_combo.pack(side=LEFT, padx=5)
        self.sec2_caliber_combo.bind('<<ComboboxSelected>>', lambda e: self._update_section2())

        # Display Area (Mini-Table)
        cols2 = ("Rank", "Configuration", "Rating", "Rounds")
        self.sec2_tree = ttk.Treeview(sec2_frame, columns=cols2, height=6, selectmode="none")
        self.sec2_tree.heading("Rank", text="Rank", anchor=W)
        self.sec2_tree.heading("Configuration", text="Configuration", anchor=W)
        self.sec2_tree.heading("Rating", text="Rating", anchor=W)
        self.sec2_tree.heading("Rounds", text="Rounds", anchor=W)
        self.sec2_tree.column("#0", width=0, stretch=False)
        self.sec2_tree.column("Rank", width=40, anchor=W)
        self.sec2_tree.column("Configuration", width=200, anchor=W)
        self.sec2_tree.column("Rating", width=80, anchor=W)
        self.sec2_tree.column("Rounds", width=60, anchor=W)
        self.sec2_tree.pack(fill=BOTH, expand=True, pady=5)

        # ==========================================
        # SECTION 3: Lower Left (Configuration Stats)
        # ==========================================
        sec3_frame = ttk.LabelFrame(main_frame, text="Configuration Stats")
        sec3_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Controls
        ctrl_frame3 = ttk.Frame(sec3_frame)
        ctrl_frame3.pack(fill=X, pady=5)
        ttk.Label(ctrl_frame3, text="Select Configuration:").pack(side=LEFT)
        self.sec3_config_var = tk.StringVar()
        self.sec3_config_combo = ttk.Combobox(ctrl_frame3, textvariable=self.sec3_config_var, state="readonly", width=40)
        self.sec3_config_combo.pack(side=LEFT, padx=5)
        self.sec3_config_combo.bind('<<ComboboxSelected>>', lambda e: self._update_section3())

        # Display Area
        self.sec3_lbl_vel = ttk.Label(sec3_frame, text="Avg Velocity: --", font=(FONT_FAMILY, 11))
        self.sec3_lbl_vel.pack(anchor=W, pady=(10, 5))

        self.sec3_lbl_moa = ttk.Label(sec3_frame, text="Avg MOA: --", font=(FONT_FAMILY, 11))
        self.sec3_lbl_moa.pack(anchor=W, pady=(0, 5))

        #   ==========================================
        # SECTION 4: Lower Right (Ammo Mfg & Caliber Analysis)
        # ==========================================
        sec4_frame = ttk.LabelFrame(main_frame, text="Ammo Manfucturer & Caliber Analysis")
        sec4_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Controls
        ctrl_frame4 = ttk.Frame(sec4_frame)
        ctrl_frame4.pack(fill=X, pady=5)

        # Mfg Dropdown
        ttk.Label(ctrl_frame4, text="Manufacturer:").pack(side=LEFT)
        self.sec4_mfg_var = tk.StringVar()
        self.sec4_mfg_combo = ttk.Combobox(ctrl_frame4, textvariable=self.sec4_mfg_var, state="readonly", width=15)
        self.sec4_mfg_combo.pack(side=LEFT, padx=5)
        self.sec4_mfg_combo.bind('<<ComboboxSelected>>', lambda e: self._update_sec4_calibers())

        # Caliber Dropdown
        ttk.Label(ctrl_frame4, text="Caliber:").pack(side=LEFT, padx=(10, 0))
        self.sec4_caliber_var = tk.StringVar()
        self.sec4_caliber_combo = ttk.Combobox(ctrl_frame4, textvariable=self.sec4_caliber_var, state="readonly", width=15)
        self.sec4_caliber_combo.pack(side=LEFT, padx=5)
        self.sec4_caliber_combo.bind('<<ComboboxSelected>>', lambda e: self._update_section4())

        # Display Area (Mini-Table)
        cols4 = ("Rank", "Firearm", "Rating", "Rounds")
        self.sec4_tree = ttk.Treeview(sec4_frame, columns=cols4, height=6, selectmode="none")
        self.sec4_tree.heading("Rank", text="Rank", anchor=W)
        self.sec4_tree.heading("Firearm", text="Firearm", anchor=W)
        self.sec4_tree.heading("Rating", text="Rating", anchor=W)
        self.sec4_tree.heading("Rounds", text="Rounds", anchor=W)
        self.sec4_tree.column("#0", width=0, stretch=False)
        self.sec4_tree.column("Rank", width=40, anchor=W)
        self.sec4_tree.column("Firearm", width=180, anchor=W)
        self.sec4_tree.column("Rating", width=80, anchor=W)
        self.sec4_tree.column("Rounds", width=60, anchor=W)
        self.sec4_tree.pack(fill=BOTH, expand=True, pady=5)

        # --- Initial Population ---
        self._populate_dropdowns()


    def _populate_dropdowns(self) -> None:
        """Populate all dropdowns with initial data."""
        # Section 1: Firearms
        firearms = db_manager.get_active_firearms()
        self.sec1_firearm_combo['values'] = [
            f"{f['mfg']} {f['name']}" +
            (" " + f['caliber_primary'] if f.get('caliber_primary') else "") +
            (" " + f['caliber_secondary'] if f.get('caliber_secondary') else "")
            for f in firearms
        ]

        if self.sec1_firearm_combo['values']:
            self.sec1_firearm_combo.current(0)

        # Section 2: Calibers (Unique list from ammo)
        ammo = db_manager.get_all_ammo()
        calibers = sorted(list(set([a['caliber'] for a in ammo if a['caliber']])))
        self.sec2_caliber_combo['values'] = calibers
        if self.sec2_caliber_combo['values']:
            self.sec2_caliber_combo.current(0)

        # Section 3: Configurations
        configs = db_manager.get_all_configurations()
        self.sec3_config_combo['values'] = [f"{c['firearm_name']} | {c['optic_mfg'] or 'None'} | {c['ammo_mfg'] or 'None'}" for c in configs]
        if self.sec3_config_combo['values']:
            self.sec3_config_combo.current(0)

        # Section 4: Ammo Mfgs
        ammo = db_manager.get_all_ammo()
        mfgs = sorted(list(set([a['mfg'] for a in ammo if a['mfg']])))
        self.sec4_mfg_combo['values'] = mfgs
        if self.sec4_mfg_combo['values']:
            self.sec4_mfg_combo.current(0)
            # Trigger caliber update for first mfg
            self._update_sec4_calibers()

    def _update_sec4_calibers(self) -> None:
        """Update Caliber dropdown based on selected Mfg in Section 4."""
        mfg = self.sec4_mfg_var.get()
        if not mfg:
            self.sec4_caliber_combo['values'] = []
            return

        ammo = db_manager.get_all_ammo()
        # Filter by Mfg
        calibers = sorted(list(set([a['caliber'] for a in ammo if a['mfg'] == mfg and a['caliber']])))
        self.sec4_caliber_combo['values'] = calibers
        if self.sec4_caliber_combo['values']:
            self.sec4_caliber_combo.current(0)
        else:
            self.sec4_caliber_var.set("")

    # =============
    def _update_section1(self):
        """Fetch and display Firearm Performance Summary."""
        selected_firearm = self.sec1_firearm_var.get()

        # Reset to defaults if nothing selected
        if not selected_firearm:
            self.sec1_lbl_total.config(text="Total Rounds: --")
            self.sec1_lbl_top_ammo.config(text="Top Ammo: --")
            return

        # Find Firearm ID
        firearms = db_manager.get_active_firearms()
        fire_id = None

        for f in firearms:

            display_str = f"{f['mfg']} {f['name']}"
            if f.get('caliber_primary'):
                display_str += " " + f['caliber_primary']
            if f.get('caliber_secondary'):
                display_str += " " + f['caliber_secondary']

            if display_str == selected_firearm:
                fire_id = f['id']
                break

        if not fire_id:
            self.sec1_lbl_total.config(text="Total Rounds: --")
            self.sec1_lbl_top_ammo.config(text="Top Ammo: --")
            return

        # Fetch Data
        data = db_manager.get_firearm_performance_summary(fire_id)

        # Update Total Rounds Label
        self.sec1_lbl_total.config(text=f"Total Rounds Fired: {data['total_rounds']}")

        # Update Top Ammo Label (No Rating)
        if data['top_ammo']:
            ammo = data['top_ammo']
            ammo_str = f"{ammo['mfg']} {ammo['name']} ({ammo['caliber']})"
            self.sec1_lbl_top_ammo.config(text=f"Top Ammo: {ammo_str}")
        else:
            self.sec1_lbl_top_ammo.config(text="Top Ammo: No Data (Min 10 Rounds)")

#==================================
    def _update_section2(self):
        """Fetch and display Top Configs for selected Caliber."""
        # Clear existing rows
        for item in self.sec2_tree.get_children():
            self.sec2_tree.delete(item)

        selected_caliber = self.sec2_caliber_var.get()
        if not selected_caliber:
            self.sec2_tree.insert("", "end", values=("", "Select a Caliber", "", ""))
            return

        # Fetch Data
        results = db_manager.get_top_configs_for_caliber(selected_caliber)

        if not results:
            self.sec2_tree.insert("", "end", values=("", "No data found (Min 10 rounds)", "", ""))
            return

        # Insert Rows
        for i, item in enumerate(results):
            rank = i + 1
            config_str = f"{item['firearm']} | {item['optic']} | {item['ammo']}"
            self.sec2_tree.insert("", "end", values=(rank, config_str, item['rating'], item['rounds']))

#============================
    def _update_section3(self):
        """Fetch and display Stats for selected Configuration."""
        selected_config = self.sec3_config_var.get()

        if not selected_config:
            self.sec3_lbl_vel.config(text="Avg Velocity: --")
            self.sec3_lbl_moa.config(text="Avg MOA: --")
            return

        # Find Config ID
        configs = db_manager.get_all_configurations()
        config_id = None
        for c in configs:
            display_str = f"{c['firearm_name']} | {c['optic_mfg'] or 'None'} | {c['ammo_mfg'] or 'None'}"
            if display_str == selected_config:
                config_id = c['id']
                break

        if not config_id:
            self.sec3_lbl_vel.config(text="Avg Velocity: --")
            self.sec3_lbl_moa.config(text="Avg MOA: --")
            return

        # Fetch Data
        stats = db_manager.get_configuration_stats(config_id)

        # Update Labels
        vel_str = f"{int(stats['avg_vel'])}" if stats['avg_vel'] else "--"
        moa_str = f"{stats['avg_moa']:.2f}" if stats['avg_moa'] else "--"

        self.sec3_lbl_vel.config(text=f"Avg Velocity: {vel_str} fps")
        self.sec3_lbl_moa.config(text=f"Avg MOA: {moa_str}")

#=================================
    def _update_section4(self):
        """Fetch and display Top Firearms for selected Mfg + Caliber."""
        # Clear existing rows
        for item in self.sec4_tree.get_children():
            self.sec4_tree.delete(item)

        selected_mfg = self.sec4_mfg_var.get()
        selected_caliber = self.sec4_caliber_var.get()

        if not selected_mfg or not selected_caliber:
            self.sec4_tree.insert("", "end", values=("", "Select Mfg and Caliber", "", ""))
            return

        # Fetch Data
        results = db_manager.get_top_firearms_for_ammo(selected_mfg, selected_caliber)

        if not results:
            self.sec4_tree.insert("", "end", values=("", "No data found (Min 10 rounds)", "", ""))
            return

        # Insert Rows
        for i, item in enumerate(results):
            rank = i + 1
            self.sec4_tree.insert("", "end", values=(rank, item['firearm'], item['rating'], item['rounds']))

#================================
    def cleanup(self) -> None:
        """Clean up resources before window is destroyed."""
        try:
            db_manager.close()
        except Exception as e:
            print(f"Error closing database: {e}")
        self.quail_icon = None

if __name__ == "__main__":
    root = ttk.Tk()
    app = MainWindow(root, "testpassword")
    root.mainloop()
