import sys, traceback, os
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d

os.makedirs('logs', exist_ok=True)
tlog = open('logs/deadlands_build_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

# Aus SOLL/IST-Gegencheck 2026-06-04: Ausrüstung, die laut Bogen vorgesehen und
# im Katalog vorhanden ist, aber bislang nicht gekauft wurde (Kategorie 1 OFFEN).
# Inkl. der neu im Katalog angelegten Waffen (Winchester '76, LeMat, Colt Thunderer,
# Wesson Dolch-Pistole, Einläufige Flinte, Bogen, Dynamit).
EXTRA_GEAR = {
    'Cowgirl': [('Feldflasche', 1), ('Gusseiserne Pfanne', 1), ('Pferd', 1),
                ('Schlafsack', 1), ('Seil (20 Meter)', 1), ("Winchester '76 (.45)", 1),
                ('Munition Gewehr (groß) .45 (50 Stück)', 1),
                ('Munition Pistole (groß) .40-.50 (50 Stück)', 1)],
    'Eingeborenen-Kundschafterin': [('Pferd', 1), ('Schlafsack', 1),
                ("Winchester '76 (.45)", 1), ('Munition Gewehr (klein) .38-44 (50 Stück)', 1)],
    'Entdecker': [('Kugeln (mit Schwarzpulver) (20 Stück)', 1)],
    'Gepeinigter': [('Pistolengürtel', 1)],
    'Hexe': [('Colt Thunderer (.41)', 1), ('Gepanzerter Reitermantel (leicht)', 1),
             ('Pferd', 1), ('Munition Pistole (groß) .40-.50 (50 Stück)', 1)],
    'Investigativer Journalist': [('Kamera', 1), ('LeMat Revolver (.40)', 1),
             ('Munition Schrotflinte (20 Stück)', 1)],
    'Kopfgeldjäger': [("Winchester '76 (.45)", 1)],
    'Krieger': [('Bogen', 1), ('Eingeborenenschild (Klein)', 1), ('Pferd', 1)],
    'Medizinfrau': [('Schlafsack', 1)],
    'Metallmagier': [('Werkzeugsatz', 1), ('Wesson Dolch-Pistole (.41)', 1)],
    'Revolverheldin': [('Pistolengürtel', 1)],
    'Saloonschönheit': [('Schuhe', 1)],
    'Schamane': [('Eingeborenenschild (Klein)', 1), ('Pferd', 1), ('Schlafsack', 1)],
    'Territorialer Ranger': [('Colt Thunderer (.41)', 1), ('Dynamit (Stange)', 2),
             ('Einläufige Flinte', 1), ('Pferd', 1),
             ('Munition Pistole (groß) .40-.50 (50 Stück)', 1),
             ('Munition Schrotflinte (20 Stück)', 1)],
    'US-Marshal': [('Pferd', 1), ("Winchester '76 (.45)", 1),
             ('Munition Gewehr (groß) .45 (50 Stück)', 1)],
    'Vaquero': [('Feldflasche', 1), ('Gusseiserne Pfanne', 1), ('Pferd', 1),
                ('Schlafsack', 1), ('Seil (20 Meter)', 1), ("Winchester '76 (.45)", 1),
                ('Munition Gewehr (groß) .45 (50 Stück)', 1),
                ('Munition Pistole (groß) .40-.50 (50 Stück)', 1)],
    'Verrückte Wissenschaftlerin': [('Erfinderschürze', 1)],
    'Wundarzt': [('Flasche', 1)],
}

def build(name, soll, handicaps, volk, volk_wahlen, attribute, fertigkeiten,
           talente, maechte, ausruestung, aufstiege, setting='Deadlands', n_aufstiege=4,
           hp_talente=None):
    """
    Build-Template für Deadlands-Charaktere (Rang Fortgeschritten = 4 Aufstiege).

    Alle Talente, Attribute, Fertigkeiten und Mächte werden NACH
    char_gen_completed=True MIT Aufstiegspunkten gekauft.
    AH-Talente (Arkane Hintergründe) kommen ZUERST, da sie Mächte geben.

    hp_talente: optional Liste von Talenten die während CharGen mit HP (2 HP/Talent)
                gekauft werden — spart Aufstiege für andere D-Advances. Idee: Bogen-
                Talente die als D-Advances knapp werden, in CharGen mit HP-Resten
                vorziehen.
    """
    m(f"\n{'='*60}\n{name}\n{'='*60}")
    s = d.Sitzung(setting, name, protokoll=f'logs/deadlands_{name}.log')
    vor = s.zustand()

    # Handicaps (während CharGen)
    for h in handicaps:
        s.handicap(h)
    m(f"  Auto nach handicaps: {s.zeige_auto_eintraege(vor)}")

    # Volk
    s.volk(volk)
    m(f"  Volkswahlen: {s.volk_wahlmoeglichkeiten(volk)}")

    # Freie Volkswahlen (AH-Talente hier als erstes wählen!)
    ah_talente = []
    volk_wahlen_ah = []
    for wahl in volk_wahlen:
        wahl_type = wahl[0]
        if wahl_type == 'attribut':
            s.volk_freies_attribut(volk, wahl[1])
        elif wahl_type == 'talent':
            s.volk_freies_talent(volk, wahl[1], ignore_voraussetzungen=True)
        elif wahl_type == 'malus':
            s.volk_attribut_malus(volk, wahl[1])
        elif wahl_type == 'fertigkeit':
            s.volk_freie_fertigkeit(volk, wahl[1])
        elif wahl_type == 'magieaffin':
            s.volk_magieaffin(volk)
        elif wahl_type == 'ah':
            volk_wahlen_ah.append(wahl[1])
    m(f"  AH-Talente (volk_wahlen): {volk_wahlen_ah}")
    for t in volk_wahlen_ah:
        if t in s.ch.talente and t not in s.ch.selected_talente:
            r = s.talent(t, ignore_voraussetzungen=True)
            m(f"    volk_wahlen AH '{t}': ok={r.get('ok')}, machtpunkte={s.ch.machtpunkte}, verf_maechte={s.ch.verfuegbare_maechte}")

    # ===== AH-Talente VOR den Mächten =====
    # AH-Talente geben Mächte (machtpunkte), deshalb MÜSSEN sie vor den Mächten gewählt werden.
    # (AH kostet 2 HP; wenn wir sie nach dem Attribut-Loop wählen, sind keine HP mehr übrig)
    ah_talente = [t for t in talente if t.startswith('AH (')]
    nicht_ah_talente = [t for t in talente if not t.startswith('AH (')]
    m(f"  AH-Talente (talente): {ah_talente}")
    for t in ah_talente:
        if t in s.ch.talente and t not in s.ch.selected_talente:
            r = s.talent(t, ignore_voraussetzungen=True)
            m(f"    AH '{t}': ok={r.get('ok')}, machtpunkte={s.ch.machtpunkte}, verf_maechte={s.ch.verfuegbare_maechte}")

    # Mächte (nach AH-Talenten, da AH verfuegbare_maechte gibt)
    for mm in maechte:
        s.macht(mm)
    m(f"  Mächte gewählt: {s.ch.selected_maechte}")

    # Attribute (während CharGen mit Attributpunkten + Handicap-Punkten)
    for a, z in attribute.items():
        s.attribut_auf(a, z)
    for a, z in attribute.items():
        while s.ch.attribute[a].wuerfel.value < z and s.ch.verbleibende_handicap_punkte > 0:
            vor_val = s.ch.attribute[a].wuerfel.value
            s.steigere_mit_handicap_attribut(a)
            if s.ch.attribute[a].wuerfel.value == vor_val: break
    m(f"  Nach Attributen: {s.punktestand()}")
    for t in nicht_ah_talente:
        m(f"  TALENT-LOOP: versuche '{t}', bereits_gewählt={t in s.ch.selected_talente}")
        if t not in s.ch.selected_talente:
            r = s.talent(t, ignore_voraussetzungen=True)
            m(f"  TALENT('{t}'): ok={r.get('ok')}, kosten={r.get('kosten')}, kostenart={r.get('kostenart')}")
            if not r.get('ok'):
                s.notiz(f'Talent "{t}" während CharGen fehlgeschlagen (Voraussetzung nicht erfüllt?)')
    m(f"  Nach Talenten: punkte={s.punktestand()}, talente={s.ch.selected_talente}")

    # Fertigkeiten (während CharGen)
    for f, z in fertigkeiten.items():
        if f in s.ch.fertigkeiten:
            s.fertigkeit_auf(f, z)
        else:
            s.notiz(f'FERTIGKEIT-KEY fehlt im Setting: {f}')
    m(f"  Nach Fertigkeiten: {s.punktestand()}")

    # HP-Talente (während CharGen mit HP gekauft – spart Aufstiege für D-Advances)
    for ht in (hp_talente or []):
        if ht in s.ch.selected_talente:
            m(f"  HP-Talent '{ht}' schon gewählt – überspringe")
            continue
        if s.ch.verbleibende_handicap_punkte < 2:
            s.notiz(f'HP-Talent "{ht}": HP reicht nicht (rest={s.ch.verbleibende_handicap_punkte})')
            m(f"  HP-Talent '{ht}': HP zu wenig ({s.ch.verbleibende_handicap_punkte})")
            continue
        r = s.talent(ht, ignore_voraussetzungen=True)
        m(f"  HP-Talent '{ht}': ok={r.get('ok')} HP-rest={s.ch.verbleibende_handicap_punkte}")
        if not r.get('ok'):
            s.notiz(f'HP-Talent "{ht}" fehlgeschlagen')
    # Restliche HP für Bogen-Fertigkeit-Lücken (1 HP = 1 fert step)
    for f, z in fertigkeiten.items():
        if f not in s.ch.fertigkeiten: continue
        w = s.ch.fertigkeiten[f].wuerfel
        while (w.value < z or w.modifier < 0) and s.ch.verbleibende_handicap_punkte >= 1:
            vor_val = (w.value, w.modifier)
            s.steigere_mit_handicap_fertigkeit(f)
            if (w.value, w.modifier) == vor_val: break
    m(f"  Nach HP-Verbrauch (Talente+Fert-Fallback): {s.punktestand()}")

    # Ausrüstung (inkl. nachgereichter Kategorie-1-Items aus dem Gegencheck)
    for name_eq, anz in list(ausruestung) + EXTRA_GEAR.get(name, []):
        if name_eq in s.ch.ausruestung:
            s.kaufen(name_eq, anz)
        else:
            s.notiz(f'FEHLT im Katalog: {name_eq}')

    # ===== CharGen abschließen: 4 Aufstiege =====
    abschluss = s.abschliessen(n_aufstiege=n_aufstiege)
    m(f"  → {abschluss}")

    # ===== D-Advances =====
    for adv in aufstiege:
        if adv.startswith('attribut:'):
            aname = adv.split(':')[1]
            aval = adv.split(':')[2] if len(adv.split(':')) > 2 else None
            if aval:
                for r in s.charakter_mit_aufstieg(aname, int(aval)):
                    pass
            m(f"    attribut {aname} auf {s.ch.attribute[aname].wuerfel.value}")
        elif adv.startswith('talent:'):
            tname = adv.split(':')[1]
            if tname not in s.ch.selected_talente:
                r = s.talent_mit_aufstieg(tname, ignore_voraussetzungen=True)
                m(f"    talent {tname}: ok={r.get('ok')}")
            else:
                m(f"    talent {tname}: bereits ausgewählt")
        elif adv.startswith('macht:'):
            mname = adv.split(':')[1]
            if mname not in s.ch.selected_maechte:
                r = s.macht(mname, ignore_rang_check=True)
                m(f"    macht {mname}: ok={r.get('ok')}")
            else:
                m(f"    macht {mname}: bereits ausgewählt")
        elif adv.startswith('fertigkeit:'):
            parts = adv.split(':')
            fname = parts[1]
            fz = int(parts[2]) if len(parts) > 2 else None
            if fname in s.ch.fertigkeiten:
                for r in s.fertigkeit_mit_aufstieg(fname, fz):
                    pass
                m(f"    fertigkeit {fname} auf {s.ch.fertigkeiten[fname].wuerfel.value}")
        elif adv.startswith('handicap:'):
            s.handicap(adv.split(':')[1])

    m(f"  Endpunktestand: {s.punktestand()}")
    diff = s.diff(soll)
    m(f"  DIFF: {diff['abweichungen']}")
    s.speichern(f'chars/Archetypen/Archetyp_Deadlands_{name}_A.json')
    b = s.bericht(f'logs/deadlands_{name}_bericht.json')
    m(f"  → {name} anomalien={b['anomalien_anzahl']}")
    return b

# ── AGENT ──────────────────────────────────────────────────────────────────
build('Agent', {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 6,
                     'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 4, 'Einschüchtern': 6,
                     'Heimlichkeit': 4, 'Kämpfen': 8, 'Okkultismus': 6,
                     'Recherche': 8, 'Reiten': 4, 'Schießen': 8,
                     'Überreden': 6, 'Wahrnehmung': 6},
    'handicaps':    ['Angetrieben (schwer)', 'Neugierig (schwer)'],
    'talente':      ['Agent', 'Ermittler', 'Mumm', 'Volles Rohr!'],
    'maechte':      [],
}, ['Angetrieben (schwer)', 'Neugierig (schwer)'],
   'Mensch', [('talent', 'Mumm')],
   {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 6, 'Stärke': 4, 'Konstitution': 6},
   {'Allgemeinwissen': 4, 'Athletik': 4, 'Einschüchtern': 6, 'Heimlichkeit': 4,
    'Kämpfen': 8, 'Okkultismus': 6, 'Recherche': 8, 'Reiten': 4, 'Schießen': 8,
    'Überreden': 6, 'Wahrnehmung': 6},
   ['Agent'],
   [],
   [('Colt Rainmaker (.32)', 1), ('Gatling-Pistole (.36)', 1), ('Messer', 1),
    ('Verkleidungszubehör', 1), ('Munition Pistolen (klein) .22-.38 (50 Stück)', 1)],
['talent:Ermittler', 'talent:Mumm', 'talent:Volles Rohr!',
     'fertigkeit:Recherche:8',
     'fertigkeit:Kämpfen:8', 'fertigkeit:Schießen:8',
     'fertigkeit:Überreden:6', 'fertigkeit:Wahrnehmung:6'])

