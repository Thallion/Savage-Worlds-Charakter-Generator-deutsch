# test units/test_superkraft_model.py
"""
Tests für das Superkraft-Datenmodell und die Superkraft-Funktionen.
Testet Phase 2 der Superkräfte-Implementierung:
- Superkraft Model (models/superkraft.py)
- SuperkraftModifikator
- Superkraft-Funktionen (functions/superkraft_funktionen.py)
- Persistenz-Integration
"""
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Kivy-Headless-Modus
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_LOG_LEVEL'] = 'critical'

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.superkraft import Superkraft, SuperkraftModifikator
import functions.superkraft_funktionen as skf


# ======================== SUPERKRAFT MODIFIKATOR TESTS ========================

class TestSuperkraftModifikator(unittest.TestCase):
    """Tests für die SuperkraftModifikator-Klasse"""

    def test_erstellen_mit_int_kosten(self):
        mod = SuperkraftModifikator("Test", 3, "Beschreibung")
        self.assertEqual(mod.name, "Test")
        self.assertEqual(mod.kosten, 3)
        self.assertEqual(mod.beschreibung, "Beschreibung")

    def test_erstellen_mit_negativen_kosten(self):
        mod = SuperkraftModifikator("Unbeholfen", -2, "Nachteil")
        self.assertEqual(mod.get_effektive_kosten(), -2)

    def test_effektive_kosten_int(self):
        mod = SuperkraftModifikator("Test", 5)
        self.assertEqual(mod.get_effektive_kosten(), 5)

    def test_effektive_kosten_string_einfach(self):
        mod = SuperkraftModifikator("Test", "3")
        self.assertEqual(mod.get_effektive_kosten(), 3)

    def test_effektive_kosten_string_alternativ(self):
        """Bei '2/4' wird der erste Wert (2) verwendet"""
        mod = SuperkraftModifikator("Test", "2/4")
        self.assertEqual(mod.get_effektive_kosten(), 2)

    def test_effektive_kosten_string_komplex(self):
        """Bei '1 pro 2 PB' wird 1 extrahiert"""
        mod = SuperkraftModifikator("Test", "1 pro 2 PB")
        self.assertEqual(mod.get_effektive_kosten(), 1)

    def test_effektive_kosten_string_negativ(self):
        mod = SuperkraftModifikator("Test", "-2")
        self.assertEqual(mod.get_effektive_kosten(), -2)

    def test_effektive_kosten_ungueltig(self):
        mod = SuperkraftModifikator("Test", "unbekannt")
        self.assertEqual(mod.get_effektive_kosten(), 0)

    def test_to_dict(self):
        mod = SuperkraftModifikator("Unbeholfen", -2, "Nachteil")
        d = mod.to_dict()
        self.assertEqual(d['name'], "Unbeholfen")
        self.assertEqual(d['kosten'], -2)
        self.assertEqual(d['beschreibung'], "Nachteil")

    def test_from_dict(self):
        data = {'name': 'Senkrechtstarter', 'kosten': 1, 'beschreibung': 'Kann starten'}
        mod = SuperkraftModifikator.from_dict(data)
        self.assertEqual(mod.name, "Senkrechtstarter")
        self.assertEqual(mod.kosten, 1)

    def test_roundtrip(self):
        """Serialisierung und Deserialisierung sind konsistent"""
        original = SuperkraftModifikator("Test", "2/4", "Beschreibung")
        restored = SuperkraftModifikator.from_dict(original.to_dict())
        self.assertEqual(original.name, restored.name)
        self.assertEqual(original.kosten, restored.kosten)
        self.assertEqual(original.beschreibung, restored.beschreibung)


# ======================== SUPERKRAFT MODEL TESTS ========================

