"""Worlds of Ulisses Archetypen - HeXXen 1773 Setting (4 Archetypen).

Raphael (Ordenskrieger), Jeanne (Schützin), Klaas (Fechter), Klara (Alchemistin).
"""
import sys, os, traceback, json
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d

OUT = 'logs/ulisses'
tlog = open(f'{OUT}/hexxen_trace.txt', 'w', encoding='utf-8')
def m(x):
    tlog.write(str(x)+'\n'); tlog.flush()


def lauf(name, soll, builder):
    m(f'\n{"="*70}\nBUILD: {name}\n{"="*70}')
    try:
        s = d.Sitzung('HeXXen 1773', name, protokoll=f'{OUT}/{name}.log')
        builder(s, soll)
        s.ch.berechne_abgeleitete_werte()
        m(f'  Endpunkte: AP={s.ch.verbleibende_attributsteigerungen} '
          f'FP={s.ch.verbleibende_fertigkeitssteigerungen} '
          f'HP={s.ch.verbleibende_handicap_punkte}/{s.ch.gesamt_handicap_punkte} '
          f'Geld={s.ch.vermoegen}')
        m(f'  Parade={s.ch.parade} Robustheit={s.ch.robustheit} '
          f'Bewegung={s.ch.bewegungsweite} Bennys={s.ch.bennys} MP={s.ch.machtpunkte}')
        m(f'  Talente: {sorted(s.ch.selected_talente)}')
        m(f'  Handicaps: {sorted(s.ch.selected_handicaps)}')
        m(f'  Mächte: {sorted(s.ch.selected_maechte)}')
        diff = s.diff(soll)
        for a in diff['abweichungen']:
            m(f'  DIFF: {a}')
        if not diff['abweichungen']:
            m('  DIFF: -- KEINE --')
        pfad = f'chars/Archetypen/Archetyp_HeXXen_1773_{name}_A.json'
        s.speichern(pfad)
        b = s.bericht(f'{OUT}/{name}_bericht.json')
        m(f'  SAVED: {pfad} | anomalien={b["anomalien_anzahl"]}')
        return s, diff
    except BaseException as e:
        m(f'  CRASH: {e!r}\n{traceback.format_exc()}')
        return None, None


def standard_mensch_hexxen(s, freies_talent, manual_handicaps, attribute_ziele,
                           fertigkeit_ziele, weitere_talente, maechte=None,
                           ausruestung=None):
    """Standard-Build mit Mensch-Volk für HeXXen (nur freies_talent, kein freies_attribut)."""
    major = [h for h in manual_handicaps if not h.endswith('_leicht')]
    minor = [h for h in manual_handicaps if h.endswith('_leicht')]
    for h in major + minor:
        if h in s.ch.handicaps:
            s.handicap(h)
        else:
            s.notiz(f'HANDICAP-KEY fehlt in HeXXen: {h}')

    s.volk('Mensch')

    if freies_talent:
        if freies_talent in s.ch.talente:
            s.volk_freies_talent('Mensch', freies_talent, ignore_voraussetzungen=True)
        else:
            s.notiz(f'TALENT-KEY fehlt fuer freies Talent: {freies_talent}')

    # Attribute regulär + HP (Bogen-Attribute haben Vorrang)
    sorted_attr = sorted(attribute_ziele.items(), key=lambda x: -x[1])
    for a, z in sorted_attr:
        s.attribut_auf(a, z)
    for a, z in sorted_attr:
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte >= 2:
            vor = s.ch.attribute[a].wuerfel.value
            s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value == vor: break

    # Fertigkeiten regulär (kein HP-Fallback hier – kommt nach Talenten)
    sorted_fert = sorted(fertigkeit_ziele.items(), key=lambda x: -x[1])
    for f, z in sorted_fert:
        if f in s.ch.fertigkeiten:
            s.fertigkeit_auf(f, z)
        else:
            s.notiz(f'FERTIGKEIT-KEY fehlt in HeXXen: {f}')

    # Bezahlte Talente (2 HP/Talent) – Bogen-Talente Vorrang vor Skill-Pips
    for t in weitere_talente:
        if t in s.ch.selected_talente: continue
        if t not in s.ch.talente:
            s.notiz(f'TALENT-KEY fehlt in HeXXen: {t}'); continue
        s.talent(t, ignore_voraussetzungen=True)

    # HP-Fallback Fertigkeiten (mit dem was übrig ist)
    for f, z in sorted_fert:
        if f not in s.ch.fertigkeiten: continue
        w = s.ch.fertigkeiten[f].wuerfel
        while (w.value < z or w.modifier < 0) and s.ch.verbleibende_handicap_punkte >= 1:
            vor = (w.value, w.modifier)
            s.steigere_mit_handicap_fertigkeit(f)
            if (w.value, w.modifier) == vor: break

    # Mächte
    for mm in (maechte or []):
        if mm in s.ch.maechte:
            s.macht(mm, ignore_rang_check=True)
        else:
            s.notiz(f'MACHT-KEY fehlt in HeXXen: {mm}')

    # Ausrüstung
    for eintrag in (ausruestung or []):
        if isinstance(eintrag, tuple):
            item, anz = eintrag
        else:
            item, anz = eintrag, 1
        if item in s.ch.ausruestung:
            s.kaufen(item, anzahl=anz, force_bei_geldmangel=True)
        else:
            s.notiz(f'AUSRÜSTUNG-KEY fehlt in HeXXen-Katalog: {item}')


