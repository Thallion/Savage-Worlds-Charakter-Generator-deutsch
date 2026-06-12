# talent-popup.py
"""
Dialog-Handler für Talente (Add/Edit/Delete).

Add/Edit laufen deklarativ über FormDialogHandlerMixin (views/popup_form.py),
der Two-Phase-Lösch-Flow über BasisDialogHandler (views/popup_basis.py).
"""
from kivy.app import App
from kivy.logger import Logger

from models.talent import Talent
from views.popup_basis import BasisDialogHandler, SofortDismissMixin
from views.popup_form import FormDialogHandlerMixin


class TalentDialogHandler(FormDialogHandlerMixin, SofortDismissMixin, BasisDialogHandler):
    element_name = "Talent"
    element_name_plural = "Talente"
    artikel_unbestimmt = "ein"
    titel_neu = "Neues Talent hinzufügen"
    titel_bearbeiten = "Talent bearbeiten"

    FELDER = [
        {"key": "name", "label": "Name des Talents", "typ": "text", "pflicht": True,
         "pflicht_meldung": "Der Name des Talents darf nicht leer sein."},
        {"key": "kategorie", "label": "Kategorie", "typ": "text"},
        {"key": "rang", "label": "Rang (A, F, V, H, L)", "typ": "text"},
        {"key": "beschreibung", "label": "Beschreibung", "typ": "text"},
        {"key": "voraussetzungen", "label": "Voraussetzungen (durch Komma getrennt)", "typ": "text"},
        {"key": "neue_maechte", "label": "Neue Mächte", "typ": "int", "default": 0,
         "zahl_meldung": "Neue Mächte muss eine gültige Zahl sein."},
        {"key": "machtpunkte", "label": "Machtpunkte", "typ": "int", "default": 0,
         "zahl_meldung": "Machtpunkte müssen eine gültige Zahl sein."},
    ]

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_talent = None

    def _get_loeschbare_elemente(self):
        return self.get_all_talente()

    def _reset_selection(self):
        self.selected_talent = None

    # ------------------------------------------------------------------
    # Add/Edit-Hooks (FormDialogHandlerMixin)
    # ------------------------------------------------------------------
    def _get_element_daten(self, talent_name_key):
        app = App.get_running_app()
        charakter = app.controller.charakter
        talent = charakter.talente.get(talent_name_key)
        if not talent:
            return None
        self.selected_talent = talent_name_key
        voraussetzungen = talent.voraussetzungen
        if isinstance(voraussetzungen, list):
            voraussetzungen = ', '.join(str(v) for v in voraussetzungen)
        return {
            'name': talent.name,
            'kategorie': talent.kategorie,
            'rang': talent.rang,
            'beschreibung': talent.beschreibung,
            'voraussetzungen': voraussetzungen,
            'neue_maechte': talent.neue_maechte,
            'machtpunkte': talent.machtpunkte,
        }

    @staticmethod
    def _parse_voraussetzungen(text):
        return [v.strip() for v in text.split(',') if v.strip()]

    def _erstelle_element(self, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        name = werte['name']
        if name in charakter.talente:
            self.show_error(f"Talent '{name}' existiert bereits.")
            return False

        new_talent = Talent(
            name=name,
            kategorie=werte['kategorie'],
            rang=werte['rang'],
            beschreibung=werte['beschreibung'],
            voraussetzungen=self._parse_voraussetzungen(werte['voraussetzungen']),
            neue_maechte=werte['neue_maechte'],
            machtpunkte=werte['machtpunkte'],
            custom=True
        )

        charakter.add_talent(new_talent)
        return True

    def _aktualisiere_element(self, talent_key, werte):
        app = App.get_running_app()
        charakter = app.controller.charakter

        talent = charakter.talente.get(talent_key)
        if not talent:
            self.show_error(f"Talent '{talent_key}' nicht mehr gefunden.")
            return False

        name = werte['name']
        if name != talent.name and name in charakter.talente:
            self.show_error(f"Ein Talent mit dem Namen '{name}' existiert bereits.")
            return False

        old_name = talent.name
        talent.name = name
        talent.kategorie = werte['kategorie']
        talent.rang = werte['rang']
        talent.beschreibung = werte['beschreibung']
        talent.voraussetzungen = self._parse_voraussetzungen(werte['voraussetzungen'])
        talent.neue_maechte = werte['neue_maechte']
        talent.machtpunkte = werte['machtpunkte']

        # Bei Namensänderung: Key im Dictionary und in selected_talente ändern
        if name != old_name:
            new_key = name
            old_key = talent_key
            charakter.talente[new_key] = talent
            if old_key != new_key and old_key in charakter.talente:
                del charakter.talente[old_key]
                if old_key in charakter.selected_talente:
                    idx = charakter.selected_talente.index(old_key)
                    charakter.selected_talente[idx] = new_key

        charakter.save_custom_talents()
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

            for talent_name in selected:
                charakter.remove_talent(talent_name)
                Logger.info(f"Talent '{talent_name}' wurde gelöscht.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_eigenschaften_widget()
            self._show_success_snackbar(f"{len(selected)} Talent(e) gelöscht")

            Logger.info(f"{len(selected)} Talent(e) wurde(n) gelöscht.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Talente: {e}")
            self.show_error("Fehler beim Löschen der Talente")

    def on_talent_select(self, talent_name):
        """Callback wenn ein Talent im Dropdown ausgewählt wurde"""
        self.selected_talent = talent_name

    def get_all_talente(self):
        """Gibt eine Liste aller verfügbaren Talente zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.talente.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Talente: {e}")
        return []

    def _refresh_eigenschaften_widget(self):
        """Aktualisiert das Talente-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Talente', 'talente_widget')
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                elif widget and hasattr(widget, 'refresh'):
                    widget.refresh()
        except Exception as e:
            Logger.warning(f"Talente-Widget nicht gefunden: {e}")
