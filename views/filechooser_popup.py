# filechooser_popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.app import App
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
from kivy.uix.filechooser import FileChooserListView

from kivy.properties import ListProperty, BooleanProperty, ObjectProperty, StringProperty
from kivymd.uix.selectioncontrol import MDCheckbox

from pathlib import Path
import json, sys, os

# ------------------------------------------------------------------------
# KV-Layout-Definition
# ------------------------------------------------------------------------
kv = '''
<FileChooserPopup>:
    orientation: 'vertical'
    spacing: "12dp"
    padding: "12dp"
    
    FileChooserListView:
        id: filechooser
        filters: root.file_filters
        path: root.default_path
        on_selection: root.update_selection(self.selection)
    
    MDTextField:
        id: filename_input
        text: root.filename
        size_hint_y: None
        height: '40dp'
        mode: "outlined"
        
        MDTextFieldHintText:
            text: 'Dateiname'
    
    MDBoxLayout:
        size_hint_y: None
        height: '40dp'
        spacing: 10
        
        MDButton:
            style: "elevated"
            size_hint_y: None
            height: 40
            on_release: root.do_cancel()
            
            MDButtonText:
                text: 'Abbrechen'
                pos_hint: {"center_x": .5, "center_y": .5}
    
        MDButton:
            style: "elevated"
            size_hint_y: None
            height: 40
            on_release: root.do_load()
            
            MDButtonText:
                text: 'Speichern' if root.save else 'Laden'
                pos_hint: {"center_x": .5, "center_y": .5}

    MDBoxLayout:
        size_hint_y: None
        height: 40 if root.show_printer_friendly_option else 0
        opacity: 1 if root.show_printer_friendly_option else 0
        spacing: 10
        padding: (10, 0)

        MDCheckbox:
            id: printer_friendly_checkbox
            active: root.printer_friendly
            on_active: root.printer_friendly = self.active
            size_hint: None, None
            size: "48dp", "48dp"
            pos_hint: {"center_y": .5}

        MDLabel:
            text: 'Druckerfreundliche Version erstellen'
            size_hint_x: None
            width: 250
            halign: 'left'
            valign: 'middle'
            text_size: self.width, self.height
'''

def get_application_root():
    if getattr(sys, "frozen", False):
        app_root = Path(sys.executable).parent
    else:
        app_root = Path(__file__).parent.resolve()
    return app_root

app_root = get_application_root()
settings_path = app_root / "settings"
settings_path.mkdir(parents=True, exist_ok=True)
Logger.debug(f"Settings-Pfad erstellt oder existiert bereits: {settings_path}")

class FileChooserPopup(MDBoxLayout):
    selection = ListProperty([])
    save = BooleanProperty(False)
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    filename = StringProperty('')
    file_filters = ListProperty(['*.*'])
    default_filename = StringProperty('')
    default_path = StringProperty('')
    printer_friendly = BooleanProperty(False)
    show_printer_friendly_option = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Standardpfad setzen
        self._set_default_path()

        # Standarddateiname setzen
        if self.save and self.default_filename:
            self.filename = self.default_filename

    def on_kv_post(self, base_widget):
        """Sicherstellen, dass der FileChooser den richtigen Pfad hat."""
        self._set_default_path()

    def _set_default_path(self):
        """Setzt den Standardpfad und stellt sicher, dass der Ordner existiert."""
        app_root = get_application_root()
        
        if self.default_path:
            path = Path(self.default_path).resolve()
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            self.ids.filechooser.path = str(path)
        else:
            self.ids.filechooser.path = str(app_root)

    def update_selection(self, selection):
        """Aktualisiert die Dateiauswahl"""
        self.selection = selection
        if selection:
            self.filename = Path(selection[0]).name
            Logger.debug(f"Ausgewählte Datei: {self.filename}")

    def do_load(self):
        """Führt den Lade- oder Speichervorgang aus"""
        path = Path(self.ids.filechooser.path)
        filename = self.ids.filename_input.text.strip()
        full_path = path / filename

        if self.save:
            if full_path.exists():
                self._show_overwrite_confirmation(path, filename)
            else:
                if self.load:
                    self.load(path, filename)
        else:
            if self.load:
                self.load(path, filename)

    def _show_overwrite_confirmation(self, path, filename):
        """Zeigt den Überschreiben-Dialog an"""
        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Bestätigung"
            ),
            MDDialogSupportingText(
                text="Datei existiert bereits. Überschreiben?"
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Nein"),
                    style="text",
                    on_release=lambda x: dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Ja"),
                    style="text",
                    on_release=lambda x: self.confirm_overwrite(dialog, path, filename),
                ),
                spacing="8dp",
            ),
        )
        dialog.open()

    def confirm_overwrite(self, dialog, path, filename):
        """Bestätigt das Überschreiben einer existierenden Datei"""
        dialog.dismiss()
        if self.load:
            vollstaendiger_pfad = path / filename
            Logger.debug(f"Überschreibung bestätigt für: {vollstaendiger_pfad}")
            self.load(path, filename)

    def do_cancel(self):
        """Bricht den Vorgang ab"""
        if self.cancel:
            Logger.debug("Abbruch des FileChooser-Popups.")
            self.cancel()            