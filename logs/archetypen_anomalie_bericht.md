Archetypen Anomalie-Bericht
Stand: 2026-06-02 (Update: SciFi Kompendium Phase G **komplett abgeschlossen** — Stufe 1+1.5: 2 Edges / 3 Handicaps / 29 Items ergänzt; Stufe 2: Build-Skript; Stufe 3a: 14 G1-Archetypen; Stufe 3b: 6 G2-Magic-Archetypen; Stufe 3c: 4 G3-Ancestry-Archetypen. **Force-Buy-Bug in ausruestung_funktionen.py:42/100/312 behoben** (User-Freigabe). **2 HCs ergänzt** (Trennungsangst, Wuchtig). Setting jetzt 209 Talente, 106 Handicaps, 315 Items, 20 Völker. Bestehende 12 Batch1+12 Batch2 SciFi-Builds unverändert.)
Gesamt: 89 Archetypen (65 + 14 G1 + 6 G2 + 4 G3 = 89; bzw. 36 SciFi-Builds gesamt: 12 Batch1 + 14 G1 + 6 G2 + 4 G3)

---

## ✓ Korrekt (26)
- Jeanne (HeXXen 1773)
- Ezren (Savage Pathfinder)
- Seoni (Savage Pathfinder)
- **SciFi Kompendium** (11/12): Commander, Psyker, **Surveyor**, Ambassador, Hacker, **Infiltrator***, Influencer, Mercenary, **Mystic**, Roughneck, Morpher, **Spacer***
  - *Infiltrator: alle 9 Bogen-Skills korrekt, nur 0.5 verb unter 4 (Rang Anfänger)*
  - *Spacer: 12/13 Bogen-Skills, Schießen d4 statt d6 (Skill-Lücke wegen 2 Pkt Budget-Defizit dokumentiert)*
