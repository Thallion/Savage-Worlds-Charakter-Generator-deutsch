# Define the values and constants here

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
    'Axt, Handbeil': {'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'Gewicht': 1, 'Kosten': 100, 'Anmerkungen': '-'},
    'Axt, Kriegsbeil': {'Schaden': 'Stä+W8', 'Mindeststärke': 'W8', 'Gewicht': 2, 'Kosten': 300, 'Anmerkungen': '—'},
    'Axt, Zweihandaxt': {'Schaden': 'Stä+W10', 'Mindeststärke': 'W10', 'Gewicht': 3.5, 'Kosten': 400, 'Anmerkungen': 'PB 2, Parade –1, Zweihändig'},
    'Dolch/Messer': {'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'Gewicht': 0.5, 'Kosten': 25, 'Anmerkungen': '—'},
    'Hellebarde': {'Schaden': 'Stä+W8', 'Mindeststärke': 'W8', 'Gewicht': 3, 'Kosten': 250, 'Anmerkungen': 'Reichweite 1, Zweihändig'},
    'Kampfstab': {'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'Gewicht': 2, 'Kosten': 10, 'Anmerkungen': 'Parade +1, Reichweite 1, Zweihändig'},
    'Katana': {'Schaden': 'Stä+W6+1', 'Mindeststärke': 'W6', 'Gewicht': 1.5, 'Kosten': 1000, 'Anmerkungen': 'Zweihändig'},
    'Keule, Leicht': {'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'Gewicht': 1, 'Kosten': 25, 'Anmerkungen': '-'},
    'Keule, Schwer': {'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'Gewicht': 2.5, 'Kosten': 50, 'Anmerkungen': '-'},
    'Kriegshammer': {'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'Gewicht': 1, 'Kosten': 250, 'Anmerkungen': 'PB 1'},
    'Lanze': {'Schaden': 'Stä+W8', 'Mindeststärke': 'W8', 'Gewicht': 3, 'Kosten': 300, 'Anmerkungen': 'PB 2 Sturmangriff, Reichweite 2, berittener Kampf'},
    'Morgenstern': {'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'Gewicht': 1.5, 'Kosten': 200, 'Anmerkungen': 'ignoriert Schildboni'},
    'Rapier': {'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'Gewicht': 1, 'Kosten': 150, 'Anmerkungen': 'Parade +1'},
    'Schwert, Kurzschwert': {'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'Gewicht': 1, 'Kosten': 100, 'Anmerkungen': '-'},
    'Schwert, Langschwert': {'Schaden': 'Stä+W8', 'Mindeststärke': 'W8', 'Gewicht': 1.5, 'Kosten': 300, 'Anmerkungen': '-'},
    'Schwert, Zweihandschwert': {'Schaden': 'Stä+W10', 'Mindeststärke': 'W10', 'Gewicht': 3, 'Kosten': 400, 'Anmerkungen': 'Zweihändig'},
    'Speer': {'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'Gewicht': 1.5, 'Kosten': 100, 'Anmerkungen': 'Reichweite 1, Parade +1 wenn zweihändig'},
    'Spieß': {'Schaden': 'Stä+W8', 'Mindeststärke': 'W8', 'Gewicht': 9, 'Kosten': 400, 'Anmerkungen': 'Reichweite 2, Zweihändig'},
    'Streitkolben': {'Schaden': 'Stä+W6', 'Mindeststärke': 'W6', 'Gewicht': 2, 'Kosten': 100, 'Anmerkungen': '—'},
    'Zweihandhammer': {'Schaden': 'Stä+W10', 'Mindeststärke': 'W10', 'Gewicht': 5, 'Kosten': 400, 'Anmerkungen': 'Zweihändig, +2 Schaden/Gegenstände (Seite 100)'},
    'Bangstick': {'Schaden': '3W6', 'Mindeststärke': 'W6', 'Gewicht': 1, 'Kosten': 5, 'Anmerkungen': '-'},
    'Bajonett': {'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'Gewicht': 0.5, 'Kosten': 25, 'Anmerkungen': 'Stä+W6 und Parade +1 am Gewehr, Reichweite 1, Zweihändig'},
    'Kettensäge': {'Schaden': '2W6+4', 'Mindeststärke': 'W6', 'Gewicht': 10, 'Kosten': 200, 'Anmerkungen': 'Kritischer Fehlschlag Eigentrffer'},
    'Schlagring': {'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'Gewicht': 0.5, 'Kosten': 20, 'Anmerkungen': '-'},
    'Schlagstock': {'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'Gewicht': 0.5, 'Kosten': 10, 'Anmerkungen': ''},
    'Springmesser': {'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'Gewicht': 0.25, 'Kosten': 10, 'Anmerkungen': '-'},
    'Überlebensmesser': {'Schaden': 'Stä+W4', 'Mindeststärke': 'W4', 'Gewicht': 0.5, 'Kosten': 50, 'Anmerkungen': '+1 auf Überleben'},
    'Molekularmesser': {'Schaden': 'Stä+W4+2', 'Mindeststärke': 'W4', 'Gewicht': 0.25, 'Kosten': 250, 'Anmerkungen': 'PB 2, nicht werfen'},
    'Molekularschwert': {'Schaden': 'Stä+W8+2', 'Mindeststärke': 'W6', 'Gewicht': 1, 'Kosten': 500, 'Anmerkungen': 'PB 4'},
    'Laserschwert': {'Schaden': 'Stä+W6+8', 'Mindeststärke': 'W4', 'Gewicht': 1, 'Kosten': 1000, 'Anmerkungen': 'PB 12'}
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
grundfertigkeiten = [
            'Allgemeinwissen* ',
            'Athletik* ',
            'Heimlichkeit* ',
            'Überreden* ',
            'Wahrnehmung* '
    ]


##SCHILDE
##TYP PARADE DECKUNG MINDESTSTÄRKE GEWICHT(IN KG) KOSTEN
##  ANTIKE & MITTELALTER  
##Klein +1 — W4 2 50
##Mittel +2 –2 W6 4 100
##Groß +3 –4 W8 6 200
##  MODERN  
##Einsatzschild +3 –4 W4 2,5 80
##Ballistischer Schild +3 –4 W6 4,5 250
##Anmerkungen: Schaden Feuerwaffen –4
##  FUTURISTISCH  
##Polymerschild, Klein +1 — W4 1 200
##Polymerschild, Mittel +2 –2 W4 2 300
##Polymerschild, Groß +3 -4 W6 3 400




##FERNKAMPFWAFFEN
##TYP FRW SCHADEN PB FR
##MINDEST­
##STÄRKE 
##GEWICHT 
##(IN KG) KOSTEN
##  MITTELALTERLICH  
##Armbrust (handgespannt) 10/20/40 2W6 2 1 W6 2,5 250
##Anmerkungen: Handgespannt.
##Armbrust, Schwer 15/30/60 2W8 2 1 W6 4 400
##Axt, Wurfaxt 3/6/12 Stä+W6 — 1 W6 1,5 100 
##Bogen 12/24/48 2W6 — 1 W6 1,5 250
##Dolch/Messer 3/6/12 Stä+W4 — 1 W4 0,5 25
##Langbogen 15/30/60 2W6 1 1 W8 1,5 300
##Netz (beschwert) 3/6/12 — — 1 W4 4 50
##Schleuder (Athletik (Werfen)) 4/8/16 Stä+W4 — 1 W4 0,5 10
##Speer/Wurfspeer 3/6/12 Stä+W6 — 1 W6 1,5 100
##  MODERN  
##Armbrust 15/30/60 2W6 2 1 W6 3,5 300
##Kompositbogen 12/24/48 Stä+W6 1 1 W6 1,5 200
##SCHWARZPULVERWAFFEN
##TYP FRW SCHADEN PB FR SCHUSS
##MINDEST­
##STÄRKE
##GEWICHT 
##(IN KG) KOSTEN
##  PISTOLEN  
##Steinschlosspistole 5/10/20 2W6+1 — 1 — W4 1,5 150
##  MUSKETEN  
##Brown Bess oder 
##ähnliche Musketen 10/20/40 2W8 — 1 — W6 7,5 300
##Donnerbüchse 10/20/40 1–3W6 — 1 — W6 6 300
##  MUSKETEN MIT GEZOGENEM LAUF  
##Kentucky Rifle 15/30/60 2W8 2 1 — W6 4 300
##Springfield Model 1861 15/30/60 2W8 — 1 — W6 5,5 250
##Glattlauf-Muskete
##Moderne Feuerwaffen
##PISTOLEN
##TYP FRW SCHADEN PB FR SCHUSS
##MINDEST­
##STÄRKE
##GEWICHT 
##(IN KG) KOSTEN
##  REVOLVER  
##Derringer (.41) 3/6/12 2W4 — 1 2 W4 0,5 100
##Polizeirevolver (.38) 10/20/40 2W6 — 1 6 W4 1 150
##Colt Peacemaker (.45) 12/24/48 2W6+1 1 1 6 W4 2 200
##Smith & Wesson (.357) 12/24/48 2W6+1 1 1 6 W4 2,5 250
##  HALBAUTOMATIK  
##Colt 1911 (.45) 12/24/48 2W6+1 1 1 7 W4 2 200
##Desert Eagle (.50) 15/30/60 2W8 2 1 7 W6 4 300
##Glock (9mm) 12/24/48 2W6 1 1 17 W4 1,5 200
##Ruger (.22) 10/20/40 2W4 — 1 9 W4 1 100
##MASCHINENPISTOLEN
##TYP FRW SCHADEN PB FR SCHUSS
##MINDEST­
##STÄRKE
##GEWICHT 
##(IN KG) KOSTEN
##H&K MP5 (9mm) 12/24/48 2W6 1 3 30 W6 5 300
##Tommy Gun (.45) 12/24/48 2W6+1 1 3 20 W6 6,5 350
##Uzi (9mm) 12/24/48 2W6 1 3 32 W4 4,5 300
##SCHROTFLINTEN
##TYP FRW SCHADEN PB FR SCHUSS
##MINDEST­
##STÄRKE
##GEWICHT 
##(IN KG) KOSTEN
##Doppelflinte 12/24/48 1–3W6 — 1 2 W6 5,5 150
##Pumpgun 12/24/48 1–3W6 — 1 6 W4 4 150
##Abgesägte Doppelflinte 5/10/20 1–3W6 — 1 2 W4 3 150
##Streetsweeper 12/24/48 1–3W6 — 1 12 W6 5 450
##“Tommy” Gun
##M1911 Colt .45
##GEWEHRE
##TYP FRW SCHADEN PB FR SCHUSS
##MINDEST­
##STÄRKE
##GEWICHT 
##(IN KG) KOSTEN
##  UNTERHEBELREPETIERER UND KAMMERVERSCHLUSSGEWEHRE  
##Barret (.50) 50/100/200 2W10 4 1 10 W8 17,5 750
##M1 Garand (.30-06) 24/48/96 2W8 2 1 8 W6 5 300
##Jagdgewehr (.308) 24/48/96 2W8 2 1 5 W6 4 350
##Sharps Big 50 (.50) 30/60/120 2W10 2 1 1 W8 5,5 400
##Spencer Carbine (.52) 20/40/80 2W8 2 1 7 W4 4 250
##Winchester ‘73 (.44-40) 24/48/96 2W8–1 2 1 15 W6 5 300
##  STURMGEWEHR  
##AK47 (7.62mm) 24/48/96 2W8+1 2 3 30 W6 5 450
##M–16 (5.56mm) 24/48/96 2W8 2 3 20/30 W6 4 400
##Steyr AUG (5.56 mm) 24/48/96 2W8 2 3 30 W6 4 400
##MASCHINENGEWEHRE
##TYP FRW SCHADEN PB FR SCHUSS
##MINDEST­
##STÄRKE
##GEWICHT 
##(IN KG) KOSTEN
##Browning Automatic Rifle 
##(BAR) (.30-06) 20/40/60 2W8 2 3 20 W8 8,5 300
##Gatling (.45) 24/48/96 2W8 2 3 100 NA 85 500
##Minigun (7.62mm) 30/60/120 2W8+1 2 5 4000 W10 42,5 100.000
##M2 Browning (.50 Cal) 50/100/200 2W10 4 3 200 NA 42 1.500
##M60 (7.62mm) 30/60/120 2W8+1 2 3 100 W8 16,5 6.000
##MG42 (7.92mm) 30/60/120 2W8+1 2 4 200 W10 13 750
##SAW (5.56mm) 30/60/120 2W8 2 4 200 W8 10 4.000
##LASER (FUTURISTISCH)
##TYP FRW SCHADEN PB FR SCHUSS
##MINDEST­
##STÄRKE
##GEWICHT 
##(IN KG) KOSTEN
##Pistole 15/30/60 2W6 2 1 50 W4 1 250
##Maschinenpistole 15/30/60 2W6 2 4 100 W4 2 500
##Gewehr 30/60/120 3W6 2 3 100 W6 4 700
##Gatling-Laser 50/100/200 3W6+4 2 4 800 W8 10 1.000
##Spezielle Waffen
##KANONEN
##TYP FRW SCHADEN PB FR FLÄCHENSCHABLONE GEWICHT 
##(IN KG) KOSTEN
##Kanone (12 Pfünder)   Nach Munitionsart  600 10.000
##Kartätsche 24″ Pfad 2W6 — 1 MFS — 50
##Rundgeschoss 50/100/200 3W6+1 4 1 — — 50
##Schrapnell 50/100/200 3W6 — 1 MFS — 50
##KATAPULTE
##TYP FRW SCHADEN PB FR FLÄCHENSCHABLONE GEWICHT 
##(IN KG) KOSTEN
##Katapult 24/48/96 3W6 4 Speziell MFS — 10.000
##Trebuchet 30/60/120 3W8 4 Speziell MFS — 50.000
##FLAMMENWERFER
##TYP FRW SCHADEN PB FR SCHUSS
##MINDEST­
##STÄRKE
##GEWICHT 
##(IN KG) KOSTEN
##Flammenwerfer Kegelschablone 3W6 — 1 10 W8 35 300
##GRANATEN
##TYP FRW SCHADEN PB FR FLÄCHEN­
##SCHABLONE
##GEWICHT 
##(IN KG) KOSTEN
##Mk II („Pineapple“, 
##Zweiter Weltkrieg) 4/8/16 3W6 — — MFS 0,5 40
##Stielhandgranate 
##(„Potato Masher“, 
##Zweiter Weltkrieg)
##5/10/20 3W6–2 — — MFS 1 50
##Mk67 (Modern) 5/10/20 3W6 — — MFS 0,5 50
##Rauchgranate 5/10/20 — — — GFS 0,5 50
##Betäubungsgranate 5/10/20 — — — GFS 0,5 50
##MINEN
##TYP FRW SCHADEN PB FR FLÄCHENSCHABLONE GEWICHT 
##(IN KG) KOSTEN
##Antipersonenmine — 2W6+2 — — KFS 5 100
##Anmerkungen: Schwere Waffe.
##Panzerabwehrmine — 4W6 — — MFS 10 200
##Bouncing Betty — 3W6 — — KFS 4,5 125
##Claymore-Mine — 3W6 — — Speziell 2 75
##RAKETEN
##TYP FRW SCHADEN PB FR FLÄCHENSCHABLONE GEWICHT 
##(IN KG) KOSTEN
##TOW 75/150/300 5W10 34 1 MFS 104 60.000
##Hellfire 150/300/600 5W10 40 Speziell MFS 50 115.000
##Sidewinder 100/200/400 4W8 6 — KFS 94 600.000
##Sparrow 150/300/600 5W8 6 — KFS 309 125.000
##RAKETENWERFER UND TORPEDOS
##TYP FRW SCHADEN PB FR FLÄCHEN­
##SCHABLONE 
##GEWICHT 
##(IN KG) KOSTEN
##AT-4 24/48/96 4W8+2 24 1 MFS 7,5 1.500
##Bazooka 24/48/96 4W8 8 1 MFS 6 500
##M203 40MM 24/48/96 4W8 — 1 MFS 1,5 1.500
##M72 Law 24/48/96 4W8+2 22 1 MFS 2,5 750
##Panzerschreck 15/30/60 4W8 12 1 MFS 10 1.000
##Torpedo 300/600/1200 8W10 22 1 KFS 1500 500.000
##FAHRZEUGWAFFEN
##TYP FRW PB­GESCHOSSE HE­GESCHOSSE FR KOSTEN
##Mittleres Maschinengewehr 30/60/120 2W8+1, PB 2 — 3 750
##Schweres Maschinengewehr 50/100/200 2W10, PB 4 — 3 1.000
##Schwerer Flammenwerfer Kegel oder MFS — 3W8 1 1.000
##20mm-Kanone 50/100/200 2W12, PB 4 — 4 50.000
##25mm-Kanone 50/100/200 3W8, PB 4 — 3 75.000
##30mm-Kanone 50/100/200 3W8, PB 6 — 3 200.000
##40mm-Kanone 75/150/300 4W8, PB 5 3W8, PB 2, MFS 4 200.000
##2-Pfünder-Panzerabwehrkanone 75/150/300 4W8, PB 5 3W6, PB 2, MFS 1 75.000
##37mm-Panzerabwehrkanone 50/100/200 4W8, PB 3 4W6, PB 3, MFS 1 100.000
##57mm-Panzerabwehrkanone 75/150/300 4W8, PB 5 3W8, PB 3, MFS 1 150.000
##75mm-Panzerkanone 75/150/300 4W10, PB 6 3W8, PB 3, MFS 1 25.0000
##76mm-Panzerkanone 75/150/300 4W10, PB 10 3W8, PB 5, MFS 1 300.000
##88mm-Panzerkanone 100/200/400 4W10+1, PB 16 4W8, PB 8, MFS 1 500.000
##120mm-Panzerkanone 100/200/400 5W10, PB 31 4W8, PB 17, MFS 1 800.000
##125mm-Panzerkanone 100/200/400 5W10, PB 30 4W8, PB 15, MFS 1 1.000.000
##  FUTURISTISCH  
##Gatling-Laser 50/100/200 3W6+4, PB 4 — 4 1.000
##Schwerer Laser 150/300/600 4W10, PB 30 — 1 1.000.000
##


