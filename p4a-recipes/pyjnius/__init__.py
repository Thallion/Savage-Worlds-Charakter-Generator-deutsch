from pythonforandroid.recipe import CythonRecipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint, info
import sh
from os.path import join


class PyjniusRecipe(CythonRecipe):
    """
    Recipe for pyjnius with Python 3+ compatibility fixes
    """
    version = "1.4.2" 
    url = "https://github.com/kivy/pyjnius/archive/{version}.tar.gz"
    name = "pyjnius"
    depends = ["six"]
    site_packages_name = "jnius"
    
    def get_recipe_env(self, arch, with_flags_in_cc=True, with_python=True):
        env = super().get_recipe_env(arch, with_flags_in_cc, with_python)
        return env
    
    def apply_patch(self, arch):
        super().apply_patch(arch)
        # Fix Python 3+ compatibility issues BEFORE cythonizing
        info("Fixing Python 3+ compatibility in pyjnius")
        jnius_dir = join(self.get_build_dir(arch.arch), "jnius")
        
        try:
            import re
            # Fix all .pxi and .pyx files in jnius directory
            import os
            for root, dirs, files in os.walk(jnius_dir):
                for file in files:
                    if file.endswith('.pxi') or file.endswith('.pyx'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                        original = content
                        
                        # Fix 1: isinstance(arg, long) → isinstance(arg, int)
                        content = content.replace("isinstance(arg, long)", "isinstance(arg, int)")
                        content = content.replace("isinstance(obj, long)", "isinstance(obj, int)")
                        content = re.sub(r'isinstance\((\w+),\s*long\)', r'isinstance(\1, int)', content)
                        
                        # Fix 2: (int, long) Tuples → (int,)
                        content = content.replace("(int, long)", "(int,)")
                        content = content.replace("(long, int)", "(int,)")
                        
                        # Fix 3: isinstance(py_arg, (int, long)) → isinstance(py_arg, int)
                        content = re.sub(r'isinstance\((\w+),\s*\(int,\s*long\)\)', r'isinstance(\1, int)', content)
                        content = re.sub(r'isinstance\((\w+),\s*\(long,\s*int\)\)', r'isinstance(\1, int)', content)
                        
                        # Fix 4: long: 'J' → int: 'J' (in Dicts)
                        content = content.replace("long: 'J',", "int: 'J',")
                        content = content.replace("long: 'J'", "int: 'J'")
                        
                        # Fix 5: tp == long → tp == int
                        content = content.replace("tp == long)", "tp == int)")
                        content = content.replace("tp == long ", "tp == int ")
                        
                        # Fix 6: , long) am Ende von Tuples
                        content = re.sub(r',\s*long\)', ')', content)
                        
                        if content != original:
                            with open(file_path, 'w') as f:
                                f.write(content)
                            info(f"Fixed Python 3+ compatibility in {file}")
            
            info("Successfully fixed Python 3+ compatibility in pyjnius")
        except Exception as e:
            info(f"Could not apply pyjnius fix: {e}")


recipe = PyjniusRecipe()