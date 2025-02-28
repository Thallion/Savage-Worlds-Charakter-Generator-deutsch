"""
Modul für die Verwaltung von Mächten im Charakter.
Dieses Modul enthält Funktionen zur Verwaltung von Mächten, einschließlich
des Auswahlens, Abwählens und Speicherns benutzerdefinierter Mächte.
"""

import json
import os
from kivy.logger import Logger
from models.macht import Macht


def initialisiere_maechte(charakter, maechte_daten):
    """
    Initialisiert die Mächte des Charakters basierend auf den bereitgestellten Daten.
    
    Args:
        charakter: Das Charakter-Objekt, dem die Mächte hinzugefügt werden sollen
        maechte_daten: Die Macht-Daten als Dictionary
    """
    charakter.maechte = {}
    try:
        for name, daten in maechte_daten.items():
            if not all(key in daten for key in ['Rang', 'Machtpunkte', 'Reichweite', 'Dauer']):
                Logger.warning(f"Ungültige oder fehlende Daten für Macht '{name}': {daten}")
                continue
            macht = charakter.Macht(
                name=name,
                rang=daten.get('Rang', ''),
                machtpunkte=daten.get('Machtpunkte', 0),
                reichweite=daten.get('Reichweite', ''),
                dauer=daten.get('Dauer', ''),
                effekt=daten.get('Effekt', ''),
                beschreibung=daten.get('Beschreibung', ''),
                voraussetzungen=daten.get('Voraussetzungen', [])
            )
            charakter.maechte[name] = macht
        Logger.debug("Mächte erfolgreich initialisiert.")
    except Exception as e:
        Logger.error(f"Fehler bei der Initialisierung der Mächte: {e}")


def waehle_macht(charakter, macht_name_key):
    """
    Wählt eine Macht aus und aktualisiert die verfügbaren Mächte des Charakters.
    
    Args:
        charakter: Das Charakter-Objekt
        macht_name_key: Der Name der Macht
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if charakter.verfuegbare_maechte > 0:
        if macht_name_key in charakter.maechte:
            macht = charakter.maechte[macht_name_key]
            if not macht.ausgewaehlt:
                if macht.voraussetzungen_erfuellt(charakter):
                    macht.auswaehlen()
                    charakter.verfuegbare_maechte -= 1
                    charakter.selected_maechte.append(macht_name_key)
                    charakter.selected_maechte = charakter.selected_maechte  # Neu zuweisen, um Kivy zu informieren
                    Logger.debug(f"Macht '{macht_name_key}' wurde ausgewählt.")
                    return True
                else:
                    Logger.warning(f"Voraussetzungen für Macht '{macht_name_key}' nicht erfüllt.")
            else:
                Logger.warning(f"Macht '{macht_name_key}' ist bereits ausgewählt.")
        else:
            Logger.error(f"Macht '{macht_name_key}' existiert nicht.")
    else:
        Logger.warning("Keine verfügbaren Mächte mehr zum Auswählen.")
    return False


def entferne_macht(charakter, macht_name_key):
    """
    Entfernt eine Macht und erhöht die verfügbaren Mächte des Charakters.
    
    Args:
        charakter: Das Charakter-Objekt
        macht_name_key: Der Name der Macht
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if macht_name_key in charakter.maechte:
        macht = charakter.maechte[macht_name_key]
        if macht.ausgewaehlt:
            macht.abwaehlen()
            charakter.verfuegbare_maechte += 1
            if macht_name_key in charakter.selected_maechte:
                charakter.selected_maechte.remove(macht_name_key)
                charakter.selected_maechte = charakter.selected_maechte  # Neu zuweisen
            Logger.debug(f"Macht '{macht_name_key}' wurde entfernt.")
            return True
        else:
            Logger.warning(f"Macht '{macht_name_key}' ist nicht ausgewählt.")
    else:
        Logger.error(f"Macht '{macht_name_key}' existiert nicht.")
    return False


def aktive_maechte(charakter):
    """
    Gibt eine Liste aller aktiven Mächte zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der aktiven Mächte
    """
    return [macht for macht in charakter.maechte.values() if macht.aktiv]


def ausgewaehlte_maechte(charakter):
    """
    Gibt eine Liste aller ausgewählten Mächte zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der ausgewählten Mächte
    """
    return [macht for macht in charakter.maechte.values() if macht.ausgewaehlt]


def add_macht(charakter, macht):
    """
    Fügt eine neue Macht hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
        macht: Das Macht-Objekt, das hinzugefügt werden soll
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if macht.name in charakter.maechte:
        Logger.warning(f"Macht '{macht.name}' existiert bereits.")
        return False
    charakter.maechte[macht.name] = macht
    Logger.info(f"Macht '{macht.name}' hinzugefügt.")
    save_custom_maechte(charakter)
    return True


def remove_macht(charakter, macht_name):
    """
    Entfernt eine Macht vollständig aus der Liste (nicht nur abwählen).
    
    Args:
        charakter: Das Charakter-Objekt
        macht_name: Der Name der zu entfernenden Macht
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if macht_name in charakter.maechte:
        del charakter.maechte[macht_name]
        Logger.info(f"Macht '{macht_name}' entfernt.")
        save_custom_maechte(charakter)
        return True
    Logger.warning(f"Macht '{macht_name}' existiert nicht.")
    return False


def erhoehe_machtpunkte(charakter, punkte):
    """
    Erhöht die Machtpunkte des Charakters.
    
    Args:
        charakter: Das Charakter-Objekt
        punkte: Die Anzahl der hinzuzufügenden Machtpunkte
    """
    charakter.machtpunkte += punkte


def senke_machtpunkte(charakter, punkte):
    """
    Verringert die Machtpunkte des Charakters.
    
    Args:
        charakter: Das Charakter-Objekt
        punkte: Die Anzahl der abzuziehenden Machtpunkte
    """
    charakter.machtpunkte -= punkte


def save_custom_maechte(charakter):
    """
    Speichert die benutzerdefinierten Mächte in einer JSON-Datei.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    # Finde die benutzerdefinierten Mächte
    custom_maechte = {name: macht.to_dict() for name, macht in charakter.maechte.items() if getattr(macht, 'custom', False)}
    if custom_maechte:
        custom_maechte_file = os.path.join(os.path.dirname(__file__), 'custom_maechte.json')
        try:
            with open(custom_maechte_file, 'w', encoding='utf-8') as f:
                json.dump(custom_maechte, f, ensure_ascii=False, indent=4)
            Logger.info(f"Benutzerdefinierte Mächte wurden in {custom_maechte_file} gespeichert.")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der benutzerdefinierten Mächte: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Mächte zum Speichern.")


def load_custom_maechte(charakter):
    """
    Lädt die benutzerdefinierten Mächte aus einer JSON-Datei und fügt sie der Mächte-Liste hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    custom_maechte_file = os.path.join(os.path.dirname(__file__), 'custom_maechte.json')
    if os.path.exists(custom_maechte_file):
        try:
            with open(custom_maechte_file, 'r', encoding='utf-8') as f:
                custom_maechte_data = json.load(f)
            for name, data in custom_maechte_data.items():
                macht = Macht.from_dict_static(data)
                charakter.maechte[name] = macht
            Logger.info(f"Benutzerdefinierte Mächte wurden aus {custom_maechte_file} geladen.")
        except Exception as e:
            Logger.error(f"Fehler beim Laden der benutzerdefinierten Mächte: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Mächte zum Laden gefunden.")