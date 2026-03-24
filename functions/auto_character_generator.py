#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO CHARACTER GENERATOR - ÜBERARBEITETE VERSION
Universelle Funktion zur automatischen Charaktergenerierung aus JSON-Templates.
- Ignoriert Voraussetzungen bei Talenten und Mächten
- Erhöht automatisch Punkte wenn benötigt
- Erstellt detailliertes Log-File mit Kostenauswertung
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Union, Optional, Any
import logging

# Projekt-Root zum Python-Path hinzufügen
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Imports
from models.charakter import Charakter
from functions.setting_funktionen import CustomElementManager
from functions.charakter_speicher import speichern_als_json
from functions.talent_funktionen import waehle_talent, waehle_freies_talent
from functions.handicap_funktionen import waehle_handicap

# Setup Logging
logger = logging.getLogger(__name__)


class CharacterGenerationError(Exception):
    """Custom Exception für Charaktergenerierungs-Fehler"""
    pass


class AutoCharacterGenerator:
    """
    Universeller Charaktergenerator für Savage Worlds.
    Generiert Charaktere aus JSON-Templates mit vollständiger API-Integration.
    ÜBERARBEITET: Ignoriert Voraussetzungen und erhöht automatisch Punkte.
    """

    def __init__(self):
        self.generated_characters = []
        self.generation_log = []
        self.cost_log = {}  # Detailliertes Kosten-Log
        self.auto_added_points = 0  # Automatisch hinzugefügte Punkte

    def generate_from_template(self, template: Union[str, Dict, Path],
                               custom_setting: Optional[str] = None,
                               output_dir: Optional[str] = None) -> Path:
        """
        Generiert einen Charakter aus einem JSON-Template.

        Args:
            template: JSON-Template als Dict, JSON-String oder Dateipfad
            custom_setting: Überschreibt das Setting aus dem Template
            output_dir: Überschreibt den Ausgabeordner

        Returns:
            Path: Pfad zur gespeicherten JSON-Datei

        Raises:
            CharacterGenerationError: Bei Fehlern in der Generierung
        """
        try:
            # Reset der Kosten-Logs
            self.cost_log = {
                'attribute': [],
                'fertigkeiten': [],
                'talente': [],
                'handicaps': [],
                'maechte': [],
                'auto_punkte': 0,
                'gesamt': {}
            }
            self.auto_added_points = 0

            # Template laden und validieren
            template_data = self._load_template(template)
            self._validate_template(template_data)
            
            # Template für späteren Zugriff speichern
            self.current_template = template_data

            # Generierungsoptionen
            options = template_data.get('generation_options', {})
            # WICHTIG: strict_points IMMER auf False setzen für automatische Punkteerhöhung
            strict_points = False  # Überschreiben - wir ignorieren Punktelimits
            allow_over_attr = True  # Fertigkeiten über Attribut erlauben
            auto_save = options.get('auto_save', True)

            char_name = template_data['name']
            self.log(f"🎯 STARTE CHARAKTERGENERIERUNG: {char_name.upper()}")
            self.log(f"⚙️ MODUS: Automatische Punkteerhöhung aktiv, Voraussetzungen werden ignoriert")

            # SCHRITT 1: CHARAKTER INITIALISIEREN
            setting_name = custom_setting or template_data.get('setting', 'SWAE')
            charakter = self._initialize_character(template_data, setting_name)

            # SCHRITT 2: VOLK UND VÖLKER-BONI
            race_name = template_data.get('race', 'Mensch')
            free_race_edge = self._apply_race(charakter, race_name, template_data)

            # SCHRITT 3: HANDICAPS HINZUFÜGEN (für Punkte)
            handicaps = template_data['handicaps']
            handicap_points = self._add_handicaps_unlimited(charakter, handicaps)

            # SCHRITT 4: ATTRIBUTE STEIGERN (mit originalen Savage Worlds Funktionen)
            target_attributes = template_data['attributes']
            attr_costs = self._advance_attributes_with_original_functions(charakter, target_attributes)

            # SCHRITT 5: FERTIGKEITEN STEIGERN (mit originalen Savage Worlds Funktionen)
            target_skills = template_data['skills']
            skill_costs = self._advance_skills_with_original_functions(charakter, target_skills)

            # SCHRITT 6: TALENTE WÄHLEN (ohne Voraussetzungen)
            edges = template_data['edges']
            edge_costs = self._select_edges_unlimited(charakter, edges, free_race_edge)

            # SCHRITT 7: MÄCHTE WÄHLEN (ohne Voraussetzungen)
            powers = template_data.get('powers', [])
            power_points = template_data.get('power_points', 0)
            if powers or power_points > 0:
                self._select_powers_unlimited(charakter, powers, power_points)

            # SCHRITT 8: AUSRÜSTUNG HINZUFÜGEN
            equipment = template_data.get('equipment', [])
            self._add_equipment(charakter, equipment)

            # SCHRITT 9: TEMPLATE-AUFSTIEGE ANWENDEN
            advances_to_apply = template_data.get('advances_to_apply', [])
            if advances_to_apply:
                self._apply_template_advances(charakter, advances_to_apply)

            # SCHRITT 10: CHARAKTERGENERIERUNG ABSCHLIESSEN
            complete_char_gen = options.get('complete_character_generation', False)
            if complete_char_gen or self._should_complete_character_generation(charakter):
                self._complete_character_generation(charakter)

            # FINALE BERECHNUNGEN
            try:
                charakter.berechne_abgeleitete_werte()
            except RecursionError:
                self.log("⚠️ Warnung: Rekursionsproblem bei abgeleiteten Werten übersprungen")

            # SELECTED_ LISTEN AKTUALISIEREN
            self._update_selected_lists(charakter)

            # CHARAKTERZUSAMMENFASSUNG
            self._print_character_summary_with_costs(charakter, attr_costs, skill_costs,
                                                     edge_costs, handicap_points)

            # KOSTEN-LOG ERSTELLEN
            cost_log_path = self._create_cost_log_file(charakter, char_name, output_dir)
            
            # HISTORIE VIEW INTEGRATION
            self._integrate_with_historie_view(charakter, char_name, cost_log_path)

            # SPEICHERN
            output_path = None
            if auto_save:
                save_dir = output_dir or options.get('save_path', 'auto_generated')
                output_path = self._save_character(charakter, char_name, save_dir)

            self.generated_characters.append(charakter)
            self.log(f"🎉 CHARAKTERGENERIERUNG ERFOLGREICH ABGESCHLOSSEN: {char_name}")

            return output_path

        except Exception as e:
            error_msg = f"Fehler bei der Charaktergenerierung: {e}"
            self.log(f"❌ {error_msg}")
            raise CharacterGenerationError(error_msg) from e

    def _load_template(self, template: Union[str, Dict, Path]) -> Dict:
        """Lädt Template aus verschiedenen Quellen"""
        if isinstance(template, dict):
            return template
        elif isinstance(template, (str, Path)):
            template_path = Path(template)
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Versuche als JSON-String zu parsen
                try:
                    return json.loads(str(template))
                except json.JSONDecodeError:
                    raise CharacterGenerationError(f"Ungültiges Template: {template}")
        else:
            raise CharacterGenerationError(f"Unbekannter Template-Typ: {type(template)}")

    def _validate_template(self, template: Dict) -> None:
        """Validiert das Template"""
        required_fields = ['name', 'attributes', 'skills', 'handicaps', 'edges']
        for field in required_fields:
            if field not in template:
                raise CharacterGenerationError(f"Pflichtfeld fehlt im Template: {field}")

    def _initialize_character(self, template: Dict, setting_name: str) -> Charakter:
        """Initialisiert den Charakter"""
        self.log("--- SCHRITT 1: CHARAKTER INITIALISIEREN ---")

        char_name = template['name']
        description = template.get('description', '')
        profile = template.get('profile', {})

        charakter = Charakter(
            active_setting_name=setting_name,
            char_name=char_name,
            alter=profile.get('age', ''),
            geschlecht=profile.get('gender', ''),
            konzept=profile.get('concept', ''),
            sprachen=profile.get('languages', '')
        )

        charakter.beschreibung = description
        charakter.custom_element_manager = CustomElementManager(charakter, setting_name=setting_name)
        charakter.custom_element_manager.set_active_setting(setting_name)

        # WICHTIG: Punkte aus Template oder Standard-Werte verwenden
        starting_attribute_points = template.get('starting_attribute_points', 5)
        starting_skill_points = template.get('starting_skill_points', 12) 
        starting_capital = template.get('starting_capital', 500)
        starting_advances = template.get('starting_advances', 0)
        
        charakter.verbleibende_attributsteigerungen = starting_attribute_points
        charakter.verbleibende_fertigkeitssteigerungen = starting_skill_points
        charakter.verbleibende_handicap_punkte = 0  # Wird später durch Handicaps erhöht
        
        # Startkapital setzen - immer als geld-Attribut
        charakter.geld = starting_capital
        if hasattr(charakter, 'taler'):
            charakter.taler = starting_capital
            
        # Aufstiege setzen falls vorhanden
        if starting_advances > 0:
            charakter.aufstiege_gesamt = starting_advances
            charakter.verbleibende_aufstiege = 0  # Werden durch Template-Aufstiege verwaltet

        self.log(f"  ✅ Charakter '{char_name}' initialisiert (Setting: {setting_name})")
        self.log(f"  💰 Punkte gesetzt: {starting_attribute_points} Attribut, {starting_skill_points} Fertigkeiten")
        self.log(f"  💎 Startkapital: {starting_capital}")
        if starting_advances > 0:
            self.log(f"  ⭐ Aufstiege: {starting_advances}")
        return charakter

    def _apply_race(self, charakter: Charakter, race_name: str, template: Dict) -> Optional[str]:
        """Wendet Völker-Auswahl und -Boni an"""
        self.log("--- SCHRITT 2: VOLK UND VÖLKER-BONI ---")

        self.log(f"  🎭 Volk gewählt: {race_name}")

        # Völker-Boni vorbereiten
        free_race_edge = template.get('free_race_edge', '')
        if race_name == 'Mensch' and not free_race_edge:
            if not hasattr(charakter, 'voelker_boni'):
                charakter.voelker_boni = {}
            charakter.voelker_boni['freie_talente'] = 1
            self.log("  🎁 Menschen-Bonus: 1 kostenloses Anfänger-Talent vorbereitet")
        elif free_race_edge:
            self.log(f"  🎁 Völker-Talent festgelegt: {free_race_edge}")

        return free_race_edge

    def _advance_attributes_unlimited(self, charakter: Charakter, target_attrs: Dict[str, int]) -> int:
        """
        Steigert Attribute auf Zielwerte - MIT automatischer Punkteerhöhung
        """
        self.log("--- SCHRITT 3: ATTRIBUTE STEIGERN (UNLIMITED) ---")

        total_costs = 0
        start_points = 5  # Standard SWAE

        # Automatisch Punkte hinzufügen wenn nötig
        needed_points = self._calculate_attribute_points_needed(charakter, target_attrs)
        if needed_points > start_points:
            additional_points = needed_points - start_points
            charakter.verbleibende_attributsteigerungen += additional_points
            self.auto_added_points += additional_points
            self.cost_log['auto_punkte'] += additional_points
            self.log(f"  💰 Automatisch {additional_points} Attributspunkte hinzugefügt")

        for attr_name, target_value in target_attrs.items():
            if attr_name not in charakter.attribute:
                self.log(f"  ❌ Attribut '{attr_name}' existiert nicht")
                continue

            attr = charakter.attribute[attr_name]
            current_value = attr.wuerfel.value

            if current_value >= target_value:
                self.log(f"  ✅ {attr_name} bereits auf W{target_value}")
                continue

            # Steigere das Attribut
            advances_needed = self._calculate_advances_needed(current_value, target_value)
            cost = advances_needed

            self.log(f"  📈 {attr_name}: W{current_value} → W{target_value} ({cost} Punkte)")

            for i in range(advances_needed):
                success = charakter.steigere_attribut(attr_name)
                if success:
                    new_value = attr.wuerfel.value
                    self.cost_log['attribute'].append({
                        'name': attr_name,
                        'von': current_value,
                        'nach': new_value,
                        'kosten': 1
                    })
                else:
                    self.log(f"    ⚠️ Steigerung {i + 1} fehlgeschlagen - füge Punkte hinzu")
                    charakter.verbleibende_attributsteigerungen += 1
                    self.auto_added_points += 1
                    success = charakter.steigere_attribut(attr_name)

            total_costs += cost

        self.log(f"📊 ATTRIBUTSKOSTEN GESAMT: {total_costs} Punkte")
        return total_costs

    def _add_handicaps_unlimited(self, charakter: Charakter, handicaps: List[str]) -> int:
        """
        Fügt Handicaps hinzu - MIT automatischer Anpassung wenn nötig
        """
        self.log("--- SCHRITT 4: HANDICAPS HINZUFÜGEN (UNLIMITED) ---")

        total_points = 0

        for handicap_entry in handicaps:
            added = False

            # Unterstütze sowohl Strings als auch Dicts (aus Template-Wizard)
            if isinstance(handicap_entry, dict):
                handicap_name = handicap_entry.get("key", handicap_entry.get("name", ""))
            else:
                handicap_name = handicap_entry

            # Suche in vorhandenen Handicaps
            for key, handicap_obj in charakter.handicaps.items():
                if handicap_name.lower() in key.lower():
                    success = waehle_handicap(charakter, key)
                    if success:
                        points = getattr(handicap_obj, 'punkte', getattr(handicap_obj, 'wert', 1))
                        total_points += points
                        self.cost_log['handicaps'].append({
                            'name': handicap_name,
                            'punkte': points
                        })
                        self.log(f"  ✅ {handicap_name} hinzugefügt (+{points} Punkte)")
                        added = True
                        break
                    else:
                        self.log(f"  ⚠️ {handicap_name} konnte nicht gewählt werden - wird trotzdem markiert")
                        # Trotzdem als ausgewählt markieren
                        if hasattr(handicap_obj, 'ausgewaehlt'):
                            handicap_obj.ausgewaehlt = True
                        points = getattr(handicap_obj, 'punkte', getattr(handicap_obj, 'wert', 1))
                        total_points += points
                        self.cost_log['handicaps'].append({
                            'name': handicap_name,
                            'punkte': points,
                            'erzwungen': True
                        })
                        added = True
                        break

            if not added:
                self.log(f"  ❌ Handicap '{handicap_name}' nicht gefunden")

        self.log(f"📊 HANDICAP-PUNKTE GESAMT: +{total_points} Punkte")
        
        # WICHTIG: Handicap-Punkte auf den Charakter setzen für die originalen Funktionen
        charakter.verbleibende_handicap_punkte = total_points
        self.log(f"💰 Handicap-Punkte auf Charakter gesetzt: {total_points}")
        
        # Log wofür die Handicap-Punkte verwendet werden können
        if total_points > 0:
            self.log(f"💰 Handicap-Punkte können verwendet werden für:")
            self.log(f"   • 2 Punkte = 1 Attributsteigerung")
            self.log(f"   • 2 Punkte = 1 Anfänger-Talent")
            self.log(f"   • 1 Punkt = 1 Fertigkeitssteigerung")
            self.log(f"   • 1 Punkt = Startgeld erhöhen")
            self.log(f"   → {total_points} Handicap-Punkte = {total_points // 2} Attribute oder {total_points} Fertigkeiten oder {total_points // 2} Talente")
        
        return total_points

    def _advance_attributes_with_original_functions(self, charakter: Charakter, target_attrs: Dict[str, int]) -> int:
        """
        Steigert Attribute auf Zielwerte mit den originalen Savage Worlds Funktionen.
        Verwendet 2 Handicap-Punkte pro Attributsteigerung (korrekte SW-Regeln)
        """
        self.log("--- SCHRITT 4: ATTRIBUTE STEIGERN (ORIGINALFUNKTIONEN) ---")
        
        total_costs = 0
        start_handicap_points = charakter.verbleibende_handicap_punkte
        
        # Importiere die originale Funktion
        from functions.character_advancement import steigere_attribut as original_steigere_attribut
        
        self.log(f"  💰 Verfügbare Handicap-Punkte zu Beginn: {start_handicap_points}")
        self.log(f"  📋 Savage Worlds Regel: 2 Handicap-Punkte = 1 Attributsteigerung")

        # Attribute steigern mit originalen Funktionen
        for attr_name, target_value in target_attrs.items():
            if attr_name not in charakter.attribute:
                self.log(f"  ❌ Attribut '{attr_name}' existiert nicht")
                continue

            attr = charakter.attribute[attr_name]
            current_value = attr.wuerfel.value

            if current_value >= target_value:
                self.log(f"  ✅ {attr_name} bereits auf W{target_value}")
                continue

            advances_needed = self._calculate_advances_needed(current_value, target_value)
            self.log(f"  📈 {attr_name}: W{current_value} → W{target_value} ({advances_needed} Steigerungen)")

            for i in range(advances_needed):
                initial_handicap = charakter.verbleibende_handicap_punkte
                initial_attr_points = charakter.verbleibende_attributsteigerungen
                
                # Merke den aktuellen Attributwert vor dem Aufruf
                initial_attr_value = attr.wuerfel.value
                initial_handicap = charakter.verbleibende_handicap_punkte
                initial_attr_points = charakter.verbleibende_attributsteigerungen
                
                # Verwende die originale Funktion - sie verwendet automatisch Handicap-Punkte wenn nötig
                original_steigere_attribut(charakter, attr_name)
                
                # Prüfe ob das Attribut tatsächlich gesteigert wurde (unabhängig vom Return-Wert)
                new_attr_value = attr.wuerfel.value
                success = (new_attr_value > initial_attr_value)
                
                if success:
                    new_value = attr.wuerfel.value
                    # Prüfe welche Punkte verwendet wurden
                    handicap_used = initial_handicap - charakter.verbleibende_handicap_punkte
                    attr_points_used = initial_attr_points - charakter.verbleibende_attributsteigerungen
                    
                    cost_source = "Standard" if attr_points_used > 0 else f"{handicap_used} Handicap-Punkte"
                    self.log(f"    ✅ Steigerung {i+1}: W{current_value} → W{new_value} ({cost_source})")
                    
                    self.cost_log['attribute'].append({
                        'name': attr_name,
                        'von': current_value,
                        'nach': new_value,
                        'kosten': 1,
                        'handicap_punkte_verwendet': handicap_used,
                        'quelle': cost_source
                    })
                    current_value = new_value
                else:
                    # Füge Attributsteigerungen hinzu wenn keine anderen Punkte verfügbar
                    shortage = advances_needed - i
                    charakter.verbleibende_attributsteigerungen += shortage
                    self.auto_added_points += shortage
                    self.cost_log['auto_punkte'] += shortage
                    self.log(f"    ⚡ Automatisch {shortage} Attributspunkte hinzugefügt")
                    
                    # Versuche erneut
                    success = original_steigere_attribut(charakter, attr_name)
                    if success:
                        new_value = attr.wuerfel.value
                        self.log(f"    ✅ Steigerung {i+1}: W{current_value} → W{new_value} (Auto-Punkte)")
                        self.cost_log['attribute'].append({
                            'name': attr_name,
                            'von': current_value,
                            'nach': new_value,
                            'kosten': 1,
                            'auto_hinzugefuegt': True
                        })
                        current_value = new_value
                    else:
                        self.log(f"    ❌ Kritischer Fehler bei {attr_name} Steigerung {i+1}")
                        break

            total_costs += advances_needed

        self.log(f"📊 ATTRIBUTSKOSTEN GESAMT: {total_costs} Punkte")
        return total_costs

    def _advance_skills_with_original_functions(self, charakter: Charakter, target_skills: Dict[str, int]) -> int:
        """
        Steigert Fertigkeiten auf Zielwerte mit den originalen Savage Worlds Funktionen.
        Verwendet 1 Handicap-Punkt pro Fertigkeitssteigerung (korrekte SW-Regeln)
        """
        self.log("--- SCHRITT 5: FERTIGKEITEN STEIGERN (ORIGINALFUNKTIONEN) ---")
        
        total_costs = 0
        start_handicap_points = charakter.verbleibende_handicap_punkte
        
        # Importiere die originale Funktion
        from functions.eigenschaften_funktionen import steigere_fertigkeit as original_steigere_fertigkeit
        
        self.log(f"  💰 Verfügbare Handicap-Punkte: {start_handicap_points}")
        self.log(f"  📋 Savage Worlds Regel: 1 Handicap-Punkt = 1 Fertigkeitssteigerung")

        # Fertigkeiten steigern mit originalen Funktionen
        for skill_name, target_value in target_skills.items():
            # Finde die Fertigkeit
            skill = None
            skill_key = None
            for key, skill_obj in charakter.fertigkeiten.items():
                if skill_name.lower() in key.lower():
                    skill = skill_obj
                    skill_key = key
                    break

            if not skill:
                self.log(f"  ❌ Fertigkeit '{skill_name}' nicht gefunden")
                continue

            current_value = skill.wuerfel.value
            current_modifier = skill.wuerfel.modifier
            current_effective = current_value + current_modifier

            if current_effective >= target_value:
                self.log(f"  ✅ {skill_name} bereits auf W{target_value}")
                continue

            steps_needed = self._calculate_skill_steps(current_effective, target_value)
            self.log(f"  📈 {skill_name}: W{current_effective} → W{target_value} ({steps_needed} Steigerungen)")

            # Steigere schrittweise mit originaler Funktion
            for i in range(steps_needed):
                initial_handicap = charakter.verbleibende_handicap_punkte
                initial_skill_points = getattr(charakter, 'verbleibende_fertigkeitssteigerungen', 0)
                
                # Verwende die originale Funktion - sie verwendet automatisch Handicap-Punkte wenn nötig
                success = original_steigere_fertigkeit(charakter, skill_key, confirm_double_cost=True)
                
                if success:
                    new_effective = skill.wuerfel.value + skill.wuerfel.modifier
                    # Prüfe welche Punkte verwendet wurden
                    handicap_used = initial_handicap - charakter.verbleibende_handicap_punkte
                    skill_points_used = initial_skill_points - getattr(charakter, 'verbleibende_fertigkeitssteigerungen', 0)
                    
                    cost_source = "Standard" if skill_points_used > 0 else f"{handicap_used} Handicap-Punkt"
                    self.log(f"    ✅ Steigerung {i+1}: W{current_effective} → W{new_effective} ({cost_source})")
                    
                    self.cost_log['fertigkeiten'].append({
                        'name': skill_name,
                        'von': current_effective,
                        'nach': new_effective,
                        'kosten': 1,
                        'handicap_punkte_verwendet': handicap_used,
                        'quelle': cost_source
                    })
                    current_effective = new_effective
                else:
                    # Füge Fertigkeitspunkte hinzu wenn keine anderen Punkte verfügbar
                    shortage = steps_needed - i
                    charakter.verbleibende_fertigkeitssteigerungen += shortage
                    self.auto_added_points += shortage
                    self.cost_log['auto_punkte'] += shortage
                    self.log(f"    ⚡ Automatisch {shortage} Fertigkeitspunkte hinzugefügt")
                    
                    # Versuche erneut
                    success = original_steigere_fertigkeit(charakter, skill_key, confirm_double_cost=True)
                    if success:
                        new_effective = skill.wuerfel.value + skill.wuerfel.modifier
                        self.log(f"    ✅ Steigerung {i+1}: W{current_effective} → W{new_effective} (Auto-Punkte)")
                        self.cost_log['fertigkeiten'].append({
                            'name': skill_name,
                            'von': current_effective,
                            'nach': new_effective,
                            'kosten': 1,
                            'auto_hinzugefuegt': True
                        })
                        current_effective = new_effective
                    else:
                        self.log(f"    ❌ Kritischer Fehler bei {skill_name} Steigerung {i+1}")
                        break

            total_costs += steps_needed

        self.log(f"📊 FERTIGKEITSKOSTEN GESAMT: {total_costs} Punkte")
        return total_costs

    def _advance_skills_unlimited(self, charakter: Charakter, target_skills: Dict[str, int]) -> int:
        """
        Steigert Fertigkeiten auf Zielwerte - MIT automatischer Punkteerhöhung
        """
        self.log("--- SCHRITT 5: FERTIGKEITEN STEIGERN (UNLIMITED) ---")

        start_skill_points = 12  # Standard SWAE
        total_costs = 0

        # Berechne benötigte Punkte
        needed_points = self._calculate_skill_points_needed(charakter, target_skills)
        if needed_points > start_skill_points:
            additional_points = needed_points - start_skill_points
            charakter.verbleibende_fertigkeitssteigerungen += additional_points
            self.auto_added_points += additional_points
            self.cost_log['auto_punkte'] += additional_points
            self.log(f"  💰 Automatisch {additional_points} Fertigkeitspunkte hinzugefügt")

        for skill_name, target_value in target_skills.items():
            # Finde die Fertigkeit
            skill = None
            for key, skill_obj in charakter.fertigkeiten.items():
                if skill_name.lower() in key.lower():
                    skill = skill_obj
                    skill_key = key
                    break

            if not skill:
                self.log(f"  ❌ Fertigkeit '{skill_name}' nicht gefunden")
                continue

            current_value = skill.wuerfel.value
            current_modifier = skill.wuerfel.modifier
            current_effective = current_value + current_modifier

            if current_effective >= target_value:
                self.log(f"  ✅ {skill_name} bereits auf W{target_value}")
                continue

            # Steigere die Fertigkeit
            steps_needed = self._calculate_skill_steps(current_effective, target_value)
            cost = steps_needed

            self.log(f"  📈 {skill_name}: W{current_effective} → W{target_value} ({cost} Punkte)")

            # Setze den Zielwert direkt
            if target_value <= 2:  # W4-2
                skill.wuerfel.value = 4
                skill.wuerfel.modifier = -2
            else:
                skill.wuerfel.value = target_value
                skill.wuerfel.modifier = 0

            self.cost_log['fertigkeiten'].append({
                'name': skill_name,
                'von': current_effective,
                'nach': target_value,
                'kosten': cost
            })

            total_costs += cost

        self.log(f"📊 FERTIGKEITSKOSTEN GESAMT: {total_costs} Punkte")
        return total_costs

    def _select_edges_unlimited(self, charakter: Charakter, edges: List[str],
                                free_race_edge: Optional[str]) -> int:
        """
        Wählt Talente mit originalen Savage Worlds Funktionen.
        Verwendet 2 Handicap-Punkte pro Talent (korrekte SW-Regeln)
        """
        self.log("--- SCHRITT 6: TALENTE WÄHLEN (ORIGINALFUNKTIONEN) ---")

        total_costs = 0
        edges_to_add = edges.copy()
        start_handicap_points = charakter.verbleibende_handicap_punkte
        
        # Importiere die originale Funktion
        from functions.talent_funktionen import get_talent_manager
        
        self.log(f"  💰 Verfügbare Handicap-Punkte: {start_handicap_points}")
        self.log(f"  📋 Savage Worlds Regel: 2 Handicap-Punkte = 1 Talent")

        # Menschen-Bonus oder Völker-Talent
        if free_race_edge:
            edges_to_add.insert(0, free_race_edge)
            self.log(f"  🎁 Völker-Talent wird hinzugefügt: {free_race_edge}")
        elif hasattr(charakter, 'voelker_boni') and charakter.voelker_boni.get('freie_talente', 0) > 0:
            if edges_to_add:
                free_edge = edges_to_add[0]
                self.log(f"  🎁 Menschen-Bonus verwendet für: {free_edge}")

        talent_manager = get_talent_manager(charakter)

        for i, edge_name in enumerate(edges_to_add):
            is_free = (i == 0 and (free_race_edge or
                                   (hasattr(charakter, 'voelker_boni') and
                                    charakter.voelker_boni.get('freie_talente', 0) > 0)))

            # Suche das Talent
            talent_key = None
            for key, talent_obj in charakter.talente.items():
                if edge_name.lower() in key.lower():
                    talent_key = key
                    break

            if not talent_key:
                self.log(f"  ❌ Talent '{edge_name}' nicht gefunden")
                continue

            if is_free:
                # Gratis-Talent über talent_auswaehlen setzen (löst Seiteneffekte aus)
                charakter.ignore_voraussetzungen = True
                result = talent_manager.talent_auswaehlen(talent_key, skip_prereq_check=True)
                if not result:
                    # Fallback: Direkt setzen
                    talent_obj = charakter.talente[talent_key]
                    if hasattr(talent_obj, 'ausgewaehlt'):
                        talent_obj.ausgewaehlt = True
                    if hasattr(talent_obj, 'aktiv'):
                        talent_obj.aktiv = True
                self.log(f"  ✅ {edge_name} hinzugefügt (GRATIS - Völker-Bonus)")
                self.cost_log['talente'].append({
                    'name': edge_name,
                    'kosten': 0,
                    'gratis': True
                })
            else:
                # Verwende die originale Talent-Funktion
                initial_handicap = charakter.verbleibende_handicap_punkte
                
                # Setze Flag zum Ignorieren von Voraussetzungen
                charakter.ignore_voraussetzungen = True
                
                result = talent_manager.waehle_talent(talent_key)

                # String-Rückgaben behandeln (z.B. "pathfinder_kostenlos_angeboten",
                # "needs_voraussetzungen_confirmation", "needs_rang_confirmation")
                if result == "pathfinder_kostenlos_angeboten":
                    result = talent_manager.waehle_pathfinder_kostenloses_talent(
                        talent_key, ignore_voraussetzungen=True)
                    self.log(f"  🎁 {edge_name} als kostenloses Pathfinder-Talent gewählt")
                elif isinstance(result, str):
                    # Andere String-Rückgaben → Talent direkt setzen (Fallback)
                    result = False

                if result is True:
                    handicap_used = initial_handicap - charakter.verbleibende_handicap_punkte
                    cost_source = f"{handicap_used} Handicap-Punkte" if handicap_used > 0 else "Standard-Punkte"
                    self.log(f"  ✅ {edge_name} hinzugefügt ({cost_source}) - Voraussetzungen ignoriert")

                    total_costs += 1
                    self.cost_log['talente'].append({
                        'name': edge_name,
                        'kosten': 1,
                        'handicap_punkte_verwendet': handicap_used,
                        'quelle': cost_source,
                        'voraussetzungen_ignoriert': True
                    })
                else:
                    # Fallback: über talent_auswaehlen mit skip_prereq_check
                    fallback_result = talent_manager.talent_auswaehlen(talent_key, skip_prereq_check=True)
                    if not fallback_result:
                        # Letzter Fallback: Direkt setzen
                        talent_obj = charakter.talente[talent_key]
                        if hasattr(talent_obj, 'ausgewaehlt'):
                            talent_obj.ausgewaehlt = True
                        if hasattr(talent_obj, 'aktiv'):
                            talent_obj.aktiv = True
                    self.log(f"  ⚠️ {edge_name} direkt gesetzt (Fallback) - Voraussetzungen ignoriert")

                    total_costs += 1
                    self.cost_log['talente'].append({
                        'name': edge_name,
                        'kosten': 1,
                        'fallback': True,
                        'voraussetzungen_ignoriert': True
                    })

        self.log(f"📊 TALENTKOSTEN GESAMT: {total_costs} Punkte")
        return total_costs

    def _select_powers_unlimited(self, charakter: Charakter, powers: List[str], power_points: int) -> None:
        """
        Wählt Mächte OHNE Voraussetzungsprüfung
        """
        self.log("--- SCHRITT 7: MÄCHTE WÄHLEN (OHNE VORAUSSETZUNGEN) ---")

        # Arkaner Hintergrund wird automatisch angenommen/hinzugefügt
        self.log("  🔮 Arkaner Hintergrund wird automatisch hinzugefügt/angenommen")

        # Stelle sicher, dass ein Arkaner Hintergrund ausgewählt ist
        arcane_found = False
        from functions.talent_funktionen import get_talent_manager
        talent_manager = get_talent_manager(charakter)

        for talent_name, talent_obj in charakter.talente.items():
            if talent_name == "AH" or talent_name.startswith("AH (") or talent_name.startswith("AH:"):
                if not talent_obj.ausgewaehlt:
                    # Über talent_auswaehlen aktivieren (löst Machtpunkte/Mächte-Erhöhung aus)
                    charakter.ignore_voraussetzungen = True
                    result = talent_manager.talent_auswaehlen(talent_name, skip_prereq_check=True)
                    if not result:
                        # Fallback
                        talent_obj.ausgewaehlt = True
                        if hasattr(talent_obj, 'aktiv'):
                            talent_obj.aktiv = True
                arcane_found = True
                self.log(f"  ✅ {talent_name} aktiviert (Machtpunkte: {charakter.machtpunkte})")
                break

        if not arcane_found:
            self.log("  ⚠️ Kein Arkaner Hintergrund gefunden - Mächte werden trotzdem hinzugefügt")

        powers_added = 0
        for power_name in powers:
            found = False
            if hasattr(charakter, 'maechte') and charakter.maechte:
                for key, power in charakter.maechte.items():
                    if power_name.lower() in key.lower():
                        if hasattr(power, 'ausgewaehlt'):
                            power.ausgewaehlt = True
                        if hasattr(power, 'aktiv'):
                            power.aktiv = True
                        self.log(f"  ✅ {power_name} hinzugefügt - Voraussetzungen ignoriert")
                        self.cost_log['maechte'].append({
                            'name': power_name,
                            'voraussetzungen_ignoriert': True
                        })
                        powers_added += 1
                        found = True
                        break

            if not found:
                self.log(f"  ❌ {power_name} nicht verfügbar")

        # Machtpunkte setzen
        if power_points > 0:
            if hasattr(charakter, 'machtpunkte'):
                charakter.machtpunkte = power_points
                self.log(f"  🔮 Machtpunkte gesetzt: {power_points}")
            else:
                self.log("  ⚠️ Machtpunkte-Property nicht gefunden")

        self.log(f"📊 MÄCHTE GESAMT: {powers_added} Mächte hinzugefügt")

    def _update_selected_lists(self, charakter: Charakter) -> None:
        """Aktualisiert die selected_ Listen basierend auf ausgewählten Items"""
        self.log("--- SELECTED_ LISTEN AKTUALISIEREN ---")
        
        # selected_talente aktualisieren
        selected_talente = []
        for talent_name, talent in charakter.talente.items():
            if getattr(talent, 'ausgewaehlt', False):
                selected_talente.append(talent_name)
        charakter.selected_talente = selected_talente
        self.log(f"  📋 selected_talente: {len(selected_talente)} Items")
        
        # selected_maechte aktualisieren  
        selected_maechte = []
        if hasattr(charakter, 'maechte') and charakter.maechte:
            for macht_name, macht in charakter.maechte.items():
                if getattr(macht, 'ausgewaehlt', False):
                    selected_maechte.append(macht_name)
        charakter.selected_maechte = selected_maechte
        self.log(f"  🔮 selected_maechte: {len(selected_maechte)} Items")
        
        # Fix für doppelte Menge
        self._fix_duplicate_items(charakter)
        
        self.log("  ✅ selected_ Listen aktualisiert")

    def _fix_duplicate_items(self, charakter: Charakter) -> None:
        """Behebt das Problem mit doppelten Items (menge=2)"""
        if hasattr(charakter, 'ausruestung') and charakter.ausruestung:
            for item_name, item in charakter.ausruestung.items():
                if hasattr(item, 'menge') and item.menge > 1:
                    item.menge = 1
                    self.log(f"    🔧 {item_name}: Menge korrigiert von {item.menge} zu 1")

    def _add_equipment(self, charakter: Charakter, equipment: List[Union[str, Dict]]) -> None:
        """Fügt Ausrüstung hinzu"""
        self.log("--- SCHRITT 8: AUSRÜSTUNG HINZUFÜGEN ---")

        items_added = 0
        
        # Erstelle Liste der Custom Equipment Namen um Duplikate zu vermeiden
        custom_equipment = self.current_template.get('custom_equipment', [])
        custom_names = {item.get('name', '').lower() for item in custom_equipment}
        
        for item in equipment:
            if isinstance(item, str):
                # Überspringe String-Items wenn sie als Custom Equipment existieren
                if item.lower() in custom_names:
                    self.log(f"  ⏭️ {item} übersprungen - wird als Custom Equipment hinzugefügt")
                    continue
                # Einfacher Gegenstandsname
                success = self._add_simple_equipment(charakter, item)
                if success:
                    items_added += 1
            elif isinstance(item, dict):
                # Custom Equipment-Objekt
                success = self._add_custom_equipment(charakter, item)
                if success:
                    items_added += 1

        # WICHTIG: Auch custom_equipment aus Template verarbeiten 
        if custom_equipment:
            self.log("  🔧 Verarbeite custom_equipment aus Template...")
            for item_data in custom_equipment:
                success = self._add_custom_equipment(charakter, item_data)
                if success:
                    items_added += 1

        self.log(f"📊 AUSRÜSTUNG GESAMT: {items_added} Gegenstände hinzugefügt")

    def _add_simple_equipment(self, charakter: Charakter, item_name: str) -> bool:
        """Fügt einfachen Ausrüstungsgegenstand hinzu"""
        # Zuerst in vorhandener Ausrüstung suchen
        if hasattr(charakter, 'ausruestung') and charakter.ausruestung:
            for key, item in charakter.ausruestung.items():
                if item_name.lower() in key.lower():
                    if hasattr(item, 'ausgewaehlt'):
                        item.ausgewaehlt = True
                    if hasattr(item, 'aktiv'):
                        item.aktiv = True
                    charakter.selected_allgemeine_ausruestung.append(item)
                    self.log(f"  ✅ {item_name} gefunden und ausgewählt")
                    return True

        # Als Custom-Item anlegen
        self.log(f"  📦 {item_name} nicht gefunden - lege als Custom-Item an...")

        try:
            from models.ausruestung import Ausruestung
            custom_item = Ausruestung(
                name=item_name,
                gewicht=1,
                kosten=10,
                setting="allgemein",
                beschreibung=f"Custom {item_name}",
                menge=1,
                ausgewaehlt=True,
                aktiv=True,
                kategorie="Allgemein",
                custom=True
            )

            success = charakter.add_ausruestung(custom_item)
            if success:
                charakter.selected_allgemeine_ausruestung.append(custom_item)
                self.log(f"    ✅ {item_name} erfolgreich hinzugefügt")
                return True
            else:
                self.log(f"    ❌ FEHLER: {item_name} konnte nicht hinzugefügt werden")
                return False

        except Exception as e:
            self.log(f"    ❌ FEHLER beim Anlegen von {item_name}: {e}")
            return False

    def _add_custom_equipment(self, charakter: Charakter, item_data: Dict) -> bool:
        """Fügt Custom Equipment mit den korrekten spezifischen Modellen hinzu"""
        item_name = item_data.get('name', 'Unbekannt')
        item_type = item_data.get('type', 'item')

        self.log(f"  🔧 Custom {item_type}: {item_name}")

        try:
            # Verwende die spezifischen Modelle basierend auf dem type
            if item_type in ["Waffe", "weapon"]:
                from models.waffe import Waffe
                
                # Standard-Properties für Waffen
                eigenschaften = item_data.get('properties', {})
                default_properties = {
                    "Schaden": eigenschaften.get("Schaden", "Stä+W4"),
                    "Reichweite": eigenschaften.get("Reichweite", "nah"),
                    "FR": eigenschaften.get("FR", "-"),
                    "Schuss": eigenschaften.get("Schuss", "-"),
                    "PB": eigenschaften.get("PB", "-")
                }
                
                custom_item = Waffe(
                    name=item_name,
                    gewicht=item_data.get('weight', 1),
                    kosten=item_data.get('cost', 0),
                    setting="custom",
                    typ=eigenschaften.get("typ", "Nahkampf"),
                    mindeststaerke=eigenschaften.get("mindeststaerke", "W4"),
                    beschreibung=item_data.get('description', f"Custom {item_name}"),
                    eigenschaften=default_properties,
                    menge=1,
                    ausgewaehlt=True,
                    aktiv=True,
                    angelegt=False,
                    kategorie="Waffe",
                    custom=True
                )
                
            elif item_type in ["Rüstung", "armor"]:
                from models.ruestung import Ruestung
                
                # Standard-Properties für Rüstungen
                eigenschaften = item_data.get('properties', {})
                
                custom_item = Ruestung(
                    name=item_name,
                    gewicht=item_data.get('weight', 2),
                    kosten=item_data.get('cost', 20),
                    setting="custom",
                    beschreibung=item_data.get('description', f"Custom {item_name}"),
                    menge=1,
                    ausgewaehlt=True,
                    aktiv=True,
                    angelegt=False,
                    kategorie="Rüstung",
                    torso=eigenschaften.get("torso", 2),
                    arme=eigenschaften.get("arme", 0),
                    beine=eigenschaften.get("beine", 0),
                    kopf=eigenschaften.get("kopf", 0),
                    mindeststaerke=eigenschaften.get("mindeststaerke", "W6"),
                    custom=True
                )
                
            elif item_type in ["Schild", "shield"]:
                from models.schild import Schild
                
                # Standard-Properties für Schilde
                eigenschaften = item_data.get('properties', {})
                
                custom_item = Schild(
                    name=item_name,
                    gewicht=item_data.get('weight', 2),
                    kosten=item_data.get('cost', 10),
                    setting="custom",
                    beschreibung=item_data.get('description', f"Custom {item_name}"),
                    menge=1,
                    ausgewaehlt=True,
                    aktiv=True,
                    angelegt=False,
                    kategorie="Schild",
                    deckung=eigenschaften.get("deckung", 1),
                    parade=eigenschaften.get("parade", 1),
                    mindeststaerke=eigenschaften.get("mindeststaerke", "W4"),
                    custom=True
                )
                
            else:
                # Fallback für allgemeine Ausrüstung
                from models.ausruestung import Ausruestung
                
                custom_item = Ausruestung(
                    name=item_name,
                    gewicht=item_data.get('weight', 1),
                    kosten=item_data.get('cost', 0),
                    setting="custom",
                    beschreibung=item_data.get('description', f"Custom {item_name}"),
                    menge=1,
                    ausgewaehlt=True,
                    aktiv=True,
                    kategorie=item_data.get('category', 'Ausrüstung'),
                    custom=True
                )

            success = charakter.add_ausruestung(custom_item)
            if success:
                # Je nach type auch zu spezialisierten Listen hinzufügen
                if item_type in ["Waffe", "weapon"]:
                    charakter.selected_waffen.append(custom_item)
                    self.log(f"    ⚔️ {item_name} zu selected_waffen hinzugefügt")
                elif item_type in ["Rüstung", "armor"]:
                    charakter.selected_ruestungen.append(custom_item)
                    self.log(f"    🛡️ {item_name} zu selected_ruestungen hinzugefügt")
                elif item_type in ["Schild", "shield"]:
                    charakter.selected_schilde.append(custom_item)
                    self.log(f"    🛡️ {item_name} zu selected_schilde hinzugefügt")
                
                self.log(f"    ✅ {item_name} erfolgreich hinzugefügt (Kategorie: {custom_item.kategorie})")
                return True
            else:
                self.log(f"    ❌ FEHLER: {item_name} konnte nicht hinzugefügt werden")
                return False

        except Exception as e:
            self.log(f"    ❌ FEHLER beim Anlegen von {item_name}: {e}")
            import traceback
            self.log(f"    📋 Traceback: {traceback.format_exc()}")
            return False

    def _calculate_attribute_points_needed(self, charakter: Charakter, target_attrs: Dict[str, int]) -> int:
        """Berechnet benötigte Attributspunkte"""
        total_needed = 0
        for attr_name, target_value in target_attrs.items():
            if attr_name in charakter.attribute:
                current = charakter.attribute[attr_name].wuerfel.value
                advances = self._calculate_advances_needed(current, target_value)
                total_needed += advances
        return total_needed

    def _calculate_skill_points_needed(self, charakter: Charakter, target_skills: Dict[str, int]) -> int:
        """Berechnet benötigte Fertigkeitspunkte"""
        total_needed = 0
        for skill_name, target_value in target_skills.items():
            for key, skill_obj in charakter.fertigkeiten.items():
                if skill_name.lower() in key.lower():
                    current = skill_obj.wuerfel.value + skill_obj.wuerfel.modifier
                    steps = self._calculate_skill_steps(current, target_value)
                    total_needed += steps
                    break
        return total_needed

    def _calculate_advances_needed(self, current: int, target: int) -> int:
        """Berechnet Anzahl der Steigerungen für Attribute"""
        # Für Attribute: W4 (4) -> W6 (6) -> W8 (8) -> W10 (10) -> W12 (12)
        steps = [4, 6, 8, 10, 12]

        current_idx = 0
        for i, val in enumerate(steps):
            if current <= val:
                current_idx = i
                break

        target_idx = len(steps) - 1
        for i, val in enumerate(steps):
            if target <= val:
                target_idx = i
                break

        return max(0, target_idx - current_idx)

    def _calculate_skill_steps(self, current_effective: int, target: int) -> int:
        """Berechnet Anzahl der Steigerungen für Fertigkeiten"""
        # Für Fertigkeiten: W4-2 (2) -> W4 (4) -> W6 (6) -> W8 (8) -> W10 (10) -> W12 (12)
        if current_effective <= 2:  # W4-2
            steps = [2, 4, 6, 8, 10, 12]
        else:
            steps = [4, 6, 8, 10, 12]

        # Finde aktuelle und Ziel-Position
        current_idx = 0
        for i, val in enumerate(steps):
            if current_effective <= val:
                current_idx = i
                break

        target_idx = len(steps) - 1
        for i, val in enumerate(steps):
            if target <= val:
                target_idx = i
                break

        return max(0, target_idx - current_idx)

    def _print_character_summary_with_costs(self, charakter: Charakter, attr_costs: int,
                                            skill_costs: int, edge_costs: int, handicap_points: int) -> None:
        """Druckt erweiterte Charakterzusammenfassung mit Kostendetails"""
        self.log("\n" + "=" * 80)
        self.log("📊 CHARAKTERZUSAMMENFASSUNG MIT KOSTENANALYSE")
        self.log("=" * 80)

        self.log(f"Charakter: {charakter.profil_daten.get('Name', 'Unbenannt')}")
        self.log(f"Setting: {charakter.active_setting_name}")

        self.log(f"\n💰 KOSTENÜBERSICHT:")
        self.log(f"Attribute: {attr_costs} Punkte")
        self.log(f"Fertigkeiten: {skill_costs} Punkte")
        self.log(f"Handicaps: +{handicap_points} Punkte (Bonus)")
        self.log(f"Talente: {edge_costs} Punkte")

        # Standardpunkte
        standard_attr = 5
        standard_skill = 12
        total_standard = standard_attr + standard_skill

        # Tatsächliche Kosten
        total_costs = attr_costs + skill_costs + edge_costs
        total_available = total_standard + handicap_points

        self.log(f"\n📈 PUNKTEBILANZ:")
        self.log(f"Standard-Punkte: {total_standard} ({standard_attr} Attr + {standard_skill} Fert)")
        self.log(f"Handicap-Bonus: +{handicap_points}")
        self.log(f"Verfügbar gesamt: {total_available}")
        self.log(f"Ausgegeben: {total_costs}")
        self.log(f"Differenz: {total_available - total_costs}")

        if self.auto_added_points > 0:
            self.log(f"\n⚡ AUTOMATISCH HINZUGEFÜGT: {self.auto_added_points} Punkte")
            self.log(f"   (Um alle Anforderungen zu erfüllen)")

        self.log(f"\n🎭 ATTRIBUTE:")
        for attr_name, attr in charakter.attribute.items():
            self.log(f"  {attr_name}: {attr.wuerfel}")

        self.log(f"\n🎯 FERTIGKEITEN (gesteigerte):")
        for skill_name, skill in charakter.fertigkeiten.items():
            if skill.wuerfel.value > 4 or skill.wuerfel.modifier > -2:
                self.log(f"  {skill_name}: {skill.wuerfel}")

        self.log(f"\n⭐ TALENTE:")
        for talent_name, talent in charakter.talente.items():
            if getattr(talent, 'ausgewaehlt', False):
                voraussetzung_ignoriert = any(t['name'] == talent_name and
                                              t.get('voraussetzungen_ignoriert', False)
                                              for t in self.cost_log['talente'])
                marker = " [!]" if voraussetzung_ignoriert else ""
                self.log(f"  {talent_name}{marker}")

        self.log(f"\n⚠️ HANDICAPS:")
        for handicap_name, handicap in charakter.handicaps.items():
            if getattr(handicap, 'ausgewaehlt', False):
                points = getattr(handicap, 'punkte', getattr(handicap, 'wert', 1))
                self.log(f"  {handicap_name} ({points} Punkte)")

        # Mächte
        powers_found = False
        if hasattr(charakter, 'maechte') and charakter.maechte:
            for macht_name, macht in charakter.maechte.items():
                if getattr(macht, 'ausgewaehlt', False):
                    if not powers_found:
                        self.log(f"\n🔮 MÄCHTE:")
                        powers_found = True
                    voraussetzung_ignoriert = any(m['name'] == macht_name and
                                                  m.get('voraussetzungen_ignoriert', False)
                                                  for m in self.cost_log.get('maechte', []))
                    marker = " [!]" if voraussetzung_ignoriert else ""
                    self.log(f"  {macht_name}{marker}")

        if hasattr(charakter, 'machtpunkte') and charakter.machtpunkte > 0:
            self.log(f"Machtpunkte: {charakter.machtpunkte}")

        self.log("\n[!] = Voraussetzungen wurden ignoriert")

    def _create_cost_log_file(self, charakter: Charakter, char_name: str, output_dir: Optional[str]) -> Path:
        """Erstellt detailliertes Kosten-Log als Datei"""
        self.log("\n--- ERSTELLE KOSTEN-LOG-DATEI ---")

        # Log-Ordner bestimmen (PyInstaller-kompatibel)
        if output_dir:
            log_dir = Path(output_dir)
        else:
            from utils.path_utils import get_chars_path
            chars_root = Path(get_chars_path())
            log_dir = chars_root / "auto_generated" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # Dateiname
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        log_filename = f"{safe_name}_kosten_{timestamp}.txt"
        log_path = log_dir / log_filename

        # Log-Inhalt erstellen
        log_content = []
        log_content.append("=" * 80)
        log_content.append(f"KOSTEN-LOG FÜR: {char_name}")
        log_content.append(f"ERSTELLT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_content.append("=" * 80)
        log_content.append("")

        # Attribute
        log_content.append("ATTRIBUTE:")
        log_content.append("-" * 40)
        total_attr_cost = 0
        for attr in self.cost_log['attribute']:
            log_content.append(f"  {attr['name']}: W{attr['von']} → W{attr['nach']} = {attr['kosten']} Punkte")
            total_attr_cost += attr['kosten']
        log_content.append(f"GESAMT: {total_attr_cost} Punkte")
        log_content.append("")

        # Fertigkeiten
        log_content.append("FERTIGKEITEN:")
        log_content.append("-" * 40)
        total_skill_cost = 0
        for skill in self.cost_log['fertigkeiten']:
            log_content.append(f"  {skill['name']}: W{skill['von']} → W{skill['nach']} = {skill['kosten']} Punkte")
            total_skill_cost += skill['kosten']
        log_content.append(f"GESAMT: {total_skill_cost} Punkte")
        log_content.append("")

        # Handicaps
        log_content.append("HANDICAPS:")
        log_content.append("-" * 40)
        total_handicap_points = 0
        for handicap in self.cost_log['handicaps']:
            erzwungen = " [ERZWUNGEN]" if handicap.get('erzwungen', False) else ""
            log_content.append(f"  {handicap['name']}: +{handicap['punkte']} Punkte{erzwungen}")
            total_handicap_points += handicap['punkte']
        log_content.append(f"GESAMT: +{total_handicap_points} Punkte (Bonus)")
        log_content.append("")
        
        # Handicap-Verwendung
        if total_handicap_points > 0:
            log_content.append("HANDICAP-PUNKTE VERWENDUNG:")
            log_content.append("-" * 40)
            log_content.append("Handicap-Punkte können verwendet werden für:")
            log_content.append("  • 1 Punkt = 2 Attributsteigerungen")
            log_content.append("  • 1 Punkt = 1 Anfänger-Talent") 
            log_content.append("  • 1 Punkt = 2 Fertigkeitssteigerungen")
            log_content.append("  • 1 Punkt = Startgeld erhöhen")
            log_content.append(f"→ {total_handicap_points} Handicap-Punkte entsprechen:")
            log_content.append(f"  - Bis zu {total_handicap_points * 2} Attribut-/Fertigkeitssteigerungen ODER")
            log_content.append(f"  - Bis zu {total_handicap_points} Talente ODER")
            log_content.append("  - Kombination aus beidem")
            log_content.append("")

        # Talente
        log_content.append("TALENTE:")
        log_content.append("-" * 40)
        total_edge_cost = 0
        for talent in self.cost_log['talente']:
            if talent.get('gratis', False):
                log_content.append(f"  {talent['name']}: GRATIS (Völker-Bonus)")
            else:
                voraussetzung = " [Voraussetzungen ignoriert]" if talent.get('voraussetzungen_ignoriert', False) else ""
                log_content.append(f"  {talent['name']}: {talent['kosten']} Punkte{voraussetzung}")
                total_edge_cost += talent['kosten']
        log_content.append(f"GESAMT: {total_edge_cost} Punkte")
        log_content.append("")

        # Mächte
        if self.cost_log.get('maechte'):
            log_content.append("MÄCHTE:")
            log_content.append("-" * 40)
            for macht in self.cost_log['maechte']:
                voraussetzung = " [Voraussetzungen ignoriert]" if macht.get('voraussetzungen_ignoriert', False) else ""
                log_content.append(f"  {macht['name']}{voraussetzung}")
            log_content.append("")

        # Zusammenfassung
        log_content.append("=" * 80)
        log_content.append("ZUSAMMENFASSUNG:")
        log_content.append("=" * 80)
        log_content.append(f"Standardpunkte Attribute: 5")
        log_content.append(f"Standardpunkte Fertigkeiten: 12")
        log_content.append(f"Handicap-Bonus: +{total_handicap_points}")
        log_content.append(f"Verfügbare Punkte gesamt: {5 + 12 + total_handicap_points}")
        log_content.append("")
        log_content.append(f"Ausgegeben für Attribute: {total_attr_cost}")
        log_content.append(f"Ausgegeben für Fertigkeiten: {total_skill_cost}")
        log_content.append(f"Ausgegeben für Talente: {total_edge_cost}")
        log_content.append(f"Ausgegeben gesamt: {total_attr_cost + total_skill_cost + total_edge_cost}")
        log_content.append("")

        # Bilanz
        verfuegbar = 5 + 12 + total_handicap_points
        ausgegeben = total_attr_cost + total_skill_cost + total_edge_cost
        differenz = verfuegbar - ausgegeben

        if differenz < 0:
            log_content.append(f"DEFIZIT: {abs(differenz)} Punkte")
            log_content.append(f"AUTOMATISCH HINZUGEFÜGT: {self.auto_added_points} Punkte")
            log_content.append("→ Charakter wurde mit zusätzlichen Punkten erstellt")
        elif differenz > 0:
            log_content.append(f"ÜBERSCHUSS: {differenz} Punkte nicht verwendet")
        else:
            log_content.append("BILANZ: Ausgeglichen (alle Punkte verwendet)")

        log_content.append("")
        log_content.append("=" * 80)
        log_content.append("HINWEISE:")
        log_content.append("- [!] = Voraussetzungen wurden ignoriert")
        log_content.append("- [ERZWUNGEN] = Handicap wurde trotz Fehler markiert")
        log_content.append("- Automatisch hinzugefügte Punkte ermöglichen die Charaktererstellung")
        log_content.append("=" * 80)

        # In Datei schreiben
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(log_content))

        self.log(f"  ✅ Kosten-Log gespeichert: {log_path}")

        # Auch die Generation-Logs speichern
        gen_log_filename = f"{safe_name}_generation_{timestamp}.txt"
        gen_log_path = log_dir / gen_log_filename

        with open(gen_log_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.generation_log))

        self.log(f"  ✅ Generierungs-Log gespeichert: {gen_log_path}")

        return log_path
        
    def _integrate_with_historie_view(self, charakter: Charakter, char_name: str, cost_log_path: Path) -> None:
        """Integriert Auto Generator Ergebnisse in das Historie View System"""
        self.log("--- HISTORIE VIEW INTEGRATION ---")
        
        try:
            # Erstelle Historie-kompatibles Log
            from views.historie_view import CharakterHistorie
            historie = CharakterHistorie()
            
            # Auto-Generation Eintrag
            historie.add_entry('auto_character_generated', {
                'name': char_name,
                'template': self.current_template.get('name', 'Unbekannt'),
                'setting': self.current_template.get('setting', 'SWAE'),
                'total_auto_points': self.auto_added_points,
                'cost_log_file': str(cost_log_path)
            })
            
            # Attribute aus Cost-Log hinzufügen
            for attr_entry in self.cost_log['attribute']:
                historie.add_entry('attribut_steigerung', {
                    'name': attr_entry['name'],
                    'von': attr_entry['von'],
                    'nach': attr_entry['nach'],
                    'kosten': attr_entry['kosten'],
                    'kosten_typ': attr_entry.get('quelle', 'Auto-Generator'),
                    'auto_generated': True
                })
            
            # Fertigkeiten aus Cost-Log hinzufügen
            for skill_entry in self.cost_log['fertigkeiten']:
                historie.add_entry('fertigkeit_steigerung', {
                    'name': skill_entry['name'],
                    'von': skill_entry['von'],
                    'nach': skill_entry['nach'],
                    'kosten': skill_entry['kosten'],
                    'kosten_typ': skill_entry.get('quelle', 'Auto-Generator'),
                    'auto_generated': True
                })
            
            # Talente aus Cost-Log hinzufügen
            for talent_entry in self.cost_log['talente']:
                historie.add_entry('talent_hinzugefuegt', {
                    'name': talent_entry['name'],
                    'kosten': talent_entry['kosten'],
                    'auto_generated': True,
                    'gratis': talent_entry.get('gratis', False),
                    'voraussetzungen_ignoriert': talent_entry.get('voraussetzungen_ignoriert', False)
                })
            
            # Handicaps aus Cost-Log hinzufügen
            for handicap_entry in self.cost_log['handicaps']:
                historie.add_entry('handicap_hinzugefuegt', {
                    'name': handicap_entry['name'],
                    'punkte': handicap_entry['punkte'],
                    'auto_generated': True,
                    'erzwungen': handicap_entry.get('erzwungen', False)
                })
            
            # Mächte aus Cost-Log hinzufügen
            for macht_entry in self.cost_log.get('maechte', []):
                historie.add_entry('macht_hinzugefuegt', {
                    'name': macht_entry['name'],
                    'auto_generated': True,
                    'voraussetzungen_ignoriert': macht_entry.get('voraussetzungen_ignoriert', False)
                })
            
            # Ausrüstung hinzufügen
            equipment_list = self.current_template.get('equipment', []) + self.current_template.get('custom_equipment', [])
            for item in equipment_list:
                item_name = item if isinstance(item, str) else item.get('name', 'Unbekannt')
                historie.add_entry('ausruestung_hinzugefuegt', {
                    'name': item_name,
                    'auto_generated': True,
                    'custom': isinstance(item, dict)
                })
            
            # Historie als JSON speichern (kompatibel mit Historie View)
            from pathlib import Path
            project_root = Path(__file__).parent.parent
            historie_dir = project_root / "chars" / "manual_logs"
            historie_dir.mkdir(parents=True, exist_ok=True)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            historie_json_path = historie_dir / f"{safe_name}_auto_gen_historie_{timestamp}.json"
            historie_txt_path = historie_dir / f"{safe_name}_auto_gen_historie_{timestamp}.txt"
            
            # JSON speichern
            import json
            with open(historie_json_path, 'w', encoding='utf-8') as f:
                json.dump(historie.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Text-Log speichern
            with open(historie_txt_path, 'w', encoding='utf-8') as f:
                f.write(historie.get_formatted_log())
            
            self.log(f"  ✅ Historie View Integration erfolgreich:")
            self.log(f"    📄 JSON: {historie_json_path}")
            self.log(f"    📄 Text: {historie_txt_path}")
            
        except Exception as e:
            self.log(f"  ⚠️ Historie View Integration fehlgeschlagen: {e}")
            import traceback
            self.log(f"    📋 Traceback: {traceback.format_exc()}")

    def _save_character(self, charakter: Charakter, char_name: str, save_dir: str) -> Path:
        """Speichert den Charakter als JSON"""
        chars_ordner = project_root / "chars" / save_dir
        chars_ordner.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        dateiname = f"{safe_name}_{timestamp}.json"
        dateipfad = chars_ordner / dateiname

        self.log(f"\n💾 SPEICHERE CHARAKTER: {dateipfad}")

        speichern_als_json(charakter, str(dateipfad))

        if dateipfad.exists():
            dateigröße = dateipfad.stat().st_size
            self.log(f"✅ Erfolgreich gespeichert ({dateigröße:,} Bytes)")
        else:
            raise CharacterGenerationError("Datei wurde nicht erstellt")

        return dateipfad

    def _apply_template_advances(self, charakter: Charakter, advances: List[Dict]) -> None:
        """Wendet Template-Aufstiege an"""
        self.log("--- SCHRITT 9: TEMPLATE-AUFSTIEGE ANWENDEN ---")
        
        if not advances:
            self.log("  ℹ️ Keine Template-Aufstiege definiert")
            return
            
        # Importiere Character Advancement Funktionen
        from functions.character_advancement import steigere_attribut, update_rang
        from functions.eigenschaften_funktionen import steigere_fertigkeit
        from functions.talent_funktionen import get_talent_manager
        
        advances_applied = 0
        
        for advance in advances:
            advance_type = advance.get('type')
            advance_name = advance.get('name', '')
            advance_value = advance.get('value')
            
            self.log(f"  🎯 Aufstieg {advance_type}: {advance_name}")
            
            # Stelle sicher dass genügend Aufstiege verfügbar sind
            if charakter.verbleibende_aufstiege <= 0:
                charakter.verbleibende_aufstiege += 1
                charakter.aufstiege_gesamt += 1
                self.log(f"    ⚡ Aufstieg hinzugefügt (gesamt: {charakter.aufstiege_gesamt})")
            
            success = False
            
            if advance_type == 'attribute':
                success = steigere_attribut(charakter, advance_name)
                if success:
                    self.log(f"    ✅ Attribut {advance_name} gesteigert")
                
            elif advance_type == 'skill':
                # Finde Fertigkeit
                for skill_key in charakter.fertigkeiten.keys():
                    if advance_name.lower() in skill_key.lower():
                        success = steigere_fertigkeit(charakter, skill_key, confirm_double_cost=True)
                        if success:
                            self.log(f"    ✅ Fertigkeit {advance_name} gesteigert")
                        break
                        
            elif advance_type == 'edge':
                talent_manager = get_talent_manager(charakter)
                for talent_key in charakter.talente.keys():
                    if advance_name.lower() in talent_key.lower():
                        success = talent_manager.waehle_talent(talent_key)
                        if success:
                            self.log(f"    ✅ Talent {advance_name} gewählt")
                        break
                        
            elif advance_type == 'power':
                # Suche Macht
                if hasattr(charakter, 'maechte') and charakter.maechte:
                    for macht_key, macht_obj in charakter.maechte.items():
                        if advance_name.lower() in macht_key.lower():
                            if hasattr(macht_obj, 'ausgewaehlt'):
                                macht_obj.ausgewaehlt = True
                            if hasattr(macht_obj, 'aktiv'):
                                macht_obj.aktiv = True
                            success = True
                            self.log(f"    ✅ Macht {advance_name} gewählt")
                            break
            
            if success:
                advances_applied += 1
            else:
                self.log(f"    ❌ Aufstieg {advance_type}:{advance_name} fehlgeschlagen")
        
        # Rang aktualisieren
        update_rang(charakter)
        
        self.log(f"📊 AUFSTIEGE ANGEWENDET: {advances_applied}/{len(advances)}")
        
    def _use_remaining_advances_for_improvements(self, charakter: Charakter) -> None:
        """Verwendet verbleibende Aufstiege für weitere Verbesserungen basierend auf Template"""
        self.log("--- VERBLEIBENDE AUFSTIEGE NUTZEN ---")
        
        while charakter.verbleibende_aufstiege > 0:
            advance_used = False
            
            # Versuche Template-Attribute weiter zu steigern
            target_attributes = self.current_template.get('attributes', {})
            for attr_name, target_value in target_attributes.items():
                if attr_name in charakter.attribute:
                    current_value = charakter.attribute[attr_name].wuerfel.value
                    if current_value < 12 and current_value < target_value + 2:  # Erlaube Steigerung über Template hinaus
                        from functions.character_advancement import steigere_attribut
                        success = steigere_attribut(charakter, attr_name)
                        if success:
                            self.log(f"  ✅ {attr_name} durch Aufstieg gesteigert auf W{charakter.attribute[attr_name].wuerfel.value}")
                            advance_used = True
                            break
            
            # Falls kein Attribut gesteigert wurde, versuche Fertigkeiten
            if not advance_used:
                target_skills = self.current_template.get('skills', {})
                for skill_name, target_value in target_skills.items():
                    # Finde die Fertigkeit
                    for key, skill_obj in charakter.fertigkeiten.items():
                        if skill_name.lower() in key.lower():
                            current_effective = skill_obj.wuerfel.value + skill_obj.wuerfel.modifier
                            if current_effective < 12 and current_effective < target_value + 2:  # Erlaube Steigerung über Template hinaus
                                from functions.eigenschaften_funktionen import steigere_fertigkeit
                                success = steigere_fertigkeit(charakter, key, confirm_double_cost=True)
                                if success:
                                    new_effective = skill_obj.wuerfel.value + skill_obj.wuerfel.modifier
                                    self.log(f"  ✅ {skill_name} durch Aufstieg gesteigert auf W{new_effective}")
                                    advance_used = True
                                    break
                    if advance_used:
                        break
            
            # Falls immer noch kein Aufstieg verwendet wurde, beende die Schleife
            if not advance_used:
                self.log(f"  ⚠️ Keine weitere Steigerung möglich, verbleibende Aufstiege: {charakter.verbleibende_aufstiege}")
                break
        
        self.log(f"📊 VERBLEIBENDE AUFSTIEGE GENUTZT: {charakter.verbleibende_aufstiege} übrig")

    def _should_complete_character_generation(self, charakter: Charakter) -> bool:
        """Prüft ob Charaktergenerierung automatisch abgeschlossen werden sollte"""
        # Prüfe ob keine Punkte mehr verfügbar sind
        no_attribute_points = charakter.verbleibende_attributsteigerungen <= 0
        no_skill_points = charakter.verbleibende_fertigkeitssteigerungen <= 0  
        no_handicap_points = charakter.verbleibende_handicap_punkte <= 0
        
        all_points_used = no_attribute_points and no_skill_points and no_handicap_points
        
        self.log(f"  📊 Punktestand - Attr: {charakter.verbleibende_attributsteigerungen}, "
                f"Skill: {charakter.verbleibende_fertigkeitssteigerungen}, "
                f"Handicap: {charakter.verbleibende_handicap_punkte}")
        
        # NEUE LOGIK: Verwende Aufstiege wenn alle Standardpunkte aufgebraucht sind
        if all_points_used and hasattr(charakter, 'verbleibende_aufstiege') and charakter.verbleibende_aufstiege > 0:
            self.log(f"  ⭐ Verwende verbleibende Aufstiege: {charakter.verbleibende_aufstiege}")
            self._use_remaining_advances_for_improvements(charakter)
            return False  # Charaktergenerierung noch nicht beenden
        
        return all_points_used

    def _complete_character_generation(self, charakter: Charakter) -> None:
        """Schließt die Charaktergenerierung ab und aktiviert Aufstiegsmodus"""
        self.log("--- SCHRITT 10: CHARAKTERGENERIERUNG ABSCHLIESSEN ---")
        
        # Charaktergenerierung als abgeschlossen markieren
        charakter.char_gen_completed = True
        
        # Aufstiege für weitere Entwicklung setzen
        if charakter.aufstiege_gesamt == 0:
            charakter.aufstiege_gesamt = 1  # Mindestens 1 Aufstieg für Anfänger
        
        # Berechne verbleibende Aufstiege aus nicht verwendeten Punkten
        remaining_attr_points = max(0, charakter.verbleibende_attributsteigerungen)
        remaining_skill_points = max(0, charakter.verbleibende_fertigkeitssteigerungen)
        remaining_handicap_points = max(0, charakter.verbleibende_handicap_punkte)
        
        # Konvertiere übrige Punkte in Aufstiege (grobe Schätzung)
        # 2 Attribut/Fertigkeitspunkte = 1 Aufstieg, 2 Handicappunkte = 1 Aufstieg
        total_remaining_points = remaining_attr_points + remaining_skill_points + remaining_handicap_points
        additional_advances = total_remaining_points // 2  # Integer-Division
        
        charakter.verbleibende_aufstiege = additional_advances
        
        # Punkte auf 0 setzen da sie in Aufstiege umgewandelt wurden
        charakter.verbleibende_attributsteigerungen = 0
        charakter.verbleibende_fertigkeitssteigerungen = 0
        charakter.verbleibende_handicap_punkte = 0
        
        # Rang basierend auf Aufstiegen setzen
        from functions.character_advancement import update_rang
        update_rang(charakter)
        
        self.log(f"  ✅ char_gen_completed = True")
        self.log(f"  🎯 Aufstiege gesamt: {charakter.aufstiege_gesamt}")
        self.log(f"  ⭐ Verbleibende Aufstiege: {charakter.verbleibende_aufstiege}")
        self.log(f"  👑 Rang: {charakter.rang}")
        
        if additional_advances > 0:
            self.log(f"  🔄 {total_remaining_points} übrige Punkte in {additional_advances} Aufstiege umgewandelt")

    def log(self, message: str) -> None:
        """Loggt eine Nachricht"""
        print(message)
        self.generation_log.append(message)


# Convenience-Funktionen
def generate_character_from_json(json_path: str, output_dir: str = None) -> Path:
    """
    Generiert einen Charakter aus einer JSON-Datei.

    Args:
        json_path: Pfad zur JSON-Template-Datei
        output_dir: Ausgabeordner (optional)

    Returns:
        Path zur gespeicherten JSON-Datei
    """
    generator = AutoCharacterGenerator()
    return generator.generate_from_template(json_path, output_dir=output_dir)


def generate_character_from_dict(template_dict: Dict, output_dir: str = None) -> Path:
    """
    Generiert einen Charakter aus einem Dictionary.

    Args:
        template_dict: Template als Dictionary
        output_dir: Ausgabeordner (optional)

    Returns:
        Path zur gespeicherten JSON-Datei
    """
    generator = AutoCharacterGenerator()
    return generator.generate_from_template(template_dict, output_dir=output_dir)


if __name__ == '__main__':
    # Beispiel-Usage
    print("🎯 AUTO CHARACTER GENERATOR - ÜBERARBEITETE VERSION")
    print("Universelle Savage Worlds Charaktergenerierung aus JSON-Templates")
    print("✨ NEU: Ignoriert Voraussetzungen und erhöht automatisch Punkte")
    print("📊 NEU: Erstellt detailliertes Kosten-Log")
    print("\nVerwende generate_character_from_json() oder generate_character_from_dict()")