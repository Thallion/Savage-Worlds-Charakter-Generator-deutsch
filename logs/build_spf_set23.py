#!/usr/bin/env python3
"""Build-Skript für Savage Pathfinder Archetypen Sets 2+3 (Novice + Seasoned).
Fokus: Code-Pfade testen, fehlende Deutsche Keys dokumentieren."""

import sys, traceback, json
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/spf_set23_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

def abschliessen(s, n_aufstiege):
    s.ch.char_gen_completed = True
    for _ in range(n_aufstiege): increase_aufstiege(s.ch)
    m(f"  → chargen abgeschlossen, {n_aufstiege} Aufstiege, Rang={s.ch.rang}")

all_results = []

def baue(name, setting, soll, manual_handicaps, klassentalent=None, volk=None,
         volk_wahlen=None, ausruestung=None, additional_skills=None, arkaner_hg=None,
         seasoniert=False, n_aufstiege=4):
    """Baut einen Archetyp und sammelt Ergebnisse."""
    result = {'name': name, 'setting': setting}
    try:
        s = d.Sitzung(setting, name, protokoll=f'logs/{name}.log')
        m(f"\n{'='*60}\nBAUE: {name} (Setting: {setting})")
        m(f"  Start: {s.punktestand()}")

        # Schritt 1: Klassentalent (Pathfinder)
        if klassentalent:
            vor = s.zustand()
            ok = s.pathfinder_klassentalent(klassentalent, ignore_voraussetzungen=True)
            auto = s.zeige_auto_eintraege(vor)
            m(f"  Klassentalent '{klassentalent}': ok={ok}")
            m(f"  Auto-Einträge: {auto}")
            if not ok:
                s.notiz(f'KLASSENTALENT "{klassentalent}" nicht gefunden oder fehlgeschlagen')

        # Schritt 2: Handicaps (nur manuelle)
        for h in manual_handicaps:
            ok = s.handicap(h)
            if not ok:
                s.notiz(f'HANDICAP "{h}" nicht gefunden oder fehlgeschlagen')
                m(f"  HANDICAP FEHLT: {h}")

        # Schritt 3: Volk
        if volk:
            vor = s.zustand()
            ok = s.volk(volk)
            auto = s.zeige_auto_eintraege(vor)
            m(f"  Volk '{volk}': ok={ok}, auto={auto}")
            if not ok:
                s.notiz(f'VOLK "{volk}" nicht gefunden')

        # Schritt 4: Volkswahlen
        if volk and volk_wahlen:
            wahlen = s.volk_wahlmoeglichkeiten(volk)
            m(f"  Volkswahlen verfügbar: {wahlen}")
            for wahl in wahlen:
                if wahl and 'freies_talent' in str(type(wahl)):
                    pass  # handled below
            for w in volk_wahlen:
                typ = w.get('typ','')
                val = w.get('wert','')
                if typ == 'freies_talent':
                    s.volk_freies_talent(volk, val, ignore_voraussetzungen=True)
                    m(f"  Freies Talent: {val}")
                elif typ == 'freies_attribut':
                    s.volk_freies_attribut(volk, val)
                    m(f"  Freies Attribut: {val}")
                elif typ == 'attribut_malus':
                    s.volk_attribut_malus(volk, val.get('attribut',''), val.get('malus',''))
                    m(f"  Attribut-Malus: {val}")
                elif typ == 'freie_fertigkeit':
                    s.volk_freie_fertigkeit(volk, val)
                    m(f"  Freie Fertigkeit: {val}")

        # Schritt 5: Attribute KOMPLETT vor Fertigkeiten
        m(f"  Attribute-SOLL: {soll.get('attribute',{})}")
        for a, z in soll.get('attribute', {}).items():
            if a in s.ch.attribute:
                s.attribut_auf(a, z)
                m(f"  attribut_auf({a}, {z}): wert={s.ch.attribute[a].wuerfel.value}")
            else:
                s.notiz(f'ATTRIBUT-KEY fehlt: {a}')

        # Attribute mit Handicap-Punkten nachsteigern
        for a, z in soll.get('attribute', {}).items():
            if a in s.ch.attribute:
                while (s.ch.attribute[a].wuerfel.value < z and
                       s.ch.verbleibende_handicap_punkte > 0):
                    vor_val = s.ch.attribute[a].wuerfel.value
                    s.steigere_mit_handicap_attribut(a)
                    if s.ch.attribute[a].wuerfel.value == vor_val:
                        break
        m(f"  Nach Attributen: {s.punktestand()}")

        # Schritt 6: Fertigkeiten
        for f, z in soll.get('fertigkeiten', {}).items():
            if f in s.ch.fertigkeiten:
                s.fertigkeit_auf(f, z)
            else:
                s.notiz(f'FERTIGKEIT-KEY fehlt: {f}')
                m(f"  FERTIGKEIT FEHLT: {f}")
        m(f"  Nach Fertigkeiten: {s.punktestand()}")

        # Schritt 7: Talente (nur die nicht schon ausgewählten)
        for t in soll.get('talente', []):
            if t not in s.ch.selected_talente:
                ok = s.talent(t, ignore_voraussetzungen=True)
                if not ok:
                    s.notiz(f'TALENT "{t}" nicht gefunden oder fehlgeschlagen')
                    m(f"  TALENT FEHLT: {t}")
                else:
                    m(f"  Talent '{t}': ok")

        # Schritt 8: Mächte
        for mm in soll.get('maechte', []):
            if mm in s.ch.maechte:
                ok = s.macht(mm)
                if not ok:
                    s.notiz(f'MACHT "{mm}" nicht gefunden')
                    m(f"  MACHT FEHLT: {mm}")
            else:
                s.notiz(f'MACHT {mm} nicht im Setting')

        # Schritt 9: Ausrüstung
        if ausruestung:
            m(f"  Vermögen vor Ausrüstung: {s.ch.vermoegen}")
            for name, anz in ausruestung:
                if name in s.ch.ausruestung:
                    r = s.kaufen(name, anzahl=anz, force_bei_geldmangel=True)
                    m(f"  Kauf: {anz}× {name}: ok={r.get('ok', '?')}")
                else:
                    s.notiz(f'AUSRÜSTUNG "{name}" fehlt im Katalog')
                    m(f"  AUSRÜSTUNG FEHLT: {name}")
            m(f"  Vermögen nach Ausrüstung: {s.ch.vermoegen}")

        # Fortgeschrittene
        if seasoniert:
            m(f"  --- Seasoned Upgrade ---")
            abschliessen(s, n_aufstiege)
            m(f"  Rang={s.ch.rang}, Aufstiege={s.ch.verbleibende_aufstiege}")
            # Seasoned-Talente
            for t in soll.get('seasoned_talente', []):
                if t not in s.ch.selected_talente:
                    ok = s.talent(t, ignore_rang_check=True, ignore_voraussetzungen=True)
                    if not ok:
                        s.notiz(f'SEASONED TALENT "{t}" nicht gefunden')
                        m(f"  SEASONED TALENT FEHLT: {t}")
                    else:
                        m(f"  Seasoned Talent '{t}': ok")
            # Seasoned-Attribute
            for a, z in soll.get('seasoned_attribute', {}).items():
                if a in s.ch.attribute:
                    while s.ch.attribute[a].wuerfel.value < z:
                        vor_val = s.ch.attribute[a].wuerfel.value
                        s.attribut_auf(a, z)
                        if s.ch.attribute[a].wuerfel.value == vor_val:
                            break
            # Seasoned-Fertigkeiten
            for f, z in soll.get('seasoned_fertigkeiten', {}).items():
                if f in s.ch.fertigkeiten:
                    s.fertigkeit_auf(f, z)
            # Seasoned-Mächte
            for mm in soll.get('seasoned_maechte', []):
                if mm in s.ch.maechte:
                    s.macht(mm, ignore_rang_check=True)
            # Seasoned-Ausrüstung (nur wenn neu)
            if soll.get('seasoned_ausruestung'):
                for name, anz in soll['seasoned_ausruestung']:
                    if name in s.ch.ausruestung:
                        s.kaufen(name, anzahl=anz, force_bei_geldmangel=True)

        # Schritt 10: Diff + Speichern
        s.ch.berechne_abgeleitete_werte()
        m(f"  PARADE={s.ch.parade} BEWEGUNG={s.ch.bewegungsweite} ROBUSTHEIT={s.ch.robustheit}")
        m(f"  End-Punktestand: {s.punktestand()}")
        diff = s.diff(soll)
        m(f"  DIFF: {diff['abweichungen']}")

        fname = f'chars/Archetypen/Archetyp_Savage_Pathfinder_{name}_A.json'
        s.speichern(fname)
        b = s.bericht(f'logs/{name}_bericht.json')
        m(f"  BERICHT: anomalien={b['anomalien_anzahl']}")

        result['ok'] = True
        result['diff'] = diff['abweichungen']
        result['anomalien'] = b['anomalien_anzahl']
        result['punkte'] = b['endzustand']['punkte']
    except BaseException as e:
        m(f"CRASH {name}: {e!r}\n{traceback.format_exc()}")
        result['ok'] = False
        result['error'] = str(e)
    all_results.append(result)
    return result


