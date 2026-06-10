# functions/volk_specials.py
"""
Volk-Sonderfälle: Halbelf (Talent ODER Attribut) und Mensch (Vielseitig:
Talent oder Fertigkeitspunkte).
Teil des aufgeteilten volk_funktionen-Moduls; Fassade: functions/volk_funktionen.py
"""

import logging
import re
from kivy.logger import Logger
from functions.volk_core import (
    _get_halbelf_attribut_gewaehlt,
    _get_halbelf_freies_talent,
    _get_mensch_fertigkeitspunkte_gewaehlt,
    _get_menschen_freies_talent,
    _reset_mensch_fertigkeitspunkte,
    _reset_menschen_freies_talent,
    _set_halbelf_attribut_gewaehlt,
    _set_halbelf_freies_talent,
    _set_mensch_fertigkeitspunkte_gewaehlt,
)
from functions.volk_wahlmoeglichkeiten import (
    waehle_freies_attribut,
    waehle_freies_talent,
)


# NEUE FUNKTIONEN für Halbelf ENTWEDER/ODER Logik

def waehle_halbelf_talent(charakter, volk_name, talent_name, ignore_voraussetzungen=False):
    """
    Wählt ein freies Talent für Halbelf aus (ENTWEDER-Teil der Wahl).
    ERWEITERT: Verhindert Mehrfachauswahl und setzt Attribut-Wahl zurück.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks (sollte Halbelf sein)
        talent_name: Name des zu wählenden Talents
        ignore_voraussetzungen: Voraussetzungsprüfung überspringen (default: False)
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
        str: "needs_voraussetzungen_confirmation" wenn Voraussetzungen nicht erfüllt
    """
    try:
        Logger.debug(f"Halbelf wählt freies Talent '{talent_name}' für Volk '{volk_name}' (ignore_voraussetzungen={ignore_voraussetzungen})")
        
        if volk_name.lower() not in ["halbelf", "halbelfen"]:
            Logger.error(f"Halbelf-Talent-Wahl nur für Halbelfen, nicht für '{volk_name}'")
            return False
        
        # NEUE LOGIK: Prüfen ob bereits ein Talent gewählt wurde
        aktuelles_talent = _get_halbelf_freies_talent(charakter)
        if aktuelles_talent and aktuelles_talent != talent_name:
            Logger.info(f"Halbelf: Setze vorheriges freies Talent '{aktuelles_talent}' zurück")
            # Vorheriges Talent abwählen (inkl. AH-Effekte, Mächte, Machtpunkte)
            from functions.talent_funktionen import talent_abwaehlen
            talent_abwaehlen(charakter, aktuelles_talent)
        
        # NEUE LOGIK: Wenn Attribut bereits gewählt wurde, zurücksetzen (ENTWEDER/ODER)
        if _get_halbelf_attribut_gewaehlt(charakter):
            Logger.info("Halbelf: Setze Geschicklichkeits-Bonus zurück (ENTWEDER/ODER)")
            if hasattr(charakter, 'attribute') and 'Geschicklichkeit' in charakter.attribute:
                geschicklichkeit = charakter.attribute['Geschicklichkeit']
                if geschicklichkeit.wert == 6:  # Von W6 auf W4 zurücksetzen
                    geschicklichkeit.wert = 4
                    Logger.debug("Geschicklichkeit von W6 auf W4 zurückgesetzt")
            _set_halbelf_attribut_gewaehlt(charakter, False)
        
        # Standard Talent-Auswahl durchführen
        result = waehle_freies_talent(charakter, volk_name, talent_name, ignore_voraussetzungen)
        
        if result is True:
            # Markiere, dass Halbelf die Talent-Option gewählt hat
            _set_halbelf_freies_talent(charakter, talent_name)
            Logger.info(f"Halbelf '{volk_name}' hat freies Talent '{talent_name}' gewählt")
            return True
        elif result == "needs_voraussetzungen_confirmation":
            return "needs_voraussetzungen_confirmation"
        
        return False
        
    except Exception as e:
        Logger.error(f"Fehler bei Halbelf-Talent-Auswahl: {e}", exc_info=True)
        return False


