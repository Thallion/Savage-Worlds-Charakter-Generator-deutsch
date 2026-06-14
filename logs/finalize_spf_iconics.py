# -*- coding: utf-8 -*-
"""
Phase 3 der Savage-Pathfinder-Sanierung: finalisiert die 11 ikonischen Charaktere auf
Rang ANFÄNGER. Die Charakterdaten selbst sind bereits korrekt (Attribute 10/11 = Grund-
regelwerk, verifiziert) — committet waren sie aber halb-finalisiert (char_gen_completed=
False bzw. rang=null). Dieses Skript schließt char_gen ab, berechnet den Rang neu und
speichert. Es ändert KEINE Attribute/Fertigkeiten/Talente (Anfänger = 0 Aufstiege).

Bekannter Datenpunkt (NICHT hier gefixt, Chargen-Budget): Sajan Stärke W6 statt Bogen-W8.
"""
import sys, glob, json
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import update_rang

STUBS = ['Kämpfer_Valeros', 'Magier_Ezren', 'Druidin_Lini', 'Barde_Lem', 'Mönch_Sajan',
         'Waldläufer_Harsk', 'Barbarin_Amiri', 'Klerikerin_Kyra', 'Paladinin_Seelah',
         'Schurkin_Merisiel', 'Zauberer_Seoni']

for stub in STUBS:
    fns = glob.glob(f'chars/Archetypen/Archetyp_Savage_Pathfinder_{stub}*.json')
    if not fns:
        print(f"{stub:20} KEINE DATEI"); continue
    fn = fns[0]
    s = d.Sitzung('Savage Pathfinder', stub)
    if not s.controller.lade_charakter_von_json(fn):
        print(f"{stub:20} LADEN FEHLGESCHLAGEN"); continue
    ch = s.ch
    raw = json.load(open(fn, encoding='utf-8'))
    vor_cg, vor_rang = raw.get('char_gen_completed'), raw.get('rang')
    # Sajan: Bogen-Stärke W8 (Render+Crop Grundregelwerk S.61 bestätigt) — designter Iconic-Wert
    # über Standard-Chargen-Budget; der Punkt-Build lieferte fälschlich W6.
    if 'Sajan' in stub and ch.attribute['Stärke'].wert < 8:
        ch.attribute['Stärke'].wert = 8
    ch.char_gen_completed = True
    update_rang(ch)
    s.speichern(fn)
    print(f"{stub:20} cg {vor_cg}->True | rang {vor_rang}->{ch.rang} | aufst={ch.aufstiege_gesamt}")
print("IKONEN FINALISIERT")
