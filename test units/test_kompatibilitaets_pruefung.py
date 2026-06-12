"""
Unit-Tests für functions/kompatibilitaets_pruefung.py

Prüft die Talent↔Handicap-Inkompatibilitätsregeln (Reich/Stinkreich ↔ Arm)
und die Savage-Pathfinder-Talent-Limits (kostenlose Klassen-/Hintergrund-/
Experte-Talente während der Charaktererstellung).
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Pfad zur Projektroot hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.kompatibilitaets_pruefung import (
    ist_talent_mit_handicaps_kompatibel,
    ist_handicap_mit_talenten_kompatibel,
    pruefe_pathfinder_talent_limits,
    pruefe_pathfinder_charaktererstellung_abschluss,
)


class FakeHandicap:
    def __init__(self, name, stufe="leicht"):
        self.name = name
        self.stufe = stufe


class FakeTalent:
    def __init__(self, name, kategorie="Kampf", ausgewaehlt=False):
        self.name = name
        self.kategorie = kategorie
        self.ausgewaehlt = ausgewaehlt
        self.beschreibung = ""


class FakeCharakter:
    def __init__(self):
        self.selected_handicaps = []
        self.selected_talente = []
        self.handicaps = {}
        self.talente = {}
        self.char_gen_completed = False

    def add_handicap(self, name, stufe="leicht"):
        self.handicaps[name] = FakeHandicap(name, stufe)
        self.selected_handicaps.append(name)


class TestTalentHandicapKompatibilitaet(unittest.TestCase):
    """Tests für Reich/Stinkreich ↔ Arm"""

    def test_reich_mit_arm_inkompatibel(self):
        """Reich und Stinkreich sind mit Arm nicht kombinierbar"""
        for talent in ("Reich", "Stinkreich"):
            with self.subTest(talent=talent):
                charakter = FakeCharakter()
                charakter.add_handicap("Arm")
                kompatibel, meldung = ist_talent_mit_handicaps_kompatibel(charakter, talent)
                self.assertFalse(kompatibel)
                self.assertIn("Arm", meldung)

    def test_reich_ohne_arm_kompatibel(self):
        """Reich ohne Arm-Handicap ist erlaubt"""
        charakter = FakeCharakter()
        charakter.add_handicap("Langsam")
        kompatibel, meldung = ist_talent_mit_handicaps_kompatibel(charakter, "Reich")
        self.assertTrue(kompatibel)
        self.assertEqual(meldung, "")

    def test_anderes_talent_mit_arm_kompatibel(self):
        """Beliebige andere Talente sind mit Arm kombinierbar"""
        charakter = FakeCharakter()
        charakter.add_handicap("Arm")
        kompatibel, _ = ist_talent_mit_handicaps_kompatibel(charakter, "Block")
        self.assertTrue(kompatibel)

    def test_verwaister_handicap_key_wird_uebersprungen(self):
        """Key in selected_handicaps ohne Eintrag in handicaps → kein Fehler"""
        charakter = FakeCharakter()
        charakter.selected_handicaps.append("Arm")  # absichtlich NICHT in handicaps
        kompatibel, _ = ist_talent_mit_handicaps_kompatibel(charakter, "Reich")
        self.assertTrue(kompatibel)

    def test_arm_mit_reich_inkompatibel(self):
        """Umgekehrte Richtung: Arm ist mit Reich/Stinkreich nicht kombinierbar"""
        for talent in ("Reich", "Stinkreich"):
            with self.subTest(talent=talent):
                charakter = FakeCharakter()
                charakter.handicaps["Arm"] = FakeHandicap("Arm")
                charakter.selected_talente = [talent]
                kompatibel, meldung = ist_handicap_mit_talenten_kompatibel(charakter, "Arm")
                self.assertFalse(kompatibel)
                self.assertIn("Arm", meldung)

    def test_arm_ohne_reich_kompatibel(self):
        """Arm ohne Reich/Stinkreich ist erlaubt"""
        charakter = FakeCharakter()
        charakter.handicaps["Arm"] = FakeHandicap("Arm")
        charakter.selected_talente = ["Block"]
        kompatibel, _ = ist_handicap_mit_talenten_kompatibel(charakter, "Arm")
        self.assertTrue(kompatibel)

    def test_anderes_handicap_mit_reich_kompatibel(self):
        """Nicht-Arm-Handicaps sind mit Reich kombinierbar"""
        charakter = FakeCharakter()
        charakter.handicaps["Langsam"] = FakeHandicap("Langsam")
        charakter.selected_talente = ["Reich"]
        kompatibel, _ = ist_handicap_mit_talenten_kompatibel(charakter, "Langsam")
        self.assertTrue(kompatibel)

    def test_unbekanntes_handicap_kompatibel(self):
        """Handicap-Name ohne Eintrag im Dict → kompatibel (Ist-Verhalten)"""
        charakter = FakeCharakter()
        charakter.selected_talente = ["Reich"]
        kompatibel, _ = ist_handicap_mit_talenten_kompatibel(charakter, "Unbekannt")
        self.assertTrue(kompatibel)


class TestPathfinderTalentLimits(unittest.TestCase):
    """Tests für pruefe_pathfinder_talent_limits()

    Die Helfer werden funktionslokal aus functions.talent_funktionen
    importiert, daher Patch im Quellmodul.
    """

    def pruefe(self, charakter, talent_name, ist_pathfinder=True,
               ist_kostenlos=True, hat_bereits=False):
        with patch('functions.talent_funktionen.ist_savage_pathfinder_setting',
                   return_value=ist_pathfinder), \
             patch('functions.talent_funktionen.ist_pathfinder_kostenloses_talent',
                   return_value=ist_kostenlos), \
             patch('functions.talent_funktionen.hat_bereits_kostenloses_pathfinder_talent',
                   return_value=hat_bereits):
            return pruefe_pathfinder_talent_limits(charakter, talent_name)

    def test_nicht_pathfinder_immer_erlaubt(self):
        """Außerhalb von Savage Pathfinder: keine Limits"""
        charakter = FakeCharakter()
        erlaubt, meldung = self.pruefe(charakter, "Irgendein Talent", ist_pathfinder=False)
        self.assertTrue(erlaubt)
        self.assertEqual(meldung, "")

    def test_kostenloses_talent_verfuegbar(self):
        """CharGen, kostenloses Talent, noch keins gewählt → erlaubt mit Hinweis"""
        charakter = FakeCharakter()
        charakter.talente["Klassentalent"] = FakeTalent("Klassentalent", kategorie="Klasse")
        erlaubt, meldung = self.pruefe(charakter, "Klassentalent", hat_bereits=False)
        self.assertTrue(erlaubt)
        self.assertIn("kostenloses", meldung)

    def test_kostenloses_talent_bereits_verbraucht(self):
        """CharGen, kostenloses Talent, aber schon eins gewählt → blockiert"""
        charakter = FakeCharakter()
        charakter.talente["Klassentalent"] = FakeTalent("Klassentalent", kategorie="Klasse")
        erlaubt, meldung = self.pruefe(charakter, "Klassentalent", hat_bereits=True)
        self.assertFalse(erlaubt)
        self.assertIn("nur", meldung)

    def test_nach_chargen_normale_kosten(self):
        """Nach Abschluss der Charaktererstellung: normale Kosten"""
        charakter = FakeCharakter()
        charakter.char_gen_completed = True
        charakter.talente["Klassentalent"] = FakeTalent("Klassentalent", kategorie="Klasse")
        erlaubt, meldung = self.pruefe(charakter, "Klassentalent", hat_bereits=True)
        self.assertTrue(erlaubt)
        self.assertIn("Normale Kosten", meldung)

    def test_unbekanntes_talent_erlaubt(self):
        """Talent nicht im Charakter-Talente-Dict → erlaubt (Ist-Verhalten)"""
        charakter = FakeCharakter()
        erlaubt, meldung = self.pruefe(charakter, "Gibt es nicht")
        self.assertTrue(erlaubt)
        self.assertEqual(meldung, "")


class TestPathfinderAbschluss(unittest.TestCase):
    """Tests für pruefe_pathfinder_charaktererstellung_abschluss()"""

    def pruefe(self, charakter, ist_pathfinder=True):
        with patch('functions.talent_funktionen.ist_savage_pathfinder_setting',
                   return_value=ist_pathfinder):
            return pruefe_pathfinder_charaktererstellung_abschluss(charakter)

    def test_nicht_pathfinder(self):
        """Außerhalb Pathfinder: immer abschließbar, keine Warnungen"""
        charakter = FakeCharakter()
        kann, warnungen = self.pruefe(charakter, ist_pathfinder=False)
        self.assertTrue(kann)
        self.assertEqual(warnungen, [])

    def test_nach_chargen_keine_warnungen(self):
        """Nach Abschluss: keine Prüfung mehr"""
        charakter = FakeCharakter()
        charakter.char_gen_completed = True
        kann, warnungen = self.pruefe(charakter)
        self.assertTrue(kann)
        self.assertEqual(warnungen, [])

    def test_hinweis_auf_verfuegbare_kostenlose_talente(self):
        """Kein kostenloses Talent gewählt, aber verfügbar → HINWEIS-Warnung"""
        charakter = FakeCharakter()
        charakter.talente["Wildnistalent"] = FakeTalent("Wildnistalent", kategorie="Klasse")
        kann, warnungen = self.pruefe(charakter)
        self.assertTrue(kann)
        self.assertTrue(any("HINWEIS" in w for w in warnungen))

    def test_info_wenn_bereits_gewaehlt(self):
        """Bereits kostenloses Talent gewählt → INFO-Meldung"""
        charakter = FakeCharakter()
        charakter.pathfinder_kostenlose_talente_gewaehlt = 1
        kann, warnungen = self.pruefe(charakter)
        self.assertTrue(kann)
        self.assertTrue(any("INFO" in w for w in warnungen))


if __name__ == '__main__':
    unittest.main()
