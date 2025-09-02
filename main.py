"""
main.py: SW_Charakter_GeneratorApp mit KivyMD Tabs, Carousel, GenerationPointsBar und Logger.
KORRIGIERT: Service Container Timing und KV-Datei-Loading
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
from kivy.uix.widget import Widget
import re
import webbrowser

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton, MDButtonText
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
from views.voelker_view import VoelkerWidget
from views.profil_view import ProfilWidget
from views.maechte_view import MaechteWidget
from views.ausruestung_view import AusruestungWidget
from views.handicaps_view import HandicapsWidget
from views.talente_view import TalenteWidget
from views.eigenschaften_view import EigenschaftenWidget
from views.charakterbogen_view import CharakterbogenWidget
from views.einstellungen_widget import EinstellungenWidget
from views.historie_view import HistorieWidget  # NEU: Import des Historie-Widgets

# Config Service für Theme-Speicherung importieren
from services.config_service import ConfigService
from services.service_container import service_container

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')

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

# Benutzerdefinierte Label-Klasse für Hyperlinks
class HyperlinkLabel(MDLabel):
    """
    Eine benutzerdefinierte MDLabel, die Hyperlinks erkennt und öffnet.
    """
    def __init__(self, **kwargs):
        # Aktiviere Markup
        kwargs['markup'] = True
        super().__init__(**kwargs)
        
        # Speicherung für URL-Informationen
        self.url_pattern = re.compile(r'https?://[^\s]+')
        self.urls = []
        self.original_text = ""  # Speichert den Text ohne Markup
        self.hover_cursor = 'hand'
        
        # Einmalige Verarbeitung des Texts
        Clock.schedule_once(self.process_text, 0)
    
    def process_text(self, dt):
        """Verarbeitet den initialen Text, um URLs zu erkennen und zu formatieren."""
        # Originaltext speichern
        self.original_text = self.text
        
        # Wenn kein Text da ist, nichts tun
        if not self.original_text:
            return
        
        # URLs im Text finden
        self.urls = []
        formatted_text = self.original_text
        offset = 0  # Versatz durch hinzugefügte Markup-Tags
        
        for match in self.url_pattern.finditer(self.original_text):
            start, end = match.span()
            url = match.group(0)
            
            # URL in der Liste speichern
            self.urls.append((start, end, url))
            
            # URL im Text formatieren
            markup = f'[color=#3498db][u]{url}[/u][/color]'
            formatted_text = (
                formatted_text[:start+offset] + 
                markup + 
                formatted_text[end+offset:]
            )
            
            # Offset für nächste URL anpassen
            offset += len(markup) - len(url)
        
        # Text mit markierten Links setzen
        if self.urls:
            Logger.info(f"HyperlinkLabel: {len(self.urls)} URLs formatiert")
            self.text = formatted_text
    
    def on_touch_down(self, touch):
        """Erkennt Klicks auf Links und öffnet sie im Browser."""
        if self.collide_point(*touch.pos) and self.urls:
            # Berechne Position im Text
            x_rel = (touch.x - self.x) / self.width
            pos = int(x_rel * len(self.original_text))
            
            # Prüfe, ob auf eine URL geklickt wurde
            for start, end, url in self.urls:
                if start - 5 <= pos <= end + 5:  # Etwas Toleranz für die Klickposition
                    Logger.info(f"Link angeklickt: {url}")
                    webbrowser.open(url)
                    return True
                    
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        """Ändert den Cursor über Links."""
        if self.collide_point(*touch.pos) and self.urls:
            x_rel = (touch.x - self.x) / self.width
            pos = int(x_rel * len(self.original_text))
            
            for start, end, url in self.urls:
                if start - 5 <= pos <= end + 5:
                    Window.set_system_cursor(self.hover_cursor)
                    return True
            
            Window.set_system_cursor('arrow')
        
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        """Setzt den Cursor zurück."""
        Window.set_system_cursor('arrow')
        return super().on_touch_up(touch)

# -----------------------------
# Screen-Klassen mit Delegationsmethoden
# -----------------------------

class EinstellungenScreen(MDScreen):
    def aktualisiere_ui(self):
        """Delegiert an das EinstellungenWidget"""
        try:
            if hasattr(self.ids, 'einstellungen_widget'):
                widget = self.ids.einstellungen_widget
                if widget and hasattr(widget, 'aktualisiere_ui'):
                    widget.aktualisiere_ui()
                    return True
            Logger.warning("EinstellungenWidget oder aktualisiere_ui nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei EinstellungenScreen.aktualisiere_ui: {str(e)}")
            return False

class VoelkerScreen(MDScreen):
    def aktualisiere_ui(self):
        """Delegiert an das VoelkerWidget"""
        try:
            if hasattr(self.ids, 'voelker_widget'):
                widget = self.ids.voelker_widget
                if widget and hasattr(widget, 'aktualisiere_ui'):
                    widget.aktualisiere_ui()
                    return True
            Logger.warning("VoelkerWidget oder aktualisiere_ui nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei VoelkerScreen.aktualisiere_ui: {str(e)}")
            return False

class ProfilScreen(MDScreen):
    def load_profil(self):
        """Delegiert an das ProfilWidget"""
        try:
            if hasattr(self.ids, 'profil_widget'):
                widget = self.ids.profil_widget
                if widget and hasattr(widget, 'load_profil'):
                    widget.load_profil()
                    return True
            Logger.warning("ProfilWidget oder load_profil nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei ProfilScreen.load_profil: {str(e)}")
            return False

class EigenschaftenScreen(MDScreen):
    def update_eigenschaften(self):
        """Delegiert an das EigenschaftenWidget"""
        try:
            if hasattr(self.ids, 'eigenschaften_widget'):
                widget = self.ids.eigenschaften_widget
                if widget and hasattr(widget, 'update_eigenschaften'):
                    widget.update_eigenschaften()
                    return True
            Logger.warning("EigenschaftenWidget oder update_eigenschaften nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei EigenschaftenScreen.update_eigenschaften: {str(e)}")
            return False

class HandicapsScreen(MDScreen):
    def refresh_widget(self):
        """Delegiert an das HandicapsWidget"""
        try:
            if hasattr(self.ids, 'handicaps_widget'):
                widget = self.ids.handicaps_widget
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                    return True
            Logger.warning("HandicapsWidget oder refresh_widget nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei HandicapsScreen.refresh_widget: {str(e)}")
            return False

class TalenteScreen(MDScreen):
    def refresh_widget(self):
        """Delegiert an das TalenteWidget"""
        try:
            if hasattr(self.ids, 'talente_widget'):
                widget = self.ids.talente_widget
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                    return True
            Logger.warning("TalenteWidget oder refresh_widget nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei TalenteScreen.refresh_widget: {str(e)}")
            return False

class MaechteScreen(MDScreen):
    def refresh_widget(self):
        """Delegiert an das MaechteWidget"""
        try:
            if hasattr(self.ids, 'maechte_widget'):
                widget = self.ids.maechte_widget
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                    return True
            Logger.warning("MaechteWidget oder refresh_widget nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei MaechteScreen.refresh_widget: {str(e)}")
            return False

class AusruestungScreen(MDScreen):
    def refresh_widget(self):
        """Delegiert an das AusruestungWidget"""
        try:
            if hasattr(self.ids, 'ausruestung_widget'):
                widget = self.ids.ausruestung_widget
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                    return True
            Logger.warning("AusruestungWidget oder refresh_widget nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei AusruestungScreen.refresh_widget: {str(e)}")
            return False

class CharakterbogenScreen(MDScreen):
    def update_overview(self, *args):
        """Delegiert an das CharakterbogenWidget"""
        try:
            if hasattr(self.ids, 'charakterbogen_widget'):
                widget = self.ids.charakterbogen_widget
                if widget and hasattr(widget, 'update_overview'):
                    widget.update_overview(*args)
                    return True
            Logger.warning("CharakterbogenWidget oder update_overview nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei CharakterbogenScreen.update_overview: {str(e)}")
            return False

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
    Eignung dieses Produkts für einen bestimmten Zweck."

    „This game references the Savage Worlds game system, 
    available from Pinnacle Entertainment Group at www.peginc.com. 
    Savage Worlds and all associated logos and trademarks are copyrights 
    of Pinnacle Entertainment Group. Used with permission.
    Pinnacle makes no representation or warranty as to the quality, 
    viability, or suitability for purpose of this product."

    Danksagungen: 
    Vielen Dank an Ulisses Spiele für die Genehmigung der App.
    Danke an die Pinnacle Entertainment Group für dieses großartige Rollenspiel
    und an Ulisses Spiele für die Übersetzung ins Deutsche.
    Besonderer Dank gilt allen Testusern, die fleißig Bugs gesammelt und 
    tolle Anregungen geliefert haben. 
    Danke an alle Savage-Fans, die dem Spiel Leben einhauchen.

    Links:
    """)
    
    # Liste der Links und deren Beschreibungen
    links = [
        ("Ulisses E-Book-Store", "https://www.ulisses-ebooks.de/browse.php?sort=4a&src=fid45795&filters=45795_0_0"),
        ("Pinnacle Entertainment Group", "https://www.peginc.com"),
        ("Savage Worlds Deutschland", "https://ulisses-spiele.de/game-system/savage-worlds/")
    ]

    def on_kv_post(self, base_widget):
        """Fügt die Link-Buttons hinzu, nachdem das KV geladen wurde."""
        # Container für Links finden
        container = self.ids.link_container
        
        # Container für linksbündige Ausrichtung konfigurieren
        container.spacing = dp(4)
        container.padding = [dp(10), dp(4), dp(10), dp(4)]  # links, oben, rechts, unten
        
        # Für jeden Link einen Button erstellen
        for label, url in self.links:
            btn = MDButton(
                style="elevated",
                size_hint_x=None,  # Keine horizontale Größenbindung
                size_hint_y=None,
                height=dp(50),
                pos_hint={"x": 0},  # Linksbündige Positionierung
                on_release=lambda x, u=url: self.open_link(u)
            )
            # Text als Kind-Widget hinzufügen
            btn_text = MDButtonText(
                text=label,
                padding=[dp(20), 0]  # Seitenpolsterung für den Text
            )
            btn.add_widget(btn_text)
            container.add_widget(btn)
            
            # Nach dem Hinzufügen die Breite des Buttons berechnen
            Clock.schedule_once(lambda dt, btn=btn, lbl=label: self._adjust_button_width(btn, lbl), 0)
        
    def _adjust_button_width(self, button, text):
        """Passt die Breite des Buttons basierend auf der Textlänge an."""
        min_width = dp(200)  # Mindestbreite
        # Ungefähre Berechnung der Textbreite (kann verfeinert werden)
        estimated_width = len(text) * dp(10) + dp(40)  # 10dp pro Zeichen + Padding
        button.width = max(min_width, estimated_width)
            
    def open_link(self, url):
        """Öffnet einen Link im Browser."""
        Logger.info(f"Öffne Link: {url}")
        webbrowser.open(url)

