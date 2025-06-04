# views/einstellungen_widget.py
"""
Refactored Einstellungen Widget - Nur UI-Logik und Delegation
Verwendet Manager-Klassen für verschiedene Funktionalitätsbereiche
KORRIGIERT: Setting-Merge-Dialog wird jetzt richtig verwendet
"""

import os
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen

# Manager Imports (falls vorhanden)
try:
    from .theme_manager import ThemeManager
    from .pdf_manager import PDFManager
    from .element_dialog_manager import ElementDialogManager
    from .statistics_manager import StatisticsManager
    MANAGERS_AVAILABLE = True
except ImportError:
    Logger.warning("Manager-Klassen nicht verfügbar, verwende vereinfachte Implementation")
    MANAGERS_AVAILABLE = False

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
        if MANAGERS_AVAILABLE:
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
            # Theme initialisieren (falls Manager verfügbar)
            if MANAGERS_AVAILABLE and hasattr(self, 'theme_manager'):
                self.theme_manager.initialize_theme()
            
            # UI-Felder mit aktuellen Werten aktualisieren
            self._update_ui_fields()
            
            # Element-Statistiken anzeigen (falls Manager verfügbar)
            if MANAGERS_AVAILABLE and hasattr(self, 'statistics_manager'):
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
        if MANAGERS_AVAILABLE and hasattr(self, 'statistics_manager'):
            self.statistics_manager.update_element_statistics_ui()
    
    def _on_character_loaded(self, data):
        """Wird aufgerufen, wenn ein Charakter geladen wurde"""
        Logger.info(f"Charakter geladen: {data}")
        self._update_ui_fields()
        if MANAGERS_AVAILABLE and hasattr(self, 'statistics_manager'):
            self.statistics_manager.update_element_statistics_ui()
    
    def _on_theme_changed(self, data):
        """Wird aufgerufen, wenn das Theme geändert wurde"""
        Logger.info(f"Theme geändert: {data}")
        if MANAGERS_AVAILABLE and hasattr(self, 'theme_manager'):
            self.theme_manager.update_color_chips()
    
    # ==================== THEME MANAGEMENT ====================
    
    def switch_theme_style(self, style):
        """Delegiert an ThemeManager oder direkt an App"""
        try:
            Logger.info(f"Theme-Stil-Wechsel angefordert: {style}")
            if MANAGERS_AVAILABLE and hasattr(self, 'theme_manager'):
                self.theme_manager.switch_theme_style(style)
            else:
                # Direkte App-Integration
                if self.app and hasattr(self.app, 'update_theme'):
                    self.app.update_theme(theme_style=style)
                    Logger.info(f"Theme-Stil gewechselt zu: {style}")
                else:
                    Logger.error("App oder update_theme Methode nicht verfügbar")
        except Exception as e:
            Logger.error(f"Fehler beim Theme-Wechsel: {str(e)}")
    
    def on_color_selected(self, color_name):
        """Delegiert an ThemeManager oder direkt an App"""
        try:
            Logger.info(f"Farb-Wechsel angefordert: {color_name}")
            if MANAGERS_AVAILABLE and hasattr(self, 'theme_manager'):
                self.theme_manager.on_color_selected(color_name)
            else:
                # Direkte App-Integration
                if self.app and hasattr(self.app, 'update_theme'):
                    self.app.update_theme(primary_palette=color_name)
                    Logger.info(f"Primärfarbe gewechselt zu: {color_name}")
                else:
                    Logger.error("App oder update_theme Methode nicht verfügbar")
        except Exception as e:
            Logger.error(f"Fehler beim Farb-Wechsel: {str(e)}")
    
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
        """KORRIGIERT: Setting-Wechsel mit Merge-Dialog"""
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
        
        # Setting-Auswahl
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
        """KORRIGIERT: Verarbeitet die Setting-Auswahl mit Merge-Dialog"""
        if not chosen_setting or not self.charakter_controller or not self.charakter_controller.charakter:
            return
        
        char = self.charakter_controller.charakter
        if chosen_setting == char.active_setting_name:
            return
        
        # HIER IST DIE KORREKTUR: Jetzt wird der Setting-Merge-Dialog verwendet
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            # Verwende die show_setting_merge_dialog Methode
            dialog_service.show_setting_merge_dialog(
                chosen_setting,
                lambda merge_choice: self._apply_setting_change(chosen_setting, merge_choice)
            )
    
    def _apply_setting_change(self, setting_name, merge_choice):
        """
        Wendet den Setting-Wechsel mit der gewählten Merge-Option an
        
        Args:
            setting_name (str): Name des neuen Settings
            merge_choice (str): 'merge' oder 'replace'
        """
        if not self.charakter_controller or not self.charakter_controller.charakter:
            return
        
        char = self.charakter_controller.charakter
        merge_elements = (merge_choice == "merge")
        
        Logger.info(f"Setting-Wechsel zu '{setting_name}' mit Merge-Option: {merge_elements}")
        
        # Setting wechseln mit der gewählten Option
        success = char.change_active_setting(setting_name, merge_elements=merge_elements)
        
        dialog_service = service_container.get_dialog_service()
        if success and dialog_service:
            merge_text = "zusammengeführt" if merge_elements else "komplett ersetzt"
            dialog_service.show_success_dialog(
                f"Setting erfolgreich zu '{setting_name}' gewechselt.\nElemente wurden {merge_text}.",
                "Setting gewechselt"
            )
            self._trigger_ui_refresh()
        elif dialog_service:
            dialog_service.show_error_dialog(f"Fehler beim Wechseln zu Setting '{setting_name}'.")
    
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
        if MANAGERS_AVAILABLE and hasattr(self, 'pdf_manager'):
            self.pdf_manager.create_character_pdf()
        else:
            Logger.info("PDF-Erstellung - Manager nicht verfügbar")
    
    def zeige_statblock(self):
        """Delegiert an StatisticsManager"""
        if MANAGERS_AVAILABLE and hasattr(self, 'statistics_manager'):
            self.statistics_manager.show_statblock()
        else:
            Logger.info("Statblock anzeigen - Manager nicht verfügbar")
    
    def zeige_element_statistiken(self):
        """Delegiert an StatisticsManager"""
        if MANAGERS_AVAILABLE and hasattr(self, 'statistics_manager'):
            self.statistics_manager.show_element_statistics()
        else:
            Logger.info("Element-Statistiken anzeigen - Manager nicht verfügbar")
    
    # ==================== ELEMENT DIALOGE ====================
    
    # Setting-Dialoge
    def open_add_setting_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_add_setting_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_add_setting_popup()
            else:
                Logger.info("Setting hinzufügen - Manager und Service nicht verfügbar")
    
    def open_delete_setting_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_delete_setting_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_delete_setting_popup()
            else:
                Logger.info("Setting löschen - Manager und Service nicht verfügbar")
    
    # Volk-Dialoge
    def open_add_volk_dialog(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_add_volk_dialog()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_add_volk_dialog()
            else:
                Logger.info("Volk hinzufügen - Manager und Service nicht verfügbar")
    
    def open_delete_volk_dialog(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_delete_volk_dialog()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_delete_volk_dialog()
            else:
                Logger.info("Volk löschen - Manager und Service nicht verfügbar")
    
    # Talent-Dialoge
    def open_add_talent_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_add_talent_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_add_talent_popup()
            else:
                Logger.info("Talent hinzufügen - Manager und Service nicht verfügbar")
    
    def open_delete_talent_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_delete_talent_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_delete_talent_popup()
            else:
                Logger.info("Talent löschen - Manager und Service nicht verfügbar")
    
    # Macht-Dialoge
    def open_add_macht_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_add_macht_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_add_macht_popup()
            else:
                Logger.info("Macht hinzufügen - Manager und Service nicht verfügbar")
    
    def open_delete_macht_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_delete_macht_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_delete_macht_popup()
            else:
                Logger.info("Macht löschen - Manager und Service nicht verfügbar")
    
    # Fertigkeit-Dialoge
    def open_add_fertigkeit_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_add_fertigkeit_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_add_fertigkeit_popup()
            else:
                Logger.info("Fertigkeit hinzufügen - Manager und Service nicht verfügbar")
    
    def open_delete_fertigkeit_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_delete_fertigkeit_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_delete_fertigkeit_popup()
            else:
                Logger.info("Fertigkeit löschen - Manager und Service nicht verfügbar")
    
    # Handicap-Dialoge
    def open_add_handicap_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_add_handicap_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_add_handicap_popup()
            else:
                Logger.info("Handicap hinzufügen - Manager und Service nicht verfügbar")
    
    def open_delete_handicap_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_delete_handicap_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_delete_handicap_popup()
            else:
                Logger.info("Handicap löschen - Manager und Service nicht verfügbar")
    
    # Ausrüstung-Dialoge
    def open_add_ausruestung_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_add_ausruestung_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_add_ausruestung_popup()
            else:
                Logger.info("Ausrüstung hinzufügen - Manager und Service nicht verfügbar")
    
    def open_delete_ausruestung_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_delete_ausruestung_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_delete_ausruestung_popup()
            else:
                Logger.info("Ausrüstung löschen - Manager und Service nicht verfügbar")
    
    # Waffen-Dialoge
    def open_add_waffe_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_add_waffe_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_add_waffe_popup()
            else:
                Logger.info("Waffe hinzufügen - Manager und Service nicht verfügbar")
    
    def open_delete_waffe_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_delete_waffe_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_delete_waffe_popup()
            else:
                Logger.info("Waffe löschen - Manager und Service nicht verfügbar")
    
    # Rüstung-Dialoge
    def open_add_ruestung_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_add_ruestung_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_add_ruestung_popup()
            else:
                Logger.info("Rüstung hinzufügen - Manager und Service nicht verfügbar")
    
    def open_delete_ruestung_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_delete_ruestung_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_delete_ruestung_popup()
            else:
                Logger.info("Rüstung löschen - Manager und Service nicht verfügbar")
    
    # Schild-Dialoge
    def open_add_schild_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_add_schild_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_add_schild_popup()
            else:
                Logger.info("Schild hinzufügen - Manager und Service nicht verfügbar")
    
    def open_delete_schild_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_delete_schild_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_delete_schild_popup()
            else:
                Logger.info("Schild löschen - Manager und Service nicht verfügbar")
    
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
            
            # Element-Statistiken aktualisieren (falls Manager verfügbar)
            if MANAGERS_AVAILABLE and hasattr(self, 'statistics_manager'):
                Clock.schedule_once(lambda dt: self.statistics_manager.update_element_statistics_ui(), 0.1)
            
        except Exception as e:
            Logger.error(f"Fehler bei UI-Refresh: {str(e)}")
    
    def aktualisiere_ui(self):
        """Öffentliche Methode zur UI-Aktualisierung"""
        self._update_ui_fields()
        if MANAGERS_AVAILABLE and hasattr(self, 'statistics_manager'):
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

                                MDSegmentButtonLabel:
                                    text: "Hell"

                            MDSegmentedButtonItem:
                                size_hint: None, None
                                size: dp(100), dp(40)
                                on_release: root.switch_theme_style('Dark')

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
                            cols: 4
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(8)
                            padding: 0
                            pos_hint: {"center_y": .5}
                            
                            # Farb-Chips - nur gültige KivyMD-Paletten
                            MDChip:
                                size_hint_y: None
                                height: dp(32)
                                on_release: root.on_color_selected("Orange")
                                MDChipText:
                                    text: "Orange"
                            
                            MDChip:
                                size_hint_y: None
                                height: dp(32)
                                on_release: root.on_color_selected("Blue")
                                MDChipText:
                                    text: "Blau"
                            
                            MDChip:
                                size_hint_y: None
                                height: dp(32)
                                on_release: root.on_color_selected("Red")
                                MDChipText:
                                    text: "Rot"
                            
                            MDChip:
                                size_hint_y: None
                                height: dp(32)
                                on_release: root.on_color_selected("Green")
                                MDChipText:
                                    text: "Grün"
                            
                            MDChip:
                                size_hint_y: None
                                height: dp(32)
                                on_release: root.on_color_selected("Purple")
                                MDChipText:
                                    text: "Lila"
                            
                            MDChip:
                                size_hint_y: None
                                height: dp(32)
                                on_release: root.on_color_selected("Teal")
                                MDChipText:
                                    text: "Türkis"
                            
                            MDChip:
                                size_hint_y: None
                                height: dp(32)
                                on_release: root.on_color_selected("Amber")
                                MDChipText:
                                    text: "Bernstein"
                            
                            MDChip:
                                size_hint_y: None
                                height: dp(32)
                                on_release: root.on_color_selected("Brown")
                                MDChipText:
                                    text: "Braun"
                            
                            MDChip:
                                size_hint_y: None
                                height: dp(32)
                                on_release: root.on_color_selected("Gray")
                                MDChipText:
                                    text: "Grau"

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

                    # Völker-Verwaltung
                    MDBoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(8)

                        MDLabel:
                            text: "Völker"
                            bold: True
                            size_hint_y: None
                            height: dp(30)

                        MDGridLayout:
                            cols: 2
                            spacing: dp(8)
                            size_hint_y: None
                            height: dp(48)

                            MDButton:
                                style: "elevated"
                                size_hint_x: 1
                                on_release: root.open_add_volk_dialog()
                                
                                MDButtonIcon:
                                    icon: "plus"
                                
                                MDButtonText:
                                    text: "Hinzufügen"

                            MDButton:
                                style: "outlined"
                                size_hint_x: 1
                                on_release: root.open_delete_volk_dialog()
                                
                                MDButtonIcon:
                                    icon: "delete"
                                
                                MDButtonText:
                                    text: "Löschen"

                    # Talente-Verwaltung
                    MDBoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(8)

                        MDLabel:
                            text: "Talente"
                            bold: True
                            size_hint_y: None
                            height: dp(30)

                        MDGridLayout:
                            cols: 2
                            spacing: dp(8)
                            size_hint_y: None
                            height: dp(48)

                            MDButton:
                                style: "elevated"
                                size_hint_x: 1
                                on_release: root.open_add_talent_popup()
                                
                                MDButtonIcon:
                                    icon: "plus"
                                
                                MDButtonText:
                                    text: "Hinzufügen"

                            MDButton:
                                style: "outlined"
                                size_hint_x: 1
                                on_release: root.open_delete_talent_popup()
                                
                                MDButtonIcon:
                                    icon: "delete"
                                
                                MDButtonText:
                                    text: "Löschen"

                    # Mächte-Verwaltung
                    MDBoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(8)

                        MDLabel:
                            text: "Mächte"
                            bold: True
                            size_hint_y: None
                            height: dp(30)

                        MDGridLayout:
                            cols: 2
                            spacing: dp(8)
                            size_hint_y: None
                            height: dp(48)

                            MDButton:
                                style: "elevated"
                                size_hint_x: 1
                                on_release: root.open_add_macht_popup()
                                
                                MDButtonIcon:
                                    icon: "plus"
                                
                                MDButtonText:
                                    text: "Hinzufügen"

                            MDButton:
                                style: "outlined"
                                size_hint_x: 1
                                on_release: root.open_delete_macht_popup()
                                
                                MDButtonIcon:
                                    icon: "delete"
                                
                                MDButtonText:
                                    text: "Löschen"

                    # Fertigkeiten-Verwaltung
                    MDBoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(8)

                        MDLabel:
                            text: "Fertigkeiten"
                            bold: True
                            size_hint_y: None
                            height: dp(30)

                        MDGridLayout:
                            cols: 2
                            spacing: dp(8)
                            size_hint_y: None
                            height: dp(48)

                            MDButton:
                                style: "elevated"
                                size_hint_x: 1
                                on_release: root.open_add_fertigkeit_popup()
                                
                                MDButtonIcon:
                                    icon: "plus"
                                
                                MDButtonText:
                                    text: "Hinzufügen"

                            MDButton:
                                style: "outlined"
                                size_hint_x: 1
                                on_release: root.open_delete_fertigkeit_popup()
                                
                                MDButtonIcon:
                                    icon: "delete"
                                
                                MDButtonText:
                                    text: "Löschen"

                    # Handicaps-Verwaltung
                    MDBoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(8)

                        MDLabel:
                            text: "Handicaps"
                            bold: True
                            size_hint_y: None
                            height: dp(30)

                        MDGridLayout:
                            cols: 2
                            spacing: dp(8)
                            size_hint_y: None
                            height: dp(48)

                            MDButton:
                                style: "elevated"
                                size_hint_x: 1
                                on_release: root.open_add_handicap_popup()
                                
                                MDButtonIcon:
                                    icon: "plus"
                                
                                MDButtonText:
                                    text: "Hinzufügen"

                            MDButton:
                                style: "outlined"
                                size_hint_x: 1
                                on_release: root.open_delete_handicap_popup()
                                
                                MDButtonIcon:
                                    icon: "delete"
                                
                                MDButtonText:
                                    text: "Löschen"

                    # Ausrüstung-Verwaltung
                    MDBoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(8)

                        MDLabel:
                            text: "Ausrüstung"
                            bold: True
                            size_hint_y: None
                            height: dp(30)

                        MDGridLayout:
                            cols: 4
                            spacing: dp(8)
                            size_hint_y: None
                            height: dp(48)

                            MDButton:
                                style: "elevated"
                                size_hint_x: 1
                                on_release: root.open_add_ausruestung_popup()
                                
                                MDButtonIcon:
                                    icon: "package-variant"
                                
                                MDButtonText:
                                    text: "Allgemein"

                            MDButton:
                                style: "elevated"
                                size_hint_x: 1
                                on_release: root.open_add_waffe_popup()
                                
                                MDButtonIcon:
                                    icon: "sword"
                                
                                MDButtonText:
                                    text: "Waffen"

                            MDButton:
                                style: "elevated"
                                size_hint_x: 1
                                on_release: root.open_add_ruestung_popup()
                                
                                MDButtonIcon:
                                    icon: "shield"
                                
                                MDButtonText:
                                    text: "Rüstungen"

                            MDButton:
                                style: "elevated"
                                size_hint_x: 1
                                on_release: root.open_add_schild_popup()
                                
                                MDButtonIcon:
                                    icon: "shield-outline"
                                
                                MDButtonText:
                                    text: "Schilde"

                        # Lösch-Buttons für Ausrüstung
                        MDGridLayout:
                            cols: 4
                            spacing: dp(8)
                            size_hint_y: None
                            height: dp(48)

                            MDButton:
                                style: "outlined"
                                size_hint_x: 1
                                on_release: root.open_delete_ausruestung_popup()
                                
                                MDButtonIcon:
                                    icon: "delete"
                                
                                MDButtonText:
                                    text: "Löschen"

                            MDButton:
                                style: "outlined"
                                size_hint_x: 1
                                on_release: root.open_delete_waffe_popup()
                                
                                MDButtonIcon:
                                    icon: "delete"
                                
                                MDButtonText:
                                    text: "Löschen"

                            MDButton:
                                style: "outlined"
                                size_hint_x: 1
                                on_release: root.open_delete_ruestung_popup()
                                
                                MDButtonIcon:
                                    icon: "delete"
                                
                                MDButtonText:
                                    text: "Löschen"

                            MDButton:
                                style: "outlined"
                                size_hint_x: 1
                                on_release: root.open_delete_schild_popup()
                                
                                MDButtonIcon:
                                    icon: "delete"
                                
                                MDButtonText:
                                    text: "Löschen"
'''

# KV-Layout laden
try:
    Builder.load_string(kv_string)
    Logger.info("Einstellungen-Layout aus String geladen")
except Exception as e:
    Logger.error(f"Fehler beim Laden des Layouts: {str(e)}")