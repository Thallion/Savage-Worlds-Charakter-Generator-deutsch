#!/usr/bin/env python3
"""
Test-Unit für functions.volk_funktionen.
Testet alle 55 Funktionen mit Mock-Charakter-Objekten.
"""

import unittest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class MockWuerfel:
    def __init__(self, value=4, modifier=0):
        self.value = value
        self.modifier = modifier


class MockAttribut:
    def __init__(self, name, wert=4, modifier=0):
        self.name = name
        self.wert = wert
        self.modifier = modifier
        self.wuerfel = MockWuerfel(value=wert, modifier=modifier)


class MockAttributRef:
    def __init__(self, attribut_name):
        self.attribut_name = attribut_name


class MockFertigkeit:
    def __init__(self, name, wert=4, modifier=0, attribut_name=None):
        self.name = name
        self.wert = wert
        self.modifier = modifier
        self.ausgewaehlt = False
        self.wuerfel = MockWuerfel(value=wert, modifier=modifier)
        self.attribut = MockAttributRef(attribut_name) if attribut_name else None


class MockTalent:
    def __init__(self, name, aktiv=True, ausgewaehlt=False, rang=0):
        self.name = name
        self.aktiv = aktiv
        self.ausgewaehlt = ausgewaehlt
        self.beschreibung = ""
        self.voraussetzungen = []
        self.rang = rang


class MockVolk:
    def __init__(self, name, effects=None):
        self.name = name
        self.ausgewaehlt = False
        self.effects = effects or {'wahlmoeglichkeiten': {}, 'spezielle_effekte': []}

    def apply_effects_to_charakter(self, charakter):
        return True

    def remove_effects_from_charakter(self, charakter):
        return True

    def has_wahlmoeglichkeit(self, typ):
        return self.effects.get('wahlmoeglichkeiten', {}).get(typ, False)


class MockCharakter:
    def __init__(self):
        self.attribute = {}
        self.fertigkeiten = {}
        self.talente = {}
        self.voelker = {}
        self.voelker_selected = {}
        self.selected_talente = []
        self._menschen_freies_attribut = None
        self._menschen_freies_talent = None
        self._halbelf_freies_talent = None
        self._halbelf_attribut_gewaehlt = False
        self._mensch_fertigkeitspunkte_gewaehlt = False
        self.verbleibende_fertigkeitssteigerungen = 0
        self.maximale_fertigkeitssteigerungen = 0

    def berechne_abgeleitete_werte(self):
        pass

    def dispatch(self, event):
        pass


class TestIstAhTalent(unittest.TestCase):
    """Tests für _ist_ah_talent"""

    def test_ah_talent_positiv(self):
        from functions.volk_funktionen import _ist_ah_talent
        self.assertTrue(_ist_ah_talent("AH (Wunder)"))
        self.assertTrue(_ist_ah_talent("AH: Magie"))

    def test_kein_ah_talent(self):
        from functions.volk_funktionen import _ist_ah_talent
        self.assertFalse(_ist_ah_talent("Kampf"))
        self.assertFalse(_ist_ah_talent(""))
        self.assertFalse(_ist_ah_talent(None))


class TestExtrahiereArkaneFertigkeit(unittest.TestCase):
    """Tests für extrahiere_arkane_fertigkeit_aus_ah"""

    def test_aus_beschreibung(self):
        from functions.volk_funktionen import extrahiere_arkane_fertigkeit_aus_ah
        talent = MockTalent("AH (Wunder)")
        talent.beschreibung = "Arkane Fertigkeit: Glaube (Willenskraft)"
        result = extrahiere_arkane_fertigkeit_aus_ah(talent)
        self.assertEqual(result, "Glaube")

    def test_aus_voraussetzungen(self):
        from functions.volk_funktionen import extrahiere_arkane_fertigkeit_aus_ah
        talent = MockTalent("AH (Magie)")
        talent.beschreibung = ""
        talent.voraussetzungen = ["Glaube W6", "Willenskraft W8"]
        result = extrahiere_arkane_fertigkeit_aus_ah(talent)
        self.assertEqual(result, "Glaube")

    def test_fallback(self):
        from functions.volk_funktionen import extrahiere_arkane_fertigkeit_aus_ah
        talent = MockTalent("AH (Wunder)")
        talent.beschreibung = ""
        talent.voraussetzungen = []
        result = extrahiere_arkane_fertigkeit_aus_ah(talent)
        self.assertEqual(result, "Glaube")

    def test_none_talent(self):
        from functions.volk_funktionen import extrahiere_arkane_fertigkeit_aus_ah
        self.assertIsNone(extrahiere_arkane_fertigkeit_aus_ah(None))