def waehle_halbelf_attribut(charakter, volk_name):
    """
    Wählt den Geschicklichkeits-Bonus für Halbelf aus (ODER-Teil der Wahl).
    ERWEITERT: Verhindert Mehrfachauswahl und setzt Talent-Wahl zurück.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks (sollte Halbelf sein)
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.debug(f"Halbelf wählt Geschicklichkeits-Bonus für Volk '{volk_name}'")
        
        if volk_name.lower() not in ["halbelf", "halbelfen"]:
            Logger.error(f"Halbelf-Attribut-Wahl nur für Halbelfen, nicht für '{volk_name}'")
            return False
        
        # NEUE LOGIK: Prüfen ob bereits Attribut gewählt wurde
        if _get_halbelf_attribut_gewaehlt(charakter):
            Logger.info("Halbelf: Geschicklichkeits-Bonus bereits gewählt")
            return True  # Bereits gewählt, nichts zu tun
        
        # NEUE LOGIK: Wenn Talent bereits gewählt wurde, zurücksetzen (ENTWEDER/ODER)
        aktuelles_talent = _get_halbelf_freies_talent(charakter)
        if aktuelles_talent:
            Logger.info(f"Halbelf: Setze vorheriges freies Talent '{aktuelles_talent}' zurück (ENTWEDER/ODER)")
            # Talent abwählen
            if aktuelles_talent in charakter.talente:
                talent = charakter.talente[aktuelles_talent]
                talent.ausgewaehlt = False
                
                # Aus selected_talente entfernen
                if hasattr(charakter, 'selected_talente') and aktuelles_talent in charakter.selected_talente:
                    charakter.selected_talente.remove(aktuelles_talent)
                    Logger.debug(f"Talent '{aktuelles_talent}' aus selected_talente entfernt")
            _set_halbelf_freies_talent(charakter, None)
        
        # Geschicklichkeits-Bonus anwenden
        success = waehle_freies_attribut(charakter, volk_name, "Geschicklichkeit")
        
        if success:
            # Markiere, dass Halbelf die Attribut-Option gewählt hat
            _set_halbelf_attribut_gewaehlt(charakter, True)
            Logger.info(f"Halbelf '{volk_name}' hat Geschicklichkeits-Bonus gewählt")
            return True
        
        return False
        
    except Exception as e:
        Logger.error(f"Fehler bei Halbelf-Attribut-Auswahl: {e}", exc_info=True)
        return False


# NEUE FUNKTIONEN für Menschen-Vielseitig (freies Talent ODER 2 Fertigkeitspunkte)

def waehle_mensch_talent(charakter, volk_name, talent_name, ignore_voraussetzungen=False):
    """
    Wählt ein freies Talent für einen Menschen aus (Vielseitig ENTWEDER-Teil).
    Setzt ggf. vorherige Fertigkeitspunkte-Wahl zurück.

    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        talent_name: Name des zu wählenden Talents
        ignore_voraussetzungen: Voraussetzungsprüfung überspringen (default: False)

    Returns:
        bool: True bei Erfolg, False bei Fehler
        str: "needs_voraussetzungen_confirmation" wenn Voraussetzungen nicht erfüllt
    """
    try:
        Logger.debug(f"Mensch Vielseitig: Wähle freies Talent '{talent_name}' für '{volk_name}' (ignore_voraussetzungen={ignore_voraussetzungen})")

        # Fertigkeitspunkte-Wahl zurücksetzen falls vorhanden
        if _get_mensch_fertigkeitspunkte_gewaehlt(charakter):
            Logger.info("Mensch Vielseitig: Setze Fertigkeitspunkte-Wahl zurück (ENTWEDER/ODER)")
            _reset_mensch_fertigkeitspunkte(charakter)

        # Standard freies Talent auswählen
        result = waehle_freies_talent(charakter, volk_name, talent_name, ignore_voraussetzungen)

        if result is True:
            Logger.info(f"Mensch Vielseitig: Talent '{talent_name}' gewählt für '{volk_name}'")

        return result

    except Exception as e:
        Logger.error(f"Fehler bei Mensch-Vielseitig-Talent-Auswahl: {e}", exc_info=True)
        return False


def waehle_mensch_fertigkeitspunkte(charakter, volk_name):
    """
    Wählt +2 Fertigkeitspunkte für einen Menschen aus (Vielseitig ODER-Teil).
    Setzt ggf. vorherige Talent-Wahl zurück.

    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks

    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.debug(f"Mensch Vielseitig: Wähle +2 Fertigkeitspunkte für '{volk_name}'")

        # Bereits gewählt?
        if _get_mensch_fertigkeitspunkte_gewaehlt(charakter):
            Logger.info("Mensch Vielseitig: Fertigkeitspunkte bereits gewählt")
            return True

        # Talent-Wahl zurücksetzen falls vorhanden
        aktuelles_talent = _get_menschen_freies_talent(charakter)
        if aktuelles_talent:
            Logger.info(f"Mensch Vielseitig: Setze Talent '{aktuelles_talent}' zurück (ENTWEDER/ODER)")
            _reset_menschen_freies_talent(charakter)

        # +2 Fertigkeitspunkte gewähren
        if hasattr(charakter, 'verbleibende_fertigkeitssteigerungen'):
            charakter.verbleibende_fertigkeitssteigerungen += 2
            Logger.debug(f"Verbleibende Fertigkeitssteigerungen erhöht auf {charakter.verbleibende_fertigkeitssteigerungen}")
        if hasattr(charakter, 'maximale_fertigkeitssteigerungen'):
            charakter.maximale_fertigkeitssteigerungen += 2
            Logger.debug(f"Maximale Fertigkeitssteigerungen erhöht auf {charakter.maximale_fertigkeitssteigerungen}")

        # Tracking setzen
        _set_mensch_fertigkeitspunkte_gewaehlt(charakter, True)

        Logger.info(f"Mensch Vielseitig: +2 Fertigkeitspunkte gewählt für '{volk_name}'")
        return True

    except Exception as e:
        Logger.error(f"Fehler bei Mensch-Vielseitig-Fertigkeitspunkte-Auswahl: {e}", exc_info=True)
        return False
