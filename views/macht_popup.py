# macht-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
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

from models.macht import Macht

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
kv = '''
<MachtDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "520dp"

    MDTextField:
        id: name_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Name der Macht'

    MDTextField:
        id: rang_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Rang'

    MDTextField:
        id: machtpunkte_input
        mode: "outlined"
        input_filter: 'int'
        
        MDTextFieldHintText:
            text: 'Machtpunkte'

    MDTextField:
        id: reichweite_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Reichweite'

    MDTextField:
        id: dauer_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Dauer'

    MDTextField:
        id: effekt_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Effekt'

    MDTextField:
        id: beschreibung_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Beschreibung'

    MDTextField:
        id: voraussetzungen_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Voraussetzungen (durch Komma getrennt)'

<DeleteMachtDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "120dp"

    MDDropDownItem:
        id: macht_dropdown
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: root.open_menu(self)

        MDDropDownItemText:
            id: selected_macht_text
            text: "Macht auswählen"
'''

Builder.load_string(kv)

class MachtDialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        
class DeleteMachtDialogContent(MDBoxLayout):
    def __init__(self, maechte_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.maechte_callback = maechte_callback
        self.menu_callback = menu_callback
        self.dialog = None
        
    def open_menu(self, instance_item):
        if not self.maechte_callback:
            return
            
        maechte = self.maechte_callback()
        if not maechte:
            return
            
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in maechte
        ]
        
        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()
        
    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'macht_dropdown'):
            self.ids.macht_dropdown.text = text_item

class MachtDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.dialog = None
        self.selected_macht = None
        self.dialog_content = None

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen einer neuen Macht"""
        dialog_content = MachtDialogContent()
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Neue Macht hinzufügen",
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
                    on_release=self.save_macht,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def show_delete_dialog(self):
        """Zeigt den Dialog zum Löschen einer Macht"""
        if not self.get_all_maechte():
            self.show_error("Keine Mächte zum Löschen verfügbar.")
            return

        dialog_content = DeleteMachtDialogContent(
            maechte_callback=self.get_all_maechte,
            menu_callback=self.on_macht_select
        )
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Macht löschen",
            ),
            MDDialogSupportingText(
                text="Wähle eine Macht zum Löschen:",
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
                    on_release=self.delete_macht,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def save_macht(self, *args):
        """Speichert eine neue Macht"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return
            
        name = self.dialog_content.ids.name_input.text.strip()
        
        if not name:
            self.show_error("Der Name der Macht darf nicht leer sein.")
            return

        # Sammle alle Eingabedaten
        rang = self.dialog_content.ids.rang_input.text.strip()
        machtpunkte_text = self.dialog_content.ids.machtpunkte_input.text.strip()
        reichweite = self.dialog_content.ids.reichweite_input.text.strip()
        dauer = self.dialog_content.ids.dauer_input.text.strip()
        effekt = self.dialog_content.ids.effekt_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()
        voraussetzungen = [v.strip() for v in self.dialog_content.ids.voraussetzungen_input.text.split(',') if v.strip()]

        if not machtpunkte_text.isdigit():
            self.show_error("Machtpunkte müssen eine gültige Zahl sein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            if name in charakter.maechte:
                self.show_error(f"Macht '{name}' existiert bereits.")
                return

            new_macht = Macht(
                name=name,
                rang=rang,
                machtpunkte=int(machtpunkte_text),
                reichweite=reichweite,
                dauer=dauer,
                effekt=effekt,
                beschreibung=beschreibung,
                voraussetzungen=voraussetzungen,
                custom=True
            )
            
            success = charakter.add_macht(new_macht)
            
            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()
                
                self.dismiss_dialog()
                Logger.info(f"Macht '{name}' wurde hinzugefügt.")
            else:
                self.show_error(f"Macht '{name}' konnte nicht hinzugefügt werden.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Macht: {e}")
            self.show_error("Fehler beim Speichern der Macht")

    def delete_macht(self, *args):
        """Löscht die ausgewählte Macht"""
        try:
            if not self.selected_macht:
                self.show_error("Bitte wähle eine Macht zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter
            
            # Temporärer Speicher für den Namen zum Logging
            macht_name = self.selected_macht
            
            success = charakter.remove_macht(macht_name)

            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()
                
                Logger.info(f"Macht '{macht_name}' wurde gelöscht.")
                self.dismiss_dialog()
            else:
                self.show_error(f"Macht '{macht_name}' konnte nicht gelöscht werden.")
                
        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Macht: {e}")
            self.show_error("Fehler beim Löschen der Macht")

    def on_macht_select(self, macht_name):
        """Callback wenn eine Macht im Dropdown ausgewählt wurde"""
        self.selected_macht = macht_name
        # Dialog-Content aktualisieren wenn vorhanden
        if (self.dialog_content and 
            hasattr(self.dialog_content.ids, 'selected_macht_text')):
            self.dialog_content.ids.selected_macht_text.text = macht_name
            Logger.info(f"Macht '{macht_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            self.dialog_content = None
            self.selected_macht = None

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