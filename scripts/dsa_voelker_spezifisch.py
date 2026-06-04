#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 4b: Spezies DSA-spezifischer gestalten + nicht-DSA-Spezies entfernen.

Quelle: DSA-Spezies-Stat-Blocks (vom User bereitgestellt, „Aventurien"-Spezies).

Aktionen:
  A. LÖSCHEN: Drachling, Necker, Nachtalb (passen nicht / nicht gewünscht)
  B. Elf:    + Harmonische Magie (Wirkungsdauer der Mächte verdoppelt),
             + Zweistimmiger Gesang, + Nichtschläfer
  C. Halbelf:+ Zweistimmiger Gesang
  D. Goblin: REWORK weg vom Savage-Pathfinder-Goblin hin zum DSA-Goblin
             (Ges +2 statt +4, Willenskraft -1, keen senses, Biss, Aberglaube;
              raus: „Alles essen"/Reiter/Überlebenskünstler/Wärmesicht)
  E. Halbork:REWORK auf DSA (KO +1 / Zäher Hund statt Stärke-Brute, Orksgeruch)
  F. Ork:    + Biss (Hauer), + Natürlicher Rüstungsschutz I (ledrige Haut)
  G. Zwerg:  + Nichtschwimmer, + Hitzeresistenz
  H. voelker_selected auf die 9 verbleibenden Spezies (alle True)

Idempotent (nutzt Marker-Flags in spezielle_effekte).
"""
import json
import sys
from pathlib import Path

SETTING = Path("settings/Savage Aventurien.json")
LOESCHEN = ["Drachling", "Necker", "Nachtalb"]
SPEZIES_9 = ["Mensch", "Elf", "Halbelf", "Zwerg", "Ork", "Halbork",
             "Goblin", "Achaz", "Holberker"]


def add_besonderheit(volk, text):
    if text not in volk["besonderheiten"]:
        volk["besonderheiten"].append(text)


def add_handicap(volk, text):
    if text not in volk["handicaps"]:
        volk["handicaps"].append(text)


def main():
    data = json.loads(SETTING.read_text(encoding="utf-8"))
    v = data["voelker"]
    log = []

    # --- A. Löschen ---------------------------------------------------------
    for nm in LOESCHEN:
        if nm in v:
            del v[nm]
            log.append(f"  − {nm} gelöscht")

    # --- B. Elf -------------------------------------------------------------
    elf = v["Elf"]
    add_besonderheit(elf, "Harmonische Magie (Die Wirkungsdauer der vom Elf "
                          "gewirkten Mächte wird verdoppelt)")
    add_besonderheit(elf, "Zweistimmiger Gesang (+1 auf Darbietung beim Singen)")
    add_besonderheit(elf, "Nichtschläfer (Benötigt keinen Schlaf, nur eine ruhige "
                          "Trance/Meditation)")
    elf["effects"]["spezielle_effekte"].update(
        harmonische_magie=True, zweistimmiger_gesang=True, nichtschlaefer=True)
    log.append("  ~ Elf: Harmonische Magie + Zweistimmiger Gesang + Nichtschläfer")

    # --- C. Halbelf ---------------------------------------------------------
    halbelf = v["Halbelf"]
    add_besonderheit(halbelf, "Zweistimmiger Gesang (+1 auf Darbietung beim Singen)")
    halbelf["effects"]["spezielle_effekte"]["zweistimmiger_gesang"] = True
    log.append("  ~ Halbelf: Zweistimmiger Gesang")

    # --- D. Goblin (DSA-Rework) --------------------------------------------
    goblin = v["Goblin"]
    goblin["besonderheiten"] = [
        "Geschickt (Geschicklichkeit W6 statt W4, Maximum W12+1)",
        "Dunkelsicht (Ignoriert Beleuchtungsabzüge auf bis zu 10\"/20 Meter)",
        "Geschärfte Sinne (Wahrnehmung W6 statt W4, Maximum W12+1)",
        "Biss (Stä+W4 Schaden, kleine Hauer/spitze Zähne)",
    ]
    goblin["handicaps"] = [
        "Größe -1 (Reduzierte Größe und Robustheit)",
        "Niedrige Seelenkraft (anfällig für Willenskraft-basierte Effekte)",
        "Abergläubisch (Aberglaube und Neugier prägen das Verhalten)",
    ]
    goblin["talente"] = []
    goblin["sprachen"] = ["Gemeinsprache", "Goblinisch"]
    goblin["effects"] = {
        "attribute_bonuses": {"Geschicklichkeit": 2, "Willenskraft": -1},
        "robustheit_bonus": 0,
        "bewegungsweite_bonus": 0,
        "fertigkeits_startboni": {"Wahrnehmung": 2},
        "fertigkeits_modifier_boni": {"Überreden": -2},
        "auto_talente": [],
        "auto_handicaps": ["Abergläubisch"],
        "spezielle_effekte": {
            "dunkelsicht": True,
            "geschaerfte_sinne": True,
            "biss": True,
            "groesse_minus1": True,
        },
        "wahlmoeglichkeiten": {},
        "groesse_modifikator": -1,
    }
    log.append("  ~ Goblin: auf DSA-Goblin umgebaut (de-SWPF: Ges+2 statt +4, keen "
               "senses, Biss, Aberglaube)")

    # --- E. Halbork (DSA-Rework) -------------------------------------------
    halbork = v["Halbork"]
    halbork["besonderheiten"] = [
        "Zäher Hund (zäher und leidensfähiger als Menschen – Konstitution W6 statt "
        "W4, Maximum W12+1)",
        "Dunkelsicht (Ignoriert Beleuchtungsabzüge auf bis zu 10\"/20 Meter)",
    ]
    halbork["handicaps"] = [
        "Außenseiter (leicht: -2 Überreden – in beiden Welten wenig angesehen)",
        "Stechender Orksgeruch (Strenger Körpergeruch: Heimlichkeit gegen "
        "Geruchssinn-Wesen -2; -1 Überreden in höfischer Gesellschaft)",
    ]
    halbork["effects"] = {
        "attribute_bonuses": {"Konstitution": 2},
        "robustheit_bonus": 0,
        "bewegungsweite_bonus": 0,
        "fertigkeits_startboni": {},
        "auto_talente": [],
        "auto_handicaps": ["Außenseiter_leicht"],
        "spezielle_effekte": {
            "dunkelsicht": True,
            "strenger_koerpergeruch": True,
        },
        "wahlmoeglichkeiten": {},
    }
    log.append("  ~ Halbork: auf DSA umgebaut (KO+1/Zäher Hund statt Stärke-Brute, "
               "Stechender Orksgeruch)")

    # --- F. Ork (additive DSA) ---------------------------------------------
    ork = v["Ork"]
    add_besonderheit(ork, "Biss (Stä+W4 Schaden, natürliche Waffe – die Hauer der Orks)")
    add_besonderheit(ork, "Natürlicher Rüstungsschutz I (Panzerung +1 durch ledrige Haut)")
    ork["effects"]["spezielle_effekte"].update(biss=True, panzerung_1=True)
    log.append("  ~ Ork: + Biss (Hauer) + Natürlicher Rüstungsschutz I")

    # --- G. Zwerg (additive DSA) -------------------------------------------
    zwerg = v["Zwerg"]
    add_besonderheit(zwerg, "Nichtschwimmer (Schlechter Auftrieb – kann nicht schwimmen)")
    add_besonderheit(zwerg, "Hitzeresistenz (+4 auf Proben gegen große Hitze, "
                            "z.B. in Schmiede/Lava)")
    add_handicap(zwerg, "Nichtschwimmer (Schlechter Auftrieb, kann nicht schwimmen)")
    zwerg["effects"]["spezielle_effekte"].update(hitzeresistenz=True, nichtschwimmer=True)
    if "Nichtschwimmer" not in zwerg["effects"].get("auto_handicaps", []):
        zwerg["effects"].setdefault("auto_handicaps", []).append("Nichtschwimmer")
    log.append("  ~ Zwerg: + Nichtschwimmer + Hitzeresistenz")

    # --- H. voelker_selected -----------------------------------------------
    data["voelker_selected"] = {sp: True for sp in SPEZIES_9}
    log.append(f"  ~ voelker_selected → {len(SPEZIES_9)} Spezies (alle True)")

    SETTING.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")

    print("Spezies-DSA-Pass abgeschlossen:")
    for line in log:
        print(line)
    print(f"\nVölker gesamt jetzt: {len(v)}  ({', '.join(v.keys())})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
