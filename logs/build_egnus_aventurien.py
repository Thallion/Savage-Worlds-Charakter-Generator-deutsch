import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/egnus_aventurien_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

def abschliessen(s, n_aufstiege):
    s.ch.char_gen_completed = True
    for _ in range(n_aufstiege): increase_aufstiege(s.ch)
    m(f"  -> chargen abgeschlossen, {n_aufstiege} Aufstiege, Rang={s.ch.rang}")

soll = {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 10, 'Stärke': 6,
                     'Konstitution': 6, 'Willenskraft': 6},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 6, 'Heimlichkeit': 4, 'Überreden': 4,
                     'Wahrnehmung': 6, 'Kämpfen': 6, 'Überleben': 6, 'Reiten': 4,
                     'Einschüchtern': 6, 'Recherche': 6, 'Okkultismus': 6,
                     'Naturwissenschaften': 6, 'Sprache': 6, 'Zaubern': 8, 'Alchemie': 8},
    # Manuell: Feind_schwer, Alt, Talisman_leicht (ueber HP-Limit -> 0 HP, aber angenommen);
    # auto durch AH (Druide): Schwur_schwer, Behindernde_Rüstung_leicht, Materialkomponenten.
    'handicaps':    ['Feind_schwer', 'Alt', 'Talisman_leicht', 'Schwur_schwer',
                     'Behindernde_Rüstung_leicht', 'Materialkomponenten'],
    # Manuell: AH (Druide), Neue Mächte (+_2), Chemiker, Machtpunkte (+_2 frei/Aufstieg);
    # auto durch AH (Druide): Bindung mit der Natur, Naturgespür.
    'talente':      ['AH (Druide)', 'Neue Mächte', 'Neue Mächte_2',
                     'Machtpunkte', 'Machtpunkte_2', 'Chemiker',
                     'Bindung mit der Natur', 'Naturgespür'],
    'maechte':      ['Eigenschaft erhöhen/senken', 'Schutz vor Naturgewalten', 'Geschoss',
                     'Aufspüren', 'Elementarmanipulation', 'Verstricken', 'Furcht',
                     'Betäuben', 'Barriere'],
}

manual_handicaps = ['Feind_schwer', 'Alt']   # beide schwer (je 2 HP) -> Limit 4 voll

