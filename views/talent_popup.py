# talent-popup.py
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

from models.talent import Talent

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
kv = '''
<TalentDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "520dp"

    MDTextField:
        id: name_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Name des Talents'

    MDTextField:
        id: kategorie_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Kategorie'

    MDTextField:
        id: rang_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Rang'

    MDTextField:
        id: beschreibung_input
        mode: "outlined"
        multiline: True
        
        MDTextFieldHintText:
            text: 'Beschreibung'

    MDTextField:
        id: voraussetzungen_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Voraussetzungen (durch Komma getrennt)'

    MDTextField:
        id: neue_maechte_input
        mode: "outlined"
        input_filter: 'int'
        
        MDTextFieldHintText:
            text: 'Neue Mächte (Anzahl)'

    MDTextField:
        id: machtpunkte_input
        mode: "outlined"
        input_filter: 'int'
        
        MDTextFieldHintText:
            text: 'Machtpunkte'

<DeleteTalentDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "120dp"

    MDDropDownItem:
        id: talent_dropdown
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: root.open_menu(self)

        MDDropDownItemText:
            id: selected_talent_text
            text: "Talent auswählen"
'''

Builder.load_string(kv)

class TalentDialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        
class DeleteTalentDialogContent(MDBoxLayout):
    def __init__(self, talente_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.talente_callback = talente_callback
        self.menu_callback = menu_callback
        self.dialog = None
        
    def open_menu(self, instance_item):
        if not self.talente_callback:
            return
            
        talente = self.talente_callback()
        if not talente:
            return
            
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in talente
        ]
        
        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()
        
    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'talent_dropdown'):
            self.ids.talent_dropdown.text = text_item

class TalentDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.dialog = None
        self.selected_talent = None
        self.dialog_content = None

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen eines neuen Talents"""
        dialog_content = TalentDialogContent()
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Neues Talent hinzufügen",
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
                    on_release=self.save_talent,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def show_delete_dialog(self):
        """Zeigt den Dialog zum Löschen eines Talents"""
        if not self.get_all_talente():
            self.show_error("Keine Talente zum Löschen verfügbar.")
            return

        dialog_content = DeleteTalentDialogContent(
            talente_callback=self.get_all_talente,
            menu_callback=self.on_talent_select
        )
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Talent löschen",
            ),
            MDDialogSupportingText(
                text="Wähle ein Talent zum Löschen:",
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
                    on_release=self.delete_talent,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def save_talent(self, *args):
        """Speichert ein neues Talent"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return
            
        name = self.dialog_content.ids.name_input.text.strip()
        
        if not name:
            self.show_error("Der Name des Talents darf nicht leer sein.")
            return

        # Sammle alle Eingabedaten
        kategorie = self.dialog_content.ids.kategorie_input.text.strip()
        rang = self.dialog_content.ids.rang_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()
        voraussetzungen = [v.strip() for v in self.dialog_content.ids.voraussetzungen_input.text.split(',') if v.strip()]
        neue_maechte_text = self.dialog_content.ids.neue_maechte_input.text.strip()
        machtpunkte_text = self.dialog_content.ids.machtpunkte_input.text.strip()

        # Validiere numerische Eingaben
        if neue_maechte_text and not neue_maechte_text.isdigit():
            self.show_error("Neue Mächte muss eine gültige Zahl sein.")
            return

        if machtpunkte_text and not machtpunkte_text.isdigit():
            self.show_error("Machtpunkte müssen eine gültige Zahl sein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            if name in charakter.talente:
                self.show_error(f"Talent '{name}' existiert bereits.")
                return

            new_talent = Talent(
                name=name,
                kategorie=kategorie,
                rang=rang,
                beschreibung=beschreibung,
                voraussetzungen=voraussetzungen,
                neue_maechte=int(neue_maechte_text) if neue_maechte_text else 0,
                machtpunkte=int(machtpunkte_text) if machtpunkte_text else 0,
                custom=True
            )
            
            # Füge das Talent hinzu
            charakter.add_talent(new_talent)
            
            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            
            self.dismiss_dialog()
            Logger.info(f"Talent '{name}' wurde hinzugefügt.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Talents: {e}")
            self.show_error("Fehler beim Speichern des Talents")

    def delete_talent(self, *args):
        """Löscht das ausgewählte Talent"""
        try:
            if not self.selected_talent:
                self.show_error("Bitte wähle ein Talent zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter
            
            talent_name = self.selected_talent
            
            # Lösche das Talent
            charakter.remove_talent(talent_name)
            
            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            
            Logger.info(f"Talent '{talent_name}' wurde gelöscht.")
            self.dismiss_dialog()
                
        except Exception as e:
            Logger.error(f"Fehler beim Löschen des Talents: {e}")
            self.show_error("Fehler beim Löschen des Talents")

    def on_talent_select(self, talent_name):
        """Callback wenn ein Talent im Dropdown ausgewählt wurde"""
        self.selected_talent = talent_name
        if (self.dialog_content and 
            hasattr(self.dialog_content.ids, 'selected_talent_text')):
            self.dialog_content.ids.selected_talent_text.text = talent_name
            Logger.info(f"Talent '{talent_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            self.dialog_content = None
            self.selected_talent = None

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

    def get_all_talente(self):
        """Gibt eine Liste aller verfügbaren Talente zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.talente.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Talente: {e}")
        return []