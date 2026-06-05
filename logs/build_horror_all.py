#!/usr/bin/env python3
"""
Build-All-Script fuer Horror Kompendium Archetypen (Seasoned = 4 Advances).
Baut alle etwa 35+ Archetypen, speichert sie und protokolliert Anomalien.

Korrektur-Stand 2025-06-03:
- Monstroese Archetypen verwenden jetzt ihr korrektes Volk (Engel/Dämon/etc.)
- Auto-Handicaps/Auto-Talente aus dem Volk werden NICHT manuell hinzugefuegt
- ignore_voraussetzungen=True + ignore_rang_check=True bei allen s.talent()-Aufrufen
- Swamp Freak / Nemesis / Slayer / Demonologist (Monstrous) bleiben Mensch (Superkraefte)
"""
import sys, os, traceback, json, time
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
sys.path.insert(0, os.path.abspath('.'))

import driver as d
from functions.character_advancement import increase_aufstiege

SETTING = 'Horror Kompendium'
OUTDIR = 'chars/Archetypen'
os.makedirs(OUTDIR, exist_ok=True)
os.makedirs('logs', exist_ok=True)

ALLLOG = open('logs/horror_all_trace.txt', 'w', encoding='utf-8')
def m(x):
    ALLLOG.write(str(x) + '\n')
    ALLLOG.flush()
def header(msg):
    ALLLOG.write('\n' + '=' * 60 + '\n' + str(msg) + '\n' + '=' * 60 + '\n')
    ALLLOG.flush()

# Skill -> regierendes Attribut (autoritativ aus 'settings/Horror Kompendium.json')
SKILL_ATTR = {
    'Allgemeinwissen': 'Verstand', 'Athletik': 'Geschicklichkeit', 'Darbietung': 'Willenskraft',
    'Diebeskunst': 'Geschicklichkeit', 'Einschüchtern': 'Willenskraft', 'Elektronik': 'Verstand',
    'Fahren': 'Geschicklichkeit', 'Fokus': 'Willenskraft', 'Geisteswissenschaften': 'Verstand',
    'Glaube': 'Willenskraft', 'Glücksspiel': 'Verstand', 'Hacken': 'Verstand', 'Heilen': 'Verstand',
    'Heimlichkeit': 'Geschicklichkeit', 'Kriegskunst': 'Verstand', 'Kämpfen': 'Geschicklichkeit',
    'Naturwissenschaften': 'Verstand', 'Okkultismus': 'Verstand', 'Pilot': 'Geschicklichkeit',
    'Provozieren': 'Verstand', 'Psionik': 'Willenskraft', 'Recherche': 'Verstand',
    'Reiten': 'Geschicklichkeit', 'Reparieren': 'Verstand', 'Schießen': 'Geschicklichkeit',
    'Seefahrt': 'Geschicklichkeit', 'Bootfahren': 'Geschicklichkeit', 'Sprache': 'Verstand',
    'Verrückte Wissenschaft': 'Verstand', 'Alchemie': 'Verstand', 'Wahrnehmung': 'Verstand',
    'Wahrsagen': 'Willenskraft', 'Zaubern': 'Verstand', 'Überleben': 'Verstand',
    'Überreden': 'Willenskraft',
}

def _attr_chargen_order(data):
    """CharGen-Attribut-Reihenfolge: Attribute, die ein hohes Skill-Ziel stützen, bekommen
    das knappe Budget (5 Attr-Punkte + HP) zuerst. So erreicht ein Attribut, das eine hohe
    Fertigkeit regiert, sein Ziel VOR der Fertigkeit -> vermeidet vermeidbare Doppelkosten
    (Skill steigt über ein noch nicht maximiertes Attribut). Reine Reihenfolge, Zielwerte
    bleiben unverändert."""
    attrs = data.get('attribute', {})
    skills = data.get('fertigkeiten', {})
    def prio(an):
        deps = [sz for sn, sz in skills.items() if SKILL_ATTR.get(sn) == an]
        return max(deps) if deps else 0
    return sorted(attrs.items(), key=lambda kv: (-prio(kv[0]), -kv[1]))

# ========================================================================
# VOLK AUTO-EINTRAEGE (aus Horror Kompendium.json)
# ========================================================================
def _load_volk_auto():
    """Liest auto_handicaps/auto_talente/attribute_bonuses direkt aus dem Setting-JSON,
    damit die SOLL-Erwartung IMMER den aktuellen Völkern entspricht (kein Stale-Dict mehr)."""
    with open('settings/Horror Kompendium.json', encoding='utf-8') as _vf:
        _vd = json.load(_vf)
    _out = {}
    for _vn, _v in _vd.get('voelker', {}).items():
        _eff = _v.get('effects', {}) or {}
        _out[_vn] = {
            'auto_handicaps': list(_eff.get('auto_handicaps', []) or []),
            'auto_talente': list(_eff.get('auto_talente', []) or []),
            'attribute_bonuses': dict(_eff.get('attribute_bonuses', {}) or {}),
        }
    _out.setdefault('Mensch', {'auto_handicaps': [], 'auto_talente': [], 'attribute_bonuses': {}})
    return _out


VOLK_AUTO = _load_volk_auto()

# ========================================================================
# REPORT
# ========================================================================
REPORT = {}

