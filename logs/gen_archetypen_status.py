# -*- coding: utf-8 -*-
"""
Erzeugt den aktuellen Archetypen-Status-Bericht (-> logs/archetypen_anomalie_bericht.md):
pro Archetyp Setting, Name, alle Punktepools (ausgegeben/Maximum), Aufstiege/Rang und
fehlende Ausrüstung.

Datenquellen:
- chars/Archetypen/Archetyp_*.json  -> AKTUELLE Wahrheit (ALLE Pools aus dem Endzustand):
  Setting, Name, Attribut-/Fertigkeitspunkte-Rest (verbleibende_*steigerungen), Handicap-Punkte,
  Aufstiege, Rang, SKP (Superkräfte), Mächte-Slots, char_gen_completed.
- logs/soll_ist_ausruestung.md      -> fehlende Ausrüstung (FEHLT_KATALOG/FEHLT_OFFEN).
"""
import json, glob, os, re, collections

def norm(s):
    return re.sub(r'[^a-z0-9äöü]', '', (s or '').lower())

# --- Ausrüstungs-Analyzer: (setting_norm, name_norm) -> [fehlende Items] ---
fehlt = {}
cur_set = None
if os.path.exists('logs/soll_ist_ausruestung.md'):
    for line in open('logs/soll_ist_ausruestung.md', encoding='utf-8'):
        ms = re.match(r'^## (.+?) \(', line)
        if ms:
            cur_set = ms.group(1).strip(); continue
        mn = re.match(r'^### (.+?) ↔', line)
        if mn:
            cur_name = mn.group(1).strip()
            continue
        if cur_set and ('FEHLT_KATALOG' in line or 'FEHLT_OFFEN' in line):
            items = re.findall(r'`([^`]+)`', line)
            if items:
                fehlt.setdefault((norm(cur_set), norm(cur_name)), []).extend(items)

# --- Setting-Stub aus Dateiname (Fallback fürs Setting), grob ---
def setting_aus_datei(fn):
    base = os.path.basename(fn).replace('Archetyp_', '').replace('.json', '')
    for s in ['Fantasy_Kompendium', 'SciFi_Kompendium', 'Horror', 'Savage_Pathfinder',
              'Deadlands', 'Superkraefte', 'SWAE', 'HeXXen_1773', 'Savage_Aventurien',
              '50_Fathoms', 'Rippers', 'Myst']:
        if base.startswith(s):
            return s.replace('_', ' ')
    return base.split('_')[0]

def stufe(rest, voll):
    return f"{voll - rest:g}/{voll:g}"

rows = collections.defaultdict(list)
for fn in sorted(glob.glob('chars/Archetypen/Archetyp_*.json')):
    d = json.load(open(fn, encoding='utf-8'))
    setting = d.get('active_setting_name') or setting_aus_datei(fn)
    name = (d.get('profil_daten') or {}).get('Name') or os.path.basename(fn)
    key = (norm(setting), norm(name))
    # Attr/Fert aus dem ENDZUSTAND des Char-JSON (Rest-Chargen-Pools), Standard 5/12.
    # Spiegelt damit auch von fill_budget Phase 0 nachträglich verbrauchte Restpunkte korrekt.
    attr_rest = min(d.get('verbleibende_attributsteigerungen', 0) or 0, 5)
    fert_rest = min(d.get('verbleibende_fertigkeitssteigerungen', 0) or 0, 12)
    attr = stufe(attr_rest, 5)
    fert = stufe(fert_rest, 12)
    # Handicap-Punkte aus JSON
    hp_max = d.get('gesamt_handicap_punkte', 0) or 0
    hp_rest = d.get('verbleibende_handicap_punkte', 0) or 0
    hp = stufe(hp_rest, hp_max) if hp_max else '0/0'
    # Aufstiege/Rang aus JSON
    au_max = d.get('aufstiege_gesamt', 0) or 0
    au_rest = d.get('verbleibende_aufstiege', 0) or 0
    au = stufe(au_rest, au_max) if au_max else '0/0'
    rang = d.get('rang') or '—'
    cg = d.get('char_gen_completed')
    # SKP (Superkräfte)
    skp_g = d.get('superkraft_punkte_gesamt', 0) or 0
    skp_v = d.get('superkraft_punkte_verbraucht', 0) or 0
    skp = f"{skp_v}/{skp_g}" if skp_g else None
    # Mächte-Slots: gewählt / (gewählt + verfügbar). verfuegbare_maechte = noch offene Slots.
    m_sel = len(d.get('selected_maechte') or [])
    m_verf = d.get('verfuegbare_maechte', 0) or 0
    maechte = f"{m_sel}/{m_sel + m_verf}" if (m_sel or m_verf) else None
    miss = fehlt.get(key, [])
    rows[setting].append({
        'name': name, 'attr': attr, 'fert': fert, 'hp': hp, 'au': au, 'rang': rang,
        'cg': cg, 'skp': skp, 'maechte': maechte, 'miss': miss,
    })

