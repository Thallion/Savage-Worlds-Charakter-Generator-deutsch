#!/usr/bin/env python3
"""
Debug-Script um den UI-Flow zu testen und zu sehen wo die Warning herkommt
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import traceback
from unittest.mock import Mock, patch
from kivy.logger import Logger

# Mock the entire UI flow
def test_ui_purchase_flow():
    print("🔍 Debug: UI Purchase Flow Test")
    print("=" * 70)
    
    # Track all Logger calls
    original_warning = Logger.warning
    original_debug = Logger.debug
    
    warning_calls = []
    
    def track_warning(message):
        warning_calls.append(str(message))
        print(f"🚨 Logger.warning: {message}")
        if 'vermögen' in str(message).lower() or 'geld' in str(message).lower():
            print("📍 Purchase-related warning detected!")
            traceback.print_stack(limit=5)
        original_warning(message)
    
    def track_debug(message):
        if 'gekauft' in str(message).lower():
            print(f"✅ Logger.debug (Purchase): {message}")
        original_debug(message)
    
    Logger.warning = track_warning
    Logger.debug = track_debug
    
    try:
        # Simulate the complete UI flow
        from config.ausruestung_config import AusruestungKategorien
        from controllers.charakter_controller import CharakterController
        
        print("1. Erstelle CharakterController...")
        controller = CharakterController()
        
        print("2. Setup Charakter mit wenig Vermögen...")
        controller.charakter.vermoegen = 500  # Wenig Geld
        
        print("3. Füge teure Ausrüstung zur Ausrüstung hinzu...")
        # Mock eine teure Minigun
        expensive_minigun = Mock()
        expensive_minigun.name = "Minigun (7.62mm)"
        expensive_minigun.kosten = 5000  # Sehr teuer!
        expensive_minigun.menge = 0
        expensive_minigun.gewicht = 50.0
        expensive_minigun.kategorie = AusruestungKategorien.WAFFE
        expensive_minigun.erhoehe_menge = Mock()
        
        # Zur Ausrüstung hinzufügen
        controller.charakter.ausruestung["Minigun (7.62mm)"] = expensive_minigun
        
        print(f"   Charakter Vermögen: {controller.charakter.vermoegen}")
        print(f"   Minigun Kosten: {expensive_minigun.kosten}")
        print(f"   Custom Preis: 10")
        print()
        
        print("4. Simuliere UI-Kaufdialog Flow...")
        
        # Step 4a: Dialog Content Validation (wie in _handle_kauf_dialog)
        print("   4a. Dialog Content Validation...")
        from views.ausruestung_view import KaufDialogContent
        
        # Simuliere Dialog Content 
        dialog_content = Mock()
        dialog_content.validate = Mock(return_value=(True, None))
        dialog_content.get_values = Mock(return_value=(1, 10.0))  # anzahl=1, preis=10
        
        is_valid, error_message = dialog_content.validate()
        print(f"      Dialog validation: {is_valid}")
        
        if is_valid:
            anzahl, preis = dialog_content.get_values()
            print(f"      Dialog values: anzahl={anzahl}, preis={preis}")
            
            # Step 4b: Controller Call (wie in _handle_kauf_dialog)
            print("   4b. Controller kaufen_ausruestung call...")
            success = controller.kaufen_ausruestung(
                "Minigun (7.62mm)",
                anzahl=anzahl,
                preis_pro_stueck=preis
            )
            
            print(f"      Controller result: {success}")
            print(f"      Charakter Vermögen nach Kauf: {controller.charakter.vermoegen}")
        
        print()
        print(f"Anzahl Warning-Aufrufe: {len(warning_calls)}")
        for i, warning in enumerate(warning_calls, 1):
            if 'vermögen' in warning.lower() or 'geld' in warning.lower():
                print(f"  {i}. Purchase Warning: {warning}")
        
    finally:
        Logger.warning = original_warning  
        Logger.debug = original_debug

if __name__ == "__main__":
    test_ui_purchase_flow()