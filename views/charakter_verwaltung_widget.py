# views/charakter_verwaltung_widget.py
"""
CharakterVerwaltungWidget - Ausgegliedert aus EinstellungenWidget
Verantwortlich für: Charakter-CRUD, PDF-Export, Statblock,
                    Charakter-Einstellungen (Punkte, Vermögen, Aufstieg/Abstieg),
                    Setting-Verwaltung
"""

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
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

# KV-Datei laden mit Mobile-Unterstützung
from utils.path_utils import get_application_root
from utils.platform_utils import is_mobile_layout
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

                Logger.debug("Event-Handler für CharakterVerwaltung registriert")
        except Exception as e:
            Logger.error(f"Fehler bei Event-Handler-Registrierung: {e}")

    def _post_init(self, dt):
        """Post-Initialisierung nach dem UI-Aufbau"""
        try:
            # Statistiken aktualisieren
            if self.statistics_manager:
                self.statistics_manager.update_element_statistics_ui()

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
        """Startet den Neuer-Charakter-Wizard mit Setting-Auswahl"""
        self._show_setting_selection_popup()

    # ==================== NEUER CHARAKTER WIZARD ====================

    def _get_available_settings(self):
        """Liest alle verfügbaren Settings aus dem settings-Verzeichnis"""
        settings_dir = Path(get_application_root()) / 'settings'
        settings = []
        if settings_dir.exists():
            for f in sorted(settings_dir.glob('*.json')):
                settings.append(f.stem)
        return settings

    def _show_setting_selection_popup(self):
        """Schritt 1: Setting-Auswahl Popup (Design wie Völker-Popup)"""
        available_settings = self._get_available_settings()
        if not available_settings:
            Logger.error("Keine Settings im settings-Verzeichnis gefunden")
            return

        # Standard: SWAE vorausgewählt
        self._wizard_selected_setting = 'SWAE' if 'SWAE' in available_settings else available_settings[0]

        # Hauptcontainer
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
        search_field.add_widget(MDTextFieldHintText(text="Setting suchen..."))
        dialog_content.add_widget(search_field)

        # Scrollbare Liste
        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=dp(280)
        )
        scroll_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, None)
        )
        items_list = MDList(size_hint_y=None, size_hint_x=1)
        items_list.bind(minimum_height=items_list.setter('height'))
        scroll_layout.add_widget(items_list)
        # Touch-Zone für zuverlässiges Scrollen auf Android
        scroll_layout.add_widget(MDBoxLayout(size_hint_x=None, width=dp(20)))
        scroll_view.add_widget(scroll_layout)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
        dialog_content.add_widget(scroll_view)

        def populate_list(*args):
            items_list.clear_widgets()
            search_text = search_field.text.lower() if search_field.text else ""
            pending = self._wizard_selected_setting

            for setting_name in available_settings:
                if search_text and search_text not in setting_name.lower():
                    continue
                is_sel = (pending == setting_name)
                item = MDListItem(
                    size_hint_y=None,
                    height=dp(48),
                    on_release=lambda x, s=setting_name: _select_setting(s),
                    md_bg_color=self.app.theme_cls.primaryContainerColor if is_sel else [0, 0, 0, 0],
                )
                if is_sel:
                    item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                headline = MDListItemHeadlineText(text=setting_name)
                if is_sel:
                    headline.bold = True
                item.add_widget(headline)
                items_list.add_widget(item)

        def _select_setting(setting_name):
            self._wizard_selected_setting = setting_name
            populate_list()

        search_field.bind(text=populate_list)
        populate_list()

        # Button-Zeile
        button_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8),
        )
        button_row.add_widget(MDBoxLayout(size_hint_x=1))
        btn_cancel = MDButton(
            MDButtonText(text="Abbrechen"),
            style="text",
            on_release=lambda x: self._wizard_setting_dialog.dismiss(),
        )
        btn_next = MDButton(
            MDButtonText(text="Weiter"),
            style="text",
            on_release=lambda x: self._on_setting_selected(),
        )
        button_row.add_widget(btn_cancel)
        button_row.add_widget(btn_next)
        dialog_content.add_widget(button_row)

        self._wizard_setting_dialog = MDDialog(
            MDDialogHeadlineText(text="Setting auswählen"),
            MDDialogContentContainer(
                dialog_content,
                orientation="vertical",
                padding=dp(0),
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self._wizard_setting_dialog.open()

    def _on_setting_selected(self):
        """Callback nach Setting-Auswahl: Dialog schließen, Konfig-Popup öffnen"""
        self._wizard_setting_dialog.dismiss()
        self._show_character_config_popup()

    def _show_character_config_popup(self):
        """Schritt 2: Startpunkte und Vermögen konfigurieren"""
        dialog_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=dp(20),
            size_hint_y=None,
        )
        dialog_content.bind(minimum_height=dialog_content.setter('height'))

        # Info-Label
        info_label = MDLabel(
            text=f"Setting: {self._wizard_selected_setting}",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(30),
        )
        dialog_content.add_widget(info_label)

        # Attribut-Punkte
        attr_row = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
        )
        attr_row.add_widget(MDLabel(
            text="Startattributs-Punkte:", size_hint_x=0.6,
            size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
        ))
        self._wizard_attr_field = MDTextField(
            text="5", mode="outlined",
            size_hint_x=0.4, size_hint_y=None, height=dp(56),
            input_filter='int'
        )
        attr_row.add_widget(self._wizard_attr_field)
        dialog_content.add_widget(attr_row)

        # Fertigkeits-Punkte
        fert_row = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
        )
        fert_row.add_widget(MDLabel(
            text="Startfertigkeits-Punkte:", size_hint_x=0.6,
            size_hint_y=None, height=dp(40), pos_hint={"center_y": .5}
        ))
        self._wizard_fert_field = MDTextField(
            text="12", mode="outlined",
            size_hint_x=0.4, size_hint_y=None, height=dp(56),
            input_filter='int'
        )
        fert_row.add_widget(self._wizard_fert_field)
        dialog_content.add_widget(fert_row)

        # Vermögen und Währung
        money_row = MDBoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(16)
        )
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
        dialog_content.add_widget(money_row)

        # Button-Zeile
        button_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8),
        )
        button_row.add_widget(MDBoxLayout(size_hint_x=1))
        btn_back = MDButton(
            MDButtonText(text="Zurück"),
            style="text",
            on_release=lambda x: self._defocus_and_call(self._on_config_back),
        )
        btn_next = MDButton(
            MDButtonText(text="Weiter"),
            style="text",
            on_release=lambda x: self._defocus_and_call(self._on_config_confirmed),
        )
        button_row.add_widget(btn_back)
        button_row.add_widget(btn_next)
        dialog_content.add_widget(button_row)

        self._wizard_config_dialog = MDDialog(
            MDDialogHeadlineText(text="Charakter-Einstellungen"),
            MDDialogContentContainer(
                dialog_content,
                orientation="vertical",
                padding=dp(0),
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self._wizard_config_dialog.open()

    def _on_config_back(self):
        """Zurück zur Setting-Auswahl"""
        self._wizard_config_dialog.dismiss()
        self._show_setting_selection_popup()

    def _on_config_confirmed(self):
        """Wizard abschließen: Charakter erstellen und zum Profil wechseln"""
        self._wizard_config_dialog.dismiss()

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
        Clock.schedule_once(lambda dt: self._switch_to_profil(), 0.1)

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

    def erzeuge_charakterbogen_pdf(self):
        """Erstellt Charakterbogen als PDF"""
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
        scroll_view = MDScrollView(size_hint=(1, None), height=dp(280))
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
        """Setting-Wechsel mit Auswahl-Popup (Mobile, Stil wie Neuer-Charakter-Wizard)"""
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
            scroll_view = MDScrollView(size_hint=(1, None), height=dp(250))
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
