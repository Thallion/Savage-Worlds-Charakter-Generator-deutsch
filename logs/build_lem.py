import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
tlog = open('logs/lem_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

# Soll-Werte: Lem, Ikonischer Barde (Savage Pathfinder, Anfänger)
# Notiz: AH(Barde) bringt auto: Scharfzüngig, Behindernde Rüstung_leicht
# Notiz: Halbling bringt auto: Glück (Talent), Größe -1 (Reduzierte Robustheit)
#        + Athletik W6 (Wendig) + Wahrnehmung W6 (Geschärfte Sinne)
# Notiz: Geschicklichkeit startet bei W6 (Halbling "Geschickt")
soll = {
    'attribute': {
        'Geschicklichkeit': 8, 'Konstitution': 6, 'Stärke': 6,
        'Verstand': 6, 'Willenskraft': 8,
    },
    'fertigkeiten': {
        'Allgemeinwissen': 4, 'Athletik': 6, 'Darbietung': 8,
        'Diebeskunst': 4, 'Geisteswissenschaften': 4, 'Heimlichkeit': 6,
        'Kämpfen': 6, 'Okkultismus': 6, 'Überreden': 6, 'Wahrnehmung': 6,
    },
    # Bogen-Handicaps (ohne Volks-/Klassen-Handicaps)
    'handicaps': ['Impulsiv', 'Sanftmütig', 'Tick',
                  'Behindernde Rüstung_leicht', 'Größe -1 (Reduzierte Robustheit)'],
    # Bogen-Talente: Barde=AH(Barde), Charismatisch, Glück=auto Halbling
    # AH(Barde) bringt zusätzlich Scharfzüngig (nicht auf Bogen → ZUVIEL-Eintrag im Diff erwartet)
    'talente': ['AH (Barde)', 'Charismatisch', 'Glück', 'Scharfzüngig'],
    'maechte': ['Eigenschaft erhöhen/senken', 'Empathie', 'Verwirrung'],
}

try:
    import driver as d
    s = d.Sitzung('Savage Pathfinder', 'Lem', protokoll='logs/lem.log')

    # --- 1: Pathfinder Klassentalent ---
    # AH(Barde) bringt auto: Scharfzüngig + Behindernde Rüstung_leicht
    r = s.pathfinder_klassentalent('AH (Barde)', ignore_voraussetzungen=True)
    m('1 AH(Barde): ok=%s FP=%d MP=%d Maechte=%d Talente=%s HC=%s' % (
        r['ok'], s.ch.verbleibende_fertigkeitssteigerungen,
        s.ch.machtpunkte, s.ch.verfuegbare_maechte,
        sorted(s.ch.selected_talente), list(s.ch.selected_handicaps)))

    # --- 2: Handicaps (keine Volks-Handicaps) ---
    # Impulsiv(schwer=2HP) + Sanftmütig(1HP) + Tick(1HP) = 4 HP gesamt
    for h in ['Impulsiv', 'Sanftmütig', 'Tick']:
        r = s.handicap(h)
        m('2 Handicap %s: ok=%s HP=%d' % (h, r['ok'], s.ch.verbleibende_handicap_punkte))

    # --- 3: Volk ---
    # Halbling bringt: Glück (Talent), Größe-1 (Handicap), Pace=5
    # + Geschicklichkeit startet W6 (Geschickt)
    # + Athletik startet W6 (Wendig) → 0 FP nötig
    # + Wahrnehmung startet W6 (Geschärfte Sinne) → 0 FP nötig
    r = s.volk('Halbling')
    m('3 Halbling: AP=%d FP=%d HP=%d HC=%s Talente=%s Pace=%s' % (
        s.ch.verbleibende_attributsteigerungen,
        s.ch.verbleibende_fertigkeitssteigerungen,
        s.ch.verbleibende_handicap_punkte,
        list(s.ch.selected_handicaps),
        sorted(s.ch.selected_talente),
        s.ch.bewegungsweite))
    m('3 Startattribute: %s' % {a: s.ch.attribute[a].wuerfel.value
        for a in ['Geschicklichkeit','Konstitution','Stärke','Verstand','Willenskraft']})
    m('3 Athletik=%d mod=%d  Wahrnehmung=%d mod=%d' % (
        s.ch.fertigkeiten['Athletik'].wuerfel.value,
        s.ch.fertigkeiten['Athletik'].wuerfel.modifier,
        s.ch.fertigkeiten['Wahrnehmung'].wuerfel.value,
        s.ch.fertigkeiten['Wahrnehmung'].wuerfel.modifier))

    # --- 4: Keine Volkswahlen bei Halbling (alles automatisch) ---
    m('4 Volkswahlen: ' + str(s.volk_wahlmoeglichkeiten('Halbling')))

    # --- 5: Attribute KOMPLETT (regulär + Handicap) VOR den Fertigkeiten ---
    # Start: GEK=W6, alle anderen W4
    # Regulär (5 AP): GEK W6→W8 + KON W4→W6 + STÄ W4→W6 + VER W4→W6 + WIL W4→W6
    # HP (2 HP): WIL W6→W8
    attr_reihenfolge = [
        ('Geschicklichkeit', 8),   # W6→W8 = 1 AP
        ('Konstitution', 6),       # W4→W6 = 1 AP
        ('Stärke', 6),             # W4→W6 = 1 AP
        ('Verstand', 6),           # W4→W6 = 1 AP
        ('Willenskraft', 6),       # W4→W6 = 1 AP (insgesamt 5 AP)
    ]
    for a, z in attr_reihenfolge:
        s.attribut_auf(a, z)
    m('5a Reguläre Attribute: AP=%d HP=%d Attr=%s' % (
        s.ch.verbleibende_attributsteigerungen, s.ch.verbleibende_handicap_punkte,
        {a: s.ch.attribute[a].wuerfel.value
         for a in ['Geschicklichkeit','Konstitution','Stärke','Verstand','Willenskraft']}))

    # Willenskraft W6→W8 mit 2 Handicap-Punkten
    vor = s.ch.attribute['Willenskraft'].wuerfel.value
    r = s.steigere_mit_handicap_attribut('Willenskraft')  # W6→W8
    m('5b HP Willenskraft: WIL=%d→%d HP=%d' % (
        vor, s.ch.attribute['Willenskraft'].wuerfel.value,
        s.ch.verbleibende_handicap_punkte))

    # --- 6: Fertigkeiten (12 FP) ---
    # Halbling-Bonus: Athletik=W6, Wahrnehmung=W6 (beide 0 FP)
    # Budget: Darbietung(3)+Kämpfen(2)+Okkultismus(2)+Diebeskunst(1)+GW(1)+Heimlichkeit(1)+Überreden(1)=11 FP
    # 1 FP spare bleibt übrig
    fert_reihenfolge = [
        ('Darbietung', 8),          # 3 FP: -2→0(1)+W6(1)+W8(1); Willenskraft W8→kein Doppelkost
        ('Kämpfen', 6),             # 2 FP: -2→0(1)+W6(1); Geschicklichkeit W8→kein Doppelkost
        ('Okkultismus', 6),         # 2 FP: -2→0(1)+W6(1); Verstand W6=W6→kein Doppelkost
        ('Diebeskunst', 4),         # 1 FP: -2→0(1); Geschicklichkeit W8→kein Doppelkost
        ('Geisteswissenschaften', 4), # 1 FP: -2→0(1); Verstand W6→kein Doppelkost
        ('Heimlichkeit', 6),        # 1 FP: Grundfertigkeit W4→W6
        ('Überreden', 6),           # 1 FP: Grundfertigkeit W4→W6
        ('Allgemeinwissen', 4),     # 0 FP: Grundfertigkeit W4
        ('Athletik', 6),            # 0 FP: schon W6 durch Halbling (Wendig)
        ('Wahrnehmung', 6),         # 0 FP: schon W6 durch Halbling (Geschärfte Sinne)
    ]
    for f, z in fert_reihenfolge:
        before = s.ch.verbleibende_fertigkeitssteigerungen
        s.fertigkeit_auf(f, z)
        after = s.ch.verbleibende_fertigkeitssteigerungen
        m('6 %s W%d: kosten=%d FP=%d' % (f, z, before-after, after))
    m('6 Nach Fertigkeiten: FP=%d HP=%d' % (
        s.ch.verbleibende_fertigkeitssteigerungen, s.ch.verbleibende_handicap_punkte))

    # --- 7: Talente (Charismatisch mit 2 HP) ---
    # AH(Barde)+Scharfzüngig auto, Glück auto von Halbling → nur Charismatisch nötig
    r = s.talent('Charismatisch', ignore_voraussetzungen=True)
    m('7 Talent Charismatisch: ok=%s HP=%d Talente=%s' % (
        r['ok'], s.ch.verbleibende_handicap_punkte, sorted(s.ch.selected_talente)))

    # --- 8: Mächte ---
    for mm in soll['maechte']:
        r = s.macht(mm, ignore_rang_check=True)
        m('8 Macht %s: ok=%s verfügbar=%d' % (mm, r['ok'], s.ch.verfuegbare_maechte))

    # --- 9: Ausrüstung ---
    ausruestung_liste = [
        'Dolch',
        'Schleuder',
        'Schleudersteine (20)',
        'Ledertunika',
        'Lederbeinlinge',
        'Abenteurerausrüstung',
        'Gegengift, Phiole',
    ]
    for item in ausruestung_liste:
        if item in s.ch.ausruestung:
            r = s.kaufen(item)
            m('9 Kauf %s: ok=%s Geld=%s' % (item, r['ok'], s.ch.vermoegen))
        else:
            s.notiz('AUSRÜSTUNG NICHT IM KATALOG: ' + item)

    # Musikinstrument (für Flöte)
    for kandidat in ['Musikinstrument', 'Flöte']:
        if kandidat in s.ch.ausruestung:
            r = s.kaufen(kandidat)
            m('9 Musikinstrument/Flöte (%s): ok=%s Geld=%s' % (kandidat, r['ok'], s.ch.vermoegen))
            break
    else:
        s.notiz('MUSIKINSTRUMENT (Flöte): kein passendes Item im Katalog')

    # Unterhalterkleidung (kein direktes Item → Unterhalterpaket versuchen)
    for kandidat in ['Unterhalterpaket']:
        if kandidat in s.ch.ausruestung:
            r = s.kaufen(kandidat)
            m('9 Unterhalterkleidung→%s: ok=%s Geld=%s' % (kandidat, r['ok'], s.ch.vermoegen))
            break
    else:
        s.notiz('UNTERHALTERKLEIDUNG: kein passendes Item im Katalog')

    # Zündhölzer (5 Stück)
    if 'Zündholz' in s.ch.ausruestung:
        r = s.kaufen('Zündholz', anzahl=5)
        m('9 Zündholz x5: ok=%s Geld=%s' % (r['ok'], s.ch.vermoegen))
    else:
        s.notiz('ZÜNDHOLZ: nicht im Katalog')

    if 'Trank: schwache Heilung' in s.ch.ausruestung:
        r = s.kaufen('Trank: schwache Heilung')
        m('9 Trank schwache Heilung: ok=%s Geld=%s' % (r['ok'], s.ch.vermoegen))

    m('9 Endvermögen: %s (Bogen: 18 GM)' % s.ch.vermoegen)

    # Profil-Daten
    s.ch.profil_daten['Sprachen'] = 'Elfisch, Gemeinsprache, Gnomisch, Halblingisch'
    s.ch.profil_daten['Konzept'] = 'Ikonischer Barde'

    s.ch.berechne_abgeleitete_werte()
    m('=== ERGEBNIS ===')
    m('  MP=%d  Bennys=%s  Parade=%s  Robustheit=%s  Bewegung=%s' % (
        s.ch.machtpunkte, s.ch.bennys, s.ch.parade, s.ch.robustheit, s.ch.bewegungsweite))
    m('  Talente: ' + str(sorted(s.ch.selected_talente)))
    m('  Handicaps: ' + str(list(s.ch.selected_handicaps)))
    m('  Mächte: ' + str(list(s.ch.selected_maechte)))
    m('  (Bogen: Parade5, Robustheit6(2), Bew5(W4), Bennys4, MP10)')
    m('  Vermögen: %s (Bogen: 18 GM)' % s.ch.vermoegen)

    diff = s.diff(soll)
    m('DIFF: ' + str(diff['abweichungen']))
    m('PUNKTE: ' + str(s.punktestand()))

    s.speichern('chars/Archetypen/Archetyp_Savage_Pathfinder_Barde_Lem_A.json')
    b = s.bericht('logs/lem_bericht.json')
    m('FERTIG anomalien=%d' % b['anomalien_anzahl'])

except BaseException as e:
    m('CRASH: %r\n%s' % (e, traceback.format_exc()))

tlog.close()
