# talent-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.clock import Clock
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

import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'talent_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'talent_popup.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"talent_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class TalentDialogContent(MDBoxLayout):
    def __init__(self, talent_data=None, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.edit_mode = False
        self.original_name = None
        
        # Wenn Talent-Daten übergeben wurden, befülle die Felder
        if talent_data:
            self.edit_mode = True
            self.original_name = talent_data.get('name', '')
            Clock.schedule_once(lambda dt: self._fill_fields(talent_data), 0.1)
    
    def _fill_fields(self, talent_data):
        """Befüllt die Felder mit den Talent-Daten beim Bearbeiten"""
        if hasattr(self.ids, 'name_input'):
            self.ids.name_input.text = talent_data.get('name', '')
        
        if hasattr(self.ids, 'kategorie_input'):
            self.ids.kategorie_input.text = talent_data.get('kategorie', '')
        
        if hasattr(self.ids, 'rang_input'):
            self.ids.rang_input.text = talent_data.get('rang', '')
        
        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = talent_data.get('beschreibung', '')
        
        if hasattr(self.ids, 'voraussetzungen_input'):
            voraussetzungen = talent_data.get('voraussetzungen', [])
            if isinstance(voraussetzungen, list):
                self.ids.voraussetzungen_input.text = ', '.join(voraussetzungen)
            else:
                self.ids.voraussetzungen_input.text = str(voraussetzungen)
        
        if hasattr(self.ids, 'neue_maechte_input'):
            self.ids.neue_maechte_input.text = str(talent_data.get('neue_maechte', 0))
        
        if hasattr(self.ids, 'machtpunkte_input'):
            self.ids.machtpunkte_input.text = str(talent_data.get('machtpunkte', 0))
        
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

    def add_talent(self, talent_daten):
        """
        Fügt ein neues Talent auf Basis der übergebenen Daten hinzu.
        
        Args:
            talent_daten (dict): Die Talentdaten aus dem Dialog
        
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            voraussetzungen = []
            # Voraussetzungen verarbeiten
            if talent_daten.get('voraussetzungen_text'):
                voraussetzungen_text = talent_daten['voraussetzungen_text']
                # Voraussetzungen an Kommas trennen
                voraussetzungen = [voraussetzung.strip() for voraussetzung in voraussetzungen_text.split(',') if voraussetzung.strip()]
            
            # Neues Talent erstellen
            talent = Talent(
                name=talent_daten['name'],
                kategorie=talent_daten['kategorie'],
                rang=talent_daten['rang'],
                voraussetzungen=voraussetzungen,
                beschreibung=talent_daten.get('beschreibung', ''),
                neue_maechte=int(talent_daten.get('neue_maechte', 0)),
                machtpunkte=int(talent_daten.get('machtpunkte', 0)),
                custom=True  # Als benutzerdefiniert markieren
            )
            
            success = self.controller.charakter.add_talent(talent)
            if success:
                Logger.info(f"Talent '{talent.name}' erfolgreich hinzugefügt.")
                return True
            else:
                Logger.warning(f"Talent '{talent.name}' konnte nicht hinzugefügt werden.")
                return False
        except Exception as e:
            Logger.error(f"Fehler beim Hinzufügen des Talents: {e}")
            return False

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
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self.dialog.open()

    def show_edit_dialog(self, talent_name_key):
        """Zeigt den Dialog zum Bearbeiten eines bestehenden Talents"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            # Hole das Talent
            talent = charakter.talente.get(talent_name_key)
            if not talent:
                self.show_error(f"Talent '{talent_name_key}' nicht gefunden.")
                return
            
            # Erstelle Dialog-Content mit Talent-Daten
            talent_data = {
                'name': talent.name,
                'kategorie': talent.kategorie,
                'rang': talent.rang,
                'beschreibung': talent.beschreibung,
                'voraussetzungen': talent.voraussetzungen,
                'neue_maechte': talent.neue_maechte,
                'machtpunkte': talent.machtpunkte
            }
            
            dialog_content = TalentDialogContent(talent_data=talent_data)
            dialog_content.dialog = self.dialog
            self.dialog_content = dialog_content
            self.selected_talent = talent_name_key  # Speichere den Key für Updates
            
            self.dialog = MDDialog(
                MDDialogHeadlineText(
                    text="Talent bearbeiten",
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
                        on_release=self.update_talent,
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

    def update_talent(self, *args):
        """Aktualisiert ein bestehendes Talent"""
        if not self.dialog_content or not self.selected_talent:
            Logger.error("Dialog-Content oder ausgewähltes Talent nicht gefunden")
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
            
            # Hole das bestehende Talent
            talent = charakter.talente.get(self.selected_talent)
            if not talent:
                self.show_error(f"Talent '{self.selected_talent}' nicht mehr gefunden.")
                return
            
            # Wenn der Name geändert wurde und bereits existiert
            if name != talent.name and name in charakter.talente:
                self.show_error(f"Ein Talent mit dem Namen '{name}' existiert bereits.")
                return
            
            # Aktualisiere das Talent
            old_name = talent.name
            talent.name = name
            talent.kategorie = kategorie
            talent.rang = rang
            talent.beschreibung = beschreibung
            talent.voraussetzungen = voraussetzungen
            talent.neue_maechte = int(neue_maechte_text) if neue_maechte_text else 0
            talent.machtpunkte = int(machtpunkte_text) if machtpunkte_text else 0
            
            # Bei Namensänderung: Key im Dictionary ändern
            if name != old_name:
                # Neuen Key erstellen
                new_key = name
                old_key = self.selected_talent
                
                # Talent unter neuem Key speichern und alten löschen
                charakter.talente[new_key] = talent
                if old_key != new_key and old_key in charakter.talente:
                    del charakter.talente[old_key]
                    
                    # Auch in selected_talente aktualisieren
                    if old_key in charakter.selected_talente:
                        idx = charakter.selected_talente.index(old_key)
                        charakter.selected_talente[idx] = new_key
            
            # Speichere die Custom Talente
            charakter.save_custom_talents()
            
            # Aktualisiere die UI
            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            
            self.dismiss_dialog()
            Logger.info(f"Talent '{name}' wurde aktualisiert.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Talents: {e}")
            self.show_error("Fehler beim Aktualisieren des Talents")

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
            size_hint=(0.85, None),
            auto_dismiss=False,
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
            size_hint=(0.85, None),
            auto_dismiss=False,
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