"""
Baut das DSA-Lexikon: fetched alle Detailseiten parallel und extrahiert
Wirkung, Merkmal, Probe, Kosten, Steigerungsfaktor, Publikation.

Input: /tmp/opencode/dsa_name_list.json (von dsa_parse_auswahl.py)
Output: config/dsa_lexikon.json
"""

import json
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from time import time

NAME_LIST = Path("/tmp/opencode/dsa_name_list.json")
OUTPUT = Path("config/dsa_lexikon.json")
CACHE_DIR = Path("/tmp/opencode/dsa_detail_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
MAX_WORKERS = 12
TIMEOUT = 30

# Felder, die wir extrahieren
FELD_RE = re.compile(
    r'<div class="spalte1">([^:<]+?)\s*:?\s*</div>\s*<div>\s*(.*?)\s*</div>',
    re.DOTALL
)
HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")

FIELDS_OF_INTEREST = {
    "Wirkung": "wirkung",
    "Probe": "probe",
    "Merkmal": "merkmal",
    "Reichweite": "reichweite",
    "Wirkungsdauer": "wirkungsdauer",
    "Zielkategorie": "zielkategorie",
    "Verbreitung": "verbreitung",
    "Steigerungsfaktor": "steigerungsfaktor",
    "AsP-Kosten": "asp_kosten",
    "KaP-Kosten": "kap_kosten",
    "Ritualdauer": "ritualdauer",
    "Publikation": "publikation",
}


def clean_text(html: str) -> str:
    """Entfernt HTML-Tags und normalisiert Whitespace."""
    text = HTML_TAG_RE.sub(" ", html)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def extract_fields(html: str) -> dict[str, str]:
    """Extrahiert die interessanten Felder aus einer Detailseite."""
    result = {}
    for match in FELD_RE.finditer(html):
        label = match.group(1).strip()
        value_html = match.group(2)
        if label in FIELDS_OF_INTEREST:
            result[FIELDS_OF_INTEREST[label]] = clean_text(value_html)
    return result


def short_description(name: str, typ: str, fields: dict) -> str:
    """Erzeugt eine knappe Kurzbeschreibung."""
    wirkung = fields.get("wirkung", "")
    if wirkung:
        satz_ende = wirkung.find(". ")
        if satz_ende > 0 and satz_ende < 250:
            return wirkung[: satz_ende + 1]
        if len(wirkung) <= 200:
            return wirkung
        return wirkung[:197] + "..."
    return f"({typ} ohne Wirkungstext)"


def fetch_one(entry: dict) -> tuple[str, dict | None]:
    """Fetched eine Detailseite (mit Cache) und parst sie."""
    name = entry["name"]
    typ = entry["typ"]
    url = entry["url"]
    cache = CACHE_DIR / f"{typ}_{urllib.parse.quote(name, safe='')[:60]}.html"
    if not cache.exists():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                cache.write_bytes(r.read())
        except Exception as e:
            return name, {"error": str(e), "typ": typ, "url": url}
    try:
        html = cache.read_text(encoding="utf-8", errors="replace")
        fields = extract_fields(html)
        if "error" in fields:
            return name, {"typ": typ, "url": url, "kurzbeschreibung": "(Parser-Fehler)"}
        return name, {
            "typ": typ,
            "url": url,
            "kurzbeschreibung": short_description(name, typ, fields),
            "wirkung_voll": fields.get("wirkung", ""),
            "merkmal": fields.get("merkmal", ""),
            "probe": fields.get("probe", ""),
            "reichweite": fields.get("reichweite", ""),
            "wirkungsdauer": fields.get("wirkungsdauer", ""),
            "zielkategorie": fields.get("zielkategorie", ""),
            "verbreitung": fields.get("verbreitung", ""),
            "steigerungsfaktor": fields.get("steigerungsfaktor", ""),
            "kosten": fields.get("asp_kosten") or fields.get("kap_kosten") or "",
            "ritualdauer": fields.get("ritualdauer", ""),
            "publikation": fields.get("publikation", ""),
        }
    except Exception as e:
        return name, {"error": str(e), "typ": typ, "url": url}


def main() -> None:
    name_list = json.loads(NAME_LIST.read_text(encoding="utf-8"))
    print(f"Zu fetchen: {len(name_list)} Einträge")
    start = time()
    results: dict[str, dict] = {}
    errors = 0
    parsed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fetch_one, entry): entry for entry in name_list}
        for i, fut in enumerate(as_completed(futures), 1):
            name, data = fut.result()
            if data and "error" not in data:
                results[name] = data
                parsed += 1
            else:
                errors += 1
                if errors <= 3:
                    print(f"  Fehler bei '{name}': {data}")
            if i % 50 == 0:
                print(f"  {i}/{len(name_list)} verarbeitet ({parsed} OK, {errors} Fehler) — {time()-start:.1f}s")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    elapsed = time() - start
    print(f"\nFertig in {elapsed:.1f}s")
    print(f"Erfolgreich geparst: {parsed}/{len(name_list)}")
    print(f"Fehler: {errors}")
    print(f"Gespeichert: {OUTPUT}")
    print(f"Größe: {OUTPUT.stat().st_size:,} Bytes")


if __name__ == "__main__":
    main()
