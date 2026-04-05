# test units/test_setting_merge.py
"""
Unit Tests für Setting-Merge-Logik (functions/setting_merge.py).
Testet Deep-Merge, Konflikterkennung, Statistiken und Formatierung.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Kivy-Headless-Modus
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_LOG_LEVEL'] = 'critical'

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDeepMerge(unittest.TestCase):
    """Tests für die _deep_merge Funktion."""

    def setUp(self):
        with patch('kivy.logger.Logger'):
            from functions.setting_merge import _deep_merge
            self._deep_merge = _deep_merge

    def test_merge_leere_dicts(self):
        """Merge zweier leerer Dictionaries."""
        result, conflicts = self._deep_merge({}, {}, "source", [])
        self.assertEqual(result, {})
        self.assertEqual(len(conflicts), 0)

    def test_merge_neuer_key(self):
        """Neuer Key wird hinzugefügt."""
        base = {"a": 1}
        overlay = {"b": 2}
        result, conflicts = self._deep_merge(base, overlay, "source", [])
        self.assertEqual(result["a"], 1)
        self.assertEqual(result["b"], 2)
        self.assertEqual(len(conflicts), 0)

    def test_merge_gleicher_wert(self):
        """Gleiche Werte erzeugen keinen Konflikt."""
        base = {"a": 1}
        overlay = {"a": 1}
        result, conflicts = self._deep_merge(base, overlay, "source", [])
        self.assertEqual(result["a"], 1)
        self.assertEqual(len(conflicts), 0)

    def test_merge_unterschiedlicher_wert_erzeugt_konflikt(self):
        """Unterschiedliche Werte erzeugen einen Konflikt."""
        base = {"startgeld": 500}
        overlay = {"startgeld": 1000}
        result, conflicts = self._deep_merge(base, overlay, "Setting B", [])
        self.assertEqual(result["startgeld"], 1000)  # Neuer Wert gewinnt
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["type"], "value_mismatch")
        self.assertEqual(conflicts[0]["key"], "startgeld")

    def test_merge_nested_dicts(self):
        """Verschachtelte Dictionaries werden rekursiv gemergt."""
        base = {"talente": {"Kampf": True}}
        overlay = {"talente": {"Magie": True}}
        result, conflicts = self._deep_merge(base, overlay, "source", [])
        self.assertIn("Kampf", result["talente"])
        self.assertIn("Magie", result["talente"])

    def test_merge_listen(self):
        """Listen werden zusammengeführt."""
        base = {"items": ["a", "b"]}
        overlay = {"items": ["b", "c"]}
        result, conflicts = self._deep_merge(base, overlay, "source", [])
        self.assertIn("a", result["items"])
        self.assertIn("b", result["items"])
        self.assertIn("c", result["items"])

    def test_merge_interne_keys_ignoriert(self):
        """Keys mit _ Prefix werden nicht überschrieben wenn schon vorhanden."""
        base = {"_internal": "base"}
        overlay = {"_internal": "overlay"}
        result, conflicts = self._deep_merge(base, overlay, "source", [])
        self.assertEqual(result["_internal"], "base")

    def test_merge_interne_keys_hinzugefuegt(self):
        """Neue interne Keys werden hinzugefügt."""
        base = {}
        overlay = {"_new_internal": "value"}
        result, conflicts = self._deep_merge(base, overlay, "source", [])
        self.assertEqual(result["_new_internal"], "value")


class TestMergeLists(unittest.TestCase):
    """Tests für die _merge_lists Funktion."""

    def setUp(self):
        with patch('kivy.logger.Logger'):
            from functions.setting_merge import _merge_lists
            self._merge_lists = _merge_lists

    def test_merge_string_listen(self):
        """String-Listen werden ohne Duplikate zusammengeführt."""
        result = self._merge_lists(["a", "b"], ["b", "c"], "cat", "source", [])
        self.assertEqual(len(result), 3)
        self.assertIn("a", result)
        self.assertIn("c", result)

    def test_merge_dict_listen_mit_name(self):
        """Dict-Listen mit name-Key werden intelligent gemergt."""
        base = [{"name": "Elf", "bonus": 1}]
        overlay = [{"name": "Zwerg", "bonus": 2}]
        result = self._merge_lists(base, overlay, "voelker", "source", [])
        names = [i["name"] for i in result]
        self.assertIn("Elf", names)
        self.assertIn("Zwerg", names)

    def test_merge_dict_listen_ueberschreibt_duplikate(self):
        """Duplikate in Dict-Listen werden überschrieben."""
        base = [{"name": "Elf", "version": 1}]
        overlay = [{"name": "Elf", "version": 2}]
        conflicts = []
        result = self._merge_lists(base, overlay, "voelker", "source", conflicts)
        # Nur ein Elf im Ergebnis
        elfs = [i for i in result if isinstance(i, dict) and i.get("name") == "Elf"]
        self.assertEqual(len(elfs), 1)
        self.assertEqual(elfs[0]["version"], 2)
        # Konflikt wurde erkannt
        self.assertGreater(len(conflicts), 0)

    def test_merge_leere_listen(self):
        """Leere Listen ergeben leere Liste."""
        result = self._merge_lists([], [], "cat", "source", [])
        self.assertEqual(result, [])


class TestHelperFunctions(unittest.TestCase):
    """Tests für Hilfsfunktionen."""

    def setUp(self):
        with patch('kivy.logger.Logger'):
            from functions.setting_merge import (
                _find_by_key, _get_key, _detect_conflict,
                _resolve_conflict_default, _is_active
            )
            self._find_by_key = _find_by_key
            self._get_key = _get_key
            self._detect_conflict = _detect_conflict
            self._resolve_conflict_default = _resolve_conflict_default
            self._is_active = _is_active

    def test_find_by_key_gefunden(self):
        """Element anhand des Schlüssels finden."""
        items = [{"name": "Elf"}, {"name": "Zwerg"}]
        result = self._find_by_key(items, "Zwerg")
        self.assertEqual(result["name"], "Zwerg")

    def test_find_by_key_nicht_gefunden(self):
        """Nicht vorhandener Key gibt None."""
        items = [{"name": "Elf"}]
        result = self._find_by_key(items, "Ork")
        self.assertIsNone(result)

    def test_get_key_dict_name(self):
        """Key aus Dict mit name extrahieren."""
        self.assertEqual(self._get_key({"name": "Elf"}), "Elf")

    def test_get_key_dict_id(self):
        """Key aus Dict mit id extrahieren."""
        self.assertEqual(self._get_key({"id": "123"}), "123")

    def test_get_key_string(self):
        """Key aus String extrahieren."""
        self.assertEqual(self._get_key("test"), "test")

    def test_get_key_andere_typen(self):
        """Andere Typen geben None."""
        self.assertIsNone(self._get_key(42))
        self.assertIsNone(self._get_key(None))

    def test_detect_conflict_gleiche_werte(self):
        """Gleiche Werte ergeben keinen Konflikt."""
        result = self._detect_conflict("key", 1, 1, "source")
        self.assertIsNone(result)

    def test_detect_conflict_unterschiedliche_werte(self):
        """Unterschiedliche Werte ergeben einen Konflikt."""
        result = self._detect_conflict("startgeld", 500, 1000, "Setting B")
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "value_mismatch")
        self.assertEqual(result["old_value"], 500)
        self.assertEqual(result["new_value"], 1000)

    def test_resolve_conflict_default(self):
        """Standard-Konfliktlösung verwendet neuen Wert."""
        result = self._resolve_conflict_default("alt", "neu")
        self.assertEqual(result, "neu")

    def test_is_active_dict_aktiv(self):
        """Dict mit aktiv=True ist aktiv."""
        self.assertTrue(self._is_active({"aktiv": True, "name": "Test"}))

    def test_is_active_dict_inaktiv(self):
        """Dict mit aktiv=False ist inaktiv."""
        self.assertFalse(self._is_active({"aktiv": False}))

    def test_is_active_dict_ohne_feld(self):
        """Dict ohne aktiv-Feld ist standardmäßig aktiv."""
        self.assertTrue(self._is_active({"name": "Test"}))

    def test_is_active_nicht_dict(self):
        """Nicht-Dict ist standardmäßig aktiv."""
        self.assertTrue(self._is_active("test"))
        self.assertTrue(self._is_active(42))


class TestCalculateSettingStatistics(unittest.TestCase):
    """Tests für calculate_setting_statistics."""

    def setUp(self):
        with patch('kivy.logger.Logger'):
            from functions.setting_merge import calculate_setting_statistics
            self.calculate = calculate_setting_statistics

    def test_leeres_setting(self):
        """Leeres Setting ergibt Nullen."""
        stats = self.calculate({})
        for cat in ["Völker", "Fertigkeiten", "Talente", "Handicaps", "Mächte", "Ausrüstung"]:
            self.assertEqual(stats[cat]["gesamt"], 0)

    def test_dict_elemente(self):
        """Dict-Elemente werden gezählt."""
        data = {
            "talente": {
                "Kampf": {"aktiv": True},
                "Magie": {"aktiv": True},
                "Tanz": {"aktiv": False},
            }
        }
        stats = self.calculate(data)
        self.assertEqual(stats["Talente"]["gesamt"], 3)
        self.assertEqual(stats["Talente"]["aktiv"], 2)
        self.assertEqual(stats["Talente"]["inaktiv"], 1)

    def test_list_elemente(self):
        """Listen-Elemente zählen alle als aktiv."""
        data = {"voelker": ["Mensch", "Elf", "Zwerg"]}
        stats = self.calculate(data)
        self.assertEqual(stats["Völker"]["gesamt"], 3)
        self.assertEqual(stats["Völker"]["aktiv"], 3)
        self.assertEqual(stats["Völker"]["inaktiv"], 0)

    def test_fertigkeiten_daten_fallback(self):
        """fertigkeiten_daten wird als Fallback für fertigkeiten verwendet."""
        data = {
            "fertigkeiten_daten": {
                "Kämpfen": {"aktiv": True},
                "Schießen": {"aktiv": True},
            }
        }
        stats = self.calculate(data)
        self.assertEqual(stats["Fertigkeiten"]["gesamt"], 2)

    def test_alle_kategorien_vorhanden(self):
        """Alle 6 Kategorien sind immer im Ergebnis."""
        stats = self.calculate({"talente": {"X": True}})
        expected = ["Völker", "Fertigkeiten", "Talente", "Handicaps", "Mächte", "Ausrüstung"]
        for cat in expected:
            self.assertIn(cat, stats)


class TestFormatStatisticsForDisplay(unittest.TestCase):
    """Tests für format_statistics_for_display."""

    def setUp(self):
        with patch('kivy.logger.Logger'):
            from functions.setting_merge import format_statistics_for_display
            self.format = format_statistics_for_display

    def test_nur_aktive(self):
        """Nur aktive Elemente zeigen einfache Zahl."""
        stats = {"Talente": {"aktiv": 5, "inaktiv": 0, "gesamt": 5}}
        result = self.format(stats)
        self.assertEqual(result, "Talente: 5")

    def test_mit_inaktiven(self):
        """Aktive und inaktive Elemente zeigen Details."""
        stats = {"Talente": {"aktiv": 3, "inaktiv": 2, "gesamt": 5}}
        result = self.format(stats)
        self.assertIn("3 aktiv", result)
        self.assertIn("2 inaktiv", result)

    def test_mehrere_kategorien(self):
        """Mehrere Kategorien werden zeilenweise formatiert."""
        stats = {
            "Völker": {"aktiv": 5, "inaktiv": 0, "gesamt": 5},
            "Talente": {"aktiv": 10, "inaktiv": 2, "gesamt": 12},
        }
        result = self.format(stats)
        lines = result.split("\n")
        self.assertEqual(len(lines), 2)

    def test_leere_stats(self):
        """Leere Stats ergeben leeren String."""
        result = self.format({})
        self.assertEqual(result, "")


class TestMergeConflicts(unittest.TestCase):
    """Tests für Konflikt-Management."""

    def setUp(self):
        with patch('kivy.logger.Logger'):
            from functions.setting_merge import get_merge_conflicts, resolve_conflict
            self.get_conflicts = get_merge_conflicts
            self.resolve = resolve_conflict

    def test_get_conflicts_ohne_konflikte(self):
        """Setting ohne Konflikte gibt leere Liste."""
        result = self.get_conflicts({"talente": {}})
        self.assertEqual(result, [])

    def test_get_conflicts_mit_konflikten(self):
        """Konflikte aus gemertem Setting extrahieren."""
        merged = {"_merge_conflicts": [{"type": "value_mismatch"}]}
        result = self.get_conflicts(merged)
        self.assertEqual(len(result), 1)

    def test_resolve_conflict_valid(self):
        """Gültigen Konflikt lösen."""
        merged = {"_merge_conflicts": [
            {"type": "value_mismatch", "key": "startgeld"}
        ]}
        result = self.resolve(merged, 0, "keep_old")
        conflicts = self.get_conflicts(result)
        self.assertEqual(conflicts[0]["resolved"], "keep_old")

    def test_resolve_conflict_ungueltig(self):
        """Ungültiger Konflikt-Index wird ignoriert."""
        merged = {"_merge_conflicts": []}
        result = self.resolve(merged, 99, "keep_old")
        self.assertEqual(result, merged)


class TestMergeSettings(unittest.TestCase):
    """Tests für die Hauptfunktion merge_settings."""

    def setUp(self):
        with patch('kivy.logger.Logger'):
            from functions.setting_merge import merge_settings
            self.merge = merge_settings

    def test_leere_liste(self):
        """Leere Setting-Liste ergibt leeres Dict."""
        result = self.merge([])
        self.assertEqual(result, {})

    @patch('functions.setting_merge._load_single_setting')
    def test_einzelnes_setting(self, mock_load):
        """Einzelnes Setting wird direkt zurückgegeben."""
        mock_load.return_value = {"talente": {"Kampf": True}}
        result = self.merge(["SWAE"])
        self.assertIn("talente", result)

    @patch('functions.setting_merge._load_single_setting')
    def test_merge_zweier_settings(self, mock_load):
        """Zwei Settings werden zusammengeführt."""
        mock_load.side_effect = [
            {"talente": {"Kampf": True}, "startgeld": 500},
            {"talente": {"Magie": True}, "startgeld": 500},
        ]
        result = self.merge(["A", "B"])
        self.assertIn("Kampf", result["talente"])
        self.assertIn("Magie", result["talente"])
        self.assertIn("_merge_conflicts", result)

    @patch('functions.setting_merge._load_single_setting')
    def test_merge_mit_konflikten(self, mock_load):
        """Merge mit widersprüchlichen Werten erzeugt Konflikte."""
        mock_load.side_effect = [
            {"startgeld": 500},
            {"startgeld": 1000},
        ]
        result = self.merge(["A", "B"])
        conflicts = result.get("_merge_conflicts", [])
        self.assertGreater(len(conflicts), 0)


if __name__ == '__main__':
    unittest.main()
