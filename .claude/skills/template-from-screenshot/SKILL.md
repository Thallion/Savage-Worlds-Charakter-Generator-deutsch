---
name: template-from-screenshot
description: Erstellt ein neues Charakter-Template JSON aus Screenshots eines Charakterbogens. Aufrufen wenn der User Screenshots eines Charakters zeigt und ein Template erstellen möchte.
allowed-tools: Read Write Bash Glob Grep
---

# Template aus Screenshot erstellen

**Argumente:** `$ARGUMENTS` — Erwartet: `<screenshot1> [screenshot2] <template-dateiname>`

Beispiel: `/template-from-screenshot screenshots/char1.png screenshots/char2.png Archetyp_SWAE_Krieger_Max`

## Ablauf

### 1. Screenshots lesen

Lese alle angegebenen Screenshot-Dateien mit dem Read-Tool (Bilder werden visuell angezeigt).
Extrahiere folgende Daten:

**Attribute (W4/W6/W8/W10/W12):**
- Stärke, Geschicklichkeit, Konstitution, Verstand, Willenskraft

**Abgeleitete Werte (nur zur Verifikation, nicht ins Template):**
- Parade, Robustheit

**Fertigkeiten (W4/W6/W8/W10/W12):**
- Alle sichtbaren Fertigkeiten mit ihren Würfelwerten

**Handicaps:**
- Name + Stufe (leicht/schwer) falls erkennbar

**Talente (Edges):**
- Alle aufgelisteten Talente

**Ausrüstung:**
- Waffen mit Stats, sonstige Gegenstände

**Profil:**
- Name, Geschlecht, Konzept, Setting (falls erkennbar)
- Rang (Anfänger/Fortgeschritten/Veteran/Held/Legendär)

### 2. Referenz-Templates prüfen

Lese ein passendes WOU-Template als Formatvorlage, z.B.:
```
templates/wou_aidan_held_anfaenger.json
```

Lese auch das Schema:
```
templates/character_template_schema.json
```

### 3. Setting ermitteln

Prüfe aus dem Screenshot welches Setting verwendet wird (SWAE, Deadlands, Fantasy Kompendium etc.).
Falls nicht erkennbar: Standard SWAE verwenden.

Prüfe welches Volk (Mensch, Elf, Zwerg etc.) der Charakter hat.
Falls Mensch in SWAE: `race_choices.freies_talent` setzen für das freie Anfänger-Talent.

### 4. Punkte validieren (mental)

Überprüfe ob die Werte regelkonform sind:
- SWAE Standard: 5 Attributpunkte, 12 Fertigkeitenpunkte
- Mensch: +1 freies Anfänger-Talent
- Handicaps: jeder Punkt = 1 Fertigkeitsteigerung ODER 2 Punkte = 1 Talent ODER 2 Punkte = 1 Attributsteigerung
- Falls Attribute > 5 Punkte benötigen: `starting_attribute_points` anpassen

Falls Voraussetzungen für Talente nicht erfüllt sind (z.B. McGyver braucht Wahrnehmung W8):
→ `strict_point_allocation: false` verwenden, Generator ignoriert Voraussetzungen

### 5. Template JSON erstellen

Dateiname: `templates/<template-dateiname>.json`

Verwende dieses Format:

```json
{
  "name": "<Charaktername>",
  "description": "<Charakterzitat oder kurze Beschreibung>",
  "setting": "<Setting-Name>",
  "race": "<Volk>",
  "profile": {
    "age": "",
    "gender": "<männlich|weiblich|...>",
    "concept": "<Konzept>",
    "languages": "",
    "rank": "<Rang>"
  },
  "race_choices": {
    "freies_talent": "<freies Mensch-Talent falls zutreffend>"
  },
  "free_race_edge": "",
  "attributes": {
    "Geschicklichkeit": <W-Wert als Zahl: 4/6/8/10/12>,
    "Konstitution": <W-Wert>,
    "Stärke": <W-Wert>,
    "Verstand": <W-Wert>,
    "Willenskraft": <W-Wert>
  },
  "skills": {
    "<Fertigkeit>": <W-Wert>,
    ...
  },
  "handicaps": [
    "<Name_stufe oder Name falls nur eine Stufe>",
    ...
  ],
  "edges": [
    "<Talentname>",
    ...
  ],
  "powers": [],
  "power_points": 0,
  "equipment": [
    {
      "name": "<Name>",
      "type": "Waffe|Rüstung|Schild|Ausrüstung",
      "description": "<kurze Beschreibung>",
      "category": "<Kategorie>",
      "properties": {
        "damage": "<z.B. Stä+W6 oder 2W6+1>",
        "range": "<z.B. 12/24/48 oder leer>",
        "ap": <Rüstungsdurchdringung als Zahl>,
        "two_handed": <true|false>
      }
    }
  ],
  "starting_attribute_points": 5,
  "starting_advances": 0,
  "advances_to_apply": [],
  "generation_options": {
    "strict_point_allocation": false,
    "allow_over_attribute": true,
    "auto_save": true,
    "save_path": "auto_generated/<template-dateiname>",
    "complete_character_generation": true
  },
  "notes": {
    "parade_calculation": "<Formel>",
    "robustheit_calculation": "<Formel>",
    "bewegung": 6,
    "parade": <Wert>,
    "robustheit": <Wert>
  }
}
```

**Wichtige Regeln für Handicap-Schlüssel:**
- Falls Handicap in schwer/leicht existiert: `"Misstrauisch_schwer"` oder `"Schwerhörig_leicht"`
- Falls nur eine Stufe: einfacher Name `"Tick"`
- Im Zweifel: einfachen Namen ohne Suffix verwenden

**Wichtige Regeln für Fertigkeiten:**
- Grundfertigkeiten (Allgemeinwissen, Athletik, Heimlichkeit, Überreden, Wahrnehmung) starten kostenlos auf W4 — trotzdem mit W4 ins Template eintragen
- W-Werte als Integer: W4=4, W6=6, W8=8, W10=10, W12=12

**race_choices:**
- Mensch (SWAE): `"freies_talent": "<Name>"` — das erste Talent aus der edges-Liste das den Regeln entspricht
- Kein freies Talent nötig: `"race_choices": {}` oder weglassen

### 6. Template testen

Nach dem Erstellen der Datei testen:

```bash
python3 -c "
from functions.auto_character_generator import AutoCharacterGenerator
gen = AutoCharacterGenerator()
result = gen.generate_from_template('templates/<template-dateiname>.json')
print('Ergebnis:', result)
" 2>&1 | tail -40
```

### 7. Ergebnis prüfen und korrigieren

Prüfe die Ausgabe auf:
- Alle Attribute korrekt?
- Alle Fertigkeiten korrekt?
- Alle Talente vorhanden (ohne unerwartete [!])?
- Handicaps korrekt mit richtigen Punkten?
- Punktebilanz sinnvoll (Differenz sollte klein sein)?

Falls Talente mit [!] (Voraussetzungen ignoriert) auftauchen:
→ Normal wenn `strict_point_allocation: false` — nur melden wenn es dem User wichtig ist

Falls Talente fehlen oder falsch:
→ Template anpassen und erneut testen

### 8. Abschlussmeldung

Berichte dem User:
- Dateiname des erstellten Templates
- Kurze Zusammenfassung der extrahierten Werte
- Eventuelle Abweichungen/Warnings
- Testbefehl zum manuellen Nachgenerieren