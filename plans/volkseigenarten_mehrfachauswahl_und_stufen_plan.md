# Plan: Mehrfachauswahl & Punkte-Stufen für Volkseigenarten

## Implementierungs-Status (Checkliste)

### ✅ Abgeschlossen

- [x] **Schritt 1a** — Branch `claude/volkseigenarten-stufen` in `main` gemergt (Commit `5740ec0`)
- [x] **Schritt 1b** — `fliegen` als Stufen-Eigenart (`fliegen_stufe1/2/3` konsolidiert, Commit `a335405`)
- [x] **Schritt 1c (teilweise)** — Neue Stufen-Eigenarten in Config:
  - [x] Hörner (Stufen: Stärke+W4/W6)
  - [x] Klauen (Stufen: W4/W6/W6+PB2)
  - [x] Regeneration (Stufen: täglich/permanent)
  - [x] Giftige Berührung (Stufen: leicht/betäubend)
  - [x] Verringerte Bewegungsweite (negative, Stufen: -1/-2 BW)
- [x] **Schritt 2** — Mehrfachauswahl-UI mit Stepper:
  - [x] Stepper-Buttons (+/-) bei `max_auswahl != 1`
  - [x] Checkbox bei `max_auswahl == 1`
  - [x] Debounce (500ms) für Touch-Events
  - [x] `_increment_eigenart`, `_decrement_eigenart` Methoden
  - [x] `_refresh_eigenarten_popup` für UI-Aktualisierung
- [x] **Schritt 2d** — `validiere_volk_erstellung`: max_auswahl pro ID Prüfung
- [x] **Verzögerte Auswahl (Auswahl nach Volkserstellung)**:
  - [x] Config: `auswahl_verzoegert: true` bei `attributserhoehung`, `attributserhoehung_zwei`, `attributsschwäche`, `magieaffin`
  - [x] Config: `auswahl_verzoegert: true` bei `freies_talent`, `freie_grundfertigkeit`, `naturtalente`
  - [x] volk_popup.py: `_show_optionen_dialog` prüft Flag und verzögert Auswahl
  - [x] volkseigenarten_funktionen.py: Validierung ignoriert fehlende `ausgewaehlt` bei verzögerter Auswahl
  - [x] volkseigenarten_funktionen.py: `eigenart_zu_effekte` setzt `wahlmoeglichkeiten` bei verzögerter Auswahl
  - [x] volk_funktionen.py: `get_volk_zusatzelemente` erkennt neue Typen (`freie_grundfertigkeit`, `freie_nicht_grundfertigkeit`)
- [x] **Tests** — 927 Tests erfolgreich
- [x] **PR #182** — Edit-Button für „Attributs-Schwäche" bei Custom-Völkern (`_on_edit_attribut_malus`, `_on_attribut_malus_chosen` in `views/voelker_view.py`)
- [x] **PR #182** — Stepper-Zähler bei Mehrfach-Eigenarten aktualisiert sich (Refresh in `_increment_eigenart` / `_decrement_eigenart` in `views/volk_popup.py`)

### ✅ Freies Volk-Talent & Arkane Hintergründe

Cross-cutting Themen, die das Volk mit dem Talent- und Macht-System verzahnen. Diese Arbeit ist im ursprünglichen Plan (Stufen + Mehrfachauswahl) nicht aufgeführt, ist aber Voraussetzung für Schritt 3a.

- [x] **PR #162 (Commit, kein PR-Nummer)** — Freies Volk-Talent ändern + AH-Aktivierung (`plans/freies_volk_talent_plan.md`)
  - `volk_funktionen.waehle_freies_talent` ruft `talent_funktionen.waehle_freies_talent` auf statt nur `ausgewaehlt = True` zu setzen — dadurch werden bei AH-Talenten Mächte (`verfuegbare_maechte`, `anzahl_maechte`), Machtpunkte (`erhoehe_machtpunkte`) und Auto-Effekte (`_apply_ah_auto_effects`) korrekt aktiviert. Auch Auto-Handicaps und Auto-Talente von AH-Talenten greifen jetzt.
  - `views/voelker_auswahl_overlay.py::_show_talent_selection` bekommt Filter-Toggle (alle Talente vs. nur verfügbare) und Voraussetzungs-Bestätigungsdialog ("Trotzdem auswählen") analog zur Haupt-Talente-Ansicht.
  - `_on_edit_zusatzelement` in `views/voelker_view.py` öffnet das Talent-Auswahl-Overlay zum Bearbeiten eines bereits gewählten Talents (Stift-Icon neben Chip).
- [x] **PR #180** — Magieaffin: freier Arkaner Hintergrund (statt fester Arkaner-Fertigkeits-Liste)
  - `extrahiere_arkane_fertigkeit_aus_ah` ermittelt die zugehörige Arkane Fertigkeit aus dem AH-Talent (Beschreibung → Voraussetzungen → Whitelist-Fallback) — funktioniert in SWAE, Deadlands, Hellfrost und Fantasy Kompendium ohne Setting-spezifische Hardcoding-Listen.
  - `waehle_magieaffin_fertigkeit(charakter, volk_name, ah_talent_name)` validiert per `_ist_ah_talent`, aktiviert das AH-Talent regulär und persistiert sowohl AH-Talent als auch abgeleitete Fertigkeit in `volk.effects['magieaffin_auswahl']`.
  - `get_magieaffin_optionen` liefert Tupel `(ah_talent_name, fertigkeit_name)` — Dialog zeigt z. B. „AH (Wunder) → Glaube" statt nur Fertigkeitsnamen.
  - `_on_edit_magieaffin` im Völker-Tab zum nachträglichen Wechseln des AH.
  - `_reset_magieaffin` mit Backwards-Compat für Legacy-Auswahlen ohne `ah_talent`-Eintrag.
