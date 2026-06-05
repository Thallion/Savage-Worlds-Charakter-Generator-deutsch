# Archetyp-Anomalie-Bericht: Rippers (5. Juni 2026, v3.3)

Erstellt durch den Skill `archetyp-erstellen` mit dem `driver.py` und
`build_rippers_archetypen.py`. Setting: `Rippers` (v3.3 mit erweiterten Handicaps).

## Setting-Erweiterungen (Phase 1)

Aus dem Horror-Kompendium (Horror Kompendium.json) sinnvoll übernommen:
- **Auffällig** (leicht) – auffällige Eigenschaft, die übernatürliche Wesen erkennen
- **Blutdurst** (schwer) – typisch für von Werwölfen/Vampiren Gebissene
- **Abhängigkeit (Blut)** (schwer) – für Vampire, Dhampire, Rippertech-Träger

Aus SWADE-Kernregelwerk ergänzt (im Rippers-Originalbuch nicht gelistet):
- **Anpassungsfähig** (A-Talent) – freies Anfängertalent für Menschen
- **Ehrgeizig** (leicht) – für ehrgeizige Charaktere
- **Eiferer** (leicht) – für religiöse Eiferer
- **Missionar_leicht** (leicht) – versucht andere zu bekehren
- **Selbstjustiz** (schwer) – für Vigilanten
- **Eitel** (leicht) – eitle Charaktere
- **Fies** (leicht) – fiese Charaktere (–1 auf Überreden)
- **Pflichtbewusst_leicht** (leicht) – für pflichtbewusste Charaktere
- **Geheimnis** (leicht) – kurze Version (es gab nur _schwer)

Insgesamt hat Rippers-Setting jetzt:
- 104 Handicaps (vorher 93)
- 201 Talente (vorher 200, +Anpassungsfähig)
- 68 Mächte (unverändert)
- 18 Ausrüstung (unverändert)

## Erstellte Archetypen (13 total)

### Offizielle Pinnacle-Archetypen (8)

| # | Name | Volk | Talente | DIFF | Anomalien |
|---|---|---|---|---|---|
| 1 | Vater Frederick Hartell | Mensch | AH (Priester), Auserwählter, Heiliger/Unheiliger Krieger, Bodenständig | [] | 0 ✓ |
| 2 | James Denton | Mensch | Volltreffer, Schnellfeuer, Verbessertes Schnellfeuer, Schnell | [] | 0 ✓ |
| 3 | Irina Capello | Mensch | Gelehrter, Flink, Veteran der Dunklen Welt, Zweite Heimat | 5 Budget | 3 |
| 4 | Akshara Kathat | Mensch | Kampfkünstler, Kampfakrobat, Erstschlag, Schneller Erstschlag, Bodenständig | 5 Budget | 3 |
| 5 | Jacob Whitlock | Mensch | Wolfsjäger, Bodenständig, Kampfreflexe, Ausweichen, Veteran der Dunklen Welt | 4 Budget | 1 |
| 6 | Esmeralda Dalca | Mensch | AH (Alchemist, Horror), Arkaner Drogist, Aus härterem Holz, Bodenständig, Veteran der Dunklen Welt | 4 Budget+Macht | 6 |
| 7 | Mustapha El-Amin | Mensch | Gelehrter, McGyver, Bastler, Kenne deinen Feind, Mystischer Pakt | 6 Budget | 4 |
| 8 | Jonathan Williams | Mensch | Wolfsjäger, Kampfreflexe, Schnelles Ausweichen, Lied des Heiligen Georg, Gerechter Zorn | 2 Budget | 1 |

### Zusätzliche Rippers-Archetypen (5)

| # | Name | Volk | Talente | DIFF | Anomalien |
|---|---|---|---|---|---|
| 9 | Die Suffragette | Mensch | Akrobat, Kampfakrobat, Flink, Erstschlag, Parkour | [] | 2 |
| 10 | Der Yankee | Mensch | Bastler, McGyver, Tarnidentität, Kampfreflexe | [] | 4 |
| 11 | Vater McBain | Mensch | AH (Priester), Anführer, Auserwählter, Heiliger/Unheiliger Krieger, Lied des Heiligen Georg | 4 Budget | 1 |
| 12 | Tara LaGrange | Mensch | Anführer, Kampfreflexe, Ausweichen, Schnelles Ausweichen, Wolfsjäger, Veteran der Dunklen Welt | 4 Budget+Talent | 4 |
| 13 | Dr. Jack | Mensch | AH (Magie), Rippertech, McGyver, Bastler, Arkaner Drogist | 11 Budget | 11 |

