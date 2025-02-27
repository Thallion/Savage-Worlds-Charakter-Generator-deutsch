"""
einstellungen.py
"""

# KivyMD-Imports
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDButton, MDIconButton, MDFabButton, MDButtonText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
from kivymd.theming import ThemableBehavior
from kivymd.uix.chip import MDChip, MDChipText
from pathlib import Path

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer
)

from kivy.lang import Builder
from kivy.app import App
from kivy.utils import get_color_from_hex
from kivy.properties import (
    NumericProperty,
    StringProperty,
    BooleanProperty,
    ObjectProperty,
    DictProperty,
    ListProperty,
)
from kivy.event import EventDispatcher
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivymd.uix.filemanager import MDFileManager
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.clock import Clock
import sys, os, json
from functools import partial
from kivy.logger import Logger, LOG_LEVELS
from pathlib import Path
from kivy.config import Config

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
    SimpleDocTemplate,
    PageBreak,
    ListFlowable,
    ListItem,
)
from reportlab.lib import colors
from PIL import Image

# Füge den übergeordneten Ordner zum sys.path hinzu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
Logger.info("Parent directory added to sys.path.")

# Importieren der benutzerdefinierten Module
from controllers.decorators import Fehlerbehandlung
from controllers.charakter_controller import CharakterController
from charakter import Charakter
from models.ausruestung import Ausruestung
from models.waffe import Waffe
from models.talent import Talent
from models.macht import Macht
from models.volk import Volk
from models.handicap import Handicap
from models.ruestung import Ruestung
from models.schild import Schild
from models.fertigkeit import Fertigkeit
from models.attribut import Attribut
from views.volk_popup import VolkDialogContent, DeleteVolkDialogContent, VolkDialogHandler
from views.macht_popup import MachtDialogContent, DeleteMachtDialogContent, MachtDialogHandler
from views.schild_popup import SchildDialogContent, DeleteSchildDialogContent, SchildDialogHandler
from views.waffe_popup import WaffeDialogContent, DeleteWaffeDialogContent, WaffeDialogHandler
from views.fertigkeit_popup import FertigkeitDialogContent, DeleteFertigkeitDialogContent, FertigkeitDialogHandler
from views.ruestung_popup import RuestungDialogContent, DeleteRuestungDialogContent, RuestungDialogHandler
from views.ausruestung_popup import AusruestungDialogContent, DeleteAusruestungDialogContent, AusruestungDialogHandler
from views.handicap_popup import HandicapDialogContent, DeleteHandicapDialogContent, HandicapDialogHandler
from views.talent_popup import TalentDialogContent, DeleteTalentDialogContent, TalentDialogHandler
from views.setting_popup import AddSettingPopup, LoadSettingPopup, DeleteSettingPopup, SettingDialogHandler

