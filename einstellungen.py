"""
einstellungen.py - Service-basierte Architektur mit vollständigen Spielelementen
"""

import os
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer

# Service Container Import
from services.service_container import service_container, get_dialog_service, get_theme_service
from services.event_service import EventTypes

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
                            text: root.get_charakter_value('maximale_attributsteigerungen', '5')
                            size_hint: None, None
                            size: dp(100), dp(30)
                            input_filter: 'int'
                            pos_hint: {"center_y": .5}
                            on_focus: if not self.focus: root.update_maximale_attributsteigerungen()

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
                            text: root.get_charakter_value('maximale_fertigkeitssteigerungen', '12')
                            size_hint: None, None
                            size: dp(100), dp(30)
                            pos_hint: {"center_y": .5}
                            input_filter: 'int'
                            on_focus: if not self.focus: root.update_maximale_fertigkeitssteigerungen()

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
                            text: root.get_charakter_value('vermoegen', '500')
                            size_hint: None, None
                            size: dp(120), dp(30)
                            input_filter: 'int'
                            on_focus: if not self.focus: root.update_vermoegen()
                            pos_hint: {"center_y": .5}

                        MDTextField:
                            id: waehrung_field
                            text: root.get_charakter_value('waehrungseinheit', 'Gold')
                            size_hint: None, None
                            size: dp(100), dp(40)
                            on_focus: if not self.focus: root.update_waehrung()
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

                        MDButton:
                            style: "elevated"
                            size_hint_x: 1
                            on_release: root.zeige_statblock()

                            MDButtonIcon:
                                icon: "card-text"

                            MDButtonText:
                                text: "Statblock anzeigen"

            # Spielelemente Card - Vollständige Version
            MDCard:
                padding: dp(16)
                spacing: dp(16)
                size_hint_y: None
                height: self.minimum_height

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(16)
                    size_hint_y: None
                    height: self.minimum_height

                    MDLabel:
                        text: "Spielelemente-Verwaltung"
                        bold: True
                        size_hint_y: None
                        height: dp(40)

                    # Volk
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "account-group"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Volk"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_volk_dialog()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_volk_dialog()

                            MDButtonIcon:
                                icon: "minus"

                    # Fertigkeiten
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "fencing"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Fertigkeiten"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_fertigkeit_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_fertigkeit_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Handicaps
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "account-alert"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Handicaps"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_handicap_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_handicap_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Talente
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "star-circle"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Talente"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_talent_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_talent_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Mächte
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "creation-outline"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Mächte"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_macht_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_macht_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Ausrüstung
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "sack"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Ausrüstung"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_ausruestung_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_ausruestung_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Rüstung
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "shield"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Rüstung"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_ruestung_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_ruestung_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Waffen
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "sword"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Waffe"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_waffe_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_waffe_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Schild
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "shield"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Schild"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_schild_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_schild_popup()

                            MDButtonIcon:
                                icon: "minus"
