import time
import win32api
import win32gui
import win32con
from PySide6.QtCore import QObject, Signal, QThread
from PySide6.QtWidgets import QApplication
from threading import Lock
from logic.logger import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.dofus_tab import DofusTab

class ClickWorker(QThread):
    error_occurred = Signal(str)

    def __init__(self, tabs, parent=None, click_callback=None):
        super().__init__(parent)
        self._running = False
        self.target_hwnds = []
        self.lock = Lock()
        self.last_click_time = 0
        self.tabs = tabs
        self.click_callback = click_callback  # <-- callback optionnel

    def update_target_windows(self, hwnds):
        with self.lock:
            self.target_hwnds = list(hwnds)
            logger.info(f"[Worker] Targets updated: {self.target_hwnds}")

    def stop(self):
        self._running = False
        logger.info("[Worker] Stopping...")
        self.wait()

    def run(self):
        self._running = True
        logger.info("[Worker] Starting...")
        while self._running:
            time.sleep(0.01)

            if not (win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000):
                continue

            now = time.time()
            if now - self.last_click_time < 0.5:
                continue

            pos = win32gui.GetCursorPos()
            hwnd = win32gui.WindowFromPoint(pos)

            hwnd_clicked = 0
            with self.lock:
                temp_hwnd = hwnd
                while temp_hwnd:
                    if temp_hwnd in self.target_hwnds:
                        hwnd_clicked = temp_hwnd
                        break
                    temp_hwnd = win32gui.GetParent(temp_hwnd)

            if hwnd_clicked == 0:
                continue

            logger.info(f"[✔] Click detected on window '{win32gui.GetWindowText(hwnd_clicked)}' (HWND: {hwnd_clicked})")

            try:
                # Si un callback est défini, on l’appelle et on ne fait PAS la réplication
                if self.click_callback:
                    self.click_callback(hwnd_clicked, pos)
                else:
                    # Sinon, comportement classique : réplication du clic sur autres onglets
                    client_pos = win32gui.ScreenToClient(hwnd_clicked, pos)
                    original_index = self.tabs.currentIndex()

                    with self.lock:
                        for target_hwnd in self.target_hwnds:
                            if target_hwnd == hwnd_clicked:
                                continue

                            target_tab_index = -1
                            for i in range(self.tabs.count()):
                                tab = self.tabs.widget(i)
                                if hasattr(tab, 'hwnd') and tab.hwnd == target_hwnd:
                                    target_tab_index = i
                                    break

                            if target_tab_index == -1:
                                logger.warning(f"No tab found for HWND {target_hwnd}")
                                continue

                            self.tabs.setCurrentIndex(target_tab_index)
                            QApplication.processEvents()
                            time.sleep(0.1)

                            try:
                                screen_pos = win32gui.ClientToScreen(target_hwnd, client_pos)
                                win32api.SetCursorPos(screen_pos)
                                time.sleep(0.02)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                time.sleep(0.02)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                logger.info(f"    -> Duplicated click on '{win32gui.GetWindowText(target_hwnd)}'")
                            except Exception as e:
                                error_msg = f"Error duplicating click on HWND {target_hwnd}: {e}"
                                logger.error(error_msg)
                                self.error_occurred.emit(error_msg)

                    self.tabs.setCurrentIndex(original_index)
                    QApplication.processEvents()

                    original_tab = self.tabs.widget(original_index)
                    if hasattr(original_tab, 'hwnd'):
                        try:
                            win32gui.SetForegroundWindow(original_tab.hwnd)
                        except Exception as e:
                            error_msg = f"Error restoring focus to original window: {e}"
                            logger.error(error_msg)
                            self.error_occurred.emit(error_msg)

                    win32api.SetCursorPos(pos)

            except Exception as e:
                error_msg = f"General error in click processing: {e}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)

            self.last_click_time = now
