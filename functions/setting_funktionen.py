# functions/setting_funktionen.py
"""
Modul für die Verwaltung von Settings und benutzerdefinierten Elementen im Charakter.
Dieses Modul enthält Funktionen zum Laden, Speichern und Verwalten von Settings
sowie die Verwaltung von benutzerdefinierten Elementen.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from kivy.logger import Logger

# Import der Konfiguration
from config.ausruestung_config import (
    AusruestungKategorien,
    LogMessages
)

# Import der Models
from models.wuerfel import Wuerfel
from models.attribut import Attribut
from models.fertigkeit import Fertigkeit
from models.handicap import Handicap
from models.talent import Talent
from models.volk import Volk
from models.macht import Macht
from models.ausruestung import Ausruestung
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild

# Import der Hilfsfunktionen
import functions.ausruestung_funktionen as ausruestung_funktionen


# Import centralized path utilities
from utils.path_utils import get_application_root


class SetEncoder(json.JSONEncoder):
    """JSON Encoder für die Serialisierung von Sets."""
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


class CustomElementManager:
    """Verwaltet benutzerdefinierte Elemente und Settings."""
    
    def __init__(self, charakter, settings_dir: Optional[Path] = None, setting_name: str = 'SWAE'):
        """
        Initialisiert den CustomElementManager.
        
        Args:
            charakter: Das Charakter-Objekt
            settings_dir: Das Verzeichnis für die Settings (optional)
            setting_name: Der Name des aktiven Settings (default: 'SWAE')
        """
        self.charakter = charakter
        if settings_dir is None:
            app_root = get_application_root()
            settings_dir = app_root / 'settings'
        else:
            settings_dir = Path(settings_dir)

        self.settings_dir = settings_dir
        self.settings = {}
        self.active_setting = None

        # Laden der Einstellungen
        self.load_all_settings()

        # Setzen des aktiven Setting-Namens nach dem Laden der Settings
        self.active_setting_name = setting_name
        self.set_active_setting(self.active_setting_name)

    def load_all_settings(self) -> None:
        """Lädt alle Einstellungen aus dem settings-Verzeichnis."""
        try:
            if not self.settings_dir.exists():
                Logger.warning(f"Settings-Verzeichnis {self.settings_dir} existiert nicht.")
                return

            for setting_file in self.settings_dir.glob('*.json'):
                try:
                    with open(setting_file, 'r', encoding='utf-8') as f:
                        setting_data = json.load(f)
                        setting_name = setting_file.stem
                        self.settings[setting_name] = setting_data
                        Logger.info(f"Setting '{setting_name}' geladen.")
                except Exception as e:
                    Logger.error(f"Fehler beim Laden von Setting {setting_file}: {e}")

        except Exception as e:
            Logger.error(f"Fehler beim Laden der Settings: {e}")

    def save_setting(self, name: str, setting_data: Dict[str, Any]) -> bool:
        """
        Speichert ein Setting in eine JSON-Datei.
        
        Args:
            name: Name des Settings
            setting_data: Die Setting-Daten als Dictionary
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        try:
            if not self.settings_dir.exists():
                self.settings_dir.mkdir(parents=True, exist_ok=True)

            file_path = self.settings_dir / f"{name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(setting_data, f, ensure_ascii=False, indent=4, cls=SetEncoder)
            
            # Setting auch zum internen Dictionary hinzufügen
            self.settings[name] = setting_data
            
            Logger.info(f"Setting '{name}' gespeichert unter {file_path}")
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Speichern von Setting '{name}': {e}")
            return False

    def set_active_setting(self, name: str) -> bool:
        """
        Setzt das aktive Setting.
        
        Args:
            name: Name des zu aktivierenden Settings
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        if name in self.settings:
            self.active_setting = self.settings[name]
            self.active_setting_name = name
            Logger.info(f"Aktives Setting geändert zu '{name}'.")
            return True
        else:
            Logger.warning(f"Setting '{name}' existiert nicht.")
            return False

    def get_active_setting(self) -> Optional[Dict[str, Any]]:
        """
        Gibt das aktive Setting zurück.
        
        Returns:
            Dict oder None: Das aktive Setting oder None
        """
        return self.active_setting

    def get_all_settings(self) -> List[str]:
        """
        Gibt eine Liste aller verfügbaren Settings zurück.
        
        Returns:
            List[str]: Liste aller Settings-Namen
        """
        return list(self.settings.keys())

    def add_setting(self, name: str, setting_data: Dict[str, Any], overwrite: bool = False) -> bool:
        """
        Fügt ein neues Setting hinzu.
        
        Args:
            name: Name des Settings
            setting_data: Die Setting-Daten
            overwrite: Überschreibt existierendes Setting wenn True
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        if name in self.settings and not overwrite:
            Logger.warning(f"Setting '{name}' existiert bereits. Verwende overwrite=True zum Überschreiben.")
            return False
        
        self.settings[name] = setting_data
        return self.save_setting(name, setting_data)

    def delete_setting(self, name: str) -> bool:
        """
        Löscht ein Setting.
        
        Args:
            name: Name des zu löschenden Settings
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        if name not in self.settings:
            Logger.warning(f"Setting '{name}' existiert nicht.")
            return False
        
        try:
            # Datei löschen
            file_path = self.settings_dir / f"{name}.json"
            if file_path.exists():
                file_path.unlink()
                Logger.info(f"Setting-Datei '{file_path}' gelöscht.")
            
            # Aus Dictionary entfernen
            del self.settings[name]
            Logger.info(f"Setting '{name}' erfolgreich gelöscht.")
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Löschen von Setting '{name}': {e}")
            return False

    def remove_element_from_active_setting(self, element_type: str, element_name: str) -> bool:
        """
        Entfernt ein Element aus dem aktiven Setting.
        
        Args:
            element_type: Typ des Elements
            element_name: Name des Elements
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        if not self.active_setting:
            Logger.error("Kein aktives Setting vorhanden.")
            return False
            
        if element_type in self.active_setting and element_name in self.active_setting[element_type]:
            del self.active_setting[element_type][element_name]
            Logger.info(f"Element '{element_name}' vom Typ '{element_type}' entfernt.")
            return True
        else:
            Logger.warning(LogMessages.ELEMENT_EXISTIERT_NICHT.format(
                name=element_name,
                typ=element_type
            ))
            return False

    def update_element(self, element_type: str, element_name: str, element_data: dict) -> bool:
        """
        Fügt ein Element zum aktiven Setting hinzu oder aktualisiert es.
        
        Args:
            element_type: Typ des Elements (z.B. 'talente', 'attribute', etc.)
            element_name: Name des Elements
            element_data: Element-Daten als Dictionary
            
        Returns:
            bool: True bei Erfolg, sonst False
        """
        try:
            if not self.active_setting:
                Logger.error("Kein aktives Setting vorhanden.")
                return False
            
            # Element-Typ-Dictionary erstellen falls nicht vorhanden
            if element_type not in self.active_setting:
                self.active_setting[element_type] = {}
            
            # Element hinzufügen/aktualisieren
            self.active_setting[element_type][element_name] = element_data
            Logger.info(f"Element '{element_name}' vom Typ '{element_type}' aktualisiert.")
            
            return True
            
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren von Element '{element_name}' (Typ: {element_type}): {e}")
            return False


