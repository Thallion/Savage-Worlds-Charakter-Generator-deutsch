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
from kivymd.uix.dialog import (
    MDDialog, MDDialogHeadlineText, MDDialogContentContainer,
    MDDialogButtonContainer
)
from utils.custom_filemanager import CustomFileManager
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

# Import centralized path utilities
from utils.path_utils import get_application_root, get_settings_path, get_user_settings_path

# Erstellen der Settings-Ordner, falls nicht existent
_native_settings_path = Path(get_settings_path())
_user_settings_path = Path(get_user_settings_path())
_native_settings_path.mkdir(parents=True, exist_ok=True)
_user_settings_path.mkdir(parents=True, exist_ok=True)
Logger.debug(f"Nativer Settings-Pfad: {_native_settings_path}")
Logger.debug(f"Benutzer Settings-Pfad: {_user_settings_path}")

# Domain-Repository zum Speichern, Laden und Löschen von Settings (DDD-Schicht)
class SettingsRepository:
    def __init__(self, settings_dir):
        # settings_dir wird als natives Verzeichnis verwendet (Rückwärtskompatibilität)
        self.settings_dir = settings_dir
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        # Benutzer-Settings werden in einem persistenten Verzeichnis gespeichert
        self.user_settings_dir = _user_settings_path
        self.user_settings_dir.mkdir(parents=True, exist_ok=True)

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
        filepath = self.user_settings_dir / dateiname
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
                controller.charakter.custom_element_manager.reload_settings()
                controller.charakter.custom_element_manager.set_active_setting(setting_name)
                controller.charakter.load_elements_from_active_setting()

                # Speichere das geladene Setting als letztes Setting in der Config
                self._save_last_setting_to_config(setting_name)

                # Setting-Change-Event für kontextabhängige UI-Umschaltung auslösen
                if hasattr(controller, 'dispatch') and setting_name:
                    controller.dispatch('on_setting_changed', setting_name)

                # Sicher auf einstellungen_widget zugreifen (kann beim Start noch nicht existieren)
                app = MDApp.get_running_app()
                if hasattr(app, 'einstellungen_widget') and app.einstellungen_widget:
                    app.einstellungen_widget.aktualisiere_ui()
                else:
                    Logger.debug("EinstellungenWidget noch nicht verfügbar für UI-Update")
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
                    controller.charakter.custom_element_manager.reload_settings()
                    Logger.info(f"Setting '{setting_name}' gelöscht.")

                    # Sicher auf einstellungen_widget zugreifen (kann beim Start noch nicht existieren)
                    app = MDApp.get_running_app()
                    if hasattr(app, 'einstellungen_widget') and app.einstellungen_widget:
                        app.einstellungen_widget.aktualisiere_ui()
                    else:
                        Logger.debug("EinstellungenWidget noch nicht verfügbar für UI-Update")
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
        self.file_manager = CustomFileManager(
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
        try:
            from utils.path_utils import get_user_settings_path
            user_settings_dir = Path(get_user_settings_path())
            
            for item in self.controller.charakter.talente.values():
                item.ausgewaehlt = False
            for item in self.controller.charakter.handicaps.values():
                item.ausgewaehlt = False
            for item in self.controller.charakter.maechte.values():
                item.ausgewaehlt = False
            for item in self.controller.charakter.ausruestung.values():
                if item is not None:
                    item.ausgewaehlt = False

            new_setting = {
                "name": setting_name,
                "description": setting_description,
                "voelker": {name: volk.to_setting_dict() for name, volk in self.controller.charakter.voelker.items()},
                "talente": {name: talent.to_dict() for name, talent in self.controller.charakter.talente.items()},
                "handicaps": {name: handicap.to_dict() for name, handicap in self.controller.charakter.handicaps.items()},
                "fertigkeiten_daten": {name: list(attribut_set) for name, attribut_set in self.controller.charakter.fertigkeiten_daten.items()},
                "maechte": {name: macht.to_dict() for name, macht in self.controller.charakter.maechte.items()},
                "ausruestung": {name: ausruestung.to_setting_dict() for name, ausruestung in self.controller.charakter.ausruestung.items()}
            }

            success = self.controller.charakter.custom_element_manager.save_setting(setting_name, new_setting)
            if success:
                self.controller.charakter.custom_element_manager.reload_settings()
                Logger.info(f"Setting 'custom_{setting_name}' gespeichert.")
                from services.service_container import service_container
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    dialog_service.show_success_dialog(f"Setting '{setting_name}' gespeichert.")
                if self.popup:
                    self.popup.dismiss()

                # Sicher auf einstellungen_widget zugreifen (kann beim Start noch nicht existieren)
                app = MDApp.get_running_app()
                if hasattr(app, 'einstellungen_widget') and app.einstellungen_widget:
                    app.einstellungen_widget.aktualisiere_ui()
                else:
                    Logger.debug("EinstellungenWidget noch nicht verfügbar für UI-Update")
            else:
                self.show_error("Setting konnte nicht gespeichert werden.")
        except Exception as e:
            self.show_error(f"Fehler beim Speichern des Settings: {e}")

    def show_error(self, message):
        error_dialog = MDDialog(
            MDDialogHeadlineText(text="Fehler"),
            MDDialogContentContainer(
                MDLabel(text=message, halign="center"),
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                create_text_button("Schließen", lambda x: error_dialog.dismiss()),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=True,
        )
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
        # Zeige das native Settings-Verzeichnis (enthält alle mitgelieferten Settings)
        settings_dir = _native_settings_path
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
        error_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(
                MDLabel(text=message, halign="center"),
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                create_text_button("Schließen", lambda x: error_dialog.dismiss()),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=True,
        )
        error_dialog.open()

class DeleteSettingPopup(MDBoxLayout, BaseFileManagerMixin):
    controller = ObjectProperty()
    popup = ObjectProperty(None)
    repository = ObjectProperty()

    def show_file_manager_popup(self):
        # Lösch-Dialog zeigt das Benutzer-Settings-Verzeichnis
        # (native Settings können nicht gelöscht werden)
        settings_dir = _user_settings_path
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
        error_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(
                MDLabel(text=message, halign="center"),
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                create_text_button("Schließen", lambda x: error_dialog.dismiss()),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=True,
        )
        error_dialog.open()

# Controller: Verknüpft die Dialoge (Views) mit dem Domain-Repository
class SettingDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.repository = SettingsRepository(_native_settings_path)
        self.dialog = None

    def show_add_dialog(self):
        """Wrapper für einheitliche Handler-Schnittstelle"""
        self.open_add_setting_popup()

    def show_delete_dialog(self):
        """Wrapper für einheitliche Handler-Schnittstelle"""
        self.open_delete_setting_popup()

    def open_add_setting_popup(self):
        popup_content = AddSettingPopup(controller=self.controller)
        popup_content.repository = self.repository

        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Neues Setting erstellen"),
            MDDialogContentContainer(
                popup_content,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                create_text_button("Abbrechen", lambda x: self.dialog.dismiss()),
                create_text_button("Speichern", popup_content.save_setting),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        popup_content.popup = self.dialog
        self.dialog.open()

    def open_load_setting_popup(self):
        popup_content = LoadSettingPopup(controller=self.controller)
        popup_content.repository = self.repository

        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Setting laden"),
            MDDialogContentContainer(
                popup_content,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                create_text_button("Abbrechen", lambda x: self.dialog.dismiss()),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        popup_content.popup = self.dialog
        self.dialog.open()

    def open_delete_setting_popup(self):
        popup_content = DeleteSettingPopup(controller=self.controller)
        popup_content.repository = self.repository

        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Setting löschen"),
            MDDialogContentContainer(
                popup_content,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                create_text_button("Abbrechen", lambda x: self.dialog.dismiss()),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        popup_content.popup = self.dialog
        popup_content.show_file_manager_popup()  # Direktstart der Dateiauswahl
        self.dialog.open()
