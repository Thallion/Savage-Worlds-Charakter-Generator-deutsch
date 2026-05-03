
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

def get_version_from_git():
    """Liest die Version aus der letzten Git-Commit-Nachricht (z.B. '0.6.1.6')"""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%s'],
            capture_output=True, text=True, cwd=Path.cwd()
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            # Prüfe ob die Commit-Nachricht wie eine Versionsnummer aussieht
            parts = version.split('.')
            if len(parts) >= 3 and all(p.isdigit() for p in parts):
                return version
    except Exception as e:
        print(f"⚠️  Git-Version konnte nicht gelesen werden: {e}")
    return None

def get_version_from_spec():
    """Liest die Version aus buildozer.spec (Fallback)"""
    spec_file = Path.cwd() / "buildozer.spec"
    if spec_file.exists():
        with open(spec_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('version') and '=' in line and not line.startswith('version.'):
                    return line.split('=', 1)[1].strip()
    return None

def get_version():
    """Ermittelt die aktuelle Version (Git-Commit > buildozer.spec > None)"""
    return get_version_from_git() or get_version_from_spec()

def update_buildozer_spec_version(version):
    """Aktualisiert die Version in buildozer.spec"""
    spec_file = Path.cwd() / "buildozer.spec"
    if not spec_file.exists():
        return

    lines = spec_file.read_text(encoding='utf-8').splitlines(keepends=True)
    updated = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('version') and '=' in stripped and not stripped.startswith('version.'):
            old_version = stripped.split('=', 1)[1].strip()
            if old_version != version:
                lines[i] = f"version = {version}\n"
                updated = True
                break

    if updated:
        spec_file.write_text(''.join(lines), encoding='utf-8')
        print(f"📝 buildozer.spec Version aktualisiert: {old_version} → {version}")

def _load_config():
    """Lädt die aktuelle Config-Datei"""
    import json
    config_file = Path.cwd() / "config" / "app_config.json"
    config_data = {}
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"⚠️  Bestehende Config konnte nicht geladen werden: {e}")
    return config_data

def _save_config(config_data):
    """Speichert die Config-Datei"""
    import json
    config_dir = Path.cwd() / "config"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "app_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

def set_desktop_config_defaults():
    """Setzt Desktop-spezifische Config-Defaults (mobile_modus=false, show_logger=false)"""
    config_data = _load_config()
    config_data['mobile_modus'] = False
    config_data['show_logger'] = False
    config_data['force_mobile_layout'] = False
    _save_config(config_data)
    print(f"🖥️  Desktop-Defaults gesetzt: mobile_modus=false, show_logger=false, force_mobile_layout=false")

def set_android_config_defaults():
    """Setzt Android-spezifische Config-Defaults (mobile_modus=true, show_logger=false)"""
    config_data = _load_config()
    config_data['mobile_modus'] = True
    config_data['show_logger'] = False
    config_data['force_mobile_layout'] = True
    _save_config(config_data)
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

def build_linux(dist_dir):
    """Build Linux Binary"""
    print("\n" + "="*50)
    print("🐧 LINUX BUILD STARTEN")
    print("="*50)
    
    try:
        # Setze Umgebungsvariable, damit build_linux.py das dist/ nicht löscht
        env = os.environ.copy()
        env["SKIP_DIST_CLEANUP"] = "1"
        result = subprocess.run([sys.executable, "build_linux.py"], 
                              check=True, cwd=Path.cwd(), env=env)
        
        if result.returncode == 0:
            # Verschiebe Linux Build nach dist/linux/ SOFORT
            src_dir = Path.cwd() / "dist" / "SavageWorldsCharakterGenerator"
            target_dir = dist_dir / "linux" / "SavageWorldsCharakterGenerator"
            
            if src_dir.exists():
                # Stelle sicher dass linux Ordner existiert
                (dist_dir / "linux").mkdir(exist_ok=True)
                shutil.move(str(src_dir), str(target_dir))
                print(f"✅ Linux Build nach {target_dir} verschoben")
                return True
            else:
                print(f"❌ Linux Build-Verzeichnis nicht gefunden: {src_dir}")
                return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Linux Build fehlgeschlagen: {e}")
        return False
    
    return False

