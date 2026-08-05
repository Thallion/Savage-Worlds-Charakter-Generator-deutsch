# test units/test_popup_basis.py
"""
Tests für den BasisDialogHandler (views/popup_basis.py).

Testet das gemeinsame Gerüst der Element-Dialog-Handler ohne echte
KivyMD-Dialoge: Lösch-Flow Phase 1 (_on_delete_action_clicked),
dismiss_dialog mit _reset_selection-Hook, show_error-Fallback und
die beiden Dismiss-Timing-Varianten.
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

os.environ.setdefault('KIVY_NO_ARGS', '1')
os.environ.setdefault('KIVY_NO_CONSOLELOG', '1')
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# KivyMD Chip-Modul hat einen Metaclass-Konflikt - vor allem anderen mocken
for _mod in ['kivymd.uix.chip', 'kivymd.uix.chip.chip']:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

from views.popup_basis import BasisDialogHandler, SofortDismissMixin


class _TestHandler(BasisDialogHandler):
    """Minimaler Test-Handler mit den Pflicht-Hooks."""
    element_name = "Waffe"
    element_name_plural = "Waffen"
    artikel_unbestimmt = "eine"

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_element = "etwas"
        self.geloescht = False

    def _get_loeschbare_elemente(self):
        return ["Schwert", "Dolch"]

    def _confirm_delete_elemente(self):
        self.geloescht = True

    def _reset_selection(self):
        self.selected_element = None


class TestDismissDialog(unittest.TestCase):
    def test_dismiss_schliesst_overlay_und_reset(self):
        handler = _TestHandler(Mock())
        overlay = Mock()
        overlay._is_open = True
        handler.overlay = overlay
        handler.dialog_content = Mock()

        handler.dismiss_dialog()

        overlay.close.assert_called_once()
        self.assertIsNone(handler.dialog_content)
        self.assertIsNone(handler.selected_element)

    def test_dismiss_ohne_offenes_overlay(self):
        handler = _TestHandler(Mock())
        overlay = Mock()
        overlay._is_open = False
        handler.overlay = overlay

        handler.dismiss_dialog()

        overlay.close.assert_not_called()
        self.assertIsNone(handler.selected_element)


class TestDeleteFlowPhase1(unittest.TestCase):
    """Phase 1 bekommt die Auswahl als Namensliste vom SearchBottomSheet."""

    def _handler(self):
        handler = _TestHandler(Mock())
        handler._delete_popup = Mock()
        handler.show_error = Mock()
        handler._show_delete_confirmation_popup = Mock()
        return handler

    def test_keine_auswahl_zeigt_fehler(self):
        handler = self._handler()

        handler._on_delete_action_clicked([])

        handler.show_error.assert_called_once()
        meldung = handler.show_error.call_args[0][0]
        self.assertIn("mindestens eine Waffe", meldung)
        handler._show_delete_confirmation_popup.assert_not_called()

    def test_auswahl_oeffnet_bestaetigung(self):
        handler = self._handler()

        with patch('views.popup_basis.Clock') as mock_clock:
            handler._on_delete_action_clicked(["Schwert"])

            handler.show_error.assert_not_called()
            self.assertEqual(handler._pending_delete_items, ["Schwert"])
            # Phase 2 erst im nächsten Frame (Sheet schließt gerade)
            handler._show_delete_confirmation_popup.assert_not_called()
            mock_clock.schedule_once.assert_called_once()
            mock_clock.schedule_once.call_args[0][0](0)

        kwargs = handler._show_delete_confirmation_popup.call_args[1]
        self.assertEqual(kwargs['selected_items'], ["Schwert"])
        self.assertEqual(kwargs['item_type'], "Waffe")
        self.assertEqual(kwargs['on_confirm'], handler._confirm_delete_elemente)

    def test_show_delete_dialog_oeffnet_bottomsheet(self):
        """Phase 1 nutzt SearchBottomSheet (ModalView), nicht MDDialog."""
        handler = _TestHandler(Mock())
        sheet = Mock()
        sheet_cls = Mock(return_value=sheet)

        with patch.dict(sys.modules, {'views.ui_components': MagicMock(SearchBottomSheet=sheet_cls)}):
            handler.show_delete_dialog()

        sheet.open.assert_called_once()
        kwargs = sheet_cls.call_args[1]
        self.assertTrue(kwargs['multi_select'])
        self.assertEqual(kwargs['items'], ["Dolch", "Schwert"])
        self.assertEqual(kwargs['on_confirm'], handler._on_delete_action_clicked)

    def test_show_delete_dialog_ohne_elemente_zeigt_fehler(self):
        handler = _TestHandler(Mock())
        handler._get_loeschbare_elemente = lambda: []
        handler.show_error = Mock()

        handler.show_delete_dialog()

        handler.show_error.assert_called_once()
        self.assertIn("Keine Waffen", handler.show_error.call_args[0][0])


class TestShowError(unittest.TestCase):
    @patch('services.service_container.service_container')
    def test_nutzt_dialog_service(self, mock_sc):
        dialog_service = Mock()
        mock_sc.get_dialog_service.return_value = dialog_service
        handler = _TestHandler(Mock())

        handler.show_error("Testfehler")

        dialog_service.show_warning_dialog.assert_called_once_with("Testfehler")

    @patch('services.service_container.service_container')
    def test_faellt_auf_logger_zurueck(self, mock_sc):
        mock_sc.get_dialog_service.side_effect = RuntimeError("kein Service")
        handler = _TestHandler(Mock())

        # Darf keine Exception werfen
        handler.show_error("Testfehler")

    @patch('services.service_container.service_container')
    def test_snackbar_nutzt_dialog_service(self, mock_sc):
        dialog_service = Mock()
        mock_sc.get_dialog_service.return_value = dialog_service
        handler = _TestHandler(Mock())

        handler._show_success_snackbar("Gespeichert")

        dialog_service.show_success_dialog.assert_called_once_with("Gespeichert")


class TestConfirmPopupCallbacks(unittest.TestCase):
    """Beide Dismiss-Timing-Varianten planen die richtigen Clock-Aufrufe."""

    def test_gestaffelte_variante(self):
        handler = _TestHandler(Mock())
        dismiss_fn = Mock()
        on_confirm = Mock()
        with patch('views.popup_basis.Clock') as mock_clock:
            _on_cancel, _on_confirm_release = handler._confirm_popup_callbacks(dismiss_fn, on_confirm)

            _on_cancel(None)
            self.assertEqual(mock_clock.schedule_once.call_count, 2)
            # Gestaffelt: kein synchroner Dismiss im on_release-Handler
            dismiss_fn.assert_not_called()

            mock_clock.reset_mock()
            _on_confirm_release(None)
            self.assertEqual(mock_clock.schedule_once.call_count, 3)
            dismiss_fn.assert_not_called()
            on_confirm.assert_not_called()  # erst verzögert über Clock

    def test_sofort_variante(self):
        class _SofortHandler(SofortDismissMixin, _TestHandler):
            pass

        handler = _SofortHandler(Mock())
        dismiss_fn = Mock()
        on_confirm = Mock()
        with patch('views.popup_basis.Clock') as mock_clock:
            _on_cancel, _on_confirm_release = handler._confirm_popup_callbacks(dismiss_fn, on_confirm)

            _on_cancel(None)
            dismiss_fn.assert_called_once()  # sofortiger Versuch
            self.assertEqual(mock_clock.schedule_once.call_count, 1)

            dismiss_fn.reset_mock()
            mock_clock.reset_mock()
            _on_confirm_release(None)
            dismiss_fn.assert_called_once()
            self.assertEqual(mock_clock.schedule_once.call_count, 2)
            on_confirm.assert_not_called()  # erst verzögert über Clock


if __name__ == '__main__':
    unittest.main()
