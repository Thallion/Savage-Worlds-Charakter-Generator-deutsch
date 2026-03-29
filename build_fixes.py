#!/usr/bin/env python3
"""
Combined buildozer hook to fix Kivy and PyJNIus Python 3+ / Cython 3.x compatibility issues.

Wird automatisch von build_android.py / build_all.py aufgerufen, BEVOR buildozer startet.
Kann auch manuell ausgeführt werden: python build_fixes.py
"""
import os
import sys
import re
from pathlib import Path


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


# p4a Hook-Funktionen (werden von python-for-android aufgerufen)
def before_apk_build(toolchain):
    """p4a Hook: Wird vor dem APK-Build aufgerufen"""
    print("P4A Hook (before_apk_build): Applying build fixes...")
    fix_kivy_python3_compatibility()
    fix_pyjnius_python3_compatibility()
    fix_android_manifest_fileprovider()


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

    if kivy_fixed or pyjnius_fixed or manifest_fixed:
        print("P4A Hook: Build fixes completed successfully")
    else:
        print("P4A Hook: No fixes were needed")
