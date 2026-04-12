# tests/test_einstellungen_widget.py
"""
Unit Tests für EinstellungenWidget
Testet das aktuelle Widget mit Managern, GameElementsHandler und service_container.
"""

import unittest
import os
import sys
from unittest.mock import Mock, MagicMock, patch, mock_open, PropertyMock

# KivyMD Chip-Modul hat einen Metaclass-Konflikt - vor allem anderen mocken
for _mod in ['kivymd.uix.chip', 'kivymd.uix.chip.chip']:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

# Builder.load_file mocken (verhindert KV-Datei-Laden ohne laufende App)
with patch('kivy.lang.Builder.load_file'):
    from views.einstellungen_widget import EinstellungenWidget

# EventTypes wird direkt gebraucht
from services.event_service import EventTypes


class _AttrDict(dict):
    """Dict mit Attribut-Zugriff (wie Kivy ids)"""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


def _create_widget():
    """Erstellt ein EinstellungenWidget mit komplett gemockten Abhängigkeiten.

    Returns:
        tuple: (widget, mocks_dict) mit allen relevanten Mocks
    """
    mock_app = Mock()
    mock_app.controller = Mock()
    mock_app.controller.charakter = Mock()

    mock_game_handler = Mock()
    mock_theme_mgr = Mock()
    mock_stats_mgr = Mock()
    mock_pdf_mgr = Mock()
    mock_event_service = Mock()
    mock_sc = Mock()
    mock_sc.get_event_service.return_value = mock_event_service
    mock_sc.get_dialog_service.return_value = Mock()

    with patch('views.einstellungen_widget.MDBoxLayout.__init__', lambda self, **kw: None), \
         patch('views.einstellungen_widget.MDApp') as mock_mdapp, \
         patch('views.einstellungen_widget.Clock') as mock_clock, \
         patch('views.einstellungen_widget.GameElementsHandler', return_value=mock_game_handler), \
         patch('views.einstellungen_widget.ThemeManager', return_value=mock_theme_mgr), \
         patch('views.einstellungen_widget.StatisticsManager', return_value=mock_stats_mgr), \
         patch('views.einstellungen_widget.PDFManager', return_value=mock_pdf_mgr), \
         patch('views.einstellungen_widget.service_container', mock_sc):

        mock_mdapp.get_running_app.return_value = mock_app
        widget = EinstellungenWidget()

    mocks = {
        'app': mock_app,
        'game_elements_handler': mock_game_handler,
        'theme_manager': mock_theme_mgr,
        'statistics_manager': mock_stats_mgr,
        'pdf_manager': mock_pdf_mgr,
        'event_service': mock_event_service,
        'service_container': mock_sc,
        'clock': mock_clock,
    }
    return widget, mocks


