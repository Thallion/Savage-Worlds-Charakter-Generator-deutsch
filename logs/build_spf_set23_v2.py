#!/usr/bin/env python3
"""Build-Skript v2 für Savage Pathfinder Sets 2+3 — mit korrigierten Deutschen Keys."""

import sys, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d

tlog = open('logs/spf_set23_v2_trace.txt', 'w', encoding='utf-8')
def m(x): tlog.write(str(x)+'\n'); tlog.flush()

all_results = []

def baue(name, klassentalent, manual_handicaps, volk, volk_wahlen,
         soll_attr, soll_fert, soll_handicaps, soll_talente, soll_maechte,
         manual_talente=None, ausruestung=None, additional_powers=None,
         freier_ah=None):
    """Baut einen Archetyp."""
    result = {'name': name}
    s = None
    try:
        s = d.Sitzung('Savage Pathfinder', name, protokoll=f'logs/{name}.log')
        m(f"\n{'='*60}\nBAUE: {name}")
        m(f"  Start: {s.punktestand()}")

        # 1: Klassentalent
        if klassentalent:
            vor = s.zustand()
            r = s.pathfinder_klassentalent(klassentalent, ignore_voraussetzungen=True)
            auto = s.zeige_auto_eintraege(vor)
            m(f"  Klasse '{klassentalent}': ok={r['ok']}")
            m(f"  Auto: {auto}")
            if not r['ok']:
                s.notiz(f'KLASSE "{klassentalent}" nicht wählbar')

        # Generischer AH (für klassenlose Charaktere)
        if freier_ah:
            r = s.talent(freier_ah, ignore_voraussetzungen=True)
            m(f"  AH '{freier_ah}': ok={r['ok']}")

        # 2: Manuelle Handicaps
        for h in manual_handicaps:
            r = s.handicap(h)
            if not r['ok']:
                s.notiz(f'HANDICAP fehlt: {h}')
                m(f"  ✗ Handicap: {h}")
            else:
                m(f"  Handicap: {h} ok, HP={s.ch.verbleibende_handicap_punkte}")

        # 3: Volk
        vor_v = s.zustand()
        r = s.volk(volk)
        auto_v = s.zeige_auto_eintraege(vor_v)
        m(f"  Volk '{volk}': ok={r['ok']}, auto={auto_v}")
        if not r['ok']:
            s.notiz(f'VOLK "{volk}" nicht gefunden')

        # 4: Volkswahlen
        wahlen = s.volk_wahlmoeglichkeiten(volk)
        m(f"  Volkswahlen: {wahlen}")
        for w in (volk_wahlen or []):
            typ = w['typ']; val = w['wert']
            if typ == 'freies_talent':
                r = s.volk_freies_talent(volk, val, ignore_voraussetzungen=True)
                m(f"  Freies Talent '{val}': ok={r['ok']}")
            elif typ == 'freies_attribut':
                r = s.volk_freies_attribut(volk, val)
                m(f"  Freies Attribut '{val}': ok={r['ok']}")

        # 5: Attribute komplett vor Fertigkeiten
        m(f"  Soll-Attribute: {soll_attr}")
        for a, z in soll_attr.items():
            if a in s.ch.attribute:
                s.attribut_auf(a, z)
            else:
                s.notiz(f'Attribut-Key fehlt: {a}')
        # HP-Attribute
        for a, z in soll_attr.items():
            if a in s.ch.attribute:
                while (s.ch.attribute[a].wuerfel.value < z and
                       s.ch.verbleibende_handicap_punkte > 0):
                    vor = s.ch.attribute[a].wuerfel.value
                    s.steigere_mit_handicap_attribut(a)
                    if s.ch.attribute[a].wuerfel.value == vor: break
        m(f"  Nach Attributen: {s.punktestand()}")
        m(f"  IST-Attr: { {a:s.ch.attribute[a].wuerfel.value for a in s.ch.attribute} }")

        # 6: Fertigkeiten
        for f, z in soll_fert.items():
            if f in s.ch.fertigkeiten:
                s.fertigkeit_auf(f, z)
            else:
                s.notiz(f'Fertigkeit fehlt: {f}')
                m(f"  ✗ Fertigkeit: {f}")
        m(f"  Nach Fertigkeiten: {s.punktestand()}")

        # 7: Manuelle Talente (die nicht auto sind)
        for t in (manual_talente or []):
            if t not in s.ch.selected_talente:
                r = s.talent(t, ignore_voraussetzungen=True)
                if not r['ok']:
                    s.notiz(f'Talent fehlt: {t}')
                    m(f"  ✗ Talent: {t}")
                else:
                    m(f"  Talent '{t}': ok, HP={s.ch.verbleibende_handicap_punkte}")

        # 8: Mächte
        for mm in soll_maechte:
            if mm in s.ch.maechte:
                r = s.macht(mm, ignore_rang_check=True)
                if not r['ok']:
                    s.notiz(f'Macht fehlt: {mm}')
                    m(f"  ✗ Macht: {mm}")

        # 9: Ausrüstung
        if ausruestung:
            for item, anz in ausruestung:
                if item in s.ch.ausruestung:
                    r = s.kaufen(item, anzahl=anz, force_bei_geldmangel=True)
                else:
                    s.notiz(f'Ausrüstung fehlt im Katalog: {item}')

        # --- Abschluss ---
        s.ch.berechne_abgeleitete_werte()
        m(f"  PARADE={s.ch.parade} BEW={s.ch.bewegungsweite} ROB={s.ch.robustheit}")
        m(f"  End-Punkte: {s.punktestand()}")
        m(f"  IST-Talente: {sorted(s.ch.selected_talente)}")
        m(f"  IST-Handicaps: {list(s.ch.selected_handicaps)}")
        m(f"  IST-Mächte: {list(s.ch.selected_maechte)}")

        diff = s.diff({'attribute': soll_attr, 'fertigkeiten': soll_fert,
                        'handicaps': soll_handicaps, 'talente': soll_talente,
                        'maechte': soll_maechte})
        m(f"  DIFF: {diff['abweichungen']}")

        s.speichern(f'chars/Archetypen/Archetyp_Savage_Pathfinder_{name}_A.json')
        b = s.bericht(f'logs/{name}_bericht.json')
        result['ok'] = True
        result['anomalien'] = b['anomalien_anzahl']
        result['punkte'] = b['endzustand']['punkte']
        result['diff'] = diff['abweichungen']
    except BaseException as e:
        m(f"CRASH {name}: {e!r}\n{traceback.format_exc()}")
        result['ok'] = False; result['error'] = str(e)
    all_results.append(result)


