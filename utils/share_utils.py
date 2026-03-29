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
    Kopiert eine Datei in ein Cache-Verzeichnis zum Teilen.

    Dateien im internen App-Speicher sind für andere Apps nicht zugänglich.
    Durch das Kopieren ins Cache-Verzeichnis wird der Zugriff ermöglicht.

    Versucht zuerst das externe Cache-Verzeichnis, dann den internen Cache
    als Fallback bei Berechtigungsproblemen.

    Returns:
        str: Pfad zur kopierten Datei im Share-Verzeichnis
    """
    # Mögliche Cache-Verzeichnisse in Prioritätsreihenfolge
    cache_dirs = []
    ext_cache = context.getExternalCacheDir()
    if ext_cache:
        cache_dirs.append(ext_cache.getAbsolutePath())
    int_cache = context.getCacheDir()
    if int_cache:
        cache_dirs.append(int_cache.getAbsolutePath())

    if not cache_dirs:
        raise OSError("Kein Cache-Verzeichnis verfügbar")

    dest_filename = os.path.basename(file_path)
    last_error = None

    for cache_base in cache_dirs:
        share_dir = os.path.join(cache_base, 'share')
        try:
            os.makedirs(share_dir, exist_ok=True)
            dest_path = os.path.join(share_dir, dest_filename)
            # shutil.copy statt copy2 - copy2 kann auf Android bei
            # Metadaten (Timestamps/Permissions) fehlschlagen
            shutil.copy(file_path, dest_path)
            Logger.debug(f"Teilen: Datei kopiert nach {dest_path}")
            return dest_path
        except PermissionError as e:
            Logger.warning(
                f"Teilen: Kein Zugriff auf {share_dir}, versuche nächstes Verzeichnis: {e}"
            )
            last_error = e
            continue
        except OSError as e:
            Logger.warning(
                f"Teilen: Fehler bei {share_dir}, versuche nächstes Verzeichnis: {e}"
            )
            last_error = e
            continue

    raise last_error or OSError("Keine beschreibbares Cache-Verzeichnis gefunden")


def _erzeuge_content_uri_via_mediastore(context, file_path, mime_type):
    """
    Erzeugt eine content:// URI über MediaStore (Android 10+).

    Funktioniert ohne FileProvider-Konfiguration im Manifest.
    Die Datei wird in den Downloads-Bereich kopiert und eine content:// URI
    zurückgegeben, die von allen Apps gelesen werden kann.

    Returns:
        Content-URI oder None bei Fehler
    """
    from jnius import autoclass

    Build_VERSION = autoclass('android.os.Build$VERSION')
    if Build_VERSION.SDK_INT < 29:
        Logger.debug("Teilen: MediaStore Downloads nicht verfügbar (API < 29)")
        return None

    try:
        ContentValues = autoclass('android.content.ContentValues')
        MediaStore_Downloads = autoclass('android.provider.MediaStore$Downloads')

        values = ContentValues()
        filename = os.path.basename(file_path)
        values.put("_display_name", filename)
        values.put("mime_type", mime_type)

        resolver = context.getContentResolver()
        uri = resolver.insert(MediaStore_Downloads.EXTERNAL_CONTENT_URI, values)

        if uri is None:
            Logger.warning("Teilen: MediaStore insert lieferte keine URI")
            return None

        # Dateiinhalt über nativen File-Descriptor schreiben
        pfd = resolver.openFileDescriptor(uri, "w")
        fd = pfd.detachFd()
        try:
            with open(file_path, 'rb') as src:
                data = src.read()
            os.write(fd, data)
        finally:
            os.close(fd)

        Logger.debug(f"Teilen: MediaStore content:// URI erzeugt für {filename}")
        return uri
    except Exception as e:
        Logger.warning(f"Teilen: MediaStore fehlgeschlagen: {e}")
        return None


def _erzeuge_content_uri(context, file_path, mime_type='*/*'):
    """
    Erzeugt eine content:// URI für die Datei.

    Versucht in dieser Reihenfolge:
    1. FileProvider (bevorzugt, benötigt Manifest-Konfiguration)
    2. MediaStore Downloads (Android 10+, ohne Manifest-Konfiguration)
    3. file:// URI mit gelocktem StrictMode (Fallback für ältere Geräte)

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

    # Versuch 2: MediaStore (Android 10+, kein Manifest-Eintrag nötig)
    mediastore_uri = _erzeuge_content_uri_via_mediastore(context, file_path, mime_type)
    if mediastore_uri is not None:
        return mediastore_uri

    # Versuch 3: StrictMode lockern und file:// URI verwenden
    # Notwendig auf Android 7+ (API 24+) wenn FileProvider nicht im Manifest konfiguriert ist
    Logger.warning("Teilen: Verwende file:// URI als letzten Fallback")
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
    from jnius import autoclass, cast

    Intent = autoclass('android.content.Intent')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    JavaString = autoclass('java.lang.String')

    context = PythonActivity.mActivity

    # Datei ins teilbare Verzeichnis kopieren
    share_path = _kopiere_in_share_verzeichnis(context, file_path)
    content_uri = _erzeuge_content_uri(context, share_path, mime_type)

    intent = Intent(Intent.ACTION_SEND)
    intent.setType(mime_type)
    # Uri muss als Parcelable gecastet werden, damit pyjnius die richtige
    # putExtra(String, Parcelable)-Überladung wählt statt putExtra(String, String)
    intent.putExtra(Intent.EXTRA_STREAM,
                    cast('android.os.Parcelable', content_uri))
    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

    # Python-String muss als CharSequence gecastet werden für createChooser
    java_title = cast('java.lang.CharSequence', JavaString(title))
    chooser = Intent.createChooser(intent, java_title)
    chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    context.startActivity(chooser)
    Logger.info(f"Android: Datei geteilt: {os.path.basename(file_path)}")
    return True


def _share_multiple_on_android(file_paths, mime_type, title):
    """Teilt mehrere Dateien über Android Share-Intent (ACTION_SEND_MULTIPLE)."""
    from jnius import autoclass, cast

    Intent = autoclass('android.content.Intent')
    ArrayList = autoclass('java.util.ArrayList')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    JavaString = autoclass('java.lang.String')

    context = PythonActivity.mActivity
    uris = ArrayList()

    for file_path in file_paths:
        # Jede Datei ins teilbare Verzeichnis kopieren
        share_path = _kopiere_in_share_verzeichnis(context, file_path)
        content_uri = _erzeuge_content_uri(context, share_path, mime_type)
        uris.add(content_uri)

    intent = Intent(Intent.ACTION_SEND_MULTIPLE)
    intent.setType(mime_type)
    intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

    # Python-String muss als CharSequence gecastet werden für createChooser
    java_title = cast('java.lang.CharSequence', JavaString(title))
    chooser = Intent.createChooser(intent, java_title)
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
