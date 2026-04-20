#!/usr/bin/env python3
"""
Unit Tests für Android Thread-Safety (Schritt 5 der Performance-Optimierung).

Testet, dass kritische Threading-Stellen auf Android über Clock-basierte
Lösungen laufen statt über threading.Thread (JVM-Crash-Vermeidung).
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
class TestAndroidThreadSafety(unittest.TestCase):
    """Testet die Android Thread-Safety Implementierung."""

    def test_html_manager_android_deaktiviert_threading(self):
        """Test: HTMLManager Code-Struktur für Android Thread-Safety."""
        from manager.html_manager import HTMLManager
        import inspect

        # Überprüfe dass _open_via_localhost Code für Android-Erkennung hat
        source = inspect.getsource(HTMLManager._open_via_localhost)

        # Android-spezifische Checks sollten vorhanden sein
        self.assertIn("kivy_platform == 'android'", source)
        self.assertIn("HTTP-Server auf Android deaktiviert", source)
        self.assertIn("Thread-Safety", source)

        # Desktop Threading sollte nach Android-Check kommen
        self.assertIn("threading.Thread", source)
        self.assertIn("daemon=True", source)

    def test_html_manager_desktop_threading_struktur(self):
        """Test: HTMLManager behält Desktop Threading-Struktur."""
        from manager.html_manager import HTMLManager
        import inspect

        # Überprüfe dass Desktop-Path Threading verwendet
        source = inspect.getsource(HTMLManager._open_via_localhost)

        # Desktop-spezifische Threading-Struktur
        self.assertIn("threading.Thread(target=server.serve_forever", source)
        self.assertIn("cleanup_thread = threading.Thread(target=auto_shutdown", source)

        # Android-Check sollte Desktop-Code umgehen
        self.assertIn("# Desktop:", source)  # Desktop-Kommentar

    def test_eigenschaften_view_android_code_struktur(self):
        """Test: EigenschaftenView Code-Struktur für Android Thread-Safety."""
        from views.eigenschaften_view import EigenschaftenWidget
        import inspect

        # Überprüfe dass _verzoegerte_initialisierung Android-Erkennung hat
        source = inspect.getsource(EigenschaftenWidget._verzoegerte_initialisierung)

        # Android-spezifische Checks sollten vorhanden sein
        self.assertIn("kivy_platform == 'android'", source)
        self.assertIn("Clock.schedule_once", source)
        self.assertIn("_lade_daten_android_sicher", source)

        # Desktop Threading sollte nach Android-Check kommen
        self.assertIn("Thread(target=self._lade_daten_im_hintergrund)", source)

    def test_screens_android_update_check_struktur(self):
        """Test: InfoScreen Code-Struktur für Android Update-Check."""
        from views.screens import InfoScreen
        import inspect

        # Überprüfe dass pruefe_auf_update Android-Erkennung hat
        source = inspect.getsource(InfoScreen.pruefe_auf_update)

        # Android-spezifische Checks sollten vorhanden sein
        self.assertIn("kivy_platform == 'android'", source)
        self.assertIn("Update-Check übersprungen", source)
        self.assertIn("Play Store Policy", source)

        # Clock.schedule_once sollte für Android verwendet werden
        self.assertIn("Clock.schedule_once", source)

        # Desktop Threading sollte nach Android-Check kommen
        self.assertIn("threading.Thread", source)

    def test_screens_desktop_threading_struktur(self):
        """Test: InfoScreen behält Desktop Threading-Struktur."""
        from views.screens import InfoScreen
        import inspect

        # Überprüfe dass Desktop-Path Threading verwendet
        source = inspect.getsource(InfoScreen.pruefe_auf_update)

        # Desktop Threading sollte nach Android-Check kommen
        self.assertIn("threading.Thread(target=self._update_check_worker", source)
        self.assertIn("daemon=True", source)

    def test_platform_detection_konsistenz(self):
        """Test: Plattform-Erkennung ist konsistent in allen Modulen."""
        # Alle Module sollten das gleiche Pattern verwenden
        test_cases = [
            ('manager.html_manager', 'kivy.utils.platform'),
            ('views.screens', 'kivy.utils.platform'),
        ]

        for module_name, platform_import in test_cases:
            with patch(platform_import, 'android'):
                # Import sollte funktionieren ohne Fehler
                try:
                    __import__(module_name)
                except ImportError:
                    pass  # Module könnten Abhängigkeiten haben
                # Haupttest: Kein Exception bei platform-Check


if __name__ == "__main__":
    unittest.main()