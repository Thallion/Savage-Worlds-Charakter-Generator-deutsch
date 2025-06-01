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
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu

from models.waffe import Waffe

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
kv = '''
<WaffeDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "720dp"

    MDTextField:
        id: name_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Name der Waffe'

    MDSegmentedButton:
        id: typ_segment
        pos_hint: {"center_x": .5}
        
        MDSegmentedButtonItem:
            id: nahkampf_button
            size_hint: None, None
            size: dp(120), dp(40)
            on_release: root.select_typ('Nahkampf')
            selected: True

            MDSegmentButtonLabel:
                text: "Nahkampf"

        MDSegmentedButtonItem:
            id: fernkampf_button
            size_hint: None, None
            size: dp(120), dp(40)
            on_release: root.select_typ('Fernkampf')

            MDSegmentButtonLabel:
                text: "Fernkampf"

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
        id: schaden_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Schaden (z.B. Stä+W8)'

    MDTextField:
        id: reichweite_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Reichweite'

    MDTextField:
        id: fr_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Feuerrate (FR)'

    MDTextField:
        id: schuss_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Schuss'

    MDTextField:
        id: pb_input
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Panzerbrechend (PB)'

    MDTextField:
        id: beschreibung_input
        mode: "outlined"
        multiline: True
        
        MDTextFieldHintText:
            text: 'Beschreibung'

<DeleteWaffeDialogContent>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    size_hint_y: None
    height: "120dp"

    MDDropDownItem:
        id: waffe_dropdown
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: root.open_menu(self)

        MDDropDownItemText:
            id: selected_waffe_text
            text: "Waffe auswählen"
'''

Builder.load_string(kv)