def create_default_setting(charakter) -> Dict[str, Any]:
    """
    Erstellt eine Standard-Einstellung.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Dict: Das Standard-Setting als Dictionary
    """
    default_setting = {
        "name": "SWAE",
        "description": "Savage-Worlds Abenteuer Edition.",
        "voelker": {name: volk.to_setting_dict() for name, volk in charakter.voelker.items()},
        "voelker_selected": charakter.voelker_selected, 
        'attribute': {name: attribut.to_dict() for name, attribut in charakter.attribute.items()},
        "fertigkeiten_daten": {name: list(attribut_set) for name, attribut_set in charakter.fertigkeiten_daten.items()},
        "talente": {name: talent.to_dict() for name, talent in charakter.talente.items()},
        "handicaps": {name: handicap.to_dict() for name, handicap in charakter.handicaps.items()},
        "maechte": {name: macht.to_dict() for name, macht in charakter.maechte.items()},
        "ausruestung": {name: ausruestung.to_setting_dict() for name, ausruestung in charakter.ausruestung.items()},
        'settingregeln': charakter.settingregeln.to_dict(),
    }
    return default_setting


def load_elements_from_active_setting(charakter, skip_equipment: bool = False, 
                                     merge_elements: bool = True, 
                                     replace_mode: bool = False) -> bool:
    """
    Lädt alle Elemente aus dem aktiven Setting.
    
    Args:
        charakter: Das Charakter-Objekt
        skip_equipment: Wenn True, wird die Ausrüstung nicht geladen
        merge_elements: Wenn True, werden Elemente gemerged statt ersetzt
        replace_mode: Wenn True, werden alle Elemente komplett ersetzt
        
    Returns:
        bool: True bei Erfolg, sonst False
    """
    try:
        Logger.info(f"Lade Elemente aus dem aktiven Setting '{charakter.active_setting_name}'")
        
        # Aktives Setting abrufen
        active_setting = charakter.custom_element_manager.get_active_setting()
        if not active_setting:
            Logger.error(f"Aktives Setting '{charakter.active_setting_name}' konnte nicht geladen werden.")
            return False
        
        # Replace-Modus überschreibt merge_elements
        if replace_mode:
            merge_elements = False
        
        # Völker laden
        _lade_voelker(charakter, active_setting, merge_elements)
        
        # Attribute laden
        _lade_attribute(charakter, active_setting, merge_elements)
        
        # Fertigkeiten laden
        _lade_fertigkeiten(charakter, active_setting, merge_elements)
        
        # Talente laden
        _lade_talente(charakter, active_setting, merge_elements)
        
        # Handicaps laden
        _lade_handicaps(charakter, active_setting, merge_elements)
        
        # Mächte laden
        _lade_maechte(charakter, active_setting, merge_elements)
        
        # Ausrüstung laden, wenn nicht übersprungen
        if not skip_equipment:
            _lade_ausruestung(charakter, active_setting, merge_elements)
        
        # Settingregeln laden
        _lade_settingregeln(charakter, active_setting)
        
        # Währung und Startgeld laden
        _lade_currency(charakter, active_setting)
        
        return True
        
    except Exception as e:
        Logger.error(f"Fehler beim Laden der Elemente aus dem aktiven Setting: {e}", exc_info=True)
        return False