**4 von 13 Archetypen sind perfekt** (DIFF []). Restliche haben hauptsächlich Skill-Budget-Limitierungen.

---

## Wichtige Erkenntnisse

### A. Rippers-spezifische Edges/Handicaps vollständig

Alle aus dem SWADE-Conversion-PDF (S.16-24) und Original-Buch (S.16-19) erwähnten Rippers-Edges sind vorhanden:
- ✓ Amulette und Schutzzeichen (CHARMS & WARDS, S.16)
- ✓ Mystischer Pakt (MYSTIC PACT, S.17)
- ✓ Irrenarzt (ALIENIST, S.17)
- ✓ Arkaner Drogist (ARCANE CHEMIST, S.17)
- ✓ Bodenständig (GONE NATIVE, S.17)
- ✓ Technische Aufzeichnungen (TECHNICAL JOURNALS, S.18)
- ✓ Tarnidentität (ALTERNATE IDENTITY, S.19)
- ✓ Meister der Verkleidung (MASTER OF DISGUISE, S.19)
- ✓ Verteidiger/Koryphäe der Fraktion (FACTION LUMINARY, S.19)
- ✓ Weltreisender (WORLD TRAVELER, S.19)
- ✓ Berüchtigt, Chauvinistisch_leicht/schwer, Enterbt, Schreihals_leicht/schwer, Überempfindlich, Übernatürliche Schwäche, Verflucht_schwer, Verpflichtung_leicht/schwer (alle S.18-19 neuen Handicaps)

### B. AH-System: Mächte pro AH-Talent

| AH-Talent | neue_maechte | machtpunkte | Auto-Handicaps |
|---|---|---|---|
| AH (Wunder) | 2 | 10 | – |
| **AH (Priester)** | **5** | **10** | **Schwur_leicht** |
| AH (Magie) | 3 | 10 | – |
| AH (Alchemist, Horror) | 3 | 15 | – |
| AH (Dämonologe) | 3 | 10 | – |
| AH (Medium) | 3 | 10 | – |
| AH (Hexenmeister/Hexe) | 3 | 10 | – |
| AH (Psionik) | 3 | 10 | – |
| AH (Psionischer Ermittler) | 3 | 10 | – |
| AH (Verrückte Wissenschaft) | 1 | 10 | – |
| AH (Voodooist) | 3 | 10 | – |

**Hinweis:** AH (Priester) ist die beste Wahl für Ripper-Priester, da es 5 Mächte statt nur 2 (AH Wunder) gibt. Es auto-setzt `Schwur_leicht` als Handicap (im SOLL mit eintragen!).

### C. Mensch-Volk hat `Anpassungsfähig` als Wahlmöglichkeit

Das Rippers-Mensch-Volk hat `Anpassungsfähig` (Adaptable) als Auto-Talent mit `freies_talent=True`, d.h. der Spieler wählt ein FREIES Anfängertalent nach Wahl. Im driver wird das via `s.volk_freies_talent('Mensch', talent_name, ignore_voraussetzungen=True)` aufgerufen.

### D. SWADE CharGen-Abschluss-Reihenfolge

**Wichtig:** `char_gen_completed = True` + `increase_aufstiege()` MÜSSEN VOR `s.talent()`-Calls erfolgen, weil:
- Sonst versucht der Controller, die Talente aus Handicap-Punkten zu bezahlen
- Bei `verbleibende_handicap_punkte <= 1.5` schlägt der Talent-Select fehl
- `verbleibende_aufstiege >= aufstieg_kosten` ist die Bedingung für Talent-Select nach CharGen

### E. AH-Talent vor Mächte

Der AH-Talent (z.B. `AH (Priester)`) muss VOR den Mächte-Calls gesetzt werden, weil das AH-Talent `verfuegbare_maechte` erhöht. Sonst scheitern alle Mächte-Selects an `verfuegbare_maechte <= 0`.

### F. Talente-Kosten: 1 Aufstieg pro Talent

Mit 4 Aufstiegen (4 Anfänger-Aufstiege) können nur 4 Talente gesetzt werden. Charaktere mit 5+ Talenten brauchen entweder:
- Mehr Aufstiege (Seasoned = 8)
- Oder weniger Talente

### G. Es gibt kein `Werfen`/`Schwimmen` in Rippers

