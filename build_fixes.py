#!/usr/bin/env python3
"""
Combined buildozer hook to fix Kivy and PyJNIus Python 3+ compatibility issues
"""
import os
import sys
import re
from pathlib import Path

def fix_kivy_python3_compatibility():
    """Fix Python 3+ compatibility issues in Kivy files"""
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
        
        # Find all .pyx files
        pyx_files = list(kivy_dir.rglob("*.pyx"))
        
        for pyx_file in pyx_files:
            try:
                # Read the file
                with open(pyx_file, 'r') as f:
                    content = f.read()
                
                # Check if fix is needed - look for __long__ method
                if ("def __long__(self):" in content and "return long(" in content):
                    print(f"P4A Hook: Fixing Python 3+ compatibility in {pyx_file}")
                    
                    # Remove the __long__ method entirely for Python 3+ 
                    old_pattern = """    def __long__(self):
        return long(self.__ref__())"""
                    
                    content = content.replace(old_pattern, "")
                    
                    # Fix cdef long declarations - replace with cdef int
                    content = re.sub(r'cdef long(?!\s+long)\s+', 'cdef int ', content)
                    
                    # Fix long() function calls - replace with int()
                    content = content.replace("= long(", "= int(")
                    
                    # Fix isinstance checks with long in tuples
                    content = content.replace("(long, int)", "(int,)")
                    content = content.replace("(int, long)", "(int,)")
                    content = content.replace("(long, ", "(")
                    content = content.replace(", long)", ")")
                    
                    # Write back the fixed content
                    with open(pyx_file, 'w') as f:
                        f.write(content)
                    
                    print(f"P4A Hook: Successfully fixed Kivy file {pyx_file}")
                    fixed_any = True
                    
            except Exception as e:
                print(f"P4A Hook: Error fixing Kivy file {pyx_file}: {e}")
    
    return fixed_any

def fix_pyjnius_python3_compatibility():
    """Fix Python 3+ compatibility issues in pyjnius"""
    print("P4A Hook: Searching for pyjnius build directories...")
    
    # Find pyjnius build directories
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
                    
                    # Apply other common fixes
                    content = content.replace("isinstance(arg, long)", "isinstance(arg, int)")
                    content = content.replace("(int, long)", "(int,)")
                    content = content.replace(", long)", ")")
                    content = content.replace("long: 'J',", "int: 'J',")
                    content = content.replace("long: 'J'", "int: 'J'")
                    content = content.replace("tp == long)", "tp == int)")
                    
                    # Write back the fixed content
                    with open(jnius_utils_file, 'w') as f:
                        f.write(content)
                    
                    print(f"P4A Hook: Successfully fixed Python 3+ compatibility in {jnius_utils_file}")
                    fixed_any = True
                else:
                    print(f"P4A Hook: File {jnius_utils_file} already appears to be fixed")
                    
            except Exception as e:
                print(f"P4A Hook: Error fixing {jnius_utils_file}: {e}")
        else:
            print(f"P4A Hook: jnius_utils.pxi not found in {pyjnius_dir}")
    
    return fixed_any

if __name__ == "__main__":
    print("P4A Hook: Starting build fixes...")
    
    # Run Kivy fixes
    kivy_fixed = fix_kivy_python3_compatibility()
    if kivy_fixed:
        print("P4A Hook: Kivy Python 3+ compatibility issues fixed")
    
    # Run pyjnius fixes  
    pyjnius_fixed = fix_pyjnius_python3_compatibility()
    if pyjnius_fixed:
        print("P4A Hook: PyJNIus Python 3+ compatibility issues fixed")
    
    if kivy_fixed or pyjnius_fixed:
        print("P4A Hook: Build fixes completed successfully")
    else:
        print("P4A Hook: No fixes were needed")