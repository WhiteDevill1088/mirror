# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_all


project_root = Path(SPECPATH).resolve().parent
datas = []
binaries = []
hiddenimports = [
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
    "config",
    "android_engine",
    "ios_engine",
]

for relative_path in (
    "scrcpy-win64-v4.0",
    "QtScrcpy",
    "uxplay-windows",
    "assets",
):
    source = project_root / relative_path
    if source.is_dir():
        datas.append((str(source), relative_path))

presets = project_root / "scrcpy_presets.json"
if presets.is_file():
    datas.append((str(presets), "."))

for package in ("adbutils", "psutil"):
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports

icon = project_root / "assets" / "morppy.ico"
version = project_root / "version_info.txt"

a = Analysis(
    [str(project_root / "morppy_app.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MorppyMirror",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=str(icon) if icon.is_file() else None,
    version=str(version) if version.is_file() else None,
)
