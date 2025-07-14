from ui.main_window import launch_app
import sys
import os

# Add the parent directory of 'testGPT4' to sys.path
# This allows 'testGPT4' to be treated as a package when main.py is run directly.
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from ui.main_window import launch_app
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = launch_app(app, open_config=False)
    sys.exit(app.exec())