class TestSuperkraft(unittest.TestCase):
    """Tests für die Superkraft-Klasse"""

    def test_erstellen_basic(self):
        kraft = Superkraft(name="Fliegen", kosten="2-18", beschreibung="Flugfähigkeit")
        self.assertEqual(kraft.name, "Fliegen")
        self.assertEqual(kraft.basis_kosten, "2-18")
        self.assertFalse(kraft.ausgewaehlt)
        self.assertTrue(kraft.aktiv)

    def test_erstellen_mit_modifikatoren(self):
        mods = {
            "Unbeholfen": {"kosten": -2, "beschreibung": "Nachteil"},
            "Senkrechtstarter": {"kosten": 1, "beschreibung": "Start"}
        }
        kraft = Superkraft(name="Fliegen", kosten="2-18", verfuegbare_modifikatoren=mods)
        self.assertEqual(len(kraft.verfuegbare_modifikatoren), 2)
        self.assertIn("Unbeholfen", kraft.verfuegbare_modifikatoren)

    def test_hat_variable_kosten_bereich(self):
        kraft = Superkraft(name="Fliegen", kosten="2-18")
        self.assertTrue(kraft.hat_variable_kosten())

    def test_hat_variable_kosten_alternativ(self):
        kraft = Superkraft(name="Test", kosten="2/4")
        self.assertTrue(kraft.hat_variable_kosten())

    def test_hat_variable_kosten_speziell(self):
        kraft = Superkraft(name="Test", kosten="speziell")
        self.assertTrue(kraft.hat_variable_kosten())

    def test_hat_feste_kosten(self):
        kraft = Superkraft(name="Furchtlos", kosten="2")
        self.assertFalse(kraft.hat_variable_kosten())

    def test_get_kosten_bereich_fest(self):
        kraft = Superkraft(name="Furchtlos", kosten="2")
        self.assertEqual(kraft.get_kosten_bereich(), (2, 2))

    def test_get_kosten_bereich_bereich(self):
        kraft = Superkraft(name="Fliegen", kosten="2-18")
        self.assertEqual(kraft.get_kosten_bereich(), (2, 18))

    def test_get_kosten_bereich_alternativ(self):
        kraft = Superkraft(name="Test", kosten="2/4")
        self.assertEqual(kraft.get_kosten_bereich(), (2, 4))

    def test_get_kosten_bereich_speziell(self):
        kraft = Superkraft(name="Test", kosten="speziell")
        self.assertEqual(kraft.get_kosten_bereich(), (0, 0))

    def test_get_feste_kosten(self):
        kraft = Superkraft(name="Furchtlos", kosten="2")
        self.assertEqual(kraft.get_feste_kosten(), 2)

    def test_get_feste_kosten_bei_variabel(self):
        kraft = Superkraft(name="Fliegen", kosten="2-18")
        self.assertEqual(kraft.get_feste_kosten(), 0)

    def test_gesamt_kosten_ohne_modifikatoren(self):
        kraft = Superkraft(name="Furchtlos", kosten="2")
        kraft.gewaehlte_kosten = 2
        self.assertEqual(kraft.gesamt_kosten, 2)

    def test_gesamt_kosten_mit_modifikatoren(self):
        kraft = Superkraft(name="Fliegen", kosten="2-18")
        kraft.gewaehlte_kosten = 6
        kraft.gewaehlte_modifikatoren = [
            SuperkraftModifikator("Unbeholfen", -2),
            SuperkraftModifikator("Senkrechtstarter", 1),
        ]
        self.assertEqual(kraft.gesamt_kosten, 5)  # 6 - 2 + 1

    def test_gesamt_kosten_minimum_null(self):
        """Gesamtkosten können nicht unter 0 fallen"""
        kraft = Superkraft(name="Test", kosten="1")
        kraft.gewaehlte_kosten = 1
        kraft.gewaehlte_modifikatoren = [
            SuperkraftModifikator("Rabatt", -5),
        ]
        self.assertEqual(kraft.gesamt_kosten, 0)