# WaffeDialogContent
class WaffeDialogContent(MDBoxLayout):
    def __init__(self, waffe_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_mode = False
        self.original_name = None
        
        # Wenn Waffen-Daten übergeben wurden, befülle die Felder
        if waffe_data:
            self.edit_mode = True
            self.original_name = waffe_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(waffe_data), 0.1)
    
    def _fill_fields(self, waffe_data):
        """Befüllt die Felder mit den Waffen-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = waffe_data.get('name', '')
        
        if hasattr(self.ids, 'typ_segment'):
            self.select_typ(waffe_data.get('typ', 'Nahkampf'))
        
        if hasattr(self.ids, 'mindeststaerke_input'):
            self.ids.mindeststaerke_input.text = waffe_data.get('mindeststaerke', '')
        
        if hasattr(self.ids, 'gewicht_input'):
            self.ids.gewicht_input.text = str(waffe_data.get('gewicht', 0))
        
        if hasattr(self.ids, 'kosten_input'):
            self.ids.kosten_input.text = str(waffe_data.get('kosten', 0))
        
        if hasattr(self.ids, 'setting_input'):
            self.ids.setting_input.text = waffe_data.get('setting', '')
        
        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = waffe_data.get('beschreibung', '')
        
        # Eigenschaften
        eigenschaften = waffe_data.get('eigenschaften', {})
        if hasattr(self.ids, 'schaden_input'):
            self.ids.schaden_input.text = eigenschaften.get('Schaden', '')
        
        if hasattr(self.ids, 'reichweite_input'):
            self.ids.reichweite_input.text = eigenschaften.get('Reichweite', '')
        
        if hasattr(self.ids, 'fr_input'):
            self.ids.fr_input.text = eigenschaften.get('FR', '')
        
        if hasattr(self.ids, 'schuss_input'):
            self.ids.schuss_input.text = eigenschaften.get('Schuss', '')
        
        if hasattr(self.ids, 'pb_input'):
            self.ids.pb_input.text = eigenschaften.get('PB', '')

    def select_typ(self, typ):
        """Wählt den Waffentyp aus und aktualisiert die Button-Zustände"""
        if hasattr(self.ids, 'nahkampf_button') and hasattr(self.ids, 'fernkampf_button'):
            self.ids.nahkampf_button.selected = (typ == 'Nahkampf')
            self.ids.fernkampf_button.selected = (typ == 'Fernkampf')
            self._selected_typ = typ  # Speichern des ausgewählten Typs

    def get_selected_typ(self):
        """Gibt den aktuell ausgewählten Waffentyp zurück"""
        return getattr(self, '_selected_typ', 'Nahkampf')  # Standard ist Nahkampf


class DeleteWaffeDialogContent(MDBoxLayout):
    def __init__(self, waffen_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.waffen_callback = waffen_callback
        self.menu_callback = menu_callback
        self.dialog = None
        
    def open_menu(self, instance_item):
        if not self.waffen_callback:
            return
            
        waffen = self.waffen_callback()
        if not waffen:
            return
            
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in waffen
        ]
        
        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()
        
    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'waffe_dropdown'):
            self.ids.waffe_dropdown.text = text_item

class WaffeDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.dialog = None
        self.selected_waffe = None
        self.dialog_content = None

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen einer neuen Waffe"""
        dialog_content = WaffeDialogContent()
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Neue Waffe hinzufügen",
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
                    on_release=self.save_waffe,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def show_delete_dialog(self):
        """Zeigt den Dialog zum Löschen einer Waffe"""
        if not self.get_all_waffen():
            self.show_error("Keine Waffen zum Löschen verfügbar.")
            return

        dialog_content = DeleteWaffeDialogContent(
            waffen_callback=self.get_all_waffen,
            menu_callback=self.on_waffe_select
        )
        dialog_content.dialog = self.dialog
        self.dialog_content = dialog_content
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Waffe löschen",
            ),
            MDDialogSupportingText(
                text="Wähle eine Waffe zum Löschen:",
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
                    on_release=self.delete_waffe,
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def show_edit_dialog(self, waffe_name):
            """Zeigt den Dialog zum Bearbeiten einer bestehenden Waffe"""
            try:
                app = App.get_running_app()
                charakter = app.controller.charakter
                
                # Hole die Waffe
                waffe = charakter.ausruestung.get(waffe_name)
                if not waffe:
                    self.show_error(f"Waffe '{waffe_name}' nicht gefunden.")
                    return
                
                # Erstelle Dialog-Content mit Waffen-Daten
                waffe_data = {
                    'name': waffe.name,
                    'typ': waffe.typ,
                    'mindeststaerke': waffe.mindeststaerke,
                    'gewicht': waffe.gewicht,
                    'kosten': waffe.kosten,
                    'setting': waffe.setting,
                    'beschreibung': waffe.beschreibung,
                    'eigenschaften': waffe.eigenschaften
                }
                
                dialog_content = WaffeDialogContent(waffe_data=waffe_data)
                dialog_content.dialog = self.dialog
                self.dialog_content = dialog_content
                self.selected_waffe = waffe_name  # Speichere den Key für Updates
                
                self.dialog = MDDialog(
                    MDDialogHeadlineText(
                        text="Waffe bearbeiten",
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
                            on_release=self.update_waffe,
                        ),
                        spacing="8dp",
                    ),
                )
                self.dialog.open()
                
            except Exception as e:
                Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
                self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def update_waffe(self, *args):
        """Aktualisiert eine bestehende Waffe"""
        if not self.dialog_content or not self.selected_waffe:
            Logger.error("Dialog-Content oder ausgewählte Waffe nicht gefunden")
            return
            
        # Grunddaten sammeln
        name = self.dialog_content.ids.name_input.text.strip()
        typ = self.dialog_content.get_selected_typ()
        mindeststaerke = self.dialog_content.ids.mindeststaerke_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()
        
        # Waffeneigenschaften sammeln
        schaden = self.dialog_content.ids.schaden_input.text.strip()
        reichweite = self.dialog_content.ids.reichweite_input.text.strip()
        fr = self.dialog_content.ids.fr_input.text.strip()
        schuss = self.dialog_content.ids.schuss_input.text.strip()
        pb = self.dialog_content.ids.pb_input.text.strip()

        # Validierungen
        if not name:
            self.show_error("Der Name der Waffe darf nicht leer sein.")
            return
            
        if typ not in ['Nahkampf', 'Fernkampf']:
            self.show_error("Bitte wählen Sie einen gültigen Typ (Nahkampf/Fernkampf).")
            return
            
        if mindeststaerke not in ['W4', 'W6', 'W8', 'W10', 'W12', '-']:
            self.show_error("Mindeststärke muss 'W4', 'W6', 'W8', 'W10', 'W12' oder '-' sein.")
            return

        try:
            gewicht = float(gewicht_text)
            kosten = float(kosten_text)
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für Gewicht und Kosten ein.")
            return

        # Eigenschaften Dictionary erstellen
        eigenschaften = {
            'Schaden': schaden if schaden else '-',
            'Reichweite': reichweite if reichweite else '-',
            'FR': fr if fr else '-',
            'Schuss': schuss if schuss else '-',
            'PB': pb if pb else '-'
        }

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            # Hole die bestehende Waffe
            waffe = charakter.ausruestung.get(self.selected_waffe)
            if not waffe:
                self.show_error(f"Waffe '{self.selected_waffe}' nicht mehr gefunden.")
                return
            
            # Wenn der Name geändert wurde und bereits existiert
            if name != waffe.name and name in charakter.ausruestung:
                self.show_error(f"Waffe mit dem Namen '{name}' existiert bereits.")
                return
            
            # Aktualisiere die Waffe
            old_name = waffe.name
            waffe.name = name
            waffe.typ = typ
            waffe.mindeststaerke = mindeststaerke
            waffe.gewicht = gewicht
            waffe.kosten = kosten
            waffe.setting = setting
            waffe.beschreibung = beschreibung
            waffe.eigenschaften = eigenschaften
            
            # Bei Namensänderung: Key im Dictionary ändern
            if name != old_name:
                # Neuen Key erstellen
                charakter.ausruestung[name] = waffe
                if old_name in charakter.ausruestung:
                    del charakter.ausruestung[old_name]
            
            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            
            self.dismiss_dialog()
            Logger.info(f"Waffe '{name}' wurde aktualisiert.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Waffe: {e}")
            self.show_error("Fehler beim Aktualisieren der Waffe")

    def save_waffe(self, *args):
        """Speichert eine neue Waffe"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return
            
        # Grunddaten sammeln
        name = self.dialog_content.ids.name_input.text.strip()
        typ = self.dialog_content.get_selected_typ()
        mindeststaerke = self.dialog_content.ids.mindeststaerke_input.text.strip()
        gewicht_text = self.dialog_content.ids.gewicht_input.text.strip()
        kosten_text = self.dialog_content.ids.kosten_input.text.strip()
        setting = self.dialog_content.ids.setting_input.text.strip()
        beschreibung = self.dialog_content.ids.beschreibung_input.text.strip()
        
        # Waffeneigenschaften sammeln
        schaden = self.dialog_content.ids.schaden_input.text.strip()
        reichweite = self.dialog_content.ids.reichweite_input.text.strip()
        fr = self.dialog_content.ids.fr_input.text.strip()
        schuss = self.dialog_content.ids.schuss_input.text.strip()
        pb = self.dialog_content.ids.pb_input.text.strip()

        # Validierungen
        if not name:
            self.show_error("Der Name der Waffe darf nicht leer sein.")
            return
            
        if typ not in ['Nahkampf', 'Fernkampf']:
            self.show_error("Bitte wählen Sie einen gültigen Typ (Nahkampf/Fernkampf).")
            return
            
        if mindeststaerke not in ['W4', 'W6', 'W8', 'W10', 'W12', '-']:
            self.show_error("Mindeststärke muss 'W4', 'W6', 'W8', 'W10', 'W12' oder '-' sein.")
            return

        try:
            gewicht = float(gewicht_text)
            kosten = float(kosten_text)
        except ValueError:
            self.show_error("Bitte geben Sie gültige Zahlen für Gewicht und Kosten ein.")
            return

        # Eigenschaften Dictionary erstellen
        eigenschaften = {
            'Schaden': schaden if schaden else '-',
            'Reichweite': reichweite if reichweite else '-',
            'FR': fr if fr else '-',
            'Schuss': schuss if schuss else '-',
            'PB': pb if pb else '-'
        }

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            if name in charakter.ausruestung:
                self.show_error(f"Waffe '{name}' existiert bereits.")
                return

            new_waffe = Waffe(
                name=name,
                gewicht=gewicht,
                kosten=kosten,
                setting=setting,
                typ=typ,
                mindeststaerke=mindeststaerke,
                beschreibung=beschreibung,
                eigenschaften=eigenschaften,
                menge=0,
                ausgewaehlt=True,
                aktiv=True,
                angelegt=False,
                kategorie='Waffe',
                custom=True
            )
            
            success = charakter.add_ausruestung(new_waffe)
            
            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()
                
                self.dismiss_dialog()
                Logger.info(f"Waffe '{name}' wurde hinzugefügt.")
            else:
                self.show_error(f"Waffe '{name}' konnte nicht hinzugefügt werden.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der Waffe: {e}")
            self.show_error("Fehler beim Speichern der Waffe")

    def delete_waffe(self, *args):
        """Löscht die ausgewählte Waffe"""
        try:
            if not self.selected_waffe:
                self.show_error("Bitte wähle eine Waffe zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter
            
            waffe_name = self.selected_waffe
            success = charakter.remove_ausruestung(waffe_name)

            if success:
                if hasattr(app, 'einstellungen_widget'):
                    app.einstellungen_widget.aktualisiere_ui()
                
                Logger.info(f"Waffe '{waffe_name}' wurde gelöscht.")
                self.dismiss_dialog()
            else:
                self.show_error(f"Waffe '{waffe_name}' konnte nicht gelöscht werden.")
                
        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Waffe: {e}")
            self.show_error("Fehler beim Löschen der Waffe")

    def on_waffe_select(self, waffe_name):
        """Callback wenn eine Waffe im Dropdown ausgewählt wurde"""
        self.selected_waffe = waffe_name
        if (self.dialog_content and 
            hasattr(self.dialog_content.ids, 'selected_waffe_text')):
            self.dialog_content.ids.selected_waffe_text.text = waffe_name
            Logger.info(f"Waffe '{waffe_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            self.dialog_content = None
            self.selected_waffe = None

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

    def get_all_waffen(self):
        """Gibt eine Liste aller verfügbaren Waffen zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return [name for name, item in charakter.ausruestung.items() if isinstance(item, Waffe)]
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Waffe: {e}")
        return []