# ===================================================================
# SET 2 — NOVICE
# ===================================================================

# --- KIRA: Barbar / Halbelf ---
# Bogen: Curious(major)=Neugierig, Loyal, Overconfident(major)→Arrogant
# Auto: Barbar→Berserker,Behände,Kampfrausch + Rüstungsbeschränkung_mittelschwer
# Budget: 5AP + 4HP (Neugierig2+Loyal1+Arrogant2? Nein, Arrogant fehlt hier nicht,
#   aber Arrogant ist SCHWER=2HP. Start 0HP, +Neugierig2 +Loyal1 +Arrogant2 = 5HP → cap at 4)
#   Warten: Keine freie Wahl bei Halbelf
#   Attribute: GEK8(W6→8=2AP), VER6(W4→6=1), WIL6, STÄ8(W4→8=2), KON6(bleibt W4→0).
#   Regulär 5AP verbraucht. HP für KON W4→W6? Kira hat KON W6 im Bogen.
#   KON W4→W6 = 2HP. 4HP total → 2HP übrig (Arrogant rejected? Nein, 2+1+2=5 aber cap=4)

baue('Kira',
     klassentalent='Barbar',
     manual_handicaps=['Neugierig', 'Loyal', 'Arrogant'],
     volk='Halbelf',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':8, 'Verstand':6, 'Willenskraft':6, 'Stärke':8, 'Konstitution':6},
     soll_fert={'Athletik':8, 'Allgemeinwissen':4, 'Kämpfen':6, 'Einschüchtern':4,
                'Wahrnehmung':6, 'Okkultismus':6, 'Überreden':4, 'Heimlichkeit':8, 'Überleben':6},
     soll_handicaps=['Neugierig', 'Loyal', 'Arrogant', 'Rüstungsbeschränkung_mittelschwer'],
     soll_talente=['Barbar', 'Berserker', 'Behände', 'Kampfrausch'],     ausruestung=[('Speer',1),('Kurzspeer/Wurfspeer',7),('Beschlagene Lederrüstung',1),('Mittlerer Schild',1),('Abenteurerausrüstung',1),('Verstrickungsbeutel',1),('Trank: schwache Heilung',1)])

# --- TELLER: Barde / Mensch ---
# Bogen: Anemic(minor)→✗, Impulsive(major)=Impulsiv, Thin skinned(minor)=Dünnhäutig_leicht
# Klasse: AH (Barde) → auto: Scharfzüngig + Behindernde Rüstung_leicht
# Budget: 5AP + 2HP (Impulsiv2)
#   (Anemic fehlt → kein HP dafür; Dünnhäutig_leicht=1HP → wird rejected? 2+1=3HP, ok)
# Warten: Nein, Dünnhäutig_leicht ist minor=1HP. Impulsiv=2HP. Total 3HP, unter cap.
# Freies Talent: Charismatisch, Freies Attribut: Geschicklichkeit W4→W6
# Attribute: GEK W6→W8(1AP), VER W4→W6(1), WIL W4→W8(2), STÄ W4→W6(1), KON W4=0
#   5AP total. Keine HP-Attribute nötig.
# Fertigkeiten: Darbietung 8, Kämpfen 8, Athletik 6, AW 6, Wahrnehmung 6, Okkultismus 4,
#   Geisteswissenschaften 4, Überreden 6, Schießen 4, Heimlichkeit 6
#   Sind das 12FP? Rechnen: Darb(3)+Kämpf(2)+AW(0)+GWi(1)+Heiml(1)+Überr(1)+Schi(1)+Okk(1) = 10
#   Plus Athletik schon W6 durch Bonus? Nein, Mensch hat keine Startboni.
#   Warten: Checken

