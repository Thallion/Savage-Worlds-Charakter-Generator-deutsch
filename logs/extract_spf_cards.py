# -*- coding: utf-8 -*-
"""
Parst die Savage-Pathfinder Archetype Cards (Set 2 + Set 3, ENGLISCH) in eine
strukturierte Target-Spec (Novice + Seasoned je Archetyp): Attribute + Fertigkeiten
mit EN->DE-Mapping. Grundlage für die Set-2/3-Sanierung (Build auf Seasoned).

Layout: pdftotext mischt zwei Spalten zeilenweise; Attribute/Fertigkeiten stehen in der
linken Spalte als '<Name> dX' (small-caps -> Lowercase-Match). Rechte Spalte (Edges/Gear)
matcht das Muster nicht und wird ignoriert. Pace/Parry/Toughness werden übersprungen.

Ausgabe: Texte/SWPF_Archetype_Cards_target.json  (+ lesbare _target.txt)
"""
import re, json
from pathlib import Path

SRC = [Path('logs/pdf_extracted/Pathfinder®_for_Savage_Worlds_Archetype_Cards_Set_2.txt'),
       Path('logs/pdf_extracted/Pathfinder®_for_Savage_Worlds_Archetype_Cards_Set_3.txt')]
OUT_JSON = Path('Texte/SWPF_Archetype_Cards_target.json')
OUT_TXT = Path('Texte/SWPF_Archetype_Cards_target.txt')

ATTR = {'agility': 'Geschicklichkeit', 'smarts': 'Verstand', 'spirit': 'Willenskraft',
        'strength': 'Stärke', 'vigor': 'Konstitution'}
SKILL = {
 'academics': 'Geisteswissenschaften', 'athletics': 'Athletik', 'battle': 'Kriegskunst',
 'boating': 'Seefahrt', 'com. knowledge': 'Allgemeinwissen', 'common knowledge': 'Allgemeinwissen',
 'driving': 'Fahren', 'electronics': 'Elektronik', 'faith': 'Glaube', 'fighting': 'Kämpfen',
 'focus': 'Fokus', 'gambling': 'Glücksspiel', 'healing': 'Heilen', 'intimidation': 'Einschüchtern',
 'languages': 'Sprache', 'language': 'Sprache', 'notice': 'Wahrnehmung', 'occult': 'Okkultismus',
 'performance': 'Darbietung', 'persuasion': 'Überreden', 'piloting': 'Pilot', 'psionics': 'Psionik',
 'repair': 'Reparieren', 'research': 'Recherche', 'riding': 'Reiten', 'science': 'Naturwissenschaften',
 'shooting': 'Schießen', 'spellcasting': 'Zaubern', 'stealth': 'Heimlichkeit', 'survival': 'Überleben',
 'taunt': 'Provozieren', 'thievery': 'Diebeskunst', 'alchemy': 'Alchemie',
}
DERIVED = ('pace', 'parry', 'toughness')

# Karten-Name (EN, GROSS) -> committed JSON-Stub (DE). Set 2/3.
NAME_MAP = {
 'KIRA': 'Kira', 'TELLER': 'Teller', 'BROKAR': 'Brokar', 'ZYRIL': 'Zyril', 'KORVA': 'Korva',
 'PAELIE': 'Paelie', 'FARIEL': 'Fariel', 'MARN': 'Marn', 'GNORR': 'Gnorr', 'MADDA': 'Madda',
 'SIL': 'Sil', 'DAMIEL': 'Damiel', 'ALAIN': 'Alain', 'IMRIJKA': 'Imrijka', 'ALAHAZRA': 'Alahazra',
 'BALAZAR': 'Balazar', 'FEIYA': 'Feiya', 'PADRIG': 'Padrig', 'DARLA': 'Darla_ohneKlasse',
}

def parse_card_text(text):
    lines = text.splitlines()
    # Indizes der RANK-Zeilen
    rank_idx = [(i, ('Seasoned' if 'SEASONED' in ln.upper() else 'Novice'))
                for i, ln in enumerate(lines) if re.search(r'RANK:\s*(NOVICE|SEASONED)', ln, re.I)]
    cards = []
    for k, (ri, rank) in enumerate(rank_idx):
        end = rank_idx[k + 1][0] if k + 1 < len(rank_idx) else len(lines)
        block = lines[ri:end]
        # Name: erste 'NAME (CLASS)'-Zeile
        name = cls = None
        for ln in block:
            mm = re.search(r'\b([A-Z][A-Z\']{2,})\s*\(([A-Z][A-Za-z ]+)\)', ln)
            if mm:
                name, cls = mm.group(1), mm.group(2).strip(); break
        attrs, skills = {}, {}
        for ln in block:
            for mm in re.finditer(r'([A-Za-z][A-Za-z.\' ]+?)\s+d(\d+)\b', ln):
                raw = mm.group(1).strip().lower()
                val = int(mm.group(2))
                if raw in ATTR: attrs[ATTR[raw]] = val
                elif raw in SKILL: skills[SKILL[raw]] = val
                # sonst: Edge/Gear-Rauschen, ignorieren
        if name and attrs:
            cards.append({'name': name, 'class': cls, 'rank': rank,
                          'stub': NAME_MAP.get(name), 'attribute': attrs, 'fertigkeiten': skills})
    return cards

def main():
    all_cards = []
    for src in SRC:
        all_cards += parse_card_text(src.read_text(encoding='utf-8'))
    # nach Stub gruppieren: {stub: {Novice:{...}, Seasoned:{...}}}
    spec = {}
    for c in all_cards:
        spec.setdefault(c['stub'] or c['name'], {})[c['rank']] = c
    OUT_JSON.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding='utf-8')
    # lesbare Fassung
    L = ["# Savage Pathfinder Archetype Cards — Target-Spec (Set 2+3, EN->DE)\n"
         "# Quelle: logs/pdf_extracted/...Set_2/3.txt  | erzeugt: logs/extract_spf_cards.py\n"]
    for stub in sorted(spec):
        L.append(f"\n=== {stub} ===")
        for rank in ('Novice', 'Seasoned'):
            c = spec[stub].get(rank)
            if not c: continue
            L.append(f"  [{rank}] {c['name']} ({c['class']})")
            L.append("    ATTR : " + ", ".join(f"{k} W{v}" for k, v in c['attribute'].items()))
            L.append("    SKILL: " + ", ".join(f"{k} W{v}" for k, v in c['fertigkeiten'].items()))
    OUT_TXT.write_text("\n".join(L), encoding='utf-8')
    named = sum(1 for s in spec if s)
    pairs = sum(1 for s in spec if 'Novice' in spec[s] and 'Seasoned' in spec[s])
    print(f"OK: {len(all_cards)} Karten, {named} Archetypen, {pairs} mit Novice+Seasoned-Paar.")
    print(f"  {OUT_JSON}\n  {OUT_TXT}")

if __name__ == '__main__':
    main()