# =============================================================================
# 1. RAPHAEL, DER ORDENSKRIEGER
# =============================================================================
soll_raphael = {
    'attribute': {'Geschicklichkeit': 6, 'Konstitution': 6, 'Stärke': 8,
                  'Verstand': 6, 'Willenskraft': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 6,
                     'Heimlichkeit': 4, 'Kämpfen': 8, 'Reiten': 8,
                     'Überreden': 4, 'Wahrnehmung': 6},
    'handicaps': ['Ehrenkodex', 'Schwur_schwer'],
    'talente': ['Aristokrat', 'Kräftig'],
}
def build_raphael(s, soll):
    standard_mensch_hexxen(
        s,
        freies_talent='Kräftig',
        manual_handicaps=['Ehrenkodex', 'Schwur_schwer'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=['Aristokrat'],
        # Plattenrüstung fehlt im HeXXen-Katalog (nur Brustharnisch/Armschienen/Beinschienen Platte)
        ausruestung=['Pferd', 'Schwert, Langschwert', 'Abenteurerpaket'],
    )
    s.notiz('AUSRÜSTUNG-KEY fehlt: Plattenrüstung mit Helm (+4) – HeXXen hat nur Einzelteile (Brustharnisch (Platte), Geschlossener Helm)')


# =============================================================================
# 2. JEANNE, DIE SCHÜTZIN
# =============================================================================
soll_jeanne = {
    'attribute': {'Geschicklichkeit': 10, 'Konstitution': 6, 'Stärke': 6,
                  'Verstand': 6, 'Willenskraft': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Heimlichkeit': 8,
                     'Kämpfen': 6, 'Provozieren': 6, 'Schießen': 10,
                     'Überreden': 4, 'Wahrnehmung': 6},
    'handicaps': ['Loyal', 'Schwerzüngig', 'Stur'],
    'talente': ['Aufmerksamkeit'],
}
def build_jeanne(s, soll):
    standard_mensch_hexxen(
        s,
        freies_talent='Aufmerksamkeit',
        manual_handicaps=['Loyal', 'Schwerzüngig', 'Stur'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=[],
        # Lederjacke fehlt – HeXXen hat 'Lederkoller' (anderes Item per skill-rule keine Substitution)
        ausruestung=['Muskete', 'Schwert, Langschwert', 'Abenteurerpaket'],
    )
    s.notiz('AUSRÜSTUNG-KEY fehlt: Lederjacke (+2 Arme,Torso) – HeXXen hat nur "Lederkoller" (anderes Item)')


# =============================================================================
# 3. KLAAS, DER FECHTER
# =============================================================================
soll_klaas = {
    'attribute': {'Geschicklichkeit': 8, 'Konstitution': 6, 'Stärke': 6,
                  'Verstand': 6, 'Willenskraft': 8},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Heimlichkeit': 6,
                     'Kämpfen': 12, 'Provozieren': 8, 'Überreden': 4, 'Wahrnehmung': 6},
    'handicaps': ['Große Klappe', 'Impulsiv', 'Phobie_leicht'],
    'talente': ['Finte'],
}
def build_klaas(s, soll):
    standard_mensch_hexxen(
        s,
        freies_talent='Finte',
        manual_handicaps=['Große Klappe', 'Impulsiv', 'Phobie_leicht'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=[],
        # Rapier + Lederjacke fehlen – HeXXen hat Fechtwaffen/Parierdolch, Lederkoller
        ausruestung=['Abenteurerpaket'],
    )
    s.notiz('AUSRÜSTUNG-KEY fehlt: Rapier (Stä+W4, Parade+1) – HeXXen hat nur "Fechtwaffen/Parierdolch"')
    s.notiz('AUSRÜSTUNG-KEY fehlt: Lederjacke (+2 Arme,Torso) – HeXXen hat nur "Lederkoller"')


# =============================================================================
# 4. KLARA, DIE ALCHEMISTIN
# =============================================================================
# AH (Alchemist) = 10 MP + 3 Startmächte. Mit Machtpunkte-Talent +5 = 15 MP wie im Bogen.
soll_klara = {
    'attribute': {'Geschicklichkeit': 6, 'Konstitution': 6, 'Stärke': 4,
                  'Verstand': 10, 'Willenskraft': 6},
    'fertigkeiten': {'Alchemie': 10, 'Allgemeinwissen': 6, 'Athletik': 4,
                     'Heimlichkeit': 4, 'Naturwissenschaften': 8, 'Reparieren': 8,
                     'Schießen': 6, 'Überreden': 4, 'Wahrnehmung': 6},
    'handicaps': ['Außenseiter', 'Neugierig', 'Tick'],
    'talente': ['AH (Alchemist)', 'Machtpunkte'],
    'maechte': ['Eigenschaft erhöhen/senken', 'Schutz', 'Strahl'],
}
def build_klara(s, soll):
    standard_mensch_hexxen(
        s,
        freies_talent='AH (Alchemist)',
        manual_handicaps=['Außenseiter', 'Neugierig', 'Tick'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=['Machtpunkte'],
        maechte=soll['maechte'],
        ausruestung=['Dolche und Messer', 'Alchemistenpaket',
                     'Abenteurerpaket', 'Pistole'],
    )


# ========================================================================
# MAIN
# ========================================================================
ALLE = [
    ('Raphael', soll_raphael, build_raphael),
    ('Jeanne',  soll_jeanne,  build_jeanne),
    ('Klaas',   soll_klaas,   build_klaas),
    ('Klara',   soll_klara,   build_klara),
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
            'mp':        s.ch.machtpunkte,
            'anomalien': len(s.anomalien),
            'abweichungen': diff['abweichungen'] if diff else None,
        })

with open(f'{OUT}/hexxen_uebersicht.json', 'w', encoding='utf-8') as fh:
    json.dump(UEBERSICHT, fh, ensure_ascii=False, indent=2)
m(f'\nÜBERSICHT: {OUT}/hexxen_uebersicht.json -- {len(UEBERSICHT)}/{len(ALLE)} builds')
tlog.close()
