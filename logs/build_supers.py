# -*- coding: utf-8 -*-
"""Baut alle 11 Superkräfte-Archetypen (Texte/Superkräfte Archetypen.txt) wie ein User
über CharakterController (driver) + functions/superkraft_funktionen. Findet Bugs/Lücken.
Keys gegen die echten Setting-Listen aufgelöst (logs/resolve.py)."""
import sys, json, traceback
sys.path.insert(0, '.claude/skills/archetyp-erstellen')
import driver as d
import functions.superkraft_funktionen as sf

ATTR = {'Agi': 'Geschicklichkeit', 'Sma': 'Verstand', 'Spi': 'Willenskraft',
        'Str': 'Stärke', 'Vig': 'Konstitution'}

# Skill-Keys EN->DE (alle existieren im Setting)
SK = {'Athletik':'Athletik','Allgemeinwissen':'Allgemeinwissen','Fahren':'Fahren','Kämpfen':'Kämpfen',
      'Fokus':'Fokus','Einschüchtern':'Einschüchtern','Wahrnehmung':'Wahrnehmung','Überreden':'Überreden',
      'Schießen':'Schießen','Heimlichkeit':'Heimlichkeit','Provozieren':'Provozieren','Heilen':'Heilen',
      'Überleben':'Überleben','Elektronik':'Elektronik','Diebeskunst':'Diebeskunst','Hacken':'Hacken',
      'Recherche':'Recherche','Naturwissenschaften':'Naturwissenschaften','Geisteswissenschaften':'Geisteswissenschaften',
      'Okkultismus':'Okkultismus','Kriegskunst':'Kriegskunst','Darbietung':'Darbietung','Reiten':'Reiten'}

