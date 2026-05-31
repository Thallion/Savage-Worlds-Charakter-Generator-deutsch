import json
hand = json.load(open('/tmp/r_handicaps.json', encoding='utf-8'))
tal = json.load(open('/tmp/r_talente.json', encoding='utf-8'))
fert = json.load(open('/tmp/r_fertigkeiten.json', encoding='utf-8'))

def find(pool, *subs):
    res = []
    for s in subs:
        for x in pool:
            if s.casefold() in x.casefold() and x not in res:
                res.append(x)
    return res

# concept -> candidate substrings  (English archetype term : German guesses)
HIND = {
 'Heroic': ['Heldenhaft', 'Heroisch'],
 'Ruthless': ['Skrupellos', 'Bösartig', 'Niederträchtig'],
 'Vengeful': ['Rachsüchtig'],
 'AllThumbs': ['Zwei linke', 'Tollpatsch'],
 'Transformation': ['Verwandlung', 'Transformation'],
 'Cautious': ['Vorsichtig'],
 'Suspicious': ['Misstrauisch', 'Argwöhn'],
 'Dependency': ['Abhängigkeit'],
 'EnvWeakness': ['Umweltschwäche', 'Schwäche', 'Verwundbar'],
 'Quirk': ['Gewohnheit', 'Marotte', 'Mienenspiel'],
 'Loyal': ['Loyal'],
 'Impulsive': ['Impulsiv', 'Tollkühn'],
 'Curious': ['Neugierig'],
 'Stubborn': ['Stur', 'Hartnäckig'],
 'Ugly': ['Hässlich', 'Distinctive'],
 'Arrogant': ['Arrogant', 'Eingebildet'],
 'Dependent': ['Schützling', 'Abhängige Person'],
 'SecretIdentity': ['Geheime Identität', 'Identität'],
 'BigMouth': ['Großmaul', 'Plappermaul'],
 'Wanted': ['Wanted', 'Gesucht'],
}
EDGE = {
 'DeadShot': ['Sicherer Schütze', 'Dead Shot', 'Todesschütze'],
 'Extraction': ['Rückzug', 'Extraction', 'Entkommen'],
 'Marksman': ['Scharfschütze', 'Schütze'],
 'Quick': ['Schnell', 'Flink', 'Reaktionsschnell'],
 'Brawny': ['Markig', 'Kräftig'],
 'Sweep': ['Rundumschlag', 'Sweep'],
 'DoubleTap': ['Doppelschuss', 'Double Tap'],
 'HardToKill': ['Schwer zu töten', 'Zäher Hund'],
 'LevelHeaded': ['Besonnen', 'Kühler Kopf'],
 'RockAndRoll': ['Rock and Roll', 'Dauerfeuer'],
 'IronJaw': ['Eisenkiefer', 'Stahlkiefer', 'Nehmerqualitäten'],
 'Attractive': ['Attraktiv', 'Anziehend'],
 'Luck': ['Glück', 'Glückspilz'],
 'Alertness': ['Aufmerksam', 'Wachsam'],
 'DangerSense': ['Gefahrensinn', 'Gefahreninstinkt'],
 'Menacing': ['Bedrohlich', 'Einschüchternd'],
 'Brute': ['Rohling', 'Brocken', 'Schläger'],
 'Feint': ['Finte'],
 'FirstStrike': ['Erstschlag', 'Erster Schlag'],
 'Humiliate': ['Demütigen', 'Erniedrigen'],
 'MightyBlow': ['Mächtiger Schlag', 'Wuchtschlag', 'Kraftvoller'],
 'Command': ['Kommandant', 'Befehl', 'Kommando'],
 'Elan': ['Elan', 'Schwung'],
 'NaturalLeader': ['Geborener Anführer', 'Anführer', 'Führungsqual'],
 'Counterattack': ['Gegenangriff', 'Konter'],
 'BrawlerBruiser': ['Raufbold', 'Schläger', 'Brawler', 'Prügel'],
 'Block': ['Blocken', 'Block'],
 'Superkraefte': ['Superkräfte'],
 'AB_Super': ['Arkaner Hintergrund (Superkräfte)', 'Superkräfte'],
}
SKILL = {
 'Athletics': ['Athletik'], 'CommonKnowledge': ['Allgemeinwissen'], 'Driving': ['Fahren'],
 'Fighting': ['Kämpfen'], 'Focus': ['Fokus', 'Focus'], 'Intimidation': ['Einschüchtern'],
 'Notice': ['Wahrnehmung'], 'Persuasion': ['Überreden'], 'Shooting': ['Schießen'],
 'Stealth': ['Heimlichkeit'], 'Taunt': ['Provozieren'], 'Healing': ['Heilen'],
 'Survival': ['Überleben'], 'Electronics': ['Elektronik'], 'Thievery': ['Schlösser knacken', 'Diebes'],
 'Academics': ['Akademiker', 'Akademisch', 'Bildung'], 'Hacking': ['Hacken'],
 'Research': ['Nachforschung', 'Recherche'], 'Science': ['Wissenschaft'], 'Occult': ['Okkultismus'],
 'Battle': ['Schlacht', 'Kriegskunst'], 'Performance': ['Auftreten', 'Vorführen'], 'Repair': ['Reparieren'],
 'Riding': ['Reiten'],
}
out = {'HANDICAPS': {}, 'EDGES': {}, 'SKILLS': {}, 'MISSING': []}
for grp, src, pool in [('HANDICAPS', HIND, hand), ('EDGES', EDGE, tal), ('SKILLS', SKILL, fert)]:
    for c, cands in src.items():
        m = find(pool, *cands)
        out[grp][c] = m
        if not m:
            out['MISSING'].append(f'{grp}:{c}')
json.dump(out, open('/tmp/resolved.json', 'w'), ensure_ascii=False, indent=0)
print('done; missing=', len(out['MISSING']))
