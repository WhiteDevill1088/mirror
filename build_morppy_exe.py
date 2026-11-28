import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SCRCPY_DIR = PROJECT_ROOT / "scrcpy-win64-v4.0"
QT_SCRCPY_DIR = PROJECT_ROOT / "QtScrcpy"
UXPLAY_DIR = PROJECT_ROOT / "uxplay-windows"
OUTPUT_EXE = PROJECT_ROOT / "dist" / "MorppyMirror.exe"
TIMESTAMP_URL = "https://timestamp.digicert.com"


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

    sign_executable()

    print(f"\nBuild successful: {OUTPUT_EXE}")
    print("Distribute this single EXE; end users do not need Python or app packages installed.")


def sign_executable():
    thumbprint = os.environ.get("MORPPY_SIGN_THUMBPRINT", "").replace(" ", "")
    if not thumbprint:
        print(
            "\nWARNING: The executable is unsigned. Windows may show an unknown-publisher "
            "or SmartScreen warning."
        )
        print(
            "For a signed build, install a trusted code-signing certificate in the current "
            "user's Personal certificate store and set MORPPY_SIGN_THUMBPRINT."
        )
        return

    if not re.fullmatch(r"[0-9A-Fa-f]{40}", thumbprint):
        raise RuntimeError("MORPPY_SIGN_THUMBPRINT must be a 40-character SHA-1 certificate thumbprint.")

    signtool = os.environ.get("MORPPY_SIGNTOOL") or shutil.which("signtool")
    if not signtool:
        raise RuntimeError(
            "MORPPY_SIGN_THUMBPRINT is configured, but signtool was not found. "
            "Install the Windows SDK signing tools or set MORPPY_SIGNTOOL to signtool.exe."
        )

    sign_command = [
        signtool,
        "sign",
        "/fd",
        "SHA256",
        "/tr",
        TIMESTAMP_URL,
        "/td",
        "SHA256",
        "/sha1",
        thumbprint,
        "/s",
        "My",
        str(OUTPUT_EXE),
    ]

    print("\nSigning executable with SHA-256 and a trusted timestamp...")
    for command in (
        sign_command,
        [signtool, "verify", "/pa", "/v", str(OUTPUT_EXE)],
    ):
        result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
        if result.returncode:
            raise RuntimeError(f"signtool failed with exit code {result.returncode}.")
    print("Authenticode signature verified.")


if __name__ == "__main__":
    try:
        build_standalone_exe()
    except (FileNotFoundError, RuntimeError) as error:
        print(f"BUILD ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
