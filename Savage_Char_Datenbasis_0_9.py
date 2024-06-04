# Define the values and constants here

settingregeln = {
    'Dynamischer Rückschlag': None,
    'Entschlossenheit': None,
    'Fanatiker': None,
    'Fertigkeitsspezialisierungen': None,
    'Fieser Schaden': None,
    'Geborener Held': None,
    'Große Abenteuer': None,
    'Helden sterben nie': None,
    'Keine Machtpunkte': None,
    'Kreativer Kampf': None,
    'Mehr Fertigkeitspunkte': None,
    'Mehr Sprachen': None,
    'Narrenglück': None,
    'Schnelle Genesung': None,
    'Schwere Entscheidungen': None,
    'Ungepanzerter Held': None,
    'Wundobergrenze': None
}
voelker = {
    'Androiden': {
        'Handicap': ['Außenseiter (Schwer)', 'Pazifist (Schwer)', 'Schwur (Schwer)'],
        'Talente': ['Konstrukt'],
        'Besonderheiten': ['Künstliche Intelligenz', 'Individuelle Persönlichkeit']
    },
    'Aquarianer': {
        'Handicap': ['Abhängigkeit'],
        'Talente': [],
        'Besonderheiten': ['Nachtsicht', 'Robustheit', 'Wasserwesen']
    },
    'Avionen': {
        'Handicap': ['Nichtschwimmer', 'Verringerte Bewegungsweite'],
        'Talente': ['Scharfe Sinne'],
        'Besonderheiten': ['Fliegen', 'Verringerte Bewegungsweite']
    },
    'Halbelfen': {
        'Handicap': ['Außenseiter (Leicht)'],
        'Talente': [],
        'Besonderheiten': ['Erbe', 'Nachtsicht']
    },
    'Elfen': {
        'Handicap': ['Zwei linke Hände'],
        'Talente': [],
        'Besonderheiten': ['Geschickt', 'Nachtsicht']
    },
    'Halblinge': {
        'Handicap': [],
        'Talente': ['Glück'],
        'Besonderheiten': ['Beherzt', 'Größe -1', 'Verringerte Bewegungsweite']
    },
    'Menschen': {
        'Handicap': [],
        'Talente': ['Anpassungsfähig'],
        'Besonderheiten': ['Anpassungsfähig']
    },
    'Rakashaner': {
        'Handicap': ['Blutrünstig', 'Nichtschwimmer', 'Volksfeind'],
        'Talente': [],
        'Besonderheiten': ['Geschickt', 'Nachtsicht', 'Zähne und Krallen']
    },
    'Saurianer': {
        'Handicap': ['Außenseiter (Leicht)', 'Kälteempfindlichkeit'],
        'Talente': ['Biss'],
        'Besonderheiten': ['Biss', 'Panzierung +2', 'Scharfe Sinne']
    },
    'Zwerge': {
        'Handicap': ['Verringerte Bewegungsweite'],
        'Talente': [],
        'Besonderheiten': ['Nachtsicht', 'Verringerte Bewegungsweite', 'Widerstandsfähig']
    }
}
konzept = {
            'characterName': '',
            'spielerName': '',
            'geschlecht': '',
            'alter': '',
            'profession': '',
            'beschreibung': '',
            'hintergrund': '',
            'sprachen': ''
        }
fertigkeiten = {
            'Athletik* ': {'Geschicklichkeit'}, 
            'Heimlichkeit* ': {'Geschicklichkeit'}, 
            'Kämpfen': {'Geschicklichkeit'},
            'Schießen': {'Geschicklichkeit'}, 
            'Diebeskunst': {'Geschicklichkeit'},      
            'Überleben': {'Geschicklichkeit'},
            'Reiten': {'Geschicklichkeit'}, 
            'Fahren': {'Geschicklichkeit'}, 
            'Seefahrt': {'Geschicklichkeit'}, 
            'Pilot': {'Geschicklichkeit'}, 
            'Überreden* ': {'Willenskraft'},
            'Darbietung': {'Willenskraft'},
            'Einschüchtern': {'Willenskraft'},
            'Fokus': {'Willenskraft'}, 
            'Glaube': {'Willenskraft'},        
            'Allgemeinwissen* ': {'Verstand'}, 
            'Wahrnehmung* ': {'Verstand'}, 
            'Heilen': {'Verstand'},
            'Provozieren': {'Verstand'},             
            'Recherche': {'Verstand'}, 
            'Reparieren': {'Verstand'}, 
            'Überleben': {'Verstand'},
            'Glücksspiel': {'Verstand'},
            'Kriegskunst': {'Verstand'},
            'Okkultismus': {'Verstand'},
            'Geisteswissenschaften': {'Verstand'},
            'Naturwissenschaften': {'Verstand'},             
            'Sprache': {'Verstand'},               
            'Elektronik': {'Verstand'}, 
            'Hacken': {'Verstand'}, 
            'Zaubern': {'Verstand'}, 
            'Psionik': {'Verstand'},
            'Verrückte Wissenschaft': {'Verstand'},             
        }
