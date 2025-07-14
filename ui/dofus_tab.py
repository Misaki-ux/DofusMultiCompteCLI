from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QTabWidget
from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtGui import QIcon
import win32gui
import win32con
import win32api
from logic.config_title_update import extract_character_name

def find_tab_widget(widget):
    while widget is not None:
        if isinstance(widget, QTabWidget):
            return widget
        widget = widget.parentWidget()
    return None

class DofusTab(QWidget):
    duplicate_state_changed = Signal(str, bool)
    focus_main_window_requested = Signal(int)

    def __init__(self, window_info, config):
        super().__init__()
        self.setObjectName("DofusTab")
        self.hwnd = window_info["hwnd"]
        self.config = config
        self.title = window_info["title"]
        self.char_name = window_info.get("char_name")
        self.char_class = window_info.get("char_class")
        self.version = window_info.get("version")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.duplicate_click_checkbox = QCheckBox("Dupliquer ce clic")
        
        # Set initial state from config
        if self.char_name and self.char_name in self.config.get("duplicate_click_characters", []):
            self.duplicate_click_checkbox.setChecked(True)
            
        self.duplicate_click_checkbox.stateChanged.connect(self.on_checkbox_change)
        layout.addWidget(self.duplicate_click_checkbox)
        layout.addStretch()

        self.title_timer = QTimer()
        self.title_timer.timeout.connect(self.check_title_update)
        self.title_timer.start(3000)

    def on_checkbox_change(self, state):
        if self.char_name:
            self.duplicate_state_changed.emit(self.char_name, state == 2) # state is 2 for checked
        self.focus_main_window_requested.emit(self.hwnd)

    def get_offset(self):
        return self.duplicate_click_checkbox.height() + 5

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if win32gui.IsWindow(self.hwnd):
            offset = self.get_offset()
            screen_pos = self.mapToGlobal(self.rect().topLeft())
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, 
                                  screen_pos.x(), screen_pos.y() + offset, 
                                  self.width(), self.height() - offset, 
                                  win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW)

    def showEvent(self, event):
        super().showEvent(event)
        if win32gui.IsWindow(self.hwnd):
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
            self.resizeEvent(None) # Force resize
            win32gui.SetForegroundWindow(self.hwnd)

    def hideEvent(self, event):
        super().hideEvent(event)
        if win32gui.IsWindow(self.hwnd):
            win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)

    def close_window(self):
        try:
            win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
        except Exception as e:
            print(f"Erreur lors de la fermeture de la fenêtre {self.char_name}: {e}")

    def check_title_update(self):
        if not win32gui.IsWindow(self.hwnd):
            self.title_timer.stop()
            return
            
        current_title = win32gui.GetWindowText(self.hwnd)
        if current_title != self.title:
            self.title = current_title
            char_name, char_class, version = extract_character_name(current_title)

            if char_name != self.char_name:
                # If char name changes, we might need to update the config
                old_char_name = self.char_name
                self.char_name = char_name
                self.char_class = char_class
                self.version = version
                
                tab_widget = find_tab_widget(self)
                if tab_widget:
                    index = tab_widget.indexOf(self)
                    if index != -1:
                        tab_widget.setTabText(index, self.char_name or "Dofus")
                        tab_widget.setTabToolTip(index, f"{self.char_name or 'Dofus'} - {self.char_class or 'Classe inconnue'} - v{self.version or '???'}")
                        
                        # Update config if the checkbox was checked for the old name
                        if self.duplicate_click_checkbox.isChecked():
                            self.duplicate_state_changed.emit(old_char_name, False)
                            self.duplicate_state_changed.emit(self.char_name, True)

    def show_error_dialog(self, message):
        """Show an error dialog with the given message."""
        from ui.error_dialog import ErrorDialog
        dialog = ErrorDialog(message, self)
        dialog.exec()
