# tests/test_theme_handler.py
"""
Unit Tests für ThemeHandler
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from kivy.app import App
from kivymd.app import MDApp

# Mocking Kivy vor Import
with patch('kivy.logger.Logger'), patch('kivymd.app.MDApp'):
    from views.handlers.theme_handler import ThemeHandler


class TestThemeHandler(unittest.TestCase):
    """Test-Klasse für ThemeHandler"""
    
    def setUp(self):
        """Setup vor jedem Test"""
        # Mock Widget
        self.mock_widget = Mock()
        self.mock_widget.ids = Mock()
        self.mock_widget.ids.colors_box = Mock()
        
        # Mock App
        self.mock_app = Mock()
        self.mock_widget.app = self.mock_app
        
        # Mock Theme Manager
        self.mock_theme_manager = Mock()
        self.mock_widget.theme_manager = self.mock_theme_manager
        
        # Theme Handler erstellen
        self.theme_handler = ThemeHandler(self.mock_widget)
        
    def test_init(self):
        """Test Initialisierung"""
        self.assertEqual(self.theme_handler.widget, self.mock_widget)
        self.assertEqual(self.theme_handler.app, self.mock_app)
        self.assertIsNotNone(self.theme_handler.theme_service)
        
    @patch('views.handlers.theme_handler.Logger')
    def test_initialize_theme_success(self, mock_logger):
        """Test erfolgreiche Theme-Initialisierung"""
        self.theme_handler.initialize_theme()
        
        # Prüfe dass Theme-Service initialisiert wurde
        self.theme_handler.theme_service.initialize_theme.assert_called_once()
        
        # Prüfe dass Farb-Chips erstellt wurden
        self.theme_handler.theme_service.create_color_chips.assert_called_once()
        
        mock_logger.info.assert_called_with("Theme-Handler initialisiert")
        
    @patch('views.handlers.theme_handler.Logger')
    def test_initialize_theme_no_colors_box(self, mock_logger):
        """Test Theme-Initialisierung ohne colors_box"""
        # Entferne colors_box
        delattr(self.mock_widget.ids, 'colors_box')
        
        self.theme_handler.initialize_theme()
        
        # Theme-Service sollte trotzdem initialisiert werden
        self.theme_handler.theme_service.initialize_theme.assert_called_once()
        
        mock_logger.info.assert_called_with("Theme-Handler initialisiert")
        
    @patch('views.handlers.theme_handler.Logger')
    def test_switch_theme_style_with_manager(self, mock_logger):
        """Test Theme-Stil-Wechsel mit ThemeManager"""
        # Manager ist verfügbar
        hasattr_mock = Mock(side_effect=lambda obj, attr: True)
        with patch('builtins.hasattr', hasattr_mock):
            self.theme_handler.switch_theme_style('Dark')
            
        self.mock_theme_manager.switch_theme_style.assert_called_once_with('Dark')
        mock_logger.info.assert_called_with("Theme-Stil-Wechsel angefordert: Dark")
        
    @patch('views.handlers.theme_handler.Logger')
    def test_switch_theme_style_without_manager(self, mock_logger):
        """Test Theme-Stil-Wechsel ohne ThemeManager"""
        # Manager nicht verfügbar
        self.mock_widget.theme_manager = None
        
        # Mock App update_theme
        self.mock_app.update_theme = Mock()
        hasattr_mock = Mock(side_effect=lambda obj, attr: obj == self.mock_app and attr == 'update_theme')
        
        with patch('builtins.hasattr', hasattr_mock):
            self.theme_handler.switch_theme_style('Light')
            
        self.mock_app.update_theme.assert_called_once_with(theme_style='Light')
        mock_logger.info.assert_called_with("Theme-Stil gewechselt zu: Light")
        
    @patch('views.handlers.theme_handler.Logger')
    def test_switch_theme_style_invalid(self, mock_logger):
        """Test ungültiger Theme-Stil"""
        self.mock_widget.theme_manager = None
        self.mock_app.update_theme = Mock()
        hasattr_mock = Mock(side_effect=lambda obj, attr: obj == self.mock_app and attr == 'update_theme')
        
        with patch('builtins.hasattr', hasattr_mock):
            self.theme_handler.switch_theme_style('Invalid')
            
        # update_theme sollte nicht aufgerufen werden
        self.mock_app.update_theme.assert_not_called()
        mock_logger.warning.assert_called_with("Ungültiger Theme-Stil 'Invalid' ignoriert")
        
    @patch('views.handlers.theme_handler.Logger')
    def test_on_color_selected_with_manager(self, mock_logger):
        """Test Farbauswahl mit ThemeManager"""
        hasattr_mock = Mock(side_effect=lambda obj, attr: True)
        with patch('builtins.hasattr', hasattr_mock):
            self.theme_handler.on_color_selected('Blue')
            
        self.mock_theme_manager.on_color_selected.assert_called_once_with('Blue')
        mock_logger.info.assert_called_with("Farb-Wechsel angefordert: Blue")
        
    @patch('views.handlers.theme_handler.Logger')
    def test_on_color_selected_without_manager_valid(self, mock_logger):
        """Test Farbauswahl ohne ThemeManager - gültige Farbe"""
        self.mock_widget.theme_manager = None
        self.mock_app.update_theme = Mock()
        hasattr_mock = Mock(side_effect=lambda obj, attr: obj == self.mock_app and attr == 'update_theme')
        
        with patch('builtins.hasattr', hasattr_mock):
            self.theme_handler.on_color_selected('Red')
            
        self.mock_app.update_theme.assert_called_once_with(primary_palette='Red')
        mock_logger.info.assert_called_with("Primärfarbe gewechselt zu: Red")
        
    @patch('views.handlers.theme_handler.Logger')
    def test_on_color_selected_without_manager_invalid(self, mock_logger):
        """Test Farbauswahl ohne ThemeManager - ungültige Farbe"""
        self.mock_widget.theme_manager = None
        self.mock_app.update_theme = Mock()
        hasattr_mock = Mock(side_effect=lambda obj, attr: obj == self.mock_app and attr == 'update_theme')
        
        with patch('builtins.hasattr', hasattr_mock):
            self.theme_handler.on_color_selected('InvalidColor')
            
        # Sollte auf Orange fallback
        self.mock_app.update_theme.assert_called_once_with(primary_palette='Orange')
        mock_logger.warning.assert_called_with(
            "Ungültige Palette 'InvalidColor' ignoriert. Verwende 'Orange' als Fallback."
        )
        
    @patch('views.handlers.theme_handler.Logger')
    def test_on_theme_changed_with_manager(self, mock_logger):
        """Test Theme-Changed Event mit ThemeManager"""
        test_data = {"theme": "Dark", "color": "Blue"}
        hasattr_mock = Mock(side_effect=lambda obj, attr: True)
        
        with patch('builtins.hasattr', hasattr_mock):
            self.theme_handler.on_theme_changed(test_data)
            
        self.mock_theme_manager.update_color_chips.assert_called_once()
        mock_logger.info.assert_called_with(f"Theme geändert: {test_data}")
        
    @patch('views.handlers.theme_handler.Logger')
    def test_on_theme_changed_without_manager(self, mock_logger):
        """Test Theme-Changed Event ohne ThemeManager"""
        self.mock_widget.theme_manager = None
        test_data = {"theme": "Light", "color": "Green"}
        
        hasattr_mock = Mock(side_effect=lambda obj, attr: attr == 'colors_box')
        with patch('builtins.hasattr', hasattr_mock):
            self.theme_handler.on_theme_changed(test_data)
            
        # Sollte theme_service.update_color_chips aufrufen
        self.theme_handler.theme_service.update_color_chips.assert_called_once()
        mock_logger.info.assert_called_with(f"Theme geändert: {test_data}")
        
    @patch('views.handlers.theme_handler.Logger')
    def test_exception_handling_initialize(self, mock_logger):
        """Test Exception-Handling bei Initialisierung"""
        # Fehler beim theme_service.initialize_theme simulieren
        self.theme_handler.theme_service.initialize_theme.side_effect = Exception("Test Error")
        
        self.theme_handler.initialize_theme()
        
        mock_logger.error.assert_called_with("Fehler bei Theme-Initialisierung: Test Error")
        
    @patch('views.handlers.theme_handler.Logger')
    def test_exception_handling_switch_style(self, mock_logger):
        """Test Exception-Handling bei Theme-Stil-Wechsel"""
        # Exception simulieren
        self.mock_theme_manager.switch_theme_style.side_effect = Exception("Test Error")
        hasattr_mock = Mock(side_effect=lambda obj, attr: True)
        
        with patch('builtins.hasattr', hasattr_mock):
            self.theme_handler.switch_theme_style('Dark')
            
        mock_logger.error.assert_called_with("Fehler beim Theme-Stil-Wechsel: Test Error")
        
    @patch('views.handlers.theme_handler.Logger')
    def test_exception_handling_color_selected(self, mock_logger):
        """Test Exception-Handling bei Farbauswahl"""
        # Exception simulieren
        self.mock_theme_manager.on_color_selected.side_effect = Exception("Test Error")
        hasattr_mock = Mock(side_effect=lambda obj, attr: True)
        
        with patch('builtins.hasattr', hasattr_mock):
            self.theme_handler.on_color_selected('Blue')
            
        mock_logger.error.assert_called_with("Fehler beim Farb-Wechsel: Test Error")


if __name__ == '__main__':
    unittest.main()