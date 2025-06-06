# migration/voelker_migration.py
"""
Migrationsskript zum Konvertieren bestehender Völker-Daten 
auf das neue Format mit strukturierten Effekten.
"""

import json
import os
from kivy.logger import Logger

def migrate_voelker_data(input_file_path, output_file_path=None):
    """
    Migriert Völker-Daten von Text-basierten Effekten zu strukturierten Effekten.
    
    Args:
        input_file_path: Pfad zur Eingabedatei
        output_file_path: Pfad zur Ausgabedatei (None = überschreibt Eingabedatei)
    """
    try:
        # Eingabedatei laden
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'voelker' not in data:
            Logger.error("Keine 'voelker' Sektion in der Datei gefunden")
            return False
        
        # Jeden Volk migrieren
        for volk_name, volk_data in data['voelker'].items():
            Logger.info(f"Migriere Volk: {volk_name}")
            migrated_effects = _migrate_single_volk(volk_name, volk_data)
            volk_data['effects'] = migrated_effects
        
        # Ausgabedatei bestimmen
        if output_file_path is None:
            output_file_path = input_file_path
        
        # Migrierte Daten speichern
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        Logger.info(f"Migration erfolgreich abgeschlossen. Datei gespeichert: {output_file_path}")
        return True
        
    except Exception as e:
        Logger.error(f"Fehler bei der Migration: {e}")
        return False

def _migrate_single_volk(volk_name, volk_data):
    """
    Migriert ein einzelnes Volk zu strukturierten Effekten.
    
    Args:
        volk_name: Name des Volks
        volk_data: Daten des Volks
        
    Returns:
        dict: Strukturierte Effekte
    """
    effects = {
        'attribute_bonuses': {},      
        'robustheit_bonus': 0,        
        'bewegungsweite_bonus': 0,    
        'fertigkeits_startboni': {},  
        'auto_talente': [],           
        'spezielle_effekte': {},      
        'wahlmoeglichkeiten': {}      
    }
    
    # Alle Texte sammeln (Handicaps + Besonderheiten)
    all_texts = []
    all_texts.extend(volk_data.get('handicaps', []))
    all_texts.extend(volk_data.get('besonderheiten', []))
    all_texts.extend(volk_data.get('talente', []))
    
    # Volk-spezifische Migrationen
    if volk_name == "Elf":
        effects['attribute_bonuses'] = {
            'Geschicklichkeit': 2,  # W4 -> W6
            'Verstand': 2,
            'Wahrnehmung': 2  # Falls als Attribut behandelt
        }
        effects['fertigkeits_startboni'] = {'Wahrnehmung': 2}
        effects['robustheit_bonus'] = -1  # Schlank
        effects['spezielle_effekte'] = {
            'elfenmagie': True,
            'nachtsicht': True,
            'geschaerfte_sinne': True
        }
    
    elif volk_name == "Gnom":
        effects['robustheit_bonus'] = -1  # Größe -1
        effects['bewegungsweite_bonus'] = -1  # Verringerte Bewegungsweite
        effects['attribute_bonuses'] = {'Konstitution': 2}
        effects['fertigkeits_startboni'] = {'Wahrnehmung': 2}
        effects['wahlmoeglichkeiten'] = {'freie_verstandsfertigkeit': True}
        effects['spezielle_effekte'] = {
            'gnomenmagie': True,
            'nachtsicht': True,
            'geschaerfte_sinne': True
        }
    
    elif volk_name == "Halbelf":
        effects['wahlmoeglichkeiten'] = {'freies_attribut': True}
        effects['spezielle_effekte'] = {
            'elfenmagie': True,
            'nachtsicht': True
        }
    
    elif volk_name == "Halbling":
        effects['robustheit_bonus'] = -1  # Größe -1
        effects['bewegungsweite_bonus'] = -1  # Verringerte Bewegungsweite
        effects['attribute_bonuses'] = {'Geschicklichkeit': 2}
        effects['fertigkeits_startboni'] = {
            'Wahrnehmung': 2,
            'Athletik': 2
        }
        effects['auto_talente'] = ['Glück']
    
    elif volk_name == "Halbork":
        effects['robustheit_bonus'] = 1  # Orkische Wildheit
        effects['attribute_bonuses'] = {'Stärke': 2}
        effects['fertigkeits_startboni'] = {'Einschüchtern': 0}  # W4-2 -> W4+0
        effects['spezielle_effekte'] = {'dunkelsicht': True}
    
    elif volk_name == "Mensch":
        effects['wahlmoeglichkeiten'] = {
            'freies_talent': True,
            'freies_attribut': True  # Nur in Savage Pathfinder aktiv
        }
    
    elif volk_name == "Zwerg":
        effects['bewegungsweite_bonus'] = -1  # Verringerte Bewegungsweite
        effects['attribute_bonuses'] = {'Konstitution': 2}
        effects['spezielle_effekte'] = {
            'dunkelsicht': True,
            'eiserne_konstitution': True,
            'steingespür': True,
            'staerke_bonus_traglast': True
        }
    
    # Generische Text-basierte Erkennung für unbekannte Völker
    for text in all_texts:
        _parse_generic_effects(text, effects)
    
    Logger.debug(f"Migrierte Effekte für {volk_name}: {effects}")
    return effects