baue('Teller',
     klassentalent='AH (Barde)',
     manual_handicaps=['Impulsiv', 'Kränklich', 'Dünnhäutig_leicht'],
     volk='Mensch',
     volk_wahlen=[{'typ':'freies_attribut','wert':'Geschicklichkeit'},
                  {'typ':'freies_talent','wert':'Charismatisch'}],
     soll_attr={'Geschicklichkeit':8, 'Verstand':6, 'Willenskraft':8, 'Stärke':6, 'Konstitution':6},
     soll_fert={'Athletik':6, 'Allgemeinwissen':6, 'Kämpfen':8, 'Wahrnehmung':6,
                'Okkultismus':4, 'Darbietung':8, 'Geisteswissenschaften':4,
                'Überreden':6, 'Schießen':4, 'Heimlichkeit':6},
     soll_handicaps=['Impulsiv', 'Kränklich', 'Dünnhäutig_leicht', 'Behindernde Rüstung_leicht'],
     soll_talente=['AH (Barde)', 'Scharfzüngig', 'Charismatisch'],
     soll_maechte=['Eigenschaft erhöhen/senken', 'Empathie', 'Verwirrung'],
     manual_talente=['Formationskämpfer'],  # Formation Fighter → Formationskämpfer ✓
     ausruestung=[('Rapier',1),('Leichte Armbrust',1),('Bolzen (10)',2),('Ledertunika',1),('Lederbeinlinge',1),('Abenteurerausrüstung',1),('Trank: schwache Heilung',1),('Gegengift, Phiole',1)])

# --- BROKAR: Kleriker / Zwerg ---
# Bogen: Code of Honor(major)=Ehrenkodex, Tongue-Tied(major)→Schwerzüngig
# Klasse: AH (Kleriker) → auto: Energie fokussieren, Gnade, Schwur_schwer
# Budget: 5AP + 4HP (Ehrenkodex2+Schwerzüngig2)
# Attribute: GEK W4→W6(1), VER W4→W6(1), WIL W4→W8(2), STÄ W4→W6(1), KON W4→W8 → 5AP+?
#   Zwerg KON startet W6? Nein, kein Attribut-Bonus. 
#   KON W4→W6(1AP)+W6→W8(2HP)=3 Steigerungen. 5AP: GEK1+VER1+WIL2+STÄ1=5, dann HP für KON W6→W8.
# Fertigkeiten: Alle W4 außer Glaube W8, Heilen, Wahrnehmung, Okkultismus, Überreden, Kämpfen W6

baue('Brokar',
     klassentalent='AH (Kleriker)',
     manual_handicaps=['Ehrenkodex', 'Schwerzüngig'],
     volk='Zwerg',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':6, 'Verstand':6, 'Willenskraft':8, 'Stärke':6, 'Konstitution':8},
     soll_fert={'Athletik':4, 'Allgemeinwissen':4, 'Glaube':8, 'Kämpfen':6,
                'Heilen':6, 'Wahrnehmung':6, 'Okkultismus':6, 'Überreden':6,
                'Schießen':4, 'Heimlichkeit':4},
     soll_handicaps=['Ehrenkodex', 'Schwerzüngig', 'Schwur_schwer'],
     soll_talente=['AH (Kleriker)', 'Energie fokussieren', 'Gnade'],
     soll_maechte=['Heilung', 'Schutz'],
     ausruestung=[('Kriegshammer',1),('Leichte Armbrust',1),('Bolzen (10)',2),('Schuppenpanzer',1),('Abenteurerausrüstung',1),('Heilertasche',1)])

# --- ZYRIL: Kämpfer / Elf ---
# Bogen: One Arm(major)=Einarmig, Loyal, Vengeful(minor)=Rachsüchtig_leicht
# Klasse: Kämpfer → auto: Kriegerische Anpassungsfähigkeit
# Elf: Schlank, GEK startet W6, VER startet W6 (Intelligent)
# Budget: 5AP + 4HP (Einarmig2+Loyal1+Rachs1)
# Attribute: GEK W6→W8(1AP), VER W6=0, WIL W4→W6(1), STÄ W4→W8(3AP), KON W4→W8 → 5AP verbraucht?
#   Warten: GEK1+WIL1+STÄ3=5AP → KON mit HP: W4→W6→W8 = 2×2HP=4HP. Passt!
# Talente: Lieblingswaffe (Trademark Weapon) mit HP (2HP)

baue('Zyril',
     klassentalent='Kämpfer',
     manual_handicaps=['Einarmig', 'Loyal', 'Rachsüchtig_leicht'],
     volk='Elf',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':8, 'Verstand':6, 'Willenskraft':6, 'Stärke':8, 'Konstitution':8},
     soll_fert={'Athletik':8, 'Allgemeinwissen':4, 'Kämpfen':8, 'Einschüchtern':6,
                'Wahrnehmung':6, 'Überreden':4, 'Reiten':6, 'Heimlichkeit':8, 'Überleben':4},
     soll_handicaps=['Einarmig', 'Loyal', 'Rachsüchtig_leicht', 'Schlank'],
     soll_talente=['Kämpfer', 'Kriegerische Anpassungsfähigkeit', 'Lieblingswaffe'],
     soll_maechte=[],
     manual_talente=['Lieblingswaffe'],
     ausruestung=[('Langschwert',1),('Schuppenpanzer',1),('Lederbeinlinge',1),('Abenteurerausrüstung',1),('Alchemistenfeuer',5)])
# --- KORVA: Schurke / Mensch ---
# Bogen: Delusional(minor)=Wahnvorstellungen_leicht, Hesitant(minor)=Zögerlich,
#   Obligation(major)=Verpflichtung_schwer
# Klasse: Schurke → auto: Hinterhältiger Angriff + Rüstungsbeschränkung_leicht
# Budget: 5AP + 4HP (Wahn1+Zöger1+Verpflicht2)
# Freies Talent: Berechnend, Freies Attribut: Verstand W4→W6
# Attribute: GEK W4→W6(1), VER W6→W8(1), WIL W4→W8(2), STÄ=0, KON=0 → 4AP, 1AP übrig
#   Aber STÄ soll W6, KON soll W6 → je W4→W6=1AP extra, beide mit HP

