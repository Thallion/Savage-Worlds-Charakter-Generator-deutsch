---
name: archetyp-erstellen
description: Erstellt einen offiziellen Archetyp Schritt für Schritt mit dem Charakter-Tool – wie ein echter User, aber headless über den CharakterController. Aufrufen, wenn der User Screenshots eines Archetyps in screenshots/ ablegt und ihn nachbauen lassen möchte, um Fehler im Code zu finden. NICHT den Template-Auto-Generator verwenden.
allowed-tools: Read Write Bash Glob Grep
---

# Archetyp mit dem Charakter-Tool erstellen (Bug-Finder)

**Zweck:** Einen offiziellen Archetyp aus Screenshots **wie ein normaler User** nachbauen –
über dieselben Aktionen, die die GUI auslöst (`CharakterController` + `volk_funktionen`),
nur headless und schnell. Jeder Schritt wird einzeln geprüft; Auffälligkeiten landen in einer
Logdatei. Ziel ist **nicht** ein perfekter Charakter, sondern **Fehler im Code zu finden**.

**WICHTIG:** Nicht den `AutoCharacterGenerator` / Template-Auto-Generator benutzen. Wir wollen
genau die echten User-Code-Pfade testen.

**Argumente:** `$ARGUMENTS` — Pfad(e) zu Screenshot(s) in `screenshots/`. Das **Setting steht im
Dateinamen** (z.B. `Savage Pathfinder Mönch 1.png` → Setting „Savage Pathfinder"). Statt
Screenshots kann auch eine Textvorlage (z.B. `Texte/<Setting> Archetypen.txt`) mit mehreren
Archetypen übergeben werden — dann pro Archetyp einen Build im selben Skript bauen.

---

## Wie der Treiber funktioniert (einmal verstehen)

`driver.py` in diesem Skill-Ordner startet den `CharakterController` headless und kapselt jede
User-Aktion so, dass **Vorher/Nachher-Punkte automatisch protokolliert** werden. Jede Aktion
gibt ein dict zurück (`{ok, aktion, kosten, kostenart, punkte, vermoegen, warnung}`).

**Prozess-Isolation:** Jeder Bash-Aufruf ist ein **eigener Python-Prozess** – der Zustand
überlebt das nicht. Deshalb: **ein einziges Build-Skript** schreiben, das alle Schritte in einem
Prozess ausführt und am Ende einen JSON-Bericht + Logdatei rausschreibt. Danach den Bericht mit
dem **Read-Tool** lesen.

**Zuverlässigkeits-Regeln (hart erkämpft):**
- Immer **aus dem Repo-Root** ausführen, mit `SDL_VIDEODRIVER=dummy`.
- **NIEMALS `KIVY_WINDOW=mock` setzen** – der Mock-Provider erfüllt `EventLoop.ensure_window()`
  nicht, `kivymd.font_definitions` ruft `sp(24)` beim Import → `sys.exit(1)`. Der Standard-sdl2-
  Provider mit dummy-Driver funktioniert headless. (driver.py macht das schon richtig.)
- **Exit-Code ignorieren** – Kivy-Teardown liefert oft `1`, obwohl alles lief. Maßgeblich ist der
  JSON-Bericht.
- Bash-Stdout ist durch Kivy-Logs verschmutzt → **immer Bericht/Logdatei per Read-Tool lesen**,
  nie stdout interpretieren.
- **Tool-Aufrufe NICHT massiv parallelisieren.** Viele parallele Bash/Read-Calls liefern
  vereinzelt verstümmelte/halhluzinierte Ausgaben. Lieber sequenziell und jeden Zwischenstand
  in eine `/tmp`-Datei schreiben, dann per Read-Tool prüfen. Im Zweifel einen Wert neu ermitteln.
- Die **Event-Historie ist headless leer** → der „Historie-View" wird hier durch das
  **Schritt-Protokoll des Treibers** ersetzt (`bericht['schritte']`).

---

## SOLL-Dict: Was kommt woher?

Das `soll`-dict dient **ausschließlich** dem Diff-Vergleich am Ende (`s.diff(soll)`). Es enthält
den **erwarteten Endzustand**, also auch Einträge die **automatisch** vom System gesetzt werden.
Im Build-Skript selbst darf man diese Auto-Einträge **nicht nochmal manuell hinzufügen**.

### Quellen automatischer Einträge

| Quelle | Was wird auto gesetzt | Wo im SOLL | Im Build-Loop? |
|---|---|---|---|
| **AH (Arkaner Hintergrund)** | Handicaps: `Behindernde Rüstung_*`, `Materialkomponenten`, `Verderbnis`, `Tick` u.a. (je nach AH) | ✓ im SOLL | ✗ **NICHT** manuell |
| **Pathfinder-Klassentalent** | Bonus-Talente: z.B. Mönch → `Waffenloser Schlag`, `Betäubende Fäuste`, `Kämpferische Disziplin`, `Beweglichkeit`; Waldläufer → `Erzfeind`, `Bevorzugtes Gelände`, `Wildnis durchqueren` | ✓ im SOLL | ✗ **NICHT** manuell |
| **Klassentalent-Auto-Handicaps** | z.B. Waldläufer → `Rüstungsbeschränkung_mittelschwer`; Mönch → `Rüstungsbeschränkung_jede` | ✓ im SOLL | ✗ **NICHT** manuell |
| **Volk-Racial** | z.B. Elf → `Zwei linke Hände`, `Nachtsicht`; Gestaltwandler → `Geheimnis_schwer` (in special_effects, **nicht** selected_handicaps!) | Nur wenn in selected_handicaps | ✗ **NICHT** manuell |
| **Superkräfte-Setting** | `Superkräfte`-Edge ist bei neuen Charakteren bereits in `selected_talente` (auto) | ✓ im SOLL | ✗ **NICHT** manuell (erneutes Wählen → False) |

### Grundregel

```
soll['handicaps']   = ALLE am Ende erwarteten Handicaps (manuell + auto)
manual_handicaps    = nur die manuell zu setzenden (für den Build-Loop)
```

**Beispiel: Sajan (Mönch)**
```python
# Im SOLL: alle Handicaps + alle Talente inkl. Mönch-Bonus-Talente
soll = {
    'handicaps': ['Heroisch', 'Loyal', 'Schwur_leicht',
                  'Rüstungsbeschränkung_jede'],        # ← auto durch Mönch
    'talente':   ['Mönch', 'Flink', 'Lieblingswaffe',
                  'Waffenloser Schlag', 'Betäubende Fäuste',  # ← auto durch Mönch
                  'Kämpferische Disziplin', 'Beweglichkeit'],
}

# Im Build: NUR die manuell zu setzenden Handicaps
for h in ['Heroisch', 'Loyal', 'Schwur_leicht']:   # ← Rüstungsbeschränkung_jede WEGLASSEN
    s.handicap(h)
```

### Auto-Einträge herausfinden

Nach `pathfinder_klassentalent()` oder `volk()` aufrufen:
```python
s.zeige_auto_eintraege(vor_snap)   # zeigt was neu hinzukam
```
Oder: `m(str(s.ch.selected_talente))` + `m(str(list(s.ch.selected_handicaps)))` nach jeder Aktion.

---

## Ablauf

### 1. Screenshot(s) / Textvorlage lesen und Soll-Werte extrahieren

Lies alle übergebenen Screenshots mit dem **Read-Tool**. Extrahiere ein `soll`-dict:
Setting (aus Dateiname), Volk + Volkseigenarten, Attribute (4/6/8/10/12), Fertigkeiten,
Handicaps (mit Stufe, **inkl.** AH-Auto-Handicaps und Klassentalent-Auto-Handicaps),
Talente (**inkl.** Klassentalent-Bonus-Talente), Mächte, Ausrüstung, Rang.

Niedrig aufgelöste Screenshots ruhig dem User gegenüber transparent auslesen und unsichere Werte
benennen.

### 2. Namen gegen echte Daten-Keys auflösen

Namen müssen **exakt** den Keys entsprechen. Vor dem Build-Skript nachschlagen:

```bash
SDL_VIDEODRIVER=dummy python3 - <<'PY' > logs/keys.json 2>/dev/null
import sys; sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d, json
s = d.Sitzung('<SETTING>', 'KeyCheck')
print(json.dumps({k: sorted(getattr(s.ch, k)) for k in
      ['handicaps','talente','maechte','ausruestung','voelker','fertigkeiten']},
      ensure_ascii=False, indent=1))
PY
```

`logs/keys.json` per Read-Tool öffnen. **Handicaps** haben oft `_leicht`/`_schwer`-Suffixe
(z.B. `Schwur_leicht`). Um AH-Auto-Einträge zu sehen: Klassentalent/AH zuerst setzen, dann
`s.zeige_auto_eintraege(vor_snap)` aufrufen.

⚠️ **Deutsche Keys sind oft nicht die naive Übersetzung.** Englische Bögen → exakte DE-Keys erst
gegen `logs/keys.json` auflösen, nie raten. Beispiele (Superkräfte Kompendium): Marksman =
`Meisterschütze`, Quick = `Schnell`, Brawny = `Kräftig`, Counterattack = `Konter`, Extraction =
`Rückzug`, Sweep = `Rundumschlag`, Performance = `Darbietung`, Academics = `Geisteswissenschaften`,
Science = `Naturwissenschaften`. Schreib am besten ein kleines Resolver-Skript (Substring-Suche
gegen die Key-Listen), das fehlende Keys als „MISSING" ausgibt → echte Setting-Lücken vs.
Tippfehler trennen.

⛔ **NIEMALS ähnliche Talente/Handicaps/Mächte als Ersatz verwenden.** Gibt es für einen Bogen-
Eintrag keinen **exakt** entsprechenden Key, dann den Eintrag **als FEHLT/MISSING dokumentieren**
(`s.notiz(...)`) — **nicht** durch ein ähnliches/„nahes" Element ersetzen. Ein angenähertes Talent
(z.B. `Mean`→`Grimmig`, `Sneak Attack`→`Hinterhältiger Angriff`) verfälscht den Test: Es testet
dann nicht mehr den **offiziellen Archetyp**, sondern eine Eigenkreation, und versteckt echte
Daten-Lücken im Setting. Lieber eine ehrliche Lücke melden als einen „passend gemachten" Charakter.

### 3. Reihenfolge – WICHTIG

Verbindliche Reihenfolge:

1. **Pathfinder:** freies Klassentalent (bei anderen Settings weglassen).
2. **Handicaps** — nur die **manuellen** (keine AH-Auto-Handicaps, keine Volks-Handicaps).
   ⚠️ **Major-Handicaps zuerst** (2 HP) um das HP-Limit von 4 korrekt auszuschöpfen.
3. **Volk**.
4. **Volkseigenarten / freie Wahlen** – ⚠️ `volk_wahlmoeglichkeiten(volk)` aufrufen und **ALLE**
   `True`-Wahlen abarbeiten, nicht nur das freie Talent! Mensch hat z.B. **freies Talent UND
   freies Attribut** (je nach Setting). Das freie Attribut gibt einen **kostenlosen**
   Würfelschritt – wird es vergessen, fehlt am Ende genau dieses Budget.
5. **Attribute KOMPLETT auf Zielwerte** – erst mit regulären Punkten, dann **sofort** die
   restlichen Steigerungen mit **Handicap-Punkten**. ⚠️ **Attribute müssen ihre Zielwerte
   erreichen, BEVOR Fertigkeiten gesteigert werden.** Sonst kosten Fertigkeiten, deren
   regierendes Attribut noch zu niedrig ist, **doppelt** (Fertigkeit > Attribut = doppelte
   Kosten) und die Punktebilanz geht nicht auf.
6. **Fertigkeiten** steigern (jetzt mit korrekten, einfachen Kosten).
7. **Talente** (nur die, die nicht schon auto durch Klasse/Volk gesetzt wurden).
8. **Mächte** (falls vorhanden).
9. **Ausrüstung** (Geldmangel → trotzdem kaufen mit `force_bei_geldmangel=True`).
10. **Restabgleich:** verbleibende Differenzen prüfen; nur Fertigkeiten ggf. noch mit
    Handicap-Punkten nachziehen (Attribute sind in Schritt 5 schon fertig).

**Für Fortgeschrittene (D-Rank, Seasoned):** nach `s.ch.char_gen_completed = True` und
`increase_aufstiege(s.ch)` die D-Advances mit `ignore_rang_check=True` setzen. ⚠️ **Seasoned-/
höhere Archetypen mit vielen Edges/Kräften** lassen sich auf Rang Anfänger NICHT 1:1 nachbauen
(nur ~1 freier Edge-Slot, begrenzte SKP) – das ist **korrektes Verhalten**, keine Anomalie. Wer
den vollen Bogen will, muss zuerst abschließen + Aufstiege vergeben.

### 4. Build-Skript schreiben

`logs/build_<name>.py` nach dieser Vorlage:

```python
import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/<name>_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

def abschliessen(s, n_aufstiege):
    s.ch.char_gen_completed = True
    for _ in range(n_aufstiege): increase_aufstiege(s.ch)
    m(f"  → chargen abgeschlossen, {n_aufstiege} Aufstiege, Rang={s.ch.rang}")

soll = {
    'attribute':    {'Geschicklichkeit': 8, 'Konstitution': 8, 'Stärke': 6,
                     'Verstand': 6, 'Willenskraft': 6},
    'fertigkeiten': {'Athletik': 8, 'Heimlichkeit': 8, 'Kämpfen': 8, 'Einschüchtern': 6,
                     'Wahrnehmung': 6, 'Heilen': 4, 'Reiten': 4, 'Allgemeinwissen': 4, 'Überreden': 4},
    # Manuelle + auto-gesetzte Handicaps (auto: Rüstungsbeschränkung_jede durch Mönch-Talent)
    'handicaps':    ['Heroisch', 'Loyal', 'Schwur_leicht', 'Rüstungsbeschränkung_jede'],
    # Manuelle + auto-gesetzte Talente (auto: Waffenloser Schlag etc. durch Mönch)
    'talente':      ['Mönch', 'Flink', 'Lieblingswaffe',
                     'Waffenloser Schlag', 'Betäubende Fäuste', 'Kämpferische Disziplin', 'Beweglichkeit'],
    'maechte':      [],
}

# Separate Liste NUR für den Build-Loop (ohne auto-Einträge)
manual_handicaps = ['Heroisch', 'Loyal', 'Schwur_leicht']   # Rüstungsbeschränkung_jede kommt auto

try:
    import driver as d
    s = d.Sitzung('Savage Pathfinder', 'Sajan', protokoll='logs/<name>.log')

    vor = s.zustand()
    if s.ist_pathfinder():
        s.pathfinder_klassentalent('Mönch', ignore_voraussetzungen=True)   # 1
        m(f"  Auto-Einträge nach Klassentalent: {s.zeige_auto_eintraege(vor)}")
    for h in manual_handicaps:                                             # 2
        s.handicap(h)
    s.volk('Mensch')                                                       # 3
    m(f"  Volkswahlen: {s.volk_wahlmoeglichkeiten('Mensch')}")
    # 4  ALLE freien Volkswahlen! (vorher prüfen was das Volk bietet)
    s.volk_freies_attribut('Mensch', 'Stärke')
    s.volk_freies_talent('Mensch', 'Flink', ignore_voraussetzungen=True)

    # 5  Attribute KOMPLETT (regulär + Handicap) VOR den Fertigkeiten
    for a, z in soll['attribute'].items():
        s.attribut_auf(a, z)
    for a, z in soll['attribute'].items():
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte > 0:
            vor_val = s.ch.attribute[a].wuerfel.value
            s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value == vor_val: break
    m(f"  Nach Attributen: {s.punktestand()}")

    for f, z in soll['fertigkeiten'].items():                             # 6
        if f in s.ch.fertigkeiten:        # KeyError-Guard: fehlende Fert. als Notiz, nicht Crash
            s.fertigkeit_auf(f, z)
        else:
            s.notiz(f'FERTIGKEIT-KEY fehlt im Setting: {f}')
    m(f"  Nach Fertigkeiten: {s.punktestand()}")

    for t in soll['talente']:                                             # 7
        if t not in s.ch.selected_talente:
            s.talent(t, ignore_voraussetzungen=True)

    for mm in soll['maechte']:                                            # 8
        s.macht(mm)

    # 9  Ausrüstung
    for name, anz in [('Kampfstab', 1), ('Dolch', 1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Heiltrank (nicht im Katalog)')

    # Fortgeschrittene Archetypen (Seasoned): abschliessen + D-Advances
    # abschliessen(s, 4)
    # s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True)
    # s.macht('Heilung', ignore_rang_check=True)

    # 10  Restabgleich
    m(f"  Restpunkte: {s.punktestand()}")
    diff = s.diff(soll)
    m('DIFF: ' + str(diff['abweichungen']))
    s.speichern('chars/Archetypen/Archetyp_Savage_Pathfinder_<name>_A.json')
    b = s.bericht('logs/<name>_bericht.json')
    m('FERTIG anomalien=%d' % b['anomalien_anzahl'])
except BaseException as e:
    m('CRASH: %r\n%s' % (e, traceback.format_exc()))
tlog.close()
```

### 5. Ausführen

```bash
SDL_VIDEODRIVER=dummy timeout 200 python3 logs/build_<name>.py 2>/dev/null
```
Exit-Code ignorieren.

### 6. Bericht prüfen (jeder Schritt einzeln!)

`logs/<name>_bericht.json` + `logs/<name>_trace.txt` mit dem **Read-Tool** öffnen. Prüfe:
- **`anomalien`** – `ok: False` (Name falsch oder echter Bug), `EXCEPTION:` (immer ein Bug),
  Punkte-Auffälligkeiten.
- **Punktebilanz** in `endzustand.punkte`: gehen reguläre + Handicap-Punkte sauber auf?
- **`SOLL/IST-DIFF`**: Welche Werte weichen ab?
  - `ZUVIEL`: Auto-Einträge aus Klassentalent/AH → mit Bogen abgleichen, meist korrekt
  - `FEHLT`: Name falsch, Budget erschöpft, oder Auto-Eintrag geht in `special_effects` statt `selected_handicaps` (z.B. Gestaltwandler → `Geheimnis_schwer`)

### 7. Auffälligkeiten klassifizieren

- **Input-Problem** (falscher Name/Wert aus Screenshot) → korrigieren, neu laufen lassen.
  ⚠️ Ein `ok=False` bei korrekt aussehendem Namen ist **fast immer ein falscher Key**, kein Bug –
  erst gegen `logs/keys.json` prüfen, bevor man einen Code-Bug meldet.
- **Eintrag fehlt im Setting-Katalog** → als FEHLT/MISSING dokumentieren, **kein** ähnliches Element
  einsetzen. Ersatz-Talente verfälschen den Test des offiziellen Archetyps (s. Schritt 2).
- **Auto-Eintrag fehlt im SOLL** → SOLL um Auto-Einträge ergänzen (s. Tabelle oben).
- **Budget geht nicht auf** → prüfen, ob Doppelkosten durch zu spät gesteigerte Attribute.
  Wenn die Erstellung trotz korrektem Input nicht aufgeht → mit `s.notiz('...')` ins Log.
- **Echter Code-Bug** (Aktion mit korrektem Input scheitert/Exception/falsche Kosten) →
  stehen lassen, klar an den User melden. Das ist das Ziel.

### 8. Abschlussmeldung

Setting, Name, gespeicherte Datei, Schritt-für-Schritt-Ergebnis, Soll/Ist-Abweichungen +
Punktebilanz, und **vermutete Code-Bugs klar getrennt** von Input-/Vorlagen-Themen. Echte
Code-/Daten-Findings zusätzlich in `logs/archetypen_anomalie_bericht.md` aufnehmen.

---

## Setting-Spezialfall: Superkräfte-Kompendium (SKP statt Punkte)

Das Setting **„Superkräfte Kompendium"** (Datei `settings/Superkräfte Kompendium.json`, mit Umlaut
+ Leerzeichen) nutzt ein **eigenes Punktesystem (Superkraftpunkte, SKP)**, das der `driver.py`
**NICHT** kapselt. Superkräfte laufen direkt über `functions/superkraft_funktionen.py`:

