#!/usr/bin/env python3
"""
Baut die Hellfrost.json Setting-Datei aus dem Fantasy Kompendium und
Hellfrost-spezifischen Daten auf.
"""

import json
import copy
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FK_PATH = os.path.join(BASE_DIR, "settings", "Fantasy Kompendium.json")
HF_PATH = os.path.join(BASE_DIR, "settings", "Hellfrost.json")

# FK laden
with open(FK_PATH, "r", encoding="utf-8") as f:
    fk = json.load(f)


# ============================================================
# 1. ATTRIBUTE (identisch zum FK)
# ============================================================
attribute = {
    "Geschicklichkeit": {"attribut_name": "Geschicklichkeit", "wert": 4, "modifier": 0},
    "Verstand": {"attribut_name": "Verstand", "wert": 4, "modifier": 0},
    "Stärke": {"attribut_name": "Stärke", "wert": 4, "modifier": 0},
    "Konstitution": {"attribut_name": "Konstitution", "wert": 4, "modifier": 0},
    "Willenskraft": {"attribut_name": "Willenskraft", "wert": 4, "modifier": 0}
}


# ============================================================
# 2. FERTIGKEITEN
# ============================================================
# Standard-SWAE (OHNE Fahren und Luftfahrt laut Conversion)
fertigkeiten_daten = {
    "Allgemeinwissen": ["Verstand"],
    "Athletik": ["Geschicklichkeit"],
    "Einschüchtern": ["Willenskraft"],
    "Elektronik": ["Verstand"],
    "Heimlichkeit": ["Geschicklichkeit"],
    "Kämpfen": ["Geschicklichkeit"],
    "Klettern": ["Stärke"],
    "Okkultismus": ["Verstand"],
    "Reparieren": ["Verstand"],
    "Reiten": ["Geschicklichkeit"],
    "Schlösser knacken": ["Geschicklichkeit"],
    "Schießen": ["Geschicklichkeit"],
    "Schwimmen": ["Geschicklichkeit"],
    "Seefahrt": ["Geschicklichkeit"],
    "Spuren lesen": ["Verstand"],
    "Überreden": ["Willenskraft"],
    "Überleben": ["Verstand"],
    "Umhören": ["Verstand"],
    "Wahrnehmung": ["Verstand"],
    "Werfen": ["Geschicklichkeit"],
    "Heilen": ["Verstand"],
    "Glücksspiel": ["Verstand"],
    "Nachforschung": ["Verstand"],
    # Hellfrost-spezifische Wissensfertigkeiten
    "Wissen (Alchemie)": ["Verstand"],
    "Wissen (Belagerungsartillerie)": ["Verstand"],
    "Wissen (Folklore)": ["Verstand"],
    "Wissen (Gegend)": ["Verstand"],
    "Wissen (Geschichte)": ["Verstand"],
    "Wissen (Handwerk)": ["Verstand"],
    "Wissen (Heraldik)": ["Verstand"],
    "Wissen (Kriegsführung)": ["Verstand"],
    "Wissen (Monster)": ["Verstand"],
    "Wissen (Rätsel)": ["Verstand"],
    "Wissen (Recht)": ["Verstand"],
    "Wissen (Religion)": ["Verstand"],
    "Wissen (Übernatürliches)": ["Verstand"],
    # Arkane Fertigkeiten (Hellfrost-spezifisch)
    "Druidenmagie": ["Verstand"],
    "Elementarmagie": ["Verstand"],
    "Heahmagie": ["Verstand"],
    "Hrimmagie": ["Verstand"],
    "Runemagie": ["Verstand"],
    "Gesangsmagie": ["Willenskraft"],
    "Glaube": ["Willenskraft"],
    # Sprache als Fertigkeit (Hellfrost-spezifisch)
    "Sprache": ["Verstand"]
}


