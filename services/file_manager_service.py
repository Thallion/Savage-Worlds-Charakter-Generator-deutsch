# services/file_manager_service.py
"""
Service für Datei-Management und File-Browser-Operationen
Korrigierte Version mit richtiger Pfad-Behandlung
"""

import os
import sys
import string
from pathlib import Path
from kivy.logger import Logger
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivy.metrics import dp
from utils.custom_filemanager import CustomFileManager


class FileManagerService:
    """Service für Datei-Management-Operationen"""
    
    def __init__(self, controller):
        self.controller = controller
        self.manager_open = False
        self.current_action = None
        self.drive_dialog = None
        self.is_windows = os.name == 'nt'
        
        # File Manager erstellen
        self.file_manager = CustomFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False,
        )
        
        # Temporäre Attribute für Aktionen
        self.temp_filename = ""
        self.temp_pdf_filename = ""
        self.temp_printer_friendly = False
    
    def get_default_directory(self, dir_type='chars'):
        """
        Bestimmt das Standard-Verzeichnis basierend auf dem Typ
        
        Args:
            dir_type (str): Typ des Verzeichnisses ('chars', 'pdfs', etc.)
            
        Returns:
            str: Pfad zum Standard-Verzeichnis
        """
        if getattr(sys, 'frozen', False):
            # Ausführbare Version
            base_dir = os.path.dirname(sys.executable)
        else:
            # Entwicklungsversion: Gehe vom services/ Ordner zum parent directory
            services_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(services_dir)  # parent directory (build/)
        
        target_dir = os.path.join(base_dir, dir_type)
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
                Logger.info(f"Verzeichnis erstellt: {target_dir}")
            except Exception as e:
                Logger.error(f"Fehler beim Erstellen des Verzeichnisses {target_dir}: {str(e)}")
        
        Logger.debug(f"Standard-Verzeichnis für '{dir_type}': {target_dir}")
        return target_dir
    
    def show_file_manager(self, path, action_type):
        """
        Zeigt den FileManager mit optionaler Laufwerksauswahl
        
        Args:
            path (str): Startpfad
            action_type (str): Art der Aktion
        """
        if not os.path.exists(path):
            Logger.warning(f"Pfad existiert nicht: {path}")
            path = os.path.expanduser("~")
        
        self.current_action = action_type
        
        if self.is_windows:
            self.show_drive_selector(path, action_type)
        else:
            self._show_file_manager_direct(path)
    
    def show_drive_selector(self, default_path, action_type):
        """
        Zeigt Dialog zur Laufwerksauswahl (Windows)
        
        Args:
            default_path (str): Standard-Pfad
            action_type (str): Art der Aktion
        """
        available_drives = self._get_available_drives()
        
        if not available_drives:
            self._show_file_manager_direct(default_path)
            return
        
        content = self._create_drive_selector_content(available_drives, default_path)
        
        self.drive_dialog = MDDialog(
            MDDialogHeadlineText(text="Laufwerksauswahl"),
            MDDialogContentContainer(content, orientation="vertical"),
        )
        self.drive_dialog.open()
    
    def _get_available_drives(self):
        """Ermittelt verfügbare Laufwerke"""
        available_drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                available_drives.append((letter, drive))
        return available_drives
    
    def _create_drive_selector_content(self, available_drives, default_path):
        """Erstellt den Inhalt für den Laufwerks-Dialog"""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(300),
            padding=dp(20)
        )
        
        content.add_widget(MDLabel(
            text="Laufwerk auswählen",
            font_size=dp(20),
            halign="center"
        ))
        
        drive_grid = MDGridLayout(cols=4, spacing=dp(10), adaptive_height=True)
        
        for letter, drive_path in available_drives:
            drive_button = MDButton(
                style="elevated",
                size_hint=(None, None),
                size=(dp(80), dp(50)),
                on_release=lambda x, p=drive_path: self.select_drive(p)
            )
            drive_button.add_widget(MDButtonText(text=f"{letter}:"))
            drive_grid.add_widget(drive_button)
        
        content.add_widget(drive_grid)
        
        current_drive = os.path.splitdrive(default_path)[0] + "\\"
        info_label = MDLabel(
            text=f"Aktuelles Laufwerk: {current_drive}",
            halign="center"
        )
        content.add_widget(info_label)
        
        cancel_button = MDButton(
            style="elevated",
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self._continue_with_path(default_path)
        )
        cancel_button.add_widget(MDButtonText(text="Aktuelles Laufwerk verwenden"))
        content.add_widget(cancel_button)
        
        return content
    
    def select_drive(self, path):
        """Wählt ein Laufwerk aus"""
        if self.drive_dialog:
            self.drive_dialog.dismiss()
            self.drive_dialog = None
        
        self._show_file_manager_direct(path)
    
    def _continue_with_path(self, path):
        """Setzt mit dem gegebenen Pfad fort"""
        if self.drive_dialog:
            self.drive_dialog.dismiss()
            self.drive_dialog = None
        
        self._show_file_manager_direct(path)
    
    def _show_file_manager_direct(self, path):
        """Zeigt den FileManager direkt an"""
        self.file_manager.show(path)
        self.manager_open = True
    
    def exit_manager(self, *args):
        """Schließt den FileManager"""
        self.manager_open = False
        self.file_manager.close()
    
    def select_path(self, path):
        """
        Verarbeitet ausgewählten Pfad basierend auf der aktuellen Aktion
        
        Args:
            path (str): Ausgewählter Pfad
        """
        self.exit_manager()
        
        try:
            if self.current_action == "save_dir":
                self._handle_save_directory(path)
            elif self.current_action == "load":
                self._handle_load_file(path)
            elif self.current_action == "save_pdf_dir":
                self._handle_save_pdf_directory(path)
            else:
                Logger.warning(f"Unbekannter Aktionstyp: {self.current_action}")
        except Exception as e:
            Logger.error(f"Fehler bei Pfad-Verarbeitung: {str(e)}", exc_info=True)
            self._show_error(f"Fehler bei der Verarbeitung: {str(e)}")
    
    def _handle_save_directory(self, path):
        """Behandelt Verzeichnisauswahl zum Speichern"""
        if os.path.isdir(path):
            full_path = os.path.join(path, self.temp_filename)
            
            if os.path.exists(full_path):
                self._request_overwrite_confirmation(full_path, self._save_character)
            else:
                self._save_character(full_path)
        else:
            self._show_error("Bitte wähle ein Verzeichnis für die Speicherung aus.")
    
    def _handle_load_file(self, path):
        """Behandelt Dateiauswahl zum Laden"""
        if not os.path.exists(path):
            self._show_error(f"Der Pfad existiert nicht: {path}")
            return
        
        if os.path.isfile(path) and path.endswith('.json'):
            success = self.controller.lade_charakter_von_json(path)
            if success:
                Logger.info(f"Charakter geladen: {path}")
                self._show_success("Charakter erfolgreich geladen", 
                                 "Der Charakter wurde aus der Datei geladen.")
            else:
                self._show_error("Fehler beim Laden des Charakters.")
        else:
            if os.path.isdir(path):
                self._show_error("Bitte wähle eine .json Charakterdatei aus.")
            else:
                self._show_error(f"Die Datei ist keine gültige JSON-Datei: {os.path.basename(path)}")
    
    def _handle_save_pdf_directory(self, path):
        """Behandelt Verzeichnisauswahl für PDF-Speicherung"""
        if os.path.isdir(path):
            full_path = os.path.join(path, self.temp_pdf_filename)
            
            if os.path.exists(full_path):
                self._request_overwrite_confirmation(full_path, self._save_pdf)
            else:
                self._save_pdf(full_path)
        else:
            self._show_error("Bitte wähle ein Verzeichnis für die Speicherung aus.")
    
    def _save_character(self, filepath):
        """Speichert den Charakter"""
        try:
            success = self.controller.speichere_charakter_als_json(filepath)
            if success:
                self._show_success("Speichern erfolgreich", f"Charakter wurde gespeichert als:\n{filepath}")
            else:
                self._show_error("Fehler beim Speichern des Charakters")
        except Exception as e:
            self._show_error(f"Fehler beim Speichern: {str(e)}")
    
    def _save_pdf(self, filepath):
        """Speichert die PDF"""
        try:
            from utils.pdf_utils import generiere_pdf
            success = generiere_pdf(self.controller.charakter, filepath, self.temp_printer_friendly)
            
            if success:
                self._show_success("PDF erstellen erfolgreich", f"PDF wurde gespeichert als:\n{filepath}")
            else:
                self._show_error("Fehler beim Erstellen der PDF-Datei.")
        except Exception as e:
            self._show_error(f"Fehler beim Erstellen der PDF: {str(e)}")
    
    def _request_overwrite_confirmation(self, filepath, callback):
        """Fragt nach Bestätigung zum Überschreiben"""
        # Hier würde normalerweise ein Dialog gezeigt werden
        # Für Einfachheit direkt überschreiben
        callback(filepath)
    
    def _show_error(self, message):
        """Zeigt eine Fehlermeldung"""
        Logger.error(f"FileManagerService Error: {message}")
        # Hier könnte ein Error-Dialog gezeigt werden
    
    def _show_success(self, title, message):
        """Zeigt eine Erfolgsmeldung"""
        Logger.info(f"FileManagerService Success: {title} - {message}")
        # Hier könnte ein Success-Dialog gezeigt werden
    
    def set_temp_filename(self, filename):
        """Setzt den temporären Dateinamen"""
        self.temp_filename = filename
        Logger.debug(f"Temp filename gesetzt: {filename}")
    
    def set_temp_pdf_settings(self, filename, printer_friendly=False):
        """Setzt die temporären PDF-Einstellungen"""
        self.temp_pdf_filename = filename
        self.temp_printer_friendly = printer_friendly
        Logger.debug(f"Temp PDF settings gesetzt: {filename}, printer_friendly: {printer_friendly}")