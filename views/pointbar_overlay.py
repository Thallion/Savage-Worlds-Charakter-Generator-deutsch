# views/pointbar_overlay.py
"""
Pointbar Overlay für zuverlässiges Touch-Handling auf Android.
Ersetzt die eingebettete Pointbar durch ein Overlay, das über dem
Hauptinhalt schwebt und unabhängig von Layout-Änderungen funktioniert.
"""

import time
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.app import App
from kivy.utils import platform

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton

from views.pointbar_view import GenerationPointsBar


class PointbarOverlay(MDBoxLayout):
    """Overlay für die Pointbar (Toolbar + Details)."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)  # Absolute Positionierung
        self.width = dp(400)  # Startbreite, wird in _update_position aktualisiert
        self.height = dp(48)  # Start Höhe (nur Toolbar)
        self.pos_hint = {}  # wird von _update_position aktualisiert
        
        # Referenzen für Positionierung
        self.root = None
        self.tabs_container = None
        self.pointbar_container = None
        self.nav_rail_container = None
        self.menu_toggle_container = None
        self.embedded_pointbar = None  # Referenz auf eingebettete (unsichtbare) Pointbar
        
        # Pointbar-Widget laden (GenerationPointsBar)
        self.pointbar = GenerationPointsBar(size_hint_y=None)
        self.pointbar.disabled = False  # Sicherstellen, dass Pointbar interaktiv ist
        self.add_widget(self.pointbar)
        self.disabled = False  # Overlay selbst auch interaktiv
        
        # Bindungen für Höhenänderungen
        self.pointbar.bind(minimum_height=self._update_height)
        self.pointbar.bind(is_expanded=self._on_expanded_changed)
        
        # Window-Bindung für Größenänderungen (Fallback)
        Window.bind(size=self._on_window_size)
        
        # Initiale Höhe setzen
        Clock.schedule_once(self._update_height, 0.1)
        
        Logger.info("PointbarOverlay initialisiert")
    
    def _update_height(self, *args):
        """Aktualisiert die Höhe des Overlays basierend auf der Pointbar."""
        if self.pointbar:
            new_height = self.pointbar.minimum_height
            Logger.debug(f"PointbarOverlay: Höhe update - pointbar.minimum_height={new_height}, current height={self.height}")
            if new_height != self.height:
                self.height = new_height
                Logger.debug(f"PointbarOverlay: Höhe geändert auf {self.height}")
                # Position aktualisieren, wenn Overlay bereits platziert ist
                if self.parent:
                    self._update_position()
    
    def _on_expanded_changed(self, instance, value):
        """Wird aufgerufen, wenn die Pointbar ein-/ausgeklappt wird."""
        Clock.schedule_once(self._update_height, 0.05)

    def _sync_embedded_expanded(self, instance, value):
        """Synchronisiert is_expanded mit der eingebetteten (unsichtbaren) Pointbar,
        damit pointbar_container.minimum_height dem Overlay folgt und
        der Hauptinhalt korrekt unter das Overlay rutscht."""
        if self.embedded_pointbar:
            self.embedded_pointbar.is_expanded = value
    
    def _on_window_size(self, window, size):
        """Passt die Position bei Fenstergrößenänderung an."""
        self._update_position()
    
    def _update_position(self, *args):
        """Aktualisiert die Position des Overlays relativ zu Tabs, Nav-Rail und Pointbar-Container."""
        if not self.parent:
            return
        
        # Tabs-Höhe ermitteln (Standard 64dp)
        tabs_height = dp(64)
        if self.tabs_container:
            tabs_height = self.tabs_container.height
        
        # Menu-Toggle-Breite ermitteln (0 wenn nicht sichtbar)
        menu_toggle_width = 0
        if self.menu_toggle_container and self.menu_toggle_container.width > 0:
            menu_toggle_width = self.menu_toggle_container.width
        
        # Nav-Rail-Breite ermitteln (0 wenn nicht sichtbar)
        nav_rail_width = 0
        if self.nav_rail_container and self.nav_rail_container.width > 0:
            nav_rail_width = self.nav_rail_container.width
        
        # Root-Dimensionen
        root = self.parent  # MDScreen
        root_height = root.height
        root_width = root.width

        # Android: Statusbar/Notch-Höhe berücksichtigen. Das Overlay hängt
        # direkt am MDScreen (nicht in outer_box), daher greift das
        # outer_box.padding aus main.py nicht.
        android_top = 0
        if platform == 'android':
            app = App.get_running_app()
            android_top = getattr(app, '_android_top_padding', 0)

        # Position: direkt unter den Tabs, über dem restlichen Content
        # Beginnt rechts von Menu-Toggle und Nav Railbar (falls sichtbar)
        self.top = root_height - android_top - tabs_height
        self.x = menu_toggle_width + nav_rail_width  # Nach rechts versetzen um beide Breiten
        self.width = root_width - menu_toggle_width - nav_rail_width  # Breite anpassen
        self.size_hint_x = None  # Absolute Breite verwenden

        # Debug-Logging
        Logger.info(f"PointbarOverlay Position: x={self.x}, width={self.width}, menu_toggle_width={menu_toggle_width}, nav_rail_width={nav_rail_width}, root_width={root_width}, tabs_height={tabs_height}, android_top={android_top}")
    
    def open(self, *args, **kwargs):
        """Fügt das Overlay zum Root-Layout hinzu und bindet an den Charakter-Controller."""
        # Nur hinzufügen, wenn nicht bereits im Parent
        if self.parent is not None:
            return
        
        app = App.get_running_app()
        root = app.root
        if not root:
            Logger.error("PointbarOverlay: Root nicht verfügbar")
            return
        
        # Referenzen auf wichtige Container speichern
        self.root = root
        self.tabs_container = root.ids.get('tabs_container')
        self.pointbar_container = root.ids.get('pointbar_container')
        self.nav_rail_container = root.ids.get('nav_rail_container')
        self.menu_toggle_container = root.ids.get('menu_toggle_container')
        self.embedded_pointbar = root.ids.get('generation_points')

        # Overlay direkt zum Root (MDScreen) hinzufügen - über allen anderen Widgets
        root.add_widget(self)
        Logger.info("PointbarOverlay zu Root (MDScreen) hinzugefügt")

        # is_expanded zwischen Overlay-Pointbar und eingebetteter (unsichtbarer)
        # Pointbar synchronisieren. Die eingebettete Pointbar bestimmt via ihrer
        # minimum_height die Höhe des pointbar_container, wodurch der Hauptinhalt
        # korrekt unter dem Overlay beginnt (kein Layout-Loch).
        if self.embedded_pointbar:
            self.embedded_pointbar.is_expanded = self.pointbar.is_expanded
            self.pointbar.bind(is_expanded=self._sync_embedded_expanded)

        # Positionierung aktualisieren
        self._update_position()
        
        # Bindungen für Größenänderungen
        if self.tabs_container:
            self.tabs_container.bind(height=self._update_position)
        if self.pointbar_container:
            self.pointbar_container.bind(height=self._update_position, pos=self._update_position)
        if self.menu_toggle_container:
            self.menu_toggle_container.bind(width=self._update_position)
        if self.nav_rail_container:
            self.nav_rail_container.bind(width=self._update_position)
        root.bind(size=self._update_position)
        
        # Charakter-Controller holen
        if hasattr(app, 'controller'):
            self.pointbar.controller = app.controller
            self.pointbar.bind_charakter_properties()
            Logger.info("PointbarOverlay geöffnet und an Controller gebunden")
    
    def close(self):
        """Entfernt das Overlay aus dem Root und entfernt Bindungen."""
        if self.parent:
            self.parent.remove_widget(self)

        # Bindungen entfernen
        if self.tabs_container:
            self.tabs_container.unbind(height=self._update_position)
        if self.pointbar_container:
            self.pointbar_container.unbind(height=self._update_position, pos=self._update_position)
        if self.menu_toggle_container:
            self.menu_toggle_container.unbind(width=self._update_position)
        if self.nav_rail_container:
            self.nav_rail_container.unbind(width=self._update_position)
        if self.root:
            self.root.unbind(size=self._update_position)

        if self.pointbar:
            self.pointbar.unbind(is_expanded=self._sync_embedded_expanded)
            self.pointbar.unbind_charakter_properties()

        self.root = None
        self.tabs_container = None
        self.pointbar_container = None
        self.menu_toggle_container = None
        self.nav_rail_container = None
        self.embedded_pointbar = None
        
        Logger.info("PointbarOverlay geschlossen")
    
    def on_touch_down(self, touch):
        """Touch-Events werden an die Pointbar weitergeleitet, falls innerhalb."""
        from kivy.logger import Logger
        
        # Debug: Overlay-Bounding-Box
        Logger.debug(f"PointbarOverlay: Bounding box: pos=({self.x:.1f},{self.y:.1f}), size=({self.width:.1f},{self.height:.1f}), top={self.top:.1f}")
        
        if self.collide_point(*touch.pos):
            Logger.debug(f"PointbarOverlay: Touch bei ({touch.pos[0]:.1f}, {touch.pos[1]:.1f}) - innerhalb, weiterleiten an Pointbar")
            result = super().on_touch_down(touch)
            Logger.debug(f"PointbarOverlay: on_touch_down result={result}")
            return result
        # Touch außerhalb - an darunterliegende Widgets weitergeben
        Logger.debug(f"PointbarOverlay: Touch bei ({touch.pos[0]:.1f}, {touch.pos[1]:.1f}) - außerhalb, weitergeben")
        return False