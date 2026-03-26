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
        # PyInstaller: Prüfe ob one-directory oder one-file Modus
        if hasattr(sys, '_MEIPASS'):
            # one-file Modus - verwende temporären Pfad
            base_path = Path(sys._MEIPASS)
        else:
            # one-directory Modus - verwende _internal Verzeichnis
            exe_dir = Path(sys.executable).parent
            internal_dir = exe_dir / '_internal'
            if internal_dir.exists():
                base_path = internal_dir
            else:
                base_path = exe_dir
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
        # PyInstaller: Prüfe ob one-directory oder one-file Modus
        if hasattr(sys, '_MEIPASS'):
            # one-file Modus - verwende temporären Pfad
            app_root = Path(sys._MEIPASS)
        else:
            # one-directory Modus - verwende _internal Verzeichnis
            exe_dir = Path(sys.executable).parent
            internal_dir = exe_dir / '_internal'
            if internal_dir.exists():
                app_root = internal_dir
            else:
                app_root = exe_dir
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

def _get_android_user_data_dir() -> str:
    """
    Gibt das persistente Datenverzeichnis auf Android zurück.
    Dieses Verzeichnis überlebt App-Updates (wird nur bei Deinstallation gelöscht).

    Returns:
        str: Pfad zum persistenten Datenverzeichnis
    """
    try:
        from android.storage import app_storage_path
        return app_storage_path()
    except ImportError:
        pass
    try:
        # Fallback: Kivy App user_data_dir
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if app:
            return app.user_data_dir
    except Exception:
        pass
    # Letzter Fallback
    return str(get_application_root())


def get_chars_path(filename: str = "") -> str:
    """
    Gibt den Pfad zum Chars-Verzeichnis oder einer spezifischen Char-Datei zurück.

    Auf Android wird ein persistentes Verzeichnis verwendet, das App-Updates überlebt.
    Auf Desktop wird das Projektverzeichnis verwendet.

    Args:
        filename (str): Optional - Name der Char-Datei

    Returns:
        str: Pfad zum Chars-Verzeichnis oder zur Char-Datei
    """
    from kivy.utils import platform as kivy_platform

    if kivy_platform == 'android':
        # Persistentes Verzeichnis auf Android (überlebt Updates)
        base = Path(_get_android_user_data_dir()) / 'chars'
    else:
        base = Path(get_resource_path("chars"))

    if filename:
        return str(base / filename)
    else:
        return str(base)

def get_settings_path(filename: str = "") -> str:
    """
    Gibt den Pfad zum nativen Settings-Verzeichnis (mitgelieferte Settings) zurück.

    Args:
        filename (str): Optional - Name der Settings-Datei

    Returns:
        str: Pfad zum nativen Settings-Verzeichnis oder zur Settings-Datei
    """
    if filename:
        return get_resource_path(f"settings/{filename}")
    else:
        return get_resource_path("settings")


def get_user_settings_path(filename: str = "") -> str:
    """
    Gibt den Pfad zum persistenten Benutzer-Settings-Verzeichnis zurück.

    Auf Android wird ein persistentes Verzeichnis verwendet, das App-Updates überlebt.
    Auf Desktop wird das gleiche Verzeichnis wie für native Settings verwendet.

    Benutzer-erstellte Settings werden hier gespeichert, damit sie bei App-Updates
    nicht verloren gehen.

    Args:
        filename (str): Optional - Name der Settings-Datei

    Returns:
        str: Pfad zum Benutzer-Settings-Verzeichnis oder zur Settings-Datei
    """
    from kivy.utils import platform as kivy_platform

    if kivy_platform == 'android':
        # Persistentes Verzeichnis auf Android (überlebt Updates)
        base = Path(_get_android_user_data_dir()) / 'settings'
    else:
        # Auf Desktop: gleicher Pfad wie native Settings
        base = Path(get_resource_path("settings"))

    if filename:
        return str(base / filename)
    else:
        return str(base)

def get_backup_path(filename: str = "") -> str:
    """
    Gibt den Pfad zum Backup-Verzeichnis oder einer spezifischen Backup-Datei zurück.

    Auf Android wird ein persistentes Verzeichnis verwendet, das App-Updates überlebt.
    Auf Desktop wird das Projektverzeichnis verwendet.

    Args:
        filename (str): Optional - Name der Backup-Datei

    Returns:
        str: Pfad zum Backup-Verzeichnis oder zur Backup-Datei
    """
    from kivy.utils import platform as kivy_platform

    if kivy_platform == 'android':
        base = Path(_get_android_user_data_dir()) / 'backups'
    else:
        base = Path(get_resource_path("backups"))

    if filename:
        return str(base / filename)
    else:
        return str(base)


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