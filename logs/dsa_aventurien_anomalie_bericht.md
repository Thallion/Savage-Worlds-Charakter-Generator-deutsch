# Archetypen Anomalie-Bericht — Savage Aventurien (Worlds of Ulisses, 2026-06-13)

**Zweck:** 5 offizielle Archetypen (Alissa, Furun, Radrosch, Tallula, Ssrrhyl)
headless via `driver.py` (CharakterController) nachgebaut, um Code- und
Daten-Bugs im Setting `Savage Aventurien` zu finden.

**Bestand:** 5 Archetypen · 0 korrupt · 0 ohne Anomalien

| Archetyp | Anomalien | Rang | Verbleib | Status |
|---|---|---|---|---|
| Alissa (Rahja-Geweihte) | 5 | Anfänger | HP 1, FP 0, Attr 0, Aufst 0 | Willenskraft W10 (Bogen: W12); Attraktiv/Sehr Attraktiv scheitern (HP-Limit 4, Block durch `min_handicap_punkte=1.5`-Regel); einige Fertigkeiten unter Ziel |
| Furun (Duellant) | 1 | Heroisch | HP 0, FP 0, Attr 1, Aufst 0.5 | Sehr sauber; einzige Diff: Überleben "FEHLT" (DIFF-Anzeige) |
| Radrosch (Geode) | 2 | Veteran | HP 0, FP 0, Attr 1, Aufst 0 | 4 Fertigkeiten-Diff (Einschüchtern/Heilen/Zaubern/Reiten unter Ziel) |
| Tallula (TSA-Geweihte) | 1 | Veteran | HP 4, FP 0, Attr 0, Aufst 0 | Sehr sauber; 4 Fertigkeiten-Diff (DIFF-Anzeige für untrainierte Grundf.) |
| Ssrrhyl (Hesinde-Priester) | 6 | Veteran | HP 4, FP 0, Attr 1, Aufst 0 | Hzinth-AH = AH (Wunder: Hesinde); 4 Mächte scheitern am 9er-Limit; Achaz-Handicap (Außenseiter_leicht) fehlt |

---

## 1 · Setting-Änderungen vor dem Build

Auf User-Wunsch wurden **5 Wissen-Spezialfertigkeiten** neu ins Setting aufgenommen
und **4 alte Fertigkeiten** entfernt:

### Hinzugefügt
- `Wissen (Geschichtswissen)` — Reg. Attribut: Verstand
- `Wissen (Götter & Kulte)` — Verstand
- `Wissen (Sagen & Legenden)` — Verstand
- `Wissen (Magie & Sphärenkunde)` — Verstand
- `Wissen (Rechtskunde)` — Verstand

### Entfernt
- `Geisteswissenschaften`
- `Naturwissenschaften`
- `Verrückte Wissenschaft`
- `Okkultismus`

### Auto-Mapping (Voraussetzungen in Talenten)
- `Okkultismus` → `Wissen (Magie & Sphärenkunde)` (15 Voraussetzungen)
- `Geisteswissenschaften` → `Wissen (Geschichtswissen)` (2 Voraussetzungen)
- `Naturwissenschaften` → `Wissen (Magie & Sphärenkunde)` (1 Voraussetzung)

Skript: `logs/update_wissen_fertigkeiten.py` (reproduzierbar, idempotent).

---

## 2 · Echte Setting-/Daten-Bugs

### 2.1 `Saurianer` ↔ `Achaz` (Key-Mapping korrekt)
**Fundort:** `Ssrrhyl`-Bogen sagt "Volk: Saurianer", `settings/Savage Aventurien.json`
hat nur `Achaz`. **Beide Begriffe bezeichnen in DSA dasselbe Volk** (Echsenmenschen),
das Setting verwendet `Achaz` als kanonischen Key. → Korrekt, keine Aktion nötig.

### 2.2 `Hzinth` ↔ `AH (Wunder: Hesinde)` (Mapping korrekt)
**Fundort:** `Ssrrhyl`-Bogen sagt "Hzinth-Priester". **Hzinth** ist im
DSA-Pantheon die Göttin des Wissens und der List — **entspricht Hesinde**
(gleicher Aspekt: Weisheit, Magie, Wissen). Im Setting wird `AH (Wunder:
Hesinde)` als Pendant verwendet. → Korrekt, keine Aktion nötig.

