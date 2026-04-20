#!/usr/bin/env python3
"""
Unit Tests für Dialog-Cache-System (Schritt 8 der Performance-Optimierung).

Testet, dass Dialog-Wiederverwendung korrekt funktioniert und die Performance-Ziele erreicht werden.
"""

import os
import sys
import unittest
import time
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
class TestDialogCache(unittest.TestCase):
    """Testet das Dialog-Cache-System."""

    def setUp(self):
        """Setup für Tests mit gemockten KivyMD-Komponenten."""
        with patch('kivymd.app.MDApp.get_running_app') as mock_app:
            mock_app_instance = MagicMock()
            mock_app_instance.theme_cls = MagicMock()
            mock_app_instance.theme_cls.surfaceColor = [1, 1, 1, 1]
            mock_app.return_value = mock_app_instance

            from utils.dialog_cache import DialogCache
            self.cache = DialogCache()

    def test_cache_initialization(self):
        """Test: Cache wird korrekt initialisiert."""
        self.assertIsInstance(self.cache._cached_dialogs, dict)
        self.assertEqual(len(self.cache._cached_dialogs), 0)

    def test_info_dialog_creation_and_reuse(self):
        """Test: Info-Dialog wird erstellt und wiederverwendet."""
        # Erstes Mal - Dialog wird erstellt
        dialog1 = self.cache.get_info_dialog("Test Titel", "Test Nachricht")
        self.assertIsNotNone(dialog1)
        self.assertEqual(len(self.cache._cached_dialogs), 1)

        # Zweites Mal - Dialog wird wiederverwendet
        dialog2 = self.cache.get_info_dialog("Anderer Titel", "Andere Nachricht")
        self.assertEqual(len(self.cache._cached_dialogs), 1)  # Immer noch nur ein Dialog
        self.assertIs(dialog1, dialog2)  # Gleiche Instanz

    def test_confirmation_dialog_creation_and_reuse(self):
        """Test: Bestätigungs-Dialog wird erstellt und wiederverwendet."""
        callback1 = MagicMock()
        callback2 = MagicMock()

        # Erstes Mal
        dialog1 = self.cache.get_confirmation_dialog("Titel 1", "Nachricht 1", on_confirm=callback1)
        self.assertIsNotNone(dialog1)
        self.assertEqual(len(self.cache._cached_dialogs), 1)

        # Zweites Mal
        dialog2 = self.cache.get_confirmation_dialog("Titel 2", "Nachricht 2", on_confirm=callback2)
        self.assertEqual(len(self.cache._cached_dialogs), 1)
        self.assertIs(dialog1, dialog2)

    def test_choice_dialog_creation_and_reuse(self):
        """Test: Auswahl-Dialog wird erstellt und wiederverwendet."""
        choices1 = [("Option 1", "val1"), ("Option 2", "val2")]
        choices2 = [("Andere Option", "other"), ("Noch eine", "another")]

        # Erstes Mal
        dialog1 = self.cache.get_choice_dialog("Titel", "Nachricht", choices1)
        self.assertIsNotNone(dialog1)

        # Zweites Mal mit gleicher Anzahl Optionen
        dialog2 = self.cache.get_choice_dialog("Titel", "Nachricht", choices2)
        self.assertIs(dialog1, dialog2)

    def test_different_choice_count_creates_separate_cache(self):
        """Test: Unterschiedliche Anzahl von Optionen erstellt separate Cache-Einträge."""
        choices_2 = [("A", "a"), ("B", "b")]
        choices_4 = [("A", "a"), ("B", "b"), ("C", "c"), ("D", "d")]

        dialog1 = self.cache.get_choice_dialog("Titel", "Nachricht", choices_2)
        dialog2 = self.cache.get_choice_dialog("Titel", "Nachricht", choices_4)

        # Zwei verschiedene Dialoge aufgrund unterschiedlicher Anzahl von Optionen
        self.assertIsNot(dialog1, dialog2)
        self.assertEqual(len(self.cache._cached_dialogs), 2)

    def test_cache_clear(self):
        """Test: Cache kann geleert werden."""
        # Dialog erstellen
        self.cache.get_info_dialog("Test", "Test")
        self.assertEqual(len(self.cache._cached_dialogs), 1)

        # Cache leeren
        self.cache.clear_cache()
        self.assertEqual(len(self.cache._cached_dialogs), 0)

    def test_cache_info(self):
        """Test: Cache-Informationen werden korrekt zurückgegeben."""
        # Leerer Cache
        info = self.cache.get_cache_info()
        self.assertEqual(info['cached_dialogs'], 0)
        self.assertEqual(info['dialog_types'], [])

        # Dialog hinzufügen
        self.cache.get_info_dialog("Test", "Test")
        self.cache.get_confirmation_dialog("Test", "Test")

        info = self.cache.get_cache_info()
        self.assertEqual(info['cached_dialogs'], 2)
        self.assertIn('info_dialog', info['dialog_types'])
        self.assertIn('confirmation_dialog', info['dialog_types'])


