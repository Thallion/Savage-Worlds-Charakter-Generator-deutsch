# models/setting_draft.py
"""
Modell für Setting-Drafts mit Metadaten.
Drafts ermöglichen das Zwischen speichern unfertiger Settings.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from kivy.logger import Logger


class SettingDraft:
    """
    Repräsentiert einen unfertigen Setting-Entwurf.
    Wird als JSON-Datei im User-Settings-Verzeichnis gespeichert.
    """
    
    DRAFT_PREFIX = "_draft_"
    
    def __init__(
        self,
        name: str,
        mode: str = "template",
        base_settings: Optional[List[str]] = None,
        description: str = "",
        current_step: int = 1,
        setting_data: Optional[Dict[str, Any]] = None,
        conflicts_resolved: int = 0,
        conflicts_remaining: int = 0,
        created: Optional[str] = None,
        last_modified: Optional[str] = None
    ):
        self.name = name
        self.mode = mode  # "empty", "template", "merge", "extract"
        self.base_settings = base_settings or []
        self.description = description
        self.current_step = current_step
        self.setting_data = setting_data or {}
        self.conflicts_resolved = conflicts_resolved
        self.conflicts_remaining = conflicts_remaining
        
        now = datetime.now().isoformat()
        self.created = created or now
        self.last_modified = last_modified or now
    
    @property
    def is_draft(self) -> bool:
        return True
    
    @property
    def draft_filename(self) -> str:
        return f"{self.DRAFT_PREFIX}{self.name}.json"
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert den Draft in ein Dictionary für JSON-Serialisierung."""
        return {
            "_draft": True,
            "_created": self.created,
            "_last_modified": self.last_modified,
            "_base_settings": self.base_settings,
            "_mode": self.mode,
            "_current_step": self.current_step,
            "_conflicts_resolved": self.conflicts_resolved,
            "_conflicts_remaining": self.conflicts_remaining,
            "name": self.name,
            "description": self.description,
            **self.setting_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SettingDraft":
        """Erstellt einen Draft aus einem Dictionary."""
        base_settings = data.pop("_base_settings", [])
        mode = data.pop("_mode", "template")
        current_step = data.pop("_current_step", 1)
        conflicts_resolved = data.pop("_conflicts_resolved", 0)
        conflicts_remaining = data.pop("_conflicts_remaining", 0)
        created = data.pop("_created", None)
        last_modified = data.pop("_last_modified", None)
        data.pop("_draft", None)
        
        name = data.pop("name", "Unnamed")
        description = data.pop("description", "")
        
        return cls(
            name=name,
            mode=mode,
            base_settings=base_settings,
            description=description,
            current_step=current_step,
            setting_data=data,
            conflicts_resolved=conflicts_resolved,
            conflicts_remaining=conflicts_remaining,
            created=created,
            last_modified=last_modified
        )
    
    def update_timestamp(self):
        """Aktualisiert den Zeitstempel für die letzte Änderung."""
        self.last_modified = datetime.now().isoformat()
    
    def to_final_setting(self) -> Dict[str, Any]:
        """Konvertiert den Draft in ein finales Setting-Dictionary ohne Draft-Metadaten."""
        result = {
            "name": self.name,
            "description": self.description,
        }
        
        for key, value in self.setting_data.items():
            if not key.startswith("_"):
                result[key] = value
        
        return result


class DraftManager:
    """
    Verwaltet das Laden, Speichern und Löschen von Drafts.
    """
    
    def __init__(self, drafts_dir: Optional[Path] = None):
        from utils.path_utils import get_user_settings_path
        
        if drafts_dir is None:
            self.drafts_dir = Path(get_user_settings_path()) / "drafts"
        else:
            self.drafts_dir = Path(drafts_dir)
        
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        self._drafts_cache: Dict[str, SettingDraft] = {}
    
    def get_draft_path(self, name: str) -> Path:
        """Gibt den Dateipfad für einen Draft zurück."""
        safe_name = self._sanitize_filename(name)
        return self.drafts_dir / f"{SettingDraft.DRAFT_PREFIX}{safe_name}.json"
    
    def _sanitize_filename(self, name: str) -> str:
        """Entfernt ungültige Zeichen aus dem Dateinamen."""
        import re
        safe = re.sub(r'[<>:"/\\|?*]', '_', name)
        return safe.strip()
    
    def save_draft(self, draft: SettingDraft) -> bool:
        """
        Speichert einen Draft als JSON-Datei.
        
        Args:
            draft: Der zu speichernde Draft
            
        Returns:
            True bei Erfolg
        """
        try:
            draft.update_timestamp()
            filepath = self.get_draft_path(draft.name)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(draft.to_dict(), f, ensure_ascii=False, indent=2)
            
            self._drafts_cache[draft.name] = draft
            Logger.info(f"Draft '{draft.name}' gespeichert unter {filepath}")
            return True
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Drafts: {e}")
            return False
    
    def load_draft(self, name: str) -> Optional[SettingDraft]:
        """
        Lädt einen Draft anhand seines Namens.
        
        Args:
            name: Der Name des Drafts
            
        Returns:
            SettingDraft oder None wenn nicht gefunden
        """
        if name in self._drafts_cache:
            return self._drafts_cache[name]
        
        try:
            filepath = self.get_draft_path(name)
            if not filepath.exists():
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            draft = SettingDraft.from_dict(data)
            self._drafts_cache[draft.name] = draft
            Logger.info(f"Draft '{name}' geladen")
            return draft
            
        except Exception as e:
            Logger.error(f"Fehler beim Laden des Drafts '{name}': {e}")
            return None
    
    def delete_draft(self, name: str) -> bool:
        """
        Löscht einen Draft.
        
        Args:
            name: Der Name des zu löschenden Drafts
            
        Returns:
            True bei Erfolg
        """
        try:
            filepath = self.get_draft_path(name)
            if filepath.exists():
                filepath.unlink()
            
            if name in self._drafts_cache:
                del self._drafts_cache[name]
            
            Logger.info(f"Draft '{name}' gelöscht")
            return True
            
        except Exception as e:
            Logger.error(f"Fehler beim Löschen des Drafts '{name}': {e}")
            return False
    
    def list_drafts(self) -> List[SettingDraft]:
        """
        Gibt eine Liste aller vorhandenen Drafts zurück.
        
        Returns:
            Liste von SettingDraft-Objekten
        """
        drafts = []
        
        try:
            for filepath in self.drafts_dir.glob(f"{SettingDraft.DRAFT_PREFIX}*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    draft = SettingDraft.from_dict(data)
                    drafts.append(draft)
                except Exception as e:
                    Logger.warning(f"Fehler beim Laden von Draft {filepath}: {e}")
            
            drafts.sort(key=lambda d: d.last_modified, reverse=True)
            
        except Exception as e:
            Logger.error(f"Fehler beim Auflisten der Drafts: {e}")
        
        return drafts
    
    def has_draft(self, name: str) -> bool:
        """Prüft ob ein Draft mit dem gegebenen Namen existiert."""
        if name in self._drafts_cache:
            return True
        return self.get_draft_path(name).exists()
    
    def clear_cache(self):
        """Leert den internen Cache."""
        self._drafts_cache.clear()


def create_empty_draft(name: str, description: str = "") -> SettingDraft:
    """Erstellt einen leeren Draft für den 'Leer starten' Modus."""
    return SettingDraft(
        name=name,
        mode="empty",
        description=description,
        setting_data=_get_empty_setting_template()
    )


def create_template_draft(name: str, base_setting: str, description: str = "") -> SettingDraft:
    """
    Erstellt einen Draft basierend auf einem bestehenden Setting.
    
    Args:
        name: Name des neuen Settings
        base_setting: Name des Basis-Settings
        description: Optionale Beschreibung
    """
    from functions.setting_funktionen import CustomElementManager
    from models.charakter import Charakter
    
    dummy_charakter = Charakter()
    manager = CustomElementManager(dummy_charakter)
    
    if base_setting not in manager.settings:
        Logger.warning(f"Base-Setting '{base_setting}' nicht gefunden, erstelle leeren Draft")
        return create_empty_draft(name, description)
    
    base_data = manager.settings[base_setting]
    
    setting_data = dict(base_data)
    
    if "fertigkeiten_daten" in setting_data and "fertigkeiten" not in setting_data:
        setting_data["fertigkeiten"] = dict(setting_data["fertigkeiten_daten"])
    
    return SettingDraft(
        name=name,
        mode="template",
        base_settings=[base_setting],
        description=description,
        setting_data=setting_data
    )


def create_merge_draft(name: str, base_settings: List[str], description: str = "") -> SettingDraft:
    """
    Erstellt einen Draft für das Zusammenführen mehrerer Settings.
    
    Args:
        name: Name des neuen Settings
        base_settings: Liste der zu merge-nenden Settings
        description: Optionale Beschreibung
    """
    from functions.setting_merge import merge_settings
    
    merged_data = merge_settings(base_settings)
    
    return SettingDraft(
        name=name,
        mode="merge",
        base_settings=base_settings,
        description=description,
        setting_data=merged_data
    )


def _get_empty_setting_template() -> Dict[str, Any]:
    """Gibt ein minimales Setting-Template zurück."""
    return {
        "voelker": {},
        "attribute": {
            "Stärke": {"basis_wert": 4},
            "Geschicklichkeit": {"basis_wert": 4},
            "Konstitution": {"basis_wert": 4},
            "Verstand": {"basis_wert": 4},
            "Willenskraft": {"basis_wert": 4}
        },
        "fertigkeiten": {},
        "fertigkeiten_daten": {},
        "talente": {},
        "handicaps": {},
        "maechte": {},
        "ausruestung": {
            "Kategorien": {
                "Waffen": {"aktiv": True},
                "Rüstungen": {"aktiv": True},
                "Ausrüstung": {"aktiv": True},
                "Transportmittel": {"aktiv": False}
            }
        },
        "settingregeln": {},
        "waehrung": {"symbol": "G", "name": "Gold"},
        "startgeld": 500
    }
