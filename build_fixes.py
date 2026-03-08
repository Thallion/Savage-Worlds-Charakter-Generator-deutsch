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


def fix_kivy_python3_compatibility():
    """Fix Python 3+ / Cython 3.x compatibility issues in ALL Kivy .pyx files"""
    print("P4A Hook: Searching for Kivy build directories...")

    # Find kivy build directories
    build_root = Path(".buildozer/android/platform/build-arm64-v8a/build/other_builds")
    if not build_root.exists():
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


def fix_pyjnius_python3_compatibility():
    """Fix Python 3+ / Cython 3.x compatibility issues in ALL pyjnius .pxi files"""
    print("P4A Hook: Searching for pyjnius build directories...")

    build_root = Path(".buildozer/android/platform/build-arm64-v8a/build/other_builds")
    if not build_root.exists():
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


if __name__ == "__main__":
    print("P4A Hook: Starting build fixes...")

    kivy_fixed = fix_kivy_python3_compatibility()
    if kivy_fixed:
        print("P4A Hook: Kivy Python 3+ compatibility issues fixed")

    pyjnius_fixed = fix_pyjnius_python3_compatibility()
    if pyjnius_fixed:
        print("P4A Hook: PyJNIus Python 3+ compatibility issues fixed")

    if kivy_fixed or pyjnius_fixed:
        print("P4A Hook: Build fixes completed successfully")
    else:
        print("P4A Hook: No fixes were needed")
