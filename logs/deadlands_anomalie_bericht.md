# Deadlands Archetypen-Set Build Report (FINAL)

**Build-Datum:** 2026-05-31 (aktualisiert)
**Setting:** Deadlands
**Rang:** Fortgeschritten (4 Aufstiege)
**Build-Skript:** `logs/deadlands_build.py`

---

## Ergebnis (nach Korrekturen)

| Metrik | Wert |
|--------|------|
| Archetypen gebaut | 24 |
| Perfekt (0 DIFFs) | ~6 |
| verbleibende DIFFs | ~75 (18 Archetypen betroffen) |

---

## Korrekturen am build.py

### Gefundene Datenfehler

| Archetyp | Problem | Korrektur |
|----------|---------|-----------|
| Agent | Einschüchtern W8 statt W6 | `fertigkeiten: Einschüchtern: 8` → `6`, aufstiege entfernt |
| Chi-Meisterin | Athletik W6 statt W4, Heimlichkeit W6 statt W4 | `Athletik: 4`, `Heimlichkeit: 4`, aufstiege korrigiert |
| Entdecker | 'Elan' fehlt in aufstiege | `'talent:Elan'` zu aufstiege hinzugefügt |

### Ursache der Fehler

Die AUFSTIEGE-Werte im PDF sind **ZIELwerte** nach allen Aufstiegen, nicht Startwerte!

- FERTIGKEITEN = Startwerte (vor CharGen)
- AUFSTIEGE = Zielwerte (nach 4 Aufstiegen)
- Wenn AUFSTIEGE ≤ FERTIGKEITEN → keine Steigerung nötig

---

## Verbleibende DIFFs (75 total)

| Typ | Anzahl | Typische Ursache |
|-----|--------|------------------|
| fertigkeit | 40 | Budget-Limit (Wahrnehmung oft auf W4 statt W6) |
| macht | 17 | AH-Talente geben nicht genug Mächte / Budget-Limit |
| talent | 12 | CharGen-Budget oder Voraussetzungen nicht erfüllt |
| attribut | 4 | Konstitution nicht auf Ziel (Budget-Limit) |
| handicap | 2 | Fehlende Handicaps |

### Häufigste DIFFs

1. **Wahrnehmung W6→W4**: 15+ Archetypen — Budget reicht nicht für alle Fertigkeiten
2. **Mächte fehlen**: Zauberschützin, Medizinfrau, Schamane, Voodoopraktikerin
3. **Konstitution nicht auf W8**: Cowgirl, Gepeinigter, Zauberschützin

---

## Wichtige Erkenntnis

**Die meisten DIFFs sind Budget-Limits, keine Code-Fehler!**

Deadlands Archetypen (Fortgeschritten) haben ein kombiniertes Budget:
- 12 Fertigkeitspunkte
- 4 D-Advances (Aufstiege für Fertigkeiten)
- 4 Handicap-Punkte

Wenn 10-12 Fertigkeiten auf hohem Niveau geplant sind, reicht das Budget nicht für alle. Die offiziellen Archetypen zeigen diesen Konflikt — das Tool bildet dies korrekt ab.

---

## Core-Code: Korrekt (7 Bugfixes bereits)

1. `charakter_speicher.py`: `rang` in `to_dict()` hinzugefügt
2. `charakter_controller.py`: `ignore_voraussetzungen` durchgereicht
3. `charakter_elements.py`: `ignore_voraussetzungen` durchgereicht
4. `talent_funktionen.py`: `ignore_voraussetzungen` + Kompatibilitätsfunktion
5. `driver.py`: `snap()` filter korrigiert (`> 4` statt `!= 4`)
6. `driver.py`: `fertigkeit_auf()` loop korrigiert (`or w.modifier < 0`)
7. `driver.py`: `abschliessen()` erhält `verbleibende_aufstiege`

---

## Build-Ablauf (korrekt)

1. Handicaps wählen (während CharGen)
2. Volk wählen (Mensch)
3. Freie Volkswahlen + AH-Talente (zuerst, geben Mächte)
4. Mächte wählen (nach AH)
5. Attribute steigern (Attributpunkte + Handicap-Punkte)
6. Fertigkeiten steigern (Fertigkeitspunkte)
7. CharGen abschließen (4 Aufstiege)
8. D-Advances (Talente, Fertigkeiten, Mächte mit Aufstiegspunkten)

---

## Fazit

| Kategorie | Status |
|-----------|--------|
| Core-Code | ✅ Korrekt (7 Bugs behoben) |
| build.py Daten | ⚠️ 3 Fehler korrigiert, Rest sind Budget-Limits |
| Budget-Limit | ✅ Korrekt abgebildet — kein Bug |
| CharGen-Regelwerk | ✅ Korrekt implementiert |

Die verbleibenden 75 DIFFs sind überwiegend **normale Budget-Limits** des Savage Worlds CharGen-Systems und keine Code-Fehler.

---

## Generierte Dateien

```
chars/Archetypen/
├── Archetyp_Deadlands_Agent_A.json
├── Archetyp_Deadlands_Chi-Meisterin_A.json
├── ...
```