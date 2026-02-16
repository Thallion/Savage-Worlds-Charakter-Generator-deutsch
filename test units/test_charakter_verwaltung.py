# tests/test_charakter_verwaltung.py
"""
Unit Tests für CharakterVerwaltungScreen und CharakterVerwaltungWidget
Testet Screen-Delegation, Handler/Manager-Initialisierung, Charakter-CRUD,
Template-Management, UI-Updates und Cleanup.
"""

import unittest
import sys
from unittest.mock import Mock, MagicMock, patch, PropertyMock

# KivyMD Chip-Modul hat einen Metaclass-Konflikt - vor allem anderen mocken
for _mod in ['kivymd.uix.chip', 'kivymd.uix.chip.chip']:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

# Builder.load_file mocken (verhindert KV-Datei-Laden ohne laufende App)
with patch('kivy.lang.Builder.load_file'):
    from views.charakter_verwaltung_widget import CharakterVerwaltungWidget

from views.screens import CharakterVerwaltungScreen
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
    """Erstellt ein CharakterVerwaltungWidget mit komplett gemockten Abhängigkeiten.

    Returns:
        tuple: (widget, mocks_dict) mit allen relevanten Mocks
    """
    mock_app = Mock()
    mock_app.controller = Mock()
    mock_app.controller.charakter = Mock()

    mock_char_handler = Mock()
    mock_tmpl_handler = Mock()
    mock_stats_mgr = Mock()
    mock_pdf_mgr = Mock()
    mock_event_service = Mock()
    mock_sc = Mock()
    mock_sc.get_event_service.return_value = mock_event_service
    mock_sc.get_dialog_service.return_value = Mock()

    with patch('views.charakter_verwaltung_widget.MDBoxLayout.__init__', lambda self, **kw: None), \
         patch('views.charakter_verwaltung_widget.MDApp') as mock_mdapp, \
         patch('views.charakter_verwaltung_widget.Clock') as mock_clock, \
         patch('views.charakter_verwaltung_widget.CharacterHandler', return_value=mock_char_handler), \
         patch('views.charakter_verwaltung_widget.TemplateHandler', return_value=mock_tmpl_handler), \
         patch('views.charakter_verwaltung_widget.StatisticsManager', return_value=mock_stats_mgr), \
         patch('views.charakter_verwaltung_widget.PDFManager', return_value=mock_pdf_mgr), \
         patch('views.charakter_verwaltung_widget.service_container', mock_sc):

        mock_mdapp.get_running_app.return_value = mock_app
        widget = CharakterVerwaltungWidget()

    mocks = {
        'app': mock_app,
        'character_handler': mock_char_handler,
        'template_handler': mock_tmpl_handler,
        'statistics_manager': mock_stats_mgr,
        'pdf_manager': mock_pdf_mgr,
        'event_service': mock_event_service,
        'service_container': mock_sc,
        'clock': mock_clock,
    }
    return widget, mocks


def _create_screen():
    """Erstellt einen CharakterVerwaltungScreen mit gemocktem __init__.

    Returns:
        CharakterVerwaltungScreen mit gemockten ids
    """
    with patch('views.screens.MDScreen.__init__', lambda self, **kw: None):
        screen = CharakterVerwaltungScreen()
    return screen


# ==================== SCREEN TESTS ====================

