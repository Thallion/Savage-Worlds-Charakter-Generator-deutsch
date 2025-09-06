# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Bestimme das Projektverzeichnis
project_dir = Path.cwd()

# Sammle alle Daten-Dateien
datas = [
    # Assets Ordner
    (str(project_dir / 'assets'), 'assets'),
    
    # Config Dateien
    (str(project_dir / 'config'), 'config'),
    
    # Settings Dateien
    (str(project_dir / 'settings'), 'settings'),
    
    # Templates
    (str(project_dir / 'templates'), 'templates'),
    
    # Views (Python-Dateien)
    (str(project_dir / 'views'), 'views'),
    
    # Chars Ordner
    (str(project_dir / 'chars'), 'chars'),
    
    # Main KV-Datei
    (str(project_dir / 'main.kv'), '.'),
    
    # Alle KV-Dateien einzeln hinzufügen für bessere Erkennung
    (str(project_dir / 'views' / 'ausruestung_popup.kv'), 'views'),
    (str(project_dir / 'views' / 'ausruestung_view.kv'), 'views'),
    (str(project_dir / 'views' / 'charakterbogen_view.kv'), 'views'),
    (str(project_dir / 'views' / 'eigenschaften_view.kv'), 'views'),
    (str(project_dir / 'views' / 'einstellungen_widget.kv'), 'views'),
    (str(project_dir / 'views' / 'fertigkeit_popup.kv'), 'views'),
    (str(project_dir / 'views' / 'handicap_popup.kv'), 'views'),
    (str(project_dir / 'views' / 'handicaps_view.kv'), 'views'),
    (str(project_dir / 'views' / 'macht_popup.kv'), 'views'),
    (str(project_dir / 'views' / 'maechte_view.kv'), 'views'),
    (str(project_dir / 'views' / 'pointbar_view.kv'), 'views'),
    (str(project_dir / 'views' / 'profil_view.kv'), 'views'),
    (str(project_dir / 'views' / 'ruestung_popup.kv'), 'views'),
    (str(project_dir / 'views' / 'schild_popup.kv'), 'views'),
    (str(project_dir / 'views' / 'setting_popup.kv'), 'views'),
    (str(project_dir / 'views' / 'talente_view.kv'), 'views'),
    (str(project_dir / 'views' / 'talent_popup.kv'), 'views'),
    (str(project_dir / 'views' / 'voelker_view.kv'), 'views'),
    (str(project_dir / 'views' / 'volk_popup.kv'), 'views'),
    (str(project_dir / 'views' / 'waffe_popup.kv'), 'views'),
]

# KivyMD Daten dynamisch hinzufügen
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
    
    # Material resources
    material_res = kivymd_base_path / 'material_resources.py'
    if material_res.exists():
        datas.append((str(material_res), 'kivymd'))
else:
    print("Warnung: KivyMD nicht in erwartetem Pfad gefunden")

# Filtere None-Werte heraus
datas = [item for item in datas if item is not None]

# Hidden imports für KivyMD und andere Dependencies
hiddenimports = [
    'kivymd',
    'kivymd.app',
    'kivymd.uix.screen',
    'kivymd.uix.boxlayout',
    'kivymd.uix.label',
    'kivymd.uix.button',
    'kivymd.uix.textfield',
    'kivymd.uix.tab',
    'kivymd.uix.tab.tab',
    'kivymd.uix.scrollview',
    'kivymd.uix.card',
    'kivymd.uix.list',
    'kivymd.uix.dialog',
    'kivymd.uix.menu',
    'kivymd.uix.navigationbar',
    'kivymd.uix.navigationdrawer',
    'kivymd.uix.selectioncontrol',
    'kivymd.uix.slider',
    'kivymd.uix.snackbar',
    'kivymd.uix.appbar',
    'kivymd.uix.tooltip',
    'kivymd.uix.progressindicator',
    'kivymd.uix.filemanager',
    'kivymd.theming',
    'kivymd.material_resources',
    'kivymd.icon_definitions',
    'kivymd.icon_definitions.md_icons',
    'kivymd.fonts',
    'kivymd.fonts.Roboto',
    'materialyoucolor',
    'materialyoucolor.utils',
    'materialyoucolor.quantize',
    'kivy',
    'kivy.app',
    'kivy.lang',
    'kivy.clock',
    'kivy.properties',
    'kivy.core.window',
    'kivy.logger',
    'kivy.metrics',
    'kivy.uix.popup',
    'kivy.uix.scrollview',
    'kivy.uix.widget',
    'kivy.uix.screenmanager',
    'kivy.uix.recycleview',
    'kivy.uix.recycleboxlayout',
    'kivy.uix.behaviors',
    'kivy.config',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.lib',
    'reportlab.lib.pagesizes',
    'reportlab.lib.units',
    'reportlab.lib.colors',
    'reportlab.platypus',
    'requests',
    'requests.adapters',
    'requests.auth',
    'requests.cookies',
    'json',
    'logging',
    'functools',
    'webbrowser',
    're',
    'sys',
    'os'
]

# Module die oft False-Positives auslösen ausschließen
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'jupyter',
    'IPython',
    'notebook',
    'tornado',
    'zmq',
    'sqlite3',
    'distutils',
    'setuptools',
    'pip',
    'wheel'
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

# One-Directory Modus: EXE nur mit Scripts, Rest separat als COLLECT
exe = EXE(
    pyz,
    a.scripts,
    [],  # Keine Binaries in EXE (für one-directory)
    exclude_binaries=True,  # Wichtig für one-directory Modus
    name='SavageWorldsCharakterGenerator',  # Ohne .exe für one-directory
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX oft False-Positive Auslöser
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Für GUI-Anwendung auf False setzen
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',  # Version Info für weniger False-Positives
    icon=str(project_dir / 'assets' / 'Savage-Worlds-Fanprodukt-Logo.png') if (project_dir / 'assets' / 'Savage-Worlds-Fanprodukt-Logo.png').exists() else None,
)

# COLLECT für one-directory Distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,  # UPX deaktiviert für weniger False-Positives
    upx_exclude=[],
    name='SavageWorldsCharakterGenerator'
)