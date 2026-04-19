"""
Logging-Setup für die Savage Worlds Charakter Generator App.
Erstellt session-basierte Log-Dateien für besseres Debugging.
"""

import os
import sys
import json
import logging
import datetime
from pathlib import Path
from kivy.logger import Logger as KivyLogger
from kivy.utils import platform

# Diagnose-Informationen für das Logging-Setup
# Wird gespeichert damit die UI die Fehlerursache anzeigen kann
_setup_error_details = []


def _get_log_level():
    """
    Liest das Log-Level aus der Konfigurationsdatei.
    
    Returns:
        int: logging.DEBUG, logging.INFO, etc.
    """
    default_level = logging.INFO
    level_mapping = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    try:
        # Pfad zur Konfigurationsdatei ermitteln
        if getattr(sys, 'frozen', False):
            app_dir = Path(sys.executable).parent
        else:
            app_dir = Path(__file__).parent.parent
        
        config_path = app_dir / "config" / "app_config.json"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            level_str = config.get('log_level', 'INFO')
            level = level_mapping.get(level_str.upper(), default_level)
            KivyLogger.debug(f"Log-Level aus Konfiguration gelesen: {level_str}")
            return level
        else:
            KivyLogger.warning(f"Konfigurationsdatei nicht gefunden, verwende Standard-Log-Level: INFO")
            return default_level
            
    except Exception as e:
        KivyLogger.warning(f"Konnte Log-Level nicht aus Konfiguration lesen: {e}, verwende INFO")
        return default_level


def get_last_setup_errors():
    """Gibt die Fehlerdetails aus dem letzten setup_file_logging-Aufruf zurück."""
    return list(_setup_error_details)


def _test_writable(app_dir):
    """Prüft ob das Verzeichnis tatsächlich beschreibbar ist (inkl. Log-Unterverzeichnis)."""
    KivyLogger.info(f"FileLogging: _test_writable für {app_dir}")
    logs_dir = os.path.join(app_dir, "logs")
    KivyLogger.info(f"FileLogging: Versuche logs-Verzeichnis zu erstellen: {logs_dir}")
    os.makedirs(logs_dir, exist_ok=True)
    # Echter Schreibtest im finalen logs-Unterverzeichnis
    test_file = os.path.join(logs_dir, ".write_test.tmp")
    KivyLogger.info(f"FileLogging: Versuche Testdatei zu schreiben: {test_file}")
    with open(test_file, 'w') as f:
        f.write("test")
    os.remove(test_file)
    KivyLogger.info(f"FileLogging: Schreibtest erfolgreich für {app_dir}")
    return True


