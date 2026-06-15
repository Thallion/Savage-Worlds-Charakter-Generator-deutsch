# -*- coding: utf-8 -*-
"""
Gemeinsamer HP-Ökonomie-Helfer für ALLE Archetyp-Builds (KEIN separates nachgelagertes Skript —
die Build-Skripte importieren und rufen `verbrauche_hp(jsonpath)` als LETZTEN Schritt auf).

Zweck: ungenutzte **Handicap-Punkte** (und Rest-Attribut-/Fertigkeitspunkte) auf per **Aufstieg**
finanzierte Attribut-/Fertigkeitssteigerungen UMBUCHEN. Anders als die Phase-0-Lückenfüllung in
fill_budget/_seasoned konvertiert das auch Schritte, die der Build bereits per Aufstieg gesetzt hat
(keine „Lücke" mehr). Reine JSON-/Journal-Buchhaltung — Würfelwerte werden NIE verändert.

Mechanik (s. [[handicap-punkte-oekonomie-optimizer]]): Das `steigerungs_journal` hält pro Schritt
die Finanzierungsquelle. Eine 'Aufstiege'-Steigerung wird auf 'Attributspunkte'/'Fertigkeitspunkte'/
'Handicap-Punkte' umgebucht, der jeweilige freie Pool dekrementiert und `aufstiege_gesamt` um die
Aufstiegskosten gesenkt (verbleibende_aufstiege bleibt → ausgegebene Aufstiege sinken).

Kosten je Schritt: Attribut 1 Aufstieg ⇔ 1 Attributpunkt ODER 2 HP; Fertigkeit einfach 0,5 Aufstieg
⇔ 1 Fertigkeitspunkt ODER 1 HP; Fertigkeit doppelt 1 Aufstieg ⇔ 2 Fertigkeitspunkte ODER 2 HP.
(Das im Journal gespeicherte 'kosten' der 'Aufstiege'-Fertigkeit kodiert einfach/doppelt bereits.)

Talent-Aufstiege (Edges) bleiben unangetastet: viele haben Rang-Voraussetzungen, eine Umbuchung in
die Chargen (2 HP) wäre regelwidrig → separater, rang-geprüfter Schritt (hier NICHT enthalten).
"""
import json

RANG_MAPPING = [(0, 4, "Anfänger"), (4, 8, "Fortgeschritten"), (8, 12, "Veteran"),
                (12, 16, "Heroisch"), (16, 100, "Legendär")]


def _rang(ausgegebene):
    for lo, hi, name in RANG_MAPPING:
        if lo <= ausgegebene < hi:
            return name
    return "Unbekannter Rang"


def _cost_entries(d):
    j = d.get('steigerungs_journal')
    if isinstance(j, dict):
        return j.get('cost_entries', [])
    if isinstance(j, list):
        return j
    return []


_SETTING_TALENTE = {}


def _edge_rang(setting, name):
    """Rang-Voraussetzung eines Edges aus dem Setting-JSON ('A'=Anfänger, 'F'=Fortgeschritten …).
    None, wenn unbekannt. Gecacht."""
    if setting not in _SETTING_TALENTE:
        try:
            _SETTING_TALENTE[setting] = json.load(
                open(f'settings/{setting}.json', encoding='utf-8')).get('talente', {}) or {}
        except Exception:
            _SETTING_TALENTE[setting] = {}
    t = _SETTING_TALENTE[setting].get(name)
    return t.get('rang') if isinstance(t, dict) else None


def konvertierbar(d):
    """Nicht-mutierend: True, wenn der Char ungenutzte Handicap-Punkte hat, die sich regelkonform
    auf einen per Aufstieg finanzierten Schritt umbuchen ließen (Skill/Attribut ODER Anfänger-Edge).
    Dient dem Status-Bericht, um „echten" HP-Rest (Bug) von legitimem (Seasoned-Edge/keine Aufstiege/
    1-HP-Rest) zu trennen."""
    hp = d.get('verbleibende_handicap_punkte', 0) or 0
    if hp < 1:
        return False
    setting = d.get('active_setting_name') or ''
    for e in _cost_entries(d):
        if e.get('zahlungsquelle') != 'Aufstiege':
            continue
        typ = e.get('typ')
        if typ == 'attribut' and hp >= 2:
            return True
        if typ == 'fertigkeit' and hp >= int(round((e.get('kosten', 0.5) or 0.5) * 2)):
            return True
        if typ == 'talent' and hp >= 2 and _edge_rang(setting, e.get('name')) in ('A', 'Anfänger', None):
            return True
    return False


