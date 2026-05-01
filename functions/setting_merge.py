# functions/setting_merge.py
"""
Merge-Logik für das Zusammenführen mehrerer Settings.
Implementiert Deep-Merge auf Element-Ebene mit Konflikterkennung.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from kivy.logger import Logger


def merge_settings(settings_list: List[str]) -> Dict[str, Any]:
    """
    Führt mehrere Settings zu einem zusammen.
    
    Args:
        settings_list: Liste von Setting-Namen zum Zusammenführen
        
    Returns:
        Das zusammengeführte Setting-Dictionary
    """
    if not settings_list:
        return {}
    
    if len(settings_list) == 1:
        return _load_single_setting(settings_list[0])
    
    result = {}
    conflicts = []
    
    for setting_name in settings_list:
        setting_data = _load_single_setting(setting_name)
        result, new_conflicts = _deep_merge(result, setting_data, setting_name, conflicts)
        conflicts.extend(new_conflicts)
    
    result["_merge_conflicts"] = conflicts
    
    return result


def _load_single_setting(setting_name: str) -> Dict[str, Any]:
    """Lädt ein einzelnes Setting."""
    try:
        from models.charakter import Charakter
        from functions.setting_funktionen import CustomElementManager
        
        dummy_charakter = Charakter()
        manager = CustomElementManager(dummy_charakter)
        
        if setting_name in manager.settings:
            return dict(manager.settings[setting_name])
        else:
            Logger.warning(f"Setting '{setting_name}' nicht gefunden")
            return {}
    except Exception as e:
        Logger.error(f"Fehler beim Laden von Setting '{setting_name}': {e}")
        return {}


def _deep_merge(
    base: Dict[str, Any],
    overlay: Dict[str, Any],
    source_name: str,
    existing_conflicts: List[Dict[str, Any]]
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Führt zwei Dictionaries rekursiv zusammen.
    
    Args:
        base: Das Basis-Dictionary
        overlay: Das Dictionary das hinzugefügt werden soll
        source_name: Name der Quelle für Konflikte
        existing_conflicts: Liste der bereits bekannten Konflikte
        
    Returns:
        Tuple von (result, conflicts)
    """
    result = dict(base)
    conflicts = list(existing_conflicts)
    
    for key, value in overlay.items():
        if key.startswith("_"):
            if key not in result:
                result[key] = value
            continue
        
        if key not in result:
            result[key] = value
        elif isinstance(value, dict) and isinstance(result[key], dict):
            result[key], new_conflicts = _deep_merge(result[key], value, source_name, [])
            conflicts.extend(new_conflicts)
        elif isinstance(value, list) and isinstance(result[key], list):
            result[key] = _merge_lists(result[key], value, key, source_name, conflicts)
        elif value != result[key]:
            conflict = _detect_conflict(key, result[key], value, source_name)
            if conflict:
                conflicts.append(conflict)
                result[key] = _resolve_conflict_default(result[key], value)
        elif isinstance(value, list) and not isinstance(result[key], list):
            result[key] = value
        elif isinstance(value, dict) and not isinstance(result[key], dict):
            result[key] = value
    
    return result, conflicts


def _merge_lists(
    base_list: List[Any],
    overlay_list: List[Any],
    category: str,
    source_name: str,
    existing_conflicts: List[Dict[str, Any]]
) -> List[Any]:
    """
    Führt zwei Listen zusammen (für Völker, Talente, etc.).
    Überschreibt Duplikate, fügt neue Elemente hinzu.
    """
    result = []
    seen_keys = set()
    
    for item in base_list:
        if isinstance(item, dict) and "name" in item:
            key = item["name"]
            result.append(item)
            seen_keys.add(key)
        elif isinstance(item, dict) and "id" in item:
            key = item["id"]
            result.append(item)
            seen_keys.add(key)
        elif isinstance(item, str):
            result.append(item)
            seen_keys.add(item)
        else:
            result.append(item)
    
    for item in overlay_list:
        if isinstance(item, dict):
            if "name" in item:
                key = item["name"]
                existing = _find_by_key(result, key, "name")
                if existing is not None:
                    if existing != item:
                        conflicts = existing_conflicts
                        conflicts.append({
                            "type": "overwrite",
                            "category": category,
                            "key": key,
                            "source": source_name,
                            "old_value": existing,
                            "new_value": item
                        })
                    result = [i for i in result if _get_key(i) != key]
                result.append(item)
                seen_keys.add(key)
            elif "id" in item:
                key = item["id"]
                result = [i for i in result if _get_key(i) != key]
                result.append(item)
                seen_keys.add(key)
            else:
                result.append(item)
        elif isinstance(item, str):
            if item not in seen_keys:
                result.append(item)
                seen_keys.add(item)
        else:
            result.append(item)
    
    return result