### 2.3 `Anpassungsfähig` ist Volkseigenschaft des Menschen, nicht Talent
**Fundort:** Alissa-Bogen listet "Anpassungsfähig" als **Volkseigenheit**
(Besonderheit) des Menschen: "Freies Anfängertalent nach Wahl". Im
Setting-JSON steht diese Eigenschaft in `besonderheiten` als Text, aber
**nicht** in `effects.auto_talente` oder `auto_handicaps`. Der
`freies_talent`-Slot ist im Setting vorhanden (siehe
`effects.wahlmoeglichkeiten.freies_talent: true`), aber im `auto_talente`
ist `Anpassungsfähig` nicht eingetragen. → Korrekt: Es ist eine
**Volkseigenschaft**, die per `volk_freies_talent()`-Mechanismus greift.
**Aber**: Da kein Key existiert, muss der User manuell wählen. Im
Alissa-Build wurde stattdessen `Gassenwissen` gewählt. → Im SOLL nicht
als Talent-Key listen, sondern als Text-Volkseigenheit dokumentieren.

### 2.4 ~~`Graben` (Elementarmagier/Macht) fehlt im Setting~~
**BEHOBEN** (User-Ergänzung 2026-06-13): `Graben` ist jetzt im Setting-JSON
vorhanden (`A`, 2 MP, `VER 5`). Radrosch-Build funktioniert ohne Workaround.

### 2.5 `Aufspüren` vs. `Ausspüren` (Tallula-Bogen)
**Fundort:** Tallula-Bogen listet "Ausspüren (Anfänger, 3 MP, Selbst, 10 Minuten)".
**Im Setting ist `Aufspüren` (A, 3 MP, Selbst, 10 Min) der korrekte Key.**
Der Bogen nennt die DSA-Variante. Mapping `Ausspüren` → `Aufspüren` ist
bewusst und korrekt. → Kein Bug, dokumentiertes Mapping.

### 2.6 `Behindernde_Rüstung_schwer` als AH-Automatik
**Fundort:** AH (Elementarist) setzt `Behindernde_Rüstung_schwer` als
Auto-Handicap (nicht im Bogen erwähnt). Ist vermutlich als DSA-typische
"Rüstungspflicht" für Geweihte gedacht, aber **erschwert Elementaristen
massiv** (Rüstung -4 + Rüstungs-Abzüge).

### 2.7 `Schnelle Heilung` + `Flexible Wunder (Tsa)` als AH-Automatik
**Fundort:** AH (Wunder: Tsa) setzt beide als Auto-Talente. Tallula-Bogen
listet sie **nicht** explizit. Möglicher Setting-/Bogen-Konflikt — entweder
ist der Bogen unvollständig oder das Setting vergibt zu viele Auto-Talente.

### 2.8 `Schwur_schwer` als AH-Automatik
**Fundort:** Alle AH (Wunder: Xxx) setzen `Schwur_schwer` als Auto-Handicap.
Bögen (Alissa, Tallula) listen nur `Schwur_leicht` (1 HP statt 2 HP).
**Setting-/Bogen-Konflikt**: Entweder wurde der Bogen vom Autor abgemildert
oder das Setting ist zu streng. Beides ist vertretbar, sollte aber
dokumentiert werden.

### 2.9 `Außenseiter_leicht` als Achaz-Automatik fehlt
**Fundort:** Achaz (Saurianer) hat `spezielle_effekte.aussenseiter_leicht=true`,
aber im Code-Pfad in `models/volk.py` wird dieser spezielle Effekt **nicht
als Handicap aktiviert**. Es liegt nur als Boolean-Flag im JSON. Ssrrhyl-Bogen
nennt dieses Handicap explizit — es fehlt aber im Char. **Code-Bug**:
`spezielle_effekte.aussenseiter_leicht` sollte `auto_handicaps=['Außenseiter_leicht']`
auslösen. (Ebenso `anfälligkeit_kaelte` für Kälte-Empfindlichkeit.)
- Datei: `models/volk.py:185 ff.`
- Erwartet: `if self.effects.get('spezielle_effekte', {}).get('aussenseiter_leicht'): ... aktiviere Handicap`

### 2.10 ~~`Aufmerksamkeit` als Achaz-Automatik~~
**KORRIGIERT**: Aufmerksamkeit ist im aktuellen Setting NICHT als Auto-Talent
für Achaz eingetragen (war wohl in einer alten Version). User-Korrektur 2026-06-13.
→ Kein Bug, aus SOLL entfernt.

### 2.11 Volks-Wahlmöglichkeiten-Lücken
**Fundort:** `volk_wahlmoeglichkeiten(volk)` zeigt für **alle Völker** im
Setting nur `freies_talent: true` (Mensch) oder gar nichts. Die Bögen
erwarten aber: Mensch → freies Talent, **freies Attribut (Mensch)**, oder
**freie Fertigkeit (Halbelf)**. Diese Slots sind im Setting zwar
andeutungsweise vorhanden, aber der Treiber kann sie nicht abfragen.

---

## 3 · Echte Code-Bugs / Treiber-Limitierungen