class TestSuperkraftAuswahl(unittest.TestCase):
    """Tests für Auswahl/Abwahl von Superkräften"""

    def test_auswaehlen_feste_kosten(self):
        kraft = Superkraft(name="Furchtlos", kosten="2")
        self.assertTrue(kraft.auswaehlen())
        self.assertTrue(kraft.ausgewaehlt)
        self.assertEqual(kraft.gewaehlte_kosten, 2)

    def test_auswaehlen_variable_kosten(self):
        kraft = Superkraft(name="Fliegen", kosten="2-18")
        self.assertTrue(kraft.auswaehlen(kosten=6))
        self.assertTrue(kraft.ausgewaehlt)
        self.assertEqual(kraft.gewaehlte_kosten, 6)

    def test_auswaehlen_doppelt(self):
        kraft = Superkraft(name="Furchtlos", kosten="2")
        kraft.auswaehlen()
        self.assertFalse(kraft.auswaehlen())

    def test_abwaehlen(self):
        kraft = Superkraft(name="Fliegen", kosten="2-18")
        kraft.auswaehlen(kosten=6)
        kraft.gewaehlte_modifikatoren = [SuperkraftModifikator("Test", 1)]
        self.assertTrue(kraft.abwaehlen())
        self.assertFalse(kraft.ausgewaehlt)
        self.assertEqual(kraft.gewaehlte_kosten, 0)
        self.assertEqual(len(kraft.gewaehlte_modifikatoren), 0)

    def test_abwaehlen_nicht_ausgewaehlt(self):
        kraft = Superkraft(name="Furchtlos", kosten="2")
        self.assertFalse(kraft.abwaehlen())


class TestSuperkraftModifikatoren(unittest.TestCase):
    """Tests für Modifikator-Verwaltung an Superkräften"""

    def setUp(self):
        self.kraft = Superkraft(
            name="Fliegen",
            kosten="2-18",
            verfuegbare_modifikatoren={
                "Unbeholfen": {"kosten": -2, "beschreibung": "Nachteil"},
                "Senkrechtstarter": {"kosten": 1, "beschreibung": "Start"},
                "Weltraumflug": {"kosten": 2, "beschreibung": "Weltraum"},
            }
        )
        self.kraft.auswaehlen(kosten=6)

    def test_modifikator_waehlen(self):
        self.assertTrue(self.kraft.waehle_modifikator("Unbeholfen"))
        self.assertEqual(len(self.kraft.gewaehlte_modifikatoren), 1)
        self.assertEqual(self.kraft.gesamt_kosten, 4)  # 6 - 2

    def test_modifikator_waehlen_unbekannt(self):
        self.assertFalse(self.kraft.waehle_modifikator("Unbekannt"))

    def test_modifikator_entfernen(self):
        self.kraft.waehle_modifikator("Senkrechtstarter")
        self.assertTrue(self.kraft.entferne_modifikator("Senkrechtstarter"))
        self.assertEqual(len(self.kraft.gewaehlte_modifikatoren), 0)

    def test_modifikator_entfernen_nicht_vorhanden(self):
        self.assertFalse(self.kraft.entferne_modifikator("Unbekannt"))

    def test_mehrere_modifikatoren(self):
        self.kraft.waehle_modifikator("Unbeholfen")
        self.kraft.waehle_modifikator("Senkrechtstarter")
        self.assertEqual(self.kraft.gesamt_kosten, 5)  # 6 - 2 + 1
        self.assertEqual(len(self.kraft.gewaehlte_modifikatoren), 2)


