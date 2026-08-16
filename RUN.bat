@echo off
title Cute Desktop Puppy - Launcher
echo ===================================================
echo   Launching Cute Desktop Puppy
echo ===================================================
echo.

if not exist venv (
    echo Creating Python Virtual Environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Launching Cute Desktop Puppy...
start "" pythonw app.py
exit
