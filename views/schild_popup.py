# schild-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.app import App
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

from models.schild import Schild

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
kv = '''
<SchildDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "520dp"

    MDTextField:
        id: name_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Name des Schildes'

    MDTextField:
        id: parade_input
        mode: "outlined"
        input_filter: 'int'
        
        MDTextFieldHintText:
            text: 'Paradebonus'

    MDTextField:
        id: deckung_input
        mode: "outlined"
        input_filter: 'int'
        
        MDTextFieldHintText:
            text: 'Deckung'

    MDTextField:
        id: mindeststaerke_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Mindeststärke (z.B. W4, W6)'

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

<DeleteSchildDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "120dp"

    MDDropDownItem:
        id: schild_dropdown
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: root.open_menu(self)

        MDDropDownItemText:
            id: selected_schild_text
            text: "Schild auswählen"
'''

Builder.load_string(kv)

class SchildDialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

class DeleteSchildDialogContent(MDBoxLayout):
    def __init__(self, schilde_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.schilde_callback = schilde_callback
        self.menu_callback = menu_callback
        self.dialog = None
        
    def open_menu(self, instance_item):
        if not self.schilde_callback:
            return
            
        schilde = self.schilde_callback()
        if not schilde:
            return
            
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in schilde
        ]
        
        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()
        
    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'schild_dropdown'):
            self.ids.schild_dropdown.text = text_item

class SchildDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.dialog = None
        self.selected_schild = None
        self.dialog_content = None

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen eines neuen Schildes"""
        dialog_content = SchildDialogContent()
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Neues Schild hinzufügen",
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
                    on_release=self.save_schild,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def show_delete_dialog(self):
        """Zeigt den Dialog zum Löschen eines Schildes"""
        if not self.get_all_schilde():
            self.show_error("Keine Schilde zum Löschen verfügbar.")
            return

        dialog_content = DeleteSchildDialogContent(
            schilde_callback=self.get_all_schilde,
            menu_callback=self.on_schild_select
        )
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Schild löschen",
            ),
            MDDialogSupportingText(
                text="Wähle ein Schild zum Löschen:",
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
                    on_release=self.delete_schild,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def save_schild(self, *args):
        """Speichert ein neues Schild"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return
            
        name = self.dialog_content.ids.name_input.text.strip()
        
        if not name:
            self.show_error("Der Name des Schildes darf nicht leer sein.")
            return

        # Validierung der Eingaben
        parade_text = self.dialog_content.ids.parade_input.text.strip()
        deckung_text = self.dialog_content.ids.deckung_input.text.strip()
        mindeststaerke = self.dialog_content.ids.mindeststaerke_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()

        # Validierung der Eingaben
        if mindeststaerke not in ['W4', 'W6', 'W8', 'W10', 'W12', '-']:
            self.show_error("Mindeststärke muss 'W4', 'W6', 'W8', 'W10', 'W12' oder '-' sein.")
            return
            
        try:
            parade = int(parade_text)
            deckung = int(deckung_text)
            gewicht = float(gewicht_text)
            kosten = float(kosten_text)
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für Parade, Deckung, Gewicht und Kosten ein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            # Prüfen ob das Schild bereits existiert
            if name in charakter.ausruestung:
                self.show_error(f"Schild '{name}' existiert bereits.")
                return

            new_schild = Schild(
                name=name,
                gewicht=gewicht,
                kosten=kosten,
                setting=setting,
                parade=parade,
                deckung=deckung,
                mindeststaerke=mindeststaerke,
                beschreibung=beschreibung,
                menge=0,
                ausgewaehlt=True,
                aktiv=True,
                angelegt=False,
                kategorie='Schild',
                custom=True
            )
            
            success = charakter.add_ausruestung(new_schild)
            
            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()
                
                self.dismiss_dialog()
                Logger.info(f"Schild '{name}' wurde hinzugefügt.")
            else:
                self.show_error(f"Schild '{name}' konnte nicht hinzugefügt werden.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Schilds: {e}")
            self.show_error("Fehler beim Speichern des Schilds")

    def delete_schild(self, *args):
        """Löscht das ausgewählte Schild"""
        try:
            if not self.selected_schild:
                self.show_error("Bitte wähle ein Schild zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter
            
            schild_name = self.selected_schild
            success = charakter.remove_ausruestung(schild_name)

            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()
                
                Logger.info(f"Schild '{schild_name}' wurde gelöscht.")
                self.dismiss_dialog()
            else:
                self.show_error(f"Schild '{schild_name}' konnte nicht gelöscht werden.")
                
        except Exception as e:
            Logger.error(f"Fehler beim Löschen des Schilds: {e}")
            self.show_error("Fehler beim Löschen des Schilds")

    def on_schild_select(self, schild_name):
        """Callback wenn ein Schild im Dropdown ausgewählt wurde"""
        self.selected_schild = schild_name
        if (self.dialog_content and 
            hasattr(self.dialog_content.ids, 'selected_schild_text')):
            self.dialog_content.ids.selected_schild_text.text = schild_name
            Logger.info(f"Schild '{schild_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            self.dialog_content = None
            self.selected_schild = None

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

    def get_all_schilde(self):
        """Gibt eine Liste aller verfügbaren Schilde zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return [name for name, item in charakter.ausruestung.items() if isinstance(item, Schild)]
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Schilde: {e}")
        return []