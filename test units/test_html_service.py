"""
Tests für HTML-Service (services/html_service.py)
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import Mock, MagicMock, patch

# Mocking für Kivy/KivyMD
sys.modules['kivy'] = MagicMock()
sys.modules['kivy.app'] = MagicMock()
sys.modules['kivy.logger'] = MagicMock()
sys.modules['kivy.clock'] = MagicMock()
sys.modules['kivy.lang'] = MagicMock()
sys.modules['kivy.metrics'] = MagicMock()
sys.modules['kivy.properties'] = MagicMock()
sys.modules['kivy.event'] = MagicMock()
sys.modules['kivy.uix'] = MagicMock()
sys.modules['kivy.uix.boxlayout'] = MagicMock()
sys.modules['kivymd'] = MagicMock()
sys.modules['kivymd.app'] = MagicMock()
sys.modules['kivymd.uix'] = MagicMock()
sys.modules['kivymd.uix.boxlayout'] = MagicMock()
sys.modules['kivymd.uix.label'] = MagicMock()
sys.modules['kivymd.uix.button'] = MagicMock()
sys.modules['kivymd.uix.dialog'] = MagicMock()
sys.modules['kivymd.uix.selectioncontrol'] = MagicMock()

# Projektverzeichnis zum Pfad hinzufügen
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TestHTMLService(unittest.TestCase):
    """Tests für den HTML-Service"""

    def setUp(self):
        self.controller = Mock()
        self.controller.charakter = Mock()
        self.controller.charakter.char_name = "Testcharakter"
        self.controller.current_character_file_path = "/tmp/chars/Testcharakter.json"

        from services.html_service import HTMLService
        self.service = HTMLService(self.controller)

    def test_is_html_supported_immer_true(self):
        """HTML-Export ist immer verfügbar"""
        self.assertTrue(self.service.is_html_supported())

    def test_get_default_html_name_from_file_path(self):
        """Testet HTML-Namen aus vorhandenem Dateipfad"""
        result = self.service.get_default_html_name()
        self.assertEqual(result, "Testcharakter.html")

    def test_get_default_html_name_from_char_name(self):
        """Testet HTML-Namen aus Charakternamen"""
        self.controller.current_character_file_path = None
        result = self.service.get_default_html_name()
        self.assertEqual(result, "Testcharakter.html")

    def test_get_default_html_name_fallback(self):
        """Testet Fallback-HTML-Name"""
        self.controller.current_character_file_path = None
        self.controller.charakter.char_name = ""
        result = self.service.get_default_html_name()
        self.assertEqual(result, "charakter.html")

    def test_check_existing_html_not_exists(self):
        """Testet Prüfung auf nicht existierende HTML"""
        exists, path, name = self.service.check_existing_html()
        self.assertFalse(exists)
        self.assertEqual(name, "Testcharakter.html")

    def test_check_existing_html_no_file_path(self):
        """Testet Prüfung ohne Dateipfad"""
        self.controller.current_character_file_path = None
        exists, path, name = self.service.check_existing_html()
        self.assertFalse(exists)
        self.assertEqual(path, "")
        self.assertEqual(name, "")

    @patch('services.html_service.generiere_html', return_value=True)
    def test_create_character_html_erfolg(self, mock_generiere):
        """Testet erfolgreiche HTML-Erstellung"""
        result = self.service.create_character_html("/tmp/test.html")
        self.assertTrue(result)
        mock_generiere.assert_called_once_with(
            self.controller.charakter, "/tmp/test.html", False
        )

    @patch('services.html_service.generiere_html', return_value=True)
    def test_create_character_html_printer_friendly(self, mock_generiere):
        """Testet HTML-Erstellung mit druckerfreundlich"""
        result = self.service.create_character_html("/tmp/test.html", printer_friendly=True)
        self.assertTrue(result)
        mock_generiere.assert_called_once_with(
            self.controller.charakter, "/tmp/test.html", True
        )

    @patch('services.html_service.generiere_html', return_value=False)
    def test_create_character_html_fehler(self, mock_generiere):
        """Testet Fehlerfall bei HTML-Erstellung"""
        result = self.service.create_character_html("/tmp/test.html")
        self.assertFalse(result)

    @patch('services.html_service.generiere_html', side_effect=Exception("Testfehler"))
    def test_create_character_html_exception(self, mock_generiere):
        """Testet Exception-Handling bei HTML-Erstellung"""
        result = self.service.create_character_html("/tmp/test.html")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
