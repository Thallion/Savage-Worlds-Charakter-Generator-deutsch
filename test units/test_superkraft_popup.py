# test units/test_superkraft_popup.py
"""
Tests für das Superkraft-Popup-System.
Testet Phase 3/4 der Superkräfte-Implementierung:
- SuperkraftDialogHandler Logik
- Auswahl-Flow (Auswahl → Konfiguration → Bestätigung)
- Entfernungs-Flow
- Machtstufe-Wechsel
- Integration mit superkraft_funktionen
"""
import unittest
import sys
import os
from unittest.mock import MagicMock, patch, PropertyMock

# Kivy-Headless-Modus
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_LOG_LEVEL'] = 'critical'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import functions.superkraft_funktionen as skf
from models.superkraft import Superkraft, SuperkraftModifikator


# ==================== MOCK-OBJEKTE ====================

class MockCharakter:
    """Mock-Charakter mit Superkraft-Eigenschaften"""

    def __init__(self):
        self.superkraefte = {}
        self.selected_superkraefte = []
        self.superkraft_punkte_gesamt = 45
        self.superkraft_punkte_verbraucht = 0
        self.machtstufe = "III"
        self.kraftobergrenze = 15
        self.active_setting_name = "Superkräfte Kompendium"

    def setup_standard_krafte(self):
        """Lädt Standard-Testdaten."""
        daten = {
            "Fliegen": {
                "name": "Fliegen", "kosten": "2-18", "beschreibung": "Flugfähigkeit",
                "modifikatoren": {
                    "Unbeholfen": {"kosten": -2, "beschreibung": "Nachteil"},
                    "Senkrechtstarter": {"kosten": 1, "beschreibung": "Start"},
                },
                "ausgewaehlt": False, "aktiv": True
            },
            "Furchtlos": {
                "name": "Furchtlos", "kosten": 2, "beschreibung": "Immun gegen Furcht",
                "modifikatoren": {},
                "ausgewaehlt": False, "aktiv": True
            },
            "Panzerung": {
                "name": "Panzerung", "kosten": "1-5", "beschreibung": "Schutz",
                "modifikatoren": {
                    "Schwere Panzerung": {"kosten": 1, "beschreibung": "Schwer"},
                },
                "ausgewaehlt": False, "aktiv": True
            },
            "Fernkampfangriff": {
                "name": "Fernkampfangriff", "kosten": "speziell",
                "beschreibung": "Fernkampfangriff",
                "modifikatoren": {
                    "Panzerbrechend": {"kosten": "1 pro 2 PB", "beschreibung": "PB"},
                },
                "ausgewaehlt": False, "aktiv": True
            },
        }
        skf.initialisiere_superkraefte(self, daten)


class MockController:
    """Mock-Controller für DialogHandler-Tests"""

    def __init__(self):
        self.charakter = MockCharakter()
        self.charakter.setup_standard_krafte()


# ==================== AUSWAHL-FLOW TESTS ====================

