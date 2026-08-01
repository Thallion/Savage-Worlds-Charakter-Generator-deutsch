"""
Migrationen für gespeicherte Charakterdaten.

Wird beim Laden auf das rohe Save-Dictionary angewendet (bevor Handicaps,
Talente & Co. gegen das Setting aufgelöst werden), damit Bestandscharaktere
Regeländerungen automatisch mitbekommen.

Zwei Arten von Migrationen:

1. Namensumbenennungen sind von sich aus wiederholbar (ein bereits neuer Name
   wird nicht noch einmal ersetzt) und laufen bei jedem Laden.
2. Wertkorrekturen dürfen nur EINMAL laufen. Sie tragen eine ID und werden in
   daten['migrationen'] vermerkt; die Liste wird mitgespeichert. Neue
   Charaktere starten mit allen IDs (siehe MIGRATIONS_IDS), für sie ist nichts
   nachzuholen.
"""

from kivy.logger import Logger

# Savage Pathfinder und Savage Aventurien führten dasselbe Handicap doppelt.
# Beide heißen jetzt "Größe -1" und wirken über groesse: -1 (die kleinen
# Völker haben dafür groesse_modifikator 0, sonst zählte die Größe doppelt).
GROESSE_ALT_NAMEN = (
    "Größe -1 (Reduzierte Robustheit)",
    "Größe -1 (Reduzierte Größe und Robustheit)",
)
GROESSE_NEU = "Größe -1"

# Wertkorrekturen: ID -> Beschreibung (Reihenfolge = Ausführungsreihenfolge)
MIGRATIONS_IDS = ("berserker_temporaer",)


def migriere_charakter_daten(daten):
    """
    Wendet alle fälligen Migrationen auf ein Save-Dictionary an.

    Args:
        daten: Das rohe Charakter-Dictionary aus der JSON-Datei (wird in place
               geändert)

    Returns:
        bool: True, wenn etwas geändert wurde
    """
    if not isinstance(daten, dict):
        return False

    geaendert = _migriere_groesse_handicap(daten)

    erledigt = list(daten.get('migrationen') or [])
    if 'berserker_temporaer' not in erledigt:
        if _migriere_berserker(daten):
            geaendert = True
        erledigt.append('berserker_temporaer')
        daten['migrationen'] = erledigt
        geaendert = True

    return geaendert


def _umbenennen_liste(werte, alt_namen, neu):
    """Alte Namen ersetzen und dabei entstehende Duplikate entfernen."""
    ergebnis = []
    geaendert = False
    for wert in werte:
        if wert in alt_namen:
            wert = neu
            geaendert = True
        if wert == neu and neu in ergebnis:
            continue
        ergebnis.append(wert)
    return ergebnis, geaendert


def _umbenennen_dict(tabelle, alt_namen, neu):
    """Nach Namen geschlüsselte Tabelle umbenennen (in place, Reihenfolge bleibt;
    ein bereits vorhandener Eintrag unter dem neuen Namen gewinnt)."""
    if not any(alt in tabelle for alt in alt_namen):
        return False

    umbenannt = {}
    for key, eintrag in list(tabelle.items()):
        if key in alt_namen:
            key = neu
            if isinstance(eintrag, dict) and eintrag.get('name') in alt_namen:
                eintrag = {**eintrag, 'name': neu}
        umbenannt.setdefault(key, eintrag)

    tabelle.clear()
    tabelle.update(umbenannt)
    return True


def _migriere_groesse_handicap(daten):
    """Führt die beiden alten "Größe -1"-Handicaps zu einem zusammen."""
    geaendert = False

    if isinstance(daten.get('selected_handicaps'), list):
        daten['selected_handicaps'], g = _umbenennen_liste(
            daten['selected_handicaps'], GROESSE_ALT_NAMEN, GROESSE_NEU
        )
        geaendert = geaendert or g

    elemente = daten.get('selected_elements') or {}
    if isinstance(elemente.get('handicaps'), dict):
        geaendert = _umbenennen_dict(
            elemente['handicaps'], GROESSE_ALT_NAMEN, GROESSE_NEU
        ) or geaendert

    if geaendert:
        Logger.info(f"Migration: Handicap auf '{GROESSE_NEU}' vereinheitlicht")
    return geaendert


def _migriere_berserker(daten):
    """
    Nimmt die dauerhaft gebuchte Stärke-Erhöhung von "Berserker" zurück.

    Berserker gibt +1 Würfeltyp Stärke ausschließlich während des
    Berserkerrauschs — die Basiswerte bleiben unverändert. Früher wurde der
    Bonus beim Wählen des Talents fest in das Attribut geschrieben.
    """
    if 'Berserker' not in (daten.get('selected_talente') or []):
        return False

    attribut = (daten.get('attribute') or {}).get('Stärke')
    if not isinstance(attribut, dict):
        return False

    wert = attribut.get('wert', 4)
    modifier = attribut.get('modifier', 0)

    # Gegenstück zu Wuerfel.increase(): erst der Modifier über W12, dann der
    # Würfeltyp; unter W4 kann nicht gesenkt werden (Attribut-Würfel)
    if wert == 12 and modifier > 0:
        attribut['modifier'] = modifier - 1
    elif wert > 4:
        attribut['wert'] = wert - 2
    else:
        Logger.warning(
            "Migration 'Berserker': Stärke steht bereits auf dem Minimum, "
            "die Erhöhung wird nicht zurückgenommen"
        )
        return False

    Logger.info(
        f"Migration 'Berserker': Stärke W{wert}{modifier:+d} -> "
        f"W{attribut.get('wert')}{attribut.get('modifier', 0):+d} "
        "(Bonus gilt nur im Berserkerrausch)"
    )
    return True
