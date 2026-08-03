import os
import sys
import shutil

APP_NAME = "MorppyMirror"
APP_DATA_DIR = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser(r"~\AppData\Local")), APP_NAME)
os.makedirs(APP_DATA_DIR, exist_ok=True)

# Helper to resolve base directory whether running from script or PyInstaller frozen bundle
def get_base_dir():
    if hasattr(sys, '_MEIPASS'):
        return getattr(sys, '_MEIPASS')
    return os.path.abspath(os.path.dirname(__file__))

BASE_DIR = get_base_dir()

def discover_binary_directory(bin_name, subfolder_names):
    """Locates directory containing bin_name (e.g. scrcpy.exe, QtScrcpy.exe, uxplay.exe)."""
    env_key = f"{bin_name.upper()}_DIRECTORY"
    if os.getenv(env_key) and os.path.exists(os.getenv(env_key)):
        return os.getenv(env_key)

    for sub in subfolder_names:
        candidate = os.path.join(BASE_DIR, sub)
        if os.path.exists(os.path.join(candidate, f"{bin_name}.exe")) or os.path.exists(os.path.join(candidate, bin_name)):
            return candidate

    if os.path.exists(os.path.join(BASE_DIR, f"{bin_name}.exe")):
        return BASE_DIR

    which_path = shutil.which(bin_name) or shutil.which(f"{bin_name}.exe")
    if which_path:
        return os.path.dirname(which_path)

    return os.path.join(BASE_DIR, subfolder_names[0]) if subfolder_names else BASE_DIR

# --- SCRCPY PATHS ---
SCRCPY_DIRECTORY = discover_binary_directory("scrcpy", ["scrcpy-win64-v4.0", "tools/scrcpy", "scrcpy"])
SCRCPY_EXECUTABLE = os.path.join(SCRCPY_DIRECTORY, "scrcpy.exe")
if not os.path.exists(SCRCPY_EXECUTABLE):
    which_scrcpy = shutil.which("scrcpy") or shutil.which("scrcpy.exe")
    if which_scrcpy:
        SCRCPY_EXECUTABLE = which_scrcpy
        SCRCPY_DIRECTORY = os.path.dirname(which_scrcpy)

# --- QTSCRCPY PATHS ---
QTSCRCPY_DIRECTORY = discover_binary_directory("QtScrcpy", ["QtScrcpy", "tools/QtScrcpy"])
QTSCRCPY_EXECUTABLE = os.path.join(QTSCRCPY_DIRECTORY, "QtScrcpy.exe")
if not os.path.exists(QTSCRCPY_EXECUTABLE):
    which_qtscrcpy = shutil.which("QtScrcpy") or shutil.which("QtScrcpy.exe")
    if which_qtscrcpy:
        QTSCRCPY_EXECUTABLE = which_qtscrcpy
        QTSCRCPY_DIRECTORY = os.path.dirname(which_qtscrcpy)

# --- ADB PATHS ---
ADB_EXECUTABLE = os.path.join(SCRCPY_DIRECTORY, "adb.exe")
if not os.path.exists(ADB_EXECUTABLE):
    which_adb = shutil.which("adb") or shutil.which("adb.exe")
    if which_adb:
        ADB_EXECUTABLE = which_adb

# --- UXPLAY PATHS ---
UXPLAY_DIRECTORY = discover_binary_directory("uxplay", ["uxplay-windows", "tools/uxplay", "uxplay"])
UXPLAY_EXECUTABLE = os.path.join(UXPLAY_DIRECTORY, "uxplay.exe")
if not os.path.exists(UXPLAY_EXECUTABLE):
    which_uxplay = shutil.which("uxplay") or shutil.which("uxplay.exe")
    if which_uxplay:
        UXPLAY_EXECUTABLE = which_uxplay
        UXPLAY_DIRECTORY = os.path.dirname(which_uxplay)

# --- DATA FILES ---
SETTINGS_FILE = os.path.join(APP_DATA_DIR, "scrcpy_settings.json")
PRESETS_FILE = os.path.join(APP_DATA_DIR, "scrcpy_presets.json")
SESSION_LOG_FILE = os.path.join(APP_DATA_DIR, "scrcpy_session_log.txt")
SESSION_HISTORY_FILE = os.path.join(APP_DATA_DIR, "scrcpy_session_history.json")

# --- UI COLORS & STYLES ---
DARK_BG_PRIMARY = "#12181b"
DARK_BG_SECONDARY = "#1a2327"
ACCENT_CYAN = "#38bdf8"
ACCENT_GREEN = "#10b981"
ACCENT_PURPLE = "#8b5cf6"
TEXT_COLOR = "#f8fafc"

EXPONENTIAL_MOVING_AVERAGE_ALPHA = 0.15