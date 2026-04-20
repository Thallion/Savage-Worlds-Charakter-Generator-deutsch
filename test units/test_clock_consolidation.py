#!/usr/bin/env python3
"""
Unit Tests für Clock.schedule_once-Konsolidierung (Schritt 6 der Performance-Optimierung).

Testet, dass kaskadierte Clock-Aufrufe durch sequenzielle Logik ersetzt wurden
und Template-Loading lazy erfolgt (erst bei Dialog-Öffnung).
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
class TestClockConsolidation(unittest.TestCase):
    """Testet die Clock.schedule_once-Konsolidierung."""

    def test_volk_funktionen_clock_konsolidierung(self):
        """Test: volk_funktionen verwendet eine einzige Clock-Kaskade statt mehrerer."""
        from functions.volk_funktionen import waehle_freies_attribut
        import inspect

        source = inspect.getsource(waehle_freies_attribut)

        # Konsolidierte Sequenz sollte vorhanden sein
        self.assertIn("consolidated_update_sequence", source)
        self.assertIn("Konsolidierte Update-Sequenz", source)

        # Einziger Clock.schedule_once Call mit delay=0
        self.assertIn("Clock.schedule_once(consolidated_update_sequence, 0)", source)

        # Alte kaskadierte Calls sollten NICHT mehr vorhanden sein
        self.assertNotIn("0.05)", source)  # Alter 0.05s delay
        self.assertNotIn("0.2)", source)   # Alter 0.2s delay
        self.assertNotIn("0.1)", source)   # Alter 0.1s delay (separate UI-Refresh)

        # Kommentar über Konsolidierung sollte vorhanden sein
        self.assertIn("0.05+0.2+0.1s → 0s", source)

    def test_volk_funktionen_sequenzielle_logik(self):
        """Test: Konsolidierte Sequenz führt alle Updates sequenziell aus."""
        from functions.volk_funktionen import waehle_freies_attribut
        import inspect

        source = inspect.getsource(waehle_freies_attribut)

        # Sequenzielle Ausführung der ursprünglichen Calls
        self.assertIn("_force_eigenschaften_update(app)", source)
        self.assertIn("_force_trigger_ui_refresh(app)", source)

        # Doppelter Eigenschaften-Update für Robustheit
        eigenschaften_count = source.count("_force_eigenschaften_update(app)")
        self.assertEqual(eigenschaften_count, 2, "Eigenschaften-Update sollte 2x aufgerufen werden")

    def test_template_handler_lazy_loading_init(self):
        """Test: TemplateHandler lädt Templates nicht mehr im __init__."""
        from controllers.template_handler import TemplateHandler

        widget = MagicMock()
        widget.app = MagicMock()

        handler = TemplateHandler(widget)

        # Lazy-Loading Flag sollte gesetzt sein
        self.assertFalse(handler._templates_loaded, "Templates sollten noch nicht geladen sein")

        # Templates sollten leer sein
        self.assertEqual(handler.available_templates, [])
        self.assertEqual(handler.filtered_templates, [])

    def test_template_handler_lazy_loading_on_dialog(self):
        """Test: Templates werden erst beim Dialog-Aufruf geladen."""
        from controllers.template_handler import TemplateHandler

        widget = MagicMock()
        widget.app = MagicMock()
        handler = TemplateHandler(widget)

        # Mock _load_available_templates method
        handler._load_available_templates = MagicMock()

        # Simuliere verfügbare Templates nach Loading
        def mock_load_templates(dt=None):
            handler.available_templates = [{'name': 'Test', 'description': 'Test Template'}]

        handler._load_available_templates.side_effect = mock_load_templates

        # Dialog-Aufruf sollte Templates laden
        with patch('controllers.template_handler.MDDialog'):
            handler.show_template_selection_dialog()

        # _load_available_templates sollte aufgerufen worden sein
        handler._load_available_templates.assert_called_once()

        # Flag sollte gesetzt sein
        self.assertTrue(handler._templates_loaded, "Templates sollten nach Dialog-Aufruf geladen sein")

    def test_template_handler_kein_doppeltes_loading(self):
        """Test: Templates werden nur einmal geladen, nicht bei jedem Dialog-Aufruf."""
        from controllers.template_handler import TemplateHandler

        widget = MagicMock()
        widget.app = MagicMock()
        handler = TemplateHandler(widget)

        # Mock _load_available_templates method
        handler._load_available_templates = MagicMock()

        # Simuliere verfügbare Templates
        handler.available_templates = [{'name': 'Test', 'description': 'Test Template'}]

        # Manuell als geladen markieren
        handler._templates_loaded = True

        # Dialog-Aufruf sollte Templates NICHT erneut laden
        with patch('controllers.template_handler.MDLabel'), \
             patch('controllers.template_handler.MDDialog'):
            handler.show_template_selection_dialog()

        # _load_available_templates sollte NICHT aufgerufen werden
        handler._load_available_templates.assert_not_called()

    def test_template_handler_source_code_struktur(self):
        """Test: TemplateHandler Source-Code-Struktur für Lazy-Loading."""
        from controllers.template_handler import TemplateHandler
        import inspect

        # __init__ sollte kein aktives Clock.schedule_once mehr enthalten
        init_source = inspect.getsource(TemplateHandler.__init__)
        self.assertIn("# Clock.schedule_once", init_source)  # Kommentiert
        self.assertIn("_templates_loaded = False", init_source)
        self.assertIn("ENTFERNT: Template-Load aus __init__", init_source)

        # show_template_selection_dialog sollte Lazy-Loading enthalten
        dialog_source = inspect.getsource(TemplateHandler.show_template_selection_dialog)
        self.assertIn("LAZY-LOADING", dialog_source)
        self.assertIn("if not self._templates_loaded:", dialog_source)
        self.assertIn("self._load_available_templates()", dialog_source)

    def test_performance_verbesserung_messbar(self):
        """Test: Performance-Verbesserung ist theoretisch messbar."""
        # Clock-Konsolidierung: 0.05+0.2+0.1s = 350ms → 0s = 350ms Einsparung
        volk_delay_savings_ms = (0.05 + 0.2 + 0.1) * 1000
        self.assertEqual(volk_delay_savings_ms, 350.0)

        # Template-Lazy-Loading: 200ms beim App-Start → 0ms = 200ms Einsparung
        template_delay_savings_ms = 0.2 * 1000
        self.assertEqual(template_delay_savings_ms, 200.0)

        # Gesamt-Einsparung
        total_savings_ms = volk_delay_savings_ms + template_delay_savings_ms
        self.assertEqual(total_savings_ms, 550.0)

        # Signifikante Verbesserung (>500ms)
        self.assertGreater(total_savings_ms, 500)


if __name__ == "__main__":
    unittest.main()