class TestVolkAuswahl(unittest.TestCase):
    """Tests für Völker-Auswahl-Funktionen"""

    def setUp(self):
        self.char = MockCharakter()
        self.mensch = MockVolk("Mensch", {
            'wahlmoeglichkeiten': {'freies_attribut': True}
        })
        self.goblin = MockVolk("Goblin", {
            'wahlmoeglichkeiten': {'freies_talent': True}
        })
        self.char.voelker = {"Mensch": self.mensch, "Goblin": self.goblin}
        self.char.voelker_selected = {"Mensch": False, "Goblin": False}

    def test_waehle_volk(self):
        from functions.volk_funktionen import waehle_volk
        result = waehle_volk(self.char, "Mensch")
        self.assertTrue(result)
        self.assertTrue(self.char.voelker_selected["Mensch"])

    def test_abwaehlen_volk(self):
        from functions.volk_funktionen import abwaehlen_volk, waehle_volk
        waehle_volk(self.char, "Mensch")
        result = abwaehlen_volk(self.char, "Mensch")
        self.assertTrue(result)
        self.assertFalse(self.char.voelker_selected["Mensch"])

    def test_get_selected_volk(self):
        from functions.volk_funktionen import get_selected_volk, waehle_volk
        waehle_volk(self.char, "Mensch")
        result = get_selected_volk(self.char)
        self.assertEqual(result.name, "Mensch")

    def test_get_selected_volk_none(self):
        from functions.volk_funktionen import get_selected_volk
        result = get_selected_volk(self.char)
        self.assertIsNone(result)

    def test_cleanup_voelker_selected(self):
        from functions.volk_funktionen import _cleanup_voelker_selected
        self.char.voelker_selected["Verwaist"] = True
        _cleanup_voelker_selected(self.char)
        self.assertNotIn("Verwaist", self.char.voelker_selected)
        self.assertIn("Mensch", self.char.voelker_selected)


class TestWahlmoeglichkeiten(unittest.TestCase):
    """Tests für hat_volk_wahlmoeglichkeit"""

    def setUp(self):
        self.char = MockCharakter()
        self.volk = MockVolk("Mensch", {
            'wahlmoeglichkeiten': {'freies_attribut': True}
        })
        self.char.voelker = {"Mensch": self.volk}
        self.char.voelker_selected = {}

    def test_hat_wahlmoeglichkeit(self):
        from functions.volk_funktionen import hat_volk_wahlmoeglichkeit
        self.assertTrue(hat_volk_wahlmoeglichkeit(self.char, "Mensch", "freies_attribut"))

    def test_hat_keine_wahlmoeglichkeit(self):
        from functions.volk_funktionen import hat_volk_wahlmoeglichkeit
        zwerg = MockVolk("Zwerg", {'wahlmoeglichkeiten': {'freies_attribut': True}})
        self.char.voelker["Zwerg"] = zwerg
        self.assertFalse(hat_volk_wahlmoeglichkeit(self.char, "Zwerg", "freies_talent"))

    def test_goblin_freies_talent(self):
        from functions.volk_funktionen import hat_volk_wahlmoeglichkeit
        goblin = MockVolk("Goblin", {
            'wahlmoeglichkeiten': {'freies_talent': True}
        })
        self.char.voelker["Goblin"] = goblin
        self.assertTrue(hat_volk_wahlmoeglichkeit(self.char, "Goblin", "freies_talent"))

    def test_mensch_freies_talent(self):
        from functions.volk_funktionen import hat_volk_wahlmoeglichkeit
        mensch = MockVolk("Mensch", {'wahlmoeglichkeiten': {}})
        self.char.voelker["Mensch"] = mensch
        self.assertTrue(hat_volk_wahlmoeglichkeit(self.char, "Mensch", "freies_anfaengertalent"))