def get_app_data_dir():
    """
    Gibt das App-Datenverzeichnis zurück, plattformspezifisch.

    Auf Android wird zuerst der interne App-Speicher verwendet (zuverlässig,
    keine Berechtigungen nötig, funktioniert auch mit Scoped Storage).
    Externer Speicher wird nur als zusätzliche Option versucht.
    """
    if platform != 'android':
        # Desktop: Verwende aktuelles Arbeitsverzeichnis
        return os.getcwd()

    _setup_error_details.clear()
    KivyLogger.info("FileLogging: Starte Suche nach beschreibbarem App-Verzeichnis")

    # Priorität 1: python-for-android app_storage_path (interner Speicher)
    # Dieser Pfad ist IMMER beschreibbar für die App - ohne Berechtigungen
    try:
        from android.storage import app_storage_path
        app_dir = app_storage_path()
        KivyLogger.info(f"FileLogging: app_storage_path gibt zurück: {app_dir}")
        if app_dir:
            KivyLogger.info(f"FileLogging: Teste Schreibbarkeit von {app_dir}")
            _test_writable(app_dir)
            KivyLogger.info(f"FileLogging: App-interner Speicher (app_storage_path) ist beschreibbar: {app_dir}")
            return app_dir
        else:
            KivyLogger.warning("FileLogging: app_storage_path gab None zurück")
            msg = "app_storage_path: Kein Pfad zurückgegeben"
            _setup_error_details.append(msg)
    except Exception as e:
        msg = f"app_storage_path: {type(e).__name__}: {e}"
        KivyLogger.warning(f"FileLogging: {msg}")
        _setup_error_details.append(msg)

    # Priorität 2: getFilesDir() via Java API (ebenfalls interner Speicher)
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        files_dir = context.getFilesDir().getAbsolutePath()
        KivyLogger.info(f"FileLogging: getFilesDir gibt zurück: {files_dir}")
        if files_dir:
            KivyLogger.info(f"FileLogging: Teste Schreibbarkeit von {files_dir}")
            _test_writable(files_dir)
            KivyLogger.info(f"FileLogging: App-interner Speicher (getFilesDir) ist beschreibbar: {files_dir}")
            return files_dir
        else:
            KivyLogger.warning("FileLogging: getFilesDir gab None zurück")
            msg = "getFilesDir: Kein Pfad zurückgegeben"
            _setup_error_details.append(msg)
    except Exception as e:
        msg = f"getFilesDir: {type(e).__name__}: {e}"
        KivyLogger.warning(f"FileLogging: {msg}")
        _setup_error_details.append(msg)

    # Priorität 3: getCacheDir() - interner Cache-Speicher (immer beschreibbar)
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        cache_dir = context.getCacheDir().getAbsolutePath()
        KivyLogger.info(f"FileLogging: getCacheDir gibt zurück: {cache_dir}")
        if cache_dir:
            KivyLogger.info(f"FileLogging: Teste Schreibbarkeit von {cache_dir}")
            _test_writable(cache_dir)
            KivyLogger.info(f"FileLogging: App-interner Cache-Speicher (getCacheDir) ist beschreibbar: {cache_dir}")
            return cache_dir
        else:
            KivyLogger.warning("FileLogging: getCacheDir gab None zurück")
            msg = "getCacheDir: Kein Pfad zurückgegeben"
            _setup_error_details.append(msg)
    except Exception as e:
        msg = f"getCacheDir: {type(e).__name__}: {e}"
        KivyLogger.warning(f"FileLogging: {msg}")
        _setup_error_details.append(msg)

    # Priorität 4: getExternalCacheDir() - externer Cache-Speicher (wenn verfügbar)
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        external_cache_dir = context.getExternalCacheDir()
        if external_cache_dir:
            external_cache_path = external_cache_dir.getAbsolutePath()
            KivyLogger.info(f"FileLogging: getExternalCacheDir gibt zurück: {external_cache_path}")
            KivyLogger.info(f"FileLogging: Teste Schreibbarkeit von {external_cache_path}")
            _test_writable(external_cache_path)
            KivyLogger.info(f"FileLogging: Externer Cache-Speicher (getExternalCacheDir) ist beschreibbar: {external_cache_path}")
            return external_cache_path
        else:
            KivyLogger.warning("FileLogging: getExternalCacheDir gab None zurück")
            msg = "getExternalCacheDir: Kein Pfad zurückgegeben"
            _setup_error_details.append(msg)
    except Exception as e:
        msg = f"getExternalCacheDir: {type(e).__name__}: {e}"
        KivyLogger.warning(f"FileLogging: {msg}")
        _setup_error_details.append(msg)

    # Priorität 5: Externer Speicher (/sdcard) - für Benutzer-Sichtbarkeit im Dateimanager
    # Nur wenn interner Speicher nicht funktioniert
    try:
        from android.storage import primary_external_storage_path
        external_path = primary_external_storage_path()
        KivyLogger.info(f"FileLogging: primary_external_storage_path gibt zurück: {external_path}")
        app_dir = os.path.join(external_path, "SavageWorldsCharGen")
        KivyLogger.info(f"FileLogging: Teste Schreibbarkeit von {app_dir}")
        _test_writable(app_dir)
        KivyLogger.info(f"FileLogging: Externer Speicher ist beschreibbar: {app_dir}")
        return app_dir
    except Exception as e:
        msg = f"primary_external_storage_path: {type(e).__name__}: {e}"
        KivyLogger.warning(f"FileLogging: {msg}")
        _setup_error_details.append(msg)

    # Letzter Fallback: Hardcodierter /sdcard-Pfad
    try:
        app_dir = "/sdcard/SavageWorldsCharGen"
        KivyLogger.info(f"FileLogging: Teste /sdcard-Fallback: {app_dir}")
        _test_writable(app_dir)
        KivyLogger.warning(f"FileLogging: /sdcard-Fallback ist beschreibbar: {app_dir}")
        return app_dir
    except Exception as e:
        msg = f"/sdcard: {type(e).__name__}: {e}"
        KivyLogger.error(f"FileLogging: {msg}")
        _setup_error_details.append(msg)

    # Nichts hat funktioniert - gib den wahrscheinlichsten Pfad zurück,
    # damit setup_file_logging noch eine Chance hat
    KivyLogger.error("FileLogging: Alle Speicheroptionen fehlgeschlagen, verwende Hardcoded-Fallback")
    fallback_path = "/data/user/0/com.github.thallion.savageworlds/files"
    KivyLogger.error(f"FileLogging: Fallback-Pfad: {fallback_path}")
    return fallback_path

