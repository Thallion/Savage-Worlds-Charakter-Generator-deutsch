# services/html_service.py
"""
Service für HTML-Erstellung und -Verwaltung
Plattformunabhängige Alternative zum PDF-Service
"""

import os
from kivy.logger import Logger
from utils.html_utils import generiere_html


class HTMLService:
    """Service für HTML-Erstellung und -Management"""

    def __init__(self, controller):
        self.controller = controller

    def is_html_supported(self):
        """
        HTML-Export ist immer verfügbar (keine externen Abhängigkeiten)

        Returns:
            bool: Immer True
        """
        return True

    def create_character_html(self, output_path, printer_friendly=False, show_steigerungen=True):
        """
        Erstellt eine HTML-Datei des Charakterbogens

        Args:
            output_path (str): Pfad für die HTML-Datei
            printer_friendly (bool): Ob druckerfreundliche Version erstellt werden soll
            show_steigerungen (bool): Ob die Steigerungsliste eingeblendet werden soll

        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            success = generiere_html(self.controller.charakter, output_path, printer_friendly, show_steigerungen)

            if success:
                Logger.info(f"HTML erfolgreich erstellt: {output_path}")
                return True
            else:
                Logger.error(f"Fehler beim Erstellen der HTML: {output_path}")
                return False

        except Exception as e:
            Logger.error(f"Ausnahme beim Erstellen der HTML: {str(e)}")
            return False

    def get_default_html_name(self):
        """
        Erstellt einen Standard-HTML-Namen basierend auf dem Charakter

        Returns:
            str: Standard-HTML-Dateiname
        """
        if hasattr(self.controller, 'current_character_file_path') and self.controller.current_character_file_path:
            char_path = self.controller.current_character_file_path
            return os.path.splitext(os.path.basename(char_path))[0] + ".html"
        else:
            character_name = self.controller.charakter.char_name if self.controller.charakter.char_name else "charakter"
            return f"{character_name.strip().replace(' ', '_')}.html"

    def check_existing_html(self):
        """
        Prüft, ob bereits eine HTML-Datei für den aktuellen Charakter existiert

        Returns:
            tuple: (exists: bool, path: str, name: str)
        """
        if hasattr(self.controller, 'current_character_file_path') and self.controller.current_character_file_path:
            char_path = self.controller.current_character_file_path
            html_name = os.path.splitext(os.path.basename(char_path))[0] + ".html"
            html_path = os.path.join(os.path.dirname(char_path), html_name)

            return os.path.exists(html_path), html_path, html_name

        return False, "", ""
