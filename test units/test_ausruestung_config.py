"""
Test-Units für ausruestung_config.py

Diese Tests prüfen die Konfigurationsklassen und Konstanten für die Ausrüstung.
"""

import unittest
import sys
from pathlib import Path

# Pfad zur Projektroot hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Imports der zu testenden Module
from config.ausruestung_config import (
    AusruestungKategorien,
    RuestungsKoerperteile,
    WaffenEigenschaften,
    SchildEigenschaften,
    StaerkeWerte,
    TraglastKonstanten,
    LogMessages
)


class TestAusruestungKategorien(unittest.TestCase):
    """Tests für die AusruestungKategorien-Klasse"""
    
    def test_konstanten_definiert(self):
        """Test ob alle Kategorien korrekt definiert sind"""
        self.assertEqual(AusruestungKategorien.WAFFE, "Waffe")
        self.assertEqual(AusruestungKategorien.RUESTUNG, "Rüstung")
        self.assertEqual(AusruestungKategorien.SCHILD, "Schild")
        self.assertEqual(AusruestungKategorien.ALLGEMEIN, "Allgemein")
    
    def test_alle_methode(self):
        """Test der alle() Methode"""
        kategorien = AusruestungKategorien.alle()
        erwartet = ["Waffe", "Rüstung", "Schild", "Allgemein"]
        
        self.assertEqual(kategorien, erwartet)
        self.assertIsInstance(kategorien, list)
        self.assertEqual(len(kategorien), 4)
    
    def test_ist_gueltig_methode(self):
        """Test der ist_gueltig() Methode"""
        # Gültige Kategorien
        self.assertTrue(AusruestungKategorien.ist_gueltig("Waffe"))
        self.assertTrue(AusruestungKategorien.ist_gueltig("Rüstung"))
        self.assertTrue(AusruestungKategorien.ist_gueltig("Schild"))
        self.assertTrue(AusruestungKategorien.ist_gueltig("Allgemein"))
        
        # Ungültige Kategorien
        self.assertFalse(AusruestungKategorien.ist_gueltig("Ungültig"))
        self.assertFalse(AusruestungKategorien.ist_gueltig(""))
        self.assertFalse(AusruestungKategorien.ist_gueltig(None))
        self.assertFalse(AusruestungKategorien.ist_gueltig("waffe"))  # Case-sensitive


class TestRuestungsKoerperteile(unittest.TestCase):
    """Tests für die RuestungsKoerperteile-Klasse"""
    
    def test_konstanten_definiert(self):
        """Test ob alle Körperteile korrekt definiert sind"""
        self.assertEqual(RuestungsKoerperteile.TORSO, "Torso")
        self.assertEqual(RuestungsKoerperteile.ARME, "Arme")
        self.assertEqual(RuestungsKoerperteile.BEINE, "Beine")
        self.assertEqual(RuestungsKoerperteile.KOPF, "Kopf")
    
    def test_alle_methode(self):
        """Test der alle() Methode"""
        teile = RuestungsKoerperteile.alle()
        erwartet = ["Torso", "Arme", "Beine", "Kopf"]
        
        self.assertEqual(teile, erwartet)
        self.assertIsInstance(teile, list)
        self.assertEqual(len(teile), 4)
    
    def test_standard_schutz_methode(self):
        """Test der standard_schutz() Methode"""
        schutz = RuestungsKoerperteile.standard_schutz()
        
        erwartet = {
            "Torso": 0,
            "Arme": 0,
            "Beine": 0,
            "Kopf": 0
        }
        
        self.assertEqual(schutz, erwartet)
        self.assertIsInstance(schutz, dict)
        
        # Prüfen ob alle Körperteile enthalten sind
        for teil in RuestungsKoerperteile.alle():
            self.assertIn(teil, schutz)
            self.assertEqual(schutz[teil], 0)


