import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
tlog = open('logs/ezren_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

# Soll-Werte aus dem Archetyp-Bogen
soll = {
    'attribute': {
        'Geschicklichkeit': 6, 'Konstitution': 6, 'Stärke': 4,
        'Verstand': 10, 'Willenskraft': 8,
    },
    'fertigkeiten': {
        'Allgemeinwissen': 8, 'Athletik': 4, 'Geisteswissenschaften': 8,
        'Heimlichkeit': 6, 'Kämpfen': 4, 'Okkultismus': 8, 'Reiten': 4,
        'Schießen': 6, 'Überreden': 6, 'Wahrnehmung': 6, 'Zaubern': 10,
    },
    # Behindernde Rüstung_jede: AH(Magier) auto → nicht manuell hinzufügen
    'handicaps': ['Alt', 'Beschämt_schwer', 'Behindernde Rüstung_jede'],
    # AH(Magier) bringt automatisch Schule, Arkane Verbindung, Zauberbücher + Behindernde Rüstung_jede
    'talente': ['AH (Magier)', 'Schule', 'Arkane Verbindung', 'Zauberbücher', 'Alleskönner'],
    'maechte': ['Arkanes entdecken/verbergen', 'Geschoss', 'Schutz'],
}

try:
    import driver as d
    s = d.Sitzung('Savage Pathfinder', 'Ezren', protokoll='logs/ezren.log')

    # --- 1: Pathfinder Klassentalent ---
    r = s.pathfinder_klassentalent('AH (Magier)', ignore_voraussetzungen=True)
    m('1 Klassentalent AH(Magier): ok=%s FP=%d MP=%d Mächte=%d' % (
        r['ok'], s.ch.verbleibende_fertigkeitssteigerungen,
        s.ch.machtpunkte, s.ch.verfuegbare_maechte))
    m('   Auto-Talente: ' + str(sorted(s.ch.selected_talente)))

    # --- 2: Handicaps ---
    # Behindernde Rüstung_jede kommt auto von AH(Magier) → nur manuell gesetzte Handicaps
    for h in ['Alt', 'Beschämt_schwer']:
        r = s.handicap(h)
        m('2 Handicap %s: ok=%s FP=%d HP=%d gesamt_HP=%d' % (
            h, r['ok'], s.ch.verbleibende_fertigkeitssteigerungen,
            s.ch.verbleibende_handicap_punkte, s.ch.gesamt_handicap_punkte))

    # --- 3: Volk ---
    s.volk('Mensch')
    m('3 Volk Mensch: AP=%d FP=%d HP=%d' % (
        s.ch.verbleibende_attributsteigerungen,
        s.ch.verbleibende_fertigkeitssteigerungen,
        s.ch.verbleibende_handicap_punkte))

    # --- 4: Volkswahlen (Anpassungsfähigkeit: freies Attribut + freies Talent) ---
    m('4 Volkswahlen: ' + str(s.volk_wahlmoeglichkeiten('Mensch')))
    s.volk_freies_attribut('Mensch', 'Verstand')
    # Alleskönner = Mensch-Freiталент laut PDF
    s.volk_freies_talent('Mensch', 'Alleskönner', ignore_voraussetzungen=True)
    m('4 Nach Volkswahlen: AP=%d FP=%d HP=%d' % (
        s.ch.verbleibende_attributsteigerungen,
        s.ch.verbleibende_fertigkeitssteigerungen,
        s.ch.verbleibende_handicap_punkte))

    # --- 5: Attribute KOMPLETT (regulär + Handicap) VOR Fertigkeiten ---
    # Reihenfolge: die teuren zuerst, damit reguläre Punkte optimal verteilt werden
    attr_reihenfolge = [
        ('Verstand', 10), ('Willenskraft', 8),
        ('Geschicklichkeit', 6), ('Konstitution', 6), ('Stärke', 4),
    ]
    for a, z in attr_reihenfolge:
        s.attribut_auf(a, z)
    m('5a Nach regulären Attributen: AP=%d HP=%d' % (
        s.ch.verbleibende_attributsteigerungen, s.ch.verbleibende_handicap_punkte))
    # Fehlende Attributsteigerungen mit Handicap-Punkten auffüllen
    for a, z in attr_reihenfolge:
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte > 0:
            vor = s.ch.attribute[a].wuerfel.value
            s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value == vor:
                break
    m('5b Nach HP-Attributen: AP=%d HP=%d Attr=%s' % (
        s.ch.verbleibende_attributsteigerungen,
        s.ch.verbleibende_handicap_punkte,
        {a: s.ch.attribute[a].wuerfel.value for a in ['Geschicklichkeit','Konstitution','Stärke','Verstand','Willenskraft']}))

    # --- 6: Fertigkeiten (reguläre FP zuerst, dann HP) ---
    fert_reihenfolge = [
        ('Zaubern', 10), ('Geisteswissenschaften', 8), ('Okkultismus', 8),
        ('Allgemeinwissen', 8), ('Schießen', 6), ('Heimlichkeit', 6),
        ('Überreden', 6), ('Wahrnehmung', 6), ('Kämpfen', 4),
        ('Reiten', 4), ('Athletik', 4),
    ]
    for f, z in fert_reihenfolge:
        s.fertigkeit_auf(f, z)
    m('6a Nach regulären Fertigkeiten: FP=%d HP=%d' % (
        s.ch.verbleibende_fertigkeitssteigerungen, s.ch.verbleibende_handicap_punkte))

    # Restliche Fertigkeitssteigerungen mit Handicap-Punkten
    for f, z in fert_reihenfolge:
        w = s.ch.fertigkeiten[f].wuerfel
        while (w.value < z or w.modifier < 0) and s.ch.verbleibende_handicap_punkte > 0:
            vor_val, vor_mod = w.value, w.modifier
            s.steigere_mit_handicap_fertigkeit(f)
            if w.value == vor_val and w.modifier == vor_mod:
                break
    m('6b Nach HP-Fertigkeiten: FP=%d HP=%d Zaubern=%d mod=%d' % (
        s.ch.verbleibende_fertigkeitssteigerungen,
        s.ch.verbleibende_handicap_punkte,
        s.ch.fertigkeiten['Zaubern'].wuerfel.value,
        s.ch.fertigkeiten['Zaubern'].wuerfel.modifier))

    # --- 7: Talente (die noch nicht durch Klasse erteilt wurden) ---
    for t in soll['talente']:
        if t not in s.ch.selected_talente:
            s.talent(t, ignore_voraussetzungen=True)

    # --- 8: Mächte ---
    for mm in soll['maechte']:
        r = s.macht(mm, ignore_rang_check=True)
        m('8 Macht %s: ok=%s' % (mm, r['ok']))
    # --- 9: Ausrüstung ---
    ausruestung_liste = [
        'Dolch',
        'Kampfstab',            # = Gehstock (Stä+W4, Parade+1, Rw+1, zweihändig)
        'Handarmbrust',
        ('Bolzen (10)', 2),     # 20 Bolzen
        'Zauberkomponentenbeutel',
        'Zauberbuch, Magier (leer)',
        'Abenteurerausrüstung',  # PDF: "Abenteuerpaket" = Abenteurerausrüstung im Setting
        'Pergament',
        'Tintenstift (Schreibfeder)',
        'Tinte (Fläschchen)',
        'Schriftrolle: Schlummer',
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
    s.ch.profil_daten['Sprachen'] = 'Abyssisch, Elfisch, Gemeinsprache, Riesisch, Thassilonisch, Zwergisch'
    s.ch.profil_daten['Konzept'] = 'Ikonischer Magier'

    # Abgeleitete Werte neu berechnen
    s.ch.berechne_abgeleitete_werte()

    m('=== ERGEBNIS ===')
    m('  MP=%d  Bennys=%s  Parade=%s  Robustheit=%s  Bewegung=%s' % (
        s.ch.machtpunkte, s.ch.bennys, s.ch.parade, s.ch.robustheit, s.ch.bewegungsweite))
    m('  Talente: ' + str(sorted(s.ch.selected_talente)))
    m('  Mächte: ' + str(list(s.ch.selected_maechte)))
    m('  (Bogen: Parade4(5 Kampfstab), Robustheit5, Bew5(W6-1), Bennys3, MP10+)')
    m('  Vermögen: %s (Bogen: 24 GM)' % s.ch.vermoegen)

    diff = s.diff(soll)
    m('DIFF: ' + str(diff['abweichungen']))
    m('PUNKTE: ' + str(s.punktestand()))

    s.speichern('chars/Archetypen/Archetyp_Savage_Pathfinder_Magier_Ezren_A.json')
    b = s.bericht('logs/ezren_bericht.json')
    m('FERTIG anomalien=%d' % b['anomalien_anzahl'])

except BaseException as e:
    m('CRASH: %r\n%s' % (e, traceback.format_exc()))

tlog.close()
