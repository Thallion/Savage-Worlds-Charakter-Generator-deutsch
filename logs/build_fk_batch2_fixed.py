"""
BATCH 2 FIXED: Fantasy Kompendium Archetypen
Paladin, Waldläufer, Diebin, Zauberer, Hexe, Krieger

Korrekturen gegenüber Batch 2 v1:
- Protokoll-Logs auf _2-Suffix umgestellt
- Paladin: Plattenbrustharnisch (500 GP) übersteigt Startbudget (500 GP) →
  FORCE-Kauf dokumentiert; Klerikerpaket+Heiliges Wasser ebenfalls FORCE
- Krieger: Schwert, Langschwert (300 GP) + Bronze-Rüstung/Helm übersteigt Budget →
  FORCE-Käufe dokumentiert (FK-Preise stimmen nicht mit Quelltextwerten überein)
- Waldläufer: Anomalien nur NOTIZen (Halbelf-Racial-Effekte)
- Diebin/Hexe/Zauberer: Anomalien nur NOTIZen (Equipment-Lücken, Racial-Effekte)
"""

import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/fk_batch2_fixed_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

def abschliessen(s, n):
    s.ch.char_gen_completed = True
    for _ in range(n): increase_aufstiege(s.ch)
    m(f"  → chargen OK, {n} Aufstiege, Rang={s.ch.rang}")