class TestWaffenEigenschaften(unittest.TestCase):
    """Tests für die WaffenEigenschaften-Klasse"""
    
    def test_konstanten_definiert(self):
        """Test ob alle Waffeneigenschaften korrekt definiert sind"""
        self.assertEqual(WaffenEigenschaften.SCHADEN, "Schaden")
        self.assertEqual(WaffenEigenschaften.REICHWEITE, "Reichweite")
        self.assertEqual(WaffenEigenschaften.FEUERRATE, "FR")
        self.assertEqual(WaffenEigenschaften.SCHUSS, "Schuss")
        self.assertEqual(WaffenEigenschaften.PANZERBRECHER, "PB")
    
    def test_standard_eigenschaften_methode(self):
        """Test der standard_eigenschaften() Methode"""
        eigenschaften = WaffenEigenschaften.standard_eigenschaften()
        
        erwartet = {
            "Schaden": "-",
            "Reichweite": "-",
            "FR": "-",
            "Schuss": "-",
            "PB": "-"
        }
        
        self.assertEqual(eigenschaften, erwartet)
        self.assertIsInstance(eigenschaften, dict)
        self.assertEqual(len(eigenschaften), 5)
        
        # Prüfen ob alle Werte auf "-" gesetzt sind
        for wert in eigenschaften.values():
            self.assertEqual(wert, "-")


class TestSchildEigenschaften(unittest.TestCase):
    """Tests für die SchildEigenschaften-Klasse"""
    
    def test_konstanten_definiert(self):
        """Test ob alle Schildeigenschaften korrekt definiert sind"""
        self.assertEqual(SchildEigenschaften.PARADE, "parade")
        self.assertEqual(SchildEigenschaften.DECKUNG, "deckung")
        self.assertEqual(SchildEigenschaften.MINDESTSTAERKE, "mindeststaerke")
    
    def test_standard_eigenschaften_methode(self):
        """Test der standard_eigenschaften() Methode"""
        eigenschaften = SchildEigenschaften.standard_eigenschaften()
        
        erwartet = {
            "parade": 0,
            "deckung": 0,
            "mindeststaerke": "W4"
        }
        
        self.assertEqual(eigenschaften, erwartet)
        self.assertIsInstance(eigenschaften, dict)
        self.assertEqual(len(eigenschaften), 3)
        
        # Spezifische Werte prüfen
        self.assertEqual(eigenschaften["parade"], 0)
        self.assertEqual(eigenschaften["deckung"], 0)
        self.assertEqual(eigenschaften["mindeststaerke"], "W4")


class TestStaerkeWerte(unittest.TestCase):
    """Tests für die StaerkeWerte-Klasse"""
    
    def test_konstanten_definiert(self):
        """Test ob alle Stärkewerte korrekt definiert sind"""
        self.assertEqual(StaerkeWerte.W4, "W4")
        self.assertEqual(StaerkeWerte.W6, "W6")
        self.assertEqual(StaerkeWerte.W8, "W8")
        self.assertEqual(StaerkeWerte.W10, "W10")
        self.assertEqual(StaerkeWerte.W12, "W12")
        self.assertEqual(StaerkeWerte.KEINE, "-")
    
    def test_mapping_vollständig(self):
        """Test ob das MAPPING alle erwarteten Werte enthält"""
        mapping = StaerkeWerte.MAPPING
        
        erwartet = {
            "W4": 4,
            "W6": 6,
            "W8": 8,
            "W10": 10,
            "W12": 12,
            "-": 0
        }
        
        self.assertEqual(mapping, erwartet)
        self.assertEqual(len(mapping), 6)
    
    def test_zu_nummer_methode(self):
        """Test der zu_nummer() Methode"""
        # Gültige Werte
        self.assertEqual(StaerkeWerte.zu_nummer("W4"), 4)
        self.assertEqual(StaerkeWerte.zu_nummer("W6"), 6)
        self.assertEqual(StaerkeWerte.zu_nummer("W8"), 8)
        self.assertEqual(StaerkeWerte.zu_nummer("W10"), 10)
        self.assertEqual(StaerkeWerte.zu_nummer("W12"), 12)
        self.assertEqual(StaerkeWerte.zu_nummer("-"), 0)
        
        # Ungültige Werte
        self.assertEqual(StaerkeWerte.zu_nummer("W20"), 0)  # Default
        self.assertEqual(StaerkeWerte.zu_nummer(""), 0)
        self.assertEqual(StaerkeWerte.zu_nummer(None), 0)
    
    def test_ist_gueltig_methode(self):
        """Test der ist_gueltig() Methode"""
        # Gültige Werte
        self.assertTrue(StaerkeWerte.ist_gueltig("W4"))
        self.assertTrue(StaerkeWerte.ist_gueltig("W6"))
        self.assertTrue(StaerkeWerte.ist_gueltig("W8"))
        self.assertTrue(StaerkeWerte.ist_gueltig("W10"))
        self.assertTrue(StaerkeWerte.ist_gueltig("W12"))
        self.assertTrue(StaerkeWerte.ist_gueltig("-"))
        
        # Ungültige Werte
        self.assertFalse(StaerkeWerte.ist_gueltig("W20"))
        self.assertFalse(StaerkeWerte.ist_gueltig(""))
        self.assertFalse(StaerkeWerte.ist_gueltig(None))
        self.assertFalse(StaerkeWerte.ist_gueltig("w4"))  # Case-sensitive