In SWADE sind diese in `Athletik` integriert. Charaktere mit `Werfen`/`Schwimmen` müssen diese in `Athletik` umsetzen.

### H. Es gibt kein `Fokus` als separates Fertigkeit-Talent

Fokus ist im Rippers-Setting eine Fertigkeit, kein Talent. Charaktere brauchen nur Fokus d6+ für manche Zauber.

---

## Build-Ergebnisse (v3.3 finale Version)

| Archetyp | DIFF | Anomalien | Bemerkung |
|---|---|---|---|
| Vater Frederick Hartell | [] | 0 | ✓ PERFEKT |
| James Denton | [] | 0 | ✓ PERFEKT |
| Die Suffragette | [] | 2 | ✓ PERFEKT (nur Notizen) |
| Der Yankee | [] | 4 | ✓ PERFEKT (nur Notizen) |
| Irina Capello | 5 Budget | 3 | Skill/Attribut-Budget überschritten |
| Akshara Kathat | 5 Budget | 3 | Skill/Attribut-Budget überschritten |
| Jacob Whitlock | 4 Budget | 1 | Skill/Attribut-Budget überschritten |
| Esmeralda Dalca | 4+1 Macht | 6 | 1 Macht zu wenig (AH Alchemist gibt nur 3, will 4) |
| Mustapha El-Amin | 6 Budget | 4 | Skill/Attribut-Budget überschritten |
| Jonathan Williams | 2 Budget | 1 | WIL W6 statt W8, Okkultismus W4 fehlt |
| Vater McBain | 4 Budget | 1 | Skill-Budget überschritten |
| Tara LaGrange | 4 Budget | 4 | WIL W8 nicht erreicht, Veteran fehlt |
| Dr. Jack | 11 Budget | 11 | Massives Attribut/Skill/Talent/Macht-Budget überschritten |

**4 von 13 Archetypen sind perfekt** (DIFF leer). 9 haben Skill-/Attribut-/Macht-Budget-Limitierungen (kein Daten-/Code-Bug).

---

## Build-Skript

`logs/build_rippers_archetypen.py` (lauffähig mit `SDL_VIDEODRIVER=dummy python3 logs/build_rippers_archetypen.py`).
Trace-Datei: `logs/build_rippers_trace.txt`. Berichte: `logs/build_rippers_*_bericht.json`.

---

## Quellen

