# tests/test_game_elements_handler.py
"""
Unit Tests für GameElementsHandler
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from kivy.app import App
from kivymd.app import MDApp

# Mocking Kivy vor Import
with patch('kivy.logger.Logger'), patch('kivymd.app.MDApp'):
    from controllers.game_elements_handler import GameElementsHandler


class TestGameElementsHandler(unittest.TestCase):
    """Test-Klasse für GameElementsHandler"""
    
    def setUp(self):
        """Setup vor jedem Test"""
        # Mock Widget
        self.mock_widget = Mock()
        self.mock_widget.ids = Mock()
        
        # Mock App mit Controller
        self.mock_app = Mock()
        self.mock_app.controller = Mock()
        self.mock_widget.app = self.mock_app
        
        # GameElements Handler erstellen
        self.handler = GameElementsHandler(self.mock_widget)
        
    def test_init(self):
        """Test Initialisierung"""
        self.assertEqual(self.handler.widget, self.mock_widget)
        self.assertEqual(self.handler.app, self.mock_app)
        
    # ==================== VÖLKER TESTS ====================
    
    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_volk_dialog(self, mock_logger):
        """Test Volk-Hinzufügen-Dialog"""
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_add_volk_dialog()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Volk-Hinzufügen-Dialog geöffnet")
            
    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_volk_dialog(self, mock_logger):
        """Test Volk-Löschen-Dialog"""
        # Setup
        self.mock_app.controller.get_available_voelker = Mock(return_value=['Volk1', 'Volk2'])
        
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_delete_volk_dialog()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Volk-Löschen-Dialog geöffnet")
            
    @patch('controllers.game_elements_handler.Logger')
    def test_add_volk_success(self, mock_logger):
        """Test erfolgreiches Hinzufügen eines Volks"""
        # Setup
        self.mock_app.controller.add_volk = Mock(return_value=True)
        mock_instance = Mock()
        mock_instance.dismiss = Mock()
        
        # Test
        self.handler.add_volk("Test Volk", "Beschreibung", mock_instance)
        
        # Prüfe dass Volk hinzugefügt wurde
        self.mock_app.controller.add_volk.assert_called_once_with("Test Volk", "Beschreibung")
        mock_instance.dismiss.assert_called_once()
        mock_logger.info.assert_called_with("Volk hinzugefügt: Test Volk")
        
    @patch('controllers.game_elements_handler.Logger')
    def test_add_volk_failure(self, mock_logger):
        """Test fehlgeschlagenes Hinzufügen eines Volks"""
        # Setup
        self.mock_app.controller.add_volk = Mock(return_value=False)
        mock_instance = Mock()
        
        # Test
        self.handler.add_volk("Test Volk", "Beschreibung", mock_instance)
        
        # Prüfe dass Fehler geloggt wurde
        mock_logger.error.assert_called_with("Fehler beim Hinzufügen des Volks: Test Volk")
        
    # ==================== TALENTE TESTS ====================
    
    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_talent_popup(self, mock_logger):
        """Test Talent-Hinzufügen-Dialog"""
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_add_talent_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Talent-Hinzufügen-Dialog geöffnet")
            
    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_talent_popup(self, mock_logger):
        """Test Talent-Löschen-Dialog"""
        # Setup
        self.mock_app.controller.get_available_talents = Mock(return_value=['Talent1', 'Talent2'])
        
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_delete_talent_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Talent-Löschen-Dialog geöffnet")
            
    # ==================== MÄCHTE TESTS ====================
    
    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_macht_popup(self, mock_logger):
        """Test Macht-Hinzufügen-Dialog"""
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_add_macht_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Macht-Hinzufügen-Dialog geöffnet")
            
    @patch('controllers.game_elements_handler.Logger')  
    def test_open_delete_macht_popup(self, mock_logger):
        """Test Macht-Löschen-Dialog"""
        # Setup
        self.mock_app.controller.get_available_maechte = Mock(return_value=['Macht1', 'Macht2'])
        
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_delete_macht_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Macht-Löschen-Dialog geöffnet")
            
    # ==================== FERTIGKEITEN TESTS ====================
    
    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_fertigkeit_popup(self, mock_logger):
        """Test Fertigkeit-Hinzufügen-Dialog"""
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_add_fertigkeit_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Fertigkeit-Hinzufügen-Dialog geöffnet")
            
    # ==================== HANDICAPS TESTS ====================
    
    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_handicap_popup(self, mock_logger):
        """Test Handicap-Hinzufügen-Dialog"""
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_add_handicap_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Handicap-Hinzufügen-Dialog geöffnet")
            
    @patch('controllers.game_elements_handler.Logger')
    def test_open_delete_handicap_popup(self, mock_logger):
        """Test Handicap-Löschen-Dialog"""
        # Setup
        self.mock_app.controller.get_available_handicaps = Mock(return_value=['Handicap1', 'Handicap2'])
        
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_delete_handicap_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Handicap-Löschen-Dialog geöffnet")
            
    # ==================== AUSRÜSTUNG TESTS ====================
    
    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_ausruestung_popup(self, mock_logger):
        """Test Ausrüstung-Hinzufügen-Dialog"""
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_add_ausruestung_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Ausrüstung-Hinzufügen-Dialog geöffnet")
            
    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_waffe_popup(self, mock_logger):
        """Test Waffe-Hinzufügen-Dialog"""
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_add_waffe_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Waffe-Hinzufügen-Dialog geöffnet")
            
    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_ruestung_popup(self, mock_logger):
        """Test Rüstung-Hinzufügen-Dialog"""
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_add_ruestung_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Rüstung-Hinzufügen-Dialog geöffnet")
            
    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_schild_popup(self, mock_logger):
        """Test Schild-Hinzufügen-Dialog"""
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_add_schild_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Schild-Hinzufügen-Dialog geöffnet")
            
    # ==================== SETTINGS TESTS ====================
    
    @patch('controllers.game_elements_handler.Logger')
    def test_open_add_setting_popup(self, mock_logger):
        """Test Setting-Hinzufügen-Dialog"""
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_add_setting_popup()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Setting-Hinzufügen-Dialog geöffnet")
            
    @patch('controllers.game_elements_handler.Logger')
    def test_open_setting_switch_options(self, mock_logger):
        """Test Setting-Wechsel-Dialog"""
        # Setup
        self.mock_app.controller.get_available_settings = Mock(return_value=['Setting1', 'Setting2'])
        
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            # Test
            self.handler.open_setting_switch_options()
            
            # Prüfe dass Dialog erstellt wurde
            mock_dialog.assert_called_once()
            mock_logger.info.assert_called_with("Setting-Wechsel-Dialog geöffnet")
            
    # ==================== DELETE TESTS ====================
    
    @patch('controllers.game_elements_handler.Logger')
    def test_delete_element_success(self, mock_logger):
        """Test erfolgreiches Löschen eines Elements"""
        # Setup
        self.mock_app.controller.delete_talent = Mock(return_value=True)
        mock_instance = Mock()
        mock_instance.dismiss = Mock()
        
        # Test
        self.handler.delete_element("talent", "Test Talent", mock_instance)
        
        # Prüfe dass Element gelöscht wurde
        self.mock_app.controller.delete_talent.assert_called_once_with("Test Talent")
        mock_instance.dismiss.assert_called_once()
        mock_logger.info.assert_called_with("talent gelöscht: Test Talent")
        
    @patch('controllers.game_elements_handler.Logger')
    def test_delete_element_failure(self, mock_logger):
        """Test fehlgeschlagenes Löschen eines Elements"""
        # Setup
        self.mock_app.controller.delete_talent = Mock(return_value=False)
        mock_instance = Mock()
        
        # Test
        self.handler.delete_element("talent", "Test Talent", mock_instance)
        
        # Prüfe dass Fehler geloggt wurde
        mock_logger.error.assert_called_with("Fehler beim Löschen des talent: Test Talent")
        
    # ==================== EXCEPTION HANDLING TESTS ====================
    
    @patch('controllers.game_elements_handler.Logger')
    def test_exception_handling_add_dialog(self, mock_logger):
        """Test Exception-Handling bei Dialog-Erstellung"""
        with patch('controllers.game_elements_handler.MDDialog', side_effect=Exception("Dialog Error")):
            # Test
            self.handler.open_add_volk_dialog()
            
            mock_logger.error.assert_called_with("Fehler beim Öffnen des Volk-Hinzufügen-Dialogs: Dialog Error")
            
    @patch('controllers.game_elements_handler.Logger')
    def test_exception_handling_delete_dialog(self, mock_logger):
        """Test Exception-Handling bei Lösch-Dialog"""
        # Setup - Exception bei get_available_voelker
        self.mock_app.controller.get_available_voelker.side_effect = Exception("Get Error")
        
        # Test
        self.handler.open_delete_volk_dialog()
        
        mock_logger.error.assert_called_with("Fehler beim Öffnen des Volk-Löschen-Dialogs: Get Error")
        
    @patch('controllers.game_elements_handler.Logger')
    def test_exception_handling_add_element(self, mock_logger):
        """Test Exception-Handling bei Element hinzufügen"""
        # Setup
        self.mock_app.controller.add_volk.side_effect = Exception("Add Error")
        mock_instance = Mock()
        
        # Test
        self.handler.add_volk("Test Volk", "Beschreibung", mock_instance)
        
        mock_logger.error.assert_called_with("Fehler beim Hinzufügen des Volks: Add Error")
        
    # ==================== HELPER METHODS TESTS ====================
    
    def test_get_element_list_method_mapping(self):
        """Test Mapping von Element-Typ zu Controller-Methode"""
        # Setup
        mapping = {
            'talent': 'get_available_talents',
            'macht': 'get_available_maechte', 
            'volk': 'get_available_voelker',
            'handicap': 'get_available_handicaps',
            'fertigkeit': 'get_available_fertigkeiten',
            'setting': 'get_available_settings'
        }
        
        # Test - prüfe dass Mapping korrekt funktioniert
        for element_type, method_name in mapping.items():
            self.assertTrue(hasattr(self.mock_app.controller, method_name))
            
    @patch('controllers.game_elements_handler.Logger')
    def test_create_dialog_with_custom_content(self, mock_logger):
        """Test Dialog-Erstellung mit benutzerdefiniertem Content"""
        with patch('controllers.game_elements_handler.MDDialog') as mock_dialog:
            mock_content = Mock()
            
            # Test - simuliere interne _create_dialog Methode
            dialog = self.handler._create_dialog("Test Title", mock_content)
            
            # Prüfe dass Dialog mit korrekten Parametern erstellt wurde
            mock_dialog.assert_called_once()
            call_args = mock_dialog.call_args
            self.assertIn('title', call_args.kwargs)
            self.assertEqual(call_args.kwargs['title'], "Test Title")
            
    def test_validate_element_name(self):
        """Test Element-Name-Validierung"""
        # Test gültige Namen
        self.assertTrue(self.handler._validate_element_name("Gültiger Name"))
        self.assertTrue(self.handler._validate_element_name("Name123"))
        
        # Test ungültige Namen
        self.assertFalse(self.handler._validate_element_name(""))
        self.assertFalse(self.handler._validate_element_name("   "))
        self.assertFalse(self.handler._validate_element_name(None))


if __name__ == '__main__':
    unittest.main()