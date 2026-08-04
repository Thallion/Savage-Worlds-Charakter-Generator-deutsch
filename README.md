# 🎲 Savage Worlds Charakter-Generator

Moderner, benutzerfreundlicher Charakter-Generator für das Savage Worlds Rollenspielsystem. Entwickelt mit Python und KivyMD 2.0.1 für eine zeitgemäße Material Design Oberfläche.

## ✨ Features

### 🎯 Kern-Funktionalitäten
- **Vollständige Charaktererstellung** nach Savage Worlds Regeln
- **Geführte Tutorials & Assistenten** für neue Benutzer
- **Interaktive Benutzeroberfläche** mit Material Design
- **PDF-Export** für professionelle Charakterbögen
- **Speichern/Laden** von Charakteren im JSON-Format
- **Multi-Setting Support** (SWAE, Deadlands, Fantasy Kompendium, Savage Pathfinder, HeXXen 1773, Sundered Skies, Horror Kompendium, Rippers, SciFi Kompendium, Superkräfte Kompendium, 50 Fathoms, Hellfrost)
- **Android-App** mit optimiertem Mobile-Layout

### 🎨 UI/UX Features
- **Dark/Light Theme** Support
- **Responsive Design** für Desktop und Smartphone (automatische Layout-Erkennung)
- **Intuitive Navigation** mit Tab-System (Desktop) und Bottom-Navigation (Mobile)
- **Non-blocking Snackbar-Benachrichtigungen** für Statusmeldungen
- **Real-time Validation** bei Eingaben

### 🧙‍♂️ Tutorials & Assistenten
- **Willkommens-Tutorial** mit Spotlight-Funktion für neue Benutzer
- **Tab-spezifische Hilfen** mit kontextbezogenen Tipps für jeden Bereich
- **Setting-Assistent** für die Erstellung und Bearbeitung eigener Settings
- **Template-Wizard** für die benutzerfreundliche Charakter-Vorlagen-Erstellung
- **Charaktererstellungs-Assistent** für geführte Schritt-für-Schritt-Erstellung

### 🔧 Technische Features
- **Automatische Punkteverteilung** mit Regelvalidierung
- **Vollständige Talente-Datenbank** mit Voraussetzungen
- **Handicaps-System** mit Punkteberechnung
- **Ausrüstungsmanager** mit Gewichts- und Kostenkalkulation
- **Backup-System** für Charakterdateien

## 🚀 Installation & Start

### Systemanforderungen
- **Python**: 3.8 oder höher
- **RAM**: Minimum 2GB, empfohlen 4GB+
- **Speicher**: ~100MB für Dependencies + ~50MB für Anwendung
- **Display**: Minimum 1024x768, empfohlen 1920x1080+

### Quick Setup

1. **Repository klonen:**
```bash
git clone https://github.com/Thallion/Savage-Worlds-Charakter-Generator-deutsch.git
cd Savage-Worlds-Charakter-Generator-deutsch
```

2. **Virtuelle Umgebung erstellen (empfohlen):**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

3. **System-Abhängigkeiten installieren (Linux):**

KivyMD benötigt `pycairo`, das C-Erweiterungen kompiliert. Dafür werden System-Pakete benötigt:

```bash
# Debian/Ubuntu:
sudo apt-get install python3-dev libcairo2-dev libffi-dev pkg-config libjpeg-dev zlib1g-dev

# Fedora/RHEL/CentOS:
sudo dnf install python3-devel cairo-devel gcc pkg-config libjpeg-devel zlib-devel

# Arch Linux:
sudo pacman -S cairo pkgconf
```

4. **Dependencies installieren:**
```bash
pip install -r requirements.txt
```

**Hinweis zu KivyMD:** Die aktuelle KivyMD 2.0.1 Version wird direkt von GitHub installiert, da sie noch nicht offiziell auf PyPI verfügbar ist.

5. **Anwendung starten:**
```bash
python main.py
```

### Alternative Installation (bei Problemen)

Falls die requirements.txt Installation fehlschlägt:

```bash
# Manuell installieren (gepinnter Commit wie in requirements.txt):
pip install https://github.com/kivymd/KivyMD/archive/365aa9b96eee63e0e29c04de297dd222f478fce5.zip
pip install "kivy>=2.3.1,<3.0"
pip install reportlab>=3.6.0
pip install Pillow>=8.0.0
pip install python-dateutil>=2.8.0
```

