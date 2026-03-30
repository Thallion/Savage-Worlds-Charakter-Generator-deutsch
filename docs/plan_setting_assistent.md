# Plan: Setting-Assistent für den Savage Worlds Charakter-Generator

## Problem-Analyse

**Aktueller Zustand:** Ein neues Setting wird als Extrakt des aktuellen Charakters erstellt. Der User muss erst einen Charakter mit den gewünschten Elementen konfigurieren, dann "Setting speichern" drücken. Das ist:

- **Verwirrend** – Setting-Erstellung und Charakter-Erstellung sind vermischt
- **Destruktiv** – alle `ausgewaehlt`-Flags werden beim Speichern still zurückgesetzt
- **Unflexibel** – kein Zusammenführen, kein selektives Übernehmen, kein Leer-Start
- **Kein Überblick** – keine Vorschau, keine Statistik, kein Zwischenstand

---

## Vision: Wizard-basierter Setting-Assistent

Ein eigenständiger, mehrstufiger Assistent (Overlay/Wizard), der Setting-Erstellung als **eigenen Workflow** behandelt – unabhängig vom aktuellen Charakter.

---

## Einstiegspunkt & Modi

Beim Start des Assistenten wählt der User einen von **4 Modi**:

| Modus | Beschreibung | Use Case |
|-------|-------------|----------|
| **Leer starten** | Komplett leeres Setting-JSON, alle Kategorien leer | Power-User baut alles selbst auf |
| **Vorlage verwenden** | Basiert auf einem bestehenden Setting (SWAE, Deadlands, etc.) | Häufigster Fall – bestehendes Setting anpassen |
| **Settings zusammenführen** | 2+ Settings kombinieren mit Konfliktlösung | Crossover-Kampagnen, Homebrew auf Basis mehrerer Quellen |
| **Aus Charakter extrahieren** | Aktuelles Verhalten (aber verbessert mit Vorschau) | Rückwärtskompatibilität |

---

## Wizard-Schritte

### Schritt 1: Grundeinstellungen

- **Setting-Name** (Pflicht, max 50 Zeichen)
- **Beschreibung** (Optional, max 200 Zeichen)
- **Modus-Auswahl** (siehe oben)
- **Basis-Setting(s) auswählen** (bei Vorlage/Zusammenführen)

### Schritt 2: Elemente konfigurieren (Kern des Assistenten)

Tab-basierte Übersicht über alle Kategorien:

| Kategorie | Aktionen |
|-----------|----------|
| **Völker** | Aktivieren/Deaktivieren, Neue hinzufügen, Bearbeiten |
| **Attribute** | Konfigurieren (normalerweise Standard beibehalten) |
| **Fertigkeiten** | Aktivieren/Deaktivieren, Zuordnung zu Attributen ändern, Neue hinzufügen |
| **Talente** | Aktivieren/Deaktivieren, Filtern nach Kategorie/Rang, Neue hinzufügen |
| **Handicaps** | Aktivieren/Deaktivieren, Neue hinzufügen |
| **Mächte** | Aktivieren/Deaktivieren, Neue hinzufügen |
| **Ausrüstung** | Aktivieren/Deaktivieren, Kategorien verwalten |
| **Settingregeln** | Spezielle Regeln ein/ausschalten |
| **Währung/Startgeld** | Konfigurieren |

**Jede Kategorie zeigt:**

- Anzahl aktiver/inaktiver Elemente als Badge
- Suchfeld zum schnellen Filtern
- Bulk-Aktionen: "Alle aktivieren", "Alle deaktivieren", "Aus Setting X importieren"
- Bei Zusammenführung: Konflikt-Markierung (Element existiert in mehreren Quellen mit unterschiedlichen Werten)

### Schritt 3: Zusammenführungs-Konflikte lösen (nur bei Merge-Modus)

- Liste aller Konflikte (z.B. Talent "Kampfreflexe" existiert in Setting A und B mit unterschiedlicher Beschreibung)
- Pro Konflikt: Quelle A wählen / Quelle B wählen / Manuell zusammenführen
- Vorschau des Ergebnisses

### Schritt 4: Vorschau & Speichern

- **Statistik-Übersicht:**
  ```
  Völker:        12 aktiv / 3 inaktiv
  Fertigkeiten:  28 aktiv / 5 inaktiv
  Talente:      147 aktiv / 23 inaktiv
  Handicaps:     45 aktiv / 8 inaktiv
  Mächte:        32 aktiv / 0 inaktiv
  Ausrüstung:    89 aktiv / 12 inaktiv
  ```
- **Diff-Ansicht** (bei Vorlage-Modus): Was wurde gegenüber der Vorlage geändert?
- **Speichern-Button** mit Bestätigungsdialog
- **Zwischenspeichern-Button** (speichert als Draft)

