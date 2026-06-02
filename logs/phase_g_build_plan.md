# Phase G — Build-Plan für 24 neue SciFi-Archetypen

**Stand:** 2026-06-01
**Quelle:** `Texte/Science_Fiction_Companion_Archetypes_(SWADE).pdf` (1269 Zeilen, 36 Archetypen, 24 NEU)
**Status:** PLAN — noch NICHT ausgeführt, wartet auf nächste Session
**User-Entscheidungen (2026-06-01):**
- Strategie: **Stufenweise mit Review** (Stufe 1 → 2 → 3a → 3b → 3c → 4 → 5)
- Handicaps: **Alle 5 hinzufügen** (Mean, Clueless, Death Wish, Anemic, Holografische Kraftprojektion)
- Völker: **2 komplett neue Völker** (Kybernetische Soldaten, Aquatische Spezies)
- Tempo: **Stufe 1 zuerst** (~30 min), dann Review-Pause

## Quellenlage

- **English `Science_Fiction_Companion_Archetypes_(SWADE).pdf`**: 36 Archetypen (alle RANK: SEASONED)
- **12 davon bereits gebaut** (Phase A-E): Commander, Psyker, Surveyor, Ambassador, Hacker, Infiltrator, Influencer, Mercenary, Roughneck, Mystic, Morpher, Spacer
- **24 NEUE** zu übersetzen und zu bauen: AI Controller, Analyst, Bounty Hunter, Chronomancer, Commando, Cyborg, Enforcer, Engineer, Envoy, Gladiator, Gravlock, Grunt, Hardlight Conjurer, Medic, Pilot, Road Warrior, Scavenger, Scrapper, Shepherd, Smuggler, Squad Leader, Star Knight, Technomancer, Warper
- **Source-Files (extrahiert)**: `/tmp/sfc_archetypes.txt` (1269 Zeilen), pro-Archetyp: `/tmp/sfc_archs/*.txt`

## Komplexitäts-Matrix der 24 Archetypen

| Char | Attr (Agi/Vig) | Skills | Edges | Hind | Ancestry? | Powers? |
|------|---------------|--------|-------|------|-----------|---------|
| AI Controller | d8/d6 | 11 | 3 | 2 | – | – |
| Analyst | d6/d6 | 11 | 4 | 2 | – | – |
| Bounty Hunter | d8/d8 | 12 | 4 | 2 | – | – |
| Chronomancer | d6/d6 | 10 | 5 | 3 | – | ✓ (3 P. / 15 PP) |
| Commando | d6/d10 | 11 | 4 | 2 | ✓ Insektoid | – |
| Cyborg | d8/d6 | 11 | 4 | 2 | ✓ Gen-Soldat | – |
| Enforcer | d8/d10 | 9 | 1 | 3 | ✓ Roboter | – |
| Engineer | d6/d6 | 11 | 4 | 2 | – | – |
| Envoy | d8/d8 | 11 | 3 | 3 | ✓ Vierarmige | – |
| Gladiator | d6/d10 | 12 | 4 | 3 | ✓ Draken | – |
| Gravlock | d8/d6 | 10 | 6 | 3 | – | ✓ (4 P. / 10 PP) |
| Grunt | d8/d8 | 11 | 4 | 3 | – | – |
| Hardlight Conjurer | d6/d6 | 11 | 6 | 4 | – | ✓ (7 P. / 15 PP) |
| Medic | d6/d6 | 11 | 4 | 3 | – | – |
| Pilot | d10/d6 | 11 | 3 | 3 | – | – |
| Road Warrior | d8/d6 | 10 | 5 | 3 | – | – |
| Scavenger | d6/d6 | 12 | 6 | 4 | – | – |
| Scrapper | d6/d12 | 9 | 4 | 3 | ✓ Elementare | – |
| Shepherd | d6/d8 | 11 | 4 | 4 | – | ✓ (3 P. / 10 PP) |
| Smuggler | d8/d6 | 12 | 5 | 2 | – | – |
| Squad Leader | d8/d8 | 10 | 4 | 3 | – | – |
| Star Knight | d8/d6 | 9 | 5 | 4 | ✓ Vierarmige | ✓ (3 P. / 10 PP) |
| Technomancer | d6/d6 | 10 | 5 | 3 | ✓ (Aquatic) | ✓ (3 P. / 10 PP) |
| Warper | d8/d6 | 11 | 5 | 2 | – | ✓ (3 P. / 10 PP) |

