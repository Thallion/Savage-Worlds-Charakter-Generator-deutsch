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

from models.waffe import Waffe

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
        kv_path = os.path.join(base_path, 'views', 'waffe_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'waffe_popup.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"waffe_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

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
            self.ids.name_input.text = str(waffe_data.get('name', ''))
        
        if hasattr(self.ids, 'typ_segment'):
            self.select_typ(waffe_data.get('typ', 'Nahkampf'))
        
        if hasattr(self.ids, 'mindeststaerke_input'):
            self.ids.mindeststaerke_input.text = str(waffe_data.get('mindeststaerke', ''))
        
        if hasattr(self.ids, 'gewicht_input'):
            self.ids.gewicht_input.text = str(waffe_data.get('gewicht', 0))
        
        if hasattr(self.ids, 'kosten_input'):
            self.ids.kosten_input.text = str(waffe_data.get('kosten', 0))
        
        if hasattr(self.ids, 'setting_input'):
            self.ids.setting_input.text = str(waffe_data.get('setting', ''))
        
        if hasattr(self.ids, 'beschreibung_input'):
            self.ids.beschreibung_input.text = str(waffe_data.get('beschreibung', ''))
        
        # Eigenschaften - Explizite String-Konvertierung für alle Werte
        eigenschaften = waffe_data.get('eigenschaften', {})
        if hasattr(self.ids, 'schaden_input'):
            schaden_wert = eigenschaften.get('Schaden', '')
            self.ids.schaden_input.text = str(schaden_wert) if schaden_wert is not None else ''
        
        if hasattr(self.ids, 'reichweite_input'):
            reichweite_wert = eigenschaften.get('Reichweite', '')
            self.ids.reichweite_input.text = str(reichweite_wert) if reichweite_wert is not None else ''
        
        if hasattr(self.ids, 'fr_input'):
            fr_wert = eigenschaften.get('FR', '')
            self.ids.fr_input.text = str(fr_wert) if fr_wert is not None else ''
        
        if hasattr(self.ids, 'schuss_input'):
            schuss_wert = eigenschaften.get('Schuss', '')
            self.ids.schuss_input.text = str(schuss_wert) if schuss_wert is not None else ''
        
        if hasattr(self.ids, 'pb_input'):
            pb_wert = eigenschaften.get('PB', '')
            self.ids.pb_input.text = str(pb_wert) if pb_wert is not None else ''

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
        self.overlay = None
        self.selected_waffe = None
        self.dialog_content = None

    def _get_overlay(self):
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt das Overlay zum Hinzufügen einer neuen Waffe"""
        dialog_content = WaffeDialogContent()
        self.dialog_content = dialog_content

        overlay = self._get_overlay()
        overlay.open(
            title="Neue Waffe hinzufügen",
            content_widget=dialog_content,
            action_text="Speichern",
            on_action=self.save_waffe,
        )

    def show_delete_dialog(self):
        """Zeigt das Overlay zum Löschen von Waffen (suchbare Liste mit Mehrfachauswahl)"""
        waffen = self.get_all_waffen()
        if not waffen:
            self.show_error("Keine Waffen zum Löschen verfügbar.")
            return

        from views.element_overlay import ElementListContent
        content = ElementListContent(
            items=waffen,
            multi_select=True,
        )
        self.dialog_content = content

        overlay = self._get_overlay()
        overlay.open(
            title="Waffe löschen",
            content_widget=content,
            action_text="Löschen",
            on_action=self.delete_waffe,
        )

    def show_edit_dialog(self, waffe_name):
        """Zeigt das Overlay zum Bearbeiten einer bestehenden Waffe"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            waffe = charakter.ausruestung.get(waffe_name)
            if not waffe:
                self.show_error(f"Waffe '{waffe_name}' nicht gefunden.")
                return

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
            self.dialog_content = dialog_content
            self.selected_waffe = waffe_name

            overlay = self._get_overlay()
            overlay.open(
                title="Waffe bearbeiten",
                content_widget=dialog_content,
                action_text="Speichern",
                on_action=self.update_waffe,
            )

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
        """Löscht die ausgewählten Waffen"""
        try:
            if not self.dialog_content:
                self.show_error("Dialog-Content nicht gefunden.")
                return

            selected = self.dialog_content.get_selected_items()
            if not selected:
                self.show_error("Bitte wähle mindestens eine Waffe zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter
            
            for waffe_name in selected:
                success = charakter.remove_ausruestung(waffe_name)
                if success:
                    Logger.info(f"Waffe '{waffe_name}' wurde gelöscht.")
                else:
                    Logger.warning(f"Waffe '{waffe_name}' konnte nicht gelöscht werden.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_ausruestung_view()
            self._show_success_snackbar(f"{len(selected)} Waffe(n) gelöscht")
            
            Logger.info(f"{len(selected)} Waffe(n) wurde(n) gelöscht.")
            self.dismiss_dialog()
                
        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Waffen: {e}")
            self.show_error("Fehler beim Löschen der Waffen")

    def on_waffe_select(self, waffe_name):
        """Callback wenn eine Waffe ausgewählt wurde"""
        self.selected_waffe = waffe_name

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_waffe = None

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
        Logger.error(f"Waffe-Fehler: {message}")

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
            Logger.debug(f"Ausrüstung-Widget nicht gefunden: {e}")

    def _show_success_snackbar(self, message):
        """Zeigt eine Erfolgs-Snackbar an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass