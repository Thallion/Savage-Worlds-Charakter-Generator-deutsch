#!/usr/bin/env python3
# test units/run_all_tests.py
"""
Test Runner für alle Savage Worlds Charakter-Generator Tests
"""

import sys
import os
import unittest
from io import StringIO

# Pfade einrichten
PROJEKT_VERZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_VERZ = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, PROJEKT_VERZ)
sys.path.insert(0, TEST_VERZ)

# Vollständige Liste aller Test-Module
TEST_MODULE = [
    'test_theme_handler',
    'test_character_handler',
    'test_template_handler',
    'test_game_elements_handler',
    'test_einstellungen_widget',
    'test_ausruestung_config',
    'test_ausruestung_funktionen',
    'test_ausruestung_settings',
    'test_auto_generator',
    'test_app_integration',
    'test_charakter_verwaltung',
    'test_cyberware',
    'test_eigenschaften_manager',
    'test_fertigkeit_steigerung',
    'test_hesindian_magier',
    'test_kompendium_barbarian',
    'test_kompendium_bard',
    'test_kompendium_cleric',
    'test_kompendium_druid',
    'test_kompendium_mage',
    'test_korrekte_reihenfolge',
    'test_kraefte_widget',
    'test_leomara_charakter',
    'test_leomara_final',
    'test_leomara_korrekte_reihenfolge',
    'test_leomara_korrekt',
    'test_setting_funktionen',
    'test_superkraft_integration',
    'test_superkraft_model',
    'test_superkraft_popup',
    'test_talent_manager',
    'test_template_handler',
    'test_wizard_service',
    'test_tutorial_service',
    'test_setting_draft',
    'test_setting_merge',
    'test_lazy_screens',
    'test_lazy_services',
]

# Doppelte entfernen
TEST_MODULE = list(dict.fromkeys(TEST_MODULE))


def run_all_tests():
    """Führt alle Tests aus und gibt Ergebnisse aus"""

    print("=" * 70)
    print("🧪 SAVAGE WORLDS CHARAKTER-GENERATOR - ALLE TESTS")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    total_tests = 0
    failed_modules = []

    for module_name in TEST_MODULE:
        try:
            module = __import__(module_name)
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

    print(f"\n📊 Gesamt: {total_tests} Tests in {len(TEST_MODULE) - len(failed_modules)} Modulen")

    if failed_modules:
        print(f"⚠️  Nicht ladbare Module: {', '.join(failed_modules)}")

    print("\n" + "=" * 70)
    print("🚀 STARTE TESTS")
    print("=" * 70)

    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        buffer=True,
        failfast=False
    )

    result = runner.run(suite)

    output = stream.getvalue()
    print(output)

    print("\n" + "=" * 70)
    print("📋 ZUSAMMENFASSUNG")
    print("=" * 70)

    erfolgreich = result.testsRun - len(result.failures) - len(result.errors)
    print(f"🎯 Tests ausgeführt: {result.testsRun}")
    print(f"✅ Erfolgreich: {erfolgreich}")
    print(f"❌ Fehlgeschlagen: {len(result.failures)}")
    print(f"💥 Fehler: {len(result.errors)}")
    print(f"⏭️  Übersprungen: {len(getattr(result, 'skipped', []))}")

    if result.testsRun > 0:
        success_rate = (erfolgreich / result.testsRun) * 100
        print(f"📈 Erfolgsrate: {success_rate:.1f}%")

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
    print("🧪 Savage Worlds Charakter-Generator Test Runner")
    print("=" * 50)
    print("Verwendung:")
    print("  python run_all_tests.py              - Alle Tests ausführen")
    print("  python run_all_tests.py <test_name>  - Einzelnen Test ausführen")
    print("  python run_all_tests.py --help       - Diese Hilfe anzeigen")
    print()
    print("Verfügbare Test-Module:")
    for m in TEST_MODULE:
        print(f"  - {m}")
    print()
    print("Beispiele:")
    print("  python run_all_tests.py test_theme_handler.TestThemeManager.test_init")
    print("  python run_all_tests.py test_cyberware")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in ['--help', '-h', 'help']:
            show_help()
            sys.exit(0)
        else:
            exit_code = run_single_test(arg)
            sys.exit(exit_code)
    else:
        print("❌ Ungültige Argumente. Verwende --help für Hilfe.")
        sys.exit(1)
