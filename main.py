"""
main.py: SW_Charakter_GeneratorApp mit KivyMD Tabs, Carousel, GenerationPointsBar und Logger.
REFACTORED: Screen-Klassen nach views/screens.py extrahiert
"""

import sys
import os
import logging
from functools import partial
from pathlib import Path
import re
import webbrowser

# Desktop-Skalierung MUSS vor allen Kivy-Imports gesetzt werden!
# Setzt KIVY_METRICS_DENSITY für korrekte dp()-Skalierung auf HiDPI-Displays.
from utils.desktop_scaling import apply_desktop_scaling
_applied_density = apply_desktop_scaling()

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
from kivymd.uix.button import MDIconButton

from controllers.charakter_controller import CharakterController
from models.charakter import Charakter
from views.pointbar_view import GenerationPointsBar
from views.wizard_bar import WizardBar
from kivy.lang import Builder
from utils.path_utils import get_application_root, get_resource_path
import os
from views.charakter_verwaltung_widget import CharakterVerwaltungWidget

# Wizard-Bar KV laden (Mobile oder Desktop)
from utils.platform_utils import get_kv_filename as _get_kv_filename
_wizard_bar_kv_name = _get_kv_filename('wizard_bar')
_wizard_bar_kv = os.path.join(get_application_root(), 'views', _wizard_bar_kv_name)
if not os.path.exists(_wizard_bar_kv):
    _wizard_bar_kv = os.path.join(get_application_root(), 'views', 'wizard_bar.kv')
if os.path.exists(_wizard_bar_kv):
    Builder.load_file(_wizard_bar_kv)
    Logger.info(f"{os.path.basename(_wizard_bar_kv)} geladen")
from views.einstellungen_widget import EinstellungenWidget
from views.historie_view import HistorieWidget
from views.voelker_view import VoelkerWidget
from views.profil_view import ProfilWidget
from views.eigenschaften_view import EigenschaftenWidget
from views.handicaps_view import HandicapsWidget
from views.talente_view import TalenteWidget
from views.maechte_view import KraefteWidget, MaechteWidget  # MaechteWidget für Rückwärtskompatibilität
from views.superkraefte_view import SuperkraefteWidget
from views.ausruestung_view import AusruestungWidget
from views.charakterbogen_view import CharakterbogenWidget

