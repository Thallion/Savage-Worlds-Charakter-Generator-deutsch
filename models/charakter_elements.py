#charakter_elements.py
"""
Verwaltung von Talenten, Handicaps, Mächten und Völkern für die Charakter-Klasse.
"""
from kivy.logger import Logger
import functions.talent_funktionen as talent_funktionen
import functions.macht_funktionen as macht_funktionen
import functions.handicap_funktionen as handicap_funktionen
import functions.superkraft_funktionen as superkraft_funktionen

class CharakterElements:
    """Mixin-Klasse für Element-Verwaltung"""
    
    # === HANDICAPS ===
    def initialisiere_handicaps(self, handicap_daten):
        handicap_funktionen.initialisiere_handicaps(self, handicap_daten)
    
    def waehle_handicap(self, handicap_name_key):
        return handicap_funktionen.waehle_handicap(self, handicap_name_key)
    
    def entferne_handicap(self, handicap_name_key, force_remove=False):
        return handicap_funktionen.entferne_handicap(self, handicap_name_key, force_remove)
    
    def reduziere_handicap(self, handicap_name_key):
        return handicap_funktionen.reduziere_handicap(self, handicap_name_key)
    
    def aktive_handicaps(self):
        return handicap_funktionen.aktive_handicaps(self)
    
    def ausgewaehlte_handicaps(self):
        return handicap_funktionen.ausgewaehlte_handicaps(self)
    
    def add_handicap(self, handicap):
        return handicap_funktionen.add_handicap(self, handicap)
    
    def remove_handicap(self, handicap_name):
        return handicap_funktionen.remove_handicap(self, handicap_name)
    
    def save_custom_handicaps(self):
        handicap_funktionen.save_custom_handicaps(self)
    
    def load_custom_handicaps(self):
        handicap_funktionen.load_custom_handicaps(self)
    
    # === TALENTE ===
    def initialisiere_talente(self, talent_daten):
        talent_funktionen.initialisiere_talente(self, talent_daten)
    
    def ausgewaehlte_talente(self):
        return talent_funktionen.ausgewaehlte_talente(self)
    
    def aktive_talente(self):
        return talent_funktionen.aktive_talente(self)
    
    def get_freie_talente(self):
        return talent_funktionen.get_freie_talente(self)
    
    def talent_auswaehlen(self, talent_name_key):
        return talent_funktionen.talent_auswaehlen(self, talent_name_key)
    
    def waehle_talent(self, talent_name_key, ignore_rang_check=False):
        """
        Wrapper für talent_funktionen.waehle_talent, mit Unterstützung für ignore_voraussetzungen.
        
        Args:
            talent_name_key: Der Name des auszuwählenden Talents
            ignore_rang_check: Flag, um die Rang-Prüfung zu überspringen
            
        Returns:
            str oder bool: Wie in talent_funktionen.waehle_talent
        """
        return talent_funktionen.waehle_talent(self, talent_name_key, ignore_rang_check)
    
    def entferne_talent(self, talent_name_key):
        return talent_funktionen.entferne_talent(self, talent_name_key)
    
    def add_talent(self, talent):
        return talent_funktionen.add_talent(self, talent)
    
    def remove_talent(self, talent_name):
        return talent_funktionen.remove_talent(self, talent_name)
    
    def save_custom_talents(self):
        talent_funktionen.save_custom_talents(self)
    
    def load_custom_talents(self):
        talent_funktionen.load_custom_talents(self)
    
    # === MÄCHTE ===
    def initialisiere_maechte(self, maechte_daten):
        macht_funktionen.initialisiere_maechte(self, maechte_daten)
    
    def waehle_macht(self, macht_name_key, ignore_rang_check=False):
        """
        Wählt eine Macht aus und aktualisiert die verfügbaren Mächte des Charakters.
        
        Args:
            macht_name_key: Der Name der Macht
            ignore_rang_check: Flag, um die Rang-Prüfung zu überspringen (für UI-Bestätigung)
            
        Returns:
            str oder bool: "needs_rang_confirmation" wenn der Rang zu niedrig ist,
                        True bei Erfolg, False bei Misserfolg
        """
        return macht_funktionen.waehle_macht(self, macht_name_key, ignore_rang_check=ignore_rang_check)
    
    def entferne_macht(self, macht_name_key):
        return macht_funktionen.entferne_macht(self, macht_name_key)
    
    def aktive_maechte(self):
        return macht_funktionen.aktive_maechte(self)
    
    def ausgewaehlte_maechte(self):
        return macht_funktionen.ausgewaehlte_maechte(self)
    
    def add_macht(self, macht):
        return macht_funktionen.add_macht(self, macht)
    
    def remove_macht(self, macht_name):
        return macht_funktionen.remove_macht(self, macht_name)
    
    def erhoehe_machtpunkte(self, punkte):
        macht_funktionen.erhoehe_machtpunkte(self, punkte)
    
    def senke_machtpunkte(self, punkte):
        macht_funktionen.senke_machtpunkte(self, punkte)
    
    def save_custom_maechte(self):
        macht_funktionen.save_custom_maechte(self)
    
    def load_custom_maechte(self):
        macht_funktionen.load_custom_maechte(self)
    
    # === SUPERKRÄFTE ===
    def initialisiere_superkraefte(self, krafte_daten):
        superkraft_funktionen.initialisiere_superkraefte(self, krafte_daten)

    def waehle_superkraft(self, kraft_name, kosten=None):
        return superkraft_funktionen.waehle_superkraft(self, kraft_name, kosten)

    def entferne_superkraft(self, kraft_name):
        return superkraft_funktionen.entferne_superkraft(self, kraft_name)

    def ausgewaehlte_superkraefte(self):
        return superkraft_funktionen.ausgewaehlte_superkraefte(self)

    def berechne_superkraft_kosten(self):
        return superkraft_funktionen.berechne_gesamt_kosten(self)

    def setze_machtstufe(self, stufe):
        return superkraft_funktionen.setze_machtstufe(self, stufe)

    def waehle_superkraft_modifikator(self, kraft_name, mod_name):
        return superkraft_funktionen.waehle_modifikator(self, kraft_name, mod_name)

    def entferne_superkraft_modifikator(self, kraft_name, mod_name):
        return superkraft_funktionen.entferne_modifikator(self, kraft_name, mod_name)

    def get_verbleibende_skp(self):
        return superkraft_funktionen.get_verbleibende_skp(self)

    def ist_superkraefte_setting(self):
        """Prüft ob das aktuelle Setting Superkräfte verwendet."""
        return superkraft_funktionen.ist_superkraefte_setting(self.active_setting_name)

    # === VÖLKER ===
    def set_selected_volk(self, volk_name):
        self.volk_manager.set_selected_volk(volk_name)
    
    def toggle_selected_volk(self, volk_name, value):
        self.volk_manager.toggle_selected_volk(volk_name, value)
    
    def waehle_volk(self, volk_name):
        self.volk_manager.waehle_volk(volk_name)
    
    def entferne_volk(self):
        self.volk_manager.entferne_volk()
    
    # === PATHFINDER SPEZIAL ===
    def waehle_pathfinder_kostenloses_talent(self, talent_name_key, ignore_voraussetzungen=False):
        """
        NEU: Wählt ein Klassen-, Hintergrund- oder Experte-Talent in Savage Pathfinder kostenlos aus.
        
        Args:
            talent_name_key: Der Name des auszuwählenden Talents
            ignore_voraussetzungen: Flag zum Ignorieren der Voraussetzungsprüfung
            
        Returns:
            str oder bool: Wie in talent_funktionen.waehle_pathfinder_kostenloses_talent
        """
        return talent_funktionen.waehle_pathfinder_kostenloses_talent(self, talent_name_key, ignore_voraussetzungen)
    
    def ist_savage_pathfinder_setting(self):
        """
        NEU: Prüft, ob das aktuelle Setting Savage Pathfinder ist.
        
        Returns:
            bool: True wenn Savage Pathfinder, sonst False
        """
        return talent_funktionen.ist_savage_pathfinder_setting(self)
    
    def hat_bereits_kostenloses_pathfinder_talent(self):
        """
        NEU: Prüft, ob bereits ein kostenloses Pathfinder-Talent gewählt wurde.
        
        Returns:
            bool: True wenn bereits ein kostenloses Talent gewählt wurde
        """
        return talent_funktionen.hat_bereits_kostenloses_pathfinder_talent(self)
    
    def ist_pathfinder_kostenloses_talent(self, talent):
        """
        NEU: Prüft, ob ein Talent zu den Kategorien gehört, die in Savage Pathfinder 
        während der Charaktererstellung kostenlos gewählt werden können.
        
        Args:
            talent: Das Talent-Objekt
            
        Returns:
            bool: True wenn Klassen-, Hintergrund- oder Experte-Talent, sonst False
        """
        return talent_funktionen.ist_pathfinder_kostenloses_talent(talent)
    
    def erfuellt_voraussetzung(self, charakter):
        """
        Prüft, ob der Charakter die Voraussetzungen für das Talent erfüllt.
        Da wir die Voraussetzungen vorerst ignorieren, geben wir immer True zurück.
        """
        return True