class TestFreieTalente(unittest.TestCase):
    """Tests für freie Talent-Funktionen"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.talente = {
            "Kampf": MockTalent("Kampf", aktiv=True, ausgewaehlt=False),
            "Athletik": MockTalent("Athletik", aktiv=True, ausgewaehlt=True),
            "Heimlichkeit": MockTalent("Heimlichkeit", aktiv=False, ausgewaehlt=False),
        }

    def test_get_freie_talente(self):
        from functions.volk_funktionen import get_freie_talente
        result = get_freie_talente(self.char)
        self.assertIn("Kampf", result)

    def test_get_freie_talente_keine(self):
        from functions.volk_funktionen import get_freie_talente
        self.char.talente = {}
        result = get_freie_talente(self.char)
        self.assertIn("Keine freien Talente verfügbar", result)


class TestVerfuegbareAttribute(unittest.TestCase):
    """Tests für Attribut-Funktionen"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.attribute = {
            "Stärke": MockAttribut("Stärke", wert=4),
            "Geschicklichkeit": MockAttribut("Geschicklichkeit", wert=6),
            "Konstitution": MockAttribut("Konstitution", wert=4),
        }

    def test_get_verfuegbare_attribute(self):
        from functions.volk_funktionen import get_verfuegbare_attribute
        result = get_verfuegbare_attribute(self.char)
        self.assertIn("Stärke", result)
        self.assertIn("Geschicklichkeit", result)

    def test_get_absenkbare_attribute(self):
        from functions.volk_funktionen import get_absenkbare_attribute
        result = get_absenkbare_attribute(self.char)
        self.assertIn("Geschicklichkeit", result)
        self.assertNotIn("Stärke", result)

    def test_get_staerkbare_attribute(self):
        from functions.volk_funktionen import get_staerkbare_attribute
        result = get_staerkbare_attribute(self.char)
        self.assertIn("Stärke", result)

    def test_get_staerkbare_attribute_mit_malus(self):
        from functions.volk_funktionen import get_staerkbare_attribute
        self.char.attribute = {
            "Stärke": MockAttribut("Stärke", wert=4, modifier=0),
            "Konstitution": MockAttribut("Konstitution", wert=4, modifier=-2),
        }
        result = get_staerkbare_attribute(self.char)
        self.assertNotIn("Konstitution", result)


class TestVerfuegbareFertigkeiten(unittest.TestCase):
    """Tests für Fertigkeits-Funktionen"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.fertigkeiten = {
            "Allgemeinwissen": MockFertigkeit("Allgemeinwissen"),
            "Athletik": MockFertigkeit("Athletik"),
        }

    def test_get_verfuegbare_fertigkeiten(self):
        from functions.volk_funktionen import get_verfuegbare_fertigkeiten
        self.char.fertigkeiten = {
            "Allgemeinwissen": MockFertigkeit("Allgemeinwissen", attribut_name="Verstand"),
            "Athletik": MockFertigkeit("Athletik", attribut_name="Stärke"),
        }
        result = get_verfuegbare_fertigkeiten(self.char)
        self.assertIn("Allgemeinwissen", result)

    def test_get_verfuegbare_fertigkeiten_keine(self):
        from functions.volk_funktionen import get_verfuegbare_fertigkeiten
        self.char.fertigkeiten = {}
        result = get_verfuegbare_fertigkeiten(self.char)
        self.assertIn("Keine Fertigkeiten verfügbar", result)


class TestWaehleFreiesAttribut(unittest.TestCase):
    """Tests für waehle_freies_attribut"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.attribute = {
            "Stärke": MockAttribut("Stärke", wert=4),
        }

    def test_waehle_freies_attribut(self):
        from functions.volk_funktionen import waehle_freies_attribut
        result = waehle_freies_attribut(self.char, "Mensch", "Stärke")
        self.assertTrue(result)
        self.assertEqual(self.char.attribute["Stärke"].wert, 6)