def setup_file_logging(app_name="SavageWorldsGenerator"):
    """
    Richtet das dateibasierte Logging ein.
    Erstellt für jede Session eine neue Log-Datei.
    
    Args:
        app_name (str): Name der App für das Logging
        
    Returns:
        str: Pfad zur erstellten Log-Datei
    """
    try:
        KivyLogger.info(f"FileLogging: Starte setup_file_logging für App '{app_name}'")
        
        # App-Datenverzeichnis ermitteln
        app_dir = get_app_data_dir()
        KivyLogger.info(f"FileLogging: App-Datenverzeichnis: {app_dir}")
        
        logs_dir = os.path.join(app_dir, "logs")
        KivyLogger.info(f"FileLogging: Logs-Verzeichnis: {logs_dir}")
        
        # Logs-Verzeichnis erstellen falls es nicht existiert
        KivyLogger.info(f"FileLogging: Versuche logs-Verzeichnis zu erstellen")
        os.makedirs(logs_dir, exist_ok=True)
        KivyLogger.info(f"FileLogging: Logs-Verzeichnis erstellt oder existiert bereits")
        
        # Session-spezifischen Dateinamen erstellen
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        platform_suffix = f"_{platform}" if platform == 'android' else ""
        log_filename = f"{app_name}_{timestamp}{platform_suffix}.log"
        log_filepath = os.path.join(logs_dir, log_filename)
        KivyLogger.info(f"FileLogging: Log-Dateiname: {log_filename}")
        KivyLogger.info(f"FileLogging: Log-Dateipfad: {log_filepath}")
        
        # File Handler für Python logging konfigurieren
        file_handler = logging.FileHandler(log_filepath, mode='w', encoding='utf-8')
        log_level = _get_log_level()
        file_handler.setLevel(log_level)
        
        # Formatter mit detaillierter Information
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Root logger konfigurieren
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        KivyLogger.info(f"FileLogging: Füge FileHandler zum Root-Logger hinzu")
        root_logger.addHandler(file_handler)
        
        # jnius reflect-Logging unterdrücken (erzeugt massenhaft DEBUG-Spam)
        logging.getLogger('kivy.jnius.reflect').setLevel(logging.WARNING)
        logging.getLogger('kivy.jnius').setLevel(logging.WARNING)

        # Kivy Logger auch in Datei umleiten
        class KivyFileHandler(logging.Handler):
            def __init__(self, file_handler):
                super().__init__()
                self.file_handler = file_handler
                
            def emit(self, record):
                # Kivy-spezifische Formatierung
                if hasattr(record, 'kivy_logger'):
                    record.name = f"Kivy.{record.name}"
                self.file_handler.emit(record)
        
        kivy_file_handler = KivyFileHandler(file_handler)
        
        # Kivy Logger Handler hinzufügen
        kivy_logger = logging.getLogger('kivy')
        KivyLogger.info(f"FileLogging: Füge FileHandler zum Kivy-Logger hinzu")
        kivy_logger.addHandler(file_handler)
        kivy_logger.setLevel(log_level)
        
        # Erfolgreiche Initialisierung loggen
        logging.info(f"=== Neue Session gestartet ===")
        logging.info(f"App: {app_name}")
        logging.info(f"Platform: {platform}")
        logging.info(f"Log-Datei: {log_filepath}")
        logging.info(f"App-Verzeichnis: {app_dir}")
        logging.info("=" * 50)
        
        # Auch über Kivy Logger ausgeben
        KivyLogger.info(f"FileLogging: Log-Datei erstellt: {log_filepath}")
        
        # Zusätzliche Info für Android-Nutzer
        if platform == 'android':
            KivyLogger.info(f"FileLogging: Android-Pfad für Dateimanager: {log_filepath}")
            KivyLogger.info(f"FileLogging: Logs-Ordner: {logs_dir}")
        
        KivyLogger.info(f"FileLogging: setup_file_logging erfolgreich abgeschlossen")
        return log_filepath
        
    except Exception as e:
        # Fallback wenn File Logging fehlschlägt - Fehler für Diagnose speichern
        error_msg = f"setup_file_logging: {type(e).__name__}: {e}"
        KivyLogger.error(f"FileLogging: Konnte Log-Datei nicht erstellen: {error_msg}")
        # Vorhandene Fehlerdetails loggen
        if _setup_error_details:
            KivyLogger.error(f"FileLogging: Vorherige Fehlerdetails: {_setup_error_details}")
        _setup_error_details.append(error_msg)
        KivyLogger.error(f"FileLogging: setup_file_logging fehlgeschlagen, kehre mit None zurück")
        return None

