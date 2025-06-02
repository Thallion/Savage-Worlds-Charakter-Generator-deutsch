# services/dialog_service.py
"""
Service für Dialog-Management und UI-Feedback
"""

from kivy.logger import Logger
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp

# Dialog-Handler Imports
from views.volk_popup import VolkDialogHandler
from views.macht_popup import MachtDialogHandler
from views.schild_popup import SchildDialogHandler
from views.waffe_popup import WaffeDialogHandler
from views.fertigkeit_popup import FertigkeitDialogHandler
from views.ruestung_popup import RuestungDialogHandler
from views.ausruestung_popup import AusruestungDialogHandler
from views.handicap_popup import HandicapDialogHandler
from views.talent_popup import TalentDialogHandler
from views.setting_popup import SettingDialogHandler

# Funktionen
from functions.statblock_generator import generate_character_statblock, copy_statblock_to_clipboard

class DialogService:
    """Service für Dialog-Management und Benutzer-Feedback"""
    
    def __init__(self, controller, theme_cls):
        self.controller = controller
        self.theme_cls = theme_cls
        
        # Dialog-Handler initialisieren
        self._initialize_dialog_handlers()
        
        # Aktuelle Dialoge verfolgen
        self.active_dialogs = {}
    
    def _initialize_dialog_handlers(self):
        """Initialisiert alle Dialog-Handler"""
        self.volk_dialog_handler = VolkDialogHandler(self.controller)
        self.macht_dialog_handler = MachtDialogHandler(self.controller)
        self.schild_dialog_handler = SchildDialogHandler(self.controller)
        self.talent_dialog_handler = TalentDialogHandler(self.controller)
        self.handicap_dialog_handler = HandicapDialogHandler(self.controller)
        self.ruestung_dialog_handler = RuestungDialogHandler(self.controller)
        self.ausruestung_dialog_handler = AusruestungDialogHandler(self.controller)
        self.waffe_dialog_handler = WaffeDialogHandler(self.controller)
        self.fertigkeit_dialog_handler = FertigkeitDialogHandler(self.controller)
        self.setting_dialog_handler = SettingDialogHandler(self.controller)
    
    def show_error_dialog(self, message, title="Fehler"):
        """
        Zeigt einen Fehlerdialog
        
        Args:
            message (str): Fehlernachricht
            title (str): Dialog-Titel
        """
        self._dismiss_dialog('error')
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        content.add_widget(MDLabel(
            text=message,
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        ))
        
        error_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self._dismiss_dialog('error')
                )
            ),
            md_bg_color=self.theme_cls.surfaceColor
        )
        
        self.active_dialogs['error'] = error_dialog
        error_dialog.open()
        Logger.error(f"Dialog Error: {message}")
    
    def show_success_dialog(self, message, title="Erfolgreich"):
        """
        Zeigt einen Erfolgsdialog
        
        Args:
            message (str): Erfolgsnachricht
            title (str): Dialog-Titel
        """
        self._dismiss_dialog('success')
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        content.add_widget(MDLabel(
            text=message,
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        ))
        
        success_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self._dismiss_dialog('success')
                )
            ),
            md_bg_color=self.theme_cls.surfaceColor
        )
        
        self.active_dialogs['success'] = success_dialog
        success_dialog.open()
        Logger.info(f"Dialog Success: {title} - {message}")
    
    def show_confirmation_dialog(self, message, title="Bestätigung", on_confirm=None, on_cancel=None):
        """
        Zeigt einen Bestätigungsdialog
        
        Args:
            message (str): Bestätigungsnachricht
            title (str): Dialog-Titel
            on_confirm (callable): Callback bei Bestätigung
            on_cancel (callable): Callback bei Abbruch
        """
        self._dismiss_dialog('confirmation')
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        content.add_widget(MDLabel(
            text=message,
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        ))
        
        def handle_confirm():
            self._dismiss_dialog('confirmation')
            if on_confirm:
                on_confirm()
        
        def handle_cancel():
            self._dismiss_dialog('confirmation')
            if on_cancel:
                on_cancel()
        
        confirmation_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: handle_cancel()
                ),
                MDButton(
                    MDButtonText(text="Bestätigen"),
                    style="text",
                    on_release=lambda x: handle_confirm()
                )
            ),
            md_bg_color=self.theme_cls.surfaceColor
        )
        
        self.active_dialogs['confirmation'] = confirmation_dialog
        confirmation_dialog.open()
    
    def show_input_dialog(self, message, title="Eingabe", default_text="", on_confirm=None, on_cancel=None):
        """
        Zeigt einen Eingabedialog
        
        Args:
            message (str): Eingabenachricht
            title (str): Dialog-Titel
            default_text (str): Standardtext
            on_confirm (callable): Callback bei Bestätigung (text wird übergeben)
            on_cancel (callable): Callback bei Abbruch
        """
        self._dismiss_dialog('input')
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(16),
            adaptive_height=True
        )
        
        content.add_widget(MDLabel(
            text=message,
            size_hint_y=None,
            height=dp(30)
        ))
        
        text_input = MDTextField(
            text=default_text,
            hint_text="Text eingeben...",
            mode="outlined"
        )
        content.add_widget(text_input)
        
        def handle_confirm():
            self._dismiss_dialog('input')
            if on_confirm:
                on_confirm(text_input.text)
        
        def handle_cancel():
            self._dismiss_dialog('input')
            if on_cancel:
                on_cancel()
        
        input_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: handle_cancel()
                ),
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: handle_confirm()
                )
            ),
            md_bg_color=self.theme_cls.surfaceColor
        )
        
        self.active_dialogs['input'] = input_dialog
        input_dialog.open()
    
    def _dismiss_dialog(self, dialog_key):
        """
        Schließt einen spezifischen Dialog
        
        Args:
            dialog_key (str): Schlüssel des zu schließenden Dialogs
        """
        if dialog_key in self.active_dialogs:
            dialog = self.active_dialogs[dialog_key]
            if dialog:
                dialog.dismiss()
            del self.active_dialogs[dialog_key]
    
    def dismiss_all_dialogs(self):
        """Schließt alle aktiven Dialoge"""
        for dialog_key in list(self.active_dialogs.keys()):
            self._dismiss_dialog(dialog_key)
    
    # Element-Dialog-Handler Methoden
    def open_add_volk_dialog(self):
        """Öffnet Dialog zum Hinzufügen eines Volkes"""
        self.volk_dialog_handler.show_add_dialog()
    
    def open_delete_volk_dialog(self):
        """Öffnet Dialog zum Löschen eines Volkes"""
        self.volk_dialog_handler.show_delete_dialog()
    
    def open_add_talent_popup(self):
        """Öffnet Dialog zum Hinzufügen eines Talents"""
        self.talent_dialog_handler.show_add_dialog()
    
    def open_delete_talent_popup(self):
        """Öffnet Dialog zum Löschen eines Talents"""
        self.talent_dialog_handler.show_delete_dialog()
    
    def open_add_macht_popup(self):
        """Öffnet Dialog zum Hinzufügen einer Macht"""
        self.macht_dialog_handler.show_add_dialog()
    
    def open_delete_macht_popup(self):
        """Öffnet Dialog zum Löschen einer Macht"""
        self.macht_dialog_handler.show_delete_dialog()
    
    def open_add_fertigkeit_popup(self):
        """Öffnet Dialog zum Hinzufügen einer Fertigkeit"""
        self.fertigkeit_dialog_handler.show_add_dialog()
    
    def open_delete_fertigkeit_popup(self):
        """Öffnet Dialog zum Löschen einer Fertigkeit"""
        self.fertigkeit_dialog_handler.show_delete_dialog()
    
    def open_add_handicap_popup(self):
        """Öffnet Dialog zum Hinzufügen eines Handicaps"""
        self.handicap_dialog_handler.show_add_dialog()
    
    def open_delete_handicap_popup(self):
        """Öffnet Dialog zum Löschen eines Handicaps"""
        self.handicap_dialog_handler.show_delete_dialog()
    
    def open_add_ausruestung_popup(self):
        """Öffnet Dialog zum Hinzufügen von Ausrüstung"""
        self.ausruestung_dialog_handler.show_add_dialog()
    
    def open_delete_ausruestung_popup(self):
        """Öffnet Dialog zum Löschen von Ausrüstung"""
        self.ausruestung_dialog_handler.show_delete_dialog()
    
    def open_add_waffe_popup(self):
        """Öffnet Dialog zum Hinzufügen einer Waffe"""
        self.waffe_dialog_handler.show_add_dialog()
    
    def open_delete_waffe_popup(self):
        """Öffnet Dialog zum Löschen einer Waffe"""
        self.waffe_dialog_handler.show_delete_dialog()
    
    def open_add_ruestung_popup(self):
        """Öffnet Dialog zum Hinzufügen einer Rüstung"""
        self.ruestung_dialog_handler.show_add_dialog()
    
    def open_delete_ruestung_popup(self):
        """Öffnet Dialog zum Löschen einer Rüstung"""
        self.ruestung_dialog_handler.show_delete_dialog()
    
    def open_add_schild_popup(self):
        """Öffnet Dialog zum Hinzufügen eines Schildes"""
        self.schild_dialog_handler.show_add_dialog()
    
    def open_delete_schild_popup(self):
        """Öffnet Dialog zum Löschen eines Schildes"""
        self.schild_dialog_handler.show_delete_dialog()
    
    def open_add_setting_popup(self):
        """Öffnet Dialog zum Hinzufügen eines Settings"""
        self.setting_dialog_handler.open_add_setting_popup()
    
    def open_load_setting_popup(self):
        """Öffnet Dialog zum Laden eines Settings"""
        self.setting_dialog_handler.open_load_setting_popup()
    
    def open_delete_setting_popup(self):
        """Öffnet Dialog zum Löschen eines Settings"""
        self.setting_dialog_handler.open_delete_setting_popup()

    def show_statblock_dialog(self):
        """
        Zeigt einen Dialog mit dem Charakterstatblock
        """
        if not self.controller or not self.controller.charakter:
            self.show_error_dialog("Kein Charakter verfügbar")
            return
        
        # Statblock generieren
        statblock_text = generate_character_statblock(self.controller.charakter)
        
        self._dismiss_dialog('statblock')
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(20),
            adaptive_height=True
        )
        
        # Scrollbarer Text für den Statblock
        from kivymd.uix.textfield import MDTextField
        text_field = MDTextField(
            text=statblock_text,
            multiline=True,
            readonly=True,
            mode="outlined",
            size_hint_y=None,
            height=dp(300),
            md_bg_color=self.theme_cls.surfaceColor
        )
        content.add_widget(text_field)
        
        # Button-Container
        button_container = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(48)
        )
        
        # Kopieren-Button
        copy_button = MDButton(
            style="elevated",
            size_hint_x=0.5,
            on_release=lambda x: self._copy_statblock(statblock_text)
        )
        copy_button.add_widget(MDButtonText(text="Kopieren"))
        button_container.add_widget(copy_button)
        
        # Schließen-Button
        close_button = MDButton(
            style="text",
            size_hint_x=0.5,
            on_release=lambda x: self._dismiss_dialog('statblock')
        )
        close_button.add_widget(MDButtonText(text="Schließen"))
        button_container.add_widget(close_button)
        
        content.add_widget(button_container)
        
        statblock_dialog = MDDialog(
            MDDialogHeadlineText(text="Charakterstatblock"),
            MDDialogContentContainer(content),
            md_bg_color=self.theme_cls.surfaceColor
        )
        
        self.active_dialogs['statblock'] = statblock_dialog
        statblock_dialog.open()

    def _copy_statblock(self, statblock_text):
        """
        Kopiert den Statblock in die Zwischenablage
        
        Args:
            statblock_text (str): Der zu kopierende Text
        """
        success = copy_statblock_to_clipboard(statblock_text)
        
        if success:
            self.show_success_dialog(
                "Der Statblock wurde in die Zwischenablage kopiert.",
                "Kopiert"
            )
        else:
            self.show_error_dialog(
                "Fehler beim Kopieren in die Zwischenablage.\n"
                "Bitte markiere den Text manuell und kopiere ihn."
            )        