# ============================================================
# 3. VÖLKER
# ============================================================
voelker = {
    "Engro": {
        "name": "Engro",
        "handicaps": [
            "Außenseiter (alle Rassen außer Engros)",
            "Klein (Größe -1, Robustheit -1)"
        ],
        "talente": [
            "Glück"
        ],
        "besonderheiten": [
            "Beherzt (Willenskraft W6 statt W4, Maximum W12+3)",
            "Glück (Ein zusätzlicher Bennie pro Spielsitzung)",
            "Heimlich (Heimlichkeit oder Schlösser knacken auf W6 - wählbar)",
            "Klein (90cm groß, Größe -1, Robustheit -1)"
        ],
        "sprachen": [
            "Engrosi"
        ],
        "altersspanne": "Erwachsen mit 20, Alt mit 70, maximales Alter 100",
        "groesse_maennlich": "0,80-1,20m, 25-40kg (Durchschnitt 0,90m, 32kg)",
        "groesse_weiblich": "0,80-1,20m, 22-37kg (Durchschnitt 0,90m, 30kg)",
        "aktiv": True,
        "custom": False,
        "effects": {
            "attribute_bonuses": {
                "Willenskraft": 2
            },
            "robustheit_bonus": -1,
            "bewegungsweite_bonus": 0,
            "fertigkeits_startboni": {},
            "auto_talente": [
                "Glück"
            ],
            "auto_handicaps": [
                "Außenseiter",
                "Klein"
            ],
            "spezielle_effekte": {
                "aussenseiter": True,
                "klein": True,
                "beherzt": True,
                "glueck": True
            },
            "wahlmoeglichkeiten": {
                "heimlich": {
                    "typ": "fertigkeit_oder",
                    "optionen": ["Heimlichkeit", "Schlösser knacken"],
                    "bonus": 2,
                    "beschreibung": "Beginne mit Heimlichkeit oder Schlösser knacken auf W6"
                }
            }
        }
    },
    "Frostblut": {
        "name": "Frostblut",
        "handicaps": [
            "Außenseiter (Misstrauen gegenüber Frostblütern)",
            "Hitzelethargie (bei 12°C+: -1 auf alle Eigenschaftswürfe)"
        ],
        "talente": [],
        "besonderheiten": [
            "Frostform (Innere Hrimmagie: Panzerung, Schnelligkeit, Schutz vor Kälte, Waffe verbessern - nur Selbst)",
            "Winterseele (+2 Konstitution gegen Kälte, +2 Panzerung gegen Kälte/Kaltfeuer/Eis)"
        ],
        "sprachen": [
            "Sprache der Elternrasse"
        ],
        "altersspanne": "Wie Elternrasse",
        "groesse_maennlich": "Wie Elternrasse",
        "groesse_weiblich": "Wie Elternrasse",
        "aktiv": True,
        "custom": False,
        "effects": {
            "attribute_bonuses": {},
            "robustheit_bonus": 0,
            "bewegungsweite_bonus": 0,
            "fertigkeits_startboni": {},
            "auto_talente": [],
            "auto_handicaps": [
                "Außenseiter",
                "Hitzelethargie"
            ],
            "spezielle_effekte": {
                "aussenseiter": True,
                "frostform": True,
                "hitzelethargie": True,
                "winterseele": True
            },
            "wahlmoeglichkeiten": {}
        }
    },
    "Frostzwerg": {
        "name": "Frostzwerg",
        "handicaps": [
            "Abgekapselt (-2 Überreden gegenüber anderen Rassen)",
            "Hitzelethargie (bei 12°C+: -1 auf alle Eigenschaftswürfe)",
            "Langsam (Bewegungsweite 5\")"
        ],
        "talente": [],
        "besonderheiten": [
            "Bergblut (Keine Abzüge für unsicheren Grund in Bergen/Hügeln)",
            "Nachtsicht (Ignoriert Abzüge für Düstere und Dunkle Beleuchtung)",
            "Widerstandsfähig (Konstitution W6 statt W4, Maximum W12+3)",
            "Winterseele (+2 Konstitution gegen Kälte, +2 Panzerung gegen Kälte/Kaltfeuer/Eis)"
        ],
        "sprachen": [
            "Zwergisch"
        ],
        "altersspanne": "Erwachsen mit 30, Alt mit 200, maximales Alter 300",
        "groesse_maennlich": "1,40-1,60m, 60-80kg (Durchschnitt 1,50m, 70kg)",
        "groesse_weiblich": "1,35-1,55m, 55-75kg (Durchschnitt 1,45m, 65kg)",
        "aktiv": True,
        "custom": False,
        "effects": {
            "attribute_bonuses": {
                "Konstitution": 2
            },
            "robustheit_bonus": 0,
            "bewegungsweite_bonus": -1,
            "fertigkeits_startboni": {},
            "auto_talente": [
                "Nachtsicht"
            ],
            "auto_handicaps": [
                "Abgekapselt",
                "Hitzelethargie"
            ],
            "spezielle_effekte": {
                "abgekapselt": True,
                "bergblut": True,
                "hitzelethargie": True,
                "nachtsicht": True,
                "langsam": True,
                "winterseele": True
            },
            "wahlmoeglichkeiten": {}
        }
    },
    "Herdelf": {
        "name": "Herdelf",
        "handicaps": [
            "Zwei linke Hände (Abneigung gegen mechanische Gegenstände inkl. Armbrüste)"
        ],
        "talente": [],
        "besonderheiten": [
            "Geschickt (Geschicklichkeit W6 statt W4, Maximum W12+3)",
            "Nachtsicht (Ignoriert Abzüge für Düstere und Dunkle Beleuchtung)",
            "Natürliche Umgebung (Druiden behandeln Elfenheime als Wildnis)",
            "Waldblut (Keine Abzüge für unsicheren Grund in Wäldern)"
        ],
        "sprachen": [
            "Herdelfisch"
        ],
        "altersspanne": "Erwachsen mit 115, Alt mit 350, maximales Alter 500",
        "groesse_maennlich": "1,65-2,05m, 52-72kg (Durchschnitt 1,85m, 58kg)",
        "groesse_weiblich": "1,65-1,95m, 44-57kg (Durchschnitt 1,85m, 53kg)",
        "aktiv": True,
        "custom": False,
        "effects": {
            "attribute_bonuses": {
                "Geschicklichkeit": 2
            },
            "robustheit_bonus": 0,
            "bewegungsweite_bonus": 0,
            "fertigkeits_startboni": {},
            "auto_talente": [
                "Nachtsicht"
            ],
            "auto_handicaps": [
                "Zwei linke Hände"
            ],
            "spezielle_effekte": {
                "nachtsicht": True,
                "natuerliche_umgebung": True,
                "waldblut": True,
                "zwei_linke_haende": True
            },
            "wahlmoeglichkeiten": {}
        }
    },
    "Mensch_Anari": {
        "name": "Mensch (Anari)",
        "handicaps": [],
        "talente": [],
        "besonderheiten": [
            "Vielseitig (Ein freies Talent oder 2 zusätzliche Fertigkeitspunkte)"
        ],
        "sprachen": [
            "Anari"
        ],
        "altersspanne": "Erwachsen mit 18, Alt mit 60, maximales Alter 80",
        "groesse_maennlich": "1,65-1,85m, 65-85kg (Durchschnitt 1,75m, 75kg)",
        "groesse_weiblich": "1,55-1,75m, 50-70kg (Durchschnitt 1,65m, 60kg)",
        "aktiv": True,
        "custom": False,
        "effects": {
            "attribute_bonuses": {},
            "robustheit_bonus": 0,
            "bewegungsweite_bonus": 0,
            "fertigkeits_startboni": {},
            "auto_talente": [],
            "spezielle_effekte": {
                "vielseitig": True
            },
            "wahlmoeglichkeiten": {
                "freies_talent_oder_fertigkeitspunkte": True
            }
        }
    },
    "Mensch_Saxa": {
        "name": "Mensch (Saxa)",
        "handicaps": [],
        "talente": [],
        "besonderheiten": [
            "Vielseitig (Ein freies Talent oder 2 zusätzliche Fertigkeitspunkte)"
        ],
        "sprachen": [
            "Saxa"
        ],
        "altersspanne": "Erwachsen mit 18, Alt mit 60, maximales Alter 80",
        "groesse_maennlich": "1,70-1,90m, 70-90kg (Durchschnitt 1,80m, 80kg)",
        "groesse_weiblich": "1,60-1,80m, 55-75kg (Durchschnitt 1,70m, 65kg)",
        "aktiv": True,
        "custom": False,
        "effects": {
            "attribute_bonuses": {},
            "robustheit_bonus": 0,
            "bewegungsweite_bonus": 0,
            "fertigkeits_startboni": {},
            "auto_talente": [],
            "spezielle_effekte": {
                "vielseitig": True
            },
            "wahlmoeglichkeiten": {
                "freies_talent_oder_fertigkeitspunkte": True
            }
        }
    },
    "Mensch_Finnar": {
        "name": "Mensch (Finnar)",
        "handicaps": [],
        "talente": [],
        "besonderheiten": [
            "Vielseitig (Ein freies Talent oder 2 zusätzliche Fertigkeitspunkte)"
        ],
        "sprachen": [
            "Finnari"
        ],
        "altersspanne": "Erwachsen mit 18, Alt mit 60, maximales Alter 80",
        "groesse_maennlich": "1,55-1,75m, 55-70kg (Durchschnitt 1,65m, 63kg)",
        "groesse_weiblich": "1,45-1,65m, 45-60kg (Durchschnitt 1,55m, 53kg)",
        "aktiv": True,
        "custom": False,
        "effects": {
            "attribute_bonuses": {},
            "robustheit_bonus": 0,
            "bewegungsweite_bonus": 0,
            "fertigkeits_startboni": {},
            "auto_talente": [],
            "spezielle_effekte": {
                "vielseitig": True
            },
            "wahlmoeglichkeiten": {
                "freies_talent_oder_fertigkeitspunkte": True
            }
        }
    },
    "Mensch_Tuomi": {
        "name": "Mensch (Tuomi)",
        "handicaps": [],
        "talente": [],
        "besonderheiten": [
            "Vielseitig (Ein freies Talent oder 2 zusätzliche Fertigkeitspunkte)"
        ],
        "sprachen": [
            "Tuomi"
        ],
        "altersspanne": "Erwachsen mit 18, Alt mit 60, maximales Alter 80",
        "groesse_maennlich": "1,50-1,70m, 55-70kg (Durchschnitt 1,60m, 63kg)",
        "groesse_weiblich": "1,40-1,60m, 45-60kg (Durchschnitt 1,50m, 53kg)",
        "aktiv": True,
        "custom": False,
        "effects": {
            "attribute_bonuses": {},
            "robustheit_bonus": 0,
            "bewegungsweite_bonus": 0,
            "fertigkeits_startboni": {},
            "auto_talente": [],
            "spezielle_effekte": {
                "vielseitig": True
            },
            "wahlmoeglichkeiten": {
                "freies_talent_oder_fertigkeitspunkte": True
            }
        }
    },
    "Taigaelf": {
        "name": "Taigaelf",
        "handicaps": [
            "Abgekapselt (-2 Überreden gegenüber anderen Rassen)",
            "Hitzelethargie (bei 12°C+: -1 auf alle Eigenschaftswürfe)",
            "Zwei linke Hände (Abneigung gegen mechanische Gegenstände inkl. Armbrüste)"
        ],
        "talente": [],
        "besonderheiten": [
            "Geschickt (Geschicklichkeit W6 statt W4, Maximum W12+3)",
            "Nachtsicht (Ignoriert Abzüge für Düstere und Dunkle Beleuchtung)",
            "Natürliche Umgebung (Druiden behandeln Elfenheime als Wildnis)",
            "Waldblut (Keine Abzüge für unsicheren Grund in Wäldern)",
            "Winterseele (+2 Konstitution gegen Kälte, +2 Panzerung gegen Kälte/Kaltfeuer/Eis)"
        ],
        "sprachen": [
            "Taigaelfisch"
        ],
        "altersspanne": "Erwachsen mit 115, Alt mit 350, maximales Alter 500",
        "groesse_maennlich": "1,65-2,05m, 52-72kg (Durchschnitt 1,85m, 58kg)",
        "groesse_weiblich": "1,65-1,95m, 44-57kg (Durchschnitt 1,85m, 53kg)",
        "aktiv": True,
        "custom": False,
        "effects": {
            "attribute_bonuses": {
                "Geschicklichkeit": 2
            },
            "robustheit_bonus": 0,
            "bewegungsweite_bonus": 0,
            "fertigkeits_startboni": {},
            "auto_talente": [
                "Nachtsicht"
            ],
            "auto_handicaps": [
                "Abgekapselt",
                "Hitzelethargie",
                "Zwei linke Hände"
            ],
            "spezielle_effekte": {
                "abgekapselt": True,
                "geschickt": True,
                "hitzelethargie": True,
                "nachtsicht": True,
                "natuerliche_umgebung": True,
                "waldblut": True,
                "winterseele": True,
                "zwei_linke_haende": True
            },
            "wahlmoeglichkeiten": {}
        }
    }
}