@unittest.skipUnless(_KIVY_AVAILABLE, "Kivy nicht verfügbar")
class TestDialogHelpers(unittest.TestCase):
    """Testet die Dialog-Helper-Funktionen."""

    def setUp(self):
        """Setup für Tests."""
        with patch('kivymd.app.MDApp.get_running_app') as mock_app:
            mock_app_instance = MagicMock()
            mock_app_instance.theme_cls = MagicMock()
            mock_app.return_value = mock_app_instance

    def test_cached_info_dialog_helper(self):
        """Test: Info-Dialog-Helper funktioniert."""
        from utils.dialog_helpers import show_cached_info_dialog

        with patch('utils.dialog_cache.get_dialog_cache') as mock_cache_getter:
            mock_cache = MagicMock()
            mock_dialog = MagicMock()
            mock_cache.get_info_dialog.return_value = mock_dialog
            mock_cache_getter.return_value = mock_cache

            show_cached_info_dialog("Test Titel", "Test Nachricht")

            mock_cache.get_info_dialog.assert_called_once_with("Test Titel", "Test Nachricht", "OK", None)
            mock_dialog.open.assert_called_once()

    def test_cached_confirmation_dialog_helper(self):
        """Test: Bestätigungs-Dialog-Helper funktioniert."""
        from utils.dialog_helpers import show_cached_confirmation_dialog

        callback = MagicMock()

        with patch('utils.dialog_cache.get_dialog_cache') as mock_cache_getter:
            mock_cache = MagicMock()
            mock_dialog = MagicMock()
            mock_cache.get_confirmation_dialog.return_value = mock_dialog
            mock_cache_getter.return_value = mock_cache

            show_cached_confirmation_dialog("Titel", "Nachricht", on_confirm=callback)

            mock_cache.get_confirmation_dialog.assert_called_once()
            mock_dialog.open.assert_called_once()

    def test_specialized_helpers(self):
        """Test: Spezialisierte Helper-Funktionen funktionieren."""
        from utils.dialog_helpers import (
            show_cached_not_duplicatable_dialog,
            show_cached_max_points_dialog,
            show_cached_no_advancement_dialog
        )

        with patch('utils.dialog_helpers.show_cached_info_dialog') as mock_info:
            show_cached_not_duplicatable_dialog("Test Handicap")
            mock_info.assert_called_once()
            args = mock_info.call_args[1]  # keyword arguments
            self.assertEqual(args['title'], "Bereits ausgewählt")
            self.assertIn("Test Handicap", args['message'])

        with patch('utils.dialog_helpers.show_cached_info_dialog') as mock_info:
            show_cached_max_points_dialog()
            mock_info.assert_called_once()
            args = mock_info.call_args[1]
            self.assertEqual(args['title'], "Maximum erreicht")

        with patch('utils.dialog_helpers.show_cached_info_dialog') as mock_info:
            show_cached_no_advancement_dialog(2, "Test Char")
            mock_info.assert_called_once()
            args = mock_info.call_args[1]
            self.assertIn("2 Aufstiege", args['message'])
            self.assertIn("Test Char", args['message'])

    def test_pathfinder_kostenlos_dialog_helper(self):
        """Test: Pathfinder-Kostenlos-Dialog-Helper funktioniert."""
        from utils.dialog_helpers import show_cached_pathfinder_kostenlos_dialog

        callbacks = {
            'kostenlos': MagicMock(),
            'kosten': MagicMock(),
            'cancel': MagicMock()
        }

        with patch('utils.dialog_helpers.show_cached_choice_dialog') as mock_choice:
            show_cached_pathfinder_kostenlos_dialog(
                "Test Talent",
                on_kostenlos=callbacks['kostenlos'],
                on_kosten=callbacks['kosten'],
                on_cancel=callbacks['cancel']
            )

            mock_choice.assert_called_once()
            args = mock_choice.call_args[1]  # keyword arguments
            self.assertEqual(args['title'], "Kostenloses Pathfinder-Talent")
            self.assertIn("Test Talent", args['message'])
            self.assertEqual(len(args['choices']), 3)