maechte = [
            'Abwehren',
            'Arkaner Schutz',
            'Abwehren',
            'Arkaner Schutz',
            'Arkanes entdecken/verbergen', 
            'Aufheben',
            'Barriere',
            'Betäuben',
            'Blenden',
            'Dunkelsicht', 
            'Eigenschaft erhöhen/senken', 
            'Elementarmanipulation',
            'Empathie', 
            'Fernsicht',
            'Flächenschlag',
            'Fliegen', 
            'Furcht', 
            'Gedankenleere', 
            'Gedankenlesen',
            'Gedankenverbindung', 
            'Geräusch/Stille', 
            'Geschoss', 
            'Gestaltwandeln', 
            'Graben', 
            'Heilung',
            'Illusion', 
            'Kriegersegen', 
            'Licht/Dunkelheit',
            'Linderung', 
            'Marionette', 
            'Objekt auslesen', 
            'Schadensfeld', 
            'Schlummer', 
            'Schutz', 
            'Schutz vor Naturgewalten', 
            'Sprachen sprechen', 
            'Strahl', 
            'Telekinese', 
            'Teleportation', 
            'Tierfreund', 
            'Trägheit/Beschleunigung', 
            'Unberührbarkeit', 
            'Unsichtbarkeit', 
            'Verbannen',
            'Verbündeten beschwören', 
            'Verkleiden', 
            'Verstricken', 
            'Verwirrung',  
            'Wachsen/Schrumpfen',  
            'Waffe verbessern',  
            'Wandkrabbler', 
            'Wiederauferstehung',  
            'Zombie',
            'Zwiesprache'
        ]
hintergrund_talente = [
            'Aristokrat',  
            'Arkane Resistenz',
            'Starke Arkane Resistenz',
            'Arkaner Hintergrund',
            'Attraktiv',
            'Sehr Attraktiv',
            'Aufmerksamkeit', 
            'Beidhändig', 
            'Bekannt', 
            'Berühmt', 
            'Berserker',
            'Charismatisch',
            'Flink',
            'Glück',
            'Großes Glück',
            'Kräftig',
            'Linguist',
            'Mutig',
            'Reich',
            'Stinkreich',
            'Rohling',
            'Schnell', 
            'Schnelle Heilung'
        ]
kampf_talente = [
            'Ausweichen',
            'Schnelles Ausweichen',
            'Beidhändiger Fernkampf',
            'Beidhändiger Kampf',
            'Berechnend',
            'Block',
            'Harter Block',
            'Doppelschuss',
            'Eisenkiefer',
            'Erstschlag',
            'Schneller Erstschlag',
            'Finte',
            'Improvisationsgabe',
            'Kampfkünstler',
            'Kampfkunstmeister',
            'Killerinstinkt',
            'Kampfreflexe',
            'Keine Gnade',
            'Kühler Kopf',
            'Sehr Kühler Kopf',
            'Lieblingswaffe',
            'Absolute Lieblingswaffe',
            'Mächtiger Hieb',
            'Meisterschütze',
            'Parkour',
            'Raufbold',
            'Schläger',
            'Riesentöter',
            'Riposte',
            'Geschickte Riposte',
            'Rückzug',
            'Wendiger Rückzug',
            'Ruhige Hände',
            'Rundumschlag',
            'Kontrollierter Rundumschlag',
            'Schmerzresistenz',
            'Stärkere Schmerzresistenz',
            'Schneller Angriff',
            'Blitzschneller Angriff',
            'Schnellfeuer',
            'Verbessertes Schnellfeuer',
            'Schwer zu töten',
            'Wirklich schwer zu töten',
            'Volles Rohr!',
            'Volltreffer'
        ]
anfuehrer_talente = [
            'Anführer',
            'Großer Anführer',
            'Anheizen',
            'Geborener Anführer',
            'Haltet die Stellung!',
            'Inspirieren',
            'Taktiker',
            'Meistertaktiker'
        ]
macht_talente = [
            'Artefakterschaffer',
            'Bastler',
            'Energieschub',
            'Heiliger/Unheiliger Krieger',
            'Kanalisieren',
            'Konzentration',
            'Machtpunkte',
            'Mentalist',
            'Neue Mächte',
            'Schnelle Machtregeneration',
            'Schnellere Machtregeneration',
            'Seelenentzug',
            'Zauberer',
            'Zusätzliche Anstrengung'
        ]
experten_talente = [
            'Akrobat',
            'Kampfakrobat',
            'Alleskönner',
            'Ass am Steuer',
            'Assassine',
            'Dieb',
            'Ermittler',
            'Gelehrter',
            'McGyver',
            'Naturbursche',
            'Reparaturgenie',
            'Soldat'
        ]
sozial_talente = [
            'Aufwiegler',
            'Bedrohlich',
            'Beziehungen',
            'Ermutigen',
            'Erniedrigen',
            'Erzürnen',
            'Gassenwissen',
            'Konter',
            'Rampensau',
            'Echte Rampensau',
            'Selbstlos',
            'Starker Wille',
            'Eiserner Wille',
            'Verlässlich'
        ]   
uebersinnliche_talente = [
            'Auserwählter',
            'Chi',
            'Heiler',
            'Mut in Flaschen',
            'Sammler',
            'Sechster Sinn',
            'Tierempathie',
            'Tiermeister'
        ]  
legendaere_talente = [
            'Gefolgsleute',
            'Handlanger',
            'Profi',
            'Experte',
            'Meister',
            'Waffenmeister',
            'Meister aller Waffen',
            'Zäh wie Leder',
            'Zäher als Leder'
        ]  