```python
import functions.superkraft_funktionen as sf
s = d.Sitzung('Superkräfte Kompendium', name)   # ch.superkraefte ist schon mit 93 Kräften gefüllt,
                                                #   machtstufe='III', 'Superkräfte'-Talent auto gesetzt
sf.setze_machtstufe(s.ch, 'III')                # Stufe I–V = 15/30/45/60/75 SKP, Obergrenze 5/10/15/20/25
sf.waehle_superkraft(s.ch, kraft_name, kosten)  # gewählte Basis-SKP; Rückgabe:
                                                #   True | False(Name unbekannt) | 'needs_kosten'
                                                #   | 'ueber_obergrenze' (kosten>Obergrenze) | 'nicht_genug_skp'
sf.waehle_modifikator(s.ch, kraft_name, mod_name)
sf.get_verbleibende_skp(s.ch)                   # gesamt - verbraucht
sf.berechne_gesamt_kosten(s.ch)
```

- **Kräfte-Daten** liegen im Setting-JSON unter dem Key `krafte` (nicht `superkraefte`).
- Attribute/Fertigkeiten/Handicaps/Talente laufen weiter über die normalen Treiber-Methoden
  (`attribut_auf`, `fertigkeit_auf`, `handicap`, `talent`).
- **Power-Key-Mapping (EN→DE), Auszug:** Armor→`Panzerung`, Melee/Ranged Attack→`Nahkampfangriff`/
  `Fernkampfangriff`, Awareness→`Kampfsinn`, Deadeye→`Zielwasser`, Dodge→`Ausweichen`,
  Parry→`Parade`, Toughness→`Robustheit`, Hardy→`Zäh`, Super Attribute/Skill/Edge→`Superattribut`/
  `Superfertigkeit`/`Supertalent`, Flight→`Fliegen`, Env. Resistance→`Umweltresistenz`,
  Speed→`Geschwindigkeit`, Leaping→`Springen`, Heightened Senses→`Geschärfte Sinne`, Genie→`Genie`,
  Mind Shield→`Gedankenschild`, Energy/Matter Control→`Energiekontrolle`/`Materiekontrolle`,
  Healing→`Heilung`, Boost/Lower Trait→`Eigenschaft erhöhen/senken`, Copycat→`Nachahmen`,
  Illusion→`Illusion`, Push→`Schieben`, Stun→`Betäuben`, Entangle→`Fesseln`,
  Animal Companion→`Tiergefährte`.
