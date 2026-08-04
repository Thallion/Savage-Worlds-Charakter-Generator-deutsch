# Savage Worlds Generator - Build Dokumentation

## Android APK Build

### GitHub Actions (Empfohlen)

Verfügbare Workflows:

1. **android-buildozer-simple.yml** ⭐ **Empfohlen**
   - Verwendet bewährte `ArtemSBulgakov/buildozer-action@v1`
   - Einfach und stabil
   - Manual Trigger: Actions → "Build Android APK - Simple Buildozer"

2. **android-docker.yml** 
   - Docker-basiert mit `kivy/buildozer:latest`
   - Fallback auf Custom Docker
   - Manual Trigger: Actions → "Build Android APK - Docker Only"

3. **android-full-app.yml**
   - Vollständig konfigurierbar
   - Wählbare Architekturen (arm64-v8a, armeabi-v7a)
   - Build-Modi: debug/release

### Lokaler Build

```bash
# Mit Docker (erfordert Docker Installation)
./build_android_local.sh debug

# Oder direkt mit Buildozer
buildozer android debug
```

## Wichtige KivyMD Konfiguration

### buildozer.spec Requirements

```ini
requirements = python3,kivy,https://github.com/kivymd/KivyMD/archive/365aa9b96eee63e0e29c04de297dd222f478fce5.zip,materialyoucolor,pillow,reportlab,requests,android
```

**Wichtig:** KivyMD wird als GitHub-Archiv geladen, aber auf einen festen **Commit gepinnt** (reproduzierbare Builds; `master.zip` zöge bei jedem Build einen anderen Stand). Begründung und Update-Regel: `docs/ANDROID_WORKAROUNDS.md` Abschnitt "KivyMD-Versionspinning".

### Build-Bereinigung

Bei KivyMD Updates immer bereinigen:

```bash
buildozer android clean
# oder
rm -rf .buildozer
```

## Docker Setup

### Offizielles Kivy Buildozer Image

```bash
# Image laden
docker pull kivy/buildozer:latest

# Build ausführen
docker run --rm \
  --volume "$PWD":/home/user/hostcwd \
  --volume "$HOME/.buildozer":/home/user/.buildozer \
  --workdir /home/user/hostcwd \
  kivy/buildozer android debug
```

### Volume-Pfade beachten

- Projekt: `/home/user/hostcwd` (nicht `/home/user/app`)
- Cache: `/home/user/.buildozer`
- Arbeitsverzeichnis: `/home/user/hostcwd`

## Build-Konfiguration

### Android Versionen

```ini
android.api = 35          # Target API (aktuell)
android.minapi = 21       # Minimum API (Android 5.0)
android.ndk = 25b         # NDK Version
```

### Architekturen

- `armeabi-v7a` - 32-bit ARM (ältere Geräte)
- `arm64-v8a` - 64-bit ARM (moderne Geräte)
- `x86_64` - Intel (Emulatoren)

### Dependencies

- **kivy** - UI Framework
- **kivymd** - Material Design Komponenten
- **materialyoucolor** - KivyMD Abhängigkeit
- **pillow** - Bildverarbeitung
- **reportlab** - PDF Generierung
- **requests** - HTTP Requests
- **android** - Android-spezifische Features

## Troubleshooting

### Häufige Probleme

1. **KivyMD Import Fehler**
   ```bash
   buildozer android clean
   ```

2. **Permission Errors**
   ```bash
   sudo chown $USER -R ~/.buildozer
   ```

3. **SDK License Issues**
   ```bash
   yes | buildozer android update
   ```

4. **Docker Permission Errors**
   ```bash
   rm -rf ~/.buildozer && mkdir ~/.buildozer
   ```

### Build-Logs

Logs finden sich in:
- `.buildozer/logs/`
- `buildozer.log`
- GitHub Actions Artifacts

### Performance

- **Cache verwenden:** `~/.buildozer` Volume mounten
- **Clean builds:** Bei Dependency-Updates
- **Parallele Jobs:** `-j4` für lokale Builds

## Erfolgreiche Build-Konfiguration

✅ **Getestet mit:**
- Ubuntu 22.04
- Python 3.11
- KivyMD master branch
- Android API 35
- NDK 25b

✅ **Workflow Status:**
- Simple Buildozer: Funktional
- Docker Build: Funktional mit korrekten Pfaden
- Full App: Konfigurierbar für verschiedene Targets