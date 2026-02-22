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

        # Zauberbücher-Talente für Tests
        self.talente["Zauberbücher"] = Talent(
            name="Zauberbücher",
            kategorie="Magier",
            rang="A",
            voraussetzungen=["Arkaner Hintergrund (Magie)"],
            beschreibung="Erhält drei neue Mächte bei Wahl des Talents Neue Mächte und sofort eine Macht des eigenen Ranges.",
            neue_maechte=0,
            machtpunkte=0
        )

        self.talente["Neue Mächte"] = Talent(
            name="Neue Mächte",
            kategorie="Macht",
            rang="A",
            voraussetzungen=["AH"],
            beschreibung="Dein Charakter kennt zwei neue Mächte.",
            neue_maechte=2,
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


class TestOderVoraussetzungen(unittest.TestCase):
    """Tests für Entweder-Oder-Voraussetzungen"""

    def setUp(self):
        """Setup für jeden Test"""
        self.charakter = MockCharakter()
        # Zusätzliche Fertigkeiten für oder-Tests
        self.charakter.fertigkeiten["Athletik"] = Fertigkeit("Athletik", self.charakter.attribute["Geschicklichkeit"], False)
        self.charakter.fertigkeiten["Schießen"] = Fertigkeit("Schießen", self.charakter.attribute["Geschicklichkeit"], False)
        self.charakter.fertigkeiten["Heilen"] = Fertigkeit("Heilen", self.charakter.attribute["Verstand"], False)
        self.charakter.fertigkeiten["Überleben"] = Fertigkeit("Überleben", self.charakter.attribute["Verstand"], False)
        self.charakter.fertigkeiten["Alchemie"] = Fertigkeit("Alchemie", self.charakter.attribute["Verstand"], False)
        self.manager = TalentManager(self.charakter)

    def test_hat_oder_ausserhalb_klammern_einfach(self):
        """Test: ' oder ' wird außerhalb von Klammern erkannt"""
        self.assertTrue(self.manager._hat_oder_ausserhalb_klammern("Kämpfen oder Schießen W6"))
        self.assertTrue(self.manager._hat_oder_ausserhalb_klammern("Athletik oder Schießen W8"))

    def test_hat_oder_innerhalb_klammern(self):
        """Test: ' oder ' innerhalb von Klammern wird ignoriert"""
        self.assertFalse(self.manager._hat_oder_ausserhalb_klammern("Schwur (leicht oder schwer)"))

    def test_hat_oder_gemischt(self):
        """Test: ' oder ' außerhalb wird erkannt, auch wenn es auch innerhalb vorkommt"""
        self.assertTrue(self.manager._hat_oder_ausserhalb_klammern("AH (Priester) oder AH (Eiferer)"))

    def test_kein_oder(self):
        """Test: String ohne ' oder ' gibt False"""
        self.assertFalse(self.manager._hat_oder_ausserhalb_klammern("Kämpfen W8"))
        self.assertFalse(self.manager._hat_oder_ausserhalb_klammern("Glück"))

    def test_oder_fertigkeit_erste_erfuellt(self):
        """Test: 'Kämpfen oder Schießen W6' - erste Alternative erfüllt"""
        # Setze Kämpfen auf W6
        self.charakter.fertigkeiten["Kämpfen"].wuerfel.value = 6
        talent = Talent("Test", "Kampf", "A", ["Kämpfen oder Schießen W6"], "", 0, 0)
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        self.assertEqual(len(fehlermeldungen), 0)

    def test_oder_fertigkeit_zweite_erfuellt(self):
        """Test: 'Kämpfen oder Schießen W6' - zweite Alternative erfüllt"""
        # Setze Schießen auf W6
        self.charakter.fertigkeiten["Schießen"].wuerfel.value = 6
        talent = Talent("Test", "Kampf", "A", ["Kämpfen oder Schießen W6"], "", 0, 0)
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        self.assertEqual(len(fehlermeldungen), 0)

    def test_oder_fertigkeit_keine_erfuellt(self):
        """Test: 'Kämpfen oder Schießen W6' - keine Alternative erfüllt"""
        # Beide Fertigkeiten auf W4 (Standard)
        talent = Talent("Test", "Kampf", "A", ["Kämpfen oder Schießen W6"], "", 0, 0)
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        self.assertEqual(len(fehlermeldungen), 1)
        self.assertIn("oder", fehlermeldungen[0])

    def test_oder_athletik_oder_schiessen_w8(self):
        """Test: 'Athletik oder Schießen W8' (Volltreffer/Scharfschütze)"""
        # Setze Athletik auf W8
        self.charakter.fertigkeiten["Athletik"].wuerfel.value = 8
        talent = Talent("Volltreffer", "Kampf", "A", ["Athletik oder Schießen W8"], "", 0, 0)
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        self.assertEqual(len(fehlermeldungen), 0)

    def test_oder_mit_fuer_qualifizierer(self):
        """Test: 'Athletik W8 für Wurfwaffen oder Schießen W8 für Bögen' (Doppelschuss)"""
        # Setze Schießen auf W8
        self.charakter.fertigkeiten["Schießen"].wuerfel.value = 8
        talent = Talent("Doppelschuss", "Kampf", "F",
                        ["Athletik W8 für Wurfwaffen oder Schießen W8 für Bögen"], "", 0, 0)
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        self.assertEqual(len(fehlermeldungen), 0)

    def test_oder_mit_fuer_keine_erfuellt(self):
        """Test: 'Athletik W8 für Wurfwaffen oder Schießen W8 für Bögen' - keine erfüllt"""
        talent = Talent("Doppelschuss", "Kampf", "F",
                        ["Athletik W8 für Wurfwaffen oder Schießen W8 für Bögen"], "", 0, 0)
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        self.assertEqual(len(fehlermeldungen), 1)

    def test_oder_komma_und_oder(self):
        """Test: 'Alchemie, Heilen oder Überleben W6' (Giftmischer)"""
        # Setze Heilen auf W6
        self.charakter.fertigkeiten["Heilen"].wuerfel.value = 6
        talent = Talent("Giftmischer", "Experte", "A",
                        ["Alchemie, Heilen oder Überleben W6"], "", 0, 0)
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        self.assertEqual(len(fehlermeldungen), 0)

    def test_oder_komma_dritte_alternative(self):
        """Test: 'Alchemie, Heilen oder Überleben W6' - dritte Alternative erfüllt"""
        self.charakter.fertigkeiten["Überleben"].wuerfel.value = 6
        talent = Talent("Giftmischer", "Experte", "A",
                        ["Alchemie, Heilen oder Überleben W6"], "", 0, 0)
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        self.assertEqual(len(fehlermeldungen), 0)

    def test_oder_komma_keine_erfuellt(self):
        """Test: 'Alchemie, Heilen oder Überleben W6' - keine Alternative erfüllt"""
        talent = Talent("Giftmischer", "Experte", "A",
                        ["Alchemie, Heilen oder Überleben W6"], "", 0, 0)
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        self.assertEqual(len(fehlermeldungen), 1)

    def test_oder_mit_weiteren_voraussetzungen(self):
        """Test: Oder-Voraussetzung kombiniert mit normaler Voraussetzung"""
        self.charakter.fertigkeiten["Schießen"].wuerfel.value = 6
        talent = Talent("Erzfeind", "Hintergrund", "A",
                        ["Athletik", "Kämpfen oder Schießen W6"], "", 0, 0)
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        # Athletik ist da aber W4 (kein Würfelwert gefordert → Talentvoraussetzung-Fallback),
        # Schießen W6 ist erfüllt
        # "Athletik" wird als Talent gesucht → nicht gefunden → Fehler
        # Aber die oder-Voraussetzung sollte erfüllt sein
        oder_fehler = [f for f in fehlermeldungen if "oder" in f.lower()]
        self.assertEqual(len(oder_fehler), 0)

    def test_oder_ah_alternativen(self):
        """Test: 'AH (Priester) oder AH (Eiferer)' - AH-Alternativen"""
        # Erstelle AH-Talente
        self.charakter.talente["Arkaner Hintergrund (Priester)"] = Talent(
            "Arkaner Hintergrund (Priester)", "Macht", "A", [], "", 3, 10)
        self.charakter.talente["Arkaner Hintergrund (Eiferer)"] = Talent(
            "Arkaner Hintergrund (Eiferer)", "Macht", "A", [], "", 3, 10)

        # Wähle Priester aus
        self.charakter.talente["Arkaner Hintergrund (Priester)"].ausgewaehlt = True

        talent = Talent("Test", "Macht", "A",
                        ["AH (Priester) oder AH (Eiferer)"], "", 0, 0)
        fehlermeldungen = self.manager.pruefe_voraussetzungen(talent)
        self.assertEqual(len(fehlermeldungen), 0)

    def test_bestehende_voraussetzungen_funktionieren_noch(self):
        """Sicherheitstest: Bestehende nicht-oder Voraussetzungen funktionieren weiterhin"""
        # Attribut-Voraussetzung
        talent_attr = Talent("Test", "Kampf", "A", ["GES W8"], "", 0, 0)
        fehler = self.manager.pruefe_voraussetzungen(talent_attr)
        self.assertEqual(len(fehler), 1)

        # Fertigkeit-Voraussetzung
        talent_fert = Talent("Test", "Kampf", "A", ["Kämpfen W8"], "", 0, 0)
        fehler = self.manager.pruefe_voraussetzungen(talent_fert)
        self.assertEqual(len(fehler), 1)

        # Talent-Voraussetzung
        talent_tal = Talent("Test", "Kampf", "A", ["Glück"], "", 0, 0)
        fehler = self.manager.pruefe_voraussetzungen(talent_tal)
        self.assertEqual(len(fehler), 1)


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


class TestZauberbuecherMechanik(unittest.TestCase):
    """Tests für die Zauberbücher-Fantasy-Kompendium-Mechanik"""

    def setUp(self):
        """Setup für jeden Test"""
        self.charakter = MockCharakter()
        self.charakter.active_setting_name = "Fantasy Kompendium"  # Für Fantasy-Kompendium-Kontext
        self.manager = TalentManager(self.charakter)

    def test_zauberbucher_talent_gibt_sofortige_macht(self):
        """Test: Zauberbücher-Talent gibt sofort +1 Macht beim Auswählen"""
        # Vorbedingungen
        initial_maechte = self.charakter.verfuegbare_maechte
        initial_anzahl = self.charakter.anzahl_maechte

        # Debug: Prüfe ob Talent existiert
        self.assertIn("Zauberbücher", self.charakter.talente)

        # Zauberbücher direkt auswählen mit talent_auswaehlen (überspringt Voraussetzungen)
        result = self.manager.talent_auswaehlen("Zauberbücher", skip_prereq_check=True)

        # Debug output bei Fehlschlag
        if not result:
            print(f"Debug: waehle_talent result: {result}")
            print(f"Debug: Talent existiert: {'Zauberbücher' in self.charakter.talente}")
            print(f"Debug: Talent ausgewählt: {self.charakter.talente['Zauberbücher'].ausgewaehlt if 'Zauberbücher' in self.charakter.talente else 'N/A'}")

        # Sollte erfolgreich sein
        self.assertTrue(result)
        self.assertTrue(self.charakter.talente["Zauberbücher"].ausgewaehlt)

        # Sollte +1 sofortige Macht geben
        self.assertEqual(self.charakter.verfuegbare_maechte, initial_maechte + 1)
        self.assertEqual(self.charakter.anzahl_maechte, initial_anzahl + 1)

    def test_neue_maechte_ohne_zauberbucher_gibt_zwei_maechte(self):
        """Test: Neue Mächte ohne Zauberbücher gibt normale 2 Mächte"""
        # Vorbedingungen
        initial_maechte = self.charakter.verfuegbare_maechte
        initial_anzahl = self.charakter.anzahl_maechte

        # Neue Mächte direkt auswählen
        result = self.manager.talent_auswaehlen("Neue Mächte", skip_prereq_check=True)

        # Sollte erfolgreich sein
        self.assertTrue(result)
        self.assertTrue(self.charakter.talente["Neue Mächte"].ausgewaehlt)

        # Sollte normale 2 Mächte geben
        self.assertEqual(self.charakter.verfuegbare_maechte, initial_maechte + 2)
        self.assertEqual(self.charakter.anzahl_maechte, initial_anzahl + 2)

    def test_neue_maechte_mit_zauberbucher_gibt_drei_maechte(self):
        """Test: Neue Mächte mit bereits gewähltem Zauberbücher gibt 3 Mächte"""
        # Zauberbücher zuerst auswählen
        self.manager.talent_auswaehlen("Zauberbücher", skip_prereq_check=True)

        # Vorbedingungen nach Zauberbücher-Auswahl
        initial_maechte = self.charakter.verfuegbare_maechte  # Sollte bereits +1 haben
        initial_anzahl = self.charakter.anzahl_maechte

        # Neue Mächte auswählen
        result = self.manager.talent_auswaehlen("Neue Mächte", skip_prereq_check=True)

        # Sollte erfolgreich sein
        self.assertTrue(result)
        self.assertTrue(self.charakter.talente["Neue Mächte"].ausgewaehlt)

        # Sollte 3 statt 2 Mächte geben (Zauberbücher-Bonus)
        self.assertEqual(self.charakter.verfuegbare_maechte, initial_maechte + 3)
        self.assertEqual(self.charakter.anzahl_maechte, initial_anzahl + 3)

    def test_zauberbucher_abwahl_entfernt_sofortige_macht(self):
        """Test: Zauberbücher-Abwahl entfernt die sofortige Macht"""
        # Zauberbücher auswählen
        self.manager.talent_auswaehlen("Zauberbücher", skip_prereq_check=True)

        # Vorbedingungen nach Auswahl
        initial_maechte = self.charakter.verfuegbare_maechte
        initial_anzahl = self.charakter.anzahl_maechte

        # Zauberbücher abwählen
        result = self.manager.talent_abwaehlen("Zauberbücher")

        # Sollte erfolgreich sein
        self.assertTrue(result)
        self.assertFalse(self.charakter.talente["Zauberbücher"].ausgewaehlt)

        # Sollte sofortige Macht entfernen (-1 Macht)
        self.assertEqual(self.charakter.verfuegbare_maechte, initial_maechte - 1)
        self.assertEqual(self.charakter.anzahl_maechte, initial_anzahl - 1)

    def test_neue_maechte_abwahl_mit_zauberbucher_entfernt_drei_maechte(self):
        """Test: Neue Mächte-Abwahl mit Zauberbücher entfernt 3 Mächte"""
        # Beide Talente auswählen
        self.manager.talent_auswaehlen("Zauberbücher", skip_prereq_check=True)
        self.manager.talent_auswaehlen("Neue Mächte", skip_prereq_check=True)

        # Vorbedingungen nach Auswahl beider Talente
        initial_maechte = self.charakter.verfuegbare_maechte  # Sollte +1 (Zauberbücher) + 3 (Neue Mächte mit Bonus) haben
        initial_anzahl = self.charakter.anzahl_maechte

        # Neue Mächte abwählen
        result = self.manager.talent_abwaehlen("Neue Mächte")

        # Sollte erfolgreich sein
        self.assertTrue(result)
        self.assertFalse(self.charakter.talente["Neue Mächte"].ausgewaehlt)

        # Sollte 3 Mächte entfernen (wegen Zauberbücher-Bonus)
        self.assertEqual(self.charakter.verfuegbare_maechte, initial_maechte - 3)
        self.assertEqual(self.charakter.anzahl_maechte, initial_anzahl - 3)

    def test_reihenfolge_neue_maechte_vor_zauberbucher(self):
        """Test: Neue Mächte vor Zauberbücher - kein Bonus beim ersten Mal"""
        # Neue Mächte zuerst auswählen (ohne Zauberbücher)
        self.manager.talent_auswaehlen("Neue Mächte", skip_prereq_check=True)
        initial_maechte_nach_neue = self.charakter.verfuegbare_maechte  # Sollte +2 haben

        # Zauberbücher danach auswählen
        self.manager.talent_auswaehlen("Zauberbücher", skip_prereq_check=True)

        # Sollte nur +1 sofortige Macht von Zauberbücher hinzufügen (kein rückwirkender Bonus)
        self.assertEqual(self.charakter.verfuegbare_maechte, initial_maechte_nach_neue + 1)

        # Neue Mächte ein zweites Mal auswählen (sollte jetzt mit Bonus sein)
        if "Neue Mächte_2" not in self.charakter.talente:
            # Erstelle neue Instanz für Mehrfachauswahl
            neue_instanz = Talent(
                name="Neue Mächte",
                kategorie="Macht",
                rang="A",
                voraussetzungen=["AH"],
                beschreibung="Dein Charakter kennt zwei neue Mächte.",
                neue_maechte=2,
                machtpunkte=0
            )
            self.charakter.talente["Neue Mächte_2"] = neue_instanz

        initial_vor_zweite_auswahl = self.charakter.verfuegbare_maechte
        result_2 = self.manager.talent_auswaehlen("Neue Mächte_2", skip_prereq_check=True)

        # Debug bei fehlenden Zauberbücher-Bonus
        if not result_2:
            print(f"Debug: Neue Mächte_2 Auswahl fehlgeschlagen")

        # Sollte jetzt 3 Mächte hinzufügen (mit Zauberbücher-Bonus)
        # Da Zauberbücher schon aktiv ist, bekommt auch die zweite Instanz den Bonus
        self.assertEqual(self.charakter.verfuegbare_maechte, initial_vor_zweite_auswahl + 3)

    def test_hat_zauberbucher_talent_hilfsfunktion(self):
        """Test: _hat_zauberbucher_talent() Hilfsfunktion"""
        # Initial sollte false sein
        self.assertFalse(self.manager._hat_zauberbucher_talent())

        # Nach Auswahl sollte true sein
        self.manager.talent_auswaehlen("Zauberbücher", skip_prereq_check=True)
        self.assertTrue(self.manager._hat_zauberbucher_talent())

        # Nach Abwahl sollte wieder false sein
        self.manager.talent_abwaehlen("Zauberbücher")
        self.assertFalse(self.manager._hat_zauberbucher_talent())

    def test_gesamtbilanz_zauberbucher_und_neue_maechte(self):
        """Test: Gesamtbilanz bei Auswahl beider Talente"""
        # Ausgangssituation
        self.assertEqual(self.charakter.verfuegbare_maechte, 0)
        self.assertEqual(self.charakter.anzahl_maechte, 0)

        # Zauberbücher auswählen
        self.manager.talent_auswaehlen("Zauberbücher", skip_prereq_check=True)
        self.assertEqual(self.charakter.verfuegbare_maechte, 1)  # +1 sofortige Macht

        # Neue Mächte auswählen
        self.manager.talent_auswaehlen("Neue Mächte", skip_prereq_check=True)
        self.assertEqual(self.charakter.verfuegbare_maechte, 4)  # +1 (Zauberbücher) + 3 (Neue Mächte mit Bonus)
        self.assertEqual(self.charakter.anzahl_maechte, 4)

        # Neue Mächte abwählen
        self.manager.talent_abwaehlen("Neue Mächte")
        self.assertEqual(self.charakter.verfuegbare_maechte, 1)  # Nur noch Zauberbücher-Macht

        # Zauberbücher abwählen
        self.manager.talent_abwaehlen("Zauberbücher")
        self.assertEqual(self.charakter.verfuegbare_maechte, 0)  # Zurück auf Ausgangssituation
        self.assertEqual(self.charakter.anzahl_maechte, 0)


def run_talent_manager_tests():
    """Führt alle TalentManager Tests aus"""
    print("="*60)
    print("TALENT MANAGER UNIT TESTS")
    print("="*60)
    
    # Erstelle Test-Suite
    suite = unittest.TestSuite()
    
    # Füge alle Test-Klassen hinzu
    suite.addTest(unittest.makeSuite(TestTalentManager))
    suite.addTest(unittest.makeSuite(TestOderVoraussetzungen))
    suite.addTest(unittest.makeSuite(TestTalentManagerCompatibility))
    suite.addTest(unittest.makeSuite(TestTalentConfigIntegration))
    suite.addTest(unittest.makeSuite(TestZauberbuecherMechanik))
    
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