# Fixed focus_aware_hotkey_manager.py
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
                    logger.info(f"Hotkey pressed: {key_combo}")
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
                
        return just_pressed
    
    def parse_hotkey_string(self, hotkey_str):
        """Parse a hotkey string into a normalized format."""
        if not hotkey_str:
            return None
            
        # Normalize the input string
        hotkey_str = hotkey_str.strip()
        
        # Handle special case for Backtab -> convert to Shift+Tab
        if hotkey_str.lower() == "backtab":
            return "shift+tab"
        
        # Split by + and normalize each part
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
            ("switch_tab_left", "Shift+Tab", lambda: self.switch_tab_left.emit()),  # Default to Shift+Tab
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
        logger.info(f"Registered {len(self.hotkey_map)} focus-aware hotkeys: {list(self.hotkey_map.keys())}")
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'hotkey_timer'):
            self.hotkey_timer.stop()
        self.unregister_all_hotkeys()
        logger.info("Focus-aware hotkey manager cleaned up")


# Fixed hotkey_manager.py
import win32gui
import win32con
import win32api
from PySide6.QtCore import QObject, QTimer, Signal
from logic.logger import logger
import threading
import ctypes
from ctypes import wintypes
from logic.config_cache import WindowsCache
from logic.app_config import app_config