# ============================================================
# 4. HANDICAPS - aus FK übernehmen + Hellfrost-spezifische
# ============================================================
handicaps = {}

# Standard-Handicaps aus FK übernehmen (Duplikate filtern)
# FK hat sowohl z.B. "Angetrieben" als auch "Angetrieben_leicht" mit identischem Inhalt.
# Wir behalten nur die _leicht/_schwer-Suffix-Versionen.
_duplikat_bare_keys = {
    "Angetrieben", "Angewohnheit", "Feind", "Gesucht", "Gierig",
    "Langsam", "Pazifist", "Phobie", "Rachsüchtig", "Schwerhörig", "Schwur"
}
for key, h in fk.get("handicaps", {}).items():
    if key in _duplikat_bare_keys:
        continue  # Bare-Name-Duplikat überspringen
    handicaps[key] = copy.deepcopy(h)

# Hellfrost-spezifische Handicaps hinzufügen
hellfrost_handicaps = {
    "Befehle_leicht": {
        "name": "Befehle",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "Der Charakter dient einer anderen Macht und muss Befehle ausführen, wenn sie erteilt werden. Zum Beispiel ein Agent eines Adeligen, ein Soldat der Eisengilde oder ein Söldner unter Vertrag.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False
    },
    "Gottverlassen_schwer": {
        "name": "Gottverlassen",
        "stufe": "schwer",
        "punkte": 2,
        "beschreibung": "Die vergangenen Taten des Helden haben einen der Götter erzürnt. Nutzbringende Zaubersprüche von Klerikern dieses Gottes schlagen automatisch fehl. Schädliche Zauber verursachen +2 Schaden. Kleriker erhalten +2 auf Vergleichende Würfe gegen den Helden. Arkane Resistenz schützt nicht.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False
    },
    "Kaltblüter_leicht": {
        "name": "Kaltblüter",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "Der Held erhält einen Abzug von -2 auf Konstitutionswürfe, um den Auswirkungen von kaltem Wetter zu widerstehen.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False
    },
    "Lehrling_leicht": {
        "name": "Lehrling",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "Erfordert Arkanen Hintergrund. Der Charakter darf das Spiel nicht mit einer arkanen Fertigkeit über W6 beginnen.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False
    },
    "Novize_schwer": {
        "name": "Novize",
        "stufe": "schwer",
        "punkte": 2,
        "beschreibung": "Erfordert Arkanen Hintergrund. Wie Lehrling, aber der Charakter beginnt zudem mit einer Macht weniger. Runenmagier beginnen dennoch mit einer Rune, dürfen aber nicht mit einer arkanen Fertigkeit über W4 beginnen.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False
    },
    "Magisches_Verbot_schwer": {
        "name": "Magisches Verbot",
        "stufe": "schwer",
        "punkte": 2,
        "beschreibung": "Der Held hat keine Verbindung zu den magischen Energien der Welt. Er kann keine Relikte erkennen, keine Bennies für ihre Aktivierung ausgeben, profitiert nicht von Tränken, kann keine Schriftrollen lesen und keinen Arkanen Hintergrund wählen. Kräutertränke funktionieren normal.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False
    },
    "Nekromantische_Schwäche_leicht": {
        "name": "Nekromantische Schwäche",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "Der Charakter erhält einen Abzug von -2 auf Eigenschaftswürfe, um den übernatürlichen Angriffen von Untoten zu widerstehen.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False
    },
    "Nekromantische_Schwäche_schwer": {
        "name": "Nekromantische Schwäche",
        "stufe": "schwer",
        "punkte": 2,
        "beschreibung": "Der Charakter erhält einen Abzug von -4 auf Eigenschaftswürfe, um den übernatürlichen Angriffen von Untoten zu widerstehen. Hat keinen Effekt auf weltlichen Schaden von Untoten.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False
    },
    "Schwarzes_Schaf_leicht": {
        "name": "Schwarzes Schaf",
        "stufe": "leicht",
        "punkte": 1,
        "beschreibung": "Nur für Helden aus der Magokratie. Der Held lehnt die Heahmagier ab und wurde von seiner Familie verstoßen. Kann kein Land oder Titel erben, -2 Überreden gegenüber Heahmagiern. Kann nicht Adelig, Arkaner Hintergrund (Heahmagier) oder Reich wählen.",
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False
    }
}
handicaps.update(hellfrost_handicaps)


# ============================================================
# 5. TALENTE - aus FK übernehmen + Hellfrost-spezifische
# ============================================================
talente = {}

# Standard-Talente aus FK übernehmen
for key, t in fk.get("talente", {}).items():
    talente[key] = copy.deepcopy(t)

# Verbotene Talente deaktivieren (laut Conversion)
verbotene_talente = [
    "Arkaner Hintergrund (Psionik)",
    "Arkaner Hintergrund (Superkräfte)",
    "Arkaner Hintergrund (Verrückte Wissenschaft)",
    "Ass",
    "Kampfsinn",
    "Machtpunkte",
    "Schnelle Machtregeneration",
    "Seelenopfer",
    "Zauberer",
    "Mutig",
    "Elan",
    "Kampfkünstler"
]

for key, t in talente.items():
    if t.get("name") in verbotene_talente:
        t["aktiv"] = False

# FK-Arkane Hintergründe deaktivieren (Hellfrost hat eigene)
fk_arkane_hintergruende = [
    "Arkaner Hintergrund (Alchemist)",
    "Arkaner Hintergrund (Barde)",
    "Arkaner Hintergrund (Begabt)",
    "Arkaner Hintergrund (Beschwörer)",
    "Arkaner Hintergrund (Diabolist)",
    "Arkaner Hintergrund (Druide)",
    "Arkaner Hintergrund (Elementarist)",
    "Arkaner Hintergrund (Hexe)",
    "Arkaner Hintergrund (Hexer)",
    "Arkaner Hintergrund (Hexer/Hexe)",
    "Arkaner Hintergrund (Illusionist)",
    "Arkaner Hintergrund (Kleriker)",
    "Arkaner Hintergrund (Klerus)",
    "Arkaner Hintergrund (Magier)",
    "Arkaner Hintergrund (Nekromant)",
    "Arkaner Hintergrund (Schamane)",
    "Arkaner Hintergrund (Tüftler)",
    "Arkaner Hintergrund (Wahrsager)",
    "Arkaner Hintergrund (Zauberer)",
]

for key, t in talente.items():
    if t.get("name") in fk_arkane_hintergruende:
        t["aktiv"] = False

# FK-Kategorie-spezifische Talente deaktivieren (gehören zu FK-Arkanen Hintergründen)
fk_kategorien = [
    "Alchemist", "Barde", "Begabt", "Beschwörer", "Diabolist",
    "Druide", "Elementarist", "Hexe", "Hexer", "Hexer/Hexe",
    "Illusionist", "Kleriker", "Klerus", "Nekromant", "Schamane",
    "Tüftler", "Wahrsager"
]

for key, t in talente.items():
    if t.get("kategorie") in fk_kategorien:
        t["aktiv"] = False