- [x] **PR #176** — Auto-Generator: race_choices + Steigerungshistorie
  - `auto_character_generator.py::_apply_race_choices` versteht `race_choices`-Dict mit `freies_talent`, `freies_attribut`, `freies_talent_oder_attribut` (Modus + Wert), `attribut_staerke_oder_konstitution`, `freie_verstandsfertigkeit` etc.
  - Unicode-normalisiertes Matching (`_resolve_key`) löst Umlaut-Probleme („Kämpfen" vs. „Kämpfer", Templates ohne Umlaute treffen die Umlaut-Variante).
  - `charakter.steigerungs_journal` protokolliert pro Würfelschritt mit `kosten_typ` (Attributspunkt / Fertigkeitspunkt / Handicap-Punkt / Aufstieg / Volk) und `phase` (generierung / aufstieg). „Auto-added points" sind jetzt transparente Aufstiege.

**Konsequenz für Schritt 3a (Macht 2+1)**: Die *AH-Aktivierungs-Logik* (Mächte + Auto-Effekte) ist über `talent_funktionen.talent_auswaehlen` bereits verfügbar — Schritt 3a muss nur noch eine eigene `volk_macht`-Eigenart anlegen, die Kosten-Formel `2 + 1·(N-1)` umsetzt und die erste Macht-Auswahl an dieselbe Aktivierung delegiert (statt das Rad neu zu erfinden).

### ✅ Multi-Slot im Völker-Tab (PR #196, gemerged)

Adressiert die **Pro-Charakter-Auswahl** für Eigenarten mit `max_auswahl > 1` und `auswahl_verzoegert: true`. Das war im ursprünglichen Plan blind.

- [x] **Datenmodell**:
  - `eigenart_zu_effekte` schreibt `wahlmoeglichkeiten_counts[typ] = N` parallel zum Skalar `wahlmoeglichkeiten[typ] = True` (`functions/volkseigenarten_funktionen.py:_bump_count`)
  - `get_volk_zusatzelemente` liefert ein `slots`-Dict pro Multi-Slot-Typ (`freies_talent`, `freies_attribut`, `freies_attribut_malus`, `freie_fertigkeit`); Legacy-Skalar-Keys bleiben befüllt (`functions/volk_funktionen.py`)
  - `reset_volk_auswahlen` iteriert Listen und unterstützt zusätzlich `attribut_malus`; neuer Helper `reconcile_volk_auswahlen` trimmt überzählige Slots samt State-Rollback (`functions/volk_funktionen.py:reconcile_volk_auswahlen`)
  - `voelker_auswahlen` als persistierte `DictProperty` am Charakter (`models/charakter_properties.py`)
- [x] **UI**:
  - Auswahl-Overlay: pro Slot eine eigene Card mit `n/N`-Fortschritt; bereits gewählte Werte werden aus folgenden Slot-Optionen herausgefiltert. Konstante `MULTI_SLOT_KEYS` als Schnittstelle zwischen `slots`-Dict und UI (`views/voelker_auswahl_overlay.py:MULTI_SLOT_KEYS`)
  - Völker-Tab: pro Slot eine Zeile mit eigenem Edit-Button, `slot_index` in allen Lambdas korrekt gecaptured; Attribut-Bonus- und Malus-Edit-Dialoge filtern bereits in anderen Slots gewählte Werte (`views/voelker_view.py`)
- [x] **Persistenz**: `voelker_auswahlen` round-trippt in `to_dict`/`from_dict`; Skalar→Liste-Migration in `_finalize_character_loading` (`functions/charakter_speicher.py`)
- [x] **Auto-Generator**: Listen-Keys `freie_talente`, `freie_attribute`, `attribute_malus` plus Legacy-Skalare (`functions/auto_character_generator.py`)
- [x] **Wizard**: Quick-Pick-Inkonsistenz behoben (`'freies_talent'` → `'talent'`); `_finish_wizard` ruft `reconcile_volk_auswahlen` mit den neuen Slot-Counts; Volk-Rename trägt die Auswahlen mit (`views/volk_popup.py`)
- [x] **Tests**: 14 neue Multi-Slot-Tests in 6 Gruppen; alle 64 Volk-/Setting-Tests grün (`test units/test_volkseigenarten_multi_slot.py`)

### ⏳ Offen

#### Schritt 2 (Rest)
- [x] Schritt 2a — Schema: `kosten_per_instanz`-Feld erkannt in `berechne_punktestand` (Default True; bei False zählt pro ID nur die erste Instanz, Vorbereitung für Sonderfälle wie Macht 2+1+1+…)
- [x] Schritt 2c — Wizard-Schritt zeigt einzelne Eigenart-Zeilen mit ×-Button zum Entfernen ( `_build_wizard_eigenart_row`, `_on_wizard_remove_eigenart`) — **ERLEDIGT**
- [x] Schritt 2e — `eigenart_zu_effekte` summiert numerische Effekte (`attribute_bonuses`, `fertigkeits_startboni`, alle additiven Felder im `spezieller_effekt`-Pfad) statt zu überschreiben; `lebenserwartung_mult` als Multiplikator multipliziert

