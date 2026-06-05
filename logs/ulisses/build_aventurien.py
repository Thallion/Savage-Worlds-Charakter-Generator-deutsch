"""Worlds of Ulisses Archetypen - Savage Aventurien Setting (2 Archetypen).

Leomara (Kriegerin), Hesindian (Magier).
"""
import sys, os, traceback, json
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d

OUT = 'logs/ulisses'
tlog = open(f'{OUT}/aventurien_trace.txt', 'w', encoding='utf-8')
def m(x):
    tlog.write(str(x)+'\n'); tlog.flush()


def lauf(name, soll, builder):
    m(f'\n{"="*70}\nBUILD: {name}\n{"="*70}')
    try:
        s = d.Sitzung('Savage Aventurien', name, protokoll=f'{OUT}/{name}.log')
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
        pfad = f'chars/Archetypen/Archetyp_Savage_Aventurien_{name}_A.json'
        s.speichern(pfad)
        b = s.bericht(f'{OUT}/{name}_bericht.json')
        m(f'  SAVED: {pfad} | anomalien={b["anomalien_anzahl"]}')
        return s, diff
    except BaseException as e:
        m(f'  CRASH: {e!r}\n{traceback.format_exc()}')
        return None, None


def standard_mensch_aventurien(s, freies_talent, freies_attribut, manual_handicaps,
                               attribute_ziele, fertigkeit_ziele, weitere_talente,
                               maechte=None, ausruestung=None):
    """Standard-Build mit Mensch-Volk für Aventurien (freies_talent + freies_attribut)."""
    major = [h for h in manual_handicaps if not h.endswith('_leicht')]
    minor = [h for h in manual_handicaps if h.endswith('_leicht')]
    for h in major + minor:
        if h in s.ch.handicaps:
            s.handicap(h)
        else:
            s.notiz(f'HANDICAP-KEY fehlt in Aventurien: {h}')

    s.volk('Mensch')

    # Freies Attribut zuerst (kostenlos W4→W6)
    if freies_attribut:
        s.volk_freies_attribut('Mensch', freies_attribut)
    # Freies Talent
    if freies_talent:
        if freies_talent in s.ch.talente:
            s.volk_freies_talent('Mensch', freies_talent, ignore_voraussetzungen=True)
        else:
            s.notiz(f'TALENT-KEY fehlt fuer freies Talent: {freies_talent}')

    # Attribute regulär + HP
    sorted_attr = sorted(attribute_ziele.items(), key=lambda x: -x[1])
    for a, z in sorted_attr:
        s.attribut_auf(a, z)
    for a, z in sorted_attr:
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte >= 2:
            vor = s.ch.attribute[a].wuerfel.value
            s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value == vor: break

    # Fertigkeiten regulär + HP
    sorted_fert = sorted(fertigkeit_ziele.items(), key=lambda x: -x[1])
    for f, z in sorted_fert:
        if f in s.ch.fertigkeiten:
            s.fertigkeit_auf(f, z)
        else:
            s.notiz(f'FERTIGKEIT-KEY fehlt in Aventurien: {f}')
    for f, z in sorted_fert:
        if f not in s.ch.fertigkeiten: continue
        w = s.ch.fertigkeiten[f].wuerfel
        while (w.value < z or w.modifier < 0) and s.ch.verbleibende_handicap_punkte >= 1:
            vor = (w.value, w.modifier)
            s.steigere_mit_handicap_fertigkeit(f)
            if (w.value, w.modifier) == vor: break

    # Talente
    for t in weitere_talente:
        if t in s.ch.selected_talente: continue
        if t not in s.ch.talente:
            s.notiz(f'TALENT-KEY fehlt in Aventurien: {t}'); continue
        s.talent(t, ignore_voraussetzungen=True)

    # Mächte
    for mm in (maechte or []):
        if mm in s.ch.maechte:
            s.macht(mm, ignore_rang_check=True)
        else:
            s.notiz(f'MACHT-KEY fehlt in Aventurien: {mm}')

    # Ausrüstung
    for eintrag in (ausruestung or []):
        if isinstance(eintrag, tuple):
            item, anz = eintrag
        else:
            item, anz = eintrag, 1
        if item in s.ch.ausruestung:
            s.kaufen(item, anzahl=anz, force_bei_geldmangel=True)
        else:
            s.notiz(f'AUSRÜSTUNG-KEY fehlt in Aventurien-Katalog: {item}')