baue('Korva',
     klassentalent='Schurke',
     manual_handicaps=['Verpflichtung_schwer', 'Wahnvorstellungen_leicht', 'Zögerlich'],
     volk='Mensch',
     volk_wahlen=[{'typ':'freies_talent','wert':'Berechnend'},
                  {'typ':'freies_attribut','wert':'Verstand'}],
     soll_attr={'Geschicklichkeit':6, 'Verstand':8, 'Willenskraft':8, 'Stärke':6, 'Konstitution':6},
     soll_fert={'Athletik':6, 'Allgemeinwissen':4, 'Kämpfen':6, 'Wahrnehmung':6,
                'Darbietung':6, 'Überreden':6, 'Heimlichkeit':6, 'Provozieren':6, 'Diebeskunst':6},
     soll_handicaps=['Verpflichtung_schwer', 'Wahnvorstellungen_leicht', 'Zögerlich',
                     'Rüstungsbeschränkung_leicht'],
     soll_talente=['Schurke', 'Hinterhältiger Angriff', 'Berechnend', 'Elan'],
     soll_maechte=[],
     manual_talente=['Elan'],
     ausruestung=[('Kurzschwert',1),('Dolch',2),('Ledertunika',1),('Lederbeinlinge',1),('Diebeswerkzeug',1),('Abenteurerausrüstung',1),('Kletterausrüstung',1),('Trank: Abwehren',1)])
# --- PAELIE: Magier / Halbling ---
# Bogen: Greedy(minor)=Gierig_leicht, Poverty(minor)=Arm, Shamed(major)=Beschämt_schwer
# Klasse: AH (Magier) → auto: Arkane Verbindung, Schule, Zauberbücher + Behindernde Rüstung_jede
# Halbling: Glück (auto), Größe -1, GEK+Wahrnehmung+? Boni
# Budget: 5AP + 2HP (Gierig1+Arm1+Beschämt2=4 aber Arm+Poverty special? Arm=leicht=1HP,
#   aber Arm halbiert Startkapital → nur 1HP wert? Ja, jedes leichte=1HP. total=1+1+2=4HP)

baue('Paelie',
     klassentalent='AH (Magier)',
     manual_handicaps=['Beschämt_schwer', 'Gierig_leicht', 'Arm'],
     volk='Halbling',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':6, 'Verstand':8, 'Willenskraft':8, 'Stärke':4, 'Konstitution':6},
     soll_fert={'Geisteswissenschaften':6, 'Athletik':6, 'Allgemeinwissen':6, 'Kämpfen':6,
                'Glücksspiel':6, 'Wahrnehmung':6, 'Okkultismus':6, 'Überreden':4,
                'Schießen':6, 'Zaubern':8, 'Heimlichkeit':4},
     soll_handicaps=['Beschämt_schwer', 'Gierig_leicht', 'Arm',
                     'Behindernde Rüstung_jede', 'Größe -1 (Reduzierte Robustheit)'],
     soll_talente=['AH (Magier)', 'Arkane Verbindung', 'Schule', 'Zauberbücher',
                   'Glück', 'Arkane Resistenz'],
     soll_maechte=['Geschoss', 'Schutz'],
     manual_talente=['Arkane Resistenz'],
     ausruestung=[('Keule',1),('Dolch',3),('Zauberkomponentenbeutel',1),('Zauberbuch, Magier (leer)',1),('Abenteurerausrüstung',1),('Schriftrolle: Schlummer',1)])

# --- FARIEL: Druide / Elf ---
# Bogen: Bad Luck(major)=Pech, Loyal, Stubborn(minor)=Stur
# Klasse: AH (Druide) → auto: Bindung mit der Natur, Naturgespür, Schwur_schwer, Behindernde Rüstung_leicht
# Elf: Schlank, GEK W6, VER W6
# Budget: 5AP + 4HP (Pech2+Loyal1+Stur1)
# Attribute: GEK W6→W8(1), VER W6, WIL W4→W8(2), STÄ W4→W6(1), KON W4→W6(1) = 5AP
# Talente: Rückzug (Extraction) mit HP (2HP)
# Zyril elastic: KON elf -1 durch Schlank → effektiv W6-1? Nein, Schlank ist nur Fluff/Handicap
#   Im Bogen: Konstitution W6(-1). Das ist ein Flavour, kein echter Malus im deutschen System.

baue('Fariel',
     klassentalent='AH (Druide)',
     manual_handicaps=['Pech', 'Loyal', 'Stur'],
     volk='Elf',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':8, 'Verstand':6, 'Willenskraft':8, 'Stärke':6, 'Konstitution':6},
     soll_fert={'Athletik':6, 'Allgemeinwissen':4, 'Glaube':8, 'Kämpfen':6,
                'Heilen':6, 'Wahrnehmung':6, 'Überreden':4, 'Schießen':8,
                'Heimlichkeit':6, 'Überleben':6},
     soll_handicaps=['Pech', 'Loyal', 'Stur', 'Schlank',
                     'Schwur_schwer', 'Behindernde Rüstung_leicht'],
     soll_talente=['AH (Druide)', 'Bindung mit der Natur', 'Naturgespür', 'Rückzug'],
     soll_maechte=['Tierfreund', 'Verstricken'],
     manual_talente=['Rückzug'],
     ausruestung=[('Kompositbogen',1),('Pfeile (20)',1),('Ledertunika',1),('Abenteurerausrüstung',1),('Verstrickungsbeutel',1),('Trank: schwache Heilung',1),('Rauchstab',2)])

