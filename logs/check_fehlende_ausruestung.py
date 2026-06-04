#!/usr/bin/env python3
"""
Systematische Extraktion fehlender Ausrüstung aus Archetyp-Bögen.

Strategie:
1. Parse Archetyp-Texte (Texte/*Archetypen*) - DE und EN Varianten
2. Extrahiere GEAR/Ausrüstung-Sektion pro Archetyp
3. Versuche jedes Item im entsprechenden Setting-Katalog zu finden
4. Dokumentiere fehlende Items

Verwendung: python3 logs/check_fehlende_ausruestung.py
Output:    logs/fehlende_ausruestung_uebersicht.md
"""
import json
import os
import re
import sys
from collections import defaultdict


def load_settings():
    """Lade alle Settings und deren Equipment-Keys."""
    settings = {}
    for f in sorted(os.listdir('settings')):
        if f.endswith('.json'):
            with open(f'settings/{f}', 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            key = f.replace('.json', '')
            settings[key] = {
                'data': data,
                'ausruestung_keys': set(),
            }
            if 'ausruestung' in data:
                if isinstance(data['ausruestung'], dict):
                    settings[key]['ausruestung_keys'] = set(data['ausruestung'].keys())
                elif isinstance(data['ausruestung'], list):
                    settings[key]['ausruestung_keys'] = set(
                        item.get('name', '') for item in data['ausruestung']
                    )
    return settings


# Aliase: EN Bogen-Item → DE Katalog-Items (zur besseren Erkennung)
# Diese werden auf bekannte deutsche Begriffe gemappt; nicht gefundene Aliase
# zeigen fehlende Items an.
ITEM_ALIASES = {
    # SciFi Kompendium
    'body armor': ['körperpanzerung', 'armor', 'kampfanzug'],
    'body armor (+4)': ['körperpanzerung +4'],
    'body armor (+2)': ['körperpanzerung'],
    'armor': ['körperpanzerung', 'rüstung', 'lederrüstung', 'kettenhemd', 'kampfanzug'],
    'body suit (+2)': ['bodysuit', 'körperpanzerung'],
    'armor jacket': ['kevlarjacke'],
    'plate mail breastplate (+4)': ['plattenharnisch', 'brustharnisch'],
    'luchadore mask': ['maske'],
    'valkyrie sword': ['schwert', 'langschwert'],
    'parka': ['winterkleidung (mantel/parka)'],
    'molecular knife': ['molekularmesser', 'messer'],
    'molecular sword': ['molekularschwert'],
    'laser pistol': ['laserpistole'],
    'pistol': ['pistole', 'revolver'],
    'knife': ['messer', 'dolch'],
    'dagger': ['dolch'],
    'sword': ['schwert', 'langschwert', 'kurzschwert'],
    'staff': ['stab'],
    'mace': ['streitkolben', 'keule', 'morgenstern'],
    'heavy mace': ['streitkolben, schwer', 'keule, schwer'],
    'light mace': ['streitkolben, leicht', 'keule, leicht'],
    'spiked chain': ['stachelkette'],
    'meteor hammer': ['meteorhammer'],
    'spear': ['speer'],
    'shield': ['schild'],
    'bow': ['bogen'],
    'crossbow': ['armbrust'],
    'rifle': ['gewehr'],
    'sniper rifle': ['scharfschützengewehr', 'gewehr'],
    'shotgun': ['schrotflinte'],
    'assault rifle': ['sturmgewehr', 'gewehr'],
    'grenade': ['granate'],
    'heavy weapon': ['granatwerfer', 'flugkörper'],
    'commlink': ['commlink'],
    'cyberdeck': ['cyberdeck'],
    'data pad': ['persönliche datenassistenz'],
    'personal data device': ['persönliche datenassistenz'],
    'holy symbol': ['heiliges symbol'],
    'focus': ['fokus', 'arkaner fokus'],
    'scroll': ['schriftrolle'],
    'component pouch': ['komponentenbeutel'],
    'med kit': ['medikit'],
    'med scanner': ['medi-scanner'],
    'med gel': ['medi-gel'],
    'tool kit': ['werkzeugkoffer'],
    'crowbar': ['brecheisen'],
    'rope': ['seil'],
    'climbing gear': ['kletterausrüstung'],
    'grapple': ['enterhaken'],
    'grappling hook': ['enterhaken'],
    'thief tools': ['dietrich', 'diebeswerkzeug'],
    'lockpick': ['dietrich'],
    'scanner': ['scanner'],
    'universal battery': ['batterie, universal-'],
    'translator': ['universalübersetzer'],
    'battery': ['batterie, universal-'],
    'field pack': ['abenteurerpaket', 'feldrucksack'],
    'backpack': ['rucksack'],
    'cloak': ['umhang', 'cape', 'kapuzenumhang'],
    'manacles': ['handschellen'],
    'binoculars': ['fernrohr', 'fernglas'],
    'ammo': ['munition', 'patronen'],
    'ammunition': ['munition', 'patronen'],
    'arrows': ['pfeile'],
    'chain': ['kettenhemd'],
    'spacesuit': ['raumanzug'],
    'space suit': ['raumanzug'],
    'red dot sight': ['rotpunktvisier', 'laser-/rotpunktvisier'],
    'adhesive patches': ['klebstoffpflaster'],
    'adhesive patch': ['klebstoffpflaster'],
    'street bike': ['chieftain-straßenbike', 'motorrad'],
    'chieftain street bike': ['chieftain-straßenbike'],
    'magnet boots': ['magnetstiefel'],
    'magnetstiefel': ['magnetstiefel'],
    'molecular knife': ['molekularmesser', 'messer'],
    'mask': ['maske'],
    'clothing': ['kleidung', 'umhang'],
    'trench coat': ['trenchcoat'],
    'armor (medium)': ['kettenhemd', 'lederrüstung'],
    'plate mail': ['plattenrüstung'],
    'leather tunic': ['ledertunika'],
    'leather armor': ['lederrüstung'],
    'studded leather': ['beschlagene lederrüstung'],
    'studded leather armor': ['beschlagene lederrüstung'],
    'chain shirt': ['kettenhemd'],
    'chainmail': ['kettenhemd'],
    'chain armor': ['kettenhemd'],
    'scale mail': ['schuppenpanzer'],
    'breastplate': ['brustharnisch'],
    'banded mail': ['brigantine'],
    'half plate': ['halbe plattenrüstung'],
    'full plate': ['volle plattenrüstung'],
    'mithral chain shirt': ['mithral-kettenhemd', 'kettenhemd'],
    'mithral scale': ['mithral-schuppenpanzer'],
    'mithral banded': ['mithral-brigantine'],
    'natural armor (+2)': ['natürliche rüstung'],
    'leather (1)': ['lederrüstung'],
    'heavy shield': ['schwerer schild'],
    'light shield': ['leichter schild'],
    'tower shield': ['turmschild'],
    'medium shield': ['mittlerer schild'],
    'holy water': ['heiliges wasser'],
    'cleric\'s pack': ['klerikerpaket'],
    'cleric\'s kit': ['klerikerpaket'],
    'wilderness pack': ['wildnispaket'],
    'wilderness kit': ['wildnispaket'],
    'mage\'s pack': ['magierpaket'],
    'entertainer\'s pack': ['unterhaltungspaket'],
    'adventurer\'s pack': ['abenteurerpaket'],
    'adventurer pack': ['abenteurerpaket'],
    'adventurer\'s lantern': ['abenteurerlaterne'],
    'smokestick': ['rauchstäbchen'],
    'smoke stick': ['rauchstäbchen'],
    'thieves tools': ['diebeswerkzeug', 'dietrich'],
    'thief tools': ['diebeswerkzeug', 'dietrich'],
    'masterwork great axe': ['streitaxt', 'zweihandaxt'],
    'great axe': ['streitaxt', 'zweihandaxt'],
    'hand axe': ['handaxt'],
    'short sword': ['kurzschwert'],
    'shortsword': ['kurzschwert'],
    'long sword': ['langschwert'],
    'longsword': ['langschwert'],
    'masterwork rapier': ['florett'],
    'rapier': ['florett'],
    'greatclub': ['großer knüppel', 'knüppel'],
    'bite/claws': ['biss', 'klauen'],
    'cloth tunic': ['stofftunika', 'tunika'],
    'whip': ['peitsche'],
    'torch': ['fackel'],
    'lantern': ['laterne'],
    'bedroll': ['schlafsack'],
    'rations': ['rationen'],
    'waterskin': ['wasserschlauch'],
    'rope (50)': ['seil'],
    'tent': ['zelt'],
    'sling': ['schleuder'],
    'sap': ['knüppel'],
    'sling bullets (20)': ['schleuderkugeln'],
    'javelin': ['wurfspeer'],
    'warhammer': ['kriegshammer'],
    'kukri': ['kukri'],
    'kama': ['kama'],
    'scythe': ['sense'],
    'falchion': ['falkenklinge'],
    'glaive': ['gleve'],
    'halberd': ['hellebarde'],
    'lance': ['lanze'],
    'morningstar': ['morgenstern'],
    'pike': ['pike'],
    'trident': ['dreizack'],
    'flail': ['flegel'],
    'longbow': ['langbogen'],
    'shortbow': ['kurzbogen'],
    'composite shortbow': ['verbundkurzbogen'],
    'composite longbow': ['verbundlangbogen'],
    'horse': ['pferd', 'streitross'],
    'riding horse': ['reitpferd'],
    'warhorse': ['streitross'],
    'saddle': ['sattel'],
    'saddlebags': ['satteltaschen'],
    'saddle blanket': ['satteldecke'],
    'thieves tools': ['diebeswerkzeug', 'dietrich'],
    'grappling hook': ['enterhaken'],
    'tent': ['zelt'],
    'tinderbox': ['feuerstein'],
    'lantern (hooded)': ['laterne'],
    'spyglass': ['fernrohr'],
    'magnifying glass': ['lupe'],
    'spellbook': ['zauberbuch'],
    'component pouch': ['komponentenbeutel'],
    'holy symbol': ['heiliges symbol'],
    'unholy symbol': ['unheiliges symbol'],
    'potion of healing': ['heiltrank'],
    'potion of growth': ['trank: vergrößerung'],
    'potion of invisibility': ['trank: unsichtbarkeit'],
    'potion of night vision': ['trank: nachtsicht'],
    'potion of speed': ['trank: beschleunigung'],
    'potion of wall climbing': ['trank: wandkrabbler'],
    'potion of environmental protection': ['trank: umgebungsschutz'],
    'scroll of fireball': ['schriftrolle: feuerball'],
    'wand of magic missile': ['stab: magisches geschoss'],
    'wand of fireball': ['stab: feuerball'],
    'cell phone': ['mobiltelefon'],
    'cellphone': ['mobiltelefon'],
    'phone': ['mobiltelefon'],
    'car': ['auto'],
    'motorcycle': ['motorrad'],
    'tech bike': ['motorrad'],
    'sports car': ['sportwagen'],
    'truck': ['lkw'],
    'van': ['lieferwagen'],
    'laptop': ['laptop'],
    'micro-fusion generator': ['energiepaket'],
    'bionic arm': ['kybernetischer arm'],
    'reinforced clothing': ['verstärkte kleidung'],
    'sword cane': ['stockdegen'],
    'cane': ['spazierstock'],
    'armor (3)': ['körperpanzerung'],
    'energy cell': ['energiepaket'],
    'gear': ['ausrüstung'],
    'katana': ['katana'],
    'rapier': ['florett'],
    'sabre': ['säbel'],
    'saber': ['säbel'],
    'sling': ['schleuder'],
    'syringe': ['spritze'],
    'first aid kit': ['erste-hilfe-kasten'],
    'zipline': ['seil'],
    'gauntlets': ['handschuhe'],
    'syringe (healing)': ['spritze'],
    'enchanted clothing': ['umhang'],
    'power armor': ['kampfanzug', 'körperpanzerung'],
    'hooded lantern': ['laterne'],
    'bullseye lantern': ['starklichtlaterne'],
    'rations (1 day)': ['rationen'],
    'rations (1 week)': ['rationen'],
    'firearm': ['feuerwaffe'],
    'firearm (modern)': ['feuerwaffe'],
    'firearm (ancient)': ['feuerwaffe'],
    'pocket laser': ['laserpistole'],
    'monoblade': ['molekularschwert'],
    'bullets': ['munition', 'patronen'],
    'auto-pistol': ['pistole'],
    'small arms': ['pistole'],
    'longarm': ['gewehr'],
    'plasmapistole': ['plasmapistole'],
    'plasma pistol': ['plasmapistole'],
    'plasma rifle': ['plasmagewehr'],
    'laser rifle': ['lasergewehr'],
    'blaster pistol': ['blasterpistole'],
    'blaster rifle': ['blastergewehr'],
    'heavy blaster pistol': ['schwere blasterpistole'],
    'energy sword': ['laserschwert'],
    'force sword': ['laserschwert'],
    'force pike': ['energiespeer'],
    'pulse cannon': None,  # not in catalog
    'railgun': None,  # not in catalog
    'drone': ['drohne'],
    'restraints': ['handschellen'],
    'spore': None,  # biologische waffe
    'fleshcraw': None,
    'camouflage suit': ['tarnanzug'],
    'ninja suit': None,
    'ranger armor': None,
    'combat armor': ['kampfanzug'],
    'armor jacket': ['kevlarjacke'],
    'rifle sling': ['gewehrriemen'],
    'mesh armor': ['synth-mesh'],
    'nanowear': ['nanowear'],
    'environment wear': ['tarnanzug'],
    'vibro-blade': ['vibro-klinge'],
    'vibro-sword': ['vibro-schwert'],
    'main-gauche': ['paradedolch'],
    'main gauche': ['paradedolch'],
    'dueling sword': ['duellschwert'],
    'buckler': ['faustschild'],
    'armor (2)': ['körperpanzerung'],
    'armor (1)': ['körperpanzerung'],
    'hand crossbow': ['handarmbrust'],
    'fire bolt': ['brandbolzen'],
    'flame arrow': ['brandpfeil'],
    'throwing knife': ['wurfmesser'],
    'padded armor': ['gepolsterte rüstung'],
    'hide armor': ['lederrüstung'],
    'robes': ['robe', 'umhang'],
    'robe': ['robe', 'umhang'],
    'mystic clothing': ['umhang'],
    'clothes': ['kleidung'],
    'common clothes': ['gewöhnliche kleidung'],
    'fine clothes': ['feine kleidung'],
    'royal clothes': ['königliche kleidung'],
    'traveling clothes': ['reisekleidung'],
    'wizard robes': ['magierrobe'],
    'wizard robe': ['magierrobe'],
    'dress': ['kleid'],
    'jewelry': ['schmuck'],
    'gem': ['edelstein'],
    'gold': ['gold'],
    'silver': ['silber'],
    'lockpick set': ['dietrich'],
    'thieves\' tools': ['diebeswerkzeug', 'dietrich'],
    'thieve\'s tools': ['diebeswerkzeug', 'dietrich'],
    'cellphone': ['mobiltelefon'],
    'smart phone': ['mobiltelefon'],
    'communicator': ['commlink'],
    'hover bike': ['schwebebike'],
    'hoverbike': ['schwebebike'],
    'speeder': ['speeder'],
    'scooter': ['roller'],
    'rifle sling': ['gewehrriemen'],
    'sniper rifle': ['scharfschützengewehr'],
    'rifle with scope': ['gewehr mit zielfernrohr'],
    'submachine gun': ['maschinenpistole'],
    'submachinegun': ['maschinenpistole'],
    'assault rifle': ['sturmgewehr'],
    'plasma cannon': None,  # not in catalog
    'gravity gun': None,  # not in catalog
    'wrist rocket': None,  # not in catalog
    'wrist blaster': None,  # not in catalog
    'jet pack': None,  # not in catalog
    'rocket pack': None,  # not in catalog
    'wings': None,  # special ability
    'glider': None,  # not in catalog
    'wrist blades': None,  # special
    'whip': ['peitsche'],
    'chain whip': ['kettepeitsche'],
    'energy whip': None,
    'garrote': ['garotte'],
    'garrotte': ['garotte'],
    'sling stone': ['schleuderkugel'],
    'sling bullet': ['schleuderkugel'],
    'stone': ['stein'],
    'rock': ['stein'],
    'throwing stone': ['wurfstein'],
    'boulder': ['felsblock'],
    'boulder (small)': ['kleiner felsblock'],
    'boulder (medium)': ['mittlerer felsblock'],
    'boulder (large)': ['großer felsblock'],
    'rock (small)': ['kleiner stein'],
    'rock (medium)': ['mittlerer stein'],
    'rock (large)': ['großer stein'],
    'cart': ['karren'],
    'carriage': ['kutsche'],
    'wagon': ['wagen'],
    'caravan': ['karawane'],
    'carriage (closed)': ['geschlossene kutsche'],
    'carriage (open)': ['offene kutsche'],
    'carriage (royal)': ['königliche kutsche'],
    'carriage (war)': ['kriegskutsche'],
    'carriage (prison)': ['gefängniswagen'],
    'carriage (hearse)': ['leichenwagen'],
    'carriage (mail)': ['postkutsche'],
    'carriage (stage)': ['postkutsche'],
    'carriage (private)': ['private kutsche'],
    'carriage (public)': ['öffentliche kutsche'],
    'carriage (taxi)': ['taxi'],
    'carriage (omnibus)': ['omnibus'],
    'carriage (tram)': ['straßenbahn'],
    'carriage (trolley)': ['straßenbahn'],
    'carriage (bus)': ['bus'],
    'carriage (van)': ['lieferwagen'],
    'carriage (truck)': ['lkw'],
    'carriage (semi)': ['sattelzug'],
    'carriage (trailer)': ['anhänger'],
    'carriage (boat)': ['boot'],
    'carriage (ship)': ['schiff'],
    'carriage (plane)': ['flugzeug'],
    'carriage (helicopter)': ['hubschrauber'],
    'carriage (submarine)': ['u-boot'],
    'carriage (rocket)': ['rakete'],
    'carriage (satellite)': ['satellit'],
    'carriage (spacecraft)': ['raumschiff'],
    'carriage (starship)': ['sternenschiff'],
    'carriage (fighter)': ['jäger'],
    'carriage (bomber)': ['bomber'],
    'carriage (transport)': ['transporter'],
    'carriage (cargo)': ['frachtschiff'],
    'carriage (passenger)': ['passagierschiff'],
    'carriage (cruise)': ['kreuzfahrtschiff'],
    'carriage (yacht)': ['yacht'],
    'carriage (sailboat)': ['segelboot'],
    'carriage (rowboat)': ['ruderboot'],
    'carriage (canoe)': ['kanu'],
    'carriage (kayak)': ['kajak'],
    'carriage (raft)': ['floß'],
    'carriage (dinghy)': ['beiboot'],
    'carriage (lifeboat)': ['rettungsboot'],
    'carriage (ferry)': ['fähre'],
    'carriage (tanker)': ['tanker'],
    'carriage (battleship)': ['kriegsschiff'],
    'carriage (carrier)': ['flugzeugträger'],
    'carriage (destroyer)': ['zerstörer'],
    'carriage (submarine)': ['u-boot'],
    'carriage (torpedo)': ['torpedo'],
    'carriage (mine)': ['seemine'],
    'carriage (depth charge)': ['wasserbombe'],
    'carriage (grenade)': ['granate'],
    'carriage (shell)': ['granate'],
    'carriage (bullet)': ['kugel'],
    'carriage (rocket)': ['rakete'],
    'carriage (missile)': ['flugkörper'],
    'carriage (torpedo)': ['torpedo'],
    'carriage (bomb)': ['bombe'],
    'carriage (nuke)': ['nuklearwaffe'],
    'carriage (drone)': ['drohne'],
    'carriage (robot)': ['roboter'],
    'carriage (mech)': ['mech'],
    'carriage (suit)': ['anzug'],
    'carriage (armor)': ['rüstung'],
    'carriage (mecha)': ['mecha'],
    'carriage (power armor)': ['kampfpanzer', 'kampfanzug'],
    'carriage (jetpack)': ['düsenrucksack'],
    'carriage (rocket boots)': ['raketenstiefel'],
    'carriage (magnet boots)': ['magnetstiefel'],
    'carriage (anti-gravity boots)': ['antigravitationsstiefel'],
    'carriage (jump boots)': ['sprungstiefel'],
    'carriage (spring boots)': ['federnde stiefel'],
    'carriage (roller skates)': ['rollschuhe'],
    'carriage (roller blades)': ['inlineskates'],
    'carriage (skateboard)': ['skateboard'],
    'carriage (scooter)': ['roller'],
    'carriage (bicycle)': ['fahrrad'],
    'carriage (motorcycle)': ['motorrad'],
    'carriage (moped)': ['moped'],
    'carriage (car)': ['auto'],
    'carriage (taxi)': ['taxi'],
    'carriage (limousine)': ['limousine'],
    'carriage (sportscar)': ['sportwagen'],
    'carriage (race car)': ['rennwagen'],
    'carriage (rally car)': ['rallye-auto'],
    'carriage (off-road)': ['geländewagen'],
    'carriage (4x4)': ['geländewagen'],
    'carriage (jeep)': ['jeep'],
    'carriage (suv)': ['suv'],
    'carriage (van)': ['lieferwagen'],
    'carriage (minivan)': ['kleinbus'],
    'carriage (pickup)': ['pickup'],
    'carriage (truck)': ['lkw'],
    'carriage (semi)': ['sattelzug'],
    'carriage (trailer)': ['anhänger'],
    'carriage (tractor)': ['traktor'],
    'carriage (bulldozer)': ['bulldozer'],
    'carriage (crane)': ['kran'],
    'carriage (excavator)': ['bagger'],
    'carriage (loader)': ['lader'],
    'carriage (dump truck)': ['kipplaster'],
    'carriage (cement mixer)': ['betonmischer'],
    'carriage (forklift)': ['gabelstapler'],
    'carriage (cherry picker)': ['hubarbeitsbühne'],
    'carriage (fire truck)': ['feuerwehrwagen'],
    'carriage (ambulance)': ['krankenwagen'],
    'carriage (police car)': ['polizeiauto'],
    'carriage (armored)': ['gepanzertes auto'],
    'carriage (tank)': ['panzer'],
    'carriage (apc)': ['spähpanzer'],
    'carriage (ifv)': ['schützenpanzer'],
    'carriage (artillery)': ['artillerie'],
    'carriage (howitzer)': ['haubitze'],
    'carriage (cannon)': ['kanone'],
    'carriage (mortar)': ['mörser'],
    'carriage (catapult)': ['katapult'],
    'carriage (ballista)': ['ballista'],
    'carriage (trebuchet)': ['trebuchet'],
    'carriage (siege tower)': ['belagerungsturm'],
    'carriage (battering ram)': ['rammbock'],
    'carriage (siege engine)': ['belagerungsmaschine'],
    'carriage (mantlet)': ['mantel'],

    # ══ EN→DE Brücken zu BEREITS vorhandenen Katalog-Keys (2026-06-04) ══
    # Die deutschen Items existieren bereits in settings/*.json — nur die
    # englischen Bogen-Begriffe fanden bisher keinen Alias. Werte = Wortgrenzen-
    # Substrings der echten Katalog-Keys (lowercase).
    # — Fantasy Kompendium —
    'acid flask': ['säureflasche'],
    "alchemist's pack": ['alchemistenpaket'],
    'antitoxin': ['gegengift'],
    'blowgun': ['blasrohr'],
    'blowgun darts': ['blasrohrpfeile'],
    '10 blowgun darts': ['blasrohrpfeile'],
    'bolts': ['bolzen'],
    '20 bolts': ['bolzen'],
    'book': ['buch'],
    'boots': ['stiefel'],
    'heavy boots': ['stiefel, schwer'],
    'bronze armor and helmet': ['bronzebrustpanzer'],
    'caltrops': ['krähenfüße'],
    'cloak w/hood': ['umhang mit kapuze'],
    'light cloak w/hood': ['umhang, leicht'],
    'cloak with hood': ['umhang mit kapuze'],
    'composite bow': ['kompositbogen'],
    'masterwork composite bow': ['kompositbogen'],
    'dagger': ['dolch'],
    'daggers': ['dolch'],
    'eight daggers': ['dolch'],
    "dungeoneer's pack": ['gewölbeforscherpaket'],
    'enclosed heavy helm': ['schwerer geschlossener helm'],
    "entertainer's pack": ['unterhalterpaket'],
    'flail': ['streitflegel'],
    'flammable arrows': ['brandpfeile'],
    '3 flammable arrows': ['brandpfeile'],
    'hide tunic': ['ledertunika'],
    "mercenary's pack": ['söldnerpaket'],
    'musical instrument': ['musikinstrument'],
    'natural armor': ['natürlicher rüstung'],
    'plate mail': ['plattenbrustharnisch'],
    'masterwork plate mail': ['plattenbrustharnisch'],
    'riding tack': ['reitbedarf'],
    'sap': ['totschläger'],
    'smokestick': ['rauchstab'],
    'tanglefoot bag': ['verstrickungsbeutel'],
    "thief's pack": ['diebespaket'],
    'thunderstone': ['donnerstein'],
    'tindertwig': ['zündholz'],
    'trapmaking kit': ['fallenherstellungsset'],
    'tunic': ['tunika'],
    'cloth tunic': ['tunika'],
    'leather tunic': ['ledertunika'],
    'masterwork leather tunic': ['ledertunika'],
    'weighted net': ['netz'],
    'holy water': ['heiliges wasser'],
    'vials of holy water': ['heiliges wasser'],
    'two vials of holy water': ['heiliges wasser'],
    'three vials of holy water': ['heiliges wasser'],
    'potion of healing': ['trank: heilung', 'heiltrank'],
    'potion of haste': ['trank: beschleunigung'],
    'potion of speed': ['trank: beschleunigung'],
    'potion of boost trait': ['trank: attributsteigerung'],
    'scroll of invisibility': ['schriftrolle: unsichtbarkeit'],
    'scroll of protection': ['schriftrolle: schutz'],
    'scroll of arcane protection': ['schriftrolle: arkaner schutz'],
    'scroll of summon ally': ['schriftrolle: verbündeten beschwören'],
    'scroll of teleport': ['schriftrolle: teleportation'],
    'scroll of boost trait': ['schriftrolle: eigenschaft erhöhen/senken'],
    'scroll of mind link': ['schriftrolle: gedankenverbindung'],
    # — SciFi Kompendium —
    'claws': ['cyberware: klauen'],
    'commercial drone': ['drohne, kommerziell'],
    'cutting torch': ['schweißbrenner'],
    'cybernetic eyes': ['cyberware: verbesserte sicht'],
    'directional microphone': ['direktionales mikrofon'],
    'flashlight': ['taschenlampe'],
    'formal clothing': ['kleidung, formell'],
    'goggles': ['schutzbrille'],
    'welding goggles': ['schutzbrille'],
    'hand axe': ['handaxt', 'handbeil'],
    'bastard sword': ['bastardschwert'],
    "alchemist's fire": ['alchemistenfeuer'],
    'chalk of spirit warding': ['kreide'],
    'fetish staff': ['stab'],
    'heartwood staff': ['stab'],
    'tower shield': ['großer schild'],
    'spiked tower shield': ['großer schild'],
    'war horse': ['streitross'],
    'war horse with padded barding': ['streitross'],
    'laser pistol with weapon lock': ['laserpistole'],
    'potions of healing': ['trank: heilung'],
    # neu in settings/Fantasy Kompendium.json angelegt (2026-06-04)
    "assassin's brew": ['mörderbräu'],
    'ether': ['äther'],
    'lotus dust': ['lotusstaub'],
    'green slime extract': ['grüner schleimextrakt'],
    'giant snake poison': ['riesenschlangengift'],
    'locked gauntlets': ['beriemter panzerhandschuh'],
    'armor spikes': ['rüstungsstacheln'],
    # Kategorien vorhandener Rüstung (studded leather = +2 Leder, scale = +3 Kette)
    'studded leather armor': ['ledertunika'],
    'studded leather': ['ledertunika'],
    'scale shirt': ['kettenhemd'],
    'masterwork scale shirt': ['kettenhemd'],
    'tunic and heavy hooded cloak': ['tunika'],
    'kevlar jacket': ['kevlarjacke'],
    'language translator': ['universalübersetzer'],
    'rebreather': ['kreislaufatemgerät'],
    'stun baton': ['betäubungsschlagstock'],
    'stun grenade': ['betäubungsgranate'],
    'switchblade': ['springmesser'],
    'toolkit': ['werkzeugkoffer'],
    'tool kit': ['werkzeugkoffer'],
    'electronic lockpick': ['dietriche'],
    'automatic shotgun': ['doppelflinte'],
    'camouflage suit': ['tarnanzug'],
}


# Erwartete Items pro Setting + Archetyp
# Struktur: setting_key -> {archetyp_name_normalized: [items]}
# Items hier sind kanonische Bogen-Namen, die via ITEM_ALIASES aufgelöst werden

SCIFI_EXPECTED = {
    'COMMANDER': ['body armor', 'laser pistol', 'molecular knife', 'biolink',
                  'personal data device', 'universal battery', 'commlink', 'grenade',
                  'molecular sword'],
    'PSYKER': ['sword', 'chain', 'dagger', 'throwing knife',
               'mystic clothing', 'focus', 'holy symbol'],
    'SURVEYOR': ['sniper rifle', 'knife', 'armor', 'rope', 'grappling hook', 'rifle'],
    'AMBASSADOR': ['laser pistol', 'knife', 'armor', 'cloak', 'commlink', 'translator'],
    'HACKER': ['pistol', 'knife', 'armor', 'commlink', 'cyberdeck', 'data pad',
               'scanner', 'med kit', 'rope'],
    'INFILTRATOR': ['pistol', 'knife', 'armor', 'thief tools', 'lockpick', 'climbing gear', 'grapple'],
    'INFLUENCER': ['pistol', 'knife', 'armor', 'commlink', 'translator'],
    'MERCENARY': ['assault rifle', 'pistol', 'knife', 'armor', 'grenade', 'field pack'],
    'ROUGHNECK': ['laser pistol', 'knife', 'armor', 'tool kit', 'rope'],
    'MYSTIC': ['staff', 'knife', 'armor', 'mystic clothing', 'focus', 'holy symbol', 'scroll', 'component pouch'],
    'MORPHER': ['pistol', 'knife', 'armor', 'commlink', 'tool kit'],
    'SPACER': ['body armor', 'spacesuit', 'knife', 'commlink', 'battery', 'red dot sight', 'adhesive patches'],
    'AI CONTROLLER': ['commlink', 'cyberdeck', 'data pad', 'tool kit', 'scanner'],
    'ANALYST': ['pistol', 'knife', 'armor', 'commlink', 'data pad', 'scanner'],
    'BOUNTY HUNTER': ['pistol', 'shotgun', 'knife', 'armor', 'manacles', 'field pack'],
    'ENGINEER': ['pistol', 'knife', 'armor', 'tool kit', 'med kit', 'rope'],
    'ENFORCER': ['pistol', 'knife', 'armor', 'grenade'],
    'ENVOY': ['pistol', 'knife', 'armor', 'commlink', 'translator'],
    'GLADIATOR': ['sword', 'knife', 'armor', 'shield', 'spear'],
    'GRUNT': ['assault rifle', 'pistol', 'knife', 'armor', 'grenade', 'field pack'],
    'MEDIC': ['pistol', 'knife', 'armor', 'med kit', 'med scanner', 'field pack'],
    'PILOT': ['pistol', 'knife', 'armor', 'commlink', 'tool kit'],
    'ROAD WARRIOR': ['pistol', 'rifle', 'knife', 'armor', 'ammunition', 'field pack'],
    'SCAVENGER': ['pistol', 'rifle', 'knife', 'armor', 'scanner', 'backpack', 'tool kit'],
    'SMUGGLER': ['pistol', 'knife', 'armor', 'commlink', 'field pack'],
    'SQUAD LEADER': ['rifle', 'pistol', 'knife', 'armor', 'grenade', 'commlink', 'binoculars'],
    'CHRONOMANCER': ['staff', 'knife', 'armor', 'focus'],
    'GRAVLOCK': ['pistol', 'knife', 'armor', 'commlink', 'crowbar', 'rope'],
    'HARDLIGHT CONJURER': ['staff', 'knife', 'armor', 'focus'],
    'SHEPHERD': ['staff', 'mace', 'knife', 'armor', 'holy symbol', 'med kit'],
    'WARPER': ['knife', 'armor', 'focus'],
    'STAR KNIGHT': ['sword', 'knife', 'armor', 'shield', 'holy symbol'],
    'COMMANDO': ['heavy weapon', 'rifle', 'pistol', 'knife', 'armor', 'grenade', 'field pack'],
    'CYBORG': ['pistol', 'rifle', 'knife', 'armor', 'commlink', 'tool kit'],
    'SCRAPPER': ['pistol', 'knife', 'armor', 'crowbar', 'tool kit', 'scanner'],
    'TECHNOMANCER': ['pistol', 'knife', 'armor', 'tool kit', 'commlink', 'scanner'],
}

SUPER_EXPECTED = {
    'THE ARCHER': ['body armor', 'chieftain street bike', 'bow', 'arrows', 'knife'],
    'THE TANK': ['body armor', 'pistol', 'grenade', 'knife'],
    'THE ICEMAN': ['parka', 'body armor', 'pistol', 'knife'],
    'THE FIRE BIRD': ['body suit (+2)', 'rifle', 'pistol', 'knife'],
    'THE SORCERESS': ['body suit (+2)', 'staff', 'focus', 'knife'],
    'THE DETECTIVE': ['pistol', 'armor', 'knife', 'commlink', 'binoculars'],
    'THE BRAWLER': ['body suit (+2)', 'luchadore mask', 'knife'],
    'THE VALKYRIE': ['plate mail breastplate (+4)', 'valkyrie sword', 'shield', 'knife'],
    'THE SPEEDSTER': ['body suit (+2)', 'knife'],
    'THE SHAMAN': ['armor', 'staff', 'focus', 'knife'],
    'THE MARTYR': ['armor', 'shield', 'mace', 'knife'],
}


def parse_english_archetypes_full_gear(text_path):
    """Parst EN-Texte und gibt pro Archetyp den VOLLSTÄNDIGEN GEAR-Text zurück."""
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()

    archetypes = {}
    current_archetype = None
    in_gear = False
    gear_lines = []
    section_names = (
        'ATTRIBUTES', 'SKILLS', 'HINDRANCES', 'EDGES', 'POWERS', 'GEAR', 'ADVANCES',
        'ANCESTRY', 'POWER LEVEL', 'RANK', 'SUPER POWERS', 'POWER POINTS',
    )

    for line in text.split('\n'):
        stripped = line.strip()
        if re.match(r'^[=\-=]{3,}$', stripped):
            continue

        is_archetype = (
            re.match(r'^[A-Z][A-Z\s\-]{2,40}$', stripped)
            and stripped not in section_names
        )
        if is_archetype:
            if in_gear:
                in_gear = False
                if current_archetype:
                    archetypes[current_archetype] = ' '.join(gear_lines)
                gear_lines = []
            current_archetype = stripped
            gear_lines = []
            continue

        if stripped == 'GEAR':
            in_gear = True
            gear_lines = []
            continue

        if in_gear:
            if stripped in section_names and stripped != 'GEAR':
                in_gear = False
                if current_archetype:
                    archetypes[current_archetype] = ' '.join(gear_lines)
                gear_lines = []
                continue
            if stripped:
                gear_lines.append(stripped)

    if current_archetype and gear_lines:
        archetypes[current_archetype] = ' '.join(gear_lines)

    return archetypes


def find_in_gear_text(item_query, gear_text, catalog_keys):
    """Prüft ob `item_query` im gear_text vorkommt UND ein Katalog-Match existiert."""
    gear_lower = gear_text.lower()
    query_lower = item_query.lower()
    in_text = query_lower in gear_lower

    candidates = [item_query]
    if item_query in ITEM_ALIASES:
        alias = ITEM_ALIASES[item_query]
        if alias is not None:
            candidates.extend(alias)
    # Wenn der Alias None ist → das Item ist explizit als nicht-im-Katalog markiert
    elif item_query not in ITEM_ALIASES:
        # Kein Alias: trotzdem Katalog-Substring versuchen
        pass

    matched_key = None
    for cand in candidates:
        cand_lower = cand.lower()
        for key in catalog_keys:
            if cand_lower == key.lower() or cand_lower in key.lower() or key.lower() in cand_lower:
                matched_key = key
                break
        if matched_key:
            break

    return in_text, matched_key is not None, matched_key


def check_archetype_gear(arch_name, gear_text, catalog_keys, expected_items):
    """Prüft alle erwarteten Items gegen den GEAR-Text."""
    findings = []
    for item in expected_items:
        in_text, in_catalog, key = find_in_gear_text(item, gear_text, catalog_keys)
        if in_text and not in_catalog:
            findings.append({
                'archetype': arch_name,
                'item': item,
                'status': 'MISSING_FROM_CATALOG',
            })
    return findings


def parse_german_ausruestung_lines(text_path):
    """Parst DE-Texte und extrahiert pro Archetyp die Ausrüstung-Items."""
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    archetypes = {}
    current = None
    in_ausr = False
    items = []
    section_names = ('Ausrüstung', 'AUSRÜSTUNG', 'Handicaps', 'HANDICAPS', 'Talente', 'TALENTE',
                      'Attribute', 'ATTRIBUTE', 'Fertigkeiten', 'FERTIGKEITEN', 'Mächte', 'MÄCHTE',
                      'RANG', 'RANK', 'Bewegung', 'BEWEGUNG', 'Parade', 'PARADE', 'Robustheit', 'ROBUSTHEIT',
                      'Machtpunkte', 'MACHTPUNKTE')
    for line in text.split('\n'):
        s = line.strip()
        if re.match(r'^[=\-=]{3,}$', s):
            continue
        # 1. NEUER Archetyp erkannt → Vorherigen speichern (auch wenn in_ausr)
        is_new_arch_init = re.match(r'^[A-ZÄÖÜ]\.\s+[A-ZÄÖÜ][a-zäöüß]+\s*\(', s)
        is_new_arch_caps = re.match(r'^[A-ZÄÖÜ][A-ZÄÖÜ\s\-,]{2,40}$', s) and s not in section_names
        if is_new_arch_init or is_new_arch_caps:
            if current and items:
                archetypes[current] = ' '.join(items)
            current = s
            items = []
            in_ausr = False
            continue

        # 2. "Ausrüstung:" - Vorherige ggf. speichern, dann starten
        if s.startswith('Ausrüstung:') or s.startswith('AUSRÜSTUNG:'):
            if in_ausr and current and items:
                archetypes[current] = ' '.join(items)
            in_ausr = True
            items = []
            rest = s.split(':', 1)[1].strip() if ':' in s else ''
            if rest:
                items.append(rest)
            continue
        if s in ('Ausrüstung', 'AUSRÜSTUNG'):
            if in_ausr and current and items:
                archetypes[current] = ' '.join(items)
            in_ausr = True
            items = []
            continue

        # 3. "Mächte:" inline beendet Ausrüstung
        if in_ausr and (s.startswith('Mächte:') or s.startswith('MÄCHTE:')):
            in_ausr = False
            if current and items:
                archetypes[current] = ' '.join(items)
            items = []
            continue
        # 4. Section end
        if in_ausr and s in section_names:
            in_ausr = False
            if current and items:
                archetypes[current] = ' '.join(items)
            items = []
            continue
        # 5. Collect items
        if in_ausr and s:
            items.append(s)
    if current and items:
        archetypes[current] = ' '.join(items)
    return archetypes


def match_archetypes(archs, expected_dict):
    """Mappe erwartete Archetyp-Namen auf geparste Archetyp-Namen (case-insensitive, partial)."""
    matched = {}
    for arch_name in expected_dict.keys():
        for parsed_name in archs.keys():
            if (arch_name.upper() in parsed_name.upper() or
                parsed_name.upper() in arch_name.upper() or
                # Spezielle Behandlung für THE X
                arch_name.upper().replace('THE ', '') in parsed_name.upper() or
                parsed_name.upper().replace('THE ', '') in arch_name.upper()):
                matched[arch_name] = parsed_name
                break
    return matched


def main():
    settings = load_settings()

    out = []
    out.append("# Fehlende Ausrüstung pro Setting (Stand: 2026-06-04)\n\n")
    out.append("Systematische Cross-Prüfung: Items, die im Archetyp-Bogen genannt werden, ")
    out.append("aber im entsprechenden Setting-Katalog (`settings/*.json`) fehlen.\n\n")
    out.append("**Methodik:**\n")
    out.append("1. Parse Archetyp-Texte (`Texte/*Archetypen*`) → GEAR-Sektion pro Archetyp\n")
    out.append("2. Iteriere durch die `*_EXPECTED`-Listen (aus Build-Scripts abgeleitet)\n")
    out.append("3. Prüfe jedes Item: (a) im GEAR-Text vorhanden? (b) im Katalog (via Alias-Map) auflösbar?\n")
    out.append("4. Items, die im Bogen vorkommen aber keinen Katalog-Match haben → MISSING\n\n")
    out.append("**Hinweis:** Nur Items, die im Bogen TEXTUELL genannt werden, werden erfasst. ")
    out.append("Substitutions/Approximationen im Build sind hier nicht sichtbar.\n\n")
    out.append("---\n\n")

    # === 1) SciFi Kompendium ===
    out.append("## 1) SciFi Kompendium — `Texte/SciFi Kompendium Archetypen.txt`\n\n")
    archs = parse_english_archetypes_full_gear('Texte/SciFi Kompendium Archetypen.txt')
    catalog = settings['SciFi Kompendium']['ausruestung_keys']
    out.append(f"**Archetypen geparst:** {len(archs)}\n\n")
    matched = match_archetypes(archs, SCIFI_EXPECTED)
    out.append(f"**Erwartete Archetypen gematcht:** {len(matched)}/{len(SCIFI_EXPECTED)}\n\n")
    all_findings = []
    for arch_name, expected in SCIFI_EXPECTED.items():
        if arch_name not in matched:
            continue
        findings = check_archetype_gear(matched[arch_name], archs[matched[arch_name]], catalog, expected)
        all_findings.extend(findings)
    out.append(f"**Items im Bogen aber fehlend im Katalog: {len(all_findings)}**\n\n")
    by_item = defaultdict(list)
    for f in all_findings:
        by_item[f['item']].append(f['archetype'])
    for item, archs_list in sorted(by_item.items()):
        out.append(f"- ❌ **{item}** — fehlt in: {', '.join(archs_list)}\n")
    out.append("\n")

    # === 2) Superkräfte ===
    out.append("## 2) Superkräfte — `Texte/Superkräfte Archetypen.txt`\n\n")
    archs = parse_english_archetypes_full_gear('Texte/Superkräfte Archetypen.txt')
    catalog = settings['Superkräfte Kompendium']['ausruestung_keys']
    out.append(f"**Archetypen geparst:** {len(archs)}\n\n")
    matched = match_archetypes(archs, SUPER_EXPECTED)
    out.append(f"**Erwartete Archetypen gematcht:** {len(matched)}/{len(SUPER_EXPECTED)}\n\n")
    all_findings = []
    for arch_name, expected in SUPER_EXPECTED.items():
        if arch_name not in matched:
            continue
        findings = check_archetype_gear(matched[arch_name], archs[matched[arch_name]], catalog, expected)
        all_findings.extend(findings)
    out.append(f"**Items im Bogen aber fehlend im Katalog: {len(all_findings)}**\n\n")
    by_item = defaultdict(list)
    for f in all_findings:
        by_item[f['item']].append(f['archetype'])
    for item, archs_list in sorted(by_item.items()):
        out.append(f"- ❌ **{item}** — fehlt in: {', '.join(archs_list)}\n")
    out.append("\n")

    # === 3) SuSK (Sundered Skies) ===
    out.append("## 3) SuSK (Sundered Skies) — `Texte/SuSK Archetypen.txt`\n\n")
    archs = parse_german_ausruestung_lines('Texte/SuSK Archetypen.txt')
    catalog = settings['Sundered Skies']['ausruestung_keys']
    out.append(f"**Archetypen geparst:** {len(archs)}\n\n")
    bogen_items_susk = set()
    for arch, gear in archs.items():
        # Word-wrap normalisieren
        normalized = re.sub(r'-\s+', '', gear)
        cleaned = re.sub(r'\([^)]*\)', '', normalized)
        for part in re.split(r'[,;]', cleaned):
            part = part.strip()
            if not part or len(part) < 3:
                continue
            if re.match(r'^\d+ Räder', part):
                continue
            bogen_items_susk.add((arch, part))
    susk_items_missing = {}
    for arch, item in sorted(bogen_items_susk):
        in_cat = False
        for key in catalog:
            if item.lower() in key.lower() or key.lower() in item.lower():
                in_cat = True
                break
        if not in_cat:
            susk_items_missing.setdefault(item, []).append(arch)
    out.append(f"**Items im Bogen aber fehlend im Katalog: {len(susk_items_missing)}**\n\n")
    for item, archs_list in sorted(susk_items_missing.items()):
        out.append(f"- ❌ **{item}** — fehlt in: {', '.join(archs_list)}\n")
    out.append("\n")

    # === 4) SWAE Wilde Welten ===
    out.append("## 4) SWAE Wilde Welten — `Texte/SWAE_Wilde_Welten_Archetypen.txt`\n\n")
    archs = parse_german_ausruestung_lines('Texte/SWAE_Wilde_Welten_Archetypen.txt')
    catalog = settings['SWAE']['ausruestung_keys']
    out.append(f"**Archetypen geparst:** {len(archs)}\n\n")
    bogen_items_swae = set()
    for arch, gear in archs.items():
        # Word-wrap normalisieren
        normalized = re.sub(r'-\s+', '', gear)
        cleaned = re.sub(r'\([^)]*\)', '', normalized)
        for part in re.split(r'[,;]', cleaned):
            part = part.strip()
            if not part or len(part) < 3:
                continue
            if re.match(r'^\d+\$?$', part) or '$' in part:
                continue
            if re.match(r'^\d+ Räder', part):
                continue
            bogen_items_swae.add((arch, part))
    swae_items_missing = {}
    for arch, item in sorted(bogen_items_swae):
        in_cat = False
        for key in catalog:
            if item.lower() in key.lower() or key.lower() in item.lower():
                in_cat = True
                break
        if not in_cat:
            swae_items_missing.setdefault(item, []).append(arch)
    out.append(f"**Items im Bogen aber fehlend im Katalog: {len(swae_items_missing)}**\n\n")
    for item, archs_list in sorted(swae_items_missing.items()):
        out.append(f"- ❌ **{item}** — fehlt in: {', '.join(archs_list)}\n")
    out.append("\n")

    with open('logs/fehlende_ausruestung_uebersicht.md', 'w', encoding='utf-8') as f:
        f.writelines(out)
    print(f"Bericht geschrieben: logs/fehlende_ausruestung_uebersicht.md")


if __name__ == '__main__':
    main()
