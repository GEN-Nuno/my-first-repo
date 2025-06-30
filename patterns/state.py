from abc import ABC, abstractmethod
from patterns.strategy import StatusTasksFilter

class TaskState(ABC):
    """State interface for task states"""
    
    @abstractmethod
    def get_filter_strategy(self):
        """Return strategy for filtering tasks in this state"""
        pass
    
    @abstractmethod
    def get_next_state(self):
        """Return the next state in the workflow"""
        pass
    
    @abstractmethod
    def get_display_properties(self):
        """Return display properties for this state"""
        pass

class WorkingState(TaskState):
    """State representing a task in progress"""
    
    def get_filter_strategy(self):
        return StatusTasksFilter("working")
    
    def get_next_state(self):
        return ClosedState()
    
    def get_display_properties(self):
        return {
            "color": "#FFC107",  # Amber color for working tasks
            "editable": True,
            "priority": 1
        }

class PlannedState(TaskState):
    """State representing a planned task"""
    
    def get_filter_strategy(self):
        return StatusTasksFilter("planned")
    
    def get_next_state(self):
        return WorkingState()
    
    def get_display_properties(self):
        return {
            "color": "#2196F3",  # Blue color for planned tasks
            "editable": True,
            "priority": 2
        }

class ClosedState(TaskState):
    """State representing a completed task"""
    
    def get_filter_strategy(self):
        return StatusTasksFilter("closed")
    
    def get_next_state(self):
        return PlannedState()
    
    def get_display_properties(self):
        return {
            "color": "#4CAF50",  # Green color for closed tasks
            "editable": False,
            "priority": 3
        }

class StateContext:
    """Context for managing task states"""
    
    @staticmethod
    def get_state_for_status(status):
        """Factory method to get state based on status string"""
        states = {
            "working": WorkingState(),
            "planned": PlannedState(),
            "closed": ClosedState()
        }
        return states.get(status, PlannedState())
