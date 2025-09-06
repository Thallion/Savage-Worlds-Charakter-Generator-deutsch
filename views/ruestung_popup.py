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

from models.ruestung import Ruestung

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
import os
import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'ruestung_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'ruestung_popup.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"ruestung_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

# RuestungDialogContent
class RuestungDialogContent(MDBoxLayout):
    def __init__(self, ruestung_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_mode = False
        self.original_name = None
        
        # Wenn Rüstungs-Daten übergeben wurden, befülle die Felder
        if ruestung_data:
            self.edit_mode = True
            self.original_name = ruestung_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(ruestung_data), 0.1)
    
    def _fill_fields(self, ruestung_data):
        """Befüllt die Felder mit den Rüstungs-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = ruestung_data.get('name', '')
        
        if hasattr(self.ids, 'torso_input'):
            self.ids.torso_input.text = str(ruestung_data.get('torso', 0))
        
        if hasattr(self.ids, 'arme_input'):
            self.ids.arme_input.text = str(ruestung_data.get('arme', 0))
        
        if hasattr(self.ids, 'beine_input'):
            self.ids.beine_input.text = str(ruestung_data.get('beine', 0))
        
        if hasattr(self.ids, 'kopf_input'):
            self.ids.kopf_input.text = str(ruestung_data.get('kopf', 0))
        
        if hasattr(self.ids, 'mindeststaerke_input'):
            self.ids.mindeststaerke_input.text = ruestung_data.get('mindeststaerke', '')
        
        if hasattr(self.ids, 'gewicht_input'):
            self.ids.gewicht_input.text = str(ruestung_data.get('gewicht', 0))
        
        if hasattr(self.ids, 'kosten_input'):
            self.ids.kosten_input.text = str(ruestung_data.get('kosten', 0))
        
        if hasattr(self.ids, 'setting_input'):
            self.ids.setting_input.text = ruestung_data.get('setting', '')
        
        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = ruestung_data.get('beschreibung', '')

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

    def show_edit_dialog(self, ruestung_name):
            """Zeigt den Dialog zum Bearbeiten einer bestehenden Rüstung"""
            try:
                app = App.get_running_app()
                charakter = app.controller.charakter
                
                # Hole die Rüstung
                ruestung = charakter.ausruestung.get(ruestung_name)
                if not ruestung:
                    self.show_error(f"Rüstung '{ruestung_name}' nicht gefunden.")
                    return
                
                # Erstelle Dialog-Content mit Rüstungs-Daten
                ruestung_data = {
                    'name': ruestung.name,
                    'torso': ruestung.torso,
                    'arme': ruestung.arme,
                    'beine': ruestung.beine,
                    'kopf': ruestung.kopf,
                    'mindeststaerke': ruestung.mindeststaerke,
                    'gewicht': ruestung.gewicht,
                    'kosten': ruestung.kosten,
                    'setting': ruestung.setting,
                    'beschreibung': ruestung.beschreibung
                }
                
                dialog_content = RuestungDialogContent(ruestung_data=ruestung_data)
                dialog_content.dialog = self.dialog
                self.dialog_content = dialog_content
                self.selected_ruestung = ruestung_name  # Speichere den Key für Updates
                
                self.dialog = MDDialog(
                    MDDialogHeadlineText(
                        text="Rüstung bearbeiten",
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
                            on_release=self.update_ruestung,
                        ),
                        spacing="8dp",
                    ),
                )
                self.dialog.open()
                
            except Exception as e:
                Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
                self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def update_ruestung(self, *args):
        """Aktualisiert eine bestehende Rüstung"""
        if not self.dialog_content or not self.selected_ruestung:
            Logger.error("Dialog-Content oder ausgewählte Rüstung nicht gefunden")
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
            
            # Hole die bestehende Rüstung
            ruestung = charakter.ausruestung.get(self.selected_ruestung)
            if not ruestung:
                self.show_error(f"Rüstung '{self.selected_ruestung}' nicht mehr gefunden.")
                return
            
            # Wenn der Name geändert wurde und bereits existiert
            if name != ruestung.name and name in charakter.ausruestung:
                self.show_error(f"Rüstung mit dem Namen '{name}' existiert bereits.")
                return
            
            # Aktualisiere die Rüstung
            old_name = ruestung.name
            ruestung.name = name
            ruestung.torso = torso
            ruestung.arme = arme
            ruestung.beine = beine
            ruestung.kopf = kopf
            ruestung.mindeststaerke = mindeststaerke
            ruestung.gewicht = gewicht
            ruestung.kosten = kosten
            ruestung.setting = setting
            ruestung.beschreibung = beschreibung
            
            # Bei Namensänderung: Key im Dictionary ändern
            if name != old_name:
                # Neuen Key erstellen
                charakter.ausruestung[name] = ruestung
                if old_name in charakter.ausruestung:
                    del charakter.ausruestung[old_name]
            
            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            
            self.dismiss_dialog()
            Logger.info(f"Rüstung '{name}' wurde aktualisiert.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Rüstung: {e}")
            self.show_error("Fehler beim Aktualisieren der Rüstung")

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