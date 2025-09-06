#!/usr/bin/env python3
"""
Universelles Build-Script für Desktop-Versionen
Automatische Plattformerkennung und entsprechender Build
"""

import sys
import platform
import subprocess
from pathlib import Path

def main():
    """Hauptfunktion - erkennt Plattform und startet entsprechenden Build"""
    current_platform = platform.system().lower()
    project_dir = Path.cwd()
    
    print("🔧 Savage Worlds Charakter Generator - Desktop Build")
    print(f"🖥️  Erkannte Plattform: {platform.system()}")
    print(f"📂 Projekt-Verzeichnis: {project_dir}")
    print()
    
    if current_platform == "windows":
        print("🪟 Starte Windows Build (One-Directory Modus)...")
        build_script = project_dir / "build_windows.py"
    elif current_platform == "linux":
        print("🐧 Starte Linux Build (One-Directory Modus)...")
        build_script = project_dir / "build_linux.py"
    elif current_platform == "darwin":
        print("🍎 macOS wird aktuell nicht unterstützt")
        print("   Verwende manuell: pyinstaller savage_worlds_generator.spec")
        return False
    else:
        print(f"❌ Unbekannte Plattform: {current_platform}")
        print("   Unterstützte Plattformen: Windows, Linux")
        return False
    
    if not build_script.exists():
        print(f"❌ Build-Script nicht gefunden: {build_script}")
        return False
    
    try:
        # Starte das plattformspezifische Build-Script
        result = subprocess.run([sys.executable, str(build_script)], 
                              cwd=project_dir, 
                              check=True)
        
        if result.returncode == 0:
            print()
            print("✅ Build erfolgreich abgeschlossen!")
            print("📦 Distribution befindet sich im 'dist/' Verzeichnis")
            
            # Gebe plattformspezifische Hinweise
            if current_platform == "windows":
                print("🪟 Windows: Verteile das gesamte Verzeichnis")
                print("   Antiviren-Vorteil: Separate DLLs reduzieren False-Positives")
            elif current_platform == "linux":
                print("🐧 Linux: Verteile das gesamte Verzeichnis")
                print("   Starten mit: ./run.sh oder direkter Binary")
            
            return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Build fehlgeschlagen mit Exit-Code: {e.returncode}")
        return False
    
    except FileNotFoundError:
        print(f"❌ Python-Interpreter nicht gefunden")
        return False
    
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n💥 Build konnte nicht abgeschlossen werden!")
        print("🔍 Überprüfe:")
        print("   • PyInstaller ist installiert: pip install pyinstaller")
        print("   • Alle Abhängigkeiten sind verfügbar")
        print("   • Build-Scripts sind vorhanden")
        sys.exit(1)
    
    print("\n🎯 Nächste Schritte:")
    print("1. Teste die erstellte Distribution")
    print("2. Verteile das gesamte dist-Verzeichnis")
    print("3. Bei Antiviren-Problemen: Melde False-Positives")