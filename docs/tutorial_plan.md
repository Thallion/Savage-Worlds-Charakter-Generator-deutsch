# Plan: Geführtes User-Tutorial für den Savage Worlds Charakter-Generator

## Problemanalyse

Die App bietet 13 Tabs mit umfangreicher Funktionalität, aber:
- **Kein Onboarding** – Nutzer landen direkt auf dem Speichern/Laden-Tab
- **Keine kontextuelle Hilfe** – nur ein statischer Info-Tab mit Lizenztexten
- **Komplexe Workflows** – Reihenfolge der Charaktererstellung ist nicht offensichtlich
- **Versteckte Features** – Swipe-Navigation, Punktesystem, Undo etc. sind nicht erklärt
- **Fachbegriffe** – Savage-Worlds-Terminologie (Parade, Robustheit, Bennies) wird vorausgesetzt

---

## Konzept: Mehrstufiges Tutorial-System

### Drei Säulen

| Säule | Typ | Wann | Zweck |
|-------|-----|------|-------|
| **1. Willkommens-Tutorial** | Geführte Tour | Erster App-Start | Grundlegende Orientierung |
| **2. Tab-Hilfen** | Kontextuelle Tooltips | Bei Tab-Wechsel (optional) | Erklärung pro Bildschirm |
| **3. Schritt-für-Schritt-Assistent** | Wizard-Modus | Auf Wunsch | Komplette Charaktererstellung begleiten |

---

## Säule 1: Willkommens-Tutorial (First-Run)

### Auslöser
- Erster App-Start (Flag `tutorial_completed` in `app_config.json`)
- Manuell aufrufbar über Info-Tab oder Einstellungen

### Schritte (jeweils ein Overlay/Dialog)

#### Schritt 1: Willkommen
```
"Willkommen beim Savage Worlds Charakter-Generator!
Diese kurze Tour zeigt dir die wichtigsten Funktionen."
[Überspringen] [Weiter →]
```

#### Schritt 2: Tab-Leiste (Highlight auf Tab-Bar)
```
"Oben findest du die Hauptnavigation.
Die Tabs führen dich durch alle Aspekte deines Charakters.
Auf Mobilgeräten kannst du auch swipen!"
```

#### Schritt 3: Punkteleiste (Highlight auf PointBar)
```
"Die Punkteleiste zeigt dir jederzeit deine verfügbaren Punkte:
• Attributpunkte (für Stärke, Geschicklichkeit etc.)
• Fertigkeitspunkte (für Kampf, Heimlichkeit etc.)
• Handicap-Punkte (gewonnene Punkte durch Nachteile)
Behalte sie im Blick – sie aktualisiert sich automatisch."
```

#### Schritt 4: Erster Charakter (Highlight auf Speichern/Laden-Tab)
```
"Starte hier: Wähle ein Setting und erstelle einen neuen Charakter.
Das Setting bestimmt, welche Völker, Talente und Mächte
verfügbar sind."
```

#### Schritt 5: Empfohlene Reihenfolge
```
"Tipp: Erstelle deinen Charakter am besten in dieser Reihenfolge:
1. Setting & neuer Charakter (Speichern/Laden)
2. Volk wählen (Völker-Tab)
3. Profil ausfüllen (Name, Konzept)
4. Attribute & Fertigkeiten verteilen (Eigenschaften)
5. Handicaps wählen (für Bonuspunkte)
6. Talente wählen
7. Ggf. Mächte/Superkräfte
8. Ausrüstung kaufen
9. Charakterbogen prüfen & als PDF exportieren"
```

#### Schritt 6: Abschluss
```
"Du kannst dieses Tutorial jederzeit in den Einstellungen
oder im Info-Tab erneut starten.
Viel Spaß beim Erstellen deines Charakters!"
[Tutorial beenden]
```

### Technische Umsetzung

```
Neue Dateien:
  services/tutorial_service.py     – Tutorial-Logik & Zustandsverwaltung
  views/tutorial_overlay.py        – Overlay-Widget (halbtransparenter Hintergrund + Spotlight)
  views/tutorial_overlay.kv        – Layout für Tutorial-Dialoge

Geänderte Dateien:
  main.py                          – Tutorial beim Start auslösen
  config/app_config.json           – Flag: tutorial_completed, tutorial_hints_enabled
  views/einstellungen_widget.py    – Button "Tutorial erneut starten"
  views/screens.py (InfoScreen)    – Link zum Tutorial
  services/service_container.py    – TutorialService registrieren
```

