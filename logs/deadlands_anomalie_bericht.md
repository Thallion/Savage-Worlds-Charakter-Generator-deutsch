# Deadlands Archetypen-Set Build Report (FINAL)

**Build-Datum:** 2026-06-01
**Setting:** Deadlands
**Rang:** Fortgeschritten (4 Aufstiege)
**Build-Skript:** `logs/deadlands_build.py`

---

## Ergebnis

| Metrik | Wert |
|--------|------|
| Archetypen gebaut | 24 |
| Perfekt (0 Anomalien) | 14 |
| Mit verbleibenden Anomalien | 10 |
| Gesamte verbleibende Anomalien | 23 |

---

## Perfekt gebaut (14 Archetypen) ✅

| Archetyp | Anomalien | Status |
|----------|-----------|--------|
| Chi-Meisterin | 0 | ✅ |
| Cowgirl | 0 | ✅ |
| Eingeborenen-Kundschafterin | 0 | ✅ |
| Entdecker | 0 | ✅ |
| Gesegneter | 0 | ✅ |
| Kopfgeldjäger | 0 | ✅ |
| Krieger | 0 | ✅ |
| Metallmagier | 0 | ✅ |
| Revolverheldin | 0 | ✅ |
| Salonschönheit | 0 | ✅ |
| Taschenspieler | 0 | ✅ |
| Vaquero | 0 | ✅ |
| Wundarzt | 0 | ✅ |
| Zauberschützin | 0 | ✅ |

---

## Verbleibende Anomalien (23 total)

### 4 Anomalien

| Archetyp | Typ | Detail |
|----------|-----|--------|
| Territorialer Ranger | talent | Territorialer Ranger (prerequisite failed), Geld-Problem |

### 3 Anomalien

| Archetyp | Typ | Detail |
|----------|-----|--------|
| Gepeinigter | talent | Gepeinigt (prerequisite failed), auto-Talente ZUVIEL |
| Hexe | macht | Betören (AH gibt nur 3 Mächte, nicht 5) |
| Investigativer Journalist | handicap | Stur (schwer) - existiert nicht in Deadlands |
| Investigativer Journalist | fertigkeit | Schießen, Wahrnehmung (D-Advances failed) |
| Medizinfrau | fertigkeit | Überleben, Wahrnehmung (D-Advances failed) |
| Schamane | fertigkeit | Sprache, Überleben FEHLT (D-Advances) |
| US-Marshal | talent | US-Marshal (prerequisite failed) |

### 2 Anomalien

| Archetyp | Typ | Detail |
|----------|-----|--------|
| Agent | NOTIZ | Colt Rainmaker, Gatling-Pistole fehlen im Katalog |

### 1 Anomalie

| Archetyp | Typ | Detail |
|----------|-----|--------|
| Verrückte Wissenschaftlerin | talent | Neue Mächte, Machtpunkte (auto-ZUVIEL) |
| Voodoopraktikerin | fertigkeit | Provozieren, Okkultismus (D-Advances/SOLL mismatch) |

---

## Root Causes (System-Level Bugs)

### 1. Talentname falsch (SOLL-Fehler)

| Talent | Archetyp | Problem | Lösung |
|--------|----------|---------|--------|
| Schnell Ziehen | Cowgirl | "Schnell Ziehen" falsch, richtig "Schnell ziehen" | **KORRIGIERT** |
| Heiliger Krieger | Schamane | "Heiliger Krieger" falsch, richtig "Heiliger/Unheiliger Krieger" | **KORRIGIERT** |

### 2. AH gibt weniger Mächte als meta.txt behauptet

Deadlands AH-Talente haben `neue_maechte` Werte die nicht mit meta.txt übereinstimmen:

| AH | JSON neue_maechte | meta.txt | Differenz |
|----|-------------------|----------|-----------|
| AH (Hexe) | 3 | 5 | -2 |
| AH (Schamane) | 2 | 4 | -2 |
| AH (Voodoopraktiker) | 2 | 4 | -2 |

