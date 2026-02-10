"""
Modul für die Verwaltung von Talenten im Charakter.
Dieses Modul enthält die TalentManager-Klasse zur zentralen Verwaltung der Charakter-Talente,
einschließlich der Auswahl, Abwahl und Überprüfung der Voraussetzungen.
ERWEITERT: Mit Savage Pathfinder Support für kostenlose Klassen-/Hintergrund-/Experte-Talente
REFACTORED: Mit TalentManager-Klasse für bessere Struktur und SOLID-Prinzipien
"""

import json
import os
import re
from pathlib import Path
from kivy.logger import Logger
from models.talent import Talent
from functions.macht_funktionen import entferne_macht


class TalentConfig:
    """Konfigurationsklasse für Talent-Einstellungen"""
    
    _config = None
    _config_path = None
    
    @classmethod
    def load_config(cls):
        """Lädt die Konfiguration aus der JSON-Datei"""
        if cls._config is None:
            if cls._config_path is None:
                cls._config_path = Path(__file__).parent.parent / 'config' / 'talent_config.json'
            
            try:
                if os.path.exists(cls._config_path):
                    with open(cls._config_path, 'r', encoding='utf-8') as f:
                        cls._config = json.load(f)
                        Logger.info(f"Talent-Konfiguration geladen von {cls._config_path}")
                else:
                    Logger.warning(f"Config-Datei nicht gefunden: {cls._config_path}, verwende Standardwerte")
                    cls._config = cls._get_default_config()
            except Exception as e:
                Logger.error(f"Fehler beim Laden der Talent-Konfiguration: {e}")
                cls._config = cls._get_default_config()
        return cls._config
    
    @classmethod
    def _get_default_config(cls):
        """Gibt die Standard-Konfiguration zurück (Fallback)"""
        return {
            "kosten": {
                "handicap_punkte": 2,
                "min_handicap_punkte": 1.5,
                "aufstieg": 1,
                "pathfinder_max_kostenlose": 1
            },
            "nicht_duplizierbare_talente": [
                "Glück", "Großes Glück", "Reich", "Stinkreich", 
                "Kräftig", "Riesenwuchs", "Klein", "Zäh", "Sehr zäh",
                "Arkaner Hintergrund: Gaben", "Arkaner Hintergrund: Magie", 
                "Arkaner Hintergrund: Psionik", "Arkaner Hintergrund: Wunder",
                "Arkaner Widerstand", "Verbesserte Arkane Resistenz",
                "Meister aller Waffen", "Waffenmeister", "Block", "Harter Block",
                "Schwer zu töten", "Schwerer zu töten", "Schnell", "Flink",
                "Raufbold", "Schläger", "Attraktiv", "Sehr attraktiv"
            ],
            "pathfinder_kostenlose_kategorien": [
                "Klasse", "Hintergrund", "Experte", "Class", "Background", "Expert"
            ],
            "rang_hierarchie": {"A": 1, "F": 2, "V": 3, "H": 4, "L": 5},
            "spezial_talente": {
                "vermoegen_talente": ["Reich", "Stinkreich"],
                "arkane_hintergruende": ["Arkaner Hintergrund: Gaben", "Arkaner Hintergrund: Magie", 
                                       "Arkaner Hintergrund: Psionik", "Arkaner Hintergrund: Wunder"]
            }
        }
    
    @classmethod
    def get(cls, key_path, default=None):
        """
        Holt einen Wert aus der Konfiguration mit Punkt-Notation.
        
        Args:
            key_path: Pfad zum Wert (z.B. "kosten.handicap_punkte")
            default: Standardwert falls Schlüssel nicht existiert
        """
        config = cls.load_config()
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value