class TestSuperkraftSerialisierung(unittest.TestCase):
    """Tests für Serialisierung/Deserialisierung"""

    def test_to_dict(self):
        kraft = Superkraft(name="Fliegen", kosten="2-18", beschreibung="Fliegen!")
        kraft.auswaehlen(kosten=6)
        kraft.waehle_modifikator("Unbeholfen", -2, "Nachteil")
        d = kraft.to_dict()
        self.assertEqual(d['name'], "Fliegen")
        self.assertEqual(d['basis_kosten'], "2-18")
        self.assertEqual(d['gewaehlte_kosten'], 6)
        self.assertTrue(d['ausgewaehlt'])
        self.assertEqual(len(d['gewaehlte_modifikatoren']), 1)

    def test_from_dict(self):
        data = {
            'name': 'Furchtlos',
            'basis_kosten': '2',
            'beschreibung': 'Immun gegen Furcht',
            'gewaehlte_kosten': 2,
            'ausgewaehlt': True,
            'aktiv': True,
            'gewaehlte_modifikatoren': [],
            'verfuegbare_modifikatoren': {},
        }
        kraft = Superkraft.from_dict(data)
        self.assertEqual(kraft.name, "Furchtlos")
        self.assertEqual(kraft.basis_kosten, "2")
        self.assertTrue(kraft.ausgewaehlt)
        self.assertEqual(kraft.gewaehlte_kosten, 2)

    def test_from_dict_mit_modifikatoren(self):
        data = {
            'name': 'Fliegen',
            'basis_kosten': '2-18',
            'beschreibung': 'Fliegen',
            'gewaehlte_kosten': 6,
            'ausgewaehlt': True,
            'aktiv': True,
            'gewaehlte_modifikatoren': [
                {'name': 'Unbeholfen', 'kosten': -2, 'beschreibung': 'Nachteil'}
            ],
            'verfuegbare_modifikatoren': {},
        }
        kraft = Superkraft.from_dict(data)
        self.assertEqual(len(kraft.gewaehlte_modifikatoren), 1)
        self.assertEqual(kraft.gewaehlte_modifikatoren[0].name, "Unbeholfen")
        self.assertEqual(kraft.gesamt_kosten, 4)  # 6 - 2

    def test_from_setting_dict(self):
        """Erstellen aus Setting-JSON-Format"""
        data = {
            "name": "Fliegen",
            "kosten": "2-18",
            "beschreibung": "Flugfähigkeit",
            "modifikatoren": {
                "Unbeholfen": {"kosten": -2, "beschreibung": "Nachteil"}
            },
            "ausgewaehlt": False,
            "aktiv": True
        }
        kraft = Superkraft.from_setting_dict(data)
        self.assertEqual(kraft.name, "Fliegen")
        self.assertEqual(kraft.basis_kosten, "2-18")
        self.assertIn("Unbeholfen", kraft.verfuegbare_modifikatoren)
        self.assertFalse(kraft.ausgewaehlt)

    def test_roundtrip(self):
        """Vollständiger Serialisierungs-Roundtrip"""
        original = Superkraft(
            name="Fliegen",
            kosten="2-18",
            beschreibung="Fliegen!",
            verfuegbare_modifikatoren={
                "Unbeholfen": {"kosten": -2, "beschreibung": "Nachteil"},
            }
        )
        original.auswaehlen(kosten=6)
        original.waehle_modifikator("Unbeholfen")

        restored = Superkraft.from_dict(original.to_dict())
        self.assertEqual(original.name, restored.name)
        self.assertEqual(original.basis_kosten, restored.basis_kosten)
        self.assertEqual(original.gewaehlte_kosten, restored.gewaehlte_kosten)
        self.assertEqual(original.ausgewaehlt, restored.ausgewaehlt)
        self.assertEqual(original.gesamt_kosten, restored.gesamt_kosten)
        self.assertEqual(len(original.gewaehlte_modifikatoren),
                         len(restored.gewaehlte_modifikatoren))


# ======================== SUPERKRAFT FUNKTIONEN TESTS ========================

class MockCharakter:
    """Mock-Charakter für Funktions-Tests"""

    def __init__(self):
        self.superkraefte = {}
        self.selected_superkraefte = []
        self.superkraft_punkte_gesamt = 45
        self.superkraft_punkte_verbraucht = 0
        self.machtstufe = "III"
        self.kraftobergrenze = 15
        self.active_setting_name = "Superkräfte Kompendium"


