"""
Test-Units für setting_funktionen.py

Diese Tests prüfen die Funktionalität der verbesserten Setting-Funktionen
einschließlich der CustomElementManager-Klasse und Hilfsfunktionen.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Pfad zur Projektroot hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Imports der zu testenden Module
from functions.setting_funktionen import (
    get_application_root,
    SetEncoder,
    CustomElementManager,
    create_default_setting,
    load_elements_from_active_setting,
    _lade_voelker,
    _lade_attribute,
    _lade_fertigkeiten,
    _lade_talente,
    _lade_handicaps,
    _lade_maechte,
    _lade_ausruestung,
    _lade_settingregeln
)

from config.ausruestung_config import LogMessages


class TestSetEncoder(unittest.TestCase):
    """Tests für den SetEncoder"""
    
    def test_set_serialization(self):
        """Test Serialisierung von Sets"""
        encoder = SetEncoder()
        test_set = {"Stärke", "Geschicklichkeit", "Verstand"}
        
        result = encoder.default(test_set)
        
        self.assertIsInstance(result, list)
        self.assertEqual(set(result), test_set)
    
    def test_non_set_passthrough(self):
        """Test dass Nicht-Sets durchgereicht werden"""
        encoder = SetEncoder()
        test_dict = {"key": "value"}
        
        with self.assertRaises(TypeError):
            encoder.default(test_dict)


class TestGetApplicationRoot(unittest.TestCase):
    """Tests für get_application_root"""
    
    def test_normal_script_mode(self):
        """Test im normalen Script-Modus"""
        with patch('sys.frozen', False, create=True):
            root = get_application_root()
            self.assertIsInstance(root, Path)
            self.assertTrue(root.exists())
    
    @patch('sys.executable', '/test/path/app.exe')
    def test_frozen_mode(self):
        """Test im gepackten Modus"""
        with patch('sys.frozen', True, create=True):
            root = get_application_root()
            self.assertEqual(root, Path('/test/path'))


class TestCustomElementManager(unittest.TestCase):
    """Tests für den CustomElementManager"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mock_charakter = Mock()
        
        # Test-Setting-Daten erstellen
        self.test_setting_data = {
            "name": "Test Setting",
            "description": "Test Description",
            "voelker": {"Mensch": {"name": "Mensch"}},
            "talente": {"Test Talent": {"name": "Test Talent"}},
            "handicaps": {"Test Handicap": {"name": "Test Handicap"}},
            "maechte": {"Test Macht": {"name": "Test Macht"}},
            "ausruestung": {"Test Item": {"name": "Test Item", "kategorie": "Allgemein"}},
            "settingregeln": {"test_rule": True}
        }
        
        # Test-Setting-Datei erstellen
        self.test_setting_file = self.temp_dir / "TestSetting.json"
        with open(self.test_setting_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_setting_data, f, indent=4)
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_init_with_existing_settings(self):
        """Test Initialisierung mit existierenden Settings"""
        manager = CustomElementManager(
            self.mock_charakter, 
            settings_dir=self.temp_dir,
            setting_name='TestSetting'
        )
        
        self.assertEqual(manager.settings_dir, self.temp_dir)
        self.assertIn('TestSetting', manager.settings)
        self.assertEqual(manager.active_setting_name, 'TestSetting')
        self.assertIsNotNone(manager.active_setting)
    
    def test_load_all_settings_empty_dir(self):
        """Test Laden von Settings aus leerem Verzeichnis"""
        empty_dir = self.temp_dir / "empty"
        empty_dir.mkdir()
        
        manager = CustomElementManager(
            self.mock_charakter,
            settings_dir=empty_dir
        )
        
        self.assertEqual(len(manager.settings), 0)
    
    def test_load_all_settings_non_existent_dir(self):
        """Test Laden von Settings aus nicht-existierendem Verzeichnis"""
        non_existent = self.temp_dir / "does_not_exist"
        
        with patch('kivy.logger.Logger') as mock_logger:
            manager = CustomElementManager(
                self.mock_charakter,
                settings_dir=non_existent
            )
            
            mock_logger.warning.assert_called()
    
    def test_save_setting(self):
        """Test Speichern eines Settings"""
        manager = CustomElementManager(
            self.mock_charakter,
            settings_dir=self.temp_dir
        )
        
        new_setting = {"name": "New Setting", "test": True}
        result = manager.save_setting("NewSetting", new_setting)
        
        self.assertTrue(result)
        self.assertTrue((self.temp_dir / "NewSetting.json").exists())
        
        # Datei lesen und prüfen
        with open(self.temp_dir / "NewSetting.json", 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, new_setting)
    
    def test_set_active_setting_success(self):
        """Test erfolgreiche Aktivierung eines Settings"""
        manager = CustomElementManager(
            self.mock_charakter,
            settings_dir=self.temp_dir
        )
        
        result = manager.set_active_setting('TestSetting')
        
        self.assertTrue(result)
        self.assertEqual(manager.active_setting_name, 'TestSetting')
        self.assertEqual(manager.active_setting, self.test_setting_data)
    
    def test_set_active_setting_non_existent(self):
        """Test Aktivierung eines nicht-existierenden Settings"""
        manager = CustomElementManager(
            self.mock_charakter,
            settings_dir=self.temp_dir
        )
        
        with patch('kivy.logger.Logger') as mock_logger:
            result = manager.set_active_setting('NonExistent')
            
            self.assertFalse(result)
            mock_logger.warning.assert_called()
    
    def test_get_active_setting(self):
        """Test Abrufen des aktiven Settings"""
        manager = CustomElementManager(
            self.mock_charakter,
            settings_dir=self.temp_dir,
            setting_name='TestSetting'
        )
        
        active = manager.get_active_setting()
        
        self.assertEqual(active, self.test_setting_data)
    
    def test_add_setting_new(self):
        """Test Hinzufügen eines neuen Settings"""
        manager = CustomElementManager(
            self.mock_charakter,
            settings_dir=self.temp_dir
        )
        
        new_setting = {"name": "Added Setting", "test": True}
        result = manager.add_setting("AddedSetting", new_setting)
        
        self.assertTrue(result)
        self.assertIn("AddedSetting", manager.settings)
    
    def test_add_setting_existing_no_overwrite(self):
        """Test Hinzufügen eines existierenden Settings ohne Überschreibung"""
        manager = CustomElementManager(
            self.mock_charakter,
            settings_dir=self.temp_dir
        )
        
        new_setting = {"name": "Test", "test": True}
        
        with patch('kivy.logger.Logger') as mock_logger:
            result = manager.add_setting("TestSetting", new_setting, overwrite=False)
            
            self.assertFalse(result)
            mock_logger.warning.assert_called()
    
    def test_add_setting_existing_with_overwrite(self):
        """Test Hinzufügen eines existierenden Settings mit Überschreibung"""
        manager = CustomElementManager(
            self.mock_charakter,
            settings_dir=self.temp_dir
        )
        
        new_setting = {"name": "Overwritten", "test": True}
        result = manager.add_setting("TestSetting", new_setting, overwrite=True)
        
        self.assertTrue(result)
        self.assertEqual(manager.settings["TestSetting"], new_setting)
    
    def test_remove_element_from_active_setting(self):
        """Test Entfernen eines Elements aus dem aktiven Setting"""
        manager = CustomElementManager(
            self.mock_charakter,
            settings_dir=self.temp_dir,
            setting_name='TestSetting'
        )
        
        result = manager.remove_element_from_active_setting('talente', 'Test Talent')
        
        self.assertTrue(result)
        self.assertNotIn('Test Talent', manager.active_setting['talente'])
    
    def test_remove_element_non_existent(self):
        """Test Entfernen eines nicht-existierenden Elements"""
        manager = CustomElementManager(
            self.mock_charakter,
            settings_dir=self.temp_dir,
            setting_name='TestSetting'
        )
        
        with patch('kivy.logger.Logger') as mock_logger:
            result = manager.remove_element_from_active_setting('talente', 'Non Existent')
            
            self.assertFalse(result)
            mock_logger.warning.assert_called()
    
    def test_remove_element_no_active_setting(self):
        """Test Entfernen eines Elements ohne aktives Setting"""
        manager = CustomElementManager(
            self.mock_charakter,
            settings_dir=self.temp_dir
        )
        manager.active_setting = None
        
        with patch('kivy.logger.Logger') as mock_logger:
            result = manager.remove_element_from_active_setting('talente', 'Test')
            
            self.assertFalse(result)
            mock_logger.error.assert_called()


