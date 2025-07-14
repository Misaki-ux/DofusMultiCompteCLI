from PySide6.QtWidgets import QPushButton, QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeyEvent

class KeybindButton(QPushButton):
    key_sequence_changed = Signal(str)

    def __init__(self, initial_key_sequence="", parent=None):
        super().__init__(initial_key_sequence, parent)
        self.current_key_sequence = initial_key_sequence
        self.setText(self.current_key_sequence)
        self.clicked.connect(self._on_button_clicked)

    def _on_button_clicked(self):
        dialog = KeyCaptureDialog(self)
        if dialog.exec() == QDialog.Accepted:
            new_sequence = dialog.get_key_sequence()
            if new_sequence:
                self.current_key_sequence = new_sequence
                self.setText(self.current_key_sequence)
                self.key_sequence_changed.emit(self.current_key_sequence)

class KeyCaptureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Press New Shortcut")
        self.setModal(True)
        self.setFixedSize(350, 120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.label = QLabel("Press any key combination...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("KeyCaptureLabel")
        layout.addWidget(self.label)

        self.key_sequence = ""
        
        # Set object name for styling
        self.setObjectName("KeyCaptureDialog")

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        # Ignore modifier-only presses if no other key is pressed
        if key in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta]:
            event.ignore()
            return

        key_text = self.key_to_string(key)
        modifier_texts = []

        if modifiers & Qt.KeyboardModifier.ControlModifier:
            modifier_texts.append("Ctrl")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            modifier_texts.append("Shift")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            modifier_texts.append("Alt")
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            modifier_texts.append("Meta") # Windows key or Command key on Mac

        # Construct the key sequence string
        if key_text:
            new_sequence = "+".join(modifier_texts + [key_text])
        else:
            new_sequence = "+".join(modifier_texts) # Only modifiers, if a key_text wasn't found

        self.key_sequence = new_sequence
        self.label.setText(f"✅ New Shortcut: {self.key_sequence}")
        
        # Change object name for different styling state
        self.label.setObjectName("KeyCaptureLabelSuccess")
        
        # Close dialog after a short delay to show the feedback
        from PySide6.QtCore import QTimer
        QTimer.singleShot(800, self.accept)
        event.accept()

    def get_key_sequence(self):
        return self.key_sequence

    def key_to_string(self, key):
        # Handle special keys
        if key == Qt.Key.Key_Tab:
            return "Tab"
        elif key == Qt.Key.Key_Backtab:
            return "Backtab"
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            return "Enter"
        elif key == Qt.Key.Key_Space:
            return "Space"
        elif key == Qt.Key.Key_Escape:
            return "Esc"
        elif key == Qt.Key.Key_Backspace:
            return "Backspace"
        elif key == Qt.Key.Key_Delete:
            return "Del"
        elif key == Qt.Key.Key_F1: return "F1"
        elif key == Qt.Key.Key_F2: return "F2"
        elif key == Qt.Key.Key_F3: return "F3"
        elif key == Qt.Key.Key_F4: return "F4"
        elif key == Qt.Key.Key_F5: return "F5"
        elif key == Qt.Key.Key_F6: return "F6"
        elif key == Qt.Key.Key_F7: return "F7"
        elif key == Qt.Key.Key_F8: return "F8"
        # Add more special keys as needed

        # For regular keys, use the text representation
        return Qt.Key(key).name.replace("Key_", "")
