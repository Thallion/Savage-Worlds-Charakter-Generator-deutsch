from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogContentContainer,
    MDDialogButtonContainer,
)
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.ausruestung import Ausruestung

import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'ausruestung_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'ausruestung_popup.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"ausruestung_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class AusruestungDialogContent(MDBoxLayout):
    def __init__(self, ausruestung_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_mode = False
        self.original_name = None
        
        # Wenn Ausrüstungs-Daten übergeben wurden, befülle die Felder
        if ausruestung_data:
            self.edit_mode = True
            self.original_name = ausruestung_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(ausruestung_data), 0.1)
    
    def _fill_fields(self, ausruestung_data):
        """Befüllt die Felder mit den Ausrüstungs-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = ausruestung_data.get('name', '')
        
        if hasattr(self.ids, 'kategorie_input'):
            self.ids.kategorie_input.text = ausruestung_data.get('kategorie', '')
        
        if hasattr(self.ids, 'gewicht_input'):
            self.ids.gewicht_input.text = str(ausruestung_data.get('gewicht', 0))
        
        if hasattr(self.ids, 'kosten_input'):
            self.ids.kosten_input.text = str(ausruestung_data.get('kosten', 0))
        
        if hasattr(self.ids, 'setting_input'):
            self.ids.setting_input.text = ausruestung_data.get('setting', '')
        
        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = ausruestung_data.get('beschreibung', '')

class DeleteAusruestungDialogContent(MDBoxLayout):
    def __init__(self, ausruestung_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.ausruestung_callback = ausruestung_callback
        self.menu_callback = menu_callback
        self.dialog = None
        
    def open_menu(self, instance_item):
        if not self.ausruestung_callback:
            return
            
        ausruestung = self.ausruestung_callback()
        if not ausruestung:
            return
            
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in ausruestung
        ]
        
        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()
        
    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'ausruestung_dropdown'):
            self.ids.ausruestung_dropdown.text = text_item

class AusruestungDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.selected_ausruestung = None
        self.dialog_content = None

    def _get_overlay(self):
        """Gibt eine gecachte ElementOverlay-Instanz zurück"""
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt das Overlay zum Hinzufügen einer neuen Ausrüstung"""
        dialog_content = AusruestungDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neue Ausrüstung hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_ausruestung,
        )

    def show_edit_dialog(self, ausruestung_name):
        """Zeigt das Overlay zum Bearbeiten einer bestehenden Ausrüstung"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            ausruestung = charakter.ausruestung.get(ausruestung_name)
            if not ausruestung:
                self.show_error(f"Ausrüstung '{ausruestung_name}' nicht gefunden.")
                return

            ausruestung_data = {
                'name': ausruestung.name,
                'kategorie': getattr(ausruestung, 'kategorie', 'Allgemein'),
                'gewicht': ausruestung.gewicht,
                'kosten': ausruestung.kosten,
                'setting': ausruestung.setting,
                'beschreibung': ausruestung.beschreibung
            }

            dialog_content = AusruestungDialogContent(ausruestung_data=ausruestung_data)
            self.dialog_content = dialog_content
            self.selected_ausruestung = ausruestung_name

            overlay = self._get_overlay()
            overlay.open(
                title="Ausrüstung bearbeiten",
                content_widget=dialog_content,
                action_text="Speichern",
                on_action=self.update_ausruestung,
            )

        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
            self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def update_ausruestung(self, *args):
        """Aktualisiert eine bestehende Ausrüstung"""
        if not self.dialog_content or not self.selected_ausruestung:
            Logger.error("Dialog-Content oder ausgewählte Ausrüstung nicht gefunden")
            return

        # Grunddaten sammeln
        name = self.dialog_content.ids.name_input.text.strip()
        kategorie = self.dialog_content.ids.kategorie_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()

        # Validierungen
        if not name:
            self.show_error("Der Name der Ausrüstung darf nicht leer sein.")
            return

        if not kategorie:
            self.show_error("Bitte geben Sie eine Kategorie an.")
            return

        try:
            gewicht = float(gewicht_text) if gewicht_text else 0
            kosten = float(kosten_text) if kosten_text else 0
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für Gewicht und Kosten ein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            # Hole die bestehende Ausrüstung
            ausruestung = charakter.ausruestung.get(self.selected_ausruestung)
            if not ausruestung:
                self.show_error(f"Ausrüstung '{self.selected_ausruestung}' nicht mehr gefunden.")
                return

            # Wenn der Name geändert wurde und bereits existiert
            if name != ausruestung.name and name in charakter.ausruestung:
                self.show_error(f"Ausrüstung mit dem Namen '{name}' existiert bereits.")
                return

            # Aktualisiere die Ausrüstung
            old_name = ausruestung.name
            ausruestung.name = name
            ausruestung.kategorie = kategorie
            ausruestung.gewicht = gewicht
            ausruestung.kosten = kosten
            ausruestung.setting = setting
            ausruestung.beschreibung = beschreibung

            # Bei Namensänderung: Key im Dictionary ändern
            if name != old_name:
                charakter.ausruestung[name] = ausruestung
                if old_name in charakter.ausruestung:
                    del charakter.ausruestung[old_name]

            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            self.dismiss_dialog()
            Logger.info(f"Ausrüstung '{name}' wurde aktualisiert.")

        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Ausrüstung: {e}")
            self.show_error("Fehler beim Aktualisieren der Ausrüstung")

    def show_delete_dialog(self):
        """Zeigt das Overlay zum Löschen von Ausrüstung (suchbare Liste mit Mehrfachauswahl)"""
        ausruestung = self.get_all_ausruestung()
        if not ausruestung:
            self.show_error("Keine Ausrüstung zum Löschen verfügbar.")
            return

        from views.element_overlay import ElementListContent
        content = ElementListContent(
            items=ausruestung,
            multi_select=True,
        )
        self.dialog_content = content

        overlay = self._get_overlay()
        overlay.open(
            title="Ausrüstung löschen",
            content_widget=content,
            action_text="Löschen",
            on_action=self.delete_ausruestung,
        )

    def save_ausruestung(self, *args):
        """Speichert eine neue Ausrüstung"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return

        # Grunddaten sammeln
        name = self.dialog_content.ids.name_input.text.strip()
        kategorie = self.dialog_content.ids.kategorie_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()

        # Validierungen
        if not name:
            self.show_error("Der Name der Ausrüstung darf nicht leer sein.")
            return

        if not kategorie:
            self.show_error("Bitte geben Sie eine Kategorie an.")
            return

        try:
            gewicht = float(gewicht_text) if gewicht_text else 0
            kosten = float(kosten_text) if kosten_text else 0
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für Gewicht und Kosten ein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            if name in charakter.ausruestung:
                self.show_error(f"Ausrüstung '{name}' existiert bereits.")
                return

            new_ausruestung = Ausruestung(
                name=name,
                kategorie=kategorie,
                gewicht=gewicht,
                kosten=kosten,
                setting=setting,
                beschreibung=beschreibung,
                menge=0,
                ausgewaehlt=True,
                aktiv=True,
                angelegt=False,
                custom=True
            )

            success = charakter.add_ausruestung(new_ausruestung)

            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()

                self.dismiss_dialog()
                Logger.info(f"Ausrüstung '{name}' wurde hinzugefügt.")
            else:
                self.show_error(f"Ausrüstung '{name}' konnte nicht hinzugefügt werden.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Ausrüstung: {e}")
            self.show_error("Fehler beim Speichern der Ausrüstung")

    def delete_ausruestung(self, *args):
        """Löscht die ausgewählten Ausrüstungen"""
        try:
            if not self.dialog_content:
                self.show_error("Dialog-Content nicht gefunden.")
                return

            selected = self.dialog_content.get_selected_items()
            if not selected:
                self.show_error("Bitte wähle mindestens eine Ausrüstung zum Löschen aus.")
                return

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
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Ausrüstungen: {e}")
            self.show_error("Fehler beim Löschen der Ausrüstungen")

    def on_ausruestung_select(self, ausruestung_name):
        """Callback wenn eine Ausrüstung ausgewählt wurde"""
        self.selected_ausruestung = ausruestung_name

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_ausruestung = None

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
        Logger.error(f"Ausrüstung-Fehler: {message}")

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
            Logger.debug(f"Ausrüstung-Widget nicht gefunden: {e}")

    def _show_success_snackbar(self, message):
        """Zeigt eine Erfolgs-Snackbar an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass