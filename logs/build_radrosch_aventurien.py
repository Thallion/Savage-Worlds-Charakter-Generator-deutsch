"""Radrosch, Sohn des Ragabosch - Geode, Zwerg, Elementarist (Savage Aventurien).

Bogen-SOLL:
  Attribute:  St W6, Ge W6, Ko W6, Ve W8, Wi W8
  Fertigkeiten: AW W4, Ath W6, Heim W4, Ueb W6, Wahr W4,
                Kämpfen W6, Ueberleben W8, Reiten W4, Einschüchtern W8,
                Heilen W6, Zaubern W6
  Handicaps:  Verringerte Bewegungsweite (Volks-Automatik)
  Volk:  Zwerg -> Konstitution +2, +3 Auto-Handicaps (Langsam_leicht, Phobie_schwer, Stur),
         Arkane Resistenz (auto), Dunkelsicht, Steingespür, Hitzeresistenz, Magische Abwehr
  Talente:  AH (Elementarist) (A, +5 Maechte), Tiermeister (A), Machtpunkte (A, +5 MP),
            Tierempathie (A), Naturbursche (A), Neue Mächte (A), Elementarer Meister (F)
  Mächte:  Elementarmanipulation (A), Schutz vor Naturgewalten (A),
           Eigenschaft erhöhen/senken (A), Graben (A), Verbündeten beschwören (A),
           Barriere (F), Wachsen/Schrumpfen (F)
  Waffen:  Stab
  Rüstung:  Robe mit Kapuze + Beinlinge

Anomalie-Notiz: 'Wissen (Geschichtswissen)' in den Wissen-Werten nicht relevant
(fuer Radrosch ist Wissen-Magie = 'Wissen (Magie & Sphaerenkunde)' gemeint)
"""
import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege


def abschliessen(s, n_aufstiege, log):
    s.ch.char_gen_completed = True
    for _ in range(n_aufstiege): increase_aufstiege(s.ch)
    log(f"  -> chargen abgeschlossen, {n_aufstiege} Aufstiege, Rang={s.ch.rang}")


