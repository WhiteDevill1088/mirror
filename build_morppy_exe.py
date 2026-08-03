import os
import sys
import shutil
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRCPY_BIN_DIR = os.path.join(PROJECT_ROOT, "scrcpy-win64-v4.0")
UXPLAY_BIN_DIR = os.path.join(PROJECT_ROOT, "uxplay-windows")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

def build_standalone_exe():
    print("==================================================")
    print(" BUILDING MORPPY MOBILE MIRROR SUITE (PyInstaller)")
    print("==================================================")

    datas = []

    # Include scrcpy-win64-v4.0 binaries & DLLs
    if os.path.exists(SCRCPY_BIN_DIR):
        print(f"Bundling Scrcpy 4.0 binaries from: {SCRCPY_BIN_DIR}")
        datas.append((SCRCPY_BIN_DIR, "scrcpy-win64-v4.0"))

    # Include uxplay-windows binaries & DLLs
    if os.path.exists(UXPLAY_BIN_DIR):
        print(f"Bundling UxPlay binaries from: {UXPLAY_BIN_DIR}")
        datas.append((UXPLAY_BIN_DIR, "uxplay-windows"))

    # Include assets directory
    if os.path.exists(ASSETS_DIR):
        print(f"Bundling assets from: {ASSETS_DIR}")
        datas.append((ASSETS_DIR, "assets"))

    # Include preset default file if present
    presets_src = os.path.join(PROJECT_ROOT, "scrcpy_presets.json")
    if os.path.exists(presets_src):
        datas.append((presets_src, "."))

    # Build PyInstaller command
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=MorppyMirror",
        "--clean"
    ]

    # Add icon if exists
    icon_path = os.path.join(ASSETS_DIR, "morppy.ico")
    if os.path.exists(icon_path):
        pyinstaller_cmd.append(f"--icon={icon_path}")

    # Add data mappings
    for src, dst in datas:
        pyinstaller_cmd.append(f"--add-data={src};{dst}")

    # Hidden imports
    hidden_imports = [
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
        "psutil",
        "adbutils",
        "config",
        "android_engine",
        "ios_engine"
    ]
    for imp in hidden_imports:
        pyinstaller_cmd.append(f"--hidden-import={imp}")

    # Target entry script
    entry_script = os.path.join(PROJECT_ROOT, "morppy_app.py")
    pyinstaller_cmd.append(entry_script)

    print("\nRunning PyInstaller command...")
    print(" ".join(pyinstaller_cmd))

    res = subprocess.run(pyinstaller_cmd, cwd=PROJECT_ROOT)
    if res.returncode == 0:
        dist_exe = os.path.join(PROJECT_ROOT, "dist", "MorppyMirror.exe")
        print("\n==================================================")
        print(" BUILD SUCCESSFUL!")
        print(f" Standalone Executable created at: {dist_exe}")
        print("==================================================")
    else:
        print("\n[ERROR] PyInstaller build failed!")
        sys.exit(1)

if __name__ == "__main__":
    build_standalone_exe()
