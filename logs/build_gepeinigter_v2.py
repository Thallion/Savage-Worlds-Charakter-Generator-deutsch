import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d

tlog = open('logs/gepeinigter_v2_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

soll = {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 4},
    'fertigkeiten': {'Athletik': 6, 'Heimlichkeit': 6, 'Einschüchtern': 8, 'Schießen': 8, 'Kämpfen': 6, 'Reiten': 6, 'Provozieren': 6, 'Okkultismus': 4, 'Allgemeinwissen': 4, 'Überreden': 4, 'Wahrnehmung': 4},
    'handicaps':    ['Fies (leicht)', 'Rachsüchtig (schwer)', 'Skrupellos (leicht)'],
    'talente':      ['Flicken', 'Killerinstinkt', 'Übernatürliches Attribut (Geschicklichkeit)'],
    'maechte':      [],
}

manual_handicaps = ['Fies (leicht)', 'Rachsüchtig (schwer)', 'Skrupellos (leicht)']

try:
    s = d.Sitzung('Deadlands', 'Gepeinigter', protokoll='logs/gepeinigter_v2.log')

    # Volkeswahl
    s.volk('Mensch')

    # Handicaps (Major zuerst)
    for h in manual_handicaps:
        s.handicap(h)

    m(f"  Punktestand nach Volk+Handicaps: {s.punktestand()}")

    # WICHTIG: Zuerst Gepeinigt-Talent wählen (Voraussetzung für Flicken)
    # Gepeinigt braucht Willenskraft W6+
    m("  Steigere Willenskraft für Gepeinigt-Voraussetzung...")
    s.attribut('Willenskraft')  # W4 -> W6 (1 Punkt)
    m(f"  Nach Willenskraft: {s.punktestand()}")

    # Jetzt Gepeinigt wählen (kostenlos - kein Rang/Ressourcen needed für A-Rang bei Anfänger)
    m("  Wähle Gepeinigt-Talent...")
    geo = s.talent('Gepeinigt')
    m(f"  Gepeinigt: {geo}")

    # Jetzt Flicken und andere Talente
    for t in ['Flicken', 'Killerinstinkt', 'Übernatürliches Attribut (Geschicklichkeit)']:
        result = s.talent(t)
        m(f"  Talent {t}: {result}")

    m(f"  Punktestand nach Talenten: {s.punktestand()}")
    m(f"  Ausgewählte Talente: {s.ch.selected_talente}")

    # Attribute VOR Fertigkeiten komplett
    ziel_attribute = {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 4}

    # Mit regulären Punkten auf Ziel
    for a, z in ziel_attribute.items():
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_attributsteigerungen > 0:
            s.attribut(a)
            m(f"  Attribut {a}: {s.ch.attribute[a].wuerfel.value}")

    # Noch fehlende mit Handicap-Punkten
    for a, z in ziel_attribute.items():
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte > 0:
            s.steigere_mit_handicap_attribut(a)
            m(f"  HP-Steigerung {a}: {s.ch.attribute[a].wuerfel.value}")

    m(f"  Nach Attributen: {s.punktestand()}")

    # Fertigkeiten
    fertigkeits_ziele = {'Athletik': 6, 'Heimlichkeit': 6, 'Einschüchtern': 8, 'Schießen': 8, 'Kämpfen': 6,
                         'Reiten': 6, 'Provozieren': 6, 'Okkultismus': 4, 'Allgemeinwissen': 4, 'Überreden': 4, 'Wahrnehmung': 4}
    for f, z in fertigkeits_ziele.items():
        if f in s.ch.fertigkeiten:
            while s.ch.fertigkeiten[f].wuerfel.value < z:
                vor = s.ch.fertigkeiten[f].wuerfel.value
                if s.ch.verbleibende_fertigkeitssteigerungen > 0:
                    s.fertigkeit(f)
                elif s.ch.verbleibende_handicap_punkte > 0:
                    s.steigere_mit_handicap_fertigkeit(f)
                else:
                    break
                if s.ch.fertigkeiten[f].wuerfel.value == vor:
                    break
        else:
            s.notiz(f'FERTIGKEIT-KEY fehlt: {f}')

    m(f"  Nach Fertigkeiten: {s.punktestand()}")

    # Attribut Prüfung
    m(f"  Finale Attribute:")
    for a in ['Geschicklichkeit', 'Verstand', 'Willenskraft', 'Stärke', 'Konstitution']:
        m(f"    {a}: W{s.ch.attribute[a].wuerfel.value}")

    m(f"  Finale Talente: {s.ch.selected_talente}")

    # Diff
    diff = s.diff(soll)
    m('DIFF: ' + str(diff))

    s.speichern('chars/Archetypen/Archetyp_Deadlands_Gepeinigter_Test_A.json')
    b = s.bericht('logs/gepeinigter_v2_bericht.json')
    m('FERTIG anomalien=%d' % b['anomalien_anzahl'])
    print(f"Anomalien: {b['anomalien_anzahl']}")
except BaseException as e:
    m('CRASH: %r\n%s' % (e, traceback.format_exc()))
    traceback.print_exc()
tlog.close()