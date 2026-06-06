# Savage Aventurien — Deep Review (Kodex-basiert)

**Erstellt:** 2026-06-06
**Basis:** `settings/Savage Aventurien.json` (9 Völker · 493 Talente · 166 Handicaps · 66 Mächte) gegen
`Texte/Kodex_der_Magie.pdf`, `Kodex_der_Helden.pdf`, `Kodex_des_Götterwirkens.pdf`, `Wildes_Aventurien*.pdf`.
**Zweck:** Was ist noch **unpassend** (raus/umbenennen)? Was **fehlt**? Sonderfrage: **Magieschulen-Talente?**

> Dies ist ein **Review-/Empfehlungsdokument** — noch nichts umgesetzt. Reihenfolge/Umfang der Umsetzung nach Abnahme.

---

## A. Unpassende Elemente (Empfehlung: entfernen / umbenennen / reflavoren)

### A1 — PF-Ancestry-Reste für Nicht-DSA-Völker  → **raus / umhängen**
Talente, deren Voraussetzung auf ein **gelöschtes PF-Volk** zeigt (tote Prereqs, nie wählbar):
| Talent | Tote Voraussetzung | Empfehlung |
|---|---|---|
| `Rüstung des Abgrunds` | Volk: Tieflinge | **löschen** (Tiefling-Höllenrüstung, kein DSA-Volk) |
| `Krallensturz` | Volk: Katzenfolk | **löschen** (Katzenvolk kein DSA-Volk) |
| `Kletterranke` | Weinranken-Leshy | **löschen** (Pflanzenwesen-Ancestry) |
| `Kudzu-Ringer` | Weinranken-Leshy | **löschen** |
| `Lässiger Illusionist` | Volk: Gnom | **umhängen** auf `AH (Illusionist)` statt löschen (gute Illusions-Mechanik, Gnom raus) |

### A2 — PF-System-Fremdkörper (Settings, die es in DSA nicht gibt)  → **raus**
| Talent | Problem | Empfehlung |
|---|---|---|
| `Mentalist` | Vor. `AH (Psionik)` – Psionik existiert in DSA/Setting nicht | **löschen** |
| `Bastler` | Vor. `AH (Verrückte Wissenschaft)` – Steampunk-Gadgets, kein DSA | **löschen** |

### A3 — Beschwörer/Eidolon-Komplex (PF-Summoner)  → **reflavoren oder reduzieren**
Die Kategorie **Beschwörer** ist noch **reine PF-Eidolon-Mechanik**: „gebundene Wesenheit", „Entwicklungspunkte", „verschmelzen".
Betroffen: `Aspekt`, `Lebensband`, `Zwillingswesenheit`, `Zusätzliche Evolution`, `Ruf des Beschwörers`, `Ruf des Schöpfers`, `Höhere Beschwörung`, `Arkane Stärkung`.
**DSA-Befund (Magie-Kodex):** Ein Beschwörer **ruft Dämonen/Elementare/Geister** und **bindet** sie zeitweise — er hat **kein** dauerhaft mitwachsendes „Eidolon" mit Evolutionspunkten. Das ständige Begleitwesen + Verschmelzen ist un-DSA.
**Empfehlung:** entweder
1. **reflavoren** zu „**gebundener Dämon/Elementar**" (Begleitwesen = beschworener Diener; Evolutionspunkte → „Machtstufen des Dieners") — behält die Mechanik, oder
2. **abspecken** auf Beschwörungs-Mächte (Verbündete beschwören) + wenige Talente; Eidolon-Spezifika (Verschmelzen, Evolution) löschen.
→ Entscheidung nötig.