- **Plausibilitätscheck:** Die Summe der gewählten Kraft-SKP muss exakt dem SKP-Budget der
  Machtstufe entsprechen (Stufe III = 45). Geht es nicht auf → Mapping/Kosten prüfen.
- Bekannte Lücken/Findings dieses Settings: siehe `logs/archetypen_anomalie_bericht.md`.

---

## Referenz: Treiber-API (`driver.py`)

| Schritt | Methode | Hinweis |
|---|---|---|
| – | `Sitzung(setting, name, protokoll=LOG)` | startet Controller + neuen Charakter |
| – | `setting_aus_dateiname(dateiname)` | Setting aus Screenshot-Namen ableiten |
| 1 | `pathfinder_klassentalent(name, ignore_voraussetzungen=False)` | nur Pathfinder; `ist_pathfinder()` |
| 2 | `handicap(name)` | exakter Key inkl. `_leicht`/`_schwer`; **major zuerst!** |
| 3 | `volk(name)` | |
| 4 | `volk_wahlmoeglichkeiten(volk)` | nur lesen: welche Wahlen bietet das Volk? |
| 4 | `volk_freies_talent / volk_freies_attribut / volk_attribut_malus / volk_freie_fertigkeit / volk_magieaffin` | je nach Volk |
| 5 | `attribut(name)` / `attribut_auf(name, ziel)` | reguläre Punkte; stoppt bei 0 |
| 5/10 | `steigere_mit_handicap_attribut(name)` | Attributsteigerung mit Handicap-Punkten |
| 6 | `fertigkeit(name)` / `fertigkeit_auf(name, ziel)` | aktiviert untrainierte Fert. (modifier −2→0) automatisch; ⚠️ `fertigkeit_auf` wirft `KeyError` bei unbekanntem Namen → vorher `if name in ch.fertigkeiten` prüfen |
| 6/10 | `steigere_mit_handicap_fertigkeit(name)` | Fertigkeit mit Handicap-Punkten |
| 7 | `talent(name, ignore_rang_check=False, ignore_voraussetzungen=False)` | |
| 8 | `macht(name, ignore_rang_check=False)` | |
| 9 | `kaufen(name, anzahl=1, force_bei_geldmangel=True)` | Geldmangel → Geld 0 + Preis 0 |
| – | `startkapital_mit_handicap()` | Handicap-Punkt → mehr Startgeld |
| – | `zustand()` / `punktestand()` / `volk_wahlmoeglichkeiten()` | Inspektion |
| – | `zeige_auto_eintraege(vor_snap)` | zeigt was neu hinzukam (nach volk/AH/Klassentalent) |
| – | `notiz(text)` | manuelle Anomalie-Notiz |
| – | `diff(soll)` | Multiset-Soll/Ist-Vergleich |
| – | `speichern(pfad)` / `bericht(pfad)` | JSON speichern / Gesamtbericht |
| (Superkräfte) | `functions.superkraft_funktionen` direkt | nicht im driver – siehe Setting-Spezialfall oben |