## Setting-Lücken (26 Einträge)

### A) 4 Edges fehlen im SciFi-Setting

| Edge (EN) | DE-Name (Vorschlag) | Kategorie | Rang | Voraussetzung |
|-----------|---------------------|-----------|------|---------------|
| Bolster | `Ermutigen (Bolster)` | Sozial | A | Geisteswissenschaften W8 |
| Breaker | `Zertrümmerer` (universell) | Experte | V | – |
| Frenzy | `Raserei` | Kampf | A | Berserker |
| Common Bond | `Gemeinsames Band` | Sozial | A | Willenskraft W8 |

### B) 5 Handicaps fehlen im SciFi-Setting

| Handicap (EN) | DE-Name | Schwere | Beschreibung |
|---------------|---------|---------|--------------|
| Mean | `Gemein` | leicht | -1 auf Überreden |
| Clueless | `Wissenslücke` | leicht | -1 auf Allgemeinwissen & Wahrnehmung |
| Death Wish | `Todeswunsch` | schwer (2HP) | Sucht epischen Tod |
| Anemic | `Blutarm` | leicht | -1 auf Konstitutionsproben |
| Holografische Kraftprojektion | `Holografische Kraftprojektion` | leicht | Hologramm, anfällig für EMP |

### C) 14 Items fehlen im SciFi-Setting

| Item (EN) | DE-Name | Kategorie | Gewicht | Kosten | Quelle (SciFi-Kompendium.txt) |
|-----------|---------|-----------|---------|--------|-------------------------------|
| Body Armor | `Körperpanzerung +4` | Rüstung | 2 | ₡200 | Z.2551 |
| Combat Spacesuit | `Raumanzug, Kampf-` | Rüstung | 10 | ₡5.000 | Z.2574 |
| Infantry Battlesuit | `Infanterie-Kampfanzug +6` | Rüstung | 6 | ₡800 | Z.2547 (bereits als `Infanteriekampfanzug`) |
| Battle Helmet | `Infanterie-Kampfanzugshelm +6` | Rüstung | 1 | ₡100 | Z.2549 |
| Gravity Harness | `Schwerkraftharnisch` | Ausrüstung | 2 | ₡500 | Z.2158 |
| Gyrojet Pistol | `Gyrojet-Pistole` | Waffe (Fern) | 1,5 | ₡400 | Z.3230 |
| Gyrojet Rifle | `Gyrojet-Gewehr` | Waffe (Fern) | 3 | ₡600 | Z.3232 |
| Holy Symbol | `Heiligtum` | Ausrüstung | 0,5 | ₡50 | – (Setting-Item) |
| Stun Grenade | `Betäubungsgranate` | Ausrüstung | 0,25 | ₡50 | – (Standard-Granate) |
| Smoke Grenade | `Rauchgranate` | Ausrüstung | 0,25 | ₡50 | – (Standard-Granate) |
| Beehive Grenade | `Bienenstock-Granate` | Ausrüstung | 0,25 | ₡50 | Z.3205 |
| Personal Data Device | `Persönliche Datenassistenz` | Ausrüstung | 0,5 | ₡500 | Z.2204 |
| Universal Battery | `Universalbatterie` | Ausrüstung | 0,5 | ₡50 | Z.2138 (bereits als `Batterie, Universal-`) |
| Vibro Blade | `Vibro-Klinge` | Waffe (Nah) | 0,5 | ₡525 | Z.3053 |
| Vibro Sword | `Vibro-Schwert` | Waffe (Nah) | 1,5 | ₡600 | Z.3054 |
| Missile Launcher | `Mikro-Flugkörperwerfer` | Waffe (Fern) | 2,5 | ₡1.000 | Z.3179, 3192 |

