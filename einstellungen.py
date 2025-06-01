# einstellungen.py (Behoben)
"""
Einstellungen-Widget - Behobene Version mit korrekter Controller-Initialisierung
"""

import os
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.screen import MDScreen

# Service Container Import
from services.service_container import service_container, get_dialog_service, get_theme_service
from services.event_service import EventTypes
from controllers.einstellungen_controller import EinstellungenController

# KV-String direkt eingebettet für bessere Kontrolle
kv_string = '''
<EinstellungenWidget>:
    MDScrollView:
        do_scroll_x: False
        do_scroll_y: True
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(24)
            padding: dp(16)
            size_hint_y: None
            height: self.minimum_height

            # Theme und Farben Card
            MDCard:
                style: "elevated"
                padding: dp(16)
                size_hint_y: None
                height: self.minimum_height
                md_bg_color: app.theme_cls.surfaceColor

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(16)
                    size_hint_y: None
                    height: self.minimum_height

                    # Theme Controls
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(16)

                        MDLabel:
                            text: 'Theme:'
                            size_hint: None, None
                            size: dp(100), dp(40)
                            pos_hint: {"center_y": .5}

                        MDSegmentedButton:
                            MDSegmentedButtonItem:
                                size_hint: None, None
                                size: dp(100), dp(40)
                                on_release: root.switch_theme_style('Light')
                                selected: app.theme_cls.theme_style == 'Light'

                                MDSegmentButtonLabel:
                                    text: "Hell"

                            MDSegmentedButtonItem:
                                size_hint: None, None
                                size: dp(100), dp(40)
                                on_release: root.switch_theme_style('Dark')
                                selected: app.theme_cls.theme_style == 'Dark'

                                MDSegmentButtonLabel:
                                    text: "Dunkel"

                    # Farbschema
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(16)

                        MDLabel:
                            text: 'Farbschema:'
                            size_hint: None, None
                            size: dp(100), dp(40)
                            pos_hint: {"center_y": .5}

                        MDGridLayout:
                            id: colors_box
                            cols: 3
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(8)
                            padding: 0
                            pos_hint: {"center_y": .5}

            # Charakter-Einstellungen Card
            MDCard:
                style: "elevated"
                padding: dp(16)
                size_hint_y: None
                height: self.minimum_height
                md_bg_color: app.theme_cls.surfaceColor

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(20)
                    size_hint_y: None
                    height: self.minimum_height

                    # Startattribute
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(45)
                        spacing: dp(25)

                        MDLabel:
                            text: "Startattributs-Punkte:"
                            size_hint: None, None
                            size: dp(180), dp(40)
                            pos_hint: {"center_y": .5}

                        MDTextField:
                            id: attributsteigerungen_field
                            text: root.get_controller_value('maximale_attributsteigerungen_input', '5')
                            size_hint: None, None
                            size: dp(100), dp(30)
                            input_filter: 'int'
                            pos_hint: {"center_y": .5}
                            on_focus: if not self.focus: root.update_maximale_attributsteigerungen()
                            on_text: root.set_controller_value('maximale_attributsteigerungen_input', self.text)

                    # Startfertigkeiten
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(20)

                        MDLabel:
                            text: "Startfertigkeits-Punkte:"
                            size_hint: None, None
                            size: dp(180), dp(40)
                            pos_hint: {"center_y": .5}

                        MDTextField:
                            id: fertigkeitssteigerungen_field
                            text: root.get_controller_value('maximale_fertigkeitssteigerungen_input', '12')
                            size_hint: None, None
                            size: dp(100), dp(30)
                            pos_hint: {"center_y": .5}
                            input_filter: 'int'
                            on_focus: if not self.focus: root.update_maximale_fertigkeitssteigerungen()
                            on_text: root.set_controller_value('maximale_fertigkeitssteigerungen_input', self.text)

                    # Vermögen Einstellungen
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(16)

                        MDLabel:
                            text: "Vermögen:"
                            size_hint: None, None
                            size: dp(100), dp(40)
                            pos_hint: {"center_y": .5}

                        MDTextField:
                            id: vermoegen_field
                            text: root.get_controller_value('vermoegen_input', '500')
                            size_hint: None, None
                            size: dp(120), dp(30)
                            input_filter: 'int'
                            on_focus: if not self.focus: root.update_vermoegen()
                            on_text: root.set_controller_value('vermoegen_input', self.text)
                            pos_hint: {"center_y": .5}

                        MDTextField:
                            id: waehrung_field
                            text: root.get_controller_value('waehrung_input', 'Gold')
                            size_hint: None, None
                            size: dp(100), dp(40)
                            on_focus: if not self.focus: root.update_waehrung()
                            on_text: root.set_controller_value('waehrung_input', self.text)
                            pos_hint: {"center_y": .5}

                    MDButton:
                        style: "elevated"
                        size_hint: None, None
                        size: dp(300), dp(40)
                        pos_hint: {"left": 1}
                        on_release: root.erhoehe_startkapital()
                        
                        MDButtonText:
                            text: 'Erhöhe Startkapital mit Handicap-Punkten'

                    MDGridLayout:
                        cols: 2
                        spacing: dp(8)
                        size_hint_y: None
                        height: dp(48)

                        MDButton:
                            style: "tonal"
                            size_hint_x: 1
                            on_release: root.erhoehe_aufstieg()

                            MDButtonIcon:
                                icon: "plus"

                            MDButtonText:
                                text: "Aufstieg"

                        MDButton:
                            style: "outlined"
                            size_hint_x: 1
                            on_release: root.senke_aufstieg()

                            MDButtonIcon:
                                icon: "minus"

                            MDButtonText:
                                text: "Abstieg"

            # Verwaltungs Card
            MDCard:
                padding: dp(16)
                spacing: dp(16)
                size_hint_y: None
                height: self.minimum_height

                MDGridLayout:
                    cols: 2
                    spacing: dp(16)
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(8)

                    # Linke Spalte - Grundfunktionen
                    MDBoxLayout:
                        orientation: 'vertical'
                        spacing: dp(16)
                        size_hint_y: None
                        height: self.minimum_height

                        # Charakter-Verwaltung
                        MDBoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(8)

                            MDLabel:
                                text: "Charakter"
                                bold: True

                            MDGridLayout:
                                cols: 3
                                spacing: dp(8)
                                size_hint_y: None
                                height: dp(48)

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1
                                    on_release: root.create_new_character()

                                    MDButtonIcon:
                                        icon: "plus"

                                    MDButtonText:
                                        text: "Neu"

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1
                                    on_release: root.speichere_charakter()

                                    MDButtonIcon:
                                        icon: "content-save"

                                    MDButtonText:
                                        text: "Speichern"

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1
                                    on_release: root.lade_charakter()

                                    MDButtonIcon:
                                        icon: "folder-open"

                                    MDButtonText:
                                        text: "Laden"

                        # Setting-Verwaltung
                        MDBoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(8)

                            MDLabel:
                                text: "Setting"
                                bold: True

                            MDGridLayout:
                                cols: 3
                                spacing: dp(8)
                                size_hint_y: None
                                height: dp(48)

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1
                                    on_release: root.open_add_setting_popup()
                                    MDButtonIcon:
                                        icon: "plus"
                                    MDButtonText:
                                        text: "Neu"

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1
                                    on_release: root.open_load_setting_popup()
                                    MDButtonIcon:
                                        icon: "folder-open"
                                    MDButtonText:
                                        text: "Laden"

                                MDButton:
                                    style: "outlined"
                                    size_hint_x: 1
                                    on_release: root.open_delete_setting_popup()
                                    MDButtonIcon:
                                        icon: "delete"
                                    MDButtonText:
                                        text: "Löschen"

                    # Rechte Spalte - PDF und weitere Funktionen
                    MDBoxLayout:
                        orientation: 'vertical'
                        spacing: dp(16)
                        size_hint_y: None
                        height: self.minimum_height

                        MDButton:
                            style: "filled"
                            size_hint_x: 1
                            on_release: root.erzeuge_charakterbogen_pdf()

                            MDButtonIcon:
                                icon: "file-pdf-box"

                            MDButtonText:
                                text: "PDF erstellen"

            # Spielelemente Card (gekürzt für bessere Übersichtlichkeit)
            MDCard:
                padding: dp(16)
                spacing: dp(16)
                size_hint_y: None
                height: self.minimum_height

                MDLabel:
                    text: "Spielelemente-Verwaltung"
                    bold: True
                    size_hint_y: None
                    height: dp(40)

                MDGridLayout:
                    cols: 4
                    spacing: dp(8)
                    size_hint_y: None
                    height: self.minimum_height

                    # Völker
                    MDButton:
                        style: "elevated"
                        size_hint_x: 1
                        on_release: root.open_add_volk_dialog()
                        MDButtonIcon:
                            icon: "account-group"
                        MDButtonText:
                            text: "Völker"

                    # Talente
                    MDButton:
                        style: "elevated"
                        size_hint_x: 1
                        on_release: root.open_add_talent_popup()
                        MDButtonIcon:
                            icon: "star-circle"
                        MDButtonText:
                            text: "Talente"

                    # Mächte
                    MDButton:
                        style: "elevated"
                        size_hint_x: 1
                        on_release: root.open_add_macht_popup()
                        MDButtonIcon:
                            icon: "creation-outline"
                        MDButtonText:
                            text: "Mächte"

                    # Ausrüstung
                    MDButton:
                        style: "elevated"
                        size_hint_x: 1
                        on_release: root.open_add_ausruestung_popup()
                        MDButtonIcon:
                            icon: "sack"
                        MDButtonText:
                            text: "Ausrüstung"
'''