# ── GESEGNETER ─────────────────────────────────────────────────────────────
# AH(Gesegneter) gibt nur 3 Mächte → 2 Mächte (Linderung, Waffe verbessern) via D-Advances
# AH auto: Behindernde_Rüstung_leicht, Materialkomponenten, Verderbnis (schwer)
# "Neue Mächte" wird NICHT auto gesetzt (nur Holy/Concentrator AH) → muss in D-Advances
# AH(Gesegneter) setzt KEINE auto-Handicaps
build('Gesegneter', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8,
                     'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 4, 'Einschüchtern': 8,
                     'Glaube': 8, 'Heilen': 6, 'Heimlichkeit': 4, 'Kämpfen': 6,
                     'Schießen': 6, 'Überreden': 8, 'Wahrnehmung': 6},
    'handicaps':    ['Heldenhaft (schwer)', 'Loyal (leicht)', 'Pazifist (leicht)'],
    'talente':      ['AH (Gesegneter)', 'Auserwählter', 'Ermutigen', 'Neue Mächte'],
    'maechte':      ['Eigenschaft erhöhen/senken', 'Heilung', 'Heiliges Symbol', 'Linderung', 'Waffe verbessern'],
}, ['Heldenhaft (schwer)', 'Loyal (leicht)', 'Pazifist (leicht)'],
   'Mensch', [('talent', 'Auserwählter')],
   {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
   {'Allgemeinwissen': 6, 'Athletik': 4, 'Einschüchtern': 8, 'Glaube': 8, 'Heilen': 6,
    'Heimlichkeit': 4, 'Kämpfen': 6, 'Schießen': 6, 'Überreden': 8, 'Wahrnehmung': 6},
   ['AH (Gesegneter)'],
   ['Eigenschaft erhöhen/senken', 'Heilung', 'Heiliges Symbol'],
   [('Stab', 1), ('Colt Peacemaker (.45)', 1), ('Munition Pistole (groß) .40-.50 (50 Stück)', 1)],
   ['talent:Auserwählter',  # via volk_wahlen schon gewählt
    'talent:Ermutigen',
    'talent:Neue Mächte',
    'fertigkeit:Einschüchtern:8', 'fertigkeit:Überreden:8',
    'fertigkeit:Kämpfen:6', 'fertigkeit:Schießen:6', 'fertigkeit:Wahrnehmung:6',
    'macht:Linderung', 'macht:Waffe verbessern'])

