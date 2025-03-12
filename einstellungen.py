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
from kivymd.uix.selectioncontrol import MDCheckbox
from pathlib import Path
from utils.pdf_utils import generiere_pdf

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer
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
from kivy.metrics import dp

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

from utils.pdf_utils import generiere_pdf, create_mod_text

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
                                cols: 3
                                spacing: dp(8)
                                size_hint_y: None
                                height: dp(48)

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1
                                    on_release: root.create_new_character()  # Hinzugefügt

                                    MDButtonIcon:
                                        icon: "plus"

                                    MDButtonText:
                                        text: "Neu"

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1
                                    on_release: root.speichere_charakter()  # Hinzugefügt

                                    MDButtonIcon:
                                        icon: "content-save"

                                    MDButtonText:
                                        text: "Speichern"

                                MDButton:
                                    style: "elevated"
                                    size_hint_x: 1
                                    on_release: root.lade_charakter()  # Hinzugefügt

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
        Clock.schedule_once(self._setup_colors)
        
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
        
        # File Manager für Speichern/Laden initialisieren
        self.manager_open = False
        
        # Erweiterten FileManager mit Laufwerksauswahl erstellen
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False,  # Disable preview to make directory navigation clearer
        )
        
        # Laufwerksauswahl-Dialog
        self.drive_dialog = None
        
        # Plattform identifizieren (für Laufwerke)
        self.is_windows = os.name == 'nt'
        
        # Variable für den aktuellen Aktionstyp (Speichern/Laden)
        self.current_action = None

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
        """
        Erstellt einen neuen Charakter mit einem Eingabedialog für den Namen,
        bevor der Speicherort ausgewählt wird.
        """
        # Dialog für die Namenseingabe erstellen
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=20,
            adaptive_height=True
        )
        
        content.add_widget(MDLabel(
            text="Bitte gib einen Namen für den neuen Charakter ein:",
            size_hint_y=None,
            height=40
        ))
        
        # Textfeld für Charakternamen
        charname_input = MDTextField(
            text="",
            hint_text="Charaktername",
            size_hint_y=None,
            height=50
        )
        content.add_widget(charname_input)
        
        # Buttons-Container
        buttons = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=50,
            pos_hint={'right': 1}
        )
        
        # Abbrechen-Button
        cancel_button = MDButton(
            on_release=lambda x: self.close_name_dialog(),
            style="elevated",
            size_hint_x=None,
            width=120
        )
        cancel_button.add_widget(MDButtonText(text="Abbrechen"))
        
        # Weiter-Button
        continue_button = MDButton(
            on_release=lambda x: self.proceed_with_new_character(charname_input.text),
            style="elevated",
            size_hint_x=None,
            width=120
        )
        continue_button.add_widget(MDButtonText(text="Weiter"))
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(continue_button)
        content.add_widget(buttons)
        
        # Dialog erstellen
        headline = MDDialogHeadlineText(text="Neuen Charakter erstellen")
        
        self.name_dialog = MDDialog(
            md_bg_color=self.theme_cls.surfaceColor
        )
        self.name_dialog.add_widget(headline)
        self.name_dialog.add_widget(content)
        self.name_dialog.open()

    def close_name_dialog(self):
        """Schließt den Namen-Eingabedialog"""
        if hasattr(self, 'name_dialog') and self.name_dialog:
            self.name_dialog.dismiss()

    def proceed_with_new_character(self, character_name):
        """
        Setzt den Prozess zur Erstellung eines neuen Charakters fort
        nachdem der Name eingegeben wurde.
        
        Args:
            character_name (str): Der eingebebene Charaktername
        """
        # Dialog schließen
        self.close_name_dialog()
        
        if not character_name.strip():
            # Wenn kein Name eingegeben wurde
            self._show_error_dialog("Bitte gib einen Namen für den Charakter ein.")
            return
        
        # Bestätigungsdialog für das Verwerfen des aktuellen Charakters
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=20,
            adaptive_height=True
        )
        
        content.add_widget(MDLabel(
            text=f"Bist du sicher, dass du einen neuen Charakter '{character_name}' erstellen möchtest? Der aktuelle Charakter wird verworfen.",
            size_hint_y=None,
            height=60
        ))
        
        # Buttons-Container
        buttons = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=50,
            pos_hint={'right': 1}
        )
        
        # Nein-Button
        no_button = MDButton(
            on_release=lambda x: self.close_confirm_dialog(),
            style="elevated",
            size_hint_x=None,
            width=100
        )
        no_button.add_widget(MDButtonText(text="Nein"))
        
        # Ja-Button
        yes_button = MDButton(
            on_release=lambda x: self.create_character_with_name(character_name),
            style="elevated",
            size_hint_x=None,
            width=100
        )
        yes_button.add_widget(MDButtonText(text="Ja"))
        
        buttons.add_widget(no_button)
        buttons.add_widget(yes_button)
        content.add_widget(buttons)
        
        # Dialog erstellen
        headline = MDDialogHeadlineText(text="Bestätigung")
        
        self.confirm_dialog = MDDialog(
            md_bg_color=self.theme_cls.surfaceColor
        )
        self.confirm_dialog.add_widget(headline)
        self.confirm_dialog.add_widget(content)
        self.confirm_dialog.open()

    def close_confirm_dialog(self):
        """Schließt den Bestätigungsdialog"""
        if hasattr(self, 'confirm_dialog') and self.confirm_dialog:
            self.confirm_dialog.dismiss()

    def create_character_with_name(self, character_name):
        """
        Erstellt einen neuen Charakter mit dem angegebenen Namen
        und aktiviert die aktuelle Setting-Einstellung.
        
        Args:
            character_name (str): Der Name des neuen Charakters
        """
        self.close_confirm_dialog()
        
        # Aktives Setting vom aktuellen Charakter abrufen
        active_setting = self.controller.charakter.active_setting_name
        
        # Neuen Charakter mit dem aktiven Setting erstellen
        self.controller.charakter = Charakter(active_setting_name=active_setting)
        
        # Namen setzen
        self.controller.charakter.char_name = character_name
        
        # Profildaten aktualisieren
        self.controller.charakter.profil_daten["Name"] = character_name
        
        # Elemente aus dem aktiven Setting laden
        self.controller.charakter.load_elements_from_active_setting()
        
        # Benutzeroberfläche aktualisieren
        self.aktualisiere_ui()
        
        # Erfolgsmeldung anzeigen
        self._show_success_dialog(
            "Neuer Charakter erstellt", 
            f"Der Charakter '{character_name}' wurde erfolgreich erstellt."
        )

    def exit_manager(self, *args):
        """Schließt den MDFileManager."""
        self.manager_open = False
        self.file_manager.close()

    def show_file_manager(self, path, action_type):
        """
        Zeigt den FileManager mit zusätzlicher Laufwerksauswahl an.
        
        Args:
            path (str): Startpfad für den FileManager
            action_type (str): Art der Aktion ("load", "save_dir", etc.)
        """
        # Überprüfe, ob der Pfad existiert
        if not os.path.exists(path):
            Logger.warning(f"Der angegebene Pfad existiert nicht: {path}")
            path = os.path.expanduser("~")  # Auf den Home-Ordner zurückfallen
            
        # Setze aktuellen Aktionstyp
        self.current_action = action_type
        
        # Unter Windows: Zeige erst den Drive-Selector
        if self.is_windows:
            self.show_drive_selector(path, action_type)
        else:
            # Unter anderen Betriebssystemen direkt den Filemanager zeigen
            self.file_manager.show(path)
            self.manager_open = True

    def show_drive_selector(self, default_path, action_type):
        """
        Zeigt einen Dialog zur Auswahl des Laufwerks (nur für Windows).
        
        Args:
            default_path (str): Standardpfad (falls Laufwerksauswahl abgebrochen wird)
            action_type (str): Art der Aktion (wird gespeichert für späteren Gebrauch)
        """
        import string
        
        # Laufwerke identifizieren
        available_drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                available_drives.append((letter, drive))
        
        if not available_drives:
            # Keine Laufwerke gefunden (unwahrscheinlich) - direkt zum Standard gehen
            self.file_manager.show(default_path)
            self.manager_open = True
            return
        
        # Dialog-Inhalt erstellen
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(300),
            padding=dp(20)
        )
        
        # Überschrift
        content.add_widget(MDLabel(
            text="Laufwerk auswählen",
            font_style="H6",
            halign="center"
        ))
        
        # Grid für Laufwerksbuttons
        from kivymd.uix.gridlayout import MDGridLayout
        drive_grid = MDGridLayout(
            cols=4, 
            spacing=dp(10),
            adaptive_height=True
        )
        
        # Laufwerksbuttons erstellen
        for letter, drive_path in available_drives:
            drive_button = MDButton(
                style="elevated",
                size_hint=(None, None),
                size=(dp(80), dp(50)),
                on_release=lambda x, p=drive_path: self.select_drive(p)
            )
            drive_button.add_widget(MDButtonText(text=f"{letter}:"))
            drive_grid.add_widget(drive_button)
        
        content.add_widget(drive_grid)
        
        # Aktuelles Laufwerk bestimmen
        current_drive = os.path.splitdrive(default_path)[0] + "\\"
        
        # Info-Label
        info_label = MDLabel(
            text=f"Aktuelles Laufwerk: {current_drive}",
            halign="center"
        )
        content.add_widget(info_label)
        
        # Abbrechen-Button (verwendet bestehenden Pfad)
        cancel_button = MDButton(
            style="elevated",
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self._continue_with_path(default_path)
        )
        cancel_button.add_widget(MDButtonText(text="Aktuelles Laufwerk verwenden"))
        content.add_widget(cancel_button)
        
        # Dialog erstellen und anzeigen
        self.drive_dialog = MDDialog(
            MDDialogHeadlineText(text="Laufwerksauswahl"),
            MDDialogContentContainer(
                content,
                orientation="vertical",
            ),
        )
        self.drive_dialog.open()

    def select_drive(self, path):
        """
        Wählt ein Laufwerk aus und öffnet den FileManager.
        
        Args:
            path (str): Pfad zum ausgewählten Laufwerk
        """
        if self.drive_dialog:
            self.drive_dialog.dismiss()
            self.drive_dialog = None
        
        # FileManager mit dem ausgewählten Laufwerk öffnen
        self.file_manager.show(path)
        self.manager_open = True

    def _continue_with_path(self, path):
        """
        Setzt den FileManager-Prozess mit dem gegebenen Pfad fort.
        
        Args:
            path (str): Der zu verwendende Pfad
        """
        if self.drive_dialog:
            self.drive_dialog.dismiss()
            self.drive_dialog = None
        
        # FileManager öffnen
        self.file_manager.show(path)
        self.manager_open = True

    def speichere_charakter(self):
        """
        Zeigt einen Dialog mit Optionen zum Speichern des Charakters.
        """
        # Prüfen, ob bereits ein Dateipfad existiert
        hat_bereits_datei = hasattr(self.controller, 'current_character_file_path') and self.controller.current_character_file_path
        
        buttons_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            adaptive_height=True
        )
        
        # Wenn eine Datei existiert, zeige den Überschreiben-Button
        if hat_bereits_datei:
            filepath = self.controller.current_character_file_path
            filename = os.path.basename(filepath)
            
            info_label = MDLabel(
                text=f"Bestehende Datei: {filename}",
                size_hint_y=None,
                height=dp(40)
            )
            buttons_container.add_widget(info_label)
            
            # Button zum Überschreiben
            ueberschreiben_button = MDButton(
                style="elevated",
                size_hint=(1, None),
                height=dp(50),
                on_release=lambda x: self._ueberschreibe_existierende_datei()
            )
            ueberschreiben_button.add_widget(MDButtonText(text="Bestehende Datei überschreiben"))
            buttons_container.add_widget(ueberschreiben_button)
            
            # Abstandshalter
            spacer = Widget(size_hint_y=None, height=dp(20))
            buttons_container.add_widget(spacer)
        
        # Button für "Als neue Datei speichern"
        new_file_button = MDButton(
            style="elevated",
            size_hint=(1, None),
            height=dp(50),
            on_release=lambda x: self._als_neue_datei_speichern()
        )
        new_file_button.add_widget(MDButtonText(text="Als neue Datei speichern..."))
        buttons_container.add_widget(new_file_button)
        
        # Dialog erstellen
        self.save_options_dialog = MDDialog(
            MDDialogHeadlineText(text="Charakter speichern"),
            MDDialogContentContainer(
                buttons_container,
                orientation="vertical",
                padding="16dp"
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self.save_options_dialog.dismiss()
                )
            )
        )
        self.save_options_dialog.open()

    def _ueberschreibe_existierende_datei(self):
        """Überschreibt die existierende Datei direkt"""
        self.save_options_dialog.dismiss()
        
        filepath = self.controller.current_character_file_path
        try:
            self.controller.charakter.speichern_als_json(filepath)
            Logger.info(f"Charakter gespeichert in: {filepath}")
            self._show_success_dialog("Speichern erfolgreich", f"Charakter wurde in bestehender Datei gespeichert.")
        except Exception as e:
            self._show_error_dialog(f"Fehler beim Speichern: {str(e)}")

    def _als_neue_datei_speichern(self):
        """Zeigt einen Dialog zum Eingeben eines Dateinamens"""
        self.save_options_dialog.dismiss()
        
        # Standardname basierend auf Charakternamen
        default_filename = self.controller.charakter.char_name if self.controller.charakter.char_name else "charakter"
        default_filename = default_filename.strip().replace(" ", "_")  # Leerzeichen durch Unterstriche ersetzen
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            padding=dp(16),
            adaptive_height=True
        )
        
        content.add_widget(MDLabel(
            text="Dateiname für neue Datei:",
            size_hint_y=None,
            height=dp(30)
        ))
        
        filename_input = MDTextField(
            text=f"{default_filename}.json",
            hint_text="Dateiname.json",
            mode="outlined"
        )
        content.add_widget(filename_input)
        
        # Dialog zum Eingeben des Dateinamens
        self.filename_dialog = MDDialog(
            MDDialogHeadlineText(text="Als neue Datei speichern"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self.filename_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Speicherort wählen"),
                    style="text",
                    on_release=lambda x: self._continue_save_new_file(filename_input.text)
                )
            )
        )
        self.filename_dialog.open()

    def _continue_save_new_file(self, filename):
        """Setzt den Speicherprozess mit Dateiauswahl fort"""
        self.filename_dialog.dismiss()
        
        # Prüfe, ob ein gültiger Dateiname eingegeben wurde
        if not filename or not filename.strip():
            self._show_error_dialog("Bitte gib einen Dateinamen ein.")
            return
        
        # Stellt sicher, dass die Dateiendung .json ist
        if not filename.lower().endswith('.json'):
            filename += '.json'
        
        # Merke den Dateinamen und gehe zum Dateibrowser
        self.temp_filename = filename
        self._open_directory_browser_for_save()

    def _open_directory_browser_for_save(self):
        """
        Öffnet den Dateibrowser um das Zielverzeichnis zum Speichern auszuwählen.
        Der Dateiname wurde bereits in self.temp_filename gespeichert.
        """
        # Verzeichnis für Charaktere bestimmen
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        chars_dir = os.path.join(base_dir, 'chars')
        if not os.path.exists(chars_dir):
            os.makedirs(chars_dir)
        
        # Setze aktuellen Aktionstyp auf Verzeichnisauswahl für Speichern
        self.current_action = "save_dir"
        
        # MDFileManager anzeigen - nur für Verzeichnisauswahl
        self.file_manager.show(chars_dir)
        self.manager_open = True

    def save_character_to_path(self, full_path):
        """
        Speichert den Charakter an den angegebenen Pfad.
        
        Args:
            full_path (str): Vollständiger Pfad inkl. Dateiname
        """
        try:
            # Controller zum Speichern verwenden statt direkt auf dem Charakter
            success = self.controller.speichere_charakter_als_json(full_path)
            if success:
                Logger.info(f"Charakter gespeichert in: {full_path}")
                
                # Erfolgsbestätigung anzeigen
                self._show_success_dialog("Speichern erfolgreich", f"Charakter wurde gespeichert als:\n{full_path}")
            else:
                self._show_error_dialog(f"Fehler beim Speichern des Charakters")
        except Exception as e:
            self._show_error_dialog(f"Fehler beim Speichern des Charakters: {str(e)}")

    def select_path(self, path):
        """
        Wird aufgerufen, wenn eine Datei oder ein Verzeichnis ausgewählt wird.
        
        Args:
            path (str): Pfad zum ausgewählten Verzeichnis oder zur Datei
        """
        self.exit_manager()
        
        try:
            if self.current_action == "save_dir":
                # Logik für Verzeichnisauswahl zum Speichern
                if os.path.isdir(path):
                    # Vollständigen Pfad zusammensetzen
                    full_path = os.path.join(path, self.temp_filename)
                    
                    # Prüfen, ob die Datei bereits existiert
                    if os.path.exists(full_path):
                        self.confirm_overwrite(full_path)
                    else:
                        # Direkt speichern
                        self.save_character_to_path(full_path)
                else:
                    # Wenn eine Datei statt eines Verzeichnisses ausgewählt wurde
                    self._show_error_dialog("Bitte wähle ein Verzeichnis für die Speicherung aus.")
            
            elif self.current_action == "load":
                # Verbesserte Fehlerbehandlung beim Laden eines Charakters
                if not os.path.exists(path):
                    self._show_error_dialog(f"Der Pfad existiert nicht: {path}")
                    return
                    
                if os.path.isfile(path) and path.endswith('.json'):
                    try:
                        # Verwende den Controller zum Laden
                        success = self.controller.lade_charakter_von_json(path)
                        
                        if success:
                            # Bei Erfolg: Dateipfad bereits im Controller gespeichert, UI aktualisieren
                            Logger.info(f"Charakter aus Datei geladen: {path}")
                            self.aktualisiere_ui()
                            
                            # Erfolgsmeldung anzeigen
                            self._show_success_dialog(
                                "Charakter erfolgreich geladen", 
                                f"Der Charakter wurde aus der Datei geladen."
                            )
                        else:
                            self._show_error_dialog(
                                "Fehler beim Laden des Charakters. Prüfe die Konsole für Details."
                            )
                    except Exception as e:
                        Logger.error(f"Unbehandelter Fehler beim Laden des Charakters: {str(e)}", exc_info=True)
                        self._show_error_dialog(
                            f"Kritischer Fehler beim Laden des Charakters: {str(e)}\n"
                            "Der Charakter konnte nicht geladen werden."
                        )
                else:
                    # Wenn ein Verzeichnis oder keine JSON-Datei ausgewählt wurde
                    if os.path.isdir(path):
                        self._show_error_dialog("Bitte wähle eine .json Charakterdatei aus.")
                    else:
                        self._show_error_dialog(f"Die ausgewählte Datei ist keine gültige JSON-Datei: {os.path.basename(path)}")
            
            elif self.current_action == "save_pdf_dir":
                # Logik für das Speichern von PDFs
                if os.path.isdir(path):
                    # Vollständigen Pfad zusammensetzen
                    full_path = os.path.join(path, self.temp_pdf_filename)
                    
                    # Prüfen, ob die Datei bereits existiert
                    if os.path.exists(full_path):
                        self.confirm_pdf_overwrite(full_path)
                    else:
                        # Direkt PDF erstellen
                        self.save_pdf_to_path(full_path)
                else:
                    # Wenn eine Datei statt eines Verzeichnisses ausgewählt wurde
                    self._show_error_dialog("Bitte wähle ein Verzeichnis für die Speicherung aus.")

            else:
                # Unbekannter Aktionstyp - Warnung loggen
                Logger.warning(f"Unbekannter Aktionstyp in select_path: {self.current_action}")
                
        except Exception as e:
            Logger.error(f"Fehler bei der Verarbeitung des ausgewählten Pfads: {str(e)}", exc_info=True)
            self._show_error_dialog(f"Fehler bei der Verarbeitung: {str(e)}")

    def lade_charakter(self):
        """Öffnet den MDFileManager im Laden-Modus."""
        # Verzeichnis für Charaktere bestimmen
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        chars_dir = os.path.join(base_dir, 'chars')
        if not os.path.exists(chars_dir):
            os.makedirs(chars_dir)
        
        # Erweiterten FileManager mit Laufwerksauswahl anzeigen
        self.show_file_manager(chars_dir, "load")

       
    def _open_directory_browser_for_save(self):
        """
        Öffnet den Dateibrowser um das Zielverzeichnis zum Speichern auszuwählen.
        Der Dateiname wurde bereits in self.temp_filename gespeichert.
        """
        # Verzeichnis für Charaktere bestimmen
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        chars_dir = os.path.join(base_dir, 'chars')
        if not os.path.exists(chars_dir):
            os.makedirs(chars_dir)
        
        # Erweiterten FileManager mit Laufwerksauswahl anzeigen
        self.show_file_manager(chars_dir, "save_dir")

    def _show_error_dialog(self, message):
        """Zeigt einen Fehlerdialog mit der angegebenen Nachricht an."""
        error_dialog = MDDialog(
            MDDialogHeadlineText(text="Fehler"),
            MDBoxLayout(
                orientation="vertical",
                spacing=10,
                padding=20,
                adaptive_height=True,
                children=[
                    MDLabel(
                        text=message,
                        size_hint_y=None,
                        height=60
                    )
                ]
            ),
            MDDialogButtonContainer(
                MDButton(
                    style="text",
                    on_release=lambda x: error_dialog.dismiss(),
                    children=[
                        MDButtonText(text="OK")
                    ]
                ),
                spacing="8dp",
            ),
        )
        error_dialog.open()

    def _show_success_dialog(self, title, message):
        """Zeigt einen Erfolgsdialog mit der angegebenen Nachricht an."""
        success_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDBoxLayout(
                orientation="vertical",
                spacing=10,
                padding=20,
                adaptive_height=True,
                children=[
                    MDLabel(
                        text=message,
                        size_hint_y=None,
                        height=60
                    )
                ]
            ),
            MDDialogButtonContainer(
                MDButton(
                    style="text",
                    on_release=lambda x: success_dialog.dismiss(),
                    children=[
                        MDButtonText(text="OK")
                    ]
                ),
                spacing="8dp",
            ),
        )
        success_dialog.open()

    def confirm_overwrite(self, filepath):
        """
        Fragt nach Bestätigung zum Überschreiben einer vorhandenen Datei.
        
        Args:
            filepath (str): Vollständiger Pfad zur Datei
        """
        content = MDBoxLayout(orientation='vertical', spacing=10, padding=20, adaptive_height=True)
        
        content.add_widget(MDLabel(
            text=f"Die Datei '{os.path.basename(filepath)}' existiert bereits. Überschreiben?",
            size_hint_y=None,
            height=30
        ))
        
        # Buttons-Container
        buttons = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=50,
            pos_hint={'right': 1}
        )
        
        # Nein-Button
        no_button = MDButton(
            on_release=lambda x: self.close_overwrite_dialog(),
            style="elevated",
            size_hint_x=None,
            width=100
        )
        no_button.add_widget(MDButtonText(text="Nein"))
        
        # Ja-Button
        yes_button = MDButton(
            on_release=lambda x: self.do_overwrite(filepath),
            style="elevated",
            size_hint_x=None,
            width=100
        )
        yes_button.add_widget(MDButtonText(text="Ja"))
        
        buttons.add_widget(no_button)
        buttons.add_widget(yes_button)
        content.add_widget(buttons)
        
        headline = MDDialogHeadlineText(text="Bestätigung")
        
        self.overwrite_dialog = MDDialog(
            md_bg_color=self.theme_cls.surfaceColor
        )
        self.overwrite_dialog.add_widget(headline)
        self.overwrite_dialog.add_widget(content)
        self.overwrite_dialog.open()

    def close_overwrite_dialog(self):
        """Schließt den Überschreiben-Dialog"""
        if hasattr(self, 'overwrite_dialog') and self.overwrite_dialog:
            self.overwrite_dialog.dismiss()

    def do_overwrite(self, filepath):
        """
        Überschreibt die Datei direkt ohne weitere Bestätigung.
        
        Args:
            filepath (str): Vollständiger Pfad zur Datei
        """
        if hasattr(self, 'overwrite_dialog') and self.overwrite_dialog:
            self.overwrite_dialog.dismiss()
        
        self.save_character_to_path(filepath)

    def save_file_with_name(self, directory, filename):
        """
        Speichert den Charakter mit dem angegebenen Dateinamen.
        
        Args:
            directory (str): Verzeichnispfad
            filename (str): Dateiname
        """
        if hasattr(self, 'filename_dialog') and self.filename_dialog:
            self.filename_dialog.dismiss()
        
        # Dateiendung hinzufügen, falls nicht vorhanden
        if not filename.endswith('.json'):
            filename += '.json'
        
        full_path = os.path.join(directory, filename)
        
        # Existiert die Datei bereits?
        if os.path.exists(full_path):
            self.confirm_overwrite(full_path)
        else:
            self.save_character_to_path(full_path)

    def ask_filename_for_save(self, directory_path, default_filename="charakter.json"):
        """
        Zeigt einen Dialog an, um den Dateinamen für das Speichern abzufragen.
        
        Args:
            directory_path (str): Pfad zum ausgewählten Verzeichnis
            default_filename (str): Vorgeschlagener Dateiname
        """
        content = MDBoxLayout(orientation='vertical', spacing=10, padding=20, adaptive_height=True)
        
        content.add_widget(MDLabel(
            text="Dateiname eingeben:",
            size_hint_y=None,
            height=30
        ))
        
        filename_input = MDTextField(
            text=default_filename,
            size_hint_y=None,
            height=50
        )
        content.add_widget(filename_input)
        
        # Buttons-Container
        buttons = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=50,
            pos_hint={'right': 1}
        )
        
        # Abbrechen-Button
        cancel_button = MDButton(
            on_release=lambda x: self.close_filename_dialog(),
            style="elevated",
            size_hint_x=None,
            width=120
        )
        cancel_button.add_widget(MDButtonText(text="Abbrechen"))
        
        # Speichern-Button
        save_button = MDButton(
            on_release=lambda x: self.save_file_with_name(directory_path, filename_input.text),
            style="elevated",
            size_hint_x=None,
            width=120
        )
        save_button.add_widget(MDButtonText(text="Speichern"))
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(save_button)
        content.add_widget(buttons)
        
        # Create dialog with MDDialogHeadlineText
        headline = MDDialogHeadlineText(text="Dateinamen eingeben")
        
        self.filename_dialog = MDDialog(
            md_bg_color=self.theme_cls.surfaceColor
        )
        self.filename_dialog.add_widget(headline)
        self.filename_dialog.add_widget(content)
        self.filename_dialog.open()

    def close_filename_dialog(self):
        """Schließt den Dateiname-Dialog"""
        if hasattr(self, 'filename_dialog') and self.filename_dialog:
            self.filename_dialog.dismiss()

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
        """
        Zeigt einen Dialog mit Optionen zum Speichern des Charakters als PDF.
        Verwendet die gleiche Dialog-Struktur wie beim Speichern von Charakteren.
        """
        # Prüfen, ob bereits eine PDF-Datei existiert (gleicher Name wie Charakter)
        hat_bereits_pdf = False
        default_pdf_name = ""
        
        if hasattr(self.controller, 'current_character_file_path') and self.controller.current_character_file_path:
            # Aus dem aktuellen Charakter-Pfad einen PDF-Pfad ableiten
            char_path = self.controller.current_character_file_path
            default_pdf_name = os.path.splitext(os.path.basename(char_path))[0] + ".pdf"
            default_pdf_path = os.path.join(os.path.dirname(char_path), default_pdf_name)
            hat_bereits_pdf = os.path.exists(default_pdf_path)
        else:
            # Wenn kein Charakter-Pfad existiert, leite Namen vom Charakternamen ab
            character_name = self.controller.charakter.char_name if self.controller.charakter.char_name else "charakter"
            default_pdf_name = f"{character_name.strip().replace(' ', '_')}.pdf"
        
        buttons_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            adaptive_height=True
        )
        
        # Checkbox für druckerfreundliche Version
        checkbox_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(16),
            size_hint_y=None,
            height=dp(48)
        )
        
        self.printer_friendly_checkbox = MDCheckbox(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={"center_y": .5}
        )
        
        checkbox_container.add_widget(self.printer_friendly_checkbox)
        checkbox_container.add_widget(MDLabel(
            text="Druckerfreundliche Version (ohne Hintergrund)",
            size_hint_x=1,
            pos_hint={"center_y": .5}
        ))
        
        buttons_container.add_widget(checkbox_container)
        
        # Wenn eine PDF existiert, zeige den Überschreiben-Button
        if hat_bereits_pdf:
            info_label = MDLabel(
                text=f"Bestehende PDF-Datei: {default_pdf_name}",
                size_hint_y=None,
                height=dp(40)
            )
            buttons_container.add_widget(info_label)
            
            # Button zum Überschreiben
            ueberschreiben_button = MDButton(
                style="elevated",
                size_hint=(1, None),
                height=dp(50),
                on_release=lambda x: self._ueberschreibe_existierende_pdf(default_pdf_path)
            )
            ueberschreiben_button.add_widget(MDButtonText(text="Bestehende PDF-Datei überschreiben"))
            buttons_container.add_widget(ueberschreiben_button)
            
            # Abstandshalter
            spacer = Widget(size_hint_y=None, height=dp(20))
            buttons_container.add_widget(spacer)
        
        # Button für "Als neue PDF-Datei speichern"
        new_file_button = MDButton(
            style="elevated",
            size_hint=(1, None),
            height=dp(50),
            on_release=lambda x: self._als_neue_pdf_speichern(default_pdf_name)
        )
        new_file_button.add_widget(MDButtonText(text="Als neue PDF-Datei speichern..."))
        buttons_container.add_widget(new_file_button)
        
        # Dialog erstellen
        self.pdf_options_dialog = MDDialog(
            MDDialogHeadlineText(text="PDF erstellen"),
            MDDialogContentContainer(
                buttons_container,
                orientation="vertical",
                padding="16dp"
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self.pdf_options_dialog.dismiss()
                )
            )
        )
        self.pdf_options_dialog.open()

    def _ueberschreibe_existierende_pdf(self, pdf_path):
        """
        Überschreibt eine bestehende PDF-Datei direkt.
        
        Args:
            pdf_path (str): Vollständiger Pfad zur vorhandenen PDF-Datei
        """
        self.pdf_options_dialog.dismiss()
        
        # PDF generieren mit dem ausgewählten Pfad
        printer_friendly = self.printer_friendly_checkbox.active
        success = generiere_pdf(self.controller.charakter, pdf_path, printer_friendly)
        
        if success:
            self._show_success_dialog("PDF erstellen erfolgreich", f"PDF wurde gespeichert als:\n{pdf_path}")
        else:
            self._show_error_dialog(f"Fehler beim Erstellen der PDF-Datei: {pdf_path}")

    def _als_neue_pdf_speichern(self, default_filename):
        """
        Zeigt einen Dialog zum Eingeben eines Dateinamens für die neue PDF.
        
        Args:
            default_filename (str): Vorgeschlagener Dateiname für die PDF
        """
        self.pdf_options_dialog.dismiss()
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            padding=dp(16),
            adaptive_height=True
        )
        
        content.add_widget(MDLabel(
            text="Dateiname für neue PDF-Datei:",
            size_hint_y=None,
            height=dp(30)
        ))
        
        filename_input = MDTextField(
            text=default_filename,
            hint_text="Dateiname.pdf",
            mode="outlined"
        )
        content.add_widget(filename_input)
        
        # Dialog zum Eingeben des Dateinamens
        self.pdf_filename_dialog = MDDialog(
            MDDialogHeadlineText(text="Als neue PDF-Datei speichern"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self.pdf_filename_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Speicherort wählen"),
                    style="text",
                    on_release=lambda x: self._continue_save_new_pdf(filename_input.text)
                )
            )
        )
        self.pdf_filename_dialog.open()

    def _continue_save_new_pdf(self, filename):
        """
        Setzt den Speicherprozess für die PDF mit Dateiauswahl fort.
        
        Args:
            filename (str): Der vom Benutzer eingegebene Dateiname für die PDF
        """
        self.pdf_filename_dialog.dismiss()
        
        # Prüfe, ob ein gültiger Dateiname eingegeben wurde
        if not filename or not filename.strip():
            self._show_error_dialog("Bitte gib einen Dateinamen ein.")
            return
        
        # Stellt sicher, dass die Dateiendung .pdf ist
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        # Speichern des Druckerfreundlich-Status und Dateinamens
        self.temp_pdf_filename = filename
        self.temp_printer_friendly = self.printer_friendly_checkbox.active
        
        # Öffne den Dateibrowser für die Verzeichnisauswahl
        self._open_directory_browser_for_pdf_save()

    def _open_directory_browser_for_pdf_save(self):
        """
        Öffnet den Dateibrowser um das Zielverzeichnis für die PDF zum Speichern auszuwählen.
        Der Dateiname und die PDF-Einstellungen wurden bereits gespeichert.
        """
        # Verzeichnis für Charaktere bestimmen
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        chars_dir = os.path.join(base_dir, 'chars')
        if not os.path.exists(chars_dir):
            os.makedirs(chars_dir)
        
        # Setze aktuellen Aktionstyp auf Verzeichnisauswahl für PDF-Speichern
        self.current_action = "save_pdf_dir"
        
        # MDFileManager anzeigen - nur für Verzeichnisauswahl
        self.file_manager.show(chars_dir)
        self.manager_open = True

    def confirm_pdf_overwrite(self, filepath):
        """
        Fragt nach Bestätigung zum Überschreiben einer vorhandenen PDF-Datei.
        
        Args:
            filepath (str): Vollständiger Pfad zur PDF-Datei
        """
        content = MDBoxLayout(orientation='vertical', spacing=10, padding=20, adaptive_height=True)
        
        content.add_widget(MDLabel(
            text=f"Die PDF-Datei '{os.path.basename(filepath)}' existiert bereits. Überschreiben?",
            size_hint_y=None,
            height=30
        ))
        
        # Buttons-Container
        buttons = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=50,
            pos_hint={'right': 1}
        )
        
        # Nein-Button
        no_button = MDButton(
            on_release=lambda x: self.close_pdf_overwrite_dialog(),
            style="elevated",
            size_hint_x=None,
            width=100
        )
        no_button.add_widget(MDButtonText(text="Nein"))
        
        # Ja-Button
        yes_button = MDButton(
            on_release=lambda x: self.do_pdf_overwrite(filepath),
            style="elevated",
            size_hint_x=None,
            width=100
        )
        yes_button.add_widget(MDButtonText(text="Ja"))
        
        buttons.add_widget(no_button)
        buttons.add_widget(yes_button)
        content.add_widget(buttons)
        
        headline = MDDialogHeadlineText(text="Bestätigung")
        
        self.pdf_overwrite_dialog = MDDialog(
            md_bg_color=self.theme_cls.surfaceColor
        )
        self.pdf_overwrite_dialog.add_widget(headline)
        self.pdf_overwrite_dialog.add_widget(content)
        self.pdf_overwrite_dialog.open()

    def close_pdf_overwrite_dialog(self):
        """Schließt den PDF-Überschreiben-Dialog"""
        if hasattr(self, 'pdf_overwrite_dialog') and self.pdf_overwrite_dialog:
            self.pdf_overwrite_dialog.dismiss()

    def do_pdf_overwrite(self, filepath):
        """
        Überschreibt die PDF-Datei direkt ohne weitere Bestätigung.
        
        Args:
            filepath (str): Vollständiger Pfad zur PDF-Datei
        """
        if hasattr(self, 'pdf_overwrite_dialog') and self.pdf_overwrite_dialog:
            self.pdf_overwrite_dialog.dismiss()
        
        # PDF generieren
        printer_friendly = self.temp_printer_friendly
        success = generiere_pdf(self.controller.charakter, filepath, printer_friendly)
        
        if success:
            self._show_success_dialog("PDF erstellen erfolgreich", f"PDF wurde gespeichert als:\n{filepath}")
        else:
            self._show_error_dialog(f"Fehler beim Erstellen der PDF-Datei: {filepath}")

    def save_pdf_to_path(self, full_path):
        """
        Erstellt die PDF an dem angegebenen Pfad.
        
        Args:
            full_path (str): Vollständiger Pfad inkl. Dateiname für die PDF
        """
        try:
            # PDF generieren
            printer_friendly = self.temp_printer_friendly
            success = generiere_pdf(self.controller.charakter, full_path, printer_friendly)
            
            if success:
                self._show_success_dialog("PDF erstellen erfolgreich", f"PDF wurde gespeichert als:\n{full_path}")
            else:
                self._show_error_dialog(f"Fehler beim Erstellen der PDF-Datei.")
        except Exception as e:
            self._show_error_dialog(f"Fehler beim Erstellen der PDF-Datei: {str(e)}")

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