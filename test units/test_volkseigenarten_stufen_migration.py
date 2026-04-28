"""
Tests für die Migration alter Stufen-IDs (vor Konsolidierung in Commit a335405).

Vor der Stufen-Konsolidierung waren `fliegen_stufe1`, `fliegen_stufe2` und
`fliegen_stufe3` separate Eigenarten-IDs. Nach der Konsolidierung gibt es
nur noch `fliegen` mit einem `stufen`-Array. Bestehende Custom-Volk-Saves
mit alten IDs müssen beim Öffnen im Wizard auf das neue Schema gemappt
werden, sonst zeigt der Wizard die Stufenauswahl als „nicht gewählt" an
und das Volk wäre nicht speicherbar.
"""

import unittest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.volkseigenarten_funktionen import (
    lade_eigenarten_fuer_bearbeitung,
    STUFEN_MIGRATIONS,
)


class TestStufenMigrationsTabelle(unittest.TestCase):
    """Stellt sicher, dass die Migrations-Tabelle alle erwarteten Einträge hat."""

    def test_alle_drei_fliegen_stufen_gemappt(self):
        self.assertIn('fliegen_stufe1', STUFEN_MIGRATIONS)
        self.assertIn('fliegen_stufe2', STUFEN_MIGRATIONS)
        self.assertIn('fliegen_stufe3', STUFEN_MIGRATIONS)

    def test_alle_eintraege_zeigen_auf_fliegen(self):
        for alt_id, mig in STUFEN_MIGRATIONS.items():
            if alt_id.startswith('fliegen_'):
                self.assertEqual(mig['neue_id'], 'fliegen')
                self.assertIn('stufe_label', mig)


class TestLadeEigenartenMitMigration(unittest.TestCase):
    """`lade_eigenarten_fuer_bearbeitung` muss alte IDs umschreiben und die
    Stufenwahl rekonstruieren."""

    def test_fliegen_stufe2_wird_zu_fliegen_mit_bw12(self):
        volk_dict = {
            'eigenarten': [
                {'id': 'fliegen_stufe2', 'typ': 'positiv', 'name': 'Fliegen', 'kosten': 4}
            ]
        }
        positive, negative = lade_eigenarten_fuer_bearbeitung(volk_dict)

        self.assertEqual(len(positive), 1)
        self.assertEqual(len(negative), 0)
        self.assertEqual(positive[0]['id'], 'fliegen')
        # Stufe muss gesetzt sein und auf BW 12 zeigen
        self.assertIn('ausgewaehlte_stufe', positive[0])
        stufe = positive[0]['ausgewaehlte_stufe']
        self.assertEqual(stufe.get('label'), 'Bewegungsweite 12')
        self.assertEqual(stufe.get('kosten'), 4)
        self.assertEqual(stufe.get('effekt', {}).get('bewegungsweite_flug'), 12)

    def test_fliegen_stufe1_wird_zu_fliegen_mit_bw6(self):
        volk_dict = {
            'eigenarten': [
                {'id': 'fliegen_stufe1', 'typ': 'positiv'}
            ]
        }
        positive, _ = lade_eigenarten_fuer_bearbeitung(volk_dict)

        self.assertEqual(positive[0]['id'], 'fliegen')
        self.assertEqual(positive[0]['ausgewaehlte_stufe']['label'], 'Bewegungsweite 6')
        self.assertEqual(positive[0]['kosten'], 2)

    def test_fliegen_stufe3_wird_zu_fliegen_mit_bw24(self):
        volk_dict = {
            'eigenarten': [
                {'id': 'fliegen_stufe3', 'typ': 'positiv'}
            ]
        }
        positive, _ = lade_eigenarten_fuer_bearbeitung(volk_dict)

        self.assertEqual(positive[0]['id'], 'fliegen')
        self.assertEqual(
            positive[0]['ausgewaehlte_stufe']['label'],
            'Bewegungsweite 24, Sprint 2W6',
        )

    def test_neue_fliegen_id_unveraendert(self):
        """Modernes Save mit `fliegen` + `ausgewaehlte_stufe` darf nicht doppelt
        migriert werden."""
        volk_dict = {
            'eigenarten': [
                {
                    'id': 'fliegen',
                    'typ': 'positiv',
                    'ausgewaehlte_stufe': {
                        'label': 'Bewegungsweite 12',
                        'kosten': 4,
                        'effekt': {'fliegen': True, 'bewegungsweite_flug': 12},
                    },
                }
            ]
        }
        positive, _ = lade_eigenarten_fuer_bearbeitung(volk_dict)
        self.assertEqual(positive[0]['id'], 'fliegen')
        self.assertEqual(
            positive[0]['ausgewaehlte_stufe']['label'], 'Bewegungsweite 12'
        )

    def test_unbekannte_id_bleibt_unberuehrt(self):
        """Eine ID, die weder in der Migrations-Tabelle noch in der Config ist,
        landet unverändert als Fallback-Eintrag in der Liste."""
        volk_dict = {
            'eigenarten': [
                {'id': 'voellig_unbekannt', 'typ': 'positiv', 'name': 'Test', 'kosten': 1}
            ]
        }
        positive, _ = lade_eigenarten_fuer_bearbeitung(volk_dict)
        self.assertEqual(len(positive), 1)
        self.assertEqual(positive[0]['id'], 'voellig_unbekannt')

    def test_gemischte_alte_und_neue_ids(self):
        """Ein Volk mit gemischten Eigenarten (alte Stufen-IDs + moderne IDs)
        wird vollständig korrekt geladen."""
        volk_dict = {
            'eigenarten': [
                {'id': 'fliegen_stufe2', 'typ': 'positiv'},
                {'id': 'nachtsicht', 'typ': 'positiv'},
                {'id': 'attributsschwäche', 'typ': 'negativ'},
            ]
        }
        positive, negative = lade_eigenarten_fuer_bearbeitung(volk_dict)
        self.assertEqual(len(positive), 2)
        self.assertEqual(len(negative), 1)
        ids_pos = {e['id'] for e in positive}
        self.assertIn('fliegen', ids_pos)
        self.assertIn('nachtsicht', ids_pos)
        # Migrierte Stufe ist gesetzt
        fliegen = next(e for e in positive if e['id'] == 'fliegen')
        self.assertEqual(fliegen['ausgewaehlte_stufe']['label'], 'Bewegungsweite 12')
        # Nicht-Stufen-Eigenart hat keine ausgewaehlte_stufe
        nachtsicht = next(e for e in positive if e['id'] == 'nachtsicht')
        self.assertNotIn('ausgewaehlte_stufe', nachtsicht)


if __name__ == '__main__':
    unittest.main()
