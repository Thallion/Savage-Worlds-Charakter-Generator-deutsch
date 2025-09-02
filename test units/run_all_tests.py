#!/usr/bin/env python3
# tests/run_all_tests.py
"""
Test Runner für alle Einstellungen Widget Handler Tests
"""

import sys
import os
import unittest
from io import StringIO

# Pfad zum Projektverzeichnis hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """Führt alle Tests aus und gibt Ergebnisse aus"""
    
    print("=" * 70)
    print("🧪 EINSTELLUNGEN WIDGET HANDLER TESTS")
    print("=" * 70)
    
    # Test Module definieren
    test_modules = [
        'test_theme_handler',
        'test_character_handler', 
        'test_template_handler',
        'test_game_elements_handler',
        'test_einstellungen_widget'
    ]
    
    # Test Suite erstellen
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    total_tests = 0
    failed_modules = []
    
    # Alle Test Module laden
    for module_name in test_modules:
        try:
            # Dynamisches Import
            module = __import__(f'tests.{module_name}', fromlist=[module_name])
            
            # Tests aus Modul laden
            module_suite = loader.loadTestsFromModule(module)
            test_count = module_suite.countTestCases()
            
            if test_count > 0:
                suite.addTest(module_suite)
                total_tests += test_count
                print(f"✅ Geladen: {module_name} ({test_count} Tests)")
            else:
                print(f"⚠️  Keine Tests gefunden in: {module_name}")
                
        except ImportError as e:
            print(f"❌ Fehler beim Laden von {module_name}: {e}")
            failed_modules.append(module_name)
        except Exception as e:
            print(f"❌ Unerwarteter Fehler bei {module_name}: {e}")
            failed_modules.append(module_name)
    
    print(f"\n📊 Gesamt: {total_tests} Tests in {len(test_modules) - len(failed_modules)} Modulen")
    
    if failed_modules:
        print(f"⚠️  Fehlgeschlagene Module: {', '.join(failed_modules)}")
    
    print("\n" + "=" * 70)
    print("🚀 STARTE TESTS")
    print("=" * 70)
    
    # Test Runner konfigurieren
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        buffer=True,
        failfast=False
    )
    
    # Tests ausführen
    result = runner.run(suite)
    
    # Ergebnisse ausgeben
    output = stream.getvalue()
    print(output)
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("📋 ZUSAMMENFASSUNG")
    print("=" * 70)
    
    print(f"🎯 Tests ausgeführt: {result.testsRun}")
    print(f"✅ Erfolgreich: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Fehlgeschlagen: {len(result.failures)}")
    print(f"💥 Fehler: {len(result.errors)}")
    print(f"⏭️  Übersprungen: {len(getattr(result, 'skipped', []))}")
    
    # Erfolgsrate berechnen
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        print(f"📈 Erfolgsrate: {success_rate:.1f}%")
    
    # Detaillierte Fehler ausgeben
    if result.failures:
        print(f"\n❌ FEHLGESCHLAGENE TESTS ({len(result.failures)}):")
        print("-" * 50)
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.splitlines()[-1] if traceback.splitlines() else 'Kein Traceback verfügbar'}")
    
    if result.errors:
        print(f"\n💥 FEHLER ({len(result.errors)}):")
        print("-" * 50)
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.splitlines()[-1] if traceback.splitlines() else 'Kein Traceback verfügbar'}")
    
    print("\n" + "=" * 70)
    
    # Exit Code setzen
    if result.failures or result.errors:
        print("❌ TESTS FEHLGESCHLAGEN")
        return 1
    else:
        print("✅ ALLE TESTS ERFOLGREICH")
        return 0

def run_single_test(test_name):
    """Führt einen einzelnen Test aus"""
    print(f"🧪 Führe einzelnen Test aus: {test_name}")
    print("=" * 50)
    
    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_name)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
        
    except Exception as e:
        print(f"❌ Fehler beim Ausführen des Tests: {e}")
        return 1

def show_help():
    """Zeigt Hilfe-Informationen"""
    print("🧪 Einstellungen Widget Handler Test Runner")
    print("=" * 50)
    print("Verwendung:")
    print("  python run_all_tests.py              - Alle Tests ausführen")
    print("  python run_all_tests.py <test_name>  - Einzelnen Test ausführen")
    print("  python run_all_tests.py --help       - Diese Hilfe anzeigen")
    print()
    print("Verfügbare Test-Module:")
    print("  - test_theme_handler")
    print("  - test_character_handler")
    print("  - test_template_handler")
    print("  - test_game_elements_handler")
    print("  - test_einstellungen_widget")
    print()
    print("Beispiele:")
    print("  python run_all_tests.py test_theme_handler.TestThemeHandler.test_init")
    print("  python run_all_tests.py test_character_handler.TestCharacterHandler")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Alle Tests ausführen
        exit_code = run_all_tests()
        sys.exit(exit_code)
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in ['--help', '-h', 'help']:
            show_help()
            sys.exit(0)
        else:
            # Einzelnen Test ausführen
            exit_code = run_single_test(arg)
            sys.exit(exit_code)
    else:
        print("❌ Ungültige Argumente. Verwende --help für Hilfe.")
        sys.exit(1)