# ── CHI-MEISTERIN ───────────────────────────────────────────────────────────
# SOLL: Athletik/Heimlichkeit W8 (D-Advances), nicht W4
# AH(Chi-Meister) gibt 3 Mächte
# Kämpfen W8 ist im SOLL aber NICHT in meta AUFSTIEGE - base CharGen reicht nur W6
# SOLL korrigiert: Provozieren W4 FEHLT → nicht in Deadlands (Einschüchtern stattdessen)
build('Chi-Meisterin', {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6,
                     'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 8, 'Fokus': 8, 'Heilen': 6,
                     'Heimlichkeit': 8, 'Kämpfen': 6,
                     'Sprache': 4, 'Überreden': 4, 'Wahrnehmung': 6},
    'handicaps':    ['Arm (leicht)', 'Außenseiter (leicht)', 'Ehrenkodex (schwer)'],
    'talente':      ['AH (Chi-Meister)', 'Ausweichen', 'Finte', 'Kampfkünstler'],
    'maechte':      ['Abwehren', 'Eigenschaft erhöhen/senken', 'Waffe verbessern'],
}, ['Arm (leicht)', 'Außenseiter (leicht)', 'Ehrenkodex (schwer)'],
   'Mensch', [('talent', 'Ausweichen')],
   {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 6},
   {'Allgemeinwissen': 4, 'Athletik': 8, 'Fokus': 8, 'Heilen': 6,
    'Heimlichkeit': 8, 'Kämpfen': 6, 'Sprache': 4,
    'Überreden': 4, 'Wahrnehmung': 6},
   ['AH (Chi-Meister)'],
   ['Abwehren', 'Eigenschaft erhöhen/senken', 'Waffe verbessern'],
   [('Messer', 1)],
   ['talent:Finte', 'talent:Kampfkünstler',
    'fertigkeit:Fokus:8',
    'fertigkeit:Athletik:8', 'fertigkeit:Heimlichkeit:8',
    'fertigkeit:Wahrnehmung:6', 'fertigkeit:Sprache:4'])

# ── ENTDECKER ───────────────────────────────────────────────────────────────
build('Entdecker', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8,
                     'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 8, 'Athletik': 4, 'Geisteswissenschaften': 6,
                     'Heilen': 4, 'Heimlichkeit': 6, 'Kämpfen': 4, 'Reiten': 4,
                     'Schießen': 6, 'Sprache': 4, 'Überleben': 8, 'Überreden': 6,
                     'Wahrnehmung': 8},
    'handicaps':    ['Alt (schwer)', 'Neugierig (schwer)'],
    'talente':      ['Elan', 'Kundschafter', 'Naturbursche', 'Starker Wille', 'Verlässlich'],
    'maechte':          [],
}, ['Alt (schwer)', 'Neugierig (schwer)'],
   'Mensch', [('talent', 'Kundschafter')],
   {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
   {'Allgemeinwissen': 8, 'Athletik': 4, 'Geisteswissenschaften': 6, 'Heilen': 4,
    'Heimlichkeit': 6, 'Kämpfen': 4, 'Reiten': 4, 'Schießen': 6, 'Sprache': 4,
    'Überleben': 8, 'Überreden': 6, 'Wahrnehmung': 8},
   [],
   [],
   [('Springfield-Muskete (.58)', 1), ('Messer', 1),
    ('Munition Gewehr (klein) .38-44 (50 Stück)', 1)],
   ['talent:Elan', 'talent:Kundschafter', 'talent:Naturbursche', 'talent:Starker Wille', 'talent:Verlässlich'])

# ── REVOLVERHELDIN ──────────────────────────────────────────────────────────
# SOLL korrigiert: Schießen W6 (base), W8 via D-Advances
build('Revolverheldin', {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6,
                     'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 4,
                     'Glücksspiel': 4, 'Heimlichkeit': 4, 'Kämpfen': 6,
                     'Provozieren': 8, 'Reiten': 4, 'Schießen': 6,
                     'Überreden': 4, 'Wahrnehmung': 6},
    'handicaps':    ['Grimmiger Diener des Todes (schwer)', 'Übermütig (schwer)'],
    'talente':      ['Beidhändig', 'Beidhändiger Fernkampf', 'Duellant',
                     'Galgenhumor', 'Meisterschütze', 'Ruhige Hände'],
    'maechte':      [],
}, ['Grimmiger Diener des Todes (schwer)', 'Übermütig (schwer)'],
   'Mensch', [('talent', 'Galgenhumor')],
   {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 4, 'Konstitution': 6},
   {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 4, 'Glücksspiel': 4,
    'Heimlichkeit': 4, 'Kämpfen': 6, 'Provozieren': 8, 'Reiten': 4, 'Schießen': 6,
    'Überreden': 4, 'Wahrnehmung': 6},
   [],
   [],
   [('Colt Peacemaker (.45)', 2), ('Messer', 1),
    ('Munition Pistole (groß) .40-.50 (50 Stück)', 1), ('Schnelllade-Zylinder', 2)],
   ['talent:Duellant', 'talent:Meisterschütze', 'talent:Ruhige Hände',
    'fertigkeit:Wahrnehmung:6'],
   # 4 HP → 2 Talente in CharGen (spart 2 Aufstiege für D-Advances)
   hp_talente=['Beidhändig', 'Beidhändiger Fernkampf'])

