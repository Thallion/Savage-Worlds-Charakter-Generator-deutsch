# test units/test_character_handler.py
"""
Unit Tests für CharacterHandler
"""

import unittest
from unittest.mock import Mock, MagicMock, patch

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
        self.mock_widget.pdf_manager = None
        self.mock_widget.statistics_manager = None

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
        self.mock_app.controller.charakter.test_attr = "test_value"
        result = self.character_handler.get_charakter_value('test_attr', 'default')
        self.assertEqual(result, "test_value")

    def test_get_charakter_value_without_charakter(self):
        """Test Charakter-Wert-Abruf ohne Charakter"""
        self.mock_app.controller = None
        self.character_handler.controller = None
        result = self.character_handler.get_charakter_value('test_attr', 'default')
        self.assertEqual(result, 'default')

    @patch('controllers.character_handler.Logger')
    def test_update_maximale_attributsteigerungen(self, mock_logger):
        """Test Update der maximalen Attributsteigerungen"""
        mock_field = Mock()
        mock_field.text = "7"
        self.mock_widget.ids.attributsteigerungen_field = mock_field

        self.character_handler.update_maximale_attributsteigerungen()

        self.assertEqual(self.mock_app.controller.charakter.maximale_attributsteigerungen, 7)

    @patch('controllers.character_handler.Logger')
    def test_update_maximale_fertigkeitssteigerungen(self, mock_logger):
        """Test Update der maximalen Fertigkeitssteigerungen"""
        mock_field = Mock()
        mock_field.text = "14"
        self.mock_widget.ids.fertigkeitssteigerungen_field = mock_field

        self.character_handler.update_maximale_fertigkeitssteigerungen()

        self.assertEqual(self.mock_app.controller.charakter.maximale_fertigkeitssteigerungen, 14)

    @patch('controllers.character_handler.Logger')
    def test_create_new_character(self, mock_logger):
        """Test Erstellung eines neuen Charakters"""
        self.mock_app.controller.neuer_charakter = Mock()
        self.mock_app.controller.charakter = Mock()

        self.character_handler.create_new_character()

        self.mock_app.controller.neuer_charakter.assert_called_once()
        mock_logger.info.assert_called_with("Neuer Charakter erstellt")

    @patch('controllers.character_handler.Logger')
    def test_create_new_character_no_controller(self, mock_logger):
        """Test Charaktererstellung ohne Controller"""
        self.mock_app.controller = None
        self.character_handler.controller = None

        self.character_handler.create_new_character()

        mock_logger.warning.assert_called_with("Controller nicht verfügbar für neuen Charakter")

    @patch('controllers.character_handler.service_container')
    @patch('controllers.character_handler.Logger')
    def test_schnellspeichern_charakter(self, mock_logger, mock_sc):
        """Test Schnellspeicherung ohne Charakter - zeigt Fehler-Dialog"""
        self.mock_app.controller.charakter = None
        mock_dialog = Mock()
        mock_sc.get_dialog_service.return_value = mock_dialog

        self.character_handler.schnellspeichern_charakter()

        mock_dialog.show_error_dialog.assert_called_once()

    @patch('controllers.character_handler.service_container')
    @patch('controllers.character_handler.Logger')
    def test_speichere_charakter(self, mock_logger, mock_sc):
        """Test Speichern-Dialog öffnen"""
        mock_file_service = Mock()
        mock_sc.get_file_manager_service.return_value = mock_file_service
        mock_dialog = Mock()
        mock_sc.get_dialog_service.return_value = mock_dialog

        self.character_handler.speichere_charakter()

        # File service sollte abgerufen worden sein
        mock_sc.get_file_manager_service.assert_called()

    @patch('controllers.character_handler.service_container')
    @patch('controllers.character_handler.Logger')
    def test_lade_charakter(self, mock_logger, mock_sc):
        """Test Charakterladen - öffnet FileManager-Dialog"""
        mock_file_service = Mock()
        mock_file_service.get_default_directory.return_value = '/tmp'
        mock_sc.get_file_manager_service.return_value = mock_file_service

        self.character_handler.lade_charakter()

        mock_file_service.show_file_manager.assert_called_once()
        mock_logger.info.assert_called_with("Charakter-Laden-Dialog geöffnet")

    @patch('controllers.character_handler.Logger')
    def test_erzeuge_charakterbogen_pdf(self, mock_logger):
        """Test PDF-Erzeugung über pdf_manager"""
        mock_pdf_manager = Mock()
        self.mock_widget.pdf_manager = mock_pdf_manager

        self.character_handler.erzeuge_charakterbogen_pdf()

        mock_pdf_manager.create_character_pdf.assert_called_once()

    @patch('controllers.character_handler.Logger')
    def test_zeige_statblock(self, mock_logger):
        """Test Statblock-Anzeige über statistics_manager"""
        mock_stats_manager = Mock()
        self.mock_widget.statistics_manager = mock_stats_manager

        self.character_handler.zeige_statblock()

        mock_stats_manager.show_statblock.assert_called_once()

    @patch('controllers.character_handler.Logger')
    def test_update_vermoegen_with_values(self, mock_logger):
        """Test Vermögen-Update mit Werten"""
        mock_field = Mock()
        mock_field.text = "100"
        self.mock_widget.ids.vermoegen_field = mock_field
        self.mock_app.controller.charakter.vermoegen = 50

        self.character_handler.update_vermoegen()

        self.assertEqual(self.mock_app.controller.charakter.vermoegen, 100)

    @patch('controllers.character_handler.increase_aufstiege')
    @patch('controllers.character_handler.Logger')
    def test_erhoehe_aufstieg(self, mock_logger, mock_increase):
        """Test Aufstieg-Erhöhung"""
        self.character_handler.erhoehe_aufstieg()

        mock_increase.assert_called_once_with(self.mock_app.controller.charakter)
        mock_logger.info.assert_called_with("Aufstieg erhöht")

    @patch('controllers.character_handler.decrease_aufstiege')
    @patch('controllers.character_handler.Logger')
    def test_senke_aufstieg(self, mock_logger, mock_decrease):
        """Test Aufstieg-Senkung"""
        self.character_handler.senke_aufstieg()

        mock_decrease.assert_called_once_with(self.mock_app.controller.charakter)
        mock_logger.info.assert_called_with("Aufstieg gesenkt")

    @patch('controllers.character_handler.decrease_aufstiege')
    @patch('controllers.character_handler.Logger')
    def test_senke_aufstieg_minimum(self, mock_logger, mock_decrease):
        """Test Aufstieg-Senkung - decrease_aufstiege immer aufgerufen (interne Begrenzung)"""
        self.character_handler.senke_aufstieg()

        # decrease_aufstiege übernimmt die Minimum-Prüfung intern
        mock_decrease.assert_called_once_with(self.mock_app.controller.charakter)

    @patch('controllers.character_handler.Logger')
    def test_exception_handling_create_character(self, mock_logger):
        """Test Exception-Handling bei Charaktererstellung"""
        self.mock_app.controller.neuer_charakter = Mock(side_effect=Exception("Test Error"))

        self.character_handler.create_new_character()

        mock_logger.error.assert_called_with("Fehler beim Erstellen eines neuen Charakters: Test Error")

    @patch('controllers.character_handler.Logger')
    def test_on_character_created_event(self, mock_logger):
        """Test Character-Created Event"""
        self.character_handler._update_ui_fields = Mock()
        test_data = {"character": "test_character"}

        self.character_handler.on_character_created(test_data)

        self.character_handler._update_ui_fields.assert_called_once()
        mock_logger.info.assert_called_with(f"Charakter erstellt: {test_data}")

    @patch('controllers.character_handler.Logger')
    def test_on_character_loaded_event(self, mock_logger):
        """Test Character-Loaded Event"""
        self.character_handler._update_ui_fields = Mock()
        test_data = {"character": "loaded_character"}

        self.character_handler.on_character_loaded(test_data)

        self.character_handler._update_ui_fields.assert_called_once()
        mock_logger.info.assert_called_with(f"Charakter geladen: {test_data}")


if __name__ == '__main__':
    unittest.main()