class TestCharakterVerwaltungScreen(unittest.TestCase):
    """Tests für CharakterVerwaltungScreen Delegation"""

    def test_refresh_widget_delegates_to_widget(self):
        """refresh_widget delegiert an charakter_verwaltung_widget"""
        screen = _create_screen()
        mock_widget = Mock()
        screen.ids = _AttrDict(charakter_verwaltung_widget=mock_widget)
        result = screen.refresh_widget()
        mock_widget.refresh_widget.assert_called_once()
        self.assertTrue(result)

    def test_refresh_widget_returns_false_no_widget_id(self):
        """refresh_widget gibt False zurück wenn Widget-ID fehlt"""
        screen = _create_screen()
        screen.ids = _AttrDict()
        result = screen.refresh_widget()
        self.assertFalse(result)

    def test_refresh_widget_returns_false_widget_none(self):
        """refresh_widget gibt False zurück wenn Widget None ist"""
        screen = _create_screen()
        screen.ids = _AttrDict(charakter_verwaltung_widget=None)
        result = screen.refresh_widget()
        self.assertFalse(result)

    def test_refresh_widget_returns_false_no_refresh_method(self):
        """refresh_widget gibt False zurück wenn Widget kein refresh_widget hat"""
        screen = _create_screen()
        mock_widget = Mock(spec=[])  # Kein refresh_widget Attribut
        screen.ids = _AttrDict(charakter_verwaltung_widget=mock_widget)
        result = screen.refresh_widget()
        self.assertFalse(result)

    def test_refresh_widget_exception_returns_false(self):
        """refresh_widget fängt Exception ab und gibt False zurück"""
        screen = _create_screen()
        mock_widget = Mock()
        mock_widget.refresh_widget.side_effect = Exception("test error")
        screen.ids = _AttrDict(charakter_verwaltung_widget=mock_widget)
        result = screen.refresh_widget()
        self.assertFalse(result)

    def test_aktualisiere_ui_delegates_to_refresh_widget(self):
        """aktualisiere_ui ist Alias für refresh_widget"""
        screen = _create_screen()
        mock_widget = Mock()
        screen.ids = _AttrDict(charakter_verwaltung_widget=mock_widget)
        result = screen.aktualisiere_ui()
        mock_widget.refresh_widget.assert_called_once()
        self.assertTrue(result)


# ==================== WIDGET INIT TESTS ====================

class TestCharakterVerwaltungWidgetInit(unittest.TestCase):
    """Tests für Widget-Initialisierung"""

    def test_init_sets_app(self):
        """__init__ setzt self.app über MDApp.get_running_app()"""
        widget, mocks = _create_widget()
        self.assertEqual(widget.app, mocks['app'])

    def test_init_sets_character_handler(self):
        """__init__ erstellt CharacterHandler"""
        widget, mocks = _create_widget()
        self.assertEqual(widget.character_handler, mocks['character_handler'])

    def test_init_sets_template_handler(self):
        """__init__ erstellt TemplateHandler"""
        widget, mocks = _create_widget()
        self.assertEqual(widget.template_handler, mocks['template_handler'])

    def test_init_sets_managers(self):
        """__init__ erstellt StatisticsManager und PDFManager"""
        widget, mocks = _create_widget()
        self.assertEqual(widget.statistics_manager, mocks['statistics_manager'])
        self.assertEqual(widget.pdf_manager, mocks['pdf_manager'])

    def test_init_schedules_post_init(self):
        """__init__ plant _post_init via Clock.schedule_once"""
        widget, mocks = _create_widget()
        mocks['clock'].schedule_once.assert_called_once_with(widget._post_init, 0)

    def test_initialize_handlers_error(self):
        """_initialize_handlers fängt Exception ab und loggt Fehler"""
        with patch('views.charakter_verwaltung_widget.MDBoxLayout.__init__', lambda self, **kw: None), \
             patch('views.charakter_verwaltung_widget.MDApp') as mock_mdapp, \
             patch('views.charakter_verwaltung_widget.Clock'), \
             patch('views.charakter_verwaltung_widget.CharacterHandler', side_effect=Exception("handler fail")), \
             patch('views.charakter_verwaltung_widget.TemplateHandler', return_value=Mock()), \
             patch('views.charakter_verwaltung_widget.StatisticsManager', return_value=Mock()), \
             patch('views.charakter_verwaltung_widget.PDFManager', return_value=Mock()), \
             patch('views.charakter_verwaltung_widget.service_container', Mock()), \
             patch('views.charakter_verwaltung_widget.Logger') as mock_logger:

            mock_mdapp.get_running_app.return_value = Mock()
            widget = CharakterVerwaltungWidget()
            mock_logger.error.assert_any_call("Fehler bei Handler-Initialisierung: handler fail")

    def test_initialize_managers_error_sets_none(self):
        """_initialize_managers setzt Manager auf None bei Fehler"""
        with patch('views.charakter_verwaltung_widget.MDBoxLayout.__init__', lambda self, **kw: None), \
             patch('views.charakter_verwaltung_widget.MDApp') as mock_mdapp, \
             patch('views.charakter_verwaltung_widget.Clock'), \
             patch('views.charakter_verwaltung_widget.CharacterHandler', return_value=Mock()), \
             patch('views.charakter_verwaltung_widget.TemplateHandler', return_value=Mock()), \
             patch('views.charakter_verwaltung_widget.StatisticsManager', side_effect=Exception("mgr fail")), \
             patch('views.charakter_verwaltung_widget.service_container', Mock()), \
             patch('views.charakter_verwaltung_widget.Logger'):

            mock_mdapp.get_running_app.return_value = Mock()
            widget = CharakterVerwaltungWidget()
            self.assertIsNone(widget.statistics_manager)
            self.assertIsNone(widget.pdf_manager)

    def test_register_event_handlers_subscribes(self):
        """_register_event_handlers abonniert CHARACTER_CREATED und CHARACTER_LOADED"""
        widget, mocks = _create_widget()
        mocks['event_service'].subscribe.assert_any_call(
            EventTypes.CHARACTER_CREATED, mocks['character_handler'].on_character_created
        )
        mocks['event_service'].subscribe.assert_any_call(
            EventTypes.CHARACTER_LOADED, mocks['character_handler'].on_character_loaded
        )

    def test_register_event_handlers_no_event_service(self):
        """_register_event_handlers funktioniert wenn kein EventService"""
        with patch('views.charakter_verwaltung_widget.MDBoxLayout.__init__', lambda self, **kw: None), \
             patch('views.charakter_verwaltung_widget.MDApp') as mock_mdapp, \
             patch('views.charakter_verwaltung_widget.Clock'), \
             patch('views.charakter_verwaltung_widget.CharacterHandler', return_value=Mock()), \
             patch('views.charakter_verwaltung_widget.TemplateHandler', return_value=Mock()), \
             patch('views.charakter_verwaltung_widget.StatisticsManager', return_value=Mock()), \
             patch('views.charakter_verwaltung_widget.PDFManager', return_value=Mock()), \
             patch('views.charakter_verwaltung_widget.service_container') as mock_sc:

            mock_sc.get_event_service.return_value = None
            mock_mdapp.get_running_app.return_value = Mock()
            # Soll keine Exception werfen
            widget = CharakterVerwaltungWidget()


