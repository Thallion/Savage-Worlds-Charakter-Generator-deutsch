# tests/test_template_handler.py
"""
Unit Tests für TemplateHandler
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from kivy.app import App
from kivymd.app import MDApp

# Mocking Kivy vor Import
with patch('kivy.logger.Logger'), patch('kivymd.app.MDApp'):
    from controllers.template_handler import TemplateHandler


class TestTemplateHandler(unittest.TestCase):
    """Test-Klasse für TemplateHandler"""
    
    def setUp(self):
        """Setup vor jedem Test"""
        # Mock Widget
        self.mock_widget = Mock()
        self.mock_widget.ids = Mock()
        
        # Mock App mit Controller
        self.mock_app = Mock()
        self.mock_app.controller = Mock()
        self.mock_widget.app = self.mock_app
        
        # Template Handler erstellen
        self.template_handler = TemplateHandler(self.mock_widget)
        
    def test_init(self):
        """Test Initialisierung"""
        self.assertEqual(self.template_handler.widget, self.mock_widget)
        self.assertEqual(self.template_handler.app, self.mock_app)
        self.assertIsNone(self.template_handler.selected_template)
        
    @patch('controllers.template_handler.Logger')
    def test_show_template_selection_dialog(self, mock_logger):
        """Test Template-Auswahl-Dialog"""
        # Setup
        self.mock_app.controller.get_available_templates = Mock(return_value=['Template1', 'Template2'])
        
        with patch('controllers.template_handler.MDDialog') as mock_dialog:
            # Test
            self.template_handler.show_template_selection_dialog()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Template-Auswahl-Dialog geöffnet")
            
    @patch('controllers.template_handler.Logger')
    def test_show_template_selection_dialog_no_templates(self, mock_logger):
        """Test Template-Dialog ohne verfügbare Templates"""
        # Setup - Keine Templates verfügbar
        self.mock_app.controller.get_available_templates = Mock(return_value=[])
        
        # Test
        self.template_handler.show_template_selection_dialog()
        
        mock_logger.warning.assert_called_with("Keine Templates verfügbar")
        
    @patch('controllers.template_handler.Logger')
    def test_on_template_selected(self, mock_logger):
        """Test Template-Auswahl"""
        # Setup
        mock_checkbox = Mock()
        mock_checkbox.text = "Test Template"
        
        # Test
        self.template_handler.on_template_selected(mock_checkbox, True)
        
        # Prüfe dass Template ausgewählt wurde
        self.assertEqual(self.template_handler.selected_template, "Test Template")
        mock_logger.info.assert_called_with("Template ausgewählt: Test Template")
        
    @patch('controllers.template_handler.Logger')
    def test_on_template_deselected(self, mock_logger):
        """Test Template-Abwahl"""
        # Setup
        self.template_handler.selected_template = "Test Template"
        mock_checkbox = Mock()
        mock_checkbox.text = "Test Template"
        
        # Test
        self.template_handler.on_template_selected(mock_checkbox, False)
        
        # Prüfe dass Template abgewählt wurde
        self.assertIsNone(self.template_handler.selected_template)
        mock_logger.info.assert_called_with("Template abgewählt: Test Template")
        
    @patch('controllers.template_handler.Logger')
    def test_generate_character_from_selected_template_with_template(self, mock_logger):
        """Test Charakter-Generierung mit ausgewähltem Template"""
        # Setup
        self.template_handler.selected_template = "Test Template"
        self.mock_app.controller.generate_character_from_template = Mock()
        
        # Test
        self.template_handler.generate_character_from_selected_template()
        
        # Prüfe dass Generierung aufgerufen wurde
        self.mock_app.controller.generate_character_from_template.assert_called_once_with("Test Template")
        mock_logger.info.assert_called_with("Charakter aus Template generiert: Test Template")
        
    @patch('controllers.template_handler.Logger')
    def test_generate_character_from_selected_template_no_template(self, mock_logger):
        """Test Charakter-Generierung ohne Template"""
        # Setup - Kein Template ausgewählt
        self.template_handler.selected_template = None
        
        with patch.object(self.template_handler, 'show_template_selection_dialog') as mock_show_dialog:
            # Test
            self.template_handler.generate_character_from_selected_template()
            
            # Prüfe dass Dialog gezeigt wird
            mock_show_dialog.assert_called_once()
            mock_logger.warning.assert_called_with("Kein Template ausgewählt - zeige Auswahl-Dialog")
            
    @patch('controllers.template_handler.Logger')
    def test_on_generate_button_clicked(self, mock_logger):
        """Test Generate-Button-Klick"""
        # Setup
        self.template_handler.selected_template = "Test Template"
        mock_instance = Mock()
        mock_instance.dismiss = Mock()
        
        with patch.object(self.template_handler, 'generate_character_from_selected_template') as mock_generate:
            # Test
            self.template_handler.on_generate_button_clicked(mock_instance)
            
            # Prüfe dass Dialog geschlossen und Generierung gestartet wird
            mock_instance.dismiss.assert_called_once()
            mock_generate.assert_called_once()
            
    @patch('controllers.template_handler.Logger')
    def test_clear_template_selection(self, mock_logger):
        """Test Template-Auswahl zurücksetzen"""
        # Setup
        self.template_handler.selected_template = "Test Template"
        
        # Test
        self.template_handler.clear_template_selection()
        
        # Prüfe dass Template zurückgesetzt wurde
        self.assertIsNone(self.template_handler.selected_template)
        mock_logger.info.assert_called_with("Template-Auswahl zurückgesetzt")
        
    @patch('controllers.template_handler.Logger')
    def test_get_template_description(self, mock_logger):
        """Test Template-Beschreibung abrufen"""
        # Setup
        self.mock_app.controller.get_template_description = Mock(return_value="Template Beschreibung")
        
        # Test
        result = self.template_handler.get_template_description("Test Template")
        
        # Prüfe Rückgabe
        self.assertEqual(result, "Template Beschreibung")
        self.mock_app.controller.get_template_description.assert_called_once_with("Test Template")
        
    @patch('controllers.template_handler.Logger')
    def test_get_template_description_no_controller(self, mock_logger):
        """Test Template-Beschreibung ohne Controller"""
        # Setup - Kein Controller
        self.mock_app.controller = None
        
        # Test
        result = self.template_handler.get_template_description("Test Template")
        
        # Prüfe Fallback
        self.assertEqual(result, "Keine Beschreibung verfügbar")
        mock_logger.warning.assert_called_with("Controller nicht verfügbar für Template-Beschreibung")
        
    @patch('controllers.template_handler.Logger')
    def test_validate_template_with_valid_template(self, mock_logger):
        """Test Template-Validierung mit gültigem Template"""
        # Setup
        self.mock_app.controller.validate_template = Mock(return_value=True)
        
        # Test
        result = self.template_handler.validate_template("Valid Template")
        
        # Prüfe Validierung
        self.assertTrue(result)
        self.mock_app.controller.validate_template.assert_called_once_with("Valid Template")
        
    @patch('controllers.template_handler.Logger')
    def test_validate_template_with_invalid_template(self, mock_logger):
        """Test Template-Validierung mit ungültigem Template"""
        # Setup
        self.mock_app.controller.validate_template = Mock(return_value=False)
        
        # Test
        result = self.template_handler.validate_template("Invalid Template")
        
        # Prüfe Validierung
        self.assertFalse(result)
        mock_logger.warning.assert_called_with("Template 'Invalid Template' ist ungültig")
        
    @patch('controllers.template_handler.Logger')
    def test_exception_handling_show_dialog(self, mock_logger):
        """Test Exception-Handling bei Dialog-Anzeige"""
        # Setup - Exception simulieren
        self.mock_app.controller.get_available_templates.side_effect = Exception("Test Error")
        
        # Test
        self.template_handler.show_template_selection_dialog()
        
        mock_logger.error.assert_called_with("Fehler beim Öffnen des Template-Dialogs: Test Error")
        
    @patch('controllers.template_handler.Logger')
    def test_exception_handling_generate_character(self, mock_logger):
        """Test Exception-Handling bei Charakter-Generierung"""
        # Setup
        self.template_handler.selected_template = "Test Template"
        self.mock_app.controller.generate_character_from_template.side_effect = Exception("Generation Error")
        
        # Test
        self.template_handler.generate_character_from_selected_template()
        
        mock_logger.error.assert_called_with("Fehler bei Template-Generierung: Generation Error")
        
    @patch('controllers.template_handler.MDSelectionControl')
    @patch('controllers.template_handler.MDListItem')
    def test_create_template_list_item(self, mock_list_item, mock_selection_control):
        """Test Erstellung von Template-Listenelementen"""
        # Setup
        mock_checkbox = Mock()
        mock_selection_control.return_value = mock_checkbox
        mock_item = Mock()
        mock_list_item.return_value = mock_item
        
        # Test
        result = self.template_handler._create_template_list_item("Test Template")
        
        # Prüfe dass Listenitem erstellt wurde
        mock_list_item.assert_called_once()
        mock_selection_control.assert_called_once()
        self.assertEqual(result, mock_item)
        
    @patch('controllers.template_handler.Logger')
    def test_handle_template_dialog_dismiss(self, mock_logger):
        """Test Template-Dialog schließen"""
        # Setup
        mock_instance = Mock()
        
        # Test
        self.template_handler.on_dialog_dismiss(mock_instance)
        
        mock_logger.info.assert_called_with("Template-Dialog geschlossen")


if __name__ == '__main__':
    unittest.main()