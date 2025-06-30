from abc import ABC, abstractmethod
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt

class AbstractThemeFactory(ABC):
    """Abstract factory interface for creating theme components"""
    
    @abstractmethod
    def create_color_scheme(self):
        """Create color scheme for the theme"""
        pass
    
    @abstractmethod
    def create_font_scheme(self):
        """Create font scheme for the theme"""
        pass
    
    @abstractmethod
    def create_style_sheet(self):
        """Create stylesheet for the theme"""
        pass
    
    @staticmethod
    def create_theme_factory(theme_name):
        """Factory method to create appropriate theme factory"""
        themes = {
            "light": LightThemeFactory,
            "dark": DarkThemeFactory
        }
        return themes.get(theme_name, LightThemeFactory)()

class LightThemeFactory(AbstractThemeFactory):
    """Concrete factory for light theme"""
    
    def create_color_scheme(self):
        return {
            "background": QColor(240, 240, 240),
            "foreground": QColor(50, 50, 50),
            "primary": QColor(66, 133, 244),
            "secondary": QColor(234, 234, 234),
            "accent": QColor(255, 152, 0),
            "error": QColor(219, 68, 55),
            "success": QColor(15, 157, 88),
            "working": QColor(255, 193, 7),
            "planned": QColor(33, 150, 243),
            "closed": QColor(76, 175, 80)
        }
    
    def create_font_scheme(self):
        header_font = QFont("Segoe UI", 12, QFont.Bold)
        normal_font = QFont("Segoe UI", 10)
        button_font = QFont("Segoe UI", 10, QFont.Medium)
        
        return {
            "header": header_font,
            "normal": normal_font,
            "button": button_font
        }
    
    def create_style_sheet(self):
        return """
            QMainWindow, QDialog {
                background-color: #F0F0F0;
            }
            
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            
            QPushButton:hover {
                background-color: #5294FF;
            }
            
            QPushButton:pressed {
                background-color: #3275E4;
            }
            
            QLabel {
                color: #323232;
            }
            
            QComboBox, QLineEdit, QSpinBox {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 4px;
                background-color: white;
            }
            
            QTableView, QTreeView, QListView {
                border: 1px solid #CCCCCC;
                background-color: white;
            }
            
            QHeaderView::section {
                background-color: #EAEAEA;
                padding: 4px;
                border: 1px solid #CCCCCC;
                font-weight: bold;
            }
        """

class DarkThemeFactory(AbstractThemeFactory):
    """Concrete factory for dark theme"""
    
    def create_color_scheme(self):
        return {
            "background": QColor(40, 40, 40),
            "foreground": QColor(220, 220, 220),
            "primary": QColor(66, 133, 244),
            "secondary": QColor(60, 60, 60),
            "accent": QColor(255, 152, 0),
            "error": QColor(219, 68, 55),
            "success": QColor(15, 157, 88),
            "working": QColor(255, 193, 7),
            "planned": QColor(33, 150, 243),
            "closed": QColor(76, 175, 80)
        }
    
    def create_font_scheme(self):
        header_font = QFont("Segoe UI", 12, QFont.Bold)
        normal_font = QFont("Segoe UI", 10)
        button_font = QFont("Segoe UI", 10, QFont.Medium)
        
        return {
            "header": header_font,
            "normal": normal_font,
            "button": button_font
        }
    
    def create_style_sheet(self):
        return """
            QMainWindow, QDialog {
                background-color: #282828;
            }
            
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            
            QPushButton:hover {
                background-color: #5294FF;
            }
            
            QPushButton:pressed {
                background-color: #3275E4;
            }
            
            QLabel {
                color: #DCDCDC;
            }
            
            QComboBox, QLineEdit, QSpinBox {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px;
                background-color: #404040;
                color: #DCDCDC;
            }
            
            QTableView, QTreeView, QListView {
                border: 1px solid #555555;
                background-color: #404040;
                color: #DCDCDC;
            }
            
            QHeaderView::section {
                background-color: #383838;
                padding: 4px;
                border: 1px solid #555555;
                font-weight: bold;
                color: #DCDCDC;
            }
        """