def _parse_generic_effects(text, effects):
    """
    Parst generische Effekte aus Textbeschreibungen.
    VERBESSERT: Robustere Erkennung von Effekten in verschiedenen Formulierungen.
    
    Args:
        text: Textbeschreibung
        effects: Effekte-Dictionary zum Aktualisieren
    """
    text_lower = text.lower()
    
    # Attribut-Boni erkennen (auch in Klammern)
    attribute = ['stärke', 'geschicklichkeit', 'konstitution', 'verstand', 'willenskraft']
    for attr in attribute:
        if f"{attr} w6 statt w4" in text_lower:
            attr_name = attr.capitalize()
            effects['attribute_bonuses'][attr_name] = 2
    
    # Fertigkeits-Boni erkennen (auch in Klammern)
    fertigkeiten = ['wahrnehmung', 'athletik', 'einschüchtern', 'kämpfen']
    for fert in fertigkeiten:
        if f"{fert} w6 statt w4" in text_lower:
            fert_name = fert.capitalize()
            effects['fertigkeits_startboni'][fert_name] = 2
        elif f"beginnt mit w4 in {fert}" in text_lower:
            fert_name = fert.capitalize()
            effects['fertigkeits_startboni'][fert_name] = 0
    
    # Robustheit-Effekte (verschiedene Formulierungen)
    if any(phrase in text_lower for phrase in [
        "robustheit um 1", "-1 robustheit", "(-1 robustheit", 
        "reduzierte robustheit um 1", "größe -1", "schlank"
    ]):
        # Prüfe, ob es ein Malus ist
        if any(neg in text_lower for neg in ["-1", "reduzierte", "schlank", "größe -1"]):
            effects['robustheit_bonus'] -= 1
        else:
            effects['robustheit_bonus'] += 1
    elif any(phrase in text_lower for phrase in ["+1 robustheit", "orkische wildheit"]):
        effects['robustheit_bonus'] += 1
    
    # Bewegungsweite-Effekte (verschiedene Formulierungen)
    if any(phrase in text_lower for phrase in [
        "verringerte bewegungsweite", "-1 bewegungsweite", "bewegungsweite -1"
    ]):
        effects['bewegungsweite_bonus'] -= 1
    
    # Wahlmöglichkeiten erkennen
    if any(phrase in text_lower for phrase in ["freies talent", "anpassungsfähigkeit"]):
        effects['wahlmoeglichkeiten']['freies_talent'] = True
    
    if any(phrase in text_lower for phrase in [
        "w6 in einem attribut statt w4", "flexibilität"
    ]):
        effects['wahlmoeglichkeiten']['freies_attribut'] = True
    
    if any(phrase in text_lower for phrase in [
        "verstandsbasierten fertigkeit auf w4", "zwanghaft"
    ]):
        effects['wahlmoeglichkeiten']['freie_verstandsfertigkeit'] = True
    
    # Spezielle Effekte
    spezial_mapping = {
        'elfenmagie': ['elfenmagie'],
        'nachtsicht': ['nachtsicht', 'dunkelsicht'],
        'steingespür': ['steingespür'],
        'gnomenmagie': ['gnomenmagie'],
        'eiserne_konstitution': ['eiserne konstitution'],
        'geschaerfte_sinne': ['geschärfte sinne'],
        'orkische_wildheit': ['orkische wildheit']
    }
    
    for effect_name, keywords in spezial_mapping.items():
        if any(keyword in text_lower for keyword in keywords):
            effects['spezielle_effekte'][effect_name] = True
    
    # Automatische Talente erkennen
    if "glück" in text_lower and any(phrase in text_lower for phrase in [
        "zusätzlicher benny", "benny pro spielsitzung"
    ]):
        if "Glück" not in effects['auto_talente']:
            effects['auto_talente'].append("Glück")

def create_sample_migrated_data():
    """
    Erstellt eine Beispieldatei mit migrierten Völker-Daten zum Testen.
    """
    sample_data = {
        "voelker": {
            "Mensch": {
                "name": "Mensch",
                "handicaps": [],
                "talente": [],
                "besonderheiten": [
                    "Anpassungsfähigkeit (Freies Talent und W6 in einem Attribut statt W4, erhöht Maximum nicht)"
                ],
                "sprachen": ["Gemeinsprache"],
                "altersspanne": "Erwachsen mit 17, Alt mit 53, maximales Alter 70–110",
                "groesse_maennlich": "1,50-1,95m, 54-100kg (Durchschnitt 1,70m, 79kg)",
                "groesse_weiblich": "1,50-1,85m, 43-84kg (Durchschnitt 1,60m, 64kg)",
                "aktiv": True,
                "custom": False,
                "effects": {
                    "attribute_bonuses": {},
                    "robustheit_bonus": 0,
                    "bewegungsweite_bonus": 0,
                    "fertigkeits_startboni": {},
                    "auto_talente": [],
                    "spezielle_effekte": {},
                    "wahlmoeglichkeiten": {
                        "freies_talent": True,
                        "freies_attribut": True
                    }
                }
            }
        }
    }
    
    with open("sample_migrated_voelker.json", 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=4)
    
    print("Beispieldatei 'sample_migrated_voelker.json' erstellt")

if __name__ == "__main__":
    # Beispiel-Aufruf
    # migrate_voelker_data("path/to/input/setting.json", "path/to/output/setting.json")
    
    # Erstelle Beispieldatei zum Testen
    create_sample_migrated_data()
    
    print("Migration verfügbar. Verwendung:")
    print("migrate_voelker_data('input.json', 'output.json')")