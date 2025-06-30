from abc import ABC, abstractmethod

class Command(ABC):
    """Command interface"""
    
    @abstractmethod
    def execute(self):
        pass

class OpenViewCommand(Command):
    """Command to open a specific view"""
    
    def __init__(self, controller, view_method):
        self.controller = controller
        self.view_method = view_method
    
    def execute(self):
        getattr(self.controller, self.view_method)()

class TaskCommand(Command):
    """Base command for task operations"""
    
    def __init__(self, controller):
        self.controller = controller

class AddTaskCommand(TaskCommand):
    """Command to add a task"""
    
    def __init__(self, controller, task):
        super().__init__(controller)
        self.task = task
    
    def execute(self):
        self.controller.add_task(self.task)

class DeleteTaskCommand(TaskCommand):
    """Command to delete a task"""
    
    def __init__(self, controller, task):
        super().__init__(controller)
        self.task = task
    
    def execute(self):
        self.controller.delete_task(self.task)

class SaveTasksCommand(TaskCommand):
    """Command to save tasks"""
    
    def execute(self):
        self.controller.save_tasks()
