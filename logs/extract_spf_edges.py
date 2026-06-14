# -*- coding: utf-8 -*-
"""
Extrahiert aus den SPF Archetype Cards (Set 2/3) die RECHTE Spalte:
HINDRANCES / EDGES / POWERS je Archetyp und Rang (Novice/Seasoned) + die
Novice->Seasoned-DELTAS (was bei Seasoned hinzukommt). Roh-EN-Namen; das
EN->DE-Mapping macht der Resolver (logs/resolve_spf_edges.py).

Spalten-Trennung: pro Zeile das Segment ab Spalte >=58 (rechte Karten-Spalte).
Ausgabe: Texte/SWPF_Archetype_Cards_edges.json (+ _edges.txt lesbar).
"""
import re, json
from pathlib import Path

SRC = [Path('logs/pdf_extracted/Pathfinder®_for_Savage_Worlds_Archetype_Cards_Set_2.txt'),
       Path('logs/pdf_extracted/Pathfinder®_for_Savage_Worlds_Archetype_Cards_Set_3.txt')]
OUT_JSON = Path('Texte/SWPF_Archetype_Cards_edges.json')
OUT_TXT = Path('Texte/SWPF_Archetype_Cards_edges.txt')

NAME_MAP = {
 'KIRA': 'Kira', 'TELLER': 'Teller', 'BROKAR': 'Brokar', 'ZYRIL': 'Zyril', 'KORVA': 'Korva',
 'PAELIE': 'Paelie', 'FARIEL': 'Fariel', 'MARN': 'Marn', 'GNORR': 'Gnorr', 'MADDA': 'Madda',
 'SIL': 'Sil', 'DAMIEL': 'Damiel', 'ALAIN': 'Alain', 'IMRIJKA': 'Imrijka', 'ALAHAZRA': 'Alahazra',
 'BALAZAR': 'Balazar', 'FEIYA': 'Feiya', 'DARLA': 'Darla_ohneKlasse', 'PADRIG': 'Padrig',
}
SECTIONS = ('ANCESTRY', 'HINDRANCES', 'EDGES', 'CLASS FEATURES', 'GEAR', 'POWERS')

def right_col(line):
    for m in re.finditer(r'\S.*?(?=\s{3,}|$)', line):
        if m.start() >= 58:
            return line[m.start():].strip()
    return ''

def parse_block_right(block):
    rc = [right_col(ln) for ln in block]
    rc = [x for x in rc if x]
    out = {'hindrances': [], 'edges': [], 'powers': []}
    section = None
    # Rechte Spalte ist vertikal versetzt: erst AB dem rechtsspaltigen "RANK:" erfassen
    # (davor = Spillover der Vorkarte), bis zum nächsten "RANK:".
    started = False
    for ln in rc:
        up = ln.upper().rstrip()
        if up.startswith('RANK:'):
            if started:
                break          # nächste Karte beginnt
            started = True; section = None; continue
        if not started:
            continue
        if up in SECTIONS:
            section = up; continue
        if section == 'HINDRANCES':
            mm = re.match(r"([A-Za-z][A-Za-z '()/-]{1,33}?)\s*\((major|minor)\)\s*:", ln, re.I)
            if mm: out['hindrances'].append((mm.group(1).strip(), mm.group(2).lower()))
        elif section == 'EDGES':
            mm = re.match(r"([A-Za-z][A-Za-z '()/-]{1,33}?):", ln)
            if mm and len(mm.group(1).split()) <= 5:
                out['edges'].append(mm.group(1).strip())
        elif section == 'POWERS':
            mm = re.match(r'power[sS]?\s*:\s*(.+)', ln, re.I)
            if mm:
                for p in re.split(r',', mm.group(1)):
                    p = re.sub(r'\(.*?\)', '', p).strip()
                    if p and not p.lower().startswith('power'):
                        out['powers'].append(p)
    return out

def parse_file(text):
    lines = text.splitlines()
    rank_idx = [(i, ('Seasoned' if 'SEASONED' in ln.upper() else 'Novice'))
                for i, ln in enumerate(lines) if re.search(r'RANK:\s*(NOVICE|SEASONED)', ln, re.I)]
    cards = []
    for k, (ri, rank) in enumerate(rank_idx):
        end = rank_idx[k + 1][0] if k + 1 < len(rank_idx) else len(lines)
        block = lines[ri:end]
        name = None
        for ln in block:
            mm = re.search(r'\b([A-Z][A-Z\']{2,})\s*\(([A-Z][A-Za-z ]+)\)', ln)
            if mm: name = mm.group(1); break
        if not name: continue
        r = parse_block_right(block)
        r['name'] = name; r['rank'] = rank; r['stub'] = NAME_MAP.get(name)
        cards.append(r)
    return cards

def main():
    allc = []
    for src in SRC:
        allc += parse_file(src.read_text(encoding='utf-8'))
    spec = {}
    for c in allc:
        spec.setdefault(c['stub'] or c['name'], {})[c['rank']] = c
    # Deltas Novice->Seasoned
    for stub, ranks in spec.items():
        nov, sea = ranks.get('Novice'), ranks.get('Seasoned')
        if nov and sea:
            ne = [e for e in sea['edges'] if e.lower() not in {x.lower() for x in nov['edges']}]
            np_ = [p for p in sea['powers'] if p.lower() not in {x.lower() for x in nov['powers']}]
            ranks['delta'] = {'edges': ne, 'powers': np_}
    OUT_JSON.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding='utf-8')
    L = ["# SPF Archetype Cards — Edges/Hindrances/Powers (roh EN) + Novice->Seasoned-Delta\n"]
    for stub in sorted(spec):
        L.append(f"\n=== {stub} ===")
        for rank in ('Novice', 'Seasoned'):
            c = spec[stub].get(rank)
            if not c: continue
            L.append(f"  [{rank}] EDGES: {c['edges']}")
            L.append(f"         HIND : {c['hindrances']}")
            if c['powers']: L.append(f"         POW  : {c['powers']}")
        if 'delta' in spec[stub]:
            L.append(f"  >> DELTA(Seasoned neu): edges={spec[stub]['delta']['edges']} powers={spec[stub]['delta']['powers']}")
    OUT_TXT.write_text("\n".join(L), encoding='utf-8')
    print(f"OK: {len(allc)} Karten, {len(spec)} Archetypen.\n  {OUT_JSON}\n  {OUT_TXT}")

if __name__ == '__main__':
    main()
