# Archetypen-Build — Skripte, Reihenfolge & Nutzung

Dieses Dokument beschreibt, **mit welchen Skripten** die mitgelieferten Archetypen
(`chars/Archetypen/Archetyp_*.json`) erzeugt werden und **in welcher Reihenfolge** sie
laufen müssen. Alle Build-Skripte liegen in `logs/` (sind getrackt) und bauen die
Archetypen **headless wie ein echter User** über den `CharakterController` (via
`driver.py` aus dem Skill `.claude/skills/archetyp-erstellen`) — **nicht** über den
Template-Auto-Generator. Ziel ist sowohl die Datenerzeugung als auch das Aufdecken
von Code-/Daten-Bugs.

> Hintergrund/How-To zum Treiber: `.claude/skills/archetyp-erstellen/SKILL.md`
> und der Referenz-Skill `wuerfel-werte-logik`.

---

## 0. Gemeinsame Ausführungsregeln (für ALLE Skripte)

```bash
# Immer aus dem Repo-Root, mit Dummy-Videotreiber:
SDL_VIDEODRIVER=dummy timeout 400 python3 logs/<skript>.py 2>/dev/null
```

- **Aus dem Repo-Root ausführen** (die Skripte erwarten relative Pfade wie `chars/…`, `Texte/…`).
- **`SDL_VIDEODRIVER=dummy` setzen** — headless ohne echtes Fenster.
- **NIEMALS `KIVY_WINDOW=mock`** — der Mock-Provider bricht beim Import von
  `kivymd.font_definitions` ab (`sp(24)` → `sys.exit(1)`).
- **Exit-Code ignorieren** — Kivy-Teardown liefert oft `1`, obwohl alles lief.
  Maßgeblich sind die geschriebenen **JSON-Berichte + Trace-Dateien** (`logs/*_bericht.json`,
  `logs/*_trace.txt`), nicht stdout (durch Kivy-Logs verschmutzt).
- **Tool-/Prozessaufrufe nicht massiv parallelisieren** — vereinzelt verstümmelte Ausgaben.
- Erzeugte Archetypen landen unter `chars/Archetypen/Archetyp_<Setting>_<Name>_A.json`.
  `chars/` ist als Datenverzeichnis getrackt; **Git ist das Sicherheitsnetz** — vor größeren
  Neuläufen ggf. Backup (`_backup_*`-Ordner werden ignoriert).

---

## 1. Pipelines pro Setting

| Setting | Archetypen | Build-Skript(e) — **in dieser Reihenfolge** |
|---|---|---|
| **Fantasy Kompendium** | 36 | 1. `build_fk_batch1_fixed.py` … `build_fk_batch5_fixed.py` (je 6) + `build_fk_batch6.py` (6)  → 2. `build_fk_anomalie_fix.py`  → 3. `fill_budget_gaps.py` |
| **SciFi Kompendium** | 30 | 1. `build_scifi_batch1.py` + `build_scifi_batch2.py` + `build_sfc_phase_g.py`  → 2. `fill_budget_gaps.py` |
| **Deadlands** | 24 | 1. `deadlands_build.py`  → 2. `fill_budget_gaps.py` |
| **Horror Kompendium** | 36 | 1. `build_horror_all.py`  → 2. `fill_horror_maechte.py` (fehlende Bogen-Mächte) |
| **Rippers** | 13 | `build_rippers_archetypen.py` (einstufig) |
| **50 Fathoms** | 13 | `build_50f_archetypen.py` (einstufig) |
| **Superkräfte Kompendium** | 11 | `build_supers.py` (einstufig, **SKP-System** — s.u.) |
| **SWAE / HeXXen 1773** | 10 / 4 | `build_swae_hexxen_fixed.py` |
| **Savage Pathfinder** | 30 | **Set 2/3** (Karten-Archetypen): Novice-Basis via `build_spf_set23_v2.py` → Seasoned via `build_spf_set23_seasoned.py`. **Ikonen** (Anfänger): `finalize_spf_iconics.py`. Siehe Abschnitt 6a. |
| **Savage Aventurien** (DSA) | 5 | Master `build_all_5_aventurien.py` ruft `build_{alissa,furun,radrosch,tallula,ssrrhyl}_aventurien.py`; `build_egnus_aventurien.py` separat |