def build_windows(dist_dir):
    """Build Windows EXE via Wine"""
    print("\n" + "="*50)
    print("🍷 WINDOWS BUILD STARTEN (via Wine)")
    print("="*50)
    
    try:
        # Setze Umgebungsvariable, damit build_windows_wine.py das dist/ nicht löscht
        env = os.environ.copy()
        env["SKIP_DIST_CLEANUP"] = "1"
        result = subprocess.run([sys.executable, "build_windows_wine.py"], 
                              check=True, cwd=Path.cwd(), env=env)
        
        if result.returncode == 0:
            # Verschiebe Windows Build nach dist/windows/ SOFORT
            src_dir = Path.cwd() / "dist" / "SavageWorldsCharakterGenerator"
            target_dir = dist_dir / "windows" / "SavageWorldsCharakterGenerator"
            
            if src_dir.exists():
                # Stelle sicher dass windows Ordner existiert
                (dist_dir / "windows").mkdir(exist_ok=True)
                shutil.move(str(src_dir), str(target_dir))
                print(f"✅ Windows Build nach {target_dir} verschoben")
                return True
            else:
                print(f"❌ Windows Build-Verzeichnis nicht gefunden: {src_dir}")
                return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Windows Build fehlgeschlagen: {e}")
        return False
    
    return False

def ensure_java17():
    """Stellt sicher dass JAVA_HOME auf Java 17 zeigt (Gradle 8.0.2 braucht Java <= 20)"""
    java17_path = "/usr/lib/jvm/java-17-openjdk-amd64"
    if os.path.exists(java17_path):
        os.environ['JAVA_HOME'] = java17_path
        print(f"☕ JAVA_HOME gesetzt auf: {java17_path}")
    else:
        current = os.environ.get('JAVA_HOME', 'nicht gesetzt')
        print(f"⚠️  Java 17 nicht unter {java17_path} gefunden, verwende: {current}")

    # Gradle-Daemon stoppen (könnte mit falscher Java-Version laufen)
    gradlew = Path.cwd() / ".buildozer" / "android" / "platform" / "build-arm64-v8a" / "dists" / "savageworlds" / "gradlew"
    if gradlew.exists():
        subprocess.run([str(gradlew), '--stop'], cwd=gradlew.parent,
                      capture_output=True, timeout=30)
        print("🛑 Gradle-Daemon gestoppt")

    # Korrupten Script-Cache löschen
    gradle_script_cache = Path.home() / ".gradle" / "caches" / "8.0.2" / "scripts"
    if gradle_script_cache.exists():
        shutil.rmtree(gradle_script_cache, ignore_errors=True)
        print("🧹 Gradle Script-Cache bereinigt")


def _clean_android_bin(extensions=None):
    """Entfernt alte Build-Artefakte aus bin/"""
    if extensions is None:
        extensions = ["*.apk", "*.aab"]
    bin_dir = Path.cwd() / "bin"
    if bin_dir.exists():
        for ext in extensions:
            for old_file in bin_dir.glob(ext):
                old_file.unlink()
                print(f"🧹 Alte Datei entfernt: {old_file.name}")


def _prepare_android_build():
    """Gemeinsame Vorbereitung für Android-Builds (Cache + Fixes)"""
    # Nur App-Quellcode-Cache löschen (nicht die kompilierten Libraries!)
    # buildozer android clean würde auch pyjnius/kivy löschen, die dann
    # wegen Cython 3.x Inkompatibilität nicht neu kompilieren können.
    app_cache = Path.cwd() / ".buildozer" / "android" / "app"
    if app_cache.exists():
        shutil.rmtree(app_cache)
        print("🧹 App-Quellcode-Cache bereinigt (.buildozer/android/app/)")

    # Cython 3.x Fixes für pyjnius/kivy anwenden (falls Sources vorhanden)
    print("🔧 Wende Cython-Kompatibilitäts-Fixes an...")
    subprocess.run([sys.executable, 'build_fixes.py'], cwd=Path.cwd())


def _run_buildozer(build_command):
    """Führt Buildozer aus mit Retry-Logik für Cython-Fixes"""
    result = subprocess.run(['buildozer'] + build_command, cwd=Path.cwd())

    if result.returncode != 0:
        # Build fehlgeschlagen - Fixes erneut anwenden und nochmal versuchen.
        # Buildozer lädt beim ersten Lauf ggf. frische Quellen herunter,
        # die die Fixes überschreiben. Nach dem Download sind sie vorhanden.
        print("⚠️  Erster Build fehlgeschlagen - wende Fixes erneut an...")
        subprocess.run([sys.executable, 'build_fixes.py'], cwd=Path.cwd())
        result = subprocess.run(['buildozer'] + build_command, cwd=Path.cwd())

    return result.returncode == 0


def _find_apksigner():
    """Findet apksigner im Android SDK"""
    sdk_path = os.environ.get('ANDROID_SDK_ROOT') or os.environ.get('ANDROID_HOME')
    if not sdk_path:
        sdk_path = os.path.expanduser("~/Android/Sdk")

    build_tools = Path(sdk_path) / "build-tools"
    if build_tools.exists():
        # Neueste Version verwenden
        versions = sorted(build_tools.iterdir(), reverse=True)
        for v in versions:
            apksigner = v / "apksigner"
            if apksigner.exists():
                return str(apksigner)
    return None


