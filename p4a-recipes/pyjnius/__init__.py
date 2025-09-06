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
    depends = ["genericndkbuild", "six"]
    site_packages_name = "jnius"
    
    def get_recipe_env(self, arch, with_flags_in_cc=True, with_python=True):
        env = super().get_recipe_env(arch, with_flags_in_cc, with_python)
        return env
    
    def apply_patch(self, arch):
        super().apply_patch(arch)
        # Fix Python 3+ compatibility issues BEFORE cythonizing
        info("Fixing Python 3+ compatibility in pyjnius")
        jnius_utils_path = join(self.get_build_dir(arch.arch), "jnius", "jnius_utils.pxi")
        
        try:
            # Read the file and fix the long type issue
            with open(jnius_utils_path, 'r') as f:
                content = f.read()
            
            # Replace isinstance(arg, long) with isinstance(arg, int) for Python 3+
            content = content.replace(
                "(isinstance(arg, long) and arg < 2147483648)",
                "(isinstance(arg, int) and arg < 2147483648)"
            )
            
            # Write the fixed content back
            with open(jnius_utils_path, 'w') as f:
                f.write(content)
            
            info("Successfully fixed Python 3+ compatibility in pyjnius")
        except Exception as e:
            info(f"Could not apply pyjnius fix: {e}")


recipe = PyjniusRecipe()