# ==================== POST-INIT TESTS ====================

class TestCharakterVerwaltungWidgetPostInit(unittest.TestCase):
    """Tests für Post-Initialisierung"""

    def test_post_init_updates_statistics(self):
        """_post_init ruft statistics_manager.update_element_statistics_ui() auf"""
        widget, mocks = _create_widget()
        widget._post_init(0)
        mocks['statistics_manager'].update_element_statistics_ui.assert_called_once()

    def test_post_init_no_statistics_manager(self):
        """_post_init funktioniert wenn statistics_manager None ist"""
        widget, mocks = _create_widget()
        widget.statistics_manager = None
        # Soll keine Exception werfen
        widget._post_init(0)

    def test_post_init_error_handling(self):
        """_post_init fängt Exception ab und loggt Fehler"""
        widget, mocks = _create_widget()
        mocks['statistics_manager'].update_element_statistics_ui.side_effect = Exception("stats fail")
        with patch('views.charakter_verwaltung_widget.Logger') as mock_logger:
            widget._post_init(0)
            mock_logger.error.assert_any_call("Fehler bei Post-Initialisierung: stats fail")


# ==================== CHARAKTER-DELEGATION TESTS ====================

class TestCharakterVerwaltungWidgetCharakter(unittest.TestCase):
    """Tests für Charakter-CRUD-Delegation an CharacterHandler"""

    def test_get_charakter_value_delegates(self):
        """get_charakter_value delegiert an character_handler"""
        widget, mocks = _create_widget()
        mocks['character_handler'].get_charakter_value.return_value = "Testname"
        result = widget.get_charakter_value('name', '')
        mocks['character_handler'].get_charakter_value.assert_called_once_with('name', '')
        self.assertEqual(result, "Testname")

    def test_create_new_character_delegates(self):
        """create_new_character delegiert an character_handler"""
        widget, mocks = _create_widget()
        widget.create_new_character()
        mocks['character_handler'].create_new_character.assert_called_once()

    def test_schnellspeichern_charakter_delegates(self):
        """schnellspeichern_charakter delegiert an character_handler"""
        widget, mocks = _create_widget()
        widget.schnellspeichern_charakter()
        mocks['character_handler'].schnellspeichern_charakter.assert_called_once()

    def test_speichere_charakter_delegates(self):
        """speichere_charakter delegiert an character_handler"""
        widget, mocks = _create_widget()
        widget.speichere_charakter()
        mocks['character_handler'].speichere_charakter.assert_called_once()

    def test_lade_charakter_delegates(self):
        """lade_charakter delegiert an character_handler"""
        widget, mocks = _create_widget()
        widget.lade_charakter()
        mocks['character_handler'].lade_charakter.assert_called_once()

    def test_erzeuge_charakterbogen_pdf_delegates(self):
        """erzeuge_charakterbogen_pdf delegiert an character_handler"""
        widget, mocks = _create_widget()
        widget.erzeuge_charakterbogen_pdf()
        mocks['character_handler'].erzeuge_charakterbogen_pdf.assert_called_once()

    def test_zeige_statblock_delegates(self):
        """zeige_statblock delegiert an character_handler"""
        widget, mocks = _create_widget()
        widget.zeige_statblock()
        mocks['character_handler'].zeige_statblock.assert_called_once()

    def test_zeige_element_statistiken_delegates(self):
        """zeige_element_statistiken delegiert an character_handler"""
        widget, mocks = _create_widget()
        widget.zeige_element_statistiken()
        mocks['character_handler'].zeige_element_statistiken.assert_called_once()

    def test_delegation_returns_handler_result(self):
        """Delegations-Methoden geben den Rückgabewert des Handlers zurück"""
        widget, mocks = _create_widget()
        mocks['character_handler'].create_new_character.return_value = "new_char"
        result = widget.create_new_character()
        self.assertEqual(result, "new_char")