class TestTraglastKonstanten(unittest.TestCase):
    """Tests für die TraglastKonstanten-Klasse"""
    
    def test_konstanten_definiert(self):
        """Test ob alle Konstanten korrekt definiert sind"""
        self.assertEqual(TraglastKonstanten.MAX_ERSCHOEPFUNG, 3)
        self.assertEqual(TraglastKonstanten.STANDARD_MULTIPLIKATOR, 1)
    
    def test_talent_multiplikatoren(self):
        """Test der TALENT_MULTIPLIKATOREN"""
        multiplikatoren = TraglastKonstanten.TALENT_MULTIPLIKATOREN
        
        erwartet = {
            "Stinkreich": 5,
            "Reich": 3
        }
        
        self.assertEqual(multiplikatoren, erwartet)
        self.assertIsInstance(multiplikatoren, dict)
        self.assertEqual(len(multiplikatoren), 2)
        
        # Spezifische Werte prüfen
        self.assertEqual(multiplikatoren["Stinkreich"], 5)
        self.assertEqual(multiplikatoren["Reich"], 3)
        
        # Prüfen ob Stinkreich höher als Reich ist
        self.assertGreater(multiplikatoren["Stinkreich"], multiplikatoren["Reich"])


class TestLogMessages(unittest.TestCase):
    """Tests für die LogMessages-Klasse"""
    
    def test_erfolg_messages_definiert(self):
        """Test ob alle Erfolgs-Nachrichten definiert sind"""
        self.assertIsInstance(LogMessages.KAUF_ERFOLGREICH, str)
        self.assertIsInstance(LogMessages.VERKAUF_ERFOLGREICH, str)
        self.assertIsInstance(LogMessages.ITEM_ZU_LISTE_HINZUGEFUEGT, str)
        self.assertIsInstance(LogMessages.RUESTUNG_ANGELEGT, str)
        self.assertIsInstance(LogMessages.RUESTUNG_ABGELEGT, str)
        
        # Prüfen ob Format-Platzhalter enthalten sind
        self.assertIn("{anzahl}", LogMessages.KAUF_ERFOLGREICH)
        self.assertIn("{name}", LogMessages.KAUF_ERFOLGREICH)
        self.assertIn("{preis}", LogMessages.KAUF_ERFOLGREICH)
        self.assertIn("{vermoegen}", LogMessages.KAUF_ERFOLGREICH)
    
    def test_warnungs_messages_definiert(self):
        """Test ob alle Warnungs-Nachrichten definiert sind"""
        self.assertIsInstance(LogMessages.NICHT_GENUEGEND_VERMOEGEN, str)
        self.assertIsInstance(LogMessages.NICHT_GENUEGEND_MENGE, str)
        self.assertIsInstance(LogMessages.TRAGLAST_UEBERSCHRITTEN, str)
        self.assertIsInstance(LogMessages.TRAGLAST_MAXIMAL, str)
        self.assertIsInstance(LogMessages.ELEMENT_EXISTIERT_NICHT, str)
        self.assertIsInstance(LogMessages.MINDESTSTAERKE_NICHT_ERFUELLT, str)
    
    def test_info_messages_definiert(self):
        """Test ob alle Info-Nachrichten definiert sind"""
        self.assertIsInstance(LogMessages.ELEMENTE_GELADEN, str)
        self.assertIsInstance(LogMessages.HANDICAP_ARM_AKTIVIERT, str)
        self.assertIsInstance(LogMessages.HANDICAP_ARM_DEAKTIVIERT, str)
        self.assertIsInstance(LogMessages.TALENT_REICH_AKTIVIERT, str)
        self.assertIsInstance(LogMessages.TALENT_REICH_DEAKTIVIERT, str)
    
    def test_fehler_messages_definiert(self):
        """Test ob alle Fehler-Nachrichten definiert sind"""
        self.assertIsInstance(LogMessages.FEHLER_BEIM_LADEN, str)
        self.assertIsInstance(LogMessages.FEHLER_ALLGEMEIN, str)
    
    def test_debug_messages_definiert(self):
        """Test ob alle Debug-Nachrichten definiert sind"""
        self.assertIsInstance(LogMessages.RUESTUNG_ZU_GESAMT, str)
        self.assertIsInstance(LogMessages.GESAMTRUESTUNG_BERECHNET, str)
    
    def test_message_formatting(self):
        """Test der Nachrichten-Formatierung"""
        # Test einer Beispiel-Nachricht
        test_message = LogMessages.KAUF_ERFOLGREICH
        formatted = test_message.format(
            anzahl=2,
            name="Schwert",
            preis=200,
            vermoegen=300
        )
        
        self.assertIn("2", formatted)
        self.assertIn("Schwert", formatted)
        self.assertIn("200", formatted)
        self.assertIn("300", formatted)
        
        # Prüfen ob keine Platzhalter mehr vorhanden sind
        self.assertNotIn("{", formatted)
        self.assertNotIn("}", formatted)
    
    def test_all_messages_haben_inhalt(self):
        """Test ob alle Nachrichten nicht-leeren Inhalt haben"""
        import inspect
        
        # Alle Klassenvariablen von LogMessages abrufen
        members = inspect.getmembers(LogMessages, lambda x: isinstance(x, str))
        
        for name, value in members:
            if not name.startswith('_'):  # Private Attribute ignorieren
                self.assertTrue(len(value) > 0, f"Message {name} ist leer")
                self.assertIsInstance(value, str, f"Message {name} ist kein String")


