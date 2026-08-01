"""
Effekt-Registry für abgeleitete Werte.

Lädt config/abgeleitete_effekte.json (Talent- und Handicap-Effekte auf
Parade, Bewegungsweite, Größe, Robustheit, Bennys, Traglast) und stellt
die beiden Summier-Funktionen bereit, die functions/abgeleitete_werte.py
und die Traglast-Berechnung verwenden.

Semantik (siehe auch _kommentar in der JSON):
- Talent-Boni sind additiv. Talente mit derselben nicht_kumulativ_gruppe
  zählen nur mit dem Maximum der Gruppe (bildet sowohl die frühere
  elif-Logik (Lieblingswaffe-Paar) als auch die oder-Logik (Behände/Flink)
  exakt ab).
- bedingung ist eine geschlossene, im Aufrufer ausgewertete Menge;
  der Effekt zählt nur, wenn die Bedingung als erfüllt übergeben wird.
- Handicap-Effekte werden über exakten name- und stufe-Lookup ermittelt;
  der Schlüssel alle_stufen gilt stufenunabhängig.
- pro_setting ersetzt für das genannte Setting den kompletten Stufen-Block,
  weil gleichnamige Handicaps settingabhängig anderes bedeuten können
  (SWAE: Zerbrechlich = +1 Schaden, Savage Pathfinder: -1 Robustheit).
"""

import json
import os
from pathlib import Path
from kivy.logger import Logger

_registry = None


def lade_abgeleitete_effekte():
    """Lädt die Effekt-Registry (mit Modul-Cache)."""
    global _registry
    if _registry is None:
        registry_pfad = Path(__file__).parent.parent / 'config' / 'abgeleitete_effekte.json'
        try:
            if os.path.exists(registry_pfad):
                with open(registry_pfad, 'r', encoding='utf-8') as f:
                    _registry = json.load(f)
                Logger.info(f"Effekt-Registry geladen von {registry_pfad}")
            else:
                Logger.error(f"Effekt-Registry nicht gefunden: {registry_pfad}")
                _registry = {"talente": {}, "handicaps": {}}
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Effekt-Registry: {e}")
            _registry = {"talente": {}, "handicaps": {}}
    return _registry


def summiere_talent_bonus(selected_talente, wert, bedingungen=None):
    """
    Summiert die Boni der gewählten Talente auf einen abgeleiteten Wert.

    Args:
        selected_talente: Liste der gewählten Talent-Namen
        wert: Name des abgeleiteten Werts ('parade', 'bewegungsweite',
              'groesse', 'robustheit', 'bennys', 'traglast_kg')
        bedingungen: Dict {bedingungs_name: bool} für bedingte Effekte
                     (z.B. {'keine_getragene_ruestung': True})

    Returns:
        int: Gesamtbonus (Gruppen-Talente nur mit dem Maximum der Gruppe)
    """
    talent_effekte = lade_abgeleitete_effekte().get('talente', {})
    bedingungen = bedingungen or {}
    summe = 0
    gruppen_maxima = {}

    for talent_name in selected_talente:
        effekt = talent_effekte.get(talent_name)
        if not effekt or wert not in effekt:
            continue
        bedingung = effekt.get('bedingung')
        if bedingung and not bedingungen.get(bedingung, False):
            continue
        bonus = effekt[wert]
        gruppe = effekt.get('nicht_kumulativ_gruppe')
        if gruppe:
            gruppen_maxima[gruppe] = max(gruppen_maxima.get(gruppe, bonus), bonus)
        else:
            summe += bonus

    return summe + sum(gruppen_maxima.values())


def summiere_handicap_bonus(charakter, wert):
    """
    Summiert die Boni/Mali der gewählten Handicaps auf einen abgeleiteten Wert.

    Args:
        charakter: Charakterobjekt (selected_handicaps + handicaps-Dict)
        wert: Name des abgeleiteten Werts (negative Werte = Malus)

    Returns:
        int: Gesamtbonus (kann negativ sein)
    """
    handicap_effekte = lade_abgeleitete_effekte().get('handicaps', {})
    setting_name = getattr(charakter, 'active_setting_name', '') or ''
    summe = 0

    for handicap_key in charakter.selected_handicaps:
        handicap = charakter.handicaps.get(handicap_key) if hasattr(charakter.handicaps, 'get') else None
        if handicap is None:
            continue
        eintrag = handicap_effekte.get(handicap.name)
        if not eintrag:
            continue
        # Gleichnamige Handicaps bedeuten je nach Setting Verschiedenes
        eintrag = (eintrag.get('pro_setting') or {}).get(setting_name) or eintrag
        effekt = eintrag.get(handicap.stufe) or eintrag.get('alle_stufen') or {}
        summe += effekt.get(wert, 0)

    return summe
