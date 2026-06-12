# test units/test_popup_form.py
"""
Tests für views/popup_form.py (FormDialogContent + FormDialogHandlerMixin).

FormDialogContent wird mit ECHTEN KivyMD-Widgets getestet (headless über
SDL-dummy + manuell registrierter MDApp-Instanz), damit fill()/collect()
gegen das reale Widget-Verhalten laufen. Der Handler-Mixin-Flow wird mit
gemocktem Overlay getestet.
"""
import os
import sys
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault('KIVY_NO_ARGS', '1')
os.environ.setdefault('KIVY_NO_CONSOLELOG', '1')
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kivy.app import App
from kivymd.app import MDApp

# KivyMD-Widgets benötigen eine registrierte App-Instanz (theme_cls)
_test_app = None
_vorherige_app = None


def setUpModule():
    global _test_app, _vorherige_app
    _vorherige_app = App._running_app
    if _vorherige_app is None:
        _test_app = MDApp()
        App._running_app = _test_app


def tearDownModule():
    # App-Registrierung zurücksetzen, damit andere Tests unbeeinflusst bleiben
    if _test_app is not None:
        App._running_app = _vorherige_app


from views.popup_form import FormDialogContent, FormDialogHandlerMixin
from views.popup_basis import BasisDialogHandler


TEST_FELDER = [
    {'key': 'name', 'label': 'Name', 'typ': 'text', 'pflicht': True,
     'pflicht_meldung': 'Der Name darf nicht leer sein.'},
    {'key': 'gewicht', 'label': 'Gewicht', 'typ': 'float', 'default': 0},
    {'key': 'punkte', 'label': 'Punkte', 'typ': 'int', 'default': 1},
    {'key': 'mindeststaerke', 'label': 'Mindeststärke', 'typ': 'auswahl',
     'erlaubt': ['W4', 'W6', '-']},
    {'key': 'attribut', 'label': 'Attribut wählen', 'typ': 'dropdown',
     'optionen': ['Geschicklichkeit', 'Stärke'], 'pflicht': True},
    {'key': 'grundfertigkeit', 'label': 'Grundfertigkeit', 'typ': 'checkbox'},
    {'key': 'beschreibung', 'label': 'Beschreibung', 'typ': 'multiline'},
]


class TestFormDialogContent(unittest.TestCase):

    def test_baut_alle_feldtypen(self):
        """Alle Feld-Typen erzeugen ein Widget unter ihrem key"""
        content = FormDialogContent(TEST_FELDER)
        self.assertEqual(set(content.feld_widgets),
                         {f['key'] for f in TEST_FELDER})

    def test_collect_roundtrip(self):
        """Eingegebene Werte kommen typkorrekt und getrimmt zurück"""
        content = FormDialogContent(TEST_FELDER)
        content.feld_widgets['name'].text = '  Schwert  '
        content.feld_widgets['gewicht'].text = '2.5'
        content.feld_widgets['punkte'].text = '3'
        content.feld_widgets['mindeststaerke'].text = 'W6'
        content._select_dropdown('attribut', 'Stärke')
        content.feld_widgets['grundfertigkeit'].active = True
        content.feld_widgets['beschreibung'].text = 'Eine Klinge'

        werte, fehler = content.collect()

        self.assertEqual(fehler, [])
        self.assertEqual(werte, {
            'name': 'Schwert',
            'gewicht': 2.5,
            'punkte': 3,
            'mindeststaerke': 'W6',
            'attribut': 'Stärke',
            'grundfertigkeit': True,
            'beschreibung': 'Eine Klinge',
        })

    def test_collect_defaults_fuer_leere_zahlenfelder(self):
        """Leere int/float-Felder fallen auf den default zurück"""
        content = FormDialogContent(TEST_FELDER)
        content.feld_widgets['name'].text = 'X'
        content.feld_widgets['mindeststaerke'].text = 'W4'
        content._select_dropdown('attribut', 'Stärke')
        werte, fehler = content.collect()
        self.assertEqual(fehler, [])
        self.assertEqual(werte['gewicht'], 0)
        self.assertEqual(werte['punkte'], 1)

    def test_collect_validierungsfehler(self):
        """Pflichtfelder, Auswahl-Wertemenge und Dropdown-Pflicht melden Fehler"""
        content = FormDialogContent(TEST_FELDER)
        content.feld_widgets['mindeststaerke'].text = 'W20'
        _, fehler = content.collect()
        self.assertIn('Der Name darf nicht leer sein.', fehler)
        self.assertTrue(any('Mindeststärke' in f for f in fehler))
        self.assertTrue(any('Attribut' in f for f in fehler))

    def test_collect_ungueltige_zahl(self):
        """Nicht parsebare Zahl → Fehlermeldung statt Exception"""
        content = FormDialogContent(TEST_FELDER)
        content.feld_widgets['name'].text = 'X'
        content.feld_widgets['mindeststaerke'].text = 'W4'
        content._select_dropdown('attribut', 'Stärke')
        content.feld_widgets['gewicht'].text = '12..5'
        _, fehler = content.collect()
        self.assertTrue(any('Gewicht' in f for f in fehler))

    def test_fill_befuellt_alle_feldtypen(self):
        """fill() schreibt Daten in Text-, Dropdown- und Checkbox-Felder"""
        content = FormDialogContent(TEST_FELDER)
        content.fill({
            'name': 'Axt', 'gewicht': 3, 'punkte': 2, 'mindeststaerke': '-',
            'attribut': 'Geschicklichkeit', 'grundfertigkeit': True,
            'beschreibung': 'Wuchtig',
        })
        werte, fehler = content.collect()
        self.assertEqual(fehler, [])
        self.assertEqual(werte['name'], 'Axt')
        self.assertEqual(werte['gewicht'], 3.0)
        self.assertEqual(werte['attribut'], 'Geschicklichkeit')
        self.assertTrue(werte['grundfertigkeit'])

    def test_callable_optionen(self):
        """Dropdown-Optionen können als Callable übergeben werden"""
        aufgerufen = []

        def optionen():
            aufgerufen.append(True)
            return []  # leer → Menü öffnet nicht (kein Fehler)

        felder = [{'key': 'a', 'label': 'A', 'typ': 'dropdown', 'optionen': optionen}]
        content = FormDialogContent(felder)
        content._open_dropdown(content.feld_widgets['a'], felder[0])
        self.assertTrue(aufgerufen)


