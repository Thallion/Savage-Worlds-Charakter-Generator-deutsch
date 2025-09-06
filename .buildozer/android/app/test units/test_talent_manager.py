#!/usr/bin/env python3
"""
Unit Tests für den TalentManager.
Testet sowohl die neue TalentManager-Klasse als auch die Rückwärtskompatibilität.
"""

import sys
import os
import unittest
from pathlib import Path

# Projektwurzel zum Python-Pfad hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions import talent_funktionen
from functions.talent_funktionen import TalentManager, get_talent_manager, TalentConfig
from models.talent import Talent
from models.attribut import Attribut
from models.fertigkeit import Fertigkeit
from models.wuerfel import Wuerfel


class MockCharakter:
    """Mock-Charakter für Tests"""
    
    def __init__(self):
        self.talente = {}
        self.attribute = {
            "Stärke": Attribut("Stärke", 4, 0),
            "Geschicklichkeit": Attribut("Geschicklichkeit", 6, 0),
            "Konstitution": Attribut("Konstitution", 4, 0),
            "Verstand": Attribut("Verstand", 8, 0),
            "Willenskraft": Attribut("Willenskraft", 4, 0)
        }
        self.fertigkeiten = {
            "Kämpfen": Fertigkeit("Kämpfen", self.attribute["Geschicklichkeit"], False),
            "Schiessen": Fertigkeit("Schiessen", self.attribute["Geschicklichkeit"], False),
            "Wahrnehmung": Fertigkeit("Wahrnehmung", self.attribute["Verstand"], True)
        }
        self.selected_talente = []
        self.verbleibende_handicap_punkte = 4.0
        self.verbleibende_aufstiege = 2
        self.char_gen_completed = False
        self.verfuegbare_maechte = 0
        self.anzahl_maechte = 0
        self.machtpunkte = 0
        self.rang = "Anfänger"
        self.active_setting_name = "SWAE"
        self.aufstiege_gesamt = 0
        self.pathfinder_kostenlose_talente_gewaehlt = 0
        self.startkapital = 500  # Für Reich-Talent-Tests
        self.selected_handicaps = []  # Für ausruestung_funktionen.py
        
        # Erstelle Test-Talente
        self._create_test_talents()
    
    def _create_test_talents(self):
        """Erstellt Test-Talente für verschiedene Szenarien"""
        # Normales Talent ohne Voraussetzungen
        self.talente["Glück"] = Talent(
            name="Glück",
            kategorie="Hintergrund",
            rang="A",
            voraussetzungen=[],
            beschreibung="Glück haben",
            neue_maechte=0,
            machtpunkte=0
        )
        
        # Talent mit Attribut-Voraussetzung
        self.talente["Kämpfer"] = Talent(
            name="Kämpfer",
            kategorie="Kampf",
            rang="A",
            voraussetzungen=["GES W8"],
            beschreibung="Besserer Kämpfer",
            neue_maechte=0,
            machtpunkte=0
        )
        
        # Talent mit Fertigkeit-Voraussetzung
        self.talente["Meisterschütze"] = Talent(
            name="Meisterschütze",
            kategorie="Kampf",
            rang="F",
            voraussetzungen=["Schiessen W8"],
            beschreibung="Besserer Schütze",
            neue_maechte=0,
            machtpunkte=0
        )
        
        # Talent mit Talent-Voraussetzung
        self.talente["Großes Glück"] = Talent(
            name="Großes Glück",
            kategorie="Hintergrund",
            rang="A",
            voraussetzungen=["Glück"],
            beschreibung="Noch mehr Glück",
            neue_maechte=0,
            machtpunkte=0
        )
        
        # Arkaner Hintergrund
        self.talente["Arkaner Hintergrund: Magie"] = Talent(
            name="Arkaner Hintergrund: Magie",
            kategorie="Macht",
            rang="A",
            voraussetzungen=[],
            beschreibung="Magische Kräfte",
            neue_maechte=3,
            machtpunkte=10
        )
        
        # Pathfinder-Talent
        self.talente["Klassen-Talent"] = Talent(
            name="Klassen-Talent",
            kategorie="Klasse",
            rang="A",
            voraussetzungen=[],
            beschreibung="Pathfinder Klassen-Talent",
            neue_maechte=0,
            machtpunkte=0
        )
        
        # Nicht duplizierbares Talent
        self.talente["Reich"] = Talent(
            name="Reich",
            kategorie="Hintergrund",
            rang="A",
            voraussetzungen=[],
            beschreibung="Reicher Charakter",
            neue_maechte=0,
            machtpunkte=0
        )
    
    def berechne_abgeleitete_werte(self):
        """Mock für berechne_abgeleitete_werte"""
        pass
    
    def erhoehe_machtpunkte(self, punkte):
        """Mock für erhoehe_machtpunkte"""
        self.machtpunkte += punkte
    
    def senke_machtpunkte(self, punkte):
        """Mock für senke_machtpunkte"""
        self.machtpunkte = max(0, self.machtpunkte - punkte)
    
    def update_char_gen_status(self):
        """Mock für update_char_gen_status"""
        pass
    
    def get_rang(self, aufstiege):
        """Mock für get_rang"""
        return "Anfänger"


