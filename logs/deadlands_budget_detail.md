# DEADLANDS ARCHETYPEN - DETAILIERTE BUDGET-ANALYSE

## Zusammenfassung

| Metrik | Wert |
|--------|------|
| Archetypen gebaut | 24 |
| Perfekt (0 Anomalien) | 13 (54%) |
| Verbleibende Anomalien | 26 |
| System-Level Bugs | 9 Archetypen betroffen |

---

## 1. BUDGET-ÜBERSICHT (Fortgeschritten = 4 Aufstiege)

### CharGen Budget

| Ressource | Menge | Verwendungszweck |
|-----------|-------|------------------|
| Attributpunkte | 5 | Attribut-Steigerungen |
| Fertigkeitspunkte | 12 | Fertigkeiten kaufen |
| Handicap-Punkte | 4 (max) | Handicaps wählen → HP für Attribut-Steigerungen |
| Aufstiege | 4 | D-Advances (Talente, Fertigkeiten, Mächte) |

### D-Advances Budget (nach CharGen)

| Typ | Verwendungszweck |
|-----|------------------|
| Talent mit Aufstieg | Freie Talente (Neue Mächte, Metallmagier, etc.) |
| Fertigkeit mit Aufstieg | Fertigkeiten auf W6+ steigern |
| Attribut mit Aufstieg | Selten (Konstitution W6→W8) |
| Macht | Mächte kaufen (nach AH) |

---

## 2. KRITISCHE BUDGET-LIMITATIONEN

### 2.1 Attribut-Steigerungen durch Handicaps

```
4 HP (aus Handicaps)
-2 HP (AH-Talent, falls vorhanden)
= 2-4 HP für Attribute

Ziel: Konstitution W8 (= 4 Schritte von W4)
Aber: Nur 2-4 HP = max KON W6-W8
```

| Archetyp | HP verfügbar | Ziel KON | Erreicht | Status |
|----------|--------------|-----------|----------|--------|
| Cowgirl | 4 HP (kein AH) | W8 | W6 | ⚠️ Budget-Limit |
| Zauberschützin | 2 HP (AH) + attr | W4 | W4 | ✅ OK |
| Revolverheldin | 4 HP (kein AH) | W6 | W6 | ✅ OK |

### 2.2 Fertigkeits-Budget

```
12 Fertigkeitspunkte für ~10-12 Fertigkeiten auf W4-W8

Problem: Viele Archetypen wollen hohe Werte (W6-W8)
→ Wahrnehmung wird oft auf W4 gelassen (Grundfertigkeit)
```

| Archetyp | Wahrnehmung SOLL | Wahrnehmung IST | Grund |
|----------|-----------------|-----------------|-------|
| Medizinfrau | W6 | W4 | D-Advance fehlgeschlagen |
| Kopfgeldjäger | W6 | W4 | D-Advance fehlgeschlagen |
| US-Marshal | W6 | W4 | D-Advance fehlgeschlagen |
| Voodoopraktikerin | W6 | W4 | D-Advance fehlgeschlagen |

---

## 3. AH-POWER-BUDGET (KRITISCH)

### Das Problem: AH gibt weniger Mächte als meta.txt

| AH | JSON `neue_maechte` | meta.txt SOLL | Differenz |
|----|--------------------|---------------|-----------|
| AH (Gesegneter) | 3 | 5 | -2 |
| AH (Hexe) | 3 | 5 | -2 |
| AH (Schamane) | 2 | 4 | -2 |
| AH (Voodoopraktiker) | 2 | 4 | -2 |
| AH (Verrückte Wissenschaft) | 2 | 4 | -2 |

### MEDIZINFRAU: Reihenfolge-Problem und Lösung

**Problem:** Medizinfrau hat 4 Mächte im SOLL, aber AH(Schamane) gibt nur 2 Mächte (verf_maechte=2).
Die 4 Mächte wurden alle während CharGen versucht → Linderung und Verwirrung failten.

