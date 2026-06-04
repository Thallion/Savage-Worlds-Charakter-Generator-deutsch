"""SciFi Kompendium Archetypen – Batch 1 v2 (Mensch-Volk + Mystische Kräfte + Skrupellos_schwer)"""
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

tlog = open('logs/scifi_batch1_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

def skills_setzen(s, skill_liste):
    for f, z in skill_liste:
        r = s.fertigkeit_auf(f, z)
        if not ok_check(r): s.notiz(f'SKILL FEHLER {f}: {r}')

def advance_attr(s, name):
    r = s.attribut(name, nur_freie_punkte=False)
    m(f"  Advance {name}: ok={ok_check(r)}")

# REIHENFOLGE (pro Charakter):
# 1. Handicaps (Major zuerst)
# 2. Volk ('Mensch') → gibt 1 freies Starttalent
# 3. volk_freies_talent → erstes Starttalent KOSTENLOS
# 4. Weitere Starttalente via talent() → kosten 2HP
# 5. Attribute (chargen pts, dann HP-Attr-Schritte)
# 6. Fertigkeiten (12pts + ggf. HP-Schritte)
# 7. abschliessen(4) + Advance-Talente

# ═══════════════════════════════════════════════════════
# 1. COMMANDER  Pace 6 Parry 4 Toughness 9(4)
# HP: Heldenhaft(2)+Loyal(1)+Skrupellos(1) = 4HP
# Mensch: Anführer free → Glück 2HP → Willenskraft d6→d8 2HP = 4HP ✓
# Willenskraft d8 jetzt erreicht (vorher nicht möglich)
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Commander', protokoll='logs/scifi_commander.log')
    s.handicap('Heldenhaft')
    s.handicap('Loyal')
    s.handicap('Skrupellos')
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Anführer', ignore_voraussetzungen=True)   # free
    s.talent('Glück', ignore_voraussetzungen=True)                             # 2HP
    m(f"  Talente: HC={s.ch.verbleibende_handicap_punkte}")
    s.attribut_auf('Verstand', 8)
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Konstitution', 6)
    s.steigere_mit_handicap_attribut('Willenskraft')  # d6→d8 (2HP)
    m(f"  Attrs: {s.punktestand()}")
    skills_setzen(s, [('Athletik',6),('Kriegskunst',6),('Elektronik',6),('Kämpfen',4),
                      ('Einschüchtern',6),('Wahrnehmung',6),('Überreden',8),('Pilot',4)])
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 4)
    for t in ['Charismatisch','Selbstlos','Elan','Geborener Anführer']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    for item in [('Körperpanzerung +4',1),('Molekularmesser',1),
                 ('Laserpistole',1),('Waffensperre',1),
                 ('Batterie, Universal-',1),('Persönliche Datenassistenz',1),
                 ('Biolink',1)]:
        s.kaufen(*item)
    s.notiz('Skills Reparieren/Schießen (12pt Budget)')
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Commander_A.json')
    b = s.bericht('logs/scifi_commander_bericht.json')
    m(f"Commander FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Commander CRASH: {e}\n{traceback.format_exc()}')

# ═══════════════════════════════════════════════════════
# 2. PSYKER  Pace 6 Parry 4 Toughness 9(4)
# HP: Übermütig(2)+Misstrauisch_leicht(1)+Dünnhäutig(1) = 4HP
# Mensch: AH(Psioniker) free → Neue Mächte 2HP → Willenskraft d4→d6 2HP = 4HP ✓
# Advance: Willenskraft d6→d8
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Psyker', protokoll='logs/scifi_psyker.log')
    s.handicap('Übermütig')
    s.handicap('Misstrauisch_leicht')
    s.handicap('Dünnhäutig')
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'AH (Psioniker)', ignore_voraussetzungen=True)  # free
    s.talent('Neue Mächte')                                                         # 2HP
    m(f"  Talente: HC={s.ch.verbleibende_handicap_punkte}")
    s.attribut_auf('Verstand', 10)
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Konstitution', 6)
    s.steigere_mit_handicap_attribut('Willenskraft')  # d4→d6 (2HP)
    m(f"  Attrs: {s.punktestand()}")
    skills_setzen(s, [('Psionik',10),('Provozieren',8),('Wahrnehmung',8),
                      ('Überreden',6),('Elektronik',4)])
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 4)
    advance_attr(s, 'Willenskraft')  # d6→d8
    for t in ['Aufmerksamkeit','Machtpunkte','Scannen']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    for macht in ['Gedankenverbindung','Gedankenlesen','Linderung','Sprachen sprechen','Betäuben']:
        r = s.macht(macht, ignore_rang_check=True)
        m(f"  Macht {macht}: ok={ok_check(r)}")
    for item in [('Körperpanzerung +4',1),('Laserpistole',1),('Waffensperre',1),
                 ('Batterie, Universal-',1),('Persönliche Datenassistenz',1),('Scanner',1),
                 ('Biolink',1)]:
        s.kaufen(*item)
    s.notiz('Skills auf 12pt Budget')
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Psyker_A.json')
    b = s.bericht('logs/scifi_psyker_bericht.json')
    m(f"Psyker FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Psyker CRASH: {e}\n{traceback.format_exc()}')

# ═══════════════════════════════════════════════════════
# 3. SURVEYOR  Pace 6 Parry 5 Toughness 9(4)
# HP: Neugierig(2)+Angewohnheit_leicht(1)+Stur(1) = 4HP
# Mensch: Atmosphärische Anpassung free → Bevorzugtes Gelände 2HP → Stärke d4→d6 2HP = 4HP ✓
# Advance: Verstand d6→d8
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Surveyor', protokoll='logs/scifi_surveyor.log')
    s.handicap('Neugierig')
    s.handicap('Angewohnheit_leicht')
    s.handicap('Stur')
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Atmosphärische Anpassung', ignore_voraussetzungen=True)  # free
    s.talent('Bevorzugtes Gelände', ignore_voraussetzungen=True)                              # 2HP
    m(f"  Talente: HC={s.ch.verbleibende_handicap_punkte}")
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Konstitution', 6)
    # FIX Doppelkosten (2026-06-04): Verstand d6→d8 via HP VOR den Skills, damit Wahrnehmung d8
    # (Verstand-Skill) EINFACH statt doppelt kostet. Die 2 HP gingen vorher an Elektronik/Pilot
    # (jetzt als Advance). Stärke bleibt d4 (Bogen d6, dokumentierte Abweichung).
    s.steigere_mit_handicap_attribut('Verstand')   # d6→d8 (2HP) – vermeidet Wahrnehmung-Doppelkosten
    m(f"  Attrs: {s.punktestand()}")
    skills_setzen(s, [('Athletik',8),('Fahren',4),('Kämpfen',6),
                      ('Wahrnehmung',8),('Schießen',6),('Überleben',8)])
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 5)  # 1 Advance mehr: der vorherige Verstand-Advance entfällt (jetzt CharGen),
                        # dafür Stärke d4→d6 (Bogen!) als Advance -> Rang bleibt Fortgeschritten
    # Verstand bereits d8 in CharGen -> kein Verstand-Advance nötig.
    # Elektronik + Pilot via Advance (vorher HP, das jetzt für Verstand gebraucht wird).
    s.fertigkeit_mit_aufstieg('Elektronik', 4)
    s.fertigkeit_mit_aufstieg('Pilot', 4)
    advance_attr(s, 'Stärke')  # d4→d6 (Bogen d6) – behebt die bisherige Stärke-Abweichung
    # Bogen: "Survival d8 & Notice d8" – jetzt bereits CharGen d8 (Verstand d8), 0 Aufstiege
    r = s.fertigkeit_mit_aufstieg('Überleben', 8)
    m(f"  Advance Überleben d8: ok={ok_check(r)}")
    # Naturwissenschaften via D-Advance (0.5 verb verbleibend)
    r = s.fertigkeit_mit_aufstieg('Naturwissenschaften', 4)
    m(f"  Advance Naturwissenschaften d4: ok={ok_check(r)}")
    for t in ['Naturbursche','Kühler Kopf']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    for item in [('Körperpanzerung +4',1),('Batterie, Universal-',1),
                 ('Rucksack',1),('Taschenlampe (10\" Strahl)',1),
                 ('Laserpistole',1),('Waffensperre',1),('Medi-Gel',2),('Scanner',1),
                 ('Tarnanzug',1)]:
        s.kaufen(*item)
    s.notiz('MISSING: Handbeil (kein SciFi-Item im deutschen Setting); Environment Wear → Tarnanzug als Alternative')
    s.notiz('Doppelkosten-Fix: Verstand d8 in CharGen -> Wahrnehmung d8 einfach; Stärke d4->d6 via Advance behebt frühere Abweichung')
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Surveyor_A.json')
    b = s.bericht('logs/scifi_surveyor_bericht.json')
    m(f"Surveyor FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Surveyor CRASH: {e}\n{traceback.format_exc()}')

# ═══════════════════════════════════════════════════════
# 4. AMBASSADOR  Pace 6 Parry 4 Toughness 9(4)
# HP: Vorsichtig(1)+Neugierig(2)+Loyal(1) = 4HP
# Mensch: Mystische Kräfte: Telepath free → auto-Mächte: Betäuben/Empathie/Gedankenlesen/Linderung/Verwirrung + 10MP
# HP: Konstitution d4→d6 2HP + 2×Fertigkeit-Schritt 1HP+1HP = 4HP ✓
# Skills: 12+2 = 14pts (volle Auswahl)
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Ambassador', protokoll='logs/scifi_ambassador.log')
    s.handicap('Vorsichtig')
    s.handicap('Neugierig')
    s.handicap('Loyal')
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Mystische Kräfte: Telepath', ignore_voraussetzungen=True)  # free!
    m(f"  Talent+Mächte: HC={s.ch.verbleibende_handicap_punkte} maechte={sorted(s.ch.selected_maechte)}")
    s.attribut_auf('Verstand', 8)
    s.attribut_auf('Willenskraft', 8)
    s.attribut_auf('Geschicklichkeit', 6)
    s.steigere_mit_handicap_attribut('Konstitution')  # d4→d6 (2HP)
    m(f"  Attrs: {s.punktestand()}")
    # Skills 12pts: Überr d8(2)+Recherche d8(3)+Prov d8(3)+Wahrn d6(1)+Geisteswiss d6(2)+AK d6(1) = 12
    skills_setzen(s, [('Geisteswissenschaften',6),('Allgemeinwissen',6),
                      ('Wahrnehmung',6),('Überreden',8),('Recherche',8),('Provozieren',8)])
    # 2HP für 2 Fertigkeits-Schritte (Einschüchtern d4 + Darbietung d4 aktivieren)
    s.steigere_mit_handicap_fertigkeit('Einschüchtern')   # 1HP
    s.steigere_mit_handicap_fertigkeit('Darbietung')      # 1HP
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 4)
    advance_attr(s, 'Verstand')   # d8→d10
    for t in ['Alleskönner','Charismatisch','Aufwiegler']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    for item in [('Körperpanzerung +4',1),('Laserpistole',1),('Waffensperre',1),
                 ('Universalübersetzer',1),('Persönliche Datenassistenz',1),('Batterie, Universal-',1),
                 ('Biolink',1)]:
        s.kaufen(*item)
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Ambassador_A.json')
    b = s.bericht('logs/scifi_ambassador_bericht.json')
    m(f"Ambassador FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Ambassador CRASH: {e}\n{traceback.format_exc()}')

# ═══════════════════════════════════════════════════════
# 5. HACKER  Pace 6 Parry 4 Toughness 7(2)
# HP: Amourös(1)+Misstrauisch_leicht(1)+Gesucht_schwer(2) = 4HP
# Mensch: Gassenwissen free → Willenskraft d6→d8 2HP + 2×Fertigkeit 1HP+1HP = 4HP ✓
# Willenskraft d8 jetzt erreicht
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Hacker', protokoll='logs/scifi_hacker.log')
    s.handicap('Amourös')
    s.handicap('Misstrauisch_leicht')
    s.handicap('Gesucht_schwer')
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Gassenwissen', ignore_voraussetzungen=True)  # free
    m(f"  Talent: HC={s.ch.verbleibende_handicap_punkte}")
    s.attribut_auf('Verstand', 8)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Geschicklichkeit', 6)
    s.attribut_auf('Konstitution', 6)
    s.steigere_mit_handicap_attribut('Willenskraft')  # d6→d8 (2HP)
    m(f"  Attrs: {s.punktestand()}")
    # Skills 12pts: AK d6(1)+Elek d8(3)+Hacken d8(3)+Recherche d8(3)+Natur d6(2) = 12
    skills_setzen(s, [('Allgemeinwissen',6),('Elektronik',8),('Hacken',8),
                      ('Recherche',8),('Naturwissenschaften',6)])
    # 2HP: Geisteswissenschaften d4 + Reparieren d4 aktivieren
    s.steigere_mit_handicap_fertigkeit('Geisteswissenschaften')  # 1HP
    s.steigere_mit_handicap_fertigkeit('Reparieren')             # 1HP
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 4)
    for t in ['Gelehrter','Ermittler','Hackerman/-woman','Kühler Kopf']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    for item in [('Kevlarweste',1),('Rucksack',1),('Universalübersetzer',1),('Persönliche Datenassistenz',1),
                 ('Cyberdeck',1),('Commlink',1)]:
        s.kaufen(*item)
    s.notiz('MISSING: Alter Wear, Schutzbrille (beide kein SciFi-Item im deutschen Setting)')
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Hacker_A.json')
    b = s.bericht('logs/scifi_hacker_bericht.json')
    m(f"Hacker FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Hacker CRASH: {e}\n{traceback.format_exc()}')

# ═══════════════════════════════════════════════════════
# 6. INFILTRATOR  Pace 6 Parry 6 Toughness 9(4)
# HP: Vorsichtig(1)+Misstrauisch_leicht(1)+Gesucht_schwer(2) = 4HP
# Mensch: Gut Ausgerüstet free → Dieb 2HP → Stärke d4→d6 2HP = 4HP ✓
# ═══════════════════════════════════════════════════════
try:
    s = d.Sitzung('SciFi Kompendium', 'Infiltrator', protokoll='logs/scifi_infiltrator.log')
    s.handicap('Vorsichtig')
    s.handicap('Misstrauisch_leicht')
    s.handicap('Gesucht_schwer')
    s.volk('Mensch')
    s.volk_freies_talent('Mensch', 'Gut Ausgerüstet', ignore_voraussetzungen=True)  # free
    s.talent('Dieb', ignore_voraussetzungen=True)                                    # 2HP
    m(f"  Talente: HC={s.ch.verbleibende_handicap_punkte}")
    s.attribut_auf('Geschicklichkeit', 8)
    s.attribut_auf('Willenskraft', 6)
    s.attribut_auf('Verstand', 6)
    s.attribut_auf('Konstitution', 6)
    # Stärke d4→d6 via HP WEGGELASSEN, um 2 HP für fehlende Skills zu haben
    m(f"  Attrs: {s.punktestand()}")
    skills_setzen(s, [('Athletik',8),('Kämpfen',8),('Hacken',6),
                      ('Wahrnehmung',6),('Heimlichkeit',8),('Diebeskunst',6)])
    # Fehlende Bogen-Skills: Elektronik via HP (Diebeskunst d6→d8 später via D-Adv)
    s.steigere_mit_handicap_fertigkeit('Elektronik')           # 1 HP
    m(f"  Skills: {s.punktestand()}")
    abschliessen(s, 4)
    # Bogen: "Fighting d8 & Thievery d8" – Skills bereits CharGen d8, daher 0 Aufstiege
    r = s.fertigkeit_mit_aufstieg('Kämpfen', 8)
    m(f"  Advance Kämpfen d8: ok={ok_check(r)}")
    # Diebeskunst d6→d8 via D-Adv (0.5 verb verbleibend)
    r = s.fertigkeit_mit_aufstieg('Diebeskunst', 8)
    m(f"  Advance Diebeskunst d8: ok={ok_check(r)}")
    for t in ['Beidhändiger Kampf','Schnell','Ausweichen']:
        r = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
        m(f"  Advance {t}: ok={ok_check(r)}")
    for item in [('Körperpanzerung +4',1),('Molekularschwert',2),('Tarnanzug',1),
                 ('Persönliche Datenassistenz',1),('Universalübersetzer',1),
                 ('Cyberdeck',1),('Direktionales Mikrofon',1),('Kreislaufatemgerät',1),
                 ('Betäubungsschlagstock',1),('EMP-Granate',4)]:
        s.kaufen(*item)
    for cw in [('Cyberware: Verborgenes Fach',1),('Cyberware: Verborgenes Fach',1)]:
        s.kaufen(*cw)
    s.notiz('MISSING: Schneidbrenner (cutting torch), Elektronischer Dietrich, Linienprojektor (kein SciFi-Item im deutschen Setting); Betäubungsknüppel → Betäubungsschlagstock, Schockgranaten → EMP-Granate')
    s.notiz('STÄRKE: Bogen d6, Build d4 (HP freigegeben für fehlende Skills Elektronik via HP, Diebeskunst d6→d8 via D-Adv)')
    s.speichern('chars/Archetypen/Archetyp_SciFi_Kompendium_Infiltrator_A.json')
    b = s.bericht('logs/scifi_infiltrator_bericht.json')
    m(f"Infiltrator FERTIG anomalien={b['anomalien_anzahl']}")
except BaseException as e:
    m(f'Infiltrator CRASH: {e}\n{traceback.format_exc()}')

tlog.close()
print("BATCH1 DONE")