# =====================================================================
# SET 2 - NOVICE
# =====================================================================

# --- KIRA (BARBARIAN, Half-Elf, Novice) ---
baue('Kira', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 8, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 8, 'Allgemeinwissen': 4, 'Kämpfen': 6, 'Einschüchtern': 4, 'Wahrnehmung': 6, 'Okkultismus': 6, 'Überreden': 4, 'Heimlichkeit': 8, 'Überleben': 6},
    # Handicaps: Curious(major) + Loyal(minor) + Overconfident(major) — OVERCONFIDENT fehlt in DE!
    # Auto: Rüstungsbeschränkung_mittelschwer durch Barbar
    'handicaps': ['Neugierig', 'Loyal', 'Rüstungsbeschränkung_mittelschwer'],
    # Talente: Barbar (class) + Trademark Weapon (javelin) = Lieblingswaffe
    'talente':   ['Barbar'],
    'maechte':   [],
}, manual_handicaps=['Neugierig', 'Loyal'],
   klassentalent='Barbar', volk='Halbelf',
   volk_wahlen=[{'typ': 'freies_talent', 'wert': 'Barbar'}] if False else [],
   ausruestung=[])

# --- TELLER (BARD, Human, Novice) ---
# Missing DE edges: Formation Fighter (not found)
# Class: Barde -> AH (Barde) is the arcaner Hintergrund, but Bard as an Edge might not exist standalone
# Teller has: Bard + Formation Fighter + Arcane Background (Bard)
# German: Edge "Barde" exists? Let's check... AH (Barde) is the arcaner Hintergrund
# The bard class edge itself might be missing!
baue('Teller', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Geisteswissenschaften': 4, 'Athletik': 6, 'Allgemeinwissen': 6, 'Kämpfen': 8, 'Wahrnehmung': 6, 'Okkultismus': 4, 'Darbietung': 8, 'Überreden': 6, 'Schießen': 4, 'Heimlichkeit': 6},
    'handicaps': ['Impulsiv'],
    'talente':   [],
    'maechte':   ['Eigenschaft erhöhen/senken', 'Empathie', 'Verwirrung'],
}, manual_handicaps=['Impulsiv'],
   klassentalent='Barde', volk='Mensch',
   volk_wahlen=[{'typ': 'freies_talent', 'wert': 'Charismatisch'}],
   ausruestung=[])