class HotkeyManager(QObject):
    """
    System-level hotkey manager using Win32 RegisterHotKey API.
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
        self.hwnd = None
        self.registered_hotkeys = {}
        self.hotkey_id_counter = 1000
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self.process_messages)
        self.message_timer.start(10)  # Check for messages every 10ms
        
        # Get configuration
        config = app_config.get_config()
        
        # Add WindowsCache instance with configuration
        self.windows_cache = WindowsCache(config)
        
        # Virtual key codes mapping
        self.vk_map = {
            'tab': win32con.VK_TAB,
            'f1': win32con.VK_F1,
            'f2': win32con.VK_F2,
            'f3': win32con.VK_F3,
            'f4': win32con.VK_F4,
            'f5': win32con.VK_F5,
            'f6': win32con.VK_F6,
            'f7': win32con.VK_F7,
            'f8': win32con.VK_F8,
            'f9': win32con.VK_F9,
            'f10': win32con.VK_F10,
            'f11': win32con.VK_F11,
            'f12': win32con.VK_F12,
        }
        
        # Modifier keys mapping
        self.mod_map = {
            'shift': win32con.MOD_SHIFT,
            'ctrl': win32con.MOD_CONTROL,
            'alt': win32con.MOD_ALT,
        }
        
        self.hotkey_callbacks = {}
        self.create_message_window()
        
    def create_message_window(self):
        """Create an invisible window to receive hotkey messages."""
        try:
            # Create a simple window class
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self.wnd_proc
            wc.lpszClassName = "HotkeyManagerWindow"
            wc.hInstance = win32api.GetModuleHandle(None)
            
            # Register the window class
            class_atom = win32gui.RegisterClass(wc)
            
            # Create the window
            self.hwnd = win32gui.CreateWindow(
                class_atom,
                "HotkeyManager",
                0,  # No style (invisible)
                0, 0, 0, 0,  # Position and size
                0,  # No parent
                0,  # No menu
                wc.hInstance,
                None
            )
            
            if self.hwnd:
                logger.info(f"Created hotkey message window: {self.hwnd}")
            else:
                logger.error("Failed to create hotkey message window")
                
        except Exception as e:
            logger.error(f"Error creating hotkey message window: {e}")
            
    def wnd_proc(self, hwnd, msg, wparam, lparam):
        """Window procedure to handle hotkey messages."""
        if msg == win32con.WM_HOTKEY:
            hotkey_id = wparam
            if hotkey_id in self.hotkey_callbacks:
                callback = self.hotkey_callbacks[hotkey_id]
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Error executing hotkey callback: {e}")
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    
    def process_messages(self):
        """Process Windows messages for hotkeys."""
        try:
            # Check for messages
            msg = win32gui.PeekMessage(self.hwnd, 0, 0, win32con.PM_REMOVE)
            if msg[0] != 0:
                win32gui.TranslateMessage(msg[1])
                win32gui.DispatchMessage(msg[1])
        except Exception as e:
            logger.error(f"Error processing hotkey message: {e}")
    
    def parse_hotkey_string(self, hotkey_str):
        """Parse a hotkey string like 'Shift+Tab' or 'F1' into modifiers and virtual key."""
        if not hotkey_str:
            return None, None
            
        # Handle special case for Backtab -> convert to Shift+Tab
        if hotkey_str.strip().lower() == "backtab":
            return win32con.MOD_SHIFT, win32con.VK_TAB
        
        parts = [part.strip().lower() for part in hotkey_str.split('+')]
        
        modifiers = 0
        vk = None
        
        for part in parts:
            if part in self.mod_map:
                modifiers |= self.mod_map[part]
            elif part in self.vk_map:
                vk = self.vk_map[part]
        
        return modifiers, vk
    
    def register_hotkey(self, hotkey_str, callback):
        """Register a system-level hotkey."""
        modifiers, vk = self.parse_hotkey_string(hotkey_str)
        
        if modifiers is None or vk is None:
            logger.error(f"Invalid hotkey string: {hotkey_str}")
            return False
            
        if not self.hwnd:
            logger.error("No message window available for hotkey registration")
            return False
            
        hotkey_id = self.hotkey_id_counter
        self.hotkey_id_counter += 1
        
        try:
            success = win32gui.RegisterHotKey(self.hwnd, hotkey_id, modifiers, vk)
            if success:
                self.registered_hotkeys[hotkey_str] = hotkey_id
                self.hotkey_callbacks[hotkey_id] = callback
                logger.info(f"Registered system hotkey: {hotkey_str} (ID: {hotkey_id})")
                return True
            else:
                # Try to get the last error to provide better debugging info
                error_code = win32api.GetLastError()
                if error_code == 1409:  # ERROR_HOTKEY_ALREADY_REGISTERED
                    logger.warning(f"Hotkey {hotkey_str} is already registered by another application")
                else:
                    logger.error(f"Failed to register hotkey {hotkey_str} (Error code: {error_code})")
                return False
        except Exception as e:
            logger.error(f"Error registering hotkey {hotkey_str}: {e}")
            return False
    
    def unregister_hotkey(self, hotkey_str):
        """Unregister a system-level hotkey."""
        if hotkey_str in self.registered_hotkeys:
            hotkey_id = self.registered_hotkeys[hotkey_str]
            try:
                win32gui.UnregisterHotKey(self.hwnd, hotkey_id)
                del self.registered_hotkeys[hotkey_str]
                del self.hotkey_callbacks[hotkey_id]
                logger.info(f"Unregistered hotkey: {hotkey_str}")
            except Exception as e:
                logger.error(f"Error unregistering hotkey {hotkey_str}: {e}")
    
    def unregister_all_hotkeys(self):
        """Unregister all hotkeys."""
        for hotkey_str in list(self.registered_hotkeys.keys()):
            self.unregister_hotkey(hotkey_str)
    
    def update_hotkeys(self, shortcuts_config):
        """Update all hotkeys based on new configuration."""
        # Unregister all existing hotkeys
        self.unregister_all_hotkeys()
        
        # Register new hotkeys
        hotkey_mappings = [
            ("switch_tab_right", "Tab", lambda: self.switch_tab_right.emit()),
            ("switch_tab_left", "Shift+Tab", lambda: self.switch_tab_left.emit()),  # Default to Shift+Tab
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
        """Clean up resources."""
        self.message_timer.stop()
        self.unregister_all_hotkeys()
        
        if self.hwnd:
            try:
                win32gui.DestroyWindow(self.hwnd)
                self.hwnd = None
            except Exception as e:
                logger.error(f"Error destroying hotkey window: {e}")


# Fixed low_level_hotkey_manager.py
import win32con
import win32api
import win32gui
import ctypes
from ctypes import wintypes
from PySide6.QtCore import QObject, QTimer, Signal
from logic.logger import logger
import threading
from logic.config_cache import WindowsCache
from logic.app_config import app_config

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
                return '+'.join(sorted(modifiers) + [main_key])
            else:
                return main_key
                
        return None
    
    def parse_hotkey_string(self, hotkey_str):
        """Parse a hotkey string into a normalized format."""
        if not hotkey_str:
            return None
            
        # Normalize the input string
        hotkey_str = hotkey_str.strip()
        
        # Handle special case for Backtab -> convert to Shift+Tab
        if hotkey_str.lower() == "backtab":
            return "shift+tab"
        
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
                return '+'.join(sorted(modifiers) + [main_key])
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
            ("switch_tab_left", "Shift+Tab", lambda: self.switch_tab_left.emit()),  # Default to Shift+Tab
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
        """Remove the keyboard hook and clean up."""
        if self.hook:
            try:
                ctypes.windll.user32.UnhookWindowsHookEx(self.hook)
                self.hook = None
                logger.info("Low-level keyboard hook removed successfully")
            except Exception as e:
                logger.error(f"Error removing low-level keyboard hook: {e}")
        self.unregister_all_hotkeys()
