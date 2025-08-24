#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO CHARACTER GENERATOR
Universelle Funktion zur automatischen Charaktergenerierung aus JSON-Templates.
Basiert auf den bewährten Test-Templates für Leomara und Hesindian.
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
from charakter import Charakter
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
    """
    
    def __init__(self):
        self.generated_characters = []
        self.generation_log = []
    
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
            # Template laden und validieren
            template_data = self._load_template(template)
            self._validate_template(template_data)
            
            # Generierungsoptionen
            options = template_data.get('generation_options', {})
            strict_points = options.get('strict_point_allocation', True)
            allow_over_attr = options.get('allow_over_attribute', True)
            auto_save = options.get('auto_save', True)
            
            char_name = template_data['name']
            self.log(f"🎯 STARTE CHARAKTERGENERIERUNG: {char_name.upper()}")
            
            # SCHRITT 1: CHARAKTER INITIALISIEREN
            setting_name = custom_setting or template_data.get('setting', 'SWAE')
            charakter = self._initialize_character(template_data, setting_name)
            
            # SCHRITT 2: VOLK UND VÖLKER-BONI
            race_name = template_data.get('race', 'Mensch')
            free_race_edge = self._apply_race(charakter, race_name, template_data)
            
            # SCHRITT 3: ATTRIBUTE STEIGERN
            target_attributes = template_data['attributes']
            attr_costs = self._advance_attributes(charakter, target_attributes)
            
            # SCHRITT 4: HANDICAPS HINZUFÜGEN
            handicaps = template_data['handicaps']
            handicap_points = self._add_handicaps(charakter, handicaps)
            
            # SCHRITT 4B: WEITERE ATTRIBUTSTEIGERUNGEN MIT HANDICAP-PUNKTEN
            if handicap_points > 0:
                additional_attr_costs = self._advance_attributes_with_handicap_points(
                    charakter, target_attributes, handicap_points
                )
                attr_costs += additional_attr_costs
            
            # SCHRITT 5: FERTIGKEITEN STEIGERN
            target_skills = template_data['skills']
            skill_costs = self._advance_skills(charakter, target_skills, 
                                             handicap_points, allow_over_attr)
            
            # SCHRITT 6: TALENTE WÄHLEN
            edges = template_data['edges']
            edge_costs = self._select_edges(charakter, edges, free_race_edge)
            
            # SCHRITT 7: MÄCHTE WÄHLEN
            powers = template_data.get('powers', [])
            power_points = template_data.get('power_points', 0)
            if powers or power_points > 0:
                self._select_powers(charakter, powers, power_points)
            
            # SCHRITT 8: AUSRÜSTUNG HINZUFÜGEN
            equipment = template_data.get('equipment', [])
            self._add_equipment(charakter, equipment)
            
            # VALIDIERUNG
            if strict_points:
                self._validate_point_allocation(attr_costs, skill_costs, edge_costs, handicap_points)
            
            # FINALE BERECHNUNGEN
            try:
                charakter.berechne_abgeleitete_werte()
            except RecursionError:
                self.log("⚠️ Warnung: Rekursionsproblem bei abgeleiteten Werten übersprungen")
            
            # CHARAKTERZUSAMMENFASSUNG
            self._print_character_summary(charakter, attr_costs, skill_costs, 
                                        edge_costs, handicap_points)
            
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
        
        self.log(f"  ✅ Charakter '{char_name}' initialisiert (Setting: {setting_name})")
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
    
    def _advance_attributes(self, charakter: Charakter, target_attrs: Dict[str, int]) -> int:
        """Steigert Attribute auf Zielwerte"""
        self.log("--- SCHRITT 3: ATTRIBUTE STEIGERN ---")
        
        total_costs = 0
        start_points = charakter.verbleibende_attributsteigerungen
        
        for attr_name, target_value in target_attrs.items():
            if attr_name not in charakter.attribute:
                self.log(f"  ⚠️ Attribut '{attr_name}' nicht gefunden - überspringe")
                continue
                
            attr = charakter.attribute[attr_name]
            current_value = attr.wuerfel.value
            
            if current_value >= target_value:
                continue
            
            # Berechne benötigte Steigerungen
            advances_needed = self._calculate_advances_needed(current_value, target_value)
            
            self.log(f"  {attr_name} (W{current_value} → W{target_value}):")
            
            for i in range(advances_needed):
                points_before = charakter.verbleibende_attributsteigerungen
                if points_before <= 0:
                    self.log(f"    Steigerung {i+1}: Keine Punkte mehr verfügbar")
                    break
                    
                success = charakter.steigere_attribut(attr_name)
                points_after = charakter.verbleibende_attributsteigerungen
                
                if success:
                    cost = points_before - points_after
                    total_costs += cost
                    new_value = attr.wuerfel.value
                    self.log(f"    Steigerung {i+1}: Erfolg → W{new_value} (Kosten: {cost})")
                else:
                    self.log(f"    Steigerung {i+1}: FEHLGESCHLAGEN")
                    break
        
        self.log(f"📊 ATTRIBUTSKOSTEN: {total_costs} von {start_points} Punkten")
        return total_costs
    
    def _add_handicaps(self, charakter: Charakter, handicaps: List[str]) -> int:
        """Fügt Handicaps hinzu"""
        self.log("--- SCHRITT 4: HANDICAPS HINZUFÜGEN ---")
        
        total_points = 0
        
        for handicap_name in handicaps:
            # Verschiedene Schreibweisen probieren
            variants = [handicap_name, handicap_name.replace("_", " "), handicap_name.lower()]
            added = False
            
            for variant in variants:
                if variant in charakter.handicaps:
                    success = waehle_handicap(charakter, variant)
                    if success:
                        handicap = charakter.handicaps[variant]
                        points = getattr(handicap, 'punkte', getattr(handicap, 'wert', 1))
                        total_points += points
                        self.log(f"  ✅ {variant} hinzugefügt: +{points} Punkte")
                        added = True
                        break
            
            if not added:
                self.log(f"  ❌ Handicap '{handicap_name}' nicht gefunden")
        
        self.log(f"📊 HANDICAP-PUNKTE GESAMT: +{total_points} Punkte")
        return total_points
    
    def _advance_attributes_with_handicap_points(self, charakter: Charakter, 
                                               target_attrs: Dict[str, int], 
                                               available_points: int) -> int:
        """Erweiterte Attributsteigerungen mit Handicap-Punkten"""
        self.log("--- SCHRITT 4B: WEITERE ATTRIBUTSTEIGERUNGEN ---")
        
        additional_costs = 0
        points_used = 0
        
        for attr_name, target_value in target_attrs.items():
            if points_used >= available_points:
                break
                
            if attr_name not in charakter.attribute:
                continue
                
            attr = charakter.attribute[attr_name]
            current_value = attr.wuerfel.value
            
            if current_value >= target_value:
                continue
            
            # Weitere Steigerungen mit Handicap-Punkten
            advances_needed = self._calculate_advances_needed(current_value, target_value)
            
            self.log(f"  {attr_name} (aktuell: W{current_value}, Ziel: W{target_value}):")
            
            for i in range(advances_needed):
                if points_used >= available_points:
                    self.log(f"    Weitere Steigerung {i+1}: Keine Handicap-Punkte mehr")
                    break
                
                success = charakter.steigere_attribut(attr_name)
                if success:
                    new_value = attr.wuerfel.value
                    points_used += 1
                    additional_costs += 1
                    self.log(f"    Weitere Steigerung {i+1}: W{new_value} (mit Handicap-Punkt)")
                else:
                    self.log(f"    Weitere Steigerung {i+1}: FEHLGESCHLAGEN")
                    break
        
        self.log(f"📊 ZUSÄTZLICHE ATTRIBUTSKOSTEN: {additional_costs} Handicap-Punkte")
        return additional_costs
    
    def _advance_skills(self, charakter: Charakter, target_skills: Dict[str, int],
                       handicap_points: int, allow_over_attribute: bool) -> int:
        """Steigert Fertigkeiten auf Zielwerte"""
        self.log("--- SCHRITT 5: FERTIGKEITEN STEIGERN ---")
        
        start_skill_points = 12  # Standard SWAE
        available_points = start_skill_points + handicap_points
        total_costs = 0
        
        self.log(f"Verfügbare Fertigkeitspunkte: {start_skill_points} + {handicap_points} = {available_points}")
        
        for skill_name, target_value in target_skills.items():
            if skill_name not in charakter.fertigkeiten:
                self.log(f"  ⚠️ Fertigkeit '{skill_name}' nicht gefunden - überspringe")
                continue
                
            skill = charakter.fertigkeiten[skill_name]
            current_value = skill.wuerfel.value
            current_modifier = skill.wuerfel.modifier
            effective_current = current_value + current_modifier
            
            if effective_current >= target_value:
                continue
            
            # Berechne benötigte Steigerungen
            advances_needed = self._calculate_skill_advances_needed(effective_current, target_value)
            
            attr_value = skill.attribut.wuerfel.value
            self.log(f"\n  {skill_name} (Attribut: {skill.attribut.attribut_name} W{attr_value}):")
            self.log(f"    Start: W{current_value}{'+' + str(current_modifier) if current_modifier > 0 else str(current_modifier) if current_modifier < 0 else ''}")
            
            for i in range(advances_needed):
                success = charakter.steigere_fertigkeit(skill_name, confirm_double_cost=allow_over_attribute)
                
                if success == True:
                    new_value = skill.wuerfel.value
                    new_modifier = skill.wuerfel.modifier
                    
                    # Kostenberechnung (vereinfacht)
                    if new_value > attr_value:
                        cost = 2  # Doppelte Kosten über Attribut
                    else:
                        cost = 1  # Normale Kosten
                    
                    total_costs += cost
                    available_points -= cost
                    
                    self.log(f"    Steigerung {i+1}: Erfolg → W{new_value}{'+' + str(new_modifier) if new_modifier > 0 else str(new_modifier) if new_modifier < 0 else ''} (Kosten: {cost})")
                elif success == "needs_confirmation":
                    self.log(f"    Steigerung {i+1}: Bestätigung erforderlich (über Attribut)")
                    if allow_over_attribute:
                        # Nochmal versuchen mit Bestätigung
                        success = charakter.steigere_fertigkeit(skill_name, confirm_double_cost=True)
                        if success:
                            new_value = skill.wuerfel.value
                            new_modifier = skill.wuerfel.modifier
                            cost = 2
                            total_costs += cost
                            available_points -= cost
                            self.log(f"    Steigerung {i+1}: Bestätigt → W{new_value}{'+' + str(new_modifier) if new_modifier > 0 else str(new_modifier) if new_modifier < 0 else ''} (Kosten: {cost})")
                    else:
                        break
                else:
                    self.log(f"    Steigerung {i+1}: FEHLGESCHLAGEN - {success}")
                    break
                
                if available_points <= 0:
                    self.log(f"    Keine Fertigkeitspunkte mehr verfügbar")
                    break
        
        self.log(f"\n📊 FERTIGKEITSKOSTEN GESAMT: {total_costs} Punkte")
        return total_costs
    
    def _select_edges(self, charakter: Charakter, edges: List[str], 
                     free_race_edge: Optional[str]) -> int:
        """Wählt Talente aus"""
        self.log("--- SCHRITT 6: TALENTE WÄHLEN ---")
        
        total_costs = 0
        
        # Kostenloses Völker-Talent
        if hasattr(charakter, 'voelker_boni') and charakter.voelker_boni.get('freie_talente', 0) > 0:
            self.log("  🎁 KOSTENLOSES VÖLKER-TALENT:")
            
            # Suche nach Arkaner Hintergrund für Menschen
            free_talent_name = free_race_edge
            if not free_talent_name:
                # Standard: Arkaner Hintergrund für Zauberer
                for name in charakter.talente.keys():
                    if "arkaner hintergrund" in name.lower() and "magie" not in name.lower():
                        free_talent_name = name
                        break
            
            if free_talent_name and free_talent_name in charakter.talente:
                success = waehle_freies_talent(charakter, free_talent_name, ignore_voraussetzungen=False)
                if success:
                    self.log(f"    ✅ Völker-Talent '{free_talent_name}' hinzugefügt (KOSTENLOS)")
                    charakter.voelker_boni['freie_talente'] -= 1
                else:
                    self.log(f"    ❌ FEHLER: Völker-Talent '{free_talent_name}' konnte nicht hinzugefügt werden")
        
        # Weitere Talente
        for edge_name in edges:
            self.log(f"\n  💫 TALENT: {edge_name}")
            if edge_name in charakter.talente:
                success = waehle_talent(charakter, edge_name)
                if success:
                    self.log(f"    ✅ Talent '{edge_name}' hinzugefügt")
                    total_costs += 1
                else:
                    self.log(f"    ❌ FEHLER: Talent '{edge_name}' konnte nicht hinzugefügt werden")
            else:
                self.log(f"    ❌ Talent '{edge_name}' nicht verfügbar")
        
        self.log(f"\n📊 TALENTKOSTEN GESAMT: {total_costs} Punkte")
        return total_costs
    
    def _select_powers(self, charakter: Charakter, powers: List[str], power_points: int) -> None:
        """Wählt Mächte aus"""
        self.log("--- SCHRITT 7: MÄCHTE WÄHLEN ---")
        
        # Prüfe Arkaner Hintergrund
        arcane_background = False
        for talent_name, talent_obj in charakter.talente.items():
            if "arkaner hintergrund" in talent_name.lower() and getattr(talent_obj, 'ausgewaehlt', False):
                arcane_background = True
                self.log(f"  ✅ Arkaner Hintergrund gefunden: {talent_name}")
                break
        
        if not arcane_background:
            self.log("  ❌ Kein Arkaner Hintergrund gefunden - keine Mächte verfügbar")
            return
        
        powers_added = 0
        for power_name in powers:
            if hasattr(charakter, 'maechte') and charakter.maechte:
                for key, power in charakter.maechte.items():
                    if power_name.lower() in key.lower():
                        if hasattr(power, 'ausgewaehlt'):
                            power.ausgewaehlt = True
                        if hasattr(power, 'aktiv'):
                            power.aktiv = True
                        self.log(f"  ✅ {power_name} gefunden und ausgewählt")
                        powers_added += 1
                        break
                else:
                    self.log(f"  ❌ {power_name} nicht gefunden")
            else:
                self.log(f"  ❌ {power_name} nicht verfügbar")
        
        # Machtpunkte setzen
        if power_points > 0:
            if hasattr(charakter, 'machtpunkte'):
                charakter.machtpunkte = power_points
                self.log(f"  🔮 Machtpunkte gesetzt: {power_points}")
            else:
                self.log("  ⚠️ Machtpunkte-Property nicht gefunden")
        
        self.log(f"📊 MÄCHTE GESAMT: {powers_added} Mächte hinzugefügt")
    
    def _add_equipment(self, charakter: Charakter, equipment: List[Union[str, Dict]]) -> None:
        """Fügt Ausrüstung hinzu"""
        self.log("--- SCHRITT 8: AUSRÜSTUNG HINZUFÜGEN ---")
        
        items_added = 0
        for item in equipment:
            if isinstance(item, str):
                # Einfacher Gegenstandsname
                success = self._add_simple_equipment(charakter, item)
                if success:
                    items_added += 1
            elif isinstance(item, dict):
                # Custom Equipment-Objekt
                success = self._add_custom_equipment(charakter, item)
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
                self.log(f"    ✅ {item_name} erfolgreich hinzugefügt")
                return True
            else:
                self.log(f"    ❌ FEHLER: {item_name} konnte nicht hinzugefügt werden")
                return False
                
        except Exception as e:
            self.log(f"    ❌ FEHLER beim Anlegen von {item_name}: {e}")
            return False
    
    def _add_custom_equipment(self, charakter: Charakter, item_data: Dict) -> bool:
        """Fügt Custom Equipment hinzu"""
        item_name = item_data['name']
        item_type = item_data['type']
        
        self.log(f"  🔧 Custom {item_type}: {item_name}")
        
        try:
            if item_type == 'weapon':
                from models.waffe import Waffe
                props = item_data.get('properties', {})
                custom_item = Waffe(
                    name=item_name,
                    gewicht=item_data.get('weight', 1),
                    kosten=item_data.get('cost', 0),
                    setting="custom",
                    typ="Nahkampf",
                    mindeststaerke=props.get('min_strength', 'W4'),
                    beschreibung=item_data.get('description', f'Custom {item_name}'),
                    eigenschaften={
                        'schaden': props.get('damage', 'Stärke+W4'),
                        'ap': props.get('ap', 0),
                        'reichweite': props.get('range', '0'),
                        'parade_bonus': props.get('parry_bonus', 0),
                        'zweihändig': props.get('two_handed', False)
                    },
                    menge=1,
                    ausgewaehlt=True,
                    aktiv=True,
                    kategorie=item_data.get('category', 'Custom Waffe'),
                    custom=True
                )
                charakter.waffen[item_name] = custom_item
                
            elif item_type == 'armor':
                from models.ruestung import Ruestung
                props = item_data.get('properties', {})
                custom_item = Ruestung(
                    name=item_name,
                    torso=props.get('armor_torso', 1),
                    arme=props.get('armor_arms', 1),
                    beine=props.get('armor_legs', 0),
                    kopf=props.get('armor_head', 0),
                    mindeststaerke=props.get('min_strength', 'W4'),
                    setting="custom",
                    gewicht=item_data.get('weight', 2),
                    kosten=item_data.get('cost', 50),
                    beschreibung=item_data.get('description', f'Custom {item_name}'),
                    menge=1,
                    ausgewaehlt=True,
                    aktiv=True,
                    kategorie=item_data.get('category', 'Custom Rüstung'),
                    custom=True
                )
                charakter.ruestungen[item_name] = custom_item
                
            elif item_type == 'shield':
                from models.schild import Schild
                props = item_data.get('properties', {})
                custom_item = Schild(
                    name=item_name,
                    gewicht=item_data.get('weight', 2),
                    kosten=item_data.get('cost', 25),
                    setting="custom",
                    parade=props.get('parry_bonus', 1),
                    deckung=props.get('cover', 2),
                    mindeststaerke=props.get('min_strength', 'W4'),
                    beschreibung=item_data.get('description', f'Custom {item_name}'),
                    menge=1,
                    ausgewaehlt=True,
                    aktiv=True,
                    kategorie=item_data.get('category', 'Custom Schild'),
                    custom=True
                )
                charakter.schilde[item_name] = custom_item
                
            else:
                # Standard Equipment
                from models.ausruestung import Ausruestung
                custom_item = Ausruestung(
                    name=item_name,
                    gewicht=item_data.get('weight', 1),
                    kosten=item_data.get('cost', 10),
                    setting="custom",
                    beschreibung=item_data.get('description', f'Custom {item_name}'),
                    menge=1,
                    ausgewaehlt=True,
                    aktiv=True,
                    kategorie=item_data.get('category', 'Custom'),
                    custom=True
                )
            
            success = charakter.add_ausruestung(custom_item)
            if success:
                self.log(f"    ✅ Custom {item_type} '{item_name}' erfolgreich hinzugefügt")
                return True
            else:
                self.log(f"    ❌ FEHLER: Custom {item_type} '{item_name}' konnte nicht hinzugefügt werden")
                return False
                
        except Exception as e:
            self.log(f"    ❌ FEHLER beim Anlegen von Custom {item_type} '{item_name}': {e}")
            return False
    
    def _calculate_advances_needed(self, current: int, target: int) -> int:
        """Berechnet benötigte Attributssteigerungen"""
        if current >= target:
            return 0
        
        # W4->W6->W8->W10->W12
        dice_progression = [4, 6, 8, 10, 12]
        
        current_idx = dice_progression.index(current) if current in dice_progression else 0
        target_idx = dice_progression.index(target) if target in dice_progression else len(dice_progression) - 1
        
        return max(0, target_idx - current_idx)
    
    def _calculate_skill_advances_needed(self, current_effective: int, target: int) -> int:
        """Berechnet benötigte Fertigkeitssteigerungen"""
        if current_effective >= target:
            return 0
        
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
    
    def _validate_point_allocation(self, attr_costs: int, skill_costs: int, 
                                 edge_costs: int, handicap_points: int) -> None:
        """Validiert die Punkteverteilung"""
        self.log("--- PUNKTEVALIDIERUNG ---")
        
        start_attr_points = 5
        start_skill_points = 12
        
        total_costs = attr_costs + skill_costs + edge_costs
        available_points = start_attr_points + start_skill_points + handicap_points
        
        balance = available_points - total_costs
        
        self.log(f"Gesamtkosten: {total_costs} Punkte")
        self.log(f"Verfügbare Punkte: {available_points} Punkte")
        self.log(f"Bilanz: {balance} Punkte")
        
        if balance < 0:
            raise CharacterGenerationError(f"Punktedefizit: {balance} Punkte - Charakter nicht realisierbar")
        elif balance > 0:
            self.log(f"⚠️ Warnung: {balance} Punkte unverwendet")
    
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
    
    def _print_character_summary(self, charakter: Charakter, attr_costs: int, 
                               skill_costs: int, edge_costs: int, handicap_points: int) -> None:
        """Druckt Charakterzusammenfassung"""
        self.log("\n" + "="*80)
        self.log("📊 CHARAKTERZUSAMMENFASSUNG")
        self.log("="*80)
        
        self.log(f"Charakter: {charakter.profil_daten.get('Name', 'Unbenannt')}")
        self.log(f"Setting: {charakter.active_setting_name}")
        
        self.log(f"\n💰 KOSTENÜBERSICHT:")
        self.log(f"Attribute: {attr_costs} Punkte")
        self.log(f"Fertigkeiten: {skill_costs} Punkte") 
        self.log(f"Handicaps: +{handicap_points} Punkte")
        self.log(f"Talente: {edge_costs} Punkte")
        
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
                self.log(f"  {talent_name}")
        
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
                    self.log(f"  {macht_name}")
        
        if hasattr(charakter, 'machtpunkte') and charakter.machtpunkte > 0:
            self.log(f"Machtpunkte: {charakter.machtpunkte}")
    
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
    print("🎯 AUTO CHARACTER GENERATOR")
    print("Universelle Savage Worlds Charaktergenerierung aus JSON-Templates")
    print("Verwende generate_character_from_json() oder generate_character_from_dict()")