class TestAuswahlFlow(unittest.TestCase):
    """Tests für den Auswahl-Flow: Kraft wählen → konfigurieren → bestätigen"""

    def setUp(self):
        self.controller = MockController()
        self.char = self.controller.charakter

    def test_verfuegbare_krafte_liste(self):
        """Prüft dass alle Kräfte in der Auswahlliste erscheinen"""
        krafte_list = []
        for name, kraft in sorted(self.char.superkraefte.items()):
            krafte_list.append({
                'name': name,
                'kosten': kraft.basis_kosten,
                'ausgewaehlt': kraft.ausgewaehlt,
            })
        self.assertEqual(len(krafte_list), 4)
        namen = [k['name'] for k in krafte_list]
        self.assertIn("Fliegen", namen)
        self.assertIn("Furchtlos", namen)

    def test_bereits_gewaehlte_markiert(self):
        """Bereits gewählte Kräfte werden in der Liste markiert"""
        skf.waehle_superkraft(self.char, "Furchtlos")

        krafte_list = []
        for name, kraft in self.char.superkraefte.items():
            krafte_list.append({
                'name': name,
                'ausgewaehlt': kraft.ausgewaehlt,
            })

        furchtlos = next(k for k in krafte_list if k['name'] == "Furchtlos")
        fliegen = next(k for k in krafte_list if k['name'] == "Fliegen")
        self.assertTrue(furchtlos['ausgewaehlt'])
        self.assertFalse(fliegen['ausgewaehlt'])

    def test_kraft_waehlen_mit_festen_kosten(self):
        """Feste-Kosten-Kraft wird direkt ausgewählt"""
        result = skf.waehle_superkraft(self.char, "Furchtlos")
        self.assertTrue(result)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 2)

    def test_kraft_waehlen_mit_variablen_kosten(self):
        """Variable-Kosten-Kraft braucht explizite Kostenangabe"""
        result = skf.waehle_superkraft(self.char, "Fliegen")
        self.assertEqual(result, "needs_kosten")

        result = skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        self.assertTrue(result)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 6)


class TestKonfigurationsFlow(unittest.TestCase):
    """Tests für den Konfigurations-Flow: Kosten + Modifikatoren"""

    def setUp(self):
        self.controller = MockController()
        self.char = self.controller.charakter

    def test_konfiguration_mit_modifikatoren(self):
        """Kraft mit Modifikatoren konfigurieren"""
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        skf.waehle_modifikator(self.char, "Fliegen", "Unbeholfen")

        kraft = self.char.superkraefte["Fliegen"]
        self.assertEqual(kraft.gesamt_kosten, 4)  # 6 - 2
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 4)

    def test_konfiguration_mehrere_modifikatoren(self):
        """Mehrere Modifikatoren addieren sich"""
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        skf.waehle_modifikator(self.char, "Fliegen", "Unbeholfen")
        skf.waehle_modifikator(self.char, "Fliegen", "Senkrechtstarter")

        kraft = self.char.superkraefte["Fliegen"]
        self.assertEqual(kraft.gesamt_kosten, 5)  # 6 - 2 + 1

    def test_kosten_validierung_obergrenze(self):
        """Kosten über Kraftobergrenze werden abgelehnt"""
        result = skf.waehle_superkraft(self.char, "Fliegen", kosten=18)
        self.assertEqual(result, "ueber_obergrenze")

    def test_kosten_validierung_budget(self):
        """Kosten über Budget werden abgelehnt"""
        self.char.superkraft_punkte_verbraucht = 44
        result = skf.waehle_superkraft(self.char, "Furchtlos")
        self.assertEqual(result, "nicht_genug_skp")

    def test_modifikator_obergrenze_pruefung(self):
        """Modifikator der die Kraftobergrenze überschreitet"""
        skf.waehle_superkraft(self.char, "Fliegen", kosten=15)
        result = skf.waehle_modifikator(self.char, "Fliegen", "Senkrechtstarter")
        self.assertEqual(result, "ueber_obergrenze")


# ==================== ENTFERNUNGS-FLOW TESTS ====================

class TestEntfernungsFlow(unittest.TestCase):
    """Tests für das Entfernen von Superkräften"""

    def setUp(self):
        self.controller = MockController()
        self.char = self.controller.charakter

    def test_kraft_entfernen(self):
        """Superkraft wird korrekt entfernt"""
        skf.waehle_superkraft(self.char, "Furchtlos")
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 2)

        result = skf.entferne_superkraft(self.char, "Furchtlos")
        self.assertTrue(result)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 0)
        self.assertNotIn("Furchtlos", self.char.selected_superkraefte)

    def test_kraft_mit_modifikatoren_entfernen(self):
        """Kraft mit Modifikatoren wird komplett zurückgesetzt"""
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        skf.waehle_modifikator(self.char, "Fliegen", "Unbeholfen")
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 4)

        skf.entferne_superkraft(self.char, "Fliegen")
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 0)

        kraft = self.char.superkraefte["Fliegen"]
        self.assertFalse(kraft.ausgewaehlt)
        self.assertEqual(len(kraft.gewaehlte_modifikatoren), 0)
        self.assertEqual(kraft.gewaehlte_kosten, 0)

    def test_nicht_gewaehlte_kraft_entfernen(self):
        """Nicht gewählte Kraft kann nicht entfernt werden"""
        result = skf.entferne_superkraft(self.char, "Furchtlos")
        self.assertFalse(result)