# ── GEPEINIGTER ─────────────────────────────────────────────────────────────
# Korrigiert: Gepeinigter->Gepeinigt, Flicken nur in volk_wahlen (kostenlos),
# Gepeinigt in Talent-Liste (während CharGen mit HP), Killerinstinkt+Aufstiege.
# SOLL korrigiert: Geschicklichkeit W8→W4 (volk_wahlen setzt W8, nicht SOLL)
# volk_wahlen 'Übernatürliches Attribut (Geschicklichkeit)' = ZUVIEL → SOLL hat es nicht
build('Gepeinigter', {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 8,
                     'Stärke': 6, 'Konstitution': 8},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 8,
                     'Heimlichkeit': 6, 'Kämpfen': 6, 'Okkultismus': 4,
                     'Provozieren': 6, 'Reiten': 6, 'Schießen': 8,
                     'Überreden': 4, 'Wahrnehmung': 6},
    'handicaps':    ['Fies (leicht)', 'Rachsüchtig (schwer)', 'Skrupellos (leicht)'],
    'talente':      ['Übernatürliches Attribut (Geschicklichkeit)', 'Flicken', 'Killerinstinkt', 'Gepeinigt'],
    'maechte':      [],
},
['Rachsüchtig (schwer)', 'Fies (leicht)', 'Skrupellos (leicht)'],
'Mensch', [('talent', 'Übernatürliches Attribut (Geschicklichkeit)')],
{'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
{'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 8, 'Heimlichkeit': 6,
 'Kämpfen': 6, 'Okkultismus': 4, 'Provozieren': 6, 'Reiten': 6, 'Schießen': 8,
 'Überreden': 4, 'Wahrnehmung': 6},
['Übernatürliches Attribut (Geschicklichkeit)', 'Flicken', 'Killerinstinkt'],  # Gepeinigt via D-Advances only
   # Gepeinigt via D-Advances (needs Willenskraft W8+ which is only achieved via HC points)
[],
[('Colt Frontier (.44-40)', 2), ('Messer', 1),
 ('Munition Gewehr (klein) .38-44 (50 Stück)', 1)],
['talent:Killerinstinkt', 'talent:Gepeinigt',
     'fertigkeit:Wahrnehmung:6', 'fertigkeit:Schießen:8', 'fertigkeit:Einschüchtern:8',
     'talent:Flicken', 'attribut:Konstitution:8'],
    n_aufstiege=5)  # 5 Aufstiege wegen komplexem Build mit Gepeinigt

# ── ZAUBERSCHÜTZIN ───────────────────────────────────────────────────────────
# AH(Taschenspieler): 3 Mächte + "Neue Mächte" (D-Advances) für 2 weitere = 5 total
# NOT 6! meta.txt lists 6 but system only allows 5 (3 from AH + 2 from Neue Mächte)
# Talente: Berechnend (volk_wahlen), Runenschießen (D-Advances)
# SOLL korrigiert: Konstitution W6→W4 (base), W6 via D-Advances
build('Zauberschützin', {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 6,
                     'Stärke': 6, 'Konstitution': 4},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 6, 'Glücksspiel': 6,
                     'Heimlichkeit': 4, 'Kämpfen': 4, 'Reiten': 6,
                     'Schießen': 8, 'Überreden': 4, 'Wahrnehmung': 6,
                     'Zaubern': 8},
    'handicaps':    ['Arrogant (schwer)', 'Neugierig (schwer)'],
    'talente':      ['AH (Taschenspieler)', 'Berechnend', 'Neue Mächte', 'Runenschießen'],
    'maechte':      ['Abstumpfen', 'Abwehren', 'Eigenschaft erhöhen/senken',
                     'Munitionszauber', 'Schutz'],
}, ['Arrogant (schwer)', 'Neugierig (schwer)'],
   'Mensch', [('talent', 'Berechnend')],
   {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 4},
   {'Allgemeinwissen': 6, 'Athletik': 6, 'Glücksspiel': 6, 'Heimlichkeit': 4,
    'Kämpfen': 4, 'Reiten': 6, 'Schießen': 8, 'Überreden': 4, 'Wahrnehmung': 6,
    'Zaubern': 8},
   ['AH (Taschenspieler)'],
   ['Abstumpfen', 'Abwehren', 'Eigenschaft erhöhen/senken'],
   [('Winchester \'73 (.44-40)', 1), ('Colt Frontier (.44-40)', 1), ('Messer', 1),
    ('Munition Gewehr (klein) .38-44 (50 Stück)', 2)],
   # Neue Mächte only in D-Advances (not SOLL talente)
   ['talent:Neue Mächte',
    'macht:Munitionszauber', 'macht:Schutz',
    'fertigkeit:Schießen:8', 'fertigkeit:Zaubern:8',
    'talent:Runenschießen',
    'attribut:Konstitution'])

# ── TASCHENSPIELER ───────────────────────────────────────────────────────────
# SOLL korrigiert: Konstitution W6→W4
build('Taschenspieler', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8,
                     'Stärke': 6, 'Konstitution': 4},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 4, 'Glücksspiel': 8,
                     'Heimlichkeit': 6, 'Kämpfen': 4, 'Okkultismus': 4,
                     'Provozieren': 6, 'Reiten': 4, 'Schießen': 4,
                     'Überreden': 6, 'Wahrnehmung': 6, 'Zaubern': 8},
    'handicaps':    ['Nachtängste (schwer)', 'Ärgermagnet (leicht)', 'Tick (leicht)'],
    'talente':      ['AH (Taschenspieler)', 'Falsch Spielen', 'Zocker'],
    'maechte':      ['Eigenschaft erhöhen/senken', 'Schmuckstücke', 'Strahl'],
}, ['Nachtängste (schwer)', 'Ärgermagnet (leicht)', 'Tick (leicht)'],
   'Mensch', [('talent', 'Falsch Spielen')],
   {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 4},
   {'Allgemeinwissen': 6, 'Athletik': 4, 'Glücksspiel': 8, 'Heimlichkeit': 6,
    'Kämpfen': 4, 'Okkultismus': 4, 'Provozieren': 6, 'Reiten': 4, 'Schießen': 4,
    'Überreden': 6, 'Wahrnehmung': 6, 'Zaubern': 8},
   ['AH (Taschenspieler)'],
   ['Eigenschaft erhöhen/senken', 'Schmuckstücke', 'Strahl'],
   [('Derringer (.41)', 1), ('Messer', 1), ('Munition Pistolen (klein) .22-.38 (50 Stück)', 1),
    ('Spielkarten', 1)],
   ['talent:Falsch Spielen', 'talent:AH (Taschenspieler)', 'talent:Zocker',
    'fertigkeit:Glücksspiel:8', 'fertigkeit:Zaubern:8',
    'fertigkeit:Überreden:6', 'fertigkeit:Provozieren:6', 'fertigkeit:Wahrnehmung:6',
    'macht:Eigenschaft erhöhen/senken', 'macht:Schmuckstücke', 'macht:Strahl'])

