#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Unit für die neue abgeleitete Größe und ihre Auswirkung auf Robustheit.

Prüft:
  - groesse-Property existiert und Default 0
  - Volk-Größe wird korrekt aus effects.groesse_modifikator gelesen
  - Talent "Kräftig" → Größe +1 (statt direktem Robustheit-Bonus)
  - Handicap "Klein" leicht → Größe -1 (statt direktem Robustheit-Bonus)
  - Robustheit summiert Größe + sonstige Robustheit-Boni
  - Migrierte Setting-Daten (Halbling, Halbriese, Goblin, Flickenmonster) korrekt
"""

import unittest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class MockWuerfel:
    def __init__(self, value=4, modifier=0):
        self.value = value
        self.modifier = modifier


class MockAttribut:
    def __init__(self, name, wert=4, modifier=0):
        self.name = name
        self.wert = wert
        self.modifier = modifier
        self.wuerfel = MockWuerfel(value=wert, modifier=modifier)


class MockFertigkeit:
    def __init__(self, wert=4):
        self.wert = wert


class MockHandicap:
    def __init__(self, name, stufe="leicht"):
        self.name = name
        self.stufe = stufe
        self.ausgewaehlt = True


class MockVolk:
    def __init__(self, name, groesse_mod=0, robustheit_bonus=0, bewegung_bonus=0):
        self.name = name
        self.effects = {
            'groesse_modifikator': groesse_mod,
            'robustheit_bonus': robustheit_bonus,
            'bewegungsweite_bonus': bewegung_bonus,
            'spezielle_effekte': {},
            'auto_talente': [],
        }

    def get_groesse_modifikator(self):
        return self.effects.get('groesse_modifikator', 0)

    def get_robustheit_bonus(self):
        return self.effects.get('robustheit_bonus', 0)

    def get_bewegungsweite_bonus(self):
        return self.effects.get('bewegungsweite_bonus', 0)


class MockCharakter:
    """Minimaler Mock, der die Felder bereitstellt, die berechne_abgeleitete_werte braucht."""

    def __init__(self, konstitution=4):
        self.attribute = {'Konstitution': MockAttribut('Konstitution', konstitution)}
        self.fertigkeiten = {}
        self.handicaps = {}
        self.talente = {}
        self.voelker = {}
        self.voelker_selected = {}
        self.selected_handicaps = []
        self.selected_talente = []
        self.selected_waffen = []
        self.selected_ruestungen = []
        self.selected_schilde = []
        self.selected_allgemeine_ausruestung = []
        self.cyberware_installationen = {}
        self.ausruestung = {}
        self.active_setting_name = "SWAE"
        self.machtpunkte = 0
        self.erschoepfung = 0
        self.wunden = 0
        self.bennys = 3
        self.entschlossenheit = 0
        self.vermoegen = 500
        self.waehrungseinheit = "Gold"
        self.gesamtgewicht = 0
        self.maximale_traglast = 40
        # Abgeleitete Werte (werden vom Test geschrieben)
        self.bewegungsweite = 6
        self.parade = 2
        self.robustheit = 0
        self.robustheit_basis = 0
        self.robustheit_mit_ruestung = ""
        self.groesse = 0


class TestGroesseBerechnung(unittest.TestCase):
    """Direkter Test der Größe-Berechnung in berechne_abgeleitete_werte."""

    def setUp(self):
        from functions.abgeleitete_werte import berechne_abgeleitete_werte
        self.berechne = berechne_abgeleitete_werte

    def test_mensch_default_groesse_0(self):
        """Mensch ohne Volk: Größe = 0, Robustheit = (KON//2) + 2."""
        char = MockCharakter(konstitution=6)
        self.berechne(char)
        self.assertEqual(char.groesse, 0)
        self.assertEqual(char.robustheit_basis, (6 // 2) + 2)  # = 5

    def test_halbling_groesse_minus_1(self):
        """Volk mit groesse_modifikator=-1: Größe = -1, Robustheit -1."""
        char = MockCharakter(konstitution=6)
        char.voelker = {'Halbling': MockVolk('Halbling', groesse_mod=-1)}
        char.voelker_selected = {'Halbling': True}
        self.berechne(char)
        self.assertEqual(char.groesse, -1)
        self.assertEqual(char.robustheit_basis, (6 // 2) + 2 - 1)  # = 4

    def test_halbriese_groesse_plus_3(self):
        """Volk mit groesse_modifikator=+3: Größe = +3, Robustheit +3."""
        char = MockCharakter(konstitution=8)
        char.voelker = {'Halbriese': MockVolk('Halbriese', groesse_mod=3)}
        char.voelker_selected = {'Halbriese': True}
        self.berechne(char)
        self.assertEqual(char.groesse, 3)
        self.assertEqual(char.robustheit_basis, (8 // 2) + 2 + 3)  # = 9

    def test_kraeftig_talent_erhoeht_groesse(self):
        """Talent 'Kräftig' erhöht Größe um 1 (nicht mehr direkt robustheit)."""
        char = MockCharakter(konstitution=6)
        char.selected_talente = ['Kräftig']
        self.berechne(char)
        self.assertEqual(char.groesse, 1)
        self.assertEqual(char.robustheit_basis, (6 // 2) + 2 + 1)  # = 6

    def test_klein_handicap_verringert_groesse(self):
        """Handicap 'Klein' leicht: Größe -1 (nicht mehr direkt robustheit)."""
        char = MockCharakter(konstitution=6)
        char.handicaps = {'Klein': MockHandicap('Klein', 'leicht')}
        char.selected_handicaps = ['Klein']
        self.berechne(char)
        self.assertEqual(char.groesse, -1)
        self.assertEqual(char.robustheit_basis, (6 // 2) + 2 - 1)  # = 4

    def test_fettleibig_handicap_robustheit_kein_groesse(self):
        """Handicap 'Fettleibig' leicht: Robustheit +1, aber Größe = 0 (Körperfett)."""
        char = MockCharakter(konstitution=6)
        char.handicaps = {'Fettleibig': MockHandicap('Fettleibig', 'leicht')}
        char.selected_handicaps = ['Fettleibig']
        self.berechne(char)
        self.assertEqual(char.groesse, 0)
        self.assertEqual(char.robustheit_basis, (6 // 2) + 2 + 1)  # = 6

    def test_raufbold_talent_robustheit_kein_groesse(self):
        """Talent 'Raufbold': Robustheit +1, aber Größe = 0."""
        char = MockCharakter(konstitution=6)
        char.selected_talente = ['Raufbold']
        self.berechne(char)
        self.assertEqual(char.groesse, 0)
        self.assertEqual(char.robustheit_basis, (6 // 2) + 2 + 1)  # = 6

    def test_halbling_mit_kraeftig_neutralisiert(self):
        """Halbling (-1 Größe) + Kräftig (+1 Größe) = 0; Robustheit unverändert."""
        char = MockCharakter(konstitution=6)
        char.voelker = {'Halbling': MockVolk('Halbling', groesse_mod=-1)}
        char.voelker_selected = {'Halbling': True}
        char.selected_talente = ['Kräftig']
        self.berechne(char)
        self.assertEqual(char.groesse, 0)
        self.assertEqual(char.robustheit_basis, (6 // 2) + 2)  # = 5

    def test_split_volk_groesse_und_robustheit(self):
        """Volk mit groesse=+1 UND robustheit_bonus=+1 (z.B. Flickenmonster):
        Größe und Rest-Robustheit werden separat addiert (insgesamt +2 auf Robustheit)."""
        char = MockCharakter(konstitution=6)
        char.voelker = {'Flickenmonster': MockVolk('Flickenmonster',
                                                    groesse_mod=1,
                                                    robustheit_bonus=1)}
        char.voelker_selected = {'Flickenmonster': True}
        self.berechne(char)
        self.assertEqual(char.groesse, 1)
        self.assertEqual(char.robustheit_basis, (6 // 2) + 2 + 1 + 1)  # = 7


class TestSettingsMigration(unittest.TestCase):
    """Verifiziert, dass die Settings-JSONs nach Migration konsistent sind."""

    def _load_volk(self, setting_datei, volk_name):
        import json
        pfad = project_root / 'settings' / setting_datei
        with pfad.open('r', encoding='utf-8') as f:
            daten = json.load(f)
        return daten['voelker'].get(volk_name)

    def test_swae_halbling(self):
        volk = self._load_volk('SWAE.json', 'Halbling')
        self.assertEqual(volk['effects']['groesse_modifikator'], -1)
        self.assertEqual(volk['effects']['robustheit_bonus'], 0)

    def test_fk_halbriese(self):
        volk = self._load_volk('Fantasy Kompendium.json', 'Halbriese')
        self.assertEqual(volk['effects']['groesse_modifikator'], 3)
        self.assertEqual(volk['effects']['robustheit_bonus'], 0)

    def test_fk_goblin(self):
        volk = self._load_volk('Fantasy Kompendium.json', 'Goblin')
        self.assertEqual(volk['effects']['groesse_modifikator'], -1)
        self.assertEqual(volk['effects']['robustheit_bonus'], 0)

    def test_horror_flickenmonster_split(self):
        """Flickenmonster: Größe +1 (aus Text) plus Untoten-Robustheit +1."""
        volk = self._load_volk('Horror Kompendium.json', 'Flickenmonster')
        self.assertEqual(volk['effects']['groesse_modifikator'], 1)
        self.assertEqual(volk['effects']['robustheit_bonus'], 1)


class TestVolkParser(unittest.TestCase):
    """Prüft, dass _parse_einzeleffekt 'Größe ±X' nach groesse_modifikator routet."""

    def test_groesse_minus_1_in_handicap_text(self):
        from models.volk import Volk
        volk = Volk(name="TestVolk", handicaps=["Größe -1 (Reduzierte Robustheit um 1)"])
        volk._parse_effects_from_text()
        self.assertEqual(volk.effects.get('groesse_modifikator', 0), -1)
        self.assertEqual(volk.effects.get('robustheit_bonus', 0), 0,
                         "robustheit_bonus darf NICHT mehr gesetzt werden, wenn Größe schon erkannt wurde")

    def test_groesse_plus_3_in_besonderheiten(self):
        from models.volk import Volk
        volk = Volk(name="TestVolk", besonderheiten=["Größe +3 (+3 Robustheit durch überragende Größe)"])
        volk._parse_effects_from_text()
        self.assertEqual(volk.effects.get('groesse_modifikator', 0), 3)
        self.assertEqual(volk.effects.get('robustheit_bonus', 0), 0)

    def test_orkische_wildheit_bleibt_robustheit(self):
        from models.volk import Volk
        volk = Volk(name="TestVolk", besonderheiten=["Orkische Wildheit (+1 Robustheit)"])
        volk._parse_effects_from_text()
        self.assertEqual(volk.effects.get('groesse_modifikator', 0), 0)
        self.assertEqual(volk.effects.get('robustheit_bonus', 0), 1,
                         "Robustheit-Boni ohne 'Größe'-Wort bleiben in robustheit_bonus")


if __name__ == '__main__':
    unittest.main(verbosity=2)
