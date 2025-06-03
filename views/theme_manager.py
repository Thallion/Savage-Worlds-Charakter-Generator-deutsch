# views/theme_manager.py
"""
Theme Manager für Einstellungen-Widget
Kapselt alle Theme-bezogenen Funktionalitäten
"""

from kivy.logger import Logger
from services.service_container import service_container
from services.event_service import EventTypes


class ThemeManager:
    """Manager für Theme-bezogene Funktionalitäten"""
    
    def __init__(self, widget):
        self.widget = widget
        self.theme_service = service_container.get_theme_service()
        self.event_service = service_container.get_event_service()
    
    def initialize_theme(self):
        """Initialisiert das Theme"""
        try:
            if self.theme_service:
                self.theme_service.initialize_theme()
                
                # Farb-Chips erstellen
                if hasattr(self.widget.ids, 'colors_box'):
                    self.theme_service.create_color_chips(
                        self.widget.ids.colors_box, 
                        self.on_color_selected
                    )
                    
        except Exception as e:
            Logger.error(f"Fehler bei Theme-Initialisierung: {str(e)}")
    
    def switch_theme_style(self, style):
        """Wechselt den Theme-Stil"""
        if self.theme_service:
            self.theme_service.switch_theme_style(style)
            
            # Event senden
            if self.event_service:
                self.event_service.publish(EventTypes.THEME_CHANGED, {'style': style})
    
    def on_color_selected(self, color_name):
        """Callback für Farbauswahl"""
        if self.theme_service and self.theme_service.switch_primary_palette(color_name):
            # Event senden
            if self.event_service:
                self.event_service.publish(EventTypes.THEME_CHANGED, {'color': color_name})
    
    def update_color_chips(self):
        """Aktualisiert die Farb-Chips"""
        if self.theme_service and hasattr(self.widget.ids, 'colors_box'):
            self.theme_service.create_color_chips(
                self.widget.ids.colors_box, 
                self.on_color_selected
            )