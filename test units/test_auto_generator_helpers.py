#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests für die neuen Auto-Generator Helfer:
- Unicode-normalisierungs-Matching (_resolve_key)
- Historie-Aufbau (_historie_dict + _add_historie_entry)
- race_choices-Pfad im Schema (Legacy free_race_edge bleibt erhalten)
"""

import sys
import unittest
from pathlib import Path

PROJEKT_VERZ = Path(__file__).parent.parent
sys.path.insert(0, str(PROJEKT_VERZ))


class NormalizeAndResolveTests(unittest.TestCase):
    """Tests für _normalize_key und _resolve_key."""

    def setUp(self):
        # Import hier, damit Test-Discovery einen klaren Fehlerpfad zeigt,
        # falls Kivy-Imports scheitern.
        from functions.auto_character_generator import AutoCharacterGenerator
        self.generator = AutoCharacterGenerator()

    def test_normalize_strips_umlauts_and_case(self):
        n = self.generator._normalize_key
        # NFKD zerlegt Umlaute. Die Implementierung ist tolerant gegenüber Case.
        self.assertEqual(n("Kämpfen"), n("kämpfen"))
        self.assertEqual(n("  Heilen  "), n("Heilen"))

    def test_resolve_exact_match_wins(self):
        keys = ["Kämpfen", "Kämpfer", "Heilen"]
        # Exakter Match muss "Kämpfen" zurückgeben – nicht "Kämpfer".
        self.assertEqual(self.generator._resolve_key(keys, "Kämpfen"), "Kämpfen")

    def test_resolve_case_insensitive(self):
        keys = ["Kämpfen", "Heilen"]
        self.assertEqual(self.generator._resolve_key(keys, "kämpfen"), "Kämpfen")

    def test_resolve_umlaut_insensitive(self):
        keys = ["Kämpfen", "Heilen", "Überreden"]
        # 'Ueberreden' ohne Umlaut-Entsprechung trifft 'Überreden' via NFKD.
        # Das ist wichtig für Templates, die manuell ohne Umlaute getippt wurden.
        resolved = self.generator._resolve_key(keys, "uberreden")
        self.assertEqual(resolved, "Überreden")

    def test_resolve_does_not_confuse_kaempfen_and_kaempfer(self):
        # Der alte Substring-Match (".lower() in ...") traf bei "Kämpfen"
        # fälschlicherweise "Kämpfer" – das wollen wir mit _resolve_key fixen.
        keys = ["Kämpfer", "Heilen"]
        # "Kämpfen" existiert nicht -> darf NICHT aus Versehen "Kämpfer" treffen.
        self.assertIsNone(self.generator._resolve_key(keys, "Kämpfen"))

    def test_resolve_returns_none_for_unknown(self):
        self.assertIsNone(self.generator._resolve_key(["Heilen"], "Völlig Anderes"))


class HistorieDictTests(unittest.TestCase):
    """Tests für _historie_dict / _add_historie_entry."""

    def setUp(self):
        from functions.auto_character_generator import AutoCharacterGenerator
        self.generator = AutoCharacterGenerator()
        self.generator._reset_historie()

    def test_empty_historie_has_expected_shape(self):
        d = self.generator._historie_dict()
        self.assertIn("session_start", d)
        self.assertIn("entries", d)
        self.assertEqual(d["entries"], [])

    def test_entries_receive_timestamp_and_phase(self):
        self.generator._add_historie_entry("charakter_erstellt", {"name": "Test"})
        d = self.generator._historie_dict()
        self.assertEqual(len(d["entries"]), 1)
        entry = d["entries"][0]
        self.assertEqual(entry["type"], "charakter_erstellt")
        self.assertIn("timestamp", entry)
        self.assertIn("details", entry)
        # phase-Default kommt aus _current_phase
        self.assertEqual(entry["details"].get("phase"), "generierung")
        self.assertTrue(entry["details"].get("auto_generated"))

    def test_entries_preserve_insertion_order(self):
        self.generator._add_historie_entry("a", {})
        self.generator._add_historie_entry("b", {})
        self.generator._add_historie_entry("c", {})
        types = [e["type"] for e in self.generator._historie_dict()["entries"]]
        self.assertEqual(types, ["a", "b", "c"])


class TemplateSchemaTests(unittest.TestCase):
    """Stellt sicher, dass das Schema den neuen race_choices-Block kennt."""

    def test_schema_contains_race_choices(self):
        import json
        schema_path = PROJEKT_VERZ / "templates" / "character_template_schema.json"
        with schema_path.open(encoding="utf-8") as f:
            schema = json.load(f)
        props = schema["properties"]
        self.assertIn("race_choices", props)
        race_choices_props = props["race_choices"]["properties"]
        # Die wichtigsten Keys müssen dokumentiert sein.
        for key in ("freies_talent", "freies_attribut",
                    "freies_talent_oder_attribut_modus",
                    "freies_talent_oder_attribut_wert",
                    "attribut_staerke_oder_konstitution",
                    "freie_verstandsfertigkeit"):
            self.assertIn(key, race_choices_props, f"Schema-Key fehlt: {key}")

    def test_schema_keeps_legacy_free_race_edge(self):
        """free_race_edge bleibt als Legacy-Feld erhalten (alte Templates)."""
        import json
        schema_path = PROJEKT_VERZ / "templates" / "character_template_schema.json"
        with schema_path.open(encoding="utf-8") as f:
            schema = json.load(f)
        self.assertIn("free_race_edge", schema["properties"])


if __name__ == "__main__":
    unittest.main()