class TalentManager:
    """
    Manager-Klasse für Talent-Operationen.
    Kapselt alle Talent-bezogenen Funktionen und befolgt SOLID-Prinzipien.
    """
    
    def __init__(self, charakter):
        """
        Initialisiert den TalentManager.
        
        Args:
            charakter: Das Charakter-Objekt
        """
        self.charakter = charakter
    
    #-----------------------------------------------
    # Hauptmethoden
    #-----------------------------------------------
    
    def waehle_talent(self, talent_name_key, ignore_rang_check=False):
        """
        Wählt ein Talent aus und verrechnet die Kosten entweder mit Handicap-Punkten oder Aufstiegen.
        ERWEITERT: Unterstützt kostenlose Pathfinder-Talente während der Charaktererstellung.
        Wenn das Talent bereits ausgewählt ist, wird eine neue Instanz mit Suffix erstellt.
        
        Args:
            talent_name_key: Der Name des auszuwählenden Talents
            ignore_rang_check: Flag, um die Rang-Prüfung zu überspringen (für UI-Bestätigung)
            
        Returns:
            str oder bool: "needs_rang_confirmation" wenn der Rang zu niedrig ist,
                           "needs_voraussetzungen_confirmation" wenn Voraussetzungen nicht erfüllt sind,
                           "not_duplicatable" wenn Talent nicht duplizierbar ist,
                           "pathfinder_kostenlos_angeboten" wenn kostenloses Pathfinder-Talent möglich ist,
                           True bei Erfolg, False bei Misserfolg
        """
        # Prüfen, ob das Talent existiert
        if talent_name_key not in self.charakter.talente:
            Logger.error(f"Talent '{talent_name_key}' existiert nicht.")
            return False
            
        talent = self.charakter.talente[talent_name_key]
        
        # NEUE LOGIK: Savage Pathfinder kostenlose Talente während Charaktererstellung
        if self._ist_kostenloses_pathfinder_talent_verfuegbar(talent):
            Logger.info(f"Pathfinder-Talent '{talent_name_key}' kann kostenlos gewählt werden.")
            return "pathfinder_kostenlos_angeboten"
        
        # Prüfe ob dieses spezifische Talent bereits ausgewählt ist (für Mehrfachauswahl)
        if talent.ausgewaehlt:
            return self._handle_mehrfachauswahl(talent, talent_name_key, ignore_rang_check)
        
        # WICHTIG: Prüfe erst Rang, dann Voraussetzungen - priorisiere Rangwarnung
        # Rang-Prüfung
        if not ignore_rang_check and self._ist_talent_rang_zu_hoch(talent.rang):
            # Wenn Rang nicht passt, nur Rangwarnung zurückgeben, weitere Prüfungen überspringen
            return "needs_rang_confirmation"
        
        # Voraussetzungsprüfung (nur wenn Rang ok ist)
        voraussetzungen_result = self._pruefe_voraussetzungen_fuer_auswahl(talent, talent_name_key)
        if voraussetzungen_result != "ok":
            return voraussetzungen_result
        
        # Kosten verrechnen und Talent auswählen
        return self._verrechne_talent_kosten(talent_name_key)
    
    def waehle_freies_talent(self, talent_name_key, ignore_voraussetzungen=False):
        """
        Wählt ein Talent als freies Talent ohne Kosten (Aufstiege oder Handicap-Punkte) aus.
        Speziell für Rasseneigenschaften wie das freie Talent der Menschen.
        Wenn das Talent bereits ausgewählt ist, wird eine neue Instanz mit Suffix erstellt.
        
        Args:
            talent_name_key: Der Name des auszuwählenden Talents
            ignore_voraussetzungen: Flag zum Ignorieren der Voraussetzungsprüfung
            
        Returns:
            str oder bool: "needs_voraussetzungen_confirmation" wenn Voraussetzungen nicht erfüllt sind,
                           "not_duplicatable" wenn Talent nicht duplizierbar ist,
                           True bei Erfolg, False bei Misserfolg
        """
        Logger.info(f"Wähle freies Talent: {talent_name_key}")
        
        # Prüfen, ob das Talent existiert
        if talent_name_key not in self.charakter.talente:
            Logger.error(f"Talent '{talent_name_key}' existiert nicht.")
            return False
            
        talent = self.charakter.talente[talent_name_key]
        
        # Prüfe ob dieses spezifische Talent bereits ausgewählt ist (für Mehrfachauswahl)
        if talent.ausgewaehlt:
            # Prüfe ob das Talent duplizierbar ist
            if talent.name in TalentConfig.get('nicht_duplizierbare_talente', []):
                Logger.warning(f"Talent '{talent.name}' kann nicht mehrfach ausgewählt werden.")
                return "not_duplicatable"
            
            # Erstelle neue Instanz für Mehrfachauswahl
            new_key = self._erstelle_neue_talent_instanz(talent, talent_name_key)
            return self.waehle_freies_talent(new_key, ignore_voraussetzungen)
        
        # Voraussetzungsprüfung
        if not ignore_voraussetzungen and not talent.voraussetzungen_erfuellt(self.charakter):
            fehlermeldungen = self.pruefe_voraussetzungen(talent)
            self.charakter.temp_voraussetzungs_fehler = fehlermeldungen
            Logger.debug(f"Rückgabe 'needs_voraussetzungen_confirmation' für {talent_name_key}")
            return "needs_voraussetzungen_confirmation"
        
        # Talent auswählen ohne Kosten
        erfolg = self.talent_auswaehlen(talent_name_key, skip_prereq_check=ignore_voraussetzungen)
        
        if erfolg:
            Logger.info(f"Freies Talent '{talent_name_key}' erfolgreich ausgewählt.")
            self.charakter.berechne_abgeleitete_werte()
            return True
        
        return False
    
    def waehle_pathfinder_kostenloses_talent(self, talent_name_key):
        """
        NEU: Wählt ein kostenloses Pathfinder-Talent während der Charaktererstellung.
        
        Args:
            talent_name_key: Der Name des auszuwählenden Talents
            
        Returns:
            True bei Erfolg, False bei Misserfolg
        """
        if talent_name_key not in self.charakter.talente:
            Logger.error(f"Talent '{talent_name_key}' existiert nicht.")
            return False
        
        talent = self.charakter.talente[talent_name_key]
        
        # Prüfe ob es ein gültiges kostenloses Talent ist
        if not ist_pathfinder_kostenloses_talent(talent):
            Logger.warning(f"Talent '{talent_name_key}' ist kein kostenloses Pathfinder-Talent.")
            return False
        
        # Prüfe ob bereits ein kostenloses Talent gewählt wurde
        if hat_bereits_kostenloses_pathfinder_talent(self.charakter):
            Logger.warning("Es wurde bereits ein kostenloses Pathfinder-Talent gewählt.")
            return False
        
        # Talent auswählen
        erfolg = self.talent_auswaehlen(talent_name_key, skip_prereq_check=False)
        
        if erfolg:
            # Markiere dass ein kostenloses Talent gewählt wurde
            if not hasattr(self.charakter, 'pathfinder_kostenlose_talente_gewaehlt'):
                self.charakter.pathfinder_kostenlose_talente_gewaehlt = 0
            self.charakter.pathfinder_kostenlose_talente_gewaehlt += 1
            Logger.info(f"Kostenloses Pathfinder-Talent '{talent_name_key}' ausgewählt.")
            self.charakter.berechne_abgeleitete_werte()
            return True
        
        return False
    
    def talent_abwaehlen(self, talent_name_key):
        """
        Wählt ein Talent ab und gibt die Ressourcen zurück.
        ERWEITERT: Berücksichtigt kostenlose Pathfinder-Talente.
        
        Args:
            talent_name_key: Der Name des zu entfernenden Talents
            
        Returns:
            True bei Erfolg, False bei Misserfolg
        """
        def talent_abwaehlen_intern():
            talent.abwaehlen(self.charakter)
            self.charakter.verfuegbare_maechte -= talent.neue_maechte
            self.charakter.anzahl_maechte -= talent.neue_maechte
            self.charakter.verfuegbare_maechte = max(self.charakter.verfuegbare_maechte, 0)  # Nicht negativ
            self.charakter.senke_machtpunkte(talent.machtpunkte)
            
            # Spezielle Anpassungen für Reich/Stinkreich
            vermoegen_talente = TalentConfig.get('spezial_talente.vermoegen_talente', ["Reich", "Stinkreich"])
            if talent_name_key in vermoegen_talente:
                from functions.ausruestung_funktionen import anpassen_vermoegen_bei_talent_reich
                anpassen_vermoegen_bei_talent_reich(self.charakter, talent_name_key, False)  # False = wird abgewählt
            
            if talent_name_key in self.charakter.selected_talente:
                self.charakter.selected_talente.remove(talent_name_key)
            Logger.debug(f"Talent '{talent_name_key}' entfernt.")
        
        # Hauptlogik
        if talent_name_key not in self.charakter.talente:
            Logger.error(f"Talent '{talent_name_key}' nicht gefunden.")
            return False
        
        talent = self.charakter.talente[talent_name_key]
        
        if not talent.ausgewaehlt:
            Logger.warning(f"Talent '{talent_name_key}' ist nicht ausgewählt.")
            return False
        
        # NEU: Prüfe ob es ein kostenloses Pathfinder-Talent ist
        if (ist_savage_pathfinder_setting(self.charakter) and 
            ist_pathfinder_kostenloses_talent(talent) and
            hasattr(self.charakter, 'pathfinder_kostenlose_talente_gewaehlt') and
            self.charakter.pathfinder_kostenlose_talente_gewaehlt > 0):
            
            # Reduziere Zähler für kostenlose Talente
            self.charakter.pathfinder_kostenlose_talente_gewaehlt -= 1
            talent_abwaehlen_intern()
            Logger.info(f"Kostenloses Pathfinder-Talent '{talent_name_key}' abgewählt.")
            return True
        
        # Mächte entfernen wenn ein Arkaner Hintergrund abgewählt wird
        if talent.name.startswith("Arkaner Hintergrund"):
            while self.charakter.maechte:
                macht_name = next(iter(self.charakter.maechte))
                entferne_macht(self.charakter, macht_name)
        
        talent_abwaehlen_intern()
        
        # Ressourcen zurückgeben (Aufstiege oder Handicap-Punkte)
        if hasattr(self.charakter, 'verbleibende_aufstiege'):
            self.charakter.verbleibende_aufstiege += 1
        
        self.charakter.berechne_abgeleitete_werte()
        return True
    
    def talent_auswaehlen(self, talent_name_key, skip_prereq_check=False):
        """
        Wählt ein Talent aus und führt die entsprechenden Anpassungen am Charakter durch.
        
        Args:
            talent_name_key: Der Name des auszuwählenden Talents
            skip_prereq_check: Voraussetzungsprüfung überspringen (default: False)
            
        Returns:
            True bei Erfolg, False bei Misserfolg
        """
        talent = self.charakter.talente.get(talent_name_key)
        if talent:
            if not talent.ausgewaehlt:
                # WICHTIG: Hier die Bedingung anpassen
                # Wenn skip_prereq_check True ist, überspringen wir die Voraussetzungsprüfung vollständig
                if skip_prereq_check or talent.voraussetzungen_erfuellt(self.charakter):
                    # Talent auswählen und Anpassungen vornehmen
                    talent.ausgewaehlt = True
                    self.charakter.verfuegbare_maechte += talent.neue_maechte
                    self.charakter.anzahl_maechte += talent.neue_maechte
                    self.charakter.erhoehe_machtpunkte(talent.machtpunkte)
                    if talent_name_key not in self.charakter.selected_talente:
                        self.charakter.selected_talente.append(talent_name_key)
                    
                    # Spezielle Anpassungen für Reich/Stinkreich
                    vermoegen_talente = TalentConfig.get('spezial_talente.vermoegen_talente', ["Reich", "Stinkreich"])
                    if talent_name_key in vermoegen_talente:
                        from functions.ausruestung_funktionen import anpassen_vermoegen_bei_talent_reich
                        anpassen_vermoegen_bei_talent_reich(self.charakter, talent_name_key, True)  # True = wird ausgewählt
                    
                    Logger.info(f"Talent '{talent_name_key}' ausgewählt.")
                    
                    # Abgeleitete Werte neu berechnen (ohne Vermögensberechnung)
                    self.charakter.berechne_abgeleitete_werte()
                    
                    return True
                else:
                    pass
                    #Logger.warning(f"Voraussetzungen für Talent '{talent_name_key}' nicht erfüllt.")
            else:
                Logger.warning(f"Talent '{talent_name_key}' ist bereits ausgewählt.")
        else:
            Logger.error(f"Talent '{talent_name_key}' existiert nicht.")
        return False
    
    def pruefe_voraussetzungen(self, talent):
        """
        Prüft alle Voraussetzungen eines Talents und gibt eine Liste von Fehlermeldungen zurück.
        
        Args:
            talent: Das zu prüfende Talent-Objekt
            
        Returns:
            Liste von Fehlermeldungen (leer wenn alle Voraussetzungen erfüllt sind)
        """
        fehlermeldungen = []
        
        if not talent.voraussetzungen:
            return fehlermeldungen
        
        for voraussetzung in talent.voraussetzungen:
            # Spezialfall: "AH" oder "Arkaner Hintergrund (beliebig)" - beliebiger Arkaner Hintergrund
            if voraussetzung == "AH" or voraussetzung == "Arkaner Hintergrund (beliebig)":
                hat_arkanen_hintergrund = False
                for talent_name, talent_obj in self.charakter.talente.items():
                    if talent_name.startswith("Arkaner Hintergrund") and talent_obj.ausgewaehlt:
                        hat_arkanen_hintergrund = True
                        break

                if not hat_arkanen_hintergrund:
                    fehlermeldungen.append("Ein beliebiger Arkaner Hintergrund (AH) wird vorausgesetzt.")
                continue

            # Spezialfall: "AH (XYZ)" - spezifischer Arkaner Hintergrund in Kurzform
            ah_kurz_match = re.match(r'^AH \((.+)\)$', voraussetzung)
            if ah_kurz_match:
                ah_name = ah_kurz_match.group(1)
                full_name = f"Arkaner Hintergrund ({ah_name})"
                talent_obj = self.charakter.talente.get(full_name)
                if not talent_obj or not talent_obj.ausgewaehlt:
                    fehlermeldungen.append(f"'{full_name}' muss ausgewählt sein.")
                continue

            # Spezialfall: "Arkaner Hintergrund (jeder außer X)" - beliebiger AH außer einem bestimmten
            ausser_match = re.match(r'^Arkaner Hintergrund \(jeder außer (.+)\)$', voraussetzung)
            if ausser_match:
                ausgeschlossener_ah = ausser_match.group(1).strip()
                hat_passenden_ah = False
                for talent_name, talent_obj in self.charakter.talente.items():
                    if (talent_name.startswith("Arkaner Hintergrund") and
                            talent_obj.ausgewaehlt and
                            talent_name != f"Arkaner Hintergrund ({ausgeschlossener_ah})"):
                        hat_passenden_ah = True
                        break
                if not hat_passenden_ah:
                    fehlermeldungen.append(
                        f"Ein beliebiger Arkaner Hintergrund außer {ausgeschlossener_ah} wird vorausgesetzt."
                    )
                continue

            # Spezialfall: "Arkaner Hintergrund (X, Y, Z)" - einer aus einer Liste von AHs
            if voraussetzung.startswith("Arkaner Hintergrund (") and "," in voraussetzung:
                inner = voraussetzung[len("Arkaner Hintergrund ("):-1]
                ah_namen = [name.strip() for name in inner.split(",")]
                hat_passenden_ah = False
                for ah_name in ah_namen:
                    full_name = f"Arkaner Hintergrund ({ah_name})"
                    talent_obj = self.charakter.talente.get(full_name)
                    if talent_obj and talent_obj.ausgewaehlt:
                        hat_passenden_ah = True
                        break
                if not hat_passenden_ah:
                    fehlermeldungen.append(
                        f"Einer der folgenden Arkanen Hintergründe wird vorausgesetzt: {', '.join(ah_namen)}"
                    )
                continue

            # Attributvoraussetzung (z.B. "STÄ W8" oder "Geschicklichkeit W8")
            attribut_match = re.match(r'^(Geschicklichkeit|Stärke|Konstitution|Verstand|Willenskraft|STÄ|GES|KON|VER|WIL)\s+W(\d+)$', voraussetzung)
            if attribut_match:
                attribut_name_or_kuerzel = attribut_match.group(1)
                wuerfel_wert = int(attribut_match.group(2))

                # Attributkürzel zu vollständigem Namen umwandeln
                attribut_mapping = {
                    'STÄ': 'Stärke',
                    'GES': 'Geschicklichkeit',
                    'KON': 'Konstitution',
                    'VER': 'Verstand',
                    'WIL': 'Willenskraft'
                }
                attribut_name = attribut_mapping.get(attribut_name_or_kuerzel, attribut_name_or_kuerzel)

                attribut = self.charakter.attribute.get(attribut_name)
                if not attribut:
                    fehlermeldungen.append(f"Attribut '{attribut_name}' nicht gefunden.")
                    continue

                if attribut.wert < wuerfel_wert:
                    fehlermeldungen.append(f"Attribut '{attribut_name}' muss mindestens W{wuerfel_wert} sein (aktuell W{attribut.wert}).")

                continue

            # Fertigkeitsvoraussetzung (z.B. "Kämpfen W8")
            fertigkeit_match = re.match(r'^(.+?)\s+W(\d+)$', voraussetzung)
            if fertigkeit_match and not attribut_match:  # Nicht bereits als Attribut erkannt
                fertigkeit_name = fertigkeit_match.group(1)
                wuerfel_wert = int(fertigkeit_match.group(2))

                fertigkeit = self.charakter.fertigkeiten.get(fertigkeit_name)
                if not fertigkeit:
                    fehlermeldungen.append(f"Fertigkeit '{fertigkeit_name}' nicht gefunden.")
                    continue

                if fertigkeit.wert < wuerfel_wert:
                    fehlermeldungen.append(f"Fertigkeit '{fertigkeit_name}' muss mindestens W{wuerfel_wert} sein (aktuell W{fertigkeit.wert}).")

                continue

            # Talentvoraussetzung (z.B. "Glück")
            talent_name = voraussetzung  # Annahme: Wenn keine spezielle Formatierung, handelt es sich um ein Talent

            talent_obj = self.charakter.talente.get(talent_name)
            if not talent_obj:
                fehlermeldungen.append(f"Vorausgesetztes Talent '{talent_name}' wurde nicht gefunden.")
                continue

            if not talent_obj.ausgewaehlt:
                fehlermeldungen.append(f"Vorausgesetztes Talent '{talent_name}' muss ausgewählt sein.")
        
        return fehlermeldungen
    
    #-----------------------------------------------
    # Private Hilfsmethoden
    #-----------------------------------------------
    
    def _ist_kostenloses_pathfinder_talent_verfuegbar(self, talent):
        """
        Prüft ob ein kostenloses Pathfinder-Talent verfügbar ist.
        
        Args:
            talent: Das Talent-Objekt
            
        Returns:
            bool: True wenn verfügbar, sonst False
        """
        return (ist_savage_pathfinder_setting(self.charakter) and 
                not self.charakter.char_gen_completed and 
                ist_pathfinder_kostenloses_talent(talent) and 
                not hat_bereits_kostenloses_pathfinder_talent(self.charakter))
    
    def _handle_mehrfachauswahl(self, talent, talent_name_key, ignore_rang_check):
        """
        Behandelt die Mehrfachauswahl eines bereits ausgewählten Talents.
        
        Args:
            talent: Das Talent-Objekt
            talent_name_key: Der Schlüssel des Talents
            ignore_rang_check: Flag für Rang-Prüfung
            
        Returns:
            str oder Ergebnis der rekursiven waehle_talent Ausführung
        """
        # Prüfe ob das Talent duplizierbar ist
        if talent.name in TalentConfig.get('nicht_duplizierbare_talente', []):
            Logger.warning(f"Talent '{talent.name}' kann nicht mehrfach ausgewählt werden.")
            return "not_duplicatable"
        
        # Erstelle neue Instanz für Mehrfachauswahl
        new_key = self._erstelle_neue_talent_instanz(talent, talent_name_key)
        return self.waehle_talent(new_key, ignore_rang_check)
    
    def _erstelle_neue_talent_instanz(self, talent, talent_name_key):
        """
        Erstellt eine neue Instanz eines Talents für Mehrfachauswahl.
        
        Args:
            talent: Das Original-Talent
            talent_name_key: Der ursprüngliche Schlüssel
            
        Returns:
            str: Der neue Schlüssel für die Talent-Instanz
        """
        base_key = talent_name_key.split('_')[0] if '_' in talent_name_key and talent_name_key.split('_')[-1].isdigit() else talent_name_key
        suffix = 2
        new_key = f"{base_key}_{suffix}"
        
        # Finde den nächsten freien Suffix
        while new_key in self.charakter.talente:
            suffix += 1
            new_key = f"{base_key}_{suffix}"
        
        # Erstelle eine Kopie des Talents mit der clone() Methode
        new_talent = talent.clone()
        new_talent.ausgewaehlt = False  # Zurücksetzen für die neue Instanz
        
        # Füge das neue Talent hinzu
        self.charakter.talente[new_key] = new_talent
        Logger.info(f"Neue Instanz von Talent '{talent.name}' mit Key '{new_key}' erstellt")
        
        return new_key
    
    def _ist_talent_rang_zu_hoch(self, talent_rang):
        """
        Prüft ob der Talentrang höher als der Charakterrang ist.
        
        Args:
            talent_rang: Der Rang des Talents
            
        Returns:
            bool: True wenn zu hoch, sonst False
        """
        return is_talent_rang_hoeher_als_charakter(self.charakter, talent_rang)
    
    def _pruefe_voraussetzungen_fuer_auswahl(self, talent, talent_name_key):
        """
        Prüft Voraussetzungen für die Talentauswahl.
        
        Args:
            talent: Das Talent-Objekt
            talent_name_key: Der Talent-Schlüssel
            
        Returns:
            str: "ok" oder "needs_voraussetzungen_confirmation"
        """
        # Prüfe ob das ignore_voraussetzungen-Flag nicht gesetzt ist
        if not hasattr(self.charakter, 'ignore_voraussetzungen') or not self.charakter.ignore_voraussetzungen:
            fehlermeldungen = self.pruefe_voraussetzungen(talent)
            if fehlermeldungen:
                # Fehlermeldungen als Attribut speichern für UI-Dialog
                self.charakter.temp_voraussetzungs_fehler = fehlermeldungen
                Logger.debug(f"Rückgabe 'needs_voraussetzungen_confirmation' für {talent_name_key}")
                return "needs_voraussetzungen_confirmation"
        return "ok"
    
    def _verrechne_talent_kosten(self, talent_name_key):
        """
        Verrechnet die Kosten für ein Talent (Handicap-Punkte oder Aufstiege).
        
        Args:
            talent_name_key: Der Talent-Schlüssel
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        # Bestimme welche Ressource verwendet werden soll
        min_handicap = TalentConfig.get('kosten.min_handicap_punkte', 1.5)
        if self.charakter.verbleibende_handicap_punkte > min_handicap:
            return self._waehle_mit_handicap_punkten(talent_name_key)
        elif self.charakter.verbleibende_aufstiege > 0:
            return self._waehle_mit_aufstieg(talent_name_key)
        else:
            Logger.warning("Keine verbleibenden Aufstiege oder Handicap-Punkte übrig.")
            return False
    
    def _waehle_mit_handicap_punkten(self, talent_name_key):
        """
        Wählt ein Talent mit Handicap-Punkten aus.
        
        Args:
            talent_name_key: Der Talent-Schlüssel
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        skip_prereq = hasattr(self.charakter, 'ignore_voraussetzungen') and self.charakter.ignore_voraussetzungen
        erfolg = self.talent_auswaehlen(talent_name_key, skip_prereq_check=skip_prereq)
        
        if erfolg:
            kosten = TalentConfig.get('kosten.handicap_punkte', 2)
            self.charakter.verbleibende_handicap_punkte -= kosten
            self._reset_ignore_voraussetzungen_flag(talent_name_key)
            
            # Event für Historie-System senden
            try:
                from services.service_container import service_container
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish('talent_added', {
                        'talent_name': talent_name_key,
                        'cost': kosten,
                        'cost_type': 'Handicap-Punkte'
                    })
            except Exception as e:
                Logger.warning(f"Event-Publishing fehlgeschlagen: {e}")
            
            self.charakter.berechne_abgeleitete_werte()
            return True
        return False
    
    def _waehle_mit_aufstieg(self, talent_name_key):
        """
        Wählt ein Talent mit einem Aufstieg aus.
        
        Args:
            talent_name_key: Der Talent-Schlüssel
            
        Returns:
            bool: True bei Erfolg, False bei Misserfolg
        """
        skip_prereq = hasattr(self.charakter, 'ignore_voraussetzungen') and self.charakter.ignore_voraussetzungen
        erfolg = self.talent_auswaehlen(talent_name_key, skip_prereq_check=skip_prereq)
        
        if erfolg:
            kosten = TalentConfig.get('kosten.aufstieg', 1)
            self.charakter.verbleibende_aufstiege -= kosten
            self.charakter.update_char_gen_status()
            self._reset_ignore_voraussetzungen_flag(talent_name_key)
            
            # Event für Historie-System senden
            try:
                from services.service_container import service_container
                event_service = service_container.get_event_service()
                if event_service:
                    event_service.publish('talent_added', {
                        'talent_name': talent_name_key,
                        'cost': kosten,
                        'cost_type': 'Aufstiege'
                    })
            except Exception as e:
                Logger.warning(f"Event-Publishing fehlgeschlagen: {e}")
            
            self.charakter.berechne_abgeleitete_werte()
            return True
        return False
    
    def _reset_ignore_voraussetzungen_flag(self, talent_name_key):
        """
        Setzt das ignore_voraussetzungen Flag zurück.
        
        Args:
            talent_name_key: Der Talent-Schlüssel für Logging
        """
        if hasattr(self.charakter, 'ignore_voraussetzungen'):
            self.charakter.ignore_voraussetzungen = False
            Logger.debug(f"Flag ignore_voraussetzungen zurückgesetzt nach Auswahl von '{talent_name_key}'")


