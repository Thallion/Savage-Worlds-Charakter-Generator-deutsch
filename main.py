"""
main.py: SW_Charakter_GeneratorApp mit KivyMD Tabs, Carousel, GenerationPointsBar und Logger.
REFACTORED: Screen-Klassen nach views/screens.py extrahiert
"""

import sys
import os
import logging
import time
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
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition

# Scrollbalken-Defaults anheben, BEVOR die ersten Widgets erzeugt werden.
# Kivy-Default ist 2dp — auf Android nicht greifbar. Explizite Werte in
# Views/KV-Dateien gewinnen weiterhin.
from utils.scrollbar_defaults import apply_scrollbar_defaults
apply_scrollbar_defaults()


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
from views.pointbar_overlay import PointbarOverlay
from kivy.lang import Builder
from utils.path_utils import get_application_root, get_resource_path
import os
from views.charakter_verwaltung_widget import CharakterVerwaltungWidget

# Wizard-Bar KV laden (Mobile oder Desktop)
from utils.platform_utils import get_kv_filename as _get_kv_filename, is_mobile_layout
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


from views.app_navigation_mixin import AppNavigationMixin
from views.app_tab_mixin import AppTabAufbauMixin


class SW_Charakter_GeneratorApp(AppNavigationMixin, AppTabAufbauMixin, MDApp):
    controller = ObjectProperty(None)
    wizard_service = ObjectProperty(None)
    use_pointbar_overlay = BooleanProperty(False)  # True für Android/Mobile, False für Desktop
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
            ("account-group",    "Abstammungen",         VoelkerScreen),
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

            # Alte Charaktere migrieren (nur wenn alte Dateien existieren).
            # Eigener try-Block, damit ein Fehler hier die Archetypen-Kopie
            # nicht verhindert.
            try:
                if old_chars_dir.exists() and old_chars_dir != new_chars_dir:
                    migrated = 0
                    for json_file in old_chars_dir.glob('*.json'):
                        target = new_chars_dir / json_file.name
                        if not target.exists():
                            shutil.copy2(str(json_file), str(target))
                            migrated += 1
                    if migrated > 0:
                        Logger.info(f"Migration: {migrated} Charakter(e) ins persistente Verzeichnis kopiert")
            except Exception as e:
                Logger.warning(f"Charakter-Migration fehlgeschlagen: {e}")

            # Archetypen aus gebündeltem App-Verzeichnis ins persistente Verzeichnis kopieren
            self._copy_archetypen_on_android(old_chars_dir, new_chars_dir)

        except Exception as e:
            Logger.warning(f"Charakter-Migration fehlgeschlagen: {e}")

    def _copy_archetypen_on_android(self, bundled_chars_dir: Path, user_chars_dir: Path):
        """Kopiert mitgelieferte Archetypen ins persistente Benutzer-Verzeichnis auf Android.

        Als Quelle wird unter allen Kandidaten das Verzeichnis mit den
        meisten Archetypen-JSONs gewählt — nicht das erste existierende.
        Das verhindert, dass ein veraltetes oder leeres Verzeichnis das
        echte Bundle verdeckt. Der kanonische p4a-App-Pfad kommt zusätzlich
        aus der Umgebungsvariable ANDROID_ARGUMENT (von p4a/start.c gesetzt).
        """
        try:
            from utils.archetypen_sync import (
                finde_beste_quelle, sync_archetypen, zaehle_archetypen,
            )

            # Hol den Root der App (wo die Ressourcen entpackt werden)
            app_root = get_application_root()

            # Mögliche Quellpfade für Archetypen sammeln
            kandidaten = []
            for env_var in ('ANDROID_ARGUMENT', 'ANDROID_APP_PATH'):
                env_dir = os.environ.get(env_var)
                if env_dir:
                    kandidaten.append(Path(env_dir) / 'chars' / 'Archetypen')
                    kandidaten.append(Path(env_dir) / 'Archetypen')
            kandidaten += [
                bundled_chars_dir / 'Archetypen',  # chars/Archetypen (normal)
                bundled_chars_dir.parent / 'Archetypen',  # /Archetypen (neben chars)
                app_root / 'Archetypen',  # Direkt im App-Root (buildozer)
                app_root / 'chars' / 'Archetypen',  # App-Root/chars/Archetypen
                Path(get_resource_path('chars/Archetypen')),  # via get_resource_path
                Path(get_resource_path('Archetypen')),  # direkt im resources
            ]
            # Duplikate entfernen, Reihenfolge erhalten
            kandidaten = list(dict.fromkeys(kandidaten))

            user_archetypen = Path(user_chars_dir) / 'Archetypen'

            for kandidat in kandidaten:
                Logger.info(f"Archetypen: Kandidat {kandidat}: {zaehle_archetypen(kandidat)} JSON(s)")

            quelle, quell_anzahl = finde_beste_quelle(kandidaten, user_archetypen)

            if not quelle:
                vorhanden = zaehle_archetypen(user_archetypen)
                Logger.warning(
                    f"Archetypen: Kein gebündeltes Verzeichnis mit Archetypen gefunden "
                    f"({len(kandidaten)} Kandidaten geprüft, {vorhanden} bereits im Ziel)"
                )
                # Nutzer sichtbar warnen, wenn offensichtlich Archetypen fehlen
                if vorhanden < 50:
                    self._zeige_archetypen_feedback(
                        f"Gebündelte Archetypen nicht gefunden — nur {vorhanden} verfügbar. "
                        f"Bitte als Fehler melden.",
                        erfolg=False,
                    )
                return

            statistik = sync_archetypen(quelle, user_archetypen)
            gesamt = zaehle_archetypen(user_archetypen)
            Logger.info(
                f"Archetypen: Quelle {quelle} ({quell_anzahl} JSONs) → "
                f"{statistik['kopiert']} kopiert, {statistik['repariert']} Namen repariert, "
                f"{statistik['vorhanden']} unverändert, {statistik['fehler']} Fehler, "
                f"{gesamt} insgesamt im Ziel"
            )

            if statistik['kopiert'] > 0:
                self._zeige_archetypen_feedback(
                    f"{statistik['kopiert']} neue Archetypen installiert ({gesamt} insgesamt)"
                )
        except Exception as e:
            Logger.error(f"Archetypen-Kopie fehlgeschlagen: {e}", exc_info=True)

    def _zeige_archetypen_feedback(self, nachricht: str, erfolg: bool = True):
        """Zeigt das Ergebnis der Archetypen-Synchronisation als Snackbar.

        Verzögert, damit die UI beim App-Start bereits aufgebaut ist.
        """
        def _show(dt):
            try:
                from services.service_container import service_container
                dialog_service = service_container.get_dialog_service()
                if dialog_service:
                    if erfolg:
                        dialog_service.show_success_dialog(nachricht)
                    else:
                        dialog_service.show_warning_dialog(nachricht)
            except Exception as e:
                Logger.warning(f"Archetypen-Feedback konnte nicht angezeigt werden: {e}")

        Clock.schedule_once(_show, 3.0)

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
        """Startet ein automatisches Backup der Benutzerdaten im Hintergrund."""
        try:
            from services.service_container import service_container
            backup_service = service_container.get_backup_service()
            if backup_service:
                backup_service.start_background_backup(delay_seconds=2.0)
        except Exception as e:
            Logger.warning(f"Auto-Backup-Start fehlgeschlagen: {e}")

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

        # Pointbar-Overlay nur im Mobile-Modus erstellen (Android oder force_mobile_layout)
        self.use_pointbar_overlay = is_mobile_layout()
        Logger.info(f"Pointbar-Modus: {'Overlay (Mobile)' if self.use_pointbar_overlay else 'Eingebettet (Desktop)'}")
        
        if self.use_pointbar_overlay:
            self.pointbar_overlay = PointbarOverlay()
            Clock.schedule_once(lambda dt: self.pointbar_overlay.open(), 0.2)
        else:
            self.pointbar_overlay = None

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