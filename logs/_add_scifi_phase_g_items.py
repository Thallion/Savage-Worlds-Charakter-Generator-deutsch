"""Phase G Stufe 1: SciFi Kompendium Setting-Lücken füllen.

Fügt 4 Talente, 5 Handicaps, 14 Items, 2 Völker und 2 Völker-Erweiterungen
in `settings/SciFi Kompendium.json` ein.

Basiert auf `logs/phase_g_build_plan.md` (Stand 2026-06-01).
"""
import json
from pathlib import Path

PATH = Path('settings/SciFi Kompendium.json')
with PATH.open(encoding='utf-8') as f:
    data = json.load(f)

report = {'hinzugefuegt': [], 'uebersprungen': [], 'aktualisiert': []}


# ═══════════════════════════════════════════════════════════════
# A) 3 Edges (Talente) fehlen im SciFi-Setting
# Hinweis 2026-06-02: Bolster (SWADE Core) hat offizielle Mechanik
# "remove Distracted or Vulnerable from an ally after Testing a foe"
# (Voraussetzung WIL W8, Novice). Diese Mechanik ist IDENTISCH mit
# dem bestehenden SciFi-Talent "Ermutigen" (WIL W8, "Kann den Zustand
# Abgelenkt oder Verwundbar nach Herausfordern aufheben."). Bolster
# ist also bereits vorhanden — KEIN neuer Eintrag nötig. Für den
# Medic-Archetyp wird direkt das bestehende "Ermutigen" gewählt.
# ═══════════════════════════════════════════════════════════════
NEUE_TALENTE = {
    "Zertrümmerer": {
        "name": "Zertrümmerer",
        "kategorie": "Experte",
        "rang": "V",
        "voraussetzungen": [],
        "beschreibung": "Verdoppelt den Wurfbonus bei Würfen gegen Objekte (Wurf auf Tabelle 'Schaden gegen Objekte'). Wird der Schaden gleich oder übersteigt die Härte des Objekts, entsteht ein Kritischer Treffer.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True,
    },
    "Raserei": {
        "name": "Raserei",
        "kategorie": "Kampf",
        "rang": "A",
        "voraussetzungen": ["Berserker"],
        "beschreibung": "Erhält +1 Angriff und +1 Schaden im Nahkampf (zusätzlich zu Berserker), aber –2 auf alle anderen Proben, solange die Raserei anhält.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True,
    },
    "Gemeinsames Band": {
        "name": "Gemeinsames Band",
        "kategorie": "Sozial",
        "rang": "A",
        "voraussetzungen": ["WIL W8"],
        "beschreibung": "Verbündete im Befehlsradius erhalten +1 auf Erholungsproben. Kumulativ mit Anführer.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True,
    },
    # Phase G Stufe 3a (Engineer, Pilot, Road Warrior):
    "Zuverlässig": {
        "name": "Zuverlässig",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": [],
        "beschreibung": "Einmal pro Spielrunde kostenlose Wiederholung eines Unterstützen-Wurfs.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True,
    },
    "Raketen-Ass": {
        "name": "Raketen-Ass",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Pilot W8"],
        "beschreibung": "Ignoriert den Multi-Aktion-Abzug, wenn der Held in derselben Runde ein Manöver und eine andere Aktion ausführt.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True,
    },
}

talente = data.setdefault('talente', {})
for name, definition in NEUE_TALENTE.items():
    if name in talente:
        report['uebersprungen'].append(f'TALENT: {name}')
        continue
    talente[name] = definition
    report['hinzugefuegt'].append(f'TALENT: {name}')


