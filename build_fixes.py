#!/usr/bin/env python3
"""
Combined buildozer hook to fix Kivy and PyJNIus Python 3+ / Cython 3.x compatibility issues.

Zusätzlich: 16 KB Page Size Alignment für Android (Google Play Pflicht ab 31.05.2026
für Updates / 01.11.2025 für neue Apps; gilt nur für 64-Bit Libraries).
Patches: pythonforandroid/archs.py common_ldflags und SDL2-Bootstrap Application.mk.

Zusätzlich: Predictive-Back-Opt-out für targetSdk 36 (Android 16) —
android:enableOnBackInvokedCallback="false" im <application>-Tag, damit
SDL2/Kivy weiterhin KEYCODE_BACK erhalten (Zurück-Taste schließt Popups).

Zusätzlich: Große Displays (Android 16, Tablets/Foldables) —
android:resizeableActivity="true" im <application>-Tag und Entfernen der
setRequestedOrientation()-Aufrufe aus PythonActivity.UnpackFilesTask
(von Google Play als "Einschränkung für Größenänderung und Ausrichtung" gemeldet).

Wird automatisch von build_android.py / build_all.py aufgerufen, BEVOR buildozer startet.
Kann auch manuell ausgeführt werden: python build_fixes.py
"""
import os
import subprocess
import sys
import re
from pathlib import Path

# Marker, der idempotente Patches kennzeichnet — verhindert Doppelpatches
# bei wiederholtem Hook-Aufruf (vor und nach p4a-Source-Download).
PAGE_SIZE_FIX_MARKER = "16KB-PAGE-SIZE-FIX"


def _find_build_root():
    """Findet das Build-Verzeichnis dynamisch (Single- oder Multi-Arch)"""
    platform_dir = Path(".buildozer/android/platform")
    if not platform_dir.exists():
        return None
    # Suche nach build-* Verzeichnissen (z.B. build-arm64-v8a, build-arm64-v8a_armeabi-v7a)
    for build_dir in sorted(platform_dir.glob("build-*/build/other_builds"), reverse=True):
        if build_dir.exists():
            print(f"P4A Hook: Build-Verzeichnis gefunden: {build_dir.parent.parent.name}")
            return build_dir
    return None


def fix_kivy_python3_compatibility():
    """Fix Python 3+ / Cython 3.x compatibility issues in ALL Kivy .pyx files"""
    print("P4A Hook: Searching for Kivy build directories...")

    # Find kivy build directories
    build_root = _find_build_root()
    if not build_root:
        print("P4A Hook: Build directory not found, skipping Kivy fix")
        return False

    kivy_dirs = list(build_root.glob("kivy*/*/kivy"))
    if not kivy_dirs:
        print("P4A Hook: No kivy directories found, skipping Kivy fix")
        return False

    fixed_any = False

    for kivy_dir in kivy_dirs:
        print(f"P4A Hook: Checking kivy directory: {kivy_dir}")

        # Alle .pyx UND .pxi Dateien rekursiv durchsuchen
        pyx_files = list(kivy_dir.rglob("*.pyx")) + list(kivy_dir.rglob("*.pxi"))

        for pyx_file in pyx_files:
            try:
                with open(pyx_file, 'r') as f:
                    content = f.read()

                original = content

                # === Fix 1: __long__ Methode komplett entfernen ===
                content = re.sub(
                    r'\n    def __long__\(self\):.*?(?=\n    def |\n    @|\nclass |\Z)',
                    '',
                    content,
                    flags=re.DOTALL
                )

                # === Fix 2: long() Funktionsaufrufe → int() ===
                # Matcht long(...) als Python-Funktionsaufruf, NICHT C-Typen wie "long long"
                # Fälle: "= long(", "(long(", " long(", Zeilenanfang "long("
                content = re.sub(r'(?<!\w)long\(', 'int(', content)

                # === Fix 3: isinstance mit long ===
                content = re.sub(
                    r'isinstance\((\w+),\s*\(int,\s*long\)\)',
                    r'isinstance(\1, int)',
                    content
                )
                content = re.sub(
                    r'isinstance\((\w+),\s*\(long,\s*int\)\)',
                    r'isinstance(\1, int)',
                    content
                )
                content = re.sub(
                    r'isinstance\((\w+),\s*long\)',
                    r'isinstance(\1, int)',
                    content
                )

                # === Fix 4: (int, long) und (long, int) Tuples → (int,) ===
                content = content.replace("(int, long)", "(int,)")
                content = content.replace("(long, int)", "(int,)")

                # === Fix 5: , long) am Ende von Tuples ===
                # Aber NICHT "long long" (C-Typ)
                content = re.sub(r',\s*long\)', ')', content)

                # === Fix 6: Alleinstehende long-Referenzen in Python-Kontext ===
                # z.B. "long:" in Dicts, "== long", "is long"
                content = content.replace("long: 'J',", "int: 'J',")
                content = content.replace("long: 'J'", "int: 'J'")
                content = re.sub(r'==\s*long\b', '== int', content)
                content = re.sub(r'\bis\s+long\b', 'is int', content)

                if content != original:
                    with open(pyx_file, 'w') as f:
                        f.write(content)
                    print(f"P4A Hook: Fixed Kivy file {pyx_file.name}")
                    fixed_any = True

            except Exception as e:
                print(f"P4A Hook: Error fixing Kivy file {pyx_file}: {e}")

    if not fixed_any:
        print("P4A Hook: Kivy files already appear to be fixed")

    return fixed_any


