# services/service_container.py
"""
Service Container für Dependency Injection
Zentralisiert die Verwaltung aller Services
"""

from kivy.logger import Logger
from kivy.app import App
from typing import Optional, Dict, Any

# Service Imports
from services.theme_service import ThemeService
from services.file_manager_service import FileManagerService
from services.pdf_service import PDFService
from services.html_service import HTMLService
from services.dialog_service import DialogService
from services.event_service import EventService
from services.config_service import ConfigService
from services.backup_service import BackupService
from services.tutorial_service import TutorialService
from services.wizard_service import WizardService


class ServiceContainer:
    """
    Dependency Injection Container für alle Services
    Implementiert Singleton-Pattern für Service-Instanzen
    """
    
    _instance = None
    _services: Dict[str, Any] = {}
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            Logger.info("ServiceContainer initialisiert")
    
    def initialize(self, charakter_controller):
        """
        Initialisiert alle Services mit den erforderlichen Abhängigkeiten
        
        Args:
            charakter_controller: Der Hauptcontroller für Charakterverwaltung
        """
        try:
            app = App.get_running_app()
            theme_cls = app.theme_cls if app else None
            
            # Core Services
            self._services['config'] = ConfigService()
            self._services['event'] = EventService()
            self._services['theme'] = ThemeService()
            self._services['backup'] = BackupService(self._services['config'])
            self._services['tutorial'] = TutorialService(self._services['config'])
            self._services['wizard'] = WizardService()
            
            # Controller-abhängige Services
            if charakter_controller:
                # Controller selbst registrieren
                self._services['charakter_controller'] = charakter_controller
                
                self._services['file_manager'] = FileManagerService(charakter_controller)
                self._services['pdf'] = PDFService(charakter_controller)
                self._services['html'] = HTMLService(charakter_controller)
                
                if theme_cls:
                    self._services['dialog'] = DialogService(charakter_controller, theme_cls)
            
            Logger.info("Alle Services erfolgreich initialisiert")
            
            # Event über erfolgreiche Initialisierung senden
            if 'event' in self._services:
                self._services['event'].publish('services_initialized', self._services.keys())
                
        except Exception as e:
            Logger.error(f"Fehler bei Service-Initialisierung: {str(e)}", exc_info=True)
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """
        Gibt einen Service zurück
        
        Args:
            service_name (str): Name des Services
            
        Returns:
            Service-Instanz oder None
        """
        service = self._services.get(service_name)
        if not service:
            Logger.warning(f"Service '{service_name}' nicht gefunden oder nicht initialisiert")
        return service
    
    def get_theme_service(self) -> Optional[ThemeService]:
        """Gibt den Theme-Service zurück"""
        return self.get_service('theme')
    
    def get_file_manager_service(self) -> Optional[FileManagerService]:
        """Gibt den FileManager-Service zurück"""
        return self.get_service('file_manager')
    
    def get_pdf_service(self) -> Optional[PDFService]:
        """Gibt den PDF-Service zurück"""
        return self.get_service('pdf')

    def get_html_service(self) -> Optional[HTMLService]:
        """Gibt den HTML-Service zurück"""
        return self.get_service('html')
    
    def get_dialog_service(self) -> Optional[DialogService]:
        """Gibt den Dialog-Service zurück"""
        return self.get_service('dialog')
    
    def get_event_service(self) -> Optional[EventService]:
        """Gibt den Event-Service zurück"""
        return self.get_service('event')
    
    def get_config_service(self) -> Optional[ConfigService]:
        """Gibt den Config-Service zurück"""
        return self.get_service('config')
    
    def get_backup_service(self) -> Optional[BackupService]:
        """Gibt den Backup-Service zurück"""
        return self.get_service('backup')
    
    def get_tutorial_service(self) -> Optional[TutorialService]:
        """Gibt den Tutorial-Service zurück"""
        return self.get_service('tutorial')
    
    def get_wizard_service(self) -> Optional[WizardService]:
        """Gibt den Wizard-Service zurück"""
        return self.get_service('wizard')

    def get_charakter_controller(self):
        """Gibt den Charakter-Controller zurück"""
        return self.get_service('charakter_controller')
    
    def register_service(self, name: str, service: Any):
        """
        Registriert einen neuen Service
        
        Args:
            name (str): Service-Name
            service: Service-Instanz
        """
        self._services[name] = service
        Logger.info(f"Service '{name}' registriert")
        
        # Event senden
        if 'event' in self._services:
            self._services['event'].publish('service_registered', {'name': name, 'service': service})
    
    def unregister_service(self, name: str):
        """
        Entfernt einen Service
        
        Args:
            name (str): Service-Name
        """
        if name in self._services:
            del self._services[name]
            Logger.info(f"Service '{name}' entfernt")
            
            # Event senden
            if 'event' in self._services:
                self._services['event'].publish('service_unregistered', {'name': name})
    
    def is_service_available(self, service_name: str) -> bool:
        """
        Prüft, ob ein Service verfügbar ist
        
        Args:
            service_name (str): Service-Name
            
        Returns:
            bool: True wenn verfügbar
        """
        return service_name in self._services and self._services[service_name] is not None
    
    def get_service_status(self) -> Dict[str, bool]:
        """
        Gibt den Status aller Services zurück
        
        Returns:
            dict: Service-Name -> Verfügbarkeit
        """
        return {name: service is not None for name, service in self._services.items()}
    
    def shutdown(self):
        """Beendet alle Services ordnungsgemäß"""
        Logger.info("ServiceContainer wird heruntergefahren...")
        
        # Event senden
        if 'event' in self._services:
            self._services['event'].publish('services_shutdown')
        
        # Services mit cleanup-Methoden aufrufen
        for name, service in self._services.items():
            try:
                if hasattr(service, 'cleanup'):
                    service.cleanup()
                    Logger.debug(f"Service '{name}' cleanup durchgeführt")
            except Exception as e:
                Logger.error(f"Fehler beim Cleanup von Service '{name}': {str(e)}")
        
        # Services entfernen
        self._services.clear()
        Logger.info("ServiceContainer heruntergefahren")


