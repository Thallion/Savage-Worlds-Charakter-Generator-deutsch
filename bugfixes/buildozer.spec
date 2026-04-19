[app]

# (str) Title of your application
title = Kivy Bugfixes Test

# (str) Package name
package.name = kivybugfixes

# (str) Package domain (needed for android/ios packaging)
package.domain = com.github.thallion

# (str) Application author
author = Jean-Michel Fenske (SavageThallion)

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,kv,md

# (list) List of inclusions using pattern matching
source.include_patterns = kivy/*.py,kivymd/*.py

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, .buildozer, __pycache__, .git

# (str) Application versioning (method 1)
version = 0.1.0

# (list) Application requirements
# Match the main app's Kivy/KivyMD versions for consistent bug reproduction.
# cython is required for building pyjnius
requirements = python3==3.11.13,kivy==2.3.0,https://github.com/kivymd/KivyMD/archive/master.zip,materialyoucolor,exceptiongroup,asyncgui,asynckivy,pillow

# (list) Supported orientations
orientation = landscape, portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = android.permission.INTERNET, android.permission.WRITE_EXTERNAL_STORAGE, android.permission.READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use.
android.ndk_api = 21

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = True

# (bool) If True, then automatically accept SDK license agreements.
android.accept_sdk_license = True

# (str) screenOrientation to set for the main activity.
android.manifest.orientation = user

# (str) launchMode for the main activity
android.manifest.launch_mode = singleTask

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (list) Gradle dependencies
android.gradle_dependencies = androidx.core:core-ktx:1.15.0, androidx.core:core:1.6.0

# (bool) Enable AndroidX support.
android.enable_androidx = True

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

# (str) The format used to package the app for release mode (aab or apk or aar).
android.release_artifact = apk

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use, defaults to master
p4a.branch = master

# (str) python-for-android specific commit to use, defaults to HEAD, must be within p4a.branch
p4a.commit = 957a3e5f

# (str) Directory containing the local recipes (pyjnius, python3)
p4a.local_recipes = ../p4a-recipes

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

# (str) p4a hook script to run before APK build (fixes Python 3+ compatibility)
p4a.hook = ./build_fixes.py


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
