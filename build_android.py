
#!/usr/bin/env python3
"""
Unified Build Script für Savage Worlds Charakter Generator
Erstellt Linux Binary, Windows EXE (via Wine), und Android APK
Organisiert alle Builds im dist/ Ordner mit Unterordnern
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import time

def set_android_config_defaults():
    """Setzt Android-spezifische Config-Defaults (mobile_modus=true, show_logger=false)"""
    project_dir = Path.cwd()
    config_dir = project_dir / "config"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "app_config.json"

    # Bestehende Config laden oder neue erstellen
    import json
    config_data = {}
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"⚠️  Bestehende Config konnte nicht geladen werden: {e}")

    # Android-Defaults setzen
    config_data['mobile_modus'] = True
    config_data['show_logger'] = False
    config_data['force_mobile_layout'] = True

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

    print(f"📱 Android-Defaults gesetzt: mobile_modus=true, show_logger=false, force_mobile_layout=true")


def setup_dist_structure():
    """Erstellt die dist-Ordnerstruktur"""
    project_dir = Path.cwd()
    dist_dir = project_dir / "dist"
    
    # Bereinige alten dist-Ordner
    if dist_dir.exists():
        print("🧹 Bereinige alten dist-Ordner...")
        shutil.rmtree(dist_dir)
    
    # Erstelle neue Struktur
    dist_dir.mkdir(exist_ok=True)
    (dist_dir / "linux").mkdir(exist_ok=True)
    (dist_dir / "windows").mkdir(exist_ok=True)
    (dist_dir / "android").mkdir(exist_ok=True)
    
    print(f"📁 Dist-Struktur erstellt: {dist_dir}")
    return dist_dir

def build_android(dist_dir):
    """Build Android APK mit Buildozer"""
    print("\n" + "="*50)
    print("🤖 ANDROID BUILD STARTEN")
    print("="*50)

    try:
        # Prüfe Buildozer Installation
        result = subprocess.run(['buildozer', '--version'],
                              capture_output=True, text=True)
        print(f"Buildozer Version: {result.stdout.strip()}")

        # Alte APKs aus bin/ entfernen, damit wir erkennen ob ein neuer Build entsteht
        bin_dir = Path.cwd() / "bin"
        if bin_dir.exists():
            old_apks = list(bin_dir.glob("*.apk"))
            for old_apk in old_apks:
                old_apk.unlink()
                print(f"🧹 Alte APK entfernt: {old_apk.name}")

        # Nur App-Quellcode-Cache löschen (nicht die kompilierten Libraries!)
        # buildozer android clean würde auch pyjnius/kivy löschen, die dann
        # wegen Cython 3.x Inkompatibilität nicht neu kompilieren können.
        app_cache = Path.cwd() / ".buildozer" / "android" / "app"
        if app_cache.exists():
            import shutil as _shutil
            _shutil.rmtree(app_cache)
            print("🧹 App-Quellcode-Cache bereinigt (.buildozer/android/app/)")

        # Cython 3.x Fixes für pyjnius/kivy anwenden (falls Sources vorhanden)
        print("🔧 Wende Cython-Kompatibilitäts-Fixes an...")
        subprocess.run([sys.executable, 'build_fixes.py'], cwd=Path.cwd())

        # Starte Android Build (erster Versuch)
        result = subprocess.run(['buildozer', 'android', 'debug'],
                              cwd=Path.cwd())

        if result.returncode != 0:
            # Build fehlgeschlagen - Fixes erneut anwenden und nochmal versuchen.
            # Buildozer lädt beim ersten Lauf ggf. frische Quellen herunter,
            # die die Fixes überschreiben. Nach dem Download sind sie vorhanden.
            print("⚠️  Erster Build fehlgeschlagen - wende Fixes erneut an...")
            subprocess.run([sys.executable, 'build_fixes.py'], cwd=Path.cwd())
            result = subprocess.run(['buildozer', 'android', 'debug'],
                                  cwd=Path.cwd())

    except FileNotFoundError:
        print("❌ Buildozer nicht gefunden! Installiere mit: pip install buildozer")
        return False

    # Finde und verschiebe APK (unabhängig vom Build Return Code)
    bin_dir = Path.cwd() / "bin"
    apk_files = list(bin_dir.glob("*.apk"))
    
    if apk_files:
        # Stelle sicher dass android Ordner existiert
        (dist_dir / "android").mkdir(exist_ok=True)
        
        for apk_file in apk_files:
            target_file = dist_dir / "android" / apk_file.name
            shutil.copy2(apk_file, target_file)
            print(f"✅ APK nach {target_file} kopiert")
        
        # Kopiere auch buildozer.spec für Referenz
        spec_file = Path.cwd() / "buildozer.spec"
        if spec_file.exists():
            shutil.copy2(spec_file, dist_dir / "android" / "buildozer.spec")
        
        return True
    else:
        print(f"❌ Keine APK-Datei gefunden in: {bin_dir}")
        return False
    
    return False

def create_dist_readme(dist_dir):
    """Erstellt eine README für den dist-Ordner"""
    readme_content = """Savage Worlds Charakter Generator - Builds
