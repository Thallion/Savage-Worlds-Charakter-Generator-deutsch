"""
Migrationsskript: Trennt 'effects.groesse_modifikator' von 'effects.robustheit_bonus'
in allen settings/*.json.

Hintergrund: Bisher wurde der Größeneffekt (Mensch=0, Halbling=-1, Halbriese=+3, etc.)
direkt im Feld 'robustheit_bonus' codiert. Mit der Einführung von 'groesse' als eigenem
abgeleiteten Wert wird Größe jetzt sauber in 'groesse_modifikator' geführt; Robustheit
addiert die Größe automatisch dazu.

Vorgehen pro Volk-Eintrag:
  1. Suche im konkatenierten Text aus 'besonderheiten' und 'handicaps' nach
     "Größe ±N" (regex r'größe\\s*([+-]?\\d+)').
  2. Wenn gefunden: setze effects.groesse_modifikator = N und reduziere
     effects.robustheit_bonus um N.
  3. Wenn nicht gefunden oder groesse_modifikator bereits gesetzt: überspringen.

Das Skript ist idempotent. Es schreibt vor jeder Änderung ein *.json.bak Backup.
"""

import json
import re
import shutil
from pathlib import Path


GROESSE_PATTERN = re.compile(r'größe\s*([+-]?\d+)', re.IGNORECASE)


def extrahiere_groesse_aus_text(volk: dict) -> int | None:
    """Extrahiert Größenwert aus Besonderheiten/Handicaps. None falls nicht gefunden."""
    texte = []
    for key in ('besonderheiten', 'handicaps'):
        wert = volk.get(key, [])
        if isinstance(wert, list):
            texte.extend(str(t) for t in wert)
        elif isinstance(wert, str):
            texte.append(wert)
    text_kombiniert = ' | '.join(texte)
    match = GROESSE_PATTERN.search(text_kombiniert)
    if match:
        return int(match.group(1))
    return None


def migriere_setting(pfad: Path) -> tuple[int, list[str]]:
    """Migriert eine Setting-Datei. Returns (anzahl_geaendert, log_zeilen)."""
    with pfad.open('r', encoding='utf-8') as f:
        daten = json.load(f)

    log_zeilen = []
    voelker = daten.get('voelker', {})
    if not isinstance(voelker, dict):
        return 0, [f"  (kein 'voelker'-Block gefunden)"]

    geaendert = 0
    for volk_name, volk in voelker.items():
        if not isinstance(volk, dict):
            continue
        effects = volk.get('effects')
        if not isinstance(effects, dict):
            continue

        # Schritt 1: rb → groesse_modifikator (idempotent)
        if effects.get('groesse_modifikator', 0) == 0:
            groesse = extrahiere_groesse_aus_text(volk)
            if groesse is not None and groesse != 0:
                alter_rb = effects.get('robustheit_bonus', 0)
                effects['groesse_modifikator'] = groesse
                effects['robustheit_bonus'] = alter_rb - groesse
                log_zeilen.append(
                    f"  {volk_name}: groesse={groesse:+d}, "
                    f"robustheit_bonus {alter_rb:+d} → {effects['robustheit_bonus']:+d}"
                )
                geaendert += 1

        # Schritt 2: Doppelung mit auto_handicaps 'Klein'/'Riesig' entfernen.
        # Wenn Volk schon einen Größen-Modifikator hat, ist das auto-applizierte
        # Klein/Riesig redundant (Größe wird sonst doppelt gezählt).
        groesse_mod = effects.get('groesse_modifikator', 0)
        auto_handicaps = effects.get('auto_handicaps', [])
        if groesse_mod < 0 and 'Klein' in auto_handicaps:
            auto_handicaps.remove('Klein')
            effects['auto_handicaps'] = auto_handicaps
            log_zeilen.append(f"  {volk_name}: auto_handicap 'Klein' entfernt (redundant zu groesse_mod {groesse_mod:+d})")
            geaendert += 1
        if groesse_mod > 0 and 'Riesig' in auto_handicaps:
            auto_handicaps.remove('Riesig')
            effects['auto_handicaps'] = auto_handicaps
            log_zeilen.append(f"  {volk_name}: auto_handicap 'Riesig' entfernt (redundant zu groesse_mod {groesse_mod:+d})")
            geaendert += 1

    if geaendert > 0:
        backup = pfad.with_suffix(pfad.suffix + '.bak')
        if not backup.exists():
            shutil.copy2(pfad, backup)
        with pfad.open('w', encoding='utf-8') as f:
            json.dump(daten, f, indent=4, ensure_ascii=False)
            f.write('\n')

    return geaendert, log_zeilen


def main():
    settings_dir = Path(__file__).resolve().parents[1] / 'settings'
    if not settings_dir.is_dir():
        raise SystemExit(f"settings-Verzeichnis nicht gefunden: {settings_dir}")

    gesamt_geaendert = 0
    print(f"Migriere settings/*.json in {settings_dir}\n")
    for pfad in sorted(settings_dir.glob('*.json')):
        anzahl, log = migriere_setting(pfad)
        if anzahl > 0:
            print(f"{pfad.name}: {anzahl} Volk/Völker migriert")
            for zeile in log:
                print(zeile)
            print()
            gesamt_geaendert += anzahl
        else:
            print(f"{pfad.name}: keine Änderung")

    print(f"\nFertig. Gesamt: {gesamt_geaendert} Volk/Völker migriert.")


if __name__ == '__main__':
    main()