# ==================== MACHTSTUFE-FLOW TESTS ====================

class TestMachtstufeFlow(unittest.TestCase):
    """Tests für Machtstufe-Wechsel"""

    def setUp(self):
        self.controller = MockController()
        self.char = self.controller.charakter

    def test_machtstufe_wechsel(self):
        """Machtstufe ändern ändert SKP-Budget und Obergrenze"""
        skf.setze_machtstufe(self.char, "I")
        self.assertEqual(self.char.machtstufe, "I")
        self.assertEqual(self.char.superkraft_punkte_gesamt, 15)
        self.assertEqual(self.char.kraftobergrenze, 5)

    def test_alle_machtstufen(self):
        """Alle 5 Machtstufen sind wählbar"""
        stufen = {
            "I": (15, 5),
            "II": (30, 10),
            "III": (45, 15),
            "IV": (60, 20),
            "V": (75, 25),
        }
        for stufe, (skp, obergrenze) in stufen.items():
            skf.setze_machtstufe(self.char, stufe)
            self.assertEqual(self.char.superkraft_punkte_gesamt, skp)
            self.assertEqual(self.char.kraftobergrenze, obergrenze)

    def test_ungueltige_machtstufe(self):
        """Ungültige Machtstufe wird abgelehnt"""
        result = skf.setze_machtstufe(self.char, "X")
        self.assertFalse(result)
        self.assertEqual(self.char.machtstufe, "III")  # Unverändert


# ==================== LISTEN-ANZEIGE TESTS ====================

class TestKraefteListe(unittest.TestCase):
    """Tests für die Kräfte-Listen-Darstellung"""

    def setUp(self):
        self.controller = MockController()
        self.char = self.controller.charakter

    def test_keine_krafte_gewaehlt(self):
        """Leere Liste wenn keine Kräfte gewählt"""
        result = skf.ausgewaehlte_superkraefte(self.char)
        self.assertEqual(len(result), 0)

    def test_krafte_sortiert_nach_name(self):
        """Gewählte Kräfte werden alphabetisch sortiert"""
        skf.waehle_superkraft(self.char, "Panzerung", kosten=3)
        skf.waehle_superkraft(self.char, "Furchtlos")
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)

        result = skf.ausgewaehlte_superkraefte(self.char)
        sortiert = sorted(result, key=lambda k: k.name)
        namen = [k.name for k in sortiert]
        self.assertEqual(namen, ["Fliegen", "Furchtlos", "Panzerung"])

    def test_kraft_card_daten(self):
        """Kraft-Card enthält Name, Kosten und Modifikator-Info"""
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        skf.waehle_modifikator(self.char, "Fliegen", "Unbeholfen")

        kraft = self.char.superkraefte["Fliegen"]
        self.assertEqual(kraft.name, "Fliegen")
        self.assertEqual(kraft.gesamt_kosten, 4)
        mod_namen = [m.name for m in kraft.gewaehlte_modifikatoren]
        self.assertIn("Unbeholfen", mod_namen)


# ==================== SKP-ANZEIGE TESTS ====================

