# volk-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.app import App
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.volk import Volk

import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'volk_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'volk_popup.kv')

    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"volk_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class VolkDialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

class DeleteVolkDialogContent(MDBoxLayout):
    def __init__(self, voelker_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.voelker_callback = voelker_callback
        self.menu_callback = menu_callback
        self.dialog = None

    def open_menu(self, instance_item):
        if not self.voelker_callback:
            return

        voelker = self.voelker_callback()
        if not voelker:
            return

        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in voelker
        ]

        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()

    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'volk_dropdown'):
            self.ids.volk_dropdown.text = text_item

class VolkDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.selected_volk = None
        self.dialog_content = None

    def _get_overlay(self):
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen eines neuen Volkes"""
        dialog_content = VolkDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neues Volk hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_volk,
        )

    def show_delete_dialog(self):
        """Zeigt das Overlay zum Löschen eines Volkes (suchbare Liste)"""
        voelker = self.get_all_voelker()
        if not voelker:
            self.show_error("Keine Völker zum Löschen verfügbar.")
            return

        from views.element_overlay import ElementListContent
        content = ElementListContent(
            items=voelker,
            on_select=self.on_volk_select,
        )
        self.dialog_content = content

        overlay = self._get_overlay()
        overlay.open(
            title="Volk löschen",
            content_widget=content,
            action_text="Löschen",
            on_action=self.delete_volk,
        )

    def save_volk(self, *args):
        """Speichert ein neues Volk"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name des Volkes darf nicht leer sein.")
            return

        handicaps = [h.strip() for h in self.dialog_content.ids.handicaps_input.text.split(',') if h.strip()]
        talente = [t.strip() for t in self.dialog_content.ids.talente_input.text.split(',') if t.strip()]
        besonderheiten = [b.strip() for b in self.dialog_content.ids.besonderheiten_input.text.split(',') if b.strip()]

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            if name in charakter.voelker:
                self.show_error(f"Volk '{name}' existiert bereits.")
                return

            new_volk = Volk(
                name=name,
                handicaps=handicaps,
                talente=talente,
                besonderheiten=besonderheiten,
                custom=True
            )

            charakter.voelker[name] = new_volk

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            self.dismiss_dialog()
            Logger.info(f"Volk '{name}' wurde hinzugefügt.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Volks: {e}")
            self.show_error("Fehler beim Speichern des Volks")

    def delete_volk(self, *args):
        """Löscht das ausgewählte Volk"""
        try:
            if not self.selected_volk:
                self.show_error("Bitte wähle ein Volk zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter

            # Temporärer Speicher für den Namen zum Logging
            volk_name = self.selected_volk

            if volk_name in charakter.voelker:
                if charakter.voelker[volk_name].ausgewaehlt:
                    self.show_error(f"Volk '{volk_name}' ist ausgewählt und kann nicht gelöscht werden.")
                    return

                del charakter.voelker[volk_name]

                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()

                Logger.info(f"Volk '{volk_name}' wurde gelöscht.")
                self.dismiss_dialog()
            else:
                self.show_error(f"Volk '{volk_name}' nicht gefunden.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen des Volks: {e}")
            self.show_error("Fehler beim Löschen des Volks")

    def on_volk_select(self, volk_name):
        """Callback wenn ein Volk im Dropdown ausgewählt wurde"""
        self.selected_volk = volk_name
        # Dialog-Content aktualisieren wenn vorhanden
        if (self.dialog_content and
            hasattr(self.dialog_content.ids, 'selected_volk_text')):
            self.dialog_content.ids.selected_volk_text.text = volk_name
            Logger.info(f"Volk '{volk_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_volk = None

    def show_error(self, message):
        """Zeigt eine Fehlermeldung an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_warning_dialog(message)
                return
        except Exception:
            pass
        Logger.error(f"Volk-Fehler: {message}")

    def get_all_voelker(self):
        """Gibt eine Liste aller verfügbaren Völker zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.voelker.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Völker: {e}")
        return []
