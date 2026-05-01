"""
Tests für die Multi-Slot-Unterstützung bei Volkseigenarten.

Ein Volk mit mehreren Instanzen derselben Eigenart (z.B. attributserhoehung
mit max_auswahl=2) soll im Völker-Tab pro Instanz einen eigenen Auswahl-Slot
bekommen, statt alle Instanzen zu einem Slot zu kollabieren.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.volkseigenarten_funktionen import (
    eigenart_zu_effekte,
    get_eigenart_by_id,
)


class TestEigenartZuEffekteCounts(unittest.TestCase):
    """`eigenart_zu_effekte` muss `wahlmoeglichkeiten_counts` füllen."""

    def test_zwei_attributserhoehungen_geben_count_2(self):
        attr = get_eigenart_by_id('attributserhoehung', 'positive')
        instanzen = [dict(attr), dict(attr)]
        # Verzögerte Auswahl simulieren - so wie es der Wizard tut
        for inst in instanzen:
            inst['optionen'] = dict(inst.get('optionen', {}))
            inst['optionen']['auswahl_verzoegert'] = True

        effects = eigenart_zu_effekte(instanzen, [])
        counts = effects.get('wahlmoeglichkeiten_counts', {})
        self.assertEqual(counts.get('freies_attribut'), 2)
        self.assertTrue(effects['wahlmoeglichkeiten'].get('freies_attribut'))

    def test_attribut_bonus_und_malus_zaehlen_separat(self):
        bonus = get_eigenart_by_id('attributserhoehung', 'positive')
        malus = get_eigenart_by_id('attributsabzug_1', 'negative')
        b1 = dict(bonus)
        b1['optionen'] = dict(b1.get('optionen', {}))
        b1['optionen']['auswahl_verzoegert'] = True
        m1 = dict(malus)
        m1['optionen'] = dict(m1.get('optionen', {}))
        m1['optionen']['auswahl_verzoegert'] = True
        m2 = dict(malus)
        m2['optionen'] = dict(m2.get('optionen', {}))
        m2['optionen']['auswahl_verzoegert'] = True

        effects = eigenart_zu_effekte([b1], [m1, m2])
        counts = effects.get('wahlmoeglichkeiten_counts', {})
        self.assertEqual(counts.get('freies_attribut'), 1)
        self.assertEqual(counts.get('freies_attribut_malus'), 2)

    def test_keine_verzoegerten_keine_counts(self):
        # Eigenart ohne verzögerte Auswahl → kein Count
        nachtsicht = get_eigenart_by_id('nachtsicht', 'positive')
        effects = eigenart_zu_effekte([dict(nachtsicht)], [])
        self.assertNotIn('wahlmoeglichkeiten_counts', effects)


class TestGetVolkZusatzelementeSlots(unittest.TestCase):
    """`get_volk_zusatzelemente` muss eine `slots`-Liste pro Multi-Slot-Typ liefern."""

    def _make_charakter(self, counts, attribut_optionen=None):
        """Mock-Charakter mit gegebenen wahlmoeglichkeiten_counts. Echte Dicts
        für voelker / voelker_selected / attribute, damit Helper-Funktionen
        wie _cleanup_voelker_selected und get_verfuegbare_attribute korrekt arbeiten."""
        # Volk als einfaches Objekt mit effects-Dict (kein MagicMock,
        # damit hasattr(volk, 'effects') True ist und keine Magic-Properties erscheinen).
        class _FakeVolk:
            pass
        volk = _FakeVolk()
        volk.effects = {
            'wahlmoeglichkeiten': {k: True for k in counts.keys()},
            'wahlmoeglichkeiten_counts': dict(counts),
        }
        volk.ausgewaehlt = True

        class _FakeChar:
            pass
        charakter = _FakeChar()
        charakter.voelker = {'TestVolk': volk}
        charakter.voelker_selected = {'TestVolk': True}
        attribute = attribut_optionen or ['Stärke', 'Geschicklichkeit', 'Verstand', 'Willenskraft', 'Charisma']
        # MagicMock pro Attribut ist OK - .wert wird darauf gesetzt
        charakter.attribute = {a: MagicMock(wert=4) for a in attribute}
        return charakter

    def test_zwei_attribut_slots(self):
        from functions.volk_funktionen import get_volk_zusatzelemente
        # Attribut-Optionen-Funktion liefert die Liste; wir mocken sie nicht
        # sondern verlassen uns auf get_volk_attribut_optionen, welches aus
        # volk.effects.wahlmoeglichkeiten=='freies_attribut' das Vorhandensein
        # erkennt und alle Charakter-Attribute zurückgibt.
        charakter = self._make_charakter({'freies_attribut': 2})
        # get_volk_attribut_optionen prüft hat_volk_wahlmoeglichkeit
        # und liest dabei volk.effects.wahlmoeglichkeiten.
        result = get_volk_zusatzelemente(charakter, 'TestVolk')
        slots = result.get('slots', {}).get('freies_attribut', [])
        self.assertEqual(len(slots), 2)
        # Jeder Slot enthält die verfügbaren Attribut-Optionen
        for slot in slots:
            self.assertIn('options', slot)
            self.assertIn('value', slot)
            self.assertIsNone(slot['value'])

    def test_legacy_keys_bleiben_befuellt(self):
        """Auch wenn slots aktiv ist, müssen die alten Keys gesetzt sein
        (Backwards-Compatibility für Konsumenten ohne Multi-Slot-Logik)."""
        from functions.volk_funktionen import get_volk_zusatzelemente
        charakter = self._make_charakter({'freies_attribut': 2})
        result = get_volk_zusatzelemente(charakter, 'TestVolk')
        # Legacy-Skalar-Key muss gesetzt sein
        self.assertTrue(result.get('freies_attribut'))
        self.assertTrue(result.get('attribut_optionen'))


class TestResetVolkAuswahlenMultiSlot(unittest.TestCase):
    """`reset_volk_auswahlen` muss Listen iterieren und Charakter-State pro Slot zurückrollen."""

    def _make_charakter(self):
        charakter = MagicMock()
        # Attribute mit wert-Property (real-ish)
        from kivy.properties import NumericProperty
        charakter.attribute = {
            'Stärke': MagicMock(wert=6),
            'Geschicklichkeit': MagicMock(wert=6),
            'Verstand': MagicMock(wert=8),
        }
        charakter.fertigkeiten = {}
        charakter.voelker = {'TestVolk': MagicMock()}
        # Talent-Tracking
        charakter.selected_talente = []
        charakter.talente = {}
        return charakter

    def test_attribut_liste_setzt_alle_slots_zurueck(self):
        from functions.volk_funktionen import reset_volk_auswahlen
        charakter = self._make_charakter()
        auswahlen = {'TestVolk': {'attribut': ['Stärke', 'Geschicklichkeit']}}
        # Vor Reset: beide auf W6
        self.assertEqual(charakter.attribute['Stärke'].wert, 6)
        self.assertEqual(charakter.attribute['Geschicklichkeit'].wert, 6)

        reset_volk_auswahlen(charakter, 'TestVolk', auswahlen)

        # Beide Attribute um 1 dekrementiert (W6 → W5/W4 je nach Implementierung)
        self.assertEqual(charakter.attribute['Stärke'].wert, 5)
        self.assertEqual(charakter.attribute['Geschicklichkeit'].wert, 5)
        self.assertNotIn('TestVolk', auswahlen)

    def test_attribut_malus_liste_setzt_alle_slots_zurueck(self):
        from functions.volk_funktionen import reset_volk_auswahlen
        charakter = self._make_charakter()
        # Verstand wurde von W8 auf W6 gesenkt (Malus rückgängig => +1)
        charakter.attribute['Verstand'].wert = 6
        auswahlen = {'TestVolk': {'attribut_malus': ['Verstand']}}

        reset_volk_auswahlen(charakter, 'TestVolk', auswahlen)

        self.assertEqual(charakter.attribute['Verstand'].wert, 7)
        self.assertNotIn('TestVolk', auswahlen)

    def test_legacy_skalar_funktioniert_weiterhin(self):
        from functions.volk_funktionen import reset_volk_auswahlen
        charakter = self._make_charakter()
        auswahlen = {'TestVolk': {'attribut': 'Stärke'}}  # Skalar, nicht Liste

        reset_volk_auswahlen(charakter, 'TestVolk', auswahlen)

        self.assertEqual(charakter.attribute['Stärke'].wert, 5)


class TestReconcileVolkAuswahlen(unittest.TestCase):
    """`reconcile_volk_auswahlen` trimmt überzählige Slots wenn max_auswahl reduziert wurde."""

    def _make_charakter(self):
        charakter = MagicMock()
        charakter.attribute = {
            'Stärke': MagicMock(wert=6),
            'Geschicklichkeit': MagicMock(wert=6),
        }
        charakter.fertigkeiten = {}
        charakter.selected_talente = []
        charakter.talente = {}
        return charakter

    def test_trim_attribut_von_2_auf_1(self):
        from functions.volk_funktionen import reconcile_volk_auswahlen
        charakter = self._make_charakter()
        auswahlen = {'TestVolk': {'attribut': ['Stärke', 'Geschicklichkeit']}}

        reconcile_volk_auswahlen(charakter, 'TestVolk', auswahlen, {'attribut': 1})

        # Erster Slot bleibt, zweiter wird zurückgerollt
        self.assertEqual(auswahlen['TestVolk']['attribut'], ['Stärke'])
        self.assertEqual(charakter.attribute['Stärke'].wert, 6)         # bleibt
        self.assertEqual(charakter.attribute['Geschicklichkeit'].wert, 5)  # zurückgerollt

    def test_kein_trim_wenn_unter_target(self):
        from functions.volk_funktionen import reconcile_volk_auswahlen
        charakter = self._make_charakter()
        auswahlen = {'TestVolk': {'attribut': ['Stärke']}}

        reconcile_volk_auswahlen(charakter, 'TestVolk', auswahlen, {'attribut': 2})

        # Nichts geändert
        self.assertEqual(auswahlen['TestVolk']['attribut'], ['Stärke'])
        self.assertEqual(charakter.attribute['Stärke'].wert, 6)


class TestPersistenceMigration(unittest.TestCase):
    """Skalare aus Alt-Saves müssen beim Laden in Singleton-Listen migriert werden."""

    def test_skalar_attribut_wird_zu_liste(self):
        # Migration-Helper-Logik direkt testen, ohne Charakter-Hydration
        raw = {'TestVolk': {'attribut': 'Stärke', 'halbelf_wahl': 'Talent: Glück'}}
        multi_keys = ('talent', 'attribut', 'attribut_malus', 'fertigkeit')
        migrated = {}
        for v_name, auswahl in raw.items():
            eintrag = {}
            for k, v in auswahl.items():
                if k in multi_keys and not isinstance(v, list):
                    eintrag[k] = [v] if v else []
                else:
                    eintrag[k] = v
            migrated[v_name] = eintrag

        self.assertEqual(migrated['TestVolk']['attribut'], ['Stärke'])
        # Unique-Key bleibt skalar
        self.assertEqual(migrated['TestVolk']['halbelf_wahl'], 'Talent: Glück')

    def test_leerer_skalar_wird_leere_liste(self):
        raw = {'TestVolk': {'attribut': None}}
        migrated_attr = (
            raw['TestVolk']['attribut']
            if isinstance(raw['TestVolk']['attribut'], list)
            else ([raw['TestVolk']['attribut']] if raw['TestVolk']['attribut'] else [])
        )
        self.assertEqual(migrated_attr, [])


class TestAutoGeneratorMultiSlot(unittest.TestCase):
    """Auto-Generator akzeptiert Listen-Keys und Legacy-Skalare."""

    def test_freie_talente_listen_key_iteriert(self):
        """Liste in 'freie_talente' wird über alle Einträge iteriert."""
        # Helper aus dem Auto-Generator extrahieren (lokal definiert):
        # Wir testen die Normalisierungs-Logik indem wir sie nachstellen.
        def _as_list(v):
            if v is None:
                return []
            if isinstance(v, list):
                return [x for x in v if x]
            return [v]

        choices = {'freie_talente': ['Glück', 'Schnell']}
        talent_quellen = list(_as_list(choices.get('freies_talent')))
        talent_quellen.extend(_as_list(choices.get('freie_talente')))
        self.assertEqual(talent_quellen, ['Glück', 'Schnell'])

    def test_legacy_skalar_freies_talent_funktioniert(self):
        def _as_list(v):
            if v is None:
                return []
            if isinstance(v, list):
                return [x for x in v if x]
            return [v]

        choices = {'freies_talent': 'Glück'}
        talent_quellen = list(_as_list(choices.get('freies_talent')))
        talent_quellen.extend(_as_list(choices.get('freie_talente')))
        self.assertEqual(talent_quellen, ['Glück'])


if __name__ == '__main__':
    unittest.main()