# ═══════════════════════════════════════════════════════════════
# B) 5 Handicaps fehlen
# ═══════════════════════════════════════════════════════════════
NEUE_HANDICAPS = {
    "Gemein": {
        "name": "Gemein",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "-1 auf Überredenproben.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False,
    },
    "Wissenslücke": {
        "name": "Wissenslücke",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "-1 auf Allgemeinwissen- und Wahrnehmungsproben.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False,
    },
    "Todeswunsch": {
        "name": "Todeswunsch",
        "stufe": "schwer",
        "punkte": 2,
        "beschreibung": "Der Charakter sehnt sich nach einem heroischen/epischen Tod. Er sucht freiwillig die gefährlichsten Situationen und weigert sich, vor deutlich überlegenen Gegnern zurückzuweichen, wenn kein Verbündeter in der Nähe ist.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False,
    },
    "Blutarm": {
        "name": "Blutarm",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "-1 auf Konstitutionsproben.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False,
    },
    "Holografische Kraftprojektion": {
        "name": "Holografische Kraftprojektion",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "Körper ist ein Hologramm. Kann nicht wirklich Schaden verursachen oder anfassen. Anfällig für EMP-Angriffe (Robustheit halbiert).",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False,
    },
    # Bonus-Handicap für Aquatische Spezies (Dependency)
    # HINZUGEFÜGT 2026-06-02 nach User-Korrektur: User-Hinweis "passt
    # vielleicht doch. schau mal den Aquarianer aus dem Fantasy Kompendium
    # an". FK-Aquarianer verwendet in auto_handicaps einen
    # volk-spezifischen Dependency-Namen. Für die SciFi-Aquatische Spezies
    # wird daher "Abhängigkeit (Wasser)" als eigenständiges Handicap
    # verwendet, semantisch klarer als "Angewohnheit_leicht" (das eher
    # für Süchte/Quirks steht) und konsistent mit dem FK-Präzedenzfall.
    "Abhängigkeit (Wasser)": {
        "name": "Abhängigkeit (Wasser)",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "Verbringt der Held nicht mindestens 1 Stunde pro Tag in Wasser, leidet er unter Erschöpfung. Nach 24 Stunden ohne Wasser droht der Tod. Hintergrund: aquatische Spezies, FK-Aquarianer-Präzedenz.",
    },
    # Phase G Stufe 3a (Envoy, Enforcer):
    "Zungenklemmung": {
        "name": "Zungenklemmung",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "Du bist der starke, stille Typ. -1 auf Einschüchtern-, Überreden- und Provozieren-Proben.",
    },
    "Schwerelosigkeitskrankheit": {
        "name": "Schwerelosigkeitskrankheit",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "In Schwerelosigkeit wird dem Helden schwindlig und er leidet unter einer Stufe Erschöpfung. Diese Erschöpfung vergeht erst nach einer Stunde in einer beliebigen anderen Schwerkraftsituation.",
    },
    "Kann nicht schwimmen": {
        "name": "Kann nicht schwimmen",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "-2 auf Athletik-Proben beim Schwimmen, und jede zurückgelegte Bewegungseinheit kostet 3 Zoll Bewegungsweite.",
    },
}

handicaps = data.setdefault('handicaps', {})
for name, definition in NEUE_HANDICAPS.items():
    if name in handicaps:
        report['uebersprungen'].append(f'HANDICAP: {name}')
        continue
    handicaps[name] = definition
    report['hinzugefuegt'].append(f'HANDICAP: {name}')


