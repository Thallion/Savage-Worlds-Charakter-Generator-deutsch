from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.app import App
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

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
kv = '''
<AusruestungDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "480dp"

    MDTextField:
        id: name_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Name der Ausrüstung'

    MDTextField:
        id: kategorie_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Kategorie'

    MDTextField:
        id: gewicht_input
        mode: "outlined"
        input_filter: 'float'
        
        MDTextFieldHintText:
            text: 'Gewicht'

    MDTextField:
        id: kosten_input
        mode: "outlined"
        input_filter: 'float'
        
        MDTextFieldHintText:
            text: 'Kosten'

    MDTextField:
        id: setting_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Setting'

    MDTextField:
        id: beschreibung_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Beschreibung'

<DeleteAusruestungDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "120dp"

    MDDropDownItem:
        id: ausruestung_dropdown
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: root.open_menu(self)

        MDDropDownItemText:
            id: selected_ausruestung_text
            text: "Ausrüstung auswählen"
'''

Builder.load_string(kv)

class AusruestungDialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

class DeleteAusruestungDialogContent(MDBoxLayout):
    def __init__(self, ausruestung_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.ausruestung_callback = ausruestung_callback
        self.menu_callback = menu_callback
        self.dialog = None
        
    def open_menu(self, instance_item):
        if not self.ausruestung_callback:
            return
            
        ausruestungen = self.ausruestung_callback()
        if not ausruestungen:
            return
            
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in ausruestungen
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
        )
        self.dialog.open()

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