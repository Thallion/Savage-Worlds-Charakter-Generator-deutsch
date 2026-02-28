# views/ui_components.py
"""
UI-Komponenten und Tab-Klassen extrahiert aus main.py
"""

from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.metrics import dp
from kivy.logger import Logger


class SwipeScreenManager(ScreenManager):
    """
    ScreenManager mit Swipe-Gestenerkennung für Mobile-Modus.

    Erkennt horizontale Wischgesten und ruft einen Callback auf,
    um zum nächsten/vorherigen Tab zu wechseln.
    """
    swipe_enabled = BooleanProperty(False)
    min_swipe_distance = NumericProperty(dp(80))
    max_vertical_drift = NumericProperty(dp(60))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._touch_start_x = None
        self._touch_start_y = None
        self._swipe_callback = None  # Callback(direction) - 'left' oder 'right'

    def on_touch_down(self, touch):
        if self.swipe_enabled and self.collide_point(*touch.pos):
            self._touch_start_x = touch.x
            self._touch_start_y = touch.y
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.swipe_enabled and self._touch_start_x is not None:
            dx = touch.x - self._touch_start_x
            dy = abs(touch.y - self._touch_start_y)

            # Horizontaler Swipe: genug horizontal, wenig vertikal
            if abs(dx) > self.min_swipe_distance and dy < self.max_vertical_drift:
                if self._swipe_callback:
                    direction = 'right' if dx > 0 else 'left'
                    self._swipe_callback(direction)

            self._touch_start_x = None
            self._touch_start_y = None

        return super().on_touch_up(touch)


from kivymd.uix.tab import MDTabsItem, MDTabsItemText


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