### D) 2 NEUE Völker

#### Kybernetische Soldaten (Cyborg-Soldat)
- **Handicaps:** Skrupellos, Low G Worlder
- **Talente:** Kampfreflexe
- **Besonderheiten:** Flight (Pace 12), Low G Worlder (-1 Stärke), Reduced Pace (Laufwürfel W4), Schmerzresistenz, Robustheit +1
- **Effekte:** flight=True, low_g_worlder=True, reduced_pace=True, schmerzresistenz=True, robustheit_bonus=1

#### Aquatische Spezies
- **Handicaps:** Dependency
- **Talente:** –
- **Besonderheiten:** Aquatic (kann nicht ertrinken, Pace 6 im Wasser), Dependency (1h/Tag im Wasser), Low Light Vision, Toughness +1
- **Effekte:** aquatic=True, dependency=True, low_light_vision=True, robustheit_bonus=1

### E) 2 bestehende Völker erweitern

#### Roboter (für Enforcer)
- Erweitere `besonderheiten` um "Keine Kernfertigkeiten: Überreden und Heimlichkeit sind keine Kernfertigkeiten"
- Ändere Programmed von leicht zu schwer (Bogen: Programmed schwer)

#### Insektoide (für Commando)
- Füge `wahlmoeglichkeiten.outsider_statt_trennungsangst: True` hinzu
- Bogen-Communo hat Outsider, Insektoide-Default hat Trennungsangst → Wahlmöglichkeit

## Archetype-Mapping (DE Edge/Skill)

### Skills (alle 30 vorhanden im SciFi-Setting)
Athletics→Athletik, Academics→Geisteswissenschaften, Battle→Kriegskunst, Com. Knowledge→Allgemeinwissen, Driving→Fahren, Electronics→Elektronik, Faith→Glaube, Fighting→Kämpfen, Focus→Fokus, Gambling→Glücksspiel, Hacking→Hacken, Healing→Heilen, Intimidation→Einschüchtern, Notice→Wahrnehmung, Occult→Okkultismus, Performance→Darbietung, Persuasion→Überreden, Piloting→Pilot, Psionics→Psionik, Repair→Reparieren, Research→Recherche, Science→Naturwissenschaften, Shooting→Schießen, Stealth→Heimlichkeit, Survival→Überleben, Taunt→Provozieren, Thievery→Diebeskunst, Weird Science→Verrückte Wissenschaft

### Edges (45 von 49 vorhanden, 4 fehlen)
- ✓ Ace→Ass am Steuer, Alertness→Aufmerksamkeit, Assassin→Assassine, Atmospheric Acclimation→Atmosphärische Anpassung, Berserk→Berserker, Block→Block, Brave→Mutig, Brawler→Raufbold, Brawny→Kräftig, Calculating→Berechnend, Command→Anführer, Combat Reflexes→Kampfreflexe, Common Bond→FEHLT, Cyborg→Cyborg, Drones→Drohnen, Duct Tape & Bubble Gum→Panzertape & Kaugummi, Elan→Elan, Exo Scientist→Exo-Wissenschaftler, Fleet-Footed→Flink, Geared Up→Gut Ausgerüstet, Gravitic Acclimation→Gravitationsanpassung, Investigator→Ermittler, Iron Jaw→Eisenkiefer, Jack-of-all-Trades→Alleskönner, Lifter→Heber, Luck→Glück, Marksman→Meisterschütze, McGyver→McGyver, Mr. Fix It→McGyver, New Powers→Neue Mächte, Power Points→Machtpunkte, Quick→Schnell, Quick Draw→Schnell Ziehen, Rearrange Time→Zeit Umordnen, Rock and Roll!→Volles Rohr!, Scavenger→Sammler, Soldier→Soldat, Steady Hands→Ruhige Hände, Streetwise→Gassenwissen, Thief→Dieb, Trademark Weapon→Lieblingswaffe, Trick Shot→Trickschuss, Two-Fisted→Beidhändig, Woodsman→Naturbursche
- ✗ Bolster, Breaker (Brecher = Techomancer-only), Common Bond, Frenzy

