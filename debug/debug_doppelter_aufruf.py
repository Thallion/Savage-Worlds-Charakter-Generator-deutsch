#!/usr/bin/env python3
"""
Debug-Script um doppelte Aufrufe zu identifizieren
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import traceback
from unittest.mock import Mock, patch
from functions.ausruestung_funktionen import kaufen
from config.ausruestung_config import AusruestungKategorien

# Patch Logger um Stack Traces zu zeigen
original_warning = None
original_debug = None

def debug_warning(message):
    print(f"🔍 WARNING CALLED: {message}")
    print("📍 Stack Trace:")
    traceback.print_stack(limit=10)
    print("-" * 50)
    if original_warning:
        original_warning(message)

def debug_debug(message): 
    print(f"✅ DEBUG (Success): {message}")
    print("📍 Stack Trace:")
    traceback.print_stack(limit=10)
    print("-" * 50)
    if original_debug:
        original_debug(message)

def test_doppelter_aufruf():
    print("🔍 Debug: Doppelter Aufruf bei Käufen")
    print("=" * 70)
    
    # Logger patchen
    from kivy.logger import Logger
    global original_warning, original_debug
    original_warning = Logger.warning
    original_debug = Logger.debug
    
    Logger.warning = debug_warning
    Logger.debug = debug_debug
    
    # Mock-Setup
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
    
    # Minigun mit hohem Original-Preis
    minigun = Mock()
    minigun.name = "Minigun (7.62mm)"
    minigun.kosten = 5000  # Sehr teuer! Mehr als Vermögen (500)
    minigun.menge = 0
    minigun.gewicht = 50.0
    minigun.kategorie = AusruestungKategorien.WAFFE
    minigun.erhoehe_menge = Mock()
    
    print(f"Charakter-Vermögen: {charakter.vermoegen}")
    print(f"Minigun Original-Kosten: {minigun.kosten}")
    print(f"Benutzerdefinierter Preis: 10")
    print()
    
    print("🧪 Test 1: Kauf mit benutzerdefiniertem Preis (niedrig)")
    print("-" * 50)
    
    # Kauf mit benutzerdefiniertem Preis von 10 (viel niedriger als 5000)
    result = kaufen(charakter, minigun, anzahl=1, preis_pro_stueck=10)
    
    print(f"\nErgebnis: {result}")
    print(f"Minigun.erhoehe_menge aufgerufen: {minigun.erhoehe_menge.called}")
    print(f"Charakter-Vermögen nach Kauf: {charakter.vermoegen}")
    
    # Logger zurücksetzen
    Logger.warning = original_warning
    Logger.debug = original_debug

if __name__ == "__main__":
    test_doppelter_aufruf()