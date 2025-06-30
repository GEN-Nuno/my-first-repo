from abc import ABC, abstractmethod

class TaskFilterStrategy(ABC):
    """Strategy interface for task filtering"""
    
    @abstractmethod
    def filter(self, tasks):
        pass

class TodayTasksFilter(TaskFilterStrategy):
    """Filter tasks scheduled for today"""
    
    def __init__(self, include_exceptions=False):
        self.include_exceptions = include_exceptions
    
    def filter(self, tasks):
        return [task for task in tasks if task.is_for_today(self.include_exceptions)]

class StatusTasksFilter(TaskFilterStrategy):
    """Filter tasks by status"""
    
    def __init__(self, status):
        self.status = status
    
    def filter(self, tasks):
        return [task for task in tasks if task.status == self.status]

class TimeCalculationStrategy(ABC):
    """Strategy interface for work time calculation"""
    
    @abstractmethod
    def calculate(self, tasks, total_work_time):
        pass

class ProportionalTimeCalculation(TimeCalculationStrategy):
    """Calculate work time proportionally to perceived effort"""
    
    def calculate(self, tasks, total_work_time):
        total_effort = sum(task.perceived_effort for task in tasks)
        if total_effort == 0:
            # Equal distribution if no effort specified
            per_task_time = total_work_time / len(tasks)
            for task in tasks:
                task.calculated_work_time = per_task_time
        else:
            # Proportional distribution
            for task in tasks:
                task.calculated_work_time = (task.perceived_effort / total_effort) * total_work_time
        
        return tasks
