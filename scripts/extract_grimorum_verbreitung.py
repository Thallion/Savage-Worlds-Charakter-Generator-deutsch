#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrahiert je Zauberspruch die 'Verbreitung' (Traditionen) aus Grimorum Cantiones.

Schreibt den Cache `scripts/grimorum_verbreitung.json` ({Zaubername: "Trad1, Trad2, ..."}).
Nur einmal nötig (bzw. wenn sich das PDF ändert). Der Doc-Generator
`gen_traditionen_zauber.py` liest diesen Cache, statt das große PDF zu parsen.

Methode: pdftotext (ohne -layout, Lesereihenfolge). Jeder Zaubereintrag beginnt mit einem
Drop-Cap-Header (Großbuchstabe auf eigener Zeile, Leerzeile, dann der Namensrest auf eigener
Zeile). Ab dem Header wird die folgende 'Verbreitung:'-Zeile gelesen (inkl. Zeilenumbruch-Wrap
bis 'Steigerungsfaktor:').

Aufruf:  python scripts/extract_grimorum_verbreitung.py
"""
import os
import re
import subprocess
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "Texte", "Grimorum_Cantiones.pdf")
OUT = os.path.join(ROOT, "scripts", "grimorum_verbreitung.json")


def main():
    if not os.path.exists(PDF):
        sys.exit(f"PDF nicht gefunden: {PDF}")
    txt = subprocess.run(["pdftotext", PDF, "-"], capture_output=True, text=True).stdout
    lines = txt.split("\n")
    N = len(lines)

    def find_verbr(start):
        for k in range(start, min(N, start + 90)):
            m = re.match(r"^Verbreitung:\s*(.*)$", lines[k])
            if m and "Hier wird angegeben" not in lines[k]:
                val = [m.group(1).strip()]
                j = k + 1
                while j < N and not lines[j].startswith("Steigerungsfaktor") and j - k < 6:
                    if not lines[j].strip():
                        break
                    val.append(lines[j].strip())
                    j += 1
                return " ".join(val).strip().rstrip(",")
        return None

    hdr = {}
    for i in range(N - 2):
        if re.fullmatch(r"[A-ZÄÖÜ]", lines[i].strip()) and lines[i + 1].strip() == "" and lines[i + 2].strip():
            cont = lines[i + 2].strip()
            if re.match(r"^[a-zäöü]", cont) and len(cont) < 40 and ":" not in cont:
                name = lines[i].strip() + cont
                v = find_verbr(i + 3)
                if v and name not in hdr:
                    hdr[name] = v

    json.dump(hdr, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    print(f"Geschrieben: {OUT}  ({len(hdr)} Zauber mit Verbreitung)")


if __name__ == "__main__":
    main()
