# views/app_navigation_mixin.py
"""
Navigations-Subsystem der App: Navigation-Rail, Bottom-Navigation,
Mehr-Popup, Swipe-Gesten, Navigationsmodus und Bildschirm-Orientierung.
Mixin der App-Klasse (main.py) — nur Methoden, kein eigener State.
"""

from kivy.config import Config
from kivy.logger import Logger
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDIconButton
from kivymd.uix.tab import MDTabsPrimary, MDTabsItem, MDTabsItemIcon, MDTabsItemText, MDTabsCarousel
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from views.ui_components import CustomTabsItem, SwipeScreenManager
from kivy.core.window import Window
from kivy.metrics import dp
from services.service_container import service_container
import time


class AppNavigationMixin:

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

                # Lazy-Instanziierung sicherstellen
                screen, screen_name = self._instantiate_screen(tab_index, screen_manager)
                if screen is None or screen_name is None:
                    Logger.warning(f"Bottom-Nav: Screen für Tab '{tab_text}' konnte nicht erzeugt werden")
                    return True

                screen_manager.transition = NoTransition()
                try:
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
            Logger.warning(f"Fehler bei Bottom-Nav-Highlighting: {e}")

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

            # Lazy-Instanziierung sicherstellen
            screen, screen_name = self._instantiate_screen(index, screen_manager)
            if screen is None or screen_name is None:
                Logger.warning(f"Popup-Wechsel: Screen für Tab '{tab_text}' konnte nicht erzeugt werden")
                return

            screen_manager.transition = NoTransition()
            try:
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

                # Lazy-Instanziierung sicherstellen
                screen, screen_name = self._instantiate_screen(item_index, screen_manager)
                if screen is None or screen_name is None:
                    Logger.warning(f"NavigationRail: Screen für Tab '{tab_text}' konnte nicht erzeugt werden")
                    return True

                # Transition ohne Animation bei direktem Tap
                screen_manager.transition = NoTransition()

                try:
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
            pointbar = None
            if hasattr(self, 'pointbar_overlay') and self.pointbar_overlay:
                pointbar = self.pointbar_overlay.pointbar
            else:
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

    def _set_mobile_navigation_style(self, force_rail=False):
        """Setzt den Mobile-Navigation-Stil: force_rail=True erzwingt NavigationRail,
        force_rail=False verwendet orientierungsbasierte Navigation.

        Args:
            force_rail (bool): True = immer NavigationRail, False = orientierungsbasiert
        """
        try:
            root = self.root
            if not root or not self._mobile_modus_active:
                return

            nav_rail_container = root.ids.get('nav_rail_container')
            bottom_bar = root.ids.get('bottom_bar_container')

            if not nav_rail_container:
                return

            if force_rail:
                # Erzwinge NavigationRail (auch im Portrait)
                nav_rail_container.width = dp(80)
                nav_rail_container.opacity = 1
                self._nav_rail_visible = True

                # Bottom-Bar verstecken
                if bottom_bar:
                    bottom_bar.height = 0
                    bottom_bar.opacity = 0

                # Aktiven Tab hervorheben
                if hasattr(self, '_current_tab_index'):
                    self._set_active_rail_item(self._current_tab_index)

                Logger.debug("Mobile-Navigation: NavigationRail erzwungen")
            else:
                # Orientierungsbasierte Navigation (Standard-Verhalten)
                self._update_mobile_orientation()
                Logger.debug("Mobile-Navigation: Orientierungsbasiert")

        except Exception as e:
            Logger.error(f"Fehler beim Setzen der Mobile-Navigation: {str(e)}")

    # Ab dieser kleinsten Displaybreite (dp) gilt ein Gerät als "großes Display"
    # (Tablet/Foldable) — Googles Standard-Schwelle für sw600dp-Layouts.
    GROSSES_DISPLAY_SW_DP = 600

    def ist_grosses_display(self):
        """True auf Tablets/Foldables (smallestScreenWidthDp >= 600).

        Ab Android 16 ignoriert das System auf solchen Geräten sämtliche
        Einschränkungen für Größenänderung und Ausrichtung.
        """
        try:
            from kivy.utils import platform as _platform
            if _platform != 'android':
                return False

            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            config = PythonActivity.mActivity.getResources().getConfiguration()
            return config.smallestScreenWidthDp >= self.GROSSES_DISPLAY_SW_DP
        except Exception as e:
            Logger.warning(f"Displaygröße nicht ermittelbar: {e}")
            return False

    def set_screen_orientation(self, orientation='auto', locked=False):
        """Setzt die Bildschirm-Orientierung auf Android.

        Auf großen Displays (Tablets/Foldables) wird KEINE Sperre angefordert:
        Android 16 ignoriert sie dort ohnehin, und eine halb wirksame Sperre
        führt zu abgeschnittenen Layouts im Multi-Window-/Freeform-Modus.

        Args:
            orientation: 'auto', 'portrait' oder 'landscape'
            locked: True = fixiert, False = flexibel (System-Einstellung beachten)

        Returns:
            True, wenn die gewünschte Sperre gesetzt wurde bzw. keine gewünscht
            war; False, wenn sie wegen eines großen Displays übersprungen wurde.
        """
        try:
            from kivy.utils import platform as _platform
            if _platform != 'android':
                Logger.info(f"Orientierung ignoriert (kein Android): {orientation}, locked={locked}")
                return True

            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            # Android ActivityInfo Orientierungs-Konstanten
            SCREEN_ORIENTATION_FULL_USER = 13        # alle 4 Richtungen, Rotationssperre beachtet
            SCREEN_ORIENTATION_SENSOR_PORTRAIT = 7   # Portrait (beide Richtungen)
            SCREEN_ORIENTATION_SENSOR_LANDSCAPE = 6  # Landscape (beide Richtungen)

            angewendet = True

            if not locked or orientation not in ('portrait', 'landscape'):
                # Flexibel bzw. 'auto': System-Einstellung beachten
                requested = SCREEN_ORIENTATION_FULL_USER
                Logger.info("Orientierung: flexibel (System-Einstellung)")
            elif self.ist_grosses_display():
                requested = SCREEN_ORIENTATION_FULL_USER
                angewendet = False
                Logger.info(
                    f"Orientierung: Sperre '{orientation}' auf großem Display übersprungen "
                    "(Android ignoriert sie dort)"
                )
            elif orientation == 'portrait':
                requested = SCREEN_ORIENTATION_SENSOR_PORTRAIT
                Logger.info("Orientierung: Portrait fixiert")
            else:
                requested = SCREEN_ORIENTATION_SENSOR_LANDSCAPE
                Logger.info("Orientierung: Landscape fixiert")

            activity.setRequestedOrientation(requested)
            return angewendet

        except ImportError:
            Logger.info("jnius nicht verfügbar (kein Android)")
            return True
        except Exception as e:
            Logger.warning(f"Fehler beim Setzen der Bildschirm-Orientierung: {e}")
            return True

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

            # Screen ggf. lazy erzeugen
            screen_instance, _ = self._instantiate_screen(index, screen_manager)
            if not screen_instance:
                Logger.warning(f"Screen '{screen_name}' konnte nicht erzeugt werden (Swipe/Nav)")
                return
            screen_manager.current = screen_name

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
