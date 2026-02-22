# views\setting_popup.py
# -*- coding: utf-8 -*-
"""
Optimierter Code für die Settings-Funktionalität:
 • Nutzung von MDBoxLayout (statt des alten BoxLayout).
 • MDDialog wird gemäß KivyMD 2.0.1 manuell zusammengesetzt,
   sodass keine ungültigen Properties (title, content_cls, buttons, etc.)
   direkt übergeben werden.
 • UI-Elemente (z. B. Textfelder, Labels) werden im inline eingebetteten
   KV‑String definiert.
 • Der Code folgt den Prinzipien von DDD und MVC.
 • MDFlatButton und MDTextButton existieren in KivyMD 2.0.1 nicht – daher
   wird MDButton mit style "text" genutzt. Der Text wird dabei über ein
   untergeordnetes MDButtonText-Widget gesetzt.
 • Für MDLabel sind als font_style nur "Display", "Headline", "Title", "Label"
   und "Body" gültig.
"""

import sys, os, json
from pathlib import Path

# Kivy/KivyMD-Module
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText

# Hilfsfunktion zum Erzeugen eines Buttons mit Text gemäß KivyMD 2.0.1
def create_text_button(button_text, on_release):
    btn = MDButton(style="text", on_release=on_release)
    btn.add_widget(MDButtonText(text=button_text))
    return btn

# KV-Definition: Alle UI-Komponenten werden hier deklariert (Popups, Textfelder, Labels)
import os
import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'setting_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'setting_popup.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"setting_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

# Hilfsfunktion zur Bestimmung des Applikations‑Rootpfads
# Import centralized path utilities
from utils.path_utils import get_application_root

# Erstellen des Ordners "settings", falls nicht existent
app_root = get_application_root()
settings_path = app_root / "settings"
settings_path.mkdir(parents=True, exist_ok=True)
Logger.debug(f"Settings-Pfad: {settings_path}")

# Domain-Repository zum Speichern, Laden und Löschen von Settings (DDD-Schicht)
class SettingsRepository:
    def __init__(self, settings_dir):
        self.settings_dir = settings_dir
        self.settings_dir.mkdir(parents=True, exist_ok=True)

    def save(self, setting_name, setting_description, charakter):
        # Alle "ausgewaehlten" Attribute zurücksetzen
        for item in charakter.talente.values():
            item.ausgewaehlt = False
        for item in charakter.handicaps.values():
            item.ausgewaehlt = False
        for item in charakter.maechte.values():
            item.ausgewaehlt = False
        for item in charakter.ausruestung.values():
            if item is not None:
                item.ausgewaehlt = False

        # Erstelle das Setting-Dictionary – jedes Model liefert seine eigene Repräsentation
        new_setting = {
            "name": setting_name,
            "description": setting_description,
            "voelker": {name: volk.to_setting_dict() for name, volk in charakter.voelker.items()},
            "talente": {name: talent.to_dict() for name, talent in charakter.talente.items()},
            "handicaps": {name: handicap.to_dict() for name, handicap in charakter.handicaps.items()},
            "fertigkeiten_daten": {name: list(attribut_set) for name, attribut_set in charakter.fertigkeiten_daten.items()},
            "maechte": {name: macht.to_dict() for name, macht in charakter.maechte.items()},
            "ausruestung": {name: ausruestung.to_setting_dict() for name, ausruestung in charakter.ausruestung.items()}
        }
        dateiname = f"{setting_name}.json"
        filepath = self.settings_dir / dateiname
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(new_setting, f, ensure_ascii=False, indent=4)
            Logger.info(f"Setting '{setting_name}' gespeichert unter {filepath}")
            return True
        except Exception as e:
            Logger.error(f"Fehler beim Speichern: {e}")
            raise e

    def load(self, filepath, controller):
        try:
            setting_datei = Path(filepath)
            if not setting_datei.is_file():
                raise FileNotFoundError("Keine gültige Datei ausgewählt")
            with open(setting_datei, "r", encoding="utf-8") as f:
                setting_data = json.load(f)
            setting_name = setting_data.get("name", setting_datei.stem)
            if controller and controller.charakter:
                controller.charakter.custom_element_manager.set_active_setting(setting_name)
                controller.charakter.load_elements_from_active_setting()

                # Speichere das geladene Setting als letztes Setting in der Config
                self._save_last_setting_to_config(setting_name)

                # Setting-Change-Event für kontextabhängige UI-Umschaltung auslösen
                if hasattr(controller, 'dispatch') and setting_name:
                    controller.dispatch('on_setting_changed', setting_name)

                MDApp.get_running_app().einstellungen_widget.aktualisiere_ui()
            Logger.info(f"Setting '{setting_name}' geladen.")
            return setting_data
        except Exception as e:
            Logger.error(f"Ladevorgang fehlgeschlagen: {e}")
            raise e

    def delete(self, filepath, controller):
        try:
            setting_name = Path(filepath).stem
            if controller and controller.charakter:
                success = controller.charakter.custom_element_manager.delete_setting(setting_name)
                if success:
                    Logger.info(f"Setting '{setting_name}' gelöscht.")
                    MDApp.get_running_app().einstellungen_widget.aktualisiere_ui()
                    return True
                else:
                    Logger.error(f"Löschen fehlgeschlagen für: {setting_name}")
                    return False
        except Exception as e:
            Logger.error(f"Fehler beim Löschen: {e}")
            raise e
    
    def _save_last_setting_to_config(self, setting_name):
        """
        Speichert das Setting als letztes verwendetes Setting in der Konfiguration
        
        Args:
            setting_name (str): Name des Settings
        """
        try:
            from services.service_container import get_config_service
            config_service = get_config_service()
            
            if config_service:
                config_service.set('last_setting', setting_name)
                Logger.info(f"Letztes Setting in Config gespeichert: {setting_name}")
            else:
                Logger.warning("ConfigService nicht verfügbar - letztes Setting konnte nicht gespeichert werden")
                
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des letzten Settings in Config: {str(e)}")