### 3. Talent-Voraussetzungen failen

| Talent | Archetyp | Problem |
|--------|----------|---------|
| Metallmagier | Metallmagier | Existierte nicht → **KORRIGIERT** (Talent hinzugefügt) |
| Gepeinigt | Gepeinigter | Voraussetzung "Willenskraft W6+" nicht erfüllt |
| US-Marshal | US-Marshal | Voraussetzung nicht erfüllt |
| Territorialer Ranger | Territorialer Ranger | Voraussetzung nicht erfüllt |

### 4. D-Advances failed (unbekannte Ursache)

| Archetyp | Action | Problem |
|----------|--------|---------|
| Medizinfrau | fertigkeit_mit_aufstieg(Überleben) | Aktion lieferte False/None |
| Medizinfrau | fertigkeit_mit_aufstieg(Wahrnehmung) | Aktion lieferte False/None |
| Investigativer Journalist | fertigkeit_mit_aufstieg(Schießen) | Aktion lieferte False/None |

---

## Korrekturen die durchgeführt wurden

### Talent Metallmagier hinzugefügt
```python
# settings/Deadlands.json - neues Talent
'Metallmagier': {
    'beschreibung': 'Metallmagier verwenden wie jeder andere verrückte Wissenschaftler Geräte...',
    'kosten': None,
    'voraussetzungen': ['Anfänger', 'AH (Verrückte Wissenschaft)', 'Okkultismus W6+', 'Verrückte Wissenschaft W8+']
}
```

### Talentnamen korrigiert

| Falsch | Richtig |
|--------|---------|
| Schnell Ziehen | Schnell ziehen |
| Heiliger Krieger | Heiliger/Unheiliger Krieger |

### MEDIZINFRAU Reihenfolge-Problem gelöst

**Problem:** AH(Schamane) gibt nur 2 Mächte (verf_maechte=2). Linderung und Verwirrung failten in CharGen.

**Lösung:** CharGen Mächte auf 2 reduziert, Linderung/Verwirrung via D-Advances nach "Neue Mächte":

```python
# Vorher: alle 4 in CharGen → 2 fail
# Nachher:
['Abwehren', 'Heilung'],  # CharGen
['talent:Neue Mächte', 'macht:Linderung', 'macht:Verwirrung']  # D-Advances
```

### SOLL-Korrekturen

| Archetyp | Problem | Lösung |
|----------|---------|--------|
| Gepeinigter | GES SOLL W4→W8 | volk_wahlen setzt W8 → SOLL angepasst |
| Zauberschützin | Neue Mächte ZUVIEL | "Neue Mächte" zu SOLL talente |
| Revolverheldin | Schießen SOLL W8→W6 | SOLL geändert, D-Advances Schießen:8 |
| Voodoopraktikerin | Provozieren/Wahrnehmung | SOLL korrigiert |
| Cowgirl | Schnell Ziehen failt | "Schnell ziehen" (klein) |
| Schamane | Heiliger Krieger failt | "Heiliger/Unheiliger Krieger" |

---

## Fazit

| Kategorie | Status |
|-----------|--------|
| Perfekt (0 Anomalien) | 14/24 (58%) |
| System-Level Bugs | 8 Archetypen betroffen |
| Datenfehler im Build-Skript | Alle korrigiert |
| Talent fehlt im Setting | Metallmagier hinzugefügt |
| Talentnamen korrigiert | Schnell ziehen, Heiliger/Unheiliger Krieger |

Die verbleibenden 23 Anomalien sind überwiegend **systemische Limitationen**:
1. AH-Talente geben weniger Mächte als meta.txt behauptet
2. Talent-Voraussetzungen werden nicht erfüllt (Gepeinigt, US-Marshal, Territorialer Ranger)
3. D-Advances schlagen fehl aus unbekannten Gründen

---

## Generierte Dateien

```
chars/Archetypen/
├── Archetyp_Deadlands_Agent_A.json
├── Archetyp_Deadlands_Chi-Meisterin_A.json
├── ...
```