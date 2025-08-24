#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für die korrekte Reihenfolge: Erst Attribute, dann Fertigkeiten steigern
"""

import sys
import os
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from charakter import Charakter
from functions.setting_funktionen import CustomElementManager

def test_korrekte_reihenfolge():
    """Test für korrekte Reihenfolge der Steigerungen."""
    print("=== TEST KORREKTE REIHENFOLGE ===")
    
    # Charakter initialisieren
    charakter = Charakter(active_setting_name="SWAE", char_name="TestChar")
    charakter.custom_element_manager = CustomElementManager(charakter, setting_name='SWAE')
    charakter.custom_element_manager.set_active_setting('SWAE')
    charakter.active_setting_name = 'SWAE'
    
    # Startpunkte setzen
    charakter.verbleibende_attributsteigerungen = 5
    charakter.verbleibende_fertigkeitssteigerungen = 12
    
    print(f"Startpunkte - Attribute: 5, Fertigkeiten: 12")
    
    # SCHRITT 1: ATTRIBUTE STEIGERN
    print("\n--- SCHRITT 1: ATTRIBUTE STEIGERN ---")
    
    # Geschicklichkeit W4 -> W6 (für Kämpfen)
    print(f"Geschicklichkeit vor Steigerung: {charakter.attribute['Geschicklichkeit'].wuerfel}")
    erfolg = charakter.steigere_attribut('Geschicklichkeit')
    print(f"Geschicklichkeit nach Steigerung: {charakter.attribute['Geschicklichkeit'].wuerfel}, Erfolg: {erfolg}")
    print(f"Verbleibende Attributpunkte: {charakter.verbleibende_attributsteigerungen}")
    
    # SCHRITT 2: FERTIGKEITEN STEIGERN (nach Attributsteigerung)
    print("\n--- SCHRITT 2: FERTIGKEITEN STEIGERN ---")
    
    # Kämpfen steigern (ist an Geschicklichkeit W6 gekoppelt)
    kaempfen = charakter.fertigkeiten['Kämpfen']
    print(f"Kämpfen vor Steigerung: {kaempfen.wuerfel} (Attribut: {kaempfen.attribut.wuerfel})")
    print(f"Verbleibende Fertigkeitspunkte: {charakter.verbleibende_fertigkeitssteigerungen}")
    
    # Erste Steigerung: W4-2 -> W4
    erfolg1 = charakter.steigere_fertigkeit('Kämpfen', confirm_double_cost=True)
    print(f"Steigerung 1: {erfolg1} -> {kaempfen.wuerfel}")
    print(f"Verbleibende Fertigkeitspunkte: {charakter.verbleibende_fertigkeitssteigerungen}")
    
    # Zweite Steigerung: W4 -> W6 (sollte normale Kosten haben, da = Geschicklichkeit)
    erfolg2 = charakter.steigere_fertigkeit('Kämpfen', confirm_double_cost=True)
    print(f"Steigerung 2: {erfolg2} -> {kaempfen.wuerfel}")
    print(f"Verbleibende Fertigkeitspunkte: {charakter.verbleibende_fertigkeitssteigerungen}")
    
    # Dritte Steigerung: W6 -> W8 (sollte doppelte Kosten haben, da > Geschicklichkeit W6)
    print(f"\nVersuche W6 -> W8 (über Attribut hinaus, sollte Bestätigung brauchen):")
    erfolg3 = charakter.steigere_fertigkeit('Kämpfen', confirm_double_cost=False)
    print(f"Ohne Bestätigung: {erfolg3}")
    
    if erfolg3 == "needs_confirmation":
        erfolg3 = charakter.steigere_fertigkeit('Kämpfen', confirm_double_cost=True)
        print(f"Mit Bestätigung: {erfolg3} -> {kaempfen.wuerfel}")
        print(f"Verbleibende Fertigkeitspunkte: {charakter.verbleibende_fertigkeitssteigerungen}")
    
    print("\n=== ZUSAMMENFASSUNG ===")
    print(f"Geschicklichkeit: {charakter.attribute['Geschicklichkeit'].wuerfel}")
    print(f"Kämpfen: {kaempfen.wuerfel}")
    print(f"Verbleibende Attributpunkte: {charakter.verbleibende_attributsteigerungen}")
    print(f"Verbleibende Fertigkeitspunkte: {charakter.verbleibende_fertigkeitssteigerungen}")

if __name__ == '__main__':
    test_korrekte_reihenfolge()