try:
    s = d.Sitzung('Savage Aventurien', 'Egnus', protokoll='logs/egnus_aventurien.log')

    # 2  Handicaps (major zuerst; Talisman_leicht als erwartete HP-Limit-Ablehnung versuchen)
    for h in manual_handicaps:
        m(s.handicap(h))
    r = s.handicap('Talisman_leicht')
    m(f"  Talisman_leicht (ueber HP-Limit, erwartet 0 HP): {r}")
    if r.get('ok') and r.get('kosten') == 0:
        s.notiz('Talisman_leicht ueber HP-Limit angenommen mit 0 HP (SWADE-konform); Original-Bogen kassierte dafuer noch 1 HP')
    m(f"  Nach Handicaps: {s.punktestand()}")

    # 3  Volk
    m(s.volk('Mensch'))
    m(f"  Volkswahlen: {s.volk_wahlmoeglichkeiten('Mensch')}")
    # 4  Freies Mensch-Talent = Machtpunkte (braucht AH, der erst spaeter kommt -> ignore + Notiz)
    m(s.volk_freies_talent('Mensch', 'Machtpunkte', ignore_voraussetzungen=True))
    s.notiz('Freies Mensch-Talent Machtpunkte mit ignore_voraussetzungen (AH kommt erst in Schritt 7) - wie Original-Bogen')

    # 5  Attribute (alle W6, exakt 5 Punkte; Verstand W8/W10 erst per Aufstieg)
    for a, z in [('Geschicklichkeit', 6), ('Verstand', 6), ('Stärke', 6),
                 ('Konstitution', 6), ('Willenskraft', 6)]:
        s.attribut_auf(a, z)
    m(f"  Nach Attributen: {s.punktestand()}")

    # 6  Fertigkeiten (Chargen-Ziele; Zaubern/Alchemie nur W6, W8 per Aufstieg.
    #    Ueberleben zuerst - AH-Voraussetzung)
    chargen_ziele = [('Überleben', 6), ('Zaubern', 6), ('Alchemie', 6), ('Kämpfen', 6),
                     ('Recherche', 6), ('Naturwissenschaften', 6), ('Sprache', 6),
                     ('Allgemeinwissen', 6), ('Athletik', 6), ('Wahrnehmung', 6),
                     ('Einschüchtern', 4)]
    for f, z in chargen_ziele:
        if f in s.ch.fertigkeiten:
            s.fertigkeit_auf(f, z)
        else:
            s.notiz(f'FERTIGKEIT-KEY fehlt im Setting: {f}')
    m(f"  Nach Fertigkeiten: {s.punktestand()}")

    # 7  Talente (AH zuerst: WIL W6 + Ueberleben W6 muessen erfuellt sein)
    vor = s.zustand()
    m(s.talent('AH (Druide)'))
    m(f"  Auto-Eintraege nach AH (Druide): {s.zeige_auto_eintraege(vor)}")
    m(s.talent('Neue Mächte'))
    m(f"  Nach Talenten: {s.punktestand()}")

    # 8  Maechte (5 durch AH + 2 durch Neue Maechte = 7)
    for mm in ['Eigenschaft erhöhen/senken', 'Schutz vor Naturgewalten', 'Geschoss',
               'Aufspüren', 'Elementarmanipulation', 'Verstricken', 'Furcht']:
        m(s.macht(mm))

    # 9  Ausruestung
    for name, anz in [('Alchemistentasche', 1), ('Abenteurerpaket', 1),
                      ('Alchemistenpaket', 1), ('Tunika', 1), ('Alchemistenfeuer', 1)]:
        if name in s.ch.ausruestung:
            m(s.kaufen(name, anz))
        else:
            s.notiz(f'FEHLT im Katalog: {name}')
    m(f"  Restpunkte Chargen: {s.punktestand()}")

    # Abschluss + 8 Aufstiege (Bogen: Veteran)
    abschliessen(s, 8)

    # Aufstieg 1+2: Verstand W6->W8->W10 (Bogen: beide bei Anfaenger!)
    m(s.charakter_mit_aufstieg('Verstand', 10))
    m(f"  Verstand nach Aufstiegen: W{s.ch.attribute['Verstand'].wuerfel.value}, {s.punktestand()}")

    # Aufstieg 3: Alchemie W6->W8 + Zaubern W6->W8 (je 0.5)
    m(s.fertigkeit_mit_aufstieg('Alchemie', 8))
    m(s.fertigkeit_mit_aufstieg('Zaubern', 8))

    # Aufstieg 4: Einschuechtern W4->W6 + Reiten aktivieren (je 0.5)
    m(s.fertigkeit_mit_aufstieg('Einschüchtern', 6))
    m(s.fertigkeit_mit_aufstieg('Reiten', 4))

    # Aufstieg 5: Chemiker (Voraussetzung AH (Alchemist) fehlt - Egnus hat AH (Druide))
    m(s.talent('Chemiker', ignore_voraussetzungen=True))
    s.notiz('Chemiker per ignore_voraussetzungen: verlangt in Savage Aventurien AH (Alchemist) + Alchemie W8; Egnus hat AH (Druide) - Bogen/Setting-Konflikt')

    # Aufstieg 6: Neue Maechte_2 + Betaeuben/Barriere
    m(s.talent('Neue Mächte', ignore_rang_check=True))
    m(s.macht('Betäuben', ignore_rang_check=True))
    m(s.macht('Barriere', ignore_rang_check=True))

    # Aufstieg 7: Okkultismus aktivieren + W4->W6 (je 0.5)
    m(s.fertigkeit_mit_aufstieg('Okkultismus', 6))

    # Aufstieg 8: Machtpunkte_2
    m(s.talent('Machtpunkte', ignore_rang_check=True))

    m(f"  Restpunkte Ende: {s.punktestand()}")
    m(f"  Rang: {s.ch.rang}, Machtpunkte: {getattr(s.ch, 'machtpunkte', '?')}")
    m(f"  Talente: {sorted(s.ch.selected_talente)}")
    m(f"  Handicaps: {sorted(s.ch.selected_handicaps)}")

    diff = s.diff(soll)
    m('DIFF: ' + str(diff['abweichungen']))
    s.speichern('chars/Archetypen/Archetyp_Savage_Aventurien_Egnus.json')
    b = s.bericht('logs/egnus_aventurien_bericht.json')
    m('FERTIG anomalien=%d' % b['anomalien_anzahl'])
except BaseException as e:
    m('CRASH: %r\n%s' % (e, traceback.format_exc()))
tlog.close()
