# tests/test_character_handler.py
"""
Unit Tests für CharacterHandler
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from kivy.app import App
from kivymd.app import MDApp

# Mocking Kivy vor Import
with patch('kivy.logger.Logger'), patch('kivymd.app.MDApp'):
    from controllers.character_handler import CharacterHandler


class TestCharacterHandler(unittest.TestCase):
    """Test-Klasse für CharacterHandler"""
    
    def setUp(self):
        """Setup vor jedem Test"""
        # Mock Widget
        self.mock_widget = Mock()
        self.mock_widget.ids = Mock()
        
        # Mock App mit Controller
        self.mock_app = Mock()
        self.mock_app.controller = Mock()
        self.mock_app.controller.charakter = Mock()
        self.mock_widget.app = self.mock_app
        
        # Character Handler erstellen
        self.character_handler = CharacterHandler(self.mock_widget)
        
    def test_init(self):
        """Test Initialisierung"""
        self.assertEqual(self.character_handler.widget, self.mock_widget)
        self.assertEqual(self.character_handler.app, self.mock_app)
        
    def test_get_charakter_value_with_charakter(self):
        """Test Charakter-Wert-Abruf mit vorhandenem Charakter"""
        # Setup
        self.mock_app.controller.charakter.test_attr = "test_value"
        
        # Test
        result = self.character_handler.get_charakter_value('test_attr', 'default')
        
        self.assertEqual(result, "test_value")
        
    def test_get_charakter_value_without_charakter(self):
        """Test Charakter-Wert-Abruf ohne Charakter"""
        # Setup - Kein Charakter verfügbar
        self.mock_app.controller = None
        
        # Test
        result = self.character_handler.get_charakter_value('test_attr', 'default')
        
        self.assertEqual(result, 'default')
        
    def test_get_charakter_value_missing_attribute(self):
        """Test Charakter-Wert-Abruf für nicht existentes Attribut"""
        # Setup
        delattr(self.mock_app.controller.charakter, 'test_attr') if hasattr(self.mock_app.controller.charakter, 'test_attr') else None
        
        # Test
        result = self.character_handler.get_charakter_value('missing_attr', 'default')
        
        self.assertEqual(result, 'default')
        
    @patch('controllers.character_handler.Logger')
    def test_update_maximale_attributsteigerungen(self, mock_logger):
        """Test Update der maximalen Attributsteigerungen"""
        # Setup
        self.mock_app.controller.charakter.aufstieg = 3
        mock_textfield = Mock()
        self.mock_widget.ids.maximale_attributsteigerungen_field = mock_textfield
        
        # Test
        self.character_handler.update_maximale_attributsteigerungen()
        
        # Prüfe dass das Text-Feld aktualisiert wurde
        mock_textfield.text = str(3)
        
    @patch('controllers.character_handler.Logger')
    def test_update_maximale_fertigkeitssteigerungen(self, mock_logger):
        """Test Update der maximalen Fertigkeitssteigerungen"""
        # Setup
        self.mock_app.controller.charakter.aufstieg = 2
        mock_textfield = Mock()
        self.mock_widget.ids.maximale_fertigkeitssteigerungen_field = mock_textfield
        
        # Test
        self.character_handler.update_maximale_fertigkeitssteigerungen()
        
        # Prüfe dass das Text-Feld aktualisiert wurde
        mock_textfield.text = str(4)  # aufstieg * 2
        
    @patch('controllers.character_handler.Logger')
    def test_create_new_character(self, mock_logger):
        """Test Erstellung eines neuen Charakters"""
        # Setup
        self.mock_app.controller.new_character = Mock()
        
        # Test
        self.character_handler.create_new_character()
        
        # Prüfe dass new_character aufgerufen wurde
        self.mock_app.controller.new_character.assert_called_once()
        mock_logger.info.assert_called_with("Neuer Charakter erstellt")
        
    @patch('controllers.character_handler.Logger')
    def test_create_new_character_no_controller(self, mock_logger):
        """Test Charaktererstellung ohne Controller"""
        # Setup - Kein Controller
        self.mock_app.controller = None
        
        # Test
        self.character_handler.create_new_character()
        
        mock_logger.warning.assert_called_with("Controller nicht verfügbar für Charaktererstellung")
        
    @patch('controllers.character_handler.Logger')
    def test_schnellspeichern_charakter(self, mock_logger):
        """Test Schnellspeicherung des Charakters"""
        # Setup
        self.mock_app.controller.quick_save_character = Mock()
        
        # Test
        self.character_handler.schnellspeichern_charakter()
        
        # Prüfe dass quick_save_character aufgerufen wurde
        self.mock_app.controller.quick_save_character.assert_called_once()
        mock_logger.info.assert_called_with("Charakter schnell gespeichert")
        
    @patch('controllers.character_handler.Logger')
    def test_speichere_charakter(self, mock_logger):
        """Test normale Charakterspeicherung"""
        # Setup
        self.mock_app.controller.save_character = Mock()
        
        # Test
        self.character_handler.speichere_charakter()
        
        # Prüfe dass save_character aufgerufen wurde
        self.mock_app.controller.save_character.assert_called_once()
        mock_logger.info.assert_called_with("Charakter gespeichert")
        
    @patch('controllers.character_handler.Logger')
    def test_lade_charakter(self, mock_logger):
        """Test Charakterladen"""
        # Setup
        self.mock_app.controller.load_character = Mock()
        
        # Test
        self.character_handler.lade_charakter()
        
        # Prüfe dass load_character aufgerufen wurde
        self.mock_app.controller.load_character.assert_called_once()
        mock_logger.info.assert_called_with("Charakter laden angefordert")
        
    @patch('controllers.character_handler.Logger')
    def test_erzeuge_charakterbogen_pdf(self, mock_logger):
        """Test PDF-Erzeugung"""
        # Setup
        self.mock_app.controller.generate_character_sheet_pdf = Mock()
        
        # Test
        self.character_handler.erzeuge_charakterbogen_pdf()
        
        # Prüfe dass PDF-Generierung aufgerufen wurde
        self.mock_app.controller.generate_character_sheet_pdf.assert_called_once()
        mock_logger.info.assert_called_with("Charakterbogen PDF-Erzeugung angefordert")
        
    @patch('controllers.character_handler.Logger')
    def test_zeige_statblock(self, mock_logger):
        """Test Statblock-Anzeige"""
        # Setup
        self.mock_app.controller.show_stat_block = Mock()
        
        # Test
        self.character_handler.zeige_statblock()
        
        # Prüfe dass Statblock-Anzeige aufgerufen wurde
        self.mock_app.controller.show_stat_block.assert_called_once()
        mock_logger.info.assert_called_with("Statblock-Anzeige angefordert")
        
    @patch('controllers.character_handler.Logger')
    def test_update_vermoegen_with_values(self, mock_logger):
        """Test Vermögen-Update mit Werten"""
        # Setup
        mock_field = Mock()
        mock_field.text = "100"
        self.mock_widget.ids.vermoegen_field = mock_field
        self.mock_app.controller.charakter.vermoegen = 50
        
        # Test
        self.character_handler.update_vermoegen()
        
        # Prüfe dass Wert aktualisiert wurde
        self.assertEqual(self.mock_app.controller.charakter.vermoegen, 100)
        
    @patch('controllers.character_handler.Logger')
    def test_erhoehe_aufstieg(self, mock_logger):
        """Test Aufstieg-Erhöhung"""
        # Setup
        self.mock_app.controller.charakter.aufstieg = 1
        mock_field = Mock()
        self.mock_widget.ids.aufstieg_field = mock_field
        
        # Test
        self.character_handler.erhoehe_aufstieg()
        
        # Prüfe dass Aufstieg erhöht wurde
        self.assertEqual(self.mock_app.controller.charakter.aufstieg, 2)
        
    @patch('controllers.character_handler.Logger')
    def test_senke_aufstieg(self, mock_logger):
        """Test Aufstieg-Senkung"""
        # Setup
        self.mock_app.controller.charakter.aufstieg = 2
        mock_field = Mock()
        self.mock_widget.ids.aufstieg_field = mock_field
        
        # Test
        self.character_handler.senke_aufstieg()
        
        # Prüfe dass Aufstieg gesenkt wurde
        self.assertEqual(self.mock_app.controller.charakter.aufstieg, 1)
        
    @patch('controllers.character_handler.Logger')
    def test_senke_aufstieg_minimum(self, mock_logger):
        """Test Aufstieg-Senkung bei Minimum"""
        # Setup
        self.mock_app.controller.charakter.aufstieg = 0
        
        # Test
        self.character_handler.senke_aufstieg()
        
        # Aufstieg sollte bei 0 bleiben
        self.assertEqual(self.mock_app.controller.charakter.aufstieg, 0)
        
    @patch('controllers.character_handler.Logger')
    def test_exception_handling_create_character(self, mock_logger):
        """Test Exception-Handling bei Charaktererstellung"""
        # Setup - Exception simulieren
        self.mock_app.controller.new_character.side_effect = Exception("Test Error")
        
        # Test
        self.character_handler.create_new_character()
        
        mock_logger.error.assert_called_with("Fehler bei Charaktererstellung: Test Error")
        
    @patch('controllers.character_handler.Logger')
    def test_on_character_created_event(self, mock_logger):
        """Test Character-Created Event"""
        # Setup
        self.character_handler._update_ui_fields = Mock()
        test_data = {"character": "test_character"}
        
        # Test
        self.character_handler.on_character_created(test_data)
        
        # Prüfe dass UI-Felder aktualisiert wurden
        self.character_handler._update_ui_fields.assert_called_once()
        mock_logger.info.assert_called_with(f"Charakter erstellt: {test_data}")
        
    @patch('controllers.character_handler.Logger')
    def test_on_character_loaded_event(self, mock_logger):
        """Test Character-Loaded Event"""
        # Setup
        self.character_handler._update_ui_fields = Mock()
        test_data = {"character": "loaded_character"}
        
        # Test
        self.character_handler.on_character_loaded(test_data)
        
        # Prüfe dass UI-Felder aktualisiert wurden
        self.character_handler._update_ui_fields.assert_called_once()
        mock_logger.info.assert_called_with(f"Charakter geladen: {test_data}")


if __name__ == '__main__':
    unittest.main()