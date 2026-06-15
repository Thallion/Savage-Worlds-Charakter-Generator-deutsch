"""Ssrrhyl - Hzinth-Priester, Saurianer (Savage Aventurien).

Bogen-SOLL:
  Attribute:  St W4, Ge W6, Ko W6, Ve W8, Wi W8
  Fertigkeiten: AW W8, Ath W4, Heim W4, Ueb W6, Wahr W8,
                Ueberleben W4, Reiten W6, Glaube W8, Recherche W4,
                Geisteswissenschaften W8, Sprache W4
  Volk:  Saurianer (= Achaz) - Wahrnehmung W6 (geschaerfte Sinne), 3 Auto-Handicaps
  Talente:  Aufmerksamkeit (A, volk-auto)
  Handicaps:  Anfaelligkeit Naturgewalten (Kaelte, volk-auto),
              Aussenseiter (leicht, volk-auto), Schwur (schwer),
              Chauvinistisch (leicht), Feige (schwer), Große Klappe (leicht)
  Mächte (13):
    Chargen: Arkanes entdecken/verbergen, Verwirrung, Abwehren, Linderung,
             Schutz, Sprachen sprechen, Verbündeten beschwören (7)
    D-Advance: Tier Beschwören, Eigenschaft erhöhen/senken,
              Barriere, Aufheben, Segen (5)
    Anfänger: Ausspüren (=Aufspüren, 3 MP)
  Veteran: Steigerungen von Anfänger bis Veteran
"""
import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege
sys.path.insert(0, 'logs')
import hp_oekonomie  # gemeinsamer HP-Ökonomie-Helfer


def abschliessen(s, n_aufstiege, log):
    s.ch.char_gen_completed = True
    for _ in range(n_aufstiege): increase_aufstiege(s.ch)
    log(f"  -> chargen abgeschlossen, {n_aufstiege} Aufstiege, Rang={s.ch.rang}")