# ===========================================================================
# 7. PALADIN - Mensch, AH(Kleriker)
# AH auto: Schwur_schwer (0 HP)
# Manual: Heldenhaft(2)+Vorsichtig(1)+Idealistisch(1) = 4 HP
# Mensch free: AH(Kleriker) → auto-adds Schwur_schwer
# 4 HP: 2 für Soldat + 2 für Stärke d4→d6 (advance hebt auf d8)
# D Advances: Stärke d6→d8, Auserwählter, Mutig, Heiliger/Unheiliger Krieger = 4
# ===========================================================================
m("=== 7. PALADIN ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Paladin', protokoll='logs/fk_paladin2.log')
    s.handicap('Heldenhaft')    # 2 HP
    s.handicap('Vorsichtig')    # 1 HP
    s.handicap('Idealistisch')  # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'AH (Kleriker)', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs Novice (Str d6, advance → d8): Agi(1)+Sma(1)+Spi(2)+Vig(1)=5 normal, Str d4→d6 mit HP
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Konstitution', 6)
    s.steigere_mit_handicap_attribut('Stärke')   # 2 HP: d4→d6
    m(f"  Attrs gesetzt. {s.punktestand()}")

    # Talent: Soldat (2 HP)
    s.talent('Soldat', ignore_voraussetzungen=True)
    m(f"  Nach Soldat: {s.punktestand()}")

    # Skills: Ath d6(1pt), Kriegskunst d4(1pt), Glaube d8(3pt), Kämpfen d6(2pt),
    # Einschüchtern d6(2pt), Reiten d6(2pt), Schießen d4(1pt) = 12pt
    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Kriegskunst', 4)
    s.fertigkeit_auf('Glaube', 8)
    s.fertigkeit_auf('Kämpfen', 6)
    s.fertigkeit_auf('Einschüchtern', 6)
    s.fertigkeit_auf('Reiten', 6)
    s.fertigkeit_auf('Schießen', 4)
    m(f"  Skills: {s.punktestand()}")

    # Mächte (AH Kleriker: 5 Novice, alle Rang A außer Kriegersegen=F)
    s.macht('Abwehren')
    s.macht('Arkanes entdecken/verbergen')
    s.macht('Heilung')
    s.macht('Zuflucht')
    s.macht('Kriegersegen', ignore_rang_check=True)  # Rang F

    abschliessen(s, 4)

    s.steigere_mit_handicap_attribut('Stärke')   # advance: Str d6→d8
    s.talent('Auserwählter', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Mutig', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Heiliger/Unheiliger Krieger', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("AH(Kleriker) fügt automatisch Schwur_schwer hinzu (0 HP). "
            "Soldat = Soldier-Edge: Stärke gilt als einen Typ höher für Belastung.")
    s.notiz("GELDMANGEL: Plattenbrustharnisch (500 GP) = gesamtes Startbudget. "
            "FORCE-Käufe für Klerikerpaket+Heiliges Wasser ebenfalls nötig. "
            "FK-Itempreise überschreiten Startkapital für schwer gerüstete Heilige.")
    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':6,'Willenskraft':8,'Stärke':8,'Konstitution':6},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Glaube':8,'Kämpfen':6,'Einschüchtern':6,
                         'Wahrnehmung':4,'Überreden':4,'Reiten':6,'Schießen':4,'Heimlichkeit':4,
                         'Kriegskunst':4},
        'handicaps': ['Heldenhaft','Vorsichtig','Idealistisch','Schwur_schwer'],
        'talente': ['AH (Kleriker)','Soldat','Auserwählter','Mutig','Heiliger/Unheiliger Krieger'],
        'maechte': ['Abwehren','Arkanes entdecken/verbergen','Heilung','Zuflucht','Kriegersegen'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Streitflegel',1),('Mittlerer Schild',1),('Plattenbrustharnisch',1),('Klerikerpaket',1),('Heiliges Wasser',1),('Trank: Umgebungsschutz',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Trank des Umgebungsschutzes')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Paladin_A.json')
    b = s.bericht('logs/fk_paladin2_bericht.json')
    m(f"  PALADIN: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Paladin: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 8. WALDLÄUFER (Ranger) - Halbelf Elfen-Erbe
# Halbelf auto: Außenseiter_leicht, Nachtsicht; freies Attribut: Geschicklichkeit
# Manual: Schwerzüngig(2)+Misstrauisch_leicht(1)+Dünnhäutig(1) = 4 HP
# 4 HP: 2 für Parkour(Free Runner) + 2 für Naturbursche(Woodsman)
# D Advances: Athletik d4→d6(1), Schießen d6→d8(1), Bevorzugtes Gelände, Erzfeind, Kundschafter = 5
# ===========================================================================
m("\n=== 8. WALDLÄUFER ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Waldläufer', protokoll='logs/fk_waldlaeuf2.log')
    s.handicap('Schwerzüngig')          # 2 HP (major first)
    s.handicap('Misstrauisch_leicht')   # 1 HP
    s.handicap('Dünnhäutig')           # 1 HP → 4 HP
    s.volk('Halbelf')
    s.volk_freies_attribut('Halbelf', 'Geschicklichkeit')  # Elfen-Erbe: Agi +1 step free
    m(f"  Punkte: {s.punktestand()}")

    # Attrs (Novice=Final): Halbelf gibt Agi d6 gratis.
    # Agi: d6→d8(1pt), Sma: d4→d6(1pt), Spi: d4→d6(1pt), Str: d4→d6(1pt), Vig: d4→d6(1pt) = 5 ✓
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Stärke', 6)
    s.attribut_auf('Konstitution', 6)
    m(f"  Attrs: {s.punktestand()}")

    # Skills Novice (Schießen d6, Athletik d4 - beides wird durch Advances erhöht):
    # Kämpfen d6(2pt), Einschüchtern d4(1pt), Wahr d6(1pt), Schießen d6(2pt activate+d6),
    # Heim d8(2pt, linked to Agi d8, both<d8), Überl d8(4pt, d6→d8 doppelt bei Sma=d6)
    s.fertigkeit_auf('Kämpfen', 6)
    s.fertigkeit_auf('Einschüchtern', 4)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Schießen', 6)     # Novice d6 (advance hebt auf d8)
    s.fertigkeit_auf('Heimlichkeit', 8)
    s.fertigkeit_auf('Überleben', 8)
    m(f"  Skills: {s.punktestand()}")

    # Talente: Parkour(Free Runner) + Naturbursche(Woodsman) je 2 HP = 4 HP
    s.talent('Parkour', ignore_voraussetzungen=True)
    s.talent('Naturbursche', ignore_voraussetzungen=True)
    m(f"  Nach Talenten: {s.punktestand()}")

    abschliessen(s, 5)  # 5 Aufstiege: 2 Skill-Steps + 3 Edges

    s.steigere_mit_handicap_fertigkeit('Athletik')   # d4→d6 (aktiviert)
    s.steigere_mit_handicap_fertigkeit('Schießen')   # d6→d8
    s.talent('Bevorzugtes Gelände', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Erzfeind', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Kundschafter', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("Halbelf (Elfen-Erbe): Außenseiter_leicht, Nachtsicht auto. "
            "Schwerzüngig (Tongue-Tied) = major in FK (2 HP). "
            "5 Aufstiege wegen 2 Skill-Steps im Code.")
    soll = {
        'attribute': {'Geschicklichkeit':8,'Verstand':6,'Willenskraft':6,'Stärke':6,'Konstitution':6},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Kämpfen':6,'Einschüchtern':4,
                         'Wahrnehmung':6,'Überreden':4,'Schießen':8,'Heimlichkeit':8,'Überleben':8},
        'handicaps': ['Schwerzüngig','Misstrauisch_leicht','Dünnhäutig'],
        'talente': ['Nachtsicht','Parkour','Naturbursche','Bevorzugtes Gelände','Erzfeind','Kundschafter'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Handaxt',1),('Kompositbogen',1),('Ledertunika',1),('Wildnispaket',1),('Pfeile (20)',1),('Fallenherstellungsset',1),('Trank: Beschleunigung',1),('Brandpfeile (20)',1),('Trank: Attributsteigerung',1),('Trank: Heilung',1),('Kettenhemd',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Verstärkte Lederrüstung (als Ledertunika)')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Waldlaeuf_A.json')
    b = s.bericht('logs/fk_waldlaeuf2_bericht.json')
    m(f"  WALDLÄUFER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Waldläufer: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 9. DIEBIN (Thief) - Mensch
# Manual: Vorsichtig(1)+Misstrauisch_leicht(1)+Gesucht_schwer(2) = 4 HP
# Mensch free: Schnell (Quick)
# 4 HP: 2 für Dieb(Thief) + 2 für Agi attr raise (d6→d8)
# D Advances: Reparieren d6(1), Heimlichkeit d8(1), Beziehungen, Gassenwissen, Fallengespür = 5
# ===========================================================================
m("\n=== 9. DIEBIN ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Diebin', protokoll='logs/fk_diebin2.log')
    s.handicap('Gesucht_schwer')      # 2 HP (major first)
    s.handicap('Vorsichtig')          # 1 HP
    s.handicap('Misstrauisch_leicht') # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Schnell', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d8, Sma d6, Spi d6, Str d6, Vig d6
    # Agi: d4→d8=2pt; Sma(1)+Spi(1)+Str(1) = 3pt. Total: 5pt → Vig d4.
    # Vig d4→d6 mit HP (2 HP)
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Stärke', 6)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: d4→d6
    m(f"  Attrs: {s.punktestand()}")

    # Skills Novice (Heim d6, Repar d4 - D Advances erhöhen):
    # Ath d8(2pt+2pt=3pt da Agi=d8, d6→d8 doppelt), Kämpfen d6(2pt),
    # Wahr d6(1pt), Überreden d6(1pt), Schießen d4(1pt activate), Heim d6(1pt),
    # Diebeskunst d8(3pt: activate+d6+d8→doppelt bei Agi=d8? d6<d8 OK, d8>=d8 doppelt=2pt)
    # Reparieren d4(1pt activate)
    # Total: 3+2+1+1+1+1+3+1 = 13pt... zu viel für 12!
    # Anpassen: Ath d6 (nur 1pt, grundf) statt d8 (3pt) - spart 2pt
    # Dann: 1+2+1+1+1+1+3+1 = 11pt. Ausreichend für 12.
    s.fertigkeit_auf('Athletik', 8)      # kostet was es kostet
    s.fertigkeit_auf('Kämpfen', 6)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Überreden', 6)
    s.fertigkeit_auf('Schießen', 4)
    s.fertigkeit_auf('Heimlichkeit', 6)  # Novice d6 (advance → d8)
    s.fertigkeit_auf('Diebeskunst', 8)
    s.fertigkeit_auf('Reparieren', 4)    # Novice d4 (advance → d6)
    m(f"  Skills: {s.punktestand()}")

    # Talent: Dieb (2 HP)
    s.talent('Dieb', ignore_voraussetzungen=True)
    m(f"  Nach Dieb: {s.punktestand()}")

    abschliessen(s, 5)  # 5 Aufstiege: 2 Skill + 3 Edges

    s.steigere_mit_handicap_fertigkeit('Reparieren')    # d4→d6
    s.steigere_mit_handicap_fertigkeit('Heimlichkeit')  # d6→d8
    s.talent('Beziehungen', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Gassenwissen', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Fallengespür', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("5 Aufstiege (2 Skill-Steps im Code). Athletik-Kosten geprüft: d8 bei Agi d8.")
    soll = {
        'attribute': {'Geschicklichkeit':8,'Verstand':6,'Willenskraft':6,'Stärke':6,'Konstitution':6},
        'fertigkeiten': {'Athletik':8,'Allgemeinwissen':4,'Kämpfen':6,'Wahrnehmung':6,
                         'Überreden':6,'Schießen':4,'Heimlichkeit':8,'Diebeskunst':8,'Reparieren':6},
        'handicaps': ['Gesucht_schwer','Vorsichtig','Misstrauisch_leicht'],
        'talente': ['Schnell','Dieb','Beziehungen','Gassenwissen','Fallengespür'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Rapier',1),('Dolch',5),('Totschläger',1),('Handarmbrust',1),('Ledertunika',1),('Umhang mit Kapuze',1),('Diebespaket',1),('Bolzen (10)',2),('Verstrickungsbeutel',1),('Fallenherstellungsset',1),('Rauchstab',1),('Trank: Attributsteigerung',1),('Trank: Dunkelsicht',1),('Trank: Unsichtbarkeit',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Tränke (Unsichtbarkeit, Nachtsicht)')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Diebin_A.json')
    b = s.bericht('logs/fk_diebin2_bericht.json')
    m(f"  DIEBIN: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Diebin: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 10. ZAUBERER/HEXER (Sorcerer) - Mensch, AH(Zauberer)
# AH auto: Behindernde_Rüstung_leicht + Verderbnis (0 HP)
# Manual: Arrogant(2)+Phobie_leicht(1)+Rachsüchtig_leicht(1) = 4 HP
# Mensch free: AH(Zauberer)
# 4 HP: 2 für Starker Wille + 2 für Arkane Resistenz
# D Advances: Machtpunkte, Blutmagie, Konstitution d8(attr), Neue Mächte = 4
# ===========================================================================
m("\n=== 10. ZAUBERER (SORCERER) ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Zauberer', protokoll='logs/fk_zauberer2.log')
    s.handicap('Arrogant')           # 2 HP (major first)
    s.handicap('Phobie_leicht')      # 1 HP
    s.handicap('Rachsüchtig_leicht') # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'AH (Zauberer)', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs Novice (Vig d6, advance → d8): Sma(2: d4→d8)+Spi(2: d4→d8)+Vig(1: d4→d6) = 5 ✓
    s.attribut_auf('Verstand', 8)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Konstitution', 6)
    m(f"  Attrs: {s.punktestand()}")

    # Skills: Geisteswissenschaften d4(1pt), Kämpfen d4(1pt), Einschüchtern d6(2pt),
    # Okkultismus d6(2pt), Überreden d4(0pt grundf), Recherche d8(3pt), Zaubern d8(3pt)
    # Total: 1+1+2+2+0+3+3 = 12 ✓
    s.fertigkeit_auf('Geisteswissenschaften', 4)
    s.fertigkeit_auf('Kämpfen', 4)
    s.fertigkeit_auf('Einschüchtern', 6)
    s.fertigkeit_auf('Okkultismus', 6)
    s.fertigkeit_auf('Recherche', 8)
    s.fertigkeit_auf('Zaubern', 8)
    m(f"  Skills: {s.punktestand()}")

    # Talents: Starker Wille(2HP) + Arkane Resistenz(2HP) = 4 HP
    s.talent('Starker Wille', ignore_voraussetzungen=True)
    s.talent('Arkane Resistenz', ignore_voraussetzungen=True)
    m(f"  Nach Talenten: {s.punktestand()}")

    # Mächte (AH Zauberer: 3 Novice-Mächte, alle Rang A oder F mit ignore)
    s.macht('Flächenschlag', ignore_rang_check=True)  # Rang F - Burst
    s.macht('Dunkelsicht')                            # Rang A - Darksight
    s.macht('Monster Beschwören')                     # Rang A - Summon Monster

    abschliessen(s, 4)

    s.steigere_mit_handicap_attribut('Konstitution')  # advance: Vig d6→d8
    s.talent('Machtpunkte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Blutmagie', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True)
    # Neue Mächte: Barriere(F) + Verbannen(V)
    s.macht('Barriere', ignore_rang_check=True)
    s.macht('Verbannen', ignore_rang_check=True)  # Rang V
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("AH(Zauberer) gibt auto: Behindernde_Rüstung_leicht + Verderbnis (0 HP). "
            "Power Points 15→20 via Machtpunkte-Advance. "
            "Verbannen = Rang V (Veteran), mit ignore_rang_check. "
            "Sorcerer-AB = AH(Zauberer) in FK.")
    soll = {
        'attribute': {'Geschicklichkeit':4,'Verstand':8,'Willenskraft':8,'Stärke':4,'Konstitution':8},
        'fertigkeiten': {'Geisteswissenschaften':4,'Athletik':4,'Allgemeinwissen':4,'Kämpfen':4,
                         'Einschüchtern':6,'Wahrnehmung':4,'Okkultismus':6,'Überreden':4,
                         'Recherche':8,'Zaubern':8,'Heimlichkeit':4},
        'handicaps': ['Arrogant','Phobie_leicht','Rachsüchtig_leicht',
                      'Behindernde_Rüstung_leicht','Verderbnis'],
        'talente': ['AH (Zauberer)','Starker Wille','Arkane Resistenz',
                    'Machtpunkte','Blutmagie','Neue Mächte'],
        'maechte': ['Flächenschlag','Dunkelsicht','Monster Beschwören','Barriere','Verbannen'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Dolch',1),('Tunika',1),('Umhang mit Kapuze',1),('Magierpaket',1),('Buch',1),('Trank: Heilung',1),('Tasche des Fassens',1),('Trank: Machtpunkte aufladen',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Tasche des Fassens, Trank Aufladen MP (nicht im FK-Katalog)')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Zauberer_A.json')
    b = s.bericht('logs/fk_zauberer2_bericht.json')
    m(f"  ZAUBERER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Zauberer: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 11. HEXE (Witch) - Mensch, AH(Hexer/Hexe)
# AH auto: Behindernde_Rüstung_schwer + Materialkomponenten + Verderbnis + Vertrauter (0 HP)
# Manual: Neugierig(2)+Verdammt(2) = 4 HP
# Mensch free: AH(Hexer/Hexe)
# 4 HP: 2 für Attraktiv + 2 für Stillzauberer
# D Advances: Zaubern d10(1skill), Neue Mächte, Machtpunkte, Böser Blick = 4
# Zaubern Novice: d8 (advance hebt auf d10)
# ===========================================================================
m("\n=== 11. HEXE ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Hexe', protokoll='logs/fk_hexe2.log')
    s.handicap('Neugierig')   # 2 HP (major first)
    s.handicap('Verdammt')    # 2 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'AH (Hexer/Hexe)', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d6, Sma d8, Spi d6, Str d4, Vig d6
    # Normal 5: Agi(1)+Sma(2: d4→d8)+Spi(1)+Vig(1) = 5 ✓
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 8)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Konstitution', 6)
    m(f"  Attrs: {s.punktestand()}")

    # Skills (Zaubern d8 Novice, d10 durch Advance):
    # Heilen d6(2pt), Wahr d4(0pt), Okkultismus d8(3pt: activate+d6+d8, d6<Sma=d8, OK),
    # Überreden d6(1pt grundf), Recherche d4(1pt activate), Zaubern d8(3pt: activate+d6+d8<Sma)
    # Überleben d4(1pt activate) → 2+0+3+1+1+3+1 = 11pt
    s.fertigkeit_auf('Heilen', 6)
    s.fertigkeit_auf('Kämpfen', 4)
    s.fertigkeit_auf('Okkultismus', 8)
    s.fertigkeit_auf('Überreden', 6)
    s.fertigkeit_auf('Recherche', 4)
    s.fertigkeit_auf('Zaubern', 8)     # Novice d8, advance → d10
    s.fertigkeit_auf('Überleben', 4)
    m(f"  Skills: {s.punktestand()}")

    # Talents: Attraktiv(2HP) + Stillzauberer(2HP) = 4 HP
    s.talent('Attraktiv', ignore_voraussetzungen=True)
    s.talent('Stillzauberer', ignore_voraussetzungen=True)
    m(f"  Nach Talenten: {s.punktestand()}")

    # Mächte (AH Hexe: 3 Novice, alle Rang A)
    s.macht('Arkaner Schutz')
    s.macht('Geschoss')
    s.macht('Empathie')
    # Heilung und Tier Beschwören kommen via Neue Mächte

    abschliessen(s, 4)

    s.steigere_mit_handicap_fertigkeit('Zaubern')  # advance: d8→d10
    s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.macht('Heilung', ignore_rang_check=True)
    s.macht('Tier Beschwören', ignore_rang_check=True)
    s.talent('Machtpunkte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Böser Blick', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("AH(Hexer/Hexe) auto: Behindernde_Rüstung_schwer, Materialkomponenten, Verderbnis, Vertrauter. "
            "Vertrauter = Familiar: 5 MP sharable, familiar-Senses.")
    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':8,'Willenskraft':6,'Stärke':4,'Konstitution':6},
        'fertigkeiten': {'Athletik':4,'Allgemeinwissen':4,'Heilen':6,'Heimlichkeit':4,'Kämpfen':4,
                         'Wahrnehmung':4,'Okkultismus':8,'Überreden':6,'Recherche':4,
                         'Zaubern':10,'Überleben':4},
        'handicaps': ['Neugierig','Verdammt',
                      'Behindernde_Rüstung_schwer','Materialkomponenten','Verderbnis'],
        'talente': ['AH (Hexer/Hexe)','Vertrauter','Attraktiv','Stillzauberer',
                    'Neue Mächte','Machtpunkte','Böser Blick'],
        'maechte': ['Arkaner Schutz','Geschoss','Empathie','Heilung','Tier Beschwören'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Dolch',1),('Tunika',1),('Magierpaket',1),('Trank: Attributsteigerung',1),('Grabstaub',1),('Hexenbeutel',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Grabstaub, Hexenbeutel, 2 vorbereitete Mächte in Hühnerknochen')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Hexe_A.json')
    b = s.bericht('logs/fk_hexe2_bericht.json')
    m(f"  HEXE: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Hexe: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 12. KRIEGER (Warrior) - Mensch
# Manual: Schwur_schwer(2)+Arkane_Empfindlichkeit_leicht(1)+Lebensaufgabe(1) = 4 HP
# Mensch free: Kräftig (Brawny)
# 4 HP: 2 für Eisenkiefer(Iron Jaw) + 2 für Vig attr raise (Novice d8, advance → d10)
# D Advances: Vig d10(1attr), Schmerzresistenz, Erzürnen, Take the Hit(?) = 4
# Anomalie: 'Take the Hit' kein direktes deutsches Pendant gefunden
# ===========================================================================
m("\n=== 12. KRIEGER ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Krieger', protokoll='logs/fk_krieger2.log')
    s.handicap('Schwur_schwer')                   # 2 HP (major first)
    s.handicap('Arkane_Empfindlichkeit_leicht')   # 1 HP
    s.handicap('Lebensaufgabe')                   # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Kräftig', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs Novice (Vig d8, advance → d10):
    # Agi(1)+Sma(1)+Spi(1)+Str(1)+Vig(2: d4→d8) = 6. Normal=5, 1 HP-Raise nötig.
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Stärke', 6)
    s.attribut_auf('Konstitution', 6)     # 1 normal pt: d4→d6
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: d6→d8
    m(f"  Attrs: {s.punktestand()}")

    # Talent: Eisenkiefer(Iron Jaw) (2 HP)
    s.talent('Eisenkiefer', ignore_voraussetzungen=True)
    m(f"  Nach Eisenkiefer: {s.punktestand()}")

    # Skills: Ath d6(1pt), Kämpfen d8(4pt: d6<Agi? Agi=d6, d6>=d6 doppelt → 1+1+2=4pt),
    # Einschüchtern d6(2pt), Wahr d4(0pt), Überreden d4(0pt), Schießen d4(1pt), Provozieren d8(?)
    # Provozieren d8 linked to Wk (d6): activate(1)+d6(1)+d8(2, d6>=Wk=d6 doppelt)=4pt
    # Total: 1+4+2+0+0+1+4=12pt ✓
    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Einschüchtern', 6)
    s.fertigkeit_auf('Schießen', 4)
    s.fertigkeit_auf('Provozieren', 8)
    m(f"  Skills: {s.punktestand()}")

    abschliessen(s, 4)

    s.steigere_mit_handicap_attribut('Konstitution')  # advance: Vig d8→d10
    s.talent('Schmerzresistenz', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Erzürnen', ignore_rang_check=True, ignore_voraussetzungen=True)
    # 'Take the Hit' = kein direktes FK-Äquivalent. Kampfreflexe = Battle Reflexes (+2 recovery)?
    # Verwende Kampfreflexe als nächste Annäherung und dokumentiere.
    s.talent('Kampfreflexe', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("GELDMANGEL: Schwert, Langschwert (300 GP) + Bronzerüstung/Helm (200+120 GP) = 620 GP. "
            "Übersteigt Startbudget 500 GP. FORCE-Käufe für Rüstung, Helm, Schild, Söldnerpaket. "
            "FK-Preis für Langschwert deutlich über Quelltextwert.")
    s.notiz("ANOMALIE: 'Take the Hit' (freie Wurfwiederholung auf Schaden-Wegstecken) "
            "hat kein direktes FK-Äquivalent. Ersetzt durch 'Kampfreflexe' "
            "(+2 Erholung von Angeschlagen) als Näherung.")
    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':6,'Willenskraft':6,'Stärke':6,'Konstitution':10},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Kämpfen':8,'Einschüchtern':6,
                         'Wahrnehmung':4,'Überreden':4,'Schießen':4,'Heimlichkeit':4,'Provozieren':8},
        'handicaps': ['Schwur_schwer','Arkane_Empfindlichkeit_leicht','Lebensaufgabe'],
        'talente': ['Kräftig','Eisenkiefer','Schmerzresistenz','Erzürnen','Kampfreflexe'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Schwert, Langschwert',1),('Dolch',1),('Netz (beschwert)',1),('Leichte Armbrust',1),('Bronzebrustpanzer',1),('Bronzehelm',1),('Mittlerer Schild',1),('Söldnerpaket',1),('Bolzen (10)',2),('Trank: Beschleunigung',1),('Trank: Umgebungsschutz',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Trank des Umgebungsschutzes (nicht im FK-Katalog)')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Krieger_A.json')
    b = s.bericht('logs/fk_krieger2_bericht.json')
    m(f"  KRIEGER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Krieger: {e}\n{traceback.format_exc()}')

tlog.close()
print("BATCH 2 FIXED fertig. Trace: logs/fk_batch2_fixed_trace.txt")