def _sign_apk(apk_path):
    """Signiert eine APK mit dem Release-Keystore via apksigner"""
    keystore = Path.cwd() / "savageworlds-release.jks"
    if not keystore.exists():
        print("⚠️  Keystore nicht gefunden, APK bleibt debug-signiert")
        return False

    apksigner = _find_apksigner()
    if not apksigner:
        print("⚠️  apksigner nicht gefunden, APK bleibt debug-signiert")
        return False

    # Erst zipalign (muss VOR dem Signieren passieren)
    sdk_path = os.environ.get('ANDROID_SDK_ROOT') or os.path.expanduser("~/Android/Sdk")
    zipalign = None
    for v in sorted(Path(sdk_path, "build-tools").iterdir(), reverse=True):
        za = v / "zipalign"
        if za.exists():
            zipalign = str(za)
            break

    if zipalign:
        aligned_path = str(apk_path) + ".aligned"
        result = subprocess.run(
            [zipalign, '-f', '4', str(apk_path), aligned_path],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            shutil.move(aligned_path, str(apk_path))
            print(f"📐 APK aligned: {Path(apk_path).name}")
        else:
            print(f"⚠️  zipalign fehlgeschlagen: {result.stderr}")

    # Signieren mit apksigner
    result = subprocess.run([
        apksigner, 'sign',
        '--ks', str(keystore),
        '--ks-key-alias', 'savageworlds',
        '--ks-pass', 'pass:savage2026',
        '--key-pass', 'pass:savage2026',
        str(apk_path)
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"🔐 APK signiert: {Path(apk_path).name}")
        return True
    else:
        print(f"❌ APK-Signierung fehlgeschlagen: {result.stderr}")
        return False


def _sign_aab(aab_path):
    """Signiert eine AAB mit dem Release-Keystore via jarsigner"""
    keystore = Path.cwd() / "savageworlds-release.jks"
    if not keystore.exists():
        print("⚠️  Keystore nicht gefunden, AAB bleibt unsigniert")
        return False

    result = subprocess.run([
        'jarsigner',
        '-sigalg', 'SHA256withRSA',
        '-digestalg', 'SHA-256',
        '-keystore', str(keystore),
        '-storepass', 'savage2026',
        '-keypass', 'savage2026',
        str(aab_path),
        'savageworlds'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"🔐 AAB signiert: {Path(aab_path).name}")
        return True
    else:
        print(f"❌ AAB-Signierung fehlgeschlagen: {result.stderr}")
        return False


def _verify_signature(artifact_path):
    """Verifiziert die Signatur eines APK/AAB"""
    suffix = Path(artifact_path).suffix

    if suffix == '.aab':
        # AAB mit jarsigner verifizieren
        result = subprocess.run(
            ['jarsigner', '-verify', str(artifact_path)],
            capture_output=True, text=True
        )
        if result.returncode == 0 and 'jar verified' in result.stdout:
            print(f"✅ Signatur verifiziert: {Path(artifact_path).name}")
        else:
            print(f"⚠️  AAB nicht signiert: {Path(artifact_path).name}")
    else:
        # APK mit apksigner verifizieren
        apksigner = _find_apksigner()
        if not apksigner:
            return
        result = subprocess.run(
            [apksigner, 'verify', '--verbose', str(artifact_path)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ Signatur verifiziert: {Path(artifact_path).name}")
        else:
            print(f"⚠️  Signatur-Verifizierung fehlgeschlagen: {Path(artifact_path).name}")


def _collect_android_artifacts(dist_dir, extensions, build_type_label):
    """Sammelt Build-Artefakte aus bin/ und kopiert sie nach dist/android/"""
    bin_dir = Path.cwd() / "bin"
    version = get_version()
    found = False

    (dist_dir / "android").mkdir(exist_ok=True)

    for ext in extensions:
        for artifact in bin_dir.glob(ext):
            suffix = artifact.suffix  # .apk oder .aab
            if version:
                new_name = f"SavageWorldsCharGen-v{version}-{build_type_label}{suffix}"
            else:
                new_name = artifact.name
            target_file = dist_dir / "android" / new_name
            shutil.copy2(artifact, target_file)
            print(f"✅ {suffix.upper()[1:]} nach {target_file} kopiert")

            # Signieren
            if suffix == '.apk':
                _sign_apk(target_file)
            elif suffix == '.aab':
                _sign_aab(target_file)

            # Signatur verifizieren
            _verify_signature(target_file)

            found = True

    return found


def build_android(dist_dir):
    """Build Android APK (debug) und AAB (release) mit Buildozer"""
    print("\n" + "="*50)
    print("🤖 ANDROID BUILD STARTEN (APK + AAB)")
    print("="*50)

    # Java 17 sicherstellen (Gradle 8.0.2 ist inkompatibel mit Java 21)
    ensure_java17()

    # Falls 16-KB-Patch neuer als kompilierte Libs: Library-Cache leeren,
    # damit p4a alle 64-Bit-.so neu mit -Wl,-z,max-page-size=16384 linkt.
    try:
        from build_android import maybe_clean_lib_cache_for_16kb_rebuild
        maybe_clean_lib_cache_for_16kb_rebuild()
    except Exception as e:
        print(f"⚠️  16-KB-Cache-Cleanup übersprungen: {e}")

    try:
        # Prüfe Buildozer Installation
        result = subprocess.run(['buildozer', '--version'],
                              capture_output=True, text=True)
        print(f"Buildozer Version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Buildozer nicht gefunden! Installiere mit: pip install buildozer")
        return False

    apk_ok = False
    aab_ok = False

    # --- 1. Debug APK bauen ---
    print("\n" + "-"*40)
    print("📦 Debug APK bauen...")
    print("-"*40)
    _clean_android_bin(["*.apk"])
    _prepare_android_build()

    if _run_buildozer(['android', 'debug']):
        apk_ok = _collect_android_artifacts(dist_dir, ["*.apk"], "debug")
        if not apk_ok:
            print("❌ Keine APK-Datei gefunden in bin/")
    else:
        print("❌ Debug APK Build fehlgeschlagen")

    # --- 2. Release AAB bauen (für Play Store) ---
    print("\n" + "-"*40)
    print("📦 Release AAB bauen (Play Store)...")
    print("-"*40)
    _clean_android_bin(["*.aab"])
    _prepare_android_build()

    if _run_buildozer(['android', 'release']):
        aab_ok = _collect_android_artifacts(dist_dir, ["*.aab"], "release")
        if not aab_ok:
            print("❌ Keine AAB-Datei gefunden in bin/")
    else:
        print("❌ Release AAB Build fehlgeschlagen")

    # Kopiere buildozer.spec für Referenz
    spec_file = Path.cwd() / "buildozer.spec"
    if spec_file.exists():
        (dist_dir / "android").mkdir(exist_ok=True)
        shutil.copy2(spec_file, dist_dir / "android" / "buildozer.spec")

    # 16 KB Page Size Alignment verifizieren (Google Play Pflicht 64-Bit)
    if apk_ok or aab_ok:
        try:
            from build_fixes import verify_so_alignment
            verify_so_alignment()
        except Exception as e:
            print(f"⚠️  Alignment-Verifikation fehlgeschlagen: {e}")

    if apk_ok and aab_ok:
        print("\n✅ Beide Android-Artefakte erstellt (APK + AAB)")
    elif apk_ok or aab_ok:
        print(f"\n⚠️  Nur {'APK' if apk_ok else 'AAB'} erstellt")

    return apk_ok or aab_ok

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
    ├── *-debug.apk                       # Android APK (Debug/Sideloading)
    ├── *-release.aab                     # Android AAB (Google Play Store)
    └── buildozer.spec                    # Build-Konfiguration (Referenz)

🚀 AUSFÜHRUNG:

Linux:
  cd linux/SavageWorldsCharakterGenerator
  ./run.sh

Windows:
  Doppelklick auf SavageWorldsCharakterGenerator.exe
  (oder über Eingabeaufforderung)

Android (Debug APK):
  APK auf Android-Gerät installieren
  (Entwickleroptionen + "Unbekannte Quellen" erforderlich)

Android (Play Store AAB):
  AAB-Datei über die Google Play Console hochladen
  (Muss vor Upload mit einem Keystore signiert werden)

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

    # Version aus Git ermitteln und buildozer.spec aktualisieren
    version = get_version()
    if version:
        print(f"📌 Aktuelle Version: {version}")
        update_buildozer_spec_version(version)
    else:
        print("⚠️  Keine Version ermittelt — verwende bestehende buildozer.spec Version")

    # Setup dist-Struktur
    dist_dir = setup_dist_structure()

    # Build-Ergebnisse verfolgen
    results = {}

    # Linux Build (Desktop-Defaults)
    print("\n⏳ Starte Linux Build...")
    set_desktop_config_defaults()
    results['linux'] = build_linux(dist_dir)

    # Windows Build via Wine (Desktop-Defaults)
    print("\n⏳ Starte Windows Build...")
    set_desktop_config_defaults()
    results['windows'] = build_windows(dist_dir)

    # Android Build (Android-Defaults)
    print("\n⏳ Starte Android Build...")
    set_android_config_defaults()
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