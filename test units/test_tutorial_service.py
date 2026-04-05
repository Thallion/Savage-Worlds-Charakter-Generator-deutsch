# test units/test_tutorial_service.py
"""
Unit Tests für TutorialService und TabHintManager (services/tutorial_service.py).
Testet Tutorial-Konfiguration, Tab-Hints, Willkommens-Tutorial und Zustandsverwaltung.
"""

import unittest
import sys
import os
import json
import tempfile
from unittest.mock import Mock, patch
from pathlib import Path

# Kivy-Headless-Modus
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_LOG_LEVEL'] = 'critical'

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTutorialService(unittest.TestCase):
    """Tests für die TutorialService-Klasse."""

    def _create_service_with_config(self, config_data=None):
        """Erstellt einen TutorialService mit benutzerdefinierter Config."""
        with patch('kivy.logger.Logger'):
            from services.tutorial_service import TutorialService
            service = TutorialService.__new__(TutorialService)
            service.config_service = None
            service._tab_hints_shown = {}
            service._welcome_completed = False
            service._tutorial_config_path = None

            if config_data is not None:
                service._config = config_data
            else:
                service._config = self._get_test_config()
            return service

    def _get_test_config(self):
        """Standard-Testkonfiguration."""
        return {
            "tab_hints": {
                "voelker": {"title": "Volk", "text": "Wähle ein Volk"},
                "profil": {"title": "Profil", "text": "Name eingeben"},
                "eigenschaften": {"title": "Attribute", "text": "Punkte verteilen"},
            },
            "welcome_tutorial": {
                "steps": [
                    {"title": "Willkommen", "text": "Erste Schritte"},
                    {"title": "Navigation", "text": "So navigierst du"},
                ]
            }
        }

    def test_get_tab_hint_existiert(self):
        """Tab-Hint für vorhandenen Tab abrufen."""
        service = self._create_service_with_config()
        hint = service.get_tab_hint('voelker')
        self.assertIsNotNone(hint)
        self.assertEqual(hint['title'], 'Volk')
        self.assertEqual(hint['text'], 'Wähle ein Volk')

    def test_get_tab_hint_nicht_vorhanden(self):
        """Tab-Hint für unbekannten Tab gibt None."""
        service = self._create_service_with_config()
        hint = service.get_tab_hint('unbekannt')
        self.assertIsNone(hint)

    def test_get_tab_hint_ohne_config(self):
        """Tab-Hint ohne Config gibt None."""
        service = self._create_service_with_config()
        service._config = None
        hint = service.get_tab_hint('voelker')
        self.assertIsNone(hint)

    def test_get_all_tab_ids(self):
        """Alle Tab-IDs abrufen."""
        service = self._create_service_with_config()
        tab_ids = service.get_all_tab_ids()
        self.assertIn('voelker', tab_ids)
        self.assertIn('profil', tab_ids)
        self.assertIn('eigenschaften', tab_ids)
        self.assertEqual(len(tab_ids), 3)

    def test_get_all_tab_ids_ohne_config(self):
        """Alle Tab-IDs ohne Config gibt leere Liste."""
        service = self._create_service_with_config()
        service._config = None
        self.assertEqual(service.get_all_tab_ids(), [])

    def test_has_tab_hint_been_shown_default(self):
        """Tab-Hint ist standardmäßig nicht angezeigt."""
        service = self._create_service_with_config()
        self.assertFalse(service.has_tab_hint_been_shown('voelker'))

    def test_mark_tab_hint_as_shown(self):
        """Tab-Hint als angezeigt markieren."""
        service = self._create_service_with_config()
        service.mark_tab_hint_as_shown('voelker')
        self.assertTrue(service.has_tab_hint_been_shown('voelker'))

    def test_mark_mehrere_hints_als_gezeigt(self):
        """Mehrere Hints unabhängig markieren."""
        service = self._create_service_with_config()
        service.mark_tab_hint_as_shown('voelker')
        service.mark_tab_hint_as_shown('profil')
        self.assertTrue(service.has_tab_hint_been_shown('voelker'))
        self.assertTrue(service.has_tab_hint_been_shown('profil'))
        self.assertFalse(service.has_tab_hint_been_shown('eigenschaften'))

    def test_reset_all_tab_hints(self):
        """Alle Tab-Hints zurücksetzen."""
        service = self._create_service_with_config()
        service.mark_tab_hint_as_shown('voelker')
        service.mark_tab_hint_as_shown('profil')
        service.reset_all_tab_hints()
        self.assertFalse(service.has_tab_hint_been_shown('voelker'))
        self.assertFalse(service.has_tab_hint_been_shown('profil'))

    def test_welcome_completed_default(self):
        """Willkommen ist standardmäßig nicht abgeschlossen."""
        service = self._create_service_with_config()
        self.assertFalse(service.is_welcome_completed())

    def test_mark_welcome_completed(self):
        """Willkommen als abgeschlossen markieren."""
        service = self._create_service_with_config()
        service.mark_welcome_completed()
        self.assertTrue(service.is_welcome_completed())

    def test_reset_welcome(self):
        """Willkommen zurücksetzen."""
        service = self._create_service_with_config()
        service.mark_welcome_completed()
        service.reset_welcome()
        self.assertFalse(service.is_welcome_completed())

    def test_should_show_welcome(self):
        """should_show_welcome basiert auf Completed-Status."""
        service = self._create_service_with_config()
        self.assertTrue(service.should_show_welcome())
        service.mark_welcome_completed()
        self.assertFalse(service.should_show_welcome())

    def test_get_welcome_steps(self):
        """Willkommens-Tutorial-Schritte abrufen."""
        service = self._create_service_with_config()
        steps = service.get_welcome_steps()
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0]['title'], 'Willkommen')
        self.assertEqual(steps[1]['title'], 'Navigation')

    def test_get_welcome_steps_ohne_config(self):
        """Willkommens-Schritte ohne Config gibt leere Liste."""
        service = self._create_service_with_config()
        service._config = None
        self.assertEqual(service.get_welcome_steps(), [])

    def test_load_state(self):
        """Tutorial-Zustand laden."""
        service = self._create_service_with_config()
        state = {
            "welcome_completed": True,
            "tab_hints_shown": {"voelker": True, "profil": False}
        }
        service.load_state(state)
        self.assertTrue(service.is_welcome_completed())
        self.assertTrue(service.has_tab_hint_been_shown('voelker'))
        self.assertFalse(service.has_tab_hint_been_shown('profil'))

    def test_load_state_none(self):
        """Leerer State wird ignoriert."""
        service = self._create_service_with_config()
        service.load_state(None)  # Kein Fehler
        self.assertFalse(service.is_welcome_completed())

    def test_load_state_ergaenzt_fehlende_tabs(self):
        """Fehlende Tab-IDs werden beim Laden ergänzt."""
        service = self._create_service_with_config()
        state = {
            "welcome_completed": False,
            "tab_hints_shown": {"voelker": True}
            # profil und eigenschaften fehlen
        }
        service.load_state(state)
        # Fehlende Tabs werden als nicht gezeigt ergänzt
        self.assertFalse(service.has_tab_hint_been_shown('profil'))
        self.assertFalse(service.has_tab_hint_been_shown('eigenschaften'))

    def test_get_next_unshown_tab_hint(self):
        """Nächsten ungezeigten Hint abrufen."""
        service = self._create_service_with_config()
        result = service.get_next_unshown_tab_hint()
        self.assertIsNotNone(result)
        tab_id, hint = result
        self.assertIn(tab_id, ['voelker', 'profil', 'eigenschaften'])

    def test_get_next_unshown_tab_hint_alle_gezeigt(self):
        """Wenn alle Hints gezeigt wurden, gibt None zurück."""
        service = self._create_service_with_config()
        for tab_id in service.get_all_tab_ids():
            service.mark_tab_hint_as_shown(tab_id)
        result = service.get_next_unshown_tab_hint()
        self.assertIsNone(result)

    def test_show_next_hint_if_available(self):
        """Nächsten verfügbaren Hint anzeigen."""
        service = self._create_service_with_config()
        result = service.show_next_hint_if_available()
        self.assertTrue(result)

    def test_show_next_hint_alle_gezeigt(self):
        """Kein Hint mehr verfügbar."""
        service = self._create_service_with_config()
        for tab_id in service.get_all_tab_ids():
            service.mark_tab_hint_as_shown(tab_id)
        result = service.show_next_hint_if_available()
        self.assertFalse(result)

    def test_save_state_mit_config_service(self):
        """Zustand wird über Config-Service gespeichert."""
        service = self._create_service_with_config()
        mock_config = Mock()
        service.config_service = mock_config
        service.mark_welcome_completed()
        mock_config.set.assert_called()
        mock_config.save_config.assert_called()

    def test_default_config(self):
        """Standard-Config bei fehlender Datei."""
        service = self._create_service_with_config()
        default = service._get_default_config()
        self.assertIn('tab_hints', default)
        self.assertIn('welcome_tutorial', default)


