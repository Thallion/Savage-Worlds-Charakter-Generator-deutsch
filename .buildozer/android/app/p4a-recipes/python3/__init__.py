from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
import sh


class Python3Recipe(Recipe):
    version = "3.10.15"
    url = "https://www.python.org/ftp/python/{version}/Python-{version}.tgz"
    name = "python3"
    
    depends = ["hostpython3", "sqlite3", "openssl", "libffi"]
    conflicts = ["python2legacy", "python2"]
    opt_depends = ["openssl", "sqlite3"]
    
    configure_args = (
        "--host={android_host}",
        "--build={android_build}",
        "--enable-shared",
        "--disable-ipv6",
        "ac_cv_file__dev_ptmx=yes",
        "ac_cv_file__dev_ptc=no",
    )


recipe = Python3Recipe()