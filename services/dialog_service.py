# services/dialog_service.py
"""
Service für Dialog-Management und UI-Feedback
ERWEITERT: Zusätzliche Dialog-Typen, Element-Merging, Statistiken und Statblock-Funktionalität
REPARIERT: Element-Statistiken funktionieren jetzt korrekt
KORRIGIERT: MDButton width=None Fehler für KivyMD 2.0.1
"""

from kivy.logger import Logger
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText, MDSnackbarSupportingText
from kivy.metrics import dp

# Dialog-Handler Imports
from views.volk_dialog_handler import VolkDialogHandler
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


def defocus_and_call(callback, *args):
    """Gibt den Fokus aller Textfelder frei und ruft den Callback verzögert auf.

    Auf Android konsumiert ein fokussiertes MDTextField die Touch-Events
    von Dialog-Buttons. Durch Window.release_all_keyboards() und eine
    kurze Verzögerung wird sichergestellt, dass der Button-Callback ausgeführt wird.

    Kann als Standalone-Funktion importiert werden:
        from services.dialog_service import defocus_and_call
    """
    from kivy.core.window import Window
    from kivy.clock import Clock
    Window.release_all_keyboards()
    Clock.schedule_once(lambda dt: callback(*args), 0.1)


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

    def show_snackbar(self, message, duration=3):
        """
        Zeigt eine nicht-blockierende Snackbar-Benachrichtigung am unteren Bildschirmrand.
        Für reine Informationen, die keine Benutzeraktion erfordern.

        Args:
            message (str): Anzuzeigende Nachricht
            duration (int): Anzeigedauer in Sekunden (Standard: 3)
        """
        try:
            snackbar = MDSnackbar(
                MDSnackbarText(text=message),
                y=dp(64),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
                duration=duration,
                auto_dismiss=True,
            )
            snackbar.open()
            Logger.info(f"Snackbar: {message}")
        except Exception as e:
            Logger.error(f"Snackbar-Fehler: {e} - Fallback auf Logger")

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
            md_bg_color=self.theme_cls.surfaceColor,
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        
        self.active_dialogs['error'] = error_dialog
        error_dialog.open()
        Logger.error(f"Dialog Error: {message}")
    
    def show_success_dialog(self, message, title="Erfolgreich"):
        """
        Zeigt eine Erfolgs-Snackbar (nicht-blockierend).
        Ersetzt den modalen Dialog für reine Bestätigungen.

        Args:
            message (str): Erfolgsnachricht
            title (str): Dialog-Titel (wird in Snackbar-Text integriert)
        """
        snackbar_text = f"{title}: {message}" if title != "Erfolgreich" else message
        self.show_snackbar(snackbar_text, duration=3)
    
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
            size_hint=(0.85, 0.6),
            auto_dismiss=False,
        )
        
        self.active_dialogs['info'] = info_dialog
        info_dialog.open()
        Logger.info(f"Dialog Info: {title}")
    
    def show_warning_dialog(self, message, title="Warnung"):
        """
        Zeigt eine Warn-Snackbar (nicht-blockierend, längere Anzeige).
        Ersetzt den modalen Dialog für Warnungen ohne Entscheidungsbedarf.

        Args:
            message (str): Warnungsnachricht
            title (str): Dialog-Titel (wird in Snackbar-Text integriert)
        """
        snackbar_text = f"{title}: {message}" if title != "Warnung" else message
        self.show_snackbar(snackbar_text, duration=4)
    
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
            md_bg_color=self.theme_cls.surfaceColor,
            size_hint=(0.85, None),
            auto_dismiss=False,
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
            # KORREKTUR: Korrekte Button-Erstellung für KivyMD 2.0.1
            if len(choices) > 3:
                # Vertikale Anordnung - size_hint_x verwenden
                choice_button = MDButton(
                    style="elevated",
                    size_hint_x=1,
                    on_release=lambda x, v=value: handle_choice(v)
                )
            else:
                # Horizontale Anordnung - feste Breite verwenden
                choice_button = MDButton(
                    style="elevated",
                    size_hint_x=None,
                    width=dp(120),
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
            md_bg_color=self.theme_cls.surfaceColor,
            size_hint=(0.85, None),
            auto_dismiss=False,
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
            mode="outlined",
            size_hint_y=None,
            height=dp(72)
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
                    on_release=lambda x: defocus_and_call(handle_cancel)
                ),
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: defocus_and_call(handle_confirm)
                )
            ),
            md_bg_color=self.theme_cls.surfaceColor,
            size_hint=(0.85, None),
            auto_dismiss=False,
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
                    on_release=lambda x: defocus_and_call(handle_cancel)
                ),
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: defocus_and_call(handle_confirm)
                )
            ),
            md_bg_color=self.theme_cls.surfaceColor,
            size_hint=(0.85, 0.5),
            auto_dismiss=False,
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
            size_hint=(0.75, None),
            auto_dismiss=False,
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
            on_release=lambda x: defocus_and_call(self._copy_statblock, statblock_text)
        )
        copy_button.add_widget(MDButtonText(text="Kopieren"))
        button_container.add_widget(copy_button)

        # Schließen-Button
        close_button = MDButton(
            style="text",
            size_hint_x=0.5,
            on_release=lambda x: defocus_and_call(self._dismiss_dialog, 'statblock')
        )
        close_button.add_widget(MDButtonText(text="Schließen"))
        button_container.add_widget(close_button)
        
        content.add_widget(button_container)
        
        statblock_dialog = MDDialog(
            MDDialogHeadlineText(text="Charakterstatblock"),
            MDDialogContentContainer(content),
            md_bg_color=self.theme_cls.surfaceColor,
            size_hint=(0.9, 0.7),
            auto_dismiss=False,
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
                "Statblock in Zwischenablage kopiert."
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
        Zeigt Statistiken über die verfügbaren Elemente - REPARIERT
        """
        try:
            # Bessere Verfügbarkeitsprüfung
            if not self.controller:
                self.show_error_dialog("Controller nicht verfügbar")
                Logger.error("Controller nicht verfügbar für Element-Statistiken")
                return
            
            if not hasattr(self.controller, 'charakter') or not self.controller.charakter:
                self.show_error_dialog("Kein Charakter verfügbar")
                Logger.error("Charakter nicht verfügbar für Element-Statistiken")
                return
            
            char = self.controller.charakter
            Logger.info(f"Erstelle Element-Statistiken für Charakter: {getattr(char, 'char_name', 'Unbenannt')}")
            
            # Statistiken sammeln mit Fehlerbehandlung
            try:
                # Sichere Zugriffe auf Charakterattribute
                active_setting = getattr(char, 'active_setting_name', 'Unbekannt')
                char_name = getattr(char, 'char_name', 'Unbenannt')
                rang = getattr(char, 'rang', 'Unbekannt')
                aufstiege = getattr(char, 'aufstiege_gesamt', 0)
                vermoegen = getattr(char, 'vermoegen', 0)
                waehrung = getattr(char, 'waehrungseinheit', 'Gold')
                machtpunkte = getattr(char, 'machtpunkte', 0)
                
                # Völker
                voelker = getattr(char, 'voelker', {})
                voelker_selected = getattr(char, 'voelker_selected', {})
                voelker_count = len(voelker)
                voelker_selected_count = sum(1 for selected in voelker_selected.values() if selected) if voelker_selected else 0
                
                # Handicaps
                handicaps = getattr(char, 'handicaps', {})
                selected_handicaps = getattr(char, 'selected_handicaps', [])
                handicaps_count = len(handicaps)
                handicaps_selected_count = len(selected_handicaps)
                
                # Talente
                talente = getattr(char, 'talente', {})
                selected_talente = getattr(char, 'selected_talente', [])
                talente_count = len(talente)
                talente_selected_count = len(selected_talente)
                
                # Mächte
                maechte = getattr(char, 'maechte', {})
                selected_maechte = getattr(char, 'selected_maechte', [])
                maechte_count = len(maechte)
                maechte_selected_count = len(selected_maechte)
                
                # Fertigkeiten
                fertigkeiten = getattr(char, 'fertigkeiten', {})
                fertigkeiten_count = len(fertigkeiten)
                
                # Ausrüstung
                ausruestung = getattr(char, 'ausruestung', {})
                selected_waffen = getattr(char, 'selected_waffen', [])
                selected_ruestungen = getattr(char, 'selected_ruestungen', [])
                selected_schilde = getattr(char, 'selected_schilde', [])
                selected_allgemeine = getattr(char, 'selected_allgemeine_ausruestung', [])
                
                ausruestung_count = len(ausruestung)
                waffen_selected_count = len(selected_waffen)
                ruestungen_selected_count = len(selected_ruestungen)
                schilde_selected_count = len(selected_schilde)
                allgemeine_selected_count = len(selected_allgemeine)
                
                # Statistiken-Text erstellen
                stats_text = f"""Aktives Setting: {active_setting}

ELEMENTE-ÜBERSICHT:

Völker: {voelker_count} verfügbar
• Ausgewählt: {voelker_selected_count}

Handicaps: {handicaps_count} verfügbar
• Ausgewählt: {handicaps_selected_count}

Talente: {talente_count} verfügbar
• Ausgewählt: {talente_selected_count}

Mächte: {maechte_count} verfügbar
• Ausgewählt: {maechte_selected_count}
• Machtpunkte: {machtpunkte}

Fertigkeiten: {fertigkeiten_count} verfügbar

Ausrüstung: {ausruestung_count} verfügbar
• Waffen: {waffen_selected_count} angelegt
• Rüstungen: {ruestungen_selected_count} angelegt
• Schilde: {schilde_selected_count} angelegt
• Gegenstände: {allgemeine_selected_count} ausgewählt

CHARAKTER-STATUS:
• Name: {char_name}
• Rang: {rang} (Aufstiege: {aufstiege})
• Vermögen: {vermoegen} {waehrung}"""
                
                Logger.info(f"Element-Statistiken erstellt: {len(stats_text)} Zeichen")
                
            except Exception as e:
                Logger.error(f"Fehler beim Sammeln der Statistiken: {str(e)}", exc_info=True)
                stats_text = f"Fehler beim Sammeln der Charakterstatistiken: {str(e)}"
            
            # Verbesserten Dialog erstellen
            self._show_improved_info_dialog(stats_text, "Element-Statistiken")
            
        except Exception as e:
            Logger.error(f"Kritischer Fehler bei Element-Statistiken: {str(e)}", exc_info=True)
            self.show_error_dialog(f"Unerwarteter Fehler: {str(e)}")

    def _show_improved_info_dialog(self, message, title="Information"):
        """
        Verbesserte Version des Info-Dialogs mit besserer Textanzeige
        
        Args:
            message (str): Informationstext
            title (str): Dialog-Titel
        """
        self._dismiss_dialog('info')
        
        # Container für den Dialog-Inhalt
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(20),
            size_hint_y=None,
            height=dp(500)  # Ausreichend Höhe für den Inhalt
        )
        
        # Scrollbarer Textbereich
        scroll_view = MDScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        # Text-Container
        text_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(16),
            spacing=dp(8)
        )
        text_container.bind(minimum_height=text_container.setter('height'))
        
        # Text-Label mit fester Breite und adaptiver Höhe
        info_label = MDLabel(
            text=message,
            size_hint_y=None,
            text_size=(dp(450), None),  # Feste Textbreite für Umbrüche
            halign="left",
            valign="top",
            markup=False,  # Kein Markup für bessere Darstellung
            font_size="14sp"
        )
        
        # Höhe basierend auf Textinhalt automatisch anpassen
        def update_label_height(instance, texture_size):
            instance.height = texture_size[1]
        
        info_label.bind(texture_size=update_label_height)
        
        # Komponenten zusammenfügen
        text_container.add_widget(info_label)
        scroll_view.add_widget(text_container)
        content.add_widget(scroll_view)
        
        # Dialog erstellen
        info_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self._dismiss_dialog('info')
                )
            ),
            md_bg_color=self.theme_cls.surfaceColor,
            size_hint=(0.9, 0.6),
            auto_dismiss=False,
        )
        
        self.active_dialogs['info'] = info_dialog
        info_dialog.open()
        Logger.info(f"Verbesserter Info-Dialog '{title}' geöffnet")

    def debug_character_data(self):
        """
        Debug-Methode zur Überprüfung der Charakter-Daten
        """
        try:
            if not self.controller or not self.controller.charakter:
                Logger.error("Debug: Kein Controller oder Charakter verfügbar")
                return
            
            char = self.controller.charakter
            Logger.debug("=== CHARAKTER DEBUG-INFO ===")
            Logger.debug(f"Charakter-Name: {getattr(char, 'char_name', 'NICHT VERFÜGBAR')}")
            Logger.debug(f"Aktives Setting: {getattr(char, 'active_setting_name', 'NICHT VERFÜGBAR')}")
            Logger.debug(f"Völker verfügbar: {len(getattr(char, 'voelker', {}))}")
            Logger.debug(f"Handicaps verfügbar: {len(getattr(char, 'handicaps', {}))}")
            Logger.debug(f"Talente verfügbar: {len(getattr(char, 'talente', {}))}")
            Logger.debug(f"Mächte verfügbar: {len(getattr(char, 'maechte', {}))}")
            Logger.debug(f"Ausrüstung verfügbar: {len(getattr(char, 'ausruestung', {}))}")
            Logger.debug("=== END DEBUG-INFO ===")
            
        except Exception as e:
            Logger.error(f"Fehler beim Debug: {str(e)}", exc_info=True)
    
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