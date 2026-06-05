"""Build alle Rippers-Archetypen (13 total) — v3, abschliessen VOR Talente."""
import sys
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/build_rippers_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()


def baue(setting, name, soll, manual_handicaps, manual_talente,
         manual_maechte, ausruestung_plan, save_path, log_path, bericht_path,
         n_aufstiege=4):
    s = d.Sitzung(setting, name, protokoll=log_path)

    for h in manual_handicaps:
        s.handicap(h)
    m(f"  [{name}] Nach Handicaps: {s.punktestand()}")

    s.volk(soll['volk'])
    m(f"  [{name}] Nach Volk: {s.punktestand()}")

    if soll.get('volk_freies_attribut'):
        s.volk_freies_attribut(soll['volk'], soll['volk_freies_attribut'])
    if soll.get('volk_freies_talent'):
        s.volk_freies_talent(soll['volk'], soll['volk_freies_talent'],
                             ignore_voraussetzungen=True)

    for a, z in soll['attribute'].items():
        s.attribut_auf(a, z)
    for a, z in soll['attribute'].items():
        while (s.ch.attribute[a].wuerfel.value < z
               and s.ch.verbleibende_handicap_punkte > 0):
            vor = s.ch.attribute[a].wuerfel.value
            s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value == vor:
                break
    m(f"  [{name}] Attribute Ist: {[(a, s.ch.attribute[a].wuerfel.value) for a in soll['attribute']]}")

    for f, z in soll['fertigkeiten'].items():
        if f in s.ch.fertigkeiten:
            s.fertigkeit_auf(f, z)
        else:
            s.notiz(f'FERTIGKEIT-KEY fehlt: {f}')

    # AH-Talent ZUERST (setzt verfuegbare_maechte > 0 für Mächte)
    ah_talent = next((t for t in manual_talente if t.startswith('AH ')), None)
    if ah_talent:
        s.talent(ah_talent, ignore_voraussetzungen=True, ignore_rang_check=True)
        m(f"  [{name}] Nach AH {ah_talent}: {s.ch.verfuegbare_maechte} Mächte verfügbar")

    # Mächte (brauchen AH)
    for mm in manual_maechte:
        s.macht(mm, ignore_rang_check=True)
    if manual_maechte:
        m(f"  [{name}] Mächte: {s.ch.selected_maechte}")

    # CharGen abschliessen + Aufstiege
    if n_aufstiege > 0:
        s.ch.char_gen_completed = True
        for _ in range(n_aufstiege):
            increase_aufstiege(s.ch)
        m(f"  [{name}] → {n_aufstiege} Aufstiege, Rang={s.ch.rang}")

    # Restliche Talente (AH wurde schon gesetzt, werden mit Aufstiegen bezahlt)
    for t in manual_talente:
        if t not in s.ch.selected_talente:
            s.talent(t, ignore_voraussetzungen=True, ignore_rang_check=True)

    for name_a, anz in ausruestung_plan:
        if name_a in s.ch.ausruestung:
            s.kaufen(name_a, anz, force_bei_geldmangel=True)
        else:
            s.notiz(f'AUSRÜSTUNG FEHLT: {name_a}')

    m(f"  [{name}] Restpunkte: {s.punktestand()}")
    diff = s.diff(soll)
    m(f'  [{name}] DIFF: {diff.get("abweichungen", diff)}')
    s.speichern(save_path)
    b = s.bericht(bericht_path)
    m(f'  [{name}] FERTIG anomalien={b["anomalien_anzahl"]}')


