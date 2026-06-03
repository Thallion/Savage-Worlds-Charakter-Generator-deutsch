# Abgleich: „Wildes Aventurien" (Fan-Konversion) ↔ Savage Aventurien.json

**Stand:** 2026-06-03
**Quellen:**
- `Texte/Wildes-Aventurien-V2.3.pdf` (50 S., vollständige Sammlung)
- `Texte/Wildes_Aventurien.pdf` (Ver. 3.0, 20 S., überarbeiteter Stab-Talentbaum + Handicaps)

**Ziel:** Prüfen, welche Talent-/Handicap-Vorschläge der PDFs bereits durch das
integrierte Fantasy Kompendium (FK) abgedeckt sind, und nur die DSA-spezifischen
Lücken ergänzen.

**Implementierung:** `scripts/dsa_add_wildes_aventurien.py` (idempotent)
**Backup:** `backup/settings/Savage Aventurien_vor_wildes_aventurien_20260603.json`

---

## 1. Talente

| PDF-Talent | Kategorie (PDF) | Status | Aktion |
|------------|-----------------|:------:|--------|
| Vertrauter | Macht | ✅ vorhanden | — |
| Alchemist | Experte | ✅ vorhanden | — |
| Meisteralchemist | Experte | ✅ vorhanden | — |
| Beschwörer | Experte | ✅ `AH (Beschwörer)` | — |
| Artefaktbauer | Experte | ✅ funktional (`Artefakterschaffer` + Meister-Variante) | — |
| Kraftlinienmagie | Machttalent | ❌ fehlt | **ergänzt** (Magier, H) |
| Kugelzauber | Machttalent | ❌ fehlt | **ergänzt** (Magier, A) |
| Mirakel | Machttalent | ❌ fehlt | **ergänzt** (Kleriker, A) |
| Magischer Alltag | Machttalent | ❌ fehlt (nur `Gnomenmagie` nah) | **ergänzt** (Macht, A) |
| Knochenkeule | Machttalent | ❌ fehlt | **ergänzt** (Schamane, F) |
| Elfenlieder | Machttalent | ⚠️ Bardenlieder da, elf-spez. fehlt | **ergänzt** (Macht, A) |
| Hexenflüche | Machttalent | ⚠️ Hexerei-Talente da, Fluch fehlt | **ergänzt** (Hexe, A) |
| Dolch des Druiden | Machttalent | ⚠️ `Herzholzstab` nah | **ergänzt** (Druide, A) |
| Bindung des Stabes | Machttalent (V3.0) | ❌ fehlt | **ergänzt** (Magier, A) |
| Fokus des Stabes | Machttalent (V3.0) | ❌ fehlt | **ergänzt** (Magier, F) |
| Flammenschwert | Machttalent (V3.0) | ❌ fehlt | **ergänzt** (Magier, V) |
| Zauberspeicher | Machttalent | ❌ fehlt | **ergänzt** (Magier, V) |
| Kraftfokus | Machttalent | ⚠️ `Zauberstab-Meisterschaft` andere Mechanik | **ergänzt** (Magier, V) |
| Eisenaffine Aura | Hintergrundtalent | ❌ fehlt | **ergänzt** (Hintergrund, A) |
| Schelm | Hintergrundtalent | ❌ fehlt | **ergänzt** (Hintergrund, A) |
| Prophezeien | Expertentalent | ❌ fehlt | **ergänzt** (Experte, A) |
| Profane Stabzauber | Machttalent (V2.3) | ⏭️ verworfen | von V3.0-Stabbaum abgelöst |
| Waffen-Stabzauber | Machttalent (V2.3) | ⏭️ verworfen | = `Flammenschwert` (V3.0) |

**Ergebnis Talente:** 16 ergänzt, 5 bereits vorhanden, 2 zugunsten der V3.0-Variante verworfen.

### Stab-Talentbaum (Reihenfolge)

```
Bindung des Stabes (A)  →  Fokus des Stabes (F)  →  Flammenschwert (V)
```

Zusätzlich eigenständig: `Zauberspeicher` (V), `Kraftfokus` (V).

---

## 2. Handicaps

| PDF-Handicap | Status | Aktion |
|--------------|:------:|--------|
| Artefaktgebunden (leicht) | ❌ fehlt | **ergänzt** (1 P) |
| Novize/Eleve (leicht/schwer) | ❌ fehlt | **ergänzt** (1 / 2 P) |
| Stigma (leicht/schwer) | ⚠️ nur `Hässlich` (−1 Überreden) nah | **ergänzt** (1 / 2 P) |
| Lästige Mindergeister (leicht, V3.0) | ❌ fehlt | **ergänzt** (1 P) |

**Ergebnis Handicaps:** 6 Einträge (4 Konzepte) ergänzt.

---

## 3. Nicht umgesetzte PDF-Hinweise

| Element | Bemerkung |
|---------|-----------|
| Gestrichene SW-Talente `Analphabet`, `Elan` | PDF markiert sie als „nicht genutzt". Noch **nicht** aus dem Setting entfernt (optional, Status 3). |
| Macht **Weissagung** | Von `Prophezeien` referenziert, fehlt im Setting. Kandidat für Phase 6.2 (neue Mächte). |
| AH (Fey) | Im Setting nicht vorhanden; `Elfenlieder` nutzt ersatzweise `Zaubern W6` + „Elf oder Halbelf". |
| Neue Fertigkeiten / Wissensfertigkeiten (Alchemie, Magiekunde, Region, …) | Eigenes Thema (Fertigkeiten-Phase), hier nicht behandelt. |
| Mächte-Anpassungen (Zauberdauer, Barriere, Eigenschaft stärken …) | Gehört zu Phase 6, hier nicht behandelt. |

---

## 4. Anpassungs-Entscheidungen (Reconciliation V2.3 ↔ V3.0)

- **Stab-Baum:** V3.0-Variante (`Bindung`/`Fokus`/`Flammenschwert`) als kanonisch
  gewählt, da klar gestufte Voraussetzungskette. V2.3-Pendants (`Profane`/`Waffen-Stabzauber`)
  verworfen.
- **Artefaktgebunden:** Malus −4 (V3.0) statt −6 (V2.3).
- **Voraussetzungen** auf Setting-Vokabular gemappt:
  `Zauberei → Zaubern`, `Willenskraft → WIL`, `Verstand → VER`,
  `Wissen (Magiekunde) → Okkultismus`, `Gildenmagier → AH (Magier)`,
  `Arkaner Hintergrund (Magie) → AH (Magie)`, `… (Wunder) → AH (Wunder)`.

---

## 5. Validierung

- [x] JSON valide & lädt (`json.load`)
- [x] Semantischer Diff gegen Backup: 0 alte Talente/Handicaps verloren oder verändert
- [x] `dsa_trappings` der Mächte unverändert (699 = 699)
- [x] Alle anderen Top-Level-Keys identisch
- [x] Voraussetzungs-Kette des Stab-Baums verweist auf existierende Talente
- [ ] In-App-Test: Talente/Handicaps in der UI auswählbar (offen, Phase 11)
- [ ] Balancing-Review gegen FK (offen, Phase 9.R)