class TestTabHintManager(unittest.TestCase):
    """Tests für die TabHintManager-Klasse."""

    def setUp(self):
        with patch('kivy.logger.Logger'):
            from services.tutorial_service import TutorialService, TabHintManager
            self.service = TutorialService.__new__(TutorialService)
            self.service.config_service = None
            self.service._tab_hints_shown = {}
            self.service._welcome_completed = False
            self.service._tutorial_config_path = None
            self.service._config = {
                "tab_hints": {
                    "voelker": {"title": "Volk", "text": "Test"},
                    "profil": {"title": "Profil", "text": "Test"},
                },
                "welcome_tutorial": {"steps": []}
            }
            self.manager = TabHintManager(self.service)

    def test_check_and_show_hint_erstmalig(self):
        """Hint wird beim ersten Mal angezeigt."""
        result = self.manager.check_and_show_hint_for_tab('voelker')
        self.assertTrue(result)

    def test_check_and_show_hint_bereits_gezeigt(self):
        """Hint wird nicht erneut angezeigt."""
        self.service.mark_tab_hint_as_shown('voelker')
        result = self.manager.check_and_show_hint_for_tab('voelker')
        self.assertFalse(result)

    def test_check_and_show_hint_unbekannter_tab(self):
        """Unbekannter Tab gibt False."""
        result = self.manager.check_and_show_hint_for_tab('unbekannt')
        self.assertFalse(result)

    def test_show_hint_manually(self):
        """Manuellen Hint anzeigen (unabhängig vom Status)."""
        self.service.mark_tab_hint_as_shown('voelker')
        result = self.manager.show_hint_manually('voelker')
        self.assertTrue(result)

    def test_show_hint_manually_unbekannt(self):
        """Manueller Hint für unbekannten Tab gibt False."""
        result = self.manager.show_hint_manually('unbekannt')
        self.assertFalse(result)

    def test_show_all_hints(self):
        """Alle verfügbaren Hints auflisten."""
        shown = self.manager.show_all_hints()
        self.assertIn('voelker', shown)
        self.assertIn('profil', shown)
        self.assertEqual(len(shown), 2)