# Globale Manager-Instanz für Kompatibilität mit altem Code
_talent_manager = None

def get_talent_manager(charakter):
    """
    Gibt eine TalentManager-Instanz für den gegebenen Charakter zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        TalentManager: Die Manager-Instanz
    """
    # Für bessere Performance könnte hier eine Cache-Logik implementiert werden
    return TalentManager(charakter)


#-----------------------------------------------
# Globale Hilfsfunktionen (für Kompatibilität)
#-----------------------------------------------

def ist_savage_pathfinder_setting(charakter):
    """
    Prüft, ob das aktuelle Setting Savage Pathfinder ist.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        bool: True wenn Savage Pathfinder, sonst False
    """
    setting_name = getattr(charakter, 'active_setting_name', '').lower()
    return 'pathfinder' in setting_name or setting_name == 'savage pathfinder'


def ist_pathfinder_kostenloses_talent(talent):
    """
    Prüft, ob ein Talent zu den Kategorien gehört, die in Savage Pathfinder 
    während der Charaktererstellung kostenlos gewählt werden können.
    
    Args:
        talent: Das Talent-Objekt
        
    Returns:
        bool: True wenn Klassen-, Hintergrund- oder Experte-Talent, sonst False
    """
    if not hasattr(talent, 'kategorie') or not talent.kategorie:
        return False
    
    kategorien = TalentConfig.get('pathfinder_kostenlose_kategorien', [])
    return talent.kategorie in kategorien