def fix_android_manifest_fileprovider():
    """Fügt FileProvider-Deklaration in AndroidManifest.xml ein (für Datei-Versenden)."""
    print("P4A Hook: Checking AndroidManifest.xml for FileProvider...")

    platform_dir = Path(".buildozer/android/platform")
    if not platform_dir.exists():
        print("P4A Hook: Platform directory not found, skipping FileProvider fix")
        return False

    # AndroidManifest.xml in allen Build-Verzeichnissen suchen
    # python-for-android legt das Manifest je nach Version an verschiedenen Pfaden ab
    manifest_files = list(platform_dir.glob("build-*/dists/*/src/main/AndroidManifest.xml"))
    if not manifest_files:
        manifest_files = list(platform_dir.glob("build-*/dists/*/AndroidManifest.xml"))
    if not manifest_files:
        # Neuere p4a-Versionen: Manifest liegt direkt im Gradle-Build
        manifest_files = list(platform_dir.glob("build-*/dists/*/templates/AndroidManifest.xml"))
    if not manifest_files:
        # Breitere Suche als letzter Versuch
        manifest_files = [
            p for p in platform_dir.glob("**/AndroidManifest.xml")
            if 'build' in str(p) and '.buildozer' in str(p)
        ]

    if not manifest_files:
        print("P4A Hook: No AndroidManifest.xml found, skipping FileProvider fix")
        return False

    fileprovider_xml = '''
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>'''

    # Pattern für fehlerhaft als String-Attribut injizierte FileProvider-Deklaration
    # (p4a fügt extra_manifest_application_arguments manchmal als quoted String in das <application>-Tag ein)
    broken_pattern = re.compile(
        r'\s*"<provider\s.*?FileProvider.*?</provider>\s*"',
        re.DOTALL
    )

    fixed_any = False
    for manifest_file in manifest_files:
        try:
            with open(manifest_file, 'r') as f:
                content = f.read()

            # Zuerst: Fehlerhaft injizierte String-Deklaration entfernen
            if broken_pattern.search(content):
                content = broken_pattern.sub('', content)
                print(f"P4A Hook: Removed broken FileProvider string injection from {manifest_file.name}")
                # Datei sofort schreiben, damit der korrekte Check folgen kann
                with open(manifest_file, 'w') as f:
                    f.write(content)

            if 'FileProvider' in content:
                print(f"P4A Hook: FileProvider already present in {manifest_file.name}")
                continue

            # Vor </application> einfügen
            if '</application>' in content:
                content = content.replace(
                    '</application>',
                    f'{fileprovider_xml}\n    </application>'
                )
                with open(manifest_file, 'w') as f:
                    f.write(content)
                print(f"P4A Hook: FileProvider added to {manifest_file}")
                fixed_any = True
            else:
                print(f"P4A Hook: </application> not found in {manifest_file}")

        except Exception as e:
            print(f"P4A Hook: Error fixing manifest {manifest_file}: {e}")

    return fixed_any


def _find_manifest_files():
    """Sammelt alle AndroidManifest-Kandidaten: gerenderte Manifeste in den
    Build-/Dist-Verzeichnissen UND die p4a-Templates (AndroidManifest.tmpl.xml),
    aus denen p4a das Manifest bei jedem Build neu rendert.

    Templates mitzupatchen ist wichtig: Patches nur am gerenderten Manifest
    gehen bei einem Re-Render verloren.
    """
    manifest_files = []

    # 1) p4a-Bootstrap-Templates (venv + buildozer-extrahierte Kopie)
    for p4a_dir in _find_all_pythonforandroid_dirs():
        for tmpl in [
            p4a_dir / "bootstraps" / "sdl2" / "build" / "templates" / "AndroidManifest.tmpl.xml",
            p4a_dir / "bootstraps" / "common" / "build" / "templates" / "AndroidManifest.tmpl.xml",
        ]:
            if tmpl.exists():
                manifest_files.append(tmpl)

    platform_dir = Path(".buildozer/android/platform")
    if platform_dir.exists():
        # 2) Templates, die bereits in die Dists kopiert wurden
        manifest_files += list(platform_dir.glob("build-*/dists/*/templates/AndroidManifest.tmpl.xml"))
        # 3) Gerenderte Manifeste (verschiedene p4a-Versionen, verschiedene Pfade)
        manifest_files += list(platform_dir.glob("build-*/dists/*/src/main/AndroidManifest.xml"))
        manifest_files += list(platform_dir.glob("build-*/dists/*/AndroidManifest.xml"))

    # Duplikate (Symlinks/mehrfache Globs) entfernen
    seen = set()
    unique = []
    for f in manifest_files:
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(f)
    return unique