# --- BROKAR (CLERIC, Dwarf, Novice) ---
# Code of Honor(major) + Tongue-Tied(major) — Tongue-Tied/Stotterer fehlt!
# Cleric (Good) -> Kleriker (Gut) - is this standalone? No, AH (Kleriker) is the arkaner Hintergrund
be = baue('Brokar', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 8},
    'fertigkeiten': {'Athletik': 4, 'Allgemeinwissen': 4, 'Glaube': 8, 'Kämpfen': 6, 'Heilen': 6, 'Wahrnehmung': 6, 'Okkultismus': 6, 'Überreden': 6, 'Schießen': 4, 'Heimlichkeit': 4},
    'handicaps': ['Ehrenkodex', 'Stumm'],  # Stumm = closest to Tongue-Tied
    'talente':   [],
    'maechte':   ['Heilung'],
}, manual_handicaps=['Ehrenkodex'],
   klassentalent='Kleriker', volk='Zwerg',
   volk_wahlen=[],
   ausruestung=[])

# --- ZYRIL (FIGHTER, Elf, Novice) ---
# One Arm(major) + Loyal(minor) + Vengeful(minor)
# Fighter + Trademark Weapon (longsword)
be = baue('Zyril', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 8, 'Konstitution': 8},
    'fertigkeiten': {'Athletik': 8, 'Allgemeinwissen': 4, 'Kämpfen': 8, 'Einschüchtern': 6, 'Wahrnehmung': 6, 'Überreden': 4, 'Reiten': 6, 'Heimlichkeit': 8, 'Überleben': 4},
    'handicaps': ['Einarmig', 'Loyal', 'Rachsüchtig_leicht'],
    'talente':   ['Kämpfer'],
    'maechte':   [],
}, manual_handicaps=['Einarmig', 'Loyal', 'Rachsüchtig_leicht'],
   klassentalent='Kämpfer', volk='Elf',
   ausruestung=[])

