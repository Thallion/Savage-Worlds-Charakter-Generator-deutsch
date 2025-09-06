# 🎲 Savage Worlds Charakter-Generator

Moderner, benutzerfreundlicher Charakter-Generator für das Savage Worlds Rollenspielsystem. Entwickelt mit Python und KivyMD 2.0.1 für eine zeitgemäße Material Design Oberfläche.

## ✨ Features

### 🎯 Kern-Funktionalitäten
- **Vollständige Charaktererstellung** nach Savage Worlds Regeln
- **Interaktive Benutzeroberfläche** mit Material Design
- **PDF-Export** für professionelle Charakterbögen
- **Speichern/Laden** von Charakteren im JSON-Format
- **Multi-Setting Support** (Deadlands, 50 Fathoms, etc.)

### 🎨 UI/UX Features
- **Dark/Light Theme** Support
- **Responsive Design** für verschiedene Bildschirmgrößen
- **Intuitive Navigation** mit Tab-System
- **Real-time Validation** bei Eingaben
- **Tooltips und Hilfe-Texte** für Anfänger

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

3. **Dependencies installieren:**
```bash
pip install -r requirements.txt
```

**Hinweis zu KivyMD:** Die aktuelle KivyMD 2.0.1 Version wird direkt von GitHub installiert, da sie noch nicht offiziell auf PyPI verfügbar ist.

4. **Anwendung starten:**
```bash
python main.py
```

### Alternative Installation (bei Problemen)

Falls die requirements.txt Installation fehlschlägt:

```bash
# Manuell installieren:
pip install https://github.com/kivymd/KivyMD/archive/master.zip
pip install kivy>=2.1.0
pip install reportlab>=3.6.0
pip install Pillow>=8.0.0
pip install python-dateutil>=2.8.0
```

## 🎮 Verwendung

### Ersten Charakter erstellen
1. **Profil**: Name, Alter, Geschlecht und Konzept eingeben
2. **Volk**: Gewünschtes Volk auswählen (Menschen, Elfen, Zwerge, etc.)
3. **Attribute**: Fünf Punkte auf Attribute verteilen
4. **Fertigkeiten**: 15 Punkte auf Fertigkeiten verteilen  
5. **Handicaps**: Optional Handicaps für zusätzliche Punkte wählen
6. **Talente**: Talente mit erworbenen Punkten auswählen
7. **Ausrüstung**: Waffen, Rüstung und Gegenstände auswählen

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
├── models/                 # Datenmodelle (Charakter, Attribute, etc.)
├── views/                  # UI-Komponenten und Layouts
├── controllers/            # Geschäftslogik und App-Steuerung
├── functions/              # Hilfsfunktionen (PDF-Export, Dateien, etc.)
├── data/                   # Spieldaten (Talente, Handicaps, Settings)
├── assets/                 # Ressourcen (Bilder, Fonts, Icons)
├── requirements.txt        # Python-Dependencies
└── README.md              # Diese Datei
```

## 🐛 Troubleshooting

### Häufige Probleme

**"ModuleNotFoundError: No module named 'kivymd'"**
```bash
# KivyMD von GitHub installieren (nicht von PyPI)
pip install https://github.com/kivymd/KivyMD/archive/master.zip
```

**KivyMD Installation schlägt fehl:**
```bash
# Zuerst Kivy installieren, dann KivyMD
pip install kivy>=2.1.0
pip install https://github.com/kivymd/KivyMD/archive/master.zip
```

**Linux: "command 'gcc' failed"**
```bash
sudo apt-get install python3-dev libffi-dev
sudo apt-get install libjpeg-dev zlib1g-dev  # für Pillow
```

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

## 📦 Executable erstellen (Optional)

Für Benutzer ohne Python-Installation:

```bash
# PyInstaller installieren
pip install pyinstaller

# Executable erstellen
pyinstaller --windowed --onefile main.py

# Executable findet sich dann in dist/
```

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
Copyright (c) 2025 Jean-Michel Fenske (Thallion)

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