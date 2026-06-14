# -*- coding: utf-8 -*-
"""Vergleicht die gebauten Deadlands-Archetyp-JSONs gegen den PDF-Bogen
US85040PDF_Deadlands_Archetypen-Set_meta.txt (Attribute, Fertigkeiten, Talente)."""
import json, re
from pathlib import Path

PDF = Path('Texte/US85040PDF_Deadlands_Archetypen-Set_meta.txt').read_text(encoding='utf-8')

def parse_pdf():
    """Zerlege PDF in Archetyp-Blöcke {NAME: {attr, fert, talente, handicaps}}."""
    blocks = {}
    # Blöcke durch ===-Header getrennt: <sep>\nNAME\n<sep>
    parts = re.split(r'={35,}\n', PDF)
    # parts: [intro, NAME1\n, body1, NAME2\n, body2, ...]
    i = 1
    while i < len(parts) - 1:
        name = parts[i].strip().splitlines()[0].strip()
        body = parts[i + 1]
        blocks[name] = parse_block(body)
        i += 2
    return blocks

def parse_block(body):
    res = {'attr': {}, 'fert': {}, 'talente': [], 'handicaps': []}
    section = None
    for line in body.splitlines():
        s = line.strip()
        if s in ('ATTRIBUTE', 'FERTIGKEITEN', 'HANDICAPS', 'TALENTE', 'AUSRÜSTUNG'):
            section = s; continue
        if s.startswith('AUFSTIEGE'):
            section = None; continue
        if not s:
            continue
        if section == 'ATTRIBUTE':
            mm = re.match(r'(.+?)\s+W(\d+)', s)
            if mm: res['attr'][mm.group(1).strip()] = int(mm.group(2))
        elif section == 'FERTIGKEITEN':
            mm = re.match(r'(.+?)\s+W(\d+)', s)
            if mm: res['fert'][mm.group(1).strip()] = int(mm.group(2))
        elif section == 'TALENTE':
            mm = re.match(r'([^:]+):', s)
            if mm and not line.startswith('    '):  # Talent-Zeilen sind 2-space, Fließtext 4-space
                res['talente'].append(mm.group(1).strip())
        elif section == 'HANDICAPS':
            mm = re.match(r'(.+?)\s*\((Schwer|Leicht)\)', s)
            if mm: res['handicaps'].append((mm.group(1).strip(), mm.group(2)))
    return res

def eff_die(value, modifier):
    return value + modifier

def load_json(name):
    p = Path(f'chars/Archetypen/Archetyp_Deadlands_{name}_A.json')
    if not p.exists(): return None
    return json.loads(p.read_text(encoding='utf-8'))

# JSON-Archetypnamen (exakt) → PDF-Header ist UPPER davon (Umlaute bleiben)
JSON_NAMES = [p.stem.replace('Archetyp_Deadlands_', '').replace('_A', '')
              for p in sorted(Path('chars/Archetypen').glob('Archetyp_Deadlands_*.json'))]

pdf = parse_pdf()
pdf_upper = {k.upper(): v for k, v in pdf.items()}
# Namen sind an die Bogen-Schreibweise angeglichen (Saloonschönheit). Keine Sonderfälle mehr.
NAME_MAP = {}
# PDF-"TALENTE"-Einträge, die in Wahrheit AH-Paketmechanik sind (keine wählbaren Edges):
AH_PAKET = {'Mächte', 'Machtpunkte', 'Rückschlag', 'Sündigen'}

def talent_vorhanden(t, jt):
    # AH-Abkürzung: "Arkaner Hintergrund (X)" ↔ "AH (X)"
    kandidaten = [t]
    mm = re.match(r'Arkaner Hintergrund \((.+)\)', t)
    if mm: kandidaten.append(f'AH ({mm.group(1)})')
    for k in kandidaten:
        if k in jt or any(k in x or x in k for x in jt):
            return True
    return False

def fert_normalisiert(fn, d):
    # "Sprache (Englisch)" → "Sprache"; "Gewerbe (X)" → irgendein "Gewerbe (...)"
    if fn.startswith('Sprache'):
        f = d['fertigkeiten'].get('Sprache'); return ('Sprache', f)
    if fn.startswith('Gewerbe'):
        for k, v in d['fertigkeiten'].items():
            if k.startswith('Gewerbe'): return (k, v)
        return (fn, None)
    return (fn, d['fertigkeiten'].get(fn))

out = []
gesamt_diffs = 0
for name in JSON_NAMES:
    d = load_json(name)
    pb = pdf_upper.get(NAME_MAP.get(name.upper(), name.upper()))
    if pb is None:
        out.append(f"### {name}\n  ⚠ KEIN PDF-Block gefunden (Header-Mismatch)\n"); continue
    diffs = []
    # Attribute
    for an, soll in pb['attr'].items():
        ist = d['attribute'].get(an)
        if ist is None:
            diffs.append(f"ATTR {an}: PDF W{soll}, JSON FEHLT"); continue
        e = eff_die(ist['wert'], ist['modifier'])
        if e != soll: diffs.append(f"ATTR {an}: PDF W{soll} ≠ JSON W{e}")
    # Fertigkeiten
    for fn, soll in pb['fert'].items():
        key, ist = fert_normalisiert(fn, d)
        if ist is None:
            diffs.append(f"FERT {fn}: PDF W{soll}, JSON FEHLT (Key '{key}')"); continue
        w = ist['wuerfel']
        if not ist.get('aktiv'):
            diffs.append(f"FERT {fn}: PDF W{soll}, JSON INAKTIV"); continue
        e = eff_die(w['value'], w['modifier'])
        if e != soll: diffs.append(f"FERT {fn} ({key}): PDF W{soll} ≠ JSON W{e}")
    # Talente (AH-Paketmechanik überspringen; AH-Abkürzung normalisieren)
    jt = set(d.get('selected_talente', []))
    for t in pb['talente']:
        if t in AH_PAKET: continue
        if not talent_vorhanden(t, jt):
            diffs.append(f"TALENT fehlt im JSON: '{t}'")
    if diffs:
        gesamt_diffs += len(diffs)
        out.append(f"### {name}  ({len(diffs)} Diffs)\n" + '\n'.join('  - ' + x for x in diffs) + '\n')
    else:
        out.append(f"### {name}  ✅ Attribute+Fertigkeiten+Talente deckungsgleich\n")

print('\n'.join(out))
print(f"\n=== GESAMT: {gesamt_diffs} Diffs über {len(JSON_NAMES)} Archetypen ===")