def fix_android_manifest_predictive_back():
    """Injiziert android:enableOnBackInvokedCallback="false" in das
    <application>-Tag des AndroidManifest.xml (und der p4a-Templates).

    Hintergrund: Ab targetSdk 36 (Android 16) ist "Predictive Back"
    standardmäßig aktiviert. Das System liefert dann KEIN KEYCODE_BACK
    mehr an die Activity — SDL2/Kivy sehen die Zurück-Taste/-Geste nicht
    mehr (kein ESC-Event, Popups mit auto_dismiss schließen nicht, die
    App wird stattdessen sofort minimiert). Da SDL2 keinen
    OnBackInvokedCallback registriert, ist der Manifest-Opt-out der
    einzige Weg, das bisherige Back-Verhalten zu erhalten.

    Idempotent: Attribut wird nur eingefügt, wenn es noch fehlt.
    """
    print("P4A Hook: Checking AndroidManifest for predictive-back opt-out...")

    manifest_files = _find_manifest_files()
    if not manifest_files:
        print("P4A Hook: No AndroidManifest files found, skipping predictive-back fix")
        return False

    fixed_any = False
    for manifest_file in manifest_files:
        try:
            with open(manifest_file, 'r') as f:
                content = f.read()

            if 'enableOnBackInvokedCallback' in content:
                print(f"P4A Hook: predictive-back opt-out already present in {manifest_file}")
                continue

            new_content, count = re.subn(
                r'<application\b',
                '<application android:enableOnBackInvokedCallback="false"',
                content,
                count=1,
            )
            if count == 0:
                print(f"P4A Hook: <application> tag not found in {manifest_file}")
                continue

            with open(manifest_file, 'w') as f:
                f.write(new_content)
            print(f"P4A Hook: predictive-back opt-out added to {manifest_file}")
            fixed_any = True

        except Exception as e:
            print(f"P4A Hook: Error fixing manifest {manifest_file}: {e}")

    if not fixed_any:
        print("P4A Hook: All manifests already have the predictive-back opt-out")

    return fixed_any


def fix_android_manifest_large_screens():
    """Deklariert die App explizit als frei skalierbar:
    android:resizeableActivity="true" im <application>-Tag.

    Hintergrund: Ab Android 16 ignoriert das System auf großen Displays
    (Tablets, Foldables) Einschränkungen für Größenänderung und Ausrichtung.
    Die p4a-Manifest-Vorlage setzt `resizeableActivity` gar nicht — der
    Default (true ab targetSdk 24) greift zwar, aber die Play-Console-Prüfung
    und Multi-Window-/Freeform-Modi bewerten die explizite Deklaration.

    Idempotent: Attribut wird nur eingefügt, wenn es noch fehlt.
    """
    print("P4A Hook: Checking AndroidManifest for resizeableActivity...")

    manifest_files = _find_manifest_files()
    if not manifest_files:
        print("P4A Hook: No AndroidManifest files found, skipping large-screen fix")
        return False

    fixed_any = False
    for manifest_file in manifest_files:
        try:
            with open(manifest_file, 'r') as f:
                content = f.read()

            if 'resizeableActivity' in content:
                print(f"P4A Hook: resizeableActivity already present in {manifest_file}")
                continue

            new_content, count = re.subn(
                r'<application\b',
                '<application android:resizeableActivity="true"',
                content,
                count=1,
            )
            if count == 0:
                print(f"P4A Hook: <application> tag not found in {manifest_file}")
                continue

            with open(manifest_file, 'w') as f:
                f.write(new_content)
            print(f"P4A Hook: resizeableActivity=true added to {manifest_file}")
            fixed_any = True

        except Exception as e:
            print(f"P4A Hook: Error fixing manifest {manifest_file}: {e}")

    if not fixed_any:
        print("P4A Hook: All manifests already declare resizeableActivity")

    return fixed_any


