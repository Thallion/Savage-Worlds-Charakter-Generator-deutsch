#!/usr/bin/env python3
"""
Test der Änderungen für Savage Pathfinder Völker.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from models.volk import Volk

def create_mock_charakter():
    """Erstellt einen Mock-Charakter mit Savage Pathfinder Völkern."""
    class MockAttribut:
        def __init__(self, name, wert=4):
            self.attribut_name = name
            self.wert = wert
    
    class MockTalent:
        def __init__(self, name, aktiv=True, ausgewaehlt=False):
            self.name = name
            self.aktiv = aktiv
            self.ausgewaehlt = ausgewaehlt
    
    class MockCharakter:
        def __init__(self):
            self.voelker = {}
            self.voelker_selected = {}
            self.attribute = {}
            self.talente = {}
            self.selected_talente = []
            self._menschen_freies_attribut = None
            self._menschen_freies_talent = None
            self._halbelf_freies_talent = None
            self._halbelf_attribut_gewaehlt = False
        
        def berechne_abgeleitete_werte(self):
            pass
        
        def dispatch(self, event):
            print(f"Event dispatched: {event}")
    
    # Lade Savage Pathfinder Setting
    with open('../settings/Savage Pathfinder.json', 'r', encoding='utf-8') as f:
        setting_data = json.load(f)
    
    charakter = MockCharakter()
    
    # Attribute erstellen
    attribut_names = ["Geschicklichkeit", "Verstand", "Stärke", "Konstitution", "Willenskraft"]
    for name in attribut_names:
        charakter.attribute[name] = MockAttribut(name)
    
    # Völker erstellen
    for volk_key, volk_data in setting_data['voelker'].items():
        volk = Volk.from_dict(volk_data)
        charakter.voelker[volk_key] = volk
        charakter.voelker_selected[volk_key] = False
    
    # Talente mocken (einige)
    charakter.talente = {
        "AH (Magier)": MockTalent("AH (Magier)", aktiv=True),
        "Berserker": MockTalent("Berserker", aktiv=True),
        "Barbar": MockTalent("Barbar", aktiv=True),
    }
    
    return charakter

def test_hat_wahlmoeglichkeit(charakter):
    """Testet hat_volk_wahlmoeglichkeit für Savage Pathfinder Völker."""
    from functions.volk_funktionen import hat_volk_wahlmoeglichkeit
    
    tests = [
        ("Halbork", "freies_attribut", False, "Halbork sollte keine Attribut-Wahl haben"),
        ("Halbork", "freies_talent", False, "Halbork sollte keine Talent-Wahl haben"),
        ("Halbelf", "freies_attribut", True, "Halbelf sollte freies Attribut haben"),
        ("Halbelf", "freies_talent", False, "Halbelf sollte keine freies Talent haben (nur Attribut)"),
        ("Mensch", "freies_attribut", True, "Mensch sollte freies Attribut haben"),
        ("Mensch", "freies_talent", True, "Mensch sollte freies Talent haben"),
    ]
    
    for volk_name, typ, expected, msg in tests:
        result = hat_volk_wahlmoeglichkeit(charakter, volk_name, typ)
        status = "✅" if result == expected else "❌"
        print(f"{status} {msg}: {result} (erwartet {expected})")

def test_get_volk_attribut_optionen(charakter):
    """Testet Attribut-Optionen."""
    from functions.volk_funktionen import get_volk_attribut_optionen, NO_ATTRIBUT_AVAILABLE_TEXT
    
    tests = [
        ("Halbork", [NO_ATTRIBUT_AVAILABLE_TEXT], "Halbork sollte keine Attribut-Optionen haben"),
        ("Halbelf", ["Geschicklichkeit", "Konstitution", "Stärke", "Verstand", "Willenskraft"], "Halbelf sollte alle Attribute haben (freies Attribut)"),
        ("Mensch", ["Geschicklichkeit", "Konstitution", "Stärke", "Verstand", "Willenskraft"], "Mensch sollte alle Attribute haben"),
    ]
    
    for volk_name, expected, msg in tests:
        result = get_volk_attribut_optionen(charakter, volk_name)
        # Sortieren für Vergleich
        result_sorted = sorted(result) if result != [NO_ATTRIBUT_AVAILABLE_TEXT] else result
        expected_sorted = sorted(expected) if expected != [NO_ATTRIBUT_AVAILABLE_TEXT] else expected
        if result_sorted == expected_sorted:
            print(f"✅ {msg}: {result}")
        else:
            print(f"❌ {msg}: {result} (erwartet {expected})")

def test_get_volk_zusatzelemente(charakter):
    """Testet Zusatzelemente."""
    from functions.volk_funktionen import get_volk_zusatzelemente
    
    tests = [
        ("Halbork", {"freie_talente": False, "freie_attribute": False, "halbelf_entweder_oder": False}),
        ("Halbelf", {"freie_talente": False, "freie_attribute": True, "halbelf_entweder_oder": False}),
        ("Mensch", {"freie_talente": True, "freie_attribute": True, "halbelf_entweder_oder": False}),
    ]
    
    for volk_name, expected in tests:
        result = get_volk_zusatzelemente(charakter, volk_name)
        ok = True
        for key, exp_val in expected.items():
            if result.get(key) != exp_val:
                ok = False
                print(f"❌ {volk_name}.{key}: {result.get(key)} (erwartet {exp_val})")
        if ok:
            print(f"✅ {volk_name}: Zusatzelemente korrekt")

if __name__ == "__main__":
    print("=== Test Savage Pathfinder Völker ===")
    charakter = create_mock_charakter()
    print("\n1. hat_volk_wahlmoeglichkeit:")
    test_hat_wahlmoeglichkeit(charakter)
    print("\n2. get_volk_attribut_optionen:")
    test_get_volk_attribut_optionen(charakter)
    print("\n3. get_volk_zusatzelemente:")
    test_get_volk_zusatzelemente(charakter)
    print("\n=== Test abgeschlossen ===")