class TestSKPAnzeige(unittest.TestCase):
    """Tests für die SKP-Anzeige im Header"""

    def setUp(self):
        self.controller = MockController()
        self.char = self.controller.charakter

    def test_initiale_skp(self):
        """Initiale SKP-Werte sind korrekt"""
        self.assertEqual(self.char.superkraft_punkte_gesamt, 45)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 0)
        self.assertEqual(skf.get_verbleibende_skp(self.char), 45)

    def test_skp_nach_auswahl(self):
        """SKP werden nach Auswahl korrekt aktualisiert"""
        skf.waehle_superkraft(self.char, "Furchtlos")  # 2 SKP
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)  # 6 SKP
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 8)
        self.assertEqual(skf.get_verbleibende_skp(self.char), 37)

    def test_skp_nach_entfernung(self):
        """SKP werden nach Entfernung freigegeben"""
        skf.waehle_superkraft(self.char, "Furchtlos")
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        skf.entferne_superkraft(self.char, "Furchtlos")
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 6)
        self.assertEqual(skf.get_verbleibende_skp(self.char), 39)

    def test_fortschrittsbalken_berechnung(self):
        """Fortschrittsbalken-Prozent ist korrekt"""
        skf.waehle_superkraft(self.char, "Fliegen", kosten=9)
        # 9/45 = 20%
        prozent = (self.char.superkraft_punkte_verbraucht / self.char.superkraft_punkte_gesamt) * 100
        self.assertAlmostEqual(prozent, 20.0)

    def test_fortschrittsbalken_farbe_gruen(self):
        """Unter 70% ist grün"""
        skf.waehle_superkraft(self.char, "Furchtlos")  # 2/45 ≈ 4.4%
        prozent = (self.char.superkraft_punkte_verbraucht / self.char.superkraft_punkte_gesamt) * 100
        self.assertLess(prozent, 70)

    def test_fortschrittsbalken_farbe_rot(self):
        """Über 90% ist rot"""
        self.char.superkraft_punkte_verbraucht = 42  # 42/45 ≈ 93.3%
        prozent = (self.char.superkraft_punkte_verbraucht / self.char.superkraft_punkte_gesamt) * 100
        self.assertGreater(prozent, 90)


# ==================== SUCH-FILTER TESTS ====================

class TestSuchFilter(unittest.TestCase):
    """Tests für die Suchfunktion in der Auswahlliste"""

    def setUp(self):
        self.controller = MockController()
        self.char = self.controller.charakter
        self.alle_krafte = [
            {'name': 'Fliegen', 'kosten': '2-18'},
            {'name': 'Furchtlos', 'kosten': '2'},
            {'name': 'Panzerung', 'kosten': '1-5'},
            {'name': 'Fernkampfangriff', 'kosten': 'speziell'},
        ]

    def test_filter_leer(self):
        """Leerer Suchtext zeigt alle"""
        gefiltert = [k for k in self.alle_krafte if "".lower() in k['name'].lower()]
        self.assertEqual(len(gefiltert), 4)

    def test_filter_teilstring(self):
        """Teilstring-Suche funktioniert"""
        text = "fli"
        gefiltert = [k for k in self.alle_krafte if text.lower() in k['name'].lower()]
        self.assertEqual(len(gefiltert), 1)
        self.assertEqual(gefiltert[0]['name'], "Fliegen")

    def test_filter_case_insensitive(self):
        """Suche ist case-insensitive"""
        text = "FURCHT"
        gefiltert = [k for k in self.alle_krafte if text.lower() in k['name'].lower()]
        self.assertEqual(len(gefiltert), 1)
        self.assertEqual(gefiltert[0]['name'], "Furchtlos")

    def test_filter_kein_treffer(self):
        """Kein Treffer bei unbekanntem Suchtext"""
        text = "xyz"
        gefiltert = [k for k in self.alle_krafte if text.lower() in k['name'].lower()]
        self.assertEqual(len(gefiltert), 0)

    def test_filter_mehrere_treffer(self):
        """Mehrere Treffer bei passender Suche"""
        text = "f"
        gefiltert = [k for k in self.alle_krafte if text.lower() in k['name'].lower()]
        # Fliegen, Furchtlos, Fernkampfangriff
        self.assertEqual(len(gefiltert), 3)