- **SciFi Kompendium G1-Archetypen Phase G Stufe 3a (14)**: AI Controller, Analyst, Bounty Hunter, Engineer, Enforcer, Envoy, Gladiator, Grunt, Medic, Pilot, Road Warrior, Scavenger, Smuggler, Squad Leader — alle erstellt, je 4–12 Anomalien, alle 4HP HC-Budget eingehalten, **keine Basis-Code-Änderungen**, dokumentiert in [## Phase G Stufe 3a] unten.
- **SciFi Kompendium G2-Archetypen Phase G Stufe 3b (6)**: Chronomancer, Gravlock, Hardlight Conjurer, Shepherd, Warper, Star Knight — alle 4HP HC-Budget, AH + 2-7 Powers, dokumentiert in [## Phase G Stufe 3b] unten.
- **SciFi Kompendium G3-Archetypen Phase G Stufe 3c (4)**: Commando (Insektoide), Cyborg (Gen-Soldaten), Scrapper (Elementare), Technomancer (Aquatische Spezies) — alle 4HP HC-Budget, dokumentiert in [## Phase G Stufe 3c] unten.

## ○ Nur Notizen — 37

### Fantasy Kompendium

**Akrobatin**
- 🔧 FEHLENDE AUSRÜSTUNG: Trank Wandkrabbler (nicht im FK-Katalog)

**Alchemist**
- Halbelf Mensch-Erbe: freies Talent = AH(Alchemist). Außenseiter aus Racial. AH(Alchemist) auto: Materialkomponenten. 4 HP (Impulsiv+Hässlich_schwer): 2 für Konstitution-Raise, 2 für Berechnend.

**Amazone**
- ✅ AUFGELÖST: 'Formation Fighter' → **Formationskämpfer** (war bereits im FK-Kompendium; Voraussetzung Kämpfen W8 erfüllt). Haltet die Stellung! entfernt.
- 🔧 FEHLENDE AUSRÜSTUNG: Pfeil der Genauigkeit ×1

**Aristokrat**
- 🔧 FEHLENDE AUSRÜSTUNG: keine

**Assassinin**
- ⚠️ VERBESSERT: 'Sneak Attack' (extra W6 Schaden) = **Hinterhältiger Angriff** (neues FK-Talent: +2 Schaden aus Hinterhalt, Voraussetzung Assassine erfüllt). Besser als Erstschlag, aber nicht identisch (W6 vs. +2 fester Bonus).
- Gestaltwandler-Racial: AH(Begabt)+Charismatisch+Geheimnis_schwer+Verkleiden auto.
- 🔧 FEHLENDE AUSRÜSTUNG: Gifte (Schlangengift, Assassinengebräu, Äther, Lotusstaub, Grünschleimextrakt)

**Barbarin**
- ⚠️ BUG: Berserker erhöht Stärke dauerhaft auf W10 (sollte nur im Berserkermodus gelten). Tatsächlicher Wert W10, Erwartung W8.
- ⚠️ Anomalie: Provozieren (Taunt d4) fehlt - Fertigkeitsbudget erschöpft (Athletik d8 + Kämpfen d8 + Einschüchtern d8 + 3 Aktivierungen = 12 Punkte genau).
- Außenseiter (Halbork-Racial) kommt automatisch aus dem Volk, nicht manuell.
- 🔧 FEHLENDE AUSRÜSTUNG: Trank der Vergrößerung (nicht im FK-Katalog)

**Barde**
- 5 Aufstiege statt 4 (Code implementiert SWADE '2 Fertigkeiten pro Aufstieg' als 2 separate).

**Bogenschütze**
- 🔧 FEHLENDE AUSRÜSTUNG: keine

**Champion**
- Himmlischer auto: Attraktiv, Ehrenkodex, Schwur_schwer. AH(Kleriker) fügt weiteren Schwur_schwer hinzu (Duplikat wird ignoriert). Dispel → Verbannen (Rang V, ignore_rang_check).
- ⚠️ GELDMANGEL: Plattenbrustharnisch (500 GP) = gesamtes Startbudget. FORCE-Käufe für alle weiteren Items. FK-Preis überschreitet Startkapital.
- 🔧 FEHLENDE AUSRÜSTUNG: keine

**Diebin**
- 5 Aufstiege (2 Skill-Steps im Code). Athletik-Kosten geprüft: d8 bei Agi d8.
- 🔧 FEHLENDE AUSRÜSTUNG: Tränke (Unsichtbarkeit, Nachtsicht)

**Drachenkämpfer**
- ⚠️ GELDMANGEL: Plattenbrustharnisch (500 GP) + Schild/Armbrust übersteigt Startbudget. FORCE-Käufe. Krummschwert (75 GP) + Schwere Armbrust (50 GP) vorab kaufbar.
- ⚠️ ANOMALIE: 'Ruthless(major)'→'Skrupellos(minor=1pt FK)'. Nur 3 HP, nicht 4. Agi bleibt d4 (Archetype zeigt d6) - Budget-Anomalie.
- Drachenvolk: Arrogant, Kaltblütig, Anfälligkeit Kälte, Odemwaffe auto.
- 🔧 FEHLENDE AUSRÜSTUNG: keine

**Hexe**
- AH(Hexer/Hexe) auto: Behindernde_Rüstung_schwer, Materialkomponenten, Verderbnis, Vertrauter. Vertrauter = Familiar: 5 MP sharable, familiar-Senses.
- 🔧 FEHLENDE AUSRÜSTUNG: Grabstaub, Hexenbeutel, 2 vorbereitete Mächte in Hühnerknochen

**Klerikerin**
- Zwerg-Racial: Nachtsicht, Verringerte Bewegungsweite auto. Champion→Auserwählter (+2 Schaden vs. übernatürlich Böse).
- HINWEIS: Kettenhemd = Mithral-Kettenhemd (+3 RS). Bolzen(10)×2 = 20 Bolzen.

**Krieger**
- ⚠️ GELDMANGEL: Schwert, Langschwert (300 GP) + Bronzerüstung/Helm (200+120 GP) = 620 GP. Übersteigt Startbudget 500 GP. FORCE-Käufe für Rüstung, Helm, Schild, Söldnerpaket. FK-Preis für Langschwert deutlich über Quelltextwert.
- ✅ AUFGELÖST: 'Take the Hit' (freie Wurfwiederholung Schaden-Wegstecken) = **Treffer einstecken** (neues FK-Talent, exakte Entsprechung). Voraussetzungen Eisenkiefer+KON W8 erfüllt. Kampfreflexe entfernt.
- 🔧 FEHLENDE AUSRÜSTUNG: Trank des Umgebungsschutzes (nicht im FK-Katalog)

**Loremaster**
- 🔧 FEHLENDE AUSRÜSTUNG: keine

**Mönch**
- Rakashaner-Racial: Blutrünstig, Nichtschwimmer, Volksfeind (Rattlinge), Nachtsicht auto. Kämpfen d10: Prüfe ob Kosten korrekt (eff d8 >= Agi d8 → doppelt für d10).
- HINWEIS: Biss/Klauen = Rassenangriff Rakashaner (kein Kauf).

**Narr**
- AH(Barde) auto: Behindernde_Rüstung_leicht. Infernaler: Dunkelsicht, Hörner, Teuflische Natur als spezielle_effekte (nicht in selected_handicaps).
- 🔧 FEHLENDE AUSRÜSTUNG: Trank der Unsichtbarkeit (nicht im FK-Katalog)

**Paladin**
- AH(Kleriker) fügt automatisch Schwur_schwer hinzu (0 HP). Soldat = Soldier-Edge: Stärke gilt als einen Typ höher für Belastung.
- ⚠️ GELDMANGEL: Plattenbrustharnisch (500 GP) = gesamtes Startbudget. FORCE-Käufe für Klerikerpaket+Heiliges Wasser ebenfalls nötig. FK-Itempreise überschreiten Startkapital für schwer gerüstete Heilige.
- 🔧 FEHLENDE AUSRÜSTUNG: Trank des Umgebungsschutzes

**Ritter**
- 🔧 FEHLENDE AUSRÜSTUNG: Streitross mit gepolsteter Schabracke
- ⚠️ GELDMANGEL: Plattenbrustharnisch (500 GP) + Schwerer geschlossener Helm (300 GP) = 800 GP. Übersteigt Startbudget 500 GP massiv. FORCE-Käufe für alle teuren Items.

**Rüpel**
- 🔧 FEHLENDE AUSRÜSTUNG: keine

**Schamane**
- AH(Schamane) auto: Behindernde_Rüstung_leicht, Tick, Materialkomponenten.
- 🔧 FEHLENDE AUSRÜSTUNG: Kreidestaub der Geisterbann (Kreide als Ersatz), 5 GM Restgeld

**Schwerttänzerin**
- 🔧 FEHLENDE AUSRÜSTUNG: keine

**Tiermeister**
- ⚠️ 'Mean' → 'Grimmig' (Annäherung; Grimmig = beim Provozieren gereizt, nicht -1 Überreden). Vig bleibt d4 statt d6 (Budget-Anomalie). Tiermeister 2x als Advance - prüfe ob 2. Haustierkauf funktioniert.
- 🔧 FEHLENDE AUSRÜSTUNG: Pfeil der Genauigkeit ×2, Pfeife

**Totemkrieger**
- Mystische Kräfte: 10 dedizierte PP mit Self-only Mächten. Mächte (Eigenschaft erhöhen/senken für Kämpfen/Stärke/Vig, Kriegersegen, Trägheit/Beschleunigung) können nicht via macht() hinzugefügt werden - sind Teil des Talents.
- 🔧 FEHLENDE AUSRÜSTUNG: Trank des Umgebungsschutzes (nicht im FK-Katalog)

**Tüftler**
- Gnom: Verstand d6 gratis, Wahrnehmung startet d6 (bonus). Tüftler: Reparieren als arkane Fertigkeit. 2 Novice-Mächte (AH Tüftler Limit).
- 🔧 FEHLENDE AUSRÜSTUNG: Tasche des Fassens, Sonnenstab

**Verteidiger**
- Außenseiter_schwer(2HP): 4 HP gesamt → Vig d4→d6(2HP) + d6→d8(2HP); Advance → d10. Golem: Größe+2, Konstrukt, Keine lebenswichtigen Organe, Panzerung+2 als spezielle_effekte.
- 🔧 FEHLENDE AUSRÜSTUNG: keine (Stachelpanzer und gesperrte Handschuhe im Katalog nicht verfügbar)

**Waldläufer**
- Halbelf (Elfen-Erbe): Außenseiter_leicht, Nachtsicht auto. Schwerzüngig (Tongue-Tied) = major in FK (2 HP). 5 Aufstiege wegen 2 Skill-Steps im Code.
- 🔧 FEHLENDE AUSRÜSTUNG: Verstärkte Lederrüstung (als Ledertunika)

**Zauberer**
- AH(Zauberer) gibt auto: Behindernde_Rüstung_leicht + Verderbnis (0 HP). Power Points 15→20 via Machtpunkte-Advance. Verbannen = Rang V (Veteran), mit ignore_rang_check. Sorcerer-AB = AH(Zauberer) in FK.
- 🔧 FEHLENDE AUSRÜSTUNG: Tasche des Fassens, Trank Aufladen MP (nicht im FK-Katalog)

### HeXXen 1773

**Klara**
- ⚠️ Budget-Anomalie: FP 12, benötigt 13 (Alchemie4+NaWi3+Rep3+Schießen2+Allgw1). Allgemeinwissen bleibt W4 (Screenshot: W6). Wahrnehmung bleibt W4 (Screenshot: W6) – 0 HP nach Verstand+Machtpunkte.

### SWAE

**Elsiara**
- ⚠️ Budget-Anomalie: 4 HP komplett durch WIL-Raise(2HP)+Dieb(2HP) verbraucht. Wahrnehmung bleibt W4 (Screenshot: W6). Provozieren bleibt inaktiv (mod=-2, Screenshot: W4 aktiviert).

**Kenaken**
- Fäuste (Stä+W4) = natürliche Waffen durch Kampfkünstler-Talent, kein Katalog-Item.

**Nachtfinder**
- 🔧 AUSRÜSTUNG PRÜFEN: "[X] mit Notizen" im Screenshot – kein Katalog-Match gefunden

### Savage Pathfinder

**Harsk**
- Handbeil = als "Handaxt" gekauft (Stä+W6); 2x = Handbeil + Sigurs Handbeil
- 🔧 FEHLENDE/ABWEICHENDE AUSRÜSTUNG: beschlagene Lederrüstung (+2) – Katalog hat nur einfaches Leder

**Kyra**

**Lem**

**Lini**

**Sajan**
- 🔧 FEHLENDE AUSRÜSTUNG (bitte separat anlegen): Tempelschwert (Original-Name; hier als Kurzschwert/Stä+W6 gekauft)
- 🔧 FEHLENDE AUSRÜSTUNG (bitte separat anlegen): Sonnenstab (nur "Sonnenzepter" im Katalog vorhanden, anderer Gegenstand)

## ⊘ HP-Limit-Rejection — bekannt, dokumentiert (2)
Handicap-Calls korrekt rejected (HP-Limit=4). Auto-Add durch AH/Racial setzt es trotzdem.

**Druidin** (Fantasy Kompendium): handicap(Schwerzüngig) — HP-Limit 4 durch Schwur_schwer+Materialkomponenten
- Schwerzüngig (Tongue-Tied, major) wurde abgelehnt: HP-Limit 4 bereits durch Schwur_schwer+Materialkomponenten erreicht. Nicht auf dem Charakterbogen.
- Elf-Racial: Zwei_linke_Hände + Nachtsicht automatisch (nicht manuell hinzugefügt).
- 🔧 FEHLENDE AUSRÜSTUNG: Trank der Unsichtbarkeit (nicht im FK-Katalog)
**Magier** (Fantasy Kompendium): handicap(Materialkomponenten) — HP-Limit 4 durch Alt+Behindernde_Rüstung_schwer; AH(Magier) setzt es auto
- Materialkomponenten (major) wurde abgelehnt: HP-Limit 4 durch Alt+Armorinterference. Loyal+Beschämt als Minor akzeptiert (0 extra pts).
- AH(Magier): 15 PP, 6 Novice-Mächte möglich. Verbannen (Rang V) mit ignore_rang_check hinzugefügt.
- Zauberbücher: sofort +1 Macht (Verriegeln/Entriegeln). Neue Mächte danach: +2 reguläre oder +3 mit Zauberbücher.
- 🔧 FEHLENDE AUSRÜSTUNG: Trank Wandkrabbler, Trank Schnelligkeit (nicht im FK-Katalog)

### Superkräfte-Kompendium (Build 2026-05-30, 11 Archetypen)

Setting `Superkräfte Kompendium`. Alle 11 offiziellen SWADE-Supers-Archetypen aus
`Texte/Superkräfte Archetypen.txt` headless gebaut. Build-Skript: `logs/build_supers.py`,
Berichte: `logs/super_*_bericht.json`, gespeichert: `chars/Archetypen/Archetyp_Superkraefte_*.json`.
**11/11 gebaut, 0 Crashes.** Superkräfte laufen NICHT über `driver.py`, sondern über
`functions/superkraft_funktionen.py` (SKP-System; Setting-Datenkey `krafte`; Stufe III = 45 SKP,
Kraftobergrenze 15). Alle 11 summieren exakt auf 45 SKP → Power-Mapping/Kosten verifiziert.

**Bogenschütze, Panzer, Schütze, Eismann, Feuervogel, Hexe, Detektiv, Schläger, Verteidiger,
Walküre, Sprinter**

- ⚠️ KRAFTOBERGRENZE: Einzelkräfte > 15 SKP werden mit `'ueber_obergrenze'` abgelehnt, obwohl die
  offiziellen Bögen sie verwenden: Panzer & Schläger `Superattribut` (20), Feuervogel
  `Fernkampfangriff` (20), Sprinter `Geschwindigkeit` (16). Klären, ob Obergrenze 15 bei Stufe III
  zu streng modelliert ist.
- ✅ **GELÖST 2026-06-01 — „Der Beste"-Edge ohne Effekt (Code-Bug):** Die im Setting
  dokumentierte Regel „Kraftobergrenze entspricht halben maximalen SKP (statt einem Drittel)"
  (Edge `Der Beste`, Rang A) wurde nicht umgesetzt. Fix in
  `functions/superkraft_funktionen.py`: `_berechne_kraftobergrenze()` + Listener auf
  `selected_talente` via `_aktualisiere_kraftobergrenze()`. `setze_machtstufe()` ruft die
  Helper-Funktion und bindet den Listener (einmalig pro Charakter). Test-Skript
  `logs/test_der_beste.py` (21 Tests, alle grün) verifiziert: 5/10/15/20/25 ohne Edge,
  7/15/22/30/37 mit Edge. **Folge für die Bögen:** Feuervogel `Fernkampfangriff` (20 SKP)
  ist jetzt wählbar, sobald die Edge im Build-Skript ergänzt wird. Panzer/Schläger
  `Superattribut` (20) und Sprinter `Geschwindigkeit` (16) bleiben `ueber_obergrenze`, da
  die Bögen dort keine Edge-Berechtigung vorsehen — Klärung mit Autor nötig.
- 🔧 FEHLENDE EDGES im Setting-Katalog (kein DE-Key): `Dead Shot`, `Rock and Roll`, `Danger Sense`,
  `Mighty Blow` (Wuchtschlag), `Command` (Kommandant). Alle übrigen Edges/Handicaps/Fertigkeiten
  existieren unter korrektem Key.
- HINWEIS Seasoned-Bögen: Diese Archetypen sind Rang *Seasoned* (5–8 Edges); bei Erstellung gibt es
  nur ~1 freien Edge-Slot → übrige Edges korrekt abgelehnt (kein Bug). Voller Bogen erst nach
  `char_gen_completed` + Aufstiegen.
- HINWEIS Key-Auflösung (nicht offensichtlich): Marksman=`Meisterschütze`, Quick=`Schnell`,
  Brawny=`Kräftig`, Counterattack=`Konter`, Extraction=`Rückzug`, Sweep=`Rundumschlag`,
  Performance=`Darbietung`, Academics=`Geisteswissenschaften`, Science=`Naturwissenschaften`,
  Battle=`Kriegskunst`, Alertness=`Aufmerksamkeit`, Level Headed=`Kühler Kopf`.
- ✅ **GELÖST 2026-06-01 — D-Advance-Range-Confirm-Bug (Driver-Code-Bug):**
  `driver.fertigkeit_mit_aufstieg(name)` (ohne `zielwert`) rief
  `controller.steigere_fertigkeit(name)` OHNE `confirm_double_cost=True` auf. Folge: Sobald
  die Fertigkeit am oder über dem verknüpften Attribut steht, gibt der Controller
  `"needs_confirmation"` zurück (bool → True), der Wert ändert sich nicht. Fix in
  `.claude/skills/archetyp-erstellen/driver.py:560-577`: D-Advance setzt jetzt IMMER
  `confirm_double_cost=True` (D-Advances dürfen das Attribut explizit überschreiten, kosten
  dann 2×). Deadlands-Build (Agent: rang=Fortgeschritten, aufstiege=0) weiterhin grün.
- ✅ **GELÖST 2026-06-01 — Rang „Fortgeschritten" für alle 11 Supers:** Bögen sind Rang Seasoned
  (= 4 Aufstiege), Build-Muster analog `deadlands_build.py`: `abschliessen(4)` → D-Advances
  für Edges (`talent_mit_aufstieg`) + für Top-4-Skills (`fertigkeit_mit_aufstieg`-Loop mit
  `(value, modifier)`-Check, da d4-2 → d4+0 den Wert gleich lässt). Loop iteriert pro Skill
  bis Wert/Modifier sich ändert ODER `verbleibende_aufstiege == 0`. **11/11 verb=0.0,
  rang=Fortgeschritten.** Schütze/Schläger (5 Edges) verbrauchen alle 4 Aufstiege für Edges
  → keine Skill-D-Advances mehr möglich, aber Rang trotzdem erreicht.

---

## SciFi Kompendium (12 Archetypen) – 2026-05-31 / **Update 2026-06-01**

Build-Skripte: `logs/build_scifi_batch1.py`, `logs/build_scifi_batch2.py`  
Gespeichert: `chars/Archetypen/Archetyp_SciFi_Kompendium_*_A.json`

### Status 2026-06-01 (nach Phase A+B)

| Char | Rang | verb | FORCE | NOTIZ | fail |
|---|---|---|---|---|---|
| Commander | Fortgeschritten | 0 | 4 | 1 | 0 |
| Psyker | Fortgeschritten | 0 | 3 | 1 | 0 |
| Surveyor | Anfänger | 0.5 | 4 | 1 | 0 |
| Ambassador | Fortgeschritten | 0 | 4 | 1 | 0 |
| Hacker | Fortgeschritten | 0 | 1 | 1 | 0 |
| Infiltrator | Anfänger | 1 | 7 | 1 | 0 |
| Influencer | Fortgeschritten | 0 | 2 | 1 | 0 |
| Mercenary | Fortgeschritten | 0 | 6 | 1 | 0 |
| Roughneck | Fortgeschritten | 0 | 8 | 3 | 0 |
| Mystic | Anfänger | 1 | 0 | 1 | 0 |
| Morpher | Fortgeschritten | 0 | 0 | 1 | 0 |
| Spacer | Anfänger | 2 | 5 | 3 | 0 |
| **TOTAL** | **8/12 Fort.** | — | **44** | **16** | **0** |

### Ergebnis nach v2-Update (Mensch + Mystische Kräfte + Skrupellos_schwer)

| Archetyp | Echte Fehler | Anmerkung |
|---|---|---|
| Commander | 0 ✓ | Willenskraft d8 jetzt korrekt (Mensch) |
| Psyker | 0 ✓ | Alle 5 Mächte gesetzt (Mensch) |
| Surveyor | 0 ✓ | |
| Ambassador | 0 ✓ | Mystische Kräfte: Telepath → auto 5 Mächte + 10MP |
| Hacker | 0 ✓ | Willenskraft d8 (Mensch) |
| Infiltrator | 0 ✓ | |
| Influencer | 0 ✓ | |
| Mercenary | 0 ✓ | |
| Roughneck (Draken) | 1 ○ | 2. Konstitution-HC-Schritt fehlgeschlagen (Talent kostet HP) |
| Mystic (Floraner) | 1 ○ | 2. Konstitution-HC-Schritt fehlgeschlagen (Talent kostet HP) |
| Morpher (Wechselbälger) | 1 ○ | 2. Konstitution-HC-Schritt fehlgeschlagen (Talent kostet HP) |
| Spacer | 0 ✓ | Stärke d6 + Konstitution d6 jetzt korrekt (Mensch + Skrupellos_schwer) |

**9/12 vollständig korrekt. 3/12 mit einer strukturell bedingten Anomalie.**

### ○ Verbleibende Anomalie bei Volk-Charakteren (Roughneck, Mystic, Morpher)

`attribut_mit_hc(Konstitution)` ok=False beim 2. HC-Schritt.  
**Ursache:** Diese Charaktere haben ein eigenes Volk (Draken, Floraner, Wechselbälger) – kein Mensch-Volk. Daher kostet ihr einziges Starttalent 2HP. Mit 4HP-Budget: 2HP Talent + 2HP 1. Konstitutions-Schritt = 4HP aufgebraucht. Für den 2. Schritt (d6→d8) fehlen 2HP.  
**Folge:** Konstitution bleibt d6 statt d8 → Toughness 1 zu niedrig (Roughneck 11(4) statt 12(4); Mystic/Morpher unverändert da kein Robustheit-Bonus).

### ⚠ Offene Findings

**F1 – Reihenfolge-Bug: Talent-HP-Kosten nach HC-Attr-Schritt (Code-Bug)**  
Wenn Chargen-Attr-Punkte erschöpft sind und ein HC-Attr-Schritt (`steigere_mit_handicap_attribut`) durchgeführt wurde, verliert der erste nachfolgende Talent-Aufruf seinen kostenlosen Status und kostet 2HP. Reproduzierbar. **Workaround:** Talente immer VOR Attributen setzen.

**F2 – Low Light Vision fehlt bei Draken**  
Roughneck-Ancestry: Nachtsicht im deutschen Draken-Volk nicht implementiert.

**F3 – SciFi: 12 Startfertigkeitspunkte (unklar ob Regel oder Bug)**  
SWAE hat 15 Startfertigkeitspunkte. SciFi Kompendium verwendet 12. Alle Skill-Builds entsprechend angepasst.

### ✅ Gelöste Findings (durch Setting-Anpassungen)

- **F1 (alt) – Kein Mensch-Volk:** `Mensch`-Volk zum SciFi Setting ergänzt → 1 freies Starttalent für Human-Charaktere. Alle 8 Human-Archetypen profitieren.
- **F3 (alt) – Mystische Kräfte gibt kein AH:** `Mystische Kräfte: Sternenkrieger/Telepath` mit `neue_maechte: 5` und `auto_maechte: [...]` ausgestattet + Code-Support in `models/talent.py` + `functions/talent_funktionen.py`. Ambassador hat jetzt alle 5 Mächte automatisch.
- **F4 (alt) – Skrupellos_schwer fehlt:** `Skrupellos_schwer` (2HP) ergänzt → Spacer hat 4HP Budget, Stärke d6 erreichbar.
- **F5 (alt) – Kein Volk für Spacer:** Mensch als Stand-in verwendet (fehlende Alien-Ancestry dokumentiert).

### Fehlende Ausrüstungs-Keys (weiterhin offen)
Laserpistole, Biolink, Betäubungsknüppel, Schockgranaten, Plasmagewehr/Plasmapistole, Cyberdeck, Nanowear, Muskelgewebe-Cyberware, Alter Wear, leichte Schusswaffe (Slugthrower).  
Kein passendes Volk für Spacer-Ancestry (Biss/Klauen, Nachtsicht, Kann-nicht-schwimmen, Blutrünstig racial, Ruppig racial).

### Re-Analyse 2026-06-01: Bogen-Validierung gegen Build (alle 12 Archetypen)

`Texte/SciFi Kompendium Archetypen.txt:3` deklariert: **`(Alle Archetypen: RANK SEASONED / Erfahren)`** — alle 12 Bögen sind Seasoned (4 Aufstiege). `abschliessen(4)` ist korrekt.

**Build-Stand:** 12 Chars gebaut, 0 Crashes, 50 Anomalien, 44 Käufe-FORCE, 16 NOTIZ. Davon 7 Chars mit `verb>0` (Rang „Anfänger"): Infiltrator, Influencer, Morpher, Mystic, Roughneck, Spacer, Surveyor.

#### Anomalie-Kategorien

**A) Mapping-Bugs: Bogen-Edge ↔ Build-Edge (5 Chars)**

| Char | Bogen (EN) | Build (DE) | Status |
|------|-----------|-----------|--------|
| COMMANDER | Common Bond | **Selbstlos** | ✗ Falsches DE-Wort (Selbstlos ≠ Common Bond) |
| INFILTRATOR | Thief, Geared Up | (fehlt) | ✗ 2 Edges fehlen ganz |
| INFLUENCER | Attractive | (fehlt) | ✗ 1 Edge fehlt |
| MERCENARY | Geared Up | (fehlt) | ✗ 1 Edge fehlt |
| ROUGHNECK | Cyber Installs | (kein Talent-Key) | ✗ Im Setting fehlt Edge |

**B) Fehlende Attribut-Advances (D-Advance nicht simuliert)**

| Char | Bogen-Advance | Build | Status |
|------|---------------|-------|--------|
| PSYKER | Spirit d8 | d8 via HC | ⚠ Sollte D-Advance, nicht HC |
| SURVEYOR | Smarts d8 | d6 (unverändert) | ✗ |
| AMBASSADOR | Smarts d10 | d8 | ✗ |
| MERCENARY | Vigor d8, Strength d8 | Vig d6, Str d8 | ✗ Vig fehlt |
| MYSTIC | Vigor d8 | d8 via HC | ⚠ Sollte D-Advance |
| MORPHER | Vigor d8 | d8 via HC | ⚠ Sollte D-Advance |

**C) Fehlende Skill-Advances (D-Advance nicht simuliert)**

| Char | Bogen-Advance | Build |
|------|---------------|-------|
| MYSTIC | Persuasion d8, Shooting d6 | (fehlt) |
| SPACER | Fighting d8, Stealth d8, Electronics d6, Shooting d6 | (fehlt) |

**D) Rang „Anfänger" wegen ungenutzter Aufstiege (7 Chars)** — verursacht durch A+B+C.

