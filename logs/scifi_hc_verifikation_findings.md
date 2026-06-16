# SciFi-Kompendium — Handicap-Verifikation gegen die offiziellen Bögen

**Stand:** 2026-06-16 · Quelle: `Texte/Science_Fiction_Companion_Archetypes_(SWADE).txt`
(+ Render der englischen Archetypen-Bögen). Geprüft: alle SciFi-Chars mit `HP < 4` bzw. `0/0`.

**Befund (Wurzel):** `build_sfc_phase_g.py` lässt bei mehreren Chars die **Spieler-Handicaps des
Bogens weg** — teils weil rassische Auto-Handicaps fälschlich aufs 4-HP-Budget angerechnet wurden
(Roboter/AB), teils schlicht falsch transkribiert ("keine Handicaps"). Rassische Handicaps geben
0 HP UND zählen nicht gegen das Spieler-Budget → diese Chars hätten je 4 HP eigene Handicaps.

## A) BEHOBEN (2026-06-16) — Spieler-Handicaps in `build_sfc_phase_g.py` ergänzt

Build neu gelaufen (`build_sfc_phase_g.py` → `fill_budget_gaps.py`). Attribute/Fertigkeiten/Mächte
**byte-identisch** zum vorherigen Stand — nur Finanzierung (HP statt Aufstieg) + korrekte Handicaps.
Rang bleibt überall Fortgeschritten.

| Char | Volk | Fix (DE-Keys) | HP | Aufstiege |
|---|---|---|---|---|
| **Enforcer** | Roboter | `Misstrauisch_schwer`(2)+`Große Klappe`(1)+`Kann nicht schwimmen`(1) | 0→**4/4** | 8→**6** |
| **Bounty Hunter** | Mensch | `Gierig_schwer`(2)+`Skrupellos_schwer`(2) | 0→**4/4** | 7→**5** |
| **Star Knight** | Mensch | `Heldenhaft`(2)+`Schwur_schwer`(2) (Ehrenkodex via AB, 0 HP) | 0→**4/4** | 8→**6** |
| **Road Warrior** | Mensch | `Heldenhaft`(2)+`Low Tech (leicht)`(1) — Ailment fehlt im DE-Setting | 0→**3/3** | 7→**6** (+`Raketen-Ass`) |

Roboter-Auto-HC (Pazifist_schwer+Programmiert) sind **rassisch** (0 HP, kein Budget-Verbrauch) →
koexistieren mit den 4 Spieler-HP. Beide Major-HC bei Star Knight wurden akzeptiert (Limit ok).

## B) Durch fehlende DE-Keys begrenzt (legitim unter 4 HP)

| Char | Volk | Bogen | Max erreichbar | Anmerkung |
|---|---|---|---|---|
| **Technomancer** | Aquatisch | Clueless(Major)+Jealous+Mild Mannered | 2 | `Clueless` fehlt im DE-Setting → nur 2 HP; aktuell 2/2 ~ok (Abhängigkeit sollte rassisch sein) |
| **Cyborg** | Bogen: Mensch+Cyborg-Edge | Clueless+Overconfident | ~2 | `Clueless` fehlt; **Identität falsch** (gebaut: Arrogant+Skrupellos statt Übermütig) |

## C) Legitim / korrekt

| Char | Begründung |
|---|---|
| **Envoy** | Bogen hat nur 3 Spieler-HC (Suspicious+Tongue-Tied+Zero-G) → 3/3 korrekt |
| **Commando** | Ex-Drone fehlt im DE-Setting → Selfless(Major)=2 ist Maximum |
| **Scrapper** | Curious+Stubborn+Quirk; gebaut 3 HP (Wuchtig statt Tick — Identitäts-Quirk, HP korrekt) |
| **Morpher** | 4/4, Spieler-HC vollständig |

## D) Offen, NUR dokumentiert (User-Entscheidung 2026-06-16: „so lassen")

Beide Chars sind **deutsche-Kompendium-only**; ihre Bögen liegen hier nur als **spaltenverschmolzener
englischer Text-Export** + **un-OCR'tes Scan-PDF** (304 S.) vor → kein sauberer Render+Crop möglich,
daher **kein** Umbau (Restunsicherheit zu hoch). Korrigierte Lesart vs. Build:

- **Cyborg**: Bogen zeigt Ahnen-Merkmale (Low G Worlder −1 Str, Reduced Pace) → eher
  **Niedergravitationsweltler**-Spezies mit *Cyborg-Edge* (gebaut: Gen-Soldaten + Arrogant/Skrupellos).
  `Clueless` fehlt im DE-Setting → Aufwärtspotenzial ohnehin gering. Aktuell HP 0/2.
- **Hardlight Conjurer**: Bogen liest sich als **Mensch** mit Anemic + Curious + **Small (Handicap,
  keine Spezies)** = 4 HP (gebaut: Insektoide + Außenseiter/Trennungsangst = 1 HP). Fixbar, aber
  Rasse + abgeleitete Werte (Insektoide-Panzerung/Klauen) müssten neu aufgebaut werden. Aktuell HP 0/1.

- **Fehlende DE-Keys** (als MISSING dokumentiert, nicht ersetzt): `Clueless`, `Ailment`, `Ex-Drone`.
