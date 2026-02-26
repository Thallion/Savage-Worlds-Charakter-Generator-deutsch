# tests/test_theme_handler.py
"""
Unit Tests für ThemeManager (manager/theme_manager.py).
Testet Theme-Initialisierung, Stil-Wechsel, Farbauswahl und Fehlerbehandlung.
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch, PropertyMock

# Kivy-Headless-Modus
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_LOG_LEVEL'] = 'critical'

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestThemeManager(unittest.TestCase):
    """Test-Klasse für ThemeManager"""

    def setUp(self):
        """Setup vor jedem Test — Mocks für App, ServiceContainer, Widget."""
        # Mock Widget mit ids.colors_box
        self.mock_widget = Mock()
        self.mock_widget.ids = Mock()
        self.mock_widget.ids.colors_box = Mock()

        # Mock App mit update_theme
        self.mock_app = Mock()
        self.mock_app.update_theme = Mock()

        # Mock Services
        self.mock_theme_service = Mock()
        self.mock_event_service = Mock()

        # Patches
        self.patcher_app = patch('manager.theme_manager.App')
        self.patcher_sc = patch('manager.theme_manager.service_container')
        self.mock_app_cls = self.patcher_app.start()
        self.mock_sc = self.patcher_sc.start()

        self.mock_app_cls.get_running_app.return_value = self.mock_app
        self.mock_sc.get_theme_service.return_value = self.mock_theme_service
        self.mock_sc.get_event_service.return_value = self.mock_event_service

        # ThemeManager instanzieren
        from manager.theme_manager import ThemeManager
        self.theme_manager = ThemeManager(self.mock_widget)

    def tearDown(self):
        self.patcher_app.stop()
        self.patcher_sc.stop()

    # === Initialisierung ===

    def test_init(self):
        """ThemeManager speichert Widget, App und Services korrekt."""
        self.assertEqual(self.theme_manager.widget, self.mock_widget)
        self.assertEqual(self.theme_manager.app, self.mock_app)
        self.assertEqual(self.theme_manager.theme_service, self.mock_theme_service)
        self.assertEqual(self.theme_manager.event_service, self.mock_event_service)

    def test_init_ohne_app(self):
        """ThemeManager funktioniert auch wenn keine App läuft."""
        self.mock_app_cls.get_running_app.return_value = None
        from manager.theme_manager import ThemeManager
        tm = ThemeManager(self.mock_widget)
        self.assertIsNone(tm.app)

    # === initialize_theme ===

    def test_initialize_theme_success(self):
        """Erfolgreiche Initialisierung ruft theme_service und create_color_chips auf."""
        self.theme_manager.initialize_theme()

        self.mock_theme_service.initialize_theme.assert_called_once()
        self.mock_theme_service.create_color_chips.assert_called_once_with(
            self.mock_widget.ids.colors_box,
            self.theme_manager.on_color_selected
        )

    def test_initialize_theme_no_colors_box(self):
        """Initialisierung ohne colors_box erstellt keine Farb-Chips."""
        # hasattr(widget.ids, 'colors_box') soll False zurückgeben
        del self.mock_widget.ids.colors_box

        self.theme_manager.initialize_theme()

        self.mock_theme_service.initialize_theme.assert_called_once()
        self.mock_theme_service.create_color_chips.assert_not_called()

    def test_initialize_theme_ohne_theme_service(self):
        """Ohne theme_service passiert nichts (kein Crash)."""
        self.theme_manager.theme_service = None
        self.theme_manager.initialize_theme()
        # Kein Fehler erwartet

    @patch('manager.theme_manager.Logger')
    def test_initialize_theme_exception(self, mock_logger):
        """Exception bei Initialisierung wird geloggt."""
        self.mock_theme_service.initialize_theme.side_effect = Exception("Test Error")

        self.theme_manager.initialize_theme()

        mock_logger.error.assert_called_once_with("Fehler bei Theme-Initialisierung: Test Error")

    # === switch_theme_style ===

    @patch('manager.theme_manager.Logger')
    def test_switch_theme_style_dark(self, mock_logger):
        """Wechsel zu Dark ruft app.update_theme auf."""
        self.theme_manager.switch_theme_style('Dark')

        self.mock_app.update_theme.assert_called_once_with(theme_style='Dark')
        mock_logger.info.assert_called_with("Theme-Stil über Manager gewechselt zu: Dark")

    @patch('manager.theme_manager.Logger')
    def test_switch_theme_style_light(self, mock_logger):
        """Wechsel zu Light ruft app.update_theme auf."""
        self.theme_manager.switch_theme_style('Light')

        self.mock_app.update_theme.assert_called_once_with(theme_style='Light')

    @patch('manager.theme_manager.Logger')
    def test_switch_theme_style_sendet_event(self, mock_logger):
        """Theme-Wechsel publiziert ein THEME_CHANGED Event."""
        from services.event_service import EventTypes
        self.theme_manager.switch_theme_style('Dark')

        self.mock_event_service.publish.assert_called_once_with(
            EventTypes.THEME_CHANGED, {'style': 'Dark'}
        )

    @patch('manager.theme_manager.Logger')
    def test_switch_theme_style_invalid(self, mock_logger):
        """Ungültiger Stil wird mit Warnung abgelehnt."""
        self.theme_manager.switch_theme_style('Invalid')

        self.mock_app.update_theme.assert_not_called()
        mock_logger.warning.assert_called_with("Ungültiger Theme-Stil: Invalid")

    @patch('manager.theme_manager.Logger')
    def test_switch_theme_style_ohne_app(self, mock_logger):
        """Ohne App wird eine Fehlermeldung geloggt."""
        self.theme_manager.app = None

        self.theme_manager.switch_theme_style('Dark')

        mock_logger.error.assert_called_with("App oder update_theme nicht verfügbar im ThemeManager")

    @patch('manager.theme_manager.Logger')
    def test_switch_theme_style_ohne_update_theme(self, mock_logger):
        """App ohne update_theme-Methode wird abgefangen."""
        del self.mock_app.update_theme

        self.theme_manager.switch_theme_style('Dark')

        mock_logger.error.assert_called_with("App oder update_theme nicht verfügbar im ThemeManager")

    @patch('manager.theme_manager.Logger')
    def test_switch_theme_style_exception(self, mock_logger):
        """Exception bei Theme-Wechsel wird geloggt."""
        self.mock_app.update_theme.side_effect = Exception("Update failed")

        self.theme_manager.switch_theme_style('Dark')

        mock_logger.error.assert_called_with("Fehler beim Theme-Stil-Wechsel im Manager: Update failed")

    # === on_color_selected ===

    @patch('manager.theme_manager.Logger')
    def test_on_color_selected_valid(self, mock_logger):
        """Gültige Farbe wird an app.update_theme übergeben."""
        self.theme_manager.on_color_selected('Blue')

        self.mock_app.update_theme.assert_called_once_with(primary_palette='Blue')
        mock_logger.info.assert_called_with("Primärfarbe über Manager gewechselt zu: Blue")

    @patch('manager.theme_manager.Logger')
    def test_on_color_selected_alle_gueltige_paletten(self, mock_logger):
        """Alle gültigen Paletten werden akzeptiert."""
        gueltige = [
            'Red', 'Pink', 'Purple', 'Deeprurple', 'Indigo', 'Blue',
            'Lightblue', 'Cyan', 'Teal', 'Green', 'Lightgreen', 'Lime',
            'Yellow', 'Amber', 'Orange', 'Deeporange', 'Brown',
            'Gray', 'Bluegray'
        ]
        for farbe in gueltige:
            self.mock_app.update_theme.reset_mock()
            self.theme_manager.on_color_selected(farbe)
            self.mock_app.update_theme.assert_called_once_with(primary_palette=farbe)

    @patch('manager.theme_manager.Logger')
    def test_on_color_selected_sendet_event(self, mock_logger):
        """Farbauswahl publiziert ein THEME_CHANGED Event."""
        from services.event_service import EventTypes
        self.theme_manager.on_color_selected('Red')

        self.mock_event_service.publish.assert_called_once_with(
            EventTypes.THEME_CHANGED, {'color': 'Red'}
        )

    @patch('manager.theme_manager.Logger')
    def test_on_color_selected_invalid_fallback_orange(self, mock_logger):
        """Ungültige Farbe fällt auf Orange zurück."""
        self.theme_manager.on_color_selected('InvalidColor')

        self.mock_app.update_theme.assert_called_once_with(primary_palette='Orange')
        mock_logger.warning.assert_called_with(
            "Ungültige Palette 'InvalidColor' im Manager, verwende Orange als Fallback"
        )

    @patch('manager.theme_manager.Logger')
    def test_on_color_selected_ohne_app(self, mock_logger):
        """Ohne App wird eine Fehlermeldung geloggt."""
        self.theme_manager.app = None

        self.theme_manager.on_color_selected('Blue')

        mock_logger.error.assert_called_with("App oder update_theme nicht verfügbar im ThemeManager")

    @patch('manager.theme_manager.Logger')
    def test_on_color_selected_exception(self, mock_logger):
        """Exception bei Farbauswahl wird geloggt."""
        self.mock_app.update_theme.side_effect = Exception("Color failed")

        self.theme_manager.on_color_selected('Blue')

        mock_logger.error.assert_called_with("Fehler beim Farb-Wechsel im Manager: Color failed")

    # === update_color_chips ===

    def test_update_color_chips(self):
        """update_color_chips delegiert an theme_service."""
        self.theme_manager.update_color_chips()

        self.mock_theme_service.create_color_chips.assert_called_once_with(
            self.mock_widget.ids.colors_box,
            self.theme_manager.on_color_selected
        )

    def test_update_color_chips_ohne_colors_box(self):
        """Ohne colors_box werden keine Chips erstellt."""
        del self.mock_widget.ids.colors_box

        self.theme_manager.update_color_chips()

        self.mock_theme_service.create_color_chips.assert_not_called()

    def test_update_color_chips_ohne_theme_service(self):
        """Ohne theme_service passiert nichts."""
        self.theme_manager.theme_service = None
        self.theme_manager.update_color_chips()
        # Kein Crash erwartet

    # === Ohne Event-Service ===

    @patch('manager.theme_manager.Logger')
    def test_switch_style_ohne_event_service(self, mock_logger):
        """Theme-Wechsel funktioniert auch ohne Event-Service."""
        self.theme_manager.event_service = None

        self.theme_manager.switch_theme_style('Dark')

        self.mock_app.update_theme.assert_called_once_with(theme_style='Dark')

    @patch('manager.theme_manager.Logger')
    def test_color_selected_ohne_event_service(self, mock_logger):
        """Farbauswahl funktioniert auch ohne Event-Service."""
        self.theme_manager.event_service = None

        self.theme_manager.on_color_selected('Blue')

        self.mock_app.update_theme.assert_called_once_with(primary_palette='Blue')


if __name__ == '__main__':
    unittest.main()