# ========================================================================
# BUILD HELPER - Human archetypes (build_seasoned_direct)
# ========================================================================
def build_seasoned_direct(name, data):
    header(f'BUILD: {name}')
    bericht_pfad = f'logs/horror_{name.lower().replace(" ","_").replace("/","_")}_bericht.json'
    protokoll_pfad = f'logs/horror_{name.lower().replace(" ","_").replace("/","_")}_log.txt'
    try:
        s = d.Sitzung(SETTING, name, protokoll=protokoll_pfad)
    except Exception as e:
        m(f'  FATAL: {e}')
        REPORT[name] = {'ok': False, 'error': f'Sitzung: {e}'}; return

    anomalies = 0
    try:
        voname = data.get('volk', 'Mensch')
        vauto = VOLK_AUTO.get(voname, VOLK_AUTO['Mensch'])

        # Handicaps (major first) — nur manuelle (keine auto)
        for h in data.get('handicaps', []):
            if h is None: continue
            r = s.handicap(h)
            if not r.get('ok'):
                anomalies += 1; m(f'  ANOM: handicap({h}): {r}')

        # Volk
        s.volk(voname)
        wm = s.volk_wahlmoeglichkeiten(voname)
        m(f'  Volkswahlen: {wm}')

        # Human choices (nur wenn Volk es unterstuetzt)
        if wm.get('freies_attribut') and data.get('freies_attribut'):
            s.volk_freies_attribut(voname, data['freies_attribut'])
        if wm.get('freies_talent') and data.get('freies_talent'):
            r = s.volk_freies_talent(voname, data['freies_talent'], ignore_voraussetzungen=True)
            if not r.get('ok'): anomalies += 1; m(f'  ANOM: freies_talent({data["freies_talent"]}): {r}')

        # Attributes (final values, nach Volk-Bonus automatisch)
        # Reihenfolge nach Skill-Priorität: Attribute mit hohen abhängigen Skills zuerst,
        # damit sie ihr Ziel im knappen CharGen-Budget erreichen (Doppelkosten-Vermeidung).
        for an, az in _attr_chargen_order(data):
            s.attribut_auf(an, az)
        for an, az in _attr_chargen_order(data):
            while s.ch.attribute[an].wuerfel.value < az and s.ch.verbleibende_handicap_punkte > 0:
                vv = s.ch.attribute[an].wuerfel.value
                s.steigere_mit_handicap_attribut(an)
                if s.ch.attribute[an].wuerfel.value == vv: break

        # Skills
        for sn, sz in data.get('fertigkeiten', {}).items():
            if sn in s.ch.fertigkeiten:
                s.fertigkeit_auf(sn, sz)
            else:
                m(f'  MISSING SKILL: {sn}'); s.notiz(f'SKILL fehlt: {sn}')
        for sn, sz in data.get('fertigkeiten', {}).items():
            if sn not in s.ch.fertigkeiten: continue
            while s.ch.fertigkeiten[sn].wuerfel.value < sz and s.ch.verbleibende_handicap_punkte > 0:
                vv = s.ch.fertigkeiten[sn].wuerfel.value
                s.steigere_mit_handicap_fertigkeit(sn)
                if s.ch.fertigkeiten[sn].wuerfel.value == vv: break

        m(f'  Punkte nach Skills: {s.punktestand()}')

        # Talents (Novice) — ignore_voraussetzungen + ignore_rang_check
        novice_edges = data.get('talente_novice', [])
        advance_edges = [a[1] for a in data.get('advances', []) if a[0] == 'talent']
        for t in novice_edges:
            if t is None: continue
            if t in s.ch.selected_talente: continue
            r = s.talent(t, ignore_voraussetzungen=True, ignore_rang_check=True)
            if not r.get('ok'): anomalies += 1; m(f'  ANOM: talent({t}): {r}')

        # Powers — soviele wie AB-Slots hergeben, Rest als Advances
        for mp in data.get('powers', []):
            if mp is None: continue
            r = s.macht(mp)
            if not r.get('ok'): anomalies += 1; m(f'  ANOM: macht({mp}): {r}')


        # Gear
        for gn, ga in data.get('gear', []):
            if gn is None: continue
            if gn in s.ch.ausruestung:
                s.kaufen(gn, ga)
            else:
                s.notiz(f'FEHLT im Katalog: {gn}')

        m(f'  Vor Abschluss: {s.punktestand()}')

        # Complete CharGen + 4 advances
        s.ch.char_gen_completed = True
        for _ in range(4):
            increase_aufstiege(s.ch)
        m(f'  Rang: {s.ch.rang}  Aufstiege: {s.ch.verbleibende_aufstiege}')

        # Detect double-cost: Welche Attribute sind zu niedrig fuer ihre Fertigkeiten?
        skill_attr_map = {
            'Athletik': 'Geschicklichkeit', 'Kämpfen': 'Geschicklichkeit',
            'Schießen': 'Geschicklichkeit', 'Heimlichkeit': 'Geschicklichkeit',
            'Fahren': 'Geschicklichkeit', 'Reiten': 'Geschicklichkeit',
            'Diebeskunst': 'Geschicklichkeit', 'Bootfahren': 'Geschicklichkeit',
            'Pilot': 'Geschicklichkeit',
            'Allgemeinwissen': 'Verstand', 'Elektronik': 'Verstand',
            'Heilen': 'Verstand', 'Wahrnehmung': 'Verstand',
            'Okkultismus': 'Verstand', 'Reparieren': 'Verstand',
            'Recherche': 'Verstand', 'Naturwissenschaften': 'Verstand',
            'Überleben': 'Verstand', 'Zaubern': 'Verstand', 'Psionik': 'Verstand',
            'Verrückte Wissenschaft': 'Verstand', 'Alchemie': 'Verstand',
            'Kriegskunst': 'Verstand', 'Glücksspiel': 'Verstand',
            'Hacken': 'Verstand', 'Geisteswissenschaften': 'Verstand',
            'Einschüchtern': 'Willenskraft', 'Darbietung': 'Willenskraft',
            'Überreden': 'Willenskraft', 'Provozieren': 'Willenskraft',
            'Glaube': 'Willenskraft',
        }
        extra_advances = 0
        # Hebe ALLE Attribute auf Zielwert, die zu niedrig sind
        for an, az in data.get('attribute', {}).items():
            if an in s.ch.attribute:
                attr_steps = 0
                while s.ch.attribute[an].wuerfel.value < az:
                    if attr_steps > 6: break  # Guard gegen Endlosschleife (Ziel unerreichbar, z.B. Cap W12)
                    attr_steps += 1
                    vv = s.ch.attribute[an].wuerfel.value
                    if s.ch.verbleibende_aufstiege <= 0:
                        increase_aufstiege(s.ch)
                        extra_advances += 1
                    s.charakter_mit_aufstieg(an, az)
                    if s.ch.attribute[an].wuerfel.value == vv: break
        # Jetzt Fertigkeiten nachziehen (auch untrainierte aktivieren)
        for sn, sz in data.get('fertigkeiten', {}).items():
            if sn not in s.ch.fertigkeiten: continue
            f = s.ch.fertigkeiten[sn]
            skill_steps = 0
            while f.wuerfel.value < sz or f.wuerfel.modifier < 0:
                if skill_steps > 6: break  # Guard
                skill_steps += 1
                vv, vm = f.wuerfel.value, f.wuerfel.modifier
                if s.ch.verbleibende_aufstiege <= 0:
                    increase_aufstiege(s.ch)
                    extra_advances += 1
                s.fertigkeit_mit_aufstieg(sn, zielwert=sz)
                if f.wuerfel.value == vv and f.wuerfel.modifier == vm: break
        if extra_advances:
            m(f'  Extra-Aufstiege: {extra_advances} (Attribut-Defizit)')
            s.notiz(f'{extra_advances} Extra-Aufstiege wegen Doppelkosten/Attribut-Defizit')

        # Retry failed novice talents with extra aufstiege
        for t in data.get('talente_novice', []):
            if t is None or t in s.ch.selected_talente: continue
            r = s.talent_mit_aufstieg(t, ignore_voraussetzungen=True)
            if not r.get('ok'): anomalies += 1; m(f'  ANOM: talent_retry({t}): {r}')

        # Apply advances
        for adv in data.get('advances', []):
            if adv[0] == 'skill':
                sn, sz = adv[1], adv[2]
                if sn in s.ch.fertigkeiten:
                    s.fertigkeit_mit_aufstieg(sn, zielwert=sz)
                else:
                    s.notiz(f'SKILL fehlt in Advance: {sn}')
            elif adv[0] == 'attribute':
                an, az = adv[1], adv[2]
                s.charakter_mit_aufstieg(an, az)
            elif adv[0] == 'talent':
                tn = adv[1]
                if tn is None: continue
                r = s.talent_mit_aufstieg(tn, ignore_voraussetzungen=True)
                if not r.get('ok'): anomalies += 1; m(f'  ANOM: talent_adv({tn}): {r}')
            elif adv[0] == 'power':
                pn = adv[1]
                if pn is None: continue
                r = s.macht(pn, ignore_rang_check=True)
                if not r.get('ok'): anomalies += 1; m(f'  ANOM: macht_adv({pn}): {r}')

        topup_adv = 0
        # === Skill-Topup: Bogen-Fertigkeiten unter Ziel (Doppelkosten) mit Aufstiegen nachziehen ===
        for sn, sz in (data.get('fertigkeiten', {}) or {}).items():
            if sn not in s.ch.fertigkeiten: continue
            g = 0
            while (s.ch.fertigkeiten[sn].wuerfel.value < sz or s.ch.fertigkeiten[sn].wuerfel.modifier < 0) and g < 8:
                g += 1
                vv = s.ch.fertigkeiten[sn].wuerfel.value; vm = s.ch.fertigkeiten[sn].wuerfel.modifier
                if s.ch.verbleibende_aufstiege < 1:
                    increase_aufstiege(s.ch); extra_advances += 1; topup_adv += 1
                s.fertigkeit_mit_aufstieg(sn, zielwert=sz)
                if s.ch.fertigkeiten[sn].wuerfel.value == vv and s.ch.fertigkeiten[sn].wuerfel.modifier == vm:
                    break
        # === Topup: alle noch fehlenden Bogen-Talente mit zusätzlichen Aufstiegen bezahlen ===
        # Doppelkosten (Skill >= Attribut) sind dem Bogen inhärent und nicht durch
        # Attributänderungen vermeidbar -> Budget reicht in CharGen nicht für alle Edges.
        # Fallback (User-Freigabe): Aufstiege erhöhen, bis jedes Bogen-Talent bezahlt ist.
        bow_talente = [t for t in (novice_edges + advance_edges) if t]
        ftt = data.get('freies_talent')
        if ftt: bow_talente.append(ftt)
        _seen = set(); bow_talente = [t for t in bow_talente if not (t in _seen or _seen.add(t))]
        for t in bow_talente:
            if t in s.ch.selected_talente: continue
            if s.ch.verbleibende_aufstiege < 1:
                increase_aufstiege(s.ch); extra_advances += 1; topup_adv += 1
            r = s.talent_mit_aufstieg(t, ignore_voraussetzungen=True)
            if not r.get('ok'):
                anomalies += 1; m(f'  TALENT nicht kaufbar trotz Aufstieg (AB/Macht?): {t}')
        if topup_adv:
            m(f'  Topup-Aufstiege für Talente: {topup_adv} (Rang jetzt {s.ch.rang})')
            s.notiz(f'{topup_adv} zusätzliche Aufstiege um alle Bogen-Talente zu bezahlen')

        # Diff & Save — inkludiere auto_handicaps/auto_talente vom Volk
        soll_at = {k: v for k, v in data.get('attribute', {}).items() if k in s.ch.attribute}
        soll_sk = {k: v for k, v in data.get('fertigkeiten', {}).items() if k in s.ch.fertigkeiten}
        all_final_talente = [t for t in (novice_edges + advance_edges) if t is not None]
        ft = data.get('freies_talent')
        if ft and ft not in all_final_talente:
            all_final_talente.append(ft)
        all_final_talente = list(set(all_final_talente + vauto['auto_talente']))
        all_handicaps = [h for h in (data.get('handicaps', []) + vauto['auto_handicaps']) if h is not None]
        all_powers = [p for p in (data.get('powers', [])) if p is not None]
        soll = {
            'attribute': soll_at,
            'fertigkeiten': soll_sk,
            'handicaps': all_handicaps,
            'talente': all_final_talente,
            'maechte': all_powers,
        }
        diff = s.diff(soll)
        m(f'  DIFF: {diff.get("abweichungen", [])}')
        m(f'  Restpunkte: {diff.get("restpunkte", {})}')

        save_path = os.path.join(OUTDIR, f'Archetyp_Horror_{name.replace(" ", "_").replace("/","_")}.json')
        s.speichern(save_path)
        m(f'  GESPEICHERT: {save_path}')

        bericht = s.bericht(bericht_pfad)
        total_anom = bericht.get('anomalien_anzahl', 0) + anomalies
        m(f'  GESAMT-ANOMALIEN: {total_anom}')
        REPORT[name] = {'ok': total_anom == 0, 'anomalien': total_anom,
                        'diff': diff.get('abweichungen', []), 'path': save_path}

    except Exception as e:
        m(f'  CRASH: {e}\n{traceback.format_exc()}')
        REPORT[name] = {'ok': False, 'error': str(e)}


