import os
import subprocess
import time
import psutil

if os.name == 'nt':
    import ctypes
    user32 = ctypes.windll.user32

from config import UXPLAY_EXECUTABLE, UXPLAY_DIRECTORY

class IOSManager:
    def __init__(self):
        self.process = None
        self.hwnd = None
        self.is_popped_out = False

    def cleanup_orphans(self):
        """Hunts down and terminates any ghost UxPlay processes lingering in memory."""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.name() and 'uxplay' in proc.name().lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        time.sleep(0.5)

    def start_server(self):
        if self.process and self.process.poll() is None:
            self.stop_server()
            return False

        self.cleanup_orphans()

        c_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        exe_path = UXPLAY_EXECUTABLE if os.path.exists(UXPLAY_EXECUTABLE) else "uxplay"
        cwd = UXPLAY_DIRECTORY if os.path.exists(UXPLAY_DIRECTORY) else None
        cmd = [exe_path, "-n", "Morppy AirPlay Receiver"]
        try:
            self.process = subprocess.Popen(cmd, shell=False, cwd=cwd, creationflags=c_flags)
            self.is_popped_out = False
            self.hwnd = None
            return True
        except Exception as exc:
            print(f"Failed to start UxPlay: {exc}")
            return False

    def stop_server(self):
        if self.process:
            try:
                self.process.kill()
            except Exception:
                pass
        self.cleanup_orphans()
        self.process = None
        self.hwnd = None

    def bring_to_front(self):
        if os.name != 'nt':
            return False
        hwnd = user32.FindWindowW(None, "AirPlay Video Stream") or user32.FindWindowW(None, "UxPlay")
        if hwnd:
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
            return True
        return False
