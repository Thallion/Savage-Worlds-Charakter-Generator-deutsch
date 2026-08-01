"""
Tests für functions/natuerliche_waffen.py

Festgeschrieben wird:
- die Ableitung aus Abstammung (Flag + Fließtext, eigene Eigenarten mit Würfel)
- die Talent-Ketten (Kampfkünstler -> Kampfkunstmeister -> Schläger)
- der Inventar-Abgleich: kostenlos, nur automatisch Gestelltes wird wieder
  eingesammelt, selbst Gekauftes bleibt
"""

import unittest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.natuerliche_waffen import abgeleitete_waffen, synchronisiere
from models.waffe import Waffe


class FakeVolk:
    def __init__(self, effects=None, besonderheiten=None):
        self.name = 'Testvolk'
        self.effects = effects or {}
        self.besonderheiten = besonderheiten or []


class FakeCharakter:
    """Charakter-Ersatz mit den vom Modul genutzten Feldern"""

    def __init__(self, volk=None, talente=None, katalog=None):
        self.voelker = {'Testvolk': volk} if volk else {}
        self.voelker_selected = {'Testvolk': True} if volk else {}
        self.selected_talente = list(talente or [])
        self.natuerliche_waffen = []
        self.ausruestung = katalog if katalog is not None else katalog_mit_allen_waffen()
        self.selected_waffen = []
        self.selected_schilde = []
        self.selected_ruestungen = []
        self.selected_allgemeine_ausruestung = []

    def besitzt(self, name):
        item = self.ausruestung.get(name)
        return bool(item and item.menge > 0)


def katalog_mit_allen_waffen():
    """Katalog wie im Setting: alle natürlichen Waffen vorhanden, Menge 0"""
    import json
    with open(project_root / 'settings' / 'SWAE.json', encoding='utf-8') as f:
        ausruestung = json.load(f)['ausruestung']
    return {
        name: Waffe.from_setting_dict(eintrag)
        for name, eintrag in ausruestung.items()
        if eintrag.get('unterkategorie') == 'Natürliche Waffe'
    }


class TestAbleitungAusVolk(unittest.TestCase):

    def test_flag_plus_fliesstext(self):
        """Setting-Völker: Flag im Effekt, Schaden im Besonderheiten-Text"""
        volk = FakeVolk(
            effects={'spezielle_effekte': {'klauen': True}},
            besonderheiten=["Klauen (Stä+W6 Schaden, PB 2)"],
        )
        self.assertEqual(abgeleitete_waffen(FakeCharakter(volk)),
                         ["Klauen (Stä+W6, PB 2)"])

    def test_flag_ohne_text_faellt_auf_w4_zurueck(self):
        volk = FakeVolk(effects={'spezielle_effekte': {'biss': True}})
        self.assertEqual(abgeleitete_waffen(FakeCharakter(volk)), ["Biss (Stä+W4)"])

    def test_eigenart_liefert_wuerfel_direkt(self):
        """Eigene Abstammung (volkseigenarten_config.json): Listen-Format"""
        volk = FakeVolk(effects={'spezielle_effekte': [
            {'typ': 'klauen', 'wert': 'W6'},
            {'typ': 'panzerbrechend', 'wert': 2},
        ]})
        self.assertEqual(abgeleitete_waffen(FakeCharakter(volk)),
                         ["Klauen (Stä+W6, PB 2)"])

    def test_natuerliche_waffe_nur_im_text(self):
        """z. B. Horror-Vampir: 'Natürliche Waffen (Biss: Stä+W4)'"""
        volk = FakeVolk(besonderheiten=["Natürliche Waffen (Biss: Stä+W4)"])
        self.assertEqual(abgeleitete_waffen(FakeCharakter(volk)), ["Biss (Stä+W4)"])

    def test_bedingte_formulierungen_zaehlen_nicht(self):
        """Formabhängige oder alternative Angaben gewähren keine Waffe"""
        volk = FakeVolk(besonderheiten=[
            "Hybridform: Natürliche Waffen (Klauen: Stä+W6)",
            "Alternativfähigkeit: Natürliche Waffen (Biss: Stä+W4)",
        ])
        self.assertEqual(abgeleitete_waffen(FakeCharakter(volk)), [])


class TestAbleitungAusTalenten(unittest.TestCase):

    def test_kampfkuenstler_gibt_w4(self):
        self.assertEqual(abgeleitete_waffen(FakeCharakter(talente=['Kampfkünstler'])),
                         ["Waffenloser Schlag (Stä+W4)"])

    def test_kette_steigert_den_wuerfel(self):
        """Kampfkünstler W4 -> Kampfkunstmeister W6 -> Schläger W8"""
        charakter = FakeCharakter(talente=['Kampfkünstler', 'Kampfkunstmeister'])
        self.assertEqual(abgeleitete_waffen(charakter), ["Waffenloser Schlag (Stä+W6)"])

        charakter = FakeCharakter(talente=['Kampfkünstler', 'Kampfkunstmeister', 'Schläger'])
        self.assertEqual(abgeleitete_waffen(charakter), ["Waffenloser Schlag (Stä+W8)"])

    def test_steigerndes_talent_allein_gibt_nichts(self):
        """Kampfkunstmeister steigert nur, wenn schon ein Würfel da ist"""
        self.assertEqual(abgeleitete_waffen(FakeCharakter(talente=['Kampfkunstmeister'])), [])

    def test_talent_verbessert_volkswaffe(self):
        """Wilde Klauen setzt die Volks-Klauen auf mindestens W6 mit PB 2"""
        volk = FakeVolk(effects={'spezielle_effekte': {'klauen': True}},
                        besonderheiten=["Klauen (Stä+W4 Schaden)"])
        charakter = FakeCharakter(volk, talente=['Wilde Klauen'])
        self.assertEqual(abgeleitete_waffen(charakter), ["Klauen (Stä+W6, PB 2)"])


