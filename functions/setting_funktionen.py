"""
Modul für die Verwaltung von Settings und benutzerdefinierten Elementen im Charakter.
Dieses Modul enthält Funktionen zum Laden, Speichern und Verwalten von Settings
sowie die Verwaltung von benutzerdefinierten Elementen.
"""

import json
import os
import sys
from pathlib import Path
from kivy.logger import Logger
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

def get_application_root():
    """
    Ermittelt das Hauptverzeichnis der Anwendung.
    
    Returns:
        Path: Das Hauptverzeichnis der Anwendung
    """
    if getattr(sys, 'frozen', False):
        # Wenn die Anwendung gepackt ist (z.B. mit cx_Freeze), verwende das Verzeichnis der ausführbaren Datei
        app_root = Path(sys.executable).parent
    else:
        # Bei normalem Python-Skript verwende das Verzeichnis der Skriptdatei
        app_root = Path(__file__).parent.parent.resolve()

    return app_root


class SetEncoder(json.JSONEncoder):
    """JSON Encoder für die Serialisierung von Sets."""
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


class CustomElementManager:
    """Verwaltet benutzerdefinierte Elemente und Settings."""
    
    def __init__(self, charakter, settings_dir=None, setting_name='SWAE'):
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

    def load_all_settings(self):
        """Lädt alle Einstellungen aus dem settings-Verzeichnis."""
        if not self.settings_dir.exists():
            try:
                self.settings_dir.mkdir(parents=True, exist_ok=True)
                Logger.info(f"Settingverzeichnis erstellt: {self.settings_dir}")
            except OSError as e:
                Logger.error(f"Fehler beim Erstellen des Settingsverzeichnisses '{self.settings_dir}': {e}")
                return

        for filename in self.settings_dir.iterdir():
            if filename.suffix == '.json':
                try:
                    with filename.open('r', encoding='utf-8') as f:
                        setting_data = json.load(f)

                    # Konvertiere 'fertigkeiten_daten' von Listen zurück zu Sets
                    if 'fertigkeiten_daten' in setting_data:
                        fertigkeiten_daten_loaded = setting_data['fertigkeiten_daten']
                        if isinstance(fertigkeiten_daten_loaded, dict):
                            for fertigkeit, attribut_list in fertigkeiten_daten_loaded.items():
                                if isinstance(attribut_list, list):
                                    setting_data['fertigkeiten_daten'][fertigkeit] = set(attribut_list)

                    setting_name = setting_data.get('name', filename.stem)
                    self.settings[setting_name] = setting_data
                    Logger.info(f"Einstellung '{setting_name}' aus {filename.name} geladen.")
                except Exception as e:
                    Logger.error(f"Fehler beim Laden des Settings '{filename.name}': {e}")

    def get_all_settings(self):
        """
        Gibt eine Liste aller verfügbaren Settings zurück.
        
        Returns:
            List: Liste aller Settings-Namen
        """
        return list(self.settings.keys())

    def get_active_setting(self):
        """
        Gibt das aktive Setting zurück.
        
        Returns:
            Dict: Das aktive Setting als Dictionary
        """
        return self.active_setting

    def set_active_setting(self, setting_name):
        """
        Setzt das aktive Setting.
        
        Args:
            setting_name: Der Name des zu aktivierenden Settings
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        if setting_name in self.settings:
            self.active_setting = self.settings[setting_name]
            self.active_setting_name = setting_name
            Logger.info(f"Aktives Setting auf '{setting_name}' gesetzt.")
            return True
        else:
            Logger.warning(f"Setting '{setting_name}' existiert nicht.")
            return False

    def add_setting(self, name, setting_data, overwrite=False):
        """
        Fügt ein neues Setting hinzu oder überschreibt ein bestehendes.
        
        Args:
            name: Der Name des Settings
            setting_data: Die Setting-Daten als Dictionary
            overwrite: Ob ein bestehendes Setting überschrieben werden soll (default: False)
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        settings_path = self.settings_dir / f"{name}.json"
        if settings_path.exists() and not overwrite:
            Logger.warning(f"Setting '{name}' existiert bereits und wird nicht überschrieben.")
            return False
        try:
            with settings_path.open('w', encoding='utf-8') as f:
                json.dump(setting_data, f, ensure_ascii=False, indent=4)
            self.settings[name] = setting_data
            Logger.info(f"Setting '{name}' erfolgreich gespeichert.")
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Settings '{name}': {e}")
            return False

    def save_setting(self, setting_name):
        """
        Speichert das aktuelle Setting unter dem angegebenen Namen.
        
        Args:
            setting_name: Der Name, unter dem das Setting gespeichert werden soll
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        if self.active_setting is None:
            Logger.error("Keine aktives Setting zum Speichern.")
            return False

        setting_data = self.active_setting.copy()

        # Konvertiere 'fertigkeiten_daten' von Sets zu Listen
        if 'fertigkeiten_daten' in setting_data:
            fertigkeiten_daten = setting_data['fertigkeiten_daten']
            if isinstance(fertigkeiten_daten, dict):
                setting_data['fertigkeiten_daten'] = {k: list(v) for k, v in fertigkeiten_daten.items()}

        # Füge 'fertigkeiten' hinzu, indem du auf self.charakter.fertigkeiten zugreifst
        setting_data['fertigkeiten'] = {
            name: fertigkeit.to_dict_with_reset_wuerfel()
            for name, fertigkeit in self.charakter.fertigkeiten.items()
        }

        # Speichere die Daten
        filename = f"{setting_name}.json"
        filepath = self.settings_dir / filename
        try:
            with filepath.open('w', encoding='utf-8') as f:
                json.dump(setting_data, f, cls=SetEncoder, ensure_ascii=False, indent=4)
            self.settings[setting_name] = setting_data
            Logger.info(f"Einstellung '{setting_name}' in {filename} gespeichert.")
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Einstellung '{setting_name}': {e}")
            return False

    def delete_setting(self, setting_name):
        """
        Löscht eine Einstellung.
        
        Args:
            setting_name: Der Name des zu löschenden Settings
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        if setting_name not in self.settings:
            Logger.warning(f"Einstellung '{setting_name}' existiert nicht.")
            return False
        filename = f"{setting_name}.json"
        filepath = self.settings_dir / filename
        try:
            filepath.unlink()
            del self.settings[setting_name]
            Logger.info(f"Einstellung '{setting_name}' aus {filename} gelöscht.")
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Einstellung '{setting_name}': {e}")
            return False

    def update_element(self, element_type, element_name, element_data):
        """
        Aktualisiert oder fügt ein Element zur aktiven Einstellung hinzu.
        
        Args:
            element_type: Der Typ des Elements (z.B. 'talente', 'handicaps', etc.)
            element_name: Der Name des Elements
            element_data: Die Daten des Elements
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        if self.active_setting is None:
            Logger.error("Keine aktive Einstellung zum Aktualisieren.")
            return False
        if element_type not in self.active_setting:
            self.active_setting[element_type] = {}
        self.active_setting[element_type][element_name] = element_data
        Logger.info(f"Element '{element_name}' zum Typ '{element_type}' hinzugefügt/aktualisiert.")
        return True

    def remove_element(self, element_type, element_name):
        """
        Entfernt ein Element aus der aktiven Einstellung.
        
        Args:
            element_type: Der Typ des Elements (z.B. 'talente', 'handicaps', etc.)
            element_name: Der Name des Elements
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        if self.active_setting is None:
            Logger.error("Keine aktive Einstellung zum Entfernen von Elementen.")
            return False
        if element_type in self.active_setting and element_name in self.active_setting[element_type]:
            del self.active_setting[element_type][element_name]
            Logger.info(f"Element '{element_name}' vom Typ '{element_type}' entfernt.")
            return True
        else:
            Logger.warning(f"Element '{element_name}' vom Typ '{element_type}' existiert nicht.")
            return False