class TestWaehleFreiesAttributMalus(unittest.TestCase):
    """Tests für waehle_freies_attribut_malus (Attributsschwäche)"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.attribute = {
            "Stärke": MockAttribut("Stärke", wert=4, modifier=0),
        }

    def test_waehle_freies_attribut_malus(self):
        from functions.volk_funktionen import waehle_freies_attribut_malus
        result = waehle_freies_attribut_malus(self.char, "Mensch", "Stärke")
        self.assertTrue(result)
        self.assertEqual(self.char.attribute["Stärke"].wuerfel.modifier, -2)
        self.assertEqual(self.char.attribute["Stärke"].wert, 4)


class TestWaehleFreiesAttributMalusUmkehr(unittest.TestCase):
    """Tests für reset_volk_auswahlen mit attribut_malus"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.attribute = {
            "Stärke": MockAttribut("Stärke", wert=4, modifier=0),
        }

    def test_reset_volk_auswahlen_malus(self):
        from functions.volk_funktionen import waehle_freies_attribut_malus, reset_volk_auswahlen
        waehle_freies_attribut_malus(self.char, "Mensch", "Stärke")
        self.assertEqual(self.char.attribute["Stärke"].wuerfel.modifier, -2)
        auswahlen_dict = {"Mensch": {"attribut_malus": ["Stärke"]}}
        result = reset_volk_auswahlen(self.char, "Mensch", auswahlen_dict)
        self.assertTrue(result)


class TestWaehleFreieFertigkeit(unittest.TestCase):
    """Tests für waehle_freie_fertigkeit"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.fertigkeiten = {
            "Allgemeinwissen": MockFertigkeit("Allgemeinwissen", wert=4, modifier=0),
        }

    def test_waehle_freie_fertigkeit_grund(self):
        from functions.volk_funktionen import waehle_freie_fertigkeit
        result = waehle_freie_fertigkeit(self.char, "Mensch", "Allgemeinwissen")
        self.assertTrue(result)
        self.assertEqual(self.char.fertigkeiten["Allgemeinwissen"].wert, 6)


class TestMagieaffin(unittest.TestCase):
    """Tests für Magieaffin-Funktionen"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.fertigkeiten = {
            "Glaube": MockFertigkeit("Glaube", wert=4, modifier=-2),
        }
        self.char.talente = {
            "AH (Wunder)": MockTalent("AH (Wunder)", aktiv=True, ausgewaehlt=False),
        }
        elf = MockVolk("Elf", {
            'wahlmoeglichkeiten': {},
            'spezielle_effekte': [{'typ': 'magieaffin', 'wert': True}]
        })
        mensch = MockVolk("Mensch", {'wahlmoeglichkeiten': {}, 'spezielle_effekte': []})
        self.char.voelker = {"Elf": elf, "Mensch": mensch}
        self.char.voelker_selected = {}

    def test_waehle_magieaffin_fertigkeit(self):
        from functions.volk_funktionen import waehle_magieaffin_fertigkeit
        result = waehle_magieaffin_fertigkeit(self.char, "Elf", "AH (Wunder)")
        self.assertTrue(result)
        self.assertEqual(self.char.fertigkeiten["Glaube"].wuerfel.modifier, 0)

    def test_get_magieaffin_optionen(self):
        from functions.volk_funktionen import get_magieaffin_optionen
        result = get_magieaffin_optionen(self.char, "Elf")
        self.assertTrue(len(result) > 0)

    def test_hat_volk_magieaffin(self):
        from functions.volk_funktionen import hat_volk_magieaffin
        self.assertTrue(hat_volk_magieaffin(self.char, "Elf"))
        self.assertFalse(hat_volk_magieaffin(self.char, "Mensch"))

    def test_get_aktuelle_magieaffin_fertigkeit(self):
        from functions.volk_funktionen import get_aktuelle_magieaffin_fertigkeit
        self.assertIsNone(get_aktuelle_magieaffin_fertigkeit(self.char, "Elf"))


class TestVolkAttributOptionen(unittest.TestCase):
    """Tests für get_volk_attribut_optionen"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.attribute = {
            "Stärke": MockAttribut("Stärke", wert=4),
            "Konstitution": MockAttribut("Konstitution", wert=4),
        }

    def test_halbork_attribut_optionen(self):
        from functions.volk_funktionen import get_volk_attribut_optionen
        volk = MockVolk("Halbork", {
            'wahlmoeglichkeiten': {'attribut_staerke_oder_konstitution': True}
        })
        self.char.voelker = {"Halbork": volk}
        result = get_volk_attribut_optionen(self.char, "Halbork")
        self.assertIn("Stärke", result)
        self.assertIn("Konstitution", result)

    def test_freies_attribut(self):
        from functions.volk_funktionen import get_volk_attribut_optionen
        volk = MockVolk("Mensch", {
            'wahlmoeglichkeiten': {'freies_attribut': True}
        })
        self.char.voelker = {"Mensch": volk}
        result = get_volk_attribut_optionen(self.char, "Mensch")
        self.assertIn("Stärke", result)


class TestVolkZusatzelemente(unittest.TestCase):
    """Tests für get_volk_zusatzelemente"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.attribute = {
            "Stärke": MockAttribut("Stärke", wert=4),
        }
        self.volk = MockVolk("Mensch", {
            'wahlmoeglichkeiten': {'freies_attribut': True, 'freies_talent': True}
        })
        self.char.voelker = {"Mensch": self.volk}
        self.char.voelker_selected = {}

    def test_get_volk_zusatzelemente(self):
        from functions.volk_funktionen import get_volk_zusatzelemente
        result = get_volk_zusatzelemente(self.char, "Mensch")
        self.assertIsInstance(result, dict)
        self.assertTrue(result['freie_talente'] or result['freies_attribut'])


class TestMenschenTracking(unittest.TestCase):
    """Tests für Menschen-spezifische Tracking-Funktionen"""

    def setUp(self):
        self.char = MockCharakter()

    def test_get_set_menschen_freies_attribut(self):
        from functions.volk_funktionen import _get_menschen_freies_attribut, _set_menschen_freies_attribut
        _set_menschen_freies_attribut(self.char, "Stärke")
        self.assertEqual(_get_menschen_freies_attribut(self.char), "Stärke")
        _set_menschen_freies_attribut(self.char, None)
        self.assertIsNone(_get_menschen_freies_attribut(self.char))

    def test_get_set_menschen_freies_talent(self):
        from functions.volk_funktionen import _get_menschen_freies_talent, _set_menschen_freies_talent
        _set_menschen_freies_talent(self.char, "Kampf")
        self.assertEqual(_get_menschen_freies_talent(self.char), "Kampf")
        _set_menschen_freies_talent(self.char, None)
        self.assertIsNone(_get_menschen_freies_talent(self.char))


class TestHalbelfTracking(unittest.TestCase):
    """Tests für Halbelf-Tracking-Funktionen"""

    def setUp(self):
        self.char = MockCharakter()

    def test_get_set_halbelf_freies_talent(self):
        from functions.volk_funktionen import _get_halbelf_freies_talent, _set_halbelf_freies_talent
        _set_halbelf_freies_talent(self.char, "Kampf")
        self.assertEqual(_get_halbelf_freies_talent(self.char), "Kampf")

    def test_get_set_halbelf_attribut_gewaehlt(self):
        from functions.volk_funktionen import _get_halbelf_attribut_gewaehlt, _set_halbelf_attribut_gewaehlt
        _set_halbelf_attribut_gewaehlt(self.char, True)
        self.assertTrue(_get_halbelf_attribut_gewaehlt(self.char))


class TestHalbelfAuswahl(unittest.TestCase):
    """Tests für Halbelf ENTWEDER/ODER"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.attribute = {"Geschicklichkeit": MockAttribut("Geschicklichkeit", wert=4)}
        self.char.talente = {"Kampf": MockTalent("Kampf", aktiv=True, ausgewaehlt=False)}
        self.char.voelker = {
            "Halbelf": MockVolk("Halbelf", {
                'wahlmoeglichkeiten': {'freies_talent': True}
            })
        }
        self.char.voelker_selected = {}

    def test_waehle_halbelf_attribut(self):
        from functions.volk_funktionen import waehle_halbelf_attribut
        result = waehle_halbelf_attribut(self.char, "Halbelf")
        self.assertTrue(result)
        self.assertEqual(self.char.attribute["Geschicklichkeit"].wert, 6)


class TestReconcileVolkAuswahlen(unittest.TestCase):
    """Tests für reconcile_volk_auswahlen"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.attribute = {"Stärke": MockAttribut("Stärke", wert=4)}
        self.char.talente = {"Kampf": MockTalent("Kampf", aktiv=True, ausgewaehlt=False)}
        self.char.selected_talente = []

    def test_reconcile_kuerzt_liste(self):
        from functions.volk_funktionen import reconcile_volk_auswahlen
        auswahlen_dict = {"Mensch": {"talent": ["Kampf", "Athletik", "Heimlichkeit"]}}
        slot_targets = {"talent": 2}
        reconcile_volk_auswahlen(self.char, "Mensch", auswahlen_dict, slot_targets)
        self.assertEqual(len(auswahlen_dict["Mensch"]["talent"]), 2)


