# -*- coding: utf-8 -*-
"""
Schließt fehlende-Mächte-Lücken in Horror-Archetypen (Pendant zu fill_budget_gaps.py,
aber für MÄCHTE statt Traits — fill_budget hebt nur Attribute/Fertigkeiten an, und davon
hat Horror 0 Defizite).

Befund 2026-06-14: Mehrere Caster-Archetypen haben freie Macht-Slots (anzahl_maechte > belegt),
die Bogen-Mächte wurden beim Build aber nicht eingetragen (s.macht im Advance-Schritt schlug fehl).
Diese passen kostenfrei in vorhandene Slots. Reicht der Slot nicht, wird — strikt im Seasoned-Cap
(ausgegebene Aufstiege < 8) — ein 'Neue Mächte'-Aufstieg gekauft und erneut versucht.
Idempotent. Fügt NUR hinzu. Quelle der Soll-Mächte: Build-Diffs (maechte FEHLT) gegen den Bogen.
"""
import sys, glob, json
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

# Aus den Build-Diffs (logs/horror_all_trace.txt): Bogen-Mächte, die im JSON FEHLEN.
FEHLENDE_MAECHTE = {
    'Exorcist':                 ['Kriegersegen'],
    'Witch':                    ['Fluchwort', 'Geisterruf'],
    'Magician':                 ['Bannung'],
    'Mummy':                    ['Eigenschaft erhöhen/senken', 'Heilung', 'Schutz'],
    'Demonologist_(Monstrous)': ['Bannung', 'Flächenschlag', 'Aufheben', 'Kriegersegen'],
}
SEASONED_CAP = 8

def jsonpath(stub):
    fns = glob.glob(f'chars/Archetypen/Archetyp_Horror_{stub}*')
    return fns[0] if fns else None

def ausgegeben(ch):
    return round(ch.aufstiege_gesamt - ch.verbleibende_aufstiege, 2)

for stub, fehlt in FEHLENDE_MAECHTE.items():
    jp = jsonpath(stub)
    if not jp:
        print(f"{stub:26} KEINE DATEI"); continue
    s = d.Sitzung('Horror Kompendium', stub)
    if not s.controller.lade_charakter_von_json(jp):
        print(f"{stub:26} LADEN FEHLGESCHLAGEN"); continue
    ch = s.ch
    add, offen = [], []
    for macht in fehlt:
        if macht in ch.selected_maechte:
            continue
        # Slot frei? sonst Neue-Mächte-Aufstieg im Cap kaufen
        if len(ch.selected_maechte) >= (ch.anzahl_maechte or 0):
            if ausgegeben(ch) + 1.0 < SEASONED_CAP:
                if ch.verbleibende_aufstiege < 1.0:
                    increase_aufstiege(ch)
                s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True)
            if len(ch.selected_maechte) >= (ch.anzahl_maechte or 0):
                offen.append(f"{macht}(kein Slot, Cap)"); continue
        r = s.macht(macht, ignore_rang_check=True)
        if r.get('ok') and macht in ch.selected_maechte:
            add.append(macht)
        else:
            offen.append(f"{macht}(macht-fail)")
    if add:
        s.speichern(jp)
    print(f"{stub:26} slots={ch.anzahl_maechte} ist={len(ch.selected_maechte)} "
          f"aufstiege={ausgegeben(ch)}")
    if add:   print(f"    + ergänzt: {add}")
    if offen: print(f"    ~ offen:   {offen}")
print("HORROR-MAECHTE-FILL DONE")
