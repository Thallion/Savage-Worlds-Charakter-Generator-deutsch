# -*- coding: utf-8 -*-
# controllers/charakter_controller.py
from kivy.app import App
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty
from kivy.logger import Logger
from models.charakter import Charakter
from models.talent import Talent
from models.macht import Macht
import logging
import traceback
import copy

# Einfacher Filter für FocusBehavior-Warnungen
class WarningFilter(logging.Filter):
    def filter(self, record):
        if (record.levelno == logging.WARNING and 
            'FocusBehavior' in str(record.getMessage()) and
            'deprecated' in str(record.getMessage())):
            return False
        return True

# Filter anwenden
logging.getLogger().addFilter(WarningFilter())

class CharakterController(EventDispatcher):
    """
    Der CharakterController ist für die Steuerung und Aktualisierung
    des Charakterobjekts zuständig und kommuniziert mit der UI.
    
    Er dient als Vermittler zwischen der Benutzeroberfläche und dem Datenmodell
    und implementiert das Model-View-Controller-Muster.
    """
    charakter = ObjectProperty(None)  # Kivy-Property für den Charakter
    current_character_file_path = StringProperty(None, allownone=True)  # Pfad der aktuellen Charakterdatei - erlaubt None

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
            # Alte Werte und verfügbare Punkte für Historie merken
            old_value = getattr(self.charakter.attribute.get(attribut_name), 'wuerfel', None)
            old_value = old_value.value if old_value else 4
            
            # Merke verfügbare Punkte vor der Steigerung
            old_attr_punkte = self.charakter.verbleibende_attributsteigerungen
            old_handicap_punkte = self.charakter.verbleibende_handicap_punkte
            old_aufstiege = self.charakter.verbleibende_aufstiege
            
            success = self.charakter.steigere_attribut(attribut_name)
            if success:
                # Neue Werte abrufen
                new_value = getattr(self.charakter.attribute.get(attribut_name), 'wuerfel', None)
                new_value = new_value.value if new_value else 4
                
                # Ermittle welche Punkte verwendet wurden
                new_attr_punkte = self.charakter.verbleibende_attributsteigerungen
                new_handicap_punkte = self.charakter.verbleibende_handicap_punkte
                new_aufstiege = self.charakter.verbleibende_aufstiege
                
                cost = 1  # Standard-Kosten
                cost_type = "Attributspunkte"
                
                if self.charakter.char_gen_completed:
                    # Im Spiel: Aufstiege verwendet
                    cost = old_aufstiege - new_aufstiege
                    cost_type = "Aufstiege"
                else:
                    # Charaktergenerierung: Prüfe welche Punkte verwendet wurden
                    if old_attr_punkte > new_attr_punkte:
                        cost = old_attr_punkte - new_attr_punkte
                        cost_type = "Attributspunkte"
                    elif old_handicap_punkte > new_handicap_punkte:
                        cost = old_handicap_punkte - new_handicap_punkte
                        cost_type = "Handicap-Punkte"
                
                self.charakter.berechne_abgeleitete_werte()
                self.dispatch('on_charakter_updated')
                
                # Event für Historie-System senden
                from services.service_container import service_container
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish('attribute_changed', {
                        'attribute_name': attribut_name,
                        'old_value': old_value,
                        'new_value': new_value,
                        'cost': cost,
                        'cost_type': cost_type
                    })
                
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
            # Alte Werte und verfügbare Punkte für Historie merken
            fertigkeit = self.charakter.fertigkeiten.get(fertigkeit_name)
            old_value = fertigkeit.wuerfel.value if fertigkeit else 0
            
            # Merke verfügbare Punkte vor der Steigerung
            old_skill_punkte = self.charakter.verbleibende_fertigkeitssteigerungen
            old_handicap_punkte = self.charakter.verbleibende_handicap_punkte
            old_aufstiege = self.charakter.verbleibende_aufstiege
            
            success = self.charakter.steigere_fertigkeit(fertigkeit_name, confirm_double_cost)
            if success == "needs_confirmation":
                return "needs_confirmation"
            elif success:
                # Neue Werte abrufen
                fertigkeit = self.charakter.fertigkeiten.get(fertigkeit_name)
                new_value = fertigkeit.wuerfel.value if fertigkeit else 0
                
                # Ermittle welche Punkte verwendet wurden
                new_skill_punkte = self.charakter.verbleibende_fertigkeitssteigerungen
                new_handicap_punkte = self.charakter.verbleibende_handicap_punkte
                new_aufstiege = self.charakter.verbleibende_aufstiege
                
                cost = 1  # Standard-Kosten
                cost_type = "Fertigkeitspunkte"
                
                if self.charakter.char_gen_completed:
                    # Im Spiel: Aufstiege verwendet
                    cost = old_aufstiege - new_aufstiege
                    cost_type = "Aufstiege"
                else:
                    # Charaktergenerierung: Prüfe welche Punkte verwendet wurden
                    if old_skill_punkte > new_skill_punkte:
                        cost = old_skill_punkte - new_skill_punkte
                        cost_type = "Fertigkeitspunkte"
                    elif old_handicap_punkte > new_handicap_punkte:
                        cost = old_handicap_punkte - new_handicap_punkte
                        cost_type = "Handicap-Punkte"
                
                self.charakter.berechne_abgeleitete_werte()
                self.dispatch('on_charakter_updated')
                
                # Event für Historie-System senden
                from services.service_container import service_container
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish('skill_changed', {
                        'skill_name': fertigkeit_name,
                        'old_value': old_value,
                        'new_value': new_value,
                        'cost': cost,
                        'cost_type': cost_type
                    })
                
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
                
                # Event für Historie-System senden
                from services.service_container import service_container
                event_service = service_container.get_event_service()
                if event_service:
                    # Handicap-Stufe und Punkte aus dem Charakter-Objekt bestimmen
                    handicap = self.charakter.handicaps.get(handicap_name)
                    if handicap:
                        Logger.info(f"Publishing handicap_added event for {handicap_name}")
                        event_service.publish('handicap_added', {
                            'handicap_name': handicap_name,
                            'stufe': handicap.stufe,
                            'points': handicap.punkte
                        })
                    else:
                        Logger.warning(f"Handicap {handicap_name} nicht im Charakter gefunden")
                else:
                    Logger.error("Event-Service nicht verfügbar für Handicap-Event")
                
            return success
        except Exception as e:
            Logger.error(f"Fehler bei Auswahl von Handicap {handicap_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Handicap-Auswahl fehlgeschlagen: {str(e)}")
            return False

    def entferne_handicap(self, handicap_name, force_remove=False):
        """
        Entfernt ein Handicap vom Charakter.
        Nach der Charaktergenerierung kostet dies Aufstiege.
        
        Args:
            handicap_name (str): Name des Handicaps
            force_remove (bool): Wenn True, wird direkt entfernt ohne Dialog-Option
            
        Returns:
            bool oder str: True bei Erfolg, False bei Fehler, 
                        "needs_advancement_X" wenn X Aufstiege benötigt werden,
                        "can_reduce" wenn Reduzierung möglich ist,
                        "has_both_options" wenn beide Optionen verfügbar sind
        """
        try:
            success = self.charakter.entferne_handicap(handicap_name, force_remove)
            if isinstance(success, str) and (success.startswith("needs_advancement_") or success == "can_reduce" or success == "has_both_options"):
                return success
            elif success:
                self.dispatch('on_charakter_updated')
                
                # Event für Historie-System senden (Handicap entfernt)
                from services.service_container import service_container
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish('handicap_removed', {
                        'handicap_name': handicap_name,
                        'action': 'removed'
                    })
                
            return success
        except Exception as e:
            Logger.error(f"Fehler bei Entfernung von Handicap {handicap_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Handicap-Entfernung fehlgeschlagen: {str(e)}")
            return False
        
    def reduziere_handicap(self, handicap_name):
        """
        Reduziert ein schweres Handicap zu einem leichten Handicap.
        
        Args:
            handicap_name (str): Name des schweren Handicaps
            
        Returns:
            bool oder str: True bei Erfolg, False bei Fehler,
                          "needs_advancement" wenn Aufstieg fehlt
        """
        try:
            success = self.charakter.reduziere_handicap(handicap_name)
            if success == "needs_advancement":
                return "needs_advancement"
            elif success:
                self.dispatch('on_charakter_updated')
                
                # Event für Historie-System senden (Handicap reduziert)
                from services.service_container import service_container
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish('handicap_reduced', {
                        'handicap_name': handicap_name,
                        'action': 'reduced'
                    })
                
            return success
        except Exception as e:
            Logger.error(f"Fehler bei Reduzierung von Handicap {handicap_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Handicap-Reduzierung fehlgeschlagen: {str(e)}")
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

    def waehle_talent(self, talent_name, ignore_rang_check=False, ignore_voraussetzungen=False):
        """
        Wählt ein Talent für den Charakter aus
        
        Args:
            talent_name (str): Name des Talents
            ignore_rang_check (bool): Flag zum Ignorieren der Rangprüfung
            ignore_voraussetzungen (bool): Flag zum Ignorieren der Voraussetzungen
            
        Returns:
            bool oder str: Ergebniscode oder Erfolgsstatus
        """
        try:
            # Flag nur setzen, wenn es angefordert wurde
            if ignore_voraussetzungen:
                self.charakter.ignore_voraussetzungen = True
                Logger.debug(f"Controller: Flag ignore_voraussetzungen gesetzt für '{talent_name}'")
                
            # Parameter weitergeben
            result = self.charakter.waehle_talent(talent_name, ignore_rang_check=ignore_rang_check)
            
            if result is True:
                self.dispatch('on_charakter_updated')
                
                # Event für Historie-System senden
                from services.service_container import service_container
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish('talent_added', {
                        'talent_name': talent_name,
                        'cost': 1,
                        'requirements': ''
                    })
                
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
                
                # Event für Historie-System senden (Talent entfernt)
                from services.service_container import service_container
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish('talent_removed', {
                        'talent_name': talent_name,
                        'action': 'removed'
                    })
                
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
                
                # Event für Historie-System senden
                from services.service_container import service_container
                event_service = service_container.get_event_service()
                if event_service:
                    # Macht-Rang aus dem Charakter-Objekt bestimmen
                    macht = self.charakter.maechte.get(macht_name)
                    if macht:
                        event_service.publish('macht_added', {
                            'macht_name': macht_name,
                            'rang': macht.rang,
                            'cost': 1
                        })
                    else:
                        Logger.warning(f"Macht {macht_name} nicht im Charakter gefunden")
                
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
                
                # Event für Historie-System senden (Macht entfernt)
                from services.service_container import service_container
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish('macht_removed', {
                        'macht_name': macht_name,
                        'action': 'removed'
                    })
                
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
            self.current_character_file_path = None  # Zurücksetzen des Dateipfads (jetzt erlaubt)
            
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


    # Pathfinder Methoden

    def waehle_pathfinder_kostenloses_talent(self, talent_name, ignore_voraussetzungen=False):
        """
        NEU: Wählt ein Klassen-, Hintergrund- oder Experte-Talent in Savage Pathfinder kostenlos aus.
        
        Args:
            talent_name (str): Name des Talents
            ignore_voraussetzungen (bool): Flag zum Ignorieren der Voraussetzungen
            
        Returns:
            bool oder str: True bei Erfolg, False bei Fehler, oder Fehlercodes
        """
        try:
            result = self.charakter.waehle_pathfinder_kostenloses_talent(talent_name, ignore_voraussetzungen)
            
            if result is True:
                self.dispatch('on_charakter_updated')
                Logger.info(f"Kostenloses Pathfinder-Talent '{talent_name}' erfolgreich ausgewählt")
            
            return result
        except Exception as e:
            Logger.error(f"Fehler bei kostenloser Pathfinder-Talent-Auswahl {talent_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Pathfinder-Talent-Auswahl fehlgeschlagen: {str(e)}")
            return False

    def ist_savage_pathfinder_setting(self):
        """
        NEU: Prüft, ob das aktuelle Setting Savage Pathfinder ist.
        
        Returns:
            bool: True wenn Savage Pathfinder, sonst False
        """
        try:
            return self.charakter.ist_savage_pathfinder_setting()
        except Exception as e:
            Logger.error(f"Fehler bei Pathfinder-Setting-Prüfung: {str(e)}")
            return False

    def hat_bereits_kostenloses_pathfinder_talent(self):
        """
        NEU: Prüft, ob bereits ein kostenloses Pathfinder-Talent gewählt wurde.
        
        Returns:
            bool: True wenn bereits ein kostenloses Talent gewählt wurde
        """
        try:
            return self.charakter.hat_bereits_kostenloses_pathfinder_talent()
        except Exception as e:
            Logger.error(f"Fehler bei Pathfinder-Talent-Prüfung: {str(e)}")
            return False

    def ist_pathfinder_kostenloses_talent(self, talent_name):
        """
        NEU: Prüft, ob ein Talent zu den Kategorien gehört, die in Savage Pathfinder 
        während der Charaktererstellung kostenlos gewählt werden können.
        
        Args:
            talent_name (str): Name des Talents
            
        Returns:
            bool: True wenn Klassen-, Hintergrund- oder Experte-Talent, sonst False
        """
        try:
            if talent_name in self.charakter.talente:
                talent = self.charakter.talente[talent_name]
                return self.charakter.ist_pathfinder_kostenloses_talent(talent)
            return False
        except Exception as e:
            Logger.error(f"Fehler bei Pathfinder-Kategorie-Prüfung für {talent_name}: {str(e)}")
            return False

    def get_pathfinder_info(self):
        """
        NEU: Gibt Informationen über den Pathfinder-Status des Charakters zurück.
        
        Returns:
            dict: Dictionary mit Pathfinder-Informationen
        """
        try:
            return {
                'ist_pathfinder_setting': self.ist_savage_pathfinder_setting(),
                'kostenlose_talente_gewaehlt': getattr(self.charakter, 'pathfinder_kostenlose_talente_gewaehlt', 0),
                'kann_kostenloses_talent_waehlen': (
                    self.ist_savage_pathfinder_setting() and 
                    not self.charakter.char_gen_completed and
                    not self.hat_bereits_kostenloses_pathfinder_talent()
                ),
                'char_gen_completed': self.charakter.char_gen_completed
            }
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Pathfinder-Informationen: {str(e)}")
            return {
                'ist_pathfinder_setting': False,
                'kostenlose_talente_gewaehlt': 0,
                'kann_kostenloses_talent_waehlen': False,
                'char_gen_completed': True
            }

    # Zusätzlich sollte in der bestehenden waehle_talent Methode 
    # ein Log-Eintrag hinzugefügt werden, wenn Pathfinder-spezifische Rückgabewerte auftreten:

    def waehle_talent(self, talent_name, ignore_rang_check=False, ignore_voraussetzungen=False):
        """
        Wählt ein Talent für den Charakter aus
        ERWEITERT: Mit verbessertem Logging für Pathfinder-Features
        
        Args:
            talent_name (str): Name des Talents
            ignore_rang_check (bool): Flag zum Ignorieren der Rangprüfung
            ignore_voraussetzungen (bool): Flag zum Ignorieren der Voraussetzungen
            
        Returns:
            bool oder str: Ergebniscode oder Erfolgsstatus
        """
        try:
            # Flag nur setzen, wenn es angefordert wurde
            if ignore_voraussetzungen:
                self.charakter.ignore_voraussetzungen = True
                Logger.debug(f"Controller: Flag ignore_voraussetzungen gesetzt für '{talent_name}'")
                
            # Parameter weitergeben
            result = self.charakter.waehle_talent(talent_name, ignore_rang_check=ignore_rang_check)
            
            # Pathfinder-spezifische Behandlung
            if result == "pathfinder_kostenlos_angeboten":
                Logger.info(f"Pathfinder-Talent '{talent_name}' kann kostenlos gewählt werden")
            elif result is True:
                self.dispatch('on_charakter_updated')
                Logger.debug(f"Talent '{talent_name}' erfolgreich ausgewählt")
            
            return result
        except Exception as e:
            Logger.error(f"Fehler bei Auswahl von Talent {talent_name}: {str(e)}")
            self.dispatch('on_charakter_error', f"Talent-Auswahl fehlgeschlagen: {str(e)}")
            return False        