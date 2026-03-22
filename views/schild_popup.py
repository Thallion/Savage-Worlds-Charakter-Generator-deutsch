# schild-popup.py
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

from models.schild import Schild

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
        kv_path = os.path.join(base_path, 'views', 'schild_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'schild_popup.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"schild_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

# SchildDialogContent
class SchildDialogContent(MDBoxLayout):
    def __init__(self, schild_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_mode = False
        self.original_name = None
        
        # Wenn Schild-Daten übergeben wurden, befülle die Felder
        if schild_data:
            self.edit_mode = True
            self.original_name = schild_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(schild_data), 0.1)
    
    def _fill_fields(self, schild_data):
        """Befüllt die Felder mit den Schild-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = schild_data.get('name', '')
        
        if hasattr(self.ids, 'parade_input'):
            self.ids.parade_input.text = str(schild_data.get('parade', 0))
        
        if hasattr(self.ids, 'deckung_input'):
            self.ids.deckung_input.text = str(schild_data.get('deckung', 0))
        
        if hasattr(self.ids, 'mindeststaerke_input'):
            self.ids.mindeststaerke_input.text = schild_data.get('mindeststaerke', '')
        
        if hasattr(self.ids, 'gewicht_input'):
            self.ids.gewicht_input.text = str(schild_data.get('gewicht', 0))
        
        if hasattr(self.ids, 'kosten_input'):
            self.ids.kosten_input.text = str(schild_data.get('kosten', 0))
        
        if hasattr(self.ids, 'setting_input'):
            self.ids.setting_input.text = schild_data.get('setting', '')
        
        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = schild_data.get('beschreibung', '')

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
            size_hint=(0.85, None),
            auto_dismiss=False,
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
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self.dialog.open()

    def show_edit_dialog(self, schild_name):
            """Zeigt den Dialog zum Bearbeiten eines bestehenden Schildes"""
            try:
                app = App.get_running_app()
                charakter = app.controller.charakter
                
                # Hole das Schild
                schild = charakter.ausruestung.get(schild_name)
                if not schild:
                    self.show_error(f"Schild '{schild_name}' nicht gefunden.")
                    return
                
                # Erstelle Dialog-Content mit Schild-Daten
                schild_data = {
                    'name': schild.name,
                    'parade': schild.parade,
                    'deckung': schild.deckung,
                    'mindeststaerke': schild.mindeststaerke,
                    'gewicht': schild.gewicht,
                    'kosten': schild.kosten,
                    'setting': schild.setting,
                    'beschreibung': schild.beschreibung
                }
                
                dialog_content = SchildDialogContent(schild_data=schild_data)
                dialog_content.dialog = self.dialog
                self.dialog_content = dialog_content
                self.selected_schild = schild_name  # Speichere den Key für Updates
                
                self.dialog = MDDialog(
                    MDDialogHeadlineText(
                        text="Schild bearbeiten",
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
                            on_release=self.update_schild,
                        ),
                        spacing="8dp",
                    ),
                    size_hint=(0.85, None),
                    auto_dismiss=False,
                )
                self.dialog.open()
                
            except Exception as e:
                Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
                self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def update_schild(self, *args):
        """Aktualisiert ein bestehendes Schild"""
        if not self.dialog_content or not self.selected_schild:
            Logger.error("Dialog-Content oder ausgewähltes Schild nicht gefunden")
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
            
            # Hole das bestehende Schild
            schild = charakter.ausruestung.get(self.selected_schild)
            if not schild:
                self.show_error(f"Schild '{self.selected_schild}' nicht mehr gefunden.")
                return
            
            # Wenn der Name geändert wurde und bereits existiert
            if name != schild.name and name in charakter.ausruestung:
                self.show_error(f"Schild mit dem Namen '{name}' existiert bereits.")
                return
            
            # Aktualisiere das Schild
            old_name = schild.name
            schild.name = name
            schild.parade = parade
            schild.deckung = deckung
            schild.mindeststaerke = mindeststaerke
            schild.gewicht = gewicht
            schild.kosten = kosten
            schild.setting = setting
            schild.beschreibung = beschreibung
            
            # Bei Namensänderung: Key im Dictionary ändern
            if name != old_name:
                # Neuen Key erstellen
                charakter.ausruestung[name] = schild
                if old_name in charakter.ausruestung:
                    del charakter.ausruestung[old_name]
            
            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            
            self.dismiss_dialog()
            Logger.info(f"Schild '{name}' wurde aktualisiert.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Schilds: {e}")
            self.show_error("Fehler beim Aktualisieren des Schilds")

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
            size_hint=(0.85, None),
            auto_dismiss=False,
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