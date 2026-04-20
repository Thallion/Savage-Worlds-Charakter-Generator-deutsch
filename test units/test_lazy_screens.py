#!/usr/bin/env python3
"""
Unit Tests für Lazy-Screen-Instanziierung (main.py).

Tests zu Plan-Schritt 2 der Android-Performance-Optimierung:
- _screen_name_for_tab erzeugt konsistente Screen-Namen.
- _instantiate_screen erzeugt den Screen einmal und ist idempotent.
- _instantiate_screen legt Widget-Registrierung und Screen-Dict an.
- _instantiate_screen liefert bestehende Screens aus dem ScreenManager zurück.
- _instantiate_screen gibt bei ungültigem Index (None, None) zurück.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Projektwurzel in den Pfad aufnehmen
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test setzt eine Kivy-Installation voraus (wird ansonsten übersprungen)
try:  # pragma: no cover - reine Umgebungsabfrage
    import kivy  # noqa: F401
    import kivymd  # noqa: F401
    _KIVY_AVAILABLE = True
except Exception:
    _KIVY_AVAILABLE = False

# KivyMD Chip-Modul hat einen Metaclass-Konflikt beim Import — präventiv mocken
if _KIVY_AVAILABLE:
    for _mod in ['kivymd.uix.chip', 'kivymd.uix.chip.chip']:
        if _mod not in sys.modules:
            sys.modules[_mod] = MagicMock()


class _FakeScreen:
    """Minimaler Ersatz für MDScreen — hat .name und nimmt jeden Kwarg."""
    def __init__(self, *args, **kwargs):
        self.name = None


class _ScreenClassA(_FakeScreen):
    pass


class _ScreenClassB(_FakeScreen):
    pass


class _FakeScreenManager:
    """Mini-ScreenManager — trackt add_widget-Aufrufe und kennt screen_names."""
    def __init__(self):
        self._screens = {}
        self.add_widget_calls = 0

    @property
    def screen_names(self):
        return list(self._screens.keys())

    def add_widget(self, screen):
        self.add_widget_calls += 1
        self._screens[screen.name] = screen

    def get_screen(self, name):
        return self._screens[name]


@unittest.skipUnless(_KIVY_AVAILABLE, "Kivy/KivyMD nicht verfügbar")
class TestLazyScreens(unittest.TestCase):
    """Testet die Lazy-Screen-Erzeugung in SW_Charakter_GeneratorApp."""

    @classmethod
    def setUpClass(cls):
        # Builder.load_file patchen, damit der main-Import keine .kv-Dateien lädt
        with patch('kivy.lang.Builder.load_file'):
            import main
            cls.AppClass = main.SW_Charakter_GeneratorApp

    def _make_dummy(self):
        """Erzeugt ein Self-Ersatzobjekt mit den vom Verfahren genutzten Attributen."""
        dummy = MagicMock()
        dummy.tab_definitions = [
            ("icon-a", "Speichern/Laden", _ScreenClassA),
            ("icon-b", "Einstellungen", _ScreenClassB),
            ("icon-c", "Völker", _ScreenClassA),
        ]
        dummy.screens = {}
        dummy.screen_instances = []
        # _register_widget_for_compatibility darf kein echter Seiteneffekt sein
        dummy._register_widget_for_compatibility = MagicMock()
        # _screen_name_for_tab ist reine Logik und soll die echte Implementierung nutzen
        dummy._screen_name_for_tab = lambda idx: self.AppClass._screen_name_for_tab(dummy, idx)
        return dummy

    # ---------- _screen_name_for_tab ----------

    def test_screen_name_for_tab_standard(self):
        dummy = self._make_dummy()
        name = self.AppClass._screen_name_for_tab(dummy, 0)
        self.assertEqual(name, "screen_0_speichern/laden")

    def test_screen_name_for_tab_replaces_umlauts_and_space(self):
        dummy = self._make_dummy()
        name = self.AppClass._screen_name_for_tab(dummy, 2)
        # 'Völker' → 'voelker'
        self.assertEqual(name, "screen_2_voelker")

    def test_screen_name_for_tab_invalid_index(self):
        dummy = self._make_dummy()
        self.assertIsNone(self.AppClass._screen_name_for_tab(dummy, -1))
        self.assertIsNone(self.AppClass._screen_name_for_tab(dummy, 99))

    # ---------- _instantiate_screen ----------

    def test_instantiate_screen_creates_once(self):
        dummy = self._make_dummy()
        sm = _FakeScreenManager()

        screen, name = self.AppClass._instantiate_screen(dummy, 1, sm)

        self.assertIsNotNone(screen)
        self.assertIsInstance(screen, _ScreenClassB)
        self.assertEqual(name, "screen_1_einstellungen")
        self.assertEqual(sm.add_widget_calls, 1)
        self.assertIn("Einstellungen", dummy.screens)
        self.assertIn(screen, dummy.screen_instances)
        dummy._register_widget_for_compatibility.assert_called_once_with(
            screen, "Einstellungen"
        )

    def test_instantiate_screen_is_idempotent(self):
        """Zweiter Aufruf mit gleichem Index erzeugt KEINEN neuen Screen."""
        dummy = self._make_dummy()
        sm = _FakeScreenManager()

        screen_a, _ = self.AppClass._instantiate_screen(dummy, 0, sm)
        screen_b, _ = self.AppClass._instantiate_screen(dummy, 0, sm)

        self.assertIs(screen_a, screen_b)
        self.assertEqual(sm.add_widget_calls, 1, "add_widget darf nur einmal gerufen werden")
        self.assertEqual(len(dummy.screen_instances), 1)

    def test_instantiate_screen_recovers_from_orphaned_screen(self):
        """Screen existiert im ScreenManager, aber nicht im dict → wird adoptiert."""
        dummy = self._make_dummy()
        sm = _FakeScreenManager()

        orphan = _ScreenClassA()
        orphan.name = "screen_0_speichern/laden"
        sm.add_widget(orphan)
        sm.add_widget_calls = 0  # Reset: Orphan-Add war Setup

        screen, name = self.AppClass._instantiate_screen(dummy, 0, sm)

        self.assertIs(screen, orphan, "Bestehender Screen wird wiederverwendet, nicht neu erzeugt")
        self.assertEqual(sm.add_widget_calls, 0, "Kein zweites add_widget bei Recovery")
        self.assertIn("Speichern/Laden", dummy.screens)

    def test_instantiate_screen_invalid_index_returns_none(self):
        dummy = self._make_dummy()
        sm = _FakeScreenManager()

        s1, n1 = self.AppClass._instantiate_screen(dummy, -1, sm)
        s2, n2 = self.AppClass._instantiate_screen(dummy, 99, sm)

        self.assertEqual((s1, n1), (None, None))
        self.assertEqual((s2, n2), (None, None))
        self.assertEqual(sm.add_widget_calls, 0)

    def test_instantiate_screen_none_manager_returns_none(self):
        dummy = self._make_dummy()
        s, n = self.AppClass._instantiate_screen(dummy, 0, None)
        self.assertEqual((s, n), (None, None))

    def test_instantiate_different_indices_creates_different_screens(self):
        dummy = self._make_dummy()
        sm = _FakeScreenManager()

        s0, _ = self.AppClass._instantiate_screen(dummy, 0, sm)
        s1, _ = self.AppClass._instantiate_screen(dummy, 1, sm)

        self.assertIsNot(s0, s1)
        self.assertEqual(sm.add_widget_calls, 2)
        self.assertEqual(len(dummy.screens), 2)


if __name__ == "__main__":
    unittest.main()
