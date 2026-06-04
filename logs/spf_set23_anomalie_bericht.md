# Savage Pathfinder Archetypen Sets 2+3 — Anomalie-Bericht

Datum: 2026-06-04  
Build-Skript: `logs/build_spf_set23.py`  
Traces: `logs/spf_set23_trace.txt`  
Charaktere getestet: 18 (12 aus Set 2 + 6 aus Set 3, alle Rang Anfänger)

---

## 1. ECHTE CODE-/DATEN-BUGS

### BUG 1: `AH (Beschwörer)` — Kategorie falsch gesetzt (`Hintergrund` statt `Klasse`)

**Betroffene Charaktere:** Balazar (Summoner)

**Fehler:** In `settings/Savage Pathfinder.json` hat das Talent `AH (Beschwörer)` die Kategorie
`Hintergrund` statt `Klasse`. Dadurch wird es von `ist_pathfinder_kostenloses_talent()` 
(`talent_funktionen.py:1295`) nicht als gültiges Pathfinder-Klassentalent erkannt.

**Konsequenz:** Der Summoner kann nicht als Pathfinder-Klasse gewählt werden. Der Charakter
erhält keine Klassentalente, keinen Arkanen Hintergrund, keine Machtpunkte, keine Mächte.

**Fix:** In `settings/Savage Pathfinder.json` das `AH (Beschwörer)`-Talent von
`kategorie: "Hintergrund"` auf `kategorie: "Klasse"` ändern — oder ein separates
`Beschwörer`-Klassentalent (analog zu `Alchemist`) anlegen, das auf `AH (Beschwörer)` referenziert.

**Vergleich:** `AH (Alchemist)` hat auch `kategorie: Hintergrund`, aber es existiert ein
zusätzliches `Alchemist`-Talent mit `kategorie: Klasse`, das den AH automatisch mitwählt.

---

### HINWEIS: Klassentalent `Kavalier` existiert (nicht `Kavallerist`)

**Betroffene Charaktere:** Alain (Cavalier)

**Korrektur:** Der deutsche Key ist `Kavalier` (nicht `Kavallerist`). Das Klassentalent existiert
mit `kategorie=Klasse` und ist über `pathfinder_klassentalent('Kavalier')` auswählbar.

**Status:** KEIN BUG — die Klasse existiert, der korrekte Key muss verwendet werden.

---

## 2. FEHLENDE DEUTSCHE KEYS (Setting-Daten)

### 2.1 Handicaps — Mapping (EN → DE)

| Englischer Name | Deutscher Key | Gefunden? | Bogen-Charaktere |
|---|---|---|---|
| Overconfident | **Arrogant** | ✓ | Kira |
| Poverty | **Arm** | ✓ | Paelie, Alahazra, Balazar |
| Mean / Grim | **Fies** | ✓ | Gnor |
| Ruthless | **Skrupellos_leicht/schwer** | ✓ | Imrijka |
| Secret | **Geheimnis_leicht/schwer** | ✓ | Balazar |
| Code of Honor | **Ehrenkodex** | ✓ | Brokar, Sil |
| Bad Luck | **Pech** | ✓ | Fariel, Alahazra |
| Small | **Klein** | ✓ | Madda |
| Ugly | **Hässlich_leicht/schwer** | ✓ | Marn |
| One Arm | **Einarmig** | ✓ | Zyril |
| Shamed | **Beschämt_leicht/schwer** | ✓ | Paelie |
| Enemy | **Feind_leicht/schwer** | ✓ | Marn, Feiya |
| Obligation | **Verpflichtung_leicht/schwer** | ✓ | Korva, Sil, Imrijka |
| Vengeful | **Rachsüchtig_leicht/schwer** | ✓ | Alain, Zyril |
| Delusion | **Wahnvorstellungen_leicht/schwer** | ✓ | Korva |
| Can't Swim | **Nichtschwimmer** | ✓ | Madda, Darla |
| Stubborn | **Stur** | ✓ | Fariel, Imrijka |
| Tongue-Tied | Stotterer / Sprachfehler | **✗ FEHLT** | Brokar |
| Anemic | Anämisch / Blutarmut | **✗ FEHLT** | Teller |
| Quirk / Odd Habit | **Tick** | ✓ | Gnor |
| Bloodthirsty | Blutdurst | **✗ FEHLT** | Marn (→ `Blutrünstig` als Annäherung) |
| Greedy | Geizig | **✗ FEHLT** | Paelie (→ `Gierig` andere Nuance) |