# --- KORVA (ROGUE, Human, Novice) ---
# Delusional(minor) + Hesitant(minor) + Obligation(major)
# Calculating + Elan + Rogue (class)
# Missing: "Wahnvorstellungen_leicht"? No, there is. But "obligation" = Verpflichtung
be = baue('Korva', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 6, 'Allgemeinwissen': 4, 'Kämpfen': 6, 'Wahrnehmung': 6, 'Darbietung': 6, 'Überreden': 6, 'Heimlichkeit': 6, 'Provozieren': 6, 'Diebeskunst': 6},
    'handicaps': ['Verpflichtung_schwer', 'Wahnvorstellungen_leicht', 'Zögerlich', 'Rüstungsbeschränkung_leicht'],
    'talente':   ['Schurke', 'Berechnend'],
    'maechte':   [],
}, manual_handicaps=['Verpflichtung_schwer', 'Wahnvorstellungen_leicht', 'Zögerlich'],
   klassentalent='Schurke', volk='Mensch',
   volk_wahlen=[{'typ': 'freies_talent', 'wert': 'Berechnend'}],
   ausruestung=[])

# --- PAELIE (WIZARD, Halfling, Novice) ---
# Greedy(minor) + Poverty(minor) + Shamed(major)
# Arcane Background (Wizard) + Arcane Resistance + Luck + Wizard (Conjurer)
# "Gierig_leicht"? yes. "Armut"? No. "Beschämt_schwer"? yes.
be = baue('Paelie', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {'Geisteswissenschaften': 6, 'Athletik': 6, 'Allgemeinwissen': 6, 'Kämpfen': 6, 'Glücksspiel': 6, 'Wahrnehmung': 6, 'Okkultismus': 6, 'Überreden': 4, 'Schießen': 6, 'Zaubern': 8, 'Heimlichkeit': 4},
    'handicaps': ['Beschämt_schwer', 'Gierig_leicht'],
    'talente':   ['Glück'],
    'maechte':   ['Geschoss', 'Schutz'],
}, manual_handicaps=['Beschämt_schwer', 'Gierig_leicht'],
   klassentalent='Magier', volk='Halbling',
   volk_wahlen=[{'typ': 'freies_talent', 'wert': 'Glück'}],
   ausruestung=[])

# --- FARIEL (DRUID, Elf, Novice) ---
# Bad Luck(major) + Loyal(minor) + Stubborn(minor)
# Arcane Background (Druid) + Druid + Extraction
be = baue('Fariel', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 6, 'Allgemeinwissen': 4, 'Glaube': 8, 'Kämpfen': 6, 'Heilen': 6, 'Wahrnehmung': 6, 'Überreden': 4, 'Schießen': 8, 'Heimlichkeit': 6, 'Überleben': 6},
    'handicaps': ['Pech', 'Loyal', 'Stur'],
    'talente':   [],
    'maechte':   ['Tierfreund', 'Verstricken'],
}, manual_handicaps=['Pech', 'Loyal', 'Stur'],
   klassentalent='Druide', volk='Elf',
   ausruestung=[])

