"""
main.py: SW_Charakter_GeneratorApp mit KivyMD Tabs, Carousel, GenerationPointsBar und Logger.
"""

import sys
import os
import logging
from functools import partial

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.theming import ThemableBehavior

from kivymd.app import MDApp
from kivymd.uix.tab import (
    MDTabsPrimary,
    MDTabsItem,
    MDTabsItemIcon,
    MDTabsItemText,
    MDTabsCarousel,
)

from controllers.charakter_controller import CharakterController
from charakter import Charakter
from views.pointbar_view import GenerationPointsBar
from einstellungen import EinstellungenWidget
from views.filechooser_popup import FileChooserPopup
from views.voelker_view import VoelkerWidget
from views.profil_view import ProfilWidget
from views.maechte_view import MaechteWidget
from views.ausruestung_view import AusruestungWidget
from views.handicaps_view import HandicapsWidget
from views.talente_view import TalenteWidget
from views.eigenschaften_view import EigenschaftenWidget
from views.charakterbogen_view import CharakterbogenWidget


class Charakter:
    def speichern_als_json(self, path):
        Logger.info(f"Charakter gespeichert unter: {path}")

class GenerationPointsBar(MDBoxLayout):
    charakter = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(MDLabel(text="Generation Points: 100", halign="center"))

class EinstellungenWidget(MDBoxLayout):
    pass

class VoelkerWidget(MDBoxLayout):
    pass

class ProfilWidget(MDBoxLayout):
    pass

class MaechteWidget(MDBoxLayout):
    pass

class AusruestungWidget(MDBoxLayout):
    pass

class HandicapsWidget(MDBoxLayout):
    pass

class TalenteWidget(MDBoxLayout):
    pass

class EigenschaftenWidget(MDBoxLayout):
    pass

class CharakterbogenWidget(MDBoxLayout):
    pass

# -----------------------------
# CustomTabsItem mit 'title' Property
# -----------------------------

class CustomTabsItem(MDTabsItem):
    """
    Eine benutzerdefinierte MDTabsItem-Klasse, die ein 'title'-Attribut hinzufügt.
    """
    title = StringProperty("")

    def __init__(self, **kwargs):
        # Pop 'title' aus kwargs, um es nicht an die Basisklasse weiterzugeben
        self.title = kwargs.pop('title', "")
        super().__init__(**kwargs)
        # Setze das 'title' Attribut basierend auf 'MDTabsItemText'
        for child in self.children:
            if isinstance(child, MDTabsItemText):
                self.title = child.text
                break

# -----------------------------
# Screen-Klassen
# -----------------------------

class EinstellungenScreen(MDScreen):
    pass

class VoelkerScreen(MDScreen):
    pass

class ProfilScreen(MDScreen):
    pass

class EigenschaftenScreen(MDScreen):
    pass

class HandicapsScreen(MDScreen):
    pass

class TalenteScreen(MDScreen):
    pass

class MaechteScreen(MDScreen):
    pass

class AusruestungScreen(MDScreen):
    pass

class CharakterbogenScreen(MDScreen):
    pass

class InfoScreen(MDScreen):
    info_text = StringProperty("""
    Lizenz- und Urheberrechtsinformationen
    Savage Worlds Fan-Produkt

    „Dieses Produkt bezieht sich auf das Regelsystem Savage Worlds, 
    erhältlich bei der Pinnacle Entertainment Group unter www.peginc.com. 
    Savage Worlds und alle zugehörigen Logos und Warenzeichen sind 
    urheberrechtlich geschützt durch die Pinnacle Entertainment Group. 
    Verwendung mit Genehmigung. Die deutsche Übersetzung der 
    Begrifflichkeiten von Ulisses Spiele darf verwendet werden. 
    Pinnacle oder Ulisses Spiele geben keine Zusicherungen oder 
    Garantien in Bezug auf die Qualität, Funktionsfähigkeit oder 
    Eignung dieses Produkts für einen bestimmten Zweck.“

    „This game references the Savage Worlds game system, 
    available from Pinnacle Entertainment Group at www.peginc.com. 
    Savage Worlds and all associated logos and trademarks are copyrights 
    of Pinnacle Entertainment Group. Used with permission.
    Pinnacle makes no representation or warranty as to the quality, 
    viability, or suitability for purpose of this product.“

    Danksagungen: 
    Vielen Dank an Ulisses Spiele für die Genehmigung der App.
    Danke an die Pinnacle Entertainment Group für dieses großartige Rollenspiel
    und an Ulisses Spiele für die Übersetzung ins Deutsche.
    Besonderer Dank gilt allen Testusern, die fleißig Bugs gesammelt und 
    tolle Anregungen geliefert haben. 
    Danke an alle Savage-Fans, die dem Spiel Leben einhauchen.

    Links:
    Ulisses E-Book-Store https://www.ulisses-ebooks.de/browse.php?sort=4a&src=fid45795&filters=45795_0_0

    Haftungsausschluss:
    Alle Urheberrechte an Charakteren, Fahrzeugen und anderen Regeln und Settings 
    liegen bei den jeweiligen Rechteinhabern. 
    Diese Anwendung erhebt keinen Anspruch auf diese Inhalte.
    """)

