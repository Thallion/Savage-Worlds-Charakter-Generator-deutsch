# fertigkeit-popup.py
"""
Dialog-Handler für Fertigkeiten (Add/Delete).

Add läuft deklarativ über FormDialogHandlerMixin (views/popup_form.py),
der Two-Phase-Lösch-Flow über BasisDialogHandler (views/popup_basis.py).
"""
from kivy.app import App
from kivy.logger import Logger

from models.fertigkeit import Fertigkeit
from views.popup_basis import BasisDialogHandler, SofortDismissMixin
from views.popup_form import FormDialogHandlerMixin


class FertigkeitDialogHandler(FormDialogHandlerMixin, SofortDismissMixin, BasisDialogHandler):
    element_name = "Fertigkeit"
    element_name_plural = "Fertigkeiten"
    artikel_unbestimmt = "eine"
    titel_neu = "Neue Fertigkeit hinzufügen"

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_fertigkeit = None

    def _get_felder(self):
        return [
            {"key": "name", "label": "Name der Fertigkeit", "typ": "text", "pflicht": True,
             "pflicht_meldung": "Der Name der Fertigkeit darf nicht leer sein."},
            {"key": "attribut", "label": "Attribut wählen", "typ": "dropdown",
             "optionen": self._get_attribut_namen, "pflicht": True,
             "pflicht_meldung": "Bitte wähle ein Attribut aus."},
            {"key": "grundfertigkeit", "label": "Grundfertigkeit", "typ": "checkbox"},
        ]

    def _get_attribut_namen(self):
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            return list(charakter.get_attribute_dict().keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Attribute: {e}")
            return []

    def _get_loeschbare_elemente(self):
        return self.get_all_fertigkeiten()

    def _reset_selection(self):
        self.selected_fertigkeit = None

    # ------------------------------------------------------------------
    # Add-Hook (FormDialogHandlerMixin) — Fertigkeiten haben keinen Edit-Flow
    # ------------------------------------------------------------------
    def _erstelle_element(self, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        name = werte['name']
        if name in charakter.fertigkeiten:
            self.show_error(f"Fertigkeit '{name}' existiert bereits.")
            return False

        attribut = charakter.get_attribute_dict().get(werte['attribut'])
        if attribut is None:
            self.show_error(f"Attribut '{werte['attribut']}' nicht gefunden.")
            return False

        new_fertigkeit = Fertigkeit(
            fertigkeit_name=name,
            attribut=attribut,
            grundfertigkeit=werte['grundfertigkeit'],
            custom=True
        )

        charakter.add_fertigkeit(new_fertigkeit)
        charakter.save_custom_fertigkeiten()
        return True

    # ------------------------------------------------------------------
    # Lösch-Flow (BasisDialogHandler)
    # ------------------------------------------------------------------
    def _confirm_delete_elemente(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch"""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            for fertigkeit_name in selected:
                charakter.remove_fertigkeit(fertigkeit_name)
                Logger.info(f"Fertigkeit '{fertigkeit_name}' wurde gelöscht.")

            charakter.save_custom_fertigkeiten()

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_fertigkeit_view()
            self._show_success_snackbar(f"{len(selected)} Fertigkeit(en) gelöscht")

            Logger.info(f"{len(selected)} Fertigkeit(en) wurde(n) gelöscht.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Fertigkeiten: {e}")
            self.show_error("Fehler beim Löschen der Fertigkeiten")

    def on_fertigkeit_select(self, fertigkeit_name):
        """Callback wenn eine Fertigkeit im Dropdown ausgewählt wurde"""
        self.selected_fertigkeit = fertigkeit_name

    def get_all_fertigkeiten(self):
        """Gibt eine Liste aller verfügbaren Fertigkeiten zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.fertigkeiten.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Fertigkeiten: {e}")
        return []

    def _refresh_fertigkeit_view(self):
        """Aktualisiert das Eigenschaften-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Eigenschaften', 'eigenschaften_widget')
                if widget and hasattr(widget, 'update_eigenschaften'):
                    widget.update_eigenschaften()
                elif widget and hasattr(widget, 'refresh'):
                    widget.refresh()
                elif widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
        except Exception as e:
            Logger.warning(f"Eigenschaften-Widget nicht gefunden: {e}")
