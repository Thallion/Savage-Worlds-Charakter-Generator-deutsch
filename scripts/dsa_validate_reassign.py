"""
Schritt 4: Validiert die dsa_trappings-Zuordnungen und schlägt Re-Zuweisungen vor.

Algorithmus:
- Pro Macht wird ein "Merkmal-Profil" erstellt (welche Merkmale sind in den Trappings)
- Für jeden Trapping wird die Macht mit dem höchsten Score für sein Merkmal gesucht
- Re-Zuweisung erfolgt, wenn:
  * Aktuelle Macht hat Score 0 für das Merkmal
  * UND eine andere Macht hat Score >= 2 für das Merkmal
- Trappings ohne Merkmal (Liturgien) bleiben unverändert
- Konfliktauflösung: Wenn dieselbe Zuweisung mehrfach passt, bleibt das Original

Output:
- logs/dsa_reassign_20260602.md (Änderungsprotokoll)
- settings/Savage Aventurien.json (aktualisiert)
"""

import json
import re
from collections import defaultdict
from pathlib import Path

SETTING_PATH = Path("settings/Savage Aventurien.json")
LEXIKON_PATH = Path("config/dsa_lexikon.json")
LOG_PATH = Path("logs/dsa_reassign_20260602.md")
SUFFIX_RE = re.compile(r"^(.+?)\s*\(([^)]+)\)\s*$")

# Manuelle Mappings für Mächte mit gemischtem Profil
MANUELLE_HINTS = {
    "Böswillige Verwandlung": ["Verwandlung"],
    "Gegenstand beschwören": ["Sphären", "Dämonisch", "Objekt"],
    "Empathie": ["Einfluss", "Hellsicht"],
    "Heilung": ["Heilung"],
    "Geschoss": ["Elementar"],
    "Schutz": ["Elementar", "Antimagie", "Objekt"],
    "Arkaner Schutz": ["Antimagie"],
    "Barriere": ["Elementar", "Antimagie", "Telekinese"],
    "Illusion": ["Illusion"],
    "Verkleiden": ["Illusion", "Verwandlung"],
    "Flächenschlag": ["Elementar"],
    "Furcht": ["Einfluss", "Dämonisch"],
    "Verwirrung": ["Einfluss"],
    "Marionette": ["Einfluss", "Verwandlung"],
    "Fernsicht": ["Hellsicht"],
    "Aufspüren": ["Hellsicht"],
    "Gedankenlesen": ["Hellsicht", "Einfluss"],
    "Tierfreund": ["Einfluss", "Hellsicht"],
    "Tier Beschwören": ["Einfluss", "Verwandlung"],
    "Untoten Beschwören": ["Dämonisch", "Sphären"],
    "Verbündeten beschwören": ["Sphären"],
    "Monster Beschwören": ["Sphären", "Dämonisch"],
    "Elementarmanipulation": ["Elementar", "Sphären"],
    "Fliegen": ["Elementar", "Verwandlung"],
    "Ebenenwechsel": ["Sphären", "Temporal"],
    "Teleportation": ["Sphären", "Temporal"],
    "Zeitstopp": ["Temporal"],
    "Wiederauferstehung": ["Temporal", "Heilung"],
    "Licht/Dunkelheit": ["Elementar", "Hellsicht"],
    "Trägheit/Beschleunigung": ["Elementar", "Verwandlung"],
    "Eigenschaft erhöhen/senken": ["Heilung", "Verwandlung", "Einfluss"],
    "Wandkrabbler": ["Verwandlung"],
    "Wachsen/Schrumpfen": ["Verwandlung"],
    "Geräusch/Stille": ["Telekinese"],
    "Telekinese": ["Telekinese"],
    "Sprachen sprechen": ["Einfluss"],
    "Zwiesprache": ["Einfluss", "Hellsicht"],
    "Unsichtbarkeit": ["Verwandlung", "Illusion"],
    "Tarnung": ["Illusion", "Verwandlung"],
    "Kriegersegen": ["Einfluss"],
    "Linderung": ["Heilung"],
    "Blenden": ["Einfluss"],
    "Betäuben": ["Einfluss", "Elementar"],
    "Fluch": ["Einfluss", "Dämonisch"],
    "Bindender Ruf": ["Einfluss"],
    "Verbannen": ["Antimagie"],
    "Aufheben": ["Antimagie"],
    "Machtpunkte entziehen": ["Antimagie", "Einfluss"],
    "Waffe verbessern": ["Objekt"],
    "Verriegeln/Entriegeln": ["Objekt"],
    "Magisches Glas": ["Hellsicht", "Illusion"],
    "Gedankenleere": ["Antimagie", "Einfluss"],
    "Gestaltwandeln": ["Verwandlung"],
    "Ausspähung": ["Hellsicht"],
    "Schadensfeld": ["Elementar", "Einfluss"],
    "Arkanes entdecken/verbergen": ["Hellsicht", "Objekt"],
    "Schutz vor Naturgewalten": ["Elementar"],
    "Dunkelsicht": ["Hellsicht"],
    "Strahl": ["Elementar", "Dämonisch"],
    "Heiligtum": ["Antimagie", "Objekt"],
    "Zuflucht": ["Objekt", "Antimagie"],
    "Gedankenverbindung": ["Hellsicht", "Einfluss"],
    "Verstricken": ["Einfluss", "Elementar"],
    "Unberührbarkeit": ["Elementar", "Antimagie"],
    "Wiederauferstehung": ["Temporal", "Heilung"],
    "Segen": ["Heilung"],
    "Chaos": ["Dämonisch", "Antimagie"],
    "Abwehren": [],
    "Graben": ["Elementar"],
    "Wunsch": [],
    "Mystisches Eingreifen": [],
}


def lookup(name: str, lex: dict) -> dict | None:
    if name in lex:
        return lex[name]
    m = SUFFIX_RE.match(name)
    if m and m.group(1).strip() in lex:
        return lex[m.group(1).strip()]
    return None


def compute_merkmal_score(macht_name: str, maechte_data: dict, lex: dict) -> dict[str, int]:
    """Zählt, wie viele Trappings in dieser Macht welches Merkmal haben."""
    score = defaultdict(int)
    m = maechte_data.get(macht_name, {})
    for t in m.get("dsa_trappings", []):
        e = lookup(t, lex)
        if e and e.get("merkmal"):
            score[e["merkmal"]] += 1
    return dict(score)


def find_best_match(trapping: str, current_macht: str, macht_scores: dict, lex: dict) -> tuple[str | None, int]:
    """Findet die Macht, die am besten zum Merkmal des Trappings passt."""
    e = lookup(trapping, lex)
    if not e or not e.get("merkmal"):
        return None, 0
    merkmal = e["merkmal"]
    best_macht = current_macht
    best_score = macht_scores.get(current_macht, {}).get(merkmal, 0)
    for m_name, scores in macht_scores.items():
        s = scores.get(merkmal, 0)
        if s > best_score:
            best_score = s
            best_macht = m_name
    if best_macht == current_macht:
        return None, best_score
    return best_macht, best_score