# ── VERRÜCKTE WISSENSCHAFTLERIN ──────────────────────────────────────────────
# AH(Verrückte Wissenschaft): 2 Mächte (Strahl, Heilung), 15 MP → via "Machtpunkte" auf 25
# "Neue Mächte" (D-Advances) für Illusion und Wachsen/Schrumpfen
# Achtung: Wachsen/Schrumpfen ist Rang F (Seasoned) - braucht ignore_rang_check
# SOLL korrigiert: Wahnvorstellungen (leicht) existiert NICHT in Deadlands → entfernt
build('Verrückte Wissenschaftlerin', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 6,
                     'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 8, 'Athletik': 4, 'Geisteswissenschaften': 6,
                     'Heilen': 4, 'Heimlichkeit': 4, 'Reparieren': 8,
                     'Naturwissenschaften': 8, 'Sprache': 4, 'Überreden': 4,
                     'Verrückte Wissenschaft': 8, 'Wahrnehmung': 4},
    'handicaps':    ['Beschämt (leicht)', 'Schlechte Augen (leicht)', 'Tick (leicht)'],
    'talente':      ['AH (Verrückte Wissenschaft)', 'Wahres Genie', 'Machtpunkte', 'Neue Mächte'],
    'maechte':      ['Strahl', 'Heilung', 'Illusion', 'Wachsen/Schrumpfen'],
}, ['Beschämt (leicht)', 'Schlechte Augen (leicht)', 'Tick (leicht)'],
   'Mensch', [('talent', 'Wahres Genie')],
   {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 6, 'Stärke': 4, 'Konstitution': 6},
   {'Allgemeinwissen': 8, 'Athletik': 4, 'Geisteswissenschaften': 6, 'Heilen': 4,
    'Heimlichkeit': 4, 'Reparieren': 8, 'Naturwissenschaften': 8, 'Sprache': 4, 'Überreden': 4,
    'Verrückte Wissenschaft': 8, 'Wahrnehmung': 6},
   ['AH (Verrückte Wissenschaft)'],
   ['Strahl', 'Heilung'],
   [('Brille', 1), ('Messer', 1)],
   # D-Advances: 4 Aufstiege
   # "Machtpunkte" VOR "Neue Mächte" (erhöht MP bevor neue Mächte gewählt werden)
   ['talent:Machtpunkte', 'talent:Neue Mächte',
    'fertigkeit:Reparieren:8', 'fertigkeit:Naturwissenschaften:8',
    'fertigkeit:Heilen:4', 'fertigkeit:Verrückte Wissenschaft:8',
    'macht:Illusion', 'macht:Wachsen/Schrumpfen'])

# ── KRIEGER ──────────────────────────────────────────────────────────────────
# SOLL korrigiert: Sprache W4 FEHLT → via D-Advances
build('Krieger', {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6,
                     'Stärke': 8, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 6, 'Heimlichkeit': 8,
                     'Kämpfen': 8, 'Provozieren': 4, 'Reiten': 6,
                     'Schießen': 6, 'Überreden': 4,
                     'Wahrnehmung': 6},
    'handicaps':    ['Außenseiter (leicht)', 'Eid auf die alten Bräuche (leicht)',
                     'Heldenhaft (schwer)'],
    'talente':      ['Beidhändiger Kampf', 'Mach ihn nicht wütend!', 'Mumm', 'Schneller Angriff'],
    'maechte':      [],
}, ['Heldenhaft (schwer)', 'Außenseiter (leicht)', 'Eid auf die alten Bräuche (leicht)'],
   'Mensch', [('talent', 'Mumm')],
   {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 8, 'Konstitution': 6},
   {'Allgemeinwissen': 6, 'Athletik': 6, 'Heimlichkeit': 8, 'Kämpfen': 8,
    'Provozieren': 4, 'Reiten': 6, 'Schießen': 6, 'Überreden': 4,
    'Wahrnehmung': 6},
   [],
   [],
   [('Eingeborenenrüstung', 1), ('Messer', 1),
    ('Lanze (Prärieindianer)', 1), ('Tomahawk', 1)],
   ['talent:Beidhändiger Kampf', 'talent:Mach ihn nicht wütend!', 'talent:Mumm',
    'talent:Schneller Angriff',
    'fertigkeit:Heimlichkeit:8', 'fertigkeit:Wahrnehmung:6',
    'fertigkeit:Sprache:4'])

# ── TERRITORIALER RANGER ──────────────────────────────────────────────────────
build('Territorialer Ranger', {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6,
                     'Stärke': 8, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 6,
                     'Heimlichkeit': 4, 'Kämpfen': 8, 'Reiten': 6,
                     'Schießen': 8, 'Überleben': 6, 'Überreden': 4,
                     'Wahrnehmung': 6},
    'handicaps':    ['Angetrieben (schwer)', 'Fettleibig (leicht)', 'Stur (leicht)'],
    'talente':      ['Doppelschuss', 'Mumm', 'Mutig', 'Territorialer Ranger'],
    'maechte':      [],
}, ['Angetrieben (schwer)', 'Fettleibig (leicht)', 'Stur (leicht)'],
   'Mensch', [('talent', 'Mutig')],
   {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 8, 'Konstitution': 6},
   {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 6, 'Heimlichkeit': 4,
    'Kämpfen': 8, 'Reiten': 6, 'Schießen': 8, 'Überleben': 6, 'Überreden': 4,
    'Wahrnehmung': 6},
    [],  # Territorialer Ranger via D-Advances (keine HP in CharGen)
   [],
   [('Gepanzerter Reitermantel (schwer)', 1), ('Messer, Bowie', 1)],
   ['talent:Doppelschuss','talent:Territorialer Ranger', 'talent:Mumm', 'talent:Mutig',
    'fertigkeit:Kämpfen:8', 'fertigkeit:Schießen:8', 'fertigkeit:Wahrnehmung:6', 'fertigkeit:Überleben:6'])

# ── MEDIZINFRAU ──────────────────────────────────────────────────────────────
# AH(Schamane): 4 Mächte (Abwehren, Heilen, Linderung, Verwirrung), 15 MP
# "Neue Mächte" (D-Advances) VOR den additionalen Mächten
build('Medizinfrau', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8,
                     'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 4, 'Glaube': 8, 'Heilen': 6,
                     'Heimlichkeit': 4, 'Kämpfen': 6, 'Okkultismus': 4,
                     'Reiten': 4, 'Sprache': 4, 'Überleben': 6,
                     'Überreden': 8, 'Wahrnehmung': 6},
    'handicaps':    ['Arm (leicht)', 'Eid auf die alten Bräuche (leicht)',
                     'Talisman (schwer)'],
    'talente':      ['AH (Schamane)', 'Geschichtenerzähler', 'Mutig', 'Fetisch', 'Neue Mächte'],
    'maechte':      ['Abwehren', 'Heilung', 'Linderung', 'Verwirrung'],
}, ['Talisman (schwer)', 'Arm (leicht)', 'Eid auf die alten Bräuche (leicht)'],
   'Mensch', [('talent', 'Mutig')],
   {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
   {'Allgemeinwissen': 6, 'Athletik': 4, 'Glaube': 8, 'Heilen': 6, 'Heimlichkeit': 4,
    'Kämpfen': 6, 'Okkultismus': 4, 'Reiten': 4, 'Sprache': 4, 'Überleben': 6,
    'Überreden': 8, 'Wahrnehmung': 6},
   ['AH (Schamane)'],
   ['Abwehren', 'Heilung'],  # CharGen: only 2 from AH (verf_maechte=2)
   [('Messer', 1)],
   # D-Advances: 5 Aufstiege (PDF-Fehler korrigiert: braucht 5 statt 4 für Überleben+Wahrnehmung)
   # Neue Mächte VOR additionalen Mächten (gives slots for Linderung, Verwirrung)
   ['talent:Geschichtenerzähler', 'talent:Fetisch',
    'talent:Neue Mächte',
    'fertigkeit:Heilen:6', 'fertigkeit:Glaube:8', 'fertigkeit:Überreden:8',
    'fertigkeit:Überleben:6', 'fertigkeit:Wahrnehmung:6',
    'macht:Linderung', 'macht:Verwirrung'],
   n_aufstiege=5)