class TestIstSuperkraefteSetting(unittest.TestCase):
    """Tests für Setting-Erkennung"""

    def test_superkraefte_kompendium(self):
        self.assertTrue(skf.ist_superkraefte_setting("Superkräfte Kompendium"))

    def test_superkraefte_kompendium_bindestrich(self):
        self.assertTrue(skf.ist_superkraefte_setting("Superkräfte-Kompendium"))

    def test_superheroes(self):
        self.assertTrue(skf.ist_superkraefte_setting("Superheroes"))

    def test_swae_nicht(self):
        self.assertFalse(skf.ist_superkraefte_setting("SWAE"))

    def test_leer(self):
        self.assertFalse(skf.ist_superkraefte_setting(""))


class TestMachtstufenDefaults(unittest.TestCase):
    """Tests für Machtstufen-Defaults"""

    def test_alle_stufen_vorhanden(self):
        for stufe in ["I", "II", "III", "IV", "V"]:
            self.assertIn(stufe, skf.MACHTSTUFEN_DEFAULTS)

    def test_stufe_i_werte(self):
        daten = skf.MACHTSTUFEN_DEFAULTS["I"]
        self.assertEqual(daten['superkraftpunkte'], 15)
        self.assertEqual(daten['kraftobergrenze'], 5)

    def test_stufe_iii_werte(self):
        daten = skf.MACHTSTUFEN_DEFAULTS["III"]
        self.assertEqual(daten['superkraftpunkte'], 45)
        self.assertEqual(daten['kraftobergrenze'], 15)

    def test_stufe_v_werte(self):
        daten = skf.MACHTSTUFEN_DEFAULTS["V"]
        self.assertEqual(daten['superkraftpunkte'], 75)
        self.assertEqual(daten['kraftobergrenze'], 25)

    def test_skp_steigt_monoton(self):
        stufen = ["I", "II", "III", "IV", "V"]
        for i in range(len(stufen) - 1):
            skp_a = skf.MACHTSTUFEN_DEFAULTS[stufen[i]]['superkraftpunkte']
            skp_b = skf.MACHTSTUFEN_DEFAULTS[stufen[i + 1]]['superkraftpunkte']
            self.assertLess(skp_a, skp_b)


class TestSetzeMachtstufe(unittest.TestCase):
    """Tests für Machtstufe setzen"""

    def setUp(self):
        self.char = MockCharakter()

    def test_setze_stufe_i(self):
        self.assertTrue(skf.setze_machtstufe(self.char, "I"))
        self.assertEqual(self.char.machtstufe, "I")
        self.assertEqual(self.char.superkraft_punkte_gesamt, 15)
        self.assertEqual(self.char.kraftobergrenze, 5)

    def test_setze_stufe_v(self):
        self.assertTrue(skf.setze_machtstufe(self.char, "V"))
        self.assertEqual(self.char.superkraft_punkte_gesamt, 75)
        self.assertEqual(self.char.kraftobergrenze, 25)

    def test_ungueltige_stufe(self):
        self.assertFalse(skf.setze_machtstufe(self.char, "VI"))
        # Werte sollten unverändert bleiben
        self.assertEqual(self.char.machtstufe, "III")


class TestInitialisiereSuperkraefte(unittest.TestCase):
    """Tests für Superkräfte-Initialisierung aus Setting-Daten"""

    def setUp(self):
        self.char = MockCharakter()

    def test_initialisiere_leer(self):
        skf.initialisiere_superkraefte(self.char, {})
        self.assertEqual(len(self.char.superkraefte), 0)

    def test_initialisiere_none(self):
        skf.initialisiere_superkraefte(self.char, None)
        self.assertEqual(len(self.char.superkraefte), 0)

    def test_initialisiere_mit_daten(self):
        daten = {
            "Fliegen": {
                "name": "Fliegen",
                "kosten": "2-18",
                "beschreibung": "Fliegen",
                "modifikatoren": {"Unbeholfen": {"kosten": -2, "beschreibung": "Nachteil"}},
                "ausgewaehlt": False,
                "aktiv": True
            },
            "Furchtlos": {
                "name": "Furchtlos",
                "kosten": 2,
                "beschreibung": "Immun",
                "modifikatoren": {},
                "ausgewaehlt": False,
                "aktiv": True
            }
        }
        skf.initialisiere_superkraefte(self.char, daten)
        self.assertEqual(len(self.char.superkraefte), 2)
        self.assertIn("Fliegen", self.char.superkraefte)
        self.assertIn("Furchtlos", self.char.superkraefte)
        self.assertEqual(self.char.superkraefte["Fliegen"].basis_kosten, "2-18")


