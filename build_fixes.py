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

Zusätzlich: Bitmap-Downsampling (BitmapFactory.Options.inSampleSize) in
PythonActivity.getLoadingScreen und launcher.Project.scanDirectory —
von Google Play als "BitmapFactory ohne Downsampling" gemeldet.

Zusätzlich: R8-Optimierung für den Release-Build (minifyEnabled + Keep-Regeln
aus src/android/proguard-rules.pro) — von Google Play als "Deine App ist nicht
optimiert" gemeldet.

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


def _find_bootstrap_java_files(java_rel_path):
    """Sammelt alle Fassungen einer Bootstrap-Java-Datei: p4a-Bootstrap-Quellen
    UND die bereits nach bootstrap_builds/dists kopierten Kopien.

    Die Bootstrap-Quelle mitzupatchen ist wichtig: ein Patch nur in der Dist
    geht verloren, sobald p4a die Dist neu erzeugt (`buildozer android clean`).

    Args:
        java_rel_path: Pfad unterhalb von `src/main/java/`,
            z.B. "org/kivy/android/PythonActivity.java"
    """
    java_files = []

    # 1) p4a-Bootstrap-Quellen (venv + buildozer-extrahierte Kopie)
    for p4a_dir in _find_all_pythonforandroid_dirs():
        java_files += list(
            (p4a_dir / "bootstraps").glob(f"*/build/src/main/java/{java_rel_path}")
        )

    platform_dir = Path(".buildozer/android/platform")
    if platform_dir.exists():
        # 2) Zwischenstände der Bootstrap-Builds
        java_files += list(platform_dir.glob(
            f"build-*/build/bootstrap_builds/*/src/main/java/{java_rel_path}"
        ))
        # 3) Fertige Dists (das, was tatsächlich kompiliert wird)
        java_files += list(platform_dir.glob(
            f"build-*/dists/*/src/main/java/{java_rel_path}"
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

    java_files = _find_bootstrap_java_files("org/kivy/android/PythonActivity.java")
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


BITMAP_FIX_MARKER = "BITMAP-DOWNSAMPLING-FIX"

# Google-Standardimplementierung (developer.android.com "Große Bitmaps effizient laden"),
# als private Hilfsmethode in die jeweilige Klasse eingefügt.
_INSAMPLESIZE_HELPER = """
    /**
     * %(marker)s: Berechnet inSampleSize (Zweierpotenz), sodass das dekodierte
     * Bitmap die geforderte Anzeigegröße nicht überschreitet. Ohne Downsampling
     * meldet Google Play "BitmapFactory ohne Downsampling"; bei größeren Assets
     * würde das Vollauflösungs-Bitmap unnötig viel Speicher belegen.
     */
    private static int calculateInSampleSize(
            BitmapFactory.Options options, int reqWidth, int reqHeight) {
        final int height = options.outHeight;
        final int width = options.outWidth;
        int inSampleSize = 1;

        if (reqWidth <= 0 || reqHeight <= 0) {
            return inSampleSize;
        }

        while ((height / inSampleSize) > reqHeight || (width / inSampleSize) > reqWidth) {
            inSampleSize *= 2;
        }

        return inSampleSize;
    }
""" % {"marker": BITMAP_FIX_MARKER}

# --- PythonActivity.getLoadingScreen: Presplash in voller Auflösung dekodiert ---
# Whitespace-tolerant, damit auch die abweichend eingerückte webview-Variante passt.
_PRESPLASH_DECODE_RE = re.compile(
    r'([ \t]*)int presplashId = this\.resourceManager\.getIdentifier\("presplash", "drawable"\);\s*'
    r'InputStream is = this\.getResources\(\)\.openRawResource\(presplashId\);\s*'
    r'Bitmap bitmap = null;\s*'
    r'try \{\s*'
    r'bitmap = BitmapFactory\.decodeStream\(is\);\s*'
    r'\} finally \{\s*'
    r'try \{\s*'
    r'is\.close\(\);\s*'
    r'\} catch \(IOException e\) \{\};\s*'
    r'\}\n'
)

_PRESPLASH_DECODE_REPLACEMENT = f'''\\g<1>int presplashId = this.resourceManager.getIdentifier("presplash", "drawable");

\\g<1>// {BITMAP_FIX_MARKER}: Presplash zweistufig laden — erst nur die Maße
\\g<1>// (inJustDecodeBounds), dann passend heruntergerechnet. Das Bild wird
\\g<1>// ohnehin nur bildschirmfüllend (FIT_CENTER) angezeigt.
\\g<1>BitmapFactory.Options presplashOptions = new BitmapFactory.Options();
\\g<1>presplashOptions.inJustDecodeBounds = true;
\\g<1>InputStream boundsStream = this.getResources().openRawResource(presplashId);
\\g<1>try {{
\\g<1>    BitmapFactory.decodeStream(boundsStream, null, presplashOptions);
\\g<1>}} finally {{
\\g<1>    try {{
\\g<1>        boundsStream.close();
\\g<1>    }} catch (IOException e) {{}};
\\g<1>}}
\\g<1>presplashOptions.inSampleSize = calculateInSampleSize(
\\g<1>    presplashOptions,
\\g<1>    getResources().getDisplayMetrics().widthPixels,
\\g<1>    getResources().getDisplayMetrics().heightPixels);
\\g<1>presplashOptions.inJustDecodeBounds = false;

\\g<1>InputStream is = this.getResources().openRawResource(presplashId);
\\g<1>Bitmap bitmap = null;
\\g<1>try {{
\\g<1>    bitmap = BitmapFactory.decodeStream(is, null, presplashOptions);
\\g<1>}} finally {{
\\g<1>    try {{
\\g<1>        is.close();
\\g<1>    }} catch (IOException e) {{}};
\\g<1>}}
'''

# --- Project.scanDirectory: Launcher-Icon in voller Auflösung dekodiert ---
_PROJECT_ICON_DECODE_RE = re.compile(
    r'([ \t]*)rv\.icon = BitmapFactory\.decodeFile\('
    r'new File\(dir, "icon\.png"\)\.getAbsolutePath\(\)\);\n'
)

_PROJECT_ICON_DECODE_REPLACEMENT = f'''\\g<1>// {BITMAP_FIX_MARKER}: Icon zweistufig laden (erst Maße, dann herunterge-
\\g<1>// rechnet). Es wird nur als Listen-Icon im Kivy-Launcher angezeigt.
\\g<1>String iconPath = new File(dir, "icon.png").getAbsolutePath();
\\g<1>BitmapFactory.Options iconOptions = new BitmapFactory.Options();
\\g<1>iconOptions.inJustDecodeBounds = true;
\\g<1>BitmapFactory.decodeFile(iconPath, iconOptions);
\\g<1>iconOptions.inSampleSize = calculateInSampleSize(iconOptions, ICON_MAX_PX, ICON_MAX_PX);
\\g<1>iconOptions.inJustDecodeBounds = false;
\\g<1>rv.icon = BitmapFactory.decodeFile(iconPath, iconOptions);
'''

# Zielkantenlänge des Launcher-Icons in px (Listeneintrag, ~48dp bei xhdpi)
_PROJECT_ICON_KONSTANTE = (
    "\n"
    f"    /** {BITMAP_FIX_MARKER}: Zielkantenlänge des Listen-Icons in Pixeln. */\n"
    "    private static final int ICON_MAX_PX = 96;\n"
)


def _fuege_java_methode_an(content, methode):
    """Hängt eine Methode ans Ende der Klasse (vor die letzte schließende Klammer)."""
    stripped = content.rstrip()
    if not stripped.endswith("}"):
        return None
    rumpf = stripped[:-1].rstrip("\n")
    return f"{rumpf}\n{methode}}}\n"


def fix_p4a_bitmap_downsampling():
    """Ergänzt BitmapFactory.Options mit inSampleSize in den p4a-Bootstrap-Klassen.

    Hintergrund: Google Play meldet "BitmapFactory ohne Downsampling" für
    `PythonActivity.getLoadingScreen` (Presplash) und
    `launcher.Project.scanDirectory` (Launcher-Icon). Beide dekodieren ihr Bild
    in voller Auflösung. Der Presplash ist aktuell klein (512x512, siehe
    `presplash.filename` in buildozer.spec), aber ein größeres Asset in einem
    späteren Update würde ungebremst Speicher belegen.

    Beide Stellen laden nun zweistufig: erst nur die Maße (inJustDecodeBounds),
    dann heruntergerechnet auf die tatsächliche Anzeigegröße.

    Idempotent: erkennt den bereits gepatchten Zustand am Marker.
    """
    print("P4A Hook: Checking p4a bootstrap classes for bitmap downsampling...")

    ziele = [
        ("org/kivy/android/PythonActivity.java", _PRESPLASH_DECODE_RE,
         _PRESPLASH_DECODE_REPLACEMENT, None),
        ("org/kivy/android/launcher/Project.java", _PROJECT_ICON_DECODE_RE,
         _PROJECT_ICON_DECODE_REPLACEMENT, _PROJECT_ICON_KONSTANTE),
    ]

    fixed_any = False
    gefunden = False

    for java_rel_path, muster, ersatz, konstante in ziele:
        for java_file in _find_bootstrap_java_files(java_rel_path):
            gefunden = True
            try:
                with open(java_file, 'r') as f:
                    content = f.read()

                if BITMAP_FIX_MARKER in content:
                    print(f"P4A Hook: bitmap downsampling already present in {java_file}")
                    continue

                new_content, count = muster.subn(ersatz, content, count=1)
                if count == 0:
                    if 'BitmapFactory' in content:
                        print(
                            f"P4A Hook: WARNUNG — BitmapFactory in {java_file} gefunden, "
                            "aber Decode-Muster passt nicht (p4a-Version geändert?)"
                        )
                    else:
                        print(f"P4A Hook: no BitmapFactory decode in {java_file}")
                    continue

                # Hilfsmethode (+ ggf. Konstante) ans Klassenende hängen
                mit_helper = _fuege_java_methode_an(
                    new_content,
                    (konstante + _INSAMPLESIZE_HELPER) if konstante else _INSAMPLESIZE_HELPER,
                )
                if mit_helper is None:
                    print(f"P4A Hook: WARNUNG — Klassenende in {java_file} nicht gefunden")
                    continue

                with open(java_file, 'w') as f:
                    f.write(mit_helper)
                print(f"P4A Hook: bitmap downsampling added to {java_file}")
                fixed_any = True

            except Exception as e:
                print(f"P4A Hook: Error fixing {java_file}: {e}")

    if not gefunden:
        print("P4A Hook: No bootstrap Java files found, skipping bitmap fix")
        return False

    if not fixed_any:
        print("P4A Hook: All bootstrap classes already downsample their bitmaps")

    return fixed_any


R8_FIX_MARKER = "R8-OPTIMIZATION-FIX"

PROGUARD_RULES_NAME = "proguard-rules.pro"

# Quelle der Wahrheit im Repo (build_fixes.py liegt im Projekt-Root).
# Absolut auflösen: der p4a-Hook läuft mit cwd = dist_dir, dort gibt es ein
# eigenes src/-Verzeichnis, ein relativer Pfad würde also ins Leere greifen.
PROGUARD_RULES_QUELLE = Path(__file__).resolve().parent / "src" / "android" / PROGUARD_RULES_NAME

# Der release-Block der p4a-Gradle-Vorlage ist leer bzw. enthält nur den
# optionalen signingConfig. Wir hängen die R8-Aktivierung direkt hinter die
# öffnende Klammer. Das Muster ist bewusst eng an buildTypes{debug{}release{}
# verankert, damit kein anderer "release {"-Block getroffen wird.
_R8_RELEASE_BLOCK_RE = re.compile(
    r'(buildTypes\s*\{\s*debug\s*\{\s*\}\s*release\s*\{)'
)

_R8_RELEASE_BLOCK_REPLACEMENT = (
    f'''\\g<1>
            // {R8_FIX_MARKER}: R8 aktivieren (Google Play "App-Optimierung").
            // Verkleinert und optimiert NUR den Java-Layer (p4a-Bootstrap, SDL2,
            // pyjnius-Glue) — Python-Code und .so-Dateien bleiben unberührt.
            minifyEnabled true
            // shrinkResources bleibt BEWUSST aus: p4a sucht Ressourcen zur
            // Laufzeit über ResourceManager.getIdentifier("presplash", "drawable")
            // per Name. Das Resource-Shrinking sieht diese Zugriffe nicht und
            // würde Presplash, Layouts und res/xml/file_paths.xml entfernen.
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), '{PROGUARD_RULES_NAME}\''''
)


def _find_gradle_files():
    """Sammelt die Gradle-Build-Dateien: p4a-Vorlagen (build.tmpl.gradle) UND
    bereits gerenderte build.gradle in den Dists.

    Die Vorlagen sind der wichtigere Teil — p4a rendert build.gradle bei jedem
    Build neu, ein Patch nur an der gerenderten Datei ginge verloren.
    """
    gradle_files = []

    # 1) p4a-Bootstrap-Vorlagen (venv + buildozer-extrahierte Kopie)
    for p4a_dir in _find_all_pythonforandroid_dirs():
        for tmpl in [
            p4a_dir / "bootstraps" / "common" / "build" / "templates" / "build.tmpl.gradle",
            p4a_dir / "bootstraps" / "sdl2" / "build" / "templates" / "build.tmpl.gradle",
        ]:
            if tmpl.exists():
                gradle_files.append(tmpl)

    platform_dir = Path(".buildozer/android/platform")
    if platform_dir.exists():
        # 2) Zwischenstände der Bootstrap-Builds
        gradle_files += list(platform_dir.glob(
            "build-*/build/bootstrap_builds/*/templates/build.tmpl.gradle"))
        # 3) In die Dists kopierte Vorlagen + gerenderte build.gradle
        gradle_files += list(platform_dir.glob("build-*/dists/*/templates/build.tmpl.gradle"))
        gradle_files += list(platform_dir.glob("build-*/dists/*/build.gradle"))

    # 4) cwd, falls der p4a-Hook bereits im Dist-Verzeichnis läuft
    for kandidat in [Path("templates/build.tmpl.gradle"), Path("build.gradle")]:
        if kandidat.exists() and Path("build.py").exists():
            gradle_files.append(kandidat)

    seen = set()
    unique = []
    for f in gradle_files:
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(f)
    return unique


def _find_proguard_ziel_dirs():
    """Verzeichnisse, in die proguard-rules.pro gehört — überall dort, wo auch
    build.gradle landet.

    p4a kopiert beim Dist-Bau das komplette Bootstrap-Build-Verzeichnis
    (`sh.cp -r build_dir dist_dir`, siehe bootstraps/sdl2/__init__.py). Die
    Datei im Bootstrap-Verzeichnis wandert dadurch automatisch in jede neu
    erzeugte Dist — nur die Dist zu bestücken würde ein `buildozer android
    clean` nicht überleben.
    """
    ziele = []

    for p4a_dir in _find_all_pythonforandroid_dirs():
        bootstrap_build = p4a_dir / "bootstraps" / "sdl2" / "build"
        if bootstrap_build.exists():
            ziele.append(bootstrap_build)

    platform_dir = Path(".buildozer/android/platform")
    if platform_dir.exists():
        ziele += [d for d in platform_dir.glob("build-*/build/bootstrap_builds/*") if d.is_dir()]
        ziele += [d for d in platform_dir.glob("build-*/dists/*") if d.is_dir()]

    # cwd, falls der p4a-Hook bereits im Dist-Verzeichnis läuft
    if Path("build.py").exists() and Path("templates").is_dir():
        ziele.append(Path("."))

    seen = set()
    unique = []
    for d in ziele:
        resolved = d.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(d)
    return unique


def fix_gradle_r8_optimization():
    """Aktiviert R8 für den Release-Build und hinterlegt die Keep-Regeln.

    Hintergrund: Google Play meldet "Deine App ist nicht optimiert — aktiviere
    ein Optimierungstool wie R8". Die p4a-Gradle-Vorlage lässt den
    release-Block leer, R8 läuft also gar nicht.

    Zwei Teile:
      1. `minifyEnabled true` + `proguardFiles` im release-Block (Vorlagen UND
         gerenderte build.gradle).
      2. `src/android/proguard-rules.pro` in jedes Dist-/Bootstrap-Verzeichnis
         kopieren. Ohne diese Keep-Regeln zerlegt R8 die App: der komplette
         Java-Layer wird nur über JNI (SDL2, CPython) und Reflection (pyjnius)
         erreicht und ist für die statische Analyse unsichtbar.

    `shrinkResources` bleibt bewusst deaktiviert — siehe Kommentar im
    eingefügten Gradle-Block.

    Idempotent: erkennt den bereits gepatchten Zustand am Marker.
    """
    print("P4A Hook: Checking Gradle build for R8 optimization...")

    if not PROGUARD_RULES_QUELLE.exists():
        print(
            f"P4A Hook: WARNUNG — {PROGUARD_RULES_QUELLE} fehlt. R8 wird NICHT "
            "aktiviert (ohne Keep-Regeln würde der Release-Build abstürzen)."
        )
        return False

    regeln = PROGUARD_RULES_QUELLE.read_text()
    fixed_any = False

    # --- Teil 1: Keep-Regeln verteilen -------------------------------------
    ziel_dirs = _find_proguard_ziel_dirs()
    for ziel_dir in ziel_dirs:
        ziel = ziel_dir / PROGUARD_RULES_NAME
        try:
            if ziel.exists() and ziel.read_text() == regeln:
                continue
            ziel.write_text(regeln)
            print(f"P4A Hook: {PROGUARD_RULES_NAME} geschrieben nach {ziel}")
            fixed_any = True
        except Exception as e:
            print(f"P4A Hook: Error writing {ziel}: {e}")

    # --- Teil 2: R8 im release-Block aktivieren ----------------------------
    gradle_files = _find_gradle_files()
    if not gradle_files:
        print("P4A Hook: No Gradle build files found, skipping R8 fix")
        return fixed_any

    for gradle_file in gradle_files:
        try:
            content = gradle_file.read_text()

            if R8_FIX_MARKER in content:
                print(f"P4A Hook: R8 already enabled in {gradle_file}")
                continue

            new_content, count = _R8_RELEASE_BLOCK_RE.subn(
                _R8_RELEASE_BLOCK_REPLACEMENT, content, count=1
            )
            if count == 0:
                if 'minifyEnabled' in content:
                    print(f"P4A Hook: {gradle_file} enables minify already (fremder Patch?)")
                else:
                    print(
                        f"P4A Hook: WARNUNG — release-Block in {gradle_file} nicht "
                        "gefunden (p4a-Version geändert?)"
                    )
                continue

            gradle_file.write_text(new_content)
            print(f"P4A Hook: R8 enabled in {gradle_file}")
            fixed_any = True

        except Exception as e:
            print(f"P4A Hook: Error fixing {gradle_file}: {e}")

    if not fixed_any:
        print("P4A Hook: R8 already enabled everywhere")

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


# ===========================================================================
# R8-Verifikation (nach dem Release-Build)
# ===========================================================================

# Von R8/D8 selbst erzeugte Klassen (Desugaring: Lambda- und API-Model-Outlining).
# Sie existieren im Quellcode nicht und werden nie über JNI/Reflection per Name
# angesprochen — ihre Umbenennung ist unbedenklich und KEIN Fehler.
_R8_SYNTHETIK_MARKER = ("$$ExternalSynthetic", "$$InternalSynthetic", "$$Lambda")

# Dasselbe auf Member-Ebene: von R8 erzeugte Lambda-Bridges ($r8$lambda$…),
# javac-Lambda-Rümpfe (lambda$methode$0) und synthetische Zugriffsmethoden
# (access$000). Alle existieren im Quellcode nicht und werden nie per Name
# aufgerufen — ihre Umbenennung ist unbedenklich.
_R8_SYNTHETIK_MEMBER_PRAEFIXE = ("$r8$lambda$", "lambda$", "access$")

# Einstiegspunkte, die ausschließlich über JNI oder pyjnius erreicht werden.
# Sie MÜSSEN im DEX vorhanden und unbenannt sein — kein Java-Code referenziert
# sie, R8 kann ihren Wegfall also nicht selbst bemerken.
R8_REFLEKTIONS_EINSTIEGSPUNKTE = {
    # manager/html_manager.py, utils/share_utils.py -> Teilen/Export
    "androidx.core.content.FileProvider": ["getUriForFile"],
    # views/app_navigation_mixin.py, main.py, android.activity.bind()
    "org.kivy.android.PythonActivity": [
        "mActivity", "registerNewIntentListener", "onNewIntent", "getLoadingScreen",
    ],
    "org.kivy.android.PythonUtil": ["loadLibraries"],
    # Presplash-Lookup zur Laufzeit (getIdentifier statt R.drawable)
    "org.renpy.android.ResourceManager": ["getIdentifier"],
    # PythonJavaClass-Brücke (NewIntentListener)
    "org.jnius.NativeInvocationHandler": ["invoke"],
    # SDL2 ruft seine Java-Seite komplett aus nativem Code auf
    "org.libsdl.app.SDLActivity": ["nativeSetenv", "onNativeResize"],
    # Entpackt das Python-Bundle beim ersten Start
    "org.kamranzafar.jtar.TarInputStream": ["getNextEntry"],
}


def _lies_keep_regeln(proguard_datei=None):
    """Liest die Keep-Regeln aus proguard-rules.pro.

    Returns:
        (praefixe, exakte) — Paketpräfixe aus `-keep class foo.bar.** { *; }`
        (inkl. abschließendem Punkt) und exakte Klassennamen aus
        `-keep class foo.Bar { *; }`.

    Die Regeln werden aus der Datei gelesen statt hier dupliziert, damit
    Prüfung und Regelwerk nicht auseinanderlaufen können.
    """
    if proguard_datei is None:
        proguard_datei = PROGUARD_RULES_QUELLE
    proguard_datei = Path(proguard_datei)

    praefixe, exakte = set(), set()
    if not proguard_datei.exists():
        return praefixe, exakte

    for zeile in proguard_datei.read_text().splitlines():
        zeile = zeile.split('#', 1)[0].strip()
        m = re.match(r'-keep(?:\w*)\s+class\s+([\w.$*]+)\s*\{', zeile)
        if not m:
            continue
        ziel = m.group(1)
        if ziel.endswith('.**') or ziel.endswith('.*'):
            praefixe.add(ziel.rstrip('*').rstrip('.') + '.')
        elif '*' not in ziel:
            exakte.add(ziel)
    return praefixe, exakte


def _ist_geschuetzt(klasse, praefixe, exakte):
    """True, wenn die Klasse von einer Keep-Regel abgedeckt ist."""
    return klasse in exakte or any(klasse.startswith(p) for p in praefixe)


def _parse_mapping(mapping_datei):
    """Parst mapping.txt zu {original_klasse: (obf_klasse, {orig_member: obf_member})}.

    Format je Klasse:  `orig.Klasse -> obf.Klasse:`
    Format je Member:  `    [n:m:]<Typ> <name>[(args)][:zeile[:zeile]] -> <obf>`

    Zeilen mit voll qualifiziertem Member-Namen (`... Fremd.Klasse.methode(...)`)
    sind Inline-Frames aus einer ANDEREN Klasse und werden übersprungen — sonst
    würden sie fälschlich der umgebenden Klasse zugeordnet.
    """
    ergebnis = {}
    aktuell = None

    for zeile in Path(mapping_datei).read_text(errors="replace").splitlines():
        if not zeile.strip() or zeile.lstrip().startswith('#'):
            continue

        if not zeile[0].isspace():
            m = re.match(r'^([\w.$]+)\s+->\s+([\w.$]+):$', zeile)
            if m:
                aktuell = m.group(1)
                ergebnis[aktuell] = (m.group(2), {})
            else:
                aktuell = None
            continue

        if aktuell is None or ' -> ' not in zeile:
            continue

        links, _, obf = zeile.strip().rpartition(' -> ')
        # führende Zeilennummern "12:34:" entfernen
        links = re.sub(r'^\d+:\d+:', '', links)
        if ' ' not in links:
            continue
        _typ, _, rest = links.partition(' ')
        name = rest.split('(', 1)[0].split(':', 1)[0].strip()
        if '.' in name:      # Inline-Frame aus fremder Klasse
            continue
        ergebnis[aktuell][1].setdefault(name, obf.strip())

    return ergebnis


def _finde_mapping_dateien():
    """Sucht mapping.txt aller Release-Builds in den Dists."""
    platform_dir = Path(".buildozer/android/platform")
    if not platform_dir.exists():
        return []
    return sorted(platform_dir.glob(
        "build-*/dists/*/build/outputs/mapping/release/mapping.txt"))


def _finde_release_dex():
    """Extrahiert classes.dex aus dem Release-AAB/-APK und liefert die
    dexdump-Ausgabe. Best-effort: None, wenn Artefakt oder dexdump fehlen.
    """
    import subprocess as _sp
    import tempfile
    import zipfile

    artefakte = []
    for muster in [
        ".buildozer/android/platform/build-*/dists/*/build/outputs/bundle/release/*.aab",
        ".buildozer/android/platform/build-*/dists/*/build/outputs/apk/release/*.apk",
        "bin/*-release*.aab",
        "bin/*-release*.apk",
    ]:
        artefakte += list(Path('.').glob(muster))
    if not artefakte:
        return None

    artefakt = max(artefakte, key=lambda p: p.stat().st_mtime)

    dexdumps = sorted(Path("/home/jean/Android/Sdk/build-tools").glob("*/dexdump"))
    if not dexdumps:
        sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROIDSDK")
        if sdk:
            dexdumps = sorted(Path(sdk).glob("build-tools/*/dexdump"))
    if not dexdumps:
        return None

    with tempfile.TemporaryDirectory() as tmp:
        try:
            with zipfile.ZipFile(artefakt) as z:
                dex_eintraege = [n for n in z.namelist() if n.endswith("classes.dex")]
                if not dex_eintraege:
                    return None
                ziel = Path(tmp) / "classes.dex"
                ziel.write_bytes(z.read(dex_eintraege[0]))
            aus = _sp.run([str(dexdumps[-1]), "-d", str(ziel)],
                          capture_output=True, text=True, timeout=300)
        except Exception:
            return None

    if aus.returncode != 0:
        return None

    klassen, akt = {}, None
    for zeile in aus.stdout.splitlines():
        m = re.match(r"\s*Class descriptor\s*:\s*'L([^;]+);'", zeile)
        if m:
            akt = m.group(1).replace("/", ".")
            klassen.setdefault(akt, set())
            continue
        m = re.match(r"\s*name\s*:\s*'([^']+)'", zeile)
        if m and akt:
            klassen[akt].add(m.group(1))
    return (artefakt, klassen)


def verify_r8_keep_rules(mapping_datei=None):
    """Prüft nach einem Release-Build, ob R8 die Keep-Regeln eingehalten hat.

    Zwei Prüfungen mit unterschiedlichen Quellen — das ist Absicht:

    1. UMBENENNUNG (mapping.txt): Jede von einer Keep-Regel abgedeckte Klasse
       muss auf sich selbst gemappt sein. Von R8 erzeugte Synthetik-Klassen
       ($$ExternalSynthetic…) sind ausgenommen.
    2. EXISTENZ (DEX): Die nur über JNI/pyjnius erreichten Einstiegspunkte
       müssen im Artefakt vorhanden sein. Das lässt sich NICHT über mapping.txt
       prüfen — R8 listet dort nicht jedes überlebende Member (z.B. fehlt
       PythonActivity.mActivity, obwohl es im DEX steht). Der DEX-Teil ist
       best-effort und wird übersprungen, wenn Artefakt oder dexdump fehlen.

    Bricht den Build NICHT ab — meldet nur. Gibt die Liste der Probleme zurück.
    """
    probleme = []

    dateien = [Path(mapping_datei)] if mapping_datei else _finde_mapping_dateien()
    if not dateien or not dateien[0].exists():
        print("\nP4A Hook: Keine mapping.txt gefunden — R8 lief nicht "
              "(Debug-Build?). R8-Verifikation übersprungen.")
        return probleme

    praefixe, exakte = _lies_keep_regeln()
    if not praefixe and not exakte:
        print(f"P4A Hook: WARNUNG — keine Keep-Regeln aus {PROGUARD_RULES_QUELLE} "
              "gelesen. R8-Verifikation nicht aussagekräftig.")
        return ["Keep-Regeln nicht lesbar"]

    mapping = dateien[-1]
    print(f"\nP4A Hook: Prüfe R8-Keep-Regeln gegen {mapping}...")
    print("-" * 70)

    # --- 1. Umbenennung ---------------------------------------------------
    eintraege = _parse_mapping(mapping)
    geprueft = 0
    for orig, (obf, member) in sorted(eintraege.items()):
        if not _ist_geschuetzt(orig, praefixe, exakte):
            continue
        if any(marker in orig for marker in _R8_SYNTHETIK_MARKER):
            continue
        geprueft += 1
        if orig != obf:
            probleme.append(f"Klasse umbenannt: {orig} -> {obf}")
            continue
        for m_orig, m_obf in sorted(member.items()):
            if m_orig == m_obf:
                continue
            if m_orig.startswith(_R8_SYNTHETIK_MEMBER_PRAEFIXE):
                continue
            probleme.append(f"Member umbenannt: {orig}.{m_orig} -> {m_obf}")

    print(f"  Keep-Regeln: {len(praefixe)} Paketpräfixe, {len(exakte)} Einzelklassen")
    print(f"  {geprueft} geschützte Klassen im Mapping geprüft")

    # --- 2. Existenz der Reflection-Einstiegspunkte ------------------------
    dex = _finde_release_dex()
    if dex is None:
        print("  ⏭️  DEX-Prüfung übersprungen (kein Release-Artefakt oder "
              "dexdump nicht gefunden)")
    else:
        artefakt, klassen = dex
        print(f"  DEX aus {artefakt.name}: {len(klassen)} Klassen")
        for klasse, noetig in sorted(R8_REFLEKTIONS_EINSTIEGSPUNKTE.items()):
            if klasse not in klassen:
                probleme.append(f"Klasse fehlt im DEX: {klasse}")
                continue
            fehlend = [m for m in noetig if m not in klassen[klasse]]
            if fehlend:
                probleme.append(
                    f"Member fehlt im DEX: {klasse} -> {', '.join(fehlend)}")

    # --- Ergebnis ---------------------------------------------------------
    print("-" * 70)
    if probleme:
        print(f"❌ R8 hat {len(probleme)} Keep-Regel-Verletzung(en) produziert:")
        for p in probleme:
            print(f"     - {p}")
        print("    Die App wird im Release-Build sehr wahrscheinlich abstürzen.")
        print(f"    Lösung: {PROGUARD_RULES_QUELLE} ergänzen und neu bauen.")
    else:
        print("✅ R8-Keep-Regeln eingehalten (keine Umbenennung, "
              "alle Reflection-Einstiegspunkte vorhanden).")

    return probleme


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
    fix_p4a_bitmap_downsampling()
    fix_gradle_r8_optimization()
    fix_p4a_ldflags_for_16kb_alignment()
    fix_sdl2_bootstrap_16kb_alignment()
    fix_sqlite3_recipe_16kb_alignment()


if __name__ == "__main__":
    # Reiner Prüfmodus: nach einem Release-Build die R8-Keep-Regeln validieren.
    # Exit-Code 1 bei Verletzung, damit der Aufruf in einer Pipeline greift.
    if "--verify-r8" in sys.argv:
        _probleme = verify_r8_keep_rules()
        sys.exit(1 if _probleme else 0)

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

    bitmap_fixed = fix_p4a_bitmap_downsampling()
    if bitmap_fixed:
        print("P4A Hook: Bitmap-Downsampling in p4a-Bootstrap-Klassen ergänzt")

    r8_fixed = fix_gradle_r8_optimization()
    if r8_fixed:
        print("P4A Hook: R8-Optimierung für den Release-Build aktiviert")

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
            orientation_fixed, bitmap_fixed, r8_fixed, archs_fixed, sdl2_fixed, sqlite3_fixed]):
        print("P4A Hook: Build fixes completed successfully")
    else:
        print("P4A Hook: No fixes were needed")
