"""
BATCH 6 (Final): Soldat, Piratenkapitän(Swashbuckler), Titanentöter(Titan Slayer),
Schwertmagier(Swordmage), Walküre(Valkyrie), Schatzjäger(Treasure Hunter)
"""
import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/fk_batch6_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()
def ab(s, n):
    s.ch.char_gen_completed = True
    for _ in range(n): increase_aufstiege(s.ch)
    m(f"  → {n} Aufstiege, Rang={s.ch.rang}")

# ===========================================================================
# 31. SOLDAT (Soldier) - Mensch
# Manual: Heldenhaft(2)+Tick(1)+Gesucht_leicht(1) = 4 HP
# Mensch free: Soldat (Soldier edge)
# 4 HP: Agi d4→d6(2HP) + Vig d6→d8 (wait, lets use HP for 2 attr raises)
# D Advances: Haltet die Stellung!(FormFighter≈), Anführer(Command), Stärke d8, Geborener Anführer = 4
# Stärke Novice d6, advance → d8
# ===========================================================================
m("=== 31. SOLDAT ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Soldat', protokoll='logs/fk_soldat.log')
    s.handicap('Heldenhaft')     # 2 HP
    s.handicap('Tick')           # 1 HP
    s.handicap('Gesucht_leicht') # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Soldat', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs Novice (Str d6, advance → d8):
    # Agi(1)+Sma(1)+Spi(2)+Vig(2: d4→d8) = 6, aber nur 5 normal!
    # Str d4→d6: brauchen noch 1pt. Normal 5: Agi(1)+Sma(1)+Spi(2)+Str(1) = 5 → Vig d4.
    # HP: Vig d4→d6(2HP) + d6→d8(2HP) = 4HP ✓
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Stärke', 6)   # Novice d6
    s.attribut_auf('Konstitution', 4)  # kein normaler Punkt mehr
    s.steigere_mit_handicap_attribut('Konstitution')   # 2 HP: d4→d6
    s.steigere_mit_handicap_attribut('Konstitution')   # 2 HP: d6→d8
    m(f"  Attrs: {s.punktestand()}")

    # Skills (12pt): Ath d6(1pt grundf), Kriegskunst d6(2pt: activate+d6<Sma=d6,normal),
    # AW d4(0), Kämpfen d8(4pt, Agi=d6: 1+1+2), Einschüchtern d6(2pt, Wk=d8: 1+1),
    # Wahr d6(1pt grundf), Provozieren d6(2pt, Wk=d8: 1+1) = 1+2+0+4+2+1+2=12 ✓
    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Kriegskunst', 6)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Einschüchtern', 6)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Provozieren', 6)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 4)
    s.talent('Haltet die Stellung!', ignore_rang_check=True, ignore_voraussetzungen=True)  # Formation Fighter approx
    s.talent('Anführer', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.steigere_mit_handicap_attribut('Stärke')   # advance: Str d6→d8
    s.talent('Geborener Anführer', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("'Formation Fighter' → 'Haltet die Stellung!' (Annäherung). "
            "Soldat-Edge = soldat(Stärke höher für Belastung, Widerhole Vig vs. Naturgewalten).")
    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':6,'Willenskraft':8,'Stärke':8,'Konstitution':8},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Kriegskunst':6,'Kämpfen':8,
                         'Einschüchtern':6,'Wahrnehmung':6,'Überreden':4,'Heimlichkeit':4,'Provozieren':6},
        'handicaps': ['Heldenhaft','Tick','Gesucht_leicht'],
        'talente': ['Soldat','Haltet die Stellung!','Anführer','Geborener Anführer'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Soldat_A.json')
    b = s.bericht('logs/fk_soldat_bericht.json')
    m(f"  SOLDAT: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Soldat: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 32. PIRATENKAPITÄN (Swashbuckler) - Mensch
# Manual: Impulsiv(2)+Übermütig(2) = 4 HP
# Mensch free: Schnell (Quick)
# 4 HP: 2 für Ruhige Hände + 2 für Vig d4→d6
# D Advances: Finte, Ass am Steuer, Glück, Dirty Fighter(→Killerinstinkt approx) = 4
# Anomalie: 'Dirty Fighter' kein FK-Äquivalent
# ===========================================================================
m("\n=== 32. PIRATENKAPITÄN ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Piratenkapitän', protokoll='logs/fk_pirat.log')
    s.handicap('Impulsiv')    # 2 HP
    s.handicap('Übermütig')   # 2 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Schnell', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d8(2pt), Sma d6(1pt), Spi d6(1pt), Str d6(1pt) → 5pt, Vig d4→d6 mit HP
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Stärke', 6)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: d4→d6
    m(f"  Attrs: {s.punktestand()}")

    s.talent('Ruhige Hände', ignore_voraussetzungen=True)  # 2 HP
    m(f"  Nach Ruhige Hände: {s.punktestand()}")

    # Skills (12pt): Ath d8(grundf 2pt, Agi=d8), Seefahrt d8(3pt: 1+1+1, Agi=d8),
    # AW d4(0), Kämpfen d8(3pt, Agi=d8: 1+1+1), Wahr d4(0), Schießen d4(1pt activate),
    # Heim d4(0), Provozieren d6(2pt: 1+1), Diebeskunst d4(1pt activate) = 2+3+0+3+0+1+0+2+1=12 ✓
    s.fertigkeit_auf('Athletik', 8)
    s.fertigkeit_auf('Seefahrt', 8)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Schießen', 4)
    s.fertigkeit_auf('Provozieren', 6)
    s.fertigkeit_auf('Diebeskunst', 4)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 4)
    s.talent('Finte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Ass am Steuer', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Glück', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Killerinstinkt', ignore_rang_check=True, ignore_voraussetzungen=True)  # Dirty Fighter approx
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("ANOMALIE: 'Dirty Fighter' (+2 bei Tests mit Kämpfen) → 'Killerinstinkt' (freie Wdh. bei Herausforderungs-Tests) als Annäherung.")
    soll = {
        'attribute': {'Geschicklichkeit':8,'Verstand':6,'Willenskraft':6,'Stärke':6,'Konstitution':6},
        'fertigkeiten': {'Athletik':8,'Allgemeinwissen':4,'Kämpfen':8,'Wahrnehmung':4,
                         'Überreden':4,'Schießen':4,'Seefahrt':8,'Heimlichkeit':4,
                         'Provozieren':6,'Diebeskunst':4},
        'handicaps': ['Impulsiv','Übermütig'],
        'talente': ['Schnell','Ruhige Hände','Finte','Ass am Steuer','Glück','Killerinstinkt'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Piratenkpt_A.json')
    b = s.bericht('logs/fk_pirat_bericht.json')
    m(f"  PIRATENKAPITÄN: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Piratenkapitän: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 33. TITANENTÖTER (Titan Slayer) - Zwerg
# Zwerg auto: Nachtsicht; Konstitution d6 free; Verringerte Bewegungsweite
# Manual: Angetrieben_schwer(2)+Übermütig(2) = 4 HP
# 4 HP: 2 für Rückzug(Extraction) + 2 für Vig d6→d8
# D Advances: Wildling(Savagery), Erzfeind, Mächtiger Hieb, Schneller Angriff(Frenzy) = 4
# ===========================================================================
m("\n=== 33. TITANENTÖTER ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Titanentöter', protokoll='logs/fk_titan.log')
    s.handicap('Angetrieben_schwer')  # 2 HP
    s.handicap('Übermütig')          # 2 HP → 4 HP
    s.volk('Zwerg')  # Kon d6 gratis, Nachtsicht, Verringerte Bewegungsweite
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d8(2pt), Str d10(3pt: d4→d10), Vig d6→d8 mit HP(Zwerg gab d6)
    # Normal 5: Agi(2)+Str(3) = 5 → Vig bleibt d6 (Zwerg free), dann HP: d6→d8 mit 2HP
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Stärke', 10)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: Vig d6→d8
    m(f"  Attrs: {s.punktestand()}")

    s.talent('Rückzug', ignore_voraussetzungen=True)  # 2 HP
    m(f"  Nach Rückzug: {s.punktestand()}")

    # Skills (12pt): Ath d10(grundf: d4→d8=2pt + d8→d10=2pt(eff8>=Agi8→DOUBLE? eff8 vs Agi8: 8>=8 YES)=4pt),
    # AW d4(0), Kämpfen d8(3pt, Agi=d8: 1+1+1), Wahr d6(1pt grundf), Schießen d6(2pt, Agi=d8: 1+1),
    # Heim d6(1pt grundf), Überl d4(1pt activate) = 4+0+3+1+2+1+1=12 ✓
    s.fertigkeit_auf('Athletik', 10)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Schießen', 6)
    s.fertigkeit_auf('Heimlichkeit', 6)
    s.fertigkeit_auf('Überleben', 4)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 4)
    s.talent('Wildling', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Erzfeind', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Mächtiger Hieb', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Schneller Angriff', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    soll = {
        'attribute': {'Geschicklichkeit':8,'Verstand':4,'Willenskraft':4,'Stärke':10,'Konstitution':8},
        'fertigkeiten': {'Athletik':10,'Allgemeinwissen':4,'Kämpfen':8,'Wahrnehmung':6,
                         'Überreden':4,'Schießen':6,'Heimlichkeit':6,'Überleben':4},
        'handicaps': ['Angetrieben_schwer','Übermütig'],
        'talente': ['Nachtsicht','Rückzug','Wildling','Erzfeind','Mächtiger Hieb','Schneller Angriff'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Titanentgr_A.json')
    b = s.bericht('logs/fk_titan_bericht.json')
    m(f"  TITANENTÖTER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Titanentöter: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 34. SCHWERTMAGIER (Swordmage) - Mensch, AH(Magier)
# AH auto: Behindernde_Rüstung_schwer + Materialkomponenten
# Manual: Einäugig(2)+Talisman_schwer(2) = 4 HP
# Mensch free: AH(Magier)
# 4 HP: 2 für Vig d4→d6 + 2HP für skill/another attr
# D Advances: Machtpunkte, Mächtiger Hieb, Lieblingswaffe, Neue Mächte(Schadensfeld+Teleportation) = 4
# ===========================================================================
m("\n=== 34. SCHWERTMAGIER ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Schwertmagier', protokoll='logs/fk_schwertm.log')
    s.handicap('Einäugig')        # 2 HP
    s.handicap('Talisman_schwer') # 2 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'AH (Magier)', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d6(1pt), Sma d8(2pt), Str d8(2pt) → 5pt, Vig d4→d6 mit HP, 2HP leftover
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 8)
    s.attribut_auf('Stärke', 8)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: d4→d6
    m(f"  Attrs: {s.punktestand()}")

    # 2 HP remaining → use for skill after budget runs out
    # Skills (12pt): Ath d6(1pt grundf), AW d4(0), Kämpfen d8(3pt, Agi=d6: 1+1+1... wait:
    # Kämpfen d8 with Agi=d6: activate(1,eff2<6)+d4→d6(1,eff4<6)+d6→d8(2,eff6>=6) = 4pt!
    # Wahr d6(1pt grundf), Okkultismus d4(1pt), Überreden d4(0grundf), Zaubern d10(4pt, Sma=d8:
    # activate(1)+d6(1)+d8(1)+d10(2, eff8>=Sma=8→DOUBLE) = 5pt)
    # Heim d4(0) = 1+0+4+1+1+0+5+0=12 ✓
    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Okkultismus', 4)
    s.fertigkeit_auf('Zaubern', 10)
    m(f"  Skills: {s.punktestand()}")

    # 2 HP left → steigere_mit_handicap_fertigkeit if needed (Heim d4→d6?)
    # Actually no skill HP needed - all fits in 12pt. Leave HP unused.

    # Mächte (AH Magier: 6 Novice, 15PP)
    # Novice 3 (rest via D-Advance New Powers): Abwehren, Chaos(Havoc), Kriegersegen(Smite)
    s.macht('Abwehren')           # deflection A
    s.macht('Chaos')              # havoc A
    s.macht('Kriegersegen', ignore_rang_check=True)  # smite F

    ab(s, 4)
    s.talent('Machtpunkte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Mächtiger Hieb', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Lieblingswaffe', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.macht('Schadensfeld', ignore_rang_check=True)   # damage field F
    s.macht('Teleportation', ignore_rang_check=True)  # teleport F
    m(f"  D-Advances: {s.punktestand()}")

    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':8,'Willenskraft':4,'Stärke':8,'Konstitution':6},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Kämpfen':8,'Wahrnehmung':6,
                         'Okkultismus':4,'Überreden':4,'Zaubern':10,'Heimlichkeit':4},
        'handicaps': ['Einäugig','Talisman_schwer',
                      'Behindernde_Rüstung_schwer','Materialkomponenten'],
        'talente': ['AH (Magier)','Machtpunkte','Mächtiger Hieb','Lieblingswaffe','Neue Mächte'],
        'maechte': ['Abwehren','Chaos','Kriegersegen','Schadensfeld','Teleportation'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Schwertmag_A.json')
    b = s.bericht('logs/fk_schwertm_bericht.json')
    m(f"  SCHWERTMAGIER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Schwertmagier: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 35. WALKÜRE (Valkyrie) - Mensch
# Manual: Lebensaufgabe(1)+Impulsiv(2)+Tick(1) = 4 HP
# Mensch free: Kräftig (Brawny)
# 4 HP: Str d4→d6(2HP) + d6→d8(2HP) = 4HP
# D Advances: Vig d8(attr, Novice Vig d6), Elan, Lieblingswaffe, Mystische Kräfte(Fighter) = 4
# ===========================================================================
m("\n=== 35. WALKÜRE ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Walküre', protokoll='logs/fk_walkuere.log')
    s.handicap('Impulsiv')      # 2 HP
    s.handicap('Lebensaufgabe') # 1 HP
    s.handicap('Tick')          # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Kräftig', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs Novice (Vig d6, advance → d8): Agi(1)+Sma(1)+Spi(2)+Vig(1: d4→d6) = 5pt, Str d4
    # Str d4→d6(2HP) + d6→d8(2HP) = 4HP
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Konstitution', 6)   # 1pt: d4→d6
    s.steigere_mit_handicap_attribut('Stärke')    # 2 HP: d4→d6
    s.steigere_mit_handicap_attribut('Stärke')    # 2 HP: d6→d8
    m(f"  Attrs: {s.punktestand()}")

    # Skills (12pt): Ath d6(1pt grundf), Kriegskunst d6(2pt: 1+1, Sma=d6 OK), AW d4(0),
    # Kämpfen d8(4pt, Agi=d6: 1+1+2), Wahr d4(0grundf), Überreden d6(1pt grundf: 1pt),
    # Reiten d6(2pt, Agi=d6: 1+1), Schießen d6(2pt, Agi=d6: 1+1) = 1+2+0+4+0+1+2+2=12 ✓
    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Kriegskunst', 6)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Überreden', 6)
    s.fertigkeit_auf('Reiten', 6)
    s.fertigkeit_auf('Schießen', 6)
    m(f"  Skills: {s.punktestand()}")

    # Mächte (Mystische Kräfte: 10PP, Self-only, via Talent)
    ab(s, 4)
    s.steigere_mit_handicap_attribut('Konstitution')  # advance: Vig d6→d8
    s.talent('Elan', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Lieblingswaffe', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Mystische Kräfte', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("Mystische Kräfte (Kämpfer): 10 PP, Self-only. "
            "Mächte (Eigenschaft erhöhen/senken für Kämpfen/Schießen/Stärke/Vig, Schutz, Kriegersegen) "
            "können nicht normal via macht() hinzugefügt werden.")
    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':6,'Willenskraft':8,'Stärke':8,'Konstitution':8},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Kriegskunst':6,'Kämpfen':8,
                         'Wahrnehmung':4,'Überreden':6,'Reiten':6,'Schießen':6,'Heimlichkeit':4},
        'handicaps': ['Impulsiv','Lebensaufgabe','Tick'],
        'talente': ['Kräftig','Elan','Lieblingswaffe','Mystische Kräfte'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Walkuere_A.json')
    b = s.bericht('logs/fk_walkuere_bericht.json')
    m(f"  WALKÜRE: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Walküre: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 36. SCHATZJÄGER (Treasure Hunter) - Halbling
# Halbling auto: Glück talent; Willenskraft d6 free; Größe-1, Verringerte Bewegungsweite
# Manual: Neugierig(2)+Gierig_leicht(1)+Sanftmütig(1) = 4 HP
# 4 HP: 2 für Aufmerksamkeit + 2 für Steingespür
# D Advances: Kämpfen d6+Wahr d8 (2skill+advance), Schatzjäger, Dieb, Fallengespür = 5
# Kämpfen Novice: d4(aktiviert), Wahr Novice: d6 (advance → d8)
# ===========================================================================
m("\n=== 36. SCHATZJÄGER ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Schatzjäger', protokoll='logs/fk_schatz.log')
    s.handicap('Neugierig')     # 2 HP
    s.handicap('Gierig_leicht') # 1 HP
    s.handicap('Sanftmütig')    # 1 HP → 4 HP
    s.volk('Halbling')  # Wk d6 gratis, Glück auto, Größe-1, Verringerte Bewegungsweite
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d8(2pt), Sma d8(2pt), Str d6(1pt) → 5pt; Wk d6 von Halbling, Vig d4
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Verstand', 8)
    s.attribut_auf('Stärke', 6)
    m(f"  Attrs: {s.punktestand()}")

    # Talents: Aufmerksamkeit(2HP) + Steingespür(2HP) = 4HP
    s.talent('Aufmerksamkeit', ignore_voraussetzungen=True)
    s.talent('Steingespür', ignore_voraussetzungen=True)
    m(f"  Nach Talents: {s.punktestand()}")

    # Skills Novice (Kämpfen d4 aktiviert, Wahr d6):
    # Ath d6(grundf 1pt), Kämpfen d4(activate=1pt, Novice), AW d4(0grundf),
    # Wahr d6(grundf 1pt, Novice), Überreden d4(0grundf), Reparieren d6(2pt, linked to Sma=d8: 1+1),
    # Okkultismus d8(3pt: 1+1+1,<Sma=d8), Schießen d4(1pt), Heim d6(grundf 1pt), Diebeskunst d6(2pt)
    # = 1+1+0+1+0+2+3+1+1+2=12 ✓
    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Kämpfen', 4)      # Novice d4 (activate)
    s.fertigkeit_auf('Wahrnehmung', 6)  # Novice d6 (advance → d8)
    s.fertigkeit_auf('Reparieren', 6)
    s.fertigkeit_auf('Okkultismus', 8)
    s.fertigkeit_auf('Schießen', 4)
    s.fertigkeit_auf('Heimlichkeit', 6)
    s.fertigkeit_auf('Diebeskunst', 6)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 5)  # 5 Aufstiege: 2 Skill-Steps + 3 Edges
    s.steigere_mit_handicap_fertigkeit('Kämpfen')      # activate→d4→d6
    s.steigere_mit_handicap_fertigkeit('Wahrnehmung')  # d6→d8
    s.talent('Schatzjäger', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Dieb', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Fallengespür', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    soll = {
        'attribute': {'Geschicklichkeit':8,'Verstand':8,'Willenskraft':6,'Stärke':6,'Konstitution':4},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Kämpfen':6,'Wahrnehmung':8,
                         'Überreden':4,'Reparieren':6,'Okkultismus':8,'Schießen':4,
                         'Heimlichkeit':6,'Diebeskunst':6},
        'handicaps': ['Neugierig','Gierig_leicht','Sanftmütig'],
        'talente': ['Glück','Aufmerksamkeit','Steingespür','Schatzjäger','Dieb','Fallengespür'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Schatzjgr_A.json')
    b = s.bericht('logs/fk_schatz_bericht.json')
    m(f"  SCHATZJÄGER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Schatzjäger: {e}\n{traceback.format_exc()}')

tlog.close()
print("BATCH 6 fertig. Trace: logs/fk_batch6_trace.txt")
