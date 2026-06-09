# -*- mode: python ; coding: utf-8 -*-
# Wine-optimierte PyInstaller Spec für Windows Build

import os
from pathlib import Path

# Wine-kompatible Pfade
project_dir = Path(r"Z:\home\jean\Dokumente\GitHub\Savage-Worlds-Charakter-Generator-deutsch")

# Daten sammeln - Wine-Pfade verwenden
# Nur existierende Pfade hinzufügen (templates/chars werden ggf. erst zur
# Laufzeit erzeugt und fehlen evtl. im Repo -> PyInstaller bricht sonst ab)
_data_candidates = [
    (str(project_dir / 'assets'), 'assets'),
    (str(project_dir / 'config'), 'config'),
    (str(project_dir / 'settings'), 'settings'),
    (str(project_dir / 'templates'), 'templates'),
    (str(project_dir / 'views'), 'views'),
    (str(project_dir / 'chars'), 'chars'),
    (str(project_dir / 'main.kv'), '.'),
]
datas = [(src, dst) for src, dst in _data_candidates if os.path.exists(src)]

# Hidden imports
hiddenimports = [
    'kivymd', 'kivymd.app', 'kivymd.uix.screen', 'kivymd.uix.boxlayout',
    'kivymd.uix.label', 'kivymd.uix.button', 'kivymd.uix.textfield',
    'kivymd.uix.filemanager', 'kivymd.theming', 'kivymd.icon_definitions',
    'kivymd.icon_definitions.md_icons', 'kivymd.material_resources',
    'kivy', 'kivy.app', 'kivy.lang', 'kivy.clock', 'kivy.properties',
    'PIL', 'PIL.Image', 'reportlab', 'reportlab.pdfgen', 'reportlab.lib',
    'requests', 'json', 'logging'
]

excludes = ['tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas']

a = Analysis(
    ['main.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure)

# One-Directory Mode für Windows
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SavageWorldsCharakterGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # Windows GUI Mode
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='SavageWorldsCharakterGenerator'
)