# Der Kivy-Launcher-Pfad in PythonActivity.UnpackFilesTask.onPostExecute erzwingt
# per setRequestedOrientation() Landscape bzw. Portrait. Google Play meldet genau
# diese Stelle als "Einschränkung für die Größenänderung und Ausrichtung".
_LAUNCHER_ORIENTATION_BLOCK_RE = re.compile(
    r'[ \t]*if \(p != null\) \{\s*'
    r'if \(p\.landscape\) \{\s*'
    r'setRequestedOrientation\(ActivityInfo\.SCREEN_ORIENTATION_LANDSCAPE\);\s*'
    r'\} else \{\s*'
    r'setRequestedOrientation\(ActivityInfo\.SCREEN_ORIENTATION_PORTRAIT\);\s*'
    r'\}\s*'
    r'\}[ \t]*\n'
)

LARGE_SCREEN_FIX_MARKER = "LARGE-SCREEN-FIX"

_LAUNCHER_ORIENTATION_REPLACEMENT = (
    f"                // {LARGE_SCREEN_FIX_MARKER}: setRequestedOrientation() entfernt.\n"
    "                // Google Play meldet diesen Kivy-Launcher-Pfad als\n"
    "                // \"Einschränkung für Größenänderung und Ausrichtung\"; ab Android 16\n"
    "                // wird er auf großen Displays ohnehin ignoriert. Die Ausrichtung\n"
    "                // steuern ausschließlich android:screenOrientation (fullUser) und\n"
    "                // die App-Einstellung in views/app_navigation_mixin.py.\n"
)


def _find_python_activity_files():
    """Sammelt alle PythonActivity.java-Kandidaten: p4a-Bootstrap-Quellen UND
    bereits nach bootstrap_builds/dists kopierte Fassungen.

    Die Bootstrap-Quelle mitzupatchen ist wichtig: ein Patch nur in der Dist
    geht verloren, sobald p4a die Dist neu erzeugt (`buildozer android clean`).
    """
    java_files = []

    # 1) p4a-Bootstrap-Quellen (venv + buildozer-extrahierte Kopie)
    for p4a_dir in _find_all_pythonforandroid_dirs():
        java_files += list(
            (p4a_dir / "bootstraps").glob(
                "*/build/src/main/java/org/kivy/android/PythonActivity.java"
            )
        )

    platform_dir = Path(".buildozer/android/platform")
    if platform_dir.exists():
        # 2) Zwischenstände der Bootstrap-Builds
        java_files += list(platform_dir.glob(
            "build-*/build/bootstrap_builds/*/src/main/java/org/kivy/android/PythonActivity.java"
        ))
        # 3) Fertige Dists (das, was tatsächlich kompiliert wird)
        java_files += list(platform_dir.glob(
            "build-*/dists/*/src/main/java/org/kivy/android/PythonActivity.java"
        ))

    # Duplikate (Symlinks/mehrfache Globs) entfernen
    seen = set()
    unique = []
    for f in java_files:
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(f)
    return unique


def fix_p4a_activity_orientation_restriction():
    """Entfernt die setRequestedOrientation()-Aufrufe aus
    PythonActivity.UnpackFilesTask.onPostExecute.

    Hintergrund: Google Play meldet für die App eine "Einschränkung für die
    Größenänderung und Ausrichtung" in
    `org.kivy.android.PythonActivity$UnpackFilesTask.onPostExecute`. Der Block
    stammt aus dem alten Kivy-Launcher (er greift nur bei einem Intent mit
    Action `org.kivy.LAUNCH`) und ist für eine eigenständige App toter Code —
    die statische Analyse von Play sieht ihn trotzdem.

    Idempotent: erkennt den bereits gepatchten Zustand am Marker.
    """
    print("P4A Hook: Checking PythonActivity.java for orientation restrictions...")

    java_files = _find_python_activity_files()
    if not java_files:
        print("P4A Hook: No PythonActivity.java found, skipping orientation fix")
        return False

    fixed_any = False
    for java_file in java_files:
        try:
            with open(java_file, 'r') as f:
                content = f.read()

            if LARGE_SCREEN_FIX_MARKER in content:
                print(f"P4A Hook: orientation restriction already removed in {java_file}")
                continue

            new_content, count = _LAUNCHER_ORIENTATION_BLOCK_RE.subn(
                _LAUNCHER_ORIENTATION_REPLACEMENT, content, count=1
            )
            if count == 0:
                if 'setRequestedOrientation' in content:
                    print(
                        f"P4A Hook: WARNUNG — setRequestedOrientation in {java_file} "
                        "gefunden, aber Block-Muster passt nicht (p4a-Version geändert?)"
                    )
                else:
                    print(f"P4A Hook: no orientation restriction in {java_file}")
                continue

            with open(java_file, 'w') as f:
                f.write(new_content)
            print(f"P4A Hook: orientation restriction removed from {java_file}")
            fixed_any = True

        except Exception as e:
            print(f"P4A Hook: Error fixing {java_file}: {e}")

    if not fixed_any:
        print("P4A Hook: All PythonActivity.java files are already free of orientation locks")

    return fixed_any


