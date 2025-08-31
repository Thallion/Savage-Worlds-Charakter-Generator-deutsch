# views/theme_manager.py
"""
Theme Manager für Einstellungen-Widget
Kapselt alle Theme-bezogenen Funktionalitäten
KORRIGIERT: Verwendet App's update_theme für Persistierung
"""

from kivy.logger import Logger
from kivy.app import App
from services.service_container import service_container
from services.event_service import EventTypes


class ThemeManager:
    """Manager für Theme-bezogene Funktionalitäten"""
    
    def __init__(self, widget):
        self.widget = widget
        self.theme_service = service_container.get_theme_service()
        self.event_service = service_container.get_event_service()
        self.app = App.get_running_app()
    
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
        """KORRIGIERT: Wechselt den Theme-Stil über App für Persistierung"""
        try:
            if self.app and hasattr(self.app, 'update_theme'):
                if style in ['Light', 'Dark']:
                    self.app.update_theme(theme_style=style)
                    Logger.info(f"Theme-Stil über Manager gewechselt zu: {style}")
                    
                    # Event senden
                    if self.event_service:
                        self.event_service.publish(EventTypes.THEME_CHANGED, {'style': style})
                else:
                    Logger.warning(f"Ungültiger Theme-Stil: {style}")
            else:
                Logger.error("App oder update_theme nicht verfügbar im ThemeManager")
        except Exception as e:
            Logger.error(f"Fehler beim Theme-Stil-Wechsel im Manager: {str(e)}")
    
    def on_color_selected(self, color_name):
        """KORRIGIERT: Callback für Farbauswahl über App für Persistierung"""
        try:
            # Gültige KivyMD-Paletten definieren - angepasst an ThemeService
            valid_palettes = [
                'Red', 'Pink', 'Purple', 'Deeprurple', 'Indigo', 'Blue', 
                'Lightblue', 'Cyan', 'Teal', 'Green', 'Lightgreen', 'Lime',
                'Yellow', 'Amber', 'Orange', 'Deeporange', 'Brown', 
                'Gray', 'Bluegray'
            ]
            
            if self.app and hasattr(self.app, 'update_theme'):
                if color_name in valid_palettes:
                    self.app.update_theme(primary_palette=color_name)
                    Logger.info(f"Primärfarbe über Manager gewechselt zu: {color_name}")
                    
                    # Event senden
                    if self.event_service:
                        self.event_service.publish(EventTypes.THEME_CHANGED, {'color': color_name})
                else:
                    Logger.warning(f"Ungültige Palette '{color_name}' im Manager, verwende Orange als Fallback")
                    self.app.update_theme(primary_palette='Orange')
            else:
                Logger.error("App oder update_theme nicht verfügbar im ThemeManager")
        except Exception as e:
            Logger.error(f"Fehler beim Farb-Wechsel im Manager: {str(e)}")
    
    def update_color_chips(self):
        """Aktualisiert die Farb-Chips"""
        if self.theme_service and hasattr(self.widget.ids, 'colors_box'):
            self.theme_service.create_color_chips(
                self.widget.ids.colors_box, 
                self.on_color_selected
            )