from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QListWidget, QListWidgetItem,
                            QMessageBox)
import os
import logging
from PyQt5.QtCore import Qt, QDate, QTimer
from utils.backup_manager import BackupManager
from utils.error_handler import ErrorHandler

class BackupRestoreDialog(QDialog):
    """Dialog for selecting and restoring backups"""
    
    def __init__(self, theme_factory, parent=None):
        super().__init__(parent)
        self.theme_factory = theme_factory
        self.colors = theme_factory.create_color_scheme()
        self.fonts = theme_factory.create_font_scheme()
        self.setStyleSheet(theme_factory.create_style_sheet())
        
        self.setWindowTitle("Restore Backup")
        self.setMinimumSize(600, 400)
        
        self.setup_ui()
        self.load_backups()
    
    def setup_ui(self):
        """Set up the UI components"""
        layout = QVBoxLayout(self)
        
        # Instructions
        layout.addWidget(QLabel("Select a backup to restore:"))
        
        # Backup list
        self.backup_list = QListWidget()
        self.backup_list.setAlternatingRowColors(True)
        layout.addWidget(self.backup_list)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_backups)
        button_layout.addWidget(refresh_button)
        
        restore_button = QPushButton("Restore Selected")
        restore_button.clicked.connect(self.restore_selected_backup)
        button_layout.addWidget(restore_button)
        
        create_button = QPushButton("Create New Backup")
        create_button.clicked.connect(self.create_new_backup)
        button_layout.addWidget(create_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def load_backups(self):
        """Load and display available backups"""
        try:
            self.backup_list.clear()
            backups = BackupManager.list_backups()
            
            if not backups:
                item = QListWidgetItem("No backups found")
                self.backup_list.addItem(item)
                return
                
            for backup in backups:
                item = QListWidgetItem(f"{backup['datetime']} - {len(backup['files'])} files")
                item.setData(Qt.UserRole, backup['path'])  # Store path for later use
                self.backup_list.addItem(item)
                
        except Exception as e:
            ErrorHandler.handle_error(e, True, self, "Error Loading Backups")
    
    def restore_selected_backup(self):
        """Restore the selected backup"""
        selected_items = self.backup_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Selection Required", "Please select a backup to restore.")
            return
            
        backup_path = selected_items[0].data(Qt.UserRole)
        if not backup_path:
            return
            
        # Confirm restoration
        confirm = QMessageBox.question(
            self,
            "Confirm Restore",
            "Restoring a backup will replace your current data. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
            
        try:
            success = BackupManager.restore_backup(backup_path)
            
            if success:
                QMessageBox.information(
                    self,
                    "Restore Successful",
                    "Backup has been successfully restored. The application will now restart."
                )
                self.accept()
                
                # Signal that app should restart to reload data
                if hasattr(self.parent(), 'restart_application'):
                    self.parent().restart_application()
                else:
                    # Fallback if parent doesn't have restart method
                    QMessageBox.information(
                        self,
                        "Manual Restart Required",
                        "Please restart the application to apply changes."
                    )
            else:
                QMessageBox.critical(
                    self,
                    "Restore Failed",
                    "Failed to restore backup. See logs for details."
                )
                
        except Exception as e:
            ErrorHandler.handle_error(e, True, self, "Restore Error")
    
    def create_new_backup(self):
        """Create a new backup"""
        try:
            backup_dir = BackupManager.create_backup()
            
            if backup_dir:
                QMessageBox.information(
                    self,
                    "Backup Created",
                    f"New backup created at:\n{backup_dir}"
                )
                self.load_backups()  # Refresh the list
            else:
                QMessageBox.warning(
                    self,
                    "Backup Failed",
                    "Failed to create backup. Check logs for details."
                )
                
        except Exception as e:
            ErrorHandler.handle_error(e, True, self, "Backup Error")
