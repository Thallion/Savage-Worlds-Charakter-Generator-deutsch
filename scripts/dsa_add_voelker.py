#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 4 der DSA-Konvertierung: Völker (Spezies) anpassen, erweitern, neu anlegen.

Quelle: https://dsa.ulisses-regelwiki.de/spezies.html
  - Spez_Holberker.html, spezies/nachtalb.html (Detaildaten)

Aktionen:
  1. NEU: Holberker (verwilderte Menschen Nordaventuriens)
  2. NEU: Nachtalb (nachtaktive Elfen-Verwandte, Nai Ashyrr)
  3. ANPASSEN: Ork  -> Strenger Körpergeruch (DSA: Stechender Orkgeruch)
  4. ANPASSEN: Achaz -> Hitzeresistenz ergänzen (Kälte-Anfälligkeit bereits vorhanden)
  5. AUFRÄUMEN: voelker_selected auf die 12 tatsächlichen Spezies umstellen (alle True)

DSA-Werte werden in den bestehenden SW-Stil (effects-Block) übersetzt, nicht
1:1 als DSA-Statblock kopiert. Idempotent.
"""
import json
import sys
from pathlib import Path

SETTING = Path("settings/Savage Aventurien.json")

# Reihenfolge der 12 DSA-Spezies (für voelker_selected)
DSA_SPEZIES_12 = [
    "Mensch", "Elf", "Halbelf", "Zwerg", "Ork", "Halbork",
    "Goblin", "Achaz", "Necker", "Drachling", "Holberker", "Nachtalb",
]


def leeres_effects():
    return {
        "attribute_bonuses": {},
        "robustheit_bonus": 0,
        "bewegungsweite_bonus": 0,
        "fertigkeits_startboni": {},
        "auto_talente": [],
        "auto_handicaps": [],
        "spezielle_effekte": {},
        "wahlmoeglichkeiten": {},
    }


# --- 1. Holberker -----------------------------------------------------------
HOLBERKER = {
    "name": "Holberker",
    "handicaps": [
        "Ungehobelt (-1 auf Verstandsproben durch fehlende Bildung)",
    ],
    "talente": [],
    "besonderheiten": [
        "Zäher Hund (+1 Robustheit, abgehärtete Wildnisbewohner)",
        "Widerstandsfähig (Konstitution W6 statt W4, Maximum W12+1)",
        "Nachtsicht (Ignoriert Abzüge für Düstere und Dunkle Beleuchtung)",
        "Richtungssinn (+2 auf Überleben zur Orientierung in der Wildnis)",
    ],
    "sprachen": ["Gemeinsprache", "Holberksch (Dialekt)"],
    "altersspanne": "Erwachsen mit 16, Alt mit 60, maximales Alter 70-90",
    "groesse_maennlich": "1,65-1,90m, 70-95kg (Durchschnitt 1,78m, 82kg)",
    "groesse_weiblich": "1,55-1,80m, 60-80kg (Durchschnitt 1,68m, 68kg)",
    "aktiv": True,
    "custom": False,
    "effects": {
        **leeres_effects(),
        "attribute_bonuses": {"Konstitution": 2, "Verstand": -1},
        "robustheit_bonus": 1,
        "fertigkeits_startboni": {"Überleben": 2},
        "auto_talente": ["Nachtsicht"],
        "spezielle_effekte": {
            "nachtsicht": True,
            "zaeher_hund": True,
            "richtungssinn": True,
            "wildnisverbunden": True,
        },
    },
}

# --- 2. Nachtalb ------------------------------------------------------------
NACHTALB = {
    "name": "Nachtalb",
    "handicaps": [
        "Lichtempfindlich (lichtscheu, -1 auf Sicht-Eigenschaftswürfe bei hellem Licht)",
        "Schlank (-1 Robustheit, -1 auf Konstitutionsproben)",
    ],
    "talente": [],
    "besonderheiten": [
        "Nächtliche Begabung (Alle Nachtalben können zaubern – wie Elfenmagie: "
        "Freie Wiederholung gegen gegnerische Mächte)",
        "Dunkelsicht (Ignoriert Beleuchtungsabzüge auf bis zu 10\"/20 Meter)",
        "Nachtsicht (Ignoriert Abzüge für Düstere und Dunkle Beleuchtung)",
        "Geschickt (Geschicklichkeit W6 statt W4, Maximum W12+1)",
        "Geschärfte Sinne (Wahrnehmung W6 statt W4, Maximum W12+1)",
        "Nichtschläfer (Benötigt keinen Schlaf, nur eine ruhige Trance)",
        "Zweistimmiger Gesang (+1 auf Darbietung beim Singen)",
    ],
    "sprachen": ["Gemeinsprache", "Nai-Ashyrr"],
    "altersspanne": "Erwachsen mit 60, Alt mit 200, maximales Alter 300-500",
    "groesse_maennlich": "1,74-2,12m, sehr schlank (Durchschnitt 1,92m)",
    "groesse_weiblich": "1,72-2,05m, sehr schlank (Durchschnitt 1,88m)",
    "aktiv": True,
    "custom": False,
    "effects": {
        **leeres_effects(),
        "attribute_bonuses": {"Geschicklichkeit": 2, "Konstitution": -1},
        "fertigkeits_startboni": {"Wahrnehmung": 2},
        "auto_talente": ["Nachtsicht"],
        "auto_handicaps": ["Lichtempfindlich", "Schlank"],
        "spezielle_effekte": {
            "nachtsicht": True,
            "dunkelsicht": True,
            "lichtempfindlich": True,
            "nachtalb_magie": True,
            "nichtschlaefer": True,
            "zweistimmiger_gesang": True,
        },
    },
}


def main():
    if not SETTING.exists():
        print(f"FEHLER: {SETTING} nicht gefunden (cwd={Path.cwd()})", file=sys.stderr)
        return 1
    data = json.loads(SETTING.read_text(encoding="utf-8"))
    voelker = data["voelker"]
    log = []

    # 1./2. Neue Völker
    for neu in (HOLBERKER, NACHTALB):
        if neu["name"] in voelker:
            log.append(f"  = {neu['name']} bereits vorhanden – übersprungen")
        else:
            voelker[neu["name"]] = neu
            log.append(f"  + {neu['name']} neu angelegt")

    # 3. Ork: Strenger Körpergeruch
    ork = voelker["Ork"]
    geruch = ("Stechender Orkgeruch (Strenger Körpergeruch: leichter aufzuspüren – "
              "Heimlichkeit gegen Geruchssinn-Wesen -2; -1 Überreden in höfischer "
              "Gesellschaft)")
    if not ork["effects"]["spezielle_effekte"].get("strenger_koerpergeruch"):
        ork["handicaps"].append(geruch)
        ork["effects"]["spezielle_effekte"]["strenger_koerpergeruch"] = True
        log.append("  ~ Ork: Strenger Körpergeruch ergänzt")
    else:
        log.append("  = Ork: Strenger Körpergeruch bereits vorhanden")

    # 4. Achaz: Hitzeresistenz
    achaz = voelker["Achaz"]
    hitze = "Widerstand gegen Naturgewalten (Hitze: +4 Resistenz, -4 Schaden)"
    if not achaz["effects"]["spezielle_effekte"].get("widerstand_hitze"):
        achaz["besonderheiten"].append(hitze)
        achaz["effects"]["spezielle_effekte"]["widerstand_hitze"] = True
        log.append("  ~ Achaz: Hitzeresistenz ergänzt")
    else:
        log.append("  = Achaz: Hitzeresistenz bereits vorhanden")

    # 5. voelker_selected neu aufbauen (12 Spezies, alle True)
    alt = data.get("voelker_selected", {})
    data["voelker_selected"] = {sp: True for sp in DSA_SPEZIES_12}
    log.append(f"  ~ voelker_selected neu aufgebaut: {len(alt)} alte Einträge -> "
               f"{len(DSA_SPEZIES_12)} DSA-Spezies (alle True)")

    SETTING.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("Völker-Anpassung abgeschlossen:")
    for line in log:
        print(line)
    print(f"\nVölker gesamt jetzt: {len(voelker)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