### Spotlight-Overlay-Mechanik
- Halbtransparenter schwarzer Hintergrund über die ganze App
- "Spotlight"-Ausschnitt um das hervorgehobene UI-Element (z.B. Tab-Leiste)
- Erklärungs-Box (MDCard) mit Text, Schritt-Indikator und Navigation
- Touch auf den Hintergrund = nächster Schritt (optional)
- Implementierung: Custom `Widget` mit `canvas`-Zeichnung (Rectangle + Stencil für Ausschnitt)

---

## Säule 2: Kontextuelle Tab-Hilfen

### Konzept
- Beim ersten Besuch jedes Tabs erscheint ein kurzer Hilfe-Hinweis
- Danach über ein `?`-Icon in der Tab-Leiste oder PointBar aufrufbar
- Jeder Tab hat eine eigene Hilfekarte

### Hilfe-Texte pro Tab

#### Speichern/Laden
```
"Hier verwaltest du deine Charaktere:
• 'Neuer Charakter' – startet einen frischen Charakter
• 'Laden' – öffnet einen gespeicherten Charakter
• 'Speichern' – sichert deinen aktuellen Charakter
• 'PDF' – exportiert den Charakterbogen als PDF
Tipp: Wähle zuerst ein Setting über den Setting-Button!"
```

#### Völker
```
"Wähle hier das Volk deines Charakters.
Jedes Volk hat besondere Fähigkeiten und Boni.
Manche Völker haben Spezialitäten zur Auswahl.
Tipp: Die Boni werden automatisch verrechnet."
```

#### Profil
```
"Gib deinem Charakter einen Namen und ein Konzept.
Das Konzept beschreibt deinen Charakter in wenigen Worten
(z.B. 'Zwergischer Schmied' oder 'Kopfgeldjäger')."
```

#### Eigenschaften
```
"Verteile hier Attribut- und Fertigkeitspunkte.
• Attribute: Grundeigenschaften wie Stärke oder Verstand
• Fertigkeiten: Erlernte Fähigkeiten wie Kämpfen oder Heimlichkeit
Nutze die +/- Buttons zum Steigern/Senken.
Tipp: Fertigkeiten über dem zugehörigen Attribut kosten doppelt!"
```

#### Handicaps
```
"Handicaps sind Nachteile deines Charakters.
Sie geben dir Bonuspunkte für Attribute, Fertigkeiten,
Talente oder Startkapital.
• Leichtes Handicap = 1 Punkt
• Schweres Handicap = 2 Punkte
Du kannst max. 4 Handicap-Punkte erhalten."
```

#### Talente
```
"Talente sind besondere Vorteile deines Charakters.
Viele haben Voraussetzungen (Rang, Attribute, Fertigkeiten).
Nicht erfüllte Voraussetzungen werden rot markiert.
Tipp: Manche Talente können mehrfach gewählt werden!"
```

#### Mächte
```
"Hier wählst du arkane Mächte, wenn dein Charakter
einen Arkanen Hintergrund besitzt (Talent).
Jede Macht hat Machtpunkte-Kosten.
Tipp: Du brauchst zuerst ein passendes Talent
(z.B. 'Arkaner Hintergrund (Magie)')."
```

#### Superkräfte
```
"Superkräfte sind nur in bestimmten Settings verfügbar
(z.B. Superkräfte Kompendium).
Sie funktionieren ähnlich wie Mächte, haben aber
eigene Punktekosten und Stufensysteme."
```

#### Ausrüstung
```
"Kaufe hier Waffen, Rüstungen und Ausrüstung.
Dein Startkapital wird oben angezeigt.
• Waffen: Nah- und Fernkampfwaffen
• Rüstung: Schutzausrüstung
• Schilde: Zusätzlicher Schutz
• Sonstige: Allgemeine Ausrüstung
Tipp: Das Tragegewicht wird automatisch berechnet!"
```

#### Charakterbogen
```
"Hier siehst du deinen fertigen Charakter auf einen Blick.
Alle abgeleiteten Werte (Parade, Robustheit, Bewegung)
werden automatisch berechnet.
Nutze den PDF-Button für einen druckfertigen Bogen."
```

#### Historie
```
"Die Historie zeigt alle Änderungen an deinem Charakter.
Du kannst Änderungen rückgängig machen (Undo).
Tipp: Nutze den Undo-Button in der Punkteleiste
für schnelles Rückgängigmachen."
```

