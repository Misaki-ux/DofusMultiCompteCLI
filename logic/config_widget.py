from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QComboBox, QSpinBox, QGridLayout, QScrollArea, QHBoxLayout
from PySide6.QtCore import Signal, Qt, QTimer
import json
import os
from logic.app_config import app_config
from logic.config_manager import save_config
from ui.keybind_button import KeybindButton # Import the new KeybindButton widget
from ui.styled_config_grid import StyledConfigGrid, StyledConfigSection

class ConfigWidget(QWidget):
    theme_changed = Signal(str)
    config_saved = Signal()

    def __init__(self, config):
        super().__init__()
        self.config = config or {}

        # Create scroll area for the entire config
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main content widget
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Set up the scroll area
        scroll_area.setWidget(content_widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        # Create sections
        self.create_theme_section()
        self.create_exclude_programs_section()
        self.create_refresh_interval_section()
        self.create_keyboard_shortcuts_section()
        self.create_save_section()

    def create_theme_section(self):
        """Create the theme selection section."""
        theme_section = StyledConfigSection("🎨 Thème de l'application")
        
        self.theme_combo = QComboBox()
        self.populate_themes()
        
        current_theme = self.config.get("theme", "dark")
        self.theme_combo.setCurrentText(current_theme)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        theme_section.add_content_widget(self.theme_combo)
        self.layout.addWidget(theme_section)

    def create_exclude_programs_section(self):
        """Create the exclude programs section."""
        exclude_section = StyledConfigSection("🚫 Programmes à exclure (un par ligne)")
        
        self.exclude_edit = QTextEdit()
        self.exclude_edit.setText("\n".join(self.config.get("exclude_programs", [])))
        self.exclude_edit.setMaximumHeight(100)
        
        exclude_section.add_content_widget(self.exclude_edit)
        self.layout.addWidget(exclude_section)

    def create_refresh_interval_section(self):
        """Create the refresh interval section."""
        refresh_section = StyledConfigSection("⏱️ Intervalle de rafraîchissement (secondes)")
        
        self.refresh_interval_spinbox = QSpinBox()
        self.refresh_interval_spinbox.setMinimum(1)
        self.refresh_interval_spinbox.setMaximum(60)
        self.refresh_interval_spinbox.setValue(self.config.get("refresh_interval", 5))
        self.refresh_interval_spinbox.setMaximumWidth(100)
        
        refresh_section.add_content_widget(self.refresh_interval_spinbox)
        self.layout.addWidget(refresh_section)

    def create_keyboard_shortcuts_section(self):
        """Create the styled keyboard shortcuts section."""
        shortcuts_section = StyledConfigSection("⌨️ Raccourcis clavier")
        
        # Create the styled grid
        self.shortcuts_grid = StyledConfigGrid()
        
        # Define default shortcuts with user-friendly labels and icons
        default_shortcuts = {
            "switch_tab_left": ("⬅️ Onglet précédent", "Shift+Tab"),
            "switch_tab_right": ("➡️ Onglet suivant", "Tab"),
            "focus_tab_1": ("1️⃣ Focuser onglet 1", "F1"),
            "focus_tab_2": ("2️⃣ Focuser onglet 2", "F2"),
            "focus_tab_3": ("3️⃣ Focuser onglet 3", "F3"),
            "focus_tab_4": ("4️⃣ Focuser onglet 4", "F4"),
            "focus_tab_5": ("5️⃣ Focuser onglet 5", "F5"),
            "focus_tab_6": ("6️⃣ Focuser onglet 6", "F6"),
            "focus_tab_7": ("7️⃣ Focuser onglet 7", "F7"),
            "focus_tab_8": ("8️⃣ Focuser onglet 8", "F8"),
        }
        
        # Use existing config values or fall back to defaults
        keyboard_shortcuts_config = self.config.get("keyboard_shortcuts", {})

        # Add rows to the grid
        for key, (label_text, default_shortcut) in default_shortcuts.items():
            current_shortcut = keyboard_shortcuts_config.get(key, default_shortcut)
            self.shortcuts_grid.add_shortcut_row(key, label_text, current_shortcut)
        
        # Get reference to shortcut widgets
        self.shortcut_edits = self.shortcuts_grid.get_shortcut_widgets()
        
        shortcuts_section.add_content_widget(self.shortcuts_grid)
        self.layout.addWidget(shortcuts_section)

    def create_save_section(self):
        """Create the save button section with feedback."""
        save_container = QWidget()
        save_layout = QVBoxLayout(save_container)
        save_layout.setSpacing(20)
        
        # Create a horizontal layout for the save button
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addStretch()
        
        # Save button
        self.save_button = QPushButton()
        self.save_button.setText("Sauvegarder la Configuration")
        self.save_button.clicked.connect(self.save_config_ui)
        self.save_button.setMinimumHeight(40)
        self.save_button.setMinimumWidth(200)
        
        # Force the button to use a specific font
        font = self.save_button.font()
        font.setPointSize(12)
        font.setBold(True)
        self.save_button.setFont(font)
        
        # Set a unique object name for styling
        self.save_button.setObjectName("SaveButton")
        
        button_layout.addWidget(self.save_button)
        
        # Status label for feedback
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(30)
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        
        save_layout.addWidget(button_container)
        save_layout.addWidget(self.status_label)
        
        self.layout.addWidget(save_container)
        
        # Timer for hiding status message
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.hide_status_message)

    def on_theme_changed(self, theme_name):
        self.theme_changed.emit(theme_name)
        app_config.set("theme", theme_name)
        save_config(app_config.get_config())


    def populate_themes(self):
      themes_dir = os.path.join(os.path.dirname(__file__), '..', 'themes')
      if os.path.exists(themes_dir):
          themes = [f for f in os.listdir(themes_dir) if f.endswith(".qss")]
          self.theme_combo.clear()
          for theme in themes:
              self.theme_combo.addItem(theme.replace(".qss", ""))

    def save_config_ui(self):
        # Step 1: Change button text immediately
        self.save_button.setText("Saving...")
        
        # Step 2: Save the config
        app_config.set("exclude_programs", self.exclude_edit.toPlainText().splitlines())
        selected_theme = self.theme_combo.currentText()
        app_config.set("theme", selected_theme)
        app_config.set("refresh_interval", self.refresh_interval_spinbox.value())

        updated_shortcuts = {}
        for key, edit_widget in self.shortcut_edits.items():
            updated_shortcuts[key] = edit_widget.current_key_sequence
        app_config.set("keyboard_shortcuts", updated_shortcuts)
        
        save_config(app_config.get_config())
        
        # Step 3: Show success
        self.save_button.setText("Saved!")
        
        # Step 4: Reset after 2 seconds
        QTimer.singleShot(2000, lambda: self.save_button.setText("Sauvegarder la Configuration"))
        
        self.theme_changed.emit(selected_theme)
        self.config_saved.emit()
    
    # reset_save_button method removed - using inline lambda instead
    
    def show_status_message(self, message, status_type="success"):
        """Show a status message with appropriate styling."""
        print(f"DEBUG: show_status_message called with: {message}")  # Debug print
        
        if not hasattr(self, 'status_label'):
            print("DEBUG: status_label does not exist!")
            return
            
        self.status_label.setText(message)
        
        # Set object name for theme-based styling
        if status_type == "success":
            self.status_label.setObjectName("StatusSuccess")
        else:  # error
            self.status_label.setObjectName("StatusError")
        
        self.status_label.show()
        print(f"DEBUG: status_label.isVisible(): {self.status_label.isVisible()}")
        
        # Force update
        self.status_label.update()
        self.update()
        
        # Hide message after 3 seconds
        if hasattr(self, 'status_timer'):
            self.status_timer.start(3000)
        else:
            print("DEBUG: status_timer does not exist!")
    
    def hide_status_message(self):
        """Hide the status message."""
        self.status_label.hide()