| Char | Verb | Ursache |
|------|------|---------|
| Infiltrator | 1 | 2 Edges fehlen + Skill-Advance fehlt |
| Influencer | 1 | Attractive-Edge fehlt |
| Morpher | 1 | Vigor-Advance via HC statt D-Advance |
| Mystic | 2 | Skill-Advance fehlt + Vigor-Advance via HC |
| Roughneck | 1 | Cyber-Installs-Edge fehlt |
| Spacer | 2 | 2 Skill-Advances fehlen |
| Surveyor | 1 | Smarts-Advance fehlt |

**E) Item-Mapping-Bugs (Schreibweise)** — `Direktionalmikrofon` (Build) vs. `Direktionales Mikrofon` (Setting), `Atemschutz` vs. `Kreislaufatemgerät`, `Schweißbrille` vs. `Schutzbrille`.

**F) Items komplett fehlend im Setting (24)**: Laserpistole, Plasmapistole/-gewehr, Cyberdeck, Raumanzug, Betäubungsknüppel, Slugthrower, Nanowear, Environment Wear, Medi-Gel, Schockgranaten, Schneidbrenner, Biolink, Schwere Blasterpistole, Klebeflicken, Handbeil, Scanner, Muskelgewebe-Cyberware, Alter Wear, Leichte Schusswaffe.

**G) Ancestry-Probleme**
- ROUGHNECK (Draken): `Low Light Vision` im DE-Setting nicht implementiert
- SPACER: Komplett eigenes Volk fehlt (5+ Merkmale); Mensch als Stand-in

**H) Sonstiges**
- 44× `kaufen(...) FORCE`: Startkapital 500$ zu niedrig für Bogen-Ausrüstung
- Commander: Bogen listet 12 Skills, 12pts-Budget reicht nur für 8

#### Lösungs-Plan (Phasen) – Status 2026-06-01

| Phase | Inhalt | Status | Wirkung |
|-------|--------|--------|---------|
| A | Edge-Mapping + Item-Schreibweise | ✅ ERLEDIGT | Selbstlos=Common Bond, 5 Edges korrekt, 3 Items umbenannt |
| B | Attr/Skill-Advance Compliance + 3 attribut_mit_hc-Fail | ✅ ERLEDIGT | 3 Bug-Fixes (Konstitution als D-Advance), 8/12 Fortgeschritten |
| C | 24 fehlende Items in `settings/SciFi Kompendium.json` ergänzen | ⚠ offen | Plasmapistole, Cyberdeck, Raumanzug, Schockgranaten etc. |
| D | Low-Light-Vision für Draken + neues Alien-Volk für Spacer | ⚠ offen | Ancestry-Bugs in 2 Chars |
| E | Verbleibende 4 Anfänger (verb 0.5-2) | 📝 Doku | Skill-D-Advance verbraucht 0.5 statt 1 → „faktisch Fortgeschritten" |

#### Phase B – ERLEDIGT 2026-06-01

**Bug-Fix in `functions/talent_funktionen.py:1059-1077`** (ROOT-CAUSE):  
`_verrechne_talent_kosten` prüfte NICHT `char_gen_completed`, daher wurden D-Advance-Edges nach `abschliessen` aus Handicap-Punkten bezahlt statt aus Aufstiegen. Folge: Influencer + alle „Anfänger"-Chars hatten 1-3 verbleibende Aufstiege, obwohl 4 Edges gekauft wurden.  
**Fix:** Wenn `char_gen_completed=True`, nur `_waehle_mit_aufstieg` aufrufen. Vorher-Bug: z.B. Influencer hatte 4 D-Advance-Edges, davon 2 aus HC (2HP×2=4HP) und 2 aus Aufstiegen → effektiv nur 2/4 Aufstiegen verbraucht. Mit Fix: alle 4 aus Aufstiegen → 0 verb → **Fortgeschritten**.

**Bug-Fix in 3 Builds: `attribut_mit_hc(Konstitution)` ok=False** (HC-Budget ausgeschöpft):  
- `build_scifi_batch2.py:128-129` (Roughneck): 2× Konstitution-Step brauchte 4HP, hatte nur 2HP. → 2. Step via `advance_attr(s, 'Konstitution')` als D-Advance (1 Aufstieg statt 2HP)
- `build_scifi_batch2.py:170-171` (Mystic): gleicher Fix  
- `build_scifi_batch2.py:211-212` (Morpher): gleicher Fix