# Basisklasse für MDFileManager-Handling (wiederverwendbare Logik)
class BaseFileManagerMixin:
    file_manager = None

    def open_file_manager(self, settings_dir, select_callback):
        self.file_manager = MDFileManager(
            exit_manager=self.close_file_manager,
            select_path=select_callback,
            ext=[".json"],
            preview=False
        )
        self.file_manager.current_path = str(settings_dir)
        self.file_manager.show(str(settings_dir))

    def close_file_manager(self, *args):
        if self.file_manager:
            self.file_manager.close()
            self.file_manager = None

# UI-Klassen für Popups – basierend auf MDBoxLayout; das Layout erfolgt ausschließlich via KV
class AddSettingPopup(MDBoxLayout, BaseFileManagerMixin):
    controller = ObjectProperty()
    popup = ObjectProperty(None)
    repository = ObjectProperty()

    def save_setting(self, *args):
        setting_name = self.ids.setting_name_input.text.strip()
        setting_description = self.ids.setting_description_input.text.strip()
        if not setting_name:
            self.show_error("Der Name des Settings darf nicht leer sein.")
            return
        settings_dir = get_application_root() / "settings"
        self.open_file_manager(settings_dir, self.datei_ausgewaehlt)

    def datei_ausgewaehlt(self, gewaehlter_ordner):
        setting_name = self.ids.setting_name_input.text.strip()
        filename = f"{setting_name}.json"
        vollstaendiger_pfad = Path(gewaehlter_ordner) / filename
        try:
            app = MDApp.get_running_app()
            charakter = app.controller.charakter
            self.repository.save(setting_name, self.ids.setting_description_input.text.strip(), charakter)
            Logger.info(f"Setting '{setting_name}' gespeichert unter {vollstaendiger_pfad}")
            if self.popup:
                self.popup.dismiss()
        except Exception as e:
            self.show_error(f"Fehler beim Speichern des Settings: {e}")
        finally:
            self.close_file_manager()

    def show_error(self, message):
        error_dialog = MDDialog(auto_dismiss=True)
        error_container = MDBoxLayout(orientation="vertical", padding="12dp", spacing="12dp")
        label = MDLabel(text=message, halign="center")
        error_container.add_widget(label)
        btn_container = MDBoxLayout(orientation="horizontal", spacing="12dp",
                                    size_hint_y=None, height="40dp")
        btn_cancel = create_text_button("Schließen", lambda x: error_dialog.dismiss())
        btn_container.add_widget(btn_cancel)
        error_container.add_widget(btn_container)
        error_dialog.add_widget(error_container)
        error_dialog.open()

class LoadSettingPopup(MDBoxLayout, BaseFileManagerMixin):
    controller = ObjectProperty()
    popup = ObjectProperty(None)
    repository = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Starte den Dateiauswahlprozess beim Initialisieren
        self.show_file_manager_popup()

    def show_file_manager_popup(self):
        settings_dir = get_application_root() / "settings"
        if not settings_dir.exists():
            settings_dir.mkdir(parents=True, exist_ok=True)
        self.open_file_manager(settings_dir, self.datei_ausgewaehlt)

    def datei_ausgewaehlt(self, gewaehlter_pfad):
        try:
            self.repository.load(gewaehlter_pfad, self.controller)
            Logger.info(f"Setting aus '{gewaehlter_pfad}' geladen.")
        except Exception as e:
            self.show_error(f"Fehler beim Laden:\n{e}")
        finally:
            self.close_file_manager()
            if self.popup:
                self.popup.dismiss()

    def show_error(self, message, title="Fehler"):
        error_dialog = MDDialog(auto_dismiss=True)
        error_container = MDBoxLayout(orientation="vertical", padding="12dp", spacing="12dp")
        label = MDLabel(text=message, halign="center")
        error_container.add_widget(label)
        btn_container = MDBoxLayout(orientation="horizontal", spacing="12dp",
                                    size_hint_y=None, height="40dp")
        btn_cancel = create_text_button("Schließen", lambda x: error_dialog.dismiss())
        btn_container.add_widget(btn_cancel)
        error_container.add_widget(btn_container)
        error_dialog.add_widget(error_container)
        error_dialog.open()

