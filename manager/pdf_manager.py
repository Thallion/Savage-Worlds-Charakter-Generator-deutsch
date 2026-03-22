# views/pdf_manager.py
"""
PDF Manager für Einstellungen-Widget
Kapselt alle PDF-bezogenen Funktionalitäten
"""

from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from services.service_container import service_container
from services.event_service import EventTypes


class PDFManager:
    """Manager für PDF-bezogene Funktionalitäten"""
    
    def __init__(self, widget):
        self.widget = widget
        self.pdf_service = service_container.get_pdf_service()
        self.dialog_service = service_container.get_dialog_service()
        self.file_service = service_container.get_file_manager_service()
        self.event_service = service_container.get_event_service()
        
        # Dialog-Referenzen
        self.pdf_options_dialog = None
        self.printer_friendly_checkbox = None
        self.temp_printer_friendly = False
    
    def create_character_pdf(self):
        """Startet den PDF-Erstellungsprozess mit Optionen"""
        if not self.pdf_service or not self.dialog_service:
            Logger.error("Erforderliche Services nicht verfügbar")
            return
        
        # Prüfe ob PDF-Erstellung auf der aktuellen Plattform unterstützt wird
        if not self.pdf_service.is_pdf_supported():
            platform_info = self.pdf_service.get_platform_info()
            self._show_platform_not_supported_dialog(platform_info)
            return
        
        # Prüfen, ob bereits eine PDF-Datei existiert
        exists, existing_path, existing_name = self.pdf_service.check_existing_pdf()
        
        # Dialog-Inhalt für PDF-Optionen erstellen
        content = self._create_pdf_options_content(exists, existing_name, existing_path)
        
        # Dialog erstellen und anzeigen
        self.pdf_options_dialog = MDDialog(
            MDDialogHeadlineText(text="PDF erstellen"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self.pdf_options_dialog.dismiss()
                )
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self.pdf_options_dialog.open()
    
    def _create_pdf_options_content(self, exists, existing_name, existing_path):
        """Erstellt den Inhalt für den PDF-Options-Dialog"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            size_hint_y=None,
            height=dp(200),
            padding=dp(16)
        )
        
        # Checkbox für druckerfreundliche Version
        checkbox_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(16),
            size_hint_y=None,
            height=dp(48)
        )
        
        self.printer_friendly_checkbox = MDCheckbox(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={"center_y": .5}
        )
        
        checkbox_container.add_widget(self.printer_friendly_checkbox)
        checkbox_container.add_widget(MDLabel(
            text="Druckerfreundliche Version (ohne Hintergrund)",
            size_hint_x=1,
            pos_hint={"center_y": .5}
        ))
        
        content.add_widget(checkbox_container)
        
        # Buttons für verschiedene Optionen
        buttons_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            height=dp(100)
        )
        
        # Wenn bestehende PDF vorhanden
        if exists:
            info_label = MDLabel(
                text=f"Bestehende PDF: {existing_name}",
                size_hint_y=None,
                height=dp(30)
            )
            content.add_widget(info_label)
            
            # Überschreiben-Button
            overwrite_btn = MDButton(
                style="elevated",
                size_hint=(1, None),
                height=dp(40),
                on_release=lambda x: self._create_pdf_at_path(existing_path, True)
            )
            overwrite_btn.add_widget(MDButtonText(text="Bestehende PDF überschreiben"))
            buttons_container.add_widget(overwrite_btn)
        
        # Neue PDF erstellen Button
        new_pdf_btn = MDButton(
            style="elevated", 
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self._start_new_pdf_creation()
        )
        new_pdf_btn.add_widget(MDButtonText(text="Als neue PDF speichern..."))
        buttons_container.add_widget(new_pdf_btn)
        
        content.add_widget(buttons_container)
        return content
    
    def _create_pdf_at_path(self, pdf_path, close_dialog=False):
        """Erstellt PDF am angegebenen Pfad"""
        if close_dialog and self.pdf_options_dialog:
            self.pdf_options_dialog.dismiss()
        
        if self.pdf_service and self.dialog_service:
            is_printer_friendly = self.printer_friendly_checkbox.active if self.printer_friendly_checkbox else False
            
            success = self.pdf_service.create_character_pdf(pdf_path, is_printer_friendly)
            
            if success:
                if self.event_service:
                    self.event_service.publish(EventTypes.PDF_CREATED, {'path': pdf_path})
                
                self.dialog_service.show_success_dialog(
                    f"PDF wurde gespeichert als:\n{pdf_path}",
                    "PDF erstellen erfolgreich"
                )
            else:
                self.dialog_service.show_error_dialog("Fehler beim Erstellen der PDF-Datei.")
    
    def _start_new_pdf_creation(self):
        """Startet den Prozess für neue PDF-Erstellung"""
        if self.pdf_options_dialog:
            self.pdf_options_dialog.dismiss()
        
        if self.dialog_service and self.pdf_service:
            default_name = self.pdf_service.get_default_pdf_name()
            
            self.dialog_service.show_input_dialog(
                "Dateiname für neue PDF:",
                "Als neue PDF speichern",
                default_name,
                self._on_pdf_filename_entered
            )
    
    def _on_pdf_filename_entered(self, filename):
        """Verarbeitet den eingegebenen PDF-Dateinamen"""
        if not filename or not filename.strip():
            if self.dialog_service:
                self.dialog_service.show_error_dialog("Bitte gib einen Dateinamen ein.")
            return
        
        # PDF-Endung sicherstellen
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        # Checkbox-Status merken für später
        self.temp_printer_friendly = self.printer_friendly_checkbox.active if self.printer_friendly_checkbox else False
        
        # FileManager Service für Verzeichnisauswahl
        if self.file_service:
            self.file_service.set_temp_pdf_settings(filename, self.temp_printer_friendly)
            chars_dir = self.file_service.get_default_directory('chars')
            self.file_service.show_file_manager(chars_dir, "save_pdf_dir")
    
    def _show_platform_not_supported_dialog(self, platform_info):
        """Zeigt Dialog für nicht unterstützte Plattform mit HTML-Alternative"""
        if not self.dialog_service:
            Logger.error("Dialog-Service nicht verfügbar für Plattform-Warnung")
            return

        platform_name = "Android" if platform_info.get('is_android') else "Unbekannte Plattform"

        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            height=dp(150),
            padding=dp(16)
        )

        content.add_widget(MDLabel(
            text=f"PDF-Erstellung ist auf {platform_name} nicht verfügbar.\n\n"
                 f"Du kannst stattdessen einen HTML-Charakterbogen erstellen, "
                 f"der im Browser geöffnet wird.",
            size_hint_y=None,
            height=dp(80)
        ))

        html_btn = MDButton(
            style="elevated",
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self._redirect_to_html_export()
        )
        html_btn.add_widget(MDButtonText(text="HTML-Charakterbogen erstellen"))
        content.add_widget(html_btn)

        self._platform_dialog = MDDialog(
            MDDialogHeadlineText(text="PDF-Erstellung nicht verfügbar"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self._platform_dialog.dismiss()
                )
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self._platform_dialog.open()

    def _redirect_to_html_export(self):
        """Leitet zum HTML-Export weiter"""
        if hasattr(self, '_platform_dialog') and self._platform_dialog:
            self._platform_dialog.dismiss()

        # HTMLManager über das Widget aufrufen
        if hasattr(self.widget, 'html_manager') and self.widget.html_manager:
            self.widget.html_manager.create_character_html()
        else:
            Logger.error("HTMLManager nicht verfügbar für HTML-Export-Redirect")