def fix_pyjnius_python3_compatibility():
    """Fix Python 3+ / Cython 3.x compatibility issues in ALL pyjnius .pxi files"""
    print("P4A Hook: Searching for pyjnius build directories...")

    build_root = _find_build_root()
    if not build_root:
        print("P4A Hook: Build directory not found, skipping pyjnius fix")
        return False

    pyjnius_dirs = list(build_root.glob("pyjnius*/*/pyjnius"))
    if not pyjnius_dirs:
        print("P4A Hook: No pyjnius directories found, skipping pyjnius fix")
        return False

    fixed_any = False

    for pyjnius_dir in pyjnius_dirs:
        jnius_dir = pyjnius_dir / "jnius"
        if not jnius_dir.exists():
            print(f"P4A Hook: jnius/ Verzeichnis nicht gefunden in {pyjnius_dir}")
            continue

        # Alle .pxi UND .pyx Dateien im jnius-Verzeichnis fixen
        pxi_files = list(jnius_dir.glob("*.pxi")) + list(jnius_dir.glob("*.pyx"))

        for pxi_file in pxi_files:
            try:
                with open(pxi_file, 'r') as f:
                    content = f.read()

                original = content

                # === Fix 1: isinstance(arg, long) → isinstance(arg, int) ===
                content = content.replace("isinstance(arg, long)", "isinstance(arg, int)")
                content = content.replace("isinstance(obj, long)", "isinstance(obj, int)")

                # === Fix 2: (int, long) Tuples → (int,) ===
                content = content.replace("(int, long)", "(int,)")
                content = content.replace("(long, int)", "(int,)")

                # === Fix 3: isinstance(py_arg, (int, long)) → isinstance(py_arg, int) ===
                # Fängt auch Fälle wie "isinstance(py_arg, (int, long)):" ab
                content = re.sub(
                    r'isinstance\((\w+),\s*\(int,\s*long\)\)',
                    r'isinstance(\1, int)',
                    content
                )
                content = re.sub(
                    r'isinstance\((\w+),\s*\(long,\s*int\)\)',
                    r'isinstance(\1, int)',
                    content
                )

                # === Fix 4: long: 'J' → int: 'J' (in Dicts) ===
                content = content.replace("long: 'J',", "int: 'J',")
                content = content.replace("long: 'J'", "int: 'J'")

                # === Fix 5: tp == long → tp == int ===
                content = content.replace("tp == long)", "tp == int)")
                content = content.replace("tp == long ", "tp == int ")

                # === Fix 6: , long) am Ende von Tuples ===
                # Aber NICHT "long long" (C-Typ) oder "long unsigned" (C-Typ)
                content = re.sub(r',\s*long\)', ')', content)

                if content != original:
                    with open(pxi_file, 'w') as f:
                        f.write(content)
                    print(f"P4A Hook: Fixed Python 3+ compatibility in {pxi_file.name}")
                    fixed_any = True

            except Exception as e:
                print(f"P4A Hook: Error fixing {pxi_file}: {e}")

    if not fixed_any:
        print("P4A Hook: pyjnius files already appear to be fixed")

    return fixed_any


def _find_pythonforandroid_dir():
    """Findet das installierte python-for-android Paket (im venv oder global)."""
    try:
        import pythonforandroid
        return Path(pythonforandroid.__file__).parent
    except ImportError:
        # Fallback: in lokalen venv-Pfaden suchen
        for candidate in [
            Path("venv/lib/python3.12/site-packages/pythonforandroid"),
            Path("venv/lib/python3.11/site-packages/pythonforandroid"),
            Path(".buildozer/android/platform/python-for-android/pythonforandroid"),
        ]:
            if candidate.exists():
                return candidate
        return None


def _find_all_pythonforandroid_dirs():
    """Liefert ALLE p4a-Installationen, die wir patchen müssen.

    Buildozer extrahiert eine eigene Kopie nach
    `.buildozer/android/platform/python-for-android/`, die NICHT mit der
    venv-Installation identisch ist. Beide brauchen den Patch, da `prebuild_arch`
    aus dem extrahierten Pfad kopiert.
    """
    dirs = []
    seen = set()

    # Primär: venv / sys.path (über Import)
    primary = _find_pythonforandroid_dir()
    if primary is not None and primary.exists():
        resolved = primary.resolve()
        if resolved not in seen:
            dirs.append(primary)
            seen.add(resolved)

    # Sekundär: buildozer-extrahiertes p4a (das ist, was tatsächlich gebaut wird)
    buildozer_p4a = Path(".buildozer/android/platform/python-for-android/pythonforandroid")
    if buildozer_p4a.exists():
        resolved = buildozer_p4a.resolve()
        if resolved not in seen:
            dirs.append(buildozer_p4a)
            seen.add(resolved)

    # Tertiär: weitere venv-Pfade als Sicherheitsnetz
    for candidate in [
        Path("venv/lib/python3.12/site-packages/pythonforandroid"),
        Path("venv/lib/python3.11/site-packages/pythonforandroid"),
    ]:
        if candidate.exists():
            resolved = candidate.resolve()
            if resolved not in seen:
                dirs.append(candidate)
                seen.add(resolved)

    return dirs