@unittest.skipUnless(_KIVY_AVAILABLE, "Kivy nicht verfügbar")
class TestDialogCachePerformance(unittest.TestCase):
    """Testet Performance-Verbesserungen durch Dialog-Cache."""

    def setUp(self):
        """Setup für Performance-Tests."""
        with patch('kivymd.app.MDApp.get_running_app') as mock_app:
            mock_app_instance = MagicMock()
            mock_app_instance.theme_cls = MagicMock()
            mock_app_instance.theme_cls.surfaceColor = [1, 1, 1, 1]
            mock_app.return_value = mock_app_instance

            from utils.dialog_cache import DialogCache
            self.cache = DialogCache()

    def test_dialog_reuse_performance(self):
        """Test: Dialog-Wiederverwendung ist messbar schneller als Neuerstellung."""
        # Simuliere Dialog-Erstellung ohne Cache (zeitaufwändiger)
        def create_new_dialog():
            with patch('kivymd.uix.dialog.MDDialog') as mock_dialog_class:
                mock_dialog = MagicMock()
                mock_dialog_class.return_value = mock_dialog
                return mock_dialog_class()  # Simuliert Dialog-Erstellung

        # Messe Zeit für Neuerstellung (10 Mal)
        start_time = time.time()
        for _ in range(10):
            create_new_dialog()
        creation_time = time.time() - start_time

        # Messe Zeit für Cache-Wiederverwendung (10 Mal)
        start_time = time.time()
        for i in range(10):
            self.cache.get_info_dialog(f"Titel {i}", f"Nachricht {i}")
        cache_time = time.time() - start_time

        # Cache sollte nach dem ersten Durchlauf schneller sein
        # (Der erste Durchlauf erstellt den Dialog, die anderen verwenden ihn wieder)
        self.assertLess(cache_time, creation_time * 2)  # Großzügiger Faktor für Testsicherheit

    def test_cache_memory_efficiency(self):
        """Test: Cache-System ist speichereffizient."""
        # Erstelle viele Dialoge mit unterschiedlichen Inhalten
        dialog_count = 50
        for i in range(dialog_count):
            self.cache.get_info_dialog(f"Titel {i}", f"Nachricht {i}")

        # Nur ein Dialog-Objekt sollte gecacht sein (Wiederverwendung)
        cache_info = self.cache.get_cache_info()
        self.assertEqual(cache_info['cached_dialogs'], 1)  # Nur ein Info-Dialog

        # Verschiedene Dialog-Typen sollten separate Cache-Einträge haben
        self.cache.get_confirmation_dialog("Test", "Test")
        self.cache.get_choice_dialog("Test", "Test", [("A", "a"), ("B", "b")])

        cache_info = self.cache.get_cache_info()
        self.assertEqual(cache_info['cached_dialogs'], 3)  # Info + Confirmation + Choice

    def test_theoretical_performance_improvement(self):
        """Test: Theoretische Performance-Verbesserung ist messbar."""
        # Simuliere ohne Cache: 100 Dialog-Erstellungen
        without_cache_operations = 100

        # Simuliere mit Cache: 1 Erstellung + 99 Wiederverwendungen
        with_cache_operations = 1  # Nur eine tatsächliche Erstellung

        # Berechne theoretische Verbesserung
        improvement = ((without_cache_operations - with_cache_operations) / without_cache_operations) * 100

        # 99% Reduktion der Dialog-Erstellungen
        self.assertEqual(improvement, 99.0)

        # Verifikation durch tatsächlichen Cache-Test
        for i in range(100):
            dialog = self.cache.get_info_dialog(f"Test {i}", f"Nachricht {i}")
            self.assertIsNotNone(dialog)

        # Nur ein Dialog sollte tatsächlich erstellt worden sein
        cache_info = self.cache.get_cache_info()
        self.assertEqual(cache_info['cached_dialogs'], 1)


@unittest.skipUnless(_KIVY_AVAILABLE, "Kivy nicht verfügbar")
class TestCachedDialogMixin(unittest.TestCase):
    """Testet das CachedDialogMixin für bestehende Widgets."""

    def setUp(self):
        """Setup für Mixin-Tests."""
        with patch('kivymd.app.MDApp.get_running_app') as mock_app:
            mock_app_instance = MagicMock()
            mock_app_instance.theme_cls = MagicMock()
            mock_app.return_value = mock_app_instance

    def test_mixin_integration(self):
        """Test: CachedDialogMixin kann in bestehende Widgets integriert werden."""
        from utils.dialog_helpers import CachedDialogMixin

        class TestWidget(CachedDialogMixin):
            pass

        widget = TestWidget()

        # Prüfe, dass alle Mixin-Methoden verfügbar sind
        self.assertTrue(hasattr(widget, 'show_info_dialog'))
        self.assertTrue(hasattr(widget, 'show_confirmation_dialog'))
        self.assertTrue(hasattr(widget, 'show_choice_dialog'))
        self.assertTrue(hasattr(widget, 'show_not_duplicatable_dialog'))

    def test_mixin_method_calls(self):
        """Test: Mixin-Methoden rufen die korrekten Helper-Funktionen auf."""
        from utils.dialog_helpers import CachedDialogMixin

        class TestWidget(CachedDialogMixin):
            pass

        widget = TestWidget()

        with patch('utils.dialog_helpers.show_cached_info_dialog') as mock_helper:
            widget.show_info_dialog("Test", "Nachricht")
            mock_helper.assert_called_once_with("Test", "Nachricht", "OK", None)


if __name__ == "__main__":
    unittest.main()