# ═══════════════════════════════════════════════════════════════
# C) 14 Items fehlen
# (Infanteriekampfanzug und Batterie, Universal- existieren bereits
# und werden NICHT überschrieben.)
# ═══════════════════════════════════════════════════════════════
NEUE_ITEMS = {
    "Körperpanzerung +4": {
        "name": "Körperpanzerung +4",
        "kategorie": "Rüstung",
        "gewicht": 2,
        "kosten": 200,
        "setting": "scifi",
        "beschreibung": "Leichte, gepanzerte Kleidung aus komplexen Polymeren. Deckt Torso, Arme und Beine ab.",
        "torso": 4, "arme": 4, "beine": 4, "kopf": 0,
        "mindeststaerke": "W4",
        "aktiv": True,
    },
    "Raumanzug, Kampf-": {
        "name": "Raumanzug, Kampf-",
        "kategorie": "Rüstung",
        "gewicht": 10,
        "kosten": 5000,
        "setting": "scifi",
        "beschreibung": "Ganzkörperanzug für den Weltraum mit Panzerung +4. Versiegelt. Liefert 12 Stunden Luft. Schützt vor Vakuum.",
        "torso": 4, "arme": 4, "beine": 4, "kopf": 0,
        "mindeststaerke": "W6",
        "aktiv": True,
    },
    "Infanterie-Kampfanzugshelm +6": {
        "name": "Infanterie-Kampfanzugshelm +6",
        "kategorie": "Rüstung",
        "gewicht": 1,
        "kosten": 100,
        "setting": "scifi",
        "beschreibung": "Helm zum Infanterie-Kampfanzug. Deckt Kopf und Gesicht ab.",
        "torso": 0, "arme": 0, "beine": 0, "kopf": 6,
        "mindeststaerke": "W4",
        "aktiv": True,
    },
    "Schwerkraftharnisch": {
        "name": "Schwerkraftharnisch",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 2,
        "kosten": 500,
        "beschreibung": "Persönliches Schwerkraft-Manipulationsfeld. Erlaubt dem Träger das Schweben (Pace 6 in der Luft, Höhe 1-2). Benötigt eine Universalbatterie.",
        "aktiv": True,
    },
    "Gyrojet-Pistole": {
        "name": "Gyrojet-Pistole",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 1.5,
        "kosten": 400,
        "typ": "Fernkampf",
        "mindeststaerke": "W4",
        "beschreibung": "Pistolen-Gyrojet. Anmerkungen: Schwere Waffe. Munition: Gyrojet-Geschosse.",
        "eigenschaften": {
            "Schaden": "3W6 (I)",
            "Reichweite": "12/24/48",
            "PB": "-",
            "FR": "1",
            "Schuss": "10",
        },
        "aktiv": True,
    },
    "Gyrojet-Gewehr": {
        "name": "Gyrojet-Gewehr",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 3,
        "kosten": 600,
        "typ": "Fernkampf",
        "mindeststaerke": "W6",
        "beschreibung": "Gewehr-Gyrojet. Anmerkungen: Schwere Waffe. Munition: Gyrojet-Geschosse.",
        "eigenschaften": {
            "Schaden": "3W6 (I)",
            "Reichweite": "24/48/96",
            "PB": "-",
            "FR": "1",
            "Schuss": "30",
        },
        "aktiv": True,
    },
    "Heiligtum": {
        "name": "Heiligtum",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.5,
        "kosten": 50,
        "beschreibung": "Heiliger Gegenstand des Glaubens. Gewährt +1 auf Glaubensproben und/oder Erholungsproben, wenn in der Nähe eines Heiligtums (SL-Entscheidung).",
        "aktiv": True,
    },
    "Betäubungsgranate": {
        "name": "Betäubungsgranate",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.25,
        "kosten": 50,
        "typ": "Fernkampf",
        "beschreibung": "Granate mit Betäubungsladung. Anmerkungen: MFS, Betäuben.",
        "eigenschaften": {
            "Schaden": "3W6 (B)",
            "Reichweite": "5/10/20",
            "PB": "-",
            "FR": "1",
            "Schuss": "1",
        },
        "aktiv": True,
    },
    "Rauchgranate": {
        "name": "Rauchgranate",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.25,
        "kosten": 50,
        "typ": "Fernkampf",
        "beschreibung": "Granate mit Rauchladung. Erzeugt eine KFS Rauchwolke. Anmerkungen: MFS.",
        "eigenschaften": {
            "Schaden": "—",
            "Reichweite": "5/10/20",
            "PB": "-",
            "FR": "1",
            "Schuss": "1",
        },
        "aktiv": True,
    },
    "Bienenstock-Granate": {
        "name": "Bienenstock-Granate",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.25,
        "kosten": 50,
        "typ": "Fernkampf",
        "beschreibung": "Granate mit Schrapnell-Ladung (Bienenstock). Wirkt in einer Kegelschablone, ähnlich einer großen Schrotflinte. Anmerkungen: MFS, Schwere Waffe.",
        "eigenschaften": {
            "Schaden": "3W6 (I)",
            "Reichweite": "5/10/20",
            "PB": "-",
            "FR": "1",
            "Schuss": "1",
        },
        "aktiv": True,
    },
    "Persönliche Datenassistenz": {
        "name": "Persönliche Datenassistenz",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.5,
        "kosten": 500,
        "beschreibung": "Tragbarer Computer / Smartphone. Ermöglicht Kommunikation, Information und moderate Hacking-Funktionen.",
        "aktiv": True,
    },
    "Vibro-Klinge": {
        "name": "Vibro-Klinge",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 0.5,
        "kosten": 525,
        "typ": "Nahkampf",
        "mindeststaerke": "W4",
        "beschreibung": "Klinge mit vibrierender Schneide. Anmerkungen: Vibro, sehr laut, +1W6 Schaden, PB 2.",
        "eigenschaften": {
            "Schaden": "Stä+W6+W4",
            "Reichweite": "nah",
            "PB": "2",
            "FR": "-",
            "Schuss": "-",
        },
        "aktiv": True,
    },
    "Vibro-Schwert": {
        "name": "Vibro-Schwert",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 1.5,
        "kosten": 600,
        "typ": "Nahkampf",
        "mindeststaerke": "W6",
        "beschreibung": "Schwert mit vibrierender Schneide. Anmerkungen: Vibro, sehr laut, +1W6 Schaden, PB 2.",
        "eigenschaften": {
            "Schaden": "Stä+W8+W6",
            "Reichweite": "nah",
            "PB": "2",
            "FR": "-",
            "Schuss": "-",
        },
        "aktiv": True,
    },
    "Mikro-Flugkörperwerfer": {
        "name": "Mikro-Flugkörperwerfer",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 2.5,
        "kosten": 1000,
        "typ": "Fernkampf",
        "mindeststaerke": "W6",
        "beschreibung": "Schulter-Flugkörperwerfer. Anmerkungen: GFS, Schwere Waffe, ignoriert Standard-Panzerung.",
        "eigenschaften": {
            "Schaden": "4W6",
            "Reichweite": "50/100/200",
            "PB": "2",
            "FR": "1",
            "Schuss": "1",
        },
        "aktiv": True,
    },
    # Phase G Stufe 3a (G1 Builds): 20+ weitere SciFi-Items
    "Biolink": {
        "name": "Biolink",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0,
        "kosten": 100,
        "beschreibung": "Implantat, das den Charakter mit seiner Waffensperre, dem Scanner und dem Anzug verbindet. Erfordert keine Hand-Aktionen für einfache Aktionen.",
        "aktiv": True,
    },
    "Klebstoffpflaster": {
        "name": "Klebstoffpflaster",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.05,
        "kosten": 5,
        "beschreibung": "Selbstklebendes Wundpflaster. Stabilisiert Verwundete (+1 auf Erste Hilfe innerhalb der Goldenen Stunde).",
        "aktiv": True,
    },
    "Medi-Scanner": {
        "name": "Medi-Scanner",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.5,
        "kosten": 200,
        "beschreibung": "Tragbares medizinisches Diagnosegerät. Erlaubt freie Wiederholung einer Heilen-Probe.",
        "aktiv": True,
    },
    "Synth-Mesh": {
        "name": "Synth-Mesh",
        "kategorie": "Rüstung",
        "setting": "scifi",
        "gewicht": 1,
        "kosten": 100,
        "beschreibung": "Anzug aus synthetischen Polymeren. Leicht und flexibel.",
        "torso": 2, "arme": 0, "beine": 0, "kopf": 0,
        "mindeststaerke": "W4",
        "aktiv": True,
    },
    "Taschenlampe": {
        "name": "Taschenlampe",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.25,
        "kosten": 10,
        "beschreibung": "Tragbare LED-Taschenlampe. Erhellt 10 Zoll Strahl, eliminiert Dämmerungsabzüge in der Lichtung.",
        "aktiv": True,
    },
    "Nahrungsriegel": {
        "name": "Nahrungsriegel",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.1,
        "kosten": 1,
        "beschreibung": "Nahrhafter Riegel. Stillt Hunger für 1 Tag.",
        "aktiv": True,
    },
    "Wasserbehälter": {
        "name": "Wasserbehälter",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.5,
        "kosten": 5,
        "beschreibung": "Wiederverschließbarer Behälter mit Trinkwasser (1 Liter).",
        "aktiv": True,
    },
    "Panzertape": {
        "name": "Panzertape",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.1,
        "kosten": 5,
        "beschreibung": "Universalklebeband. Unverzichtbar für Improvisation und schnelle Reparaturen.",
        "aktiv": True,
    },
    "Kaugummi": {
        "name": "Kaugummi",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0,
        "kosten": 0.5,
        "beschreibung": "Kaumasse. Nützlich beim Anbringen kleiner Sensoren, Glücksbringer.",
        "aktiv": True,
    },
    "Seil": {
        "name": "Seil",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 2,
        "kosten": 10,
        "beschreibung": "30 Meter leichtes Kletterseil. Hält 500 kg.",
        "aktiv": True,
    },
    "Kevlarjacke & Jeans": {
        "name": "Kevlarjacke & Jeans",
        "kategorie": "Rüstung",
        "setting": "scifi",
        "gewicht": 1.5,
        "kosten": 100,
        "beschreibung": "Lässige Kleidung mit Kevlar-Verstärkung an Jacke und Hose.",
        "torso": 2, "arme": 2, "beine": 2, "kopf": 0,
        "mindeststaerke": "W4",
        "aktiv": True,
    },
    "Jagdgewehr": {
        "name": "Jagdgewehr",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 3,
        "kosten": 300,
        "typ": "Fernkampf",
        "mindeststaerke": "W6",
        "beschreibung": "Hochleistungs-Repetierbüchse. Anmerkungen: Snapfire.",
        "eigenschaften": {
            "Schaden": "2W8+1",
            "Reichweite": "24/48/96",
            "PB": "2",
            "FR": "1",
            "Schuss": "5",
        },
        "aktiv": True,
    },
    "Glock 9mm": {
        "name": "Glock 9mm",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 1,
        "kosten": 150,
        "typ": "Fernkampf",
        "mindeststaerke": "W4",
        "beschreibung": "Standard-Halbautomatik-Pistole.",
        "eigenschaften": {
            "Schaden": "2W6",
            "Reichweite": "12/24/48",
            "PB": "1",
            "FR": "1",
            "Schuss": "15",
        },
        "aktiv": True,
    },
    "Medikit": {
        "name": "Medikit",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 1,
        "kosten": 100,
        "beschreibung": "Umfangreiches medizinisches Set. +1 auf Heilen-Proben.",
        "aktiv": True,
    },
    "Granatwerfer": {
        "name": "Granatwerfer",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 2.5,
        "kosten": 400,
        "typ": "Fernkampf",
        "mindeststaerke": "W6",
        "beschreibung": "Unterlauf-Granatwerfer. Anmerkungen: Snapfire, LBT.",
        "eigenschaften": {
            "Schaden": "siehe Granate",
            "Reichweite": "8/16/32",
            "PB": "-",
            "FR": "1",
            "Schuss": "1",
        },
        "aktiv": True,
    },
    "Granate": {
        "name": "Granate",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.25,
        "kosten": 50,
        "typ": "Fernkampf",
        "beschreibung": "Standard-Sprenggranate. Anmerkungen: MFS, Schwere Waffe.",
        "eigenschaften": {
            "Schaden": "3W6",
            "Reichweite": "5/10/20",
            "PB": "-",
            "FR": "1",
            "Schuss": "1",
        },
        "aktiv": True,
    },
    "Rohr": {
        "name": "Rohr",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 1.5,
        "kosten": 0,
        "typ": "Nahkampf",
        "mindeststaerke": "W4",
        "beschreibung": "Metallrohr. Anmerkungen: Parade −2.",
        "eigenschaften": {
            "Schaden": "Stä+W6",
            "Reichweite": "nah",
            "PB": "-2",
            "FR": "-",
            "Schuss": "-",
        },
        "aktiv": True,
    },
    "Standard-Gyrojet": {
        "name": "Standard-Gyrojet",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.05,
        "kosten": 5,
        "beschreibung": "Standard-Patrone für Gyrojet-Waffen. Munition, MFS.",
        "aktiv": True,
    },
    "Rauch-Gyrojet": {
        "name": "Rauch-Gyrojet",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.05,
        "kosten": 10,
        "beschreibung": "Gyrojet-Patrone mit Rauchladung. Erzeugt eine KFS Rauchwolke. Anmerkungen: MFS, -4 auf Laser/Elektronik.",
        "aktiv": True,
    },
    "Spreng-Gyrojet": {
        "name": "Spreng-Gyrojet",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.05,
        "kosten": 15,
        "beschreibung": "Gyrojet-Patrone mit Sprengladung. Anmerkungen: MFS.",
        "eigenschaften": {
            "Schaden": "3W4",
            "Reichweite": "12/24/48",
            "PB": "-",
            "FR": "1",
            "Schuss": "1",
        },
        "aktiv": True,
    },
    "Pulspatronen-Gatling": {
        "name": "Pulspatronen-Gatling",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 4,
        "kosten": 1500,
        "typ": "Fernkampf",
        "mindeststaerke": "W8",
        "beschreibung": "Schwere Impulskanone. Anmerkungen: Snapfire.",
        "eigenschaften": {
            "Schaden": "3W8",
            "Reichweite": "20/40/80",
            "PB": "-",
            "FR": "3",
            "Schuss": "20",
        },
        "aktiv": True,
    },
    "Leichte Flugkörper": {
        "name": "Leichte Flugkörper",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.5,
        "kosten": 100,
        "beschreibung": "Leichte Lenkwaffe für Mikro-Flugkörperwerfer. Anmerkungen: GFS.",
        "eigenschaften": {
            "Schaden": "4W6",
            "Reichweite": "50/100/200",
            "PB": "2",
            "FR": "1",
            "Schuss": "1",
        },
        "aktiv": True,
    },
    "Rotpunktvisier": {
        "name": "Rotpunktvisier",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.25,
        "kosten": 50,
        "beschreibung": "Reflexvisier mit Leuchtpunkt. +1 auf Schießen-Proben bei kurzer und mittlerer Reichweite.",
        "aktiv": True,
    },
    "Energie-Kampfaxt": {
        "name": "Energie-Kampfaxt",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 4,
        "kosten": 1200,
        "typ": "Nahkampf",
        "mindeststaerke": "W8",
        "beschreibung": "Schwere Energieaxt. Anmerkungen: Vibro, Cauterize, Kritischer Fehler trifft Benutzer.",
        "eigenschaften": {
            "Schaden": "Stä+W10",
            "Reichweite": "nah",
            "PB": "4",
            "FR": "-",
            "Schuss": "-",
        },
        "aktiv": True,
    },
    "Commlink": {
        "name": "Commlink",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0.05,
        "kosten": 25,
        "beschreibung": "Implantat oder tragbares Kommunikationsgerät. Ermöglicht Reichweiten-Kommunikation bis 5 Meilen.",
        "aktiv": True,
    },
    "Betäubungspike": {
        "name": "Betäubungspike",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 1.5,
        "kosten": 200,
        "typ": "Nahkampf",
        "mindeststaerke": "W6",
        "beschreibung": "Schockspeer. Anmerkungen: Nicht-tödlich, Stun, Reichweite 2 (Reach).",
        "eigenschaften": {
            "Schaden": "Stä+W6",
            "Reichweite": "2",
            "PB": "-",
            "FR": "-",
            "Schuss": "-",
        },
        "aktiv": True,
    },
    "Sprungpack": {
        "name": "Sprungpack",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 3,
        "kosten": 1500,
        "beschreibung": "Düsenrucksack. Erlaubt eine volle Bewegungsrunde, ignoriert 2 Punkte Ausweich-Abzug. Benötigt Universalbatterie.",
        "aktiv": True,
    },
    "Lasergewehr": {
        "name": "Lasergewehr",
        "kategorie": "Waffe",
        "setting": "scifi",
        "gewicht": 3,
        "kosten": 800,
        "typ": "Fernkampf",
        "mindeststaerke": "W6",
        "beschreibung": "Standard-Lasergewehr. Anmerkungen: Cauterize, Overcharge.",
        "eigenschaften": {
            "Schaden": "3W6",
            "Reichweite": "30/60/120",
            "PB": "2",
            "FR": "3",
            "Schuss": "20",
        },
        "aktiv": True,
    },
    "Mikrosender": {
        "name": "Mikrosender",
        "kategorie": "Ausrüstung",
        "setting": "scifi",
        "gewicht": 0,
        "kosten": 50,
        "beschreibung": "Subminiatur-Sender. Reichweite 100 Meilen, einseitig.",
        "aktiv": True,
    },
}

