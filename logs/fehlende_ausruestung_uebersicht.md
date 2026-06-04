# Fehlende Ausrüstung pro Setting (Stand: 2026-06-04)

Systematische Cross-Prüfung: Items, die im Archetyp-Bogen genannt werden, aber im entsprechenden Setting-Katalog (`settings/*.json`) fehlen.

**Methodik:**
1. Parse Archetyp-Texte (`Texte/*Archetypen*`) → GEAR-Sektion pro Archetyp
2. Iteriere durch die `*_EXPECTED`-Listen (aus Build-Scripts abgeleitet)
3. Prüfe jedes Item: (a) im GEAR-Text vorhanden? (b) im Katalog (via Alias-Map) auflösbar?
4. Items, die im Bogen vorkommen aber keinen Katalog-Match haben → MISSING

**Hinweis:** Nur Items, die im Bogen TEXTUELL genannt werden, werden erfasst. Substitutions/Approximationen im Build sind hier nicht sichtbar.

---

## 1) SciFi Kompendium — `Texte/SciFi Kompendium Archetypen.txt`

**Archetypen geparst:** 12

**Erwartete Archetypen gematcht:** 12/36

**Items im Bogen aber fehlend im Katalog: 0**


## 2) Superkräfte — `Texte/Superkräfte Archetypen.txt`

**Archetypen geparst:** 11

**Erwartete Archetypen gematcht:** 9/11

**Items im Bogen aber fehlend im Katalog: 1**

- ❌ **luchadore mask** — fehlt in: THE BRAWLER

## 3) SuSK (Sundered Skies) — `Texte/SuSK Archetypen.txt`

**Archetypen geparst:** 6

**Items im Bogen aber fehlend im Katalog: 6**

- ❌ **15 Kugeln mit Schießpulver** — fehlt in: WILDLING-PLÜNDERER
- ❌ **6 Pfund)** — fehlt in: ELFISCHER ASTBRECHER
- ❌ **Eichendornrüstung** — fehlt in: ELFISCHER ASTBRECHER
- ❌ **Schlafleintuch** — fehlt in: AUSERKORENER DRAKIN-MAGIER, ELFISCHER ASTBRECHER, GELÄUTERTER HIMMELSPIRAT, GLÜHBLÜTIGER SANGESPRIESTER, KRIEGSPRIESTER
- ❌ **Schwebeöl** — fehlt in: ELFISCHER ASTBRECHER
- ❌ **Wasserschlauch** — fehlt in: ELFISCHER ASTBRECHER, GELÄUTERTER HIMMELSPIRAT, GLÜHBLÜTIGER SANGESPRIESTER, KRIEGSPRIESTER

## 4) SWAE Wilde Welten — `Texte/SWAE_Wilde_Welten_Archetypen.txt`

**Archetypen geparst:** 7

**Items im Bogen aber fehlend im Katalog: 8**

- ❌ **2 Berettas M92SB + 4 Magazine** — fehlt in: E. Ghisoni (Pistolero)
- ❌ **2 Schnappmesser** — fehlt in: T. Engelhardt (Muskeln),
- ❌ **Flachmann mit Whiskey** — fehlt in: R. Ulrich (Privatdetektiv)
- ❌ **Glock 9mm + 2 Magazine** — fehlt in: B. Geselan (Taxifahrer), P. Molotiw (Pfandleiher), R. Steiner (Professor), R. Ulrich (Privatdetektiv), V. Hugenau (Meisterdieb)
- ❌ **Glock 9mm mit 2 Extra-Magazinen** — fehlt in: T. Engelhardt (Muskeln),
- ❌ **Malaydoskop** — fehlt in: B. Geselan (Taxifahrer), E. Ghisoni (Pistolero), P. Molotiw (Pfandleiher), R. Steiner (Professor), R. Ulrich (Privatdetektiv), T. Engelhardt (Muskeln),, V. Hugenau (Meisterdieb)
- ❌ **Mobiltelefon** — fehlt in: B. Geselan (Taxifahrer), E. Ghisoni (Pistolero), P. Molotiw (Pfandleiher), R. Steiner (Professor), R. Ulrich (Privatdetektiv), T. Engelhardt (Muskeln),, V. Hugenau (Meisterdieb)
- ❌ **Schalldämpfer für Berettas** — fehlt in: E. Ghisoni (Pistolero)

