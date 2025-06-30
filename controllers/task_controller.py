from patterns.command import Command
from patterns.strategy import TaskFilterStrategy, TodayTasksFilter
from models.task_model import Task
from patterns.state import StateContext
from PyQt5.QtWidgets import QMessageBox
import datetime

class TaskController:
    """Controller for task-related operations"""
    
    def __init__(self, model):
        self.model = model
        self.current_filter_strategy = TodayTasksFilter()
    
    def set_filter_strategy(self, strategy):
        """Set the strategy for filtering tasks"""
        if not isinstance(strategy, TaskFilterStrategy):
            raise TypeError("Strategy must be a TaskFilterStrategy")
        
        self.current_filter_strategy = strategy
    
    def get_filtered_tasks(self):
        """Get tasks filtered by the current strategy"""
        return self.current_filter_strategy.filter(self.model.tasks)
    
    def add_task(self, task):
        """Add a new task to the model"""
        self.model.add_task(task)
    
    def delete_task(self, task):
        """Remove a task from the model"""
        self.model.delete_task(task)
    
    def delete_closed_tasks(self):
        """Delete all closed tasks from the model"""
        self.model.delete_closed_tasks()
    
    def update_task(self, task, attributes):
        """Update task attributes"""
        for key, value in attributes.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # Handle state transitions if status changes
        if 'status' in attributes:
            # Update display properties based on new state
            state = StateContext.get_state_for_status(task.status)
            properties = state.get_display_properties()
            # The properties could be used to update UI elements
        
        self.model.notify()
        return True
    
    def save_tasks(self):
        """Save all tasks to configuration file"""
        self.model.save_tasks()
        return True
    
    def add_tag(self, tag):
        """Add a new tag"""
        self.model.add_tag(tag)
        self.model.save_tags()
    
    def delete_tag(self, tag):
        """Delete a tag"""
        self.model.delete_tag(tag)
        self.model.save_tags()
    
    def create_new_task(self, name="", status="planned", days=None, details="", tags=None):
        """Create a new task with the given attributes"""
        return Task(name=name, status=status, days=days if days else ["Free"], 
                    details=details, tags=tags if tags else [])
    
    def show_task_detail_view(self, task, parent=None):
        """Show a detail view for the given task"""
        from views.task_detail_view import TaskDetailView
        from views.builders.theme_factory import LightThemeFactory
        
        theme_factory = LightThemeFactory()
        detail_view = TaskDetailView(theme_factory, task, self)
        result = detail_view.exec_()
        
        # If the dialog was accepted, notify model observers
        if result == detail_view.Accepted:
            self.model.notify()
        
        return True

    def get_today_tasks(self, include_free=True, auto_add_only_today=False):
        """
        Get tasks for today, with options to filter
        
        Args:
            include_free: If True, include Free tasks in results
            auto_add_only_today: If True, only return tasks for today's day (for auto-adding)
        """
        today = datetime.datetime.now().strftime("%A")
        
        if auto_add_only_today:
            # For automatic addition, only get tasks scheduled specifically for today
            # Explicitly exclude Free tasks for auto-adding
            return [task for task in self.model.tasks if today in task.days and "Free" not in task.days]
        else:
            # Normal behavior - get today's tasks + optional Free tasks
            return self.model.get_today_tasks(include_free=include_free)
    
    def save_today_tasks(self, tasks):
        """Save today's tasks to configuration file"""
        # Ensure we have a valid task list
        if tasks is None:
            print("Error: No tasks provided to save_today_tasks")
            return False
            
        # Log tasks being saved
        task_names = [task.name for task in tasks]
        print(f"Saving today's tasks: {task_names}")
        
        # Save all provided tasks without filtering
        result = self.model.save_today_tasks(tasks)
        
        if result:
            # Make sure to save to the main task list too for consistency
            self.save_tasks()
            
            # Make sure the model notifies all observers of the change
            self.model.notify()
            
            return True
        else:
            print("Failed to save today's tasks")
            return False
    
    def get_all_tasks(self):
        """Get all tasks from the model"""
        return self.model.tasks.copy()
    
    def get_all_tags(self):
        """Get all tags from the model"""
        return self.model.tags.copy()
    
    def refresh_all_schedule_view(self, view):
        """Refresh the all schedule view with current model data"""
        if view:
            view.refresh_view(self.get_all_tasks(), self.get_all_tags())
    
    def refresh_today_task_view(self, view):
        """Refresh the today task view with current model data"""
        if not view:
            return
            
        # Get all tasks to ensure view has access to complete data
        all_tasks = self.model.tasks.copy()
        
        # Check if the view already has tasks
        if hasattr(view, 'tasks') and view.tasks:
            # Keep existing tasks
            current_tasks = view.tasks
            
            # Get auto-add tasks that should be added
            auto_tasks = self.get_today_tasks(include_free=False, auto_add_only_today=True)
            
            # Check for tasks to auto-add (that aren't already in the list)
            current_task_names = {task.name for task in current_tasks}
            for task in auto_tasks:
                if task.name not in current_task_names:
                    current_tasks.append(task)
            
            # Update view with both preserved and auto-added tasks
            view.all_tasks = all_tasks
            view.set_tasks(current_tasks)
        else:
            # No tasks yet, set auto-add tasks
            auto_tasks = self.get_today_tasks(include_free=False, auto_add_only_today=True)
            view.all_tasks = all_tasks
            view.set_tasks(auto_tasks)
        
        # Set tags and update dropdown
        view.set_tags(self.get_all_tags())
        if hasattr(view, 'update_task_selection_dropdown'):
            view.update_task_selection_dropdown()