# --- MARN: Waldläufer / Halbork ---
# Bogen: Bloodthirsty(major)=Blutrünstig, Enemy(minor)=Feind_leicht, Ugly(minor)=Hässlich_leicht
# Klasse: Waldläufer → auto: Erzfeind, Bevorzugtes Gelände, Wildnis durchqueren + Rüstungsbeschränkung_mittelschwer
# Halbork: Außenseiter_leicht (auto), STÄ W6 (Strong)
# Budget: 5AP + 4HP (Blutr2+Feind1+Hässl1)
# Attribute: GEK W4→W8(2), VER W4, WIL W4→W6(1), STÄ W6→W8(1), KON W4→W6(1) = 5AP

baue('Marn',
     klassentalent='Waldläufer',
     manual_handicaps=['Blutrünstig', 'Feind_leicht', 'Hässlich_leicht'],
     volk='Halbork',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':8, 'Verstand':4, 'Willenskraft':6, 'Stärke':8, 'Konstitution':6},
     soll_fert={'Athletik':8, 'Allgemeinwissen':4, 'Kämpfen':8, 'Einschüchtern':6,
                'Wahrnehmung':4, 'Okkultismus':4, 'Überreden':4, 'Reiten':4,
                'Heimlichkeit':6, 'Überleben':6},
     soll_handicaps=['Blutrünstig', 'Feind_leicht', 'Hässlich_leicht',
                     'Rüstungsbeschränkung_mittelschwer', 'Außenseiter_leicht'],
     soll_talente=['Waldläufer', 'Erzfeind', 'Bevorzugtes Gelände', 'Wildnis durchqueren',
                   'Schnell', 'Rundumschlag'],
     soll_maechte=[],
     manual_talente=['Schnell', 'Rundumschlag'],
     ausruestung=[('Streitflegel',1),('Handaxt',3),('Schuppenpanzer',1),('Lederbeinlinge',1),('Abenteurerausrüstung',1),('Alchemistenfeuer',1)])
# --- GNORR: Zauberer / Zwerg ---
# Bogen: Driven(major)=Angetrieben_schwer, Mean(minor)=Fies, Quirk(minor)=Tick
# Klasse: AH (Zauberer) → auto: Blutlinie + Behindernde Rüstung_jede
# Budget: 5AP + 3HP (Angetrieben2+Fies1+Tick1=4)

baue('Gnor',
     klassentalent='AH (Zauberer)',
     manual_handicaps=['Angetrieben_schwer', 'Fies', 'Tick'],
     volk='Zwerg',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':6, 'Verstand':6, 'Willenskraft':8, 'Stärke':8, 'Konstitution':8},
     soll_fert={'Athletik':6, 'Allgemeinwissen':4, 'Kämpfen':6, 'Einschüchtern':6,
                'Wahrnehmung':6, 'Okkultismus':6, 'Überreden':4, 'Schießen':4,
                'Zaubern':8, 'Heimlichkeit':4},
     soll_handicaps=['Angetrieben_schwer', 'Fies', 'Tick', 'Behindernde Rüstung_jede'],
     soll_talente=['AH (Zauberer)', 'Blutlinie'],
     soll_maechte=['Eigenschaft erhöhen/senken'],
     ausruestung=[('Leichte Armbrust',1),('Bolzen (10)',2),('Abenteurerausrüstung',1),('Trank: schwache Heilung',1)])

# --- MADDA: Mönch / Halbork ---
# Bogen: Can't Swim(minor)=Nichtschwimmer, Heroic(major)=Heroisch, Small(minor)=Klein
# Klasse: Mönch → auto: Betäubende Fäuste, Beweglichkeit, Kämpferische Disziplin, Waffenloser Schlag
#   + Rüstungsbeschränkung_jede
# Halbork: Außenseiter_leicht, STÄ W6
# Budget: 5AP + 2HP (Nichtschw1+Hero2+Klein1=4)
# Attribute: GEK W4→W8(2), VER W4→W6(1), WIL=0, STÄ W6→W8(1), KON W4→W6(1) = 5AP
# Talent: Raufbold (Brawler) mit HP oder frei?

baue('Madda',
     klassentalent='Mönch',
     manual_handicaps=['Heroisch', 'Klein', 'Nichtschwimmer'],
     volk='Halbork',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':8, 'Verstand':6, 'Willenskraft':6, 'Stärke':8, 'Konstitution':6},
     soll_fert={'Athletik':8, 'Allgemeinwissen':4, 'Kämpfen':10, 'Heilen':6,
                'Einschüchtern':6, 'Wahrnehmung':6, 'Überreden':4, 'Heimlichkeit':6},
     soll_handicaps=['Heroisch', 'Klein', 'Nichtschwimmer',
                     'Rüstungsbeschränkung_jede', 'Außenseiter_leicht'],
     soll_talente=['Mönch', 'Betäubende Fäuste', 'Beweglichkeit', 'Kämpferische Disziplin',
                   'Waffenloser Schlag', 'Raufbold'],
     soll_maechte=[],
     manual_talente=['Raufbold'],
     ausruestung=[('Shuriken',6),('Krähenfüße',1),('Abenteurerausrüstung',1),('Alchemistenfeuer',3),('Sonnenzepter',1),('Trank: schwache Heilung',1)])