SPEC = [
 dict(name='Bogenschuetze', attr=dict(Agi=10,Sma=6,Spi=8,Str=6,Vig=8),
   skills={'Athletik':10,'Allgemeinwissen':6,'Fahren':6,'Kämpfen':10,'Fokus':6,'Einschüchtern':6,
           'Wahrnehmung':8,'Überreden':6,'Schießen':12,'Heimlichkeit':8,'Provozieren':6},
   hind=[('Heldenhaft','Heroic M'),('Skrupellos','Ruthless m'),('Rachsüchtig_leicht','Vengeful m')],
   edges=[(None,'Dead Shot'),('Rückzug','Extraction'),('Meisterschütze','Marksman'),('Schnell','Quick'),('Superkräfte','Super Powers')],
   powers=[('Kampfsinn',5),('Zielwasser',2),('Ausweichen',3),('Fesseln',1),('Fernkampfangriff',12),('Betäuben',7),('Superattribut',6),('Superfertigkeit',9)]),
 dict(name='Panzer', attr=dict(Agi=8,Sma=6,Spi=8,Str=12,Vig=12),
   skills={'Athletik':8,'Allgemeinwissen':4,'Fahren':6,'Kämpfen':12,'Fokus':6,'Einschüchtern':8,
           'Wahrnehmung':6,'Überreden':4,'Heimlichkeit':4,'Überleben':6},
   hind=[('Heldenhaft','Heroic M'),('Zwei linke Hände','All Thumbs m'),('Transformation (leicht)','Transformation m')],
   edges=[('Kräftig','Brawny'),('Rundumschlag','Sweep'),('Superkräfte','Super Powers')],
   powers=[('Panzerung',10),('Springen',4),('Nahkampfangriff',11),('Superattribut',20)]),
 dict(name='Schuetze', attr=dict(Agi=10,Sma=8,Spi=8,Str=8,Vig=8),
   skills={'Athletik':8,'Allgemeinwissen':6,'Elektronik':8,'Fahren':8,'Kämpfen':8,'Einschüchtern':10,
           'Wahrnehmung':6,'Überreden':4,'Schießen':12,'Heimlichkeit':6,'Diebeskunst':8},
   hind=[('Misstrauisch_schwer','Suspicious M'),('Vorsichtig','Cautious m'),('Skrupellos','Ruthless m')],
   edges=[(None,'Dead Shot'),('Doppelschuss','Double Tap'),('Rückzug','Extraction'),('Schwer zu töten','Hard to Kill'),('Meisterschütze','Marksman'),('Kühler Kopf','Level Headed'),('Schnell','Quick'),(None,'Rock and Roll'),('Superkräfte','Super Powers')],
   powers=[('Kampfsinn',5),('Zielwasser',3),('Ausweichen',5),('Parade',5),('Superattribut',8),('Supertalent',10),('Superfertigkeit',7),('Robustheit',2)]),
 dict(name='Eismann', attr=dict(Agi=8,Sma=6,Spi=8,Str=12,Vig=10),
   skills={'Athletik':8,'Allgemeinwissen':4,'Kämpfen':10,'Fokus':12,'Heilen':6,'Einschüchtern':6,
           'Wahrnehmung':6,'Überreden':6,'Heimlichkeit':8,'Überleben':8,'Provozieren':6},
   hind=[('Abhängigkeit','Dependency M'),('Umweltschwäche','Env. Weakness m'),('Angewohnheit_leicht','Quirk m')],
   edges=[('Eisenkiefer','Iron Jaw'),('Superkräfte','Super Powers')],
   powers=[('Umweltresistenz',7),('Materiekontrolle',12),('Fernkampfangriff',8),('Superattribut',10),('Superfertigkeit',5),('Robustheit',3)]),
 dict(name='Feuervogel', attr=dict(Agi=10,Sma=8,Spi=8,Str=6,Vig=6),
   skills={'Athletik':10,'Allgemeinwissen':6,'Elektronik':6,'Kämpfen':8,'Fokus':12,'Einschüchtern':8,
           'Wahrnehmung':6,'Überreden':6,'Heimlichkeit':6},
   hind=[('Impulsiv','Impulsive M'),('Umweltschwäche','Env. Weakness m'),('Loyal','Loyal m')],
   edges=[('Attraktiv','Attractive'),('Superkräfte','Super Powers')],
   powers=[('Ausweichen',5),('Umweltresistenz',3),('Fliegen',8),('Fernkampfangriff',20),('Superattribut',2),('Superfertigkeit',5),('Robustheit',2)]),
 dict(name='Hexe', attr=dict(Agi=6,Sma=12,Spi=8,Str=4,Vig=6),
   skills={'Geisteswissenschaften':6,'Athletik':6,'Allgemeinwissen':6,'Kämpfen':6,'Fokus':10,'Einschüchtern':10,
           'Wahrnehmung':8,'Okkultismus':8,'Überreden':6,'Heimlichkeit':6},
   hind=[('Neugierig','Curious M'),('Skrupellos','Ruthless m'),('Stur','Stubborn m')],
   edges=[('Glück','Luck'),('Superkräfte','Super Powers')],
   powers=[('Panzerung',4),('Eigenschaft erhöhen/senken',4),('Nachahmen',12),('Umweltresistenz',5),('Heilung',3),('Illusion',11),('Fernkampfangriff',6)]),
 dict(name='Detektiv', attr=dict(Agi=8,Sma=10,Spi=8,Str=10,Vig=10),
   skills={'Geisteswissenschaften':6,'Athletik':6,'Allgemeinwissen':8,'Fahren':8,'Elektronik':6,'Kämpfen':8,'Hacken':8,
           'Einschüchtern':10,'Wahrnehmung':10,'Überreden':6,'Recherche':8,'Schießen':8,'Heimlichkeit':8},
   hind=[('Neugierig','Curious M'),('Stur','Stubborn m'),('Hässlich','Ugly m')],
   edges=[('Aufmerksamkeit','Alertness'),(None,'Danger Sense'),('Bedrohlich','Menacing'),('Superkräfte','Super Powers')],
   powers=[('Kampfsinn',3),('Zielwasser',3),('Genie',3),('Geschärfte Sinne',1),('Nahkampfangriff',4),('Gedankenschild',3),('Parade',3),('Superattribut',10),('Superfertigkeit',15)]),
 dict(name='Schlaeger', attr=dict(Agi=10,Sma=6,Spi=6,Str=12,Vig=12),
   skills={'Athletik':8,'Allgemeinwissen':6,'Fahren':6,'Kämpfen':12,'Einschüchtern':6,'Wahrnehmung':6,
           'Darbietung':6,'Überreden':4,'Heimlichkeit':6,'Provozieren':8},
   hind=[('Arrogant','Arrogant M'),('Heldenhaft','Heroic M')],
   edges=[('Raufbold','Brawler/Bruiser'),('Rohling','Brute'),('Finte','Feint'),('Erstschlag','First Strike'),('Erniedrigen','Humiliate'),(None,'Mighty Blow'),('Superkräfte','Super Powers')],
   powers=[('Nahkampfangriff',11),('Parade',3),('Superattribut',20),('Supertalent',8),('Superfertigkeit',3)]),
 dict(name='Verteidiger', attr=dict(Agi=6,Sma=10,Spi=8,Str=6,Vig=8),
   skills={'Athletik':6,'Allgemeinwissen':6,'Fahren':6,'Elektronik':8,'Kämpfen':6,'Fokus':10,'Hacken':10,
           'Einschüchtern':6,'Wahrnehmung':6,'Überreden':6,'Naturwissenschaften':8,'Heimlichkeit':4},
   hind=[('Heldenhaft','Heroic M'),('Umweltschwäche','Env. Weakness m'),('Vorsichtig','Cautious m')],
   edges=[(None,'Command'),('Elan','Elan'),('Geborener Anführer','Natural Leader'),('Superkräfte','Super Powers')],
   powers=[('Panzerung',7),('Ausweichen',6),('Energiekontrolle',12),('Heilung',5),('Parade',6),('Superattribut',2),('Superfertigkeit',7)]),
 dict(name='Walkuere', attr=dict(Agi=8,Sma=6,Spi=8,Str=12,Vig=12),
   skills={'Athletik':6,'Kriegskunst':6,'Allgemeinwissen':6,'Kämpfen':12,'Einschüchtern':10,'Wahrnehmung':6,
           'Überreden':6,'Reiten':8,'Heimlichkeit':4,'Provozieren':6},
   hind=[('Impulsiv','Impulsive M'),('Angewohnheit_leicht','Quirk m'),('Stur','Stubborn m')],
   edges=[(None,'Command'),('Konter','Counterattack'),('Elan','Elan'),('Schnell','Quick'),('Superkräfte','Super Powers')],
   powers=[('Tiergefährte',13),('Nahkampfangriff',7),('Superattribut',14),('Superfertigkeit',6),('Robustheit',5)]),
 dict(name='Sprinter', attr=dict(Agi=10,Sma=8,Spi=6,Str=6,Vig=6),
   skills={'Athletik':10,'Allgemeinwissen':6,'Kämpfen':10,'Einschüchtern':6,'Wahrnehmung':8,'Überreden':6,
           'Recherche':6,'Naturwissenschaften':8,'Heimlichkeit':8,'Provozieren':6},
   hind=[('Geheimidentität','Secret Identity M'),('Schutzbefohlener (leicht)','Dependent m'),('Loyal','Loyal m')],
   edges=[('Erstschlag','First Strike'),('Konter','Counterattack'),('Schnell','Quick'),('Superkräfte','Super Powers')],
   powers=[('Ausweichen',2),('Nahkampfangriff',6),('Parade',4),('Schieben',4),('Fernkampfangriff',8),('Geschwindigkeit',16),('Superattribut',2),('Superfertigkeit',3)]),
]


