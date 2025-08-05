# Savage Worlds Charakter-Generator

Ein moderner, plattformübergreifender Charakter-Generator für das Savage Worlds Rollenspielsystem, entwickelt mit Python und KivyMD 2.0.1.

## 📋 Überblick

Diese Anwendung ermöglicht es Spielern und Spielleitern, schnell und einfach Charaktere für Savage Worlds zu erstellen und zu verwalten. Das Projekt folgt modernen Softwareentwicklungsprinzipien wie Clean Code, Domain-Driven Design (DDD) und dem Model-View-Controller (MVC) Pattern.

## ✨ Features

### Kern-Features
- **Vollständige Charaktererstellung** nach Savage Worlds Regeln
- **Multi-Setting Support** (SWAE, Savage Pathfinder, etc.)
- **Völker-System** mit automatischen Attributs- und Talentboni
- **Attribute & Fertigkeiten** mit Würfel-System (W4-W12+)
- **Talente & Handicaps** mit Voraussetzungsprüfung
- **Mächte-System** für arkane Charaktere
- **Ausrüstung-Verwaltung** (Waffen, Rüstungen, Schilde, Gegenstände)
- **PDF-Export** für Charakterbögen
- **Statblock-Generator** für schnelle Referenz

### UI/UX Features
- **Moderne KivyMD 2.0.1 Oberfläche** mit Material Design
- **Dark/Light Theme** Support
- **Responsive Design** für verschiedene Bildschirmgrößen
- **Tab-Navigation** mit intuitiver Benutzerführung
- **Tooltips & Hilfe-Texte** für bessere Benutzerführung

### Technische Features
- **MVC-Architektur** für saubere Trennung der Verantwortlichkeiten
- **Service Container** für Dependency Injection
- **Event-System** für lose Kopplung
- **Config-Service** für persistente Einstellungen
- **Dialog-Service** für einheitliche Benutzerinteraktion
- **Threading** für bessere Performance
- **Caching** für optimierte Render-Performance

## 🏗️ Projekt-Struktur

```
savage-worlds-generator/
├── main.py                     # Hauptanwendung
├── charakter.py               # Charakter-Kernmodell
├── controllers/               # Controller-Schicht (MVC)
│   └── charakter_controller.py
├── models/                    # Datenmodelle
│   ├── attribut.py
│   ├── fertigkeit.py
│   ├── talent.py
│   ├── handicap.py
│   ├── macht.py
│   ├── ausruestung.py
│   ├── waffe.py
│   ├── ruestung.py
│   ├── schild.py
│   ├── volk.py
│   └── wuerfel.py
├── views/                     # UI-Komponenten (MVC)
│   ├── eigenschaften_view.py
│   ├── voelker_view.py
│   ├── profil_view.py
│   ├── talente_view.py
│   ├── handicaps_view.py
│   ├── maechte_view.py
│   ├── ausruestung_view.py
│   ├── charakterbogen_view.py
│   ├── pointbar_view.py
│   └── einstellungen_widget.py
├── services/                  # Hilfsdienste
│   ├── service_container.py
│   ├── config_service.py
│   ├── theme_service.py
│   ├── dialog_service.py
│   ├── event_service.py
│   ├── file_manager_service.py
│   └── pdf_service.py
├── functions/                 # Domänen-spezifische Funktionen
│   ├── eigenschaften_funktionen.py
│   ├── volk_funktionen.py
│   ├── setting_funktionen.py
│   ├── charakter_speicher.py
│   └── statblock_generator.py
├── settings/                  # Spiel-Settings und Regeln
├── assets/                    # Bilder und Ressourcen
└── config/                    # Anwendungskonfiguration
```

## 🚀 Installation

### Voraussetzungen
- Python 3.8 oder höher
- Git (für Entwicklung)

### Dependencies
```python
# Core Dependencies
kivy>=2.1.0
kivymd==2.0.1
python-dateutil>=2.8.0

# Optional Dependencies
reportlab>=3.6.0      # PDF-Export
pillow>=8.0.0         # Bildverarbeitung
```

### Setup
1. Repository klonen:
```bash
git clone [repository-url]
cd savage-worlds-generator
```

2. Virtuelle Umgebung erstellen (empfohlen):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

3. Dependencies installieren:
```bash
pip install -r requirements.txt
```

4. Anwendung starten:
```bash
python main.py
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

### Settings wechseln
1. In den Einstellungen das gewünschte Setting auswählen
2. Anwendung neu starten für vollständige Aktivierung

## 🛠️ Entwicklung

### Code-Standards
- **Clean Code**: Saubere, lesbare und wartbare Code-Basis
- **DDD**: Domain-Driven Design für fachliche Klarheit
- **MVC**: Strikte Trennung von Model, View und Controller
- **SOLID**: Befolgen der SOLID-Prinzipien
- **PEP 8**: Python Style Guide Konformität

### Architektur-Prinzipien
```python
# Model: Datenstruktur und Geschäftslogik
class Attribut:
    def __init__(self, attribut_name, wert=4, modifier=0):
        self.name = attribut_name
        self.wuerfel = Wuerfel(wert, modifier)