def fix_p4a_ldflags_for_16kb_alignment():
    """Patcht pythonforandroid/archs.py so, dass alle p4a-Recipes mit
    16 KB Alignment Linker-Flags gebaut werden.

    Hintergrund: p4a setzt LDFLAGS in archs.py:Arch.get_env() neu und ignoriert
    LDFLAGS aus os.environ. Der einzige zuverlässige Weg, allen Recipes einen
    Linker-Flag mitzugeben, ist die `common_ldflags` Liste.

    Der Flag `-Wl,-z,max-page-size=16384` wirkt nur beim 64-Bit-Linker; bei
    armeabi-v7a (32-Bit) ist er harmlos / wird ignoriert.
    """
    print("P4A Hook: Applying 16 KB page-size LDFLAGS to p4a archs.py...")

    p4a_dir = _find_pythonforandroid_dir()
    if p4a_dir is None:
        print("P4A Hook: pythonforandroid not found, skipping 16 KB LDFLAGS fix")
        return False

    archs_file = p4a_dir / "archs.py"
    if not archs_file.exists():
        print(f"P4A Hook: {archs_file} not found, skipping")
        return False

    try:
        content = archs_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"P4A Hook: Cannot read {archs_file}: {e}")
        return False

    if PAGE_SIZE_FIX_MARKER in content:
        print("P4A Hook: archs.py already patched for 16 KB alignment")
        return False

    # Original: common_ldflags = ['-L{ctx_libs_dir}']
    pattern = re.compile(
        r"common_ldflags\s*=\s*\['-L\{ctx_libs_dir\}'\]",
        re.MULTILINE,
    )
    replacement = (
        "common_ldflags = ['-L{ctx_libs_dir}', "
        "'-Wl,-z,max-page-size=16384', "
        "'-Wl,-z,common-page-size=16384']  # " + PAGE_SIZE_FIX_MARKER
    )

    new_content, count = pattern.subn(replacement, content, count=1)
    if count == 0:
        print(f"P4A Hook: common_ldflags pattern not found in {archs_file}")
        return False

    try:
        archs_file.write_text(new_content, encoding="utf-8")
        print(f"P4A Hook: 16 KB LDFLAGS injected into {archs_file}")
        return True
    except Exception as e:
        print(f"P4A Hook: Cannot write {archs_file}: {e}")
        return False


def _patch_application_mk(mk_file: Path) -> bool:
    """Fügt 16 KB Alignment APP_LDFLAGS in eine Application.mk ein. Idempotent."""
    try:
        content = mk_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"P4A Hook: Cannot read {mk_file}: {e}")
        return False

    if PAGE_SIZE_FIX_MARKER in content:
        return False  # Bereits gepatcht

    snippet = (
        "\n# " + PAGE_SIZE_FIX_MARKER + "\n"
        "ifneq ($(filter arm64-v8a x86_64,$(APP_ABI)),)\n"
        "APP_LDFLAGS += -Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384\n"
        "endif\n"
    )

    # Anhängen reicht — Application.mk ist klein und alle Direktiven sind global
    new_content = content.rstrip() + "\n" + snippet

    try:
        mk_file.write_text(new_content, encoding="utf-8")
        print(f"P4A Hook: 16 KB APP_LDFLAGS appended to {mk_file}")
        return True
    except Exception as e:
        print(f"P4A Hook: Cannot write {mk_file}: {e}")
        return False


