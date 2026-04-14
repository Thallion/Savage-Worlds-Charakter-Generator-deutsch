"""
Fix: Bottom navigation touch delayed/blocked by ScrollView
============================================================

Workaround:
1. Use on_touch_down instead of on_touch_up/on_release for nav buttons
2. Add debounce to prevent double-triggers
3. Use touch.opos (original position) as fallback for collision check
   to tolerate finger drift during tap
4. Increase touch target height to dp(64)

How to test:
1. Run this code on Android
2. Scroll the content rapidly
3. Immediately tap a nav button — it responds instantly
4. No delay, no missed taps

Fix explanation:
- on_touch_down fires immediately, before ScrollView's scroll_timeout
- Debounce prevents the same touch from triggering multiple buttons
- touch.opos fallback handles finger drift (common on mobile)
- Larger touch targets reduce miss rate
"""

import time
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

KV = """
MDScreen:

    MDBoxLayout:
        orientation: "vertical"

        MDScrollView:
            do_scroll_x: False
            size_hint_y: 1

            MDBoxLayout:
                orientation: "vertical"
                spacing: "8dp"
                padding: "16dp"
                adaptive_height: True

                MDLabel:
                    text: "Scroll this area, then tap nav buttons below."
                    adaptive_height: True

                MDLabel:
                    text: "Buttons respond instantly via on_touch_down!"
                    adaptive_height: True

                Widget:
                    size_hint_y: None
                    height: "1200dp"

        # Bottom navigation bar — custom touch handling
        NavBar:
            id: navbar
"""


class NavButton(MDBoxLayout):
    """Navigation button that uses on_touch_down with debounce and drift tolerance."""

    def __init__(self, label_text="", on_tap=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_x = 1
        self.size_hint_y = None
        self.height = dp(64)  # Larger touch target
        self._on_tap = on_tap
        self._last_tap = 0

        self.md_bg_color = (0.2, 0.2, 0.3, 1)
        self.radius = [dp(8)]
        self.add_widget(MDLabel(
            text=label_text,
            halign="center",
            pos_hint={"center_y": 0.5},
        ))

    def on_touch_down(self, touch):
        # Use on_touch_down for instant response (before ScrollView timeout)
        # Check collision with both current pos AND original pos (drift tolerance)
        if self.collide_point(*touch.pos) or self.collide_point(*touch.opos):
            now = time.monotonic()
            if now - self._last_tap < 0.5:
                return True  # Debounce
            self._last_tap = now

            if self._on_tap:
                self._on_tap()
            return True
        return super().on_touch_down(touch)


class NavBar(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(64)
        self.spacing = dp(4)
        self.padding = dp(4)

        for i in range(3):
            idx = i + 1
            self.add_widget(NavButton(
                label_text=f"Tab {idx}",
                on_tap=lambda n=idx: print(f"Tab {n} tapped (instant!)"),
            ))


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()
