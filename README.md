# Morppy Mobile Mirror Suite

## Build the Windows application

Build on **64-bit Windows**. PyInstaller does not cross-compile Windows executables from Linux or macOS.

1. Install 64-bit Python 3.12 and Git.
2. Put the complete Windows scrcpy 4.0 distribution in `scrcpy-win64-v4.0` beside `build_windows.bat`. It must contain `scrcpy.exe`, `adb.exe`, and the other DLLs/files from that distribution.
3. Put the complete QtScrcpy distribution in `QtScrcpy` (containing `QtScrcpy.exe`) and the complete UxPlay Windows distribution in `uxplay-windows` (containing `uxplay.exe`). The build validates all three toolsets so the packaged app has every advertised engine.
4. Open the project folder in File Explorer and run `build_windows.bat`.
5. Double-click `dist\MorppyMirror.exe`.

The batch file creates a local build-only virtual environment and installs the build dependencies. These are needed only on the computer that builds the app. The output is one **single-file EXE**: distribute `dist\MorppyMirror.exe` by itself. The target computer does not need Python, pip, PyQt5, or separately installed scrcpy/ADB/QtScrcpy/UxPlay.

The EXE bundles the Python runtime, PyQt5 and its Qt plugins, `adbutils`, `psutil`, and all three vendor tool folders. On first launch, PyInstaller extracts its bundled files to a temporary directory; startup may take a little longer. User settings and session data are stored under `%LOCALAPPDATA%\MorppyMirror`.

## Windows security prompts

The executable is built without a console window and does not request administrator privileges.

An unsigned executable may still trigger Microsoft Defender SmartScreen, and Windows Firewall may request permission for wireless ADB or the AirPlay receiver. Those protections cannot safely be disabled or bypassed by the app. For distribution to other users, sign the executable with a trusted code-signing certificate and timestamp the signature. If you use those network features, allow access on private networks only when Windows presents the firewall prompt and you intend to use them.

## Run from source

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python morppy_app.py
```