def cleanup_old_logs(max_age_days=7, max_files=20):
    """
    Bereinigt alte Log-Dateien um Speicherplatz zu sparen.
    
    Args:
        max_age_days (int): Maximales Alter der Log-Dateien in Tagen
        max_files (int): Maximale Anzahl von Log-Dateien
    """
    try:
        app_dir = get_app_data_dir()
        logs_dir = os.path.join(app_dir, "logs")
        
        if not os.path.exists(logs_dir):
            return
            
        # Alle Log-Dateien finden
        log_files = []
        for filename in os.listdir(logs_dir):
            if filename.endswith('.log'):
                filepath = os.path.join(logs_dir, filename)
                stat = os.stat(filepath)
                log_files.append((filepath, stat.st_mtime))
        
        # Nach Änderungsdatum sortieren (neueste zuerst)
        log_files.sort(key=lambda x: x[1], reverse=True)
        
        # Alte Dateien löschen
        cutoff_time = datetime.datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        deleted_count = 0
        
        for i, (filepath, mtime) in enumerate(log_files):
            should_delete = False
            
            # Löschen wenn zu alt
            if mtime < cutoff_time:
                should_delete = True
                
            # Löschen wenn zu viele Dateien (nur die ältesten behalten)
            if i >= max_files:
                should_delete = True
                
            if should_delete:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except OSError:
                    pass
        
        if deleted_count > 0:
            logging.info(f"FileLogging: {deleted_count} alte Log-Dateien gelöscht")
            
    except Exception as e:
        KivyLogger.warning(f"FileLogging: Fehler beim Bereinigen alter Logs: {str(e)}")

def log_system_info():
    """
    Loggt Systeminformationen für Debugging.
    """
    try:
        import sys
        import kivy
        
        logging.info("=== System Information ===")
        logging.info(f"Python Version: {sys.version}")
        logging.info(f"Kivy Version: {kivy.__version__}")
        logging.info(f"Platform: {platform}")
        
        if platform == 'android':
            try:
                from android import mActivity
                from android.permissions import request_permissions, Permission
                logging.info("Android: App läuft im Android-Modus")
            except ImportError:
                logging.warning("Android: Import fehlgeschlagen (Emulator?)")
        
        # App-spezifische Informationen
        logging.info(f"Working Directory: {os.getcwd()}")
        logging.info(f"App Data Directory: {get_app_data_dir()}")
        logging.info("=" * 30)
        
    except Exception as e:
        logging.error(f"Fehler beim Loggen der Systeminformationen: {str(e)}")

# Convenience-Funktionen für häufig verwendete Log-Level
def log_transaction(action, item_name, amount, price, success, details=""):
    """Spezielle Logging-Funktion für Ausrüstungstransaktionen"""
    status = "ERFOLG" if success else "FEHLER"
    logging.info(f"TRANSACTION [{status}]: {action} - {item_name} x{amount} @ {price} - {details}")

def log_android_event(event_name, details=""):
    """Spezielle Logging-Funktion für Android-Events"""
    logging.info(f"ANDROID_EVENT: {event_name} - {details}")