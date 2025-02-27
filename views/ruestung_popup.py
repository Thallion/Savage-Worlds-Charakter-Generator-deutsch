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

from models.ruestung import Ruestung

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
kv = '''
<RuestungDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "720dp"

    MDTextField:
        id: name_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Name der Rüstung'

    MDTextField:
        id: torso_input
        mode: "outlined"
        input_filter: 'int'
        
        MDTextFieldHintText:
            text: 'Schutzwert Torso'

    MDTextField:
        id: arme_input
        mode: "outlined"
        input_filter: 'int'
        
        MDTextFieldHintText:
            text: 'Schutzwert Arme'

    MDTextField:
        id: beine_input
        mode: "outlined"
        input_filter: 'int'
        
        MDTextFieldHintText:
            text: 'Schutzwert Beine'

    MDTextField:
        id: kopf_input
        mode: "outlined"
        input_filter: 'int'
        
        MDTextFieldHintText:
            text: 'Schutzwert Kopf'

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

<DeleteRuestungDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "120dp"

    MDDropDownItem:
        id: ruestung_dropdown
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: root.open_menu(self)

        MDDropDownItemText:
            id: selected_ruestung_text
            text: "Rüstung auswählen"
'''

Builder.load_string(kv)

class RuestungDialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

class DeleteRuestungDialogContent(MDBoxLayout):
    def __init__(self, ruestungen_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.ruestungen_callback = ruestungen_callback
        self.menu_callback = menu_callback
        self.dialog = None
        
    def open_menu(self, instance_item):
        if not self.ruestungen_callback:
            return
            
        ruestungen = self.ruestungen_callback()
        if not ruestungen:
            return
            
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in ruestungen
        ]
        
        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()
        
    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'ruestung_dropdown'):
            self.ids.ruestung_dropdown.text = text_item

class RuestungDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.dialog = None
        self.selected_ruestung = None
        self.dialog_content = None

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen einer neuen Rüstung"""
        dialog_content = RuestungDialogContent()
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Neue Rüstung hinzufügen",
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
                    on_release=self.save_ruestung,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def show_delete_dialog(self):
        """Zeigt den Dialog zum Löschen einer Rüstung"""
        if not self.get_all_ruestungen():
            self.show_error("Keine Rüstungen zum Löschen verfügbar.")
            return

        dialog_content = DeleteRuestungDialogContent(
            ruestungen_callback=self.get_all_ruestungen,
            menu_callback=self.on_ruestung_select
        )
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Rüstung löschen",
            ),
            MDDialogSupportingText(
                text="Wähle eine Rüstung zum Löschen:",
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
                    on_release=self.delete_ruestung,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def save_ruestung(self, *args):
        """Speichert eine neue Rüstung"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return
            
        # Grunddaten sammeln
        name = self.dialog_content.ids.name_input.text.strip()
        mindeststaerke = self.dialog_content.ids.mindeststaerke_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()
        
        # Rüstungswerte sammeln
        torso_text = self.dialog_content.ids.torso_input.text.strip()
        arme_text = self.dialog_content.ids.arme_input.text.strip()
        beine_text = self.dialog_content.ids.beine_input.text.strip()
        kopf_text = self.dialog_content.ids.kopf_input.text.strip()

        # Validierungen
        if not name:
            self.show_error("Der Name der Rüstung darf nicht leer sein.")
            return

        if mindeststaerke not in ['W4', 'W6', 'W8', 'W10', 'W12', '-']:
            self.show_error("Mindeststärke muss 'W4', 'W6', 'W8', 'W10', 'W12' oder '-' sein.")
            return

        try:
            torso = int(torso_text) if torso_text else 0
            arme = int(arme_text) if arme_text else 0
            beine = int(beine_text) if beine_text else 0
            kopf = int(kopf_text) if kopf_text else 0
            gewicht = float(gewicht_text) if gewicht_text else 0
            kosten = float(kosten_text) if kosten_text else 0
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für die Schutzwerte, Gewicht und Kosten ein.")
            return

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            if name in charakter.ausruestung:
                self.show_error(f"Rüstung '{name}' existiert bereits.")
                return

            new_ruestung = Ruestung(
                name=name,
                torso=torso,
                arme=arme,
                beine=beine,
                kopf=kopf,
                mindeststaerke=mindeststaerke,
                setting=setting,
                gewicht=gewicht,
                kosten=kosten,
                beschreibung=beschreibung,
                menge=0,
                ausgewaehlt=True,
                aktiv=True,
                angelegt=False,
                kategorie='Rüstung',
                custom=True
            )
            
            success = charakter.add_ausruestung(new_ruestung)
            
            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()
                
                self.dismiss_dialog()
                Logger.info(f"Rüstung '{name}' wurde hinzugefügt.")
            else:
                self.show_error(f"Rüstung '{name}' konnte nicht hinzugefügt werden.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Rüstung: {e}")
            self.show_error("Fehler beim Speichern der Rüstung")

    def delete_ruestung(self, *args):
        """Löscht die ausgewählte Rüstung"""
        try:
            if not self.selected_ruestung:
                self.show_error("Bitte wähle eine Rüstung zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter
            
            ruestung_name = self.selected_ruestung
            success = charakter.remove_ausruestung(ruestung_name)

            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()
                
                Logger.info(f"Rüstung '{ruestung_name}' wurde gelöscht.")
                self.dismiss_dialog()
            else:
                self.show_error(f"Rüstung '{ruestung_name}' konnte nicht gelöscht werden.")
                
        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Rüstung: {e}")
            self.show_error("Fehler beim Löschen der Rüstung")

    def on_ruestung_select(self, ruestung_name):
        """Callback wenn eine Rüstung im Dropdown ausgewählt wurde"""
        self.selected_ruestung = ruestung_name
        if (self.dialog_content and 
            hasattr(self.dialog_content.ids, 'selected_ruestung_text')):
            self.dialog_content.ids.selected_ruestung_text.text = ruestung_name
            Logger.info(f"Rüstung '{ruestung_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            self.dialog_content = None
            self.selected_ruestung = None

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

    def get_all_ruestungen(self):
        """Gibt eine Liste aller verfügbaren Rüstungen zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return [name for name, item in charakter.ausruestung.items() 
                       if isinstance(item, Ruestung)]
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Rüstungen: {e}")
        return []