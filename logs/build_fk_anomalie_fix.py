"""
FK Anomalie-Fix: Neue Talente lösen bestehende Anomalien auf
- Krieger:    'Take the Hit'     → 'Treffer einstecken' (NEU, exakte Entsprechung)
- Assassinin: 'Sneak Attack'     → 'Hinterhältiger Angriff' (NEU, bessere Näherung)
- Amazone:    'Formation Fighter'→ 'Formationskämpfer' (war bereits in FK, übersehen)
"""

import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/fk_anomalie_fix_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

def ab(s, n):
    s.ch.char_gen_completed = True
    for _ in range(n): increase_aufstiege(s.ch)
    m(f"  → chargen OK, {n} Aufstiege, Rang={s.ch.rang}")

# ===========================================================================
# KRIEGER - Mensch
# Fix: 'Take the Hit' (freie Wurfwiederholung Schaden-Wegstecken) → 'Treffer einstecken'
# Voraussetzungen Treffer einstecken: F, Eisenkiefer + KON W8 → beide erfüllt!
# ===========================================================================
m("=== KRIEGER (Anomalie-Fix) ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Krieger', protokoll='logs/fk_krieger3.log')
    s.handicap('Schwur_schwer')
    s.handicap('Arkane_Empfindlichkeit_leicht')
    s.handicap('Lebensaufgabe')
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Kräftig', ignore_voraussetzungen=True)

    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Stärke', 6)
    s.attribut_auf('Konstitution', 6)
    s.steigere_mit_handicap_attribut('Konstitution')   # 2 HP: d6→d8
    m(f"  Attrs: {s.punktestand()}")

    s.talent('Eisenkiefer', ignore_voraussetzungen=True)
    m(f"  Nach Eisenkiefer: {s.punktestand()}")

    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Einschüchtern', 6)
    s.fertigkeit_auf('Schießen', 4)
    s.fertigkeit_auf('Provozieren', 8)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 4)
    s.steigere_mit_handicap_attribut('Konstitution')   # advance: d8→d10
    s.talent('Schmerzresistenz', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Erzürnen', ignore_rang_check=True, ignore_voraussetzungen=True)
    # FIX: 'Take the Hit' → 'Treffer einstecken' (Voraussetzungen erfüllt: Eisenkiefer+KON W8)
    s.talent('Treffer einstecken', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("AUFGELÖST: 'Take the Hit' (freie Wurfwiederholung Schaden-Wegstecken) = "
            "'Treffer einstecken' (neues FK-Talent, exakte Entsprechung). "
            "Voraussetzungen Eisenkiefer+KON W8 erfüllt.")
    s.notiz("GELDMANGEL: Schwert, Langschwert (300 GP) + Bronzerüstung/Helm (200+120 GP) = 620 GP. "
            "Übersteigt Startbudget 500 GP. FORCE-Käufe nötig.")
    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':6,'Willenskraft':6,'Stärke':6,'Konstitution':10},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Kämpfen':8,'Einschüchtern':6,
                         'Wahrnehmung':4,'Überreden':4,'Schießen':4,'Heimlichkeit':4,'Provozieren':8},
        'handicaps': ['Schwur_schwer','Arkane_Empfindlichkeit_leicht','Lebensaufgabe'],
        'talente': ['Kräftig','Eisenkiefer','Schmerzresistenz','Erzürnen','Treffer einstecken'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    for name, anz in [('Schwert, Langschwert',1),('Dolch',1),('Netz (beschwert)',1),
                      ('Leichte Armbrust',1),('Bronzebrustpanzer',1),('Bronzehelm',1),
                      ('Mittlerer Schild',1),('Söldnerpaket',1),('Bolzen (10)',2),
                      ('Trank: Beschleunigung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Trank des Umgebungsschutzes (nicht im FK-Katalog)')
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Krieger_A.json')
    b = s.bericht('logs/fk_krieger3_bericht.json')
    m(f"  KRIEGER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Krieger: {e}\n{traceback.format_exc()}')

# ===========================================================================
# ASSASSININ - Gestaltwandler
# Fix: 'Sneak Attack' → 'Hinterhältiger Angriff' (bessere Näherung, Voraussetzung erfüllt)
# ===========================================================================
m("\n=== ASSASSININ (Anomalie-Fix) ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Assassinin', protokoll='logs/fk_assassinin3.log')
    s.handicap('Blutrünstig')
    s.handicap('Gesucht_schwer')
    s.volk('Gestaltwandler')
    m(f"  Punkte: {s.punktestand()}")

    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Stärke', 6)
    s.attribut_auf('Konstitution', 6)
    m(f"  Attrs: {s.punktestand()}")

    s.talent('Assassine', ignore_voraussetzungen=True)
    m(f"  Nach Assassine: {s.punktestand()}")

    s.fertigkeit_auf('Athletik', 8)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Fokus', 6)
    s.fertigkeit_auf('Heilen', 4)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Schießen', 6)
    s.fertigkeit_auf('Heimlichkeit', 6)
    s.fertigkeit_auf('Diebeskunst', 6)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 4)
    s.steigere_mit_handicap_fertigkeit('Heimlichkeit')  # d6→d8
    s.talent('Giftmischer', ignore_rang_check=True, ignore_voraussetzungen=True)
    # FIX: 'Sneak Attack' → 'Hinterhältiger Angriff' (Voraussetzung Assassine erfüllt!)
    s.talent('Hinterhältiger Angriff', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Dieb', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("VERBESSERT: 'Sneak Attack' (extra W6 Schaden bei Überraschungsangriff) = "
            "'Hinterhältiger Angriff' (neues FK-Talent: +2 Schaden aus Hinterhalt). "
            "Voraussetzung Assassine erfüllt. Näher als Erstschlag (freier Angriff bei Bewegung).")
    s.notiz("Gestaltwandler-Racial: AH(Begabt)+Charismatisch+Geheimnis_schwer+Verkleiden auto.")
    soll = {
        'attribute': {'Geschicklichkeit':8,'Verstand':6,'Willenskraft':4,'Stärke':6,'Konstitution':6},
        'fertigkeiten': {'Athletik':8,'Allgemeinwissen':4,'Kämpfen':8,'Fokus':6,'Heilen':4,
                         'Wahrnehmung':6,'Überreden':4,'Schießen':6,'Heimlichkeit':6},
        'handicaps': ['Blutrünstig','Gesucht_schwer'],
        'talente': ['AH (Begabt)','Charismatisch','Assassine','Giftmischer',
                    'Hinterhältiger Angriff','Dieb'],
        'maechte': ['Verkleiden'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    for name, anz in [('Dolch',1),('Blasrohr',1),('Totschläger',1),('Ledertunika',1),
                      ('Umhang mit Kapuze',1),('Bandolier',1),('Diebespaket',1),
                      ('Blasrohrpfeile (20)',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Gifte (Schlangengift, Assassinengebräu, Äther, Lotusstaub, Grünschleimextrakt)')
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Assassinin_A.json')
    b = s.bericht('logs/fk_assassinin3_bericht.json')
    m(f"  ASSASSININ: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Assassinin: {e}\n{traceback.format_exc()}')

# ===========================================================================
# AMAZONE - Mensch
# Fix: 'Formation Fighter' → 'Formationskämpfer' (war bereits im FK, war übersehen)
# Voraussetzungen: A, Kämpfen W8 → Amazone hat Kämpfen W8!
# ===========================================================================
m("\n=== AMAZONE (Anomalie-Fix) ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Amazone', protokoll='logs/fk_amazone3.log')
    s.handicap('Heldenhaft')
    s.handicap('Idealistisch')
    s.handicap('Loyal')
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Flink', ignore_voraussetzungen=True)

    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Stärke', 6)
    s.steigere_mit_handicap_attribut('Konstitution')   # 2 HP: d4→d6
    m(f"  Attrs: {s.punktestand()}")

    s.talent('Schnell', ignore_voraussetzungen=True)   # 2 HP
    m(f"  Nach Schnell: {s.punktestand()}")

    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Einschüchtern', 6)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Reiten', 6)
    s.fertigkeit_auf('Schießen', 8)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 4)
    s.talent('Volltreffer', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Im Sattel geboren', ignore_rang_check=True, ignore_voraussetzungen=True)
    # FIX: Formation Fighter → Formationskämpfer (war bereits in FK-JSON, Kämpfen W8 erfüllt!)
    s.talent('Formationskämpfer', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Meisterschütze', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("AUFGELÖST: 'Formation Fighter' (+2 Überzahlbonus) = 'Formationskämpfer' "
            "(war bereits im FK-Kompendium; Voraussetzung Kämpfen W8 erfüllt). "
            "Kein Anomalie mehr.")
    soll = {
        'attribute': {'Geschicklichkeit':8,'Verstand':6,'Willenskraft':6,'Stärke':6,'Konstitution':6},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Kämpfen':8,'Einschüchtern':6,
                         'Wahrnehmung':6,'Überreden':4,'Reiten':6,'Schießen':8,'Heimlichkeit':4},
        'handicaps': ['Heldenhaft','Idealistisch','Loyal'],
        'talente': ['Flink','Schnell','Volltreffer','Im Sattel geboren',
                    'Formationskämpfer','Meisterschütze'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    for name, anz in [('Chakram',1),('Bogen, Kurz-',1),('Entermesser',1),('Bronzebrustpanzer',1),
                      ('Pfeile (20)',1),('Brandpfeile (20)',1),('Abenteurerpaket',1),
                      ('Trank: Beschleunigung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Pfeil der Genauigkeit ×1')
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Amazone_A.json')
    b = s.bericht('logs/fk_amazone3_bericht.json')
    m(f"  AMAZONE: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Amazone: {e}\n{traceback.format_exc()}')

tlog.close()
