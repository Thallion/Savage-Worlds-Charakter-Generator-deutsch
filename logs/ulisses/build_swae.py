"""Worlds of Ulisses Archetypen - SWAE-Setting (9 Archetypen).

Baut: Arthan, Beatriz, Clementine, The Shroud, Aidan, Sozius, Samael, Asera, Zoetta
Quelle: Texte/Worlds_of_Ulisses_Archetypen.txt
"""
import sys, os, traceback, json
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d

OUT = 'logs/ulisses'
os.makedirs(OUT, exist_ok=True)
tlog = open(f'{OUT}/swae_trace.txt', 'w', encoding='utf-8')

def m(x):
    tlog.write(str(x) + '\n')
    tlog.flush()

def lauf(name, soll, builder):
    """Führt einen Build aus, speichert + Bericht."""
    m(f'\n{"="*70}\nBUILD: {name}\n{"="*70}')
    try:
        s = d.Sitzung('SWAE', name, protokoll=f'{OUT}/{name.replace(" ","_")}.log')
        builder(s, soll)
        s.ch.berechne_abgeleitete_werte()
        m(f'  Endpunkte: AP={s.ch.verbleibende_attributsteigerungen} '
          f'FP={s.ch.verbleibende_fertigkeitssteigerungen} '
          f'HP={s.ch.verbleibende_handicap_punkte}/{s.ch.gesamt_handicap_punkte} '
          f'Geld={s.ch.vermoegen}')
        m(f'  Parade={s.ch.parade} Robustheit={s.ch.robustheit} '
          f'Bewegung={s.ch.bewegungsweite} Bennys={s.ch.bennys}')
        m(f'  Talente: {sorted(s.ch.selected_talente)}')
        m(f'  Handicaps: {sorted(s.ch.selected_handicaps)}')
        diff = s.diff(soll)
        if diff['abweichungen']:
            for a in diff['abweichungen']:
                m(f'  DIFF: {a}')
        else:
            m('  DIFF: -- KEINE --')
        pfad = f'chars/Archetypen/Archetyp_SWAE_{name.replace(" ","_")}_A.json'
        s.speichern(pfad)
        b = s.bericht(f'{OUT}/{name.replace(" ","_")}_bericht.json')
        m(f'  SAVED: {pfad} | anomalien={b["anomalien_anzahl"]}')
        return s, diff
    except BaseException as e:
        m(f'  CRASH: {e!r}\n{traceback.format_exc()}')
        return None, None


# ========================================================================
# Helfer-Routinen für den klassischen SWAE-Mensch-Build (Volk Mensch, freies Talent)
# ========================================================================
def standard_mensch(s, freies_talent, manual_handicaps, attribute_ziele,
                    fertigkeit_ziele, weitere_talente, maechte=None,
                    ausruestung=None, freies_talent_voraussetzungen=True):
    """Standard-Build: handicaps → volk → free talent → attr (regulär)
       → fert (regulär) → bezahlte Talente (HP) → attr/fert HP-Fallback
       → mächte → ausrüstung.

    Wichtig: bezahlte Talente (2 HP/Talent) werden vor dem HP-Fallback gekauft,
    damit das HP-Budget priorisiert auf Talente geht (sonst gehen HP an einzelne
    Skill-Pips verloren, die der Bogen weniger dringend braucht)."""
    # 2. Handicaps – major zuerst
    major = [h for h in manual_handicaps if not h.endswith('_leicht')]
    minor = [h for h in manual_handicaps if h.endswith('_leicht')]
    for h in major + minor:
        if h in s.ch.handicaps:
            s.handicap(h)
        else:
            s.notiz(f'HANDICAP-KEY fehlt in SWAE: {h}')

    # 3. Volk Mensch
    s.volk('Mensch')

    # 4. freies Talent (Mensch hat in SWAE nur freies_talent, kein freies_attribut)
    if freies_talent:
        if freies_talent in s.ch.talente:
            s.volk_freies_talent('Mensch', freies_talent,
                                 ignore_voraussetzungen=freies_talent_voraussetzungen)
        else:
            s.notiz(f'TALENT-KEY fehlt fuer freies Talent: {freies_talent}')

    # 5a. Attribute regulär
    sorted_attr = sorted(attribute_ziele.items(), key=lambda x: -x[1])
    for a, z in sorted_attr:
        s.attribut_auf(a, z)

    # 5b. HP-Fallback Attribute (Bogen-Attributwerte haben Vorrang vor Talenten/Skills)
    for a, z in sorted_attr:
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte >= 2:
            vor = s.ch.attribute[a].wuerfel.value
            s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value == vor:
                break

    # 6a. Fertigkeiten regulär
    sorted_fert = sorted(fertigkeit_ziele.items(), key=lambda x: -x[1])
    for f, z in sorted_fert:
        if f in s.ch.fertigkeiten:
            s.fertigkeit_auf(f, z)
        else:
            s.notiz(f'FERTIGKEIT-KEY fehlt in SWAE: {f}')

    # 7. Bezahlte Talente (2 HP pro Talent) – nach Attr-Fertig, vor HP-Fert-Fallback
    # So bekommen Bogen-Talente Priorität ggü. einzelnen Skill-Pips.
    for t in weitere_talente:
        if t in s.ch.selected_talente:
            continue
        if t not in s.ch.talente:
            s.notiz(f'TALENT-KEY fehlt in SWAE: {t}')
            continue
        s.talent(t, ignore_voraussetzungen=True)

    # 6b. HP-Fallback Fertigkeiten (mit was an HP übrig ist)
    for f, z in sorted_fert:
        if f not in s.ch.fertigkeiten:
            continue
        w = s.ch.fertigkeiten[f].wuerfel
        while (w.value < z or w.modifier < 0) and s.ch.verbleibende_handicap_punkte >= 1:
            vor = (w.value, w.modifier)
            s.steigere_mit_handicap_fertigkeit(f)
            if (w.value, w.modifier) == vor:
                break

    # 8. Mächte
    for mm in (maechte or []):
        if mm in s.ch.maechte:
            s.macht(mm, ignore_rang_check=True)
        else:
            s.notiz(f'MACHT-KEY fehlt in SWAE: {mm}')

    # 9. Ausrüstung – mit force_bei_geldmangel
    for eintrag in (ausruestung or []):
        if isinstance(eintrag, tuple):
            item, anz = eintrag
        else:
            item, anz = eintrag, 1
        if item in s.ch.ausruestung:
            s.kaufen(item, anzahl=anz, force_bei_geldmangel=True)
        else:
            s.notiz(f'AUSRÜSTUNG-KEY fehlt in SWAE-Katalog: {item}')