class TestTutorialServiceMitDatei(unittest.TestCase):
    """Tests für TutorialService mit echter Config-Datei."""

    def test_load_config_von_datei(self):
        """Config aus JSON-Datei laden."""
        config_data = {
            "tab_hints": {"test": {"title": "T", "text": "X"}},
            "welcome_tutorial": {"steps": [{"title": "Hi", "text": "Hallo"}]}
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            with patch('kivy.logger.Logger'):
                from services.tutorial_service import TutorialService
                service = TutorialService.__new__(TutorialService)
                service.config_service = None
                service._tab_hints_shown = {}
                service._welcome_completed = False
                service._tutorial_config_path = Path(config_path)
                service._config = None
                service._load_config()

                self.assertIsNotNone(service._config)
                self.assertIn('test', service.get_all_tab_ids())
                steps = service.get_welcome_steps()
                self.assertEqual(len(steps), 1)
                self.assertEqual(steps[0]['title'], 'Hi')
        finally:
            os.unlink(config_path)

    def test_load_config_fehlende_datei(self):
        """Fehlende Config-Datei erzeugt Default-Config."""
        with patch('kivy.logger.Logger'):
            from services.tutorial_service import TutorialService
            service = TutorialService.__new__(TutorialService)
            service.config_service = None
            service._tab_hints_shown = {}
            service._welcome_completed = False
            service._tutorial_config_path = Path("/nicht/existent/config.json")
            service._config = None
            service._load_config()

            self.assertIsNotNone(service._config)
            self.assertEqual(service.get_all_tab_ids(), [])


if __name__ == '__main__':
    unittest.main()
