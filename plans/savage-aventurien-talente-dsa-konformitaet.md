# Plan: SP/FK-Talente im Setting „Savage Aventurien" auf DSA-Konformität prüfen

**Datei-Status:** Planungs- + Fortschrittsdokument
**Erstellt am:** 2026-06-05
**Letztes Update:** 2026-06-05 (Strategie-Erweiterung: breiterer Ansatz + Klassentalente → Hintergrund; Review-Korrekturen)
**Verwandter Plan:** `logs/dsa_konvertierungs_plan.md` (Gesamt-Konvertierung: Völker, Mächte, Handicaps, Ausrüstung). Dieser Plan hier ist der **Talent-Teilplan**; die Talent-Strategie hier hat Vorrang vor `dsa_konvertierungs_plan.md §7.1` ("alle 22 Klassen bleiben" ist überholt).
**Quellen:**
- `settings/Savage Aventurien.json` (Ziel-Setting)
- `settings/Savage Pathfinder.json` (SP-Quelle)
- `settings/Fantasy Kompendium.json` (FK-Quelle)
- `Texte/Wildes_Aventurien.pdf` + `Texte/Wildes-Aventurien-V2.3.pdf` (**offizielle SW-DSA-Konversion** — kanonische SW-Terminologie, bereits integriert: `scripts/dsa_add_wildes_aventurien.py`, Abgleich `logs/wildes_aventurien_abgleich.md`)
- `Texte/dsa_lexikon.json` (DSA-Zauber/Liturgien/Rituale, 684 Einträge)
- `Texte/Kodex_der_Magie.pdf` (DSA-Magie-Traditionen)
- `Texte/Kodex_der_Helden.pdf` (DSA-Professionen, Völker, Archetypen)
- `Texte/Kodex_des_Götterwirkens.pdf` (DSA-Götter, Geweihte, Liturgien)

---

## 0. Wichtige Grundsätze (verbindlich für alle Änderungen)

1. **Generische SW-Begriffe statt DSA-Regelmechanik**
   - ❌ KEINE DSA-Regeltermini in Talent-Beschreibungen: `AsP` (Astralenergie), `QS` (Qualitätsstufe), `LE` (Lebensenergie), `KdV` (Karmadifferenz), `AP` als Abenteuerpunkte, `FW` (Fertigkeitswert), `GdV`, `ZfW`, `VW`
   - ✅ Savage Worlds Standard: **Machtpunkte (MP), Bennys, Würfeltypen (W4–W12+2), Erleichterungen/Erschwernisse, Wild Die, Aktionen, Runden, Attribute (GES/VER/STÄ/KON/WIL)**
   - Beispiel: „kostet 4–12 AsP pro Stunde" → „kostet 1–2 Machtpunkte pro Stunde"
2. **Namen dürfen DSA-spezifisch sein** (z.B. „Gjalsker Tierkrieger", „Boron", „Rondra", „Ferkina") — aber die Mechanik wird in SW-Terminologie beschrieben
3. **Schamanen-Traditionen** (Ferkina, Gjalsker, Fjarninger, Nivesen, Ork-Blutkrieger, Tahaya, Trollzacker) sind als kulturelle Animisten-Stammestraditionen erlaubt
4. **Verbotene Klassen-Konzepte**: PF2 Klassen (Alchemist, Barbarian, Magus, Sorcerer, Oracle, Warlock, Witch, Summoner/Eidolon, Ninja, Gunslinger, Shifter, etc.) sind in DSA kein Klassen-Konzept. Werden zu Berufs-/Hintergrund-Talenten oder gelöscht

### 0bis. Erweiterte Strategie (Stand 2026-06-05, verbindlich)

5. **Breiterer Ansatz — SP/FK-Talente weiternutzen, wo es geht**
   - Talente aus Savage Pathfinder (SP) und Fantasy Kompendium (FK) werden **behalten**, wo sich eine **sinnvolle DSA-Lösung** findet (Umbenennung, generische SW-Mechanik, DSA-Trapping/Flair).
   - **Nur Talente, die wir nicht sauber zuweisen können, kommen raus** (Status 3). Löschen ist die Ausnahme, nicht die Regel — vorher prüfen, ob ein DSA-Pendant existiert.
6. **DSA-Kodex-Essenz × FK/SWPF in Einklang bringen (aktuelle Hauptaufgabe)**
   - Die Essenz der DSA-Kodex-Dateien (`Kodex_der_Magie/Helden/Götterwirken`, `dsa_lexikon.json`) wird extrahiert und mit den bestehenden FK-/SWPF-Talenten **harmonisiert**: gleiche Mechanik, DSA-Begriff/Flair obendrauf.
   - **Wildes Aventurien** (offizielle SW-DSA-Konversion) ist dabei die **kanonische SW-Terminologie-Referenz** und hat bei Namens-/Traditions-Fragen Vorrang vor ad-hoc-Übersetzungen aus den DSA5-Hardcovern. Etablierte WA-Begriffe: `AH (Magie)` + Vorteil `Gildenmagier`, `AH (Wunder: Gott)`, `AH (Schamanismus)`, `AH (Fey)` (Elfen), `AH (Tiergeister)` (Tiergeist-Bindung), Traditionsartefakte `Magierstab`/`Druidendolch`.
7. **Klassentalente → normale Hintergrund-Talente (NEU, verbindlich)**
   - DSA kennt **kein Klassensystem**, sondern Professionen/Hintergründe. Daher werden alle **Klassen-Basistalente** (Kategorie `Klasse`, 14 Stück) zu **`Hintergrund`-Talenten** umgewandelt (DSA-Profession als Hintergrund).
   - Klassen-**spezifische** Folge-Talente (Kategorien `Magier`, `Mönch`, `Druide`, `Paladin`, `Inquisitor`, `Barbar`, `Kämpfer`, … ) bleiben mechanisch erhalten, werden aber DSA-konform umkategorisiert (Profession/Tradition statt „Klasse").
   - Voraussetzungen, die auf Klassen-Talente verweisen (z.B. „Mindestens zwei X-Talente", prereq `[Klassenname]`), müssen beim Umbau **mitgezogen** werden — sonst entstehen verwaiste Voraussetzungen (siehe Review-Befund Wandler, §3 Schritt 3).
8. **Talentnamen nur umbenennen, wenn nötig (User-Vorgabe 2026-06-05)**
   - Ziel: **größtmögliche Kompatibilität zum Savage-Worlds-Regelwerk**. SW-Talentnamen bleiben, wo möglich.
   - DSA-Flair primär über **Beschreibung/Fluff** (Trapping, Profession, Tradition im Beschreibungstext), **nicht** über Umbenennung. Umbenennen nur, wenn der SW-Name inhaltlich falsch/irreführend für DSA ist (z.B. PF2-Klassen-Konzepte).
   - Konsequenz für die früheren Kategorie-B/C-Tabellen (§4): die dort vorgeschlagenen Massen-Umbenennungen (`Boron X`, `Rondra X`, `Praios X` …) werden **zurückgestuft** — bevorzugt Fluff statt Rename.

### 0ter. User-Entscheidungen (2026-06-05, verbindlich)

| Thema | Entscheidung |
|---|---|
| **Neue magische Traditionen** | `AH (Geode)`, `AH (Kristallomant)`, `AH (Zibilja)`, `AH (Zaubertänzer)` als **je eigener Arkaner Hintergrund** ergänzen (Status 4). ✅ angelegt (§10). |
| **Akademisch vs. intuitiv** | Zwei Zauberfertigkeiten: **`Zaubern` (Verstand)** = akademisch (Gildenmagier/Klugheit-Traditionen) · NEU **`Magie` (Willenskraft)** = intuitiv (Intuition/Charisma-Traditionen). Intuitive AHs bekommen Voraussetzung **WIL W6 statt VER W6**. Kodex-Leiteigenschaft entscheidet: Geode (Charisma) & Zibilja (Intuition) → `Magie`; Kristallomant (Klugheit) → bleibt `Zaubern`; Zaubertänzer (Charisma) → `Darbietung`. Bestehende intuitive **Hexe** & **Hexer/Hexe** ebenfalls auf `Magie` umgestellt. Gildenmagier-Zweige (Elementarist/Illusionist/Nekromant/Beschwörer) bleiben `Zaubern`. |
| **Geweihte / Wunder** | **Je Gottheit ein eigenes `AH (Wunder: Gott)`.** Umfang: **12 Alveranische + 6 Halbgötter** (Aves, Ifirn, Kor, Nandus, Swafnir, Angrosch) = **18**. **Außeralveranische werden weggelassen** (KEIN Rastullah, Namenloser, Levthan, Tairach, Kha). |
| **Geweihten-Talente** | Zu jeder Kirche gibt es **Traditions-Sonderfertigkeiten** (z.B. *Rahja: Durchhaltevermögen*), die als charakteristisches Geweihten-Talent **konvertiert** werden. |
| **Gildenmagier** | `AH (Magier)` bleibt **wie es ist — einer reicht** (keine separaten Grau-/Weiß-/Schwarzmagier-Zweige). |
| **Weltliche Berufe** | **Reiner Fluff** — keine neuen Talente. SW-**Expertentalente** (Dieb, Soldat, Gelehrter, Akrobat, Ass am Steuer …) decken sie ab; DSA-Beruf nur im Beschreibungstext. |
| **Vorgehen** | **Einzeln & überlegt**, Schritt für Schritt mit Bestätigung. |
| **Reihenfolge** | **Zuerst** die SP-AH/FK-AH-**Dopplungen auflösen** (§9), erst danach neue AHs. |

---

## 1. Ausgangslage

| Quelle | Talente in `Savage Aventurien.json` (Original) |
|---|---|
| Gesamt (Original) | **504** |
| Nur Aventurien (custom) | 16 (3,2 %) |
| Aus Savage Pathfinder (SP) | 466 (252 exklusiv + 214 mit FK) |
| Aus Fantasy Kompendium (FK) | 236 (22 exklusiv + 214 mit SP) |

**Befund:** 488 von 504 Talenten (96,8 %) stammen aus SP/FK. Der DSA-Eigenanteil ist sehr klein. Viele Talente enthalten PF2-Klassen-Konzepte, PF-Völker, D&D-Magieparadigmen und anachronistische Feuerwaffen.

**Aktueller Stand (nach 6 Schritten):** **469 Talente** (−35, ca. −7 %)
**Neu erstellt:** 0 — *Korrektur (Review 2026-06-05):* `AH (Magier)` war **bereits vor Schritt 1 vorhanden** (byte-identisch in Backup `pre_revolverheld`) und wurde **nicht** in Schritt 5 erstellt. Die −35-Bilanz geht ohne jede Neuerstellung auf (35 echte Löschungen, 4 Umbenennungen).
**Umbenannt:** 4 (Wandler → Gjalsker Tierkrieger, +3 abhängige Talente). ⚠️ **Unvollständig:** Das 4. Wandler-Kategorie-Talent `Verbesserte Defensive Instinkte` blieb mit `kategorie: "Wandler"` + Voraussetzung „Mindestens zwei Wandler-Talente" zurück → verwaiste Voraussetzung (offen, siehe §7).

---

## 2. DSA-Referenz (verbindlich für die Bewertung)

### 2.1 Boron — der Todesgott (NICHT Nekromant!)

> Quelle: `Kodex_des_Götterwirkens.pdf:1846ff`
>
> *„Das Plündern von Leichen ist dem Gott ebenso verhasst wie Untote, und wo immer solch abscheuliche Kreaturen existieren, werden die Geweihten des Gottes alles daransetzen, sie zu vernichten."*
>
> *Tradition (Boronkirche) als Sonderfertigkeit — Untotenschreck: Borongeweihte Waffen richten doppelten Schaden gegen Untote an.*
>
> Feindbilder der Boronkirche: **„Totenschändung, Entweihung der Totenruhe, Grabraub, Nekromantie"** (Z. 1922)
>
> Orden: **Golgariten** (Kämpferorden), Basaltfaust, Rabengarde, Hand Borons.
>
> Heiliges Tier: Rabe.
>
> Aspekte: Dunkelheit, Ruhe, Schlaf, Schweigen, Tod, Vergessen.

**Konsequenz für die Planung:**
- Boron-Geweihte sind **TOTENFEINDE**, sie kämpfen GEGEN Untote und Nekromanten
- Ein „Blutlinie des Grabes" o.ä. als Boron-Talent ist **falsch** – das wäre Dämonenpaktierer/Seelenpaktierer/Nekromant (verbotene Tradition)
- „Untote zerstören" als Kleriker-Talent passt zu Boron (Untotenschreck), aber NICHT zu „positiver Energie kanalisieren" (D&D-Konzept)

### 2.2 DSA-Magie-Traditionen

> Quelle: `Kodex_der_Magie.pdf`, Kapitel 2 (S. 34ff), Traditionen-Übersicht S. 79

**Kanonische Traditionen:**
- **Gildenmagier** (mit Zweigen: Verwandlungs-Zweig, Seekrieg-Zweig, Selbstverwandler-Zweig, Fremdverwandler-Zweig, Philosophen-Zweig …) → **ersetzt durch `AH (Magier)`** (Schritt 5)
- **Druiden**
- **Schamanen** (mit Animisten / Geoden-Variante)
- **Hexen** (Hexenkessel, Hexenflüche, Vertraute)
- **Kristallomanten** (Kristallkugel, kein traditionelles AsP-System)
- **Geweihte** (separate Sonderfertigkeit pro Gott; eigene Tradition je Kirche)
- **Zauberalchimisten**
- **Zibilja** (Ritualmagier)
- **Zauberbarden** (Khunchomer / Sangara) und **Zaubertänzer** (Alhanisch)
- **Geoden** (zwergische Tradition)

**Schwarze / Verbotene Traditionen:**
- **Paktierer** (Minderpaktierer, Seelenpaktierer) – Pakt mit Erzdämon
- **Dämonenpaktierer** (siehe `Kodex_der_Magie.pdf` S. 214ff: „Die Kreise der Verdammnis")
- **Borbaradianer** (Kult des Namenlosen, Pakt mit dem „Dritten" Erzdämon)

### 2.3 DSA-Völker (im Helden-Kodex bestätigt)

`Kodex_der_Helden.pdf` enthält: Elf, Halbelf, Zwerg, Ork, Goblin, Achaz, Holberker, Mensch.
**Nicht** im Helden-Kodex enthalten: Gnom, Halbling, Aasimar, Tiefling, Oread, Undine, Ifrit, Sylphe, Tengu, Kitsune.

### 2.4 Drachen in Aventurien

- Drachen existieren als „alte Verbündete"
- Echte DSA-Archetypen: **Xorloscher Drachenkämpfer**, **Drachenkult**, **Drachenei-Akademie** (Graumagier)
- **Es gibt KEINEN „Drachenblutlinien"-Sorcerer** wie in PF2
- → `AH (Zauberer) Drachenblutlinie` und `Drachenjünger` sind entfernt (Schritt 3a)

### 2.5 Gjalsker Tierkrieger (DSA-Verwandlungsmagier-Analogon)

> Quelle: `Kodex_der_Magie.pdf` Z. 1950, 2274-2359; `Kodex_der_Helden.pdf` Z. 569 (Kultur Gjalsker, 34 AP)

- Kulturabhängige Animisten-Stammestradition der **Gjalsker** (Nordland-Volk, Thorwaler-verwandt)
- Bindung an **tierischen Patron-Geist (Durro-Dûn)**: Bär, Wolf, Falke, Eule, Feuermolch, Wildkatze, Vielfraß, Luchs, Rabe …
- **Tierkräfte I-III** (übermenschliche Merkmale)
- **Tierverwandlung** (Hauptform) und **mächtige Tierverwandlung** (Säbelzahntiger, Mammut, Nashorn)
- Traditionsartefakt: **Krallenkette** (Metallkette)
- → **Wandler-Klasse umbenannt zu `Gjalsker Tierkrieger`** (Schritt 3b/3d)

### 2.6 Schwarze Schwellen / Limbus

- In Aventurien gibt es **Limbus** (Zwischenreich) als jenseitige Ebene
- KEINE **Elementarebenen** im PF2-Sinn → `Elementare Reise` entfernt (Schritt 4)
- Dschinne (Feuer-, Eis-, Luft-, Erde-, Wasserdschinn) sind eigenständige magische Wesen

---

## 3. Fortschritts-Übersicht (alle durchgeführten Änderungen)

### Schritt 1 — Revolverheld-Block entfernt ✅ (Backup: `pre_revolverheld_20260605.json`)

6 Talente entfernt (Deadlaws/Gunslinger-Import, anachronistisch für Standard-Aventurien):
- `Revolverheld` (Klasse)
- `Zielen (Revolverheld)`
- `Todesschuss (Revolverheld)`
- `Extra Schneid`
- `Betrug des Todes`
- `Todesschütze` (zusätzlich, abhängig)

### Schritt 2 — Gnom/Halbling/Ancestries entfernt ✅ (Backup: `pre_gnomhalbling_20260605.json`)

5 Talente entfernt (PF-Ancestries, keine DSA-Völker):
- `Gnomenmagie`
- `Glücklicher Halbling`
- `Oread-Gräber`
- `Wasserabstammung` (Undine)
- `Himmlischer Diener` (Aasimar)

### Schritt 3 — Drachen-Linie + Wandler → Gjalsker Tierkrieger ✅ (Backups: `pre_drachenj_20260605.json`, `pre_tierkrieger_20260605.json`)

**3a) Entfernt (4 Talente):**
- `AH (Zauberer) Drachenblutlinie`
- `Drachenjünger` (I, II, III)

**3a) Text-Fix:**
- `Klingenzahn` — wörtliche PF-Referenz „nach Pathfinder-Regeln" entfernt (→ Halbork-Stoßzahn-Biss)

**3b) Umbenannt (4 Talente):**
- `Wandler` → `Gjalsker Tierkrieger` (Hintergrund, Voraussetzung: Kultur: Gjalsker)
- `Wandler-Tiergestalt` → `Tierverwandlung (Gjalsker)`
- `Verbesserte Form (Wandler)` → `Mächtige Tierverwandlung`
- `Erweiterter Aspekt` → `Ausdauernde Tiergestalt`

**3c) Entfernt (1 Talent):**
- `Chimären-Aspekt` (PF2 Shifter-spezifisch, passt nicht zu Gjalsker Mono-Patron-Tradition)

