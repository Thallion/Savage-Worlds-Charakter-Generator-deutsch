# Worlds of Ulisses Archetypen — Vorder-/Rückseiten-Zuordnung

Quelle: `Texte/Worlds_of_Ulisses_Archetypen.pdf` (10 Seiten A4 = **5 Bögen à 4 Archetypen**).
- **Ungerade Seiten (1,3,5,7,9)** = je 4 **Vorderseiten** (Name + Attribute/Fertigkeiten). Per
  `pdftotext` lesbar (`Worlds_of_Ulisses_Archetypen.txt`).
- **Gerade Seiten (2,4,6,8,10)** = je 4 **Rückseiten** (Handicaps/Talente/Mächte/Ausrüstung),
  für Duplexdruck **horizontal gespiegelt** angeordnet. `pdftotext` liefert dort NICHTS
  (Text als Pfade/gespiegelt) → nur per **Render+Crop** lesbar
  (`pdftoppm -r 200 -f <gerade Seite> ...`, dann Quadranten croppen).

## ZUORDNUNGS-REGEL (wichtig!)
Die Rückseite ist gegenüber der Vorderseite **links↔rechts gespiegelt** (Zeile bleibt gleich):

| Vorderseite-Position | → Rückseite-Position |
|---|---|
| oben-links (TL)  | oben-rechts (TR) |
| oben-rechts (TR) | oben-links (TL) |
| unten-links (BL) | unten-rechts (BR) |
| unten-rechts (BR)| unten-links (BL) |

D.h. NICHT positionsgleich übernehmen — sonst bekommt jeder Charakter die falsche Rückseite.

## Bogen 1 (Seiten 1+2, SWAE) — verifiziert per Render+Crop 2026-06-14
| Vorderseite | Pos | Rückseite-Pos | Inhalt Rückseite | Gespeicherter Archetyp |
|---|---|---|---|---|
| ARTHAN, der Priester | TL | TR | AH Wunder, Heiler; Ehrenkodex/Pazifist/Sanftmütig; Heilung/Linderung; Kettenhemd/Kriegshammer | `Archetyp_SWAE_Arthan_A` (+ `Myst_Priester_Arthan`) |
| ELSIARA, die Brigantin | TR | TL | Assassine, Dieb; Gesucht/Gierig/Nichtschwimmer; Lederrüstung/Dolch | `Archetyp_SWAE_Brigantin_Elsiara_A` |
| KENAKEN, die Kampfkünstlerin | BL | BR | Kampfkünstler; Arrogant/Stur/Kränklich; Fäuste | `Archetyp_SWAE_Kenaken_A` |
| NACHTFINDER, die Magierin | BR | BL | AH Magie, Machtpunkte; Alt/Neugierig; Abwehren/Geschoss; Stab/Bücher | `Archetyp_SWAE_Nachtfinder_A` |

**Ergebnis Bogen 1: alle 4 Rückseiten korrekt zugeordnet gespeichert** (Spiegelung berücksichtigt).

## Alle 5 Bögen — räumliche Vorderseiten-Positionen + Verifikation (Render+Crop 2026-06-14)
Spalten = Vorderseiten-Position (S. ungerade); die korrekte Rückseite steht auf der nächsten
(geraden) Seite an der **gespiegelten** Position. ✓ = gespeicherter Archetyp trägt die richtige Rückseite.

| Bogen | TL | TR | BL | BR |
|---|---|---|---|---|
| 1 (S.1+2, SWAE)        | Arthan (Priester) ✓ | Elsiara (Brigantin) ✓ | Kenaken (Kampfk.) ✓ | Nachtfinder (Magierin) ✓ |
| 2 (S.3+4, HeXXen)      | Raphael (Ordenskr.) ✓ | Jeanne (Schützin) ✓ | Klaas (Fechter) ✓ | Klara (Alchemistin) ✓ |
| 3 (S.5+6)              | Beatriz (Polizistin) ✓ | Clementine (Bastlerin) ✓ | The Shroud (Vigilant) ✓ | Aidan (Held) ✓ |
| 4 (S.7+8, Aventurien)  | Leomara (Kriegerin) ✓ | Hesindian (Magier) ✓ | Romoxosch (Zwerg) ✓ | Angrond (Streuner) ✓ |
| 5 (S.9+10)             | Sozius (Pilot) ✓ | Samael (Pistoliero) ✓ | Asera (Kopfgeldj.) ✓ | Zoetta (Planerin) ✓ |

**ERGEBNIS: alle 20 Archetypen (5 Bögen × 4) korrekt zugeordnet gespeichert** — die horizontale
Spiegelung wurde durchgehend richtig berücksichtigt. Jeder Front-Charakter trägt exakt die
Rückseiten-Handicaps/-Talente/-Mächte/-Ausrüstung der gespiegelten Position (Render+Crop gegen
die gespeicherten JSONs geprüft, alle deckungsgleich).

Build-Skripte: `logs/ulisses/build_swae.py`, `build_hexxen.py`, `build_aventurien.py`.
