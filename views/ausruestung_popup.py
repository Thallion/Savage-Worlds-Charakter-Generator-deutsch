from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock
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
        self.dialog = None
        self.selected_ausruestung = None
        self.dialog_content = None

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen einer neuen Ausrüstung"""
        dialog_content = AusruestungDialogContent()
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Neue Ausrüstung hinzufügen",
            ),
            MDDialogContentContainer(
                dialog_content,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=self.dismiss_dialog,
                ),
                MDButton(
                    MDButtonText(text="Speichern"),
                    style="text",
                    on_release=self.save_ausruestung,
                ),
                spacing="8dp",
            ),
            auto_dismiss=False,
        )
        self.dialog.open()

    def show_edit_dialog(self, ausruestung_name):
        """Zeigt den Dialog zum Bearbeiten einer bestehenden Ausrüstung"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            # Hole die Ausrüstung
            ausruestung = charakter.ausruestung.get(ausruestung_name)
            if not ausruestung:
                self.show_error(f"Ausrüstung '{ausruestung_name}' nicht gefunden.")
                return
            
            # Erstelle Dialog-Content mit Ausrüstungs-Daten
            ausruestung_data = {
                'name': ausruestung.name,
                'kategorie': getattr(ausruestung, 'kategorie', 'Allgemein'),
                'gewicht': ausruestung.gewicht,
                'kosten': ausruestung.kosten,
                'setting': ausruestung.setting,
                'beschreibung': ausruestung.beschreibung
            }
            
            dialog_content = AusruestungDialogContent(ausruestung_data=ausruestung_data)
            dialog_content.dialog = self.dialog
            self.dialog_content = dialog_content
            self.selected_ausruestung = ausruestung_name  # Speichere den Key für Updates
            
            self.dialog = MDDialog(
                MDDialogHeadlineText(
                    text="Ausrüstung bearbeiten",
                ),
                MDDialogContentContainer(
                    dialog_content,
                    orientation="vertical",
                ),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="Abbrechen"),
                        style="text",
                        on_release=self.dismiss_dialog,
                    ),
                    MDButton(
                        MDButtonText(text="Speichern"),
                        style="text",
                        on_release=self.update_ausruestung,
                    ),
                    spacing="8dp",
                ),
                auto_dismiss=False,
            )
            self.dialog.open()
            
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
                # Neuen Key erstellen
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
        """Zeigt den Dialog zum Löschen einer Ausrüstung"""
        if not self.get_all_ausruestung():
            self.show_error("Keine Ausrüstung zum Löschen verfügbar.")
            return

        dialog_content = DeleteAusruestungDialogContent(
            ausruestung_callback=self.get_all_ausruestung,
            menu_callback=self.on_ausruestung_select
        )
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Ausrüstung löschen",
            ),
            MDDialogSupportingText(
                text="Wähle eine Ausrüstung zum Löschen:",
            ),
            MDDialogContentContainer(
                dialog_content,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=self.dismiss_dialog,
                ),
                MDButton(
                    MDButtonText(text="Löschen"),
                    style="text",
                    on_release=self.delete_ausruestung,
                ),
                spacing="8dp",
            ),
            auto_dismiss=False,
        )
        self.dialog.open()

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
        """Löscht die ausgewählte Ausrüstung"""
        try:
            if not self.selected_ausruestung:
                self.show_error("Bitte wähle eine Ausrüstung zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter
            
            ausruestung_name = self.selected_ausruestung
            success = charakter.remove_ausruestung(ausruestung_name)

            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()
                
                Logger.info(f"Ausrüstung '{ausruestung_name}' wurde gelöscht.")
                self.dismiss_dialog()
            else:
                self.show_error(f"Ausrüstung '{ausruestung_name}' konnte nicht gelöscht werden.")
                
        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Ausrüstung: {e}")
            self.show_error("Fehler beim Löschen der Ausrüstung")

    def on_ausruestung_select(self, ausruestung_name):
        """Callback wenn eine Ausrüstung im Dropdown ausgewählt wurde"""
        self.selected_ausruestung = ausruestung_name
        if (self.dialog_content and 
            hasattr(self.dialog_content.ids, 'selected_ausruestung_text')):
            self.dialog_content.ids.selected_ausruestung_text.text = ausruestung_name
            Logger.info(f"Ausrüstung '{ausruestung_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            self.dialog_content = None
            self.selected_ausruestung = None

    def show_error(self, message):
        """Zeigt eine Fehlermeldung im Dialog an"""
        error_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Fehler",
            ),
            MDDialogSupportingText(
                text=message,
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Schließen"),
                    style="text",
                    on_release=lambda x: error_dialog.dismiss(),
                ),
                spacing="8dp",
            ),
            auto_dismiss=False,
        )
        error_dialog.open()

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