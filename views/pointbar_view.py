# views/pointbar_view.py
# Änderungen:
# - Klasse LabelValuePair als Python-Klasse definiert mit StringProperty.
# - Im KV ist jetzt <LabelValuePair> statt <LabelValuePair@BoxLayout>.

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.logger import Logger

# KivyMD-Imports
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton, MDFabButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
from kivymd.theming import ThemableBehavior

class LabelValuePair(MDBoxLayout):
    key_text = StringProperty("")
    value_text = StringProperty("")

class CharakterGridLayout(MDGridLayout):
    adaptive_height = True

kv = '''
<LabelValuePair>:
    orientation: 'horizontal'
    height: 20
    spacing: 5
    padding: [0, 0, 0, 0]
    md_bg_color: app.theme_cls.backgroundColor

    MDLabel:
        text: root.key_text
        theme_text_color: "Custom"
        text_color: [1, 0.65, 0, 1]  # Orange
        halign: 'left'
        valign: 'middle'
        size_hint_x: None
        width: 200  # Erhöht für längere Labels
        font_size: '10sp'
        shorten: True
        shorten_from: 'right'
        text_size: self.size

    MDLabel:
        text: root.value_text
        theme_text_color: "Custom"
        text_color: [1, 1, 1, 1]  # Weiß
        halign: 'left'
        valign: 'middle'
        size_hint_x: None
        width: 100
        font_size: '10sp'
        shorten: True
        shorten_from: 'right'
        text_size: self.size

<GenerationPointsBar>:
    orientation: 'horizontal'
    spacing: "60dp"  # Mehr Abstand zwischen Logo und Content
    size_hint_y: None
    height: "100dp"
    md_bg_color: app.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: 'horizontal'
        spacing: "20dp"  # Mehr Abstand zwischen den Spalten

        Image:
            source: 'assets/Savage-Worlds-Fanprodukt-Logo.png'
            size_hint: None, None
            size: dp(180), dp(180)  # Anpassung der Bildgröße
            allow_stretch: True
            keep_ratio: True
            pos_hint: {'center_y': 0.5}  # Vertikale Zentrierung

        # Erste Spalte
        MDBoxLayout:
            orientation: 'vertical'
            spacing: "2dp"
            size_hint_x: 0.33
            
            LabelValuePair:
                key_text: "Name:"
                value_text: root.char_name_text
            LabelValuePair:
                key_text: "Setting:"
                value_text: root.active_setting_name_text
            LabelValuePair:
                key_text: "Rang:"
                value_text: root.rang_text
            LabelValuePair:
                key_text: "Aufstiege:"
                value_text: root.aufstiege_text

        # Zweite Spalte
        MDBoxLayout:
            orientation: 'vertical'
            spacing: "2dp"
            size_hint_x: 0.33
            
            LabelValuePair:
                key_text: "Attribute-Punkte:"
                value_text: root.attribut_text
            LabelValuePair:
                key_text: "Fähigkeiten-Punkte:"
                value_text: root.faehigkeiten_text
            LabelValuePair:
                key_text: "Handicap-Punkte:"
                value_text: root.handicaps_text
            LabelValuePair:
                key_text: "Mächte:"
                value_text: root.maechte_text

        # Dritte Spalte
        MDBoxLayout:
            orientation: 'vertical'
            spacing: "2dp"
            size_hint_x: 0.33
            
            LabelValuePair:
                key_text: "Machtpunkte:"
                value_text: root.machtpunkte_text
            LabelValuePair:
                key_text: "Gewicht:"
                value_text: root.gewicht_text
            LabelValuePair:
                key_text: "Vermögen:"
                value_text: root.vermoegen_text
'''
Builder.load_string(kv)