handicaps = [
             'Alt (schwer)',
             'Analphabet (leicht)',
             'Angetrieben (leicht)',
             'Angetrieben (schwer)',
             'Angewohnheit (leicht)',
             'Angewohnheit (schwer)',           
             'Arm (leicht)',
             'Arrogant (schwer)',
             'Außenseiter (leicht)',
             'Außenseiter (schwer)',
             'Beschämt (leicht)',
             'Beschämt (schwer)',
             'Blind (schwer)',
             'Blutrünstig (schwer)',
             'Dünnhäutig (leicht)',
             'Dünnhäutig (schwer)',             
             'Ehrenkodex (schwer)',
             'Eifersüchtig (leicht)',
             'Eifersüchtig (schwer)',
             'Einarmig (schwer)',
             'Einäugig (schwer)',
             'Feige (schwer)',
             'Feind (leicht)',
             'Feind (schwer)',
             'Fettleibig (leicht)',
             'Fies (leicht)',
             'Geheimnis (leicht)',
             'Geheimnis (schwer)',
             'Gesucht (leicht)',
             'Gesucht (schwer)',
             'Gierig (leicht)',
             'Gierig (schwer)',
             'Große Klappe (leicht)',
             'Hässlich (leicht)',
             'Hässlich (schwer)',
             'Heldenhaft (schwer)',
             'Impulsiv (schwer)',
             'Jung (leicht)',
             'Jung (schwer)',
             'Klein (leicht)',
             'Kränklich (leicht)',
             'Langsam (leicht)',
             'Langsam (schwer)',
             'Lebensaufgabe (leicht)',
             'Loyal (leicht)',
             'Misstrauisch (leicht)',
             'Misstrauisch (schwer)',
             'Neugierig (schwer)',
             'Nichtschwimmer (leicht)',
             'Pazifist (leicht)',
             'Pazifist (schwer)',
             'Pech (schwer)',
             'Phobie (leicht)',
             'Phobie (schwer)',
             'Rachsüchtig (leicht)',
             'Rachsüchtig (schwer)',
             'Sanftmütig (leicht)',
             'Schlechte Augen (leicht)',
             'Schlechte Augen (schwer)',
             'Schwerhörig (leicht)',
             'Schwerhörig (schwer)',
             'Schwerzüngig (schwer)',
             'Schwur (leicht)',
             'Schwur (schwer)',
             'Skrupellos (leicht)',
             'Skrupellos (schwer)',
             'Stumm (schwer)',
             'Stur (leicht)',
             'Tick (leicht)',
             'Tollpatschig (schwer)',
             'Übermütig (schwer)',
             'Verpeilt (schwer)'
        ]
