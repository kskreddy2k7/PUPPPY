#!/bin/bash
echo "========================================================"
echo "   BUILDING CUTE PUPPY STANDALONE macOS APP & DMG"
echo "========================================================"

pip install pyinstaller PySide6 Pillow

# Build macOS .app Bundle via PyInstaller
pyinstaller --noconfirm --onedir --windowed --name "CutePuppy" --clean \
    --add-data "assets:assets" \
    --add-data "config:config" \
    app.py

if [ -d "dist/CutePuppy.app" ]; then
    echo "========================================================"
    echo "SUCCESS! CutePuppy.app generated at dist/CutePuppy.app"
    echo "========================================================"
    
    # Package into .dmg if create-dmg or hdiutil is available
    if command -v hdiutil &> /dev/null; then
        echo "Packaging dist/CutePuppy.dmg..."
        hdiutil create -volname "CutePuppy" -srcfolder "dist/CutePuppy.app" -ov -format UDZO "dist/CutePuppy.dmg"
        echo "CutePuppy.dmg generated successfully at dist/CutePuppy.dmg!"
    fi
else
    echo "Build failed. Please check PyInstaller output."
fi