### Technische Umsetzung

```
Speicherung in app_config.json:
  "tab_hints_shown": {
    "speichern_laden": false,
    "voelker": false,
    "profil": false,
    ...
  }

Implementierung:
  - tutorial_service.py verwaltet den Zustand welche Hints gezeigt wurden
  - on_tab_switch() in main.py prüft, ob der Hint für diesen Tab schon gezeigt wurde
  - Anzeige als MDSnackbar (lang) oder kleiner MDDialog
  - ?-Button (MDIconButton) in der PointBar zum manuellen Aufruf
```

---

## Säule 3: Schritt-für-Schritt-Assistent (Wizard-Modus)

### Konzept
- Optionaler Modus, der den Nutzer durch die komplette Charaktererstellung führt
- Aktivierbar über Button auf dem Speichern/Laden-Tab oder nach "Neuer Charakter"
- Blendet irrelevante Tabs aus und führt sequentiell durch die nötigen Schritte
- Zeigt pro Schritt einen Fortschrittsbalken und kontextuelle Hilfe

### Ablauf

```
┌─────────────────────────────────────────────────┐
│  Schritt 1/8: Setting & Neuer Charakter         │
│  ████░░░░░░░░░░░░░░░░░░░░░░░░░░  12%           │
│                                                  │
│  [Wähle ein Setting und erstelle einen neuen     │
│   Charakter. Das Setting bestimmt die            │
│   verfügbaren Optionen.]                         │
│                                                  │
│  [← Zurück]  [Schritt überspringen]  [Weiter →] │
└─────────────────────────────────────────────────┘
```

### Schritte des Assistenten

| # | Tab-Wechsel zu | Aufgabe | Validierung |
|---|---------------|---------|-------------|
| 1 | Speichern/Laden | Setting wählen & neuen Charakter erstellen | Charakter existiert |
| 2 | Völker | Volk auswählen | Volk ist gesetzt |
| 3 | Profil | Name und Konzept eingeben | Name ist nicht leer |
| 4 | Eigenschaften | Attribut- und Fertigkeitspunkte verteilen | Punkte aufgebraucht |
| 5 | Handicaps | (Optional) Handicaps wählen | - |
| 6 | Talente | Talente wählen | - |
| 7 | Mächte* | Mächte wählen (*nur wenn relevant) | - |
| 8 | Ausrüstung | Ausrüstung kaufen | - |
| ✓ | Charakterbogen | Zusammenfassung & PDF-Export | - |

### Technische Umsetzung

```
Neue Dateien:
  services/wizard_service.py           – Wizard-Zustandsmaschine
  views/wizard_bar.py                  – Fortschrittsbalken-Widget
  views/wizard_bar.kv                  – Layout

Geänderte Dateien:
  main.py                              – Wizard-Modus Integration
  views/charakter_verwaltung_widget.py – "Geführte Erstellung" Button
  views/pointbar_view.py               – Wizard-Fortschrittsanzeige einblenden
```

### Wizard-Service Architektur

```python
class WizardService:
    """Verwaltet den Wizard-Modus für geführte Charaktererstellung."""

    def __init__(self):
        self.aktiv = False
        self.aktueller_schritt = 0
        self.schritte = [...]  # Liste der WizardSchritt-Objekte

    def starten(self):
        """Startet den Wizard-Modus."""

    def naechster_schritt(self):
        """Wechselt zum nächsten Schritt, validiert den aktuellen."""

    def vorheriger_schritt(self):
        """Geht einen Schritt zurück."""

    def schritt_ueberspringen(self):
        """Überspringt den aktuellen optionalen Schritt."""

    def beenden(self):
        """Beendet den Wizard-Modus."""

    def ist_schritt_valide(self) -> bool:
        """Prüft ob der aktuelle Schritt abgeschlossen ist."""
```

---

## Implementierungsreihenfolge

### Phase 1: Grundlagen (Priorität: Hoch)
1. **TutorialService** erstellen (`services/tutorial_service.py`)
   - Config-Integration (Flags lesen/schreiben)
   - Zustandsverwaltung (welche Tutorials/Hints wurden gezeigt)
   - Service im ServiceContainer registrieren

