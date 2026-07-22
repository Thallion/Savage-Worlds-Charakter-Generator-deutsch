[← Zurück zur CLAUDE.md](../CLAUDE.md)

# Build & Distribution

```bash
# Desktop builds (PyInstaller)
python build_linux.py          # Linux
python build_windows.py        # Windows
python build_all.py            # All platforms

# Android (Buildozer)
python build_android.py        # Android APK
buildozer android debug        # Direct Buildozer

# Windows via Wine (on Linux)
python build_windows_wine.py
```

## Build-Specs
- `savage_worlds_generator.spec` (Windows)
- `savage_worlds_generator_linux.spec` (Linux)
- `savage_worlds_generator_wine.spec` (Wine)
- `buildozer.spec` (Android)

## Android: API-Level & Voraussetzungen

- **targetSdk / `android.api` = 36** (Android 16), `android.minapi = 21`
- SDK Platform 36 + Build-Tools müssen im lokalen SDK (`android.sdk_path`) installiert sein — `android.skip_update = True` verhindert den Auto-Download durch buildozer
- `build_fixes.py` (p4a.hook) injiziert u.a. den **Predictive-Back-Opt-out** (`android:enableOnBackInvokedCallback="false"`) ins Manifest — ohne ihn erhält Kivy ab targetSdk 36 kein `KEYCODE_BACK` mehr. Details: [ANDROID_WORKAROUNDS.md](ANDROID_WORKAROUNDS.md)
