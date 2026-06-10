"""
Zentrale Pfad-Utilities für PyInstaller-kompatible Pfade
"""
import sys
import os
from pathlib import Path

def _get_app_root_from_file() -> Path:
    """Ermittelt den App-Root über den Speicherort dieser Datei.
    Funktioniert auf allen Plattformen zuverlässig, inkl. Android/p4a."""
    return Path(__file__).parent.parent.resolve()


def get_resource_path(relative_path: str) -> str:
    """
    Gibt den korrekten Pfad zu einer Ressource zurück, sowohl im Development als auch in der gepackten EXE.

    Args:
        relative_path (str): Relativer Pfad zur Ressource (z.B. 'assets/logo.png' oder 'chars/character.json')

    Returns:
        str: Absoluter Pfad zur Ressource
    """
    base_path = _resolve_base_path()
    resource_path = base_path / relative_path
    return str(resource_path)

def get_application_root() -> Path:
    """
    Ermittelt das Hauptverzeichnis der Anwendung (kompatibel mit PyInstaller und Android/p4a).

    Returns:
        Path: Das Hauptverzeichnis der Anwendung
    """
    return _resolve_base_path()


def _resolve_base_path() -> Path:
    """Zentrale Pfad-Erkennung für alle Laufzeitumgebungen.

    Reihenfolge:
    1. Android/p4a: ANDROID_ARGUMENT/ANDROID_APP_PATH – wird von p4a (start.c)
       direkt auf das entpackte App-Verzeichnis gesetzt und ist damit die
       verlässlichste Quelle auf Android
    2. PyInstaller one-file (_MEIPASS) – eindeutig
    3. PyInstaller one-dir (_internal/ neben der EXE) – eindeutig
    4. PyInstaller one-dir (EXE-Verzeichnis enthält main.py) – eindeutig
    5. __file__-basiert – funktioniert auf allen übrigen Plattformen
    """
    # Android/p4a: kanonischer App-Pfad aus der Umgebung (nur dort gesetzt)
    android_app_path = os.environ.get('ANDROID_ARGUMENT') or os.environ.get('ANDROID_APP_PATH')
    if android_app_path:
        p = Path(android_app_path)
        if p.is_dir():
            return p

    if getattr(sys, 'frozen', False):
        # PyInstaller one-file
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)

        # PyInstaller one-dir: sys.executable liegt neben den App-Dateien
        try:
            exe_dir = Path(sys.executable).parent.resolve()
            internal_dir = exe_dir / '_internal'
            if internal_dir.exists():
                return internal_dir
            # EXE-Verzeichnis ist direkt der App-Root (älteres PyInstaller)
            if (exe_dir / 'main.py').exists():
                return exe_dir
        except Exception:
            pass

        # Android/p4a-Fallback: sys.executable zeigt auf _python_bundle/bin/,
        # nicht auf das App-Verzeichnis – deshalb __file__ verwenden.
        return _get_app_root_from_file()

    # Development oder normale Python-Ausführung
    return _get_app_root_from_file()

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

def safe_filename_stem(path) -> str:
    """Gibt den Dateinamen ohne Extension zurück, korrekt als UTF-8 dekodiert.

    Auf Android/Python-for-Android werden Dateinamen mit Nicht-ASCII-Zeichen
    (Umlaute wie ä, ö, ü) manchmal als Surrogate-Escape-Sequenzen zurückgegeben,
    wenn die Filesystem-Locale nicht auf UTF-8 gesetzt ist. Diese surrogates
    können von keiner Schriftart gerendert werden und erscheinen als Kästchen.

    Diese Funktion erkennt solche surrogates und konvertiert sie zurück zu den
    ursprünglichen UTF-8-Bytes, um den korrekten Unicode-String zu erhalten.
    """
    stem = Path(path).stem
    try:
        stem.encode('utf-8')
        return stem
    except UnicodeEncodeError:
        try:
            return stem.encode('utf-8', errors='surrogatepass').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            return stem


# Für Backward-Kompatibilität
def get_project_root() -> Path:
    """Alias für get_application_root()"""
    return get_application_root()