#### Schritt 3 — Sonderfälle
- [x] Schritt 3a — `volk_macht`-Eigenart mit Kostenformel 2 + 1 je weitere (N-1), UI `_show_macht_optionen_dialog`, AH-Aktivierung (Begabt) — **ERLEDIGT** (AH-Aktivierungs-Pattern über PR #162 + #180)
- [x] Schritt 3b — `volk_talent`-Eigenart mit Kostenformel 2 + Rang, UI `_show_talent_rang_optionen_dialog`, skip_prereq_check — **ERLEDIGT** (PR #162 Voraussetzungs-Bestätigung)
- [x] Schritt 3c — `volk_superkraft`-Eigenart mit Kosten 2 + Punkte der Superkraft, Setting-Filterung in `_show_eigenarten_popup` — **ERLEDIGT**

#### Schritt 4 — Vollständigkeit
- [ ] Biss, Graben, Keine lebenswichtigen Organe
- [ ] Panzerung (3), Parade (3), Reichweite (3)
- [ ] Größe +1 (3), Größe -1
- [ ] Macht (Volkseigenschaft), Talent (Volk), Superkräfte
- [ ] Wandkrabbler, Wärmesicht, Widerstand gegen Naturgewalten
- [ ] Anfälligkeit für Naturgewalten, Volksfeind, Weniger Grundfertigkeiten
- [ ] Kann nicht sprechen, Schlechte Parade, Zäh, Zusätzliche Aktion, Wuchtig

---

## Kontext

Das Volkseigenarten-Punktesystem (`config/volkseigenarten_config.json` + `functions/volkseigenarten_funktionen.py` + `views/volk_popup.py`) bildet das Regelwerk aus `Texte/volksgenerierung.txt` derzeit nur unvollständig ab:

- **Mehrfachauswahl** (z. B. Robustheit (3) = bis zu 3×, Attributserhöhung (U) = unbegrenzt) wird als Checkbox umgesetzt — ein zweiter Klick **entfernt** die Auswahl, statt eine zweite Instanz hinzuzufügen (`views/volk_popup.py:424`). `max_auswahl` wird zwar in der Anzeige (`(1/2)`) und der Validierung (`functions/volkseigenarten_funktionen.py:256` ff.) verwendet, aber die UI erlaubt das nicht.
- **Punkte-Stufen** (z. B. Fliegen 2/4/6, Klauen 2/3/4) werden als getrennte Eigenarten modelliert (`fliegen_stufe1`, `fliegen_stufe2`, `fliegen_stufe3`). Das verschwendet Platz in der Liste und verhindert Wiederherstellung der Auswahl als „Stufe 2 von 3".
- **Sonderfälle** mit gestaffelten Kosten (Macht 2+1, Talent 2+X, Superkräfte 2+X) sind gar nicht abbildbar.

Das aktuelle Schema kennt nur ein einzelnes `kosten`-Feld und einen einzelnen `effekt`-Dict pro Eintrag.

## Bereits implementiert (Branch `claude/volkseigenarten-stufen`, Commit `a335405`, **noch nicht in `main`**)

Die Code-Seite für Schritt 1 existiert auf einem Branch, aber **kein einziger Eintrag in `config/volkseigenarten_config.json` nutzt das neue Schema**:

- `functions/volkseigenarten_funktionen.py`: neue Helfer `stufen_kosten_bereich(eigenart)` und `wende_stufe_an(eigenart, stufe)`
- `eigenart_zu_effekte` und `eigenart_zu_besonderheiten` lesen `ausgewaehlte_stufe` aus
- `validiere_volk_erstellung` lehnt Eigenarten mit `stufen` ohne Stufenwahl ab
- `lade_eigenarten_fuer_bearbeitung` stellt `ausgewaehlte_stufe` wieder her
- `views/volk_popup.py`: `_show_stufen_dialog` (Radio-Stil), Anzeige `[2-6 EP]` solange keine Stufe gewählt
- `test units/test_volkseigenarten_stufen.py`: 14 Unit-Tests

**Status:** Branch ist seit dem 27.04.2026 ungemergt. Vor Schritt 2 muss er entweder gemergt oder rebase't werden.

## Drei Sub-Probleme (vollständige Klassifikation aus `Texte/volksgenerierung.txt`)

### A) Mehrfachauswahl ohne Optionen (begrenzt oder unbegrenzt, gleiche Kosten je Instanz)

| Eigenart | max | Kosten je Instanz | Effekt je Instanz |
|---|---|---|---|
| Bewegungsweite (2) | 2 | 2 | +2 BW, +1 Würfeltyp Sprint |
| Geringeres Schlafbedürfnis (2) | 2 | 1 | 1× halb, 2× nie |
| Größe +1 (3) | 3 | 1 | +1 Robustheit, +1 max. Stärke |
| Panzerung (3) | 3 | 1 | +2 Panzerung |
| Parade (3) | 3 | 1 | +1 Parade |
| Reichweite (3) | 3 | 1 | +1 Reichweite |
| Robustheit (3) | 3 | 1 | +1 Robustheit |

### B) Mehrfachauswahl mit Optionen (Auswahl je Instanz)

| Eigenart | max | Kosten | Auswahl pro Instanz |
|---|---|---|---|
| Anfälligkeit für Naturgewalten (U) | 0 | -1 | Umgebungseffekt (Hitze, Kälte, Strahlung …) |
| Attributserhöhung (U) | 0 | 2 | Attribut |
| Furcht/Angst (2) | 2 | -2 | Furchtquelle |
| Handicap (U) | 0 | -1 / -2 | Handicap-Auswahl |
| Immunität gegen Gift oder Krankheit (2) | 2 | 1 | Gift / Krankheit |
| Volksfeind (U) | 0 | -1 | Anderes Volk im Setting |
| Weniger Grundfertigkeiten (5) | 5 | -1 | Eine Grundfertigkeit |
| Widerstand gegen Naturgewalten (U) | 0 | 1 | Umgebungseffekt |

### C) Punkte-Stufen (eine Auswahl, eine Stufe)

| Eigenart | Stufen | Kosten | Effekte |
|---|---|---|---|
| Attributsabzug (1×/Attribut) | 2 | -2 / -3 | -1 Attribut / -2 Attribut |
| Fertigkeit (1/Fert) | 2 | 1 / 2 | W4 / W6 (1 EP für Grundfert auf W6) |
| Fertigkeitsabzug (1×/Fert) | 2 | -1 / -2 | -1/-2 / -2/-4 (häufig vs. selten) |
| Fertigkeitsbonus (1/Fert) | 2 | 1 / 2 | +1 / +2 |
| Fliegen (1) | 3 | 2 / 4 / 6 | BW 6 / BW 12 / BW 24 + 2W6 Sprint |
| Giftige Berührung (1) | 2 | 1 / 3 | leicht / Betäubung-tödlich-lähmend |
| Handicap (U, je Instanz) | 2 | -1 / -2 | leicht / schwer |
| Hörner (1) | 2 | 1 / 2 | Stärke+W4 / Stärke+W6 |
| Klauen (1) | 3 | 2 / 3 / 4 | W4 / W6 / W6+PB2 |
| Regeneration (1) | 2 | 2 / 3 | täglich / +permanente Verletzungen |
| Verringerte Bewegungsweite (1) | 2 | -1 / -2 | -1 BW / -2 BW + Athletik-Malus |
| Wasserwesen (1) | 2 | 1 / 2 | amphibisch / heimisch |

### D) Sonderfälle (Grundkosten + variable Zusatzkosten)

| Eigenart | Formel | Notizen |
|---|---|---|
| Macht (U) | 2 + 1 je weitere | Erste Auswahl aktiviert AH (Begabt). Weitere Mächte erhöhen Mächte-Liste, **nicht** Machtpunkte. |
| Talent (U) | 2 + Rang (0–4) | Voraussetzungen außer „andere Talente" werden ignoriert. Max. Helden-Rang. |
| Superkräfte (1) | 2 + Punkte der gewählten Superkraft | Aktiviert AH (Superkräfte). Setting muss Superkräfte enthalten. |

## Vollständigkeits-Lücken in der heutigen Config

Aus den Regeln fehlen außerdem komplett (über Stufen/Mehrfach hinaus): **Biss**, **Graben**, **Keine lebenswichtigen Organe**, **Klauen**, **Macht (Volkseigenschaft)**, **Muss nicht atmen** als eigene Eigenart, **Panzerung**, **Parade**, **Reichweite**, **Springer**, **Superkräfte**, **Talent (Volk)**, **Wandkrabbler**, **Wärmesicht**, **Widerstand gegen Naturgewalten**, **Zäh**, **Zusätzliche Aktion**, **Anfälligkeit für Naturgewalten**, **Größe -1**, **Kann nicht sprechen**, **Schlechte Parade**, **Volksfeind**, **Weniger Grundfertigkeiten**, **Wuchtig**. Diese werden in Schritt 4 nachgezogen — vorgelagerte Schritte führen das Schema ein, ohne dass die Liste vollständig sein muss.

## Schritt 1 — Stufen-Eigenarten in Config nachziehen (Branch ist Code-fertig)

### 1a) Branch `claude/volkseigenarten-stufen` mergen

Vor allen weiteren Schritten: Branch in `main` mergen (oder rebase + Merge), damit Config-Edits gegen die neuen Helfer testbar sind. Die 14 Tests müssen weiter grün sein.

### 1b) Bestehende Mehrfach-Einträge konsolidieren

`config/volkseigenarten_config.json`:
- `fliegen_stufe1` / `fliegen_stufe2` / `fliegen_stufe3` zu **einer** Eigenart `fliegen` mit `stufen`-Array zusammenfassen.

```json
{
    "id": "fliegen",
    "name": "Fliegen",
    "max_auswahl": 1,
    "beschreibung": "Das Volk kann fliegen. In der Luft wird mit Athletik manövriert.",
    "effekt_typ": "spezieller_effekt",
    "stufen": [
        {"label": "Bewegungsweite 6", "kosten": 2, "effekt": {"fliegen": true, "bewegungsweite_flug": 6}},
        {"label": "Bewegungsweite 12", "kosten": 4, "effekt": {"fliegen": true, "bewegungsweite_flug": 12}},
        {"label": "Bewegungsweite 24, Sprint 2W6", "kosten": 6, "effekt": {"fliegen": true, "bewegungsweite_flug": 24, "sprint_wuerfel": "2W6"}}
    ]
}
```

### 1c) Restliche Stufen-Eigenarten aus Sub-Problem C neu/konsolidiert anlegen

Für jede Eigenart aus Tabelle C einen Eintrag mit `stufen`-Array anlegen. Beispiele:

```json
{"id": "klauen", "name": "Klauen", "max_auswahl": 1, "effekt_typ": "natuerliche_waffe",
 "stufen": [
   {"label": "Stärke + W4", "kosten": 2, "effekt": {"klauen": "W4"}},
   {"label": "Stärke + W6", "kosten": 3, "effekt": {"klauen": "W6"}},
   {"label": "Stärke + W6, PB 2", "kosten": 4, "effekt": {"klauen": "W6", "panzerbrechend": 2}}
 ]
}
```

```json
{"id": "regeneration", "name": "Regeneration", "max_auswahl": 1, "effekt_typ": "spezieller_effekt",
 "stufen": [
   {"label": "Täglich", "kosten": 2, "effekt": {"regeneration": "taeglich"}},
   {"label": "Inkl. permanente Verletzungen", "kosten": 3, "effekt": {"regeneration": "permanent"}}
 ]
}
```

`Hörner`, `Wasserwesen`, `Giftige Berührung`, `Verringerte Bewegungsweite`, `Attributsabzug`, `Fertigkeitsabzug`, `Handicap`, `Fertigkeit`, `Fertigkeitsbonus` analog. Achtung: **Fertigkeit / Fertigkeitsbonus / Handicap / Attributsabzug / Fertigkeitsabzug** sind sowohl Stufen- *als auch* Mehrfachauswahl-Eigenarten — die Stufe gilt pro Instanz, also bei Schritt 2 noch einmal anfassen.

### 1d) Test-Anpassungen

Bestehende Volk-Regressionstests, die `fliegen_stufe2` o. ä. erwarten, auf das neue ID-Schema umstellen. Wenn vorhandene Charakter-JSONs `effects.eigenarten` mit alten IDs enthalten, einen kleinen Migrationspfad in `lade_eigenarten_fuer_bearbeitung` ergänzen (alte ID → neue ID + Stufe).

---

## Schritt 2 — Mehrfachauswahl-UI (Sub-Probleme A + B)

### 2a) Schema-Erweiterung

`config/volkseigenarten_config.json`:

- `max_auswahl: 0` → unbegrenzt (bereits dokumentiert, aber UI handhabt es nicht)
- `max_auswahl: 2..N` → bis zu N Instanzen
- Neues optionales Feld `kosten_per_instanz: true` (Default: true) — explizit machen, dass Kosten pro Instanz gelten. Für Sonderfälle (Schritt 3) wird das auf `false` gesetzt.

### 2b) UI-Wechsel: Checkbox → Stepper bei `max_auswahl != 1`

`views/volk_popup.py:399-446` — die Checkbox-Schleife wird so umgebaut:

```
[Robustheit                  [1 EP]    (3×) ]   [ −  2  + ]
[Anpassungsfähig             [2 EP]         ]   [ ☐ ]      ← bleibt Checkbox
[Attributserhöhung           [2 EP]    (U)  ]   [ −  3  + ]
```

- `+`-Button: ruft `_toggle_eigenart(eigenart_id, eigenart_typ, active=True)` auf — bei Optionen-Eigenarten öffnet sich der Optionen-Dialog (Attribut wählen etc.); bei Stufen-Eigenarten der Stufen-Dialog. Jede Bestätigung legt eine **neue Instanz** in `aktuelle_auswahl` an.
- `−`-Button: entfernt die letzte Instanz dieser Eigenart-ID.
- Bei `max_auswahl == 1` weiterhin Checkbox.
- Bei `max_auswahl == 0` (`U`) ist `+` immer aktiv.
- Bei `max_auswahl > 1` wird `+` deaktiviert (`disabled=True`), wenn `aktuelle_anzahl >= max_auswahl`.
- Debounce 500 ms wie bei Checkboxen (siehe `CLAUDE.md`). Da wir bereits in einem Popup mit eigenem ScrollView sind, ist das OK — aber Stepper-Buttons sind nicht in `CLAUDE.md` validiert. **Risiko-Mitigation:** Falls Touch-Bounce auf Android auftritt, fallback auf das Pattern „Klick auf Zeile öffnet ein separates Stepper-Popup" (siehe Risiken).

### 2c) Anzeige der Einzel-Instanzen

Im Volk-Bearbeiten-View (Anzeige der gewählten Eigenarten) jede Instanz separat listen, mit individuellem `×`-Entfernen-Button:

```
Attributserhöhung — Stärke           [2 EP] [×]
Attributserhöhung — Verstand         [2 EP] [×]
Robustheit                           [1 EP] [×]
Robustheit                           [1 EP] [×]
```

`eigenart_zu_besonderheiten` muss je Instanz formatiert werden (heute schon eine Liste — passt, nur eindeutige Anzeige sicherstellen).

### 2d) `berechne_punktestand` & `validiere_volk_erstellung`

- Schon kompatibel: liest jede Auswahl einzeln. Aber: `validiere_volk_erstellung` muss `max_auswahl` *pro ID* zählen und gegen das Limit prüfen.
- Für Eigenarten mit Stufe + Optionen + mehrfach (z. B. `Fertigkeit (1/Fert)`): Es ist je Fertigkeit eine separate Instanz, jede Instanz hat ihre eigene Stufenwahl.

### 2e) `eigenart_zu_effekte`

Pro Instanz separat in `effects['eigenarten']` schreiben (heute schon der Fall). Aber: für gleichartige Effekte (z. B. 2× Robustheit = +2) muss der Aufruf zum Charakter-Effekt summieren, nicht überschreiben. `functions/volk_funktionen.py` prüfen.

---

## Schritt 3 — Sonderfälle (Sub-Problem D)

### 3a) Macht (2 + 1 je weitere)

Schema-Erweiterung in `config/volkseigenarten_config.json`:

```json
{
    "id": "volk_macht",
    "name": "Macht",
    "max_auswahl": 0,
    "kosten": 2,
    "kosten_zusatz_je_weitere": 1,
    "effekt_typ": "macht_volk",
    "optionen": {"typ": "macht_auswahl"}
}
```

`berechne_punktestand`: Sonderfall:

```
if eigenart.id == 'volk_macht':
    kosten = 2 + max(0, anzahl - 1) * 1
else:
    kosten = eigenart.kosten * anzahl
```

`functions/volk_funktionen.py`: Erste Macht-Auswahl aktiviert AH (Begabt) automatisch (Pattern aus `Magieaffin`-Logik in Commit `57b4c59`). Weitere Mächte erhöhen nur Mächte-Liste — **keine zusätzlichen Machtpunkte**.

UI: Optionen-Dialog `macht_auswahl` (neuer Optionen-Typ in `volk_popup.py`). Liefert eine Macht aus `models/macht.py` zurück.

### 3b) Talent (2 + Rang)

Schema-Erweiterung:

```json
{
    "id": "volk_talent",
    "name": "Talent",
    "max_auswahl": 0,
    "kosten": 2,
    "kosten_zusatz_je_rang": 1,
    "effekt_typ": "talent_volk",
    "optionen": {"typ": "talent_rang_auswahl"}
}
```

`berechne_punktestand`: 

```
kosten = 2 + rang  # rang 0=Anfänger, 1=Erfahren, ..., 4=Held
```

UI: Zwei-Schritt-Dialog
1. Talent wählen (alle Voraussetzungen außer „anderes Talent" ignorieren — entspricht der `skip_prereq_check`-Variante aus `talent_funktionen.talent_auswaehlen`)
2. Rang wählen (Anfänger / Erfahren / Veteran / Heroisch / Held)

`functions/volk_funktionen.py`: Talent regulär über `talent_funktionen.talent_auswaehlen(charakter, name, skip_prereq_check=True)` aktivieren, damit AH-Talente auch via Volk-Talent funktionieren (siehe `plans/freies_volk_talent_plan.md` für die Kopplung).

### 3c) Superkräfte (2 + X)

Schema-Erweiterung:

```json
{
    "id": "volk_superkraft",
    "name": "Superkräfte",
    "max_auswahl": 0,
    "kosten": 2,
    "kosten_zusatz_aus_option": "punkte_kosten",
    "effekt_typ": "superkraft_volk",
    "optionen": {"typ": "superkraft_auswahl"},
    "voraussetzung": "setting_hat_superkraefte"
}
```

`berechne_punktestand`:

```
kosten = 2 + selected_option.get('punkte_kosten', 0)
```

UI: Optionen-Dialog `superkraft_auswahl` nutzt `superkraft_funktionen.py` zum Auswählen einer Superkraft + ihrer Stufe. Liefert die Punktekosten als Bestandteil der Auswahl zurück.

`functions/volk_funktionen.py`: Aktiviert AH (Superkräfte) automatisch. Eigenart ist nur in Settings sichtbar, die Superkräfte enthalten — Filterung in `lade_volkseigenarten_config()` via `voraussetzung`-Feld.

---

## Schritt 4 — Vollständigkeit (Folge-Issue)

Eigenarten aus den Regeln, die heute komplett fehlen, in einem separaten Branch nachziehen. Liste siehe „Vollständigkeits-Lücken" oben. Dieser Schritt baut auf Schritt 1–3 auf, weil viele dieser Eigenarten Stufen oder Mehrfachauswahl brauchen (Panzerung 3, Parade 3, Reichweite 3, Größe +1 (3), Talent (U), Macht (U), Superkräfte (1), Anfälligkeit für Naturgewalten (U), Volksfeind (U), Widerstand (U), Weniger Grundfertigkeiten (5)).

---

## Datei-Übersicht (alle Schritte)

| Datei | Schritt | Änderung | Status |
|---|---|---|---|
| `config/volkseigenarten_config.json` | 1, 2, 3, 4 | `stufen`-Arrays, `kosten_per_instanz`, `kosten_zusatz_*`, neue Eigenarten | ✅ Teilweise |
| `functions/volkseigenarten_funktionen.py` | 1, 2, Multi-Slot | `stufen_kosten_bereich`, `wende_stufe_an`, `validiere_volk_erstellung` mit Mehrfach-Limits, `EFFEKT_TYPEN` mit `natuerliche_waffe`, `wahlmoeglichkeiten_counts`, `STUFEN_MIGRATIONS`, `kosten_per_instanz`-Flag | ✅ |
| `views/volk_popup.py` | 1, 2, Multi-Slot | Stepper-Widget bei `max_auswahl != 1`, `_show_stufen_dialog`, `_increment/decrement_eigenart`, `_refresh_eigenarten_popup`, Quick-Pick-Key-Fix, `reconcile_volk_auswahlen`-Aufruf, Volk-Rename | ✅ |
| `functions/volk_funktionen.py` | 2, Multi-Slot, Freies-Talent, Magieaffin | `slots`-Rückgabe in `get_volk_zusatzelemente`, `reset_volk_auswahlen` mit Listen, `reconcile_volk_auswahlen`, `waehle_freies_talent` delegiert an `talent_funktionen` (PR #162), `waehle_magieaffin_fertigkeit` mit AH-Talent-Auswahl + `extrahiere_arkane_fertigkeit_aus_ah` (PR #180) | ✅ |
| `views/voelker_view.py` | Multi-Slot, Freies-Talent | N Zeilen pro Slot, `slot_index`-Lambdas, Filter bereits gewählter Werte in Edit-Dialogen, `_on_edit_zusatzelement` für Talente, `_on_edit_magieaffin`, `aktualisiere_ui` synchronisiert aus `charakter.voelker_auswahlen` | ✅ |
| `views/voelker_auswahl_overlay.py` | Multi-Slot, Freies-Talent | N Cards pro Slot mit `n/N`-Fortschritt, `MULTI_SLOT_KEYS`-Konstante, Filter bereits gewählter Werte, `_show_talent_selection` mit Filter-Toggle und Voraussetzungs-Bestätigungsdialog (PR #162) | ✅ |
| `functions/charakter_speicher.py` | Multi-Slot | `voelker_auswahlen` Round-Trip + Skalar→Liste-Migration in `_finalize_character_loading` | ✅ |
| `functions/auto_character_generator.py` | Multi-Slot, race_choices (PR #176) | Listen-Keys `freie_talente` / `freie_attribute` / `attribute_malus` plus Legacy-Skalare; `_apply_race_choices` mit `race_choices`-Dict; `_resolve_key` Unicode-normalisiertes Matching; `steigerungs_journal` mit `kosten_typ` + `phase` | ✅ |
| `models/charakter_properties.py` | Multi-Slot | `voelker_auswahlen` als persistierte `DictProperty` | ✅ |
| `models/volk.py` | 2 | `effects['eigenarten']` ist bereits eine Liste | ✅ |
| `test units/test_volkseigenarten_stufen.py` | 1 | 14 Tests | ✅ |
| `test units/test_volkseigenarten_mehrfach.py` | 2 | 9 Tests | ✅ |
| `test units/test_volkseigenarten_multi_slot.py` | Multi-Slot | 14 Tests in 6 Gruppen | ✅ |
| `test units/test_volkseigenarten_stufen_migration.py` | Schritt 1d | 8 Tests für Migration alter Stufen-IDs | ✅ |
| `test units/test_volkseigenarten_schritt_2_rest.py` | Schritt 2a/2e | 9 Tests für `kosten_per_instanz` + Effekte summieren | ✅ |
| `test units/test_auto_generator_helpers.py` | race_choices (PR #176) | Tests für `_normalize_key`, `_resolve_key`, `_historie_dict`, race_choices-Schema | ✅ |
| `test units/test_volkseigenarten_sonderfaelle.py` | 3 | Tests für `volk_macht`/`volk_talent`/`volk_superkraft` Eigenarten | ⏳ Offen |

---

## Risiken & Edge Cases

1. **Datenmigration alter Charaktere.** Charaktere mit altem `fliegen_stufe2` in `effects.eigenarten` müssen beim Laden auf das neue Schema (`fliegen` + `ausgewaehlte_stufe`) gemappt werden. Pfad: `lade_eigenarten_fuer_bearbeitung` mit ID-Mapping-Tabelle für die konsolidierten Eigenarten.
2. **Backward-compat der Config.** Eigenarten ohne `stufen` müssen sich exakt wie heute verhalten (✅ in Schritt 1 schon berücksichtigt). Eigenarten ohne `kosten_zusatz_*` ebenfalls.
3. **Stepper-Buttons auf Android.** 500ms Debounce implementiert. **⚠️ Android-Smoke-Test ausstehend** — verifizieren dass Touch-Bounce nicht zu Doppel-Increment führt.
4. **Validierung mehrfacher Instanzen mit gleicher Option.** Beispiel: 2× „Attributserhöhung — Stärke" — die Regeln erlauben max. 1× pro Attribut. Validierung muss nicht nur `max_auswahl` sondern auch Optionen-Eindeutigkeit prüfen, wo es Sinn ergibt (Attribut, Fertigkeit, Volk bei Volksfeind).
5. **Punkte-Anzeige im Wizard.** `formatiere_punkte_anzeige` muss Macht-Degression (2 + 1 + 1 + …) statt simpler Multiplikation berücksichtigen (Schritt 3).
6. **Setting-Filterung Superkräfte.** Eigenart `volk_superkraft` darf nur in Settings auftauchen, die Superkräfte unterstützen. Das Setting-Feature-Flag liegt in `settings/*.json` — Lade-Filter in `lade_volkseigenarten_config()`.
7. **Talent-Voraussetzungs-Sonderregel.** Volks-Talent (Schritt 3b) ignoriert Voraussetzungen außer „andere Talente". Das `skip_prereq_check`-Pattern ist durch PR #162 (`talent_funktionen.talent_auswaehlen(skip_prereq_check=True)`) und den Voraussetzungs-Bestätigungsdialog im Volk-Talent-Overlay schon verfügbar — Schritt 3b braucht nur die Volkseigenart selbst plus die Kosten-Formel `2 + Rang`.
8. **Auto-Talente / Auto-Handicaps doppelt ausgelöst.** Wenn Macht (Schritt 3a) AH (Begabt) aktiviert und der User AH (Begabt) zusätzlich als reguläres Talent wählt, darf nichts doppelt einfließen. `_apply_ah_auto_effects` ist seit PR #180 idempotent (Magieaffin testet `if not ah_talent.ausgewaehlt: ...` vor Aktivierung) — diese Idempotenz muss für `volk_macht` (Schritt 3a) übernommen werden.
9. **Stufen × Multi-Slot Verschränkung.** Eigenarten aus Tabelle C, die `max_auswahl > 1` haben (Fertigkeit, Fertigkeitsbonus, Handicap, Attributsabzug, Fertigkeitsabzug), brauchen pro Slot eine eigene Stufenwahl + Optionswert. Im Wizard wird das via separate Eigenart-Instanzen in `volk.eigenarten` gelöst; jede Instanz behält ihre `ausgewaehlte_stufe`. Round-Trip nach Reload für Multi-Slot Stufen-Eigenarten ist **noch nicht regressionsgetestet** — Test-Lücke für Schritt 1d.
10. **Zwei UI-Pfade für Mehrfachauswahl.** Wizard-Stepper (Schritt 2) vs. Völker-Tab Auswahl-Cards (Multi-Instance-Branch) speisen sich aus unterschiedlichen Datenebenen — der Stepper definiert `max_auswahl` / Anzahl der Eigenart-Instanzen im *Volk*, die Cards bestücken die *Pro-Charakter-Auswahl*. Beim PR-Merge muss verifiziert sein, dass beide Pfade konsistent zählen (`wahlmoeglichkeiten_counts` aus `eigenart_zu_effekte` ⇆ `voelker_auswahlen[volk][typ]`-Längen).

---

## Reihenfolge & PR-Strategie

1. **✅ PR 1 — Branch `claude/volkseigenarten-stufen` mergen.** (Commit `5740ec0`) — **ERLEDIGT**
2. **✅ PR 2 — Schritt 1 Config (Stufen-Eigenarten).** (Hörner, Klauen, Regeneration, etc.) — **ERLEDIGT**
3. **✅ PR 3 — Schritt 2 Mehrfach-UI.** Stepper-Buttons, validiere_volk_erstellung — **ERLEDIGT**
4. **✅ PR 4 — Verzögerte Auswahl.** `auswahl_verzoegert` in Config, `_show_optionen_dialog`, `eigenart_zu_effekte` — **ERLEDIGT**
5. **✅ PR #162 — Freies Volk-Talent ändern + AH-Aktivierung.** `talent_funktionen.talent_auswaehlen`-Delegation, Filter-Toggle, Voraussetzungs-Bestätigungsdialog, Edit-Modus für freies_talent — **ERLEDIGT**
6. **✅ PR #176 — Auto-Generator: race_choices + Steigerungshistorie.** `_apply_race_choices` mit Volks-Wahlmöglichkeiten-Dict, `_resolve_key` Unicode-Matching, `steigerungs_journal` mit `kosten_typ` + `phase` — **ERLEDIGT**
7. **✅ PR #180 — Magieaffin → AH-Talent (freier Arkaner Hintergrund).** `extrahiere_arkane_fertigkeit_aus_ah`, `_ist_ah_talent`, AH-Talent-Auswahl im Setting statt fester Liste — **ERLEDIGT**
8. **✅ PR 5 (#182) — Bugfix Attributs-Schwäche-Edit + Stepper-Counter.** — **ERLEDIGT**
9. **✅ PR 6 (#196) — Multi-Slot im Völker-Tab.** `wahlmoeglichkeiten_counts`, `slots`-Dict, `voelker_auswahlen` als persistierte DictProperty, N Cards pro Slot — **ERLEDIGT**
10. **✅ PR 7 (#197) — Schritt 1d.** Migration Tests für `fliegen_stufe` (`STUFEN_MIGRATIONS` + `eigenart_typ`-Lookup-Fix) — **ERLEDIGT**
11. **✅ PR 8 (#198) — Schritt 2 (Rest, 2a + 2e).** `kosten_per_instanz`-Feld; Effekte summieren — **ERLEDIGT**
12. **✅ PR 9 — Schritt 3 Sonderfälle.** `volk_macht` (Kosten 2+1×(N-1)), `volk_talent` (Kosten 2+Rang), `volk_superkraft` (Kosten 2+SKP), Setting-Filterung — **ERLEDIGT**
13. **⏳ PR 8b — Schritt 2c.** Wizard-Review-Step widgetisieren mit Einzel-Instanzen + ×-Buttons — **OFFEN, erfordert UI-Rewrite**
14. **⏳ PR 10+ — Schritt 4 Vollständigkeit.** Pro Themenblock ein PR — **OFFEN**

---

## Verifikation

### Unit-Tests

Pro Schritt eigene Tests in `test units/`:
- **Schritt 1 (vorhanden):** `test_volkseigenarten_stufen.py` — 14 Tests
- **Schritt 1d (vorhanden, PR #197):** `test_volkseigenarten_stufen_migration.py` — 8 Tests für Migration alter Stufen-IDs
- **Schritt 2:** `test_volkseigenarten_mehrfach.py` — 9 Tests (Mehrfach-Limit, Stepper-State, Optionen pro Instanz, gleiche Option doppelt verhindern, Punkte-Summe)
- **Schritt 2 (Rest, vorhanden, PR #198):** `test_volkseigenarten_schritt_2_rest.py` — 9 Tests für `kosten_per_instanz` + Effekte summieren
- **Multi-Slot Völker-Tab (vorhanden, PR #196):** `test_volkseigenarten_multi_slot.py` — 14 Tests in 6 Gruppen
- **race_choices / Auto-Generator (vorhanden, PR #176):** `test_auto_generator_helpers.py` — `_normalize_key`, `_resolve_key`, `_historie_dict`, race_choices-Schema-Coverage
- **Schritt 3:** `test_volkseigenarten_sonderfaelle.py` (neu) — Macht-Degression (2/3/4 EP für 1/2/3 Mächte), Talent-Rang-Kosten, Superkraft-X-Aufschlag, AH-Aktivierung idempotent

Voraussetzung: `python "test units/run_all_tests.py"` muss nach jedem Schritt grün sein (aktuell: 927 Tests).

### Manuelle Tests

- App starten (`python main.py`), Volk Editor öffnen.
- **Schritt 1:** Fliegen wählen → Stufen-Dialog erscheint → BW 12 (4 EP) wählen → in der Liste steht „Fliegen [4 EP] · Bewegungsweite 12". Volk speichern, neu laden — Stufenwahl erhalten.
- **Schritt 2:** Robustheit 3× wählen über Stepper → Punkte korrekt summiert (3 EP). 4. Klick disabled. Attributserhöhung 2× wählen mit verschiedenen Attributen → in der Übersicht zwei Chips „Stärke" + „Verstand".
- **Schritt 3:** Volk-Macht 2× wählen → Punktestand 2 + 1 = 3 EP. AH (Begabt) im Charakter-View aktiviert, Mächte-Liste enthält beide gewählten Mächte, Machtpunkte unverändert von Volk-Macht.
- **Multi-Slot:** Custom-Volk mit 2× `attributserhoehung` erstellen, Volk einem Charakter zuweisen → Overlay zeigt zwei Cards „Freies Attribut (1/2)" / „(2/2)" → Stärke + Verstand wählen → im Völker-Tab zwei Zeilen mit eigenen Edit-Buttons, beide W6. Speichern, neu laden — beide Slots erhalten. Custom-Volk auf 1× reduzieren → `reconcile_volk_auswahlen` rollt zweiten Slot zurück (Verstand W4), im Tab nur eine Zeile.
- **Magieaffin (PR #180):** Volk mit Magieaffin-Eigenart einem Charakter zuweisen → Overlay zeigt AH-Talente des aktiven Settings als „AH (Wunder) → Glaube"-Tupel → AH (Magie) wählen → im Charakter-Tab ist „Arkaner Hintergrund (Magie)" als ausgewähltes Talent sichtbar, Mächte-Slots aktiviert, Machtpunkte gemäß Talent-Definition gesetzt.
- **Freies Volk-Talent (PR #162):** Mensch wählen → Filter-Toggle (Filter-Icon) im Talent-Auswahl-Dialog umschalten → Talent mit nicht erfüllten Voraussetzungen wählen → Bestätigungsdialog erscheint → „Trotzdem auswählen" → Talent gewählt. Stift-Icon im Völker-Tab nutzen → Auswahl ändern → vorheriges Talent wird sauber abgewählt (inkl. AH-Effekte falls AH-Talent).

### Android-Smoke-Test

Nach Schritt 2: Stepper-Buttons im Volk-Editor antippen, prüfen dass Touch-Bounce nicht zu Doppel-Increment führt. Falls ja: Mitigation aus „Risiken" Punkt 3 anwenden.

### Backward-Compat-Test

Ein älteres Charakter-JSON mit `effects.eigenarten` der alten Form (`fliegen_stufe2`) laden. Erwartung: lädt fehlerfrei, Eigenart wird als „Fliegen — BW 12" angezeigt, Speichern schreibt das neue Schema zurück.
