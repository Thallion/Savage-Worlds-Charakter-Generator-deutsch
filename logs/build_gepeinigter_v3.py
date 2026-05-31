import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/gepeinigter_v3_trace.txt', 'w', encoding='utf-8')
def m(x):
    tlog.write(str(x)+'\n')
    tlog.flush()

soll = {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 8,
                     'Stärke': 6, 'Konstitution': 8},
    'fertigkeiten': {'Athletik': 6, 'Heimlichkeit': 6, 'Einschüchtern': 8,
                     'Schießen': 8, 'Kämpfen': 6, 'Reiten': 6, 'Provozieren': 6,
                     'Okkultismus': 4, 'Allgemeinwissen': 4, 'Überreden': 4,
                     'Wahrnehmung': 4},
    'handicaps':    ['Fies (leicht)', 'Rachsüchtig (schwer)', 'Skrupellos (leicht)'],
    'talente':      ['Gepeinigt', 'Flicken', 'Killerinstinkt',
                     'Übernatürliches Attribut (Geschicklichkeit)'],
    'maechte':      [],
}

manual_handicaps = ['Rachsüchtig (schwer)', 'Fies (leicht)', 'Skrupellos (leicht)']

try:
    s = d.Sitzung('Deadlands', 'Gepeinigter', protokoll='logs/gepeinigter_v3.log')

    vor = s.zustand()

    # CharGen abschließen und 4 Aufstiege geben (Rang Fortgeschritten)
    s.ch.char_gen_completed = True
    for _ in range(4):
        increase_aufstiege(s.ch)
    m(f"CharGen abgeschlossen: Rang={s.ch.rang}, Aufstiege={s.ch.verbleibende_aufstiege}")

    # Handicaps (Major zuerst)
    for h in manual_handicaps:
        s.handicap(h)
    m(f"Handicaps done: {s.punktestand()}")
    m(f"Auto-Eintraege: {s.zeige_auto_eintraege(vor)}")

    # Volk
    s.volk('Mensch')
    m(f"Volkswahlen: {s.volk_wahlmoeglichkeiten('Mensch')}")

    # Flicken ALS FREIES VOLKSTALENT (kostenlos, nicht nochmal per talent()!)
    s.volk_freies_talent('Mensch', 'Flicken', ignore_voraussetzungen=True)
    m(f"Flicken via volk_freies_talent: selected={s.ch.selected_talente}")
    sys.stderr.write(f"DEBUG: Start Attribute-Loop\n")
    sys.stderr.flush()

    # Attribute VOR Fertigkeiten (regulaer + HC-Punkte)
    ziel_attribute = {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 8,
                      'Stärke': 6, 'Konstitution': 8}

    for a, z in ziel_attribute.items():
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_attributsteigerungen > 0:
            r = s.attribut(a)
            sys.stderr.write(f"DEBUG attribut({a}): val={s.ch.attribute[a].wuerfel.value} pts={s.ch.verbleibende_attributsteigerungen}\n")
            sys.stderr.flush()
            if not r or not r.get('ok'):
                sys.stderr.write(f"DEBUG attribut({a}) fehlgeschlagen, breche ab\n")
                break

    for a, z in ziel_attribute.items():
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte > 0:
            s.steigere_mit_handicap_attribut(a)

    m(f"Nach Attributen: {s.punktestand()}")

    # Gepeinigt waehlen (Voraussetzung fuer Ubernatuerliches Attribut)
    geo = s.talent('Gepeinigt', ignore_voraussetzungen=True)
    m(f"Gepeinigt: ok={geo.get('ok')}, kosten={geo.get('kosten')}")
    m(f"HP nach Gepeinigt: {s.ch.verbleibende_handicap_punkte}")

    # Ubernatuerliches Attribut per Aufstieg
    r = s.talent_mit_aufstieg('Übernatürliches Attribut (Geschicklichkeit)')
    m(f"UbernAtt via Aufstieg: ok={r.get('ok') if isinstance(r, dict) else True}, Aufstiege={s.ch.verbleibende_aufstiege}")

    # Killerinstinkt per Aufstieg
    r = s.talent_mit_aufstieg('Killerinstinkt')
    m(f"Killerinstinkt via Aufstieg: ok={r.get('ok') if isinstance(r, dict) else True}, Aufstiege={s.ch.verbleibende_aufstiege}")

    m(f"Punktestand vor Fertigkeiten: {s.punktestand()}")
    m(f"Selected Talente: {s.ch.selected_talente}")

    # Fertigkeiten
    fertigkeits_ziele = {
        'Athletik': 6, 'Heimlichkeit': 6, 'Einschüchtern': 8,
        'Schießen': 8, 'Kämpfen': 6, 'Reiten': 6, 'Provozieren': 6,
        'Okkultismus': 4, 'Allgemeinwissen': 4, 'Überreden': 4,
        'Wahrnehmung': 4
    }

    for f, z in fertigkeits_ziele.items():
        if f in s.ch.fertigkeiten:
            fert = s.ch.fertigkeiten[f]
            # Aktiviere zuerst untrainierte Fertigkeiten (modifier -2 -> 0)
            if fert.wuerfel.modifier < 0:
                if s.ch.verbleibende_fertigkeitssteigerungen > 0:
                    s.fertigkeit(f)
                elif s.ch.verbleibende_handicap_punkte > 0:
                    s.steigere_mit_handicap_fertigkeit(f)
                elif s.ch.verbleibende_aufstiege >= 0.5:
                    s.fertigkeit_mit_aufstieg(f)
            # Dann bis Zielwert steigern
            while fert.wuerfel.value < z:
                vor_val = fert.wuerfel.value
                if s.ch.verbleibende_fertigkeitssteigerungen > 0:
                    s.fertigkeit(f)
                elif s.ch.verbleibende_handicap_punkte > 0:
                    s.steigere_mit_handicap_fertigkeit(f)
                elif s.ch.verbleibende_aufstiege >= 0.5:
                    s.fertigkeit_mit_aufstieg(f)
                else:
                    m(f"  {f} kann nicht weiter gesteigert werden (Punkte=0)")
                    break
                if fert.wuerfel.value == vor_val:
                    m(f"  {f} keine Aenderung, abbrechen")
                    break
        else:
            s.notiz(f'FERTIGKEIT-KEY fehlt im Setting: {f}')

    m(f"Nach Fertigkeiten: {s.punktestand()}")

    # Finale Attribut-Pruefung
    m(f"Finale Attribute:")
    for a in ['Geschicklichkeit', 'Verstand', 'Willenskraft', 'Stärke', 'Konstitution']:
        m(f"  {a}: W{s.ch.attribute[a].wuerfel.value}")

    m(f"Finale Talente: {s.ch.selected_talente}")
    m(f"Finale Handicaps: {s.ch.selected_handicaps}")

    diff = s.diff(soll)
    m(f"DIFF: {diff['abweichungen']}")

    s.speichern('chars/Archetypen/Archetyp_Deadlands_Gepeinigter_Test_A.json')
    b = s.bericht('logs/gepeinigter_v3_bericht.json')
    m(f"FERTIG anomalien={b['anomalien_anzahl']}")
    print(f"Anomalien: {b['anomalien_anzahl']}")
except BaseException as e:
    m(f"CRASH: {e}\n{traceback.format_exc()}")
    traceback.print_exc()
tlog.close()