**3d) Gjalsker-Beschreibungen generisch:**
- AsP/QS-Verweise raus, generische SW-Machtpunkte und Stufenangaben (1 Stunde / 1 Tag / 1 Woche) statt QS-Stunden
- „Animistenkräfte" → „Merkmale" (um DSA-Begriff zu vermeiden)

### Schritt 4 — Weitere PF2-Spezifika entfernt ✅ (Backup: `pre_generic_20260605.json`)

9 Talente entfernt:
- `Kreuzblütig` (PF2 Crossblooded Sorcery)
- `Elementare Reise` (PF Elementar-Ebenen)
- `Zornprophet` I/II/III (kein DSA-Konzept)
- `Horizontwanderer` I/II (PF2 Horizon Walker)
- `Böser Blick` (Hexer/Hexe, PF2 Evil Eye)
- `Untoter Vertrauter` (PF Necromancer-Familiar)

### Schritt 5 — AH (Zauberer) komplett raus + Klingenzahn raus + AH (Magier) neu ✅ (Backup: `pre_ah_zauberer_20260605.json`)

**Bestand bestätigt (KEINE Neuerstellung — Review-Korrektur 2026-06-05):**
- `AH (Magier)` (Hintergrund) existierte bereits vor Schritt 1 (byte-identisch in `pre_revolverheld`). Ist-Werte: VER W6 + Okkultismus W6, Arkane Fertigkeit Zaubern (Verstand), **15 MP, `neue_maechte: 6`** (NICHT „3" wie ursprünglich notiert), `auto_talente: [Zauberbücher, Arkane Verbindung, Schule]`, `auto_handicaps: [Behindernde Rüstung_jede, Behindernde_Rüstung_schwer, Materialkomponenten]`.
- ⚠️ **Namens-Inkonsistenz (offen):** Talent heißt `AH (Magier)`, aber 5 abhängige Talente (`Kraftlinienmagie`, `Kugelzauber`, `Magischer Alltag`, `Zauberbücher`) und das `Zauberer`-Talent fordern als Voraussetzung `AH (Magie)`. Wildes-Aventurien-kanonisch ist `AH (Magie)` (+ Vorteil `Gildenmagier`) → empfohlene Auflösung: Talent in `AH (Magie)` umbenennen oder Prereqs auf `AH (Magier)` vereinheitlichen.

**Entfernt (7 Talente):**
- `AH (Zauberer)` (Base)
- `AH (Zauberer) Abnorme Blutlinie`
- `AH (Zauberer) Arkane Blutlinie`
- `AH (Zauberer) Blutlinie des Grabes`
- `AH (Zauberer) Dämonische Blutlinie`
- `AH (Zauberer) Elementare Blutlinie`
- `Klingenzahn` (final — User-Korrektur, passt doch nicht zu DSA)

**Prereq-Update (3 Talente):** `Große Macht`, `Phänomenale Macht`, `Blutlinie` → Voraussetzung von `AH (Zauberer)` auf `AH (Magier)` umgestellt

### Schritt 6 — Blutlinie-Talente raus ✅ (Backup: `pre_blutlinie_20260605.json`)

3 Talente entfernt (PF2 Sorcerer Bloodline-System):
- `Blutlinie`
- `Mächtige Blutlinie`
- `Einzigartige Blutlinie`

**Verbleibend in Kategorie „Zauberer" (4):** `Bevorzugte Mächte (Zauberer)`, `Arkane Meisterschaft (Zauberer)`, `Große Macht`, `Phänomenale Macht`

---

## 4. Geplante weitere Schritte (gemäß ursprünglichem Plan)

### Kategorie B — Umbenennen / DSA-Adaptieren (~40 Talente)

| Aktuelles Talent | Empfehlung | DSA-Äquivalent |
|---|---|---|
| `AH (Zauberer) Dämonische Blutlinie` | **ENTFERNT** (Schritt 5) | – |
| `AH (Zauberer) Blutlinie des Grabes` | **ENTFERNT** (Schritt 5) | – |
| `AH (Zauberer) Arkane Blutlinie` | **ENTFERNT** (Schritt 5) | – |
| `AH (Zauberer) Elementare Blutlinie` | **ENTFERNT** (Schritt 5) | – |
| `AH (Zauberer) Abnorme Blutlinie` | **ENTFERNT** (Schritt 5) | – |
| `Kreuzblütig` | **ENTFERNT** (Schritt 4) | – |
| `Untoter Vertrauter` | **ENTFERNT** (Schritt 4) | – |
| `Konstrukt-Vertrauter` | Umbenennen | `Homunculus-Vertrauter` |
| `Seelengefäß` | Umbenennen | `Seelenkäfig (Bann des Namenlosen)` |
| `Infernale Rüstung` | Umbenennen | `Dämonische Rüstung` |
| `Zorn der Hölle` | Umbenennen | `Dämonischer Zorn` |
| `Elementare Reise` | **ENTFERNT** (Schritt 4) | – |
| `Beschwörung` (Diabolist) | Umbenennen | `Dämonenbeschwörung` (verboten) |
| `Untote zerstören` (Kleriker) | Umbenennen | `Untotenschreck (Boron)` — exakt Boronkirchen-SF |
| `Böses Entdecken` (Paladin) | Umbenennen | `Göttliches Entdecken (Praios/Hesinde)` |
| `Böses Niederstrecken` (Paladin) | Umbenennen | `Rondras Zorn` |
| `Aura der Gerechtigkeit` (Paladin) | Umbenennen | `Aura der Praioskirche` |
| `Aura der Tapferkeit` (Paladin) | Umbenennen | `Aura der Rondra` |
| `Mystische Mächte (Paladin)` | Umbenennen | `Geweihtenmächte (Rondra)` |
| `Mystische Mächte (Inquisitor)` | Umbenennen | `Geweihtenmächte (Boron)` |
| `Bann` (Inquisitor) | Umbenennen | `Borons Bann` |
| `Brandmal` (Inquisitor) | Umbenennen | `Borons Mal` |
| `Schwäche ausnutzen` (Inquisitor) | Umbenennen | `Schwäche ausnutzen (Boron)` |
| `Wahres Urteil` (Inquisitor) | Umbenennen | `Urteil der Boronkirche` |
| `Hexenflüche` (Hexe) | **Behalten** | Echte DSA-Mechanik |
| `Böser Blick` (Hexer/Hexe) | **ENTFERNT** (Schritt 4) | – |

### Kategorie C — Klassen → Hintergrund-Talente umwandeln (14 `Klasse`-Talente)

> **Strategie-Update 2026-06-05:** Gemäß Grundsatz 7 werden die Klassen **nicht nur umbenannt, sondern in `kategorie: "Hintergrund"` überführt** (DSA-Profession statt Klasse). Namen folgen — wo vorhanden — Wildes Aventurien. Die klassenspezifischen Folge-Talent-Kategorien (Magier 13, Mönch 10, Druide 9, Beschwörer 9, Barde 7, Kleriker 7, Barbar 6, Paladin 6, Inquisitor 6, Waldläufer 5, Alchemist 5, Hexe 5, Kämpfer 4, Hexenmeister 4, Kavalier 4, Zauberer 4, Magus 4, Ninja 4, Schurke 3, Orakel 3, Diabolist 3, Schamane 3, Elementarmagier 2, Illusionist 2, Tüftler 2, Hexer/Hexe 1, Nekromant 1, Wandler 1) bleiben mechanisch erhalten und werden auf die jeweilige DSA-Profession/Tradition umkategorisiert. Beim Umbenennen einer Klasse: **alle Voraussetzungen** der Folge-Talente (prereq `[Klassenname]`, „Mindestens zwei X-Talente") mitziehen.

| Aktuelles Talent | Empfehlung | DSA-Pendant |
|---|---|---|
| `Alchemist` (Klasse) | Umbenennen zu `Alchimist` (Hintergrund) | Zauberalchimist (DSA-Profession) |
| `AH (Alchemist)` | Umbenennen zu `AH (Alchimist)` | s.o. |
| `Barbar` (Klasse) | Umbenennen zu `Barbar (Thorwaler)` | Thorwaler als „Barbaren" Aventuriens |
| `Inquisitor` (Klasse) | Umbenennen zu `Inquisitor (Boron)` | Boronkirche-Ordensmitglied |
| `Kavalier` (Klasse) | Umbenennen zu `Turnierritter` | DSA-Turnier-Kultur (Weiden, Gareth, Al'Anfa) |
| `Kämpfer` (Klasse) | Umbenennen zu `Krieger (Beruf)` | Söldner / Berufskrieger |
| `Magus` (Klasse) | Löschen oder umbenennen | Gildenmagier + Kampf-Spez. (selten) |
| `Mönch` (Klasse) | Umkategorisieren zu „Hintergrund" | DSA-Mönch (Hesinde/Peraine-Kloster) |
| `Ninja` (Klasse) | **Löschen** (passt nicht zu Aventurien) | – |
| `Paladin` (Klasse) | Umbenennen zu `Ritter (Rondrageweihter)` | Rondra = Göttin des Kampfes |
| `Schurke` (Klasse) | Umbenennen zu `Dieb` (Hintergrund) | DSA-Beruf (Phex-Kirche, Gilde) |
| `Waldläufer` (Klasse) | Umbenennen zu `Wildnisläufer` | Echte DSA-Profession |
| `Wandler` (Klasse) | **UMBENANNT** zu `Gjalsker Tierkrieger` (Schritt 3) | – |
| `AH (Hexe)` | Umbenennen zu `AH (Hexe – Aventurien-Tradition)` | Echte DSA-Hexe |
| `AH (Hexenmeister)` | Löschen oder umbenennen zu `AH (Dämonenpaktierer)` | Passt nicht zu DSA |
| `AH (Orakel)` | Umbenennen zu `AH (Geschicksdeuterin/Seherin)` | Hesinde-Seher, Godi, Zahori |
| `AH (Beschwörer)` | Umbenennen zu `AH (Dämonenbeschwörer) [verboten]` | Verbotene schwarze Tradition |
| `AH (Tüftler)` | Umbenennen zu `AH (Mechanikus)` | DSA-Tüftler (Myranor/Brabak) |
| `AH (Diabolist)` | Umbenennen zu `AH (Dämonologe) [verboten]` | Pfad des Namenlosen |
| `AH (Hexer/Hexe)` | **Behalten** | Echte DSA-Tradition |

### Kategorie D — PF2-Prestige-Klassen (~20 Talente)

| Talent | Empfehlung | DSA-Äquivalent |
|---|---|---|
| `Arkaner Betrüger` (I-III) | Umbenennen zu `Arkaner Dieb` | Dieb mit Gildenmagier-Vorbackground |
| `Arkaner Bogenschütze` (I-III) | Behalten als `Arkaner Bogenschütze (Elf)` | Elfen-Magie-Tradition |
| `Assassine` (I-III) | Umbenennen zu `Killari` | Echte DSA-Profession |
| `Drachenjünger` (I-III) | **ENTFERNT** (Schritt 3) | – |
| `Duellant` (I-III) | Umbenennen zu `Fechtmeister` | DSA-Beruf |
| `Heiliger Verteidiger` (I-III) | Umbenennen zu `Heiliger Verteidiger (Rondra)` | Rondra-Kirche-Ordensritter |
| `Horizontwanderer` (I/II) | **ENTFERNT** (Schritt 4) | – |
| `Kundschafter-Chronist` (I-III) | Löschen oder umbenennen | – |
| `Meisteralchemist` (I-III) | Umbenennen zu `Meister der Alchimie` | – |
| `Meisterspion` (I-III) | Umbenennen zu `Killari-Meister` | – |
| `Mystischer Ritter` (I-III) | Umbenennen zu `Rondra-Ritter` | Rondra-Ordensritter |
| `Mystischer Theurg` (I-III) | Umbenennen zu `Doppelgeweihter` | Geweihter + Gildenmagier (selten) |
| `Naturwächter` (I-III) | Umbenennen zu `Druide der Alten Eiche` | Druide-Tradition |
| `Schattentänzer` (I-III) | Löschen oder umbenennen | – |
| `Schlachtherold` (I-III) | Umbenennen zu `Kriegsänger` | Zauberbarde-Tradition |
| `Unbeugsamer Verteidiger` (I-III) | Umbenennen zu `Unbeugsamer Rondra-Ritter` | – |
| `Wissenshüter` (I-III) | Umbenennen zu `Hesinde-Geweihter` | – |
| `Zornprophet` (I-III) | **ENTFERNT** (Schritt 4) | – |

### Kategorie E — Positiv-Liste (gut DSA-konform, NICHT anfassen)

Diese Talente sind bereits korrekt DSA-adaptiert:

- **Magier-Stab-Talente** (16x): `Bindung des Stabes`, `Fokus des Stabes`, `Flammenschwert`, `Kraftfokus`, `Kraftlinienmagie`, `Kugelzauber`, `Zauberspeicher`, `Zauberstab-Meisterschaft` – **Kraftlinien** sind eine echte DSA-Magie-Eigenheit
- `Eisenaffine Aura` – **Bann des Eisens** ist ein echtes DSA-Konzept
- `Bannlied`, `Klagelied` – Barden passen zu DSA
- `Mirakel`, `Prophezeien` – **Godi** und **Sterndeuter** sind DSA-Berufe
- `Magischer Alltag` – nennt `Sapefacta`, `Accuratum` (echte DSA-Zauber)
- `AH (Druide)`, `AH (Kleriker)`, `AH (Schamane)`, `AH (Magier)` (NEU), `AH (Elementarist)`, `AH (Illusionist)`, `AH (Nekromant)`, `AH (Barde)`, `AH (Hexer/Hexe)`, `AH (Begabt)`
- Combat-Talente: `Berserker`, `Kraftvoller Schlag`, `Einschüchterndes Niederstarren`, `Kampfrausch`, `Kundschafter`, `Flinker Angreifer`
- `Bindung mit der Natur`, `Naturgespür`, `Naturverbundenheit` – Druide-Themen
- `Tiergestalt`, `Tiermeister`, `Tierempathie` – Druide-/Schamanen-Themen
- `Elfenlieder` – Elfen-Magie in DSA
- `Hexenflüche` – Echte DSA-Hexen-Mechanik
- `Dolch des Druiden` – DSA-Druidendolch
- `Knochenkeule` – Schamanen-Waffe
- `Kraftlinienmagie` – DSA-Kraftlinien
- `Mirakel` – Echte Boron-/Rondra-Mirakel
- `Schelm` – Echte DSA-Profession

### Aventurien-Custom-Talente (15, alle behalten — Schritt 3 entfernte 1: `Chimären-Aspekt`)

`Bindung des Stabes`, `Dolch des Druiden`, `Eisenaffine Aura`, `Elfenlieder`, `Flammenschwert`, `Fokus des Stabes`, `Gjalsker Tierkrieger` (NEU), `Hexenflüche`, `Knochenkeule`, `Kraftfokus`, `Kraftlinienmagie`, `Kugelzauber`, `Magischer Alltag`, `Mirakel`, `Prophezeien`, `Schelm`, `Zauberspeicher`, `Tierverwandlung (Gjalsker)` (NEU), `Mächtige Tierverwandlung` (NEU), `Ausdauernde Tiergestalt` (NEU), `AH (Magier)` (NEU)

---

## 5. Statistik & Verifikation

| Metrik | Original | Aktuell | Delta |
|---|---|---|---|
| Talente gesamt | 504 | **503** | −35 (Löschungen) +34 (neue AH, §10/§11) |
| Kategorie „Revolverheld" | 5 | 0 | −5 |
| Kategorie „Klasse" | 22 | **0** ✅ | −22 (alle aufgelöst: Wandler→Gjalsker §3; 10 →Hintergrund + 4 umbenannt §12) |
| Kategorie „Gjalsker Tierkrieger" | 0 | 4 | +4 (neu) |
| Kategorie „Wandler" | 4 | 0 | −4 (umbenannt) |
| Kategorie „Zauberer" | 7 | 4 | −3 (Blutlinie-Talente raus) |
| Verwaiste Voraussetzungen | 0 | **0** ✅ | `Verbesserte Defensive Instinkte` → Gjalsker umgehängt (Schritt 0a) |
| Namens-Inkonsistenz `AH (Magie)`↔`AH (Magier)` | – | **0** ✅ | 5 Prereqs auf `AH (Magier)` korrigiert (Schritt 0b), kein Rename |
| Setting-Tests grün | 101 | 101 | OK (deckt Kategorie-/Prereq-Verwaisung nicht ab → eigener Check nötig) |

---

## 6. Backups (alle in `backup/settings/`)

| Backup-Datei | Schritt |
|---|---|
| `Savage Aventurien_pre_revolverheld_20260605.json` | Schritt 1 |
| `Savage Aventurien_pre_gnomhalbling_20260605.json` | Schritt 2 |
| `Savage Aventurien_pre_drachenj_20260605.json` | Schritt 3a |
| `Savage Aventurien_pre_tierkrieger_20260605.json` | Schritt 3b–d |
| `Savage Aventurien_pre_generic_20260605.json` | Schritt 4 |
| `Savage Aventurien_pre_ah_zauberer_20260605.json` | Schritt 5 |
| `Savage Aventurien_pre_blutlinie_20260605.json` | Schritt 6 |
| `Savage Aventurien_pre_ah_dopplung_20260605.json` | §9 (AH-Handicap-Dopplungen) |
| `Savage Aventurien_pre_namensbugfix_20260605.json` | §7 Schritt 0a/0b (Wandler-Waise + AH-Magier-Prereqs) |
| `Savage Aventurien_pre_klasse_hintergrund_20260606.json` | §12 (Kategorie C: Klasse→Hintergrund + 4 PF2-Umbenennungen) |
| `Savage Aventurien_pre_inquisitor_praios_20260606.json` | §13 (Inquisitor-Block → Praios/Bannstrahler-Fluff) |
| `Savage Aventurien_pre_geweihten_pool_20260606.json` | §13 (Paladin-Block → geteilter Geweihten-Pool + Engine-Wildcard) |
| `Savage Aventurien_pre_seher_aufloesen_20260606.json` | §13.5 (AH (Seher) auflösen → prophetische Talente in Pool + name-Feld-Fix) |

---

## 7. Nächste Schritte

**Sofort-Korrekturen aus dem Review — ✅ ERLEDIGT 2026-06-05 (Backup: `pre_namensbugfix_20260605.json`):**

0a. ✅ **Wandler-Waise geschlossen:** `Verbesserte Defensive Instinkte` → `kategorie: "Gjalsker Tierkrieger"`, Voraussetzung → „Mindestens zwei Gjalsker Tierkrieger-Talente". (Gjalsker-Kategorie jetzt 4 Talente.)
0b. ✅ **`AH (Magie)`→`AH (Magier)` vereinheitlicht** (5 Talente: `Zauberbücher`, `Zauberer`, `Kraftlinienmagie`, `Kugelzauber`, `Magischer Alltag`). **Entscheidung (Grundsatz 8):** KEIN Talent umbenannt — die 5 falschen Prereqs auf den existierenden Namen `AH (Magier)` korrigiert (9 Geschwister-Talente nutzten ihn bereits; beide Quell-Settings nennen ihn so). Verwaiste Voraussetzungen jetzt **0**.
0c. **Plan-Selbstkonsistenz:** §3.6 „Verbleibend in Kategorie Zauberer (4)" verifiziert = `Bevorzugte Mächte (Zauberer)`, `Arkane Meisterschaft (Zauberer)`, `Große Macht`, `Phänomenale Macht`; das Basis-`Zauberer`-Talent (kategorie `Macht`) existiert weiterhin → bei Klasse→Hintergrund-Umbau (Grundsatz 7) mitbehandeln.

**Hauptaufgabe (DSA-Kodex-Essenz × FK/SWPF harmonisieren) — empfohlene Reihenfolge, je mit User-Bestätigung pro Schritt:**

1. ✅ **Kategorie C – Klassen → Hintergrund (14 `Klasse`-Talente): ERLEDIGT 2026-06-06** (siehe §12, Backup `pre_klasse_hintergrund_20260606.json`). 10 weltliche/legitime Professionen nur umgehängt (kein Rename, Grundsatz 8); 4 PF2-Klassen umbenannt: Ninja→Meuchler, Magus→Schwertmagier, AH (Hexenmeister)→AH (Paktierer), AH (Orakel)→AH (Seher). 0 `Klasse` übrig, Tests grün.
2. ✅ **Kategorie B – Inquisitor-Block (6×) → Praios/Bannstrahler: ERLEDIGT 2026-06-06** (§13). **Korrektur gegenüber Erstplanung:** Inquisitor ist DSA **Praios** (Heilige Inquisition / Orden vom Bannstrahl), **nicht Boron** (Quelle: Kodex des Götterwirkens). Name behalten (DSA-kanonisch), nur Beschreibungen reflavored.
3. ✅ **Kategorie B – Paladin-Block (6×) → geteilter Geweihten-Pool: ERLEDIGT 2026-06-06** (§13). Statt feste Götter-Pakete: **alle göttlichen Kampf-/Wirk-Talente in einen für ALLE Geweihten wählbaren Pool** (Vor: neuer Engine-Wildcard `AH (Wunder: beliebig)`). User-Entscheidung „jeder Geweihten-Spieler schnürt sein eigenes Paket".
4. **Kategorie B – Übrige PF2-Spezifika** (`Konstrukt-Vertrauter`, `Seelengefäß`, `Infernale Rüstung`, `Zorn der Hölle`, `Beschwörung`): DSA-Pendant prüfen, sonst Status 3.
5. **Kategorie D – Prestige-Klassen (44 Talente, Kategorie `Prestige`)**: einzeln prüfen — behalten mit DSA-Mapping (Grundsatz 5) oder Status 3, wenn nicht sauber zuweisbar.
6. **Querschnitt – DSA-Essenz-Abgleich**: pro behaltenem SP/FK-Talent prüfen, ob DSA-Kodex/`dsa_lexikon`/WA ein Trapping/Flair beisteuert (z.B. ikonische Zaubernamen), ohne die SW-Mechanik zu ändern.

**Verifikation nach jedem Schritt:** Talentzahl, **Prereq-Integrität** (keine verwaisten `[Talent]`/„zwei X-Talente"-Verweise), Kategorie-Konsistenz, Setting-Tests grün.

**Stand: 2026-06-05, nach Schritt 6 + Strategie-Erweiterung (Review).**

---

## 8. DSA-Kodex-Abgleich: Fluff-Kandidaten & Lücken (2026-06-05)

> Methode: Volltext aus `Kodex_der_Helden/Magie/Götterwirken.pdf` (pdftotext) gegen die 469 vorhandenen Talente abgeglichen. Die DSA-Professions-/Traditions-Taxonomie stammt aus dem Helden-Kodex-Inhaltsverzeichnis (Zaubererprofessionen / Geweihtenprofessionen / Weltliche Professionen).

### 8.1 Fluff-Kandidaten — vorhandenes SP/FK-Talent → DSA-Konzept (Mechanik behalten, DSA-Name/Flair drauf)

| Vorhandene Talente | DSA-Konzept (Fluff) | Kodex-Beleg |
|---|---|---|
| `Bindung des Stabes`, `Fokus des Stabes`, `Zauberspeicher`, `Zauberstab-Meisterschaft`, `Kraftfokus` | **Stabzauber** (Gildenmagier-Stabmagie) | Magie: „Stabzauber" ×62 |
| `Eisenaffine Aura` | **Bann des Eisens** | Magie ×11 |
| `Kraftlinienmagie` | **Kraftlinien** | Magie ×11 |
| `Artefakterschaffer`, `Meisterlicher Artefakterschaffer` | **Artefaktmagie / Apporte** | Magie: „Artefakt" ×55, „Apport" ×75 |
| `Vertrauter`, `Verbesserter/Entwickelter Vertrauter`, `Konstrukt-Vertrauter` | **Vertrautentier** (Hexe/Magier) | Magie: „Vertrautentier" ×62 |
| `Tiergestalt`, `Wahre Form`, `Schnelle Verwandlung` | **Gestaltwandel / Salander** (Druiden/Animisten) | Magie: „Animist" ×57 |
| `Bestienflüsterer`, `Tierempathie`, `Tiermeister` | **Animisten-Tierbann / Druidische Tierfreundschaft** | Magie: „Animist" ×57 |
| `Heiler`, `Schnelle Heilung`, `Gnade`, `Energie fokussieren` | **Peraine-/Travia-Heiltradition** | Götter: „Peraine" ×76 |
| `Mirakel`, `Untote zerstören` | **Mirakel / Boron-Untotenschreck** | Götter: „Boron" ×37, „Mirakel" ×17 |
| `Prophezeien`, `Sechster Sinn`, `Offenbarung`, `Große Offenbarung` | **Hellsicht / Hesinde-Auguren, Zahori, Sternkundige** | Magie: „Kristallomant" (Hellsicht) ×63 |
| `Gelehrter`, `Wissenshüter` (I–III) | **Hesinde-Magister / Gelehrter** | Götter: „Hesinde" ×68 |
| `Giftmischer`, `Chemiker`, `Meisterlicher Alchemist`, `Meisteralchemist` (I–III) | **Zauberalchimist / Giftmischer** | Magie: „Zauberalchimist" ×13 |
| `Hexenflüche`, `Großer/Grandioser/Zusätzlicher Hex` | **Hexenflüche / Verwünschungen** | Magie: „Hexe" ×164 |
| `Schelm`, `Täuscher`, `Scharfzüngig`, `Lässiger Illusionist` | **Scharlatan / Schelmische Magie** | Magie: „Scharlatan" ×43 |
| `Ritter`, `Ordensfähigkeit`, `Panier`, Kavalier-Block | **Ritterorden** (Theaterritter, Schwerterorden …) | Götter: „Orden" ×259 |
| `Soldat`, `Kämpferisches Können`, `Waffenspezialisierung`, `Berserker`, `Kampfrausch` | **Söldner / Krieger / Gardist / Thorwaler-Berserker** | Helden: Söldner ×31, Krieger ×108 |
| `Knochenkeule`, `Geweihter Fetisch`, `Urtümliche Magie` | **Schamanen-Stammestradition** (Ferkina/Gjalsker …) | ✓ bereits DSA |
| `Elfenlieder` | **Elfische Lieder (AH Fey)** | Magie: „Elf" ×33 |
| `Bann`, `Brandmal`, `Wahres Urteil` (Inquisitor) | **Praios-/Boron-Inquisition** (Hexenjäger) | Helden: „Hexenjäger", Götter: „Praios" ×123 |

### 8.2 Lücken — DSA-Konzepte OHNE jede Talent-Abbildung (Kandidaten für Status 4 / Repurposing)

**A) Magische Traditionen (im Helden-Kodex eigene Zaubererprofessionen, hier 0 Talente):**
| DSA-Tradition | Status | Lösungsidee |
|---|---|---|
| **Geode** (zwergische Erz-/Kristallmagie) | ❌ fehlt | Neues `AH (Geode)` oder Fluff über `Steingespür`/Erd-Mächte; zwergisch, Verstand-/Willenskraft-basiert |
| **Kristallomant** (Kristallmagie, Hellsicht) | ❌ fehlt | `AH (Kristallomant)`; verbindet Hellsicht-Mächte mit Kristall-Traditionsartefakt |
| **Zibilja** (tulamidische Ritualmagierin) | ❌ fehlt | `AH (Zibilja)` (Ritualmagie) oder Fluff über `AH (Magier)`-Variante |
| **Zaubertänzer** (Tanzmagie, Tulamiden/Novadis) | ❌ fehlt | `AH (Zaubertänzer)` — Darbietung-/Tanz-basiert (wie `AH (Barde)`, aber Tanz) |
| **Gildenmagier-Zweige** Grau-/Weiß-/Schwarzmagier, Qabalothe, Gildenlose | ⚠️ nur generisch | `AH (Magie)` deckt nur „den Magier" ab; Zweige als optionale Folge-Talente/Fluff |

**B) Geweihte / Kirchen — die göttliche Seite ist DÜNN.** Aktuell nur `AH (Kleriker)`, `Mirakel`, `Untote zerstören`, `Gnade`, `Energie fokussieren`, `Bevorzugte/Göttliche Meisterschaft (Kleriker)`. DSA hat dagegen separate Traditionen pro Gott:
- **12 Alveranische:** Praios, Rondra, Efferd, Travia, Boron, Hesinde, Firun, Tsa, Phex, Peraine, Ingerimm, Rahja (alle im Götter-Kodex ×27–123 belegt).
- **Halbgötter:** Aves, Ifirn, Kor, Nandus, Swafnir, Angrosch.
- **Außeralveranisch / fremd:** Rastullah (×55), Der Namenlose (×173), Levthan, Tairach, Kha.
→ Großes Fluff-/Status-4-Feld: pro Kirche ein `AH (Wunder: Gott)` (WA-Schema) + 1–2 charakteristische Geweihten-Talente. Vgl. Kategorie-B-Plan (Boron/Rondra/Praios) — dort nur 3 von 12+ angefangen.

**C) Weltliche Professionen ohne Talent-Pendant:**
| DSA-Beruf | Status | Lösungsidee |
|---|---|---|
| **Schmied / Handwerksmeister** | ❌ fehlt | Hintergrund-Talent „Schmiedemeister" (+ Reparieren/Waffen); `Zwergischer Schmied` war im Master-Plan §7.3 geplant |
| **Kurtisane** | ❌ fehlt | Sozial-Talent (Rahja-nah); Fluff über `Attraktiv`/`Charismatisch` + neues „Kurtisane" |
| **Seefahrer / Pirat / Thorwaler** | ❌ fehlt | Hintergrund „Seemann" (Boot fahren); Master-Plan §7.3 „Thorwaler Seemann" |
| **Novadi / Wüstenkrieger (Rastullah)** | ❌ fehlt | Kämpfer-Hintergrund + Rastullah-Glaube |
| **Gladiator** | ❌ fehlt | Kampf-Hintergrund (Arena); Fluff über vorhandene Kampf-Talente |

### 8.3 Empfehlung / Priorisierung

1. **Zuerst Fluff (8.1) ohne Mechanik-Änderung** — billig, hoher DSA-Gewinn: nur Beschreibungen/Namen, deckt die Hauptmasse der SP/FK-Talente ab.
2. **Geweihten-Seite (8.2-B) ausbauen** — größte inhaltliche Lücke; mit dem laufenden Kategorie-B-Plan (Boron/Rondra/Praios) zusammenlegen und auf alle 12 Götter erweitern.
3. **Magische Sondertraditionen (8.2-A)** — Geode/Kristallomant/Zibilja/Zaubertänzer als optionale `AH (…)` ergänzen (Status 4), wenn gewünscht; sonst bewusst Status 5 (weglassen).
4. **Weltliche Berufe (8.2-C)** — teils bereits im Master-Plan §7.3 vorgesehen (Zwergischer Schmied, Thorwaler Seemann, Wüstensohn); dort konsolidieren.

> ~~Offene User-Entscheidung~~ **Entschieden (2026-06-05, siehe §0ter):** 8.2-A → 4 neue AH (Geode/Kristallomant/Zibilja/Zaubertänzer). 8.2-B → 18 neue `AH (Wunder: Gott)` (12 Alveranische + 6 Halbgötter), Außeralveranische weggelassen. 8.2-C (weltliche Berufe) → nur Fluff, keine neuen Talente.

---

## 9. AH-Dopplungen SP × FK auflösen ✅ ERLEDIGT 2026-06-05 (Backup: `pre_ah_dopplung_20260605.json`)

> **Ergebnis:** Kanonische Familie = **FK/Unterstrich** (SWADE-Standard). SP-Familie in 8 Talenten umgeschrieben (Mapping: `_leicht`→`Behindernde_Rüstung_leicht`/−2; `_jede`→`Behindernde_Rüstung_schwer`/−4; `_mittelschwer`→`Behindernde_Rüstung_schwer`/−4), Dubletten entfernt, 3 SP-Katalog-Einträge gelöscht. Verifiziert: 0 SP-Rest-Referenzen, 469 Talente unverändert, keine verwaisten `auto_handicaps`, Setting-Tests grün (75 passed / 8988 subtests). Betroffen: `AH (Barde)`, `AH (Druide)`, `AH (Magier)`, `AH (Hexenmeister)`, `AH (Hexe)`, `AH (Orakel)`, `Alchemist`, `Magus`.

### 9.1 Befund (verifiziert 2026-06-05)

Das Setting ist ein Merge aus Savage Pathfinder (SP) und Fantasy Kompendium (FK). 12 AH-Namen existieren in **beiden** Quellen. Der Merge hat für mehrere AHs SP+FK **kombiniert** und dabei **doppelte Handicaps mit unterschiedlicher Schreibweise** in dieselbe `auto_handicaps`-Liste geschrieben.

**Kern-Ursache — zwei Handicap-Familien im Katalog (dasselbe SWADE-Handicap „Behindernde Rüstung", doppelt modelliert):**

| Familie | Keys | Stufen | Herkunft |
|---|---|---|---|
| **SP** (Leerzeichen) | `Behindernde Rüstung_jede`, `Behindernde Rüstung_leicht`, `Behindernde Rüstung_mittelschwer` | alle „schwer"/2 Pkt | Savage Pathfinder |
| **FK** (Unterstrich) | `Behindernde_Rüstung_leicht` (leicht/1 Pkt), `Behindernde_Rüstung_schwer` (schwer/2 Pkt) | leicht/schwer | Fantasy Kompendium = **SWADE-Standard** |

Beide Familien sind als getrennte Einträge im Handicap-Katalog vorhanden und werden quer referenziert (SP-Variante 8×, FK-Variante 9× in `auto_handicaps`).

**Betroffene AHs mit Doppel-/Misch-Referenz (Aventurien-Ist):**
| AH | `auto_handicaps` (Ist) | Problem |
|---|---|---|
| `AH (Barde)` | `Behindernde Rüstung_leicht` **+** `Behindernde_Rüstung_leicht` | dasselbe Handicap doppelt (Leer+Unterstrich) |
| `AH (Druide)` | `Schwur_schwer`, `Behindernde Rüstung_leicht` **+** `Behindernde_Rüstung_leicht`, `Materialkomponenten` | dito doppelt |
| `AH (Magier)` | `Behindernde Rüstung_jede` **+** `Behindernde_Rüstung_schwer`, `Materialkomponenten` | zwei verschiedene Rüstungs-Restriktionen gleichzeitig |
| `AH (Kleriker)` | `Schwur_schwer` + SP-`auto_talente` (Gnade, Energie fokussieren) | Merge-Hybrid (Talente aus SP, Basis aus FK) — funktional ok, aber prüfen |

Weitere Merge-Hybride (FK-Basis + SP-`auto_talente`, ohne Handicap-Dopplung): `AH (Barde)`/`AH (Druide)`/`AH (Magier)` ziehen SP-Auto-Talente mit — gewollt behalten, nur Handicaps bereinigen.

### 9.2 Empfehlung

1. **Eine Behindernde-Rüstung-Familie als kanonisch festlegen** → Empfehlung: **FK/Unterstrich** (`Behindernde_Rüstung_leicht/schwer`), weil = SWADE-Standard (leicht=−2, schwer=−4) → Grundsatz „größtmögliche SW-Kompatibilität".
2. SP-Familie (`Behindernde Rüstung_*` mit Leerzeichen) aus den AH-`auto_handicaps` auf die FK-Keys **umschreiben**, Dubletten entfernen.
3. SP-Familien-Einträge im Handicap-Katalog erst löschen, wenn **kein** Talent/Volk/Handicap sie mehr referenziert (vorher repo-weiten Ref-Check fahren — auch andere Settings teilen ggf. den Katalog nicht, aber sicher ist sicher).
4. Mapping SP→FK: `_jede`→`_schwer`, `_mittelschwer`→`_schwer`, `_leicht`(SP, ist real „schwer") → **prüfen** (SP-`Behindernde Rüstung_leicht` hat `stufe: schwer`/2 Pkt, FK-`Behindernde_Rüstung_leicht` hat `stufe: leicht`/1 Pkt → **inhaltlicher Unterschied!** Pro AH entscheiden, welche Schwere gemeint ist).

> ✅ **Entschieden & umgesetzt (§9 oben):** (a) FK/Unterstrich kanonisch. (b) SP-`leicht`→FK-`leicht` (−2, regelkonform).

---

## 10. Schritt 1 — Neue Arkane Hintergründe + intuitive Zauberfertigkeit ✅ ERLEDIGT 2026-06-05

> Backups: `pre_neue_ah_traditionen_20260605.json` (4 neue AH), `pre_magie_willenskraft_20260605.json` (Magie-Skill + intuitive Umstellung), `pre_ah_fey_20260605.json` (AH (Fey)).

### 10.1 Zwei Zauberfertigkeiten (akademisch vs. intuitiv)

- **`Zaubern` (Verstand)** — akademische Magie (Gildenmagier & Klugheit-Traditionen). Unverändert.
- **`Magie` (Willenskraft)** — NEU, intuitive Magie (Intuition/Charisma-Traditionen **und elfische Fey-Magie**). `fertigkeiten_daten["Magie"] = ["Willenskraft"]`, in `_BEKANNTE_ARKANE_FERTIGKEITEN` (functions/volk_funktionen.py) aufgenommen.
- *Entscheidung (User):* AH (Fey) nutzt **`Magie`** als Skill — KEIN separater „Fey"-Skill (entgegen WA-Wortlaut „Fey (Willenskraft)"; Skill-Konsolidierung gewünscht).
- Intuitive AHs: Voraussetzung **WIL W6 statt VER W6**.
- Engine-Hinweis: Skill-Name = ein Attribut (aus `fertigkeiten_daten`); der Parser (`extrahiere_arkane_fertigkeit_aus_ah`) liest den Namen **vor der Klammer** → Skillnamen müssen klammerfrei sein (`Magie`, `Fey` ✓).

### 10.2 Angelegte AHs (alle `kategorie: Hintergrund`, `rang: A`, 10 MP)

| AH | Skill (Attr) | Mächte | Voraussetzung | auto_handicaps | Traditionsartefakt / Fluff |
|---|---|---|---|---|---|
| `AH (Geode)` | **Magie (WIL)** | 5 | WIL W6, Volk: Zwerg | Behindernde_Rüstung_schwer, Materialkomponenten | Lebensring (zwergisch) |
| `AH (Kristallomant)` | Zaubern (VER) | 5 | VER W6 | Behindernde_Rüstung_schwer, Materialkomponenten | Kristallkugel (achaz-nah) |
| `AH (Zibilja)` | **Magie (WIL)** | 5 | WIL W6 | Behindernde_Rüstung_schwer, Materialkomponenten | Sippenchronik (tulamidisch) |
| `AH (Zaubertänzer)` | Darbietung (WIL) | 4 | WIL W6 | Behindernde_Rüstung_leicht, Materialkomponenten | Zauberkleidung (Tanzmagie) |
| `AH (Fey)` | **Magie (WIL)** | 2 | WIL W6, Elf/Halbelf | Behindernde_Rüstung_leicht | elfische Magie; alle Elfen zaubern (WA). *badoc bewusst gestrichen — nicht alle Elfen sind badoc.* |

### 10.3 Bestehende intuitive AHs umgestellt (Zaubern→Magie, VER→WIL)

- `AH (Hexe)` (Hexen = intuitiv) — zugleich fehlerhaftes Beschreibungs-Parsing repariert (extrahierte vorher „Zaubern], Behindernde Rüstung").
- `AH (Hexer/Hexe)`.
- Gildenmagier-Zweige (`AH (Elementarist/Illusionist/Nekromant/Beschwörer/Diabolist)`) bleiben akademisch (`Zaubern`/Verstand).

**Verifikation:** Talente 469→**474** (+5 neue AH). Parser liefert für alle intuitiven AHs `Magie`/`Fey` → Willenskraft; akademische unverändert `Zaubern`/Verstand. Setting-/Volk-/Fertigkeit-Tests grün.

---

## 11. Schritt 2 — `AH (Wunder: Gott)` je Gottheit (✅ KOMPLETT, 18/18)

> Umfang: **12 Alveranische + 6 Halbgötter = 18** (Außeralveranische bewusst weggelassen). Backup je Gott.

### 11.1 Template (User-bestätigt 2026-06-05)
- **AH (Wunder: Gott)**: `kategorie: Hintergrund`, `rang: A`, Arkane Fertigkeit **Glaube (Willenskraft)**, **10 MP**, **3 neue Mächte**, Voraussetzung **WIL W6**, `auto_handicaps: [Schwur_schwer]` (= verbindlicher Moralkodex/Tabu der Kirche). Beschreibung mit Aspekten + heiligem Symbol.
- **Je 1 Traditions-Sonderfertigkeit** wird vom AH via `auto_talente` mitaktiviert (User-Vorgabe). **Reihenfolge der Wahl:**
  1. **Bestehendes SW-Talent bevorzugen**, wenn es thematisch passt (z.B. Phex→`Glück`, Tsa→`Schnelle Heilung`, Rondra→`Mutig`).
  2. Nur sonst ein **neues** Talent `kategorie: Geweihter`, `rang: A`, Voraussetzung = jeweiliges AH.
- ⚠️ **KEINE DSA-Regelbegriffe** in Beschreibungen (kein LeP, AsP, „Furcht-Stufe I–IV", Regenerationsphase, FP, QS). Nur SW-Mechanik (Bennies, Würfeltypen, +2/−2, Wunden, natürliche Heilungsprobe, Furchttabelle). Lehre aus Tsa/Phex/Rondra-Korrektur 2026-06-05.
- Vorgehen: **Dreierblöcke**.

### 11.2 Fortschritt (18/18 ✅)

| # | Gott | AH | Traditions-SF (Talent, auto_talente) | Status |
|--:|---|---|---|:--:|
| 1 | **Praios** (Götterfürst; Sonne/Ordnung/Recht/Magiebann) | `AH (Wunder: Praios)` | **Arkane Resistenz** (bestehendes SW-Talent; −2 für gegnerische Mächte) | ✅ |
| 2 | **Rondra** (Löwin; Kampf/Ehre/Sturm) | `AH (Wunder: Rondra)` | **Mutig** (bestehendes SW-Talent; +2 Furchtproben) | ✅ |
| 3 | **Efferd** (Gezeiten; Meer/Wetter/Schifffahrt) | `AH (Wunder: Efferd)` | **Meister des Meeres (Efferd)** — +2 Bootfahren/Schwimmen/Navigation | ✅ |
| 4 | **Travia** (Gütige Mutter; Heim/Familie/Treue) | `AH (Wunder: Travia)` | **Heimstatt (Travia)** — bis 3 Gefährten +2 natürliche Heilung beim Rasten im Haus | ✅ |
| 5 | **Boron** (der Schweigsame; Tod/Ruhe/Dunkelheit) | `AH (Wunder: Boron)` | **Untotenschreck (Boron)** — +2 Schaden gegen Untote (DSA: doppelt) | ✅ |
| 6 | **Hesinde** (Allwissende; Wissen/Magie/Schlange) | `AH (Wunder: Hesinde)` | **Scharfe Sinne (Hesinde)** — +2 Wahrnehmung gegen Illusionen/Täuschung | ✅ |
| 7 | **Firun** (Weißer Jäger; Eis/Winter/Jagd) | `AH (Wunder: Firun)` | **Wildniskunde (Firun)** — +2 Überleben/Spuren lesen in Wildnis/Winter | ✅ |
| 8 | **Tsa** (junge Göttin; Geburt/Leben/Wandel) | `AH (Wunder: Tsa)` | **Schnelle Heilung** (bestehendes SW-Talent; +2 natürliche Heilung) | ✅ |
| 9 | **Phex** (der Listenreiche; Diebstahl/Glück/Schatten) | `AH (Wunder: Phex)` | **Glück** (bestehendes SW-Talent; +1 Benny) | ✅ |
| 10 | **Peraine** (die Gütige; Heilkunst/Ackerbau) | `AH (Wunder: Peraine)` | **Widerstandsfähigkeit gegen Krankheiten (Peraine)** — +2 vs Krankheit/Gift, Krankheiten nur leicht | ✅ |
| 11 | **Ingerimm** (Himmlischer Schmied; Feuer/Handwerk) | `AH (Wunder: Ingerimm)` | **Feuerschutz (Ingerimm)** — +2 vs Feuer/Hitze, −2 Feuerschaden | ✅ |
| 12 | **Rahja** (Schöne Göttin; Liebe/Freude/Wein) | `AH (Wunder: Rahja)` | **Durchhaltevermögen (Rahja)** — +2 um Angeschlagen zu beenden | ✅ |
| 13 | **Aves** (Herr des Horizontes; Reise/Schicksal) *[Halbgott]* | `AH (Wunder: Aves)` | **Wegfindung (Aves)** — +2 Orientierung/Reisen, verirrt sich nicht | ✅ |
| 14 | **Ifirn** (Schwanengleiche, Tochter Firuns) *[Halbgott]* | `AH (Wunder: Ifirn)` | **Innere Wärme (Ifirn)** — +2 vs Kälte, −2 Kälteschaden | ✅ |
| 15 | **Kor** (Herr der Schlachten; Kampf/Sold) *[Halbgott]* | `AH (Wunder: Kor)` | **Schmerzresistenz** (bestehend; ignoriert eine Stufe Wundabzüge) | ✅ |
| 16 | **Nandus** (Halbgott des Wissens) *[Halbgott]* | `AH (Wunder: Nandus)` | **Gelehrter** (bestehend; +2 Wissensfertigkeit) | ✅ |
| 17 | **Swafnir** (Gottwal; Thorwaler/Seefahrt) *[Halbgott]* | `AH (Wunder: Swafnir)` | **Anführer** (bestehend; rallyt Verbündete im Befehlsradius) | ✅ |
| 18 | **Angrosch** (zwergischer Schmiedegott ≈ Ingerimm) *[Halbgott, Volk: Zwerg]* | `AH (Wunder: Angrosch)` | **Feuerschutz (Angrosch)** — +2 vs Feuer/Hitze, −2 Feuerschaden | ✅ |

**Backups:** `pre_ah_wunder_praios_`, `_block2_` … `_block6_`, `_fix_phextsa_`. **Stand:** 503 Talente, Tests grün (116).
**Bestehende SW-Talente als Geweihten-SF:** Praios→`Arkane Resistenz`, Rondra→`Mutig`, Tsa→`Schnelle Heilung`, Phex→`Glück`, Kor→`Schmerzresistenz`, Nandus→`Gelehrter`, Swafnir→`Anführer`. **Neue SF (Kategorie `Geweihter`, 11):** Efferd, Travia, Boron, Hesinde, Firun, Peraine, Ingerimm, Rahja, Aves, Ifirn, Angrosch.

---

## 12. Kategorie C — Klassen → Hintergrund (✅ ERLEDIGT 2026-06-06)

> Grundsatz 7 (DSA hat kein Klassensystem) + Grundsatz 8 (nur umbenennen wenn nötig). Backup: `pre_klasse_hintergrund_20260606.json`. Talentzahl unverändert (503, reine Umkategorisierung/Umbenennung, keine Löschung).

### 12.1 Nur umgehängt (Klasse → Hintergrund, **kein** Rename) — 10 Talente
Weltliche bzw. für DSA legitime Professionen; SW-Name DSA-tauglich, DSA-Flair bleibt der späteren Querschnitts-Beschreibungspflege (§7.6) überlassen:
`Barbar`, `Kämpfer`, `Mönch`, `Paladin`, `Schurke`, `Waldläufer`, `Kavalier`, `Inquisitor`, `Alchemist`, `AH (Hexe)`.
- Folge-Kategorien (`Barbar`, `Mönch`, `Paladin`, `Schurke`, `Waldläufer`, `Inquisitor`, `Kavalier`, `Alchemist`, `Kämpfer`, `Hexe`) bleiben als Gruppierung erhalten; deren Voraussetzungen waren nicht betroffen.

### 12.2 Umbenannt (4 PF2-Klassenkonzepte, User-Entscheidung 2026-06-06)
Folge-Kategorie, Voraussetzungen (`[Klasse]`, „Mindestens zwei X-Talente/-Vorteile") und Beschreibungen jeweils mitgezogen; PF/asiatisches Flair entfernt:

| Alt | Neu | Folge-Talente (mit umbenannt) | Mechanik-Anpassung |
|---|---|---|---|
| `Ninja` | **`Meuchler`** (Hintergrund) | `Keine Spur`, `Meister-Ninja-Trick`→`Meister-Meuchler-Trick`, `Ki-Ladung`→`Präparierte Klinge`, `Unsichtbare Klinge` | Ki-/Mystik-Fluff raus → mundaner Auftragsmörder (Killari-nah) |
| `Magus` | **`Schwertmagier`** (Hintergrund) | `Zauberstab-Meisterschaft`, `Zaubererinnerung`, `Gegenschlag (Magus)`→`Gegenschlag (Schwertmagier)`, `Wahrer Magus`→`Wahrer Schwertmagier` | seltene Gildenmagier-Kampftradition; Mechanik unverändert |
| `AH (Hexenmeister)` | **`AH (Paktierer)`** (Hintergrund) | `Weitere/Starke/Mächtige Hexerei`, `Arkane Meisterschaft (Hexenmeister)`→`(Paktierer)` | **intuitiv: Skill Zaubern→`Magie`, Vor VER W6→WIL W6**; verbotene schwarze Tradition (Dämonenpakt); „Hexen"→„Paktierer/Verfluchungen" |
| `AH (Orakel)` | **`AH (Seher)`** (Hintergrund) | `Offenbarung`, `Göttliche Meisterschaft`, `Große Offenbarung` | Glaube/WIL bleibt; Geschicksdeuter/Hellsicht-Fluff (Hesinde-Augur, Zahori, Godi) |

### 12.3 Verifikation
- `Klasse`-Talente: **0** ✅. Talente gesamt: **503** (unverändert).
- Parser `extrahiere_arkane_fertigkeit_aus_ah`: `AH (Paktierer)`→`Magie`/Willenskraft, `AH (Seher)`→`Glaube`/Willenskraft ✅.
- Keine verwaisten `auto_talente`; keine Alt-Namen-Reste (Ninja/Magus/Hexenmeister/Orakel) in Namen/Voraussetzungen/Kategorien. Setting-Tests grün (42).
- **Vorbestehende (nicht von diesem Schritt verursachte) Beobachtung:** drei Voraussetzungen nutzen Plural-Form gegen Singular-Kategorie — `Mindestens zwei Schurken-Talente` (Kat. `Schurke`), `Mindestens zwei Hexen-Talente` (Kat. `Hexe`), `Mindestens zwei Druiden-Talente` (Kat. `Druide`). Funktional über die Prereq-Prüfung abgedeckt; ggf. später kosmetisch vereinheitlichen.

---

## 13. Kategorie B — Geweihten-Talente (Inquisitor → Praios; Paladin → geteilter Pool) (✅ ERLEDIGT 2026-06-06)

> Quelle: `Kodex_des_Götterwirkens.pdf` (pdftotext-Recherche). Backups: `pre_inquisitor_praios_`, `pre_geweihten_pool_`.

### 13.1 DSA-Befund (Götterwirken)
- **Inquisitor = Praios.** *Heilige Inquisition der Praioskirche* + *Orden vom Bannstrahl* (Bannstrahler, fanatischer **Laienorden**, „Feuer und Schwert", Ziel: Verbot jeder Magie). Tradition (Praioskirche) = **Magieschutz** = bereits gesetztes `Arkane Resistenz` bei `AH (Wunder: Praios)`. → frühere Erstplanung „Inquisitor → Boron" war **falsch**.
- **Golgariten = Boron** (berittener Untotenjäger-Orden, „Kampf vom Pferderücken", Rabenschnabel) — als DSA-Beleg geführt; floss ins generische Pool-Reframing (Streitross/Unheiliges) ein, **nicht** als eigenes Paket.

### 13.2 Inquisitor-Block → Praios (nur Reflavoring, Namen + Mechanik unverändert)
`Inquisitor` (Hintergrund, Laienorden — **kein AH nötig**) + Folge-Talente `Bann`, `Brandmal`, `Mystische Mächte (Inquisitor)`, `Schwäche ausnutzen`, `Wahres Urteil`, `Gebrandmarkt für Vergeltung`: Beschreibungen auf Praios/Heilige Inquisition/Bannstrahler umgestellt; Feindbild = Dämonen, Untote, Ketzer, verbotene Magie.

### 13.3 Paladin-Block → geteilter Geweihten-Pool (User-Entscheidung: kein festes Götter-Paket)
**Engine-Erweiterung** (`functions/talent_funktionen.py`, `_pruefe_einzelne_voraussetzung`): neuer Wildcard **`AH (Wunder: beliebig)`** / `AH (Wunder)` = „hat irgendein `AH (Wunder: …)`" (= ist Geweihter). Funktional getestet (Geweihter ✓ / Magier abgelehnt).

- **Basis `Paladin` gelöscht** (dekomponiert; `auto_handicap: Ehrenkodex` → Geweihte haben ohnehin `Schwur_schwer` via AH; `Aura der Tapferkeit` bleibt als eigenständiges `Übersinnlich`-Talent erhalten).
- **6 Folge-Talente → Kategorie `Geweihter`, Vor `AH (Wunder: beliebig)`**, „böse"/D&D-Alignment durch DSA-Feindbild ersetzt:

| alt (Paladin) | neu (Pool) | Vor. |
|---|---|---|
| Böses Niederstrecken | **Niederstrecken des Unheiligen** | AH (Wunder: beliebig) |
| Aura der Gerechtigkeit | **Geweihte Aura** | AH (Wunder: beliebig) + Niederstrecken des Unheiligen |
| Böses Entdecken | **Das Unheilige erspüren** | AH (Wunder: beliebig) |
| Reittier (Paladin) | **Gesegnetes Streitross** | AH (Wunder: beliebig) |
| Gnade (Paladin) | **Lindernde Hand** (Heilung/Linderung) | AH (Wunder: beliebig) |
| Mystische Mächte (Paladin) | **Kampfsegen** (10 gewidmete MP, Kampf-/Heil-Liturgien) | AH (Wunder: beliebig) |

- **Extern:** `Heiliger Champion` (Legendär) Vor → `AH (Wunder: beliebig)` + „Mindestens zwei Geweihter-Talente", „Böses-Niederstrecken" → „Niederstrecken des Unheiligen". `Schlachtherold` Vor `Kavalier oder Paladin` → `Kavalier oder AH (Wunder: beliebig)`.

### 13.4 Verifikation
- Talente 503 → **502** (Basis Paladin gelöscht, sonst Umbenennung/Recat). Kategorie `Paladin`: **0**. Kategorie `Geweihter`: **17** (11 Götter-SF + 6 Pool). Keine Waisen (Prereq/auto_talente). Tests grün (115).
- **Vorbestehende Engine-Lücke (nicht behoben, breiter Scope):** `"Mindestens zwei X-Talente"` wird vom Validator nicht ausgewertet (fällt auf Talent-Namens-Lookup → „nicht gefunden"). Betrifft viele Settings (Wahres Urteil, Mächtige Hexerei, Heiliger Champion …). Konvention beibehalten.

### 13.5 Seher-Auflösung → prophetische Talente im Pool (✅ ERLEDIGT 2026-06-06)
> Backup `pre_seher_aufloesen_20260606.json`. User-Entscheidung: „AH Seher auflösen und prophetische Talente allen Geweihten zugänglich machen."
- **`AH (Seher)` gelöscht** (502 → **501** Talente). Prophetie ist jetzt Gabe **jedes** Geweihten (der via `AH (Wunder: Gott)` ohnehin Glaube + MP + Mächte hat), kein eigener AH mehr.
- **3 Folge-Talente → Geweihten-Pool** (Kategorie `Geweihter`, Vor `AH (Wunder: beliebig)`), „Seher/Mysterium" → generisch „Geweihter / göttliche Mächte": `Offenbarung`, `Göttliche Meisterschaft`, `Große Offenbarung`.
- **`Göttliche Einmischung`**: verwaiste Listen-Voraussetzung `AH (Kleriker, Seher, Wunder)` → `{oder: [AH (Kleriker), AH (Wunder: beliebig)]}`.
- **Nebeneffekt:** `Mirakel` (Vor `AH (Wunder)`) war zuvor durch Literal-Lookup unerfüllbar → durch den neuen Wildcard `AH (Wunder)` jetzt korrekt für alle Geweihten erfüllbar.
- **Bugfix nebenher:** 9 Talente hatten nach den §12-Renames ein veraltetes inneres `name`-Feld (≠ Dict-Key: Paktierer/Seher/Schwertmagier/Meuchler-Familien) → global `name = key` gesetzt.
- **Bereits offen abgedeckt:** `Prophezeien` (explizit „auch ohne Arkanen Hintergrund") und `Sechster Sinn` (kein Prereq) → unverändert. Geweihten-Pool jetzt **20** (11 Götter-SF + 6 Paladin-Pool + 3 prophetische). Tests grün (114).

### 13.6 Offen (optional)
- **Tsa/Peraine-Heilzweig:** im Pool-Modell decken `Lindernde Hand` + `Kampfsegen` (Heilung) das bereits ab; ggf. weitere Heil-Liturgie-Talente ergänzen.

---

## 14. Zweite Traditions-Sonderfertigkeit je Alveranischem Gott (✅ ERLEDIGT 2026-06-06)

> Quelle: `Kodex_des_Götterwirkens.pdf` – Abschnitte „Die Tradition (Xkirche) als Sonderfertigkeit". Jede der 12 Alveranischen Kirchen listet **zwei** echte Traditions-SFs; bisher war nur eine umgesetzt (§11). User-Wunsch: zweite ergänzen, wo möglich mit **bestehendem SW-Talent**. Backup `pre_zweite_tradition_sf_20260606.json`. Beide SFs werden vom `AH (Wunder: Gott)` via `auto_talente` mitaktiviert (Tradition = Paket beider Fähigkeiten).

| Gott | 1. SF | 2. SF (neu) | Quelle 2. SF |
|---|---|---|---|
| Praios | Arkane Resistenz (=Magieschutz) | **Wille des Götterfürsten (Praios)** | custom (+2 Macht gegen Widerstand) |
| Rondra | Mutig (=Fürchtet nichts) | **Heldenhafter Widerstand** | **bestehend** (Zustand aufheben) |
| Efferd | Meister des Meeres (Efferd) | **Kraft der Leidenschaft (Efferd)** | custom (+2 Glaube bei Leidenschaft) |
| Travia | Heimstatt (Travia) | **Speisesegen (Travia)** | custom (Mahlzeit → +1 nat. Heilung) |
| Boron | Untotenschreck (Boron) | **Nachtsicht** | **bestehend** (Dunkelheits-Abzüge) |
| Hesinde | Scharfe Sinne (Hesinde) | **Klarer Verstand (Hesinde)** | custom (+2 WIL vs Verwirrung) |
| Firun | Wildniskunde (Firun) | **Starker Wille** | **bestehend** (+2 Willenskraft-Widerstand) |
| Tsa | Schnelle Heilung (=Regeneration) | **Flexible Wunder (Tsa)** | custom (Macht-Modifikator −1) |
| Phex | Glück (=Glückskind) | **Feilschen mit Phex** | custom (Silber opfern → +1) |
| Peraine | Widerstand g. Krankheiten (Peraine) | **Heiler** | **bestehend** (+2 Heilungsproben) |
| Ingerimm | Feuerschutz (Ingerimm) | **Meister des Handwerks (Ingerimm)** | custom (+2 Handwerk) |
| Rahja | Durchhaltevermögen (Rahja) | **Geschenk der Freude (Rahja)** | custom (Zustand bei anderem nehmen) |

- **4 bestehende SW-Talente** (Heldenhafter Widerstand, Nachtsicht, Starker Wille, Heiler) + **8 neue Custom-SFs** (Kategorie `Geweihter`, rang A, Vor jeweiliges AH). Alle in reiner SW-Mechanik (keine DSA-Regelbegriffe; Erschüttert/Abgelenkt, natürliche Heilungsprobe, +2/−2, Silbertaler).
- **Halbgötter (Aves, Ifirn, Kor, Nandus, Swafnir, Angrosch):** Kodex gibt ihnen nur **eine** echte SF; die zweite Trad.-Position ist **„Eingeschränkte Segnungen"** (eine *Einschränkung*, kein Bonus). Daher **kein** zweites Talent ergänzt — bewusst (kein Erfinden). Mechanische Unterscheidung: volle Götter = 2 Trad.-Talente, Halbgötter = 1. **„Eingeschränkte Segnungen" als reiner Fluff** in die 6 Halbgott-AH-Beschreibungen aufgenommen (User-Entscheidung 2026-06-06: keine Mechanik).

### 14.1 AH-(Wunder)-Beschreibungen ergänzt (✅ 2026-06-06, Backup `pre_ah_beschreibung_autotalente_`)
Alle 18 `AH (Wunder: Gott)`-Beschreibungen nennen jetzt explizit die **automatisch aktivierten** Sonderfertigkeiten („Diese Tradition aktiviert automatisch die Sonderfertigkeiten X und Y."); Halbgötter zusätzlich der „Eingeschränkte Segnungen"-Fluffsatz. Parser (`extrahiere_arkane_fertigkeit_aus_ah`) unverändert korrekt (Skill `Glaube` vor erster Klammer).

**Verifikation:** 501 → **509** Talente (+8 Custom). Alle 12 Alveranischen-AHs haben 2 auto_talente (0 Waisen), 6 Halbgötter je 1. Kategorie `Geweihter`: 28. Tests grün (87).

### 14.2 Korrektur: Angrosch = Ingerimm (zusammengeführt, ✅ 2026-06-06)
> Backup `pre_angrosch_merge_20260606.json`. User-Klarstellung: **Angrosch ist nur der zwergische Name des Ingerimm**, kein eigener (Halb-)Gott.
- `AH (Wunder: Angrosch)` + Custom-SF `Feuerschutz (Angrosch)` **gelöscht** (Duplikat; Ingerimm hat bereits `Feuerschutz (Ingerimm)`). Nur wechselseitige Referenzen, keine Waisen.
- Zwergischer Name in die Ingerimm-Beschreibung integriert: „…des Ingerimm (Himmlischer Schmied; **von den Zwergen Angrosch genannt**)…".
- **Neuer Stand der Götter-AHs: 17** = 12 Alveranische + **5** Halbgötter (Aves, Ifirn, Kor, Nandus, Swafnir). Talente 509 → **507**. Tests grün (42). (Frühere „18 / 6 Halbgötter"-Angaben in §0ter/§11 sind entsprechend überholt.)

---

## 15. Kategorie-B-Reste: PF2-Höllen/Konstrukt-Talente → DSA (✅ ERLEDIGT 2026-06-06)

> Quelle: `Kodex_der_Magie.pdf` (pdftotext). Backup `pre_golembauer_daemonologe_20260606.json`. **Alle 5 behalten** (Grundsatz 5), DSA-Vorlagen statt Löschen; Eltern-AHs mit umbenannt (User: „5 Talente + Eltern-AHs"). Keine Talentzahl-Änderung (507).

**DSA-Belege:** Golems sind eigene Konstrukt-Kategorie („Golems (Homunculus, laufende Truhen)"), **Golembau** echte magische Kunst; **Schwarze Gilde** = Dämonenbeschwörung + Nekromantie; Dämonen aus den **Niederhöllen**.

| alt (PF) | neu (DSA) | Kat./AH |
|---|---|---|
| `AH (Tüftler)` (Reparieren) | **`AH (Golembauer)`** (Zaubern/VER, magischer Golembau) | AH; Skill Reparieren→**Zaubern** |
| `Konstrukt-Vertrauter` | **`Homunkulus`** | Kat. Tüftler→**Golembauer** |
| `Tüftlerrüstung` | **`Golem-Panzerung`** | Kat. Golembauer |
| `AH (Diabolist)` (Zaubern) | **`AH (Dämonologe)`** (verbotene Schwarzmagie, Heptagramm) | AH |
| `Beschwörung` | **`Dämonenbeschwörung`** | Kat. Diabolist→**Dämonologe**, auto_talente des AH |
| `Infernale Rüstung` | **`Dämonische Rüstung`** | Kat. Dämonologe |
| `Zorn der Hölle` | **`Zorn der Niederhöllen`** | Kat. Dämonologe |
| `AH (Nekromant)` | bleibt benannt, DSA-Fluff (Schwarze Gilde, Boron/Inquisition gejagt) | — |
| `Seelengefäß` | bleibt benannt; Nekromantie/Phylakterium (Pfad zur Lichwerdung) | Kat. Nekromant |

**Verifikation:** Kategorie Golembauer (2) / Dämonologe (3). Parser: alle drei AHs → `Zaubern`. Keine Alt-Reste/Waisen/Namensdrift. Tests grün (87). Damit ist Kategorie-B-Rest (Plan §7 Schritt 4) **abgeschlossen** – nächste Phase: Kategorie D (44 Prestige-Talente).

---

## 16. Kategorie D — Prestige-Talente entkoppelt (✅ ERLEDIGT 2026-06-06)

> Backup `pre_meisterschaft_renames_20260606.json`. Keine Talentzahl-Änderung (507).

**Kernbefund:** Die 44 „Prestige"-Talente waren **bereits konzept-offen** — alle Einstiegs-Talente sind über Fertigkeiten/Attribute/AH gegated (z.B. Duellant = GES W8 + Kämpfen W8), **nicht** über Klassen; die I/II/III-Ketten sind normale Steigerungsstufen. „Prestige" ist nur ein Anzeige-Label ohne Engine-Logik (nicht in `pathfinder_kostenlose_kategorien`).

- **Kategorie `Prestige` → `Meisterschaft`** (alle 44; entfernt den letzten Klassensystem-Begriff).
- **DSA-Umbenennungen (nur wo nötig, User-Wahl):** `Arkaner Betrüger`→**Phexens List**, `Kundschafter-Chronist`→**Chronist** (entfernt Pathfinder-Bezug), `Mystischer Ritter`→**Kampfmagier**, `Naturwächter`→**Hüter der Wildnis** (je I/II/III, Ketten-Prereqs mitgezogen). **Assassine bleibt** (systemneutral).
- **Zurückgestellt** (DSA-Bezug noch offen): `Mystischer Theurg` (Kandidat: **Doppelbegabter** — kanonischer DSA-Begriff für Doppel-AH), `Schattentänzer` (kein klares DSA-Pendant; Name evtl. belassen).
- **Waisen gefixt:** `Meisteralchemist` Vor `Mutagene`→`AH (Alchemist)` + `Alchemie W8`; `Unbeugsamer Verteidiger` Vor `Nerven aus Stahl`→`KON W8`.

**Verifikation:** 44 `Meisterschaft`, alle 4 umbenannten Ketten intakt (Tier-Prereqs korrekt), keine Alt-Reste/Waisen/Namensdrift. Tests grün (87). Damit ist Kategorie D (Plan §7 Schritt 5) abgeschlossen.

---

## 17. Verwaiste Klassennamen-Voraussetzungen (✅ ERLEDIGT 2026-06-06)

> Status: **umgesetzt** (User-Go 2026-06-06, gebündelt mit dem Beschwörer/Eidolon-Reflavor §18). Backup `pre_klassenprereq_eidolon_20260606.json`.
> **Ergebnis:** Alle **23** bloßen Klassennamen-Voraussetzungen auf das jeweilige `AH (Klasse)` umgeschrieben (`Barde→AH (Barde)`, `Druide→AH (Druide)`, `Kleriker→AH (Kleriker)`, `Magier→AH (Magier)`, `Hexe→AH (Hexe)`, `Paktierer→AH (Paktierer)`, `Beschwörer→AH (Beschwörer)`). `'Mindestens zwei X'` und rang-Codes (`L`) unangetastet. Funktional verifiziert (TalentManager: `AH (Barde)` mit AH erfüllt → `[]`, ohne → korrekte Fehlermeldung; vorher schlug bloßes `'Barde'` immer fehl). Talentzahl 507 unverändert. Tests grün (73).

### Ursprünglicher Befund (zur Nachvollziehbarkeit)

**Befund (Prereq-Integritätscheck über alle 507 Talente):** **23 Folge-Talente** fordern als Voraussetzung einen **bloßen Klassennamen**, der in „Savage Aventurien" gar **kein Talent (mehr) ist** — geerbt aus Savage Pathfinder, wo z.B. `Bannlied.vor = ['Barde']` auf das Klassen-Basistalent zeigte. Da der Validator (`_pruefe_einzelne_voraussetzung`) bloße Klassennamen **nicht** speziell behandelt, fällt er auf den Literal-Talent-Lookup zurück → „nicht gefunden" → die Voraussetzung schlägt **immer** fehl.

| Klassen-Prereq (existiert nicht als Talent) | betroffene Folge-Talente | Anz. |
|---|---|--:|
| `Barde` | Bannlied, Klagelied | 2 |
| `Druide` | Tiergestalt, Bevorzugte Mächte (Druide), Göttliche Meisterschaft (Druide) | 3 |
| `Kleriker` | Bevorzugte Mächte (Kleriker), Göttliche Meisterschaft (Kleriker) | 2 |
| `Magier` | Bevorzugte Mächte (Magier), Arkane Meisterschaft (Magier) | 2 |
| `Hexe` | Zusätzlicher Hex, Großer Hex, Grandioser Hex, Arkane Meisterschaft (Hexe) | 4 |
| `Paktierer` | Weitere Hexerei, Starke Hexerei, Mächtige Hexerei, Arkane Meisterschaft (Paktierer) | 4 |
| `Beschwörer` | Zusätzliche Evolution, Ruf des Schöpfers, Ruf des Beschwörers, Lebensband, Aspekt, Zwillingseidolon | 6 |
| **Summe** | | **23** |

**Vorgeschlagener Fix (noch offen):** jede bloße Klassennamen-Voraussetzung auf das entsprechende **`AH (Klasse)`** umschreiben (z.B. `'Barde'`→`'AH (Barde)'`). **Alle 7 Ziel-AHs existieren bereits** (`AH (Barde/Druide/Kleriker/Magier/Hexe/Paktierer/Beschwörer)` — verifiziert 2026-06-06). Rationale: passt zu „kein Klassensystem / für alle Konzepte freigeben" (Grundsatz 7) und repariert die kaputten Voraussetzungen, ohne neue Mechanik. Hintergrund-basierte „Klassen" (Mönch, Barbar, Schurke, Waldläufer, Kavalier, Inquisitor, Alchemist, Kämpfer, Paladin→Pool, Gjalsker) sind **nicht** betroffen — deren Basistalent trägt den geforderten Namen bzw. wurde bereits umgestellt.

**Weitere verwaiste Talent-/Fähigkeits-Referenzen (separater, kleinerer Befund, ebenfalls noch offen):** einige Folge-Talente fordern PF-Mächte/-Ancestry-Namen, die hier kein Talent sind: `Monster beschwören`/`Tier beschwören` (→ Ungezügelte/Höhere Beschwörung, Arkane Stärkung), `Odemwaffe`/`Versengen`-Ketten, `Lykanthropie` (→ Schnelle Verwandlung), sowie ggf. entfernte PF-Ancestries (`Ifrits`, `Sylphen`, `eine böse Gesinnung`). Beim Klassen-Prereq-Fix gleich mit-sichten und im selben Durchgang sauber zuordnen oder Status-3-prüfen.

**Engine-Lücke „Mindestens zwei X-Talente" (§13.4): ✅ GESCHLOSSEN 2026-06-06.** Neuer Handler in `functions/talent_funktionen.py::_pruefe_einzelne_voraussetzung` (vor dem Talent-Fallthrough): Regex `^Mindestens (\w+) (.+?)-(?:Talente|Vorteile)$` → Zahlwort→Zahl + Kategorie über **längsten Präfix** (Plural-/Genitiv-tolerant: „Hexen"→„Hexe", „Druiden"→„Druide", „Schurken"→„Schurke") → zählt **ausgewählte** Talente dieser Kategorie ≥ benötigt. Damit funktionieren die **17 Kategorie-Capstones** (Mächtige Hexerei, Überlegener Ansturm, Wahres Urteil, Grandioser Hex, Tödliche Darbietung, Heiliger Champion, Heimvorteil, Meisterangriff, Perfekter Körper, Schon gesehen, Unaufhaltsame Wut, Veteran des ewigen Krieges, Gut vorbereitet, Wahrer Schwertmagier, Unsichtbare Klinge, Verbesserte Defensive Instinkte, Zwillingswesenheit), die vorher **immer fehlschlugen** (Capstones unwählbar). Alle 17 Token mappen auf existierende Kategorien. **6 Unit-Tests** (`test_talent_manager.py::TestMindestensKategorieVoraussetzung`). Geteilte Engine → kommt auch Savage Pathfinder zugute. Volle Suite 951/952 grün (1 vorbestehender KivyMD-UI-Fehler, unrelated).

**Noch offen (separate Cleanup-Phase): PF-Altlasten-Prereqs** — ~Dutzend Folge-Talente fordern Fremdsetting-Referenzen, die hier kein Talent/Skill sind: `Odemwaffe`, `Tier/Monster beschwören`, `Lykanthropie`, `Ifrits`, `Sylphen`, `eine böse Gesinnung`, `Flügel`, `MM`, `AH (Psionik)`, `AH (Verrückte Wissenschaft)`, `AH (Elementarmagier)` (→ Elementarist), `AH (Diabolist)`/`AH (Zauberer)` (Vertrauter, veraltet nach §15), plus Tippfehler `Ver W8` (Wissenshüter → `VER W8`) und `Fortgeschritten` (Mystische Kräfte → Rang `F`).

---

## 18. Querschnitt — DSA-Essenz/Fluff in Beschreibungen (LÄUFT, §7 Schritt 6)

> Ziel (Grundsatz 6 + §8.3 Prio 1): jedem behaltenen SP/FK-Talent ein DSA-Trapping/Flair in der **Beschreibung** geben (Profession/Kultur/Tradition/ikonischer Begriff), **ohne** SW-Mechanik zu ändern und **ohne** DSA-Regelbegriffe (kein LeP/AsP/QS/FP). Methode: führender DSA-Kontextsatz vor die bestehende (rein mechanische) Beschreibung; Mechanik-Liste unverändert. Roadmap = §8.1-Tabelle. Blockweise mit Verifikation.

### Block 1 — Weltliche Hintergrund-Professionen ✅ ERLEDIGT 2026-06-06
> Backup `pre_querschnitt_professionen_20260606.json`. Die in §12 auf `Hintergrund` umgehängten Klassentalente hatten nur mechanische Ability-Listen ohne DSA-Rahmen. Je ein führender DSA-Kontextsatz vorangestellt (keine Mechanik berührt):
- `Barbar` → **Trollzacker / Fjarninger / Thorwaler-Berserker** (User-Korrektur: nicht „Norbarde"), kämpferische Raserei statt Fechtschule.
- `Kämpfer` → Berufskrieger/Söldner/Gardist eines aventurischen Heeres.
- `Mönch` → **Hruruzat** (kanonische aventurische Kunst des waffenlosen Kampfes, Kodex der Helden:7582; DSA kennt KEINE klassischen Kampfmönche – User-Hinweis bestätigt, ehrlich so formuliert), als körperlich-geistige Disziplin.
- `Schurke` → Dieb/Strolch/Beutelschneider, Phex-nah.
- `Waldläufer` → Wildnisläufer/Förster/Kopfgeldjäger.
- `Kavalier` → Reiterkrieger eines aventurischen Ritterordens (Turnier/Lanze/Ehre).
- `Alchemist` → Zauberalchimist hesindegefälliger Laboratorien.

**Verifikation:** 507 Talente unverändert (nur Beschreibungstext), JSON lädt, keine DSA-Regelbegriffe eingefügt. Tests grün (`test_setting_funktionen` + `test_talent_manager` = 72).

### Block 2 — Stab-/Gildenmagie: KEIN Eingriff nötig ✅ (geprüft 2026-06-06)
Bindung/Fokus des Stabes, Zauberspeicher, Zauberstab-Meisterschaft, Kraftfokus, Kraftlinienmagie, Kugelzauber, Flammenschwert, Eisenaffine Aura, Magischer Alltag sind **bereits durchgehend DSA-nativ** (Magierstab, Kraftlinien, Bann des Eisens, Kristallkugel-Untotenwarnung, Sapefacta/Accuratum) — die Custom-Aventurien-Positiv-Liste (§4 Kat. E „nicht anfassen"). Übersprungen.

### Block 3 — Druide/Schamane/Tier: größtenteils nativ ✅ (geprüft 2026-06-06)
Die `Druide`-/`Schamane`-kategorisierten Talente (Tiergestalt, Naturgespür, Wahre Form, Dolch des Druiden, Knochenkeule, Bindung mit der Natur) tragen bereits DSA-Flair (Geister-Zwiesprache, Vulkanglasdolch, Kraftlinien). Der Rest (Tiermeister, Tierempathie, Bestienflüsterer, Vertrauter-Familie, Naturverbundenheit, Schnelle Verwandlung) sind **universelle, systemneutrale SW-Edges** → bewusst **clean** gelassen (Grundsatz 8: forciertes DSA-Flair = Rauschen, schadet SW-Kompatibilität). Kein Eingriff.

### Block 4 — Beschwörer/Eidolon-Familie ✅ ERLEDIGT 2026-06-06 (Backup `pre_klassenprereq_eidolon_`)
Vollständiger Befund: **„Eidolon" (PF-Summoner-Begleitwesen) war die einzige verbliebene Nicht-DSA-Terminologie** im gesamten Talent-Bestand (7 Beschreibungen: Aspekt, Lebensband, Ruf des Schöpfers/Beschwörers, Zusätzliche Evolution, Zwillings…, Entwickelter Vertrauter). User-Entscheidung: Eidolon → **„(gebundene) Wesenheit"** (an DSA-Vertrautentier angelehnt), „Evolutionspunkte"→„Entwicklungspunkte". Talent **`Zwillingseidolon` → `Zwillingswesenheit`** umbenannt (literaler PF-Begriff im Namen; referenzfrei). `AH (Beschwörer)` bekam DSA-Rahmen (Gildenmagier-Beschwörung, ruft/bindet Geister & Elementardiener; parser-sicher: Skill-Zeile zuerst → liefert weiter `Zaubern`). Mechanik unverändert. Talentzahl 507.

### Fazit Querschnitt
Die DSA-Essenz-Harmonisierung ist damit **inhaltlich abgeschlossen**: 0 PF/D&D-Begriffe in Beschreibungen, 0 verwaiste Klassen-Prereqs, Professionen geflairt, alles übrige bereits DSA-nativ oder bewusst systemneutral. Optionaler Rest = reine Geschmacks-Politur einzelner generischer Edges (nicht erforderlich).
