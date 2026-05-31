import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
tlog = open('logs/kyra_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

# Soll-Werte: Kyra, Ikonische Klerikerin (Savage Pathfinder, Anfängerin)
soll = {
    'attribute': {
        'Geschicklichkeit': 6, 'Konstitution': 6, 'Stärke': 6,
        'Verstand': 8, 'Willenskraft': 8,
    },
    'fertigkeiten': {
        'Allgemeinwissen': 4, 'Athletik': 4, 'Einschüchtern': 6,
        'Glaube': 8, 'Heilen': 6, 'Heimlichkeit': 4,
        'Kämpfen': 6, 'Okkultismus': 6, 'Reiten': 4,
        'Überreden': 6, 'Wahrnehmung': 6,
    },
    # AH(Kleriker) bringt Schwur_schwer automatisch → NICHT manuell hinzufügen
    'handicaps': ['Ehrenkodex', 'Heroisch', 'Schwur_schwer'],
    # AH(Kleriker) bringt Energie fokussieren + Gnade automatisch
    # Mensch-Freiталент: Heiler
    'talente': ['AH (Kleriker)', 'Energie fokussieren', 'Gnade', 'Heiler'],
    'maechte': ['Heilung', 'Schutz', 'Waffe verbessern'],
}

try:
    import driver as d
    s = d.Sitzung('Savage Pathfinder', 'Kyra', protokoll='logs/kyra.log')

    # --- 1: Pathfinder Klassentalent ---
    # AH(Kleriker) bringt auto: Energie fokussieren, Gnade, Schwur_schwer
    r = s.pathfinder_klassentalent('AH (Kleriker)', ignore_voraussetzungen=True)
    m('1 AH(Kleriker): ok=%s FP=%d MP=%d Maechte=%d Talente=%s HC=%s' % (
        r['ok'], s.ch.verbleibende_fertigkeitssteigerungen,
        s.ch.machtpunkte, s.ch.verfuegbare_maechte,
        sorted(s.ch.selected_talente), list(s.ch.selected_handicaps)))

    # --- 2: Handicaps (NICHT Schwur_schwer – kommt durch AH(Kleriker)) ---
    # Ehrenkodex = schweres Handicap (2 HP), Heroisch (Heldenhaft) = schweres Handicap (2 HP)
    for h in ['Ehrenkodex', 'Heroisch']:
        r = s.handicap(h)
        m('2 Handicap %s: ok=%s HP=%d gesamt=%d' % (
            h, r['ok'], s.ch.verbleibende_handicap_punkte, s.ch.gesamt_handicap_punkte))

    # --- 3: Volk ---
    s.volk('Mensch')
    m('3 Mensch: AP=%d FP=%d HP=%d HC=%s Talente=%s' % (
        s.ch.verbleibende_attributsteigerungen,
        s.ch.verbleibende_fertigkeitssteigerungen,
        s.ch.verbleibende_handicap_punkte,
        list(s.ch.selected_handicaps),
        sorted(s.ch.selected_talente)))

    # --- 4: Volkswahlen Mensch (freies_talent + freies_attribut) ---
    m('4 Volkswahlen: ' + str(s.volk_wahlmoeglichkeiten('Mensch')))
    # Freies Attribut: Geschicklichkeit W4→W6 (spart 1 regulären AP)
    r = s.volk_freies_attribut('Mensch', 'Geschicklichkeit')
    m('4 volk_freies_attribut(Geschicklichkeit): ok=%s GEK=%d AP=%d' % (
        r['ok'], s.ch.attribute['Geschicklichkeit'].wuerfel.value,
        s.ch.verbleibende_attributsteigerungen))
    # Freies Talent: Heiler
    r = s.volk_freies_talent('Mensch', 'Heiler', ignore_voraussetzungen=True)
    m('4 volk_freies_talent(Heiler): ok=%s Talente=%s' % (
        r['ok'], sorted(s.ch.selected_talente)))

    # --- 5: Attribute KOMPLETT (regulär + Handicap-Punkte) VOR den Fertigkeiten ---
    # Mit freiem GEK W6: Regulär: KON(1)+STÄ(1)+VER(2)+WIL W4→W6(1) = 5 AP
    # Dann 2 HP für WIL W6→W8
    attr_reihenfolge = [
        ('Konstitution', 6), ('Stärke', 6), ('Verstand', 8), ('Willenskraft', 6),
    ]
    for a, z in attr_reihenfolge:
        s.attribut_auf(a, z)
    m('5a Reguläre Attribute: AP=%d HP=%d Attr=%s' % (
        s.ch.verbleibende_attributsteigerungen, s.ch.verbleibende_handicap_punkte,
        {a: s.ch.attribute[a].wuerfel.value
         for a in ['Geschicklichkeit', 'Konstitution', 'Stärke', 'Verstand', 'Willenskraft']}))

    # Willenskraft W6→W8 mit Handicap-Punkten (2 HP)
    for a, z in [('Willenskraft', 8)]:
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte > 0:
            vor = s.ch.attribute[a].wuerfel.value
            s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value == vor:
                break
    m('5b HP-Attribute: AP=%d HP=%d Attr=%s' % (
        s.ch.verbleibende_attributsteigerungen,
        s.ch.verbleibende_handicap_punkte,
        {a: s.ch.attribute[a].wuerfel.value
         for a in ['Geschicklichkeit', 'Konstitution', 'Stärke', 'Verstand', 'Willenskraft']}))

    # --- 6: Fertigkeiten (12 reguläre FP + 2 HP-FP) ---
    # Budget: Glaube(3)+Einschüchtern(2)+Heilen(2)+Kämpfen(2)+Okkultismus(2)+Reiten(1) = 12 FP regulär
    # Dann: Überreden W6(1 HP) + Wahrnehmung W6(1 HP) = 2 HP
    fert_reihenfolge = [
        ('Glaube', 8),          # 3 FP: -2→0(1) + W6(1) + W8(1); attr=Verstand W8 → kein Doppelkost
        ('Einschüchtern', 6),   # 2 FP: -2→0(1) + W6(1); attr=Willenskraft W8 → kein Doppelkost
        ('Heilen', 6),          # 2 FP: -2→0(1) + W6(1); attr=Verstand W8 → kein Doppelkost
        ('Kämpfen', 6),         # 2 FP: -2→0(1) + W6(1); attr=Geschicklichkeit W6 → kein Doppelkost
        ('Okkultismus', 6),     # 2 FP: -2→0(1) + W6(1); attr=Verstand W8 → kein Doppelkost
        ('Reiten', 4),          # 1 FP: -2→0(1); attr=Geschicklichkeit W6 → kein Doppelkost
        ('Heimlichkeit', 4),    # 0 FP (Grundfertigkeit W4)
        ('Allgemeinwissen', 4), # 0 FP (Grundfertigkeit W4)
        ('Athletik', 4),        # 0 FP (Grundfertigkeit W4)
        ('Überreden', 4),       # 0 FP (Grundfertigkeit W4, W6 mit HP)
        ('Wahrnehmung', 4),     # 0 FP (Grundfertigkeit W4, W6 mit HP)
    ]
    for f, z in fert_reihenfolge:
        s.fertigkeit_auf(f, z)
    m('6a Nach regulären Fertigkeiten: FP=%d HP=%d' % (
        s.ch.verbleibende_fertigkeitssteigerungen, s.ch.verbleibende_handicap_punkte))
    m('6a Fertigkeiten: Glaube=%d Einschüchtern=%d Heilen=%d Kämpfen=%d Okkultismus=%d Reiten=%d' % (
        s.ch.fertigkeiten['Glaube'].wuerfel.value,
        s.ch.fertigkeiten['Einschüchtern'].wuerfel.value,
        s.ch.fertigkeiten['Heilen'].wuerfel.value,
        s.ch.fertigkeiten['Kämpfen'].wuerfel.value,
        s.ch.fertigkeiten['Okkultismus'].wuerfel.value,
        s.ch.fertigkeiten['Reiten'].wuerfel.value))

    # Überreden W6 und Wahrnehmung W6 mit HP (je 1 HP)
    for f, z in [('Überreden', 6), ('Wahrnehmung', 6)]:
        w = s.ch.fertigkeiten[f].wuerfel
        while w.value < z and s.ch.verbleibende_handicap_punkte > 0:
            vor = w.value
            s.steigere_mit_handicap_fertigkeit(f)
            if w.value == vor:
                break
        m('6b HP-Fertigkeit %s: W%d mod=%d HP=%d' % (
            f, w.value, w.modifier, s.ch.verbleibende_handicap_punkte))

    # --- 7: Talente (alle schon durch Klasse + freies Mensch-Talent abgedeckt) ---
    m('7 Talente nach Klasse+Volk: %s' % sorted(s.ch.selected_talente))
    # Keine weiteren Talente nötig

    # --- 8: Mächte ---
    for mm in soll['maechte']:
        r = s.macht(mm, ignore_rang_check=True)
        m('8 Macht %s: ok=%s verfügbar=%d' % (mm, r['ok'], s.ch.verfuegbare_maechte))

    # --- 9: Ausrüstung ---
    ausruestung_liste = [
        'Krummschwert',
        'Schleuder',
        'Schleudersteine (20)',
        'Ledertunika',
        'Lederbeinlinge',
        'Heilertasche',
        'Heiliges Symbol, Silber',
        'Heiliges Wasser',
        'Abenteurerausrüstung',
    ]
    for item in ausruestung_liste:
        if item in s.ch.ausruestung:
            r = s.kaufen(item)
            m('9 Kauf %s: ok=%s Geld=%s' % (item, r['ok'], s.ch.vermoegen))
        else:
            s.notiz('AUSRÜSTUNG NICHT IM KATALOG: ' + item)
            m('9 FEHLT: ' + item)

    # Helm: "Lederkappe" als nächste verfügbare Option
    for helm_kandidat in ['Lederkappe', 'Schwerer Helm']:
        if helm_kandidat in s.ch.ausruestung:
            r = s.kaufen(helm_kandidat)
            m('9 Helm=%s: ok=%s Geld=%s' % (helm_kandidat, r['ok'], s.ch.vermoegen))
            break
    else:
        s.notiz('HELM: Kein passender Helm im Katalog gefunden')

    # Klerikergewandung: kein direktes Item, Klerikerpaket als Ersatz oder Notiz
    if 'Klerikerpaket' in s.ch.ausruestung:
        r = s.kaufen('Klerikerpaket')
        m('9 Klerikerpaket (statt Gewandung): ok=%s Geld=%s' % (r['ok'], s.ch.vermoegen))
    else:
        s.notiz('KLERIKERGEWANDUNG: kein passendes Item im Katalog')

    m('9 Endvermögen: %s (Bogen: 29 GM)' % s.ch.vermoegen)

    # Sprachen als Profildaten
    s.ch.profil_daten['Sprachen'] = 'Celestisch, Elfisch, Gemeinsprache, Halblingisch, Kelisch'
    s.ch.profil_daten['Konzept'] = 'Ikonische Klerikerin'

    s.ch.berechne_abgeleitete_werte()
    m('=== ERGEBNIS ===')
    m('  MP=%d  Bennys=%s  Parade=%s  Robustheit=%s  Bewegung=%s' % (
        s.ch.machtpunkte, s.ch.bennys, s.ch.parade, s.ch.robustheit, s.ch.bewegungsweite))
    m('  Talente: ' + str(sorted(s.ch.selected_talente)))
    m('  Handicaps: ' + str(list(s.ch.selected_handicaps)))
    m('  Mächte: ' + str(list(s.ch.selected_maechte)))
    m('  (Bogen: Parade5, Robustheit7(2), Bew6, Bennys3, MP10)')
    m('  Vermögen: %s (Bogen: 29 GM)' % s.ch.vermoegen)

    diff = s.diff(soll)
    m('DIFF: ' + str(diff['abweichungen']))
    m('PUNKTE: ' + str(s.punktestand()))

    s.speichern('chars/Archetypen/Archetyp_Savage_Pathfinder_Klerikerin_Kyra_A.json')
    b = s.bericht('logs/kyra_bericht.json')
    m('FERTIG anomalien=%d' % b['anomalien_anzahl'])

except BaseException as e:
    m('CRASH: %r\n%s' % (e, traceback.format_exc()))

tlog.close()