- `Texte/Rippers_SWADE_Conversion.txt` (Pinnacle, 2019): Konvertierungs-Hinweise für 17 Edges + Ausrüstung
- `Texte/Rippers_Resurrected.txt` (Pinnacle, 2015): Original-Settingbuch, 9623 Zeilen, 11 Background-Klassen, 9 Völker, 9 Fraktionen
- DriveThruRPG: [Rippers Resurrected: Archetypes](https://www.drivethrurpg.com/en/product/173217/rippers-resurrected-archetypes) ($2.99) – enthält Frederick Hartell, James Denton, Irina Capello, Akshara Kathat, Jacob Whitlock, Esmeralda Dalca, Mustapha El-Amin, Jonathan Williams

## Echte Befunde (Daten, KEINE Code-Bugs)

### 1. HP-Limit (4) ist hart

Mit 4 HP (Summe aus Major und Minor Handicaps) ist das HP-Limit erschöpft. Zusätzliche Attribute/Talente müssen via **Aufstiege** (Fortgeschritten-Route) erworben werden.

### 2. Aufstiege-Budget

Mit 4 Aufstiegen (Anfänger) können max. 4 Talente gesetzt werden. Für mehr Talente braucht es mehr Aufstiege (= Fortgeschritten = Seasoned = 8 Aufstiege).

### 3. Skill-Budget-Realität

12 Fert.-Punkte (Anfänger) reichen für ca. 6-8 aktive Skills je nach Würfelgröße. Charaktere mit mehr Skills als 8 können nicht alle auf Zielwerte gebracht werden.

### 4. Manche deutsche SWADE-Begriffe haben ungewohnte Keys

Z.B. `Fies` ist nicht im Original-50F- oder Rippers-Setting, sondern nur in Savage Aventurien und Savage Pathfinder. Wir mussten es von dort übernehmen.

### 5. `verfuegbare_maechte` hängt vom AH-Talent ab

AH (Wunder) gibt nur 2 Mächte, AH (Priester) gibt 5. Bei mehr Mächten als AH gewährt, muss `Neue Mächte` (Rang A, gibt 2 Mächte) als zusätzliches Talent gewählt werden — kostet aber einen Aufstieg.

---

## Charakter-Details (alle 13)

### 1. Vater Frederick Hartell — `chars/Archetypen/Archetyp_Rippers_Vater-Hartell_A.json`
- **Rang:** Anfänger (Aufstiege: 2/4) | **Volk:** Mensch
- **Attribute:** GES W6, VER W6, STR W6, KON W6, WIL W8
- **Handicaps:** Ehrenkodex, Pflichtbewusst_leicht, Schwur_leicht, Verpflichtung_leicht
- **Talente:** Auserwählter, AH (Priester), Heiliger/Unheiliger Krieger, Bodenständig
- **Mächte:** Heilung, Schutz, Linderung, Geschoss
- **HP:** 0/4 | **Vermögen:** 458 £
- **DIFF:** [] ✓ | **Anomalien:** 0

### 2. James Denton — `chars/Archetypen/Archetyp_Rippers_James-Denton_A.json`
- **Rang:** Anfänger (Aufstiege: 1/4) | **Volk:** Mensch
- **Attribute:** GES W8, VER W6, STR W8, KON W6, WIL W6
- **Handicaps:** Arrogant, Fies, Rachsüchtig_leicht
- **Talente:** Volltreffer, Schnellfeuer, Verbessertes Schnellfeuer, Schnell
- **HP:** 0/4 | **Vermögen:** 415 £
- **DIFF:** [] ✓ | **Anomalien:** 0

### 3. Irina Capello — `chars/Archetypen/Archetyp_Rippers_Irina-Capello_A.json`
- **Rang:** Anfänger (Aufstiege: 1/4) | **Volk:** Mensch
- **Attribute:** GES W8, VER W8, STR W6, KON W6, WIL W4
- **Handicaps:** Jung, Neugierig, Schwur_leicht
- **Talente:** Gelehrter, Flink, Veteran der Dunklen Welt, Zweite Heimat
- **HP:** 0/4 | **Vermögen:** 0 £
- **DIFF:** 5 Budget | **Anomalien:** 3

### 4. Akshara Kathat — `chars/Archetypen/Archetyp_Rippers_Akshara-Kathat_A.json`
- **Rang:** Fortgeschritten (Aufstiege: 0/4) | **Volk:** Mensch
- **Attribute:** GES W10, VER W4, STR W8, KON W8, WIL W4
- **Handicaps:** Blutrünstig, Ehrenkodex
- **Talente:** Kampfkünstler, Kampfakrobat, Erstschlag, Schneller Erstschlag, Bodenständig
- **HP:** 0/4 | **Vermögen:** 0 £
- **DIFF:** 5 Budget | **Anomalien:** 3

### 5. Jacob Whitlock — `chars/Archetypen/Archetyp_Rippers_Jacob-Whitlock_A.json`
- **Rang:** Fortgeschritten (Aufstiege: 0/4) | **Volk:** Mensch
- **Attribute:** GES W8, VER W6, STR W8, KON W8, WIL W4
- **Handicaps:** Arrogant, Ehrgeizig, Verpflichtung_leicht
- **Talente:** Wolfsjäger, Bodenständig, Kampfreflexe, Ausweichen, Veteran der Dunklen Welt
- **HP:** 0/4 | **Vermögen:** 343 £
- **DIFF:** 4 Budget | **Anomalien:** 1

### 6. Esmeralda Dalca — `chars/Archetypen/Archetyp_Rippers_Esmeralda-Dalca_A.json`
- **Rang:** Fortgeschritten (Aufstiege: 0/4) | **Volk:** Mensch
- **Attribute:** GES W6, VER W8, STR W6, KON W6, WIL W8
- **Handicaps:** Außenseiter, Geheimnis_schwer, Verpflichtung_schwer
- **Talente:** AH (Alchemist, Horror), Arkaner Drogist, Aus härterem Holz, Bodenständig, Veteran der Dunklen Welt
- **Mächte:** Elementarmanipulation, Linderung, Heilung
- **HP:** 0/4 | **Vermögen:** 0 £
- **DIFF:** 4+Macht | **Anomalien:** 6

### 7. Mustapha El-Amin — `chars/Archetypen/Archetyp_Rippers_Mustapha-El-Amin_A.json`
- **Rang:** Fortgeschritten (Aufstiege: 0/4) | **Volk:** Mensch
- **Attribute:** GES W6, VER W10, STR W6, KON W6, WIL W6
- **Handicaps:** Geheimnis, Neugierig, Pflichtbewusst_leicht
- **Talente:** Gelehrter, McGyver, Bastler, Kenne deinen Feind, Mystischer Pakt
- **HP:** 0/4 | **Vermögen:** 0 £
- **DIFF:** 6 Budget | **Anomalien:** 4

### 8. Jonathan Williams — `chars/Archetypen/Archetyp_Rippers_Jonathan-Williams_A.json`
- **Rang:** Fortgeschritten (Aufstiege: 0/4) | **Volk:** Mensch
- **Attribute:** GES W8, VER W6, STR W8, KON W6, WIL W6
- **Handicaps:** Ehrenkodex, Eiferer, Missionar_leicht
- **Talente:** Wolfsjäger, Kampfreflexe, Schnelles Ausweichen, Lied des Heiligen Georg, Gerechter Zorn
- **HP:** 0/4 | **Vermögen:** 58 £
- **DIFF:** 2 Budget | **Anomalien:** 1

### 9. Die Suffragette — `chars/Archetypen/Archetyp_Rippers_Die-Suffragette_A.json`
- **Rang:** Fortgeschritten (Aufstiege: 0/4) | **Volk:** Mensch
- **Attribute:** GES W10, VER W6, STR W6, KON W6, WIL W6
- **Handicaps:** Eitel, Impulsiv, Selbstjustiz
- **Talente:** Akrobat, Kampfakrobat, Flink, Erstschlag, Parkour
- **HP:** 0/4 | **Vermögen:** 0 £
- **DIFF:** [] ✓ | **Anomalien:** 2 (Notizen)

### 10. Der Yankee — `chars/Archetypen/Archetyp_Rippers_Der-Yankee_A.json`
- **Rang:** Anfänger (Aufstiege: 1/4) | **Volk:** Mensch
- **Attribute:** GES W8, VER W8, STR W6, KON W6, WIL W6
- **Handicaps:** Arrogant, Eitel, Missionar_leicht
- **Talente:** Bastler, McGyver, Tarnidentität, Kampfreflexe
- **HP:** 0/4 | **Vermögen:** 0 £
- **DIFF:** [] ✓ | **Anomalien:** 4 (Notizen)

### 11. Vater McBain — `chars/Archetypen/Archetyp_Rippers_Vater-McBain_A.json`
- **Rang:** Anfänger (Aufstiege: 1/4) | **Volk:** Mensch
- **Attribute:** GES W6, VER W6, STR W6, KON W6, WIL W8
- **Handicaps:** Ehrenkodex, Pflichtbewusst_leicht, Schwur_leicht, Verpflichtung_schwer
- **Talente:** Anführer, AH (Priester), Auserwählter, Heiliger/Unheiliger Krieger, Lied des Heiligen Georg
- **Mächte:** Heilung, Schutz, Linderung, Bannung, Geistersicht
- **HP:** 0/4 | **Vermögen:** 400 £
- **DIFF:** 4 Budget | **Anomalien:** 1

### 12. Tara LaGrange — `chars/Archetypen/Archetyp_Rippers_Tara-LaGrange_A.json`
- **Rang:** Fortgeschritten (Aufstiege: 0/4) | **Volk:** Mensch
- **Attribute:** GES W8, VER W6, STR W8, KON W6, WIL W4
- **Handicaps:** Missionar_leicht, Pflichtbewusst_leicht, Verpflichtung_leicht
- **Talente:** Anführer, Kampfreflexe, Ausweichen, Schnelles Ausweichen, Wolfsjäger
- **HP:** 1/3 | **Vermögen:** 0 £
- **DIFF:** 4 Budget | **Anomalien:** 4

### 13. Dr. Jack — `chars/Archetypen/Archetyp_Rippers_Dr-Jack_A.json`
- **Rang:** Fortgeschritten (Aufstiege: 0/4) | **Volk:** Mensch
- **Attribute:** GES W6, VER W10, STR W6, KON W6, WIL W6
- **Handicaps:** Arrogant, Selbstjustiz
- **Talente:** AH (Magie), Rippertech, McGyver, Bastler, Arkaner Drogist
- **Mächte:** Elementarmanipulation, Heilung, Linderung
- **HP:** 0/4 | **Vermögen:** 0 £
- **DIFF:** 11 Budget | **Anomalien:** 11