def create_default_setting(charakter):
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


def load_elements_from_active_setting(self, skip_equipment=False):
    """
    Lädt alle Elemente aus dem aktiven Setting.
    
    Args:
        skip_equipment (bool): Wenn True, wird die Ausrüstung nicht geladen (hilfreich beim Laden eines Charakters)
        
    Returns:
        bool: True bei Erfolg, sonst False
    """
    try:
        Logger.info(f"Lade Elemente aus dem aktiven Setting '{self.active_setting_name}'")
        
        # Aktives Setting abrufen
        active_setting = self.custom_element_manager.get_active_setting()
        if not active_setting:
            Logger.error(f"Aktives Setting '{self.active_setting_name}' konnte nicht geladen werden.")
            return False
        
        # Farben laden
        self.settingregeln.farbschema = active_setting.get('farbschema', 'Blue')
        
        # Völker laden (komplett ersetzen)
        voelker_data = active_setting.get('voelker', {})
        if voelker_data:
            # Völker zurücksetzen
            self.voelker = {}
            for name, volk_dict in voelker_data.items():
                try:
                    self.voelker[name] = Volk.from_dict(volk_dict)
                except Exception as e:
                    Logger.warning(f"Fehler beim Laden des Volkes '{name}': {e}")
            Logger.info(f"{len(self.voelker)} Völker geladen.")
        
        # Fertigkeiten_daten direkt aus dem Setting laden
        fertigkeiten_daten = active_setting.get('fertigkeiten_daten', {})
        if fertigkeiten_daten:
            # Fertigkeiten_daten setzen
            self.fertigkeiten_daten = {}
            for name, attribut_set in fertigkeiten_daten.items():
                if isinstance(attribut_set, list):
                    # Konvertiere Listen zurück zu Sets
                    self.fertigkeiten_daten[name] = set(attribut_set)
                else:
                    self.fertigkeiten_daten[name] = attribut_set
            # Fertigkeiten neu initialisieren
            self.initialisiere_fertigkeiten()
            Logger.info(f"{len(self.fertigkeiten_daten)} Fertigkeiten-Daten geladen, {len(self.fertigkeiten)} Fertigkeiten initialisiert.")
        
        # Handicaps laden (komplett ersetzen)
        handicaps_data = active_setting.get('handicaps', {})
        if handicaps_data:
            # Handicaps zurücksetzen
            self.handicaps = {}
            for name, handicap_dict in handicaps_data.items():
                try:
                    self.handicaps[name] = Handicap.from_dict_static(handicap_dict)
                except Exception as e:
                    Logger.warning(f"Fehler beim Laden des Handicaps '{name}': {e}")
            Logger.info(f"{len(self.handicaps)} Handicaps geladen.")
        
        # Talente laden (komplett ersetzen)
        talente_data = active_setting.get('talente', {})
        if talente_data:
            # Talente zurücksetzen
            self.talente = {}
            for name, talent_dict in talente_data.items():
                try:
                    self.talente[name] = Talent.from_dict_static(talent_dict)
                except Exception as e:
                    Logger.warning(f"Fehler beim Laden des Talents '{name}': {e}")
            Logger.info(f"{len(self.talente)} Talente geladen.")
        
        # Mächte laden (komplett ersetzen)
        maechte_data = active_setting.get('maechte', {})
        if maechte_data:
            # Mächte zurücksetzen
            self.maechte = {}
            for name, macht_dict in maechte_data.items():
                try:
                    self.maechte[name] = Macht.from_dict_static(macht_dict)
                except Exception as e:
                    Logger.warning(f"Fehler beim Laden der Macht '{name}': {e}")
            Logger.info(f"{len(self.maechte)} Mächte geladen.")
        
        # Ausrüstung laden, wenn nicht übersprungen
        if not skip_equipment:
            ausruestung_data = active_setting.get('ausruestung', {})
            if ausruestung_data:
                # Ausrüstung zurücksetzen
                self.ausruestung = {}
                for name, item_dict in ausruestung_data.items():
                    try:
                        kategorie = item_dict.get('kategorie', 'Allgemein')
                        if kategorie == 'Waffe':
                            item = Waffe.from_setting_dict(item_dict)
                        elif kategorie == 'Rüstung':
                            item = Ruestung.from_setting_dict(item_dict)
                        elif kategorie == 'Schild':
                            item = Schild.from_setting_dict(item_dict)
                        else:
                            item = Ausruestung.from_setting_dict(item_dict)
                        
                        self.ausruestung[name] = item
                    except Exception as e:
                        Logger.warning(f"Fehler beim Laden des Ausrüstungsgegenstands '{name}': {e}")
                Logger.info(f"{len(self.ausruestung)} Ausrüstungsgegenstände geladen.")
        
        # Settingregeln laden
        settingregeln_data = active_setting.get('settingregeln', {})
        if settingregeln_data:
            try:
                self.settingregeln.from_dict(settingregeln_data)
                Logger.info("Settingregeln geladen.")
            except Exception as e:
                Logger.warning(f"Fehler beim Laden der Settingregeln: {e}")
        
        return True
    except Exception as e:
        Logger.error(f"Fehler beim Laden der Elemente aus dem aktiven Setting: {e}", exc_info=True)
        return False