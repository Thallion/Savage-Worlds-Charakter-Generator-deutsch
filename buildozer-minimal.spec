[app]
title = Savage Worlds Generator
package.name = savageworlds
package.domain = com.github.thallion
source.dir = .
source.include_exts = py,png,jpg,jpeg,json
source.exclude_dirs = tests, bin, venv, .buildozer, __pycache__, .git, .github
version = 0.5.5.8
requirements = python3==3.11.13,kivy==2.3.0,https://github.com/kivymd/KivyMD/archive/master.zip,materialyoucolor,exceptiongroup,asyncgui,asynckivy,pillow,reportlab,android

[buildozer]
log_level = 2

[app]
orientation = landscape
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
p4a.branch = develop
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
android.skip_update = True