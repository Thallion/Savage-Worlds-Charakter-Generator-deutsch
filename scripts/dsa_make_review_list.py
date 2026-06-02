"""
Erzeugt eine formatierte Diskussions-Liste (Markdown) aller DSA-Trappings
mit Name / Merkmal / Kurzbeschreibung — separat vom JSON, nur für Review.

Output: logs/dsa_trappings_zuordnung.md
"""

import json
import re
from pathlib import Path
from collections import defaultdict

SETTING_PATH = Path("settings/Savage Aventurien.json")
LEXIKON_PATH = Path("config/dsa_lexikon.json")
OUTPUT = Path("logs/dsa_trappings_zuordnung.md")
SUFFIX_RE = re.compile(r"^(.+?)\s*\(([^)]+)\)\s*$")

WIRKUNGS_MAX = 220


def lookup(name: str, lex: dict) -> dict | None:
    if name in lex:
        return lex[name]
    m = SUFFIX_RE.match(name)
    if m and m.group(1).strip() in lex:
        return lex[m.group(1).strip()]
    return None


def render_trapping(name: str, lex: dict) -> str:
    """Markdown-Zeile für ein Trapping."""
    eintrag = lookup(name, lex)
    if eintrag is None:
        return f"- **{name}** — ⚠️ nicht im Wiki-Lexikon"
    merkmal = eintrag.get("merkmal", "").strip() or "—"
    typ = eintrag.get("typ", "?")
    wirkung = eintrag.get("wirkung_voll", "").strip()
    if len(wirkung) > WIRKUNGS_MAX:
        wirkung = wirkung[:WIRKUNGS_MAX - 1] + "…"
    return f"- **{name}** (`{typ}`, Merkmal *{merkmal}*)\n  {wirkung}"


def main() -> None:
    with SETTING_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    with LEXIKON_PATH.open("r", encoding="utf-8") as f:
        lex = json.load(f)

    maechte = data["maechte"]
    lines = [
        "# DSA-Trappings: Zuordnungs-Review",
        "",
        "**Stand:** 2026-06-02",
        "**Quelle:** `config/dsa_lexikon.json` (684 Einträge aus dsa.ulisses-regelwiki.de)",
        "**Setting:** `settings/Savage Aventurien.json` (73 Mächte, davon 70 mit Trappings)",
        "",
        "**Ziel:** Pro Macht die zugeordneten DSA-Trappings mit **Name / Merkmal / Kurzbeschreibung** prüfen.",
        "**Format:** `Name [Merkmal]: Beschreibung` — Merkmal zeigt die magische Kategorie und hilft bei der Zuordnung.",
        "",
        "**Legende Status:**",
        "- ✅ OK — passt zur SW-Macht",
        "- ⚠️ Prüfen — Merkmal passt nicht offensichtlich",
        "- ❌ Falsch — sollte woanders einsortiert werden",
        "",
        "---",
        "",
    ]

    for macht_name, macht in maechte.items():
        if not isinstance(macht, dict):
            continue
        trap_list = macht.get("dsa_trappings")
        if not isinstance(trap_list, list) or not trap_list:
            continue

        beschreibung = macht.get("beschreibung", "").split("\n\nDSA-Trappings:")[0]
        rang = macht.get("rang", "?")
        mp = macht.get("machtpunkte", "?")

        lines.append(f"## {macht_name}  ·  Rang {rang}  ·  {mp} MP")
        lines.append("")
        lines.append(f"> {beschreibung}")
        lines.append("")
        for t in trap_list:
            lines.append(render_trapping(t, lex))
        lines.append("")
        lines.append("**Status:** ⬜ ungeprüft  ✅ OK  ⚠️ prüfen  ❌ falsch")
        lines.append("")
        lines.append("---")
        lines.append("")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Geschrieben: {OUTPUT} ({OUTPUT.stat().st_size:,} Bytes, {len(lines)} Zeilen)")


if __name__ == "__main__":
    main()