---

## 2. Mehrstufige Pipelines im Detail

Diese drei Settings brauchen **nach** dem Roh-Build noch Nachbearbeitungs-Stufen.
**Nur die Batches laufen reicht NICHT.**

### 2.1 Fantasy Kompendium (3 Stufen)

```bash
for n in 1 2 3 4 5; do SDL_VIDEODRIVER=dummy python3 logs/build_fk_batch${n}_fixed.py 2>/dev/null; done
SDL_VIDEODRIVER=dummy python3 logs/build_fk_batch6.py        2>/dev/null   # 6 weitere
SDL_VIDEODRIVER=dummy python3 logs/build_fk_anomalie_fix.py  2>/dev/null   # Stufe 2
SDL_VIDEODRIVER=dummy python3 logs/fill_budget_gaps.py       2>/dev/null   # Stufe 3
```

- **Stufe 2 — `build_fk_anomalie_fix.py`** baut Krieger/Assassinin/Amazone NEU mit den
  **korrekten Talent-Keys** (die Batches bauen dort bewusst noch falsche Näherungen):
  - „Take the Hit" → `Treffer einstecken`
  - „Sneak Attack" → `Hinterhältiger Angriff`
  - „Formation Fighter" → `Formationskämpfer`
  Läuft die Stufe nicht, bleiben diese drei Archetypen mit falschen Talenten.
- **Stufe 3 — `fill_budget_gaps.py`** (s. Abschnitt 3).

### 2.2 SciFi Kompendium (2 Stufen)

```bash
SDL_VIDEODRIVER=dummy python3 logs/build_scifi_batch1.py  2>/dev/null
SDL_VIDEODRIVER=dummy python3 logs/build_scifi_batch2.py  2>/dev/null
SDL_VIDEODRIVER=dummy python3 logs/build_sfc_phase_g.py   2>/dev/null
SDL_VIDEODRIVER=dummy python3 logs/fill_budget_gaps.py    2>/dev/null
```

### 2.3 Deadlands (2 Stufen)

```bash
SDL_VIDEODRIVER=dummy python3 logs/deadlands_build.py   2>/dev/null   # alle 24 (build()-Schleife)
SDL_VIDEODRIVER=dummy python3 logs/fill_budget_gaps.py  2>/dev/null   # Budget-Lücken
```

Quelle/Bogen: `Texte/US85040PDF_Deadlands_Archetypen-Set_meta.pdf` (deutschsprachig).

### 2.4 Savage Pathfinder (Sanierung 2026-06, mehrstufig)

Pathfinder war das unsauberste Setting (Skripte reproduzierten den committeten Stand nicht;
committete Daten halb-finalisiert). Sanierung in 4 Phasen:

