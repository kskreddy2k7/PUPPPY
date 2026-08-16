@echo off
echo Building CutePuppy Windows Executable...

set PYTHONPATH=src
python -c "from cute_puppy.animation import generate_all_assets; generate_all_assets()"

pyinstaller --noconfirm CutePuppy.spec

if exist dist\CutePuppy.exe (
    echo Build Successful: dist\CutePuppy.exe
) else (
    echo Build Failed!
    exit /b 1
)
