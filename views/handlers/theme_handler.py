# views/handlers/theme_handler.py
"""
Theme-Management Handler für EinstellungenWidget
Ausgegliedert für bessere Code-Organisation
"""

from kivy.logger import Logger
from services.theme_service import ThemeService
from services.service_container import get_event_service
from services.event_service import EventTypes


class ThemeHandler:
    """Handler für Theme-Management Funktionalitäten"""
    
    def __init__(self, widget):
        self.widget = widget
        self.app = widget.app
        self.theme_service = ThemeService()
        
    def initialize_theme(self):
        """Initialisiert das Theme-System"""
        try:
            # Theme-Service initialisieren
            self.theme_service.initialize_theme()
            
            # Farb-Chips erstellen (falls colors_box verfügbar)
            if hasattr(self.widget.ids, 'colors_box'):
                self.theme_service.create_color_chips(
                    self.widget.ids.colors_box, 
                    self.on_color_selected
                )
            
            Logger.info("Theme-Handler initialisiert")
        except Exception as e:
            Logger.error(f"Fehler bei Theme-Initialisierung: {e}")

    def switch_theme_style(self, style):
        """Delegiert an ThemeManager oder direkt an App - KORRIGIERT mit Validierung"""
        try:
            Logger.info(f"Theme-Stil-Wechsel angefordert: {style}")
            
            # Prüfe ob ThemeManager verfügbar ist
            MANAGERS_AVAILABLE = hasattr(self.widget, 'theme_manager') and self.widget.theme_manager is not None
            
            if MANAGERS_AVAILABLE:
                self.widget.theme_manager.switch_theme_style(style)
            else:
                # Direkte App-Integration
                if self.app and hasattr(self.app, 'update_theme'):
                    if style in ['Light', 'Dark']:
                        self.app.update_theme(theme_style=style)
                        Logger.info(f"Theme-Stil gewechselt zu: {style}")
                    else:
                        Logger.warning(f"Ungültiger Theme-Stil '{style}' ignoriert")
                else:
                    Logger.error("App oder update_theme Methode nicht verfügbar")
        except Exception as e:
            Logger.error(f"Fehler beim Theme-Stil-Wechsel: {e}")

    def on_color_selected(self, color_name):
        """Delegiert an ThemeManager oder direkt an App - KORRIGIERT mit Palette-Validierung"""
        try:
            Logger.info(f"Farb-Wechsel angefordert: {color_name}")
            
            # Gültige KivyMD-Paletten definieren - angepasst an ThemeService
            valid_palettes = [
                'Red', 'Pink', 'Purple', 'Deeprurple', 'Indigo', 'Blue', 
                'Lightblue', 'Cyan', 'Teal', 'Green', 'Lightgreen', 'Lime',
                'Yellow', 'Amber', 'Orange', 'Deeporange', 'Brown', 
                'Gray', 'Bluegray'
            ]
            
            # Prüfe ob ThemeManager verfügbar ist
            MANAGERS_AVAILABLE = hasattr(self.widget, 'theme_manager') and self.widget.theme_manager is not None
            
            if MANAGERS_AVAILABLE:
                self.widget.theme_manager.on_color_selected(color_name)
            else:
                # Direkte App-Integration mit Validierung
                if self.app and hasattr(self.app, 'update_theme'):
                    if color_name in valid_palettes:
                        self.app.update_theme(primary_palette=color_name)
                        Logger.info(f"Primärfarbe gewechselt zu: {color_name}")
                    else:
                        Logger.warning(f"Ungültige Palette '{color_name}' ignoriert. Verwende 'Orange' als Fallback.")
                        self.app.update_theme(primary_palette='Orange')
                else:
                    Logger.error("App oder update_theme Methode nicht verfügbar")
        except Exception as e:
            Logger.error(f"Fehler beim Farb-Wechsel: {e}")
            
    def on_theme_changed(self, data):
        """Wird aufgerufen, wenn das Theme geändert wurde"""
        try:
            Logger.info(f"Theme geändert: {data}")
            
            # Prüfe ob ThemeManager verfügbar ist
            MANAGERS_AVAILABLE = hasattr(self.widget, 'theme_manager') and self.widget.theme_manager is not None
            
            if MANAGERS_AVAILABLE:
                self.widget.theme_manager.update_color_chips()
            else:
                # Direkte Aktualisierung der Farb-Chips
                if hasattr(self.widget.ids, 'colors_box'):
                    self.theme_service.update_color_chips(
                        self.widget.ids.colors_box,
                        self.on_color_selected
                    )
        except Exception as e:
            Logger.error(f"Fehler bei Theme-Change-Event: {e}")