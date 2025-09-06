#!/usr/bin/env python3
"""
Buildozer hook to fix pyjnius Python 3+ compatibility issues
"""
import os
import sys
from pathlib import Path

def fix_pyjnius_python3_compatibility():
    """Fix Python 3+ compatibility issues in pyjnius"""
    print("P4A Hook: Searching for pyjnius build directories...")
    
    # Find pyjnius build directories
    build_root = Path(".buildozer/android/platform/build-arm64-v8a/build/other_builds")
    if not build_root.exists():
        print("P4A Hook: Build directory not found, skipping fix")
        return
    
    pyjnius_dirs = list(build_root.glob("pyjnius*/*/pyjnius"))
    if not pyjnius_dirs:
        print("P4A Hook: No pyjnius directories found, skipping fix")
        return
    
    for pyjnius_dir in pyjnius_dirs:
        jnius_utils_file = pyjnius_dir / "jnius" / "jnius_utils.pxi"
        if jnius_utils_file.exists():
            print(f"P4A Hook: Fixing Python 3+ compatibility in {jnius_utils_file}")
            
            try:
                # Read the file
                with open(jnius_utils_file, 'r') as f:
                    content = f.read()
                
                # Check if fix is needed
                if "(isinstance(arg, long) and arg < 2147483648)" in content:
                    # Apply the fix
                    content = content.replace(
                        "(isinstance(arg, long) and arg < 2147483648)",
                        "(isinstance(arg, int) and arg < 2147483648)"
                    )
                    
                    # Write back the fixed content
                    with open(jnius_utils_file, 'w') as f:
                        f.write(content)
                    
                    print(f"P4A Hook: Successfully fixed Python 3+ compatibility in {jnius_utils_file}")
                else:
                    print(f"P4A Hook: File {jnius_utils_file} already appears to be fixed")
                    
            except Exception as e:
                print(f"P4A Hook: Error fixing {jnius_utils_file}: {e}")
        else:
            print(f"P4A Hook: jnius_utils.pxi not found in {pyjnius_dir}")

if __name__ == "__main__":
    fix_pyjnius_python3_compatibility()