"""
Modul für die Verwaltung von Attributen und Fertigkeiten im Charakter.
Dieses Modul enthält die EigenschaftenManager-Klasse zur zentralen Verwaltung der Charakter-Eigenschaften,
einschließlich der Initialisierung, Steigerung und Senkung von Attributen und Fertigkeiten.
"""

import json
import os
from pathlib import Path
from kivy.logger import Logger
from models.wuerfel import Wuerfel
from models.attribut import Attribut
from models.fertigkeit import Fertigkeit


class EigenschaftenManager:
    """
    Zentrale Manager-Klasse für die Verwaltung von Attributen und Fertigkeiten.
    """
    
    def __init__(self, config_path=None):
        """
        Initialisiert den EigenschaftenManager.
        
        Args:
            config_path: Pfad zur Config-Datei (optional)
        """
        self.config = self._load_config(config_path)
        self.grundfertigkeiten = self.config.get('grundfertigkeiten', [])
        self.standard_attribute = self.config.get('standard_attribute', {})
        self.kosten = self.config.get('kosten', {})
        
    def _load_config(self, config_path=None):
        """
        Lädt die Konfiguration aus der JSON-Datei.
        
        Args:
            config_path: Pfad zur Config-Datei
            
        Returns:
            dict: Konfigurationsdaten
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'eigenschaften_config.json'
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    Logger.info(f"Eigenschaften-Konfiguration geladen von {config_path}")
                    return config
            else:
                Logger.warning(f"Config-Datei nicht gefunden: {config_path}, verwende Standardwerte")
                return self._get_default_config()
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Konfiguration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self):
        """
        Gibt die Standard-Konfiguration zurück.
        
        Returns:
            dict: Standard-Konfigurationsdaten
        """
        return {
            "grundfertigkeiten": [
                "Allgemeinwissen",
                "Athletik", 
                "Heimlichkeit",
                "Überreden",
                "Wahrnehmung"
            ],
            "standard_attribute": {
                "Stärke": {"wert": 4, "modifier": 0},
                "Geschicklichkeit": {"wert": 4, "modifier": 0},
                "Konstitution": {"wert": 4, "modifier": 0},
                "Verstand": {"wert": 4, "modifier": 0},
                "Willenskraft": {"wert": 4, "modifier": 0}
            },
            "start_attributsteigerungen": 5,
            "kosten": {
                "attribut_chargen": 1,
                "attribut_spiel": 1,
                "fertigkeit_chargen": 1,
                "fertigkeit_spiel": 1,
                "fertigkeit_ueber_attribut": 2
            }
        }
    
    #-----------------------------------------------
    # Attribut-Funktionen
    #-----------------------------------------------
    
    def initialisiere_attribute(self, charakter):
        """
        Initialisiert die Basisattribute für den Charakter.
        
        Args:
            charakter: Das Charakter-Objekt
        """
        # Attribute erstellen
        charakter.attribute = {}
        for name, daten in self.standard_attribute.items():
            attribut = Attribut(
                attribut_name=name,
                wert=daten["wert"],
                modifier=daten["modifier"]
            )
            attribut.bind(wert=charakter.on_attribut_wert_change)
            attribut.bind(modifier=charakter.on_attribut_modifier_change)
            charakter.attribute[name] = attribut
        
        charakter.verbleibende_attributsteigerungen = self.config.get('start_attributsteigerungen', 5)
        Logger.info(f"Attribute initialisiert mit {charakter.verbleibende_attributsteigerungen} verfügbaren Steigerungen")
    
    def get_attribute_dict(self, charakter):
        """
        Gibt ein Wörterbuch aller Attribute zurück.
        
        Args:
            charakter: Das Charakter-Objekt
            
        Returns:
            dict: Dictionary mit allen Attributen
        """
        return charakter.attribute
    
    def steigere_attribut(self, charakter, attribut_name):
        """
        Steigert ein Attribut um eine Stufe.
        
        Args:
            charakter: Das Charakter-Objekt
            attribut_name: Der Name des zu steigernden Attributs
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        attribut = charakter.attribute.get(attribut_name)
        if not attribut:
            Logger.error(f"Attribut '{attribut_name}' existiert nicht.")
            return False
        
        # Prüfe ob Maximum erreicht
        max_wert = self.config.get('max_wuerfel_wert', 12)
        if attribut.wuerfel.value >= max_wert:
            Logger.warning(f"Attribut '{attribut_name}' hat bereits den Maximalwert W{max_wert}.")
            return False
        
        # Bestimme die Kosten
        if charakter.char_gen_completed:
            kosten = self.kosten.get('attribut_spiel', 1)
            if charakter.verbleibende_aufstiege < kosten:
                Logger.warning(f"Nicht genügend Aufstiege verfügbar. Benötigt: {kosten}, Verfügbar: {charakter.verbleibende_aufstiege}")
                return False
            charakter.verbleibende_aufstiege -= kosten
        else:
            kosten = self.kosten.get('attribut_chargen', 1)
            # Prüfe zuerst normale Attributspunkte
            if charakter.verbleibende_attributsteigerungen >= kosten:
                charakter.verbleibende_attributsteigerungen -= kosten
            # Falls keine normalen Punkte verfügbar, prüfe Handicap-Punkte (2 HP = 1 Attr)
            elif hasattr(charakter, 'verbleibende_handicap_punkte') and charakter.verbleibende_handicap_punkte >= 2:
                charakter.verbleibende_handicap_punkte -= 2
                Logger.info(f"Attributsteigerung mit 2 Handicap-Punkten bezahlt.")
            else:
                verfügbare_attr = charakter.verbleibende_attributsteigerungen
                verfügbare_hp = getattr(charakter, 'verbleibende_handicap_punkte', 0)
                Logger.warning(f"Nicht genügend Punkte verfügbar. Benötigt: {kosten} Attributspunkte ODER 2 Handicap-Punkte. Verfügbar: {verfügbare_attr} Attributspunkte, {verfügbare_hp} Handicap-Punkte")
                return False
        
        # Alte Werte für Event merken
        old_value = attribut.wuerfel.value
        
        # Führe die Steigerung durch
        attribut.wuerfel.increase()
        Logger.debug(f"Attribut '{attribut_name}' wurde auf W{attribut.wuerfel.value}+{attribut.wuerfel.modifier} gesteigert.")
        
        # Event für Historie-System senden
        new_value = attribut.wuerfel.value
        cost_type = "Aufstiege" if charakter.char_gen_completed else (
            "Handicap-Punkte" if hasattr(charakter, 'verbleibende_handicap_punkte') and 
            charakter.verbleibende_attributsteigerungen < kosten and
            charakter.verbleibende_handicap_punkte >= 2 else "Attributspunkte"
        )
        
        try:
            from services.service_container import service_container
            event_service = service_container.get_event_service()
            if event_service:
                event_service.publish('attribute_changed', {
                    'attribute_name': attribut_name,
                    'old_value': old_value,
                    'new_value': new_value,
                    'cost': kosten,
                    'cost_type': cost_type
                })
        except Exception as e:
            Logger.warning(f"Event-Publishing fehlgeschlagen: {e}")
        
        # Aktualisiere abgeleitete Werte
        charakter.rang = charakter.get_rang(charakter.aufstiege_gesamt)
        charakter.berechne_abgeleitete_werte()
        
        return True
    
    def senke_attribut(self, charakter, attribut_name):
        """
        Senkt ein Attribut um eine Stufe.
        
        Args:
            charakter: Das Charakter-Objekt
            attribut_name: Der Name des zu senkenden Attributs
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        attribut = charakter.attribute.get(attribut_name)
        if not attribut:
            Logger.error(f"Attribut '{attribut_name}' existiert nicht.")
            return False
        
        # Prüfe ob Minimum erreicht
        if attribut.wuerfel.value <= 4:
            Logger.warning(f"Attribut '{attribut_name}' kann nicht unter W4 gesenkt werden.")
            return False
        
        # Senke das Attribut
        attribut.wuerfel.decrease()
        Logger.debug(f"Attribut '{attribut_name}' wurde auf W{attribut.wuerfel.value}+{attribut.wuerfel.modifier} gesenkt.")
        
        # Gib Punkte zurück
        if charakter.char_gen_completed:
            kosten = self.kosten.get('attribut_spiel', 1)
            charakter.verbleibende_aufstiege += kosten
        else:
            kosten = self.kosten.get('attribut_chargen', 1)
            charakter.verbleibende_attributsteigerungen += kosten
        
        # Aktualisiere abgeleitete Werte
        charakter.rang = charakter.get_rang(charakter.aufstiege_gesamt)
        charakter.berechne_abgeleitete_werte()
        
        return True
    
    #-----------------------------------------------
    # Fertigkeiten-Funktionen
    #-----------------------------------------------
    
    def initialisiere_fertigkeiten(self, charakter):
        """
        Initialisiert die Fertigkeiten des Charakters.
        
        Args:
            charakter: Das Charakter-Objekt
        """
        # Erstelle Sets für Vergleiche
        fertigkeiten_namen_in_daten = set(charakter.fertigkeiten_daten.keys())
        fertigkeiten_namen_aktuell = set(charakter.fertigkeiten.keys())
        
        # Aktualisiere oder erstelle Fertigkeiten
        for fertigkeit_name, attribut_set in charakter.fertigkeiten_daten.items():
            if not isinstance(attribut_set, set) or len(attribut_set) != 1:
                Logger.error(f"Fertigkeit '{fertigkeit_name}' hat eine ungültige Attribut-Zuweisung.")
                continue
            
            attribut_name = next(iter(attribut_set))
            attribut_obj = charakter.attribute.get(attribut_name)
            
            if attribut_obj is None:
                Logger.error(f"Attribut '{attribut_name}' für Fertigkeit '{fertigkeit_name}' nicht gefunden.")
                continue
            
            ist_grundfertigkeit = fertigkeit_name in self.grundfertigkeiten
            
            if fertigkeit_name in charakter.fertigkeiten:
                # Bestehende Fertigkeit aktualisieren
                fertigkeit = charakter.fertigkeiten[fertigkeit_name]
                fertigkeit.attribut = attribut_obj
                fertigkeit.grundfertigkeit = ist_grundfertigkeit
            else:
                # Neue Fertigkeit erstellen
                fertigkeit = Fertigkeit(
                    fertigkeit_name=fertigkeit_name,
                    attribut=attribut_obj,
                    grundfertigkeit=ist_grundfertigkeit,
                )
                fertigkeit.bind(wert=charakter.on_fertigkeit_wert_change)
                fertigkeit.bind(modifier=charakter.on_fertigkeit_modifier_change)
                charakter.fertigkeiten[fertigkeit_name] = fertigkeit
        
        # Entferne veraltete Fertigkeiten
        fertigkeiten_zu_entfernen = fertigkeiten_namen_aktuell - fertigkeiten_namen_in_daten
        for fertigkeit_name in fertigkeiten_zu_entfernen:
            del charakter.fertigkeiten[fertigkeit_name]
            Logger.info(f"Fertigkeit '{fertigkeit_name}' wurde entfernt, da sie nicht im geladenen Setting vorhanden ist.")
    
    def steigere_fertigkeit(self, charakter, fertigkeit_name, confirm_double_cost=False):
        """
        Steigert eine Fertigkeit um eine Stufe.
        
        Args:
            charakter: Das Charakter-Objekt
            fertigkeit_name: Der Name der zu steigernden Fertigkeit
            confirm_double_cost: Bestätigung für doppelte Kosten
            
        Returns:
            str oder bool: "needs_confirmation" wenn Bestätigung erforderlich, True bei Erfolg, False bei Misserfolg
        """
        fertigkeit = charakter.fertigkeiten.get(fertigkeit_name)
        if not fertigkeit:
            Logger.error(f"Fertigkeit '{fertigkeit_name}' existiert nicht.")
            return False
        
        # Prüfe ob Maximum erreicht
        max_wert = self.config.get('max_wuerfel_wert', 12)
        if fertigkeit.wuerfel.value >= max_wert:
            Logger.warning(f"Fertigkeit '{fertigkeit_name}' hat bereits den Maximalwert W{max_wert}.")
            return False
        
        # Prüfe ob Fertigkeit über Attribut steigt (Berücksichtige effektive Werte)
        if fertigkeit.attribut:
            fertigkeit_eff = fertigkeit.wuerfel.value + (fertigkeit.wuerfel.modifier if fertigkeit.wuerfel.value == 4 else 0)
            attribut_eff = fertigkeit.attribut.wuerfel.value + (fertigkeit.attribut.wuerfel.modifier if fertigkeit.attribut.wuerfel.value == 4 else 0)
            if fertigkeit_eff >= attribut_eff:
                if not confirm_double_cost:
                    return "needs_confirmation"
        
        # Berechne Kosten
        kosten = self._berechne_fertigkeit_kosten(charakter, fertigkeit, fertigkeit.attribut)
        
        # Prüfe verfügbare Punkte
        if charakter.char_gen_completed:
            if charakter.verbleibende_aufstiege < kosten:
                Logger.warning(f"Nicht genügend Aufstiege. Benötigt: {kosten}, Verfügbar: {charakter.verbleibende_aufstiege}")
                return False
            charakter.verbleibende_aufstiege -= kosten
        else:
            # Verwende das richtige Attribut für Fertigkeitspunkte
            verfuegbare_punkte = charakter.verbleibende_fertigkeitssteigerungen
            
            # Prüfe zuerst normale Fertigkeitspunkte
            if verfuegbare_punkte >= kosten:
                charakter.verbleibende_fertigkeitssteigerungen -= kosten
            # Falls keine normalen Punkte verfügbar, prüfe Handicap-Punkte (1 HP = 1 Fertigkeitssteigerung)
            elif hasattr(charakter, 'verbleibende_handicap_punkte') and charakter.verbleibende_handicap_punkte >= kosten:
                charakter.verbleibende_handicap_punkte -= kosten
                Logger.info(f"Fertigkeitssteigerung mit {kosten} Handicap-Punkt(en) bezahlt.")
            else:
                verfügbare_hp = getattr(charakter, 'verbleibende_handicap_punkte', 0)
                Logger.warning(f"Nicht genügend Punkte verfügbar. Benötigt: {kosten} Fertigkeitspunkte ODER {kosten} Handicap-Punkte. Verfügbar: {verfuegbare_punkte} Fertigkeitspunkte, {verfügbare_hp} Handicap-Punkte")
                return False
        
        # Alte Werte für Event merken
        old_value = fertigkeit.wuerfel.value
        
        # Steigere die Fertigkeit
        fertigkeit.wuerfel.increase()
        Logger.debug(f"Fertigkeit '{fertigkeit_name}' wurde auf W{fertigkeit.wuerfel.value}+{fertigkeit.wuerfel.modifier} gesteigert.")
        
        # Event für Historie-System senden
        new_value = fertigkeit.wuerfel.value
        cost_type = "Aufstiege" if charakter.char_gen_completed else (
            "Handicap-Punkte" if hasattr(charakter, 'verbleibende_handicap_punkte') and 
            charakter.verbleibende_fertigkeitssteigerungen < kosten and
            charakter.verbleibende_handicap_punkte >= kosten else "Fertigkeitspunkte"
        )
        
        try:
            from services.service_container import service_container
            event_service = service_container.get_event_service()
            if event_service:
                event_service.publish('skill_changed', {
                    'skill_name': fertigkeit_name,
                    'old_value': old_value,
                    'new_value': new_value,
                    'cost': kosten,
                    'cost_type': cost_type
                })
        except Exception as e:
            Logger.warning(f"Event-Publishing fehlgeschlagen: {e}")
        
        return True
    
    def _berechne_fertigkeit_kosten(self, charakter, fertigkeit, attribut):
        """
        Berechnet die Kosten für eine Fertigkeitssteigerung.
        
        Args:
            charakter: Das Charakter-Objekt
            fertigkeit: Die Fertigkeit
            attribut: Das zugehörige Attribut
            
        Returns:
            int: Die Kosten
        """
        if charakter.char_gen_completed:
            base_kosten = self.kosten.get('fertigkeit_spiel', 1)
        else:
            base_kosten = self.kosten.get('fertigkeit_chargen', 1)
        
        # Doppelte Kosten wenn Fertigkeit über Attribut (Berücksichtige effektive Werte)
        if attribut:
            fertigkeit_eff = fertigkeit.wuerfel.value + (fertigkeit.wuerfel.modifier if fertigkeit.wuerfel.value == 4 else 0)
            attribut_eff = attribut.wuerfel.value + (attribut.wuerfel.modifier if attribut.wuerfel.value == 4 else 0)
            if fertigkeit_eff > attribut_eff:
                return base_kosten * self.kosten.get('fertigkeit_ueber_attribut', 2)
        
        return base_kosten
    
    def senke_fertigkeit(self, charakter, fertigkeit_name):
        """
        Senkt eine Fertigkeit um eine Stufe.
        
        Args:
            charakter: Das Charakter-Objekt
            fertigkeit_name: Der Name der zu senkenden Fertigkeit
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        fertigkeit = charakter.fertigkeiten.get(fertigkeit_name)
        if not fertigkeit:
            Logger.error(f"Fertigkeit '{fertigkeit_name}' existiert nicht.")
            return False
        
        # Prüfe ob Minimum erreicht (0 für normale, 4 für Grundfertigkeiten)
        min_wert = 4 if fertigkeit.grundfertigkeit else 0
        if fertigkeit.wuerfel.value <= min_wert:
            Logger.warning(f"Fertigkeit '{fertigkeit_name}' kann nicht unter W{min_wert} gesenkt werden.")
            return False
        
        # Berechne Rückerstattung
        kosten = self._berechne_fertigkeit_kosten(charakter, fertigkeit, fertigkeit.attribut)
        
        # Senke die Fertigkeit
        fertigkeit.wuerfel.decrease()
        Logger.debug(f"Fertigkeit '{fertigkeit_name}' wurde auf W{fertigkeit.wuerfel.value}+{fertigkeit.wuerfel.modifier} gesenkt.")
        
        # Erstatte Punkte zurück
        if charakter.char_gen_completed:
            charakter.verbleibende_aufstiege += kosten
        else:
            charakter.verbleibende_fertigkeitssteigerungen += kosten
        
        return True
    
    def add_fertigkeit(self, charakter, fertigkeit):
        """
        Fügt eine neue Fertigkeit hinzu.
        
        Args:
            charakter: Das Charakter-Objekt
            fertigkeit: Die hinzuzufügende Fertigkeit
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        if fertigkeit.fertigkeit_name in charakter.fertigkeiten:
            Logger.warning(f"Fertigkeit '{fertigkeit.fertigkeit_name}' existiert bereits.")
            return False
        
        fertigkeit.bind(wert=charakter.on_fertigkeit_wert_change)
        fertigkeit.bind(modifier=charakter.on_fertigkeit_modifier_change)
        charakter.fertigkeiten[fertigkeit.fertigkeit_name] = fertigkeit
        
        Logger.info(f"Fertigkeit '{fertigkeit.fertigkeit_name}' hinzugefügt.")
        self.save_custom_fertigkeiten(charakter)
        
        return True
    
    def remove_fertigkeit(self, charakter, fertigkeit_name):
        """
        Entfernt eine Fertigkeit.
        
        Args:
            charakter: Das Charakter-Objekt
            fertigkeit_name: Der Name der zu entfernenden Fertigkeit
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        if fertigkeit_name not in charakter.fertigkeiten:
            Logger.warning(f"Fertigkeit '{fertigkeit_name}' existiert nicht.")
            return False
        
        # Verhindere das Entfernen von Grundfertigkeiten
        if fertigkeit_name in self.grundfertigkeiten:
            Logger.warning(f"Grundfertigkeit '{fertigkeit_name}' kann nicht entfernt werden.")
            return False
        
        del charakter.fertigkeiten[fertigkeit_name]
        Logger.info(f"Fertigkeit '{fertigkeit_name}' entfernt.")
        self.save_custom_fertigkeiten(charakter)
        
        return True
    
    def save_custom_fertigkeiten(self, charakter):
        """
        Speichert die benutzerdefinierten Fertigkeiten in einer JSON-Datei.
        
        Args:
            charakter: Das Charakter-Objekt
        """
        custom_fertigkeiten = {
            name: fertigkeit.to_dict()
            for name, fertigkeit in charakter.fertigkeiten.items()
            if getattr(fertigkeit, 'custom', False)
        }
        
        if not custom_fertigkeiten:
            Logger.info("Keine benutzerdefinierten Fertigkeiten zum Speichern.")
            return
        
        custom_fertigkeiten_file = Path(__file__).parent / 'custom_fertigkeiten.json'
        
        try:
            with open(custom_fertigkeiten_file, 'w', encoding='utf-8') as f:
                json.dump(custom_fertigkeiten, f, ensure_ascii=False, indent=4)
            Logger.info(f"Benutzerdefinierte Fertigkeiten wurden in {custom_fertigkeiten_file} gespeichert.")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der benutzerdefinierten Fertigkeiten: {e}")
    
    def load_custom_fertigkeiten(self, charakter):
        """
        Lädt die benutzerdefinierten Fertigkeiten aus einer JSON-Datei.
        
        Args:
            charakter: Das Charakter-Objekt
        """
        custom_fertigkeiten_file = Path(__file__).parent / 'custom_fertigkeiten.json'
        
        if not custom_fertigkeiten_file.exists():
            Logger.info("Keine benutzerdefinierten Fertigkeiten zum Laden gefunden.")
            return
        
        try:
            with open(custom_fertigkeiten_file, 'r', encoding='utf-8') as f:
                custom_fertigkeiten_data = json.load(f)
            
            attribute_dict = self.get_attribute_dict(charakter)
            
            for name, data in custom_fertigkeiten_data.items():
                fertigkeit = Fertigkeit.from_dict_static(data, attribute_dict)
                if fertigkeit:
                    charakter.fertigkeiten[name] = fertigkeit
            
            Logger.info(f"Benutzerdefinierte Fertigkeiten wurden aus {custom_fertigkeiten_file} geladen.")
        except Exception as e:
            Logger.error(f"Fehler beim Laden der benutzerdefinierten Fertigkeiten: {e}")