def build(spec):
    rep = {'name': spec['name'], 'missing': [], 'powers': [], 'edges_false': [], 'hind_false': [],
           'trait_shortfall': [], 'errors': [], 'edges_auto_present': []}
    try:
        s = d.Sitzung('Superkräfte Kompendium', spec['name'], protokoll=f"logs/super_{spec['name']}.log")
        sf.setze_machtstufe(s.ch, 'III')
        for key, label in sorted(spec['hind'], key=lambda x: 0 if (x[0] and 'schwer' in x[0]) else 1):
            if key is None:
                rep['missing'].append('Handicap: ' + label); continue
            if key not in s.ch.handicaps:
                rep['missing'].append(f'Handicap-KEY fehlt: {key} ({label})'); continue
            r = s.handicap(key)
            if not r['ok']:
                rep['hind_false'].append([label, key])
        s.volk('Mensch')
        for a, z in spec['attr'].items():
            s.attribut_auf(ATTR[a], z)
        for a, z in spec['attr'].items():
            while s.ch.attribute[ATTR[a]].wuerfel.value < z and s.ch.verbleibende_handicap_punkte > 0:
                v0 = s.ch.attribute[ATTR[a]].wuerfel.value
                s.steigere_mit_handicap_attribut(ATTR[a])
                if s.ch.attribute[ATTR[a]].wuerfel.value == v0:
                    break
        for a, z in spec['attr'].items():
            iv = s.ch.attribute[ATTR[a]].wuerfel.value
            if iv < z:
                rep['trait_shortfall'].append(f'{ATTR[a]} W{iv}<W{z}')
        for f, z in spec['skills'].items():
            if f not in s.ch.fertigkeiten:
                rep['missing'].append('Fertigkeit-KEY fehlt: ' + f); continue
            s.fertigkeit_auf(f, z)
            iv = s.ch.fertigkeiten[f].wuerfel.value
            if iv < z:
                rep['trait_shortfall'].append(f'{f} W{iv}<W{z}')
        for key, label in spec['edges']:
            if key is None:
                rep['missing'].append('Edge: ' + label); continue
            if key not in s.ch.talente:
                rep['missing'].append(f'Edge-KEY fehlt: {key} ({label})'); continue
            if key in s.ch.selected_talente:
                rep['edges_auto_present'].append(key); continue
            r = s.talent(key)
            if not r['ok']:
                rep['edges_false'].append([label, key])
        for nm, ko in spec['powers']:
            try:
                res = sf.waehle_superkraft(s.ch, nm, ko)
            except Exception as e:
                res = 'EXC:' + repr(e)
            if res is not True:
                rep['powers'].append([nm, ko, res])
        rep['skp'] = f"{sf.berechne_gesamt_kosten(s.ch)}/{s.ch.superkraft_punkte_gesamt}"
        rep['selected_superkraefte'] = list(s.ch.selected_superkraefte)
        rep['anomalien'] = len(s.anomalien)
        s.speichern(f"chars/Archetypen/Archetyp_Superkraefte_{spec['name']}.json")
        s.bericht(f"logs/super_{spec['name']}_bericht.json")
    except BaseException as e:
        rep['errors'].append('CRASH: ' + repr(e) + '\n' + traceback.format_exc())
    return rep


summary = [build(sp) for sp in SPEC]
json.dump(summary, open('logs/supers_summary.json', 'w'), ensure_ascii=False, indent=1)
print('FERTIG', len(summary))