```
Schritt 7: macht(Abwehren) → ok=True, verf_maechte=1
Schritt 8: macht(Heilung) → ok=True, verf_maechte=0
Schritt 9: macht(Linderung) → ok=False (keine Slots mehr!)
Schritt 10: macht(Verwirrung) → ok=False
```

**Lösung:** CharGen Mächte auf 2 reduziert, Linderung/Verwirrung via D-Advances nach "Neue Mächte":

```python
# Vorher (fehlerhaft):
['Abwehren', 'Heilung', 'Linderung', 'Verwirrung'],  # alle 4 in CharGen

# Nachher (korrigiert):
['Abwehren', 'Heilung'],  # CharGen: nur 2 von AH
# D-Advances:
['talent:Neue Mächte',  # ← VOR den additionalen Mächten
 'macht:Linderung', 'macht:Verwirrung']
```

### Beispiel: Hexe

```
SOLL: 5 Mächte (Betören, Empathie, Flächenschlag, Kriegersegen, Verwirrung)
AH (Hexe) gibt: 3 Mächte (laut JSON)
D-Advances "Neue Mächte": +2 (theoretisch)

Problem: Betören failt weil AH nur 3 Mächte erlaubt
→ 2 Mächte fehlen (Betören, Kriegersegen)
```

---

## 4. TALENT-BUDGET

### 4.1 Talent-Voraussetzungen failen

| Talent | Archetyp | Voraussetzung | Problem |
|--------|----------|---------------|---------|
| Metallmagier | Metallmagier | Okkultismus W6+, Verrückte Wissenschaft W8+ | **KORRIGIERT** (Talent hinzugefügt) |
| Gepeinigt | Gepeinigter | Willenskraft W6+ | W6 vorhanden aber failt? |
| Heiliger Krieger | Schamane | ? | prerequisite failed |
| US-Marshal | US-Marshal | ? | prerequisite failed |
| Territorialer Ranger | Territorialer Ranger | ? | prerequisite failed |

### 4.2 Auto-Talente (ZUVIEL im SOLL/IST-DIFF)

AH-Talente setzen automatisch Talente wie "Neue Mächte" oder "Machtpunkte".
Diese erscheinen im IST aber nicht im SOLL → "ZUVIEL" warnings.

| Archetyp | Auto-Talent | Ursache |
|----------|-------------|---------|
| Gepeinigter | Flicken, Gepeinigt, Killerinstinkt | volk_wahlen + AH setzt diese auto |
| Gesegneter | Neue Mächte | AH (Gesegneter) gibt "Neue Mächte" auto |
| Schamane | Neue Mächte | AH (Schamane) gibt "Neue Mächte" auto |
| Verrückte Wissenschaftlerin | Machtpunkte | AH gibt "Machtpunkte" auto |
| Voodoopraktikerin | Machtpunkte | AH gibt "Machtpunkte" auto |
| Hexe | Machtpunkte, Neue Mächte | AH gibt beides auto |

**Lösung**: SOLL um Auto-Talente erweitern (in deadlands_build.py bereits korrigiert für Zauberschützin)

---

## 5. D-ADVANCES FAILURES

### Unbekannte Ursachen - D-Advances schlagen fehl

| Archetyp | Action | Fehler |
|----------|--------|--------|
| Cowgirl | talent_mit_aufstieg(Schnell Ziehen) | ok=False |
| Medizinfrau | fertigkeit_mit_aufstieg(Überleben) | ok=False |
| Medizinfrau | fertigkeit_mit_aufstieg(Wahrnehmung) | ok=False |
| Investigativer Journalist | fertigkeit_mit_aufstieg(Schießen) | ok=False |

**Mögliche Ursachen:**
1. Aufstiege bereits auf Maximum (keine verbleibenden Aufstiege)
2. Zielwert bereits erreicht (keine Steigerung nötig)
3. Voraussetzungen nicht erfüllt
4. Kosten nicht bezahlbar (Geld/Budget)

