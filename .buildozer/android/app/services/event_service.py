# services/event_service.py
"""
Event-Service für anwendungsweite Event-Kommunikation
Implementiert Publisher-Subscriber Pattern
"""

from kivy.logger import Logger
from kivy.clock import Clock
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    """Event-Datenklasse"""
    event_type: str
    data: Any = None
    timestamp: datetime = None
    source: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EventService:
    """
    Service für Event-Management und -Kommunikation
    Ermöglicht lose gekoppelte Kommunikation zwischen Komponenten
    """
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        self._enabled = True
        
        Logger.info("EventService initialisiert")
    
    def subscribe(self, event_type: str, callback: Callable, source: str = None) -> bool:
        """
        Registriert einen Listener für einen Event-Typ
        
        Args:
            event_type (str): Typ des Events
            callback (Callable): Callback-Funktion
            source (str): Optionale Quellenangabe für Debugging
            
        Returns:
            bool: True bei Erfolg
        """
        try:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            
            if callback not in self._listeners[event_type]:
                self._listeners[event_type].append(callback)
                Logger.debug(f"Listener für '{event_type}' registriert (Quelle: {source})")
                return True
            else:
                Logger.warning(f"Listener für '{event_type}' bereits registriert")
                return False
                
        except Exception as e:
            Logger.error(f"Fehler beim Registrieren des Listeners: {str(e)}")
            return False
    
    def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """
        Entfernt einen Listener für einen Event-Typ
        
        Args:
            event_type (str): Typ des Events
            callback (Callable): Callback-Funktion
            
        Returns:
            bool: True bei Erfolg
        """
        try:
            if event_type in self._listeners and callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)
                Logger.debug(f"Listener für '{event_type}' entfernt")
                
                # Leere Listen entfernen
                if not self._listeners[event_type]:
                    del self._listeners[event_type]
                
                return True
            else:
                Logger.warning(f"Listener für '{event_type}' nicht gefunden")
                return False
                
        except Exception as e:
            Logger.error(f"Fehler beim Entfernen des Listeners: {str(e)}")
            return False
    
    def publish(self, event_type: str, data: Any = None, source: str = None, 
                async_callback: bool = False) -> bool:
        """
        Veröffentlicht ein Event
        
        Args:
            event_type (str): Typ des Events
            data (Any): Event-Daten
            source (str): Quelle des Events
            async_callback (bool): Ob Callbacks asynchron ausgeführt werden sollen
            
        Returns:
            bool: True bei Erfolg
        """
        if not self._enabled:
            return False
        
        try:
            event = Event(event_type=event_type, data=data, source=source)
            
            # Event zur Historie hinzufügen
            self._add_to_history(event)
            
            # Listeners benachrichtigen
            if event_type in self._listeners:
                listeners = self._listeners[event_type].copy()  # Kopie für Thread-Safety
                
                if async_callback:
                    # Asynchrone Ausführung über Clock
                    Clock.schedule_once(
                        lambda dt: self._notify_listeners(listeners, event), 0
                    )
                else:
                    # Synchrone Ausführung
                    self._notify_listeners(listeners, event)
                
                Logger.debug(f"Event '{event_type}' an {len(listeners)} Listener gesendet")
            else:
                Logger.debug(f"Keine Listener für Event '{event_type}' registriert")
            
            return True
            
        except Exception as e:
            Logger.error(f"Fehler beim Veröffentlichen des Events: {str(e)}")
            return False
    
    def _notify_listeners(self, listeners: List[Callable], event: Event):
        """
        Benachrichtigt alle Listener über ein Event
        
        Args:
            listeners (List[Callable]): Liste der Listener
            event (Event): Das Event
        """
        for listener in listeners:
            try:
                # Prüfen, ob Listener ein Event-Objekt oder nur Daten erwartet
                import inspect
                sig = inspect.signature(listener)
                
                if len(sig.parameters) > 1 or any(
                    param.name in ['event', 'event_obj'] for param in sig.parameters.values()
                ):
                    # Listener erwartet Event-Objekt
                    listener(event)
                else:
                    # Listener erwartet nur Daten
                    listener(event.data)
                    
            except Exception as e:
                Logger.error(f"Fehler beim Ausführen des Listeners: {str(e)}")
    
    def _add_to_history(self, event: Event):
        """
        Fügt ein Event zur Historie hinzu
        
        Args:
            event (Event): Das Event
        """
        self._event_history.append(event)
        
        # Historie-Größe begrenzen
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size:]
    
    def get_event_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """
        Gibt die Event-Historie zurück
        
        Args:
            event_type (str): Optionaler Filter für Event-Typ
            limit (int): Maximale Anzahl Events
            
        Returns:
            List[Event]: Event-Historie
        """
        history = self._event_history
        
        if event_type:
            history = [e for e in history if e.event_type == event_type]
        
        return history[-limit:] if limit > 0 else history
    
    def clear_history(self):
        """Löscht die Event-Historie"""
        self._event_history.clear()
        Logger.info("Event-Historie gelöscht")
    
    def get_listener_count(self, event_type: str = None) -> int:
        """
        Gibt die Anzahl der Listener zurück
        
        Args:
            event_type (str): Optionaler Event-Typ
            
        Returns:
            int: Anzahl der Listener
        """
        if event_type:
            return len(self._listeners.get(event_type, []))
        else:
            return sum(len(listeners) for listeners in self._listeners.values())
    
    def get_registered_events(self) -> List[str]:
        """
        Gibt alle registrierten Event-Typen zurück
        
        Returns:
            List[str]: Event-Typen
        """
        return list(self._listeners.keys())
    
    def enable(self):
        """Aktiviert den Event-Service"""
        self._enabled = True
        Logger.info("EventService aktiviert")
    
    def disable(self):
        """Deaktiviert den Event-Service"""
        self._enabled = False
        Logger.info("EventService deaktiviert")
    
    def is_enabled(self) -> bool:
        """Gibt zurück, ob der Event-Service aktiviert ist"""
        return self._enabled
    
    def publish_delayed(self, event_type: str, data: Any = None, 
                       delay_seconds: float = 1.0, source: str = None) -> bool:
        """
        Veröffentlicht ein Event mit Verzögerung
        
        Args:
            event_type (str): Typ des Events
            data (Any): Event-Daten
            delay_seconds (float): Verzögerung in Sekunden
            source (str): Quelle des Events
            
        Returns:
            bool: True bei Erfolg
        """
        try:
            Clock.schedule_once(
                lambda dt: self.publish(event_type, data, source), 
                delay_seconds
            )
            Logger.debug(f"Verzögertes Event '{event_type}' geplant ({delay_seconds}s)")
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Planen des verzögerten Events: {str(e)}")
            return False
    
    def cleanup(self):
        """Bereinigt den Event-Service"""
        Logger.info("EventService wird bereinigt...")
        self._listeners.clear()
        self._event_history.clear()
        self._enabled = False
        Logger.info("EventService bereinigt")


