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
from kivy.uix.widget import Widget
from kivy.metrics import dp

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

        # Orientierungs-Tracking für Mobile Landscape
        self._current_orientation = None
        self._debounce_resize_event = None
        self._is_mobile = False

        from utils.platform_utils import is_mobile_layout
        self._is_mobile = is_mobile_layout()

        if self._is_mobile:
            from kivy.core.window import Window
            Window.bind(on_resize=self._on_size_change)
            # Initiale Orientierung prüfen
            Clock.schedule_once(self._check_initial_orientation, 0.1)

        self.load_profil()
        Logger.info("ProfilWidget initialisiert und an Charakteränderungen gebunden.")

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

    # ── Orientierungs-Management (Mobile Landscape) ──

    def _check_initial_orientation(self, dt):
        """Prüft beim Start ob Landscape-Layout nötig ist."""
        from kivy.core.window import Window
        is_landscape = Window.width > Window.height
        if is_landscape:
            self._current_orientation = 'portrait'  # Erzwingt Rebuild
            self._rebuild_for_orientation()
        else:
            self._current_orientation = 'portrait'

    def _on_size_change(self, instance, width, height):
        """Reagiert auf Fenster-/Orientierungswechsel."""
        new_orientation = 'landscape' if width > height else 'portrait'
        if new_orientation != self._current_orientation:
            if self._debounce_resize_event:
                self._debounce_resize_event.cancel()
            self._debounce_resize_event = Clock.schedule_once(
                lambda dt: self._rebuild_for_orientation(), 0.15
            )

    def _rebuild_for_orientation(self):
        """Baut das Layout passend zur aktuellen Orientierung neu auf."""
        from kivy.core.window import Window

        is_landscape = Window.width > Window.height
        new_orientation = 'landscape' if is_landscape else 'portrait'

        # Aktuelle Feldwerte sichern
        field_values = {}
        for field_id in ('name_input', 'alter_input', 'geschlecht_input', 'konzept_input', 'sprachen_input'):
            if field_id in self.ids:
                field_values[field_id] = self.ids[field_id].text

        # Alte Widgets entfernen
        self.clear_widgets()

        if is_landscape:
            self._build_landscape_layout()
        else:
            self._build_portrait_layout()

        # Feldwerte wiederherstellen
        for field_id, text in field_values.items():
            if field_id in self.ids:
                self.ids[field_id].text = text

        self._current_orientation = new_orientation
        Logger.info(f"ProfilWidget: Layout neu gebaut für {new_orientation}")

    def _create_field_group(self, label_text, field_id, hint_text, change_callback):
        """Erstellt eine Feld-Gruppe (Label + TextField) für Mobile-Layout."""
        group = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(70),
            spacing=dp(2),
        )

        label = MDLabel(
            text=label_text,
            size_hint_y=None,
            height=dp(24),
            halign='left',
            theme_text_color="Primary",
            font_size=dp(13),
        )
        group.add_widget(label)

        field = MDTextField(
            hint_text=hint_text,
            size_hint_x=1,
        )
        field.bind(text=change_callback)
        group.add_widget(field)

        # ID registrieren
        self.ids[field_id] = field

        return group

    def _build_portrait_layout(self):
        """Baut das Portrait-Layout auf (einspaltig, wie mobile KV)."""
        self.orientation = 'vertical'

        container = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=[dp(12), dp(8), dp(12), dp(12)],
            spacing=dp(6),
        )

        container.add_widget(self._create_field_group(
            "Name:", "name_input", "Name eingeben",
            lambda inst, val: self.on_char_name_change(self, val)))
        container.add_widget(self._create_field_group(
            "Alter:", "alter_input", "Alter eingeben",
            lambda inst, val: self.on_alter_change(self, val)))
        container.add_widget(self._create_field_group(
            "Geschlecht:", "geschlecht_input", "Geschlecht eingeben",
            lambda inst, val: self.on_geschlecht_change(self, val)))
        container.add_widget(self._create_field_group(
            "Konzept:", "konzept_input", "Konzept eingeben",
            lambda inst, val: self.on_konzept_change(self, val)))
        container.add_widget(self._create_field_group(
            "Sprachen:", "sprachen_input", "Sprachen eingeben",
            lambda inst, val: self.on_sprachen_change(self, val)))

        # Spacer - drückt alle Felder nach oben
        container.add_widget(Widget(size_hint_y=1))

        self.add_widget(container)

    def _build_landscape_layout(self):
        """Baut das Landscape-Layout auf (zweispaltig)."""
        self.orientation = 'vertical'

        container = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, 1),
            padding=[dp(12), dp(8), dp(12), dp(12)],
            spacing=dp(16),
        )

        # Linke Spalte: Name, Alter, Geschlecht
        left_col = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.5,
            spacing=dp(6),
        )
        left_col.add_widget(self._create_field_group(
            "Name:", "name_input", "Name eingeben",
            lambda inst, val: self.on_char_name_change(self, val)))
        left_col.add_widget(self._create_field_group(
            "Alter:", "alter_input", "Alter eingeben",
            lambda inst, val: self.on_alter_change(self, val)))
        left_col.add_widget(self._create_field_group(
            "Geschlecht:", "geschlecht_input", "Geschlecht eingeben",
            lambda inst, val: self.on_geschlecht_change(self, val)))
        left_col.add_widget(Widget(size_hint_y=1))

        # Rechte Spalte: Konzept, Sprachen
        right_col = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.5,
            spacing=dp(6),
        )
        right_col.add_widget(self._create_field_group(
            "Konzept:", "konzept_input", "Konzept eingeben",
            lambda inst, val: self.on_konzept_change(self, val)))
        right_col.add_widget(self._create_field_group(
            "Sprachen:", "sprachen_input", "Sprachen eingeben",
            lambda inst, val: self.on_sprachen_change(self, val)))
        right_col.add_widget(Widget(size_hint_y=1))

        container.add_widget(left_col)
        container.add_widget(right_col)

        self.add_widget(container)

    # ── Charakter-Bindings ──

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