class TestCreateDefaultSetting(unittest.TestCase):
    """Tests für create_default_setting"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.mock_charakter = Mock()
        
        # Mock-Daten erstellen
        mock_volk = Mock()
        mock_volk.to_setting_dict.return_value = {"name": "Mensch"}
        
        mock_attribut = Mock()
        mock_attribut.to_dict.return_value = {"name": "Stärke", "wert": 6}
        
        mock_talent = Mock()
        mock_talent.to_dict.return_value = {"name": "Test Talent"}
        
        mock_handicap = Mock()
        mock_handicap.to_dict.return_value = {"name": "Test Handicap"}
        
        mock_macht = Mock()
        mock_macht.to_dict.return_value = {"name": "Test Macht"}
        
        mock_ausruestung = Mock()
        mock_ausruestung.to_setting_dict.return_value = {"name": "Test Item"}
        
        mock_settingregeln = Mock()
        mock_settingregeln.to_dict.return_value = {"rule": True}
        
        # Charakter-Attribute setzen
        self.mock_charakter.voelker = {"Mensch": mock_volk}
        self.mock_charakter.voelker_selected = ["Mensch"]
        self.mock_charakter.attribute = {"Stärke": mock_attribut}
        self.mock_charakter.fertigkeiten_daten = {"Klettern": {"Stärke", "Geschicklichkeit"}}
        self.mock_charakter.talente = {"Test Talent": mock_talent}
        self.mock_charakter.handicaps = {"Test Handicap": mock_handicap}
        self.mock_charakter.maechte = {"Test Macht": mock_macht}
        self.mock_charakter.ausruestung = {"Test Item": mock_ausruestung}
        self.mock_charakter.settingregeln = mock_settingregeln
    
    def test_create_default_setting(self):
        """Test Erstellung des Default-Settings"""
        result = create_default_setting(self.mock_charakter)
        
        self.assertEqual(result["name"], "SWAE")
        self.assertEqual(result["description"], "Savage-Worlds Abenteuer Edition.")
        self.assertIn("voelker", result)
        self.assertIn("attribute", result)
        self.assertIn("fertigkeiten_daten", result)
        self.assertIn("talente", result)
        self.assertIn("handicaps", result)
        self.assertIn("maechte", result)
        self.assertIn("ausruestung", result)
        self.assertIn("settingregeln", result)
        
        # Prüfen ob fertigkeiten_daten als Liste serialisiert wurden
        self.assertEqual(result["fertigkeiten_daten"]["Klettern"], ["Stärke", "Geschicklichkeit"])


class TestLoadElementsFromActiveSetting(unittest.TestCase):
    """Tests für load_elements_from_active_setting"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.mock_charakter = Mock()
        self.mock_charakter.active_setting_name = "TestSetting"
        
        # Mock CustomElementManager
        self.mock_manager = Mock()
        self.mock_charakter.custom_element_manager = self.mock_manager
        
        # Test-Setting-Daten
        self.test_setting = {
            "voelker": {"Mensch": {"name": "Mensch"}},
            "attribute": {"Stärke": {"name": "Stärke", "wert": 6}},
            "fertigkeiten_daten": {"Klettern": ["Stärke", "Geschicklichkeit"]},
            "talente": {"Test Talent": {"name": "Test Talent"}},
            "handicaps": {"Test Handicap": {"name": "Test Handicap"}},
            "maechte": {"Test Macht": {"name": "Test Macht"}},
            "ausruestung": {"Test Item": {"name": "Test Item", "kategorie": "Allgemein"}},
            "settingregeln": {"rule": True}
        }
        
        self.mock_manager.get_active_setting.return_value = self.test_setting
        
        # Mock für Charakter-Attribute
        self.mock_charakter.voelker = {}
        self.mock_charakter.attribute = {}
        self.mock_charakter.fertigkeiten_daten = {}
        self.mock_charakter.talente = {}
        self.mock_charakter.handicaps = {}
        self.mock_charakter.maechte = {}
        self.mock_charakter.ausruestung = {}
        
        # Mock settingregeln
        mock_settingregeln = Mock()
        self.mock_charakter.settingregeln = mock_settingregeln
    
    @patch('functions.setting_funktionen.Logger')
    @patch('functions.setting_funktionen._lade_voelker')
    @patch('functions.setting_funktionen._lade_attribute')
    @patch('functions.setting_funktionen._lade_fertigkeiten')
    @patch('functions.setting_funktionen._lade_talente')
    @patch('functions.setting_funktionen._lade_handicaps')
    @patch('functions.setting_funktionen._lade_maechte')
    @patch('functions.setting_funktionen._lade_ausruestung')
    @patch('functions.setting_funktionen._lade_settingregeln')
    def test_load_elements_success(self, mock_lade_settingregeln, mock_lade_ausruestung,
                                  mock_lade_maechte, mock_lade_handicaps, mock_lade_talente,
                                  mock_lade_fertigkeiten, mock_lade_attribute, 
                                  mock_lade_voelker, mock_logger):
        """Test erfolgreiches Laden aller Elemente"""
        result = load_elements_from_active_setting(self.mock_charakter)
        
        self.assertTrue(result)
        
        # Prüfen ob alle Lade-Funktionen aufgerufen wurden
        mock_lade_voelker.assert_called_once()
        mock_lade_attribute.assert_called_once()
        mock_lade_fertigkeiten.assert_called_once()
        mock_lade_talente.assert_called_once()
        mock_lade_handicaps.assert_called_once()
        mock_lade_maechte.assert_called_once()
        mock_lade_ausruestung.assert_called_once()
        mock_lade_settingregeln.assert_called_once()
    
    @patch('functions.setting_funktionen.Logger')
    def test_load_elements_no_active_setting(self, mock_logger):
        """Test Laden ohne aktives Setting"""
        self.mock_manager.get_active_setting.return_value = None
        
        result = load_elements_from_active_setting(self.mock_charakter)
        
        self.assertFalse(result)
        mock_logger.error.assert_called()
    
    @patch('functions.setting_funktionen.Logger')
    @patch('functions.setting_funktionen._lade_voelker')
    def test_load_elements_skip_equipment(self, mock_lade_voelker, mock_logger):
        """Test Laden mit übersprungener Ausrüstung"""
        with patch('functions.setting_funktionen._lade_ausruestung') as mock_lade_ausruestung:
            result = load_elements_from_active_setting(
                self.mock_charakter, 
                skip_equipment=True
            )
            
            self.assertTrue(result)
            mock_lade_ausruestung.assert_not_called()
    
    @patch('functions.setting_funktionen.Logger')
    def test_load_elements_replace_mode(self, mock_logger):
        """Test Laden im Replace-Modus"""
        with patch('functions.setting_funktionen._lade_voelker') as mock_lade_voelker:
            result = load_elements_from_active_setting(
                self.mock_charakter,
                replace_mode=True
            )
            
            # Im Replace-Modus sollte merge_elements=False sein
            mock_lade_voelker.assert_called_with(
                self.mock_charakter, 
                self.test_setting, 
                False  # merge_elements=False
            )


