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
from kivymd.uix.selectioncontrol import MDCheckbox

kv = '''
<ProfilWidget>:
    orientation: 'vertical'
    padding: [10, 10, 10, 10]
    spacing: 10
    md_bg_color: self.theme_cls.backgroundColor

    ScrollView:
        do_scroll_x: False
        MDGridLayout:
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            padding: [10, 10, 10, 10]
            spacing: 10

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: '60dp'
                spacing: 10
                adaptive_height: True

                MDLabel:
                    text: "Name:"
                    size_hint_x: None
                    width: 150
                    halign: 'left'
                    theme_text_color: "Primary"

                MDTextField:
                    id: name_input
                    text: root.char_name
                    on_text: root.char_name = self.text
                    multiline: False
                    size_hint_x: None
                    width: 300
                    mode: "outlined"

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: '60dp'
                spacing: 10
                adaptive_height: True

                MDLabel:
                    text: "Alter:"
                    size_hint_x: None
                    width: 150
                    halign: 'left'
                    theme_text_color: "Primary"

                MDTextField:
                    id: alter_input
                    text: root.alter
                    on_text: root.alter = self.text
                    multiline: False
                    size_hint_x: None
                    width: 50
                    mode: "outlined"

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: '60dp'
                spacing: 10
                adaptive_height: True

                MDLabel:
                    text: "Geschlecht:"
                    size_hint_x: None
                    width: 150
                    halign: 'left'
                    theme_text_color: "Primary"

                MDTextField:
                    id: geschlecht_input
                    text: root.geschlecht
                    on_text: root.geschlecht = self.text
                    multiline: False
                    size_hint_x: None
                    width: 100
                    mode: "outlined"

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: '60dp'
                spacing: 10
                adaptive_height: True

                MDLabel:
                    text: "Konzept:"
                    size_hint_x: None
                    width: 150
                    halign: 'left'
                    theme_text_color: "Primary"

                MDTextField:
                    id: konzept_input
                    text: root.konzept
                    on_text: root.konzept = self.text
                    multiline: False
                    size_hint_x: None
                    width: 300
                    mode: "outlined"

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: '60dp'
                spacing: 10
                adaptive_height: True

                MDLabel:
                    text: "Sprachen:"
                    size_hint_x: None
                    width: 150
                    halign: 'left'
                    theme_text_color: "Primary"

                MDTextField:
                    id: sprachen_input
                    text: root.sprachen
                    on_text: root.sprachen = self.text
                    multiline: False
                    size_hint_x: None
                    width: 300
                    mode: "outlined"

            MDLabel:
                text: "Settingregeln"
                size_hint_y: None
                height: 30
                halign: 'left'
                theme_text_color: "Primary"

            MDGridLayout:
                id: checkbox_container
                cols: 1
                size_hint_y: None
                size_hint_x: None
                width: self.minimum_width
                height: self.minimum_height
                spacing: 5
                padding: (0, 10, 0, 10)                    
'''

Builder.load_string(kv)

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
        self.settingregeln = SettingRegeln()
        Clock.schedule_once(self.setup_checkboxes)

    def setup_checkboxes(self, dt):
        try:
            self.ids.checkbox_container.clear_widgets()
        except KeyError:
            Logger.error("Fehler: 'checkbox_container' ID nicht im KV-File gefunden.")
            return

        for attr, prop in self.settingregeln.__class__.__dict__.items():
            if isinstance(prop, BooleanProperty):
                regel_label = attr.replace('_', ' ').title()
                h_layout = MDBoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=40,
                    padding=(5, 0),
                    spacing=10,
                    adaptive_height=True
                )

                label = MDLabel(
                    text=regel_label,
                    halign='left',
                    theme_text_color="Primary",
                    size_hint_x=None,
                    width=300
                )

                checkbox = MDCheckbox(
                    active=getattr(self.settingregeln, attr),
                    size_hint_x=None,
                    width=50,
                    selected_color=self.theme_cls.primary_color
                )

                def callback(instance, value, attr=attr):
                    setattr(self.settingregeln, attr, value)
                    Logger.info(f"Settingregel '{attr}' gesetzt auf {value}")

                checkbox.bind(active=callback)
                h_layout.add_widget(label)
                h_layout.add_widget(checkbox)
                self.ids.checkbox_container.add_widget(h_layout)

    # Die restlichen Methoden bleiben unverändert
    def on_charakter_changed(self, instance, value):
        self.charakter = value
        if self.charakter:
            self.load_profil()
        else:
            Logger.warning("ProfilWidget: Charakter ist None in on_charakter_changed")

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

            Logger.debug("ProfilWidget: Profildaten erfolgreich geladen und UI aktualisiert.")
        except Exception as e:
            Logger.error(f"ProfilWidget: Fehler beim Laden der Profildaten: {e}")

    def on_field_change(self, field_name, value):
        if not self.charakter:
            Logger.warning("ProfilWidget: self.charakter ist None in on_field_change")
            return

        self.charakter.set_profil_daten(field_name, value)