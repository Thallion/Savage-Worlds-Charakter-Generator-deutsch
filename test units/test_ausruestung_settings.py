"""
Test-Units für Ausrüstungs-Laden und -Berechnung aus allen Settings.

Diese Tests prüfen, dass die Ausrüstungsdaten in JEDEM Setting korrekt
geladen und berechnet werden können. Verhindert Crashes durch fehlerhafte
Daten (z.B. String-Werte bei kosten/gewicht).
"""

import unittest
from unittest.mock import Mock, patch
import sys
import json
from pathlib import Path

# Pfad zur Projektroot hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Imports der zu testenden Module
from functions.ausruestung_funktionen import (
    erstelle_item_nach_kategorie,
    berechne_gesamtkosten,
    berechne_gesamt_ruestungsschutz,
)

from config.ausruestung_config import (
    AusruestungKategorien,
    RuestungsKoerperteile,
)

from models.ausruestung import Ausruestung
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild


class TestAusruestungAusSettings(unittest.TestCase):
    """Tests, die alle Setting-JSONs automatisch durchgehen und Ausrüstung validieren."""

    @classmethod
    def setUpClass(cls):
        """Alle Setting-JSON-Dateien aus settings/ laden."""
        settings_dir = project_root / "settings"
        cls.settings = {}

        for setting_path in sorted(settings_dir.glob("*.json")):
            with open(setting_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            ausruestung = data.get("ausruestung", {})
            if ausruestung:
                cls.settings[setting_path.stem] = ausruestung

        # Sicherstellen, dass mindestens Settings gefunden wurden
        assert len(cls.settings) > 0, "Keine Setting-Dateien mit Ausrüstung gefunden!"

    def test_alle_settings_ausruestung_ladbar(self):
        """Für jedes Setting: Alle Ausrüstungsgegenstände via erstelle_item_nach_kategorie() erstellen."""
        for setting_name, ausruestung in self.settings.items():
            with self.subTest(setting=setting_name):
                for item_name, item_dict in ausruestung.items():
                    with self.subTest(item=item_name):
                        item = erstelle_item_nach_kategorie(item_dict)
                        self.assertIsNotNone(
                            item,
                            f"Item '{item_name}' in Setting '{setting_name}' konnte nicht erstellt werden"
                        )

    def test_alle_items_haben_numerische_werte(self):
        """kosten und gewicht sind numerisch (int/float), nicht String."""
        for setting_name, ausruestung in self.settings.items():
            with self.subTest(setting=setting_name):
                for item_name, item_dict in ausruestung.items():
                    with self.subTest(item=item_name):
                        item = erstelle_item_nach_kategorie(item_dict)
                        self.assertIsNotNone(item, f"Item '{item_name}' ist None")

                        self.assertIsInstance(
                            item.kosten, (int, float),
                            f"'{item_name}' in '{setting_name}': kosten={item.kosten!r} ist kein numerischer Wert"
                        )
                        self.assertIsInstance(
                            item.gewicht, (int, float),
                            f"'{item_name}' in '{setting_name}': gewicht={item.gewicht!r} ist kein numerischer Wert"
                        )

    def test_alle_items_haben_name(self):
        """Jedes Item hat einen nicht-leeren name."""
        for setting_name, ausruestung in self.settings.items():
            with self.subTest(setting=setting_name):
                for item_name, item_dict in ausruestung.items():
                    with self.subTest(item=item_name):
                        item = erstelle_item_nach_kategorie(item_dict)
                        self.assertIsNotNone(item, f"Item '{item_name}' ist None")
                        self.assertTrue(
                            item.name,
                            f"Item in '{setting_name}' hat keinen Namen"
                        )

    def test_gesamtkosten_berechenbar(self):
        """Mock-Charakter mit allen Items eines Settings füllen, berechne_gesamtkosten() aufrufen."""
        for setting_name, ausruestung in self.settings.items():
            with self.subTest(setting=setting_name):
                charakter = Mock()
                charakter.ausruestung = {}

                for item_name, item_dict in ausruestung.items():
                    item = erstelle_item_nach_kategorie(item_dict)
                    if item is not None:
                        item.menge = 1
                        item.ausgewaehlt = True
                        charakter.ausruestung[item.name] = item

                # Separate Listen dürfen nicht existieren (hasattr-Prüfung in berechne_gesamtkosten)
                del charakter.waffen
                del charakter.ruestungen
                del charakter.schilde

                kosten = berechne_gesamtkosten(charakter)
                self.assertIsInstance(
                    kosten, (int, float),
                    f"Gesamtkosten für '{setting_name}' sind nicht numerisch: {kosten!r}"
                )

    def test_gesamtgewicht_berechenbar(self):
        """Gesamtgewicht über alle Items eines Settings berechnen."""
        for setting_name, ausruestung in self.settings.items():
            with self.subTest(setting=setting_name):
                gesamtgewicht = 0.0

                for item_name, item_dict in ausruestung.items():
                    item = erstelle_item_nach_kategorie(item_dict)
                    if item is not None:
                        # Gewicht * Menge berechnen (wie CharakterEquipment es tun würde)
                        gewicht_beitrag = item.gewicht * 1  # Menge = 1
                        self.assertIsInstance(
                            gewicht_beitrag, (int, float),
                            f"Gewicht-Berechnung für '{item_name}' in '{setting_name}' fehlgeschlagen"
                        )
                        gesamtgewicht += gewicht_beitrag

                self.assertIsInstance(
                    gesamtgewicht, (int, float),
                    f"Gesamtgewicht für '{setting_name}' ist nicht numerisch: {gesamtgewicht!r}"
                )

    @patch('functions.ausruestung_funktionen.Logger')
    def test_ruestungsschutz_berechenbar(self, mock_logger):
        """berechne_gesamt_ruestungsschutz() aufrufen — kein Fehler, alle Körperteil-Werte numerisch."""
        for setting_name, ausruestung in self.settings.items():
            with self.subTest(setting=setting_name):
                charakter = Mock()
                charakter.ausruestung = {}

                for item_name, item_dict in ausruestung.items():
                    if item_dict.get("kategorie") == AusruestungKategorien.RUESTUNG:
                        item = erstelle_item_nach_kategorie(item_dict)
                        if item is not None:
                            item.angelegt = True
                            item.ausgewaehlt = True
                            charakter.ausruestung[item.name] = item

                schutz = berechne_gesamt_ruestungsschutz(charakter)

                self.assertIsInstance(schutz, dict)
                for koerperteil, wert in schutz.items():
                    self.assertIsInstance(
                        wert, (int, float),
                        f"Schutzwert für '{koerperteil}' in '{setting_name}' ist nicht numerisch: {wert!r}"
                    )


if __name__ == '__main__':
    unittest.main(verbosity=2)
