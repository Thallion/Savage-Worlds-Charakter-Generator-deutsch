"""SciFi Kompendium Archetypen – Batch 2 v2 (Mensch-Volk + Skrupellos_schwer)"""
import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

def abschliessen(s, n):
    s.ch.char_gen_completed = True
    for _ in range(n): increase_aufstiege(s.ch)

def ok_check(r):
    if isinstance(r, list): return not r or r[-1].get('ok', True)
    if isinstance(r, dict): return r.get('ok', True)
    return True

tlog = open('logs/scifi_batch2_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

def skills_setzen(s, skill_liste):
    for f, z in skill_liste:
        r = s.fertigkeit_auf(f, z)
        if not ok_check(r): s.notiz(f'SKILL FEHLER {f}: {r}')

def advance_attr(s, name):
    r = s.attribut(name, nur_freie_punkte=False)
    m(f"  Advance {name}: ok={ok_check(r)}")

# ═══════════════════════════════════════════════════════
# 7. INFLUENCER  Pace 6 Parry 4 Toughness 7(2)
# HP: Große Klappe(1)+Neugierig(2)+Angewohnheit_leicht(1) = 4HP
# Mensch: Attraktiv free → Charismatisch 2HP + 2×Fertigkeit 1HP+1HP = 4HP ✓
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Influencer', protokoll='logs/scifi_influencer.log')
    s.handicap('Große Klappe')
    s.handicap('Neugierig')
    s.handicap('Angewohnheit_leicht')
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Attraktiv', ignore_voraussetzungen=True)  # free
    s.talent('Charismatisch')                                                   # 2HP
    m(f"  Talente: HC={s.ch.verbleibende_handicap_punkte}")
    s.attribut_auf('Verstand', 8)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Konstitution', 6)
    m(f"  Attrs: {s.punktestand()}")
    # Skills 12pts: Darbietung d8(3)+Überreden d8(2)+Provozieren d6(2)+Recherche d6(2)+Heim d6(1)+Pilot d4(1) = 11 → 1 spare
    # +2HP Fertigkeitsschritte → Schießen d4(1) + Elektronik d4(1)
    skills_setzen(s, [('Darbietung',8),('Überreden',8),('Provozieren',6),
                      ('Recherche',6),('Heimlichkeit',6),('Pilot',4)])
    s.steigere_mit_handicap_fertigkeit('Schießen')    # 1HP
    s.steigere_mit_handicap_fertigkeit('Elektronik')  # 1HP
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 4)
    for t in ['Beziehungen','Berühmt','Rampensau','Täuscher']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    for item in [('Kevlarweste',1),('Springmesser',1),
                 ('Taschencomputer',1),('Kleidung, formell',1),
                 ('Drohne, Kommerziell',1)]:
        s.kaufen(*item)
    s.notiz('MISSING: Leichte Schusswaffe (Slugthrower)')
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Influencer_A.json')
    b = s.bericht('logs/scifi_influencer_bericht.json')
    m(f"Influencer FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Influencer CRASH: {e}\n{traceback.format_exc()}')

# ═══════════════════════════════════════════════════════
# 8. MERCENARY  Pace 6 Parry 6 Toughness 11(4)
# HP: Kybernetische Nebenwirkungen(2)+Rebellisch(1)+Gesucht_leicht(1) = 4HP
# Mensch: Gut Ausgerüstet free → Stärke d4→d6 2HP + 2×Fertigkeit 1HP+1HP = 4HP ✓
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Mercenary', protokoll='logs/scifi_mercenary.log')
    s.handicap('Kybernetische Nebenwirkungen')
    s.handicap('Rebellisch')
    s.handicap('Gesucht_leicht')
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Gut Ausgerüstet', ignore_voraussetzungen=True)  # free
    m(f"  Talent: HC={s.ch.verbleibende_handicap_punkte}")
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Konstitution', 6)
    s.steigere_mit_handicap_attribut('Stärke')   # d4→d6 (2HP)
    m(f"  Attrs: {s.punktestand()}")
    # Skills 12pts: Athle d6(1)+Fahren d6(2)+Kämpfen d8(3)+Einsch d6(2)+Wahr d6(1)+Schießen d8(3) = 12
    skills_setzen(s, [('Athletik',6),('Fahren',6),('Kämpfen',8),
                      ('Einschüchtern',6),('Wahrnehmung',6),('Schießen',8)])
    # 2HP: Allgemeinwissen d6(Grundf, d4→d6=1HP) + Elektronik d4 aktivieren(1HP)
    s.steigere_mit_handicap_fertigkeit('Allgemeinwissen')  # 1HP: d4→d6
    s.steigere_mit_handicap_fertigkeit('Elektronik')       # 1HP: activate d4
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 4)
    advance_attr(s, 'Konstitution')   # d6→d8
    advance_attr(s, 'Stärke')         # d6→d8
    for t in ['Schnell','Gassenwissen']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    for item in [('Infanteriekampfanzug',1),('Molekularschwert',1),('Komlink',1),('Taschencomputer',1)]:
        s.kaufen(*item)
    for cw in [('Cyberware: Adrenalindrüse',1),('Cyberware: Verbesserte Sicht',1)]:
        s.kaufen(*cw)
    s.notiz('MISSING: Automatisches Schrotgewehr, Muskelgewebe-Cyberware')
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Mercenary_A.json')
    b = s.bericht('logs/scifi_mercenary_bericht.json')
    m(f"Mercenary FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Mercenary CRASH: {e}\n{traceback.format_exc()}')

# ═══════════════════════════════════════════════════════
# 9. ROUGHNECK (Draken)  Pace 5 Parry 5 Toughness 12(4)
# Unverändert – Draken-Volk, kein Mensch
# HP: Einarmig(2)+Impulsiv(2) = 4HP
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Roughneck', protokoll='logs/scifi_roughneck.log')
    s.handicap('Einarmig')
    s.handicap('Impulsiv')
    s.volk('Draken')
    m(f"  Draken HC: {list(s.ch.selected_handicaps)}")
    s.talent('Gut Ausgerüstet')   # free base (vor Attrs)
    m(f"  Talent: HC={s.ch.verbleibende_handicap_punkte}")
    s.attribut_auf('Verstand', 8)
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Stärke', 8)    # Draken starts d6, costs 1pt → d8
    s.steigere_mit_handicap_attribut('Konstitution')   # d4→d6 (2HP)
    s.steigere_mit_handicap_attribut('Konstitution')   # d6→d8 (2HP)
    m(f"  Attrs: {s.punktestand()}")
    skills_setzen(s, [('Fahren',6),('Elektronik',6),('Kämpfen',6),
                      ('Einschüchtern',6),('Reparieren',8)])
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 4)
    for t in ['Schläger','Reparaturgenie','Rohling']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    s.notiz('ADVANCE: Cyber Installs – kein Talent-Key, via Ausrüstung modelliert')
    s.notiz('ANCESTRY BUG: Low Light Vision nicht im deutschen Draken implementiert')
    for item in [('Infanteriekampfanzug',1),('Rucksack',1),('Taschenlampe (10\" Strahl)',1),
                 ('Taschencomputer',1),('Werkzeugkoffer',1),('Batterie, Universal-',1)]:
        s.kaufen(*item)
    for cw in [('Cyberware: Ersatzgliedmaße',1),('Cyberware: Klauen',1)]:
        s.kaufen(*cw)
    s.notiz('MISSING: Plasmapistole, Schweißbrille')
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Roughneck_A.json')
    b = s.bericht('logs/scifi_roughneck_bericht.json')
    m(f"Roughneck FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Roughneck CRASH: {e}\n{traceback.format_exc()}')

# ═══════════════════════════════════════════════════════
# 10. MYSTIC (Floraner)  Pace 5 Parry 4 Toughness 6(0)
# Unverändert – Floraner-Volk, kein Mensch
# HP: Vorsichtig(1)+Heldenhaft(2)+Langsam_leicht(1) = 4HP
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Mystic', protokoll='logs/scifi_mystic.log')
    s.handicap('Heldenhaft')
    s.handicap('Vorsichtig')
    s.handicap('Langsam_leicht')
    s.volk('Floraner')
    m(f"  Floraner Talente: {list(s.ch.selected_talente)}")
    s.talent('AH (Mystiker)', ignore_voraussetzungen=True)   # free base (vor Attrs)
    m(f"  Talent: HC={s.ch.verbleibende_handicap_punkte}")
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Stärke', 6)
    s.steigere_mit_handicap_attribut('Konstitution')   # d4→d6 (2HP)
    s.steigere_mit_handicap_attribut('Konstitution')   # d6→d8 (2HP) – Vigor d8 Advance pre-consumed
    m(f"  Attrs: {s.punktestand()}")
    skills_setzen(s, [('Fokus',8),('Überreden',8),('Provozieren',6),
                      ('Wahrnehmung',6),('Geisteswissenschaften',6),
                      ('Okkultismus',4),('Schießen',6)])
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 4)
    for t in ['Elan','Neue Mächte']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    for macht in ['Eigenschaft erhöhen/senken','Empathie','Objekt auslesen','Linderung','Kriegersegen']:
        r = s.macht(macht, ignore_rang_check=True)
        m(f"  Macht {macht}: ok={ok_check(r)}")
    for item in [('Batterie, Universal-',2),('Taschencomputer',1)]:
        s.kaufen(*item)
    s.notiz('MISSING: Plasmagewehr')
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Mystic_A.json')
    b = s.bericht('logs/scifi_mystic_bericht.json')
    m(f"Mystic FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Mystic CRASH: {e}\n{traceback.format_exc()}')

# ═══════════════════════════════════════════════════════
# 11. MORPHER (Wechselbälger)  Pace 6 Parry 4 Toughness 6(0)
# Unverändert – Wechselbälger-Volk, kein Mensch
# HP: Große Klappe(1)+Loyal(1)+Beschämt(1)+Pechvogel(leicht)(1) = 4HP
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Morpher', protokoll='logs/scifi_morpher.log')
    s.handicap('Große Klappe')
    s.handicap('Loyal')
    s.handicap('Beschämt')
    s.handicap('Pechvogel (leicht)')
    s.volk('Wechselbälger')
    m(f"  Wechselbälger HC: {list(s.ch.selected_handicaps)}")
    s.talent('AH (Wandler)', ignore_voraussetzungen=True)   # free base (vor Attrs)
    m(f"  Talent: HC={s.ch.verbleibende_handicap_punkte}")
    s.attribut_auf('Verstand', 8)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Geschicklichkeit', 6)
    s.steigere_mit_handicap_attribut('Konstitution')   # d4→d6 (2HP)
    s.steigere_mit_handicap_attribut('Konstitution')   # d6→d8 (2HP) – Vigor d8 advance pre-consumed
    m(f"  Attrs: {s.punktestand()}")
    skills_setzen(s, [('Fokus',8),('Überreden',8),('Heimlichkeit',8),
                      ('Provozieren',8),('Wahrnehmung',6),('Elektronik',4)])
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 4)
    for t in ['Erniedrigen','Neue Mächte','Täuscher']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    for macht in ['Verkleiden','Schutz vor Naturgewalten','Heilung','Gestaltwandeln']:
        r = s.macht(macht, ignore_rang_check=True)
        m(f"  Macht {macht}: ok={ok_check(r)}")
    for item in [('Komlink',1),('Taschencomputer',1)]:
        s.kaufen(*item)
    s.notiz('MISSING: Laserpistole, Nanowear, Elektronisches Schloss')
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Morpher_A.json')
    b = s.bericht('logs/scifi_morpher_bericht.json')
    m(f"Morpher FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Morpher CRASH: {e}\n{traceback.format_exc()}')

# ═══════════════════════════════════════════════════════
# 12. SPACER  Pace 6 Parry 6 Toughness 9(4)
# HP: Arrogant(2)+Skrupellos_schwer(2) = 4HP  ← NEU: Skrupellos_schwer statt Skrupellos!
# Mensch (Stand-in, kein passendes Alien-Volk): Ass am Steuer free
# HP: Konstitution d4→d6 2HP + Stärke d4→d6 2HP = 4HP ✓
# Stärke d6 UND Konstitution d6 jetzt beide erreichbar!
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Spacer', protokoll='logs/scifi_spacer.log')
    s.handicap('Arrogant')
    s.handicap('Skrupellos_schwer')   # NEU: Ruthless Major jetzt korrekt
    s.notiz('ANCESTRY MISSING: kein passendes Volk – Biss/Klauen, Nachtsicht, Kann-nicht-schwimmen, Blutrünstig, Ruppig fehlen')
    s.notiz('Mensch als Stand-in Volk (kein passendes Alien-Volk im deutschen Setting)')
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Ass am Steuer', ignore_voraussetzungen=True)  # free
    m(f"  Talent: HC={s.ch.verbleibende_handicap_punkte}")
    s.attribut_auf('Geschicklichkeit', 10)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 6)
    s.steigere_mit_handicap_attribut('Konstitution')   # d4→d6 (2HP)
    s.steigere_mit_handicap_attribut('Stärke')         # d4→d6 (2HP)  ← jetzt möglich!
    m(f"  Attrs: {s.punktestand()}")
    # Skills (Advances pre-consumed: Kämpfen d8, Heimlichkeit d8, Elektronik d6, Schießen d6)
    skills_setzen(s, [('Pilot',10),('Kämpfen',8),('Heimlichkeit',8),
                      ('Einschüchtern',4),('Wahrnehmung',6),
                      ('Elektronik',6),('Schießen',6)])
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 4)
    for t in ['Bedrohlich','Ausweichen']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    for item in [('Infanteriekampfanzug',1),('Molekularmesser',1),
                 ('Laser-/Rotpunktvisier',1),('Komlink',1),('Batterie, Universal-',1)]:
        s.kaufen(*item)
    s.notiz('MISSING: Schwere Blasterpistole, Raumanzug, Klebeflicken×3')
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Spacer_A.json')
    b = s.bericht('logs/scifi_spacer_bericht.json')
    m(f"Spacer FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Spacer CRASH: {e}\n{traceback.format_exc()}')

tlog.close()
print("BATCH2 DONE")
