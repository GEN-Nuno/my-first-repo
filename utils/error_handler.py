"""
Centralized error handling and logging
"""
import os
import sys
import logging
import traceback
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox

from .config import LOG_DIR

class ErrorHandler:
    """Centralized error handling and logging system"""
    
    @classmethod
    def setup_logging(cls):
        """Set up logging configuration"""
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        log_file = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Log app startup
        logging.info("Application started")
        return logging.getLogger()
    
    @staticmethod
    def handle_error(exception, show_ui=True, parent=None, title="Error"):
        """Handle exceptions with optional UI notification"""
        error_msg = str(exception)
        
        # Log the error with traceback
        logging.error(f"Error occurred: {error_msg}", exc_info=True)
        
        # Display UI error if requested
        if show_ui and parent:
            QMessageBox.critical(parent, title, f"An error occurred: {error_msg}")
    
    @staticmethod
    def log_info(message):
        """Log informational message"""
        logging.info(message)
    
    @staticmethod
    def log_warning(message):
        """Log warning message"""
        logging.warning(message)
