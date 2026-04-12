# utils/intent_handler.py
"""
Android Intent-Handler für eingehende JSON-Dateien (Charakter/Settings).
Ermöglicht das Empfangen von .json-Dateien über "Teilen" oder "Öffnen mit".
"""

import os
import json
import shutil
from pathlib import Path
from kivy.logger import Logger
from kivy.utils import platform as kivy_platform


def handle_incoming_intent(app):
    """
    Prüft ob die App über einen Intent mit Datei gestartet/fortgesetzt wurde
    und importiert die Datei bei Bedarf.

    Wird beim App-Start (on_start) und bei on_new_intent aufgerufen.

    Args:
        app: Die MDApp-Instanz (SW_Charakter_GeneratorApp)
    """
    if kivy_platform != 'android':
        return

    try:
        from jnius import autoclass

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        activity = PythonActivity.mActivity
        intent = activity.getIntent()

        if not intent:
            return

        action = intent.getAction()
        Logger.info(f"IntentHandler: Action={action}")

        if action == Intent.ACTION_SEND:
            _handle_send_intent(app, intent)
            # Intent als verarbeitet markieren, um doppelte Verarbeitung zu verhindern
            intent.setAction("")
        elif action == Intent.ACTION_VIEW:
            _handle_view_intent(app, intent)
            intent.setAction("")

    except Exception as e:
        Logger.error(f"IntentHandler: Fehler beim Verarbeiten des Intents: {e}")


def handle_new_intent(app, intent):
    """
    Verarbeitet einen neuen Intent (on_new_intent Callback).

    Args:
        app: Die MDApp-Instanz
        intent: Der Android Intent
    """
    if kivy_platform != 'android':
        return

    try:
        from jnius import autoclass
        IntentClass = autoclass('android.content.Intent')

        action = intent.getAction()
        Logger.info(f"IntentHandler: Neuer Intent, Action={action}")

        if action == IntentClass.ACTION_SEND:
            _handle_send_intent(app, intent)
        elif action == IntentClass.ACTION_VIEW:
            _handle_view_intent(app, intent)

    except Exception as e:
        Logger.error(f"IntentHandler: Fehler bei neuem Intent: {e}")


def _handle_send_intent(app, intent):
    """Verarbeitet ACTION_SEND - Datei wurde über 'Teilen' gesendet."""
    try:
        from jnius import autoclass
        IntentClass = autoclass('android.content.Intent')

        uri = intent.getParcelableExtra(IntentClass.EXTRA_STREAM)
        if uri:
            Logger.info(f"IntentHandler: SEND URI empfangen: {uri.toString()}")
            _import_from_uri(app, uri)
            return

        text = intent.getStringExtra(IntentClass.EXTRA_TEXT)
        if text:
            Logger.info(f"IntentHandler: EXTRA_TEXT empfangen ({len(text)} Zeichen)")
            _import_from_text(app, text)
            return

        Logger.info("IntentHandler: ACTION_SEND ohne EXTRA_STREAM oder EXTRA_TEXT")

    except Exception as e:
        Logger.error(f"IntentHandler: Fehler bei ACTION_SEND: {e}")


def _handle_view_intent(app, intent):
    """Verarbeitet ACTION_VIEW - Datei wurde über 'Öffnen mit' geöffnet."""
    try:
        uri = intent.getData()
        if uri:
            Logger.info(f"IntentHandler: VIEW URI empfangen: {uri.toString()}")
            _import_from_uri(app, uri)
        else:
            Logger.info("IntentHandler: ACTION_VIEW ohne URI")

    except Exception as e:
        Logger.error(f"IntentHandler: Fehler bei ACTION_VIEW: {e}")


def _import_from_text(app, text):
    """
    Importiert JSON-Text der als String (EXTRA_TEXT) gesendet wurde.
    WhatsApp teilt oft Dateien als Text statt als Dateianhang.

    Args:
        app: Die MDApp-Instanz
        text: Der empfangene Text (JSON-Inhalt)
    """
    try:
        if not text or not text.strip():
            _show_import_error(app, "Kein Inhalt empfangen.")
            return

        # JSON validieren
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            Logger.error(f"IntentHandler: Ungültige JSON im Text: {e}")
            _show_import_error(app, f"Der geteilte Inhalt ist kein gültiges JSON:\n{e}")
            return

        # Typ erkennen
        file_type = _detect_json_type(data)
        Logger.info(f"IntentHandler: Erkannter Typ aus Text: {file_type}")

        # Dateiname aus JSON-Daten oder Zeitstempel generieren
        import datetime
        char_name = data.get('name', data.get('char_name', ''))
        if char_name:
            safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"{safe_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            filename = f"import_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Speichern
        if file_type == 'charakter':
            target_path = _save_to_chars_dir(filename, text)
            if target_path:
                _show_import_success_charakter(app, filename, target_path)
        elif file_type == 'setting':
            target_path = _save_to_settings_dir(filename, text)
            if target_path:
                _show_import_success_setting(app, filename)
        else:
            target_path = _save_to_chars_dir(filename, text)
            if target_path:
                _show_import_success_charakter(app, filename, target_path)

    except Exception as e:
        Logger.error(f"IntentHandler: Fehler beim Importieren aus Text: {e}")
        _show_import_error(app, f"Fehler beim Import:\n{e}")


