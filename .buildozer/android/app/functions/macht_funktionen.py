"""
Modul für die Verwaltung von Mächten im Charakter.
Dieses Modul enthält die MachtManager-Klasse zur Verwaltung von Mächten, 
einschließlich des Auswahlens, Abwählens und Speicherns benutzerdefinierter Mächte.
"""

import json
import os
from pathlib import Path
from kivy.logger import Logger
from models.macht import Macht


class MachtManager:
    """
    Manager-Klasse für die Verwaltung von Mächten.
    Implementiert das Single Responsibility Principle und kapselt alle Macht-bezogenen Operationen.
    """
    
    def __init__(self):
        """Initialisiert den MachtManager und lädt die Konfiguration."""
        self.config = self._load_config()
        self.rang_werte = self._prepare_rang_werte()
        
    def _load_config(self):
        """
        Lädt die Konfiguration aus der JSON-Datei.
        
        Returns:
            dict: Die geladene Konfiguration oder Standard-Werte bei Fehler
        """
        config_path = Path(__file__).parent.parent / 'config' / 'macht_config.json'
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                Logger.warning(f"Konfigurationsdatei nicht gefunden: {config_path}")
                return self._get_default_config()
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Konfiguration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self):
        """
        Gibt die Standard-Konfiguration zurück.
        
        Returns:
            dict: Standard-Konfigurationswerte
        """
        return {
            "rang_werte": {
                "vollstaendige_namen": {
                    "anfänger": 1,
                    "fortgeschritten": 2,
                    "veteran": 3,
                    "heroisch": 4,
                    "legendär": 5
                },
                "abkuerzungen": {
                    "a": 1,
                    "f": 2,
                    "v": 3,
                    "h": 4,
                    "l": 5
                },
                "englische_bezeichnungen": {
                    "novice": 1,
                    "seasoned": 2,
                    "veteran": 3,
                    "heroic": 4,
                    "legendary": 5
                }
            },
            "dateipfade": {
                "custom_maechte_file": "custom_maechte.json"
            },
            "standard_werte": {
                "fallback_rang": "a",
                "fallback_rang_wert": 1,
                "debug_logging": true
            }
        }
    
    def _prepare_rang_werte(self):
        """
        Bereitet die Rang-Werte aus der Konfiguration vor.
        
        Returns:
            dict: Kombinierte Rang-Werte aus allen Kategorien
        """
        rang_werte = {}
        
        # Alle Rang-Kategorien aus der Config zusammenführen
        for kategorie in self.config.get("rang_werte", {}).values():
            if isinstance(kategorie, dict):
                rang_werte.update(kategorie)
                
        return rang_werte
    
    def initialisiere_maechte(self, charakter, maechte_daten):
        """
        Initialisiert die Mächte des Charakters basierend auf den bereitgestellten Daten.
        
        Args:
            charakter: Das Charakter-Objekt, dem die Mächte hinzugefügt werden sollen
            maechte_daten: Die Macht-Daten als Dictionary
        """
        charakter.maechte = {}
        try:
            for name, daten in maechte_daten.items():
                if not self._validate_macht_daten(daten):
                    Logger.warning(f"Ungültige oder fehlende Daten für Macht '{name}': {daten}")
                    continue
                    
                macht = self._create_macht_from_data(charakter, name, daten)
                charakter.maechte[name] = macht
                
            Logger.debug("Mächte erfolgreich initialisiert.")
        except Exception as e:
            Logger.error(f"Fehler bei der Initialisierung der Mächte: {e}")
    
    def _validate_macht_daten(self, daten):
        """
        Validiert die Macht-Daten.
        
        Args:
            daten: Die zu validierenden Daten
            
        Returns:
            bool: True wenn Daten valide, sonst False
        """
        required_fields = ['Rang', 'Machtpunkte', 'Reichweite', 'Dauer']
        return all(key in daten for key in required_fields)
    
    def _create_macht_from_data(self, charakter, name, daten):
        """
        Erstellt ein Macht-Objekt aus den Daten.
        
        Args:
            charakter: Das Charakter-Objekt
            name: Name der Macht
            daten: Daten der Macht
            
        Returns:
            Macht: Das erstellte Macht-Objekt
        """
        return charakter.Macht(
            name=name,
            rang=daten.get('Rang', ''),
            machtpunkte=daten.get('Machtpunkte', 0),
            reichweite=daten.get('Reichweite', ''),
            dauer=daten.get('Dauer', ''),
            effekt=daten.get('Effekt', ''),
            beschreibung=daten.get('Beschreibung', ''),
            voraussetzungen=daten.get('Voraussetzungen', [])
        )
    
    def is_macht_rang_hoeher_als_charakter(self, charakter, macht_rang):
        """
        Prüft, ob der Rang der Macht höher ist als der des Charakters.
        
        Args:
            charakter: Das Charakter-Objekt
            macht_rang: Der Rang der Macht als String
            
        Returns:
            bool: True, wenn der Macht-Rang höher ist, sonst False
        """
        Logger.debug(f"Rangprüfung - Charakter-Rang: '{charakter.rang}', Macht-Rang: '{macht_rang}'")
        
        # Normalisieren auf Kleinbuchstaben
        charakter_rang = charakter.rang.lower()
        macht_rang = macht_rang.lower() if macht_rang else self.config["standard_werte"]["fallback_rang"]
        
        # Rang-Werte abrufen
        charakter_rang_wert = self._get_rang_wert(charakter_rang)
        macht_rang_wert = self._get_rang_wert(macht_rang)
        
        Logger.debug(f"Rangprüfung - Charakter-Wert: {charakter_rang_wert}, Macht-Wert: {macht_rang_wert}")
        
        # Vergleich durchführen
        is_higher = macht_rang_wert > charakter_rang_wert
        Logger.debug(f"Rangprüfung - Ergebnis: {is_higher} (Macht-Rang {'>' if is_higher else '<='} Charakter-Rang)")
        
        return is_higher
    
    def _get_rang_wert(self, rang):
        """
        Gibt den numerischen Wert eines Rangs zurück.
        
        Args:
            rang: Der Rang als String
            
        Returns:
            int: Der numerische Rang-Wert
        """
        # Direkte Übereinstimmung suchen
        if rang in self.rang_werte:
            return self.rang_werte[rang]
        
        # Versuche ersten Buchstaben
        if rang and rang[0] in self.rang_werte:
            return self.rang_werte[rang[0]]
        
        # Fallback auf Anfänger
        return self.config["standard_werte"]["fallback_rang_wert"]
    
    def waehle_macht(self, charakter, macht_name_key, ignore_rang_check=False):
        """
        Wählt eine Macht aus und aktualisiert die verfügbaren Mächte des Charakters.
        
        Args:
            charakter: Das Charakter-Objekt
            macht_name_key: Der Name der Macht
            ignore_rang_check: Flag, um die Rang-Prüfung zu überspringen (für UI-Bestätigung)
            
        Returns:
            str oder bool: "needs_rang_confirmation" wenn der Rang zu niedrig ist,
                           True bei Erfolg, False bei Misserfolg
        """
        if not self._can_select_macht(charakter):
            Logger.warning("Keine verfügbaren Mächte mehr zum Auswählen.")
            return False
            
        if macht_name_key not in charakter.maechte:
            Logger.error(f"Macht '{macht_name_key}' existiert nicht.")
            return False
            
        macht = charakter.maechte[macht_name_key]
        
        if macht.ausgewaehlt:
            Logger.warning(f"Macht '{macht_name_key}' ist bereits ausgewählt.")
            return False
        
        # Rangprüfung
        if not ignore_rang_check and self.is_macht_rang_hoeher_als_charakter(charakter, macht.rang):
            return "needs_rang_confirmation"
        
        # Voraussetzungen prüfen
        if not macht.voraussetzungen_erfuellt(charakter):
            Logger.warning(f"Voraussetzungen für Macht '{macht_name_key}' nicht erfüllt.")
            return False
        
        # Macht auswählen
        return self._select_macht(charakter, macht, macht_name_key)
    
    def _can_select_macht(self, charakter):
        """
        Prüft, ob noch Mächte ausgewählt werden können.
        
        Args:
            charakter: Das Charakter-Objekt
            
        Returns:
            bool: True wenn Mächte verfügbar, sonst False
        """
        return charakter.verfuegbare_maechte > 0
    
    def _select_macht(self, charakter, macht, macht_name_key):
        """
        Führt die eigentliche Auswahl einer Macht durch.
        
        Args:
            charakter: Das Charakter-Objekt
            macht: Das Macht-Objekt
            macht_name_key: Der Name der Macht
            
        Returns:
            bool: True bei Erfolg
        """
        macht.auswaehlen()
        charakter.verfuegbare_maechte -= 1
        charakter.selected_maechte.append(macht_name_key)
        charakter.selected_maechte = charakter.selected_maechte  # Neu zuweisen für Kivy
        Logger.debug(f"Macht '{macht_name_key}' wurde ausgewählt.")
        return True
    
    def entferne_macht(self, charakter, macht_name_key, adjust_verfuegbare_maechte=True):
        """
        Entfernt eine Macht und erhöht optional die verfügbaren Mächte des Charakters.
        
        Args:
            charakter: Das Charakter-Objekt
            macht_name_key: Der Name der Macht
            adjust_verfuegbare_maechte: Ob die verfügbaren Mächte angepasst werden sollen
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        if macht_name_key not in charakter.maechte:
            Logger.error(f"Macht '{macht_name_key}' existiert nicht.")
            return False
            
        macht = charakter.maechte[macht_name_key]
        
        if not macht.ausgewaehlt:
            Logger.warning(f"Macht '{macht_name_key}' ist nicht ausgewählt.")
            return False
        
        # Macht abwählen
        macht.abwaehlen()
        
        # Verfügbare Mächte anpassen
        if adjust_verfuegbare_maechte:
            charakter.verfuegbare_maechte += 1
            
        # Aus selected_maechte entfernen
        if macht_name_key in charakter.selected_maechte:
            charakter.selected_maechte.remove(macht_name_key)
            charakter.selected_maechte = charakter.selected_maechte  # Neu zuweisen
            
        Logger.debug(f"Macht '{macht_name_key}' wurde entfernt.")
        return True
    
    def aktive_maechte(self, charakter):
        """
        Gibt eine Liste aller aktiven Mächte zurück.
        
        Args:
            charakter: Das Charakter-Objekt
            
        Returns:
            list: Liste der aktiven Mächte
        """
        return [macht for macht in charakter.maechte.values() if macht.aktiv]
    
    def ausgewaehlte_maechte(self, charakter):
        """
        Gibt eine Liste aller ausgewählten Mächte zurück.
        
        Args:
            charakter: Das Charakter-Objekt
            
        Returns:
            list: Liste der ausgewählten Mächte
        """
        return [macht for macht in charakter.maechte.values() if macht.ausgewaehlt]
    
    def add_macht(self, charakter, macht):
        """
        Fügt eine neue Macht hinzu.
        
        Args:
            charakter: Das Charakter-Objekt
            macht: Das Macht-Objekt, das hinzugefügt werden soll
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        if macht.name in charakter.maechte:
            Logger.warning(f"Macht '{macht.name}' existiert bereits.")
            return False
            
        charakter.maechte[macht.name] = macht
        Logger.info(f"Macht '{macht.name}' hinzugefügt.")
        self.save_custom_maechte(charakter)
        return True
    
    def remove_macht(self, charakter, macht_name):
        """
        Entfernt eine Macht vollständig aus der Liste.
        
        Args:
            charakter: Das Charakter-Objekt
            macht_name: Der Name der zu entfernenden Macht
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        if macht_name not in charakter.maechte:
            Logger.warning(f"Macht '{macht_name}' existiert nicht.")
            return False
            
        del charakter.maechte[macht_name]
        Logger.info(f"Macht '{macht_name}' entfernt.")
        self.save_custom_maechte(charakter)
        return True
    
    def erhoehe_machtpunkte(self, charakter, punkte):
        """
        Erhöht die Machtpunkte des Charakters.
        
        Args:
            charakter: Das Charakter-Objekt
            punkte: Die Anzahl der hinzuzufügenden Machtpunkte
        """
        charakter.machtpunkte += punkte
        Logger.debug(f"Machtpunkte um {punkte} erhöht. Neue Anzahl: {charakter.machtpunkte}")
    
    def senke_machtpunkte(self, charakter, punkte):
        """
        Verringert die Machtpunkte des Charakters.
        
        Args:
            charakter: Das Charakter-Objekt
            punkte: Die Anzahl der abzuziehenden Machtpunkte
        """
        charakter.machtpunkte = max(0, charakter.machtpunkte - punkte)
        Logger.debug(f"Machtpunkte um {punkte} gesenkt. Neue Anzahl: {charakter.machtpunkte}")
    
    def save_custom_maechte(self, charakter):
        """
        Speichert die benutzerdefinierten Mächte in einer JSON-Datei.
        
        Args:
            charakter: Das Charakter-Objekt
        """
        custom_maechte = self._get_custom_maechte(charakter)
        
        if not custom_maechte:
            Logger.info("Keine benutzerdefinierten Mächte zum Speichern.")
            return
            
        custom_maechte_file = self._get_custom_maechte_path()
        
        try:
            with open(custom_maechte_file, 'w', encoding='utf-8') as f:
                json.dump(custom_maechte, f, ensure_ascii=False, indent=4)
            Logger.info(f"Benutzerdefinierte Mächte wurden in {custom_maechte_file} gespeichert.")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der benutzerdefinierten Mächte: {e}")
    
    def _get_custom_maechte(self, charakter):
        """
        Sammelt alle benutzerdefinierten Mächte.
        
        Args:
            charakter: Das Charakter-Objekt
            
        Returns:
            dict: Dictionary mit benutzerdefinierten Mächten
        """
        return {
            name: macht.to_dict() 
            for name, macht in charakter.maechte.items() 
            if getattr(macht, 'custom', False)
        }
    
    def _get_custom_maechte_path(self):
        """
        Gibt den Pfad zur custom_maechte.json zurück.
        
        Returns:
            Path: Pfad zur Datei
        """
        filename = self.config["dateipfade"]["custom_maechte_file"]
        return Path(__file__).parent / filename
    
    def load_custom_maechte(self, charakter):
        """
        Lädt die benutzerdefinierten Mächte aus einer JSON-Datei.
        
        Args:
            charakter: Das Charakter-Objekt
        """
        custom_maechte_file = self._get_custom_maechte_path()
        
        if not custom_maechte_file.exists():
            Logger.info("Keine benutzerdefinierten Mächte zum Laden gefunden.")
            return
            
        try:
            with open(custom_maechte_file, 'r', encoding='utf-8') as f:
                custom_maechte_data = json.load(f)
                
            for name, data in custom_maechte_data.items():
                macht = Macht.from_dict_static(data)
                charakter.maechte[name] = macht
                
            Logger.info(f"Benutzerdefinierte Mächte wurden aus {custom_maechte_file} geladen.")
        except Exception as e:
            Logger.error(f"Fehler beim Laden der benutzerdefinierten Mächte: {e}")


# Globale Instanz des MachtManagers für Kompatibilität
_macht_manager = MachtManager()

# Wrapper-Funktionen für Rückwärtskompatibilität
def initialisiere_maechte(charakter, maechte_daten):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.initialisiere_maechte(charakter, maechte_daten)

def is_macht_rang_hoeher_als_charakter(charakter, macht_rang):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.is_macht_rang_hoeher_als_charakter(charakter, macht_rang)

def waehle_macht(charakter, macht_name_key, ignore_rang_check=False):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.waehle_macht(charakter, macht_name_key, ignore_rang_check)

def entferne_macht(charakter, macht_name_key, adjust_verfuegbare_maechte=True):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.entferne_macht(charakter, macht_name_key, adjust_verfuegbare_maechte)

def aktive_maechte(charakter):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.aktive_maechte(charakter)

def ausgewaehlte_maechte(charakter):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.ausgewaehlte_maechte(charakter)

def add_macht(charakter, macht):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.add_macht(charakter, macht)

def remove_macht(charakter, macht_name):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.remove_macht(charakter, macht_name)

def erhoehe_machtpunkte(charakter, punkte):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.erhoehe_machtpunkte(charakter, punkte)

def senke_machtpunkte(charakter, punkte):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.senke_machtpunkte(charakter, punkte)

def save_custom_maechte(charakter):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.save_custom_maechte(charakter)

def load_custom_maechte(charakter):
    """Wrapper für Rückwärtskompatibilität."""
    return _macht_manager.load_custom_maechte(charakter)