ausruestung = data.setdefault('ausruestung', {})
for name, definition in NEUE_ITEMS.items():
    if name in ausruestung:
        report['uebersprungen'].append(f'ITEM: {name}')
        continue
    ausruestung[name] = definition
    report['hinzugefuegt'].append(f'ITEM: {name}')


# ═══════════════════════════════════════════════════════════════
# D) 2 NEUE Völker
# ═══════════════════════════════════════════════════════════════
NEUE_VOELKER = {
    "Kybernetische Soldaten": {
        "name": "Kybernetische Soldaten",
        "handicaps": [
            "Skrupellos",
            "Niedergravitations-/Schwerelosigkeitsweltler",
        ],
        "talente": [
            "Kampfreflexe",
        ],
        "besonderheiten": [
            "Ausgebildet für den Krieg (-4 auf Allgemeinwissenproben)",
            "Flight (Schwerkraftantrieb, Pace 12, Sprint-W6)",
            "Low G Worlder (-1 Stärke, kumulativ mit Handicap)",
            "Reduced Pace (Laufwürfel W4)",
            "Robustheit +1",
            "Schmerzresistenz (ignoriert 1 Punkt Wundabzüge)",
        ],
        "sprachen": [],
        "altersspanne": "30-50 Jahre",
        "groesse_maennlich": "1,80-2,10m",
        "groesse_weiblich": "1,70-2,00m",
        "aktiv": True,
        "custom": False,
        "effects": {
            "attribute_bonuses": {},
            "robustheit_bonus": 1,
            "bewegungsweite_bonus": 0,
            "fertigkeits_startboni": {},
            "fertigkeits_startmalus": {},
            "fertigkeits_modifier_boni": {},
            "auto_talente": [
                "Kampfreflexe",
            ],
            "auto_handicaps": [
                "Skrupellos",
                "Niedergravitations-/Schwerelosigkeitsweltler",
            ],
            "spezielle_effekte": {
                "flight": True,
                "low_g_worlder": True,
                "reduced_pace": True,
                "schmerzresistenz": True,
                "ausgebildet_fuer_krieg": True,
            },
            "wahlmoeglichkeiten": {},
        },
    },
    "Aquatische Spezies": {
        "name": "Aquatische Spezies",
        "handicaps": [
            "Abhängigkeit (Wasser)",
        ],
        "talente": [],
        "besonderheiten": [
            "Aquatic (kann nicht ertrinken, Pace 6 im Wasser)",
            "Dependency (1 Stunde pro Tag im Wasser, sonst Erschöpfung)",
            "Low Light Vision (Dämmerungssicht)",
            "Robustheit +1",
        ],
        "sprachen": [],
        "altersspanne": "Variabel",
        "groesse_maennlich": "variabel",
        "groesse_weiblich": "variabel",
        "aktiv": True,
        "custom": False,
        "effects": {
            "attribute_bonuses": {},
            "robustheit_bonus": 1,
            "bewegungsweite_bonus": 0,
            "fertigkeits_startboni": {},
            "fertigkeits_startmalus": {},
            "fertigkeits_modifier_boni": {},
            "auto_talente": [],
            "auto_handicaps": [
                "Abhängigkeit (Wasser)",
            ],
            "spezielle_effekte": {
                "aquatic": True,
                "dependency": True,
                "low_light_vision": True,
                "daemmerungssicht": True,
            },
            "wahlmoeglichkeiten": {},
        },
    },
}

