from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                            QLabel, QGroupBox, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QComboBox, QSpinBox, QCheckBox,
                            QMessageBox, QHeaderView, QLineEdit, QMenu,
                            QAction)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QKeySequence, QIcon, QColor  # Added QColor import here
import locale
from datetime import datetime
import os
import logging

from utils.error_handler import ErrorHandler

class MainView(QMainWindow):
    """Main view of the scheduler application"""
    
    def __init__(self, theme_factory):
        super().__init__()
        self.theme_factory = theme_factory
        self.colors = theme_factory.create_color_scheme()
        self.fonts = theme_factory.create_font_scheme()
        self.setStyleSheet(theme_factory.create_style_sheet())
        
        self.setWindowTitle("Task Scheduler")
        self.setMinimumSize(800, 600)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Initialize UI components
        self.today_task_button = None
        self.all_schedule_button = None
        self.calculate_button = None
        self.excel_export_button = None
        self.task_table = None
        self.date_label = None
        self.theme_toggle = None
        
        # Set up timer for date updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_date_label)
        self.timer.start(3600000)  # Update every hour
        
        # Set up shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        # Today's tasks (Ctrl+T)
        today_shortcut = QAction("Today's Tasks", self)
        today_shortcut.setShortcut(QKeySequence("Ctrl+T"))
        today_shortcut.triggered.connect(lambda: self.today_task_button.click() if self.today_task_button else None)
        self.addAction(today_shortcut)
        
        # All schedules (Ctrl+A)
        all_shortcut = QAction("All Schedules", self)
        all_shortcut.setShortcut(QKeySequence("Ctrl+A"))
        all_shortcut.triggered.connect(lambda: self.all_schedule_button.click() if self.all_schedule_button else None)
        self.addAction(all_shortcut)
        
        # Calculate (Ctrl+C)
        calc_shortcut = QAction("Calculate", self)
        calc_shortcut.setShortcut(QKeySequence("Ctrl+C"))
        calc_shortcut.triggered.connect(lambda: self.calculate_button.click() if self.calculate_button and self.calculate_button.isEnabled() else None)
        self.addAction(calc_shortcut)
        
        # Search (Ctrl+F)
        search_shortcut = QAction("Search", self)
        search_shortcut.setShortcut(QKeySequence("Ctrl+F"))
        search_shortcut.triggered.connect(self.focus_search)
        self.addAction(search_shortcut)
    
    def focus_search(self):
        """Focus the search box"""
        if self.search_box:
            self.search_box.setFocus()
    
    def build_header(self):
        """Build the header section with title and navigation buttons"""
        header_layout = QHBoxLayout()
        
        # Date label (top left)
        self.date_label = QLabel()
        self.date_label.setFont(self.fonts["normal"])
        self.update_date_label()  # Set initial date
        header_layout.addWidget(self.date_label)
        
        header_layout.addStretch(1)  # Add stretch to push title to center
        
        # Title
        title_label = QLabel("Task Scheduler")
        title_label.setFont(self.fonts["header"])
        header_layout.addWidget(title_label)
        
        # Theme toggle
        self.theme_toggle = QPushButton("🌙 / ☀️")  # Moon/sun icons
        self.theme_toggle.setToolTip("Toggle dark/light theme")
        self.theme_toggle.setMaximumWidth(50)
        self.theme_toggle.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_toggle)
        
        # Navigation buttons
        button_layout = QHBoxLayout()
        
        self.today_task_button = QPushButton("Today's Tasks")
        self.today_task_button.setFont(self.fonts["button"])
        self.today_task_button.setToolTip("Edit today's tasks (Ctrl+T)")
        button_layout.addWidget(self.today_task_button)
        
        self.all_schedule_button = QPushButton("All Schedules")
        self.all_schedule_button.setFont(self.fonts["button"])
        self.all_schedule_button.setToolTip("View and edit all scheduled tasks (Ctrl+A)")
        button_layout.addWidget(self.all_schedule_button)
        
        header_layout.addStretch(1)  # Add stretch to push buttons to right
        header_layout.addLayout(button_layout)
        self.main_layout.addLayout(header_layout)
    
    def build_content(self):
        """Build the main content section with today's tasks"""
        # Today's tasks group
        tasks_group = QGroupBox("Today's Tasks Window")
        tasks_group.setFont(self.fonts["normal"])
        tasks_layout = QVBoxLayout(tasks_group)
        
        # Task table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels(["Task Name", "Status", "Effort", "Completed", "Details"])
        self.task_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tasks_layout.addWidget(self.task_table)
        
        self.main_layout.addWidget(tasks_group)
    
    def build_footer(self):
        """Build the footer section with action buttons"""
        footer_layout = QHBoxLayout()
        
        # Calculation button
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.setFont(self.fonts["button"])
        self.calculate_button.setEnabled(False)  # Disabled initially
        self.calculate_button.setToolTip("Calculate work time distribution (Ctrl+C)")
        footer_layout.addWidget(self.calculate_button)
        
        # Excel export button
        self.excel_export_button = QPushButton("EXCEL Export")
        self.excel_export_button.setFont(self.fonts["button"])
        
        # Check for Excel dependencies
        try:
            from utils.excel_exporter import ExcelExporter, EXCEL_AVAILABLE, MISSING_DEPENDENCIES
            
            if EXCEL_AVAILABLE:
                self.excel_export_button.setEnabled(True)
                self.excel_export_button.setToolTip("Export tasks to Excel")
                self.excel_export_button.clicked.connect(self.export_to_excel)
            else:
                self.excel_export_button.setEnabled(False)
                missing = ", ".join(MISSING_DEPENDENCIES)
                self.excel_export_button.setToolTip(f"Excel export requires: {missing}")
        except ImportError:
            self.excel_export_button.setEnabled(False)
            self.excel_export_button.setToolTip("Excel export requires additional packages")
        
        footer_layout.addWidget(self.excel_export_button)
        
        # Backup menu
        backup_button = QPushButton("Backup/Restore")
        backup_button.setFont(self.fonts["button"])
        backup_menu = QMenu(self)
        
        create_backup_action = QAction("Create Backup", self)
        create_backup_action.triggered.connect(self.create_backup)
        backup_menu.addAction(create_backup_action)
        
        restore_backup_action = QAction("Restore from Backup", self)
        restore_backup_action.triggered.connect(self.show_restore_dialog)
        backup_menu.addAction(restore_backup_action)
        
        backup_button.setMenu(backup_menu)
        footer_layout.addWidget(backup_button)
        
        footer_layout.addStretch()
        self.main_layout.addLayout(footer_layout)
    
    def update_today_tasks(self, tasks):
        """Update the today's tasks table"""
        self.task_table.setRowCount(0)  # Clear existing rows
        
        for idx, task in enumerate(tasks):
            self.task_table.insertRow(idx)
            
            # Task name (not editable)
            name_item = QTableWidgetItem(task.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            
            # Set background color based on priority - Fix color handling
            try:
                color_str = task.get_priority_color()
                name_item.setBackground(QColor(color_str))
            except Exception as e:
                # Fallback to default color if there's an error
                name_item.setBackground(QColor("#2196F3"))  # Default blue
            
            self.task_table.setItem(idx, 0, name_item)
            
            # Status (dropdown)
            status_combo = QComboBox()
            status_combo.addItems(["Working", "Planned", "Completed"])
            # Map UI labels to internal values
            status_map = {"Working": "working", "Planned": "planned", "Completed": "closed"}
            reverse_map = {"working": "Working", "planned": "Planned", "closed": "Completed"}
            
            status_combo.setCurrentText(reverse_map.get(task.status, "Planned"))
            status_combo.currentTextChanged.connect(
                lambda text, t=task: self.update_task_attribute(t, "status", status_map.get(text, "planned"))
            )
            self.task_table.setCellWidget(idx, 1, status_combo)
            
            # Perceived effort (spinbox)
            effort_spin = QSpinBox()
            effort_spin.setRange(0, 100)
            effort_spin.setValue(task.perceived_effort)
            effort_spin.valueChanged.connect(lambda value, t=task: self.update_task_attribute(t, "perceived_effort", value))
            self.task_table.setCellWidget(idx, 2, effort_spin)
            
            # Completed today (checkbox)
            completed_check = QCheckBox()
            completed_check.setChecked(task.completed_today)
            completed_check.stateChanged.connect(lambda state, t=task: self.update_task_attribute(t, "completed_today", state == Qt.Checked))
            check_widget = QWidget()
            check_layout = QHBoxLayout(check_widget)
            check_layout.addWidget(completed_check)
            check_layout.setAlignment(Qt.AlignCenter)
            check_layout.setContentsMargins(0, 0, 0, 0)
            self.task_table.setCellWidget(idx, 3, check_widget)
            
            # Detail button
            detail_button = QPushButton("Details")
            self.task_table.setCellWidget(idx, 4, detail_button)
            # Connect to show task detail view
            detail_button.clicked.connect(lambda checked, t=task: self.show_task_detail(t))
        
        # 計算ボタンの有効/無効を更新
        self.update_calculate_button(tasks)
    
    def update_task_attribute(self, task, attribute, value):
        """Update a task attribute and notify the model"""
        if hasattr(task, attribute):
            setattr(task, attribute, value)
            if hasattr(self, 'task_detail_controller'):
                self.task_detail_controller.model.notify()
            # Update calculate button state after attribute change
            self.update_calculate_button(self.task_detail_controller.get_filtered_tasks() if hasattr(self, 'task_detail_controller') else [])
    
    def show_task_detail(self, task):
        """Show task detail in a new window"""
        if hasattr(self, 'task_detail_controller'):
            self.task_detail_controller.show_task_detail_view(task, self)
    
    # Remove the Observer.update method and replace with a method the controller can call
    def refresh_view(self, tasks):
        """Refresh the view with the provided tasks"""
        try:
            # Log the tasks being displayed for debugging
            task_names = [task.name for task in tasks]
            print(f"Refreshing main view with tasks: {task_names}")
            
            # Update the task table
            self.update_today_tasks(tasks)
            
            # Update calculate button status based on latest tasks
            self.update_calculate_button(tasks)
        except Exception as e:
            print(f"Error in MainView refresh: {e}")
            import traceback
            traceback.print_exc()

    def show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)

    def update_calculate_button(self, tasks):
        """Update the calculate button based on task completion status"""
        if not tasks:
            self.calculate_button.setEnabled(False)
            self.calculate_button.setToolTip("No tasks for today")
            return
            
        all_completed = all(task.completed_today for task in tasks)
        self.calculate_button.setEnabled(all_completed)
        
        if all_completed:
            self.calculate_button.setToolTip("All tasks are completed, calculation enabled")
        else:
            self.calculate_button.setToolTip("Complete all tasks to enable calculation")
    
    def set_task_detail_controller(self, controller):
        """タスク詳細表示用のコントローラーを設定"""
        self.task_detail_controller = controller

    def update_date_label(self):
        """Update the date label with current date information"""
        today = datetime.now()
        # Format: June 26, 2023 (Monday)
        date_format = today.strftime("%B %d, %Y (%A)")
        
        if self.date_label:
            self.date_label.setText(date_format)
        
        # English to Japanese day-of-week mapping
        dow_map = {
            'Monday': 'Monday',
            'Tuesday': 'Tuesday',
            'Wednesday': 'Wednesday',
            'Thursday': 'Thursday',
            'Friday': 'Friday',
            'Saturday': 'Saturday',
            'Sunday': 'Sunday'
        }
        
        for eng, jpn in dow_map.items():
            date_format = date_format.replace(eng, jpn)
        
        if self.date_label:
            self.date_label.setText(date_format)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        try:
            # Determine current theme by examining stylesheet
            current_stylesheet = self.styleSheet()
            is_dark = "background-color: #282828" in current_stylesheet
            
            # Create new theme factory based on desired theme
            if is_dark:
                from views.builders.theme_factory import LightThemeFactory
                new_factory = LightThemeFactory()
            else:
                from views.builders.theme_factory import DarkThemeFactory
                new_factory = DarkThemeFactory()
                
            # Apply new theme
            self.theme_factory = new_factory
            self.colors = new_factory.create_color_scheme()
            self.fonts = new_factory.create_font_scheme()
            self.setStyleSheet(new_factory.create_style_sheet())
            
            # Emit signal to notify about theme change
            if hasattr(self, 'task_detail_controller') and self.task_detail_controller:
                # Notify the controller about the theme change
                self.task_detail_controller.model.notify()
                
            logging.info(f"Theme changed to {'light' if is_dark else 'dark'}")
            
        except Exception as e:
            ErrorHandler.handle_error(e, True, self, "Theme Toggle Error")
    
    def export_to_excel(self):
        """Export tasks to Excel"""
        try:
            from utils.excel_exporter import ExcelExporter, EXCEL_AVAILABLE, MISSING_DEPENDENCIES
            
            if not EXCEL_AVAILABLE:
                missing = ", ".join(MISSING_DEPENDENCIES)
                QMessageBox.warning(
                    self,
                    "Missing Dependencies",
                    f"Excel export requires the following Python packages: {missing}\n\n"
                    f"Please install them using pip:\npip install {' '.join(MISSING_DEPENDENCIES)}"
                )
                return
            
            # Get tasks from controller
            if hasattr(self, 'task_detail_controller'):
                tasks = self.task_detail_controller.get_all_tasks()
                
                # Export
                filename = ExcelExporter.export_tasks(tasks)
                
                if filename:
                    QMessageBox.information(
                        self, 
                        "Export Successful", 
                        f"Tasks exported to:\n{filename}"
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Export Failed",
                        "Failed to export tasks. Check the logs for details."
                    )
                    
        except Exception as e:
            ErrorHandler.handle_error(e, True, self, "Export Error")
    
    def create_backup(self):
        """Create a data backup"""
        try:
            from utils.backup_manager import BackupManager
            
            backup_dir = BackupManager.create_backup()
            
            if backup_dir:
                QMessageBox.information(
                    self, 
                    "Backup Created", 
                    f"Backup created successfully at:\n{backup_dir}"
                )
            else:
                QMessageBox.warning(
                    self, 
                    "Backup Failed", 
                    "Failed to create backup. Check logs for details."
                )
                
        except Exception as e:
            ErrorHandler.handle_error(e, True, self, "Backup Error")
    
    def show_restore_dialog(self):
        """Show dialog to select and restore a backup"""
        # This would be implemented as a new dialog to select from available backups
        # For now, show a message that this feature is coming soon
        QMessageBox.information(
            self,
            "Coming Soon",
            "The restore from backup feature will be available in a future update."
        )
    def create_backup(self):
        """Create a data backup"""
        try:
            from utils.backup_manager import BackupManager
            
            backup_dir = BackupManager.create_backup()
            
            if backup_dir:
                QMessageBox.information(
                    self, 
                    "Backup Created", 
                    f"Backup created successfully at:\n{backup_dir}"
                )
            else:
                QMessageBox.warning(
                    self, 
                    "Backup Failed", 
                    "Failed to create backup. Check logs for details."
                )
                
        except Exception as e:
            ErrorHandler.handle_error(e, True, self, "Backup Error")
    
    def show_restore_dialog(self):
        """Show dialog to select and restore a backup"""
        # This would be implemented as a new dialog to select from available backups
        # For now, show a message that this feature is coming soon
        QMessageBox.information(
            self,
            "Coming Soon",
            "The restore from backup feature will be available in a future update."
        )