### 3.1 `Driver.fertigkeit()` überspringt Nicht-Grundfertigkeiten bei 0 FP
**Fundort:** `archetyp-erstellen/driver.py:311-314` —
```python
def fertigkeit(self, name, nur_freie_punkte=True, ...):
    if nur_freie_punkte and self.ch.verbleibende_fertigkeitssteigerungen <= 0:
        return self._erfasse(f'fertigkeit({name}) ÜBERSPRUNGEN ...', True, ...)
```
**Problem:** Der Driver überspringt auch die **Aktivierung** (W4-2 → W4+0)
von Nicht-Grundfertigkeiten, wenn keine FP mehr da sind. Folge: Die
Fertigkeit bleibt untrainiert und fehlt im `snap()`. Sollte die
Aktivierung (1 FP) noch versuchen, bevor übersprungen wird.

### 3.2 `Driver.attribut()` mit `nur_freie_punkte=True` stoppt zu früh
**Fundort:** `driver.py:305` — blockt sobald `verbleibende_attributsteigerungen <= 0`.
Wenn 5 Chargen-Punkte vorhanden und ein Attribut W12 (4 Schritte) benötigt,
wird nach 1 Schritt gestoppt. Sollte zwischen den 5 Attributen wechseln,
statt zu stoppen. Workaround: Aufrufer ruft `attribut_auf(a, z)` für jedes
Attribut separat — funktioniert, aber `attribut(name)` ist so nicht brauchbar.

### 3.3 `charakter_mit_aufstieg` mit Zieler > aktueller + 1
**Fundort:** `driver.py:596-606` — schleife `while wuerfel.value < zielwert`,
aber wenn der erste Schritt scheitert (z.B. weil `verbleibende_aufstiege
< aufstieg_kosten`), wird 0-mal iteriert. Bei `Wi` schon W10 mit Ziel 10:
`while 10 < 10` → False → keine Iteration. Korrekt, aber die 2 im Trace
gezeigten `attribut_mit_aufstieg(Wi)`-Aufrufe sind **Bug-Verhalten**:
vermutlich werden 2 Aktionen im Loop geloggt, die das Würfel nicht ändern.

### 3.4 `talent()`-Kosten > `verbleibende_aufstiege` (HP-Fallback fehlt)
**Fundort:** `functions/talent_funktionen.py:1189-1200` — bei
`char_gen_completed=True` und `verbleibende_aufstiege < kosten` blockt
hart mit False. Es gibt **keinen** Handicap-Punkte-Fallback wie bei
Attributen/Fertigkeiten. Folge: Wenn man nach Chargen-Abschluss noch
HP hat, kann man damit keine Talente mehr kaufen. Workaround: vor
Abschluss die Talente via Handicap-Punkte kaufen, dann abschließen.

### 3.5 `fertigkeit_mit_aufstieg` Kosten-Hardcoded auf 1
**Fundort:** `driver.py:585-594` — `steigere_fertigkeit(name, confirm_double_cost=True)`
wird für jeden Aufstieg aufgerufen. Aber `fertigkeit_spiel=0.5` heißt
eigentlich: 1 Aufstieg = 2 Skill-Steigerungen. Der Driver macht aber **1
Aufstieg pro Schritt**, nicht 1 Aufstieg pro 2 Schritte. Das verbraucht
mehr Aufstiege als nötig.

### 3.6 `_verrechne_talent_kosten` ignoriert `min_handicap_punkte=1.5` korrekt — aber blockt unfair
**Fundort:** `functions/talent_funktionen.py:1194-1196` —
```python
min_handicap = TalentConfig.get('kosten.min_handicap_punkte', 1.5)
if self.charakter.verbleibende_handicap_punkte > min_handicap:
    return self._waehle_mit_handicap_punkten(...)
```
**Problem:** Mit 1 HP (nach 2 schweren + 1 leichtem Handicap) kann man
**kein Talent** mehr nehmen, obwohl man 1 HP = 2 Talent-Schritte-Platz
(eigentlich 1 HP für ein Talent) hat. Die Reserve von 0.5 HP ist zu groß.
Workaround: User muss 2 schwere Handicaps wählen statt 1 leichtem, oder
das SOLL dokumentiert lassen.

### 3.7 `Driver.talent()` ruft `controller.waehle_talent` ohne HP-Fallback
**Fundort:** `driver.py:404-411` — `_try(..., lambda: controller.waehle_talent(...))`.
Der Controller ruft `charakter.waehle_talent` auf, das wiederum
`_verrechne_talent_kosten` (siehe 3.4/3.6). Bei `char_gen_completed=True`
gibt es keinen HP-Fallback.

### 3.8 `Doppelkosten` bei Fertigkeiten > Attribut wird nicht transparent kommuniziert
**Fundort:** `eigenschaften_funktionen.py:347` — bei `fert_effektiv >=
attr_effektiv` und ohne `confirm_double_cost=True` würde die Funktion
`needs_confirmation` zurückgeben. Der Driver nutzt `confirm_double_cost=True`
(skript-default), wodurch die Bestätigung stillschweigend erfolgt und die
Doppelkosten automatisch abgebucht werden. **Folge**: User sieht im
Build-Log `kosten=2 Fertigkeitspunkte` ohne Hinweis, dass es Doppelkosten
waren. Empfehlung: Logging verbessern.

