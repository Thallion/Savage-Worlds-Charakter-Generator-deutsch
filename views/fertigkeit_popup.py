# fertigkeit-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.fertigkeit import Fertigkeit
from views.popup_basis import BasisDialogHandler, SofortDismissMixin

import os
import sys
import time

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'fertigkeit_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'fertigkeit_popup.kv')

    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"fertigkeit_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class FertigkeitDialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.selected_attribut = None

    def open_attribut_menu(self, instance_item):
        app = App.get_running_app()
        charakter = app.controller.charakter
        attribute = list(charakter.get_attribute_dict().keys())

        menu_items = [
            {
                "text": attribut,
                "on_release": lambda x=attribut: self.select_attribut(x),
            }
            for attribut in attribute
        ]

        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()

    def select_attribut(self, attribut):
        self.selected_attribut = attribut
        if hasattr(self.ids, 'selected_attribut_text'):
            self.ids.selected_attribut_text.text = attribut

class DeleteFertigkeitDialogContent(MDBoxLayout):
    def __init__(self, fertigkeiten_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.fertigkeiten_callback = fertigkeiten_callback
        self.menu_callback = menu_callback
        self.dialog = None

    def open_menu(self, instance_item):
        if not self.fertigkeiten_callback:
            return

        fertigkeiten = self.fertigkeiten_callback()
        if not fertigkeiten:
            return

        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in fertigkeiten
        ]

        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()

    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'fertigkeit_dropdown'):
            self.ids.fertigkeit_dropdown.text = text_item

class FertigkeitDialogHandler(SofortDismissMixin, BasisDialogHandler):
    element_name = "Fertigkeit"
    element_name_plural = "Fertigkeiten"
    artikel_unbestimmt = "eine"

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_fertigkeit = None

    def _get_loeschbare_elemente(self):
        return self.get_all_fertigkeiten()

    def _reset_selection(self):
        self.selected_fertigkeit = None

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen einer neuen Fertigkeit"""
        dialog_content = FertigkeitDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neue Fertigkeit hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_fertigkeit,
        )

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

    def save_fertigkeit(self, *args):
        """Speichert eine neue Fertigkeit"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name der Fertigkeit darf nicht leer sein.")
            return

        # Validiere Attribut
        if not hasattr(self.dialog_content, 'selected_attribut') or not self.dialog_content.selected_attribut:
            self.show_error("Bitte wähle ein Attribut aus.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            if name in charakter.fertigkeiten:
                self.show_error(f"Fertigkeit '{name}' existiert bereits.")
                return

            # Attributobjekt abrufen
            attribut = charakter.get_attribute_dict().get(self.dialog_content.selected_attribut)
            if attribut is None:
                self.show_error(f"Attribut '{self.dialog_content.selected_attribut}' nicht gefunden.")
                return

            grundfertigkeit = self.dialog_content.ids.grundfertigkeit_checkbox.active

            new_fertigkeit = Fertigkeit(
                fertigkeit_name=name,
                attribut=attribut,
                grundfertigkeit=grundfertigkeit,
                custom=True
            )

            # Füge die Fertigkeit hinzu
            charakter.add_fertigkeit(new_fertigkeit)

            # Speichere die Custom Fertigkeiten
            charakter.save_custom_fertigkeiten()

            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            self.dismiss_dialog()
            Logger.info(f"Fertigkeit '{name}' wurde hinzugefügt.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Fertigkeit: {e}")
            self.show_error("Fehler beim Speichern der Fertigkeit")

    def delete_fertigkeit(self, *args):
        """Löscht die ausgewählten Fertigkeiten"""
        try:
            if not self.dialog_content:
                self.show_error("Dialog-Content nicht gefunden.")
                return

            selected = self.dialog_content.get_selected_items()
            if not selected:
                self.show_error("Bitte wähle mindestens eine Fertigkeit zum Löschen aus.")
                return

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
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Fertigkeiten: {e}")
            self.show_error("Fehler beim Löschen der Fertigkeiten")


    def on_fertigkeit_select(self, fertigkeit_name):
        """Callback wenn eine Fertigkeit im Dropdown ausgewählt wurde"""
        self.selected_fertigkeit = fertigkeit_name
        if (self.dialog_content and
            hasattr(self.dialog_content.ids, 'selected_fertigkeit_text')):
            self.dialog_content.ids.selected_fertigkeit_text.text = fertigkeit_name
            Logger.info(f"Fertigkeit '{fertigkeit_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

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
