#!/usr/bin/env python3
"""
Debug-Script um nur die Purchase-related Warnings zu verfolgen
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import traceback
from unittest.mock import Mock, patch
from functions.ausruestung_funktionen import kaufen
from config.ausruestung_config import AusruestungKategorien, LogMessages

def test_purchase_warnings():
    print("🔍 Debug: Purchase-Warnings isoliert")
    print("=" * 70)
    
    # Nur Purchase-relevante Warnings abfangen
    from kivy.logger import Logger
    
    original_warning = Logger.warning
    original_debug = Logger.debug
    
    purchase_warning_count = 0
    
    def filter_warning(message):
        nonlocal purchase_warning_count
        
        # Nur Warnings die mit unserem Purchase-Problem zu tun haben
        if any(keyword in str(message).lower() for keyword in [
            'nicht genügend', 'vermögen', 'geld', 'kauf', 'purchase', 
            'insufficient', 'money', 'wealth'
        ]):
            purchase_warning_count += 1
            print(f"🚨 PURCHASE WARNING #{purchase_warning_count}: {message}")
            print("📍 Stack Trace:")
            traceback.print_stack(limit=6)
            print("-" * 50)
            
        # Original-Warning nur für Purchase-relevante Meldungen aufrufen
        if original_warning and any(keyword in str(message).lower() for keyword in [
            'nicht genügend', 'vermögen', 'geld', 'kauf'
        ]):
            original_warning(message)
    
    def filter_debug(message):
        # Nur Debug-Messages die uns interessieren
        if any(keyword in str(message).lower() for keyword in [
            'gekauft', 'kauf', 'vermögen', 'purchase'
        ]):
            print(f"✅ PURCHASE DEBUG: {message}")
        if original_debug:
            original_debug(message)
    
    # Patches anwenden
    Logger.warning = filter_warning
    Logger.debug = filter_debug
    
    try:
        # Mock-Setup
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
        
        charakter.berechne_gesamtgewicht = Mock()
        charakter.berechne_traglast = Mock(return_value=100)
        charakter.berechne_abgeleitete_werte = Mock()
        
        # Minigun Setup
        minigun = Mock()
        minigun.name = "Minigun (7.62mm)"
        minigun.kosten = 5000
        minigun.menge = 0
        minigun.gewicht = 50.0
        minigun.kategorie = AusruestungKategorien.WAFFE
        minigun.erhoehe_menge = Mock()
        
        print(f"Setup - Vermögen: {charakter.vermoegen}, Item-Kosten: {minigun.kosten}, Custom-Preis: 10")
        print()
        
        # Test 1: Mit unzureichendem Vermögen (Original-Preis)
        print("🧪 Test 1: Kauf mit Original-Preis (sollte Warning geben)")
        print("-" * 50)
        charakter.vermoegen = 500  # Reset
        result1 = kaufen(charakter, minigun, anzahl=1, preis_pro_stueck=None)  # Benutzt Original-Preis 5000
        print(f"Ergebnis: {result1}")
        print()
        
        # Test 2: Mit Custom-Preis (niedrig)
        print("🧪 Test 2: Kauf mit Custom-Preis (sollte erfolgreich sein)")
        print("-" * 50)
        charakter.vermoegen = 500  # Reset
        result2 = kaufen(charakter, minigun, anzahl=1, preis_pro_stueck=10)  # Custom-Preis 10
        print(f"Ergebnis: {result2}")
        print()
        
        # Test 3: Double-Call Test - Simuliert das was im Log passiert
        print("🧪 Test 3: Double-Call Test")
        print("-" * 50)
        charakter.vermoegen = 500  # Reset
        # Erst der Check mit Original-Preis (simuliert possible pre-validation)
        temp_result = charakter.vermoegen < minigun.kosten
        if temp_result:
            print(f"Pre-Validation: Nicht genügend Vermögen (Original-Preis Check)")
            Logger.warning(LogMessages.NICHT_GENUEGEND_VERMOEGEN.format(
                anzahl=1, name=minigun.name
            ))
        
        # Dann der echte Kauf mit Custom-Preis
        result3 = kaufen(charakter, minigun, anzahl=1, preis_pro_stueck=10)
        print(f"Echter Kauf Ergebnis: {result3}")
        print()
        
        print(f"Anzahl Purchase-Warnings insgesamt: {purchase_warning_count}")
        
    finally:
        # Patches zurücksetzen
        Logger.warning = original_warning
        Logger.debug = original_debug

if __name__ == "__main__":
    test_purchase_warnings()