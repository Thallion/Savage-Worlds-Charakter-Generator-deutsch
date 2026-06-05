# Horror Kompendium — Komplett-Review gegen Kauf-PDF (US85083)

Quelle: `logs/pdf_extracted/US85083_Horror-Kompendium_KaufPDF_250210_LZ_meta.pdf` (202 S.)
vs. `settings/Horror Kompendium.json`. Stand 2026-06-05.

**Bestand:** Talente 174 · Handicaps 100 · Mächte 68 · Ausrüstung 68 · Fertigkeiten 33.

## 1. Handicaps (PDF „Neue Handicaps", S.6) — VOLLSTÄNDIG ✓
Alle 16 neuen Handicaps vorhanden (teils andere Keys):
Amourös→`Verliebt`, Grauen→`Düsternis`, Tiefer Schlaf→`Tiefschläfer`, Rüpel→`Tyrann`,
Aberglaube→`Abergläubisch`, Nachtängste→`Nachtschrecken`. Bluter, Kugelmagnet,
Materialkomponenten, Opfer, Schreckhaft, Schreihals, Unnatürlicher Appetit, Verdammt,
Verderbnis, Verflucht direkt vorhanden.

## 2. Fertigkeit (PDF „Neue Fertigkeit", S.7) — 1 FEHLT
- **`Alchemie` (Verstand) FEHLT** in `fertigkeiten_daten`, obwohl `AH (Alchemist, Horror)`
  existiert → der Arkane Hintergrund hat keine arkane Fertigkeit. Soll: `"Alchemie": ["Verstand"]`.

## 3. Talente
### 3a. Allgemeine neue Talente (S.8-11)
- Vorhanden: Galgenhumor, Veteran der Dunklen Welt, Bevorzugte Macht, Monsterjäger,
  Mystische Kräfte; Unerbittlich=`Unerschütterlich`, Stillzauberer=`Stiller Wirker`,
  Seher=`Visionen`, Scream Queen/King=`Schreikönigin/Schreikönig`.
- **FEHLT: `Final Girl/Guy`** (Soziales Edge), **`Betagt`** (Monster, +2 Verstand/Allgemeinwissen),
  **`Furchterregend (-2)`** (Monster).
- **PRÜFEN: `Courage`** (Anführer-Edge: Verbündete im Befehlsradius würfeln misslungene Furchtprobe
  neu). `Ermutigen` ist NICHT dasselbe (hebt Abgelenkt/Verwundbar auf). Wahrscheinlich fehlt Courage.

### 3b. Arkane Hintergründe (S.57-71) — VOLLSTÄNDIG ✓ (10/10)
Alchemist, Dämonologe, Hexenmeister/Hexe, Medium, Okkultist, Priester, Psionischer/Übersinnlicher
Ermittler, Verdorbener, Voodooist, Wahrsager.

### 3c. Race-spezifische Monster-Talente (S.12-23) — GROSSE LÜCKE
Nur `Höllenfeuer` vorhanden. ~50 fehlen. Brechen KEINE Archetypen (nutzen nur allg. Edges+AH),
ABER der offizielle Demon-Bogen hat das Edge **Klauen** (fehlt). Fehlend je Volk:
- Dämon: Dämonische Flügel, Dämonische Unsterblichkeit, Dämonischer Biss, Versengendes Höllenfeuer,
  Klauen, Körperlos, Übernatürliches Spüren, Panzerhaut, Wahrer Dämon
- Engel: Engelsgleiche/Gottgleiche Zähigkeit, Flügelschlag, Schneller Flug, Göttliche Klinge,
  Heiliges Licht, Versengender Flächenschlag, Sprachen sprechen, Unsterblichkeit der Engel
- Flickwerk: Abnehmbare Teile, Entladen, Flashbacks, Gebrüll
- Mumie: Mumienfäule, Schwarmrufer, Mächtiger Schwarmrufer, Graben, Langsame/Schnelle
  Mumien-Regeneration, Sturmrufer
- Phantom: Phantom-Unsichtbarkeit, Schaurige Berührung, Übergang
- Vampir: Bezaubern, Erschaffer, Kinder der Nacht, Knecht, Nebelform, Tagschreiter, Tiergestalt,
  Überfressen, Wandkrabbler
- Werwolf: Alpha, Sprechen, Zähigkeit
- Wiedergänger: Gedankenfresser, Gestank, Herr der Zombies, Todesberührung, Unerbittlicher Verfolger

## 4. Mächte (PDF „Neue Mächte", S.73-84) — ~14 von 17 FEHLEN
- Vorhanden: Verbündeten beschwören, Zombie, Fluch=`Fluchwort`.
- **FEHLT**: Aspekt der Rada Loa, Albträume, Aufspüren, Ausspähung (Scrying; `Fernsicht`=Farsight ist
  was anderes), Boden weihen, Dämon beschwören, Exorzismus, Illusionäre Schrecken, Kadaversinn,
  Seance, Verriegeln/Entriegeln, Verwandlung unterdrücken, Zorn der Petro Loa, Zuflucht.
- Folge: Voodoo-/Exorzismus-Builds (AH Voodooist/Priester/Medium) können ihre Kern-Mächte nicht wählen.

## 5. Ausrüstung (Kap.2 S.25 + Kap.5 S.85-99) — WEITGEHEND VOLLSTÄNDIG ✓
Kern-Items vorhanden (EMF-Detektor, Geisterfalle, Geisterjägerpaket, Heiliges Symbol, Holzpfähle,
Kaltes-Eisen-Kugeln/Schwert, Silber-/Knoblauch-/UV-Kugeln, Vampirjäger-Armbrust, Weihwasser, Salz).
Kleinere Varianten-Lücken: Weihwasser als Granate/Pistole/Spray, Knoblauchgeschosse, „Pflock, geworfen".

