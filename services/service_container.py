# services/service_container.py
"""
Service Container für Dependency Injection
Zentralisiert die Verwaltung aller Services
"""

import time
from kivy.logger import Logger
from kivy.app import App
from typing import Optional, Dict, Any, Callable

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

    Services werden teilweise lazy initialisiert: Nicht-kritische Services
    (`backup`, `tutorial`, `pdf`, `html`) werden erst beim ersten Zugriff
    erzeugt — das spart Startup-Zeit auf Android.
    """

    _instance = None
    _services: Dict[str, Any] = {}
    _lazy_factories: Dict[str, Callable[[], Any]] = {}
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
        Initialisiert alle Services mit den erforderlichen Abhängigkeiten.

        Kernservices werden sofort instanziiert, nicht-kritische Services
        nur als Factory registriert und beim ersten Zugriff erzeugt.

        Args:
            charakter_controller: Der Hauptcontroller für Charakterverwaltung
        """
        try:
            app = App.get_running_app()
            theme_cls = app.theme_cls if app else None

            # --- Kernservices (eager) ---
            self._services['config'] = ConfigService()
            self._services['event'] = EventService()
            self._services['theme'] = ThemeService()
            self._services['wizard'] = WizardService()

            # --- Nicht-kritische Services als Lazy-Factories registrieren ---
            # WICHTIG: Erst alle Factories registrieren, dann erst eager construieren.
            # So bleiben Factories registriert, auch wenn ein eager-Service-Constructor
            # später scheitert.
            config_service = self._services['config']
            self._lazy_factories['backup'] = lambda: BackupService(config_service)
            self._lazy_factories['tutorial'] = lambda: TutorialService(config_service)

            if charakter_controller:
                self._lazy_factories['pdf'] = lambda: PDFService(charakter_controller)
                self._lazy_factories['html'] = lambda: HTMLService(charakter_controller)

            # --- Controller-abhängige eager Services ---
            if charakter_controller:
                # Controller selbst registrieren
                self._services['charakter_controller'] = charakter_controller

                # FileManager wird früh gebraucht (Auto-Load) → eager
                try:
                    self._services['file_manager'] = FileManagerService(charakter_controller)
                except Exception as e:
                    Logger.error(f"FileManagerService-Init fehlgeschlagen: {e}", exc_info=True)

                if theme_cls:
                    # Dialog wird bei fast jeder Nutzeraktion gebraucht → eager
                    try:
                        self._services['dialog'] = DialogService(charakter_controller, theme_cls)
                    except Exception as e:
                        Logger.error(f"DialogService-Init fehlgeschlagen: {e}", exc_info=True)

            eager = sorted(self._services.keys())
            lazy = sorted(self._lazy_factories.keys())
            Logger.info(
                f"ServiceContainer: {len(eager)} eager Services "
                f"({', '.join(eager)}), {len(lazy)} lazy Services "
                f"({', '.join(lazy)})"
            )

            # Event über erfolgreiche Initialisierung senden (nur eager Services)
            if 'event' in self._services:
                self._services['event'].publish('services_initialized', list(self._services.keys()))

        except Exception as e:
            Logger.error(f"Fehler bei Service-Initialisierung: {str(e)}", exc_info=True)
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """
        Gibt einen Service zurück. Erzeugt Lazy-Services beim ersten Zugriff.

        Args:
            service_name (str): Name des Services

        Returns:
            Service-Instanz oder None
        """
        service = self._services.get(service_name)
        if service is not None:
            return service

        # Lazy-Factory vorhanden? → jetzt erzeugen
        factory = self._lazy_factories.get(service_name)
        if factory is not None:
            try:
                start = time.monotonic()
                service = factory()
                elapsed_ms = (time.monotonic() - start) * 1000.0
                self._services[service_name] = service
                # Factory nur einmal aufrufen
                del self._lazy_factories[service_name]
                Logger.info(
                    f"Lazy-Service: '{service_name}' in {elapsed_ms:.1f} ms instanziiert"
                )

                # Event senden, falls EventService verfügbar
                event_service = self._services.get('event')
                if event_service and service_name != 'event':
                    try:
                        event_service.publish(
                            'service_lazy_initialized',
                            {'name': service_name, 'elapsed_ms': elapsed_ms}
                        )
                    except Exception:
                        pass  # Event-Fehler darf Service-Nutzung nicht blockieren

                return service
            except Exception as e:
                Logger.error(
                    f"Fehler beim Lazy-Init von Service '{service_name}': {str(e)}",
                    exc_info=True
                )
                return None

        Logger.warning(f"Service '{service_name}' nicht gefunden oder nicht initialisiert")
        return None
    
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
        Prüft, ob ein Service verfügbar ist (bereits instanziiert oder
        via Lazy-Factory verfügbar).

        Args:
            service_name (str): Service-Name

        Returns:
            bool: True wenn verfügbar
        """
        if service_name in self._services and self._services[service_name] is not None:
            return True
        return service_name in self._lazy_factories

    def is_service_loaded(self, service_name: str) -> bool:
        """
        Prüft, ob ein Service tatsächlich bereits instanziiert wurde.

        Nützlich für Shutdown-Pfade und Tests, um Lazy-Services nicht
        unnötig zu materialisieren.

        Args:
            service_name (str): Service-Name

        Returns:
            bool: True wenn Service bereits erzeugt wurde
        """
        return service_name in self._services and self._services[service_name] is not None

    def get_service_status(self) -> Dict[str, bool]:
        """
        Gibt den Status aller Services zurück.

        Lazy-Services, die noch nicht instanziiert wurden, erscheinen mit
        `False`.

        Returns:
            dict: Service-Name -> bereits instanziiert
        """
        status = {name: service is not None for name, service in self._services.items()}
        for lazy_name in self._lazy_factories:
            status.setdefault(lazy_name, False)
        return status
    
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
        self._lazy_factories.clear()
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