# NEU: HistorieScreen Klasse
class HistorieScreen(MDScreen):
    def refresh_widget(self):
        """Delegiert an das HistorieWidget"""
        try:
            if hasattr(self.ids, 'historie_widget'):
                widget = self.ids.historie_widget
                if widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
                    return True
            Logger.warning("HistorieWidget oder refresh_widget nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler bei HistorieScreen.refresh_widget: {str(e)}")
            return False

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
# KV-Layout wird jetzt aus main.kv geladen
# -----------------------------

# -----------------------------
# Haupt-App
# -----------------------------

class SW_Charakter_GeneratorApp(MDApp):
    controller = ObjectProperty(None)
    screens = {}  # Dictionary to hold screen instances

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info("Init SW_Charakter_GeneratorApp")
        
        # Ressourcen-Extraktion für PyInstaller EXE
        from utils.resource_extractor import resource_extractor
        if not resource_extractor.extract_resources():
            Logger.error("Fehler bei Ressourcen-Extraktion")
        
        # KORRIGIERT: Frühe Controller-Initialisierung für Service Container
        self.charakter = Charakter()
        self.controller = CharakterController()
        
        # Service Container früh initialisieren
        service_container.initialize(self.controller)
        Logger.info("Service Container früh initialisiert")
        
        # Deine Icons + Tab-Texte + zugehörige Screens
        # NEU: Historie-Tab hinzugefügt
        self.tab_definitions = [
            ("cog",              "Einstellungen",  EinstellungenScreen),
            ("account-group",    "Völker",         VoelkerScreen),
            ("account-details",  "Profil",         ProfilScreen),
            ("arm-flex",         "Eigenschaften",  EigenschaftenScreen),
            ("account-alert",    "Handicaps",      HandicapsScreen),
            ("star-circle",      "Talente",        TalenteScreen),
            ("creation-outline", "Mächte",         MaechteScreen),
            ("shield-sword",     "Ausrüstung",     AusruestungScreen),
            ("account",          "Charakter",      CharakterbogenScreen),
            ("history",          "Historie",       HistorieScreen),  # NEU: Historie-Tab
            ("information",      "Info",           InfoScreen),      # INFO-Tab hinzugefügt
        ]

    def build(self):
        # KORRIGIERT: Theme aus Config laden (Service Container ist bereits initialisiert)
        self.load_theme_from_config()
        return Builder.load_file('main.kv')

    def load_theme_from_config(self):
        """Lädt die Theme-Einstellungen aus der Konfiguration"""
        try:
            Logger.info("=== Theme-Laden gestartet ===")
            
            # Config Service aus Service Container holen
            from services.service_container import get_config_service
            config_service = get_config_service()
            
            if not config_service:
                Logger.warning("ConfigService nicht verfügbar, verwende Standard-Theme")
                self.theme_cls.theme_style = "Dark"
                self.theme_cls.primary_palette = "Orange"
                self.theme_cls.primary_color = (1.0, 0.596, 0.0, 1.0)
                return
            
            # Config-Status prüfen
            config_dict = config_service.get_config_dict()
            Logger.info(f"Geladene Config-Daten: {config_dict}")
            
            theme_style = config_service.get('theme_style', 'Dark')
            primary_palette = config_service.get('primary_palette', 'Orange')
            
            Logger.info(f"Gelesene Werte: Style={theme_style}, Palette={primary_palette}")
            
            # Gültige KivyMD-Paletten definieren
            valid_palettes = [
                'Red', 'Pink', 'Purple', 'Deeprurple', 'Indigo', 'Blue', 
                'Lightblue', 'Cyan', 'Teal', 'Green', 'Lightgreen', 'Lime',
                'Yellow', 'Amber', 'Orange', 'Deeporange', 'Brown', 'Gray', 'Bluegray'
            ]
            
            # Palette validieren
            if primary_palette not in valid_palettes:
                Logger.warning(f"Ungültige Palette '{primary_palette}' gefunden, verwende 'Orange'")
                primary_palette = 'Orange'
                # Korrigierte Palette speichern
                config_service.set('primary_palette', primary_palette)
            
            # Theme-Style validieren
            if theme_style not in ['Light', 'Dark']:
                Logger.warning(f"Ungültiger Theme-Style '{theme_style}' gefunden, verwende 'Dark'")
                theme_style = 'Dark'
                config_service.set('theme_style', theme_style)
            
            Logger.info(f"Angewandte Werte: Style={theme_style}, Palette={primary_palette}")
            
            # Theme anwenden
            self.theme_cls.theme_style = theme_style
            self.theme_cls.primary_palette = primary_palette
            
            # Orange-spezifische Farbe setzen, falls Orange gewählt wurde
            if primary_palette == "Orange":
                self.theme_cls.primary_color = (1.0, 0.596, 0.0, 1.0)
                Logger.debug("Orange-spezifische Farbe gesetzt")
                
            Logger.info(f"=== Theme erfolgreich geladen: {theme_style}, {primary_palette} ===")
            
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Theme-Einstellungen: {str(e)}", exc_info=True)
            # Fallback auf Standard-Werte
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Orange"
            self.theme_cls.primary_color = (1.0, 0.596, 0.0, 1.0)
            Logger.info("Fallback-Theme angewendet")

    def update_theme(self, theme_style=None, primary_palette=None):
        """
        Aktualisiert das Theme und speichert die Änderungen in der Konfiguration
        
        Args:
            theme_style (str): 'Light' oder 'Dark'
            primary_palette (str): Name der primären Farbpalette
        """
        try:
            Logger.info(f"=== Theme-Update gestartet: Style={theme_style}, Palette={primary_palette} ===")
            
            # Config Service aus Service Container holen
            from services.service_container import get_config_service
            config_service = get_config_service()
            
            # Gültige KivyMD-Paletten definieren
            valid_palettes = [
                'Red', 'Pink', 'Purple', 'Deeprurple', 'Indigo', 'Blue', 
                'Lightblue', 'Cyan', 'Teal', 'Green', 'Lightgreen', 'Lime',
                'Yellow', 'Amber', 'Orange', 'Deeporange', 'Brown', 'Gray', 'Bluegray'
            ]
            
            changes = {}
            
            if theme_style:
                if theme_style in ['Light', 'Dark']:
                    self.theme_cls.theme_style = theme_style
                    changes['theme_style'] = theme_style
                    Logger.info(f"Theme-Stil geändert zu: {theme_style}")
                else:
                    Logger.warning(f"Ungültiger Theme-Stil: {theme_style}")
            
            if primary_palette:
                # Palette validieren
                if primary_palette in valid_palettes:
                    self.theme_cls.primary_palette = primary_palette
                    changes['primary_palette'] = primary_palette
                    
                    # Spezielle Farbe für Orange setzen
                    if primary_palette == "Orange":
                        self.theme_cls.primary_color = (1.0, 0.596, 0.0, 1.0)
                        Logger.debug("Orange-spezifische Farbe gesetzt")
                    
                    Logger.info(f"Primäre Palette geändert zu: {primary_palette}")
                else:
                    Logger.warning(f"Ungültige Palette '{primary_palette}' ignoriert. Gültige Paletten: {valid_palettes}")
                    return  # Abbrechen wenn ungültige Palette
            
            # Änderungen in der Konfiguration speichern
            if changes and config_service:
                Logger.info(f"Speichere Theme-Änderungen: {changes}")
                config_service.update_multiple(changes, save_immediately=True)
                Logger.info(f"Theme-Einstellungen in Konfiguration gespeichert: {changes}")
                
                # Debug: Verifikation der gespeicherten Werte
                saved_style = config_service.get('theme_style', 'Unknown')
                saved_palette = config_service.get('primary_palette', 'Unknown')
                Logger.info(f"Verifikation - Gespeicherte Werte: Style={saved_style}, Palette={saved_palette}")
            elif not config_service:
                Logger.warning("ConfigService nicht verfügbar, Theme-Änderungen werden nicht gespeichert")
            elif not changes:
                Logger.debug("Keine Theme-Änderungen zu speichern")
            
            Logger.info(f"=== Theme-Update abgeschlossen ===")
                
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Themes: {str(e)}", exc_info=True)

    def get_current_theme_style(self):
        """Gibt den aktuellen Theme-Stil zurück"""
        return self.theme_cls.theme_style

    def get_current_primary_palette(self):
        """Gibt die aktuelle primäre Farbpalette zurück"""
        return self.theme_cls.primary_palette

    def on_start(self):
        Logger.info("=== App-Start gestartet ===")
        
        # KORRIGIERT: Service Container ist bereits in __init__ initialisiert
        Logger.info("Service Container bereits initialisiert")
        
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
            
            # WICHTIG: Widget-Registrierung für Kompatibilität
            self._register_widget_for_compatibility(screen_instance, tab_text)

        # Binde Mausklick => on_tab_switch
        tabs_bar.bind(on_tab_switch=self.on_tab_switch)

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
        
    def debug_config_info(self):
        """Debug-Methode um Config-Informationen anzuzeigen"""
        try:
            Logger.info("=== CONFIG DEBUG INFO ===")
            
            # Config Service holen
            from services.service_container import get_config_service
            config_service = get_config_service()
            
            if config_service:
                # Config-Pfad anzeigen
                config_path = getattr(config_service, '_config_path', 'Unbekannt')
                Logger.info(f"Config-Pfad: {config_path}")
                
                # Config-Inhalt anzeigen
                config_dict = config_service.get_config_dict()
                Logger.info(f"Config-Inhalt: {config_dict}")
                
                # Prüfen ob Datei existiert
                import os
                if hasattr(config_service, '_config_path') and os.path.exists(config_service._config_path):
                    Logger.info(f"Config-Datei existiert: JA")
                    
                    # Datei-Inhalt direkt lesen
                    try:
                        with open(config_service._config_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        Logger.info(f"Datei-Inhalt direkt: {file_content}")
                    except Exception as read_error:
                        Logger.error(f"Fehler beim Lesen der Config-Datei: {read_error}")
                else:
                    Logger.warning("Config-Datei existiert: NEIN")
            else:
                Logger.error("Config-Service nicht verfügbar")
            
            Logger.info("=== CONFIG DEBUG INFO ENDE ===")
            
        except Exception as e:
            Logger.error(f"Fehler bei Config-Debug: {str(e)}", exc_info=True)

    def _register_widget_for_compatibility(self, widget, tab_name):
        """
        Registriert Widgets bei der App für Legacy-Kompatibilität
        
        Args:
            widget: Das Widget
            tab_name (str): Name des Tabs
        """
        try:
            # Spezielle Registrierung für wichtige Widgets
            if tab_name == 'Einstellungen':
                self.einstellungen_widget = widget
                Logger.debug("EinstellungenWidget bei App registriert")
            
            elif tab_name == 'Eigenschaften':
                self.eigenschaften_widget = widget
                Logger.debug("EigenschaftenWidget bei App registriert")
            
            elif tab_name == 'Ausrüstung':
                self.ausruestung_widget = widget
                Logger.debug("AusrüstungWidget bei App registriert")
            
            elif tab_name == 'Profil':
                self.profil_widget = widget
                Logger.debug("ProfilWidget bei App registriert")
            
            elif tab_name == 'Völker':
                self.voelker_widget = widget
                Logger.debug("VölkerWidget bei App registriert")
            
            elif tab_name == 'Talente':
                self.talente_widget = widget
                Logger.debug("TalenteWidget bei App registriert")
            
            elif tab_name == 'Mächte':
                self.maechte_widget = widget
                Logger.debug("MächteWidget bei App registriert")
            
            elif tab_name == 'Handicaps':
                self.handicaps_widget = widget
                Logger.debug("HandicapsWidget bei App registriert")
            
            elif tab_name == 'Charakter':
                self.charakterbogen_widget = widget
                Logger.debug("CharakterbogenWidget bei App registriert")

            elif tab_name == 'Historie':
                self.historie_widget = widget
                Logger.debug("HistorieWidget bei App registriert")

        except Exception as e:
            Logger.error(f"Fehler bei Widget-Registrierung für {tab_name}: {str(e)}")

    def get_widget_by_tab_text(self, tab_text, widget_id):
        """Retrieve widget by tab text and widget ID."""
        Logger.debug(f"get_widget_by_tab_text aufgerufen mit tab_text = {tab_text}, widget_id = {widget_id}")
        
        # Zuerst im screens Dictionary suchen
        screen = self.screens.get(tab_text)
        if screen:
            Logger.debug(f"Screen {tab_text} gefunden, IDs: {screen.ids.keys()}")
            widget = screen.ids.get(widget_id)
            if widget:
                Logger.debug(f"Widget {widget_id} gefunden")
                return widget
            else:
                Logger.error(f"Widget {widget_id} not found in screen {tab_text}.")
        else:
            Logger.error(f"Screen {tab_text} not found.")
        
        # Fallback: Direkt bei der App suchen
        try:
            widget_attr_name = f"{tab_text.lower()}_widget"
            if hasattr(self, widget_attr_name):
                app_widget = getattr(self, widget_attr_name)
                if app_widget and hasattr(app_widget, 'ids'):
                    widget = app_widget.ids.get(widget_id)
                    if widget:
                        Logger.debug(f"Widget {widget_id} über App-Attribut gefunden")
                        return widget
        except Exception as e:
            Logger.error(f"Fehler beim Fallback-Widget-Zugriff: {str(e)}")
        
        return None

    # Neue Hilfsmethoden für sichere Widget-Zugriffe
    def get_einstellungen_widget(self):
        """Sichere Methode zum Abrufen des Einstellungen-Widgets"""
        return getattr(self, 'einstellungen_widget', None)

    def get_eigenschaften_widget(self):
        """Sichere Methode zum Abrufen des Eigenschaften-Widgets"""
        return getattr(self, 'eigenschaften_widget', None)

    def get_ausruestung_widget(self):
        """Sichere Methode zum Abrufen des Ausrüstung-Widgets"""
        return getattr(self, 'ausruestung_widget', None)

    def safe_widget_call(self, widget_getter, method_name, *args, **kwargs):
        """
        Sichere Methode zum Aufrufen von Widget-Methoden
        
        Args:
            widget_getter: Funktion zum Abrufen des Widgets
            method_name (str): Name der aufzurufenden Methode
            *args, **kwargs: Argumente für die Methode
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            widget = widget_getter()
            if widget and hasattr(widget, method_name):
                method = getattr(widget, method_name)
                if callable(method):
                    method(*args, **kwargs)
                    return True
                else:
                    Logger.warning(f"'{method_name}' ist nicht aufrufbar")
            else:
                Logger.warning(f"Widget oder Methode '{method_name}' nicht gefunden")
            return False
        except Exception as e:
            Logger.error(f"Fehler beim Widget-Methodenaufruf '{method_name}': {str(e)}")
            return False

    def on_stop(self):
        """Wird beim Beenden der App aufgerufen"""
        try:
            # Service Container bereinigen
            service_container.shutdown()
            
            # Cleanup für alle registrierten Widgets
            widgets_to_cleanup = [
                'einstellungen_widget', 'eigenschaften_widget', 'ausruestung_widget',
                'profil_widget', 'voelker_widget', 'talente_widget', 'maechte_widget',
                'handicaps_widget', 'charakterbogen_widget'
            ]
            
            for widget_name in widgets_to_cleanup:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    if widget and hasattr(widget, 'cleanup'):
                        try:
                            widget.cleanup()
                            Logger.debug(f"Widget {widget_name} bereinigt")
                        except Exception as e:
                            Logger.error(f"Fehler beim Bereinigen von {widget_name}: {str(e)}")
            
            Logger.info("App-Cleanup abgeschlossen")
            
        except Exception as e:
            Logger.error(f"Fehler beim App-Cleanup: {str(e)}")

    # Aktualisierte refresh_current_tab Methode
    def refresh_current_tab(self):
        """
        Aktualisiert den aktuellen Tab explizit.
        Wird aufgerufen, wenn ein Tab-Inhalt aktualisiert werden muss,
        ohne den Tab zu wechseln.
        """
        try:
            # Finde den Index des aktuellen Tabs
            carousel = self.root.ids.tabs_carousel
            index = carousel.index
            
            # Finde den Tab-Titel basierend auf dem Index
            if 0 <= index < len(self.tab_definitions):
                tab_title = self.tab_definitions[index][1]
                
                # Sichere Tab-Updates direkt über die Screen-Instanzen
                screen = self.screens.get(tab_title)
                if screen:
                    if tab_title == 'Eigenschaften' and hasattr(screen, 'update_eigenschaften'):
                        screen.update_eigenschaften()
                    elif tab_title == 'Ausrüstung' and hasattr(screen, 'refresh_widget'):
                        screen.refresh_widget()
                    elif tab_title == 'Profil' and hasattr(screen, 'load_profil'):
                        screen.load_profil()
                    elif tab_title == 'Völker' and hasattr(screen, 'aktualisiere_ui'):
                        screen.aktualisiere_ui()
                    elif tab_title == 'Talente' and hasattr(screen, 'refresh_widget'):
                        screen.refresh_widget()
                    elif tab_title == 'Mächte' and hasattr(screen, 'refresh_widget'):
                        screen.refresh_widget()
                    elif tab_title == 'Handicaps' and hasattr(screen, 'refresh_widget'):
                        screen.refresh_widget()
                    elif tab_title == 'Charakter' and hasattr(screen, 'update_overview'):
                        screen.update_overview(0)
                    elif tab_title == 'Einstellungen' and hasattr(screen, 'aktualisiere_ui'):
                        screen.aktualisiere_ui()
                    elif tab_title == 'Historie' and hasattr(screen, 'refresh_widget'):
                        screen.refresh_widget()

                Logger.info(f"UI-Aktualisierung für aktuellen Tab '{tab_title}' abgeschlossen")
            else:
                Logger.error(f"Ungültiger Carousel-Index: {index}")
        except Exception as e:
            Logger.error(f"Fehler bei der Aktualisierung des aktuellen Tabs: {str(e)}", exc_info=True)

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label):
        """
        Wird aufgerufen, wenn ein Tab gewechselt wird.
        - Aktualisiert den Carousel-Index
        - Aktualisiert die UI-Elemente des aktiven Tabs
        """
        # Zugriff auf den Tab-Titel
        tab_title = getattr(instance_tab, 'title', 'Unbekannt')
        Logger.info(f"Tab-Wechsel zu: {tab_title}")

        # Finde den Index des aktiven Tabs
        index = next((i for i, tab in enumerate(self.tab_definitions) if tab[1] == tab_title), 0)

        # Setze den Carousel-Index
        self.root.ids.tabs_carousel.index = index
        
        try:
            # Tab-spezifische Aktualisierungen direkt über Screen-Instanzen
            screen = self.screens.get(tab_title)
            if screen:
                if tab_title == 'Eigenschaften' and hasattr(screen, 'update_eigenschaften'):
                    screen.update_eigenschaften()
                elif tab_title == 'Ausrüstung' and hasattr(screen, 'refresh_widget'):
                    screen.refresh_widget()
                elif tab_title == 'Profil' and hasattr(screen, 'load_profil'):
                    screen.load_profil()
                elif tab_title == 'Völker' and hasattr(screen, 'aktualisiere_ui'):
                    screen.aktualisiere_ui()
                elif tab_title == 'Talente' and hasattr(screen, 'refresh_widget'):
                    screen.refresh_widget()
                elif tab_title == 'Mächte' and hasattr(screen, 'refresh_widget'):
                    screen.refresh_widget()
                elif tab_title == 'Handicaps' and hasattr(screen, 'refresh_widget'):
                    screen.refresh_widget()
                elif tab_title == 'Charakter' and hasattr(screen, 'update_overview'):
                    Logger.debug("Charakterbogen-Tab erkannt")
                    screen.update_overview(0)
                elif tab_title == 'Historie' and hasattr(screen, 'refresh_widget'):
                    Logger.debug("Historie-Tab erkannt")
                    screen.refresh_widget()
                    
            Logger.info(f"UI-Aktualisierung für Tab {tab_title} erfolgreich")
                    
        except Exception as e:
            Logger.error(f"Fehler bei UI-Aktualisierung für Tab {tab_title}: {str(e)}", exc_info=True)

if __name__ == "__main__":
    Logger.info("Starte SW_Charakter_GeneratorApp")
    SW_Charakter_GeneratorApp().run()