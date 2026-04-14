"""
Bug: Bottom navigation touch delayed/blocked by ScrollView
============================================================

PR: Thallion/Savage-Worlds-Charakter-Generator-deutsch#150, #152

How to reproduce:
1. Run this code on Android
2. Scroll the content area up and down
3. Immediately tap a bottom navigation button
4. The button often doesn't register the first tap
5. Sometimes requires 2-3 taps or waiting a moment after scrolling

Expected behavior:
- Bottom navigation should respond instantly to taps, regardless of scrolling

Actual behavior:
- When using on_touch_up for bottom nav buttons, the ScrollView's
  scroll_timeout interferes with touch event delivery
- After scrolling, touches near the bottom are still being processed
  by the ScrollView's momentum/deceleration logic
- The bottom navigation button's on_touch_up fires too late or not at all

Root cause:
- ScrollView consumes on_touch_down during scroll_timeout window
- Bottom navigation using on_touch_up receives delayed events
- Finger drift during tap (common on mobile) moves the touch out of
  the button's collision area by the time on_touch_up fires

Platform: Android (touch screens)
"""

from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp

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
                    text: "Scroll this area, then try tapping nav buttons below."
                    adaptive_height: True

                MDLabel:
                    text: "The buttons often don't respond after scrolling."
                    adaptive_height: True

                Widget:
                    size_hint_y: None
                    height: "1200dp"

        # Bottom navigation bar
        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            md_bg_color: app.theme_cls.surfaceContainerColor
            spacing: "4dp"
            padding: "4dp"

            MDButton:
                style: "text"
                size_hint_x: 1
                # BUG: on_release (= on_touch_up) is delayed after scrolling
                on_release: print("Tab 1 tapped")

                MDButtonText:
                    text: "Tab 1"

            MDButton:
                style: "text"
                size_hint_x: 1
                on_release: print("Tab 2 tapped")

                MDButtonText:
                    text: "Tab 2"

            MDButton:
                style: "text"
                size_hint_x: 1
                on_release: print("Tab 3 tapped")

                MDButtonText:
                    text: "Tab 3"
"""


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()