# ========================================================================
# BUILD HELPER - Monstrous archetypes
# ========================================================================
def build_monstrous(name, data, has_superkraefte=False):
    header(f'BUILD (MONSTROeS): {name}')
    bericht_pfad = f'logs/horror_{name.lower().replace(" ","_")}_bericht.json'
    protokoll_pfad = f'logs/horror_{name.lower().replace(" ","_")}_log.txt'
    try:
        s = d.Sitzung(SETTING, name, protokoll=protokoll_pfad)
    except Exception as e:
        m(f'  FATAL: {e}')
        REPORT[name] = {'ok': False, 'error': str(e), 'monstrous': True}; return

    anomalies = 0
    try:
        voname = data.get('volk', 'Mensch')
        vauto = VOLK_AUTO.get(voname, VOLK_AUTO['Mensch'])
        auto_hc_set = set(vauto['auto_handicaps'])
        auto_tal_set = set(vauto['auto_talente'])

        if has_superkraefte:
            m(f'  INFO: Archetyp nutzt Superkraefte/Gifts of the Night — nur partiell baubar')

        # Handicaps — NUR manuelle (auto werden vom Volk gesetzt)
        for h in data.get('handicaps', []):
            if h is None:
                m(f'  SKIP Unknown HC key (None)')
                continue
            r = s.handicap(h)
            if not r.get('ok'): anomalies += 1; m(f'  ANOM: handicap({h}): {r}')

        # Volk
        s.volk(voname)
        wm = s.volk_wahlmoeglichkeiten(voname)
        m(f'  Volkswahlen: {wm}')
        m(f'  Auto-Handicaps: {vauto["auto_handicaps"]}')
        m(f'  Auto-Talente: {vauto["auto_talente"]}')
        m(f'  Attribute-Boni: {vauto["attribute_bonuses"]}')

        # Human choices nur wenn Volk es unterstuetzt
        if wm.get('freies_attribut') and data.get('freies_attribut'):
            s.volk_freies_attribut(voname, data['freies_attribut'])
        if wm.get('freies_talent') and data.get('freies_talent'):
            r = s.volk_freies_talent(voname, data['freies_talent'], ignore_voraussetzungen=True)
            if not r.get('ok'): anomalies += 1; m(f'  ANOM: freies_talent({data["freies_talent"]})')

        # Attributes (final values — Volk-Boni bereits automatisch)
        # Reihenfolge nach Skill-Priorität (Doppelkosten-Vermeidung, s. _attr_chargen_order).
        for an, az in _attr_chargen_order(data):
            s.attribut_auf(an, az)
        for an, az in _attr_chargen_order(data):
            while s.ch.attribute[an].wuerfel.value < az and s.ch.verbleibende_handicap_punkte > 0:
                vv = s.ch.attribute[an].wuerfel.value
                s.steigere_mit_handicap_attribut(an)
                if s.ch.attribute[an].wuerfel.value == vv: break

        # Skills
        for sn, sz in data.get('fertigkeiten', {}).items():
            if sn in s.ch.fertigkeiten:
                s.fertigkeit_auf(sn, sz)
            else:
                m(f'  MISSING SKILL: {sn}'); s.notiz(f'SKILL fehlt: {sn}')
        for sn, sz in data.get('fertigkeiten', {}).items():
            if sn not in s.ch.fertigkeiten: continue
            while s.ch.fertigkeiten[sn].wuerfel.value < sz and s.ch.verbleibende_handicap_punkte > 0:
                vv = s.ch.fertigkeiten[sn].wuerfel.value
                s.steigere_mit_handicap_fertigkeit(sn)
                if s.ch.fertigkeiten[sn].wuerfel.value == vv: break

        m(f'  Punkte nach Skills: {s.punktestand()}')

        # Edges — ignore_voraussetzungen + ignore_rang_check
        for t in data.get('talente_novice', []):
            if t is None: continue
            if t in s.ch.selected_talente: continue
            r = s.talent(t, ignore_voraussetzungen=True, ignore_rang_check=True)
            if not r.get('ok'): anomalies += 1; m(f'  ANOM: talent({t}): {r}')

        # Powers — soviele wie AB-Slots hergeben, Rest als Advances
        for mp in data.get('powers', []):
            if mp is None: continue
            r = s.macht(mp)
            if not r.get('ok'): anomalies += 1; m(f'  ANOM: macht({mp}): {r}')

        # Gear
        for gn, ga in data.get('gear', []):
            if gn is None: continue
            if gn in s.ch.ausruestung: s.kaufen(gn, ga)
            else: s.notiz(f'FEHLT im Katalog: {gn}')

        # Document monstrous powers / Superkraefte
        for mp in data.get('monstrous_powers', []):
            s.notiz(f'MONSTROeSE KRAFT (nicht simulierbar): {mp}')

        m(f'  Vor Abschluss: {s.punktestand()}')

        # Complete + advances
        s.ch.char_gen_completed = True
        for _ in range(4):
            increase_aufstiege(s.ch)
        m(f'  Rang: {s.ch.rang}')

         # Hebe ALLE Attribute auf Zielwert (Doppelkosten vermeiden)
        extra_advances = 0
        for an, az in data.get('attribute', {}).items():
            if an in s.ch.attribute:
                attr_steps = 0
                while s.ch.attribute[an].wuerfel.value < az:
                    if attr_steps > 6: break  # Guard gegen Endlosschleife (Ziel unerreichbar, z.B. Cap W12)
                    attr_steps += 1
                    vv = s.ch.attribute[an].wuerfel.value
                    if s.ch.verbleibende_aufstiege <= 0:
                        increase_aufstiege(s.ch)
                        extra_advances += 1
                    s.charakter_mit_aufstieg(an, az)
                    if s.ch.attribute[an].wuerfel.value == vv: break
        # Jetzt Fertigkeiten nachziehen (auch untrainierte aktivieren)
        for sn, sz in data.get('fertigkeiten', {}).items():
            if sn not in s.ch.fertigkeiten: continue
            f = s.ch.fertigkeiten[sn]
            skill_steps = 0
            while f.wuerfel.value < sz or f.wuerfel.modifier < 0:
                if skill_steps > 6: break
                skill_steps += 1
                vv, vm = f.wuerfel.value, f.wuerfel.modifier
                if s.ch.verbleibende_aufstiege <= 0:
                    increase_aufstiege(s.ch)
                    extra_advances += 1
                s.fertigkeit_mit_aufstieg(sn, zielwert=sz)
                if f.wuerfel.value == vv and f.wuerfel.modifier == vm: break
        if extra_advances:
            m(f'  Extra-Aufstiege: {extra_advances} (Attribut-Defizit)')
            s.notiz(f'{extra_advances} Extra-Aufstiege wegen Doppelkosten/Attribut-Defizit')

        # Retry failed novice talents with extra aufstiege
        for t in data.get('talente_novice', []):
            if t is None or t in s.ch.selected_talente: continue
            r = s.talent_mit_aufstieg(t, ignore_voraussetzungen=True)
            if not r.get('ok'): anomalies += 1; m(f'  ANOM: talent_retry({t}): {r}')

        for adv in data.get('advances', []):
            if adv[0] == 'skill':
                sn, sz = adv[1], adv[2]
                if sn in s.ch.fertigkeiten:
                    s.fertigkeit_mit_aufstieg(sn, zielwert=sz)
            elif adv[0] == 'attribute':
                an, az = adv[1], adv[2]
                s.charakter_mit_aufstieg(an, az)
            elif adv[0] == 'talent':
                tn = adv[1]
                if tn is None: continue
                r = s.talent_mit_aufstieg(tn, ignore_voraussetzungen=True)
                if not r.get('ok'): anomalies += 1; m(f'  ANOM: talent_adv({tn}): {r}')
            elif adv[0] == 'power':
                pn = adv[1]
                if pn is None: continue
                r = s.macht(pn, ignore_rang_check=True)
                if not r.get('ok'): anomalies += 1; m(f'  ANOM: macht_adv({pn}): {r}')

        topup_adv = 0
        # === Skill-Topup: Bogen-Fertigkeiten unter Ziel (Doppelkosten) mit Aufstiegen nachziehen ===
        for sn, sz in (data.get('fertigkeiten', {}) or {}).items():
            if sn not in s.ch.fertigkeiten: continue
            g = 0
            while (s.ch.fertigkeiten[sn].wuerfel.value < sz or s.ch.fertigkeiten[sn].wuerfel.modifier < 0) and g < 8:
                g += 1
                vv = s.ch.fertigkeiten[sn].wuerfel.value; vm = s.ch.fertigkeiten[sn].wuerfel.modifier
                if s.ch.verbleibende_aufstiege < 1:
                    increase_aufstiege(s.ch); extra_advances += 1; topup_adv += 1
                s.fertigkeit_mit_aufstieg(sn, zielwert=sz)
                if s.ch.fertigkeiten[sn].wuerfel.value == vv and s.ch.fertigkeiten[sn].wuerfel.modifier == vm:
                    break  # kein Fortschritt trotz Aufstieg -> echte Blockade
        # === Topup: alle noch fehlenden Bogen-Talente mit zusätzlichen Aufstiegen bezahlen ===
        # (Doppelkosten Skill>=Attribut sind bogeninhärent; Fallback per User-Freigabe.)
        _bt = [t for t in (data.get('talente_novice', []) or []) if t]
        _bt += [a[1] for a in (data.get('advances', []) or []) if a[0] == 'talent' and a[1]]
        _ftm = data.get('freies_talent')
        if _ftm: _bt.append(_ftm)
        _seen = set(); _bt = [t for t in _bt if not (t in _seen or _seen.add(t))]
        for t in _bt:
            if t in s.ch.selected_talente: continue
            if s.ch.verbleibende_aufstiege < 1:
                increase_aufstiege(s.ch); extra_advances += 1; topup_adv += 1
            r = s.talent_mit_aufstieg(t, ignore_voraussetzungen=True)
            if not r.get('ok'):
                anomalies += 1; m(f'  TALENT nicht kaufbar trotz Aufstieg (AB/Macht?): {t}')
        if topup_adv:
            m(f'  Topup-Aufstiege für Talente: {topup_adv} (Rang jetzt {s.ch.rang})')
            s.notiz(f'{topup_adv} zusätzliche Aufstiege um alle Bogen-Talente zu bezahlen')

        # Diff & Save — inkludiere auto_handicaps/auto_talente vom Volk
        soll_at = {k: v for k, v in data.get('attribute', {}).items() if k in s.ch.attribute}
        soll_sk = {k: v for k, v in data.get('fertigkeiten', {}).items() if k in s.ch.fertigkeiten}
        avt = [a[1] for a in data.get('advances', []) if a[0] == 'talent' and a[1] is not None]
        all_final_talente = [t for t in (data.get('talente_novice', []) + avt) if t is not None]
        ft = data.get('freies_talent')
        if ft and ft not in all_final_talente:
            all_final_talente.append(ft)
        all_final_talente = list(set(all_final_talente + vauto['auto_talente']))
        all_handicaps = [h for h in (data.get('handicaps', []) + vauto['auto_handicaps']) if h is not None]
        all_powers = [p for p in (data.get('powers', [])) if p is not None]
        soll = {
            'attribute': soll_at, 'fertigkeiten': soll_sk,
            'handicaps': all_handicaps,
            'talente': all_final_talente,
            'maechte': all_powers,
        }
        diff = s.diff(soll)
        m(f'  DIFF: {diff.get("abweichungen", [])}')
        m(f'  Restpunkte: {diff.get("restpunkte", {})}')

        save_path = os.path.join(OUTDIR, f'Archetyp_Horror_{name.replace(" ", "_").replace("/","_")}.json')
        s.speichern(save_path)
        m(f'  GESPEICHERT: {save_path}')

        bericht = s.bericht(bericht_pfad)
        total_anom = bericht.get('anomalien_anzahl', 0) + anomalies
        m(f'  GESAMT-ANOMALIEN: {total_anom}')
        REPORT[name] = {'ok': total_anom == 0, 'anomalien': total_anom,
                        'diff': diff.get('abweichungen', []), 'path': save_path,
                        'monstrous': True, 'superkraefte': has_superkraefte}

    except Exception as e:
        m(f'  CRASH: {e}\n{traceback.format_exc()}')
        REPORT[name] = {'ok': False, 'error': str(e), 'monstrous': True}


