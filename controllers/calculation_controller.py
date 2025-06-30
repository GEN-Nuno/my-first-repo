from patterns.strategy import ProportionalTimeCalculation
from views.calculation_view import CalculationView
from views.builders.theme_factory import LightThemeFactory
from datetime import datetime

class CalculationController:
    """Controller for handling work time calculations"""
    
    def __init__(self, model):
        self.model = model
        self.calculation_strategy = ProportionalTimeCalculation()
    
    def set_calculation_strategy(self, strategy):
        """Set the strategy used for calculations"""
        self.calculation_strategy = strategy
    
    def calculate_work_time(self, tasks, total_work_time):
        """Calculate work time for tasks based on the current strategy"""
        return self.calculation_strategy.calculate(tasks, total_work_time)
    
    def save_work_time(self, calculated_tasks):
        """Save calculated work time to configuration file"""
        try:
            result = self.model.save_work_time(calculated_tasks)
            # Notify observers after saving
            self.model.notify()
            return result
        except Exception as e:
            print(f"Error saving work time: {e}")
            return False
    
    def show_calculation_view(self, tasks):
        """Show the calculation view for the given tasks"""
        # Ensure all tasks have completed_today flag set to True
        if not all(task.completed_today for task in tasks):
            return False
        
        theme_factory = LightThemeFactory()
        view = CalculationView(theme_factory, tasks, self)
        view.exec_()  # Use exec_ to make it modal
        return True