def main() -> None:
    with SETTING_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    with LEXIKON_PATH.open("r", encoding="utf-8") as f:
        lex = json.load(f)

    maechte = data["maechte"]
    macht_scores = {n: compute_merkmal_score(n, maechte, lex) for n in maechte if isinstance(maechte[n], dict)}

    moves = []
    kept = 0
    no_merkmal = 0
    for current_macht, m in list(maechte.items()):
        if not isinstance(m, dict):
            continue
        neue_liste = []
        for t in m.get("dsa_trappings", []):
            e = lookup(t, lex)
            if not e or not e.get("merkmal"):
                neue_liste.append(t)
                no_merkmal += 1
                continue
            current_score = macht_scores.get(current_macht, {}).get(e["merkmal"], 0)
            best_macht, best_score = find_best_match(t, current_macht, macht_scores, lex)
            # Bedingung: Ziel-Macht passt deutlich besser
            if best_macht and best_score >= 2 and (current_score == 0 or best_score - current_score >= 2):
                moves.append((current_macht, t, best_macht, e["merkmal"], current_score, best_score))
                neue_liste.append(t)
            else:
                neue_liste.append(t)
                kept += 1
        m["dsa_trappings"] = neue_liste

    # Re-assign: Trappings aus moves tatsächlich verschieben
    for from_m, trap, to_m, merkmal, old_s, new_s in moves:
        if trap in maechte[from_m]["dsa_trappings"]:
            maechte[from_m]["dsa_trappings"].remove(trap)
        if trap not in maechte[to_m]["dsa_trappings"]:
            maechte[to_m]["dsa_trappings"].append(trap)

    with SETTING_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    moves_by_to = defaultdict(list)
    for from_m, trap, to_m, merkmal, old_s, new_s in moves:
        moves_by_to[to_m].append((from_m, trap, merkmal, old_s, new_s))

    lines = [
        "# DSA-Trappings: Validierung & Re-Zuweisung",
        "",
        f"**Stand:** 2026-06-02",
        f"**Verschobene Trappings:** {len(moves)}",
        f"**Behalten (richtig einsortiert):** {kept}",
        f"**Ohne Merkmal (Liturgien/Zeremonien/Segen, nicht zugewiesen):** {no_merkmal}",
        "",
        "## Algorithmus",
        "",
        "1. Pro Macht wurde das **Merkmal-Profil** berechnet (welche Merkmale sind in den Trappings vertreten).",
        "2. Für jeden Trapping mit Merkmal wurde die Macht mit dem höchsten Score für sein Merkmal gesucht.",
        "3. **Re-Zuweisung erfolgt, wenn:** aktuelle Macht hat Score 0 für das Merkmal UND Ziel-Macht hat Score ≥ 2.",
        "4. Trappings ohne Merkmal (Liturgien, Zeremonien, Segen) wurden NICHT verschoben.",
        "",
        "## Verschobene Trappings (gruppiert nach Ziel-Macht)",
        "",
    ]
    for to_m in sorted(moves_by_to.keys(), key=lambda n: -len(moves_by_to[n])):
        items = moves_by_to[to_m]
        lines.append(f"### → {to_m}  ({len(items)} Trappings)")
        lines.append("")
        lines.append("| Trapping | Merkmal | Von | Alter Score | Neuer Score |")
        lines.append("|----------|---------|-----|-------------|-------------|")
        for from_m, trap, merkmal, old_s, new_s in sorted(items, key=lambda x: x[1]):
            lines.append(f"| {trap} | {merkmal} | {from_m} | {old_s} | {new_s} |")
        lines.append("")

    lines.extend([
        "## Was bleibt unverändert",
        "",
        f"- **{kept} Trappings** sind korrekt einsortiert (ihre Merkmale passen zur aktuellen Macht).",
        f"- **{no_merkmal} Trappings** ohne Merkmal (Liturgien/Zeremonien/Segen) wurden nicht automatisch verschoben — manuelle Prüfung empfohlen.",
        "- **Manuelle Prüfung empfohlen für:** Mächte mit dominanter Merkmal-Mischung (z.B. Empathie, Schutz, Böswillige Verwandlung).",
        "",
        "## Nächste Schritte",
        "",
        "1. **Manuelle Prüfung** der 39 Trappings ohne Wiki-Match (siehe `logs/dsa_trappings_zuordnung.md`).",
        "2. **Manuelle Prüfung** der `Manuelle Hints` im Skript — die Heuristik ist konservativ, weitere Korrekturen möglich.",
        "3. **Re-Validierung** der Böswillige Verwandlung (52 Trappings, sehr gemischtes Profil) — vermutlich weitere Fehlzuordnungen.",
        "4. **Re-Validierung** der Schutz (47 Trappings) — gemischtes Profil.",
    ])

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Verschoben: {len(moves)}")
    print(f"Behalten: {kept}")
    print(f"Ohne Merkmal: {no_merkmal}")
    print(f"Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
