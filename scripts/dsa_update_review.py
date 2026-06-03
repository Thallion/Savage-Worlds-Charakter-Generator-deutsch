"""
Pflegt das Entscheidungs-Log für die Trappings-Re-Zuweisung.
Liest/schreibt logs/dsa_decisions.json und aktualisiert einen Header
in logs/dsa_trappings_zuordnung.md.
"""

import json
from pathlib import Path
from datetime import datetime

DECISIONS_PATH = Path("logs/dsa_decisions.json")
MARKDOWN_PATH = Path("logs/dsa_trappings_zuordnung.md")


def load_decisions() -> dict:
    if DECISIONS_PATH.exists():
        return json.loads(DECISIONS_PATH.read_text(encoding="utf-8"))
    return {
        "meta": {
            "erstellt": "2026-06-02",
            "quelle_setting": "settings/Savage Aventurien.json",
            "status": "in Bearbeitung — JSON noch nicht geändert",
        },
        "entscheidungen": [],
    }


def save_decisions(d: dict) -> None:
    d["meta"]["letzte_aktualisierung"] = datetime.now().isoformat(timespec="seconds")
    DECISIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DECISIONS_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def add_decision(d: dict, von: str, trapping: str, nach: str | None, status: str, batch: int) -> None:
    d["entscheidungen"].append({
        "batch": batch,
        "von": von,
        "trapping": trapping,
        "nach": nach,
        "status": status,  # "move" | "loeschen" | "offen"
    })


def render_header(d: dict) -> str:
    """Erzeugt den Markdown-Header mit allen Entscheidungen."""
    lines = [
        "# DSA-Trappings: Zuordnungs-Review (in Bearbeitung)",
        "",
        f"**Stand:** {d['meta'].get('letzte_aktualisierung', '2026-06-02')}",
        f"**Quelle:** `config/dsa_lexikon.json` (684 Einträge aus dsa.ulisses-regelwiki.de)",
        f"**Setting:** `settings/Savage Aventurien.json` (73 Mächte, davon 70 mit Trappings)",
        f"**Status:** ⏳ JSON noch NICHT geändert — wird am Ende in einem Schwung aktualisiert.",
        "",
        "**Arbeitsweise:** Manuelle Validierung in kleinen Batches (5-10 Trappings). Bei Unklarheit: `OFFEN`. Bei `löschen`: Trapping wird komplett entfernt. Bei `→ MACHT`: Trapping wird beim JSON-Update in die Ziel-Macht verschoben.",
        "",
        "**Format der Trapping-Zeile:** `Name [Merkmal]: Beschreibung` — Merkmal zeigt die magische Kategorie.",
        "",
        "**Legende Status:**",
        "- ✅ JA — Move-Entscheidung getroffen",
        "- ❌ NEIN — explizit abgelehnt (z.B. Böswillige Verwandlung passt nicht)",
        "- ⏸ OFFEN — keine Entscheidung, bleibt im aktuellen Zustand",
        "- 🗑 LÖSCHEN — Trapping wird komplett entfernt",
        "",
        "---",
        "",
        "## Entscheidungs-Log (laufend)",
        "",
        "| Batch | Trapping | Von | Nach | Status |",
        "|-------|----------|-----|------|--------|",
    ]
    by_status = {"move": "✅", "move_bedingt": "⚠️", "nein": "❌", "offen": "⏸", "loeschen": "🗑", "bestaetigt": "✓"}
    for e in d["entscheidungen"]:
        status_icon = by_status.get(e["status"], "?")
        nach = e["nach"] or "—"
        lines.append(f"| {e['batch']} | {e['trapping']} | {e['von']} | {nach} | {status_icon} {e['status']} |")
    lines.extend([
        "",
        "**Statistik:**",
    ])
    moves = sum(1 for e in d["entscheidungen"] if e["status"] == "move")
    deletes = sum(1 for e in d["entscheidungen"] if e["status"] == "loeschen")
    opens = sum(1 for e in d["entscheidungen"] if e["status"] == "offen")
    lines.append(f"- ✅ Moves: {moves}")
    lines.append(f"- 🗑 Löschungen: {deletes}")
    lines.append(f"- ⏸ Offen: {opens}")
    lines.extend([
        "",
        "---",
        "",
        "## Original-Zuordnungen (zur Review)",
        "",
        "Die folgenden Abschnitte zeigen die **Original-Trappings** im Setting. Die oben dokumentierten `→` Moves werden beim JSON-Update am Ende angewendet.",
        "",
    ])
    return "\n".join(lines)


def update_markdown(d: dict, original_body: str) -> None:
    """Schreibt das Markdown mit Header + Original-Body."""
    header = render_header(d)
    full = header + original_body
    MARKDOWN_PATH.write_text(full, encoding="utf-8")
    print(f"Aktualisiert: {MARKDOWN_PATH} ({len(full):,} Zeichen)")


def main() -> None:
    import sys
    if len(sys.argv) >= 6:
        batch = int(sys.argv[1])
        von = sys.argv[2]
        trapping = sys.argv[3]
        nach = sys.argv[4] if sys.argv[4] != "-" else None
        status = sys.argv[5]
        d = load_decisions()
        add_decision(d, von, trapping, nach, status, batch)
        save_decisions(d)
        body_path = Path("logs/dsa_trappings_zuordnung_body.md")
        if body_path.exists():
            update_markdown(d, body_path.read_text(encoding="utf-8"))
            print(f"Decision hinzugefügt: {trapping} von {von} → {nach} ({status})")
        else:
            print("Body-Datei nicht gefunden — nur JSON aktualisiert")
    else:
        if MARKDOWN_PATH.exists():
            text = MARKDOWN_PATH.read_text(encoding="utf-8")
            marker = "## Abwehren"
            idx = text.find(marker)
            if idx > 0:
                body = text[idx - 3:]
                Path("logs/dsa_trappings_zuordnung_body.md").write_text(body, encoding="utf-8")
                print(f"Body extrahiert: logs/dsa_trappings_zuordnung_body.md ({len(body):,} Zeichen)")
        d = load_decisions()
        body = Path("logs/dsa_trappings_zuordnung_body.md").read_text(encoding="utf-8") if Path("logs/dsa_trappings_zuordnung_body.md").exists() else ""
        update_markdown(d, body)


if __name__ == "__main__":
    main()
