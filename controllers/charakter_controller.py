# -*- coding: utf-8 -*-
# controllers/charakter_controller.py
from kivy.app import App
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty
from kivy.logger import Logger
from charakter import Charakter
from models.talent import Talent
from models.macht import Macht
import logging
import traceback
import copy

class CharakterController(EventDispatcher):
    """
    Der CharakterController ist für die Steuerung und Aktualisierung
    des Charakterobjekts zuständig und kommuniziert mit der UI.
    
    Er dient als Vermittler zwischen der Benutzeroberfläche und dem Datenmodell
    und implementiert das Model-View-Controller-Muster.
    """
    charakter = ObjectProperty(None)  # Kivy-Property für den Charakter
    current_character_file_path = StringProperty(None)  # Pfad der aktuellen Charakterdatei

    def __init__(self, char_name="", alter="", geschlecht="", konzept="", sprachen="",
                 bennys="3", entschlossenheit="0", beschreibung="", hintergrund=""):
        super().__init__()  # EventDispatcher initialisieren

        # Registrieren von Events
        self.register_event_type('on_charakter_changed')
        self.register_event_type('on_charakter_updated')
        self.register_event_type('on_charakter_loaded')
        self.register_event_type('on_charakter_error')

        # Erzeuge den Charakter
        self.charakter = Charakter(
            char_name=char_name,
            alter=alter,
            geschlecht=geschlecht,
            konzept=konzept,
            sprachen=sprachen,
            bennys=bennys,
            entschlossenheit=entschlossenheit,
            beschreibung=beschreibung,
            hintergrund=hintergrund
        )

        # Charakter-Ereignisse mit Controller-Methoden verbinden
        self.charakter.bind(on_charakter_change=self.on_model_change)

        Logger.info("CharakterController initialisiert")

    # Event-Handler für Änderungen im Charakter-Modell
    def on_model_change(self, *args):
        """Wird aufgerufen, wenn sich das Charakter-Modell ändert"""
        Logger.debug("Modell-Änderung erkannt")
        try:
            # Event zur Benachrichtigung der UI auslösen
            self.dispatch('on_charakter_updated')
        except Exception as e:
            Logger.error(f"Fehler bei Verarbeitung von Modell-Änderung: {str(e)}")
            self.dispatch('on_charakter_error', f"UI-Update fehlgeschlagen: {str(e)}")

    # Ereignis-Handler (Platzhalter, werden von Verbrauchern überschrieben)
    def on_charakter_updated(self, *args):
        """Event-Handler für Aktualisierungen am Charakter"""
        pass

    def on_charakter_changed(self, *args):
        """Event-Handler für grundlegende Änderungen am Charakter"""
        pass

    def on_charakter_loaded(self, *args):
        """Event-Handler für das Laden eines neuen Charakters"""
        pass
    
    def on_charakter_error(self, error_msg):
        """Event-Handler für Fehler bei Charakteroperationen"""
        Logger.error(f"Charakterfehler: {error_msg}")
        pass

    # ============================
    # Operationen auf Attributen
    # ============================
    def steigere_attribut(self, attribut_name):
        """
        Steigert ein Attribut des Charakters
        
        Args:
            attribut_name (str): Name des Attributs
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            success = self.charakter.steigere_attribut(attribut_name)
            if success:
                self.charakter.berechne_abgeleitete_werte()
                self.dispatch('on_charakter_updated')
            return success
        except Exception as e:
            Logger.error(f"Fehler bei Steigerung von Attribut {attribut_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Attributsteigerung fehlgeschlagen: {str(e)}")
            return False

    def senke_attribut(self, attribut_name):
        """
        Senkt ein Attribut des Charakters
        
        Args:
            attribut_name (str): Name des Attributs
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            success = self.charakter.senke_attribut(attribut_name)
            if success:
                self.charakter.berechne_abgeleitete_werte()
                self.dispatch('on_charakter_updated')
            return success
        except Exception as e:
            Logger.error(f"Fehler bei Senkung von Attribut {attribut_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Attributsenkung fehlgeschlagen: {str(e)}")
            return False

    # ============================
    # Operationen auf Fertigkeiten
    # ============================
    def steigere_fertigkeit(self, fertigkeit_name, confirm_double_cost=False):
        """
        Steigert eine Fertigkeit des Charakters
        
        Args:
            fertigkeit_name (str): Name der Fertigkeit
            confirm_double_cost (bool): Ob die doppelten Kosten bestätigt wurden
            
        Returns:
            bool oder str: True bei Erfolg, False bei Fehler, "needs_confirmation" wenn Bestätigung erforderlich
        """
        try:
            success = self.charakter.steigere_fertigkeit(fertigkeit_name, confirm_double_cost)
            if success == "needs_confirmation":
                return "needs_confirmation"
            elif success:
                self.charakter.berechne_abgeleitete_werte()
                self.dispatch('on_charakter_updated')
            return success
        except Exception as e:
            Logger.error(f"Fehler bei Steigerung von Fertigkeit {fertigkeit_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Fertigkeitssteigerung fehlgeschlagen: {str(e)}")
            return False

    def senke_fertigkeit(self, fertigkeit_name):
        """
        Senkt eine Fertigkeit des Charakters
        
        Args:
            fertigkeit_name (str): Name der Fertigkeit
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            success = self.charakter.senke_fertigkeit(fertigkeit_name)
            if success:
                self.charakter.berechne_abgeleitete_werte()
                self.dispatch('on_charakter_updated')
            return success
        except Exception as e:
            Logger.error(f"Fehler bei Senkung von Fertigkeit {fertigkeit_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Fertigkeitssenkung fehlgeschlagen: {str(e)}")
            return False

    # ============================
    # Operationen auf Handicaps
    # ============================
    def waehle_handicap(self, handicap_name):
        """
        Wählt ein Handicap für den Charakter aus
        
        Args:
            handicap_name (str): Name des Handicaps
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            success = self.charakter.waehle_handicap(handicap_name)
            if success:
                self.dispatch('on_charakter_updated')
            return success
        except Exception as e:
            Logger.error(f"Fehler bei Auswahl von Handicap {handicap_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Handicap-Auswahl fehlgeschlagen: {str(e)}")
            return False

    def entferne_handicap(self, handicap_name):
        """
        Entfernt ein Handicap vom Charakter
        
        Args:
            handicap_name (str): Name des Handicaps
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            success = self.charakter.entferne_handicap(handicap_name)
            if success:
                self.dispatch('on_charakter_updated')
            return success
        except Exception as e:
            Logger.error(f"Fehler bei Entfernung von Handicap {handicap_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Handicap-Entfernung fehlgeschlagen: {str(e)}")
            return False

    def aktive_handicaps(self):
        """
        Gibt alle aktiven Handicaps des Charakters zurück
        
        Returns:
            list: Liste der aktiven Handicaps
        """
        return self.charakter.aktive_handicaps()

    def ausgewaehlte_handicaps(self):
        """
        Gibt alle ausgewählten Handicaps des Charakters zurück
        
        Returns:
            list: Liste der ausgewählten Handicaps
        """
        return self.charakter.ausgewaehlte_handicaps()

    # ============================
    # Operationen auf Talenten
    # ============================
    def waehle_talent(self, talent_name, ignore_rang_check=False):
        """
        Wählt ein Talent für den Charakter aus
        
        Args:
            talent_name (str): Name des Talents
            ignore_rang_check (bool): Flag zum Ignorieren der Rangprüfung (für UI-Bestätigung)
            
        Returns:
            bool oder str: "needs_rang_confirmation" wenn Rang-Bestätigung benötigt wird,
                        True bei Erfolg, False bei Fehler
        """
        try:
            result = self.charakter.waehle_talent(talent_name, ignore_rang_check=ignore_rang_check)
            if result is True:  # Nur bei True-Wert, nicht bei "needs_rang_confirmation"
                self.dispatch('on_charakter_updated')
            return result
        except Exception as e:
            Logger.error(f"Fehler bei Auswahl von Talent {talent_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Talent-Auswahl fehlgeschlagen: {str(e)}")
            return False

    def entferne_talent(self, talent_name):
        """
        Entfernt ein Talent vom Charakter
        
        Args:
            talent_name (str): Name des Talents
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            success = self.charakter.entferne_talent(talent_name)
            if success:
                self.dispatch('on_charakter_updated')
            return success
        except Exception as e:
            Logger.error(f"Fehler bei Entfernung von Talent {talent_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Talent-Entfernung fehlgeschlagen: {str(e)}")
            return False

    def aktive_talente(self):
        """
        Gibt alle aktiven Talente des Charakters zurück
        
        Returns:
            list: Liste der aktiven Talente
        """
        return self.charakter.aktive_talente()

    def ausgewaehlte_talente(self):
        """
        Gibt alle ausgewählten Talente des Charakters zurück
        
        Returns:
            list: Liste der ausgewählten Talente
        """
        return self.charakter.ausgewaehlte_talente()

    # ============================
    # Operationen auf Mächten
    # ============================
    def waehle_macht(self, macht_name, ignore_rang_check=False):
        """
        Wählt eine Macht für den Charakter aus
        
        Args:
            macht_name (str): Name der Macht
            ignore_rang_check (bool): Flag zum Ignorieren der Rangprüfung (für UI-Bestätigung)
            
        Returns:
            bool oder str: "needs_rang_confirmation" wenn Rang-Bestätigung benötigt wird,
                        True bei Erfolg, False bei Fehler
        """
        try:
            result = self.charakter.waehle_macht(macht_name, ignore_rang_check=ignore_rang_check)
            if result is True:  # Nur bei True-Wert, nicht bei "needs_rang_confirmation"
                self.dispatch('on_charakter_updated')
            return result
        except Exception as e:
            Logger.error(f"Fehler bei Auswahl von Macht {macht_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Macht-Auswahl fehlgeschlagen: {str(e)}")
            return False

    def entferne_macht(self, macht_name):
        """
        Entfernt eine Macht vom Charakter
        
        Args:
            macht_name (str): Name der Macht
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            success = self.charakter.entferne_macht(macht_name)
            if success:
                self.dispatch('on_charakter_updated')
            return success
        except Exception as e:
            Logger.error(f"Fehler bei Entfernung von Macht {macht_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Macht-Entfernung fehlgeschlagen: {str(e)}")
            return False

    def aktive_maechte(self):
        """
        Gibt alle aktiven Mächte des Charakters zurück
        
        Returns:
            list: Liste der aktiven Mächte
        """
        return self.charakter.aktive_maechte()

    def ausgewaehlte_maechte(self):
        """
        Gibt alle ausgewählten Mächte des Charakters zurück
        
        Returns:
            list: Liste der ausgewählten Mächte
        """
        return self.charakter.ausgewaehlte_maechte()

    # ============================
    # Operationen auf Ausrüstung
    # ============================
    def kaufen_ausruestung(self, item_name, anzahl=1, preis_pro_stueck=None):
        """
        Kauft einen Ausrüstungsgegenstand für den Charakter
        
        Args:
            item_name (str): Name des Gegenstands
            anzahl (int): Anzahl der zu kaufenden Gegenstände
            preis_pro_stueck (float): Preis pro Stück (optional)
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            # Prüfen, ob der Gegenstand existiert
            if item_name in self.charakter.ausruestung:
                item = self.charakter.ausruestung[item_name]
            else:
                Logger.warning(f"Ausrüstungsgegenstand '{item_name}' nicht gefunden.")
                return False

            success = self.charakter.kaufen(item, anzahl=anzahl, preis_pro_stueck=preis_pro_stueck)
            if success:
                Logger.debug(f"Ausrüstung '{item.name}' gekauft.")
                self.dispatch('on_charakter_updated')
            return success
        except Exception as e:
            Logger.error(f"Fehler beim Kauf von Ausrüstung {item_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Ausrüstungskauf fehlgeschlagen: {str(e)}")
            return False

    def verkaufen_ausruestung(self, item_name, anzahl=1, preis_pro_stueck=None):
        """
        Verkauft einen Ausrüstungsgegenstand des Charakters
        
        Args:
            item_name (str): Name des Gegenstands
            anzahl (int): Anzahl der zu verkaufenden Gegenstände
            preis_pro_stueck (float): Preis pro Stück (optional)
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            # Prüfen, ob der Gegenstand existiert
            if item_name in self.charakter.ausruestung:
                item = self.charakter.ausruestung[item_name]
            else:
                Logger.warning(f"Ausrüstungsgegenstand '{item_name}' nicht gefunden.")
                return False

            erfolg = self.charakter.verkaufen(item, anzahl, preis_pro_stueck)
            if erfolg:
                Logger.debug(f"Ausrüstung '{item.name}' verkauft.")
                self.dispatch('on_charakter_updated')
            return erfolg
        except Exception as e:
            Logger.error(f"Fehler beim Verkauf von Ausrüstung {item_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Ausrüstungsverkauf fehlgeschlagen: {str(e)}")
            return False

    # ============================
    # Lade- und Speicherfunktionen
    # ============================
# Folgende Methoden für CharakterController überprüfen und bei Bedarf anpassen

# In controllers/charakter_controller.py

# Überprüfe, ob diese Methode korrekt implementiert ist
    def lade_charakter_von_json(self, dateipfad):
        """
        Lädt einen Charakter aus einer JSON-Datei
        
        Args:
            dateipfad (str): Pfad zur JSON-Datei
                
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            # Sichern des aktuellen Charakters (falls das Laden fehlschlägt)
            original_charakter = None
            try:
                import copy
                original_charakter = copy.deepcopy(self.charakter)
            except Exception as backup_error:
                Logger.warning(f"Konnte keine Backup-Kopie erstellen: {str(backup_error)}")
            
            # Charakter laden
            success = self.charakter.laden_von_json(dateipfad)
            
            if success:
                self.current_character_file_path = dateipfad
                Logger.info(f"Charakter erfolgreich aus {dateipfad} geladen.")
                
                # Events auslösen zur Aktualisierung der UI
                self.dispatch('on_charakter_changed', self.charakter)
                self.dispatch('on_charakter_loaded')
                self.dispatch('on_charakter_updated')
                
                return True
            else:
                # Bei Fehler: Ursprünglichen Charakter wiederherstellen
                if original_charakter:
                    self.charakter = original_charakter
                    Logger.warning("Charakter konnte nicht geladen werden. Ursprünglicher Charakter wiederhergestellt.")
                self.dispatch('on_charakter_error', "Fehler beim Laden des Charakters")
                return False
                
        except Exception as e:
            Logger.error(f"Fehler beim Laden des Charakters: {str(e)}", exc_info=True)
            # Bei Fehler: Ursprünglichen Charakter wiederherstellen
            if original_charakter:
                self.charakter = original_charakter
                Logger.warning("Charakter konnte nicht geladen werden. Ursprünglicher Charakter wiederhergestellt.")
            self.dispatch('on_charakter_error', f"Kritischer Fehler beim Laden: {str(e)}")
            return False

    def speichere_charakter_als_json(self, dateipfad):
        """
        Speichert den Charakter in einer JSON-Datei
        
        Args:
            dateipfad (str): Pfad zur Zieldatei
                
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            # Charakter speichern
            success = self.charakter.speichern_als_json(dateipfad)
            if success:
                self.current_character_file_path = dateipfad
                Logger.info(f"Charakter erfolgreich in {dateipfad} gespeichert.")
                self.dispatch('on_charakter_updated')
                return True
            else:
                self.dispatch('on_charakter_error', "Fehler beim Speichern des Charakters")
                return False
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Charakters: {str(e)}", exc_info=True)
            self.dispatch('on_charakter_error', f"Fehler beim Speichern: {str(e)}")
            return False

    def neuer_charakter(self, char_name="", setting_name=None):
        """
        Erstellt einen neuen Charakter
        
        Args:
            char_name (str): Name des neuen Charakters
            setting_name (str): Name des zu verwendenden Settings (optional)
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            # Backup des alten Charakters für Notfall-Wiederherstellung
            alter_charakter = self.charakter
            
            # Neuen Charakter erstellen
            self.charakter = Charakter(char_name=char_name, active_setting_name=setting_name)
            self.current_character_file_path = None  # Zurücksetzen des Dateipfads
            
            # UI-Updates auslösen
            self.dispatch('on_charakter_changed', self.charakter)
            Logger.info(f"Neuer Charakter '{char_name}' mit Setting '{setting_name}' erstellt.")
            return True
        except Exception as e:
            # Wiederherstellung des alten Charakters bei Fehler
            self.charakter = alter_charakter
            Logger.error(f"Fehler beim Erstellen eines neuen Charakters: {str(e)}", exc_info=True)
            self.dispatch('on_charakter_error', f"Fehler beim Erstellen des Charakters: {str(e)}")
            return False

    # ============================
    # UI-Update-Methoden
    # ============================
    def update_ui(self):
        """
        Aktualisiert alle relevanten UI-Komponenten
        Diese Methode löst keine Fehler aus, wenn UI-Komponenten nicht verfügbar sind
        """
        # Löse Events aus, die von UI-Widgets abgefangen werden können
        self.dispatch('on_charakter_updated')