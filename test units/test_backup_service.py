# tests/test_backup_service.py
"""
Unit Tests für BackupService (services/backup_service.py).
Testet Backup-Erstellung, Rotation, Wiederherstellung und Änderungserkennung.
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
import zipfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Kivy-Headless-Modus
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_LOG_LEVEL'] = 'critical'

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBackupService(unittest.TestCase):
    """Test-Klasse für BackupService"""

    def setUp(self):
        """Setup vor jedem Test — erstellt temporäre Verzeichnisse."""
        self.test_dir = tempfile.mkdtemp()
        self.chars_dir = os.path.join(self.test_dir, 'chars')
        self.config_dir = os.path.join(self.test_dir, 'config')
        self.backup_dir = os.path.join(self.test_dir, 'backups')
        self.settings_dir = os.path.join(self.test_dir, 'settings')

        os.makedirs(self.chars_dir)
        os.makedirs(self.config_dir)
        os.makedirs(self.settings_dir)

        # Mock ConfigService
        self.mock_config = Mock()
        self.mock_config.get.side_effect = lambda key, default=None: {
            'auto_backup_enabled': True,
            'max_backups': 3,
        }.get(key, default)

        # Patches
        self.patcher_logger = patch('services.backup_service.Logger')
        self.mock_logger = self.patcher_logger.start()

        self.patcher_config_dir = patch(
            'services.backup_service.BackupService._get_config_dir',
            return_value=self.config_dir
        )
        self.patcher_config_dir.start()

        self.patcher_user_settings = patch(
            'services.backup_service.BackupService._get_user_settings_dir',
            return_value=self.settings_dir
        )
        self.patcher_user_settings.start()

    def tearDown(self):
        """Aufräumen nach jedem Test."""
        self.patcher_logger.stop()
        self.patcher_config_dir.stop()
        self.patcher_user_settings.stop()
        shutil.rmtree(self.test_dir)

    def _erstelle_test_charakter(self, name="TestChar"):
        """Erstellt eine Test-Charakterdatei."""
        dateipfad = os.path.join(self.chars_dir, f"{name}.json")
        with open(dateipfad, 'w', encoding='utf-8') as f:
            json.dump({"char_name": name, "setting": "SWAE"}, f)
        return dateipfad

    def _erstelle_test_config(self):
        """Erstellt eine Test-Konfigurationsdatei."""
        dateipfad = os.path.join(self.config_dir, "app_config.json")
        with open(dateipfad, 'w', encoding='utf-8') as f:
            json.dump({"theme_style": "Dark"}, f)
        return dateipfad

    def _erstelle_service(self):
        """Erstellt einen BackupService mit Mock-Config."""
        from services.backup_service import BackupService
        return BackupService(self.mock_config)

    @patch('services.backup_service.get_backup_path')
    @patch('services.backup_service.get_chars_path')
    def test_01_backup_erstellen(self, mock_chars_path, mock_backup_path):
        """Test: Backup wird korrekt als ZIP erstellt."""
        mock_chars_path.return_value = self.chars_dir
        mock_backup_path.return_value = self.backup_dir

        self._erstelle_test_charakter("Held1")
        self._erstelle_test_config()

        service = self._erstelle_service()
        ergebnis = service.erstelle_backup()

        self.assertTrue(ergebnis)
        self.assertTrue(os.path.isdir(self.backup_dir))

        # Prüfe ob ZIP erstellt wurde
        backup_dateien = [f for f in os.listdir(self.backup_dir) if f.endswith('.zip')]
        self.assertEqual(len(backup_dateien), 1)
        self.assertTrue(backup_dateien[0].startswith('backup_'))

        # Prüfe ZIP-Inhalt
        with zipfile.ZipFile(os.path.join(self.backup_dir, backup_dateien[0]), 'r') as zf:
            namen = zf.namelist()
            self.assertIn('chars/Held1.json', namen)
            self.assertIn('config/app_config.json', namen)

    @patch('services.backup_service.get_backup_path')
    @patch('services.backup_service.get_chars_path')
    def test_02_kein_backup_ohne_daten(self, mock_chars_path, mock_backup_path):
        """Test: Kein Backup wenn keine Benutzerdaten vorhanden."""
        mock_chars_path.return_value = self.chars_dir
        mock_backup_path.return_value = self.backup_dir

        service = self._erstelle_service()
        ergebnis = service.erstelle_backup()

        self.assertFalse(ergebnis)

    def test_03_backup_deaktiviert(self):
        """Test: Kein Backup wenn auto_backup_enabled=False."""
        self.mock_config.get.side_effect = lambda key, default=None: {
            'auto_backup_enabled': False,
            'max_backups': 3,
        }.get(key, default)

        service = self._erstelle_service()
        ergebnis = service.erstelle_backup()

        self.assertFalse(ergebnis)

    @patch('services.backup_service.get_backup_path')
    @patch('services.backup_service.get_chars_path')
    def test_04_backup_rotation(self, mock_chars_path, mock_backup_path):
        """Test: Alte Backups werden gelöscht wenn max_backups überschritten."""
        mock_chars_path.return_value = self.chars_dir
        mock_backup_path.return_value = self.backup_dir

        os.makedirs(self.backup_dir, exist_ok=True)

        # 4 alte Backup-Dateien erstellen (max_backups=3)
        for i in range(4):
            backup_name = f"backup_2024010{i}_120000.zip"
            pfad = os.path.join(self.backup_dir, backup_name)
            with zipfile.ZipFile(pfad, 'w') as zf:
                zf.writestr('dummy.txt', 'test')

        # Charakter NACH den alten Backups erstellen → neuerer Zeitstempel
        import time
        time.sleep(0.05)
        self._erstelle_test_charakter("Held1")

        service = self._erstelle_service()
        service.erstelle_backup()

        # max_backups=3, also sollten nur 3 bleiben (4 alte + 1 neues = 5 → 3)
        backup_dateien = [f for f in os.listdir(self.backup_dir) if f.endswith('.zip')]
        self.assertLessEqual(len(backup_dateien), 3)

    @patch('services.backup_service.get_chars_path')
    def test_05_backup_wiederherstellen(self, mock_chars_path):
        """Test: Backup kann wiederhergestellt werden."""
        mock_chars_path.return_value = self.chars_dir

        # Backup-ZIP manuell erstellen
        os.makedirs(self.backup_dir, exist_ok=True)
        backup_pfad = os.path.join(self.backup_dir, 'backup_test.zip')
        with zipfile.ZipFile(backup_pfad, 'w') as zf:
            zf.writestr('chars/WiederhergestellterHeld.json',
                        json.dumps({"char_name": "WiederhergestellterHeld"}))
            zf.writestr('config/app_config.json',
                        json.dumps({"theme_style": "Light"}))

        service = self._erstelle_service()
        ergebnis = service.stelle_backup_wieder_her(backup_pfad)

        self.assertTrue(ergebnis)
        self.assertTrue(os.path.isfile(
            os.path.join(self.chars_dir, 'WiederhergestellterHeld.json')
        ))
        self.assertTrue(os.path.isfile(
            os.path.join(self.config_dir, 'app_config.json')
        ))

        # Inhalt prüfen
        with open(os.path.join(self.chars_dir, 'WiederhergestellterHeld.json'), 'r') as f:
            daten = json.load(f)
        self.assertEqual(daten['char_name'], 'WiederhergestellterHeld')

    @patch('services.backup_service.get_backup_path')
    def test_06_liste_backups(self, mock_backup_path):
        """Test: Backup-Liste wird korrekt zurückgegeben."""
        mock_backup_path.return_value = self.backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

        # Test-Backups erstellen
        for name in ['backup_20240101_120000.zip', 'backup_20240102_120000.zip']:
            pfad = os.path.join(self.backup_dir, name)
            with zipfile.ZipFile(pfad, 'w') as zf:
                zf.writestr('dummy.txt', 'test')

        service = self._erstelle_service()
        backups = service.liste_backups()

        self.assertEqual(len(backups), 2)
        # Neueste zuerst
        self.assertIn('backup_20240102', backups[0]['name'])
        self.assertIn('pfad', backups[0])
        self.assertIn('datum', backups[0])
        self.assertIn('groesse', backups[0])

    @patch('services.backup_service.get_backup_path')
    @patch('services.backup_service.get_chars_path')
    def test_07_kein_backup_ohne_aenderungen(self, mock_chars_path, mock_backup_path):
        """Test: Kein neues Backup wenn keine Änderungen seit letztem Backup."""
        mock_chars_path.return_value = self.chars_dir
        mock_backup_path.return_value = self.backup_dir

        self._erstelle_test_charakter("Held1")
        self._erstelle_test_config()

        service = self._erstelle_service()
        # Erstes Backup
        service.erstelle_backup()
        # Zweites Backup ohne Änderungen
        ergebnis = service.erstelle_backup()

        self.assertFalse(ergebnis)

    def test_08_wiederherstellung_ungueltige_datei(self):
        """Test: Wiederherstellung schlägt bei ungültiger Datei fehl."""
        service = self._erstelle_service()

        # Nicht existierende Datei
        ergebnis = service.stelle_backup_wieder_her('/nicht/existent.zip')
        self.assertFalse(ergebnis)

        # Keine ZIP-Datei
        ergebnis = service.stelle_backup_wieder_her('/tmp/test.txt')
        self.assertFalse(ergebnis)

    def test_09_properties(self):
        """Test: Properties geben korrekte Werte zurück."""
        service = self._erstelle_service()

        self.assertTrue(service.auto_backup_enabled)
        self.assertEqual(service.max_backups, 3)

    def test_10_properties_ohne_config(self):
        """Test: Properties haben sinnvolle Defaults ohne ConfigService."""
        from services.backup_service import BackupService
        service = BackupService(config_service=None)

        self.assertTrue(service.auto_backup_enabled)
        self.assertEqual(service.max_backups, 5)

    @patch('services.backup_service.get_backup_path')
    @patch('services.backup_service.get_chars_path')
    def test_11_settings_werden_gesichert(self, mock_chars_path, mock_backup_path):
        """Test: User-Settings werden im Backup mit gesichert."""
        mock_chars_path.return_value = self.chars_dir
        mock_backup_path.return_value = self.backup_dir

        self._erstelle_test_charakter("Held1")

        # User-Setting erstellen
        settings_datei = os.path.join(self.settings_dir, "MeinSetting.json")
        with open(settings_datei, 'w', encoding='utf-8') as f:
            json.dump({"name": "MeinSetting"}, f)

        service = self._erstelle_service()
        service.erstelle_backup()

        backup_dateien = [f for f in os.listdir(self.backup_dir) if f.endswith('.zip')]
        with zipfile.ZipFile(os.path.join(self.backup_dir, backup_dateien[0]), 'r') as zf:
            namen = zf.namelist()
            self.assertIn('settings/MeinSetting.json', namen)


if __name__ == '__main__':
    unittest.main()
