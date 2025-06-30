from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QListWidget, QLineEdit, QLabel, QMessageBox)

class TagEditDialog(QDialog):
    """Dialog for editing tags"""
    
    def __init__(self, theme_factory, tags, controller):
        super().__init__()
        self.theme_factory = theme_factory
        self.colors = theme_factory.create_color_scheme()
        self.fonts = theme_factory.create_font_scheme()
        self.setStyleSheet(theme_factory.create_style_sheet())
        
        self.tags = tags.copy()
        self.controller = controller
        
        self.setWindowTitle("Edit Tags")
        self.setMinimumSize(350, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components"""
        layout = QVBoxLayout(self)
        
        # Instructions
        layout.addWidget(QLabel("Add or remove tags:"))
        
        # Tag list
        self.tag_list = QListWidget()
        self.tag_list.addItems(self.tags)
        layout.addWidget(self.tag_list)
        
        # Input area for new tag
        input_layout = QHBoxLayout()
        
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Enter new tag")
        input_layout.addWidget(self.tag_input)
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_tag)
        input_layout.addWidget(add_button)
        
        layout.addLayout(input_layout)
        
        # Delete selected tag
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_tag)
        layout.addWidget(delete_button)
        
        # Ok/Cancel buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.save_tags)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def add_tag(self):
        """Add a new tag"""
        new_tag = self.tag_input.text().strip()
        
        if not new_tag:
            return
            
        if new_tag in self.tags:
            QMessageBox.warning(self, "Warning", f"Tag '{new_tag}' already exists.")
            return
            
        self.tags.append(new_tag)
        self.tag_list.clear()
        self.tag_list.addItems(self.tags)
        self.tag_input.clear()
    
    def delete_tag(self):
        """Delete the selected tag"""
        selected_items = self.tag_list.selectedItems()
        
        if not selected_items:
            QMessageBox.information(self, "Information", "Please select a tag to delete.")
            return
            
        tag = selected_items[0].text()
        
        confirm = QMessageBox.question(
            self, "Confirm", f"Delete tag '{tag}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.tags.remove(tag)
            self.tag_list.clear()
            self.tag_list.addItems(self.tags)
    
    def save_tags(self):
        """Save the tags and close the dialog"""
        # Instead of directly accessing model.tags, use the controller methods
        current_tags = self.controller.get_all_tags()
        
        # Add new tags
        for tag in self.tags:
            if tag not in current_tags:
                self.controller.add_tag(tag)
                
        # Remove deleted tags
        for tag in current_tags:
            if tag not in self.tags:
                self.controller.delete_tag(tag)
    
        self.accept()
