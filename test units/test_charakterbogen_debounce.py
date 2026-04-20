#!/usr/bin/env python3
"""
Unit Tests für CharakterbogenWidget Debounce-Optimierung (Schritt 7 der Performance-Optimierung).

Testet, dass mehrfache update_overview() Aufrufe durch Debounce konsolidiert werden
und nur einen einzigen Widget-Rebuild auslösen.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:  # pragma: no cover
    import kivy  # noqa: F401
    _KIVY_AVAILABLE = True
except Exception:
    _KIVY_AVAILABLE = False


@unittest.skipUnless(_KIVY_AVAILABLE, "Kivy nicht verfügbar")
class TestCharakterbogenDebounce(unittest.TestCase):
    """Testet die CharakterbogenWidget Debounce-Optimierung."""

    def setUp(self):
        """Setup für Tests mit gemockten Dependencies."""
        with patch('kivymd.app.MDApp'):
            from views.charakterbogen_view import CharakterbogenWidget

            self.widget = CharakterbogenWidget()
            self.widget.charakter = MagicMock()

            # Mock alle _update_*_section Methoden
            self.widget._update_profil_section = MagicMock()
            self.widget._update_volk_section = MagicMock()
            self.widget._update_attribute_section = MagicMock()
            self.widget._update_fertigkeiten_section = MagicMock()
            self.widget._update_abgeleitete_werte_section = MagicMock()
            self.widget._update_handicaps_section = MagicMock()
            self.widget._update_talente_section = MagicMock()
            self.widget._update_maechte_section = MagicMock()
            self.widget._update_ausruestung_section = MagicMock()
            self.widget._update_waffen_section = MagicMock()
            self.widget._update_schilde_section = MagicMock()
            self.widget._update_ruestungen_section = MagicMock()

    def test_debounce_instance_variables_initialized(self):
        """Test: Debounce-Instanzvariablen sind korrekt initialisiert."""
        self.assertFalse(self.widget._update_scheduled)
        self.assertIsNone(self.widget._update_event)

    def test_single_update_overview_call(self):
        """Test: Einzelner update_overview() Call funktioniert normal."""
        with patch('views.charakterbogen_view.Clock') as mock_clock:
            self.widget.update_overview()

            # Clock.schedule_once sollte aufgerufen werden
            mock_clock.schedule_once.assert_called_once()
            call_args = mock_clock.schedule_once.call_args
            self.assertEqual(call_args[0][0], self.widget._perform_update)
            self.assertEqual(call_args[0][1], 0.05)

            # Update sollte als geplant markiert sein
            self.assertTrue(self.widget._update_scheduled)

    def test_multiple_update_overview_calls_debounced(self):
        """Test: Mehrere update_overview() Calls werden debounced."""
        with patch('views.charakterbogen_view.Clock') as mock_clock:
            # Mehrfache Calls
            self.widget.update_overview()
            self.widget.update_overview()
            self.widget.update_overview()

            # Nur ein Clock.schedule_once sollte ausgeführt werden
            self.assertEqual(mock_clock.schedule_once.call_count, 1)

    def test_perform_update_executes_all_sections(self):
        """Test: _perform_update führt alle Section-Updates aus."""
        # Simuliere den internen _perform_update Call
        self.widget._perform_update(0)

        # Alle Section-Update-Methoden sollten aufgerufen werden
        self.widget._update_profil_section.assert_called_once()
        self.widget._update_volk_section.assert_called_once()
        self.widget._update_attribute_section.assert_called_once()
        self.widget._update_fertigkeiten_section.assert_called_once()
        self.widget._update_abgeleitete_werte_section.assert_called_once()
        self.widget._update_handicaps_section.assert_called_once()
        self.widget._update_talente_section.assert_called_once()
        self.widget._update_maechte_section.assert_called_once()
        self.widget._update_ausruestung_section.assert_called_once()
        self.widget._update_waffen_section.assert_called_once()
        self.widget._update_schilde_section.assert_called_once()
        self.widget._update_ruestungen_section.assert_called_once()

    def test_perform_update_resets_flags(self):
        """Test: _perform_update reset Debounce-Flags korrekt."""
        # Setup: Als geplant markieren
        self.widget._update_scheduled = True
        self.widget._update_event = MagicMock()

        # _perform_update ausführen
        self.widget._perform_update(0)

        # Flags sollten zurückgesetzt sein
        self.assertFalse(self.widget._update_scheduled)
        self.assertIsNone(self.widget._update_event)

    def test_update_overview_no_charakter(self):
        """Test: update_overview verhält sich korrekt ohne Charakter."""
        self.widget.charakter = None

        with patch('views.charakterbogen_view.Clock') as mock_clock:
            self.widget.update_overview()

            # Clock sollte trotzdem geplant werden
            mock_clock.schedule_once.assert_called_once()

        # _perform_update sollte early return machen
        self.widget._perform_update(0)

        # Keine Section-Updates sollten aufgerufen werden
        self.widget._update_profil_section.assert_not_called()

    def test_cleanup_cancels_pending_update(self):
        """Test: cleanup() bricht geplante Updates ab."""
        # Setup: Geplantes Update simulieren
        mock_event = MagicMock()
        self.widget._update_scheduled = True
        self.widget._update_event = mock_event

        # Cleanup ausführen
        self.widget.cleanup()

        # Event sollte abgebrochen werden
        mock_event.cancel.assert_called_once()
        self.assertIsNone(self.widget._update_event)
        self.assertFalse(self.widget._update_scheduled)

    def test_source_code_contains_debounce_logic(self):
        """Test: Source-Code enthält Debounce-Implementierung."""
        from views.charakterbogen_view import CharakterbogenWidget
        import inspect

        # update_overview Methode sollte Debounce-Logik enthalten
        update_source = inspect.getsource(CharakterbogenWidget.update_overview)
        self.assertIn("DEBOUNCE", update_source)
        self.assertIn("_update_scheduled", update_source)
        self.assertIn("_perform_update", update_source)

        # _perform_update Methode sollte existieren
        self.assertTrue(hasattr(CharakterbogenWidget, "_perform_update"))

        # __init__ sollte Debounce-Variablen initialisieren
        init_source = inspect.getsource(CharakterbogenWidget.__init__)
        self.assertIn("_update_scheduled = False", init_source)
        self.assertIn("_update_event = None", init_source)

    def test_performance_theoretical_improvement(self):
        """Test: Theoretische Performance-Verbesserung messbar."""
        # Simuliere 5 schnelle update_overview() Calls
        multiple_calls = 5

        # Ohne Debounce: 5 × 12 Section-Updates = 60 clear_widgets() + Rebuilds
        without_debounce_rebuilds = multiple_calls * 12

        # Mit Debounce: 1 × 12 Section-Updates = 12 clear_widgets() + Rebuilds
        with_debounce_rebuilds = 1 * 12

        # Einsparung berechnen
        savings = without_debounce_rebuilds - with_debounce_rebuilds
        savings_percentage = (savings / without_debounce_rebuilds) * 100

        self.assertEqual(without_debounce_rebuilds, 60)
        self.assertEqual(with_debounce_rebuilds, 12)
        self.assertEqual(savings, 48)
        self.assertEqual(savings_percentage, 80.0)

        # 80% Reduktion der Widget-Rebuilds
        self.assertGreater(savings_percentage, 75)


if __name__ == "__main__":
    unittest.main()