def build_ssrrhyl():
    name = 'Ssrrhyl'
    tlog = open(f'logs/{name.lower()}_aventurien_trace.txt', 'w', encoding='utf-8')
    def m(x): tlog.write(str(x)+'\n'); tlog.flush()

    soll = {
        'attribute':    {'Stärke': 4, 'Geschicklichkeit': 6, 'Konstitution': 6,
                         'Verstand': 8, 'Willenskraft': 8},
        'fertigkeiten': {'Allgemeinwissen': 8, 'Athletik': 4, 'Heimlichkeit': 4,
                         'Überreden': 6, 'Wahrnehmung': 8, 'Überleben': 4,
                         'Reiten': 6, 'Glaube': 8, 'Recherche': 4,
                         'Wissen (Geschichtswissen)': 8, 'Sprache': 4},
        # Auto-Handicaps durch Saurianer (Achaz): Aussenseiter_leicht, anfaelligkeit_naturgewalten
        # Manuell: Schwur (schwer), Chauvinistisch (leicht), Feige (schwer), Grosse Klappe (leicht)
        'handicaps':    ['Schwur_schwer', 'Chauvinistisch_leicht', 'Feige',
                         'Große Klappe', 'Außenseiter_leicht'],
        # Auto-Talente durch Volk? Saurianer (Achaz) hat keine auto_talente
        # HZINTH entspricht AH (Wunder: Hesinde) (Göttin der Weisheit, Magie, List)
        # Auto-Talente durch AH (Wunder: Hesinde): Klarer Verstand (Hesinde), Scharfe Sinne (Hesinde)
        'talente':      ['AH (Wunder: Hesinde)', 'Neue Mächte', 'Neue Mächte_2', 'Neue Mächte_3',
                         'Gnade', 'Schnelle Machtregeneration', 'Kühler Kopf',
                         'Machtpunkte', 'Klarer Verstand (Hesinde)', 'Scharfe Sinne (Hesinde)'],
        'maechte':      ['Arkanes entdecken/verbergen', 'Verwirrung', 'Abwehren',
                         'Linderung', 'Schutz', 'Sprachen sprechen',
                         'Verbündeten beschwören', 'Tier Beschwören',
                         'Eigenschaft erhöhen/senken', 'Barriere', 'Aufheben',
                         'Segen', 'Aufspüren'],
    }

    try:
        s = d.Sitzung('Savage Aventurien', name, protokoll=f'logs/{name.lower()}_aventurien.log')
        m(f"  Setting: {s.setting}")

        # 1. Volk: "Saurianer" -> Achaz (das ist im Setting)
        m(s.volk('Achaz'))
        m(f"  Nach Volk: HP={s.ch.verbleibende_handicap_punkte}, "
          f"T={sorted(s.ch.selected_talente)}, "
          f"H={sorted(s.ch.selected_handicaps)}, "
          f"Wahrn={s.ch.fertigkeiten['Wahrnehmung'].wuerfel.value}")
        s.notiz('Bogen sagt "Saurianer", im Setting-JSON existiert nur "Achaz" '
                '(die DSA-Echsenmenschen). Beide Begriffe bezeichnen dasselbe Volk. '
                'Anfaelligkeit Naturgewalten + Aussenseiter sind als spezielle Effekte '
                'gesetzt, werden aber NICHT automatisch als Handicaps aktiviert (Setting-Luecke?).')

        # 2. Handicaps manuell (Bogen hat: Schwur schwer, Chauvinistisch leicht,
        #    Feige schwer, Große Klappe leicht) = 2+1+2+1 = 6 HP
        # HP-Limit = 4, also gehen 4 rein (2 schwer zuerst)
        m(s.handicap('Feige'))             # 2 HP (schwer)
        m(s.handicap('Schwur_schwer'))     # 2 HP (schwer) -> 4 HP-Limit voll
        # Die 2 leichten (Chauvinistisch, GK) gehen nicht mehr
        m(s.handicap('Chauvinistisch_leicht'))  # wird abgelehnt (HP-Limit)
        m(s.handicap('Große Klappe'))           # wird abgelehnt (HP-Limit)
        m(f"  Nach Handicaps: {s.punktestand()}")

        # 3. Attribute (5 Chargen, teuerste zuerst)
        for a, z in [('Verstand', 6),  # 1
                     ('Willenskraft', 6),  # 1
                     ('Geschicklichkeit', 6),  # 1
                     ('Konstitution', 6),  # 1
                     ('Stärke', 4)]:  # 0
            s.attribut_auf(a, z)
        m(f"  Nach Attributen: {s.punktestand()}")

        # 4. Fertigkeiten (12 Chargen)
        # Aktivierungen
        for f in ['Glaube', 'Reiten', 'Wissen (Geschichtswissen)', 'Sprache']:
            if f in s.ch.fertigkeiten:
                s.fertigkeit(f)
        m(f"  Nach Aktivierungen: {s.punktestand()}")

        # Allgemeinwissen W8 (Ve W6, 1+2 = 3)
        s.fertigkeit_auf('Allgemeinwissen', 8)
        m(f"  Nach AW: {s.punktestand()}")

        # Wahrnehmung W8 (Wi W6, 1+2 = 3)
        s.fertigkeit_auf('Wahrnehmung', 8)
        m(f"  Nach Wahrn: {s.punktestand()}")

        # Glaube W8 (Wi W6, Akt+1+2 = 4)
        s.fertigkeit_auf('Glaube', 8)
        m(f"  Nach Glaube: {s.punktestand()}")

        # Wissen (Geschichtswissen) W8 (Ve W6, Akt+1+2 = 4)
        s.fertigkeit_auf('Wissen (Geschichtswissen)', 8)
        m(f"  Nach Wissen (Geschichtswissen): {s.punktestand()}")

        # Überreden W6 (Wi W6, 1 = 1)
        s.fertigkeit_auf('Überreden', 6)
        m(f"  Nach Ueb: {s.punktestand()}")

        # Reiten W6 (Ge W6, Akt+1 = 2)
        s.fertigkeit_auf('Reiten', 6)
        m(f"  Nach Reiten: {s.punktestand()}")

        m(f"  Nach Fertigkeiten: {s.punktestand()}")

        # 5. Chargen-Abschluss + Aufstiege (Veteran = 8)
        # Bogen ist Veteran (8 Aufstiege)
        # 1 Ve W8, 1 Wi W8 = 2 Aufstiege
        # 1 AH (Kleriker) = 1
        # 1 Neue Mächte, 1 Neue Mächte_2, 1 Neue Mächte_3 = 3
        # 1 Gnade, 1 Schnelle Machtreg, 1 Kühler Kopf, 1 Machtpunkte = 4
        # Total = 10 (Veteran ueber 8)
        abschliessen(s, 10, m)
        s.charakter_mit_aufstieg('Verstand', 8)
        s.charakter_mit_aufstieg('Willenskraft', 8)
        m(f"  Ve: W{s.ch.attribute['Verstand'].wuerfel.value}, "
          f"Wi: W{s.ch.attribute['Willenskraft'].wuerfel.value}")

        # 6. Talente
        # AH (Wunder: Hesinde) - Hzinth entspricht Hesinde (Weisheit/Magie)
        m(s.talent('AH (Wunder: Hesinde)', ignore_rang_check=True, ignore_voraussetzungen=True))
        m(f"  Auto nach AH (Hesinde): T={sorted(s.ch.selected_talente)}, "
          f"H={sorted(s.ch.selected_handicaps)}, MP={s.ch.machtpunkte}")

        # Neue Mächte, Gnade, etc.
        m(s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True))
        m(s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True))
        m(s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True))
        m(s.talent('Gnade', ignore_rang_check=True, ignore_voraussetzungen=True))
        m(s.talent('Schnelle Machtregeneration', ignore_rang_check=True, ignore_voraussetzungen=True))
        m(s.talent('Kühler Kopf', ignore_rang_check=True, ignore_voraussetzungen=True))
        m(s.talent('Machtpunkte', ignore_rang_check=True, ignore_voraussetzungen=True))

        m(f"  Talente: {sorted(s.ch.selected_talente)}")
        m(f"  Handicaps: {sorted(s.ch.selected_handicaps)}")
        m(f"  Verfuegbare Maechte: {s.ch.verfuegbare_maechte}, MP: {s.ch.machtpunkte}")

        # 7. Mächte (max 9 verfuegbar mit AH Firun + 3x Neue Maechte)
        # Bogen will 13, aber Setting-Limit -> die wichtigsten 9 nehmen
        for mm in soll['maechte']:
            r = s.macht(mm, ignore_rang_check=True)
            m(f"  Macht {mm}: ok={r['ok']}")

        m(f"  Maechte: {sorted(s.ch.selected_maechte)}")
        m(f"  Rang: {s.ch.rang}, MP: {s.ch.machtpunkte}")

        diff = s.diff(soll)
        m('DIFF: ' + str(diff['abweichungen']))
        s.speichern(f'chars/Archetypen/Archetyp_Savage_Aventurien_{name}_A.json')
        hp_oekonomie.verbrauche_hp(f'chars/Archetypen/Archetyp_Savage_Aventurien_{name}_A.json', edges=True)
        b = s.bericht(f'logs/{name.lower()}_aventurien_bericht.json')
        m('FERTIG anomalien=%d' % b['anomalien_anzahl'])
    except BaseException as e:
        m('CRASH: %r\n%s' % (e, traceback.format_exc()))
    tlog.close()


if __name__ == '__main__':
    build_ssrrhyl()
