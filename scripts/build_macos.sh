#!/bin/bash
set -e

echo "Building CutePuppy macOS App Bundle..."

python3 -c "from cute_puppy.animation import generate_all_assets; generate_all_assets()"

pyinstaller --noconfirm CutePuppy.spec

if [ -d "dist/CutePuppy.app" ]; then
    echo "Build Successful: dist/CutePuppy.app"
else
    echo "Build Failed!"
    exit 1
fi
