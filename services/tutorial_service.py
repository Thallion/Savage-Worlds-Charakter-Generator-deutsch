# services/tutorial_service.py
"""
Tutorial-Service für geführte Benutzer-Einführung.
Verwaltet Willkommens-Tutorial, kontextuelle Tab-Hilfen und Tutorial-Zustand.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from kivy.logger import Logger


class TutorialService:
    """
    Service für Tutorial-Management.
    Lädt Tutorial-Konfiguration und verwaltet den Anzeigestatus.
    """
    
    def __init__(self, config_service=None):
        self.config_service = config_service
        self._config = None
        self._tab_hints_shown: Dict[str, bool] = {}
        self._welcome_completed = False
        self._tutorial_config_path = None
        
        self._load_config()
    
    def _get_config_path(self) -> Path:
        """Gibt den Pfad zur Tutorial-Konfiguration zurück."""
        if self._tutorial_config_path:
            return self._tutorial_config_path
        
        from utils.path_utils import get_application_root
        return Path(get_application_root()) / 'config' / 'tutorial_config.json'
    
    def _load_config(self):
        """Lädt die Tutorial-Konfiguration."""
        try:
            config_path = self._get_config_path()
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                Logger.info(f"Tutorial-Konfiguration geladen von {config_path}")
            else:
                Logger.warning(f"Tutorial-Konfigurationsdatei nicht gefunden: {config_path}")
                self._config = self._get_default_config()
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Tutorial-Konfiguration: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Gibt eine Standard-Konfiguration zurück."""
        return {
            "tab_hints": {},
            "welcome_tutorial": {"steps": []}
        }
    
    def get_tab_hint(self, tab_id: str) -> Optional[Dict[str, str]]:
        """
        Gibt den Hilfe-Text für einen Tab zurück.
        
        Args:
            tab_id: Die ID des Tabs (z.B. 'speichern_laden', 'voelker')
            
        Returns:
            Dict mit 'title' und 'text' oder None
        """
        if not self._config:
            return None
        
        tab_hints = self._config.get('tab_hints', {})
        return tab_hints.get(tab_id)
    
    def get_all_tab_ids(self) -> List[str]:
        """Gibt eine Liste aller verfügbaren Tab-IDs zurück."""
        if not self._config:
            return []
        return list(self._config.get('tab_hints', {}).keys())
    
    def has_tab_hint_been_shown(self, tab_id: str) -> bool:
        """Prüft ob ein Tab-Hint bereits angezeigt wurde."""
        return self._tab_hints_shown.get(tab_id, False)
    
    def mark_tab_hint_as_shown(self, tab_id: str):
        """Markiert einen Tab-Hint als angezeigt."""
        self._tab_hints_shown[tab_id] = True
        self._save_state()
    
    def reset_all_tab_hints(self):
        """Setzt alle Tab-Hints zurück (werden wieder angezeigt)."""
        self._tab_hints_shown = {tab_id: False for tab_id in self.get_all_tab_ids()}
        self._save_state()
        Logger.info("Alle Tab-Hints zurückgesetzt")
    
    def is_welcome_completed(self) -> bool:
        """Prüft ob das Willkommens-Tutorial abgeschlossen wurde."""
        return self._welcome_completed
    
    def mark_welcome_completed(self):
        """Markiert das Willkommens-Tutorial als abgeschlossen."""
        self._welcome_completed = True
        self._save_state()
        Logger.info("Willkommens-Tutorial als abgeschlossen markiert")
    
    def reset_welcome(self):
        """Setzt das Willkommen-Tutorial zurück (kann erneut gezeigt werden)."""
        self._welcome_completed = False
        self._save_state()
        Logger.info("Willkommens-Tutorial zurückgesetzt")
    
    def get_welcome_steps(self) -> List[Dict[str, Any]]:
        """Gibt die Schritte des Willkommens-Tutorials zurück."""
        if not self._config:
            return []
        return self._config.get('welcome_tutorial', {}).get('steps', [])
    
    def should_show_welcome(self) -> bool:
        """Prüft ob das Willkommens-Tutorial gezeigt werden sollte."""
        return not self._welcome_completed
    
    def _save_state(self):
        """Speichert den Tutorial-Zustand in der App-Konfiguration."""
        try:
            if self.config_service:
                tutorial_state = {
                    "welcome_completed": self._welcome_completed,
                    "tab_hints_shown": self._tab_hints_shown
                }
                self.config_service.set('tutorial_state', tutorial_state)
                self.config_service.save_config()
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Tutorial-Zustands: {e}")
    
    def load_state(self, state: Dict[str, Any]):
        """Lädt den Tutorial-Zustand aus der App-Konfiguration."""
        if not state:
            return
        
        self._welcome_completed = state.get('welcome_completed', False)
        self._tab_hints_shown = state.get('tab_hints_shown', {})
        
        all_tabs = set(self.get_all_tab_ids())
        shown_tabs = set(self._tab_hints_shown.keys())
        if all_tabs != shown_tabs:
            for tab_id in all_tabs - shown_tabs:
                self._tab_hints_shown[tab_id] = False
    
    def get_next_unshown_tab_hint(self) -> Optional[tuple]:
        """
        Gibt den nächsten Tab zurück, dessen Hint noch nicht gezeigt wurde.
        
        Returns:
            Tuple (tab_id, hint_data) oder None
        """
        priority_order = [
            'speichern_laden',
            'voelker',
            'profil',
            'eigenschaften',
            'handicaps',
            'talente',
            'maechte',
            'ausruestung',
            'charakterbogen',
            'historie'
        ]
        
        for tab_id in priority_order:
            if not self.has_tab_hint_been_shown(tab_id):
                hint = self.get_tab_hint(tab_id)
                if hint:
                    return (tab_id, hint)
        
        return None
    
    def show_next_hint_if_available(self) -> bool:
        """
        Zeigt den nächsten verfügbaren Tab-Hint.
        
        Returns:
            True wenn ein Hint angezeigt wurde, False wenn keiner mehr verfügbar
        """
        next_hint = self.get_next_unshown_tab_hint()
        if next_hint:
            tab_id, hint = next_hint
            self.mark_tab_hint_as_shown(tab_id)
            return True
        return False


