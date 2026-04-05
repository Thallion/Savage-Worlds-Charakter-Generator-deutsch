# test units/test_setting_draft.py
"""
Unit Tests für SettingDraft und DraftManager (models/setting_draft.py).
Testet Serialisierung, Persistenz und Draft-Verwaltung.
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch
from pathlib import Path

# Kivy-Headless-Modus
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_LOG_LEVEL'] = 'critical'

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSettingDraft(unittest.TestCase):
    """Tests für die SettingDraft-Klasse."""

    def setUp(self):
        with patch('kivy.logger.Logger'):
            from models.setting_draft import SettingDraft
            self.SettingDraft = SettingDraft

    def test_init_minimal(self):
        """Minimale Initialisierung."""
        draft = self.SettingDraft(name="Test")
        self.assertEqual(draft.name, "Test")
        self.assertEqual(draft.mode, "template")
        self.assertEqual(draft.base_settings, [])
        self.assertEqual(draft.description, "")
        self.assertEqual(draft.current_step, 1)
        self.assertEqual(draft.setting_data, {})
        self.assertTrue(draft.is_draft)

    def test_init_vollstaendig(self):
        """Vollständige Initialisierung."""
        draft = self.SettingDraft(
            name="Mein Setting",
            mode="merge",
            base_settings=["SWAE", "Deadlands"],
            description="Testbeschreibung",
            current_step=3,
            setting_data={"talente": {"Kampf": {"aktiv": True}}},
            conflicts_resolved=2,
            conflicts_remaining=1
        )
        self.assertEqual(draft.name, "Mein Setting")
        self.assertEqual(draft.mode, "merge")
        self.assertEqual(len(draft.base_settings), 2)
        self.assertEqual(draft.current_step, 3)
        self.assertEqual(draft.conflicts_resolved, 2)

    def test_draft_filename(self):
        """Draft-Dateiname wird korrekt generiert."""
        draft = self.SettingDraft(name="Test Setting")
        self.assertEqual(draft.draft_filename, "_draft_Test Setting.json")

    def test_to_dict(self):
        """Serialisierung zu Dictionary."""
        draft = self.SettingDraft(
            name="Test",
            mode="empty",
            description="Desc",
            base_settings=["SWAE"],
            current_step=2,
            setting_data={"talente": {"Kampf": True}}
        )
        d = draft.to_dict()
        self.assertTrue(d["_draft"])
        self.assertEqual(d["name"], "Test")
        self.assertEqual(d["description"], "Desc")
        self.assertEqual(d["_mode"], "empty")
        self.assertEqual(d["_base_settings"], ["SWAE"])
        self.assertEqual(d["_current_step"], 2)
        self.assertIn("talente", d)

    def test_from_dict(self):
        """Deserialisierung aus Dictionary."""
        data = {
            "_draft": True,
            "_created": "2026-01-01T12:00:00",
            "_last_modified": "2026-01-02T12:00:00",
            "_base_settings": ["SWAE"],
            "_mode": "template",
            "_current_step": 3,
            "_conflicts_resolved": 1,
            "_conflicts_remaining": 0,
            "name": "Restored",
            "description": "Wiederhergestellt",
            "talente": {"Kampf": True},
            "handicaps": {"Blind": True}
        }
        draft = self.SettingDraft.from_dict(data)
        self.assertEqual(draft.name, "Restored")
        self.assertEqual(draft.mode, "template")
        self.assertEqual(draft.base_settings, ["SWAE"])
        self.assertEqual(draft.current_step, 3)
        self.assertEqual(draft.description, "Wiederhergestellt")
        self.assertIn("talente", draft.setting_data)
        self.assertIn("handicaps", draft.setting_data)

    def test_roundtrip_to_dict_from_dict(self):
        """Serialisierung und Deserialisierung ergeben gleiches Objekt."""
        original = self.SettingDraft(
            name="Roundtrip",
            mode="merge",
            base_settings=["A", "B"],
            description="Test",
            current_step=2,
            setting_data={"voelker": {"Elf": {"aktiv": True}}}
        )
        d = original.to_dict()
        restored = self.SettingDraft.from_dict(d)
        self.assertEqual(restored.name, original.name)
        self.assertEqual(restored.mode, original.mode)
        self.assertEqual(restored.base_settings, original.base_settings)
        self.assertEqual(restored.description, original.description)
        self.assertEqual(restored.current_step, original.current_step)

    def test_to_final_setting(self):
        """Konvertierung zu finalem Setting ohne Metadaten."""
        draft = self.SettingDraft(
            name="Final",
            description="Finales Setting",
            setting_data={
                "talente": {"Kampf": True},
                "_internal": "wird ignoriert",
                "voelker": {"Mensch": {}}
            }
        )
        final = draft.to_final_setting()
        self.assertEqual(final["name"], "Final")
        self.assertEqual(final["description"], "Finales Setting")
        self.assertIn("talente", final)
        self.assertIn("voelker", final)
        self.assertNotIn("_internal", final)
        self.assertNotIn("_draft", final)

    def test_update_timestamp(self):
        """Zeitstempel wird aktualisiert."""
        draft = self.SettingDraft(name="Test")
        old_timestamp = draft.last_modified
        import time
        time.sleep(0.01)
        draft.update_timestamp()
        self.assertNotEqual(draft.last_modified, old_timestamp)

    def test_from_dict_fehlende_felder(self):
        """Fehlende Felder bekommen Standardwerte."""
        data = {"name": "Minimal"}
        draft = self.SettingDraft.from_dict(data)
        self.assertEqual(draft.name, "Minimal")
        self.assertEqual(draft.mode, "template")
        self.assertEqual(draft.current_step, 1)
        self.assertEqual(draft.base_settings, [])


class TestDraftManager(unittest.TestCase):
    """Tests für die DraftManager-Klasse."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        with patch('kivy.logger.Logger'):
            from models.setting_draft import DraftManager, SettingDraft
            self.manager = DraftManager(drafts_dir=Path(self.temp_dir))
            self.SettingDraft = SettingDraft

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_draft(self, name="Test", mode="template", **kwargs):
        return self.SettingDraft(name=name, mode=mode, **kwargs)

    def test_save_draft(self):
        """Draft speichern."""
        draft = self._create_draft()
        result = self.manager.save_draft(draft)
        self.assertTrue(result)
        # Datei existiert
        self.assertTrue(self.manager.has_draft("Test"))

    def test_load_draft(self):
        """Draft laden."""
        draft = self._create_draft(name="Laden", description="Lade-Test")
        self.manager.save_draft(draft)
        self.manager.clear_cache()

        loaded = self.manager.load_draft("Laden")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, "Laden")
        self.assertEqual(loaded.description, "Lade-Test")

    def test_load_draft_nicht_vorhanden(self):
        """Nicht vorhandenen Draft laden gibt None."""
        result = self.manager.load_draft("Gibt es nicht")
        self.assertIsNone(result)

    def test_load_draft_aus_cache(self):
        """Draft wird aus Cache geladen."""
        draft = self._create_draft(name="Cache")
        self.manager.save_draft(draft)
        # Zweiter Aufruf sollte aus Cache kommen
        loaded = self.manager.load_draft("Cache")
        self.assertIsNotNone(loaded)

    def test_delete_draft(self):
        """Draft löschen."""
        draft = self._create_draft(name="Löschen")
        self.manager.save_draft(draft)
        result = self.manager.delete_draft("Löschen")
        self.assertTrue(result)
        self.assertFalse(self.manager.has_draft("Löschen"))

    def test_delete_draft_nicht_vorhanden(self):
        """Nicht vorhandenen Draft löschen gibt True (idempotent)."""
        result = self.manager.delete_draft("Gibt es nicht")
        self.assertTrue(result)

    def test_list_drafts_leer(self):
        """Leere Draft-Liste."""
        drafts = self.manager.list_drafts()
        self.assertEqual(len(drafts), 0)

    def test_list_drafts_mehrere(self):
        """Mehrere Drafts auflisten."""
        for name in ["Alpha", "Beta", "Gamma"]:
            self.manager.save_draft(self._create_draft(name=name))

        drafts = self.manager.list_drafts()
        self.assertEqual(len(drafts), 3)
        names = [d.name for d in drafts]
        self.assertIn("Alpha", names)
        self.assertIn("Beta", names)
        self.assertIn("Gamma", names)

    def test_list_drafts_sortiert_nach_datum(self):
        """Drafts werden nach Änderungsdatum sortiert (neueste zuerst)."""
        import time
        for name in ["Alt", "Mittel", "Neu"]:
            self.manager.save_draft(self._create_draft(name=name))
            time.sleep(0.02)

        drafts = self.manager.list_drafts()
        self.assertEqual(drafts[0].name, "Neu")
        self.assertEqual(drafts[-1].name, "Alt")

    def test_has_draft(self):
        """Draft-Existenz prüfen."""
        self.assertFalse(self.manager.has_draft("Test"))
        self.manager.save_draft(self._create_draft())
        self.assertTrue(self.manager.has_draft("Test"))

    def test_clear_cache(self):
        """Cache leeren."""
        self.manager.save_draft(self._create_draft())
        self.manager.clear_cache()
        self.assertEqual(len(self.manager._drafts_cache), 0)

    def test_get_draft_path(self):
        """Draft-Pfad generieren."""
        path = self.manager.get_draft_path("Test")
        self.assertTrue(str(path).endswith("_draft_Test.json"))

    def test_sanitize_filename(self):
        """Ungültige Zeichen im Dateinamen ersetzen."""
        safe = self.manager._sanitize_filename('Test<>:"/\\|?*Name')
        self.assertNotIn('<', safe)
        self.assertNotIn('>', safe)
        self.assertNotIn('"', safe)

    def test_roundtrip_json(self):
        """Vollständiger Roundtrip: erstellen → speichern → laden → prüfen."""
        original = self._create_draft(
            name="Roundtrip",
            mode="merge",
            base_settings=["SWAE", "Deadlands"],
            description="Roundtrip-Test",
            current_step=3,
            setting_data={"talente": {"Kampfmeister": {"aktiv": True}}}
        )
        self.manager.save_draft(original)
        self.manager.clear_cache()

        loaded = self.manager.load_draft("Roundtrip")
        self.assertEqual(loaded.name, "Roundtrip")
        self.assertEqual(loaded.mode, "merge")
        self.assertEqual(loaded.base_settings, ["SWAE", "Deadlands"])
        self.assertEqual(loaded.current_step, 3)
        self.assertIn("talente", loaded.setting_data)