# ========================================================================
# ARCHETYPE DATA — Human
# ========================================================================

# --- GHOST HUNTER (Human) ---
ghost_hunter = {
    'volk': 'Mensch',
    'freies_attribut': 'Geschicklichkeit',
    'freies_talent': None,
    'handicaps': ['Neugierig', 'Gierig_leicht', 'Tick'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {
        'Athletik': 4, 'Allgemeinwissen': 4, 'Fahren': 4, 'Elektronik': 6,
        'Kämpfen': 4, 'Wahrnehmung': 6, 'Okkultismus': 6, 'Darbietung': 6,
        'Überreden': 6, 'Reparieren': 6, 'Recherche': 6, 'Naturwissenschaften': 6,
        'Schießen': 6, 'Heimlichkeit': 4,
    },
    'talente_novice': ['Stinkreich'],
    'powers': [],
    'gear': [('EMF-Detektor', 1), ('Geisterfalle', 1), ('Geisterjägerpaket', 1),
               ('Kamera (normal)', 1), ('Taschenlampe (10" Strahl)', 1)],

    'advances': [
        ('skill', 'Elektronik', 6),
        ('skill', 'Reparieren', 6),
        ('talent', 'Bekannt'),
        ('talent', 'Monsterjäger'),
    ],
}

# --- NERD (Human) ---
nerd = {
    'volk': 'Mensch',
    'freies_attribut': 'Verstand',
    'freies_talent': None,
    'handicaps': ['Schlechte Augen', 'Neugierig', 'Außenseiter'],
    'attribute': {'Geschicklichkeit': 4, 'Verstand': 10, 'Willenskraft': 6, 'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {
        'Geisteswissenschaften': 8, 'Athletik': 4, 'Allgemeinwissen': 4,
        'Elektronik': 6, 'Kämpfen': 4, 'Hacken': 4, 'Wahrnehmung': 8,
        'Okkultismus': 4, 'Überreden': 4, 'Reparieren': 6, 'Recherche': 8,
        'Naturwissenschaften': 6, 'Schießen': 4, 'Heimlichkeit': 4,
    },
    'talente_novice': ['Ermittler', 'Gelehrter'],
    'powers': [],
    'gear': [('Rucksack', 1), ('Taschenlampe (10" Strahl)', 1), ('Schutzbrille', 1),
               ('Werkzeugkoffer', 1)],

    'advances': [
        ('skill', 'Geisteswissenschaften', 8),
        ('skill', 'Elektronik', 6),
        ('skill', 'Okkultismus', 4),
        ('skill', 'Wahrnehmung', 8),
        ('talent', 'McGyver'),
        ('talent', 'Berechnend'),
    ],
}

# --- JOCK (Human) ---
jock = {
    'volk': 'Mensch',
    'freies_attribut': 'Stärke',
    'freies_talent': 'Kräftig',
    'handicaps': ['Arrogant', 'Tyrann_leicht', 'Eifersüchtig'],
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 4, 'Willenskraft': 6, 'Stärke': 10, 'Konstitution': 8},
    'fertigkeiten': {
        'Athletik': 10, 'Allgemeinwissen': 4, 'Fahren': 4, 'Kämpfen': 8,
        'Einschüchtern': 6, 'Wahrnehmung': 4, 'Überreden': 4,
        'Schießen': 4, 'Heimlichkeit': 6, 'Überleben': 4, 'Provozieren': 4,
    },
    'talente_novice': [],
    'powers': [],
    'gear': [('Keule, Leicht', 1), ('Kevlarweste', 1), ('Feuerzeug', 1),
               ('Taschenlampe (10" Strahl)', 1)],

    'advances': [
        ('talent', 'Attraktiv'),
        ('talent', 'Flink'),
        ('skill', 'Athletik', 10),
        ('attribute', 'Stärke', 10),
    ],
}

