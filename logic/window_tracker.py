import win32gui
import win32process

def get_dofus_windows(exclude_list):
    
    results = []

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd)
        if any(ex in title for ex in exclude_list):
            return
        if "Dofus" in title or "-" in title:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            results.append({
                "hwnd": hwnd,
                "title": title,
                "pid": pid,
                "rect": rect
            })

    win32gui.EnumWindows(callback, None)
    return results

def find_dofus_window_by_pid(pid):
        def callback(hwnd, hwnds):
            try:
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                    hwnds.append(hwnd)
            except:
                pass
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds[0] if hwnds else None