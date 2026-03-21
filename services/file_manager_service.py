# services/file_manager_service.py
"""
Service für Datei-Management und File-Browser-Operationen
KORRIGIERT: Bessere Pfad-Behandlung und Dateiname-Generierung
"""

import os
import sys
import string
from pathlib import Path
from datetime import datetime
from kivy.logger import Logger

# Import centralized path utilities
from utils.path_utils import get_chars_path, get_templates_path, get_application_root
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
        self._android_permissions_granted = False

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
        self.template_callback = None

    def _request_android_permissions(self, callback=None):
        """
        Fordert Speicher-Berechtigungen auf Android an (READ/WRITE_EXTERNAL_STORAGE).
        """
        from kivy.utils import platform as kivy_platform
        if kivy_platform != 'android':
            self._android_permissions_granted = True
            if callback:
                callback()
            return

        try:
            from android.permissions import request_permissions, Permission, check_permission
            from kivy.clock import Clock

            needed = []
            try:
                if not check_permission(Permission.READ_EXTERNAL_STORAGE):
                    needed.append(Permission.READ_EXTERNAL_STORAGE)
                if not check_permission(Permission.WRITE_EXTERNAL_STORAGE):
                    needed.append(Permission.WRITE_EXTERNAL_STORAGE)
            except Exception:
                needed = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]

            if needed:
                def _on_permissions(permissions, results):
                    try:
                        granted = all(results)
                        self._android_permissions_granted = granted

                        def _continue_on_main_thread(dt):
                            if granted:
                                Logger.info("Android Speicher-Berechtigungen erteilt")
                            else:
                                Logger.warning("Android Speicher-Berechtigungen verweigert")
                            if callback:
                                callback()

                        Clock.schedule_once(_continue_on_main_thread, 0.1)
                    except Exception as e:
                        self._android_permissions_granted = True
                        try:
                            Clock.schedule_once(lambda dt: callback() if callback else None, 0.1)
                        except Exception:
                            pass

                request_permissions(needed, _on_permissions)
            else:
                self._android_permissions_granted = True
                if callback:
                    callback()

        except ImportError:
            Logger.warning("android.permissions nicht verfügbar")
            self._android_permissions_granted = True
            if callback:
                callback()
        except Exception as e:
            Logger.error(f"Fehler bei Android-Berechtigungsanforderung: {e}")
            self._android_permissions_granted = True
            if callback:
                callback()
    
    def get_default_directory(self, dir_type='chars'):
        """
        Bestimmt das Standard-Verzeichnis basierend auf dem Typ und letzten verwendeten Pfad

        Args:
            dir_type (str): Typ des Verzeichnisses ('chars', 'pdfs', etc.)

        Returns:
            str: Pfad zum Verzeichnis (letzter verwendeter Pfad oder Standard-Fallback)
        """
        try:
            # Ersten: Versuche letzten verwendeten Pfad aus Konfiguration zu laden
            last_used_dir = self._get_last_used_directory(dir_type)
            if last_used_dir and os.path.exists(last_used_dir) and os.path.isdir(last_used_dir):
                Logger.debug(f"Verwende letzten Pfad für '{dir_type}': {last_used_dir}")
                return last_used_dir

            # Fallback: Standard-Verzeichnis bestimmen
            if dir_type == 'chars':
                target_dir = get_chars_path()
            elif dir_type == 'templates':
                target_dir = get_templates_path()
            else:
                # Für andere Verzeichnisse verwende application root
                app_root = get_application_root()
                target_dir = str(app_root / dir_type)

            # KORRIGIERT: Bessere Verzeichniserstellung mit Fehlerbehandlung
            if not os.path.exists(target_dir):
                try:
                    os.makedirs(target_dir, exist_ok=True)
                    Logger.info(f"Verzeichnis erstellt: {target_dir}")
                except Exception as e:
                    Logger.error(f"Fehler beim Erstellen des Verzeichnisses {target_dir}: {str(e)}")
                    # Fallback auf Home-Verzeichnis
                    fallback_dir = os.path.join(os.path.expanduser("~"), dir_type)
                    try:
                        os.makedirs(fallback_dir, exist_ok=True)
                        target_dir = fallback_dir
                        Logger.warning(f"Fallback-Verzeichnis verwendet: {target_dir}")
                    except Exception as e2:
                        Logger.error(f"Auch Fallback-Verzeichnis konnte nicht erstellt werden: {str(e2)}")
                        # Letzter Fallback: Home-Verzeichnis
                        target_dir = os.path.expanduser("~")

            Logger.debug(f"Standard-Verzeichnis für '{dir_type}': {target_dir}")
            return target_dir

        except Exception as e:
            Logger.error(f"Fehler bei get_default_directory: {str(e)}")
            # Final fallback
            return os.path.expanduser("~")

    def _get_last_used_directory(self, dir_type):
        """
        Lädt den zuletzt verwendeten Pfad für den gegebenen Verzeichnistyp aus der Konfiguration

        Args:
            dir_type (str): Verzeichnistyp ('chars', 'pdfs')

        Returns:
            str: Letzter verwendeter Pfad oder None
        """
        try:
            from services.service_container import service_container
            config_service = service_container.get_config_service()
            if not config_service:
                return None

            if dir_type == 'chars':
                return config_service.config.last_character_directory
            elif dir_type == 'pdfs':
                return config_service.config.last_pdf_directory
            else:
                return None
        except Exception as e:
            Logger.error(f"Fehler beim Laden des letzten Pfads für '{dir_type}': {str(e)}")
            return None

    def _save_last_used_directory(self, dir_type, directory_path):
        """
        Speichert den letzten verwendeten Pfad für den gegebenen Verzeichnistyp in der Konfiguration

        Args:
            dir_type (str): Verzeichnistyp ('chars', 'pdfs')
            directory_path (str): Verzeichnispfad zum Speichern
        """
        try:
            from services.service_container import service_container
            config_service = service_container.get_config_service()
            if not config_service:
                Logger.warning("Config-Service nicht verfügbar, kann letzten Pfad nicht speichern")
                return

            if dir_type == 'chars':
                config_service.config.last_character_directory = directory_path
            elif dir_type == 'pdfs':
                config_service.config.last_pdf_directory = directory_path
            else:
                Logger.warning(f"Unbekannter Verzeichnistyp: {dir_type}")
                return

            config_service.save_config()
            Logger.debug(f"Letzter Pfad für '{dir_type}' gespeichert: {directory_path}")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern des letzten Pfads für '{dir_type}': {str(e)}")

    def generate_default_filename(self, file_type='character'):
        """
        Generiert einen Standard-Dateinamen basierend auf dem Charakternamen und Typ
        
        Args:
            file_type (str): Typ der Datei ('character', 'pdf')
            
        Returns:
            str: Generierter Dateiname
        """
        try:
            if self.controller and self.controller.charakter:
                char_name = getattr(self.controller.charakter, 'char_name', '')
                if char_name:
                    # Ungültige Zeichen für Dateinamen entfernen
                    safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_name = safe_name.replace(' ', '_')
                else:
                    safe_name = "Charakter"
            else:
                safe_name = "Charakter"
            
            # Zeitstempel hinzufügen
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if file_type == 'character':
                filename = f"{safe_name}_{timestamp}.json"
            elif file_type == 'pdf':
                filename = f"{safe_name}_{timestamp}.pdf"
            else:
                filename = f"{safe_name}_{timestamp}.{file_type}"
            
            Logger.debug(f"Generierter Dateiname: {filename}")
            return filename
            
        except Exception as e:
            Logger.error(f"Fehler bei Dateiname-Generierung: {str(e)}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"Charakter_{timestamp}.json"
    
    def show_file_manager(self, path, action_type):
        """
        Zeigt den FileManager mit optionaler Laufwerksauswahl.
        Auf Android werden zuerst Speicher-Berechtigungen angefordert.

        Args:
            path (str): Startpfad
            action_type (str): Art der Aktion
        """
        # KORRIGIERT: Automatische Dateiname-Generierung für Speicher-Aktionen
        if action_type == "save_dir" and not self.temp_filename:
            self.temp_filename = self.generate_default_filename('character')
            Logger.info(f"Automatisch generierter Dateiname: {self.temp_filename}")
        elif action_type == "save_pdf_dir" and not self.temp_pdf_filename:
            self.temp_pdf_filename = self.generate_default_filename('pdf')
            Logger.info(f"Automatisch generierter PDF-Dateiname: {self.temp_pdf_filename}")
        elif action_type == "save_html_dir" and not getattr(self, 'temp_html_filename', ''):
            self.temp_html_filename = self.generate_default_filename('html')
            Logger.info(f"Automatisch generierter HTML-Dateiname: {self.temp_html_filename}")

        if not os.path.exists(path):
            Logger.warning(f"Pfad existiert nicht: {path}")
            # KORRIGIERT: Besserer Fallback
            if action_type == 'load_template':
                path = self.get_default_directory('templates')
            elif action_type in ['save_dir', 'load']:
                path = self.get_default_directory('chars')
            else:
                path = os.path.expanduser("~")

        self.current_action = action_type

        # Android: Berechtigungen bei jedem Aufruf prüfen
        from kivy.utils import platform as kivy_platform
        if kivy_platform == 'android':
            Logger.info(f"Android FileManager: permissions_granted={self._android_permissions_granted}")
            if not self._android_permissions_granted:
                Logger.info("Android: Fordere Berechtigungen an...")
                self._request_android_permissions(
                    callback=lambda: self._open_file_manager_for_platform(path)
                )
            else:
                Logger.info("Android: Berechtigungen vorhanden, öffne FileManager...")
                self._open_file_manager_for_platform(path)
        else:
            self._open_file_manager_for_platform(path)

    def _open_file_manager_for_platform(self, path):
        """Öffnet den FileManager plattformspezifisch"""
        from kivy.utils import platform as kivy_platform

        # Android: Sicherstellen dass der Pfad existiert und zugreifbar ist
        if kivy_platform == 'android':
            path = self._get_valid_android_path(path)

        Logger.info(f"FileManager öffnen mit Pfad: {path}")

        if self.is_windows:
            self.show_drive_selector(path, self.current_action)
        else:
            self._show_file_manager_direct(path)

    def _get_valid_android_path(self, path):
        """Ermittelt einen gültigen und zugreifbaren Pfad auf Android.
        Verwendet den app-internen chars/ Ordner als Standard."""

        # Prüfe ob der übergebene Pfad existiert und zugreifbar ist
        if path and os.path.exists(path) and os.access(path, os.R_OK):
            return path

        Logger.info(f"Android: Pfad nicht zugreifbar: {path}")

        # Standard: App-internes chars/ Verzeichnis
        chars_dir = get_chars_path()
        if os.path.exists(chars_dir) and os.access(chars_dir, os.R_OK):
            Logger.info(f"Android: Verwende chars-Verzeichnis: {chars_dir}")
            return chars_dir

        # chars/ Verzeichnis erstellen falls nicht vorhanden
        try:
            os.makedirs(chars_dir, exist_ok=True)
            Logger.info(f"Android: chars-Verzeichnis erstellt: {chars_dir}")
            return chars_dir
        except Exception as e:
            Logger.warning(f"Android: Konnte chars-Verzeichnis nicht erstellen: {e}")

        # Fallback: App-Wurzelverzeichnis
        app_root = str(get_application_root())
        if os.path.exists(app_root):
            Logger.info(f"Android: Verwende App-Root: {app_root}")
            return app_root

        home = os.path.expanduser("~")
        Logger.warning(f"Android: Verwende Home als letzten Fallback: {home}")
        return home
    
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
        try:
            Logger.info(f"FileManager.show() aufrufen mit: {path}")
            self.file_manager.show(path)
            self.manager_open = True
            Logger.info("FileManager erfolgreich geöffnet")
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des FileManagers: {e}", exc_info=True)
            # Fallback: Versuche mit Home-Verzeichnis
            try:
                fallback = os.path.expanduser("~")
                Logger.info(f"FileManager Fallback mit: {fallback}")
                self.file_manager.show(fallback)
                self.manager_open = True
            except Exception as e2:
                Logger.error(f"FileManager Fallback ebenfalls fehlgeschlagen: {e2}")
    
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
            Logger.info(f"Ausgewählter Pfad: {path}")
            Logger.info(f"Aktuelle Aktion: {self.current_action}")
            
            if self.current_action == "save_dir":
                self._handle_save_directory(path)
            elif self.current_action == "load":
                self._handle_load_file(path)
            elif self.current_action == "save_pdf_dir":
                self._handle_save_pdf_directory(path)
            elif self.current_action == "save_html_dir":
                self._handle_save_html_directory(path)
            elif self.current_action == "load_template":
                self._handle_load_template(path)
            else:
                Logger.warning(f"Unbekannter Aktionstyp: {self.current_action}")
        except Exception as e:
            Logger.error(f"Fehler bei Pfad-Verarbeitung: {str(e)}", exc_info=True)
            self._show_error(f"Fehler bei der Verarbeitung: {str(e)}")
    
    def _handle_save_directory(self, path):
        """KORRIGIERT: Behandelt Verzeichnisauswahl zum Speichern"""
        try:
            # Überprüfen ob ein Dateiname gesetzt ist
            if not self.temp_filename:
                self.temp_filename = self.generate_default_filename('character')
                Logger.warning(f"Kein temp_filename gesetzt, generiere automatisch: {self.temp_filename}")
            
            if os.path.isdir(path):
                # Verzeichnis ausgewählt - Dateiname anhängen
                full_path = os.path.join(path, self.temp_filename)
            elif os.path.isfile(path):
                # Datei ausgewählt - verwende den Pfad direkt
                full_path = path
            else:
                # Pfad existiert nicht - erstelle Verzeichnis falls nötig
                parent_dir = os.path.dirname(path)
                if not os.path.exists(parent_dir):
                    try:
                        os.makedirs(parent_dir, exist_ok=True)
                        Logger.info(f"Verzeichnis erstellt: {parent_dir}")
                    except Exception as e:
                        Logger.error(f"Konnte Verzeichnis nicht erstellen: {str(e)}")
                        self._show_error(f"Konnte Verzeichnis nicht erstellen: {str(e)}")
                        return
                
                # Wenn der Pfad eine Dateiendung hat, verwende ihn direkt
                if path.endswith('.json'):
                    full_path = path
                else:
                    # Andernfalls als Verzeichnis behandeln
                    full_path = os.path.join(path, self.temp_filename)
            
            # Sicherstellen dass der Pfad mit .json endet
            if not full_path.endswith('.json'):
                if full_path.endswith('\\') or full_path.endswith('/'):
                    full_path = full_path + self.temp_filename
                else:
                    full_path = full_path + '.json'
            
            Logger.info(f"Vollständiger Speicherpfad: {full_path}")
            
            # Überprüfen ob Datei bereits existiert
            if os.path.exists(full_path):
                self._request_overwrite_confirmation(full_path, self._save_character)
            else:
                self._save_character(full_path)
                
        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten des Speicherpfads: {str(e)}", exc_info=True)
            self._show_error(f"Fehler beim Verarbeiten des Speicherpfads: {str(e)}")
    
    def _handle_load_file(self, path):
        """Behandelt Dateiauswahl zum Laden"""
        if not os.path.exists(path):
            self._show_error(f"Der Pfad existiert nicht: {path}")
            return
        
        if os.path.isfile(path) and path.endswith('.json'):
            success = self.controller.lade_charakter_von_json(path)
            if success:
                Logger.info(f"Charakter geladen: {path}")
                # Letzten verwendeten Pfad speichern
                directory = os.path.dirname(path)
                self._save_last_used_directory('chars', directory)
                self._show_success("Charakter erfolgreich geladen",
                                 "Der Charakter wurde aus der Datei geladen.")
            else:
                self._show_error("Fehler beim Laden des Charakters.")
        else:
            if os.path.isdir(path):
                self._show_error("Bitte wähle eine .json Charakterdatei aus.")
            else:
                self._show_error(f"Die Datei ist keine gültige JSON-Datei: {os.path.basename(path)}")
    
    def _handle_load_template(self, path):
        """Behandelt Dateiauswahl zum Laden eines Templates"""
        if not os.path.exists(path):
            self._show_error(f"Der Pfad existiert nicht: {path}")
            return

        if os.path.isdir(path):
            self._show_error("Bitte wähle eine .json Template-Datei aus.")
            return

        if not path.endswith('.json'):
            self._show_error(f"Die Datei ist keine gültige JSON-Datei: {os.path.basename(path)}")
            return

        if self.template_callback:
            self.template_callback(path)
        else:
            Logger.warning("Kein template_callback registriert")

    def _handle_save_pdf_directory(self, path):
        """KORRIGIERT: Behandelt Verzeichnisauswahl für PDF-Speicherung"""
        try:
            # Überprüfen ob ein PDF-Dateiname gesetzt ist
            if not self.temp_pdf_filename:
                self.temp_pdf_filename = self.generate_default_filename('pdf')
                Logger.warning(f"Kein temp_pdf_filename gesetzt, generiere automatisch: {self.temp_pdf_filename}")
            
            if os.path.isdir(path):
                full_path = os.path.join(path, self.temp_pdf_filename)
            elif path.endswith('.pdf'):
                full_path = path
            else:
                full_path = path + '.pdf'
            
            Logger.info(f"Vollständiger PDF-Speicherpfad: {full_path}")
            
            if os.path.exists(full_path):
                self._request_overwrite_confirmation(full_path, self._save_pdf)
            else:
                self._save_pdf(full_path)
                
        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten des PDF-Speicherpfads: {str(e)}", exc_info=True)
            self._show_error(f"Fehler beim Verarbeiten des PDF-Speicherpfads: {str(e)}")
    
    def _handle_save_html_directory(self, path):
        """Behandelt Verzeichnisauswahl für HTML-Speicherung"""
        try:
            if not getattr(self, 'temp_html_filename', ''):
                self.temp_html_filename = self.generate_default_filename('html')
                Logger.warning(f"Kein temp_html_filename gesetzt, generiere automatisch: {self.temp_html_filename}")

            if os.path.isdir(path):
                full_path = os.path.join(path, self.temp_html_filename)
            elif path.endswith('.html'):
                full_path = path
            else:
                full_path = path + '.html'

            Logger.info(f"Vollständiger HTML-Speicherpfad: {full_path}")

            if os.path.exists(full_path):
                self._request_overwrite_confirmation(full_path, self._save_html)
            else:
                self._save_html(full_path)

        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten des HTML-Speicherpfads: {str(e)}", exc_info=True)
            self._show_error(f"Fehler beim Verarbeiten des HTML-Speicherpfads: {str(e)}")

    def _save_html(self, filepath):
        """Speichert die HTML-Datei"""
        try:
            Logger.info(f"Versuche HTML zu speichern unter: {filepath}")

            # Verzeichnis erstellen falls nötig
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                Logger.info(f"Verzeichnis erstellt: {directory}")

            from utils.html_utils import generiere_html
            printer_friendly = getattr(self, 'temp_html_printer_friendly', False)
            success = generiere_html(self.controller.charakter, filepath, printer_friendly)

            if success:
                self._show_success("HTML erstellen erfolgreich", f"HTML wurde gespeichert als:\n{filepath}")
                directory = os.path.dirname(filepath)
                self._save_last_used_directory('html', directory)
                # Reset temp settings
                self.temp_html_filename = ""
                self.temp_html_printer_friendly = False

                # Im Browser öffnen (plattformspezifisch)
                from kivy.utils import platform as kivy_platform
                if kivy_platform == 'android':
                    from manager.html_manager import HTMLManager
                    HTMLManager._open_file_on_android(os.path.abspath(filepath), 'text/html')
                else:
                    import webbrowser
                    file_url = 'file://' + os.path.abspath(filepath)
                    webbrowser.open(file_url)
            else:
                self._show_error("Fehler beim Erstellen der HTML-Datei.")
        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der HTML: {str(e)}", exc_info=True)
            self._show_error(f"Fehler beim Erstellen der HTML: {str(e)}")

    def _save_character(self, filepath):
        """Speichert den Charakter"""
        try:
            Logger.info(f"Versuche Charakter zu speichern unter: {filepath}")
            
            # Verzeichnis erstellen falls nötig
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                Logger.info(f"Verzeichnis erstellt: {directory}")
            
            success = self.controller.speichere_charakter_als_json(filepath)
            if success:
                self._show_success("Speichern erfolgreich", f"Charakter wurde gespeichert als:\n{filepath}")
                # Letzten verwendeten Pfad speichern
                directory = os.path.dirname(filepath)
                self._save_last_used_directory('chars', directory)
                # Reset temp filename
                self.temp_filename = ""
            else:
                self._show_error("Fehler beim Speichern des Charakters")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern: {str(e)}", exc_info=True)
            self._show_error(f"Fehler beim Speichern: {str(e)}")
    
    def _save_pdf(self, filepath):
        """Speichert die PDF"""
        try:
            Logger.info(f"Versuche PDF zu speichern unter: {filepath}")
            
            # Verzeichnis erstellen falls nötig
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                Logger.info(f"Verzeichnis erstellt: {directory}")
            
            from utils.pdf_utils import generiere_pdf
            success = generiere_pdf(self.controller.charakter, filepath, self.temp_printer_friendly)
            
            if success:
                self._show_success("PDF erstellen erfolgreich", f"PDF wurde gespeichert als:\n{filepath}")
                # Letzten verwendeten Pfad speichern
                directory = os.path.dirname(filepath)
                self._save_last_used_directory('pdfs', directory)
                # Reset temp settings
                self.temp_pdf_filename = ""
                self.temp_printer_friendly = False
            else:
                self._show_error("Fehler beim Erstellen der PDF-Datei.")
        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der PDF: {str(e)}", exc_info=True)
            self._show_error(f"Fehler beim Erstellen der PDF: {str(e)}")
    
    def _request_overwrite_confirmation(self, filepath, callback):
        """Fragt nach Bestätigung zum Überschreiben"""
        # Hier würde normalerweise ein Dialog gezeigt werden
        # Für Einfachheit direkt überschreiben
        Logger.info(f"Datei existiert bereits, überschreibe: {filepath}")
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

    def set_temp_html_settings(self, filename, printer_friendly=False):
        """Setzt die temporären HTML-Einstellungen"""
        self.temp_html_filename = filename
        self.temp_html_printer_friendly = printer_friendly
        Logger.debug(f"Temp HTML settings gesetzt: {filename}, printer_friendly: {printer_friendly}")
    
    def clear_temp_settings(self):
        """Löscht alle temporären Einstellungen"""
        self.temp_filename = ""
        self.temp_pdf_filename = ""
        self.temp_printer_friendly = False
        Logger.debug("Temporäre Einstellungen gelöscht")