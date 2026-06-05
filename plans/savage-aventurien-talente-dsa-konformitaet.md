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
| Talente gesamt | 504 | 469 | **−35** |
| Kategorie „Revolverheld" | 5 | 0 | −5 |
| Kategorie „Klasse" | 22 | 21 | −1 (Wandler → Gjalsker Tierkrieger) |
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

---

## 7. Nächste Schritte

**Sofort-Korrekturen aus dem Review — ✅ ERLEDIGT 2026-06-05 (Backup: `pre_namensbugfix_20260605.json`):**

0a. ✅ **Wandler-Waise geschlossen:** `Verbesserte Defensive Instinkte` → `kategorie: "Gjalsker Tierkrieger"`, Voraussetzung → „Mindestens zwei Gjalsker Tierkrieger-Talente". (Gjalsker-Kategorie jetzt 4 Talente.)
0b. ✅ **`AH (Magie)`→`AH (Magier)` vereinheitlicht** (5 Talente: `Zauberbücher`, `Zauberer`, `Kraftlinienmagie`, `Kugelzauber`, `Magischer Alltag`). **Entscheidung (Grundsatz 8):** KEIN Talent umbenannt — die 5 falschen Prereqs auf den existierenden Namen `AH (Magier)` korrigiert (9 Geschwister-Talente nutzten ihn bereits; beide Quell-Settings nennen ihn so). Verwaiste Voraussetzungen jetzt **0**.
0c. **Plan-Selbstkonsistenz:** §3.6 „Verbleibend in Kategorie Zauberer (4)" verifiziert = `Bevorzugte Mächte (Zauberer)`, `Arkane Meisterschaft (Zauberer)`, `Große Macht`, `Phänomenale Macht`; das Basis-`Zauberer`-Talent (kategorie `Macht`) existiert weiterhin → bei Klasse→Hintergrund-Umbau (Grundsatz 7) mitbehandeln.

**Hauptaufgabe (DSA-Kodex-Essenz × FK/SWPF harmonisieren) — empfohlene Reihenfolge, je mit User-Bestätigung pro Schritt:**

1. **Kategorie C – Klassen → Hintergrund (14 `Klasse`-Talente)**: Kategorie auf `Hintergrund` umstellen + DSA-Namen (WA-konform); Folge-Talent-Kategorien + Voraussetzungen mitziehen.
2. **Kategorie B – Inquisitor-Talente (6×)** → `Boron X` (Geweihten-Tradition, WA: `AH (Wunder: Boron)`).
3. **Kategorie B – Paladin-Talente (6×)** → `Rondra X` / `Praios X` (WA: `AH (Wunder: Gott)`).
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

## 11. Schritt 2 — `AH (Wunder: Gott)` je Gottheit (🔄 läuft, 1/18)

> Umfang: **12 Alveranische + 6 Halbgötter = 18** (Außeralveranische bewusst weggelassen). Backup je Gott.

### 11.1 Template (User-bestätigt 2026-06-05)
- **AH (Wunder: Gott)**: `kategorie: Hintergrund`, `rang: A`, Arkane Fertigkeit **Glaube (Willenskraft)**, **10 MP**, **3 neue Mächte**, Voraussetzung **WIL W6**, `auto_handicaps: [Schwur_schwer]` (= verbindlicher Moralkodex/Tabu der Kirche). Beschreibung mit Aspekten + heiligem Symbol.
- **Je 1 konvertierte Traditions-Sonderfertigkeit** als eigenes Talent: `kategorie: Geweihter` (neue Sammelkategorie, NICHT 18 Einzelkategorien), `rang: A`, Voraussetzung = jeweiliges `AH (Wunder: Gott)`.

### 11.2 Fortschritt

| # | Gott | AH | Traditions-SF (Talent) | Status |
|--:|---|---|---|:--:|
| 1 | **Praios** (Götterfürst; Sonne/Ordnung/Recht/Magiebann) | `AH (Wunder: Praios)` | **Magieschutz (Praios)** — +2 widerstehen ggü. arkanen Mächten (DSA: +1 Seelenkraft) | ✅ 2026-06-05 (Backup `pre_ah_wunder_praios_`) |
| 2–12 | Rondra, Efferd, Travia, Boron, Hesinde, Firun, Tsa, Phex, Peraine, Ingerimm, Rahja | – | – | ⬜ offen |
| 13–18 | Aves, Ifirn, Kor, Nandus, Swafnir, Angrosch (Halbgötter) | – | – | ⬜ offen |

**Stand nach Praios:** 476 Talente. Tests grün.
