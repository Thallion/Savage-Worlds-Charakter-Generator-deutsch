"""
Zentrale Pfad-Utilities für PyInstaller-kompatible Pfade
"""
import sys
import os
from pathlib import Path

def get_resource_path(relative_path: str) -> str:
    """
    Gibt den korrekten Pfad zu einer Ressource zurück, sowohl im Development als auch in der gepackten EXE.
    
    Args:
        relative_path (str): Relativer Pfad zur Ressource (z.B. 'assets/logo.png' oder 'chars/character.json')
        
    Returns:
        str: Absoluter Pfad zur Ressource
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
        else:
            # Fallback für andere Packer wie cx_Freeze
            base_path = Path(sys.executable).parent
    else:
        # Development-Modus: Verwende das Projektverzeichnis
        base_path = Path(__file__).parent.parent.resolve()
    
    resource_path = base_path / relative_path
    return str(resource_path)

def get_application_root() -> Path:
    """
    Ermittelt das Hauptverzeichnis der Anwendung (kompatibel mit PyInstaller).
    
    Returns:
        Path: Das Hauptverzeichnis der Anwendung
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            app_root = Path(sys._MEIPASS)
        else:
            # Fallback für andere Packer wie cx_Freeze
            app_root = Path(sys.executable).parent
    else:
        # Development-Modus
        app_root = Path(__file__).parent.parent.resolve()
    
    return app_root

def get_assets_path(filename: str = "") -> str:
    """
    Gibt den Pfad zum Assets-Verzeichnis oder einer spezifischen Asset-Datei zurück.
    
    Args:
        filename (str): Optional - Name der Asset-Datei
        
    Returns:
        str: Pfad zum Assets-Verzeichnis oder zur Asset-Datei
    """
    if filename:
        return get_resource_path(f"assets/{filename}")
    else:
        return get_resource_path("assets")

def get_chars_path(filename: str = "") -> str:
    """
    Gibt den Pfad zum Chars-Verzeichnis oder einer spezifischen Char-Datei zurück.
    
    Args:
        filename (str): Optional - Name der Char-Datei
        
    Returns:
        str: Pfad zum Chars-Verzeichnis oder zur Char-Datei
    """
    if filename:
        return get_resource_path(f"chars/{filename}")
    else:
        return get_resource_path("chars")

def get_settings_path(filename: str = "") -> str:
    """
    Gibt den Pfad zum Settings-Verzeichnis oder einer spezifischen Settings-Datei zurück.
    
    Args:
        filename (str): Optional - Name der Settings-Datei
        
    Returns:
        str: Pfad zum Settings-Verzeichnis oder zur Settings-Datei
    """
    if filename:
        return get_resource_path(f"settings/{filename}")
    else:
        return get_resource_path("settings")

def get_templates_path(filename: str = "") -> str:
    """
    Gibt den Pfad zum Templates-Verzeichnis oder einer spezifischen Template-Datei zurück.
    
    Args:
        filename (str): Optional - Name der Template-Datei
        
    Returns:
        str: Pfad zum Templates-Verzeichnis oder zur Template-Datei
    """
    if filename:
        return get_resource_path(f"templates/{filename}")
    else:
        return get_resource_path("templates")

# Für Backward-Kompatibilität
def get_project_root() -> Path:
    """Alias für get_application_root()"""
    return get_application_root()