# --- PSYCHIC (Human) ---
psychic = {
    'volk': 'Mensch',
    'freies_attribut': 'Willenskraft',
    'freies_talent': 'AH (Psionischer Ermittler)',
    'handicaps': ['Düsternis_leicht', 'Sanftmütig', 'Opfer_schwer'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {
        'Athletik': 4, 'Allgemeinwissen': 6, 'Fahren': 4, 'Kämpfen': 4,
        'Wahrnehmung': 8, 'Okkultismus': 4, 'Überreden': 6, 'Psionik': 8,
        'Recherche': 4, 'Heimlichkeit': 6,
    },
    'talente_novice': ['Aufmerksamkeit'],
    'powers': ['Verwirrung', 'Empathie', 'Gedankenlesen'],
    'gear': [('Taser', 1), ('Kleidung, Alltag', 1), ('Taschenlampe (10" Strahl)', 1)],

    'advances': [
        ('talent', 'Sechster Sinn'),
        ('talent', None),  # Scan - MISSING
        ('talent', 'Seher'),
        ('talent', 'Kühler Kopf'),
    ],
}

# --- EXORCIST (Human) ---
exorcist = {
    'volk': 'Mensch',
    'freies_attribut': 'Willenskraft',
    'freies_talent': 'AH (Priester)',
    'handicaps': ['Alt', 'Abergläubisch_leicht', 'Misstrauisch_leicht', 'Schwur_schwer'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {
        'Geisteswissenschaften': 4, 'Athletik': 6, 'Allgemeinwissen': 6,
        'Glaube': 8, 'Kämpfen': 4, 'Einschüchtern': 8, 'Wahrnehmung': 6,
        'Okkultismus': 6, 'Überreden': 6, 'Recherche': 6, 'Heimlichkeit': 6,
    },
    'talente_novice': ['Mut', 'Elan'],
    'powers': ['Heilung', 'Schutz', 'Linderung', 'Schutzkreis', 'Kriegersegen'],
    'gear': [('Silberdolch', 1), ('Weihwasser (Flasche)', 1)],

    'advances': [
        ('talent', None),  # Aura of Courage - MISSING
        ('talent', None),  # Mercy - MISSING
        ('talent', 'Mut'),  # already at novice
        ('attribute', 'Verstand', 8),
    ],
}

# --- GAMER (Human) ---
gamer = {
    'volk': 'Mensch',
    'freies_attribut': 'Verstand',
    'freies_talent': None,
    'handicaps': ['Loyal', 'Arm', 'Tick', 'Stur'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {
        'Geisteswissenschaften': 4, 'Athletik': 4, 'Kriegskunst': 6,
        'Allgemeinwissen': 4, 'Fahren': 4, 'Elektronik': 4, 'Kämpfen': 4,
        'Wahrnehmung': 4, 'Okkultismus': 4, 'Überreden': 8,
        'Schießen': 4, 'Heimlichkeit': 4, 'Provozieren': 6,
    },
    'talente_novice': ['Anführer', 'Selbstlos', 'Mutig', 'Elan', 'Anheizen'],
    'powers': [],
    'gear': [('Pfefferspray', 1), ('Rucksack', 1)],

    'advances': [
        ('talent', 'Glück'),
        ('talent', 'Elan'),  # already at novice
        ('talent', 'Selbstlos'),  # already at novice
        ('talent', 'Mutig'),  # already at novice
    ],
}

# --- PARTY ANIMAL (Human) ---
party_animal = {
    'volk': 'Mensch',
    'freies_attribut': 'Willenskraft',
    'freies_talent': 'Charismatisch',
    'handicaps': ['Verliebt_leicht', 'Große Klappe', 'Schreihals_schwer'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 8},
    'fertigkeiten': {
        'Athletik': 6, 'Allgemeinwissen': 6, 'Fahren': 4, 'Glücksspiel': 6,
        'Einschüchtern': 6, 'Wahrnehmung': 4, 'Darbietung': 6,
        'Überreden': 8, 'Heimlichkeit': 6, 'Provozieren': 6,
    },
    'talente_novice': ['Improvisationsgabe'],
    'powers': [],
    'gear': [('Feuerzeug', 1), ('Kleidung, Alltag', 1)],

    'advances': [
        ('talent', 'Erniedrigen'),
        ('talent', 'Geschickte Riposte'),
        ('talent', 'Mut in Flaschen'),
        ('talent', 'Improvisationsgabe'),  # already at novice
    ],
}

# --- RUNNER (Human) ---
runner = {
    'volk': 'Mensch',
    'freies_attribut': 'Konstitution',
    'freies_talent': 'Flink',
    'handicaps': ['Schreckhaft_leicht', 'Loyal', 'Feige'],
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 8},
    'fertigkeiten': {
        'Athletik': 8, 'Allgemeinwissen': 6, 'Fahren': 4, 'Kämpfen': 4,
        'Heilen': 4, 'Wahrnehmung': 4, 'Okkultismus': 4, 'Überreden': 6,
        'Heimlichkeit': 8, 'Überleben': 4, 'Provozieren': 4,
    },
    'talente_novice': ['Ausweichen', 'Rückzug'],
    'powers': [],
    'gear': [('UV-Granate', 4), ('Wanderstiefel', 1),
               ('Taschenlampe (10" Strahl)', 1)],

    'advances': [
        ('talent', 'Schnell'),
        ('talent', 'Parkour'),
        ('attribute', 'Konstitution', 8),
        ('talent', 'Ausweichen'),  # already at novice
    ],
}

# --- WITCH (Human) ---
witch = {
    'volk': 'Mensch',
    'freies_attribut': 'Willenskraft',
    'freies_talent': 'AH (Hexenmeister/Hexe)',
    'handicaps': ['Skrupellos', 'Dünnhäutig', 'Rachsüchtig_leicht'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {
        'Athletik': 4, 'Allgemeinwissen': 6, 'Kämpfen': 4, 'Einschüchtern': 8,
        'Wahrnehmung': 4, 'Okkultismus': 8, 'Überreden': 4,
        'Recherche': 4, 'Zaubern': 8, 'Heimlichkeit': 6, 'Überleben': 4,
    },
    'talente_novice': ['Bedrohlich'],
    'powers': ['Tierfreund', 'Eigenschaft erhöhen/senken', 'Fluchwort', 'Schutz', 'Geisterruf'],
    'gear': [('Silberdolch', 1), ('Rucksack', 1)],

    'advances': [
        ('talent', 'Machtpunkte'),
        ('talent', 'Energieschub'),
        ('skill', 'Allgemeinwissen', 6),
        ('skill', 'Einschüchtern', 8),
        ('talent', 'Neue Mächte'),
        ('power', 'Fluchwort'),
        ('power', 'Geisterruf'),
    ],
}

# --- DOCTOR (Human) ---
doctor = {
    'volk': 'Mensch',
    'freies_attribut': 'Verstand',
    'freies_talent': 'Heiler',
    'handicaps': ['Bluter_schwer', 'Vorsichtig', 'Beschämt'],
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {
        'Geisteswissenschaften': 6, 'Athletik': 4, 'Allgemeinwissen': 6,
        'Fahren': 4, 'Kämpfen': 6, 'Heilen': 8, 'Einschüchtern': 6,
        'Wahrnehmung': 4, 'Überreden': 6, 'Recherche': 4,
        'Naturwissenschaften': 4, 'Heimlichkeit': 4,
    },
    'talente_novice': ['Berserker', 'Schwer zu töten'],
    'powers': [],
    'gear': [('Überlebensmesser', 1), ('Erste-Hilfe-Tasche', 1)],

    'advances': [
        ('attribute', 'Willenskraft', 8),
        ('talent', 'Heiler'),  # already at novice
        ('talent', 'Unerbittlich'),
        ('talent', 'Schwer zu töten'),  # already at novice
    ],
}

# --- OCCULTIST (Human) ---
occultist = {
    'volk': 'Mensch',
    'freies_attribut': 'Willenskraft',
    'freies_talent': 'AH (Okkultist)',
    'handicaps': ['Übermütig'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {
        'Athletik': 6, 'Allgemeinwissen': 4, 'Kämpfen': 6, 'Wahrnehmung': 6,
        'Okkultismus': 8, 'Überreden': 8, 'Recherche': 6, 'Zaubern': 8, 'Heimlichkeit': 4,
    },
    'talente_novice': [],
    'powers': ['Arkanes entdecken/verbergen', 'Aufheben', 'Schutz', 'Schutzkreis'],
    'gear': [('Kleidung, Alltag', 1), ('Taschenlampe (10" Strahl)', 1)],

    'advances': [
        ('attribute', 'Stärke', 6),
        ('skill', 'Überreden', 8),
        ('skill', 'Zaubern', 8),
        ('talent', 'Stillzauberer'),
        ('talent', 'Neue Mächte'),
        ('power', 'Aufheben'),
    ],
}

# --- CONSTABLE (Human) ---
constable = {
    'volk': 'Mensch',
    'freies_attribut': 'Konstitution',
    'freies_talent': 'Mut',
    'handicaps': ['Heldenhaft', 'Schwur_schwer'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 8},
    'fertigkeiten': {
        'Athletik': 6, 'Allgemeinwissen': 6, 'Kämpfen': 8, 'Heilen': 4,
        'Einschüchtern': 6, 'Wahrnehmung': 8, 'Überreden': 6,
        'Schießen': 6, 'Heimlichkeit': 6,
    },
    'talente_novice': ['Block', 'Eisenkiefer'],
    'powers': [],
    'gear': [('Schlagstock', 1), ('Handschellen', 1), ('Laterne', 1),
               ('Trillerpfeife', 1), ('Laternen-Öl', 1)],

    'advances': [
        ('talent', 'Schmerzresistenz'),
        ('skill', 'Heilen', 4),
        ('skill', 'Heimlichkeit', 6),
        ('skill', 'Kämpfen', 8),
        ('talent', 'Block'),  # already at novice
    ],
}

# --- JOURNALIST (Human) ---
journalist = {
    'volk': 'Mensch',
    'freies_attribut': 'Verstand',
    'freies_talent': 'Charismatisch',
    'handicaps': ['Neugierig', 'Pazifist_leicht', 'Stur'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {
        'Geisteswissenschaften': 6, 'Athletik': 4, 'Allgemeinwissen': 8,
        'Kämpfen': 4, 'Wahrnehmung': 8, 'Okkultismus': 4,
        'Überreden': 8, 'Recherche': 8, 'Heimlichkeit': 6,
    },
    'talente_novice': ['Aufmerksamkeit', 'Beziehungen'],
    'powers': [],
    'gear': [('Derringer', 1), ('Rucksack', 1), ('Kamera (normal)', 1),
               ('Regenschirm', 1), ('Patronen (Klein)', 1)],

    'advances': [
        ('skill', 'Okkultismus', 4),
        ('skill', 'Überreden', 8),
        ('talent', 'Ermittler'),
        ('talent', 'Beziehungen'),  # already at novice
        ('talent', 'Gassenwissen'),
    ],
}

# --- BURGLAR (Human) ---
burglar = {
    'volk': 'Mensch',
    'freies_attribut': 'Geschicklichkeit',
    'freies_talent': 'Dieb',
    'handicaps': ['Gierig_schwer', 'Abergläubisch_leicht', 'Gesucht_leicht'],
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {
        'Athletik': 8, 'Allgemeinwissen': 4, 'Kämpfen': 4, 'Wahrnehmung': 6,
        'Überreden': 6, 'Schießen': 6, 'Heimlichkeit': 8,
        'Provozieren': 6, 'Diebeskunst': 8,
    },
    'talente_novice': ['Parkour', 'Gassenwissen', 'Starker Wille'],
    'powers': [],
    'gear': [('Derringer', 1), ('Dolch/Messer', 1), ('Dietriche', 1),
               ('Seil, Nylon (10" / 20 m)', 1), ('Patronen (Klein)', 1)],

    'advances': [
        ('attribute', 'Willenskraft', 8),
        ('talent', 'Starker Wille'),  # already at novice
        ('skill', 'Athletik', 8),
        ('skill', 'Überreden', 6),
        ('talent', 'Parkour'),  # already at novice
    ],
}

# --- ARISTOCRAT (Human) ---
aristocrat = {
    'volk': 'Mensch',
    'freies_attribut': 'Verstand',
    'freies_talent': 'Aristokrat',
    'handicaps': ['Arrogant', 'Vorsichtig', 'Misstrauisch_leicht'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {
        'Geisteswissenschaften': 6, 'Athletik': 6, 'Allgemeinwissen': 6,
        'Kämpfen': 6, 'Wahrnehmung': 4, 'Überreden': 6,
        'Recherche': 4, 'Reiten': 4, 'Schießen': 4,
        'Heimlichkeit': 4, 'Provozieren': 6,
    },
    'talente_novice': ['Stinkreich', 'Kühler Kopf', 'Geschickte Riposte'],
    'powers': [],
    'gear': [('Rapier', 1), ('Kleidung, Alltag', 1), ('Pferd', 1)],

    'advances': [
        ('talent', 'Beziehungen'),
        ('attribute', 'Verstand', 8),
        ('talent', 'Geschickte Riposte'),  # already at novice
        ('talent', 'Kühler Kopf'),  # already at novice
    ],
}

# --- MAMBO (Human) ---
mambo = {
    'volk': 'Mensch',
    'freies_attribut': 'Willenskraft',
    'freies_talent': 'AH (Voodooist)',
    'handicaps': ['Heldenhaft', 'Abergläubisch_leicht', 'Misstrauisch_leicht'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 8},
    'fertigkeiten': {
        'Athletik': 4, 'Allgemeinwissen': 6, 'Glaube': 8, 'Kämpfen': 4,
        'Heilen': 6, 'Einschüchtern': 6, 'Wahrnehmung': 6,
        'Okkultismus': 6, 'Darbietung': 4, 'Überreden': 8, 'Heimlichkeit': 6,
    },
    'talente_novice': [],
    'powers': [],
    'gear': [('Schlagstock', 1), ('Silberdolch', 1), ('Kerze', 1),
               ('Weihwasser (Flasche)', 1)],

    'advances': [
        ('skill', 'Okkultismus', 6),
        ('skill', 'Darbietung', 4),
        ('talent', 'Machtpunkte'),
        ('talent', 'Heiliger/Unheiliger Krieger'),
        ('talent', 'Der/Die Auserwählte'),
    ],
}

# --- SAILOR (Human) ---
sailor = {
    'volk': 'Mensch',
    'freies_attribut': 'Konstitution',
    'freies_talent': 'Ass am Steuer',
    'handicaps': ['Verliebt_leicht', 'Verpeilt', 'Langsam_leicht'],
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 4, 'Willenskraft': 6, 'Stärke': 8, 'Konstitution': 8},
    'fertigkeiten': {
        'Athletik': 8, 'Seefahrt': 8, 'Allgemeinwissen': 4, 'Kämpfen': 6,
        'Einschüchtern': 6, 'Wahrnehmung': 4, 'Überreden': 4,
        'Heimlichkeit': 4, 'Überleben': 6,
    },
    'talente_novice': ['Mut in Flaschen', 'Schmerzresistenz', 'Ruhige Hände'],
    'powers': [],
    'gear': [('Seil, Hanf (10" / 20 m)', 1), ('Trillerpfeife', 1)],

    'advances': [
        ('attribute', 'Konstitution', 8),
        ('talent', 'Mut in Flaschen'),  # already at novice
        ('talent', 'Schmerzresistenz'),  # already at novice
        ('talent', 'Meisterschütze'),
    ],
}

# --- EXPLORER (Human) ---
explorer = {
    'volk': 'Mensch',
    'freies_attribut': 'Verstand',
    'freies_talent': 'Sechster Sinn',
    'handicaps': ['Neugierig', 'Übermütig'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {
        'Geisteswissenschaften': 6, 'Athletik': 6, 'Allgemeinwissen': 6,
        'Fahren': 4, 'Kämpfen': 6, 'Wahrnehmung': 6, 'Überreden': 4,
        'Pilot': 4, 'Recherche': 6, 'Schießen': 6,
        'Heimlichkeit': 4, 'Überleben': 8,
    },
    'talente_novice': ['Kühler Kopf', 'Reich', 'Naturbursche'],
    'powers': [],
    'gear': [('Pistole', 1), ('Überlebensmesser', 1), ('Kevlarweste', 1),
               ('Wanderstiefel', 1), ('Erste-Hilfe-Tasche', 1),
               ('Taschenlampe (10" Strahl)', 1), ('Seil, Nylon (10" / 20 m)', 1),
               ('Patronen (Mittel)', 1)],

    'advances': [
        ('attribute', 'Verstand', 8),
        ('skill', 'Überleben', 8),
        ('skill', 'Wahrnehmung', 6),
        ('talent', 'Naturbursche'),  # already at novice
        ('talent', 'Kühler Kopf'),  # already at novice
    ],
}

# --- SOLDIER (Human) ---
soldier = {
    'volk': 'Mensch',
    'freies_attribut': 'Willenskraft',
    'freies_talent': 'Soldat',
    'handicaps': ['Schreckhaft_leicht', 'Stur', 'Schwur_schwer'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 8, 'Konstitution': 6},
    'fertigkeiten': {
        'Athletik': 6, 'Kriegskunst': 4, 'Allgemeinwissen': 4,
        'Kämpfen': 6, 'Einschüchtern': 6, 'Wahrnehmung': 4,
        'Überreden': 4, 'Schießen': 10, 'Heimlichkeit': 6, 'Überleben': 4,
    },
    'talente_novice': ['Kräftig', 'Volles Rohr!', 'Anführer'],
    'powers': [],
    'gear': [('Gewehr', 1), ('Überlebensmesser', 1),
               ('Helm (Kette)', 1), ('Wanderstiefel', 1), ('Reiserationen', 1)],

    'advances': [
        ('talent', 'Anführer'),  # already at novice
        ('attribute', 'Willenskraft', 8),
        ('skill', 'Schießen', 10),
        ('talent', 'Volles Rohr!'),  # already at novice
    ],
}

# --- SOCIALITE (Human) ---
socialite = {
    'volk': 'Mensch',
    'freies_attribut': 'Willenskraft',
    'freies_talent': 'Sehr Attraktiv',
    'handicaps': ['Große Klappe', 'Gierig_schwer', 'Schreihals_leicht'],
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {
        'Athletik': 6, 'Allgemeinwissen': 4, 'Fahren': 4, 'Kämpfen': 4,
        'Glücksspiel': 4, 'Wahrnehmung': 6, 'Darbietung': 8,
        'Überreden': 8, 'Schießen': 4, 'Heimlichkeit': 4,
        'Überleben': 4, 'Provozieren': 6,
    },
    'talente_novice': ['Bekannt'],
    'powers': [],
    'gear': [('Kleidung, Alltag', 1), ('Feuerzeug', 1)],

    'advances': [
        ('skill', 'Darbietung', 8),
        ('skill', 'Überleben', 4),
        ('talent', 'Bekannt'),  # already at novice
        ('attribute', 'Verstand', 8),
        ('talent', 'Aufwiegler'),
    ],
}

# --- GUMSHOE (Human) ---
gumshoe = {
    'volk': 'Mensch',
    'freies_attribut': 'Verstand',
    'freies_talent': 'Ermittler',
    'handicaps': ['Neugierig', 'Gierig_leicht', 'Stur'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 8},
    'fertigkeiten': {
        'Athletik': 4, 'Allgemeinwissen': 6, 'Fahren': 4, 'Kämpfen': 6,
        'Einschüchtern': 4, 'Wahrnehmung': 6, 'Überreden': 6,
        'Recherche': 8, 'Schießen': 4, 'Heimlichkeit': 6,
        'Überleben': 4, 'Provozieren': 6, 'Diebeskunst': 4,
    },
    'talente_novice': ['Eisenkiefer', 'Gassenwissen'],
    'powers': [],
    'gear': [('Pistole', 1), ('Kamera (normal)', 1), ('Taschenlampe (10" Strahl)', 1),
               ('Handschellen', 1), ('Dietriche', 1)],

    'advances': [
        ('skill', 'Fahren', 4),
        ('skill', 'Kämpfen', 6),
        ('skill', 'Allgemeinwissen', 6),
        ('skill', 'Überleben', 4),
        ('talent', 'Gassenwissen'),  # already at novice
        ('talent', 'Eisenkiefer'),  # already at novice
    ],
}

# --- LIBRARIAN (Human) ---
librarian = {
    'volk': 'Mensch',
    'freies_attribut': 'Verstand',
    'freies_talent': 'Gelehrter',
    'handicaps': ['Tollpatschig', 'Sanftmütig', 'Tick'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 10, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {
        'Geisteswissenschaften': 8, 'Athletik': 4, 'Allgemeinwissen': 6,
        'Wahrnehmung': 8, 'Okkultismus': 8, 'Überreden': 6,
        'Recherche': 8, 'Heimlichkeit': 6,
    },
    'talente_novice': ['Mut', 'Ermittler'],
    'powers': [],
    'gear': [('Kevlarweste', 1), ('Rucksack', 1)],

    'advances': [
        ('attribute', 'Willenskraft', 8),
        ('talent', 'Mut'),  # already at novice
        ('talent', 'Ermittler'),  # already at novice
        ('talent', 'Alleskönner'),
    ],
}

# --- MAGICIAN (Human) ---
magician = {
    'volk': 'Mensch',
    'freies_attribut': 'Willenskraft',
    'freies_talent': 'AH (Medium)',
    'handicaps': ['Geheimnis_schwer', 'Tick', 'Dünnhäutig'],
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {
        'Athletik': 6, 'Allgemeinwissen': 4, 'Kämpfen': 4, 'Einschüchtern': 4,
        'Wahrnehmung': 4, 'Okkultismus': 4, 'Darbietung': 8,
        'Überreden': 6, 'Zaubern': 6, 'Heimlichkeit': 8, 'Diebeskunst': 6,
    },
    'talente_novice': ['Elan', 'Bekannt', 'Geisterfreund'],
    'powers': ['Bannung', 'Arkanes entdecken/verbergen', 'Empathie'],
    'gear': [('Silberdolch', 1), ('Kerze', 1), ('Taschenlampe (10" Strahl)', 1),
               ('Kleidung, Alltag', 1), ('Salz (5kg Sack)', 1)],

    'advances': [
        ('attribute', 'Geschicklichkeit', 8),
        ('skill', 'Überreden', 8),
        ('skill', 'Heimlichkeit', 8),
        ('talent', 'Bekannt'),  # already at novice
        ('talent', 'Elan'),  # already at novice
    ],
}

# --- SURVIVOR (Human) ---
survivor = {
    'volk': 'Mensch',
    'freies_attribut': 'Willenskraft',
    'freies_talent': 'Mut',
    'handicaps': ['Heldenhaft', 'Loyal', 'Misstrauisch_leicht'],
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {
        'Athletik': 6, 'Allgemeinwissen': 4, 'Fahren': 4, 'Kämpfen': 8,
        'Wahrnehmung': 6, 'Überreden': 6, 'Schießen': 6,
        'Heimlichkeit': 6, 'Überleben': 6, 'Provozieren': 6,
    },
    'talente_novice': ['Scream Queen/King', 'Sehr Attraktiv'],
    'powers': [],
    'gear': [('Schrotflinte', 1), ('Kevlarweste', 1), ('Taschenlampe (10" Strahl)', 1)],

    'advances': [
        ('talent', 'Scream Queen/King'),  # already at novice
        ('skill', 'Kämpfen', 8),
        ('skill', 'Schießen', 6),
        ('talent', 'Mut'),  # already at novice
        ('attribute', 'Stärke', 6),
    ],
}


# ========================================================================
# MONSTROUS ARCHETYPES — korrigiert mit korrektem Volk + Auto-Eintraegen
# ========================================================================

# --- ANGEL (Engel) ---
# Engel auto_handicaps: ['Schwur', 'Auffällig'] -> 'Schwur_schwer' entfernt
# Engel auto_talente: ['Flug'] (nicht manuell)
# Engel attribute_bonuses: {Stärke: 2, Konstitution: 2}
angel_data = {
    'volk': 'Engel',
    'handicaps': ['Arrogant', 'Eifersüchtig', 'Rachsüchtig_leicht'],  # 'Schwur_schwer' ENTFERNT (auto)
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 10, 'Konstitution': 10},
    'fertigkeiten': {
        'Athletik': 6, 'Allgemeinwissen': 4, 'Glaube': 6, 'Kämpfen': 8,
        'Heilen': 6, 'Einschüchtern': 6, 'Wahrnehmung': 6,
        'Okkultismus': 6, 'Darbietung': 4, 'Überreden': 4, 'Heimlichkeit': 6,
    },
    'talente_novice': ['Attraktiv', 'Starker Wille'],
    'powers': [],
    'monstrous_powers': ['Ageless', 'Beautify', 'Flight Pace 12', 'Immune to Disease and Poison',
                          'Wing Strike (Str+d8, Reach 2)'],
    'gear': [('Taschenlampe (10" Strahl)', 1), ('Feuerzeug', 1)],
    'advances': [
        ('attribute', 'Geschicklichkeit', 8),
        ('skill', 'Kämpfen', 8), ('skill', 'Einschüchtern', 8),
        ('talent', 'Rundumschlag'),
        ('talent', None),  # Wing Strike - MISSING
    ],
}

# --- DEMON (Dämon) ---
# Dämon auto_handicaps: ['Böse', 'Schwäche (Geweihtes Wasser)'] -> keine Ueberschneidung
# Dämon auto_talente: ['Infrarotsicht'] -> nicht manuell
demon_data = {
    'volk': 'D\u00e4mon',
    'handicaps': ['Gierig_leicht', 'Skrupellos', 'Beschämt'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 8},
    'fertigkeiten': {
        'Athletik': 6, 'Allgemeinwissen': 4, 'Kämpfen': 6, 'Glücksspiel': 4,
        'Einschüchtern': 4, 'Wahrnehmung': 4, 'Okkultismus': 6,
        'Überreden': 8, 'Schießen': 4, 'Heimlichkeit': 6,
        'Provozieren': 8, 'Diebeskunst': 6,
    },
    'talente_novice': ['Attraktiv', 'Beziehungen'],
    'powers': [],
    'monstrous_powers': ['Ageless', 'Bespoil', 'Darkvision', 'Deal Maker',
                          'Claws (Str+d4)', 'Mystic Powers (Demon) Tempter'],
    'gear': [('Kleidung, Alltag', 1)],
    'advances': [
        ('talent', None),  # Claws - MISSING
        ('skill', 'Überreden', 8), ('skill', 'Diebeskunst', 6),
        ('talent', 'Beziehungen'),
        ('talent', 'Mystische Kräfte'),
    ],
}

# --- PATCHWORK MAN (Flickenmonster) ---
# Flickenmonster auto_handicaps: ['Hässlich', 'Außenseiter', 'Schwerfällig',
#   'Schwäche (Feuer)', 'Schwäche (Elektrizität)'] -> 'Schwäche (Feuer)' entfernt
# Flickenmonster auto_talente: ['Zäh', 'Kräftig'] -> 'Kräftig' entfernt
# Flickenmonster attribute_bonuses: {Stärke: 2, Konstitution: 2}
patchwork_data = {
    'volk': 'Flickenmonster',
    'handicaps': ['Verpeilt', 'Phobie_schwer', 'Schreihals_leicht',
                  'Rachsüchtig_schwer'],  # 'Schwäche (Feuer)' ENTFERNT (auto), None fuer Loyal entfernt
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 4, 'Willenskraft': 6, 'Stärke': 12, 'Konstitution': 12},
    'fertigkeiten': {
        'Athletik': 8, 'Allgemeinwissen': 4, 'Kämpfen': 8, 'Einschüchtern': 6,
        'Wahrnehmung': 4, 'Überreden': 4, 'Reparieren': 4,
        'Heimlichkeit': 4, 'Überleben': 4, 'Verrückte Wissenschaft': 4,
    },
    'talente_novice': ['Arkane Resistenz', 'Berserker', 'Mut'],  # 'Kräftig' ENTFERNT (auto)
    'powers': [],
    'monstrous_powers': ['Ageless', 'Parts', 'Undead (+2 Toughness, +2 recover Shaken)'],
    'gear': [('Kevlarweste', 1)],
    'advances': [
        ('talent', 'Raufbold'),
        ('talent', 'Eisenkiefer'),
        ('talent', 'Mut'),
        ('talent', 'Wildheit'),
    ],
}

# --- MUMMY (Mumie) ---
# Mumie auto_handicaps: ['Hässlich', 'Langsam', 'Schwäche (Feuer)'] -> beide entfernt
# Mumie auto_talente: ['Zäh'] -> nicht manuell
mummy_data = {
    'volk': 'Mumie',
    'handicaps': ['Schwerfällig', 'Zögerlich', 'Materialkomponenten_schwer',
                  'Schwerzüngig'],  # 'Langsam_leicht' + 'Schwäche (Feuer)' ENTFERNT (auto)
    'attribute': {'Geschicklichkeit': 4, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 10, 'Konstitution': 10},
    'fertigkeiten': {
        'Geisteswissenschaften': 4, 'Athletik': 8, 'Allgemeinwissen': 4,
        'Kämpfen': 4, 'Heilen': 6, 'Wahrnehmung': 4,
        'Okkultismus': 6, 'Überreden': 4, 'Recherche': 8, 'Heimlichkeit': 4,
        'Alchemie': 8,
    },
    'talente_novice': ['AH (Alchemist, Horror)', 'Rohling'],
    'powers': ['Eigenschaft erhöhen/senken', 'Heilung', 'Schutz', 'Flächenschlag', 'Schlummer'],
    'monstrous_powers': ['Ageless'],
    'gear': [('Robe (dünn)', 1)],
    'advances': [
        ('attribute', 'Willenskraft', 8),
        ('talent', 'Machtpunkte'),
        ('talent', None),  # Old - MISSING
        ('talent', 'Neue Mächte'),
        ('power', 'Flächenschlag'),
        ('power', 'Schlummer'),
    ],
}

# --- REVENANT (Wiedergänger) ---
# Wiedergänger auto_handicaps: ['Schwur', 'Hässlich'] -> 'Schwur_schwer' entfernt
# Wiedergänger auto_talente: ['Zäh'] -> nicht manuell
revenant_data = {
    'volk': 'Wiederg\u00e4nger',
    'handicaps': ['Blutrünstig', 'Skrupellos', 'Stur'],  # 'Schwur_schwer' ENTFERNT (auto)
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 10},
    'fertigkeiten': {
        'Athletik': 6, 'Allgemeinwissen': 4, 'Fahren': 4, 'Kämpfen': 8,
        'Einschüchtern': 8, 'Wahrnehmung': 6, 'Okkultismus': 4,
        'Überreden': 4, 'Schießen': 8, 'Heimlichkeit': 6,
    },
    'talente_novice': ['Bedrohlich'],
    'powers': [],
    'monstrous_powers': ['Ageless', 'Hardy', 'Regeneration (slow)', 'Undead'],
    'gear': [('Taser', 1), ('Kleidung, Alltag', 1), ('Taschenlampe (10" Strahl)', 1)],
    'advances': [
        ('talent', 'Schmerzresistenz'),
        ('talent', 'Schnell'),
        ('skill', 'Wahrnehmung', 6), ('skill', 'Heimlichkeit', 6),
        ('talent', 'Seelenentzug'),
    ],
}

# --- PHANTOM ---
# Phantom auto_handicaps: ['Schwäche (Salz)'] -> entfernt
# Phantom auto_talente: ['Flug'] -> nicht manuell
phantom_data = {
    'volk': 'Phantom',
    'handicaps': ['Große Klappe', 'Neugierig', 'Düsternis_leicht'],  # 'Schwäche (Salz)' ENTFERNT (auto)
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 10, 'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {
        'Athletik': 4, 'Allgemeinwissen': 4, 'Kämpfen': 4, 'Einschüchtern': 8,
        'Wahrnehmung': 6, 'Okkultismus': 4, 'Überreden': 4,
        'Recherche': 4, 'Schießen': 6, 'Heimlichkeit': 8,
        'Provozieren': 8, 'Diebeskunst': 6,
    },
    'talente_novice': ['Galgenhumor'],
    'powers': [],
    'monstrous_powers': ['Ageless', 'Darkvision', "Doesn't Breathe", 'Ethereal'],
    'gear': [('Kleidung, Alltag', 1)],
    'advances': [
        ('talent', None),  # Bolster - MISSING
        ('skill', 'Einschüchtern', 8), ('skill', 'Schießen', 6),
        ('skill', 'Wahrnehmung', 6), ('skill', 'Heimlichkeit', 8),
        ('talent', None),  # Invisibility - MISSING
    ],
}

# --- VAMPIRE (Vampir) ---
# Vampir auto_handicaps: ['Schwäche (Sonnenlicht)', 'Schwäche (Pfahl)',
#   'Abhängigkeit (Blut)', 'Schwäche (Geweihtes Wasser)'] -> alle 3 entfernt
# Vampir auto_talente: ['Nachtsicht', 'Zäh'] -> nicht manuell
# Vampir attribute_bonuses: {Stärke: 2}
vampire_data = {
    'volk': 'Vampir',
    'handicaps': ['Arrogant', 'Blutrünstig', 'Angewohnheit_schwer'],
    # 'Schwäche (Geweihtes Wasser)', 'Schwäche (Sonnenlicht)', 'Schwäche (Pfahl)' ENTFERNT (auto)
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 12, 'Konstitution': 10},  # Willenskraft 8->6 (Bogen: Spirit d6, Audit 2026-06-04)
    'fertigkeiten': {
        'Athletik': 8, 'Allgemeinwissen': 6, 'Kämpfen': 8, 'Einschüchtern': 6,
        'Wahrnehmung': 6, 'Okkultismus': 6, 'Überreden': 6, 'Heimlichkeit': 8,
    },
    'talente_novice': ['Attraktiv'],
    'powers': [],
    'monstrous_powers': ['Ageless', 'Bite (Str+d4)', 'Darkvision', 'Undead',
                          'Charm (puppet)', 'Claws (Str+d6)'],
    'gear': [('Robe (dünn)', 1)],
    'advances': [
        ('attribute', 'Willenskraft', 8),
        ('skill', 'Einschüchtern', 8), ('skill', 'Überreden', 8),
        ('talent', None),  # Charm - MISSING
        ('talent', None),  # Claws - MISSING
    ],
}

# --- WEREWOLF ---
# Werwolf auto_handicaps: ['Blutdurst', 'Schwäche (Silber)'] -> keine Ueberschneidung (Nones)
# Werwolf auto_talente: ['Gestaltwandel', 'Infrarotsicht'] -> nicht manuell
werewolf_data = {
    'volk': 'Werwolf',
    'handicaps': ['Impulsiv', 'Loyal', 'Dünnhäutig'],
    # None-Eintraege (Cannot speak, Transformation, Weakness silver) komplett entfernt
    'attribute': {'Geschicklichkeit': 12, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 12, 'Konstitution': 12},
    'fertigkeiten': {
        'Athletik': 8, 'Allgemeinwissen': 4, 'Kämpfen': 8, 'Einschüchtern': 6,
        'Wahrnehmung': 6, 'Überreden': 4, 'Heimlichkeit': 6,
        'Überleben': 6, 'Diebeskunst': 4,
    },
    'talente_novice': ['Raufbold', 'Schnell'],
    'powers': [],
    'monstrous_powers': ['Bite/Claws (Str+d8, AP 2)', 'Infravision', 'Regeneration (slow)',
                          'Speed (+2 Pace, run die up)', 'Fleet-Footed (d10)'],
    'gear': [('Keule, Schwer', 1)],
    'advances': [
        ('talent', 'Flink'),
        ('attribute', 'Konstitution', 12),
        ('talent', 'Raufbold'),
        ('talent', 'Kampfreflexe'),
    ],
}

# --- SLAYER (Mensch + Superkraefte) ---
slayer_data = {
    'volk': 'Mensch',
    'freies_attribut': 'Willenskraft',
    'freies_talent': 'Scream Queen/King',
    'handicaps': ['Heldenhaft', 'Loyal', 'Misstrauisch_leicht'],
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 10, 'Stärke': 6, 'Konstitution': 8},
    'fertigkeiten': {
        'Athletik': 6, 'Allgemeinwissen': 4, 'Fahren': 4, 'Kämpfen': 8,
        'Wahrnehmung': 6, 'Okkultismus': 6, 'Überreden': 6,
        'Schießen': 8, 'Heimlichkeit': 8, 'Überleben': 4, 'Provozieren': 6,
    },
    'talente_novice': ['Assassine', 'Attraktiv', 'Block', 'Mut', 'Monsterjäger'],
    'powers': [],
    'monstrous_powers': ['Hardy', 'Gifts of the Night (13 pts)'],
    'gear': [('Kevlarweste', 1), ('Schrotflinte', 1), ('Kaltes-Eisen-Schwert', 1), ('Holzpfähle (5)', 1)],
    'advances': [
        ('talent', 'Scream Queen/King'),
        ('skill', 'Überreden', 6), ('skill', 'Okkultismus', 6),
        ('talent', 'Mut'),
        ('attribute', 'Verstand', 8),
    ],
}

# --- DEMONOLOGIST (Monstrous) (Mensch + Superkraefte) ---
demonologist_data = {
    'volk': 'Mensch',
    'freies_attribut': 'Verstand',
    'freies_talent': 'AH (Dämonologe)',
    'handicaps': ['Skrupellos', 'Dünnhäutig', 'Rachsüchtig_leicht'],
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 10, 'Willenskraft': 10, 'Stärke': 4, 'Konstitution': 8},
    'fertigkeiten': {
        'Athletik': 4, 'Allgemeinwissen': 6, 'Kämpfen': 4, 'Einschüchtern': 10,
        'Wahrnehmung': 6, 'Okkultismus': 10, 'Überreden': 4,
        'Recherche': 6, 'Zaubern': 10, 'Heimlichkeit': 6, 'Überleben': 4,
    },
    'talente_novice': ['Kanalisieren', 'Höllenfeuer', 'Bedrohlich'],
    'powers': ['Bannung', 'Strahl', 'Flächenschlag', 'Aufheben', 'Chaos', 'Kriegersegen', 'Verbündeten beschwören'],
    'monstrous_powers': ['Ageless (dark magic)', 'Gifts of the Night (14 pts)'],
    'gear': [('Silberdolch', 1)],
    'advances': [
        ('talent', 'Machtpunkte'),
        ('talent', 'Energieschub'),
        ('skill', 'Kämpfen', 4), ('skill', 'Einschüchtern', 10),
        ('talent', None),  # New Powers (blast, dispel) - MISSING
    ],
}

# --- SWAMP FREAK (Mensch + Superkraefte) ---
swamp_freak_data = {
    'volk': 'Mensch',
    'freies_attribut': 'Konstitution',
    'handicaps': ['Schwerfällig', 'Arm', 'Hässlich'],
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 4, 'Willenskraft': 8, 'Stärke': 10, 'Konstitution': 10},
    'fertigkeiten': {
        'Athletik': 6, 'Allgemeinwissen': 4, 'Kämpfen': 8, 'Heilen': 6,
        'Einschüchtern': 8, 'Wahrnehmung': 4, 'Okkultismus': 4,
        'Überreden': 4, 'Heimlichkeit': 8, 'Überleben': 6,
    },
    'talente_novice': ['Bedrohlich'],
    'powers': [],
    'monstrous_powers': ['Ageless', 'Aquatic', 'Armor +4', 'Claws', 'Gifts of the Night (6pts)',
                          'Hardy', 'Low Light Vision'],
    'gear': [('Kleidung, Alltag', 1)],
    'advances': [
        ('attribute', 'Geschicklichkeit', 8),
        ('skill', 'Kämpfen', 8), ('skill', 'Heimlichkeit', 8),
        ('talent', 'Heiler'),
        ('talent', 'Konter'),
    ],
}

# --- NEMESIS (Mensch + Superkraefte) ---
nemesis_data = {
    'volk': 'Mensch',
    'freies_attribut': 'Stärke',
    'freies_talent': None,
    'handicaps': ['Vorsichtig', 'Geheimnis_leicht', 'Schwur_schwer'],
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 10, 'Konstitution': 10},
    'fertigkeiten': {
        'Athletik': 8, 'Allgemeinwissen': 4, 'Fahren': 6, 'Kämpfen': 8,
        'Wahrnehmung': 6, 'Okkultismus': 6, 'Überreden': 4,
        'Schießen': 8, 'Heimlichkeit': 8, 'Überleben': 6,
    },
    'talente_novice': ['Block', 'Raufbold'],
    'powers': [],
    'monstrous_powers': ['Ageless', 'Gifts of the Night (13pts)', 'Heightened Smell',
                          'Fear (-2)'],
    'gear': [('Kevlarweste', 1), ('Gewehr', 1), ('Silberkugeln (10)', 1), ('Schwert, Kurzschwert', 1)],
    'advances': [
        ('talent', 'Erstschlag'),
        ('talent', 'Flink'),
        ('skill', 'Athletik', 8), ('skill', 'Okkultismus', 6),
        ('talent', 'Block'),
    ],
}


