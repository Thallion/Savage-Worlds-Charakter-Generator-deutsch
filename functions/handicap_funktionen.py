"""
Modul für die Verwaltung von Handicaps im Charakter.
Dieses Modul enthält Funktionen zur Verwaltung von Handicaps, einschließlich
des Auswahlens, Abwählens und Speicherns benutzerdefinierter Handicaps.
"""

import json
import os
from kivy.logger import Logger
from models.handicap import Handicap


def initialisiere_handicaps(charakter, handicap_daten):
    """
    Initialisiert die Handicaps des Charakters basierend auf der bereitgestellten Liste.
    
    Args:
        charakter: Das Charakter-Objekt, dem die Handicaps hinzugefügt werden sollen
        handicap_daten: Die Handicap-Daten als Liste von Dictionaries
    """
    charakter.handicaps = {}
    try:
        for daten in handicap_daten:
            name = daten.get('Name', '')
            stufe = daten.get('Stufe', '').lower()
            beschreibung = daten.get('Beschreibung', 'Keine Beschreibung verfügbar')

            # Immer ein eindeutiger Schlüssel mit Name und Stufe
            name_key = f"{name} ({stufe})"

            # Initialisiere das Handicap
            handicap = charakter.Handicap(
                name=name,  # Name ohne Stufe
                stufe=stufe,
                beschreibung=beschreibung
            )
            charakter.handicaps[name_key] = handicap
        Logger.debug("Handicaps erfolgreich initialisiert.")
    except Exception as e:
        Logger.error(f"Fehler bei der Initialisierung der Handicaps: {e}")


def waehle_handicap(charakter, handicap_name_key):
    """
    Wählt ein Handicap aus und verrechnet die Handicap-Punkte.
    
    Args:
        charakter: Das Charakter-Objekt
        handicap_name_key: Der Schlüssel des Handicaps in der handicaps-Dictionary
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if handicap_name_key in charakter.handicaps:
        handicap = charakter.handicaps[handicap_name_key]
        if not handicap.ausgewaehlt:
            neue_gesamtpunkte = charakter.gesamt_handicap_punkte + handicap.punkte     
            Logger.info(f"neue_gesamtpunkte '{neue_gesamtpunkte} Kosten: {handicap.punkte} Gesamt {charakter.gesamt_handicap_punkte}")
            if neue_gesamtpunkte <= 4:           
                handicap.auswaehlen()
                charakter.gesamt_handicap_punkte = neue_gesamtpunkte
                charakter.verbleibende_handicap_punkte += handicap.punkte  
                charakter.verbleibende_handicap_punkte = min(charakter.verbleibende_handicap_punkte, 4) 
                charakter.selected_handicaps.append(handicap_name_key)
                Logger.info(f"Handicap '{handicap_name_key}' ausgewählt.")
                Logger.info(f"verbleibend '{charakter.verbleibende_handicap_punkte} Kosten: {handicap.punkte} Gesamt {charakter.gesamt_handicap_punkte}")
                charakter.selected_handicaps = charakter.selected_handicaps  # Neu zuweisen
                return True
            else:
                handicap.auswaehlen()
                charakter.selected_handicaps.append(handicap_name_key)
                if neue_gesamtpunkte == 5:
                    charakter.gesamt_handicap_punkte = 4
                    charakter.verbleibende_handicap_punkte += handicap.punkte 
                    charakter.verbleibende_handicap_punkte = min(charakter.verbleibende_handicap_punkte, 4)
                    Logger.info(f"verbleibend '{charakter.verbleibende_handicap_punkte} Kosten: {handicap.punkte} Gesamt {charakter.gesamt_handicap_punkte}")
                    charakter.selected_handicaps = charakter.selected_handicaps  # Neu zuweisen 
                    Logger.warning(f"Handicap '{handicap_name_key}' ausgewählt. Handicap-punkte nicht erhöht, da Maximum von 4 erreicht.")
                    Logger.info(f"Handicap '{handicap_name_key}' ausgewählt.")
                    return True
                else:
                    Logger.warning(f"Handicap '{handicap_name_key}' ausgewählt. Handicap-punkte nicht erhöht, da Maximum von 4 erreicht.")
                    charakter.selected_handicaps = charakter.selected_handicaps  # Neu zuweisen  
                    Logger.info(f"Handicap '{handicap_name_key}' ausgewählt.")
                    charakter.verbleibende_handicap_punkte = min(charakter.verbleibende_handicap_punkte, 4)
                    return True                  
        else:
            Logger.warning(f"Handicap '{handicap_name_key}' ist bereits ausgewählt.")
    else:
        Logger.error(f"Handicap '{handicap_name_key}' existiert nicht.")
    return False


def entferne_handicap(charakter, handicap_name_key):
    """
    Entfernt ein Handicap und erstattet die Handicap-Punkte zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        handicap_name_key: Der Schlüssel des Handicaps in der handicaps-Dictionary
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if handicap_name_key in charakter.handicaps:
        handicap = charakter.handicaps[handicap_name_key]
        if handicap.ausgewaehlt:
            handicap.abwaehlen()
            charakter.gesamt_handicap_punkte -= handicap.punkte
            charakter.gesamt_handicap_punkte = max(charakter.gesamt_handicap_punkte, 0)
            charakter.verbleibende_handicap_punkte -= handicap.punkte
            charakter.verbleibende_handicap_punkte = max(charakter.verbleibende_handicap_punkte, 0)
            Logger.info(f"Handicap '{handicap_name_key}' entfernt.")
            if handicap_name_key in charakter.selected_handicaps:
                charakter.selected_handicaps.remove(handicap_name_key)
                charakter.selected_handicaps = charakter.selected_handicaps  # Neu zuweisen
            return True
        else:
            Logger.warning(f"Handicap '{handicap_name_key}' ist nicht ausgewählt.")
    else:
        Logger.error(f"Handicap '{handicap_name_key}' existiert nicht.")
    return False


