# -*- coding: utf-8 -*-
"""
Finalisiert alle Archetypen mit char_gen_completed=false (meist Worlds-of-Ulisses-Importe,
gebaut via logs/ulisses/build_{swae,hexxen,aventurien}.py, die char_gen nie abschlossen +
Pathfinder Darla_A). Schließt char_gen ab und berechnet den Rang neu. Ändert KEINE
Attribute/Fertigkeiten/Talente — nur den Abschluss-Status + Rang.
"""
import sys, glob, json, os
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import update_rang

ziel = []
for fn in sorted(glob.glob('chars/Archetypen/Archetyp_*.json')):
    if not json.load(open(fn, encoding='utf-8')).get('char_gen_completed'):
        ziel.append(fn)

print(f"{len(ziel)} unfertige Archetypen werden finalisiert.\n")
for fn in ziel:
    raw = json.load(open(fn, encoding='utf-8'))
    setting = raw.get('active_setting_name') or '?'
    name = (raw.get('profil_daten') or {}).get('Name') or os.path.basename(fn)
    s = d.Sitzung(setting if setting != '?' else 'SWAE', name)
    if not s.controller.lade_charakter_von_json(fn):
        print(f"  {name:28} LADEN FEHLGESCHLAGEN"); continue
    ch = s.ch
    vor_rang = raw.get('rang')
    ch.char_gen_completed = True
    update_rang(ch)
    s.speichern(fn)
    print(f"  {setting:20} {name:28} rang {str(vor_rang):8} -> {ch.rang} (Aufstiege {ch.aufstiege_gesamt})")
print("\nFERTIG")
