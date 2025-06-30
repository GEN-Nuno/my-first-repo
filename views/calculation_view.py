from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt

class CalculationView(QDialog):
    """View for calculating and displaying work time distribution"""
    
    def __init__(self, theme_factory, tasks, controller):
        super().__init__()
        self.theme_factory = theme_factory
        self.colors = theme_factory.create_color_scheme()
        self.fonts = theme_factory.create_font_scheme()
        self.setStyleSheet(theme_factory.create_style_sheet())
        
        self.tasks = tasks
        self.controller = controller
        
        self.setWindowTitle("Work Time Calculation")
        self.setMinimumSize(600, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components"""
        layout = QVBoxLayout(self)
        
        # Total work time input
        work_time_layout = QHBoxLayout()
        work_time_label = QLabel("Total Work Time (hours):")
        work_time_layout.addWidget(work_time_label)
        
        self.work_time_input = QDoubleSpinBox()
        self.work_time_input.setRange(0.5, 24.0)
        self.work_time_input.setValue(8.0)  # Default 8 hours
        self.work_time_input.setSingleStep(0.5)
        work_time_layout.addWidget(self.work_time_input)
        
        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate)
        work_time_layout.addWidget(calculate_button)
        
        layout.addLayout(work_time_layout)
        
        # Table for showing tasks and calculated time
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Task Name", "Perceived Effort", "Tags", "Calculated Hours"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.update_task_table()
        
        # Save button
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_results)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def update_task_table(self):
        """Update the task table with current task data"""
        self.table.setRowCount(len(self.tasks))
        
        for idx, task in enumerate(self.tasks):
            # Task name
            name_item = QTableWidgetItem(task.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(idx, 0, name_item)
            
            # Perceived effort
            effort_item = QTableWidgetItem(str(task.perceived_effort))
            effort_item.setFlags(effort_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(idx, 1, effort_item)
            
            # Tags
            tags_item = QTableWidgetItem(", ".join(task.tags))
            tags_item.setFlags(tags_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(idx, 2, tags_item)
            
            # Calculated time (initially empty)
            time_item = QTableWidgetItem("未計算")  # Changed to Japanese
            time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(idx, 3, time_item)
    
    def calculate(self):
        """Calculate work time distribution based on perceived effort"""
        total_work_time = self.work_time_input.value()
        
        try:
            # Check for valid input
            if total_work_time <= 0:
                QMessageBox.warning(self, "Warning", "Please enter a valid work time")
                return
                
            # Ensure there are tasks with perceived effort
            total_effort = sum(task.perceived_effort for task in self.tasks)
            
            if total_effort == 0:
                # If all tasks have 0 effort, distribute time equally
                equal_time = total_work_time / len(self.tasks)
                for task in self.tasks:
                    task.calculated_work_time = equal_time
            else:
                # Use the controller to perform calculation
                self.controller.calculate_work_time(self.tasks, total_work_time)
            
            # Update the table with calculated values
            for idx, task in enumerate(self.tasks):
                time_item = QTableWidgetItem(f"{task.calculated_work_time:.2f}")
                time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(idx, 3, time_item)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Calculation error: {str(e)}")
    
    def save_results(self):
        """Save the calculation results"""
        # Check if calculation has been performed
        if not all(hasattr(task, 'calculated_work_time') and task.calculated_work_time > 0 for task in self.tasks):
            QMessageBox.warning(self, "Warning", "Please calculate work time before saving.")
            return
        
        # Save the results
        if self.controller.save_work_time(self.tasks):
            QMessageBox.information(self, "Success", "Work time data saved successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save work time data.")
