# manager/html_manager.py
"""
HTML Manager für Charakterbogen-Export
Kapselt alle HTML-bezogenen Funktionalitäten (analog zu PDFManager)
"""

import webbrowser
import time
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
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

    def _on_printer_checkbox_clicked(self, checkbox):
        """Handler für Druckerfreundlich-Checkbox mit Debounce."""
        now = time.monotonic()
        if hasattr(self, '_last_printer_checkbox_time') and (now - self._last_printer_checkbox_time) < 0.5:
            return
        self._last_printer_checkbox_time = now
        self.temp_printer_friendly = checkbox.active

    def _on_steigerungen_checkbox_clicked(self, checkbox):
        """Handler für Steigerungen-Checkbox mit Debounce."""
        now = time.monotonic()
        if hasattr(self, '_last_steigerungen_checkbox_time') and (now - self._last_steigerungen_checkbox_time) < 0.5:
            return
        self._last_steigerungen_checkbox_time = now
        self.temp_show_steigerungen = checkbox.active

    def create_character_html(self):
        """Startet den HTML-Erstellungsprozess - zeigt zuerst Optionen-Popup"""
        if not self.html_service or not self.dialog_service:
            Logger.error("Erforderliche Services nicht verfügbar für HTML-Export")
            return

        # Temp-Werte zurücksetzen
        self.temp_printer_friendly = False
        self.temp_show_steigerungen = True

        # Zuerst Optionen-Popup für Checkboxen zeigen
        self._show_options_popup()

    def create_character_pdf_android(self):
        """Exportiert den Charakterbogen als PDF auf Android via PrintManager."""
        from kivy.utils import platform as kivy_platform

        if kivy_platform != 'android':
            Logger.warning("PDF-Export: Nur auf Android verfügbar")
            if self.dialog_service:
                self.dialog_service.show_warning_dialog(
                    "PDF-Export ist nur auf Android verfügbar."
                )
            return

        if not self.html_service or not self.dialog_service:
            Logger.error("Erforderliche Services nicht verfügbar für PDF-Export")
            return

        # Temp-Werte zurücksetzen
        self.temp_printer_friendly = False
        self.temp_show_steigerungen = True

        # Optionen-Popup mit PDF-Option zeigen
        self._show_pdf_options_popup()

    def _show_pdf_options_popup(self):
        """Zeigt Popup für PDF-Export-Optionen auf Android."""
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox
        from utils.android_print_utils import is_android

        if not is_android():
            Logger.warning("PDF-Optionen: Nur auf Android verfügbar")
            return

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(160),
            padding=dp(16)
        )

        checkbox_list = MDList(size_hint_y=None)
        checkbox_list.bind(minimum_height=checkbox_list.setter('height'))

        printer_item = MDListItem(size_hint_y=None, height=dp(48))
        printer_item.add_widget(MDListItemSupportingText(
            text="Druckerfreundliche Version (ohne Farben)"
        ))
        self.printer_friendly_checkbox = MDListItemTrailingCheckbox()
        cb = self.printer_friendly_checkbox
        self.printer_friendly_checkbox.bind(
            on_release=lambda x, cb=cb: self._on_printer_checkbox_clicked(cb)
        )
        printer_item.add_widget(self.printer_friendly_checkbox)
        checkbox_list.add_widget(printer_item)

        steigerungen_item = MDListItem(size_hint_y=None, height=dp(48))
        steigerungen_item.add_widget(MDListItemSupportingText(
            text="Steigerungen einblenden"
        ))
        self.show_steigerungen_checkbox = MDListItemTrailingCheckbox(active=True)
        cb2 = self.show_steigerungen_checkbox
        self.show_steigerungen_checkbox.bind(
            on_release=lambda x, cb=cb2: self._on_steigerungen_checkbox_clicked(cb)
        )
        steigerungen_item.add_widget(self.show_steigerungen_checkbox)
        checkbox_list.add_widget(steigerungen_item)

        scroll = MDScrollView(do_scroll_x=False, do_scroll_y=True, bar_width=dp(15))
        scroll.add_widget(checkbox_list)
        content.add_widget(scroll)

        self._options_popup = MDDialog(
            MDDialogHeadlineText(text="PDF-Export Optionen"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self._options_popup.dismiss()
                ),
                MDButton(
                    MDButtonText(text="PDF erstellen"),
                    style="filled",
                    on_release=lambda x: self._on_pdf_options_confirmed()
                ),
            ),
            size_hint=(0.85, None),
        )
        self._options_popup.open()

    def _on_pdf_options_confirmed(self):
        """Bestätigt PDF-Optionen und startet die PDF-Erstellung auf Android."""
        self.temp_printer_friendly = self.printer_friendly_checkbox.active if self.printer_friendly_checkbox else False
        self.temp_show_steigerungen = self.show_steigerungen_checkbox.active if self.show_steigerungen_checkbox else True
        self._options_popup.dismiss()

        self._create_pdf_on_android()

    def _show_options_popup(self):
        """Zeigt separates Popup für HTML-Export-Optionen (Checkboxen).

        Checkboxen werden in eigenem Popup mit eigenem ScrollView angezeigt,
        um Touch-Probleme auf Android zu vermeiden (analog zu Volkseigenarten-Popup).
        """
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(160),
            padding=dp(16)
        )

        checkbox_list = MDList(size_hint_y=None)
        checkbox_list.bind(minimum_height=checkbox_list.setter('height'))

        # Checkbox: Druckerfreundlich
        printer_item = MDListItem(size_hint_y=None, height=dp(48))
        printer_item.add_widget(MDListItemSupportingText(
            text="Druckerfreundliche Version (ohne Farben)"
        ))
        self.printer_friendly_checkbox = MDListItemTrailingCheckbox()
        cb = self.printer_friendly_checkbox
        self.printer_friendly_checkbox.bind(
            on_release=lambda x, cb=cb: self._on_printer_checkbox_clicked(cb)
        )
        printer_item.add_widget(self.printer_friendly_checkbox)
        checkbox_list.add_widget(printer_item)

        # Checkbox: Steigerungen
        steigerungen_item = MDListItem(size_hint_y=None, height=dp(48))
        steigerungen_item.add_widget(MDListItemSupportingText(
            text="Steigerungen einblenden"
        ))
        self.show_steigerungen_checkbox = MDListItemTrailingCheckbox(active=True)
        cb2 = self.show_steigerungen_checkbox
        self.show_steigerungen_checkbox.bind(
            on_release=lambda x, cb=cb2: self._on_steigerungen_checkbox_clicked(cb)
        )
        steigerungen_item.add_widget(self.show_steigerungen_checkbox)
        checkbox_list.add_widget(steigerungen_item)

        scroll = MDScrollView(do_scroll_x=False, do_scroll_y=True, bar_width=dp(15))
        scroll.add_widget(checkbox_list)
        content.add_widget(scroll)

        self._options_popup = MDDialog(
            MDDialogHeadlineText(text="HTML-Export Optionen"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self._options_popup.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Weiter"),
                    style="filled",
                    on_release=lambda x: self._on_options_confirmed()
                ),
            ),
            size_hint=(0.85, None),
        )
        self._options_popup.open()

    def _on_options_confirmed(self):
        """Übernimmt Checkbox-Werte und zeigt Speicher-Dialog"""
        self.temp_printer_friendly = self.printer_friendly_checkbox.active if self.printer_friendly_checkbox else False
        self.temp_show_steigerungen = self.show_steigerungen_checkbox.active if self.show_steigerungen_checkbox else True
        self._options_popup.dismiss()

        # Prüfen, ob bereits eine HTML-Datei existiert
        exists, existing_path, existing_name = self.html_service.check_existing_html()

        # Speicher-Dialog anzeigen (ohne Checkboxen)
        self._show_save_dialog(exists, existing_name, existing_path)

    def _show_save_dialog(self, exists, existing_name, existing_path):
        """Zeigt den Speicher-Dialog (überschreiben / neu speichern)"""
        content_height = dp(160) if exists else dp(100)
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            height=content_height,
            padding=dp(16)
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
            content.add_widget(overwrite_btn)

        new_html_btn = MDButton(
            style="elevated",
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self._start_new_html_creation()
        )
        new_html_btn.add_widget(MDButtonText(text="Als neue HTML speichern..."))
        content.add_widget(new_html_btn)

        # Button-Zeile manuell statt MDDialogButtonContainer (bessere Touch-Kompatibilität auf Android)
        button_row = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
        )
        button_row.add_widget(MDBoxLayout(size_hint_x=1))
        btn_cancel = MDButton(
            MDButtonText(text="Abbrechen"),
            style="text",
            on_release=lambda x: self._dismiss_save_dialog(),
        )
        button_row.add_widget(btn_cancel)
        content.add_widget(button_row)

        self.html_options_dialog = MDDialog(
            MDDialogHeadlineText(text="HTML-Charakterbogen erstellen"),
            MDDialogContentContainer(content),
            size_hint=(0.85, None),
        )
        self.html_options_dialog.open()

    def _close_html_options_dialog(self, clear_ref=True):
        """Schließt den HTML-Speicher-Dialog robust.

        Auf Android kann der Dialog in einem inkonsistenten Zustand hängen
        bleiben, wenn direkt nach dem dismiss() ein neuer Dialog geöffnet
        wird. Diese Methode ruft dismiss() auf und plant zusätzlich einen
        verzögerten zweiten Versuch, falls der erste dismiss() durch die
        Animation noch nicht wirksam war.

        Args:
            clear_ref (bool): Referenz nach dem Schließen auf None setzen.
                              Muss False sein, wenn der Dialog noch sichtbar
                              sein könnte (z. B. beim Abbrechen), damit ein
                              erneuter Schließen-Versuch möglich bleibt.
        """
        dialog = self.html_options_dialog
        if not dialog:
            return

        def _do_dismiss(*_):
            try:
                dialog.dismiss()
            except Exception as e:
                Logger.warning(f"Fehler beim Schließen des HTML-Dialogs: {e}")

        _do_dismiss()
        # Zweiter Versuch verzögert, falls der erste nicht gegriffen hat
        # (z. B. wegen Timing-Problemen der Dismiss-Animation auf Android).
        Clock.schedule_once(_do_dismiss, 0.15)

        if clear_ref:
            # Referenz erst nach den Dismiss-Versuchen löschen.
            Clock.schedule_once(lambda dt: setattr(self, 'html_options_dialog', None), 0.3)

    def _dismiss_save_dialog(self):
        """Schließt den Speicher-Dialog sicher (Abbrechen-Button)."""
        # Referenz NICHT sofort löschen, damit bei Bedarf weitere Dismiss-
        # Versuche möglich sind, falls der erste nicht gegriffen hat.
        self._close_html_options_dialog(clear_ref=False)

    def _create_html_at_path(self, html_path, close_dialog=False):
        """Erstellt HTML am angegebenen Pfad und öffnet sie im Browser"""
        if close_dialog:
            self._close_html_options_dialog()

        if self.html_service and self.dialog_service:
            is_printer_friendly = self.temp_printer_friendly
            show_steigerungen = self.temp_show_steigerungen

            success = self.html_service.create_character_html(html_path, is_printer_friendly, show_steigerungen)

            if success:
                # Falls der Dialog noch offen ist (z. B. weil dismiss nicht
                # zuverlässig gegriffen hat), nun sicher schließen.
                self._close_html_options_dialog()

                # HTML im Browser öffnen
                self._open_in_browser(html_path)

                self.dialog_service.show_success_dialog(
                    f"HTML gespeichert und im Browser geöffnet."
                )
            else:
                self.dialog_service.show_error_dialog("Fehler beim Erstellen der HTML-Datei.")

    def _start_new_html_creation(self):
        """Startet den Prozess für neue HTML-Erstellung.

        Der aktuelle Dialog wird zuerst geschlossen, dann wird der
        Eingabe-Dialog verzögert geöffnet, damit die Dismiss-Animation
        auf Android abgeschlossen werden kann (ansonsten kann der alte
        Dialog als "Geister-Modal" hängen bleiben und z. B. den Abbrechen-
        Button unbrauchbar machen).
        """
        self._close_html_options_dialog()

        if self.dialog_service and self.html_service:
            default_name = self.html_service.get_default_html_name()

            # Nächsten Dialog verzögert öffnen, damit der vorherige Dialog
            # sicher geschlossen ist (wichtig für Android-Touch-Handling).
            Clock.schedule_once(
                lambda dt: self.dialog_service.show_input_dialog(
                    "Dateiname für neue HTML:",
                    "Als neue HTML speichern",
                    default_name,
                    self._on_html_filename_entered
                ),
                0.2
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

        ANDROID-SICHERHEIT: Auf Android wird kein HTTP-Server-Thread verwendet,
        da threading.Thread JVM-Crashes verursachen kann. Stattdessen wird
        auf das android_print_utils.py System verwiesen.
        """
        import os
        from kivy.utils import platform as kivy_platform

        # Android: HTTP-Server-Threads vermeiden (JVM-Crash-Risiko).
        # Wir werfen eine Exception, damit der Aufrufer (_open_file_on_android)
        # auf die nächste Strategie fällt (FileProvider/Share-Intent).
        # `webbrowser.open("file://...")` löst auf Android ≥ 7 eine
        # FileUriExposedException aus und funktioniert nicht.
        if kivy_platform == 'android':
            Logger.warning(
                "HTMLManager: HTTP-Server auf Android deaktiviert (Thread-Safety). "
                "Fallback auf FileProvider/Share-Intent über android_print_utils.py"
            )
            raise RuntimeError("HTTP-Server auf Android deaktiviert")

        # Desktop: HTTP-Server wie bisher (thread-sicher)
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

        # Server im Hintergrund-Thread starten (nur Desktop)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        # URL zusammenbauen und im Browser öffnen
        encoded_name = urllib.parse.quote(filename)
        url = f"http://127.0.0.1:{port}/{encoded_name}"
        Logger.info(f"Desktop: HTML-Server gestartet auf Port {port}, öffne {url}")

        import webbrowser
        webbrowser.open(url)

        # Server nach 5 Minuten automatisch stoppen (Aufräumen - nur Desktop)
        def auto_shutdown():
            import time
            time.sleep(300)
            try:
                if HTMLManager._http_server is server:
                    server.shutdown()
                    HTMLManager._http_server = None
                    Logger.info("Desktop: HTML-Server automatisch gestoppt")
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

    def _create_pdf_on_android(self):
        """Erstellt HTML und konvertiert diese zu PDF auf Android."""
        if not self.html_service:
            Logger.error("PDF: HTML-Service nicht verfügbar")
            if self.dialog_service:
                self.dialog_service.show_error_dialog("PDF-Export fehlgeschlagen.")
            return

        charakter = self.html_service.controller.charakter
        char_name = charakter.char_name if hasattr(charakter, 'char_name') and charakter.char_name else "charakter"
        pdf_name = f"{char_name.strip().replace(' ', '_')}.pdf"

        from utils.android_print_utils import get_downloads_path

        downloads_dir = get_downloads_path()
        if not downloads_dir:
            Logger.error("PDF: Download-Verzeichnis nicht gefunden")
            if self.dialog_service:
                self.dialog_service.show_error_dialog("PDF-Export fehlgeschlagen: Kein Download-Ordner gefunden.")
            return

        import os
        html_path = os.path.join(downloads_dir, f"{char_name.strip().replace(' ', '_')}.html")
        pdf_path = os.path.join(downloads_dir, pdf_name)

        is_printer_friendly = self.temp_printer_friendly
        show_steigerungen = self.temp_show_steigerungen

        success = self.html_service.create_character_html(html_path, is_printer_friendly, show_steigerungen)

        if not success:
            Logger.error("PDF: HTML-Erstellung fehlgeschlagen")
            if self.dialog_service:
                self.dialog_service.show_error_dialog("PDF-Export fehlgeschlagen: HTML-Erstellung fehlgeschlagen.")
            return

        from utils.android_print_utils import print_html_to_pdf
        pdf_result = print_html_to_pdf(html_path, pdf_name)

        if pdf_result:
            Logger.info(f"Android Print: Druckdialog wird geöffnet, PDF-Name: {pdf_result}")
            if self.dialog_service:
                self.dialog_service.show_warning_dialog(
                    "Der Druckdialog wird geöffnet. Wählen Sie dort 'Als PDF speichern' aus.\n\n"
                    "Hinweis: Auf einigen Android-Geräten erscheint der Druckdialog möglicherweise im Hintergrund. "
                    "Prüfen Sie Ihre Benachrichtigungen oder wechseln Sie zur Drucker-App."
                )
        else:
            Logger.error("PDF: PDF-Erstellung fehlgeschlagen")
            if self.dialog_service:
                self.dialog_service.show_error_dialog(
                    "PDF-Export fehlgeschlagen.\n\n"
                    "Mögliche Ursachen:\n"
                    "• Keine Berechtigung zum Speichern von Dateien\n"
                    "• HTML-Datei konnte nicht geladen werden\n"
                    "• Druckdienst ist nicht verfügbar\n\n"
                    "Bitte überprüfen Sie die Logs für weitere Details."
                )
