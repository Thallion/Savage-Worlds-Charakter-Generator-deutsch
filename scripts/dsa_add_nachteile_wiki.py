#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ergänzt Handicaps aus dem DSA-Regelwiki (Nachteile), die im Setting
"Savage Aventurien" noch fehlen UND sinnvoll nach Savage Worlds übersetzbar sind.

Quelle: https://dsa.ulisses-regelwiki.de/nachteilauswahl.html (81 Nachteile)
Abgleich-Doku: logs/dsa_nachteile_abgleich.md

Bewusst NICHT übernommen: DSA-Ressourcen-Mechaniken (Niedrige Astral-/Karmalkraft,
Schwache Zaubermelodien/-tänze, Limbus-Medium, Wenige Predigten/Visionen, …), da
sie kein SW-Pendant haben, sowie alles, was bereits durch ein SW-Handicap abgedeckt
ist (siehe Abgleich-Doku).

Idempotent: bereits vorhandene Keys werden übersprungen.
"""
import json
import sys
from pathlib import Path

SETTING = Path("settings/Savage Aventurien.json")


def handicap(key, name, stufe, punkte, beschreibung):
    return key, {
        "name": name,
        "stufe": stufe,
        "punkte": punkte,
        "beschreibung": beschreibung,
        "ausgewaehlt": False,
        "aktiv": True,
        "custom": False,
    }


NEUE_HANDICAPS = [
    handicap("Hitzeempfindlich_leicht", "Hitzeempfindlich", "leicht", 1,
             "Der Charakter leidet stark unter großer Hitze. In praller Sonne, in "
             "Wüsten oder nahe Feuersglut zieht er −2 von allen Proben ab und ist "
             "doppelt so anfällig für Erschöpfung durch Hitze."),
    handicap("Kaelteempfindlich_leicht", "Kälteempfindlich", "leicht", 1,
             "Der Charakter leidet stark unter Kälte. Bei Frost, Schnee oder "
             "eisigem Wind zieht er −2 von allen Proben ab und ist doppelt so "
             "anfällig für Erschöpfung durch Kälte."),
    handicap("Farbenblind_leicht", "Farbenblind", "leicht", 1,
             "Der Charakter kann Farben nicht oder nur eingeschränkt unterscheiden. "
             "Bei Proben, die das Erkennen von Farben erfordern (Wappen, Signale, "
             "alchemistische Tinkturen u.ä.), zieht er −2 ab."),
    handicap("Schlafwandler_leicht", "Schlafwandler", "leicht", 1,
             "Der Charakter wandelt im Schlaf umher. Bei einer 1 auf einem W6 zu "
             "Beginn einer Nachtruhe steht er auf und geht schlafwandelnd umher – "
             "was ihn unbeabsichtigt in Gefahr bringen, die Wache verraten oder "
             "schlicht Gegenstände verlieren lassen kann."),
    handicap("Giftanfaellig_leicht", "Giftanfällig", "leicht", 1,
             "Der Körper des Charakters reagiert besonders heftig auf Gifte. "
             "Proben, um Giften zu widerstehen, sind um −2 erschwert, und die "
             "Wirkung erlittener Gifte ist um eine Stufe verschärft."),
    handicap("Alkoholunvertraeglich_leicht", "Unverträglichkeit gegenüber Alkohol",
             "leicht", 1,
             "Der Charakter verträgt keinen Alkohol. Schon geringe Mengen machen "
             "ihn betrunken; Proben gegen die Wirkung von Alkohol sind um −4 "
             "erschwert."),
    handicap("Strenger_Koerpergeruch_leicht", "Strenger Körpergeruch", "leicht", 1,
             "Der Charakter verströmt einen durchdringenden Eigengeruch (typisch "
             "für Orks, Achaz oder Waldmenschen). Wesen mit gutem Geruchssinn "
             "spüren ihn leichter auf (Heimlichkeit gegen sie −2), und in "
             "höfischer Gesellschaft zieht er −1 auf Überreden ab. "
             "(DSA: Stechender Orkgeruch, Raubtiergeruch, Jagdwildgeruch.)"),
    handicap("Eisenempfindlich_leicht", "Empfindlichkeit gegen Eisen", "leicht", 1,
             "Feenblütige Wesen (Elfen, Halbelfen) vertragen kaltes Eisen schlecht. "
             "Der Charakter erleidet durch Waffen und Gegenstände aus unedlem Eisen "
             "+2 Schaden und ist beim Wirken von Mächten um −2 erschwert, solange "
             "ihn unedles Metall berührt. (DSA: Empfindlichkeit unedle Metalle.)"),
]


def main():
    if not SETTING.exists():
        print(f"FEHLER: {SETTING} nicht gefunden (cwd={Path.cwd()})", file=sys.stderr)
        return 1
    data = json.loads(SETTING.read_text(encoding="utf-8"))
    handicaps = data["handicaps"]

    added, skipped = [], []
    for key, eintrag in NEUE_HANDICAPS:
        if key in handicaps or any(
            v.get("name") == eintrag["name"] and v.get("stufe") == eintrag["stufe"]
            for v in handicaps.values()
        ):
            skipped.append(key)
        else:
            handicaps[key] = eintrag
            added.append(key)

    SETTING.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Handicaps: +{len(added)} neu, {len(skipped)} übersprungen")
    for n in added:
        print(f"   + {n}")
    if skipped:
        print(f"   (übersprungen: {', '.join(skipped)})")
    print(f"\nGesamt jetzt: {len(handicaps)} Handicap-Einträge")
    return 0


if __name__ == "__main__":
    sys.exit(main())