### Arcane Backgrounds (alle 7 vorhanden)
AH (Chronomant), AH (Gravitationshexer), AH (Hartlichtformer), AH (Hirte), AH (Sternenritter), AH (Technomancer), AH (Wandler)

### Handicaps (Mapping der 24 Archetypen)
Heroic→Heldenhaft, Loyal→Loyal, Vow (Major)→Schwur_schwer, Big Mouth→Große Klappe, Ailment (Minor)→Totkrank (leicht), Amorous→Amourös, Anemic→Blutarm (FEHLT), Arrogant→Arrogant, Bloodthirsty→Blutrünstig, Clueless→Wissenslücke (FEHLT), Code of Honor→Ehrenkodex, Curious→Neugierig, Death Wish→Todeswunsch (FEHLT), Elderly→Alt, Greedy (Major)→Gierig_schwer, Heroic→Heldenhaft, Holographic force projection→Holografische Kraftprojektion (FEHLT), Jealous (Minor)→Eifersüchtig, Low G Worlder→Niedergravitations-/Schwerelosigkeitsweltler, Low Tech→Low Tech (leicht), Loyal→Loyal, Mean→Gemein (FEHLT), Mild Mannered→Sanftmütig, Overconfident→Übermütig, Quirk→Tick, Rebellious→Rebellisch, Selfless (Minor)→Aufopferungsvoll (leicht), Small→Klein, Suspicious→Misstrauisch_leicht

## 5-stufiger Ausführungsplan

### Stufe 1: Setting-Lücken füllen (30 min, 26 Einträge)
**Datei: `settings/SciFi Kompendium.json`**
- 4 Edges hinzufügen (siehe Sektion A oben)
- 5 Handicaps hinzufügen (siehe Sektion B oben)
- 14 Items hinzufügen (siehe Sektion C oben)
- 2 neue Völker hinzufügen (siehe Sektion D oben)
- 2 Völker-Erweiterungen (Roboter, Insektoide, siehe Sektion E oben)
- **Helfer-Script:** `logs/_add_scifi_phase_g_items.py` (analog zu `logs/_add_scifi_items.py`)
- **Validierung:** `python -c "import json; json.load(open('settings/SciFi Kompendium.json'))"`
- **Header-Update:** `logs/archetypen_anomalie_bericht.md` mit "Phase G Stufe 1 — 26 Setting-Erweiterungen"

### Stufe 2: Build-Script-Gerüst (1 h)
**Neue Datei: `logs/build_sfc_phase_g.py`**
- Pattern analog zu `build_scifi_batch1.py` und `build_scifi_batch2.py`
- Helfer: `_set_standard_session()`, `_set_volkauswahl()`, `_set_archetype_attrs()`
- Pro Archetyp-Sektion: G1 (12), G2 (6), G3 (6)
- Output-Format: pro Char `logs/sfc_<char>_bericht.json` + `logs/sfc_<char>.json`

### Stufe 3a: Batch G1 — 12 Chars ohne Magic/Ancestry (1-2 h)
**Chars:** AI Controller, Analyst, Bounty Hunter, Engineer, Grunt, Medic, Pilot, Road Warrior, Scavenger, Smuggler, Squad Leader, Enforcer
- Muster wie `build_scifi_batch1.py`
- `validiere(s, 4.0)` am Ende für SEASONED
- Pro Char: `logs/sfc_<char>_bericht.json` + `logs/sfc_<char>.json`
- **REVIEW-PUNKT** nach dieser Stufe

### Stufe 3b: Batch G2 — 6 Magic Chars (1-2 h)
**Chars:** Chronomancer, Gravlock, Hardlight Conjurer, Shepherd, Warper, Star Knight
- AH + 3-7 Mächte + PP-Tracking
- `validiere(s, 4.0)` am Ende
- **REVIEW-PUNKT** nach dieser Stufe