---

## 6. GELÖSTE PROBLEME

### 6.1 SOLL-Fehler korrigiert

| Archetyp | Problem | Lösung |
|----------|---------|--------|
| Gepeinigter | GES SOLL W4→W8 | volk_wahlen setzt W8 → SOLL angepasst |
| Zauberschützin | Neue Mächte ZUVIEL | "Neue Mächte" zu SOLL talente |
| Revolverheldin | Schießen SOLL W8→W6 | SOLL W6, D-Advances W8 |
| Kopfgeldjäger | Wahrnehmung SOLL W4→W6 | SOLL W6, D-Advances W6 |
| Voodoopraktikerin | Provozieren/Wahrnehmung | SOLL korrigiert |
| Metallmagier | "Chaos"→"Strahl" | Tippfehler korrigiert |
| Medizinfrau | AH 4→2 Mächte + falsche Reihenfolge | SOLL angepasst, D-Advances korrigiert |
| Verrückte Wissenschaftlerin | Wahnvorstellungen | Nicht in Deadlands → entfernt |

### 6.2 Talent hinzugefügt

**Metallmagier** (neu in Deadlands.json):
```python
'Metallmagier': {
    'beschreibung': 'Metallmagier verwenden wie jeder andere verrückte Wissenschaftler Geräte...',
    'kosten': None,
    'voraussetzungen': ['Anfänger', 'AH (Verrückte Wissenschaft)', 'Okkultismus W6+', 'Verrückte Wissenschaft W8+']
}
```

### 6.3 MEDIZINFRAU: Reihenfolge-Problem gelöst

CharGen Mächte auf 2 reduziert, Linderung/Verwirrung via D-Advances nach "Neue Mächte".

---

## 7. VERBLEIBENDE PROBLEME (System-Level)

### Nicht fixbar durch SOLL-Korrekturen:

1. **AH neue_maechte mismatch**: Deadlands.json muss aktualisiert werden
2. **"Neue Mächte" fügt keine Slots hinzu**: System-Bug in talent_funktionen.py
3. **Talent prerequisites fail**: Unbekannte Ursache
4. **D-Advances failures**: Unknown cause

---

## 8. BUDGET-RECHNUNG BEISPIEL

### Metallmagier (korrigiert)

```
CharGen:
- 4 HP (Handicaps: Arrogant schwer, Nachtängste schwer)
- 2 HP (AH Verrückte Wissenschaft)
- 2 HP übrig → Geschicklichkeit/Verstand/Willenskraft/Stärke steigern

Fertigkeiten (12 Punkte):
- 12 Fertigkeiten auf W4-W8
- Okkultismus W6, Verrückte Wissenschaft W8, etc.

D-Advances (4 Aufstiege):
1. talent:Neue Mächte
2. talent:Metallmagier
3. fertigkeit:Verrückte Wissenschaft:8
4. fertigkeit:Wahrnehmung:6

Mächte (via AH + Neue Mächte):
- Ausfall, Schmuckstücke (via AH)
- Flächenschlag, Strahl (via D-Advances)
```

---

## 9. EMPFEHLUNGEN

### Kurzfristig (SOLL-Korrekturen):
- ✅ Alle machbaren SOLL-Korrekturen durchgeführt
- ✅ Metallmagier-Talent hinzugefügt
- ✅ MEDIZINFRAU Reihenfolge-Problem gelöst
- Keine weiteren SOLL-Korrekturen möglich

### Langfristig (Code-Änderungen):
1. **settings/Deadlands.json**: `neue_maechte` für AH-Talente korrigieren
2. **talent_funktionen.py**: "Neue Mächte" muss `verf_maechte` erhöhen
3. **charakter_controller.py**: D-Advance failures debuggen
4. **Driver/Tests**: Prerequisites für Gepeinigt, Heiliger Krieger, US-Marshal prüfen