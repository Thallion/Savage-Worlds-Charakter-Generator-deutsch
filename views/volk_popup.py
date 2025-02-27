# volk-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.volk import Volk

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
kv = '''
<VolkDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "320dp"

    MDTextField:
        id: name_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Name des Volkes'

    MDTextField:
        id: handicaps_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Handicaps (durch Komma getrennt)'

    MDTextField:
        id: talente_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Talente (durch Komma getrennt)'

    MDTextField:
        id: besonderheiten_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Besonderheiten (durch Komma getrennt)'

<DeleteVolkDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "120dp"

    MDDropDownItem:
        id: volk_dropdown
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: root.open_menu(self)

        MDDropDownItemText:
            id: selected_volk_text
            text: "Volk auswählen"
'''

Builder.load_string(kv)

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
        self.dialog = None
        self.selected_volk = None
        self.dialog_content = None

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen eines neuen Volkes"""
        dialog_content = VolkDialogContent()
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Neues Volk hinzufügen",
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
                    on_release=self.save_volk,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def show_delete_dialog(self):
        """Zeigt den Dialog zum Löschen eines Volkes"""
        if not self.get_all_voelker():
            self.show_error("Keine Völker zum Löschen verfügbar.")
            return

        dialog_content = DeleteVolkDialogContent(
            voelker_callback=self.get_all_voelker,
            menu_callback=self.on_volk_select
        )
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Volk löschen",
            ),
            MDDialogSupportingText(
                text="Wähle ein Volk zum Löschen:",
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
                    on_release=self.delete_volk,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

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
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            self.dialog_content = None
            self.selected_volk = None

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