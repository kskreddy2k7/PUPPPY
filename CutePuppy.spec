# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Include assets and VERSION file
added_files = [
    ('assets', 'assets'),
    ('VERSION', '.'),
]

a = Analysis(
    ['src/cute_puppy/main.py'],
    pathex=['src'],
    binaries=[],
    datas=added_files,
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CutePuppy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='CutePuppy.app',
    icon=None,
    bundle_identifier='com.cutepuppy.desktop',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleExecutable': 'CutePuppy',
        'CFBundleName': 'CutePuppy',
        'CFBundleDisplayName': 'Cute Puppy',
        'CFBundleIdentifier': 'com.cutepuppy.desktop',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,
    },
)