class TestWaehleSuperkraft(unittest.TestCase):
    """Tests für Superkraft-Auswahl"""

    def setUp(self):
        self.char = MockCharakter()
        daten = {
            "Fliegen": {
                "name": "Fliegen", "kosten": "2-18", "beschreibung": "Fliegen",
                "modifikatoren": {}, "ausgewaehlt": False, "aktiv": True
            },
            "Furchtlos": {
                "name": "Furchtlos", "kosten": 2, "beschreibung": "Immun",
                "modifikatoren": {}, "ausgewaehlt": False, "aktiv": True
            },
            "Panzerung": {
                "name": "Panzerung", "kosten": "1-5", "beschreibung": "Schutz",
                "modifikatoren": {}, "ausgewaehlt": False, "aktiv": True
            },
        }
        skf.initialisiere_superkraefte(self.char, daten)

    def test_waehle_feste_kosten(self):
        result = skf.waehle_superkraft(self.char, "Furchtlos")
        self.assertTrue(result)
        self.assertTrue(self.char.superkraefte["Furchtlos"].ausgewaehlt)
        self.assertIn("Furchtlos", self.char.selected_superkraefte)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 2)

    def test_waehle_variable_kosten_ohne_angabe(self):
        result = skf.waehle_superkraft(self.char, "Fliegen")
        self.assertEqual(result, "needs_kosten")

    def test_waehle_variable_kosten_mit_angabe(self):
        result = skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        self.assertTrue(result)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 6)

    def test_waehle_unbekannte_kraft(self):
        result = skf.waehle_superkraft(self.char, "Unbekannt")
        self.assertFalse(result)

    def test_waehle_bereits_ausgewaehlt(self):
        skf.waehle_superkraft(self.char, "Furchtlos")
        result = skf.waehle_superkraft(self.char, "Furchtlos")
        self.assertFalse(result)

    def test_ueber_kraftobergrenze(self):
        """Kosten über Kraftobergrenze (15 bei Stufe III)"""
        result = skf.waehle_superkraft(self.char, "Fliegen", kosten=18)
        self.assertEqual(result, "ueber_obergrenze")

    def test_nicht_genug_skp(self):
        """Nicht genug SKP verfügbar"""
        self.char.superkraft_punkte_verbraucht = 44  # Nur 1 SKP übrig
        result = skf.waehle_superkraft(self.char, "Furchtlos")  # Kostet 2
        self.assertEqual(result, "nicht_genug_skp")

    def test_mehrere_kraefte_waehlen(self):
        skf.waehle_superkraft(self.char, "Furchtlos")  # 2 SKP
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)  # 6 SKP
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 8)
        self.assertEqual(len(self.char.selected_superkraefte), 2)


class TestEntferneSuperkraft(unittest.TestCase):
    """Tests für Superkraft-Entfernung"""

    def setUp(self):
        self.char = MockCharakter()
        daten = {
            "Furchtlos": {
                "name": "Furchtlos", "kosten": 2, "beschreibung": "Immun",
                "modifikatoren": {}, "ausgewaehlt": False, "aktiv": True
            },
            "Fliegen": {
                "name": "Fliegen", "kosten": "2-18", "beschreibung": "Fliegen",
                "modifikatoren": {}, "ausgewaehlt": False, "aktiv": True
            },
        }
        skf.initialisiere_superkraefte(self.char, daten)

    def test_entferne_superkraft(self):
        skf.waehle_superkraft(self.char, "Furchtlos")
        self.assertTrue(skf.entferne_superkraft(self.char, "Furchtlos"))
        self.assertFalse(self.char.superkraefte["Furchtlos"].ausgewaehlt)
        self.assertNotIn("Furchtlos", self.char.selected_superkraefte)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 0)

    def test_entferne_nicht_ausgewaehlt(self):
        self.assertFalse(skf.entferne_superkraft(self.char, "Furchtlos"))

    def test_entferne_unbekannt(self):
        self.assertFalse(skf.entferne_superkraft(self.char, "Unbekannt"))

    def test_skp_werden_zurueckgegeben(self):
        skf.waehle_superkraft(self.char, "Furchtlos")  # 2 SKP
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)  # 6 SKP
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 8)
        skf.entferne_superkraft(self.char, "Furchtlos")
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 6)


