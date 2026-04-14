"""
Bug: Checkbox fires multiple times on single tap (Android)
==========================================================

How to reproduce:
1. Run this code on Android
2. Tap a checkbox in the list
3. Watch the console output — the callback fires 2-3 times per tap
4. The checkbox toggles back to its original state (appears unresponsive)

Expected behavior:
- One tap = one toggle, one callback

Actual behavior:
- Android touch screens report multiple touch events within a short window
- on_active fires for each event, causing the checkbox to toggle multiple times
- Result: checkbox appears stuck or unresponsive

Platform: Android (touch screens)
Note: Also affects MDButton on_release in some cases
"""

from kivy.lang import Builder
from kivymd.app import MDApp

KV = """
MDScreen:

    MDScrollView:
        do_scroll_x: False

        MDList:
            id: item_list
"""


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        from kivymd.uix.list import (
            MDListItem,
            MDListItemSupportingText,
            MDListItemTrailingCheckbox,
        )

        for i in range(10):
            item = MDListItem(size_hint_y=None, height="48dp")
            item.add_widget(MDListItemSupportingText(text=f"Item {i + 1}"))

            checkbox = MDListItemTrailingCheckbox()
            # Using on_active — this does NOT reliably work on Android
            checkbox.bind(on_active=lambda cb, value, idx=i: print(
                f"on_active: Item {idx + 1} = {value}"
            ))
            item.add_widget(checkbox)
            self.root.ids.item_list.add_widget(item)


Test().run()
