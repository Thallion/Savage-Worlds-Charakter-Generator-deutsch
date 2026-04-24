#!/usr/bin/env python3
"""
Unit Tests für den Android Scoped-Storage-Fix in `utils/android_print_utils.py`
und die Android-Fallback-Logik in `manager/html_manager.py::_open_via_localhost`.

Hintergrund: Unter Scoped Storage (targetSdk ≥ 29) ist
`/storage/emulated/0/Download/` für normale Apps nicht mehr beschreibbar —
`open(..., 'w')` scheitert mit PermissionError. Der Fix bevorzugt die
app-private externe Ablage (`getExternalFilesDir(DOWNLOADS)`), die ohne
Runtime-Permission immer beschreibbar ist.

Zusätzlich: Auf Android muss `_open_via_localhost` eine Exception werfen,
damit `_open_file_on_android` auf FileProvider (Strategie 2) fällt — der
bisherige `webbrowser.open("file://...")`-Fallback löst eine
FileUriExposedException aus.
"""

import inspect
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:  # pragma: no cover
    import kivy  # noqa: F401
    _KIVY_AVAILABLE = True
except Exception:
    _KIVY_AVAILABLE = False


@unittest.skipUnless(_KIVY_AVAILABLE, "Kivy nicht verfügbar")
class TestGetDownloadsPath(unittest.TestCase):
    """Testet `get_downloads_path()` unter verschiedenen Android-Pfadverfügbarkeiten."""

    def setUp(self):
        # Fake `jnius.autoclass` — nur Environment/PythonActivity werden gebraucht.
        self._env = MagicMock(name='Environment')
        self._env.DIRECTORY_DOWNLOADS = 'Download'

        self._context = MagicMock(name='mActivity')
        python_activity = MagicMock(name='PythonActivity')
        python_activity.mActivity = self._context

        def _autoclass(name):
            if name == 'android.os.Environment':
                return self._env
            if name == 'org.kivy.android.PythonActivity':
                return python_activity
            raise AssertionError(f"Unerwarteter autoclass-Aufruf: {name}")

        self._fake_jnius = MagicMock()
        self._fake_jnius.autoclass.side_effect = _autoclass

        self._patches = [
            patch.dict('sys.modules', {'jnius': self._fake_jnius}),
            patch('utils.android_print_utils.is_android', return_value=True),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()

    def _make_dir(self, path, exists=True):
        d = MagicMock()
        d.exists.return_value = exists
        d.getAbsolutePath.return_value = path
        return d

    def test_prefers_app_private_external_dir(self):
        """App-private externer Downloads-Ordner wird bevorzugt."""
        from utils import android_print_utils

        app_private = self._make_dir('/data/user/0/app/files/Download', exists=True)
        self._context.getExternalFilesDir.return_value = app_private
        self._context.getFilesDir.return_value = self._make_dir('/data/user/0/app/files')

        result = android_print_utils.get_downloads_path()

        self.assertEqual(result, '/data/user/0/app/files/Download')
        self._context.getExternalFilesDir.assert_called_once_with('Download')
        # Öffentlicher Scoped-Storage-Pfad darf NICHT verwendet werden
        self._env.getExternalStoragePublicDirectory.assert_not_called()

    def test_creates_app_private_dir_if_missing(self):
        """Wenn externes Verzeichnis noch nicht existiert, wird mkdirs() aufgerufen."""
        from utils import android_print_utils

        app_private = MagicMock()
        app_private.exists.side_effect = [False, True]
        app_private.getAbsolutePath.return_value = '/data/user/0/app/files/Download'
        self._context.getExternalFilesDir.return_value = app_private

        result = android_print_utils.get_downloads_path()

        app_private.mkdirs.assert_called_once()
        self.assertEqual(result, '/data/user/0/app/files/Download')

    def test_falls_back_to_internal_when_external_unavailable(self):
        """Ohne externe Ablage → Rückgriff auf internes app-Verzeichnis."""
        from utils import android_print_utils

        self._context.getExternalFilesDir.return_value = None
        self._context.getFilesDir.return_value = self._make_dir('/data/user/0/app/files')

        result = android_print_utils.get_downloads_path()

        self.assertEqual(result, '/data/user/0/app/files')

    def test_falls_back_to_internal_when_external_raises(self):
        """Exception aus getExternalFilesDir → Fallback auf internes Verzeichnis, kein Crash."""
        from utils import android_print_utils

        self._context.getExternalFilesDir.side_effect = RuntimeError("boom")
        self._context.getFilesDir.return_value = self._make_dir('/data/user/0/app/files')

        result = android_print_utils.get_downloads_path()

        self.assertEqual(result, '/data/user/0/app/files')

    def test_returns_none_on_desktop(self):
        """Auf Nicht-Android liefert die Funktion None."""
        for p in self._patches:
            p.stop()
        self._patches = []
        with patch('utils.android_print_utils.is_android', return_value=False):
            from utils import android_print_utils
            self.assertIsNone(android_print_utils.get_downloads_path())


@unittest.skipUnless(_KIVY_AVAILABLE, "Kivy nicht verfügbar")
class TestOpenViaLocalhostAndroidFallback(unittest.TestCase):
    """Stellt sicher, dass `_open_via_localhost` auf Android den HTTP-Server
    verwendet (statt RuntimeError zu werfen oder file:// URIs zu öffnen)."""

    def test_android_no_longer_raises(self):
        """_open_via_localhost wirft kein RuntimeError mehr auf Android."""
        from manager.html_manager import HTMLManager

        source = inspect.getsource(HTMLManager._open_via_localhost)
        # Kein platform-spezifischer RuntimeError mehr
        self.assertNotIn('RuntimeError', source)
        # Kein raise/return im Android-Block (die Funktion läuft plattformübergreifend)
        self.assertNotIn('raise RuntimeError', source)
        # HTTPServer-Ansatz wird plattformübergreifend verwendet
        self.assertIn('HTTPServer', source)
        self.assertIn('webbrowser.open(url)', source)

    def test_source_does_not_use_file_uri_webbrowser_on_android(self):
        """Regression: `webbrowser.open('file://...')` ist nicht mehr im Code."""
        from manager.html_manager import HTMLManager

        source = inspect.getsource(HTMLManager._open_via_localhost)
        # file://-URI mit webbrowser.open darf nirgends im Code vorkommen
        self.assertNotIn('webbrowser.open(f"file://', source)
        self.assertNotIn("webbrowser.open('file://", source)
        # Bestätigt dass HTTP-Server-Ansatz verwendet wird
        self.assertIn('HTTPServer', source)
        self.assertIn('http://127.0.0.1', source)


if __name__ == "__main__":
    unittest.main()