# ==================== TEMPLATE-MANAGEMENT TESTS ====================

class TestCharakterVerwaltungWidgetTemplate(unittest.TestCase):
    """Tests für Template-Delegation und Template-Wizard"""

    def test_open_template_selection_dialog_delegates(self):
        """open_template_selection_dialog delegiert an template_handler"""
        widget, mocks = _create_widget()
        widget.open_template_selection_dialog()
        mocks['template_handler'].open_template_selection_dialog.assert_called_once()

    def test_show_template_selection_dialog_delegates(self):
        """show_template_selection_dialog delegiert an template_handler"""
        widget, mocks = _create_widget()
        widget.show_template_selection_dialog()
        mocks['template_handler'].show_template_selection_dialog.assert_called_once()

    def test_generate_character_from_selected_template_delegates(self):
        """generate_character_from_selected_template delegiert an template_handler"""
        widget, mocks = _create_widget()
        widget.generate_character_from_selected_template()
        mocks['template_handler'].generate_character_from_selected_template.assert_called_once()

    def test_selected_template_property_returns_handler_value(self):
        """selected_template Property gibt Wert vom template_handler zurück"""
        widget, mocks = _create_widget()
        mocks['template_handler'].selected_template = {'name': 'Test Template'}
        result = widget.selected_template
        self.assertEqual(result, {'name': 'Test Template'})

    def test_selected_template_property_no_handler(self):
        """selected_template gibt None zurück wenn kein template_handler"""
        widget, mocks = _create_widget()
        widget.template_handler = None
        result = widget.selected_template
        self.assertIsNone(result)

    def test_selected_template_property_no_attr(self):
        """selected_template gibt None zurück wenn template_handler kein Attribut hat"""
        widget, mocks = _create_widget()
        del widget.template_handler
        result = widget.selected_template
        self.assertIsNone(result)

    def test_create_template_wizard_calls_show(self):
        """create_template_wizard ruft show_template_wizard auf"""
        widget, mocks = _create_widget()
        with patch('views.charakter_verwaltung_widget.show_template_wizard', create=True) as mock_show:
            # Patch den Import innerhalb der Methode
            with patch.dict('sys.modules', {'views.template_wizard': MagicMock(show_template_wizard=mock_show)}):
                widget.create_template_wizard()
                mock_show.assert_called_once()

    def test_create_template_wizard_error_shows_dialog(self):
        """create_template_wizard zeigt Fehler-Dialog bei Exception"""
        widget, mocks = _create_widget()
        mock_dialog_service = Mock()

        # show_template_wizard wirft Exception
        mock_wizard_module = MagicMock()
        mock_wizard_module.show_template_wizard.side_effect = Exception("wizard fail")

        mock_sc = Mock()
        mock_sc.get_dialog_service.return_value = mock_dialog_service

        with patch.dict('sys.modules', {'views.template_wizard': mock_wizard_module}):
            # Patch sowohl modul-level als auch den Re-Import im except-Block
            with patch('views.charakter_verwaltung_widget.service_container', mock_sc), \
                 patch('services.service_container.service_container', mock_sc):
                widget.create_template_wizard()
                mock_dialog_service.show_error_dialog.assert_called_once()

    def test_create_template_wizard_callback_updates_handler(self):
        """Template-Wizard Callback aktualisiert template_handler"""
        widget, mocks = _create_widget()

        captured_callback = None

        def capture_show(callback=None):
            nonlocal captured_callback
            captured_callback = callback

        mock_wizard_module = MagicMock()
        mock_wizard_module.show_template_wizard = capture_show

        with patch.dict('sys.modules', {'views.template_wizard': mock_wizard_module}):
            with patch('views.charakter_verwaltung_widget.service_container') as mock_sc:
                mock_sc.get_dialog_service.return_value = Mock()
                widget.create_template_wizard()

        self.assertIsNotNone(captured_callback)

        # Callback ausführen
        with patch('views.charakter_verwaltung_widget.service_container') as mock_sc:
            mock_sc.get_dialog_service.return_value = Mock()
            captured_callback('/path/to/template.json', {'name': 'My Template'})

        mocks['template_handler']._load_templates.assert_called_once()
        self.assertEqual(mocks['template_handler'].selected_template, {
            'name': 'My Template',
            'path': '/path/to/template.json',
            'data': {'name': 'My Template'}
        })