2. **Kontextuelle Tab-Hilfen** (Säule 2)
   - Hilfe-Texte als Daten-Struktur definieren
   - `?`-Button in PointBar oder Tab-Leiste
   - Anzeige als MDDialog mit "Nicht mehr anzeigen"-Checkbox
   - Integration in `on_tab_switch()`
   - **Begründung:** Geringstes Risiko, größter Sofortnutzen

### Phase 2: Willkommens-Tour (Priorität: Hoch)
3. **Spotlight-Overlay** implementieren (`views/tutorial_overlay.py`)
   - Canvas-basiertes Overlay mit Spotlight-Ausschnitt
   - Schritt-Navigation (Weiter/Zurück/Überspringen)
   - Schritt-Indikator (Punkte oder "3/6")

4. **First-Run-Erkennung** und Tutorial-Auslösung
   - Flag in Config
   - Auslösung in `on_start()` nach Tab-Aufbau
   - "Tutorial wiederholen"-Button in Einstellungen

### Phase 3: Wizard-Modus (Priorität: Mittel)
5. **WizardService** erstellen
6. **Wizard-Fortschrittsbalken** als Widget
7. **Integration** in Speichern/Laden und PointBar
8. **Validierungslogik** pro Schritt

### Phase 4: Verfeinerung (Priorität: Niedrig)
9. **Animationen** für Overlay-Übergänge
10. **Mobile-Optimierung** der Tutorial-Dialoge
11. **Erweiterte Tooltips** für komplexe UI-Elemente (z.B. Würfel-Icons)
12. **"Wusstest du?"-Tipps** – zufällige Tipps beim App-Start nach abgeschlossenem Tutorial

---

## Designrichtlinien

### Allgemein
- Alle Texte auf **Deutsch**
- Tutorial darf **jederzeit abgebrochen** werden
- Kein Tutorial-Zwang – alles ist optional und wiederholbar
- Tutorial-Fortschritt wird **persistent gespeichert**
- **MDDialog mit `size_hint=(0.85, None)`** für Android-Kompatibilität

### Visuell
- Spotlight-Overlay: Hintergrund `rgba(0, 0, 0, 0.7)`
- Erklärungsbox: `MDCard` mit Theme-Farben
- Schritt-Indikator: Kleine Punkte (aktiv/inaktiv)
- Animations-Dauer: 300ms für Übergänge

### UX-Prinzipien
- **Progressive Disclosure** – nicht alles auf einmal erklären
- **Kontext statt Handbuch** – Hilfe dort wo sie gebraucht wird
- **Lernkurve respektieren** – Anfänger führen, Experten nicht stören
- **Keine Wiederholung** – einmal gezeigte Hints nicht nochmal zeigen (außer manuell)

---

## Dateien-Übersicht (Neue & Geänderte)

### Neue Dateien
| Datei | Zweck |
|-------|-------|
| `services/tutorial_service.py` | Tutorial-Zustandsverwaltung & Logik |
| `services/wizard_service.py` | Wizard-Modus Zustandsmaschine |
| `views/tutorial_overlay.py` | Spotlight-Overlay Widget |
| `views/tutorial_overlay.kv` | Overlay-Layout |
| `views/wizard_bar.py` | Fortschrittsbalken Widget |
| `views/wizard_bar.kv` | Fortschrittsbalken Layout |
| `config/tutorial_config.json` | Hilfe-Texte & Tutorial-Schritte (Daten) |

### Geänderte Dateien
| Datei | Änderung |
|-------|----------|
| `main.py` | First-Run-Check, Tutorial-Start, Wizard-Integration |
| `services/service_container.py` | TutorialService & WizardService registrieren |
| `views/pointbar_view.py` | `?`-Hilfe-Button, Wizard-Fortschrittsanzeige |
| `views/einstellungen_widget.py` | "Tutorial wiederholen"-Button, Hint-Reset |
| `views/screens.py` | InfoScreen: Link zum Tutorial |
| `views/charakter_verwaltung_widget.py` | "Geführte Erstellung"-Button |

---

## Aufwandsschätzung

| Phase | Umfang |
|-------|--------|
| Phase 1: Tab-Hilfen | ~400 Zeilen Code + Texte |
| Phase 2: Willkommens-Tour | ~600 Zeilen Code (Overlay-Mechanik) |
| Phase 3: Wizard-Modus | ~500 Zeilen Code |
| Phase 4: Verfeinerung | ~200 Zeilen Code |
| **Gesamt** | **~1700 Zeilen** |
