# handicap-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.app import App
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.handicap import Handicap

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
kv = '''
<HandicapDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "320dp"

    MDTextField:
        id: name_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Name des Handicaps'

    MDDropDownItem:
        id: stufe_dropdown
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: root.open_stufen_menu(self)

        MDDropDownItemText:
            id: selected_stufe_text
            text: "Stufe wählen"

    MDTextField:
        id: beschreibung_input
        mode: "outlined"
        multiline: True
        
        MDTextFieldHintText:
            text: 'Beschreibung'

<DeleteHandicapDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "120dp"

    MDDropDownItem:
        id: handicap_dropdown
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: root.open_menu(self)

        MDDropDownItemText:
            id: selected_handicap_text
            text: "Handicap auswählen"
'''

Builder.load_string(kv)

class HandicapDialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.selected_stufe = None

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

class HandicapDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.dialog = None
        self.selected_handicap = None
        self.dialog_content = None

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen eines neuen Handicaps"""
        dialog_content = HandicapDialogContent()
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Neues Handicap hinzufügen",
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
                    on_release=self.save_handicap,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def show_delete_dialog(self):
        """Zeigt den Dialog zum Löschen eines Handicaps"""
        if not self.get_all_handicaps():
            self.show_error("Keine Handicaps zum Löschen verfügbar.")
            return

        dialog_content = DeleteHandicapDialogContent(
            handicaps_callback=self.get_all_handicaps,
            menu_callback=self.on_handicap_select
        )
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Handicap löschen",
            ),
            MDDialogSupportingText(
                text="Wähle ein Handicap zum Löschen:",
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
                    on_release=self.delete_handicap,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

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
            
            self.dismiss_dialog()
            Logger.info(f"Handicap '{name}' wurde hinzugefügt.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Handicaps: {e}")
            self.show_error("Fehler beim Speichern des Handicaps")

    def delete_handicap(self, *args):
        """Löscht das ausgewählte Handicap"""
        try:
            if not self.selected_handicap:
                self.show_error("Bitte wähle ein Handicap zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter
            
            handicap_name = self.selected_handicap
            
            # Lösche das Handicap
            charakter.remove_handicap(handicap_name)
            
            # Speichere die Custom Handicaps
            charakter.save_custom_handicaps()
            
            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            
            Logger.info(f"Handicap '{handicap_name}' wurde gelöscht.")
            self.dismiss_dialog()
                
        except Exception as e:
            Logger.error(f"Fehler beim Löschen des Handicaps: {e}")
            self.show_error("Fehler beim Löschen des Handicaps")

    def on_handicap_select(self, handicap_name):
        """Callback wenn ein Handicap im Dropdown ausgewählt wurde"""
        self.selected_handicap = handicap_name
        if (self.dialog_content and 
            hasattr(self.dialog_content.ids, 'selected_handicap_text')):
            self.dialog_content.ids.selected_handicap_text.text = handicap_name
            Logger.info(f"Handicap '{handicap_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            self.dialog_content = None
            self.selected_handicap = None

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
        )
        error_dialog.open()

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