# --- MARN (RANGER, Half-Orc, Novice) ---
# Bloodthirsty(major) + Enemy(minor) + Ugly(minor)
# Quick + Ranger + Sweep
be = baue('Marn', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 4, 'Willenskraft': 6, 'Stärke': 8, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 8, 'Allgemeinwissen': 4, 'Kämpfen': 8, 'Einschüchtern': 6, 'Wahrnehmung': 4, 'Okkultismus': 4, 'Überreden': 4, 'Reiten': 4, 'Heimlichkeit': 6, 'Überleben': 6},
    'handicaps': ['Blutrünstig', 'Feind_leicht', 'Hässlich_leicht', 'Rüstungsbeschränkung_mittelschwer'],
    'talente':   ['Schnell', 'Rundumschlag'],
    'maechte':   [],
}, manual_handicaps=['Blutrünstig', 'Feind_leicht', 'Hässlich_leicht'],
   klassentalent='Waldläufer', volk='Halbork',
   volk_wahlen=[{'typ': 'freies_talent', 'wert': 'Schnell'}],
   ausruestung=[])

# --- GNORR (SORCERER, Dwarf, Novice) ---
# Driven(major) + Mean(minor) + Quirk(minor)
# Missing hindrances: Mean/Grimmig (not found), Quirk/Eigenart (not found)
# Arcane Background (Sorcerer) + Sorcerer
be = baue('Gnor', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 8, 'Konstitution': 8},
    'fertigkeiten': {'Athletik': 6, 'Allgemeinwissen': 4, 'Kämpfen': 6, 'Einschüchtern': 6, 'Wahrnehmung': 6, 'Okkultismus': 6, 'Überreden': 4, 'Schießen': 4, 'Zaubern': 8, 'Heimlichkeit': 4},
    'handicaps': ['Angetrieben_schwer', 'Behindernde Rüstung_jede'],
    'talente':   [],
    'maechte':   ['Eigenschaft erhöhen/senken'],
}, manual_handicaps=['Angetrieben_schwer'],
   klassentalent='Zauberer', volk='Zwerg',
   ausruestung=[])

# --- MADDA (MONK, Half-Orc, Novice) ---
# Can't Swim(minor) + Heroic(major) + Small(minor)
# "Nichtschwimmer" exists! "Klein" exists!
# Brawler + Monk (class)
be = baue('Madda', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 8, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 8, 'Allgemeinwissen': 4, 'Kämpfen': 10, 'Heilen': 6, 'Einschüchtern': 6, 'Wahrnehmung': 6, 'Überreden': 4, 'Heimlichkeit': 6},
    'handicaps': ['Heroisch', 'Klein', 'Nichtschwimmer',
                  'Rüstungsbeschränkung_jede'],
    'talente':   ['Mönch', 'Raufbold'],
    'maechte':   [],
}, manual_handicaps=['Heroisch', 'Klein', 'Nichtschwimmer'],
   klassentalent='Mönch', volk='Halbork',
   volk_wahlen=[{'typ': 'freies_talent', 'wert': 'Raufbold'}],
   ausruestung=[])

# --- SIL (PALADIN, Elf, Novice) ---
# Code of Honor(major) + Loyal(minor) + Obligation(minor) + Vow(major)
# Vow = Schwur (schwer)
# Paladin + Luck
be = baue('Sil', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 8, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 6, 'Allgemeinwissen': 6, 'Kämpfen': 6, 'Wahrnehmung': 6, 'Okkultismus': 4, 'Überreden': 6, 'Reiten': 8, 'Schießen': 8, 'Heimlichkeit': 4},
    'handicaps': ['Ehrenkodex', 'Loyal', 'Schwur_schwer',
                  'Verpflichtung_leicht'],  # Obligation(minor)
    'talente':   ['Paladin', 'Glück'],
    'maechte':   [],
}, manual_handicaps=['Ehrenkodex', 'Loyal', 'Schwur_schwer', 'Verpflichtung_leicht'],
   klassentalent='Paladin', volk='Elf',
   volk_wahlen=[{'typ': 'freies_talent', 'wert': 'Glück'}],
   ausruestung=[])

