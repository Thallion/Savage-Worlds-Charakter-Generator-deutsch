#!/usr/bin/env python3
"""
Debug-Script für das Vermögensproblem beim Kauf
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from unittest.mock import Mock
from functions.ausruestung_funktionen import kaufen
from models.ausruestung import Ausruestung
from config.ausruestung_config import AusruestungKategorien

def debug_vermoegen_problem():
    print("🔍 Debug: Vermögensproblem beim Kauf")
    print("=" * 50)
    
    # Mock-Charakter erstellen
    charakter = Mock()
    charakter.vermoegen = 500
    charakter.startkapital = 500
    charakter.erschoepfung = 0
    charakter.gesamtgewicht = 10
    charakter.ausruestung = {}
    charakter.selected_allgemeine_ausruestung = []
    charakter.selected_waffen = []
    charakter.selected_ruestungen = []
    charakter.selected_schilde = []
    charakter.selected_talente = set()
    charakter.selected_handicaps = set()
    
    # Mock-Funktionen
    charakter.berechne_gesamtgewicht = Mock()
    charakter.berechne_traglast = Mock(return_value=100)
    charakter.berechne_abgeleitete_werte = Mock()
    
    # Test-Item erstellen
    test_item = Mock()
    test_item.name = "Test Schwert"
    test_item.kosten = 100
    test_item.menge = 1
    test_item.gewicht = 2.0
    test_item.kategorie = AusruestungKategorien.WAFFE
    test_item.erhoehe_menge = Mock()
    
    print(f"Vor dem Kauf:")
    print(f"  Charakter.vermögen: {charakter.vermoegen}")
    print(f"  Item.kosten: {test_item.kosten}")
    print(f"  Kaufmenge: 1")
    print(f"  Gesamtpreis: {test_item.kosten * 1}")
    print(f"  Vermögen ausreichend? {charakter.vermoegen >= (test_item.kosten * 1)}")
    print()
    
    # Kauf durchführen
    result = kaufen(charakter, test_item, 1)
    
    print(f"Nach dem Kauf:")
    print(f"  Kauf erfolgreich: {result}")
    print(f"  Charakter.vermögen: {charakter.vermoegen}")
    print(f"  test_item.erhoehe_menge aufgerufen: {test_item.erhoehe_menge.called}")
    
    print()
    print("🧪 Test mit unzureichendem Vermögen:")
    print("-" * 30)
    
    # Test mit unzureichendem Vermögen
    charakter.vermoegen = 50  # Weniger als Kosten (100)
    test_item2 = Mock()
    test_item2.name = "Teures Item"
    test_item2.kosten = 200
    test_item2.menge = 1
    test_item2.gewicht = 1.0
    test_item2.kategorie = AusruestungKategorien.ALLGEMEIN
    test_item2.erhoehe_menge = Mock()
    
    print(f"Vor dem Kauf:")
    print(f"  Charakter.vermögen: {charakter.vermoegen}")
    print(f"  Item.kosten: {test_item2.kosten}")
    print(f"  Vermögen ausreichend? {charakter.vermoegen >= test_item2.kosten}")
    
    result2 = kaufen(charakter, test_item2, 1)
    
    print(f"Nach dem Kauf:")
    print(f"  Kauf erfolgreich: {result2}")
    print(f"  Charakter.vermögen: {charakter.vermoegen}")
    print(f"  test_item2.erhoehe_menge aufgerufen: {test_item2.erhoehe_menge.called}")
    
    print()
    print("🎯 Analyse:")
    if result2:
        print("❌ BUG: Kauf war erfolgreich obwohl Vermögen unzureichend!")
    else:
        print("✅ KORREKT: Kauf wurde bei unzureichendem Vermögen abgelehnt")


if __name__ == "__main__":
    debug_vermoegen_problem()