# ── COWGIRL ───────────────────────────────────────────────────────────────────
# SOLL korrigiert: Konstitution W8 via D-Advances, Wahrnehmung W6 via D-Advances
# Schnell Ziehen via D-Advances (not during CharGen)
build('Cowgirl', {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8,
                     'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 6, 'Einschüchtern': 4,
                     'Glücksspiel': 4, 'Heimlichkeit': 4, 'Kämpfen': 6,
                     'Provozieren': 4, 'Reiten': 8, 'Schießen': 8,
                     'Überreden': 4, 'Wahrnehmung': 4},
    'handicaps':    ['Übermütig (schwer)', 'Loyal (leicht)', 'Tick (leicht)'],
    'talente':      ['Tierempathie', 'Im Sattel geboren', 'Schnell ziehen'],
    'maechte':      [],
}, ['Übermütig (schwer)', 'Loyal (leicht)', 'Tick (leicht)'],
   'Mensch', [('talent', 'Tierempathie')],
   {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
   {'Allgemeinwissen': 6, 'Athletik': 6, 'Einschüchtern': 4, 'Glücksspiel': 4,
    'Heimlichkeit': 4, 'Kämpfen': 6, 'Provozieren': 4, 'Reiten': 8, 'Schießen': 8,
    'Überreden': 4, 'Wahrnehmung': 4},
   [],
   [],
   [('Colt Peacemaker (.45)', 1), ('Winchester \'73 (.44-40)', 1), ('Messer', 1),
    ('Lasso', 1)],
   ['talent:Tierempathie', 'talent:Im Sattel geboren',
    'talent:Schnell ziehen',
    'fertigkeit:Reiten:8', 'fertigkeit:Schießen:8',
    'attribut:Konstitution'])

# ── EINGEBORENEN-KUNDSCHAFTERIN ──────────────────────────────────────────────
# SOLL korrigiert: Sprache W6→W4
build('Eingeborenen-Kundschafterin', {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 6,
                     'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Heimlichkeit': 8,
                     'Kämpfen': 6, 'Provozieren': 4, 'Reiten': 6,
                     'Schießen': 8, 'Sprache': 4, 'Überleben': 8,
                     'Überreden': 4, 'Wahrnehmung': 8},
    'handicaps':    ['Heldenhaft (schwer)', 'Fies (leicht)', 'Ärgermagnet (leicht)'],
    'talente':      ['Parkour', 'Kundschafter', 'Naturbursche'],
    'maechte':      [],
}, ['Heldenhaft (schwer)', 'Fies (leicht)', 'Ärgermagnet (leicht)'],
   'Mensch', [('talent', 'Kundschafter')],
   {'Geschicklichkeit': 8, 'Verstand': 8, 'Willenskraft': 6, 'Stärke': 4, 'Konstitution': 6},
   {'Allgemeinwissen': 4, 'Athletik': 6, 'Heimlichkeit': 8, 'Kämpfen': 6,
    'Provozieren': 4, 'Reiten': 6, 'Schießen': 8, 'Sprache': 4, 'Überleben': 8,
    'Überreden': 4, 'Wahrnehmung': 8},
   [],
   [],
   [('Winchester \'73 (.44-40)', 1), ('Messer', 1)],
   ['talent:Parkour', 'talent:Kundschafter', 'talent:Naturbursche',
    'fertigkeit:Überleben:8', 'fertigkeit:Wahrnehmung:8',
    'fertigkeit:Reiten:6', 'fertigkeit:Athletik:6'])

# ── METALLMAGIER ──────────────────────────────────────────────────────────────
# AH(Verrückte Wissenschaft): 2 Mächte (Ausfall, Schmuckstücke), 15 MP
# meta.txt says "Chaos" but actual Deadlands power is "Strahl"
# "Neue Mächte" in D-Advances für Flächenschlag und Strahl
build('Metallmagier', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 6,
                     'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 4, 'Geisteswissenschaften': 4,
                     'Heimlichkeit': 4, 'Kämpfen': 4, 'Naturwissenschaften': 4,
                     'Okkultismus': 6, 'Recherche': 6, 'Reparieren': 6,
                     'Überreden': 6, 'Verrückte Wissenschaft': 8, 'Wahrnehmung': 6},
    'handicaps':    ['Arrogant (schwer)', 'Nachtängste (schwer)'],
    'talente':      ['AH (Verrückte Wissenschaft)', 'Kühler Kopf', 'Metallmagier', 'Neue Mächte'],
    'maechte':      ['Ausfall', 'Flächenschlag', 'Schmuckstücke', 'Strahl'],
}, ['Arrogant (schwer)', 'Nachtängste (schwer)'],
   'Mensch', [('talent', 'Kühler Kopf')],
   {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 6},
   {'Allgemeinwissen': 4, 'Athletik': 4, 'Geisteswissenschaften': 4, 'Heimlichkeit': 4,
    'Kämpfen': 4, 'Naturwissenschaften': 4, 'Okkultismus': 6, 'Recherche': 6,
    'Reparieren': 6, 'Überreden': 6, 'Verrückte Wissenschaft': 8, 'Wahrnehmung': 6},
   ['AH (Verrückte Wissenschaft)'],
   ['Ausfall', 'Schmuckstücke'],  # CharGen: 2 from AH
   [('Derringer (.41)', 1), ('Munition Pistolen (klein) .22-.38 (50 Stück)', 1)],
   # D-Advances: 4 Aufstiege
   # Need Verrückte Wissenschaft W8 and Wahrnehmung W6
   ['talent:Neue Mächte', 'talent:Metallmagier',
    'fertigkeit:Verrückte Wissenschaft:8', 'fertigkeit:Wahrnehmung:6',
    'macht:Flächenschlag', 'macht:Strahl'])

# ── KOPFGELDJÄGER ───────────────────────────────────────────────────────────
# SOLL korrigiert: Bedrohlich in SOLL (not D-Advances), Wahrnehmung W6
build('Kopfgeldjäger', {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6,
                     'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 6,
                     'Heimlichkeit': 6, 'Kämpfen': 6, 'Reiten': 6,
                     'Schießen': 8, 'Überleben': 6, 'Überreden': 4,
                     'Wahrnehmung': 6},
    'handicaps':    ['Arrogant (schwer)', 'Skrupellos (schwer)'],
    'talente':      ['Bedrohlich', 'Gassenwissen', 'Keine Gnade', 'Ruhige Hände', 'Volltreffer'],
    'maechte':      [],
}, ['Arrogant (schwer)', 'Skrupellos (schwer)'],
   'Mensch', [('talent', 'Gassenwissen')],
   {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 6},
   {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 6, 'Heimlichkeit': 6,
    'Kämpfen': 6, 'Reiten': 6, 'Schießen': 8, 'Überleben': 6, 'Überreden': 4,
    'Wahrnehmung': 6},
   [],
   [],
   [('Winchester \'73 (.44-40)', 1), ('Colt Frontier (.44-40)', 2),
    ('Munition Gewehr (klein) .38-44 (50 Stück)', 2)],
   ['talent:Gassenwissen', 'talent:Keine Gnade', 'talent:Ruhige Hände', 'talent:Volltreffer',
    'talent:Bedrohlich',
    'fertigkeit:Schießen:8', 'fertigkeit:Überleben:6',
    'fertigkeit:Wahrnehmung:6'])