### Stufe 3c: Batch G3 — 6 Ancestry Chars (1-2 h)
**Chars:** Commando, Cyborg, Envoy, Gladiator, Scrapper, Technomancer
- Volk + Ancestry-Besonderheiten
- `validiere(s, 4.0)` am Ende

### Stufe 4: Anomalie-Bericht aktualisieren (30 min)
**Datei: `logs/archetypen_anomalie_bericht.md`**
- Header: "Stand: 2026-06-01 (Update: Phase G – 24 neue SciFi-Archetypen aus SWADE English)"
- Neue Sektion "## Phase G – 24 neue SciFi-Archetypen (Science Fiction Companion SWADE)"
- Pro Char: ✓/⚠/✗ Status + Anomalien + MISSING-Items

### Stufe 5: Verifikation & Regressions-Tests (15 min)
- `python "test units/run_all_tests.py"` — alle bisherigen Tests grün
- Total-Anomalien-Check: 92 (Phase E) + X (Phase G) — Schwellwert < 150 als Erfolg
- Falls Regression: `git checkout` auf vorherigen Commit

## Wichtige Referenzen (für nächste Session)

### Source-Files
- `/tmp/sfc_archetypes.txt` — 1269 Zeilen, alle 36 Archetypen extrahiert
- `/tmp/sfc_archs/*.txt` — 36 per-Archetyp-Source-Files
- `Texte/Science_Fiction_Companion_Archetypes_(SWADE).pdf` — English Original
- `Texte/SciFi-Kompendium.txt` — Deutsche Quelle (21.506 Zeilen)
- `Texte/SciFi Kompendium Archetypen.txt` — 12 Deutsche Archetypen (bereits gebaut)

### Hilfs-Scripts
- `logs/_add_scifi_items.py` — Vorlage für Stufe-1-Helfer (Phase C Pattern)
- `logs/build_scifi_batch1.py` + `build_scifi_batch2.py` — Vorlagen für Phase 3 Builds
- `logs/archetypen_anomalie_bericht.md` — Anomalie-Bericht (Header update + neue Sektion)

### Code-Pfade
- `models/wuerfel.py:46-74` — `increase()` d4-2→d4+0
- `functions/eigenschaften_funktionen.py:296-302, 481-484` — `fertigkeit()` skip-Logik
- `functions/talent_funktionen.py:1148-1149` — **BUG `_waehle_mit_aufstieg` (Phase F)**
- `.claude/skills/archetyp-erstellen/driver.py:560-577` — FIXED `fertigkeit_mit_aufstieg`
- `.claude/skills/archetyp-erstellen/SKILL.md` — Skill-Workflow

### Run-Befehle
```bash
# Run app
python main.py

# Run all tests
python "test units/run_all_tests.py"

# Run single test module
python -m pytest "test units/test_theme_handler.py"

# Build Linux binary
python build_linux.py

# Build Windows binary
python build_windows.py
```

## Erwartete Stats nach Phase G

- **Talente:** 204 → 208 (+4)
- **Handicaps:** 95 → 100 (+5)
- **Items:** 272 → 286 (+14)
- **Völker:** 18 → 20 (+2, +2 erweitert)
- **Archetypen total:** 65 → 89 (24 neue SciFi-Charaktere)
- **Geschätzte Anomalien:** 92 (alt) + ~120 (Phase G) = ~210 (Schwellwert < 250 als Erfolg)

## Nächste Session — Schritt 1.1

Wenn die neue Session startet, **erstes Ziel**:

1. **Setting-Lücken-Helfer-Script erstellen:** `logs/_add_scifi_phase_g_items.py`
   - Lade `settings/SciFi Kompendium.json`
   - Füge 4 Edges, 5 Handicaps, 14 Items, 2 Völker, 2 Völker-Erweiterungen hinzu
   - Speichere JSON
   - Validiere mit `json.load()`
2. **Stichproben-Test:** Führe `python logs/build_scifi_batch2.py` aus → keine Regression
3. **Anomalie-Bericht-Header aktualisieren:** "Stand: 2026-06-01 (Update: Phase G Stufe 1)"

Bei Erfolg → Review-Pause → Stufe 2 (Build-Script-Gerüst).