## 6. Völker (falsche Keys) — in dieser Sitzung bereits korrigiert
Handicaps + Attribut-Boni PDF-konform (siehe `archetypen_anomalie_bericht.md`).
**OFFEN — Dämon `spezielle_effekte` falsch**: `panzerung_2`, `natuerliche_waffen`, `furchteinflössend`
sind KEINE Volkseigenarten. Quellen (dt. PDF + Horror_Companion_Archetypes): Klauen = **Edge**,
Panzerhaut/Dämonischer Biss = **Talente**, Furcht kommt beim Dämon nicht vor. Echte Volkseigenarten:
Dunkelsicht (`infrarotsicht` ✓), Widerstand Naturgewalten (`resistenz_feuer`, aber zu eng — PDF:
Kälte/Elektr./Hitze), Alterslos, Entziehen, Pakt, Immunität, +Konst/+Wil.

---

## STATUS: INTEGRIERT (2026-06-05)

Alle fehlenden Inhalte mit Original-PDF-Bezeichnungen ergänzt in `settings/Horror Kompendium.json`.
Bestand danach: Talente **230** (+56), Mächte **82** (+14), Fertigkeiten **34** (+1).

- **Fertigkeit:** `Alchemie` (Verstand) ergänzt.
- **14 neue Mächte:** Aspekt der Rada Loa, Albträume, Aufspüren, Ausspähung, Boden weihen,
  Dämon beschwören, Exorzismus, Illusionäre Schrecken, Kadaversinn, Seance, Verriegeln/Entriegeln,
  Verwandlung unterdrücken, Zorn der Petro Loa, Zuflucht. (Dämon beschwören & Exorzismus haben
  laut PDF MP „Speziell" → als `machtpunkte:0` + Hinweis in der Beschreibung, da der Loader nur
  int-MP lädt.)
- **4 allgemeine Edges:** Courage, Final Girl/Guy, Betagt, Furchterregend.
- **~52 Race-Monster-Talente** (kategorie „Monströs", Voraussetzung = Volk; geteilte Talente
  Klauen/Gebrüll/Wandkrabbler/Übernatürliches Spüren/Abnehmbare Teile/Regeneration (schnell)
  als Einzeleintrag mit `{oder:[…]}`). Namenskollision gelöst: Dämon-Feuerkegel = `Höllenfeuer (Dämon)`
  (bestehendes `Höllenfeuer` ist ein anderes Macht-Edge).
- **Demon-Archetyp:** Edge `Klauen` ergänzt (steht so auf dem offiziellen Bogen).
- **Dämon-Volk bereinigt:** `natuerliche_waffen`/`panzerung_2`/`furchteinflössend` aus
  `spezielle_effekte` + besonderheiten entfernt (sind Talente/Edges, keine Volkseigenart; Klauen/
  Panzerhaut jetzt als wählbare Talente vorhanden). `infrarotsicht`/`resistenz_feuer` bleiben.

**Nicht dupliziert (inhaltlich identische Bestands-Keys, ggf. aus SWAE/Fantasy):**
Unerbittlich=`Unerschütterlich`, Seher=`Visionen`, Stillzauberer=`Stiller Wirker`,
Scream Queen/King=`Schreikönigin/Schreikönig` (Furchteffekt-Tabelle neu würfeln — Spalten-OCR
hatte es mit Courage vertauscht; verifiziert), Zäh (Flickwerk-Talent = bestehendes `Zäh`).

**Verifiziert headless:** Setting lädt (230/82/34); neue Keys auflösbar; neue Race-Talente verhalten
sich beim Wählen exakt wie bestehende (Anfänger ohne freien Slot → False; Fortg. → needs_rang_confirmation).
`test_groesse.py` 16/16 grün.

---

## NACHTRAG: Keys auf PDF-Bezeichnungen umbenannt (2026-06-05)

Auf Wunsch (Rippers = Horror-Kompendium-Ableger → identische Namen) konsequent umbenannt statt
Synonyme zu belassen. In **Horror Kompendium.json + Rippers.json** sowie in den 5 betroffenen
Horror-Archetypen:

| alt (Bestand) | neu (PDF-Bezeichnung) | Archetyp |
|---|---|---|
| Unerschütterlich | **Unerbittlich** | Doctor |
| Visionen | **Seher** | Psychic |
| Stiller Wirker | **Stillzauberer** | Occultist |
| Schreikönigin/Schreikönig | **Scream Queen/King** (+ `_2`) | Slayer, Survivor |

- `Visionen` ist in Pathfinder/Aventurien KEIN Talent-Key (nur Substring in Fließtext) → unberührt.
- `Stillzauberer` existierte bereits in 6 anderen Settings → Umbenennung erhöht die Konsistenz.
- Methode: quoted-exact Textersetzung (`"alt"`→`"neu"`), trifft Key + `name` + Voraussetzungen +
  Steigerungs-Journal, NICHT Beschreibungstexte. Kein Kern-Code (`functions/`,`models/`) referenziert
  die Namen.
- Verifiziert: Horror (230 Talente) + Rippers (200) laden, neue Keys auflösbar, alte weg;
  Archetyp-Referenzen aktualisiert; `test_groesse.py` 16/16.
