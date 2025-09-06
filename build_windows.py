#!/usr/bin/env python3
"""
Build-Script für Windows EXE mit PyInstaller (One-Directory Modus)
Reduziert Antiviren-False-Positives durch Verzeichnis-Distribution
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """Hauptfunktion für Windows Build"""
    project_dir = Path.cwd()
    print(f"Projekt-Verzeichnis: {project_dir}")
    
    # Prüfe ob PyInstaller verfügbar ist
    try:
        import PyInstaller
        print(f"PyInstaller Version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller nicht gefunden! Installiere mit: pip install pyinstaller")
        return False
    
    # Bereinige alte Builds (Wine-kompatibel)
    dist_dir = project_dir / "dist"
    build_dir = project_dir / "build"
    
    def safe_rmtree(path):
        """Wine-kompatible Verzeichnis-Löschung"""
        if path.exists():
            try:
                shutil.rmtree(path)
                return True
            except (OSError, FileNotFoundError, PermissionError) as e:
                print(f"⚠️  Konnte {path} nicht vollständig löschen: {e}")
                print("   Fahre trotzdem fort...")
                return False
        return True
    
    if dist_dir.exists():
        print("🧹 Bereinige altes dist-Verzeichnis...")
        safe_rmtree(dist_dir)
    
    if build_dir.exists():
        print("🧹 Bereinige altes build-Verzeichnis...")
        safe_rmtree(build_dir)
    
    # PyInstaller ausführen
    spec_file = project_dir / "savage_worlds_generator.spec"
    
    if not spec_file.exists():
        print(f"❌ Spec-Datei nicht gefunden: {spec_file}")
        return False
    
    print("🔨 Starte PyInstaller Build (One-Directory Modus)...")
    print("   Dies reduziert Antiviren-False-Positives durch getrennte DLL-Dateien")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",  # Bereinige Cache
        str(spec_file)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, cwd=project_dir)
        if result.returncode == 0:
            print("✅ Build erfolgreich!")
            
            # Überprüfe Ausgabe (plattformspezifisch)
            exe_dir = dist_dir / "SavageWorldsCharakterGenerator"
            
            # Windows: .exe, Linux: ohne Endung
            if os.name == 'nt':
                exe_file = exe_dir / "SavageWorldsCharakterGenerator.exe"
            else:
                exe_file = exe_dir / "SavageWorldsCharakterGenerator"
            
            if exe_file.exists():
                print(f"📂 Ausgabe-Verzeichnis: {exe_dir}")
                print(f"🚀 Hauptprogramm: {exe_file}")
                print(f"📊 Verzeichnisgröße: {get_dir_size(exe_dir):.1f} MB")
                
                # Erstelle README für Benutzer
                create_user_readme(exe_dir)
                
                if os.name == 'nt':
                    print("\n🎯 Antiviren-Vorteile des One-Directory Modus:")
                    print("   • Separate DLL-Dateien reduzieren Verdacht")
                    print("   • Keine gepackte EXE-Datei")
                    print("   • Transparente Dateistruktur")
                    print("   • Weniger False-Positive Warnungen")
                else:
                    print("\n⚠️  Linux Build erstellt (keine Windows .exe)")
                    print("   Für echte Windows .exe:")
                    print("   1. Auf Windows-System builden")
                    print("   2. Wine verwenden: wine python build_windows.py")
                    print("   3. Docker nutzen: python docker_windows_build.py")
                
                return True
            else:
                print(f"❌ EXE-Datei nicht gefunden: {exe_file}")
                return False
    
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller Build fehlgeschlagen: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False

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
    return total / (1024 * 1024)  # Konvertiere zu MB

def create_user_readme(exe_dir):
    """Erstellt eine README-Datei für den Benutzer"""
    readme_content = """Savage Worlds Charakter Generator
==================================

INSTALLATION:
- Keine Installation erforderlich
- Einfach das gesamte Verzeichnis an gewünschten Ort kopieren

AUSFÜHRUNG:
- Doppelklick auf SavageWorldsCharakterGenerator.exe
- Das Programm startet direkt

ANTIVIREN-HINWEIS:
- Diese Version verwendet den "One-Directory" Modus
- Reduziert False-Positive Warnungen von Antiviren-Software
- Alle Dateien sind sichtbar und nicht gepackt

VERZEICHNISSTRUKTUR:
- SavageWorldsCharakterGenerator.exe  (Hauptprogramm)
- _internal/                          (Programmbibliotheken)
- assets/                            (Bilder und Ressourcen)
- config/                            (Konfigurationsdateien)

Bei Problemen kontaktiere den Entwickler.
"""
    
    readme_file = exe_dir / "README.txt"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📄 README erstellt: {readme_file}")

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Build erfolgreich abgeschlossen!")
        print("Das Programm befindet sich im 'dist/SavageWorldsCharakterGenerator' Verzeichnis")
    else:
        print("\n💥 Build fehlgeschlagen!")
        sys.exit(1)