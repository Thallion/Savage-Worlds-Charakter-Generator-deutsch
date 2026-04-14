"""
Fix: MDScrollView.on_touch_move crasht mit TypeError
=====================================================

Workaround: Monkey-patch MDScrollView.on_touch_move to catch both
AttributeError AND TypeError when convert_overscroll accesses None.

How to test:
1. Run this code on Android
2. Scroll quickly with multiple fingers
3. Scroll while the view is decelerating
4. No crash — scrolling works smoothly

Fix explanation:
- Replace MDScrollView.on_touch_move with a version that wraps
  convert_overscroll() in a try/except catching (AttributeError, TypeError)
- Falls back to the base ScrollView.on_touch_move to preserve scrolling
"""

from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.scrollview import MDScrollView

# --- Monkey-Patch: catch TypeError in addition to AttributeError ---
_orig_on_touch_move = MDScrollView.on_touch_move


def _patched_on_touch_move(self, touch):
    try:
        self.effect_x.convert_overscroll(touch)
        self.effect_y.convert_overscroll(touch)
    except (AttributeError, TypeError):
        pass
    # Call base ScrollView.on_touch_move, bypassing the buggy MDScrollView version
    ScrollView.on_touch_move(self, touch)


MDScrollView.on_touch_move = _patched_on_touch_move

KV = """
MDScreen:

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            spacing: "8dp"
            padding: "16dp"
            adaptive_height: True

            MDLabel:
                text: "Scroll quickly with multiple fingers — no crash!"
                adaptive_height: True

            MDLabel:
                text: "The monkey-patch catches TypeError from None pos."
                adaptive_height: True

            MDLabel:
                text: "Item 1\\nLorem ipsum dolor sit amet"
                adaptive_height: True

            MDLabel:
                text: "Item 2\\nConsectetur adipiscing elit"
                adaptive_height: True

            MDLabel:
                text: "Item 3\\nSed do eiusmod tempor"
                adaptive_height: True

            MDLabel:
                text: "Item 4\\nIncididunt ut labore"
                adaptive_height: True

            MDLabel:
                text: "Item 5\\nEt dolore magna aliqua"
                adaptive_height: True

            MDLabel:
                text: "Item 6\\nUt enim ad minim veniam"
                adaptive_height: True

            MDLabel:
                text: "Item 7\\nQuis nostrud exercitation"
                adaptive_height: True

            MDLabel:
                text: "Item 8\\nUllamco laboris nisi"
                adaptive_height: True

            MDLabel:
                text: "Item 9\\nUt aliquip ex ea commodo"
                adaptive_height: True

            MDLabel:
                text: "Item 10\\nConsequat duis aute irure"
                adaptive_height: True

            Widget:
                size_hint_y: None
                height: "600dp"
"""


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()
