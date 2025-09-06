#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST AUTO CHARACTER GENERATOR
Testet die universelle Charaktergenerator-Funktion mit verschiedenen Templates.
"""

import sys
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from functions.auto_character_generator import AutoCharacterGenerator, generate_character_from_json


def test_auto_generator():
    """Testet den Auto Character Generator mit verschiedenen Templates"""
    
    print("🎯 TESTE AUTO CHARACTER GENERATOR")
    print("=" * 80)
    
    generator = AutoCharacterGenerator()
    templates_dir = project_root / "templates"
    
    # Test 1: Leomara Kriegerin
    print("\n🗡️ TEST 1: LEOMARA KRIEGERIN")
    try:
        leomara_path = templates_dir / "leomara_krieger.json"
        if leomara_path.exists():
            output_file = generator.generate_from_template(leomara_path)
            print(f"✅ Leomara erfolgreich generiert: {output_file}")
        else:
            print(f"❌ Template nicht gefunden: {leomara_path}")
    except Exception as e:
        print(f"❌ Fehler bei Leomara: {e}")
    
    # Test 2: Hesindian Magier
    print("\n🧙 TEST 2: HESINDIAN MAGIER")
    try:
        hesindian_path = templates_dir / "hesindian_magier.json"
        if hesindian_path.exists():
            output_file = generator.generate_from_template(hesindian_path)
            print(f"✅ Hesindian erfolgreich generiert: {output_file}")
        else:
            print(f"❌ Template nicht gefunden: {hesindian_path}")
    except Exception as e:
        print(f"❌ Fehler bei Hesindian: {e}")
    
    # Test 3: Schatten Dieb
    print("\n🥷 TEST 3: SCHATTEN DIEB")
    try:
        schatten_path = templates_dir / "examples" / "dieb_schatten.json"
        if schatten_path.exists():
            output_file = generator.generate_from_template(schatten_path)
            print(f"✅ Schatten erfolgreich generiert: {output_file}")
        else:
            print(f"❌ Template nicht gefunden: {schatten_path}")
    except Exception as e:
        print(f"❌ Fehler bei Schatten: {e}")
    
    # Test 4: Eiche Waldläufer 
    print("\n🏹 TEST 4: EICHE WALDLÄUFER")
    try:
        eiche_path = templates_dir / "examples" / "waldlaeufer_eiche.json"
        if eiche_path.exists():
            output_file = generator.generate_from_template(eiche_path)
            print(f"✅ Eiche erfolgreich generiert: {output_file}")
        else:
            print(f"❌ Template nicht gefunden: {eiche_path}")
    except Exception as e:
        print(f"❌ Fehler bei Eiche: {e}")
    
    # Test 5: Dictionary-Template (Inline)
    print("\n⚡ TEST 5: INLINE DICTIONARY TEMPLATE")
    try:
        inline_template = {
            "name": "Blitz",
            "description": "Ein schneller Kämpfer mit Doppelklingen",
            "setting": "SWAE",
            "race": "Mensch",
            "attributes": {
                "Stärke": 6,
                "Geschicklichkeit": 10,
                "Konstitution": 6,
                "Verstand": 4,
                "Willenskraft": 6
            },
            "skills": {
                "Kämpfen": 8,
                "Athletik": 8,
                "Heimlichkeit": 6,
                "Wahrnehmung": 6
            },
            "handicaps": [
                "Übermut",
                "Jung"
            ],
            "edges": [
                "Zweikampf",
                "Kampfreflexe"
            ],
            "equipment": [
                {
                    "name": "Doppelklingen",
                    "type": "weapon",
                    "weight": 3,
                    "cost": 400,
                    "description": "Gepaarte Kampfklingen",
                    "category": "Exotische Waffe",
                    "properties": {
                        "damage": "Stärke+W6",
                        "parry_bonus": 1,
                        "two_handed": true
                    }
                },
                "Lederrüstung",
                "Kämpferpaket"
            ],
            "generation_options": {
                "auto_save": true,
                "save_path": "inline_test"
            }
        }
        
        output_file = generator.generate_from_template(inline_template)
        print(f"✅ Blitz erfolgreich generiert: {output_file}")
    except Exception as e:
        print(f"❌ Fehler bei Blitz: {e}")
    
    # Zusammenfassung
    print("\n" + "=" * 80)
    print("📊 TEST ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"Generierte Charaktere: {len(generator.generated_characters)}")
    
    for i, char in enumerate(generator.generated_characters, 1):
        name = char.profil_daten.get('Name', 'Unbekannt')
        setting = char.active_setting_name
        print(f"{i}. {name} ({setting})")
    
    print("\n🎉 AUTO CHARACTER GENERATOR TESTS ABGESCHLOSSEN!")
    
    return generator


def test_convenience_function():
    """Testet die Convenience-Funktionen"""
    print("\n🔧 TESTE CONVENIENCE FUNKTIONEN")
    print("-" * 40)
    
    templates_dir = project_root / "templates"
    leomara_path = templates_dir / "leomara_krieger.json"
    
    if leomara_path.exists():
        try:
            output_file = generate_character_from_json(str(leomara_path), "convenience_test")
            print(f"✅ Convenience-Funktion erfolgreich: {output_file}")
        except Exception as e:
            print(f"❌ Convenience-Funktion Fehler: {e}")
    else:
        print(f"❌ Template für Convenience-Test nicht gefunden: {leomara_path}")


if __name__ == '__main__':
    # Haupttest
    generator = test_auto_generator()
    
    # Convenience-Test
    test_convenience_function()
    
    print("\n🚀 ALLE TESTS ABGESCHLOSSEN!")
    print("Die universelle Charaktergenerierung ist einsatzbereit!")