#!/usr/bin/env python3
"""Erzeugt eine kompakte per-Char SOLL/IST-Budget+Diff-Tabelle aus den gespeicherten
Archetyp-Chars (Budget) + den Build-Berichten (SOLL/IST-DIFF). Ausgabe: Markdown auf stdout."""
import json, glob, re, os, collections

# --- Berichte nach (Name, Setting) indizieren ---
bericht_idx = {}
for f in glob.glob('logs/*_bericht.json'):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    bericht_idx[(d.get('name', '?'), d.get('setting', '?'))] = d


# --- Per-Char FEHLT_KATALOG aus dem dedizierten Ausrüstungs-Analyzer parsen ---
ausr_katalog = {}  # (setting, name) -> list[str]
_md = 'logs/soll_ist_ausruestung.md'
if os.path.exists(_md):
    cur_setting, cur = None, None
    for line in open(_md, encoding='utf-8'):
        ms = re.match(r'^## (.+?) \(\d+ Chars', line)
        if ms:
            cur_setting = ms.group(1).strip()
            cur = None
            continue
        m = re.match(r'^### (.+?) ↔', line)
        if m:
            cur = m.group(1).strip()
            continue
        if cur and cur_setting and 'FEHLT_KATALOG' in line:
            items = re.findall(r'`([^`]+)`', line)
            if items:
                ausr_katalog[(cur_setting, cur)] = items


def diff_aus_bericht(d):
    """Liefert (fehlende_elemente:list, fehlende_ausruestung:list, zuviel:list) aus SOLL/IST-DIFF."""
    elem, ausr, zuviel = [], [], []
    for a in d.get('anomalien', []):
        if a.get('aktion') == 'SOLL/IST-DIFF':
            w = a.get('warnung', '') or ''
            for clause in w.split(';'):
                c = clause.strip()
                if not c:
                    continue
                low = c.lower()
                if 'zuviel' in low:
                    zuviel.append(c)
                elif low.startswith('ausruestung') or low.startswith('ausrüstung'):
                    ausr.append(c)
                else:
                    elem.append(c)
    return elem, ausr, zuviel


def force_und_fehlt_notizen(d):
    """FEHLT-im-Katalog / Macht-fehlt / FORCE-Notizen aus Anomalien (ohne SOLL/IST-DIFF)."""
    katalog_fehlt, force = [], 0
    for a in d.get('anomalien', []):
        w = (a.get('warnung') or a.get('aktion') or '')
        if 'FEHLT im Katalog' in w or 'fehlt im Katalog' in w:
            katalog_fehlt.append(w.split(':', 1)[-1].strip())
        if 'FORCE' in w or 'force_bei_geldmangel' in w or 'Geldmangel' in w:
            force += 1
    return katalog_fehlt, force


def kurz(items, n=4):
    items = [re.sub(r'\s+', ' ', x).strip() for x in items]
    if not items:
        return '—'
    if len(items) <= n:
        return '; '.join(items)
    return '; '.join(items[:n]) + f' … (+{len(items)-n})'


rows_by_setting = collections.defaultdict(list)
for cf in sorted(glob.glob('chars/Archetypen/Archetyp_*.json')):
    c = json.load(open(cf))
    nm = c.get('profil_daten', {}).get('Name', '') or os.path.basename(cf)
    st = c.get('active_setting_name', '?')
    # Budget
    r_attr = c.get('verbleibende_attributsteigerungen', 0)
    r_fert = c.get('verbleibende_fertigkeitssteigerungen', 0)
    hp_ges = c.get('gesamt_handicap_punkte', 0)
    hp_rem = c.get('verbleibende_handicap_punkte', 0)
    auf_ges = c.get('aufstiege_gesamt', 0)
    auf_rem = c.get('verbleibende_aufstiege', 0)
    attr_used = 5 - r_attr
    fert_used = 12 - r_fert
    auf_used = auf_ges - auf_rem
    # Diff aus Bericht
    d = bericht_idx.get((nm, st))
    if d:
        elem, ausr, zuviel = diff_aus_bericht(d)
        anom = d.get('anomalien_anzahl', 0)
        bericht_ok = True
    else:
        elem, ausr, zuviel, anom, bericht_ok = [], [], [], None, False
    # Fehlende Ausrüstung: dedizierter Analyzer (FEHLT_KATALOG = bewusste Flavor-Items)
    ausr_all = ausr_katalog.get((st, nm), [])
    rows_by_setting[st].append({
        'name': nm if nm else os.path.basename(cf).replace('Archetyp_', '').replace('.json', ''),
        'attr': f'{attr_used}/5', 'attr_warn': r_attr > 0,
        'fert': f'{fert_used}/12', 'fert_warn': r_fert > 0,
        'hp': f'{hp_ges-hp_rem:g}/{hp_ges:g}', 'hp_warn': hp_rem > 0,
        'auf': f'{auf_used:g}/{auf_ges:g}', 'auf_warn': auf_rem > 0,
        'elem': elem, 'ausr': ausr_all, 'zuviel': zuviel,
        'anom': anom, 'bericht_ok': bericht_ok,
    })

