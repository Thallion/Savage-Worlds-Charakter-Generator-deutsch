# test units/test_game_elements_handler.py
"""
Unit Tests für GameElementsHandler
"""

import unittest
from unittest.mock import Mock, MagicMock, patch

# Mocking Kivy vor Import
with patch('kivy.logger.Logger'), patch('kivymd.app.MDApp'):
    from controllers.game_elements_handler import GameElementsHandler


class TestGameElementsHandler(unittest.TestCase):
    """Test-Klasse für GameElementsHandler"""

    def setUp(self):
        """Setup vor jedem Test"""
        self.mock_widget = Mock()
        self.mock_widget.ids = Mock()

        self.mock_app = Mock()
        self.mock_app.controller = Mock()
        self.mock_app.controller.charakter = Mock()
        self.mock_widget.app = self.mock_app

        self.handler = GameElementsHandler(self.mock_widget)

    def test_init(self):
        """Test Initialisierung"""
        self.assertEqual(self.handler.widget, self.mock_widget)
        self.assertEqual(self.handler.app, self.mock_app)

    def test_charakter_controller_property(self):
        """Test charakter_controller Property"""
        self.assertEqual(self.handler.charakter_controller, self.mock_app.controller)

    # ==================== STUB METHODS ====================

    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_volk_dialog(self, mock_logger):
        """Test Volk-Hinzufügen-Stub"""
        self.handler.open_add_volk_dialog()
        mock_logger.info.assert_called_with("Volk hinzufügen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_volk_dialog(self, mock_logger):
        """Test Volk-Löschen-Stub"""
        self.handler.open_delete_volk_dialog()
        mock_logger.info.assert_called_with("Volk löschen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_talent_popup(self, mock_logger):
        """Test Talent-Hinzufügen-Stub"""
        self.handler.open_add_talent_popup()
        mock_logger.info.assert_called_with("Talent hinzufügen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_talent_popup(self, mock_logger):
        """Test Talent-Löschen-Stub"""
        self.handler.open_delete_talent_popup()
        mock_logger.info.assert_called_with("Talent löschen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_macht_popup(self, mock_logger):
        """Test Macht-Hinzufügen-Stub"""
        self.handler.open_add_macht_popup()
        mock_logger.info.assert_called_with("Macht hinzufügen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_macht_popup(self, mock_logger):
        """Test Macht-Löschen-Stub"""
        self.handler.open_delete_macht_popup()
        mock_logger.info.assert_called_with("Macht löschen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_fertigkeit_popup(self, mock_logger):
        """Test Fertigkeit-Hinzufügen-Stub"""
        self.handler.open_add_fertigkeit_popup()
        mock_logger.info.assert_called_with("Fertigkeit hinzufügen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_fertigkeit_popup(self, mock_logger):
        """Test Fertigkeit-Löschen-Stub"""
        self.handler.open_delete_fertigkeit_popup()
        mock_logger.info.assert_called_with("Fertigkeit löschen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_handicap_popup(self, mock_logger):
        """Test Handicap-Hinzufügen-Stub"""
        self.handler.open_add_handicap_popup()
        mock_logger.info.assert_called_with("Handicap hinzufügen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_handicap_popup(self, mock_logger):
        """Test Handicap-Löschen-Stub"""
        self.handler.open_delete_handicap_popup()
        mock_logger.info.assert_called_with("Handicap löschen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_ausruestung_popup(self, mock_logger):
        """Test Ausrüstung-Hinzufügen-Stub"""
        self.handler.open_add_ausruestung_popup()
        mock_logger.info.assert_called_with("Ausrüstung hinzufügen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_ausruestung_popup(self, mock_logger):
        """Test Ausrüstung-Löschen-Stub"""
        self.handler.open_delete_ausruestung_popup()
        mock_logger.info.assert_called_with("Ausrüstung löschen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_waffe_popup(self, mock_logger):
        """Test Waffe-Hinzufügen-Stub"""
        self.handler.open_add_waffe_popup()
        mock_logger.info.assert_called_with("Waffe hinzufügen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_waffe_popup(self, mock_logger):
        """Test Waffe-Löschen-Stub"""
        self.handler.open_delete_waffe_popup()
        mock_logger.info.assert_called_with("Waffe löschen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_ruestung_popup(self, mock_logger):
        """Test Rüstung-Hinzufügen-Stub"""
        self.handler.open_add_ruestung_popup()
        mock_logger.info.assert_called_with("Rüstung hinzufügen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_ruestung_popup(self, mock_logger):
        """Test Rüstung-Löschen-Stub"""
        self.handler.open_delete_ruestung_popup()
        mock_logger.info.assert_called_with("Rüstung löschen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_schild_popup(self, mock_logger):
        """Test Schild-Hinzufügen-Stub"""
        self.handler.open_add_schild_popup()
        mock_logger.info.assert_called_with("Schild hinzufügen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_schild_popup(self, mock_logger):
        """Test Schild-Löschen-Stub"""
        self.handler.open_delete_schild_popup()
        mock_logger.info.assert_called_with("Schild löschen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_setting_popup(self, mock_logger):
        """Test Setting-Hinzufügen-Stub"""
        self.handler.open_add_setting_popup()
        mock_logger.info.assert_called_with("Setting hinzufügen - Stub aufgerufen")

    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_setting_popup(self, mock_logger):
        """Test Setting-Löschen-Stub"""
        self.handler.open_delete_setting_popup()
        mock_logger.info.assert_called_with("Setting löschen - Stub aufgerufen")

    # ==================== SETTING MANAGEMENT ====================

    @patch('controllers.game_elements_handler.service_container')
    def test_open_setting_switch_options_no_charakter(self, mock_sc):
        """Test Setting-Wechsel ohne Charakter - zeigt Fehler-Dialog"""
        self.mock_app.controller.charakter = None
        mock_dialog = Mock()
        mock_sc.get_dialog_service.return_value = mock_dialog

        self.handler.open_setting_switch_options()

        mock_dialog.show_error_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.service_container')
    def test_open_setting_switch_options_single_setting(self, mock_sc):
        """Test Setting-Wechsel mit nur einem verfügbaren Setting"""
        char = self.mock_app.controller.charakter
        char.custom_element_manager.get_all_settings.return_value = ['SWAE']
        char.active_setting_name = 'SWAE'
        mock_dialog = Mock()
        mock_sc.get_dialog_service.return_value = mock_dialog

        self.handler.open_setting_switch_options()

        mock_dialog.show_info_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.service_container')
    def test_open_setting_switch_options_multiple_settings(self, mock_sc):
        """Test Setting-Wechsel mit mehreren Settings - zeigt Auswahl"""
        char = self.mock_app.controller.charakter
        char.custom_element_manager.get_all_settings.return_value = ['SWAE', 'Fantasy Kompendium']
        char.active_setting_name = 'SWAE'
        mock_dialog = Mock()
        mock_sc.get_dialog_service.return_value = mock_dialog

        self.handler.open_setting_switch_options()

        mock_dialog.show_choice_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_apply_setting_change_success(self, mock_sc, mock_logger):
        """Test erfolgreicher Setting-Wechsel"""
        char = self.mock_app.controller.charakter
        char.change_active_setting.return_value = True
        mock_dialog = Mock()
        mock_sc.get_dialog_service.return_value = mock_dialog
        mock_sc.get_event_service.return_value = None

        self.handler._apply_setting_change('Fantasy Kompendium', 'merge')

        mock_dialog.show_success_dialog.assert_called_once()
        mock_logger.info.assert_called()

    @patch('controllers.game_elements_handler.service_container')
    def test_apply_setting_change_failure(self, mock_sc):
        """Test fehlgeschlagener Setting-Wechsel"""
        char = self.mock_app.controller.charakter
        char.change_active_setting.return_value = False
        mock_dialog = Mock()
        mock_sc.get_dialog_service.return_value = mock_dialog
        mock_sc.get_event_service.return_value = None

        self.handler._apply_setting_change('Fantasy Kompendium', 'replace')

        mock_dialog.show_error_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.service_container')
    def test_on_setting_choice_made_same_setting(self, mock_sc):
        """Test Setting-Auswahl mit gleichem Setting - keine Änderung"""
        char = self.mock_app.controller.charakter
        char.active_setting_name = 'SWAE'
        mock_dialog = Mock()
        mock_sc.get_dialog_service.return_value = mock_dialog

        self.handler._on_setting_choice_made('SWAE')

        # Kein Merge-Dialog sollte geöffnet werden
        mock_dialog.show_setting_merge_dialog.assert_not_called()

    @patch('controllers.game_elements_handler.service_container')
    def test_on_setting_choice_made_different_setting(self, mock_sc):
        """Test Setting-Auswahl mit anderem Setting - zeigt Merge-Dialog"""
        char = self.mock_app.controller.charakter
        char.active_setting_name = 'SWAE'
        mock_dialog = Mock()
        mock_sc.get_dialog_service.return_value = mock_dialog

        self.handler._on_setting_choice_made('Fantasy Kompendium')

        mock_dialog.show_setting_merge_dialog.assert_called_once()


if __name__ == '__main__':
    unittest.main()