def build_radrosch():
    name = 'Radrosch'
    tlog = open(f'logs/{name.lower()}_aventurien_trace.txt', 'w', encoding='utf-8')
    def m(x): tlog.write(str(x)+'\n'); tlog.flush()

    soll = {
        'attribute':    {'Stärke': 6, 'Geschicklichkeit': 6, 'Konstitution': 6,
                         'Verstand': 8, 'Willenskraft': 8},
        'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Heimlichkeit': 4,
                         'Überreden': 6, 'Wahrnehmung': 4, 'Kämpfen': 6,
                         'Überleben': 8, 'Reiten': 4, 'Einschüchtern': 8,
                         'Heilen': 6, 'Zaubern': 6},
        # Auto-Handicaps durch Zwerg: Langsam_leicht, Phobie_schwer, Stur
        # Auto-Handicap durch AH (Elementarist): Behindernde_Rüstung_schwer
        'handicaps':    ['Langsam_leicht', 'Phobie_schwer', 'Stur',
                         'Behindernde_Rüstung_schwer'],
        # Auto-Talente durch Zwerg: Arkane Resistenz
        'talente':      ['Arkane Resistenz',
                         'AH (Elementarist)', 'Tiermeister', 'Machtpunkte',
                         'Tierempathie', 'Naturbursche', 'Neue Mächte', 'Elementarer Meister'],
        'maechte':      ['Elementarmanipulation', 'Schutz vor Naturgewalten',
                         'Eigenschaft erhöhen/senken', 'Graben',
                         'Verbündeten beschwören', 'Barriere', 'Wachsen/Schrumpfen'],
    }

    try:
        s = d.Sitzung('Savage Aventurien', name, protokoll=f'logs/{name.lower()}_aventurien.log')
        m(f"  Setting: {s.setting}")

        # 1. Volk Zwerg (bringt Volks-Boni + 3 Auto-Handicaps + Arkane Resistenz)
        m(s.volk('Zwerg'))
        m(f"  Nach Volk: HP={s.ch.verbleibende_handicap_punkte}, "
          f"T={sorted(s.ch.selected_talente)}, "
          f"H={sorted(s.ch.selected_handicaps)}, "
          f"Konst={s.ch.attribute['Konstitution'].wuerfel.value}")
        # Bogen: Verringerte Bewegungsweite = setzt bonus -1
        # Schauen wir ob das automatisch ging

        # 2. Attribute (5 Chargen, teuerste zuerst)
        # Konstitution hat Volks-Bonus +2, ist also schon W6 (Bonus). Aber wir wollen W6 = kein Schritt noetig
        # Verstand W8 (=2 Schritte), Willenskraft W8 (=2 Schritte), St+Ge W6 (je 1)
        # Total 6 Schritte, mit 5 Chargen-Punkten reicht nicht!
        # Strategie: 4 Chargen-Attr (St, Ge, Ve, Wi je 1 Schritt = 4) + 2 via 2x HP
        # Bzw: Volks-Bonus Konstitution = +2, d.h. Konst schon W6
        for a, z in [('Verstand', 6),  # 1 Schritt
                     ('Willenskraft', 6),  # 1
                     ('Stärke', 6),  # 1
                     ('Geschicklichkeit', 6)]:  # 1
            s.attribut_auf(a, z)
        m(f"  Nach Attributen: {s.punktestand()}")

        # 3. Fertigkeiten (12 Chargen)
        # Aktivierungen
        for f in ['Kämpfen', 'Überleben', 'Einschüchtern', 'Heilen', 'Zaubern',
                  'Athletik', 'Überreden']:
            if f in s.ch.fertigkeiten:
                s.fertigkeit(f)
        m(f"  Nach Aktivierungen: {s.punktestand()}")

        # Strategie: hohe Werte zuerst
        # Ueberleben W8 (Wi W6, W6->W8 = 2 = 1+2 = 3)
        s.fertigkeit_auf('Überleben', 8)
        m(f"  Nach Ueberleben: {s.punktestand()}")

        # Einschüchtern W8 (St W6, 1+2 = 3)
        s.fertigkeit_auf('Einschüchtern', 8)
        m(f"  Nach Einschüchtern: {s.punktestand()}")

        # Athletik W6 (St W6, 1 = 1)
        s.fertigkeit_auf('Athletik', 6)
        m(f"  Nach Athletik: {s.punktestand()}")

        # Überreden W6 (Wi W6, 1 = 1)
        s.fertigkeit_auf('Überreden', 6)
        m(f"  Nach Ueberreden: {s.punktestand()}")

        # Kämpfen W6 (St W6, Akt+1 = 2)
        s.fertigkeit_auf('Kämpfen', 6)
        m(f"  Nach Kämpfen: {s.punktestand()}")

        # Heilen W6 (Ve W6, Akt+1 = 2)
        s.fertigkeit_auf('Heilen', 6)
        m(f"  Nach Heilen: {s.punktestand()}")

        # Zaubern W6 (Ve W6, Akt+1 = 2)
        s.fertigkeit_auf('Zaubern', 6)
        m(f"  Nach Zaubern: {s.punktestand()}")

        m(f"  Nach Fertigkeiten: {s.punktestand()}")

        # 4. Chargen-Abschluss + Aufstiege
        # 7 Talente (1 Aufstieg je) = 7
        # Ve W8 + Wi W8 (je 1 Attribut-Aufstieg) = 2
        # Total 9 -> 9 Aufstiege
        abschliessen(s, 9, m)
        s.charakter_mit_aufstieg('Verstand', 8)
        s.charakter_mit_aufstieg('Willenskraft', 8)
        m(f"  Ve: W{s.ch.attribute['Verstand'].wuerfel.value}, "
          f"Wi: W{s.ch.attribute['Willenskraft'].wuerfel.value}")

        # 5. Talente
        # AH (Elementarist) - 5 neue Maechte, +5 MP
        m(s.talent('AH (Elementarist)', ignore_rang_check=True, ignore_voraussetzungen=True))
        m(f"  Auto nach AH: MP={s.ch.machtpunkte}, "
          f"verfuegbare_maechte={s.ch.verfuegbare_maechte}")

        # Tiermeister (A, keine Voraussetzungen)
        m(s.talent('Tiermeister', ignore_rang_check=True, ignore_voraussetzungen=True))

        # Machtpunkte (A, +5 MP, aber wir haben schon welche)
        m(s.talent('Machtpunkte', ignore_rang_check=True, ignore_voraussetzungen=True))

        # Tierempathie (A)
        m(s.talent('Tierempathie', ignore_rang_check=True, ignore_voraussetzungen=True))

        # Naturbursche (A)
        m(s.talent('Naturbursche', ignore_rang_check=True, ignore_voraussetzungen=True))

        # Neue Mächte (A, braucht AH)
        m(s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True))

        # Elementarer Meister (F, +1 Element, braucht AH Elementarist)
        m(s.talent('Elementarer Meister', ignore_rang_check=True, ignore_voraussetzungen=True))

        m(f"  Talente: {sorted(s.ch.selected_talente)}")
        m(f"  Handicaps: {sorted(s.ch.selected_handicaps)}")
        m(f"  Verfuegbare Maechte: {s.ch.verfuegbare_maechte}, MP: {s.ch.machtpunkte}")

        # 6. Maechte
        # Bogen: 5 AH-Mächte + 2 Neue Mächte = 7
        for mm in soll['maechte']:
            r = s.macht(mm)
            m(f"  Macht {mm}: ok={r['ok']}")

        m(f"  Maechte: {sorted(s.ch.selected_maechte)}")
        m(f"  Rang: {s.ch.rang}, MP: {s.ch.machtpunkte}")

        diff = s.diff(soll)
        m('DIFF: ' + str(diff['abweichungen']))
        s.speichern(f'chars/Archetypen/Archetyp_Savage_Aventurien_{name}_A.json')
        b = s.bericht(f'logs/{name.lower()}_aventurien_bericht.json')
        m('FERTIG anomalien=%d' % b['anomalien_anzahl'])
    except BaseException as e:
        m('CRASH: %r\n%s' % (e, traceback.format_exc()))
    tlog.close()


if __name__ == '__main__':
    build_radrosch()
