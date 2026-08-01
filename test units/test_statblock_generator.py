"""
Tests für functions/statblock_generator.py

Schwerpunkt: die Abstammungs-Zeilen. Volks-Talente, -Handicaps und
-Besonderheiten stehen nur am Volk und nicht in selected_talente /
selected_handicaps — ohne sie fehlten sie im Export.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.statblock_generator import _basisname, _format_volk_zeilen


def fake_volk(talente=None, handicaps=None, besonderheiten=None):
    volk = Mock()
    volk.name = 'Testvolk'
    volk.talente = talente or []
    volk.handicaps = handicaps or []
    volk.besonderheiten = besonderheiten or []
    return volk


class FakeCharakter:
    def __init__(self, volk=None, selected_talente=None, selected_handicaps=None):
        self.voelker = {'Testvolk': volk} if volk else {}
        self.voelker_selected = {'Testvolk': True} if volk else {}
        self.selected_talente = selected_talente or []
        self.selected_handicaps = selected_handicaps or []


class TestBasisname(unittest.TestCase):
    """Stufen-Suffix und Klammerzusatz gehören nicht zum Vergleichsnamen"""

    def test_stufen_suffix_wird_entfernt(self):
        self.assertEqual(_basisname("Schwur_schwer"), "Schwur")
        self.assertEqual(_basisname("Langsam_leicht"), "Langsam")

    def test_klammerzusatz_wird_entfernt(self):
        self.assertEqual(_basisname("Schwur (schwer: dem Orden)"), "Schwur")
        self.assertEqual(_basisname("Nachtsicht"), "Nachtsicht")


class TestVolkZeilen(unittest.TestCase):

    def test_ohne_volk_keine_zeilen(self):
        self.assertEqual(_format_volk_zeilen(FakeCharakter()), [])

    def test_talente_handicaps_und_besonderheiten(self):
        charakter = FakeCharakter(fake_volk(
            talente=["Nachtsicht"],
            handicaps=["Blutrünstig", "Nichtschwimmer"],
            besonderheiten=["Klauen (Stä+W4 Schaden, PB 2)"],
        ))
        self.assertEqual(_format_volk_zeilen(charakter), [
            ("Abstammungs-Talente", "Nachtsicht"),
            ("Abstammungs-Handicaps", "Blutrünstig, Nichtschwimmer"),
            ("Besonderheiten", "Klauen (Stä+W4 Schaden, PB 2)"),
        ])

    def test_auto_elemente_werden_nicht_doppelt_gelistet(self):
        """Was schon als Talent/Handicap gewählt ist, steht nicht noch einmal da"""
        charakter = FakeCharakter(
            fake_volk(talente=["Nachtsicht"], handicaps=["Langsam (leicht)"]),
            selected_talente=["Nachtsicht", "Block"],
            selected_handicaps=["Langsam_leicht"],
        )
        self.assertEqual(_format_volk_zeilen(charakter), [
            ("Abstammungs-Talente", ""),
            ("Abstammungs-Handicaps", ""),
            ("Besonderheiten", ""),
        ])


if __name__ == '__main__':
    unittest.main()
