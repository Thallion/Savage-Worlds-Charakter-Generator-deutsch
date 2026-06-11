# test units/test_template_handler.py
"""
Unit Tests für TemplateHandler
"""

import unittest
from unittest.mock import Mock, MagicMock, patch


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

        # Kivy Clock patchen damit __init__ nicht fehlschlägt
        with patch('kivy.logger.Logger'), \
             patch('kivy.clock.Clock.schedule_once'), \
             patch('kivymd.app.MDApp'):
            from controllers.template_handler import TemplateHandler
            self.TemplateHandler = TemplateHandler

        with patch('kivy.clock.Clock.schedule_once'):
            self.template_handler = self.TemplateHandler(self.mock_widget)

    def test_init(self):
        """Test Initialisierung"""
        self.assertEqual(self.template_handler.widget, self.mock_widget)
        self.assertEqual(self.template_handler.app, self.mock_app)
        self.assertIsNone(self.template_handler.selected_template)
        self.assertEqual(self.template_handler.available_templates, [])

    @patch('controllers.template_handler.MDButtonText')
    @patch('controllers.template_handler.MDButton')
    @patch('controllers.template_handler.MDLabel')
    @patch('controllers.template_handler.MDDialog')
    def test_show_template_selection_dialog_no_templates(self, mock_dialog_class, mock_label, mock_button, mock_button_text):
        """Test Template-Dialog ohne verfügbare Templates - zeigt Info-Dialog"""
        mock_dialog_inst = Mock()
        mock_dialog_class.return_value = mock_dialog_inst

        # Lazy-Loading bereits erfolgt markieren (simuliert)
        self.template_handler._templates_loaded = True
        self.template_handler.available_templates = []
        self.template_handler.show_template_selection_dialog()

        mock_dialog_class.assert_called()
        mock_dialog_inst.open.assert_called_once()

    def test_show_template_selection_dialog_with_templates(self):
        """Test Template-Dialog mit verfügbaren Templates - ruft _show_template_search_dialog"""
        templates = [{'name': 'Template1', 'description': 'Desc1', 'file': Mock()}]
        self.template_handler.available_templates = templates
        # Lazy-Loading überspringen, sonst überschreibt _load_available_templates die Vorgabe
        self.template_handler._templates_loaded = True

        with patch.object(self.template_handler, '_show_template_search_dialog') as mock_search:
            self.template_handler.show_template_selection_dialog()
            mock_search.assert_called_once()

    def test_show_template_selection_dialog_laedt_lazy(self):
        """Test Lazy-Loading: erster Dialog-Aufruf lädt die Templates genau einmal"""
        templates = [{'name': 'Template1', 'description': 'Desc1', 'file': Mock()}]

        def fake_load():
            self.template_handler.available_templates = templates

        with patch.object(self.template_handler, '_load_available_templates', side_effect=fake_load) as mock_load, \
                patch.object(self.template_handler, '_show_template_search_dialog') as mock_search:
            self.template_handler._templates_loaded = False
            self.template_handler.show_template_selection_dialog()
            self.template_handler.show_template_selection_dialog()
            mock_load.assert_called_once()
            self.assertEqual(mock_search.call_count, 2)

    @patch('controllers.template_handler.Logger')
    def test_on_template_selected_from_dialog(self, mock_logger):
        """Test Template-Auswahl aus Dialog - setzt selected_template"""
        template = {'name': 'Test Template', 'description': 'Desc', 'file': Mock()}

        self.template_handler._on_template_selected_from_dialog(template)

        self.assertEqual(self.template_handler.selected_template, template)
        mock_logger.info.assert_called_with("Template ausgewählt: Test Template")

    @patch('controllers.template_handler.MDButtonText')
    @patch('controllers.template_handler.MDButton')
    @patch('controllers.template_handler.MDLabel')
    @patch('controllers.template_handler.MDDialog')
    def test_generate_character_from_selected_template_no_template(self, mock_dialog_class, mock_label, mock_button, mock_button_text):
        """Test Charakter-Generierung ohne ausgewähltes Template - zeigt Dialog"""
        mock_dialog_inst = Mock()
        mock_dialog_class.return_value = mock_dialog_inst

        self.template_handler.selected_template = None
        self.template_handler.generate_character_from_selected_template()

        mock_dialog_class.assert_called()

    def test_generate_character_from_selected_template_with_template(self):
        """Test Charakter-Generierung mit ausgewähltem Template"""
        template = {'name': 'Test Template', 'description': 'Desc', 'file': Mock()}
        self.template_handler.selected_template = template

        with patch.object(self.template_handler, '_generate_character_from_template') as mock_gen:
            self.template_handler.generate_character_from_selected_template()
            mock_gen.assert_called_once_with(template, None)

    def test_dismiss_template_dialog(self):
        """Test Template-Dialog schließen"""
        mock_dialog = Mock()
        self.template_handler.template_dialog = mock_dialog

        self.template_handler._dismiss_template_dialog()

        mock_dialog.dismiss.assert_called_once()
        self.assertIsNone(self.template_handler.template_dialog)

    def test_dismiss_template_dialog_no_dialog(self):
        """Test Template-Dialog schließen wenn kein Dialog vorhanden"""
        self.template_handler.template_dialog = None
        # Should not raise
        self.template_handler._dismiss_template_dialog()

    @patch('controllers.template_handler.service_container')
    @patch('controllers.template_handler.Logger')
    def test_open_template_selection_dialog(self, mock_logger, mock_sc):
        """Test Template-Auswahl via FileManager"""
        mock_file_service = Mock()
        mock_file_service.get_default_directory.return_value = '/tmp/templates'
        mock_sc.get_file_manager_service.return_value = mock_file_service

        self.template_handler.open_template_selection_dialog()

        mock_file_service.show_file_manager.assert_called_once()

    @patch('controllers.template_handler.service_container')
    @patch('controllers.template_handler.Logger')
    def test_open_template_selection_dialog_no_service(self, mock_logger, mock_sc):
        """Test Template-Auswahl ohne FileManager-Service - zeigt Fehler"""
        mock_sc.get_file_manager_service.return_value = None

        self.template_handler.open_template_selection_dialog()

        mock_logger.error.assert_called()

    def test_on_template_dialog_item_selected(self):
        """Test Callback bei Template-Auswahl im Dialog"""
        template = {'name': 'Test', 'description': 'Desc', 'file': Mock()}
        mock_callback = Mock()

        with patch.object(self.template_handler, '_dismiss_template_dialog') as mock_dismiss:
            self.template_handler._on_template_dialog_item_selected(mock_callback, template)

            mock_dismiss.assert_called_once()
            mock_callback.assert_called_once_with(template)

    @patch('controllers.template_handler.Logger')
    def test_on_template_file_selected_invalid_json(self, mock_logger):
        """Test Callback mit ungültiger JSON-Datei"""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("no valid json!!!")
            temp_path = f.name

        try:
            with patch.object(self.template_handler, '_show_error_dialog') as mock_error:
                self.template_handler._on_template_file_selected(temp_path)
                mock_error.assert_called()
        finally:
            os.unlink(temp_path)

    def test_load_templates(self):
        """Test _load_templates - lädt Templates neu"""
        with patch.object(self.template_handler, '_load_available_templates') as mock_load:
            self.template_handler._load_templates()
            mock_load.assert_called_once()

    @patch('controllers.template_handler.Logger')
    def test_load_available_templates_no_dir(self, mock_logger):
        """Test Template-Laden ohne vorhandenes Verzeichnis"""
        with patch('controllers.template_handler.get_templates_path', return_value='/nonexistent/path'):
            # Should not raise
            self.template_handler._load_available_templates(0)
        # available_templates remains empty or unchanged


if __name__ == '__main__':
    unittest.main()
