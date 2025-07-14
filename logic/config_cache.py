import win32gui
import win32process
import win32con
import win32api
from logic.config_manager import load_config
from logic.logger import logger
from logic.config_title_update import extract_character_name

def get_windows_in_z_order():
    windows = []
    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            windows.append(hwnd)
        return True
    win32gui.EnumWindows(enum_callback, None)
    return list(reversed(windows))

class WindowsCache:
    def __init__(self, config):
        self.config = config
        self.cache = []

    def is_relevant_window(self, hwnd):
        try:
            # Get window title
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return False
            
            # Check if window belongs to Dofus or WindowsDofusCLI process
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
                proc_name = win32process.GetModuleFileNameEx(handle, 0)
                win32api.CloseHandle(handle)
                
                # Check if process name matches Dofus or WindowsDofusCLI
                if "dofus" not in proc_name.lower() and "windowsdofuscli" not in proc_name.lower():
                    return False
            except Exception:
                # If we can't get process info, check title as fallback
                if "Dofus -" not in title:
                    return False
            
            # Use extract_character_name to positively identify Dofus windows
            char_name, char_class, version = extract_character_name(title)
            if char_name is None and char_class is None and version is None:
                logger.info(f"Checking window: '{title}'")
                logger.info(f"  -> Rejected: Not a recognized Dofus window title format.")
                return False

            exclude = self.config.get("exclude_programs", [])
            for e in exclude:
                if e and e.lower() in title.lower():
                    logger.info(f"Checking window: '{title}'")
                    logger.info(f"  -> Rejected: Excluded by rule '{e}'.")
                    return False
                    
            logger.info(f"Checking window: '{title}'")
            logger.info(f"  -> Accepted: '{title}'")
            return True
        except Exception as e:
            logger.error(f"Error checking window: {e}")
            return False

    def update(self):
        all_windows = get_windows_in_z_order()
        self.cache = []
        for hwnd in all_windows:
            if self.is_relevant_window(hwnd):
                title = win32gui.GetWindowText(hwnd)
                char_name, char_class, version = extract_character_name(title)
                self.cache.append({
                    "hwnd": hwnd,
                    "title": title,
                    "char_name": char_name,
                    "char_class": char_class,
                    "version": version
                })

    def get_cache(self):
        return self.cache

    def get_titles(self):
        return [win32gui.GetWindowText(hwnd) for hwnd in self.cache]

    def is_dofus_window_active(self):
        """Check if any Dofus window or Dofus Multi Compte window is active."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return False
                
            # Get window title and process name
            title = win32gui.GetWindowText(hwnd)
            process_id = win32process.GetWindowThreadProcessId(hwnd)[1]
            process_name = win32process.GetModuleFileNameEx(win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, process_id))
            
            # Check if it's a Dofus window
            if "dofus" in process_name.lower() or "windowsdofuscli" in process_name.lower():
                return True
                
            # Check if it's our main window
            if "Dofus Multi Compte" in title:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking active window: {e}")
            return False
