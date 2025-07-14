from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class ErrorDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Erreur")
        self.setWindowModality(Qt.WindowModal)

        # Use an object name to allow specific styling via QSS
        self.setObjectName("ErrorDialog")

        layout = QVBoxLayout(self)

        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button, 0, Qt.AlignRight)

        # Apply some default styling that can be overridden by themes
        self.setStyleSheet("""
            #ErrorDialog {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
            }
            QLabel {
                color: #333333;
                font-size: 10pt;
            }
        """)
