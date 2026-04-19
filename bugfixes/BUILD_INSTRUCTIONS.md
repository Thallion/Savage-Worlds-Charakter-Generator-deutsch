# Building the Kivy Bugfixes Test App

This directory contains a minimal Kivy/KivyMD test app to reproduce and fix Android build issues.

## Prerequisites

- Python 3.8+ with virtualenv recommended
- Buildozer installed (`pip install buildozer`)
- Android SDK/NDK configured (via buildozer)
- Kivy and KivyMD dependencies (installed automatically)

## Build Configuration

The `buildozer.spec` file has been configured with:

- Python 3.11.13
- Kivy 2.3.0
- KivyMD from GitHub master
- Android API 33 (minimum 21)
- ARM64-v8a architecture
- Local recipes for pyjnius and python3 (with Python 3+ compatibility fixes)
- Hook script `build_fixes.py` for automatic patching

## Build Scripts

Two build scripts are provided for easy building. By default, they perform a **full clean rebuild** (force + clean) to ensure all compatibility fixes are applied correctly.

### `build.py` (Python version)
```bash
python build.py [--incremental] [--no-clean] [--no-force] [--debug]
```

### `build.sh` (Bash version)
```bash
./build.sh [--incremental] [--no-clean] [--no-force] [--debug]
```

**Default behavior (no flags):** `--force --clean` (full clean rebuild)

**Options:**
- `--incremental`: Skip cleaning and forcing (incremental build, faster)
- `--no-clean`: Force rebuild but skip cleaning (keep downloaded packages)
- `--no-force`: Clean but don't force rebuild (reuse existing dist if possible)
- `--debug`: Enable verbose debug output

**Examples:**
```bash
# Full clean rebuild (recommended for first build or after changes)
./build.sh

# Incremental build (faster, for quick testing)
./build.sh --incremental

# Force rebuild without cleaning (keep downloaded SDK/NDK)
./build.sh --no-clean

# Clean without forcing (reuse compiled recipes)
./build.sh --no-force

# Debug output
./build.sh --debug
```

## Manual Build Steps

If you prefer to run buildozer manually (scripts automate these steps):

1. Apply compatibility fixes:
   ```bash
   python build_fixes.py
   ```

2. For a full clean rebuild (recommended):
   ```bash
   buildozer android clean
   buildozer android debug --force-build
   ```

3. For incremental builds (faster testing):
   ```bash
   buildozer android debug
   ```

4. For force rebuild without cleaning:
   ```bash
   buildozer android debug --force-build
   ```

5. For cleaning without forcing:
   ```bash
   buildozer android clean
   buildozer android debug
   ```

## Fixes Applied

The build system includes the following fixes:

### 1. Python 3+ / Cython 3.x Compatibility
- **PyJNIus**: All `isinstance(arg, long)` references replaced with `isinstance(arg, int)`
- **Kivy**: `long()` function calls replaced with `int()`, `__long__` methods removed
- **Tuples**: `(int, long)` and `(long, int)` tuples replaced with `(int,)`

### 2. Android Manifest FileProvider
- FileProvider declaration added to AndroidManifest.xml for file sharing compatibility

### 3. Local Recipes
- Custom `pyjnius` recipe with enhanced patching in `apply_patch` method
- Custom `python3` recipe matching the main app's version

## Known Issues & Workarounds

### Cython "long" Type Errors
The primary crash was due to `undeclared name not builtin: long` errors in PyJNIus. This has been fixed by patching the `.pxi` files. The fixes are applied:

1. **Automatically** via the hook script `build_fixes.py` (runs during build)
2. **Manually** via the local recipe's `apply_patch` method
3. **Fallback** manual patches applied to already-unpacked sources

### Android Touch Bounce Issues
The app includes the standard Kivy/KivyMD Android workarounds:
- `TextFieldScrollView` for proper text field focus
- Checkbox debounce pattern (500ms timeout)
- Separate popup dialogs for checkbox lists

### Broadcast Receiver API 31+ Compatibility
If you encounter `RECEIVER_EXPORTED` / `RECEIVER_NOT_EXPORTED` errors, you may need to:
1. Set `android.api = 31` or higher in `buildozer.spec`
2. Add appropriate receiver flags in Android manifest (already handled by Kivy's bootstrap)

## Testing the APK

After successful build, install the APK on an Android device:

```bash
adb install bin/kivybugfixes-0.1.0-arm64-v8a-debug.apk
```

Or use buildozer's install command:

```bash
buildozer android deploy
```

## Troubleshooting

### Build Fails with Cython Errors
- Check that `build_fixes.py` ran successfully (look for "P4A Hook" messages)
- Verify patches were applied: `grep -r "isinstance.*long" .buildozer/android/platform/build-*/build/other_builds/pyjnius/`
- Manually apply missing patches if needed

### Build Takes Too Long
- Use `--force` only when necessary (clean rebuild)
- Buildozer caches downloads in `~/.buildozer/cache`

### APK Crashes on Launch
Check Logcat for errors:
```bash
adb logcat -s python
adb logcat -s DEBUG
```

Common issues:
1. Missing permissions (already included: INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE)
2. Native library conflicts (ensure single architecture build)
3. Python module import errors

## Directory Structure

```
bugfixes/
├── main.py              # Test app source
├── buildozer.spec       # Build configuration
├── build_fixes.py       # Compatibility hook script
├── build.py             # Python build script
├── build.sh             # Bash build script
├── BUILD_INSTRUCTIONS.md # This file
└── .buildozer/          # Build directories (generated)
```

## Related Files in Main Project

- `../buildozer.spec` - Main app's build configuration (reference)
- `../p4a-recipes/` - Local recipes used by both main app and test app
- `../bugfixes/` - This test app directory

## License

Same as main project: CC BY-NC-SA 4.0