# ==================== UI UPDATE TESTS ====================

class TestCharakterVerwaltungWidgetUI(unittest.TestCase):
    """Tests für UI-Update-Methoden"""

    def test_refresh_widget_calls_statistics(self):
        """refresh_widget ruft statistics_manager.update_element_statistics_ui() auf"""
        widget, mocks = _create_widget()
        widget.refresh_widget()
        mocks['statistics_manager'].update_element_statistics_ui.assert_called()

    def test_refresh_widget_no_statistics_manager(self):
        """refresh_widget funktioniert wenn statistics_manager None ist"""
        widget, mocks = _create_widget()
        widget.statistics_manager = None
        # Soll keine Exception werfen
        widget.refresh_widget()

    def test_refresh_widget_error_handling(self):
        """refresh_widget fängt Exception ab"""
        widget, mocks = _create_widget()
        mocks['statistics_manager'].update_element_statistics_ui.side_effect = Exception("ui fail")
        with patch('views.charakter_verwaltung_widget.Logger') as mock_logger:
            widget.refresh_widget()
            mock_logger.error.assert_any_call(
                "Fehler beim Aktualisieren des CharakterVerwaltungWidgets: ui fail"
            )

    def test_aktualisiere_ui_delegates_to_refresh(self):
        """aktualisiere_ui ruft refresh_widget auf"""
        widget, mocks = _create_widget()
        with patch.object(widget, 'refresh_widget') as mock_refresh:
            widget.aktualisiere_ui()
            mock_refresh.assert_called_once()


# ==================== CLEANUP TESTS ====================

class TestCharakterVerwaltungWidgetCleanup(unittest.TestCase):
    """Tests für Cleanup/on_stop"""

    def test_on_stop_unsubscribes_events(self):
        """on_stop deregistriert CHARACTER_CREATED und CHARACTER_LOADED"""
        widget, mocks = _create_widget()
        with patch('views.charakter_verwaltung_widget.service_container', mocks['service_container']):
            widget.on_stop()
            mocks['event_service'].unsubscribe.assert_any_call(
                EventTypes.CHARACTER_CREATED, mocks['character_handler'].on_character_created
            )
            mocks['event_service'].unsubscribe.assert_any_call(
                EventTypes.CHARACTER_LOADED, mocks['character_handler'].on_character_loaded
            )

    def test_on_stop_no_event_service(self):
        """on_stop funktioniert wenn kein EventService verfügbar"""
        widget, mocks = _create_widget()
        mocks['service_container'].get_event_service.return_value = None
        with patch('views.charakter_verwaltung_widget.service_container', mocks['service_container']):
            # Soll keine Exception werfen
            widget.on_stop()

    def test_on_stop_error_handling(self):
        """on_stop fängt Exception ab"""
        widget, mocks = _create_widget()
        mocks['service_container'].get_event_service.side_effect = Exception("cleanup fail")
        with patch('views.charakter_verwaltung_widget.service_container', mocks['service_container']), \
             patch('views.charakter_verwaltung_widget.Logger') as mock_logger:
            widget.on_stop()
            mock_logger.error.assert_any_call("Fehler beim Bereinigen: cleanup fail")


if __name__ == '__main__':
    unittest.main()