class TestEinstellungenWidgetInit(unittest.TestCase):
    """Tests für Initialisierung"""

    def test_init_sets_app(self):
        """__init__ setzt self.app über MDApp.get_running_app()"""
        widget, mocks = _create_widget()
        self.assertEqual(widget.app, mocks['app'])

    def test_init_sets_game_elements_handler(self):
        """__init__ erstellt GameElementsHandler"""
        widget, mocks = _create_widget()
        self.assertEqual(widget.game_elements_handler, mocks['game_elements_handler'])

    def test_init_sets_managers(self):
        """__init__ erstellt ThemeManager, StatisticsManager, PDFManager"""
        widget, mocks = _create_widget()
        self.assertEqual(widget.theme_manager, mocks['theme_manager'])
        self.assertEqual(widget.statistics_manager, mocks['statistics_manager'])
        self.assertEqual(widget.pdf_manager, mocks['pdf_manager'])

    def test_init_schedules_post_init(self):
        """__init__ plant _post_init via Clock.schedule_once"""
        widget, mocks = _create_widget()
        mocks['clock'].schedule_once.assert_called_once_with(widget._post_init, 0)

    def test_initialize_handlers_error(self):
        """_initialize_handlers fängt Exception ab und loggt Fehler"""
        with patch('views.einstellungen_widget.MDBoxLayout.__init__', lambda self, **kw: None), \
             patch('views.einstellungen_widget.MDApp') as mock_mdapp, \
             patch('views.einstellungen_widget.Clock'), \
             patch('views.einstellungen_widget.GameElementsHandler', side_effect=Exception("fail")), \
             patch('views.einstellungen_widget.ThemeManager', return_value=Mock()), \
             patch('views.einstellungen_widget.StatisticsManager', return_value=Mock()), \
             patch('views.einstellungen_widget.PDFManager', return_value=Mock()), \
             patch('views.einstellungen_widget.service_container', Mock()), \
             patch('views.einstellungen_widget.Logger') as mock_logger:

            mock_mdapp.get_running_app.return_value = Mock()
            widget = EinstellungenWidget()
            mock_logger.error.assert_any_call("Fehler bei Handler-Initialisierung: fail")

    def test_initialize_managers_error_sets_none(self):
        """_initialize_managers setzt Manager auf None bei Fehler"""
        with patch('views.einstellungen_widget.MDBoxLayout.__init__', lambda self, **kw: None), \
             patch('views.einstellungen_widget.MDApp') as mock_mdapp, \
             patch('views.einstellungen_widget.Clock'), \
             patch('views.einstellungen_widget.GameElementsHandler', return_value=Mock()), \
             patch('views.einstellungen_widget.ThemeManager', side_effect=Exception("mgr fail")), \
             patch('views.einstellungen_widget.service_container', Mock()), \
             patch('views.einstellungen_widget.Logger'):

            mock_mdapp.get_running_app.return_value = Mock()
            widget = EinstellungenWidget()
            self.assertIsNone(widget.theme_manager)
            self.assertIsNone(widget.statistics_manager)
            self.assertIsNone(widget.pdf_manager)

    def test_register_event_handlers(self):
        """_register_event_handlers abonniert THEME_CHANGED"""
        widget, mocks = _create_widget()
        mocks['event_service'].subscribe.assert_any_call(
            EventTypes.THEME_CHANGED, widget._on_theme_changed
        )


class TestEinstellungenWidgetPostInit(unittest.TestCase):
    """Tests für Post-Initialisierung"""

    def test_post_init_initializes_theme(self):
        """_post_init ruft theme_manager.initialize_theme() auf"""
        widget, mocks = _create_widget()
        widget._post_init(0)
        mocks['theme_manager'].initialize_theme.assert_called_once()

    def test_post_init_updates_statistics(self):
        """_post_init ruft statistics_manager.update_element_statistics_ui() auf"""
        widget, mocks = _create_widget()
        widget._post_init(0)
        mocks['statistics_manager'].update_element_statistics_ui.assert_called_once()

    def test_post_init_no_theme_manager(self):
        """_post_init funktioniert wenn theme_manager None ist"""
        widget, mocks = _create_widget()
        widget.theme_manager = None
        widget.statistics_manager = None
        # Soll keine Exception werfen
        widget._post_init(0)

    def test_post_init_error_handling(self):
        """_post_init fängt Exception ab und loggt Fehler"""
        widget, mocks = _create_widget()
        mocks['theme_manager'].initialize_theme.side_effect = Exception("theme fail")
        with patch('views.einstellungen_widget.Logger') as mock_logger:
            widget._post_init(0)
            mock_logger.error.assert_any_call("Fehler bei Post-Initialisierung: theme fail")


