import json
from pathlib import Path

path = Path('settings/SciFi Kompendium.json')
with path.open(encoding='utf-8') as f:
    data = json.load(f)

items = data.setdefault('ausruestung', {})

neu = {
    "Plasmapistole": {
        "name": "Plasmapistole", "kategorie": "Waffe", "setting": "scifi",
        "gewicht": 4, "kosten": 800, "aktiv": True,
        "beschreibung": "Pistole, die superheiße Gas-Geschosse abfeuert. Anmerkungen: Kauterisieren, Plasma, Schwere Waffe. Munition: Energiepakete.",
        "typ": "Fernkampf", "mindeststaerke": "W6",
        "eigenschaften": {"Schaden": "2W10 (I)", "Reichweite": "5/10/20", "FR": "1", "Schuss": "10", "PB": "-"},
    },
    "Plasmagewehr": {
        "name": "Plasmagewehr", "kategorie": "Waffe", "setting": "scifi",
        "gewicht": 6, "kosten": 1000, "aktiv": True,
        "beschreibung": "Gewehr, das superheiße Gas-Geschosse abfeuert. Anmerkungen: Kauterisieren, Plasma, Schwere Waffe. Munition: Energiepakete.",
        "typ": "Fernkampf", "mindeststaerke": "W8",
        "eigenschaften": {"Schaden": "2W10 (I)", "Reichweite": "10/20/40", "FR": "1", "Schuss": "10", "PB": "-"},
    },
    "Blasterpistole": {
        "name": "Blasterpistole", "kategorie": "Waffe", "setting": "scifi",
        "gewicht": 0.5, "kosten": 200, "aktiv": True,
        "beschreibung": "Teilchenbeschleuniger in Pistolenform. Anmerkungen: –. Munition: Partikelpakete.",
        "typ": "Fernkampf", "mindeststaerke": "W4",
        "eigenschaften": {"Schaden": "2W6+2", "Reichweite": "12/24/48", "FR": "1", "Schuss": "50", "PB": "2"},
    },
    "Schwere Blasterpistole": {
        "name": "Schwere Blasterpistole", "kategorie": "Waffe", "setting": "scifi",
        "gewicht": 1.5, "kosten": 300, "aktiv": True,
        "beschreibung": "Schwere Variante der Blasterpistole (Teilchenbeschleuniger). Anmerkungen: –. Munition: Partikelpakete.",
        "typ": "Fernkampf", "mindeststaerke": "W6",
        "eigenschaften": {"Schaden": "3W6", "Reichweite": "10/20/40", "FR": "1", "Schuss": "40", "PB": "2"},
    },
    "Blastergewehr": {
        "name": "Blastergewehr", "kategorie": "Waffe", "setting": "scifi",
        "gewicht": 3, "kosten": 600, "aktiv": True,
        "beschreibung": "Teilchenbeschleuniger in Gewehr-Form. Anmerkungen: –. Munition: Partikelpakete.",
        "typ": "Fernkampf", "mindeststaerke": "W6",
        "eigenschaften": {"Schaden": "3W6+2", "Reichweite": "25/50/100", "FR": "1", "Schuss": "30", "PB": "2"},
    },
    "Laserpistole": {
        "name": "Laserpistole", "kategorie": "Waffe", "setting": "scifi",
        "gewicht": 1, "kosten": 250, "aktiv": True,
        "beschreibung": "Pistole, die gebündelte Laserstrahlen verschießt. Anmerkungen: Kauterisieren, Überladen. Munition: Energiepakete.",
        "typ": "Fernkampf", "mindeststaerke": "W4",
        "eigenschaften": {"Schaden": "2W6", "Reichweite": "15/30/60", "FR": "1", "Schuss": "50", "PB": "2"},
    },
    "Betäubungsschlagstock": {
        "name": "Betäubungsschlagstock", "kategorie": "Waffe", "setting": "scifi",
        "gewicht": 1, "kosten": 260, "aktiv": True,
        "beschreibung": "Nahkampfwaffe, die das Ziel betäubt. Anmerkungen: Betäuben, Betäubungsschaden.",
        "typ": "Nahkampf", "mindeststaerke": "W4",
        "eigenschaften": {"Schaden": "Stä+W4", "Reichweite": "nah", "FR": "-", "Schuss": "-", "PB": "-"},
    },
    "EMP-Granate": {
        "name": "EMP-Granate", "kategorie": "Waffe", "setting": "scifi",
        "gewicht": 0.5, "kosten": 150, "aktiv": True,
        "beschreibung": "Granate mit elektromagnetischem Impuls. Anmerkungen: Nicht tödlich, nur gegen elektronische Geräte.",
        "typ": "Fernkampf",
        "eigenschaften": {"Schaden": "4W6", "Reichweite": "5/10/20", "FR": "1", "Schuss": "1", "PB": "-"},
    },
    "Cyberdeck": {
        "name": "Cyberdeck", "kategorie": "Ausrüstung", "setting": "scifi",
        "gewicht": 1, "kosten": 500, "aktiv": True,
        "beschreibung": "Hardware für Netrunning. Ermöglicht Hackern die direkte Verbindung mit der virtuellen Realität. Z (Zero-Tangle).",
    },
    "Raumanzug": {
        "name": "Raumanzug", "kategorie": "Rüstung", "setting": "scifi",
        "gewicht": 9, "kosten": 500, "aktiv": True,
        "beschreibung": "Ganzkörperanzug für den Weltraum. Versiegelt. Liefert 12 Stunden Luft. Schützt vor Vakuum.",
        "torso": 1, "arme": 1, "beine": 1, "kopf": 0,
        "mindeststaerke": "W4",
    },
    "Nanowear": {
        "name": "Nanowear", "kategorie": "Ausrüstung", "setting": "scifi",
        "gewicht": 2, "kosten": 500, "aktiv": True,
        "beschreibung": "Fortschrittlicher Stoff, der Form, Farbe oder Textur verändern kann (Smoking, Parka, Trainingsanzug). Bildet KEINE Panzerungen oder versiegelten Anzüge. Z (Zero-Tangle).",
    },
    "Scanner": {
        "name": "Scanner", "kategorie": "Ausrüstung", "setting": "scifi",
        "gewicht": 0.5, "kosten": 500, "aktiv": True,
        "beschreibung": "Gerät zum Aufspüren und Identifizieren von Materie oder Energie. Ziele müssen nicht sichtbar sein. Reichweite: 50m (klein/Handheld) oder 500m (mittel/Rucksack).",
    },
    "Medi-Gel": {
        "name": "Medi-Gel", "kategorie": "Ausrüstung", "setting": "scifi",
        "gewicht": 0.5, "kosten": 50, "aktiv": True,
        "beschreibung": "Medizinisches Gel, das eine Dosis +2 auf Heilen-Proben innerhalb der Goldenen Stunde gewährt, oder +2 um eine verblutende Person zu stabilisieren. Z (Zero-Tangle).",
    },
    "Waffensperre": {
        "name": "Waffensperre", "kategorie": "Ausrüstung", "setting": "scifi",
        "gewicht": 0, "kosten": 200, "aktiv": True,
        "beschreibung": "Biometrische Sperre, die eine Waffe an eine Person koppelt. ES I: Fingerabdruck, ES II+: Biorhythmus.",
    },
    "Tarnanzug": {
        "name": "Tarnanzug", "kategorie": "Rüstung", "setting": "scifi",
        "gewicht": 1, "kosten": 2500, "aktiv": True,
        "beschreibung": "Ganzkörperanzug, der Farbe und Schatten an die Umgebung anpasst. Gewährt +2 auf Heimlichkeitsproben. Bei ES II: Verdoppelte Kosten für Unsichtbarkeit (1 Stunde Energie, ES III: 1 Tag).",
        "torso": 0, "arme": 0, "beine": 0, "kopf": 0,
        "mindeststaerke": "W4",
    },
    "Holoprojektor": {
        "name": "Holoprojektor", "kategorie": "Ausrüstung", "setting": "scifi",
        "gewicht": 2, "kosten": 1000, "aktiv": True,
        "beschreibung": "3D-Hologramm-Projektor. Erzeugt Bilder, die eine KFS (4m Durchmesser) um das Gerät ausfüllen. Kann Furchtprobe auslösen oder Angreifer ablenken (SL-Ermessen). Z (Zero-Tangle).",
    },
    "Energiepaket": {
        "name": "Energiepaket", "kategorie": "Ausrüstung", "setting": "scifi",
        "gewicht": 0.5, "kosten": 50, "aktiv": True,
        "beschreibung": "Standard-Energiemunition für Plasma- und Laserwaffen. Munition.",
    },
    "Zielsystem": {
        "name": "Zielsystem", "kategorie": "Cyberware", "setting": "scifi",
        "gewicht": 0, "kosten": 5000, "aktiv": True,
        "beschreibung": "Implantat mit integriertem Ziel- und Nachverfolgungssystem. Reduziert bei direktem Schießen die Abzüge von Angesagten Zielen, Deckung, Reichweite, Größenkategorie und Geschwindigkeit um 2 Punkte. Funktioniert nicht mit Gelenkten Waffen. 1 ES-Slot.",
        "esslots": 1,
    },
}

hinzugefuegt = 0
uebersprungen = []
for name, definition in neu.items():
    if name in items:
        uebersprungen.append(name)
        continue
    items[name] = definition
    hinzugefuegt += 1

with path.open('w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Hinzugefügt: {hinzugefuegt}")
print(f"Übersprungen (bereits vorhanden): {uebersprungen}")
print(f"Gesamt Items jetzt: {len(items)}")