class TestModifikatorFunktionen(unittest.TestCase):
    """Tests für Modifikator-Verwaltung über Funktionen"""

    def setUp(self):
        self.char = MockCharakter()
        daten = {
            "Fliegen": {
                "name": "Fliegen", "kosten": "2-18", "beschreibung": "Fliegen",
                "modifikatoren": {
                    "Unbeholfen": {"kosten": -2, "beschreibung": "Nachteil"},
                    "Senkrechtstarter": {"kosten": 1, "beschreibung": "Start"},
                },
                "ausgewaehlt": False, "aktiv": True
            },
        }
        skf.initialisiere_superkraefte(self.char, daten)
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)

    def test_waehle_modifikator(self):
        result = skf.waehle_modifikator(self.char, "Fliegen", "Unbeholfen")
        self.assertTrue(result)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 4)  # 6 - 2

    def test_waehle_unbekannten_modifikator(self):
        result = skf.waehle_modifikator(self.char, "Fliegen", "Unbekannt")
        self.assertFalse(result)

    def test_waehle_modifikator_unbekannte_kraft(self):
        result = skf.waehle_modifikator(self.char, "Unbekannt", "Unbeholfen")
        self.assertFalse(result)

    def test_entferne_modifikator(self):
        skf.waehle_modifikator(self.char, "Fliegen", "Senkrechtstarter")
        result = skf.entferne_modifikator(self.char, "Fliegen", "Senkrechtstarter")
        self.assertTrue(result)
        self.assertEqual(self.char.superkraft_punkte_verbraucht, 6)

    def test_modifikator_ueber_obergrenze(self):
        """Modifikator der die Kraftobergrenze überschreitet"""
        # Kraft hat 6 SKP, Obergrenze ist 15 - setze Kosten knapp unter Grenze
        self.char.superkraefte["Fliegen"].gewaehlte_kosten = 15
        skf._aktualisiere_skp(self.char)  # Aktualisiere SKP
        result = skf.waehle_modifikator(self.char, "Fliegen", "Senkrechtstarter")
        self.assertEqual(result, "ueber_obergrenze")


class TestAusgewaehlteSuperkraefte(unittest.TestCase):
    """Tests für ausgewaehlte_superkraefte-Funktion"""

    def setUp(self):
        self.char = MockCharakter()
        daten = {
            "Furchtlos": {
                "name": "Furchtlos", "kosten": 2, "beschreibung": "Immun",
                "modifikatoren": {}, "ausgewaehlt": False, "aktiv": True
            },
            "Fliegen": {
                "name": "Fliegen", "kosten": "2-18", "beschreibung": "Fliegen",
                "modifikatoren": {}, "ausgewaehlt": False, "aktiv": True
            },
        }
        skf.initialisiere_superkraefte(self.char, daten)

    def test_keine_ausgewaehlt(self):
        result = skf.ausgewaehlte_superkraefte(self.char)
        self.assertEqual(len(result), 0)

    def test_eine_ausgewaehlt(self):
        skf.waehle_superkraft(self.char, "Furchtlos")
        result = skf.ausgewaehlte_superkraefte(self.char)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Furchtlos")

    def test_mehrere_ausgewaehlt(self):
        skf.waehle_superkraft(self.char, "Furchtlos")
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        result = skf.ausgewaehlte_superkraefte(self.char)
        self.assertEqual(len(result), 2)


