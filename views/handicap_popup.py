# handicap-popup.py
"""
Dialog-Handler für Handicaps (Add/Edit/Delete).

Add/Edit laufen deklarativ über FormDialogHandlerMixin (views/popup_form.py),
der Two-Phase-Lösch-Flow über BasisDialogHandler (views/popup_basis.py).
"""
from kivy.app import App
from kivy.logger import Logger

from models.handicap import Handicap
from views.popup_basis import BasisDialogHandler, SofortDismissMixin
from views.popup_form import FormDialogHandlerMixin


class HandicapDialogHandler(FormDialogHandlerMixin, SofortDismissMixin, BasisDialogHandler):
    element_name = "Handicap"
    element_name_plural = "Handicaps"
    artikel_unbestimmt = "ein"
    titel_neu = "Neues Handicap hinzufügen"
    titel_bearbeiten = "Handicap bearbeiten"

    FELDER = [
        {"key": "name", "label": "Name des Handicaps", "typ": "text", "pflicht": True,
         "pflicht_meldung": "Der Name des Handicaps darf nicht leer sein."},
        {"key": "stufe", "label": "Stufe wählen", "typ": "dropdown",
         "optionen": ['leicht', 'schwer'], "pflicht": True,
         "pflicht_meldung": "Bitte wähle eine Stufe aus."},
        {"key": "beschreibung", "label": "Beschreibung", "typ": "text", "pflicht": True,
         "pflicht_meldung": "Die Beschreibung darf nicht leer sein."},
    ]

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_handicap = None

    def _get_loeschbare_elemente(self):
        return self.get_all_handicaps()

    def _reset_selection(self):
        self.selected_handicap = None

    # ------------------------------------------------------------------
    # Add/Edit-Hooks (FormDialogHandlerMixin)
    # ------------------------------------------------------------------
    def _get_element_daten(self, handicap_name_key):
        app = App.get_running_app()
        charakter = app.controller.charakter
        handicap = charakter.handicaps.get(handicap_name_key)
        if not handicap:
            return None
        self.selected_handicap = handicap_name_key
        self._edit_original_name = handicap.name
        return {
            'name': handicap.name,
            'stufe': handicap.stufe,
            'beschreibung': handicap.beschreibung,
        }

    def _erstelle_element(self, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        name = werte['name']
        if name in charakter.handicaps:
            self.show_error(f"Handicap '{name}' existiert bereits.")
            return False

        new_handicap = Handicap(
            name=name,
            stufe=werte['stufe'],
            beschreibung=werte['beschreibung'],
            custom=True
        )

        charakter.add_handicap(new_handicap)
        charakter.save_custom_handicaps()
        return True

    def _aktualisiere_element(self, handicap_key, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        handicap = charakter.handicaps.get(handicap_key)
        if not handicap:
            self.show_error(f"Handicap '{handicap_key}' nicht mehr gefunden.")
            return False

        name = werte['name']
        if name != handicap.name and name in charakter.handicaps:
            self.show_error(f"Ein Handicap mit dem Namen '{name}' existiert bereits.")
            return False

        handicap.name = name
        handicap.stufe = werte['stufe']
        handicap.beschreibung = werte['beschreibung']
        handicap.update_punkte()  # Punkte neu berechnen

        # Bei Namensänderung: Key (Format "Name (stufe)") und selected_handicaps anpassen
        original_name = getattr(self, '_edit_original_name', None)
        if original_name and name != original_name:
            new_key = f"{name} ({werte['stufe']})"
            old_key = handicap_key
            charakter.handicaps[new_key] = handicap
            if old_key != new_key and old_key in charakter.handicaps:
                del charakter.handicaps[old_key]
                if old_key in charakter.selected_handicaps:
                    idx = charakter.selected_handicaps.index(old_key)
                    charakter.selected_handicaps[idx] = new_key

        charakter.save_custom_handicaps()
        return True

    def _nach_speichern(self):
        super()._nach_speichern()
        self._refresh_handicap_view()

    # ------------------------------------------------------------------
    # Lösch-Flow (BasisDialogHandler)
    # ------------------------------------------------------------------
    def _confirm_delete_elemente(self):
        """Phase 2: Führt das tatsächliche Löschen durch."""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            charakter = app.controller.charakter

            for handicap_name in selected:
                charakter.remove_handicap(handicap_name)
                Logger.info(f"Handicap '{handicap_name}' wurde gelöscht.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            Logger.info(f"{len(selected)} Handicap(s) wurde(n) gelöscht.")
            if hasattr(self, '_delete_popup') and self._delete_popup:
                self._delete_popup.dismiss()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Handicaps: {e}")
            self.show_error("Fehler beim Löschen der Handicaps")

    def on_handicap_select(self, handicap_name):
        """Callback wenn ein Handicap im Dropdown ausgewählt wurde"""
        self.selected_handicap = handicap_name

    def _refresh_handicap_view(self):
        """Aktualisiert die Handicap-RecycleView nach Änderungen."""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Handicaps', 'handicaps_widget')
                if widget:
                    from kivy.clock import Clock
                    Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)
        except Exception as e:
            Logger.warning(f"Handicap-Widget nicht gefunden: {e}")

    def get_all_handicaps(self):
        """Gibt eine Liste aller verfügbaren Handicaps zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.handicaps.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Handicaps: {e}")
        return []
