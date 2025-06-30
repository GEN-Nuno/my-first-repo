from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QTableWidget, QTableWidgetItem,
                            QHeaderView, QDialog, QFormLayout, QLineEdit, 
                            QTextEdit, QComboBox, QCheckBox, QGroupBox,
                            QMessageBox)
from PyQt5.QtCore import Qt
# Remove Observer import
from models.task_model import Task
from views.tag_edit_view import TagEditDialog

class AllScheduleView(QMainWindow):
    """View for editing all scheduled tasks"""
    
    def __init__(self, theme_factory):
        super().__init__()
        self.theme_factory = theme_factory
        self.colors = theme_factory.create_color_scheme()
        self.fonts = theme_factory.create_font_scheme()
        self.setStyleSheet(theme_factory.create_style_sheet())
        
        self.controller = None
        self.tasks = []
        self.tags = []
        
        self.setWindowTitle("Edit All Schedules")
        self.setMinimumSize(900, 600)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
    
    def set_controller(self, controller):
        """Set the controller for this view"""
        self.controller = controller
    
    def set_tasks(self, tasks):
        """Set the tasks to display"""
        self.tasks = tasks
        self.update_task_table()
    
    def set_tags(self, tags):
        """Set available tags"""
        self.tags = tags
    
    def build_header(self):
        """Build the header section"""
        header_layout = QHBoxLayout()
        
        title_label = QLabel("All Schedules")
        title_label.setFont(self.fonts["header"])
        header_layout.addWidget(title_label)
        
        # Add search box to All Schedules view
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search tasks...")
        self.search_box.setMaximumWidth(200)
        self.search_box.textChanged.connect(self.search_tasks)
        header_layout.addWidget(self.search_box)
        
        self.main_layout.addLayout(header_layout)
    
    def build_content(self):
        """Build the main content section with task table"""
        # Task table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)  # Name, Status, Days, Tags, Edit, Delete
        self.task_table.setHorizontalHeaderLabels(["Task Name", "Status", "Days", "Tags", "Edit", "Delete"])
        self.task_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.main_layout.addWidget(self.task_table)
    
    def build_footer(self):
        """Build the footer section with action buttons"""
        button_layout = QHBoxLayout()
        
        # Add task button
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.show_add_task_dialog)
        button_layout.addWidget(self.add_button)
        
        # Tags button
        self.tags_button = QPushButton("Tags")
        self.tags_button.clicked.connect(self.show_tags_dialog)
        button_layout.addWidget(self.tags_button)
        
        # Bulk delete button
        self.bulk_delete_button = QPushButton("Delete Completed")
        self.bulk_delete_button.clicked.connect(self.delete_closed_tasks)
        button_layout.addWidget(self.bulk_delete_button)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_tasks)
        button_layout.addWidget(self.save_button)
        
        self.main_layout.addLayout(button_layout)
    
    def update_task_table(self):
        """Update the task table with current tasks"""
        self.task_table.setRowCount(0)  # Clear existing rows

        for idx, task in enumerate(self.tasks):
            self.task_table.insertRow(idx)
            
            # Name column
            name_item = QTableWidgetItem(task.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.task_table.setItem(idx, 0, name_item)
            
            # Status column
            status_item = QTableWidgetItem(task.status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.task_table.setItem(idx, 1, status_item)
            
            # Days column
            days_item = QTableWidgetItem(", ".join(task.days))
            days_item.setFlags(days_item.flags() & ~Qt.ItemIsEditable)
            self.task_table.setItem(idx, 2, days_item)
            
            # Tags column
            tags_item = QTableWidgetItem(", ".join(task.tags))
            tags_item.setFlags(tags_item.flags() & ~Qt.ItemIsEditable)
            self.task_table.setItem(idx, 3, tags_item)
            
            # Edit button
            edit_btn = QPushButton("編集")
            edit_btn.clicked.connect(lambda _, t=task: self.show_edit_task_dialog(t))
            self.task_table.setCellWidget(idx, 4, edit_btn)
            
            # Delete button
            delete_btn = QPushButton("削除")
            delete_btn.clicked.connect(lambda _, t=task: self.delete_task(t))
            self.task_table.setCellWidget(idx, 5, delete_btn)
    
    def show_add_task_dialog(self):
        """Show dialog for adding a new task"""
        dialog = TaskDialog(self.theme_factory, None, self.tags)
        if dialog.exec_() == QDialog.Accepted:
            # Create new task
            task = self.controller.create_new_task(
                name=dialog.name_edit.text(),
                status=dialog.status_combo.currentText(),
                days=dialog.get_selected_days(),
                details=dialog.details_edit.toPlainText(),
                tags=[dialog.tags_combo.currentText()]
            )
            self.controller.add_task(task)
            self.update_task_table()
    
    def show_edit_task_dialog(self, task):
        """Show dialog for editing an existing task"""
        dialog = TaskDialog(self.theme_factory, task, self.tags)
        if dialog.exec_() == QDialog.Accepted:
            # Update task
            attributes = {
                "name": dialog.name_edit.text(),
                "status": dialog.status_combo.currentText(),
                "days": dialog.get_selected_days(),
                "details": dialog.details_edit.toPlainText(),
                "tags": [dialog.tags_combo.currentText()]
            }
            self.controller.update_task(task, attributes)
            self.update_task_table()
    
    def delete_task(self, task):
        """Delete a single task"""
        confirm = QMessageBox.question(
            self, "Confirm", f"Delete task '{task.name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.controller.delete_task(task)
            self.update_task_table()
    
    def delete_closed_tasks(self):
        """Delete all closed tasks"""
        closed_tasks = [task for task in self.tasks if task.status == "closed"]
        if not closed_tasks:
            QMessageBox.information(self, "Information", "No completed tasks to delete.")
            return
            
        confirm = QMessageBox.question(
            self, "Confirm", f"Delete {len(closed_tasks)} completed tasks?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.controller.delete_closed_tasks()
            self.update_task_table()
    
    def show_tags_dialog(self):
        """Show dialog for editing tags"""
        dialog = TagEditDialog(self.theme_factory, self.tags, self.controller)
        if dialog.exec_() == QDialog.Accepted:
            # Tags are updated directly in the controller
            self.tags = self.controller.model.tags
    
    def save_tasks(self):
        """Save all tasks"""
        if self.controller.save_tasks():
            QMessageBox.information(self, "Success", "Tasks saved successfully.")
    
    # Replace Observer update method with controller-driven refresh
    def refresh_view(self, tasks=None, tags=None):
        """Refresh the view with data from controller"""
        if tasks is not None:
            self.tasks = tasks
        if tags is not None:
            self.tags = tags
        
        self.update_task_table()
        
        # Make sure controller is properly set
        if not self.controller and hasattr(self, 'controller_ref'):
            self.controller = self.controller_ref

    def search_tasks(self, text):
        """Filter tasks based on search text"""
        if not text.strip():
            # If search is empty, show all rows
            for row in range(self.task_table.rowCount()):
                self.task_table.setRowHidden(row, False)
            return
        
        # Otherwise, hide rows that don't match the search text
        text = text.lower()
        for row in range(self.task_table.rowCount()):
            show_row = False
            
            # Check task name
            name_item = self.task_table.item(row, 0)
            if name_item and text in name_item.text().lower():
                show_row = True
                
            # Check task status
            status_item = self.task_table.item(row, 1)
            if status_item and text in status_item.text().lower():
                show_row = True
                
            # Check task days
            days_item = self.task_table.item(row, 2)
            if days_item and text in days_item.text().lower():
                show_row = True
                
            # Check task tags
            tags_item = self.task_table.item(row, 3)
            if tags_item and text in tags_item.text().lower():
                show_row = True
                
            self.task_table.setRowHidden(row, not show_row)

class TaskDialog(QDialog):
    """Dialog for adding or editing a task"""
    
    def __init__(self, theme_factory, task=None, tags=None):
        super().__init__()
        self.theme_factory = theme_factory
        self.colors = theme_factory.create_color_scheme()
        self.fonts = theme_factory.create_font_scheme()
        self.setStyleSheet(theme_factory.create_style_sheet())
        
        self.task = task
        self.tags = tags or []
        
        self.setWindowTitle("タスク編集" if task else "タスク追加")
        self.setup_ui()
        
        # Fill with task data if editing
        if task:
            self.populate_task_data()
    
    def setup_ui(self):
        """Set up the UI components"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Task name
        self.name_edit = QLineEdit()
        form_layout.addRow("タスク名:", self.name_edit)
        
        # Status dropdown
        self.status_combo = QComboBox()
        self.status_combo.addItems(["working", "planned", "closed"])
        form_layout.addRow("状態:", self.status_combo)
        
        # Days checkboxes
        days_group = QGroupBox("曜日")
        days_layout = QHBoxLayout()
        
        self.day_checkboxes = {}
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Free"]:
            checkbox = QCheckBox(day)
            days_layout.addWidget(checkbox)
            self.day_checkboxes[day] = checkbox
        
        days_group.setLayout(days_layout)
        form_layout.addRow(days_group)
        
        # Tags dropdown
        self.tags_combo = QComboBox()
        self.tags_combo.addItems(self.tags)
        form_layout.addRow("タグ:", self.tags_combo)
        
        # Task details
        self.details_edit = QTextEdit()
        form_layout.addRow("タスク詳細:", self.details_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setMinimumWidth(400)
    
    def populate_task_data(self):
        """Fill dialog with existing task data"""
        if not self.task:
            return
            
        self.name_edit.setText(self.task.name)
        self.status_combo.setCurrentText(self.task.status)
        
        # Set days checkboxes
        for day, checkbox in self.day_checkboxes.items():
            checkbox.setChecked(day in self.task.days)
        
        # Set tag if available
        if self.task.tags and self.task.tags[0] in self.tags:
            self.tags_combo.setCurrentText(self.task.tags[0])
            
        self.details_edit.setText(self.task.details)
    
    def get_selected_days(self):
        """Get list of selected days"""
        return [day for day, checkbox in self.day_checkboxes.items() if checkbox.isChecked()]