# --- Private Hilfsfunktionen für das Laden von Elementen ---

def _lade_voelker(charakter, active_setting: Dict[str, Any], merge_elements: bool) -> None:
    """Lädt Völker aus dem Setting."""
    voelker_data = active_setting.get('voelker', {})
    if voelker_data:
        if not merge_elements:
            charakter.voelker = {}
        for name, volk_dict in voelker_data.items():
            try:
                if not merge_elements or name not in charakter.voelker:
                    volk = Volk.from_setting_dict(volk_dict)
                    charakter.voelker[name] = volk
            except Exception as e:
                Logger.warning(f"Fehler beim Laden des Volks '{name}': {e}")
        Logger.info(LogMessages.ELEMENTE_GELADEN.format(
            anzahl=len(charakter.voelker),
            typ="Völker"
        ))


def _lade_attribute(charakter, active_setting: Dict[str, Any], merge_elements: bool) -> None:
    """Lädt Attribute aus dem Setting."""
    attribute_data = active_setting.get('attribute', {})
    if attribute_data:
        if not merge_elements:
            charakter.attribute = {}
        for name, attr_dict in attribute_data.items():
            try:
                if not merge_elements or name not in charakter.attribute:
                    attribut = Attribut.from_dict(attr_dict)
                    charakter.attribute[name] = attribut
            except Exception as e:
                Logger.warning(f"Fehler beim Laden des Attributs '{name}': {e}")
        Logger.info(LogMessages.ELEMENTE_GELADEN.format(
            anzahl=len(charakter.attribute),
            typ="Attribute"
        ))


def _lade_fertigkeiten(charakter, active_setting: Dict[str, Any], merge_elements: bool) -> None:
    """Lädt Fertigkeiten aus dem Setting."""
    fertigkeiten_daten = active_setting.get('fertigkeiten_daten', {})
    if fertigkeiten_daten:
        if not merge_elements:
            charakter.fertigkeiten_daten = {}
        for name, attribut_list in fertigkeiten_daten.items():
            try:
                if not merge_elements or name not in charakter.fertigkeiten_daten:
                    charakter.fertigkeiten_daten[name] = set(attribut_list)
            except Exception as e:
                Logger.warning(f"Fehler beim Laden der Fertigkeitsdaten '{name}': {e}")
        Logger.info(LogMessages.ELEMENTE_GELADEN.format(
            anzahl=len(charakter.fertigkeiten_daten),
            typ="Fertigkeiten"
        ))


def _lade_talente(charakter, active_setting: Dict[str, Any], merge_elements: bool) -> None:
    """Lädt Talente aus dem Setting."""
    talente_data = active_setting.get('talente', {})
    if talente_data:
        if not merge_elements:
            charakter.talente = {}
        for name, talent_dict in talente_data.items():
            try:
                if not merge_elements or name not in charakter.talente:
                    talent = Talent.from_dict(talent_dict)
                    charakter.talente[name] = talent
            except Exception as e:
                Logger.warning(f"Fehler beim Laden des Talents '{name}': {e}")
        Logger.info(LogMessages.ELEMENTE_GELADEN.format(
            anzahl=len(charakter.talente),
            typ="Talente"
        ))


