# services/pdf_service.py
"""
Service für PDF-Erstellung und -Verwaltung
"""

import os
from kivy.logger import Logger
from utils.pdf_utils import generiere_pdf


class PDFService:
    """Service für PDF-Erstellung und -Management"""
    
    def __init__(self, controller):
        self.controller = controller
    
    def create_character_pdf(self, output_path, printer_friendly=False):
        """
        Erstellt ein PDF des Charakterbogens
        
        Args:
            output_path (str): Pfad für die PDF-Datei
            printer_friendly (bool): Ob druckerfreundliche Version erstellt werden soll
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            success = generiere_pdf(self.controller.charakter, output_path, printer_friendly)
            
            if success:
                Logger.info(f"PDF erfolgreich erstellt: {output_path}")
                return True
            else:
                Logger.error(f"Fehler beim Erstellen der PDF: {output_path}")
                return False
                
        except Exception as e:
            Logger.error(f"Ausnahme beim Erstellen der PDF: {str(e)}", exc_info=True)
            return False
    
    def get_default_pdf_name(self):
        """
        Erstellt einen Standard-PDF-Namen basierend auf dem Charakter
        
        Returns:
            str: Standard-PDF-Dateiname
        """
        if hasattr(self.controller, 'current_character_file_path') and self.controller.current_character_file_path:
            # Aus dem aktuellen Charakter-Pfad ableiten
            char_path = self.controller.current_character_file_path
            return os.path.splitext(os.path.basename(char_path))[0] + ".pdf"
        else:
            # Aus dem Charakternamen ableiten
            character_name = self.controller.charakter.char_name if self.controller.charakter.char_name else "charakter"
            return f"{character_name.strip().replace(' ', '_')}.pdf"
    
    def check_existing_pdf(self):
        """
        Prüft, ob bereits eine PDF-Datei für den aktuellen Charakter existiert
        
        Returns:
            tuple: (exists: bool, path: str, name: str)
        """
        if hasattr(self.controller, 'current_character_file_path') and self.controller.current_character_file_path:
            char_path = self.controller.current_character_file_path
            pdf_name = os.path.splitext(os.path.basename(char_path))[0] + ".pdf"
            pdf_path = os.path.join(os.path.dirname(char_path), pdf_name)
            
            return os.path.exists(pdf_path), pdf_path, pdf_name
        
        return False, "", ""
    
    def validate_pdf_filename(self, filename):
        """
        Validiert und korrigiert einen PDF-Dateinamen
        
        Args:
            filename (str): Zu validierender Dateiname
            
        Returns:
            str: Korrigierter Dateiname oder None bei Fehler
        """
        if not filename or not filename.strip():
            return None
        
        filename = filename.strip()
        
        # .pdf-Endung hinzufügen, falls nicht vorhanden
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        # Ungültige Zeichen entfernen (vereinfacht)
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        return filename
    
    def get_pdf_options(self):
        """
        Gibt verfügbare PDF-Optionen zurück
        
        Returns:
            dict: PDF-Optionen mit Standardwerten
        """
        return {
            'printer_friendly': False,
            'include_background': True,
            'paper_size': 'A4',
            'margins': 'normal'
        }
    
    def estimate_pdf_size(self, character):
        """
        Schätzt die Anzahl der Seiten für die PDF basierend auf dem Charakter
        
        Args:
            character: Charakter-Objekt
            
        Returns:
            int: Geschätzte Anzahl Seiten
        """
        # Einfache Schätzung basierend auf Inhalten
        pages = 1  # Basis-Seite
        
        # Zusätzliche Seiten für umfangreiche Inhalte
        if len(character.selected_talente) > 10:
            pages += 1
        
        if len(character.selected_maechte) > 5:
            pages += 1
        
        if len(character.selected_allgemeine_ausruestung) > 20:
            pages += 1
        
        return min(pages, 5)  # Max. 5 Seiten
    
    def create_pdf_preview_info(self, character):
        """
        Erstellt Informationen für eine PDF-Vorschau
        
        Args:
            character: Charakter-Objekt
            
        Returns:
            dict: Preview-Informationen
        """
        return {
            'character_name': character.char_name or "Unbenannter Charakter",
            'estimated_pages': self.estimate_pdf_size(character),
            'creation_date': "Heute",
            'includes': {
                'profile': True,
                'attributes': True,
                'skills': True,
                'talents': len(character.selected_talente),
                'powers': len(character.selected_maechte),
                'equipment': len(character.selected_allgemeine_ausruestung),
                'weapons': len(character.selected_waffen),
                'armor': len(character.selected_ruestungen)
            }
        }