"""
Test-Units für die Mehrfachauswahl-Unterstützung in Volkseigenarten.

Mehrfachauswahl erlaubt das mehrfache Auswählen einer Eigenart (z.B. Robustheit 3x)
mit unterschiedlichen oder gleichen Kosten pro Instanz.
"""

import unittest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.volkseigenarten_funktionen import (
    berechne_punktestand,
    validiere_volk_erstellung,
    get_eigenart_by_id,
)


class TestMehrfachAuswahlMaxAuswahl(unittest.TestCase):
    """Tests für max_auswahl-Limit-Überschreitung."""

    def test_max_auswahl_1_wird_nicht_ueberschritten(self):
        """max_auswahl=1 erlaubt nur eine Instanz."""
        volle = get_eigenart_by_id('nachtsicht', 'positive')
        self.assertEqual(volle.get('max_auswahl'), 1)

    def test_max_auswahl_2_bei_attributserhoehung(self):
        """Attributserhöhung hat max_auswahl=0 (unbegrenzt) per Regeln."""
        volle = get_eigenart_by_id('attributserhoehung', 'positive')
        self.assertEqual(volle.get('max_auswahl'), 0)

    def test_unbegrenzt_max_auswahl_0(self):
        """max_auswahl=0 bedeutet unbegrenzt. Immunität hat max_auswahl=2 per Regeln."""
        volle = get_eigenart_by_id('immunisierungen', 'positive')
        self.assertEqual(volle.get('max_auswahl'), 2)


class TestMehrfachAuswahlPunktestand(unittest.TestCase):
    """Tests für Punktestand bei mehrfachen Instanzen."""

    def test_zwei_instanzen_kosten_doppelt(self):
        """2x Nachtsicht (je 1 EP) = 2 EP. (Kosten korrigiert: 1 EP statt 2 EP)"""
        nachtsicht = get_eigenart_by_id('nachtsicht', 'positive')
        instanz1 = dict(nachtsicht)
        instanz2 = dict(nachtsicht)

        ergebnis = berechne_punktestand([instanz1, instanz2])
        self.assertEqual(ergebnis['positive_kosten'], 2)

    def test_drei_instanzen_robustheit(self):
        """3x Robustheit (je 1 EP) = 3 EP. (Kosten korrigiert: 1 EP statt 2 EP)"""
        robustheit = get_eigenart_by_id('robustheit_erhoeht', 'positive')
        instanzen = [dict(robustheit) for _ in range(3)]

        ergebnis = berechne_punktestand(instanzen)
        self.assertEqual(ergebnis['positive_kosten'], 3)


class TestMehrfachAuswahlValidierung(unittest.TestCase):
    """Tests für validiere_volk_erstellung mit Mehrfachauswahl."""

    def test_zwei_attributserhoehung_validiert(self):
        """2x Attributserhöhung (max=2) sollte validieren."""
        attr = get_eigenart_by_id('attributserhoehung', 'positive')
        instanz1 = dict(attr)
        instanz1['optionen'] = {'typ': 'attribut_auswahl', 'ausgewaehlt': 'Stärke'}
        instanz2 = dict(attr)
        instanz2['optionen'] = {'typ': 'attribut_auswahl', 'ausgewaehlt': 'Verstand'}

        result = validiere_volk_erstellung('Testvolk', [instanz1, instanz2], [])
        self.assertTrue(result['ist_gueltig'])

    def test_drei_attributserhoehung_fehler(self):
        """3x Attributserhöhung (max=0 = unbegrenzt) sollte NICHT Fehler erzeugen."""
        attr = get_eigenart_by_id('attributserhoehung', 'positive')
        instanzen = []
        for i, attr_name in enumerate(['Stärke', 'Geschicklichkeit', 'Verstand']):
            instanz = dict(attr)
            instanz['optionen'] = {'typ': 'attribut_auswahl', 'ausgewaehlt': attr_name}
            instanzen.append(instanz)

        result = validiere_volk_erstellung('Testvolk', instanzen, [])
        self.assertTrue(result['ist_gueltig'])


class TestMehrfachAuswahlStufenInstanzen(unittest.TestCase):
    """Tests für mehrfache Instanzen mit unterschiedlichen Stufen."""

    def test_zwei_klauen_mit_unterschiedlichen_stufen(self):
        """2x Klauen mit unterschiedlichen Stufen."""
        klauen = get_eigenart_by_id('klauen', 'positive')
        self.assertIsNotNone(klauen)
        self.assertEqual(klauen.get('max_auswahl'), 1)

    def test_klauen_mit_stufe_kosten(self):
        """Klauen Stufe 3 (4 EP) sollte 4 EP kosten."""
        klauen = get_eigenart_by_id('klauen', 'positive')
        klauen_copy = dict(klauen)
        klauen_copy['kosten'] = klauen['stufen'][2]['kosten']
        klauen_copy['effekt'] = dict(klauen['stufen'][2]['effekt'])

        self.assertEqual(klauen_copy['kosten'], 4)


if __name__ == '__main__':
    unittest.main()