# --- SIL: Paladin / Elf ---
# Bogen: Code of Honor(major)=Ehrenkodex (AUTO von Paladin!), Loyal, Obligation(minor)=Verpflichtung_leicht,
#   Vow(major)=Schwur_schwer
# Klasse: Paladin → auto: Aura der Tapferkeit, Böses Entdecken, Böses Niederstrecken + Ehrenkodex
# Elf: Schlank, GEK W6, VER W6
# Budget: 5AP + 4HP (Ehrenkodex AUTO + Loyal1+Verpflicht1+Schwur2=4) — aber Paladin gibt Ehrenkodex auto
#   → nur 2HP von Loyal+Verpflicht? Oder zählt auto-Ehrenkodex zum HP-Limit?

baue('Sil',
     klassentalent='Paladin',
     manual_handicaps=['Loyal', 'Verpflichtung_leicht', 'Schwur_schwer'],
     volk='Elf',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':8, 'Verstand':6, 'Willenskraft':8, 'Stärke':8, 'Konstitution':6},
     soll_fert={'Athletik':6, 'Allgemeinwissen':6, 'Kämpfen':6, 'Wahrnehmung':6,
                'Okkultismus':4, 'Überreden':6, 'Reiten':8, 'Schießen':8, 'Heimlichkeit':4},
     soll_handicaps=['Ehrenkodex', 'Loyal', 'Verpflichtung_leicht', 'Schwur_schwer', 'Schlank'],
     soll_talente=['Paladin', 'Aura der Tapferkeit', 'Böses Entdecken', 'Böses Niederstrecken', 'Glück'],
     soll_maechte=[],
     manual_talente=['Glück'],
     ausruestung=[('Langschwert',1),('Kompositbogen',1),('Pfeile (20)',1),('Kettenhemd',1),('Lederbeinlinge',1),('Abenteurerausrüstung',1)])
# --- DARLA: Keine Klasse / Mensch ---
# Bogen: Can't Swim(minor)=Nichtschwimmer, Impulsive(major)=Impulsiv, Loyal
# Kein Klassentalent! Verwendet AH (Magie) als generischen arkanen Hintergrund
# Budget: 5AP + 4HP (Nichtschw1+Impulsiv2+Loyal1)
# Freies Talent: Auserwählter (Champion), Freies Attribut: Verstand W4→W6
# Talente: AH (Magie) mit 2HP

baue('Darla',
     klassentalent=None,
     manual_handicaps=['Impulsiv', 'Loyal', 'Nichtschwimmer'],
     volk='Mensch',
     volk_wahlen=[{'typ':'freies_attribut','wert':'Verstand'},
                  {'typ':'freies_talent','wert':'Auserwählter'}],
     freier_ah='AH (Magie)',
     soll_attr={'Geschicklichkeit':6, 'Verstand':8, 'Willenskraft':8, 'Stärke':6, 'Konstitution':6},
     soll_fert={'Athletik':4, 'Allgemeinwissen':6, 'Kämpfen':6, 'Wahrnehmung':6,
                'Okkultismus':6, 'Überreden':8, 'Reiten':4, 'Zaubern':8, 'Heimlichkeit':4},
     soll_handicaps=['Impulsiv', 'Loyal', 'Nichtschwimmer'],
     soll_talente=['AH (Magie)', 'Auserwählter'],
     soll_maechte=['Geschoss', 'Eigenschaft erhöhen/senken', 'Schutz'],
     ausruestung=[('Kurzschwert',1),('Leichte Armbrust',1),('Bolzen (10)',2),('Ledertunika',1),('Lederbeinlinge',1),('Abenteurerausrüstung',1),('Trank: schwache Heilung',1)])

# ===================================================================
# SET 3 — NOVICE
# ===================================================================

# --- DAMIEL: Alchemist / Elf ---
# Bogen: Favored Class(major)→✗(nicht im DE), Impulsive(major)=Impulsiv
# Klasse: Alchemist → auto: AH (Alchemist) + Behindernde Rüstung_leicht
# Elf: Schlank, GEK W6, VER W6
# Budget: 5AP + 2HP (nur Impulsiv2; Favored Class fehlt)
# Attribute: GEK W6→W8(1), VER W6→W8(1), WIL W4→W6(1), STÄ W4→W6(1), KON W4→W6(1) = 5AP
# Talente: Berechnend (Calculating)

baue('Damiel',
     klassentalent='Alchemist',
     manual_handicaps=['Impulsiv'],
     volk='Elf',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':8, 'Verstand':8, 'Willenskraft':6, 'Stärke':6, 'Konstitution':6},
     soll_fert={'Alchemie':8, 'Athletik':8, 'Allgemeinwissen':6, 'Kämpfen':8,
                'Wahrnehmung':6, 'Okkultismus':4, 'Überreden':6, 'Heimlichkeit':6, 'Diebeskunst':6},
     soll_handicaps=['Impulsiv', 'Schlank', 'Behindernde Rüstung_leicht'],
     soll_talente=['Alchemist', 'AH (Alchemist)', 'Berechnend'],
     soll_maechte=['Abwehren', 'Gestaltwandeln'],
     manual_talente=['Berechnend'],
     ausruestung=[('Rapier',1),('Dolch',1),('Ledertunika',1),('Lederbeinlinge',1),('Abenteurerausrüstung',1)])

