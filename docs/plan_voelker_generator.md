# Plan: Völker-Generator (Race/Species Creator)

## Kontext

Spielleiterinnen und Spieler sollen eigene Völker (oder kulturelle Archetypen) nach dem offiziellen Savage Worlds Punktesystem erschaffen können. Völker starten mit 2 Punkten positiver Eigenarten; zusätzliche positive Eigenarten müssen mit gleichwertigen negativen ausgeglichen werden. Der bestehende `volk_popup.py` ist rudimentär (nur Freitext-Eingabe ohne Punktesystem) und wird durch einen mehrstufigen Wizard ersetzt.

## Architektur-Entscheidungen

- **UI**: Mehrstufiger Wizard (analog `views/template_wizard.py`)
- **Daten**: Neue JSON-Konfigdatei `config/volkseigenarten_config.json`
- **CRUD**: Erstellen + Bearbeiten + Löschen von Custom-Völkern
- **Bestehende Patterns**: Wiederverwendung von `VolkDialogHandler` (erweitern), `Volk`-Model, `dialog_service`-Integration

---

## Schritt 1: Volkseigenarten-Konfigdatei erstellen

**Neue Datei:** `config/volkseigenarten_config.json`

Struktur pro Eigenart:
```json
{
  "positive": [
    {
      "id": "anpassungsfaehig",
      "name": "Anpassungsfähig",
      "kosten": 2,
      "max_auswahl": 1,
      "beschreibung": "Das Volk zeigt große Vielfalt...",
      "effekt_typ": "wahlmoeglichkeit",
      "effekt": { "freies_talent": true },
      "optionen": null
    },
    {
      "id": "attributserhoehung",
      "name": "Attributserhöhung",
      "kosten": 2,
      "max_auswahl": 0,
      "beschreibung": "Erhöht ein bestimmtes Attribut um einen Würfeltyp.",
      "effekt_typ": "attribut_bonus",
      "effekt": { "attribut_bonus": 2 },
      "optionen": {
        "typ": "attribut_auswahl",
        "attribute": ["Stärke", "Geschicklichkeit", "Konstitution", "Verstand", "Willenskraft"]
      }
    },
    {
      "id": "fliegen",
      "name": "Fliegen",
      "kosten": [2, 4, 6],
      "max_auswahl": 1,
      "beschreibung": "Fliegen mit Bewegungsweite 6/12/24.",
      "effekt_typ": "spezieller_effekt",
      "effekt": { "fliegen": true },
      "optionen": {
        "typ": "stufen_auswahl",
        "stufen": [
          { "kosten": 2, "label": "Bewegungsweite 6" },
          { "kosten": 4, "label": "Bewegungsweite 12" },
          { "kosten": 6, "label": "Bewegungsweite 24" }
        ]
      }
    }
  ],
  "negativ": [
    {
      "id": "abhaengigkeit",
      "name": "Abhängigkeit",
      "kosten": -2,
      "max_auswahl": 1,
      "beschreibung": "Das Volk muss alle 24 Stunden eine Substanz konsumieren...",
      "effekt_typ": "spezieller_effekt",
      "effekt": { "abhaengigkeit": true },
      "optionen": {
        "typ": "text_eingabe",
        "platzhalter": "Substanz (z.B. Wasser, Sonnenlicht)"
      }
    }
  ]
}
```

Alle ~33 positiven und ~13 negativen Eigenarten aus den Regeln werden aufgenommen. `max_auswahl: 0` = unbegrenzt (U).

---

## Schritt 2: Volkseigenarten-Ladelogik

**Neue Datei:** `functions/volkseigenarten_funktionen.py`