# Extrahierte Screen-Klassen
from views.screens import (
    CharakterVerwaltungScreen, EinstellungenScreen, VoelkerScreen, ProfilScreen, EigenschaftenScreen,
    HandicapsScreen, TalenteScreen, MaechteScreen, SuperkraefteScreen, AusruestungScreen,
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
    wizard_service = ObjectProperty(None)
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
        
        # Wizard Service initialisieren
        self.wizard_service = service_container.get_wizard_service()
        if self.wizard_service:
            self.wizard_service.charakter_controller = self.controller
            self._bind_wizard_events()
        
        # Android Statusbar/Notch-Höhe und Navigationsleisten-Höhe ermitteln
        self._android_top_padding = dp(24)  # Fallback
        self._android_bottom_padding = dp(24)  # Fallback für System-Navigationsleiste
        self._detect_android_top_padding()
        self._detect_android_bottom_padding()

        # NavigationRail-Items und Modus-Tracking
        self.rail_items = []
        self._bottom_nav_items = []  # Bottom-Navigation-Items für Portrait-Modus
        self._bottom_nav_tab_indices = []  # Tab-Indices der Bottom-Nav-Items
        self._mobile_modus_active = False
        self._mobile_modus_override = None  # None = automatisch, True/False = manuell
        self._nav_rail_visible = False  # NavigationRail Sichtbarkeit im Mobile-Modus
        self._current_tab_index = 0  # Aktueller Tab-Index für Swipe-Navigation
        self._last_rail_touch_time = 0  # Debounce für doppelte Touch-Events

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
            ("flash-outline",    "Superkräfte",          SuperkraefteScreen),
            ("shield-sword",     "Ausrüstung",           AusruestungScreen),
            ("account",          "Charakter",            CharakterbogenScreen),
            ("history",          "Historie",             HistorieScreen),
            ("information",      "Info",                 InfoScreen),
        ]

    def build(self):
        # Auf Android: Fenster automatisch verschieben, damit die Tastatur
        # das fokussierte Textfeld nicht überdeckt
        from kivy.utils import platform as _platform
        if _platform == 'android':
            Window.softinput_mode = 'below_target'

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
            
            # Validierung: Prüfen ob das Setting existiert (natives oder Benutzer-Verzeichnis)
            from utils.path_utils import get_settings_path, get_user_settings_path
            native_file = Path(get_settings_path(f"{last_setting}.json"))
            user_file = Path(get_user_settings_path(f"{last_setting}.json"))

            if native_file.exists() or user_file.exists():
                Logger.info(f"Setting-Datei für '{last_setting}' gefunden.")
                return last_setting
            else:
                Logger.warning(f"Setting-Datei für '{last_setting}' nicht gefunden, verwende Standard-Setting 'SWAE'")
                # Standard-Setting in Config speichern
                config_service.set('last_setting', 'SWAE')
                return "SWAE"
                
        except Exception as e:
            Logger.error(f"Fehler beim Laden des letzten Settings: {str(e)}", exc_info=True)
            return "SWAE"

    def _migrate_chars_on_android(self):
        """Migriert Charaktere vom alten App-Verzeichnis ins persistente Verzeichnis auf Android."""
        from kivy.utils import platform as kivy_platform
        if kivy_platform != 'android':
            return

        try:
            from utils.path_utils import get_application_root, get_chars_path
            import shutil

            old_chars_dir = Path(get_application_root()) / 'chars'
            new_chars_dir = Path(get_chars_path())

            # Neues Verzeichnis erstellen falls nötig
            new_chars_dir.mkdir(parents=True, exist_ok=True)

            # Alte Charaktere migrieren (nur wenn alte Dateien existieren)
            if old_chars_dir.exists() and old_chars_dir != new_chars_dir:
                migrated = 0
                for json_file in old_chars_dir.glob('*.json'):
                    target = new_chars_dir / json_file.name
                    if not target.exists():
                        shutil.copy2(str(json_file), str(target))
                        migrated += 1
                if migrated > 0:
                    Logger.info(f"Migration: {migrated} Charakter(e) ins persistente Verzeichnis kopiert")

            # Archetypen aus gebündeltem App-Verzeichnis ins persistente Verzeichnis kopieren
            self._copy_archetypen_on_android(old_chars_dir, new_chars_dir)

        except Exception as e:
            Logger.warning(f"Charakter-Migration fehlgeschlagen: {e}")

    def _copy_archetypen_on_android(self, bundled_chars_dir: Path, user_chars_dir: Path):
        """Kopiert mitgelieferte Archetypen ins persistente Benutzer-Verzeichnis auf Android.

        Vergleicht Dateigröße statt mtime, da APK-Extraktion oft ältere Timestamps
        setzt als bereits vorhandene User-Dateien.
        """
        try:
            import shutil

            # Hol den Root der App (wo die Ressourcen entpackt werden)
            app_root = get_application_root()
            
            # Prüfe mehrere mögliche Quellpfade für Archetypen
            possible_sources = [
                bundled_chars_dir / 'Archetypen',  # chars/Archetypen (normal)
                bundled_chars_dir.parent / 'Archetypen',  # /Archetypen (neben chars)
                app_root / 'Archetypen',  # Direkt im App-Root (buildozer)
                app_root / 'chars' / 'Archetypen',  # App-Root/chars/Archetypen
                Path(get_resource_path('chars/Archetypen')),  # via get_resource_path
                Path(get_resource_path('Archetypen')),  # direkt im resources
            ]

            bundled_archetypen = None
            for src in possible_sources:
                Logger.debug(f"Archetypen: Prüfe {src}")
                if src.exists():
                    bundled_archetypen = src
                    Logger.info(f"Archetypen: Gefunden in {src}")
                    break

            if not bundled_archetypen:
                Logger.warning(f"Archetypen: Kein gebündeltes Verzeichnis gefunden in {len(possible_sources)} möglichen Pfaden:")
                for src in possible_sources:
                    Logger.warning(f"Archetypen:   - {src}: {src.exists()}")
                return

            user_archetypen = user_chars_dir / 'Archetypen'
            user_archetypen.mkdir(parents=True, exist_ok=True)

            # Zähle Quelldateien
            source_files = list(bundled_archetypen.rglob('*'))
            source_count = sum(1 for f in source_files if f.is_file())
            Logger.info(f"Archetypen: Quelle hat {source_count} Datei(en)")

            copied = 0
            for item in bundled_archetypen.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(bundled_archetypen)
                    target = user_archetypen / rel_path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    # Kopieren wenn Zieldatei fehlt oder abweichende Größe hat (Update)
                    if not target.exists() or item.stat().st_size != target.stat().st_size:
                        shutil.copy2(str(item), str(target))
                        copied += 1
                        Logger.debug(f"Archetypen: Kopiert {item.name}")

            if copied > 0:
                Logger.info(f"Archetypen: {copied} Datei(en) ins persistente Verzeichnis kopiert")
            else:
                # Auch loggen wenn nichts kopiert wurde, weil bereits vorhanden
                existing_count = sum(1 for f in user_archetypen.rglob('*') if f.is_file())
                Logger.info(f"Archetypen: Bereits {existing_count} Datei(en) im Zielverzeichnis vorhanden")
        except Exception as e:
            Logger.error(f"Archetypen-Kopie fehlgeschlagen: {e}", exc_info=True)

    def _migrate_settings_on_android(self):
        """Migriert benutzerdefinierte Settings vom alten App-Verzeichnis ins persistente Verzeichnis auf Android."""
        from kivy.utils import platform as kivy_platform
        if kivy_platform != 'android':
            return

        try:
            from utils.path_utils import get_settings_path, get_user_settings_path
            import shutil

            old_settings_dir = Path(get_settings_path())
            new_settings_dir = Path(get_user_settings_path())

            # Neues Verzeichnis erstellen falls nötig
            new_settings_dir.mkdir(parents=True, exist_ok=True)

            # Nur migrieren wenn die Verzeichnisse unterschiedlich sind
            if old_settings_dir.exists() and old_settings_dir != new_settings_dir:
                # Mitgelieferte Settings-Namen ermitteln (diese nicht migrieren,
                # da sie sowieso immer aus dem nativen Verzeichnis geladen werden)
                native_settings = {f.stem for f in old_settings_dir.glob('*.json')}

                # Benutzerdefinierte Settings migrieren (custom_*.json und andere)
                migrated = 0
                for json_file in old_settings_dir.glob('*.json'):
                    target = new_settings_dir / json_file.name
                    if not target.exists():
                        shutil.copy2(str(json_file), str(target))
                        migrated += 1
                if migrated > 0:
                    Logger.info(f"Migration: {migrated} Setting(s) ins persistente Verzeichnis kopiert")
        except Exception as e:
            Logger.warning(f"Settings-Migration fehlgeschlagen: {e}")

    def _erstelle_auto_backup(self):
        """Erstellt ein automatisches Backup der Benutzerdaten beim App-Start."""
        try:
            from services.service_container import service_container
            backup_service = service_container.get_backup_service()
            if backup_service:
                backup_service.erstelle_backup()
        except Exception as e:
            Logger.warning(f"Auto-Backup fehlgeschlagen: {e}")

    def on_start(self):
        """Wird nach build() aufgerufen, wenn das Layout verfügbar ist."""
        Logger.info("=== App-Start gestartet ===")

        # Charaktere auf Android ins persistente Verzeichnis migrieren
        self._migrate_chars_on_android()

        # Settings auf Android ins persistente Verzeichnis migrieren
        self._migrate_settings_on_android()

        # Automatisches Backup der Benutzerdaten erstellen
        self._erstelle_auto_backup()

        # Fenster maximieren (nur Desktop — auf Android unnötig und kann
        # Race-Conditions bei der Layout-Initialisierung verursachen)
        from kivy.utils import platform as _platform
        if _platform != 'android':
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

        # KORRIGIERT: Tabs und Screens mit mehr Verzögerung für vollständige UI-Initialisierung
        # Window.bind(on_resize) wird NACH Tab-Setup in build_tabs_and_screens_immediate gebunden,
        # um Race-Condition bei Android-Startup zu vermeiden
        Clock.schedule_once(lambda dt: self.build_tabs_and_screens_immediate(), 0.5)

        # Android: Intent-Handler für empfangene JSON-Dateien registrieren
        self._setup_android_intent_handler()

        # Android: Gespeicherte Bildschirm-Orientierung anwenden
        self._apply_saved_orientation()

    def _check_and_show_welcome_tutorial(self):
        """Lädt Tutorial-Zustand und zeigt Willkommens-Tutorial bei Bedarf."""
        try:
            from services.service_container import service_container
            from views.tutorial_overlay import show_welcome_tutorial
            
            tutorial_service = service_container.get_tutorial_service()
            if not tutorial_service:
                Logger.warning("TutorialService nicht verfügbar")
                return
            
            # Tutorial-Zustand aus Config laden
            config_service = service_container.get_config_service()
            if config_service:
                tutorial_state = config_service.get('tutorial_state', {})
                tutorial_service.load_state(tutorial_state)
            
            # Willkommens-Tutorial bei Bedarf zeigen
            if tutorial_service.should_show_welcome():
                Logger.info("Zeige Willkommens-Tutorial...")
                Clock.schedule_once(lambda dt: show_welcome_tutorial(), 1.0)
            
        except Exception as e:
            Logger.error(f"Fehler beim Prüfen des Tutorial-Status: {e}")
    
    def _bind_wizard_events(self):
        """Bindet die Wizard-Events an UI-Updates."""
        if not self.wizard_service:
            return
        
        self.wizard_service.bind_event('on_wizard_started', self._on_wizard_started)
        self.wizard_service.bind_event('on_wizard_finished', self._on_wizard_finished)
        self.wizard_service.bind_event('on_wizard_cancelled', self._on_wizard_cancelled)
        self.wizard_service.bind_event('on_step_changed', self._on_wizard_step_changed)
        Logger.info("Wizard-Events gebunden")
    
    def _on_wizard_started(self, schritt):
        """Wird aufgerufen wenn der Wizard startet."""
        Logger.info("Wizard gestartet - UI aktualisieren")
        self._show_wizard_bar()
        if schritt:
            # Popup zuerst zeigen, dann nach Schließen den Dialog öffnen
            self._show_wizard_popup_and_then(schritt, self._open_new_char_dialog)
    
    def _show_wizard_popup_and_then(self, schritt, callback):
        """Zeigt das Wizard-Popup und ruft nach dem Schließen den Callback auf."""
        if not schritt or not schritt.popup_title:
            callback()
            return

        try:
            from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
            from kivymd.uix.button import MDButton, MDButtonText
            from kivymd.uix.scrollview import MDScrollView
            from kivymd.uix.label import MDLabel
            from kivy.metrics import dp

            content = MDBoxLayout(orientation="vertical", size_hint_y=None, adaptive_height=True)
            scroll = MDScrollView(size_hint_y=None, height="300dp")
            text_label = MDLabel(
                text=schritt.popup_text,
                theme_text_color="Primary",
                size_hint_y=None,
                adaptive_height=True,
            )
            scroll.add_widget(text_label)
            content.add_widget(scroll)

            # Debounce-Flag gegen doppeltes Feuern auf Android
            callback_fired = [False]

            def _on_verstanden(x):
                if callback_fired[0]:
                    return
                callback_fired[0] = True
                dialog.dismiss()
                callback()

            dialog = MDDialog(
                MDDialogHeadlineText(text=schritt.popup_title),
                MDDialogContentContainer(content),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(text="Verstanden"),
                        style="filled",
                        on_release=_on_verstanden
                    ),
                ),
                size_hint=(0.85, None),
            )
            dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Wizard-Popups: {e}")
            callback()
    
    def _on_wizard_finished(self):
        """Wird aufgerufen wenn der Wizard beendet wird."""
        Logger.info("Wizard beendet - UI aktualisieren")
        self._hide_wizard_bar()
    
    def _on_wizard_cancelled(self):
        """Wird aufgerufen wenn der Wizard abgebrochen wird."""
        Logger.info("Wizard abgebrochen - UI aktualisieren")
        self._hide_wizard_bar()
    
    def _on_wizard_step_changed(self, schritt):
        """Wird aufgerufen wenn sich der Wizard-Schritt ändert."""
        if not schritt:
            return
        
        Logger.info(f"Wizard-Schritt geändert: {schritt.tab_id} - {schritt.title}")
        
        if schritt.tab_id == 'neuer_charakter':
            # Zuerst zum Speichern/Laden Tab wechseln
            self._switch_to_tab_index(0)
            # Dann Dialog öffnen (verzögert, damit Tab-Wechsel abgeschlossen ist)
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._open_new_char_dialog(), 0.3)
        else:
            self._navigate_to_wizard_tab(schritt.tab_name)
    
    def _open_new_char_dialog(self):
        """Öffnet den Neuer-Charakter-Dialog nach dem Tab-Wechsel."""
        char_verwaltung = self._get_charakter_verwaltung_widget()
        Logger.info(f"CharakterVerwaltungWidget gefunden: {char_verwaltung is not None}")
        if char_verwaltung:
            Logger.info("Öffne Neuer-Charakter-Dialog...")
            char_verwaltung.create_new_character()
        else:
            Logger.error("CharakterVerwaltungWidget nicht gefunden!")
    
    def _get_charakter_verwaltung_widget(self):
        """Gibt das CharakterVerwaltungWidget zurück."""
        try:
            # Direkt über das App-Attribut (wird bei Screen-Erstellung gesetzt)
            if hasattr(self, 'charakter_verwaltung_widget') and self.charakter_verwaltung_widget:
                Logger.debug(f"Widget über App-Attribut gefunden: {self.charakter_verwaltung_widget}")
                return self.charakter_verwaltung_widget
            
            # Fallback: Über screen_instances
            if hasattr(self, 'screen_instances'):
                Logger.debug(f"screen_instances hat {len(self.screen_instances)} Einträge")
                for screen in self.screen_instances:
                    if hasattr(screen, 'ids') and 'charakter_verwaltung_widget' in screen.ids:
                        widget = screen.ids.charakter_verwaltung_widget
                        self.charakter_verwaltung_widget = widget
                        Logger.debug(f"Widget über screen_instances gefunden: {widget}")
                        return widget
            
            # Fallback: Über ScreenManager
            root = self.root
            if root:
                screen_manager = root.ids.get('tabs_carousel')
                if screen_manager and hasattr(screen_manager, 'screens'):
                    for screen in screen_manager.screens:
                        if hasattr(screen, 'ids') and 'charakter_verwaltung_widget' in screen.ids:
                            widget = screen.ids.charakter_verwaltung_widget
                            self.charakter_verwaltung_widget = widget
                            Logger.debug(f"Widget über ScreenManager.screens gefunden: {widget}")
                            return widget
                
                # Letzter Fallback: root.ids
                widget = root.ids.get('charakter_verwaltung_widget')
                if widget:
                    Logger.debug(f"Widget über root.ids gefunden: {widget}")
                    return widget
        except Exception as e:
            Logger.error(f"Fehler beim Suchen des CharakterVerwaltungWidget: {e}")
        Logger.warning("CharakterVerwaltungWidget konnte nicht gefunden werden")
        return None
    
    def _show_wizard_bar(self):
        """Zeigt die Wizard-Bar an."""
        try:
            wizard_bar = self.root.ids.get('wizard_bar')
            if wizard_bar:
                wizard_bar.opacity = 1
                wizard_bar.height = "56dp"
                Logger.debug("Wizard-Bar eingeblendet")
        except Exception as e:
            Logger.error(f"Fehler beim Einblenden der Wizard-Bar: {e}")
    
    def _hide_wizard_bar(self):
        """Blendet die Wizard-Bar aus."""
        try:
            wizard_bar = self.root.ids.get('wizard_bar')
            if wizard_bar:
                wizard_bar.opacity = 0
                wizard_bar.height = 0
                Logger.debug("Wizard-Bar ausgeblendet")
        except Exception as e:
            Logger.error(f"Fehler beim Ausblenden der Wizard-Bar: {e}")
    
    def _navigate_to_wizard_tab(self, tab_name):
        """Navigiert zum Wizard-Tab."""
        if not tab_name:
            return
        
        tab_name_to_index = {
            'Neuer Charakter': 0,
            'Völker': 2,
            'Profil': 3,
            'Eigenschaften': 4,
            'Handicaps': 5,
            'Talente': 6,
            'Mächte': 7,
            'Ausrüstung': 9,
            'Charakterbogen': 10,
            'Historie': 11,
            'Info': 12,
        }
        
        index = tab_name_to_index.get(tab_name)
        if index is not None:
            self._switch_to_tab_index(index)

    def _setup_android_intent_handler(self):
        """Registriert den Android Intent-Handler für eingehende Dateien (Teilen/Öffnen mit)."""
        from kivy.utils import platform as kivy_platform
        if kivy_platform != 'android':
            return

        try:
            from utils.intent_handler import handle_incoming_intent, handle_new_intent

            # Intent verarbeiten, mit dem die App gestartet wurde
            # Verzögert, damit UI vollständig initialisiert ist
            Clock.schedule_once(lambda dt: handle_incoming_intent(self), 2.0)

            # Listener für neue Intents registrieren (App bereits im Vordergrund)
            # WICHTIG: android.activity.bind() nutzt registerNewIntentListener()
            # und erzeugt einen Java NewIntentListener — PythonActivity.mActivity.bind()
            # ist NICHT dasselbe und funktioniert nicht für on_new_intent.
            from android import activity as android_activity

            # Callback als benannte Funktion, damit GC die Referenz nicht verliert
            def _on_new_intent(intent):
                handle_new_intent(self, intent)

            self._intent_callback = _on_new_intent  # Referenz halten
            android_activity.bind(on_new_intent=_on_new_intent)
            Logger.info("Android Intent-Handler registriert (via android.activity.bind)")

        except ImportError:
            Logger.info("android.activity nicht verfügbar (kein Android)")
        except Exception as e:
            Logger.warning(f"Android Intent-Handler konnte nicht registriert werden: {e}")

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

            # NavigationRail und Bottom-Navigation aufbauen und initialen Modus setzen
            self.build_navigation_rail()
            self.build_bottom_navigation()
            self._setup_swipe_navigation(screen_manager)
            self._apply_initial_navigation_mode()

            # Fenster-Resize-Event NACH initialer Navigation binden
            # (verhindert Race-Condition bei Android-Startup)
            Window.bind(on_resize=self._on_window_resize)

            # Superkräfte-Tab-Sichtbarkeit an Setting binden
            if self.controller:
                self.controller.bind(on_setting_changed=self._on_setting_changed_update_tabs)
                # Initial prüfen
                Clock.schedule_once(lambda dt: self._on_setting_changed_update_tabs(
                    self.controller, getattr(self.controller.charakter, 'active_setting_name', '')), 0.5)

            # Tutorial-Zustand laden und Willkommens-Tutorial bei Bedarf zeigen
            self._check_and_show_welcome_tutorial()

        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der Tabs und Screens: {str(e)}", exc_info=True)

    def _on_setting_changed_update_tabs(self, instance, setting_name):
        """Blendet den Superkräfte-Tab je nach Setting ein oder aus."""
        try:
            from functions.superkraft_funktionen import ist_superkraefte_setting
            is_sk = ist_superkraefte_setting(setting_name)

            # Finde den Superkräfte-Tab-Index in tab_definitions
            sk_index = None
            for i, (icon_str, tab_text, screen_class) in enumerate(self.tab_definitions):
                if tab_text == "Superkräfte":
                    sk_index = i
                    break

            if sk_index is None or sk_index >= len(self.tab_items):
                return

            tab_item = self.tab_items[sk_index]

            if is_sk:
                # Tab einblenden
                tab_item.opacity = 1
                tab_item.disabled = False
                tab_item.size_hint_x = None
                tab_item.width = tab_item._original_width if hasattr(tab_item, '_original_width') else dp(120)
            else:
                # Tab ausblenden - Originalbreite merken
                if not hasattr(tab_item, '_original_width') or tab_item.width > 0:
                    tab_item._original_width = tab_item.width
                tab_item.opacity = 0
                tab_item.disabled = True
                tab_item.size_hint_x = None
                tab_item.width = 0

            # NavigationRail aktualisieren
            self._update_rail_superkraefte_visibility(is_sk)

            Logger.info(f"Superkräfte-Tab {'eingeblendet' if is_sk else 'ausgeblendet'} für Setting '{setting_name}'")
        except Exception as e:
            Logger.error(f"Fehler bei Tab-Sichtbarkeit: {e}")

    def _update_rail_superkraefte_visibility(self, visible):
        """Aktualisiert die Sichtbarkeit des Superkräfte-Eintrags in der NavigationRail."""
        try:
            rail = self.root.ids.get('nav_rail_content') if self.root else None
            if not rail:
                return

            # Finde den Superkräfte-Index
            sk_index = None
            for i, (_, tab_text, _) in enumerate(self.tab_definitions):
                if tab_text == "Superkräfte":
                    sk_index = i
                    break

            if sk_index is None:
                return

            for child in rail.children:
                if hasattr(child, '_rail_index') and child._rail_index == sk_index:
                    if visible:
                        child.opacity = 1
                        child.disabled = False
                        child.height = dp(64)
                    else:
                        child.opacity = 0
                        child.disabled = True
                        child.height = 0
                    break
        except Exception as e:
            Logger.debug(f"Rail-Update für Superkräfte: {e}")

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

            # Tab-Index tracken und Bottom-Nav aktualisieren
            self._current_tab_index = tab_index
            self._set_active_bottom_nav_item(tab_index)

            # ScreenManager-Screen setzen
            root = self.root
            if root and root.ids.get('tabs_carousel'):
                screen_manager = root.ids['tabs_carousel']

                # WICHTIG: NoTransition für Tab-Bar-Klicks setzen um
                # Animations-Konflikte mit vorherigen Swipe-Transitionen zu vermeiden
                screen_manager.transition = NoTransition()

                # Get screen name from tab index
                if 0 <= tab_index < len(self.tab_definitions):
                    tab_text = self.tab_definitions[tab_index][1]
                    clean_name = tab_text.lower().replace(' ', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
                    screen_name = f"screen_{tab_index}_{clean_name}"

                    # Screen suchen und wechseln - getrennte try-Blöcke
                    # damit ein Transitionsfehler keinen neuen Screen erzeugt
                    screen_exists = False
                    if hasattr(screen_manager, 'get_screen'):
                        try:
                            screen_manager.get_screen(screen_name)
                            screen_exists = True
                        except Exception:
                            Logger.warning(f"Screen '{screen_name}' nicht gefunden, erstelle neu...")

                        if screen_exists:
                            screen_manager.current = screen_name
                        else:
                            # Screen dynamisch erstellen (nur bei echtem ScreenNotFound)
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
                                    # Widget-Registrierung für den neuen Screen
                                    self._register_widget_for_compatibility(new_screen, tab_text)
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

    def build_bottom_navigation(self):
        """Erstellt die Bottom-Navigation-Leiste für den Portrait-Modus.

        Zeigt die 5 wichtigsten Screens direkt und einen 'Mehr'-Button
        für alle weiteren Screens.
        """
        try:
            root = self.root
            if not root:
                return

            bottom_nav_box = root.ids.get('bottom_nav_box')
            if not bottom_nav_box:
                Logger.warning("bottom_nav_box nicht im Layout gefunden")
                return

            bottom_nav_box.clear_widgets()
            self._bottom_nav_items = []
            self._bottom_nav_tab_indices = []

            # Die 5 wichtigsten Tabs für direkte Bottom-Navigation
            # (Index in tab_definitions, Icon, Kurzname)
            bottom_nav_definitions = [
                (4,  "arm-flex",          "Werte"),
                (5,  "account-alert",     "Handicaps"),
                (6,  "star-circle",       "Talente"),
                (7,  "creation-outline",  "Mächte"),
                (9,  "shield-sword",      "Ausrüst."),
            ]

            for tab_index, icon_str, short_label in bottom_nav_definitions:
                item = MDBoxLayout(
                    orientation='vertical',
                    size_hint=(1, 1),
                    padding=[0, dp(2), 0, 0],
                )
                item._bottom_nav_tab_index = tab_index

                icon = MDIcon(
                    icon=icon_str,
                    halign='center',
                    pos_hint={'center_x': 0.5},
                    size_hint_y=None,
                    height=dp(24),
                )
                icon._is_nav_icon = True

                label = MDLabel(
                    text=short_label,
                    halign='center',
                    font_style='Label',
                    role='small',
                    size_hint_y=None,
                    height=dp(16),
                )
                label._is_nav_label = True

                item.add_widget(icon)
                item.add_widget(label)
                # on_touch_down statt on_touch_up: Bottom-Bar liegt NICHT in einem
                # ScrollView, daher ist sofortige Reaktion möglich und zuverlässiger.
                item.bind(on_touch_down=self._on_bottom_nav_touch)

                bottom_nav_box.add_widget(item)
                self._bottom_nav_items.append(item)
                self._bottom_nav_tab_indices.append(tab_index)

            # "Mehr"-Button hinzufügen
            mehr_item = MDBoxLayout(
                orientation='vertical',
                size_hint=(1, 1),
                padding=[0, dp(2), 0, 0],
            )
            mehr_item._bottom_nav_tab_index = -1  # Spezialwert für "Mehr"

            mehr_icon = MDIcon(
                icon="dots-horizontal",
                halign='center',
                pos_hint={'center_x': 0.5},
                size_hint_y=None,
                height=dp(24),
            )
            mehr_icon._is_nav_icon = True

            mehr_label = MDLabel(
                text="Mehr",
                halign='center',
                font_style='Label',
                role='small',
                size_hint_y=None,
                height=dp(16),
            )
            mehr_label._is_nav_label = True

            mehr_item.add_widget(mehr_icon)
            mehr_item.add_widget(mehr_label)
            mehr_item.bind(on_touch_down=self._on_bottom_nav_touch)

            bottom_nav_box.add_widget(mehr_item)
            self._bottom_nav_items.append(mehr_item)

            Logger.info(f"Bottom-Navigation mit {len(self._bottom_nav_items)} Items erstellt")

        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der Bottom-Navigation: {str(e)}", exc_info=True)

    def _on_bottom_nav_touch(self, item, touch):
        """Callback wenn ein Bottom-Nav-Item angetippt wird"""
        if not item.collide_point(*touch.pos):
            return False

        # Scroll-Gesten ignorieren
        if hasattr(touch, 'is_mouse_scrolling') and touch.is_mouse_scrolling:
            return False

        # Debounce: 500ms (Android-Standard, verhindert Doppel-Taps)
        import time as _time
        now = _time.time()
        if now - self._last_rail_touch_time < 0.5:
            return True
        self._last_rail_touch_time = now

        try:
            tab_index = item._bottom_nav_tab_index

            if tab_index == -1:
                # "Mehr"-Button: Alle Screens anzeigen
                self._show_more_screens_popup()
                return True

            # Zum Screen wechseln
            root = self.root
            if not root:
                return False

            screen_manager = root.ids.get('tabs_carousel')
            if not screen_manager:
                return False

            if 0 <= tab_index < len(self.tab_definitions):
                tab_text = self.tab_definitions[tab_index][1]
                clean_name = tab_text.lower().replace(' ', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
                screen_name = f"screen_{tab_index}_{clean_name}"

                screen_manager.transition = NoTransition()
                try:
                    screen_manager.get_screen(screen_name)
                    screen_manager.current = screen_name
                except Exception:
                    Logger.warning(f"Screen '{screen_name}' nicht gefunden")
                    return True

                self._current_tab_index = tab_index
                self._set_active_bottom_nav_item(tab_index)
                self._set_active_rail_item(tab_index)
                self.update_active_screen(tab_index)

                Logger.info(f"Bottom-Nav-Wechsel zu: {tab_text}")

            return True

        except Exception as e:
            Logger.error(f"Fehler beim Bottom-Nav-Wechsel: {str(e)}")
            return False

    def _set_active_bottom_nav_item(self, active_tab_index):
        """Hebt das aktive Bottom-Nav-Item visuell hervor"""
        try:
            for item in self._bottom_nav_items:
                tab_idx = getattr(item, '_bottom_nav_tab_index', None)
                is_active = (tab_idx == active_tab_index)
                # Aktives Item hervorheben durch Farbe der Icon/Label-Kinder
                for child in item.children:
                    if hasattr(child, '_is_nav_icon') and child._is_nav_icon:
                        if is_active:
                            child.theme_icon_color = "Custom"
                            child.icon_color = self.theme_cls.primaryColor
                        else:
                            child.theme_icon_color = "Custom"
                            child.icon_color = self.theme_cls.onSurfaceVariantColor
                    elif hasattr(child, '_is_nav_label') and child._is_nav_label:
                        if is_active:
                            child.theme_text_color = "Custom"
                            child.text_color = self.theme_cls.primaryColor
                        else:
                            child.theme_text_color = "Custom"
                            child.text_color = self.theme_cls.onSurfaceVariantColor
        except Exception as e:
            Logger.debug(f"Fehler bei Bottom-Nav-Highlighting: {e}")

    def _show_more_screens_popup(self):
        """Zeigt ein Popup mit allen verfügbaren Screens als Grid"""
        try:
            from kivy.uix.modalview import ModalView
            from kivy.uix.gridlayout import GridLayout
            from kivy.uix.behaviors import ButtonBehavior

            # ModalView erstellen (halbtransparenter Hintergrund)
            popup = ModalView(
                size_hint=(1, None),
                height=dp(420),
                pos_hint={'y': 0},
                background_color=(0, 0, 0, 0.5),
                auto_dismiss=True,
            )

            # Container mit Hintergrundfarbe
            container = MDBoxLayout(
                orientation='vertical',
                md_bg_color=self.theme_cls.surfaceContainerHighColor,
                padding=[dp(12), dp(16), dp(12), dp(12)],
                spacing=dp(8),
                radius=[dp(20), dp(20), 0, 0],
            )

            # Titel-Leiste mit Schließen-Button
            header = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(36),
            )
            title_label = MDLabel(
                text="Alle Screens",
                font_style='Title',
                role='medium',
                halign='left',
                valign='center',
            )
            close_btn = MDIconButton(
                icon="close",
                style="standard",
                size_hint=(None, None),
                size=(dp(36), dp(36)),
                pos_hint={'center_y': 0.5},
                on_release=lambda x: popup.dismiss(),
            )
            header.add_widget(title_label)
            header.add_widget(close_btn)
            container.add_widget(header)

            # Scrollbarer Grid-Bereich
            scroll = ScrollView(
                do_scroll_x=False,
                do_scroll_y=True,
            )

            grid = GridLayout(
                cols=4,
                size_hint_y=None,
                spacing=dp(8),
                padding=[0, dp(8), 0, dp(8)],
            )
            grid.bind(minimum_height=grid.setter('height'))

            for i, (icon_str, tab_text, _) in enumerate(self.tab_definitions):

                grid_item = MDBoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(72),
                    padding=[dp(4), dp(8), dp(4), dp(4)],
                    spacing=dp(2),
                )
                grid_item._popup_tab_index = i

                # Aktiven Screen hervorheben
                if i == self._current_tab_index:
                    grid_item.md_bg_color = self.theme_cls.secondaryContainerColor
                    grid_item.radius = [dp(12)]

                icon = MDIcon(
                    icon=icon_str,
                    halign='center',
                    pos_hint={'center_x': 0.5},
                    size_hint_y=None,
                    height=dp(28),
                )

                # Kurzname für Grid
                short_names = {
                    "Speichern/Laden": "Speichern",
                    "Einstellungen": "Settings",
                    "Eigenschaften": "Werte",
                    "Ausrüstung": "Ausrüst.",
                    "Superkräfte": "S-Kräfte",
                }
                display_name = short_names.get(tab_text, tab_text)

                label = MDLabel(
                    text=display_name,
                    halign='center',
                    font_style='Label',
                    role='small',
                    size_hint_y=None,
                    height=dp(24),
                    text_size=(dp(80), None),
                )

                grid_item.add_widget(icon)
                grid_item.add_widget(label)

                # Touch-Handler mit Closure für Index
                def make_touch_handler(idx, p):
                    def handler(inst, touch):
                        if inst.collide_point(*touch.pos):
                            p.dismiss()
                            self._switch_to_tab_from_popup(idx)
                            return True
                        return False
                    return handler

                grid_item.bind(on_touch_up=make_touch_handler(i, popup))
                grid.add_widget(grid_item)

            scroll.add_widget(grid)
            container.add_widget(scroll)

            # Schnellaktionen: Speichern + Beenden
            actions = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(48),
                spacing=dp(8),
                padding=[dp(8), dp(4), dp(8), 0],
            )

            save_item = MDBoxLayout(
                orientation='horizontal',
                size_hint=(1, 1),
                spacing=dp(4),
            )
            save_icon = MDIcon(
                icon="content-save",
                halign='center',
                pos_hint={'center_y': 0.5},
                size_hint_x=None,
                width=dp(24),
            )
            save_label = MDLabel(
                text="Schnellspeichern",
                font_style='Label',
                role='medium',
                halign='left',
                valign='center',
            )
            save_item.add_widget(save_icon)
            save_item.add_widget(save_label)

            def on_save_touch(inst, touch):
                if inst.collide_point(*touch.pos):
                    popup.dismiss()
                    self.quick_save()
                    return True
                return False

            save_item.bind(on_touch_up=on_save_touch)
            actions.add_widget(save_item)

            container.add_widget(actions)
            popup.add_widget(container)
            popup.open()

        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Mehr-Popups: {str(e)}", exc_info=True)

    def _switch_to_tab_from_popup(self, index):
        """Wechselt zum Tab nach Auswahl im Mehr-Popup"""
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

            screen_manager.transition = NoTransition()
            try:
                screen_manager.get_screen(screen_name)
                screen_manager.current = screen_name
            except Exception:
                Logger.warning(f"Screen '{screen_name}' nicht gefunden")
                return

            self._current_tab_index = index
            self._set_active_bottom_nav_item(index)
            if index < len(self.rail_items):
                self._set_active_rail_item(index)
            self.update_active_screen(index)

            Logger.info(f"Popup-Wechsel zu: {tab_text}")

        except Exception as e:
            Logger.error(f"Fehler bei Tab-Wechsel aus Popup: {str(e)}")

    def _on_rail_item_touch(self, item, touch):
        """Callback wenn ein Rail-Item losgelassen wird (touch_up).

        Verwendet on_touch_up statt on_touch_down, damit ScrollView
        Scroll-Gesten verarbeiten kann (Android-Kompatibilität).
        """
        if not item.collide_point(*touch.pos):
            # Lenienter Fallback: Startposition prüfen (Android-Fingerdrift beim Loslassen)
            if not item.collide_point(*touch.opos):
                return False

        # Scroll-Gesten ignorieren (nur Taps verarbeiten)
        if hasattr(touch, 'is_mouse_scrolling') and touch.is_mouse_scrolling:
            return False
        if touch.grab_current is not None and touch.grab_current is not item:
            return False

        # Debounce: Doppelte Touch-Events innerhalb 500ms ignorieren
        import time as _time
        now = _time.time()
        if now - self._last_rail_touch_time < 0.5:
            return True
        self._last_rail_touch_time = now

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
                self._set_active_bottom_nav_item(item_index)
                self._current_tab_index = item_index
                self.update_active_screen(item_index)

                # In Portrait-Modus Rail nach Auswahl automatisch schließen
                is_portrait = Window.height > Window.width
                if is_portrait and self._nav_rail_visible:
                    self.toggle_navigation_rail()

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
        Wechselt zwischen Desktop-Tabs und mobiler Navigation.

        Desktop: Immer obere Tab-Leiste, keine Bottom-Bar, kein Rail.
        Mobile Portrait: Bottom-Bar (kein Rail, keine Tabs).
        Mobile Landscape: NavigationRail (keine Bottom-Bar, keine Tabs).

        Args:
            mobile (bool): True für mobile Navigation, False für Desktop-Tabs
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
            bottom_bar = root.ids.get('bottom_bar_container')

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

            # Modus-Flag ZUERST setzen (wird von _update_mobile_orientation benötigt)
            self._mobile_modus_active = mobile

            if mobile:
                # Tabs verstecken — Container UND MDTabsPrimary kollabieren,
                # damit die Tab-Widgets nicht über den Container hinausragen
                # und Touch-Events im Pointbar-Bereich abfangen (Kivy
                # dispatcht Touches an Kinder auch wenn der Eltern-Container
                # height=0 hat).
                tabs_container.height = 0
                tabs_container.opacity = 0
                tabs_bar = root.ids.get('tabs_bar')
                if tabs_bar:
                    tabs_bar.size_hint_y = None
                    tabs_bar.height = 0
                    tabs_bar.opacity = 0

                # Menü-Toggle-Button verstecken
                if menu_toggle:
                    menu_toggle.width = 0
                    menu_toggle.opacity = 0

                # Content-Padding reduzieren
                tab_content_box.padding = [dp(4), 0, dp(4), dp(4)]

                # Android: Top-Padding auf äußerstes Layout für Statusbar/Notch
                from kivy.utils import platform as _platform
                if _platform == 'android':
                    outer_box = root.ids.get('outer_box')
                    if outer_box:
                        outer_box.padding = [0, self._android_top_padding, 0, 0]

                    # Swipe nur auf Android aktivieren
                    if screen_manager and hasattr(screen_manager, 'swipe_enabled'):
                        screen_manager.swipe_enabled = True

                # Orientierung bestimmt ob Rail oder Bottom-Bar
                self._update_mobile_orientation()

                # Aktive Items hervorheben
                if current_index < len(self.rail_items):
                    self._set_active_rail_item(current_index)
                self._set_active_bottom_nav_item(current_index)

                Logger.info("Mobile Navigation aktiviert")
            else:
                # NavigationRail verstecken
                nav_rail_container.width = 0
                nav_rail_container.opacity = 0
                self._nav_rail_visible = False

                # Menü-Toggle-Button verstecken
                if menu_toggle:
                    menu_toggle.width = 0
                    menu_toggle.opacity = 0

                # Bottom-Bar verstecken
                if bottom_bar:
                    bottom_bar.height = 0
                    bottom_bar.opacity = 0

                # Tabs zeigen (Container + MDTabsPrimary wiederherstellen)
                tabs_container.height = dp(64)
                tabs_container.opacity = 1
                tabs_bar = root.ids.get('tabs_bar')
                if tabs_bar:
                    tabs_bar.size_hint_y = 1
                    tabs_bar.height = dp(48)
                    tabs_bar.opacity = 1

                # Content-Padding wiederherstellen
                tab_content_box.padding = [dp(30), 0, dp(30), dp(30)]

                # Swipe deaktivieren
                if screen_manager and hasattr(screen_manager, 'swipe_enabled'):
                    screen_manager.swipe_enabled = False

                # Aktiven Tab setzen (ohne erneuten Screen-Wechsel)
                if current_index < len(self.tab_items):
                    self.tab_items[current_index].active = True

                Logger.info("Desktop-Tabs aktiviert")

        except Exception as e:
            Logger.error(f"Fehler beim Moduswechsel: {str(e)}", exc_info=True)

    def _apply_initial_navigation_mode(self):
        """Wendet den initialen Navigationsmodus basierend auf Config an.

        Desktop: Immer Tabs, außer mobile_modus in Config ist True.
        Android: Immer mobile Navigation (Bottom-Bar/Rail je nach Orientierung).
        """
        try:
            from kivy.utils import platform as _platform
            from services.service_container import get_config_service
            config_service = get_config_service()

            if config_service:
                mobile_modus = config_service.get('mobile_modus', False)

                if _platform == 'android':
                    # Android: Immer mobile Navigation
                    self._mobile_modus_override = True
                    self.set_navigation_mode(True)
                    Logger.info("Android: Mobile Navigation aktiviert")
                elif mobile_modus:
                    # Desktop mit explizit aktiviertem Mobile-Modus (Einstellungen)
                    self._mobile_modus_override = True
                    self.set_navigation_mode(True)
                    Logger.info("Mobiler Modus aus Config geladen")
                # else: Desktop bleibt im Tab-Modus (Standard)

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

    def _update_mobile_orientation(self):
        """Aktualisiert die Navigation basierend auf Portrait/Landscape im Mobile-Modus.

        Portrait: Bottom-Bar mit Padding für System-Navigationsleiste.
        Landscape: NavigationRail links, keine Bottom-Bar.
        """
        try:
            root = self.root
            if not root or not self._mobile_modus_active:
                return

            nav_rail_container = root.ids.get('nav_rail_container')
            if not nav_rail_container:
                return

            is_portrait = Window.height > Window.width
            bottom_bar = root.ids.get('bottom_bar_container')

            # Pointbar im Landscape zuklappen, im Portrait aufklappen
            pointbar = root.ids.get('generation_points')

            if is_portrait:
                # Portrait: Rail verstecken, Bottom-Bar anzeigen
                nav_rail_container.width = 0
                nav_rail_container.opacity = 0
                self._nav_rail_visible = False
                if bottom_bar:
                    # Höhe = Inhalt (64dp) + Platz für System-Navigationsleiste
                    # 64dp statt 56dp für bessere Touch-Zielfläche auf Android
                    bottom_bar.height = dp(64) + self._android_bottom_padding
                    bottom_bar.padding = [0, dp(4), 0, self._android_bottom_padding]
                    bottom_bar.opacity = 1
                if pointbar:
                    pointbar.is_expanded = True
                Logger.debug("Mobile Portrait: Rail versteckt, Bottom-Bar sichtbar")
            else:
                # Landscape: Rail anzeigen, Bottom-Bar verstecken, Pointbar zuklappen
                nav_rail_container.width = dp(92)
                nav_rail_container.opacity = 1
                self._nav_rail_visible = True
                if bottom_bar:
                    bottom_bar.height = 0
                    bottom_bar.opacity = 0
                if pointbar:
                    pointbar.is_expanded = False
                Logger.debug("Mobile Landscape: Rail sichtbar, Bottom-Bar versteckt")

        except Exception as e:
            Logger.error(f"Fehler bei Orientierungs-Update: {str(e)}")

    def set_screen_orientation(self, orientation='auto', locked=False):
        """Setzt die Bildschirm-Orientierung auf Android.

        Args:
            orientation: 'auto', 'portrait' oder 'landscape'
            locked: True = fixiert, False = flexibel (System-Einstellung beachten)
        """
        try:
            from kivy.utils import platform as _platform
            if _platform != 'android':
                Logger.info(f"Orientierung ignoriert (kein Android): {orientation}, locked={locked}")
                return

            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            # Android ActivityInfo Orientierungs-Konstanten
            SCREEN_ORIENTATION_USER = 2           # System-Einstellung beachten
            SCREEN_ORIENTATION_PORTRAIT = 1       # Portrait fixiert
            SCREEN_ORIENTATION_LANDSCAPE = 0      # Landscape fixiert
            SCREEN_ORIENTATION_SENSOR_PORTRAIT = 7   # Portrait (beide Richtungen)
            SCREEN_ORIENTATION_SENSOR_LANDSCAPE = 6  # Landscape (beide Richtungen)

            if not locked:
                # Flexibel: System-Einstellung beachten
                requested = SCREEN_ORIENTATION_USER
                Logger.info("Orientierung: flexibel (System-Einstellung)")
            elif orientation == 'portrait':
                requested = SCREEN_ORIENTATION_SENSOR_PORTRAIT
                Logger.info("Orientierung: Portrait fixiert")
            elif orientation == 'landscape':
                requested = SCREEN_ORIENTATION_SENSOR_LANDSCAPE
                Logger.info("Orientierung: Landscape fixiert")
            else:
                # auto + locked: System-Einstellung beachten
                requested = SCREEN_ORIENTATION_USER
                Logger.info("Orientierung: Auto (System-Einstellung)")

            activity.setRequestedOrientation(requested)

        except ImportError:
            Logger.info("jnius nicht verfügbar (kein Android)")
        except Exception as e:
            Logger.warning(f"Fehler beim Setzen der Bildschirm-Orientierung: {e}")

    def _apply_saved_orientation(self):
        """Wendet die gespeicherte Orientierungs-Einstellung an."""
        try:
            config_service = service_container.get_config_service()
            if not config_service:
                return

            orientation = config_service.get('screen_orientation', 'auto')
            locked = config_service.get('screen_orientation_locked', False)
            self.set_screen_orientation(orientation, locked)
        except Exception as e:
            Logger.warning(f"Fehler beim Anwenden der gespeicherten Orientierung: {e}")

    def _detect_android_top_padding(self):
        """Ermittelt die Statusbar/Notch-Höhe auf Android für korrektes Top-Padding"""
        try:
            from kivy.utils import platform as _platform
            if _platform != 'android':
                return

            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            resources = activity.getResources()

            # Statusbar-Höhe abfragen
            resource_id = resources.getIdentifier(
                'status_bar_height', 'dimen', 'android'
            )
            if resource_id > 0:
                status_bar_px = resources.getDimensionPixelSize(resource_id)
                # Pixel zu dp umrechnen
                density = resources.getDisplayMetrics().density
                status_bar_dp = status_bar_px / density if density > 0 else 24

                # Display-Cutout (Notch) prüfen - API 28+
                cutout_dp = 0
                try:
                    Build_VERSION = autoclass('android.os.Build$VERSION')
                    if Build_VERSION.SDK_INT >= 28:
                        window = activity.getWindow()
                        decorView = window.getDecorView()
                        rootInsets = decorView.getRootWindowInsets()
                        if rootInsets:
                            cutout = rootInsets.getDisplayCutout()
                            if cutout:
                                cutout_top_px = cutout.getSafeInsetTop()
                                cutout_dp = cutout_top_px / density if density > 0 else 0
                except Exception:
                    pass

                # Das Maximum von Statusbar und Cutout verwenden + kleiner Puffer
                top_dp = max(status_bar_dp, cutout_dp) + 4
                self._android_top_padding = dp(top_dp)
                Logger.info(
                    f"Android Top-Padding: {top_dp:.0f}dp "
                    f"(Statusbar: {status_bar_dp:.0f}dp, Cutout: {cutout_dp:.0f}dp)"
                )
            else:
                Logger.warning("Android: status_bar_height Resource nicht gefunden, verwende Fallback")
        except ImportError:
            Logger.info("jnius nicht verfügbar (kein Android), verwende Fallback-Padding")
        except Exception as e:
            Logger.warning(f"Android Top-Padding Erkennung fehlgeschlagen: {e}, verwende Fallback")

    def _detect_android_bottom_padding(self):
        """Ermittelt die System-Navigationsleisten-Höhe auf Android für Bottom-Padding"""
        try:
            from kivy.utils import platform as _platform
            if _platform != 'android':
                return

            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            resources = activity.getResources()

            # Navigation-Bar-Höhe abfragen
            resource_id = resources.getIdentifier(
                'navigation_bar_height', 'dimen', 'android'
            )
            if resource_id > 0:
                nav_bar_px = resources.getDimensionPixelSize(resource_id)
                density = resources.getDisplayMetrics().density
                nav_bar_dp = nav_bar_px / density if density > 0 else 24

                # Sicherheitspuffer hinzufügen
                bottom_dp = nav_bar_dp + 4
                self._android_bottom_padding = dp(bottom_dp)
                Logger.info(
                    f"Android Bottom-Padding: {bottom_dp:.0f}dp "
                    f"(Navigationsleiste: {nav_bar_dp:.0f}dp)"
                )
            else:
                Logger.warning("Android: navigation_bar_height Resource nicht gefunden, verwende Fallback")
        except ImportError:
            Logger.info("jnius nicht verfügbar (kein Android), verwende Fallback-Padding")
        except Exception as e:
            Logger.warning(f"Android Bottom-Padding Erkennung fehlgeschlagen: {e}, verwende Fallback")

    def _on_window_resize(self, instance, width, height):
        """Reagiert auf Fenster-Resize.

        Desktop: Kein automatischer Moduswechsel (Tabs bleiben immer).
        Android/Mobile: Orientierung aktualisieren (Portrait ↔ Landscape).
        """
        try:
            from kivy.utils import platform as _platform

            # Auf Android/Mobile: Orientierung bei Rotation aktualisieren
            if self._mobile_modus_active:
                self._update_mobile_orientation()

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

    def _is_tab_swipeable(self, index):
        """Gibt True zurück, wenn der Tab per Swipe erreichbar sein soll."""
        if index < 0 or index >= len(self.tab_definitions):
            return False
        # Ausgeblendete Tabs (z.B. Superkräfte bei nicht passendem Setting) überspringen
        if index < len(self.tab_items) and self.tab_items[index].disabled:
            return False
        return True

    def _on_swipe(self, direction):
        """Callback für Swipe-Gesten auf dem Content-Bereich"""
        try:
            if not self._mobile_modus_active:
                return

            num_tabs = len(self.tab_definitions)
            if num_tabs == 0:
                return

            step = 1 if direction == 'left' else -1 if direction == 'right' else None
            if step is None:
                return

            new_index = self._current_tab_index + step
            # Überspringe deaktivierte Tabs (z.B. Superkräfte bei nicht passendem Setting)
            while 0 <= new_index < num_tabs and not self._is_tab_swipeable(new_index):
                new_index += step

            if new_index < 0 or new_index >= num_tabs:
                return  # Rand erreicht, nicht wrappen

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

            # NavigationRail- und Bottom-Nav-Highlight aktualisieren
            if index < len(self.rail_items):
                self._set_active_rail_item(index)
            self._set_active_bottom_nav_item(index)

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
                nav_rail_container.width = dp(120)
                nav_rail_container.opacity = 1
                self._nav_rail_visible = True
                Logger.info("NavigationRail eingeblendet")
        except Exception as e:
            Logger.error(f"Fehler beim Toggle der NavigationRail: {str(e)}")

    def quick_save(self):
        """Schnellspeichern über die Bottom-Bar"""
        try:
            if hasattr(self, 'charakter_verwaltung_widget') and self.charakter_verwaltung_widget:
                self.charakter_verwaltung_widget.schnellspeichern_charakter()
            else:
                Logger.warning("CharakterVerwaltungWidget nicht verfügbar für Schnellspeichern")
        except Exception as e:
            Logger.error(f"Fehler beim Schnellspeichern: {str(e)}")

    def quit_app(self):
        """Beendet die App"""
        try:
            Logger.info("App wird beendet über Bottom-Bar")
            self.stop()
        except Exception as e:
            Logger.error(f"Fehler beim Beenden: {str(e)}")

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
                
                elif tab_name == 'Superkräfte' and 'superkraefte_widget' in screen_instance.ids:
                    widget = screen_instance.ids.superkraefte_widget
                    self.superkraefte_widget = widget
                    Logger.debug("SuperkraefteWidget bei App registriert")

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
            ],
            size_hint=(0.85, None),
            auto_dismiss=False,
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
                'Superkräfte': getattr(self, 'superkraefte_widget', None),
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