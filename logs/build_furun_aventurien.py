"""Furun - Duellant, Mensch, Kämpfer (Savage Aventurien).

Bogen-SOLL:
  Attribute:  St W8, Ge W8, Ko W6, Ve W6, Wi W6 (7 Schritte, brauchen 5 Chargen + 1 Aufstieg)
  Fertigkeiten: AW W4, Ath W6, Heim W6, Ueb W4, Wahr W6,
                Kämpfen W10, Ueberleben W4, Reiten W6, Glaube W4,
                Heilen W4, Wissen (Goetter) W6
  Handicaps:  Grosse Klappe (leicht), Impulsiv (schwer), Sanftmuetig (leicht) = 4 HP
  Talente:  Aufmerksamkeit (A, volk-frei), Beidhändig (A, GES W8),
            Beidhändiger Kampf (A, GES W8 + Beidhändig),
            Blitzschneller Angriff (V, Schneller Angriff),
            Block (F, Kämpfen W8), Harter Block (V, Block),
            Schnell (A, GES W8), Schneller Angriff (F, Kämpfen W8),
            Riposte (F, Kämpfen W8)

Schwierigkeit: Viele Talente (8) kosten je 2 HP = 16 HP. Mit max 4 HP nur 2 Talente.
Loesung: Chargen-Phase = nur 2 Talente, Rest ueber Aufstiege.
"""
import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege


def abschliessen(s, n_aufstiege, log):
    s.ch.char_gen_completed = True
    for _ in range(n_aufstiege): increase_aufstiege(s.ch)
    log(f"  -> chargen abgeschlossen, {n_aufstiege} Aufstiege, Rang={s.ch.rang}")