class TestInitialisiereVoelkerSystem(unittest.TestCase):
    """Tests für initialisiere_voelker_system"""

    def setUp(self):
        self.char = MockCharakter()
        self.volk = MockVolk("Mensch", {'wahlmoeglichkeiten': {}})
        self.char.voelker = {"Mensch": self.volk}
        self.char.voelker_selected = {"Mensch": False}

    def test_initialisiere_voelker_system(self):
        from functions.volk_funktionen import initialisiere_voelker_system
        result = initialisiere_voelker_system(self.char)
        self.assertTrue(result)
        self.assertTrue(hasattr(self.char, '_menschen_freies_attribut'))
        self.assertTrue(hasattr(self.char, '_menschen_freies_talent'))


class TestGetVoelkerStatusInfo(unittest.TestCase):
    """Tests für get_voelker_status_info"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.voelker = {"Mensch": MockVolk("Mensch", {'wahlmoeglichkeiten': {}})}
        self.char.voelker_selected = {"Mensch": True, "Verwaist": True}

    def test_get_voelker_status_info(self):
        from functions.volk_funktionen import get_voelker_status_info
        result = get_voelker_status_info(self.char)
        self.assertEqual(result['voelker_gesamt'], 1)
        self.assertEqual(result['voelker_selected_gesamt'], 2)
        self.assertIn("Verwaist", result['verwaiste_eintraege'])
        self.assertEqual(result['ausgewaehltes_volk'], "Mensch")


class TestMenschenVielseitig(unittest.TestCase):
    """Tests für Menschen-Vielseitig (freies Talent ODER 2 Fertigkeitspunkte)"""

    def setUp(self):
        self.char = MockCharakter()
        self.char.talente = {"Kampf": MockTalent("Kampf", aktiv=True, ausgewaehlt=False)}
        self.char.voelker = {
            "Mensch": MockVolk("Mensch", {
                'wahlmoeglichkeiten': {'freies_talent_oder_fertigkeitspunkte': True}
            })
        }
        self.char.voelker_selected = {}
        self.char.verbleibende_fertigkeitssteigerungen = 0
        self.char.maximale_fertigkeitssteigerungen = 0

    def test_waehle_mensch_fertigkeitspunkte(self):
        from functions.volk_funktionen import waehle_mensch_fertigkeitspunkte
        result = waehle_mensch_fertigkeitspunkte(self.char, "Mensch")
        self.assertTrue(result)
        self.assertEqual(self.char.verbleibende_fertigkeitssteigerungen, 2)

    def test_get_set_mensch_fertigkeitspunkte_gewaehlt(self):
        from functions.volk_funktionen import _get_mensch_fertigkeitspunkte_gewaehlt, _set_mensch_fertigkeitspunkte_gewaehlt
        _set_mensch_fertigkeitspunkte_gewaehlt(self.char, True)
        self.assertTrue(_get_mensch_fertigkeitspunkte_gewaehlt(self.char))

    def test_reset_mensch_fertigkeitspunkte(self):
        from functions.volk_funktionen import (
            waehle_mensch_fertigkeitspunkte,
            _get_mensch_fertigkeitspunkte_gewaehlt,
            _reset_mensch_fertigkeitspunkte
        )
        waehle_mensch_fertigkeitspunkte(self.char, "Mensch")
        self.assertTrue(_get_mensch_fertigkeitspunkte_gewaehlt(self.char))
        _reset_mensch_fertigkeitspunkte(self.char)
        self.assertFalse(_get_mensch_fertigkeitspunkte_gewaehlt(self.char))


class TestNoAttributAvailableText(unittest.TestCase):
    """Tests für NO_ATTRIBUT_AVAILABLE_TEXT Konstabte"""

    def test_no_attribut_available_text(self):
        from functions.volk_funktionen import get_verfuegbare_attribute, NO_ATTRIBUT_AVAILABLE_TEXT
        class EmptyChar:
            attribute = None
        result = get_verfuegbare_attribute(EmptyChar())
        self.assertIn(NO_ATTRIBUT_AVAILABLE_TEXT, result)


if __name__ == '__main__':
    unittest.main()