# ── SALOONSCHÖNHEIT ───────────────────────────────────────────────────────────
build('Saloonschönheit', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8,
                     'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 6, 'Darbietung': 8,
                     'Glücksspiel': 4, 'Heilen': 4, 'Heimlichkeit': 4,
                     'Kämpfen': 4, 'Provozieren': 6, 'Schießen': 4,
                     'Überreden': 8, 'Wahrnehmung': 6},
    'handicaps':    ['Heldenhaft (schwer)', 'Neugierig (schwer)'],
    'talente':      ['Attraktiv', 'Gassenwissen', 'Geschichtenerzähler', 'Konter', 'Mutig'],
    'maechte':      [],
}, ['Heldenhaft (schwer)', 'Neugierig (schwer)'],
   'Mensch', [('talent', 'Attraktiv')],
   {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
   {'Allgemeinwissen': 6, 'Athletik': 6, 'Darbietung': 8, 'Glücksspiel': 4, 'Heilen': 4,
    'Heimlichkeit': 4, 'Kämpfen': 4, 'Provozieren': 6, 'Schießen': 4, 'Überreden': 8,
    'Wahrnehmung': 6},
   ['Attraktiv'],
   [],
   [('Derringer (.41)', 1), ('Munition Pistolen (klein) .22-.38 (50 Stück)', 1)],
   ['talent:Gassenwissen', 'talent:Geschichtenerzähler', 'talent:Konter', 'talent:Mutig',
    'fertigkeit:Darbietung:8', 'fertigkeit:Überreden:8', 'fertigkeit:Wahrnehmung:6'])

# ── WUNDARZT ─────────────────────────────────────────────────────────────────
# SOLL korrigiert: Heimlichkeit W8→W6, Reiten FEHLT→via D-Advances
build('Wundarzt', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8,
                     'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 4, 'Geisteswissenschaften': 4,
                     'Heilen': 8, 'Heimlichkeit': 4, 'Kämpfen': 6,
                     'Naturwissenschaften': 4, 'Provozieren': 8, 'Reiten': 4,
                     'Schießen': 6, 'Überreden': 4, 'Wahrnehmung': 6},
    'handicaps':    ['Heldenhaft (schwer)', 'Kränkelnd (schwer)', 'Tiefer Schlaf (leicht)'],
    'talente':      ['Erniedrigen', 'Galgenhumor', 'Heiler'],
    'maechte':      [],
}, ['Heldenhaft (schwer)', 'Kränkelnd (schwer)', 'Tiefer Schlaf (leicht)'],
   'Mensch', [('talent', 'Galgenhumor')],
   {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
   {'Allgemeinwissen': 6, 'Athletik': 4, 'Geisteswissenschaften': 4, 'Heilen': 8,
    'Heimlichkeit': 4, 'Kämpfen': 6, 'Naturwissenschaften': 4, 'Provozieren': 8,
    'Reiten': 4, 'Schießen': 6, 'Überreden': 4, 'Wahrnehmung': 6},
   [],
   [],
   [('Arzttasche', 1), ('Colt Army (.44)', 1), ('Messer', 1),
    ('Munition Pistole (groß) .40-.50 (50 Stück)', 1)],
   ['talent:Erniedrigen', 'talent:Galgenhumor', 'talent:Heiler',
    'fertigkeit:Provozieren:8', 'fertigkeit:Heilen:8',
    'fertigkeit:Schießen:6', 'fertigkeit:Reiten:4',
    'fertigkeit:Wahrnehmung:6'])

# ── SCHAMANE ─────────────────────────────────────────────────────────────────
# AH(Schamane): 4 Mächte, 15 MP
# "Neue Mächte" (D-Advances) VOR additionalen Mächten
# Achtung:meta.txt "Neue Mächte (Waffe verbessern, Wildniswandler)" = die TALENTE, nicht Mächte!
build('Schamane', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8,
                     'Stärke': 6, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 8,
                     'Glaube': 8, 'Heilen': 6, 'Heimlichkeit': 4,
                     'Kämpfen': 6, 'Reiten': 6, 'Sprache': 4,
                     'Überleben': 4, 'Überreden': 4, 'Wahrnehmung': 6},
    'handicaps':    ['Außenseiter (leicht)', 'Eid auf die alten Bräuche (leicht)',
                     'Heldenhaft (schwer)'],
    'talente':      ['AH (Schamane)', 'Die Gunst des Geistes', 'Heiliger/Unheiliger Krieger', 'Neue Mächte'],
    'maechte':      ['Eigenschaft erhöhen/senken', 'Schutz', 'Waffe verbessern', 'Wildniswandler'],
}, ['Heldenhaft (schwer)', 'Außenseiter (leicht)', 'Eid auf die alten Bräuche (leicht)'],
   'Mensch', [('talent', 'Die Gunst des Geistes')],
   {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 6, 'Konstitution': 6},
   {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 8, 'Glaube': 8, 'Heilen': 6,
    'Heimlichkeit': 4, 'Kämpfen': 6, 'Reiten': 6, 'Sprache': 4, 'Überleben': 4,
    'Überreden': 4, 'Wahrnehmung': 6},
   ['AH (Schamane)'],
   ['Eigenschaft erhöhen/senken', 'Schutz'],
   [('Eingeborenenrüstung', 1), ('Tomahawk', 1)],
   # D-Advances: 4 Aufstiege
   # Heiliger Krieger muss explizit sein, dann Neue Mächte, dann Mächte
['talent:Heiliger/Unheiliger Krieger', 'talent:Neue Mächte',
     'fertigkeit:Wahrnehmung:6', 'fertigkeit:Sprache:4', 'fertigkeit:Reiten:6', 'fertigkeit:Überleben:4',
     'macht:Waffe verbessern', 'macht:Wildniswandler'])

# ── US-MARSHAL ──────────────────────────────────────────────────────────────
build('US-Marshal', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 6,
                     'Stärke': 6, 'Konstitution': 8},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 6, 'Einschüchtern': 6,
                     'Gewerbe (Recht)': 4, 'Heimlichkeit': 6, 'Kämpfen': 6,
                     'Schießen': 8, 'Überreden': 6, 'Wahrnehmung': 6},
    'handicaps':    ['Ehrenkodex (schwer)', 'Schwur (schwer)'],
    'talente':      ['Aufmerksamkeit', 'Eisenkiefer', 'Kühler Kopf', 'US-Marshal'],
    'maechte':      [],
}, ['Ehrenkodex (schwer)', 'Schwur (schwer)'],
   'Mensch', [('talent', 'Eisenkiefer')],
   {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 8},
   {'Allgemeinwissen': 6, 'Athletik': 6, 'Einschüchtern': 6, 'Gewerbe (Recht)': 4,
    'Heimlichkeit': 6, 'Kämpfen': 6, 'Schießen': 8, 'Überreden': 6, 'Wahrnehmung': 6},
    [],  # US-Marshal via D-Advances (keine HP in CharGen)
   [],
   [('Colt Frontier (.44-40)', 1), ('Winchester \'73 (.44-40)', 1),
    ('Munition Gewehr (klein) .38-44 (50 Stück)', 1)],
['talent:Aufmerksamkeit', 'talent:Eisenkiefer', 'talent:Kühler Kopf', 'talent:US-Marshal',
     'fertigkeit:Schießen:8', 'fertigkeit:Überreden:6', 'fertigkeit:Wahrnehmung:6'])

# ── VAQUERO ────────────────────────────────────────────────────────────────────
# SOLL korrigiert: Sprache W6→W4, Wahrnehmung W6→W4
build('Vaquero', {
    'attribute':    {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6,
                     'Stärke': 6, 'Konstitution': 8},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 4,
                     'Heilen': 4, 'Heimlichkeit': 4, 'Kämpfen': 8,
                     'Reiten': 6, 'Schießen': 8, 'Sprache': 4,
                     'Überreden': 4, 'Wahrnehmung': 4},
    'handicaps':    ['Heldenhaft (schwer)', 'Loyal (leicht)', 'Verlogene Augen (leicht)'],
    'talente':      ['Hahnwedeln', 'Im Sattel geboren', 'Lieblingswaffe', 'Ruhige Hände'],
    'maechte':      [],
}, ['Heldenhaft (schwer)', 'Loyal (leicht)', 'Verlogene Augen (leicht)'],
   'Mensch', [('talent', 'Im Sattel geboren')],
   {'Geschicklichkeit': 8, 'Verstand': 6, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 8},
   {'Allgemeinwissen': 4, 'Athletik': 6, 'Einschüchtern': 4, 'Heilen': 4, 'Heimlichkeit': 4,
    'Kämpfen': 8, 'Reiten': 6, 'Schießen': 8, 'Sprache': 4, 'Überreden': 4, 'Wahrnehmung': 4},
   [],
   [],
   [('Colt Peacemaker (.45)', 1), ('Winchester \'73 (.44-40)', 1), ('Messer', 1),
    ('Lasso', 1)],
   ['talent:Hahnwedeln', 'talent:Im Sattel geboren', 'talent:Lieblingswaffe', 'talent:Ruhige Hände',
    'fertigkeit:Kämpfen:8', 'fertigkeit:Schießen:8'])