class TestDraftHelperFunctions(unittest.TestCase):
    """Tests für die Hilfsfunktionen in setting_draft.py."""

    def test_create_empty_draft(self):
        """Leeren Draft erstellen."""
        with patch('kivy.logger.Logger'):
            from models.setting_draft import create_empty_draft
            draft = create_empty_draft("Leer", "Beschreibung")
            self.assertEqual(draft.name, "Leer")
            self.assertEqual(draft.mode, "empty")
            self.assertEqual(draft.description, "Beschreibung")
            # Leeres Template hat Grundstruktur
            self.assertIn("voelker", draft.setting_data)
            self.assertIn("attribute", draft.setting_data)
            self.assertIn("talente", draft.setting_data)
            self.assertIn("startgeld", draft.setting_data)

    def test_empty_draft_hat_5_attribute(self):
        """Leeres Template hat 5 Grundattribute."""
        with patch('kivy.logger.Logger'):
            from models.setting_draft import create_empty_draft
            draft = create_empty_draft("Test")
            attribute = draft.setting_data.get("attribute", {})
            self.assertEqual(len(attribute), 5)
            self.assertIn("Stärke", attribute)
            self.assertIn("Geschicklichkeit", attribute)
            self.assertIn("Konstitution", attribute)
            self.assertIn("Verstand", attribute)
            self.assertIn("Willenskraft", attribute)

    def test_empty_draft_startgeld(self):
        """Leeres Template hat Standard-Startgeld."""
        with patch('kivy.logger.Logger'):
            from models.setting_draft import create_empty_draft
            draft = create_empty_draft("Test")
            self.assertEqual(draft.setting_data.get("startgeld"), 500)


if __name__ == '__main__':
    unittest.main()