def _import_from_uri(app, uri):
    """
    Importiert eine JSON-Datei von einer Content-URI oder File-URI.

    1. Liest den Inhalt über ContentResolver
    2. Validiert ob es eine gültige JSON-Datei ist
    3. Erkennt ob es ein Charakter oder Setting ist
    4. Kopiert die Datei ins passende Verzeichnis
    5. Bietet dem User an, den Charakter zu laden

    Args:
        app: Die MDApp-Instanz
        uri: Android Uri-Objekt
    """
    try:
        from jnius import autoclass

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity

        # Dateiname aus URI ermitteln
        filename = _get_filename_from_uri(context, uri)
        if not filename:
            filename = "empfangene_datei.json"

        # .json-Endung sicherstellen
        if not filename.lower().endswith('.json'):
            Logger.warning(f"IntentHandler: Datei ist keine JSON: {filename}")
            _show_import_error(app, f"Nur .json-Dateien werden unterstützt.\nEmpfangen: {filename}")
            return

        # Inhalt über ContentResolver lesen
        content = _read_content_from_uri(context, uri)
        if not content:
            _show_import_error(app, "Die Datei konnte nicht gelesen werden.")
            return

        # JSON validieren
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            Logger.error(f"IntentHandler: Ungültige JSON-Datei: {e}")
            _show_import_error(app, f"Die Datei enthält kein gültiges JSON:\n{e}")
            return

        # Typ erkennen: Charakter oder Setting?
        file_type = _detect_json_type(data)
        Logger.info(f"IntentHandler: Erkannter Dateityp: {file_type}")

        # In passendes Verzeichnis kopieren
        if file_type == 'charakter':
            target_path = _save_to_chars_dir(filename, content)
            if target_path:
                _show_import_success_charakter(app, filename, target_path)
        elif file_type == 'setting':
            target_path = _save_to_settings_dir(filename, content)
            if target_path:
                _show_import_success_setting(app, filename)
        else:
            # Unbekannter Typ - als Charakter behandeln (häufigstes Szenario)
            target_path = _save_to_chars_dir(filename, content)
            if target_path:
                _show_import_success_charakter(app, filename, target_path)

    except Exception as e:
        Logger.error(f"IntentHandler: Fehler beim Importieren: {e}")
        _show_import_error(app, f"Fehler beim Import:\n{e}")


def _get_filename_from_uri(context, uri):
    """Ermittelt den Dateinamen aus einer Content-URI über den ContentResolver."""
    try:
        scheme = uri.getScheme()

        if scheme == 'file':
            path = uri.getPath()
            return os.path.basename(path) if path else None

        if scheme == 'content':
            from jnius import autoclass
            Cursor = autoclass('android.database.Cursor')

            cursor = context.getContentResolver().query(uri, None, None, None, None)
            if cursor and cursor.moveToFirst():
                # OpenableColumns.DISPLAY_NAME = "_display_name"
                name_index = cursor.getColumnIndex("_display_name")
                if name_index >= 0:
                    filename = cursor.getString(name_index)
                    cursor.close()
                    return filename
                cursor.close()

        return None
    except Exception as e:
        Logger.warning(f"IntentHandler: Dateiname konnte nicht ermittelt werden: {e}")
        return None


def _read_content_from_uri(context, uri):
    """Liest den gesamten Inhalt einer URI über den ContentResolver."""
    try:
        from jnius import autoclass

        BufferedReader = autoclass('java.io.BufferedReader')
        InputStreamReader = autoclass('java.io.InputStreamReader')
        StringBuilder = autoclass('java.lang.StringBuilder')

        input_stream = context.getContentResolver().openInputStream(uri)
        if not input_stream:
            Logger.error("IntentHandler: InputStream ist null")
            return None

        reader = BufferedReader(InputStreamReader(input_stream, 'UTF-8'))
        sb = StringBuilder()
        line = reader.readLine()
        while line is not None:
            sb.append(line)
            sb.append('\n')
            line = reader.readLine()

        reader.close()
        input_stream.close()

        content = sb.toString()
        Logger.info(f"IntentHandler: {len(content)} Zeichen gelesen")
        return content

    except Exception as e:
        Logger.error(f"IntentHandler: Fehler beim Lesen der URI: {e}")
        return None


def _detect_json_type(data):
    """
    Erkennt ob die JSON-Daten ein Charakter oder ein Setting sind.

    Charakter-Dateien enthalten typischerweise: char_name, setting, rang, etc.
    Setting-Dateien enthalten typischerweise: Talente, Handicaps, Völker, etc.

    Returns:
        str: 'charakter', 'setting' oder 'unbekannt'
    """
    if not isinstance(data, dict):
        return 'unbekannt'

    # Charakter-Schlüssel
    charakter_keys = {'char_name', 'setting', 'rang', 'erfahrungspunkte', 'attribute'}
    # Setting-Schlüssel
    setting_keys = {'Talente', 'Handicaps', 'Völker', 'Fertigkeiten', 'Mächte'}

    char_matches = len(charakter_keys.intersection(data.keys()))
    setting_matches = len(setting_keys.intersection(data.keys()))

    if char_matches >= 2:
        return 'charakter'
    elif setting_matches >= 2:
        return 'setting'
    else:
        return 'unbekannt'


