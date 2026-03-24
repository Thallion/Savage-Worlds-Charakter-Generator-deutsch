# utils/share_utils.py
"""
Plattformübergreifende Teilen-Funktionalität für Dateien.
Unterstützt Android (Share-Intent) und Desktop (xdg-open / open / Explorer).
"""

import os
import shutil
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


def _kopiere_in_share_verzeichnis(context, file_path):
    """
    Kopiert eine Datei in das externe Cache-Verzeichnis zum Teilen.

    Dateien im internen App-Speicher sind für andere Apps nicht zugänglich.
    Durch das Kopieren ins externe Cache-Verzeichnis wird der Zugriff ermöglicht.

    Returns:
        str: Pfad zur kopierten Datei im Share-Verzeichnis
    """
    cache_dir = context.getExternalCacheDir()
    if cache_dir:
        share_dir = os.path.join(cache_dir.getAbsolutePath(), 'share')
    else:
        # Fallback auf internen Cache
        share_dir = os.path.join(context.getCacheDir().getAbsolutePath(), 'share')

    os.makedirs(share_dir, exist_ok=True)
    dest_path = os.path.join(share_dir, os.path.basename(file_path))
    shutil.copy2(file_path, dest_path)
    Logger.debug(f"Teilen: Datei kopiert nach {dest_path}")
    return dest_path


def _erzeuge_content_uri(context, file_path):
    """
    Erzeugt eine content:// URI für die Datei über FileProvider.

    Falls FileProvider nicht konfiguriert ist (Manifest fehlt), wird als Fallback
    StrictMode gelockert und eine file:// URI verwendet.

    Returns:
        Content-URI für die Datei
    """
    from jnius import autoclass

    File = autoclass('java.io.File')
    java_file = File(file_path)

    # Versuch 1: FileProvider (bevorzugt, sicher)
    try:
        FileProvider = autoclass('androidx.core.content.FileProvider')
        authority = context.getPackageName() + '.fileprovider'
        content_uri = FileProvider.getUriForFile(context, authority, java_file)
        Logger.debug(f"Teilen: FileProvider URI erzeugt für {os.path.basename(file_path)}")
        return content_uri
    except Exception as e:
        Logger.warning(f"Teilen: FileProvider nicht verfügbar ({e}), verwende Fallback")

    # Versuch 2: StrictMode lockern und file:// URI verwenden
    # Notwendig auf Android 7+ (API 24+) wenn FileProvider nicht im Manifest konfiguriert ist
    try:
        StrictMode = autoclass('android.os.StrictMode')
        Builder = autoclass('android.os.StrictMode$VmPolicy$Builder')
        StrictMode.setVmPolicy(Builder().build())
        Logger.debug("Teilen: StrictMode VmPolicy gelockert für file:// URI")
    except Exception as e:
        Logger.warning(f"Teilen: StrictMode konnte nicht angepasst werden: {e}")

    Uri = autoclass('android.net.Uri')
    return Uri.fromFile(java_file)


def _share_on_android(file_path, mime_type, title):
    """Teilt eine Datei über Android Share-Intent mit FileProvider."""
    from jnius import autoclass

    Intent = autoclass('android.content.Intent')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')

    context = PythonActivity.mActivity

    # Datei ins teilbare Verzeichnis kopieren
    share_path = _kopiere_in_share_verzeichnis(context, file_path)
    content_uri = _erzeuge_content_uri(context, share_path)

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
    ArrayList = autoclass('java.util.ArrayList')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')

    context = PythonActivity.mActivity
    uris = ArrayList()

    for file_path in file_paths:
        # Jede Datei ins teilbare Verzeichnis kopieren
        share_path = _kopiere_in_share_verzeichnis(context, file_path)
        content_uri = _erzeuge_content_uri(context, share_path)
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