def hat_bereits_kostenloses_pathfinder_talent(charakter):
    """
    Prüft, ob bereits ein kostenloses Pathfinder-Talent gewählt wurde.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        bool: True wenn bereits ein kostenloses Talent gewählt wurde
    """
    if not hasattr(charakter, 'pathfinder_kostenlose_talente_gewaehlt'):
        charakter.pathfinder_kostenlose_talente_gewaehlt = 0
    
    max_kostenlose = TalentConfig.get('kosten.pathfinder_max_kostenlose', 1)
    return charakter.pathfinder_kostenlose_talente_gewaehlt >= max_kostenlose


def is_talent_rang_hoeher_als_charakter(charakter, talent_rang):
    """
    Prüft, ob der Rang des Talents höher ist als der des Charakters.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_rang: Der Rang des Talents (z.B. 'A', 'F', 'V', 'H', 'L')
        
    Returns:
        bool: True wenn der Talent-Rang höher ist als der Charakter-Rang, sonst False
    """
    rang_hierarchie = TalentConfig.get('rang_hierarchie', {'A': 1, 'F': 2, 'V': 3, 'H': 4, 'L': 5})
    
    charakter_rang = charakter.rang if hasattr(charakter, 'rang') else 'A'
    
    # Normalisieren der Rang-Strings
    charakter_rang = charakter_rang.upper() if charakter_rang else 'A'
    talent_rang = talent_rang.upper() if talent_rang else 'A'
    
    # Falls es längere Bezeichnungen sind, nehme ersten Buchstaben
    if len(charakter_rang) > 1:
        charakter_rang = charakter_rang[0]
    if len(talent_rang) > 1:
        talent_rang = talent_rang[0]
    
    charakter_rang_wert = rang_hierarchie.get(charakter_rang, 1)
    talent_rang_wert = rang_hierarchie.get(talent_rang, 1)
    
    return talent_rang_wert > charakter_rang_wert


