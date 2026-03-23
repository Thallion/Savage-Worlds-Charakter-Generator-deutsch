# utils/share_utils.py
"""
Plattformübergreifende Teilen-Funktionalität für Dateien.
Unterstützt Android (Share-Intent) und Desktop (xdg-open / open / Explorer).
"""

import os
import subprocess
from pathlib import Path
from kivy.logger import Logger
from kivy.utils import platform as kivy_platform


def share_file(file_path, mime_type='*/*', title="Datei teilen"):
    """
    Teilt eine Datei über die plattformspezifische Teilen-Funktion.

    Args:
        file_path: Pfad zur Datei
        mime_type: MIME-Typ der Datei (z.B. 'application/json', 'application/pdf')
        title: Titel für den Teilen-Dialog

    Returns:
        bool: True bei Erfolg
    """
    file_path = str(file_path)
    if not os.path.exists(file_path):
        Logger.error(f"Teilen: Datei nicht gefunden: {file_path}")
        return False

    try:
        if kivy_platform == 'android':
            return _share_on_android(file_path, mime_type, title)
        else:
            return _share_on_desktop(file_path)
    except Exception as e:
        Logger.error(f"Fehler beim Teilen der Datei: {e}")
        return False


def share_multiple_files(file_paths, mime_type='*/*', title="Dateien teilen"):
    """
    Teilt mehrere Dateien über die plattformspezifische Teilen-Funktion.

    Args:
        file_paths: Liste von Dateipfaden
        mime_type: MIME-Typ der Dateien
        title: Titel für den Teilen-Dialog

    Returns:
        bool: True bei Erfolg
    """
    # Nur existierende Dateien
    existing = [str(p) for p in file_paths if os.path.exists(str(p))]
    if not existing:
        Logger.error("Teilen: Keine der angegebenen Dateien existiert")
        return False

    try:
        if kivy_platform == 'android':
            return _share_multiple_on_android(existing, mime_type, title)
        else:
            # Auf Desktop: Ordner mit den Dateien öffnen
            return _share_on_desktop(existing[0])
    except Exception as e:
        Logger.error(f"Fehler beim Teilen der Dateien: {e}")
        return False


def get_mime_type(file_path):
    """Bestimmt den MIME-Typ anhand der Dateiendung."""
    ext = Path(file_path).suffix.lower()
    mime_types = {
        '.json': 'application/json',
        '.pdf': 'application/pdf',
        '.html': 'text/html',
        '.htm': 'text/html',
        '.txt': 'text/plain',
    }
    return mime_types.get(ext, '*/*')


def _share_on_android(file_path, mime_type, title):
    """Teilt eine Datei über Android Share-Intent mit FileProvider."""
    from jnius import autoclass

    Intent = autoclass('android.content.Intent')
    File = autoclass('java.io.File')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')

    context = PythonActivity.mActivity
    java_file = File(file_path)

    # FileProvider für sichere URI-Erzeugung verwenden
    try:
        FileProvider = autoclass('androidx.core.content.FileProvider')
        authority = context.getPackageName() + '.fileprovider'
        content_uri = FileProvider.getUriForFile(context, authority, java_file)
    except Exception:
        Uri = autoclass('android.net.Uri')
        content_uri = Uri.fromFile(java_file)

    intent = Intent(Intent.ACTION_SEND)
    intent.setType(mime_type)
    intent.putExtra(Intent.EXTRA_STREAM, content_uri)
    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

    chooser = Intent.createChooser(intent, title)
    chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    context.startActivity(chooser)
    Logger.info(f"Android: Datei geteilt: {os.path.basename(file_path)}")
    return True


def _share_multiple_on_android(file_paths, mime_type, title):
    """Teilt mehrere Dateien über Android Share-Intent (ACTION_SEND_MULTIPLE)."""
    from jnius import autoclass

    Intent = autoclass('android.content.Intent')
    File = autoclass('java.io.File')
    ArrayList = autoclass('java.util.ArrayList')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')

    context = PythonActivity.mActivity
    uris = ArrayList()

    for file_path in file_paths:
        java_file = File(file_path)
        try:
            FileProvider = autoclass('androidx.core.content.FileProvider')
            authority = context.getPackageName() + '.fileprovider'
            content_uri = FileProvider.getUriForFile(context, authority, java_file)
        except Exception:
            Uri = autoclass('android.net.Uri')
            content_uri = Uri.fromFile(java_file)
        uris.add(content_uri)

    intent = Intent(Intent.ACTION_SEND_MULTIPLE)
    intent.setType(mime_type)
    intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

    chooser = Intent.createChooser(intent, title)
    chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    context.startActivity(chooser)
    Logger.info(f"Android: {len(file_paths)} Dateien geteilt")
    return True


def _share_on_desktop(file_path):
    """Öffnet den Dateimanager mit der Datei ausgewählt (Desktop)."""
    import sys

    file_path = os.path.abspath(file_path)
    folder = os.path.dirname(file_path)

    try:
        if sys.platform == 'win32':
            # Windows: Explorer mit Datei markiert öffnen
            subprocess.Popen(['explorer', '/select,', file_path])
        elif sys.platform == 'darwin':
            # macOS: Finder mit Datei markiert öffnen
            subprocess.Popen(['open', '-R', file_path])
        else:
            # Linux: Dateimanager mit dem Ordner öffnen
            subprocess.Popen(['xdg-open', folder])
        Logger.info(f"Desktop: Ordner geöffnet für: {os.path.basename(file_path)}")
        return True
    except Exception as e:
        Logger.warning(f"Desktop: Dateimanager konnte nicht geöffnet werden: {e}")
        return False
