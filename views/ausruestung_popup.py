# ausruestung-popup.py
"""
Dialog-Handler für allgemeine Ausrüstung (Add/Edit/Delete).

Add/Edit laufen deklarativ über FormDialogHandlerMixin (views/popup_form.py),
der Two-Phase-Lösch-Flow über BasisDialogHandler (views/popup_basis.py).
"""
from kivy.app import App
from kivy.logger import Logger

from models.ausruestung import Ausruestung
from views.popup_basis import BasisDialogHandler
from views.popup_form import FormDialogHandlerMixin


class AusruestungDialogHandler(FormDialogHandlerMixin, BasisDialogHandler):
    element_name = "Ausrüstung"
    element_name_plural = "Ausrüstungen"
    artikel_unbestimmt = "eine"
    titel_neu = "Neue Ausrüstung hinzufügen"
    titel_bearbeiten = "Ausrüstung bearbeiten"

    FELDER = [
        {"key": "name", "label": "Name der Ausrüstung", "typ": "text", "pflicht": True,
         "pflicht_meldung": "Der Name der Ausrüstung darf nicht leer sein."},
        {"key": "kategorie", "label": "Kategorie", "typ": "text", "pflicht": True,
         "pflicht_meldung": "Bitte geben Sie eine Kategorie an."},
        {"key": "gewicht", "label": "Gewicht", "typ": "float", "default": 0,
         "zahl_meldung": "Bitte geben Sie gültige Zahlen für Gewicht und Kosten ein."},
        {"key": "kosten", "label": "Kosten", "typ": "float", "default": 0,
         "zahl_meldung": "Bitte geben Sie gültige Zahlen für Gewicht und Kosten ein."},
        {"key": "setting", "label": "Setting", "typ": "text"},
        {"key": "beschreibung", "label": "Beschreibung", "typ": "text"},
    ]

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_ausruestung = None

    def _get_loeschbare_elemente(self):
        return self.get_all_ausruestung()

    def _reset_selection(self):
        self.selected_ausruestung = None

    # ------------------------------------------------------------------
    # Add/Edit-Hooks (FormDialogHandlerMixin)
    # ------------------------------------------------------------------
    def _get_element_daten(self, ausruestung_name):
        app = App.get_running_app()
        charakter = app.controller.charakter
        ausruestung = charakter.ausruestung.get(ausruestung_name)
        if not ausruestung:
            return None
        self.selected_ausruestung = ausruestung_name
        return {
            'name': ausruestung.name,
            'kategorie': getattr(ausruestung, 'kategorie', 'Allgemein'),
            'gewicht': ausruestung.gewicht,
            'kosten': ausruestung.kosten,
            'setting': ausruestung.setting,
            'beschreibung': ausruestung.beschreibung,
        }

    def _erstelle_element(self, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        if werte['name'] in charakter.ausruestung:
            self.show_error(f"Ausrüstung '{werte['name']}' existiert bereits.")
            return False

        new_ausruestung = Ausruestung(
            name=werte['name'],
            kategorie=werte['kategorie'],
            gewicht=werte['gewicht'],
            kosten=werte['kosten'],
            setting=werte['setting'],
            beschreibung=werte['beschreibung'],
            menge=0,
            ausgewaehlt=True,
            aktiv=True,
            angelegt=False,
            custom=True
        )

        if not charakter.add_ausruestung(new_ausruestung):
            self.show_error(f"Ausrüstung '{werte['name']}' konnte nicht hinzugefügt werden.")
            return False
        return True

    def _aktualisiere_element(self, ausruestung_key, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        ausruestung = charakter.ausruestung.get(ausruestung_key)
        if not ausruestung:
            self.show_error(f"Ausrüstung '{ausruestung_key}' nicht mehr gefunden.")
            return False

        name = werte['name']
        if name != ausruestung.name and name in charakter.ausruestung:
            self.show_error(f"Ausrüstung mit dem Namen '{name}' existiert bereits.")
            return False

        old_name = ausruestung.name
        ausruestung.name = name
        ausruestung.kategorie = werte['kategorie']
        ausruestung.gewicht = werte['gewicht']
        ausruestung.kosten = werte['kosten']
        ausruestung.setting = werte['setting']
        ausruestung.beschreibung = werte['beschreibung']

        # Bei Namensänderung: Key im Dictionary ändern
        if name != old_name:
            charakter.ausruestung[name] = ausruestung
            if old_name in charakter.ausruestung:
                del charakter.ausruestung[old_name]
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

            for ausruestung_name in selected:
                success = charakter.remove_ausruestung(ausruestung_name)
                if success:
                    Logger.info(f"Ausrüstung '{ausruestung_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Ausrüstung '{ausruestung_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_ausruestung_view()
            self._show_success_snackbar(f"{len(selected)} Ausrüstung(en) gelöscht")

            Logger.info(f"{len(selected)} Ausrüstung(en) wurde(n) gelöscht.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Ausrüstungen: {e}")
            self.show_error("Fehler beim Löschen der Ausrüstungen")

    def on_ausruestung_select(self, ausruestung_name):
        """Callback wenn eine Ausrüstung ausgewählt wurde"""
        self.selected_ausruestung = ausruestung_name

    def get_all_ausruestung(self):
        """Gibt eine Liste aller verfügbaren Ausrüstung zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.ausruestung.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Ausrüstung: {e}")
        return []

    def _refresh_ausruestung_view(self):
        """Aktualisiert das Ausrüstung-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Ausrüstung', 'ausruestung_widget')
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                elif widget and hasattr(widget, 'refresh'):
                    widget.refresh()
        except Exception as e:
            Logger.warning(f"Ausrüstung-Widget nicht gefunden: {e}")