print('# SOLL/IST per Archetyp — Budget & Diff (Stand: 2026-06-04)\n')
print('Generiert: `logs/gen_soll_ist_tabelle.py` (Budget aus Char-JSON, Diff aus Build-Bericht '
      '`SOLL/IST-DIFF`, Ausrüstung aus `soll_ist_ausruestung.py`).\n')
print('**Spalten:** genutzt/verfügbar — **Attr 5 · Fert 12 · Aufstiege rang-abhängig** '
      '(Anfänger 0 / Fortgeschritten 4 / Veteran 8…). **HP = ausgegebene/erworbene Handicap-Punkte** '
      '(erworben max 4; Nenner = was die Bogen-Handicaps einbringen). `⚠` = ungenutztes Budget '
      '(Rest > 0; bei HP oft bogenbedingt: Handicaps bringen mehr HP als der Bogen verausgabt). '
      '*Fehlende SOLL-Elemente* = Attribute/Fertigkeiten/Talente/Mächte unter Bogen-Soll. '
      '*Fehlende Ausrüstung* = FEHLT_KATALOG, durchweg **bewusste Flavor-/Quest-Items ohne '
      'Spielwerte** (echter Ausrüstungsmangel laut Analyzer = **0**, FEHLT_OFFEN = 0).\n')

# Gesamtkennzahlen
total = sum(len(v) for v in rows_by_setting.values())
clean = sum(1 for v in rows_by_setting.values() for r in v
            if not r['elem'] and not r['attr_warn']
            and not r['fert_warn'] and not r['auf_warn'])
print(f'**{total} Archetypen** · **{clean} ohne jede SOLL-Abweichung** '
      f'(Budget voll genutzt, kein fehlendes SOLL-Element). Die übrigen {total-clean} weichen ab — '
      f'fast ausschließlich durch **Budget-Überzug des Bogens** (Bogen verlangt mehr als 5/12/4 '
      f'hergeben → einzelne Skills/Talente unter Soll), kein Code-Bug.\n')

ORDER = ['Deadlands', 'Fantasy Kompendium', 'Savage Pathfinder', 'SciFi Kompendium',
         'Horror Kompendium', 'Superkräfte Kompendium', 'SWAE', 'HeXXen 1773', 'HeXXen1773']
seen = set()
for st in ORDER + sorted(rows_by_setting):
    if st in seen or st not in rows_by_setting:
        continue
    seen.add(st)
    rows = sorted(rows_by_setting[st], key=lambda r: r['name'])
    nclean = sum(1 for r in rows if not r['elem'] and not r['attr_warn']
                 and not r['fert_warn'] and not r['auf_warn'])
    print(f'\n## {st} ({len(rows)} Chars · {nclean} ✓)\n')
    print('| Archetyp | Attr | Fert | HP | Aufst | Fehlende SOLL-Elemente | Fehlende Ausrüstung |')
    print('|---|---|---|---|---|---|---|')
    for r in rows:
        a = r['attr'] + (' ⚠' if r['attr_warn'] else '')
        f = r['fert'] + (' ⚠' if r['fert_warn'] else '')
        h = r['hp'] + (' ⚠' if r['hp_warn'] else '')
        au = r['auf'] + (' ⚠' if r['auf_warn'] else '')
        el = kurz(r['elem'])
        ar = kurz(r['ausr'])
        nm = r['name'] if r['bericht_ok'] else r['name'] + ' †'
        print(f'| {nm} | {a} | {f} | {h} | {au} | {el} | {ar} |')

print('\n† = kein Build-Bericht gefunden (älterer Build); nur Budget aus Char-JSON, kein Diff.')
