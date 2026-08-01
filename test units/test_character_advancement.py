"""
Charakterisierungstests für functions/character_advancement.py

Schreibt das IST-Verhalten von Rang-Berechnung, Attribut-Steigern/-Senken,
Aufstiegs-Verwaltung und Startkapital-Erhöhung fest.

Bewusst festgeschriebene Quirks (Ist-Verhalten, nicht "korrigieren"):
- steigere_attribut zieht den Punkt ab, BEVOR das Attribut geprüft wird –
  bei unbekanntem Attribut ist der Punkt trotzdem weg.
- senke_attribut gibt auf den Erfolgspfaden None zurück (nicht True).
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Pfad zur Projektroot hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.character_advancement import (
    update_rang,
    get_rang,
    steigere_attribut,
    senke_attribut,
    increase_aufstiege,
    decrease_aufstiege,
    erhoehe_startkapital,
    senke_startkapital,
)

# Identisch zu models/charakter.py
RANG_MAPPING = [
    (0, 4, "Anfänger", 1),
    (4, 8, "Fortgeschritten", 2),
    (8, 12, "Veteran", 3),
    (12, 16, "Heroisch", 4),
    (16, 100, "Legendär", 5),
]


class FakeWuerfel:
    def __init__(self, value=4, modifier=0):
        self.value = value
        self.modifier = modifier
        self.increase_aufrufe = 0
        self.decrease_aufrufe = 0

    def increase(self):
        self.increase_aufrufe += 1
        self.value = min(12, self.value + 2)

    def decrease(self):
        self.decrease_aufrufe += 1
        self.value = max(4, self.value - 2)


class FakeAttribut:
    def __init__(self):
        self.wuerfel = FakeWuerfel()


class FakeCharakter:
    def __init__(self):
        self.rang_mapping = list(RANG_MAPPING)
        self.rang = "Anfänger"
        self.aufstiege_gesamt = 0
        self.verbleibende_aufstiege = 0
        self.verbleibende_attributsteigerungen = 5
        self.maximale_attributsteigerungen = 5
        self.verbleibende_handicap_punkte = 0
        self.gesamt_handicap_punkte = 4
        self.char_gen_completed = False
        self.vermoegen = 0
        self.startgeld_einloesungen = 0
        self.attribute = {'Stärke': FakeAttribut()}
        self.update_char_gen_status = Mock()


class CharacterAdvancementTestBasis(unittest.TestCase):
    """Gemeinsamer Logger-Patch für alle Tests"""

    def setUp(self):
        patcher = patch('functions.character_advancement.Logger')
        self.mock_logger = patcher.start()
        self.addCleanup(patcher.stop)


class TestRangBerechnung(CharacterAdvancementTestBasis):

    def test_get_rang_grenzwerte(self):
        """Rang-Grenzen: 0-3 Anfänger, 4-7 Fortgeschritten, 8-11 Veteran, ..."""
        charakter = FakeCharakter()
        faelle = [
            (0, "Anfänger"), (3, "Anfänger"),
            (4, "Fortgeschritten"), (7, "Fortgeschritten"),
            (8, "Veteran"), (11, "Veteran"),
            (12, "Heroisch"), (15, "Heroisch"),
            (16, "Legendär"), (99, "Legendär"),
        ]
        for ausgegeben, erwartet in faelle:
            with self.subTest(ausgegebene_aufstiege=ausgegeben):
                self.assertEqual(get_rang(charakter, ausgegeben), erwartet)

    def test_get_rang_ausserhalb_mapping(self):
        """Werte außerhalb des Mappings → 'Unbekannter Rang'"""
        charakter = FakeCharakter()
        self.assertEqual(get_rang(charakter, -1), "Unbekannter Rang")
        self.assertEqual(get_rang(charakter, 100), "Unbekannter Rang")

    def test_update_rang_nutzt_ausgegebene_aufstiege(self):
        """Rang basiert auf aufstiege_gesamt - verbleibende_aufstiege"""
        charakter = FakeCharakter()
        charakter.aufstiege_gesamt = 5
        charakter.verbleibende_aufstiege = 1
        update_rang(charakter)
        self.assertEqual(charakter.rang, "Fortgeschritten")


class TestSteigereAttribut(CharacterAdvancementTestBasis):

    def test_nach_chargen_mit_aufstieg(self):
        """Nach CharGen: kostet 1 Aufstieg, Würfel wird erhöht"""
        charakter = FakeCharakter()
        charakter.char_gen_completed = True
        charakter.aufstiege_gesamt = 2
        charakter.verbleibende_aufstiege = 2
        ergebnis = steigere_attribut(charakter, 'Stärke')
        self.assertTrue(ergebnis)
        self.assertEqual(charakter.verbleibende_aufstiege, 1)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.increase_aufrufe, 1)
        charakter.update_char_gen_status.assert_called_once()
        # Rang wird mitgepflegt: 2 gesamt - 1 verbleibend = 1 ausgegeben
        self.assertEqual(charakter.rang, "Anfänger")

    def test_nach_chargen_ohne_aufstieg(self):
        """Nach CharGen ohne verbleibende Aufstiege → False, keine Steigerung"""
        charakter = FakeCharakter()
        charakter.char_gen_completed = True
        charakter.verbleibende_aufstiege = 0
        ergebnis = steigere_attribut(charakter, 'Stärke')
        self.assertFalse(ergebnis)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.increase_aufrufe, 0)

    def test_waehrend_chargen_mit_attributpunkt(self):
        """Während CharGen: kostet 1 Attributsteigerung"""
        charakter = FakeCharakter()
        charakter.verbleibende_attributsteigerungen = 1
        ergebnis = steigere_attribut(charakter, 'Stärke')
        self.assertTrue(ergebnis)
        self.assertEqual(charakter.verbleibende_attributsteigerungen, 0)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.increase_aufrufe, 1)

    def test_waehrend_chargen_handicap_punkte_fallback(self):
        """Keine Attributpunkte, aber >1.5 Handicap-Punkte → kostet 2 HP"""
        charakter = FakeCharakter()
        charakter.verbleibende_attributsteigerungen = 0
        charakter.verbleibende_handicap_punkte = 2
        ergebnis = steigere_attribut(charakter, 'Stärke')
        self.assertTrue(ergebnis)
        self.assertEqual(charakter.verbleibende_handicap_punkte, 0)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.increase_aufrufe, 1)

    def test_waehrend_chargen_zu_wenige_handicap_punkte(self):
        """Keine Attributpunkte und nur 1 HP (≤1.5) → False"""
        charakter = FakeCharakter()
        charakter.verbleibende_attributsteigerungen = 0
        charakter.verbleibende_handicap_punkte = 1
        ergebnis = steigere_attribut(charakter, 'Stärke')
        self.assertFalse(ergebnis)
        self.assertEqual(charakter.verbleibende_handicap_punkte, 1)

    def test_unbekanntes_attribut_punkt_trotzdem_weg(self):
        """QUIRK (Ist-Verhalten): Punkt wird VOR der Attribut-Prüfung abgezogen"""
        charakter = FakeCharakter()
        charakter.verbleibende_attributsteigerungen = 1
        ergebnis = steigere_attribut(charakter, 'GibtEsNicht')
        self.assertFalse(ergebnis)
        self.assertEqual(charakter.verbleibende_attributsteigerungen, 0)


class TestSenkeAttribut(CharacterAdvancementTestBasis):

    def test_nach_chargen_gibt_aufstieg_zurueck(self):
        """Nach CharGen: verbleibende_aufstiege +1, Würfel gesenkt, Rückgabe None (Quirk)"""
        charakter = FakeCharakter()
        charakter.char_gen_completed = True
        charakter.aufstiege_gesamt = 3
        charakter.verbleibende_aufstiege = 1
        ergebnis = senke_attribut(charakter, 'Stärke')
        self.assertIsNone(ergebnis)
        self.assertEqual(charakter.verbleibende_aufstiege, 2)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.decrease_aufrufe, 1)

    def test_nach_chargen_maximum_erreicht(self):
        """verbleibende == gesamt → False, keine Senkung"""
        charakter = FakeCharakter()
        charakter.char_gen_completed = True
        charakter.aufstiege_gesamt = 2
        charakter.verbleibende_aufstiege = 2
        ergebnis = senke_attribut(charakter, 'Stärke')
        self.assertFalse(ergebnis)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.decrease_aufrufe, 0)

    def test_waehrend_chargen_handicap_punkte_zuerst(self):
        """Während CharGen: zuerst werden Handicap-Punkte zurückgegeben"""
        charakter = FakeCharakter()
        charakter.verbleibende_handicap_punkte = 2
        charakter.gesamt_handicap_punkte = 4
        ergebnis = senke_attribut(charakter, 'Stärke')
        self.assertIsNone(ergebnis)
        self.assertEqual(charakter.verbleibende_handicap_punkte, 3)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.decrease_aufrufe, 1)

    def test_waehrend_chargen_dann_attributpunkte(self):
        """HP voll → Attributsteigerung wird zurückgegeben"""
        charakter = FakeCharakter()
        charakter.verbleibende_handicap_punkte = 4
        charakter.gesamt_handicap_punkte = 4
        charakter.verbleibende_attributsteigerungen = 3
        charakter.maximale_attributsteigerungen = 5
        ergebnis = senke_attribut(charakter, 'Stärke')
        self.assertIsNone(ergebnis)
        self.assertEqual(charakter.verbleibende_attributsteigerungen, 4)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.decrease_aufrufe, 1)

    def test_waehrend_chargen_alles_maximal(self):
        """HP und Attributpunkte voll → False"""
        charakter = FakeCharakter()
        charakter.verbleibende_handicap_punkte = 4
        charakter.gesamt_handicap_punkte = 4
        charakter.verbleibende_attributsteigerungen = 5
        charakter.maximale_attributsteigerungen = 5
        ergebnis = senke_attribut(charakter, 'Stärke')
        self.assertFalse(ergebnis)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.decrease_aufrufe, 0)


class TestAufstiegsVerwaltung(CharacterAdvancementTestBasis):

    def test_increase_aufstiege(self):
        """+1 gesamt und +1 verbleibend, Rang bleibt bei 0 ausgegebenen"""
        charakter = FakeCharakter()
        increase_aufstiege(charakter)
        self.assertEqual(charakter.aufstiege_gesamt, 1)
        self.assertEqual(charakter.verbleibende_aufstiege, 1)
        self.assertEqual(charakter.rang, "Anfänger")

    def test_rang_steigt_erst_nach_ausgeben(self):
        """4 Aufstiege erhalten = weiter Anfänger; erst Ausgeben erhöht den Rang"""
        charakter = FakeCharakter()
        for _ in range(4):
            increase_aufstiege(charakter)
        self.assertEqual(charakter.rang, "Anfänger")
        # 4 Aufstiege ausgeben
        charakter.char_gen_completed = True
        for _ in range(4):
            steigere_attribut(charakter, 'Stärke')
        self.assertEqual(charakter.rang, "Fortgeschritten")

    def test_decrease_aufstiege(self):
        """-1 gesamt und -1 verbleibend"""
        charakter = FakeCharakter()
        charakter.aufstiege_gesamt = 2
        charakter.verbleibende_aufstiege = 1
        decrease_aufstiege(charakter)
        self.assertEqual(charakter.aufstiege_gesamt, 1)
        self.assertEqual(charakter.verbleibende_aufstiege, 0)

    def test_decrease_aufstiege_clamping(self):
        """Werte fallen nie unter 0"""
        charakter = FakeCharakter()
        decrease_aufstiege(charakter)
        self.assertEqual(charakter.aufstiege_gesamt, 0)
        self.assertEqual(charakter.verbleibende_aufstiege, 0)


class TestStartkapital(CharacterAdvancementTestBasis):

    def test_erhoehe_mit_setting_startgeld(self):
        """Setting-spezifisches Startgeld wird verwendet, kostet 1 HP"""
        charakter = FakeCharakter()
        charakter.verbleibende_handicap_punkte = 1
        charakter.custom_element_manager = Mock()
        charakter.custom_element_manager.get_active_setting.return_value = {'startgeld': 250}
        erhoehe_startkapital(charakter)
        self.assertEqual(charakter.vermoegen, 250)
        self.assertEqual(charakter.verbleibende_handicap_punkte, 0)

    def test_erhoehe_ohne_setting_default(self):
        """Ohne custom_element_manager: Default 500"""
        charakter = FakeCharakter()
        charakter.verbleibende_handicap_punkte = 1
        erhoehe_startkapital(charakter)
        self.assertEqual(charakter.vermoegen, 500)

    def test_erhoehe_manager_fehler_sicherheits_fallback(self):
        """Manager wirft Exception → Sicherheits-Fallback 500"""
        charakter = FakeCharakter()
        charakter.verbleibende_handicap_punkte = 1
        charakter.custom_element_manager = Mock()
        charakter.custom_element_manager.get_active_setting.side_effect = RuntimeError("kaputt")
        erhoehe_startkapital(charakter)
        self.assertEqual(charakter.vermoegen, 500)

    def test_erhoehe_ohne_handicap_punkte(self):
        """Keine HP → Vermögen unverändert"""
        charakter = FakeCharakter()
        charakter.verbleibende_handicap_punkte = 0
        erhoehe_startkapital(charakter)
        self.assertEqual(charakter.vermoegen, 0)
        self.assertEqual(charakter.startgeld_einloesungen, 0)

    def test_zuruecknehmen_erstattet_handicap_punkt(self):
        """Rücknahme: Geld weg, Handicap-Punkt zurück"""
        charakter = FakeCharakter()
        charakter.verbleibende_handicap_punkte = 1
        erhoehe_startkapital(charakter)
        self.assertEqual(charakter.startgeld_einloesungen, 1)

        erfolg, meldung = senke_startkapital(charakter)
        self.assertTrue(erfolg)
        self.assertEqual(meldung, "")
        self.assertEqual(charakter.vermoegen, 0)
        self.assertEqual(charakter.verbleibende_handicap_punkte, 1)
        self.assertEqual(charakter.startgeld_einloesungen, 0)

    def test_zuruecknehmen_ohne_einloesung(self):
        """Nichts eingelöst → Rücknahme schlägt fehl"""
        charakter = FakeCharakter()
        charakter.vermoegen = 500
        erfolg, meldung = senke_startkapital(charakter)
        self.assertFalse(erfolg)
        self.assertIn("keine Handicap-Punkte", meldung)
        self.assertEqual(charakter.vermoegen, 500)

    def test_zuruecknehmen_wenn_geld_ausgegeben(self):
        """Geld schon ausgegeben → Rücknahme schlägt fehl, nichts ändert sich"""
        charakter = FakeCharakter()
        charakter.verbleibende_handicap_punkte = 1
        erhoehe_startkapital(charakter)
        charakter.vermoegen -= 100  # Ausrüstung gekauft

        erfolg, meldung = senke_startkapital(charakter)
        self.assertFalse(erfolg)
        self.assertIn("bereits ausgegeben", meldung)
        self.assertEqual(charakter.vermoegen, 400)
        self.assertEqual(charakter.verbleibende_handicap_punkte, 0)
        self.assertEqual(charakter.startgeld_einloesungen, 1)

    def test_zuruecknehmen_nutzt_setting_startgeld(self):
        """Zurückgenommen wird genau das Setting-Startgeld"""
        charakter = FakeCharakter()
        charakter.verbleibende_handicap_punkte = 2
        charakter.custom_element_manager = Mock()
        charakter.custom_element_manager.get_active_setting.return_value = {'startgeld': 250}
        erhoehe_startkapital(charakter)
        erhoehe_startkapital(charakter)
        self.assertEqual(charakter.vermoegen, 500)

        senke_startkapital(charakter)
        self.assertEqual(charakter.vermoegen, 250)
        self.assertEqual(charakter.verbleibende_handicap_punkte, 1)
        self.assertEqual(charakter.startgeld_einloesungen, 1)


if __name__ == '__main__':
    unittest.main()