class TestHilfsfunktionen(unittest.TestCase):
    """Tests für die privaten Hilfsfunktionen"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.mock_charakter = Mock()
        self.mock_charakter.voelker = {}
        self.mock_charakter.attribute = {}
        self.mock_charakter.fertigkeiten_daten = {}
        self.mock_charakter.talente = {}
        self.mock_charakter.handicaps = {}
        self.mock_charakter.maechte = {}
        self.mock_charakter.ausruestung = {}
        
        self.test_setting = {
            "voelker": {"Mensch": {"name": "Mensch"}},
            "attribute": {"Stärke": {"name": "Stärke", "wert": 6}},
            "fertigkeiten_daten": {"Klettern": ["Stärke", "Geschicklichkeit"]},
            "talente": {"Test Talent": {"name": "Test Talent"}},
            "handicaps": {"Test Handicap": {"name": "Test Handicap"}},
            "maechte": {"Test Macht": {"name": "Test Macht"}},
            "ausruestung": {"Test Item": {"name": "Test Item", "kategorie": "Allgemein"}},
            "settingregeln": {"rule": True}
        }
    
    @patch('functions.setting_funktionen.Volk')
    @patch('functions.setting_funktionen.Logger')
    def test_lade_voelker_merge(self, mock_logger, mock_volk):
        """Test Laden von Völkern im Merge-Modus"""
        mock_volk_instance = Mock()
        mock_volk.from_setting_dict.return_value = mock_volk_instance
        
        _lade_voelker(self.mock_charakter, self.test_setting, merge_elements=True)
        
        self.assertIn("Mensch", self.mock_charakter.voelker)
        self.assertEqual(self.mock_charakter.voelker["Mensch"], mock_volk_instance)
    
    @patch('functions.setting_funktionen.Volk')
    @patch('functions.setting_funktionen.Logger')
    def test_lade_voelker_replace(self, mock_logger, mock_volk):
        """Test Laden von Völkern im Replace-Modus"""
        # Volk bereits vorhanden
        self.mock_charakter.voelker["Alt"] = Mock()
        
        mock_volk_instance = Mock()
        mock_volk.from_setting_dict.return_value = mock_volk_instance
        
        _lade_voelker(self.mock_charakter, self.test_setting, merge_elements=False)
        
        # Altes Volk sollte weg sein
        self.assertNotIn("Alt", self.mock_charakter.voelker)
        # Neues Volk sollte da sein
        self.assertIn("Mensch", self.mock_charakter.voelker)
    
    @patch('functions.setting_funktionen.ausruestung_funktionen.erstelle_item_nach_kategorie')
    @patch('functions.setting_funktionen.Logger')
    def test_lade_ausruestung(self, mock_logger, mock_erstelle_item):
        """Test Laden von Ausrüstung"""
        mock_item = Mock()
        mock_erstelle_item.return_value = mock_item
        
        _lade_ausruestung(self.mock_charakter, self.test_setting, merge_elements=True)
        
        mock_erstelle_item.assert_called_once_with({
            "name": "Test Item", 
            "kategorie": "Allgemein"
        })
        self.assertIn("Test Item", self.mock_charakter.ausruestung)
        self.assertEqual(self.mock_charakter.ausruestung["Test Item"], mock_item)
    
    @patch('functions.setting_funktionen.Logger')
    def test_lade_settingregeln(self, mock_logger):
        """Test Laden von Settingregeln"""
        mock_settingregeln = Mock()
        self.mock_charakter.settingregeln = mock_settingregeln
        
        _lade_settingregeln(self.mock_charakter, self.test_setting)
        
        mock_settingregeln.from_dict.assert_called_once_with({"rule": True})
    
    @patch('functions.setting_funktionen.Logger')
    def test_lade_fertigkeiten(self, mock_logger):
        """Test Laden von Fertigkeiten"""
        _lade_fertigkeiten(self.mock_charakter, self.test_setting, merge_elements=True)
        
        self.assertIn("Klettern", self.mock_charakter.fertigkeiten_daten)
        self.assertEqual(
            self.mock_charakter.fertigkeiten_daten["Klettern"],
            {"Stärke", "Geschicklichkeit"}
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)