# services/dialog_service.py
"""
Service für Dialog-Management und UI-Feedback
ERWEITERT: Zusätzliche Dialog-Typen, Element-Merging, Statistiken und Statblock-Funktionalität
"""

from kivy.logger import Logger
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
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

# Statblock Generator Import
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
    
    def show_info_dialog(self, message, title="Information"):
        """
        Zeigt einen Informationsdialog mit scrollbarem Inhalt
        
        Args:
            message (str): Informationstext
            title (str): Dialog-Titel
        """
        self._dismiss_dialog('info')
        
        # ScrollView für längere Texte
        scroll_view = MDScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            size_hint_y=None,
            height=dp(400)  # Feste Höhe für bessere Kontrolle
        )
        
        info_label = MDLabel(
            text=message,
            size_hint_y=None,
            text_size=(dp(400), None),  # Definiere Textbreite für Umbrüche
            halign="left",
            valign="top"
        )
        # Höhe basierend auf Textinhalt berechnen
        info_label.bind(texture_size=info_label.setter('size'))
        
        content.add_widget(info_label)
        scroll_view.add_widget(content)
        
        info_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(scroll_view),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self._dismiss_dialog('info')
                )
            ),
            md_bg_color=self.theme_cls.surfaceColor,
            size_hint=(0.8, 0.8)  # Größerer Dialog für mehr Inhalt
        )
        
        self.active_dialogs['info'] = info_dialog
        info_dialog.open()
        Logger.info(f"Dialog Info: {title}")
    
    def show_warning_dialog(self, message, title="Warnung"):
        """
        Zeigt einen Warnungsdialog
        
        Args:
            message (str): Warnungsnachricht
            title (str): Dialog-Titel
        """
        self._dismiss_dialog('warning')
        
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
        
        warning_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self._dismiss_dialog('warning')
                )
            ),
            md_bg_color=self.theme_cls.surfaceColor
        )
        
        self.active_dialogs['warning'] = warning_dialog
        warning_dialog.open()
        Logger.warning(f"Dialog Warning: {message}")
    
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
    
    def show_choice_dialog(self, message, title="Auswahl", choices=None, on_choice=None):
        """
        Zeigt einen Dialog mit mehreren Auswahloptionen
        
        Args:
            message (str): Hauptnachricht
            title (str): Dialog-Titel
            choices (list): Liste von Auswahloptionen [(text, value), ...]
            on_choice (callable): Callback bei Auswahl (erhält gewählten value)
        """
        if not choices:
            choices = [("OK", "ok")]
        
        self._dismiss_dialog('choice')
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(20),
            adaptive_height=True
        )
        
        # Hauptnachricht
        content.add_widget(MDLabel(
            text=message,
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        ))
        
        # Button-Container
        button_container = MDBoxLayout(
            orientation="vertical" if len(choices) > 3 else "horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48) if len(choices) <= 3 else dp(48 * len(choices)),
            adaptive_height=True
        )
        
        def handle_choice(choice_value):
            self._dismiss_dialog('choice')
            if on_choice:
                on_choice(choice_value)
        
        # Buttons für jede Auswahl erstellen
        for text, value in choices:
            choice_button = MDButton(
                style="elevated",
                size_hint_x=1 if len(choices) > 3 else None,
                width=dp(120) if len(choices) <= 3 else None,
                on_release=lambda x, v=value: handle_choice(v)
            )
            choice_button.add_widget(MDButtonText(text=text))
            button_container.add_widget(choice_button)
        
        content.add_widget(button_container)
        
        choice_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self._dismiss_dialog('choice')
                )
            ),
            md_bg_color=self.theme_cls.surfaceColor
        )
        
        self.active_dialogs['choice'] = choice_dialog
        choice_dialog.open()
    
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
    
    def show_multiline_input_dialog(self, message, title="Eingabe", default_text="", on_confirm=None, on_cancel=None):
        """
        Zeigt einen mehrzeiligen Eingabedialog
        
        Args:
            message (str): Eingabenachricht
            title (str): Dialog-Titel
            default_text (str): Standardtext
            on_confirm (callable): Callback bei Bestätigung (text wird übergeben)
            on_cancel (callable): Callback bei Abbruch
        """
        self._dismiss_dialog('multiline_input')
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(16),
            size_hint_y=None,
            height=dp(300)
        )
        
        content.add_widget(MDLabel(
            text=message,
            size_hint_y=None,
            height=dp(30)
        ))
        
        text_input = MDTextField(
            text=default_text,
            hint_text="Text eingeben...",
            mode="outlined",
            multiline=True,
            size_hint_y=1
        )
        content.add_widget(text_input)
        
        def handle_confirm():
            self._dismiss_dialog('multiline_input')
            if on_confirm:
                on_confirm(text_input.text)
        
        def handle_cancel():
            self._dismiss_dialog('multiline_input')
            if on_cancel:
                on_cancel()
        
        multiline_dialog = MDDialog(
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
            md_bg_color=self.theme_cls.surfaceColor,
            size_hint=(0.8, 0.7)
        )
        
        self.active_dialogs['multiline_input'] = multiline_dialog
        multiline_dialog.open()
    
    def show_progress_dialog(self, title="Verarbeitung...", message="Bitte warten..."):
        """
        Zeigt einen Fortschrittsdialog (ohne Abbrechen-Button)
        
        Args:
            title (str): Dialog-Titel
            message (str): Nachricht
            
        Returns:
            str: Dialog-Schlüssel für dismiss_dialog()
        """
        dialog_key = 'progress'
        self._dismiss_dialog(dialog_key)
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(20),
            size_hint_y=None,
            height=dp(100)
        )
        
        content.add_widget(MDLabel(
            text=message,
            size_hint_y=None,
            height=dp(40),
            halign="center"
        ))
        
        progress_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content),
            md_bg_color=self.theme_cls.surfaceColor,
            auto_dismiss=False  # Verhindert das Schließen durch Außenklick
        )
        
        self.active_dialogs[dialog_key] = progress_dialog
        progress_dialog.open()
        return dialog_key
    
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
    
    def show_setting_merge_dialog(self, setting_name, on_choice=None):
        """
        Zeigt einen Dialog für Setting-Wechsel mit Merge-Option
        
        Args:
            setting_name (str): Name des neuen Settings
            on_choice (callable): Callback mit gewählter Option
        """
        message = (f"Wie möchtest du zu Setting '{setting_name}' wechseln?\n\n"
                  "Zusammenführen: Behält deine ausgewählten Elemente und fügt neue hinzu\n"
                  "Ersetzen: Lädt das Setting komplett neu (ausgewählte Elemente gehen verloren)")
        
        choices = [
            ("Zusammenführen", "merge"),
            ("Ersetzen", "replace")
        ]
        
        self.show_choice_dialog(
            message=message,
            title="Setting-Wechsel",
            choices=choices,
            on_choice=on_choice
        )
    
    def show_element_statistics_dialog(self):
        """
        Zeigt Statistiken über die verfügbaren Elemente
        """
        if not self.controller or not self.controller.charakter:
            self.show_error_dialog("Kein Charakter verfügbar")
            return
        
        char = self.controller.charakter
        
        # Statistiken sammeln
        stats_text = f"""Aktives Setting: {char.active_setting_name}

ELEMENTE-ÜBERSICHT:

Völker: {len(char.voelker)} verfügbar
• Ausgewählt: {sum(1 for selected in char.voelker_selected.values() if selected)}

Handicaps: {len(char.handicaps)} verfügbar
• Ausgewählt: {len(char.selected_handicaps)}

Talente: {len(char.talente)} verfügbar
• Ausgewählt: {len(char.selected_talente)}

Mächte: {len(char.maechte)} verfügbar
• Ausgewählt: {len(char.selected_maechte)}
• Machtpunkte: {char.machtpunkte}

Fertigkeiten: {len(char.fertigkeiten)} verfügbar

Ausrüstung: {len(char.ausruestung)} verfügbar
• Waffen: {len(char.selected_waffen)} angelegt
• Rüstungen: {len(char.selected_ruestungen)} angelegt
• Schilde: {len(char.selected_schilde)} angelegt
• Gegenstände: {len(char.selected_allgemeine_ausruestung)} ausgewählt

CHARAKTER-STATUS:
• Name: {char.char_name}
• Rang: {char.rang} (Aufstiege: {char.aufstiege_gesamt})
• Vermögen: {char.vermoegen} {char.waehrungseinheit}"""
        
        self.show_info_dialog(stats_text, "Element-Statistiken")
    
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
    
    def dismiss_dialog(self, dialog_key):
        """
        Öffentliche Methode zum Schließen eines Dialogs
        
        Args:
            dialog_key (str): Schlüssel des Dialogs
        """
        self._dismiss_dialog(dialog_key)
    
    # Element-Dialog-Handler Methoden
    def open_add_volk_dialog(self):
        """Öffnet Dialog zum Hinzufügen eines Volkes"""
        try:
            self.volk_dialog_handler.show_add_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Volk-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Volk-Dialogs.")
    
    def open_delete_volk_dialog(self):
        """Öffnet Dialog zum Löschen eines Volkes"""
        try:
            self.volk_dialog_handler.show_delete_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Volk-Lösch-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Volk-Lösch-Dialogs.")
    
    def open_add_talent_popup(self):
        """Öffnet Dialog zum Hinzufügen eines Talents"""
        try:
            self.talent_dialog_handler.show_add_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Talent-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Talent-Dialogs.")
    
    def open_delete_talent_popup(self):
        """Öffnet Dialog zum Löschen eines Talents"""
        try:
            self.talent_dialog_handler.show_delete_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Talent-Lösch-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Talent-Lösch-Dialogs.")
    
    def open_add_macht_popup(self):
        """Öffnet Dialog zum Hinzufügen einer Macht"""
        try:
            self.macht_dialog_handler.show_add_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Macht-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Macht-Dialogs.")
    
    def open_delete_macht_popup(self):
        """Öffnet Dialog zum Löschen einer Macht"""
        try:
            self.macht_dialog_handler.show_delete_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Macht-Lösch-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Macht-Lösch-Dialogs.")
    
    def open_add_fertigkeit_popup(self):
        """Öffnet Dialog zum Hinzufügen einer Fertigkeit"""
        try:
            self.fertigkeit_dialog_handler.show_add_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Fertigkeit-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Fertigkeit-Dialogs.")
    
    def open_delete_fertigkeit_popup(self):
        """Öffnet Dialog zum Löschen einer Fertigkeit"""
        try:
            self.fertigkeit_dialog_handler.show_delete_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Fertigkeit-Lösch-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Fertigkeit-Lösch-Dialogs.")
    
    def open_add_handicap_popup(self):
        """Öffnet Dialog zum Hinzufügen eines Handicaps"""
        try:
            self.handicap_dialog_handler.show_add_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Handicap-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Handicap-Dialogs.")
    
    def open_delete_handicap_popup(self):
        """Öffnet Dialog zum Löschen eines Handicaps"""
        try:
            self.handicap_dialog_handler.show_delete_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Handicap-Lösch-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Handicap-Lösch-Dialogs.")
    
    def open_add_ausruestung_popup(self):
        """Öffnet Dialog zum Hinzufügen von Ausrüstung"""
        try:
            self.ausruestung_dialog_handler.show_add_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Ausrüstung-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Ausrüstung-Dialogs.")
    
    def open_delete_ausruestung_popup(self):
        """Öffnet Dialog zum Löschen von Ausrüstung"""
        try:
            self.ausruestung_dialog_handler.show_delete_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Ausrüstung-Lösch-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Ausrüstung-Lösch-Dialogs.")
    
    def open_add_waffe_popup(self):
        """Öffnet Dialog zum Hinzufügen einer Waffe"""
        try:
            self.waffe_dialog_handler.show_add_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Waffe-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Waffe-Dialogs.")
    
    def open_delete_waffe_popup(self):
        """Öffnet Dialog zum Löschen einer Waffe"""
        try:
            self.waffe_dialog_handler.show_delete_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Waffe-Lösch-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Waffe-Lösch-Dialogs.")
    
    def open_add_ruestung_popup(self):
        """Öffnet Dialog zum Hinzufügen einer Rüstung"""
        try:
            self.ruestung_dialog_handler.show_add_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Rüstung-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Rüstung-Dialogs.")
    
    def open_delete_ruestung_popup(self):
        """Öffnet Dialog zum Löschen einer Rüstung"""
        try:
            self.ruestung_dialog_handler.show_delete_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Rüstung-Lösch-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Rüstung-Lösch-Dialogs.")
    
    def open_add_schild_popup(self):
        """Öffnet Dialog zum Hinzufügen eines Schildes"""
        try:
            self.schild_dialog_handler.show_add_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Schild-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Schild-Dialogs.")
    
    def open_delete_schild_popup(self):
        """Öffnet Dialog zum Löschen eines Schildes"""
        try:
            self.schild_dialog_handler.show_delete_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Schild-Lösch-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Schild-Lösch-Dialogs.")
    
    def open_add_setting_popup(self):
        """Öffnet Dialog zum Hinzufügen eines Settings"""
        try:
            self.setting_dialog_handler.open_add_setting_popup()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Setting-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Setting-Dialogs.")
    
    def open_load_setting_popup(self):
        """Öffnet Dialog zum Laden eines Settings"""
        try:
            self.setting_dialog_handler.open_load_setting_popup()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Setting-Lade-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Setting-Lade-Dialogs.")
    
    def open_delete_setting_popup(self):
        """Öffnet Dialog zum Löschen eines Settings"""
        try:
            self.setting_dialog_handler.open_delete_setting_popup()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Setting-Lösch-Dialogs: {str(e)}")
            self.show_error_dialog("Fehler beim Öffnen des Setting-Lösch-Dialogs.")