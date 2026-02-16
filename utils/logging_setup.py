"""
Logging-Setup für die Savage Worlds Charakter Generator App.
Erstellt session-basierte Log-Dateien für besseres Debugging.
"""

import os
import logging
import datetime
from pathlib import Path
from kivy.logger import Logger as KivyLogger
from kivy.utils import platform

def get_app_data_dir():
    """
    Gibt das App-Datenverzeichnis zurück, plattformspezifisch.
    """
    if platform == 'android':
        try:
            # DIREKTER Zugriff auf externen Speicher - umgeht Android-Storage-API
            external_path = "/sdcard"
            app_dir = os.path.join(external_path, "SavageWorldsCharGen")
            
            # Versuche Ordner zu erstellen
            try:
                os.makedirs(app_dir, exist_ok=True)
                # Test-Schreibzugriff
                test_file = os.path.join(app_dir, "test_write.tmp")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                KivyLogger.info(f"FileLogging: Direkter /sdcard Zugriff erfolgreich: {app_dir}")
                return app_dir
            except Exception as e:
                KivyLogger.warning(f"FileLogging: /sdcard nicht beschreibbar: {e}")
                
            # Fallback 1: Android Storage API
            try:
                from android.storage import primary_external_storage_path
                external_path = primary_external_storage_path()
                app_dir = os.path.join(external_path, "SavageWorldsCharGen")
                os.makedirs(app_dir, exist_ok=True)
                KivyLogger.info(f"FileLogging: Android Storage API erfolgreich: {app_dir}")
                return app_dir
            except Exception as e:
                KivyLogger.warning(f"FileLogging: Android Storage API fehlgeschlagen: {e}")
                
            # Fallback 2: App-interner Speicher (wie bisher)
            try:
                from android.storage import app_storage_path
                app_dir = app_storage_path()
                KivyLogger.warning(f"FileLogging: Fallback auf App-internen Speicher: {app_dir}")
                return app_dir
            except Exception as e:
                KivyLogger.error(f"FileLogging: Alle Android-Speicher-Optionen fehlgeschlagen: {e}")
                return "/data/data/com.github.thallion.savageworlds/files"
                
        except ImportError:
            # Fallback wenn Android-Module nicht verfügbar
            return "/sdcard/SavageWorldsCharGen"
    else:
        # Desktop: Verwende aktuelles Arbeitsverzeichnis
        return os.getcwd()

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
        # App-Datenverzeichnis ermitteln
        app_dir = get_app_data_dir()
        logs_dir = os.path.join(app_dir, "logs")
        
        # Logs-Verzeichnis erstellen falls es nicht existiert
        os.makedirs(logs_dir, exist_ok=True)
        
        # Session-spezifischen Dateinamen erstellen
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        platform_suffix = f"_{platform}" if platform == 'android' else ""
        log_filename = f"{app_name}_{timestamp}{platform_suffix}.log"
        log_filepath = os.path.join(logs_dir, log_filename)
        
        # File Handler für Python logging konfigurieren
        file_handler = logging.FileHandler(log_filepath, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter mit detaillierter Information
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Root logger konfigurieren
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        
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
        kivy_logger.addHandler(file_handler)
        kivy_logger.setLevel(logging.DEBUG)
        
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
        
        return log_filepath
        
    except Exception as e:
        # Fallback wenn File Logging fehlschlägt
        KivyLogger.error(f"FileLogging: Konnte Log-Datei nicht erstellen: {str(e)}")
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