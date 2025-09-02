# views/einstellungen_widget.py
"""
REFACTORED: Einstellungen Widget - Hauptklasse
Stark vereinfacht durch Auslagerung in Handler-Klassen
"""

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import Clock

# Handler imports
from .handlers import (
    ThemeHandler, 
    CharacterHandler, 
    TemplateHandler, 
    GameElementsHandler
)

# Service imports
from services.service_container import service_container, get_event_service
from services.event_service import EventTypes

# Manager availability check
try:
    from manager.theme_manager import ThemeManager
    from manager.statistics_manager import StatisticsManager
    from manager.pdf_manager import PDFManager
    from manager.element_dialog_manager import ElementDialogManager
    MANAGERS_AVAILABLE = True
except ImportError:
    MANAGERS_AVAILABLE = False
    Logger.warning("Manager nicht verfügbar")

# KV-Datei laden
Builder.load_file('/home/jean/Dokumente/GitHub/Savage-Worlds-Charakter-Generator-deutsch/views/einstellungen_widget.kv')


class EinstellungenWidget(MDBoxLayout):
    """
    REFACTORED: Hauptklasse für Einstellungen
    Deutlich vereinfacht - Funktionalität in Handler-Klassen ausgelagert
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        
        # Handler initialisieren
        self._initialize_handlers()
        
        # Manager initialisieren (falls verfügbar)
        self._initialize_managers()
        
        # Event-Handler registrieren
        self._register_event_handlers()
        
        # Post-Initialisierung planen
        Clock.schedule_once(self._post_init, 0)
    
    def _initialize_handlers(self):
        """Initialisiert alle Handler"""
        try:
            self.theme_handler = ThemeHandler(self)
            self.character_handler = CharacterHandler(self)
            self.template_handler = TemplateHandler(self)
            self.game_elements_handler = GameElementsHandler(self)
            
            Logger.info("Alle Handler erfolgreich initialisiert")
        except Exception as e:
            Logger.error(f"Fehler bei Handler-Initialisierung: {e}")
    
    def _initialize_managers(self):
        """Initialisiert Manager (falls verfügbar)"""
        try:
            if MANAGERS_AVAILABLE:
                self.theme_manager = ThemeManager(self)
                self.statistics_manager = StatisticsManager(self)
                self.pdf_manager = PDFManager(self)
                self.element_dialog_manager = ElementDialogManager(self)
                Logger.info("Manager erfolgreich initialisiert")
            else:
                self.theme_manager = None
                self.statistics_manager = None
                self.pdf_manager = None
                self.element_dialog_manager = None
                Logger.info("Manager nicht verfügbar - Handler-Only Modus")
        except Exception as e:
            Logger.error(f"Fehler bei Manager-Initialisierung: {e}")
            self.theme_manager = None
            self.statistics_manager = None
            self.pdf_manager = None
            self.element_dialog_manager = None

    def _register_event_handlers(self):
        """Registriert Event-Handler"""
        try:
            event_service = service_container.get_event_service()
            
            if event_service:
                # Character-Events
                event_service.subscribe(EventTypes.CHARACTER_CREATED, self.character_handler.on_character_created)
                event_service.subscribe(EventTypes.CHARACTER_LOADED, self.character_handler.on_character_loaded)
                event_service.subscribe(EventTypes.THEME_CHANGED, self.theme_handler.on_theme_changed)
                
                Logger.debug("Event-Handler für Einstellungen registriert")
        except Exception as e:
            Logger.error(f"Fehler bei Event-Handler-Registrierung: {e}")

    def _post_init(self, dt):
        """Post-Initialisierung nach dem UI-Aufbau"""
        try:
            # Theme initialisieren
            self.theme_handler.initialize_theme()
            
            # UI-Felder aktualisieren  
            self.character_handler._update_ui_fields()
            
            # Statistiken aktualisieren (falls Manager verfügbar)
            if MANAGERS_AVAILABLE and hasattr(self, 'statistics_manager') and self.statistics_manager:
                self.statistics_manager.update_element_statistics_ui()
            
            Logger.info("Post-Initialisierung erfolgreich abgeschlossen")
        except Exception as e:
            Logger.error(f"Fehler bei Post-Initialisierung: {e}")

    # ==================== DELEGIERTE METHODEN ====================
    # Alle Methoden delegieren an die entsprechenden Handler
    
    # Theme-Management (delegiert an ThemeHandler)
    def switch_theme_style(self, style):
        """Delegiert Theme-Stil-Wechsel an ThemeHandler"""
        return self.theme_handler.switch_theme_style(style)
    
    def on_color_selected(self, color_name):
        """Delegiert Farbauswahl an ThemeHandler"""
        return self.theme_handler.on_color_selected(color_name)
    
    # Character-Management (delegiert an CharacterHandler)
    def get_charakter_value(self, attribute, default_value=''):
        """Delegiert Charakter-Wert-Abruf an CharacterHandler"""
        return self.character_handler.get_charakter_value(attribute, default_value)
    
    def update_maximale_attributsteigerungen(self):
        """Delegiert Attributsteigerungen-Update an CharacterHandler"""
        return self.character_handler.update_maximale_attributsteigerungen()
    
    def update_maximale_fertigkeitssteigerungen(self):
        """Delegiert Fertigkeitssteigerungen-Update an CharacterHandler"""
        return self.character_handler.update_maximale_fertigkeitssteigerungen()
    
    def update_vermoegen(self):
        """Delegiert Vermögen-Update an CharacterHandler"""
        return self.character_handler.update_vermoegen()
    
    def update_waehrung(self):
        """Delegiert Währung-Update an CharacterHandler"""
        return self.character_handler.update_waehrung()
    
    def erhoehe_startkapital(self):
        """Delegiert Startkapital-Erhöhung an CharacterHandler"""
        return self.character_handler.erhoehe_startkapital()
    
    def erhoehe_aufstieg(self):
        """Delegiert Aufstieg-Erhöhung an CharacterHandler"""
        return self.character_handler.erhoehe_aufstieg()
    
    def senke_aufstieg(self):
        """Delegiert Aufstieg-Senkung an CharacterHandler"""
        return self.character_handler.senke_aufstieg()
    
    def create_new_character(self):
        """Delegiert Charakter-Erstellung an CharacterHandler"""
        return self.character_handler.create_new_character()
    
    def schnellspeichern_charakter(self):
        """Delegiert Schnellspeicherung an CharacterHandler"""
        return self.character_handler.schnellspeichern_charakter()
    
    def speichere_charakter(self):
        """Delegiert Charakterspeicherung an CharacterHandler"""
        return self.character_handler.speichere_charakter()
    
    def lade_charakter(self):
        """Delegiert Charakterladen an CharacterHandler"""
        return self.character_handler.lade_charakter()
    
    def erzeuge_charakterbogen_pdf(self):
        """Delegiert PDF-Erzeugung an CharacterHandler"""
        return self.character_handler.erzeuge_charakterbogen_pdf()
    
    def zeige_statblock(self):
        """Delegiert Statblock-Anzeige an CharacterHandler"""
        return self.character_handler.zeige_statblock()
    
    def zeige_element_statistiken(self):
        """Delegiert Element-Statistiken an CharacterHandler"""
        return self.character_handler.zeige_element_statistiken()
    
    # Template-Management (delegiert an TemplateHandler)
    def open_template_selection_dialog(self):
        """Delegiert Template-Dialog an TemplateHandler"""
        return self.template_handler.open_template_selection_dialog()
        
    def show_template_selection_dialog(self):
        """Delegiert Template-Dialog an TemplateHandler"""
        return self.template_handler.show_template_selection_dialog()
    
    def generate_character_from_selected_template(self):
        """Delegiert Template-Generierung an TemplateHandler"""
        return self.template_handler.generate_character_from_selected_template()
    
    @property
    def selected_template(self):
        """Property für ausgewähltes Template (für KV-Zugriff)"""
        if hasattr(self, 'template_handler') and self.template_handler:
            return getattr(self.template_handler, 'selected_template', None)
        return None
    
    # Game Elements Management (delegiert an GameElementsHandler)
    def open_add_volk_dialog(self):
        """Delegiert Volk-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_volk_dialog()
    
    def open_delete_volk_dialog(self):
        """Delegiert Volk-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_volk_dialog()
    
    def open_add_talent_popup(self):
        """Delegiert Talent-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_talent_popup()
    
    def open_delete_talent_popup(self):
        """Delegiert Talent-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_talent_popup()
    
    def open_add_macht_popup(self):
        """Delegiert Macht-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_macht_popup()
    
    def open_delete_macht_popup(self):
        """Delegiert Macht-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_macht_popup()
    
    def open_add_fertigkeit_popup(self):
        """Delegiert Fertigkeit-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_fertigkeit_popup()
    
    def open_delete_fertigkeit_popup(self):
        """Delegiert Fertigkeit-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_fertigkeit_popup()
    
    def open_add_handicap_popup(self):
        """Delegiert Handicap-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_handicap_popup()
    
    def open_delete_handicap_popup(self):
        """Delegiert Handicap-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_handicap_popup()
    
    def open_add_ausruestung_popup(self):
        """Delegiert Ausrüstung-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_ausruestung_popup()
    
    def open_add_waffe_popup(self):
        """Delegiert Waffen-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_waffe_popup()
    
    def open_add_ruestung_popup(self):
        """Delegiert Rüstung-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_ruestung_popup()
    
    def open_add_schild_popup(self):
        """Delegiert Schild-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_add_schild_popup()
    
    def open_delete_ausruestung_popup(self):
        """Delegiert Ausrüstung-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_ausruestung_popup()
    
    def open_delete_waffe_popup(self):
        """Delegiert Waffen-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_waffe_popup()
    
    def open_delete_ruestung_popup(self):
        """Delegiert Rüstung-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_ruestung_popup()
    
    def open_delete_schild_popup(self):
        """Delegiert Schild-Lösch-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_delete_schild_popup()
    
    def open_add_setting_popup(self):
        if MANAGERS_AVAILABLE and hasattr(self, 'element_dialog_manager'):
            self.element_dialog_manager.open_add_setting_popup()
        else:
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.open_add_setting_popup()
            else:
                Logger.info("Setting hinzufügen - Manager und Service nicht verfügbar")
    
    def open_setting_switch_options(self):
        """Delegiert Setting-Wechsel-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_setting_switch_options()
    
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

    # ==================== CLEANUP ====================
    
    def on_stop(self):
        """Cleanup beim Beenden"""
        try:
            # Event-Handler entfernen
            event_service = service_container.get_event_service()
            
            if event_service:
                event_service.unsubscribe(EventTypes.CHARACTER_CREATED, self.character_handler.on_character_created)
                event_service.unsubscribe(EventTypes.CHARACTER_LOADED, self.character_handler.on_character_loaded)
                event_service.unsubscribe(EventTypes.THEME_CHANGED, self.theme_handler.on_theme_changed)
            
            Logger.info("EinstellungenWidget bereinigt")
        except Exception as e:
            Logger.error(f"Fehler beim Bereinigen: {e}")