class EinstellungenWidget(MDScreen):
    """
    Hauptwidget für Einstellungen
    Nutzt Service Container für Dependency Injection
    """
    
    controller = ObjectProperty(None, allownone=True)
    
    def __init__(self, **kwargs):
        # Controller sofort initialisieren, bevor das Widget aufgebaut wird
        self.app = App.get_running_app()
        self.einstellungen_controller = None
        
        # Controller-Initialisierung versuchen
        self._initialize_controller()
        
        # Parent initialisieren (löst KV-Aufbau aus)
        super().__init__(**kwargs)
        
        # Event-Handler registrieren
        self._register_event_handlers()
        
        # UI nach vollständiger Initialisierung aufbauen
        Clock.schedule_once(self._post_init, 0)
    
    def _initialize_controller(self):
        """Initialisiert den Controller früh"""
        try:
            if hasattr(self.app, 'controller') and self.app.controller:
                self.einstellungen_controller = EinstellungenController(self.app.controller)
                self.controller = self.einstellungen_controller
                
                # Service Container initialisieren
                service_container.initialize(self.app.controller)
                Logger.info("Controller und Services erfolgreich initialisiert")
            else:
                Logger.warning("App-Controller nicht verfügbar")
                
        except Exception as e:
            Logger.error(f"Fehler bei Controller-Initialisierung: {str(e)}", exc_info=True)
    
    def get_controller_value(self, attr_name, default=''):
        """
        Sichere Methode zum Abrufen von Controller-Werten
        
        Args:
            attr_name (str): Name des Attributs
            default (str): Standardwert falls Controller nicht verfügbar
            
        Returns:
            str: Wert oder Standardwert
        """
        try:
            if self.einstellungen_controller and hasattr(self.einstellungen_controller, attr_name):
                return str(getattr(self.einstellungen_controller, attr_name))
            return str(default)
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen von {attr_name}: {str(e)}")
            return str(default)
    
    def set_controller_value(self, attr_name, value):
        """
        Sichere Methode zum Setzen von Controller-Werten
        
        Args:
            attr_name (str): Name des Attributs
            value: Neuer Wert
        """
        try:
            if self.einstellungen_controller and hasattr(self.einstellungen_controller, attr_name):
                setattr(self.einstellungen_controller, attr_name, value)
        except Exception as e:
            Logger.error(f"Fehler beim Setzen von {attr_name}: {str(e)}")
    
    def _register_event_handlers(self):
        """Registriert Event-Handler für verschiedene Events"""
        try:
            event_service = service_container.get_event_service()
            if event_service:
                # Character-Events
                event_service.subscribe(EventTypes.CHARACTER_CREATED, self._on_character_created)
                event_service.subscribe(EventTypes.CHARACTER_LOADED, self._on_character_loaded)
                event_service.subscribe(EventTypes.THEME_CHANGED, self._on_theme_changed)
                
                Logger.debug("Event-Handler für Einstellungen registriert")
        except Exception as e:
            Logger.error(f"Fehler bei Event-Handler-Registrierung: {str(e)}")
    
    def _post_init(self, dt):
        """Post-Initialisierung nach dem UI-Aufbau"""
        try:
            # Theme initialisieren
            theme_service = service_container.get_theme_service()
            if theme_service:
                theme_service.initialize_theme()
                
                # Farb-Chips erstellen
                if hasattr(self.ids, 'colors_box'):
                    theme_service.create_color_chips(
                        self.ids.colors_box, 
                        self.on_color_selected
                    )
            
            # UI-Felder mit aktuellen Werten aktualisieren
            self._update_ui_fields()
            
            # Event senden
            event_service = service_container.get_event_service()
            if event_service:
                event_service.publish(EventTypes.TAB_CHANGED, {'tab': 'Einstellungen'})
            
        except Exception as e:
            Logger.error(f"Fehler bei Post-Initialisierung: {str(e)}", exc_info=True)
    
    # Event-Handler
    def _on_character_created(self, data):
        """Wird aufgerufen, wenn ein neuer Charakter erstellt wurde"""
        Logger.info(f"Neuer Charakter erstellt: {data}")
        self._update_ui_fields()
    
    def _on_character_loaded(self, data):
        """Wird aufgerufen, wenn ein Charakter geladen wurde"""
        Logger.info(f"Charakter geladen: {data}")
        self._update_ui_fields()
    
    def _on_theme_changed(self, data):
        """Wird aufgerufen, wenn das Theme geändert wurde"""
        Logger.info(f"Theme geändert: {data}")
        # Farb-Chips aktualisieren
        theme_service = service_container.get_theme_service()
        if theme_service and hasattr(self.ids, 'colors_box'):
            theme_service.create_color_chips(
                self.ids.colors_box, 
                self.on_color_selected
            )
    
    # Theme-Management
    def switch_theme_style(self, style):
        """Wechselt den Theme-Stil"""
        theme_service = service_container.get_theme_service()
        if theme_service:
            theme_service.switch_theme_style(style)
            
            # Event senden
            event_service = service_container.get_event_service()
            if event_service:
                event_service.publish(EventTypes.THEME_CHANGED, {'style': style})
    
    def on_color_selected(self, color_name):
        """Callback für Farbauswahl"""
        theme_service = service_container.get_theme_service()
        if theme_service and theme_service.switch_primary_palette(color_name):
            # Event senden
            event_service = service_container.get_event_service()
            if event_service:
                event_service.publish(EventTypes.THEME_CHANGED, {'color': color_name})
    
    # Charakter-Verwaltung (vereinfacht für Stabilität)
    def create_new_character(self):
        """Startet den Prozess zur Erstellung eines neuen Charakters"""
        dialog_service = service_container.get_dialog_service()
        if not dialog_service:
            Logger.error("Dialog-Service nicht verfügbar")
            return
        
        dialog_service.show_input_dialog(
            "Bitte gib einen Namen für den neuen Charakter ein:",
            "Neuen Charakter erstellen",
            "",
            self._on_new_character_name
        )
    
    def _on_new_character_name(self, character_name):
        """Verarbeitet den eingegebenen Charakternamen"""
        if not character_name.strip():
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog("Bitte gib einen Namen für den Charakter ein.")
            return
        
        if self.einstellungen_controller:
            success = self.einstellungen_controller.create_new_character(character_name)
            dialog_service = service_container.get_dialog_service()
            
            if success and dialog_service:
                # Event senden
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish(EventTypes.CHARACTER_CREATED, {'name': character_name})
                
                dialog_service.show_success_dialog(
                    f"Der Charakter '{character_name}' wurde erfolgreich erstellt.",
                    "Neuer Charakter erstellt"
                )
            elif dialog_service:
                dialog_service.show_error_dialog("Fehler beim Erstellen des Charakters.")
    
    def speichere_charakter(self):
        """Startet den Speicherprozess für den Charakter"""
        if not self.einstellungen_controller:
            Logger.error("Controller nicht verfügbar")
            return
        
        # Vereinfachte Speicherung ohne komplexe Dialoge
        current_path = self.einstellungen_controller.get_current_file_path()
        
        if current_path:
            success = self.einstellungen_controller.save_character(current_path)
            dialog_service = service_container.get_dialog_service()
            
            if success and dialog_service:
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish(EventTypes.CHARACTER_SAVED, {'path': current_path})
                
                dialog_service.show_success_dialog(
                    "Charakter wurde erfolgreich gespeichert.",
                    "Speichern erfolgreich"
                )
            elif dialog_service:
                dialog_service.show_error_dialog("Fehler beim Speichern des Charakters.")
        else:
            # Als neue Datei speichern
            file_service = service_container.get_file_manager_service()
            if file_service:
                chars_dir = file_service.get_default_directory('chars')
                file_service.show_file_manager(chars_dir, "save_dir")
    
    def lade_charakter(self):
        """Öffnet den Lade-Dialog für Charaktere"""
        file_service = service_container.get_file_manager_service()
        if file_service:
            chars_dir = file_service.get_default_directory('chars')
            file_service.show_file_manager(chars_dir, "load")
    
    # Charakterwerte-Updates
    def update_vermoegen(self):
        """Aktualisiert das Vermögen"""
        if self.einstellungen_controller:
            success = self.einstellungen_controller.update_vermoegen()
            if not success:
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_error_dialog(self.einstellungen_controller.fehler_meldung)
    
    def update_waehrung(self):
        """Aktualisiert die Währung"""
        if self.einstellungen_controller:
            success = self.einstellungen_controller.update_waehrung()
            if success:
                self._update_ui_after_character_change()
    
    def update_maximale_attributsteigerungen(self):
        """Aktualisiert die maximalen Attributsteigerungen"""
        if self.einstellungen_controller:
            success = self.einstellungen_controller.update_maximale_attributsteigerungen()
            if not success:
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_error_dialog(self.einstellungen_controller.fehler_meldung)
    
    def update_maximale_fertigkeitssteigerungen(self):
        """Aktualisiert die maximalen Fertigkeitssteigerungen"""
        if self.einstellungen_controller:
            success = self.einstellungen_controller.update_maximale_fertigkeitssteigerungen()
            if not success:
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_error_dialog(self.einstellungen_controller.fehler_meldung)
    
    # Charakter-Operationen
    def erhoehe_aufstieg(self):
        """Erhöht die Aufstiege"""
        if self.einstellungen_controller:
            self.einstellungen_controller.erhoehe_aufstieg()
    
    def senke_aufstieg(self):
        """Senkt die Aufstiege"""
        if self.einstellungen_controller:
            self.einstellungen_controller.senke_aufstieg()
    
    def erhoehe_startkapital(self):
        """Erhöht das Startkapital"""
        if self.einstellungen_controller:
            success = self.einstellungen_controller.erhoehe_startkapital()
            if success:
                self._update_ui_fields()
    
    # PDF-Erstellung (vereinfacht)
    def erzeuge_charakterbogen_pdf(self):
        """Startet den PDF-Erstellungsprozess"""
        pdf_service = service_container.get_pdf_service()
        dialog_service = service_container.get_dialog_service()
        
        if not pdf_service or not dialog_service:
            Logger.error("Erforderliche Services nicht verfügbar")
            return
        
        # Vereinfachte PDF-Erstellung
        default_name = pdf_service.get_default_pdf_name()
        
        # Direkt erstellen ohne komplexe Dialoge
        chars_dir = service_container.get_file_manager_service().get_default_directory('chars') if service_container.get_file_manager_service() else ""
        pdf_path = os.path.join(chars_dir, default_name) if chars_dir else default_name
        
        success = pdf_service.create_character_pdf(pdf_path, printer_friendly=False)
        if success:
            event_service = service_container.get_event_service()
            if event_service:
                event_service.publish(EventTypes.PDF_CREATED, {'path': pdf_path})
            
            dialog_service.show_success_dialog(
                f"PDF wurde gespeichert als:\n{pdf_path}",
                "PDF erstellen erfolgreich"
            )
        else:
            dialog_service.show_error_dialog("Fehler beim Erstellen der PDF-Datei.")
    
    # Element-Dialog-Delegierung (vereinfacht)
    def open_add_setting_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_setting_popup()
    
    def open_load_setting_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_load_setting_popup()
    
    def open_delete_setting_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_setting_popup()
    
    def open_add_volk_dialog(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_volk_dialog()
    
    def open_add_talent_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_talent_popup()
    
    def open_add_macht_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_macht_popup()
    
    def open_add_ausruestung_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_ausruestung_popup()
    
    # UI-Update-Methoden
    def _update_ui_fields(self):
        """Aktualisiert die UI-Felder mit aktuellen Werten"""
        if not self.einstellungen_controller:
            return
        
        try:
            # Vermögen-Feld aktualisieren
            if hasattr(self.ids, 'vermoegen_field'):
                self.ids.vermoegen_field.text = self.einstellungen_controller.vermoegen_input
            
            # Währung-Feld aktualisieren  
            if hasattr(self.ids, 'waehrung_field'):
                self.ids.waehrung_field.text = self.einstellungen_controller.waehrung_input
            
            # Attributsteigerungen-Feld aktualisieren
            if hasattr(self.ids, 'attributsteigerungen_field'):
                self.ids.attributsteigerungen_field.text = self.einstellungen_controller.maximale_attributsteigerungen_input
            
            # Fertigkeitssteigerungen-Feld aktualisieren
            if hasattr(self.ids, 'fertigkeitssteigerungen_field'):
                self.ids.fertigkeitssteigerungen_field.text = self.einstellungen_controller.maximale_fertigkeitssteigerungen_input
                
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der UI-Felder: {str(e)}")
    
    def _update_ui_after_character_change(self):
        """Aktualisiert die UI nach Änderungen am Charakter"""
        if self.einstellungen_controller:
            self.einstellungen_controller.update_ui()
        
        # Event senden
        event_service = service_container.get_event_service()
        if event_service:
            event_service.publish(EventTypes.CHARACTER_UPDATED)
    
    def aktualisiere_ui(self):
        """Öffentliche Methode zur UI-Aktualisierung"""
        self._update_ui_after_character_change()
        self._update_ui_fields()
    
    def cleanup(self):
        """Bereinigt das Widget beim Beenden"""
        try:
            # Event-Handler entfernen
            event_service = service_container.get_event_service()
            if event_service:
                event_service.unsubscribe(EventTypes.CHARACTER_CREATED, self._on_character_created)
                event_service.unsubscribe(EventTypes.CHARACTER_LOADED, self._on_character_loaded)
                event_service.unsubscribe(EventTypes.THEME_CHANGED, self._on_theme_changed)
            
            Logger.info("EinstellungenWidget bereinigt")
        except Exception as e:
            Logger.error(f"Fehler beim Bereinigen: {str(e)}")


# KV-Layout laden
try:
    Builder.load_string(kv_string)
    Logger.info("Einstellungen-Layout aus String geladen")
except Exception as e:
    Logger.error(f"Fehler beim Laden des Layouts: {str(e)}")