# --- DARLA (NO CLASS, Human, Novice) ---
# Can't Swim(minor) + Impulsive(major) + Loyal(minor)
# Arcane Background (Magic) + Champion
# NO class edge! (uses generic Magic)
be = baue('Darla_ohneKlasse', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 4, 'Allgemeinwissen': 6, 'Kämpfen': 6, 'Wahrnehmung': 6, 'Okkultismus': 6, 'Überreden': 8, 'Reiten': 4, 'Zaubern': 8, 'Heimlichkeit': 4},
    'handicaps': ['Impulsiv', 'Loyal', 'Nichtschwimmer'],
    'talente':   ['Auserwählter'],
    'maechte':   ['Geschoss', 'Eigenschaft erhöhen/senken', 'Schutz'],
}, manual_handicaps=['Impulsiv', 'Loyal', 'Nichtschwimmer'],
   klassentalent=None,  # No class!
   volk='Mensch',
   volk_wahlen=[{'typ': 'freies_talent', 'wert': 'Auserwählter'}],
   arkaner_hg='AH (Magie)',  # Generic Magic
   ausruestung=[])

# =====================================================================
# SET 3 - NOVICE
# =====================================================================

# --- DAMIEL (ALCHEMIST, Elf, Novice) ---
# Favored Class(major) + Impulsive(major)
# Alchemist + Calculating + Arcane Background (Alchemist)
be = baue('Damiel', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Alchemie': 8, 'Athletik': 8, 'Allgemeinwissen': 6, 'Kämpfen': 8, 'Wahrnehmung': 6, 'Okkultismus': 4, 'Überreden': 6, 'Heimlichkeit': 6, 'Diebeskunst': 6},
    # Favored Class hindrance is not in DE system - probably a special rule
    'handicaps': ['Impulsiv', 'Behindernde Rüstung_leicht'],
    'talente':   ['Berechnend'],
    'maechte':   ['Abwehren', 'Gestaltwandeln'],
}, manual_handicaps=['Impulsiv'],
   klassentalent='Alchemist', volk='Elf',
   volk_wahlen=[{'typ': 'freies_talent', 'wert': 'Berechnend'}],
   ausruestung=[])

# --- ALAIN (CAVALIER, Human, Novice) ---
# Impulsive(major) + Vengeful(minor) + Vow(major-order)
# Cavalier + Command
# "Kavallerist" missing! Class talent doesn't exist
be = baue('Alain', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 8, 'Konstitution': 8},
    'fertigkeiten': {'Athletik': 6, 'Schlacht': 4, 'Allgemeinwissen': 4, 'Kämpfen': 8, 'Wahrnehmung': 6, 'Überreden': 6, 'Reiten': 6, 'Schießen': 6, 'Heimlichkeit': 4, 'Überleben': 4},
    'handicaps': ['Impulsiv', 'Rachsüchtig_leicht', 'Schwur_schwer'],
    'talente':   [],
    'maechte':   [],
}, manual_handicaps=['Impulsiv', 'Rachsüchtig_leicht', 'Schwur_schwer'],
   klassentalent='Kavallerist',  # THIS WILL FAIL - Kavallerist not in DE system
   volk='Mensch',
   ausruestung=[])

# --- IMRIJKA (INQUISITOR, Half-Orc, Novice) ---
# Obligation(minor) + Outsider(minor) + Ruthless(minor) + Stubborn(minor) + Vow(minor)
# "Rücksichtslos" not found! But "Stur" exists
# Elan + Inquisitor
be = baue('Imrijka', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 6, 'Allgemeinwissen': 6, 'Kämpfen': 6, 'Einschüchtern': 6, 'Wahrnehmung': 6, 'Okkultismus': 4, 'Überreden': 6, 'Schießen': 8, 'Heimlichkeit': 4, 'Überleben': 4},
    'handicaps': ['Stur', 'Verpflichtung_leicht', 'Schwur_leicht'],
    'talente':   ['Elan'],
    'maechte':   [],
}, manual_handicaps=['Stur', 'Verpflichtung_leicht', 'Schwur_leicht'],
   klassentalent='Inquisitor', volk='Halbork',
   volk_wahlen=[{'typ': 'freies_talent', 'wert': 'Elan'}],
   ausruestung=[])