# =============================================================================
# 1. LEOMARA, DIE KRIEGERIN
# =============================================================================
# PDF: Bei Rondra, welch' Narretei! (Rondra = aventurische Gottheit)
soll_leomara = {
    'attribute': {'Geschicklichkeit': 6, 'Konstitution': 6, 'Stärke': 6,
                  'Verstand': 8, 'Willenskraft': 8},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 4, 'Einschüchtern': 6,
                     'Heilen': 6, 'Heimlichkeit': 4, 'Kriegskunst': 6,
                     'Kämpfen': 6, 'Schießen': 6, 'Überreden': 6, 'Wahrnehmung': 6},
    'handicaps': ['Ehrenkodex', 'Loyal', 'Phobie_leicht'],
    'talente': ['Anführer'],
}
def build_leomara(s, soll):
    standard_mensch_aventurien(
        s,
        freies_talent='Anführer',
        freies_attribut='Verstand',  # gratis W4→W6, spart 1 Attr-Steig
        manual_handicaps=['Ehrenkodex', 'Loyal', 'Phobie_leicht'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=[],
        ausruestung=['Schwert, Langschwert', 'Mittlerer Schild', 'Abenteurerpaket'],
    )
    # Gambeson nicht im Aventurien-Katalog (Tuchrüstung wäre die Entsprechung,
    # aber per skill-rule keine Substitution)
    s.notiz('AUSRÜSTUNG-KEY fehlt: Gambeson (+1 Torso/Arme) – Aventurien hat keine "Gambeson"-Entsprechung')
    s.notiz('AUSRÜSTUNG-KEY fehlt: Kriegerbrief (Flavor-Item ohne Spielwerte)')


# =============================================================================
# 2. HESINDIAN, DER MAGIER
# =============================================================================
# AH (Magier) in Aventurien gibt 15 MP direkt – PDF nennt Machtpunkte-Talent, aber das
# wäre 15+5=20 MP, Bogen sagt 15 MP. Diskrepanz: SWAE-Bogen vs. Aventurien-Setting.
# Mit ignore_voraussetzungen=True, weil Hesindian's Skills nicht Okkultismus W6 hat.
soll_hesindian = {
    'attribute': {'Geschicklichkeit': 4, 'Konstitution': 6, 'Stärke': 4,
                  'Verstand': 10, 'Willenskraft': 8},
    'fertigkeiten': {'Allgemeinwissen': 8, 'Athletik': 4, 'Heimlichkeit': 6,
                     'Kämpfen': 4, 'Recherche': 6, 'Überleben': 4,
                     'Überreden': 6, 'Wahrnehmung': 4, 'Zaubern': 10},
    # Auto durch AH (Magier): Materialkomponenten, Behindernde Rüstung_jede, Behindernde_Rüstung_schwer
    'handicaps': ['Neugierig', 'Schlechte Augen_leicht', 'Tick',
                  'Materialkomponenten', 'Behindernde Rüstung_jede', 'Behindernde_Rüstung_schwer'],
    # AH (Magier) liefert 15 MP direkt + Auto-Talente: Schule, Arkane Verbindung, Zauberbücher
    'talente': ['AH (Magier)', 'Schule', 'Arkane Verbindung', 'Zauberbücher'],
    'maechte': ['Geschoss', 'Heilung', 'Blenden'],
}
def build_hesindian(s, soll):
    standard_mensch_aventurien(
        s,
        freies_talent='AH (Magier)',
        freies_attribut='Verstand',  # gratis W4→W6 für Zauber-Attribut
        manual_handicaps=['Neugierig', 'Schlechte Augen_leicht', 'Tick'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=[],
        maechte=soll['maechte'],
        ausruestung=['Stab', 'Abenteurerpaket'],  # Magierstab + Reiserobe = nicht im Katalog
    )
    s.notiz('AUSRÜSTUNG-KEY: PDF "Magierstab" → "Stab" im Aventurien-Katalog gewählt (Stä+W4, Parade+1, zweihändig). Anders benannt aber gleiche Spielwerte.')
    s.notiz('AUSRÜSTUNG-KEY fehlt: Reiserobe (Flavor-Item, kein RS)')
    s.notiz('DISKREPANZ: PDF zeigt "MACHTPUNKTE: mehr Macht" als Talent, aber AH (Magier) gibt in Aventurien bereits 15 MP. SWAE-AH gibt 10 MP, weshalb der Bogen +5 Machtpunkte-Talent vorgesehen hat.')


# =============================================================================
# 3. ROMOXOSCH, DER ZWERG (rebuild unter Aventurien)
# =============================================================================
# Aventurien Zwerg gibt auto: Konstitution +1 (W4→W6), Nachtsicht-Talent,
# Nichtschwimmer-Handicap, Langsam_leicht-Handicap, Bewegung 5.
# PDF erwähnt "Verringerte Bewegungsweite" – das ist Aventurien Langsam_leicht.
# Auto-Handicaps zählen NICHT zum HP-Limit von 4.
soll_romoxosch = {
    'attribute': {'Geschicklichkeit': 6, 'Konstitution': 8, 'Stärke': 8,
                  'Verstand': 6, 'Willenskraft': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Diebeskunst': 6,
                     'Einschüchtern': 4, 'Heimlichkeit': 4, 'Kämpfen': 6,
                     'Reparieren': 6, 'Schießen': 6, 'Überreden': 4,
                     'Wahrnehmung': 6},
    # Manuell: Gierig_schwer, Misstrauisch_leicht, Phobie_leicht
    # Auto durch Zwerg-Volk: Nichtschwimmer, Langsam_leicht
    'handicaps': ['Gierig_schwer', 'Misstrauisch_leicht', 'Phobie_leicht',
                  'Nichtschwimmer', 'Langsam_leicht'],
    # Manuell: Mutig. Auto durch Zwerg: Nachtsicht
    'talente': ['Mutig', 'Nachtsicht'],
}
def build_romoxosch(s, soll):
    # Volk-Spezialfall: Zwerg hat KEINE freien Wahlen, daher nicht standard_mensch
    # Reihenfolge: Handicaps → Volk → Attr → Fert → Talente → Ausrüstung
    manual_handicaps = ['Gierig_schwer', 'Misstrauisch_leicht', 'Phobie_leicht']
    major = [h for h in manual_handicaps if not h.endswith('_leicht')]
    minor = [h for h in manual_handicaps if h.endswith('_leicht')]
    for h in major + minor:
        s.handicap(h)
    s.volk('Zwerg')
    # Keine freien Wahlen bei Zwerg
    # Attribute (Konstitution startet schon W6 dank Zwerg-Bonus)
    sorted_attr = sorted(soll['attribute'].items(), key=lambda x: -x[1])
    for a, z in sorted_attr:
        s.attribut_auf(a, z)
    for a, z in sorted_attr:
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte >= 2:
            vor = s.ch.attribute[a].wuerfel.value
            s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value == vor: break
    # Fertigkeiten
    sorted_fert = sorted(soll['fertigkeiten'].items(), key=lambda x: -x[1])
    for f, z in sorted_fert:
        if f in s.ch.fertigkeiten:
            s.fertigkeit_auf(f, z)
    for f, z in sorted_fert:
        if f not in s.ch.fertigkeiten: continue
        w = s.ch.fertigkeiten[f].wuerfel
        while (w.value < z or w.modifier < 0) and s.ch.verbleibende_handicap_punkte >= 1:
            vor = (w.value, w.modifier)
            s.steigere_mit_handicap_fertigkeit(f)
            if (w.value, w.modifier) == vor: break
    # Talente: Mutig manuell, Nachtsicht auto
    if 'Mutig' not in s.ch.selected_talente:
        s.talent('Mutig', ignore_voraussetzungen=True)
    # Ausrüstung
    for item in ['Kettenhemd', 'Kriegsbeil', 'Öllampe', 'Abenteurerausrüstung']:
        if item in s.ch.ausruestung:
            s.kaufen(item, anzahl=1, force_bei_geldmangel=True)
        else:
            s.notiz(f'AUSRÜSTUNG-KEY fehlt in Aventurien-Katalog: {item}')
    # Armbrust hat Varianten – wähle "Schwere Armbrust" als 10/20/40 2W6 PB2 Match
    if 'Schwere Armbrust' in s.ch.ausruestung:
        s.kaufen('Schwere Armbrust', anzahl=1, force_bei_geldmangel=True)
    else:
        s.notiz('AUSRÜSTUNG: PDF "Armbrust (10/20/40, 2W6, PB 2)" → Schwere Armbrust gewählt')
    s.notiz('AUSRÜSTUNG: PDF "Werkzeug zur Fallenentschärfung" → Diebeswerkzeug gewählt')
    if 'Diebeswerkzeuge' in s.ch.ausruestung:
        s.kaufen('Diebeswerkzeuge', 1, force_bei_geldmangel=True)


# =============================================================================
# 4. ANGROND, DER STREUNER (rebuild unter Aventurien)
# =============================================================================
# Volk Mensch (PDF beschreibt "Streuner" als Konzept, nicht Volk).
soll_angrond = {
    'attribute': {'Geschicklichkeit': 8, 'Konstitution': 6, 'Stärke': 4,
                  'Verstand': 6, 'Willenskraft': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 8, 'Diebeskunst': 8,
                     'Heimlichkeit': 8, 'Kämpfen': 6, 'Provozieren': 6,
                     'Überreden': 6, 'Wahrnehmung': 6},
    'handicaps': ['Phobie_schwer', 'Tick'],
    'talente': ['Beidhändig', 'Glück'],
}
def build_angrond(s, soll):
    standard_mensch_aventurien(
        s,
        freies_talent='Glück',
        freies_attribut='Geschicklichkeit',  # gratis W4→W6 für Geschicklichkeit
        manual_handicaps=['Phobie_schwer', 'Tick'],
        attribute_ziele=soll['attribute'],
        fertigkeit_ziele=soll['fertigkeiten'],
        weitere_talente=['Beidhändig'],  # Geschick W8 erfüllt Voraussetzung
        ausruestung=[('Wurf-Dolch/Messer', 5), 'Kurzschwert', 'Abenteurerpaket'],
    )
    s.notiz('AUSRÜSTUNG-KEY fehlt: Lederweste (+1 Torso) – Aventurien hat nur Lederrüstung-Varianten')


# ========================================================================
# MAIN
# ========================================================================
ALLE = [
    ('Leomara',   soll_leomara,   build_leomara),
    ('Hesindian', soll_hesindian, build_hesindian),
    ('Romoxosch', soll_romoxosch, build_romoxosch),
    ('Angrond',   soll_angrond,   build_angrond),
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

with open(f'{OUT}/aventurien_uebersicht.json', 'w', encoding='utf-8') as fh:
    json.dump(UEBERSICHT, fh, ensure_ascii=False, indent=2)
m(f'\nÜBERSICHT: {OUT}/aventurien_uebersicht.json -- {len(UEBERSICHT)}/{len(ALLE)} builds')
tlog.close()