class TestEinstellungenWidgetTheme(unittest.TestCase):
    """Tests für Theme-Delegation"""

    def test_switch_theme_style_delegates(self):
        """switch_theme_style delegiert an ThemeManager"""
        widget, mocks = _create_widget()
        widget.switch_theme_style('Dark')
        mocks['theme_manager'].switch_theme_style.assert_called_once_with('Dark')

    def test_switch_theme_style_returns_result(self):
        """switch_theme_style gibt Rückgabewert des ThemeManagers zurück"""
        widget, mocks = _create_widget()
        mocks['theme_manager'].switch_theme_style.return_value = True
        result = widget.switch_theme_style('Light')
        self.assertTrue(result)

    def test_switch_theme_style_no_manager(self):
        """switch_theme_style loggt Warnung wenn ThemeManager None"""
        widget, mocks = _create_widget()
        widget.theme_manager = None
        with patch('views.einstellungen_widget.Logger') as mock_logger:
            widget.switch_theme_style('Dark')
            mock_logger.warning.assert_called_with("ThemeManager nicht verfügbar")

    def test_on_color_selected_delegates(self):
        """on_color_selected delegiert an ThemeManager"""
        widget, mocks = _create_widget()
        widget.on_color_selected('Blue')
        mocks['theme_manager'].on_color_selected.assert_called_once_with('Blue')

    def test_on_color_selected_no_manager(self):
        """on_color_selected loggt Warnung wenn ThemeManager None"""
        widget, mocks = _create_widget()
        widget.theme_manager = None
        with patch('views.einstellungen_widget.Logger') as mock_logger:
            widget.on_color_selected('Blue')
            mock_logger.warning.assert_called_with("ThemeManager nicht verfügbar")

    def test_on_theme_changed_updates_chips(self):
        """_on_theme_changed ruft update_color_chips() auf"""
        widget, mocks = _create_widget()
        widget._on_theme_changed({'color': 'Red'})
        mocks['theme_manager'].update_color_chips.assert_called_once()

    def test_on_theme_changed_no_manager(self):
        """_on_theme_changed loggt Warnung wenn ThemeManager None"""
        widget, mocks = _create_widget()
        widget.theme_manager = None
        with patch('views.einstellungen_widget.Logger') as mock_logger:
            widget._on_theme_changed({})
            mock_logger.warning.assert_called_with(
                "ThemeManager nicht verfügbar für Theme-Update"
            )


class TestEinstellungenWidgetCharakter(unittest.TestCase):
    """Tests für Charakter-Methoden"""

    def test_get_charakter_value_success(self):
        """get_charakter_value liest Attribut vom Charakter"""
        widget, mocks = _create_widget()
        mocks['app'].controller.charakter.name = "Testname"
        result = widget.get_charakter_value('name', '')
        self.assertEqual(result, "Testname")

    def test_get_charakter_value_returns_string(self):
        """get_charakter_value gibt str zurück"""
        widget, mocks = _create_widget()
        mocks['app'].controller.charakter.wert = 42
        result = widget.get_charakter_value('wert', '')
        self.assertEqual(result, "42")

    def test_get_charakter_value_default(self):
        """get_charakter_value gibt default_value zurück wenn Attribut fehlt"""
        widget, mocks = _create_widget()
        # Damit getattr den default zurückgibt, muss das Attribut wirklich fehlen
        # Bei einem Mock existiert jedes Attribut, also spec verwenden
        mocks['app'].controller.charakter = Mock(spec=[])
        result = widget.get_charakter_value('nicht_vorhanden', 'fallback')
        self.assertEqual(result, 'fallback')

    def test_get_charakter_value_no_controller(self):
        """get_charakter_value gibt default_value zurück wenn kein Controller"""
        widget, mocks = _create_widget()
        mocks['app'].controller = None
        result = widget.get_charakter_value('name', 'default')
        self.assertEqual(result, 'default')



