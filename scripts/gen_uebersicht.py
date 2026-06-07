#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generiert docs/Savage_Aventurien_Elemente_Uebersicht.md aus settings/Savage Aventurien.json.

Jeder Eintrag mit seinem mechanischen Effekt:
- Völker: positive Eigenarten, Handicaps, kompakte Mechanik-Zeile
- Talente: nach Kategorie, Effekt + Voraussetzungen
- Handicaps: Tabelle Name/Stufe/Punkte/Effekt
- Mächte: NUR der SW-Regelabschnitt (Effekt + Modifikatoren); die eingebetteten
  DSA-Trapping-Erklärungen werden abgeschnitten, DSA-Trappings nur als Namen gelistet.

Aufruf:  python scripts/gen_uebersicht.py
"""
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "settings", "Savage Aventurien.json")
OUT = os.path.join(ROOT, "docs", "Savage_Aventurien_Elemente_Uebersicht.md")

RANG = {"A": "Anfänger", "F": "Fortgeschritten", "V": "Veteran", "H": "Held", "L": "Legendär"}


def rang_lbl(r):
    return f"{r} – {RANG.get(r, r)}" if r in RANG else (r or "—")


def vor_to_str(v):
    if not v:
        return "—"

    def one(x):
        if isinstance(x, str):
            return x
        if isinstance(x, list):
            return " UND ".join(one(i) for i in x)
        if isinstance(x, dict):
            if "oder" in x:
                return "(" + " ODER ".join(one(i) for i in x["oder"]) + ")"
            return " UND ".join(one(i) for i in x.values())
        return str(x)

    return ", ".join(one(i) for i in v) if isinstance(v, list) else one(v)


def clean(s):
    return (s or "").replace("\r", "").strip()


def indent_ml(s):
    return clean(s).replace("\n", "\n    ")


def sw_regelabschnitt(beschreibung, trappings):
    """Gibt nur den SW-Regelabschnitt zurück: alles vor der ersten eingebetteten
    DSA-Trapping-Erklärung (Zeile, die mit '<Trapping-Name>:' beginnt)."""
    besch = beschreibung or ""
    tset = [t for t in (trappings or []) if t]
    if not tset:
        return clean(besch)
    lines = besch.split("\n")
    cut = len(lines)
    # Trapping-Zeile = "<Name>:" ODER "<Name> (<Zusatz>):" (längste Namen zuerst matchen)
    pat = re.compile(
        r"^(?:" + "|".join(re.escape(t) for t in sorted(tset, key=len, reverse=True))
        + r")(?: \([^)]*\))?:"
    )
    for i, line in enumerate(lines):
        if pat.match(line.strip()):
            cut = i
            break
    return clean("\n".join(lines[:cut]))


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    tal, hand, mae, vk = d["talente"], d["handicaps"], d["maechte"], d["voelker"]
    o = []
    W = o.append

    W("# Savage Aventurien — Elemente-Übersicht\n")
    W("> Automatisch generiert aus `settings/Savage Aventurien.json` "
      "(`python scripts/gen_uebersicht.py`). Jeder Eintrag mit seinem **mechanischen Effekt**.\n")
    W(f"**Setting:** {d.get('name')}  ")
    W(f"**Währung:** {d.get('waehrung')} (Silbertaler) · **Startgeld:** {d.get('startgeld')}  ")
    W(f"**Umfang:** {len(vk)} Völker · {len(tal)} Talente · {len(hand)} Handicaps · {len(mae)} Mächte\n")
    W("**Rang-Legende:** A=Anfänger · F=Fortgeschritten · V=Veteran · H=Held · L=Legendär\n")
    W("---\n## Inhalt\n\n1. [Völker](#1-völker)\n2. [Talente](#2-talente)\n"
      "3. [Handicaps](#3-handicaps)\n4. [Mächte](#4-mächte)\n\n---\n")

    # 1. VÖLKER
    W("## 1. Völker\n")
    for name in sorted(vk):
        x = vk[name]
        e = x.get("effects", {})
        W(f"### {name}\n")
        bes = x.get("besonderheiten") or []
        if bes:
            W("**Positive Eigenarten:**\n")
            for b in bes:
                W(f"- {clean(b)}")
            W("")
        else:
            W("**Positive Eigenarten:** —\n")
        hc = x.get("handicaps") or []
        if hc:
            W("**Handicaps / Nachteile:**\n")
            for h in hc:
                W(f"- {clean(h)}")
            W("")
        else:
            W("**Handicaps / Nachteile:** —\n")
        m = []
        ab = e.get("attribute_bonuses") or {}
        if ab:
            m.append("Attribut-Boni: " + ", ".join(f"{k} +{v // 2} Würfelstufe(n)" for k, v in ab.items()))
        sb = e.get("fertigkeits_startboni") or {}
        if sb:
            m.append("Fertigkeits-Start: " + ", ".join(f"{k} W{4 + v}" for k, v in sb.items()))
        mb = e.get("fertigkeits_modifier_boni") or {}
        if mb:
            m.append("Fertigkeits-Mod: " + ", ".join(f"{k} {v:+d}" for k, v in mb.items()))
        if e.get("robustheit_bonus"):
            m.append(f"Robustheit {e['robustheit_bonus']:+d}")
        if e.get("bewegungsweite_bonus"):
            m.append(f"Bewegungsweite {e['bewegungsweite_bonus']:+d}")
        if e.get("groesse_modifikator"):
            m.append(f"Größe {e['groesse_modifikator']:+d}")
        if (e.get("wahlmoeglichkeiten") or {}).get("freies_talent"):
            m.append("Freies Anfängertalent")
        if e.get("auto_talente"):
            m.append("Auto-Talente: " + ", ".join(e["auto_talente"]))
        if e.get("auto_handicaps"):
            m.append("Auto-Handicaps: " + ", ".join(e["auto_handicaps"]))
        sp = [k for k, v in (e.get("spezielle_effekte") or {}).items() if v]
        if sp:
            m.append("Spezial-Flags: " + ", ".join(sp))
        W("**Mechanik:** " + ("; ".join(m) if m else "—") + "\n")

    # 2. TALENTE
    W("---\n## 2. Talente\n")
    bk = defaultdict(list)
    for nm, t in tal.items():
        bk[t.get("kategorie", "(ohne)")].append((nm, t))
    ro = {"A": 0, "F": 1, "V": 2, "H": 3, "L": 4}
    for kat in sorted(bk, key=str.lower):
        its = sorted(bk[kat], key=lambda it: (ro.get(it[1].get("rang", ""), 9), it[0].lower()))
        W(f"### Kategorie: {kat} ({len(its)})\n")
        for nm, t in its:
            head = f"**{nm}** _(Rang {rang_lbl(t.get('rang', ''))})_"
            ex = []
            if t.get("machtpunkte"):
                ex.append(f"{t['machtpunkte']} MP")
            if t.get("neue_maechte"):
                ex.append(f"+{t['neue_maechte']} Mächte")
            if ex:
                head += " — " + ", ".join(ex)
            W(head)
            W(f"  - **Effekt:** {indent_ml(t.get('beschreibung', '')) or '—'}")
            vs = vor_to_str(t.get("voraussetzungen") or t.get("voraussetzung"))
            if vs != "—":
                W(f"  - **Voraussetzungen:** {vs}")
            W("")

    # 3. HANDICAPS  (Stufe + Punkte zu einer breiteren Spalte zusammengefasst)
    W("---\n## 3. Handicaps\n")
    W("| Handicap | Schwere | Mechanischer Effekt |\n"
      "|---|:---:|---|")
    for nm in sorted(hand, key=str.lower):
        h = hand[nm]
        stufe = h.get("stufe", "—")
        pkt = h.get("punkte", "—")
        schwere = f"{stufe} ({pkt} Pkt)" if stufe != "—" else "—"
        b = clean(h.get("beschreibung", "")).replace("\n", " ").replace("|", "/") or "—"
        W(f"| {nm} | {schwere} | {b} |")

    # 4. MÄCHTE (nur SW-Regelabschnitt; DSA-Trappings nur als Namen)
    W("\n---\n## 4. Mächte\n")
    for nm in sorted(mae, key=str.lower):
        mm = mae[nm]
        meta = [f"Rang {mm.get('rang', '—')}", f"{mm.get('machtpunkte', '?')} MP",
                f"Reichweite {clean(mm.get('reichweite', '—')) or '—'}",
                f"Dauer {clean(mm.get('dauer', '—')) or '—'}"]
        W(f"**{nm}** _({' · '.join(meta)})_")
        sw = sw_regelabschnitt(mm.get("beschreibung", ""), mm.get("dsa_trappings"))
        W(f"  - **Effekt (SW):** {indent_ml(sw) or '—'}")
        tr = mm.get("dsa_trappings") or []
        if tr:
            W(f"  - **DSA-Zauber (Trappings):** {', '.join(tr)}")
        W("")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(o))
    print(f"Geschrieben: {OUT}")
    print(f"{len(vk)} Völker · {len(tal)} Talente · {len(hand)} Handicaps · {len(mae)} Mächte · {os.path.getsize(OUT)} Bytes")


if __name__ == "__main__":
    main()
