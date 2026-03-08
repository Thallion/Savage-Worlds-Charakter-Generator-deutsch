"""
main.py: SW_Charakter_GeneratorApp mit KivyMD Tabs, Carousel, GenerationPointsBar und Logger.
REFACTORED: Screen-Klassen nach views/screens.py extrahiert
"""

import sys
import os
import logging
from functools import partial
import re
import webbrowser

# Logging-Setup als erstes importieren und initialisieren
from utils.logging_setup import setup_file_logging, cleanup_old_logs, log_system_info

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition


from kivymd.uix.boxlayout import MDBoxLayout
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
from kivymd.uix.label import MDLabel, MDIcon

from controllers.charakter_controller import CharakterController
from models.charakter import Charakter
from views.pointbar_view import GenerationPointsBar
from views.charakter_verwaltung_widget import CharakterVerwaltungWidget
from views.einstellungen_widget import EinstellungenWidget
from views.historie_view import HistorieWidget
from views.voelker_view import VoelkerWidget
from views.profil_view import ProfilWidget
from views.eigenschaften_view import EigenschaftenWidget
from views.handicaps_view import HandicapsWidget
from views.talente_view import TalenteWidget
from views.maechte_view import KraefteWidget, MaechteWidget  # MaechteWidget für Rückwärtskompatibilität
from views.ausruestung_view import AusruestungWidget
from views.charakterbogen_view import CharakterbogenWidget

# Extrahierte Screen-Klassen
from views.screens import (
    CharakterVerwaltungScreen, EinstellungenScreen, VoelkerScreen, ProfilScreen, EigenschaftenScreen,
    HandicapsScreen, TalenteScreen, MaechteScreen, AusruestungScreen, 
    CharakterbogenScreen, HistorieScreen, InfoScreen, HyperlinkLabel
)
from views.ui_components import CustomTabsItem, SwipeScreenManager
from utils.logging_utils import GUIHandler

# Config Service für Theme-Speicherung importieren
from services.config_service import ConfigService
from services.service_container import service_container

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')