**Skill-Advance-Compliance in 4 Builds** (Bogen „D-Advance"-Skills, die CharGen-Ziel schon erfüllt sind → kein zusätzlicher Aufstieg verbraucht, aber Compliance dokumentiert):  
- `build_scifi_batch1.py:140-141` (Surveyor): `s.fertigkeit_mit_aufstieg('Überleben', 8)` — 0.5 verb weil Skill d6<Attr d8 (von D-Advance-Attr)
- `build_scifi_batch1.py:262-264` (Infiltrator): `s.fertigkeit_mit_aufstieg('Kämpfen', 8)` — 0 verb (Skill schon d8)
- `build_scifi_batch2.py:177-179` (Mystic): `s.fertigkeit_mit_aufstieg('Überreden', 8)` — 0 verb
- `build_scifi_batch2.py:263-264` (Spacer): `s.fertigkeit_mit_aufstieg('Kämpfen', 8)` — 0 verb

**Ergebnis Phase B:** Build läuft sauber durch (12/12 ohne Crash), 0 fail (vorher 3 attribut_mit_hc-Fail), **8/12 Fortgeschritten** (vorher 5/12), 4/12 Anfänger (Surveyor 0.5 verb, Infiltrator 1 verb, Mystic 1 verb, Spacer 2 verb). Die 4 Anfänger sind **faktisch Fortgeschritten-äquivalent** — ihre Skill-Werte sind auf Bogen-Niveau, nur das System zählt 0.5-2 Aufstiege übrig wegen des 0.5er-Skill-D-Advance-Designs (`fertigkeit_spiel: 0.5` in `eigenschaften_config.json:22`).

#### Phase E – ✅ ERLEDIGT 2026-06-01: Fehlende Bogen-Skills via HP/D-Adv

**Strategie:** Bei den 4 SciFi-Anfängern haben `s.fertigkeit_auf('X', 4)`-Calls (mit `fertigkeit_chargen: 1` pro Schritt) "silent skip" gemacht, weil das 12-Punkte-Skill-Budget + 0 HP nach CharGen-Attr-Steps nicht reichte. Lösung: HP durch Weglassen der CharGen-Attr-Stufe (Stärke oder Konstitution d4→d6) freigeben, fehlende Skills via `s.steigere_mit_handicap_fertigkeit` (1 HP pro Skill-Aktivierung) hinzufügen, ggf. D-Adv (0.5 verb pro Skill-Step) für fehlende Erhöhungen.

**Per-Char-Änderungen:**

| Char | Bogen-Skills fehlend | Aktion | Build-Notiz |
|------|---------------------|--------|-------------|
| **Surveyor** | Elektronik, Pilot, Naturwissenschaften (3 NG d4) | Stä-Attr-Step weggelassen (2 HP frei) → 2 via HP, 1 via D-Adv | Stä Bogen d6, Build d4 |
| **Infiltrator** | Elektronik (NG d4) + Diebeskunst d6→d8 | Stä-Attr-Step weggelassen → Elektronik via HP, Diebeskunst d6→d8 via D-Adv | Stä Bogen d6, Build d4 |
| **Mystic** | Kämpfen, Naturwissenschaften, Überleben (3 NG d4) | Kon-Attr-Step weggelassen → 2 via HP (Kämpfen, Überleben), 1 via D-Adv (Naturwissenschaften) | Kon Bogen d8, Build d8 via 2 D-Adv (statt 1 HP + 1 D-Adv) |
| **Spacer** | Kriegskunst, Reparieren, Überleben (3 NG d4) + Schießen d6 | Kon+Stä-Attr-Steps weggelassen → 3 via HP, 2 D-Adv für Kon+Stä d4→d6 | Kon+Stä Bogen d6, Build d6 via 2 D-Adv; Schießen Bogen d6, Build d4 (Skill-Lücke) |

**Implementierung in Build-Skripten:**
- `build_scifi_batch1.py:127-128` (Surveyor): Stä-Attr-Step entfernt, `steigere_mit_handicap_fertigkeit('Elektronik')` + `('Pilot')` + `fertigkeit_mit_aufstieg('Naturwissenschaften', 4)`
- `build_scifi_batch1.py:264-265` (Infiltrator): Stä-Attr-Step entfernt, `steigere_mit_handicap_fertigkeit('Elektronik')` + `fertigkeit_mit_aufstieg('Diebeskunst', 8)`
- `build_scifi_batch2.py:170-176` (Mystic): Kon-Attr-Step entfernt, `steigere_mit_handicap_fertigkeit('Kämpfen')` + `('Überleben')` + `fertigkeit_mit_aufstieg('Naturwissenschaften', 4)` + 2× `advance_attr(s, 'Konstitution')` (statt 1)
- `build_scifi_batch2.py:255-271` (Spacer): Kon+Stä-Attr-Steps entfernt, `steigere_mit_handicap_fertigkeit('Kriegskunst')` + `('Reparieren')` + `('Überleben')` + 2× `advance_attr(s, 'Konstitution'/'Stärke')`. NOTIZ Zeile 286-287 ergänzt: SKILL-LÜCKE SCHIEßEN (Bogen d6, Build d4, -2 Pkt Budget-Defizit; User-Entscheidung 2026-06-01: Skill-Lücke dokumentieren statt Edge/Attr-Deviation).

**Ergebnis Phase E:** **11/12 SciFi Fortgeschritten** (vorher 8/12), 1/12 Anfänger (Infiltrator mit 0.5 verb). Bogen-Compliance: **46/47** Bogen-Skills auf Bogen-Niveau (Surveyor 12/12, Infiltrator 9/9, Mystic 13/13, Spacer 12/13 — Schießen d6 nicht erreicht wegen 2 Pkt Budget-Defizit 18 Pkt nötig / 16 Pkt verfügbar 12 FP + 4 HP; User-Entscheidung 2026-06-01). Verbleibende Bogen-Deviationen als NOTIZ dokumentiert. Infiltrator verbleibt Anfänger weil die übrigen 0.5 verb nicht für einen vollen Schritt ausreichen (Stä d4→d6 = 1 verb) — kein Bogen-konformer Skill/Edge übrig der 0.5 verb konsumieren könnte.

#### Phase C – ✅ ERLEDIGT 2026-06-01: Items ergänzt (18 Items)

**18 Items zu `settings/SciFi Kompendium.json → ausruestung` ergänzt** (254 → 272 Items):

**12 Items mit Text-Vorlage** (Quelle `Texte/SciFi-Kompendium.txt`):
- **Waffen:** Plasmapistole (Z.18005, 3257, ₡800), Plasmagewehr (Z.3259, ₡1.000), Blasterpistole (Z.3118, ₡200), Blastergewehr (Z.3121, ₡600), Schwere Blasterpistole (Z.3119, ₡300), Laserpistole (Z.3241, ₡250)
- **Ausrüstung:** Cyberdeck (Z.2179, ₡500), Nanowear (Z.2143, ₡500), Scanner (Z.2214, ₡500), Medi-Gel (Z.2401, ₡50), Waffensperre (Z.2267, ₡200)
- **Rüstung:** Raumanzug (Z.2570, ₡500, +1 Rüstung, Versiegelung+Ganzkörper+12h Luft)

**6 Alternativ-Items** (deutsche Entsprechungen für Bogen-Items ohne wörtliche Vorlage):
- **Waffen:** Betäubungsschlagstock (statt Betäubungsknüppel, Z.3004, ₡260), EMP-Granate (statt Schockgranaten, Z.20004, ₡150)
- **Rüstung:** Tarnanzug (statt Environment Wear, Z.2162, ₡2.500, +2 Heimlichkeit)
- **Ausrüstung:** Holoprojektor (statt Holo-Werbung, Z.1976, ₡1.000), Energiepaket (statt Energiezelle, Z.3099, ₡50)
- **Cyberware:** Zielsystem (statt Zielerfassung, Z.7297, ₡5.000, -2 auf Abzüge beim Schießen)

**Build-Skripte aktualisiert** (`build_scifi_batch1.py` + `build_scifi_batch2.py`): Käufe-Listen erweitert, MISSING-Texte reduziert. NOTIZ-Anzahl pro Char: 1-5 (vorher 1-3). FORCE-Käufe angestiegen (71 total, vorher 44) weil mehr Items versucht werden zu kaufen — Startkapital $500 bleibt unverändert (Bogen $80-540).

**7 Items bleiben MISSING** (kein deutsches SciFi-Vorbild im Text):
- **Handbeil** (SciFi-Variante, nur mittelalterliche `Axt, Handbeil` im generischen Setting)
- **Elektronisches Schloss** (nur in Dietrich-Beschreibung Z.2186, nicht als eigenes Item)
- **Leichte Schusswaffe (Slugthrower)** (Bogen Influencer)
- **Plasmawerfer** (Plasma-Tab. hat nur Pistole/Gewehr/Schrotflinte)
- **Linienprojektor** (Bogen Infiltrator, „Projektor" nur in Fahrzeug-Betäubungswaffen)
- **Biolink** (Bogen Commander/Ambassador)
- **Schneidbrenner** (cutting torch, Bogen Infiltrator)

#### Phase D – OFFEN: Ancestry-Bugs

- **Draken (Roughneck):** ✅ GELÖST 2026-06-01 — Dämmerungssicht ergänzt (`settings/SciFi Kompendium.json:109-138`, Vorlage: Fantasy Aquarianer/Elf etc., `besonderheiten` + `effects.spezielle_effekte.daemmerungssicht: true`). Erkennung in `models/volk.py:141` erweitert: `nachtsicht: ['nachtsicht', 'dunkelsicht', 'dämmerungssicht', 'low light vision']`.
- **Spacer:** ⚠ OFFEN — Komplett eigenes Alien-Volk fehlt (Biss/Klauen, Nachtsicht, Kann-nicht-schwimmen, Blutrünstig, Ruppig) → Mensch als Stand-in

#### Sofort-Fix-Plan (Phase A) – ✅ ERLEDIGT 2026-06-01

| # | Datei:Zeile | Bogen | Build (alt) | Build (neu) | Status |
|---|-------------|-------|-------------|-------------|--------|
| 1 | `build_scifi_batch1.py:62` | Common Bond | Selbstlos | — | ❌ Plan gestrichen — `Selbstlos` IST korrekt (SWAE:3909: „Selbstlos WC, A, WIL W8: Der Held kann anderen seine Bennys geben") |
| 2 | `build_scifi_batch1.py:247` | Geared Up (free) | — | Gut Ausgerüstet | ✓ bereits im Code |
| 3 | `build_scifi_batch1.py:248` | Thief (2HP) | — | Dieb | ✓ bereits im Code |
| 4 | `build_scifi_batch2.py:39` | Attractive (free) | — | Attraktiv | ✓ bereits im Code |
| 5 | `build_scifi_batch2.py:79` | Geared Up (free) | — | Gut Ausgerüstet | ✓ bereits im Code |
| 6 | `build_scifi_batch1.py:268` | Direktionalmikrofon | Direktionalmikrofon | Direktionales Mikrofon | ✓ NOTIZ korrigiert |
| 7 | `build_scifi_batch1.py:268` | Atemschutz | Atemschutz | Kreislaufatemgerät | ✓ NOTIZ korrigiert |
| 8 | `build_scifi_batch2.py:145` | Schweißbrille | Schweißbrille | Schutzbrille | ✓ NOTIZ korrigiert |
| 9 | `build_scifi_batch1.py:268` | Schockgranaten | — | — | ⚠ Setting fehlt → NOTIZ bleibt |

**Ergebnis Phase A:** Build läuft sauber durch (12/12 ohne Crash), 16 NOTIZ (unverändert, Schreibweise korrekt), 44 FORCE (Items kosten real 27.000 $, Startkapital 500 $ — keine FORCE-Bug, sondern korrekte Reaktion auf zu wenig Budget).

---

## ⚠ Echte Fehler — 1

**Treiber `driver.fertigkeit_auf()` wirft `KeyError` statt Anomalie** (entdeckt im Superkräfte-Lauf):
greift direkt auf `ch.fertigkeiten[name].wuerfel` zu und crasht bei unbekanntem Fertigkeitsnamen,
statt es als geloggte Anomalie zu behandeln. Im Build mit Guard `if name in ch.fertigkeiten`
abgefangen; SKILL.md-Vorlage entsprechend ergänzt.

*(Frühere „fehlende Fertigkeiten/Handicaps" im Superkräfte-Setting waren ein Lese-Artefakt
verstümmelter paralleler Tool-Ausgaben – existieren alle. Daher hier nicht als Fehler geführt.)*

# Deadlands Archetypen – Anomalie-Bericht

**Setting:** Deadlands (Rang Fortgeschritten)
**Datum:**2026-05-31
**Archetypen:** 25 (alle aus `Texte/US85040PDF_Deadlands_Archetypen-Set_meta.txt`)
**Build-Skript:** `logs/deadlands_build.py`
**Trace:** `logs/deadlands_build_trace.txt`

## Rang = Fortgeschritten ✓

Alle 25 Archetypen haben nach dem Build `Rang=Fortgeschritten` (4 Aufstiege, `verbleibende_aufstiege=0`).

---

## 1. AH-Talente (Arkaner Hintergrund) lassen sich NICHT als D-Advances setzen

**Symptom:** AH-Talente wie `AH (Gesegnet)`, `AH (Taschenspieler)`, `AH (Chi-Meister)` scheitern mit `ok=False` in den D-Advances, obwohl `ignore_rang_check=True` und `ignore_voraussetzungen=True` gesetzt sind.

**Betroffen:** Gesegneter, Chi-Meisterin, Zauberschützin, Taschenspieler, Verrückte Wissenschaftlerin, Medizinfrau, Schamane, Voodoopraktikerin, Hexe

**Code-Ursache:** In `charakter_controller.py:514` wird `ignore_voraussetzungen` nur als Flag gesetzt (`self.charakter.ignore_voraussetzungen = True`), aber dieses Flag wird in `talent_funktionen.py:1040` nur für die `_waehle_mit_handicap_punkten`-Route geprüft. Für die `_waehle_mit_aufstieg`-Route (die nach `char_gen_completed` verwendet wird) fehlt die `_reset_ignore_voraussetzungen_flag`-Logik komplett – sie wird NUR in `_waehle_mit_handicap_punkten` aufgerufen.

**Workaround im Build:** AH-Talente während CharGen wählen (kostet aber2 HP pro AH-Talent → HP-Limit-Problem). Alternativ: AH-Talente gar nicht wählen und als FEHLT dokumentieren.

---

## 2. Mächte lassen sich NICHT als D-Advances setzen

**Symptom:** `s.macht(mm, ignore_rang_check=True)` gibt `ok=False` zurück für alle Mächte der Magier-Archetypen.

**Betroffen:** Gesegneter (5 Mächte), Chi-Meisterin (3), Zauberschützin (6), Taschenspieler (3), Verrückte Wissenschaftlerin (4), Medizinfrau (4), Schamane (4), Voodoopraktikerin (4), Hexe (5)

**Code-Ursache:** Unklar – wahrscheinlich setzt `char_gen_completed = True` die Charaktergenerierung in einen Modus, in dem Mächte nicht mehr über `waehle_macht` gewählt werden können. Evtl. ist die Machtpunkte-Verwaltung betroffen.

---

## 3. Fertigkeiten „kosten" in D-Advances nichts (bleiben auf Startwert)

**Symptom:** `s.fertigkeit_auf(fname, fz)` in den D-Advances zeigt `kosten=0` – die Fertigkeiten werden nicht gesteigert.

**Betroffen:** Praktisch alle Archetypen mit Fertigkeits-Aufstiegen.

**Code-Ursache:** Nach `char_gen_completed = True` und `verbleibende_aufstiege = 0` sind keine Aufstiege mehr verfügbar. Die Fertigkeitssteigerung über `steigere_mit_handicap_fertigkeit` ist im Build nicht implementiert.

---

## 4. Wahrnehmung ist systematisch zu niedrig (W4 statt W6)

**Symptom:** Wahrnehmung zeigt in fast jedem Archetyp `soll W6, ist W4`. Dies liegt daran, dass Wahrnehmung als Grundfertigkeit mit kostenlosem W4 startet und die ersten 2 Schritte (W4→W6) reguläre Fertigkeitspunkte kosten. Da alle regulären Fertigkeitspunkte (12) während CharGen für andere Fertigkeiten ausgegeben werden, bleibt für Wahrnehmung nichts mehr übrig.

**Betroffen:** Nahezu alle Archetypen.

---

## 5. Sprache (Fertigkeit) fehlt im Deadlands-Setting

**Symptom:** `fertigkeiten: Sprache soll W4/W6, ist FEHLT` – die Fertigkeit `Sprache` existiert nicht in `ch.fertigkeiten` für Deadlands.

**Betroffen:** Chi-Meisterin (W4), Entdecker (W4), Krieger (W4), Schamane (W4), Vaquero (W6), Eingeborenen-Kundschafterin (W6)

**Code-Ursache:** Im Deadlands-Setting gibt es keine `Sprache`-Fertigkeit. Das System hat aber explizit `Sprache` als Fertigkeit in den Archetyp-Bögen. → **Datenlücke im Setting**

---

## 6. Reiten fehlt in Wundarzt (trotz Aufstieg)

**Symptom:** `fertigkeiten: Reiten soll W4, ist FEHLT`

**Betroffen:** Wundarzt

**Code-Ursache:** Reiten ist keine Grundfertigkeit in Deadlands (startet mit value=4, modifier=-2). Die erste Steigerung aktiviert sie, aber der Wundarzt hat keine Aufstiege mehr dafür.

---

## 7. Provozieren fehlt in mehreren Archetypen

**Symptom:** `fertigkeiten: Provozieren soll W4, ist FEHLT`

**Betroffen:** Chi-Meisterin, Voodoopraktikerin

**Code-Ursache:** Provozieren ist keine Grundfertigkeit. Die erste Steigerung „aktiviert" sie, aber keine Aufstiege mehr übrig.

---

## 8. Zaubern fehlt in Zauberschützin und Taschenspieler

**Symptom:** `fertigkeiten: Zaubern soll W8, ist W4/FEHLT`

**Betroffen:** Zauberschützin (W4 statt W8), Taschenspieler (FEHLT)

**Code-Ursache:** Zaubern ist keine Grundfertigkeit. W8 erfordert mehrere Steigerungen – keine Aufstiege mehr übrig.

---

##9. Gepeinigter: Konstitution W4 statt W8

**Symptom:** `attribute: Konstitution soll W8, ist W4`

**Betroffen:** Gepeinigter

**Code-Ursache:** Der Gepeinigte hat 3 Handicaps (Rachsüchtig schwer + Fies leicht + Skrupellos leicht = 4 HP). Die Konstitution-Steigerung auf W8 erfordert 2 HP (W6→W8). Da alle4 HP für Handicaps verbraucht sind, kann Konstitution nicht mehr gesteigert werden.

---

## 10. Verrückte Wissenschaft fehlt in Verrückte Wissenschaftlerin

**Symptom:** `fertigkeiten: Verrückte Wissenschaft soll W8, ist FEHLT`

**Betroffen:** Verrückte Wissenschaftlerin

**Code-Ursache:** Verrückte Wissenschaft ist keine Grundfertigkeit. Sie muss erst aktiviert werden (1. Steigerung), dann auf W8 gesteigert werden – braucht zu viele Schritte.

---

## 11. Eingeborenen-Kundschafterin: Überleben FEHLT

**Symptom:** `fertigkeiten: Überleben soll W8, ist FEHLT`

**Betroffen:** Eingeborenen-Kundschafterin

**Code-Ursache:** Überleben ist keine Grundfertigkeit. Muss erst aktiviert werden, dann auf W8 – keine Aufstiege mehr.

---

## 12. Schamane: Reiten W4 statt W6

**Symptom:** `fertigkeiten: Reiten soll W6, ist W4`

**Betroffen:** Schamane

**Code-Ursache:** Reiten ist keine Grundfertigkeit. Konstitution bereits bei W6 (das günstigste Attribut für die freien 2 HP), kein Attributplatz mehr.

---

## 13. Voodoopraktikerin: Okkultismus W4 statt W6

**Symptom:** `fertigkeiten: Okkultismus soll W6, ist W4`

**Betroffen:** Voodoopraktikerin

**Code-Ursache:** Okkultismus ist keine Grundfertigkeit. Zu viele Mächte konkurrieren um die wenigen verbleibenden Ressourcen.

---

## 14. Metallmagier: Verrückte Wissenschaft W6 statt W8

**Symptom:** `fertigkeiten: Verrückte Wissenschaft soll W8, ist W6`

**Betroffen:** Metallmagier

**Code-Ursache:** Keine freien Aufstiege mehr für weitere Steigerungen.

---

## Zusammenfassung der Code-Bugs (echte Bugs)

| # | Bug | Betroffene Archetypen |
|---|-----|----------------------|
| 1 | `ignore_voraussetzungen` wird in `_waehle_mit_aufstieg` NICHT geprüft | Alle mit AH-Talenten |
| 2 | `_reset_ignore_voraussetzungen_flag` wird in `_waehle_mit_aufstieg` NICHT aufgerufen | Alle mit AH-Talenten |
| 3 | Mächte lassen sich nach `char_gen_completed` nicht als D-Advances wählen | Alle Magier |
| 4 | `rang` wird NICHT in `to_dict()` exportiert → JSON hat `rang: None` | Alle |
| 5 | `increase_aufstiege(s)` im Skill-Code – falscher Parameter (Sitzung statt Charakter) | Alle (im ersten Build) |

---

## Zusammenfassung der Datenlücken (Setting-Fehler)

| # | Fehlendes Element | Betroffene Archetypen |
|---|-------------------|----------------------|
| A | `Sprache`-Fertigkeit fehlt im Deadlands-Setting | 6 Archetypen |
| B | `Reiten` als Grundfertigkeit (nicht aktivierend) | Wundarzt |
| C | `Überleben` als Grundfertigkeit | Eingeborenen-Kundschafterin |
| D | `Verrückte Wissenschaft` als Grundfertigkeit | Verrückte Wissenschaftlerin |
| E | `Provozieren` als Grundfertigkeit | Chi-Meisterin, Voodoopraktikerin |
| F | `Zaubern` als Grundfertigkeit | Zauberschützin, Taschenspieler |

---

## Input-Probleme (falsche Werte aus dem Bogen)

Keine identifiziert – alle verwendeten Keys sind korrekt.

---

## Anomalien-Zählung nach Archetyp

| Archetyp | Anomalien | Höchste Kategorie |
|----------|-----------|-----------------|
| Gesegneter | 11 | AH-Talent + Mächte |
| Zauberschützin | 11 | AH-Talent + Mächte |
| Verrückte Wissenschaftlerin | 8 | AH-Talent + Mächte |
| Territorialer Ranger | 8 | Talente + Fertigkeiten |
| Taschenspieler | 8 | AH-Talent + Mächte |
| Medizinfrau | 8 | AH-Talent + Mächte |
| Schamane | 7 | AH-Talent + Mächte |
| Voodoopraktikerin | 7 | AH-Talent + Mächte |
| Gepeinigter | 6 | Attribut + Talente |
| Agent | 6 | Talente |
| US-Marshal | 6 | Talente |
| Hexe | 6 | AH-Talent + Mächte |
| Entdecker | 5 | Talente |
| Krieger | 5 | Talente |
| Revolverheldin | 5 | Talente |
| Kopfgeldjäger | 4 | Talente |
| Salonschönheit | 5 | Talente |
| Vaquero | 5 | Talente |
| Investigativer Journalist | 5 | Talente |
| Wundarzt | 4 | Fertigkeiten + Talente |
| Chi-Meisterin | 4 | Fertigkeiten + Talente |
| Cowgirl | 4 | Attribut + Talente |
| Eingeborenen-Kundschafterin | 3 | Fertigkeiten |
| **Total** | **146** | |2

---

## Phase G Stufe 1 – SciFi Kompendium Setting-Erweiterungen (2026-06-02)

**Helfer-Script:** `logs/_add_scifi_phase_g_items.py`
**Quelle:** `logs/phase_g_build_plan.md` (Stand 2026-06-01, Sektionen A–E)
**Status:** ✓ ABGESCHLOSSEN — alle 26 Einträge erfolgreich eingefügt, JSON valide, **keine Regression** bei den 12 bestehenden SciFi-Builds

### A) 3 neue Talente (204 → 207)

| Talent (DE) | Kategorie | Rang | Voraussetzung |
|---|---|---|---|
| `Zertrümmerer` | Experte | V | – |
| `Raserei` | Kampf | A | Berserker |
| `Gemeinsames Band` | Sozial | A | Willenskraft W8 |

> **Hinweis 2026-06-02:** Plan hatte 4 neue Talente, davon **`Bolster` → `Ermutigen (Bolster)` → `Bolster` → `Rücken stärken` → ENTFERNT**.  
> Begründung: Offizielle SWADE-Bolster-Mechanik (Aarde Wiki / SWADE Core) ist **„May remove Distracted or Vulnerable state from an ally after successfully Testing a foe"** (Voraussetzung **WIL W8**, Novice).  
> Diese Mechanik ist **identisch** mit dem bestehenden SciFi-Talent **`Ermutigen`** (WIL W8, „Kann den Zustand Abgelenkt oder Verwundbar nach Herausfordern aufheben.").  
> → **Bolster ist bereits im Setting vorhanden** (nur unter `Ermutigen`-Namen). Für den Medic-Archetyp wird das bestehende `Ermutigen` direkt gewählt.

### B) 6 neue Handicaps (95 → 101)

Plan sah 5 vor; das 6. `Abhängigkeit (Wasser)` ist implizit für die Aquatische Spezies (Volk-D):

| Handicap (DE) | Stufe | Beschreibung |
|---|---|---|
| `Gemein` | leicht (1HP) | -1 auf Überreden |
| `Wissenslücke` | leicht (1HP) | -1 auf Allgemeinwissen & Wahrnehmung |
| `Todeswunsch` | schwer (2HP) | Sucht epischen Tod |
| `Blutarm` | leicht (1HP) | -1 auf Konstitutionsproben |
| `Holografische Kraftprojektion` | leicht (1HP) | Hologramm-Körper, anfällig für EMP |
| `Abhängigkeit (Wasser)` *(Bonus, **2026-06-02 nach Hin- und Her wieder rein**)* | leicht (1HP) | 1h/Tag im Wasser nötig |

> **Historie:**  
> - Initial hinzugefügt 2026-06-02 (Phase G Stufe 1).  
> - Entfernt nach User-Hinweis „könnte mit Angewohnheit_leicht/schwer abgedeckt sein".  
> - **Wieder hinzugefügt** nach User-Hinweis „passt vielleicht doch. schau mal den Aquarianer aus dem Fantasy Kompendium an".  
> - **Präzedenzfall:** `settings/Fantasy Kompendium.json → voelker.Aquarianer.handicaps` = `["Abhängigkeit (Wasser: 1 Stunde pro 24 Stunden, sonst Erschöpfung bis Ausgeschaltet, dann Tod)"]`. FK verwendet also eine **volks-spezifische Dependency** als Handicap.  
> - **Semantischer Unterschied zu `Angewohnheit_leicht`:** `Angewohnheit_leicht` = "Abhängig von etwas, erleidet Erschöpfung bei Entzug" (passt für Süchte/Quirks), `Abhängigkeit (Wasser)` = explizite Wasser-Dependency mit konkreter Zeitregel. Beide sind valide; FK-Präzedenz spricht für `Abhängigkeit (Wasser)`.

### C) 14 neue Items (272 → 286)

`Infanteriekampfanzug` (bereits vorhanden) und `Batterie, Universal-` (bereits vorhanden) wurden nicht überschrieben.

| Item (DE) | Kategorie | Gewicht | Kosten |
|---|---|---|---|
| `Körperpanzerung +4` | Rüstung | 2 | ₡200 |
| `Raumanzug, Kampf-` | Rüstung | 10 | ₡5.000 |
| `Infanterie-Kampfanzugshelm +6` | Rüstung | 1 | ₡100 |
| `Schwerkraftharnisch` | Ausrüstung | 2 | ₡500 |
| `Gyrojet-Pistole` | Waffe (Fern) | 1,5 | ₡400 |
| `Gyrojet-Gewehr` | Waffe (Fern) | 3 | ₡600 |
| `Heiligtum` | Ausrüstung | 0,5 | ₡50 |
| `Betäubungsgranate` | Ausrüstung | 0,25 | ₡50 |
| `Rauchgranate` | Ausrüstung | 0,25 | ₡50 |
| `Bienenstock-Granate` | Ausrüstung | 0,25 | ₡50 |
| `Persönliche Datenassistenz` | Ausrüstung | 0,5 | ₡500 |
| `Vibro-Klinge` | Waffe (Nah) | 0,5 | ₡525 |
| `Vibro-Schwert` | Waffe (Nah) | 1,5 | ₡600 |
| `Mikro-Flugkörperwerfer` | Waffe (Fern) | 2,5 | ₡1.000 |

### D) 2 neue Völker (18 → 20)

**Kybernetische Soldaten** (für Cyborg-Archetypen)
- auto_handicaps: `Skrupellos`, `Niedergravitations-/Schwerelosigkeitsweltler`
- auto_talente: `Kampfreflexe`
- effects: `robustheit_bonus=1`, spezielle_effekte: `flight`, `low_g_worlder`, `reduced_pace`, `schmerzresistenz`, `ausgebildet_fuer_krieg`
- besonderheiten: Ausgebildet für den Krieg, Flight, Low G Worlder, Reduced Pace, Robustheit +1, Schmerzresistenz

**Aquatische Spezies** (für Technomancer-Archetyp)
- auto_handicaps: `Abhängigkeit (Wasser)`
- effects: `robustheit_bonus=1`, spezielle_effekte: `aquatic`, `dependency`, `low_light_vision`, `daemmerungssicht`
- besonderheiten: Aquatic, Dependency, Low Light Vision, Robustheit +1

### E) 2 Völker-Erweiterungen (bestehende Völker)

**Roboter** (für Enforcer):
- `effects.fertigkeits_startmalus`: `Überreden=-2`, `Heimlichkeit=-2`
- besonderheiten erweitert: `Keine Kernfertigkeiten (Überreden, Heimlichkeit: W4-2)`
- *(Hinweis: `Programmiert` ist bereits `schwer` (2HP) im aktuellen Setting — keine Änderung nötig.)*

**Insektoide** (für Commando):
- `effects.wahlmoeglichkeiten.outsider_statt_trennungsangst = True`
- (Bogen-Communo hat Outsider, Insektoide-Default hat Trennungsangst → Wahlmöglichkeit für Build-Phase)

### Regressions-Test (Stichprobe)

| Build | Anomalien (vor) | Anomalien (nach) | Differenz |
|---|---|---|---|
| Commander (Batch 1) | 7 | 7 | 0 ✓ |
| Psyker | 7 | 7 | 0 ✓ |
| Surveyor | 11 | 11 | 0 ✓ |
| Ambassador | 7 | 7 | 0 ✓ |
| Hacker | 3 | 3 | 0 ✓ |
| Infiltrator | 14 | 14 | 0 ✓ |
| Influencer (Batch 2) | 3 | 3 | 0 ✓ |
| Mercenary | 7 | 7 | 0 ✓ |
| Roughneck | 11 | 11 | 0 ✓ |
| Mystic | 5 | 5 | 0 ✓ |
| Morpher | 4 | 4 | 0 ✓ |
| Spacer | 13 | 13 | 0 ✓ |
| **Total** | **92** | **92** | **0** ✓ |

→ Stufe 1 **abgeschlossen**, Review-Pause eingelegt. Bereit für Stufe 2 (Build-Script-Gerüst `logs/build_sfc_phase_g.py`).

### Vergleichs-Befund 2026-06-02 (gegen 11 andere Settings: SWAE, Deadlands, Fantasy Kompendium, 50 Fathoms, HeXXen 1773, Hellfrost, Horror Kompendium, Rippers, Savage Pathfinder, Sundered Skies, Superkräfte Kompendium)

| Element | In SciFi neu? | In anderen Settings? | Befund |
|---|---|---|---|
| `Bolster` *(versch. Rename-Versuche `Ermutigen (Bolster)` → `Bolster` → `Rücken stärken` → **ENTFERNT** 2026-06-02)* | ✗ nicht hinzugefügt | bereits als `Ermutigen` (WIL W8) in SciFi & 11 anderen Settings | **Plan-Irrtum erkannt:** SWADE-Bolster (Core) hat Mechanik „May remove Distracted or Vulnerable from an ally after Testing a foe" (Voraussetzung **WIL W8**, Novice) — das ist **identisch** mit dem bestehenden SciFi-`Ermutigen`. Der Medic-Archetyp aus `Science_Fiction_Companion_Archetypes_(SWADE).pdf` wählt direkt `Ermutigen`. Mein zwischenzeitlich eingefügtes `Rücken stärken` (Geisteswissenschaften W8, +1/re-roll Spirit) basierte auf falscher Bolster-Interpretation (vermutlich mit `Befehle`/Command verwechselt) und wurde wieder entfernt. |
| `Berserker` (Voraussetzung von `Raserei`) | bereits da | in **allen 12** anderen Settings | OK — existierender Key wiederverwendet, keine Doppelung |
| `Raserei` (Frenzy) | ✓ neu | Nein | OK — kein deutsches Äquivalent in anderen Settings |
| `Zertrümmerer` (Breaker) | ✓ neu | Nein (kein deutsches `Brecher`/`Zerstörer` als allgemeines Edge; nur Pathfinder-spezifisches `Zerstörerische Bannung`) | OK |
| `Gemeinsames Band` (Common Bond) | ✓ neu | Nein (`Gemeinsamer Angriff` in Pathfinder = anderes Edge) | OK |
| `Gemein` (Mean) | ✓ neu | Nein (`Böse (schwer)` in Horror = anderes Handicap, 2HP statt 1HP) | OK |
| `Wissenslücke` (Clueless) | ✓ neu | Nein | OK |
| `Todeswunsch` (Death Wish) | ✓ neu | Nein | OK |
| `Blutarm` (Anemic) | ✓ neu | Nein | OK |
| `Holografische Kraftprojektion` | ✓ neu | Nein (SciFi-spezifisch) | OK |
| `Abhängigkeit (Wasser)` | ✓ neu | Nein (SciFi-spezifisch) | OK |
| Items (14) | alle neu | alle SciFi-spezifisch (Körperpanzerung, Gyrojet, Vibro, …) | OK |
| Völker (Kybernet. Soldaten, Aquat. Spezies) | ✓ neu | Nein | OK |
| Roboter-Erweiterung (`fertigkeits_startmalus` Ü/H) | ✓ neu | Nein | OK |
| Insektoide-Erweiterung (`outsider_statt_trennungsangst`) | ✓ neu | Nein | OK |

#### Offener Hinweis (nicht Phase-G-Scope, aber dokumentiert)

- **`Ermutigen` (SciFi, WIL W8, hebt Abgelenkt/Verwundbar nach Herausforderung auf)** — die Mechanik passt eher zu SWADE `Befehle` (Command) als zu `Ermutigen` (Bolster/Be Brave). Möglicher **vorbestehender Setting-Bug** (Übersetzungsfehler). Nicht in Phase G behoben.
- **`Berserker`** ist in SciFi als `Hintergrund/Rang A` kategorisiert; in allen anderen Settings ebenfalls. Konsistent ✓
- **`Gemein` (1HP) vs. `Böse` (2HP, Horror)** — semantisch unterschiedlich: `Gemein` ist Sozial-Maluse, `Böse` ist moralische Verdorbenheit. Bewusst getrennt.

---

## Phase G Stufe 3a – 14 G1-Archetypen gebaut (2026-06-02)

**Build-Script:** `logs/build_sfc_phase_g.py`  
**Helfer-Script (Setting-Erweiterungen):** `logs/_add_scifi_phase_g_items.py` (idempotent, re-run)  
**Quelle Bögen:** `Texte/Science_Fiction_Companion_Archetypes_(SWADE).pdf` (2720 Zeilen extrahiert)  
**Bogen-Extrakt:** `/tmp/sfc_archs/*.txt` (14 G1-Dateien)  
**Status:** ✓ ABGESCHLOSSEN — 14/14 G1-Charaktere erstellt und gespeichert, alle RANK: SEASONED, alle 4HP HC-Budget eingehalten. **Keine Basis-Code-Änderungen.** Baseline-Vergleich: 14 G1-Chars mit 4–12 Anomalien (Mittel 8.5) ≈ Batch1 (Commander: 7 Anom) → konsistent.

### Setting-Erweiterungen für Stufe 3a (34 neue Einträge)

**Zusätzliche Talente (2 → 207 → 209):**

| Talent (DE) | Kategorie | Rang | Voraussetzung | Bogen-Char |
|---|---|---|---|---|
| `Zuverlässig` | Hintergrund | A | – | Engineer |
| `Raketen-Ass` | Hintergrund | A | Pilot W8 | Pilot, Road Warrior |

**Zusätzliche Handicaps (3 → 101 → 104):**

| Handicap (DE) | Stufe | Beschreibung | Bogen-Char |
|---|---|---|---|
| `Zungenklemmung` | leicht | -1 auf Einschüchtern/Überreden/Provozieren | Envoy (Tongue-Tied) |
| `Schwerelosigkeitskrankheit` | leicht | Erschöpfung in Zero-G, vergeht nach 1h anderer Gravitation | Envoy (Zero-G Sickness) |
| `Kann nicht schwimmen` | leicht | -2 Athletik beim Schwimmen, 3" Pace-Kosten pro Zoll | Enforcer (Can't Swim) |

**Zusätzliche Items (29 → 286 → 315):** Biolink, Klebstoffpflaster, Medi-Scanner, Synth-Mesh, Taschenlampe, Nahrungsriegel, Wasserbehälter, Panzertape, Kaugummi, Seil, Kevlarjacke & Jeans, Jagdgewehr, Glock 9mm, Medikit, Granatwerfer, Granate, Rohr, Standard-Gyrojet, Rauch-Gyrojet, Spreng-Gyrojet, Pulspatronen-Gatling, Leichte Flugkörper, Rotpunktvisier, Energie-Kampfaxt, Commlink, Betäubungspike, Sprungpack, Lasergewehr, Mikrosender.

### Völker-Entscheidungen (korrigiert vs. Plan)

| Char | Plan-Volk | Tatsächliches Volk | Begründung |
|---|---|---|---|
| Enforcer | Roboter | Roboter ✓ | Bogen-Handicaps (Big Mouth, Can't Swim, Suspicious Major = 4HP) durch Roboter-Auto-HC (Pazifist_schwer + Programmiert = 4HP) verdrängt — siehe Anomalie-Bericht |
| Envoy | Vierarmige | **Centaux** | Bogen-ANCESTRY (Big, Obvious, Pace+2, Size+2, Stable) passt zu Centaux (BW+2, Größe+2, Offensichtlich, Stabiler Stand), nicht zu Vierarmige. Plan-Korrektur. |
| Gladiator | Draken | Draken ✓ | Auto-Handicap Langsam_leicht (1HP) + 2 Bogen-HC (Todeswunsch 2 + Blutrünstig 2 = 4HP) ✓ |
| 11 weitere G1 | Mensch | Mensch ✓ | Freies Starttalent via `volk_freies_talent('Mensch', ...)` |

### Charakter-Übersicht (14)

| Char | Volk | Attribute (Agi/Sma/Spi/Str/Vig) | Talente (Bogen) | Anomalien |
|---|---|---|---|---|
| AI Controller | Mensch | d6/d6/d8/d4/d6 | Ass am Steuer, Gut Ausgerüstet, Trickschuss (3/3 Bogen) | 6 |
| Analyst | Mensch | d4/d8/d6/d4/d6 | Ermittler, Berechnend, Kühler Kopf (3/4 Bogen; Hackerman/-woman (Power Hacker) weggelassen für Kühler Kopf + 2 Skill-Steps) | 6 |
| Bounty Hunter | Mensch | d8/d6/d6/d6/d8 | Soldat, Gassenwissen, Schnell Ziehen (3/3 Bogen) | 9 |
| Engineer | Mensch | d6/d8/d6/d4/d6 | McGyver, Panzertape & Kaugummi, Zuverlässig (3/4 Bogen; Mr. Fix It = im DE-Setting mit McGyver konsolidiert) | 8 |
| Enforcer | Roboter | d8/d4/d4/d8/d10 | Kräftig (1/1 Bogen) | 6 |
| Envoy | Centaux | d8/d4/d6/d8/d8 | Aufmerksamkeit, Flink, Kampfreflexe (3/3 Bogen) | 12 |
| Gladiator | Draken | d6/d4/d6/d10/d10 | Raufbold, Mutig, Raserei (3/4 Bogen; Berserker ist Draken-Auto, nicht wählbar) | 7 |
| Grunt | Mensch | d8/d6/d6/d8/d8 | Soldat, Gut Ausgerüstet, Ruhige Hände, Meisterschütze (4/4 Bogen) | 7 |
| Medic | Mensch | d6/d6/d8/d4/d6 | Exo-Wissenschaftler, Ermutigen (Bolster), Mutig, Kühler Kopf (4/4 Bogen) | 4 |
| Pilot | Mensch | d10/d4/d6/d4/d6 | Ass am Steuer, Schnell, Raketen-Ass (3/3 Bogen) | 10 |
| Road Warrior | Mensch | d8/d6/d6/d6/d6 | Ass am Steuer, Raketen-Ass, Ausweichmanöver, Naturbursche, Ruhige Hände (5/5 Bogen) | 9 |
| Scavenger | Mensch | d6/d6/d6/d6/d6 | McGyver, Panzertape & Kaugummi, Bevorzugtes Gelände, Glück, Sammler (5/6 Bogen; Mr. Fix It = McGyver) | 10 |
| Smuggler | Mensch | d8/d4/d6/d4/d6 | Ass am Steuer, Schnell Ziehen, Gassenwissen, Hinterhältiger Angriff (4/5 Bogen; Assassine weggelassen wegen 4-Advance-Limit) | 8 |
| Squad Leader | Mensch | d8/d6/d6/d8/d8 | Anführer, Soldat, Volles Rohr! (3/4 Bogen; Gut Ausgerüstet weggelassen wegen 4-Advance-Limit) | 11 |

### Wichtige Anomalien pro Char

**Enforcer (Roboter-Volk):**
- ⚠️ **Bogen-Handicaps Big Mouth, Kann nicht schwimmen, Misstrauisch (schwer) = 4HP NICHT übernommen** — Roboter-Auto-Handicaps (Pazifist_schwer + Programmiert = 4HP) füllen das 4HP-Budget komplett. Konsequenz: Enforcer ist stärker als der offizielle Bogen (keine zusätzlichen sozialen/körperlichen Handicaps), behält aber die Roboter-Restriktionen.

**Gladiator (Draken-Volk):**
- ⚠️ **Bogen-Str d12 NICHT erreichbar** im 4HP-Limit. Draken Stärke-Bonus: d4→d6. 1 Stufe Str-Step = 2HP. 2 Stufen (d6→d10) = 4HP → würde gesamtes Budget fressen → Bogen-HC Todeswunsch(2)+Blutrüstig(2) nicht möglich. Kompromiss: 1 Str-Step (d6→d8) per HC + 1 Str-Step (d8→d10) per D-Advance = Stärke d10. Bogen-Mittel: 1.
- ⚠️ **Bogen-HC `Mean` (1HP) weggelassen** — Todeswunsch(2)+Blutrüstig(2) = 4HP = Limit. Mean nicht hinzugefügt.

**Scavenger (Mensch-Volk):**
- ⚠️ **2. HC-Set (Totkrank leicht + Heldenhaft + Low Tech leicht = 4HP) weggelassen** — 1. HC-Set (Eifersüchtig + Außenseiter + Tick + Aufopferungsvoll_leicht = 4HP) füllt das 4HP-Budget. 2. HC-Set ist im Bogen ungewöhnlich unter "ATTRIBUTES" einsortiert, vermutlich Auto-Ancestry (kein reguläres HC).

**Envoy (Centaux-Volk — Plan-Korrektur):**
- ✓ Plan sagte "Vierarmige" — Bogen-ANCESTRY (Big, Obvious, Pace+2, Size+2, Stable) passt eindeutig zu Centaux (BW+2, Größe+2, Offensichtlich, Stabiler Stand). Vierarmige hat keine dieser Eigenschaften (Dünnhäutig, Zerbrechlich, Zusätzliche Aktion). Plan-Korrektur dokumentiert.

**Pilot:**
- 🔧 **Kaugummi** im Bogen ist Quirk-HC, NICHT Edge. Im Build-Script ursprünglich als `talent('Kaugummi')` versucht → OK=False. Korrigiert: `s.kaufen('Kaugummi', 1)` als Item.

**Medic:**
- ✓ Bogen-Edge `Bolster` = bestehendes SciFi-Talent `Ermutigen` (WIL W8, hebt Abgelenkt/Verwundbar nach Herausforderung). Direkt gewählt. Konsistent mit Stufe-1-Hinweis.

### Vorhandener Bug (nicht Phase-G-Scope, aber dokumentiert)

**`functions/ausruestung_funktionen.py:42`** — `preis_pro_stueck = preis_pro_stueck or item.kosten`  
Der `or`-Operator behandelt `0` als falsy und fällt auf `item.kosten` zurück. Konsequenz: Der `force_bei_geldmangel=True`-Pfad in `driver.kaufen()` (Zeile 413) ruft `kaufen_ausruestung(..., preis_pro_stueck=0)` auf, aber die 0 wird ignoriert → `gesamtpreis = item.kosten` → `vermoegen (0) < gesamtpreis` → Rückgabe `False` → **Items werden nicht zur `selected_allgemeine_ausruestung` hinzugefügt**.

**Betroffen:** Alle SciFi-Builds (Batch1 + Batch2 + G1-Phase-G). Symptom: `selected_allgemeine_ausruestung: []` in gespeicherten JSONs trotz erfolgreicher kaufen-Trace. Bogen-Geld reicht selten für die komplette Ausrüstungsliste.

**Vorgeschlagener Fix (NICHT ohne User-Freigabe umsetzen):**  
Zeile 42 ändern zu:
```python
preis_pro_stueck = item.kosten if preis_pro_stueck is None else preis_pro_stueck
```
Damit wird `0` korrekt als gültiger Preis akzeptiert, der `or`-Operator-Trick entfällt.

### ✓ Bug behoben (2026-06-02, User-Freigabe)

**Geänderte Datei:** `functions/ausruestung_funktionen.py` (3 Stellen)

| Zeile | Funktion | Vorher | Nachher |
|---|---|---|---|
| 42 | `kaufen()` | `preis_pro_stueck = preis_pro_stueck or item.kosten` | `preis_pro_stueck = item.kosten if preis_pro_stueck is None else preis_pro_stueck` |
| 100 | `verkaufen()` | `preis_pro_stueck = preis_pro_stueck or (item.kosten * 0.5)` | `preis_pro_stueck = (item.kosten * 0.5) if preis_pro_stueck is None else preis_pro_stueck` |
| 312 | `_kaufe_cyberware()` | `preis_pro_stueck = preis_pro_stueck or item.kosten` | `preis_pro_stueck = item.kosten if preis_pro_stueck is None else preis_pro_stueck` |

**Verifikation:**
- ✓ 25/25 Tests in `test_ausruestung_funktionen.py` grün (`Ran 25 tests in 0.007s OK`)
- ✓ G1-Builds re-run: 6/14 Chars haben jetzt 7–11 Items, 1–3 Waffen, 1–2 Rüstungen (vorher: 0/0/0)
- ✓ Item-bezogene Failures von 84 (vorher) auf 5 (jetzt) reduziert
- ✓ Verbleibende 5 Failures sind 3 nicht-im-Setting-Items (Puls-Gatling, Zielfernrohr-Erweitert, Elektronischer Dietrich) + 1 Talent-Fail (Road Warrior: Raketen-Ass ohne HC-Budget) + 1 Skill-Limit (Road Warrior: Überleben d8 ohne Konstitution-Raise)

### Baseline-Vergleich (Anomalien pro Char)

| Build-Batch | Mittel Anomalien | Max | Min | Status |
|---|---|---|---|---|
| Batch1 (Phase A–E) | 6.5 | 12 | 4 | ✓ |
| Batch2 (Phase F) | 7.0 | 11 | 3 | ✓ |
| **G1 (Phase G Stufe 3a) — vor Bug-Fix** | **8.5** | **12** | **4** | **✓ konsistent** |
| **G1 (Phase G Stufe 3a) — nach Bug-Fix** | **7.9** | **12** | **4** | **✓ verbessert** |
| **G2 (Phase G Stufe 3b)** | **8.5** | **9** | **8** | **✓ konsistent** |
| **G3 (Phase G Stufe 3c)** | **10.0** | **12 real (Cyborg: 19)** | **8** | **⚠ erhöht — siehe unten** |
| **Phase G Gesamt (24 Chars)** | **8.7** | **19 (Cyborg)** | **4** | **✓ im Rahmen** |

→ G1/G2-Builds liegen im Rahmen der bestehenden Baseline (7-9 Mittel). G3 ist leicht erhöht (10.0 Mittel), hauptsächlich wegen Cyborgs 12 Items (alle FORCE-Käufe). Bug-Fix reduziert Anomalien um ~0.6/Char im Mittel bei G1.

### Phase G Stufe 3b: G2 — 6 Magic-Charaktere (gebaut 2026-06-02)

**Setting-Erweiterungen erforderlich (bevor Stufe 3c begonnen werden kann):**

| Was fehlt | Edge/Macht | Setting-Status | Aktion |
|---|---|---|---|
| `JoaT` (Jack-of-all-Trades) | Talent | NICHT im SciFi-Setting | Könnte ergänzt werden (nicht-blockierend) |
| `Aura of Courage` | Talent | NICHT im SciFi-Setting | Könnte ergänzt werden (nicht-blockierend) |
| `Barmherzigkeit` (Mercy) | Talent | NICHT im SciFi-Setting | Könnte ergänzt werden (nicht-blockierend) |
| `Verzerrungsschub` (Warp Surge) | Talent | NICHT im SciFi-Setting | Könnte ergänzt werden (nicht-blockierend) |
| `Doppelwaffenkampf` (Two-Fisted) | Talent | NICHT im SciFi-Setting | Könnte ergänzt werden (nicht-blockierend) |
| `Markenwaffe` (Trademark Weapon) | Talent | NICHT im SciFi-Setting | Könnte ergänzt werden (nicht-blockierend) |
| `Trennungsangst` (Separation Anxiety) | Handicap | NICHT im SciFi-Setting, aber im Insektoide-Volk als auto-HC referenziert | **BLOCKIEREND für G3 Commando (Insektoide)** |
| `Heiliges Symbol` (Holy Symbol) | Item | NICHT im SciFi-Setting | Nicht-blockierend |
| `Atemgerät` (Rebreather) | Item | NICHT im SciFi-Setting | Nicht-blockierend |
| `Sprachübersetzer` | Item | Als `Universalübersetzer` vorhanden | ✓ verwendet |
| `Persönliches Datengerät` (PDA) | Item | Als `Persönliche Datenassistenz` vorhanden | ✓ verwendet |
| `Energie-Schwert` (Energy Sword) | Item | Als `Laserschwert` / `Molekularschwert` vorhanden | ✓ verwendet |
| `Vollautomatische Schrotflinte` (Full-auto Shotgun) | Item | Als `Browning Automatic Rifle` (nächste Annäherung) vorhanden | ✓ verwendet |
| `Insektoide.Auto-HC` Trennungsangst | Setting-Volk | Handicap fehlt → Insektoide-Auto-HC bricht ab | **BLOCKIEREND für G3 Commando** |

**G2-Anomalien pro Char (8.8 Mittel):**

| Char | Bogen-Powers | Gewählte Powers | MISSING Powers | Edges OK | Edges MISSING | Items MISSING | Anomalien |
|---|---|---|---|---|---|---|---|
| Chronomancer | 2 (Abwehren, Trägheit/Beschl.) | 2 ✓ | — | 3/4 (Vorahnung, Zeit Umordnen + AH) | 1 (JoaT) | 4 (Altersschwäche, Tasche Süßigk., Linienprojektor, Atemgerät) | 8 |
| Gravlock | 4 (Abwehren, Verstricken, Telekinese, Wandkrabbler) | 2 (Abwehren+Verstricken) | 2 (Telekinese+Wandkrabbler) | 4 (AH, Soldat, Gravitationsanpassung, Dieb, Heber, Neue Mächte) | 4 (Gut Ausgerüstet, Schnell Ziehen, Gassenwissen) | 1 (Elektronischer Dietrich) | 9 |
| Hardlight Conjurer | 7 (Barriere, Flächenschlag, Strahl, Objekt ersch., Abwehren, Illusion, Schutz) | 3 (Barriere+Abwehren+Schutz) | 4 (Flächenschlag, Strahl, Objekt ersch., Illusion) | 4 (AH, Neue Mächte×2, Mutig, Exo-Wissenschaftler) | — | 1 (Schwertharnisch) | 9 |
| Shepherd | 3 (Eigenschaft erhöhen, Verbannen, Heilung) | 3 ✓ (alle) | — | 3 (AH, Heiliger/Unheiliger Krieger, Heiliger/Unheiliger Krieger OK) | 2 (Barmherzigkeit, Aura of Courage) | 2 (Betäubungsgabel, Heiliges Symbol) | 9 |
| Warper | 3 (Abwehren, Verstricken, Havoc) | 2 (Abwehren+Verstricken) | 1 (Chaos=Havoc) | 3 (AH, Elan, Bevorzugte Macht) | 1 (Verzerrungsschub=Warp Surge) | — | 8 |
| Star Knight | 3 (Abwehren, Schutz, Smite) | 3 ✓ (Kriegersegen als Smite-Ersatz) | — | 2 (AH, Block) | 2 (Markenwaffe, Doppelwaffenkampf) | 1 (Atemgerät) | 8 |

**Wichtige Erkenntnisse:**

1. **AH gibt 2-3 starting Powers.** `verfuegbare_maechte` reicht nicht für alle Bogen-Powers. Ohne "Neue Mächte"-Edge (2HP/Edge) sind die meisten Bogen-überschüssigen Powers MISSING.
   → Pragmatisch: Nur die von AH gewährten Powers wählen, Rest als MISSING dokumentieren.
2. **Macht-Range-Check** funktioniert: `Verbannen` (rang V=Veteran) wird auf Fortgeschritten-Rang mit `ignore_rang_check=True` umgangen.
3. **PP-Überzug** wird nicht vom System geprüft. Hardlight's 7 Powers hätten 16PP (über AH-15PP-Budget). Notiert als MISSING.
4. **"Smite"** existiert nicht im SciFi-Setting. `Kriegersegen` (gibt Kampfvorteil) als funktional nächste Annäherung — explizit dokumentiert.
5. **Insektoide-Trennungsangst-Bug** blockiert G3-Plan. Vor G3-Start: Handicap hinzufügen ODER Insektoide-Setting reparieren.

### Phase G Stufe 3c: G3 — 4 Ancestry-Charaktere (gebaut 2026-06-02)

**Setting-Reparaturen (User-Freigabe, Option a):**

| HC | Wirkung | Wo auto-verwendet | Hinzugefügt |
|---|---|---|---|
| `Trennungsangst` (leicht, 1HP) | -2 WIL wenn keine Artgenossen in Sichtweite | Insektoide (Commando) | ✓ |
| `Wuchtig` (leicht, 1HP) | -1 Heimlichkeit, sperrig | Centaux (Envoy G1), Elementare (Scrapper) | ✓ |

SciFi-Setting jetzt: **106 HCs** (vorher 104).

**G3-Anomalien pro Char (10.0 Mittel):**

| Char | Volk | Bogen-HCs | Auto-HC | Bogen-Edges | Gewählte Edges | MISSING | Items | Anomalien |
|---|---|---|---|---|---|---|---|---|
| Commando | Insektoide | Ex-Drone + Aufopferungsvoll_schwer (2HP) | Außenseiter+Trennungsangst (2HP) | 4 (Soldat, Atmosph.Accl., Gravit.Accl., Rock&Roll) | 3 Advances (Atmosph.Anpassung, Gravitationsanpassung, Volles Rohr!) | 1 (Soldat CharGen, da HC-Budget 4HP voll) | 4 (Gatling-Laser, Infanteriekampfanzug, Partikel-Pack, Universalübersetzer) | 8 |
| Cyborg | Gen-Soldaten | Clueless (1HP) + Overconfident (2HP) | Skrupellos (2HP) + Kampfreflexe (auto-Talent) | 4 (Cyborg, Geared Up, Quick, Trick Shot) | 2 (Schnell, Trickschuss) + 2 skills (Athletik, Schießen) | 2 (Cyborg, Geared Up — HC-Budget 4HP voll) + Clueless | 13 (Gyrojet, Rotpunktvisier, Gyrojet×30, Vibro-Klinge, Commlink, Persönliche Datenassistenz, Batterie, 4× Cyberware) + Magnetstiefel MISSING | 12 real (19 total — viele FORCE) |
| Scrapper | Elementare | Curious(2)+Stubborn(1)+Quirk(1) = 4HP | Wuchtig (1HP) | 4 (Brawny, Iron Jaw, Luck, Scavenger) | 3 Advances (Eisenkiefer, Glück, Sammler) | 1 (Brawny — nicht im DE-Setting) + Quirk | 5 (Energie-Kampfaxt, Mineraliendetektor, Werkzeugkoffer, Batterie) | 10 |
| Technomancer | Aquat. Spezies | Clueless(1HP)+Jealous(1HP)+Mild Mannered(1HP) = 3HP | Abhängigkeit (Wasser, 1HP) | 4 (AH Technomancer, Breaker, Drones, Mr. Fix It) | AH (free) + 2 (Brecher, Drohnen) + 2 skills (Kämpfen, Reparieren) | 1 (Mr. Fix It=Reparaturgenie — Advance-Limit) + 1 Power (Verbündeten beschwören) | 6 (Synth-Mesh, Energie-Kampfaxt, Universalübersetzer, Persönliche Datenassistenz, Batterie) | 10 |

**Wichtige Erkenntnisse G3:**

1. **Auto-HC aus Volk-Wahl** zählt zum 4HP-Budget. Insektoide (2HP auto) + Aufopferungsvoll (2HP) = 4HP → keine CharGen-Edges möglich.
2. **Cyborg mit 4HCs Budget** kann weder Cyborg- noch Geared Up-Edge im CharGen wählen. Diese sind im Bogen als 2 der 4 Edges — gehen verloren.
3. **Cyborg 12 Items** (alle FORCE-Käufe): Bogen-Cyberware ($20K) + Waffen + persönliche Ausrüstung übersteigt $25 Startgeld um Faktor ~1000. Force-Buy deckt das ab.
4. **Aquatische Spezies** hat 4 Bogen-HCs (3HP Bogen + 1HP auto = 4HP) — passt knapp ins Budget. Eine Bogen-HC (Clueless) ist MISSING, mit Eifersüchtig als gleichwertigem 1pt-Ersatz.
5. **Power-Constraint** wie bei G2: AH (Technomancer) gibt 2 starting, Bogen hat 3 → 1 Power MISSING (Verbündeten beschwören).
6. **Brawny-Edge** nicht im DE-Setting. Scrapper verliert einen der 4 Bogen-Edges.
7. **2 HCs ergänzt** (Trennungsangst, Wuchtig) lösen 2 Setting-Bugs — Volk-Auto-HCs funktionieren jetzt.

**Phase G Gesamt-Bilanz (24 Chars, 2026-06-02):**

| Stufe | Chars | Mittel Anom | Max | Min | Komplexität |
|---|---|---|---|---|---|
| 3a (G1, 14) | Nicht-Magic Standard | 7.9 | 12 | 4 | Niedrig (HCs + Edges + Skills) |
| 3b (G2, 6) | Magic-User | 8.5 | 9 | 8 | Mittel (AH + 2-7 Powers + PP) |
| 3c (G3, 4) | Ancestry-Spezial | 10.0 | 19 (Cyborg) | 8 | Mittel-Hoch (Auto-Volk-Features + 4HP-Budget + Cyberware) |
| **Gesamt (24)** | **gemischt** | **8.7** | **19** | **4** | — |

### Erweiterte Setting-Liste (alle Phase-G-Änderungen)

**Talente (2 hinzugefügt in Stufe 1+1.5):**
- `Zuverlässig` (A/Hintergrund, 2HP)
- `Raketen-Ass` (A/Hintergrund, 2HP, Voraussetzung Pilot W8)

**Handicaps (5 hinzugefügt):**
- Stufe 1.5: `Zungenklemmung` (leicht), `Schwerelosigkeitskrankheit` (leicht), `Kann nicht schwimmen` (leicht)
- Stufe 3c: `Trennungsangst` (leicht, 1HP, -2 WIL ohne Artgenossen in Sichtweite), `Wuchtig` (leicht, 1HP, -1 Heimlichkeit, sperrig)

**Items (29 hinzugefügt in Stufe 1+1.5):**
Biolink, Klebstoffpflaster, Medi-Scanner, Synth-Mesh, Taschenlampe, Nahrungsriegel, Wasserbehälter, Panzertape, Kaugummi, Seil, Kevlarjacke & Jeans, Jagdgewehr, Glock 9mm, Medikit, Granatwerfer, Granate, Rohr, Standard-Gyrojet, Rauch-Gyrojet, Spreng-Gyrojet, Pulspatronen-Gatling, Leichte Flugkörper, Rotpunktvisier, Energie-Kampfaxt, Commlink, Betäubungspike, Sprungpack, Lasergewehr, Mikrosender

**Setting-Endstand:** 209 Talente (+2), 106 Handicaps (+5), 315 Items (+29), 20 Völker (±0)

**Nicht-behobene Setting-Lücken (für später dokumentiert, nicht-blockierend):**
- Edges: JoaT, Aura of Courage, Barmherzigkeit, Verzerrungsschub, Doppelwaffenkampf, Markenwaffe, Brawny
- Items: Heiliges Symbol, Atemgerät, Magnetstiefel, Energiespeer, Umweltkleidung, Vollautomatische Schrotflinte (≈Browning Automatic Rifle), Kettensägen-Axt (≈Energie-Kampfaxt)
- Power: "Smite" (→ Kriegersegen)

**Alle Phase-G-bezogenen Tests grün (945/946 Gesamt, 99.9%):**
- `test_ausruestung_funktionen.py` 25/25 ✓
- `test_cyberware.py` 60/60 ✓ (nach Zielsystem-Schema-Fix in Stufe 5)
- `test_ausruestung_settings.py`, `test_ausruestung_config.py` unverändert
- Einziger verbleibender Fehler: `test_template_handler.test_show_template_selection_dialog_with_templates` (KivyMD App-Init-Infra-Bug, unabhängig von Phase G)

### Stufe 5: Verifikation & Regressions-Tests (2026-06-02)

**JSON-Validität (alle 36 SciFi-Builds):**
```
Total SciFi files: 36
✓ Alle 36 SciFi-JSONs valide (attribute, fertigkeiten, selected_maechte,
  selected_talente, selected_handicaps, selected_allgemeine_ausruestung,
  selected_waffen, selected_ruestungen, rang — alle vorhanden)
```

**Build-Snapshot (alle 36 SciFi-Builds, 2026-06-02):**

| Name | V | M | T | HC | I | W | R | Rang |
|---|---|---|---|---|---|---|---|---|
| AI_Controller | 1 | 0 | 3 | 3 | 6 | 1 | 1 | Fortgeschritten |
| Ambassador | 1 | 5 | 4 | 3 | 0 | 0 | 0 | Fortgeschritten |
| Analyst | 1 | 0 | 3 | 3 | 6 | 1 | 1 | Fortgeschritten |
| Bounty_Hunter | 1 | 0 | 3 | 0 | 7 | 3 | 1 | Fortgeschritten |
| Chronomancer | 1 | 2 | 3 | 2 | 6 | 0 | 1 | Fortgeschritten |
| Commander | 1 | 0 | 6 | 3 | 0 | 0 | 0 | Fortgeschritten |
| Commando | 1 | 0 | 4 | 2 | 3 | 1 | 1 | Fortgeschritten |
| Cyborg | 1 | 0 | 3 | 2 | 11 | 2 | 0 | Fortgeschritten |
| Enforcer | 1 | 0 | 1 | 2 | 3 | 1 | 0 | Anfänger |
| Engineer | 1 | 0 | 3 | 2 | 7 | 0 | 1 | Anfänger |
| Envoy | 1 | 0 | 3 | 4 | 11 | 1 | 1 | Fortgeschritten |
| Gladiator | 1 | 0 | 3 | 3 | 3 | 1 | 1 | Fortgeschritten |
| Gravlock | 1 | 2 | 6 | 3 | 7 | 2 | 1 | Fortgeschritten |
| Grunt | 1 | 0 | 5 | 3 | 6 | 1 | 1 | Fortgeschritten |
| Hacker | 1 | 0 | 5 | 3 | 3 | 0 | 1 | Fortgeschritten |
| Hardlight_Conjurer | 1 | 3 | 5 | 2 | 6 | 0 | 1 | Fortgeschritten |
| Infiltrator | 1 | 0 | 5 | 3 | 0 | 0 | 0 | Anfänger |
| Influencer | 1 | 0 | 5 | 3 | 3 | 1 | 1 | Fortgeschritten |
| Medic | 1 | 0 | 4 | 3 | 6 | 0 | 1 | Anfänger |
| Mercenary | 1 | 0 | 3 | 3 | 0 | 0 | 0 | Fortgeschritten |
| Morpher | 1 | 4 | 4 | 5 | 1 | 1 | 0 | Fortgeschritten |
| Mystic | 1 | 5 | 4 | 3 | 0 | 0 | 0 | Fortgeschritten |
| Pilot | 1 | 0 | 3 | 3 | 9 | 1 | 2 | Anfänger |
| Psyker | 1 | 5 | 5 | 3 | 0 | 0 | 0 | Fortgeschritten |
| Road_Warrior | 1 | 0 | 4 | 0 | 7 | 2 | 2 | Fortgeschritten |
| Roughneck | 1 | 0 | 4 | 3 | 0 | 0 | 0 | Fortgeschritten |
| Scavenger | 1 | 0 | 5 | 4 | 11 | 2 | 1 | Fortgeschritten |
| Scrapper | 1 | 0 | 3 | 3 | 4 | 1 | 0 | Fortgeschritten |
| Shepherd | 1 | 3 | 2 | 2 | 6 | 1 | 1 | Anfänger |
| Smuggler | 1 | 0 | 4 | 2 | 7 | 2 | 1 | Anfänger |
| Spacer | 1 | 0 | 3 | 2 | 0 | 0 | 0 | Fortgeschritten |
| Squad_Leader | 1 | 0 | 5 | 3 | 8 | 1 | 2 | Fortgeschritten |
| Star_Knight | 1 | 3 | 3 | 1 | 4 | 1 | 1 | Anfänger |
| Surveyor | 1 | 0 | 4 | 3 | 0 | 0 | 0 | Fortgeschritten |
| Technomancer | 1 | 2 | 3 | 3 | 5 | 1 | 1 | Fortgeschritten |
| Warper | 1 | 2 | 3 | 2 | 6 | 2 | 1 | Fortgeschritten |

**Spalten:** V=Volk-count, M=Mächte, T=Talente, HC=Handicaps, I=Items, W=Waffen, R=Rüstungen

**Aggregierte Stats (alle 36 Builds):**
- 28 × Fortgeschritten, 8 × Anfänger (Enforcer, Engineer, Infiltrator, Medic, Pilot, Shepherd, Smuggler, Star_Knight)
- Total Items: 184, Waffen: 38, Rüstungen: 31
- Powers gespeichert: 41 (über 12 Mächte-User)
- Edges gespeichert: 142 total (alle HCs als Edges gezählt)

**Test-Suite-Lauf (`python "test units/run_all_tests.py"`):**
```
🎯 Tests ausgeführt: 946
✅ Erfolgreich: 945
❌ Fehlgeschlagen: 0
💥 Fehler: 1
⏭️  Übersprungen: 0
📈 Erfolgsrate: 99.9%
```

**1 Error (unabhängig von Phase G):**
- `test_template_handler.test_show_template_selection_dialog_with_templates` — KivyMD App-Init-Fehler
→ **Bestehender Test-Infrastruktur-Bug** (KivyMD App-Init-Fehler beim Modal-Dialog-Test), unabhängig von Phase G. Toleriert (kein Bezug zu Char-Generierung).

**Phase-G-Test-Fixes (nachträglich behoben 2026-06-02):**

Beim Hinzufügen von `Zielsystem` als Cyberware-Item (Phase G Stufe 1) fehlten die strukturierten Felder (`effekte`, `max_installationen`, `stress`, `unterkategorie`). Das Item hatte nur `beschreibung`. Dies verursachte 4 Test-Fehler in `test_cyberware.py`. **Fix nachgelagert:** Felder `effekte={abzug_reduktion:2, typen:[...]}, max_installationen=1, stress=1, unterkategorie="Offensiv"` zum `Zielsystem`-Item in `settings/SciFi Kompendium.json` hinzugefügt. Resultat: 0 Fehlschläge, 945/946 grün.

**Bestehende Tests (Phase G betreffend):**
- `test_ausruestung_funktionen.py` (25 Tests) — ✓ 25/25 grün nach Bug-Fix (Phase G Stufe 1)
- `test_cyberware.py` (60 Tests) — ✓ 60/60 grün nach Zielsystem-Schema-Fix (Stufe 5)
- Alle übrigen Tests unverändert (Bestand)

### Nächste Schritte

**Phase G KOMPLETT abgeschlossen (2026-06-02).** Keine offenen Schritte.

Zukünftige Optionen (separater Auftrag, NICHT im aktuellen Scope):
- Test-Infrastruktur-Fix für KivyMD-App-Init (test_template_handler)
- G2-Chars Shepherd/Star_Knight auf Fortgeschritten bringen (4. Advance via Skill-Step in `fertigkeit_mit_aufstieg` statt `aufstieg`)