class _FormTestHandler(FormDialogHandlerMixin, BasisDialogHandler):
    """Minimaler Handler für den Add/Edit-Flow"""
    element_name = "Testelement"
    element_name_plural = "Testelemente"
    titel_neu = "Neues Testelement hinzufügen"
    titel_bearbeiten = "Testelement bearbeiten"
    FELDER = [
        {'key': 'name', 'label': 'Name', 'typ': 'text', 'pflicht': True},
    ]

    def __init__(self, controller):
        super().__init__(controller)
        self.erstellt = None
        self.aktualisiert = None
        self.daten = {'Alt': {'name': 'Alt'}}
        self.refresh_aufrufe = 0

    def _get_loeschbare_elemente(self):
        return list(self.daten)

    def _confirm_delete_elemente(self):
        pass

    def _get_element_daten(self, key):
        return self.daten.get(key)

    def _erstelle_element(self, werte):
        self.erstellt = werte
        return True

    def _aktualisiere_element(self, key, werte):
        self.aktualisiert = (key, werte)
        return True

    def _nach_speichern(self):
        self.refresh_aufrufe += 1


class TestFormDialogHandlerMixin(unittest.TestCase):

    def _handler_mit_overlay(self):
        handler = _FormTestHandler(Mock())
        overlay = Mock()
        overlay._is_open = True
        handler.overlay = overlay
        handler._get_overlay = Mock(return_value=overlay)
        return handler, overlay

    def test_show_add_dialog_oeffnet_overlay(self):
        handler, overlay = self._handler_mit_overlay()
        handler.show_add_dialog()
        overlay.open.assert_called_once()
        kwargs = overlay.open.call_args.kwargs
        self.assertEqual(kwargs['title'], "Neues Testelement hinzufügen")
        self.assertIsInstance(kwargs['content_widget'], FormDialogContent)

    def test_save_neu_erstellt_und_schliesst(self):
        handler, overlay = self._handler_mit_overlay()
        handler.show_add_dialog()
        handler.dialog_content.feld_widgets['name'].text = 'Neu'
        handler._on_save_neu()
        self.assertEqual(handler.erstellt, {'name': 'Neu'})
        self.assertEqual(handler.refresh_aufrufe, 1)
        overlay.close.assert_called_once()

    def test_save_neu_validierungsfehler_kein_dismiss(self):
        handler, overlay = self._handler_mit_overlay()
        handler.show_add_dialog()
        with patch.object(handler, 'show_error') as mock_error:
            handler._on_save_neu()
        mock_error.assert_called_once()
        self.assertIsNone(handler.erstellt)
        overlay.close.assert_not_called()

    def test_edit_flow(self):
        handler, overlay = self._handler_mit_overlay()
        handler.show_edit_dialog('Alt')
        overlay.open.assert_called_once()
        self.assertEqual(overlay.open.call_args.kwargs['title'], "Testelement bearbeiten")
        handler.dialog_content.feld_widgets['name'].text = 'Umbenannt'
        handler._on_save_bearbeiten()
        self.assertEqual(handler.aktualisiert, ('Alt', {'name': 'Umbenannt'}))
        overlay.close.assert_called_once()

    def test_edit_unbekanntes_element(self):
        handler, overlay = self._handler_mit_overlay()
        with patch.object(handler, 'show_error') as mock_error:
            handler.show_edit_dialog('GibtEsNicht')
        mock_error.assert_called_once()
        overlay.open.assert_not_called()


if __name__ == '__main__':
    unittest.main()
