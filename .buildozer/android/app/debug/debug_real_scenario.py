#!/usr/bin/env python3
"""
Debug-Script um das echte Szenario zu testen
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_exact_user_scenario():
    print("🔍 Debug: Exaktes User-Szenario")
    print("=" * 70)
    
    # Track warnings
    from kivy.logger import Logger
    original_warning = Logger.warning
    warning_count = 0
    
    def count_warnings(msg):
        nonlocal warning_count
        if 'vermögen' in str(msg).lower() or 'geld' in str(msg).lower():
            warning_count += 1
            print(f"🚨 Purchase Warning #{warning_count}: {msg}")
        return original_warning(msg)
    
    Logger.warning = count_warnings
    
    try:
        from controllers.charakter_controller import CharakterController
        from config.ausruestung_config import AusruestungKategorien
        
        # Setup wie in der echten App
        print("Setting up real scenario...")
        controller = CharakterController()
        
        # Lade eine echte Ausrüstung aus dem System
        controller.charakter.vermoegen = 100  # Sehr wenig Geld
        
        # Prüfe welche Ausrüstung verfügbar ist
        print(f"Verfügbare Ausrüstung: {len(controller.charakter.ausruestung)} Items")
        
        if controller.charakter.ausruestung:
            # Nimm das erste teure Item
            expensive_items = []
            for name, item in controller.charakter.ausruestung.items():
                if hasattr(item, 'kosten') and item.kosten > 100:
                    expensive_items.append((name, item, item.kosten))
            
            if expensive_items:
                # Sortiere nach Kosten
                expensive_items.sort(key=lambda x: x[2], reverse=True)
                item_name, item, kosten = expensive_items[0]
                
                print(f"Testing mit: {item_name}")
                print(f"  Item Kosten: {kosten}")
                print(f"  Charakter Vermögen: {controller.charakter.vermoegen}")
                print(f"  Custom Preis: 10")
                print()
                
                # Test 1: Original Preis (sollte Warning geben)
                print("Test 1: Mit Original-Preis (erwartet: Warning + Failure)")
                result1 = controller.kaufen_ausruestung(item_name, anzahl=1, preis_pro_stueck=None)
                print(f"  Ergebnis: {result1}")
                
                # Reset
                controller.charakter.vermoegen = 100
                warning_count = 0
                
                print("\nTest 2: Mit Custom-Preis (erwartet: Success, keine Warning)")
                result2 = controller.kaufen_ausruestung(item_name, anzahl=1, preis_pro_stueck=10)
                print(f"  Ergebnis: {result2}")
                print(f"  Vermögen danach: {controller.charakter.vermoegen}")
                print(f"  Warnings während Test 2: {warning_count}")
                
                if result2 and warning_count > 0:
                    print("\n🎯 PROBLEM REPLIZIERT!")
                    print("Purchase successful but warning shown - this matches user's experience")
                elif result2 and warning_count == 0:
                    print("\n✅ Alles OK!")
                    print("Purchase successful and no warnings - user should not see error")
                else:
                    print(f"\n❓ Purchase failed (result={result2}) - need to investigate further")
                    
            else:
                print("Keine teuren Items gefunden für Test")
        else:
            print("Keine Ausrüstung verfügbar für Test")
            
    finally:
        Logger.warning = original_warning

if __name__ == "__main__":
    test_exact_user_scenario()