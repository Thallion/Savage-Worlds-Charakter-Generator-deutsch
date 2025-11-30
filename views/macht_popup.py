# macht-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.clock import Clock
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

import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'macht_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'macht_popup.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"macht_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class MachtDialogContent(MDBoxLayout):
    def __init__(self, macht_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_mode = False
        self.original_name = None
        
        # Wenn Macht-Daten übergeben wurden, befülle die Felder
        if macht_data:
            self.edit_mode = True
            self.original_name = macht_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(macht_data), 0.1)
    
    def _fill_fields(self, macht_data):
        """Befüllt die Felder mit den Macht-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = macht_data.get('name', '')
        
        if hasattr(self.ids, 'rang_input'):
            self.ids.rang_input.text = macht_data.get('rang', '')
        
        if hasattr(self.ids, 'machtpunkte_input'):
            self.ids.machtpunkte_input.text = str(macht_data.get('machtpunkte', 0))
        
        if hasattr(self.ids, 'reichweite_input'):
            self.ids.reichweite_input.text = macht_data.get('reichweite', '')
        
        if hasattr(self.ids, 'dauer_input'):
            self.ids.dauer_input.text = macht_data.get('dauer', '')
        
        if hasattr(self.ids, 'effekt_input'):
            self.ids.effekt_input.text = macht_data.get('effekt', '')
        
        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = macht_data.get('beschreibung', '')
        
        if hasattr(self.ids, 'voraussetzungen_input'):
            voraussetzungen = macht_data.get('voraussetzungen', [])
            if isinstance(voraussetzungen, list):
                self.ids.voraussetzungen_input.text = ', '.join(voraussetzungen)
            else:
                self.ids.voraussetzungen_input.text = str(voraussetzungen)
        
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

    def show_edit_dialog(self, macht_name_key):
        """Zeigt den Dialog zum Bearbeiten einer bestehenden Macht"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            # Hole die Macht
            macht = charakter.maechte.get(macht_name_key)
            if not macht:
                self.show_error(f"Macht '{macht_name_key}' nicht gefunden.")
                return
            
            # Erstelle Dialog-Content mit Macht-Daten
            macht_data = {
                'name': macht.name,
                'rang': macht.rang,
                'machtpunkte': macht.machtpunkte,
                'reichweite': macht.reichweite,
                'dauer': macht.dauer,
                'effekt': macht.effekt,
                'beschreibung': macht.beschreibung,
                'voraussetzungen': macht.voraussetzungen
            }
            
            dialog_content = MachtDialogContent(macht_data=macht_data)
            dialog_content.dialog = self.dialog
            self.dialog_content = dialog_content
            self.selected_macht = macht_name_key  # Speichere den Key für Updates
            
            self.dialog = MDDialog(
                MDDialogHeadlineText(
                    text="Macht bearbeiten",
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
                        on_release=self.update_macht,
                    ),
                    spacing="8dp",
                ),
            )
            self.dialog.open()
            
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Bearbeitungsdialogs: {e}")
            self.show_error("Fehler beim Öffnen des Bearbeitungsdialogs")

    def update_macht(self, *args):
        """Aktualisiert eine bestehende Macht"""
        if not self.dialog_content or not self.selected_macht:
            Logger.error("Dialog-Content oder ausgewählte Macht nicht gefunden")
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
            
            # Hole die bestehende Macht
            macht = charakter.maechte.get(self.selected_macht)
            if not macht:
                self.show_error(f"Macht '{self.selected_macht}' nicht mehr gefunden.")
                return
            
            # Wenn der Name geändert wurde und bereits existiert
            if name != macht.name and name in charakter.maechte:
                self.show_error(f"Eine Macht mit dem Namen '{name}' existiert bereits.")
                return
            
            # Aktualisiere die Macht
            old_name = macht.name
            macht.name = name
            macht.rang = rang
            macht.machtpunkte = int(machtpunkte_text)
            macht.reichweite = reichweite
            macht.dauer = dauer
            macht.effekt = effekt
            macht.beschreibung = beschreibung
            macht.voraussetzungen = voraussetzungen
            
            # Bei Namensänderung: Key im Dictionary ändern
            if name != old_name:
                # Neuen Key erstellen
                new_key = name
                old_key = self.selected_macht
                
                # Macht unter neuem Key speichern und alten löschen
                charakter.maechte[new_key] = macht
                if old_key != new_key and old_key in charakter.maechte:
                    del charakter.maechte[old_key]
                    
                    # Auch in selected_maechte aktualisieren
                    if old_key in charakter.selected_maechte:
                        idx = charakter.selected_maechte.index(old_key)
                        charakter.selected_maechte[idx] = new_key
            
            # Speichere die Custom Mächte
            charakter.save_custom_maechte()
            
            # Aktualisiere die UI
            maechte_widget = app.get_widget_by_tab_text('Mächte', 'maechte_widget')
            if maechte_widget and hasattr(maechte_widget, 'refresh_widget'):
                maechte_widget.refresh_widget()
            
            self.dismiss_dialog()
            Logger.info(f"Macht '{name}' wurde aktualisiert.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren der Macht: {e}")
            self.show_error("Fehler beim Aktualisieren der Macht")

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
                # Aktualisiere die UI
                maechte_widget = app.get_widget_by_tab_text('Mächte', 'maechte_widget')
                if maechte_widget and hasattr(maechte_widget, 'refresh_widget'):
                    maechte_widget.refresh_widget()
                
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
                # Aktualisiere die UI
                maechte_widget = app.get_widget_by_tab_text('Mächte', 'maechte_widget')
                if maechte_widget and hasattr(maechte_widget, 'refresh_widget'):
                    maechte_widget.refresh_widget()
                
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