class TestEinstellungenWidgetDialoge(unittest.TestCase):
    """Tests für Dialog-Delegation via service_container"""

    def _make_widget_with_dialog_service(self):
        """Erstellt Widget mit gemocktem DialogService"""
        widget, mocks = _create_widget()
        mock_dialog_service = Mock()
        mocks['service_container'].get_dialog_service.return_value = mock_dialog_service
        return widget, mocks, mock_dialog_service

    def test_open_add_volk_dialog(self):
        """open_add_volk_dialog delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_add_volk_dialog()
            ds.open_add_volk_dialog.assert_called_once()

    def test_open_delete_volk_dialog(self):
        """open_delete_volk_dialog delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_delete_volk_dialog()
            ds.open_delete_volk_dialog.assert_called_once()

    def test_open_add_talent_popup(self):
        """open_add_talent_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_add_talent_popup()
            ds.open_add_talent_popup.assert_called_once()

    def test_open_delete_talent_popup(self):
        """open_delete_talent_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_delete_talent_popup()
            ds.open_delete_talent_popup.assert_called_once()

    def test_open_add_macht_popup(self):
        """open_add_macht_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_add_macht_popup()
            ds.open_add_macht_popup.assert_called_once()

    def test_open_delete_macht_popup(self):
        """open_delete_macht_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_delete_macht_popup()
            ds.open_delete_macht_popup.assert_called_once()

    def test_open_add_fertigkeit_popup(self):
        """open_add_fertigkeit_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_add_fertigkeit_popup()
            ds.open_add_fertigkeit_popup.assert_called_once()

    def test_open_delete_fertigkeit_popup(self):
        """open_delete_fertigkeit_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_delete_fertigkeit_popup()
            ds.open_delete_fertigkeit_popup.assert_called_once()

    def test_open_add_handicap_popup(self):
        """open_add_handicap_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_add_handicap_popup()
            ds.open_add_handicap_popup.assert_called_once()

    def test_open_delete_handicap_popup(self):
        """open_delete_handicap_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_delete_handicap_popup()
            ds.open_delete_handicap_popup.assert_called_once()

    def test_open_add_ausruestung_popup(self):
        """open_add_ausruestung_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_add_ausruestung_popup()
            ds.open_add_ausruestung_popup.assert_called_once()

    def test_open_delete_ausruestung_popup(self):
        """open_delete_ausruestung_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_delete_ausruestung_popup()
            ds.open_delete_ausruestung_popup.assert_called_once()

    def test_open_add_waffe_popup(self):
        """open_add_waffe_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_add_waffe_popup()
            ds.open_add_waffe_popup.assert_called_once()

    def test_open_delete_waffe_popup(self):
        """open_delete_waffe_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_delete_waffe_popup()
            ds.open_delete_waffe_popup.assert_called_once()

    def test_open_add_ruestung_popup(self):
        """open_add_ruestung_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_add_ruestung_popup()
            ds.open_add_ruestung_popup.assert_called_once()

    def test_open_delete_ruestung_popup(self):
        """open_delete_ruestung_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_delete_ruestung_popup()
            ds.open_delete_ruestung_popup.assert_called_once()

    def test_open_add_schild_popup(self):
        """open_add_schild_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_add_schild_popup()
            ds.open_add_schild_popup.assert_called_once()

    def test_open_delete_schild_popup(self):
        """open_delete_schild_popup delegiert an DialogService"""
        widget, mocks, ds = self._make_widget_with_dialog_service()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.open_delete_schild_popup()
            ds.open_delete_schild_popup.assert_called_once()

    def test_dialog_service_none_logs_warning(self):
        """Dialog-Methoden loggen Warnung wenn DialogService None"""
        widget, mocks, _ = self._make_widget_with_dialog_service()
        mocks['service_container'].get_dialog_service.return_value = None
        with patch('views.einstellungen_widget.service_container', mocks['service_container']), \
             patch('views.einstellungen_widget.Logger') as mock_logger:
            widget.open_add_volk_dialog()
            mock_logger.warning.assert_called_with(
                "DialogService nicht verfügbar - Volk hinzufügen nicht möglich"
            )


class TestEinstellungenWidgetLog(unittest.TestCase):
    """Tests für Log-Funktionen"""

    def test_open_log_file_no_filepath(self):
        """open_log_file kehrt zurück wenn log_filepath None"""
        widget, mocks = _create_widget()
        mocks['app'].log_filepath = None
        with patch('views.einstellungen_widget.Logger'):
            widget.open_log_file()

    def test_open_log_file_no_attr(self):
        """open_log_file kehrt zurück wenn log_filepath Attribut fehlt"""
        widget, mocks = _create_widget()
        del mocks['app'].log_filepath
        with patch('views.einstellungen_widget.Logger'):
            widget.open_log_file()

    def test_open_log_file_success(self):
        """open_log_file liest Datei und kopiert in Zwischenablage (Desktop)"""
        widget, mocks = _create_widget()
        mocks['app'].log_filepath = '/tmp/test.log'

        log_content = "Line1\nLine2\nLine3"
        with patch('views.einstellungen_widget.Logger'), \
             patch('views.einstellungen_widget.os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=log_content)), \
             patch.object(widget, '_copy_to_clipboard') as mock_copy:
            widget.open_log_file()
            mock_copy.assert_called_once()
            copied_text = mock_copy.call_args[0][0]
            self.assertIn("Line1", copied_text)
            self.assertIn("Session Log", copied_text)

    def test_open_log_file_includes_header(self):
        """open_log_file fügt Header mit Dateiinfo hinzu"""
        widget, mocks = _create_widget()
        mocks['app'].log_filepath = '/tmp/test.log'

        with patch('views.einstellungen_widget.Logger'), \
             patch('views.einstellungen_widget.os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="content")), \
             patch.object(widget, '_copy_to_clipboard') as mock_copy:
            widget.open_log_file()
            copied_text = mock_copy.call_args[0][0]
            self.assertIn("test.log", copied_text)
            self.assertIn("Zeichen", copied_text)

    def test_open_log_file_read_error(self):
        """open_log_file fängt Lese-Fehler ab"""
        widget, mocks = _create_widget()
        mocks['app'].log_filepath = '/tmp/test.log'

        with patch('views.einstellungen_widget.Logger') as mock_logger, \
             patch('views.einstellungen_widget.os.path.exists', return_value=True), \
             patch('builtins.open', side_effect=IOError("read fail")):
            widget.open_log_file()
            mock_logger.error.assert_called()

    def test_copy_to_clipboard_posix(self):
        """_copy_to_clipboard nutzt xclip auf POSIX"""
        widget, mocks = _create_widget()
        with patch('views.einstellungen_widget.os.name', 'posix'), \
             patch('kivy.utils.platform', 'linux'), \
             patch('subprocess.run') as mock_run:
            widget._copy_to_clipboard("test text")
            mock_run.assert_called()

    def test_copy_to_clipboard_android(self):
        """_copy_to_clipboard nutzt Kivy Clipboard auf Android"""
        widget, mocks = _create_widget()
        mock_clipboard = MagicMock()
        with patch('kivy.utils.platform', 'android'), \
             patch('kivy.core.clipboard.Clipboard', mock_clipboard), \
             patch('builtins.open', mock_open()):
            widget._copy_to_clipboard("test text")
            mock_clipboard.copy.assert_called_once_with("test text")

    def test_copy_to_clipboard_error_reraises(self):
        """_copy_to_clipboard wirft Exception weiter bei Fehler"""
        widget, mocks = _create_widget()
        # Patch den Import von kivy.utils innerhalb der Methode
        with patch.dict('sys.modules', {'kivy.utils': MagicMock(platform='linux')}), \
             patch('views.einstellungen_widget.os.name', 'posix'), \
             patch('subprocess.run', side_effect=Exception("xclip fail")), \
             patch('kivy.core.clipboard.Clipboard.copy', side_effect=Exception("clipboard fail")):
            with self.assertRaises(Exception):
                widget._copy_to_clipboard("text")


class TestEinstellungenWidgetCleanup(unittest.TestCase):
    """Tests für Cleanup/on_stop"""

    def test_on_stop_unsubscribes_events(self):
        """on_stop deregistriert THEME_CHANGED Event-Handler"""
        widget, mocks = _create_widget()
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            widget.on_stop()
            mocks['event_service'].unsubscribe.assert_called_once_with(
                EventTypes.THEME_CHANGED, widget._on_theme_changed
            )

    def test_on_stop_no_event_service(self):
        """on_stop funktioniert wenn kein EventService verfügbar"""
        widget, mocks = _create_widget()
        mocks['service_container'].get_event_service.return_value = None
        with patch('views.einstellungen_widget.service_container', mocks['service_container']):
            # Soll keine Exception werfen
            widget.on_stop()

    def test_on_stop_error_handling(self):
        """on_stop fängt Exception ab"""
        widget, mocks = _create_widget()
        mocks['service_container'].get_event_service.side_effect = Exception("cleanup fail")
        with patch('views.einstellungen_widget.service_container', mocks['service_container']), \
             patch('views.einstellungen_widget.Logger') as mock_logger:
            widget.on_stop()
            mock_logger.error.assert_any_call("Fehler beim Bereinigen: cleanup fail")


if __name__ == '__main__':
    unittest.main()
