# views/profil_view.py

from kivy.lang import Builder
from kivy.app import App
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.logger import Logger
from models.settingregeln import SettingRegeln
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput

import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei (mit Mobile-Unterstützung)
def load_kv_file():
    from utils.platform_utils import is_mobile_layout

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(__file__))

    # Mobile-KV bevorzugen wenn verfügbar
    mobile = is_mobile_layout()
    kv_name = 'profil_view_mobile.kv' if mobile else 'profil_view.kv'
    kv_path = os.path.join(base_path, 'views', kv_name)

    # Fallback auf Desktop-KV wenn Mobile-KV nicht existiert
    if not os.path.exists(kv_path):
        kv_path = os.path.join(base_path, 'views', 'profil_view.kv')

    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
        Logger.info(f"profil_view: KV-Datei geladen: {os.path.basename(kv_path)}")
    else:
        Logger.error(f"profil_view: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class ProfilWidget(MDBoxLayout):
    char_name = StringProperty('')
    alter = StringProperty('')
    geschlecht = StringProperty('')
    konzept = StringProperty('')
    sprachen = StringProperty('')
    settingregeln = ObjectProperty(None)
    charakter = ObjectProperty(None)  

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = App.get_running_app().controller
        self.controller.bind(charakter=self.on_charakter_changed)
        self.controller.bind(on_charakter_loaded=self._on_charakter_loaded)
        self.charakter = self.controller.charakter

        self.bind(
            char_name=self.on_char_name_change,
            alter=self.on_alter_change,
            geschlecht=self.on_geschlecht_change,
            konzept=self.on_konzept_change,
            sprachen=self.on_sprachen_change,
        )

        self.load_profil()
        Logger.info("ProfilWidget initialisiert und an Charakteränderungen gebunden.")
        # self.settingregeln = SettingRegeln()
        # Clock.schedule_once(self.setup_checkboxes)

    # def setup_checkboxes(self, dt):
    #     try:
    #         self.ids.checkbox_container.clear_widgets()
    #     except KeyError:
    #         Logger.error("Fehler: 'checkbox_container' ID nicht im KV-File gefunden.")
    #         return

    #     for attr, prop in self.settingregeln.__class__.__dict__.items():
    #         if isinstance(prop, BooleanProperty):
    #             regel_label = attr.replace('_', ' ').title()
    #             h_layout = MDBoxLayout(
    #                 orientation='horizontal',
    #                 size_hint_y=None,
    #                 height=40,
    #                 padding=(5, 0),
    #                 spacing=10,
    #                 adaptive_height=True
    #             )

    #             label = MDLabel(
    #                 text=regel_label,
    #                 halign='left',
    #                 theme_text_color="Primary",
    #                 size_hint_x=None,
    #                 width=300
    #             )

    #             checkbox = CheckBox(
    #                 active=getattr(self.settingregeln, attr),
    #                 size_hint_x=None,
    #                 width=50,
    #                 selected_color=self.theme_cls.primary_color
    #             )

    #             def callback(instance, value, attr=attr):
    #                 setattr(self.settingregeln, attr, value)
    #                 Logger.info(f"Settingregel '{attr}' gesetzt auf {value}")

    #             checkbox.bind(active=callback)
    #             h_layout.add_widget(label)
    #             h_layout.add_widget(checkbox)
    #             self.ids.checkbox_container.add_widget(h_layout)

    # Die restlichen Methoden bleiben unverändert
    def on_charakter_changed(self, instance, value):
        self.charakter = value
        if self.charakter:
            self.load_profil()
        else:
            Logger.warning("ProfilWidget: Charakter ist None in on_charakter_changed")

    def _on_charakter_loaded(self, *args):
        """Wird aufgerufen, wenn ein Charakter aus Datei geladen wird."""
        self.charakter = self.controller.charakter
        self.load_profil()

    def on_char_name_change(self, instance, value):
        self.on_field_change('Name', value)

    def on_alter_change(self, instance, value):
        self.on_field_change('Alter', value)

    def on_geschlecht_change(self, instance, value):
        self.on_field_change('Geschlecht', value)

    def on_konzept_change(self, instance, value):
        self.on_field_change('Konzept', value)

    def on_sprachen_change(self, instance, value):
        self.on_field_change('Sprachen', value)
    
    def force_focus(self, field_id):
        """Erzwingt Focus auf ein Textfeld - Android Workaround"""
        try:
            field = self.ids[field_id]
            field.focus = True
        except KeyError:
            Logger.warning(f"ProfilWidget: Textfeld {field_id} nicht gefunden")
    
    def auto_focus_on_tap(self, instance):
        """Automatischer Tab/Focus nach erstem Tap - Android Workaround"""
        from kivy.clock import Clock
        def delayed_focus(dt):
            instance.focus = True
            Logger.info(f"ProfilWidget: Auto-Focus auf {instance.id}")
        Clock.schedule_once(delayed_focus, 0.1)

    def load_profil(self, dt=None):
        try:
            if not self.charakter:
                Logger.error("ProfilWidget: self.charakter ist None in load_profil")
                return

            profil_daten = self.charakter.profil_daten
            self.char_name = profil_daten.get('Name', '')
            self.alter = profil_daten.get('Alter', '')
            self.geschlecht = profil_daten.get('Geschlecht', '')
            self.konzept = profil_daten.get('Konzept', '')
            self.sprachen = profil_daten.get('Sprachen', '')

            # Textfelder direkt aktualisieren (KV-Bindings werden nach User-Eingabe nicht mehr propagiert)
            if hasattr(self, 'ids'):
                if 'name_input' in self.ids:
                    self.ids.name_input.text = self.char_name
                if 'alter_input' in self.ids:
                    self.ids.alter_input.text = self.alter
                if 'geschlecht_input' in self.ids:
                    self.ids.geschlecht_input.text = self.geschlecht
                if 'konzept_input' in self.ids:
                    self.ids.konzept_input.text = self.konzept
                if 'sprachen_input' in self.ids:
                    self.ids.sprachen_input.text = self.sprachen

            Logger.debug("ProfilWidget: Profildaten erfolgreich geladen und UI aktualisiert.")
        except Exception as e:
            Logger.error(f"ProfilWidget: Fehler beim Laden der Profildaten: {e}")

    def on_field_change(self, field_name, value):
        if not self.charakter:
            Logger.warning("ProfilWidget: self.charakter ist None in on_field_change")
            return

        self.charakter.set_profil_daten(field_name, value)