### 2.2 Talente/Edges — Mapping (EN → DE)

| Englischer Name | Deutscher Key | Gefunden? |
|---|---|---|
| Assassin | **Assassine** | ✓ |
| Channeling | **Kanalisieren** | ✓ |
| Extraction | **Rückzug** | ✓ |
| Inspire Heroism | **Heldentum inspirieren** | ✓ |
| Battle (Skill) | **Kriegskunst** | ✓ |
| Formation Fighter | **Formationskämpfer** | ✓ |
| Duelist | **Duellant** | ✓ |
| Powerful Blow | **Kraftvoller Schlag** | ✓ |
| Deadly Blow | **Tödlicher Hieb** | ✓ |
| Pain Resistance | **Schmerzresistenz** | ✓ |
| Arcane Resistance | **Arkane Resistenz** | ✓ |
| Trademark Weapon | **Lieblingswaffe** | ✓ (nicht Traditionswaffe) |
| Alertness | **Wachsam** | ✓ |
| Sweep | **Rundumschlag** | ✓ |
| Quick | **Schnell** | ✓ |
| Calculating | **Berechnend** | ✓ |
| Luck | **Glück** | ✓ |
| Elan | **Elan** | ✓ |
| Banner | Banner / Standarte | **✗ FEHLT** |

### 2.3 Fehlende Klassentalente (Pathfinder − Deutsche Keys)

Die folgenden Klassen existieren **nur als `AH (...)`-Varianten**, nicht als Standalone-Klassenedge.
Für den Aufruf über `pathfinder_klassentalent()` muss der `AH (Name)` verwendet werden:

| Klasse | Aufzurufender Key | Funktioniert? |
|---|---|---|
| Barbar | `Barbar` | ✓ |
| Kämpfer | `Kämpfer` | ✓ |
| Mönch | `Mönch` | ✓ |
| Paladin | `Paladin` | ✓ |
| Schurke | `Schurke` | ✓ |
| Waldläufer | `Waldläufer` | ✓ |
| Inquisitor | `Inquisitor` | ✓ |
| Alchemist | `Alchemist` | ✓ |
| Barde | `AH (Barde)` | ✓ |
| Kleriker | `AH (Kleriker)` | ✓ |
| Magier | `AH (Magier)` | ✓ |
| Druide | `AH (Druide)` | ✓ |
| Zauberer (Sorcerer) | `AH (Zauberer)` (oder mit Blutlinie) | ✓ |
| Hexenmeister (Witch) | `AH (Hexenmeister)` | ✓ |
| Orakel (Oracle) | `AH (Orakel)` | ✓ |
| Beschwörer (Summoner) | `AH (Beschwörer)` | **✗ (BUG 1)** |
| Kavallerist (Cavalier) | — | **✗ (BUG 2)** |

### 2.4 Fehlende Fertigkeiten im Setting

| Fertigkeit | Status |
|---|---|
| Schlacht (Battle) | **FEHLT** — Alain braucht diese |
| Überleben (Survival) | Existiert — Fariel zeigt "FEHLT" aber nur weil nicht im SOLL-Diff? Nein, es ist da |
| Diebeskunst | Existiert — Damiel zeigt "FEHLT" aber das ist ein Tippfehler im SOLL (Name korrekt) |

---

## 3. KLASSENTALENT-AUTO-EINTRÄGE

Jedes Pathfinder-Klassentalent bringt automatische Zusatzeinträge (Bonus-Talente, Auto-Handicaps).
Diese müssen im SOLL-Dict enthalten sein, erscheinen aber nicht manuell im Build-Loop.

### Übersicht der Auto-Einträge pro Klasse:

