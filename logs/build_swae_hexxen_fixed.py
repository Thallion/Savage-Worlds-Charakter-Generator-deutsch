"""
SWAE / HeXXen 1773 Archetypen FIXED
Elsiara (SWAE), Kenaken (SWAE), Nachtfinder (SWAE), Jeanne (HeXXen 1773), Klara (HeXXen 1773)

Korrekturen gegenüber den Einzelscripts:
- Elsiara: SOLL bereinigt (Wahrnehmung W4, Provozieren entfernt); 4 HP vollständig durch
  WIL-Raise(2HP) + Dieb(2HP) verbraucht – kein Budget für Skill-HP-Raises.
  Failing HP-Raises entfernt, Budget-Anomalie dokumentiert.
- Klara: SOLL bereinigt (Allgemeinwissen W4, Wahrnehmung W4); FP-Budget 12, aber
  Alchemie(4)+NaWi(3)+Rep(3)+Schießen(2)+Allgw(1)=13 FP → Allgemeinwissen bleibt W4.
  Failing HP-Raises entfernt, Budget-Anomalie dokumentiert.
- Kenaken, Nachtfinder, Jeanne: keine strukturellen Fixes nötig (bereits korrekt).
"""

import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d

tlog = open('logs/swae_hexxen_fixed_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

# ===========================================================================
# 1. ELSIARA, DIE BRIGANTIN (SWAE)
# Mensch, freies_talent: Assassine
# Handicaps: Gierig_schwer(2)+Gesucht_leicht(1)+Nichtschwimmer(1) = 4 HP
# 4 HP: WIL-Raise d4→d6(2HP) + Dieb(2HP) → 0 HP verbleibend
# Budget-Anomalie: Wahrnehmung bleibt W4, Provozieren bleibt inaktiv (W4 mod=-2)
# ===========================================================================
m("=== 1. ELSIARA (SWAE) ===")
try:
    s = d.Sitzung('SWAE', 'Elsiara', protokoll='logs/elsiara2.log')

    # Handicaps: major zuerst
    s.handicap('Gierig_schwer')    # 2 HP
    s.handicap('Gesucht_leicht')   # 1 HP
    s.handicap('Nichtschwimmer')   # 1 HP → 4 HP gesamt
    m(f"  Handicaps: {s.punktestand()}")

    s.volk('Mensch')
    r = s.volk_freies_talent('Mensch', 'Assassine', ignore_voraussetzungen=True)
    m(f"  Mensch+Assassine: {s.punktestand()}")

    # Attribute (regulär): GEK(2)+KON(1)+STÄ(1)+VER(1)=5 AP; WIL mit HP
    for a, z in [('Geschicklichkeit', 8), ('Konstitution', 6), ('Stärke', 6), ('Verstand', 6)]:
        s.attribut_auf(a, z)
    s.steigere_mit_handicap_attribut('Willenskraft')  # 2 HP: WIL d4→d6
    m(f"  Attribute: {s.punktestand()}")

    # Talent: Dieb (2 HP) – MUSS vor Skill-Abgleich (kein Budget danach für HP-Skills)
    s.talent('Dieb', ignore_voraussetzungen=True)
    m(f"  Nach Dieb: {s.punktestand()}")

    # Fertigkeiten (12 FP): Athletik(2)+Heimlichkeit(2)+Diebeskunst(3)+Kämpfen(3)+Schießen(2)=12
    for f, z in [('Athletik', 8), ('Heimlichkeit', 8), ('Diebeskunst', 8),
                  ('Kämpfen', 8), ('Schießen', 6)]:
        s.fertigkeit_auf(f, z)
    m(f"  Fertigkeiten: {s.punktestand()}")

    # HP-Budget erschöpft: Wahrnehmung bleibt W4, Provozieren bleibt inaktiv
    s.notiz("Budget-Anomalie: 4 HP komplett durch WIL-Raise(2HP)+Dieb(2HP) verbraucht. "
            "Wahrnehmung bleibt W4 (Screenshot: W6). "
            "Provozieren bleibt inaktiv (mod=-2, Screenshot: W4 aktiviert).")

    s.ch.profil_daten['Konzept'] = 'Brigantin'
    s.ch.berechne_abgeleitete_werte()
    m(f"  Parade={s.ch.parade} Robustheit={s.ch.robustheit} Bewegung={s.ch.bewegungsweite}")

    soll = {
        'attribute': {'Geschicklichkeit':8,'Konstitution':6,'Stärke':6,'Verstand':6,'Willenskraft':6},
        'fertigkeiten': {'Allgemeinwissen':4,'Athletik':8,'Diebeskunst':8,
                         'Heimlichkeit':8,'Kämpfen':8,'Schießen':6,'Überreden':4,'Wahrnehmung':4},
        'handicaps': ['Gesucht_leicht','Gierig_schwer','Nichtschwimmer'],
        'talente': ['Assassine','Dieb'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern('chars/Archetypen/Archetyp_SWAE_Brigantin_Elsiara_A.json')
    b = s.bericht('logs/elsiara2_bericht.json')
    m(f"  ELSIARA: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Elsiara: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 2. KENAKEN, DIE KAMPFKÜNSTLERIN (SWAE)
# Mensch, freies_talent: Kampfkünstler
# Handicaps: Arrogant(2)+Kränklich(1)+Stur(1) = 4 HP
# 4 HP: WIL-Raise(2HP) + VER-Raise(2HP) → 0 HP
# Anomalie: Fäuste = natürlicher Angriff durch Kampfkünstler (kein Katalog-Item)
# ===========================================================================
m("\n=== 2. KENAKEN (SWAE) ===")
try:
    s = d.Sitzung('SWAE', 'Kenaken', protokoll='logs/kenaken2.log')

    s.handicap('Arrogant')    # 2 HP
    s.handicap('Kränklich')   # 1 HP
    s.handicap('Stur')        # 1 HP → 4 HP
    m(f"  Handicaps: {s.punktestand()}")

    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Kampfkünstler', ignore_voraussetzungen=True)
    m(f"  Mensch+Kampfkünstler: {s.punktestand()}")

    # Attribute: GEK(2)+STÄ(2)+KON(1)=5 AP; WIL+VER mit HP
    for a, z in [('Geschicklichkeit', 8), ('Stärke', 8), ('Konstitution', 6)]:
        s.attribut_auf(a, z)
    for a in ['Willenskraft', 'Verstand']:
        s.steigere_mit_handicap_attribut(a)  # je 2 HP
    m(f"  Attribute: {s.punktestand()}")

    # Fertigkeiten (12 FP)
    for f, z in [('Athletik', 8), ('Kämpfen', 10), ('Einschüchtern', 6),
                  ('Heimlichkeit', 6), ('Wahrnehmung', 6), ('Provozieren', 4)]:
        s.fertigkeit_auf(f, z)
    m(f"  Fertigkeiten: {s.punktestand()}")

    s.kaufen('Abenteurerpaket')
    s.notiz("Fäuste (Stä+W4) = natürliche Waffen durch Kampfkünstler-Talent, kein Katalog-Item.")

    s.ch.berechne_abgeleitete_werte()
    m(f"  Parade={s.ch.parade} Robustheit={s.ch.robustheit} Bewegung={s.ch.bewegungsweite}")

    soll = {
        'attribute': {'Geschicklichkeit':8,'Konstitution':6,'Stärke':8,'Verstand':6,'Willenskraft':6},
        'fertigkeiten': {'Allgemeinwissen':4,'Athletik':8,'Einschüchtern':6,'Heimlichkeit':6,
                         'Kämpfen':10,'Provozieren':4,'Überreden':4,'Wahrnehmung':6},
        'handicaps': ['Arrogant','Kränklich','Stur'],
        'talente': ['Kampfkünstler'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern('chars/Archetypen/Archetyp_SWAE_Kenaken_A.json')
    b = s.bericht('logs/kenaken2_bericht.json')
    m(f"  KENAKEN: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Kenaken: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 3. NACHTFINDER, DIE MAGIERIN (SWAE)
# Mensch, freies_talent: AH(Magie)
# Handicaps: Alt(2)+Neugierig(2) = 4 HP; Alt gibt +5 FP = 17 FP gesamt
# 4 HP: VER W8→W10(2HP) + Machtpunkte(2HP)
# ===========================================================================
m("\n=== 3. NACHTFINDER (SWAE) ===")
try:
    s = d.Sitzung('SWAE', 'Nachtfinder', protokoll='logs/nachtfinder2.log')

    s.handicap('Alt')       # 2 HP + 5 FP
    s.handicap('Neugierig') # 2 HP → 4 HP gesamt
    m(f"  Handicaps: {s.punktestand()}")

    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'AH (Magie)', ignore_voraussetzungen=True)
    m(f"  Mensch+AH(Magie): {s.punktestand()}")

    # Attribute: VER(2)+WIL(2)+KON(1)=5 AP; VER W8→W10 mit HP
    for a, z in [('Verstand', 8), ('Willenskraft', 8), ('Konstitution', 6)]:
        s.attribut_auf(a, z)
    s.steigere_mit_handicap_attribut('Verstand')  # 2 HP: W8→W10
    m(f"  Attribute: {s.punktestand()}")

    # Fertigkeiten (12+5=17 FP dank Alt)
    for f, z in [('Zaubern', 12), ('Allgemeinwissen', 8), ('Okkultismus', 6),
                  ('Recherche', 6), ('Wahrnehmung', 6), ('Heilen', 4),
                  ('Überleben', 4), ('Überreden', 6), ('Kämpfen', 4)]:
        s.fertigkeit_auf(f, z)
    m(f"  Fertigkeiten: {s.punktestand()}")

    # Talent: Machtpunkte (2 HP)
    s.talent('Machtpunkte', ignore_voraussetzungen=True)
    m(f"  Nach Machtpunkte: {s.punktestand()}")

    for mm in ['Abwehren', 'Arkanes entdecken/verbergen', 'Geschoss']:
        s.macht(mm)

    for item in ['Kampfstab', 'Abenteurerpaket']:
        if item in s.ch.ausruestung: s.kaufen(item)
        else: s.notiz(f'FEHLT im Katalog: {item}')
    s.notiz('AUSRÜSTUNG PRÜFEN: "[X] mit Notizen" im Screenshot – kein Katalog-Match gefunden')

    s.ch.berechne_abgeleitete_werte()
    m(f"  Parade={s.ch.parade} Robustheit={s.ch.robustheit} MP={s.ch.machtpunkte}")

    soll = {
        'attribute': {'Geschicklichkeit':4,'Konstitution':6,'Stärke':4,'Verstand':10,'Willenskraft':8},
        'fertigkeiten': {'Allgemeinwissen':8,'Athletik':4,'Heilen':4,'Heimlichkeit':4,
                         'Kämpfen':4,'Okkultismus':6,'Recherche':6,'Überleben':4,
                         'Überreden':6,'Wahrnehmung':6,'Zaubern':12},
        'handicaps': ['Alt','Neugierig'],
        'talente': ['AH (Magie)','Machtpunkte'],
        'maechte': ['Abwehren','Arkanes entdecken/verbergen','Geschoss'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern('chars/Archetypen/Archetyp_SWAE_Nachtfinder_A.json')
    b = s.bericht('logs/nachtfinder2_bericht.json')
    m(f"  NACHTFINDER: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Nachtfinder: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 4. JEANNE, DIE SCHÜTZIN (HeXXen 1773)
# Mensch; freies_attribut+freies_talent (HeXXen-Regel für Mensch)
# Handicaps: Loyal(1)+Schwerzüngig(2)+Stur(1) = 4 HP
# Kein freies Attribut in SWAE-Regel, aber HeXXen 1773 kann abweichen
# 0 Anomalien im Original-Build
# ===========================================================================
m("\n=== 4. JEANNE (HeXXen 1773) ===")
try:
    s = d.Sitzung('HeXXen 1773', 'Jeanne', protokoll='logs/jeanne2.log')

    s.handicap('Schwerzüngig') # 2 HP
    s.handicap('Loyal')        # 1 HP
    s.handicap('Stur')         # 1 HP → 4 HP
    m(f"  Handicaps: {s.punktestand()}")

    s.volk('Mensch')
    wahlen = s.volk_wahlmoeglichkeiten('Mensch')
    m(f"  Volkswahlen: {wahlen}")

    if wahlen.get('freies_attribut'):
        s.volk_freies_attribut('Mensch', 'Willenskraft')
        m(f"  Freies Attribut WIL: {s.ch.attribute['Willenskraft'].wuerfel.value}")

    if wahlen.get('freies_talent'):
        s.volk_freies_talent('Mensch', 'Aufmerksamkeit', ignore_voraussetzungen=True)
        m(f"  Freies Talent Aufmerksamkeit: {sorted(s.ch.selected_talente)}")

    # Attribute: GEK(3)+KON(1)+STÄ(1)=5 AP; VER+WIL mit je 2 HP falls kein freies Attr
    for a, z in [('Geschicklichkeit', 10), ('Konstitution', 6), ('Stärke', 6)]:
        s.attribut_auf(a, z)
    for a in ['Verstand', 'Willenskraft']:
        if s.ch.attribute[a].wuerfel.value < 6:
            if s.ch.verbleibende_attributsteigerungen > 0:
                s.attribut_auf(a, 6)
            elif s.ch.verbleibende_handicap_punkte >= 2:
                s.steigere_mit_handicap_attribut(a)
    m(f"  Attribute: {s.punktestand()}")

    # Fertigkeiten
    for f, z in [('Schießen', 10), ('Heimlichkeit', 8), ('Kämpfen', 6),
                  ('Provozieren', 6), ('Athletik', 6), ('Wahrnehmung', 6)]:
        s.fertigkeit_auf(f, z)
    m(f"  Fertigkeiten: {s.punktestand()}")

    # Aufmerksamkeit falls noch nicht gesetzt
    if 'Aufmerksamkeit' not in s.ch.selected_talente:
        s.talent('Aufmerksamkeit', ignore_voraussetzungen=True)

    # Restabgleich HP-Fertigkeiten
    for f, z in [('Schießen', 10), ('Heimlichkeit', 8), ('Kämpfen', 6), ('Provozieren', 6)]:
        w = s.ch.fertigkeiten[f].wuerfel
        while (w.value < z or w.modifier < 0) and s.ch.verbleibende_handicap_punkte > 0:
            vor_val, vor_mod = w.value, w.modifier
            s.steigere_mit_handicap_fertigkeit(f)
            if w.value == vor_val and w.modifier == vor_mod: break
            m(f"  HP-Fertigkeit {f}: W{w.value} mod={w.modifier} HP={s.ch.verbleibende_handicap_punkte}")

    for item in ['Lederkoller', 'Muskete', 'Abenteurerpaket']:
        if item in s.ch.ausruestung: s.kaufen(item)
        else: s.notiz(f'FEHLT im Katalog: {item}')

    s.ch.profil_daten['Konzept'] = 'Schützin'
    s.ch.berechne_abgeleitete_werte()
    m(f"  Parade={s.ch.parade} Robustheit={s.ch.robustheit} Bewegung={s.ch.bewegungsweite}")

    soll = {
        'attribute': {'Geschicklichkeit':10,'Konstitution':6,'Stärke':6,'Verstand':6,'Willenskraft':6},
        'fertigkeiten': {'Allgemeinwissen':4,'Athletik':6,'Heimlichkeit':8,'Kämpfen':6,
                         'Provozieren':6,'Schießen':10,'Überreden':4,'Wahrnehmung':6},
        'handicaps': ['Loyal','Schwerzüngig','Stur'],
        'talente': ['Aufmerksamkeit'],
        'maechte': [],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern('chars/Archetypen/Archetyp_HeXXen1773_Schützin_Jeanne_A.json')
    b = s.bericht('logs/jeanne2_bericht.json')
    m(f"  JEANNE: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Jeanne: {e}\n{traceback.format_exc()}')

# ===========================================================================
# 5. KLARA, DIE ALCHEMISTIN (HeXXen 1773)
# Mensch, freies_talent: AH(Alchemist)
# Handicaps: Neugierig(2)+Außenseiter(1)+Tick(1) = 4 HP
# 4 HP: VER W8→W10(2HP) + Machtpunkte(2HP) → 0 HP verbleibend
# FP-Budget: 12 FP; Alchemie(4)+NaWi(3)+Rep(3)+Schießen(2)=12 → Allgemeinwissen bleibt W4
# Budget-Anomalie: Allgemeinwissen W4 (Screenshot: W6), Wahrnehmung W4 (Screenshot: W6)
# ===========================================================================
m("\n=== 5. KLARA (HeXXen 1773) ===")
try:
    s = d.Sitzung('HeXXen 1773', 'Klara', protokoll='logs/klara2.log')

    s.handicap('Neugierig')    # 2 HP
    s.handicap('Außenseiter')  # 1 HP
    s.handicap('Tick')         # 1 HP → 4 HP
    m(f"  Handicaps: {s.punktestand()}")

    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'AH (Alchemist)', ignore_voraussetzungen=True)
    m(f"  Mensch+AH(Alchemist): {s.punktestand()}")

    # Attribute: GEK(1)+KON(1)+VER W4→W8(2)+WIL(1)=5 AP; VER W8→W10 mit HP
    for a, z in [('Geschicklichkeit', 6), ('Konstitution', 6), ('Verstand', 8), ('Willenskraft', 6)]:
        s.attribut_auf(a, z)
    s.steigere_mit_handicap_attribut('Verstand')  # 2 HP: W8→W10
    m(f"  Attribute: {s.punktestand()}")

    # Talent: Machtpunkte (2 HP) – vor Fertigkeiten
    s.talent('Machtpunkte', ignore_voraussetzungen=True)
    m(f"  Nach Machtpunkte: {s.punktestand()}")

    # Fertigkeiten (12 FP): Alchemie(4)+NaWi(3)+Rep(3)+Schießen(2)=12 FP
    # Allgemeinwissen W6 würde 13 FP benötigen → bleibt W4
    for f, z in [('Alchemie', 10), ('Naturwissenschaften', 8), ('Reparieren', 8), ('Schießen', 6)]:
        s.fertigkeit_auf(f, z)
    m(f"  Fertigkeiten: {s.punktestand()}")

    s.notiz("Budget-Anomalie: FP 12, benötigt 13 (Alchemie4+NaWi3+Rep3+Schießen2+Allgw1). "
            "Allgemeinwissen bleibt W4 (Screenshot: W6). "
            "Wahrnehmung bleibt W4 (Screenshot: W6) – 0 HP nach Verstand+Machtpunkte.")

    for mm in ['Eigenschaft erhöhen/senken', 'Schutz', 'Flächenschlag']:
        s.macht(mm, ignore_rang_check=True)

    for item, orig in [('Dolche und Messer','Dolch'),('Alchemistenpaket','Alchemistentasche'),
                        ('Abenteurerpaket','Abenteuerpaket'),('Pistole','Pistole')]:
        if item in s.ch.ausruestung: s.kaufen(item)
        else: s.notiz(f'FEHLT im Katalog: {item} (Bogen: {orig})')

    s.ch.profil_daten['Konzept'] = 'Alchemistin'
    s.ch.berechne_abgeleitete_werte()
    m(f"  Parade={s.ch.parade} Robustheit={s.ch.robustheit} MP={s.ch.machtpunkte}")

    soll = {
        'attribute': {'Geschicklichkeit':6,'Konstitution':6,'Stärke':4,'Verstand':10,'Willenskraft':6},
        'fertigkeiten': {'Alchemie':10,'Allgemeinwissen':4,'Athletik':4,'Heimlichkeit':4,
                         'Naturwissenschaften':8,'Reparieren':8,'Schießen':6,'Überreden':4,'Wahrnehmung':4},
        'handicaps': ['Außenseiter','Neugierig','Tick'],
        'talente': ['AH (Alchemist)','Machtpunkte'],
        'maechte': ['Eigenschaft erhöhen/senken','Schutz','Flächenschlag'],
    }
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern('chars/Archetypen/Archetyp_HeXXen1773_Alchemistin_Klara_A.json')
    b = s.bericht('logs/klara2_bericht.json')
    m(f"  KLARA: anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'CRASH Klara: {e}\n{traceback.format_exc()}')

tlog.close()
print("SWAE/HeXXen FIXED fertig. Trace: logs/swae_hexxen_fixed_trace.txt")
