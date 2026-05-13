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
