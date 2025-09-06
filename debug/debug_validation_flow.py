#!/usr/bin/env python3
"""
Debug-Script um den kompletten Validierungs-Flow zu verfolgen
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import traceback
from unittest.mock import Mock, patch
from functions.ausruestung_funktionen import kaufen
from controllers.charakter_controller import CharakterController
from config.ausruestung_config import AusruestungKategorien

def trace_all_calls():
    print("🔍 Debug: Kompletter Validierungs-Flow")
    print("=" * 70)
    
    # Alle relevanten Funktionen patchen um Aufrufe zu verfolgen
    from kivy.logger import Logger
    from functions import ausruestung_funktionen
    
    original_warning = Logger.warning
    original_debug = Logger.debug
    original_kaufen = ausruestung_funktionen.kaufen
    
    call_count = 0
    
    def trace_warning(message):
        nonlocal call_count
        call_count += 1
        print(f"🚨 WARNING #{call_count}: {message}")
        print("📍 Stack Trace:")
        traceback.print_stack(limit=8)
        print("-" * 50)
        if original_warning:
            original_warning(message)
    
    def trace_debug(message):
        print(f"✅ DEBUG: {message}")
        if original_debug:
            original_debug(message)
    
    def trace_kaufen(charakter, item, anzahl=1, preis_pro_stueck=None):
        print(f"🛒 KAUFEN aufgerufen:")
        print(f"   Item: {item.name}")
        print(f"   Original-Preis: {item.kosten}")
        print(f"   Custom-Preis: {preis_pro_stueck}")
        print(f"   Charakter-Vermögen: {charakter.vermoegen}")
        print(f"   Anzahl: {anzahl}")
        
        result = original_kaufen(charakter, item, anzahl, preis_pro_stueck)
        print(f"   Ergebnis: {result}")
        print(f"   Vermögen danach: {charakter.vermoegen}")
        print("-" * 50)
        return result
    
    # Patches anwenden
    Logger.warning = trace_warning
    Logger.debug = trace_debug
    ausruestung_funktionen.kaufen = trace_kaufen
    
    try:
        # Mock-Setup ähnlich wie in der echten App
        charakter = Mock()
        charakter.vermoegen = 500  # Hat 500 Vermögen
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
        
        charakter.berechne_gesamtgewicht = Mock()
        charakter.berechne_traglast = Mock(return_value=100)
        charakter.berechne_abgeleitete_werte = Mock()
        
        # Minigun Setup
        minigun = Mock()
        minigun.name = "Minigun (7.62mm)"
        minigun.kosten = 5000  # Sehr teuer! Mehr als Vermögen (500)
        minigun.menge = 0
        minigun.gewicht = 50.0
        minigun.kategorie = AusruestungKategorien.WAFFE
        minigun.erhoehe_menge = Mock()
        
        print(f"Setup:")
        print(f"   Charakter-Vermögen: {charakter.vermoegen}")
        print(f"   Minigun Original-Kosten: {minigun.kosten}")
        print(f"   Test-Preis: 10")
        print()
        
        # Test 1: Direkter Aufruf der kaufen Funktion
        print("🧪 Test 1: Direkter kaufen() Aufruf")
        print("-" * 50)
        result1 = kaufen(charakter, minigun, anzahl=1, preis_pro_stueck=10)
        print(f"Direktes Ergebnis: {result1}")
        print()
        
        # Reset für Test 2
        charakter.vermoegen = 500
        minigun.erhoehe_menge.reset_mock()
        
        # Test 2: Über Controller (ähnlich wie in der App)
        print("🧪 Test 2: Über CharakterController")
        print("-" * 50)
        
        # Controller Mock
        controller = Mock()
        controller.charakter = charakter
        controller.charakter.ausruestung = {minigun.name: minigun}
        controller.charakter.kaufen = Mock(side_effect=lambda item, anzahl=1, preis_pro_stueck=None: kaufen(charakter, item, anzahl, preis_pro_stueck))
        
        # Simuliere den Controller-Aufruf
        from controllers.charakter_controller import CharakterController
        real_controller = CharakterController()
        real_controller.charakter = charakter
        real_controller.charakter.ausruestung = {minigun.name: minigun}
        
        result2 = real_controller.kaufen_ausruestung(minigun.name, anzahl=1, preis_pro_stueck=10)
        print(f"Controller Ergebnis: {result2}")
        
        print()
        print(f"Anzahl der Warnungen insgesamt: {call_count}")
        
    finally:
        # Patches zurücksetzen
        Logger.warning = original_warning
        Logger.debug = original_debug
        ausruestung_funktionen.kaufen = original_kaufen

if __name__ == "__main__":
    trace_all_calls()