# -----------------------------
# Logger-Handler
# -----------------------------

class GUIHandler(logging.Handler):
    def __init__(self, logger_widget, **kwargs):
        super().__init__(**kwargs)
        self.logger_widget = logger_widget
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        msg = self.format(record)
        Clock.schedule_once(lambda dt: self.update_gui(msg), 0)

    def update_gui(self, msg):
        lines = self.logger_widget.text.splitlines()
        lines.append(msg)
        self.logger_widget.text = "\n".join(lines[-15:])  # Letzte 10 Zeilen anzeigen

# -----------------------------
# KV-Layout
# -----------------------------

kv = '''
#:import MDDivider kivymd.uix.divider.MDDivider

<EinstellungenScreen>:
    EinstellungenWidget:
        id: einstellungen_widget

<VoelkerScreen>:
    VoelkerWidget:
        id: voelker_widget

<ProfilScreen>:
    ProfilWidget:
        id: profil_widget

<EigenschaftenScreen>:
    EigenschaftenWidget:
        id: eigenschaften_widget

<HandicapsScreen>:
    HandicapsWidget:
        id: handicaps_widget

<TalenteScreen>:
    TalenteWidget:
        id: talente_widget

<MaechteScreen>:
    MaechteWidget:
        id: maechte_widget

<AusruestungScreen>:
    AusruestungWidget:
        id: ausruestung_widget

<CharakterbogenScreen>:
    CharakterbogenWidget:
        id: charakterbogen_widget

<InfoScreen>:
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(10)

    ScrollView:
        do_scroll_x: False
        do_scroll_y: True

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            md_bg_color: app.theme_cls.backgroundColor
            height: self.minimum_height
            padding: dp(10)
            spacing: dp(10)

            MDLabel:
                text: root.info_text
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'left'
                valign: 'top'

MDScreen:
    # Wir packen alles in eine einzige vertikale MDBoxLayout-Struktur
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: app.theme_cls.backgroundColor

        # ----------------- (1) OBERE MENÜLEISTE (TABS) -----------------
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(60)  # Höhe der Tabbar
            padding: [30, 0, 0, 0]
            md_bg_color: app.theme_cls.backgroundColor
            MDTabsPrimary:
                id: tabs_bar
                # In "on_start" füllen wir hier MDTabsItem rein.

        # ----------------- (2) POINTBAR -------------------
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(100)
            md_bg_color: app.theme_cls.backgroundColor

            GenerationPointsBar:
                id: generation_points
                charakter: app.controller.charakter

        # ----------------- (3) TAB-INHALT (CAROUSEL) -------------------
        MDBoxLayout:
            orientation: 'vertical'
            id: tab_content_box
            padding: [30, 30, 30, 30]
            size_hint_y: 1  # Füllt den restlichen Platz
            md_bg_color: app.theme_cls.backgroundColor

            MDTabsCarousel:
                id: tabs_carousel
                size_hint: (1, 1)
                # Screens werden dynamisch hinzugefügt.

        # ----------------- (4) LOGGER (unten) -------------------
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(60)
            md_bg_color: app.theme_cls.backgroundColor

            TextInput:
                id: logger_label
                text: "Logger: Keine neuen Nachrichten"
                readonly: True
                multiline: True
                background_color: (0, 0, 0, 0)
                foreground_color: (1, 1, 1, 1)
'''

