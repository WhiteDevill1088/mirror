# Morppy Mobile Mirror Suite

Morppy is a Windows desktop app for Android screen mirroring and AirPlay reception. The packaged release is designed as a single self-contained EXE; Android devices still need debugging authorization, and network features need local-network access.

- New to Morppy? Start with [How to Use](HOW_TO_USE.md).
- Building or signing a Windows release? See the instructions below.

## Build the Windows application

Build on **64-bit Windows**. PyInstaller does not cross-compile Windows executables from Linux or macOS.

1. Install 64-bit Python 3.12 and Git.
2. Put the complete Windows scrcpy 4.0 distribution in `scrcpy-win64-v4.0` beside `build_windows.bat`. It must contain `scrcpy.exe`, `adb.exe`, and the other DLLs/files from that distribution.
3. Put the complete QtScrcpy distribution in `QtScrcpy` (containing `QtScrcpy.exe`) and the complete UxPlay Windows distribution in `uxplay-windows` (containing `uxplay.exe`). The build validates all three toolsets so the packaged app has every advertised engine.
4. For a signed build, install a trusted code-signing certificate into the build user's **Current User > Personal** certificate store, install the Windows SDK SignTool, and set `MORPPY_SIGN_THUMBPRINT` to the certificate's 40-character SHA-1 thumbprint before building. Optionally set `MORPPY_SIGNTOOL` if `signtool.exe` is not on `PATH`. The build signs with SHA-256, adds a trusted timestamp, and verifies the signature; signing or verification errors fail the build.
5. Open the project folder in File Explorer and run `build_windows.bat`.
6. Distribute `dist\MorppyMirror.exe` and launch it on a supported Windows x64 computer.

The batch file creates a local build-only virtual environment and installs the build dependencies. These are needed only on the computer that builds the app. The output is one **single-file EXE**: distribute `dist\MorppyMirror.exe` by itself. On supported 64-bit Windows 10/11, the target computer does not need Python, pip, PyQt5, the Visual C++ Redistributable, or separately installed scrcpy/ADB/QtScrcpy/UxPlay; these application runtimes and tools are bundled. First launch extracts the bundled files into a temporary directory, so allow enough free disk space and do not delete that temporary directory while the app is running. User preferences and session data are stored under `%LOCALAPPDATA%\MorppyMirror`.

The code-signing certificate and Windows SDK are **build-machine** requirements only, never end-user prerequisites. Keep the signing private key protected and do not commit it to the repository. For automated builds, provision the certificate in the signing runner's current-user certificate store using the CI provider's protected secret mechanism; expose only its public thumbprint as `MORPPY_SIGN_THUMBPRINT`.

The EXE bundles the Python runtime, PyQt5 and its Qt plugins, `adbutils`, `psutil`, and all three vendor tool folders.

Open **Theme Studio** to preview Cupertino Light, Hybrid Studio, or Midnight Glass and apply a Light, Dark, or System appearance across the app. The selected theme is saved with the app's local preferences.

## Windows security prompts

The executable is built without a console window and does not request administrator privileges.

An unsigned executable may show an unknown-publisher or Microsoft Defender SmartScreen warning. Signing with a valid certificate from a trusted certificate authority identifies the publisher and helps establish file integrity; it does **not** guarantee that SmartScreen will never warn, particularly for a new publisher or a file without established reputation. Distribute the same signed file consistently, keep the signing certificate valid, and submit incorrect Microsoft Defender detections through Microsoft's official security-intelligence submission process. Never instruct users to disable SmartScreen, Defender, or Windows security checks.

Windows Firewall may separately request permission for wireless ADB or the AirPlay receiver. Allow access on private networks only when you use those features. This is separate from application signing and cannot be removed by bundling.

## Run from source

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python morppy_app.py
```
