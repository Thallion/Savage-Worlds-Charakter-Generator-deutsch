# fertigkeit-popup.py
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
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel

from models.fertigkeit import Fertigkeit

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
kv = '''
<FertigkeitDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "280dp"

    MDTextField:
        id: name_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Name der Fertigkeit'

    MDDropDownItem:
        id: attribut_dropdown
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: root.open_attribut_menu(self)

        MDDropDownItemText:
            id: selected_attribut_text
            text: "Attribut wählen"

    MDBoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: "48dp"
        spacing: "8dp"
        padding: ["4dp", "0dp", "0dp", "0dp"]

        MDCheckbox:
            id: grundfertigkeit_checkbox
            active: False
            size_hint: None, None
            size: "48dp", "48dp"

        MDLabel:
            text: 'Grundfertigkeit'
            adaptive_size: True

<DeleteFertigkeitDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "120dp"

    MDDropDownItem:
        id: fertigkeit_dropdown
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: root.open_menu(self)

        MDDropDownItemText:
            id: selected_fertigkeit_text
            text: "Fertigkeit auswählen"
'''

Builder.load_string(kv)

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

class FertigkeitDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.dialog = None
        self.selected_fertigkeit = None
        self.dialog_content = None

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen einer neuen Fertigkeit"""
        dialog_content = FertigkeitDialogContent()
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Neue Fertigkeit hinzufügen",
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
                    on_release=self.save_fertigkeit,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def show_delete_dialog(self):
        """Zeigt den Dialog zum Löschen einer Fertigkeit"""
        if not self.get_all_fertigkeiten():
            self.show_error("Keine Fertigkeiten zum Löschen verfügbar.")
            return

        dialog_content = DeleteFertigkeitDialogContent(
            fertigkeiten_callback=self.get_all_fertigkeiten,
            menu_callback=self.on_fertigkeit_select
        )
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Fertigkeit löschen",
            ),
            MDDialogSupportingText(
                text="Wähle eine Fertigkeit zum Löschen:",
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
                    on_release=self.delete_fertigkeit,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

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
        """Löscht die ausgewählte Fertigkeit"""
        try:
            if not self.selected_fertigkeit:
                self.show_error("Bitte wähle eine Fertigkeit zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter
            
            fertigkeit_name = self.selected_fertigkeit
            
            # Lösche die Fertigkeit
            charakter.remove_fertigkeit(fertigkeit_name)
            
            # Speichere die Custom Fertigkeiten
            charakter.save_custom_fertigkeiten()
            
            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            
            Logger.info(f"Fertigkeit '{fertigkeit_name}' wurde gelöscht.")
            self.dismiss_dialog()
                
        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Fertigkeit: {e}")
            self.show_error("Fehler beim Löschen der Fertigkeit")

    def on_fertigkeit_select(self, fertigkeit_name):
        """Callback wenn eine Fertigkeit im Dropdown ausgewählt wurde"""
        self.selected_fertigkeit = fertigkeit_name
        if (self.dialog_content and 
            hasattr(self.dialog_content.ids, 'selected_fertigkeit_text')):
            self.dialog_content.ids.selected_fertigkeit_text.text = fertigkeit_name
            Logger.info(f"Fertigkeit '{fertigkeit_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            self.dialog_content = None
            self.selected_fertigkeit = None

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