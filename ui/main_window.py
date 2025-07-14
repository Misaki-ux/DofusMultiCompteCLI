import sys
import os
import win32gui
import win32process
import win32api
import win32con
from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QApplication, QMessageBox
from PySide6.QtCore import Qt, QSize, QTimer, QEvent
from PySide6.QtGui import QIcon
from ui.dofus_tab import DofusTab
from ui.error_dialog import ErrorDialog
from logic.config_title_update import extract_character_name
from logic.config_manager import load_config, save_config
from logic.app_config import app_config
from logic.config_widget import ConfigWidget
from logic.config_cache import WindowsCache
from logic.click_worker import ClickWorker
from logic.hotkey_manager import HotkeyManager
from logic.low_level_hotkey_manager import LowLevelHotkeyManager
from logic.focus_aware_hotkey_manager import FocusAwareHotkeyManager
from logic.logger import logger
import subprocess

def get_window_rect(hwnd):
    try:
        return win32gui.GetWindowRect(hwnd)
    except Exception:
        return (0, 0, 0, 0)

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Dofus Multi Compte")

        screen = self.app.primaryScreen()
        if screen:
            self.setGeometry(screen.availableGeometry())

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, '..', 'img', 'logo.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout()
        self.central_widget.setLayout(main_layout)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab_by_index)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.config_button = QPushButton()
        config_icon_path = os.path.join(script_dir, '..', 'img', 'config_icon.png')
        self.config_button.setIcon(QIcon(config_icon_path))
        self.config_button.setIconSize(QSize(16, 16))
        self.config_button.setFixedSize(24, 24)
        self.config_button.setToolTip("Configuration")
        self.config_button.setFlat(True)
        self.config_button.clicked.connect(self.show_config_tab)
        button_layout.addWidget(self.config_button)

        self.refresh_button = QPushButton()
        refresh_icon_path = os.path.join(script_dir, '..', 'img', 'refresh.png')
        self.refresh_button.setIcon(QIcon(refresh_icon_path))
        self.refresh_button.setIconSize(QSize(16, 16))
        self.refresh_button.setFixedSize(20, 20)
        self.refresh_button.setToolTip("Rafraîchir")
        self.refresh_button.setFlat(True)
        self.refresh_button.clicked.connect(self.refresh_tabs)
        button_layout.addWidget(self.refresh_button)

        self.quit_dofus_button = QPushButton()
        quit_icon_path = os.path.join(script_dir, '..', 'img', 'logo-close.png')
        self.quit_dofus_button.setIcon(QIcon(quit_icon_path))
        self.quit_dofus_button.setIconSize(QSize(24, 24))
        self.quit_dofus_button.setFixedSize(24, 24)
        self.quit_dofus_button.setToolTip("Quitter Dofus")
        self.quit_dofus_button.setFlat(True)
        self.quit_dofus_button.clicked.connect(self.quit_dofus_cli)
        button_layout.addWidget(self.quit_dofus_button)

        self.exit_app_button = QPushButton()
        close_app_icon_path = os.path.join(script_dir, '..', 'img', 'close_app.png')
        self.exit_app_button.setIcon(QIcon(close_app_icon_path))
        self.exit_app_button.setIconSize(QSize(24, 24))
        self.exit_app_button.setFixedSize(24, 24)
        self.exit_app_button.setToolTip("Quitter l'application")
        self.exit_app_button.setFlat(True)
        self.exit_app_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_app_button)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        self.tabs.setCornerWidget(button_widget, Qt.TopRightCorner)
        main_layout.addWidget(self.tabs)

        config = app_config.get_config()
        self.windows_cache = WindowsCache(config)
        self.windows_cache.update()

        self.setup_shortcuts()

        empty_widget = QWidget()
        empty_layout = QVBoxLayout()
        empty_layout.addStretch()
        empty_widget.setLayout(empty_layout)
        self.tabs.addTab(empty_widget, " ")

        theme = config.get('theme', 'purple')
        self.apply_theme(theme)

        self.click_worker = ClickWorker(self.tabs)
        self.click_worker.error_occurred.connect(self.show_error_dialog)
        self.click_worker.start()

        self.showMaximized()
        self.show()

    def handle_duplicate_state_changed(self, char_name, is_checked):
        checked_chars = app_config.get("duplicate_click_characters", [])
        if is_checked and char_name not in checked_chars:
            checked_chars.append(char_name)
        elif not is_checked and char_name in checked_chars:
            checked_chars.remove(char_name)

        app_config.set("duplicate_click_characters", checked_chars)
        save_config(app_config.get_config())
        self.update_worker_targets()
        self.update_focus_aware_windows()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        logger.info("Updating keyboard shortcuts...")
        
        # Get shortcuts configuration
        shortcuts_config = app_config.get("keyboard_shortcuts", {
            "switch_tab_right": "Tab",
            "switch_tab_left": "Shift+Tab",
            "focus_tab_1": "F1",
            "focus_tab_2": "F2",
            "focus_tab_3": "F3",
            "focus_tab_4": "F4",
            "focus_tab_5": "F5",
            "focus_tab_6": "F6",
            "focus_tab_7": "F7",
            "focus_tab_8": "F8"
        })
        
        # Initialize hotkey managers
        self.hotkey_manager = HotkeyManager(self)
        self.low_level_hotkey_manager = LowLevelHotkeyManager(self)
        self.focus_aware_hotkey_manager = FocusAwareHotkeyManager(self)
        
        # Connect signals to slots
        self.connect_hotkey_signals()
        
        # Update hotkeys for all managers
        self.update_all_hotkeys(shortcuts_config)
        
        # Set main window handle for low-level manager
        self.low_level_hotkey_manager.set_main_window_hwnd(int(self.winId()))
        
        logger.info("Keyboard shortcuts initialized successfully")

    def connect_hotkey_signals(self):
        """Connect hotkey signals to appropriate slots."""
        # System-level hotkeys
        self.hotkey_manager.switch_tab_right.connect(self.switch_to_next_tab)
        self.hotkey_manager.switch_tab_left.connect(self.switch_to_previous_tab)
        self.hotkey_manager.focus_tab_1.connect(lambda: self.bring_tab_to_front(0))
        self.hotkey_manager.focus_tab_2.connect(lambda: self.bring_tab_to_front(1))
        self.hotkey_manager.focus_tab_3.connect(lambda: self.bring_tab_to_front(2))
        self.hotkey_manager.focus_tab_4.connect(lambda: self.bring_tab_to_front(3))
        self.hotkey_manager.focus_tab_5.connect(lambda: self.bring_tab_to_front(4))
        self.hotkey_manager.focus_tab_6.connect(lambda: self.bring_tab_to_front(5))
        self.hotkey_manager.focus_tab_7.connect(lambda: self.bring_tab_to_front(6))
        self.hotkey_manager.focus_tab_8.connect(lambda: self.bring_tab_to_front(7))
        
        # Low-level hotkeys
        self.low_level_hotkey_manager.switch_tab_right.connect(self.switch_to_next_tab)
        self.low_level_hotkey_manager.switch_tab_left.connect(self.switch_to_previous_tab)
        self.low_level_hotkey_manager.focus_tab_1.connect(lambda: self.bring_tab_to_front(0))
        self.low_level_hotkey_manager.focus_tab_2.connect(lambda: self.bring_tab_to_front(1))
        self.low_level_hotkey_manager.focus_tab_3.connect(lambda: self.bring_tab_to_front(2))
        self.low_level_hotkey_manager.focus_tab_4.connect(lambda: self.bring_tab_to_front(3))
        self.low_level_hotkey_manager.focus_tab_5.connect(lambda: self.bring_tab_to_front(4))
        self.low_level_hotkey_manager.focus_tab_6.connect(lambda: self.bring_tab_to_front(5))
        self.low_level_hotkey_manager.focus_tab_7.connect(lambda: self.bring_tab_to_front(6))
        self.low_level_hotkey_manager.focus_tab_8.connect(lambda: self.bring_tab_to_front(7))
        
        # Focus-aware hotkeys
        self.focus_aware_hotkey_manager.switch_tab_right.connect(self.switch_to_next_tab)
        self.focus_aware_hotkey_manager.switch_tab_left.connect(self.switch_to_previous_tab)
        self.focus_aware_hotkey_manager.focus_tab_1.connect(lambda: self.bring_tab_to_front(0))
        self.focus_aware_hotkey_manager.focus_tab_2.connect(lambda: self.bring_tab_to_front(1))
        self.focus_aware_hotkey_manager.focus_tab_3.connect(lambda: self.bring_tab_to_front(2))
        self.focus_aware_hotkey_manager.focus_tab_4.connect(lambda: self.bring_tab_to_front(3))
        self.focus_aware_hotkey_manager.focus_tab_5.connect(lambda: self.bring_tab_to_front(4))
        self.focus_aware_hotkey_manager.focus_tab_6.connect(lambda: self.bring_tab_to_front(5))
        self.focus_aware_hotkey_manager.focus_tab_7.connect(lambda: self.bring_tab_to_front(6))
        self.focus_aware_hotkey_manager.focus_tab_8.connect(lambda: self.bring_tab_to_front(7))

    def update_all_hotkeys(self, shortcuts_config):
        """Update hotkeys for all managers."""
        try:
            # Update system-level hotkeys
            self.hotkey_manager.update_hotkeys(shortcuts_config)
            
            # Update low-level hotkeys
            self.low_level_hotkey_manager.update_hotkeys(shortcuts_config)
            
            # Update focus-aware hotkeys
            self.focus_aware_hotkey_manager.update_hotkeys(shortcuts_config)
            
            logger.info("Hotkeys updated successfully")
        except Exception as e:
            logger.error(f"Error updating hotkeys: {str(e)}")

    def show_error_dialog(self, message):
        dialog = ErrorDialog(message, self)
        dialog.exec()

    def apply_theme(self, theme_name):
        """Apply the selected theme to the application."""
        try:
            # Load QSS file
            theme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'themes', f'{theme_name}.qss')
            if os.path.exists(theme_path):
                with open(theme_path, 'r') as f:
                    qss = f.read()
                    
                # Apply QSS to application
                self.app.setStyleSheet(qss)
                
                # No need to update button styles separately since they're now in theme
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error applying theme: {str(e)}")
            logger.error(f"Error applying theme: {str(e)}")

    def update_button_styles(self):
        """Update button styles to match current theme."""
        # No need to update styles since they're now in theme
        pass

    def switch_to_next_tab(self):
        print("TAB PRESSED - GOING FORWARD")  # Debug print
        if self.tabs.count() > 0:
            current = self.tabs.currentIndex()
            new_index = (current + 1) % self.tabs.count()
            print(f"   {current} → {new_index}")  # Debug print
            print(f"   Current tab text: '{self.tabs.tabText(current)}'")
            print(f"   New tab text: '{self.tabs.tabText(new_index)}'")
            
            # Force the main window and tab widget to have focus
            self.setFocus()
            self.tabs.setFocus()
            self.tabs.setCurrentIndex(new_index)
            print(f"   Final tab text: '{self.tabs.tabText(self.tabs.currentIndex())}'")

    def switch_to_previous_tab(self):
        """Switch to the previous tab."""
        print("SHIFT+TAB PRESSED - GOING BACKWARD")
        if self.tabs.count() > 0:
            current = self.tabs.currentIndex()
            new_index = (current - 1) % self.tabs.count()  # Use modulo for rotation
            print(f"   {current} → {new_index}")
            print(f"   Current tab text: '{self.tabs.tabText(current)}'")
            print(f"   New tab text: '{self.tabs.tabText(new_index)}'")
            
            # Force the main window and tab widget to have focus
            self.setFocus()
            self.tabs.setFocus()
            self.tabs.setCurrentIndex(new_index)
            print(f"   Final tab text: '{self.tabs.tabText(self.tabs.currentIndex())}'")

    def ensure_main_window_focus(self):
        """Briefly ensure the main window has focus to process hotkey actions."""
        try:
            # Get the main window handle
            main_hwnd = int(self.winId())
            
            # Briefly bring main window to front without disrupting the user too much
            win32gui.SetWindowPos(main_hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
            win32gui.SetWindowPos(main_hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
        except Exception as e:
            logger.debug(f"Failed to temporarily adjust main window focus: {e}")

    def on_config_saved(self):
        load_config()
        self.update_shortcuts()

    def quit_dofus_cli(self):
        script_path = "F:/cours/My Ai/Gemini-CLI/gemini-cli/testGPT4/kill_dofus.ps1"
        try:
            subprocess.Popen(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path], shell=True)
            logger.info("Attempted to terminate Dofus processes.")
        except Exception as e:
            self.show_error_dialog(f"Error executing PowerShell script: {e}")

    def update_worker_targets(self):
        target_hwnds = []
        max_tabs = app_config.get("max_tabs", 8)
        for i in range(self.tabs.count()):
            if len(target_hwnds) >= max_tabs:
                break
            tab = self.tabs.widget(i)
            if isinstance(tab, DofusTab) and tab.duplicate_click_checkbox.isChecked():
                target_hwnds.append(tab.hwnd)
        self.click_worker.update_target_windows(target_hwnds)

    def update_focus_aware_windows(self):
        """Update the focus-aware hotkey manager with current Dofus windows."""
        dofus_hwnds = []
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if isinstance(tab, DofusTab):
                dofus_hwnds.append(tab.hwnd)
        
        if hasattr(self, 'focus_aware_hotkey_manager'):
            self.focus_aware_hotkey_manager.set_dofus_windows(dofus_hwnds)

    def handle_duplicate_state_changed(self, char_name, is_checked):
        checked_chars = app_config.get("duplicate_click_characters", [])
        if is_checked and char_name not in checked_chars:
            checked_chars.append(char_name)
        elif not is_checked and char_name in checked_chars:
            checked_chars.remove(char_name)
        
        app_config.set("duplicate_click_characters", checked_chars)
        save_config(app_config.get_config())
        self.update_worker_targets()
        self.update_focus_aware_windows()

    def on_tab_clicked(self, index):
        self.bring_tab_to_front(index)

    def on_tab_changed(self, index):
        self.bring_tab_to_front(index)

    def bring_tab_to_front(self, index):
        """Bring a specific tab to the front and ensure it has focus."""
        print(f"Focusing tab {index}...")
        
        if index < 0 or index >= self.tabs.count():
            print(f"Invalid tab index: {index}")
            return
            
        # Set the tab as current
        self.tabs.setCurrentIndex(index)
        print(f"Set current index to {index}")
        
        # Get the tab widget
        tab = self.tabs.widget(index)
        if tab and isinstance(tab, DofusTab):
            # Ensure the tab has focus
            tab.setFocus()
            print(f"Set focus to tab {index}")
            
            # Get the window handle
            hwnd = tab.hwnd
            if hwnd:
                try:
                    # Ensure the window is visible and on top
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    win32gui.SetForegroundWindow(hwnd)
                    print(f"Brought window {hwnd} to front")
                except Exception as e:
                    logger.error(f"Error bringing window to front: {e}")
        else:
            print(f"Tab {index} is not a DofusTab or has no hwnd")

    def get_window_info(self, hwnd):
        """Get window information from the WindowsCache."""
        try:
            window_info = self.windows_cache.get_window_info(hwnd)
            if window_info:
                # Get saved position from config
                saved_rect = app_config.get_window_position(hwnd)
                if saved_rect:
                    window_info['rect'] = saved_rect
                return window_info
            return None
        except Exception as e:
            logger.error(f"Error getting window info: {e}")
            return None

    
    def refresh_tabs(self):
        """Refresh the tabs by updating window positions and recreating tabs."""
        print("Refreshing tabs...")
        
        # Save current positions
        current_positions = {}
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if isinstance(tab, DofusTab):
                try:
                    hwnd = tab.hwnd
                    if hwnd:
                        rect = win32gui.GetWindowRect(hwnd)
                        if rect:
                            current_positions[str(hwnd)] = list(rect)
                            print(f"Saved position for window {hwnd}: {rect}")
                            
                            # Get window style
                            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                            # Remove any minimized/maximized flags
                            style &= ~(win32con.WS_MINIMIZE | win32con.WS_MAXIMIZE)
                            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
                            
                            # Ensure window is visible
                            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                            
                            # Save initial window state
                            if not hasattr(self, 'initial_window_states'):
                                self.initial_window_states = {}
                            self.initial_window_states[hwnd] = {
                                "style": style,
                                "ex_style": win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE),
                                "rect": rect,
                                "visible": style & win32con.WS_VISIBLE != 0
                            }
                            
                except Exception as e:
                    logger.error(f"Error saving window position: {e}")
        
        # Clear existing tabs
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        
        # Update cache and recreate tabs
        self.windows_cache.update()
        window_infos = self.windows_cache.get_cache()
        
        for info in window_infos:
            hwnd = info.get("hwnd")
            if hwnd:
                if hasattr(self, 'initial_window_states'):
                    initial_state = self.initial_window_states.get(hwnd)
                    if initial_state:
                        try:
                            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, initial_state["style"])
                            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, initial_state["ex_style"])
                            win32gui.MoveWindow(hwnd, *initial_state["rect"], True)
                            if initial_state["visible"]:
                                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                            else:
                                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                            print(f"Restored initial state for window {hwnd}")
                            continue
                        except Exception as e:
                            logger.error(f"Error restoring initial state for window {hwnd}: {e}")
                
                saved_rect = current_positions.get(str(hwnd))
                if saved_rect:
                    try:
                        win32gui.MoveWindow(hwnd, *saved_rect, True)
                        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                        style &= ~(win32con.WS_MINIMIZE | win32con.WS_MAXIMIZE)
                        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
                        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    except Exception as e:
                        logger.error(f"Error restoring window position: {e}")
                
                config = app_config.get_config()
                tab = DofusTab(info, config)
                title = extract_character_name(info.get("title", "Dofus"))[0]
                if not title:
                    title = "Dofus"
                self.tabs.addTab(tab, title)
                
                # Connect signals
                tab.duplicate_state_changed.connect(self.handle_duplicate_state_changed)
                tab.focus_main_window_requested.connect(self.ensure_main_window_focus)

        self.update_worker_targets()
        self.update_focus_aware_windows()

    def show_config_tab(self):
        """Show the configuration tab."""
        config_tab = None
        for i in range(self.tabs.count()):
            if isinstance(self.tabs.widget(i), ConfigWidget):
                config_tab = self.tabs.widget(i)
                break
        
        if config_tab is None:
            config_tab = ConfigWidget(app_config.get_config())
            config_tab.theme_changed.connect(self.apply_theme)
            config_tab.config_saved.connect(self.on_config_saved)
            self.tabs.addTab(config_tab, " Configuration")
        
        self.tabs.setCurrentWidget(config_tab)
    
    def on_config_saved(self):
        """Handle configuration save event."""
        # Update theme if changed
        config = app_config.get_config()
        theme = config.get('theme')
        if theme:
            self.apply_theme(theme)
        
        # Update shortcuts
        self.setup_shortcuts()

    def close_tab_by_index(self, index):
        print(f"Closing tab {index}")
        if self.tabs.count() > 1:  # Keep at least one tab
            tab = self.tabs.widget(index)
            if isinstance(tab, DofusTab):
                reply = QMessageBox.question(self, 'Confirmer la fermeture',
                                             f"Êtes-vous sûr de vouloir fermer l'onglet pour {tab.char_name or 'Dofus'}?\n"
                                             "Cela fermera également le client Dofus associé.",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    tab.close_window()
                    self.tabs.removeTab(index)
                    self.update_worker_targets()
                    self.update_focus_aware_windows()
            else:  # For config tab
                self.tabs.removeTab(index)
            print(f"Remaining tab count: {self.tabs.count()}")

    def closeEvent(self, event):
        """Save window positions and close all tabs before closing."""
        print("Saving window positions before closing...")
        
        # Save positions of all Dofus windows
        current_positions = {}
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if isinstance(tab, DofusTab):
                try:
                    hwnd = tab.hwnd
                    if hwnd:
                        rect = win32gui.GetWindowRect(hwnd)
                        if rect:
                            current_positions[str(hwnd)] = list(rect)  # Convert hwnd to string
                            print(f"Saved position for window {hwnd}: {rect}")
                except Exception as e:
                    logger.error(f"Error saving window position: {e}")
        
        # Save positions to config
        config = app_config.get_config()
        config['window_positions'] = current_positions
        save_config(config)
        logger.info(f"Saved config: {config}")
        print("Configuration saved successfully.")
        
        # Close all tabs
        for i in reversed(range(self.tabs.count())):
            tab = self.tabs.widget(i)
            if isinstance(tab, DofusTab):
                tab.close_window()
            self.tabs.removeTab(i)
        
        # Clean up hotkey managers
        if hasattr(self, 'hotkey_manager'):
            self.hotkey_manager.cleanup()
        if hasattr(self, 'low_level_hotkey_manager'):
            self.low_level_hotkey_manager.cleanup()
        if hasattr(self, 'focus_aware_hotkey_manager'):
            self.focus_aware_hotkey_manager.cleanup()
        
        self.click_worker.stop()
        event.accept()
    
    def save_initial_window_states(self):
        """Save the initial state of all Dofus and WindowsDofusCLI windows."""
        try:
            self.initial_window_states = {}
            def get_windows_in_z_order():
              windows = []

              def enum_windows(hwnd, lParam):
                  if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                      windows.append(hwnd)
                  return True

              # Enumère les fenêtres de haut en bas (top-level windows)
              win32gui.EnumWindows(enum_windows, None)

              # EnumWindows retourne dans l'ordre Z de bas en haut, on inverse donc pour avoir top en premier
              windows.reverse()
              return windows
            # Get all Dofus and WindowsDofusCLI windows
            all_windows = get_windows_in_z_order()
            for hwnd in all_windows:
                try:
                    # Get window title and process name
                    title = win32gui.GetWindowText(hwnd)
                    process_id = win32process.GetWindowThreadProcessId(hwnd)[1]
                    process_name = win32process.GetModuleFileNameEx(
                        win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, process_id)
                    )
                    
                    # Check if it's a Dofus or WindowsDofusCLI window
                    if "dofus" in process_name.lower() or "windowsdofuscli" in process_name.lower():
                        # Save window state
                        self.initial_window_states[hwnd] = {
                            "rect": win32gui.GetWindowRect(hwnd),
                            "style": win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE),
                            "ex_style": win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE),
                            "title": title,
                            "process_name": process_name
                        }
                        print(f"Saved initial state for window {hwnd}")
                        
                except Exception as e:
                    logger.error(f"Error saving initial state for window {hwnd}: {e}")
                    
        except Exception as e:
            logger.error(f"Error saving initial window states: {e}")

    def restore_initial_window_states(self):
        """Restore the initial state of all Dofus and WindowsDofusCLI windows."""
        if not hasattr(self, 'initial_window_states'):
            return
            
        try:
            for hwnd, state in self.initial_window_states.items():
                try:
                    # Restore window style and position
                    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, state["style"])
                    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, state["ex_style"])
                    win32gui.MoveWindow(hwnd, *state["rect"], True)
                    
                    # Show window if it was visible
                    if state["style"] & win32con.WS_VISIBLE:
                        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    else:
                        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                        
                    print(f"Restored initial state for window {hwnd}")
                    
                except Exception as e:
                    logger.error(f"Error restoring initial state for window {hwnd}: {e}")
                    
        except Exception as e:
            logger.error(f"Error restoring initial window states: {e}")

def launch_app(app, open_config=True):
    """Launch the main application window."""
    window = MainWindow(app)
    window.show()
    return window
