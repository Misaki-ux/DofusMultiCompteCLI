from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from ui.keybind_button import KeybindButton

class StyledConfigRow(QFrame):
    """A styled row for the configuration grid with gradient background."""
    
    def __init__(self, label_text, shortcut_button, is_even_row=False, parent=None):
        super().__init__(parent)
        self.setObjectName("StyledConfigRow")
        
        # Set the frame style
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(20)
        
        # Create and style the label
        self.label = QLabel(label_text)
        self.label.setObjectName("ConfigRowLabel")
        self.label.setMinimumWidth(200)
        self.label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(shortcut_button)
        layout.addStretch()  # Push content to the left
        
        # Apply row-specific class for styling
        self.apply_row_class(is_even_row)
    
    def apply_row_class(self, is_even_row):
        """Apply CSS class based on row type."""
        if is_even_row:
            self.setProperty("rowType", "even")
        else:
            self.setProperty("rowType", "odd")

class StyledConfigGrid(QWidget):
    """A styled grid widget for configuration items with alternating row colors."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StyledConfigGrid")
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        
        # Header
        self.create_header()
        
        # Container for rows
        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(2)
        
        self.layout.addWidget(self.rows_container)
        
        # Store references to shortcut widgets
        self.shortcut_widgets = {}
    
    def create_header(self):
        """Create a styled header for the grid."""
        header_frame = QFrame()
        header_frame.setObjectName("ConfigGridHeader")
        header_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        header_frame.setLineWidth(2)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 10, 12, 10)
        header_layout.setSpacing(20)
        
        action_label = QLabel("Action")
        action_label.setObjectName("ConfigHeaderLabel")
        action_label.setMinimumWidth(200)
        action_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        shortcut_label = QLabel("Keyboard Shortcut")
        shortcut_label.setObjectName("ConfigHeaderLabel")
        shortcut_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        header_layout.addWidget(action_label)
        header_layout.addWidget(shortcut_label)
        header_layout.addStretch()
        
        self.layout.addWidget(header_frame)
    
    def add_shortcut_row(self, key, label_text, current_shortcut):
        """Add a styled row for a keyboard shortcut."""
        shortcut_button = KeybindButton(current_shortcut)
        shortcut_button.setMinimumWidth(150)
        shortcut_button.setMaximumWidth(200)
        
        # Store reference
        self.shortcut_widgets[key] = shortcut_button
        
        # Determine if this is an even row (for alternating colors)
        row_count = self.rows_layout.count()
        is_even_row = (row_count % 2) == 0
        
        # Create the styled row
        row = StyledConfigRow(label_text, shortcut_button, is_even_row)
        
        # Add to layout
        self.rows_layout.addWidget(row)
        
        return shortcut_button
    
    def get_shortcut_widgets(self):
        """Return the dictionary of shortcut widgets."""
        return self.shortcut_widgets

class StyledConfigSection(QFrame):
    """A styled section container for configuration elements."""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("StyledConfigSection")
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(1)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("ConfigSectionTitle")
        layout.addWidget(title_label)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content_widget)
    
    def add_content_widget(self, widget):
        """Add a widget to the content area."""
        self.content_layout.addWidget(widget)
