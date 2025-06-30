"""
Backup and restore functionality for application data
"""
import os
import json
import shutil
import datetime
import logging

from .config import BACKUP_DIR, DATA_FILES

class BackupManager:
    """Manages data backups and restoration"""
    
    @staticmethod
    def create_backup():
        """Create backup of all configuration files"""
        # Ensure backup directory exists
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(BACKUP_DIR, timestamp)
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup all conf files
            for key, file_path in DATA_FILES.items():
                if os.path.exists(file_path):
                    target_path = os.path.join(backup_dir, os.path.basename(file_path))
                    shutil.copy(file_path, target_path)
                    logging.info(f"Backed up {key} to {target_path}")
            
            # Create a backup info file
            with open(os.path.join(backup_dir, "backup_info.json"), "w") as f:
                info = {
                    "timestamp": timestamp,
                    "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "files": list(DATA_FILES.keys())
                }
                json.dump(info, f, indent=4)
                
            logging.info(f"Backup completed: {backup_dir}")
            return backup_dir
        
        except Exception as e:
            logging.error(f"Backup failed: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def list_backups():
        """List all available backups"""
        if not os.path.exists(BACKUP_DIR):
            return []
            
        backups = []
        for backup_dir in os.listdir(BACKUP_DIR):
            full_path = os.path.join(BACKUP_DIR, backup_dir)
            if os.path.isdir(full_path):
                info_file = os.path.join(full_path, "backup_info.json")
                if os.path.exists(info_file):
                    with open(info_file, "r") as f:
                        try:
                            info = json.load(f)
                            backups.append({
                                "dir": backup_dir,
                                "path": full_path,
                                "datetime": info.get("datetime", "Unknown"),
                                "files": info.get("files", [])
                            })
                        except:
                            # If info file is corrupted, still include basic info
                            backups.append({
                                "dir": backup_dir,
                                "path": full_path,
                                "datetime": "Info file corrupted",
                                "files": []
                            })
        
        # Sort backups by directory name (which contains timestamp)
        backups.sort(key=lambda b: b["dir"], reverse=True)
        return backups
    
    @staticmethod
    def restore_backup(backup_path):
        """Restore data from a backup"""
        if not os.path.exists(backup_path):
            logging.error(f"Backup path not found: {backup_path}")
            return False
        
        try:
            # Create backup of current files first
            BackupManager.create_backup()
            
            # Restore files from backup
            for key, file_path in DATA_FILES.items():
                backup_file = os.path.join(backup_path, os.path.basename(file_path))
                if os.path.exists(backup_file):
                    shutil.copy(backup_file, file_path)
                    logging.info(f"Restored {key} from backup")
            
            logging.info(f"Backup restored successfully from {backup_path}")
            return True
        
        except Exception as e:
            logging.error(f"Restore failed: {str(e)}", exc_info=True)
            return False
