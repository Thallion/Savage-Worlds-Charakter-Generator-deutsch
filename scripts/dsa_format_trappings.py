"""
Formatiert die dsa_trappings-Listen um auf 'Name [Merkmal]: Kurzbeschreibung'
und regeneriert den Beschreibungs-Anhang.

Basiert auf config/dsa_lexikon.json (Schritt 1).
"""

import json
import re
from pathlib import Path

SETTING_PATH = Path("settings/Savage Aventurien.json")
LEXIKON_PATH = Path("config/dsa_lexikon.json")
LOG_PATH = Path("logs/dsa_trappings_format_20260602.log")
PRAEFIX = "\n\nDSA-Trappings: "
TRENNZEICHEN = ", "
SUFFIX_RE = re.compile(r"^(.+?)\s*\(([^)]+)\)\s*$")
MAX_KURZBESCHREIBUNG = 180


def lookup(name: str, lex: dict) -> tuple[dict | None, str | None]:
    """Versucht name im Lexikon zu finden, ggf. mit Suffix-Stripping.
    Gibt (lexikon-eintrag, basis-name) zurück; basis-name ist None wenn exakter Match."""
    if name in lex:
        return lex[name], None
    m = SUFFIX_RE.match(name)
    if m:
        basis = m.group(1).strip()
        if basis in lex:
            return lex[basis], basis
    return None, None


def format_trapping(name: str, lex: dict) -> str:
    """Formatiert einen Trapping-Eintrag."""
    eintrag, _ = lookup(name, lex)
    if eintrag is None:
        return name
    name_anzeige = eintrag.get("name", name)
    merkmal = eintrag.get("merkmal", "").strip()
    kurz = eintrag.get("kurzbeschreibung", "").strip()
    if not kurz:
        return name
    if len(kurz) > MAX_KURZBESCHREIBUNG:
        kurz = kurz[: MAX_KURZBESCHREIBUNG - 1] + "…"
    if merkmal:
        return f"{name} [{merkmal}]: {kurz}"
    return f"{name}: {kurz}"


def main() -> None:
    with SETTING_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    with LEXIKON_PATH.open("r", encoding="utf-8") as f:
        lex = json.load(f)

    maechte = data["maechte"]
    log_lines = []

    aktualisiert = 0
    angereichert = 0
    ohne_anreicherung = 0
    suffix_aufgelöst = 0

    for macht_name, macht in maechte.items():
        if not isinstance(macht, dict):
            continue
        trap_list = macht.get("dsa_trappings")
        if not isinstance(trap_list, list) or not trap_list:
            continue

        neue_liste = []
        for t in trap_list:
            formatted = format_trapping(t, lex)
            neue_liste.append(formatted)
            if formatted != t:
                angereichert += 1
                if t not in lex:
                    _, basis = lookup(t, lex)
                    if basis:
                        suffix_aufgelöst += 1
            else:
                ohne_anreicherung += 1

        macht["dsa_trappings"] = neue_liste

        # Beschreibungs-Anhang regenerieren
        beschreibung = macht.get("beschreibung", "")
        if "DSA-Trappings:" in beschreibung:
            idx = beschreibung.find("\n\nDSA-Trappings:")
            if idx >= 0:
                beschreibung = beschreibung[:idx]
        anhang = PRAEFIX + TRENNZEICHEN.join(neue_liste)
        macht["beschreibung"] = beschreibung + anhang
        aktualisiert += 1

    with SETTING_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log = [
        "DSA-Trappings-Formatierung — Schritt 2+3",
        "",
        f"Mächte aktualisiert: {aktualisiert}",
        f"Trappings angereichert (Treffer im Lexikon): {angereichert}",
        f"  davon Suffix-Varianten aufgelöst: {suffix_aufgelöst}",
        f"Trappings ohne Anreicherung (nicht im Wiki): {ohne_anreicherung}",
        f"  Beispiele:",
    ]
    for macht_name, macht in maechte.items():
        if not isinstance(macht, dict):
            continue
        for t in macht.get("dsa_trappings", []):
            if ":" not in t and "[" not in t and t not in lex:
                log.append(f"    - {macht_name}: {t}")
                break
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(log), encoding="utf-8")

    print(f"Mächte aktualisiert: {aktualisiert}")
    print(f"Trappings angereichert: {angereichert} (davon {suffix_aufgelöst} Suffix aufgelöst)")
    print(f"Trappings ohne Anreicherung: {ohne_anreicherung}")
    print(f"Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
