#!/usr/bin/env python3
"""
Integration Tests für die gesamte App.
Testet die Integration der Manager-Klassen mit der main.py und echten Komponenten.
"""

import sys
import os
import unittest
import tempfile
import json
from pathlib import Path

# Projektwurzel zum Python-Pfad hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestAppIntegration(unittest.TestCase):
    """Integration Tests für die gesamte App"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = None
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_imports_work(self):
        """Test dass alle kritischen Module importiert werden können"""
        try:
            # Test Manager-Imports
            from functions.eigenschaften_funktionen import EigenschaftenManager
            from functions.talent_funktionen import TalentManager
            
            # Test Config-Imports
            from functions.eigenschaften_funktionen import get_eigenschaften_manager
            from functions.talent_funktionen import get_talent_manager, TalentConfig
            
            # Test Hauptkomponenten
            from models.charakter import Charakter
            import main
            
            self.assertTrue(True, "Alle kritischen Imports erfolgreich")
            
        except ImportError as e:
            self.fail(f"Import-Fehler: {e}")
    
    def test_config_files_exist_and_valid(self):
        """Test dass Config-Dateien existieren und valide sind"""
        config_dir = project_root / 'config'
        
        # Test eigenschaften_config.json
        eigenschaften_config = config_dir / 'eigenschaften_config.json'
        self.assertTrue(eigenschaften_config.exists(), "eigenschaften_config.json existiert")
        
        with open(eigenschaften_config, 'r', encoding='utf-8') as f:
            eigenschaften_data = json.load(f)
        
        # Prüfe Struktur
        self.assertIn('grundfertigkeiten', eigenschaften_data)
        self.assertIn('standard_attribute', eigenschaften_data)
        self.assertIn('kosten', eigenschaften_data)
        self.assertIsInstance(eigenschaften_data['grundfertigkeiten'], list)
        
        # Test talent_config.json
        talent_config = config_dir / 'talent_config.json'
        self.assertTrue(talent_config.exists(), "talent_config.json existiert")
        
        with open(talent_config, 'r', encoding='utf-8') as f:
            talent_data = json.load(f)
        
        # Prüfe Struktur
        self.assertIn('kosten', talent_data)
        self.assertIn('nicht_duplizierbare_talente', talent_data)
        self.assertIn('pathfinder_kostenlose_kategorien', talent_data)
        self.assertIsInstance(talent_data['nicht_duplizierbare_talente'], list)
    
    def test_charakter_creation_with_managers(self):
        """Test Charakter-Erstellung mit neuen Manager-Klassen"""
        try:
            from models.charakter import Charakter
            from functions import eigenschaften_funktionen, talent_funktionen
            
            # Erstelle Charakter
            charakter = Charakter()
            self.assertIsNotNone(charakter)
            
            # Test EigenschaftenManager Integration
            eigenschaften_manager = eigenschaften_funktionen.get_eigenschaften_manager()
            self.assertIsNotNone(eigenschaften_manager)
            
            # Test TalentManager Integration  
            talent_manager = talent_funktionen.get_talent_manager(charakter)
            self.assertIsNotNone(talent_manager)
            self.assertEqual(talent_manager.charakter, charakter)
            
            # Test dass Attribute initialisiert sind
            if hasattr(charakter, 'attribute') and charakter.attribute:
                self.assertGreater(len(charakter.attribute), 0)
                
                # Test eine Attribut-Steigerung
                initial_value = charakter.attribute['Stärke'].wuerfel.value
                erfolg = eigenschaften_funktionen.steigere_attribut(charakter, 'Stärke')
                if erfolg:
                    final_value = charakter.attribute['Stärke'].wuerfel.value
                    self.assertGreater(final_value, initial_value)
            
        except Exception as e:
            self.fail(f"Charakter-Erstellung mit Managern fehlgeschlagen: {e}")
    
    def test_legacy_functions_still_work(self):
        """Test dass alle alten Funktionen noch funktionieren"""
        try:
            from models.charakter import Charakter
            from functions import eigenschaften_funktionen, talent_funktionen
            
            charakter = Charakter()
            
            # Test alte Eigenschaften-Funktionen
            if hasattr(charakter, 'attribute') and charakter.attribute:
                # Teste alte steigere_attribut Funktion
                initial_steigerungen = charakter.verbleibende_attributsteigerungen
                erfolg = eigenschaften_funktionen.steigere_attribut(charakter, 'Geschicklichkeit')
                if erfolg:
                    self.assertLess(charakter.verbleibende_attributsteigerungen, initial_steigerungen)
            
            # Test alte Talent-Funktionen (nur wenn Talente vorhanden)
            if hasattr(charakter, 'talente') and charakter.talente:
                talent_namen = list(charakter.talente.keys())
                if talent_namen:
                    erstes_talent = talent_namen[0]
                    # Teste waehle_talent Funktion (erwarten verschiedene Rückgabewerte)
                    result = talent_funktionen.waehle_talent(charakter, erstes_talent)
                    # Result kann True, False oder ein Status-String sein
                    self.assertIsNotNone(result)
            
        except Exception as e:
            self.fail(f"Legacy-Funktionen Test fehlgeschlagen: {e}")
    
    def test_manager_config_loading(self):
        """Test dass Manager ihre Configs korrekt laden"""
        try:
            from functions.eigenschaften_funktionen import EigenschaftenManager
            from functions.talent_funktionen import TalentManager, TalentConfig
            from models.charakter import Charakter
            
            # Test EigenschaftenManager Config
            eigenschaften_manager = EigenschaftenManager()
            self.assertIsNotNone(eigenschaften_manager.config)
            self.assertIsInstance(eigenschaften_manager.grundfertigkeiten, list)
            self.assertIsInstance(eigenschaften_manager.standard_attribute, dict)
            
            # Test TalentManager Config
            charakter = Charakter()
            talent_manager = TalentManager(charakter)
            
            config = TalentConfig.load_config()
            self.assertIsNotNone(config)
            self.assertIn('kosten', config)
            
            # Test Config.get Methode
            handicap_punkte = TalentConfig.get('kosten.handicap_punkte', 0)
            self.assertGreater(handicap_punkte, 0)
            
        except Exception as e:
            self.fail(f"Manager Config Loading Test fehlgeschlagen: {e}")
    
    def test_main_module_imports(self):
        """Test dass main.py importiert werden kann ohne Fehler"""
        try:
            import main
            
            # Prüfe dass wichtige Klassen verfügbar sind
            self.assertTrue(hasattr(main, 'SW_Charakter_GeneratorApp'))
            
            # Test dass die App-Klasse instanziiert werden kann
            # (ohne sie zu starten)
            app_class = getattr(main, 'SW_Charakter_GeneratorApp')
            self.assertIsNotNone(app_class)
            
        except Exception as e:
            self.fail(f"main.py Import Test fehlgeschlagen: {e}")
    
    def test_models_integration(self):
        """Test Integration mit Model-Klassen"""
        try:
            from models.attribut import Attribut
            from models.fertigkeit import Fertigkeit
            from models.talent import Talent
            from models.wuerfel import Wuerfel
            
            # Test Attribut-Erstellung
            attribut = Attribut("Stärke", 4, 0)
            self.assertEqual(attribut.attribut_name, "Stärke")
            self.assertEqual(attribut.wuerfel.value, 4)
            
            # Test Fertigkeit-Erstellung
            fertigkeit = Fertigkeit("Kämpfen", attribut, False)
            self.assertEqual(fertigkeit.fertigkeit_name, "Kämpfen")
            self.assertEqual(fertigkeit.attribut, attribut)
            
            # Test Talent-Erstellung
            talent = Talent("Glück", "Hintergrund", "A", [], "Glücklich sein")
            self.assertEqual(talent.name, "Glück")
            self.assertEqual(talent.kategorie, "Hintergrund")
            
        except Exception as e:
            self.fail(f"Models Integration Test fehlgeschlagen: {e}")
    
    def test_error_handling_robustness(self):
        """Test Robustheit der Fehlerbehandlung"""
        try:
            from functions import eigenschaften_funktionen, talent_funktionen
            from models.charakter import Charakter
            
            charakter = Charakter()
            
            # Test mit ungültigen Eingaben
            if hasattr(charakter, 'attribute'):
                # Teste ungültiges Attribut
                result = eigenschaften_funktionen.steigere_attribut(charakter, 'UnbekanntesAttribut')
                self.assertFalse(result)  # Sollte False zurückgeben, nicht crashen
            
            if hasattr(charakter, 'talente'):
                # Teste ungültiges Talent
                result = talent_funktionen.waehle_talent(charakter, 'UnbekannteTalent')
                self.assertFalse(result)  # Sollte False zurückgeben, nicht crashen
            
        except Exception as e:
            self.fail(f"Error Handling Test fehlgeschlagen: {e}")


def run_integration_tests():
    """Führt alle Integration Tests aus"""
    print("="*60)
    print("APP INTEGRATION TESTS")
    print("="*60)
    
    # Erstelle Test-Suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAppIntegration))
    
    # Führe Tests aus
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Zeige Zusammenfassung
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("🎉 ALLE INTEGRATION TESTS ERFOLGREICH!")
        print(f"✅ {result.testsRun} Tests bestanden")
    else:
        print("❌ EINIGE INTEGRATION TESTS FEHLGESCHLAGEN!")
        print(f"❌ {len(result.failures)} Fehler, {len(result.errors)} Exceptions")
        for test, error in result.failures + result.errors:
            print(f"  - {test}: {error.splitlines()[-1] if error else 'Unbekannter Fehler'}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)