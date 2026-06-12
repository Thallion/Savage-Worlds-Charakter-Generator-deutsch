---
name: wuerfel-werte-logik
description: Referenz für die exakte Würfel-/Modifikator-Logik (W4-2 … W12+2), die Cap-/Kosten-/Ausstiegslogik vor und nach char_gen_completed, das freie Menschen-Talent/-Attribut, wie Volkseigenschaften Attribute/Fertigkeiten erhöhen/senken/modifizieren und welche Talente/Handicaps abgeleitete Werte (Robustheit, Parade, Bewegungsweite, Bennys) beeinflussen. Aufrufen bei Arbeiten an Charaktererstellung, Steigerungslogik, Punktebilanz, Volk-/Talent-Effekten oder beim Nachbauen von Archetypen (ergänzt den Skill archetyp-erstellen). Alle Angaben sind gegen den Code verifiziert (Datei:Zeile genannt).
allowed-tools: Read Grep Glob Bash
---

# Würfel-, Werte- & Steigerungs-Logik (Grundverständnis)

**Zweck:** Das exakte mechanische Modell hinter Würfeln, Steigerungskosten, der
Ausstiegslogik (`char_gen_completed`), Volkseigenschaften und Talent-/Handicap-Effekten
auf abgeleitete Werte. Damit lassen sich Punktebilanzen nachrechnen, Bugs einordnen und
Archetypen korrekt nachbauen. **Quelle ist immer der Code** – bei Zweifeln die genannten
Datei:Zeile-Stellen per Read prüfen, nicht raten.

> Verwandter Skill: **`archetyp-erstellen`** (baut Archetypen headless über den Controller).
> Dieser Skill liefert das *Warum* hinter den dortigen Reihenfolge-/Kosten-Regeln.

---

## 1. Die Würfelleiter (`models/wuerfel.py`)

```
W4-2   W4   W6   W8   W10   W12   W12+1   W12+2   (W12+3 = Warnung, aber erlaubt)
```

- **Gültige Würfelwerte:** `VALID_VALUES = [4, 6, 8, 10, 12]` (`value`), plus `modifier`.
- **Stufen** (`STUFEN = {4:1, 6:2, 8:3, 10:4, 12:5}`):
  `stufe = STUFEN[value] + (modifier wenn value==12)`.
  Der Modifier zählt **nur bei W12** als Stufe (W12+1 = Stufe 6, W12+2 = Stufe 7).
- **`total_value`** = `value + modifier` nur bei W12, sonst `value`.
  ⇒ Bei W4-2 ist `total_value` = 4 (der `-2`-Modifier zählt **nicht** in `total_value`),
  aber der „effektive" Wert für Kosten/Vergleiche ist `value + modifier` = 2 (s. §3).

### Sonderstellen des Modifiers
| Würfel | Bedeutung |
|--------|-----------|
| **W4-2** | untrainierte Nicht-Grundfertigkeit (`modifier = -2`, nur `typ="fertigkeit"`) |
| **W12+1 / W12+2** | über das Maximum hinaus (nur W12 erlaubt `modifier > 0`) |
| **W4-1** | Attributsschwäche / negativer Volks-Bonus (flacher `modifier = -1`) |

### `increase()` / `decrease()` – exaktes Verhalten
- **increase:** `W4-2 → W4` (Sprung: `modifier += 2`), dann `W4→W6→W8→W10→W12`,
  dann `W12 → W12+1 → W12+2` (ab W12+2 Warnung, steigert trotzdem). `wuerfel.py:46`.
- **decrease:** `W12+x → W12` (modifier−1), `W12→W10→…→W4`; bei `W4` **nur Fertigkeiten**
  (mit `modifier > -2`) → `W4-2`. Attribute können **nicht unter W4**. `wuerfel.py:76`.

