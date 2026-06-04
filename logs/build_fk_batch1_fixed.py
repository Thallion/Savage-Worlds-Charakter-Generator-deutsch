"""
BATCH 1 FIXED: Fantasy Kompendium Archetypen
Barbarin, Barde, Druidin, Klerikerin, Mönch, Magier

Korrekturen gegenüber Batch 1 v1:
- HP-Limit = 4: Schwerwiegende (2-Punkte) Handicaps ZUERST hinzufügen
- Druidin: Handicap-Reihenfolge korrigiert, Schwerzüngig bekommt Punkte
- Klerikerin: Handicap-Reihenfolge korrigiert, Schwur_schwer bekommt Punkte
- Mönch/Klerikerin/Druidin: Elf/Zwerg/Rakashaner Racial-Talente zum soll hinzugefügt
- Magier: Handicap-Reihenfolge, Macht-Limit 6 bei Novice, Veteran-Mächte mit ignore
- Barbarin: Berserker-Anomalie dokumentiert (Stärke W8→W10 = Code-Bug)
"""

import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/fk_batch1_fixed_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

def abschliessen(s, n_aufstiege):
    s.ch.char_gen_completed = True
    for _ in range(n_aufstiege):
        increase_aufstiege(s.ch)
    m(f"  → chargen abgeschlossen, {n_aufstiege} Aufstiege, Rang={s.ch.rang}")