# =============================================================================
# 1. ARTHAN, DER PRIESTER
# =============================================================================
soll_arthan = {
    'attribute': {'Geschicklichkeit': 6, 'Konstitution': 6, 'Stärke': 6,
                  'Verstand': 6, 'Willenskraft': 8},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 4, 'Glaube': 8, 'Heilen': 8,
                     'Heimlichkeit': 4, 'Kämpfen': 6, 'Überreden': 8, 'Wahrnehmung': 6},
    # Manuelle: Ehrenkodex(s), Pazifist_leicht, Sanftmütig (=leicht in SWAE)
    # AH(Wunder) auto: nichts spezielles (keine zusätzlichen Handicaps in SWAE)
    'handicaps': ['Ehrenkodex', 'Pazifist_leicht', 'Sanftmütig'],
    'talente': ['AH (Wunder)', 'Heiler'],
    'maechte': ['Heilung', 'Linderung', 'Waffe verbessern'],
}
def build_arthan(s, soll):
    standard_mensch(
        s,
        freies_talent='AH (Wunder)',
        manual_handicaps=['Ehrenkodex', 'Pazifist_leicht', 'Sanftmütig'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=['Heiler'],
        maechte=soll['maechte'],
        ausruestung=['Kettenhemd', 'Kriegshammer', 'Abenteurerpaket'],
    )


# =============================================================================
# 2. BEATRIZ, DIE POLIZISTIN
# =============================================================================
soll_beatriz = {
    'attribute': {'Geschicklichkeit': 6, 'Konstitution': 6, 'Stärke': 6,
                  'Verstand': 8, 'Willenskraft': 6},
    'fertigkeiten': {'Allgemeinwissen': 8, 'Athletik': 4, 'Heimlichkeit': 4,
                     'Kämpfen': 6, 'Recherche': 8, 'Schießen': 6,
                     'Überreden': 6, 'Wahrnehmung': 8},
    'handicaps': ['Angewohnheit_leicht', 'Ehrenkodex', 'Loyal'],
    'talente': ['Beziehungen', 'Ermittler'],
}
def build_beatriz(s, soll):
    standard_mensch(
        s,
        freies_talent='Ermittler',
        manual_handicaps=['Angewohnheit_leicht', 'Ehrenkodex', 'Loyal'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=['Beziehungen'],
        ausruestung=['Kevlarweste', 'Pistole'],  # 9mm-Pistole / Polizeiauto = nicht im Katalog
    )


# =============================================================================
# 3. CLEMENTINE, DIE BASTLERIN
# =============================================================================
soll_clementine = {
    'attribute': {'Geschicklichkeit': 4, 'Konstitution': 6, 'Stärke': 4,
                  'Verstand': 10, 'Willenskraft': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 4, 'Heimlichkeit': 4,
                     'Naturwissenschaften': 10, 'Recherche': 8, 'Reparieren': 8,
                     'Überreden': 4, 'Wahrnehmung': 8},
    'handicaps': ['Misstrauisch_schwer', 'Schwerhörig_leicht', 'Tick'],
    'talente': ['Gelehrter', 'McGyver', 'Reparaturgenie'],
}
def build_clementine(s, soll):
    standard_mensch(
        s,
        freies_talent='McGyver',
        manual_handicaps=['Misstrauisch_schwer', 'Schwerhörig_leicht', 'Tick'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=['Gelehrter', 'Reparaturgenie'],
        ausruestung=['Revolver', 'Brechstange'],  # Van = wahrscheinlich nicht im Katalog
    )


# =============================================================================
# 4. THE SHROUD, DER VIGILANT
# =============================================================================
soll_shroud = {
    'attribute': {'Geschicklichkeit': 8, 'Konstitution': 6, 'Stärke': 6,
                  'Verstand': 4, 'Willenskraft': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 8, 'Einschüchtern': 6,
                     'Fahren': 6, 'Heimlichkeit': 4, 'Kämpfen': 8, 'Provozieren': 6,
                     'Schießen': 6, 'Überreden': 4, 'Wahrnehmung': 6},
    # Fies (leicht, 1 HP) wurde nachgepflegt - jetzt alle 3 manuellen HC mit korrektem HP-Budget
    'handicaps': ['Blutrünstig', 'Fies', 'Skrupellos'],
    'talente': ['Akrobat', 'Ruhige Hände'],
}
def build_shroud(s, soll):
    standard_mensch(
        s,
        freies_talent='Akrobat',
        manual_handicaps=['Blutrünstig', 'Fies', 'Skrupellos'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=['Ruhige Hände'],
        ausruestung=['Pistole'],  # Cape / Maske = nicht im Standardkatalog
    )


# =============================================================================
# 5. AIDAN, DER HELD
# =============================================================================
soll_aidan = {
    'attribute': {'Geschicklichkeit': 6, 'Konstitution': 6, 'Stärke': 6,
                  'Verstand': 6, 'Willenskraft': 8},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 4, 'Einschüchtern': 6,
                     'Heimlichkeit': 4, 'Kämpfen': 4, 'Provozieren': 6,
                     'Schießen': 4, 'Überreden': 10, 'Wahrnehmung': 6},
    'handicaps': ['Heldenhaft', 'Loyal', 'Sanftmütig'],
    'talente': ['Attraktiv', 'Starker Wille'],
}
def build_aidan(s, soll):
    standard_mensch(
        s,
        freies_talent='Attraktiv',
        manual_handicaps=['Heldenhaft', 'Loyal', 'Sanftmütig'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=['Starker Wille'],
        ausruestung=['Machete', 'Pistole'],  # Lederjacke = nicht im SWAE-Katalog
    )


# =============================================================================
# 6. SOZIUS, DER PILOT
# =============================================================================
soll_sozius = {
    'attribute': {'Geschicklichkeit': 8, 'Konstitution': 6, 'Stärke': 6,
                  'Verstand': 8, 'Willenskraft': 4},
    # PDF "Fluggeräte lenken" = SWAE-Fertigkeit "Pilot" (Geschicklichkeit)
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 4, 'Pilot': 10,
                     'Heimlichkeit': 4, 'Kämpfen': 4, 'Reparieren': 4,
                     'Schießen': 8, 'Überreden': 4, 'Wahrnehmung': 8},
    'handicaps': ['Dünnhäutig', 'Impulsiv'],
    'talente': ['Ass am Steuer', 'Aufmerksamkeit'],
}
def build_sozius(s, soll):
    standard_mensch(
        s,
        freies_talent='Ass am Steuer',
        manual_handicaps=['Dünnhäutig', 'Impulsiv'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=['Aufmerksamkeit'],
        ausruestung=[],  # Eruptor-Blaster / E-Schild = SciFi-Items, nicht in SWAE
    )
    s.notiz('AUSRÜSTUNG-KEY fehlt: Eruptor-Blaster (SciFi-Item)')
    s.notiz('AUSRÜSTUNG-KEY fehlt: E-Schild (SciFi-Item)')


# =============================================================================
# 7. SAMAEL, DER PISTOLIERO
# =============================================================================
soll_samael = {
    'attribute': {'Geschicklichkeit': 8, 'Konstitution': 6, 'Stärke': 6,
                  'Verstand': 6, 'Willenskraft': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Heimlichkeit': 6,
                     'Kämpfen': 6, 'Provozieren': 6, 'Schießen': 10,
                     'Überreden': 4, 'Wahrnehmung': 6},
    'handicaps': ['Angewohnheit_leicht', 'Feind_leicht', 'Gesucht_leicht'],
    'talente': ['Beidhändig', 'Beidhändiger Fernkampf'],
}
def build_samael(s, soll):
    standard_mensch(
        s,
        freies_talent='Beidhändig',
        manual_handicaps=['Angewohnheit_leicht', 'Feind_leicht', 'Gesucht_leicht'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=['Beidhändiger Fernkampf'],
        ausruestung=['Streitkolben'],  # Eruptor-Blaster, MuSP-Anzug = nicht in SWAE
    )
    s.notiz('AUSRÜSTUNG-KEY fehlt: Eruptor-Blaster x2 (SciFi-Item)')
    s.notiz('AUSRÜSTUNG-KEY fehlt: MuSP-Anzug (SciFi-Item)')


# =============================================================================
# 8. ASERA, DIE KOPFGELDJÄGERIN
# =============================================================================
soll_asera = {
    'attribute': {'Geschicklichkeit': 8, 'Konstitution': 6, 'Stärke': 4,
                  'Verstand': 8, 'Willenskraft': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Heimlichkeit': 8,
                     'Kämpfen': 6, 'Schießen': 6, 'Überleben': 8,
                     'Überreden': 4, 'Wahrnehmung': 8},
    # ANGETRIEBEN (schwer): Verbrecher zu finden. BLUTRÜNSTIG: keine Gefangenen.
    'handicaps': ['Angetrieben_schwer', 'Blutrünstig'],
    'talente': ['Naturbursche'],
}
def build_asera(s, soll):
    standard_mensch(
        s,
        freies_talent='Naturbursche',
        manual_handicaps=['Angetrieben_schwer', 'Blutrünstig'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=[],
        ausruestung=[],  # Flammengewehr, Schockstab, Lederwams = SciFi/Leder = nicht in SWAE
    )
    s.notiz('AUSRÜSTUNG-KEY fehlt: Flammengewehr (Kegelschablone, 3W6)')
    s.notiz('AUSRÜSTUNG-KEY fehlt: Schockstab (Stä+W4, Betäubt-Effekt)')
    s.notiz('AUSRÜSTUNG-KEY fehlt: Lederwams (+1 Torso)')


# =============================================================================
# 9. ZOETTA, DIE PLANERIN
# =============================================================================
soll_zoetta = {
    'attribute': {'Geschicklichkeit': 6, 'Konstitution': 6, 'Stärke': 6,
                  'Verstand': 8, 'Willenskraft': 8},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 4, 'Einschüchtern': 6,
                     'Heilen': 6, 'Heimlichkeit': 4, 'Kriegskunst': 6,
                     'Kämpfen': 6, 'Schießen': 6, 'Überreden': 6, 'Wahrnehmung': 6},
    'handicaps': ['Langsam_leicht', 'Loyal', 'Pech'],
    'talente': ['Anführer'],
}
def build_zoetta(s, soll):
    standard_mensch(
        s,
        freies_talent='Anführer',
        manual_handicaps=['Langsam_leicht', 'Loyal', 'Pech'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=[],
        ausruestung=['Säbel'],  # Eruptor-Blaster, Lederwams = nicht in SWAE
    )
    s.notiz('AUSRÜSTUNG-KEY fehlt: Eruptor-Blaster (SciFi-Item)')
    s.notiz('AUSRÜSTUNG-KEY fehlt: Lederwams (+1 Torso)')


# ========================================================================
# MAIN: alle Builds nacheinander
# ========================================================================
ALLE = [
    ('Arthan',         soll_arthan,     build_arthan),
    ('Beatriz',        soll_beatriz,    build_beatriz),
    ('Clementine',     soll_clementine, build_clementine),
    ('The_Shroud',     soll_shroud,     build_shroud),
    ('Aidan',          soll_aidan,      build_aidan),
    ('Sozius',         soll_sozius,     build_sozius),
    ('Samael',         soll_samael,     build_samael),
    ('Asera',          soll_asera,      build_asera),
    ('Zoetta',         soll_zoetta,     build_zoetta),
]

UEBERSICHT = []
for name, soll, builder in ALLE:
    s, diff = lauf(name, soll, builder)
    if s is not None:
        UEBERSICHT.append({
            'name': name,
            'attr_rest': s.ch.verbleibende_attributsteigerungen,
            'fert_rest': s.ch.verbleibende_fertigkeitssteigerungen,
            'hp_rest':   s.ch.verbleibende_handicap_punkte,
            'hp_gesamt': s.ch.gesamt_handicap_punkte,
            'anomalien': len(s.anomalien),
            'abweichungen': diff['abweichungen'] if diff else None,
        })

# Schreibe Übersicht
with open(f'{OUT}/swae_uebersicht.json', 'w', encoding='utf-8') as fh:
    json.dump(UEBERSICHT, fh, ensure_ascii=False, indent=2)
m(f'\nÜBERSICHT geschrieben: {OUT}/swae_uebersicht.json')
m(f'Gesamt: {len(UEBERSICHT)}/{len(ALLE)} Builds erfolgreich')
tlog.close()
