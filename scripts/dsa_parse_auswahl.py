"""
Parst die 5 DSA-Auswahlseiten und baut eine Liste aller Namen + URL-Typ.
Kein Web-Scraping der Detailseiten — das macht build_lexikon_from_auswahl.py.
"""

import json
import re
from pathlib import Path
from urllib.parse import quote_plus

AUSWAHL_URLS = {
    "Zauber": "https://dsa.ulisses-regelwiki.de/zauberauswahl.html",
    "Ritual": "https://dsa.ulisses-regelwiki.de/ritualauswahl.html",
    "Liturgie": "https://dsa.ulisses-regelwiki.de/liturgieauswahl.html",
    "Zeremonie": "https://dsa.ulisses-regelwiki.de/zeremonieauswahl.html",
    "Segen": "https://dsa.ulisses-regelwiki.de/segenauswahl.html",
}

DETAIL_URL_TEMPLATES = {
    "Zauber": "https://dsa.ulisses-regelwiki.de/zauber.html?zauber={}",
    "Ritual": "https://dsa.ulisses-regelwiki.de/ritual.html?ritual={}",
    "Liturgie": "https://dsa.ulisses-regelwiki.de/liturgie.html?liturgie={}",
    "Zeremonie": "https://dsa.ulisses-regelwiki.de/zeremonie.html?zeremonie={}",
    "Segen": "https://dsa.ulisses-regelwiki.de/segen.html?segen={}",
}

LINK_RE = re.compile(r"<a href='(zauber|ritual|liturgie|zeremonie|segen)\.html\?\1=([^']+)'[^>]*>([^<]+)</a>")

CACHE_DIR = Path("/tmp/opencode/dsa_auswahl_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_auswahl(typ: str, url: str) -> list[tuple[str, str]]:
    cache = CACHE_DIR / f"{typ.lower()}.html"
    if not cache.exists():
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            cache.write_bytes(r.read())
    html = cache.read_text(encoding="utf-8", errors="replace")
    matches = LINK_RE.findall(html)
    out = []
    for kind, encoded, name in matches:
        out.append((name.strip(), encoded))
    return out


def build_name_list() -> dict[str, dict]:
    """{ name: {typ, encoded} }"""
    result = {}
    for typ, url in AUSWAHL_URLS.items():
        names = fetch_auswahl(typ, url)
        for name, encoded in names:
            if name in result:
                result[name]["duplicate_in"].append(typ)
            else:
                result[name] = {"typ": typ, "encoded": encoded, "duplicate_in": []}
    return result


def main() -> None:
    name_list = build_name_list()
    print(f"Eindeutige Namen: {len(name_list)}")
    by_typ = {}
    for name, info in name_list.items():
        by_typ.setdefault(info["typ"], []).append(name)
    for typ, names in by_typ.items():
        print(f"  {typ}: {len(names)}")
    duplicates = {n: i for n, i in name_list.items() if i["duplicate_in"]}
    if duplicates:
        print(f"  Duplikate: {len(duplicates)}")
        for n, i in list(duplicates.items())[:5]:
            print(f"    {n}: in {i['typ']} + {i['duplicate_in']}")
    out = Path("/tmp/opencode/dsa_name_list.json")
    out.write_text(json.dumps(
        [{"name": n, "typ": i["typ"], "encoded": i["encoded"], "url": DETAIL_URL_TEMPLATES[i["typ"]].format(i["encoded"])}
         for n, i in name_list.items()],
        ensure_ascii=False, indent=2
    ))
    print(f"Gespeichert: {out}")


if __name__ == "__main__":
    main()
