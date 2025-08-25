#charakter_equipment.py
"""
Ausrüstungsverwaltung für die Charakter-Klasse.
"""
from kivy.logger import Logger
import functions.ausruestung_funktionen as ausruestung_funktionen

class CharakterEquipment:
    """Mixin-Klasse für Ausrüstungsverwaltung"""
    
    def initialisiere_ausruestung(self, ausruestung):
        self.ausruestung = {}
        try:
            for name, item in ausruestung.items():
                self.ausruestung[name] = item
            Logger.debug("Ausrüstung erfolgreich initialisiert.")
        except Exception as e:
            Logger.error(f"Fehler bei der Initialisierung der Ausrüstung: {e}")
    
    def add_ausruestung(self, item):
        if item.name in self.ausruestung:
            self.ausruestung[item.name].menge += item.menge
        else:
            self.ausruestung[item.name] = item
        return True
    
    def remove_ausruestung(self, item_name):
        if item_name in self.ausruestung:
            del self.ausruestung[item_name]
            return True
        else:
            return False
    
    def ausruestung_nach_setting(self, setting):
        """
        Gibt eine Liste der Ausrüstung für ein bestimmtes Setting zurück.

        :param setting: Das gewünschte Setting ('modern', 'mittelalter', 'futuristisch').
        """
        return [ausr for ausr in self.ausruestung.values() if ausr.setting == setting.lower()]
    
    def kaufen(self, item, anzahl=1, preis_pro_stueck=None):
        return ausruestung_funktionen.kaufen(self, item, anzahl, preis_pro_stueck)
    
    def verkaufen(self, item, anzahl=1, preis_pro_stueck=None):
        return ausruestung_funktionen.verkaufen(self, item, anzahl, preis_pro_stueck)
    
    def get_item_by_name(self, item_name):
        return ausruestung_funktionen.get_item_by_name(self, item_name)
    
    def berechne_gesamtkosten(self):
        return ausruestung_funktionen.berechne_gesamtkosten(self)
    
    def berechne_traglast(self):
        """Berechnet die maximale Traglast basierend auf Stärke-Attribut"""
        try:
            staerke_wert = getattr(self, 'staerke', 4)
            if hasattr(staerke_wert, 'wert'):
                staerke_wert = staerke_wert.wert
            
            # Savage Worlds Traglast-Berechnung: Stärke x 10
            return int(staerke_wert) * 10
        except (AttributeError, ValueError, TypeError):
            return 100  # Fallback-Wert
    
    def berechne_gesamtgewicht(self):
        """Berechnet das Gesamtgewicht der Ausrüstung"""
        try:
            gesamtgewicht = 0
            if hasattr(self, 'ausruestung') and self.ausruestung:
                for item in self.ausruestung.values():
                    if hasattr(item, 'gewicht') and hasattr(item, 'menge'):
                        gesamtgewicht += (item.gewicht or 0) * (item.menge or 1)
            return gesamtgewicht
        except (AttributeError, TypeError):
            return 0
    
    def berechne_gesamt_ruestungsschutz(self):
        return ausruestung_funktionen.berechne_gesamt_ruestungsschutz(self)
    
    def get_effektive_staerke(self, fuer_ausruestung=False):
        """
        Berechnet die effektive Stärke des Charakters.
        Berücksichtigt das Talent "Kräftig" und das Handicap "Fettleibig" für Mindeststärke und Traglast.
        
        Args:
            fuer_ausruestung: Ob die Stärke für Mindeststärke/Traglast (True) oder normal (False) berechnet werden soll
            
        Returns:
            int: Der effektive Stärkewert
        """
        # Basiswert der Stärke
        staerke_attribut = self.attribute.get('Stärke')
        if not staerke_attribut:
            Logger.warning("Stärke-Attribut nicht gefunden.")
            return 4  # Standardwert
        
        staerke_wert = staerke_attribut.wert
        
        # Für Mindeststärke und Traglast
        if fuer_ausruestung:
            # Prüfen, ob der Charakter das Talent "Kräftig" hat
            if "Kräftig" in self.selected_talente:
                # Stärke um einen Würfeltyp erhöhen
                if staerke_wert == 4:
                    staerke_wert = 6
                elif staerke_wert == 6:
                    staerke_wert = 8
                elif staerke_wert == 8:
                    staerke_wert = 10
                elif staerke_wert == 10:
                    staerke_wert = 12
            
            # Prüfen, ob der Charakter das Handicap "Fettleibig" hat
            for handicap_name in self.selected_handicaps:
                if handicap_name in self.handicaps:
                    handicap = self.handicaps[handicap_name]
                    if "Fettleibig" in handicap.name and handicap.stufe == "leicht":
                        # Stärke um einen Würfeltyp reduzieren für Mindeststärke
                        if staerke_wert == 12:
                            staerke_wert = 10
                        elif staerke_wert == 10:
                            staerke_wert = 8
                        elif staerke_wert == 8:
                            staerke_wert = 6
                        elif staerke_wert == 6:
                            staerke_wert = 4
                        # W4 bleibt W4
        
        return staerke_wert