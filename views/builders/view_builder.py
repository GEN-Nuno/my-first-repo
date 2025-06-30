from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QMainWindow

class ViewBuilder(ABC):
    """Abstract builder interface for views"""
    
    def __init__(self, theme_factory):
        self.theme_factory = theme_factory
        self.view = None
    
    @abstractmethod
    def create_view(self):
        """Create the base view"""
        pass
    
    @abstractmethod
    def build_header(self):
        """Build the header section"""
        pass
    
    @abstractmethod
    def build_content(self):
        """Build the main content section"""
        pass
    
    @abstractmethod
    def build_footer(self):
        """Build the footer section"""
        pass
    
    def get_result(self):
        """Return the built view"""
        return self.view

class MainViewBuilder(ViewBuilder):
    """Concrete builder for main view"""
    
    def create_view(self):
        """Create the base main view"""
        from views.main_view import MainView
        self.view = MainView(self.theme_factory)
    
    def build_header(self):
        """Build the header section with navigation buttons"""
        self.view.build_header()
    
    def build_content(self):
        """Build the main content section with today's tasks"""
        self.view.build_content()
    
    def build_footer(self):
        """Build the footer section with action buttons"""
        self.view.build_footer()

class TodayTaskViewBuilder(ViewBuilder):
    """Concrete builder for today's task view"""
    
    def create_view(self):
        """Create the base today task view"""
        from views.today_task_view import TodayTaskView
        self.view = TodayTaskView(self.theme_factory)
    
    def build_header(self):
        """Build the header section"""
        self.view.build_header()
    
    def build_content(self):
        """Build the task list content"""
        self.view.build_content()
    
    def build_footer(self):
        """Build the action buttons"""
        self.view.build_footer()

class AllScheduleViewBuilder(ViewBuilder):
    """Concrete builder for all schedule view"""
    
    def create_view(self):
        """Create the base all schedule view"""
        from views.all_schedule_view import AllScheduleView
        self.view = AllScheduleView(self.theme_factory)
    
    def build_header(self):
        """Build the header section"""
        self.view.build_header()
    
    def build_content(self):
        """Build the schedule content"""
        self.view.build_content()
    
    def build_footer(self):
        """Build the action buttons"""
        self.view.build_footer()

class Director:
    """Director that constructs views using builders"""
    
    def __init__(self, builder):
        self.builder = builder
    
    def construct(self):
        """Construct the complete view"""
        self.builder.create_view()
        self.builder.build_header()
        self.builder.build_content()
        self.builder.build_footer()
        return self.builder.get_result()
