# SciFi-Kompendium — Handicap-Verifikation gegen die offiziellen Bögen

**Stand:** 2026-06-16 (2. Durchlauf) · Quelle: `Texte/Science_Fiction_Companion_Archetypes_(SWADE).pdf`
(Render+Crop der Attribut-/Fertigkeits-/Hindrance-Blöcke; Hindrance-Text zusätzlich via `pdftotext -layout`).

## Kern-Erkenntnis (korrigiert die 1.-Durchlauf-Annahme!)

Die im 1. Durchlauf als **„MISSING im DE-Setting"** abgetanen Handicaps existieren **alle** — nur
unter anderem deutschen Namen. Dadurch erreichen **alle 5 Problem-Chars die vollen 4 HP** mit
existierenden Keys:

| Bogen (EN) | DE-Key (verifiziert per Beschreibung) | Punkte |
|---|---|---|
| Clueless (–1 Common Knowledge & Notice) | **Verpeilt** | 2 |
| Overconfident | **Übermütig** | 2 |
| Ex-Drone (–2 Spirit wenn kein Verbündeter in 5'') | **Ehemalige Drohne** | 2 |
| Ailment Minor (–1 vs. Erschöpfung, Krit→schwer) | **Totkrank (leicht)** | 1 |
| Anemic / Curious / Small | **Blutarm / Neugierig / Klein** | 1 / 2 / 1 |

Außerdem existieren die im 1. Durchlauf als MISSING geführten Edges **Cyborg** und **Gut Ausgerüstet**
(Geared Up). **Regel bestätigt:** „rassische Auto-Handicaps geben 0 HP und verbrauchen das 4-HP-Budget
NICHT" — die ANCESTRY-Blöcke der Bögen (Aquatic, Insektoide, Low-G/Flight) sind rassisch.

## BEHOBEN (2026-06-16, 2. Durchlauf) — alle 5 auf 4 HP, render-verifiziert

Build neu gelaufen (`build_sfc_phase_g.py` → `fill_budget_gaps.py`). Attribute jetzt **bogentreu**
(Render+Crop), HP voll genutzt, keine vermeidbaren Doppelkosten mehr.

| Char | Volk | Spieler-HC (4 HP) | Korrektur ggü. altem Build |
|---|---|---|---|
| **Road Warrior** | Mensch | Heldenhaft(2)+Totkrank leicht(1)+Low Tech(1) | Ailment ergänzt (war 3 HP); Vig d8→**d6** (Über-Advance entfernt) |
| **Technomancer** | Aquatische Spezies | Verpeilt(2)+Eifersüchtig(1)+Sanftmütig(1) | Verpeilt ergänzt (war 2 HP); Repair-Advance d10→**d8** |
| **Commando** | Insektoide | Aufopferungsvoll schwer(2)+Ehemalige Drohne(2) | Ehemalige Drohne ergänzt (war 2 HP); Verstand d6→**d4**; Skill-Overshoots (Wahrn/Pilot/Überl/Rep) korrigiert |
| **Cyborg** | Mensch* | Verpeilt(2)+Übermütig(2) | War Arrogant+Skrupellos (falsch, 2 HP) → Verpeilt+Übermütig; Volk Gen-Soldaten→Mensch; Agi d10→**d8**; Skills komplett neu (Pilot/Repair waren Fremd-Bogen) |
| **Hardlight Conjurer** | Mensch | Neugierig(2)+Blutarm(1)+Klein(1) | War Insektoide+Außenseiter (falsch, 1 HP) → Mensch+Blutarm/Neugierig/Klein; Agi d8→**d6**, Spi d6→**d8**, Vig d8→**d6** |

Alle: **HP 4/4, Rest 0**. Rang Fortgeschritten (Technomancer fällt auf **Anfänger** — bewusste „beste
Ökonomie", HP statt Aufstiege, User-Regel „Rang fällt ok").

\* **Cyborg-Volk:** Der Bogen zeigt eine Ancestry **Flight (Pace 12) + Low-G Worlder (–1 Str) +
Reduced Pace** — dafür gibt es **kein** passendes DE-Volk (keines hat „Fliegen"). Als **Mensch**
gebaut (sauberer als das alte Gen-Soldaten mit fälschlichem rassischem Skrupellos+Kampfreflexe);
Flug/Low-G sind nicht modellierbar → dokumentiert.

## Doppelkosten

- **Vermeidbar & behoben:** Hardlight `Naturwissenschaften d10` war doppelt, weil der alte Build
  Verstand erst per **Aufstieg** (nach den Skills) auf d10 zog. Jetzt Verstand d10 in der Chargen
  **vor** dem Skill → einfache Kosten.
- **Inhärent (nicht behebbar):** Commando `Schießen d8`(>Agi d6) & `Wahrnehmung d6`(>Sma d4),
  RoadWarrior `Überleben d8`(>Sma d6) — Skill übersteigt das regierende Attribut by Bogen-Design;
  billiger nur durch Attribut-Abweichung vom Bogen.

## Offene Daten-/Modellierungs-Notiz (vorbestehend, NICHT HP-bezogen)

- **Cyborg `Wahrnehmung` zeigt d8 statt Bogen-d6.** Ursache: das Implantat **`Cyberware: Verbesserte
  Sicht`** trägt `effekte.wahrnehmung_bonus: 2` → hebt den Wahrnehmungs-**Würfel** dauerhaft um +2
  (Basis d4 → d8). Der gedruckte Bogen-Notice d6 ist der Basiswert; das Implantat-„+2 auf Notice" ist
  **situativ** (Beleuchtung) und sollte den Würfel nicht permanent erhöhen. Das ist eine
  Setting-Daten-Modellierung (app-weit, betrifft jeden Char mit dem Implantat) und war schon im
  committeten Cyborg so — **nicht** im Rahmen der HP-Aufgabe geändert. Kandidat für späteren Daten-Fix:
  `wahrnehmung_bonus` als situativen Roll-Bonus statt Würfel-Boost behandeln.
- **Hardlight `Mächte 3/7`:** Bogen hat 7 Powers (16 PP), AH-Budget 15 PP → 4 Powers passen nicht ins
  Macht-Budget (wie bisher dokumentiert, kein HP-Thema).

## Verifikations-Methode

Render: `pdftoppm -r 150` der Seiten 10/14/18 → `convert -crop` je Archetyp-Quadrant → Read-Tool.
`fill_budget_gaps.parse_sheet` auf dem TXT-Export reproduziert dieselben Würfelwerte (hier zuverlässig,
da die Archetypen vertikal gestapelt sind) und wird nur zum **Anheben** (nie Senken) genutzt.
