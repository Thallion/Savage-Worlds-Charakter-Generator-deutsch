# schild-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
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
from views.popup_basis import BasisDialogHandler

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

class SchildDialogHandler(BasisDialogHandler):
    element_name = "Schild"
    element_name_plural = "Schilde"
    artikel_unbestimmt = "ein"

    def __init__(self, controller):
        super().__init__(controller)
        self.selected_schild = None

    def _get_loeschbare_elemente(self):
        return self.get_all_schilde()

    def _reset_selection(self):
        self.selected_schild = None

    def show_add_dialog(self):
        """Zeigt das Overlay zum Hinzufügen eines neuen Schildes"""
        dialog_content = SchildDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neues Schild hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_schild,
        )

    def _confirm_delete_elemente(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch"""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            for schild_name in selected:
                success = charakter.remove_ausruestung(schild_name)
                if success:
                    Logger.info(f"Schild '{schild_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Schild '{schild_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_ausruestung_view()
            self._show_success_snackbar(f"{len(selected)} Schild(er) gelöscht")

            Logger.info(f"{len(selected)} Schild(er) wurde(n) gelöscht.")

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Schilde: {e}")
            self.show_error("Fehler beim Löschen der Schilde")

    def show_edit_dialog(self, schild_name):
        """Zeigt das Overlay zum Bearbeiten eines bestehenden Schildes"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            schild = charakter.ausruestung.get(schild_name)
            if not schild:
                self.show_error(f"Schild '{schild_name}' nicht gefunden.")
                return

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
            self.dialog_content = dialog_content
            self.selected_schild = schild_name

            overlay = self._get_overlay()
            overlay.open(
                title="Schild bearbeiten",
                content_widget=dialog_content,
                action_text="Speichern",
                on_action=self.update_schild,
            )

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


    def on_schild_select(self, schild_name):
        """Callback wenn ein Schild ausgewählt wurde"""
        self.selected_schild = schild_name

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

    def _refresh_ausruestung_view(self):
        """Aktualisiert das Ausrüstung-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Ausrüstung', 'ausruestung_widget')
                if widget and hasattr(widget, 'refresh'):
                    widget.refresh()
                elif widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
        except Exception as e:
            Logger.warning(f"Ausrüstung-Widget nicht gefunden: {e}")