# ========================================================================
# MAIN
# ========================================================================
if __name__ == '__main__':
    m('=' * 60)
    m(f'BUILD START: Horror Kompendium ALL Archetypes')
    m(f'Time: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    m('=' * 60)

    # Human archetypes (full build)
    human_archetypes = [
        ('Ghost Hunter', ghost_hunter),
        ('Nerd', nerd),
        ('Jock', jock),
        ('Psychic', psychic),
        ('Exorcist', exorcist),
        ('Gamer', gamer),
        ('Party Animal', party_animal),
        ('Runner', runner),
        ('Witch', witch),
        ('Doctor', doctor),
        ('Occultist', occultist),
        ('Constable', constable),
        ('Journalist', journalist),
        ('Burglar', burglar),
        ('Aristocrat', aristocrat),
        ('Mambo', mambo),
        ('Sailor', sailor),
        ('Explorer', explorer),
        ('Soldier', soldier),
        ('Socialite', socialite),
        ('Gumshoe', gumshoe),
        ('Librarian', librarian),
        ('Magician', magician),
        ('Survivor', survivor),
    ]

    for name, data in human_archetypes:
        try:
            build_seasoned_direct(name, data)
        except Exception as e:
            m(f'BUILD CRASH {name}: {e}\n{traceback.format_exc()}')
            REPORT[name] = {'ok': False, 'error': str(e)}

    # Monstrous archetypes (partial build, korrigiert)
    monstrous_archetypes = [
        ('Angel', angel_data, False),                    # Engel Volk
        ('Demon', demon_data, False),                    # Dämon Volk
        ('Patchwork Man', patchwork_data, False),        # Flickenmonster Volk
        ('Mummy', mummy_data, False),                    # Mumie Volk
        ('Revenant', revenant_data, False),              # Wiedergänger Volk
        ('Phantom', phantom_data, False),                # Phantom Volk
        ('Vampire', vampire_data, False),                # Vampir Volk
        ('Werewolf', werewolf_data, False),              # Werwolf Volk
        ('Slayer', slayer_data, True),                   # Mensch + Superkraefte
        ('Demonologist (Monstrous)', demonologist_data, True),  # Mensch + Superkraefte
        ('Swamp Freak', swamp_freak_data, True),          # Mensch + Superkraefte
        ('Nemesis', nemesis_data, True),                  # Mensch + Superkraefte
    ]

    for name, data, has_sk in monstrous_archetypes:
        try:
            build_monstrous(name, data, has_superkraefte=has_sk)
        except Exception as e:
            m(f'BUILD CRASH {name}: {e}\n{traceback.format_exc()}')
            REPORT[name] = {'ok': False, 'error': str(e), 'monstrous': True}

    # Summary
    header('ZUSAMMENFASSUNG')
    ok_count = sum(1 for r in REPORT.values() if r.get('ok'))
    total = len(REPORT)
    m(f'Erfolgreich: {ok_count}/{total}')
    for name, r in sorted(REPORT.items()):
        status = 'OK' if r.get('ok') else ('SUPER' if r.get('superkraefte') else ('MONSTROeS' if r.get('monstrous') else 'FEHLER'))
        anom = r.get('anomalien', '?')
        err = r.get('error', '')
        diff = r.get('diff', [])
        m(f'  [{status}] {name}: anomalien={anom} diff={len(diff)} {err}')
        if diff:
            for d in diff[:3]:
                m(f'    - {d}')

    m(f'\nGesamtberichte in logs/horror_*_bericht.json')
    m(f'Trace-Log: logs/horror_all_trace.txt')
    ALLLOG.close()
    print(f'BUILD COMPLETE: {ok_count}/{total} successful')
