# Abgleich: DSA-Regelwiki „Spezies" ↔ Savage Aventurien Völker

**Stand:** 2026-06-03
**Quelle:** https://dsa.ulisses-regelwiki.de/spezies.html + DSA-Spezies-Stat-Blocks
**Implementierung:** `scripts/dsa_add_voelker.py` (Pass 1) + `scripts/dsa_voelker_spezifisch.py` (Pass 2)
**Backups:** `…_vor_voelker_20260603.json`, `…_vor_voelker_dsa_20260603.json`

> **ENDSTAND (Pass 2, 2026-06-03): 9 Spezies** = Mensch, Elf, Halbelf, Zwerg, Ork,
> Halbork, Goblin, Achaz, Holberker. **Necker, Drachling, Nachtalb gelöscht.**
> Details siehe Abschnitt **7** (DSA-Spezifisch-Pass).
> Abschnitte 1–5 sind der **historische Pass-1-Stand** (12 Spezies inkl. Nachtalb) und
> werden durch Abschnitt 7 überschrieben.

---

## 1. Abgleich der offiziellen DSA-Spezies (10)

| DSA-Spezies | Status im Setting | Aktion |
|-------------|-------------------|--------|
| Achaz | ✅ vorhanden | **angepasst** (Hitzeresistenz ergänzt) |
| Elf | ✅ vorhanden | unverändert |
| Goblin | ✅ vorhanden | unverändert |
| Halbelf | ✅ vorhanden | unverändert |
| Halbork | ✅ vorhanden | unverändert |
| **Holberker** | ❌ fehlte | **NEU angelegt** |
| Mensch | ✅ vorhanden | unverändert |
| **Nachtalb** | ❌ fehlte | **NEU angelegt** |
| Ork | ✅ vorhanden | **angepasst** (Strenger Körpergeruch) |
| Zwerg | ✅ vorhanden | unverändert |

**Zusätzlich im Setting** (nicht auf der offiziellen Spezies-Übersicht, aus anderen
DSA-Quellen): **Necker**, **Drachling** — bleiben erhalten.

→ Völker gesamt: **12**

---

## 2. Neue Spezies (DSA → SW-Konversion)

Die DSA-Statblocks (LE/SK/ZK/GS) wurden **nicht** 1:1 kopiert, sondern in den
bestehenden SW-`effects`-Stil übersetzt (Attribut-Boni, Besonderheiten, Handicaps),
konsistent zu den vorhandenen 10 Völkern.

### 2.1 Holberker
*Verwilderte Menschen Nordaventuriens (Holberk, Svellttal). Quelle: „Orks – Hauer & Schwarzer Pelz", S. 19.*

| DSA-Wert | SW-Umsetzung |
|----------|--------------|
| KO +1, KL −1 | `Konstitution +2` (Widerstandsfähig), `Verstand −1` (Ungehobelt) |
| Dunkelsicht I | Nachtsicht (auto_talent) |
| Richtungssinn (typisch) | `Überleben` Startbonus +2 |
| Hohe Zähigkeit / „Zäher Hund" / LE-Grundwert 6 | über `Konstitution +2` (W4→W6 ⇒ +1 Robustheit) abgebildet |

> **Balancing 2026-06-03:** Ursprünglich `Konstitution +2` **und** separater
> `robustheit_bonus +1` (= +2 effektive Robustheit). Auf Wunsch reduziert: nur noch
> `Konstitution +2`, was über den Würfelschritt von selbst **+1 Robustheit** ergibt.
> Separater Robustheits-Bonus und „Zäher Hund (+1 Robustheit)"-Besonderheit entfernt.

### 2.2 Nachtalb
*Nachtaktive Elfen-Verwandte (Nai Ashyrr). Sehr schlank, magisch begabt, lichtscheu.*

| DSA-Wert | SW-Umsetzung |
|----------|--------------|
| GE +1 | `Geschicklichkeit +2` (Geschickt) |
| IN +1 / Dunkelsicht | `Wahrnehmung` Startbonus +2 + Dunkelsicht |
| KL oder KK −2 / Zä −6 (sehr fragil) | `Konstitution −1` + Handicap `Schlank` |
| Auto „Zauberer" (20 AsP) | Besonderheit „Nächtliche Begabung" (Elfenmagie-artig) |
| Auto „Zweistimmiger Gesang" | +1 Darbietung beim Singen |
| Empf. „Nichtschläfer" | Nichtschläfer-Besonderheit |
| Typ. Nachteil „Lichtempfindlich" | Handicap `Lichtempfindlich` (auto) |
| Typ. Nachteil „Raubtiergeruch" | optional via `Strenger Körpergeruch` (nicht auto) |

---

## 3. Angepasste Spezies

| Volk | Änderung | DSA-Bezug |
|------|----------|-----------|
| **Ork** | Handicap `Strenger Körpergeruch` ergänzt (Heimlichkeit −2 ggü. Geruchssinn-Wesen, −1 Überreden höfisch) | DSA: Stechender Orkgeruch |
| **Achaz** | Besonderheit „Widerstand gegen Naturgewalten (Hitze: +4 Resistenz, −4 Schaden)" ergänzt | DSA: Achaz sind hitzeresistent; Kälte-Anfälligkeit war bereits vorhanden |

