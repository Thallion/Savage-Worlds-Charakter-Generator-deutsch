"""
BATCH 5 FIXED: Fantasy Kompendium Archetypen
Akrobatin, Amazone, Schwerttänzerin, Aristokrat, Verteidiger, Rüpel

Korrekturen gegenüber Batch 5 v1:
- Protokoll-Logs auf _2-Suffix umgestellt
- Verteidiger: Außenseiter_schwer (2 HP) statt Außenseiter_leicht →
  2. Konstitution-Steigerung (d6→d8) jetzt korrekt; Advance → d10
- Alle übrigen Anomalien nur NOTIZen (fehlende Tränke, Racial-Effekte)
"""
import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/fk_batch5_fixed_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()
def ab(s, n):
    s.ch.char_gen_completed = True
    for _ in range(n): increase_aufstiege(s.ch)
    m(f"  → {n} Aufstiege, Rang={s.ch.rang}")

# ===========================================================================
# 25. AKROBATIN (Acrobat) - Halbelf Elfen-Erbe
# Halbelf: Nachtsicht, freies Attribut Geschicklichkeit
# Manual: Übermütig(2)+Schwerzüngig(2) = 4 HP
# 4 HP: 2 für Schnell + 2 für Vig attr raise (d4→d6)
# D Advances: Dieb, Akrobat, Parkour, Kampfakrobat = 4
# ===========================================================================
m("=== 25. AKROBATIN ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Akrobatin', protokoll='logs/fk_akrobat2.log')
    s.handicap('Übermütig')    # 2 HP
    s.handicap('Schwerzüngig') # 2 HP → 4 HP
    s.volk('Halbelf')
    s.volk_freies_attribut('Halbelf', 'Geschicklichkeit')  # Agi d6 gratis
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d12(Halbelf d6→d12=3pt), Sma d6(1pt), Str d6(1pt) → 5pt, Vig d4→d6 mit HP
    s.attribut_auf('Geschicklichkeit', 12)  # d6→d12 = 3 steps = 3pt
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Stärke', 6)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: d4→d6
    m(f"  Attrs: {s.punktestand()}")

    # Talent: Schnell (2 HP)
    s.talent('Schnell', ignore_voraussetzungen=True)
    m(f"  Nach Schnell: {s.punktestand()}")

    # Skills (12pt): Ath d12(grundf: 4pt all <Agi d12), AW d4(0),
    # Kämpfen d6(2pt: 1+1,<Agi12), Wahr d6(grundf 1pt), Schießen d4(1pt),
    # Heim d8(grundf: d4→d8=2pt, all <Agi12), Diebeskunst d6(2pt: 1+1,<Agi12)
    # Total: 4+0+2+1+1+2+2=12 ✓
    s.fertigkeit_auf('Athletik', 12)
    s.fertigkeit_auf('Kämpfen', 6)
    s.fertigkeit_auf('Wahrnehmung', 6)
    s.fertigkeit_auf('Schießen', 4)
    s.fertigkeit_auf('Heimlichkeit', 8)
    s.fertigkeit_auf('Diebeskunst', 6)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 4)
    s.talent('Dieb', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Akrobat', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Parkour', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Kampfakrobat', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    soll = {
        'attribute': {'Geschicklichkeit':12,'Verstand':6,'Willenskraft':4,'Stärke':6,'Konstitution':6},
        'fertigkeiten': {'Athletik':12,'Allgemeinwissen':4,'Kämpfen':6,'Wahrnehmung':6,
                         'Überreden':4,'Schießen':4,'Heimlichkeit':8,'Diebeskunst':6},
        'handicaps': ['Übermütig','Schwerzüngig'],
        'talente': ['Nachtsicht','Schnell','Dieb','Akrobat','Parkour','Kampfakrobat'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Stab (3,5 m)',1),('Dolch',8),('Peitsche',1),('Ledertunika',1),('Bandolier',1),('Diebespaket',1),('Rauchstab',1),('Krähenfüße',1),
                       ('Trank: Beschleunigung',1),('Trank: Heilung',1),('Trank: Geistige Stärke',1),('Trank: Attributsteigerung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Trank Wandkrabbler (nicht im FK-Katalog)')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Akrobatin_A.json')
    b = s.bericht('logs/fk_akrobat2_bericht.json')
    m(f"  AKROBATIN: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Akrobatin: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 26. AMAZONE (Amazon) - Mensch
# Manual: Heldenhaft(2)+Idealistisch(1)+Loyal(1) = 4 HP
# Mensch free: Flink (Fleet-Footed)
# 4 HP: 2 für Schnell + 2 für Vig d4→d6
# D Advances: Volltreffer, Im Sattel geboren, Formation Fighter(?), Meisterschütze = 4
# Anomalie: Formation Fighter kein FK-Äquivalent → Haltet die Stellung! als Näherung
# ===========================================================================
m("\n=== 26. AMAZONE ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Amazone', protokoll='logs/fk_amazone2.log')
    s.handicap('Heldenhaft')    # 2 HP
    s.handicap('Idealistisch')  # 1 HP
    s.handicap('Loyal')         # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Flink', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d8(2pt), Sma d6(1pt), Spi d6(1pt), Str d6(1pt) → 5pt, Vig d4→d6 mit HP
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Stärke', 6)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: d4→d6
    m(f"  Attrs: {s.punktestand()}")

    s.talent('Schnell', ignore_voraussetzungen=True)  # 2 HP
    m(f"  Nach Schnell: {s.punktestand()}")

    # Skills (12pt): Ath d6(grundf 1pt), AW d4(0), Kämpfen d8(3pt, Agi=d8: 1+1+1),
    # Einschüchtern d6(2pt), Wahr d6(1pt grundf), Reiten d6(2pt, Agi=d8: 1+1),
    # Schießen d8(3pt, Agi=d8: 1+1+1) = 1+0+3+2+1+2+3=12 ✓
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
    # Formation Fighter kein FK-Äquivalent
    s.talent('Haltet die Stellung!', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Meisterschütze', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("ANOMALIE: 'Formation Fighter' (+2 Überzahlbonus) kein FK-Äquivalent. "
            "Ersetzt durch 'Haltet die Stellung!' (+1 Robustheit Statisten).")
    soll = {
        'attribute': {'Geschicklichkeit':8,'Verstand':6,'Willenskraft':6,'Stärke':6,'Konstitution':6},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Kämpfen':8,'Einschüchtern':6,
                         'Wahrnehmung':6,'Überreden':4,'Reiten':6,'Schießen':8,'Heimlichkeit':4},
        'handicaps': ['Heldenhaft','Idealistisch','Loyal'],
        'talente': ['Flink','Schnell','Volltreffer','Im Sattel geboren',
                    'Haltet die Stellung!','Meisterschütze'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Chakram',1),('Bogen, Kurz-',1),('Entermesser',1),('Bronzebrustpanzer',1),('Pfeile (20)',1),('Brandpfeile (20)',1),('Abenteurerpaket',1),('Trank: Beschleunigung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: Pfeil der Genauigkeit ×1')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Amazone_A.json')
    b = s.bericht('logs/fk_amazone2_bericht.json')
    m(f"  AMAZONE: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Amazone: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 27. SCHWERTTÄNZERIN (Blade Dancer) - Mensch, AH(Barde)
# AH auto: Behindernde_Rüstung_leicht
# Manual: Talisman_schwer(2)+Loyal(1)+Beschämt(1) = 4 HP
# Mensch free: AH(Barde)
# 4 HP: 2 für Vig d4→d6 + 2 für Sehr Attraktiv? Nein - D Advance!
# Alle Edges sind D Advances → 4 HP für Attrs/Skills
# D Advances: Sehr Attraktiv, Beidhändiger Kampf, Neue Mächte, Schneller Angriff = 4
# ===========================================================================
m("\n=== 27. SCHWERTTÄNZERIN ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Schwerttänzerin', protokoll='logs/fk_schwert2.log')
    s.handicap('Talisman_schwer')  # 2 HP
    s.handicap('Loyal')            # 1 HP
    s.handicap('Beschämt')         # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'AH (Barde)', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d8(2pt), Spi d8(2pt), Str d6(1pt) → 5pt, Vig d4→d6 mit HP(2HP), 2HP für Skill
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Stärke', 6)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: d4→d6
    m(f"  Attrs: {s.punktestand()}")

    # Skills (12pt+2HP): Ath d8(grundf: d4→d8=2pt,Agi=d8),
    # Kämpfen d8(3pt, Agi=d8), Wahr d4(0grundf), Darbietung d10(5pt,Wk=d8→d8→d10 double),
    # Heim d8(grundf: 2pt, Agi=d8) = 2+3+0+5+2=12 ✓
    s.fertigkeit_auf('Athletik', 8)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Darbietung', 10)
    s.fertigkeit_auf('Heimlichkeit', 8)
    m(f"  Skills: {s.punktestand()}")

    # 2 HP restlich → Darbietung/Heim waren teuer, kein extra HP-Skill nötig
    # Mächte (AH Barde: 3 Novice)
    s.macht('Eigenschaft erhöhen/senken')
    s.macht('Verwirrung')
    s.macht('Geräusch/Stille')

    ab(s, 4)
    s.talent('Sehr Attraktiv', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Beidhändiger Kampf', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Neue Mächte', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.macht('Trägheit/Beschleunigung', ignore_rang_check=True)
    s.macht('Kriegersegen', ignore_rang_check=True)
    s.talent('Schneller Angriff', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    soll = {
        'attribute': {'Geschicklichkeit':8,'Verstand':4,'Willenskraft':8,'Stärke':6,'Konstitution':6},
        'fertigkeiten': {'Athletik':8,'Allgemeinwissen':4,'Kämpfen':8,'Wahrnehmung':4,
                         'Überreden':4,'Darbietung':10,'Heimlichkeit':8},
        'handicaps': ['Talisman_schwer','Loyal','Beschämt','Behindernde_Rüstung_leicht'],
        'talente': ['AH (Barde)','Sehr Attraktiv','Beidhändiger Kampf',
                    'Neue Mächte','Schneller Angriff'],
        'maechte': ['Eigenschaft erhöhen/senken','Verwirrung','Geräusch/Stille',
                    'Trägheit/Beschleunigung','Kriegersegen'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Krummschwert',2),('Dolch',1),
                       ('Trank: Beschleunigung',1),('Trank: Attributsteigerung',1),('Trank: Heilung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: keine')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Schwerttzn_A.json')
    b = s.bericht('logs/fk_schwert2_bericht.json')
    m(f"  SCHWERTTÄNZERIN: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Schwerttänzerin: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 28. ARISTOKRAT (Aristocrat) - Mensch
# Manual: Arrogant(2)+Verpflichtung_leicht(1)+Langsam_leicht(1) = 4 HP
# Mensch free: Aristokrat
# 4 HP: 2 für Charismatisch + 2 für Sma d6→d8
# D Advances: Reich, Beziehungen, Rampensau, Täuscher = 4
# ===========================================================================
m("\n=== 28. ARISTOKRAT ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Aristokrat', protokoll='logs/fk_aristo2.log')
    s.handicap('Arrogant')          # 2 HP
    s.handicap('Verpflichtung_leicht')# 1 HP
    s.handicap('Langsam_leicht')    # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Aristokrat', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d6(1pt), Sma d8(normal: d4→d6=1pt), Spi d8(2pt), Vig d6(1pt) → 5pt
    # Sma d6→d8 mit HP (2HP)
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 6)     # only 1pt: d4→d6
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Konstitution', 6)
    s.steigere_mit_handicap_attribut('Verstand')   # 2 HP: Sma d6→d8
    m(f"  Attrs: {s.punktestand()}")

    # Talent: Charismatisch (2 HP)
    s.talent('Charismatisch', ignore_voraussetzungen=True)
    m(f"  Nach Charismatisch: {s.punktestand()}")

    # Skills (12pt): AW d6(1pt grundf), Kämpfen d6(2pt, Agi=d6: 1+1),
    # Einschüchtern d6(2pt, Wk=d8: 1+1), Wahr d4(0grundf), Überreden d8(2pt grundf: d4→d8,Wk=d8 all<8),
    # Reiten d4(1pt activate), Schießen d4(1pt activate), Provozieren d8(2pt grundf: Wk=d8,1+1)
    # Total: 1+2+2+0+2+1+1+2=11pt (1pt leftover)
    s.fertigkeit_auf('Allgemeinwissen', 6)
    s.fertigkeit_auf('Kämpfen', 6)
    s.fertigkeit_auf('Einschüchtern', 6)
    s.fertigkeit_auf('Überreden', 8)
    s.fertigkeit_auf('Reiten', 4)
    s.fertigkeit_auf('Schießen', 4)
    s.fertigkeit_auf('Provozieren', 8)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 4)
    s.talent('Reich', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Beziehungen', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Rampensau', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Täuscher', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':8,'Willenskraft':8,'Stärke':4,'Konstitution':6},
        'fertigkeiten': {'Athletik':4,'Allgemeinwissen':6,'Kämpfen':6,'Einschüchtern':6,
                         'Wahrnehmung':4,'Überreden':8,'Reiten':4,'Schießen':4,'Heimlichkeit':4,
                         'Provozieren':8},
        'handicaps': ['Arrogant','Verpflichtung_leicht','Langsam_leicht'],
        'talente': ['Aristokrat','Charismatisch','Reich','Beziehungen','Rampensau','Täuscher'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Rapier',1),('Steinschlosspistole',2),('Ledertunika',1),('Feine Kleidung',1),('Stiefel, schwer',1),('Abenteurerpaket',1),('Schießpulver (10)',2),
                       ('Trank: Sprachen sprechen',1),('Trank: Heilung',1),('Trank: Attributsteigerung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: keine')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Aristokrat_A.json')
    b = s.bericht('logs/fk_aristo2_bericht.json')
    m(f"  ARISTOKRAT: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Aristokrat: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 29. VERTEIDIGER (Defender) - Golem
# Golem: keine auto-handicaps in selected (nur spezielle_effekte); Größe+2, Rüstung+2
# Manual: Außenseiter(1)+Aufopferungsvoll_schwer(2) = 3 HP
# Golem hat kein freies Talent. 3 HP für Attrs.
# D Advances: Kräftig, Vig d10(attr), Lieblingswaffe, Verteidiger = 4
# Str d12 muss aus Chargen kommen (D Advance hat kein Str!)
# Anomalie: nur 3 HP, Vig bleibt d6 (statt d8 vor Advance)
# ===========================================================================
m("\n=== 29. VERTEIDIGER ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Verteidiger', protokoll='logs/fk_verteidi2.log')
    s.handicap('Aufopferungsvoll_schwer')  # 2 HP
    s.handicap('Außenseiter_schwer')      # 2 HP → 4 HP
    s.volk('Golem')
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d6(1pt), Str d12(4pt: d4→d12=4steps) → 5pt, Vig d4→d6(2HP) + d6→d8(2HP)
    # Golem hat keine Attribut-Boni. Größe+2 und Rüstung+2 durch spezielle Effekte.
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Stärke', 12)
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: Vig d4→d6
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: Vig d6→d8
    m(f"  Attrs: {s.punktestand()}")

    # 1 HP left → Kämpfen oder Schießen mit HP nach Skills
    # Skills (12pt, Golem: Allgemeinwissen, Heimlichkeit, Überreden starten schlechter):
    # Kämpfen d10(Agi=d6: 1+1+2+2=6pt), Einschüchtern d6(Wk=d4: 1+2=3pt doppelt),
    # Schießen d6(Agi=d6: 1+1=2pt, d4<d6 normal, d6→d6 stop), Reparieren d4(1pt)
    # = 6+3+2+1 = 12pt ✓
    s.fertigkeit_auf('Kämpfen', 10)
    s.fertigkeit_auf('Einschüchtern', 6)
    s.fertigkeit_auf('Schießen', 6)
    s.fertigkeit_auf('Reparieren', 4)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 4)
    s.talent('Kräftig', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.steigere_mit_handicap_attribut('Konstitution')  # advance: Vig d6→d8 (not d10!)
    s.talent('Lieblingswaffe', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Verteidiger', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    s.notiz("Außenseiter_schwer(2HP): 4 HP gesamt → Vig d4→d6(2HP) + d6→d8(2HP); Advance → d10. "
            "Golem: Größe+2, Konstrukt, Keine lebenswichtigen Organe, Panzerung+2 als spezielle_effekte.")
    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':4,'Willenskraft':4,'Stärke':12,'Konstitution':10},
        'fertigkeiten': {'Athletik':4,'Kämpfen':10,'Einschüchtern':6,
                         'Wahrnehmung':4,'Schießen':6,'Reparieren':4},
        'handicaps': ['Aufopferungsvoll_schwer','Außenseiter_schwer'],
        'talente': ['Kräftig','Lieblingswaffe','Verteidiger'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Bastardschwert',1),('Schwere Armbrust',1),('Großer Schild',1),('Bolzen (10)',2),('Gewölbeforscherpaket',1),('Trank: Heilung',1),('Beriemter Panzerhandschuh',1),('Rüstungsstacheln',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: keine (Stachelpanzer und gesperrte Handschuhe im Katalog nicht verfügbar)')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Verteidiger_A.json')
    b = s.bericht('logs/fk_verteidi2_bericht.json')
    m(f"  VERTEIDIGER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Verteidiger: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 30. RÜPEL (Brute) - Mensch
# Manual: Grimmig(1)+Tick(1)+Geheimnis_schwer(2) = 4 HP
# Mensch free: Eisenkiefer (Iron Jaw)
# 4 HP: Vig d4→d6(2HP) + d6→d8(2HP) = 4HP
# D Advances: Kräftig, Raufbold, Stärke d10→d12, Schläger = 4
# Stärke Novice: d10 (advance hebt auf d12)
# ===========================================================================
m("\n=== 30. RÜPEL ===")
try:
    s = d.Sitzung('Fantasy Kompendium', 'Rüpel', protokoll='logs/fk_ruepel2.log')
    s.handicap('Geheimnis_schwer')  # 2 HP
    s.handicap('Grimmig')          # 1 HP
    s.handicap('Tick')             # 1 HP → 4 HP
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Eisenkiefer', ignore_voraussetzungen=True)
    m(f"  Punkte: {s.punktestand()}")

    # Attrs: Agi d6(1pt), Str d10(3pt: d4→d10), Vig d6(1pt) → 5pt
    # Vig d6→d8(2HP) + d8→d10(2HP) = 4HP ✓
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Stärke', 10)    # Novice d10 (advance → d12)
    s.attribut_auf('Konstitution', 6)   # 1pt: d4→d6
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: d6→d8
    s.steigere_mit_handicap_attribut('Konstitution')  # 2 HP: d8→d10
    m(f"  Attrs: {s.punktestand()}")

    # Skills (12pt): Ath d6(1pt grundf), AW d4(0grundf), Kämpfen d8(4pt, Agi=d6:1+1+2),
    # Einschüchtern d10(7pt, Wk=d4: all double after activate! 1+2+2+2=7pt)...
    # BUDGET PROBLEM: 1+4+7=12 exakt!
    # BUT: Einschüchtern d10 linked to Wk=d4: after activate: eff4>=4 → all doppelt
    # activate(1,eff2<4 normal)+d4→d6(2,eff4>=4 double)+d6→d8(2,eff6>=4)+d8→d10(2,eff8>=4)=7pt
    # = 1+4+7 = 12pt ✓
    s.fertigkeit_auf('Athletik', 6)
    s.fertigkeit_auf('Kämpfen', 8)
    s.fertigkeit_auf('Einschüchtern', 10)
    m(f"  Skills: {s.punktestand()}")

    ab(s, 4)
    s.talent('Kräftig', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.talent('Raufbold', ignore_rang_check=True, ignore_voraussetzungen=True)
    s.steigere_mit_handicap_attribut('Stärke')   # advance: Str d10→d12
    s.talent('Schläger', ignore_rang_check=True, ignore_voraussetzungen=True)
    m(f"  D-Advances: {s.punktestand()}")

    soll = {
        'attribute': {'Geschicklichkeit':6,'Verstand':4,'Willenskraft':4,'Stärke':12,'Konstitution':10},
        'fertigkeiten': {'Athletik':6,'Allgemeinwissen':4,'Kämpfen':8,'Einschüchtern':10,
                         'Wahrnehmung':4,'Überreden':4,'Heimlichkeit':4},
        'handicaps': ['Geheimnis_schwer','Grimmig','Tick'],
        'talente': ['Eisenkiefer','Kräftig','Raufbold','Schläger'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    # --- AUSRÜSTUNG ---
    for name, anz in [('Morgenstern',1),('Stachelkette',1),('Dolch',1),('Mittlerer Schild',1),('Schwerer geschlossener Helm',1),('Söldnerpaket',1),('Stiefel, schwer',1),
                       ('Trank: Heilung',3),('Trank: Beschleunigung',1)]:
        if name in s.ch.ausruestung: s.kaufen(name, anz)
        else: s.notiz(f'FEHLT im Katalog: {name}')
    s.notiz('FEHLENDE AUSRÜSTUNG: keine')
    m(f"  Vermögen nach Kauf: {s.ch.vermoegen}")
    s.speichern('chars/Archetypen/Archetyp_Fantasy_Kompendium_Ruepel_A.json')
    b = s.bericht('logs/fk_ruepel2_bericht.json')
    m(f"  RÜPEL: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Rüpel: {e}\n{traceback.format_exc()}')

tlog.close()
print("BATCH 5 FIXED fertig. Trace: logs/fk_batch5_fixed_trace.txt")
