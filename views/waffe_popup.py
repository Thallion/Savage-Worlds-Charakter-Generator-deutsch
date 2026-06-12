# waffe-popup.py
"""
Dialog-Handler für Waffen (Add/Edit/Delete).

Add/Edit laufen deklarativ über FormDialogHandlerMixin (views/popup_form.py),
der Two-Phase-Lösch-Flow über BasisDialogHandler (views/popup_basis.py).
"""
from kivy.app import App
from kivy.logger import Logger

from models.waffe import Waffe
from views.popup_basis import BasisDialogHandler
from views.popup_form import FormDialogHandlerMixin

MINDESTSTAERKE_WERTE = ['W4', 'W6', 'W8', 'W10', 'W12', '-']
ZAHL_MELDUNG = "Bitte geben Sie gültige Zahlen für Gewicht und Kosten ein."


class WaffeDialogHandler(FormDialogHandlerMixin, BasisDialogHandler):
    element_name = "Waffe"
    element_name_plural = "Waffen"
    artikel_unbestimmt = "eine"
    titel_neu = "Neue Waffe hinzufügen"
    titel_bearbeiten = "Waffe bearbeiten"

    FELDER = [
        {"key": "name", "label": "Name der Waffe", "typ": "text", "pflicht": True,
         "pflicht_meldung": "Der Name der Waffe darf nicht leer sein."},
        {"key": "typ", "label": "Typ", "typ": "segment",
         "optionen": ['Nahkampf', 'Fernkampf'], "default": 'Nahkampf'},
        {"key": "mindeststaerke", "label": "Mindeststärke (z.B. W4, W6)", "typ": "auswahl",
         "erlaubt": MINDESTSTAERKE_WERTE,
         "erlaubt_meldung": "Mindeststärke muss 'W4', 'W6', 'W8', 'W10', 'W12' oder '-' sein."},
        {"key": "gewicht", "label": "Gewicht", "typ": "float",
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "kosten", "label": "Kosten", "typ": "float",
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "setting", "label": "Setting", "typ": "text"},
        {"key": "schaden", "label": "Schaden (z.B. Stä+W8)", "typ": "text"},
        {"key": "reichweite", "label": "Reichweite", "typ": "text"},
        {"key": "fr", "label": "Feuerrate (FR)", "typ": "text"},
        {"key": "schuss", "label": "Schuss", "typ": "text"},
        {"key": "pb", "label": "Panzerbrechend (PB)", "typ": "text"},
        {"key": "beschreibung", "label": "Beschreibung", "typ": "multiline"},
    ]

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_waffe = None

    def _get_loeschbare_elemente(self):
        return self.get_all_waffen()

    def _reset_selection(self):
        self.selected_waffe = None

    # ------------------------------------------------------------------
    # Add/Edit-Hooks (FormDialogHandlerMixin)
    # ------------------------------------------------------------------
    def _get_element_daten(self, waffe_name):
        app = App.get_running_app()
        charakter = app.controller.charakter
        waffe = charakter.ausruestung.get(waffe_name)
        if not waffe:
            return None
        self.selected_waffe = waffe_name
        eigenschaften = waffe.eigenschaften or {}
        return {
            'name': waffe.name,
            'typ': waffe.typ,
            'mindeststaerke': waffe.mindeststaerke,
            'gewicht': waffe.gewicht,
            'kosten': waffe.kosten,
            'setting': waffe.setting,
            'schaden': eigenschaften.get('Schaden', ''),
            'reichweite': eigenschaften.get('Reichweite', ''),
            'fr': eigenschaften.get('FR', ''),
            'schuss': eigenschaften.get('Schuss', ''),
            'pb': eigenschaften.get('PB', ''),
            'beschreibung': waffe.beschreibung,
        }

    @staticmethod
    def _baue_eigenschaften(werte):
        """Waffeneigenschaften-Dict mit '-'-Fallback für leere Felder."""
        return {
            'Schaden': werte['schaden'] if werte['schaden'] else '-',
            'Reichweite': werte['reichweite'] if werte['reichweite'] else '-',
            'FR': werte['fr'] if werte['fr'] else '-',
            'Schuss': werte['schuss'] if werte['schuss'] else '-',
            'PB': werte['pb'] if werte['pb'] else '-',
        }

    def _erstelle_element(self, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        name = werte['name']
        if name in charakter.ausruestung:
            self.show_error(f"Waffe '{name}' existiert bereits.")
            return False

        new_waffe = Waffe(
            name=name,
            gewicht=werte['gewicht'],
            kosten=werte['kosten'],
            setting=werte['setting'],
            typ=werte['typ'],
            mindeststaerke=werte['mindeststaerke'],
            beschreibung=werte['beschreibung'],
            eigenschaften=self._baue_eigenschaften(werte),
            menge=0,
            ausgewaehlt=True,
            aktiv=True,
            angelegt=False,
            kategorie='Waffe',
            custom=True
        )

        if not charakter.add_ausruestung(new_waffe):
            self.show_error(f"Waffe '{name}' konnte nicht hinzugefügt werden.")
            return False
        return True

    def _aktualisiere_element(self, waffe_key, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        waffe = charakter.ausruestung.get(waffe_key)
        if not waffe:
            self.show_error(f"Waffe '{waffe_key}' nicht mehr gefunden.")
            return False

        name = werte['name']
        if name != waffe.name and name in charakter.ausruestung:
            self.show_error(f"Waffe mit dem Namen '{name}' existiert bereits.")
            return False

        old_name = waffe.name
        waffe.name = name
        waffe.typ = werte['typ']
        waffe.mindeststaerke = werte['mindeststaerke']
        waffe.gewicht = werte['gewicht']
        waffe.kosten = werte['kosten']
        waffe.setting = werte['setting']
        waffe.beschreibung = werte['beschreibung']
        waffe.eigenschaften = self._baue_eigenschaften(werte)

        # Bei Namensänderung: Key im Dictionary ändern
        if name != old_name:
            charakter.ausruestung[name] = waffe
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

            for waffe_name in selected:
                success = charakter.remove_ausruestung(waffe_name)
                if success:
                    Logger.info(f"Waffe '{waffe_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Waffe '{waffe_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_ausruestung_view()
            self._show_success_snackbar(f"{len(selected)} Waffe(n) gelöscht")

            Logger.info(f"{len(selected)} Waffe(n) wurde(n) gelöscht.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Waffen: {e}")
            self.show_error("Fehler beim Löschen der Waffen")

    def on_waffe_select(self, waffe_name):
        """Callback wenn eine Waffe ausgewählt wurde"""
        self.selected_waffe = waffe_name

    def get_all_waffen(self):
        """Gibt eine Liste aller verfügbaren Waffen zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return [name for name, item in charakter.ausruestung.items() if isinstance(item, Waffe)]
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Waffe: {e}")
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
