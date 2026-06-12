# backup_restore.py

"""
Backup and restore functionality for encrypted database folder.
Uses pyzipper for AES-256 encrypted ZIP archives.
Integrates with database password for encryption.
"""
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple

try:
    import pyzipper
except ImportError:
    raise ImportError("pyzipper is required. Install with: pip install pyzipper")


class BackupManager:
    """Manages encrypted backups and restoration of the user data root."""

    def __init__(self, data_root: Path, backups_path: Optional[Path] = None):
        """
        Initialize BackupManager.

        Args:
            data_root: Path to <Project>/datadb folder (contains .db and .auth)
            backups_path: Path to store backups (defaults to <Project>/backups)
        """
        self.data_root = Path(data_root).resolve()

        # Determine backups path relative to data_root if not provided
        if backups_path:
            self.backups_path = Path(backups_path).resolve()
        else:
            # Assumes parent of datadb is the project root, so sibling 'backups' exists
            self.backups_path = self.data_root.parent / "backups"


        print(f"[DEBUG] BackupManager initialized. Data: {self.data_root}, Backups: {self.backups_path}")

    def create_backup(self, password: str) -> Tuple[bool, str]:
        try:

            if not self.data_root.exists():
                error_msg = f"Data root folder not found: {self.data_root}"
                print(f"[ERROR] {error_msg}")
                return False, error_msg

            if not self.backups_path.exists():
                error_msg = f"Backups folder not found: {self.backups_path}"
                print(f"[ERROR] {error_msg}")
                return False, error_msg

            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_file = self.backups_path / f"backup_{timestamp}.zip"
            print(f"[DEBUG] Creating backup: {backup_file}")

            # Create encrypted ZIP
            with pyzipper.AESZipFile(
                str(backup_file),
                'w',
                compression=pyzipper.ZIP_DEFLATED,
                encryption=pyzipper.WZ_AES
            ) as zf:
                zf.setpassword(password.encode('utf-8'))

                # Add all files from data_root EXCEPT the backups folder itself
                file_count = 0
                skipped_dirs = ["backups"]

                for file_path in self.data_root.rglob('*'):
                    if file_path.is_file():
                        # Check if file is inside a skipped directory
                        is_skipped = False
                        rel_path_parts = file_path.relative_to(self.data_root).parts

                        for skip_dir in skipped_dirs:
                            if skip_dir in rel_path_parts:
                                is_skipped = True
                                break

                        if not is_skipped:
                            arcname = file_path.relative_to(self.data_root)
                            zf.write(file_path, arcname=arcname)
                            file_count += 1

                print(f"[DEBUG] Added {file_count} files to backup")

            backup_size_mb = backup_file.stat().st_size / (1024 * 1024)
            message = (
                f"Backup created successfully!\n\n"
                f"Source: {self.data_root}\n"
                f"File: {backup_file.name}\n"
                f"Size: {backup_size_mb:.2f} MB"
            )
            print(f"[DEBUG] {message}")
            return True, message

        except Exception as e:
            error_msg = f"Backup failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            return False, error_msg

    def list_backups(self) -> List[Path]:
        if not self.backups_path.exists():
            print(f"[DEBUG] Backups folder does not exist: {self.backups_path}")
            return []

        backups = sorted(
            self.backups_path.glob("backup_*.zip"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        print(f"[DEBUG] Found {len(backups)} backups")
        return backups

    def get_backup_info(self, backup_path: Path) -> Tuple[str, str]:
        try:
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(backup_path.stat().st_mtime)
            date_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
            info = f"{date_str}  •  {size_mb:.2f} MB"
            return backup_path.name, info
        except Exception as e:
            print(f"[ERROR] Failed to get backup info for {backup_path}: {e}")
            return backup_path.name, "Unknown"

    def restore_backup(self, backup_path: Path, password: str) -> Tuple[bool, str]:
        """
        Restore from a backup (overwrites current data root content).
        Creates a safety backup of current data before restoration.

        ASSUMPTIONS:
        - backup_path exists
        - data_root exists and is writable
        - backups_path exists
        """
        try:
            if not backup_path.exists():
                error_msg = f"Backup file not found: {backup_path}"
                print(f"[ERROR] {error_msg}")
                return False, error_msg

            print(f"[DEBUG] Starting restore from: {backup_path}")

            # Create temporary extraction directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Extract backup
                try:
                    with pyzipper.AESZipFile(str(backup_path), 'r') as zf:
                        zf.setpassword(password.encode('utf-8'))
                        zf.extractall(path=temp_path)
                        print(f"[DEBUG] Extracted backup successfully")
                except RuntimeError as e:
                    if "Bad password" in str(e):
                        error_msg = "Backup decryption failed: Incorrect password"
                    else:
                        error_msg = f"Extraction failed: {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    return False, error_msg

                # Verify extraction: Check for critical files (.db or .auth)
                has_db = any(temp_path.glob("*.db"))
                has_auth = (temp_path / ".auth").exists()

                if not has_db and not has_auth:
                    error_msg = "Backup is corrupted: No database (.db) or auth (.auth) files found in archive."
                    print(f"[ERROR] {error_msg}")
                    return False, error_msg

                # Create safety backup of current data_root before replacing
                safety_backup_path = None

                # Identify what to back up (exclude the backups folder itself)
                items_to_backup = [f for f in self.data_root.iterdir()
                                   if f.name != "backups" and f.name != ".gitkeep"]

                if items_to_backup:
                    safety_backup_path = self.data_root.parent / f"data_safety_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    print(f"[DEBUG] Creating safety backup at: {safety_backup_path}")

                    # Create the safety backup folder ONLY if we are moving data
                    safety_backup_path.mkdir(parents=True, exist_ok=True)

                    for item in items_to_backup:
                        if item.is_dir():
                            shutil.copytree(item, safety_backup_path / item.name)
                        else:
                            shutil.copy2(item, safety_backup_path / item.name)

                    # Now clear the data root
                    print(f"[DEBUG] Clearing current data root...")
                    for item in items_to_backup:
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()

                # Move restored content into place
                print(f"[DEBUG] Moving restored content to data root...")
                for item in temp_path.iterdir():
                    dest = self.data_root / item.name
                    if item.is_dir():
                        shutil.move(str(item), str(dest))
                    else:
                        shutil.move(str(item), str(dest))

                print(f"[DEBUG] Data restored successfully")

                # CLEANUP: Delete safety backup folder after successful restore
                if safety_backup_path and safety_backup_path.exists():
                    try:
                        shutil.rmtree(safety_backup_path)
                        print(f"[DEBUG] Cleaned up safety backup: {safety_backup_path}")
                    except Exception as e:
                        print(f"[WARNING] Could not delete safety backup: {e}")

                message = (
                    f"Restore completed successfully!\n\n"
                    f"Restored from: {backup_path.name}\n"
                    f"Location: {self.data_root}\n"
                )
                print(f"[DEBUG] {message}")
                return True, message

        except Exception as e:
            error_msg = f"Restore failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            return False, error_msg

    def verify_backup(self, backup_path: Path, password: str) -> Tuple[bool, str]:
        try:
            with pyzipper.AESZipFile(str(backup_path), 'r') as zf:
                zf.setpassword(password.encode('utf-8'))
                file_list = zf.namelist()

                # Check for critical files in the root of the archive
                has_db = any(f.endswith('.db') for f in file_list)
                has_auth = '.auth' in file_list or any(f == '.auth' or f.startswith('./.auth') for f in file_list)

                if not has_db and not has_auth:
                    error_msg = "Backup verification failed: Missing critical files (.db or .auth)"
                    print(f"[ERROR] {error_msg}")
                    return False, error_msg

                print(f"[DEBUG] Backup verification passed: {len(file_list)} files")
                return True, f"Backup is valid ({len(file_list)} files)"

        except RuntimeError as e:
            if "Bad password" in str(e):
                error_msg = "Backup password verification failed: Incorrect password"
            else:
                error_msg = f"Backup verification failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Backup verification failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            return False, error_msg

    def delete_backup(self, backup_path: Path) -> Tuple[bool, str]:
        try:
            backup_path.unlink()
            message = f"Backup deleted: {backup_path.name}"
            print(f"[DEBUG] {message}")
            return True, message
        except Exception as e:
            error_msg = f"Failed to delete backup: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