#-----------------------------------------------
# Modul-Funktionen (für direkte Verwendung ohne Manager-Instanz)
#-----------------------------------------------

def get_freie_talente(charakter):
    """
    Gibt eine Liste von Talenten zurück, die als freie Talente ausgewählt werden können.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der Namen von freien Talenten
    """
    frei_talente = []
    for talent in charakter.talente.values():
        if not talent.ausgewaehlt and talent.aktiv:
            frei_talente.append(talent.name)
    # Füge einen Platzhalter hinzu, falls keine freien Talente verfügbar sind
    if not frei_talente:
        frei_talente = ['Keine freien Talente verfügbar']
    return frei_talente


def initialisiere_talente(charakter, talent_daten):
    """
    Initialisiert die Talente des Charakters basierend auf der bereitgestellten Liste.
    
    Args:
        charakter: Das Charakter-Objekt, dem die Talente hinzugefügt werden sollen
        talent_daten: Die Talent-Daten als Dictionary
    """
    try:
        for kategorie, talente in talent_daten.items():
            for name, daten in talente.items():
                talent = Talent(
                    name=name,
                    kategorie=kategorie,
                    rang=daten.get('Rang', ''),
                    voraussetzungen=daten.get('Voraussetzungen', []),
                    beschreibung=daten.get('Beschreibung', ''),
                    neue_maechte=daten.get('neue_maechte', 0),
                    machtpunkte=daten.get('machtpunkte', 0)
                )
                charakter.talente[name] = talent
    except Exception as e:
        Logger.error(f"Fehler bei der Initialisierung der Talente: {e}")


