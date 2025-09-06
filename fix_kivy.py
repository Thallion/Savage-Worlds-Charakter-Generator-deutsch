#!/usr/bin/env python3
"""
Fix Kivy Python 3+ compatibility issues
"""
import os
import sys
from pathlib import Path

def fix_kivy_files():
    """Fix Python 3+ compatibility issues in Kivy files"""
    print("Searching for Kivy build directories...")
    
    # Find kivy build directories
    build_root = Path(".buildozer/android/platform/build-arm64-v8a/build/other_builds")
    if not build_root.exists():
        print("Build directory not found!")
        return False
    
    kivy_dirs = list(build_root.glob("kivy*/*/kivy"))
    if not kivy_dirs:
        print("No kivy directories found!")
        return False
    
    fixed_any = False
    
    for kivy_dir in kivy_dirs:
        print(f"Checking kivy directory: {kivy_dir}")
        
        # Find all .pyx and .pxd files
        pyx_files = list(kivy_dir.rglob("*.pyx"))
        pxd_files = list(kivy_dir.rglob("*.pxd"))
        
        for pyx_file in pyx_files:
            print(f"Checking file: {pyx_file}")
            
            try:
                # Read the file
                with open(pyx_file, 'r') as f:
                    content = f.read()
                
                # Check if fix is needed - look for any long references
                if ("def __long__(self):" in content and "return long(" in content) or \
                   ("if PY_MAJOR_VERSION < 3:" in content and "return long(" in content) or \
                   ("IF PY_MAJOR_VERSION < 3:" in content and "return long(" in content) or \
                   ("cdef long " in content) or ("= long(" in content) or \
                   ("(long, " in content) or (", long)" in content):
                    print(f"Fixing Python 3+ compatibility in {pyx_file}")
                    
                    # Add necessary imports at top if not present
                    if "from cpython.version cimport PY_MAJOR_VERSION" not in content:
                        # Find a good place to add the import (after existing imports or at top)
                        lines = content.split('\n')
                        import_added = False
                        for i, line in enumerate(lines):
                            if line.startswith('from ') or line.startswith('import ') or line.startswith('cimport '):
                                continue
                            elif not line.strip() or line.strip().startswith('#'):
                                continue
                            else:
                                # Insert import before the first non-import line
                                lines.insert(i, "from cpython.version cimport PY_MAJOR_VERSION")
                                import_added = True
                                break
                        if not import_added:
                            # If no good place found, add at beginning
                            lines.insert(0, "from cpython.version cimport PY_MAJOR_VERSION")
                        content = '\n'.join(lines)
                    
                    # Remove the __long__ method entirely for Python 3+ 
                    # Since Python 3 doesn't have long type, we can just remove this method
                    old_pattern = """    def __long__(self):
        return long(self.__ref__())"""
                    
                    # Simply remove the method for Python 3+
                    new_pattern = ""
                    
                    content = content.replace(old_pattern, new_pattern)
                    
                    # Also handle the case where we already applied other fixes
                    old_runtime_pattern = """    def __long__(self):
        if PY_MAJOR_VERSION < 3:
            return long(self.__ref__())
        else:
            return int(self.__ref__())"""
                    
                    content = content.replace(old_runtime_pattern, new_pattern)
                    
                    old_compile_pattern = """    IF PY_MAJOR_VERSION < 3:
        def __long__(self):
            return long(self.__ref__())
    ELSE:
        def __long__(self):
            return int(self.__ref__())"""
                    
                    content = content.replace(old_compile_pattern, new_pattern)
                    
                    # Fix cdef long declarations - replace with cdef int
                    import re
                    # Use regex to replace only "cdef long " followed by a variable name (not "long long")
                    content = re.sub(r'cdef long(?!\s+long)\s+', 'cdef int ', content)
                    
                    # Also fix any "long long long" mistakes from previous runs
                    content = content.replace("cdef long long long ", "cdef int ")
                    
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
                    
                    print(f"Successfully fixed {pyx_file}")
                    fixed_any = True
                else:
                    print(f"File {pyx_file} doesn't need fixing")
                    
            except Exception as e:
                print(f"Error fixing {pyx_file}: {e}")
        
        # Now process .pxd files
        for pxd_file in pxd_files:
            print(f"Checking header file: {pxd_file}")
            
            try:
                # Read the file
                with open(pxd_file, 'r') as f:
                    content = f.read()
                
                # Check if fix is needed - look for long declarations
                if ("cdef long " in content):
                    print(f"Fixing Python 3+ compatibility in {pxd_file}")
                    
                    # Fix cdef long declarations - replace with cdef int
                    import re
                    # Use regex to replace only "cdef long " followed by a variable name (not "long long")
                    content = re.sub(r'cdef long(?!\s+long)\s+', 'cdef int ', content)
                    
                    # Also fix any "long long long" mistakes from previous runs
                    content = content.replace("cdef long long long ", "cdef int ")
                    
                    # Write back the fixed content
                    with open(pxd_file, 'w') as f:
                        f.write(content)
                    
                    print(f"Successfully fixed {pxd_file}")
                    fixed_any = True
                else:
                    print(f"Header file {pxd_file} doesn't need fixing")
                    
            except Exception as e:
                print(f"Error fixing {pxd_file}: {e}")
    
    return fixed_any

if __name__ == "__main__":
    if fix_kivy_files():
        print("Kivy files have been fixed. You can now run the build again.")
        print("Command: buildozer --profile local android debug")
    else:
        print("No Kivy files were found or needed fixing.")
        print("Make sure the build has been started at least once to create the kivy directories.")