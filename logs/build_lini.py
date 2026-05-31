import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
tlog = open('logs/lini_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

# Soll-Werte aus dem Archetyp-Bogen
soll = {
    'attribute': {
        'Geschicklichkeit': 6, 'Konstitution': 6, 'Stärke': 6,
        'Verstand': 6, 'Willenskraft': 8,
    },
    'fertigkeiten': {
        'Allgemeinwissen': 6, 'Athletik': 6, 'Einschüchtern': 4, 'Glaube': 8,
        'Heilen': 4, 'Heimlichkeit': 4, 'Kämpfen': 6, 'Reiten': 4,
        'Überleben': 8, 'Überreden': 4, 'Wahrnehmung': 6,
    },
    # AH(Druide) auto: Schwur_schwer + Behindernde Rüstung_leicht
    # Gnom auto-Handicaps: Langsam_leicht, Größe -1 (Reduzierte Robustheit), Zwanghaft
    'handicaps': ['Neugierig', 'Tick', 'Zwei linke Hände',
                  'Schwur_schwer', 'Behindernde Rüstung_leicht',
                  'Langsam_leicht', 'Größe -1 (Reduzierte Robustheit)', 'Zwanghaft'],
    # AH(Druide) auto: Bindung mit der Natur, Naturgespür
    # Gnom auto-Talent: Gnomenmagie
    'talente': ['AH (Druide)', 'Bindung mit der Natur', 'Naturgespür', 'Gnomenmagie',
                'Neue Mächte', 'Tiermeister'],
    'maechte': ['Elementarmanipulation', 'Schutz', 'Schutz vor Naturgewalten',
                'Tierfreund', 'Verstricken'],
}

try:
    import driver as d
    s = d.Sitzung('Savage Pathfinder', 'Lini', protokoll='logs/lini.log')

    # --- 1: Pathfinder Klassentalent ---
    r = s.pathfinder_klassentalent('AH (Druide)', ignore_voraussetzungen=True)
    m('1 AH(Druide): ok=%s FP=%d MP=%d Mächte=%d Talente=%s HC=%s' % (
        r['ok'], s.ch.verbleibende_fertigkeitssteigerungen,
        s.ch.machtpunkte, s.ch.verfuegbare_maechte,
        sorted(s.ch.selected_talente), list(s.ch.selected_handicaps)))

    # --- 2: Handicaps (NICHT Schwur_schwer – kommt durch AH(Druide)) ---
    for h in ['Neugierig', 'Tick', 'Zwei linke Hände']:
        r = s.handicap(h)
        m('2 Handicap %s: ok=%s FP=%d HP=%d gesamt=%d' % (
            h, r['ok'], s.ch.verbleibende_fertigkeitssteigerungen,
            s.ch.verbleibende_handicap_punkte, s.ch.gesamt_handicap_punkte))

    # --- 3: Volk ---
    s.volk('Gnom')
    m('3 Gnom: AP=%d FP=%d HP=%d HC=%s Talente=%s' % (
        s.ch.verbleibende_attributsteigerungen,
        s.ch.verbleibende_fertigkeitssteigerungen,
        s.ch.verbleibende_handicap_punkte,
        list(s.ch.selected_handicaps),
        sorted(s.ch.selected_talente)))

    # --- 4: Volkswahlen – Gnom hat freie_fertigkeit! ---
    m('4 Volkswahlen: ' + str(s.volk_wahlmoeglichkeiten('Gnom')))
    # Freie Fertigkeit: Überleben aktivieren (spart 1 FP für die Aktivierung)
    r = s.volk_freie_fertigkeit('Gnom', 'Überleben')
    m('4 volk_freie_fertigkeit(Überleben): ok=%s Überleben wert=%d mod=%d' % (
        r['ok'], s.ch.fertigkeiten['Überleben'].wuerfel.value,
        s.ch.fertigkeiten['Überleben'].wuerfel.modifier))

    # --- 5: Attribute KOMPLETT (regulär + Handicap) VOR Fertigkeiten ---
    # 5 reguläre AP für 5 Schritte, 2 HP für Willenskraft W6→W8
    attr_reihenfolge = [
        ('Willenskraft', 8), ('Geschicklichkeit', 6),
        ('Konstitution', 6), ('Stärke', 6), ('Verstand', 6),
    ]
    for a, z in attr_reihenfolge:
        s.attribut_auf(a, z)
    m('5a Reguläre Attribute: AP=%d HP=%d' % (
        s.ch.verbleibende_attributsteigerungen, s.ch.verbleibende_handicap_punkte))
    for a, z in attr_reihenfolge:
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte > 0:
            vor = s.ch.attribute[a].wuerfel.value
            s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value == vor:
                break
    m('5b HP-Attribute: AP=%d HP=%d Attr=%s' % (
        s.ch.verbleibende_attributsteigerungen,
        s.ch.verbleibende_handicap_punkte,
        {a: s.ch.attribute[a].wuerfel.value
         for a in ['Geschicklichkeit','Konstitution','Stärke','Verstand','Willenskraft']}))

    # --- 6: Fertigkeiten mit 12 FP (Budget eng wegen Überleben-Doppelkosten) ---
    # Überleben schon aktiviert (freie Fertigkeit), also nur W4→W6→W8 nötig (2+2 FP)
    # Mit 12 FP: Glaube(3)+Kämpfen(2)+Überleben W6(1)+Allgemeinwissen(1)+Athletik(1)+
    #            Einschüchtern(1)+Heilen(1)+Reiten(1)+Wahrnehmung(1) = 12 FP genau
    fert_reihenfolge = [
        ('Glaube', 8),          # 3 FP (Willenskraft W8 → kein Doppelkost)
        ('Kämpfen', 6),         # 2 FP
        ('Überleben', 8),       # 2 FP (Naturgespür → Willenskraft W8, kein Doppelkost mehr)
        ('Allgemeinwissen', 6), # 1 FP
        ('Athletik', 6),        # 1 FP
        ('Einschüchtern', 4),   # 1 FP
        ('Heilen', 4),          # 1 FP
        ('Reiten', 4),          # 1 FP
        ('Wahrnehmung', 6),     # 1 FP
        ('Heimlichkeit', 4),    # 0 FP (GF)
        ('Überreden', 4),       # 0 FP (GF)
    ]
    for f, z in fert_reihenfolge:
        s.fertigkeit_auf(f, z)
    m('6a Nach regulären Fertigkeiten: FP=%d HP=%d' % (
        s.ch.verbleibende_fertigkeitssteigerungen, s.ch.verbleibende_handicap_punkte))
    m('6a Überleben=%d mod=%d Wahrnehmung=%d mod=%d' % (
        s.ch.fertigkeiten['Überleben'].wuerfel.value,
        s.ch.fertigkeiten['Überleben'].wuerfel.modifier,
        s.ch.fertigkeiten['Wahrnehmung'].wuerfel.value,
        s.ch.fertigkeiten['Wahrnehmung'].wuerfel.modifier))

    # --- 7: Talente (mit HP) ---
    for t in ['Neue Mächte', 'Tiermeister']:
        if t not in s.ch.selected_talente:
            r = s.talent(t, ignore_voraussetzungen=True)
            m('7 Talent %s: ok=%s HP=%d' % (t, r['ok'], s.ch.verbleibende_handicap_punkte))

    # HP-Restabgleich Fertigkeiten (nach Talenten, falls noch HP übrig)
    m('Nach Talenten: HP=%d' % s.ch.verbleibende_handicap_punkte)
    fert_hp = [('Überleben', 8), ('Wahrnehmung', 6)]
    for f, z in fert_hp:
        w = s.ch.fertigkeiten[f].wuerfel
        while (w.value < z or w.modifier < 0) and s.ch.verbleibende_handicap_punkte > 0:
            vor_val, vor_mod = w.value, w.modifier
            s.steigere_mit_handicap_fertigkeit(f)
            if w.value == vor_val and w.modifier == vor_mod:
                break
        m('6b HP-Fertigkeit %s: W%d mod=%d HP=%d' % (f, w.value, w.modifier, s.ch.verbleibende_handicap_punkte))

    # --- 8: Mächte ---
    for mm in soll['maechte']:
        r = s.macht(mm, ignore_rang_check=True)
        m('8 Macht %s: ok=%s verfügbar=%d' % (mm, r['ok'], s.ch.verfuegbare_maechte))

    # --- 9: Ausrüstung ---
    # weiche Ledertunika und -hose (+2) = Ledertunika + Lederbeinlinge
    ausruestung_liste = [
        'Sichel',
        'Schleuder',
        'Schleudersteine (20)',      # 20 Steine
        'Reisekleidung',
        'Ledertunika',               # weiche Ledertunika (+1)
        'Lederbeinlinge',            # -hose (+1) → zusammen +2
        'Abenteurerausrüstung',
        'Donnerstein',
        'Zauberkomponentenbeutel',
        ('Rauchstab', 5),            # 5 x Rauchstäbe
        'Trank: schwache Heilung',
    ]
    for eintrag in ausruestung_liste:
        if isinstance(eintrag, tuple):
            item, anzahl = eintrag
        else:
            item, anzahl = eintrag, 1
        if item in s.ch.ausruestung:
            r = s.kaufen(item, anzahl=anzahl)
            m('9 Kauf %s x%d: ok=%s Geld=%s' % (item, anzahl, r['ok'], s.ch.vermoegen))
        else:
            s.notiz('AUSRÜSTUNG NICHT IM KATALOG: ' + item)

    # Profil-Daten
    s.ch.profil_daten['Sprachen'] = 'Druidisch, Elfisch, Gemeinsprache, Gnomisch, Sylvanisch'
    s.ch.profil_daten['Konzept'] = 'Ikonische Druidin'

    s.ch.berechne_abgeleitete_werte()
    m('=== ERGEBNIS ===')
    m('  MP=%d  Bennys=%s  Parade=%s  Robustheit=%s  Bewegung=%s' % (
        s.ch.machtpunkte, s.ch.bennys, s.ch.parade, s.ch.robustheit, s.ch.bewegungsweite))
    m('  Talente: ' + str(sorted(s.ch.selected_talente)))
    m('  Handicaps: ' + str(list(s.ch.selected_handicaps)))
    m('  Mächte: ' + str(list(s.ch.selected_maechte)))
    m('  (Bogen: Parade5, Robustheit6(2), Bew5(W4), Bennys3, MP10)')
    m('  Vermögen: %s (Bogen: 39 GM)' % s.ch.vermoegen)

    diff = s.diff(soll)
    m('DIFF: ' + str(diff['abweichungen']))
    m('PUNKTE: ' + str(s.punktestand()))

    s.speichern('chars/Archetypen/Archetyp_Savage_Pathfinder_Druidin_Lini_A.json')
    b = s.bericht('logs/lini_bericht.json')
    m('FERTIG anomalien=%d' % b['anomalien_anzahl'])

except BaseException as e:
    m('CRASH: %r\n%s' % (e, traceback.format_exc()))

tlog.close()
