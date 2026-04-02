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

    # ==================== DIALOG HANDLER DELEGATION ====================

    def _setup_dialog_service_mock(self, handler_attr):
        """Hilfsmethode: Mock-DialogService mit Handler einrichten"""
        mock_handler = Mock()
        mock_dialog_service = Mock()
        setattr(mock_dialog_service, handler_attr, mock_handler)
        return mock_handler, mock_dialog_service

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_add_talent_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Talent-Hinzufügen delegiert an DialogService.talent_dialog_handler"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('talent_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_add_talent_popup()

        mock_handler.show_add_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_delete_talent_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Talent-Löschen delegiert an DialogService.talent_dialog_handler"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('talent_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_delete_talent_popup()

        mock_handler.show_delete_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_add_handicap_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Handicap-Hinzufügen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('handicap_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_add_handicap_popup()

        mock_handler.show_add_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_delete_handicap_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Handicap-Löschen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('handicap_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_delete_handicap_popup()

        mock_handler.show_delete_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_add_macht_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Macht-Hinzufügen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('macht_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_add_macht_popup()

        mock_handler.show_add_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_delete_macht_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Macht-Löschen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('macht_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_delete_macht_popup()

        mock_handler.show_delete_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_add_fertigkeit_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Fertigkeit-Hinzufügen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('fertigkeit_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_add_fertigkeit_popup()

        mock_handler.show_add_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_delete_fertigkeit_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Fertigkeit-Löschen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('fertigkeit_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_delete_fertigkeit_popup()

        mock_handler.show_delete_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_add_volk_dialog_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Volk-Hinzufügen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('volk_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_add_volk_dialog()

        mock_handler.show_add_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_delete_volk_dialog_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Volk-Löschen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('volk_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_delete_volk_dialog()

        mock_handler.show_delete_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_add_setting_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Setting-Hinzufügen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('setting_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_add_setting_popup()

        mock_handler.show_add_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_delete_setting_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Setting-Löschen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('setting_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_delete_setting_popup()

        mock_handler.show_delete_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_add_ausruestung_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Ausrüstung-Hinzufügen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('ausruestung_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_add_ausruestung_popup()

        mock_handler.show_add_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_delete_ausruestung_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Ausrüstung-Löschen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('ausruestung_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_delete_ausruestung_popup()

        mock_handler.show_delete_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_add_waffe_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Waffe-Hinzufügen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('waffe_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_add_waffe_popup()

        mock_handler.show_add_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_delete_waffe_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Waffe-Löschen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('waffe_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_delete_waffe_popup()

        mock_handler.show_delete_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_add_ruestung_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Rüstung-Hinzufügen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('ruestung_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_add_ruestung_popup()

        mock_handler.show_add_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_delete_ruestung_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Rüstung-Löschen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('ruestung_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_delete_ruestung_popup()

        mock_handler.show_delete_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_add_schild_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Schild-Hinzufügen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('schild_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_add_schild_popup()

        mock_handler.show_add_dialog.assert_called_once()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_open_delete_schild_popup_delegiert_an_dialog_service(self, mock_sc, mock_logger):
        """Test Schild-Löschen delegiert an DialogService"""
        mock_handler, mock_ds = self._setup_dialog_service_mock('schild_dialog_handler')
        mock_sc.get_dialog_service.return_value = mock_ds

        self.handler.open_delete_schild_popup()

        mock_handler.show_delete_dialog.assert_called_once()

    # ==================== FALLBACK BEI FEHLENDEM DIALOG SERVICE ====================

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_handler_ohne_dialog_service_loggt_warnung(self, mock_sc, mock_logger):
        """Test: Ohne DialogService wird eine Warnung geloggt"""
        mock_sc.get_dialog_service.return_value = None

        self.handler.open_add_talent_popup()

        mock_logger.warning.assert_called()

    @patch('controllers.game_elements_handler.Logger')
    @patch('controllers.game_elements_handler.service_container')
    def test_handler_ohne_dialog_service_kein_fehler(self, mock_sc, mock_logger):
        """Test: Ohne DialogService kein Crash"""
        mock_sc.get_dialog_service.return_value = None

        # Sollte keinen Fehler werfen
        self.handler.open_add_talent_popup()
        self.handler.open_delete_handicap_popup()
        self.handler.open_add_macht_popup()

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
        """Test Setting-Wechsel mit mehreren Settings - öffnet Overlay"""
        char = self.mock_app.controller.charakter
        char.custom_element_manager.get_all_settings.return_value = ['SWAE', 'Fantasy Kompendium']
        char.active_setting_name = 'SWAE'

        with patch('views.setting_wechsel_overlay.SettingWechselOverlay') as MockOverlay:
            mock_overlay_instance = Mock()
            MockOverlay.return_value = mock_overlay_instance

            self.handler.open_setting_switch_options()

            mock_overlay_instance.open.assert_called_once_with(
                current_setting='SWAE',
                available_settings=['SWAE', 'Fantasy Kompendium'],
                on_setting_chosen=self.handler._on_setting_overlay_chosen,
            )

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
    def test_on_setting_overlay_chosen_calls_apply(self, mock_sc):
        """Test Overlay-Callback ruft _apply_setting_change auf"""
        with patch.object(self.handler, '_apply_setting_change') as mock_apply:
            self.handler._on_setting_overlay_chosen('Fantasy Kompendium', 'merge')
            mock_apply.assert_called_once_with('Fantasy Kompendium', 'merge')

    @patch('controllers.game_elements_handler.service_container')
    def test_on_setting_overlay_chosen_replace(self, mock_sc):
        """Test Overlay-Callback mit Replace-Modus"""
        with patch.object(self.handler, '_apply_setting_change') as mock_apply:
            self.handler._on_setting_overlay_chosen('Deadlands', 'replace')
            mock_apply.assert_called_once_with('Deadlands', 'replace')


if __name__ == '__main__':
    unittest.main()