class TestTalentManager(unittest.TestCase):
    """Unit Tests für TalentManager"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.charakter = MockCharakter()
        self.manager = TalentManager(self.charakter)
    
    def test_manager_initialization(self):
        """Test der Manager-Initialisierung"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.charakter, self.charakter)
    
    def test_config_loading(self):
        """Test des Config-Ladens"""
        config = TalentConfig.load_config()
        self.assertIsInstance(config, dict)
        self.assertIn('kosten', config)
        self.assertIn('nicht_duplizierbare_talente', config)
    
    def test_waehle_talent_success(self):
        """Test erfolgreiche Talent-Auswahl"""
        # Talent ohne Voraussetzungen auswählen
        result = self.manager.waehle_talent("Glück")
        self.assertTrue(result)
        self.assertTrue(self.charakter.talente["Glück"].ausgewaehlt)
        self.assertIn("Glück", self.charakter.selected_talente)
        self.assertEqual(self.charakter.verbleibende_handicap_punkte, 2.0)
    
    def test_waehle_talent_rang_zu_hoch(self):
        """Test Talent-Auswahl mit zu hohem Rang"""
        # Setze niedrigen Charakter-Rang
        self.charakter.rang = "A"
        
        # Versuche Fortgeschrittenen-Talent zu wählen
        result = self.manager.waehle_talent("Meisterschütze")
        self.assertEqual(result, "needs_rang_confirmation")
    
    def test_waehle_talent_voraussetzungen_nicht_erfuellt(self):
        """Test Talent-Auswahl mit unerfüllten Voraussetzungen"""
        # Versuche Talent mit Fertigkeit-Voraussetzung zu wählen (Schiessen W8, aber haben nur W4)
        result = self.manager.waehle_talent("Meisterschütze", ignore_rang_check=True)
        self.assertEqual(result, "needs_voraussetzungen_confirmation")
    
    def test_waehle_talent_mit_voraussetzungen_erfuellt(self):
        """Test erfolgreiche Talent-Auswahl mit erfüllten Voraussetzungen"""
        # Setze Geschicklichkeit auf W8 für Kämpfer-Talent
        self.charakter.attribute["Geschicklichkeit"].wuerfel.value = 8
        
        result = self.manager.waehle_talent("Kämpfer")
        self.assertTrue(result)
        self.assertTrue(self.charakter.talente["Kämpfer"].ausgewaehlt)
    
    def test_waehle_talent_not_duplicatable(self):
        """Test Mehrfachauswahl nicht duplizierbarer Talente"""
        # Wähle Reich aus
        self.manager.waehle_talent("Reich")
        
        # Versuche nochmal zu wählen
        result = self.manager.waehle_talent("Reich")
        self.assertEqual(result, "not_duplicatable")
    
    def test_waehle_freies_talent(self):
        """Test freie Talent-Auswahl"""
        result = self.manager.waehle_freies_talent("Glück")
        self.assertTrue(result)
        self.assertTrue(self.charakter.talente["Glück"].ausgewaehlt)
        # Handicap-Punkte sollten unverändert bleiben
        self.assertEqual(self.charakter.verbleibende_handicap_punkte, 4.0)
    
    def test_waehle_pathfinder_kostenloses_talent(self):
        """Test kostenlose Pathfinder-Talent-Auswahl"""
        result = self.manager.waehle_pathfinder_kostenloses_talent("Klassen-Talent")
        self.assertTrue(result)
        self.assertTrue(self.charakter.talente["Klassen-Talent"].ausgewaehlt)
        self.assertEqual(self.charakter.pathfinder_kostenlose_talente_gewaehlt, 1)
    
    def test_talent_abwaehlen(self):
        """Test Talent-Abwahl"""
        # Erst auswählen
        self.manager.waehle_talent("Glück")
        self.assertTrue(self.charakter.talente["Glück"].ausgewaehlt)
        
        # Dann abwählen
        result = self.manager.talent_abwaehlen("Glück")
        self.assertTrue(result)
        self.assertFalse(self.charakter.talente["Glück"].ausgewaehlt)
        self.assertNotIn("Glück", self.charakter.selected_talente)
    
    def test_arkaner_hintergrund_machtpunkte(self):
        """Test Arkaner Hintergrund Machtpunkte-Gewährung"""
        result = self.manager.waehle_talent("Arkaner Hintergrund: Magie")
        self.assertTrue(result)
        self.assertEqual(self.charakter.verfuegbare_maechte, 3)
        self.assertEqual(self.charakter.anzahl_maechte, 3)
        self.assertEqual(self.charakter.machtpunkte, 10)
    
    def test_pruefe_voraussetzungen_attribut(self):
        """Test Voraussetzungen-Prüfung für Attribute"""
        talent = self.charakter.talente["Kämpfer"]
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        
        # GES W8 ist erfüllt (haben W6)
        self.assertEqual(len(fehlermeldungen), 1)
        self.assertIn("Geschicklichkeit", fehlermeldungen[0])
    
    def test_pruefe_voraussetzungen_fertigkeit(self):
        """Test Voraussetzungen-Prüfung für Fertigkeiten"""
        talent = self.charakter.talente["Meisterschütze"]
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        
        # Schiessen W8 ist nicht erfüllt (haben W4)
        self.assertEqual(len(fehlermeldungen), 1)
        self.assertIn("Schiessen", fehlermeldungen[0])
    
    def test_pruefe_voraussetzungen_talent(self):
        """Test Voraussetzungen-Prüfung für Talente"""
        talent = self.charakter.talente["Großes Glück"]
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        
        # Glück ist nicht ausgewählt
        self.assertEqual(len(fehlermeldungen), 1)
        self.assertIn("Glück", fehlermeldungen[0])
    
    def test_mehrfachauswahl_erlaubt(self):
        """Test Mehrfachauswahl bei erlaubten Talenten"""
        # Verwende Kämpfer statt Glück (Glück ist laut Config nicht duplizierbar)
        self.charakter.attribute["Geschicklichkeit"].wuerfel.value = 8  # Erfülle Voraussetzung
        
        # Wähle Kämpfer aus (ist duplizierbar)
        self.manager.waehle_talent("Kämpfer")
        
        # Wähle nochmal - sollte neue Instanz erstellen
        result = self.manager.waehle_talent("Kämpfer")
        self.assertTrue(result)
        
        # Sollte jetzt Kämpfer_2 geben
        self.assertIn("Kämpfer_2", self.charakter.talente)
        self.assertTrue(self.charakter.talente["Kämpfer_2"].ausgewaehlt)


