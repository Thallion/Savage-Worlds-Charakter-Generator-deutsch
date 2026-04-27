"""
Test-Units für die Stufen-Unterstützung in Volkseigenarten.

Stufen-Eigenarten haben mehrere Punkte-/Effekt-Stufen (z.B. Fliegen 2/4/6 EP).
Beim Auswählen einer Stufe werden kosten und effekt aus der Stufe in die
Eigenart-Instanz übernommen.
"""

import unittest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.volkseigenarten_funktionen import (
    stufen_kosten_bereich,
    wende_stufe_an,
    eigenart_zu_besonderheiten,
    eigenart_zu_effekte,
    validiere_volk_erstellung,
    berechne_punktestand,
)


def _fliegen_eigenart():
    """Beispiel: Fliegen mit 3 Stufen (2/4/6 EP)."""
    return {
        'id': 'fliegen',
        'name': 'Fliegen',
        'max_auswahl': 1,
        'effekt_typ': 'spezieller_effekt',
        'beschreibung': 'Das Volk kann fliegen.',
        'stufen': [
            {'label': 'Bewegungsweite 6', 'kosten': 2,
             'effekt': {'fliegen': True, 'bewegungsweite_flug': 6}},
            {'label': 'Bewegungsweite 12', 'kosten': 4,
             'effekt': {'fliegen': True, 'bewegungsweite_flug': 12}},
            {'label': 'Bewegungsweite 24', 'kosten': 6,
             'effekt': {'fliegen': True, 'bewegungsweite_flug': 24}},
        ],
    }


def _einfache_eigenart():
    """Eigenart ohne Stufen (Backward-Compat-Test)."""
    return {
        'id': 'nachtsicht',
        'name': 'Nachtsicht',
        'kosten': 1,
        'max_auswahl': 1,
        'effekt_typ': 'spezieller_effekt',
        'effekt': {'nachtsicht': True},
        'beschreibung': 'Ignoriert Abzüge für Düstere/Dunkle Beleuchtung.',
    }


class TestStufenKostenBereich(unittest.TestCase):

    def test_returns_min_max_for_stufen(self):
        eigenart = _fliegen_eigenart()
        self.assertEqual(stufen_kosten_bereich(eigenart), (2, 6))

    def test_returns_none_without_stufen(self):
        self.assertIsNone(stufen_kosten_bereich(_einfache_eigenart()))

    def test_returns_none_for_empty_stufen(self):
        self.assertIsNone(stufen_kosten_bereich({'id': 'x', 'stufen': []}))

    def test_handles_single_stufe(self):
        eigenart = {'id': 'x', 'stufen': [{'kosten': 3, 'effekt': {}}]}
        self.assertEqual(stufen_kosten_bereich(eigenart), (3, 3))


class TestWendeStufeAn(unittest.TestCase):

    def test_kopiert_kosten_und_effekt(self):
        eigenart = _fliegen_eigenart()
        gewaehlt = eigenart['stufen'][1]  # 4 EP, BW 12

        wende_stufe_an(eigenart, gewaehlt)

        self.assertEqual(eigenart['kosten'], 4)
        self.assertEqual(eigenart['effekt'], {'fliegen': True, 'bewegungsweite_flug': 12})
        self.assertEqual(eigenart['ausgewaehlte_stufe']['label'], 'Bewegungsweite 12')

    def test_effekt_ist_kopie_kein_alias(self):
        """Mutationen am Eigenart-Effekt dürfen die Stufen-Quelle nicht verändern."""
        eigenart = _fliegen_eigenart()
        original_stufe = eigenart['stufen'][0]

        wende_stufe_an(eigenart, original_stufe)
        eigenart['effekt']['bewegungsweite_flug'] = 999

        self.assertEqual(original_stufe['effekt']['bewegungsweite_flug'], 6)

    def test_no_op_for_none(self):
        eigenart = _fliegen_eigenart()
        wende_stufe_an(eigenart, None)
        self.assertNotIn('ausgewaehlte_stufe', eigenart)


class TestBesonderheitenStufenLabel(unittest.TestCase):

    def test_zeigt_label_der_gewaehlten_stufe(self):
        eigenart = _fliegen_eigenart()
        wende_stufe_an(eigenart, eigenart['stufen'][2])  # BW 24

        besonderheiten = eigenart_zu_besonderheiten([eigenart], [])

        self.assertEqual(len(besonderheiten), 1)
        self.assertIn('Fliegen', besonderheiten[0])
        self.assertIn('Bewegungsweite 24', besonderheiten[0])

    def test_einfache_eigenart_unveraendert(self):
        eigenart = _einfache_eigenart()
        besonderheiten = eigenart_zu_besonderheiten([eigenart], [])
        self.assertIn('Nachtsicht', besonderheiten[0])


class TestEffectsPersistierenStufe(unittest.TestCase):

    def test_ausgewaehlte_stufe_im_effects_eintrag(self):
        eigenart = _fliegen_eigenart()
        eigenart['typ'] = 'positiv'
        wende_stufe_an(eigenart, eigenart['stufen'][1])

        effects = eigenart_zu_effekte([eigenart], [])
        eintraege = effects.get('eigenarten', [])

        self.assertEqual(len(eintraege), 1)
        self.assertEqual(eintraege[0]['kosten'], 4)
        self.assertEqual(eintraege[0]['ausgewaehlte_stufe']['label'], 'Bewegungsweite 12')

    def test_einfache_eigenart_keine_stufe_im_effects(self):
        eigenart = _einfache_eigenart()
        eigenart['typ'] = 'positiv'

        effects = eigenart_zu_effekte([eigenart], [])

        self.assertNotIn('ausgewaehlte_stufe', effects['eigenarten'][0])


class TestValidierungErzwingtStufenwahl(unittest.TestCase):

    def test_stufen_eigenart_ohne_auswahl_erzeugt_fehler(self):
        eigenart = _fliegen_eigenart()  # noch keine Stufe gewählt

        result = validiere_volk_erstellung('Testvolk', [eigenart], [])

        self.assertFalse(result['ist_gueltig'])
        self.assertTrue(any('Stufe' in f for f in result['fehler']),
                        f"Erwartete Stufen-Fehlermeldung in {result['fehler']}")

    def test_stufen_eigenart_mit_auswahl_validiert(self):
        eigenart = _fliegen_eigenart()
        wende_stufe_an(eigenart, eigenart['stufen'][0])  # 2 EP

        result = validiere_volk_erstellung('Testvolk', [eigenart], [])

        # Sollte keine Stufen-Fehler haben (Punkte könnten ggf. trotzdem unausgeglichen sein)
        self.assertFalse(any('Stufe' in f for f in result['fehler']),
                         f"Unerwartete Stufen-Fehlermeldung in {result['fehler']}")


class TestPunktestandMitStufen(unittest.TestCase):

    def test_kosten_aus_stufe_fliessen_in_punktestand(self):
        eigenart = _fliegen_eigenart()
        wende_stufe_an(eigenart, eigenart['stufen'][2])  # 6 EP

        ergebnis = berechne_punktestand([eigenart])

        self.assertEqual(ergebnis['positive_kosten'], 6)


if __name__ == '__main__':
    unittest.main()