# -----------------------------
# Haupt-App
# -----------------------------

class SW_Charakter_GeneratorApp(MDApp):
    controller = ObjectProperty(None)
    screens = {}  # Dictionary to hold screen instances

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info("Init SW_Charakter_GeneratorApp")
        self.charakter = Charakter()
        self.controller = CharakterController()
        # Deine Icons + Tab-Texte + zugehörige Screens
        self.tab_definitions = [
            ("cog",              "Einstellungen",  EinstellungenScreen),
            ("account-group",    "Völker",         VoelkerScreen),
            ("account-details",          "Profil",         ProfilScreen),
            ("arm-flex",         "Eigenschaften",  EigenschaftenScreen),
            ("account-alert",    "Handicaps",      HandicapsScreen),
            ("star-circle",      "Talente",        TalenteScreen),
            ("creation-outline", "Mächte",         MaechteScreen),
            ("shield-sword",     "Ausrüstung",     AusruestungScreen),
            ("account",  "Charakter",      CharakterbogenScreen),
            ("information",      "Info",           InfoScreen),
        ]

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.primary_color = (1.0, 0.596, 0.0, 1.0)  # Orange
        return Builder.load_string(kv)

    def on_start(self):
        # Fenster maximieren
        Window.maximize()

        # Logger binden
        logger_widget = self.root.ids.logger_label
        log_handler = GUIHandler(logger_widget)
        Logger.addHandler(log_handler)
        Logger.info("Logger eingerichtet.")

        # Tabbar & Carousel referenzieren
        tabs_bar = self.root.ids.tabs_bar
        carousel = self.root.ids.tabs_carousel

        # Initialize screens dictionary
        self.screens = {}

        # Build tabs and screens
        for icon_str, tab_text, ScreenClass in self.tab_definitions:
            # Create Tab Item
            tab_item = CustomTabsItem(title=tab_text)
            tab_item.add_widget(MDTabsItemIcon(icon=icon_str))
            tab_item.add_widget(MDTabsItemText(text=tab_text))
            tabs_bar.add_widget(tab_item)

            # Create screen instance and add to carousel
            screen_instance = ScreenClass()
            carousel.add_widget(screen_instance)
            self.screens[tab_text] = screen_instance  # Store screen in dictionary

        # Binde Mausklick => on_tab_switch
        tabs_bar.bind(on_tab_switch=self.on_tab_switch)

        # Binde Pfeiltasten
        Window.bind(on_key_down=self.on_key_down)

        # Optional: Ersten Tab aktivieren
        if self.tab_definitions:
            # Suche das erste CustomTabsItem
            first_tab = None
            for tab in reversed(tabs_bar.children):  # Da children in Kivy reversed sind
                if isinstance(tab, CustomTabsItem):
                    first_tab = tab
                    break
            if first_tab:
                first_tab.active = True
                Logger.info(f"Erster Tab '{first_tab.title}' aktiviert.")
                # Setze den Carousel-Index entsprechend
                carousel.index = 0

    def get_widget_by_tab_text(self, tab_text, widget_id):
        """Retrieve widget by tab text and widget ID."""
        screen = self.screens.get(tab_text)
        if screen:
            widget = screen.ids.get(widget_id)
            if widget:
                return widget
            else:
                Logger.error(f"Widget {widget_id} not found in screen {tab_text}.")
        else:
            Logger.error(f"Screen {tab_text} not found.")
        return None

    # ------- Tab-Wechsel => Aktualisiere Screen und Carousel
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label):
        """
        Wird aufgerufen, wenn ein Tab gewechselt wird.
        - Aktualisiert den Carousel-Index
        - Aktualisiert die UI-Elemente des aktiven Tabs
        
        Args:
            instance_tabs: MDTabsPrimary
            instance_tab: CustomTabsItem 
            instance_tab_label: MDTabsItemLabel
        """
        # Zugriff auf den Tab-Titel
        tab_title = getattr(instance_tab, 'title', 'Unbekannt')
        Logger.info(f"Tab-Wechsel zu: {tab_title}")

        # Finde den Index des aktiven Tabs
        index = next((i for i, tab in enumerate(self.tab_definitions) if tab[1] == tab_title), 0)

        # Setze den Carousel-Index
        self.root.ids.tabs_carousel.index = index
        
        try:
            # Tab-spezifische Aktualisierungen
            if tab_title == 'Eigenschaften':
                widget = self.get_widget_by_tab_text('Eigenschaften', 'eigenschaften_widget')
                if widget:
                    widget.update_eigenschaften()
            elif tab_title == 'Ausrüstung':
                widget = self.get_widget_by_tab_text('Ausrüstung', 'ausruestung_widget')
                if widget:
                    widget.refresh_widget()
            elif tab_title == 'Profil':
                widget = self.get_widget_by_tab_text('Profil', 'profil_widget')
                if widget:
                    widget.load_profil()
            elif tab_title == 'Völker':
                widget = self.get_widget_by_tab_text('Völker', 'voelker_widget')
                if widget:
                    widget.aktualisiere_ui()
            elif tab_title == 'Talente':
                widget = self.get_widget_by_tab_text('Talente', 'talente_widget')
                if widget:
                    widget.refresh_widget()
            elif tab_title == 'Mächte':
                widget = self.get_widget_by_tab_text('Mächte', 'maechte_widget')
                if widget:
                    widget.refresh_widget()
            elif tab_title == 'Handicaps':
                widget = self.get_widget_by_tab_text('Handicaps', 'handicaps_widget')
                if widget:
                    widget.refresh_widget()
            elif tab_title == 'Charakter':
                widget = self.get_widget_by_tab_text('Charakter', 'charakterbogen_widget')
                if widget:
                    widget.update_overview(0)
                    
            Logger.info(f"UI-Aktualisierung für Tab {tab_title} erfolgreich")
                    
        except Exception as e:
            Logger.error(f"Fehler bei UI-Aktualisierung für Tab {tab_title}: {str(e)}", exc_info=True)

    # ------- Pfeiltasten => tabs wechseln
    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 276:  # Links Pfeil
            self.switch_tab_relative(-1)
        elif key == 275:  # Rechts Pfeil
            self.switch_tab_relative(1)
        return False  # Weitergabe des Events

    def switch_tab_relative(self, direction):
        """
        Wechselt den Tab im Carousel um +1 oder -1.
        """
        carousel = self.root.ids.tabs_carousel
        new_idx = carousel.index + direction
        if 0 <= new_idx < len(carousel.slides):
            carousel.index = new_idx
            Logger.info(f"Carousel-Index geändert auf: {new_idx}")
            # Auch Tab oben markieren (optional)
            tabs_bar = self.root.ids.tabs_bar
            if 0 <= new_idx < len(self.tab_definitions):
                tab_title = self.tab_definitions[new_idx][1]
                # Suche das Tab mit dem entsprechenden Titel
                for tab in reversed(tabs_bar.children):
                    if isinstance(tab, CustomTabsItem) and tab.title == tab_title:
                        tab.active = True
                        Logger.info(f"Tab '{tab.title}' aktiviert via Pfeiltaste.")
                        break

    # ------- Beispiel: Speichern / Laden
    def speichere_charakter(self):
        content = FileChooserPopup(save=True)
        content.bind(on_dismiss=self.dismiss_popup)
        self._popup = Popup(title="Speichere Charakter", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def speichern_datei_ausgewaehlt(self, path, filename):
        if path and filename:
            full_path = os.path.join(path, filename)
            self.charakter.speichern_als_json(full_path)
            Logger.info(f"Charakter gespeichert unter: {full_path}")
        self.dismiss_popup()

    def dismiss_popup(self, *args):
        if hasattr(self, '_popup') and self._popup:
            self._popup.dismiss()

# -----------------------------
# Starte die App
# -----------------------------

if __name__ == "__main__":
    Logger.info("Starte SW_Charakter_GeneratorApp")
    SW_Charakter_GeneratorApp().run()
