#charakter_persistence.py
"""
Persistenz-Funktionalität für die Charakter-Klasse.
Behandelt das Speichern und Laden von Charakterdaten.
"""
import json
from pathlib import Path
from kivy.logger import Logger
import functions.charakter_speicher as charakter_speicher

class CharakterPersistence:
    """Mixin-Klasse für Speichern/Laden Funktionalität"""
    
    def speichern_als_json(self, dateipfad):
        """
        Speichert den Charakter als JSON-Datei.
        
        Args:
            dateipfad (str): Der Pfad zur Zieldatei
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            charakter_speicher.speichern_als_json(self, dateipfad)
            Logger.info(f"Charakter erfolgreich in {dateipfad} gespeichert.")
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Charakters: {e}")
            return False

    def laden_von_json(self, dateipfad):
        """
        Lädt einen Charakter aus einer JSON-Datei.
        
        Args:
            dateipfad (str): Der Pfad zur JSON-Datei
            
        Returns:
            bool: True, wenn das Laden erfolgreich war, sonst False
        """
        try:
            with open(dateipfad, 'r', encoding='utf-8') as f:
                daten = json.load(f)
            
            # Wichtige Informationen vorübergehend speichern
            altes_setting = self.active_setting_name
            
            # Backup der aktiven Ausrüstung erstellen
            temp_ausruestung = {}
            for name, item in self.ausruestung.items():
                temp_ausruestung[name] = item
            
            # Backup der ausgewählten Ausrüstung
            temp_selected_waffen = list(self.selected_waffen)
            temp_selected_ruestungen = list(self.selected_ruestungen)
            temp_selected_schilde = list(self.selected_schilde)
            temp_selected_allgemeine_ausruestung = list(self.selected_allgemeine_ausruestung)
            
            # Alle Daten aus der JSON in dieses Charakterobjekt laden
            charakter_speicher.from_dict(self, daten)
            Logger.info(f"Charakter erfolgreich von {dateipfad} geladen.")
            
            # Setting-Verwaltung nach dem Laden
            if "voelker" in daten and "handicaps" in daten and "talente" in daten and "maechte" in daten:
                Logger.info("Ausrüstung aus der gespeicherten Datei verwenden, nicht aus dem Setting")
                
                # Speichere das geladene Setting als letztes Setting in der Config (auch bei gleichem Setting)
                self._save_last_setting_to_config(self.active_setting_name)
                
                if self.active_setting_name != altes_setting:
                    if not self.custom_element_manager.set_active_setting(self.active_setting_name):
                        Logger.warning(f"Das Setting '{self.active_setting_name}' konnte nicht aktiviert werden.")
                        # Fallback auf Standard-Setting
                        if "SWAE" in self.custom_element_manager.get_all_settings():
                            Logger.warning("Wechsle zurück zum Standard-Setting 'SWAE'.")
                            self.active_setting_name = "SWAE"
                            self.custom_element_manager.set_active_setting(self.active_setting_name)
                            # Speichere das Fallback-Setting in der Config
                            self._save_last_setting_to_config("SWAE")
                        else:
                            # Standard-Setting erstellen, wenn es nicht existiert
                            Logger.warning("Standard-Setting 'SWAE' nicht gefunden. Erstelle es neu.")
                            default_setting = self.create_default_setting()
                            self.custom_element_manager.add_setting("SWAE", default_setting, overwrite=True)
                            self.active_setting_name = "SWAE"
                            self.custom_element_manager.set_active_setting("SWAE")
                            # Speichere das neu erstellte Standard-Setting in der Config
                            self._save_last_setting_to_config("SWAE")
                    else:
                        # Setting wurde erfolgreich aktiviert, speichere es in der Config
                        self._save_last_setting_to_config(self.active_setting_name)
            else:
                Logger.warning("Unvollständige Charakterdaten, lade Elemente aus dem aktiven Setting")
                if "ausruestung" in daten:
                    # Ausrüstung aus den Daten wiederherstellen
                    self.ausruestung = temp_ausruestung
                    self.selected_waffen = temp_selected_waffen
                    self.selected_ruestungen = temp_selected_ruestungen
                    self.selected_schilde = temp_selected_schilde
                    self.selected_allgemeine_ausruestung = temp_selected_allgemeine_ausruestung
                
                # Aktiviere das Setting mit Merging, ohne die Ausrüstung zu laden
                self.load_elements_from_active_setting(skip_equipment=True, merge_elements=True)
            
            # Abgeleitete Werte berechnen
            self.berechne_abgeleitete_werte()
            
            # UI aktualisieren
            self.dispatch('on_charakter_change')
            
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Laden des Charakters: {e}", exc_info=True)
            return False

    def to_dict(self):
        """
        Konvertiert diesen Charakter in ein Dictionary.
        
        Returns:
            dict: Dictionary mit den Charakterdaten
        """
        return charakter_speicher.to_dict(self)

    def from_dict(self, data):
        """
        Lädt Daten aus einem Dictionary in diesen Charakter.
        
        Args:
            data (dict): Dictionary mit Charakterdaten
        """
        charakter_speicher.from_dict(self, data)

    def reload_character_data(self):
        """Aktualisiert den Charakter, um nach dem Laden eines neuen Settings alle Elemente korrekt zu laden."""
        data = self.to_dict()
        self.from_dict(data)