def ausgewaehlte_talente(charakter):
    """
    Gibt eine Liste aller ausgewählten Talente zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der ausgewählten Talente
    """
    return [talent for talent in charakter.talente.values() if talent.ausgewaehlt]


def aktive_talente(charakter):
    """
    Gibt eine Liste aller aktiven Talente zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der aktiven Talente
    """
    return [talent for talent in charakter.talente.values() if talent.aktiv]


def add_talent(charakter, talent):
    """
    Fügt ein Talent zur aktiven Einstellung hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
        talent: Das hinzuzufügende Talent-Objekt
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    charakter.talente[talent.name] = talent
    charakter.custom_element_manager.update_element('talente', talent.name, talent.to_dict())
    return True


def remove_talent(charakter, talent_name):
    """
    Entfernt ein Talent aus der aktiven Einstellung.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name: Der Name des zu entfernenden Talents
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if talent_name in charakter.talente:
        del charakter.talente[talent_name]
        charakter.custom_element_manager.remove_element('talente', talent_name)
        return True
    return False


def save_custom_talents(charakter):
    """
    Speichert die benutzerdefinierten Talente in einer JSON-Datei.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    import json
    import os
    
    # Finde die benutzerdefinierten Talente
    custom_talente = {name: talent.to_dict() for name, talent in charakter.talente.items() if getattr(talent, 'custom', False)}
    if custom_talente:
        custom_talente_file = os.path.join(os.path.dirname(__file__), 'custom_talente.json')
        try:
            with open(custom_talente_file, 'w', encoding='utf-8') as f:
                json.dump(custom_talente, f, ensure_ascii=False, indent=4)
            Logger.info(f"Benutzerdefinierte Talente wurden in {custom_talente_file} gespeichert.")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der benutzerdefinierten Talente: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Talente zum Speichern.")


def load_custom_talents(charakter):
    """
    Lädt die benutzerdefinierten Talente aus einer JSON-Datei und fügt sie der Talentliste hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    import json
    import os
    
    custom_talente_file = os.path.join(os.path.dirname(__file__), 'custom_talente.json')
    if os.path.exists(custom_talente_file):
        try:
            with open(custom_talente_file, 'r', encoding='utf-8') as f:
                custom_talents_data = json.load(f)
            for name, data in custom_talents_data.items():
                talent = Talent.from_dict_static(data)
                charakter.talente[name] = talent
            Logger.info(f"Benutzerdefinierte Talente wurden aus {custom_talente_file} geladen.")
        except Exception as e:
            Logger.error(f"Fehler beim Laden der benutzerdefinierten Talente: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Talente zum Laden gefunden.")


