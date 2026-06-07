#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fügt die gemappten DSA-Liturgien als Trappings (mit Kurzbeschreibung) in die
jeweilige SW-Macht von settings/Savage Aventurien.json ein.

Quelle des Mappings: LITURGIE_SW aus gen_traditionen_zauber.py.
Quelle der Kurzbeschreibung: scripts/liber_beschreibung.json (aus dem Liber Liturgium).

Idempotent: fügt eine Liturgie nur hinzu, wenn sie unter ihrer Ziel-Macht noch nicht als
Trapping vorhanden ist. Aufruf:  python scripts/add_liturgien_trappings.py
"""
import json
import os
import importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "settings", "Savage Aventurien.json")
BESCH = os.path.join(ROOT, "scripts", "liber_beschreibung.json")


def base(n):
    return n.split(" (")[0].strip()


def main():
    spec = importlib.util.spec_from_file_location("gen", os.path.join(ROOT, "scripts", "gen_traditionen_zauber.py"))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    LIT = gen.LITURGIE_SW

    besch = json.load(open(BESCH, encoding="utf-8"))
    d = json.load(open(SRC, encoding="utf-8"))
    mae = d["maechte"]

    # Validierung Ziel-Mächte
    unknown = {v for v in LIT.values() if v not in mae}
    if unknown:
        raise SystemExit(f"Unbekannte Ziel-Mächte: {sorted(unknown)}")

    import re
    added = []
    resynced = 0
    for lit, macht in sorted(LIT.items()):
        m = mae[macht]
        traps = m.setdefault("dsa_trappings", [])
        vorhanden = {base(t).lower() for t in traps}
        desc = besch.get(lit, "").strip() or f"DSA-Liturgie, abgebildet über die Macht {macht}."
        if base(lit).lower() in vorhanden:
            # bestehende Trapping-Zeile auf aktuelle (saubere) Kurzbeschreibung re-syncen
            pat = re.compile(r"^" + re.escape(lit) + r": .*$", re.M)
            neu, n = pat.subn(f"{lit}: {desc}", m["beschreibung"])
            if n and neu != m["beschreibung"]:
                m["beschreibung"] = neu
                resynced += 1
            continue
        traps.append(lit)
        m["beschreibung"] = m["beschreibung"].rstrip("\n") + f"\n{lit}: {desc}"
        added.append((macht, lit))

    out = json.dumps(d, ensure_ascii=False, indent=2)
    assert not out.endswith("\n")
    open(SRC, "w", encoding="utf-8").write(out)

    from collections import Counter
    c = Counter(macht for macht, _ in added)
    print(f"Hinzugefügt: {len(added)} Liturgie-Trappings · re-synct: {resynced}")
    for macht, n in c.most_common():
        print(f"  +{n:2}  {macht}")


if __name__ == "__main__":
    main()
