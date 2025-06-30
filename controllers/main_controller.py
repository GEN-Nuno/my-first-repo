from PyQt5.QtWidgets import QApplication, QMessageBox
import os
import sys
import traceback
import logging

from patterns.command import Command, OpenViewCommand
from patterns.observer import Observer
from views.builders.view_builder import Director, TodayTaskViewBuilder, AllScheduleViewBuilder
from views.builders.theme_factory import LightThemeFactory, DarkThemeFactory, AbstractThemeFactory
from controllers.task_controller import TaskController
from controllers.calculation_controller import CalculationController
from utils.error_handler import ErrorHandler
from utils.excel_exporter import ExcelExporter
from utils.config import UI_THEME  # Fixed import statement

class MainController(Observer):
    """Main controller for the scheduler application"""
    
    def __init__(self, model, view_builder):
        self.model = model
        self.model.attach(self)
        
        try:
            # Create main view
            director = Director(view_builder)
            self.main_view = director.construct()
            
            # Initialize sub-controllers
            self.task_controller = TaskController(model)
            self.calculation_controller = CalculationController(model)
            
            # Set the task controller in main view for task details
            self.main_view.set_task_detail_controller(self.task_controller)
            
            # Connect UI signals to commands
            self.connect_signals()
            
            # Initialize view with current data
            self.refresh_main_view()
        except Exception as e:
            ErrorHandler.handle_error(e)
            traceback.print_exc()
            QApplication.quit()
    
    def connect_signals(self):
        """Connect UI signals to commands"""
        # Main view buttons
        try:
            self.main_view.today_task_button.clicked.connect(
                lambda: OpenViewCommand(self, "show_today_task_view").execute()
            )
            self.main_view.all_schedule_button.clicked.connect(
                lambda: OpenViewCommand(self, "show_all_schedule_view").execute()
            )
            self.main_view.calculate_button.clicked.connect(
                lambda: OpenViewCommand(self, "show_calculation_view").execute()
            )
            if hasattr(self.main_view, 'excel_export_button'):
                self.main_view.excel_export_button.clicked.connect(
                    self.export_to_excel
                )
        except Exception as e:
            ErrorHandler.handle_error(e)
            traceback.print_exc()
    
    def update(self, subject):
        """Observer pattern update method - Controller receives model updates"""
        if subject == self.model:
            try:
                # Refresh main view
                self.refresh_main_view()
                
                # Also update any open subsidiary views
                if hasattr(self, '_all_schedule_view') and self._all_schedule_view.isVisible():
                    self.task_controller.refresh_all_schedule_view(self._all_schedule_view)
                    
                if hasattr(self, '_today_task_view') and self._today_task_view.isVisible():
                    self.task_controller.refresh_today_task_view(self._today_task_view)
                    
            except Exception as e:
                print(f"Error updating views: {e}")
                traceback.print_exc()
    
    def refresh_main_view(self):
        """Refresh the main view with current model data"""
        try:
            # Get today's tasks INCLUDING Free tasks - make sure we have the latest data
            today_tasks = self.model.get_today_tasks(include_free=True)
            
            # Pass tasks to the view for display
            self.main_view.refresh_view(today_tasks)
        except Exception as e:
            ErrorHandler.handle_error(e, True, self.main_view, "Refresh Error")
    
    def show_main_view(self):
        """Show the main application window"""
        self.main_view.show()
    
    def show_today_task_view(self):
        """Show the today's task view"""
        try:
            theme_factory = LightThemeFactory()
            builder = TodayTaskViewBuilder(theme_factory)
            director = Director(builder)
            view = director.construct()
            
            # Set up view with controller and data
            view.set_controller(self.task_controller)
            view.set_tags(self.model.tags)
            
            # Connect a signal when the dialog is accepted/closed
            view.finished.connect(lambda result: self.model.notify())
            
            # Store reference to prevent garbage collection
            self._today_task_view = view
            view.show()
        except Exception as e:
            QMessageBox.critical(self.main_view, "Error", f"Failed to open Today's Task view: {str(e)}")
            print(f"Error showing today task view: {e}")
            traceback.print_exc()
    
    def show_all_schedule_view(self):
        """Show the all schedule view"""
        try:
            theme_factory = LightThemeFactory()
            builder = AllScheduleViewBuilder(theme_factory)
            director = Director(builder)
            view = director.construct()
            
            # Set up view with controller and data through controller
            view.set_controller(self.task_controller)
            
            # Refresh view with data from the controller
            self.task_controller.refresh_all_schedule_view(view)
            
            # Connect to model updates
            # Store reference to the view for later refresh
            self._all_schedule_view = view
            
            # Show the view
            view.show()
        except Exception as e:
            QMessageBox.critical(self.main_view, "Error", f"Failed to open All Schedule view: {str(e)}")
            print(f"Error showing all schedule view: {e}")
            traceback.print_exc()
    
    def show_calculation_view(self):
        """Show the calculation view if all tasks are completed"""
        try:
            # Get today's tasks including Free tasks that have been manually added
            today_tasks = self.model.get_today_tasks(include_free=True)
            
            # Check if all tasks are completed
            if not today_tasks:
                self.main_view.show_error("本日のタスクがありません。")
                return
                
            if not all(task.completed_today for task in today_tasks):
                self.main_view.show_error("Not all tasks are completed for today!")
                return
            
            self.calculation_controller.show_calculation_view(today_tasks)
        except Exception as e:
            QMessageBox.critical(self.main_view, "Error", f"Failed to open Calculation view: {str(e)}")
            print(f"Error showing calculation view: {e}")
            traceback.print_exc()
    
    def export_to_excel(self):
        """Export tasks to Excel"""
        try:
            # Check if Excel export is available
            from utils.excel_exporter import ExcelExporter, EXCEL_AVAILABLE, MISSING_DEPENDENCIES
            
            if not EXCEL_AVAILABLE:
                missing = ", ".join(MISSING_DEPENDENCIES)
                QMessageBox.warning(
                    self.main_view,
                    "Missing Dependencies",
                    f"Excel export requires the following Python packages: {missing}\n\n"
                    f"Please install them using pip:\npip install {' '.join(MISSING_DEPENDENCIES)}"
                )
                return
            
            # Get all tasks
            tasks = self.model.tasks
            
            # Use excel exporter utility
            filename = ExcelExporter.export_tasks(tasks)
            
            if filename:
                QMessageBox.information(
                    self.main_view,
                    "Export Successful",
                    f"Tasks exported to:\n{filename}"
                )
            else:
                QMessageBox.critical(
                    self.main_view,
                    "Export Failed",
                    "Failed to export tasks. Check the logs for details."
                )
                
        except Exception as e:
            ErrorHandler.handle_error(e, True, self.main_view, "Export Error")
    
    def restart_application(self):
        """Restart the application to apply changes"""
        python = sys.executable
        os.execl(python, python, *sys.argv)
        python = sys.executable
        os.execl(python, python, *sys.argv)
