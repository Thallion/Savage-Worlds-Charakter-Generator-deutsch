"""
Hängt die DSA-Trappings an die Beschreibung der Mächte an, damit die
Suchfunktion (views/maechte_view.py) auch DSA-Begriffe findet.

Format: "\n\nDSA-Trappings: T1, T2, T3, ..."

Nur Mächte mit nicht-leerer dsa_trappings-Liste werden angefasst.
Bestehende Beschreibungstexte bleiben unangetastet (Wortlaut 1:1 erhalten).
"""

import json
from pathlib import Path

SETTING_PATH = Path("settings/Savage Aventurien.json")
TRENNZEICHEN = ", "
PRAEFIX = "\n\nDSA-Trappings: "


def main() -> None:
    with SETTING_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    maechte = data.get("maechte", {})

    aktualisiert = 0
    uebersprungen = 0
    beispiele = []

    for name, macht in maechte.items():
        if not isinstance(macht, dict):
            continue
        trap = macht.get("dsa_trappings")
        if not isinstance(trap, list) or not trap:
            uebersprungen += 1
            continue

        beschreibung = macht.get("beschreibung", "")

        if "DSA-Trappings:" in beschreibung:
            continue

        anhang = PRAEFIX + TRENNZEICHEN.join(trap)
        macht["beschreibung"] = beschreibung + anhang
        aktualisiert += 1
        if len(beispiele) < 3:
            beispiele.append((name, macht["beschreibung"][:300]))

    with SETTING_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Aktualisiert: {aktualisiert}")
    print(f"Übersprungen (leere/keine dsa_trappings): {uebersprungen}")
    print(f"Beispiele (erste 3):")
    for name, snippet in beispiele:
        print(f"  - {name}: {snippet}...")


if __name__ == "__main__":
    main()