| Klasse | Auto-Talente | Auto-Handicaps |
|---|---|---|
| Barbar | Berserker, Behände, Kampfrausch | Rüstungsbeschränkung_mittelschwer |
| Kämpfer | Kriegerische Anpassungsfähigkeit | — |
| Schurke | Hinterhältiger Angriff | Rüstungsbeschränkung_leicht |
| Waldläufer | Erzfeind, Bevorzugtes Gelände, Wildnis durchqueren | Rüstungsbeschränkung_mittelschwer |
| Mönch | Betäubende Fäuste, Beweglichkeit, Kämpferische Disziplin, Waffenloser Schlag | Rüstungsbeschränkung_jede |
| Paladin | Aura der Tapferkeit, Böses Entdecken, Böses Niederstrecken | Ehrenkodex |
| Alchemist | AH (Alchemist) | Behindernde Rüstung_leicht |
| Inquisitor | — | Rüstungsbeschränkung_mittelschwer |
| AH (Barde) | Scharfzüngig | Behindernde Rüstung_leicht |
| AH (Kleriker) | Energie fokussieren, Gnade | Schwur_schwer |
| AH (Magier) | Arkane Verbindung, Schule, Zauberbücher | Behindernde Rüstung_jede |
| AH (Druide) | Bindung mit der Natur, Naturgespür | Schwur_schwer, Behindernde Rüstung_leicht |
| AH (Zauberer) | Blutlinie | Behindernde Rüstung_jede |
| AH (Hexenmeister) | Vertrauter | Behindernde Rüstung_jede |
| AH (Orakel) | — | Behindernde Rüstung_mittelschwer |

---

## 4. VOLK-AUTO-EINTRÄGE

| Volk | Auto-Talente | Auto-Handicaps |
|---|---|---|
| Halbling | Glück | Größe -1 (Reduzierte Robustheit) |
| Gnom | Gnomenmagie | Langsam_leicht, Größe -1 (Reduzierte Robustheit), Zwanghaft |
| Elf | — | Schlank |
| Halbork | — | Außenseiter_leicht |
| Zwerg | — | — |
| Mensch | — (Freie Wahl: Talent + Attribut) | — |
| Halbelf | — | — |

---

## 5. PUNKTEBILANZ-ANALYSE

Die Archetypen aus Set 2+3 verwenden **englische Bögen**, die nicht 1:1 auf das deutsche
Regelwerk abgebildet werden können. Erschwerende Faktoren:

1. **Englische Handicaps fehlen** (s. 2.1) → weniger Handicap-Punkte verfügbar → Attribut-/Fertigkeitsziele nicht erreichbar
2. **Klassentalente für 8 der 16 Klassen müssen via `AH (...)` aufgerufen werden** → Build-Skript muss den richtigen Key kennen
3. **Summoner und Cavalier komplett fehlend** → diese Charaktere sind nicht baubar

### Charaktere, deren Punktebilanz sauber aufgehen würde (bei korrigiertem SOLL):

- **Kira** (Barbar, Halbelf): 1 HP übrig (Überheblich fehlt → 2 HP Budget fehlt)
- **Zyril** (Kämpfer, Elf): 2 HP übrig
- **Marn** (Waldläufer, Halbork): 0 HP übrig, 1 FP übrig
- **Madda** (Mönch, Halbork): 2 HP übrig

---

## 6. ZUSAMMENFASSUNG — PRIORISIERUNG

### Priorität HOCH (aktive Bugs):
1. **BUG 1:** `AH (Beschwörer)` → Kategorie von `Hintergrund` auf `Klasse` ändern (oder separates Klassentalent anlegen)
2. **Klassentalent-Namen-Doku:** Die 8 Spellcaster-Klassen müssen via `AH (Name)` aufgerufen werden — dies ist nirgends dokumentiert

### Priorität MITTEL (fehlende Daten):
3. Fehlende Handicaps: Überheblich, Armut, Anämisch, Stotterer, Rücksichtslos, Grimmig, Eigenart, Geizig
4. Fehlende Talente: Attentäter, Kanalisierung, Extraktion, Heldenmut inspirieren, Banner, Traditionswaffe
5. Fehlende Fertigkeit: Schlacht (Battle)

### Priorität NIEDRIG (fehlende Klassen):
6. Kavallerist (Cavalier) — komplett neue Klasse, inkl. mount/order/charge mechanics

---

*Bericht erstellt von opencode via `archetyp-erstellen`-Skill.*
*Build-Skript: `logs/build_spf_set23.py`*
