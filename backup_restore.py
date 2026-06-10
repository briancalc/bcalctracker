#backup_restore.py

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
    """Manages encrypted backups and restoration of the datadb folder."""

    def __init__(self, datadb_path: Path, backups_path: Optional[Path] = None):
        """
        Initialize BackupManager.

        Args:
            datadb_path: Path to ~/bcalctrack/datadb folder
            backups_path: Path to store backups (defaults to ~/bcalctrack/backups)
        """
        self.datadb_path = Path(datadb_path)
        self.backups_path = Path(backups_path) if backups_path else self.datadb_path.parent / "backups"
        self.backups_path.mkdir(parents=True, exist_ok=True)
        print(f"[DEBUG] BackupManager initialized. Data: {self.datadb_path}, Backups: {self.backups_path}")

    def create_backup(self, password: str) -> Tuple[bool, str]:
        try:
            if not self.datadb_path.exists():
                error_msg = f"Datadb folder not found: {self.datadb_path}"
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

                # Add all files from datadb folder
                file_count = 0
                for file_path in self.datadb_path.rglob('*'):
                    if file_path.is_file():
                        # Calculate relative path for archive
                        arcname = file_path.relative_to(self.datadb_path.parent)
                        zf.write(file_path, arcname=arcname)
                        file_count += 1

                print(f"[DEBUG] Added {file_count} files to backup")

            backup_size_mb = backup_file.stat().st_size / (1024 * 1024)
            message = f"Backup created successfully!\n\nFile: {backup_file.name}\nSize: {backup_size_mb:.2f} MB"
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
        Restore from a backup (overwrites current datadb folder).
        Creates a safety backup of current data before restoration.

        Args:
            backup_path: Path to backup ZIP file
            password: Password for decryption

        Returns:
            Tuple of (success: bool, message: str)
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

                # Verify extraction
                extracted_datadb = temp_path / "datadb"
                if not extracted_datadb.exists():
                    error_msg = "Backup is corrupted: datadb folder not found in archive"
                    print(f"[ERROR] {error_msg}")
                    return False, error_msg


                # Create safety backup of current datadb before replacing
                safety_backup_path = None
                if self.datadb_path.exists():
                    safety_backup_path = self.datadb_path.parent / f"datadb_safety_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    print(f"[DEBUG] Creating safety backup: {safety_backup_path}")
                    shutil.copytree(self.datadb_path, safety_backup_path)

                    # Remove old datadb
                    shutil.rmtree(self.datadb_path)

                # Move restored datadb into place
                shutil.move(str(extracted_datadb), str(self.datadb_path))
                print(f"[DEBUG] Datadb restored successfully")

                # CLEANUP: Delete safety backup folder after successful restore
                if safety_backup_path and safety_backup_path.exists():
                    try:
                        shutil.rmtree(safety_backup_path)
                        print(f"[DEBUG] Cleaned up safety backup: {safety_backup_path}")
                    except Exception as e:
                        print(f"[WARNING] Could not delete safety backup: {e}")

                message = (
                    f"Restore completed successfully!\n\n"
                    f"Restored from: {backup_path.name}\n\n"
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
                if not any('datadb' in f for f in file_list):
                    error_msg = "Backup is missing datadb folder"
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
