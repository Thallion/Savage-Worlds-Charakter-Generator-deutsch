# schild-popup.py
"""
Dialog-Handler für Schilde (Add/Edit/Delete).

Add/Edit laufen deklarativ über FormDialogHandlerMixin (views/popup_form.py),
der Two-Phase-Lösch-Flow über BasisDialogHandler (views/popup_basis.py).
"""
from kivy.app import App
from kivy.logger import Logger

from models.schild import Schild
from views.popup_basis import BasisDialogHandler
from views.popup_form import FormDialogHandlerMixin

MINDESTSTAERKE_WERTE = ['W4', 'W6', 'W8', 'W10', 'W12', '-']
ZAHL_MELDUNG = "Bitte geben Sie gültige Zahlen für Parade, Deckung, Gewicht und Kosten ein."


class SchildDialogHandler(FormDialogHandlerMixin, BasisDialogHandler):
    element_name = "Schild"
    element_name_plural = "Schilde"
    artikel_unbestimmt = "ein"
    titel_neu = "Neues Schild hinzufügen"
    titel_bearbeiten = "Schild bearbeiten"

    FELDER = [
        {"key": "name", "label": "Name des Schildes", "typ": "text", "pflicht": True,
         "pflicht_meldung": "Der Name des Schildes darf nicht leer sein."},
        {"key": "parade", "label": "Paradebonus", "typ": "int",
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "deckung", "label": "Deckung", "typ": "int",
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "mindeststaerke", "label": "Mindeststärke (z.B. W4, W6)", "typ": "auswahl",
         "erlaubt": MINDESTSTAERKE_WERTE,
         "erlaubt_meldung": "Mindeststärke muss 'W4', 'W6', 'W8', 'W10', 'W12' oder '-' sein."},
        {"key": "gewicht", "label": "Gewicht", "typ": "float",
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "kosten", "label": "Kosten", "typ": "float",
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "setting", "label": "Setting", "typ": "text"},
        {"key": "beschreibung", "label": "Beschreibung", "typ": "text"},
    ]

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_schild = None

    def _get_loeschbare_elemente(self):
        return self.get_all_schilde()

    def _reset_selection(self):
        self.selected_schild = None

    # ------------------------------------------------------------------
    # Add/Edit-Hooks (FormDialogHandlerMixin)
    # ------------------------------------------------------------------
    def _get_element_daten(self, schild_name):
        app = App.get_running_app()
        charakter = app.controller.charakter
        schild = charakter.ausruestung.get(schild_name)
        if not schild:
            return None
        self.selected_schild = schild_name
        return {
            'name': schild.name,
            'parade': schild.parade,
            'deckung': schild.deckung,
            'mindeststaerke': schild.mindeststaerke,
            'gewicht': schild.gewicht,
            'kosten': schild.kosten,
            'setting': schild.setting,
            'beschreibung': schild.beschreibung,
        }

    def _erstelle_element(self, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        if werte['name'] in charakter.ausruestung:
            self.show_error(f"Schild '{werte['name']}' existiert bereits.")
            return False

        new_schild = Schild(
            name=werte['name'],
            gewicht=werte['gewicht'],
            kosten=werte['kosten'],
            setting=werte['setting'],
            parade=werte['parade'],
            deckung=werte['deckung'],
            mindeststaerke=werte['mindeststaerke'],
            beschreibung=werte['beschreibung'],
            menge=0,
            ausgewaehlt=True,
            aktiv=True,
            angelegt=False,
            kategorie='Schild',
            custom=True
        )

        if not charakter.add_ausruestung(new_schild):
            self.show_error(f"Schild '{werte['name']}' konnte nicht hinzugefügt werden.")
            return False
        return True

    def _aktualisiere_element(self, schild_key, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        schild = charakter.ausruestung.get(schild_key)
        if not schild:
            self.show_error(f"Schild '{schild_key}' nicht mehr gefunden.")
            return False

        name = werte['name']
        if name != schild.name and name in charakter.ausruestung:
            self.show_error(f"Schild mit dem Namen '{name}' existiert bereits.")
            return False

        old_name = schild.name
        schild.name = name
        schild.parade = werte['parade']
        schild.deckung = werte['deckung']
        schild.mindeststaerke = werte['mindeststaerke']
        schild.gewicht = werte['gewicht']
        schild.kosten = werte['kosten']
        schild.setting = werte['setting']
        schild.beschreibung = werte['beschreibung']

        # Bei Namensänderung: Key im Dictionary ändern
        if name != old_name:
            charakter.ausruestung[name] = schild
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

            for schild_name in selected:
                success = charakter.remove_ausruestung(schild_name)
                if success:
                    Logger.info(f"Schild '{schild_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Schild '{schild_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_ausruestung_view()
            self._show_success_snackbar(f"{len(selected)} Schild(er) gelöscht")

            Logger.info(f"{len(selected)} Schild(er) wurde(n) gelöscht.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Schilde: {e}")
            self.show_error("Fehler beim Löschen der Schilde")

    def on_schild_select(self, schild_name):
        """Callback wenn ein Schild ausgewählt wurde"""
        self.selected_schild = schild_name

    def get_all_schilde(self):
        """Gibt eine Liste aller verfügbaren Schilde zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return [name for name, item in charakter.ausruestung.items() if isinstance(item, Schild)]
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Schilde: {e}")
        return []

    def _refresh_ausruestung_view(self):
        """Aktualisiert das Ausrüstung-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Ausrüstung', 'ausruestung_widget')
                if widget and hasattr(widget, 'refresh'):
                    widget.refresh()
                elif widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
        except Exception as e:
            Logger.warning(f"Ausrüstung-Widget nicht gefunden: {e}")