Funktionen:
- `lade_volkseigenarten_config()` - Lädt und cached die JSON-Konfigdatei
- `berechne_punktestand(ausgewaehlte_eigenarten)` - Berechnet den aktuellen Punktestand (Start: 2, positiv kostet, negativ gibt)
- `ist_punktestand_gueltig(ausgewaehlte_eigenarten)` - Prüft ob positive - negative >= 0 (ausgeglichen)
- `eigenart_zu_effekte(ausgewaehlte_eigenarten)` - Konvertiert ausgewählte Eigenarten in das `Volk.effects`-Dictionary
- `eigenart_zu_besonderheiten(ausgewaehlte_eigenarten)` - Generiert die `besonderheiten`-Liste (Beschreibungstexte)
- `eigenart_zu_handicaps(ausgewaehlte_eigenarten)` - Generiert die `handicaps`-Liste
- `validiere_eigenart_auswahl(eigenart, aktuelle_auswahlen)` - Prüft ob eine Eigenart noch wählbar ist (max_auswahl)

---

## Schritt 3: Wizard-UI implementieren

**Überarbeitete Datei:** `views/volk_popup.py` (erweitern, nicht neue Datei)
**Überarbeitete Datei:** `views/volk_popup.kv` (erweitern)

### Wizard-Schritte (4 Schritte):

#### Schritt 1: Name & Grunddaten
- Textfeld: Name des Volkes (Pflichtfeld)
- Textfeld: Beschreibung (optional)
- Anzeige: "Verfügbare Punkte: 2"

#### Schritt 2: Positive Volkseigenarten
- Scrollbare Liste aller positiven Eigenarten
- Jede Eigenart als Card/ListItem mit:
  - Name + Kosten in Klammern
  - Kurzbeschreibung
  - Checkbox oder +/- Buttons (für mehrfach wählbare)
  - Bei Optionen (Attribut-Auswahl, Stufen): Dropdown/Buttons einblenden
- Oben: Live-Punkteanzeige (z.B. "Punkte: 4 / 2 verfügbar → 2 Punkte durch negative ausgleichen")

#### Schritt 3: Negative Volkseigenarten
- Gleiche Darstellung wie Schritt 2
- Oben: Live-Punkteanzeige mit Hinweis ob Balance erreicht
- Warnung wenn noch Punkte ausgeglichen werden müssen

#### Schritt 4: Vorschau & Speichern
- Zusammenfassung: Name, Beschreibung
- Liste gewählter positiver Eigenarten mit Kosten
- Liste gewählter negativer Eigenarten mit Kosten
- Gesamtpunktestand (muss >= 0 sein, d.h. ausgeglichen)
- Generiertes `effects`-Dictionary als Vorschau
- Speichern-Button (nur aktiv wenn gültig)

### Wizard-Navigation:
- Zurück / Weiter Buttons (wie `template_wizard.py`)
- Fortschrittsanzeige "Schritt X von 4"
- Abbrechen-Button
- Validierung beim Weitergehen (Name nicht leer in Schritt 1)

### Klassen:

```python
class VolkGeneratorWizard:
    """Mehrstufiger Wizard für Völker-Erstellung und -Bearbeitung"""
    def __init__(self, controller, callback=None, edit_volk=None):
        # edit_volk: Volk-Objekt für Bearbeitung, None für Neuerstellung
    
    def start_wizard(self)
    def _show_current_step(self)
    def _create_name_step(self) -> Widget
    def _create_positive_step(self) -> Widget
    def _create_negative_step(self) -> Widget
    def _create_preview_step(self) -> Widget
    def _next_step(self, *args)
    def _previous_step(self, *args)
    def _save_volk(self)
    def _cancel_wizard(self, *args)
    def _update_punkte_anzeige(self)
```

---

## Schritt 4: VolkDialogHandler erweitern

**Datei:** `views/volk_popup.py`

Änderungen an `VolkDialogHandler`:
- `show_add_dialog()` → Startet `VolkGeneratorWizard` (statt altem simplen Dialog)
- `show_edit_dialog(volk_name)` → Startet `VolkGeneratorWizard` mit `edit_volk=volk_objekt`
- `show_delete_dialog()` → Bleibt wie bisher (funktioniert bereits)
- `save_volk()` → Wird in den Wizard verlagert, erstellt `Volk`-Objekt mit korrektem `effects`-Dict