## 🎮 Verwendung

### Willkommens-Tutorial (für Einsteiger)
Beim ersten Start der App wird automatisch ein geführtes Tutorial angezeigt:
- **Übersicht** der wichtigsten Funktionen und Navigation
- **Spotlight-Highlights** zeigen wichtige UI-Bereiche
- **Schritt-für-Schritt-Anleitung** für die erste Charaktererstellung
- **Tab-spezifische Hilfen** können jederzeit über das Fragezeichen-Symbol aufgerufen werden

Das Tutorial kann in den **Einstellungen** jederzeit erneut gestartet werden.

### Ersten Charakter erstellen
**Empfohlene Reihenfolge (auch im Tutorial gezeigt):**
1. **Setting wählen**: Zuerst ein Spielsetting auswählen (bestimmt verfügbare Völker, Talente, etc.)
2. **Neuer Charakter**: Über "Speichern/Laden" → "Neuer Charakter"
3. **Volk**: Gewünschtes Volk auswählen (Menschen, Elfen, Zwerge, etc.)
4. **Profil**: Name, Alter, Geschlecht und Konzept eingeben
5. **Eigenschaften**: Attribut- und Fertigkeitspunkte verteilen
6. **Handicaps**: Optional Handicaps für Bonuspunkte wählen
7. **Talente**: Talente mit erworbenen Punkten auswählen
8. **Mächte/Superkräfte**: Bei entsprechenden Talenten verfügbar
9. **Ausrüstung**: Waffen, Rüstung und Gegenstände kaufen
10. **Charakterbogen**: Finalen Charakter prüfen und als PDF exportieren

### Assistenten verwenden

**Setting-Assistent** (für fortgeschrittene Benutzer):
- Über Einstellungen zugänglich
- 4-Schritt-Wizard zum Erstellen eigener Settings
- Merge-Funktion zum Kombinieren bestehender Settings

**Template-Wizard**:
- Erstellt Charakter-Vorlagen aus fertigen Charakteren  
- Mehrstufiger Dialog für detaillierte Template-Konfiguration
- Templates können später für automatische Charaktererstellung verwendet werden

### Charaktere verwalten
- **Speichern**: `Datei > Speichern` oder `Strg+S`
- **Laden**: `Datei > Öffnen` oder `Strg+O`
- **PDF-Export**: `Datei > Als PDF exportieren`
- **Neuer Charakter**: `Datei > Neu` oder `Strg+N`

### Settings wechseln
1. In den Einstellungen das gewünschte Setting auswählen
2. Anwendung neu starten für vollständige Aktivierung
3. Neue Talente und Handicaps werden automatisch geladen

## 🛠️ Projekt-Struktur

```
Savage-Worlds-Charakter-Generator-deutsch/
├── main.py                 # Einstiegspunkt der Anwendung
├── main.kv                 # Root Kivy Layout
├── models/                 # Datenmodelle (Charakter, Attribute, Waffen, etc.)
├── views/                  # UI-Komponenten und Layouts
│   ├── *_view.py/.kv       # Desktop-Layouts (12 Tab-Views)
│   ├── *_view_mobile.kv    # Smartphone-optimierte Layouts (12 Mobile-Varianten)
│   └── *_popup.py/.kv      # Modale Dialoge (11 Popups)
├── controllers/            # Geschäftslogik und App-Steuerung
├── services/               # Service Container (DI), Dialog, Theme, Backup, HTML, etc.
├── functions/              # Spielmechanik-Funktionen (inkl. Cyberware)
├── manager/                # Domain-Manager (PDF, HTML, Statistik, Völker)
├── settings/               # Spielsetting-Daten (12 Settings als JSON)
├── config/                 # App-Konfiguration (JSON)
├── templates/              # Charakter-Vorlagen (43+ Templates als JSON)
├── utils/                  # Hilfsfunktionen (Logging, Pfade, Plattform, Sharing)
├── assets/                 # Ressourcen (Bilder, Logos)
├── docs/                   # Dokumentation und Planungen
├── scripts/                # Utility-Skripte
├── test units/             # Test-Suite (30+ Testmodule, unittest)
├── requirements.txt        # Python-Dependencies
└── README.md               # Diese Datei
```

## 🐛 Troubleshooting

### Häufige Probleme

