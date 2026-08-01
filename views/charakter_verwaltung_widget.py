# views/charakter_verwaltung_widget.py
"""
CharakterVerwaltungWidget - Ausgegliedert aus EinstellungenWidget
Verantwortlich für: Charakter-CRUD, PDF-Export, Statblock,
                    Charakter-Einstellungen (Punkte, Vermögen, Aufstieg/Abstieg),
                    Setting-Verwaltung
"""

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon, MDListItemTrailingCheckbox
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import BooleanProperty
from pathlib import Path

# Mixins mit den ausgelagerten Subsystemen
from views.charakter_verwaltung_versand import CharakterVersandMixin
from views.charakter_verwaltung_export import CharakterbogenExportMixin
from views.charakter_verwaltung_config import CharakterConfigMixin

# Handler imports
from controllers.character_handler import CharacterHandler
from controllers.game_elements_handler import GameElementsHandler

# Service imports
from services.service_container import service_container, get_event_service
from services.event_service import EventTypes

# Manager imports
from manager.statistics_manager import StatisticsManager
from manager.pdf_manager import PDFManager
from manager.html_manager import HTMLManager

# File Manager
from utils.custom_filemanager import CustomFileManager

# KV-Datei laden mit Mobile-Unterstützung
from utils.path_utils import get_application_root, safe_filename_stem
from utils.platform_utils import is_mobile_layout, landscape_height
import os

_base_path = str(get_application_root())
_mobile = is_mobile_layout()
_kv_name = 'charakter_verwaltung_widget_mobile.kv' if _mobile else 'charakter_verwaltung_widget.kv'
_kv_path = os.path.join(_base_path, 'views', _kv_name)

# Fallback auf Desktop-KV wenn Mobile-KV nicht existiert
if not os.path.exists(_kv_path):
    _kv_path = os.path.join(_base_path, 'views', 'charakter_verwaltung_widget.kv')

Builder.load_file(_kv_path)
Logger.info(f"charakter_verwaltung_widget: KV-Datei geladen: {os.path.basename(_kv_path)}")