def verbrauche_hp(jsonpath, pin_rang=False, edges=False):
    """Bucht im gespeicherten Char Aufstiege auf freie Chargen-Währung um. Mutiert die Datei.
    pin_rang=True: reduziert Aufstiege nur soweit, dass der aktuelle Rang erhalten bleibt
    (für Seasoned-Karten, die nicht auf Anfänger fallen sollen).
    edges=True: bucht zusätzlich per Aufstieg gekaufte ANFÄNGER-Edges ('A') auf je 2 Handicap-
    Punkte um (Voraussetzungen werden — wie in den Builds — ignoriert; Rang 'A' bleibt aber
    Pflicht, da Seasoned-Edges nicht chargen-finanzierbar sind). Standard aus, weil das Seasoned-
    Karten an der Rang-Grenze auf Anfänger fallen lassen kann.
    Gibt ein Report-Dict zurück oder None, wenn nichts umgebucht wurde."""
    d = json.load(open(jsonpath, encoding='utf-8'))
    setting = d.get('active_setting_name') or ''
    ce = _cost_entries(d)
    attr_pts = d.get('verbleibende_attributsteigerungen', 0) or 0
    fert_pts = d.get('verbleibende_fertigkeitssteigerungen', 0) or 0
    hp = d.get('verbleibende_handicap_punkte', 0) or 0
    attr0, fert0, hp0 = attr_pts, fert_pts, hp
    g0 = d.get('aufstiege_gesamt', 0) or 0
    v = d.get('verbleibende_aufstiege', 0) or 0
    rang0 = d.get('rang')
    spent0 = round(g0 - v, 2)
    # Rang-Untergrenze (Anzahl ausgegebener Aufstiege), wenn pin_rang
    min_spent = 0
    if pin_rang:
        for lo, hi, name in RANG_MAPPING:
            if name == rang0:
                min_spent = lo
                break
    freed, schritte = 0.0, []

    def darf_frei(adv_kosten):
        return (not pin_rang) or (round(spent0 - (freed + adv_kosten), 2) >= min_spent)

    # 1) Attributschritte: Attributpunkte (1) zuerst, sonst 2 Handicap-Punkte.
    for e in ce:
        if e.get('typ') != 'attribut' or e.get('zahlungsquelle') != 'Aufstiege' or 'wert' not in e:
            continue
        if not darf_frei(1):
            continue
        if attr_pts >= 1:
            attr_pts -= 1; e['zahlungsquelle'] = 'Attributspunkte'; e['kosten'] = 1
        elif hp >= 2:
            hp -= 2; e['zahlungsquelle'] = 'Handicap-Punkte'; e['kosten'] = 2
        else:
            continue
        freed += 1
        schritte.append(f"{e['name']}(attr d{e['wert']}) -1A")

    # 2) Fertigkeitsschritte: Chargenkosten = Aufstiegskosten×2 (1 einfach / 2 doppelt);
    #    Fertigkeitspunkte zuerst, sonst Handicap-Punkte.
    for e in ce:
        if e.get('typ') != 'fertigkeit' or e.get('zahlungsquelle') != 'Aufstiege' or 'wert' not in e:
            continue
        adv = e.get('kosten', 0.5) or 0.5
        if not darf_frei(adv):
            continue
        need = int(round(adv * 2))
        if fert_pts >= need:
            fert_pts -= need; e['zahlungsquelle'] = 'Fertigkeitspunkte'; e['kosten'] = need
        elif hp >= need:
            hp -= need; e['zahlungsquelle'] = 'Handicap-Punkte'; e['kosten'] = need
        else:
            continue
        freed += adv
        schritte.append(f"{e['name']}(fert d{e['wert']}) -{adv}A")

    # 3) Edges (Talent-Aufstiege): nur Anfänger-Edges ('A') auf 2 Handicap-Punkte umbuchen.
    if edges:
        for e in ce:
            if e.get('typ') != 'talent' or e.get('zahlungsquelle') != 'Aufstiege':
                continue
            rg = _edge_rang(setting, e.get('name'))
            if rg not in ('A', 'Anfänger', None):   # Seasoned+ Edge -> nicht chargen-fähig
                continue
            if not darf_frei(1) or hp < 2:
                continue
            hp -= 2; e['zahlungsquelle'] = 'Handicap-Punkte'; e['kosten'] = 2
            freed += 1
            schritte.append(f"{e['name']}(edge) -1A")

    if freed <= 0:
        return None

    g1 = round(g0 - freed, 2)
    d['aufstiege_gesamt'] = g1
    d['verbleibende_attributsteigerungen'] = attr_pts
    d['verbleibende_fertigkeitssteigerungen'] = fert_pts
    d['verbleibende_handicap_punkte'] = hp
    spent1 = round(g1 - v, 2)
    d['rang'] = _rang(spent1)
    with open(jsonpath, 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=4)

    return {'freed': round(freed, 2), 'hp': f"{hp0}->{hp}", 'attr': f"{attr0}->{attr_pts}",
            'fert': f"{fert0}->{fert_pts}", 'aufst': f"{spent0}->{spent1}",
            'rang': f"{rang0}->{d['rang']}" if rang0 != d['rang'] else d['rang'], 'schritte': schritte}
