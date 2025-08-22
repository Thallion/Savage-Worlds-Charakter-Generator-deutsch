"""
Modul für die Verwaltung von Handicaps im Charakter.
Dieses Modul enthält die HandicapManager-Klasse zur Verwaltung von Handicaps, 
einschließlich des Auswahlens, Abwählens und Speicherns benutzerdefinierter Handicaps.

Refactored mit HandicapManager Klasse nach DDD, SOLID und Clean Code Prinzipien.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from kivy.logger import Logger
from models.handicap import Handicap


class HandicapManager:
    """
    Manager-Klasse für die zentrale Verwaltung von Handicaps.
    Implementiert das Single Responsibility Principle und kapselt die Handicap-Logik.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialisiert den HandicapManager mit Konfiguration.
        
        Args:
            config_path: Pfad zur handicap_config.json (optional)
        """
        self.config = self._load_config(config_path)
        self._cache_config_values()
        
    def _load_config(self, config_path: Optional[Path] = None) -> Dict:
        """
        Lädt die Handicap-Konfiguration aus einer JSON-Datei.
        
        Args:
            config_path: Pfad zur Konfigurationsdatei
            
        Returns:
            Dict mit der Konfiguration
        """
        if config_path is None:
            # Standard-Pfad relativ zu diesem Modul
            config_path = Path(__file__).parent.parent / 'config' / 'handicap_config.json'
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                Logger.warning(f"Config-Datei nicht gefunden: {config_path}. Verwende Standardwerte.")
                return self._get_default_config()
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Config: {e}. Verwende Standardwerte.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """
        Gibt die Standard-Konfiguration zurück, falls keine Config-Datei vorhanden ist.
        
        Returns:
            Dict mit Standardwerten
        """
        return {
            "handicap_effects": {
                "Alt": {
                    "schwer": {
                        "fertigkeitssteigerungen_bonus": 5,
                        "bewegungsweite_malus": 1
                    }
                },
                "Arm": {
                    "leicht": {
                        "vermoegen_modifikator": 0.5
                    }
                },
                "Jung": {
                    "leicht": {
                        "attributsteigerungen": 4,
                        "fertigkeitssteigerungen": 10
                    },
                    "schwer": {
                        "attributsteigerungen": 3,
                        "fertigkeitssteigerungen": 10
                    }
                }
            },
            "standard_werte": {
                "max_handicap_punkte": 4,
                "punkte_leicht": 1,
                "punkte_schwer": 2,
                "standard_attributsteigerungen": 5,
                "standard_fertigkeitssteigerungen": 12
            },
            "nicht_duplizierbare_handicaps": [
                "Alt", "Jung", "Blind", "Einarmig", "Einäugig", 
                "Stumm", "Analphabet", "Klein", "Fettleibig", "Langsam"
            ]
        }
    
    def _cache_config_values(self):
        """Cache häufig verwendete Konfigurationswerte für bessere Performance."""
        self.max_handicap_punkte = self.config['standard_werte']['max_handicap_punkte']
        self.nicht_duplizierbare_handicaps = set(self.config['nicht_duplizierbare_handicaps'])
        self.handicap_effects = self.config['handicap_effects']
        self.standard_werte = self.config['standard_werte']
    
    def initialisiere_handicaps(self, charakter, handicap_daten: List[Dict]):
        """
        Initialisiert die Handicaps des Charakters basierend auf der bereitgestellten Liste.
        
        Args:
            charakter: Das Charakter-Objekt, dem die Handicaps hinzugefügt werden sollen
            handicap_daten: Die Handicap-Daten als Liste von Dictionaries
        """
        charakter.handicaps = {}
        try:
            for daten in handicap_daten:
                name = daten.get('Name', '')
                stufe = daten.get('Stufe', '').lower()
                beschreibung = daten.get('Beschreibung', 'Keine Beschreibung verfügbar')

                # Immer ein eindeutiger Schlüssel mit Name und Stufe
                name_key = f"{name} ({stufe})"

                # Initialisiere das Handicap
                handicap = charakter.Handicap(
                    name=name,  # Name ohne Stufe
                    stufe=stufe,
                    beschreibung=beschreibung
                )
                charakter.handicaps[name_key] = handicap
            Logger.debug("Handicaps erfolgreich initialisiert.")
        except Exception as e:
            Logger.error(f"Fehler bei der Initialisierung der Handicaps: {e}")

    def waehle_handicap(self, charakter, handicap_name_key: str) -> bool:
        """
        Wählt ein Handicap aus und verrechnet die Handicap-Punkte.
        Wenn das Handicap bereits ausgewählt ist, wird eine neue Instanz mit Suffix erstellt.
        
        Args:
            charakter: Das Charakter-Objekt
            handicap_name_key: Der Schlüssel des Handicaps in der handicaps-Dictionary
            
        Returns:
            True bei Erfolg, False bei Misserfolg
        """
        if handicap_name_key not in charakter.handicaps:
            Logger.error(f"Handicap '{handicap_name_key}' existiert nicht.")
            return False
            
        handicap = charakter.handicaps[handicap_name_key]
        
        # Prüfe ob dieses spezifische Handicap bereits ausgewählt ist
        if handicap.ausgewaehlt:
            # Prüfe ob Handicap duplizierbar ist
            handicap_basis_name = handicap.name
            if handicap_basis_name in self.nicht_duplizierbare_handicaps:
                Logger.warning(f"Handicap '{handicap_basis_name}' kann nicht dupliziert werden.")
                return False
            
            # Finde einen freien Suffix für eine neue Instanz
            new_key = self._finde_freien_handicap_key(charakter, handicap_name_key)
            
            # Erstelle eine Kopie des Handicaps
            new_handicap = handicap.clone()
            new_handicap.ausgewaehlt = False
            
            # Füge das neue Handicap hinzu
            charakter.handicaps[new_key] = new_handicap
            Logger.info(f"Neue Instanz von Handicap '{handicap.name}' mit Key '{new_key}' erstellt")
            
            # Wähle die neue Instanz aus
            return self.waehle_handicap(charakter, new_key)
        
        # Normale Verarbeitung für noch nicht ausgewählte Handicaps
        neue_gesamtpunkte = charakter.gesamt_handicap_punkte + handicap.punkte     
        Logger.info(f"neue_gesamtpunkte '{neue_gesamtpunkte} Kosten: {handicap.punkte} Gesamt {charakter.gesamt_handicap_punkte}")
        
        if neue_gesamtpunkte <= self.max_handicap_punkte:           
            handicap.auswaehlen()
            charakter.gesamt_handicap_punkte = neue_gesamtpunkte
            charakter.verbleibende_handicap_punkte += handicap.punkte  
            charakter.verbleibende_handicap_punkte = min(charakter.verbleibende_handicap_punkte, self.max_handicap_punkte) 
            charakter.selected_handicaps.append(handicap_name_key)
            
            # Handicap-spezifische Effekte anwenden
            self._apply_handicap_effects(charakter, handicap)
            
            Logger.info(f"Handicap '{handicap_name_key}' ausgewählt.")
            Logger.info(f"verbleibend '{charakter.verbleibende_handicap_punkte} Kosten: {handicap.punkte} Gesamt {charakter.gesamt_handicap_punkte}")
            charakter.selected_handicaps = charakter.selected_handicaps  # Neu zuweisen
            
            # Abgeleitete Werte neu berechnen
            charakter.berechne_abgeleitete_werte()
            
            return True
        else:
            # Spezialbehandlung für 5. Punkt (wird auf 4 begrenzt)
            if neue_gesamtpunkte == 5:
                handicap.auswaehlen()
                charakter.selected_handicaps.append(handicap_name_key)
                
                # Handicap-spezifische Effekte anwenden
                self._apply_handicap_effects(charakter, handicap)
                
                charakter.gesamt_handicap_punkte = self.max_handicap_punkte
                charakter.verbleibende_handicap_punkte += handicap.punkte 
                charakter.verbleibende_handicap_punkte = min(charakter.verbleibende_handicap_punkte, self.max_handicap_punkte)
                Logger.info(f"verbleibend '{charakter.verbleibende_handicap_punkte} Kosten: {handicap.punkte} Gesamt {charakter.gesamt_handicap_punkte}")
                charakter.selected_handicaps = charakter.selected_handicaps
                Logger.warning(f"Handicap '{handicap_name_key}' ausgewählt. Handicap-punkte nicht erhöht, da Maximum von 4 erreicht.")
                
                # Abgeleitete Werte neu berechnen
                charakter.berechne_abgeleitete_werte()
                
                return True
            else:
                Logger.warning(f"Handicap '{handicap_name_key}' kann nicht ausgewählt werden. Maximum überschritten.")
                return False

    def _finde_freien_handicap_key(self, charakter, base_key: str) -> str:
        """
        Findet einen freien Schlüssel für ein dupliziertes Handicap.
        
        Args:
            charakter: Das Charakter-Objekt
            base_key: Der Basis-Schlüssel des Handicaps
            
        Returns:
            Ein freier Schlüssel für das neue Handicap
        """
        # Entferne eventuell vorhandenen Suffix
        if '_' in base_key and base_key.split('_')[-1].isdigit():
            base_key = '_'.join(base_key.split('_')[:-1])
        
        suffix = 2
        new_key = f"{base_key}_{suffix}"
        
        while new_key in charakter.handicaps:
            suffix += 1
            new_key = f"{base_key}_{suffix}"
        
        return new_key

    def _apply_handicap_effects(self, charakter, handicap: Handicap):
        """
        Wendet die Effekte eines Handicaps auf den Charakter an.
        Verwendet die Konfiguration für die Effekte.
        
        Args:
            charakter: Das Charakter-Objekt
            handicap: Das Handicap-Objekt
        """
        handicap_name = handicap.name
        stufe = handicap.stufe
        
        # Prüfe ob Effekte in der Config definiert sind
        if handicap_name in self.handicap_effects:
            if stufe in self.handicap_effects[handicap_name]:
                effects = self.handicap_effects[handicap_name][stufe]
                
                # Alt (schwer) - Mehr Fertigkeitspunkte
                if 'fertigkeitssteigerungen_bonus' in effects:
                    bonus = effects['fertigkeitssteigerungen_bonus']
                    charakter.verbleibende_fertigkeitssteigerungen += bonus
                    charakter.maximale_fertigkeitssteigerungen += bonus
                    Logger.info(f"Handicap '{handicap_name} ({stufe})': +{bonus} Fertigkeitssteigerungen")
                
                # Arm (leicht) - Halbiertes Vermögen
                if 'vermoegen_modifikator' in effects:
                    from functions.ausruestung_funktionen import anpassen_vermoegen_bei_handicap_arm
                    anpassen_vermoegen_bei_handicap_arm(charakter, True)
                    Logger.info(f"Handicap '{handicap_name} ({stufe})': Vermögen angepasst")
                
                # Jung - Anpassung der Steigerungen
                if 'attributsteigerungen' in effects:
                    charakter.verbleibende_attributsteigerungen = effects['attributsteigerungen']
                    charakter.maximale_attributsteigerungen = effects['attributsteigerungen']
                    Logger.info(f"Handicap '{handicap_name} ({stufe})': Attributsteigerungen={effects['attributsteigerungen']}")
                
                if 'fertigkeitssteigerungen' in effects:
                    charakter.verbleibende_fertigkeitssteigerungen = effects['fertigkeitssteigerungen']
                    charakter.maximale_fertigkeitssteigerungen = effects['fertigkeitssteigerungen']
                    Logger.info(f"Handicap '{handicap_name} ({stufe})': Fertigkeitssteigerungen={effects['fertigkeitssteigerungen']}")

    def _remove_handicap_effects(self, charakter, handicap: Handicap):
        """
        Macht die Effekte eines Handicaps rückgängig.
        Verwendet die Konfiguration für die Effekte.
        
        Args:
            charakter: Das Charakter-Objekt
            handicap: Das Handicap-Objekt
        """
        handicap_name = handicap.name
        stufe = handicap.stufe
        
        # Prüfe ob Effekte in der Config definiert sind
        if handicap_name in self.handicap_effects:
            if stufe in self.handicap_effects[handicap_name]:
                effects = self.handicap_effects[handicap_name][stufe]
                
                # Alt (schwer) - Fertigkeitspunkte zurücknehmen
                if 'fertigkeitssteigerungen_bonus' in effects:
                    bonus = effects['fertigkeitssteigerungen_bonus']
                    charakter.verbleibende_fertigkeitssteigerungen -= bonus
                    charakter.maximale_fertigkeitssteigerungen -= bonus
                    charakter.verbleibende_fertigkeitssteigerungen = max(charakter.verbleibende_fertigkeitssteigerungen, 0)
                    Logger.info(f"Handicap '{handicap_name} ({stufe})' entfernt: -{bonus} Fertigkeitssteigerungen")
                
                # Arm (leicht) - Vermögen zurücksetzen
                if 'vermoegen_modifikator' in effects:
                    from functions.ausruestung_funktionen import anpassen_vermoegen_bei_handicap_arm
                    anpassen_vermoegen_bei_handicap_arm(charakter, False)
                    Logger.info(f"Handicap '{handicap_name} ({stufe})' entfernt: Vermögen zurückgesetzt")
                
                # Jung - Standardwerte wiederherstellen
                if 'attributsteigerungen' in effects or 'fertigkeitssteigerungen' in effects:
                    charakter.verbleibende_attributsteigerungen = self.standard_werte['standard_attributsteigerungen']
                    charakter.maximale_attributsteigerungen = self.standard_werte['standard_attributsteigerungen']
                    charakter.verbleibende_fertigkeitssteigerungen = self.standard_werte['standard_fertigkeitssteigerungen']
                    charakter.maximale_fertigkeitssteigerungen = self.standard_werte['standard_fertigkeitssteigerungen']
                    Logger.info(f"Handicap '{handicap_name}' entfernt: Steigerungen auf Standardwerte zurückgesetzt")

    def entferne_handicap(self, charakter, handicap_name_key: str, force_remove: bool = False) -> bool:
        """
        Entfernt ein Handicap. Nach der Charaktergenerierung kostet dies Aufstiege.
        
        Args:
            charakter: Das Charakter-Objekt
            handicap_name_key: Der Schlüssel des Handicaps
            force_remove: Erzwingt das Entfernen ohne Kosten
            
        Returns:
            True bei Erfolg, False bei Misserfolg
        """
        if handicap_name_key not in charakter.handicaps:
            Logger.error(f"Handicap '{handicap_name_key}' existiert nicht.")
            return False
            
        handicap = charakter.handicaps[handicap_name_key]
        
        if not handicap.ausgewaehlt:
            Logger.warning(f"Handicap '{handicap_name_key}' ist nicht ausgewählt.")
            return False
        
        # Prüfe ob genug Aufstiege vorhanden sind (wenn nicht force_remove)
        if not force_remove and getattr(charakter, 'char_gen_completed', False):
            kosten = self.config.get('kosten_entfernung', {}).get(handicap.stufe, 1)
            if getattr(charakter, 'verfuegbare_aufstiege', 0) < kosten:
                Logger.warning(f"Nicht genug Aufstiege zum Entfernen von '{handicap_name_key}' (benötigt: {kosten})")
                return False
            charakter.verfuegbare_aufstiege -= kosten
        
        # Entferne das Handicap
        handicap.abwaehlen()
        charakter.gesamt_handicap_punkte -= handicap.punkte
        charakter.verbleibende_handicap_punkte -= handicap.punkte
        charakter.verbleibende_handicap_punkte = max(charakter.verbleibende_handicap_punkte, 0)
        
        if handicap_name_key in charakter.selected_handicaps:
            charakter.selected_handicaps.remove(handicap_name_key)
        
        # Effekte rückgängig machen
        self._remove_handicap_effects(charakter, handicap)
        
        Logger.info(f"Handicap '{handicap_name_key}' entfernt.")
        
        # Abgeleitete Werte neu berechnen
        charakter.berechne_abgeleitete_werte()
        
        return True

    def aktive_handicaps(self, charakter) -> List[Handicap]:
        """Gibt eine Liste aller aktiven Handicaps zurück."""
        return [handicap for handicap in charakter.handicaps.values() if handicap.aktiv]

    def ausgewaehlte_handicaps(self, charakter) -> List[Handicap]:
        """Gibt eine Liste aller ausgewählten Handicaps zurück."""
        return [handicap for handicap in charakter.handicaps.values() if handicap.ausgewaehlt]

    def add_handicap(self, charakter, handicap: Handicap) -> bool:
        """Fügt ein neues Handicap hinzu."""
        handicap_key = f"{handicap.name} ({handicap.stufe})"
        if handicap_key in charakter.handicaps:
            Logger.warning(f"Handicap '{handicap_key}' existiert bereits.")
            return False
        
        charakter.handicaps[handicap_key] = handicap
        Logger.info(f"Handicap '{handicap_key}' hinzugefügt.")
        return True

    def remove_handicap(self, charakter, handicap_name: str) -> bool:
        """Entfernt ein Handicap vollständig aus der Liste."""
        if handicap_name not in charakter.handicaps:
            Logger.error(f"Handicap '{handicap_name}' existiert nicht.")
            return False
        
        handicap = charakter.handicaps[handicap_name]
        
        # Wenn ausgewählt, erst abwählen
        if handicap.ausgewaehlt:
            self.entferne_handicap(charakter, handicap_name, force_remove=True)
        
        # Aus Dictionary entfernen
        del charakter.handicaps[handicap_name]
        Logger.info(f"Handicap '{handicap_name}' vollständig entfernt.")
        return True


# Globale Instanz des HandicapManagers
_handicap_manager = HandicapManager()

# Wrapper-Funktionen für Rückwärtskompatibilität  
def initialisiere_handicaps(charakter, handicap_daten):
    """Wrapper für Rückwärtskompatibilität."""
    return _handicap_manager.initialisiere_handicaps(charakter, handicap_daten)

def waehle_handicap(charakter, handicap_name_key):
    """Wrapper für Rückwärtskompatibilität."""
    return _handicap_manager.waehle_handicap(charakter, handicap_name_key)

def entferne_handicap(charakter, handicap_name_key, force_remove=False):
    """Wrapper für Rückwärtskompatibilität."""
    return _handicap_manager.entferne_handicap(charakter, handicap_name_key, force_remove)

def aktive_handicaps(charakter):
    """Wrapper für Rückwärtskompatibilität."""
    return _handicap_manager.aktive_handicaps(charakter)

def ausgewaehlte_handicaps(charakter):
    """Wrapper für Rückwärtskompatibilität."""
    return _handicap_manager.ausgewaehlte_handicaps(charakter)

def add_handicap(charakter, handicap):
    """Wrapper für Rückwärtskompatibilität."""
    return _handicap_manager.add_handicap(charakter, handicap)

def remove_handicap(charakter, handicap_name):
    """Wrapper für Rückwärtskompatibilität."""
    return _handicap_manager.remove_handicap(charakter, handicap_name)

# Private Hilfsfunktionen (werden noch benötigt)
def _apply_handicap_effects(charakter, handicap):
    """Wrapper für Rückwärtskompatibilität."""
    return _handicap_manager._apply_handicap_effects(charakter, handicap)

def _remove_handicap_effects(charakter, handicap):
    """Wrapper für Rückwärtskompatibilität."""
    return _handicap_manager._remove_handicap_effects(charakter, handicap)

# Zusätzliche Funktionen für bestehende Funktionalität
def reduziere_handicap(charakter, handicap_name_key):
    """
    Reduziert ein schweres Handicap zu einem leichten Handicap.
    Diese Funktion wird beibehalten da sie spezielle Logik enthält.
    """
    if handicap_name_key not in charakter.handicaps:
        Logger.error(f"Handicap '{handicap_name_key}' existiert nicht.")
        return False
        
    handicap = charakter.handicaps[handicap_name_key]
    
    if not handicap.ausgewaehlt:
        Logger.warning(f"Handicap '{handicap_name_key}' ist nicht ausgewählt.")
        return False
        
    if handicap.stufe != "schwer":
        Logger.warning(f"Handicap '{handicap_name_key}' ist nicht schwer und kann nicht reduziert werden.")
        return False
    
    # Suche das leichte Handicap mit gleichem Namen
    leichtes_handicap_key = None
    leichtes_handicap = None
    
    for key, other_handicap in charakter.handicaps.items():
        if (other_handicap.name == handicap.name and 
            other_handicap.stufe == "leicht"):
            leichtes_handicap_key = key
            leichtes_handicap = other_handicap
            Logger.debug(f"Leichtes Handicap gefunden: '{key}'")
            break
    
    if not leichtes_handicap:
        Logger.error(f"Kein leichtes Handicap für '{handicap.name}' gefunden.")
        return False
    
    # Nach Charaktergenerierung kostet es 1 Aufstieg
    if getattr(charakter, 'char_gen_completed', False):
        if getattr(charakter, 'verbleibende_aufstiege', 0) < 1:
            Logger.warning("Nicht genügend Aufstiege für Handicap-Reduzierung.")
            return "needs_advancement"
        charakter.verbleibende_aufstiege -= 1
    else:
        # Während der Charaktergenerierung: Punkte anpassen
        charakter.gesamt_handicap_punkte -= 1
        charakter.gesamt_handicap_punkte = max(charakter.gesamt_handicap_punkte, 0)
        charakter.verbleibende_handicap_punkte -= 1
        charakter.verbleibende_handicap_punkte = max(charakter.verbleibende_handicap_punkte, 0)
    
    # Schweres Handicap entfernen
    handicap.abwaehlen()
    _handicap_manager._remove_handicap_effects(charakter, handicap)
    if handicap_name_key in charakter.selected_handicaps:
        charakter.selected_handicaps.remove(handicap_name_key)
    
    # Leichtes Handicap aktivieren
    leichtes_handicap.auswaehlen()
    _handicap_manager._apply_handicap_effects(charakter, leichtes_handicap)
    if leichtes_handicap_key not in charakter.selected_handicaps:
        charakter.selected_handicaps.append(leichtes_handicap_key)
    
    # Listen neu zuweisen für UI-Update
    charakter.selected_handicaps = charakter.selected_handicaps
    
    # Abgeleitete Werte neu berechnen
    charakter.berechne_abgeleitete_werte()
    
    Logger.info(f"Handicap '{handicap.name}' von schwer auf leicht reduziert.")
    
    return True

# Custom Handicaps Funktionen
def save_custom_handicaps(charakter):
    """Speichert benutzerdefinierte Handicaps."""
    try:
        custom_handicaps = {
            name: handicap.to_dict() 
            for name, handicap in charakter.handicaps.items() 
            if getattr(handicap, 'custom', False)
        }
        
        if hasattr(charakter, 'custom_element_manager'):
            charakter.custom_element_manager.save_custom_element('handicaps', custom_handicaps)
        
        Logger.info(f"Benutzerdefinierte Handicaps gespeichert: {len(custom_handicaps)} Einträge")
    except Exception as e:
        Logger.error(f"Fehler beim Speichern benutzerdefinierter Handicaps: {e}")

def load_custom_handicaps(charakter):
    """Lädt benutzerdefinierte Handicaps."""
    try:
        if hasattr(charakter, 'custom_element_manager'):
            custom_handicaps = charakter.custom_element_manager.load_custom_element('handicaps')
            
            for name, data in custom_handicaps.items():
                if name not in charakter.handicaps:
                    handicap = Handicap.from_dict_static(data)
                    if handicap:
                        handicap.custom = True
                        charakter.handicaps[name] = handicap
            
            Logger.info(f"Benutzerdefinierte Handicaps geladen: {len(custom_handicaps)} Einträge")
    except Exception as e:
        Logger.error(f"Fehler beim Laden benutzerdefinierter Handicaps: {e}")

def get_handicap_manager() -> HandicapManager:
    """Gibt die globale HandicapManager-Instanz zurück."""
    return _handicap_manager