class TestKonfigurationIntegration(unittest.TestCase):
    """Integrationstests für die gesamte Konfiguration"""
    
    def test_alle_exports_verfügbar(self):
        """Test ob alle exportierten Klassen verfügbar sind"""
        from config.ausruestung_config import __all__
        
        erwartete_exports = [
            'AusruestungKategorien',
            'RuestungsKoerperteile',
            'WaffenEigenschaften',
            'SchildEigenschaften',
            'StaerkeWerte',
            'TraglastKonstanten',
            'LogMessages'
        ]
        
        self.assertEqual(set(__all__), set(erwartete_exports))
    
    def test_konsistenz_zwischen_klassen(self):
        """Test Konsistenz zwischen verschiedenen Konfigurationsklassen"""
        # Prüfen ob Standard-Mindeststärke gültiger Stärke-Wert ist
        standard_staerke = SchildEigenschaften.standard_eigenschaften()["mindeststaerke"]
        self.assertTrue(StaerkeWerte.ist_gueltig(standard_staerke))
        
        # Prüfen ob alle Körperteile in Standard-Schutz enthalten sind
        koerperteile = RuestungsKoerperteile.alle()
        standard_schutz = RuestungsKoerperteile.standard_schutz()
        
        for teil in koerperteile:
            self.assertIn(teil, standard_schutz)
    
    def test_dataclass_verhalten(self):
        """Test ob die Klassen sich wie Dataclasses verhalten"""
        # AusruestungKategorien sollte Klassenvariablen haben
        self.assertTrue(hasattr(AusruestungKategorien, 'WAFFE'))
        self.assertTrue(hasattr(AusruestungKategorien, 'alle'))
        self.assertTrue(callable(AusruestungKategorien.alle))
        
        # StaerkeWerte sollte MAPPING-Dictionary haben
        self.assertTrue(hasattr(StaerkeWerte, 'MAPPING'))
        self.assertIsInstance(StaerkeWerte.MAPPING, dict)


if __name__ == '__main__':
    # Test-Suite mit verschiedenen Verbosity-Levels
    unittest.main(verbosity=2)