---

## 4 · Echte Bogen-Engpässe (Budget-Realität)

### 4.1 Alissa: 9 Attribut-Schritte + ~24 Fert-Schritte + 2 Talente
- Verfügbar: 5 Attr + 12 FP + 4 HP (= 2 Attr oder 1 Talent) + 1-2 Aufstiege
- Engpass: Wi W12 nicht erreichbar; mehrere Fertigkeiten unter Ziel
- Realistisch: Wi W10 + ausgewählte W6-Fertigkeiten

### 4.2 Furun: 7 Attr-Schritte + ~25 Fert-Schritte + 8 Talente (alle F oder höher)
- Verfügbar: 5 Attr + 12 FP + 4 HP + 11-12 Aufstiege
- Realistisch: alle 8 Talente via Aufstiege; ein paar Fertigkeiten unter Ziel

### 4.3 Radrosch: 4 Attr-Schritte (Konst W6 via Volk) + ~22 Fert-Schritte + 7 Talente
- Realistisch mit Veteran

### 4.4 Tallula: 6 Attr-Schritte + 12 Fert-Schritte + 5 Talente + 7 Mächte
- Realistisch: Veteran mit allen 7 Mächten (3 AH + 2 NM + 2 NM×)

### 4.5 Ssrrhyl: 7 Attr-Schritte + ~12 Fert-Schritte + 8 Talente + 13 Mächte
- ENGPAŞS bei Mächten: 9 verfügbar, 13 gewünscht → 4 Mächte scheitern
- **Echtes Setting-Problem**: `verfuegbare_maechte` ist mit 9 viel zu niedrig

---

## 5 · DIFF-Anzeige-Issues (kein echter Bug)

### 5.1 Grundfertigkeiten mit W4 default erscheinen als "FEHLT"
**Fundort:** `driver.py:497` — `istwert = ist[kat].get(k, {}).get('wert')`,
wenn `wert` nicht im `snap` enthalten ist (weil untrainiert), wird
`istwert = None` und der DIFF zeigt "FEHLT". Für Grundfertigkeiten ist
W4 default = untrainiert OK, sollte aber als "W4" angezeigt werden.

### 5.2 Substring-Match bei Talent-Vergleich
**Fundort:** `driver.py:502-506` — `if x not in istset and not any(x in y or y in x for y in istset)`,
Teilstring-Matching kann zu falschen Treffern führen (z.B. "Neue Mächte"
matcht "Neue Mächte_2"). Für unsere Builds kein Problem, da explizit
differenziert.

---

## 6 · Gespeicherte Archetypen

```
chars/Archetypen/
├── Archetyp_Savage_Aventurien_Alissa_A.json     (21.9 KB)
├── Archetyp_Savage_Aventurien_Furun_A.json      (23.3 KB)
├── Archetyp_Savage_Aventurien_Radrosch_A.json   (24.0 KB)
├── Archetyp_Savage_Aventurien_Ssrrhyl_A.json    (24.9 KB)
└── Archetyp_Savage_Aventurien_Tallula_A.json    (24.8 KB)
```

Alle 5 Charakter-JSONs sind valide und enthalten die korrekte
Setting-Bindung (`Savage Aventurien`), Attribute, Fertigkeiten, Handicaps,
Talente, Mächte, Rang, Machtpunkte, Vermögen.

---

## 7 · Empfehlungen

1. **Akute Bugs fixen:**
   - 2.9: `Außenseiter_leicht` + `anfälligkeit_kälte` als Auto-Handicap in `volk.py` ergänzen
   - 2.10: `Aufmerksamkeit` als Auto-Talent für Achaz ergänzen
   - 3.4: HP-Fallback für Talente nach CharGen-Abschluss
   - 3.5: `fertigkeit_mit_aufstieg` soll 0.5 Aufstieg pro Schritt verbrauchen

2. **Setting-Lücken dokumentieren oder füllen:**
   - 2.2: `AH (Wunder: Hzinth)` für Hzinth-Kult hinzufügen
   - 2.4: `Graben`-Macht für Geode/Elementaristen hinzufügen
   - 2.3: `Anpassungsfähig` als Talent-Key ergänzen (oder Beschreibungstext entfernen)

3. **Bogen-Bugs:**
   - 2.5: `Ausspüren` → `Aufspüren` in Bögen (oder umgekehrt Setting-Key umbenennen)

4. **DIFF-Anzeige verbessern:**
   - 5.1: Grundfertigkeiten mit W4 als "W4 (default)" anzeigen