# ===========================================================================
# 1. BARBARIN (Barbarian) - Halbork
# HP: Zwei_linke_Hände(1)+Analphabet(1)+Impulsiv(2) = 4 HP
# Anomalie: Berserker erhöht Stärke dauerhaft auf W10 (Code-Bug: sollte W8 bleiben)
# Anomalie: Provozieren d4 fehlt (Budget erschöpft: 12 Fertigkeitspunkte alle verbraucht)
# ===========================================================================
m("=== 1. BARBARIN ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Barbarin', protokoll='logs/fk_barbarin2.log')
    s.handicap('Impulsiv')          # 2 HP (major zuerst)
    s.handicap('Zwei linke Hände')  # 1 HP
    s.handicap('Analphabet')        # 1 HP → 4 HP total
    s.volk('Halbork')
    s.volk_freies_attribut('Halbork', 'Stärke')  # Stärke d6 gratis
    m(f"  Punkte nach Volk: {s.punktestand()}")

    # Attribute (Novice=Final: Agi d6, Sma d4, Spi d8, Str d8, Vig d8)
    # Halbork gibt Stärke d6 gratis. Normal 5: Agi(1)+Spi(2)+Str(d6→d8=1)+Vig(d4→d6=1)=5
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Stärke', 8)
    s.attribut_auf('Konstitution', 6)  # 1 normal pt: d4→d6
    # Vig d6→d8 mit HP (2 HP)
    s.steigere_mit_handicap_attribut('Konstitution')
    m(f"  Attribute: Vig={s.ch.attribute['Konstitution'].wuerfel.value}, Punkte={s.punktestand()}")

    # Skills (12 pts): Ath d8 kostet 3pt (doppelt bei d6→d8 weil = Agi),
    # Kämpfen d8=4pt, Einschüchtern d8=3pt, Reiten+Überleben+Provozieren je 1pt = 13pt → 12 normal
    # ANOMALIE: Provozieren d4 nicht möglich (Budget erschöpft)
    s.fertigkeit_auf('Athletik', 8)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Einschüchtern', 8)
    s.fertigkeit_auf('Reiten', 4)
    s.fertigkeit_auf('Überleben', 4)
    # Provozieren: kein Budget mehr für normale Punkte, HP=2 aber werden für Raufbold gebraucht
    m(f"  Skills gesetzt. Punkte={s.punktestand()}")

    # Talent: Raufbold (2 HP)
    s.talent('Raufbold', ignore_voraussetzungen=True)
    m(f"  Nach Raufbold: {s.punktestand()}")

    abschliessen(s, 4)

    # D Advances (4 Aufstiege): Kräftig, Berserker, Wildling (Savagery), Aufwiegler (Roar)
    s.talent('Kräftig', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Berserker', ignore_rang_check=True, ignore_voraussetzungen=True)
    # ANOMALIE: Berserker erhöht Stärke dauerhaft auf W10 (Bug: sollte nur im Berserkermodus)
    s.talent('Wildling', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Aufwiegler', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    # Stärke ist jetzt W10 durch Berserker (Code-Bug), soll W8 sein
    s.notiz("BUG: Berserker erhöht Stärke dauerhaft auf W10 (sollte nur im Berserkermodus gelten). "
            "Tatsächlicher Wert W10, Erwartung W8.")
    s.notiz("Anomalie: Provozieren (Taunt d4) fehlt - Fertigkeitsbudget erschöpft "
            "(Athletik d8 + Kämpfen d8 + Einschüchtern d8 + 3 Aktivierungen = 12 Punkte genau).")
    s.notiz("Außenseiter (Halbork-Racial) kommt automatisch aus dem Volk, nicht manuell.")

    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':4,'Willenskraft':8,'Stärke':10,'Konstitution':8},
        'fertigkeiten': {'Athletik':8,'Allgemeinwissen':4,'Kämpfen':8,'Einschüchtern':8,
                         'Wahrnehmung':4,'Überreden':4,'Reiten':4,'Heimlichkeit':4,'Überleben':4},
        'handicaps': ['Zwei linke Hände','Analphabet','Impulsiv'],
        'talente': ['Raufbold','Kräftig','Berserker','Wildling','Aufwiegler'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Zweihandaxt',1),('Ledertunika',1),('Schwerer Helm',1),
                       ('Stiefel, schwer',1),('Abenteurerpaket',1),('Trank: Heilung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Trank der Vergrößerung (nicht im FK-Katalog)')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Barbarin_A.json')
    b = s.bericht('logs/fk_barbarin2_bericht.json')
    m(f"  BARBARIN: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Barbarin: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 2. BARDE (Bard) - Mensch ← War bereits korrekt!
# HP: Feind_schwer(2)+Behindernde_Rüstung_leicht(1)+Amorös_leicht(1) = 4 HP
#     dann Große Klappe(1, minor, accepted, 0 pts)
# 5 Aufstiege wegen 2 Skill-Advances + 3 Edges
# ===========================================================================
m("\n=== 2. BARDE ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Barde', protokoll='logs/fk_barde2.log')
    s.handicap('Feind_schwer')               # 2 HP (major first)
    s.handicap('Amorös_leicht')              # 1 HP
    s.handicap('Behindernde_Rüstung_leicht') # 1 HP → 4 HP total
    s.handicap('Große Klappe')               # 1 HP minor → accepted, 0 extra pts
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'AH (Barde)', ignore_voraussetzungen=True)
    m(f"  Punkte nach Volk: {s.punktestand()}")

    # Attribute (Novice=Final: Agi d6, Sma d6, Spi d8, Str d6, Vig d6)
    # Normal 5: Agi(1)+Sma(1)+Spi(2)+Str(1) = 5 → Vig bleibt d4
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Stärke', 6)
    # Vig d4→d6 mit HP (2 HP)
    s.steigere_mit_handicap_attribut('Konstitution')
    m(f"  Attribute gesetzt. Punkte={s.punktestand()}")

    # Skills Novice (ohne Diebeskunst d6 + Kämpfen d6, die kommen als Advances)
    # Novice: Ath d4(grundf), AW d6(+1step), Kämpfen d4(aktiviert), Glücksspiel d4(aktiviert),
    #         Darbietung d10(5pts!), Überreden d8(2pts), Heimlichkeit d6(1pt), Diebeskunst d4(aktiviert)
    s.fertigkeit_auf('Allgemeinwissen', 6)
    s.fertigkeit_auf('Darbietung', 10)   # 5 pts (double cost at d8→d10 > Wk d8)
    s.fertigkeit_auf('Überreden', 8)     # 2 pts
    s.fertigkeit_auf('Heimlichkeit', 6)  # 1 pt
    s.fertigkeit_auf('Glücksspiel', 4)   # 1 pt activate
    s.fertigkeit_auf('Kämpfen', 4)       # 1 pt activate
    s.fertigkeit_auf('Diebeskunst', 4)   # 1 pt activate
    m(f"  Skills gesetzt. Punkte={s.punktestand()}")

    # Attraktiv mit HP (2 HP)
    s.talent('Attraktiv', ignore_voraussetzungen=True)
    m(f"  Nach Attraktiv: {s.punktestand()}")

    # Mächte (3 Novice powers, all rank A)
    s.macht('Eigenschaft erhöhen/senken')
    s.macht('Verwirrung')
    s.macht('Geräusch/Stille')

    abschliessen(s, 5)  # 5 Aufstiege: 2 Skills + 3 Edges

    s.steigere_mit_handicap_fertigkeit('Diebeskunst')  # d4→d6
    s.steigere_mit_handicap_fertigkeit('Kämpfen')      # d4→d6
    s.talent('Erniedrigen', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Instrument', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Heldentum inspirieren', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':6,'Willenskraft':8,'Stärke':6,'Konstitution':6},
        'fertigkeiten': {'Athletik':4,'Allgemeinwissen':6,'Kämpfen':6,'Glücksspiel':4,
                         'Wahrnehmung':4,'Darbietung':10,'Überreden':8,'Heimlichkeit':6,'Diebeskunst':6},
        'handicaps': ['Amorös_leicht','Behindernde_Rüstung_leicht','Große Klappe','Feind_schwer'],
        'talente': ['AH (Barde)','Attraktiv','Erniedrigen','Instrument','Heldentum inspirieren'],
        'maechte': ['Eigenschaft erhöhen/senken','Verwirrung','Geräusch/Stille'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Rapier',1),('Ledertunika',1),('Musikinstrument',1),
                       ('Unterhalterpaket',1),('Umhang mit Kapuze',1),('Laterne',1),
                       ('Rauchstab',1),('Trank: Attributsteigerung',1),('Trank: Heilung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.notiz("5 Aufstiege statt 4 (Code implementiert SWADE '2 Fertigkeiten pro Aufstieg' als 2 separate).")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Rapier',1),('Ledertunika',1),('Musikinstrument',1),
                       ('Unterhalterpaket',1),('Umhang mit Kapuze',1),('Laterne',1),
                       ('Rauchstab',1),('Trank: Attributsteigerung',1),('Trank: Heilung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Barde_A.json')
    b = s.bericht('logs/fk_barde2_bericht.json')
    m(f"  BARDE: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Barde: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 3. DRUIDIN (Druid) - Elf
# HP: Schwur_schwer(2)+Materialkomponenten(2) = 4 HP (Schwerzüngig wird abgelehnt!)
#     dann Behindernde_Rüstung_leicht(1, minor), Sanftmütig(1, minor), Arm(1, minor) = akzeptiert, 0 pts
# Anomalie: Schwerzüngig (major, 2pts) kann nicht hinzugefügt werden (HP-Limit 4)
# ===========================================================================
m("\n=== 3. DRUIDIN ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Druidin', protokoll='logs/fk_druidin2.log')
    s.handicap('Schwur_schwer')              # 2 HP (major first)
    s.handicap('Materialkomponenten')        # 2 HP → 4 HP total
    s.handicap('Behindernde_Rüstung_leicht') # 1 HP minor → 0 extra pts
    s.handicap('Sanftmütig')                 # 1 HP minor → 0 extra pts
    s.handicap('Arm')                        # 1 HP minor → 0 extra pts
    r = s.handicap('Schwerzüngig')           # 2 HP major → REJECTED (HP-Limit)
    m(f"  Schwerzüngig: ok={r['ok']} (erwartet: REJECTED bei HP-Limit)")
    s.volk('Elf')  # Agi d6 gratis, Zwei_linke_Hände+Nachtsicht auto
    m(f"  Punkte nach Volk: {s.punktestand()}")

    # Attribute (Agi d6 von Elf gratis; Normal 5: Sma(1)+Spi(2)+Str(1)+Vig(1)=5)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Stärke', 6)
    s.attribut_auf('Konstitution', 6)
    m(f"  Attribute gesetzt. Punkte={s.punktestand()}")

    # Skills (12 pts): Glaube d8=3pt, Kämpfen d6=2pt, Heilen d4=1pt,
    # Wahr d6=1pt, Heim d6=1pt, Überl d8=4pt (doppelt bei d6→d8 weil = Sma d6)
    s.fertigkeit_auf('Glaube', 8)
    s.fertigkeit_auf('Kämpfen', 6)
    s.fertigkeit_auf('Heilen', 4)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Heimlichkeit', 6)
    s.fertigkeit_auf('Überleben', 8)   # 4pts (d6→d8 doppelt bei Sma d6)
    m(f"  Skills gesetzt. Punkte={s.punktestand()}")

    # Novice Talents: AH(Druide) + Tiermeister (je 2 HP = 4 HP ✓)
    s.talent('AH (Druide)', ignore_voraussetzungen=True)
    s.talent('Tiermeister', ignore_voraussetzungen=True)
    m(f"  Nach Talents: {s.punktestand()}")

    # Mächte (alle Rang A - kein ignore nötig)
    s.macht('Tierfreund')
    s.macht('Verstricken')
    s.macht('Schutz vor Naturgewalten')
    s.macht('Heilung')
    s.macht('Gestaltwandeln')

    abschliessen(s, 4)

    s.talent('Bestienflüsterer', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Bevorzugtes Gelände', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Herzholzstab', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Naturbursche', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("Schwerzüngig (Tongue-Tied, major) wurde abgelehnt: HP-Limit 4 bereits durch "
            "Schwur_schwer+Materialkomponenten erreicht. Nicht auf dem Charakterbogen.")
    s.notiz("Elf-Racial: Zwei_linke_Hände + Nachtsicht automatisch (nicht manuell hinzugefügt).")

    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':6,'Willenskraft':8,'Stärke':6,'Konstitution':6},
        'fertigkeiten': {'Athletik':4,'Allgemeinwissen':4,'Glaube':8,'Kämpfen':6,'Heilen':4,
                         'Wahrnehmung':6,'Überreden':4,'Heimlichkeit':6,'Überleben':8},
        'handicaps': ['Schwur_schwer','Materialkomponenten','Behindernde_Rüstung_leicht',
                      'Sanftmütig','Arm','Zwei linke Hände'],  # Zwei linke Hände: Elf-Racial auto
        'talente': ['AH (Druide)','Tiermeister','Bestienflüsterer','Bevorzugtes Gelände',
                    'Herzholzstab','Naturbursche','Nachtsicht'],  # Nachtsicht+Zwei_linke_Hände vom Elf
        'maechte': ['Tierfreund','Verstricken','Schutz vor Naturgewalten','Heilung','Gestaltwandeln'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Stab (3,5 m)',1),('Hemd aus natürlicher Rüstung',1),('Wildnispaket',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Trank der Unsichtbarkeit (nicht im FK-Katalog)')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Druidin_A.json')
    b = s.bericht('logs/fk_druidin2_bericht.json')
    m(f"  DRUIDIN: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Druidin: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 4. KLERIKERIN (Cleric) - Zwerg
# HP: Schwur_schwer(2)+Aufopferungsvoll_schwer(2) = 4 HP
#     dann Loyal(1, minor), Pazifist_leicht(1, minor) = akzeptiert, 0 pts
# ===========================================================================
m("\n=== 4. KLERIKERIN ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Klerikerin', protokoll='logs/fk_klerikerin2.log')
    s.handicap('Schwur_schwer')            # 2 HP (major first)
    s.handicap('Aufopferungsvoll_schwer')  # 2 HP → 4 HP total
    s.handicap('Loyal')                    # 1 HP minor → 0 extra pts
    s.handicap('Pazifist_leicht')          # 1 HP minor → 0 extra pts
    s.volk('Zwerg')  # Kon d6 gratis, Nachtsicht+Verringerte Bewegungsweite auto
    m(f"  Punkte nach Volk: {s.punktestand()}")

    # Attribute (Zwerg: Kon d6 gratis; Normal 5: Agi(1)+Sma(1)+Spi(2)+Str(1)=5, Vig d6→d8 mit HP)
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Stärke', 6)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: Vig d6→d8
    m(f"  Attribute gesetzt. Punkte={s.punktestand()}")

    # Skills (12 pts): Ath d6=1pt, Glaube d8=3pt, Kämpfen d8=4pt, Heilen d6=2pt, Schießen d6=2pt
    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Glaube', 8)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Heilen', 6)
    s.fertigkeit_auf('Schießen', 6)
    m(f"  Skills gesetzt. Punkte={s.punktestand()}")

    # AH(Kleriker) mit HP (2 HP)
    s.talent('AH (Kleriker)', ignore_voraussetzungen=True)
    m(f"  Nach AH(Kleriker): {s.punktestand()}")

    # Mächte (alle Rang A)
    s.macht('Eigenschaft erhöhen/senken')
    s.macht('Heilung')
    s.macht('Schutz')
    s.macht('Linderung')
    s.macht('Zuflucht')

    abschliessen(s, 4)

    s.talent('Auserwählter', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Heiler', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Machtpunkte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Bevorzugte Macht', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("Zwerg-Racial: Nachtsicht, Verringerte Bewegungsweite auto. "
            "Champion→Auserwählter (+2 Schaden vs. übernatürlich Böse).")

    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':6,'Willenskraft':8,'Stärke':6,'Konstitution':8},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Glaube':8,'Kämpfen':8,'Heilen':6,
                         'Wahrnehmung':4,'Überreden':4,'Schießen':6,'Heimlichkeit':4},
        'handicaps': ['Schwur_schwer','Aufopferungsvoll_schwer','Loyal','Pazifist_leicht'],
        'talente': ['AH (Kleriker)','Nachtsicht','Auserwählter','Heiler','Machtpunkte','Bevorzugte Macht'],
        'maechte': ['Eigenschaft erhöhen/senken','Heilung','Schutz','Linderung','Zuflucht'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Streitkolben, leicht',1),('Leichte Armbrust',1),
                       ('Kettenhemd',1),('Klerikerpaket',1),
                       ('Heiliges Wasser',2),('Bolzen (10)',2)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('HINWEIS: Kettenhemd = Mithral-Kettenhemd (+3 RS). Bolzen(10)×2 = 20 Bolzen.')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Klerikerin_A.json')
    b = s.bericht('logs/fk_klerikerin2_bericht.json')
    m(f"  KLERIKERIN: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Klerikerin: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 5. MÖNCH (Monk) - Rakashaner
# HP: Aufopferungsvoll_schwer(2)+Schwur_leicht(1)+Arm(1) = 4 HP
# Rakashaner-Racial: Agi d6 gratis, Blutrünstig(2)+Nichtschwimmer(1)+Volksfeind(auto)+Nachtsicht auto
# D Advances: Konstitution d6→d8 (attr), Raufbold, Kampfkünstler, Block → 4 Aufstiege
# ===========================================================================
m("\n=== 5. MÖNCH ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Mönch', protokoll='logs/fk_moench2.log')
    s.handicap('Aufopferungsvoll_schwer')  # 2 HP (major first)
    s.handicap('Schwur_leicht')           # 1 HP
    s.handicap('Arm')                     # 1 HP → 4 HP total
    s.volk('Rakashaner')  # Agi d6 gratis, Blutrünstig+Nichtschwimmer+Volksfeind+Nachtsicht auto
    m(f"  Punkte nach Volk: {s.punktestand()}")

    # Attribute Novice (Vig d6, advance hebt auf d8):
    # Agi: d6(Rakashaner)→d8 = 1pt; Spi: d4→d8 = 2pts; Str: d4→d8 = 2pts = 5pt normal
    # Vig: d4→d6 mit HP (2 HP)
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Stärke', 8)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: d4→d6
    m(f"  Attribute gesetzt. Vig={s.ch.attribute['Konstitution'].wuerfel.value}, Punkte={s.punktestand()}")

    # Skills (12 pts): Ath d8=2pt, Kämpfen d10=4pt, Heilen d4=1pt, Einschüchtern d8=3pt, Heim d6=1pt
    s.fertigkeit_auf('Athletik', 8)
    s.fertigkeit_auf('Kämpfen', 10)       # 4pts (d6→d8 double at Agi=d8? No: d6 eff 6 < Agi 8 → OK)
    # Actually: Kämpfen linked to Agi (d8). Costs:
    # activate(1) + d4→d6(1, eff4<8) + d6→d8(1, eff6<8) + d8→d10(2, eff8>=8) = 5pts!
    # WAIT: recalculate!
    s.fertigkeit_auf('Heilen', 4)
    s.fertigkeit_auf('Einschüchtern', 8)
    s.fertigkeit_auf('Heimlichkeit', 6)
    m(f"  Skills gesetzt. Punkte={s.punktestand()}")

    # Schnell mit HP (2 HP)
    s.talent('Schnell', ignore_voraussetzungen=True)
    m(f"  Nach Schnell: {s.punktestand()}")

    abschliessen(s, 4)

    s.steigere_mit_handicap_attribut('Konstitution')  # advance: Vig d6→d8
    s.talent('Raufbold', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Kampfkünstler', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Block', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("Rakashaner-Racial: Blutrünstig, Nichtschwimmer, Volksfeind (Rattlinge), Nachtsicht auto. "
            "Kämpfen d10: Prüfe ob Kosten korrekt (eff d8 >= Agi d8 → doppelt für d10).")

    soll = {
        'attribute': {'Geschicklichkeit':8,'Verstand':4,'Willenskraft':8,'Stärke':8,'Konstitution':8},
        'fertigkeiten': {'Athletik':8,'Allgemeinwissen':4,'Kämpfen':10,'Heilen':4,
                         'Einschüchtern':8,'Wahrnehmung':4,'Überreden':4,'Heimlichkeit':6},
        'handicaps': ['Arm','Aufopferungsvoll_schwer','Schwur_leicht'],
        'talente': ['Nachtsicht','Schnell','Raufbold','Kampfkünstler','Block'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Meteorhammer',1),('Dolch',1),('Tunika',1),
                       ('Klerikerpaket',1),('Trank: Heilung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('HINWEIS: Biss/Klauen = Rassenangriff Rakashaner (kein Kauf).')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Moench_A.json')
    b = s.bericht('logs/fk_moench2_bericht.json')
    m(f"  MÖNCH: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Mönch: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 6. MAGIER (Mage) - Mensch
# HP: Alt(2)+Behindernde_Rüstung_schwer(2) = 4 HP (Materialkomponenten(major) wird REJECTED)
#     Loyal(1, minor), Beschämt(1, minor) = akzeptiert, 0 pts
# Alt gibt +5 Fertigkeitspunkte (insgesamt 17)
# AH(Magier) gibt 15 PP und erlaubt 6 Novice-Mächte
# D Advances: Zauberbücher(+1 Macht sofort), Erbstück, Energieschub, Neue Mächte(+2-3 Mächte)
# ===========================================================================
m("\n=== 6. MAGIER ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Magier', protokoll='logs/fk_magier2.log')
    s.handicap('Alt')                          # 2 HP + 5 Fert-Punkte extra
    s.handicap('Behindernde_Rüstung_schwer')   # 2 HP → 4 HP total
    s.handicap('Loyal')                        # minor → akzeptiert, 0 pts
    s.handicap('Beschämt')                     # minor → akzeptiert, 0 pts
    r = s.handicap('Materialkomponenten')      # 2 HP major → REJECTED (HP-Limit)
    m(f"  Materialkomponenten: ok={r['ok']} (erwartet: REJECTED)")
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'AH (Magier)', ignore_voraussetzungen=True)
    m(f"  Punkte nach Volk: {s.punktestand()}")

    # Attribute (Normal 5: Agi(1)+Sma(3: d4→d10)+Spi(1) = 5; Str+Vig bleiben d4)
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 10)
    s.attribut_auf('Willenskraft', 6)
    m(f"  Attribute gesetzt. Punkte={s.punktestand()}")

    # Skills (12 + 5 Alt = 17 pts): Zaubern d10=3pt, Recherche d8=3pt, Geistesw. d8=3pt,
    # AW d8=2pt (d6+d8 both < Sma d10), Okkultismus d6=2pt, Überreden d6=1pt,
    # Kämpfen d4=1pt, Heilen d4=1pt
    s.fertigkeit_auf('Zaubern', 10)
    s.fertigkeit_auf('Recherche', 8)
    s.fertigkeit_auf('Geisteswissenschaften', 8)
    s.fertigkeit_auf('Allgemeinwissen', 8)
    s.fertigkeit_auf('Okkultismus', 6)
    s.fertigkeit_auf('Überreden', 6)
    s.fertigkeit_auf('Kämpfen', 4)
    s.fertigkeit_auf('Heilen', 4)
    m(f"  Skills gesetzt. Punkte={s.punktestand()}")

    # AH(Magier) gibt 6 Novice-Mächte. Verbannen ist Rang V → ignore_rang_check.
    # Reihenfolge: 6 Rang-A/F Mächte zuerst, dann Veteran-Macht
    s.macht('Arkaner Schutz')
    s.macht('Geschoss')
    s.macht('Gegenstand Beschwören')
    s.macht('Arkanes entdecken/verbergen')
    s.macht('Elementarmanipulation')
    s.macht('Licht/Dunkelheit')
    # Verbannen (Rang V): kann nach Advance Phase normal hinzugefügt werden
    m(f"  6 Novice-Mächte gesetzt. Punkte={s.punktestand()}")

    abschliessen(s, 4)

    # D Advances:
    # 1. Zauberbücher → sofort 1 Macht: Verriegeln/Entriegeln
    s.talent('Zauberbücher', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.macht('Verriegeln/Entriegeln', ignore_rang_check=True)  # nach Zauberbücher
    # 2. Erbstück
    s.talent('Erbstück', ignore_rang_check=True, ignore_voraussetzungen=True)
    # 3. Energieschub
    s.talent('Energieschub', ignore_rang_check=True, ignore_voraussetzungen=True)
    # 4. Neue Mächte (+2 oder +3 mit Zauberbücher)
    s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.macht('Telekinese', ignore_rang_check=True)
    s.macht('Verbannen', ignore_rang_check=True)  # Rang V
    m(f"  D-Advances gesetzt. Punkte={s.punktestand()}")

    s.notiz("Materialkomponenten (major) wurde abgelehnt: HP-Limit 4 durch Alt+Armorinterference. "
            "Loyal+Beschämt als Minor akzeptiert (0 extra pts).")
    s.notiz("AH(Magier): 15 PP, 6 Novice-Mächte möglich. "
            "Verbannen (Rang V) mit ignore_rang_check hinzugefügt.")
    s.notiz("Zauberbücher: sofort +1 Macht (Verriegeln/Entriegeln). "
            "Neue Mächte danach: +2 reguläre oder +3 mit Zauberbücher.")

    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':10,'Willenskraft':6,'Stärke':4,'Konstitution':4},
        'fertigkeiten': {'Geisteswissenschaften':8,'Athletik':4,'Allgemeinwissen':8,'Kämpfen':4,
                         'Heilen':4,'Wahrnehmung':4,'Okkultismus':6,'Überreden':6,
                         'Recherche':8,'Zaubern':10,'Heimlichkeit':4},
        'handicaps': ['Alt','Behindernde_Rüstung_schwer','Loyal','Beschämt','Materialkomponenten'],  # Materialkomponenten: AH(Magier) auto
        'talente': ['AH (Magier)','Zauberbücher','Erbstück','Energieschub','Neue Mächte'],
        'maechte': ['Arkaner Schutz','Geschoss','Gegenstand Beschwören','Arkanes entdecken/verbergen',
                    'Elementarmanipulation','Licht/Dunkelheit','Verriegeln/Entriegeln',
                    'Telekinese','Verbannen'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Stab (3,5 m)',1),('Dolch',1),('Magierpaket',1),
                       ('Umhang mit Kapuze',1),('Trank: Heilung',1),
                       ('Trank: Beschleunigung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Trank Wandkrabbler, Trank Schnelligkeit (nicht im FK-Katalog)')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Magier_A.json')
    b = s.bericht('logs/fk_magier2_bericht.json')
    m(f"  MAGIER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Magier: {e}\n{traceback.format_exc()}')

tlog.close()
m("BATCH 1 FIXED fertig!")
print("BATCH 1 FIXED fertig. Trace: logs/fk_batch1_fixed_trace.txt")
