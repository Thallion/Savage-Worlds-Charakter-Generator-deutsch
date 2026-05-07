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


class CharakterVerwaltungWidget(MDBoxLayout):
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

    def _show_character_config_popup(self):
        """Schritt 2: Startpunkte und Vermögen konfigurieren.
        Verwendet ModalView statt MDDialog für Android-Kompatibilität."""
        from kivy.uix.modalview import ModalView
        from kivy.animation import Animation

        # Bottom-Padding für Android-Navigationsleiste
        from kivy.utils import platform as kivy_platform
        bottom_pad = dp(48) if kivy_platform == 'android' else 0

        # Sheet-Container
        sheet = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=landscape_height(380, 0.75) + bottom_pad,
            pos_hint={'center_x': 0.5},
            md_bg_color=self.app.theme_cls.surfaceContainerColor,
            radius=[dp(16), dp(16), 0, 0],
            padding=[0, dp(8), 0, bottom_pad],
        )

        # Drag-Handle
        handle_container = MDBoxLayout(
            orientation='vertical', size_hint_y=None, height=dp(20),
            padding=[0, dp(8), 0, dp(4)],
        )
        handle_container.add_widget(MDBoxLayout(
            size_hint=(None, None), size=(dp(32), dp(4)),
            pos_hint={'center_x': 0.5},
            md_bg_color=(0.5, 0.5, 0.5, 1), radius=[dp(2)],
        ))
        sheet.add_widget(handle_container)

        # Header: Zurück + Titel + Weiter
        header = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(48),
            padding=[dp(8), 0, dp(8), 0], spacing=dp(8),
        )
        from kivymd.uix.button import MDIconButton
        header.add_widget(MDIconButton(
            icon="arrow-left",
            on_release=lambda x: self._config_sheet_back(modal),
            pos_hint={'center_y': 0.5},
        ))
        header.add_widget(MDLabel(
            text="Charakter-Einstellungen",
            font_style="Title", role="medium", bold=True,
            size_hint_x=1, pos_hint={'center_y': 0.5},
        ))
        header.add_widget(MDIconButton(
            icon="check",
            on_release=lambda x: self._config_sheet_confirm(modal),
            pos_hint={'center_y': 0.5},
        ))
        sheet.add_widget(header)

        # Formular-Inhalt
        form = MDBoxLayout(
            orientation='vertical', spacing=dp(16),
            padding=[dp(20), dp(8), dp(20), dp(16)],
            size_hint_y=None,
        )
        form.bind(minimum_height=form.setter('height'))

        # Info-Label
        form.add_widget(MDLabel(
            text=f"Setting: {self._wizard_selected_setting}",
            theme_text_color="Secondary", font_style="Body",
            size_hint_y=None, height=dp(24),
        ))

        # Attribut-Punkte
        attr_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16))
        attr_row.add_widget(MDLabel(
            text="Attributs-Punkte:", size_hint_x=0.6,
            size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
        ))
        self._wizard_attr_field = MDTextField(
            text="5", mode="outlined",
            size_hint_x=0.4, size_hint_y=None, height=dp(56),
            input_filter='int'
        )
        attr_row.add_widget(self._wizard_attr_field)
        form.add_widget(attr_row)

        # Fertigkeits-Punkte
        fert_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16))
        fert_row.add_widget(MDLabel(
            text="Fertigkeits-Punkte:", size_hint_x=0.6,
            size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
        ))
        self._wizard_fert_field = MDTextField(
            text="12", mode="outlined",
            size_hint_x=0.4, size_hint_y=None, height=dp(56),
            input_filter='int'
        )
        fert_row.add_widget(self._wizard_fert_field)
        form.add_widget(fert_row)

        # Vermögen und Währung
        money_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16))
        money_row.add_widget(MDLabel(
            text="Vermögen:", size_hint_x=0.3,
            size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
        ))
        self._wizard_money_field = MDTextField(
            text="500", mode="outlined",
            size_hint_x=0.35, size_hint_y=None, height=dp(56),
            input_filter='int'
        )
        money_row.add_widget(self._wizard_money_field)
        self._wizard_currency_field = MDTextField(
            text="Gold", mode="outlined",
            size_hint_x=0.35, size_hint_y=None, height=dp(56),
        )
        money_row.add_widget(self._wizard_currency_field)
        form.add_widget(money_row)

        sheet.add_widget(form)

        # ModalView erstellen
        modal = ModalView(
            size_hint=(1, 1),
            background_color=(0, 0, 0, 0),
            background='',
            auto_dismiss=False,
        )
        modal.add_widget(sheet)
        self._wizard_config_sheet = sheet
        self._wizard_config_modal = modal

        # Öffnen mit Animation
        modal.open()
        sheet.y = -sheet.height
        Animation(y=0, duration=0.25, t='out_cubic').start(sheet)

    def _config_sheet_back(self, modal):
        """Zurück zur Setting-Auswahl"""
        from kivy.animation import Animation
        sheet = self._wizard_config_sheet
        anim = Animation(y=-sheet.height, duration=0.2, t='in_cubic')
        anim.bind(on_complete=lambda *a: modal.dismiss())
        anim.start(sheet)
        Clock.schedule_once(lambda dt: self._show_setting_selection_popup(), 0.3)

    def _config_sheet_confirm(self, modal):
        """Wizard abschließen: Charakter erstellen und zum Profil wechseln"""
        # Werte aus den Feldern lesen
        try:
            attr_punkte = int(self._wizard_attr_field.text)
        except (ValueError, AttributeError):
            attr_punkte = 5
        try:
            fert_punkte = int(self._wizard_fert_field.text)
        except (ValueError, AttributeError):
            fert_punkte = 12
        try:
            vermoegen = int(self._wizard_money_field.text)
        except (ValueError, AttributeError):
            vermoegen = 500
        waehrung = getattr(self._wizard_currency_field, 'text', 'Gold') or 'Gold'

        # Sheet schließen
        from kivy.animation import Animation
        sheet = self._wizard_config_sheet
        anim = Animation(y=-sheet.height, duration=0.2, t='in_cubic')
        anim.bind(on_complete=lambda *a: modal.dismiss())
        anim.start(sheet)

        setting_name = self._wizard_selected_setting

        # Charakter erstellen über Controller
        if self.app.controller:
            self.app.controller.neuer_charakter(setting_name=setting_name)

            char = self.app.controller.charakter
            if char:
                char.char_gen_completed = False
                char.maximale_attributsteigerungen = attr_punkte
                char.verbleibende_attributsteigerungen = attr_punkte
                char.maximale_fertigkeitssteigerungen = fert_punkte
                char.verbleibende_fertigkeitssteigerungen = fert_punkte
                char.vermoegen = vermoegen
                char.waehrungseinheit = waehrung

            # UI aktualisieren
            self.character_handler._update_ui_fields()
            self.character_handler._refresh_profil_widget()

        # Zum Profil-Tab wechseln (Index 3)
        Clock.schedule_once(lambda dt: self._switch_to_profil(), 0.3)

        Logger.info(f"Neuer Charakter mit Setting '{setting_name}' erstellt "
                    f"(Attr: {attr_punkte}, Fert: {fert_punkte}, "
                    f"Vermögen: {vermoegen} {waehrung})")

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

    def erzeuge_charakterbogen_pdf(self):
        """Erstellt Charakterbogen als PDF"""
        from kivy.utils import platform as kivy_platform

        # Auf Android: Nutze HTML->PDF über PrintManager
        if kivy_platform == 'android':
            if hasattr(self, 'html_manager') and self.html_manager:
                return self.html_manager.create_character_pdf_android()
            else:
                Logger.error("HTMLManager nicht verfügbar für Android-PDF")
                return

        # Auf Desktop: Nutze klassischen PDF-Manager
        return self.character_handler.erzeuge_charakterbogen_pdf()

    def erzeuge_charakterbogen_html(self):
        """Erstellt Charakterbogen als HTML"""
        if hasattr(self, 'html_manager') and self.html_manager:
            return self.html_manager.create_character_html()
        else:
            Logger.error("HTMLManager nicht verfügbar")

    def lade_charakterbogen(self):
        """Öffnet einen gespeicherten Charakterbogen (HTML oder PDF)"""
        try:
            file_service = service_container.get_file_manager_service()
            if not file_service:
                Logger.error("FileManager-Service nicht verfügbar")
                return

            chars_dir = file_service.get_default_directory('chars')
            self._show_charakterbogen_file_list(chars_dir)
        except Exception as e:
            Logger.error(f"Fehler beim Laden des Charakterbogens: {e}")

    def _show_charakterbogen_file_list(self, chars_dir):
        """Zeigt eine Liste aller HTML/PDF Charakterbögen zum Öffnen"""
        import glob as glob_mod

        # HTML und PDF Dateien suchen
        files = []
        for ext in ('*.html', '*.pdf'):
            files.extend(glob_mod.glob(os.path.join(str(chars_dir), ext)))

        if not files:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_info_dialog(
                    "Keine Charakterbögen (HTML/PDF) gefunden.\n"
                    "Erstelle zuerst einen Charakterbogen über 'HTML erstellen' oder 'PDF erstellen'.",
                    "Keine Dateien"
                )
            return

        # Nach Änderungsdatum sortieren (neueste zuerst)
        files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

        self._bogen_selected_file = files[0] if files else None

        dialog_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
        )
        dialog_content.bind(minimum_height=dialog_content.setter('height'))

        # Suchfeld
        search_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(56),
            size_hint_x=1
        )
        search_field.add_widget(MDTextFieldHintText(text="Datei suchen..."))
        dialog_content.add_widget(search_field)

        # Scrollbare Liste
        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=landscape_height(280, 0.45),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(20) if _mobile else dp(15),
            bar_margin=dp(8) if _mobile else dp(4),
        )
        if _mobile:
            scroll_view.scroll_type = ['bars', 'content']
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
            pending = self._bogen_selected_file

            for fpath in files:
                fname = os.path.basename(fpath)
                if search_text and search_text not in fname.lower():
                    continue
                is_sel = (pending == fpath)
                is_pdf = fname.lower().endswith('.pdf')
                icon = "file-pdf-box" if is_pdf else "language-html5"

                item = MDListItem(
                    size_hint_y=None,
                    height=dp(48),
                    on_release=lambda x, p=fpath: _select_file(p),
                    md_bg_color=self.app.theme_cls.primaryContainerColor if is_sel else [0, 0, 0, 0],
                )
                if is_sel:
                    item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                else:
                    item.add_widget(MDListItemLeadingIcon(icon=icon))
                headline = MDListItemHeadlineText(text=fname)
                if is_sel:
                    headline.bold = True
                item.add_widget(headline)
                items_list.add_widget(item)

        def _select_file(fpath):
            self._bogen_selected_file = fpath
            populate_list()

        search_field.bind(text=populate_list)
        populate_list()

        # Button-Zeile
        button_row = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
        )
        button_row.add_widget(MDBoxLayout(size_hint_x=1))
        btn_cancel = MDButton(
            MDButtonText(text="Abbrechen"),
            style="text",
            on_release=lambda x: self._bogen_dialog.dismiss(),
        )
        btn_open = MDButton(
            MDButtonText(text="Öffnen"),
            style="text",
            on_release=lambda x: self._open_selected_bogen(),
        )
        button_row.add_widget(btn_cancel)
        button_row.add_widget(btn_open)
        dialog_content.add_widget(button_row)

        self._bogen_dialog = MDDialog(
            MDDialogHeadlineText(text="Charakterbogen öffnen"),
            MDDialogContentContainer(
                dialog_content, orientation="vertical", padding=dp(0)
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self._bogen_dialog.open()

    def _open_selected_bogen(self):
        """Öffnet den ausgewählten Charakterbogen"""
        self._bogen_dialog.dismiss()
        fpath = getattr(self, '_bogen_selected_file', None)
        if not fpath:
            return

        try:
            from kivy.utils import platform as kivy_platform
            is_pdf = fpath.lower().endswith('.pdf')
            mime = 'application/pdf' if is_pdf else 'text/html'

            if kivy_platform == 'android':
                from manager.html_manager import HTMLManager
                HTMLManager._open_file_on_android(fpath, mime)
            else:
                import webbrowser
                file_url = 'file://' + os.path.abspath(fpath)
                webbrowser.open(file_url)
                Logger.info(f"Charakterbogen geöffnet: {file_url}")
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Charakterbogens: {e}")
            if self.dialog_service:
                self.dialog_service.show_error_dialog(
                    f"Fehler beim Öffnen: {e}"
                )

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

    # ==================== MOBILE POPUPS ====================

    def open_punkte_popup(self):
        """Öffnet Popup für Attribut-/Fertigkeitspunkte (Mobile)"""
        try:
            char = self.app.controller.charakter if self.app.controller else None
            attr_val = str(getattr(char, 'maximale_attributsteigerungen', 5)) if char else '5'
            fert_val = str(getattr(char, 'maximale_fertigkeitssteigerungen', 12)) if char else '12'

            content = MDBoxLayout(
                orientation="vertical", spacing=dp(20), padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter('height'))

            # Attribut-Punkte
            attr_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            attr_row.add_widget(MDLabel(
                text="Attributs-Punkte:", size_hint_x=0.6,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_attr_field = MDTextField(
                text=attr_val, mode="outlined",
                size_hint_x=0.4, size_hint_y=None, height=dp(56),
                input_filter='int'
            )
            attr_row.add_widget(self._popup_attr_field)
            content.add_widget(attr_row)

            # Fertigkeits-Punkte
            fert_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            fert_row.add_widget(MDLabel(
                text="Fertigkeits-Punkte:", size_hint_x=0.6,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_fert_field = MDTextField(
                text=fert_val, mode="outlined",
                size_hint_x=0.4, size_hint_y=None, height=dp(56),
                input_filter='int'
            )
            fert_row.add_widget(self._popup_fert_field)
            content.add_widget(fert_row)

            # Buttons
            button_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
            )
            button_row.add_widget(MDBoxLayout(size_hint_x=1))
            button_row.add_widget(MDButton(
                MDButtonText(text="Abbrechen"), style="text",
                on_release=lambda x: self._defocus_and_call(self._punkte_dialog.dismiss),
            ))
            button_row.add_widget(MDButton(
                MDButtonText(text="Übernehmen"), style="text",
                on_release=lambda x: self._defocus_and_call(self._apply_punkte_popup),
            ))
            content.add_widget(button_row)

            self._punkte_dialog = MDDialog(
                MDDialogHeadlineText(text="Start-Punkte"),
                MDDialogContentContainer(content, orientation="vertical", padding=dp(0)),
                size_hint=(0.85, None),
                auto_dismiss=False,
            )
            self._punkte_dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Punkte-Popups: {e}")

    def _apply_punkte_popup(self):
        """Wendet die Werte aus dem Punkte-Popup an"""
        try:
            self._punkte_dialog.dismiss()
            char = self.app.controller.charakter if self.app.controller else None
            if not char:
                return

            try:
                attr_val = int(self._popup_attr_field.text)
                old_attr = char.maximale_attributsteigerungen
                differenz = attr_val - old_attr
                char.maximale_attributsteigerungen = attr_val
                char.verbleibende_attributsteigerungen = max(0, char.verbleibende_attributsteigerungen + differenz)
                if 'attributsteigerungen_field' in self.ids:
                    self.ids.attributsteigerungen_field.text = str(attr_val)
            except ValueError:
                pass

            try:
                fert_val = int(self._popup_fert_field.text)
                old_fert = char.maximale_fertigkeitssteigerungen
                differenz = fert_val - old_fert
                char.maximale_fertigkeitssteigerungen = fert_val
                char.verbleibende_fertigkeitssteigerungen = max(0, char.verbleibende_fertigkeitssteigerungen + differenz)
                if 'fertigkeitssteigerungen_field' in self.ids:
                    self.ids.fertigkeitssteigerungen_field.text = str(fert_val)
            except ValueError:
                pass

            # Button-Text aktualisieren
            if 'punkte_button_text' in self.ids:
                self.ids.punkte_button_text.text = (
                    f"Attr: {char.maximale_attributsteigerungen} / "
                    f"Fert: {char.maximale_fertigkeitssteigerungen}"
                )

            Logger.info(f"Punkte aktualisiert: Attr={char.maximale_attributsteigerungen}, "
                        f"Fert={char.maximale_fertigkeitssteigerungen}")
        except Exception as e:
            Logger.error(f"Fehler beim Anwenden der Punkte: {e}")

    def open_vermoegen_popup(self):
        """Öffnet Popup für Vermögen/Währung (Mobile)"""
        try:
            char = self.app.controller.charakter if self.app.controller else None
            money_val = str(getattr(char, 'vermoegen', 500)) if char else '500'
            currency_val = str(getattr(char, 'waehrungseinheit', 'Gold')) if char else 'Gold'

            content = MDBoxLayout(
                orientation="vertical", spacing=dp(20), padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter('height'))

            # Vermögen
            money_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            money_row.add_widget(MDLabel(
                text="Vermögen:", size_hint_x=0.4,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_money_field = MDTextField(
                text=money_val, mode="outlined",
                size_hint_x=0.6, size_hint_y=None, height=dp(56),
                input_filter='int'
            )
            money_row.add_widget(self._popup_money_field)
            content.add_widget(money_row)

            # Währung
            currency_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
            )
            currency_row.add_widget(MDLabel(
                text="Währung:", size_hint_x=0.4,
                size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
            ))
            self._popup_currency_field = MDTextField(
                text=currency_val, mode="outlined",
                size_hint_x=0.6, size_hint_y=None, height=dp(56),
            )
            currency_row.add_widget(self._popup_currency_field)
            content.add_widget(currency_row)

            # Buttons
            button_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
            )
            button_row.add_widget(MDBoxLayout(size_hint_x=1))
            button_row.add_widget(MDButton(
                MDButtonText(text="Abbrechen"), style="text",
                on_release=lambda x: self._defocus_and_call(self._vermoegen_dialog.dismiss),
            ))
            button_row.add_widget(MDButton(
                MDButtonText(text="Übernehmen"), style="text",
                on_release=lambda x: self._defocus_and_call(self._apply_vermoegen_popup),
            ))
            content.add_widget(button_row)

            self._vermoegen_dialog = MDDialog(
                MDDialogHeadlineText(text="Vermögen & Währung"),
                MDDialogContentContainer(content, orientation="vertical", padding=dp(0)),
                size_hint=(0.85, None),
                auto_dismiss=False,
            )
            self._vermoegen_dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Vermögen-Popups: {e}")

    def _apply_vermoegen_popup(self):
        """Wendet die Werte aus dem Vermögen-Popup an"""
        try:
            self._vermoegen_dialog.dismiss()
            char = self.app.controller.charakter if self.app.controller else None
            if not char:
                return

            try:
                money_val = int(self._popup_money_field.text)
                char.vermoegen = money_val
                if 'vermoegen_field' in self.ids:
                    self.ids.vermoegen_field.text = str(money_val)
            except ValueError:
                pass

            currency_val = self._popup_currency_field.text or 'Gold'
            char.waehrungseinheit = currency_val
            if 'waehrung_field' in self.ids:
                self.ids.waehrung_field.text = currency_val

            # Button-Text aktualisieren
            if 'vermoegen_button_text' in self.ids:
                self.ids.vermoegen_button_text.text = f"{char.vermoegen} {char.waehrungseinheit}"

            Logger.info(f"Vermögen aktualisiert: {char.vermoegen} {char.waehrungseinheit}")
        except Exception as e:
            Logger.error(f"Fehler beim Anwenden des Vermögens: {e}")

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

    # ==================== TEILEN / VERSENDEN ====================

    def versende_charakter(self):
        """Zeigt Dialog zum Versenden von Charakter-Dateien (JSON, PDF, HTML)"""
        try:
            controller = self.app.controller
            if not controller or not controller.charakter:
                self._show_share_warning("Kein Charakter geladen.")
                return

            char_name = getattr(controller.charakter, 'char_name', 'Charakter')
            char_file_path = getattr(controller, 'current_character_file_path', None)

            # Verfügbare Dateien sammeln
            dateien = self._sammle_charakter_dateien(char_file_path, char_name)

            if not dateien:
                self._show_share_warning(
                    "Keine Charakter-Dateien zum Versenden gefunden.\n"
                    "Speichere den Charakter zuerst."
                )
                return

            self._zeige_versende_dialog(dateien, f"Charakter versenden: {char_name}")
        except Exception as e:
            Logger.error(f"Fehler beim Versenden des Charakters: {e}")

    def _sammle_charakter_dateien(self, char_file_path, char_name):
        """Sammelt alle vorhandenen Dateien eines Charakters (JSON, PDF, HTML)."""
        dateien = []

        if char_file_path and os.path.exists(char_file_path):
            dateien.append({
                'pfad': char_file_path,
                'name': os.path.basename(char_file_path),
                'typ': 'Charakter (JSON)',
                'icon': 'code-json',
            })

            # Zugehörige PDF/HTML im gleichen Verzeichnis suchen
            ordner = os.path.dirname(char_file_path)
            basis = Path(char_file_path).stem

            pdf_pfad = os.path.join(ordner, f"{basis}.pdf")
            if os.path.exists(pdf_pfad):
                dateien.append({
                    'pfad': pdf_pfad,
                    'name': os.path.basename(pdf_pfad),
                    'typ': 'Charakterbogen (PDF)',
                    'icon': 'file-pdf-box',
                })

            html_pfad = os.path.join(ordner, f"{basis}.html")
            if os.path.exists(html_pfad):
                dateien.append({
                    'pfad': html_pfad,
                    'name': os.path.basename(html_pfad),
                    'typ': 'Charakterbogen (HTML)',
                    'icon': 'language-html5',
                })
        else:
            # Kein gespeicherter Charakter - in chars/ und Archetypen/ nach passenden Dateien suchen
            from utils.path_utils import get_chars_path, get_resource_path
            import glob as glob_mod

            chars_dir = get_chars_path()
            for ext in ('*.json', '*.pdf', '*.html'):
                for f in glob_mod.glob(os.path.join(chars_dir, ext)):
                    if char_name.lower() in os.path.basename(f).lower():
                        icon = 'code-json' if f.endswith('.json') else (
                            'file-pdf-box' if f.endswith('.pdf') else 'language-html5'
                        )
                        typ = 'JSON' if f.endswith('.json') else (
                            'PDF' if f.endswith('.pdf') else 'HTML'
                        )
                        dateien.append({
                            'pfad': f,
                            'name': os.path.basename(f),
                            'typ': typ,
                            'icon': icon,
                        })

            # Auch in Archetypen/ suchen (gebündelt + persistentes Verzeichnis auf Android)
            archetypen_dirs = set()
            
            # Suche an mehreren möglichen Stellen (wie in main.py)
            app_root = Path(get_application_root())
            
            # Gebündelte Archetypen aus verschiedenen Quellen
            possible_archetypen = [
                app_root / 'Archetypen',
                app_root / 'chars' / 'Archetypen',
                Path(get_resource_path('Archetypen')),
                Path(get_resource_path('chars/Archetypen')),
            ]
            
            for arch_path in possible_archetypen:
                if arch_path.exists() and arch_path.is_dir():
                    archetypen_dirs.add(str(arch_path))
                    Logger.debug(f"Archetypen: Gefunden in {arch_path}")
            
            # Auf Android: auch im persistenten User-Chars-Verzeichnis
            user_archetypen = os.path.join(get_chars_path(), 'Archetypen')
            archetypen_dirs.add(user_archetypen)

            for archetyps_dir in archetypen_dirs:
                if os.path.isdir(archetyps_dir):
                    for ext in ('*.json', '*.pdf', '*.html'):
                        for f in glob_mod.glob(os.path.join(archetyps_dir, ext)):
                            if char_name.lower() in os.path.basename(f).lower():
                                # Prüfen ob bereits in dateien
                                if not any(d['pfad'] == f for d in dateien):
                                    icon = 'code-json' if f.endswith('.json') else (
                                        'file-pdf-box' if f.endswith('.pdf') else 'language-html5'
                                    )
                                    typ = 'Archetyp (JSON)' if f.endswith('.json') else (
                                        'Archetyp (PDF)' if f.endswith('.pdf') else 'Archetyp (HTML)'
                                    )
                                    dateien.append({
                                        'pfad': f,
                                        'name': os.path.basename(f),
                                        'typ': typ,
                                        'icon': icon,
                                    })

        return dateien

    def _zeige_versende_dialog(self, dateien, titel):
        """Zeigt einen Dialog mit Checkboxen für die zu versendenden Dateien."""
        from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemTrailingCheckbox
        from kivymd.uix.label import MDIcon
        from kivymd.uix.scrollview import MDScrollView

        dialog_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(16),
            size_hint_y=None,
        )
        dialog_content.bind(minimum_height=dialog_content.setter('height'))

        dialog_content.add_widget(MDLabel(
            text="Dateien zum Versenden auswählen:",
            size_hint_y=None,
            height=dp(30),
        ))

        checkboxes = []

        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=min(dp(300), dp(48) * len(dateien) + dp(20)),
            bar_width=dp(20) if _mobile else dp(15),
            bar_margin=dp(8) if _mobile else dp(4),
        )
        if _mobile:
            scroll_view.scroll_type = ['bars', 'content']
        scroll_layout = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(48) * len(dateien),
            padding=[0, 0, dp(32), 0] if _mobile else [0, 0, 0, 0],
        )
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        for datei in dateien:
            item = MDListItem(
                size_hint_y=None,
                height=dp(48),
            )
            item.add_widget(MDIcon(
                icon=datei['icon'],
                size_hint=(None, None),
                size=(dp(24), dp(24)),
                pos_hint={"center_y": .5},
            ))
            item.add_widget(MDListItemHeadlineText(
                text=f"{datei['name']} ({datei['typ']})",
            ))

            trailing = MDListItemTrailingCheckbox(
                active=True,
            )
            item.add_widget(trailing)
            checkboxes.append((trailing, datei, item))

            scroll_layout.add_widget(item)

        scroll_view.add_widget(scroll_layout)
        dialog_content.add_widget(scroll_view)

        def _on_versenden(x):
            self._versende_dialog.dismiss()
            ausgewaehlte = [d['pfad'] for cb, d, item in checkboxes if cb.active]
            if ausgewaehlte:
                self._versende_dateien(ausgewaehlte, titel)

        self._versende_dialog = MDDialog(
            MDDialogHeadlineText(text=titel),
            MDDialogContentContainer(dialog_content, orientation="vertical"),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self._versende_dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Versenden"),
                    style="text",
                    on_release=_on_versenden,
                ),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self._versende_dialog.open()

    def _versende_dateien(self, dateipfade, titel="Dateien versenden"):
        """Versendet die ausgewählten Dateien über die Plattform-Teilen-Funktion."""
        from utils.share_utils import share_file, share_multiple_files, get_mime_type

        try:
            if len(dateipfade) == 1:
                mime = get_mime_type(dateipfade[0])
                success = share_file(dateipfade[0], mime, titel)
            else:
                success = share_multiple_files(dateipfade, '*/*', titel)

            if not success:
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_warning_dialog(
                        "Versenden fehlgeschlagen."
                    )
        except Exception as e:
            Logger.error(f"Fehler beim Versenden: {e}")

    def versende_setting(self):
        """Versendet das aktuell aktive Setting als JSON-Datei."""
        try:
            controller = self.app.controller
            if not controller or not controller.charakter:
                self._show_share_warning("Kein Charakter geladen.")
                return

            setting_name = getattr(controller.charakter, 'active_setting_name', None)
            if not setting_name:
                self._show_share_warning("Kein aktives Setting vorhanden.")
                return

            # Setting-Datei finden (zuerst im Benutzer-Verzeichnis, dann nativ)
            from utils.path_utils import get_settings_path, get_user_settings_path

            setting_file = None
            user_file = os.path.join(get_user_settings_path(), f"{setting_name}.json")
            native_file = os.path.join(get_settings_path(), f"{setting_name}.json")

            if os.path.exists(user_file):
                setting_file = user_file
            elif os.path.exists(native_file):
                setting_file = native_file

            if not setting_file:
                self._show_share_warning(f"Setting-Datei für '{setting_name}' nicht gefunden.")
                return

            from utils.share_utils import share_file
            success = share_file(setting_file, 'application/json', f"Setting versenden: {setting_name}")

            if not success:
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_warning_dialog(
                        "Versenden fehlgeschlagen."
                    )
        except Exception as e:
            Logger.error(f"Fehler beim Versenden des Settings: {e}")

    def _show_share_warning(self, message):
        """Zeigt eine Warnung beim Versenden."""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.show_warning_dialog(message)

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