---

## Zwischenspeichern / Draft-System

- Unfertige Settings werden als `_draft_{name}.json` im User-Settings-Verzeichnis gespeichert
- Beim nächsten Öffnen des Assistenten: "Entwurf fortsetzen?" Dialog
- Drafts enthalten zusätzliche Metadaten:
  ```json
  {
    "_draft": true,
    "_created": "2026-03-30T14:22:00",
    "_last_modified": "2026-03-30T15:10:00",
    "_base_settings": ["SWAE", "Fantasy Kompendium"],
    "_mode": "merge",
    "_current_step": 2,
    "_conflicts_resolved": 5,
    "_conflicts_remaining": 3
  }
  ```
- Drafts erscheinen **nicht** in der Setting-Auswahl des Charaktergenerators

---

## Status-Übersicht (Dashboard)

Erreichbar über den Einstellungen-Tab, zeigt:

- **Aktives Setting:** Name, Beschreibung, Erstelldatum
- **Installierte Settings:** Liste aller nativen + User-Settings mit Elementanzahlen
- **Entwürfe:** Offene Drafts mit Fortschrittsanzeige
- **Quick Actions:**
  - Setting duplizieren
  - Setting exportieren (JSON-Download)
  - Setting importieren (JSON-Upload)
  - Setting löschen (nur User-Settings)

---

## Technische Umsetzung

### Neue Dateien

| Datei | Zweck |
|-------|-------|
| `views/setting_assistent_view.py` | Haupt-Wizard-Widget (MDScreen mit Steps) |
| `views/setting_assistent_view.kv` | Layout des Wizards |
| `views/setting_assistent_view_mobile.kv` | Mobile-Layout |
| `views/setting_element_list.py` | Wiederverwendbare Element-Liste mit Suche/Filter/Bulk |
| `views/setting_element_list.kv` | Layout der Element-Liste |
| `views/setting_conflict_view.py` | Konflikt-Auflösungs-UI |
| `views/setting_dashboard_view.py` | Status-Dashboard |
| `functions/setting_merge.py` | Merge-Logik für Settings |
| `models/setting_draft.py` | Draft-Modell mit Metadaten |

### Zu ändernde Dateien

| Datei | Änderung |
|-------|----------|
| `views/einstellungen_widget.py/.kv` | Button "Setting-Assistent öffnen", Dashboard einbetten |
| `functions/setting_funktionen.py` | `SettingsRepository` um Draft-Methoden erweitern |
| `views/setting_popup.py` | Refactoring – "Neues Setting" leitet zum Assistenten weiter |
| `services/config_service.py` | Draft-Pfade konfigurieren |

### Architektur-Entscheidungen

1. **Wizard als eigener Screen** (nicht Popup) – genug Platz für komplexe UI
2. **Setting-Daten im Wizard sind unabhängig vom Charakter** – keine Seiteneffekte
3. **Merge-Algorithmus:** Deep-Merge auf Element-Ebene, Konflikte bei gleichem `name` aber unterschiedlichen Feldern
4. **Draft-Persistenz:** Automatisches Zwischenspeichern alle 60 Sekunden + bei Step-Wechsel
5. **Rückwärtskompatibilität:** Bestehende Settings bleiben unverändert, Drafts nutzen erweitertes Schema

---

## Implementierungs-Phasen

### Phase 1 – Fundament

- Draft-Modell und Persistenz
- Wizard-Grundgerüst (Schritt 1 + 4)
- Modus "Vorlage verwenden" (häufigster Use Case)
- Statistik-Vorschau

### Phase 2 – Element-Editor

- Tab-basierter Element-Editor (Schritt 2)
- Suche, Filter, Bulk-Aktionen pro Kategorie
- Modus "Leer starten"

### Phase 3 – Merge

- Multi-Setting-Auswahl
- Merge-Algorithmus
- Konflikt-Auflösungs-UI (Schritt 3)

### Phase 4 – Dashboard & Polish

- Status-Dashboard im Einstellungen-Tab
- Setting-Import/Export
- Autosave für Drafts
- Mobile-Layouts

---

## UX-Prinzipien

1. **Setting ≠ Charakter** – Der Assistent macht klar, dass ein Setting eine *Spielwelt-Konfiguration* ist, nicht ein Charakter-Zustand
2. **Nicht-destruktiv** – Änderungen am Setting beeinflussen nie den aktuellen Charakter (erst beim expliziten Setting-Wechsel)
3. **Fortschritt sichtbar** – Progressbar im Wizard, Element-Zähler, Draft-Status
4. **Rückgängig möglich** – Jeder Wizard-Schritt ist reversibel, Drafts bleiben erhalten
5. **Übersichtlich** – Statistiken und Zusammenfassungen statt endloser Listen