# Globale Service-Container-Instanz
service_container = ServiceContainer()


# Decorator für Service-Injection
def inject_service(service_name: str):
    """
    Decorator für automatische Service-Injection
    
    Args:
        service_name (str): Name des zu injizierenden Services
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            service = service_container.get_service(service_name)
            if service:
                return func(self, service, *args, **kwargs)
            else:
                Logger.error(f"Service '{service_name}' für {func.__name__} nicht verfügbar")
                return None
        return wrapper
    return decorator


# Convenience-Funktionen
def get_theme_service() -> Optional[ThemeService]:
    """Gibt den Theme-Service zurück"""
    return service_container.get_theme_service()

def get_dialog_service() -> Optional[DialogService]:
    """Gibt den Dialog-Service zurück"""
    return service_container.get_dialog_service()

def get_file_service() -> Optional[FileManagerService]:
    """Gibt den FileManager-Service zurück"""
    return service_container.get_file_manager_service()

def get_pdf_service() -> Optional[PDFService]:
    """Gibt den PDF-Service zurück"""
    return service_container.get_pdf_service()

def get_html_service() -> Optional[HTMLService]:
    """Gibt den HTML-Service zurück"""
    return service_container.get_html_service()

def get_event_service() -> Optional[EventService]:
    """Gibt den Event-Service zurück"""
    return service_container.get_event_service()

def get_config_service() -> Optional[ConfigService]:
    """Gibt den Config-Service zurück"""
    return service_container.get_config_service()

def get_backup_service() -> Optional[BackupService]:
    """Gibt den Backup-Service zurück"""
    return service_container.get_backup_service()

def get_tutorial_service() -> Optional[TutorialService]:
    """Gibt den Tutorial-Service zurück"""
    return service_container.get_tutorial_service()