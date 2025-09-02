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

# Handler imports (excluding redundant theme_handler)
from controllers.character_handler import CharacterHandler
from controllers.template_handler import TemplateHandler
from controllers.game_elements_handler import GameElementsHandler

# Service imports
from services.service_container import service_container, get_event_service
from services.event_service import EventTypes

# Manager imports - these are the primary implementations
from manager.theme_manager import ThemeManager
from manager.statistics_manager import StatisticsManager
from manager.pdf_manager import PDFManager

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
        """Initialisiert alle Handler (excluding theme - handled by manager)"""
        try:
            self.character_handler = CharacterHandler(self)
            self.template_handler = TemplateHandler(self)
            self.game_elements_handler = GameElementsHandler(self)
            
            Logger.info("Alle Handler erfolgreich initialisiert")
        except Exception as e:
            Logger.error(f"Fehler bei Handler-Initialisierung: {e}")
    
    def _initialize_managers(self):
        """Initialisiert Manager - diese sind die primären Implementierungen"""
        try:
            self.theme_manager = ThemeManager(self)
            self.statistics_manager = StatisticsManager(self)
            self.pdf_manager = PDFManager(self)
            # DialogService wird direkt über service_container verwendet (keine redundante Zwischenschicht)
            Logger.info("Manager erfolgreich initialisiert")
        except Exception as e:
            Logger.error(f"Fehler bei Manager-Initialisierung: {e}")
            # Set defaults to prevent attribute errors
            self.theme_manager = None
            self.statistics_manager = None
            self.pdf_manager = None

    def _register_event_handlers(self):
        """Registriert Event-Handler"""
        try:
            event_service = service_container.get_event_service()
            
            if event_service:
                # Character-Events
                event_service.subscribe(EventTypes.CHARACTER_CREATED, self.character_handler.on_character_created)
                event_service.subscribe(EventTypes.CHARACTER_LOADED, self.character_handler.on_character_loaded)
                event_service.subscribe(EventTypes.THEME_CHANGED, self._on_theme_changed)
                
                Logger.debug("Event-Handler für Einstellungen registriert")
        except Exception as e:
            Logger.error(f"Fehler bei Event-Handler-Registrierung: {e}")

    def _post_init(self, dt):
        """Post-Initialisierung nach dem UI-Aufbau"""
        try:
            # Theme initialisieren (directly via manager)
            if self.theme_manager:
                self.theme_manager.initialize_theme()
            
            # UI-Felder aktualisieren  
            self.character_handler._update_ui_fields()
            
            # Statistiken aktualisieren
            if self.statistics_manager:
                self.statistics_manager.update_element_statistics_ui()
            
            Logger.info("Post-Initialisierung erfolgreich abgeschlossen")
        except Exception as e:
            Logger.error(f"Fehler bei Post-Initialisierung: {e}")

    # ==================== DELEGIERTE METHODEN ====================
    # Alle Methoden delegieren an die entsprechenden Manager/Handler
    
    # Theme-Management (direct delegation to ThemeManager)
    def switch_theme_style(self, style):
        """Delegiert Theme-Stil-Wechsel an ThemeManager"""
        if self.theme_manager:
            return self.theme_manager.switch_theme_style(style)
        else:
            Logger.warning("ThemeManager nicht verfügbar")
    
    def on_color_selected(self, color_name):
        """Delegiert Farbauswahl an ThemeManager"""
        if self.theme_manager:
            return self.theme_manager.on_color_selected(color_name)
        else:
            Logger.warning("ThemeManager nicht verfügbar")
            
    def _on_theme_changed(self, data):
        """Callback für Theme-Änderungen"""
        if self.theme_manager:
            self.theme_manager.update_color_chips()
        else:
            Logger.warning("ThemeManager nicht verfügbar für Theme-Update")
    
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
        """Öffnet Dialog zum Hinzufügen von Settings"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_setting_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Setting hinzufügen nicht möglich")
    
    def open_setting_switch_options(self):
        """Delegiert Setting-Wechsel-Dialog an GameElementsHandler"""
        return self.game_elements_handler.open_setting_switch_options()
    
    def open_delete_setting_popup(self):
        """Öffnet Dialog zum Löschen von Settings"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_setting_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Setting löschen nicht möglich")
    
    # Volk-Dialoge
    def open_add_volk_dialog(self):
        """Öffnet Dialog zum Hinzufügen von Völkern"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_volk_dialog()
        else:
            Logger.warning("DialogService nicht verfügbar - Volk hinzufügen nicht möglich")
    
    def open_delete_volk_dialog(self):
        """Öffnet Dialog zum Löschen von Völkern"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_volk_dialog()
        else:
            Logger.warning("DialogService nicht verfügbar - Volk löschen nicht möglich")
    
    # Talent-Dialoge
    def open_add_talent_popup(self):
        """Öffnet Dialog zum Hinzufügen von Talenten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_talent_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Talent hinzufügen nicht möglich")
    
    def open_delete_talent_popup(self):
        """Öffnet Dialog zum Löschen von Talenten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_talent_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Talent löschen nicht möglich")
    
    # Macht-Dialoge
    def open_add_macht_popup(self):
        """Öffnet Dialog zum Hinzufügen von Mächten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_macht_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Macht hinzufügen nicht möglich")
    
    def open_delete_macht_popup(self):
        """Öffnet Dialog zum Löschen von Mächten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_macht_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Macht löschen nicht möglich")
    
    # Fertigkeit-Dialoge
    def open_add_fertigkeit_popup(self):
        """Öffnet Dialog zum Hinzufügen von Fertigkeiten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_fertigkeit_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Fertigkeit hinzufügen nicht möglich")
    
    def open_delete_fertigkeit_popup(self):
        """Öffnet Dialog zum Löschen von Fertigkeiten"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_fertigkeit_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Fertigkeit löschen nicht möglich")
    
    # Handicap-Dialoge
    def open_add_handicap_popup(self):
        """Öffnet Dialog zum Hinzufügen von Handicaps"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_handicap_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Handicap hinzufügen nicht möglich")
    
    def open_delete_handicap_popup(self):
        """Öffnet Dialog zum Löschen von Handicaps"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_handicap_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Handicap löschen nicht möglich")
    
    # Ausrüstung-Dialoge
    def open_add_ausruestung_popup(self):
        """Öffnet Dialog zum Hinzufügen von Ausrüstung"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_ausruestung_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Ausrüstung hinzufügen nicht möglich")
    
    def open_delete_ausruestung_popup(self):
        """Öffnet Dialog zum Löschen von Ausrüstung"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_ausruestung_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Ausrüstung löschen nicht möglich")
    
    # Waffen-Dialoge
    def open_add_waffe_popup(self):
        """Öffnet Dialog zum Hinzufügen von Waffen"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_waffe_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Waffe hinzufügen nicht möglich")
    
    def open_delete_waffe_popup(self):
        """Öffnet Dialog zum Löschen von Waffen"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_waffe_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Waffe löschen nicht möglich")
    
    # Rüstung-Dialoge
    def open_add_ruestung_popup(self):
        """Öffnet Dialog zum Hinzufügen von Rüstungen"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_ruestung_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Rüstung hinzufügen nicht möglich")
    
    def open_delete_ruestung_popup(self):
        """Öffnet Dialog zum Löschen von Rüstungen"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_ruestung_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Rüstung löschen nicht möglich")
    
    # Schild-Dialoge
    def open_add_schild_popup(self):
        """Öffnet Dialog zum Hinzufügen von Schilden"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_add_schild_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Schild hinzufügen nicht möglich")
    
    def open_delete_schild_popup(self):
        """Öffnet Dialog zum Löschen von Schilden"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.open_delete_schild_popup()
        else:
            Logger.warning("DialogService nicht verfügbar - Schild löschen nicht möglich")

    # ==================== CLEANUP ====================
    
    def on_stop(self):
        """Cleanup beim Beenden"""
        try:
            # Event-Handler entfernen
            event_service = service_container.get_event_service()
            
            if event_service:
                event_service.unsubscribe(EventTypes.CHARACTER_CREATED, self.character_handler.on_character_created)
                event_service.unsubscribe(EventTypes.CHARACTER_LOADED, self.character_handler.on_character_loaded)
                event_service.unsubscribe(EventTypes.THEME_CHANGED, self._on_theme_changed)
            
            Logger.info("EinstellungenWidget bereinigt")
        except Exception as e:
            Logger.error(f"Fehler beim Bereinigen: {e}")