'''


class EinstellungenWidget(MDScreen):
    """
    Hauptwidget für Einstellungen
    Nutzt Service Container für Dependency Injection
    """
    
    controller = ObjectProperty(None, allownone=True)
    
    def __init__(self, **kwargs):
        # App und Controller-Initialisierung
        self.app = App.get_running_app()
        self.charakter_controller = None
        
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
                self.charakter_controller = self.app.controller
                self.controller = self.charakter_controller
                
                # Service Container initialisieren
                service_container.initialize(self.app.controller)
                Logger.info("Controller und Services erfolgreich initialisiert")
            else:
                Logger.warning("App-Controller nicht verfügbar")
                
        except Exception as e:
            Logger.error(f"Fehler bei Controller-Initialisierung: {str(e)}", exc_info=True)
    
    def get_charakter_value(self, attr_name, default=''):
        """
        Sichere Methode zum Abrufen von Charakter-Werten
        
        Args:
            attr_name (str): Name des Attributs
            default (str): Standardwert falls Charakter nicht verfügbar
            
        Returns:
            str: Wert oder Standardwert
        """
        try:
            if self.charakter_controller and hasattr(self.charakter_controller, 'charakter'):
                charakter = self.charakter_controller.charakter
                if charakter and hasattr(charakter, attr_name):
                    return str(getattr(charakter, attr_name))
            return str(default)
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen von {attr_name}: {str(e)}")
            return str(default)
    
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
    
    # Charakter-Verwaltung (direkter Zugriff auf CharakterController)
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
        
        if self.charakter_controller:
            # Direkte Verwendung des CharakterController aus main.py
            success = self.charakter_controller.neuer_charakter(character_name)
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
                
                # Aktualisiere alle UIs
                self._trigger_ui_refresh()
                
            elif dialog_service:
                dialog_service.show_error_dialog("Fehler beim Erstellen des Charakters.")
        else:
            Logger.error("CharakterController nicht verfügbar")
    
    def _trigger_ui_refresh(self):
        """Löst eine Aktualisierung aller UI-Komponenten aus"""
        try:
            # Aktualisiere alle Widget-Tabs über die App
            if hasattr(self.app, 'refresh_current_tab'):
                Clock.schedule_once(lambda dt: self.app.refresh_current_tab(), 0.1)
            
            # Aktualisiere eigene UI-Felder
            Clock.schedule_once(lambda dt: self._update_ui_fields(), 0.1)
            
        except Exception as e:
            Logger.error(f"Fehler bei UI-Refresh: {str(e)}")
    
    def speichere_charakter(self):
        """Zeigt einen Dialog mit Optionen zum Speichern des Charakters"""
        if not self.charakter_controller:
            Logger.error("Controller nicht verfügbar")
            return
        
        # Prüfen, ob bereits ein Dateipfad existiert
        current_path = getattr(self.charakter_controller, 'current_character_file_path', None)
        
        # Dialog-Inhalt für Speicher-Optionen erstellen
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivy.uix.widget import Widget
        
        buttons_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),  # Mehr Abstand zwischen Elementen
            size_hint_y=None,
            height=dp(200),  # Mehr Höhe für bessere Darstellung
            padding=dp(20)   # Mehr Padding
        )
        
        # Wenn eine Datei existiert, zeige den Überschreiben-Button
        if current_path:
            filename = os.path.basename(current_path)
            
            info_label = MDLabel(
                text=f"Bestehende Datei:\n{filename}",  # Zeilenumbruch für längere Namen
                size_hint_y=None,
                height=dp(60),  # Mehr Höhe für mehrzeiligen Text
                halign="center",
                valign="middle",
                text_size=(None, None)  # Automatische Textgröße
            )
            buttons_container.add_widget(info_label)
            
            # Button zum Überschreiben
            ueberschreiben_button = MDButton(
                style="elevated",
                size_hint=(1, None),
                height=dp(48),  # Standard-Button-Höhe
                on_release=lambda x: self._ueberschreibe_existierende_datei(current_path)
            )
            ueberschreiben_button.add_widget(MDButtonText(text="Bestehende Datei überschreiben"))
            buttons_container.add_widget(ueberschreiben_button)
        
        # Button für "Als neue Datei speichern" (ohne Spacer)
        new_file_button = MDButton(
            style="elevated",
            size_hint=(1, None),
            height=dp(48),  # Standard-Button-Höhe
            on_release=lambda x: self._als_neue_datei_speichern()
        )
        new_file_button.add_widget(MDButtonText(text="Als neue Datei speichern..."))
        buttons_container.add_widget(new_file_button)
        
        # Dialog erstellen und anzeigen
        self.save_options_dialog = MDDialog(
            MDDialogHeadlineText(text="Charakter speichern"),
            MDDialogContentContainer(buttons_container),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self.save_options_dialog.dismiss()
                )
            )
        )
        self.save_options_dialog.open()
    
    def _ueberschreibe_existierende_datei(self, filepath):
        """Überschreibt die existierende Datei direkt"""
        self.save_options_dialog.dismiss()
        
        if self.charakter_controller:
            success = self.charakter_controller.speichere_charakter_als_json(filepath)
            dialog_service = service_container.get_dialog_service()
            
            if success and dialog_service:
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish(EventTypes.CHARACTER_SAVED, {'path': filepath})
                
                dialog_service.show_success_dialog(
                    "Charakter wurde in bestehender Datei gespeichert.",
                    "Speichern erfolgreich"
                )
            elif dialog_service:
                dialog_service.show_error_dialog("Fehler beim Speichern des Charakters.")
    
    def _als_neue_datei_speichern(self):
        """Zeigt einen Dialog zum Eingeben eines Dateinamens"""
        self.save_options_dialog.dismiss()
        
        # Standardname basierend auf Charakternamen
        character_name = "charakter"
        if self.charakter_controller and self.charakter_controller.charakter:
            character_name = self.charakter_controller.charakter.char_name or "charakter"
        
        default_filename = f"{character_name.strip().replace(' ', '_')}.json"
        
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.show_input_dialog(
                "Dateiname für neue Datei:",
                "Als neue Datei speichern",
                default_filename,
                self._on_save_filename_entered
            )
    
    def _on_save_filename_entered(self, filename):
        """Verarbeitet den eingegebenen Dateinamen für das Speichern"""
        if not filename or not filename.strip():
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog("Bitte gib einen Dateinamen ein.")
            return
        
        # Stellt sicher, dass die Dateiendung .json ist
        if not filename.lower().endswith('.json'):
            filename += '.json'
        
        # FileManager Service für Verzeichnisauswahl
        file_service = service_container.get_file_manager_service()
        if file_service:
            file_service.set_temp_filename(filename)
            # chars ist ein Hauptordner, kein Unterordner
            chars_dir = file_service.get_default_directory('chars')
            file_service.show_file_manager(chars_dir, "save_dir")
    
    def lade_charakter(self):
        """Öffnet den Lade-Dialog für Charaktere"""
        file_service = service_container.get_file_manager_service()
        if file_service:
            # chars ist ein Hauptordner, kein Unterordner
            chars_dir = file_service.get_default_directory('chars')
            file_service.show_file_manager(chars_dir, "load")
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog("File-Manager-Service nicht verfügbar.")
    
    # Charakterwerte-Updates
    def update_vermoegen(self):
        """Aktualisiert das Vermögen"""
        if self.charakter_controller and self.charakter_controller.charakter:
            try:
                new_value = int(self.ids.vermoegen_field.text)
                self.charakter_controller.charakter.vermoegen = new_value
                Logger.info(f"Vermögen auf {new_value} aktualisiert")
            except ValueError:
                Logger.error("Ungültiger Wert für Vermögen eingegeben")
    
    def update_waehrung(self):
        """Aktualisiert die Währung"""
        if self.charakter_controller and self.charakter_controller.charakter:
            new_value = self.ids.waehrung_field.text
            self.charakter_controller.charakter.waehrungseinheit = new_value
            Logger.info(f"Währung auf '{new_value}' aktualisiert")
    
    def update_maximale_attributsteigerungen(self):
        """Aktualisiert die maximalen Attributsteigerungen"""
        if self.charakter_controller and self.charakter_controller.charakter:
            try:
                new_value = int(self.ids.attributsteigerungen_field.text)
                self.charakter_controller.charakter.maximale_attributsteigerungen = new_value
                self.charakter_controller.charakter.verbleibende_attributsteigerungen = new_value
                Logger.info(f"Maximale Attributsteigerungen auf {new_value} aktualisiert")
            except ValueError:
                Logger.error("Ungültiger Wert für Attributsteigerungen eingegeben")
    
    def update_maximale_fertigkeitssteigerungen(self):
        """Aktualisiert die maximalen Fertigkeitssteigerungen"""
        if self.charakter_controller and self.charakter_controller.charakter:
            try:
                new_value = int(self.ids.fertigkeitssteigerungen_field.text)
                self.charakter_controller.charakter.maximale_fertigkeitssteigerungen = new_value
                self.charakter_controller.charakter.verbleibende_fertigkeitssteigerungen = new_value
                Logger.info(f"Maximale Fertigkeitssteigerungen auf {new_value} aktualisiert")
            except ValueError:
                Logger.error("Ungültiger Wert für Fertigkeitssteigerungen eingegeben")
    
    # Charakter-Operationen
    def erhoehe_aufstieg(self):
        """Erhöht die Aufstiege"""
        if self.charakter_controller and self.charakter_controller.charakter:
            self.charakter_controller.charakter.increase_aufstiege()
    
    def senke_aufstieg(self):
        """Senkt die Aufstiege"""
        if self.charakter_controller and self.charakter_controller.charakter:
            self.charakter_controller.charakter.decrease_aufstiege()
    
    def erhoehe_startkapital(self):
        """Erhöht das Startkapital"""
        if self.charakter_controller and self.charakter_controller.charakter:
            success = self.charakter_controller.charakter.erhoehe_startkapital()
            if success:
                self._update_ui_fields()
    
    # Statblock-Funktionalität
    def zeige_statblock(self):
        """Zeigt den Charakterstatblock in einem Dialog an"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.show_statblock_dialog()
        else:
            Logger.error("Dialog-Service nicht verfügbar")
    
    # PDF-Erstellung mit vollständigen Optionen
    def erzeuge_charakterbogen_pdf(self):
        """Startet den PDF-Erstellungsprozess mit Optionen"""
        pdf_service = service_container.get_pdf_service()
        dialog_service = service_container.get_dialog_service()
        
        if not pdf_service or not dialog_service:
            Logger.error("Erforderliche Services nicht verfügbar")
            return
        
        # Prüfen, ob bereits eine PDF-Datei existiert
        exists, existing_path, existing_name = pdf_service.check_existing_pdf()
        
        # Dialog-Inhalt für PDF-Optionen erstellen
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.selectioncontrol import MDCheckbox
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            size_hint_y=None,
            height=dp(200),  # Feste Höhe statt adaptive_height
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
            height=dp(100)  # Feste Höhe statt self.minimum_height
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
            )
        )
        self.pdf_options_dialog.open()
    
    def _create_pdf_at_path(self, pdf_path, close_dialog=False):
        """Erstellt PDF am angegebenen Pfad"""
        if close_dialog and hasattr(self, 'pdf_options_dialog'):
            self.pdf_options_dialog.dismiss()
        
        pdf_service = service_container.get_pdf_service()
        dialog_service = service_container.get_dialog_service()
        
        if pdf_service and dialog_service:
            printer_friendly = getattr(self, 'printer_friendly_checkbox', None)
            is_printer_friendly = printer_friendly.active if printer_friendly else False
            
            success = pdf_service.create_character_pdf(pdf_path, is_printer_friendly)
            
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
    
    def _start_new_pdf_creation(self):
        """Startet den Prozess für neue PDF-Erstellung"""
        self.pdf_options_dialog.dismiss()
        
        dialog_service = service_container.get_dialog_service()
        pdf_service = service_container.get_pdf_service()
        
        if dialog_service and pdf_service:
            default_name = pdf_service.get_default_pdf_name()
            
            dialog_service.show_input_dialog(
                "Dateiname für neue PDF:",
                "Als neue PDF speichern",
                default_name,
                self._on_pdf_filename_entered
            )
    
    def _on_pdf_filename_entered(self, filename):
        """Verarbeitet den eingegebenen PDF-Dateinamen"""
        if not filename or not filename.strip():
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog("Bitte gib einen Dateinamen ein.")
            return
        
        # PDF-Endung sicherstellen
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        # Checkbox-Status merken für später
        printer_friendly = getattr(self, 'printer_friendly_checkbox', None)
        self.temp_printer_friendly = printer_friendly.active if printer_friendly else False
        
        # FileManager Service für Verzeichnisauswahl
        file_service = service_container.get_file_manager_service()
        if file_service:
            file_service.set_temp_pdf_settings(filename, self.temp_printer_friendly)
            # chars ist ein Hauptordner, kein Unterordner
            chars_dir = file_service.get_default_directory('chars')
            file_service.show_file_manager(chars_dir, "save_pdf_dir")
    
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
    
    def open_delete_volk_dialog(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_volk_dialog()
    
    def open_add_talent_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_talent_popup()
    
    def open_delete_talent_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_talent_popup()
    
    def open_add_macht_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_macht_popup()
    
    def open_delete_macht_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_macht_popup()
    
    def open_add_fertigkeit_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_fertigkeit_popup()
    
    def open_delete_fertigkeit_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_fertigkeit_popup()
    
    def open_add_handicap_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_handicap_popup()
    
    def open_delete_handicap_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_handicap_popup()
    
    def open_add_ausruestung_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_ausruestung_popup()
    
    def open_delete_ausruestung_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_ausruestung_popup()
    
    def open_add_waffe_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_waffe_popup()
    
    def open_delete_waffe_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_waffe_popup()
    
    def open_add_ruestung_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_ruestung_popup()
    
    def open_delete_ruestung_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_ruestung_popup()
    
    def open_add_schild_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_schild_popup()
    
    def open_delete_schild_popup(self):
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_schild_popup()
    
    # UI-Update-Methoden
    def _update_ui_fields(self):
        """Aktualisiert die UI-Felder mit aktuellen Werten"""
        if not self.charakter_controller or not self.charakter_controller.charakter:
            return
        
        try:
            charakter = self.charakter_controller.charakter
            
            # Vermögen-Feld aktualisieren
            if hasattr(self.ids, 'vermoegen_field'):
                self.ids.vermoegen_field.text = str(charakter.vermoegen)
            
            # Währung-Feld aktualisieren  
            if hasattr(self.ids, 'waehrung_field'):
                self.ids.waehrung_field.text = str(charakter.waehrungseinheit)
            
            # Attributsteigerungen-Feld aktualisieren
            if hasattr(self.ids, 'attributsteigerungen_field'):
                self.ids.attributsteigerungen_field.text = str(charakter.maximale_attributsteigerungen)
            
            # Fertigkeitssteigerungen-Feld aktualisieren
            if hasattr(self.ids, 'fertigkeitssteigerungen_field'):
                self.ids.fertigkeitssteigerungen_field.text = str(charakter.maximale_fertigkeitssteigerungen)
                
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der UI-Felder: {str(e)}")
    
    def _update_ui_after_character_change(self):
        """Aktualisiert die UI nach Änderungen am Charakter"""
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