def _lade_handicaps(charakter, active_setting: Dict[str, Any], merge_elements: bool) -> None:
    """Lädt Handicaps aus dem Setting."""
    handicaps_data = active_setting.get('handicaps', {})
    if handicaps_data:
        if not merge_elements:
            charakter.handicaps = {}
        for name, handicap_dict in handicaps_data.items():
            try:
                if not merge_elements or name not in charakter.handicaps:
                    handicap = Handicap.from_dict(handicap_dict)
                    charakter.handicaps[name] = handicap
            except Exception as e:
                Logger.warning(f"Fehler beim Laden des Handicaps '{name}': {e}")
        Logger.info(LogMessages.ELEMENTE_GELADEN.format(
            anzahl=len(charakter.handicaps),
            typ="Handicaps"
        ))


def _lade_maechte(charakter, active_setting: Dict[str, Any], merge_elements: bool) -> None:
    """Lädt Mächte aus dem Setting."""
    maechte_data = active_setting.get('maechte', {})
    if maechte_data:
        if not merge_elements:
            charakter.maechte = {}
        for name, macht_dict in maechte_data.items():
            try:
                if not merge_elements or name not in charakter.maechte:
                    macht = Macht.from_dict(macht_dict)
                    charakter.maechte[name] = macht
            except Exception as e:
                Logger.warning(f"Fehler beim Laden der Macht '{name}': {e}")
        Logger.info(LogMessages.ELEMENTE_GELADEN.format(
            anzahl=len(charakter.maechte),
            typ="Mächte"
        ))


def _lade_ausruestung(charakter, active_setting: Dict[str, Any], merge_elements: bool) -> None:
    """Lädt Ausrüstung aus dem Setting."""
    ausruestung_data = active_setting.get('ausruestung', {})
    if ausruestung_data:
        if not merge_elements:
            # Ausrüstung zurücksetzen bei Replace-Modus
            charakter.ausruestung = {}
        
        for name, item_dict in ausruestung_data.items():
            try:
                # Nur hinzufügen wenn nicht bereits vorhanden (bei Merge) oder immer (bei Replace)
                if not merge_elements or name not in charakter.ausruestung:
                    # Verwende die zentrale Funktion zum Erstellen des Items
                    item = ausruestung_funktionen.erstelle_item_nach_kategorie(item_dict)
                    if item is not None:
                        charakter.ausruestung[name] = item
                    else:
                        Logger.warning(f"Ausrüstung '{name}' konnte nicht erstellt werden und wird übersprungen.")
            except Exception as e:
                Logger.warning(LogMessages.FEHLER_BEIM_LADEN.format(
                    name=name,
                    error=e
                ))
        
        Logger.info(LogMessages.ELEMENTE_GELADEN.format(
            anzahl=len(charakter.ausruestung),
            typ="Ausrüstungsgegenstände"
        ))


def _lade_settingregeln(charakter, active_setting: Dict[str, Any]) -> None:
    """Lädt Settingregeln aus dem Setting."""
    settingregeln_data = active_setting.get('settingregeln', {})
    if settingregeln_data:
        try:
            charakter.settingregeln.from_dict(settingregeln_data)
            Logger.info("Settingregeln geladen.")
        except Exception as e:
            Logger.warning(f"Fehler beim Laden der Settingregeln: {e}")


def _lade_currency(charakter, active_setting: Dict[str, Any]) -> None:
    """Lädt Währung und Startgeld aus dem Setting."""
    try:
        # Startgeld laden
        startgeld = active_setting.get('startgeld')
        if startgeld is not None:
            charakter.vermoegen = startgeld
            Logger.info(f"Startgeld auf {startgeld} gesetzt.")
        
        # Währung laden
        waehrung = active_setting.get('waehrung')
        if waehrung:
            charakter.waehrungseinheit = waehrung
            Logger.info(f"Währungseinheit auf '{waehrung}' gesetzt.")
            
    except Exception as e:
        Logger.warning(f"Fehler beim Laden der Währungseinstellungen: {e}")


# Export der öffentlichen Funktionen und Klassen
__all__ = [
    'get_application_root',
    'SetEncoder',
    'CustomElementManager',
    'create_default_setting',
    'load_elements_from_active_setting'
]