class TestTalentManagerCompatibility(unittest.TestCase):
    """Tests für Rückwärtskompatibilität"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.charakter = MockCharakter()
    
    def test_get_talent_manager(self):
        """Test get_talent_manager Funktion"""
        manager = get_talent_manager(self.charakter)
        self.assertIsInstance(manager, TalentManager)
        self.assertEqual(manager.charakter, self.charakter)
    
    def test_legacy_functions_work(self):
        """Test dass alte Funktionen noch funktionieren"""
        # Teste alte waehle_talent Funktion
        result = talent_funktionen.waehle_talent(self.charakter, "Glück")
        self.assertTrue(result)
        self.assertTrue(self.charakter.talente["Glück"].ausgewaehlt)
        
        # Teste alte talent_abwaehlen Funktion
        result = talent_funktionen.talent_abwaehlen(self.charakter, "Glück")
        self.assertTrue(result)
        self.assertFalse(self.charakter.talente["Glück"].ausgewaehlt)
    
    def test_legacy_waehle_freies_talent(self):
        """Test alte waehle_freies_talent Funktion"""
        result = talent_funktionen.waehle_freies_talent(self.charakter, "Glück")
        self.assertTrue(result)
        self.assertTrue(self.charakter.talente["Glück"].ausgewaehlt)
    
    def test_legacy_pruefe_voraussetzungen(self):
        """Test alte pruefe_voraussetzungen Funktion"""
        talent = self.charakter.talente["Kämpfer"]
        fehlermeldungen = talent_funktionen.pruefe_voraussetzungen(self.charakter, talent)
        self.assertIsInstance(fehlermeldungen, list)


class TestTalentConfigIntegration(unittest.TestCase):
    """Tests für Config-Integration"""
    
    def test_config_get_method(self):
        """Test TalentConfig.get Methode"""
        handicap_punkte = TalentConfig.get('kosten.handicap_punkte', 0)
        self.assertEqual(handicap_punkte, 2)
        
        nicht_duplizierbar = TalentConfig.get('nicht_duplizierbare_talente', [])
        self.assertIn('Reich', nicht_duplizierbar)
        self.assertIn('Glück', nicht_duplizierbar)
    
    def test_config_default_fallback(self):
        """Test Config-Fallback auf Standardwerte"""
        inexistent = TalentConfig.get('inexistent.key', 'default')
        self.assertEqual(inexistent, 'default')


def run_talent_manager_tests():
    """Führt alle TalentManager Tests aus"""
    print("="*60)
    print("TALENT MANAGER UNIT TESTS")
    print("="*60)
    
    # Erstelle Test-Suite
    suite = unittest.TestSuite()
    
    # Füge alle Test-Klassen hinzu
    suite.addTest(unittest.makeSuite(TestTalentManager))
    suite.addTest(unittest.makeSuite(TestTalentManagerCompatibility))
    suite.addTest(unittest.makeSuite(TestTalentConfigIntegration))
    
    # Führe Tests aus
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Zeige Zusammenfassung
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("🎉 ALLE TALENT MANAGER TESTS ERFOLGREICH!")
        print(f"✅ {result.testsRun} Tests bestanden")
    else:
        print("❌ EINIGE TALENT MANAGER TESTS FEHLGESCHLAGEN!")
        print(f"❌ {len(result.failures)} Fehler, {len(result.errors)} Exceptions")
        for test, error in result.failures + result.errors:
            print(f"  - {test}: {error.splitlines()[-1] if error else 'Unbekannter Fehler'}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_talent_manager_tests()
    sys.exit(0 if success else 1)