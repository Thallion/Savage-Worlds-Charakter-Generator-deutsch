"""Build alle 50F-Archetypen (13 total) — v6 mit korrigierten Keys."""
import sys
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
from functions.character_advancement import increase_aufstiege

tlog = open('logs/build_50f_trace.txt', 'w', encoding='utf-8')
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

    for mm in manual_maechte:
        s.macht(mm, ignore_rang_check=True)

    if n_aufstiege > 0:
        s.ch.char_gen_completed = True
        for _ in range(n_aufstiege):
            increase_aufstiege(s.ch)
        m(f"  [{name}] → {n_aufstiege} Aufstiege, Rang={s.ch.rang}")

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
# 1. PIRAT (Mensch) — Fies (statt Arrogant)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 1: Pirat ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Pirat',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Flink',
        'attribute': {'Geschicklichkeit': 8, 'Stärke': 8, 'Konstitution': 6, 'Verstand': 6, 'Willenskraft': 6},
        'fertigkeiten': {'Kämpfen': 8, 'Schießen': 8, 'Seefahrt': 6, 'Athletik': 6,
                        'Heimlichkeit': 6, 'Wahrnehmung': 6, 'Einschüchtern': 6,
                        'Allgemeinwissen': 4, 'Diebeskunst': 4},
        'handicaps': ['Gezeichnet', 'Blutrünstig', 'Fies', 'Gierig_leicht'],
        'talente': ['Flink', 'Beute!', 'Block', 'Kampfreflexe', 'Schnelles Ausweichen'],
    },
    manual_handicaps=['Gezeichnet', 'Blutrünstig', 'Fies', 'Gierig_leicht'],
    manual_talente=['Flink', 'Beute!', 'Block', 'Kampfreflexe', 'Schnelles Ausweichen'],
    manual_maechte=[],
    ausruestung_plan=[('Entermesser', 1), ('Steinschlosspistole', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Pirat_A.json',
    log_path='logs/build_50f_pirat.log',
    bericht_path='logs/build_50f_pirat_bericht.json',
)


# =============================================================================
# 2. WALFÄNGER (Grael)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 2: Walfänger ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Walfänger',
    soll={
        'volk': 'Grael',
        'attribute': {'Stärke': 10, 'Konstitution': 8, 'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 6},
        'fertigkeiten': {'Seefahrt': 8, 'Athletik': 8, 'Wahrnehmung': 6,
                        'Kämpfen': 6, 'Überleben': 6, 'Überreden': 4},
        'handicaps': ['Loyal', 'Arrogant'],
        'talente': ['Walfänger', 'Sturmjäger', 'Windsinn'],
    },
    manual_handicaps=['Loyal', 'Arrogant'],
    manual_talente=['Walfänger', 'Sturmjäger', 'Windsinn'],
    manual_maechte=[],
    ausruestung_plan=[('Harpune_Fernkampf', 1), ('Entermesser', 1), ('Seil, Hanf (20 Meter)', 1),
                      ('Öl (0,5 l)', 1), ('Lederwams', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Walfaenger_A.json',
    log_path='logs/build_50f_walfaenger.log',
    bericht_path='logs/build_50f_walfaenger_bericht.json',
)


# =============================================================================
# 3. ELEMENTARMAGIER (Mensch) — Wassermagier
# =============================================================================
m("=" * 70 + "\n=== Archetyp 3: Elementarmagier ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Elementarmagier',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'AH (Elementarmagie)',
        'attribute': {'Verstand': 8, 'Willenskraft': 8, 'Geschicklichkeit': 6, 'Konstitution': 4, 'Stärke': 4},
        'fertigkeiten': {'Zaubern': 8, 'Wahrnehmung': 6, 'Allgemeinwissen': 6,
                        'Überreden': 6, 'Athletik': 4, 'Heimlichkeit': 4},
        'handicaps': ['Geheimnis', 'Arrogant'],
        'talente': ['AH (Elementarmagie)', 'Elementarmeisterschaft', 'Arkane Stärkung'],
        'maechte': ['Elementarmanipulation', 'Linderung', 'Heilung'],
    },
    manual_handicaps=['Geheimnis', 'Arrogant'],
    manual_talente=['Elementarmeisterschaft', 'Arkane Stärkung'],
    manual_maechte=['Elementarmanipulation', 'Linderung', 'Heilung'],
    ausruestung_plan=[('Alchemistentasche', 1), ('Buch', 1), ('Tinte (Fläschchen)', 1),
                      ('Feder', 1), ('Robe mit Kapuze', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Elementarmagier_A.json',
    log_path='logs/build_50f_magier.log',
    bericht_path='logs/build_50f_magier_bericht.json',
)


# =============================================================================
# 4. SEEFFIZIER (Mensch) — Kieranischer Kapitän
# =============================================================================
m("=" * 70 + "\n=== Archetyp 4: Seeoffizier ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Seeoffizier',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Anführer',
        'attribute': {'Verstand': 8, 'Willenskraft': 8, 'Geschicklichkeit': 6, 'Konstitution': 6, 'Stärke': 6},
        'fertigkeiten': {'Seefahrt': 10, 'Einschüchtern': 8, 'Überreden': 6,
                        'Wahrnehmung': 6, 'Allgemeinwissen': 6, 'Athletik': 6,
                        'Kämpfen': 6, 'Überleben': 4},
        'handicaps': ['Loyal', 'Arrogant'],
        'talente': ['Anführer', 'Erfahrener Kapitän', 'Rammgeschwindigkeit!', 'Sturmjäger'],
    },
    manual_handicaps=['Loyal', 'Arrogant'],
    manual_talente=['Erfahrener Kapitän', 'Rammgeschwindigkeit!', 'Sturmjäger'],
    manual_maechte=[],
    ausruestung_plan=[('Entermesser', 1), ('Steinschlosspistole', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Seeoffizier_A.json',
    log_path='logs/build_50f_seeoffizier.log',
    bericht_path='logs/build_50f_seeoffizier_bericht.json',
)


# =============================================================================
# 5. BÜCHSENMACHER (Mensch)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 5: Büchsenmacher ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Büchsenmacher',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Bastler',
        'attribute': {'Verstand': 8, 'Geschicklichkeit': 6, 'Willenskraft': 6, 'Konstitution': 6, 'Stärke': 6},
        'fertigkeiten': {'Reparieren': 8, 'Naturwissenschaften': 8, 'Allgemeinwissen': 6,
                        'Wahrnehmung': 6, 'Überreden': 4, 'Heimlichkeit': 4,
                        'Kämpfen': 4},
        'handicaps': ['Schlechte Augen', 'Ehrenkodex'],
        'talente': ['Bastler', 'Büchsenmacher', 'Glück', 'Schnelle Heilung'],
    },
    manual_handicaps=['Schlechte Augen', 'Ehrenkodex'],
    manual_talente=['Büchsenmacher', 'Glück', 'Schnelle Heilung'],
    manual_maechte=[],
    ausruestung_plan=[('Büchsenmacherwerkzeug', 1), ('Entermesser', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Buechsenmacher_A.json',
    log_path='logs/build_50f_buechsenmacher.log',
    bericht_path='logs/build_50f_buechsenmacher_bericht.json',
)


# =============================================================================
# 6. ATANI-KUNDSCHAFTER (Atani) — kein Scharfschütze in 50F, nehme Volltreffer
# =============================================================================
m("=" * 70 + "\n=== Archetyp 6: Atani-Kundschafter ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Atani-Kundschafter',
    soll={
        'volk': 'Atani',
        'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Konstitution': 6, 'Stärke': 4},
        'fertigkeiten': {'Athletik': 8, 'Wahrnehmung': 8, 'Heimlichkeit': 6,
                        'Überleben': 6, 'Schießen': 6, 'Kämpfen': 4,
                        'Allgemeinwissen': 4, 'Recherche': 4},
        'handicaps': ['Neugierig', 'Jung'],
        'talente': ['Kundschafter', 'Volltreffer', 'Flink', 'Akrobat'],
    },
    manual_handicaps=['Neugierig', 'Jung'],
    manual_talente=['Kundschafter', 'Volltreffer', 'Flink', 'Akrobat'],
    manual_maechte=[],
    ausruestung_plan=[('Bogen', 1), ('Kurzbogen', 1), ('Seil, Hanf (10 Meter)', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Atani-Kundschafter_A.json',
    log_path='logs/build_50f_atani.log',
    bericht_path='logs/build_50f_atani_bericht.json',
)


# =============================================================================
# 7. SCHWARZPULVER-MUSKETIER (Mensch) — kein Scharfschütze, nehme Volltreffer
# =============================================================================
m("=" * 70 + "\n=== Archetyp 7: Schwarzpulver-Musketier ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Schwarzpulver-Musketier',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Volltreffer',
        'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Konstitution': 6, 'Stärke': 6},
        'fertigkeiten': {'Schießen': 10, 'Athletik': 6, 'Wahrnehmung': 6,
                        'Kämpfen': 6, 'Reparieren': 4, 'Allgemeinwissen': 4,
                        'Überleben': 4},
        'handicaps': ['Arrogant', 'Rachsüchtig_leicht'],
        'talente': ['Volltreffer', 'Musketier', 'Kampfreflexe', 'Schnelles Ausweichen'],
    },
    manual_handicaps=['Arrogant', 'Rachsüchtig_leicht'],
    manual_talente=['Musketier', 'Kampfreflexe', 'Schnelles Ausweichen'],
    manual_maechte=[],
    ausruestung_plan=[('Muskete', 1), ('Pulverhorn', 1), ('Kugeln (10)', 1), ('Steinschlosspistole', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Schwarzpulver-Musketier_A.json',
    log_path='logs/build_50f_musketier.log',
    bericht_path='logs/build_50f_musketier_bericht.json',
)


# =============================================================================
# 8. KRAKENKRIEGER (Kraken) — Willenskraft W4 reicht
# =============================================================================
m("=" * 70 + "\n=== Archetyp 8: Krakenkrieger ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Krakenkrieger',
    soll={
        'volk': 'Kraken',
        'attribute': {'Stärke': 8, 'Konstitution': 8, 'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 4},
        'fertigkeiten': {'Kämpfen': 8, 'Athletik': 8, 'Heimlichkeit': 6,
                        'Wahrnehmung': 6, 'Allgemeinwissen': 4, 'Überleben': 4,
                        'Einschüchtern': 4},
        'handicaps': ['Blutrünstig', 'Loyal'],
        'talente': ['Krakenknochenschwert und -rüstung', 'Kampfreflexe', 'Kampfakrobat'],
    },
    manual_handicaps=['Blutrünstig', 'Loyal'],
    manual_talente=['Krakenknochenschwert und -rüstung', 'Kampfreflexe', 'Kampfakrobat'],
    manual_maechte=[],
    ausruestung_plan=[('Krakenknochenrüstung', 1), ('Krummsäbel', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Krakenkrieger_A.json',
    log_path='logs/build_50f_kraken.log',
    bericht_path='logs/build_50f_kraken_bericht.json',
)


# =============================================================================
# 9. DOREEN-INFILTRATOR (Doreen) — kein Diebeskunst-Talent, nehme Assassine
# =============================================================================
m("=" * 70 + "\n=== Archetyp 9: Doreen-Infiltrator ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Doreen-Infiltrator',
    soll={
        'volk': 'Doreen',
        'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Konstitution': 6, 'Stärke': 6},
        'fertigkeiten': {'Heimlichkeit': 8, 'Diebeskunst': 8, 'Kämpfen': 6,
                        'Wahrnehmung': 6, 'Athletik': 6, 'Überreden': 4,
                        'Allgemeinwissen': 4},
        'handicaps': ['Geheimnis', 'Gierig_leicht'],
        'talente': ['Schmutziger Kämpfer', 'Flink', 'Ausweichen', 'Assassine'],
    },
    manual_handicaps=['Geheimnis', 'Gierig_leicht'],
    manual_talente=['Schmutziger Kämpfer', 'Flink', 'Ausweichen', 'Assassine'],
    manual_maechte=[],
    ausruestung_plan=[('Messer', 1), ('Dietrich-Set', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Doreen-Infiltrator_A.json',
    log_path='logs/build_50f_doreen.log',
    bericht_path='logs/build_50f_doreen_bericht.json',
)


# =============================================================================
# 10. SCURILLIAN-SCHMUGGLER (Scurillian) — Volltreffer statt Scharfschütze
# =============================================================================
m("=" * 70 + "\n=== Archetyp 10: Scurillian-Schmuggler ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Scurillian-Schmuggler',
    soll={
        'volk': 'Scurillian',
        'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Konstitution': 6, 'Stärke': 6},
        'fertigkeiten': {'Heimlichkeit': 8, 'Wahrnehmung': 8, 'Diebeskunst': 6,
                        'Kämpfen': 6, 'Überreden': 6, 'Allgemeinwissen': 4,
                        'Athletik': 4},
        'handicaps': ['Fies', 'Gierig_leicht'],
        'talente': ['Flink', 'Volltreffer', 'Glück', 'Schmutziger Kämpfer'],
    },
    manual_handicaps=['Fies', 'Gierig_leicht'],
    manual_talente=['Flink', 'Volltreffer', 'Glück', 'Schmutziger Kämpfer'],
    manual_maechte=[],
    ausruestung_plan=[('Armbrust, Leichte', 1), ('Bolzen (10)', 1), ('Messer', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Scurillian-Schmuggler_A.json',
    log_path='logs/build_50f_scurillian.log',
    bericht_path='logs/build_50f_scurillian_bericht.json',
)


# =============================================================================
# 11. SCHATZJÄGER (Mensch)
# =============================================================================
m("=" * 70 + "\n=== Archetyp 11: Schatzjäger ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Schatzjäger',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Glück',
        'attribute': {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Konstitution': 6, 'Stärke': 6},
        'fertigkeiten': {'Wahrnehmung': 8, 'Allgemeinwissen': 8, 'Athletik': 6,
                        'Überleben': 6, 'Heimlichkeit': 6, 'Kämpfen': 4,
                        'Schießen': 4, 'Überreden': 4},
        'handicaps': ['Gierig_leicht', 'Neugierig'],
        'talente': ['Glück', 'Schatzjäger', 'Flink', 'Akrobat'],
    },
    manual_handicaps=['Gierig_leicht', 'Neugierig'],
    manual_talente=['Schatzjäger', 'Flink', 'Akrobat'],
    manual_maechte=[],
    ausruestung_plan=[('Entermesser', 1), ('Steinschlosspistole', 1), ('Seil, Hanf (10 Meter)', 1),
                      ('Laterne', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Schatzjaeger_A.json',
    log_path='logs/build_50f_schatzjaeger.log',
    bericht_path='logs/build_50f_schatzjaeger_bericht.json',
)


# =============================================================================
# 12. MATROSE (Mensch) — kein Ausdauernd, nehme Zäher als Leder
# =============================================================================
m("=" * 70 + "\n=== Archetyp 12: Matrose ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Matrose',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'Kielratte',
        'attribute': {'Geschicklichkeit': 8, 'Konstitution': 6, 'Willenskraft': 6, 'Stärke': 6, 'Verstand': 6},
        'fertigkeiten': {'Seefahrt': 8, 'Athletik': 8, 'Wahrnehmung': 6,
                        'Kämpfen': 6, 'Überleben': 4, 'Allgemeinwissen': 4,
                        'Heimlichkeit': 4, 'Überreden': 4},
        'handicaps': ['Loyal', 'Arrogant'],
        'talente': ['Kielratte', 'Kletteräffchen', 'Flink', 'Zäher als Leder'],
    },
    manual_handicaps=['Loyal', 'Arrogant'],
    manual_talente=['Kletteräffchen', 'Flink', 'Zäher als Leder'],
    manual_maechte=[],
    ausruestung_plan=[('Entermesser', 1), ('Seil, Hanf (20 Meter)', 1), ('Öl (0,5 l)', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Matrose_A.json',
    log_path='logs/build_50f_matrose.log',
    bericht_path='logs/build_50f_matrose_bericht.json',
)


# =============================================================================
# 13. WINDMAGIER (Mensch) — Eigenheit → Angewohnheit
# =============================================================================
m("=" * 70 + "\n=== Archetyp 13: Windmagier ===\n" + "=" * 70)
baue(
    setting='50 Fathoms', name='Windmagier',
    soll={
        'volk': 'Mensch', 'volk_freies_talent': 'AH (Elementarmagie)',
        'attribute': {'Verstand': 8, 'Willenskraft': 8, 'Geschicklichkeit': 6, 'Konstitution': 4, 'Stärke': 4},
        'fertigkeiten': {'Zaubern': 8, 'Seefahrt': 6, 'Wahrnehmung': 6,
                        'Allgemeinwissen': 6, 'Überreden': 4, 'Athletik': 4,
                        'Überleben': 4},
        'handicaps': ['Geheimnis', 'Angewohnheit_leicht'],
        'talente': ['AH (Elementarmagie)', 'Sturmjäger', 'Windsinn', 'Arkane Stärkung'],
        'maechte': ['Elementarmanipulation', 'Geräusch/Stille', 'Schutz vor Naturgewalten'],
    },
    manual_handicaps=['Geheimnis', 'Angewohnheit_leicht'],
    manual_talente=['Sturmjäger', 'Windsinn', 'Arkane Stärkung'],
    manual_maechte=['Elementarmanipulation', 'Geräusch/Stille', 'Schutz vor Naturgewalten'],
    ausruestung_plan=[('Robe mit Kapuze', 1), ('Buch', 1), ('Tinte (Fläschchen)', 1),
                      ('Feder', 1), ('Alchemistentasche', 1)],
    save_path='chars/Archetypen/Archetyp_50_Fathoms_Windmagier_A.json',
    log_path='logs/build_50f_windmagier.log',
    bericht_path='logs/build_50f_windmagier_bericht.json',
)


m("=" * 70 + "\n=== ALLE 13 ARCHETYPEN FERTIG ===\n" + "=" * 70)
tlog.close()
