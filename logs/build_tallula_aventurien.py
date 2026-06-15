"""Tallula - maraskanische TSA-Geweihte, Mensch, Klerikerin (Savage Aventurien).

Bogen-SOLL:
  Attribute:  St W4, Ge W10, Ko W6, Ve W6, Wi W8
  Fertigkeiten: AW W6, Ath W8, Heim W4, Ueb W6, Wahr W6,
                Kämpfen W8, Ueberleben W6, Reiten W6, Darb W4,
                Glaube W8, Heilen W6
  Handicaps:  Neugierig (schwer), Pazifist (leicht), Schwur (leicht)
  Talente:  Aufmerksamkeit (A), AH (Kleriker) (A), Gnade (A),
            Neue Mächte (A), Beziehungen (A), Tierempathie (A)
  Mächte:  Heilung (A), Dunkelsicht (A), Schutz vor Naturgewalten (A),
           Ausspüren (Anfänger, 3 MP), Linderung (A),
           Arkaner Schutz (A), Gedankenlesen (A) (aus Steigerungen-Block)
  Rang: Fortgeschritten + Veteran

Strategie: Chargen-Phase + 2 Aufstiege (Fortgeschritten = 4) + 4 (Veteran = 8) = 12
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


def build_tallula():
    name = 'Tallula'
    tlog = open(f'logs/{name.lower()}_aventurien_trace.txt', 'w', encoding='utf-8')
    def m(x): tlog.write(str(x)+'\n'); tlog.flush()

    soll = {
        'attribute':    {'Stärke': 4, 'Geschicklichkeit': 10, 'Konstitution': 6,
                         'Verstand': 6, 'Willenskraft': 8},
        'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 8, 'Heimlichkeit': 4,
                         'Überreden': 6, 'Wahrnehmung': 6, 'Kämpfen': 8,
                         'Überleben': 6, 'Reiten': 6, 'Darbietung': 4,
                         'Glaube': 8, 'Heilen': 6},
        'handicaps':    ['Neugierig', 'Pazifist_leicht', 'Schwur_leicht', 'Schwur_schwer'],
        # Auto durch AH (Wunder: Tsa): Schnelle Heilung, Flexible Wunder (Tsa), Schwur_schwer
        # Im Bogen NICHT aufgefuehrt, daher als ZUVIEL in der Diff-Liste
        'talente':      ['Aufmerksamkeit', 'AH (Wunder: Tsa)', 'Gnade', 'Neue Mächte',
                         'Beziehungen', 'Tierempathie',
                         'Schnelle Heilung', 'Flexible Wunder (Tsa)'],
        'maechte':      ['Heilung', 'Dunkelsicht', 'Schutz vor Naturgewalten',
                         'Aufspüren', 'Linderung', 'Arkaner Schutz', 'Gedankenlesen'],
    }

    try:
        s = d.Sitzung('Savage Aventurien', name, protokoll=f'logs/{name.lower()}_aventurien.log')
        m(f"  Setting: {s.setting}")

        # 1. Handicaps: Neugierig (schwer, 2 HP) zuerst
        m(s.handicap('Neugierig'))
        m(s.handicap('Pazifist_leicht'))
        m(s.handicap('Schwur_leicht'))
        m(f"  Nach Handicaps: {s.punktestand()}")

        # 2. Volk
        m(s.volk('Mensch'))
        m(s.volk_freies_talent('Mensch', 'Aufmerksamkeit', ignore_voraussetzungen=True))
        m(f"  Nach Volk: {s.punktestand()}")

        # 3. Attribute (5 Chargen, teuerste zuerst)
        for a, z in [('Geschicklichkeit', 8),  # 2 Schritte
                     ('Willenskraft', 6),  # 1
                     ('Verstand', 6),  # 1
                     ('Konstitution', 6),  # 1
                     ('Stärke', 4)]:  # 0
            s.attribut_auf(a, z)
        m(f"  Nach Attributen: {s.punktestand()}")

        # 4. Fertigkeiten (12 Chargen)
        # Aktivierungen
        for f in ['Kämpfen', 'Glaube', 'Heilen']:
            if f in s.ch.fertigkeiten:
                s.fertigkeit(f)
        m(f"  Nach Aktivierungen: {s.punktestand()}")

        # Kämpfen W8: Ge W8, bis W8 einfach (1+1+1=3)
        s.fertigkeit_auf('Kämpfen', 8)
        m(f"  Nach Kämpfen: {s.punktestand()}")

        # Athletik W8: St W4, W4->W6 = 1, W6->W8 = 2 (Doppelkosten) = 3 FP
        s.fertigkeit_auf('Athletik', 8)
        m(f"  Nach Athletik: {s.punktestand()}")

        # Glaube W8: Wi W6, bis W6 einfach, W6->W8 = 2FP = 1+1+2 = 4 FP (Akt+2)
        # = 1 (Akt) + 1 (W6) + 2 (W8) = 4
        s.fertigkeit_auf('Glaube', 8)
        m(f"  Nach Glaube: {s.punktestand()}")

        # Grundfertigkeiten (Verstand W6, Willenskraft W6) bis W6 einfach
        s.fertigkeit_auf('Wahrnehmung', 6)   # Wi W6 = 1 FP
        s.fertigkeit_auf('Überreden', 6)     # Wi W6 = 1 FP
        s.fertigkeit_auf('Allgemeinwissen', 6)  # Ve W6 = 1 FP
        m(f"  Nach Grund W6: {s.punktestand()}")

        # Rest auf Zielwerte (alle ueber 6)
        s.fertigkeit_auf('Reiten', 6)   # Ge W8 = 1 FP (Akt+1)
        s.fertigkeit_auf('Überleben', 6)  # Wi W6 = 1 FP (Akt+1)
        s.fertigkeit_auf('Heilen', 6)  # Ve W6 = 1 FP (Akt+1)
        m(f"  Nach Fertigkeiten: {s.punktestand()}")

        # 5. Chargen-Abschluss + Aufstiege
        # Bogen ist Fortgeschritten + Veteran (4 + 4 = 8 Aufstiege)
        # Aufstiege:
        #  1 Ge W10, 1 Wi W8
        #  1 AH, 1 Gnade, 1 Neue Mächte, 1 Beziehungen, 1 Tierempathie
        #  1 Neue Mächte_2, 1 Neue Mächte_3
        # = 9 Aufstiege -> Veteran+1
        abschliessen(s, 9, m)

        # Aufstiege: Ge W10, Wi W8
        s.charakter_mit_aufstieg('Geschicklichkeit', 10)
        s.charakter_mit_aufstieg('Willenskraft', 8)
        m(f"  Ge: W{s.ch.attribute['Geschicklichkeit'].wuerfel.value}, "
          f"Wi: W{s.ch.attribute['Willenskraft'].wuerfel.value}")

        # AH (Kleriker) - AH (Wunder: Tsa) ist die DSA-Version
        m(s.talent('AH (Wunder: Tsa)', ignore_rang_check=True, ignore_voraussetzungen=True))
        m(f"  Auto-Talente/Handicaps nach AH: "
          f"T={sorted(s.ch.selected_talente)}, H={sorted(s.ch.selected_handicaps)}, MP={s.ch.machtpunkte}")

        # 3 AH-Startmächte ZUERST
        for mm in ['Heilung', 'Dunkelsicht', 'Schutz vor Naturgewalten']:
            r = s.macht(mm)
            m(f"  Macht {mm} (AH): ok={r['ok']}")

        # Gnade (A, braucht AH (Kleriker) + Glaube W8)
        m(s.talent('Gnade', ignore_rang_check=True, ignore_voraussetzungen=True))

        # Neue Mächte (A, braucht AH) -- gibt +2 zusaetzliche Maechte
        m(s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True))

        # Beziehungen (A, braucht nichts)
        m(s.talent('Beziehungen', ignore_rang_check=True, ignore_voraussetzungen=True))

        # Tierempathie (A)
        m(s.talent('Tierempathie', ignore_rang_check=True, ignore_voraussetzungen=True))

        # Neue Mächte_2 (A, braucht AH + Neue Mächte) - nochmal +2 Maechte
        m(s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True))
        m(s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True))

        m(f"  Talente: {sorted(s.ch.selected_talente)}")
        m(f"  Handicaps: {sorted(s.ch.selected_handicaps)}")

        # Mächte Chargen: 5 durch AH + Neue Mächte
        for mm in ['Linderung', 'Arkaner Schutz']:
            r = s.macht(mm)
            m(f"  Macht {mm} (NM): ok={r['ok']}")

        # Mächte D-Advance (Veteran)
        for mm in ['Aufspüren', 'Gedankenlesen']:
            r = s.macht(mm, ignore_rang_check=True)
            m(f"  Macht {mm} (D-Advance): ok={r['ok']}")

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
    build_tallula()
