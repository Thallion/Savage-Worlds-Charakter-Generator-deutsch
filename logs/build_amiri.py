# -*- coding: utf-8 -*-
"""Rebuild Amiri (Barbarin, Savage Pathfinder, ANFÄNGER) wie ein User über den Controller.
Bogen-SOLL aus dem deutschen Grundregelwerk + Iconic-Sheet (vom User geliefert).
Root-Cause des committed Builds: 3 Handicaps + Mensch-Frei-Attribut fehlten -> Attribute/
Fertigkeiten unterfinanziert, Ausrüstung leer."""
import sys, os, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
sys.path.insert(0, os.path.abspath('.'))
import driver as d

tlog = open('logs/amiri_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x) + '\n'); tlog.flush()

soll = {
    'attribute':   {'Geschicklichkeit': 8, 'Konstitution': 8, 'Stärke': 10,
                    'Verstand': 4, 'Willenskraft': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 6,
                     'Heimlichkeit': 4, 'Kämpfen': 8, 'Reiten': 4, 'Schießen': 6,
                     'Überleben': 4, 'Überreden': 4, 'Wahrnehmung': 6},
    # manuell: Blutrünstig(2), Lebensaufgabe(1), Arm(1)  + auto Rüstungsbeschränkung_mittelschwer (Barbar)
    'handicaps':   ['Blutrünstig', 'Lebensaufgabe', 'Arm', 'Rüstungsbeschränkung_mittelschwer'],
    # Barbar(class) + Rohling(Mensch frei) + auto Berserker/Behände/Kampfrausch (Barbar)
    'talente':     ['Barbar', 'Rohling', 'Berserker', 'Behände', 'Kampfrausch'],
    'maechte':     [],
}
manual_handicaps = ['Blutrünstig', 'Lebensaufgabe', 'Arm']   # major zuerst

try:
    s = d.Sitzung('Savage Pathfinder', 'Barbarin_Amiri',
                  protokoll='logs/amiri_log.txt')
    vor = s.zustand()
    # 1 Klassentalent
    s.pathfinder_klassentalent('Barbar', ignore_voraussetzungen=True)
    m('Auto nach Klassentalent: ' + str(s.zeige_auto_eintraege(vor)))
    # 2 Handicaps (major zuerst)
    for h in manual_handicaps:
        r = s.handicap(h); m(f'handicap({h}): ok={r.get("ok")} kosten={r.get("kosten")}')
    # 3 Volk
    s.volk('Mensch')
    m('Volkswahlen: ' + str(s.volk_wahlmoeglichkeiten('Mensch')))
    # 4 Mensch: freies Talent + freies Attribut (Anpassungsfähigkeit)
    r = s.volk_freies_talent('Mensch', 'Rohling', ignore_voraussetzungen=True)
    m(f'freies_talent(Rohling): ok={r.get("ok")}')
    r = s.volk_freies_attribut('Mensch', 'Stärke')
    m(f'freies_attribut(Stärke): ok={r.get("ok")}')
    # 5 Attribute komplett (regulär dann HP) VOR Fertigkeiten
    for a, z in soll['attribute'].items():
        s.attribut_auf(a, z)
    for a, z in soll['attribute'].items():
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte > 0:
            vv = s.ch.attribute[a].wuerfel.value
            s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value == vv: break
    m('Nach Attributen: ' + str(s.punktestand()))
    m('  Attr-Ist: ' + str({a: s.ch.attribute[a].wuerfel.value for a in soll['attribute']}))
    # 6 Fertigkeiten
    for f, z in soll['fertigkeiten'].items():
        if f in s.ch.fertigkeiten:
            s.fertigkeit_auf(f, z)
        else:
            s.notiz(f'FERTIGKEIT-KEY fehlt: {f}')
    m('Nach Fertigkeiten: ' + str(s.punktestand()))
    m('  Fert-Ist: ' + str({f: (s.ch.fertigkeiten[f].wuerfel.value, s.ch.fertigkeiten[f].wuerfel.modifier) for f in soll['fertigkeiten'] if f in s.ch.fertigkeiten}))
    # 7 Talente (nur nicht-auto)
    for t in soll['talente']:
        if t not in s.ch.selected_talente:
            r = s.talent(t, ignore_voraussetzungen=True)
            m(f'talent({t}): ok={r.get("ok")}')
    # 8 (keine Mächte)
    # 9 Ausrüstung
    gear = [('Bastardschwert', 1), ('Handaxt', 1), ('Kurzbogen', 1),
            ('Pfeile (20)', 1), ('Ledertunika', 1), ('Lederbeinlinge', 1),
            ('Abenteurerausrüstung', 1)]
    for name, anz in gear:
        if name in s.ch.ausruestung:
            r = s.kaufen(name, anz); m(f'kaufen({name}): ok={r.get("ok")} verm={r.get("vermoegen")}')
        else:
            s.notiz(f'FEHLT im Katalog: {name}'); m(f'FEHLT im Katalog: {name}')
    s.notiz('Bogen: "beschlagene Ledertunika und -beinlinge (+2)" — beschlagene/studded Variante nicht im Katalog, Standard-Leder verwendet')
    # 10 Restabgleich
    m('Restpunkte: ' + str(s.punktestand()))
    diff = s.diff(soll)
    m('DIFF: ' + str(diff['abweichungen']))
    # Finalisieren wie die anderen Ikonen (Anfänger, 0 Aufstiege)
    from functions.character_advancement import update_rang
    s.ch.char_gen_completed = True
    update_rang(s.ch)
    m(f'finalisiert: cg=True rang={s.ch.rang}')
    s.speichern('chars/Archetypen/Archetyp_Savage_Pathfinder_Barbarin_Amiri_A.json')
    b = s.bericht('logs/amiri_bericht.json')
    m('FERTIG anomalien=%d' % b['anomalien_anzahl'])
except BaseException as e:
    m('CRASH: %r\n%s' % (e, traceback.format_exc()))
tlog.close()