def build_furun():
    name = 'Furun'
    tlog = open(f'logs/{name.lower()}_aventurien_trace.txt', 'w', encoding='utf-8')
    def m(x): tlog.write(str(x)+'\n'); tlog.flush()

    soll = {
        'attribute':    {'Stärke': 8, 'Geschicklichkeit': 8, 'Konstitution': 6,
                         'Verstand': 6, 'Willenskraft': 6},
        'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Heimlichkeit': 6,
                         'Überreden': 4, 'Wahrnehmung': 6, 'Kämpfen': 10,
                         'Überleben': 4, 'Reiten': 6, 'Glaube': 4,
                         'Heilen': 4, 'Wissen (Götter & Kulte)': 6},
        'handicaps':    ['Große Klappe', 'Impulsiv', 'Sanftmütig'],
        'talente':      ['Beidhändig', 'Beidhändiger Kampf', 'Blitzschneller Angriff',
                         'Block', 'Harter Block', 'Schnell', 'Schneller Angriff',
                         'Riposte', 'Aufmerksamkeit'],
        'maechte':      [],
    }

    try:
        s = d.Sitzung('Savage Aventurien', name, protokoll=f'logs/{name.lower()}_aventurien.log')
        m(f"  Setting: {s.setting}")

        # 1. Handicaps: Impulsiv (schwer) zuerst
        m(s.handicap('Impulsiv'))
        m(s.handicap('Große Klappe'))
        m(s.handicap('Sanftmütig'))
        m(f"  Nach Handicaps: {s.punktestand()}")

        # 2. Volk
        m(s.volk('Mensch'))
        m(s.volk_freies_talent('Mensch', 'Aufmerksamkeit', ignore_voraussetzungen=True))
        m(f"  Nach Volk: {s.punktestand()}")

        # 3. Attribute (5 Chargen)
        # Strategie: St statt Ge auf W6 setzen, damit Kämpfen W10 KEINE Doppelkosten hat
        #   (St = regierendes Attribut, St W6 = Kämpfen bis W6 einfach)
        for a, z in [('Stärke', 6),  # 1
                     ('Konstitution', 6),  # 1
                     ('Verstand', 6),  # 1
                     ('Willenskraft', 6),  # 1
                     ('Geschicklichkeit', 4)]:  # 0 (bleibt W4)
            s.attribut_auf(a, z)
        m(f"  Nach Attributen: {s.punktestand()}")

        # 4. Fertigkeiten (12 Chargen)
        # Aktivierungen
        for f in ['Kämpfen', 'Reiten', 'Glaube', 'Heilen', 'Wissen (Götter & Kulte)']:
            if f in s.ch.fertigkeiten:
                s.fertigkeit(f)  # Aktivierung
        m(f"  Nach Aktivierungen: {s.punktestand()}")

        # Kämpfen W10: St W6 -> bis W6 einfach, W6->W8 = 2FP (Doppelkosten weil St=W6=Ge), W8->W10 = 2FP
        # Hmm, Doppelkosten weil St W6 = Kämpfen W6 -> trotzdem 2 FP
        # Mit St W8: W4+W6+W8+W10 = 1+1+1+1 = 4 FP total
        s.fertigkeit_auf('Kämpfen', 8)  # erstmal W8 (St W6, 1+1+2=4 FP)
        m(f"  Nach Kämpfen W8: {s.punktestand()}")

        # Rest auf Zielwerte
        s.fertigkeit_auf('Athletik', 6)      # St W6, bis W6 einfach = 1 FP
        s.fertigkeit_auf('Heimlichkeit', 6)  # Ge W4 -> W6 = 1+1=2 FP (kein Doppelkosten)
        s.fertigkeit_auf('Reiten', 6)        # Ge W4 = 2 FP
        s.fertigkeit_auf('Wahrnehmung', 6)   # Wi W6 = 1 FP
        s.fertigkeit_auf('Wissen (Götter & Kulte)', 6)  # Ve W6 = 1 FP
        m(f"  Nach Fertigkeiten: {s.punktestand()}")

        # 5. Chargen-Abschluss + Aufstiege
        # 1 St W8, 1 Ge W8, 2 Kämpfen W10 (W8->W10), 1 Wissen W6, 8 Talente = 13
        abschliessen(s, 13, m)

        # Aufstiege: St W8, Ge W8, Kämpfen W10, Wissen (Götter) W6
        s.charakter_mit_aufstieg('Stärke', 8)
        s.charakter_mit_aufstieg('Geschicklichkeit', 8)
        s.fertigkeit_mit_aufstieg('Kämpfen', 10)
        s.fertigkeit_mit_aufstieg('Wissen (Götter & Kulte)', 6)
        m(f"  St: W{s.ch.attribute['Stärke'].wuerfel.value}, "
          f"Ge: W{s.ch.attribute['Geschicklichkeit'].wuerfel.value}, "
          f"Kämpfen: W{s.ch.fertigkeiten['Kämpfen'].wuerfel.value}, "
          f"Wissen (Götter): W{s.ch.fertigkeiten['Wissen (Götter & Kulte)'].wuerfel.value}")

        # Talente: Aufstiege verteilen
        for t in ['Beidhändig', 'Schnell', 'Block', 'Schneller Angriff',
                  'Riposte', 'Harter Block', 'Beidhändiger Kampf',
                  'Blitzschneller Angriff']:
            r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
            m(f"  Talent {t}: ok={r['ok']}")

        m(f"  Talente: {sorted(s.ch.selected_talente)}")
        m(f"  Handicaps: {sorted(s.ch.selected_handicaps)}")
        diff = s.diff(soll)
        m('DIFF: ' + str(diff['abweichungen']))
        s.speichern(f'chars/Archetypen/Archetyp_Savage_Aventurien_{name}_A.json')
        b = s.bericht(f'logs/{name.lower()}_aventurien_bericht.json')
        m('FERTIG anomalien=%d' % b['anomalien_anzahl'])
    except BaseException as e:
        m('CRASH: %r\n%s' % (e, traceback.format_exc()))
    tlog.close()


if __name__ == '__main__':
    build_furun()