def fix_sdl2_bootstrap_16kb_alignment():
    """Patcht Application.mk in SDL2-Bootstrap für 16 KB Alignment der
    via ndk-build gebauten Libraries (libSDL2*, libmain).

    Diese Bibliotheken sehen die p4a-`LDFLAGS` (siehe archs.py-Patch) NICHT,
    weil sie über Android `ndk-build` linken. Sie brauchen `APP_LDFLAGS`
    direkt in der Bootstrap Application.mk.
    """
    print("P4A Hook: Patching SDL2 bootstrap Application.mk for 16 KB alignment...")

    fixed_any = False

    # 1) ALLE p4a-Source-Standorte (venv + buildozer-extrahiert)
    # Buildozer extrahiert eine eigene p4a-Kopie, aus der `prebuild_arch`
    # die Bootstrap-Dateien in den Build-Dir kopiert. BEIDE müssen gepatcht sein.
    for p4a_dir in _find_all_pythonforandroid_dirs():
        src_mk = p4a_dir / "bootstraps" / "sdl2" / "build" / "jni" / "Application.mk"
        if src_mk.exists() and _patch_application_mk(src_mk):
            fixed_any = True

    # 2) Bereits ausgepackte Kopien in .buildozer (für inkrementelle Builds)
    platform_dir = Path(".buildozer/android/platform")
    if platform_dir.exists():
        # Beide Kandidatenpfade: dists und bootstrap_builds
        candidates = list(platform_dir.glob("build-*/dists/*/jni/Application.mk"))
        candidates += list(platform_dir.glob("build-*/build/bootstrap_builds/sdl2/jni/Application.mk"))
        for mk_file in candidates:
            if _patch_application_mk(mk_file):
                fixed_any = True

    if not fixed_any:
        print("P4A Hook: SDL2 Application.mk files already appear to be patched")

    return fixed_any


def fix_sqlite3_recipe_16kb_alignment():
    """Patcht die p4a-Sqlite3-Recipe-`Android.mk` für 16-KB-Alignment.

    Sqlite3 wird wie SDL2 über `ndk-build` gebaut, hat aber nur ein eigenes
    Android.mk (kein Application.mk). Wir injizieren `LOCAL_LDFLAGS` direkt
    in das Android.mk — bedingt auf `TARGET_ARCH_ABI` (nur 64-Bit).
    """
    print("P4A Hook: Patching sqlite3 Android.mk for 16 KB alignment...")

    snippet = (
        "\n# " + PAGE_SIZE_FIX_MARKER + "\n"
        "ifneq ($(filter arm64-v8a x86_64,$(TARGET_ARCH_ABI)),)\n"
        "LOCAL_LDFLAGS += -Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384\n"
        "endif\n"
    )

    fixed_any = False
    candidates = []

    # 1) ALLE p4a-Source-Standorte (venv + buildozer-extrahiert).
    # Buildozer's `prebuild_arch` kopiert Android.mk aus der EXTRAHIERTEN
    # p4a-Kopie unter .buildozer/android/platform/python-for-android/, NICHT
    # aus dem venv. Wenn nur das venv gepatcht wird, erscheint im Build-Dir
    # weiterhin eine ungepatchte Android.mk. Beide Pfade müssen gepatcht sein.
    for p4a_dir in _find_all_pythonforandroid_dirs():
        src_mk = p4a_dir / "recipes" / "sqlite3" / "Android.mk"
        if src_mk.exists():
            candidates.append(src_mk)

    # 2) Bereits in .buildozer kopierte Build-Verzeichnisse (inkrementelle Builds)
    platform_dir = Path(".buildozer/android/platform")
    if platform_dir.exists():
        candidates += list(platform_dir.glob(
            "build-*/build/other_builds/sqlite3/*/sqlite3/jni/Android.mk"
        ))

    for mk_file in candidates:
        try:
            content = mk_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"P4A Hook: Konnte {mk_file} nicht lesen: {e}")
            continue

        if PAGE_SIZE_FIX_MARKER in content:
            continue  # bereits gepatcht

        # Vor `include $(BUILD_SHARED_LIBRARY)` einfügen
        if "include $(BUILD_SHARED_LIBRARY)" in content:
            new_content = content.replace(
                "include $(BUILD_SHARED_LIBRARY)",
                snippet + "\ninclude $(BUILD_SHARED_LIBRARY)",
            )
        else:
            new_content = content.rstrip() + "\n" + snippet

        try:
            mk_file.write_text(new_content, encoding="utf-8")
            print(f"P4A Hook: Patched {mk_file}")
            fixed_any = True
        except Exception as e:
            print(f"P4A Hook: Konnte {mk_file} nicht schreiben: {e}")

    if not fixed_any:
        print("P4A Hook: sqlite3 Android.mk already patched or not found")

    return fixed_any


