@echo off
title Morppy Mobile Mirror Suite (Dev Runner)
cd /d "%~dp0"
echo Launching Morppy Suite in development mode...
python morppy_app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Morppy exited with error code %ERRORLEVEL%.
    pause
)