# View: UI-Komponente ohne Geschäftslogik
class EigenschaftenWidget(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = App.get_running_app().controller

# Controller: Vermittler zwischen Model und View
class CharakterController:
    def steigere_attribut(self, attribut_name):
        return self.charakter.steigere_attribut(attribut_name)
```

### Neue Features hinzufügen
1. **Model**: Datenstruktur in `models/` erstellen
2. **Function**: Geschäftslogik in `functions/` implementieren
3. **View**: UI-Komponente in `views/` entwickeln
4. **Controller**: Integration über Controller-Schicht
5. **Service**: Bei Bedarf Service für übergreifende Funktionalität

### Testing
- Unit Tests für Geschäftslogik in `functions/`
- Integration Tests für Controller-Schicht
- UI Tests für kritische Benutzerinteraktionen

## 📚 API-Dokumentation

### Charakter-API
```python
# Charakter erstellen
charakter = Charakter()

# Attribut steigern
result = charakter.steigere_attribut("Stärke")

# Talent auswählen
result = charakter.waehle_talent("Kämpfer")

# Charakter speichern
charakter.speichern_als_json("mein_held.json")
```

### Service-API
```python
# Theme ändern
theme_service = get_theme_service()
theme_service.switch_theme("dark")

# Dialog anzeigen
dialog_service = get_dialog_service()
dialog_service.show_info("Charakter gespeichert!")
```

## 🎨 KivyMD 2.0.1 Kompatibilität

Das Projekt verwendet die neueste KivyMD Version mit folgenden wichtigen Änderungen:

### Buttons
```python
# Neu in 2.0.1
button = MDButton(style="elevated")
button.add_widget(MDButtonText(text="Klick mich"))

# Alt (nicht mehr verfügbar)
# MDFlatButton, MDRaisedButton - entfernt
```

### Typography
```python
# Neu in 2.0.1
MDLabel(font_style="Headline")  # Statt H1, H2, etc.

# Alt
# font_style="H6" - entfernt
```

### Dialogs
```python
# Neu in 2.0.1
dialog = MDDialog(
    MDDialogHeadlineText(text="Titel"),
    MDDialogContentContainer(content),
    MDDialogButtonContainer(buttons)
)
```

## 🌟 Besondere Features

### Völker-System
- Automatische Attributs-/Talentboni
- Wahlmöglichkeiten für flexible Völker
- Halbelf-Unterstützung mit mehreren Optionen

### Savage Pathfinder Integration
- Kostenlose Anfänger-Talente
- Erweiterte Attributs-Steigerungen
- Spezielle Pathfinder-Regeln

### Performance-Optimierungen
- Threading für UI-Updates
- Caching für Würfel-Icons
- Lazy Loading für große Datensätze

## 📄 Lizenz

Dieses Produkt bezieht sich auf das Regelsystem Savage Worlds, erhältlich bei der Pinnacle Entertainment Group unter www.peginc.com. Savage Worlds und alle zugehörigen Logos und Warenzeichen sind urheberrechtlich geschützt durch die Pinnacle Entertainment Group. Verwendung mit Genehmigung.

Die deutsche Übersetzung der Begrifflichkeiten von Ulisses Spiele darf verwendet werden. Pinnacle oder Ulisses Spiele geben keine Zusicherungen oder Garantien in Bezug auf die Qualität, Funktionsfähigkeit oder Eignung dieses Produkts für einen bestimmten Zweck.

## 🤝 Danksagungen

- **Pinnacle Entertainment Group** für das großartige Savage Worlds System
- **Ulisses Spiele** für die deutsche Übersetzung und Genehmigung
- **KivyMD Team** für das ausgezeichnete UI-Framework
- **Community** für Feedback und Bug-Reports

## 📞 Support

Bei Fragen oder Problemen:
1. Issues im Repository erstellen
2. Dokumentation prüfen
3. Ulisses Discord: Kanal Savage Worlds

## 🔄 Roadmap

### Geplante Features
- [ ] Kampagnen-Verwaltung
- [ ] Gruppen-Features
- [ ] Mobile App (Android)
- [ ] Linux App (Debian/Ubuntu)
- [ ] Erweitertes Setting-System

### Known Issues
- Siehe Issues im Repository

---

**Version**: 0.5.4.0  
**Letzte Aktualisierung**: August 2025  
**Entwickelt mit**: Python 3.12, KivyMD 2.0.1

## Lizenz
Dieses Projekt ist lizenziert unter der Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
Siehe [LICENSE](LICENSE) für Details.