**"ModuleNotFoundError: No module named 'kivymd'"**
```bash
# KivyMD von GitHub installieren (nicht von PyPI) — gepinnter Commit:
pip install https://github.com/kivymd/KivyMD/archive/365aa9b96eee63e0e29c04de297dd222f478fce5.zip
```

**KivyMD Installation schlägt fehl:**
```bash
# Zuerst Kivy installieren, dann KivyMD
pip install "kivy>=2.3.1,<3.0"
pip install https://github.com/kivymd/KivyMD/archive/365aa9b96eee63e0e29c04de297dd222f478fce5.zip
```

**Linux: pycairo / "Python dependency not found" / "command 'gcc' failed"**

KivyMD hängt von `pycairo` ab, das System-Bibliotheken zum Kompilieren benötigt:

```bash
# Debian/Ubuntu:
sudo apt-get install python3-dev libcairo2-dev libffi-dev pkg-config libjpeg-dev zlib1g-dev

# Fedora/RHEL/CentOS:
sudo dnf install python3-devel cairo-devel gcc pkg-config libjpeg-devel zlib-devel

# Arch Linux:
sudo pacman -S cairo pkgconf
```

Danach erneut `pip install -r requirements.txt` ausführen.

**Windows: "Microsoft Visual C++ 14.0 is required"**
- Visual Studio Build Tools installieren oder
- Vorkompilierte Wheels verwenden: `pip install --only-binary=all kivymd`

**Performance Probleme:**
- Mindestens Python 3.9+ verwenden
- 4GB+ RAM sicherstellen  
- SSD für bessere Ladezeiten nutzen

**PDF-Export funktioniert nicht:**
```bash
pip install --upgrade reportlab
```

## 📦 Build & Distribution

### Desktop (PyInstaller)

```bash
python build_linux.py          # Linux
python build_windows.py        # Windows
python build_desktop.py        # Plattform-automatisch
```

### Android (Buildozer)

```bash
buildozer android debug        # Debug APK
bash build_android_local.sh    # Lokaler Android Build
```

Siehe [README_BUILD.md](README_BUILD.md) und [README_CROSS_PLATFORM_BUILD.md](README_CROSS_PLATFORM_BUILD.md) für Details.

## 🔄 Updates

```bash
# Repository aktualisieren
git pull

# Dependencies aktualisieren
pip install --upgrade -r requirements.txt

# Anwendung neu starten
python main.py
```

## 📄 Lizenz & Rechtliches

### Creative Commons Lizenz
Dieses Projekt ist lizenziert unter der **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License** - siehe [LICENSE.md](LICENSE.md) für Details.

**Kurz gesagt:**
- ✅ Freie Nutzung für private und Bildungszwecke
- ✅ Modifikationen und Weitergabe erlaubt
- ❌ Keine kommerzielle Nutzung
- 📋 Namensnennung erforderlich
- 🔄 Weitergabe unter gleichen Bedingungen

### Savage Worlds Fan-Produkt
„Dieses Produkt bezieht sich auf das Regelsystem Savage Worlds, erhältlich bei der Pinnacle Entertainment Group unter www.peginc.com. Savage Worlds und alle zugehörigen Logos und Warenzeichen sind urheberrechtlich geschützt durch die Pinnacle Entertainment Group. Verwendung mit Genehmigung. Die deutsche Übersetzung der Begrifflichkeiten von Ulisses Spiele darf verwendet werden. Pinnacle oder Ulisses Spiele geben keine Zusicherungen oder Garantien in Bezug auf die Qualität, Funktionsfähigkeit oder Eignung dieses Produkts für einen bestimmten Zweck."

### Copyright
Copyright (c) 2025-2026 Jean-Michel Fenske (Thallion)

## 🤝 Beitragen

Verbesserungsvorschläge und Bug-Reports sind willkommen:
1. [Issue erstellen](https://github.com/Thallion/Savage-Worlds-Charakter-Generator-deutsch/issues) für Bug-Reports oder Feature-Requests
2. Fork & Pull Request für Code-Beiträge

## 🙏 Danksagungen

- **Pinnacle Entertainment Group** für das großartige Savage Worlds System
- **Ulisses Spiele** für die deutsche Übersetzung und Lokalisierung
- **KivyMD Team** für das exzellente UI Framework
- **Python Community** für die fantastischen Libraries
- **Community** für Feedback und Bug-Reports