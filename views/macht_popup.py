# macht-popup.py
"""
Dialog-Handler für Mächte (Add/Edit/Delete).

Add/Edit laufen deklarativ über FormDialogHandlerMixin (views/popup_form.py),
der Two-Phase-Lösch-Flow über BasisDialogHandler (views/popup_basis.py).
"""
from kivy.app import App
from kivy.logger import Logger

from models.macht import Macht
from views.popup_basis import BasisDialogHandler, SofortDismissMixin
from views.popup_form import FormDialogHandlerMixin


class MachtDialogHandler(FormDialogHandlerMixin, SofortDismissMixin, BasisDialogHandler):
    element_name = "Macht"
    element_name_plural = "Mächte"
    artikel_unbestimmt = "eine"
    titel_neu = "Neue Macht hinzufügen"
    titel_bearbeiten = "Macht bearbeiten"

    FELDER = [
        {"key": "name", "label": "Name der Macht", "typ": "text", "pflicht": True,
         "pflicht_meldung": "Der Name der Macht darf nicht leer sein."},
        {"key": "rang", "label": "Rang", "typ": "text"},
        {"key": "machtpunkte", "label": "Machtpunkte", "typ": "int",
         "zahl_meldung": "Machtpunkte müssen eine gültige Zahl sein."},
        {"key": "reichweite", "label": "Reichweite", "typ": "text"},
        {"key": "dauer", "label": "Dauer", "typ": "text"},
        {"key": "effekt", "label": "Effekt", "typ": "text"},
        {"key": "beschreibung", "label": "Beschreibung", "typ": "text"},
        {"key": "voraussetzungen", "label": "Voraussetzungen (durch Komma getrennt)", "typ": "text"},
    ]

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_macht = None

    def _get_loeschbare_elemente(self):
        return self.get_all_maechte()

    def _reset_selection(self):
        self.selected_macht = None

    # ------------------------------------------------------------------
    # Add/Edit-Hooks (FormDialogHandlerMixin)
    # ------------------------------------------------------------------
    def _get_element_daten(self, macht_name_key):
        app = App.get_running_app()
        charakter = app.controller.charakter
        macht = charakter.maechte.get(macht_name_key)
        if not macht:
            return None
        self.selected_macht = macht_name_key
        voraussetzungen = macht.voraussetzungen
        if isinstance(voraussetzungen, list):
            voraussetzungen = ', '.join(str(v) for v in voraussetzungen)
        return {
            'name': macht.name,
            'rang': macht.rang,
            'machtpunkte': macht.machtpunkte,
            'reichweite': macht.reichweite,
            'dauer': macht.dauer,
            'effekt': macht.effekt,
            'beschreibung': macht.beschreibung,
            'voraussetzungen': voraussetzungen,
        }

    @staticmethod
    def _parse_voraussetzungen(text):
        return [v.strip() for v in text.split(',') if v.strip()]

    def _erstelle_element(self, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        name = werte['name']
        if name in charakter.maechte:
            self.show_error(f"Macht '{name}' existiert bereits.")
            return False

        new_macht = Macht(
            name=name,
            rang=werte['rang'],
            machtpunkte=werte['machtpunkte'],
            reichweite=werte['reichweite'],
            dauer=werte['dauer'],
            effekt=werte['effekt'],
            beschreibung=werte['beschreibung'],
            voraussetzungen=self._parse_voraussetzungen(werte['voraussetzungen']),
            custom=True
        )

        if not charakter.add_macht(new_macht):
            self.show_error(f"Macht '{name}' konnte nicht hinzugefügt werden.")
            return False
        return True

    def _aktualisiere_element(self, macht_key, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        macht = charakter.maechte.get(macht_key)
        if not macht:
            self.show_error(f"Macht '{macht_key}' nicht mehr gefunden.")
            return False

        name = werte['name']
        if name != macht.name and name in charakter.maechte:
            self.show_error(f"Eine Macht mit dem Namen '{name}' existiert bereits.")
            return False

        old_name = macht.name
        macht.name = name
        macht.rang = werte['rang']
        macht.machtpunkte = werte['machtpunkte']
        macht.reichweite = werte['reichweite']
        macht.dauer = werte['dauer']
        macht.effekt = werte['effekt']
        macht.beschreibung = werte['beschreibung']
        macht.voraussetzungen = self._parse_voraussetzungen(werte['voraussetzungen'])

        # Bei Namensänderung: Key im Dictionary und in selected_maechte ändern
        if name != old_name:
            new_key = name
            old_key = macht_key
            charakter.maechte[new_key] = macht
            if old_key != new_key and old_key in charakter.maechte:
                del charakter.maechte[old_key]
                if old_key in charakter.selected_maechte:
                    idx = charakter.selected_maechte.index(old_key)
                    charakter.selected_maechte[idx] = new_key

        charakter.save_custom_maechte()
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

            for macht_name in selected:
                success = charakter.remove_macht(macht_name)
                if success:
                    Logger.info(f"Macht '{macht_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Macht '{macht_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_macht_view()
            self._show_success_snackbar(f"{len(selected)} Macht/Mächte gelöscht")

            Logger.info(f"{len(selected)} Macht/Mächte wurde(n) gelöscht.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Mächte: {e}")
            self.show_error("Fehler beim Löschen der Mächte")

    def on_macht_select(self, macht_name):
        """Callback wenn eine Macht im Dropdown ausgewählt wurde"""
        self.selected_macht = macht_name

    def get_all_maechte(self):
        """Gibt eine Liste aller verfügbaren Mächte zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.maechte.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Mächte: {e}")
        return []

    def _refresh_macht_view(self):
        """Aktualisiert das Macht-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Mächte', 'maechte_widget')
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                elif widget and hasattr(widget, 'refresh'):
                    widget.refresh()
        except Exception as e:
            Logger.warning(f"Macht-Widget nicht gefunden: {e}")