# --- ALAIN: Kavalier / Mensch ---
# Bogen: Impulsive(major)=Impulsiv, Vengeful(minor)=Rachsüchtig_leicht, Vow(major)=Schwur_schwer
# Klasse: Kavalier → kein auto-Eintrag sichtbar (nur Kavalier selbst)
# Budget: 5AP + 4HP (Imp2+Rach1+Schwur2=5→cap4→Rach rejected? Oder Schwur schlägt fehl?)
#   Warten: Impulsiv=2, Rachsüchtig_leicht=1, Schwur_schwer=2 → total 5HP, cap 4.
#   Letztes Handicap rejected → dokumentieren

baue('Alain',
     klassentalent='Kavalier',
     manual_handicaps=['Impulsiv', 'Rachsüchtig_leicht', 'Schwur_schwer'],
     volk='Mensch',
     volk_wahlen=[{'typ':'freies_attribut','wert':'Konstitution'},
                  {'typ':'freies_talent','wert':'Lieblingswaffe'}],
     soll_attr={'Geschicklichkeit':8, 'Verstand':6, 'Willenskraft':6, 'Stärke':8, 'Konstitution':8},
     soll_fert={'Athletik':6, 'Kriegskunst':4, 'Allgemeinwissen':4, 'Kämpfen':8,
                'Wahrnehmung':6, 'Überreden':6, 'Reiten':6, 'Schießen':6,
                'Heimlichkeit':4, 'Überleben':4},
     soll_handicaps=['Impulsiv', 'Rachsüchtig_leicht', 'Schwur_schwer'],
     soll_talente=['Kavalier', 'Lieblingswaffe'],     ausruestung=[('Rapier',1),('Leichte Armbrust',1),('Bolzen (10)',2),('Ledertunika',1),('Lederbeinlinge',1),('Abenteurerausrüstung',1),('Trank: schwache Heilung',1),('Gegengift, Phiole',1)])

# --- IMRIJKA: Inquisitor / Halbork ---
# Bogen: Obligation(minor)=Verpflichtung_leicht, Outsider(minor)=Außenseiter_leicht (AUTO!),
#   Ruthless(minor)=Skrupellos_leicht, Stubborn(minor)=Stur, Vow(minor)=Schwur_leicht
# Klasse: Inquisitor → auto: Rüstungsbeschränkung_mittelschwer
# Halbork: Außenseiter_leicht + STÄ W6
# Budget: 5AP + 4HP — viele minors (4×1=4). Aber Außenseiter ist auto → nur 3HP von manuellen?
#   Verpflichtung1+Skrupellos1+Stur1+Schwur1=4 manuell → Außenseiter auto nicht zum Limit.
#   Wenn Außenseiter auto und 4 manuell → 5HP total, cap 4 → eines rejected.
#   Oder: Verpflichtung+Skrupellos+Stur+Schwur=4HP (alle vier je 1) → kein Reject nötig.

baue('Imrijka',
     klassentalent='Inquisitor',
     manual_handicaps=['Verpflichtung_leicht', 'Skrupellos_leicht', 'Stur', 'Schwur_leicht'],
     volk='Halbork',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':8, 'Verstand':6, 'Willenskraft':8, 'Stärke':6, 'Konstitution':6},
     soll_fert={'Athletik':6, 'Allgemeinwissen':6, 'Kämpfen':6, 'Einschüchtern':6,
                'Wahrnehmung':6, 'Okkultismus':4, 'Überreden':6, 'Schießen':8,
                'Heimlichkeit':4, 'Überleben':4},
     soll_handicaps=['Verpflichtung_leicht', 'Skrupellos_leicht', 'Stur', 'Schwur_leicht',
                     'Rüstungsbeschränkung_mittelschwer', 'Außenseiter_leicht'],
     soll_talente=['Inquisitor', 'Elan'],
     soll_maechte=[],
     manual_talente=['Elan'],
     ausruestung=[('Morgenstern',1),('Kurzbogen',1),('Pfeile (20)',1),('Dolch',1),('Schuppenpanzer',1),('Abenteurerausrüstung',1),('Heiliges Wasser',1),('Heiliges Symbol, Silber',1),('Sonnenzepter',1)])
# --- ALAHAZRA: Orakel / Mensch ---
# Bogen: Bad Luck(major)=Pech, Loyal, Poverty(minor)=Arm
# Klasse: AH (Orakel) → auto: Behindernde Rüstung_mittelschwer
# Budget: 5AP + 4HP (Pech2+Loyal1+Arm1)
# Freies Attribut: Willenskraft W4→W6, Freies Talent: ?
# Attribute: GEK W4→W6(1), VER W4→W6(1), WIL W6→W10(4? 2AP+2HP), STÄ=0, KON=0 → 
#   WIL W6→W8(1AP)+W8→W10(2HP) = 1AP+2HP. Plus STÄ/KON mit restlichen Punkten.

