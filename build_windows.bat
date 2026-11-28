@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher "py" was not found. Install 64-bit Python 3.12 and retry.
    exit /b 1
)

py -3.12 -m venv .venv-build
if errorlevel 1 exit /b %ERRORLEVEL%

call .venv-build\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 exit /b %ERRORLEVEL%

python -m pip install -r requirements-build.txt
if errorlevel 1 exit /b %ERRORLEVEL%

python build_morppy_exe.py
if errorlevel 1 exit /b %ERRORLEVEL%

echo.
echo Build output: dist\MorppyMirror.exe
echo Distribute this single EXE. End users do not need Python or pip installed.
endlocal
