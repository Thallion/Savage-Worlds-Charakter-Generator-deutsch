"""
BATCH 4 FIXED: Fantasy Kompendium Archetypen
Narr, Ritter, Schamane, Meister des Wissens, Totemkrieger, Tüftler

Korrekturen gegenüber Batch 4 v1:
- Protokoll-Logs auf _2-Suffix umgestellt
- Narr: Wahrnehmung d6 ergänzt (notice d6 aus Referenz, fehlte im ursprünglichen Build)
- Schamane: Kämpfen d4 ergänzt (fighting d4 aus Referenz, fehlte im ursprünglichen Build)
- Ritter: Plattenbrustharnisch (500 GP) + Schwerer geschlossener Helm (300 GP) =
  800 GP übersteigt Startbudget stark → FORCE-Käufe dokumentiert
"""
import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/fk_batch4_fixed_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()
def ab(s, n):
    s.ch.char_gen_completed = True
    for _ in range(n): increase_aufstiege(s.ch)
    m(f"  → {n} Aufstiege, Rang={s.ch.rang}")

# ===========================================================================
# 19. NARR (Jester) - Infernaler, AH(Barde)
# AH auto: Behindernde_Rüstung_leicht
# Infernaler: kein auto in selected_handicaps (nur spezielle_effekte)
# Manual: Große Klappe(1)+Übermütig(2)+Tick(1) = 4 HP
# 4 HP: 2 für AH(Barde) + 2 für Vig attr raise (d4→d6)
# D Advances: Konter, Ermutigen, Erniedrigen, Täuscher = 4
# ===========================================================================
m("=== 19. NARR ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Narr', protokoll='logs/fk_narr2.log')
    s.handicap('Übermütig')      # 2 HP
    s.handicap('Große Klappe')   # 1 HP
    s.handicap('Tick')           # 1 HP → 4 HP
    s.volk('Infernaler')
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d6(1), Sma d8(2), Spi d8(2) → 5pt, Vig d4→d6 mit HP
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 8)
    s.attribut_auf('Willenskraft', 8)
    s.steigere_mit_handicap_attribut('Konstitution')   # 2 HP: d4→d6
    m(f"  Attrs: {s.punktestand()}")

    # AH(Barde) mit HP (2 HP) - auto-adds Behindernde_Rüstung_leicht
    s.talent('AH (Barde)', ignore_voraussetzungen=True)
    m(f"  Nach AH(Barde): {s.punktestand()}")

    # Skills (12pt): Ath d6(1pt grundf), AW d6(1pt grundf), Kämpfen d4(1pt),
    # Einschüchtern d6(2pt), Wahr d6(1pt grundf), Darbietung d10(5pt), Überreden d6(1pt grundf)
    # = 1+1+1+2+1+5+1 = 12 ✓
    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Allgemeinwissen', 6)
    s.fertigkeit_auf('Kämpfen', 4)
    s.fertigkeit_auf('Einschüchtern', 6)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Darbietung', 10)
    s.fertigkeit_auf('Überreden', 6)
    m(f"  Skills: {s.punktestand()}")

    # Mächte (AH Barde: 3 Novice)
    s.macht('Eigenschaft erhöhen/senken')
    s.macht('Verwirrung')
    s.macht('Geräusch/Stille')

    ab(s, 4)
    s.talent('Konter', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Ermutigen', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Erniedrigen', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Täuscher', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("AH(Barde) auto: Behindernde_Rüstung_leicht. Infernaler: Dunkelsicht, Hörner, Teuflische Natur als spezielle_effekte (nicht in selected_handicaps).")
    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':8,'Willenskraft':8,'Stärke':4,'Konstitution':6},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':6,'Kämpfen':4,'Einschüchtern':6,
                         'Wahrnehmung':6,'Darbietung':10,'Überreden':6,'Heimlichkeit':4},
        'handicaps': ['Übermütig','Große Klappe','Tick','Behindernde_Rüstung_leicht'],
        'talente': ['AH (Barde)','Konter','Ermutigen','Erniedrigen','Täuscher'],
        'maechte': ['Eigenschaft erhöhen/senken','Verwirrung','Geräusch/Stille'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Dolch/Messer',1),('Totschläger',1),('Ledertunika',1),('Unterhalterpaket',1),('Trank: Attributsteigerung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Trank der Unsichtbarkeit (nicht im FK-Katalog)')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Narr_A.json')
    b = s.bericht('logs/fk_narr2_bericht.json')
    m(f"  NARR: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Narr: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 20. RITTER (Knight) - Mensch
# Manual: Ehrenkodex(2)+Verpflichtung_schwer(2) = 4 HP
# Mensch free: Kräftig
# 4 HP: 2 für Vig d4→d6 + 2 für Vig d6→d8
# D Advances: Soldat(1), Kriegskunst d6+Überreden d6(2skill), Ritter(1), Block(1) = 5
# Vig Novice: d4 (alle Attr-HP für Vig)
# ===========================================================================
m("\n=== 20. RITTER ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Ritter', protokoll='logs/fk_ritter2.log')
    s.handicap('Ehrenkodex')         # 2 HP
    s.handicap('Verpflichtung_schwer')# 2 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Kräftig', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d6(1), Sma d6(1), Spi d6(1), Str d8(2) → 5pt; Vig d4→d8 mit HP
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Stärke', 8)
    # Vig d4→d6 (2HP) then d6→d8 (2HP) = 4HP
    s.steigere_mit_handicap_attribut('Konstitution')  # d4→d6
    s.steigere_mit_handicap_attribut('Konstitution')  # d6→d8
    m(f"  Attrs: {s.punktestand()}")

    # Skills Novice (Kriegskunst d4, Überreden d4 - beide via Advances auf d6):
    # AW d4(0), Kriegskunst d4(1pt activate, Novice), Kämpfen d8(4pt, Agi=d6), Wahr d6(1pt),
    # Überreden d4(0grundf Novice), Reiten d8(4pt, Agi=d6), Schießen d6(2pt) = 0+1+4+1+0+4+2=12 ✓
    # Kämpfen d8: linked to Agi d6. activate(1,eff2<6)+d4→d6(1,eff4<6)+d6→d8(2,eff6>=6) = 4pt ✓
    # Reiten d8: linked to Agi d6. Same: 4pt ✓
    s.fertigkeit_auf('Kriegskunst', 4)    # activate only (Novice, advance → d6)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Reiten', 8)
    s.fertigkeit_auf('Schießen', 6)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 5)  # 5 Aufstiege: 2 Skill-Steps + 3 Edges
    s.steigere_mit_handicap_fertigkeit('Kriegskunst')   # d4→d6
    s.steigere_mit_handicap_fertigkeit('Überreden')     # d4→d6 (grundf)
    s.talent('Soldat', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Ritter', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Block', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':6,'Willenskraft':6,'Stärke':8,'Konstitution':8},
        'fertigkeiten': {'Athletik':4,'Allgemeinwissen':4,'Kriegskunst':6,'Kämpfen':8,
                         'Wahrnehmung':6,'Überreden':6,'Reiten':8,'Schießen':6,'Heimlichkeit':4},
        'handicaps': ['Ehrenkodex','Verpflichtung_schwer'],
        'talente': ['Kräftig','Soldat','Ritter','Block'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Bastardschwert',1),('Schwere Armbrust',1),('Lanze',1),('Plattenbrustharnisch',1),('Schwerer geschlossener Helm',1),('Mittlerer Schild',1),('Söldnerpaket',1),('Bolzen (10)',2),('Reitbedarf',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Streitross mit gepolsteter Schabracke')
    s.notiz('GELDMANGEL: Plattenbrustharnisch (500 GP) + Schwerer geschlossener Helm (300 GP) = 800 GP. '
            'Übersteigt Startbudget 500 GP massiv. FORCE-Käufe für alle teuren Items.')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Ritter_A.json')
    b = s.bericht('logs/fk_ritter2_bericht.json')
    m(f"  RITTER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Ritter: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 21. SCHAMANE (Shaman) - Mensch, AH(Schamane)
# AH auto: Behindernde_Rüstung_leicht + Tick + Materialkomponenten
# Manual: Chauvinistisch_schwer(2)+Loyal(1)+Arm(1) = 4 HP
# Mensch free: AH(Schamane)
# 4 HP: 2 für Vig d4→d6 + 2 für Wahr skill (d6→d8 HP nach Skills)
# D Advances: Geweihter Fetisch, Bestienflüsterer, Neue Mächte(Verstricken+Tierfreund), Urtümliche Magie = 4
# ===========================================================================
m("\n=== 21. SCHAMANE ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Schamane', protokoll='logs/fk_schamane2.log')
    s.handicap('Chauvinistisch_schwer')# 2 HP
    s.handicap('Loyal')                # 1 HP
    s.handicap('Arm')                  # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'AH (Schamane)', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d6(1), Sma d6(1), Spi d10(3), Vig d6(Novice d4→d6 mit HP) → 5pt normal
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 10)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: Vig d4→d6
    m(f"  Attrs: {s.punktestand()}")

    # Skills (12pt normal): Glaube d10(4pt), Heilen d6(2pt), Wahr d6(1pt grundf),
    # Okkultismus d6(2pt), Überl d6(2pt), Heim d4(0grundf) → 4+2+1+2+2=11pt, 1pt left
    # Then Wahr d6→d8 mit HP (2HP): linked to Sma d6. eff6>=6 → 2HP
    s.fertigkeit_auf('Glaube', 10)
    s.fertigkeit_auf('Heilen', 6)
    s.fertigkeit_auf('Kämpfen', 4)     # fighting d4 (1pt Aktivierung)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Okkultismus', 6)
    s.fertigkeit_auf('Überleben', 6)
    m(f"  Skills (normal): {s.punktestand()}")

    # Wahr d6→d8 mit HP (2 HP): double cost because d6 eff >= Sma d6 eff
    # But wait: after attr raise (2HP) and before skill HP, HP=2 remaining. Use for Wahr d8.
    # BUT: talent takes HP first if HP > 1.5. Take talent FIRST isn't possible since AH is free.
    # steigere_mit_handicap_fertigkeit bypasses talent HP check.
    s.steigere_mit_handicap_fertigkeit('Wahrnehmung')   # 2HP: d6→d8 (double cost)
    m(f"  Nach Wahr d8: {s.punktestand()}")

    # Mächte (AH Schamane: 5 Novice)
    s.macht('Arkaner Schutz')
    s.macht('Eigenschaft erhöhen/senken')
    s.macht('Flächenschlag', ignore_rang_check=True)  # Burst F
    s.macht('Abwehren')   # deflection
    s.macht('Linderung')  # relief

    ab(s, 4)
    s.talent('Geweihter Fetisch', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Bestienflüsterer', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.macht('Verstricken', ignore_rang_check=True)
    s.macht('Tierfreund', ignore_rang_check=True)
    s.talent('Urtümliche Magie', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("AH(Schamane) auto: Behindernde_Rüstung_leicht, Tick, Materialkomponenten.")
    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':6,'Willenskraft':10,'Stärke':4,'Konstitution':6},
        'fertigkeiten': {'Athletik':4,'Allgemeinwissen':4,'Glaube':10,'Heilen':6,'Kämpfen':4,
                         'Wahrnehmung':8,'Okkultismus':6,'Überreden':4,'Heimlichkeit':4,'Überleben':6},
        'handicaps': ['Chauvinistisch_schwer','Loyal','Arm',
                      'Behindernde_Rüstung_leicht','Tick','Materialkomponenten'],
        'talente': ['AH (Schamane)','Geweihter Fetisch','Bestienflüsterer','Neue Mächte','Urtümliche Magie'],
        'maechte': ['Arkaner Schutz','Eigenschaft erhöhen/senken','Flächenschlag',
                    'Abwehren','Linderung','Verstricken','Tierfreund'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Stab (3,5 m)',1),('Dolch',1),('Ledertunika',1),('Wildnispaket',1),('Kreide (Schachtel mit 12 Stück)',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Kreidestaub der Geisterbann (Kreide als Ersatz), 5 GM Restgeld')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Schamane_A.json')
    b = s.bericht('logs/fk_schamane2_bericht.json')
    m(f"  SCHAMANE: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Schamane: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 22. MEISTER DES WISSENS (Loremaster) - Elf, AH(Magier)
# Elf auto: Zwei_linke_Hände, Nachtsicht; Agi d6 free
# AH auto: Behindernde_Rüstung_schwer, Materialkomponenten
# Manual: Neugierig(2)+Pazifist_leicht(1)+Tick(1) = 4 HP
# 4 HP: 2 für AH(Magier) + 2 für Spi d4→d6 (dann normal d6→d8 = 1pt)
# D Advances: Ermittler, Gelehrter, Alleskönner, Kühler Kopf = 4
# ===========================================================================
m("\n=== 22. MEISTER DES WISSENS ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Loremaster', protokoll='logs/fk_loremaster2.log')
    s.handicap('Neugierig')      # 2 HP
    s.handicap('Pazifist_leicht')# 1 HP
    s.handicap('Tick')           # 1 HP → 4 HP
    s.volk('Elf')   # Agi d6 gratis, Zwei_linke_Hände, Nachtsicht auto
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d8(d6→d8=1pt), Sma d10(3pt), Spi d8(d4→d6=1pt + d6→d8=1pt=2pt) → 6pt, 1 HP-Raise
    # Normal 5: Agi(1)+Sma(3)+Spi(1: d4→d6) = 5. Then Spi d6→d8 mit HP (2HP).
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Verstand', 10)
    s.attribut_auf('Willenskraft', 6)   # only 1 normal pt left → d4→d6
    s.steigere_mit_handicap_attribut('Willenskraft')  # 2 HP: d6→d8
    m(f"  Attrs: {s.punktestand()}")

    # Talent: AH(Magier) (2 HP)
    s.talent('AH (Magier)', ignore_voraussetzungen=True)
    m(f"  Nach AH(Magier): {s.punktestand()}")

    # Skills (12pt): Geistesw. d8(3pt), Ath d4(0grundf), AW d8(2pt),
    # Kämpfen d4(1pt), Wahr d6(1pt grundf), Überreden d4(0grundf),
    # Recherche d8(3pt), Zaubern d6(2pt) = 3+0+2+1+1+0+3+2 = 12 ✓
    s.fertigkeit_auf('Geisteswissenschaften', 8)
    s.fertigkeit_auf('Allgemeinwissen', 8)
    s.fertigkeit_auf('Kämpfen', 4)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Recherche', 8)
    s.fertigkeit_auf('Zaubern', 6)
    m(f"  Skills: {s.punktestand()}")

    # Mächte (AH Magier: 6 Novice, 15PP)
    s.macht('Arkanes entdecken/verbergen')
    s.macht('Verbannen', ignore_rang_check=True)  # dispel V
    s.macht('Aufspüren')          # locate
    s.macht('Verriegeln/Entriegeln')
    s.macht('Gedankenlesen')
    s.macht('Sprachen sprechen')

    ab(s, 4)
    s.talent('Ermittler', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Gelehrter', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Alleskönner', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Kühler Kopf', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    soll = {
        'attribute': {'Geschicklichkeit':8,'Verstand':10,'Willenskraft':8,'Stärke':4,'Konstitution':4},
        'fertigkeiten': {'Geisteswissenschaften':8,'Athletik':4,'Allgemeinwissen':8,'Kämpfen':4,
                         'Wahrnehmung':6,'Überreden':4,'Recherche':8,'Zaubern':6,'Heimlichkeit':4},
        'handicaps': ['Neugierig','Pazifist_leicht','Tick',
                      'Zwei linke Hände','Behindernde_Rüstung_schwer','Materialkomponenten'],
        'talente': ['Nachtsicht','AH (Magier)','Ermittler','Gelehrter','Alleskönner','Kühler Kopf'],
        'maechte': ['Arkanes entdecken/verbergen','Verbannen','Aufspüren',
                    'Verriegeln/Entriegeln','Gedankenlesen','Sprachen sprechen'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Dolch',1),('Tunika',1),('Magierpaket',1),('Buch',1),
                       ('Schriftrolle: Arkaner Schutz',1),('Schriftrolle: Verbündeten beschwören',1),
                       ('Schriftrolle: Schutz',1),('Schriftrolle: Unsichtbarkeit',1),
                       ('Schriftrolle: Teleportation',1),('Schriftrolle: Gedankenverbindung',1),
                       ('Schriftrolle: Eigenschaft erhöhen/senken',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: keine')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Loremaster_A.json')
    b = s.bericht('logs/fk_loremaster2_bericht.json')
    m(f"  LOREMASTER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Loremaster: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 23. TOTEMKRIEGER (Totem Warrior) - Mensch
# Manual: Nichtschwimmer(1)+Heldenhaft(2)+Dünnhäutig(1) = 4 HP
# Mensch free: Kräftig (Brawny)
# 4 HP: 2 für Schwer zu töten + 2 für Vig attr raise (d6→d8)
# D Advances: Kämpfen d10(1skill), Schmerzresistenz, Mächtiger Hieb, Mystische Kräfte = 4
# Mystische Kräfte: 10 PP, Self-only, Mächte können nicht normal hinzugefügt werden
# ===========================================================================
m("\n=== 23. TOTEMKRIEGER ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Totemkrieger', protokoll='logs/fk_totemkr2.log')
    s.handicap('Heldenhaft')      # 2 HP
    s.handicap('Nichtschwimmer')  # 1 HP
    s.handicap('Dünnhäutig')      # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Kräftig', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Spi d8(2), Str d8(2), Vig d6(1 normal d4→d6, then d6→d8 mit HP) → 5pt normal
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Stärke', 8)
    s.attribut_auf('Konstitution', 6)  # 1pt: d4→d6
    # Vig d6→d8 mit HP (2HP)
    s.steigere_mit_handicap_attribut('Konstitution')
    m(f"  Attrs: {s.punktestand()}")

    # Talent: Schwer zu töten (2 HP)
    s.talent('Schwer zu töten', ignore_voraussetzungen=True)
    m(f"  Nach Schwer zu töten: {s.punktestand()}")

    # Skills Novice (Kämpfen d8, advance → d10):
    # Ath d6(1pt grundf), Kämpfen d8(Agi=d4, doppelt!: 1+2+2=5pt), Einschüchtern d8(3pt),
    # Wahr d4(0grundf), Okkultismus d4(1pt), Überl d4(1pt), Heim d4(0grundf) = 1+5+3+0+1+1=11pt ✓
    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Kämpfen', 8)         # Novice d8 (Advance → d10)
    s.fertigkeit_auf('Einschüchtern', 8)
    s.fertigkeit_auf('Okkultismus', 4)
    s.fertigkeit_auf('Überleben', 4)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 4)
    s.steigere_mit_handicap_fertigkeit('Kämpfen')  # d8→d10
    s.talent('Schmerzresistenz', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Mächtiger Hieb', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Mystische Kräfte', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("Mystische Kräfte: 10 dedizierte PP mit Self-only Mächten. "
            "Mächte (Eigenschaft erhöhen/senken für Kämpfen/Stärke/Vig, Kriegersegen, Trägheit/Beschleunigung) "
            "können nicht via macht() hinzugefügt werden - sind Teil des Talents.")
    soll = {
        'attribute': {'Geschicklichkeit':4,'Verstand':4,'Willenskraft':8,'Stärke':8,'Konstitution':8},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Kämpfen':10,'Einschüchtern':8,
                         'Wahrnehmung':4,'Überreden':4,'Okkultismus':4,'Heimlichkeit':4,'Überleben':4},
        'handicaps': ['Heldenhaft','Nichtschwimmer','Dünnhäutig'],
        'talente': ['Kräftig','Schwer zu töten','Schmerzresistenz','Mächtiger Hieb','Mystische Kräfte'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Streitaxt',1),('Kurz-/Wurfspeer',1),('Ledertunika',1),('Wildnispaket',1),('Rauchstab',1),
                       ('Trank: Heilung',3),('Trank: Attributsteigerung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Trank des Umgebungsschutzes (nicht im FK-Katalog)')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Totemkmpf_A.json')
    b = s.bericht('logs/fk_totemkr2_bericht.json')
    m(f"  TOTEMKRIEGER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Totemkrieger: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 24. TÜFTLER (Tinkerer) - Gnom, AH(Tüftler)
# Gnom auto: Nachtsicht, Geschärfte Sinne talente; Verstand d6 free; Wahrnehmung +2
# AH auto: nothing
# Manual: Neugierig(2)+Wahnvorstellungen_leicht(1)+Fettleibig(1) = 4 HP
# 4 HP: 2 für AH(Tüftler) + 2 für Vig d4→d6
# D Advances: McGyver, Machtpunkte, Neue Mächte(Darksight+Wallwalker), Tüftlerrüstung = 4
# ===========================================================================
m("\n=== 24. TÜFTLER ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Tüftler', protokoll='logs/fk_tueftler2.log')
    s.handicap('Neugierig')            # 2 HP
    s.handicap('Wahnvorstellungen_leicht')# 1 HP
    s.handicap('Fettleibig')           # 1 HP → 4 HP
    s.volk('Gnom')    # Verstand d6 gratis, Nachtsicht+Geschärfte Sinne auto
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Sma d12(3: d6→d12=3pts), Spi d6(1), Str d6(1) → 5pt; Vig d4→d6 mit HP
    s.attribut_auf('Verstand', 12)    # 3pts (d6→d12=3 steps)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Stärke', 6)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: d4→d6
    m(f"  Attrs: {s.punktestand()}")

    # AH(Tüftler) mit HP (2 HP)
    s.talent('AH (Tüftler)', ignore_voraussetzungen=True)
    m(f"  Nach AH(Tüftler): {s.punktestand()}")

    # Skills: Wahrnehmung startet bei d6 wegen Gnome-Bonus (fertigkeits_startboni).
    # Reparieren d12: linked to Sma(d12). activate(1)+d6(1)+d8(1)+d10(1)+d12(1) = 5pt all <d12
    # AW d6(1pt grundf), Kämpfen d6(2pt), Wahr d8(1pt: d6→d8, linked to Sma=d12, 6<12 normal) = 5pt
    # Recherche d6(2pt) → 5+1+2+1+2=11pt ✓ (1pt leftover)
    s.fertigkeit_auf('Reparieren', 12)
    s.fertigkeit_auf('Allgemeinwissen', 6)
    s.fertigkeit_auf('Kämpfen', 6)
    s.fertigkeit_auf('Wahrnehmung', 8)  # Gnom gives d6 start, raise to d8 = 1pt
    s.fertigkeit_auf('Recherche', 6)
    m(f"  Skills: {s.punktestand()}")

    # Mächte (AH Tüftler: 2 Novice)
    s.macht('Flächenschlag', ignore_rang_check=True)  # Burst (gun)
    s.macht('Schutz vor Naturgewalten')               # environmental protection (suit)

    ab(s, 4)
    s.talent('McGyver', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Machtpunkte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.macht('Dunkelsicht', ignore_rang_check=True)
    s.macht('Wandkrabbler', ignore_rang_check=True)
    s.talent('Tüftlerrüstung', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("Gnom: Verstand d6 gratis, Wahrnehmung startet d6 (bonus). "
            "Tüftler: Reparieren als arkane Fertigkeit. 2 Novice-Mächte (AH Tüftler Limit).")
    soll = {
        'attribute': {'Geschicklichkeit':4,'Verstand':12,'Willenskraft':6,'Stärke':6,'Konstitution':6},
        'fertigkeiten': {'Allgemeinwissen':6,'Athletik':4,'Kämpfen':6,'Wahrnehmung':8,
                         'Überreden':4,'Reparieren':12,'Heimlichkeit':4,'Recherche':6},
        'handicaps': ['Neugierig','Wahnvorstellungen_leicht','Fettleibig'],
        'talente': ['Nachtsicht','Geschärfte Sinne','AH (Tüftler)',
                    'McGyver','Machtpunkte','Neue Mächte','Tüftlerrüstung'],
        'maechte': ['Flächenschlag','Schutz vor Naturgewalten','Dunkelsicht','Wandkrabbler'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Dolch',1),('Ledertunika',1),('Artefakterschaffertasche',1),('Abenteurerpaket',1),('Fallenherstellungsset',1),('Rauchstab',1),('Verstrickungsbeutel',1),('Donnerstein',1),('Trank: Heilung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Tasche des Fassens, Sonnenstab')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Tueftler_A.json')
    b = s.bericht('logs/fk_tueftler2_bericht.json')
    m(f"  TÜFTLER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Tüftler: {e}\n{traceback.format_exc()}')

tlog.close()
print("BATCH 4 FIXED fertig. Trace: logs/fk_batch4_fixed_trace.txt")