baue('Alahazra',
     klassentalent='AH (Orakel)',
     manual_handicaps=['Pech', 'Loyal', 'Arm'],
     volk='Mensch',
     volk_wahlen=[{'typ':'freies_attribut','wert':'Willenskraft'},
                  {'typ':'freies_talent','wert':'Glück'}],
     soll_attr={'Geschicklichkeit':6, 'Verstand':6, 'Willenskraft':10, 'Stärke':6, 'Konstitution':6},
     soll_fert={'Athletik':6, 'Allgemeinwissen':4, 'Glaube':10, 'Kämpfen':4,
                'Heilen':6, 'Wahrnehmung':6, 'Okkultismus':6, 'Überreden':6, 'Heimlichkeit':4},
     soll_handicaps=['Pech', 'Loyal', 'Arm', 'Behindernde Rüstung_mittelschwer'],
     soll_talente=['AH (Orakel)', 'Glück'],
     soll_maechte=['Arkanes entdecken/verbergen', 'Schutz vor Naturgewalten', 'Heilung'],
     ausruestung=[('Stab',1),('Schleuder',1),('Schleudersteine (20)',1),('Ledertunika',1),('Lederbeinlinge',1),('Abenteurerausrüstung',1)])

# --- BALAZAR: Beschwörer / Gnom ---
# BUG: AH (Beschwörer) kategorie=Hintergrund → NICHT als Klassentalent wählbar!
# Bogen: Enemy(major)=Feind_schwer, Poverty(minor)=Arm, Secret(minor)=Geheimnis_leicht
# Budget: 5AP + 4HP (Feind2+Arm1+Geheim1)
# Gnom: Gnomenmagie, Langsam_leicht, Größe -1, Zwanghaft
# Wird scheitern weil Klasse nicht wählbar → dokumentiert als BUG

baue('Balazar',
     klassentalent='Beschwörer',  # ← gefixt: neues Klassentalent (kategorie=Klasse)
     manual_handicaps=['Feind_schwer', 'Arm', 'Geheimnis_leicht'],
     volk='Gnom',
     volk_wahlen=[],
     soll_attr={'Geschicklichkeit':6, 'Verstand':8, 'Willenskraft':8, 'Stärke':4, 'Konstitution':6},
     soll_fert={'Athletik':4, 'Allgemeinwissen':6, 'Kämpfen':6, 'Heilen':4,
                'Wahrnehmung':6, 'Okkultismus':8, 'Überreden':4, 'Reiten':4,
                'Schießen':4, 'Zaubern':8, 'Heimlichkeit':4, 'Überleben':4},
     soll_handicaps=['Feind_schwer', 'Arm', 'Geheimnis_leicht',
                     'Langsam_leicht', 'Größe -1 (Reduzierte Robustheit)', 'Zwanghaft'],
     soll_talente=['Gnomenmagie'],
     soll_maechte=['Abwehren', 'Heilung'],
     ausruestung=[('Keule',1),('Dolch',1),('Handarmbrust',1),('Bolzen (10)',1),('Abenteurerausrüstung',1),('Sonnenzepter',3),('Schriftrolle: Geschoss',1)])

# --- FEIYA: Hexenmeister / Mensch ---
# Bogen: Driven(major)=Angetrieben_schwer, Enemy(minor)=Feind_leicht, Loyal
# Klasse: AH (Hexenmeister) → auto: Vertrauter + Behindernde Rüstung_jede
# Budget: 5AP + 4HP (Angetrieben2+Feind1+Loyal1)
# Freies Talent: Glück, Freies Attribut: Willenskraft W4→W6
# Talente: Wachsam (Alertness) mit 2HP

baue('Feiya',
     klassentalent='AH (Hexenmeister)',
     manual_handicaps=['Angetrieben_schwer', 'Feind_leicht', 'Loyal'],
     volk='Mensch',
     volk_wahlen=[{'typ':'freies_attribut','wert':'Willenskraft'},
                  {'typ':'freies_talent','wert':'Glück'}],
     soll_attr={'Geschicklichkeit':6, 'Verstand':8, 'Willenskraft':8, 'Stärke':6, 'Konstitution':6},
     soll_fert={'Athletik':4, 'Allgemeinwissen':6, 'Kämpfen':4, 'Heilen':6,
                'Einschüchtern':6, 'Wahrnehmung':6, 'Okkultismus':6, 'Überreden':4,
                'Zaubern':8, 'Heimlichkeit':4},
     soll_handicaps=['Angetrieben_schwer', 'Feind_leicht', 'Loyal', 'Behindernde Rüstung_jede'],
     soll_talente=['AH (Hexenmeister)', 'Vertrauter', 'Glück', 'Wachsam'],
     soll_maechte=['Eigenschaft erhöhen/senken', 'Schutz'],
     manual_talente=['Wachsam'],
     ausruestung=[('Stab',1),('Dolch',1),('Abenteurerausrüstung',1),('Heilertasche',1),('Verstrickungsbeutel',1),('Sonnenzepter',2),('Schriftrolle: Geschoss',2)])


# ===================================================================
# ZUSAMMENFASSUNG
# ===================================================================
m("\n" + "="*60)
m("ZUSAMMENFASSUNG")
m("="*60)
for r in all_results:
    status = "OK" if r.get('ok') else f"CRASH: {r.get('error','?')}"
    m(f"  {r['name']:25s} | {status:15s} | anomalien={r.get('anomalien','?')} | diff={len(r.get('diff',[]))}")

tlog.close()
print(f"Done. {len(all_results)} characters. See logs/spf_set23_v2_trace.txt")
