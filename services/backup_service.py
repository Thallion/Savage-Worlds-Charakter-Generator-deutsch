# services/backup_service.py
"""
Backup-Service für automatische Sicherung von Charakteren und Einstellungen.
Erstellt ZIP-Backups bei App-Start und rotiert alte Backups.
"""

import json
import os
import shutil
import threading
import time
import zipfile
from datetime import datetime
from pathlib import Path
from kivy.logger import Logger
from kivy.clock import Clock
from utils.path_utils import get_chars_path, get_backup_path


class BackupService:
    """
    Erstellt und verwaltet automatische Backups von Benutzerdaten.
    Sichert chars/ und config/ als ZIP-Archiv.
    """

    def __init__(self, config_service=None):
        self._config_service = config_service
        self._backup_thread = None
        self._backup_running = False

    @property
    def auto_backup_enabled(self) -> bool:
        """Prüft ob automatisches Backup aktiviert ist."""
        if self._config_service:
            return self._config_service.get('auto_backup_enabled', True)
        return True

    @property
    def max_backups(self) -> int:
        """Maximale Anzahl aufbewahrter Backups."""
        if self._config_service:
            return self._config_service.get('max_backups', 5)
        return 5

    def start_background_backup(self, delay_seconds: float = 2.0):
        """
        Startet ein automatisches Backup in einem Hintergrund-Thread.

        Args:
            delay_seconds (float): Verzögerung in Sekunden bevor Backup startet
        """
        if not self.auto_backup_enabled:
            Logger.info("BackupService: Auto-Backup ist deaktiviert")
            return

        if self._backup_running:
            Logger.info("BackupService: Backup bereits in Bearbeitung")
            return

        Logger.info(f"BackupService: Starte Hintergrund-Backup in {delay_seconds}s")

        self._backup_thread = threading.Thread(
            target=self._background_backup_worker,
            args=(delay_seconds,),
            daemon=True,
            name="BackupService-Worker"
        )
        self._backup_thread.start()

    def _background_backup_worker(self, delay_seconds: float):
        """
        Worker-Funktion für Hintergrund-Backup.

        Args:
            delay_seconds (float): Verzögerung vor Backup-Start
        """
        try:
            self._backup_running = True

            # Kurze Verzögerung damit App Zeit für wichtigere Startup-Tasks hat
            time.sleep(delay_seconds)

            start_time = time.monotonic()

            # Backup erstellen (I/O-intensiv, aber thread-safe)
            erfolg = self.erstelle_backup()

            elapsed_ms = (time.monotonic() - start_time) * 1000.0

            if erfolg:
                Logger.info(f"BackupService: Hintergrund-Backup erfolgreich in {elapsed_ms:.1f} ms")
            else:
                Logger.info(f"BackupService: Hintergrund-Backup übersprungen ({elapsed_ms:.1f} ms)")

        except Exception as e:
            Logger.error(f"BackupService: Fehler im Hintergrund-Backup: {e}", exc_info=True)
        finally:
            self._backup_running = False

    def erstelle_backup(self) -> bool:
        """
        Erstellt ein ZIP-Backup von chars/ und config/ Verzeichnissen.

        Returns:
            bool: True bei Erfolg
        """
        if not self.auto_backup_enabled:
            Logger.info("BackupService: Auto-Backup ist deaktiviert")
            return False

        try:
            backup_dir = get_backup_path()
            chars_dir = get_chars_path()
            config_dir = self._get_config_dir()

            # Prüfe ob es überhaupt Daten zum Sichern gibt
            hat_chars = os.path.isdir(chars_dir) and any(
                f.endswith('.json') for f in os.listdir(chars_dir)
            )
            hat_config = os.path.isdir(config_dir) and any(
                f.endswith('.json') for f in os.listdir(config_dir)
            )

            if not hat_chars and not hat_config:
                Logger.info("BackupService: Keine Benutzerdaten zum Sichern vorhanden")
                return False

            # Backup-Verzeichnis erstellen
            os.makedirs(backup_dir, exist_ok=True)

            # Prüfen ob sich seit dem letzten Backup etwas geändert hat
            if not self._hat_aenderungen(backup_dir, chars_dir, config_dir):
                Logger.info("BackupService: Keine Änderungen seit letztem Backup")
                return False

            # ZIP-Backup erstellen
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.zip"
            backup_path = os.path.join(backup_dir, backup_name)

            dateien_gesichert = 0
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Charaktere sichern
                if hat_chars:
                    for datei in os.listdir(chars_dir):
                        if datei.endswith('.json'):
                            dateipfad = os.path.join(chars_dir, datei)
                            zf.write(dateipfad, f"chars/{datei}")
                            dateien_gesichert += 1

                # Konfiguration sichern
                if hat_config:
                    for datei in os.listdir(config_dir):
                        if datei.endswith('.json'):
                            dateipfad = os.path.join(config_dir, datei)
                            zf.write(dateipfad, f"config/{datei}")
                            dateien_gesichert += 1

                # User-Settings sichern (Android: separates Verzeichnis)
                user_settings_dir = self._get_user_settings_dir()
                if user_settings_dir and os.path.isdir(user_settings_dir):
                    for datei in os.listdir(user_settings_dir):
                        if datei.endswith('.json'):
                            dateipfad = os.path.join(user_settings_dir, datei)
                            zf.write(dateipfad, f"settings/{datei}")
                            dateien_gesichert += 1

            Logger.info(
                f"BackupService: Backup erstellt: {backup_name} "
                f"({dateien_gesichert} Dateien)"
            )

            # Alte Backups rotieren
            self._rotiere_backups(backup_dir)

            return True

        except Exception as e:
            Logger.error(f"BackupService: Fehler beim Erstellen des Backups: {e}")
            return False

    def stelle_backup_wieder_her(self, backup_pfad: str) -> bool:
        """
        Stellt ein Backup aus einer ZIP-Datei wieder her.

        Args:
            backup_pfad (str): Pfad zur ZIP-Backup-Datei

        Returns:
            bool: True bei Erfolg
        """
        try:
            if not os.path.isfile(backup_pfad) or not backup_pfad.endswith('.zip'):
                Logger.error(f"BackupService: Ungültige Backup-Datei: {backup_pfad}")
                return False

            chars_dir = get_chars_path()
            config_dir = self._get_config_dir()

            # Verzeichnisse erstellen falls nötig
            os.makedirs(chars_dir, exist_ok=True)
            os.makedirs(config_dir, exist_ok=True)

            wiederhergestellt = 0
            with zipfile.ZipFile(backup_pfad, 'r') as zf:
                for info in zf.infolist():
                    if info.filename.startswith('chars/') and info.filename.endswith('.json'):
                        dateiname = os.path.basename(info.filename)
                        ziel = os.path.join(chars_dir, dateiname)
                        with zf.open(info) as quelle, open(ziel, 'wb') as zieldatei:
                            zieldatei.write(quelle.read())
                        wiederhergestellt += 1

                    elif info.filename.startswith('config/') and info.filename.endswith('.json'):
                        dateiname = os.path.basename(info.filename)
                        ziel = os.path.join(config_dir, dateiname)
                        with zf.open(info) as quelle, open(ziel, 'wb') as zieldatei:
                            zieldatei.write(quelle.read())
                        wiederhergestellt += 1

                    elif info.filename.startswith('settings/') and info.filename.endswith('.json'):
                        user_settings_dir = self._get_user_settings_dir()
                        if user_settings_dir:
                            os.makedirs(user_settings_dir, exist_ok=True)
                            dateiname = os.path.basename(info.filename)
                            ziel = os.path.join(user_settings_dir, dateiname)
                            with zf.open(info) as quelle, open(ziel, 'wb') as zieldatei:
                                zieldatei.write(quelle.read())
                            wiederhergestellt += 1

            Logger.info(
                f"BackupService: Backup wiederhergestellt: {wiederhergestellt} Dateien "
                f"aus {os.path.basename(backup_pfad)}"
            )
            return wiederhergestellt > 0

        except Exception as e:
            Logger.error(f"BackupService: Fehler bei Wiederherstellung: {e}")
            return False

    def liste_backups(self) -> list:
        """
        Gibt eine Liste aller verfügbaren Backups zurück (neueste zuerst).

        Returns:
            list: Liste von Dicts mit 'pfad', 'name', 'datum', 'groesse'
        """
        try:
            backup_dir = get_backup_path()

            if not os.path.isdir(backup_dir):
                return []

            backups = []
            for datei in os.listdir(backup_dir):
                if datei.endswith('.zip') and datei.startswith('backup_'):
                    pfad = os.path.join(backup_dir, datei)
                    stat = os.stat(pfad)
                    backups.append({
                        'pfad': pfad,
                        'name': datei,
                        'datum': datetime.fromtimestamp(stat.st_mtime),
                        'groesse': stat.st_size,
                    })

            # Neueste zuerst
            backups.sort(key=lambda b: b['datum'], reverse=True)
            return backups

        except Exception as e:
            Logger.error(f"BackupService: Fehler beim Auflisten der Backups: {e}")
            return []

    def _hat_aenderungen(self, backup_dir: str, chars_dir: str, config_dir: str) -> bool:
        """
        Prüft ob sich seit dem letzten Backup Dateien geändert haben.

        Vergleicht die jüngste Änderungszeit der Quelldateien mit dem
        Erstellungsdatum des neuesten Backups.
        """
        try:
            # Neuestes Backup finden
            backup_dateien = sorted(
                [f for f in os.listdir(backup_dir)
                 if f.endswith('.zip') and f.startswith('backup_')],
                reverse=True
            )
            if not backup_dateien:
                return True  # Kein Backup vorhanden → Änderungen

            letztes_backup = os.path.join(backup_dir, backup_dateien[0])
            backup_zeit = os.path.getmtime(letztes_backup)

            # Jüngste Änderungszeit der Quelldateien ermitteln
            for verzeichnis in [chars_dir, config_dir]:
                if not os.path.isdir(verzeichnis):
                    continue
                for datei in os.listdir(verzeichnis):
                    if datei.endswith('.json'):
                        dateipfad = os.path.join(verzeichnis, datei)
                        if os.path.getmtime(dateipfad) > backup_zeit:
                            return True

            return False

        except Exception:
            return True  # Im Zweifel: Backup erstellen

    def _rotiere_backups(self, backup_dir: str):
        """Löscht alte Backups, behält nur max_backups."""
        try:
            backup_dateien = sorted(
                [f for f in os.listdir(backup_dir)
                 if f.endswith('.zip') and f.startswith('backup_')],
                reverse=True
            )

            max_b = self.max_backups
            if len(backup_dateien) > max_b:
                for alte_datei in backup_dateien[max_b:]:
                    pfad = os.path.join(backup_dir, alte_datei)
                    os.remove(pfad)
                    Logger.info(f"BackupService: Altes Backup gelöscht: {alte_datei}")

        except Exception as e:
            Logger.error(f"BackupService: Fehler bei Backup-Rotation: {e}")

    def _get_config_dir(self) -> str:
        """Gibt den Pfad zum Config-Verzeichnis zurück."""
        from kivy.utils import platform as kivy_platform
        if kivy_platform == 'android':
            from utils.path_utils import _get_android_user_data_dir
            return str(Path(_get_android_user_data_dir()) / 'config')
        else:
            from utils.path_utils import get_application_root
            return str(get_application_root() / 'config')

    def _get_user_settings_dir(self) -> str:
        """Gibt den Pfad zum User-Settings-Verzeichnis zurück."""
        try:
            from utils.path_utils import get_user_settings_path
            return get_user_settings_path()
        except Exception:
            return ""

    def cleanup(self):
        """Bereinigt den Backup-Service (für ServiceContainer.shutdown)."""
        if self._backup_thread and self._backup_thread.is_alive():
            Logger.info("BackupService: Warte auf Backup-Thread...")
            # Thread ist daemon, wird automatisch beendet bei App-Ende
            # Maximal 2s warten, dann fortfahren
            self._backup_thread.join(timeout=2.0)
            if self._backup_thread.is_alive():
                Logger.warning("BackupService: Backup-Thread läuft noch, App wird trotzdem beendet")

        Logger.info("BackupService bereinigt")
