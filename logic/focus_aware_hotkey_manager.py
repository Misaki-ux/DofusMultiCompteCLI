import win32gui
import win32con
import win32api
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QApplication
from logic.logger import logger

class FocusAwareHotkeyManager(QObject):
    """
    A simpler hotkey manager that monitors focus and handles hotkeys accordingly.
    This works by monitoring the current focused window and handling hotkeys
    when appropriate windows are in focus.
    """
    
    # Signals for hotkey events
    switch_tab_right = Signal()
    switch_tab_left = Signal()
    focus_tab_1 = Signal()
    focus_tab_2 = Signal()
    focus_tab_3 = Signal()
    focus_tab_4 = Signal()
    focus_tab_5 = Signal()
    focus_tab_6 = Signal()
    focus_tab_7 = Signal()
    focus_tab_8 = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = QApplication.instance()
        self.main_window = parent
        self.shortcuts_config = {}
        self.dofus_hwnds = set()
        
        # Create a timer to check for hotkey presses
        self.hotkey_timer = QTimer()
        self.hotkey_timer.timeout.connect(self.check_hotkeys)
        self.hotkey_timer.start(50)  # Check every 50ms
        
        # Track key states
        self.key_states = {}
        self.last_key_states = {}
        
        # Virtual key codes
        self.vk_map = {
            'tab': 0x09,  # VK_TAB
            'backtab': 0x09,  # Same as tab, but with shift modifier
            'f1': 0x70,   # VK_F1
            'f2': 0x71,   # VK_F2
            'f3': 0x72,   # VK_F3
            'f4': 0x73,   # VK_F4
            'f5': 0x74,   # VK_F5
            'f6': 0x75,   # VK_F6
            'f7': 0x76,   # VK_F7
            'f8': 0x77,   # VK_F8
            'f9': 0x78,   # VK_F9
            'f10': 0x79,  # VK_F10
            'f11': 0x7A,  # VK_F11
            'f12': 0x7B,  # VK_F12
            'shift': 0x10,  # VK_SHIFT
            'ctrl': 0x11,   # VK_CONTROL
            'alt': 0x12,    # VK_MENU
        }
        
        self.hotkey_map = {}
        
    def set_dofus_windows(self, hwnds):
        """Set the list of Dofus window handles."""
        self.dofus_hwnds = set(hwnds)
        
    def should_handle_hotkeys(self):
        """Check if we should handle hotkeys based on current focus."""
        try:
            foreground_hwnd = win32gui.GetForegroundWindow()
            
            # Check if it's our main window
            if self.main_window and foreground_hwnd == int(self.main_window.winId()):
                return True
                
            # Check if it's one of our tracked Dofus windows
            if foreground_hwnd in self.dofus_hwnds:
                return True
                
            # Check if it's any Dofus window by title
            try:
                title = win32gui.GetWindowText(foreground_hwnd)
                if 'dofus' in title.lower():
                    return True
            except:
                pass
                
        except Exception as e:
            logger.debug(f"Error checking focus: {e}")
            
        return False
    
    def check_hotkeys(self):
        """Check for hotkey presses."""
        if not self.should_handle_hotkeys():
            return
            
        try:
            # Update key states
            self.last_key_states = self.key_states.copy()
            self.key_states = {}
            
            for key_name, vk_code in self.vk_map.items():
                self.key_states[key_name] = bool(win32api.GetAsyncKeyState(vk_code) & 0x8000)
            
            # Check for new key presses (key down events)
            for key_combo, callback in self.hotkey_map.items():
                if self.is_hotkey_pressed(key_combo):
                    print(f"🎯 HOTKEY: {key_combo}")  # Clean debug print
                    logger.debug(f"Hotkey pressed: {key_combo}")
                    try:
                        callback()
                    except Exception as e:
                        logger.error(f"Error executing hotkey callback: {e}")
                        
        except Exception as e:
            logger.debug(f"Error checking hotkeys: {e}")
    
    def is_hotkey_pressed(self, key_combo):
        """Check if a specific hotkey combination was just pressed."""
        keys = key_combo.split('+')
        
        # Check if all keys in the combination are currently pressed
        all_pressed = True
        for key in keys:
            if not self.key_states.get(key, False):
                all_pressed = False
                break
                
        if not all_pressed:
            return False
            
        # Check if at least one key was just pressed (transition from not pressed to pressed)
        just_pressed = False
        for key in keys:
            if self.key_states.get(key, False) and not self.last_key_states.get(key, False):
                just_pressed = True
                break
                
        # Remove debug print for cleaner output
                
        return just_pressed
    
    def parse_hotkey_string(self, hotkey_str):
        """Parse a hotkey string into a normalized format."""
        if not hotkey_str:
            return None
            
        # Normalize common variations
        hotkey_str = hotkey_str.replace("Backtab", "Tab")
        
        parts = [part.strip().lower() for part in hotkey_str.split('+')]
        
        # Normalize the order: modifiers first, then main key
        modifiers = []
        main_key = None
        
        for part in parts:
            if part in ['shift', 'ctrl', 'alt']:
                modifiers.append(part)
            elif part in self.vk_map:
                main_key = part
                
        if main_key:
            if modifiers:
                return '+'.join(sorted(modifiers) + [main_key])
            else:
                return main_key
                
        return None
    
    def register_hotkey(self, hotkey_str, callback):
        """Register a hotkey."""
        normalized_key = self.parse_hotkey_string(hotkey_str)
        if normalized_key:
            self.hotkey_map[normalized_key] = callback
            logger.info(f"Registered focus-aware hotkey: {hotkey_str} -> {normalized_key}")
            return True
        else:
            logger.error(f"Invalid hotkey string: {hotkey_str}")
            return False
    
    def unregister_hotkey(self, hotkey_str):
        """Unregister a hotkey."""
        normalized_key = self.parse_hotkey_string(hotkey_str)
        if normalized_key and normalized_key in self.hotkey_map:
            del self.hotkey_map[normalized_key]
            logger.info(f"Unregistered hotkey: {hotkey_str}")
    
    def unregister_all_hotkeys(self):
        """Unregister all hotkeys."""
        self.hotkey_map.clear()
        logger.info("Unregistered all focus-aware hotkeys")
    
    def update_hotkeys(self, shortcuts_config):
        """Update all hotkeys based on new configuration."""
        self.shortcuts_config = shortcuts_config
        
        # Unregister all existing hotkeys
        self.unregister_all_hotkeys()
        
        # Register new hotkeys
        hotkey_mappings = [
            ("switch_tab_right", "Tab", lambda: self.switch_tab_right.emit()),
            ("switch_tab_left", "Shift+Tab", lambda: self.switch_tab_left.emit()),
            ("focus_tab_1", "F1", lambda: self.focus_tab_1.emit()),
            ("focus_tab_2", "F2", lambda: self.focus_tab_2.emit()),
            ("focus_tab_3", "F3", lambda: self.focus_tab_3.emit()),
            ("focus_tab_4", "F4", lambda: self.focus_tab_4.emit()),
            ("focus_tab_5", "F5", lambda: self.focus_tab_5.emit()),
            ("focus_tab_6", "F6", lambda: self.focus_tab_6.emit()),
            ("focus_tab_7", "F7", lambda: self.focus_tab_7.emit()),
            ("focus_tab_8", "F8", lambda: self.focus_tab_8.emit()),
        ]
        
        for config_key, default_sequence, callback in hotkey_mappings:
            sequence = shortcuts_config.get(config_key, default_sequence)
            if sequence:
                self.register_hotkey(sequence, callback)
        
        # Debug: Show registered hotkeys
        print(f"DEBUG: Registered {len(self.hotkey_map)} focus-aware hotkeys: {list(self.hotkey_map.keys())}")
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'hotkey_timer'):
            self.hotkey_timer.stop()
        self.unregister_all_hotkeys()
        logger.info("Focus-aware hotkey manager cleaned up")