voelker = data.setdefault('voelker', {})
for name, definition in NEUE_VOELKER.items():
    if name in voelker:
        report['uebersprungen'].append(f'VOLK: {name}')
        continue
    voelker[name] = definition
    report['hinzugefuegt'].append(f'VOLK: {name}')


# ═══════════════════════════════════════════════════════════════
# E) 2 bestehende Völker erweitern
# ═══════════════════════════════════════════════════════════════
# Roboter: Überreden und Heimlichkeit sind keine Grundfertigkeiten (W4-2).
# Auch in 'besonderheiten' dokumentiert für Sichtbarkeit im UI.
if 'Roboter' in voelker:
    rb = voelker['Roboter']
    rb.setdefault('effects', {})
    rb['effects'].setdefault('fertigkeits_startmalus', {})
    rb['effects']['fertigkeits_startmalus'].setdefault('Überreden', -2)
    rb['effects']['fertigkeits_startmalus'].setdefault('Heimlichkeit', -2)
    if 'Keine Kernfertigkeiten (Überreden, Heimlichkeit: W4-2)' not in rb.get('besonderheiten', []):
        rb.setdefault('besonderheiten', []).append(
            'Keine Kernfertigkeiten (Überreden, Heimlichkeit: W4-2)'
        )
    report['aktualisiert'].append('VOLK: Roboter (fertigkeits_startmalus + besonderheit)')

