# Cross-Platform Build Guide

## Das Problem
Du versuchst eine Windows .exe auf einem Linux-System zu erstellen. PyInstaller kann nur für das aktuelle Betriebssystem builden.

## Lösungen

### 1. 🐧 Linux Build (Aktuell funktionierend)
```bash
python build_desktop.py
```
**Ergebnis:** `dist/SavageWorldsCharakterGenerator/SavageWorldsCharakterGenerator` (Linux Binary)

### 2. 🪟 Windows Build (Benötigt Windows-System)

#### Option A: Auf Windows-System
1. Code auf Windows-Rechner kopieren
2. Python + Abhängigkeiten installieren
3. `python build_windows.py` ausführen

#### Option B: Mit Wine (Linux → Windows)
```bash
# Wine installieren
sudo apt install wine winetricks

# Windows Python in Wine installieren
winetricks python312

# Mit Wine builden
wine python build_windows.py
```

#### Option C: Mit Docker (Experimentell)
```bash
python docker_windows_build.py
```

### 3. 🍎 macOS Build (Benötigt macOS-System)
```bash
python build_desktop.py  # Auf macOS ausführen
```

## Cross-Compilation Alternativen

### PyInstaller Limitierungen
- **Windows .exe:** Nur auf Windows oder mit Wine
- **Linux Binary:** Nur auf Linux  
- **macOS App:** Nur auf macOS

### Alternative: GitHub Actions CI/CD
```yaml
# .github/workflows/build.yml
name: Multi-Platform Build

on: [push, pull_request]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python build_windows.py
      - uses: actions/upload-artifact@v3
        with:
          name: windows-exe
          path: dist/

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python build_linux.py
      - uses: actions/upload-artifact@v3
        with:
          name: linux-binary
          path: dist/
```

## Empfehlung für dich

Da du aktuell auf Linux entwickelst:

1. **Für Tests:** Nutze den funktionierenden Linux Build
   ```bash
   python build_desktop.py
   ```

2. **Für Windows-Distribution:** 
   - Nutze GitHub Actions für automatische Windows Builds
   - Oder bitte einen Windows-Nutzer um den Build
   - Oder teste Wine-basierte Cross-Compilation

3. **One-Directory Modus Vorteil bleibt:** 
   - Weniger Antiviren-Probleme auch bei späterem Windows Build
   - Transparente Dateistruktur
   - Bessere Debugging-Möglichkeiten

## Aktueller Status
✅ **Linux Build:** Vollständig funktionsfähig  
⏳ **Windows Build:** Benötigt Windows-System oder Wine  
⏳ **macOS Build:** Benötigt macOS-System