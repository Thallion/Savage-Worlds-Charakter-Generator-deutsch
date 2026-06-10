# handicap-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.handicap import Handicap
from views.popup_basis import BasisDialogHandler, SofortDismissMixin

import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'handicap_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'handicap_popup.kv')

    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"handicap_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class HandicapDialogContent(MDBoxLayout):
    def __init__(self, handicap_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.selected_stufe = None
        self.edit_mode = False
        self.original_name = None

        # Wenn Handicap-Daten übergeben wurden, befülle die Felder
        if handicap_data:
            self.edit_mode = True
            self.original_name = handicap_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(handicap_data), 0.1)

    def _fill_fields(self, handicap_data):
        """Befüllt die Felder mit den Handicap-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = handicap_data.get('name', '')

        if hasattr(self.ids, 'selected_stufe_text'):
            stufe = handicap_data.get('stufe', 'leicht')
            self.ids.selected_stufe_text.text = stufe
            self.selected_stufe = stufe

        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = handicap_data.get('beschreibung', '')

    def open_stufen_menu(self, instance_item):
        menu_items = [
            {
                "text": stufe,
                "on_release": lambda x=stufe: self.select_stufe(x),
            }
            for stufe in ['leicht', 'schwer']
        ]

        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()

    def select_stufe(self, stufe):
        self.selected_stufe = stufe
        if hasattr(self.ids, 'selected_stufe_text'):
            self.ids.selected_stufe_text.text = stufe

class DeleteHandicapDialogContent(MDBoxLayout):
    def __init__(self, handicaps_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.handicaps_callback = handicaps_callback
        self.menu_callback = menu_callback
        self.dialog = None

    def open_menu(self, instance_item):
        if not self.handicaps_callback:
            return

        handicaps = self.handicaps_callback()
        if not handicaps:
            return

        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in handicaps
        ]

        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()

    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'handicap_dropdown'):
            self.ids.handicap_dropdown.text = text_item

class HandicapDialogHandler(SofortDismissMixin, BasisDialogHandler):
    element_name = "Handicap"
    element_name_plural = "Handicaps"
    artikel_unbestimmt = "ein"

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_handicap = None

    def _get_loeschbare_elemente(self):
        return self.get_all_handicaps()

    def _reset_selection(self):
        self.selected_handicap = None

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen eines neuen Handicaps"""
        dialog_content = HandicapDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neues Handicap hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_handicap,
        )

    def show_edit_dialog(self, handicap_name_key):
        """Zeigt den Dialog zum Bearbeiten eines bestehenden Handicaps"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            # Hole das Handicap
            handicap = charakter.handicaps.get(handicap_name_key)
            if not handicap:
                self.show_error(f"Handicap '{handicap_name_key}' nicht gefunden.")
                return

            # Erstelle Dialog-Content mit Handicap-Daten
            handicap_data = {
                'name': handicap.name,
                'stufe': handicap.stufe,
                'beschreibung': handicap.beschreibung
            }

            dialog_content = HandicapDialogContent(handicap_data=handicap_data)
            self.dialog_content = dialog_content
            self.selected_handicap = handicap_name_key  # Speichere den Key für Updates

            overlay = self._get_overlay()
            overlay.open(
                title="Handicap bearbeiten",
                content_widget=dialog_content,
                action_text="Speichern",
                on_action=self.update_handicap,
            )

        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
            self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def update_handicap(self, *args):
        """Aktualisiert ein bestehendes Handicap"""
        if not self.dialog_content or not self.selected_handicap:
            Logger.error("Dialog-Content oder ausgewähltes Handicap nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name des Handicaps darf nicht leer sein.")
            return

        # Validiere Stufe
        if not hasattr(self.dialog_content, 'selected_stufe') or not self.dialog_content.selected_stufe:
            self.show_error("Bitte wähle eine Stufe aus.")
            return

        stufe = self.dialog_content.selected_stufe
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()

        if not beschreibung:
            self.show_error("Die Beschreibung darf nicht leer sein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            # Hole das bestehende Handicap
            handicap = charakter.handicaps.get(self.selected_handicap)
            if not handicap:
                self.show_error(f"Handicap '{self.selected_handicap}' nicht mehr gefunden.")
                return

            # Wenn der Name geändert wurde und bereits existiert
            if name != handicap.name and name in charakter.handicaps:
                self.show_error(f"Ein Handicap mit dem Namen '{name}' existiert bereits.")
                return

            # Aktualisiere das Handicap
            handicap.name = name
            handicap.stufe = stufe
            handicap.beschreibung = beschreibung
            handicap.update_punkte()  # Punkte neu berechnen

            # Bei Namensänderung: Key im Dictionary ändern
            if name != self.dialog_content.original_name and self.dialog_content.original_name:
                # Neuen Key erstellen
                new_key = f"{name} ({stufe})"
                old_key = self.selected_handicap

                # Handicap unter neuem Key speichern und alten löschen
                charakter.handicaps[new_key] = handicap
                if old_key != new_key and old_key in charakter.handicaps:
                    del charakter.handicaps[old_key]

                    # Auch in selected_handicaps aktualisieren
                    if old_key in charakter.selected_handicaps:
                        idx = charakter.selected_handicaps.index(old_key)
                        charakter.selected_handicaps[idx] = new_key

            # Speichere die Custom Handicaps
            charakter.save_custom_handicaps()

            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_handicap_view()

            self.dismiss_dialog()
            Logger.info(f"Handicap '{name}' wurde aktualisiert.")

        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Handicaps: {e}")
            self.show_error("Fehler beim Aktualisieren des Handicaps")

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
            self.show_error("Fehler beim L��schen der Handicaps")

    def save_handicap(self, *args):
        """Speichert ein neues Handicap"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name des Handicaps darf nicht leer sein.")
            return

        # Validiere Stufe
        if not hasattr(self.dialog_content, 'selected_stufe') or not self.dialog_content.selected_stufe:
            self.show_error("Bitte wähle eine Stufe aus.")
            return

        # Sammle alle Eingabedaten
        stufe = self.dialog_content.selected_stufe
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()

        if not beschreibung:
            self.show_error("Die Beschreibung darf nicht leer sein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            if name in charakter.handicaps:
                self.show_error(f"Handicap '{name}' existiert bereits.")
                return

            new_handicap = Handicap(
                name=name,
                stufe=stufe,
                beschreibung=beschreibung,
                custom=True
            )

            # Füge das Handicap hinzu
            charakter.add_handicap(new_handicap)

            # Speichere die Custom Handicaps
            charakter.save_custom_handicaps()

            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_handicap_view()

            self.dismiss_dialog()
            Logger.info(f"Handicap '{name}' wurde hinzugefügt.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Handicaps: {e}")
            self.show_error("Fehler beim Speichern des Handicaps")

    def delete_handicap(self, *args):
        """Löscht die ausgewählten Handicaps"""
        try:
            if not self.dialog_content:
                self.show_error("Dialog-Content nicht gefunden.")
                return

            selected = self.dialog_content.get_selected_items()
            if not selected:
                self.show_error("Bitte wähle mindestens ein Handicap zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter

            for handicap_name in selected:
                charakter.remove_handicap(handicap_name)
                Logger.info(f"Handicap '{handicap_name}' wurde gelöscht.")

            charakter.save_custom_handicaps()

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_handicap_view()
            self._show_success_snackbar(f"{len(selected)} Handicap(s) gelöscht")

            Logger.info(f"{len(selected)} Handicap(s) wurde(n) gelöscht.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Handicaps: {e}")
            self.show_error("Fehler beim Löschen der Handicaps")


    def on_handicap_select(self, handicap_name):
        """Callback wenn ein Handicap im Dropdown ausgewählt wurde"""
        self.selected_handicap = handicap_name
        if (self.dialog_content and
            hasattr(self.dialog_content.ids, 'selected_handicap_text')):
            self.dialog_content.ids.selected_handicap_text.text = handicap_name
            Logger.info(f"Handicap '{handicap_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

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