---

## 4. voelker_selected — Aufräumung

**Vorher (15, größtenteils veraltet):** Elf, Gnom, Halbelf, Halbling, Halbork, Ifrits,
Mensch, Oreads, Zwerg, Android, Aquarianer, Avionen, Halbelfe, Rakashaner, Saurianer —
nur `Mensch` auf `True`; die meisten Keys entsprachen **nicht** den tatsächlichen Völkern.

**Nachher (12 DSA-Spezies, alle `True`):** Mensch, Elf, Halbelf, Zwerg, Ork, Halbork,
Goblin, Achaz, Necker, Drachling, Holberker, Nachtalb.

---

## 5. Validierung

- [x] JSON valide & lädt
- [x] Semantischer Diff: 0 alte Völker verloren; nur `Ork` + `Achaz` geändert (wie geplant)
- [x] Talente, Handicaps, Mächte, Ausrüstung, Settingregeln, Fertigkeiten unverändert
- [x] Neue Völker schema-identisch zu `Elf`
- [x] Verwendete Attribute (`Konstitution`, `Verstand`, `Geschicklichkeit`) & Fertigkeiten (`Überleben`, `Wahrnehmung`) existieren im Setting
- [x] `test_volk_funktionen.py`: **46/46 pass** (nach Mock-Fix, siehe unten)
- [ ] In-App-Test: neue Völker im „Neuer Charakter"-Wizard wählbar (offen, Phase 11)