class GenerationPointsBar(MDBoxLayout):
    charakter = ObjectProperty(None)  
    char_name_text = StringProperty("")
    active_setting_name_text = StringProperty("")
    attribut_text = StringProperty("")  
    faehigkeiten_text = StringProperty("")  
    aufstiege_text = StringProperty("")  
    maechte_text = StringProperty("")  
    machtpunkte_text = StringProperty("")  
    vermoegen_text = StringProperty("")  
    handicaps_text = StringProperty("")  
    gewicht_text = StringProperty("")  
    rang_text = StringProperty("")  

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = App.get_running_app().controller
        self.controller.bind(charakter=self.on_charakter_changed)
        self.on_charakter_changed(self.controller, self.controller.charakter)
        Logger.info("GenerationPointsBar initialisiert und an Charakter-Änderungen gebunden.")

    def on_charakter_changed(self, instance, value):
        if hasattr(self, 'charakter') and self.charakter:
            self.unbind_charakter_properties()
        self.charakter = value
        if self.charakter:
            self.bind_charakter_properties()
            self.update_all_texts()

    def unbind_charakter_properties(self):
        # Bindings entfernen, falls nötig
        self.charakter.unbind(verbleibende_attributsteigerungen=self.update_attribut_text)
        self.charakter.unbind(maximale_attributsteigerungen=self.update_attribut_text)
        self.charakter.unbind(verbleibende_fertigkeitssteigerungen=self.update_faehigkeiten_text)
        self.charakter.unbind(maximale_fertigkeitssteigerungen=self.update_faehigkeiten_text)
        self.charakter.unbind(verbleibende_aufstiege=self.update_aufstiege_text)
        self.charakter.unbind(aufstiege_gesamt=self.update_aufstiege_text)
        self.charakter.unbind(verfuegbare_maechte=self.update_maechte_text)
        self.charakter.unbind(machtpunkte=self.update_machtpunkte_text)
        self.charakter.unbind(vermoegen=self.update_vermoegen_text)
        self.charakter.unbind(verbleibende_handicap_punkte=self.update_handicaps_text)
        self.charakter.unbind(gesamt_handicap_punkte=self.update_handicaps_text)
        self.charakter.unbind(gesamtgewicht=self.update_gewicht_text)
        self.charakter.unbind(maximale_traglast=self.update_gewicht_text)
        self.charakter.unbind(rang=self.update_rang_text)
        self.charakter.unbind(char_name=self.update_charakter_name)
        self.charakter.unbind(active_setting_name=self.update_setting_name)
        Logger.info("Alte Charakter-Bindings entfernt.")

    def bind_charakter_properties(self):
        if self.charakter:
            Logger.debug(f"GenerationPointsBar verwendet Charakter-Objekt mit ID {id(self.charakter)}")
            self.charakter.bind(verbleibende_attributsteigerungen=self.update_attribut_text)
            self.charakter.bind(maximale_attributsteigerungen=self.update_attribut_text)
            self.charakter.bind(verbleibende_fertigkeitssteigerungen=self.update_faehigkeiten_text)
            self.charakter.bind(maximale_fertigkeitssteigerungen=self.update_faehigkeiten_text)
            self.charakter.bind(verbleibende_aufstiege=self.update_aufstiege_text)
            self.charakter.bind(aufstiege_gesamt=self.update_aufstiege_text)
            self.charakter.bind(verfuegbare_maechte=self.update_maechte_text)
            self.charakter.bind(machtpunkte=self.update_machtpunkte_text)
            self.charakter.bind(vermoegen=self.update_vermoegen_text)
            self.charakter.bind(waehrungseinheit=self.update_vermoegen_text)
            self.charakter.bind(verbleibende_handicap_punkte=self.update_handicaps_text)
            self.charakter.bind(gesamt_handicap_punkte=self.update_handicaps_text)
            self.charakter.bind(gesamtgewicht=self.update_gewicht_text)
            self.charakter.bind(maximale_traglast=self.update_gewicht_text)
            self.charakter.bind(rang=self.update_rang_text)
            self.charakter.bind(char_name=self.update_charakter_name)
            self.charakter.bind(active_setting_name=self.update_setting_name)
            Logger.info("GenerationPointsBar ist nun mit Charakter-Eigenschaften gebunden.")

    def update_all_texts(self):
        self.char_name_text = self.charakter.char_name if self.charakter.char_name else "Unbekannt"
        self.active_setting_name_text = self.charakter.active_setting_name if self.charakter.active_setting_name else "Unbekanntes Setting"

        self.update_attribut_text(None, None)
        self.update_faehigkeiten_text(None, None)
        self.update_aufstiege_text(None, None)
        self.update_maechte_text(None, None)
        self.update_machtpunkte_text(None, None)
        self.update_vermoegen_text(None, None)
        self.update_handicaps_text(None, None)
        self.update_gewicht_text(None, None)
        self.update_rang_text(None, None)

    def update_charakter_name(self, instance, value):
        self.char_name_text = value if value else "Unbekannt"

    def update_setting_name(self, instance, value):
        self.active_setting_name_text = value if value else "Unbekanntes Setting"

    def update_attribut_text(self, instance, value):
        self.attribut_text = f"{self.charakter.verbleibende_attributsteigerungen} / {self.charakter.maximale_attributsteigerungen}"

    def update_handicaps_text(self, instance, value):
        self.handicaps_text = f"{self.charakter.verbleibende_handicap_punkte} / {self.charakter.gesamt_handicap_punkte}"

    def update_faehigkeiten_text(self, instance, value):
        self.faehigkeiten_text = f"{self.charakter.verbleibende_fertigkeitssteigerungen} / {self.charakter.maximale_fertigkeitssteigerungen}"

    def update_aufstiege_text(self, instance, value):
        self.aufstiege_text = f"{self.charakter.verbleibende_aufstiege} / {self.charakter.aufstiege_gesamt}"

    def update_maechte_text(self, instance, value):
        self.maechte_text = f"{self.charakter.verfuegbare_maechte}"

    def update_machtpunkte_text(self, instance, value):
        self.machtpunkte_text = f"{self.charakter.machtpunkte}"

    def update_vermoegen_text(self, instance, value):
        self.vermoegen_text = f"{self.charakter.vermoegen} {self.charakter.waehrungseinheit}"

    def update_gewicht_text(self, instance, value):
        self.gewicht_text = f"{self.charakter.gesamtgewicht} / {self.charakter.maximale_traglast} kg"

    def update_rang_text(self, instance, value):
        self.rang_text = f"{self.charakter.rang}"
        Logger.debug(f"Rang aktualisiert: {self.rang_text}")