### A4 — Wuxia-/Asia-Begriffe in Kategorie **Hruruzat**  → **umbenennen**
Nach Mönch→Hruruzat sind die Talentnamen noch fernöstlich (Kung-Fu-Film), nicht aventurisch:
| Alt | Vorschlag (DSA/Hruruzat) |
|---|---|
| `Kranich-Stil` | **Hruruzat-Form** (oder konkrete Form, z. B. „Form des Skorpions") |
| `Bebende Handfläche` | **Erschütternder Schlag** |
| `Versteinerungsschlag` | **Lähmender Nervenschlag** |
| `Bebende Handfläche`/`Versteinerungsschlag` Beschreibungen | DSA-Regelbegriffe prüfen |
(`Mächtige Innere Kraft` bereits ok; `Betäubende Fäuste`, `Waffenloser Schlag`, `Kämpferische Disziplin`, `Beweglichkeit` sind neutral.)

### A5 — Alignment-/D&D-Reste  → **umbenennen**
| Talent | Problem | Empfehlung |
|---|---|---|
| `Heiliger/Unheiliger Krieger` | Gut/Böse-Achse (D&D) | umbenennen **`Glaubenskrieger`**, „heilig/unheilig" → „geweiht" |
(„Das Unheilige erspüren", „Niederstrecken des Unheiligen" sind **OK** — DSA-Feindbild Dämonen/Untote, keine Alignment-Achse.)

### A6 — Von Wildes Aventurien gestrichenes SW-Talent  → **raus**
| Element | Empfehlung |
|---|---|
| `Elan` (Talent) | **löschen** (WA streicht Elan; Plan §8.5) |
| `Analphabet` (Handicap) | WA streicht es zwar — aber Analphabetentum ist in DSA verbreitet/sinnvoll → **behalten** (Abweichung von WA bewusst) |

### A7 — „Mystische Mächte (weltliche Profession)"  → **prüfen**
`Mystische Mächte (Schurke)`, `(Waldläufer)`, `(Hruruzat)` geben **mundanen** Professionen je 10 gewidmete Machtpunkte. In DSA gibt es **keine** mundanen Halbzauberer (anders als PF Magus/Ranger).
- `Mystische Mächte (Inquisitor)` = **OK** (Praios-Laienwirken, göttlich begründet).
- Schurke/Waldläufer/Hruruzat: **un-DSA** → entweder löschen oder klar als seltene Begabung (AH-Voraussetzung) umdeuten.
→ Entscheidung nötig.

### A8 — Veraltete Verweise / vage Voraussetzungen  → **bereinigen**
| Talent | Problem | Fix |
|---|---|---|
| `Vertrauter` | AH-Liste enthält tote Namen (`Diabolist`, `Hexer`, `Zauberer`, `Elementarmagier`) | auf gültige AHs setzen: Druide, Schamane, Nekromant, Paktierer, Dämonologe, Hexe, Elementarist, Magier |
| `Elementare Absorption` | Vor. `AH (Elementarmagier)` (existiert nicht) | → `AH (Elementarist)` |
| `Bestienmeister-Stil` | Vor. „Tiermeister **oder ähnliche Fähigkeit**" (unauswertbar) | → nur `Tiermeister` |
| `Wissenshüter` | Vor. `Ver W8` (Tippfehler) | → `VER W8` |
| `Mystische Kräfte` | Vor. `Fortgeschritten` (statt Rang-Code) | → `F` |
| PF-Macht-Refs | `Odemwaffe`, `Tier/Monster beschwören`, `Lykanthropie` als Vorauss. | als Trapping/Talent zuordnen oder Prereq lockern |

---

## B. Fehlende DSA-Konzepte (Kandidaten zum Ergänzen)

| Konzept | Status im Setting | Bewertung |
|---|---|---|
| **Magieschulen / Akademien** | generisch via Talent `Schule` + `Bevorzugte Mächte (Magier)` | **ausreichend abgebildet** — siehe C |
| **Merkmalskenntnis** (Spezialisierung auf ein Magie-Merkmal) | via `Bevorzugte Mächte`/`Schule` | abgedeckt |
| **Repräsentation** (Tradition: Gildenmagier, Elf, Druide, Hexe, Geode, Schelm, Zibilja, Kristallomant, Zaubertänzer, Geweihte) | als eigene `AH (…)` vorhanden | **vollständig** |
| **Borbaradianer / Demonologe-Tiefe** | `AH (Dämonologe)` + `AH (Paktierer)` | vorhanden; ausreichend |
| **Außeralveranische Geweihte** (Rastullah, Namenloser, Levthan…) | bewusst weggelassen (§0ter) | **kein Bedarf** |
| **Weltliche Professionen** (Schmied, Seemann, Gladiator…) | via `Experte`-Talente + Fluff | abgedeckt (User-Entscheidung: nur Fluff) |
| **Geode-Kraftlinien/Erzkunde, Zibilja-Trommelmagie** | AH vorhanden, Mächte generisch | optional: ikonische Trappings ergänzen |

**Kurz: Es fehlt strukturell wenig.** Der größte „Mangel" ist eher Bereinigung (Abschnitt A) als Ergänzung.

---

## C. Sonderfrage: Magieschulen-Talente?

**DSA-Befund (Magie-Kodex):** Gildenmagier werden an **Akademien** ausgebildet (Z. 9549 ff.), jede mit Schwerpunkt-Fachbereichen und einer **Repräsentation/Hauszauber**-Liste; Spezialisierung läuft über **Merkmalskenntnis** (Z. 1087).

**Im Setting bereits vorhanden:**
- Talent **`Schule`** (Kat. Magier): „wählt eine Schule, die bestimmt, auf welche **Arten von Mächten** er sich spezialisiert" = funktional die Akademie-/Merkmals-Spezialisierung.
- **`Bevorzugte Mächte (Magier)`** = bevorzugte Sprüche (Repräsentation/Hauszauber-Äquivalent).
- **`AH (Magier)`** + Stabmagie-Talente (Bindung/Fokus des Stabes, Kraftlinienmagie …) = Gildenmagier-Handwerk.

**Empfehlung: KEINE 20–30 Einzel-Akademie-Talente anlegen** (Bloat, widerspricht „nur wo sinnvoll und nötig"). Stattdessen:
1. **`Schule`-Beschreibung anreichern** mit aventurischen Akademie-/Schwerpunkt-Beispielen als Auswahl-Fluff, z. B.:
   - *Schwarze Akademie zu Al'Anfa* (Verwandlung/Nekromantie-nah), *Halle der Antimagie zu Lowangen* (Antimagie), *Akademie der Magischen Rüstung zu Gareth* (Schutz/Kampf), *Weiße Halle zu Norburg* (Heilung/Hellsicht), *Schule der Verformungen* (Verwandlung), *Drachenei-Akademie zu Elenvina* (Beschwörung).
   - Mechanik unverändert: Spezialisierung auf Macht-Art(en).
2. Optional **ein** generisches Talent **`Hauszauber`** (Kat. Magier): eine bei Akademie-Wahl bestimmte Macht ist um −1 MP günstiger / +1 auf die Probe — falls mehr Akademie-Gefühl gewünscht. (Nur falls erwünscht; sonst Status 5.)

→ **Default-Empfehlung:** Variante 1 (Fluff in `Schule`), kein neues Mechanik-Talent.

---

## D. Priorisierte Umsetzungs-Empfehlung

1. **Schnelle Bereinigung (geringes Risiko):** A1 (5 Ancestry-Talente), A2 (Mentalist, Bastler), A6 (Elan), A8 (tote/vage Prereqs).  → ~9 Löschungen + ~6 Prereq-Fixes.
2. **Umbenennungen (Flavor):** A4 (Hruruzat-Namen), A5 (Glaubenskrieger).
3. **Entscheidungsbedarf:** A3 (Beschwörer/Eidolon reflavoren vs. abspecken), A7 (Mystische Mächte weltlich).
4. **Magieschulen:** C-Variante 1 (Fluff in `Schule`).

**Offen für Abnahme** — sag, welche Blöcke ich umsetzen soll (1 ist sofort safe machbar).

---

## E. Umsetzungs-Status (User-Entscheidungen 2026-06-06)

> Backup `pre_deepreview_block1_20260606.json`. 493→**486 Talente**. Tests grün (124).

- **A1 PF-Ancestry ✅:** gelöscht: Rüstung des Abgrunds, Krallensturz, Kletterranke, Kudzu-Ringer. `Lässiger Illusionist` → Vor. `AH (Illusionist)`.
- **A2 PF-Fremdsysteme ✅:** Mentalist **und** Bastler gelöscht.
- **A4 Wuxia ✅:** Kranich-Stil→**Hruruzat-Form**, Bebende Handfläche→**Erschütternder Schlag**, Versteinerungsschlag→**Lähmender Nervenschlag**.
- **A5 Alignment ✅:** Heiliger/Unheiliger Krieger→**Glaubenskrieger** (heilig/unheilig→geweiht).
- **A6 Elan:** **bleibt** (User-Entscheidung, entgegen WA).
- **A8 Verweise ✅:** Vertrauter (saubere AH-Liste), Elementare Absorption→`AH (Elementarist)`, Bestienmeister-Stil→`Tiermeister`, Wissenshüter→`VER W8`, Mystische Kräfte→`F`, Schnelle Verwandlung→`Tiergestalt`. **Versengen gelöscht** (PF-Drachenodem ohne Odemwaffe sinnlos).
- **A7 Mystische Mächte (Schurke/Waldläufer/Hruruzat): ⏸ Wiedervorlage** (zurückgestellt).
- **A3 Beschwörer/Eidolon: ✅ KOMPLETT GELÖSCHT** (User: „nehmen wir komplett raus – Vertrautentier + Elementarbeschwörungen decken das Thema ab"; Backup `pre_beschwoerer_raus_`). 9 Eidolon-Talente (Aspekt, Lebensband, Zwillingswesenheit, Zusätzliche Evolution, Ruf des Beschwörers/Schöpfers, Höhere/Ungezügelte Beschwörung, Arkane Stärkung) **+ `AH (Beschwörer)`** entfernt. Keine Rest-Referenzen (Vertrauter-AH-Liste enthielt Beschwörer ohnehin nicht mehr). 486→**476 Talente**.
- **Magieschulen (C):** noch offen — Default = Fluff in `Schule`.