class CharakterVerwaltungWidget(CharakterVersandMixin, CharakterbogenExportMixin,
                                CharakterConfigMixin, MDBoxLayout):
    """
    Widget für Charakterverwaltung - ausgegliedert aus EinstellungenWidget
    Fokussiert auf: Charakter-CRUD, PDF-Export, Statblock,
                    Charakter-Einstellungen, Setting-Verwaltung
    """

    char_gen_completed = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

        # Handler initialisieren
        self._initialize_handlers()

        # Manager initialisieren
        self._initialize_managers()

        # Event-Handler registrieren
        self._register_event_handlers()

        # Post-Initialisierung planen
        Clock.schedule_once(self._post_init, 0)

    def _initialize_handlers(self):
        """Initialisiert Handler für Charakterverwaltung"""
        try:
            self.character_handler = CharacterHandler(self)
            self.game_elements_handler = GameElementsHandler(self)

            Logger.info("CharakterVerwaltung Handler erfolgreich initialisiert")
        except Exception as e:
            Logger.error(f"Fehler bei Handler-Initialisierung: {e}")

    def _initialize_managers(self):
        """Initialisiert Manager für erweiterte Funktionen"""
        try:
            self.statistics_manager = StatisticsManager(self)
            self.pdf_manager = PDFManager(self)
            self.html_manager = HTMLManager(self)
            Logger.info("CharakterVerwaltung Manager erfolgreich initialisiert")
        except Exception as e:
            Logger.error(f"Fehler bei Manager-Initialisierung: {e}")
            self.statistics_manager = None
            self.pdf_manager = None
            self.html_manager = None

    def _register_event_handlers(self):
        """Registriert Event-Handler"""
        try:
            event_service = service_container.get_event_service()

            if event_service:
                # Character-Events
                event_service.subscribe(EventTypes.CHARACTER_CREATED, self.character_handler.on_character_created)
                event_service.subscribe(EventTypes.CHARACTER_LOADED, self.character_handler.on_character_loaded)
                # Generierungsstatus bei Laden/Erstellen synchronisieren
                event_service.subscribe(EventTypes.CHARACTER_CREATED, lambda data: self._sync_char_gen_status())
                event_service.subscribe(EventTypes.CHARACTER_LOADED, lambda data: self._sync_char_gen_status())

                Logger.debug("Event-Handler für CharakterVerwaltung registriert")
        except Exception as e:
            Logger.error(f"Fehler bei Event-Handler-Registrierung: {e}")

    def _post_init(self, dt):
        """Post-Initialisierung nach dem UI-Aufbau"""
        try:
            # Statistiken aktualisieren
            if self.statistics_manager:
                self.statistics_manager.update_element_statistics_ui()

            # Generierungsstatus synchronisieren
            self._sync_char_gen_status()

            Logger.info("CharakterVerwaltung Post-Initialisierung erfolgreich abgeschlossen")
        except Exception as e:
            Logger.error(f"Fehler bei Post-Initialisierung: {e}")

    # ==================== HILFSMETHODEN ====================

    def _defocus_and_call(self, callback):
        """Defokussiert alle TextFields und ruft callback verzögert auf.
        Behebt Android-Problem: TextField-Fokus schluckt Button-Touch-Events."""
        Window.release_all_keyboards()
        Clock.schedule_once(lambda dt: callback(), 0.1)

    # ==================== CHARAKTERVERWALTUNG METHODEN ====================

    def get_charakter_value(self, attribute, default_value=''):
        """Delegiert Charakter-Wert-Abruf an CharacterHandler"""
        return self.character_handler.get_charakter_value(attribute, default_value)

    def create_new_character(self):
        """Startet den Wizard für die Charaktererstellung mit Namensabfrage und Setting-Auswahl."""
        import time
        now = time.monotonic()
        if hasattr(self, '_last_new_char_time') and (now - self._last_new_char_time) < 0.5:
            return
        self._last_new_char_time = now

        try:
            self._show_new_character_dialog()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Neuer-Charakter-Dialogs: {e}")
    
    def _show_new_character_dialog(self):
        """Zeigt einen Dialog zur Eingabe des Charakternamens und Setting-Auswahl."""
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
        
        content = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, adaptive_height=True)
        
        name_field = MDTextField(size_hint_x=1)
        name_field.add_widget(MDTextFieldHintText(text="Charaktername"))
        content.add_widget(name_field)
        
        app = MDApp.get_running_app()
        if not hasattr(app, 'controller') or not app.controller:
            Logger.warning("Controller nicht verfügbar")
            return
        
        available_settings = self._get_available_settings()
        
        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        if _mobile:
            list_layout.padding = [0, 0, dp(32), 0]

        selected_setting = [available_settings[0] if available_settings else None]
        checkboxes = {}

        for setting_name in available_settings:
            list_item = MDListItem(
                size_hint_y=None,
                height=dp(56) if _mobile else dp(48),
                on_release=lambda x, s=setting_name: self._select_new_char_setting(s, selected_setting, checkboxes)
            )
            list_item.add_widget(MDListItemHeadlineText(text=setting_name))
            checkbox = MDListItemTrailingCheckbox(
                active=(setting_name == selected_setting[0]),
                group="new_char_setting"
            )
            list_item.add_widget(checkbox)
            list_layout.add_widget(list_item)
            checkboxes[setting_name] = checkbox

        scroll = MDScrollView(size_hint_y=None, height=landscape_height(200, 0.35))
        if _mobile:
            scroll.bar_width = dp(20)
            scroll.bar_margin = dp(8)
            scroll.scroll_type = ['bars', 'content']
        scroll.add_widget(list_layout)
        content.add_widget(scroll)

        def on_create(instance):
            char_name = name_field.text.strip()
            if not char_name:
                self._show_error_dialog("Bitte gib einen Charakternamen ein.")
                return
            
            setting_name = selected_setting[0]
            if not setting_name:
                self._show_error_dialog("Bitte wähle ein Setting aus.")
                return
            
            dialog.dismiss()
            self._create_character_with_setting(char_name, setting_name)
        
        dialog = MDDialog(
            MDDialogHeadlineText(text="Neuer Charakter"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Erstellen"),
                    style="filled",
                    on_release=on_create
                ),
            ),
            size_hint=(0.85, None),
        )
        dialog.open()
    
    def _select_new_char_setting(self, setting_name, selected_setting, checkboxes):
        """Wählt ein Setting für den neuen Charakter aus."""
        selected_setting[0] = setting_name
        for s, cb in checkboxes.items():
            cb.active = (s == setting_name)
    
    def _create_character_with_setting(self, char_name: str, setting_name: str):
        """Erstellt einen neuen Charakter mit dem gegebenen Namen und Setting."""
        try:
            app = MDApp.get_running_app()
            if not hasattr(app, 'controller') or not app.controller:
                Logger.error("Controller nicht verfügbar")
                return
            
            controller = app.controller

            # Über controller.neuer_charakter() gehen, damit current_character_file_path
            # zurückgesetzt und der Undo-Stack geleert wird. Sonst würde Schnellspeichern
            # später blind in die zuvor geladene Datei schreiben.
            if not controller.neuer_charakter(char_name=char_name, setting_name=setting_name):
                self._show_error_dialog("Charakter konnte nicht erstellt werden.")
                return
            
            try:
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_success_dialog(f"Charakter '{char_name}' erstellt.")
            except Exception:
                pass
            
            # Wizard-Modus: Zum nächsten Schritt wechseln (Völker)
            wizard_service = service_container.get_wizard_service()
            if wizard_service and wizard_service.aktiv:
                schritt = wizard_service.get_aktueller_schritt()
                if schritt and schritt.tab_id == 'neuer_charakter':
                    wizard_service.naechster_schritt()
            
            if hasattr(app, '_switch_to_tab_index'):
                app._switch_to_tab_index(2)
            
        except Exception as e:
            Logger.error(f"Fehler beim Erstellen des Charakters: {e}")
            self._show_error_dialog(f"Fehler beim Erstellen: {e}")
    
    def _show_error_dialog(self, message: str):
        """Zeigt einen Fehlerdialog."""
        try:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog(message)
            else:
                Logger.error(message)
        except Exception:
            Logger.error(message)
    
    def open_setting_assistent(self):
        """Öffnet den Setting-Assistenten zum Erstellen/Bearbeiten von Settings."""
        try:
            from views.setting_assistent_view import SettingAssistentDialogHandler
            
            app = MDApp.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                handler = SettingAssistentDialogHandler(app.controller)
                handler.show_assistent()
            else:
                Logger.warning("Controller nicht verfügbar - Setting-Assistent kann nicht geöffnet werden")
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Setting-Assistenten: {e}")
    
    def start_wizard_mode(self):
        """Startet den Charakter-Erstellungs-Wizard."""
        import time
        now = time.monotonic()
        if hasattr(self, '_last_wizard_time') and (now - self._last_wizard_time) < 0.5:
            return
        self._last_wizard_time = now

        try:
            from services.service_container import service_container

            wizard_service = service_container.get_wizard_service()
            if not wizard_service:
                Logger.error("WizardService nicht verfügbar")
                return

            app = MDApp.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                wizard_service.charakter_controller = app.controller

            wizard_service.starten()

            # Navigation und Dialog-Öffnung erfolgt über _on_wizard_started in main.py
            # NICHT hier doppelt navigieren, sonst öffnet sich "Neuer Charakter" zweimal

            Logger.info("Charakter-Erstellungs-Wizard gestartet")
            
        except Exception as e:
            Logger.error(f"Fehler beim Starten des Wizards: {e}")

    # ==================== NEUER CHARAKTER WIZARD ====================

    def _get_available_settings(self):
        """Liest alle verfügbaren Settings aus dem nativen und Benutzer-Settings-Verzeichnis"""
        from utils.path_utils import get_settings_path, get_user_settings_path

        settings_set = set()
        # Native Settings laden
        native_dir = Path(get_settings_path())
        if native_dir.exists():
            for f in native_dir.glob('*.json'):
                settings_set.add(safe_filename_stem(f))

        # Benutzer-Settings laden (persistentes Verzeichnis)
        user_dir = Path(get_user_settings_path())
        if user_dir.exists() and user_dir != native_dir:
            for f in user_dir.glob('*.json'):
                settings_set.add(safe_filename_stem(f))

        return sorted(settings_set)

    def _show_setting_selection_popup(self):
        """Schritt 1: Setting-Auswahl als MDDialog.
        Gleicher Stil wie der Setting-Wechsel-Dialog."""
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer
        from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

        available_settings = self._get_available_settings()
        if not available_settings:
            Logger.error("Keine Settings im settings-Verzeichnis gefunden")
            return

        # Standard: SWAE vorausgewählt
        default_setting = 'SWAE' if 'SWAE' in available_settings else available_settings[0]
        self._wizard_pending_setting = default_setting

        # Hauptcontainer
        dialog_content = MDBoxLayout(
            orientation="vertical", spacing=dp(15), padding=dp(20),
            size_hint_y=None,
        )
        dialog_content.bind(minimum_height=dialog_content.setter('height'))

        # Suchfeld
        search_field = MDTextField(
            mode="outlined", size_hint_y=None, height=dp(56), size_hint_x=1
        )
        search_field.add_widget(MDTextFieldHintText(text="Setting suchen..."))
        dialog_content.add_widget(search_field)

        # Scrollbare Liste
        scroll_view = MDScrollView(size_hint=(1, None), height=landscape_height(250, 0.4))
        scroll_layout = MDBoxLayout(orientation="horizontal", size_hint=(1, None))
        items_list = MDList(size_hint_y=None, size_hint_x=1)
        items_list.bind(minimum_height=items_list.setter('height'))
        scroll_layout.add_widget(items_list)
        scroll_layout.add_widget(MDBoxLayout(size_hint_x=None, width=dp(20)))
        scroll_view.add_widget(scroll_layout)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
        dialog_content.add_widget(scroll_view)

        def populate_list(*args):
            items_list.clear_widgets()
            search_text = search_field.text.lower() if search_field.text else ""
            pending = self._wizard_pending_setting

            for setting_name in sorted(available_settings):
                if search_text and search_text not in setting_name.lower():
                    continue
                is_sel = (pending == setting_name)
                item = MDListItem(
                    size_hint_y=None, height=dp(48),
                    on_release=lambda x, s=setting_name: _select(s),
                    md_bg_color=self.app.theme_cls.primaryContainerColor if is_sel else [0, 0, 0, 0],
                )
                if is_sel:
                    item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                headline = MDListItemHeadlineText(text=setting_name)
                if is_sel:
                    headline.bold = True
                item.add_widget(headline)
                items_list.add_widget(item)

        def _select(setting_name):
            self._wizard_pending_setting = setting_name
            populate_list()

        search_field.bind(text=populate_list)
        populate_list()

        # Buttons
        button_row = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
        )
        button_row.add_widget(MDBoxLayout(size_hint_x=1))
        button_row.add_widget(MDButton(
            MDButtonText(text="Abbrechen"), style="text",
            on_release=lambda x: self._defocus_and_call(self._wizard_setting_dialog.dismiss),
        ))
        button_row.add_widget(MDButton(
            MDButtonText(text="Auswählen"), style="text",
            on_release=lambda x: self._defocus_and_call(self._apply_wizard_setting),
        ))
        dialog_content.add_widget(button_row)

        self._wizard_setting_dialog = MDDialog(
            MDDialogHeadlineText(text="Setting auswählen"),
            MDDialogContentContainer(dialog_content, orientation="vertical", padding=dp(0)),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self._wizard_setting_dialog.open()

    def _apply_wizard_setting(self):
        """Wendet die Setting-Auswahl im Wizard an und geht zum nächsten Schritt."""
        try:
            self._wizard_setting_dialog.dismiss()
            self._wizard_selected_setting = self._wizard_pending_setting
            self._show_character_config_popup()
        except Exception as e:
            Logger.error(f"Fehler bei Setting-Auswahl im Wizard: {e}")

    def _switch_to_profil(self):
        """Wechselt zum Profil-Tab"""
        try:
            app = self.app
            # Profil ist Tab-Index 3
            if hasattr(app, '_switch_to_tab_index'):
                app._switch_to_tab_index(3)
            elif hasattr(app, '_on_rail_item_click'):
                app._on_rail_item_click(3)
            else:
                # Fallback: Direkt über ScreenManager
                root = app.root
                if root:
                    screen_manager = root.ids.get('tabs_carousel')
                    if screen_manager:
                        from kivy.uix.screenmanager import NoTransition
                        screen_manager.transition = NoTransition()
                        screen_manager.current = "screen_3_profil"
        except Exception as e:
            Logger.error(f"Fehler beim Wechsel zum Profil-Tab: {e}")

    def schnellspeichern_charakter(self):
        """Schnellspeicherung des Charakters"""
        return self.character_handler.schnellspeichern_charakter()

    def speichere_charakter(self):
        """Speichert den Charakter mit Dialog"""
        return self.character_handler.speichere_charakter()

    def lade_charakter(self):
        """Lädt einen Charakter"""
        return self.character_handler.lade_charakter()

    def loesche_charakter(self):
        """Öffnet den FileManager zum Löschen eines Charakters"""
        try:
            from utils.path_utils import get_chars_path

            chars_dir = get_chars_path()
            chars_path = Path(chars_dir)
            if not chars_path.exists():
                chars_path.mkdir(parents=True, exist_ok=True)

            self._char_delete_fm = CustomFileManager(
                exit_manager=self._exit_char_delete,
                select_path=self._on_char_delete_selected,
                preview=False,
            )
            self._char_delete_fm.show(chars_dir)

        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des FileManagers: {e}")

    def _exit_char_delete(self, *args):
        """Schließt den FileManager für Char-Löschen"""
        if hasattr(self, '_char_delete_fm'):
            self._char_delete_fm.close()

    def _on_char_delete_selected(self, selected_path):
        """Wird aufgerufen wenn eine Datei ausgewählt wurde"""
        try:
            fname = os.path.basename(selected_path)
            dialog_service = service_container.get_dialog_service()

            def do_delete(*args):
                try:
                    if not os.path.exists(selected_path):
                        Logger.warning(f"Datei nicht mehr vorhanden: {selected_path}")
                        if dialog_service:
                            dialog_service.show_warning_dialog(
                                f"Datei '{fname}' ist nicht mehr vorhanden (bereits gelöscht)."
                            )
                        self._exit_char_delete()
                        return
                    os.remove(selected_path)
                    Logger.info(f"Charakter gelöscht: {selected_path}")
                    if dialog_service:
                        dialog_service.show_success_dialog(f"Charakter '{fname}' gelöscht.")
                    self._exit_char_delete()
                except Exception as e:
                    Logger.error(f"Fehler beim Löschen: {e}")
                    if dialog_service:
                        dialog_service.show_error_dialog(f"Fehler beim Löschen: {e}")

            if dialog_service:
                dialog_service.show_choice_dialog(
                    message=f"Möchtest du '{fname}' wirklich löschen?",
                    title="Charakter löschen",
                    choices=[("Ja, löschen", "delete"), ("Abbrechen", "cancel")],
                    on_choice=lambda c: do_delete() if c == "delete" else None
                )
            else:
                do_delete()

        except Exception as e:
            Logger.error(f"Fehler bei Char-Löschen: {e}")

    def zeige_statblock(self):
        """Zeigt Statblock an"""
        return self.character_handler.zeige_statblock()

    def zeige_element_statistiken(self):
        """Zeigt Element-Statistiken an"""
        return self.character_handler.zeige_element_statistiken()

    # ==================== CHARAKTER-EINSTELLUNGEN ====================

    def update_maximale_attributsteigerungen(self):
        """Aktualisiert die maximalen Attributsteigerungen und passt verbleibende Punkte an"""
        try:
            if not self.app.controller:
                Logger.warning("Controller nicht verfügbar für Attributsteigerungen-Update")
                return

            char = self.app.controller.charakter
            field_value = self.ids.attributsteigerungen_field.text
            try:
                new_value = int(field_value)
                old_value = char.maximale_attributsteigerungen
                differenz = new_value - old_value
                char.maximale_attributsteigerungen = new_value
                char.verbleibende_attributsteigerungen = max(0, char.verbleibende_attributsteigerungen + differenz)
                Logger.info(f"Attributsteigerungen: max={new_value}, verbleibend={char.verbleibende_attributsteigerungen}")
            except ValueError:
                Logger.warning(f"Ungültiger Wert für Attributsteigerungen: {field_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Attributsteigerungen: {e}")

    def update_maximale_fertigkeitssteigerungen(self):
        """Aktualisiert die maximalen Fertigkeitssteigerungen und passt verbleibende Punkte an"""
        try:
            if not self.app.controller:
                Logger.warning("Controller nicht verfügbar für Fertigkeitssteigerungen-Update")
                return

            char = self.app.controller.charakter
            field_value = self.ids.fertigkeitssteigerungen_field.text
            try:
                new_value = int(field_value)
                old_value = char.maximale_fertigkeitssteigerungen
                differenz = new_value - old_value
                char.maximale_fertigkeitssteigerungen = new_value
                char.verbleibende_fertigkeitssteigerungen = max(0, char.verbleibende_fertigkeitssteigerungen + differenz)
                Logger.info(f"Fertigkeitssteigerungen: max={new_value}, verbleibend={char.verbleibende_fertigkeitssteigerungen}")
            except ValueError:
                Logger.warning(f"Ungültiger Wert für Fertigkeitssteigerungen: {field_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Fertigkeitssteigerungen: {e}")

    def update_vermoegen(self):
        """Aktualisiert das Vermögen"""
        try:
            if not self.app.controller:
                Logger.warning("Controller nicht verfügbar für Vermögen-Update")
                return

            field_value = self.ids.vermoegen_field.text
            try:
                new_value = int(field_value)
                self.app.controller.charakter.vermoegen = new_value
                Logger.info(f"Vermögen aktualisiert auf: {new_value}")
            except ValueError:
                Logger.warning(f"Ungültiger Wert für Vermögen: {field_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Vermögens: {e}")

    def update_waehrung(self):
        """Aktualisiert die Währungseinheit"""
        try:
            if not self.app.controller:
                Logger.warning("Controller nicht verfügbar für Währung-Update")
                return

            new_value = self.ids.waehrung_field.text
            self.app.controller.charakter.waehrungseinheit = new_value
            Logger.info(f"Währungseinheit aktualisiert auf: {new_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Währung: {e}")

    def _show_warning(self, title, message):
        """Zeigt ein Warn-Popup an"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.show_warning_dialog(message, title)
        else:
            Logger.warning(f"{title}: {message}")

    def erhoehe_startkapital(self):
        """Erhöht das Startkapital mit Handicap-Punkten"""
        try:
            if not self.app.controller:
                Logger.warning("Controller nicht verfügbar für Startkapital-Erhöhung")
                return

            char = self.app.controller.charakter
            if not char:
                return

            if char.verbleibende_handicap_punkte <= 0:
                self._show_warning(
                    "Keine Handicap-Punkte",
                    "Es sind keine Handicap-Punkte verfügbar.\n\n"
                    "Wähle zuerst Handicaps aus, um Punkte zu erhalten, "
                    "die du für zusätzliches Startkapital einsetzen kannst."
                )
                return

            self.app.controller.erhoehe_startkapital_mit_handicap()
            Logger.info("Startkapital mit Handicap-Punkten erhöht")
        except Exception as e:
            Logger.error(f"Fehler beim Erhöhen des Startkapitals: {e}")

    def senke_startkapital(self):
        """Nimmt eine Startkapital-Einlösung zurück und erstattet den Handicap-Punkt"""
        try:
            if not self.app.controller:
                Logger.warning("Controller nicht verfügbar für Startkapital-Rücknahme")
                return

            char = self.app.controller.charakter
            if not char:
                return

            if getattr(char, 'startgeld_einloesungen', 0) <= 0:
                self._show_warning(
                    "Nichts zurückzunehmen",
                    "Für dieses Setting wurden keine Handicap-Punkte in Startkapital "
                    "umgewandelt."
                )
                return

            erfolg, meldung = self.app.controller.senke_startkapital_mit_handicap()
            if not erfolg:
                self._show_warning("Rücknahme nicht möglich", meldung)
                return

            Logger.info("Startkapital-Einlösung zurückgenommen")
        except Exception as e:
            Logger.error(f"Fehler beim Zurücknehmen des Startkapitals: {e}")

    def toggle_char_gen_completed(self):
        """Umschaltet den Charakter-Generierungsstatus"""
        try:
            if not (self.app.controller and self.app.controller.charakter):
                return
            char = self.app.controller.charakter
            new_value = not char.char_gen_completed
            char.char_gen_completed = new_value
            self.char_gen_completed = new_value
            Logger.info(f"Charakter-Generierungsstatus über Einstellungen geändert: {new_value}")
        except Exception as e:
            Logger.error(f"Fehler beim Umschalten des Generierungsstatus: {e}")

    def _sync_char_gen_status(self):
        """Synchronisiert den lokalen char_gen_completed-Status mit dem Charakter-Modell"""
        try:
            if self.app.controller and self.app.controller.charakter:
                self.char_gen_completed = self.app.controller.charakter.char_gen_completed
        except Exception as e:
            Logger.error(f"Fehler beim Synchronisieren des Generierungsstatus: {e}")

    def erhoehe_aufstieg(self):
        """Erhöht die Aufstiege"""
        try:
            if not (self.app.controller and self.app.controller.charakter):
                Logger.warning("Controller oder Charakter nicht verfügbar für Aufstieg-Erhöhung")
                return

            char = self.app.controller.charakter
            if not char.char_gen_completed:
                self._show_warning(
                    "Charaktergenerierung nicht abgeschlossen",
                    "Aufstiege können erst nach Abschluss der Charaktergenerierung "
                    "hinzugefügt werden.\n\n"
                    "Schließe zuerst die Charaktererstellung ab."
                )
                return

            from functions.character_advancement import increase_aufstiege
            increase_aufstiege(char)
            Logger.info("Aufstieg erhöht")
        except Exception as e:
            Logger.error(f"Fehler beim Erhöhen des Aufstiegs: {e}")

    def senke_aufstieg(self):
        """Senkt die Aufstiege"""
        try:
            if not (self.app.controller and self.app.controller.charakter):
                Logger.warning("Controller oder Charakter nicht verfügbar für Aufstieg-Senkung")
                return

            char = self.app.controller.charakter
            if not char.char_gen_completed:
                self._show_warning(
                    "Charaktergenerierung nicht abgeschlossen",
                    "Aufstiege können erst nach Abschluss der Charaktergenerierung "
                    "verändert werden.\n\n"
                    "Schließe zuerst die Charaktererstellung ab."
                )
                return

            if char.verbleibende_aufstiege <= 0 and char.aufstiege_gesamt <= 0:
                self._show_warning(
                    "Kein Abstieg möglich",
                    "Es sind keine Aufstiege vorhanden, die entfernt werden könnten."
                )
                return

            from functions.character_advancement import decrease_aufstiege
            decrease_aufstiege(char)
            Logger.info("Aufstieg gesenkt")
        except Exception as e:
            Logger.error(f"Fehler beim Senken des Aufstiegs: {e}")

    # ==================== SETTING-VERWALTUNG ====================

    def open_add_setting_popup(self):
        """Öffnet Dialog zum Hinzufügen von Settings"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_setting_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Setting hinzufügen nicht möglich")

    def open_setting_switch_options(self):
        """Delegiert Setting-Wechsel-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_setting_switch_options()

    def open_setting_switch_popup(self):
        """Setting-Wechsel - delegiert an GameElementsHandler (Overlay statt MDDialog)"""
        return self.game_elements_handler.open_setting_switch_options()

    def _open_setting_switch_popup_legacy(self):
        """LEGACY: Setting-Wechsel mit Auswahl-Popup (alter MDDialog-Code, nicht mehr verwendet)"""
        try:
            if not (self.app.controller and self.app.controller.charakter):
                self._show_warning("Kein Charakter", "Kein Charakter verfügbar.")
                return

            char = self.app.controller.charakter
            available_settings = char.custom_element_manager.get_all_settings()
            current_setting = char.active_setting_name

            if not available_settings or len(available_settings) <= 1:
                self._show_warning(
                    "Kein Setting-Wechsel möglich",
                    f"Nur ein Setting verfügbar: '{current_setting}'"
                )
                return

            self._switch_pending_setting = current_setting

            # Hauptcontainer
            dialog_content = MDBoxLayout(
                orientation="vertical", spacing=dp(15), padding=dp(20),
                size_hint_y=None,
            )
            dialog_content.bind(minimum_height=dialog_content.setter('height'))

            # Info
            dialog_content.add_widget(MDLabel(
                text=f"Aktuelles Setting: {current_setting}",
                theme_text_color="Secondary", font_style="Body",
                size_hint_y=None, height=dp(30),
            ))

            # Suchfeld
            search_field = MDTextField(
                mode="outlined", size_hint_y=None, height=dp(56), size_hint_x=1
            )
            search_field.add_widget(MDTextFieldHintText(text="Setting suchen..."))
            dialog_content.add_widget(search_field)

            # Scrollbare Liste
            scroll_view = MDScrollView(size_hint=(1, None), height=landscape_height(250, 0.4))
            scroll_layout = MDBoxLayout(orientation="horizontal", size_hint=(1, None))
            items_list = MDList(size_hint_y=None, size_hint_x=1)
            items_list.bind(minimum_height=items_list.setter('height'))
            scroll_layout.add_widget(items_list)
            scroll_layout.add_widget(MDBoxLayout(size_hint_x=None, width=dp(20)))
            scroll_view.add_widget(scroll_layout)
            scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
            dialog_content.add_widget(scroll_view)

            def populate_list(*args):
                items_list.clear_widgets()
                search_text = search_field.text.lower() if search_field.text else ""
                pending = self._switch_pending_setting

                for setting_name in sorted(available_settings):
                    if search_text and search_text not in setting_name.lower():
                        continue
                    is_sel = (pending == setting_name)
                    is_current = (setting_name == current_setting)
                    item = MDListItem(
                        size_hint_y=None, height=dp(48),
                        on_release=lambda x, s=setting_name: _select(s),
                        md_bg_color=self.app.theme_cls.primaryContainerColor if is_sel else [0, 0, 0, 0],
                    )
                    if is_sel:
                        item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                    label_text = f"{setting_name} (aktiv)" if is_current else setting_name
                    headline = MDListItemHeadlineText(text=label_text)
                    if is_sel:
                        headline.bold = True
                    item.add_widget(headline)
                    items_list.add_widget(item)

            def _select(setting_name):
                self._switch_pending_setting = setting_name
                populate_list()

            search_field.bind(text=populate_list)
            populate_list()

            # Buttons
            button_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
            )
            button_row.add_widget(MDBoxLayout(size_hint_x=1))
            button_row.add_widget(MDButton(
                MDButtonText(text="Abbrechen"), style="text",
                on_release=lambda x: self._defocus_and_call(self._switch_dialog.dismiss),
            ))
            button_row.add_widget(MDButton(
                MDButtonText(text="Wechseln"), style="text",
                on_release=lambda x: self._defocus_and_call(self._apply_setting_switch),
            ))
            dialog_content.add_widget(button_row)

            self._switch_dialog = MDDialog(
                MDDialogHeadlineText(text="Setting wechseln"),
                MDDialogContentContainer(dialog_content, orientation="vertical", padding=dp(0)),
                size_hint=(0.85, None),
                auto_dismiss=False,
            )
            self._switch_dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Setting-Wechsel-Popups: {e}")

    def _apply_setting_switch(self):
        """Wendet den Setting-Wechsel aus dem Popup an"""
        try:
            self._switch_dialog.dismiss()
            chosen = getattr(self, '_switch_pending_setting', None)
            if not chosen:
                return

            char = self.app.controller.charakter
            if chosen == char.active_setting_name:
                return

            # Delegiere an GameElementsHandler für Merge-Dialog
            self.game_elements_handler._on_setting_choice_made(chosen)
        except Exception as e:
            Logger.error(f"Fehler beim Setting-Wechsel: {e}")

    def open_delete_setting_popup(self):
        """Öffnet Dialog zum Löschen von Settings"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_setting_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Setting löschen nicht möglich")

    # ==================== UI UPDATE METHODEN ====================

    def refresh_widget(self):
        """Aktualisiert das Widget"""
        try:
            if self.statistics_manager:
                self.statistics_manager.update_element_statistics_ui()
            Logger.debug("CharakterVerwaltungWidget erfolgreich aktualisiert")
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des CharakterVerwaltungWidgets: {e}")

    def aktualisiere_ui(self):
        """Alias für refresh_widget - Kompatibilität"""
        self.refresh_widget()

    # ==================== CLEANUP ====================

    def on_stop(self):
        """Cleanup beim Beenden"""
        try:
            # Event-Handler entfernen
            event_service = service_container.get_event_service()

            if event_service:
                event_service.unsubscribe(EventTypes.CHARACTER_CREATED, self.character_handler.on_character_created)
                event_service.unsubscribe(EventTypes.CHARACTER_LOADED, self.character_handler.on_character_loaded)

            Logger.info("CharakterVerwaltungWidget bereinigt")
        except Exception as e:
            Logger.error(f"Fehler beim Bereinigen: {e}")

    # ==================== LOG KOPIEREN ====================

    def _copy_to_clipboard(self, text: str):
        """Kopiert Text in die Zwischenablage."""
        import shutil
        from kivy.utils import platform as kivy_platform

        try:
            if kivy_platform == 'android':
                from android.clipboard import clipboard
                clipboard.copy(text)
                Logger.info("Text über Android Clipboard kopiert")
                return

            if kivy_platform == 'win':
                import subprocess
                subprocess.run(['clip'], input=text.encode('utf-8'), check=True)
                Logger.info("Text über Windows clip.exe kopiert")
                return

            if kivy_platform == 'linux':
                try:
                    subprocess.run(['xclip', '-selection', 'c'], input=text.encode('utf-8'), check=True)
                    Logger.info("Text über xclip kopiert")
                    return
                except Exception:
                    pass

                try:
                    subprocess.run(['xsel', '-bc'], input=text.encode('utf-8'), check=True)
                    Logger.info("Text über xsel kopiert")
                    return
                except Exception:
                    pass

            # Fallback: Kivy Clipboard
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(text)
            Logger.info("Text über Kivy Clipboard kopiert (fallback)")

        except Exception as e:
            Logger.warning(f"System-Clipboard fehlgeschlagen, verwende Kivy: {e}")
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(text)
            Logger.info("Text über Kivy Clipboard kopiert (fallback)")

    def open_log_file(self):
        """Exportiert die Log-Datei — auf Android über Teilen-Dialog, auf Desktop in Zwischenablage"""
        try:
            app = MDApp.get_running_app()
            if not hasattr(app, 'log_filepath') or not app.log_filepath:
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_warning_dialog("Keine Log-Datei verfügbar")
                return

            log_filepath = app.log_filepath

            if not os.path.exists(log_filepath):
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_warning_dialog(f"Log-Datei nicht gefunden: {log_filepath}")
                return

            from kivy.utils import platform
            if platform == 'android':
                # Android: Log-Datei über Teilen-Dialog exportieren
                try:
                    from utils.share_utils import share_file
                    share_file(
                        log_filepath,
                        mime_type='text/plain',
                        title="Log-Datei teilen"
                    )
                    Logger.info(f"Log-Datei zum Teilen geöffnet: {log_filepath}")
                except Exception as e:
                    Logger.error(f"Fehler beim Teilen der Log-Datei: {e}")
                    # Fallback: In Zwischenablage kopieren
                    self._copy_log_to_clipboard(log_filepath)
            else:
                self._copy_log_to_clipboard(log_filepath)

        except Exception as e:
            Logger.error(f"Fehler beim Log-Export: {e}")

    def _copy_log_to_clipboard(self, log_filepath):
        """Kopiert den Log-Inhalt in die Zwischenablage (Desktop-Fallback)"""
        try:
            with open(log_filepath, 'r', encoding='utf-8') as f:
                log_content = f.read()

            header = f"=== Session Log ===\n"
            header += f"Datei: {os.path.basename(log_filepath)}\n"
            header += f"Pfad: {log_filepath}\n"
            header += f"Größe: {len(log_content)} Zeichen\n\n"

            full_content = header + log_content
            self._copy_to_clipboard(full_content)

            lines_count = log_content.count('\n')
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(
                    f"Log kopiert!\n\n{lines_count} Zeilen • {len(log_content)} Zeichen"
                )
            Logger.info(f"Log-Inhalt kopiert ({lines_count} Zeilen)")

        except Exception as e:
            Logger.error(f"Fehler beim Lesen der Log-Datei: {e}")
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog(f"Fehler: {e}")
