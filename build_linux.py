#!/usr/bin/env python3
"""
Build-Script für Linux Binary mit PyInstaller (One-Directory Modus)
Reduziert potentielle Probleme durch Verzeichnis-Distribution
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """Hauptfunktion für Linux Build"""
    project_dir = Path.cwd()
    print(f"Projekt-Verzeichnis: {project_dir}")
    
    # Prüfe ob PyInstaller verfügbar ist
    try:
        import PyInstaller
        print(f"PyInstaller Version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller nicht gefunden! Installiere mit: pip install pyinstaller")
        return False
    
    # Bereinige alte Builds
    dist_dir = project_dir / "dist"
    build_dir = project_dir / "build"
    
    if dist_dir.exists():
        print("🧹 Bereinige altes dist-Verzeichnis...")
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        print("🧹 Bereinige altes build-Verzeichnis...")
        shutil.rmtree(build_dir)
    
    # Linux-spezifische .spec Datei erstellen
    create_linux_spec(project_dir)
    
    # PyInstaller ausführen
    spec_file = project_dir / "savage_worlds_generator_linux.spec"
    
    print("🔨 Starte PyInstaller Build (One-Directory Modus für Linux)...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",  # Bereinige Cache
        str(spec_file)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, cwd=project_dir)
        if result.returncode == 0:
            print("✅ Build erfolgreich!")
            
            # Überprüfe Ausgabe
            exe_dir = dist_dir / "SavageWorldsCharakterGenerator"
            exe_file = exe_dir / "SavageWorldsCharakterGenerator"
            
            if exe_file.exists():
                # Mache die Binary ausführbar
                os.chmod(exe_file, 0o755)
                
                print(f"📂 Ausgabe-Verzeichnis: {exe_dir}")
                print(f"🚀 Hauptprogramm: {exe_file}")
                print(f"📊 Verzeichnisgröße: {get_dir_size(exe_dir):.1f} MB")
                
                # Erstelle Linux README
                create_linux_readme(exe_dir)
                
                # Erstelle Launcher-Script
                create_launcher_script(exe_dir)
                
                print("\n🐧 Linux One-Directory Vorteile:")
                print("   • Separate .so-Dateien sind sichtbar")
                print("   • Keine gepackte Binary")
                print("   • Transparente Dateistruktur")
                print("   • Bessere Debugging-Möglichkeiten")
                
                return True
            else:
                print(f"❌ Binary nicht gefunden: {exe_file}")
                return False
    
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller Build fehlgeschlagen: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False

def create_linux_spec(project_dir):
    """Erstellt Linux-spezifische .spec Datei"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

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
'''
    
    spec_file = project_dir / "savage_worlds_generator_linux.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"📄 Linux .spec Datei erstellt: {spec_file}")

def get_dir_size(path):
    """Berechnet die Größe eines Verzeichnisses in MB"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                pass
    return total / (1024 * 1024)

def create_linux_readme(exe_dir):
    """Erstellt Linux README-Datei"""
    readme_content = """Savage Worlds Charakter Generator (Linux)
=========================================

INSTALLATION:
- Keine Installation erforderlich
- Gesamtes Verzeichnis an gewünschten Ort kopieren

AUSFÜHRUNG:
- Terminal: ./SavageWorldsCharakterGenerator
- oder: ./run.sh (Launcher-Script)
- oder: Doppelklick auf run.sh im Dateimanager

SYSTEMVORAUSSETZUNGEN:
- Linux mit X11 oder Wayland
- Keine zusätzlichen Python-Pakete erforderlich

VERZEICHNISSTRUKTUR:
- SavageWorldsCharakterGenerator  (Hauptprogramm)
- run.sh                          (Launcher-Script)
- _internal/                      (Programmbibliotheken)
- assets/                        (Bilder und Ressourcen)
- config/                        (Konfigurationsdateien)

HINWEISE:
- Bei Problemen: chmod +x SavageWorldsCharakterGenerator
- Für Desktop-Integration: run.sh verwenden

Bei Problemen kontaktiere den Entwickler.
"""
    
    readme_file = exe_dir / "README.txt"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📄 Linux README erstellt: {readme_file}")

def create_launcher_script(exe_dir):
    """Erstellt ein Launcher-Script für einfachere Ausführung"""
    launcher_content = """#!/bin/bash
# Launcher Script für Savage Worlds Charakter Generator

# Wechsle ins Programmverzeichnis
cd "$(dirname "$0")"

# Starte das Programm
./SavageWorldsCharakterGenerator

# Warte auf Eingabe bei Fehlern
if [ $? -ne 0 ]; then
    echo "Fehler beim Starten des Programms. Drücke Enter zum Schließen..."
    read
fi
"""
    
    launcher_file = exe_dir / "run.sh"
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    # Mache das Script ausführbar
    os.chmod(launcher_file, 0o755)
    
    print(f"🚀 Launcher-Script erstellt: {launcher_file}")

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Linux Build erfolgreich abgeschlossen!")
        print("Das Programm befindet sich im 'dist/SavageWorldsCharakterGenerator' Verzeichnis")
        print("Starten mit: cd dist/SavageWorldsCharakterGenerator && ./run.sh")
    else:
        print("\n💥 Build fehlgeschlagen!")
        sys.exit(1)