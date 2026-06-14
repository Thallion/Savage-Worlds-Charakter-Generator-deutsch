# -*- coding: utf-8 -*-
"""
Parst die 11 ikonischen Charaktere (Rang ANFÄNGER) aus dem deutschen
Texte/SWPF_Grundregelwerk.txt — sauber strukturiert, KEIN EN->DE-Mapping nötig.
Extrahiert Attribute, Fertigkeiten, Talente, Handicaps, Abstammung.

Ausgabe: Texte/SWPF_Ikonen_target.{json,txt}  (Soll für Phase 3 der PF-Sanierung)
"""
import re, json
from pathlib import Path

SRC = Path('Texte/SWPF_Grundregelwerk.txt')
OUT_JSON = Path('Texte/SWPF_Ikonen_target.json')
OUT_TXT = Path('Texte/SWPF_Ikonen_target.txt')

# Ikone -> committed JSON-Stub
STUB = {
 'VALEROS': 'Kämpfer_Valeros', 'EZREN': 'Magier_Ezren', 'LINI': 'Druidin_Lini',
 'LEM': 'Barde_Lem', 'SAJAN': 'Mönch_Sajan', 'HARSK': 'Waldläufer_Harsk',
 'AMIRI': 'Barbarin_Amiri', 'KYRA': 'Klerikerin_Kyra', 'SEELAH': 'Paladinin_Seelah',
 'MERISIEL': 'Schurkin_Merisiel', 'SEONI': 'Zauberer_Seoni',
}
SECT = {'attribute', 'abgeleitet', 'handicaps', 'talente', 'sprachen', 'abstammung',
        'fertigkeiten', 'ausrüstung', 'ausrustung'}

def norm_h(s):
    return re.sub(r'[^a-zäöü]', '', s.lower())

def parse():
    text = SRC.read_text(encoding='utf-8')
    lines = text.splitlines()
    heads = [(i, re.search(r'\b([A-ZÄÖÜ]+)\s*\(ANFÄNGER(?:IN)?, IKONISCHE?R?', ln))
             for i, ln in enumerate(lines)]
    heads = [(i, m.group(1)) for i, m in heads if m and m.group(1) in STUB]
    # dedup (Lini doppelt) -> letzter Block gewinnt (vollständiger)
    seen = {}
    for i, nm in heads:
        seen[nm] = i
    out = {}
    items = sorted(seen.items(), key=lambda x: x[1])
    allstarts = [i for _, i in items]
    for nm, start in items:
        nxt = min([s for s in allstarts if s > start] + [start + 60])
        block = lines[start:nxt]
        rec = {'attribute': {}, 'fertigkeiten': {}, 'talente': [], 'handicaps': [], 'abstammung': None}
        section = None
        buf = {}
        for ln in block:
            raw = ln.strip()
            if not raw:
                continue
            mhead = re.match(r'([A-Za-zÄÖÜäöü]+)\s*:?\s*(.*)', raw)
            key = norm_h(raw.split(':')[0]) if ':' in raw else norm_h(raw)
            if key in SECT:
                section = key
                rest = raw.split(':', 1)[1].strip() if ':' in raw else ''
                buf.setdefault(section, [])
                if rest:
                    buf[section].append(rest)
                continue
            if section in ('attribute',):
                mm = re.match(r'([A-Za-zäöü]+)\s+W(\d+)', raw)
                if mm: rec['attribute'][mm.group(1)] = int(mm.group(2))
                else: section = None
            elif section in ('handicaps', 'talente', 'fertigkeiten', 'abstammung'):
                # Fortsetzungszeilen anhängen, bis neue Section
                if norm_h(raw.split(':')[0]) in SECT:
                    section = None
                else:
                    buf[section].append(raw)
        # Auswerten
        def joined(sec):
            s = ' '.join(buf.get(sec, [])).strip()
            return re.sub(r'-\s+', '', s)  # Soft-Hyphen am Zeilenende zusammenführen
        for fn, fv in re.findall(r'([A-Za-zäöüÄÖÜ ]+?)\s+W(\d+)', joined('fertigkeiten')):
            rec['fertigkeiten'][fn.strip().lstrip(', ').strip()] = int(fv)
        rec['talente'] = [t.strip() for t in re.split(r',', joined('talente')) if t.strip()]
        rec['handicaps'] = [h.strip() for h in re.split(r',', joined('handicaps')) if h.strip()]
        rec['abstammung'] = joined('abstammung') or None
        rec['stub'] = STUB[nm]
        out[nm] = rec
    return out

def main():
    spec = parse()
    OUT_JSON.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding='utf-8')
    L = ["# SWPF Ikonen (ANFÄNGER) — Soll aus Grundregelwerk (deutsch)\n"]
    for nm in sorted(spec):
        r = spec[nm]
        L.append(f"\n=== {nm} -> {r['stub']} ===")
        L.append("  ATTR : " + ", ".join(f"{k} W{v}" for k, v in r['attribute'].items()))
        L.append("  SKILL: " + ", ".join(f"{k} W{v}" for k, v in r['fertigkeiten'].items()))
        L.append(f"  TAL  : {r['talente']}")
        L.append(f"  HAND : {r['handicaps']}")
        L.append(f"  ABST : {r['abstammung']}")
    OUT_TXT.write_text("\n".join(L), encoding='utf-8')
    print(f"OK: {len(spec)} Ikonen.\n  {OUT_JSON}\n  {OUT_TXT}")

if __name__ == '__main__':
    main()