## Domain-Regeln (Kurzgedächtnis)

- **Manuelle vs. auto-gesetzte Einträge trennen** (s. Tabelle oben). Nie AH-Auto-Handicaps
  oder Klassentalent-Bonus-Talente in den Build-Loop aufnehmen — aber **immer im SOLL**.
- **Volks-Handicaps niemals manuell** wählen (kommen durchs Volk).
- **Keine Ersatz-Elemente.** Fehlt ein exakter Key für ein Bogen-Talent/-Handicap/-Macht, wird es
  als FEHLT dokumentiert — nie durch ein ähnliches ersetzt. Sonst wird nicht der offizielle
  Archetyp getestet, sondern eine Eigenkreation, und Setting-Lücken bleiben unentdeckt.
- **Major-Handicaps zuerst** im Build-Loop — HP-Limit=4, falsche Reihenfolge kann bewirken,
  dass ein Major-Handicap (2 HP) abgelehnt wird wenn das Limit schon durch Minors erreicht ist.
- **Attribute komplett (inkl. Handicap-Steigerungen) VOR den Fertigkeiten** – sonst Doppelkosten.
- Grundfertigkeiten (z.B. Allgemeinwissen, Athletik, Heimlichkeit, Überreden, Wahrnehmung)
  starten kostenlos auf W4 (modifier 0). Nicht-Grundfertigkeiten starten untrainiert
  (value 4, **modifier −2**); die erste Steigerung „aktiviert" sie (modifier −2→0, value bleibt 4).
