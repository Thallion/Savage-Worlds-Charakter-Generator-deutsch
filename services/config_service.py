# services/config_service.py
"""
Configuration Service für Anwendungseinstellungen
Verwaltet Konfiguration mit JSON-basierter Persistierung
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union
from kivy.logger import Logger
from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class AppConfig:
    """Datenklasse für Anwendungskonfiguration"""
    
    # Theme-Einstellungen
    theme_style: str = "Dark"
    primary_palette: str = "Orange"
    
    # Charaktergenerierung
    default_attribute_points: int = 5
    default_skill_points: int = 12
    default_money: int = 500
    default_currency: str = "Gold"
    
    # UI-Einstellungen
    window_maximized: bool = True
    window_width: int = 1200
    window_height: int = 800
    mobile_modus: bool = False
    show_logger: bool = True
    auto_save_enabled: bool = True
    auto_save_interval: int = 300  # Sekunden
    
    # Dateipfade
    last_character_directory: str = ""
    last_pdf_directory: str = ""
    
    # Erweiterte Einstellungen
    debug_mode: bool = False
    log_level: str = "INFO"
    max_recent_files: int = 10
    
    # PDF-Einstellungen
    default_printer_friendly: bool = False
    pdf_paper_size: str = "A4"
    
    # Backup-Einstellungen
    auto_backup_enabled: bool = True
    max_backups: int = 5
    
    # Setting-Einstellungen
    last_setting: str = "SWAE"

    # Mobile-Layout-Override (für Desktop-Tests)
    force_mobile_layout: bool = False

    # Desktop-Skalierung: "auto" für automatische Erkennung, oder float (z.B. 1.5)
    desktop_scale_factor: str = "auto"

    # Bildschirm-Orientierung (Android): "auto", "portrait", "landscape"
    screen_orientation: str = "auto"
    # Orientierung fixieren (True = fixiert, False = flexibel/System-Einstellung)
    screen_orientation_locked: bool = False

    # Tutorial-Zustand
    tutorial_state: dict = field(default_factory=dict)

    # Version und Metadaten
    config_version: str = "1.0"
    last_updated: str = ""
    
    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()


class ConfigService:
    """
    Service für Konfigurationsverwaltung
    Bietet typisierte Konfiguration mit Validation und Persistierung
    """
    
    def __init__(self, config_file: str = "app_config.json"):
        self.config_file = config_file
        self.config: AppConfig = AppConfig()
        self._config_path = self._get_config_path()
        self._listeners: Dict[str, list] = {}
        
        # Konfiguration laden
        self.load_config()
        
        Logger.info(f"ConfigService initialisiert (Pfad: {self._config_path})")
    
    def _get_config_path(self) -> Path:
        """
        Bestimmt den Pfad für die Konfigurationsdatei
        
        Returns:
            Path: Pfad zur Konfigurationsdatei
        """
        if getattr(sys, 'frozen', False):
            # Ausführbare Version
            app_dir = Path(sys.executable).parent
        else:
            # Entwicklungsversion
            app_dir = Path(__file__).parent.parent
        
        config_dir = app_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        return config_dir / self.config_file
    
    def load_config(self) -> bool:
        """
        Lädt die Konfiguration aus der Datei
        
        Returns:
            bool: True bei Erfolg
        """
        try:
            if self._config_path.exists():
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Konfiguration aus Dictionary erstellen
                self.config = AppConfig(**data)
                
                Logger.info("Konfiguration erfolgreich geladen")
                self._notify_listeners('config_loaded', self.config)
                return True
            else:
                # Standard-Konfiguration erstellen
                Logger.info("Keine Konfigurationsdatei gefunden, erstelle Standard-Konfiguration")
                self.save_config()
                return True
                
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Konfiguration: {str(e)}")
            # Bei Fehler Standard-Konfiguration verwenden
            self.config = AppConfig()
            return False
    
    def save_config(self) -> bool:
        """
        Speichert die Konfiguration in der Datei
        
        Returns:
            bool: True bei Erfolg
        """
        try:
            # Zeitstempel aktualisieren
            self.config.last_updated = datetime.now().isoformat()
            
            # Konfiguration als Dictionary serialisieren
            config_dict = asdict(self.config)
            
            # In Datei speichern
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            Logger.debug("Konfiguration gespeichert")
            self._notify_listeners('config_saved', self.config)
            return True
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Konfiguration: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Holt einen Konfigurationswert
        
        Args:
            key (str): Konfigurationsschlüssel
            default (Any): Standardwert
            
        Returns:
            Any: Konfigurationswert
        """
        try:
            return getattr(self.config, key, default)
        except AttributeError:
            Logger.warning(f"Konfigurationsschlüssel '{key}' nicht gefunden")
            return default
    
    def set(self, key: str, value: Any, save_immediately: bool = True) -> bool:
        """
        Setzt einen Konfigurationswert
        
        Args:
            key (str): Konfigurationsschlüssel
            value (Any): Neuer Wert
            save_immediately (bool): Sofort speichern
            
        Returns:
            bool: True bei Erfolg
        """
        try:
            if hasattr(self.config, key):
                old_value = getattr(self.config, key)
                setattr(self.config, key, value)
                
                Logger.debug(f"Konfiguration geändert: {key} = {value} (vorher: {old_value})")
                
                if save_immediately:
                    self.save_config()
                
                self._notify_listeners('config_changed', {'key': key, 'value': value, 'old_value': old_value})
                return True
            else:
                Logger.warning(f"Konfigurationsschlüssel '{key}' nicht gültig")
                return False
                
        except Exception as e:
            Logger.error(f"Fehler beim Setzen der Konfiguration: {str(e)}")
            return False
    
    def update_multiple(self, updates: Dict[str, Any], save_immediately: bool = True) -> bool:
        """
        Aktualisiert mehrere Konfigurationswerte
        
        Args:
            updates (Dict[str, Any]): Zu aktualisierende Werte
            save_immediately (bool): Sofort speichern
            
        Returns:
            bool: True bei Erfolg
        """
        try:
            changed_values = {}
            
            for key, value in updates.items():
                if hasattr(self.config, key):
                    old_value = getattr(self.config, key)
                    setattr(self.config, key, value)
                    changed_values[key] = {'new': value, 'old': old_value}
                else:
                    Logger.warning(f"Konfigurationsschlüssel '{key}' nicht gültig")
            
            if changed_values and save_immediately:
                self.save_config()
            
            if changed_values:
                self._notify_listeners('config_batch_changed', changed_values)
                Logger.debug(f"{len(changed_values)} Konfigurationswerte aktualisiert")
            
            return True
            
        except Exception as e:
            Logger.error(f"Fehler beim Batch-Update der Konfiguration: {str(e)}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Setzt die Konfiguration auf Standardwerte zurück
        
        Returns:
            bool: True bei Erfolg
        """
        try:
            self.config = AppConfig()
            self.save_config()
            Logger.info("Konfiguration auf Standardwerte zurückgesetzt")
            self._notify_listeners('config_reset', self.config)
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Zurücksetzen der Konfiguration: {str(e)}")
            return False
    
    def export_config(self, export_path: Union[str, Path]) -> bool:
        """
        Exportiert die Konfiguration in eine andere Datei
        
        Args:
            export_path (Union[str, Path]): Export-Pfad
            
        Returns:
            bool: True bei Erfolg
        """
        try:
            export_path = Path(export_path)
            config_dict = asdict(self.config)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            Logger.info(f"Konfiguration exportiert nach: {export_path}")
            return True
            
        except Exception as e:
            Logger.error(f"Fehler beim Exportieren der Konfiguration: {str(e)}")
            return False
    
    def import_config(self, import_path: Union[str, Path]) -> bool:
        """
        Importiert eine Konfiguration aus einer Datei
        
        Args:
            import_path (Union[str, Path]): Import-Pfad
            
        Returns:
            bool: True bei Erfolg
        """
        try:
            import_path = Path(import_path)
            
            if not import_path.exists():
                Logger.error(f"Import-Datei nicht gefunden: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Konfiguration validieren und laden
            self.config = AppConfig(**data)
            self.save_config()
            
            Logger.info(f"Konfiguration importiert von: {import_path}")
            self._notify_listeners('config_imported', self.config)
            return True
            
        except Exception as e:
            Logger.error(f"Fehler beim Importieren der Konfiguration: {str(e)}")
            return False
    
    def add_listener(self, event: str, callback):
        """
        Fügt einen Listener für Konfigurationsänderungen hinzu
        
        Args:
            event (str): Event-Typ
            callback: Callback-Funktion
        """
        if event not in self._listeners:
            self._listeners[event] = []
        
        if callback not in self._listeners[event]:
            self._listeners[event].append(callback)
            Logger.debug(f"Config-Listener für '{event}' hinzugefügt")
    
    def remove_listener(self, event: str, callback):
        """
        Entfernt einen Listener
        
        Args:
            event (str): Event-Typ
            callback: Callback-Funktion
        """
        if event in self._listeners and callback in self._listeners[event]:
            self._listeners[event].remove(callback)
            Logger.debug(f"Config-Listener für '{event}' entfernt")
    
    def _notify_listeners(self, event: str, data: Any):
        """
        Benachrichtigt Listener über Änderungen
        
        Args:
            event (str): Event-Typ
            data (Any): Event-Daten
        """
        if event in self._listeners:
            for callback in self._listeners[event]:
                try:
                    callback(data)
                except Exception as e:
                    Logger.error(f"Fehler beim Benachrichtigen des Config-Listeners: {str(e)}")
    
    def get_config_dict(self) -> Dict[str, Any]:
        """
        Gibt die Konfiguration als Dictionary zurück
        
        Returns:
            Dict[str, Any]: Konfiguration
        """
        return asdict(self.config)
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validiert die aktuelle Konfiguration
        
        Returns:
            Dict[str, Any]: Validierungsergebnis
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Theme-Validierung
            valid_themes = ['Light', 'Dark']
            if self.config.theme_style not in valid_themes:
                validation_result['errors'].append(f"Ungültiger Theme-Stil: {self.config.theme_style}")
                validation_result['valid'] = False
            
            # Numerische Werte validieren
            if self.config.default_attribute_points < 0:
                validation_result['errors'].append("Attributpunkte dürfen nicht negativ sein")
                validation_result['valid'] = False
            
            if self.config.default_skill_points < 0:
                validation_result['errors'].append("Fertigkeitspunkte dürfen nicht negativ sein")
                validation_result['valid'] = False
            
            # Weitere Validierungen...
            
        except Exception as e:
            validation_result['errors'].append(f"Validierungsfehler: {str(e)}")
            validation_result['valid'] = False
        
        return validation_result
    
    def cleanup(self):
        """Bereinigt den Config-Service"""
        Logger.info("ConfigService wird bereinigt...")
        self.save_config()
        self._listeners.clear()
        Logger.info("ConfigService bereinigt")


# Convenience-Funktionen
def get_app_config() -> Optional[AppConfig]:
    """Gibt die aktuelle App-Konfiguration zurück"""
    from services.service_container import service_container
    config_service = service_container.get_config_service()
    return config_service.config if config_service else None

def set_config_value(key: str, value: Any) -> bool:
    """Setzt einen Konfigurationswert"""
    from services.service_container import service_container
    config_service = service_container.get_config_service()
    return config_service.set(key, value) if config_service else False

def get_config_value(key: str, default: Any = None) -> Any:
    """Holt einen Konfigurationswert"""
    from services.service_container import service_container
    config_service = service_container.get_config_service()
    return config_service.get(key, default) if config_service else default