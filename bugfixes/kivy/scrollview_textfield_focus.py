"""
Bug: ScrollView steals touch from MDTextField on Android
========================================================

Kivy Issues: kivy/kivy#4399, kivy/kivy#890, kivy/kivy#7320

How to reproduce:
1. Run this code on Android (or emulate touch with Kivy touch simulation)
2. Tap on any of the TextFields inside the ScrollView
3. The keyboard appears briefly and immediately disappears

Expected behavior:
- Tapping a TextField should focus it and keep the keyboard open

Actual behavior:
- ScrollView uses a scroll_timeout (55-200ms) to distinguish scroll from tap
- During this timeout, touch events are NOT passed to children
- When the timeout expires, ScrollView decides it was a tap and passes the touch
- But by then, the TextField has already lost focus

Root cause:
- ScrollView._do_touch_up() dispatches the touch to children only after
  scroll_timeout, causing a race condition with TextField.focus

Platform: Android (touch screens with scroll_timeout > 0)
"""

from kivy.lang import Builder
from kivymd.app import MDApp

KV = """
MDScreen:

    MDScrollView:
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


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()
