# views/charakter_verwaltung_widget.py
"""
NEUES: CharakterVerwaltungWidget - Ausgegliedert aus EinstellungenWidget
Verantwortlich für alle Charakterverwaltungs-Funktionen
"""

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import Clock

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
        """Erstellt einen neuen Charakter"""
        return self.character_handler.create_new_character()
    
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