==========================================

Dieses Verzeichnis enthält die fertigen Builds für alle Plattformen:

📁 VERZEICHNISSTRUKTUR:
├── linux/
│   └── SavageWorldsCharakterGenerator/    # Linux Binary (One-Directory)
│       ├── SavageWorldsCharakterGenerator # Hauptprogramm
│       ├── run.sh                        # Launcher-Script
│       └── README.txt                    # Linux-spezifische Anweisungen
│
├── windows/
│   └── SavageWorldsCharakterGenerator/    # Windows EXE (via Wine)
│       ├── SavageWorldsCharakterGenerator.exe # Hauptprogramm
│       └── README_WINDOWS.txt            # Windows-spezifische Anweisungen
│
└── android/
    ├── *.apk                             # Android APK-Datei(en)
    └── buildozer.spec                    # Build-Konfiguration (Referenz)

🚀 AUSFÜHRUNG:

Linux:
  cd linux/SavageWorldsCharakterGenerator
  ./run.sh

Windows:
  Doppelklick auf SavageWorldsCharakterGenerator.exe
  (oder über Eingabeaufforderung)

Android:
  APK auf Android-Gerät installieren
  (Entwickleroptionen + "Unbekannte Quellen" erforderlich)

📋 HINWEISE:

• Alle Builds enthalten alle notwendigen Abhängigkeiten
• One-Directory Modus reduziert Antiviren-Probleme
• Linux/Windows: Gesamtes Verzeichnis kopieren (nicht nur die EXE)
• Android: APK direkt installierbar

🔧 BUILD-INFORMATIONEN:

Diese Builds wurden erstellt mit:
- build_all.py (Unified Build Script)
- PyInstaller (Linux/Windows Desktop)
- Buildozer + Python-for-Android (Android)
- Wine Cross-Compilation (Windows auf Linux)

Version: Siehe jeweilige README-Dateien in den Unterordnern
"""
    
    readme_file = dist_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📄 Dist README erstellt: {readme_file}")

def print_summary(dist_dir, results):
    """Druckt eine Zusammenfassung der Build-Ergebnisse"""
    print("\n" + "="*60)
    print("📊 BUILD-ZUSAMMENFASSUNG")
    print("="*60)
    
    total_builds = len(results)
    successful_builds = sum(results.values())
    
    print(f"Erfolgreiche Builds: {successful_builds}/{total_builds}")
    print()
    
    for platform, success in results.items():
        status = "✅ ERFOLGREICH" if success else "❌ FEHLGESCHLAGEN"
        print(f"{platform.upper():10} : {status}")
    
    print(f"\n📁 Alle Builds in: {dist_dir}")
    
    # Zeige Verzeichnisgrößen
    for subdir in ['linux', 'windows', 'android']:
        subdir_path = dist_dir / subdir
        if subdir_path.exists() and any(subdir_path.iterdir()):
            size_mb = get_dir_size(subdir_path)
            print(f"   {subdir}/: {size_mb:.1f} MB")
    
    if successful_builds == total_builds:
        print("\n🎉 ALLE BUILDS ERFOLGREICH!")
        print("Die Anwendung ist bereit für die Verteilung auf allen Plattformen.")
    else:
        print(f"\n⚠️  {total_builds - successful_builds} Build(s) fehlgeschlagen")
        print("Prüfe die Fehlermeldungen oben für Details.")

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

def main():
    """Hauptfunktion - Führt alle Builds aus"""
    print("🚀 SAVAGE WORLDS CHARAKTER GENERATOR - UNIFIED BUILD")
    print("Erstellt Builds für Linux, Windows (Wine) und Android")
    print("="*60)
    
    start_time = time.time()
    
    # Android-Config-Defaults setzen
    set_android_config_defaults()

    # Setup dist-Struktur
    dist_dir = setup_dist_structure()
    
    # Build-Ergebnisse verfolgen
    results = {}

    # Android Build
    print("\n⏳ Starte Android Build...")
    results['android'] = build_android(dist_dir)
    
    # README für dist-Ordner erstellen
    create_dist_readme(dist_dir)
    
    # Zusammenfassung
    end_time = time.time()
    duration = end_time - start_time
    
    print_summary(dist_dir, results)
    print(f"\n⏱️  Gesamtdauer: {duration:.1f} Sekunden")
    
    # Exit Code basierend auf Erfolg
    if all(results.values()):
        print("\n✨ Build-Prozess erfolgreich abgeschlossen!")
        return 0
    else:
        print("\n💥 Einige Builds sind fehlgeschlagen!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚡ Build durch Benutzer abgebrochen!")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unerwarteter Fehler: {e}")
        sys.exit(1)