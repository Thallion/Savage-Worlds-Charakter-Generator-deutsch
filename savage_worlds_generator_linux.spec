# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Bestimme das Projektverzeichnis
project_dir = Path.cwd()

# Sammle alle Daten-Dateien
datas = [
    (str(project_dir / 'assets'), 'assets'),
    (str(project_dir / 'config'), 'config'),
    (str(project_dir / 'settings'), 'settings'),
    (str(project_dir / 'templates'), 'templates'),
    (str(project_dir / 'views'), 'views'),
    (str(project_dir / 'chars'), 'chars'),
    (str(project_dir / 'main.kv'), '.'),
]

# KivyMD Daten dynamisch hinzufügen (Linux)
kivymd_base_path = project_dir / 'venv' / 'lib' / 'python3.12' / 'site-packages' / 'kivymd'
if kivymd_base_path.exists():
    # Icon definitions
    icon_defs = kivymd_base_path / 'icon_definitions.py'
    if icon_defs.exists():
        datas.append((str(icon_defs), 'kivymd'))
    
    # Fonts (Material Design Icons + Roboto)
    fonts_path = kivymd_base_path / 'fonts'
    if fonts_path.exists():
        datas.append((str(fonts_path), 'kivymd/fonts'))
    
    # UI KV-Dateien
    uix_path = kivymd_base_path / 'uix'
    if uix_path.exists():
        datas.append((str(uix_path), 'kivymd/uix'))
    
    # Bilder
    images_path = kivymd_base_path / 'images'
    if images_path.exists():
        datas.append((str(images_path), 'kivymd/images'))

# Hidden imports für Linux
hiddenimports = [
    'kivymd', 'kivymd.app', 'kivymd.uix.screen', 'kivymd.uix.boxlayout',
    'kivymd.uix.label', 'kivymd.uix.button', 'kivymd.uix.textfield',
    'kivymd.uix.tab', 'kivymd.uix.scrollview', 'kivymd.uix.card',
    'kivymd.uix.list', 'kivymd.uix.dialog', 'kivymd.uix.menu',
    'kivymd.uix.selectioncontrol', 'kivymd.uix.filemanager',
    'kivymd.theming', 'kivymd.icon_definitions', 'kivymd.icon_definitions.md_icons',
    'kivymd.material_resources', 'kivymd.fonts',
    'kivy', 'kivy.app', 'kivy.lang', 'kivy.clock', 'kivy.properties',
    'PIL', 'PIL.Image', 'reportlab', 'reportlab.pdfgen', 'reportlab.lib',
    'requests', 'json', 'logging'
]

# Excludes für Linux
excludes = [
    'tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas',
    'jupyter', 'IPython', 'tornado', 'zmq', 'sqlite3'
]

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

# One-Directory Modus für Linux
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
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='SavageWorldsCharakterGenerator'
)