# --- Markdown ---
def flag(s, voll_str):
    # ⚠ wenn ausgegeben < max
    a, b = s.split('/')
    try:
        return s + (' ⚠' if float(a) < float(b) else '')
    except ValueError:
        return s

L = ["# Archetypen-Status-Bericht\n"]
import datetime
L.append(f"**Stand:** {datetime.date.today().isoformat()} · automatisch erzeugt von "
         f"`logs/gen_archetypen_status.py`.\n")
L.append("Pro Archetyp: **Setting, Name, alle Punktepools (ausgegeben/Maximum), Aufstiege/Rang, "
         "fehlende Ausrüstung.**\n")
L.append("**Pools:** Attr (Chargen 5) · Fert (Chargen 12) · HP = Handicap-Punkte (ausgegeben/erworben, "
         "Max 4) · Mächte = gewählte/verfügbare Macht-Slots (Arkaner Hintergrund) · "
         "Aufst = Aufstiege (ausgegeben/gesamt, rangabhängig) · SKP nur Superkräfte. "
         "`⚠` = Pool nicht voll ausgegeben. `(unfertig)` = `char_gen_completed=false`.\n")
L.append("Alle Pools (Attr/Fert/HP/Aufstiege/Rang/SKP/Mächte) aus dem ENDZUSTAND der aktuellen "
         "Char-JSONs; fehlende Ausrüstung aus `logs/soll_ist_ausruestung.md` "
         "(FEHLT_KATALOG = bewusste Flavor-/Quest-Items ohne Spielwerte).\n")

gesamt = sum(len(v) for v in rows.values())
unfertig = sum(1 for v in rows.values() for r in v if r['cg'] is False)
L.append(f"\n**Bestand:** {gesamt} Archetypen über {len(rows)} Settings · "
         f"{unfertig} mit `char_gen_completed=false` (unfertig).\n")

# Übersicht
L.append("\n| Setting | Chars | unfertig |\n|---|---|---|")
for setting in sorted(rows):
    uf = sum(1 for r in rows[setting] if r['cg'] is False)
    L.append(f"| {setting} | {len(rows[setting])} | {uf or ''} |")

for setting in sorted(rows):
    rs = sorted(rows[setting], key=lambda r: r['name'])
    has_skp = any(r['skp'] for r in rs)
    has_m = any(r['maechte'] for r in rs)
    L.append(f"\n## {setting} ({len(rs)} Chars)\n")
    head = ("| Char | Attr | Fert | HP | " + ("Mächte | " if has_m else "")
            + ("SKP | " if has_skp else "") + "Aufst | Rang | Fehlende Ausrüstung |")
    sep = ("|---|---|---|---|" + ("---|" if has_m else "") + ("---|" if has_skp else "")
           + "---|---|---|")
    L.append(head); L.append(sep)
    for r in rs:
        nm = r['name'] + (' *(unfertig)*' if r['cg'] is False else '')
        mcell = (f" {flag(r['maechte'], '') if r['maechte'] else '—'} |" if has_m else "")
        skpcell = (f" {flag(r['skp'], '') if r['skp'] else '—'} |" if has_skp else "")
        miss = ', '.join(r['miss']) if r['miss'] else '—'
        L.append(f"| {nm} | {flag(r['attr'],'5')} | {flag(r['fert'],'12')} | {flag(r['hp'],'4')} |"
                 f"{mcell}{skpcell} {flag(r['au'],'')} | {r['rang']} | {miss} |")

open('logs/archetypen_anomalie_bericht.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print(f"OK: {gesamt} Archetypen, {len(rows)} Settings, {unfertig} unfertig -> logs/archetypen_anomalie_bericht.md")
