"""
Tests für Schritt 3 (Sonderfälle) des Volkseigenarten-Plans:
- 3a: volk_macht mit Kostenformel 2+1×(N-1)
- 3b: volk_talent mit Kostenformel 2+Rang
- 3c: volk_superkraft mit Kosten 2+SKP-Kosten
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
from functions.superkraft_funktionen import ist_superkraefte_setting


class TestVolkMachtKostenformel(unittest.TestCase):
    """volk_macht: Kostenformel 2 + 1×(N-1)"""

    def test_eine_macht_kostet_2(self):
        eigenarten = [{'id': 'volk_macht', 'kosten': 2, 'kosten_per_instanz': False}]
        result = berechne_punktestand(eigenarten)
        self.assertEqual(result['positive_kosten'], 2)

    def test_zwei_maechte_kosten_4(self):
        eigenarten = [
            {'id': 'volk_macht', 'kosten': 2, 'kosten_per_instanz': False},
            {'id': 'volk_macht', 'kosten': 2, 'kosten_per_instanz': False},
        ]
        result = berechne_punktestand(eigenarten)
        # Formel 2+1×(2-1)=3 wird auf erste Instanz angewendet; zweite wird
        # wegen kosten_per_instanz=False skippen. → 3 EP
        self.assertEqual(result['positive_kosten'], 3)

    def test_drei_maechte_kosten_4(self):
        eigenarten = [
            {'id': 'volk_macht', 'kosten': 2, 'kosten_per_instanz': False},
            {'id': 'volk_macht', 'kosten': 2, 'kosten_per_instanz': False},
            {'id': 'volk_macht', 'kosten': 2, 'kosten_per_instanz': False},
        ]
        result = berechne_punktestand(eigenarten)
        # Formel 2+1×(3-1)=4 wird auf erste Instanz angewendet; zweite+dritte
        # werden wegen kosten_per_instanz=False übersprungen. → 4 EP
        self.assertEqual(result['positive_kosten'], 4)


class TestVolkSuperkraftKosten(unittest.TestCase):
    """volk_superkraft: 2 + SKP-Kosten"""

    def test_superkraft_mit_3_skp_kostet_5(self):
        eigenarten = [{
            'id': 'volk_superkraft',
            'kosten': 2,
            'optionen': {'punkte_kosten': 3}
        }]
        result = berechne_punktestand(eigenarten)
        self.assertEqual(result['positive_kosten'], 5)

    def test_superkraft_mit_5_skp_kostet_7(self):
        eigenarten = [{
            'id': 'volk_superkraft',
            'kosten': 2,
            'optionen': {'punkte_kosten': 5}
        }]
        result = berechne_punktestand(eigenarten)
        self.assertEqual(result['positive_kosten'], 7)


class TestVolkTalentBasisKosten(unittest.TestCase):
    """volk_talent: Kosten werden in _show_talent_rang_optionen_dialog
    auf 2 + rang gesetzt; hier testen wir die Grundkosten 2."""

    def test_volk_talent_basis_kosten_2(self):
        eigenarten = [{'id': 'volk_talent', 'kosten': 2}]
        result = berechne_punktestand(eigenarten)
        self.assertEqual(result['positive_kosten'], 2)


class TestVolkSuperkraftSettingFilter(unittest.TestCase):
    """volk_superkraft ist nur in Superkräfte-Settings verfügbar."""

    def test_superkraefte_setting_wird_erkannt(self):
        self.assertTrue(ist_superkraefte_setting("Superkräfte Kompendium"))
        self.assertTrue(ist_superkraefte_setting("Superkräfte-Kompendium"))
        self.assertTrue(ist_superkraefte_setting("Superheroes"))

    def test_nicht_superkraefte_setting_wird_abgelehnt(self):
        self.assertFalse(ist_superkraefte_setting("SWAE"))
        self.assertFalse(ist_superkraefte_setting("Deadlands"))
        self.assertFalse(ist_superkraefte_setting("Fantasy Kompendium"))


class TestVolkMachtEffektTyp(unittest.TestCase):
    """macht_volk als effekt_typ wird in eigenart_zu_effekte korrekt verarbeitet."""

    def test_macht_volk_speichert_ausgewaehlte_macht(self):
        eigenart = {
            'id': 'volk_macht',
            'name': 'Macht',
            'typ': 'positiv',
            'effekt_typ': 'macht_volk',
            'kosten': 2,
            'optionen': {'typ': 'macht_auswahl', 'ausgewaehlt': 'Feuerball'}
        }
        effects = eigenart_zu_effekte([eigenart], [])
        self.assertIn('spezielle_effekte', effects)
        macht_effekte = [e for e in effects['spezielle_effekte'] if e['typ'] == 'macht_volk']
        self.assertEqual(len(macht_effekte), 1)
        self.assertEqual(macht_effekte[0]['wert'], 'Feuerball')


class TestVolkSuperkraftEffektTyp(unittest.TestCase):
    """superkraft_volk als effekt_typ wird in eigenart_zu_effekte verarbeitet."""

    def test_superkraft_volk_speichert_kraft_und_kosten(self):
        eigenart = {
            'id': 'volk_superkraft',
            'name': 'Superkräfte',
            'typ': 'positiv',
            'effekt_typ': 'superkraft_volk',
            'kosten': 5,
            'optionen': {
                'typ': 'superkraft_auswahl',
                'ausgewaehlt': 'Rüstung',
                'punkte_kosten': 3
            }
        }
        effects = eigenart_zu_effekte([eigenart], [])
        self.assertIn('spezielle_effekte', effects)
        sk_effekte = [e for e in effects['spezielle_effekte'] if e['typ'] == 'superkraft_volk']
        self.assertEqual(len(sk_effekte), 1)
        self.assertEqual(sk_effekte[0]['wert'], 'Rüstung')
        self.assertEqual(sk_effekte[0]['punkte_kosten'], 3)


if __name__ == '__main__':
    unittest.main()