def _find_by_key(items: List[Any], key: str, key_name: str = "name") -> Optional[Any]:
    """Findet ein Element in einer Liste anhand seines Schlüssels."""
    for item in items:
        if isinstance(item, dict) and item.get(key_name) == key:
            return item
    return None


def _get_key(item: Any) -> Optional[str]:
    """Extrahiert den Schlüssel aus einem Element."""
    if isinstance(item, dict):
        return item.get("name") or item.get("id")
    elif isinstance(item, str):
        return item
    return None


def _detect_conflict(
    key: str,
    old_value: Any,
    new_value: Any,
    source_name: str
) -> Optional[Dict[str, Any]]:
    """
    Erkennt einen Konflikt zwischen zwei Werten.
    
    Returns:
        Konflikt-Dictionary oder None wenn kein Konflikt
    """
    if old_value == new_value:
        return None
    
    return {
        "type": "value_mismatch",
        "key": key,
        "source": source_name,
        "old_value": old_value,
        "new_value": new_value
    }


def _resolve_conflict_default(old_value: Any, new_value: Any) -> Any:
    """
    Standard-Konfliktlösung: Überschreibt mit neuem Wert.
    """
    return new_value


def get_merge_conflicts(merged_setting: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrahiert die Konfliktliste aus einem zusammengeführten Setting.
    
    Args:
        merged_setting: Das Ergebnis von merge_settings()
        
    Returns:
        Liste der Konflikte
    """
    return merged_setting.get("_merge_conflicts", [])


def resolve_conflict(
    merged_setting: Dict[str, Any],
    conflict_index: int,
    resolution: str
) -> Dict[str, Any]:
    """
    Löst einen Konflikt in einem zusammengeführten Setting.
    
    Args:
        merged_setting: Das zusammengeführte Setting
        conflict_index: Index des Konflikts in der Liste
        resolution: "keep_old", "use_new", oder "custom"
        
    Returns:
        Das modifizierte Setting
    """
    conflicts = get_merge_conflicts(merged_setting)
    
    if conflict_index >= len(conflicts):
        Logger.warning(f"Konflikt-Index {conflict_index} nicht gefunden")
        return merged_setting
    
    conflict = conflicts[conflict_index]
    conflict["resolved"] = resolution
    
    return merged_setting


def calculate_setting_statistics(setting_data: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    """
    Berechnet Statistiken für ein Setting.
    
    Args:
        setting_data: Das Setting-Dictionary
        
    Returns:
        Dictionary mit Statistiken pro Kategorie
    """
    stats = {}
    
    categories = [
        ("voelker", "Abstammungen"),
        ("fertigkeiten", "Fertigkeiten"),
        ("talente", "Talente"),
        ("handicaps", "Handicaps"),
        ("maechte", "Mächte"),
        ("ausruestung", "Ausrüstung")
    ]
    
    for key, label in categories:
        if key in setting_data:
            data = setting_data[key]
            if isinstance(data, dict):
                active = sum(1 for v in data.values() if _is_active(v))
                inactive = len(data) - active
                stats[label] = {"aktiv": active, "inaktiv": inactive, "gesamt": len(data)}
            elif isinstance(data, list):
                stats[label] = {"aktiv": len(data), "inaktiv": 0, "gesamt": len(data)}
        elif key == "fertigkeiten" and "fertigkeiten_daten" in setting_data:
            data = setting_data["fertigkeiten_daten"]
            if isinstance(data, dict):
                active = sum(1 for v in data.values() if _is_active(v))
                inactive = len(data) - active
                stats[label] = {"aktiv": active, "inaktiv": inactive, "gesamt": len(data)}
            elif isinstance(data, list):
                stats[label] = {"aktiv": len(data), "inaktiv": 0, "gesamt": len(data)}
        else:
            stats[label] = {"aktiv": 0, "inaktiv": 0, "gesamt": 0}
    
    return stats


def _is_active(element: Any) -> bool:
    """Prüft ob ein Element als aktiv markiert ist."""
    if isinstance(element, dict):
        return element.get("aktiv", True)
    return True


def format_statistics_for_display(stats: Dict[str, Dict[str, int]]) -> str:
    """
    Formatiert Statistiken für die Anzeige.
    
    Args:
        stats: Das Ergebnis von calculate_setting_statistics()
        
    Returns:
        Formatierter String
    """
    lines = []
    
    for category, values in stats.items():
        gesamt = values.get("gesamt", 0)
        aktiv = values.get("aktiv", 0)
        inaktiv = values.get("inaktiv", 0)
        
        if inaktiv > 0:
            lines.append(f"{category}: {aktiv} aktiv / {inaktiv} inaktiv")
        else:
            lines.append(f"{category}: {aktiv}")
    
    return "\n".join(lines)