### ✅ Test-Bug behoben (2026-06-03)
`test_waehle_freies_attribut` / `test_waehle_halbelf_attribut` schlugen fehl
(„von W4 auf W4 erhöht"). Ursache war **kein Produktiv-Bug**, sondern der Test-Mock:
`MockAttribut.wert` und `MockWuerfel.value` waren entkoppelt und replizierten nicht die
Binding-Synchronisation des echten Modells (`models/attribut.py` bindet
`wuerfel.value → wert`). Fix: `MockAttribut.wert`/`.modifier` als Properties über
`wuerfel` umgesetzt → spiegelt das echte Verhalten. Beide Tests grün, keine Regression.

---

## 5b. Offene Review-Punkte aus Pass 1 (historisch)

- **Holberker:** ✅ erledigt 2026-06-03 – auf `Konstitution +2` (⇒ +1 Robustheit)
  reduziert, separater `robustheit_bonus` entfernt.
- ~~**Nachtalb:** „Nächtliche Begabung"~~ → hinfällig, Nachtalb in Pass 2 gelöscht.
- **Kultur-Handicaps** (`Hitzeempfindlich`/`Kälteempfindlich`/`Strenger Körpergeruch`)
  sind aktuell nur bei Ork/Achaz hinterlegt; Menschen-Kulturen (Tulamiden,
  Thorwaler, Waldmenschen) folgen ggf. in einer Kultur-Phase.

---

## 7. DSA-Spezifisch-Pass (2026-06-03, `scripts/dsa_voelker_spezifisch.py`)

Ziel: Die generischen Fantasy-Kompendium-Spezies passten nicht 100 % zu DSA
(„Goblins sind keine Savage-Pathfinder-Goblins"). Auf Basis der DSA-Spezies-Stat-Blocks
geschärft + nicht passende Spezies entfernt.

### 6.1 Gelöscht
- **Necker**, **Drachling** (nicht auf der DSA-Spezies-Übersicht)
- **Nachtalb** (auf User-Wunsch entfernt, obwohl offiziell)

### 6.2 DSA-Schärfungen

| Volk | Änderung | DSA-Bezug |
|------|----------|-----------|
| **Elf** | Attribute **GES W6 + WIL W6** (geschickt + **intuitiv**, kein Verstand-Bonus mehr) · Geschärfte Sinne = Wahrnehmung W6 · Schlank + Zwei linke Hände · + **Harmonische Magie** (verdoppelt Wirkungsdauer der gewirkten Mächte) · + Zweistimmiger Gesang · + Nichtschläfer | Elfen intuitiv, nicht verstandsgetrieben; Auto Zauberer/Zweistimmiger Gesang, Nichtschläfer (empf.) |
| **Goblin** | **Rework**: Ges +2 (statt +4), Willenskraft −1 (MU/KL −1), Geschärfte Sinne (Gehör/Geruch → Wahrnehmung +2), Biss, Aberglaube; **raus**: „Alles essen", Fähiger Reiter, Überlebenskünstler, Wärmesicht | FF+1/GE+1, Dunkelsicht I, Herausragender Sinn (Gehör/Geruch), klein, Schlechte Eigenschaft (Aberglaube) |
| **Halbork** | **Rework**: KO +1 / Zäher Hund (statt Stärke-Brute) · Außenseiter (leicht) | KO +1, CH −1, Auto Zäher Hund |
| **Ork** | + Biss (Hauer) · + Natürlicher Rüstungsschutz I | empf. Biss I, Natürlicher Rüstungsschutz I |

> **Nachjustierung 2026-06-03 (User-Feedback):**
> - **Elf:** Verstand-Bonus → **Willenskraft** (Intuition); Elfen sind intuitiv, nicht
>   verstandsgetrieben. Attribute jetzt GES W6 + WIL W6 + Wahrnehmung W6.
> - **Orkgeruch entfernt bei Ork *und* Halbork** – `Außenseiter` reicht (vorher inkonsistent:
>   nur einer hatte ihn). `strenger_koerpergeruch`-Flag bei beiden raus.
>
> **Nachjustierung 2 (2026-06-03, Review-Feedback):**
> - **Elf:** `Konstitution −1` **entfernt** – erzeugte die ungültige Anzeige „W4-1/W3"
>   (Attribute gehen nicht unter W4). Frailty jetzt sauber über das Handicap **Schlank**.
> - **Schlank in die Engine verdrahtet** (`functions/abgeleitete_werte.py`): gibt jetzt
>   echte **−1 Robustheit** (war vorher nur kosmetischer Text – §8.7-Fall). Elf-Robustheit = 3.
> - **Elfenmagie:** „Freie Wiederholung gegen gegnerische Mächte" entfernt → „Elfen sind von
>   Natur aus magiebegabt und können zaubern" (rein beschreibend; `elfenmagie`-Flag ist nur ein
>   Parser-Keyword, keine Code-Mechanik).
> - **Geschärfte Sinne** (Goblin) auf die Elf-Schreibweise vereinheitlicht:
>   „Wahrnehmung W6 statt W4, Maximum W12+1" statt „+2 auf Wahrnehmung" (Würfelstufen, kein „+2").
> - **Holberker Richtungssinn:** „+2 auf Überleben" → „Überleben W6 statt W4".
> - ✅ **Goblin & Holberker W4-1 aufgelöst** (User-Entscheid „in Handicap umwandeln"):
>   - **Goblin:** `Willenskraft −1` → Handicap **`Selbstzweifel`** (−1 Willenskraft-Proben, auto).
>   - **Holberker:** `Verstand −1` → Handicap **`Ungebildet`** (verstandbasierte Fertigkeiten
>     schwerer steigerbar, auto).
>   - Volks-`auto_handicaps` laufen über `volk.py` (setzen nur `ausgewaehlt`) → gewähren
>     **keine** Handicap-Punkte (kein Build-Exploit). **Jetzt nirgends mehr ein W4-1-Attribut.**
| **Zwerg** | + Nichtschwimmer · + Hitzeresistenz | empf. Unfähig (Schwimmen), typ. Hitzeresistenz |
| **Halbelf** | + Zweistimmiger Gesang | typ. Zweistimmiger Gesang |

### 6.3 Mechanik-Hinweis (vgl. Plan §8.7)

Greifen **generisch** (kein Hardcoding nötig):
- Attribut-Boni (`attribute_bonuses`), `groesse_modifikator` (Goblin −1),
  `panzerung_1` (Ork/Goblin natürliche Panzerung), `auto_handicaps`
  (Goblin → `Abergläubisch`, Zwerg → `Nichtschwimmer`, Halbork → `Außenseiter_leicht`).

Rein **beschreibend** (UI-Text, GM-/Spieler-Anwendung, keine Engine-Automatik):
- **Harmonische Magie**, Zweistimmiger Gesang, Nichtschläfer, Biss, Geschärfte Sinne,
  Hitzeresistenz, Zäher Hund. (Konsistent mit bestehenden Besonderheiten wie Achaz „Biss".)

### 6.4 Validierung Pass 2
- [x] JSON valide · 9 Völker · andere Bereiche (Talente/Handicaps/Mächte/Ausrüstung) unverändert
- [x] Reworkte Völker schema-identisch zu `Elf`
- [x] `test_volk_funktionen.py`: 46/46 grün
- [x] auto_handicap-Keys verifiziert (`Abergläubisch`, `Nichtschwimmer`, `Außenseiter_leicht`)
- [ ] In-App-Test der 9 Völker im Wizard (offen, Phase 11)

### 7.5 Offene Balance-/Design-Fragen
- **Elf:** ✅ angepasst – GES W6 + WIL W6 (intuitiv) statt Ges/Verstand. (Weiterhin zwei
  +2-Boni; im SW-Idiom bewusst, bei Bedarf auf einen reduzieren.)
- **Mensch**: DSA-Kulturvarianten (Mittelländer/Tulamiden/Thorwaler/Nivesen/Waldmenschen) mit je eigenen typ. Vor-/Nachteilen noch nicht als Wahl abgebildet (Kultur-Phase).
- **Achaz**: bereits reptilientauglich (Biss, Panzerung +2, Kälte-Anfälligkeit, Hitzeresistenz) – DSA-konform, kein weiterer Handlungsbedarf.