class TabHintManager:
    """
    Verwaltet die Anzeige von kontextuellen Tab-Hilfen.
    """
    
    def __init__(self, tutorial_service: TutorialService):
        self.tutorial_service = tutorial_service
        self._current_hint_dialog = None
    
    def check_and_show_hint_for_tab(self, tab_id: str) -> bool:
        """
        Prüft ob für den Tab ein Hint angezeigt werden sollte und zeigt ihn.
        
        Args:
            tab_id: Die ID des aktuellen Tabs
            
        Returns:
            True wenn ein Hint angezeigt wurde
        """
        if self.tutorial_service.has_tab_hint_been_shown(tab_id):
            return False
        
        hint = self.tutorial_service.get_tab_hint(tab_id)
        if not hint:
            return False
        
        self.tutorial_service.mark_tab_hint_as_shown(tab_id)
        return True
    
    def show_hint_manually(self, tab_id: str) -> bool:
        """
        Zeigt den Hint für einen Tab manuell (unabhängig vom Status).
        
        Args:
            tab_id: Die ID des Tabs
            
        Returns:
            True wenn ein Hint angezeigt wurde
        """
        hint = self.tutorial_service.get_tab_hint(tab_id)
        if not hint:
            return False
        
        return True
    
    def show_all_hints(self) -> List[str]:
        """
        Zeigt alle verfügbaren Tab-Hints der Reihe nach.
        
        Returns:
            Liste der angezeigten Tab-IDs
        """
        shown = []
        for tab_id in self.tutorial_service.get_all_tab_ids():
            if self.tutorial_service.get_tab_hint(tab_id):
                shown.append(tab_id)
        return shown