class TestSynchronisation(unittest.TestCase):

    def test_waffe_landet_kostenlos_im_inventar(self):
        charakter = FakeCharakter(talente=['Kampfkünstler'])
        gestellt = synchronisiere(charakter)
        self.assertEqual(gestellt, ["Waffenloser Schlag (Stä+W4)"])
        self.assertTrue(charakter.besitzt("Waffenloser Schlag (Stä+W4)"))
        item = charakter.ausruestung["Waffenloser Schlag (Stä+W4)"]
        self.assertEqual(item.kosten, 0)
        self.assertEqual(item.gewicht, 0)
        self.assertIn(item, charakter.selected_waffen)

    def test_verbesserung_ersetzt_die_alte_waffe(self):
        charakter = FakeCharakter(talente=['Kampfkünstler'])
        synchronisiere(charakter)
        charakter.selected_talente.append('Kampfkunstmeister')
        synchronisiere(charakter)
        self.assertFalse(charakter.besitzt("Waffenloser Schlag (Stä+W4)"))
        self.assertTrue(charakter.besitzt("Waffenloser Schlag (Stä+W6)"))
        self.assertEqual(charakter.natuerliche_waffen, ["Waffenloser Schlag (Stä+W6)"])

    def test_rueckstufung_stellt_die_schwaechere_waffe_wieder(self):
        """Kampfkunstmeister abgewählt, Kampfkünstler bleibt → wieder Stä+W4"""
        charakter = FakeCharakter(talente=['Kampfkünstler', 'Kampfkunstmeister'])
        synchronisiere(charakter)
        self.assertTrue(charakter.besitzt("Waffenloser Schlag (Stä+W6)"))

        charakter.selected_talente.remove('Kampfkunstmeister')
        synchronisiere(charakter)
        self.assertEqual(charakter.natuerliche_waffen, ["Waffenloser Schlag (Stä+W4)"])
        self.assertTrue(charakter.besitzt("Waffenloser Schlag (Stä+W4)"))
        self.assertFalse(charakter.besitzt("Waffenloser Schlag (Stä+W6)"))

    def test_abgewaehltes_talent_nimmt_die_waffe_zurueck(self):
        charakter = FakeCharakter(talente=['Kampfkünstler'])
        synchronisiere(charakter)
        charakter.selected_talente.remove('Kampfkünstler')
        self.assertEqual(synchronisiere(charakter), [])
        self.assertFalse(charakter.besitzt("Waffenloser Schlag (Stä+W4)"))
        self.assertEqual(charakter.selected_waffen, [])

    def test_selbst_gekaufte_waffe_bleibt(self):
        """Was der Spieler selbst besitzt, wird nicht eingesammelt"""
        charakter = FakeCharakter(talente=['Kampfkünstler'])
        charakter.ausruestung["Waffenloser Schlag (Stä+W4)"].erhoehe_menge(1)
        synchronisiere(charakter)
        self.assertEqual(charakter.natuerliche_waffen, [])

        charakter.selected_talente.remove('Kampfkünstler')
        synchronisiere(charakter)
        self.assertTrue(charakter.besitzt("Waffenloser Schlag (Stä+W4)"))

    def test_ist_wiederholbar(self):
        charakter = FakeCharakter(talente=['Kampfkünstler'])
        synchronisiere(charakter)
        synchronisiere(charakter)
        synchronisiere(charakter)
        self.assertEqual(charakter.ausruestung["Waffenloser Schlag (Stä+W4)"].menge, 1)
        self.assertEqual(charakter.natuerliche_waffen, ["Waffenloser Schlag (Stä+W4)"])

    def test_waffen_ausserhalb_des_katalogs_werden_ignoriert(self):
        charakter = FakeCharakter(talente=['Kampfkünstler'], katalog={})
        self.assertEqual(synchronisiere(charakter), [])


class TestSettingKatalog(unittest.TestCase):
    """Jede ableitbare Waffe muss in JEDEM Setting im Katalog stehen"""

    def test_alle_settings_kennen_alle_natuerlichen_waffen(self):
        import json
        from functions.natuerliche_waffen import lade_config, waffen_name

        config = lade_config()
        gruppen = config['gruppen']
        namen = {name for pfad in (project_root / 'settings').glob('*.json')
                 for name in json.loads(pfad.read_text(encoding='utf-8'))['ausruestung']}

        # Alle Kombinationen, die die Talent-/Eigenart-Regeln erzeugen können
        erwartet = set()
        for regel in config['talente'].values():
            gruppe = gruppen[regel['gruppe']]
            wiederholung = regel.get('wiederholung') or {}
            for wuerfel in config['wuerfel_kette']:
                for pb in (0, int(regel.get('pb') or 0), int(wiederholung.get('pb') or 0)):
                    erwartet.add(waffen_name(gruppe, wuerfel, pb))

        for pfad in sorted((project_root / 'settings').glob('*.json')):
            katalog = json.loads(pfad.read_text(encoding='utf-8'))['ausruestung']
            for name in sorted(namen & erwartet):
                with self.subTest(setting=pfad.stem, waffe=name):
                    self.assertIn(name, katalog)


if __name__ == '__main__':
    unittest.main()
