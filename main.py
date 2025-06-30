import sys
from PyQt5.QtWidgets import QApplication, QMessageBox

from utils.config import UI_THEME
from utils.error_handler import ErrorHandler
from controllers.main_controller import MainController
from models.schedule_model import ScheduleModel
from views.builders.view_builder import MainViewBuilder
from views.builders.theme_factory import AbstractThemeFactory

def main():
    """Application entry point"""
    try:
        # Set up logging
        logger = ErrorHandler.setup_logging()
        
        app = QApplication(sys.argv)
        
        # Exception hook to catch unhandled exceptions
        def exception_hook(exctype, value, traceback):
            ErrorHandler.handle_error(value, True, None, "Unhandled Error")
            sys.__excepthook__(exctype, value, traceback)
        
        sys.excepthook = exception_hook
        
        # Initialize model
        model = ScheduleModel()
        
        # Set up view with builder and abstract factory patterns
        theme_factory = AbstractThemeFactory.create_theme_factory(UI_THEME)
        view_builder = MainViewBuilder(theme_factory)
        
        # Initialize controller
        controller = MainController(model, view_builder)
        
        # Show main window and start app
        controller.show_main_view()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        ErrorHandler.handle_error(e)
        
        # Show error in UI since we can't rely on controller at this point
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Startup Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
