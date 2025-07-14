from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeyEvent

class KeybindEdit(QLineEdit):
    key_sequence_changed = Signal(str)

    def __init__(self, initial_key_sequence="", parent=None):
        super().__init__(initial_key_sequence, parent)
        self.setPlaceholderText("Press a key combination...")
        self.setReadOnly(True)
        self.current_key_sequence = initial_key_sequence
        self.setText(self.current_key_sequence)

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

        self.current_key_sequence = new_sequence
        self.setText(self.current_key_sequence)
        self.key_sequence_changed.emit(self.current_key_sequence)
        event.accept()

    def key_to_string(self, key):
        # Handle special keys
        if key == Qt.Key.Key_Tab:
            return "Tab"
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
