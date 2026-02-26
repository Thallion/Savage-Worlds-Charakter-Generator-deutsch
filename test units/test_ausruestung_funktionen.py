"""
Test-Units für ausruestung_funktionen.py

Diese Tests prüfen die Funktionalität der verbesserten Ausrüstungs-Funktionen
einschließlich der neuen Konfigurationsdatei-Integration.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Pfad zur Projektroot hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Imports der zu testenden Module
from functions.ausruestung_funktionen import (
    kaufen, 
    verkaufen, 
    berechne_gesamt_ruestungsschutz,
    get_item_by_name,
    berechne_gesamtkosten,
    anpassen_vermoegen_bei_handicap_arm,
    anpassen_vermoegen_bei_talent_reich,
    erstelle_item_nach_kategorie,
    _pruefe_traglast,
    _item_zu_ausruestung_hinzufuegen,
    _item_aus_ausruestung_entfernen,
    _berechne_vermoegen_multiplikator
)

from config.ausruestung_config import (
    AusruestungKategorien,
    RuestungsKoerperteile,
    TraglastKonstanten,
    LogMessages
)

from models.ausruestung import Ausruestung
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild


class TestAusruestungKonfig(unittest.TestCase):
    """Tests für die Ausrüstungs-Konfiguration"""
    
    def test_kategorien_vollständig(self):
        """Test ob alle erwarteten Kategorien vorhanden sind"""
        kategorien = AusruestungKategorien.alle()
        erwartet = ["Waffe", "Rüstung", "Schild", "Allgemein"]
        self.assertEqual(kategorien, erwartet)
    
    def test_kategorie_validierung(self):
        """Test der Kategorie-Validierung"""
        self.assertTrue(AusruestungKategorien.ist_gueltig("Waffe"))
        self.assertTrue(AusruestungKategorien.ist_gueltig("Rüstung"))
        self.assertFalse(AusruestungKategorien.ist_gueltig("Ungültig"))
    
    def test_koerperteile_standard_schutz(self):
        """Test der Standard-Schutzwerte"""
        schutz = RuestungsKoerperteile.standard_schutz()
        erwartet = {"Torso": 0, "Arme": 0, "Beine": 0, "Kopf": 0}
        self.assertEqual(schutz, erwartet)
    
    def test_traglast_konstanten(self):
        """Test der Traglast-Konstanten"""
        self.assertEqual(TraglastKonstanten.MAX_ERSCHOEPFUNG, 3)
        self.assertEqual(TraglastKonstanten.STANDARD_MULTIPLIKATOR, 1)
        self.assertIn("Reich", TraglastKonstanten.TALENT_MULTIPLIKATOREN)
        self.assertIn("Stinkreich", TraglastKonstanten.TALENT_MULTIPLIKATOREN)


class TestAusruestungFunktionen(unittest.TestCase):
    """Tests für die Ausrüstungs-Funktionen"""

    def setUp(self):
        """Setup für jeden Test"""
        # Mock-Charakter erstellen
        self.charakter = Mock()
        self.charakter.vermoegen = 500
        self.charakter.startkapital = 500
        self.charakter.erschoepfung = 0
        self.charakter.gesamtgewicht = 0
        self.charakter.ausruestung = {}
        self.charakter.selected_allgemeine_ausruestung = []
        self.charakter.selected_waffen = []
        self.charakter.selected_ruestungen = []
        self.charakter.selected_schilde = []
        self.charakter.waffen = {}
        self.charakter.ruestungen = {}
        self.charakter.schilde = {}
        self.charakter.selected_talente = set()
        self.charakter.selected_handicaps = set()
        
        # Mock-Funktionen
        self.charakter.berechne_gesamtgewicht = Mock()
        self.charakter.berechne_traglast = Mock(return_value=100)
        self.charakter.berechne_abgeleitete_werte = Mock()
        
        # Test-Item erstellen
        self.test_item = Mock(spec=Ausruestung)
        self.test_item.name = "Test Schwert"
        self.test_item.kosten = 100
        self.test_item.menge = 1
        self.test_item.gewicht = 2.0
        self.test_item.kategorie = AusruestungKategorien.WAFFE
        self.test_item.erhoehe_menge = Mock()
        self.test_item.verringere_menge = Mock()
    
    def test_kaufen_erfolgreich(self):
        """Test erfolgreichen Kauf"""
        result = kaufen(self.charakter, self.test_item, 1)
        
        self.assertTrue(result)
        self.assertEqual(self.charakter.vermoegen, 400)  # 500 - 100
        self.test_item.erhoehe_menge.assert_called_once_with(1)
    
    def test_kaufen_unzureichendes_vermoegen(self):
        """Test Kauf mit unzureichendem Vermögen"""
        self.charakter.vermoegen = 50
        
        result = kaufen(self.charakter, self.test_item, 1)
        
        self.assertFalse(result)
        self.assertEqual(self.charakter.vermoegen, 50)  # Unverändert
        self.test_item.erhoehe_menge.assert_not_called()
    
    def test_kaufen_mehrere_items(self):
        """Test Kauf mehrerer Items"""
        result = kaufen(self.charakter, self.test_item, 3)
        
        self.assertTrue(result)
        self.assertEqual(self.charakter.vermoegen, 200)  # 500 - 300
        self.test_item.erhoehe_menge.assert_called_once_with(3)
    
    def test_verkaufen_erfolgreich(self):
        """Test erfolgreichen Verkauf"""
        self.test_item.menge = 2
        
        result = verkaufen(self.charakter, self.test_item, 1)
        
        self.assertTrue(result)
        self.assertEqual(self.charakter.vermoegen, 550)  # 500 + 50 (50% von 100)
        self.test_item.verringere_menge.assert_called_once_with(1)
    
    def test_verkaufen_unzureichende_menge(self):
        """Test Verkauf mit unzureichender Menge"""
        self.test_item.menge = 1
        
        result = verkaufen(self.charakter, self.test_item, 2)
        
        self.assertFalse(result)
        self.assertEqual(self.charakter.vermoegen, 500)  # Unverändert
        self.test_item.verringere_menge.assert_not_called()
    
    def test_verkaufen_item_entfernen_bei_null_menge(self):
        """Test dass Item entfernt wird wenn Menge 0 erreicht"""
        self.test_item.menge = 1
        self.test_item.name = "Test Item"
        self.charakter.ausruestung["Test Item"] = self.test_item
        self.charakter.selected_allgemeine_ausruestung = [self.test_item]
        
        # Mock für verringere_menge um menge auf 0 zu setzen
        def mock_verringere_menge(anzahl):
            self.test_item.menge = 0
        
        self.test_item.verringere_menge = Mock(side_effect=mock_verringere_menge)
        
        result = verkaufen(self.charakter, self.test_item, 1)
        
        self.assertTrue(result)
        self.assertEqual(len(self.charakter.ausruestung), 0)
        self.assertEqual(len(self.charakter.selected_allgemeine_ausruestung), 0)
    
    @patch('functions.ausruestung_funktionen.Logger')
    def test_ruestungsschutz_berechnung(self, mock_logger):
        """Test Berechnung des Rüstungsschutzes"""
        # Mock-Rüstung erstellen
        ruestung1 = Mock(spec=Ruestung)
        ruestung1.angelegt = True
        ruestung1.ausgewaehlt = True
        ruestung1.torso = 2
        ruestung1.arme = 1
        ruestung1.beine = 1
        ruestung1.kopf = 0
        ruestung1.name = "Lederrüstung"
        
        ruestung2 = Mock(spec=Ruestung)
        ruestung2.angelegt = True
        ruestung2.ausgewaehlt = True
        ruestung2.torso = 1
        ruestung2.arme = 0
        ruestung2.beine = 0
        ruestung2.kopf = 2
        ruestung2.name = "Helm"
        
        self.charakter.ausruestung = {
            "Lederrüstung": ruestung1,
            "Helm": ruestung2
        }
        
        schutz = berechne_gesamt_ruestungsschutz(self.charakter)
        
        erwartet = {
            RuestungsKoerperteile.TORSO: 3,  # 2 + 1
            RuestungsKoerperteile.ARME: 1,   # 1 + 0
            RuestungsKoerperteile.BEINE: 1,  # 1 + 0
            RuestungsKoerperteile.KOPF: 2    # 0 + 2
        }
        
        self.assertEqual(schutz, erwartet)
    
    def test_get_item_by_name(self):
        """Test Item-Suche nach Name"""
        item1 = Mock()
        item1.name = "Schwert"
        item2 = Mock()
        item2.name = "Schild"
        
        self.charakter.selected_waffen = [item1]
        self.charakter.selected_schilde = [item2]
        self.charakter.selected_ruestungen = []
        self.charakter.selected_allgemeine_ausruestung = []
        
        result = get_item_by_name(self.charakter, "Schwert")
        self.assertEqual(result, item1)
        
        result = get_item_by_name(self.charakter, "Schild")
        self.assertEqual(result, item2)
        
        result = get_item_by_name(self.charakter, "Nicht vorhanden")
        self.assertIsNone(result)
    
    def test_berechne_gesamtkosten(self):
        """Test Berechnung der Gesamtkosten"""
        item1 = Mock()
        item1.ausgewaehlt = True
        item1.kosten = 100
        item1.menge = 2
        
        item2 = Mock()
        item2.ausgewaehlt = True
        item2.kosten = 50
        item2.menge = 1
        
        item3 = Mock()
        item3.ausgewaehlt = False  # Nicht ausgewählt
        item3.kosten = 200
        item3.menge = 1
        
        self.charakter.ausruestung = {
            "Item1": item1,
            "Item2": item2,
            "Item3": item3
        }
        
        kosten = berechne_gesamtkosten(self.charakter)
        self.assertEqual(kosten, 250)  # (100*2) + (50*1) = 250
    
    def test_anpassen_vermoegen_handicap_arm_aktiviert(self):
        """Test Vermögens-Anpassung bei Handicap 'Arm' aktiviert"""
        self.charakter.vermoegen = 500
        
        anpassen_vermoegen_bei_handicap_arm(self.charakter, True)
        
        self.assertEqual(self.charakter.vermoegen, 250)  # Halbiert
    
    def test_anpassen_vermoegen_handicap_arm_deaktiviert(self):
        """Test Vermögens-Anpassung bei Handicap 'Arm' deaktiviert"""
        self.charakter.vermoegen = 250
        self.charakter.startkapital = 500
        self.charakter.selected_talente = set()
        
        anpassen_vermoegen_bei_handicap_arm(self.charakter, False)
        
        self.assertEqual(self.charakter.vermoegen, 500)  # Wiederhergestellt
    
    def test_anpassen_vermoegen_talent_reich(self):
        """Test Vermögens-Anpassung bei Talent 'Reich'"""
        self.charakter.startkapital = 500
        self.charakter.selected_handicaps = set()  # Kein 'Arm' aktiv
        
        anpassen_vermoegen_bei_talent_reich(self.charakter, "Reich", True)
        
        self.assertEqual(self.charakter.vermoegen, 1500)  # 500 * 3
    
    def test_anpassen_vermoegen_talent_stinkreich(self):
        """Test Vermögens-Anpassung bei Talent 'Stinkreich'"""
        self.charakter.startkapital = 500
        self.charakter.selected_handicaps = set()
        
        anpassen_vermoegen_bei_talent_reich(self.charakter, "Stinkreich", True)
        
        self.assertEqual(self.charakter.vermoegen, 2500)  # 500 * 5
    
    def test_anpassen_vermoegen_talent_mit_arm_handicap(self):
        """Test dass Reich-Talent bei aktivem Arm-Handicap ignoriert wird"""
        self.charakter.startkapital = 500
        self.charakter.selected_handicaps = {"Arm"}
        original_vermoegen = self.charakter.vermoegen
        
        anpassen_vermoegen_bei_talent_reich(self.charakter, "Reich", True)
        
        # Vermögen sollte unverändert bleiben
        self.assertEqual(self.charakter.vermoegen, original_vermoegen)
    
    def test_erstelle_item_nach_kategorie_waffe(self):
        """Test Item-Erstellung für Waffe"""
        item_dict = {
            'kategorie': AusruestungKategorien.WAFFE,
            'name': 'Schwert',
            'kosten': 100
        }
        
        with patch('functions.ausruestung_funktionen.Waffe') as mock_waffe:
            mock_waffe.from_setting_dict.return_value = Mock()
            
            result = erstelle_item_nach_kategorie(item_dict)
            
            mock_waffe.from_setting_dict.assert_called_once_with(item_dict)
    
    def test_erstelle_item_nach_kategorie_unbekannt(self):
        """Test Item-Erstellung für unbekannte Kategorie"""
        item_dict = {
            'kategorie': 'Unbekannt',
            'name': 'Test',
            'kosten': 50
        }
        
        with patch('functions.ausruestung_funktionen.Ausruestung') as mock_ausruestung:
            mock_ausruestung.from_setting_dict.return_value = Mock()
            
            result = erstelle_item_nach_kategorie(item_dict)
            
            mock_ausruestung.from_setting_dict.assert_called_once_with(item_dict)
    
    def test_pruefe_traglast_ueberschritten(self):
        """Test Traglast-Prüfung bei Überschreitung"""
        self.charakter.gesamtgewicht = 150
        self.charakter.berechne_traglast.return_value = 100
        self.charakter.erschoepfung = 1
        
        _pruefe_traglast(self.charakter)
        
        self.assertEqual(self.charakter.erschoepfung, 2)
    
    def test_pruefe_traglast_max_erschoepfung(self):
        """Test Traglast-Prüfung bei maximaler Erschöpfung"""
        self.charakter.gesamtgewicht = 150
        self.charakter.berechne_traglast.return_value = 100
        self.charakter.erschoepfung = TraglastKonstanten.MAX_ERSCHOEPFUNG
        
        _pruefe_traglast(self.charakter)
        
        # Erschöpfung sollte nicht weiter steigen
        self.assertEqual(self.charakter.erschoepfung, TraglastKonstanten.MAX_ERSCHOEPFUNG)
    
    def test_berechne_vermoegen_multiplikator(self):
        """Test Berechnung des Vermögens-Multiplikators"""
        # Kein Talent aktiv
        self.charakter.selected_talente = set()
        multiplikator = _berechne_vermoegen_multiplikator(self.charakter)
        self.assertEqual(multiplikator, 1)
        
        # Reich aktiv
        self.charakter.selected_talente = {"Reich"}
        multiplikator = _berechne_vermoegen_multiplikator(self.charakter)
        self.assertEqual(multiplikator, 3)
        
        # Stinkreich aktiv (höchster Wert)
        self.charakter.selected_talente = {"Reich", "Stinkreich"}
        multiplikator = _berechne_vermoegen_multiplikator(self.charakter)
        self.assertEqual(multiplikator, 5)
        
        # Stinkreich ausschließen
        multiplikator = _berechne_vermoegen_multiplikator(self.charakter, exclude_talent="Stinkreich")
        self.assertEqual(multiplikator, 3)


class TestIntegration(unittest.TestCase):
    """Integrationstests"""
    
    def setUp(self):
        """Setup für Integrationstests"""
        # Echter Mock-Charakter mit realistischeren Werten
        self.charakter = Mock()
        self.charakter.vermoegen = 500
        self.charakter.startkapital = 500
        self.charakter.erschoepfung = 0
        self.charakter.gesamtgewicht = 10
        self.charakter.ausruestung = {}
        self.charakter.selected_allgemeine_ausruestung = []
        self.charakter.selected_waffen = []
        self.charakter.selected_ruestungen = []
        self.charakter.selected_schilde = []
        self.charakter.selected_talente = set()
        self.charakter.selected_handicaps = set()
        
        self.charakter.berechne_gesamtgewicht = Mock()
        self.charakter.berechne_traglast = Mock(return_value=80)
        self.charakter.berechne_abgeleitete_werte = Mock()
    
    def test_vollstaendiger_kaufprozess(self):
        """Test eines vollständigen Kauf-Prozesses"""
        # Test-Item erstellen
        schwert = Mock(spec=Waffe)
        schwert.name = "Langschwert"
        schwert.kosten = 150
        schwert.menge = 0
        schwert.gewicht = 3.0
        schwert.kategorie = AusruestungKategorien.WAFFE
        schwert.erhoehe_menge = Mock(side_effect=lambda x: setattr(schwert, 'menge', schwert.menge + x))
        
        # Kaufen
        result = kaufen(self.charakter, schwert, 1)
        
        # Verifikation
        self.assertTrue(result)
        self.assertEqual(self.charakter.vermoegen, 350)  # 500 - 150
        self.assertEqual(schwert.menge, 1)
        self.charakter.berechne_abgeleitete_werte.assert_called()
    
    def test_kauf_und_verkauf_zyklus(self):
        """Test Kauf und anschließender Verkauf"""
        # Setup
        item = Mock(spec=Ausruestung)
        item.name = "Test Item"
        item.kosten = 100
        item.menge = 0
        item.kategorie = AusruestungKategorien.ALLGEMEIN
        
        def mock_erhoehe_menge(anzahl):
            item.menge += anzahl
        
        def mock_verringere_menge(anzahl):
            item.menge -= anzahl
        
        item.erhoehe_menge = Mock(side_effect=mock_erhoehe_menge)
        item.verringere_menge = Mock(side_effect=mock_verringere_menge)
        
        # Kaufen
        kauf_result = kaufen(self.charakter, item, 2)
        self.assertTrue(kauf_result)
        self.assertEqual(self.charakter.vermoegen, 300)  # 500 - 200
        self.assertEqual(item.menge, 2)
        
        # Verkaufen (einen Teil)
        verkauf_result = verkaufen(self.charakter, item, 1)
        self.assertTrue(verkauf_result)
        self.assertEqual(self.charakter.vermoegen, 350)  # 300 + 50 (50% von 100)
        self.assertEqual(item.menge, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)