@echo off
title Building CutePuppy Standalone Windows Application...
echo.
echo ========================================================
echo   BUILDING CUTE PUPPY STANDALONE WINDOWS APP (GUI-ONLY)
echo ========================================================
echo.

pip install pyinstaller PySide6 Pillow

echo.
echo Packaging CutePuppy.exe (No Console / GUI-only)...
pyinstaller --noconfirm --onedir --windowed --name "CutePuppy" --clean ^
    --add-data "assets;assets" ^
    --add-data "config;config" ^
    app.py

echo.
if exist "dist\CutePuppy\CutePuppy.exe" (
    echo ========================================================
    echo SUCCESS! CutePuppy.exe generated cleanly at:
    echo dist\CutePuppy\CutePuppy.exe
    echo ========================================================
) else (
    echo Build failed. Check PyInstaller output logs.
)
pause