class TestBerechnungen(unittest.TestCase):
    """Tests für Kostenberechnungen"""

    def setUp(self):
        self.char = MockCharakter()
        daten = {
            "Furchtlos": {
                "name": "Furchtlos", "kosten": 2, "beschreibung": "Immun",
                "modifikatoren": {}, "ausgewaehlt": False, "aktiv": True
            },
            "Fliegen": {
                "name": "Fliegen", "kosten": "2-18", "beschreibung": "Fliegen",
                "modifikatoren": {"Unbeholfen": {"kosten": -2, "beschreibung": "N"}},
                "ausgewaehlt": False, "aktiv": True
            },
        }
        skf.initialisiere_superkraefte(self.char, daten)

    def test_berechne_gesamt_kosten_leer(self):
        self.assertEqual(skf.berechne_gesamt_kosten(self.char), 0)

    def test_berechne_gesamt_kosten(self):
        skf.waehle_superkraft(self.char, "Furchtlos")
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        self.assertEqual(skf.berechne_gesamt_kosten(self.char), 8)

    def test_berechne_gesamt_kosten_mit_mod(self):
        skf.waehle_superkraft(self.char, "Fliegen", kosten=6)
        skf.waehle_modifikator(self.char, "Fliegen", "Unbeholfen")
        self.assertEqual(skf.berechne_gesamt_kosten(self.char), 4)  # 6 - 2

    def test_get_verbleibende_skp(self):
        self.assertEqual(skf.get_verbleibende_skp(self.char), 45)
        skf.waehle_superkraft(self.char, "Furchtlos")
        self.assertEqual(skf.get_verbleibende_skp(self.char), 43)

    def test_validiere_kraftobergrenze_ok(self):
        self.assertTrue(skf.validiere_kraftobergrenze(self.char, "Test", 15))

    def test_validiere_kraftobergrenze_ueber(self):
        self.assertFalse(skf.validiere_kraftobergrenze(self.char, "Test", 16))


class TestMachtstufenDaten(unittest.TestCase):
    """Tests für get_machtstufen_daten"""

    def test_ohne_custom_element_manager(self):
        """Fallback auf Defaults wenn kein Manager vorhanden"""
        char = MockCharakter()
        daten = skf.get_machtstufen_daten(char, "III")
        self.assertEqual(daten['superkraftpunkte'], 45)
        self.assertEqual(daten['kraftobergrenze'], 15)

    def test_unbekannte_stufe(self):
        char = MockCharakter()
        daten = skf.get_machtstufen_daten(char, "VI")
        # Fallback auf Stufe III
        self.assertEqual(daten['superkraftpunkte'], 45)

    def test_default_machtstufe(self):
        """Ohne explizite Stufe wird charakter.machtstufe verwendet"""
        char = MockCharakter()
        char.machtstufe = "I"
        daten = skf.get_machtstufen_daten(char)
        self.assertEqual(daten['superkraftpunkte'], 15)


class TestSuperkraftStr(unittest.TestCase):
    """Tests für String-Darstellung"""

    def test_str_einfach(self):
        kraft = Superkraft(name="Furchtlos", kosten="2")
        kraft.auswaehlen()
        text = str(kraft)
        self.assertIn("Furchtlos", text)
        self.assertIn("SKP", text)

    def test_str_mit_modifikatoren(self):
        kraft = Superkraft(name="Fliegen", kosten="2-18")
        kraft.auswaehlen(kosten=6)
        kraft.waehle_modifikator("Unbeholfen", -2, "Nachteil")
        text = str(kraft)
        self.assertIn("Fliegen", text)
        self.assertIn("Unbeholfen", text)

    def test_repr(self):
        kraft = Superkraft(name="Fliegen", kosten="2-18")
        text = repr(kraft)
        self.assertIn("Fliegen", text)
        self.assertIn("2-18", text)


if __name__ == '__main__':
    unittest.main()
