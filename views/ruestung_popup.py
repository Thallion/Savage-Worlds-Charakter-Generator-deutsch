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
        self.overlay = None
        self.selected_ruestung = None
        self.dialog_content = None

    def _get_overlay(self):
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt das Overlay zum Hinzufügen einer neuen Rüstung"""
        dialog_content = RuestungDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neue Rüstung hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_ruestung,
        )

    def show_delete_dialog(self):
        """Zeigt das Overlay zum Löschen einer Rüstung (suchbare Liste)"""
        ruestungen = self.get_all_ruestungen()
        if not ruestungen:
            self.show_error("Keine Rüstungen zum Löschen verfügbar.")
            return

        from views.element_overlay import ElementListContent
        content = ElementListContent(
            items=ruestungen,
            on_select=self.on_ruestung_select,
        )
        self.dialog_content = content

        overlay = self._get_overlay()
        overlay.open(
            title="Rüstung löschen",
            content_widget=content,
            action_text="Löschen",
            on_action=self.delete_ruestung,
        )

    def show_edit_dialog(self, ruestung_name):
        """Zeigt das Overlay zum Bearbeiten einer bestehenden Rüstung"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            ruestung = charakter.ausruestung.get(ruestung_name)
            if not ruestung:
                self.show_error(f"Rüstung '{ruestung_name}' nicht gefunden.")
                return

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
            self.dialog_content = dialog_content
            self.selected_ruestung = ruestung_name

            overlay = self._get_overlay()
            overlay.open(
                title="Rüstung bearbeiten",
                content_widget=dialog_content,
                action_text="Speichern",
                on_action=self.update_ruestung,
            )

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
        """Callback wenn eine Rüstung ausgewählt wurde"""
        self.selected_ruestung = ruestung_name

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_ruestung = None

    def show_error(self, message):
        """Zeigt eine Fehlermeldung an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_warning_dialog(message)
                return
        except Exception:
            pass
        Logger.error(f"Rüstung-Fehler: {message}")

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