⚠️ **`Attribut.wert` ist an `wuerfel.value` gebunden** (`models/attribut.py:24/27-28`):
Setzen von `wuerfel.value`/`wuerfel.modifier` aktualisiert `wert`/`modifier` automatisch.
Mocks in Tests müssen das spiegeln (sonst „von W4 auf W4"-Scheinfehler).

---

## 2. Aufstiegslogik: vor vs. nach `char_gen_completed`

Das Flag `charakter.char_gen_completed` schaltet die komplette Kosten-/Punktequelle um.
Kern in `functions/eigenschaften_funktionen.py` (Klasse `EigenschaftenManager`, ab Z.129/320;
die Modul-Wrapper `steigere_attribut`/`steigere_fertigkeit` ab Z.682/694 delegieren dorthin).

| | **VOR** (`char_gen_completed = False`) | **NACH** (`= True`) |
|---|---|---|
| **Attribut** | aus `verbleibende_attributsteigerungen` (Kosten `attribut_chargen`=1); Fallback **2 Handicap-Punkte = 1 Attribut** | aus `verbleibende_aufstiege` (Kosten `attribut_spiel`=1) |
| **Fertigkeit** | aus `verbleibende_fertigkeitssteigerungen` (Kosten `fertigkeit_chargen`=1); Fallback **1 HP = 1 Fertigkeitsschritt** | aus `verbleibende_aufstiege` (Kosten `fertigkeit_spiel`=**0,5** ⇒ 1 Aufstieg = 2 Fertigkeitsschritte) |
| **Handicap-Punkte als Quelle** | ja (s. Fallbacks) | **nein** (nur Aufstiege) |
| **Rang** | bleibt Anfänger | aus ausgegebenen Aufstiegen berechnet |
| **W-Maximum** | `value >= 12` blockiert (max **W12** über Steigern-Pfad) | dito |

**Wichtig:** `steigere_attribut` blockt hart bei `value >= max_wuerfel_wert` (=12,
`eigenschaften_config.json`). **W12+1/+2 sind über den normalen Steigern-Pfad NICHT
erreichbar** – sie entstehen nur durch Volk-/Talent-Effekte, die den Modifier direkt setzen
(Racial-Texte „Maximum W12+1" heben die *erlaubte* Obergrenze an, werden vom generischen
Cap aber nicht automatisch durchgesetzt). `eigenschaften_funktionen.py:147` / `339`.

> Der alternative Modulpfad `functions/character_advancement.py:32` (`steigere_attribut`)
> hat **keinen** W12-Cap und ruft `increase()` direkt. Die Produktiv-UI nutzt aber den
> `EigenschaftenManager`-Pfad (`models/charakter.py:271-291`).

### Übergang sauber abschließen (für Fortgeschrittene-Builds)
```python
s.ch.char_gen_completed = True
for _ in range(n): increase_aufstiege(s.ch)   # +1 aufstiege_gesamt UND +1 verbleibende
```
`increase_aufstiege` (`character_advancement.py:138`) erhöht beide Zähler und setzt den Rang neu.

---

## 3. Kosten & Doppelkosten (`_berechne_fertigkeit_kosten`, Z.469)

- **Basis:** chargen 1 / Spiel 0,5 pro Fertigkeitsschritt; Attribut 1 / 1.
- **Doppelkosten:** Wenn `fertigkeit_effektiv >= attribut_effektiv` → Kosten × `fertigkeit_ueber_attribut` (=2).
  `effektiv = wuerfel.value + wuerfel.modifier` (also **W4-2 = 2**, **W4 = 4**, **W6 = 6** …).
  ⇒ Eine Fertigkeit, die ihr regierendes Attribut **erreicht oder übersteigt**, kostet doppelt.
  Steigern liefert dann erst `"needs_confirmation"` (`eigenschaften_funktionen.py:347`).
- **Konsequenz für Reihenfolge:** Attribute **komplett vor** den zugehörigen Fertigkeiten
  steigern, sonst zahlt man Doppelkosten und die Punktebilanz geht nicht auf.

### Startbudget & Handicap-Punkte
- Start: **5** Attributsteigerungen, **12** Fertigkeitssteigerungen
  (`models/charakter_properties.py:20-21`, `eigenschaften_config.json:16`).
- Handicap-Punkte: schwer = 2 HP, leicht = 1 HP, **max 4 HP** (`handicap_config.json:46`,
  `talent_config.json`: `handicap_punkte=2`, `min_handicap_punkte=1.5`).
- Umrechnung: **2 HP → 1 Attribut** · **1 HP → 1 Fertigkeitsschritt** · **1 HP → mehr Startgeld**
  (`erhoehe_startkapital`, `character_advancement.py`) · **2 HP → 1 Talent** (Talent-Logik).

### Rang-Mapping (`models/charakter.py:157`)
Basis = **ausgegebene** Aufstiege (`aufstiege_gesamt − verbleibende_aufstiege`):
`0–3 Anfänger · 4–7 Fortgeschritten · 8–11 Veteran · 12–15 Heroisch · 16+ Legendär`.

---

## 4. Volkseigenschaften: Attribute/Fertigkeiten erhöhen/senken/modifizieren

Angewendet in **`Volk.apply_effects_to_charakter`** (`models/volk.py:185`) aus dem
`effects`-Block des Setting-JSON. **Reihenfolge-Regel:** Volk **vor** dem manuellen Steigern
wählen – die Boni greifen nur auf **unveränderten Basiswerten** (s.u.).

### `effects.attribute_bonuses` = `{Attribut: n}`
- **Positiv:** nur wenn Attribut noch `W4 + modifier 0` ⇒ `wuerfel.value = 4 + n`.
  Der Wert `n` ist die **Differenz zu 4 in Würfel-Pips** (2 pro Stufe):
  `+2 → W6`, `+4 → W8` (z.B. Goblin Geschicklichkeit), `+6 → W10`. `volk.py:206-211`.
  Ist das Attribut schon erhöht → **Bonus verfällt** (wird übersprungen). `volk.py:212`.
- **Negativ:** nur wenn `modifier == 0` ⇒ `wuerfel.modifier = n` (flacher Malus,
  **kein** Würfelschritt runter): `-1 → W4-1`, `-2 → W4-2`. `volk.py:214-218`.
  (Anzeige-Konvention: zusätzlich ein passendes Handicap in `handicaps[]`, z.B. Elf/Nachtalb
  `Schlank` neben `Konstitution: -1` – das ist **keine** Doppelung.)

### `effects.fertigkeits_startboni` = `{Fertigkeit: n}` (`volk.py:222`)
- **Grundfertigkeit** (Allgemeinwissen, Athletik, Heimlichkeit, Überreden, Wahrnehmung):
  `W4+0 → W(4+n)` (z.B. `+2 → W6`).
- **Nicht-Grundfertigkeit** (startet `W4-2` untrainiert): `+n>0` ⇒ `value = 4+n, modifier 0`
  (z.B. `+2 → W6`); `n<0` ⇒ `modifier = -2+n`.
- `fertigkeits_startmalus` (Z.250): `W4 → W4+malus`. `fertigkeits_modifier_boni` (Z.259):
  flacher `modifier += x` (Würfeltyp unverändert).

### Weitere `effects`-Felder
| Feld | Wirkung | Berechnet in |
|------|---------|--------------|
| `robustheit_bonus` | flacher +/- auf Robustheit | `abgeleitete_werte.py:99` |
| `groesse_modifikator` | Größe (⇒ Robustheit) | `abgeleitete_werte.py:96` |
| `bewegungsweite_bonus` | +/- Bewegungsweite | `abgeleitete_werte.py:51` |
| `auto_talente` | Talente auto auf `ausgewaehlt`, inkl. Machtpunkte/neue Mächte | `volk.py:272` |
| `auto_handicaps` | Handicaps auto in `selected_handicaps` | `volk.py:290` |
| `auto_mächte` / `spezielle_effekte:[{typ:'macht_volk'}]` | Mächte + ggf. `AH (Begabt)` | `volk.py:298/305` |
| `spezielle_effekte: panzerung_1/2/bonus` | natürliche Panzerung (zum Rüstungsschutz, **nicht** Basis-Robustheit) | `abgeleitete_werte.py:281` |

> ⚠️ Sanity-Check im Code: `robustheit_bonus != 0` **und** `groesse_modifikator != 0`
> gleichzeitig erzeugt eine Warnung (mögliche Doppelcodierung). `abgeleitete_werte.py:235`.

### Freies Menschen-Talent / -Attribut (`functions/volk_funktionen.py`)
Menschen haben **Einzel-Slots**: Es kann nur **ein** freies Talent **und ein** freies Attribut
gleichzeitig aktiv sein. Bei Neuwahl wird die vorherige Wahl **zurückgesetzt**:
- **freies Attribut** (`waehle_freies_attribut`, Z.687): vorheriges Attribut **W6 → W4**
  zurück, dann neues `wuerfel.value = 6`. Gibt einen **kostenlosen** Würfelschritt.
- **freies Talent** (`waehle_freies_talent`, Z.604): vorheriges via `talent_abwaehlen`
  (inkl. AH-Effekte/Mächte/Machtpunkte) zurück, dann neues über
  `talent_funktionen.waehle_freies_talent` (aktiviert AH, Auto-Handicaps etc.).

⚠️ Beim Archetyp-Build **ALLE** `True`-Wahlmöglichkeiten abarbeiten
(`volk_wahlmoeglichkeiten(volk)`), nicht nur eine – sonst fehlt Budget.

---

## 5. Talente & Handicaps, die abgeleitete Werte beeinflussen

Vollständig **datengetrieben** in **`config/abgeleitete_effekte.json`**
(geladen von `functions/effekt_registry.py`, angewendet in
`functions/abgeleitete_werte.py`). Inhalt:

### Parade (`= 2 + Kämpfen//2 + Bonus`, Z.39)
`+1`: Block · Harter Block (ersetzt Block) · Meister aller Waffen · Waffenmeister ·
Herdritter (Hellfrost) · **Lieblingswaffe**. `+2`: **Absolute Lieblingswaffe** (ersetzt Lieblingswaffe).

### Robustheit (`= Konstitution//2 + 2 + Größe + Robustheit-Bonus`, Z.111)
- **Größe +1:** Kräftig (Talent), Volk-Größe. **Größe −1:** Klein (Handicap, leicht).
- **Robustheit-Bonus +1:** Raufbold · Schläger · Jünger Erthas (Hellfrost) · Fettleibig (leicht) ·
  AH(Zauberer) Abnorme/Dämonische Blutlinie · Volk-`robustheit_bonus` · Cyberware.
- **+2:** AH(Zauberer) Drachenblutlinie (Schuppenhaut).
- **Kämpferische Disziplin** (Mönch): +1 Robustheit **nur ohne getragene Rüstung** (Z.81–91).
- Natürliche Panzerung (Volk/Cyberware) zählt zum **Rüstungsschutz**, nicht zur Basis.
- Merksatz: **Konstitution +2 (W4→W6) ⇒ +1 Robustheit** (6//2+2=5 vs 4//2+2=4).

### Bewegungsweite (`Basis 6`, Z.46)
- **−1:** Langsam (leicht), Fettleibig (leicht), Alt (schwer). **−2:** Langsam (schwer).
- **+2:** Behände (Barbar), Flink (Hintergrund). Volk-`bewegungsweite_bonus`, Cyberware.
- Minimum 1.

### Bennys (`Basis 3`, Z.129)
- **+1:** Glück · Großes Glück · Jung (leicht) · Volk mit `auto_talente`-`Glück` (z.B. Halbling).
- **+2:** Jung (schwer).

> Diese Effekte sind **namensbasiert** in `config/abgeleitete_effekte.json` hinterlegt.
> Ein neues Talent/Handicap mit Robustheits-/Parade-/Bewegungs-Wirkung muss dort
> **zusätzlich** eingetragen werden – es reicht nicht, es nur ins Setting-JSON zu
> schreiben. (Relevanter Stolperstein bei DSA-/Setting-Erweiterungen.)
> Semantik: additiv; `nicht_kumulativ_gruppe` ⇒ nur Gruppen-Maximum zählt
> (Lieblingswaffe-Paar, Behände/Flink); Block-Paar bewusst additiv;
> `bedingung: keine_getragene_ruestung` für Kämpferische Disziplin.
> Traglast (`Kräftig` +20 kg, `traglast_kg`) läuft über dieselbe Registry.
> Absicherung: `test units/test_abgeleitete_werte.py` (Charakterisierung + Registry-Smoke).

---

## 6. Schnell-Checkliste „Punktebilanz geht nicht auf"

1. Volk **vor** dem Steigern gewählt? (sonst verfallen Attribut-/Skill-Boni, `volk.py:212`)
2. Alle freien Volkswahlen abgearbeitet (Mensch: Talent **und** Attribut)?
3. Attribute **komplett** (inkl. Handicap-Steigerungen) **vor** Fertigkeiten? (Doppelkosten, §3)
4. Fertigkeit ≥ Attribut ⇒ Doppelkosten eingeplant?
5. `char_gen_completed` korrekt? (vorher: Steigerungs-/HP-Pools; nachher: nur Aufstiege, Skill 0,5)
6. Major-Handicaps zuerst (HP-Limit 4)?
7. Abgeleiteter Wert fehlt trotz Talent? → Name in `config/abgeleitete_effekte.json` hinterlegt (§5)?

---

*Ende des Skills. Bei Unsicherheit immer die genannte Datei:Zeile per Read gegenprüfen.*