# Hellfrost-spezifische Talente hinzufügen
hellfrost_talente = {
    # ---- Arkane Hintergründe (Hellfrost) ----
    "Arkaner Hintergrund (Druidentum)": {
        "name": "Arkaner Hintergrund (Druidentum)",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Herd- oder Taigaelf oder Engro"],
        "beschreibung": "Arkane Fertigkeit: Druidenmagie (Verstand). Startmächte: 3. Druiden ziehen an den Fäden der Naturmagie und manipulieren Pflanzen und Tiere. In Wildnis +1 auf Druidenmagie, in Städten -1.",
        "neue_maechte": 3,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Arkaner Hintergrund (Elementarmagie)": {
        "name": "Arkaner Hintergrund (Elementarmagie)",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": [],
        "beschreibung": "Arkane Fertigkeit: Elementarmagie (Verstand). Startmächte: 3. Der Elementarist beginnt mit einem Element (Erde, Feuer, Luft oder Wasser) und kann weitere durch das Talent Meister der Elemente meistern.",
        "neue_maechte": 3,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Arkaner Hintergrund (Heahmagie)": {
        "name": "Arkaner Hintergrund (Heahmagie)",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Mensch (Anari)"],
        "beschreibung": "Arkane Fertigkeit: Heahmagie (Verstand). Startmächte: 3. Heahmagier schöpfen ihre Macht durch magische Stäbe. Ohne Stab -2 auf alle Heahmagiewürfe. Der Stab verursacht Stä+W4 Schaden.",
        "neue_maechte": 3,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Arkaner Hintergrund (Hrimmagie)": {
        "name": "Arkaner Hintergrund (Hrimmagie)",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": [],
        "beschreibung": "Arkane Fertigkeit: Hrimmagie (Verstand). Startmächte: 3. Hrimmagier ziehen ihre Kraft aus Eis und Schnee. Alle Zauber haben Kälte/Eis-Ausprägung. Helfrosteffekt beeinflusst Feuerzauber anderer, stärkt aber Hrimmagier.",
        "neue_maechte": 3,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Arkaner Hintergrund (Runenmagie)": {
        "name": "Arkaner Hintergrund (Runenmagie)",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Frostzwerg"],
        "beschreibung": "Runenmagier ritzen Runen der Macht auf Steintafeln. Jede Rune hat eine eigene arkane Fertigkeit und ist mit drei Zaubersprüchen verknüpft. Beginnt mit einer Rune.",
        "neue_maechte": 3,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Arkaner Hintergrund (Gesangsmagie)": {
        "name": "Arkaner Hintergrund (Gesangsmagie)",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": [],
        "beschreibung": "Arkane Fertigkeit: Gesangsmagie (Willenskraft). Startmächte: 3. Skalden bündeln magische Fäden durch die Kraft ihres Gesangs. Behindernde Rüstung: -1 auf Gesangsmagie in Metallrüstung.",
        "neue_maechte": 3,
        "machtpunkte": 0,
        "auto_handicaps": ["Behindernde_Rüstung_leicht"],
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Arkaner Hintergrund (Wunder)": {
        "name": "Arkaner Hintergrund (Wunder)",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": [],
        "beschreibung": "Arkane Fertigkeit: Glaube (Willenskraft). Startmächte: 3. Priester und Paladine erhalten Wunder von ihrem Schutzgott. Erhält automatisch das Talent Beziehungen und das Handicap Befehle für den Glauben.",
        "neue_maechte": 3,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },

    # ---- Anführertalente (Hellfrost) ----
    "Durchbrecht die Mauer!": {
        "name": "Durchbrecht die Mauer!",
        "kategorie": "Anführer",
        "rang": "F",
        "voraussetzungen": ["Verstand W8+", "Wissen (Kriegsführung) W8+"],
        "beschreibung": "Massenschlacht: Reduziert den Belagerungsbonus gegnerischer Befestigungen um 1. Mit Wissensprobe (Kriegsführung) auf -2 (Erfolg) oder -3 (Steigerung).",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Ehre oder Tod": {
        "name": "Ehre oder Tod",
        "kategorie": "Anführer",
        "rang": "V",
        "voraussetzungen": ["Anführen", "Haltet die Stellung!", "Willenskraft W8+", "Wissen (Kriegsführung) W8+"],
        "beschreibung": "Massenschlacht: +2 auf Willenskraftwürfe für Moral in Massenschlachten.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Eine Frage der Ehre": {
        "name": "Eine Frage der Ehre",
        "kategorie": "Anführer",
        "rang": "H",
        "voraussetzungen": ["Anführen", "Inspirieren", "Verstand W8+", "Wissen (Kriegsführung) W10+"],
        "beschreibung": "Massenschlacht: Fügt der eigenen Armee einen zusätzlichen Marker hinzu.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Fanatismus": {
        "name": "Fanatismus",
        "kategorie": "Anführer",
        "rang": "F",
        "voraussetzungen": ["Anführen", "Anheizen"],
        "beschreibung": "Truppen unter dem Kommando erhalten +2 auf Willenskraftwürfe gegen Furcht und ziehen -2 von Würfen auf der Furchttabelle ab.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Haltet die Mauer!": {
        "name": "Haltet die Mauer!",
        "kategorie": "Anführer",
        "rang": "F",
        "voraussetzungen": ["Verstand W8+", "Wissen (Kriegsführung) W8+"],
        "beschreibung": "Massenschlacht: Erhöht den Belagerungsbonus verteidigter Befestigungen um +1. Mit Wissensprobe (Kriegsführung) auf +2 (Erfolg) oder +3 (Steigerung).",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Keine Gefangenen!": {
        "name": "Keine Gefangenen!",
        "kategorie": "Anführer",
        "rang": "V",
        "voraussetzungen": ["Anführen", "Anheizen", "Willenskraft W8+", "Wissen (Kriegsführung) W10+"],
        "beschreibung": "Massenschlacht: Einmal pro Kampf kann ein Sturmangriff angesagt werden. Bei Erfolg verliert der Gegner einen zusätzlichen Marker.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Koordinierte Feuerkraft": {
        "name": "Koordinierte Feuerkraft",
        "kategorie": "Anführer",
        "rang": "V",
        "voraussetzungen": ["Anführen", "Verstand W6+", "Schießen W8+", "Werfen W8+"],
        "beschreibung": "Fernkampfeinheiten in Befehlsreichweite feuern als Einheit. +2 pro Schütze auf Angriffswurf des Helden. Pro Steigerung +1W6 Bonusschaden.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Taktiker": {
        "name": "Taktiker",
        "kategorie": "Anführer",
        "rang": "F",
        "voraussetzungen": ["Wildcard", "Anführen", "Verstand W8+", "Wissen (Kriegsführung) W6+"],
        "beschreibung": "Zu Beginn eines Kampfes Wissensprobe (Kriegsführung): Pro Erfolg und Steigerung eine zusätzliche Initiativekarte, die an Verbündete verteilt werden kann.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },

    # ---- Expertentalente (Hellfrost-Organisationen) ----
    "Bewahrer des Wissens": {
        "name": "Bewahrer des Wissens",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Verstand W8+", "Nachforschung W6+", "nicht Analphabet"],
        "beschreibung": "Trägt Schriftrollen (5 Pfund). Ungeübte Verstand-Fertigkeiten werden mit W4 statt W4-2 abgelegt, wenn eine Runde studiert wird. Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Gildendieb": {
        "name": "Gildendieb",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Dieb", "Sprache Fingersprech"],
        "beschreibung": "+2 auf Umhörenproben im Heimatland. Wildcard-Würfel W8 für Heimlichkeit, Klettern oder Schlösser knacken (wähle eine). Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Gnadensschwester": {
        "name": "Gnadensschwester",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Heilen W8+", "Handicap Pazifist", "weiblich"],
        "beschreibung": "+2 auf Heilenwürfe, +1 Überreden. Kann ab Veteran das Talent Mitstreiter erwerben. Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Grauer Legionär": {
        "name": "Grauer Legionär",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Willenskraft W8+", "Kämpfen W8+", "Schießen oder Werfen W6+", "keine Familie/Verantwortung"],
        "beschreibung": "Immun gegen Einschüchterung und Furcht. Kann sich keiner anderen Organisation anschließen. Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Herdritter": {
        "name": "Herdritter",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Konstitution W8+", "Willenskraft W8+", "Kämpfen W6+", "Reiten W6+", "Überleben W8+"],
        "beschreibung": "+1 Parade und +2 auf Angriffe mit Angesagtem Ziel gegen Monster mit Immunität/Resistenz (Kälte). +2 auf Überlebenwürfe bei Temperaturen unter dem Gefrierpunkt. Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Klingentänzer": {
        "name": "Klingentänzer",
        "kategorie": "Kampf",
        "rang": "A",
        "voraussetzungen": ["Herd- oder Taigaelf", "Beidhändiger Kampf", "Geschicklichkeit W8+", "Kämpfen W8+"],
        "beschreibung": "Sprintenwurf auf Bewegungsweite addieren und sich mindestens so weit bewegen. Jedes angrenzende Ziel wird mit -2 angegriffen. Jedes Ziel auf dem Weg muss angegriffen werden.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Prügler": {
        "name": "Prügler",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Engro", "Stärke W6+", "Willenskraft W8+", "Einschüchtern W6+", "Schießen W8+"],
        "beschreibung": "Reichweite der Schleuder +1 pro Rang. Stä+W6 Schaden auf kurze Reichweite. +1 Überreden gegenüber Engros. Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Rabenritter": {
        "name": "Rabenritter",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Anführen", "ein weiteres Anführertalent", "Verstand W6+", "Willenskraft W6+", "Wissen (Kriegsführung) W8+"],
        "beschreibung": "+1\" Befehlsreichweite pro Rang. +1 auf Wissen (Kriegsführung). Kann Rangvoraussetzungen von Anführertalenten ignorieren. Anführertalente gelten auch für WildCards. Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Reliquiar (Arkanologe)": {
        "name": "Reliquiar (Arkanologe)",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Verstand W8+", "Wahrnehmung W6+", "Wissen (Übernatürliches) W8+"],
        "beschreibung": "Kann Relikte mit Wissensprobe (Übernatürliches) identifizieren. +2 auf Allgemeinwissen- und Wissenswürfe bezüglich Relikten. Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Reliquiar (Reliquius)": {
        "name": "Reliquiar (Reliquius)",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Geschicklichkeit W8+", "Schlösser knacken W6+", "Wahrnehmung W6+"],
        "beschreibung": "+2 auf Wahrnehmung beim Suchen nach Fallen/Geheimtüren. +2 auf Entschärfenwürfe. Wird nie von Fallen überrascht. Kann Geschicklichkeitsprobe -2 ablegen um Fallen auszuweichen. Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Söldner der Eisengilde": {
        "name": "Söldner der Eisengilde",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Stärke W8+", "Willenskraft W6+", "Kämpfen W6+"],
        "beschreibung": "Überzahlbonus +1 höher (maximal +5). Beginnt mit Kettenhemd, Langschwert und mittlerem Schild (Leihgabe). Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Waldhüter": {
        "name": "Waldhüter",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Schießen W8+", "Arkaner Hintergrund (Druidentum) oder Naturbursche"],
        "beschreibung": "Kann mit weltlichen Tieren sprechen. Erhält die Macht Tierfreund (Verstand als arkane Fertigkeit für Nicht-Druiden). Druiden erhalten +2 auf Tierfreund. Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Weghüter": {
        "name": "Weghüter",
        "kategorie": "Experte",
        "rang": "A",
        "voraussetzungen": ["Konstitution W6+", "Kämpfen W8+", "Reiten W6+", "Spuren lesen W6+", "Überleben W6+"],
        "beschreibung": "+2 auf Überlebens- und Spuren-lesen-Würfe. +2 auf Wahrnehmung für Hinterhalte, Fallen und verborgene Waffen (nicht in urbaner Umgebung). Erhält Beziehungen und Handicap Befehle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },

    # ---- Hintergrundtalente (Hellfrost) ----
    "Adelig (Hellfrost)": {
        "name": "Adelig",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": [],
        "beschreibung": "Der Charakter ist von adeligem Geblüt. +2 Überreden, +2 Geld. Magokratie-Adelige benötigen Arkaner Hintergrund (Heahmagier).",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Alte Familie": {
        "name": "Alte Familie",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Arkaner Hintergrund (Heahmagie)"],
        "beschreibung": "+2 auf Wissenswürfe (Übernatürliches). Beginnt als Magier-Baron.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Bücherei": {
        "name": "Bücherei",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Reich oder Bewahrer des Wissens", "nicht Analphabet"],
        "beschreibung": "Besitzt Wissensbände. Erhält Punkte gleich halbem Verstandwürfel, verteilt auf Bände (max +3 pro Band), die Boni auf Wissensfertigkeiten geben.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Kräutermagie": {
        "name": "Kräutermagie",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Verstand W8+", "Überleben W6+", "Wissen (Alchemie) W6+"],
        "beschreibung": "Der Held kann Kräuter identifizieren und Heilmittel brauen.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Heiliger Krieger": {
        "name": "Heiliger Krieger",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Willenskraft W8+", "Glaube W6+"],
        "beschreibung": "Priester können übernatürlich böse Kreaturen (Untote, Dämonen) vertreiben. Reichweite gleich Willenskraftwürfel in Zoll. Vergleichender Willenskraftwurf gegen Glauben.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Linguist (Hellfrost)": {
        "name": "Linguist",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Verstand W6+", "nicht Analphabet"],
        "beschreibung": "Beherrscht eine Zahl von Sprachen gleich dem Verstandwürfel.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Styrimathr": {
        "name": "Styrimathr",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Seefahrt W8+"],
        "beschreibung": "Besitzt ein Smabyrding (kleines Schiff ohne Eisrigg). Keine Besatzung inklusive.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Vom Tod berührt": {
        "name": "Vom Tod berührt",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Konstitution W6+", "Willenskraft W8+"],
        "beschreibung": "+2 auf Widerstehen von nekromantischen Zaubern und übernatürlichen Merkmalen von Untoten.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Warmblüter": {
        "name": "Warmblüter",
        "kategorie": "Hintergrund",
        "rang": "A",
        "voraussetzungen": ["Engro, Herdelf oder Mensch", "Konstitution W8+"],
        "beschreibung": "+2 auf Konstitutionswürfe, um den Auswirkungen von kaltem Wetter zu widerstehen.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },

    # ---- Jüngertalente ----
    "Jünger Dargars": {
        "name": "Jünger Dargars",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Stärke W8+", "Einschüchtern W8+", "Glaube W8+", "Kämpfen W8+", "Anhänger Dargars"],
        "beschreibung": "Wenn ein Statist mit einem Schlag Außer Gefecht gesetzt wird, müssen benachbarte Verbündete des Opfers Willenskraftprobe bestehen oder sind Angeschlagen. Kann Kriegsschrei ohne Rassenbeschränkung erlernen.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Eiras": {
        "name": "Jünger Eiras",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Willenskraft W8+", "Glaube W8+", "Heilen W6+", "Anhänger Eiras"],
        "beschreibung": "+2 auf alle Heilenwürfe (natürlich und magisch). Bis zu 5 Gefährten profitieren vom Bonus auf natürliche Heilungswürfe.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Eostres (Pflanzenmutter)": {
        "name": "Jünger Eostres (Pflanzenmutter)",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Geschicklichkeit W8+", "Konstitution W8+", "Willenskraft W8+", "Glaube W8+", "Anhänger Eostres"],
        "beschreibung": "Keine Abzüge bei Bewegung in natürlichem schwierigem Gelände (Vegetation). +1 auf Glaubenswürfe in starker Vegetation. Vorteile von Auserwählter und Heiliger Krieger gegen Pflanzenwesen.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Eostres (Tiermutter)": {
        "name": "Jünger Eostres (Tiermutter)",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Tierempathie", "Willenskraft W8+", "Glaube W8+", "Anhänger Eostres"],
        "beschreibung": "Vorteile des Talents Tiermeister, aber der Tiergefährte ist eine Wildcard und sammelt Erfahrungspunkte.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Erthas": {
        "name": "Jünger Erthas",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Konstitution W8+", "Klettern W6+", "Glaube W8+", "Überleben W6+", "Anhänger Erthas"],
        "beschreibung": "+1 auf Robustheit. +2 auf Überlebenswürfe unter der Erde.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Freos": {
        "name": "Jünger Freos",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Geschicklichkeit W8+", "Konstitution W8+", "Glaube W8+", "Anhänger Freos"],
        "beschreibung": "Jegliches Terrain eine Kategorie niedriger (Überlandreise). Im taktischen Kampf ist jegliches Terrain normaler Untergrund.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Helas": {
        "name": "Jünger Helas",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Willenskraft W8+", "Glaube W8+", "Anhänger Helas"],
        "beschreibung": "+1 auf Glaubenswürfe in Grabstätten und Todesorten. Bei zwei Steigerungen auf Zombie/Mächtige Untote sind diese permanent.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Hoenirs": {
        "name": "Jünger Hoenirs",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Gelehrter", "Verstand W10+", "Glaube W8+", "Anhänger Hoenirs"],
        "beschreibung": "+1 auf alle Wissens- und Allgemeinwissenswürfe (außer Gelehrter-Fertigkeiten). Kann ungeübte Wissensfertigkeiten mit W4-2 ablegen.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Hothars": {
        "name": "Jünger Hothars",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Ermittler", "Verstand W8+", "Glaube W8+", "Wahrnehmung W6+", "Anhänger Hothars"],
        "beschreibung": "+2 auf Widerstandswürfe gegen geistige Beeinflussung (inkl. Willensduell, Marionette, Verwirrung). Kumulativ mit Eiserner Wille.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Kenaz'": {
        "name": "Jünger Kenaz'",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Konstitution W8+", "Glaube W8+", "Anhänger Kenaz'"],
        "beschreibung": "+2 auf Konstitution gegen Hitze, +4 Panzerung gegen Feuer/Hitze-Schaden. Metallwaffen können mit magischer Hitze erhitzt werden: +2/+4 Schaden gegen Kreaturen mit Resistenz/Immunität (Kälte).",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Maeras": {
        "name": "Jünger Maeras",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Verstand W8+", "Willenskraft W6+", "Glaube W8+", "Anhänger Maeras"],
        "beschreibung": "Kann jeden Zauberspruch erlernen (mit -2 auf Glauben). +2 auf Glaubenswurf bei Bann.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Nauthiz'": {
        "name": "Jünger Nauthiz'",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Dieb", "Geschicklichkeit W10+", "Glaube W8+", "Glücksspiel W8+", "Anhänger Nauthiz'"],
        "beschreibung": "Bei einer 1 auf Glücksspiel-, Heimlichkeits- oder Schlösser-knacken-Würfel kann automatisch wiederholt werden. Bei erneutem Fehlschlag: 24h Erschöpfungsstufe.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Neorthes": {
        "name": "Jünger Neorthes",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Konstitution W8+", "Glaube W6+", "Schwimmen W6+", "Seefahrt W6+", "Anhänger Neorthes"],
        "beschreibung": "Halbierter täglicher Wasserbedarf. Konstitutionsprobe bei Dehydrierung nur alle 12h statt 6h. Kann Runden gleich Konstitutionswürfel beim Ertrinken überleben.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Nihts": {
        "name": "Jünger Nihts",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Verstand W6+", "Glaube W8+", "Heimlichkeit W8+", "Wahrnehmung W8+", "Anhänger Nihts"],
        "beschreibung": "Ignoriert Abzüge für düstere und dunkle Beleuchtung. Nur -2 bei totaler Dunkelheit (auch magischer).",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger der Nornen": {
        "name": "Jünger der Nornen",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Verstand W8+", "Glaube W8+", "Anhänger der Nornen"],
        "beschreibung": "Kann Weissagungen treffen. Beteiligte Helden geben je einen Bennie aus. Eine Karte wird gezogen und liefert Boni oder Abzüge bis Abentuerende.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Rigrs": {
        "name": "Jünger Rigrs",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Aufmerksamkeit", "Konstitution W8+", "Glaube W8+", "Wahrnehmung W8+", "Anhänger Rigrs"],
        "beschreibung": "Benötigt nur 3 Stunden Schlaf. Nur -1 Konstitutionsabzug bei Schlafentzug statt -2. Gilt im Schlaf als aktive Wache.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Scaethas": {
        "name": "Jünger Scaethas",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Willenskraft W8+", "Glaube W8+", "Kämpfen W8+", "Anhänger Scaethas"],
        "beschreibung": "Vorteile von Auserwählter und Heiliger Krieger gegen Untote. +2 auf Glaube-Widerstandswürfe gegen nekromantische Zauber.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Sigels": {
        "name": "Jünger Sigels",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Konstitution W8+", "Willenskraft W8+", "Glaube W8+", "Anhänger Sigels"],
        "beschreibung": "Kälte-, Kaltfeuer- und Eisangriffe verursachen halben Schaden. +2 auf Konstitution gegen Kälte.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Thunors": {
        "name": "Jünger Thunors",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Konstitution W8+", "Glaube W8+", "Anhänger Thunors"],
        "beschreibung": "+2 auf Konstitution bei Wind und Regen, +2 Panzerung gegen Blitz/Elektrizitätsschaden. Seefahrer erhalten +1 auf Seefahrt bei Sturm.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Tiws": {
        "name": "Jünger Tiws",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Konstitution W8+", "Stärke W8+", "Glaube W8+", "Kämpfen W10+", "Anhänger Tiws"],
        "beschreibung": "Gilt als einen Rang höher für Voraussetzungen von Kampftalenten.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Valis": {
        "name": "Jünger Valis",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Konstitution W6+", "Glaube W8+", "Anhänger Valis"],
        "beschreibung": "Immun gegen jegliche Art von Krankheit und Gift (magisch und weltlich). Kann Krankheitsträger sein.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Jünger Vars": {
        "name": "Jünger Vars",
        "kategorie": "Jünger",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Wunder)", "Glaube W8+", "Überreden W8+", "Umhören W8+", "Anhänger Vars"],
        "beschreibung": "Umhörenprobe zum Verkaufen: Erfolg = 50%, Steigerung = 75% des Preises. Probe alle 4 Tage statt 1x/Woche. +1 Überreden.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },

    # ---- Kampftalente (Hellfrost) ----
    "Blut und Eingeweide": {
        "name": "Blut und Eingeweide",
        "kategorie": "Kampf",
        "rang": "V",
        "voraussetzungen": ["Kämpfen, Schießen oder Werfen W10+"],
        "beschreibung": "Massenschlacht: Halbiert (abgerundet) die negative Marker-Differenz für Angriffswürfe.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Erzfeind": {
        "name": "Erzfeind",
        "kategorie": "Kampf",
        "rang": "F",
        "voraussetzungen": ["Verstand W8+", "Kämpfen, Schießen oder Werfen W8+"],
        "beschreibung": "Wähle eine Kreaturenart. +1 Parade gegen Erzfeinde, W8 statt W6 Bonusschaden bei Steigerung. Kann mehrfach gewählt werden.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Kriegsschrei": {
        "name": "Kriegsschrei",
        "kategorie": "Kampf",
        "rang": "F",
        "voraussetzungen": ["Frostzwerg oder Saxa", "Einschüchtern W8+"],
        "beschreibung": "Einschüchternwurf gegen alle Gegner auf einmal (Große Schablone). Jede Kreatur unter der Schablone muss Willenskraftwurf bestehen.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Mächtiger Schuss": {
        "name": "Mächtiger Schuss",
        "kategorie": "Kampf",
        "rang": "V",
        "voraussetzungen": ["Stärke W8+", "Schießen W10+"],
        "beschreibung": "Bogen verursacht Stä+W6 statt 2W6 Schaden. Nur für Bögen und Langbögen.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Mächtiger Wurf": {
        "name": "Mächtiger Wurf",
        "kategorie": "Kampf",
        "rang": "V",
        "voraussetzungen": ["Stärke W8+", "Werfen W10+"],
        "beschreibung": "Wurfwaffen-Reichweite +1/2/4. Stärke eine Stufe höher (max W12+2) auf kurze Reichweite.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Meister übergroßer Waffen": {
        "name": "Meister übergroßer Waffen",
        "kategorie": "Kampf",
        "rang": "V",
        "voraussetzungen": ["Stärke W10+", "Kämpfen W10+", "Größe +0 oder größer"],
        "beschreibung": "Kann zweihändige Nahkampfwaffen einhändig führen. Kann mit normaler einhändiger Waffe kombiniert werden.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Nekromantische Verstümmelung": {
        "name": "Nekromantische Verstümmelung",
        "kategorie": "Kampf",
        "rang": "V",
        "voraussetzungen": ["Willenskraft W8+", "Kämpfen W10+"],
        "beschreibung": "Angesagte Ziele gegen Untote verursachen normalen zusätzlichen Schaden (ignoriert Untot-Merkmal).",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Riesenspalter": {
        "name": "Riesenspalter",
        "kategorie": "Kampf",
        "rang": "H",
        "voraussetzungen": ["Riesentöter"],
        "beschreibung": "Gegen Kreaturen 3+ Stufen größer: Kann Panzerung oder Größe umgehen statt +1W6 Schaden.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Schildwall": {
        "name": "Schildwall",
        "kategorie": "Kampf",
        "rang": "F",
        "voraussetzungen": ["Block", "mittlerer oder großer Schild"],
        "beschreibung": "Ein benachbarter Kamerad erhält den Schildbonus des Helden auf seine Parade. Nur höchster Bonus gilt.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Schneegänger": {
        "name": "Schneegänger",
        "kategorie": "Kampf",
        "rang": "A",
        "voraussetzungen": ["Geschicklichkeit W6+"],
        "beschreibung": "Schnee: 1,5\" statt 2\" pro Zoll. Raues Eis = normaler Untergrund. Glattes Eis = raues Eis.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Schneeläufer": {
        "name": "Schneeläufer",
        "kategorie": "Kampf",
        "rang": "F",
        "voraussetzungen": ["Schneegänger"],
        "beschreibung": "Schnee und glattes Eis = normaler Untergrund.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Stahlwall": {
        "name": "Stahlwall",
        "kategorie": "Kampf",
        "rang": "V",
        "voraussetzungen": ["Geschicklichkeit W8+", "Kämpfen W8+", "Wahrnehmung W8+"],
        "beschreibung": "Gegner erhalten keinen Überzahlbonus gegen den Helden.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Tapfer": {
        "name": "Tapfer",
        "kategorie": "Kampf",
        "rang": "A",
        "voraussetzungen": ["Willenskraft W8+"],
        "beschreibung": "+2 auf alle Willenskraftwürfe gegen Furcht. -2 von Würfen auf der Furchttabelle.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },

    # ---- Machttalente (Hellfrost) ----
    "Alchemie": {
        "name": "Alchemie",
        "kategorie": "Macht",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (beliebig)", "arkane Fertigkeit W6+", "Wissen (Alchemie) W6+"],
        "beschreibung": "Kann alchemistische Gegenstände (Tränke, Schriftrollen, Zauberstäbe) erschaffen. Wissensprobe (Alchemie) zum Herstellen. Kosten: 50gs pro Rang des Zaubers.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Eiseskälte": {
        "name": "Eiseskälte",
        "kategorie": "Macht",
        "rang": "V",
        "voraussetzungen": ["Arkaner Hintergrund (Kälte-Ausprägungen)", "arkane Fertigkeit W10+", "Wissen (Übernatürliches) W10+"],
        "beschreibung": "Kälte/Kaltfeuer/Eis-Zauber verursachen gegen Resistenz (Kälte) normalen und gegen Immunität (Kälte) halben Schaden. Doppelter Schaden gegen Empfindlich (Kälte).",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Fokus": {
        "name": "Fokus",
        "kategorie": "Macht",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (beliebig)", "Willenskraft W6+", "arkane Fertigkeit W8+"],
        "beschreibung": "Bei Angeschlagen durch Zauber oder Sog: sofortige Erholungsprobe mit -2.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Stärkerer Fokus": {
        "name": "Stärkerer Fokus",
        "kategorie": "Macht",
        "rang": "H",
        "voraussetzungen": ["Fokus"],
        "beschreibung": "Wie Fokus, aber ohne -2 Abzug.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Konzentration": {
        "name": "Konzentration",
        "kategorie": "Macht",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (beliebig)", "Konstitution W6+", "Verstand W6+", "Willenskraft W6+"],
        "beschreibung": "+2 auf Widerstehen von Konzentrationsstörungen.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Stärkere Konzentration": {
        "name": "Stärkere Konzentration",
        "kategorie": "Macht",
        "rang": "V",
        "voraussetzungen": ["Konzentration"],
        "beschreibung": "Bonus steigt auf +4.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Meister der Elemente": {
        "name": "Meister der Elemente",
        "kategorie": "Macht",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Elementarmagie)"],
        "beschreibung": "Meistere ein neues Element. Einmal pro Rang. Jedes zusätzliche Element: -1 auf alle Elementarmagiewürfe. Arkhseidmadr (alle 4 Elemente): keine Abzüge.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Runenkenntnis": {
        "name": "Runenkenntnis",
        "kategorie": "Macht",
        "rang": "A",
        "voraussetzungen": ["Arkaner Hintergrund (Runenmagie)", "Wissen (Übernatürliches) W8+", "spezifische Runenfertigkeit W8+"],
        "beschreibung": "+1 auf arkane Fertigkeitswürfe für die drei Zaubersprüche der gewählten Rune. Einmal pro Rang, jedes Mal andere Rune.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Stab verstärken": {
        "name": "Stab verstärken",
        "kategorie": "Macht",
        "rang": "F",
        "voraussetzungen": ["Arkaner Hintergrund (Heahmagie)", "Heahmagie W8+", "Wissen (Übernatürliches) W8+"],
        "beschreibung": "Wähle eine Stabfähigkeit: Ablenken (-1/-2 auf Fernkampf), Aura (+2 Einschüchtern/Überreden), Schaden (Stä+W6 PB1/Stä+W8 PB2), oder Zauberspeicher (+2 auf gespeicherten Zauber). Einmal pro Rang.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Zauberfinesse": {
        "name": "Zauberfinesse",
        "kategorie": "Macht",
        "rang": "A",
        "voraussetzungen": ["Arkaner Hintergrund (außer Runenmagie)", "arkane Fertigkeit W8+", "Wissen (Übernatürliches) W8+"],
        "beschreibung": "Wähle einen Zauber und eine Option: Arkan (WC-Würfel +1), Panzerbrechend (PB 2), Reichweite (+2/4/8), Schwere Waffe, oder Selektiv (Ziele ausnehmen). Mehrfach wählbar.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Zaubersprüche kombinieren": {
        "name": "Zaubersprüche kombinieren",
        "kategorie": "Macht",
        "rang": "H",
        "voraussetzungen": ["Arkaner Hintergrund (beliebig)", "arkane Fertigkeit W10+", "Wissen (Übernatürliches) W10+"],
        "beschreibung": "Kann zwei unterschiedliche Zaubersprüche gleichzeitig auf dasselbe Ziel wirken. Eine arkane Fertigkeitsprobe für beide.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },

    # ---- Soziale Talente (Hellfrost) ----
    "Meisterhafter Erzähler": {
        "name": "Meisterhafter Erzähler",
        "kategorie": "Sozial",
        "rang": "F",
        "voraussetzungen": ["Verstand W8+", "Überreden W8+", "Wissen (Folklore) W8+"],
        "beschreibung": "Variable Ruhmvergabe: W8 statt W6. Keine Ruhmabzüge bei kritischem Fehlschlag.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },
    "Legendärer Erzähler": {
        "name": "Legendärer Erzähler",
        "kategorie": "Sozial",
        "rang": "H",
        "voraussetzungen": ["Meisterhafter Erzähler"],
        "beschreibung": "Pro Steigerung nach der ersten +1W8 Ruhm bei variabler Ruhmvergabe.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    },

    # ---- Wildcard-Talente (Hellfrost) ----
    "Energieschub (Hellfrost)": {
        "name": "Energieschub",
        "kategorie": "Wildcard",
        "rang": "F",
        "voraussetzungen": ["Wildcard", "Arkaner Hintergrund (beliebig)", "arkane Fertigkeit W10+"],
        "beschreibung": "Verdoppelt den Schaden arkaner Angriffe in dieser Runde.",
        "neue_maechte": 0,
        "machtpunkte": 0,
        "ausgewaehlt": False,
        "aktiv": True
    }
}
talente.update(hellfrost_talente)


# ============================================================
# 6. MÄCHTE - aus FK übernehmen, nicht verfügbare entfernen
# ============================================================
maechte = {}

# Standard-Mächte aus FK übernehmen
for key, m in fk.get("maechte", {}).items():
    maechte[key] = copy.deepcopy(m)

# Nicht verfügbare Mächte deaktivieren (laut Conversion)
nicht_verfuegbare_maechte = [
    "Blenden",
    "Dunkelsicht",
    "Fernsicht",
    "Gedankenlesen",
    "Körperlosigkeit",
    "Machtraud",
    "Maskieren",
    "Niederwerfen",
    "Schadensfeld",
    "Verbündete beschwören",
    "Verwüstung",
    "Weissagung"
]

for key, m in maechte.items():
    if m.get("name") in nicht_verfuegbare_maechte:
        m["aktiv"] = False

# Verschleiern bleibt, aber Licht wird deaktiviert (Licht/Verschleiern → nur Verschleiern)
# Prüfen ob "Licht" als separate Macht existiert
for key, m in maechte.items():
    if m.get("name") == "Licht":
        m["aktiv"] = False


# ============================================================
# 7. AUSRÜSTUNG - aus FK übernehmen (mittelalterliches Setting)
# ============================================================
ausruestung = {}

# Standard-Ausrüstung aus FK übernehmen
for key, a in fk.get("ausruestung", {}).items():
    ausruestung[key] = copy.deepcopy(a)

# Hellfrost-spezifische Ausrüstung hinzufügen
hellfrost_ausruestung = {
    "Winterkleidung": {
        "name": "Winterkleidung",
        "kategorie": "Allgemein",
        "gewicht": 3,
        "kosten": 10,
        "setting": "mittelalterlich",
        "beschreibung": "Pelzmantel, Handschuhe, Wollmütze und dicke Stiefel. +2 auf Konstitutionswürfe gegen Kälte.",
        "aktiv": True
    },
    "Winterkleidung, schwere": {
        "name": "Winterkleidung, schwere",
        "kategorie": "Allgemein",
        "gewicht": 5,
        "kosten": 50,
        "setting": "mittelalterlich",
        "beschreibung": "Doppellagige Pelze und isolierte Kleidung. +4 auf Konstitutionswürfe gegen Kälte.",
        "aktiv": True
    },
    "Schneeschuhe": {
        "name": "Schneeschuhe",
        "kategorie": "Allgemein",
        "gewicht": 2,
        "kosten": 5,
        "setting": "mittelalterlich",
        "beschreibung": "Erlauben Bewegung im Schnee ohne Abzüge. -1 auf Kämpfen und Geschicklichkeitsproben.",
        "aktiv": True
    },
    "Eispickel": {
        "name": "Eispickel",
        "kategorie": "Allgemein",
        "gewicht": 1.5,
        "kosten": 5,
        "setting": "mittelalterlich",
        "beschreibung": "+2 auf Kletternwürfe in Eis/Schnee-Umgebung.",
        "aktiv": True
    },
    "Alchemistenkoffer": {
        "name": "Alchemistenkoffer",
        "kategorie": "Allgemein",
        "gewicht": 10,
        "kosten": 200,
        "setting": "mittelalterlich",
        "beschreibung": "Tragbares Labor für Kräutermagie und Alchemie. Enthält Werkzeuge, Tiegel und Phiolen.",
        "aktiv": True
    },
    "Eisholzaxt": {
        "name": "Eisholzaxt",
        "kategorie": "Waffe",
        "gewicht": 4,
        "kosten": 100,
        "setting": "mittelalterlich",
        "beschreibung": "Axt aus magisch gehärtetem Eisholz. Leichter als Stahl, genauso scharf.",
        "aktiv": True,
        "typ": "Nahkampf",
        "mindeststaerke": "W6",
        "eigenschaften": {
            "Schaden": "Stä+W8",
            "Reichweite": "nah",
            "FR": "-",
            "Schuss": "-",
            "PB": "-"
        }
    },
    "Wissensband": {
        "name": "Wissensband",
        "kategorie": "Allgemein",
        "gewicht": 1,
        "kosten": 100,
        "setting": "mittelalterlich",
        "beschreibung": "Ein Buch, das Wissen zu einem bestimmten Thema enthält. Benötigt das Talent Bücherei.",
        "aktiv": True
    }
}
ausruestung.update(hellfrost_ausruestung)


# ============================================================
# 8. SETTINGREGELN
# ============================================================
settingregeln = {
    "strahlschablone": False,
    "große_hoehen": False,
    "verrat": False,
    "schwierige_heilung": False,
    "freizeit": False,
    "riesige_feinde": False,
    "schurkische_entschlossenheit": False,
    "dynamischer_rueckschlag": False,
    "entschlossenheit": False,
    "fanatiker": False,
    "fertigkeitsspezialisierungen": False,
    "fieser_schaden": False,
    "geborener_held": True,
    "grosse_abenteuer": False,
    "helden_sterben_nie": False,
    "keine_machtpunkte": True,
    "kreativer_kampf": False,
    "mehr_fertigkeitspunkte": False,
    "mehr_sprachen": False,
    "narrenglueck": False,
    "schnelle_genesung": False,
    "schwere_entscheidungen": False,
    "ungepanzerter_held": False,
    "wundobergrenze": False
}


# ============================================================
# 9. VOELKER_SELECTED
# ============================================================
voelker_selected = {
    "Engro": True,
    "Frostblut": True,
    "Frostzwerg": True,
    "Herdelf": True,
    "Mensch_Anari": True,
    "Mensch_Saxa": True,
    "Mensch_Finnar": True,
    "Mensch_Tuomi": True,
    "Taigaelf": True
}


# ============================================================
# ZUSAMMENBAUEN
# ============================================================
hellfrost = {
    "name": "Hellfrost",
    "description": "Hellfrost - Ein gefrorenes Fantasy-Setting für Savage Worlds",
    "voelker": voelker,
    "voelker_selected": voelker_selected,
    "attribute": attribute,
    "fertigkeiten_daten": fertigkeiten_daten,
    "handicaps": handicaps,
    "talente": talente,
    "maechte": maechte,
    "ausruestung": ausruestung,
    "settingregeln": settingregeln
}


# ============================================================
# SCHREIBEN
# ============================================================
with open(HF_PATH, "w", encoding="utf-8") as f:
    json.dump(hellfrost, f, ensure_ascii=False, indent=4)

print(f"Hellfrost.json geschrieben: {HF_PATH}")
print(f"  Völker: {len(voelker)}")
print(f"  Fertigkeiten: {len(fertigkeiten_daten)}")
print(f"  Handicaps: {len(handicaps)}")
print(f"  Talente: {len(talente)}")
print(f"  Mächte: {len(maechte)}")
print(f"  Ausrüstung: {len(ausruestung)}")

# JSON validieren
try:
    with open(HF_PATH, "r", encoding="utf-8") as f:
        json.load(f)
    print("JSON-Validierung: OK")
except json.JSONDecodeError as e:
    print(f"JSON-Validierung: FEHLER - {e}")
