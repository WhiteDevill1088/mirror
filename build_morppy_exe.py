import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SCRCPY_DIR = PROJECT_ROOT / "scrcpy-win64-v4.0"
QT_SCRCPY_DIR = PROJECT_ROOT / "QtScrcpy"
UXPLAY_DIR = PROJECT_ROOT / "uxplay-windows"
OUTPUT_EXE = PROJECT_ROOT / "dist" / "MorppyMirror.exe"


def validate_build_inputs():
    if sys.platform != "win32":
        raise RuntimeError("Build the Windows executable on Windows; PyInstaller cannot cross-compile.")
    if sys.maxsize <= 2**32:
        raise RuntimeError("Use 64-bit Python to build the Windows x64 package.")

    required_files = {
        "scrcpy": SCRCPY_DIR / "scrcpy.exe",
        "ADB": SCRCPY_DIR / "adb.exe",
        "QtScrcpy": QT_SCRCPY_DIR / "QtScrcpy.exe",
        "UxPlay": UXPLAY_DIR / "uxplay.exe",
    }
    missing = [f"{name}: {path}" for name, path in required_files.items() if not path.is_file()]
    if missing:
        missing_list = "\n".join(f"  - {entry}" for entry in missing)
        raise FileNotFoundError(
            "The complete Windows tool distributions are required to bundle all app features:\n"
            f"{missing_list}\n"
            "Place the complete distributions in scrcpy-win64-v4.0, QtScrcpy, and "
            "uxplay-windows beside this script."
        )


def build_standalone_exe():
    validate_build_inputs()

    spec_path = PROJECT_ROOT / "MorppyMirror.spec"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--distpath",
        str(PROJECT_ROOT / "dist"),
        "--workpath",
        str(PROJECT_ROOT / "build" / "pyinstaller"),
        str(spec_path),
    ]

    print("Building MorppyMirror as a single-file Windows application...")
    print("The executable bundles Python, Python packages, Qt, and the vendor tool folders.")
    result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)

    if not OUTPUT_EXE.is_file():
        raise FileNotFoundError(f"PyInstaller completed but did not create {OUTPUT_EXE}")
    print(f"\nBuild successful: {OUTPUT_EXE}")
    print("Distribute this single EXE; end users do not need Python or pip packages installed.")


if __name__ == "__main__":
    try:
        build_standalone_exe()
    except (FileNotFoundError, RuntimeError) as error:
        print(f"BUILD ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