# =============================================================================
# 1. VATER FREDERICK HARTELL — Clergy (Irish Priest, Miracles)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 1: Vater Frederick Hartell ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Vater Frederick Hartell',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Auserwählter',
        'attribute': {'Geschicklichkeit': 6, 'Stärke': 6, 'Konstitution': 6, 'Verstand': 6, 'Willenskraft': 8},
        'fertigkeiten': {'Glaube': 8, 'Heilen': 6, 'Kämpfen': 6, 'Wahrnehmung': 6,
                        'Allgemeinwissen': 6, 'Überreden': 6, 'Überleben': 4,
                        'Sprache': 4},
        'handicaps': ['Ehrenkodex', 'Pflichtbewusst_leicht', 'Verpflichtung_leicht', 'Schwur_leicht'],
        'talente': ['AH (Priester)', 'Auserwählter', 'Heiliger/Unheiliger Krieger',
                    'Bodenständig'],
        'maechte': ['Heilung', 'Schutz', 'Linderung', 'Geschoss'],
    },
    manual_handicaps=['Ehrenkodex', 'Pflichtbewusst_leicht', 'Verpflichtung_leicht'],
    manual_talente=['AH (Priester)', 'Auserwählter', 'Heiliger/Unheiliger Krieger',
                    'Bodenständig'],
    manual_maechte=['Heilung', 'Schutz', 'Linderung', 'Geschoss'],
    ausruestung_plan=[('Heiliges Symbol', 1), ('Weihwasser (Flasche)', 1),
                      ('Knoblauch (Bund)', 1), ('Holzpfähle (5)', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Vater-Hartell_A.json',
    log_path='logs/build_rippers_hartell.log',
    bericht_path='logs/build_rippers_hartell_bericht.json',
)


# =============================================================================
# 2. JAMES DENTON — Cowboy (American, Quincy-Morris-Typ)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 2: James Denton ===\n" + "=" * 70)
baue(
    setting='Rippers', name='James Denton',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Volltreffer',
        'attribute': {'Geschicklichkeit': 8, 'Stärke': 8, 'Konstitution': 6, 'Verstand': 6, 'Willenskraft': 6},
        'fertigkeiten': {'Schießen': 8, 'Kämpfen': 6, 'Reiten': 8, 'Wahrnehmung': 6,
                        'Athletik': 6, 'Überreden': 6, 'Überleben': 4, 'Heimlichkeit': 4,
                        'Allgemeinwissen': 4},
        'handicaps': ['Arrogant', 'Rachsüchtig_leicht', 'Fies'],
        'talente': ['Volltreffer', 'Schnellfeuer', 'Verbessertes Schnellfeuer', 'Schnell'],
    },
    manual_handicaps=['Arrogant', 'Rachsüchtig_leicht', 'Fies'],
    manual_talente=['Volltreffer', 'Schnellfeuer', 'Verbessertes Schnellfeuer', 'Schnell'],
    manual_maechte=[],
    ausruestung_plan=[('Silberkugeln (10)', 1), ('Heiliges Symbol', 1),
                      ('Holzpfähle (5)', 1), ('Salz (5kg Sack)', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_James-Denton_A.json',
    log_path='logs/build_rippers_denton.log',
    bericht_path='logs/build_rippers_denton_bericht.json',
)


# =============================================================================
# 3. IRINA CAPELLO — Explorer (Italian, Survival/Tracking)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 3: Irina Capello ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Irina Capello',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Gelehrter',
        'attribute': {'Geschicklichkeit': 8, 'Stärke': 6, 'Konstitution': 6, 'Verstand': 8, 'Willenskraft': 6},
        'fertigkeiten': {'Überleben': 8, 'Wahrnehmung': 8, 'Recherche': 6, 'Athletik': 6,
                        'Sprache': 6, 'Schießen': 6, 'Kämpfen': 4, 'Heimlichkeit': 4,
                        'Allgemeinwissen': 6, 'Naturwissenschaften': 4},
        'handicaps': ['Neugierig', 'Jung', 'Schwur_leicht'],
        'talente': ['Gelehrter', 'Flink', 'Veteran der Dunklen Welt', 'Zweite Heimat'],
    },
    manual_handicaps=['Neugierig', 'Jung', 'Schwur_leicht'],
    manual_talente=['Gelehrter', 'Flink', 'Veteran der Dunklen Welt', 'Zweite Heimat'],
    manual_maechte=[],
    ausruestung_plan=[('Geisterjägerpaket', 1), ('EMF-Detektor', 1), ('Salz (5kg Sack)', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Irina-Capello_A.json',
    log_path='logs/build_rippers_capello.log',
    bericht_path='logs/build_rippers_capello_bericht.json',
)


# =============================================================================
# 4. AKSHARA KATHAT — Slayer (Indian, Sword + Bow)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 4: Akshara Kathat ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Akshara Kathat',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Kampfkünstler',
        'attribute': {'Geschicklichkeit': 10, 'Stärke': 8, 'Konstitution': 8, 'Verstand': 6, 'Willenskraft': 6},
        'fertigkeiten': {'Kämpfen': 10, 'Athletik': 8, 'Schießen': 8, 'Wahrnehmung': 6,
                        'Heimlichkeit': 6, 'Überleben': 6, 'Sprache': 4, 'Überreden': 4,
                        'Allgemeinwissen': 4},
        'handicaps': ['Ehrenkodex', 'Blutrünstig'],
        'talente': ['Kampfkünstler', 'Kampfakrobat', 'Erstschlag', 'Schneller Erstschlag',
                    'Bodenständig'],
    },
    manual_handicaps=['Ehrenkodex', 'Blutrünstig'],
    manual_talente=['Kampfkünstler', 'Kampfakrobat', 'Erstschlag', 'Schneller Erstschlag',
                    'Bodenständig'],
    manual_maechte=[],
    ausruestung_plan=[('Kaltes-Eisen-Schwert', 1), ('Silberdolch', 1),
                      ('Holzpfähle (5)', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Akshara-Kathat_A.json',
    log_path='logs/build_rippers_kathat.log',
    bericht_path='logs/build_rippers_kathat_bericht.json',
)


# =============================================================================
# 5. JACOB WHITLOCK — Slayer (British, Sword + Gun)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 5: Jacob Whitlock ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Jacob Whitlock',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Wolfsjäger',
        'attribute': {'Geschicklichkeit': 8, 'Stärke': 8, 'Konstitution': 8, 'Verstand': 6, 'Willenskraft': 6},
        'fertigkeiten': {'Kämpfen': 8, 'Schießen': 8, 'Athletik': 6, 'Wahrnehmung': 6,
                        'Überreden': 6, 'Überleben': 6, 'Heimlichkeit': 4,
                        'Allgemeinwissen': 6, 'Recherche': 4, 'Einschüchtern': 4},
        'handicaps': ['Arrogant', 'Ehrgeizig', 'Verpflichtung_leicht'],
        'talente': ['Wolfsjäger', 'Bodenständig', 'Kampfreflexe', 'Ausweichen',
                    'Veteran der Dunklen Welt'],
    },
    manual_handicaps=['Arrogant', 'Ehrgeizig', 'Verpflichtung_leicht'],
    manual_talente=['Wolfsjäger', 'Bodenständig', 'Kampfreflexe', 'Ausweichen',
                    'Veteran der Dunklen Welt'],
    manual_maechte=[],
    ausruestung_plan=[('Silberkugeln (10)', 1), ('Silberdolch', 1),
                      ('Holzpfähle (5)', 1), ('Knoblauch (Bund)', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Jacob-Whitlock_A.json',
    log_path='logs/build_rippers_whitlock.log',
    bericht_path='logs/build_rippers_whitlock_bericht.json',
)


# =============================================================================
# 6. ESMERALDA DALCA — Old Worlder (Romanian Vampire Hunter, Alchemist)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 6: Esmeralda Dalca ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Esmeralda Dalca',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'AH (Alchemist, Horror)',
        'attribute': {'Geschicklichkeit': 6, 'Stärke': 6, 'Konstitution': 6, 'Verstand': 8, 'Willenskraft': 8},
        'fertigkeiten': {'Naturwissenschaften': 8, 'Wissen (Rippertech)': 8,
                        'Recherche': 6, 'Wahrnehmung': 6,
                        'Überreden': 6, 'Heilen': 4, 'Kämpfen': 4, 'Schießen': 4,
                        'Sprache': 6, 'Allgemeinwissen': 6},
        'handicaps': ['Außenseiter', 'Geheimnis_schwer', 'Verpflichtung_schwer'],
        'talente': ['AH (Alchemist, Horror)', 'Arkaner Drogist', 'Aus härterem Holz',
                    'Bodenständig', 'Veteran der Dunklen Welt'],
        'maechte': ['Elementarmanipulation', 'Linderung', 'Heilung', 'Geräusch/Stille'],
    },
    manual_handicaps=['Außenseiter', 'Geheimnis_schwer', 'Verpflichtung_schwer'],
    manual_talente=['AH (Alchemist, Horror)', 'Arkaner Drogist', 'Aus härterem Holz',
                    'Bodenständig', 'Veteran der Dunklen Welt'],
    manual_maechte=['Elementarmanipulation', 'Linderung', 'Heilung', 'Geräusch/Stille'],
    ausruestung_plan=[('EMF-Detektor', 1), ('Geisterjägerpaket', 1),
                      ('Silberkugeln (10)', 1), ('Knoblauchkugeln (10)', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Esmeralda-Dalca_A.json',
    log_path='logs/build_rippers_dalca.log',
    bericht_path='logs/build_rippers_dalca_bericht.json',
)


# =============================================================================
# 7. MUSTAPHA EL-AMIN — Scholar (Egyptian)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 7: Mustapha El-Amin ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Mustapha El-Amin',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Gelehrter',
        'attribute': {'Geschicklichkeit': 6, 'Stärke': 6, 'Konstitution': 6, 'Verstand': 10, 'Willenskraft': 6},
        'fertigkeiten': {'Allgemeinwissen': 8, 'Recherche': 8, 'Sprache': 8, 'Geisteswissenschaften': 8,
                        'Wissen (Rippertech)': 6, 'Überreden': 6, 'Wahrnehmung': 6,
                        'Okkultismus': 6, 'Naturwissenschaften': 4, 'Kämpfen': 4},
        'handicaps': ['Neugierig', 'Geheimnis', 'Pflichtbewusst_leicht'],
        'talente': ['Gelehrter', 'McGyver', 'Bastler', 'Kenne deinen Feind', 'Mystischer Pakt'],
    },
    manual_handicaps=['Neugierig', 'Geheimnis', 'Pflichtbewusst_leicht'],
    manual_talente=['Gelehrter', 'McGyver', 'Bastler', 'Kenne deinen Feind', 'Mystischer Pakt'],
    manual_maechte=[],
    ausruestung_plan=[('Geisterjägerpaket', 1), ('EMF-Detektor', 1),
                      ('UV-Kugeln (10)', 1), ('Weihwasser (Flasche)', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Mustapha-El-Amin_A.json',
    log_path='logs/build_rippers_amin.log',
    bericht_path='logs/build_rippers_amin_bericht.json',
)


# =============================================================================
# 8. JONATHAN WILLIAMS — Witch Hunter (American, Anti-Magic)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 8: Jonathan Williams ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Jonathan Williams',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Wolfsjäger',
        'attribute': {'Geschicklichkeit': 8, 'Stärke': 8, 'Konstitution': 6, 'Verstand': 6, 'Willenskraft': 8},
        'fertigkeiten': {'Kämpfen': 8, 'Schießen': 6, 'Wahrnehmung': 6, 'Glaube': 6,
                        'Athletik': 6, 'Einschüchtern': 6, 'Überleben': 4,
                        'Allgemeinwissen': 4, 'Überreden': 4, 'Okkultismus': 4},
        'handicaps': ['Ehrenkodex', 'Eiferer', 'Missionar_leicht'],
        'talente': ['Wolfsjäger', 'Kampfreflexe', 'Schnelles Ausweichen',
                    'Lied des Heiligen Georg', 'Gerechter Zorn'],
    },
    manual_handicaps=['Ehrenkodex', 'Eiferer', 'Missionar_leicht'],
    manual_talente=['Wolfsjäger', 'Kampfreflexe', 'Schnelles Ausweichen',
                    'Lied des Heiligen Georg', 'Gerechter Zorn'],
    manual_maechte=[],
    ausruestung_plan=[('Vampirjäger-Armbrust', 1), ('Silberkugeln (10)', 1),
                      ('Holzpfähle (5)', 1), ('Weihwasser (Flasche)', 1),
                      ('Heiliges Symbol', 1), ('Knoblauch (Bund)', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Jonathan-Williams_A.json',
    log_path='logs/build_rippers_williams.log',
    bericht_path='logs/build_rippers_williams_bericht.json',
)


# =============================================================================
# 9. DIE SUFFRAGETTE (Akrobatin, Masked Crusader)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 9: Die Suffragette ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Die Suffragette',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Akrobat',
        'attribute': {'Geschicklichkeit': 10, 'Stärke': 6, 'Konstitution': 6, 'Verstand': 6, 'Willenskraft': 6},
        'fertigkeiten': {'Athletik': 8, 'Kämpfen': 8, 'Heimlichkeit': 6, 'Wahrnehmung': 6,
                        'Schießen': 4, 'Überreden': 6, 'Provozieren': 4,
                        'Allgemeinwissen': 4},
        'handicaps': ['Impulsiv', 'Selbstjustiz', 'Eitel'],
        'talente': ['Akrobat', 'Kampfakrobat', 'Flink', 'Erstschlag', 'Parkour'],
    },
    manual_handicaps=['Impulsiv', 'Selbstjustiz', 'Eitel'],
    manual_talente=['Akrobat', 'Kampfakrobat', 'Flink', 'Erstschlag', 'Parkour'],
    manual_maechte=[],
    ausruestung_plan=[('Geisterjägerpaket', 1), ('Silberdolch', 1),
                      ('Holzpfähle (5)', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Die-Suffragette_A.json',
    log_path='logs/build_rippers_suffragette.log',
    bericht_path='logs/build_rippers_suffragette_bericht.json',
)


# =============================================================================
# 10. DER YANKEE (Tüftler / Masked Crusader)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 10: Der Yankee ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Der Yankee',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Bastler',
        'attribute': {'Geschicklichkeit': 8, 'Stärke': 6, 'Konstitution': 6, 'Verstand': 8, 'Willenskraft': 6},
        'fertigkeiten': {'Reparieren': 8, 'Wissen (Rippertech)': 6,
                        'Naturwissenschaften': 6, 'Schießen': 6, 'Wahrnehmung': 6,
                        'Kämpfen': 4, 'Athletik': 4, 'Allgemeinwissen': 4,
                        'Überreden': 4, 'Heimlichkeit': 4},
        'handicaps': ['Eitel', 'Arrogant', 'Missionar_leicht'],
        'talente': ['Bastler', 'McGyver', 'Tarnidentität', 'Kampfreflexe'],
    },
    manual_handicaps=['Eitel', 'Arrogant', 'Missionar_leicht'],
    manual_talente=['Bastler', 'McGyver', 'Tarnidentität', 'Kampfreflexe'],
    manual_maechte=[],
    ausruestung_plan=[('Vampirjäger-Armbrust', 1), ('UV-Granate', 2),
                      ('Bewegungsmelder', 1), ('Geisterfalle', 1), ('Geisterjägerpaket', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Der-Yankee_A.json',
    log_path='logs/build_rippers_yankee.log',
    bericht_path='logs/build_rippers_yankee_bericht.json',
)


# =============================================================================
# 11. VATER McBAIN (Anführer-Geistlicher, Orden des Heiligen Georg)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 11: Vater McBain ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Vater McBain',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Anführer',
        'attribute': {'Geschicklichkeit': 6, 'Stärke': 6, 'Konstitution': 6, 'Verstand': 6, 'Willenskraft': 8},
        'fertigkeiten': {'Glaube': 10, 'Überreden': 8, 'Wahrnehmung': 6, 'Kämpfen': 6,
                        'Heilen': 6, 'Allgemeinwissen': 6, 'Sprache': 6,
                        'Einschüchtern': 6, 'Überleben': 4},
        'handicaps': ['Ehrenkodex', 'Pflichtbewusst_leicht', 'Verpflichtung_schwer', 'Schwur_leicht'],
        'talente': ['AH (Priester)', 'Anführer', 'Auserwählter',
                    'Heiliger/Unheiliger Krieger', 'Lied des Heiligen Georg'],
        'maechte': ['Heilung', 'Schutz', 'Linderung', 'Bannung', 'Geistersicht'],
    },
    manual_handicaps=['Ehrenkodex', 'Pflichtbewusst_leicht', 'Verpflichtung_schwer'],
    manual_talente=['AH (Priester)', 'Anführer', 'Auserwählter',
                    'Heiliger/Unheiliger Krieger', 'Lied des Heiligen Georg'],
    manual_maechte=['Heilung', 'Schutz', 'Linderung', 'Bannung', 'Geistersicht'],
    ausruestung_plan=[('Heiliges Symbol', 1), ('Weihwasser (Flasche)', 2),
                      ('Holzpfähle (5)', 1), ('Silberkugeln (10)', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Vater-McBain_A.json',
    log_path='logs/build_rippers_mcbain.log',
    bericht_path='logs/build_rippers_mcbain_bericht.json',
)


# =============================================================================
# 12. TARA LaGRANGE (Venator-Anführerin, Amerikanerin)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 12: Tara LaGrange ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Tara LaGrange',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Anführer',
        'attribute': {'Geschicklichkeit': 8, 'Stärke': 8, 'Konstitution': 6, 'Verstand': 6, 'Willenskraft': 8},
        'fertigkeiten': {'Schießen': 8, 'Kämpfen': 8, 'Reiten': 6, 'Wahrnehmung': 6,
                        'Athletik': 6, 'Überreden': 6, 'Überleben': 6,
                        'Allgemeinwissen': 4, 'Einschüchtern': 4},
        'handicaps': ['Pflichtbewusst_leicht', 'Missionar_leicht', 'Verpflichtung_leicht'],
        'talente': ['Anführer', 'Kampfreflexe', 'Ausweichen', 'Schnelles Ausweichen',
                    'Wolfsjäger', 'Veteran der Dunklen Welt'],
    },
    manual_handicaps=['Pflichtbewusst_leicht', 'Missionar_leicht', 'Verpflichtung_leicht'],
    manual_talente=['Anführer', 'Kampfreflexe', 'Ausweichen', 'Schnelles Ausweichen',
                    'Wolfsjäger', 'Veteran der Dunklen Welt'],
    manual_maechte=[],
    ausruestung_plan=[('Silberkugeln (10)', 2), ('Silberdolch', 1),
                      ('Holzpfähle (5)', 1), ('Salz (5kg Sack)', 1),
                      ('Vampirjäger-Armbrust', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Tara-LaGrange_A.json',
    log_path='logs/build_rippers_lagrange.log',
    bericht_path='logs/build_rippers_lagrange_bericht.json',
)


# =============================================================================
# 13. DR. JACK (Rosenkreuzer-Wissenschaftler, Rippertech-Erfinder)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 13: Dr. Jack ===\n" + "=" * 70)
baue(
    setting='Rippers', name='Dr. Jack',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'AH (Magie)',
        'attribute': {'Geschicklichkeit': 6, 'Stärke': 6, 'Konstitution': 6, 'Verstand': 10, 'Willenskraft': 6},
        'fertigkeiten': {'Wissen (Rippertech)': 10, 'Naturwissenschaften': 8, 'Reparieren': 6,
                        'Heilen': 6, 'Recherche': 6, 'Wahrnehmung': 6, 'Allgemeinwissen': 6,
                        'Geisteswissenschaften': 6, 'Sprache': 4, 'Überreden': 4,
                        'Okkultismus': 4},
        'handicaps': ['Arrogant', 'Selbstjustiz', 'Geheimnis_schwer'],
        'talente': ['AH (Magie)', 'Rippertech', 'McGyver', 'Bastler', 'Arkaner Drogist',
                    'Mystischer Pakt', 'Bodenständig'],
        'maechte': ['Elementarmanipulation', 'Heilung', 'Linderung',
                    'Arkaner Schutz', 'Arkanes entdecken/verbergen'],
    },
    manual_handicaps=['Arrogant', 'Selbstjustiz', 'Geheimnis_schwer'],
    manual_talente=['AH (Magie)', 'Rippertech', 'McGyver', 'Bastler', 'Arkaner Drogist',
                    'Mystischer Pakt', 'Bodenständig'],
    manual_maechte=['Elementarmanipulation', 'Heilung', 'Linderung', 'Arkaner Schutz',
                    'Arkanes entdecken/verbergen'],
    ausruestung_plan=[('EMF-Detektor', 1), ('Geisterjägerpaket', 1),
                      ('Bewegungsmelder', 2), ('UV-Granate', 1),
                      ('Silberkugeln (10)', 1)],
    save_path='chars/Archetypen/Archetyp_Rippers_Dr-Jack_A.json',
    log_path='logs/build_rippers_jack.log',
    bericht_path='logs/build_rippers_jack_bericht.json',
)


m("\n=== ALLE 13 ARCHETYPEN FERTIG ===")