# Globale Manager-Instanz für Kompatibilität mit altem Code
_eigenschaften_manager = None

def get_eigenschaften_manager():
    """
    Gibt die globale EigenschaftenManager-Instanz zurück.
    
    Returns:
        EigenschaftenManager: Die Manager-Instanz
    """
    global _eigenschaften_manager
    if _eigenschaften_manager is None:
        _eigenschaften_manager = EigenschaftenManager()
    return _eigenschaften_manager


#-----------------------------------------------
# Kompatibilitätsfunktionen für alten Code
#-----------------------------------------------

def initialisiere_attribute(charakter):
    """Kompatibilitätsfunktion - verwendet EigenschaftenManager"""
    return get_eigenschaften_manager().initialisiere_attribute(charakter)

def get_attribute_dict(charakter):
    """Kompatibilitätsfunktion - verwendet EigenschaftenManager"""
    return get_eigenschaften_manager().get_attribute_dict(charakter)

def steigere_attribut(charakter, attribut_name):
    """Kompatibilitätsfunktion - verwendet EigenschaftenManager"""
    return get_eigenschaften_manager().steigere_attribut(charakter, attribut_name)

def senke_attribut(charakter, attribut_name):
    """Kompatibilitätsfunktion - verwendet EigenschaftenManager"""
    return get_eigenschaften_manager().senke_attribut(charakter, attribut_name)

