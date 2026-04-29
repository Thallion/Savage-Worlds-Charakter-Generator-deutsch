"""
Tests für Schritt 2 (Rest) des Volkseigenarten-Plans:
- 2a: `kosten_per_instanz`-Feld in `berechne_punktestand`
- 2e: Numerische Effekte werden in `eigenart_zu_effekte` summiert
       statt überschrieben.
"""

import unittest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.volkseigenarten_funktionen import (
    berechne_punktestand,
    eigenart_zu_effekte,
)


class TestKostenPerInstanzFlag(unittest.TestCase):
    """`kosten_per_instanz` (Default True) bestimmt, ob jede Instanz
    einer Eigenart-ID eigene Kosten verursacht."""

    def test_default_true_zwei_instanzen_zaehlen_doppelt(self):
        eigenarten = [
            {'id': 'robustheit_erhoeht', 'kosten': 1},
            {'id': 'robustheit_erhoeht', 'kosten': 1},
        ]
        result = berechne_punktestand(eigenarten)
        self.assertEqual(result['positive_kosten'], 2)

    def test_kosten_per_instanz_false_zaehlt_nur_einmal(self):
        eigenarten = [
            {'id': 'volk_macht', 'kosten': 2, 'kosten_per_instanz': False},
            {'id': 'volk_macht', 'kosten': 2, 'kosten_per_instanz': False},
            {'id': 'volk_macht', 'kosten': 2, 'kosten_per_instanz': False},
        ]
        result = berechne_punktestand(eigenarten)
        # Schritt 3a: volk_macht 3× → Formel 2+1×(3-1)=4 EP
        self.assertEqual(result['positive_kosten'], 4)

    def test_gemischt_kosten_per_instanz(self):
        """Eigenarten mit kosten_per_instanz=False und ohne mischen sich korrekt."""
        eigenarten = [
            {'id': 'volk_macht', 'kosten': 2, 'kosten_per_instanz': False},
            {'id': 'volk_macht', 'kosten': 2, 'kosten_per_instanz': False},
            {'id': 'robustheit_erhoeht', 'kosten': 1},
            {'id': 'robustheit_erhoeht', 'kosten': 1},
        ]
        result = berechne_punktestand(eigenarten)
        # Schritt 3a: volk_macht 2× → 2+1×(2-1)=3 EP, robustheit 2× → 2 EP
        self.assertEqual(result['positive_kosten'], 5)

    def test_negative_eigenart_mit_kosten_per_instanz_false(self):
        """Auch negative Eigenarten respektieren das Flag."""
        eigenarten = [
            {'id': 'volk_macht_neg', 'kosten': -1, 'kosten_per_instanz': False},
            {'id': 'volk_macht_neg', 'kosten': -1, 'kosten_per_instanz': False},
        ]
        result = berechne_punktestand(eigenarten)
        self.assertEqual(result['negative_punkte'], 1)


class TestEffekteSummierenAttribute(unittest.TestCase):
    """`eigenart_zu_effekte` summiert Boni statt zu überschreiben."""

    def test_zwei_attribut_bonus_auf_selbes_attribut_summieren(self):
        # Hypothetische Doppel-Auswahl mit konkretem Attribut (defensiv)
        eigenart = {
            'id': 'attr_test',
            'name': 'Test',
            'effekt_typ': 'attribut_bonus',
            'kosten': 2,
            'effekt': {'attribut_bonus': 2},
            'optionen': {'typ': 'attribut_auswahl', 'ausgewaehlt': 'Stärke'},
        }
        effects = eigenart_zu_effekte([dict(eigenart), dict(eigenart)], [])
        self.assertEqual(effects['attribute_bonuses']['Stärke'], 4)

    def test_zwei_grundfertigkeit_bonus_auf_selbe_fertigkeit_summieren(self):
        eigenart = {
            'id': 'fert_test',
            'name': 'Test',
            'effekt_typ': 'fertigkeits_bonus',
            'kosten': 1,
            'effekt': {'grundfertigkeit_bonus': 2},
            'optionen': {'typ': 'grundfertigkeit_auswahl', 'ausgewaehlt': 'Athletik'},
        }
        effects = eigenart_zu_effekte([dict(eigenart), dict(eigenart)], [])
        self.assertEqual(effects['fertigkeits_startboni']['Athletik'], 4)


class TestEffekteSummierenSpeziellerEffekt(unittest.TestCase):
    """Numerische Felder im `spezieller_effekt`-Pfad summieren statt überschreiben."""

    def test_zwei_athletik_malus_summieren(self):
        eigenart = {
            'id': 'athletik_test',
            'name': 'Test',
            'effekt_typ': 'spezieller_effekt',
            'kosten': -1,
            'effekt': {'athletik_malus': 1},
        }
        effects = eigenart_zu_effekte([], [dict(eigenart), dict(eigenart)])
        self.assertEqual(effects.get('athletik_malus'), 2)

    def test_zwei_bewegungsweite_flug_summieren(self):
        eigenart = {
            'id': 'flug_test',
            'name': 'Test',
            'effekt_typ': 'spezieller_effekt',
            'kosten': 2,
            'effekt': {'bewegungsweite_flug': 6},
        }
        effects = eigenart_zu_effekte([dict(eigenart), dict(eigenart)], [])
        self.assertEqual(effects.get('bewegungsweite_flug'), 12)

    def test_lebenserwartung_mult_multipliziert(self):
        """`lebenserwartung_mult` ist ein Multiplikator und wird multipliziert,
        nicht summiert."""
        eigenart = {
            'id': 'leben_test',
            'name': 'Test',
            'effekt_typ': 'spezieller_effekt',
            'kosten': 1,
            'effekt': {'lebenserwartung_mult': 2},
        }
        effects = eigenart_zu_effekte([dict(eigenart), dict(eigenart)], [])
        self.assertEqual(effects.get('lebenserwartung_mult'), 4)


if __name__ == '__main__':
    unittest.main()