# --- ALAHAZRA (ORACLE, Human, Novice) ---
# Bad Luck(major) + Loyal(minor) + Poverty(minor)
# "Armut" fehlt im DE
# Arcane Background (Oracle) + Oracle + Power Surge
be = baue('Alahazra', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 10, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 6, 'Allgemeinwissen': 4, 'Glaube': 10, 'Kämpfen': 4, 'Heilen': 6, 'Wahrnehmung': 6, 'Okkultismus': 6, 'Überreden': 6, 'Heimlichkeit': 4},
    'handicaps': ['Pech', 'Loyal'],  # Poverty missing
    'talente':   [],
    'maechte':   ['Arkanes entdecken/verbergen', 'Schutz vor Naturgewalten', 'Heilung'],
}, manual_handicaps=['Pech', 'Loyal'],
   klassentalent='Orakel', volk='Mensch',
   ausruestung=[])

# --- BALAZAR (SUMMONER, Gnome, Novice) ---
# Enemy(major) + Poverty(minor) + Secret(minor)
# Arcane Background (Summoner) + Extra Evolution + Summoner
# "Armut" fehlt. "Geheimnis_leicht"? Let's check - no
be = baue('Balazar', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 4, 'Allgemeinwissen': 6, 'Kämpfen': 6, 'Heilen': 4, 'Wahrnehmung': 6, 'Okkultismus': 8, 'Überreden': 4, 'Reiten': 4, 'Schießen': 4, 'Zaubern': 8, 'Heimlichkeit': 4, 'Überleben': 4},
    'handicaps': ['Feind_schwer'],  # Poverty + Secret missing
    'talente':   [],
    'maechte':   ['Abwehren', 'Heilung'],
}, manual_handicaps=['Feind_schwer'],
   klassentalent='Beschwörer', volk='Gnom',
   ausruestung=[])

# --- FEIYA (WITCH, Human, Novice) ---
# Driven(major) + Enemy(minor) + Loyal(minor)
# Arcane Background (Witch) + Alertness + Luck + Witch
be = baue('Feiya', 'Savage Pathfinder', {
    'attribute': {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Athletik': 4, 'Allgemeinwissen': 6, 'Kämpfen': 4, 'Heilen': 6, 'Einschüchtern': 6, 'Wahrnehmung': 6, 'Okkultismus': 6, 'Überreden': 4, 'Zaubern': 8, 'Heimlichkeit': 4},
    'handicaps': ['Angetrieben_schwer', 'Feind_leicht', 'Loyal'],
    'talente':   ['Glück', 'Wachsam'],
    'maechte':   ['Eigenschaft erhöhen/senken', 'Schutz'],
}, manual_handicaps=['Angetrieben_schwer', 'Feind_leicht', 'Loyal'],
   klassentalent='Hexenmeister', volk='Mensch',
   volk_wahlen=[{'typ': 'freies_talent', 'wert': 'Glück'}],
   ausruestung=[])


# =====================================================================
# Zusammenfassung
# =====================================================================
m("\n" + "="*60)
m("ZUSAMMENFASSUNG")
m("="*60)
for r in all_results:
    status = "OK" if r.get('ok') else f"CRASH: {r.get('error','?')}"
    m(f"  {r['name']:25s} | {status:15s} | anomalien={r.get('anomalien','?')} | punkte={r.get('punkte','?')}")

# Wichtige fehlende Deutsche Keys dokumentieren
fehlende_keys = """
FEHLENDE DEUTSCHE KEYS IM SAVAGE PATHFINDER SETTING:
=====================================================
Klassentalente: Barde, Kleriker, Druide, Orakel, Zauberer als Standalone-Edges (existieren nur als AH)
  Kavallerist (Cavalier) - fehlt komplett
Handicaps: Überheblich (Overconfident), Armut (Poverty), Geizig, Anämisch (Anemic),
  Rücksichtslos (Ruthless), Grimmig (Mean), Eigenart (Quirk), Blutdurst (Bloodthirsty),
  Stotterer/Sprachfehler (Tongue-tied)
Talente: Attentäter (Assassin), Kanalisierung (Channeling), Extraktion (Extraction),
  Traditionswaffe (Trademark Weapon) - exists as "Lieblingswaffe"? No, that's Favorite Weapon,
  Heldenmut inspirieren (Inspire Heroism), Banner, Tödlicher Schlag (Deadly Blow),
  Mächtiger Schlag (Powerful Blow? No, exists as Kraftvoller Schlag)
"""
m(fehlende_keys)

tlog.close()
print(f"\nBuild completed. {len(all_results)} characters processed.")
print(f"See logs/spf_set23_trace.txt for details.")
