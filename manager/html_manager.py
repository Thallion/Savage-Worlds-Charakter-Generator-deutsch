# manager/html_manager.py
"""
HTML Manager für Charakterbogen-Export
Kapselt alle HTML-bezogenen Funktionalitäten (analog zu PDFManager)
"""

import webbrowser
import time
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from services.service_container import service_container


class HTMLManager:
    """Manager für HTML-bezogene Funktionalitäten"""

    def __init__(self, widget):
        self.widget = widget
        self.html_service = service_container.get_html_service()
        self.dialog_service = service_container.get_dialog_service()
        self.file_service = service_container.get_file_manager_service()

        # Dialog-Referenzen
        self.html_options_dialog = None
        self.printer_friendly_checkbox = None
        self.show_steigerungen_checkbox = None
        self.temp_printer_friendly = False
        self.temp_show_steigerungen = True

    def _on_printer_checkbox_clicked(self, instance, value):
        """Handler für Druckerfreundlich-Checkbox (on_active)."""
        self.temp_printer_friendly = value

    def _on_steigerungen_checkbox_clicked(self, instance, value):
        """Handler für Steigerungen-Checkbox (on_active)."""
        self.temp_show_steigerungen = value

    def create_character_html(self):
        """Startet den HTML-Erstellungsprozess mit Optionen"""
        if not self.html_service or not self.dialog_service:
            Logger.error("Erforderliche Services nicht verfügbar für HTML-Export")
            return

        # Prüfen, ob bereits eine HTML-Datei existiert
        exists, existing_path, existing_name = self.html_service.check_existing_html()

        # Dialog-Inhalt für HTML-Optionen erstellen
        content = self._create_html_options_content(exists, existing_name, existing_path)

        # Dialog erstellen und anzeigen
        self.html_options_dialog = MDDialog(
            MDDialogHeadlineText(text="HTML-Charakterbogen erstellen"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self.html_options_dialog.dismiss()
                )
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self.html_options_dialog.open()

    def _create_html_options_content(self, exists, existing_name, existing_path):
        """Erstellt den Inhalt für den HTML-Options-Dialog"""
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox

        # Höhe anpassen: mit existierender HTML brauchen wir mehr Platz
        # für Info-Label und Überschreiben-Button
        content_height = dp(320) if exists else dp(260)
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            height=content_height,
            padding=dp(16)
        )

        # Liste für Checkboxen
        checkbox_list = MDList(
            size_hint_y=None,
        )
        checkbox_list.bind(minimum_height=checkbox_list.setter('height'))

        # Checkbox für druckerfreundliche Version
        printer_item = MDListItem(
            size_hint_y=None,
            height=dp(48)
        )
        printer_item.add_widget(MDListItemSupportingText(
            text="Druckerfreundliche Version (ohne Farben)"
        ))
        self.printer_friendly_checkbox = MDListItemTrailingCheckbox()
        self.printer_friendly_checkbox.bind(on_active=self._on_printer_checkbox_clicked)
        printer_item.add_widget(self.printer_friendly_checkbox)
        checkbox_list.add_widget(printer_item)

        # Checkbox für Steigerungen einblenden
        steigerungen_item = MDListItem(
            size_hint_y=None,
            height=dp(48)
        )
        steigerungen_item.add_widget(MDListItemSupportingText(
            text="Steigerungen einblenden"
        ))
        self.show_steigerungen_checkbox = MDListItemTrailingCheckbox(
            active=True
        )
        self.show_steigerungen_checkbox.bind(on_active=self._on_steigerungen_checkbox_clicked)
        steigerungen_item.add_widget(self.show_steigerungen_checkbox)
        checkbox_list.add_widget(steigerungen_item)

        content.add_widget(checkbox_list)

        # Buttons - bei zwei Buttons mehr Höhe benötigt
        buttons_height = dp(100) if exists else dp(52)
        buttons_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            height=buttons_height
        )

        if exists:
            info_label = MDLabel(
                text=f"Bestehende HTML: {existing_name}",
                size_hint_y=None,
                height=dp(30)
            )
            content.add_widget(info_label)

            overwrite_btn = MDButton(
                style="elevated",
                size_hint=(1, None),
                height=dp(40),
                on_release=lambda x: self._create_html_at_path(existing_path, True)
            )
            overwrite_btn.add_widget(MDButtonText(text="Bestehende HTML überschreiben"))
            buttons_container.add_widget(overwrite_btn)

        new_html_btn = MDButton(
            style="elevated",
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self._start_new_html_creation()
        )
        new_html_btn.add_widget(MDButtonText(text="Als neue HTML speichern..."))
        buttons_container.add_widget(new_html_btn)

        content.add_widget(buttons_container)
        return content

    def _create_html_at_path(self, html_path, close_dialog=False):
        """Erstellt HTML am angegebenen Pfad und öffnet sie im Browser"""
        if close_dialog and self.html_options_dialog:
            self.html_options_dialog.dismiss()

        if self.html_service and self.dialog_service:
            is_printer_friendly = self.printer_friendly_checkbox.active if self.printer_friendly_checkbox else False
            show_steigerungen = self.show_steigerungen_checkbox.active if self.show_steigerungen_checkbox else True

            success = self.html_service.create_character_html(html_path, is_printer_friendly, show_steigerungen)

            if success:
                # HTML im Browser öffnen
                self._open_in_browser(html_path)

                self.dialog_service.show_success_dialog(
                    f"HTML gespeichert und im Browser geöffnet."
                )
            else:
                self.dialog_service.show_error_dialog("Fehler beim Erstellen der HTML-Datei.")

    def _start_new_html_creation(self):
        """Startet den Prozess für neue HTML-Erstellung"""
        if self.html_options_dialog:
            self.html_options_dialog.dismiss()

        if self.dialog_service and self.html_service:
            default_name = self.html_service.get_default_html_name()

            self.dialog_service.show_input_dialog(
                "Dateiname für neue HTML:",
                "Als neue HTML speichern",
                default_name,
                self._on_html_filename_entered
            )

    def _on_html_filename_entered(self, filename):
        """Verarbeitet den eingegebenen HTML-Dateinamen"""
        if not filename or not filename.strip():
            if self.dialog_service:
                self.dialog_service.show_error_dialog("Bitte gib einen Dateinamen ein.")
            return

        # HTML-Endung sicherstellen
        if not filename.lower().endswith('.html'):
            filename += '.html'

        self.temp_printer_friendly = self.printer_friendly_checkbox.active if self.printer_friendly_checkbox else False
        self.temp_show_steigerungen = self.show_steigerungen_checkbox.active if self.show_steigerungen_checkbox else True

        # FileManager Service für Verzeichnisauswahl
        if self.file_service:
            self.file_service.set_temp_html_settings(filename, self.temp_printer_friendly, self.temp_show_steigerungen)
            chars_dir = self.file_service.get_default_directory('chars')
            self.file_service.show_file_manager(chars_dir, "save_html_dir")

    # Klassen-Variable für den lokalen HTTP-Server (wird wiederverwendet)
    _http_server = None
    _http_server_port = None

    def _open_in_browser(self, html_path):
        """Öffnet die HTML-Datei im Standard-Browser (plattformspezifisch)"""
        try:
            import os
            from kivy.utils import platform as kivy_platform

            abs_path = os.path.abspath(html_path)

            if kivy_platform == 'android':
                self._open_file_on_android(abs_path, 'text/html')
            else:
                file_url = 'file://' + abs_path
                webbrowser.open(file_url)
                Logger.info(f"HTML-Datei im Browser geöffnet: {file_url}")
        except Exception as e:
            Logger.warning(f"Konnte HTML-Datei nicht im Browser öffnen: {e}")

    @staticmethod
    def _open_file_on_android(file_path, mime_type='*/*'):
        """Öffnet eine Datei auf Android über mehrere Fallback-Strategien.

        Für HTML-Dateien wird bevorzugt ein lokaler HTTP-Server gestartet und
        die Datei über webbrowser.open() mit http://localhost geöffnet.
        Das funktioniert zuverlässig auf allen Android-Versionen, da
        webbrowser.open() mit HTTP-URLs nachweislich funktioniert (wie im Info-Screen).
        """
        import os

        if not os.path.exists(file_path):
            Logger.error(f"Android: Datei nicht gefunden: {file_path}")
            return

        # Strategie 1: Lokaler HTTP-Server + webbrowser.open() (für HTML)
        # webbrowser.open() funktioniert auf Android mit HTTP-URLs einwandfrei
        if mime_type == 'text/html':
            try:
                HTMLManager._open_via_localhost(file_path)
                return
            except Exception as e:
                Logger.warning(f"Android: Localhost-Strategie fehlgeschlagen: {e}")

        # Strategie 2: Intent mit FileProvider (Android 7+)
        try:
            HTMLManager._open_with_fileprovider(file_path, mime_type)
            return
        except Exception as e:
            Logger.warning(f"Android: FileProvider fehlgeschlagen: {e}")

        # Strategie 3: Intent mit file:// URI (ältere Android-Versionen)
        try:
            HTMLManager._open_with_file_uri(file_path, mime_type)
            return
        except Exception as e:
            Logger.warning(f"Android: file:// URI fehlgeschlagen: {e}")

        # Strategie 4: Android Share-Intent als letzter Fallback
        try:
            HTMLManager._share_file_on_android(file_path, mime_type)
        except Exception as e:
            Logger.error(f"Android: Alle Öffnungs-Strategien fehlgeschlagen: {e}")

    @staticmethod
    def _open_via_localhost(file_path):
        """Öffnet eine HTML-Datei über einen lokalen HTTP-Server im Browser.

        Startet einen einfachen HTTP-Server im Hintergrund, der die Datei
        über http://localhost serviert. webbrowser.open() funktioniert auf
        Android zuverlässig mit HTTP-URLs (wie die Links im Info-Screen).
        """
        import os
        import threading
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        import urllib.parse

        abs_path = os.path.abspath(file_path)
        serve_dir = os.path.dirname(abs_path)
        filename = os.path.basename(abs_path)

        # Falls bereits ein Server läuft, diesen stoppen
        if HTMLManager._http_server is not None:
            try:
                HTMLManager._http_server.shutdown()
            except Exception:
                pass
            HTMLManager._http_server = None

        # Freien Port finden und Server starten
        server = HTTPServer(('127.0.0.1', 0), lambda *args, **kwargs:
            SimpleHTTPRequestHandler(*args, directory=serve_dir, **kwargs))
        port = server.server_address[1]

        HTMLManager._http_server = server
        HTMLManager._http_server_port = port

        # Server im Hintergrund-Thread starten
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        # URL zusammenbauen und im Browser öffnen
        encoded_name = urllib.parse.quote(filename)
        url = f"http://127.0.0.1:{port}/{encoded_name}"
        Logger.info(f"Android: HTML-Server gestartet auf Port {port}, öffne {url}")
        webbrowser.open(url)

        # Server nach 5 Minuten automatisch stoppen (Aufräumen)
        def auto_shutdown():
            import time
            time.sleep(300)
            try:
                if HTMLManager._http_server is server:
                    server.shutdown()
                    HTMLManager._http_server = None
                    Logger.info("Android: HTML-Server automatisch gestoppt")
            except Exception:
                pass

        cleanup_thread = threading.Thread(target=auto_shutdown, daemon=True)
        cleanup_thread.start()

    @staticmethod
    def _open_with_fileprovider(file_path, mime_type):
        """Öffnet eine Datei über FileProvider (bevorzugt auf Android 7+)"""
        from jnius import autoclass

        Intent = autoclass('android.content.Intent')
        File = autoclass('java.io.File')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        FileProvider = autoclass('androidx.core.content.FileProvider')

        context = PythonActivity.mActivity
        java_file = File(file_path)
        authority = context.getPackageName() + '.fileprovider'
        content_uri = FileProvider.getUriForFile(context, authority, java_file)

        intent = Intent(Intent.ACTION_VIEW)
        intent.setDataAndType(content_uri, mime_type)
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

        context.startActivity(intent)
        Logger.info(f"Android: Datei geöffnet via FileProvider: {file_path}")

    @staticmethod
    def _open_with_file_uri(file_path, mime_type):
        """Öffnet eine Datei über file:// URI (Fallback für ältere Android-Versionen)"""
        from jnius import autoclass

        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        File = autoclass('java.io.File')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        context = PythonActivity.mActivity
        java_file = File(file_path)
        content_uri = Uri.fromFile(java_file)

        intent = Intent(Intent.ACTION_VIEW)
        intent.setDataAndType(content_uri, mime_type)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

        context.startActivity(intent)
        Logger.info(f"Android: Datei geöffnet via file:// URI: {file_path}")

    @staticmethod
    def _share_file_on_android(file_path, mime_type):
        """Teilt eine Datei über Android Share-Intent (letzter Fallback)"""
        from jnius import autoclass
        import os

        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        File = autoclass('java.io.File')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        context = PythonActivity.mActivity
        java_file = File(file_path)

        # Versuche FileProvider für Share
        try:
            FileProvider = autoclass('androidx.core.content.FileProvider')
            authority = context.getPackageName() + '.fileprovider'
            content_uri = FileProvider.getUriForFile(context, authority, java_file)
        except Exception:
            content_uri = Uri.fromFile(java_file)

        intent = Intent(Intent.ACTION_SEND)
        intent.setType(mime_type)
        intent.putExtra(Intent.EXTRA_STREAM, content_uri)
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

        chooser = Intent.createChooser(intent, "Charakterbogen öffnen mit...")
        chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(chooser)
        Logger.info(f"Android: Datei geteilt via Share-Intent: {os.path.basename(file_path)}")
