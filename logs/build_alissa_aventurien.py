"""Bauen der 5 DSA-Archetypen aus screenshots/ mit den NEUEN Wissen-Fertigkeiten.

Strategie: max aus Chargen-Phase holen, dann char_gen_completed + Aufstiege.
"""
import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege


def abschliessen(s, n_aufstiege, log):
    s.ch.char_gen_completed = True
    for _ in range(n_aufstiege): increase_aufstiege(s.ch)
    log(f"  -> chargen abgeschlossen, {n_aufstiege} Aufstiege, Rang={s.ch.rang}")


def setup_allgemein(s, m):
    """Gemeinsame Setup-Schritte (Handicaps + AH + Volk) für alle Geweihten/Kleriker."""
    m(s.handicap('Impulsiv'))
    m(s.talent('AH (Wunder: Rahja)', ignore_voraussetzungen=True))
    m(s.handicap('Pazifist_leicht'))
    m(s.volk('Mensch'))
    m(s.volk_freies_talent('Mensch', 'Gassenwissen', ignore_voraussetzungen=True))


def build_alissa():
    name = 'Alissa'
    tlog = open(f'logs/{name.lower()}_aventurien_trace.txt', 'w', encoding='utf-8')
    def m(x): tlog.write(str(x)+'\n'); tlog.flush()

    soll = {
        'attribute':    {'Stärke': 4, 'Geschicklichkeit': 6, 'Konstitution': 6,
                         'Verstand': 10, 'Willenskraft': 10},  # statt 12 (Engpass)
        'fertigkeiten': {'Allgemeinwissen': 8, 'Athletik': 8, 'Heimlichkeit': 4,
                         'Überreden': 8, 'Wahrnehmung': 8, 'Darbietung': 4,
                         'Glaube': 8, 'Recherche': 8, 'Heilen': 8,
                         'Geisteswissenschaften': 8},
        # Manuelle Handicaps: Impulsiv (schwer), Pazifist_leicht
        # Auto durch AH (Wunder: Rahja): Schwur_schwer (Bogen-Konflikt: Schwur_leicht)
        'handicaps':    ['Impulsiv', 'Pazifist_leicht', 'Schwur_schwer'],
        # Manuelle Talente: Attraktiv, Sehr Attraktiv, Gassenwissen
        # Auto durch AH (Wunder: Rahja): Durchhaltevermögen (Rahja), Geschenk der Freude (Rahja)
        # Volk Mensch: "Anpassungsfähig" ist Volkseigenheit, kein eigenes Talent
        #   -> der freie Talent-Slot wurde mit Gassenwissen belegt
        'talente':      ['Attraktiv', 'Sehr Attraktiv', 'Gassenwissen',
                         'AH (Wunder: Rahja)',
                         'Durchhaltevermögen (Rahja)', 'Geschenk der Freude (Rahja)'],
        # AH (Wunder: Rahja) gibt 3 Startmächte (Bogen waehlt: Eigenschaft, Empathie, Linderung)
        'maechte':      ['Eigenschaft erhöhen/senken', 'Empathie', 'Linderung'],
    }

    try:
        s = d.Sitzung('Savage Aventurien', name, protokoll=f'logs/{name.lower()}_aventurien.log')
        m(f"  Setting: {s.setting}")

        # Handicaps + AH + Volk
        setup_allgemein(s, m)
        s.notiz('Bogen-Volkseigenheit "Anpassungsfaehig" = "Freies Anfaengertalent nach Wahl" '
                '(Mensch). Kein eigenstaendiger "Anpassungsfaehig"-Talent-Key im Setting. '
                'Gewaehlt: Gassenwissen als das freie Mensch-Talent.')

        # Attribute (5 Chargen - teuerste zuerst)
        for a, z in [('Willenskraft', 6),  # 1 Schritt
                     ('Verstand', 8),      # 2 Schritte
                     ('Geschicklichkeit', 6), ('Konstitution', 6),
                     ('Stärke', 4)]:
            s.attribut_auf(a, z)
        m(f"  Nach Attributen: {s.punktestand()}")

        # Fertigkeiten (12 Chargen)
        # Aktivierungen
        for f in ['Glaube', 'Recherche', 'Heilen',
                  'Wissen (Geschichtswissen)', 'Wissen (Götter & Kulte)']:
            if f in s.ch.fertigkeiten:
                s.fertigkeit(f)
        m(f"  Nach Aktivierungen: {s.punktestand()}")

        # Verstand-Wissen auf W8 (Ve W8 = bis W8 einfach)
        for f in ['Wissen (Geschichtswissen)', 'Wissen (Götter & Kulte)',
                  'Recherche', 'Heilen']:
            s.fertigkeit_auf(f, 8)
        m(f"  Nach Verstand-Fert: {s.punktestand()}")

        # Glaube W6 (Wi W6 = bis W6 einfach)
        s.fertigkeit_auf('Glaube', 6)
        m(f"  Nach Glaube W6: {s.punktestand()}")

        # Grundfertigkeiten (Verstand W8) - max was geht
        for f in ['Allgemeinwissen', 'Wahrnehmung', 'Überreden']:
            s.fertigkeit_auf(f, 6)
        m(f"  Nach Grund: {s.punktestand()}")

        # Rest auf W4
        for f in ['Heimlichkeit', 'Athletik', 'Darbietung']:
            s.fertigkeit_auf(f, 4)
        m(f"  Nach Fertigkeiten: {s.punktestand()}")

        # Talente
        m(s.talent('Attraktiv', ignore_voraussetzungen=True))
        m(f"  Nach Talenten: {s.punktestand()}")

        # Maechte
        for mm in soll['maechte']:
            m(s.macht(mm))

        # Abschluss + Aufstiege
        abschliessen(s, 3, m)
        s.charakter_mit_aufstieg('Verstand', 10)
        s.charakter_mit_aufstieg('Willenskraft', 10)
        m(f"  Ve: W{s.ch.attribute['Verstand'].wuerfel.value}, "
          f"Wi: W{s.ch.attribute['Willenskraft'].wuerfel.value}")
        r = s.talent('Sehr Attraktiv', ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Sehr Attraktiv (Aufstieg): ok={r['ok']}")
        r = s.charakter_mit_aufstieg('Willenskraft', 12)
        m(f"  Willenskraft -> W{s.ch.attribute['Willenskraft'].wuerfel.value}")

        m(f"  Rang: {s.ch.rang}, MP: {s.ch.machtpunkte}")
        m(f"  Talente: {sorted(s.ch.selected_talente)}")
        m(f"  Handicaps: {sorted(s.ch.selected_handicaps)}")
        m(f"  Maechte: {sorted(s.ch.selected_maechte)}")
        diff = s.diff(soll)
        m('DIFF: ' + str(diff['abweichungen']))
        s.speichern(f'chars/Archetypen/Archetyp_Savage_Aventurien_{name}_A.json')
        b = s.bericht(f'logs/{name.lower()}_aventurien_bericht.json')
        m('FERTIG anomalien=%d' % b['anomalien_anzahl'])
    except BaseException as e:
        m('CRASH: %r\n%s' % (e, traceback.format_exc()))
    tlog.close()


if __name__ == '__main__':
    build_alissa()
