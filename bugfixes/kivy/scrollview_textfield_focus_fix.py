"""
Fix: ScrollView steals touch from MDTextField on Android
========================================================

Workaround: Custom ScrollView that detects taps vs scrolls and
forces TextField focus on tap.

How to test:
1. Run this code on Android
2. Tap on any of the TextFields inside the ScrollView
3. The keyboard should appear and stay open
4. Scrolling should still work normally

Fix explanation:
- On touch_down: record touch position and find any MDTextField under it
- On touch_up: check if it was a tap (movement < dp(30)) vs scroll gesture
- If tap: force field.focus = True via Clock.schedule_once
  (twice: immediately + 100ms delay as safety net)
"""

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField

KV = """
MDScreen:

    TextFieldScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            spacing: "16dp"
            padding: "16dp"
            adaptive_height: True

            MDLabel:
                text: "Tap any TextField below."
                adaptive_height: True

            MDTextField:
                mode: "outlined"
                size_hint_y: None
                height: "56dp"
                MDTextFieldHintText:
                    text: "Field 1"

            MDTextField:
                mode: "outlined"
                size_hint_y: None
                height: "56dp"
                MDTextFieldHintText:
                    text: "Field 2"

            MDTextField:
                mode: "outlined"
                size_hint_y: None
                height: "56dp"
                MDTextFieldHintText:
                    text: "Field 3"

            # Filler to make content scrollable
            Widget:
                size_hint_y: None
                height: "800dp"
"""


class TextFieldScrollView(MDScrollView):
    """ScrollView that correctly handles TextField focus on Android.

    Standard MDScrollView uses scroll_timeout to distinguish taps from
    scrolls. This delay causes TextField to briefly gain and immediately
    lose focus on Android touch screens.

    This fix detects taps (touch movement < dp(30)) and forces focus
    on the TextField under the touch point.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._touch_start_pos = None
        self._touch_field = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_start_pos = touch.pos
            self._touch_field = self._find_textfield(touch.pos)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        result = super().on_touch_up(touch)

        if (
            self._touch_start_pos
            and self._touch_field
            and self.collide_point(*touch.pos)
        ):
            dx = abs(touch.pos[0] - self._touch_start_pos[0])
            dy = abs(touch.pos[1] - self._touch_start_pos[1])

            if dx < dp(30) and dy < dp(30):
                # It was a tap, not a scroll — force focus
                field = self._touch_field
                Clock.schedule_once(lambda dt: setattr(field, 'focus', True), 0)
                Clock.schedule_once(lambda dt: setattr(field, 'focus', True), 0.1)

        self._touch_start_pos = None
        self._touch_field = None
        return result

    def _find_textfield(self, pos):
        """Walk widget tree to find MDTextField under touch position."""
        def walk(widget):
            if isinstance(widget, MDTextField) and widget.collide_point(*pos):
                return widget
            for child in reversed(widget.children):
                found = walk(child)
                if found:
                    return found
            return None

        if self.children:
            return walk(self.children[0])
        return None


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()
