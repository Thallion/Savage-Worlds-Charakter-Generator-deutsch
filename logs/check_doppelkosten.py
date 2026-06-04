#!/usr/bin/env python3
"""
Prüfung: doppelt bezahlte Fertigkeitsschritte in den gespeicherten Archetyp-JSONs.

Sucht im steigerungs_journal jedes Char-JSON nach Schritten mit
  zahlungsquelle == "Fertigkeitspunkte"  und  kosten >= 2
(= Doppelkosten, weil die Fertigkeit ihr regierendes Attribut erreicht/übersteigt)
und klassifiziert sie mit dem SETTING-SPEZIFISCHEN Skill->Attribut-Mapping als:

  * INHÄRENT  – Skill-Endwert > Attribut-Endwert: der Bogen gibt Skill > Attribut vor,
                nicht vermeidbar ohne das Attribut ÜBER den Bogen zu heben.
  * VERMEIDBAR – Attribut-Endwert >= Skill-Wert beim Doppel-Schritt: das Attribut hätte
                (zumindest via Advance) VOR der Fertigkeit auf Ziel gebracht werden können
                -> Doppelkosten durch bessere Attribut-Reihenfolge / Deferral vermeidbar.

Aufruf:  python3 logs/check_doppelkosten.py
"""
import json, glob, os
from collections import defaultdict

def lade_mappings():
    """setting_name -> {fertigkeit: regierendes_attribut}"""
    maps = {}
    for s in glob.glob('settings/*.json'):
        try:
            dd = json.load(open(s, encoding='utf-8'))
        except Exception:
            continue
        fd = dd.get('fertigkeiten_daten', {})
        if isinstance(fd, dict) and fd:
            mp = {k: (v[0] if isinstance(v, list) and v else v) for k, v in fd.items()}
            # Unter mehreren Schlüsseln ablegen: name-Feld UND Dateiname (robust gegen
            # Bindestrich/Leerzeichen-Abweichungen, z.B. "Superkräfte-Kompendium")
            for key in {dd.get('name'), os.path.basename(s)[:-5]}:
                if key:
                    maps[key] = mp
    return maps

def attr_finalwerte(d):
    at = d.get('attribute'); af = {}
    if isinstance(at, list):
        for a in at:
            af[a.get('attribut_name')] = a.get('wuerfel', {}).get('value', a.get('wert'))
    elif isinstance(at, dict):
        for k, v in at.items():
            af[k] = v.get('value', v.get('wert')) if isinstance(v, dict) else v
    return af

def map_fuer_char(d, maps):
    """Robuste Auflösung des Skill->Attr-Mappings: active_setting_name, sonst Fuzzy."""
    setn = d.get('active_setting_name') or d.get('setting')
    if setn and setn in maps:
        return maps[setn]
    def norm(x):
        return x.replace(' ', '').replace('-', '').lower() if x else x
    if setn:
        for k in maps:
            if norm(k) == norm(setn):
                return maps[k]
    return None

def main():
    maps = lade_mappings()
    files = sorted(glob.glob('chars/Archetypen/Archetyp_*.json'))
    avoid = defaultdict(list); inherent = defaultdict(list); unresolved = []
    n_av = n_inh = 0
    for f in files:
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        sk2at = map_fuer_char(d, maps)
        af = attr_finalwerte(d)
        sj = d.get('steigerungs_journal')
        ce = sj.get('cost_entries', []) if isinstance(sj, dict) else []
        base = os.path.basename(f)
        for e in ce:
            if e.get('typ') == 'fertigkeit' and e.get('zahlungsquelle') == 'Fertigkeitspunkte' and e.get('kosten', 0) >= 2:
                sk = e['name']; V = e['wert']
                attr = sk2at.get(sk) if sk2at else None
                av = af.get(attr) if attr else None
                if attr is None or av is None:
                    unresolved.append(f"{base}: {sk}@{V} (Mapping/Attr unbekannt, Setting={d.get('active_setting_name')})")
                    continue
                eintrag = f"{sk}@{V} ({attr} final {av})"
                if av >= V:
                    avoid[base].append(eintrag); n_av += 1
                else:
                    inherent[base].append(eintrag); n_inh += 1
    print(f"Geprüfte Char-JSONs: {len(files)}")
    print(f"Doppelkosten gesamt: {n_av + n_inh}  |  VERMEIDBAR: {n_av}  |  INHÄRENT: {n_inh}")
    if avoid:
        print("\n=== VERMEIDBARE Doppelkosten (Fix lohnt) ===")
        for k, v in sorted(avoid.items()):
            print(f"  {k}: {', '.join(v)}")
    if unresolved:
        print("\n=== UNAUFGELÖST (Mapping prüfen) ===")
        for u in unresolved:
            print(f"  {u}")
    print(f"\n(INHÄRENT = Bogen gibt Skill > Attribut vor, nicht vermeidbar ohne Attribut über Bogen.)")
    print("(VERMEIDBAR = Attribut-Endwert >= Skillwert. ABER nur ein echter Fix, wenn das Attribut")
    print(" sein Ziel in CharGen erreichen kann — erreicht es das Ziel nur per Aufstieg, würde das")
    print(" Verschieben des Skill-Schritts auf einen Advance nur sonst ungenutzte Fertigkeitspunkte")
    print(" verschwenden. Erst prüfen, ob das Attribut in CharGen vorgezogen werden kann!)")

if __name__ == '__main__':
    main()
