# controllers/einstellungen_controller.py
"""
Controller für Einstellungen-Verwaltung
Trennt Business Logic von der UI
"""

from kivy.logger import Logger
from kivy.app import App
from kivy.clock import Clock


class EinstellungenController:
    """Controller für Einstellungen-Management"""
    
    def __init__(self, charakter_controller):
        self.charakter_controller = charakter_controller
        self.app = App.get_running_app()
        
        # Einstellungen-Daten
        self.vermoegen_input = "500"
        self.waehrung_input = "Gold"
        self.maximale_attributsteigerungen_input = "5"
        self.maximale_fertigkeitssteigerungen_input = "12"
        self.fehler_meldung = ""
        
        self._initialize_values()
    
    def _initialize_values(self):
        """Initialisiert die Werte basierend auf dem aktuellen Charakter"""
        if self.charakter_controller and self.charakter_controller.charakter:
            char = self.charakter_controller.charakter
            self.vermoegen_input = str(char.vermoegen)
            self.waehrung_input = char.waehrungseinheit
            self.maximale_attributsteigerungen_input = str(char.maximale_attributsteigerungen)
            self.maximale_fertigkeitssteigerungen_input = str(char.maximale_fertigkeitssteigerungen)
    
    # Charakter-Verwaltung
    def create_new_character(self, character_name):
        """
        Erstellt einen neuen Charakter
        
        Args:
            character_name (str): Name des neuen Charakters
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            if not character_name.strip():
                raise ValueError("Charaktername darf nicht leer sein")
            
            # Aktives Setting ermitteln
            active_setting = self.charakter_controller.charakter.active_setting_name
            
            # Neuen Charakter erstellen
            success = self.charakter_controller.neuer_charakter(character_name, active_setting)
            
            if success:
                # Profildaten aktualisieren
                self.charakter_controller.charakter.profil_daten["Name"] = character_name
                
                # Elemente aus Setting laden
                self.charakter_controller.charakter.load_elements_from_active_setting()
                
                # Werte aktualisieren
                self._initialize_values()
                
                Logger.info(f"Neuer Charakter '{character_name}' erstellt")
                return True
            
            return False
            
        except Exception as e:
            Logger.error(f"Fehler beim Erstellen des Charakters: {str(e)}", exc_info=True)
            return False
    
    def save_character(self, filepath):
        """
        Speichert den aktuellen Charakter
        
        Args:
            filepath (str): Pfad für die Speicherung
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            return self.charakter_controller.speichere_charakter_als_json(filepath)
        except Exception as e:
            Logger.error(f"Fehler beim Speichern: {str(e)}", exc_info=True)
            return False
    
    def load_character(self, filepath):
        """
        Lädt einen Charakter
        
        Args:
            filepath (str): Pfad zur Charakterdatei
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            success = self.charakter_controller.lade_charakter_von_json(filepath)
            if success:
                self._initialize_values()
            return success
        except Exception as e:
            Logger.error(f"Fehler beim Laden: {str(e)}", exc_info=True)
            return False
    
    # Charakterwerte-Verwaltung
    def update_vermoegen(self):
        """Aktualisiert das Vermögen"""
        try:
            neues_vermoegen = int(self.vermoegen_input)
            if neues_vermoegen < 0:
                raise ValueError("Vermögen darf nicht negativ sein")
            
            self.charakter_controller.charakter.vermoegen = neues_vermoegen
            self.fehler_meldung = ""
            return True
            
        except ValueError as e:
            self.fehler_meldung = f"Ungültiges Vermögen: {str(e)}"
            Logger.error(self.fehler_meldung)
            return False
    
    def update_waehrung(self):
        """Aktualisiert die Währungseinheit"""
        try:
            waehrung = self.waehrung_input.strip()
            if not waehrung:
                raise ValueError("Währung darf nicht leer sein")
            
            self.charakter_controller.charakter.waehrungseinheit = waehrung
            self.fehler_meldung = ""
            return True
            
        except ValueError as e:
            self.fehler_meldung = f"Ungültige Währung: {str(e)}"
            Logger.error(self.fehler_meldung)
            return False
    
    def update_maximale_attributsteigerungen(self):
        """Aktualisiert die maximalen Attributsteigerungen"""
        try:
            neue_max = int(self.maximale_attributsteigerungen_input)
            if neue_max < 0:
                raise ValueError("Attributsteigerungen dürfen nicht negativ sein")
            
            char = self.charakter_controller.charakter
            char.maximale_attributsteigerungen = neue_max
            char.verbleibende_attributsteigerungen = neue_max
            self.fehler_meldung = ""
            return True
            
        except ValueError as e:
            self.fehler_meldung = f"Ungültige Attributsteigerungen: {str(e)}"
            Logger.error(self.fehler_meldung)
            return False
    
    def update_maximale_fertigkeitssteigerungen(self):
        """Aktualisiert die maximalen Fertigkeitssteigerungen"""
        try:
            neue_max = int(self.maximale_fertigkeitssteigerungen_input)
            if neue_max < 0:
                raise ValueError("Fertigkeitssteigerungen dürfen nicht negativ sein")
            
            char = self.charakter_controller.charakter
            char.maximale_fertigkeitssteigerungen = neue_max
            char.verbleibende_fertigkeitssteigerungen = neue_max
            self.fehler_meldung = ""
            return True
            
        except ValueError as e:
            self.fehler_meldung = f"Ungültige Fertigkeitssteigerungen: {str(e)}"
            Logger.error(self.fehler_meldung)
            return False
    
    # Charakter-Operationen
    def erhoehe_aufstieg(self):
        """Erhöht die Aufstiege des Charakters"""
        try:
            self.charakter_controller.charakter.increase_aufstiege()
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Erhöhen der Aufstiege: {str(e)}")
            return False
    
    def senke_aufstieg(self):
        """Senkt die Aufstiege des Charakters"""
        try:
            self.charakter_controller.charakter.decrease_aufstiege()
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Senken der Aufstiege: {str(e)}")
            return False
    
    def erhoehe_startkapital(self):
        """Erhöht das Startkapital mit Handicap-Punkten"""
        try:
            self.charakter_controller.charakter.erhoehe_startkapital()
            self.vermoegen_input = str(self.charakter_controller.charakter.vermoegen)
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Erhöhen des Startkapitals: {str(e)}")
            return False
    
    # Setting-Verwaltung
    def change_active_setting(self, setting_name):
        """
        Wechselt das aktive Setting
        
        Args:
            setting_name (str): Name des neuen Settings
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            if self.charakter_controller and self.charakter_controller.charakter:
                char = self.charakter_controller.charakter
                success = char.custom_element_manager.set_active_setting(setting_name)
                
                if success:
                    char.load_elements_from_active_setting()
                    Logger.info(f"Setting gewechselt zu: {setting_name}")
                    return True
                else:
                    self.fehler_meldung = f"Setting '{setting_name}' konnte nicht geladen werden"
                    return False
            
            return False
            
        except Exception as e:
            self.fehler_meldung = f"Fehler beim Setting-Wechsel: {str(e)}"
            Logger.error(self.fehler_meldung, exc_info=True)
            return False
    
    def get_all_settings(self):
        """
        Gibt alle verfügbaren Settings zurück
        
        Returns:
            list: Liste der verfügbaren Settings
        """
        try:
            if self.charakter_controller and self.charakter_controller.charakter:
                return self.charakter_controller.charakter.custom_element_manager.get_all_settings()
            return []
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Settings: {str(e)}")
            return []
    
    # UI-Update-Methoden
    def update_ui(self):
        """Löst UI-Updates aus"""
        try:
            if self.app and hasattr(self.app, 'refresh_current_tab'):
                self.app.refresh_current_tab()
            
            # Alternative: Spezifische UI-Updates
            Clock.schedule_once(self._delayed_ui_update, 0.1)
            
        except Exception as e:
            Logger.error(f"Fehler beim UI-Update: {str(e)}")
    
    def _delayed_ui_update(self, dt):
        """Verzögertes UI-Update"""
        try:
            if self.app and hasattr(self.app, 'get_widget_by_tab_text'):
                # Eigenschaften-Tab aktualisieren
                eigenschaften_widget = self.app.get_widget_by_tab_text('Eigenschaften', 'eigenschaften_widget')
                if eigenschaften_widget:
                    eigenschaften_widget.update_eigenschaften()
                
                # Weitere Widgets bei Bedarf...
                
        except Exception as e:
            Logger.error(f"Fehler beim verzögerten UI-Update: {str(e)}")
    
    # Getter-Methoden
    def get_character_info(self):
        """
        Gibt Informationen über den aktuellen Charakter zurück
        
        Returns:
            dict: Charakter-Informationen
        """
        if self.charakter_controller and self.charakter_controller.charakter:
            char = self.charakter_controller.charakter
            return {
                'name': char.char_name,
                'vermoegen': char.vermoegen,
                'waehrung': char.waehrungseinheit,
                'aufstiege': char.aufstiege_gesamt,
                'rang': char.rang,
                'setting': char.active_setting_name
            }
        return {}
    
    def has_unsaved_changes(self):
        """
        Prüft, ob ungespeicherte Änderungen vorliegen
        
        Returns:
            bool: True wenn ungespeicherte Änderungen vorhanden
        """
        # Hier könnte eine Logik implementiert werden, die prüft
        # ob Änderungen seit dem letzten Speichern vorgenommen wurden
        return False
    
    def get_current_file_path(self):
        """
        Gibt den aktuellen Dateipfad zurück
        
        Returns:
            str: Dateipfad oder None
        """
        if hasattr(self.charakter_controller, 'current_character_file_path'):
            return self.charakter_controller.current_character_file_path
        return None