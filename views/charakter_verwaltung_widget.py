# views/charakter_verwaltung_widget.py
"""
NEUES: CharakterVerwaltungWidget - Ausgegliedert aus EinstellungenWidget
Verantwortlich für alle Charakterverwaltungs-Funktionen
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
from pathlib import Path

# Handler imports
from controllers.character_handler import CharacterHandler
from controllers.template_handler import TemplateHandler

# Service imports
from services.service_container import service_container, get_event_service
from services.event_service import EventTypes

# Manager imports
from manager.statistics_manager import StatisticsManager
from manager.pdf_manager import PDFManager
from manager.html_manager import HTMLManager

# KV-Datei laden
from utils.path_utils import get_application_root
import os
kv_path = os.path.join(get_application_root(), 'views', 'charakter_verwaltung_widget.kv')
Builder.load_file(kv_path)


class CharakterVerwaltungWidget(MDBoxLayout):
    """
    Neues Widget für Charakterverwaltung - ausgegliedert aus EinstellungenWidget
    Fokussiert auf: Charakter-CRUD, PDF-Export, Statblock, Template-Management
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
            self.template_handler = TemplateHandler(self)
            
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
            height=dp(380)
        )

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
            height=dp(300)
        )

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
            on_release=lambda x: self._on_config_back(),
        )
        btn_next = MDButton(
            MDButtonText(text="Weiter"),
            style="text",
            on_release=lambda x: self._on_config_confirmed(),
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
    
    def zeige_statblock(self):
        """Zeigt Statblock an"""
        return self.character_handler.zeige_statblock()
    
    def zeige_element_statistiken(self):
        """Zeigt Element-Statistiken an"""
        return self.character_handler.zeige_element_statistiken()
    
    # ==================== TEMPLATE-MANAGEMENT ====================
    
    def open_template_selection_dialog(self):
        """Öffnet Template-Auswahl Dialog"""
        return self.template_handler.open_template_selection_dialog()
        
    def show_template_selection_dialog(self):
        """Zeigt Template-Auswahl Dialog"""
        return self.template_handler.show_template_selection_dialog()
    
    def generate_character_from_selected_template(self):
        """Generiert Charakter aus ausgewähltem Template"""
        return self.template_handler.generate_character_from_selected_template()
    
    @property
    def selected_template(self):
        """Property für ausgewähltes Template (für KV-Zugriff)"""
        if hasattr(self, 'template_handler') and self.template_handler:
            return getattr(self.template_handler, 'selected_template', None)
        return None
    
    def create_template_wizard(self):
        """Startet den Template-Wizard für benutzerfreundliche Template-Erstellung"""
        try:
            from views.template_wizard import show_template_wizard
            
            def on_template_created(template_path, template_data):
                """Callback nach erfolgreicher Template-Erstellung"""
                Logger.info(f"Template erstellt: {template_path}")
                
                # Template-Handler aktualisieren falls verfügbar
                if hasattr(self, 'template_handler') and self.template_handler:
                    # Templates neu laden
                    self.template_handler._load_templates()
                    
                    # Neues Template automatisch auswählen
                    template_name = template_data.get('name', 'Neues Template')
                    self.template_handler.selected_template = {
                        'name': template_name,
                        'path': str(template_path),
                        'data': template_data
                    }
                    Logger.info(f"Template '{template_name}' automatisch ausgewählt")
                
                # Erfolgs-Dialog anzeigen
                from services.service_container import service_container
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_success_dialog(
                        f"Template '{template_data.get('name', 'Unbenannt')}' wurde erfolgreich erstellt und ist jetzt verfügbar!",
                        "Template-Wizard erfolgreich"
                    )
            
            # Wizard starten
            show_template_wizard(callback=on_template_created)
            Logger.info("Template-Wizard gestartet")
            
        except Exception as e:
            Logger.error(f"Fehler beim Starten des Template-Wizards: {e}")
            
            # Fehler-Dialog anzeigen
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog(
                    f"Template-Wizard konnte nicht gestartet werden: {str(e)}"
                )
    
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