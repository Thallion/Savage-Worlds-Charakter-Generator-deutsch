#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Legt pro Gottheit eine SW-Macht 'Mirakel (<Gott>)' an und füllt sie mit deren
rein narrativen (mechanisch nicht über eine Standard-Macht abbildbaren) Liturgien
als Trappings inkl. Kurzbeschreibung.

Narrativ = Liturgie aus liber_herkunft.json, die WEDER in LITURGIE_SW gemappt ist
NOCH bereits als Trapping einer Macht existiert. universell/Zwölfgötterkult → 'Mirakel (Zwölfgötter)'.

Idempotent. Aufruf:  python scripts/add_mirakel_maechte.py
"""
import json
import os
import importlib.util
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "settings", "Savage Aventurien.json")
HERK = os.path.join(ROOT, "scripts", "liber_herkunft.json")
BESCH = os.path.join(ROOT, "scripts", "liber_beschreibung.json")

# Anzeige-Namen der Gottheit im Macht-Beschreibungstext
GOTT_NAME = {
    "Zwölfgötter": "der Zwölfgötter", "Praios": "Praios'", "Rondra": "Rondras",
    "Efferd": "Efferds", "Travia": "Travias", "Boron": "Borons", "Hesinde": "Hesindes",
    "Firun": "Firuns", "Tsa": "Tsas", "Phex": "Phex'", "Peraine": "Peraines",
    "Ingerimm": "Ingerimms", "Rahja": "Rahjas", "Aves": "Aves'", "Ifirn": "Ifirns",
    "Kor": "Kors", "Nandus": "Nandus'", "Swafnir": "Swafnirs", "Angrosch": "Angroschs",
    "Gravesh": "Gravesh'", "Himmelswölfe": "der Himmelswölfe", "H’Szint": "H’Szints",
    "Kamaluq": "Kamaluqs", "Tairach": "Tairachs", "Zsahh": "Zsahhs", "H’Ranga": "H’Rangas",
    "Riva": "Rivas", "Namenlos": "des Namenlosen",
}


def base(n):
    return n.split(" (")[0].strip()


def main():
    spec = importlib.util.spec_from_file_location("gen", os.path.join(ROOT, "scripts", "gen_traditionen_zauber.py"))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    LIT = gen.LITURGIE_SW

    herk = json.load(open(HERK, encoding="utf-8"))
    besch = json.load(open(BESCH, encoding="utf-8"))
    d = json.load(open(SRC, encoding="utf-8"))
    mae = d["maechte"]

    # Vollständiger Rebuild: bestehende Mirakel-Mächte entfernen ...
    for nm in [n for n in mae if n.startswith("Mirakel (")]:
        del mae[nm]

    # ... narrativ = Liturgie weder in LITURGIE_SW gemappt NOCH Trapping einer (Nicht-Mirakel-)Macht
    vorhandene_traps = {base(t).lower() for m in mae.values() for t in (m.get("dsa_trappings") or [])}
    by_god = defaultdict(list)
    for lit, goetter in herk.items():
        if lit in LIT or base(lit).lower() in vorhandene_traps:
            continue
        ziele = {("Zwölfgötter" if g in ("universell", "Zwölfgötterkult") else g) for g in goetter}
        for g in ziele:
            by_god[g].append(lit)

    traps = 0
    for gott in sorted(by_god):
        mname = f"Mirakel ({gott})"
        gname = GOTT_NAME.get(gott, gott)
        besch_lines = [
            f"Seltene, erzählerische Wundertaten im Namen {gname}. Diese Liturgien haben keine feste "
            f"Spielwert-Wirkung – die genaue Auswirkung legt die Spielleitung als göttlichen Eingriff "
            f"fest (oft Bennie- oder Wild-Card-würdig)."
        ]
        trapping_names = []
        for lit in sorted(by_god[gott], key=str.lower):
            desc = besch.get(lit, "").strip() or "Erzählerische Wundertat (Wirkung nach Spielleiter-Entscheid)."
            besch_lines.append(f"{lit}: {desc}")
            trapping_names.append(lit)
            traps += 1
        mae[mname] = {
            "name": mname, "rang": "F", "machtpunkte": 0, "reichweite": "—", "dauer": "—",
            "beschreibung": "\n".join(besch_lines),
            "dsa_trappings": trapping_names, "effekt": "",
            "aktiv": True, "ausgewaehlt": False, "custom": False, "voraussetzungen": [],
        }

    out = json.dumps(d, ensure_ascii=False, indent=2)
    assert not out.endswith("\n")
    open(SRC, "w", encoding="utf-8").write(out)
    print(f"Mirakel-Mächte (rebuild): {len(by_god)} · Trappings: {traps}")
    print("Mirakel-Mächte:", ", ".join(f"Mirakel ({g})" for g in sorted(by_god)))


if __name__ == "__main__":
    main()