# Standard Event-Typen
class EventTypes:
    """Konstanten für Standard-Event-Typen"""
    
    # Charakter-Events
    CHARACTER_CREATED = "character_created"
    CHARACTER_LOADED = "character_loaded"
    CHARACTER_SAVED = "character_saved"
    CHARACTER_UPDATED = "character_updated"
    
    # Attribut-Events
    ATTRIBUTE_CHANGED = "attribute_changed"
    SKILL_CHANGED = "skill_changed"
    
    # UI-Events
    TAB_CHANGED = "tab_changed"
    THEME_CHANGED = "theme_changed"
    
    # Setting-Events
    SETTING_CHANGED = "setting_changed"
    SETTING_LOADED = "setting_loaded"
    
    # Service-Events
    SERVICES_INITIALIZED = "services_initialized"
    SERVICE_REGISTERED = "service_registered"
    SERVICE_UNREGISTERED = "service_unregistered"
    SERVICES_SHUTDOWN = "services_shutdown"
    
    # Dialog-Events
    DIALOG_OPENED = "dialog_opened"
    DIALOG_CLOSED = "dialog_closed"
    
    # File-Events
    FILE_LOADED = "file_loaded"
    FILE_SAVED = "file_saved"
    PDF_CREATED = "pdf_created"


# Convenience-Decorator für Event-Handler
def event_handler(event_type: str, service_ref: str = 'event_service'):
    """
    Decorator für automatische Event-Handler-Registrierung
    
    Args:
        event_type (str): Event-Typ
        service_ref (str): Name des Service-Attributs
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Event-Service aus der Instanz holen
            event_service = getattr(self, service_ref, None)
            if event_service:
                event_service.subscribe(event_type, func)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator