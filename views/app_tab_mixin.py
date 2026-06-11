# views/app_tab_mixin.py
"""
Tab-/Screen-Aufbau der App: Tabs erstellen, Screens lazy instanziieren,
Tab-Wechsel und Aktualisierung des aktiven Screens.
Mixin der App-Klasse (main.py) — nur Methoden, kein eigener State.
"""

from models.charakter import Charakter
from kivy.clock import Clock
from kivy.logger import Logger
from kivymd.uix.tab import MDTabsPrimary, MDTabsItem, MDTabsItemIcon, MDTabsItemText, MDTabsCarousel
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp
import time


class AppTabAufbauMixin:

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

            # Tabs und Screens aufbauen — Screens nur für Tab 0 sofort,
            # alle anderen werden lazy bei erstem Tab-Wechsel erzeugt (spart Startup-Zeit, v.a. Android).
            for i, (icon_str, tab_text, ScreenClass) in enumerate(self.tab_definitions):
                Logger.info(f"Erstelle Tab {i+1}/{len(self.tab_definitions)}: '{tab_text}' mit Icon '{icon_str}'")

                # Tab-Item für alle Tabs sofort erstellen (Tab-Bar bleibt vollständig sichtbar)
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

                # Screen-Instanzierung: Tab 0 + Historie sofort (Historie braucht
                # früh registrierte Event-Listener für Änderungs-Logging), Rest on-demand
                if i == 0 or tab_text == "Historie":
                    screen_instance, screen_name = self._instantiate_screen(i, screen_manager)
                    if screen_instance and screen_name:
                        screen_manager.current = screen_name
                    Logger.info(f"✓ Tab '{tab_text}' + Screen (eager) erstellt")
                else:
                    Logger.info(f"✓ Tab '{tab_text}' erstellt (Screen lazy)")

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

    def _screen_name_for_tab(self, tab_index):
        """Erzeugt den kanonischen Screen-Namen für einen Tab-Index."""
        if tab_index < 0 or tab_index >= len(self.tab_definitions):
            return None
        tab_text = self.tab_definitions[tab_index][1]
        clean_name = tab_text.lower().replace(' ', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
        return f"screen_{tab_index}_{clean_name}"

    def _instantiate_screen(self, tab_index, screen_manager):
        """
        Instanziiert den Screen für den gegebenen Tab-Index, falls noch nicht geschehen.

        Lazy-Loading: Screens werden erst erzeugt, wenn sie tatsächlich gebraucht werden
        (Tab-Wechsel, Swipe, programmatische Navigation) — spart Startup-Zeit v.a. auf Android.

        Returns:
            (screen_instance, screen_name) oder (None, None) bei Fehler/ungültigem Index.
        """
        try:
            if tab_index < 0 or tab_index >= len(self.tab_definitions):
                Logger.warning(f"Lazy-Screen: Ungültiger tab_index {tab_index}")
                return None, None

            if screen_manager is None:
                Logger.error("Lazy-Screen: screen_manager ist None")
                return None, None

            _, tab_text, ScreenClass = self.tab_definitions[tab_index]
            screen_name = self._screen_name_for_tab(tab_index)

            # Bereits registriert?
            if tab_text in self.screens:
                return self.screens[tab_text], screen_name

            # Sicherheitsnetz: vielleicht im ScreenManager ohne dict-Eintrag?
            if screen_name and screen_name in getattr(screen_manager, 'screen_names', []):
                try:
                    existing = screen_manager.get_screen(screen_name)
                    self.screens[tab_text] = existing
                    if not hasattr(self, 'screen_instances'):
                        self.screen_instances = []
                    if existing not in self.screen_instances:
                        self.screen_instances.append(existing)
                    return existing, screen_name
                except Exception:
                    pass  # neu erzeugen

            # Neu erzeugen
            t0 = time.monotonic()
            screen_instance = ScreenClass()
            screen_instance.name = screen_name
            screen_manager.add_widget(screen_instance)

            self.screens[tab_text] = screen_instance
            if not hasattr(self, 'screen_instances'):
                self.screen_instances = []
            self.screen_instances.append(screen_instance)
            self._register_widget_for_compatibility(screen_instance, tab_text)

            dt_ms = (time.monotonic() - t0) * 1000
            Logger.info(f"Lazy-Screen: '{tab_text}' (Index {tab_index}) in {dt_ms:.1f} ms instanziiert")
            return screen_instance, screen_name

        except Exception as e:
            safe_name = (
                self.tab_definitions[tab_index][1]
                if 0 <= tab_index < len(self.tab_definitions) else str(tab_index)
            )
            Logger.error(f"Lazy-Screen: Fehler bei '{safe_name}': {e}", exc_info=True)
            return None, None

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

                    # Screen ggf. lazy erzeugen und dann wechseln
                    screen_instance, _ = self._instantiate_screen(tab_index, screen_manager)
                    if screen_instance:
                        screen_manager.current = screen_name
                    else:
                        Logger.error(f"Tab-Wechsel zu '{screen_name}' fehlgeschlagen: Screen konnte nicht erzeugt werden")
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