def aktive_handicaps(charakter):
    """
    Gibt eine Liste aller aktiven Handicaps zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der aktiven Handicaps
    """
    return [handicap for handicap in charakter.handicaps.values() if handicap.aktiv]


def ausgewaehlte_handicaps(charakter):
    """
    Gibt eine Liste aller ausgewählten Handicaps zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der ausgewählten Handicaps
    """
    return [handicap for handicap in charakter.handicaps.values() if handicap.ausgewaehlt]


def add_handicap(charakter, handicap):
    """
    Fügt ein neues Handicap hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
        handicap: Das hinzuzufügende Handicap-Objekt
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if handicap.name in charakter.handicaps:
        Logger.warning(f"Handicap '{handicap.name}' existiert bereits.")
        return False
    charakter.handicaps[handicap.name] = handicap
    Logger.info(f"Handicap '{handicap.name}' hinzugefügt.")
    save_custom_handicaps(charakter)
    return True


def remove_handicap(charakter, handicap_name):
    """
    Entfernt ein Handicap vollständig aus der Liste (nicht nur abwählen).
    
    Args:
        charakter: Das Charakter-Objekt
        handicap_name: Der Name des zu entfernenden Handicaps
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if handicap_name in charakter.handicaps:
        del charakter.handicaps[handicap_name]
        Logger.info(f"Handicap '{handicap_name}' entfernt.")
        save_custom_handicaps(charakter)
        return True
    Logger.warning(f"Handicap '{handicap_name}' existiert nicht.")
    return False


def save_custom_handicaps(charakter):
    """
    Speichert die benutzerdefinierten Handicaps in einer JSON-Datei.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    # Finde die benutzerdefinierten Handicaps
    custom_handicaps = {
        name: handicap.to_dict()
        for name, handicap in charakter.handicaps.items()
        if getattr(handicap, 'custom', False)
    }
    if custom_handicaps:
        custom_handicaps_file = os.path.join(os.path.dirname(__file__), 'custom_handicaps.json')
        try:
            with open(custom_handicaps_file, 'w', encoding='utf-8') as f:
                json.dump(custom_handicaps, f, ensure_ascii=False, indent=4)
            Logger.info(f"Benutzerdefinierte Handicaps wurden in {custom_handicaps_file} gespeichert.")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der benutzerdefinierten Handicaps: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Handicaps zum Speichern.")


def load_custom_handicaps(charakter):
    """
    Lädt die benutzerdefinierten Handicaps aus einer JSON-Datei und fügt sie der Handicaps-Liste hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    custom_handicaps_file = os.path.join(os.path.dirname(__file__), 'custom_handicaps.json')
    if os.path.exists(custom_handicaps_file):
        try:
            with open(custom_handicaps_file, 'r', encoding='utf-8') as f:
                custom_handicaps_data = json.load(f)
            for name, data in custom_handicaps_data.items():
                handicap = Handicap.from_dict_static(data)
                if handicap:
                    charakter.handicaps[name] = handicap
            Logger.info(f"Benutzerdefinierte Handicaps wurden aus {custom_handicaps_file} geladen.")
        except Exception as e:
            Logger.error(f"Fehler beim Laden der benutzerdefinierten Handicaps: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Handicaps zum Laden gefunden.")