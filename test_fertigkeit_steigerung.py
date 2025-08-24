#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schnelltest für die Fertigkeitssteigerung um das Problem zu verstehen.
"""

import sys
import os
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from charakter import Charakter
from models.wuerfel import Wuerfel
from functions.setting_funktionen import CustomElementManager

def test_fertigkeit_steigerung():
    """Test für einzelne Fertigkeitssteigerung."""
    print("=== FERTIGKEITSSTEIGERUNG TEST ===")
    
    # Charakter initialisieren
    charakter = Charakter(active_setting_name="SWAE", char_name="TestChar")
    charakter.custom_element_manager = CustomElementManager(charakter, setting_name='SWAE')
    charakter.custom_element_manager.set_active_setting('SWAE')
    charakter.active_setting_name = 'SWAE'
    
    # Startpunkte
    charakter.verbleibende_fertigkeitspunkte = 15
    charakter.verbleibende_fertigkeitssteigerungen = 15
    
    # Test eine Fertigkeit
    fertigkeit_name = "Kämpfen"
    if fertigkeit_name in charakter.fertigkeiten:
        fert = charakter.fertigkeiten[fertigkeit_name]
        print(f"\nVor Steigerung:")
        print(f"  {fertigkeit_name}: {fert.wuerfel} (value={fert.wuerfel.value}, modifier={fert.wuerfel.modifier})")
        print(f"  Verfügbare Punkte: {getattr(charakter, 'verbleibende_fertigkeitspunkte', charakter.verbleibende_fertigkeitssteigerungen)}")
        
        # Mehrere Steigerungen testen
        for i in range(5):
            erfolg = charakter.steigere_fertigkeit(fertigkeit_name, confirm_double_cost=True)
            current_value = fert.wuerfel.value
            current_modifier = fert.wuerfel.modifier
            verfuegbare_punkte = getattr(charakter, 'verbleibende_fertigkeitspunkte', charakter.verbleibende_fertigkeitssteigerungen)
            
            print(f"  Steigerung {i+1}: {erfolg} -> {fert.wuerfel} (value={current_value}, modifier={current_modifier})")
            print(f"    Verfügbare Punkte: {verfuegbare_punkte}")
            
            if not erfolg or erfolg == "needs_confirmation":
                print(f"    Stoppe bei Steigerung {i+1}")
                break
    else:
        print(f"Fertigkeit '{fertigkeit_name}' nicht gefunden")

if __name__ == '__main__':
    test_fertigkeit_steigerung()