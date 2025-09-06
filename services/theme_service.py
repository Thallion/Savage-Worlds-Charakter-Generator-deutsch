# services/theme_service.py
"""
Service für Theme-Management und Farbschema-Verwaltung
"""

from kivy.app import App
from kivy.logger import Logger
from kivymd.uix.chip import MDChip, MDChipText
from kivy.metrics import dp


class ThemeService:
    """Service für Theme- und Farbverwaltung"""
    
    def __init__(self):
        self.available_colors = [
            'Blau', 'Grün', 'Lila', 
            'Rot', 'Orange', 'Rosa',
            'Indigo', 'Limette', 'Gelb',
            'Blaugrün'
        ]
        self.current_color = ""
        
    def initialize_theme(self):
        """Initialisiert das Theme mit der aktuellen App-Konfiguration"""
        app = App.get_running_app()
        if app:
            self.current_color = app.theme_cls.primary_palette
            Logger.info(f"Theme initialisiert mit Farbe: {self.current_color}")
    
    def switch_theme_style(self, style):
        """
        Wechselt zwischen hellem und dunklem Theme
        
        Args:
            style (str): 'Light' oder 'Dark'
        """
        app = App.get_running_app()
        if app:
            app.theme_cls.theme_style = style
            Logger.info(f"Theme-Stil gewechselt zu: {style}")
    
    def switch_primary_palette(self, color_name):
        """
        Wechselt die primäre Farbpalette
        
        Args:
            color_name (str): Name der neuen Farbe
        """
        app = App.get_running_app()
        if app:
            app.theme_cls.primary_palette = color_name
            self.current_color = color_name
            Logger.info(f"Primäre Palette gewechselt zu: {color_name}")
            return True
        return False
    
    def update_color_chips(self, colors_container, on_color_selected):
        """
        Aktualisiert die Farb-Chips nach einer Farbänderung
        
        Args:
            colors_container: Container-Widget für die Chips
            on_color_selected: Callback-Funktion für Farbauswahl
        """
        # Einfach die Chips neu erstellen
        self.create_color_chips(colors_container, on_color_selected)
    
    def create_color_chips(self, colors_container, on_color_selected):
        """
        Erstellt Farb-Chips für die UI
        
        Args:
            colors_container: Container-Widget für die Chips
            on_color_selected: Callback-Funktion für Farbauswahl
        """
        if not colors_container:
            Logger.warning("Kein Container für Farb-Chips verfügbar")
            return
            
        # Aktuelle Farbe vor der Erstellung der Chips synchronisieren
        app = App.get_running_app()
        if app:
            self.current_color = app.theme_cls.primary_palette
            
        colors_container.clear_widgets()
        
        # Mapping von deutschen Namen zu KivyMD-Paletten
        color_mapping = {
            'Blau': 'Blue',
            'Grün': 'Green', 
            'Lila': 'Purple',
            'Rot': 'Red',
            'Orange': 'Orange',
            'Rosa': 'Pink',
            'Indigo': 'Indigo',
            'Limette': 'Lime',
            'Gelb': 'Yellow',
            'Blaugrün': 'Teal'
        }
        
        for farbe in self.available_colors:
            kivymd_palette = color_mapping.get(farbe, farbe)
            chip = MDChip(
                MDChipText(
                    text=farbe,
                    theme_text_color="Secondary",
                ),
                type="filter",
                active=kivymd_palette == self.current_color,
                md_bg_color=self._get_chip_background_color(kivymd_palette),
                on_release=lambda x, german=farbe, english=kivymd_palette: on_color_selected(english)
            )
            colors_container.add_widget(chip)
    
    def _get_chip_background_color(self, farbe):
        """
        Bestimmt die Hintergrundfarbe für einen Chip
        
        Args:
            farbe (str): Name der Farbe
            
        Returns:
            list: RGBA-Farbwerte
        """
        app = App.get_running_app()
        if app and farbe == self.current_color:
            return app.theme_cls.primaryColor
        return [0, 0, 0, 0]  # Transparent
    
    def get_current_theme_info(self):
        """
        Gibt Informationen über das aktuelle Theme zurück
        
        Returns:
            dict: Theme-Informationen
        """
        app = App.get_running_app()
        if app:
            return {
                'style': app.theme_cls.theme_style,
                'primary_palette': app.theme_cls.primary_palette,
                'primary_color': app.theme_cls.primaryColor
            }
        return {}