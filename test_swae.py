#!/usr/bin/env python3
"""
Test für SWAE Halbelf (freies_talent_oder_attribut).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from models.volk import Volk

def create_mock_charakter_swae():
    class MockAttribut:
        def __init__(self, name, wert=4):
            self.attribut_name = name
            self.wert = wert
    
    class MockCharakter:
        def __init__(self):
            self.voelker = {}
            self.voelker_selected = {}
            self.attribute = {}
            self.talente = {}
            self.selected_talente = []
            self._halbelf_freies_talent = None
            self._halbelf_attribut_gewaehlt = False
        
        def berechne_abgeleitete_werte(self):
            pass
        
        def dispatch(self, event):
            pass
    
    with open('settings/SWAE.json', 'r', encoding='utf-8') as f:
        setting_data = json.load(f)
    
    charakter = MockCharakter()
    
    attribut_names = ["Geschicklichkeit", "Verstand", "Stärke", "Konstitution", "Willenskraft"]
    for name in attribut_names:
        charakter.attribute[name] = MockAttribut(name)
    
    # Nur Halbelf laden
    volk_data = setting_data['voelker']['Halbelf']
    volk = Volk.from_dict(volk_data)
    charakter.voelker['Halbelf'] = volk
    charakter.voelker_selected['Halbelf'] = False
    
    return charakter

def test_swae_halbelf():
    from functions.volk_funktionen import get_volk_zusatzelemente, get_volk_attribut_optionen, hat_volk_wahlmoeglichkeit
    
    charakter = create_mock_charakter_swae()
    
    print("=== SWAE Halbelf Test ===")
    
    # hat_volk_wahlmoeglichkeit
    print("1. hat_volk_wahlmoeglichkeit:")
    print(f"   freies_attribut: {hat_volk_wahlmoeglichkeit(charakter, 'Halbelf', 'freies_attribut')}")
    print(f"   freies_talent: {hat_volk_wahlmoeglichkeit(charakter, 'Halbelf', 'freies_talent')}")
    print(f"   freies_talent_oder_attribut: {hat_volk_wahlmoeglichkeit(charakter, 'Halbelf', 'freies_talent_oder_attribut')}")
    
    # get_volk_zusatzelemente
    print("\n2. get_volk_zusatzelemente:")
    zusatz = get_volk_zusatzelemente(charakter, 'Halbelf')
    for k, v in zusatz.items():
        print(f"   {k}: {v}")
    if zusatz['halbelf_entweder_oder']:
        print("   ✅ ENTWEDER/ODER erkannt")
    else:
        print("   ❌ ENTWEDER/ODER nicht erkannt")
    
    # get_volk_attribut_optionen
    print("\n3. get_volk_attribut_optionen:")
    optionen = get_volk_attribut_optionen(charakter, 'Halbelf')
    print(f"   {optionen}")
    if optionen == ["Geschicklichkeit"]:
        print("   ✅ Korrekte Attribut-Option (Geschicklichkeit)")
    else:
        print("   ❌ Falsche Attribut-Option")
    
    print("\n=== Test abgeschlossen ===")

if __name__ == "__main__":
    test_swae_halbelf()