kv = '''
<EinstellungenWidget>:
    MDScrollView:
        do_scroll_x: False
        do_scroll_y: True
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(24)
            padding: dp(16)
            size_hint_y: None
            height: self.minimum_height

            # Theme und Farben Card
            MDCard:
                style: "elevated"
                padding: dp(16)
                size_hint_y: None
                height: self.minimum_height
                md_bg_color: app.theme_cls.surfaceColor

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(16)
                    size_hint_y: None
                    height: self.minimum_height

                    # Theme Controls
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(16)

                        MDLabel:
                            text: 'Theme:'
                            size_hint: None, None
                            size: dp(100), dp(40)
                            pos_hint: {"center_y": .5}

                        MDSegmentedButton:
                            MDSegmentedButtonItem:
                                size_hint: None, None
                                size: dp(100), dp(40)
                                on_release: root.switch_theme_style('Light')
                                selected: app.theme_cls.theme_style == 'Light'

                                MDSegmentButtonLabel:
                                    text: "Hell"

                            MDSegmentedButtonItem:
                                size_hint: None, None
                                size: dp(100), dp(40)
                                on_release: root.switch_theme_style('Dark')
                                selected: app.theme_cls.theme_style == 'Dark'

                                MDSegmentButtonLabel:
                                    text: "Dunkel"

                    # Farbschema
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(16)

                        MDLabel:
                            text: 'Farbschema:'
                            size_hint: None, None
                            size: dp(100), dp(40)
                            pos_hint: {"center_y": .5}

                        MDGridLayout:
                            id: colors_box
                            cols: 3
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(8)
                            padding: 0
                            pos_hint: {"center_y": .5}

            # Charakter-Einstellungen Card
            MDCard:
                style: "elevated"
                padding: dp(16)
                size_hint_y: None
                height: self.minimum_height
                md_bg_color: app.theme_cls.surfaceColor

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(20)
                    size_hint_y: None
                    height: self.minimum_height

                    # Startattribute
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(45)
                        spacing: dp(25)

                        MDLabel:
                            text: "Startattributs-Punkte:"
                            size_hint: None, None
                            size: dp(180), dp(40)
                            pos_hint: {"center_y": .5}

                        MDTextField:
                            text: root.maximale_attributsteigerungen_input
                            size_hint: None, None
                            size: dp(100), dp(30)
                            input_filter: 'int'
                            pos_hint: {"center_y": .5}
                            on_focus: if not self.focus: root.update_maximale_attributsteigerungen()
                            on_text: root.maximale_attributsteigerungen_input = self.text

                    # Startfertigkeiten
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(20)

                        MDLabel:
                            text: "Startfertigkeits-Punkte:"
                            size_hint: None, None
                            size: dp(180), dp(40)
                            pos_hint: {"center_y": .5}

                        MDTextField:
                            text: root.maximale_fertigkeitssteigerungen_input
                            size_hint: None, None
                            size: dp(100), dp(30)
                            pos_hint: {"center_y": .5}
                            input_filter: 'int'
                            on_focus: if not self.focus: root.update_maximale_fertigkeitssteigerungen()
                            on_text: root.maximale_fertigkeitssteigerungen_input = self.text

                    # Vermögen Einstellungen
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(16)

                        MDLabel:
                            text: "Vermögen:"
                            size_hint: None, None
                            size: dp(100), dp(40)
                            pos_hint: {"center_y": .5}

                        MDTextField:
                            text: root.vermoegen_input
                            size_hint: None, None
                            size: dp(120), dp(30)
                            input_filter: 'int'
                            on_focus: if not self.focus: root.update_vermoegen()
                            on_text: root.vermoegen_input = self.text
                            pos_hint: {"center_y": .5}

                        MDTextField:
                            text: root.waehrung_input
                            size_hint: None, None
                            size: dp(100), dp(40)
                            on_focus: if not self.focus: root.update_waehrung()
                            on_text: root.waehrung_input = self.text
                            pos_hint: {"center_y": .5}

                    MDButton:
                        style: "elevated"
                        size_hint: None, None
                        size: dp(300), dp(40)
                        pos_hint: {"left": 1}
                        on_release: root.erhoehe_startkapital(); root.update_vermoegen()
                        
                        MDButtonText:
                            text: 'Erhöhe Startkapital mit Handicap-Punkten'

                    MDGridLayout:
                        cols: 2
                        spacing: dp(8)
                        size_hint_y: None
                        height: dp(48)

                        MDButton:
                            style: "tonal"
                            size_hint_x: 1
                            on_release: root.erhoehe_Auftstiege()

                            MDButtonIcon:
                                icon: "plus"

                            MDButtonText:
                                text: "Aufstieg"

                        MDButton:
                            style: "outlined"
                            size_hint_x: 1
                            on_release: root.senke_auftstiege()

                            MDButtonIcon:
                                icon: "minus"

                            MDButtonText:
                                text: "Abstieg"

            # Verwaltungs Card
            MDCard:
                padding: dp(16)
                spacing: dp(16)
                size_hint_y: None
                height: self.minimum_height

                MDGridLayout:
                    cols: 2
                    spacing: dp(16)
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(8)

                    # Linke Spalte - Grundfunktionen
                    MDBoxLayout:
                        orientation: 'vertical'
                        spacing: dp(16)
                        size_hint_y: None
                        height: self.minimum_height

                        # Charakter-Verwaltung
                        MDBoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(8)

                            MDLabel:
                                text: "Charakter"
                                bold: True

                            MDGridLayout:
                                cols: 2
                                spacing: dp(8)
                                size_hint_y: None
                                height: dp(48)

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1

                                    MDButtonIcon:
                                        icon: "content-save"

                                    MDButtonText:
                                        text: "Speichern"

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1

                                    MDButtonIcon:
                                        icon: "folder-open"

                                    MDButtonText:
                                        text: "Laden"

                        # Setting-Verwaltung
                        MDBoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(8)

                            MDLabel:
                                text: "Setting"
                                bold: True

                            MDGridLayout:
                                cols: 3
                                spacing: dp(8)
                                size_hint_y: None
                                height: dp(48)

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1
                                    on_release: root.open_add_setting_popup()
                                    MDButtonIcon:
                                        icon: "plus"
                                    MDButtonText:
                                        text: "Neu"

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1
                                    on_release: root.open_load_setting_popup()
                                    MDButtonIcon:
                                        icon: "folder-open"
                                    MDButtonText:
                                        text: "Laden"

                                MDButton:
                                    style: "outlined"
                                    size_hint_x: 1
                                    on_release: root.open_delete_setting_popup()
                                    MDButtonIcon:
                                        icon: "delete"
                                    MDButtonText:
                                        text: "Löschen"

                    # Rechte Spalte - PDF und Aufstiege
                    MDBoxLayout:
                        orientation: 'vertical'
                        spacing: dp(16)
                        size_hint_y: None
                        height: self.minimum_height

                        MDButton:
                            style: "filled"
                            size_hint_x: 1
                            on_release: root.erzeuge_charakterbogen_pdf()

                            MDButtonIcon:
                                icon: "file-pdf-box"

                            MDButtonText:
                                text: "PDF erstellen"

            # Spielelemente Card
            MDCard:
                padding: dp(16)
                spacing: dp(16)
                size_hint_y: None
                height: self.minimum_height

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(16)
                    size_hint_y: None
                    height: self.minimum_height

                    # Volk
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "account-group"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Volk"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_volk_dialog()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_volk_dialog()

                            MDButtonIcon:
                                icon: "minus"

                    # Fertigkeiten
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "fencing"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Fertigkeiten"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_fertigkeit_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_fertigkeit_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Handicaps
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "account-alert"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Handicaps"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_handicap_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_handicap_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Talente
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "star-circle"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Talente"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_talent_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_talent_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Mächte
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "creation-outline"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Mächte"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_macht_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_macht_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Ausrüstung
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "sack"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Ausrüstung"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_ausruestung_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_ausruestung_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Rüstung
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "shield"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Rüstung"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_ruestung_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_ruestung_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Waffen
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "sword"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Waffe"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_waffe_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_waffe_popup()

                            MDButtonIcon:
                                icon: "minus"

                    # Schild
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(16)

                        MDIcon:
                            icon: "shield"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Schild"
                            size_hint_x: None
                            width: dp(100)
                            pos_hint: {"center_y": .5}

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_add_schild_popup()

                            MDButtonIcon:
                                icon: "plus"

                        MDButton:
                            style: "text"
                            size_hint: None, None
                            size: dp(48), dp(48)
                            on_release: root.open_delete_schild_popup()

                            MDButtonIcon:
                                icon: "minus"

<FileChooserPopup>:
    orientation: 'vertical'
    
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

# Checkbox für druckerfreundliche Version
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
Builder.load_string(kv)

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

class EinstellungenWidget(MDScreen):
    controller = ObjectProperty()
    vermoegen_input = StringProperty("500")
    waehrung_input = StringProperty("Gold")
    maximale_attributsteigerungen_input = StringProperty("5")
    maximale_fertigkeitssteigerungen_input = StringProperty("12")
    fehler_meldung = StringProperty("")
    current_color = StringProperty("")
    available_colors = ListProperty([
        'Blue', 'Green', 'Teal', 
        'Purple', 'Red', 'Saddlebrown', 
        'Orange', 'Gold', 'Olive'
    ])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = App.get_running_app().controller
        self._init_values()
        Clock.schedule_once(self._setup_colors)  # Verzögerte Initialisierung

        # Dialog-Handler initialisieren
        self.volk_dialog_handler = VolkDialogHandler(self.controller)
        self.macht_dialog_handler = MachtDialogHandler(self.controller)
        self.schild_dialog_handler = SchildDialogHandler(self.controller)
        self.talent_dialog_handler = TalentDialogHandler(self.controller)
        self.handicap_dialog_handler = HandicapDialogHandler(self.controller)
        self.ruestung_dialog_handler = RuestungDialogHandler(self.controller)
        self.ausruestung_dialog_handler = AusruestungDialogHandler(self.controller)        
        self.waffe_dialog_handler = WaffeDialogHandler(self.controller)
        self.fertigkeit_dialog_handler = FertigkeitDialogHandler(self.controller)
        self.setting_dialog_handler = SettingDialogHandler(self.controller)

    def _init_values(self):
        self.vermoegen_input = str(self.controller.charakter.vermoegen)
        self.waehrung_input = self.controller.charakter.waehrungseinheit
        self.maximale_attributsteigerungen_input = str(
            self.controller.charakter.maximale_attributsteigerungen
        )
        self.maximale_fertigkeitssteigerungen_input = str(
            self.controller.charakter.maximale_fertigkeitssteigerungen
        )
        App.get_running_app().einstellungen_widget = self

    def _setup_colors(self, *args):
        app = App.get_running_app()
        self.current_color = app.theme_cls.primary_palette
        self.create_color_chips()

    def create_color_chips(self, *args):
        if not hasattr(self.ids, 'colors_box'):
            return
            
        self.ids.colors_box.clear_widgets()
        for farbe in self.available_colors:
            # Chip mit Text erstellen
            chip = MDChip(
                MDChipText(
                    text=farbe,
                    theme_text_color="Secondary",
                ),
                type="filter",
                active=farbe == self.current_color,
                md_bg_color=self.theme_cls.primaryColor if farbe == self.current_color else [0, 0, 0, 0],
                on_release=lambda x, f=farbe: self.switch_primary_palette(f)
            )
            self.ids.colors_box.add_widget(chip)

    def get_chip_text_color(self, farbe):
        """Ermittelt die passende Textfarbe für den Chip basierend auf dem Theme."""
        if self.theme_cls.theme_style == "Dark":
            return [1, 1, 1, 1]  # Weiß für dunkles Theme
        return [0, 0, 0, 1]  # Schwarz für helles Theme

    def switch_theme_style(self, style):
        App.get_running_app().theme_cls.theme_style = style

    def switch_primary_palette(self, color_name):
        app = App.get_running_app()
        app.theme_cls.primary_palette = color_name
        self.current_color = color_name
        self.create_color_chips()  

    def create_new_character(self):
        # Bestätigungsdialog anzeigen
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text='Bist du sicher, dass du einen neuen Charakter erstellen möchtest? Der aktuelle Charakter wird verworfen.'))
        buttons = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_yes = Button(text='Ja')
        btn_no = Button(text='Nein')
        buttons.add_widget(btn_yes)
        buttons.add_widget(btn_no)
        content.add_widget(buttons)
        popup = Popup(title='Bestätigung', content=content, size_hint=(0.5, 0.5))

        def confirm_new_character(instance):
            popup.dismiss()
            # Aktives Setting vom aktuellen Charakter abrufen
            active_setting = self.controller.charakter.active_setting_name
            # Neuen Charakter mit dem aktiven Setting erstellen
            self.controller.charakter = Charakter(active_setting_name=active_setting)
            # Elemente aus dem aktiven Setting laden
            self.controller.charakter.load_elements_from_active_setting()
            # Benutzeroberfläche aktualisieren
            self.aktualisiere_ui()

        btn_yes.bind(on_release=confirm_new_character)
        btn_no.bind(on_release=popup.dismiss)
        popup.open()

    def speichere_charakter(self):
        # Versuche, das Verzeichnis relativ zur ausführbaren Datei zu finden
        if getattr(sys, 'frozen', False):
            # Wenn das Programm durch cx_Freeze gepackt ist, nutze den Ordner der ausführbaren Datei
            base_dir = os.path.dirname(sys.executable)
        else:
            # Bei normalem Python-Skript nutze den Pfad des aktuellen Skripts
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # chars-Verzeichnis im Basisverzeichnis anlegen
        chars_dir = os.path.join(base_dir, 'chars')
        if not os.path.exists(chars_dir):
            os.makedirs(chars_dir)
        
        # Öffne das FileChooser-Popup und setze das Standardverzeichnis
        content = FileChooserPopup(
            save=True,
            load=self.speichere_char_in_datei,
            cancel=self.dismiss_popup,
            file_filters=['*.json'],
            default_filename='charakter.json',
            default_path=chars_dir  # Standardpfad auf chars_dir setzen
        )
        self._popup = Popup(title="Charakter speichern", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def speichere_char_in_datei(self, pfad, dateiname):
        if dateiname:
            vollstaendiger_pfad = os.path.join(pfad, dateiname)
            self.controller.charakter.speichern_als_json(vollstaendiger_pfad)
        self.dismiss_popup()

    def lade_charakter(self):
        # Basisverzeichnis dynamisch basierend auf cx_Freeze-Umgebung bestimmen
        if getattr(sys, 'frozen', False):
            # Bei gepackter Anwendung (cx_Freeze) das Verzeichnis der ausführbaren Datei verwenden
            base_dir = os.path.dirname(sys.executable)
        else:
            # Bei normalem Python-Skript das Skriptverzeichnis verwenden
            base_dir = os.path.dirname(os.path.abspath(__file__))

        # Verzeichnis für Charaktere unterhalb des Basisverzeichnisses festlegen
        chars_dir = os.path.join(base_dir, 'chars')
        if not os.path.exists(chars_dir):
            os.makedirs(chars_dir)

        # FileChooser-Popup zum Laden eines Charakters öffnen, Standardpfad auf chars_dir setzen
        content = FileChooserPopup(
            load=self.laden_datei_ausgewaehlt,
            cancel=self.dismiss_popup,
            file_filters=['*.json'],
            default_path=chars_dir  # Standardpfad auf chars_dir setzen
        )
        self._popup = Popup(title="Charakter laden", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def laden_datei_ausgewaehlt(self, pfad, dateiname):

        if dateiname:
            vollstaendiger_pfad = os.path.join(pfad, dateiname)
            self.controller.charakter.laden_von_json(vollstaendiger_pfad)
            Logger.debug("Charakter aus Datei geladen. Aktualisiere die UI.")
            
            # Speichern des Pfades der geladenen Charakterdatei
            self.controller.current_character_file_path = vollstaendiger_pfad
            
            # Aktualisiere die UI nach dem Laden
            self.aktualisiere_ui()        
        
        self.dismiss_popup()

    def erhoehe_Auftstiege(self):
        self.controller.charakter.increase_aufstiege()

    def erhoehe_startkapital(self):
        self.controller.charakter.erhoehe_startkapital()
        self.vermoegen_input = str(self.controller.charakter.vermoegen)

    def senke_auftstiege(self):
        self.controller.charakter.decrease_aufstiege()

    def update_vermoegen(self):
        """Validiert und aktualisiert das Vermögen basierend auf den Eingaben."""
        try:
            # Versuche, das Vermögen als Integer zu parsen
            neues_vermoegen = int(self.vermoegen_input)
            if neues_vermoegen < 0:
                raise ValueError("Vermögen darf nicht negativ sein.")
            self.controller.charakter.vermoegen = neues_vermoegen
            self.fehler_meldung = ""
        except ValueError:
            # Zeige eine Fehlermeldung an oder handle den Fehler entsprechend
            Logger.error("Ungültiges Vermögen. Bitte gib eine positive Zahl ein.")
            self.fehler_meldung = "Ungültiges Vermögen. Bitte gib eine positive Zahl ein."

    def update_maximale_attributsteigerungen(self):
        """Validiert und aktualisiert das Startattribute basierend auf den Eingaben."""
        try:
            # Versuche, das Vermögen als Integer zu parsen
            neu_maximale_attributsteigerungen = int(self.maximale_attributsteigerungen_input)
            if neu_maximale_attributsteigerungen < 0:
                raise ValueError("Startattribute darf nicht negativ sein.")
            self.controller.charakter.maximale_attributsteigerungen = neu_maximale_attributsteigerungen
            self.controller.charakter.verbleibende_attributsteigerungen = neu_maximale_attributsteigerungen
            self.fehler_meldung = ""
        except ValueError:
            # Zeige eine Fehlermeldung an oder handle den Fehler entsprechend
            Logger.error("Ungültiges Startattribut. Bitte gib eine positive Zahl ein.")
            self.fehler_meldung = "Ungültiges Startattribut. Bitte gib eine positive Zahl ein."

    def update_maximale_fertigkeitssteigerungen(self):
        """Validiert und aktualisiert das Startfertigkeiten basierend auf den Eingaben."""
        try:
            # Versuche, das Vermögen als Integer zu parsen
            neu_maximale_fertigkeitssteigerungen = int(self.maximale_fertigkeitssteigerungen_input)
            if neu_maximale_fertigkeitssteigerungen < 0:
                raise ValueError("Startfertigkeiten darf nicht negativ sein.")
            self.controller.charakter.maximale_fertigkeitssteigerungen = neu_maximale_fertigkeitssteigerungen
            self.controller.charakter.verbleibende_fertigkeitssteigerungen = neu_maximale_fertigkeitssteigerungen
            self.fehler_meldung = ""
        except ValueError:
            # Zeige eine Fehlermeldung an oder handle den Fehler entsprechend
            Logger.error("Ungültiges Startfertigkeit. Bitte gib eine positive Zahl ein.")
            self.fehler_meldung = "Ungültiges Startfertigkeit. Bitte gib eine positive Zahl ein."

    def update_waehrung(self):
        """Aktualisiert die Währungseinheit basierend auf den Eingaben."""
        self.controller.charakter.waehrungseinheit = self.waehrung_input.strip()
        self.fehler_meldung = ""
        self.aktualisiere_ui()

    def get_widget_by_tab_text(self, tab_text, widget_id):
        """Sucht in app.root.ids.tabs_carousel den Screen, dessen Name == tab_text.
        Gibt daraus das child-Widget mit ID == widget_id zurück."""
        app = App.get_running_app()
        try:
            carousel = app.root.ids.tabs_carousel
            for index, (icon, name, screen_class) in enumerate(app.tab_definitions):
                if name == tab_text:
                    screen = carousel.slides[index]
                    Logger.debug(f"Screen {name} has IDs: {screen.ids}")
                    widget = screen.ids.get(widget_id)
                    if widget:
                        return widget
                    else:
                        Logger.error(f"Widget {widget_id} not found in screen {name}.")
                    break
            return None
        except Exception as e:
            Logger.error(f"Fehler in get_widget_by_tab_text: {e}")
            return None

    def aktualisiere_ui(self):
        Logger.debug("aktualisiere_ui aufgerufen")
        try:
            app = App.get_running_app()

            # 1) Charakterbogen aktualisieren
            charakterbogen_widget = self.get_widget_by_tab_text('Charakter', 'charakterbogen_widget')
            if charakterbogen_widget:
                charakterbogen_widget.update_overview(0)
                Logger.debug("CharakterbogenWidget.update_overview() aufgerufen.")
            else:
                Logger.error("CharakterbogenWidget nicht gefunden.")

            # 2) Eigenschaften-Tab
            eigenschaften_widget = self.get_widget_by_tab_text('Eigenschaften', 'eigenschaften_widget')
            if eigenschaften_widget:
                eigenschaften_widget.update_eigenschaften()
                Logger.debug("EigenschaftenWidget.update_eigenschaften() aufgerufen.")
            else:
                Logger.error("EigenschaftenWidget nicht gefunden.")

            # 3) Ausrüstung-Tab
            ausruestung_widget = self.get_widget_by_tab_text('Ausrüstung', 'ausruestung_widget')
            if ausruestung_widget:
                ausruestung_widget.refresh_widget()
                Logger.debug("AusrüstungWidget.refresh_widget() aufgerufen.")
            else:
                Logger.error("AusrüstungWidget nicht gefunden.")

            # 4) Profil-Tab
            profil_widget = self.get_widget_by_tab_text('Profil', 'profil_widget')
            if profil_widget:
                profil_widget.load_profil()
                Logger.debug("ProfilWidget.load_profil() aufgerufen.")
            else:
                Logger.error("ProfilWidget nicht gefunden.")

            # 5) Völker-Tab
            voelker_widget = self.get_widget_by_tab_text('Völker', 'voelker_widget')
            if voelker_widget:
                voelker_widget.aktualisiere_ui()
                Logger.debug("VoelkerWidget.aktualisiere_ui() aufgerufen.")
            else:
                Logger.error("VoelkerWidget nicht gefunden.")

            # 6) Talente-Tab
            talente_widget = self.get_widget_by_tab_text('Talente', 'talente_widget')
            if talente_widget:
                talente_widget.refresh_widget()
                Logger.debug("TalenteWidget.refresh_widget() aufgerufen.")
            else:
                Logger.error("TalenteWidget nicht gefunden.")

            # 7) Mächte-Tab
            maechte_widget = self.get_widget_by_tab_text('Mächte', 'maechte_widget')
            if maechte_widget:
                maechte_widget.refresh_widget()
                Logger.debug("MaechteWidget.refresh_widget() aufgerufen.")
            else:
                Logger.error("MaechteWidget nicht gefunden.")

            # 8) Handicaps-Tab
            handicaps_widget = self.get_widget_by_tab_text('Handicaps', 'handicaps_widget')
            if handicaps_widget:
                handicaps_widget.refresh_widget()
                Logger.debug("HandicapsWidget.refresh_widget() aufgerufen.")
            else:
                Logger.error("HandicapWidget nicht gefunden.")

            Logger.info("UI erfolgreich aktualisiert.")

        except Exception as e:
            Logger.error(f"Fehler in aktualisiere_ui: {e}", exc_info=True)
            raise

    def erzeuge_charakterbogen_pdf(self):
        # Versuche, das Verzeichnis relativ zur ausführbaren Datei zu finden
        if getattr(sys, 'frozen', False):
            # Wenn das Programm durch cx_Freeze gepackt ist, nutze den Ordner der ausführbaren Datei
            base_dir = os.path.dirname(sys.executable)
        else:
            # Bei normalem Python-Skript nutze den Pfad des aktuellen Skripts
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # chars-Verzeichnis im Basisverzeichnis anlegen
        chars_dir = os.path.join(base_dir, 'chars')
        if not os.path.exists(chars_dir):
            os.makedirs(chars_dir)
        
        # Öffne das FileChooser-Popup und setze das Standardverzeichnis
        content = FileChooserPopup(
            save=True,
            load=self.speichere_pdf_datei_ausgewaehlt,
            cancel=self.dismiss_popup,
            file_filters=['*.pdf'],
            default_filename='charakter.pdf',
            default_path=chars_dir,  # Standardpfad auf chars_dir setzen
            show_printer_friendly_option=True  # Option aktivieren
        )
        self._popup = Popup(title="PDF speichern", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def generiere_pdf(self, output_pdf, printer_friendly=False):
        """
        Generiert das Charakterbogen-PDF und speichert es unter dem angegebenen Pfad.
        """
        # Versuche, das Verzeichnis relativ zur ausführbaren Datei zu finden
        if getattr(sys, 'frozen', False):
            # Wenn das Programm durch cx_Freeze gepackt ist, nutze den Ordner der ausführbaren Datei
            base_dir = os.path.dirname(sys.executable)
        else:
            # Bei normalem Python-Skript nutze den Pfad des aktuellen Skripts
            base_dir = os.path.dirname(os.path.abspath(__file__))

        # Datei-Pfad für das Hintergrundbild relativ zum Basisverzeichnis
        background_img = os.path.join(base_dir, "assets", "charbogen_hintergrund.jpg")  # Hintergrundbild

        charakter = self.controller.charakter

        # Dokument erstellen mit konsistenten Seitenrändern
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=A4,
            topMargin=10,      # Oberer Rand auf 10 Punkte setzen
            bottomMargin=10,   # Unterer Rand auf 10 Punkte setzen
            leftMargin=25,     # Linker Rand auf 10 Punkte setzen
            rightMargin=25     # Rechter Rand auf 10 Punkte setzen
        )

        elements = []

        # Hintergrundbild-Funktion definieren
        def add_background(canvas_obj, doc_obj):
            if not printer_friendly:
                canvas_obj.drawImage(background_img, 0, 0, width=A4[0], height=A4[1])

        # Styles definieren
        styles = getSampleStyleSheet()

        # Individuelle Anpassungen der Stile
        style_normal = styles['Normal']
        style_heading = styles['Heading2']
        style_title = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            leading=12,
            spaceBefore=0,
            spaceAfter=12
        )

        # Farbdefinitionen, abhängig von printer_friendly
        if not printer_friendly:
            moccasin = colors.HexColor('#ffb961')  # Moccasin für die Kopfzeile
            oldlace = colors.HexColor('#FFE4B5')   # OldLace für die restlichen Zeilen
        else:
            moccasin = colors.white
            oldlace = colors.white

        # Einheitliche Stilbefehle definieren als separate Liste
        tabellen_style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), moccasin),          # Kopfzeile
            ('BACKGROUND', (0, 1), (-1, -1), oldlace),          # Zeilen
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),   # Kopfzeile fett
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]

        # Erstellen eines Basis TableStyle
        tabellen_style = TableStyle(tabellen_style_commands)

        # Überschrift mit angepasstem Stil
        elements.append(Paragraph("Charakterbogen:", style_title))
        elements.append(Spacer(1, 6))  # 6 Punkte Abstand

        # Maximale Größen für Elemente definieren
        max_width = 450  # Maximalbreite in Punkten
        max_height = 750  # Maximalhöhe in Punkten

        # Funktion zum sicheren Hinzufügen von Elementen
        def add_element_safely(element):
            if isinstance(element, KeepTogether):
                # Vermeide das direkte Aufrufen von wrap auf KeepTogether
                # Stattdessen logge eine Warnung und füge die Inhalte einzeln hinzu
                # Logger.warning("KeepTogether innerhalb von add_element_safely wird nicht unterstützt.")
                for item in element._content:
                    add_element_safely(item)
            else:
                elements.append(element)

        # **Profildaten Abschnitt**
        profil_section = []
        profil_section.append(Paragraph("Profil", style_heading))
        profil_data = charakter.profil_daten
        profil_table_data = [["Attribut", "Beschreibung"]]
        for key, value in profil_data.items():
            profil_table_data.append([key, value])

        # Anpassung der colWidths auf 275 Punkte
        profil_table = Table(profil_table_data, colWidths=[60, 225], hAlign='LEFT')  # Summe = 275
        profil_table.setStyle(tabellen_style)
        profil_section.append(profil_table)
        profil_section.append(Spacer(1, 6))
        elements.append(KeepTogether(profil_section))

        # **Kombination von Attribute, Fertigkeiten und Abgeleitete Werte**
        combined_section = []

        # **Linke Spalte: Attribute und Fertigkeiten**
        left_column_content = []

        # **Attribut-Tabelle mit Überschrift**
        attribute_header = Paragraph("Attribute", style_heading)
        attribute_data = [["Attribut", "Wert"]]
        for attribut in charakter.attribute.values():
            wert_text = f"W{attribut.wert}"
            mod_text = self.create_mod_text(attribut.modifier)
            combined_text = f"{wert_text} {mod_text}" if mod_text else wert_text
            attribute_data.append([attribut.attribut_name, combined_text])

        attribute_table = Table(attribute_data, colWidths=[100, 50], hAlign='LEFT')
        attribute_table.setStyle(tabellen_style)
        left_column_content.append(attribute_header)
        left_column_content.append(attribute_table)
        left_column_content.append(Spacer(1, 6))  # 6 Punkte Abstand

        # **Fertigkeiten-Tabelle mit Überschrift**
        fertigkeiten_header = Paragraph("Fertigkeiten", style_heading)
        fertigkeiten_data = [["Fertigkeit", "Wert"]]
        for fertigkeit in charakter.fertigkeiten.values():
            if fertigkeit.modifier == -2:
                continue
            if fertigkeit.modifier == 0 and fertigkeit.wert not in [4, 6, 8, 10, 12]:
                continue
            wert_text = f"W{fertigkeit.wert}"
            mod_text = self.create_mod_text(fertigkeit.modifier)
            combined_text = f"{wert_text} {mod_text}" if mod_text else wert_text
            fertigkeiten_data.append([fertigkeit.fertigkeit_name, combined_text])

        fertigkeiten_table = Table(fertigkeiten_data, colWidths=[100, 50], hAlign='LEFT')
        fertigkeiten_table.setStyle(tabellen_style)
        left_column_content.append(fertigkeiten_header)
        left_column_content.append(fertigkeiten_table)
        left_column_content.append(Spacer(1, 6))  # 6 Punkte Abstand

        # **Rechte Spalte: Abgeleitete Werte / Volk**

        right_column_content = []

        # **Volk Abschnitt**
        volk_section = []

        # Ausgewähltes Volk ermitteln
        selected_volk = None
        for volk, aktiv in charakter.voelker_selected.items():
            if aktiv:
                selected_volk = volk
                break

        if not selected_volk:
            volk_section.append(Paragraph("Kein Volk ausgewählt.", style_normal))
        else:
            # Ausgewähltes Volk aus charakter.voelker holen
            volk_obj = charakter.voelker.get(selected_volk, None)

            volk_text = f"Volk: {selected_volk}"
            volk_section.append(Paragraph(volk_text, style_heading))

            if not volk_obj:
                volk_section.append(Paragraph("Keine Daten für das ausgewählte Volk vorhanden.", style_normal))
            else:
                # Talente
                if volk_obj.talente:
                    volk_section.append(Paragraph(" ", style_normal))
                    talente_table_data = [["Talent"]]
                    for talent in volk_obj.talente:
                        talente_table_data.append([Paragraph(talent, style_normal)])
                    talente_table = Table(talente_table_data, colWidths=[200], hAlign='LEFT')
                    talente_table.setStyle(TableStyle(tabellen_style_commands.copy()))
                    volk_section.append(talente_table)
                    volk_section.append(Spacer(3, 1))

                # Handicaps
                if volk_obj.handicaps:
                    volk_section.append(Paragraph(" ", style_normal))
                    handicaps_table_data = [["Handicap"]]
                    for handicap in volk_obj.handicaps:
                        handicaps_table_data.append([Paragraph(handicap, style_normal)])
                    handicaps_table = Table(handicaps_table_data, colWidths=[200], hAlign='LEFT')
                    handicaps_table.setStyle(TableStyle(tabellen_style_commands.copy()))
                    volk_section.append(handicaps_table)
                    volk_section.append(Spacer(3, 1))

                # Besonderheiten
                if volk_obj.besonderheiten:
                    volk_section.append(Paragraph(" ", style_normal))
                    besonderheiten_table_data = [["Besonderheit"]]
                    for besonderheit in volk_obj.besonderheiten:
                        besonderheiten_table_data.append([Paragraph(besonderheit, style_normal)])
                    besonderheiten_table = Table(besonderheiten_table_data, colWidths=[200], hAlign='LEFT')
                    besonderheiten_table.setStyle(TableStyle(tabellen_style_commands.copy()))
                    volk_section.append(besonderheiten_table)
                    volk_section.append(Spacer(3, 1))

        right_column_content.append(volk_section)
        right_column_content.append(Spacer(1, 6))      

        abgeleitete_header = Paragraph("Abgeleitete Werte", style_heading)
        abgeleitete_data = [["Beschreibung", "Wert"]]
        abgeleitete_werte = {
            'Bewegungsweite': charakter.bewegungsweite,
            'Parade': charakter.parade,
            'Robustheit': charakter.robustheit_mit_ruestung,
            'Machtpunkte': charakter.machtpunkte,
            'Wunden': charakter.wunden,
            'Erschöpfung': charakter.erschoepfung,
            'Bennys': charakter.bennys,
            'Entschlossenheit': charakter.entschlossenheit,
            'Maximale Traglast': f"{charakter.gesamtgewicht} / {charakter.maximale_traglast} kg",
        }
        for key, value in abgeleitete_werte.items():
            abgeleitete_data.append([key, str(value)])

        abgeleitete_table = Table(abgeleitete_data, colWidths=[100, 70], hAlign='LEFT')
        abgeleitete_table.setStyle(tabellen_style)
        right_column_content.append(abgeleitete_header)
        right_column_content.append(abgeleitete_table)
        right_column_content.append(Spacer(1, 6))  # 6 Punkte Abstand

        # **Kombinieren der linken und rechten Spalte mit Abstand**
        combined_data = [
            [left_column_content, Spacer(1, 10), right_column_content]
        ]
        combined_table = Table(combined_data, colWidths=[200, 20, 180], hAlign='LEFT')
        combined_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Inhalt oben ausrichten
        ]))
        combined_section.append(combined_table)
        combined_section.append(Spacer(1, 6))  # 6 Punkte Abstand
        elements.append(KeepTogether(combined_section))

        # **Handicaps Abschnitt**
        handicaps_section = []
        handicaps_section.append(Paragraph("Handicaps", style_heading))
        handicaps = charakter.selected_handicaps
        data = [["Handicap", "Stufe"]]
        for handicap_name_key in handicaps:
            handicap = charakter.handicaps.get(handicap_name_key)
            if handicap:
                data.append([handicap.name, handicap.stufe])
                # Beschreibung hinzufügen
                beschreibung_paragraph = Paragraph(handicap.beschreibung, style_normal)
                data.append([beschreibung_paragraph, ''])  # Leeres Feld für zweite Spalte

        table = Table(data, colWidths=[450, 75], hAlign='LEFT')  # Summe = 275 + 300 = 575
        # Definieren eines neuen TableStyle für Handicaps, basierend auf tabellen_style_commands
        handicaps_style_commands = tabellen_style_commands.copy()
        for row in range(2, len(data), 2):
            handicaps_style_commands.extend([
                ('SPAN', (0, row), (-1, row)),          # Span über alle Spalten
                ('BACKGROUND', (0, row), (-1, row), oldlace),  # Hintergrundfarbe für Beschreibung
            ])

        handicaps_style = TableStyle(handicaps_style_commands)
        table.setStyle(handicaps_style)
        handicaps_section.append(table)
        handicaps_section.append(Spacer(1, 12))  # 12 Punkte Abstand
        #handicaps_content = KeepTogether(handicaps_section)
        #add_element_safely(handicaps_content)
        elements.append(KeepTogether(handicaps_section))

        # **Talente Abschnitt**
        talente_section = []
        talente_section.append(Paragraph("Talente", style_heading))
        talente = charakter.selected_talente
        data = [["Talent", "Rang"]]
        for talent_name_key in talente:
            talent = charakter.talente.get(talent_name_key)
            if talent:
                data.append([
                    talent.name,
                    talent.rang,
                ])
                # Beschreibung hinzufügen
                beschreibung_paragraph = Paragraph(talent.beschreibung, style_normal)
                data.append([beschreibung_paragraph])  # Nur eine Spalte

        table = Table(data, colWidths=[450, 75], hAlign='LEFT')  # Nur eine Spalte, volle Breite
        # Definieren eines neuen TableStyle für Talente, basierend auf tabellen_style_commands
        talente_style_commands = tabellen_style_commands.copy()
        for row in range(2, len(data), 2):
            talente_style_commands.extend([
                ('SPAN', (0, row), (-1, row)),          # Span über alle Spalten (hier nur eine)
                ('BACKGROUND', (0, row), (-1, row), oldlace),  # Hintergrundfarbe für Beschreibung
            ])

        talente_style = TableStyle(talente_style_commands)
        table.setStyle(talente_style)
        talente_section.append(table)
        talente_section.append(Spacer(1, 12))  # 12 Punkte Abstand
        #talente_content = KeepTogether(talente_section)
        #add_element_safely(talente_content)
        elements.append(KeepTogether(talente_section))

        # **Mächte Abschnitt**
        maechte_section = []
        maechte_section.append(Paragraph("Mächte", style_heading))
        maechte = charakter.selected_maechte
        data = [["Name", "Rang", "MP", "Reichweite", "Dauer"]]
        for macht_name_key in maechte:
            macht = charakter.maechte.get(macht_name_key)
            if macht:
                data.append([
                    macht.name,
                    macht.rang,
                    macht.machtpunkte,
                    macht.reichweite,
                    macht.dauer
                ])
                # Beschreibung hinzufügen
                beschreibung_paragraph = Paragraph(macht.beschreibung, style_normal)
                data.append([beschreibung_paragraph] + [''] * 4)  # Beschreibung über alle 6 Spalten

        table = Table(data, colWidths=[205, 80, 80, 80, 80], hAlign='LEFT')  # Summe = 575
        # Definieren eines neuen TableStyle für Mächte, basierend auf tabellen_style_commands
        maechte_style_commands = tabellen_style_commands.copy()
        for row in range(2, len(data), 2):
            maechte_style_commands.extend([
                ('SPAN', (0, row), (-1, row)),          # Span über alle Spalten
                ('BACKGROUND', (0, row), (-1, row), oldlace),  # Hintergrundfarbe für Beschreibung
            ])

        maechte_style = TableStyle(maechte_style_commands)
        table.setStyle(maechte_style)
        maechte_section.append(table)
        maechte_section.append(Spacer(1, 12))  # 12 Punkte Abstand
        #maechte_content = KeepTogether(maechte_section)
        #add_element_safely(maechte_content)
        elements.append(KeepTogether(maechte_section))

        # **Allgemeine Ausrüstung Abschnitt** (analog zu Waffen)
        allgemeine_ausruestung_section = []
        allgemeine_ausruestung_section.append(Paragraph("Allgemeine Ausrüstung", style_heading))

        allgemeine_ausruestung_items = [item for name, item in charakter.ausruestung.items()
                                        if item in charakter.selected_allgemeine_ausruestung and item.ausgewaehlt]

        # Spalten analog zu Waffen (dort Name, Schaden etc.): hier Name, Menge, Beschreibung
        data = [["Name", "Menge", "Beschreibung"]]
        for item in allgemeine_ausruestung_items:
            menge = getattr(item, 'menge', 1)
            beschreibung_text = getattr(item, 'beschreibung', '-')
            
            # Hier wird ein Paragraph-Objekt für die Beschreibung erstellt
            beschreibung_paragraph = Paragraph(beschreibung_text, style_normal)
            
            data.append([
                item.name,
                str(menge),
                beschreibung_paragraph
            ])

        allgemeine_table = Table(data, colWidths=[175, 50, 300], hAlign='LEFT')
        allgemeine_table.setStyle(TableStyle(tabellen_style_commands.copy()))
        allgemeine_ausruestung_section.append(allgemeine_table)
        allgemeine_ausruestung_section.append(Spacer(1, 12))
        elements.append(KeepTogether(allgemeine_ausruestung_section))

        # **Waffen Abschnitt**
        waffen_section = []
        waffen_section.append(Paragraph("Waffen", style_heading))
        waffen = [w for w in charakter.selected_waffen if w.angelegt]
        data = [["Name", "Schaden", "Reichweite", "FR", "Schuss", "PB"]]
        for waffe in waffen:
            eigenschaften = waffe.eigenschaften
            data.append([
                waffe.name,
                eigenschaften.get('Schaden', '-'),
                eigenschaften.get('Reichweite', '-'),
                eigenschaften.get('FR', '-'),
                eigenschaften.get('Schuss', '-'),
                eigenschaften.get('PB', '-')
            ])

        # Berechnung der Spaltenbreiten basierend auf Anzahl der Spalten und Gesamtbreite 
        waffen_table = Table(data, colWidths=[205, 70, 70, 60, 60, 60], hAlign='LEFT')  # Summe = 575
        waffen_table.setStyle(tabellen_style)
        waffen_section.append(waffen_table)
        waffen_section.append(Spacer(1, 12))  # 12 Punkte Abstand
        #waffen_content = KeepTogether(waffen_section)
        #add_element_safely(waffen_content)
        elements.append(KeepTogether(waffen_section))

        # **Rüstungen Abschnitt**
        ruestungen_section = []
        ruestungen_section.append(Paragraph("Rüstungen", style_heading))
        ruestungen = [r for r in charakter.selected_ruestungen if r.angelegt]
        if ruestungen:
            data = [["Name", "Torso", "Arme", "Beine", "Kopf"]]
            for ruestung in ruestungen:
                data.append([
                    ruestung.name,
                    str(ruestung.torso),
                    str(ruestung.arme),
                    str(ruestung.beine),
                    str(ruestung.kopf)
                ])
            # Gesamten Rüstungsschutz berechnen
            gesamt_ruestungsschutz = charakter.berechne_gesamt_ruestungsschutz()
            # Gesamtrüstungsschutz als letzte Zeile hinzufügen
            data.append([
                "Gesamt",
                str(gesamt_ruestungsschutz['Torso']),
                str(gesamt_ruestungsschutz['Arme']),
                str(gesamt_ruestungsschutz['Beine']),
                str(gesamt_ruestungsschutz['Kopf'])
            ])
            # Berechnung der Spaltenbreiten basierend auf Anzahl der Spalten und Gesamtbreite
            table = Table(data, colWidths=[205, 80, 80, 80, 80], hAlign='LEFT')  # Summe = 525
            ruestungen_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), moccasin),
                ('BACKGROUND', (0, 1), (-1, -2), oldlace),
                ('BACKGROUND', (0, -1), (-1, -1), moccasin),  # Letzte Zeile
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Kopfzeile fett
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Letzte Zeile fett
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])
            table.setStyle(ruestungen_style)
            ruestungen_section.append(table)
        else:
            ruestungen_section.append(Paragraph("Keine Rüstungen angelegt.", style_normal))
        ruestungen_section.append(Spacer(1, 12))  # 12 Punkte Abstand
        #ruestungen_content = KeepTogether(ruestungen_section)
        #add_element_safely(ruestungen_content)
        elements.append(KeepTogether(ruestungen_section))

        # **Schilde Abschnitt** (analog zu Waffen)
        schilde_section = []
        schilde_section.append(Paragraph("Schilde", style_heading))

        # Analog zu Waffen (waffen = [w for w in ... if w.angelegt]):
        # Bei Schilden: nur angelegte Schilde anzeigen
        schilde_items = [
            s for name, s in charakter.ausruestung.items()
            if s in charakter.selected_schilde and s.angelegt
            ]

        # Spalten analog zu Waffen, nur an Schilde angepasst:
        # Name, Parade, Deckung, Mindeststärke, Beschreibung
        data = [["Name", "Parade", "Deckung", "Mindeststärke"]]
        for schild in schilde_items:
            parade = getattr(schild, 'parade', '-')
            deckung = getattr(schild, 'deckung', '-')
            mindeststaerke = getattr(schild, 'mindeststaerke', '-')
            data.append([
                schild.name,
                str(parade),
                str(deckung),
                mindeststaerke
            ])

        schilde_table = Table(data, colWidths=[265, 80, 80, 100], hAlign='LEFT')
        schilde_table.setStyle(TableStyle(tabellen_style_commands.copy()))
        schilde_section.append(schilde_table)
        schilde_section.append(Spacer(1, 12))
        elements.append(KeepTogether(schilde_section))

        #Logger.debug(f"=== Allgemeine Ausrüstung ===")
        for name, item in charakter.ausruestung.items():
            Logger.debug(f"{name} - ausgewaehlt={item.ausgewaehlt}, angelegt={item.angelegt}, kategorie={item.kategorie}")
        Logger.debug(f"selected_allgemeine_ausruestung: {charakter.selected_allgemeine_ausruestung}")

        #Logger.debug(f"allgemeine_ausruestung_items (gefiltert): {allgemeine_ausruestung_items}")

        # PDF erstellen mit oder ohne Hintergrundbild
        if printer_friendly:
            doc.build(elements)
        else:
            doc.build(elements, onFirstPage=add_background, onLaterPages=add_background)

        Logger.info(f"PDF wurde erfolgreich erstellt.")

    def speichere_pdf_datei_ausgewaehlt(self, pfad, dateiname):
        if dateiname:
            vollstaendiger_pfad = os.path.join(pfad, dateiname)
            printer_friendly = self._popup.content.printer_friendly  # Wert der Checkbox abrufen
            self.generiere_pdf(vollstaendiger_pfad, printer_friendly)
        self.dismiss_popup()

    def create_mod_text(self, modifier):
        """
        Erstellt den Text für den Modifier.
        """
        if modifier != 0:
            return f"{modifier:+}"
        else:
            return ""

    def dismiss_popup(self):
        if self._popup:
            self._popup.dismiss()

    def change_active_setting(self, setting_name):
        if self.controller and self.controller.charakter:
            success = self.controller.charakter.custom_element_manager.set_active_setting(setting_name)
            if success:
                self.controller.charakter.load_elements_from_active_setting()
            else:
                self.fehler_meldung = f"Das Setting '{setting_name}' konnte nicht erstellt werden."

    def get_all_settings(self):
        if self.controller and self.controller.charakter:
            return self.controller.charakter.custom_element_manager.get_all_settings()
        else:
            return []    


    # Dialog Popups zum Hinzufügen und entfernen von Elementen

    def open_add_setting_popup(self):
        self.setting_dialog_handler.open_add_setting_popup()

    def open_load_setting_popup(self):
        self.setting_dialog_handler.open_load_setting_popup()        

    def open_delete_setting_popup(self):
        self.setting_dialog_handler.open_delete_setting_popup()

    def open_add_volk_dialog(self):
        self.volk_dialog_handler.show_add_dialog()

    def open_delete_volk_dialog(self):
        self.volk_dialog_handler.show_delete_dialog()

    def open_add_talent_popup(self):
        self.talent_dialog_handler.show_add_dialog()      

    def open_delete_talent_popup(self):
        self.talent_dialog_handler.show_delete_dialog()

    def open_add_macht_popup(self):
        self.macht_dialog_handler.show_add_dialog()

    def open_delete_macht_popup(self):
        self.macht_dialog_handler.show_delete_dialog()

    def open_add_fertigkeit_popup(self):
        self.fertigkeit_dialog_handler.show_add_dialog()

    def open_delete_fertigkeit_popup(self):
        self.fertigkeit_dialog_handler.show_delete_dialog()

    def open_add_handicap_popup(self):
        self.handicap_dialog_handler.show_add_dialog()

    def open_delete_handicap_popup(self):
        self.handicap_dialog_handler.show_delete_dialog()

    def open_add_ausruestung_popup(self):
        self.ausruestung_dialog_handler.show_add_dialog()

    def open_delete_ausruestung_popup(self):
        self.ausruestung_dialog_handler.show_delete_dialog()

    def open_add_waffe_popup(self):
        self.waffe_dialog_handler.show_add_dialog()

    def open_delete_waffe_popup(self):
        self.waffe_dialog_handler.show_delete_dialog()

    def open_add_ruestung_popup(self):
        self.ruestung_dialog_handler.show_add_dialog()

    def open_delete_ruestung_popup(self):
        self.ruestung_dialog_handler.show_delete_dialog()

    def open_add_schild_popup(self):
        self.schild_dialog_handler.show_add_dialog()

    def open_delete_schild_popup(self):
        self.schild_dialog_handler.show_delete_dialog()