---

## Schritt 5: VoelkerWidget Integration

**Datei:** `views/voelker_view.py`

Änderungen:
- Button "Volk erstellen" hinzufügen (ruft `dialog_service.volk_dialog_handler.show_add_dialog()` auf)
- Button "Volk bearbeiten" für custom Völker (nur sichtbar wenn ein custom Volk ausgewählt ist)
- Button "Volk löschen" für custom Völker

**Datei:** `views/voelker_view.kv` (und ggf. `voelker_view_mobile.kv`)
- Buttons für Erstellen/Bearbeiten/Löschen im UI-Layout einbauen

---

## Schritt 6: Persistenz

Die Speicherung nutzt die bestehende Infrastruktur:
- Custom-Völker werden mit `custom=True` im `charakter.voelker`-Dict gespeichert
- Beim Speichern eines Charakters werden sie via `Volk.to_dict()` serialisiert
- Zusätzlich: Custom-Völker in der Setting-JSON speichern (via `setting_funktionen.py`), damit sie setting-übergreifend verfügbar bleiben

---

## Zu ändernde Dateien

| Datei | Aktion | Beschreibung |
|-------|--------|-------------|
| `config/volkseigenarten_config.json` | **NEU** | Alle Volkseigenarten mit Punktwerten |
| `functions/volkseigenarten_funktionen.py` | **NEU** | Lade-, Berechnungs- und Validierungslogik |
| `views/volk_popup.py` | **ÄNDERN** | `VolkGeneratorWizard` hinzufügen, `VolkDialogHandler` erweitern |
| `views/volk_popup.kv` | **ÄNDERN** | Wizard-Layout (oder programmatisch erstellen wie template_wizard.py) |
| `views/voelker_view.py` | **ÄNDERN** | Buttons für Erstellen/Bearbeiten/Löschen |
| `views/voelker_view.kv` | **ÄNDERN** | Button-Layout |
| `views/voelker_view_mobile.kv` | **ÄNDERN** | Mobile Button-Layout (falls vorhanden) |

### Wiederverwendete bestehende Komponenten:
- `models/volk.py` → `Volk`-Klasse mit `effects`, `to_dict()`, `from_dict()`, `custom`-Flag
- `views/template_wizard.py` → Wizard-Muster (Navigation, Schrittanzeige, Dialog-Erstellung)
- `services/dialog_service.py` → `volk_dialog_handler` bereits registriert
- `functions/volk_funktionen.py` → `waehle_volk()`, `abwaehlen_volk()` für Integration

---

## Verifikation / Testplan

1. **Unit-Tests** (`test units/test_volkseigenarten.py` - neu):
   - Laden der JSON-Konfigdatei
   - Punkteberechnung (2 Startpunkte, korrekte Addition/Subtraktion)
   - Validierung: Ausgeglichene Punkte, max_auswahl Limits
   - Konvertierung Eigenarten → Volk.effects Dictionary
   - Bearbeitung: Laden eines bestehenden Volks in den Wizard

2. **Manuelle Tests**:
   - App starten: `python main.py`
   - Völker-Tab öffnen → "Volk erstellen" Button
   - Wizard durchlaufen: Name eingeben → Positive wählen → Negative wählen → Vorschau → Speichern
   - Erstelltes Volk in der Völker-Liste auswählen
   - Prüfen: Effekte werden korrekt auf den Charakter angewendet
   - Custom Volk bearbeiten → Änderungen speichern
   - Custom Volk löschen
   - Charakter speichern/laden mit custom Volk

3. **Regressions-Tests**:
   - Bestehende Tests ausführen: `python "test units/run_all_tests.py"`
   - Sicherstellen dass bestehende Völker-Auswahl weiter funktioniert
