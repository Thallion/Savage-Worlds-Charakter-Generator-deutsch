"""
Tests für functions/charakter_migration.py

Die Migrationen laufen beim Laden auf dem rohen Save-Dictionary. Festgeschrieben
wird hier:
- "Größe -1" vereinheitlicht beide Alt-Namen (idempotent, ohne Duplikate)
- die Berserker-Korrektur läuft genau EINMAL (Marker in daten['migrationen'])
"""

import unittest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.charakter_migration import (
    GROESSE_NEU,
    MIGRATIONS_IDS,
    migriere_charakter_daten,
)


def basis_daten(**extra):
    daten = {
        'selected_handicaps': [],
        'selected_talente': [],
        'selected_elements': {'handicaps': {}},
        'attribute': {'Stärke': {'attribut_name': 'Stärke', 'wert': 8, 'modifier': 0}},
    }
    daten.update(extra)
    return daten


class TestGroesseHandicapMigration(unittest.TestCase):
    """Die beiden alten "Größe -1"-Handicaps werden zusammengeführt"""

    def test_beide_alt_namen_werden_umbenannt(self):
        for alt in ("Größe -1 (Reduzierte Robustheit)",
                    "Größe -1 (Reduzierte Größe und Robustheit)"):
            daten = basis_daten(
                selected_handicaps=['Langsam_leicht', alt],
                selected_elements={'handicaps': {
                    'Langsam_leicht': {'ausgewaehlt': True, 'stufe': 'leicht', 'punkte': 1},
                    alt: {'name': alt, 'ausgewaehlt': True, 'stufe': 'leicht', 'punkte': 1},
                }},
            )
            migriere_charakter_daten(daten)
            self.assertEqual(daten['selected_handicaps'], ['Langsam_leicht', GROESSE_NEU])
            self.assertIn(GROESSE_NEU, daten['selected_elements']['handicaps'])
            self.assertEqual(
                daten['selected_elements']['handicaps'][GROESSE_NEU]['name'], GROESSE_NEU
            )
            self.assertNotIn(alt, daten['selected_elements']['handicaps'])

    def test_reihenfolge_der_handicaps_bleibt(self):
        daten = basis_daten(
            selected_elements={'handicaps': {
                'Feind_schwer': {},
                'Größe -1 (Reduzierte Robustheit)': {},
                'Zwanghaft': {},
            }},
        )
        migriere_charakter_daten(daten)
        self.assertEqual(list(daten['selected_elements']['handicaps']),
                         ['Feind_schwer', GROESSE_NEU, 'Zwanghaft'])

    def test_beide_alt_namen_gleichzeitig_ergeben_keinen_doppelten_eintrag(self):
        daten = basis_daten(
            selected_handicaps=['Größe -1 (Reduzierte Robustheit)',
                                'Größe -1 (Reduzierte Größe und Robustheit)'],
        )
        migriere_charakter_daten(daten)
        self.assertEqual(daten['selected_handicaps'], [GROESSE_NEU])

    def test_ist_wiederholbar(self):
        daten = basis_daten(selected_handicaps=['Größe -1 (Reduzierte Robustheit)'])
        migriere_charakter_daten(daten)
        migriere_charakter_daten(daten)
        self.assertEqual(daten['selected_handicaps'], [GROESSE_NEU])


class TestBerserkerMigration(unittest.TestCase):
    """Berserker gibt Stärke nur im Berserkerrausch — nicht dauerhaft"""

    def test_staerke_wird_um_einen_wuerfeltyp_gesenkt(self):
        daten = basis_daten(selected_talente=['Kräftig', 'Berserker'])
        self.assertTrue(migriere_charakter_daten(daten))
        self.assertEqual(daten['attribute']['Stärke']['wert'], 6)
        self.assertIn('berserker_temporaer', daten['migrationen'])

    def test_ueber_w12_wird_der_modifier_gesenkt(self):
        daten = basis_daten(
            selected_talente=['Berserker'],
            attribute={'Stärke': {'attribut_name': 'Stärke', 'wert': 12, 'modifier': 2}},
        )
        migriere_charakter_daten(daten)
        self.assertEqual(daten['attribute']['Stärke'],
                         {'attribut_name': 'Stärke', 'wert': 12, 'modifier': 1})

    def test_w4_bleibt_unveraendert(self):
        daten = basis_daten(
            selected_talente=['Berserker'],
            attribute={'Stärke': {'attribut_name': 'Stärke', 'wert': 4, 'modifier': 0}},
        )
        migriere_charakter_daten(daten)
        self.assertEqual(daten['attribute']['Stärke']['wert'], 4)

    def test_laeuft_nur_einmal(self):
        daten = basis_daten(selected_talente=['Berserker'])
        migriere_charakter_daten(daten)
        migriere_charakter_daten(daten)
        migriere_charakter_daten(daten)
        self.assertEqual(daten['attribute']['Stärke']['wert'], 6)

    def test_ohne_berserker_bleibt_staerke_gleich(self):
        daten = basis_daten(selected_talente=['Kräftig'])
        migriere_charakter_daten(daten)
        self.assertEqual(daten['attribute']['Stärke']['wert'], 8)
        self.assertIn('berserker_temporaer', daten['migrationen'])

    def test_bereits_migrierte_daten_bleiben_unberuehrt(self):
        daten = basis_daten(selected_talente=['Berserker'],
                            migrationen=list(MIGRATIONS_IDS))
        self.assertFalse(migriere_charakter_daten(daten))
        self.assertEqual(daten['attribute']['Stärke']['wert'], 8)


if __name__ == '__main__':
    unittest.main()