**Quellen** (EN-Karten + DE-Grundregelwerk):
- Set 2/3 Karten: `Texte/Pathfinder®_for_Savage_Worlds_Archetype_Cards_Set_2/3.pdf` (EN, je Novice+Seasoned).
- Ikonen: `Texte/SWPF_Grundregelwerk.txt` (DE, „ANFÄNGER, IKONISCH…", sauber strukturiert).

**Extraktoren → Target-Specs unter `Texte/`:**
```bash
python3 logs/extract_spf_cards.py     # -> SWPF_Archetype_Cards_target.{json,txt}  (Traits, EN->DE)
python3 logs/extract_spf_edges.py     # -> SWPF_Archetype_Cards_edges.{json,txt}   (Edges/Mächte + Delta)
python3 logs/extract_spf_iconics.py   # -> SWPF_Ikonen_target.{json,txt}            (Ikonen, DE)
```
Spalten-Falle der Karten: zwei interleavte Spalten; Traits links (`Name dX`), Edges/Mächte rechts
(ab Spalte ≥58), vertikal versetzt → erst ab dem rechtsspaltigen `RANK:` erfassen.

**Build (Set 2/3 → Seasoned) + Finalize (Ikonen → Anfänger):**
```bash
SDL_VIDEODRIVER=dummy python3 logs/build_spf_set23_seasoned.py  2>/dev/null  # Novice-Basis + Δ-Aufstiege
SDL_VIDEODRIVER=dummy python3 logs/finalize_spf_iconics.py      2>/dev/null  # char_gen + Rang=Anfänger
```
- `build_spf_set23_seasoned.py`: lädt committete Novice-Basis (= Novice-Karte, verifiziert), hebt
  Traits auf Seasoned, ergänzt Seasoned-Edges/-Mächte (EN→DE-Map im Skript), backfillt fehlende
  Novice-Mächte. Idempotent, Seasoned-Cap. **17/17 trait-deckungsgleich.**
  - **HP-Ökonomie (Phase 0) + Doppelkosten-Fix** (wie `fill_budget_gaps.py`): Seasoned-Lücken werden
    ZUERST aus Rest-Punkten + ungenutzten Handicap-Punkten gefüllt (solange char_gen offen), erst der
    Rest per Aufstieg (mit `while < kosten`-Top-up für Doppelschritte). Senkt die Aufstiege bei Chars
    mit HP-Resten (Balazar/Brokar/Kira: je 1 Aufstieg gespart; Kira Fortgeschritten→Anfänger).
  - ⚠ **Re-Run-Falle:** Das Skript ist idempotent gegenüber dem committeten (Seasoned-)Stand → ein
    erneuter Lauf füllt KEINE Lücken (keine Gaps mehr) und die HP-Ökonomie greift NICHT. Um die
    Phase-0-Wirkung zu reproduzieren, zuerst die **Novice-Basis** der betroffenen Chars
    wiederherstellen: `git show 0500a55~1:<pfad> > <pfad>` (Stand VOR der Sanierung, char_gen=False),
    dann `build_spf_set23_seasoned.py` laufen lassen.
- `finalize_spf_iconics.py`: 11 Ikonen, nur Abschluss + Rang (Daten waren korrekt, 10/11 Attr = Quelle).

**Per Render+Crop der Originalkarten gelöst (Methode: [pdf-bogen-audit]):**
- **Feiya** (Set 2/3): Seasoned-Karte war im pdftotext korrupt (Spalten-Bleed) → korrekte Werte aus
  Render+Crop (Set 3, S.7) als Override im Build (`TRAITS['Feiya']['Seasoned']` etc.), kein SKIP mehr.
- **Sajan**: Stärke W8 (Render+Crop Grundregelwerk S.61 bestätigt, designter Iconic-Wert über
  Standard-Budget) — als Override in `finalize_spf_iconics.py` verankert (Punkt-Build lieferte W6).

**Bekannte offene Punkte (Quellen-/Budget-bedingt, dokumentiert):**
- **Darla_A**: klassen-Variante ohne Kartenquelle (Karte ist „NO CLASS" = Darla_ohneKlasse) → unverändert.
- **4 Edges nicht EN→DE-auflösbar** (kein sicherer Key, NICHT substituiert): bane, Enhance, Hex(cackle), Trapping.
- **6 Set-2/3 bleiben Anfänger** (Karten-Δ <4 Aufstiege bzw. fehlender Edge wäre der 4.).
- **Naming angeglichen:** `Gnor`→`Gnorr` (Karte), alle Ikonen auf `_A`-Suffix vereinheitlicht.

---

## 3. Gemeinsamer Finalizer: `fill_budget_gaps.py`

Schließt **Budget-Lücken** (Bogen-Werte, die der reguläre Punkte-Build nicht erreicht).
Eigenschaften:

- **Idempotent**, hebt **nur an** (senkt nie, überschreitet nie den Bogenwert).
- **Phase 0 — freie Chargen-Währung zuerst:** Lücken werden ERST aus übrigen Attribut-/
  Fertigkeitspunkten UND ungenutzten **Handicap-Punkten** gefüllt (Chargen wird kurz
  wiedereröffnet, `steigere_*` zieht Pkt-Pool, sonst HP: 2 HP/Attribut, 1–2 HP/Fertigkeit),
  erst der Rest per **Aufstieg** (Phase 1/2). So werden keine Handicap-Punkte verschenkt
  (sie sind nach char_gen eingefroren) und es bleibt mehr Aufstiegs-Budget, um bogentreue
  Fertigkeiten zu erreichen, die sonst am Cap hängen blieben.
- **Doppelkosten-bewusster Aufstiegs-Top-up:** Vor jedem Fertigkeitsschritt wird geprüft, ob er
  doppelt kostet (Fertigkeit ≥ regierendes Attribut → 1.0 statt 0.5 Aufstiege); der Pool wird
  per `while < kosten: increase_aufstiege` aufgefüllt. (Früher nur `< 0.5` → ein Doppelschritt
  bei genau 0.5 Restaufstieg blieb „stuck"; das verlor z.B. Road_Warrior Überleben d8.)
- Strikt im **Seasoned-/Fortgeschritten-Cap** (ausgegebene Aufstiege < 8).
- Vergleicht jeden gespeicherten Archetyp gegen den jeweiligen **PDF-Bogen**.
- Deckt aktuell **SciFi Kompendium, Fantasy Kompendium** (englische Bögen, `agility d8`-Muster)
  **und Deadlands** (deutscher Bogen, `Geschicklichkeit W8`, eigener Parser `parse_german_sheets`).
- Report: `/tmp/gapfill_report.txt` (pro Archetyp: angehobene Werte / offene Reste).
- **Reihenfolge:** immer **als LETZTE Stufe** nach dem jeweiligen Roh-Build laufen lassen.

> ⚠️ `parse_sheet` (pdftotext) liest Würfelwerte **nicht zuverlässig** (d4/d6/d8-Verwischung,
> s. [[pdf-bogen-audit-methode]]). Es taugt als Build-Ziel, aber NICHT als Verifikations-Orakel.
> Bogen-Treue final immer per **Render+Crop** der Original-PDF prüfen (`pdftoppm -r 200` + crop+zoom).

Neues Setting hinzufügen: PDF-Bogen + Header-Mapping ergänzen; bei deutschem Bogen die
`parse_german_sheets`-Schleife wiederverwenden (Header = Archetypname in Großbuchstaben).

> **Horror** braucht `fill_budget_gaps.py` **nicht**: dort gibt es **0 Attribut-/Fertigkeits-Defizite**
> (die wenigen Diffs sind Volks-Überschüsse IST>SOLL). Horrors einzige Aufstiegs-relevante Lücke
> sind **fehlende Mächte** → separater Schritt `fill_horror_maechte.py` (s.u.).

### 3b. Mächte-Finalizer Horror: `fill_horror_maechte.py`

Pendant zu `fill_budget_gaps.py`, aber für **Mächte** statt Traits. Hintergrund: einige
Caster-Archetypen haben **freie Macht-Slots** (`anzahl_maechte` > belegt), deren Bogen-Mächte der
Build aber nicht eingetragen hat. Das Skript füllt sie (kostenfrei in freie Slots; reicht der Slot
nicht, **ein `Neue Mächte`-Aufstieg im Seasoned-Cap**, dann erneut). Idempotent, fügt nur hinzu.

```bash
SDL_VIDEODRIVER=dummy python3 logs/build_horror_all.py     2>/dev/null   # Stufe 1
SDL_VIDEODRIVER=dummy python3 logs/fill_horror_maechte.py  2>/dev/null   # Stufe 2
```

Stand 2026-06-14: schließt 7/11 Lücken (Exorcist, Witch, Magician, Mummy). Offen bleibt nur
**Demonologist (Monstrous)** — Super-Archetyp mit vollen Slots (3/3) und bereits 11 Aufstiegen
(über Seasoned), daher bewusst **nicht** erzwungen.

---

## 4. Setting-Spezialfall: Superkräfte Kompendium (SKP)

`build_supers.py` nutzt **nicht** das normale Punktesystem, sondern **Superkraftpunkte (SKP)**
über `functions/superkraft_funktionen.py` (nicht im `driver` gekapselt). Machtstufe I–V =
15/30/45/60/75 SKP, Kraftobergrenze je Kraft = 1/3 (Stufe III = 15). Attribute/Fertigkeiten/
Handicaps/Talente laufen weiter über die normalen Treiber-Methoden. Details:
`.claude/skills/archetyp-erstellen/SKILL.md` (Abschnitt Superkräfte). Quelle: englische
„Super Powers Archetype Cards" (alle POWER LEVEL III), 11 von 37 Karten gebaut.

**Obergrenze-Fix + offene App-Themen (2026-06-14):**
- **Behoben:** Das Hintergrundtalent **„Der Beste"** hebt die Obergrenze auf 1/2 (Stufe III = 22).
  Es muss VOR der Kräfte-Wahl gesetzt werden — `build_supers.py` tat das zu spät (D-Advances),
  wodurch Feuervogel (Fire Bird) seinen 20-SKP-Fernkampf verlor. Jetzt in Schritt 5 gesetzt → 45/45.
- **Behoben (Mehrfachwahl):** Panzer/Schlaeger haben `Superattribut` 20. Das Kompendium erlaubt
  „fünfmal Superattribut → 5 Stufen", aber `waehle_superkraft` lehnte jede zweite Instanz ab. Fix:
  Kräfte mit Setting-Kosten `"X/Stufe"` sind wiederholbar (Kosten stapeln auf, Obergrenze pro Stufe);
  Build-SPEC `Superattribut 20 → 2×10`. Panzer/Schlaeger jetzt 45/45. Tests in `test_superkraft_model.py`.
- **Offen (RAW-Spannung):** Sprinter `Geschwindigkeit 16` ist EINE Kraft (`3-17`, kein `/Stufe`) >
  Obergrenze 15 ohne „Der Beste" → 29/45. Nur durch Obergrenze-Lockerung lösbar (bewusst nicht gemacht).
  Stand: 10/11 Archetypen 45/45.

---

## 5. Verifikations- & Audit-Skripte (bauen nichts)

| Skript | Zweck |
|---|---|
| `logs/deadlands_pdf_vergleich.py` | Deadlands-JSONs gegen PDF-Bogen (Attribute/Fertigkeiten/Talente). Normalisiert AH-Kürzel, AH-Paketmechanik (Mächte/Machtpunkte/Rückschlag), `Sprache (X)`→`Sprache`. |
| `logs/soll_ist_ausruestung.py` | Bogen-SOLL vs. Char-IST Ausrüstung; deutscher Parser für Deadlands (AUSRÜSTUNG≠GEAR). |
| `logs/_deadlands_offen.py` | Listet offene Bogen-Ausrüstung je Deadlands-Archetyp (Katalog vs. fehlend). |
| `logs/check_pdf_gear.py`, `logs/check_fehlende_ausruestung.py` | Ausrüstungs-Abgleich/-Lücken. |
| `logs/check_doppelkosten.py` | Prüft alle Archetyp-JSONs auf doppelt bezahlte Skills. |
| `logs/gen_soll_ist_tabelle.py` | Erzeugt SOLL/IST-Übersichtstabelle. |

**Reproduzierbarkeits-Check (nach Refaktorierungen):** Pipeline neu laufen lassen, dann
`git diff chars/Archetypen/Archetyp_<Setting>_*` — 0 Abweichungen = Build-Verhalten erhalten.

---

## 6. PDF-Textquellen & Extraktion

Die Bögen/Archetyp-PDFs liegen unter **`Texte/`**. Extrahierte Texte zur Wiederverwendung
liegen **ebenfalls unter `Texte/`** (manche Roh-Extraktionen zusätzlich unter
`logs/pdf_extracted/`, das ist gitignored).

| Setting | PDF (in `Texte/`) | Extrahierter Text | Sprache |
|---|---|---|---|
| Fantasy Kompendium | `SW Fantasy Kompendium Archetypen.pdf` | `…Archetypen.txt` | **EN** (Fantasy Companion) → EN→DE-Mapping |
| SciFi Kompendium | (Science Fiction Companion) | `Science_Fiction_Companion_Archetypes_(SWADE).txt` | **EN** → EN→DE-Mapping |
| Deadlands | `US85040PDF_Deadlands_Archetypen-Set_meta.pdf` | `…meta.txt` | **DE** (deutscher Bogen) |
| Horror Kompendium | `Horror_Companion_Archetypes_(SWADE).pdf` | `Horror_Companion_Archetypes_(SWADE)_raw.txt` | **EN** → EN→DE-Mapping |

### Waren Skripte zur Konsolidierung nötig?

- **Deadlands (DE):** Bogen ist sauber strukturiert → direkt parsebar (`deadlands_pdf_vergleich.py`,
  Parser in `fill_budget_gaps.py`). **Kein** Spezial-Aufwand.
- **Fantasy/SciFi (EN):** pdftotext brauchbar genug; `fill_budget_gaps.py` parst die EN-Bögen
  (`agility d8`-Muster). EN→DE-Mapping nötig.
- **Horror (EN) — Sonderfall:** Das PDF hat ein stark gestyltes Magazin-Layout.
  `pdftotext` (default) **und** `pdftotext -layout` liefern **unbrauchbaren Buchstabensalat**.
  Nur **`pdftotext -raw`** gibt die Werte-/Edge-/Gear-Blöcke in Lesereihenfolge — die gestylten
  Archetyp-**Titel** zerfallen dort aber teils in Einzelzeichen, und `Agility d6` vs. `Agility⏎d6`
  ist uneinheitlich. **Eine vollautomatische Konsolidierung war NICHT zuverlässig möglich.**
  → Die maßgebliche, konsolidierte Datenfassung sind die **hand-transkribierten Python-Dicts**
  in `logs/build_horror_all.py` (pro Archetyp `attribute`/`fertigkeiten`/`talente`/…).
  Stichprobe 2026-06-14 (Ghost Hunter, Nerd): Transkription deckungsgleich mit dem PDF.

### Extraktions-Skript (Wiederverwendung)

```bash
python3 logs/extract_horror_text.py   # -> Texte/Horror_Companion_Archetypes_(SWADE)_raw.txt
```

`logs/extract_horror_text.py` ruft `pdftotext -raw`, setzt einen erklärenden Header und legt den
Text reproduzierbar unter `Texte/` ab. **Faustregel für stark gestylte PDFs: `-raw` statt
`-layout`** — und Würfelwerte nie aus Low-Res ableiten (s. Domain-Regeln).

---

## 7. Wichtige Domain-Regeln (Kurz)

- **Reihenfolge im Build-Loop:** (Pathfinder: freies Klassentalent →) Handicaps (Major zuerst!)
  → Volk → ALLE freien Volkswahlen → **Attribute komplett** → Fertigkeiten → Talente → Mächte
  → Ausrüstung. Attribute VOR Fertigkeiten, sonst Doppelkosten (Fertigkeit > Attribut).
- **Auto-Einträge nie manuell** in den Build-Loop: AH-Auto-Handicaps, Klassentalent-Bonus-Talente,
  Volks-Racials. Sie gehören ins SOLL (Vergleich), aber das System setzt sie selbst.
- **Keine Ersatz-Elemente.** Fehlt ein exakter Key, als FEHLT dokumentieren — nie ein ähnliches
  Talent/Handicap/Macht einsetzen (verfälscht den Test des offiziellen Archetyps).
- **Bogen-PDF-Audit nur per Render+Crop+Zoom** prüfen, nie Low-Res/pdftotext für Würfelwerte
  (d4/d6/d8 verschwimmen).
- **Rang Fortgeschritten/Seasoned** = 4–7 ausgegebene Aufstiege. Manche Archetypen erreichen alle
  Bogenwerte mit < 4 Aufstiegen und bleiben dadurch rechnerisch „Anfänger" — kein Stat-Bug.
