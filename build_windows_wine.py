#!/usr/bin/env python3
"""
Wine-basiertes Windows Build Script
Optimiert für Cross-Compilation von Linux zu Windows
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_wine_setup():
    """Prüft Wine-Installation und Setup"""
    print("🍷 Prüfe Wine-Setup...")
    
    try:
        # Prüfe Wine
        result = subprocess.run(['wine', '--version'], capture_output=True, text=True)
        print(f"   Wine Version: {result.stdout.strip()}")
        
        # Prüfe Python in Wine
        result = subprocess.run(['wine', 'python', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   Python in Wine: {result.stdout.strip()}")
        else:
            print("❌ Python nicht in Wine gefunden!")
            print("Installiere mit: winetricks python311")
            return False
            
        return True
        
    except FileNotFoundError:
        print("❌ Wine nicht gefunden!")
        print("Installiere mit: sudo apt install wine")
        return False

def prepare_wine_build():
    """Bereitet das Build-Environment vor"""
    project_dir = Path.cwd()
    
    print("🧹 Bereinige alte Builds (Linux-native)...")
    
    # Native Linux cleanup (vermeidet Wine-Probleme)
    dirs_to_clean = ['dist', 'build', '__pycache__']
    for dir_name in dirs_to_clean:
        dir_path = project_dir / dir_name
        if dir_path.exists():
            # Respektiere SKIP_DIST_CLEANUP Umgebungsvariable für dist-Verzeichnis
            if dir_name == 'dist' and os.environ.get("SKIP_DIST_CLEANUP"):
                print(f"   ⏭️  {dir_name}/ übersprungen (SKIP_DIST_CLEANUP gesetzt)")
                continue
            try:
                shutil.rmtree(dir_path)
                print(f"   ✅ {dir_name}/ gelöscht")
            except Exception as e:
                print(f"   ⚠️  {dir_name}/ konnte nicht gelöscht werden: {e}")
    
    # Erstelle Wine-kompatible .spec Datei
    create_wine_spec(project_dir)
    
    return True

def create_wine_spec(project_dir):
    """Erstellt Wine-optimierte .spec Datei"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# Wine-optimierte PyInstaller Spec für Windows Build

import os
from pathlib import Path

# Wine-kompatible Pfade
project_dir = Path(r"Z:\\home\\jean\\Dokumente\\GitHub\\Savage-Worlds-Charakter-Generator-deutsch")

# Daten sammeln - Wine-Pfade verwenden
datas = [
    (str(project_dir / 'assets'), 'assets'),
    (str(project_dir / 'config'), 'config'),
    (str(project_dir / 'settings'), 'settings'),
    (str(project_dir / 'templates'), 'templates'),
    (str(project_dir / 'views'), 'views'),
    (str(project_dir / 'chars'), 'chars'),
    (str(project_dir / 'main.kv'), '.'),
]

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
'''
    
    spec_file = project_dir / "savage_worlds_generator_wine.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"📄 Wine .spec Datei erstellt: {spec_file}")
    return spec_file

def run_wine_build():
    """Führt den Wine-basierten Build aus"""
    project_dir = Path.cwd()
    spec_file = project_dir / "savage_worlds_generator_wine.spec"
    
    print("🍷 Starte Wine PyInstaller...")
    
    # Wine Environment für bessere Kompatibilität
    env = os.environ.copy()
    env['WINEDLLOVERRIDES'] = 'msvcr120,msvcp120=n'  # Native DLLs verwenden
    env['WINEDEBUG'] = '-all'  # Debug-Ausgaben reduzieren
    
    cmd = [
        'wine', 'python', '-m', 'PyInstaller',
        '--clean',
        str(spec_file)
    ]
    
    try:
        print("📦 PyInstaller läuft... (das kann einige Minuten dauern)")
        result = subprocess.run(cmd, env=env, cwd=project_dir, check=True)
        
        if result.returncode == 0:
            print("✅ Wine Build erfolgreich!")
            return verify_wine_build()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Wine Build fehlgeschlagen: {e}")
        return False
    
    return False

def verify_wine_build():
    """Überprüft das Build-Ergebnis"""
    project_dir = Path.cwd()
    dist_dir = project_dir / "dist" / "SavageWorldsCharakterGenerator"
    exe_file = dist_dir / "SavageWorldsCharakterGenerator.exe"
    
    if exe_file.exists():
        size_mb = get_dir_size(dist_dir)
        print(f"🎉 Windows EXE erstellt!")
        print(f"📂 Verzeichnis: {dist_dir}")
        print(f"🚀 EXE-Datei: {exe_file}")
        print(f"📊 Größe: {size_mb:.1f} MB")
        
        # Erstelle README für Windows-Nutzer
        create_windows_readme(dist_dir)
        
        print("\n📋 Nächste Schritte:")
        print("1. Teste die .exe auf einem Windows-System")
        print("2. Verteile das gesamte dist-Verzeichnis")
        print("3. One-Directory Modus reduziert Antiviren-Probleme")
        
        return True
    else:
        print(f"❌ EXE nicht gefunden: {exe_file}")
        return False

def get_dir_size(path):
    """Berechnet Verzeichnisgröße in MB"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                pass
    return total / (1024 * 1024)

def create_windows_readme(dist_dir):
    """Erstellt README für Windows-Nutzer"""
    readme_content = """Savage Worlds Charakter Generator (Windows)
============================================

Diese Version wurde mit Wine cross-compiliert.

INSTALLATION:
- Keine Installation erforderlich
- Komplettes Verzeichnis kopieren

AUSFÜHRUNG:
- Doppelklick auf SavageWorldsCharakterGenerator.exe
- Oder: Start über Eingabeaufforderung

ANTIVIREN-HINWEIS:
- One-Directory Modus reduziert False-Positives
- Alle DLLs sind separat und sichtbar
- Bei Problemen: Ausnahme für das Verzeichnis hinzufügen

VERZEICHNISSTRUKTUR:
- SavageWorldsCharakterGenerator.exe  (Hauptprogramm)
- _internal/                          (Bibliotheken)
- Alle Ressourcen transparent sichtbar

CROSS-COMPILATION:
Diese .exe wurde mit Wine unter Linux erstellt.
Bei Problemen bitte melden.

Viel Spaß mit dem Charaktergenerator!
"""
    
    readme_file = dist_dir / "README_WINDOWS.txt"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📄 Windows README erstellt: {readme_file}")

def main():
    """Hauptfunktion"""
    print("🍷 Wine-basierter Windows Build")
    print("Cross-Compilation: Linux → Windows .exe")
    print()
    
    # Prüfe Wine Setup
    if not check_wine_setup():
        return False
    
    # Bereite Build vor
    if not prepare_wine_build():
        return False
    
    # Führe Build aus
    if not run_wine_build():
        return False
    
    print("\n🎉 Windows Build erfolgreich abgeschlossen!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💥 Build fehlgeschlagen!")
        print("Mögliche Lösungen:")
        print("1. Wine neu installieren: sudo apt install --reinstall wine")
        print("2. Python in Wine installieren: winetricks python311")
        print("3. PyInstaller in Wine installieren: wine pip install pyinstaller")
        sys.exit(1)
    else:
        print("\n🎯 Die Windows .exe ist bereit für die Verteilung!")