def verify_so_alignment(libs_dir: Path = None):
    """Prüft per `objdump -p` das ELF LOAD-Alignment aller .so-Dateien unter
    libs_dir/arm64-v8a/. Erwartet: align 2**14 (16 KB).

    Gibt eine Liste der nicht-konformen Libraries zurück. Macht KEIN
    Build-Abbruch — nur Warnung.
    """
    if libs_dir is None:
        # Default: Suche in den Standard-Buildozer-Output-Pfaden
        for candidate in Path(".buildozer/android/platform").glob(
            "build-*/dists/*/libs"
        ):
            libs_dir = candidate
            break

    if libs_dir is None or not Path(libs_dir).exists():
        print("P4A Hook: Keine libs/-Verzeichnisse zum Verifizieren gefunden.")
        return []

    arm64_dir = Path(libs_dir) / "arm64-v8a"
    if not arm64_dir.exists():
        print(f"P4A Hook: {arm64_dir} existiert nicht (32-Bit-only Build?)")
        return []

    print(f"\nP4A Hook: Prüfe 16 KB Alignment unter {arm64_dir}...")
    print("-" * 70)

    bad = []
    so_files = sorted(arm64_dir.glob("*.so"))
    if not so_files:
        print(f"P4A Hook: Keine .so-Dateien in {arm64_dir}")
        return []

    for so in so_files:
        try:
            out = subprocess.check_output(
                ["objdump", "-p", str(so)],
                stderr=subprocess.STDOUT,
                text=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"  ⚠️  {so.name}: objdump fehlgeschlagen ({e})")
            continue

        # Suche LOAD-Zeilen mit "align 2**N"
        load_aligns = re.findall(r"LOAD .* align 2\*\*(\d+)", out)
        if not load_aligns:
            print(f"  ?  {so.name}: keine LOAD-Segmente gefunden")
            continue

        max_align = max(int(a) for a in load_aligns)
        if max_align >= 14:
            print(f"  ✅ {so.name}: align 2**{max_align} (16 KB OK)")
        else:
            print(f"  ❌ {so.name}: align 2**{max_align} (4 KB - NICHT 16 KB ALIGNED)")
            bad.append(so.name)

    print("-" * 70)
    if bad:
        print(f"⚠️  {len(bad)}/{len(so_files)} 64-Bit-Library(s) NICHT 16 KB aligned:")
        for name in bad:
            print(f"     - {name}")
        print(
            "    Lösung: NDK-Bump in buildozer.spec (auf 26b/28c) und/oder "
            "build_fixes.py-Patches prüfen."
        )
    else:
        print(f"✅ Alle {len(so_files)} Libraries sind 16 KB aligned (Google Play konform).")

    return bad


# p4a Hook-Funktionen (werden von python-for-android aufgerufen)
def before_apk_build(toolchain):
    """p4a Hook: Wird vor dem APK-Build aufgerufen"""
    print("P4A Hook (before_apk_build): Applying build fixes...")
    fix_kivy_python3_compatibility()
    fix_pyjnius_python3_compatibility()
    fix_android_manifest_fileprovider()
    fix_android_manifest_predictive_back()
    fix_android_manifest_large_screens()
    fix_p4a_activity_orientation_restriction()
    fix_p4a_ldflags_for_16kb_alignment()
    fix_sdl2_bootstrap_16kb_alignment()
    fix_sqlite3_recipe_16kb_alignment()


if __name__ == "__main__":
    print("P4A Hook: Starting build fixes...")

    kivy_fixed = fix_kivy_python3_compatibility()
    if kivy_fixed:
        print("P4A Hook: Kivy Python 3+ compatibility issues fixed")

    pyjnius_fixed = fix_pyjnius_python3_compatibility()
    if pyjnius_fixed:
        print("P4A Hook: PyJNIus Python 3+ compatibility issues fixed")

    manifest_fixed = fix_android_manifest_fileprovider()
    if manifest_fixed:
        print("P4A Hook: FileProvider in AndroidManifest.xml eingefügt")

    back_fixed = fix_android_manifest_predictive_back()
    if back_fixed:
        print("P4A Hook: Predictive-Back-Opt-out in AndroidManifest.xml eingefügt")

    large_screen_fixed = fix_android_manifest_large_screens()
    if large_screen_fixed:
        print("P4A Hook: resizeableActivity=true in AndroidManifest.xml eingefügt")

    orientation_fixed = fix_p4a_activity_orientation_restriction()
    if orientation_fixed:
        print("P4A Hook: Ausrichtungs-Sperre aus PythonActivity.java entfernt")

    archs_fixed = fix_p4a_ldflags_for_16kb_alignment()
    if archs_fixed:
        print("P4A Hook: archs.py mit 16 KB LDFLAGS gepatcht")

    sdl2_fixed = fix_sdl2_bootstrap_16kb_alignment()
    if sdl2_fixed:
        print("P4A Hook: SDL2-Bootstrap Application.mk mit 16 KB APP_LDFLAGS gepatcht")

    sqlite3_fixed = fix_sqlite3_recipe_16kb_alignment()
    if sqlite3_fixed:
        print("P4A Hook: sqlite3 Android.mk mit 16 KB LOCAL_LDFLAGS gepatcht")

    if any([kivy_fixed, pyjnius_fixed, manifest_fixed, back_fixed, large_screen_fixed,
            orientation_fixed, archs_fixed, sdl2_fixed, sqlite3_fixed]):
        print("P4A Hook: Build fixes completed successfully")
    else:
        print("P4A Hook: No fixes were needed")