# Insektoide: Wahlmöglichkeit 'outsider_statt_trennungsangst' ergänzen.
if 'Insektoide' in voelker:
    ins = voelker['Insektoide']
    ins.setdefault('effects', {})
    ins['effects'].setdefault('wahlmoeglichkeiten', {})
    ins['effects']['wahlmoeglichkeiten'].setdefault('outsider_statt_trennungsangst', True)
    report['aktualisiert'].append('VOLK: Insektoide (wahlmoeglichkeiten.outsider_statt_trennungsangst)')


# ═══════════════════════════════════════════════════════════════
# Save + report
# ═══════════════════════════════════════════════════════════════
with PATH.open('w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('=' * 60)
print('PHASE G STUFE 1 — SciFi Kompendium Setting-Erweiterungen')
print('=' * 60)
print(f"Hinzugefügt: {len(report['hinzugefuegt'])}")
for e in report['hinzugefuegt']:
    print(f"  + {e}")
print()
print(f"Übersprungen (bereits vorhanden): {len(report['uebersprungen'])}")
for e in report['uebersprungen']:
    print(f"  = {e}")
print()
print(f"Aktualisiert: {len(report['aktualisiert'])}")
for e in report['aktualisiert']:
    print(f"  ~ {e}")
print()
print(f"Gesamt Talente:      {len(data['talente'])}")
print(f"Gesamt Handicaps:    {len(data['handicaps'])}")
print(f"Gesamt Items:        {len(data['ausruestung'])}")
print(f"Gesamt Völker:       {len(data['voelker'])}")

# JSON-Validierung
try:
    with PATH.open(encoding='utf-8') as f:
        json.load(f)
    print("\n✓ JSON valide")
except Exception as e:
    print(f"\n✗ JSON-FEHLER: {e}")