def _save_to_chars_dir(filename, content):
    """Speichert den Inhalt als Datei im Charakter-Verzeichnis."""
    try:
        from utils.path_utils import get_chars_path

        chars_dir = get_chars_path()
        os.makedirs(chars_dir, exist_ok=True)

        target_path = os.path.join(chars_dir, filename)

        # Falls Datei bereits existiert, Zähler anhängen
        if os.path.exists(target_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(target_path):
                target_path = os.path.join(chars_dir, f"{base}_{counter}{ext}")
                counter += 1

        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)

        Logger.info(f"IntentHandler: Charakter gespeichert: {target_path}")
        return target_path

    except Exception as e:
        Logger.error(f"IntentHandler: Fehler beim Speichern des Charakters: {e}")
        return None


def _save_to_settings_dir(filename, content):
    """Speichert den Inhalt als Datei im Benutzer-Settings-Verzeichnis."""
    try:
        from utils.path_utils import get_user_settings_path

        settings_dir = get_user_settings_path()
        os.makedirs(settings_dir, exist_ok=True)

        target_path = os.path.join(settings_dir, filename)

        # Falls Datei bereits existiert, Zähler anhängen
        if os.path.exists(target_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(target_path):
                target_path = os.path.join(settings_dir, f"{base}_{counter}{ext}")
                counter += 1

        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)

        Logger.info(f"IntentHandler: Setting gespeichert: {target_path}")
        return target_path

    except Exception as e:
        Logger.error(f"IntentHandler: Fehler beim Speichern des Settings: {e}")
        return None


def _show_import_success_charakter(app, filename, filepath):
    """Zeigt Erfolgs-Dialog mit Option den Charakter zu laden."""
    from kivy.clock import Clock

    def _show_dialog(dt):
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()

            if dialog_service:
                from kivymd.uix.dialog import (
                    MDDialog, MDDialogHeadlineText, MDDialogSupportingText,
                    MDDialogContentContainer, MDDialogButtonContainer
                )
                from kivymd.uix.button import MDButton, MDButtonText

                dialog = MDDialog(
                    MDDialogHeadlineText(text="Charakter empfangen"),
                    MDDialogSupportingText(
                        text=f"'{filename}' wurde importiert.\n\nMöchtest du den Charakter jetzt laden?"
                    ),
                    MDDialogButtonContainer(
                        MDButton(
                            MDButtonText(text="Später"),
                            style="text",
                            on_release=lambda x: dialog.dismiss(),
                        ),
                        MDButton(
                            MDButtonText(text="Jetzt laden"),
                            style="text",
                            on_release=lambda x: _load_and_dismiss(app, filepath, dialog),
                        ),
                        spacing="8dp",
                    ),
                    size_hint=(0.85, None),
                )
                dialog.open()
            else:
                Logger.info(f"IntentHandler: Charakter importiert (kein Dialog-Service): {filename}")

        except Exception as e:
            Logger.error(f"IntentHandler: Fehler beim Anzeigen des Erfolgs-Dialogs: {e}")

    Clock.schedule_once(_show_dialog, 1.0)


def _load_and_dismiss(app, filepath, dialog):
    """Lädt den importierten Charakter und schließt den Dialog."""
    try:
        dialog.dismiss()
        if app.controller:
            success = app.controller.lade_charakter_von_json(filepath)
            if success:
                Logger.info(f"IntentHandler: Importierter Charakter geladen: {filepath}")
            else:
                Logger.error(f"IntentHandler: Fehler beim Laden des Charakters: {filepath}")
    except Exception as e:
        Logger.error(f"IntentHandler: Fehler beim Laden: {e}")


def _show_import_success_setting(app, filename):
    """Zeigt Erfolgs-Snackbar für importiertes Setting."""
    from kivy.clock import Clock

    def _show(dt):
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(
                    f"Setting '{filename}' importiert. Verfügbar nach Neustart."
                )
            else:
                Logger.info(f"IntentHandler: Setting importiert: {filename}")
        except Exception as e:
            Logger.error(f"IntentHandler: Fehler beim Anzeigen des Setting-Erfolgs: {e}")

    Clock.schedule_once(_show, 1.0)


def _show_import_error(app, message):
    """Zeigt Fehler-Dialog für fehlgeschlagenen Import."""
    from kivy.clock import Clock

    def _show(dt):
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog(f"Import fehlgeschlagen:\n{message}")
            else:
                Logger.error(f"IntentHandler: Import-Fehler: {message}")
        except Exception as e:
            Logger.error(f"IntentHandler: Fehler beim Anzeigen des Fehler-Dialogs: {e}")

    Clock.schedule_once(_show, 1.0)