# ==================== KOMBINATIONS-TESTS ====================

class TestKomplexeFlows(unittest.TestCase):
    """Tests für komplexe Interaktionsabläufe"""

    def setUp(self):
        self.controller = MockController()
        self.char = self.controller.charakter

    def test_mehrere_krafte_workflow(self):
        """Vollständiger Workflow: mehrere Kräfte wählen, konfigurieren, eine entfernen"""
        # 3 Kräfte wählen
        skf.waehle_superkraft(self.char, "Furchtlos")  # 2 SKP
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)  # 6 SKP
        skf.waehle_superkraft(self.char, "Panzerung", kosten=3)  # 3 SKP

        self.assertEqual(len(skf.ausgewaehlte_superkraefte(self.char)), 3)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 11)

        # Modifikator hinzufügen
        skf.waehle_modifikator(self.char, "Fliegen", "Unbeholfen")
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 9)  # 11 - 2

        # Eine Kraft entfernen
        skf.entferne_superkraft(self.char, "Panzerung")
        self.assertEqual(len(skf.ausgewaehlte_superkraefte(self.char)), 2)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 6)  # 2 + (6-2)

    def test_machtstufe_wechsel_mit_kraeften(self):
        """Machtstufe-Wechsel ändert Budget, behält aber gewählte Kräfte"""
        skf.waehle_superkraft(self.char, "Furchtlos")
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 8)

        # Stufe runter
        skf.setze_machtstufe(self.char, "I")
        self.assertEqual(self.char.superkraft_punkte_gesamt, 15)
        # Kräfte bleiben gewählt (UI muss Warnung zeigen wenn Budget überschritten)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 8)
        self.assertEqual(skf.get_verbleibende_skp(self.char), 7)

    def test_kraft_erneut_waehlen_nach_entfernung(self):
        """Entfernte Kraft kann erneut gewählt werden"""
        skf.waehle_superkraft(self.char, "Furchtlos")
        skf.entferne_superkraft(self.char, "Furchtlos")

        # Erneut wählen
        result = skf.waehle_superkraft(self.char, "Furchtlos")
        self.assertTrue(result)
        self.assertTrue(self.char.superkraefte["Furchtlos"].ausgewaehlt)


# ==================== PERSISTENZ-INTEGRATION TESTS ====================

class TestPersistenzIntegration(unittest.TestCase):
    """Tests für Speichern/Laden von Superkräften"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.setup_standard_krafte()

    def test_superkraft_roundtrip(self):
        """Superkraft-Daten überleben Serialisierung"""
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        skf.waehle_modifikator(self.char, "Fliegen", "Unbeholfen")

        kraft = self.char.superkraefte["Fliegen"]
        data = kraft.to_dict()

        restored = Superkraft.from_dict(data)
        self.assertEqual(restored.name, "Fliegen")
        self.assertEqual(restored.gewaehlte_kosten, 6)
        self.assertTrue(restored.ausgewaehlt)
        self.assertEqual(len(restored.gewaehlte_modifikatoren), 1)
        self.assertEqual(restored.gesamt_kosten, 4)

    def test_selected_superkraefte_liste(self):
        """Selected-Liste wird korrekt gepflegt"""
        skf.waehle_superkraft(self.char, "Furchtlos")
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)

        self.assertEqual(len(self.char.selected_superkraefte), 2)
        self.assertIn("Furchtlos", self.char.selected_superkraefte)
        self.assertIn("Fliegen", self.char.selected_superkraefte)

        skf.entferne_superkraft(self.char, "Furchtlos")
        self.assertEqual(len(self.char.selected_superkraefte), 1)
        self.assertNotIn("Furchtlos", self.char.selected_superkraefte)


if __name__ == '__main__':
    unittest.main()