nahkampf_waffe = {
    'Axt, Handbeil': {'Reichweite': 'nah', 'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 1, 'Kosten': 100, 'Anmerkungen': '-'},
    'Axt, Kriegsbeil': {'Reichweite': 'nah', 'Schaden': 'Stä+W8', 'Mindeststärke': 'W8', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 2, 'Kosten': 300, 'Anmerkungen': '—'},
    'Axt, Zweihandaxt': {'Reichweite': 'nah', 'Schaden': 'Stä+W10', 'Mindeststärke': 'W10', 'PB': 2, 'FR': '-', 'Schuss': '-', 'Gewicht': 3.5, 'Kosten': 400, 'Anmerkungen': 'Parade –1, Zweihändig'},
    'Dolch/Messer': {'Reichweite': 'nah', 'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 0.5, 'Kosten': 25, 'Anmerkungen': '—'},
    'Hellebarde': {'Reichweite': 'nah', 'Schaden': 'Stä+W8', 'Mindeststärke': 'W8', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 3, 'Kosten': 250, 'Anmerkungen': 'Reichweite 1, Zweihändig'},
    'Kampfstab': {'Reichweite': 'nah', 'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 2, 'Kosten': 10, 'Anmerkungen': 'Parade +1, Reichweite 1, Zweihändig'},
    'Katana': {'Reichweite': 'nah', 'Schaden': 'Stä+W6+1', 'Mindeststärke': 'W6', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 1.5, 'Kosten': 1000, 'Anmerkungen': 'Zweihändig'},
    'Keule, Leicht': {'Reichweite': 'nah', 'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 1, 'Kosten': 25, 'Anmerkungen': '-'},
    'Keule, Schwer': {'Reichweite': 'nah', 'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 2.5, 'Kosten': 50, 'Anmerkungen': '-'},
    'Kriegshammer': {'Reichweite': 'nah', 'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'PB': 1, 'FR': '-', 'Schuss': '-', 'Gewicht': 1, 'Kosten': 250, 'Anmerkungen': '-'},
    'Lanze': {'Reichweite': 'nah', 'Schaden': 'Stä+W8', 'Mindeststärke': 'W8', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 3, 'Kosten': 300, 'Anmerkungen': 'PB 2 Sturmangriff, Reichweite 2, berittener Kampf'},
    'Morgenstern': {'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 1.5, 'Kosten': 200, 'Anmerkungen': 'ignoriert Schildboni'},
    'Rapier': {'Reichweite': 'nah', 'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 1, 'Kosten': 150, 'Anmerkungen': 'Parade +1'},
    'Schwert, Kurzschwert': {'Reichweite': 'nah', 'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 1, 'Kosten': 100, 'Anmerkungen': '-'},
    'Schwert, Langschwert': {'Reichweite': 'nah', 'Schaden': 'Stä+W8', 'Mindeststärke': 'W8', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 1.5, 'Kosten': 300, 'Anmerkungen': '-'},
    'Schwert, Zweihandschwert': {'Reichweite': 'nah', 'Schaden': 'Stä+W10', 'Mindeststärke': 'W10', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 3, 'Kosten': 400, 'Anmerkungen': 'Zweihändig'},
    'Speer': {'Reichweite': 'nah', 'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 1.5, 'Kosten': 100, 'Anmerkungen': 'Reichweite 1, Parade +1 wenn zweihändig'},
    'Spieß': {'Reichweite': 'nah', 'Schaden': 'Stä+W8', 'Mindeststärke': 'W8', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 9, 'Kosten': 400, 'Anmerkungen': 'Reichweite 2, Zweihändig'},
    'Streitkolben': {'Reichweite': 'nah', 'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 2, 'Kosten': 100, 'Anmerkungen': '—'},
    'Zweihandhammer': {'Reichweite': 'nah', 'Schaden': 'Stä+W10', 'Mindeststärke': 'W10', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 5, 'Kosten': 400, 'Anmerkungen': 'Zweihändig, +2 Schaden/Gegenstände (Seite 100)'},
    'Bangstick': {'Reichweite': 'nah', 'Schaden': '3W6', 'Mindeststärke': 'W6', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 1, 'Kosten': 5, 'Anmerkungen': '-'},
    'Bajonett': {'Reichweite': 'nah', 'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 0.5, 'Kosten': 25, 'Anmerkungen': 'Stä+W6 und Parade +1 am Gewehr, Reichweite 1, Zweihändig'},
    'Kettensäge': {'Reichweite': 'nah', 'Schaden': '2W6+4', 'Mindeststärke': 'W6', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 10, 'Kosten': 200, 'Anmerkungen': 'Kritischer Fehlschlag Eigentrffer'},
    'Schlagring': {'Reichweite': 'nah', 'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 0.5, 'Kosten': 20, 'Anmerkungen': '-'},
    'Schlagstock': {'Reichweite': 'nah', 'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 0.5, 'Kosten': 10, 'Anmerkungen': '-'},
    'Springmesser': {'Reichweite': 'nah', 'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 0.25, 'Kosten': 10, 'Anmerkungen': '-'},
    'Überlebensmesser': {'Reichweite': 'nah', 'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'PB': '-', 'FR': '-', 'Schuss': '-', 'Gewicht': 0.5, 'Kosten': 50, 'Anmerkungen': '+1 auf Überleben'},
    'Molekularmesser': {'Reichweite': 'nah', 'Schaden': 'Stä+W4+2', 'Mindeststärke': 'W4', 'PB': 2, 'FR': '-', 'Schuss': '-', 'Gewicht': 0.25, 'Kosten': 250, 'Anmerkungen': 'nicht werfen'},
    'Molekularschwert': {'Reichweite': 'nah', 'Schaden': 'Stä+W8+2', 'Mindeststärke': 'W6', 'PB': 4, 'FR': '-', 'Schuss': '-', 'Gewicht': 1, 'Kosten': 500, 'Anmerkungen': '-'},
    'Laserschwert': {'Reichweite': 'nah', 'Schaden': 'Stä+W6+8', 'Mindeststärke': 'W4', 'PB': 12, 'FR': '-', 'Schuss': '-', 'Gewicht': 1, 'Kosten': 1000, 'Anmerkungen': '-'}
}
fernkampf_waffe = {
    'Browning Automatic Rifle (BAR) (.30-06)': {'Reichweite': '20/40/60', 'Schaden': '2W8', 'PB': 2, 'FR': 3, 'Schuss': 20, 'Mindeststärke': 'W8', 'Gewicht': 8.5, 'Kosten': 300},
    'Gatling (.45)': {'Reichweite': '24/48/96', 'Schaden': '2W8', 'PB': 2, 'FR': 3, 'Schuss': 100, 'Mindeststärke': '-', 'Gewicht': 85, 'Kosten': 500},
    'Minigun (7.62mm)': {'Reichweite': '30/60/120', 'Schaden': '2W8+1', 'PB': 2, 'FR': 5, 'Schuss': 4000, 'Mindeststärke': 'W10', 'Gewicht': 42.5, 'Kosten': 100000},
    'M2 Browning (.50 Cal)': {'Reichweite': '50/100/200', 'Schaden': '2W10', 'PB': 4, 'FR': 3, 'Schuss': 200, 'Mindeststärke': '-', 'Gewicht': 42, 'Kosten': 1500},
    'M60 (7.62mm)': {'Reichweite': '30/60/120','Schaden': '2W8+1', 'PB': 2, 'FR': 3, 'Schuss': 100, 'Mindeststärke': 'W8', 'Gewicht': 16.5, 'Kosten': 6000},
    'MG42 (7.92mm)': { 'Reichweite': '30/60/120','Schaden': '2W8+1', 'PB': 2, 'FR': 4, 'Schuss': 200, 'Mindeststärke': 'W10', 'Gewicht': 13, 'Kosten': 750},
    'SAW (5.56mm)': { 'Reichweite': '30/60/120', 'Schaden': '2W8', 'PB': 2, 'FR': 4, 'Schuss': 200, 'Mindeststärke': 'W8', 'Gewicht': 10, 'Kosten': 4000},
    'Pistole': { 'Reichweite': '15/30/60', 'Schaden': '2W6', 'PB': 2, 'FR': 1, 'Schuss': 50, 'Mindeststärke': 'W4', 'Gewicht': 1, 'Kosten': 250},
    'Maschinenpistole': { 'Reichweite': '15/30/60', 'Schaden': '2W6', 'PB': 2, 'FR': 4, 'Schuss': 100, 'Mindeststärke': 'W4', 'Gewicht': 2, 'Kosten': 500},
    'Gewehr': { 'Reichweite': '30/60/120', 'Schaden': '3W6', 'PB': 2, 'FR': 3, 'Schuss': 100, 'Mindeststärke': 'W6', 'Gewicht': 4, 'Kosten': 700},
    'Gatling-Laser': { 'Reichweite': '50/100/200', 'Schaden': '3W6+4', 'PB': 2, 'FR': 4, 'Schuss': 800, 'Mindeststärke': 'W8', 'Gewicht': 10, 'Kosten': 1000}
}
spezielle_waffe = {
    'Kanonen': {
        'Kanone (12 Pfünder)': {'Reichweite': 'Nach Munitionsart', 'Schaden': '—', 'PB': '—', 'FR': '—', 'Flächenschablone': '—', 'Gewicht': 600, 'Kosten': 10000},
        'Kartätsche': {'Reichweite': '24″ Pfad', 'Schaden': '2W6', 'PB': '—', 'FR': '1', 'Flächenschablone': 'MFS', 'Gewicht': 50, 'Kosten': 50},
        'Rundgeschoss': {'Reichweite': '50/100/200', 'Schaden': '3W6+1', 'PB': 4, 'FR': '1', 'Flächenschablone': '—', 'Gewicht': 50, 'Kosten': 50},
        'Schrapnell': {'Reichweite': '50/100/200', 'Schaden': '3W6', 'PB': '—', 'FR': '1', 'Flächenschablone': 'MFS', 'Gewicht': 50, 'Kosten': 50},
    },
    'Katapulte': {
        'Katapult': {'Reichweite': '24/48/96', 'Schaden': '3W6', 'PB': 4, 'FR': 'Speziell', 'Flächenschablone': 'MFS', 'Gewicht': 10000, 'Kosten': 10000},
        'Trebuchet': {'Reichweite': '30/60/120', 'Schaden': '3W8', 'PB': 4, 'FR': 'Speziell', 'Flächenschablone': 'MFS', 'Gewicht': 50000, 'Kosten': 50000},
    },
    'Flammenwerfer': {
        'Flammenwerfer': {'Reichweite': 'Kegelschablone', 'Schaden': '3W6', 'PB': '—', 'FR': 1, 'Schuss': 10, 'Mindeststärke': 'W8', 'Gewicht': 35, 'Kosten': 300},
    },
    'Granaten': {
        'Mk II (Pineapple, Zweiter Weltkrieg)': {'Reichweite': '4/8/16', 'Schaden': '3W6', 'PB': '—', 'FR': '—', 'Flächenschablone': 'MFS', 'Gewicht': 0.5, 'Kosten': 40},
        'Stielhandgranate (Potato Masher, Zweiter Weltkrieg)': {'Reichweite': '5/10/20', 'Schaden': '3W6–2', 'PB': '—', 'FR': '—', 'Flächenschablone': 'MFS', 'Gewicht': 1, 'Kosten': 50},
        'Mk67 (Modern)': {'Reichweite': '5/10/20', 'Schaden': '3W6', 'PB': '—', 'FR': '—', 'Flächenschablone': 'MFS', 'Gewicht': 0.5, 'Kosten': 50},
        'Rauchgranate': {'Reichweite': '5/10/20', 'Schaden': '—', 'PB': '—', 'FR': '—', 'Flächenschablone': 'GFS', 'Gewicht': 0.5, 'Kosten': 50},
        'Betäubungsgranate': {'Reichweite': '5/10/20', 'Schaden': '—', 'PB': '—', 'FR': '—', 'Flächenschablone': 'GFS', 'Gewicht': 0.5, 'Kosten': 50},
    },
    'Minen': {
        'Antipersonenmine': {'Reichweite': '—', 'Schaden': '2W6+2', 'PB': '—', 'FR': '—', 'Flächenschablone': 'KFS', 'Gewicht': 5, 'Kosten': 100},
        'Panzerabwehrmine': {'Reichweite': '—', 'Schaden': '4W6', 'PB': '—', 'FR': '—', 'Flächenschablone': 'MFS', 'Gewicht': 10, 'Kosten': 200},
        'Bouncing Betty': {'Reichweite': '—', 'Schaden': '3W6', 'PB': '—', 'FR': '—', 'Flächenschablone': 'KFS', 'Gewicht': 4.5, 'Kosten': 125},
        'Claymore-Mine': {'Reichweite': '—', 'Schaden': '3W6', 'PB': '—', 'FR': '—', 'Flächenschablone': 'Speziell', 'Gewicht': 2, 'Kosten': 75},
    },
    'Raketen': {
        'TOW': {'Reichweite': '75/150/300', 'Schaden': '5W10', 'PB': 34, 'FR': 1, 'Flächenschablone': 'MFS', 'Gewicht': 104, 'Kosten': 60000},
        'Hellfire': {'Reichweite': '150/300/600', 'Schaden': '5W10', 'PB': 40, 'FR': 'Speziell', 'Flächenschablone': 'MFS', 'Gewicht': 50, 'Kosten': 115000},
        'Sidewinder': {'Reichweite': '100/200/400', 'Schaden': '4W8', 'PB': 6, 'FR': '—', 'Flächenschablone': 'KFS', 'Gewicht': 94, 'Kosten': 600000},
        'Sparrow': {'Reichweite': '150/300/600', 'Schaden': '5W8', 'PB': 6, 'FR': '—', 'Flächenschablone': 'KFS', 'Gewicht': 309, 'Kosten': 125000},
    },
    'Raketenwerfer und Torpedos': {
        'AT-4': {'Reichweite': '24/48/96', 'Schaden': '4W8+2', 'PB': 24, 'FR': 1, 'Flächenschablone': 'MFS', 'Gewicht': 7.5, 'Kosten': 1500},
        'Bazooka': {'Reichweite': '24/48/96', 'Schaden': '4W8', 'PB': 8, 'FR': 1, 'Flächenschablone': 'MFS', 'Gewicht': 6, 'Kosten': 500},
        'M203 40MM': {'Reichweite': '24/48/96', 'Schaden': '4W8', 'PB': '—', 'FR': 1, 'Flächenschablone': 'MFS', 'Gewicht': 1.5, 'Kosten': 1500},
        'M72 Law': {'Reichweite': '24/48/96', 'Schaden': '4W8+2', 'PB': 22, 'FR': 1, 'Flächenschablone': 'MFS', 'Gewicht': 2.5, 'Kosten': 750},
        'Panzerschreck': {'Reichweite': '15/30/60', 'Schaden': '4W8', 'PB': 12, 'FR': 1, 'Flächenschablone': 'MFS', 'Gewicht': 10, 'Kosten': 1000},
        'Torpedo': {'Reichweite': '300/600/1200', 'Schaden': '8W10', 'PB': 22, 'FR': 1, 'Flächenschablone': 'KFS', 'Gewicht': 1500, 'Kosten': 500000},
    },
}
fahrzeug_waffe = {
    'Mittleres Maschinengewehr': {'Reichweite': '30/60/120', 'PB-Geschosse': '2W8+1, PB 2', 'HE-Geschosse': '—', 'FR': 3, 'Kosten': 750},
    'Schweres Maschinengewehr': {'Reichweite': '50/100/200', 'PB-Geschosse': '2W10, PB 4', 'HE-Geschosse': '—', 'FR': 3, 'Kosten': 1000},
    'Schwerer Flammenwerfer': {'Reichweite': 'Kegel oder MFS', 'PB-Geschosse': '—', 'HE-Geschosse': '3W8', 'FR': 1, 'Kosten': 1000},
    '20mm-Kanone': {'Reichweite': '50/100/200', 'PB-Geschosse': '2W12, PB 4', 'HE-Geschosse': '—', 'FR': 4, 'Kosten': 50000},
    '25mm-Kanone': {'Reichweite': '50/100/200', 'PB-Geschosse': '3W8, PB 4', 'HE-Geschosse': '—', 'FR': 3, 'Kosten': 75000},
    '30mm-Kanone': {'Reichweite': '50/100/200', 'PB-Geschosse': '3W8, PB 6', 'HE-Geschosse': '—', 'FR': 3, 'Kosten': 200000},
    '40mm-Kanone': {'Reichweite': '75/150/300', 'PB-Geschosse': '4W8, PB 5', 'HE-Geschosse': '3W8, PB 2, MFS', 'FR': 4, 'Kosten': 200000},
    '2-Pfünder-Panzerabwehrkanone': {'Reichweite': '75/150/300', 'PB-Geschosse': '4W8, PB 5', 'HE-Geschosse': '3W6, PB 2, MFS', 'FR': 1, 'Kosten': 75000},
    '37mm-Panzerabwehrkanone': {'Reichweite': '50/100/200', 'PB-Geschosse': '4W8, PB 3', 'HE-Geschosse': '4W6, PB 3, MFS', 'FR': 1, 'Kosten': 100000},
    '57mm-Panzerabwehrkanone': {'Reichweite': '75/150/300', 'PB-Geschosse': '4W8, PB 5', 'HE-Geschosse': '3W8, PB 3, MFS', 'FR': 1, 'Kosten': 150000},
    '75mm-Panzerkanone': {'Reichweite': '75/150/300', 'PB-Geschosse': '4W10, PB 6', 'HE-Geschosse': '3W8, PB 3, MFS', 'FR': 1, 'Kosten': 250000},
    '76mm-Panzerkanone': {'Reichweite': '75/150/300', 'PB-Geschosse': '4W10, PB 10', 'HE-Geschosse': '3W8, PB 5, MFS', 'FR': 1, 'Kosten': 300000},
    '88mm-Panzerkanone': {'Reichweite': '100/200/400', 'PB-Geschosse': '4W10+1, PB 16', 'HE-Geschosse': '4W8, PB 8, MFS', 'FR': 1, 'Kosten': 500000},
    '120mm-Panzerkanone': {'Reichweite': '100/200/400', 'PB-Geschosse': '5W10, PB 31', 'HE-Geschosse': '4W8, PB 17, MFS', 'FR': 1, 'Kosten': 800000},
    '125mm-Panzerkanone': {'Reichweite': '100/200/400', 'PB-Geschosse': '5W10, PB 30', 'HE-Geschosse': '4W8, PB 15, MFS', 'FR': 1, 'Kosten': 1000000},
    'Futuristisch': {
        'Gatling-Laser': {'Reichweite': '50/100/200', 'PB-Geschosse': '3W6+4, PB 4', 'HE-Geschosse': '—', 'FR': 4, 'Kosten': 1000},
        'Schwerer Laser': {'Reichweite': '150/300/600', 'PB-Geschosse': '4W10, PB 30', 'HE-Geschosse': '—', 'FR': 1, 'Kosten': 1000000},
    }
}
ausruestung = {
    'Pferd': {'Kosten': 300, 'Gewicht': 0},
    'Streitross': {'Kosten': 750, 'Gewicht': 0},
    'Sattel': {'Kosten': 10, 'Gewicht': 5},
    'Verzierter Sattel': {'Kosten': 50, 'Gewicht': 5},
    'Brechstange': {'Kosten': 10, 'Gewicht': 1},
    'Dietriche': {'Kosten': 200, 'Gewicht': 0.5},
    'Erste-Hilfe-Tasche': {'Kosten': 10, 'Gewicht': 0.5},
    'Fackel': {'Kosten': 5, 'Gewicht': 0.5},
    'Feuerstein und Stahl': {'Kosten': 3, 'Gewicht': 0.5},
    'Feuerzeug': {'Kosten': 2, 'Gewicht': 0},
    'Fläschchen (Keramik)': {'Kosten': 5, 'Gewicht': 0.5},
    'Hammer': {'Kosten': 10, 'Gewicht': 0.5},    
    'Handschellen': {'Kosten': 15, 'Gewicht': 1},
    'Kamera (Einweg)': {'Kosten': 10, 'Gewicht': 0.5},
    'Kamera (normal)': {'Kosten': 75, 'Gewicht': 1},
    'Kamera (digital)': {'Kosten': 300, 'Gewicht': 0.5},
    'Kerze (eine Stunde, 2" Radius)': {'Kosten': 1, 'Gewicht': 0.5},
    'Köcher (für 20 Pfeile/Bolzen)': {'Kosten': 25, 'Gewicht': 1},
    'Laterne (4 Stunden, 4" Radius)': {'Kosten': 25, 'Gewicht': 1.5},
    'Öl (für Laterne, 0,5 Liter)': {'Kosten': 2, 'Gewicht': 0.5},
    'Regenschirm': {'Kosten': 5, 'Gewicht': 1},
    'Rucksack': {'Kosten': 50, 'Gewicht': 1},
    'Sanitätskoffer': {'Kosten': 100, 'Gewicht': 2},
    'Schaufel': {'Kosten': 5, 'Gewicht': 2.5},
    'Schlafsack (winterfest)': {'Kosten': 25, 'Gewicht': 2},
    'Schutzbrille': {'Kosten': 20, 'Gewicht': 0.5},
    'Seife': {'Kosten': 1, 'Gewicht': 0.1},
    'Seil, Hanf (10" / 20 m)': {'Kosten': 10, 'Gewicht': 7.5},
    'Seil, Nylon (10" / 20 m)': {'Kosten': 10, 'Gewicht': 1.5},
    'Taschenlampe (10" Strahl)': {'Kosten': 20, 'Gewicht': 1.5},
    'Trillerpfeife': {'Kosten': 2, 'Gewicht': 0},
    'Wasserflasche (Wasserschlauch)': {'Kosten': 5, 'Gewicht': 0.5},
    'Werkzeugkoffer': {'Kosten': 200, 'Gewicht': 2.5},
    'Wetzstein': {'Kosten': 5, 'Gewicht': 0.5},
    'Wolldecke': {'Kosten': 10, 'Gewicht': 2},
    'Wurfanker': {'Kosten': 100, 'Gewicht': 1},
    'Laser-/Rotpunktvisier': {'Kosten': 150, 'Gewicht': 0.5},
    'Zielfernrohr': {'Kosten': 100, 'Gewicht': 1},
    'Zweibein/Dreibein': {'Kosten': 100, 'Gewicht': 1},
    'Kleidung, Alltag': {'Kosten': 20, 'Gewicht': 1},
    'Kleidung, formell': {'Kosten': 200, 'Gewicht': 1.5},
    'Tarnkleidung': {'Kosten': 20, 'Gewicht': 1.5},
    'Wanderstiefel': {'Kosten': 100, 'Gewicht': 1},
    'Winterkleidung (Mantel/Parka)': {'Kosten': 200, 'Gewicht': 1.5},
    'Winterstiefel': {'Kosten': 100, 'Gewicht': 0.5},
    'Desktop': {'Kosten': 800, 'Gewicht': 10},
    'GPS': {'Kosten': 250, 'Gewicht': 0.5},
    'Laptop': {'Kosten': 1200, 'Gewicht': 2.5},
    'Taschencomputer': {'Kosten': 250, 'Gewicht': 0.5},
    'Pfeile/Bolzen': {'Kosten': 1, 'Gewicht': 1},
    'Patronen (Klein)': {'Kosten': 10, 'Gewicht': 0.5},
    'Patronen (Mittel)': {'Kosten': 20, 'Gewicht': 1},
    'Patronen (Groß)': {'Kosten': 50, 'Gewicht': 7.5},
    'Laserbatterien (Pistole)': {'Kosten': 20, 'Gewicht': 0.1},
    'Laserbatterien (Gewehr, Maschinenpistole)': {'Kosten': 20, 'Gewicht': 0.25},
    'Gattling': {'Kosten': 50, 'Gewicht': 2},
    'Kugel (mit Schwarzpulver)': {'Kosten': 1, 'Gewicht': 0.25},
    'Schrotflinte': {'Kosten': 15, 'Gewicht': 1.5},
    'Flintenlaufgschosse': {'Kosten': 20, 'Gewicht': 1.5},
    'Schleudersteine': {'Kosten': 2, 'Gewicht': 1},
    'Pfefferspray': {'Kosten': 15, 'Gewicht': 0.25},
    'Taser': {'Kosten': 25, 'Gewicht': 0.25},
    'Handy-Abhörer': {'Kosten': 650, 'Gewicht': 2.5},
    'Knopfkamera': {'Kosten': 50, 'Gewicht': 0},
    'Nachtsichtbrille': {'Kosten': 500, 'Gewicht': 1.5},
    'Parabolmikrofon': {'Kosten': 750, 'Gewicht': 2},
    'Senderdetektor': {'Kosten': 525, 'Gewicht': 0.5},
    'Störtelefon': {'Kosten': 150, 'Gewicht': 1},
    'Telefonanzapfung': {'Kosten': 250, 'Gewicht': 0},
    '„Wanze“ (Mikrotransmitter)': {'Kosten': 30, 'Gewicht': 0}
}
ruestung = {
    'Jacke': {'Torso': 1, 'Arme': 1, 'Beine': 0, 'Kopf': 0, 'Mindeststärke': 'W4', 'Gewicht': 2.5, 'Kosten': 20},
    'Robe': {'Torso': 1, 'Arme': 1, 'Beine': 1, 'Kopf': 0, 'Mindeststärke': 'W4', 'Gewicht': 4, 'Kosten': 30},
    'Beinlinge': {'Torso': 0, 'Arme': 0, 'Beine': 1, 'Kopf': 0, 'Mindeststärke': 'W4', 'Gewicht': 2.5, 'Kosten': 20},
    'Kappe': {'Torso': 0, 'Arme': 0, 'Beine': 0, 'Kopf': 1, 'Mindeststärke': 'W4', 'Gewicht': 0.5, 'Kosten': 5},
    'Platten-Rossharnisch': {'Torso': 0, 'Arme': 0, 'Beine': 0, 'Kopf': 0, 'Mindeststärke': 'W10', 'Gewicht': 25, 'Kosten': 1500},
    'Brustharnisch': {'Torso': 4, 'Arme': 0, 'Beine': 0, 'Kopf': 0, 'Mindeststärke': 'W10', 'Gewicht': 15, 'Kosten': 500},
    'Armschienen': {'Torso': 0, 'Arme': 4, 'Beine': 0, 'Kopf': 0, 'Mindeststärke': 'W10', 'Gewicht': 5, 'Kosten': 200},
    'Beinschienen': {'Torso': 0, 'Arme': 0, 'Beine': 4, 'Kopf': 0, 'Mindeststärke': 'W10', 'Gewicht': 5, 'Kosten': 200},
    'Schwerer Helm': {'Torso': 0, 'Arme': 0, 'Beine': 0, 'Kopf': 4, 'Mindeststärke': 'W10', 'Gewicht': 2, 'Kosten': 100},
    'Schwerer Helm, geschlossen': {'Torso': 0, 'Arme': 0, 'Beine': 0, 'Kopf': 4, 'Mindeststärke': 'W10', 'Gewicht': 4, 'Kosten': 200},
    'Splitterschutzjacke': {'Torso': 2, 'Arme': 0, 'Beine': 0, 'Kopf': 0, 'Mindeststärke': 'W6', 'Gewicht': 2.5, 'Kosten': 40},
    'Kevlarweste': {'Torso': 2, 'Arme': 0, 'Beine': 0, 'Kopf': 0, 'Mindeststärke': 'W6', 'Gewicht': 2.5, 'Kosten': 200},
    'Kevlarweste mit Keramikplatten': {'Torso': 4, 'Arme': 0, 'Beine': 0, 'Kopf': 0, 'Mindeststärke': 'W8', 'Gewicht': 8.5, 'Kosten': 500},
    'Kevlarhelm': {'Torso': 0, 'Arme': 0, 'Beine': 0, 'Kopf': 4, 'Mindeststärke': 'W4', 'Gewicht': 2.5, 'Kosten': 80},
    'Bombenschutzanzug': {'Torso': 10, 'Arme': 10, 'Beine': 10, 'Kopf': 10, 'Mindeststärke': 'W12', 'Gewicht': 40, 'Kosten': 25000},
    'Infanteriekampfanzug': {'Torso': 6, 'Arme': 6, 'Beine': 6, 'Kopf': 0, 'Mindeststärke': 'W6', 'Gewicht': 6, 'Kosten': 800},
    'Kampfhelm': {'Torso': 0, 'Arme': 0, 'Beine': 0, 'Kopf': 6, 'Mindeststärke': 'W6', 'Gewicht': 1, 'Kosten': 100}
}
schilde = {
    'Antike & Mittelalter': {
        'Klein': {
            'Parade': '+1',
            'Deckung': '—',
            'Mindeststärke': 'W4',
            'Gewicht': 2,
            'Kosten': 50
        },
        'Mittel': {
            'Parade': '+2',
            'Deckung': '–2',
            'Mindeststärke': 'W6',
            'Gewicht': 4,
            'Kosten': 100
        },
        'Groß': {
            'Parade': '+3',
            'Deckung': '–4',
            'Mindeststärke': 'W8',
            'Gewicht': 6,
            'Kosten': 200
        }
    },
    'Modern': {
        'Einsatzschild': {
            'Parade': '+3',
            'Deckung': '–4',
            'Mindeststärke': 'W4',
            'Gewicht': 2.5,
            'Kosten': 80
        },
        'Ballistischer Schild': {
            'Parade': '+3',
            'Deckung': '–4',
            'Mindeststärke': 'W6',
            'Gewicht': 4.5,
            'Kosten': 250
        },
        'Anmerkungen': 'Schaden Feuerwaffen –4'
    },
    'Futuristisch': {
        'Polymerschild, Klein': {
            'Parade': '+1',
            'Deckung': '—',
            'Mindeststärke': 'W4',
            'Gewicht': 1,
            'Kosten': 200
        },
        'Polymerschild, Mittel': {
            'Parade': '+2',
            'Deckung': '–2',
            'Mindeststärke': 'W4',
            'Gewicht': 2,
            'Kosten': 300
        },
        'Polymerschild, Groß': {
            'Parade': '+3',
            'Deckung': '–4',
            'Mindeststärke': 'W6',
            'Gewicht': 3,
            'Kosten': 400
        }
    }
}
grundfertigkeiten = [
            'Allgemeinwissen* ',
            'Athletik* ',
            'Heimlichkeit* ',
            'Überreden* ',
            'Wahrnehmung* '
    ]
