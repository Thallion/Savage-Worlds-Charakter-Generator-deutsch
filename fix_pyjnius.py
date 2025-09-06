#!/usr/bin/env python3
"""
Manual pyjnius Python 3+ compatibility fix script
"""
import os
import sys
from pathlib import Path

def fix_pyjnius_files():
    """Fix Python 3+ compatibility issues in all pyjnius files"""
    print("Searching for pyjnius build directories...")
    
    # Find pyjnius build directories
    build_root = Path(".buildozer/android/platform/build-arm64-v8a/build/other_builds")
    if not build_root.exists():
        print("Build directory not found!")
        return False
    
    pyjnius_dirs = list(build_root.glob("pyjnius*/*/pyjnius"))
    if not pyjnius_dirs:
        print("No pyjnius directories found!")
        return False
    
    fixed_any = False
    
    for pyjnius_dir in pyjnius_dirs:
        print(f"Checking pyjnius directory: {pyjnius_dir}")
        
        # Find all .pxi files
        pxi_files = list(pyjnius_dir.rglob("*.pxi"))
        
        for pxi_file in pxi_files:
            print(f"Checking file: {pxi_file}")
            
            try:
                # Read the file
                with open(pxi_file, 'r') as f:
                    content = f.read()
                
                # Check if fix is needed - look for all long references
                if "long" in content:
                    print(f"Fixing Python 3+ compatibility in {pxi_file}")
                    
                    # Apply all the fixes
                    content = content.replace(
                        "isinstance(arg, long)",
                        "isinstance(arg, int)"
                    )
                    content = content.replace(
                        "(int, long)",
                        "(int,)"
                    )
                    content = content.replace(
                        ", long)",
                        ")"
                    )
                    # Fix dictionary references like "long: 'J'"
                    content = content.replace(
                        "long: 'J',",
                        "int: 'J',"
                    )
                    content = content.replace(
                        "long: 'J'",
                        "int: 'J'"
                    )
                    # Fix PY2 conditional references like "(PY2 and tp == long)"
                    content = content.replace(
                        "tp == long)",
                        "tp == int)"
                    )
                    
                    # Write back the fixed content
                    with open(pxi_file, 'w') as f:
                        f.write(content)
                    
                    print(f"Successfully fixed {pxi_file}")
                    fixed_any = True
                else:
                    print(f"File {pxi_file} doesn't need fixing")
                    
            except Exception as e:
                print(f"Error fixing {pxi_file}: {e}")
    
    return fixed_any

if __name__ == "__main__":
    if fix_pyjnius_files():
        print("Pyjnius files have been fixed. You can now run the build again.")
        print("Command: buildozer --profile local android debug")
    else:
        print("No pyjnius files were found or needed fixing.")
        print("Make sure the build has been started at least once to create the pyjnius directories.")