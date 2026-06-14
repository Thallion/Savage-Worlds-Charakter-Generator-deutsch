# -*- coding: utf-8 -*-
"""
Extrahiert den Text der (englischen) SWADE Horror Companion Archetypen nach Texte/
zur Wiederverwendung (Build-Abgleich / Verifikation).

WARUM NUR -raw:
  Das PDF hat ein stark gestyltes Magazin-Layout. Getestet 2026-06-14:
    * pdftotext (default)  -> Buchstabensalat (Spaltenerkennung scheitert)
    * pdftotext -layout    -> ebenfalls unbrauchbar (Titel/Spalten zerstreut)
    * pdftotext -raw       -> Werte-/Edge-/Gear-Blöcke in LESEREIHENFOLGE (brauchbar);
                              nur die gestylten Archetyp-TITEL zerfallen teils in Einzelzeichen.
  Deshalb ist -raw die einzig sinnvolle automatische Ablage. Eine VOLLSTÄNDIGE Konsolidierung
  in strukturierte Felder ließ sich NICHT zuverlässig automatisieren (das -raw mischt
  'Agility d6' vs. 'Agility\\nd6' uneinheitlich, Banner zerfallen unregelmäßig).

  => Die maßgebliche, konsolidierte Datenfassung sind die HAND-TRANSKRIBIERTEN Python-Dicts
     in logs/build_horror_all.py (pro Archetyp: 'attribute'/'fertigkeiten'/'talente'/...).
     Dieses Skript liefert nur die rohe Textquelle zum Gegenlesen.

AUSGABE:  Texte/Horror_Companion_Archetypes_(SWADE)_raw.txt
AUFRUF :  python3 logs/extract_horror_text.py   (kein Kivy nötig)
"""
import subprocess
from pathlib import Path

PDF = Path('Texte/Horror_Companion_Archetypes_(SWADE).pdf')
RAW_OUT = Path('Texte/Horror_Companion_Archetypes_(SWADE)_raw.txt')

HEADER = (
    "# Horror Companion Archetypes (SWADE) — pdftotext -raw\n"
    "# Sprache: ENGLISCH (Original). Build-Setting 'Horror Kompendium' ist DEUTSCH -> EN->DE-Mapping nötig.\n"
    "# Quelle-PDF: Texte/Horror_Companion_Archetypes_(SWADE).pdf\n"
    "# Erzeugt von: logs/extract_horror_text.py  (nur -raw ist brauchbar, s. Skript-Header)\n"
    "# Struktur je Archetyp: Werteblock (Attr+Skills+Pace/Parry/Toughness) -> 'SKILLS/ATTRIBUTES'\n"
    "#   -> Name (gestylt, ggf. zerfallen) -> Zitat -> HINDRANCES -> EDGES -> GEAR -> (B) Advances.\n"
    "# Konsolidierte/maßgebliche Daten: hand-transkribierte Dicts in logs/build_horror_all.py.\n"
    "# ----------------------------------------------------------------------------------------\n\n"
)

def main():
    raw = subprocess.run(['pdftotext', '-raw', str(PDF), '-'],
                         capture_output=True, text=True, check=True).stdout
    RAW_OUT.write_text(HEADER + raw, encoding='utf-8')
    print(f"OK: {RAW_OUT}  ({len(raw.splitlines())} Zeilen)")

if __name__ == '__main__':
    main()
