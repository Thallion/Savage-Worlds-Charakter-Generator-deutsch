# test units/test_wizard_service.py
"""
Unit Tests für WizardService und WizardSchritt (services/wizard_service.py).
Testet Wizard-Zustandsverwaltung, Schritt-Navigation, Validierung und Events.
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Kivy-Headless-Modus
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_LOG_LEVEL'] = 'critical'

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWizardSchritt(unittest.TestCase):
    """Tests für die WizardSchritt-Klasse."""

    def setUp(self):
        with patch('kivy.logger.Logger'):
            from services.wizard_service import WizardSchritt
            self.WizardSchritt = WizardSchritt

    def test_init_basic(self):
        """Grundlegende Initialisierung eines WizardSchritts."""
        schritt = self.WizardSchritt(
            tab_id='test_tab',
            tab_name='Test Tab',
            title='Test Titel',
            description='Beschreibung'
        )
        self.assertEqual(schritt.tab_id, 'test_tab')
        self.assertEqual(schritt.tab_name, 'Test Tab')
        self.assertEqual(schritt.title, 'Test Titel')
        self.assertEqual(schritt.description, 'Beschreibung')
        self.assertEqual(schritt.popup_title, '')
        self.assertEqual(schritt.popup_text, '')
        self.assertTrue(schritt.is_required)

    def test_init_optional(self):
        """Optionaler Schritt."""
        schritt = self.WizardSchritt(
            tab_id='opt', tab_name='Opt', title='Optional',
            description='', is_required=False
        )
        self.assertFalse(schritt.is_required)

    def test_init_with_popup(self):
        """Schritt mit Popup-Text."""
        schritt = self.WizardSchritt(
            tab_id='t', tab_name='T', title='T', description='',
            popup_title='Hilfe', popup_text='Erklärung'
        )
        self.assertEqual(schritt.popup_title, 'Hilfe')
        self.assertEqual(schritt.popup_text, 'Erklärung')

    def test_validate_default_validator(self):
        """Standard-Validator gibt immer True zurück."""
        schritt = self.WizardSchritt(
            tab_id='t', tab_name='T', title='T', description=''
        )
        is_valid, error = schritt.validate(None)
        self.assertTrue(is_valid)
        self.assertEqual(error, '')

    def test_validate_custom_validator_success(self):
        """Benutzerdefinierter Validator - Erfolg."""
        schritt = self.WizardSchritt(
            tab_id='t', tab_name='T', title='T', description='',
            validator=lambda c: c is not None
        )
        is_valid, error = schritt.validate("charakter")
        self.assertTrue(is_valid)

    def test_validate_custom_validator_fail(self):
        """Benutzerdefinierter Validator - Fehlschlag."""
        schritt = self.WizardSchritt(
            tab_id='t', tab_name='T', title='T', description='',
            validator=lambda c: c is not None
        )
        is_valid, error = schritt.validate(None)
        self.assertFalse(is_valid)
        self.assertEqual(error, 'Validierung fehlgeschlagen')

    def test_validate_exception_handling(self):
        """Validator mit Exception wird abgefangen."""
        def bad_validator(c):
            raise ValueError("Test-Fehler")

        schritt = self.WizardSchritt(
            tab_id='t', tab_name='T', title='T', description='',
            validator=bad_validator
        )
        is_valid, error = schritt.validate(None)
        self.assertFalse(is_valid)
        self.assertIn('Test-Fehler', error)


class TestWizardService(unittest.TestCase):
    """Tests für die WizardService-Klasse."""

    def setUp(self):
        with patch('kivy.logger.Logger'):
            from services.wizard_service import WizardService
            self.service = WizardService(charakter_controller=None)

    def test_init(self):
        """Initialisierung mit Standard-Schritten."""
        self.assertFalse(self.service.aktiv)
        self.assertEqual(self.service.aktueller_schritt_index, 0)
        self.assertGreater(len(self.service.schritte), 0)

    def test_schritte_anzahl(self):
        """Es gibt 9 Standard-Schritte."""
        self.assertEqual(len(self.service.schritte), 9)

    def test_schritte_tab_ids(self):
        """Alle erwarteten Tab-IDs sind vorhanden."""
        tab_ids = [s.tab_id for s in self.service.schritte]
        expected = ['neuer_charakter', 'voelker', 'profil', 'eigenschaften',
                    'handicaps', 'talente', 'maechte', 'ausruestung', 'charakterbogen']
        self.assertEqual(tab_ids, expected)

    def test_starten(self):
        """Wizard starten."""
        self.service.starten()
        self.assertTrue(self.service.aktiv)
        self.assertEqual(self.service.aktueller_schritt_index, 0)

    def test_starten_doppelt_ignoriert(self):
        """Doppelter Start wird ignoriert."""
        self.service.starten()
        self.service.aktueller_schritt_index = 3
        self.service.starten()  # Sollte nichts ändern
        self.assertEqual(self.service.aktueller_schritt_index, 3)

    def test_beenden(self):
        """Wizard beenden."""
        self.service.starten()
        self.service.beenden()
        self.assertFalse(self.service.aktiv)
        self.assertEqual(self.service.aktueller_schritt_index, 0)

    def test_beenden_ohne_start(self):
        """Beenden ohne Start ist ok."""
        self.service.beenden()  # Kein Fehler
        self.assertFalse(self.service.aktiv)

    def test_abbrechen(self):
        """Wizard abbrechen."""
        self.service.starten()
        self.service.abbrechen()
        self.assertFalse(self.service.aktiv)

    def test_naechster_schritt(self):
        """Nächster Schritt."""
        self.service.starten()
        result = self.service.naechster_schritt()
        self.assertTrue(result)
        self.assertEqual(self.service.aktueller_schritt_index, 1)

    def test_naechster_schritt_mehrfach(self):
        """Mehrere Schritte vorwärts."""
        self.service.starten()
        for i in range(3):
            self.service.naechster_schritt()
        self.assertEqual(self.service.aktueller_schritt_index, 3)

    def test_naechster_schritt_am_ende_beendet(self):
        """Am letzten Schritt beendet naechster_schritt() den Wizard."""
        self.service.starten()
        self.service.aktueller_schritt_index = len(self.service.schritte) - 1
        result = self.service.naechster_schritt()
        self.assertFalse(result)
        self.assertFalse(self.service.aktiv)

    def test_naechster_schritt_ohne_start(self):
        """Nächster Schritt ohne Start gibt False."""
        result = self.service.naechster_schritt()
        self.assertFalse(result)

    def test_vorheriger_schritt(self):
        """Vorheriger Schritt."""
        self.service.starten()
        self.service.naechster_schritt()
        self.service.naechster_schritt()
        result = self.service.vorheriger_schritt()
        self.assertTrue(result)
        self.assertEqual(self.service.aktueller_schritt_index, 1)

    def test_vorheriger_schritt_am_anfang(self):
        """Am Anfang gibt vorheriger_schritt() False."""
        self.service.starten()
        result = self.service.vorheriger_schritt()
        self.assertFalse(result)
        self.assertEqual(self.service.aktueller_schritt_index, 0)

    def test_vorheriger_schritt_ohne_start(self):
        """Vorheriger Schritt ohne Start gibt False."""
        result = self.service.vorheriger_schritt()
        self.assertFalse(result)

    def test_gehe_zu_schritt(self):
        """Zu bestimmtem Schritt navigieren."""
        self.service.starten()
        result = self.service.gehe_zu_schritt(5)
        self.assertTrue(result)
        self.assertEqual(self.service.aktueller_schritt_index, 5)

    def test_gehe_zu_schritt_ungueltig_negativ(self):
        """Negativer Index gibt False."""
        self.service.starten()
        result = self.service.gehe_zu_schritt(-1)
        self.assertFalse(result)

    def test_gehe_zu_schritt_ungueltig_zu_gross(self):
        """Index über Maximum gibt False."""
        self.service.starten()
        result = self.service.gehe_zu_schritt(100)
        self.assertFalse(result)

    def test_gehe_zu_schritt_ohne_start(self):
        """Ohne Start gibt False."""
        result = self.service.gehe_zu_schritt(3)
        self.assertFalse(result)

    def test_get_aktueller_schritt(self):
        """Aktuellen Schritt abrufen."""
        self.service.starten()
        schritt = self.service.get_aktueller_schritt()
        self.assertIsNotNone(schritt)
        self.assertEqual(schritt.tab_id, 'neuer_charakter')

    def test_get_aktueller_schritt_nach_navigation(self):
        """Schritt nach Navigation."""
        self.service.starten()
        self.service.naechster_schritt()
        schritt = self.service.get_aktueller_schritt()
        self.assertEqual(schritt.tab_id, 'voelker')

    def test_get_fortschritt(self):
        """Fortschritt als Tuple."""
        self.service.starten()
        current, total = self.service.get_fortschritt()
        self.assertEqual(current, 0)
        self.assertEqual(total, 9)

    def test_get_fortschritt_prozent(self):
        """Fortschritt in Prozent."""
        self.service.starten()
        self.assertEqual(self.service.get_fortschritt_prozent(), 0.0)

        self.service.aktueller_schritt_index = len(self.service.schritte) - 1
        self.assertEqual(self.service.get_fortschritt_prozent(), 100.0)

    def test_get_fortschritt_prozent_mitte(self):
        """Fortschritt in der Mitte."""
        self.service.starten()
        self.service.aktueller_schritt_index = 4
        prozent = self.service.get_fortschritt_prozent()
        self.assertGreater(prozent, 0)
        self.assertLess(prozent, 100)

    def test_ist_erster_schritt(self):
        """Erster Schritt prüfen."""
        self.service.starten()
        self.assertTrue(self.service.ist_erster_schritt())
        self.service.naechster_schritt()
        self.assertFalse(self.service.ist_erster_schritt())

    def test_ist_letzter_schritt(self):
        """Letzter Schritt prüfen."""
        self.service.starten()
        self.assertFalse(self.service.ist_letzter_schritt())
        self.service.aktueller_schritt_index = len(self.service.schritte) - 1
        self.assertTrue(self.service.ist_letzter_schritt())

    def test_schritt_ueberspringen_optional(self):
        """Optionalen Schritt überspringen."""
        self.service.starten()
        # Profil (Index 2) ist optional
        self.service.gehe_zu_schritt(2)
        result = self.service.schritt_ueberspringen()
        self.assertTrue(result)
        self.assertEqual(self.service.aktueller_schritt_index, 3)

    def test_schritt_ueberspringen_erforderlich(self):
        """Erforderlichen Schritt kann man nicht überspringen."""
        self.service.starten()
        # neuer_charakter (Index 0) ist erforderlich
        result = self.service.schritt_ueberspringen()
        self.assertFalse(result)
        self.assertEqual(self.service.aktueller_schritt_index, 0)

    def test_schritt_ueberspringen_ohne_start(self):
        """Überspringen ohne Start gibt False."""
        result = self.service.schritt_ueberspringen()
        self.assertFalse(result)

    def test_bind_event(self):
        """Event binden und auslösen."""
        callback = Mock()
        self.service.bind_event('on_wizard_started', callback)
        self.service.starten()
        callback.assert_called_once()

    def test_unbind_event(self):
        """Event entbinden."""
        callback = Mock()
        self.service.bind_event('on_wizard_started', callback)
        self.service.unbind_event('on_wizard_started', callback)
        self.service.starten()
        callback.assert_not_called()

    def test_event_on_step_changed(self):
        """on_step_changed Event wird bei Navigation ausgelöst."""
        callback = Mock()
        self.service.bind_event('on_step_changed', callback)
        self.service.starten()
        self.service.naechster_schritt()
        callback.assert_called_once()

    def test_event_on_wizard_finished(self):
        """on_wizard_finished Event bei Beenden."""
        callback = Mock()
        self.service.bind_event('on_wizard_finished', callback)
        self.service.starten()
        self.service.beenden()
        callback.assert_called_once()

    def test_event_on_wizard_cancelled(self):
        """on_wizard_cancelled Event bei Abbrechen."""
        callback = Mock()
        self.service.bind_event('on_wizard_cancelled', callback)
        self.service.starten()
        self.service.abbrechen()
        callback.assert_called_once()

    def test_bind_ungueltige_event_ignoriert(self):
        """Unbekanntes Event beim Binden ignorieren."""
        callback = Mock()
        self.service.bind_event('on_unknown', callback)
        # Kein Fehler, Callback wird einfach nicht registriert

    def test_validate_neuer_charakter_kein_charakter(self):
        """Validierung ohne Charakter schlägt fehl."""
        result = self.service._validate_neuer_charakter(None)
        self.assertFalse(result)

    def test_validate_neuer_charakter_mit_daten(self):
        """Validierung mit Name und Setting gelingt."""
        mock_char = Mock()
        mock_char.char_name = "Testhold"
        mock_char.active_setting_name = "SWAE"
        result = self.service._validate_neuer_charakter(mock_char)
        self.assertTrue(result)

    def test_validate_neuer_charakter_ohne_name(self):
        """Validierung ohne Name schlägt fehl."""
        mock_char = Mock()
        mock_char.char_name = ""
        mock_char.name = ""
        mock_char.active_setting_name = "SWAE"
        result = self.service._validate_neuer_charakter(mock_char)
        self.assertFalse(result)

    def test_validate_volk(self):
        """Volk-Validierung."""
        mock_char = Mock()
        mock_char.volk = "Mensch"
        self.assertTrue(self.service._validate_volk(mock_char))

        mock_char.volk = None
        self.assertFalse(self.service._validate_volk(mock_char))

    def test_validate_volk_kein_charakter(self):
        """Volk-Validierung ohne Charakter."""
        self.assertFalse(self.service._validate_volk(None))

    def test_get_charakter_ohne_controller(self):
        """_get_charakter ohne Controller gibt None."""
        result = self.service._get_charakter()
        self.assertIsNone(result)

    def test_get_charakter_mit_controller(self):
        """_get_charakter mit Controller gibt Charakter."""
        mock_controller = Mock()
        mock_controller.charakter = "test_charakter"
        self.service.charakter_controller = mock_controller
        result = self.service._get_charakter()
        self.assertEqual(result, "test_charakter")


if __name__ == '__main__':
    unittest.main()
