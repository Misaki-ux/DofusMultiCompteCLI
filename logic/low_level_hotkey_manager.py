import win32con
import win32api
import win32gui
import ctypes
from ctypes import wintypes
from PySide6.QtCore import QObject, QTimer, Signal
from logic.logger import logger
import threading
from logic.config_cache import WindowsCache  # Correction de l'import
from logic.app_config import app_config  # Import app_config

class LowLevelHotkeyManager(QObject):
    """
    Low-level keyboard hook manager that intercepts keys before they reach any application.
    This ensures hotkeys work even when game windows have focus.
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
        self.hook = None
        self.hotkey_map = {}
        self.pressed_keys = set()
        self.main_window_hwnd = None
        
        # Get configuration
        config = app_config.get_config()
        
        # Add WindowsCache instance with configuration
        self.windows_cache = WindowsCache(config)
        
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
        
        self.install_hook()
        
    def set_main_window_hwnd(self, hwnd):
        """Set the main window handle to check if it's focused."""
        self.main_window_hwnd = hwnd
        
    def install_hook(self):
        """Install the low-level keyboard hook."""
        try:
            # Define the hook procedure
            self.hook_proc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)(self.low_level_keyboard_proc)
            
            # Install the hook
            self.hook = ctypes.windll.user32.SetWindowsHookExW(
                win32con.WH_KEYBOARD_LL,
                self.hook_proc,
                ctypes.windll.kernel32.GetModuleHandleW(None),
                0
            )
            
            if self.hook:
                logger.info("Low-level keyboard hook installed successfully")
            else:
                logger.error("Failed to install low-level keyboard hook")
                
        except Exception as e:
            logger.error(f"Error installing keyboard hook: {e}")
    
    def low_level_keyboard_proc(self, nCode, wParam, lParam):
        """Low-level keyboard hook procedure."""
        try:
            if nCode >= 0:
                # Get the keyboard data
                kbd_struct = ctypes.cast(lParam, ctypes.POINTER(self.KBDLLHOOKSTRUCT)).contents
                vk_code = kbd_struct.vkCode
                
                # Check if this is a key we're interested in
                if wParam == win32con.WM_KEYDOWN or wParam == win32con.WM_SYSKEYDOWN:
                    self.pressed_keys.add(vk_code)
                    
                    # Only handle hotkeys if a Dofus window or our main window is active
                    if not self.windows_cache.is_dofus_window_active():
                        return ctypes.windll.user32.CallNextHookEx(self.hook, nCode, wParam, lParam)
                        
                    # Check if we should handle this key combination
                    if self.should_intercept_key(vk_code):
                        # Handle the hotkey
                        if self.handle_hotkey(vk_code):
                            # Return 1 to prevent further processing
                            return 1
                
                elif wParam == win32con.WM_KEYUP or wParam == win32con.WM_SYSKEYUP:
                    self.pressed_keys.discard(vk_code)
                    
        except Exception as e:
            logger.error(f"Error in keyboard hook proc: {e}")
            
        return ctypes.windll.user32.CallNextHookEx(self.hook, nCode, wParam, lParam)
    
    def should_intercept_key(self, vk_code):
        """Check if we should intercept this key based on current state."""
        # Only intercept when the main window or a Dofus window is focused
        try:
            foreground_hwnd = win32gui.GetForegroundWindow()
            foreground_title = win32gui.GetWindowText(foreground_hwnd)
            
            # Check if it's our main window or a Dofus window
            if (self.main_window_hwnd and foreground_hwnd == self.main_window_hwnd) or \
               'dofus' in foreground_title.lower() or 'dofus multi compte' in foreground_title.lower():
                return True
                
        except Exception:
            pass
            
        return False
    
    def handle_hotkey(self, vk_code):
        """Handle a detected hotkey combination."""
        try:
            # Check current key combination
            key_combo = self.get_current_key_combination(vk_code)
            
            if key_combo in self.hotkey_map:
                callback = self.hotkey_map[key_combo]
                # Execute callback in the main thread
                callback()
                return True  # Intercept the key
                
        except Exception as e:
            logger.error(f"Error handling hotkey: {e}")
            
        return False  # Don't intercept
    
    def get_current_key_combination(self, vk_code):
        """Get the current key combination as a string."""
        modifiers = []
        
        # Check for modifier keys
        if 0x10 in self.pressed_keys:  # VK_SHIFT
            modifiers.append('shift')
        if 0x11 in self.pressed_keys:  # VK_CONTROL
            modifiers.append('ctrl')
        if 0x12 in self.pressed_keys:  # VK_MENU (Alt)
            modifiers.append('alt')
            
        # Get the main key name
        main_key = None
        for key_name, key_vk in self.vk_map.items():
            if key_vk == vk_code and key_name not in ['shift', 'ctrl', 'alt']:
                main_key = key_name
                break
                
        if main_key:
            if modifiers:
                return '+'.join(modifiers + [main_key])
            else:
                return main_key
                
        return None
    
    def parse_hotkey_string(self, hotkey_str):
        """Parse a hotkey string into a normalized format."""
        if not hotkey_str:
            return None
            
        # Normalize common variations
        hotkey_str = hotkey_str.strip().lower()
        
        # Special handling for Backtab vs Tab
        if hotkey_str == "backtab":
            return "shift+tab"
        elif hotkey_str == "tab":
            return "tab"
        
        # Handle other hotkeys
        parts = [part.strip().lower() for part in hotkey_str.split('+')]
        
        # Normalize the order: modifiers first, then main key
        modifiers = []
        main_key = None
        
        for part in parts:
            if part in ['shift', 'ctrl', 'alt']:
                modifiers.append(part)
            else:
                main_key = part
                break
        
        if main_key:
            if modifiers:
                return '+'.join(modifiers + [main_key])
            else:
                return main_key
                
        return None
    
    def register_hotkey(self, hotkey_str, callback):
        """Register a hotkey with the low-level hook."""
        normalized_key = self.parse_hotkey_string(hotkey_str)
        if normalized_key:
            self.hotkey_map[normalized_key] = callback
            logger.info(f"Registered low-level hotkey: {hotkey_str} -> {normalized_key}")
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
        logger.info("Unregistered all hotkeys")
    
    def update_hotkeys(self, shortcuts_config):
        """Update all hotkeys based on new configuration."""
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
    
    def cleanup(self):
        """Clean up the keyboard hook."""
        if self.hook:
            try:
                ctypes.windll.user32.UnhookWindowsHookEx(self.hook)
                self.hook = None
                logger.info("Low-level keyboard hook removed")
            except Exception as e:
                logger.error(f"Error removing keyboard hook: {e}")
    
    # Structure for low-level keyboard input
    class KBDLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [
            ("vkCode", wintypes.DWORD),
            ("scanCode", wintypes.DWORD),
            ("flags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
        ]