# ── VOODOOPRAKTIKERIN ────────────────────────────────────────────────────────
build('Voodoopraktikerin', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8,
                     'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 6, 'Einschüchtern': 8,
                     'Glaube': 8, 'Heilen': 6, 'Heimlichkeit': 4,
                     'Kämpfen': 4, 'Okkultismus': 6, 'Provozieren': 4,
                     'Überreden': 4, 'Wahrnehmung': 4},
    'handicaps':    ['Heldenhaft (schwer)', 'Talisman (schwer)'],
    'talente':      ['AH (Voodoopraktiker)', 'Begünstigt', 'Mutig', 'Machtpunkte', 'Neue Mächte'],
    'maechte':      ['Aspekt der Rada-Loa', 'Eigenschaft erhöhen/senken', 'Heilung', 'Zorn der Petro-Loa'],
}, ['Heldenhaft (schwer)', 'Talisman (schwer)'],
   'Mensch', [('talent', 'Begünstigt')],
   {'Geschicklichkeit': 6, 'Verstand': 6, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
   {'Allgemeinwissen': 6, 'Athletik': 6, 'Einschüchtern': 8, 'Glaube': 8, 'Heilen': 6,
    'Heimlichkeit': 4, 'Kämpfen': 4, 'Okkultismus': 6, 'Provozieren': 4,
    'Überreden': 4, 'Wahrnehmung': 4},
   ['AH (Voodoopraktiker)'],
   ['Aspekt der Rada-Loa', 'Eigenschaft erhöhen/senken'],  # CharGen: only 2 from AH (verf_maechte=2); Heilung/Zorn via D-Advances
   [('Messer', 1)],
['talent:Machtpunkte', 'talent:Neue Mächte', 'talent:Mutig',
     'fertigkeit:Heilen:6', 'fertigkeit:Okkultismus:6', 'fertigkeit:Provozieren:4',
     'macht:Heilung', 'macht:Zorn der Petro-Loa'])

# ── HEXE ──────────────────────────────────────────────────────────────────────
# ── HEXE ──────────────────────────────────────────────────────────────────────
# AH(Hexe): 5 Mächte, 15 MP
# "Machtpunkte" (D-Advances) VOR "Neue Mächte" (laut meta: "...Machtpunkte, Neue Mächte (Betören, Flächenschlag)")
# Hexe hat Betören, Empathie, Flächenschlag, Kriegersegen, Verwirrung via AH
build('Hexe', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8,
                     'Stärke': 4, 'Konstitution': 6},
    'fertigkeiten': {'Allgemeinwissen': 4, 'Athletik': 4, 'Einschüchtern': 6,
                     'Heimlichkeit': 4, 'Kämpfen': 6, 'Okkultismus': 8,
                     'Reiten': 4, 'Schießen': 6, 'Überreden': 4,
                     'Wahrnehmung': 6, 'Zaubern': 8},
    'handicaps':    ['Beschämt (leicht)', 'Loyal (leicht)', 'Schwur (schwer)'],
    'talente':      ['AH (Hexe)', 'Vertrauter', 'Wichita-Hexe', 'Machtpunkte', 'Neue Mächte'],
    'maechte':      ['Betoeren', 'Empathie', 'Flächenschlag', 'Kriegersegen', 'Verwirrung'],
}, ['Schwur (schwer)', 'Beschämt (leicht)', 'Loyal (leicht)'],
   'Mensch', [('talent', 'Vertrauter')],
   {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 8, 'Stärke': 4, 'Konstitution': 6},
   {'Allgemeinwissen': 4, 'Athletik': 4, 'Einschüchtern': 6, 'Heimlichkeit': 4,
    'Kämpfen': 6, 'Okkultismus': 8, 'Reiten': 4, 'Schießen': 6, 'Überreden': 4,
    'Wahrnehmung': 6, 'Zaubern': 8},
   ['AH (Hexe)'],
   ['Betoeren', 'Empathie', 'Flächenschlag'],  # CharGen: only 3 (verf_maechte=3); Kriegersegen/Verwirrung via D-Advances
   [('Colt Lightning (.38)', 1), ('Messer', 1), ('Peitsche', 1)],
   # D-Advances: 4 Aufstiege
   # Machtpunkte VOR Neue Mächte (laut meta)
['talent:Machtpunkte', 'talent:Neue Mächte', 'talent:Wichita-Hexe',
     'fertigkeit:Okkultismus:8', 'fertigkeit:Zaubern:8',
     'macht:Flächenschlag', 'macht:Kriegersegen', 'macht:Verwirrung'])  # Kriegersegen + Verwirrung via D-Advances (Neue Mächte gives more MP)

# ── INVESTIGATIVER JOURNALIST ────────────────────────────────────────────────
build('Investigativer Journalist', {
    'attribute':    {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 6,
                     'Stärke': 6, 'Konstitution': 4},
    'fertigkeiten': {'Allgemeinwissen': 6, 'Athletik': 4, 'Einschüchtern': 4,
                     'Gewerbe (Recht)': 6, 'Heimlichkeit': 6, 'Kämpfen': 4,
                     'Okkultismus': 4, 'Provozieren': 6, 'Recherche': 8,
                     'Schießen': 6, 'Überreden': 8, 'Wahrnehmung': 6},
    'handicaps':    ['Große Klappe (leicht)', 'Neugierig (schwer)', 'Stur_schwer'],
    'talente':      ['Aufmerksamkeit', 'Ermittler', 'Geschichtenerzähler', 'Mumm'],
    'maechte':      [],
}, ['Neugierig (schwer)', 'Stur_schwer', 'Große Klappe (leicht)'],
   'Mensch', [('talent', 'Aufmerksamkeit')],
   {'Geschicklichkeit': 6, 'Verstand': 8, 'Willenskraft': 6, 'Stärke': 6, 'Konstitution': 4},
   {'Allgemeinwissen': 6, 'Athletik': 4, 'Einschüchtern': 4, 'Gewerbe (Recht)': 6,
    'Heimlichkeit': 6, 'Kämpfen': 4, 'Okkultismus': 4, 'Provozieren': 6,
    'Recherche': 8, 'Schießen': 6, 'Überreden': 8, 'Wahrnehmung': 6},
   [],
   [],
   [('Colt Lightning (.38)', 1), ('Munition Pistolen (klein) .22-.38 (50 Stück)', 1)],
['talent:Aufmerksamkeit', 'talent:Ermittler', 'talent:Geschichtenerzähler', 'talent:Mumm',
     'fertigkeit:Überreden:8', 'fertigkeit:Recherche:8',
     'fertigkeit:Schießen:6', 'fertigkeit:Wahrnehmung:6'])

m("\n=== FERTIG ===")
tlog.close()
print("Build abgeschlossen")