#-----------------------------------------------
# Kompatibilitätsfunktionen für alten Code
#-----------------------------------------------

def waehle_talent(charakter, talent_name_key, ignore_rang_check=False):
    """Kompatibilitätsfunktion - verwendet TalentManager"""
    return get_talent_manager(charakter).waehle_talent(talent_name_key, ignore_rang_check)

def waehle_freies_talent(charakter, talent_name_key, ignore_voraussetzungen=False):
    """Kompatibilitätsfunktion - verwendet TalentManager"""
    return get_talent_manager(charakter).waehle_freies_talent(talent_name_key, ignore_voraussetzungen)

def waehle_pathfinder_kostenloses_talent(charakter, talent_name_key):
    """Kompatibilitätsfunktion - verwendet TalentManager"""
    return get_talent_manager(charakter).waehle_pathfinder_kostenloses_talent(talent_name_key)

def talent_abwaehlen(charakter, talent_name_key):
    """Kompatibilitätsfunktion - verwendet TalentManager"""
    return get_talent_manager(charakter).talent_abwaehlen(talent_name_key)

def talent_auswaehlen(charakter, talent_name_key, skip_prereq_check=False):
    """Kompatibilitätsfunktion - verwendet TalentManager"""
    return get_talent_manager(charakter).talent_auswaehlen(talent_name_key, skip_prereq_check)

def pruefe_voraussetzungen(charakter, talent):
    """Kompatibilitätsfunktion - verwendet TalentManager"""
    return get_talent_manager(charakter).pruefe_voraussetzungen(talent)

# Aliases für Rückwärtskompatibilität mit alten Funktionsnamen
entferne_talent = talent_abwaehlen

# Legacy-Konstante für Rückwärtskompatibilität mit Views
# Diese wird von views/talente_view.py importiert
NICHT_DUPLIZIERBARE_TALENTE = TalentConfig.get('nicht_duplizierbare_talente', [])