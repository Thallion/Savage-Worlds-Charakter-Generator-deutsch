#!/usr/bin/env python3
"""
Merges SWAE base elements (handicaps, talente, maechte) into
Horror Kompendium and SciFi Kompendium JSON files.

SWAE elements are inserted BEFORE existing Kompendium elements,
so that specialized entries appear at the end.
Elements already present in a Kompendium (by key) are skipped.
The generic "Arkaner Hintergrund" from SWAE is always skipped.
"""

import json
from pathlib import Path
from collections import OrderedDict

SETTINGS_DIR = Path(__file__).resolve().parent.parent / "settings"
SWAE_PATH = SETTINGS_DIR / "SWAE.json"
KOMPENDIEN = [
    SETTINGS_DIR / "Horror Kompendium.json",
    SETTINGS_DIR / "SciFi Kompendium.json",
]
SECTIONS = ["handicaps", "talente", "maechte"]
SKIP_KEYS = {"Arkaner Hintergrund"}


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")


def merge_section(swae_section: OrderedDict, komp_section: OrderedDict, section_name: str) -> tuple[OrderedDict, int]:
    """Merge SWAE entries before Kompendium entries, skipping duplicates and SKIP_KEYS."""
    merged = OrderedDict()
    inserted = 0

    # First: add SWAE elements that are not already in Kompendium
    for key, value in swae_section.items():
        if key in SKIP_KEYS:
            continue
        if key not in komp_section:
            merged[key] = value
            inserted += 1

    # Then: add all existing Kompendium elements
    for key, value in komp_section.items():
        merged[key] = value

    return merged, inserted


def main():
    swae = load_json(SWAE_PATH)
    print(f"SWAE geladen: {SWAE_PATH.name}")
    for section in SECTIONS:
        print(f"  {section}: {len(swae[section])} Einträge")

    for komp_path in KOMPENDIEN:
        komp = load_json(komp_path)
        print(f"\n{'='*60}")
        print(f"Verarbeite: {komp_path.name}")

        total_inserted = 0
        for section in SECTIONS:
            swae_section = swae.get(section, OrderedDict())
            komp_section = komp.get(section, OrderedDict())

            existing_keys = set(komp_section.keys())
            skipped = existing_keys & set(swae_section.keys()) - SKIP_KEYS

            merged, inserted = merge_section(swae_section, komp_section, section)
            komp[section] = merged
            total_inserted += inserted

            print(f"  {section}: +{inserted} SWAE-Einträge eingefügt, "
                  f"{len(skipped)} übersprungen (bereits vorhanden), "
                  f"gesamt: {len(merged)}")
            if skipped:
                print(f"    Übersprungen: {sorted(skipped)}")

        save_json(komp_path, komp)
        print(f"  => {komp_path.name} gespeichert ({total_inserted} neue Einträge)")


if __name__ == "__main__":
    main()
