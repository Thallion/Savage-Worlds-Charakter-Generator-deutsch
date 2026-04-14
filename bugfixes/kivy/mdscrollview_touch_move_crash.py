"""
Bug: MDScrollView.on_touch_move crasht mit TypeError
=====================================================

KivyMD Issue: MDScrollView.convert_overscroll() auf None

How to reproduce:
1. Run this code on Android
2. Scroll quickly in the ScrollView, especially with multi-finger gestures
3. Try to scroll while the view is still decelerating
4. The app crashes with: TypeError: 'NoneType' object is not subscriptable

Expected behavior:
- Scrolling should work smoothly without crashes

Actual behavior:
- MDScrollView.on_touch_move calls effect_x/effect_y.convert_overscroll(touch)
- convert_overscroll calls get_component() which accesses pos[-1] on last_touch_pos
- last_touch_pos can be None when touch events arrive out of order
- KivyMD only catches AttributeError, not TypeError → crash

Root cause:
- MDScrollView.convert_overscroll() accesses self.last_touch_pos[-1]
- last_touch_pos is None when no previous touch was recorded
- The except clause only handles AttributeError, missing TypeError

Platform: Android (most common), but can occur on any platform with rapid touch
KivyMD version: 2.0.1.dev0 (GitHub master)
"""

from kivy.lang import Builder
from kivymd.app import MDApp

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
                text: "Scroll quickly with multiple fingers."
                adaptive_height: True

            MDLabel:
                text: "Try scrolling while view is decelerating."
                adaptive_height: True

            # Many items to make it scrollable
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

            # Filler
            Widget:
                size_hint_y: None
                height: "600dp"
"""


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()
