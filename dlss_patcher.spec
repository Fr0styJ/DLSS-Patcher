# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# Locate the customtkinter package to bundle its assets (themes, images)
import customtkinter
ctk_path = Path(customtkinter.__file__).parent

# Collect all customtkinter data files (themes, images, font files)
ctk_datas = [
    (str(ctk_path / "assets"), "customtkinter/assets"),
]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=ctk_datas,
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'requests',
        'bs4',
        'beautifulsoup4',
        'winreg',
        'ctypes',
        'threading',
        'zipfile',
        'tempfile',
        'shutil',
        'scanner',
        'scraper',
        'updater',
        'registry_mgr',
        'ui',
        'darkdetect',
        'packaging',
    ],
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
    name='DLSS Patcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # No black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,         # Request admin via UAC at launch
    manifest='dlss_patcher.manifest',
    icon=None,              # Add an .ico path here if you have one
)