class DeleteSettingPopup(MDBoxLayout, BaseFileManagerMixin):
    controller = ObjectProperty()
    popup = ObjectProperty(None)
    repository = ObjectProperty()

    def show_file_manager_popup(self):
        settings_dir = get_application_root() / "settings"
        if not settings_dir.exists():
            settings_dir.mkdir(parents=True, exist_ok=True)
        self.open_file_manager(settings_dir, self.datei_ausgewaehlt)

    def datei_ausgewaehlt(self, gewaehlter_pfad):
        try:
            self.repository.delete(gewaehlter_pfad, self.controller)
        except Exception as e:
            self.show_error(f"Fehler beim Löschen des Settings:\n{e}")
        finally:
            self.close_file_manager()
            if self.popup:
                self.popup.dismiss()

    def show_error(self, message, title="Fehler"):
        error_dialog = MDDialog(auto_dismiss=True)
        error_container = MDBoxLayout(orientation="vertical", padding="12dp", spacing="12dp")
        label = MDLabel(text=message, halign="center")
        error_container.add_widget(label)
        btn_container = MDBoxLayout(orientation="horizontal", spacing="12dp",
                                    size_hint_y=None, height="40dp")
        btn_cancel = create_text_button("Schließen", lambda x: error_dialog.dismiss())
        btn_container.add_widget(btn_cancel)
        error_container.add_widget(btn_container)
        error_dialog.add_widget(error_container)
        error_dialog.open()

# Controller: Verknüpft die Dialoge (Views) mit dem Domain-Repository
class SettingDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        settings_dir = get_application_root() / "settings"
        self.repository = SettingsRepository(settings_dir)
        self.dialog = None

    def open_add_setting_popup(self):
        popup_content = AddSettingPopup(controller=self.controller)
        popup_content.repository = self.repository

        # Container für den Dialogaufbau (Titel, Inhalt, Buttonleiste)
        container = MDBoxLayout(orientation="vertical", spacing="12dp", padding="12dp")
        title_label = MDLabel(text="Neues Setting erstellen", halign="center",
                              font_style="Title", size_hint_y=None, height="40dp")
        container.add_widget(title_label)
        container.add_widget(popup_content)
        btn_container = MDBoxLayout(orientation="horizontal", spacing="12dp",
                                    size_hint_y=None, height="40dp")
        btn_cancel = create_text_button("Abbrechen", lambda x: self.dialog.dismiss())
        btn_save = create_text_button("Speichern", popup_content.save_setting)
        btn_container.add_widget(btn_cancel)
        btn_container.add_widget(btn_save)
        container.add_widget(btn_container)
        self.dialog = MDDialog(auto_dismiss=False)
        self.dialog.add_widget(container)
        popup_content.popup = self.dialog
        self.dialog.open()

    def open_load_setting_popup(self):
        popup_content = LoadSettingPopup(controller=self.controller)
        popup_content.repository = self.repository
        container = MDBoxLayout(orientation="vertical", spacing="12dp", padding="12dp")
        title_label = MDLabel(text="Setting laden", halign="center",
                              font_style="Title", size_hint_y=None, height="40dp")
        container.add_widget(title_label)
        container.add_widget(popup_content)
        btn_container = MDBoxLayout(orientation="horizontal", spacing="12dp",
                                    size_hint_y=None, height="40dp")
        btn_cancel = create_text_button("Abbrechen", lambda x: self.dialog.dismiss())
        btn_container.add_widget(btn_cancel)
        container.add_widget(btn_container)
        self.dialog = MDDialog(auto_dismiss=False)
        self.dialog.add_widget(container)
        popup_content.popup = self.dialog
        self.dialog.open()

    def open_delete_setting_popup(self):
        popup_content = DeleteSettingPopup(controller=self.controller)
        popup_content.repository = self.repository
        container = MDBoxLayout(orientation="vertical", spacing="12dp", padding="12dp")
        title_label = MDLabel(text="Setting löschen", halign="center",
                              font_style="Title", size_hint_y=None, height="40dp")
        container.add_widget(title_label)
        container.add_widget(popup_content)
        btn_container = MDBoxLayout(orientation="horizontal", spacing="12dp",
                                    size_hint_y=None, height="40dp")
        btn_cancel = create_text_button("Abbrechen", lambda x: self.dialog.dismiss())
        btn_container.add_widget(btn_cancel)
        container.add_widget(btn_container)
        self.dialog = MDDialog(auto_dismiss=False)
        self.dialog.add_widget(container)
        popup_content.popup = self.dialog
        popup_content.show_file_manager_popup()  # Direktstart der Dateiauswahl
        self.dialog.open()