class SW_Charakter_GeneratorApp(MDApp):
    controller = ObjectProperty(None)
    screens = {}  # Dictionary to hold screen instances

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info("Init SW_Charakter_GeneratorApp")
        
        # File-Logging als erstes initialisieren
        try:
            self.log_filepath = setup_file_logging("SavageWorldsCharakterGenerator")
            cleanup_old_logs()  # Alte Logs bereinigen
            log_system_info()   # System-Info loggen
            Logger.info(f"Session-Logging aktiviert: {self.log_filepath}")
            logging.info("=== App-Initialisierung gestartet ===")
            
            # Log-Pfad für einfache Anzeige speichern
            if self.log_filepath:
                self.log_directory = os.path.dirname(self.log_filepath)
            else:
                self.log_directory = None
                
        except Exception as e:
            Logger.error(f"Konnte File-Logging nicht initialisieren: {str(e)}")
            self.log_filepath = None
            self.log_directory = None
        
        # Ressourcen-Extraktion für PyInstaller EXE
        from utils.resource_extractor import resource_extractor
        if not resource_extractor.extract_resources():
            Logger.error("Fehler bei Ressourcen-Extraktion")
            logging.error("Ressourcen-Extraktion fehlgeschlagen")
        else:
            logging.info("Ressourcen erfolgreich extrahiert")
        
        # KORRIGIERT: Frühe Controller-Initialisierung für Service Container
        # Zuerst Service Container mit temporärem Controller initialisieren um Config Service zu erhalten
        temp_controller = CharakterController()
        service_container.initialize(temp_controller)
        Logger.info("Service Container früh initialisiert")
        logging.info("Service Container erfolgreich initialisiert")
        
        # Letztes Setting aus Config laden
        last_setting = self._load_last_setting_from_config()
        Logger.info(f"Geladenes letztes Setting: {last_setting}")
        
        # Charakter mit dem geladenen Setting initialisieren
        self.charakter = Charakter(active_setting_name=last_setting)
        self.controller = CharakterController()
        
        # Service Container mit dem finalen Controller aktualisieren
        service_container.initialize(self.controller)
        
        # NavigationRail-Items und Modus-Tracking
        self.rail_items = []
        self._mobile_modus_active = False
        self._mobile_modus_override = None  # None = automatisch, True/False = manuell
        self._nav_rail_visible = False  # NavigationRail Sichtbarkeit im Mobile-Modus
        self._current_tab_index = 0  # Aktueller Tab-Index für Swipe-Navigation

        # Deine Icons + Tab-Texte + zugehörige Screens
        # NEU: CharakterVerwaltung-Tab hinzugefügt
        self.tab_definitions = [
            ("content-save",     "Speichern/Laden",      CharakterVerwaltungScreen),
            ("cog",              "Einstellungen",        EinstellungenScreen),
            ("account-group",    "Völker",               VoelkerScreen),
            ("account-details",  "Profil",               ProfilScreen),
            ("arm-flex",         "Eigenschaften",        EigenschaftenScreen),
            ("account-alert",    "Handicaps",            HandicapsScreen),
            ("star-circle",      "Talente",              TalenteScreen),
            ("creation-outline", "Mächte",               MaechteScreen),
            ("shield-sword",     "Ausrüstung",           AusruestungScreen),
            ("account",          "Charakter",            CharakterbogenScreen),
            ("history",          "Historie",             HistorieScreen),
            ("information",      "Info",                 InfoScreen),
        ]

    def build(self):
        # KORRIGIERT: Theme aus Config laden (Service Container ist bereits initialisiert)
        self.load_theme_from_config()
        return self.load_main_kv()
    
    def load_main_kv(self):
        """PyInstaller-kompatibles Laden der main.kv Datei"""
        if getattr(sys, 'frozen', False):
            # PyInstaller Bundle
            base_path = sys._MEIPASS
            kv_path = os.path.join(base_path, 'main.kv')
        else:
            # Normale Ausführung
            kv_path = 'main.kv'
        
        if os.path.exists(kv_path):
            return Builder.load_file(kv_path)
        else:
            Logger.error(f"Main KV-Datei nicht gefunden: {kv_path}")
            return None

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
                    
                    Logger.info(f"Primärpalette geändert zu: {primary_palette}")
                else:
                    Logger.warning(f"Ungültige Palette: {primary_palette}")
            
            # Änderungen in Config speichern
            if changes and config_service:
                for key, value in changes.items():
                    config_service.set(key, value)
                    Logger.info(f"Config gespeichert: {key} = {value}")
                
                Logger.info("=== Theme-Update erfolgreich abgeschlossen ===")
            
        except Exception as e:
            Logger.error(f"Fehler beim Update des Themes: {str(e)}", exc_info=True)
    
    def _load_last_setting_from_config(self):
        """
        Lädt das zuletzt verwendete Setting aus der Konfiguration
        
        Returns:
            str: Name des letzten Settings oder "SWAE" als Fallback
        """
        try:
            Logger.info("=== Lade letztes Setting aus Config ===")
            
            # Config Service aus Service Container holen
            from services.service_container import get_config_service
            config_service = get_config_service()
            
            if not config_service:
                Logger.warning("ConfigService nicht verfügbar, verwende Standard-Setting")
                return "SWAE"
            
            # Letztes Setting aus Config laden
            last_setting = config_service.get('last_setting', 'SWAE')
            
            Logger.info(f"Letztes Setting aus Config geladen: {last_setting}")
            
            # Validierung: Prüfen ob das Setting existiert
            from utils.path_utils import get_application_root
            settings_dir = get_application_root() / 'settings'
            setting_file = settings_dir / f"{last_setting}.json"
            
            if setting_file.exists():
                Logger.info(f"Setting-Datei gefunden: {setting_file}")
                return last_setting
            else:
                Logger.warning(f"Setting-Datei '{setting_file}' nicht gefunden, verwende Standard-Setting 'SWAE'")
                # Standard-Setting in Config speichern
                config_service.set('last_setting', 'SWAE')
                return "SWAE"
                
        except Exception as e:
            Logger.error(f"Fehler beim Laden des letzten Settings: {str(e)}", exc_info=True)
            return "SWAE"

    def on_start(self):
        """Wird nach build() aufgerufen, wenn das Layout verfügbar ist."""
        Logger.info("=== App-Start gestartet ===")
        
        # Fenster maximieren
        Window.maximize()
        
        # Controller mit der App verbinden
        if self.controller:
            self.controller.app = self
            # Charakter an Controller übergeben
            self.controller.charakter = self.charakter

        root = self.root
        if not root:
            Logger.error("Root-Widget nicht verfügbar")
            return

        # Logger-Widget konfigurieren  
        logger_widget = root.ids.get('logger_label') if root else None
        if logger_widget:
            log_handler = GUIHandler(logger_widget)
            Logger.addHandler(log_handler)
            Logger.info("Logger-Handler hinzugefügt")
        else:
            Logger.warning("Logger-Widget nicht gefunden")

        # Fenster-Resize-Event für automatischen Moduswechsel
        Window.bind(on_resize=self._on_window_resize)

        # KORRIGIERT: Tabs und Screens mit mehr Verzögerung für vollständige UI-Initialisierung
        Clock.schedule_once(lambda dt: self.build_tabs_and_screens_immediate(), 0.5)

    def build_tabs_and_screens_immediate(self):
        """Erstellt die Tabs und Screen-Inhalte sofort (wie in main_backup.py)"""
        try:
            Logger.info("=== Tabs und Screens werden erstellt ===")
            root = self.root
            if not root:
                Logger.error("Root-Widget nicht verfügbar")
                return

            # Tabbar & ScreenManager referenzieren
            tabs_bar = root.ids.get('tabs_bar')
            screen_manager = root.ids.get('tabs_carousel')  # Keeping the same ID

            if not tabs_bar or not screen_manager:
                Logger.error(f"Tabs_bar ({tabs_bar}) oder ScreenManager ({screen_manager}) nicht verfügbar")
                return

            # Finde das MDTabsScrollView-Kind und das interne Container-Widget  
            scroll_view = None
            for child in tabs_bar.children:
                if 'MDTabsScrollView' in str(type(child)):
                    scroll_view = child
                    break
            
            if not scroll_view:
                Logger.error("KRITISCH: MDTabsScrollView nicht gefunden!")
                return

            # Scrollbar für Tab-Navigation besser sichtbar machen (wichtig für Android)
            scroll_view.bar_width = dp(8)
            scroll_view.bar_margin = dp(2)
            scroll_view.do_scroll_x = True
            scroll_view.do_scroll_y = False
            
            # MDTabsScrollView hat normalerweise ein internes Layout-Widget
            container = None
            if scroll_view.children:
                container = scroll_view.children[0]  # Das erste (und einzige) Kind sollte der Container sein
            
            if not container:
                Logger.error("KRITISCH: Container-Widget im MDTabsScrollView nicht gefunden!")
                return
            
            # Leere den Container und ScreenManager
            container.clear_widgets()
            screen_manager.clear_widgets()

            # Initialize screens dictionary
            self.screens = {}
            # WICHTIG: Tab-Items-Liste behalten um WeakReference-Probleme zu vermeiden
            self.tab_items = []
            # WICHTIG: Screen-Instances-Liste behalten um WeakReference-Probleme zu vermeiden  
            self.screen_instances = []

            # Build tabs and screens SOFORT
            for i, (icon_str, tab_text, ScreenClass) in enumerate(self.tab_definitions):
                Logger.info(f"Erstelle Tab {i+1}/{len(self.tab_definitions)}: '{tab_text}' mit Icon '{icon_str}'")
                
                # Create Tab Item
                tab_item = MDTabsItem()
                icon_widget = MDTabsItemIcon(icon=icon_str)
                text_widget = MDTabsItemText(text=tab_text)
                
                # Setze parent-Referenzen für KivyMD's interne Logik
                if hasattr(icon_widget, '_tabs'):
                    icon_widget._tabs = tabs_bar
                if hasattr(text_widget, '_tabs'):
                    text_widget._tabs = tabs_bar
                if hasattr(tab_item, '_tabs'):
                    tab_item._tabs = tabs_bar
                
                tab_item.add_widget(icon_widget)
                tab_item.add_widget(text_widget)
                
                # Füge Tab zum Container hinzu
                container.add_widget(tab_item)
                
                # WICHTIG: Referenz behalten um WeakReference-Problem zu vermeiden
                self.tab_items.append(tab_item)

                # Create screen instance and add to screen manager  
                try:
                    # Create the screen instance directly (ScreenClass is already a Screen)
                    screen_instance = ScreenClass()
                    clean_name = tab_text.lower().replace(' ', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
                    screen_instance.name = f"screen_{i}_{clean_name}"
                    
                    # Add to ScreenManager
                    screen_manager.add_widget(screen_instance)
                    
                    # Setze den ersten Screen als aktuellen Screen
                    if i == 0:
                        screen_manager.current = screen_instance.name
                        
                except Exception as e:
                    Logger.error(f"Fehler beim Erstellen von {ScreenClass.__name__}: {str(e)}")
                    screen_instance = None
                
                # Store screen with tab_text as key (like in original)
                if screen_instance:
                    self.screens[tab_text] = screen_instance
                    # WICHTIG: Starke Referenz behalten um Garbage Collection zu verhindern
                    self.screen_instances.append(screen_instance)
                    
                    # WICHTIG: Widget-Registrierung für Kompatibilität
                    self._register_widget_for_compatibility(screen_instance, tab_text)
                else:
                    Logger.error(f"DEBUG: Screen {tab_text} konnte nicht erstellt werden!")
                
                Logger.info(f"✓ Tab '{tab_text}' erfolgreich erstellt und registriert")

            # Stelle sicher dass tabs_bar seine Tab-Updates verarbeitet
            if hasattr(tabs_bar, '_trigger_update_tab_width'):
                tabs_bar._trigger_update_tab_width()
            
            # SOFORT: Tab-Event-Binding
            tabs_bar.bind(on_tab_switch=self.on_tab_switch)
            
            # Debug: Alle Screen-Namen ausgeben
            Logger.info(f"DEBUG: ScreenManager enthält {len(screen_manager.screen_names)} Screens:")
            for screen_name in screen_manager.screen_names:
                Logger.info(f"  - {screen_name}")
                
            Logger.info(f"DEBUG: Starke Referenzen: {len(self.screen_instances)} Screen-Instanzen behalten")
            Logger.info(f"DEBUG: self.screens Dictionary: {len(self.screens)} Einträge")

            # SOFORT: Ersten Tab aktivieren (mit sicherer Referenz)
            if self.tab_items:
                # Verzögere die Aktivierung etwas, damit die Widgets vollständig initialisiert sind
                Clock.schedule_once(lambda dt: self._activate_first_tab(screen_manager), 0.1)

            Logger.info(f"=== {len(self.tab_definitions)} Tabs und Screens erfolgreich erstellt ===")

            # NavigationRail aufbauen und initialen Modus setzen
            self.build_navigation_rail()
            self._setup_swipe_navigation(screen_manager)
            self._apply_initial_navigation_mode()

        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der Tabs und Screens: {str(e)}", exc_info=True)

    def _activate_first_tab(self, screen_manager):
        """Aktiviert den ersten Tab mit Verzögerung um KivyMD-Initialisierung abzuwarten"""
        try:
            if self.tab_items:
                first_tab = self.tab_items[0]
                first_tab.active = True
                Logger.info(f"Erster Tab verzögert aktiviert.")
                # ScreenManager braucht kein Index-Setting - wird bereits beim add_widget gesetzt
        except Exception as e:
            Logger.error(f"Fehler bei verzögerter Tab-Aktivierung: {str(e)}")


    def on_tab_switch(self, tabs_instance, tab_item, tab_content=None):
        """Handle tab switching mit verbessertem Logging und Error Handling"""
        try:
            # KORRIGIERT: Suche in self.tab_items statt tabs_instance.children
            tab_index = None
            for i, stored_tab in enumerate(self.tab_items):
                if stored_tab == tab_item:
                    tab_index = i
                    break

            if tab_index is None:
                Logger.warning("Tab-Index konnte nicht ermittelt werden")
                return

            # Tab-Namen für Logging
            tab_name = self.tab_definitions[tab_index][1] if tab_index < len(self.tab_definitions) else "Unknown"
            Logger.info(f"Tab-Wechsel zu Index {tab_index}: {tab_name}")

            # Tab-Index tracken
            self._current_tab_index = tab_index

            # ScreenManager-Screen setzen
            root = self.root
            if root and root.ids.get('tabs_carousel'):
                screen_manager = root.ids['tabs_carousel']
                
                # Get screen name from tab index
                if 0 <= tab_index < len(self.tab_definitions):
                    tab_text = self.tab_definitions[tab_index][1]
                    clean_name = tab_text.lower().replace(' ', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
                    screen_name = f"screen_{tab_index}_{clean_name}"
                    
                    # Check if screen exists, create if needed
                    if hasattr(screen_manager, 'get_screen'):
                        try:
                            screen = screen_manager.get_screen(screen_name)
                            screen_manager.current = screen_name
                        except Exception as e:
                            Logger.warning(f"Screen '{screen_name}' nicht gefunden, erstelle neu...")
                            # Try to create screen dynamically
                            if 0 <= tab_index < len(self.tab_definitions):
                                ScreenClass = self.tab_definitions[tab_index][2]
                                try:
                                    new_screen = ScreenClass()
                                    new_screen.name = screen_name
                                    screen_manager.add_widget(new_screen)
                                    # Keep strong reference
                                    if not hasattr(self, 'screen_instances'):
                                        self.screen_instances = []
                                    self.screen_instances.append(new_screen)
                                    self.screens[tab_text] = new_screen
                                    screen_manager.current = screen_name
                                    Logger.info(f"Screen '{screen_name}' dynamisch erstellt")
                                except Exception as create_error:
                                    Logger.error(f"Dynamische Erstellung von '{screen_name}' fehlgeschlagen: {create_error}")
                    else:
                        Logger.error("ScreenManager hat keine get_screen Methode")
                else:
                    Logger.error(f"Ungültiger Tab-Index: {tab_index}")

            # Screen-spezifische Updates
            self.update_active_screen(tab_index)

        except Exception as e:
            Logger.error(f"Fehler beim Tab-Wechsel: {str(e)}", exc_info=True)

    def update_active_screen(self, tab_index):
        """Aktualisiert den aktiven Screen basierend auf dem Tab-Index"""
        try:
            if tab_index >= len(self.tab_definitions):
                return
                
            # Hole tab_text (wie in der ursprünglichen Version)
            tab_text = self.tab_definitions[tab_index][1]
            
            screen = self.screens.get(tab_text)
            if screen:
                # Try to call the screen's own methods first (delegated to underlying widgets)
                if hasattr(screen, 'refresh_widget'):
                    Clock.schedule_once(lambda dt: screen.refresh_widget(), 0.1)
                    Logger.debug(f"Screen '{tab_text}' refresh getriggert")
                elif hasattr(screen, 'aktualisiere_ui'):
                    Clock.schedule_once(lambda dt: screen.aktualisiere_ui(), 0.1)
                    Logger.debug(f"Screen '{tab_text}' UI-Update getriggert")
                elif hasattr(screen, 'update_overview'):
                    Clock.schedule_once(lambda dt: screen.update_overview(), 0.1)
                    Logger.debug(f"Screen '{tab_text}' overview-Update getriggert")
                    
                # If screen doesn't have the method, try to find the underlying widget
                elif hasattr(screen, 'ids'):
                    # Map tab names to their widget IDs as defined in main.kv
                    widget_id_map = {
                        'Charakterverwaltung': 'charakter_verwaltung_widget',
                        'Einstellungen': 'einstellungen_widget',
                        'Völker': 'voelker_widget',
                        'Profil': 'profil_widget', 
                        'Eigenschaften': 'eigenschaften_widget',
                        'Handicaps': 'handicaps_widget',
                        'Talente': 'talente_widget',
                        'Mächte': 'maechte_widget',
                        'Ausrüstung': 'ausruestung_widget',
                        'Charakter': 'charakterbogen_widget',
                        'Historie': 'historie_widget'
                    }
                    
                    widget_id = widget_id_map.get(tab_text)
                    if widget_id and widget_id in screen.ids:
                        widget = screen.ids[widget_id]
                        if hasattr(widget, 'refresh_widget'):
                            Clock.schedule_once(lambda dt: widget.refresh_widget(), 0.1)
                            Logger.debug(f"Widget '{widget_id}' refresh getriggert")
                        elif hasattr(widget, 'aktualisiere_ui'):
                            Clock.schedule_once(lambda dt: widget.aktualisiere_ui(), 0.1)
                            Logger.debug(f"Widget '{widget_id}' UI-Update getriggert")
                        elif hasattr(widget, 'update_overview'):
                            Clock.schedule_once(lambda dt: widget.update_overview(), 0.1)
                            Logger.debug(f"Widget '{widget_id}' overview-Update getriggert")
                
        except Exception as e:
            Logger.error(f"Fehler beim Screen-Update: {str(e)}")

    def build_navigation_rail(self):
        """Erstellt scrollbare NavigationRail-Items für alle Tab-Definitionen"""
        try:
            root = self.root
            if not root:
                return

            nav_rail_box = root.ids.get('nav_rail_box')
            if not nav_rail_box:
                Logger.warning("nav_rail_box nicht im Layout gefunden")
                return

            nav_rail_box.clear_widgets()
            self.rail_items = []
            self._active_rail_index = 0

            for i, (icon_str, tab_text, _) in enumerate(self.tab_definitions):
                # Vertikales Item: Icon + Label
                item = MDBoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(64),
                    padding=[dp(4), dp(8), dp(4), dp(4)],
                    spacing=dp(2),
                )
                item._rail_index = i

                icon = MDIcon(
                    icon=icon_str,
                    halign='center',
                    pos_hint={'center_x': 0.5},
                    size_hint_y=None,
                    height=dp(28),
                )

                label = MDLabel(
                    text=tab_text,
                    halign='center',
                    font_style='Label',
                    role='small',
                    size_hint_y=None,
                    height=dp(20),
                )

                item.add_widget(icon)
                item.add_widget(label)

                # Touch-Event auf on_touch_up binden (statt on_touch_down),
                # damit ScrollView Scroll-Gesten erkennen kann
                item.bind(on_touch_up=self._on_rail_item_touch)

                nav_rail_box.add_widget(item)
                self.rail_items.append(item)

            Logger.info(f"NavigationRail mit {len(self.rail_items)} Items erstellt")

        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der NavigationRail: {str(e)}", exc_info=True)

    def _on_rail_item_touch(self, item, touch):
        """Callback wenn ein Rail-Item losgelassen wird (touch_up).

        Verwendet on_touch_up statt on_touch_down, damit ScrollView
        Scroll-Gesten verarbeiten kann (Android-Kompatibilität).
        """
        if not item.collide_point(*touch.pos):
            return False

        # Scroll-Gesten ignorieren (nur Taps verarbeiten)
        if hasattr(touch, 'is_mouse_scrolling') and touch.is_mouse_scrolling:
            return False
        if touch.grab_current is not None and touch.grab_current is not item:
            return False

        try:
            item_index = item._rail_index

            # Screen wechseln
            root = self.root
            if not root:
                return False

            screen_manager = root.ids.get('tabs_carousel')
            if not screen_manager:
                return False

            if 0 <= item_index < len(self.tab_definitions):
                tab_text = self.tab_definitions[item_index][1]
                clean_name = tab_text.lower().replace(' ', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
                screen_name = f"screen_{item_index}_{clean_name}"

                # Transition ohne Animation bei direktem Tap
                screen_manager.transition = NoTransition()

                try:
                    screen_manager.get_screen(screen_name)
                    screen_manager.current = screen_name
                except Exception:
                    Logger.warning(f"Screen '{screen_name}' nicht gefunden")

                # Aktives Item visuell hervorheben
                self._set_active_rail_item(item_index)
                self._current_tab_index = item_index
                self.update_active_screen(item_index)
                Logger.info(f"NavigationRail-Wechsel zu: {tab_text}")

            return True

        except Exception as e:
            Logger.error(f"Fehler beim NavigationRail-Wechsel: {str(e)}")
            return False

    def _set_active_rail_item(self, active_index):
        """Hebt das aktive Rail-Item visuell hervor"""
        self._active_rail_index = active_index
        for i, item in enumerate(self.rail_items):
            if i == active_index:
                item.md_bg_color = self.theme_cls.secondaryContainerColor
            else:
                item.md_bg_color = (0, 0, 0, 0)

    def set_navigation_mode(self, mobile):
        """
        Wechselt zwischen Desktop-Tabs und mobiler NavigationRail

        Args:
            mobile (bool): True für NavigationRail, False für Tabs
        """
        try:
            if self._mobile_modus_active == mobile:
                return

            root = self.root
            if not root:
                return

            tabs_container = root.ids.get('tabs_container')
            nav_rail_container = root.ids.get('nav_rail_container')
            tab_content_box = root.ids.get('tab_content_box')
            screen_manager = root.ids.get('tabs_carousel')
            menu_toggle = root.ids.get('menu_toggle_container')

            if not all([tabs_container, nav_rail_container, tab_content_box]):
                Logger.warning("Layout-Elemente für Moduswechsel nicht verfügbar")
                return

            # Aktuellen Screen-Index ermitteln
            current_index = 0
            if screen_manager and screen_manager.current:
                for i, (_, tab_text, _) in enumerate(self.tab_definitions):
                    clean_name = tab_text.lower().replace(' ', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
                    if screen_manager.current == f"screen_{i}_{clean_name}":
                        current_index = i
                        break

            self._current_tab_index = current_index

            if mobile:
                # Tabs verstecken
                tabs_container.height = 0
                tabs_container.opacity = 0

                # NavigationRail immer sichtbar (kompakt)
                nav_rail_container.width = dp(72)
                nav_rail_container.opacity = 1
                self._nav_rail_visible = True

                # Menü-Toggle-Button verstecken (Rail ist immer sichtbar)
                if menu_toggle:
                    menu_toggle.width = 0
                    menu_toggle.opacity = 0

                # Content-Padding reduzieren
                tab_content_box.padding = [dp(4), 0, dp(4), dp(4)]

                # Pointbar auf Smartphone weiter runter (Statusbar/Notch-Abstand)
                main_content_area = root.ids.get('main_content_area')
                if main_content_area:
                    main_content_area.padding = [0, dp(12), 0, 0]

                # Swipe aktivieren
                if screen_manager and hasattr(screen_manager, 'swipe_enabled'):
                    screen_manager.swipe_enabled = True

                # Aktives Rail-Item hervorheben
                if current_index < len(self.rail_items):
                    self._set_active_rail_item(current_index)

                Logger.info("Mobiler Modus aktiviert (Swipe + NavigationRail)")
            else:
                # NavigationRail verstecken
                nav_rail_container.width = 0
                nav_rail_container.opacity = 0
                self._nav_rail_visible = False

                # Menü-Toggle-Button verstecken
                if menu_toggle:
                    menu_toggle.width = 0
                    menu_toggle.opacity = 0

                # Tabs zeigen
                tabs_container.height = dp(60)
                tabs_container.opacity = 1

                # Content-Padding wiederherstellen
                tab_content_box.padding = [dp(30), 0, dp(30), dp(30)]

                # Swipe deaktivieren
                if screen_manager and hasattr(screen_manager, 'swipe_enabled'):
                    screen_manager.swipe_enabled = False

                # Aktiven Tab setzen (ohne erneuten Screen-Wechsel)
                if current_index < len(self.tab_items):
                    self.tab_items[current_index].active = True

                Logger.info("Desktop-Modus aktiviert (Tabs)")

            self._mobile_modus_active = mobile

        except Exception as e:
            Logger.error(f"Fehler beim Moduswechsel: {str(e)}", exc_info=True)

    def _apply_initial_navigation_mode(self):
        """Wendet den initialen Navigationsmodus basierend auf Config an"""
        try:
            from services.service_container import get_config_service
            config_service = get_config_service()

            if config_service:
                mobile_modus = config_service.get('mobile_modus', False)
                if mobile_modus:
                    self._mobile_modus_override = True
                    self.set_navigation_mode(True)
                    Logger.info("Mobiler Modus aus Config geladen")
                else:
                    # Automatische Erkennung basierend auf Fensterbreite
                    if Window.width < dp(800):
                        self.set_navigation_mode(True)

                # Logger-Sichtbarkeit aus Config laden
                show_logger = config_service.get('show_logger', True)
                self.set_logger_visible(show_logger)

        except Exception as e:
            Logger.error(f"Fehler beim Laden des initialen Navigationsmodus: {str(e)}")

    def set_logger_visible(self, visible: bool):
        """Steuert die Sichtbarkeit der Logger-Box (Logger-Handler bleibt aktiv)"""
        try:
            root = self.root
            if not root:
                return
            logger_container = root.ids.get('logger_container')
            if not logger_container:
                return

            if visible:
                logger_container.height = dp(60)
                logger_container.opacity = 1
                logger_container.disabled = False
            else:
                logger_container.height = 0
                logger_container.opacity = 0
                logger_container.disabled = True

            Logger.debug(f"Logger-Box Sichtbarkeit: {visible}")
        except Exception as e:
            Logger.error(f"Fehler beim Setzen der Logger-Sichtbarkeit: {str(e)}")

    def _on_window_resize(self, instance, width, height):
        """Automatischer Moduswechsel basierend auf Fensterbreite"""
        try:
            # Bei manuellem Override nicht automatisch wechseln
            if self._mobile_modus_override is not None:
                return

            if width < dp(800):
                self.set_navigation_mode(True)
            else:
                self.set_navigation_mode(False)

        except Exception as e:
            Logger.error(f"Fehler bei Fenster-Resize-Handler: {str(e)}")

    def _setup_swipe_navigation(self, screen_manager):
        """Konfiguriert die Swipe-Navigation auf dem ScreenManager"""
        try:
            if hasattr(screen_manager, 'swipe_enabled'):
                screen_manager._swipe_callback = self._on_swipe
                Logger.info("Swipe-Navigation konfiguriert")
            else:
                Logger.warning("ScreenManager unterstützt kein Swipe (kein SwipeScreenManager)")
        except Exception as e:
            Logger.error(f"Fehler bei Swipe-Setup: {str(e)}")

    def _on_swipe(self, direction):
        """Callback für Swipe-Gesten auf dem Content-Bereich"""
        try:
            if not self._mobile_modus_active:
                return

            num_tabs = len(self.tab_definitions)
            if num_tabs == 0:
                return

            if direction == 'left':
                # Swipe nach links → nächster Tab
                new_index = self._current_tab_index + 1
                if new_index >= num_tabs:
                    return  # Am Ende, nicht wrappen
            elif direction == 'right':
                # Swipe nach rechts → vorheriger Tab
                new_index = self._current_tab_index - 1
                if new_index < 0:
                    return  # Am Anfang, nicht wrappen
            else:
                return

            self._switch_to_tab_index(new_index, direction)

        except Exception as e:
            Logger.error(f"Fehler bei Swipe-Handler: {str(e)}")

    def _switch_to_tab_index(self, index, swipe_direction=None):
        """Wechselt zum Tab mit dem angegebenen Index mit Slide-Animation"""
        try:
            if index < 0 or index >= len(self.tab_definitions):
                return

            root = self.root
            if not root:
                return

            screen_manager = root.ids.get('tabs_carousel')
            if not screen_manager:
                return

            tab_text = self.tab_definitions[index][1]
            clean_name = tab_text.lower().replace(' ', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
            screen_name = f"screen_{index}_{clean_name}"

            # Slide-Animation setzen
            if swipe_direction:
                transition = SlideTransition()
                transition.direction = 'left' if swipe_direction == 'left' else 'right'
                transition.duration = 0.2
                screen_manager.transition = transition
            else:
                screen_manager.transition = NoTransition()

            try:
                screen_manager.get_screen(screen_name)
                screen_manager.current = screen_name
            except Exception:
                Logger.warning(f"Screen '{screen_name}' nicht gefunden bei Swipe")
                return

            self._current_tab_index = index

            # NavigationRail-Highlight aktualisieren
            if index < len(self.rail_items):
                self._set_active_rail_item(index)

            # Screen-spezifische Updates
            self.update_active_screen(index)

            Logger.info(f"Swipe-Wechsel zu: {tab_text} (Index {index})")

        except Exception as e:
            Logger.error(f"Fehler bei Tab-Wechsel per Swipe: {str(e)}")

    def toggle_navigation_rail(self):
        """Blendet die NavigationRail im Mobile-Modus ein/aus"""
        try:
            if not self._mobile_modus_active:
                return

            root = self.root
            if not root:
                return

            nav_rail_container = root.ids.get('nav_rail_container')
            if not nav_rail_container:
                return

            if self._nav_rail_visible:
                # Rail ausblenden (kein disabled - Android-Kompatibilität)
                nav_rail_container.width = 0
                nav_rail_container.opacity = 0
                self._nav_rail_visible = False
                Logger.info("NavigationRail ausgeblendet")
            else:
                # Rail einblenden
                nav_rail_container.width = dp(100)
                nav_rail_container.opacity = 1
                self._nav_rail_visible = True
                Logger.info("NavigationRail eingeblendet")
        except Exception as e:
            Logger.error(f"Fehler beim Toggle der NavigationRail: {str(e)}")

    def get_screen(self, screen_name):
        """Hilfsmethode zum Abrufen von Screen-Objekten"""
        return self.screens.get(screen_name)

    def _register_widget_for_compatibility(self, screen_instance, tab_name):
        """
        Registriert Screen-Widgets bei der App für Legacy-Kompatibilität
        
        Args:
            screen_instance: Das Screen-Widget
            tab_name (str): Name des Tabs
        """
        try:
            # Hole das tatsächliche Widget aus dem Screen
            widget = None
            if hasattr(screen_instance, 'ids'):
                if tab_name == 'Charakterverwaltung' and 'charakter_verwaltung_widget' in screen_instance.ids:
                    widget = screen_instance.ids.charakter_verwaltung_widget
                    self.charakter_verwaltung_widget = widget
                    Logger.debug("CharakterVerwaltungWidget bei App registriert")
                
                elif tab_name == 'Einstellungen' and 'einstellungen_widget' in screen_instance.ids:
                    widget = screen_instance.ids.einstellungen_widget
                    self.einstellungen_widget = widget
                    Logger.debug("EinstellungenWidget bei App registriert")
                
                elif tab_name == 'Eigenschaften' and 'eigenschaften_widget' in screen_instance.ids:
                    widget = screen_instance.ids.eigenschaften_widget
                    self.eigenschaften_widget = widget
                    Logger.debug("EigenschaftenWidget bei App registriert")
                
                elif tab_name == 'Ausrüstung' and 'ausruestung_widget' in screen_instance.ids:
                    widget = screen_instance.ids.ausruestung_widget
                    self.ausruestung_widget = widget
                    Logger.debug("AusrüstungWidget bei App registriert")
                
                elif tab_name == 'Profil' and 'profil_widget' in screen_instance.ids:
                    widget = screen_instance.ids.profil_widget
                    self.profil_widget = widget
                    Logger.debug("ProfilWidget bei App registriert")
                
                elif tab_name == 'Völker' and 'voelker_widget' in screen_instance.ids:
                    widget = screen_instance.ids.voelker_widget
                    self.voelker_widget = widget
                    Logger.debug("VölkerWidget bei App registriert")
                
                elif tab_name == 'Talente' and 'talente_widget' in screen_instance.ids:
                    widget = screen_instance.ids.talente_widget
                    self.talente_widget = widget
                    Logger.debug("TalenteWidget bei App registriert")
                
                elif tab_name == 'Mächte' and 'maechte_widget' in screen_instance.ids:
                    widget = screen_instance.ids.maechte_widget
                    self.maechte_widget = widget
                    Logger.debug("MächteWidget bei App registriert")
                
                elif tab_name == 'Handicaps' and 'handicaps_widget' in screen_instance.ids:
                    widget = screen_instance.ids.handicaps_widget
                    self.handicaps_widget = widget
                    Logger.debug("HandicapsWidget bei App registriert")
                
                elif tab_name == 'Charakter' and 'charakterbogen_widget' in screen_instance.ids:
                    widget = screen_instance.ids.charakterbogen_widget
                    self.charakterbogen_widget = widget
                    Logger.debug("CharakterbogenWidget bei App registriert")
                
                elif tab_name == 'Historie' and 'historie_widget' in screen_instance.ids:
                    widget = screen_instance.ids.historie_widget
                    self.historie_widget = widget
                    Logger.debug("HistorieWidget bei App registriert")
            
        except Exception as e:
            Logger.error(f"Fehler bei Widget-Registrierung für '{tab_name}': {str(e)}")
    
    def show_log_info(self):
        """Zeigt Informationen über die Log-Dateien in einem Dialog."""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.boxlayout import MDBoxLayout
        
        content = MDBoxLayout(orientation="vertical", spacing="12dp", adaptive_height=True)
        
        if self.log_filepath:
            # Log-Datei-Info
            info_label = MDLabel(
                text=f"Aktuelle Log-Datei:\n{self.log_filepath}\n\nLog-Ordner:\n{self.log_directory}",
                size_hint_y=None,
                theme_text_color="Primary",
                halign="left"
            )
            info_label.bind(texture_size=info_label.setter('size'))
            content.add_widget(info_label)
            
            # Android-spezifische Hilfe
            from kivy.utils import platform
            if platform == 'android':
                help_label = MDLabel(
                    text="Auf Android findest du die Logs hier:\n• Dateimanager → Interner Speicher → SavageWorldsCharGen → logs\n• Oder: /sdcard/SavageWorldsCharGen/logs/",
                    size_hint_y=None,
                    theme_text_color="Secondary",
                    halign="left"
                )
                help_label.bind(texture_size=help_label.setter('size'))
                content.add_widget(help_label)
        else:
            error_label = MDLabel(
                text="Logging ist nicht aktiv oder fehlgeschlagen.",
                size_hint_y=None,
                theme_text_color="Error",
                halign="left"
            )
            error_label.bind(texture_size=error_label.setter('size'))
            content.add_widget(error_label)
        
        dialog = MDDialog(
            title="Log-Dateien Information",
            content_cls=content,
            buttons=[
                MDButton(
                    MDButtonText(text="Schließen"),
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def get_widget_by_tab_text(self, tab_text, widget_id):
        """
        Holt ein Widget basierend auf Tab-Text und Widget-ID
        
        Args:
            tab_text (str): Text des Tabs (z.B. 'Handicaps')
            widget_id (str): ID des Widgets (z.B. 'handicaps_widget')
            
        Returns:
            Widget oder None: Das gefundene Widget oder None
        """
        try:
            # Direkte Zuordnung zu den registrierten Widgets
            widget_map = {
                'Charakterverwaltung': getattr(self, 'charakter_verwaltung_widget', None),
                'Einstellungen': getattr(self, 'einstellungen_widget', None),
                'Eigenschaften': getattr(self, 'eigenschaften_widget', None),
                'Ausrüstung': getattr(self, 'ausruestung_widget', None),
                'Profil': getattr(self, 'profil_widget', None),
                'Völker': getattr(self, 'voelker_widget', None),
                'Talente': getattr(self, 'talente_widget', None),
                'Mächte': getattr(self, 'maechte_widget', None),
                'Handicaps': getattr(self, 'handicaps_widget', None),
            }
            
            widget = widget_map.get(tab_text)
            if widget:
                Logger.debug(f"Widget für Tab '{tab_text}' gefunden: {type(widget).__name__}")
                return widget
            else:
                Logger.warning(f"Widget für Tab '{tab_text}' nicht gefunden")
                return None
                
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen des Widgets für Tab '{tab_text}': {e}")
            return None


if __name__ == "__main__":
    SW_Charakter_GeneratorApp().run()