# views/einstellungen_widget.py
"""
Refactored Einstellungen Widget - Nur UI-Logik und Delegation
Verwendet Manager-Klassen für verschiedene Funktionalitätsbereiche
"""

import os
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen

# Manager Imports
from .theme_manager import ThemeManager
from .pdf_manager import PDFManager
from .element_dialog_manager import ElementDialogManager
from .statistics_manager import StatisticsManager

# Service Container Import
from services.service_container import service_container
from services.event_service import EventTypes


class EinstellungenWidget(MDScreen):
    """
    Hauptwidget für Einstellungen - Refactored Version
    Delegiert Funktionalitäten an spezialisierte Manager
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
        
        # Manager initialisieren
        self._initialize_managers()
        
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
    
    def _initialize_managers(self):
        """Initialisiert alle Manager"""
        try:
            self.theme_manager = ThemeManager(self)
            self.pdf_manager = PDFManager(self)
            self.element_dialog_manager = ElementDialogManager(self)
            self.statistics_manager = StatisticsManager(self)
            
            Logger.info("Alle Manager erfolgreich initialisiert")
            
        except Exception as e:
            Logger.error(f"Fehler bei Manager-Initialisierung: {str(e)}", exc_info=True)
    
    def get_charakter_value(self, attr_name, default=''):
        """
        Sichere Methode zum Abrufen von Charakter-Werten
        
        Args:
            attr_name (str): Name des Attributs
            default (str): Standardwert falls Charakter nicht verfügbar
            
        Returns:
            str: Wert oder Standardwert (immer als String)
        """
        try:
            if self.charakter_controller and hasattr(self.charakter_controller, 'charakter'):
                charakter = self.charakter_controller.charakter
                if charakter and hasattr(charakter, attr_name):
                    value = getattr(charakter, attr_name)
                    return str(value)  # Immer als String zurückgeben
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
            self.theme_manager.initialize_theme()
            
            # UI-Felder mit aktuellen Werten aktualisieren
            self._update_ui_fields()
            
            # Element-Statistiken anzeigen
            self.statistics_manager.update_element_statistics_ui()
            
            # Event senden
            event_service = service_container.get_event_service()
            if event_service:
                event_service.publish(EventTypes.TAB_CHANGED, {'tab': 'Einstellungen'})
            
        except Exception as e:
            Logger.error(f"Fehler bei Post-Initialisierung: {str(e)}", exc_info=True)
    
    # ==================== EVENT HANDLERS ====================
    
    def _on_character_created(self, data):
        """Wird aufgerufen, wenn ein neuer Charakter erstellt wurde"""
        Logger.info(f"Neuer Charakter erstellt: {data}")
        self._update_ui_fields()
        self.statistics_manager.update_element_statistics_ui()
    
    def _on_character_loaded(self, data):
        """Wird aufgerufen, wenn ein Charakter geladen wurde"""
        Logger.info(f"Charakter geladen: {data}")
        self._update_ui_fields()
        self.statistics_manager.update_element_statistics_ui()
    
    def _on_theme_changed(self, data):
        """Wird aufgerufen, wenn das Theme geändert wurde"""
        Logger.info(f"Theme geändert: {data}")
        self.theme_manager.update_color_chips()
    
    # ==================== THEME MANAGEMENT ====================
    
    def switch_theme_style(self, style):
        """Delegiert an ThemeManager"""
        self.theme_manager.switch_theme_style(style)
    
    def on_color_selected(self, color_name):
        """Delegiert an ThemeManager"""
        self.theme_manager.on_color_selected(color_name)
    
    # ==================== CHARAKTER MANAGEMENT ====================
    
    def create_new_character(self):
        """Delegiert an EinstellungenController"""
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
            # Direkte Verwendung des CharakterController
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
    
    def speichere_charakter(self):
        """Delegiert Speicher-Logik"""
        # Hier könnte man eine vereinfachte Version implementieren
        # oder direkt an den FileManager delegieren
        file_service = service_container.get_file_manager_service()
        if file_service:
            chars_dir = file_service.get_default_directory('chars')
            file_service.show_file_manager(chars_dir, "save_dir")
    
    def lade_charakter(self):
        """Delegiert Lade-Logik"""
        file_service = service_container.get_file_manager_service()
        if file_service:
            chars_dir = file_service.get_default_directory('chars')
            file_service.show_file_manager(chars_dir, "load")
    
    # ==================== SETTING MANAGEMENT ====================
    
    def open_setting_switch_options(self):
        """Vereinfachte Setting-Wechsel-Logik"""
        if not self.charakter_controller or not self.charakter_controller.charakter:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_error_dialog("Kein Charakter verfügbar.")
            return
        
        # Verfügbare Settings direkt über den Charakter abrufen
        char = self.charakter_controller.charakter
        available_settings = char.custom_element_manager.get_all_settings()
        current_setting = char.active_setting_name
        
        if not available_settings or len(available_settings) <= 1:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_info_dialog(
                    f"Nur ein Setting verfügbar: '{current_setting}'",
                    "Kein Setting-Wechsel möglich"
                )
            return
        
        # Einfache Setting-Auswahl
        setting_choices = []
        for setting_name in available_settings:
            if setting_name != current_setting:
                setting_choices.append((setting_name, setting_name))
        
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            message = f"Aktuelles Setting: {current_setting}\n\nWähle ein neues Setting:"
            dialog_service.show_choice_dialog(
                message,
                "Setting wechseln", 
                setting_choices,
                self._on_setting_choice_made
            )
    
    def _on_setting_choice_made(self, chosen_setting):
        """Verarbeitet die Setting-Auswahl"""
        if not chosen_setting or not self.charakter_controller or not self.charakter_controller.charakter:
            return
        
        char = self.charakter_controller.charakter
        if chosen_setting == char.active_setting_name:
            return
        
        # Einfacher Setting-Wechsel mit Merge (Standard)
        success = char.change_active_setting(chosen_setting, merge_elements=True)
        
        dialog_service = service_container.get_dialog_service()
        if success and dialog_service:
            dialog_service.show_success_dialog(
                f"Setting erfolgreich zu '{chosen_setting}' gewechselt.",
                "Setting gewechselt"
            )
            self._trigger_ui_refresh()
        elif dialog_service:
            dialog_service.show_error_dialog(f"Fehler beim Wechseln zu Setting '{chosen_setting}'.")
    
    # ==================== CHARAKTERWERTE UPDATES ====================
    
    def update_vermoegen(self):
        """Aktualisiert das Vermögen"""
        if self.charakter_controller and self.charakter_controller.charakter and hasattr(self.ids, 'vermoegen_field'):
            try:
                new_value = int(self.ids.vermoegen_field.text)
                self.charakter_controller.charakter.vermoegen = new_value
                Logger.info(f"Vermögen auf {new_value} aktualisiert")
            except ValueError:
                Logger.error("Ungültiger Wert für Vermögen eingegeben")
    
    def update_waehrung(self):
        """Aktualisiert die Währung"""
        if self.charakter_controller and self.charakter_controller.charakter and hasattr(self.ids, 'waehrung_field'):
            new_value = self.ids.waehrung_field.text
            self.charakter_controller.charakter.waehrungseinheit = new_value
            Logger.info(f"Währung auf '{new_value}' aktualisiert")
    
    def update_maximale_attributsteigerungen(self):
        """Aktualisiert die maximalen Attributsteigerungen"""
        if self.charakter_controller and self.charakter_controller.charakter and hasattr(self.ids, 'attributsteigerungen_field'):
            try:
                new_value = int(self.ids.attributsteigerungen_field.text)
                self.charakter_controller.charakter.maximale_attributsteigerungen = new_value
                self.charakter_controller.charakter.verbleibende_attributsteigerungen = new_value
                Logger.info(f"Maximale Attributsteigerungen auf {new_value} aktualisiert")
            except ValueError:
                Logger.error("Ungültiger Wert für Attributsteigerungen eingegeben")
    
    def update_maximale_fertigkeitssteigerungen(self):
        """Aktualisiert die maximalen Fertigkeitssteigerungen"""
        if self.charakter_controller and self.charakter_controller.charakter and hasattr(self.ids, 'fertigkeitssteigerungen_field'):
            try:
                new_value = int(self.ids.fertigkeitssteigerungen_field.text)
                self.charakter_controller.charakter.maximale_fertigkeitssteigerungen = new_value
                self.charakter_controller.charakter.verbleibende_fertigkeitssteigerungen = new_value
                Logger.info(f"Maximale Fertigkeitssteigerungen auf {new_value} aktualisiert")
            except ValueError:
                Logger.error("Ungültiger Wert für Fertigkeitssteigerungen eingegeben")
    
    # ==================== CHARAKTER OPERATIONEN ====================
    
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
            return success
    
    # ==================== PDF & STATISTIKEN ====================
    
    def erzeuge_charakterbogen_pdf(self):
        """Delegiert an PDFManager"""
        self.pdf_manager.create_character_pdf()
    
    def zeige_statblock(self):
        """Delegiert an StatisticsManager"""
        self.statistics_manager.show_statblock()
    
    def zeige_element_statistiken(self):
        """Delegiert an StatisticsManager"""
        self.statistics_manager.show_element_statistics()
    
    # ==================== ELEMENT DIALOGE ====================
    
    # Setting-Dialoge
    def open_add_setting_popup(self):
        self.element_dialog_manager.open_add_setting_popup()
    
    def open_delete_setting_popup(self):
        self.element_dialog_manager.open_delete_setting_popup()
    
    # Volk-Dialoge
    def open_add_volk_dialog(self):
        self.element_dialog_manager.open_add_volk_dialog()
    
    def open_delete_volk_dialog(self):
        self.element_dialog_manager.open_delete_volk_dialog()
    
    # Talent-Dialoge
    def open_add_talent_popup(self):
        self.element_dialog_manager.open_add_talent_popup()
    
    def open_delete_talent_popup(self):
        self.element_dialog_manager.open_delete_talent_popup()
    
    # Macht-Dialoge
    def open_add_macht_popup(self):
        self.element_dialog_manager.open_add_macht_popup()
    
    def open_delete_macht_popup(self):
        self.element_dialog_manager.open_delete_macht_popup()
    
    # Fertigkeit-Dialoge
    def open_add_fertigkeit_popup(self):
        self.element_dialog_manager.open_add_fertigkeit_popup()
    
    def open_delete_fertigkeit_popup(self):
        self.element_dialog_manager.open_delete_fertigkeit_popup()
    
    # Handicap-Dialoge
    def open_add_handicap_popup(self):
        self.element_dialog_manager.open_add_handicap_popup()
    
    def open_delete_handicap_popup(self):
        self.element_dialog_manager.open_delete_handicap_popup()
    
    # Ausrüstung-Dialoge
    def open_add_ausruestung_popup(self):
        self.element_dialog_manager.open_add_ausruestung_popup()
    
    def open_delete_ausruestung_popup(self):
        self.element_dialog_manager.open_delete_ausruestung_popup()
    
    # Waffen-Dialoge
    def open_add_waffe_popup(self):
        self.element_dialog_manager.open_add_waffe_popup()
    
    def open_delete_waffe_popup(self):
        self.element_dialog_manager.open_delete_waffe_popup()
    
    # Rüstung-Dialoge
    def open_add_ruestung_popup(self):
        self.element_dialog_manager.open_add_ruestung_popup()
    
    def open_delete_ruestung_popup(self):
        self.element_dialog_manager.open_delete_ruestung_popup()
    
    # Schild-Dialoge
    def open_add_schild_popup(self):
        self.element_dialog_manager.open_add_schild_popup()
    
    def open_delete_schild_popup(self):
        self.element_dialog_manager.open_delete_schild_popup()
    
    # ==================== UI UPDATES ====================
    
    def _update_ui_fields(self):
        """Aktualisiert die UI-Felder mit aktuellen Werten"""
        if not self.charakter_controller or not hasattr(self.charakter_controller, 'charakter'):
            return
        
        try:
            charakter = self.charakter_controller.charakter
            if not charakter:
                return
            
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
    
    def _trigger_ui_refresh(self):
        """Löst eine Aktualisierung aller UI-Komponenten aus"""
        try:
            # Aktualisiere alle Widget-Tabs über die App
            if hasattr(self.app, 'refresh_current_tab'):
                Clock.schedule_once(lambda dt: self.app.refresh_current_tab(), 0.1)
            
            # Aktualisiere eigene UI-Felder
            Clock.schedule_once(lambda dt: self._update_ui_fields(), 0.1)
            Clock.schedule_once(lambda dt: self.statistics_manager.update_element_statistics_ui(), 0.1)
            
        except Exception as e:
            Logger.error(f"Fehler bei UI-Refresh: {str(e)}")
    
    def aktualisiere_ui(self):
        """Öffentliche Methode zur UI-Aktualisierung"""
        self._update_ui_fields()
        self.statistics_manager.update_element_statistics_ui()
    
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


# KV-String direkt eingebettet für bessere Kontrolle
kv_string = '''
#:import MDDivider kivymd.uix.divider.MDDivider

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
                                    on_release: root.open_setting_switch_options()
                                    MDButtonIcon:
                                        icon: "swap-horizontal"
                                    MDButtonText:
                                        text: "Wechseln"

                                MDButton:
                                    style: "outlined"
                                    size_hint_x: 1
                                    on_release: root.open_delete_setting_popup()
                                    MDButtonIcon:
                                        icon: "delete"
                                    MDButtonText:
                                        text: "Löschen"

                    # Rechte Spalte - PDF, Statblock und Statistiken
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

                        MDButton:
                            style: "tonal"
                            size_hint_x: 1
                            on_release: root.zeige_element_statistiken()

                            MDButtonIcon:
                                icon: "chart-bar"

                            MDButtonText:
                                text: "Element-Statistiken"

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

                    # Kompakte Statistik-Anzeige
                    MDBoxLayout:
                        id: element_stats_box
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(4)

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

# KV-Layout laden
try:
    Builder.load_string(kv_string)
    Logger.info("Einstellungen-Layout aus String geladen")
except Exception as e:
    Logger.error(f"Fehler beim Laden des Layouts: {str(e)}")