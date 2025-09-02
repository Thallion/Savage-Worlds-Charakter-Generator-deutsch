# tests/test_einstellungen_widget.py
"""
Unit Tests für refactortes EinstellungenWidget
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from kivy.app import App
from kivymd.app import MDApp

# Mocking Kivy und KivyMD vor Import
with patch('kivy.logger.Logger'), patch('kivymd.app.MDApp'), \
     patch('kivy.lang.Builder'), patch('kivy.clock.Clock'):
    from views.einstellungen_widget import EinstellungenWidget


class TestEinstellungenWidget(unittest.TestCase):
    """Test-Klasse für das refactorte EinstellungenWidget"""
    
    def setUp(self):
        """Setup vor jedem Test"""
        # Mock App
        self.mock_app = Mock()
        
        # Mock Handler-Klassen
        self.mock_theme_handler = Mock()
        self.mock_character_handler = Mock()
        self.mock_template_handler = Mock()
        self.mock_game_elements_handler = Mock()
        
        # Mock Manager-Klassen
        self.mock_theme_manager = Mock()
        self.mock_statistics_manager = Mock()
        
        # Mock Event Service
        self.mock_event_service = Mock()
        self.mock_service_container = Mock()
        self.mock_service_container.get_event_service.return_value = self.mock_event_service
        
    @patch('views.einstellungen_widget.MDApp.get_running_app')
    @patch('views.einstellungen_widget.get_service_container')
    @patch('views.einstellungen_widget.MANAGERS_AVAILABLE', True)
    @patch('views.einstellungen_widget.ThemeHandler')
    @patch('views.einstellungen_widget.CharacterHandler')
    @patch('views.einstellungen_widget.TemplateHandler')
    @patch('views.einstellungen_widget.GameElementsHandler')
    @patch('views.einstellungen_widget.ThemeManager')
    @patch('views.einstellungen_widget.StatisticsManager')
    def test_init_with_managers(self, mock_stats_manager, mock_theme_manager,
                               mock_game_handler, mock_template_handler, 
                               mock_char_handler, mock_theme_handler,
                               mock_get_service_container, mock_get_app):
        """Test Initialisierung mit verfügbaren Managern"""
        # Setup
        mock_get_app.return_value = self.mock_app
        mock_get_service_container.return_value = self.mock_service_container
        
        mock_theme_handler.return_value = self.mock_theme_handler
        mock_char_handler.return_value = self.mock_character_handler
        mock_template_handler.return_value = self.mock_template_handler
        mock_game_handler.return_value = self.mock_game_elements_handler
        
        mock_theme_manager.return_value = self.mock_theme_manager
        mock_stats_manager.return_value = self.mock_statistics_manager
        
        # Test
        widget = EinstellungenWidget()
        
        # Prüfe Handler-Initialisierung
        self.assertEqual(widget.theme_handler, self.mock_theme_handler)
        self.assertEqual(widget.character_handler, self.mock_character_handler)
        self.assertEqual(widget.template_handler, self.mock_template_handler)
        self.assertEqual(widget.game_elements_handler, self.mock_game_elements_handler)
        
        # Prüfe Manager-Initialisierung
        self.assertEqual(widget.theme_manager, self.mock_theme_manager)
        self.assertEqual(widget.statistics_manager, self.mock_statistics_manager)
        
    @patch('views.einstellungen_widget.MDApp.get_running_app')
    @patch('views.einstellungen_widget.get_service_container')
    @patch('views.einstellungen_widget.MANAGERS_AVAILABLE', False)
    @patch('views.einstellungen_widget.ThemeHandler')
    @patch('views.einstellungen_widget.CharacterHandler')
    @patch('views.einstellungen_widget.TemplateHandler')
    @patch('views.einstellungen_widget.GameElementsHandler')
    def test_init_without_managers(self, mock_game_handler, mock_template_handler, 
                                  mock_char_handler, mock_theme_handler,
                                  mock_get_service_container, mock_get_app):
        """Test Initialisierung ohne Manager (Handler-Only-Modus)"""
        # Setup
        mock_get_app.return_value = self.mock_app
        mock_get_service_container.return_value = self.mock_service_container
        
        mock_theme_handler.return_value = self.mock_theme_handler
        mock_char_handler.return_value = self.mock_character_handler
        mock_template_handler.return_value = self.mock_template_handler
        mock_game_handler.return_value = self.mock_game_elements_handler
        
        # Test
        widget = EinstellungenWidget()
        
        # Prüfe Handler-Initialisierung
        self.assertEqual(widget.theme_handler, self.mock_theme_handler)
        self.assertEqual(widget.character_handler, self.mock_character_handler)
        self.assertEqual(widget.template_handler, self.mock_template_handler)
        self.assertEqual(widget.game_elements_handler, self.mock_game_elements_handler)
        
        # Prüfe Manager sind None
        self.assertIsNone(widget.theme_manager)
        self.assertIsNone(widget.statistics_manager)
        
    @patch('views.einstellungen_widget.MDApp.get_running_app')
    @patch('views.einstellungen_widget.get_service_container')
    @patch('views.einstellungen_widget.ThemeHandler')
    @patch('views.einstellungen_widget.CharacterHandler')
    @patch('views.einstellungen_widget.TemplateHandler')
    @patch('views.einstellungen_widget.GameElementsHandler')
    def test_event_registration(self, mock_game_handler, mock_template_handler, 
                               mock_char_handler, mock_theme_handler,
                               mock_get_service_container, mock_get_app):
        """Test Event-Handler-Registrierung"""
        # Setup
        mock_get_app.return_value = self.mock_app
        mock_get_service_container.return_value = self.mock_service_container
        
        mock_theme_handler.return_value = self.mock_theme_handler
        mock_char_handler.return_value = self.mock_character_handler
        mock_template_handler.return_value = self.mock_template_handler
        mock_game_handler.return_value = self.mock_game_elements_handler
        
        # Test
        widget = EinstellungenWidget()
        
        # Prüfe Event-Service-Subscriptions
        self.mock_event_service.subscribe.assert_any_call(
            unittest.mock.ANY, self.mock_character_handler.on_character_created
        )
        self.mock_event_service.subscribe.assert_any_call(
            unittest.mock.ANY, self.mock_character_handler.on_character_loaded
        )
        self.mock_event_service.subscribe.assert_any_call(
            unittest.mock.ANY, self.mock_theme_handler.on_theme_changed
        )
        
    # ==================== DELEGATIONS-TESTS ====================
    
    @patch('views.einstellungen_widget.MDApp.get_running_app')
    @patch('views.einstellungen_widget.get_service_container') 
    @patch('views.einstellungen_widget.ThemeHandler')
    @patch('views.einstellungen_widget.CharacterHandler')
    @patch('views.einstellungen_widget.TemplateHandler')
    @patch('views.einstellungen_widget.GameElementsHandler')
    def test_theme_delegation(self, mock_game_handler, mock_template_handler, 
                             mock_char_handler, mock_theme_handler,
                             mock_get_service_container, mock_get_app):
        """Test Theme-Methoden-Delegation"""
        # Setup
        mock_get_app.return_value = self.mock_app
        mock_get_service_container.return_value = self.mock_service_container
        
        mock_theme_handler.return_value = self.mock_theme_handler
        mock_char_handler.return_value = self.mock_character_handler
        mock_template_handler.return_value = self.mock_template_handler
        mock_game_handler.return_value = self.mock_game_elements_handler
        
        widget = EinstellungenWidget()
        
        # Test switch_theme_style Delegation
        widget.switch_theme_style('Dark')
        self.mock_theme_handler.switch_theme_style.assert_called_once_with('Dark')
        
        # Test on_color_selected Delegation
        widget.on_color_selected('Blue')
        self.mock_theme_handler.on_color_selected.assert_called_once_with('Blue')
        
    @patch('views.einstellungen_widget.MDApp.get_running_app')
    @patch('views.einstellungen_widget.get_service_container')
    @patch('views.einstellungen_widget.ThemeHandler')
    @patch('views.einstellungen_widget.CharacterHandler')
    @patch('views.einstellungen_widget.TemplateHandler')
    @patch('views.einstellungen_widget.GameElementsHandler')
    def test_character_delegation(self, mock_game_handler, mock_template_handler, 
                                 mock_char_handler, mock_theme_handler,
                                 mock_get_service_container, mock_get_app):
        """Test Character-Methoden-Delegation"""
        # Setup
        mock_get_app.return_value = self.mock_app
        mock_get_service_container.return_value = self.mock_service_container
        
        mock_theme_handler.return_value = self.mock_theme_handler
        mock_char_handler.return_value = self.mock_character_handler
        mock_template_handler.return_value = self.mock_template_handler
        mock_game_handler.return_value = self.mock_game_elements_handler
        
        widget = EinstellungenWidget()
        
        # Test get_charakter_value Delegation
        self.mock_character_handler.get_charakter_value.return_value = "test_value"
        result = widget.get_charakter_value('test_attr', 'default')
        
        self.mock_character_handler.get_charakter_value.assert_called_once_with('test_attr', 'default')
        self.assertEqual(result, "test_value")
        
        # Test create_new_character Delegation
        widget.create_new_character()
        self.mock_character_handler.create_new_character.assert_called_once()
        
        # Test Speicher-/Lade-Delegationen
        widget.schnellspeichern_charakter()
        self.mock_character_handler.schnellspeichern_charakter.assert_called_once()
        
        widget.speichere_charakter()
        self.mock_character_handler.speichere_charakter.assert_called_once()
        
        widget.lade_charakter()
        self.mock_character_handler.lade_charakter.assert_called_once()
        
    @patch('views.einstellungen_widget.MDApp.get_running_app')
    @patch('views.einstellungen_widget.get_service_container')
    @patch('views.einstellungen_widget.ThemeHandler')
    @patch('views.einstellungen_widget.CharacterHandler')
    @patch('views.einstellungen_widget.TemplateHandler')
    @patch('views.einstellungen_widget.GameElementsHandler')
    def test_template_delegation(self, mock_game_handler, mock_template_handler, 
                                mock_char_handler, mock_theme_handler,
                                mock_get_service_container, mock_get_app):
        """Test Template-Methoden-Delegation"""
        # Setup
        mock_get_app.return_value = self.mock_app
        mock_get_service_container.return_value = self.mock_service_container
        
        mock_theme_handler.return_value = self.mock_theme_handler
        mock_char_handler.return_value = self.mock_character_handler
        mock_template_handler.return_value = self.mock_template_handler
        mock_game_handler.return_value = self.mock_game_elements_handler
        
        # Mock selected_template property
        self.mock_template_handler.selected_template = "Test Template"
        
        widget = EinstellungenWidget()
        
        # Test show_template_selection_dialog Delegation
        widget.show_template_selection_dialog()
        self.mock_template_handler.show_template_selection_dialog.assert_called_once()
        
        # Test generate_character_from_selected_template Delegation
        widget.generate_character_from_selected_template()
        self.mock_template_handler.generate_character_from_selected_template.assert_called_once()
        
        # Test selected_template Property
        result = widget.selected_template
        self.assertEqual(result, "Test Template")
        
    @patch('views.einstellungen_widget.MDApp.get_running_app')
    @patch('views.einstellungen_widget.get_service_container')
    @patch('views.einstellungen_widget.ThemeHandler')
    @patch('views.einstellungen_widget.CharacterHandler')
    @patch('views.einstellungen_widget.TemplateHandler')
    @patch('views.einstellungen_widget.GameElementsHandler')
    def test_game_elements_delegation(self, mock_game_handler, mock_template_handler, 
                                     mock_char_handler, mock_theme_handler,
                                     mock_get_service_container, mock_get_app):
        """Test GameElements-Methoden-Delegation"""
        # Setup
        mock_get_app.return_value = self.mock_app
        mock_get_service_container.return_value = self.mock_service_container
        
        mock_theme_handler.return_value = self.mock_theme_handler
        mock_char_handler.return_value = self.mock_character_handler
        mock_template_handler.return_value = self.mock_template_handler
        mock_game_handler.return_value = self.mock_game_elements_handler
        
        widget = EinstellungenWidget()
        
        # Test Volk-Delegationen
        widget.open_add_volk_dialog()
        self.mock_game_elements_handler.open_add_volk_dialog.assert_called_once()
        
        widget.open_delete_volk_dialog()
        self.mock_game_elements_handler.open_delete_volk_dialog.assert_called_once()
        
        # Test Talent-Delegationen
        widget.open_add_talent_popup()
        self.mock_game_elements_handler.open_add_talent_popup.assert_called_once()
        
        widget.open_delete_talent_popup()
        self.mock_game_elements_handler.open_delete_talent_popup.assert_called_once()
        
        # Test Macht-Delegationen
        widget.open_add_macht_popup()
        self.mock_game_elements_handler.open_add_macht_popup.assert_called_once()
        
        widget.open_delete_macht_popup()
        self.mock_game_elements_handler.open_delete_macht_popup.assert_called_once()
        
        # Test Setting-Delegationen
        widget.open_add_setting_popup()
        self.mock_game_elements_handler.open_add_setting_popup.assert_called_once()
        
        widget.open_setting_switch_options()
        self.mock_game_elements_handler.open_setting_switch_options.assert_called_once()
        
        widget.open_delete_setting_popup()
        self.mock_game_elements_handler.open_delete_setting_popup.assert_called_once()
        
    # ==================== POST-INIT TESTS ====================
    
    @patch('views.einstellungen_widget.MDApp.get_running_app')
    @patch('views.einstellungen_widget.get_service_container')
    @patch('views.einstellungen_widget.MANAGERS_AVAILABLE', True)
    @patch('views.einstellungen_widget.ThemeHandler')
    @patch('views.einstellungen_widget.CharacterHandler')
    @patch('views.einstellungen_widget.TemplateHandler')
    @patch('views.einstellungen_widget.GameElementsHandler')
    @patch('views.einstellungen_widget.ThemeManager')
    @patch('views.einstellungen_widget.StatisticsManager')
    def test_post_init_with_managers(self, mock_stats_manager, mock_theme_manager,
                                    mock_game_handler, mock_template_handler, 
                                    mock_char_handler, mock_theme_handler,
                                    mock_get_service_container, mock_get_app):
        """Test Post-Initialisierung mit Managern"""
        # Setup
        mock_get_app.return_value = self.mock_app
        mock_get_service_container.return_value = self.mock_service_container
        
        mock_theme_handler.return_value = self.mock_theme_handler
        mock_char_handler.return_value = self.mock_character_handler
        mock_template_handler.return_value = self.mock_template_handler
        mock_game_handler.return_value = self.mock_game_elements_handler
        
        mock_theme_manager.return_value = self.mock_theme_manager
        mock_stats_manager.return_value = self.mock_statistics_manager
        
        widget = EinstellungenWidget()
        
        # Test Post-Init-Ausführung
        widget._post_init(0)
        
        # Prüfe dass Theme initialisiert wurde
        self.mock_theme_handler.initialize_theme.assert_called_once()
        
        # Prüfe dass Character-Handler UI aktualisiert
        self.mock_character_handler._update_ui_fields.assert_called_once()
        
        # Prüfe dass Statistics-Manager aktualisiert wird
        self.mock_statistics_manager.update_element_statistics_ui.assert_called_once()
        
    # ==================== CLEANUP TESTS ====================
    
    @patch('views.einstellungen_widget.MDApp.get_running_app')
    @patch('views.einstellungen_widget.get_service_container')
    @patch('views.einstellungen_widget.ThemeHandler')
    @patch('views.einstellungen_widget.CharacterHandler')
    @patch('views.einstellungen_widget.TemplateHandler')
    @patch('views.einstellungen_widget.GameElementsHandler')
    def test_on_stop_cleanup(self, mock_game_handler, mock_template_handler, 
                            mock_char_handler, mock_theme_handler,
                            mock_get_service_container, mock_get_app):
        """Test Cleanup beim Beenden"""
        # Setup
        mock_get_app.return_value = self.mock_app
        mock_get_service_container.return_value = self.mock_service_container
        
        mock_theme_handler.return_value = self.mock_theme_handler
        mock_char_handler.return_value = self.mock_character_handler
        mock_template_handler.return_value = self.mock_template_handler
        mock_game_handler.return_value = self.mock_game_elements_handler
        
        widget = EinstellungenWidget()
        
        # Test Cleanup
        widget.on_stop()
        
        # Prüfe Event-Unsubscriptions
        self.mock_event_service.unsubscribe.assert_any_call(
            unittest.mock.ANY, self.mock_character_handler.on_character_created
        )
        self.mock_event_service.unsubscribe.assert_any_call(
            unittest.mock.ANY, self.mock_character_handler.on_character_loaded
        )
        self.mock_event_service.unsubscribe.assert_any_call(
            unittest.mock.ANY, self.mock_theme_handler.on_theme_changed
        )
        
    # ==================== ERROR HANDLING TESTS ====================
    
    @patch('views.einstellungen_widget.MDApp.get_running_app')
    @patch('views.einstellungen_widget.get_service_container')
    @patch('views.einstellungen_widget.ThemeHandler', side_effect=Exception("Handler Error"))
    @patch('views.einstellungen_widget.Logger')
    def test_handler_initialization_error(self, mock_logger, mock_theme_handler,
                                         mock_get_service_container, mock_get_app):
        """Test Fehlerbehandlung bei Handler-Initialisierung"""
        # Setup
        mock_get_app.return_value = self.mock_app
        mock_get_service_container.return_value = self.mock_service_container
        
        # Test - sollte Exception abfangen
        widget = EinstellungenWidget()
        
        mock_logger.error.assert_called_with("Fehler bei Handler-Initialisierung: Handler Error")
        
    @patch('views.einstellungen_widget.MDApp.get_running_app')
    @patch('views.einstellungen_widget.get_service_container')
    @patch('views.einstellungen_widget.ThemeHandler')
    @patch('views.einstellungen_widget.CharacterHandler')
    @patch('views.einstellungen_widget.TemplateHandler')
    @patch('views.einstellungen_widget.GameElementsHandler')
    @patch('views.einstellungen_widget.Logger')
    def test_post_init_error_handling(self, mock_logger, mock_game_handler, 
                                     mock_template_handler, mock_char_handler, 
                                     mock_theme_handler, mock_get_service_container, 
                                     mock_get_app):
        """Test Fehlerbehandlung bei Post-Initialisierung"""
        # Setup
        mock_get_app.return_value = self.mock_app
        mock_get_service_container.return_value = self.mock_service_container
        
        mock_theme_handler.return_value = self.mock_theme_handler
        mock_char_handler.return_value = self.mock_character_handler
        mock_template_handler.return_value = self.mock_template_handler
        mock_game_handler.return_value = self.mock_game_elements_handler
        
        # Simuliere Fehler bei Theme-Initialisierung
        self.mock_theme_handler.initialize_theme.side_effect = Exception("Theme Error")
        
        widget = EinstellungenWidget()
        
        # Test Post-Init mit Fehler
        widget._post_init(0)
        
        mock_logger.error.assert_called_with("Fehler bei Post-Initialisierung: Theme Error")


if __name__ == '__main__':
    unittest.main()