- Fertigkeit > regierendes Attribut → **doppelte Kosten**.
- Handicap-Punkte: Schwere Handicaps = 2 HP, leichte = 1 HP. Max. 4 HP pro Charakter.
  2 HP = 1 Attributsteigerung oder 1 Talent; 1 HP = 1 Fertigkeitsschritt (Sonderfall).
- **HP-Limit-Rejected:** Wird ein HP-Limit-Rejection erwartet (Major kommt nicht rein),
  das Handicap trotzdem versuchen, als `ok=False`-Anomalie dokumentieren und im SOLL
  weglassen — oder prüfen ob es doch durch AH/Racial auto gesetzt wird (dann doch ins SOLL).
- Geld reicht nicht für Ausrüstung → auf 0 setzen und trotzdem kaufen (`force_bei_geldmangel=True`).
  FORCE-Käufe erscheinen als `ok=False`-Anomalien im Bericht — das ist dokumentiertes Verhalten,
  kein Bug.
- **Superkräfte:** SKP-System läuft NICHT über den driver, sondern über
  `functions.superkraft_funktionen` (siehe Setting-Spezialfall). `'ueber_obergrenze'` bei einer
  Einzelkraft > Kraftobergrenze ist dokumentiertes Verhalten — bei offiziellen Bögen mit Kräften
  >15 SKP klären, ob die Obergrenze zu streng modelliert ist.
- **Fuzzy-Diff-Hinweis:** `diff()` verwendet Teilstring-Matching bei Listen (Talente, Handicaps,
  Mächte). `'Neue Mächte'` matcht `'Neue Mächte_2'`. Wenn der Bogen zwei identisch benannte
  Einträge hat (z.B. 2× `Neue Mächte`), muss im SOLL der Name zweimal stehen.

## Was der Treiber NICHT kann (bekannte Grenzen)

- Keine echten Kivy-Widgets/Popups – nur Controller-Logik. UI-spezifische Bugs (Checkbox-
  Doppelklick, Dialog-Größe) sind damit **nicht** auffindbar.
- Keine Bilderkennung – Screenshots musst du selbst lesen.
- Event-Historie bleibt leer (Service ist da, aber ohne UI werden kaum Events erzeugt).
- **Superkräfte/SKP** sind nicht im Treiber gekapselt – direkt über
  `functions.superkraft_funktionen` ansteuern (siehe Setting-Spezialfall).

---

*Ende des Skills.*
