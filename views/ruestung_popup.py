# ruestung-popup.py
"""
Dialog-Handler für Rüstungen (Add/Edit/Delete).

Add/Edit laufen deklarativ über FormDialogHandlerMixin (views/popup_form.py),
der Two-Phase-Lösch-Flow über BasisDialogHandler (views/popup_basis.py).
"""
from kivy.app import App
from kivy.logger import Logger

from models.ruestung import Ruestung
from views.popup_basis import BasisDialogHandler
from views.popup_form import FormDialogHandlerMixin

MINDESTSTAERKE_WERTE = ['W4', 'W6', 'W8', 'W10', 'W12', '-']
ZAHL_MELDUNG = "Bitte geben Sie gültige Zahlen für die Schutzwerte, Gewicht und Kosten ein."


class RuestungDialogHandler(FormDialogHandlerMixin, BasisDialogHandler):
    element_name = "Rüstung"
    element_name_plural = "Rüstungen"
    artikel_unbestimmt = "eine"
    titel_neu = "Neue Rüstung hinzufügen"
    titel_bearbeiten = "Rüstung bearbeiten"

    FELDER = [
        {"key": "name", "label": "Name der Rüstung", "typ": "text", "pflicht": True,
         "pflicht_meldung": "Der Name der Rüstung darf nicht leer sein."},
        {"key": "torso", "label": "Schutzwert Torso", "typ": "int", "default": 0,
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "arme", "label": "Schutzwert Arme", "typ": "int", "default": 0,
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "beine", "label": "Schutzwert Beine", "typ": "int", "default": 0,
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "kopf", "label": "Schutzwert Kopf", "typ": "int", "default": 0,
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "mindeststaerke", "label": "Mindeststärke (z.B. W4, W6)", "typ": "auswahl",
         "erlaubt": MINDESTSTAERKE_WERTE,
         "erlaubt_meldung": "Mindeststärke muss 'W4', 'W6', 'W8', 'W10', 'W12' oder '-' sein."},
        {"key": "gewicht", "label": "Gewicht", "typ": "float", "default": 0,
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "kosten", "label": "Kosten", "typ": "float", "default": 0,
         "zahl_meldung": ZAHL_MELDUNG},
        {"key": "setting", "label": "Setting", "typ": "text"},
        {"key": "beschreibung", "label": "Beschreibung", "typ": "text"},
    ]

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_ruestung = None

    def _get_loeschbare_elemente(self):
        return self.get_all_ruestungen()

    def _reset_selection(self):
        self.selected_ruestung = None

    # ------------------------------------------------------------------
    # Add/Edit-Hooks (FormDialogHandlerMixin)
    # ------------------------------------------------------------------
    def _get_element_daten(self, ruestung_name):
        app = App.get_running_app()
        charakter = app.controller.charakter
        ruestung = charakter.ausruestung.get(ruestung_name)
        if not ruestung:
            return None
        self.selected_ruestung = ruestung_name
        return {
            'name': ruestung.name,
            'torso': ruestung.torso,
            'arme': ruestung.arme,
            'beine': ruestung.beine,
            'kopf': ruestung.kopf,
            'mindeststaerke': ruestung.mindeststaerke,
            'gewicht': ruestung.gewicht,
            'kosten': ruestung.kosten,
            'setting': ruestung.setting,
            'beschreibung': ruestung.beschreibung,
        }

    def _erstelle_element(self, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        name = werte['name']
        if name in charakter.ausruestung:
            self.show_error(f"Rüstung '{name}' existiert bereits.")
            return False

        new_ruestung = Ruestung(
            name=name,
            torso=werte['torso'],
            arme=werte['arme'],
            beine=werte['beine'],
            kopf=werte['kopf'],
            mindeststaerke=werte['mindeststaerke'],
            setting=werte['setting'],
            gewicht=werte['gewicht'],
            kosten=werte['kosten'],
            beschreibung=werte['beschreibung'],
            menge=0,
            ausgewaehlt=True,
            aktiv=True,
            angelegt=False,
            kategorie='Rüstung',
            custom=True
        )

        if not charakter.add_ausruestung(new_ruestung):
            self.show_error(f"Rüstung '{name}' konnte nicht hinzugefügt werden.")
            return False
        return True

    def _aktualisiere_element(self, ruestung_key, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        ruestung = charakter.ausruestung.get(ruestung_key)
        if not ruestung:
            self.show_error(f"Rüstung '{ruestung_key}' nicht mehr gefunden.")
            return False

        name = werte['name']
        if name != ruestung.name and name in charakter.ausruestung:
            self.show_error(f"Rüstung mit dem Namen '{name}' existiert bereits.")
            return False

        old_name = ruestung.name
        ruestung.name = name
        ruestung.torso = werte['torso']
        ruestung.arme = werte['arme']
        ruestung.beine = werte['beine']
        ruestung.kopf = werte['kopf']
        ruestung.mindeststaerke = werte['mindeststaerke']
        ruestung.gewicht = werte['gewicht']
        ruestung.kosten = werte['kosten']
        ruestung.setting = werte['setting']
        ruestung.beschreibung = werte['beschreibung']

        # Bei Namensänderung: Key im Dictionary ändern
        if name != old_name:
            charakter.ausruestung[name] = ruestung
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

            for ruestung_name in selected:
                success = charakter.remove_ausruestung(ruestung_name)
                if success:
                    Logger.info(f"Rüstung '{ruestung_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Rüstung '{ruestung_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_ausruestung_view()
            self._show_success_snackbar(f"{len(selected)} Rüstung(en) gelöscht")

            Logger.info(f"{len(selected)} Rüstung(en) wurde(n) gelöscht.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Rüstungen: {e}")
            self.show_error("Fehler beim Löschen der Rüstungen")

    def on_ruestung_select(self, ruestung_name):
        """Callback wenn eine Rüstung ausgewählt wurde"""
        self.selected_ruestung = ruestung_name

    def get_all_ruestungen(self):
        """Gibt eine Liste aller verfügbaren Rüstungen zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return [name for name, item in charakter.ausruestung.items()
                        if isinstance(item, Ruestung)]
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Rüstungen: {e}")
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