def initialisiere_fertigkeiten(charakter):
    """Kompatibilitätsfunktion - verwendet EigenschaftenManager"""
    return get_eigenschaften_manager().initialisiere_fertigkeiten(charakter)

def steigere_fertigkeit(charakter, fertigkeit_name, confirm_double_cost=False):
    """Kompatibilitätsfunktion - verwendet EigenschaftenManager"""
    return get_eigenschaften_manager().steigere_fertigkeit(charakter, fertigkeit_name, confirm_double_cost)

def senke_fertigkeit(charakter, fertigkeit_name):
    """Kompatibilitätsfunktion - verwendet EigenschaftenManager"""
    return get_eigenschaften_manager().senke_fertigkeit(charakter, fertigkeit_name)

def add_fertigkeit(charakter, fertigkeit):
    """Kompatibilitätsfunktion - verwendet EigenschaftenManager"""
    return get_eigenschaften_manager().add_fertigkeit(charakter, fertigkeit)

def remove_fertigkeit(charakter, fertigkeit_name):
    """Kompatibilitätsfunktion - verwendet EigenschaftenManager"""
    return get_eigenschaften_manager().remove_fertigkeit(charakter, fertigkeit_name)

def save_custom_fertigkeiten(charakter):
    """Kompatibilitätsfunktion - verwendet EigenschaftenManager"""
    return get_eigenschaften_manager().save_custom_fertigkeiten(charakter)

def load_custom_fertigkeiten(charakter):
    """Kompatibilitätsfunktion - verwendet EigenschaftenManager"""
    return get_eigenschaften_manager().load_custom_fertigkeiten(charakter)