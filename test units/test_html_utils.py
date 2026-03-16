"""
Tests für HTML-Generierung (utils/html_utils.py)
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import Mock, MagicMock, patch

# Mocking für Kivy/KivyMD
sys.modules['kivy'] = MagicMock()
sys.modules['kivy.app'] = MagicMock()
sys.modules['kivy.logger'] = MagicMock()
sys.modules['kivy.clock'] = MagicMock()
sys.modules['kivy.lang'] = MagicMock()
sys.modules['kivy.metrics'] = MagicMock()
sys.modules['kivy.properties'] = MagicMock()
sys.modules['kivy.event'] = MagicMock()
sys.modules['kivy.uix'] = MagicMock()
sys.modules['kivy.uix.boxlayout'] = MagicMock()
sys.modules['kivymd'] = MagicMock()
sys.modules['kivymd.app'] = MagicMock()
sys.modules['kivymd.uix'] = MagicMock()
sys.modules['kivymd.uix.boxlayout'] = MagicMock()
sys.modules['kivymd.uix.label'] = MagicMock()
sys.modules['kivymd.uix.button'] = MagicMock()
sys.modules['kivymd.uix.dialog'] = MagicMock()
sys.modules['kivymd.uix.selectioncontrol'] = MagicMock()

# Projektverzeichnis zum Pfad hinzufügen
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def _create_mock_charakter():
    """Erstellt ein Mock-Charakter-Objekt für Tests"""
    charakter = Mock()
    charakter.char_name = "Testcharakter"
    charakter.active_setting_name = "SWAE"

    # Profildaten
    charakter.profil_daten = {
        'Name': 'Testcharakter',
        'Setting': 'SWAE',
        'Rang': 'Anfänger',
    }

    # Attribute
    attr1 = Mock()
    attr1.attribut_name = "Stärke"
    attr1.wert = 6
    attr1.modifier = 0
    attr2 = Mock()
    attr2.attribut_name = "Geschicklichkeit"
    attr2.wert = 8
    attr2.modifier = 1
    charakter.attribute = {'Stärke': attr1, 'Geschicklichkeit': attr2}

    # Fertigkeiten
    fert1 = Mock()
    fert1.fertigkeit_name = "Athletik"
    fert1.wert = 6
    fert1.modifier = 0
    fert2 = Mock()
    fert2.fertigkeit_name = "Heilen"
    fert2.wert = 4
    fert2.modifier = -2  # Sollte gefiltert werden
    fert3 = Mock()
    fert3.fertigkeit_name = "Schießen"
    fert3.wert = 8
    fert3.modifier = 0
    charakter.fertigkeiten = {
        'Athletik': fert1,
        'Heilen': fert2,
        'Schießen': fert3
    }

    # Volk
    charakter.voelker_selected = {'Mensch': True, 'Elf': False}
    volk_obj = Mock()
    volk_obj.talente = ["Vielseitigkeit"]
    volk_obj.handicaps = []
    volk_obj.besonderheiten = ["Anpassungsfähig"]
    charakter.voelker = {'Mensch': volk_obj}

    # Abgeleitete Werte
    charakter.bewegungsweite = 6
    charakter.parade = 5
    charakter.robustheit_mit_ruestung = 7
    charakter.machtpunkte = 0
    charakter.wunden = 0
    charakter.erschoepfung = 0
    charakter.bennys = 3
    charakter.entschlossenheit = 0
    charakter.gesamtgewicht = 5.0
    charakter.maximale_traglast = 30

    # Handicaps
    handicap1 = Mock()
    handicap1.name = "Loyal"
    handicap1.stufe = "Leicht"
    handicap1.beschreibung = "Der Charakter ist seinen Freunden treu."
    charakter.selected_handicaps = ['Loyal']
    charakter.handicaps = {'Loyal': handicap1}

    # Talente
    talent1 = Mock()
    talent1.name = "Aufmerksam"
    talent1.rang = "Anfänger"
    talent1.beschreibung = "+2 auf Wahrnehmung"
    charakter.selected_talente = ['Aufmerksam']
    charakter.talente = {'Aufmerksam': talent1}

    # Mächte (leer)
    charakter.selected_maechte = []
    charakter.maechte = {}

    # Superkräfte (leer)
    charakter.selected_superkraefte = []
    charakter.superkraefte = {}

    # Ausrüstung
    ausruestung_item = Mock()
    ausruestung_item.name = "Seil"
    ausruestung_item.menge = 1
    ausruestung_item.beschreibung = "10m Seil"
    ausruestung_item.ausgewaehlt = True
    charakter.ausruestung = {'Seil': ausruestung_item}
    charakter.selected_allgemeine_ausruestung = [ausruestung_item]

    # Waffen (leer)
    charakter.selected_waffen = []

    # Rüstungen (leer)
    charakter.selected_ruestungen = []

    # Schilde (leer)
    charakter.selected_schilde = []

    # Journal (leer)
    charakter.steigerungs_journal = None

    return charakter


class TestHTMLGenerierung(unittest.TestCase):
    """Tests für die HTML-Generierungsfunktion"""

    def setUp(self):
        self.charakter = _create_mock_charakter()
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.temp_dir, "test_charakter.html")

    def tearDown(self):
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_generiere_html_erfolg(self, mock_cyber, mock_logger):
        """Testet erfolgreiche HTML-Generierung"""
        from utils.html_utils import generiere_html
        result = generiere_html(self.charakter, self.output_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_path))

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_enthaelt_grundstruktur(self, mock_cyber, mock_logger):
        """Testet ob HTML die Grundstruktur enthält"""
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('<!DOCTYPE html>', content)
        self.assertIn('<meta charset="utf-8">', content)
        self.assertIn('<meta name="viewport"', content)
        self.assertIn('Charakterbogen:', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_enthaelt_profil(self, mock_cyber, mock_logger):
        """Testet ob HTML Profildaten enthält"""
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Profil', content)
        self.assertIn('Testcharakter', content)
        self.assertIn('SWAE', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_enthaelt_attribute(self, mock_cyber, mock_logger):
        """Testet ob HTML Attribute enthält"""
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Stärke', content)
        self.assertIn('W6', content)
        self.assertIn('Geschicklichkeit', content)
        self.assertIn('W8 +1', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_filtert_fertigkeiten(self, mock_cyber, mock_logger):
        """Testet ob Fertigkeiten mit modifier=-2 gefiltert werden"""
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Athletik', content)
        self.assertIn('Schießen', content)
        self.assertNotIn('Heilen', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_enthaelt_handicaps(self, mock_cyber, mock_logger):
        """Testet ob HTML Handicaps enthält"""
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Loyal', content)
        self.assertIn('Leicht', content)
        self.assertIn('Der Charakter ist seinen Freunden treu.', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_enthaelt_talente(self, mock_cyber, mock_logger):
        """Testet ob HTML Talente enthält"""
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Aufmerksam', content)
        self.assertIn('+2 auf Wahrnehmung', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_enthaelt_volk(self, mock_cyber, mock_logger):
        """Testet ob HTML Volksdaten enthält"""
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Mensch', content)
        self.assertIn('Vielseitigkeit', content)
        self.assertIn('Anpassungsfähig', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_enthaelt_abgeleitete_werte(self, mock_cyber, mock_logger):
        """Testet ob HTML abgeleitete Werte enthält"""
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Bewegungsweite', content)
        self.assertIn('Parade', content)
        self.assertIn('Robustheit', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_enthaelt_ausruestung(self, mock_cyber, mock_logger):
        """Testet ob HTML Ausrüstung enthält"""
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Seil', content)
        self.assertIn('10m Seil', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_printer_friendly_kein_farbhintergrund(self, mock_cyber, mock_logger):
        """Testet druckerfreundliche Version ohne Farbhintergründe"""
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path, printer_friendly=True)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Kein Moccasin/OldLace in der printer_friendly Version
        self.assertNotIn('#ffb961', content)
        self.assertNotIn('#FFE4B5', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_normal_version_hat_farben(self, mock_cyber, mock_logger):
        """Testet normale Version hat Farbhintergründe"""
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path, printer_friendly=False)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('#ffb961', content)
        self.assertIn('#FFE4B5', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_escape_sonderzeichen(self, mock_cyber, mock_logger):
        """Testet ob Sonderzeichen korrekt escaped werden"""
        self.charakter.profil_daten = {
            'Name': '<script>alert("XSS")</script>',
            'Setting': 'Test & Setting',
        }
        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertNotIn('<script>', content)
        self.assertIn('&lt;script&gt;', content)
        self.assertIn('&amp;', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_mit_waffen(self, mock_cyber, mock_logger):
        """Testet HTML-Generierung mit Waffen"""
        waffe = Mock()
        waffe.name = "Langschwert"
        waffe.angelegt = True
        waffe.eigenschaften = {
            'Schaden': 'St+W8',
            'Reichweite': '-',
            'FR': '-',
            'Schuss': '-',
            'PB': '-'
        }
        self.charakter.selected_waffen = [waffe]

        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Langschwert', content)
        self.assertIn('St+W8', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_mit_ruestungen(self, mock_cyber, mock_logger):
        """Testet HTML-Generierung mit Rüstungen"""
        ruestung = Mock()
        ruestung.name = "Kettenhemd"
        ruestung.angelegt = True
        ruestung.torso = 3
        ruestung.arme = 2
        ruestung.beine = 0
        ruestung.kopf = 0
        self.charakter.selected_ruestungen = [ruestung]
        self.charakter.berechne_gesamt_ruestungsschutz = Mock(return_value={
            'Torso': 3, 'Arme': 2, 'Beine': 0, 'Kopf': 0
        })

        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Kettenhemd', content)
        self.assertIn('Gesamt', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_mit_maechten(self, mock_cyber, mock_logger):
        """Testet HTML-Generierung mit Mächten"""
        macht = Mock()
        macht.name = "Bolzen"
        macht.rang = "Anfänger"
        macht.machtpunkte = "1-6"
        macht.reichweite = "12/24/48"
        macht.dauer = "Sofort"
        macht.beschreibung = "Feuert magische Bolzen."
        self.charakter.selected_maechte = ['Bolzen']
        self.charakter.maechte = {'Bolzen': macht}

        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Bolzen', content)
        self.assertIn('12/24/48', content)
        self.assertIn('Feuert magische Bolzen.', content)

    @patch('utils.html_utils.Logger')
    @patch('functions.cyberware_funktionen.ist_cyberware_setting', return_value=False)
    def test_html_mit_steigerungen(self, mock_cyber, mock_logger):
        """Testet HTML-Generierung mit Steigerungs-Journal"""
        self.charakter.steigerungs_journal = {
            'entries': [
                {
                    'type': 'attribut_steigerung',
                    'rang': 'Fortgeschritten',
                    'details': {
                        'name': 'Stärke',
                        'von': 6,
                        'nach': 8,
                        'kosten': 1,
                        'kosten_typ': 'Aufstieg'
                    }
                }
            ]
        }

        from utils.html_utils import generiere_html
        generiere_html(self.charakter, self.output_path)

        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('Steigerungen', content)
        self.assertIn('Stärke', content)
        self.assertIn('W6', content)
        self.assertIn('W8', content)

    @patch('utils.html_utils.Logger')
    def test_generiere_html_fehler_bei_ungueltigem_pfad(self, mock_logger):
        """Testet Fehlerbehandlung bei ungültigem Pfad"""
        from utils.html_utils import generiere_html
        result = generiere_html(self.charakter, "/nonexistent/path/test.html")
        self.assertFalse(result)


class TestHelperFunktionen(unittest.TestCase):
    """Tests für Hilfsfunktionen"""

    def test_esc_normal(self):
        """Testet normales Escaping"""
        from utils.html_utils import _esc
        self.assertEqual(_esc("Hello"), "Hello")
        self.assertEqual(_esc("<b>bold</b>"), "&lt;b&gt;bold&lt;/b&gt;")
        self.assertEqual(_esc("A & B"), "A &amp; B")

    def test_esc_none(self):
        """Testet Escaping von None"""
        from utils.html_utils import _esc
        self.assertEqual(_esc(None), "")

    def test_esc_number(self):
        """Testet Escaping von Zahlen"""
        from utils.html_utils import _esc
        self.assertEqual(_esc(42), "42")

    def test_create_mod_text(self):
        """Testet Modifier-Text-Erzeugung"""
        from utils.html_utils import _create_mod_text
        self.assertEqual(_create_mod_text(0), "")
        self.assertEqual(_create_mod_text(2), "+2")
        self.assertEqual(_create_mod_text(-1), "-1")


if __name__ == '__main__':
    unittest.main()
