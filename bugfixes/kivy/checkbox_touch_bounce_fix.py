"""
Fix: Checkbox fires multiple times on single tap (Android)
==========================================================

Workaround: Use on_release instead of on_active, with a 500ms
time-based debounce to filter duplicate touch events.

How to test:
1. Run this code on Android
2. Tap any checkbox in the list
3. Console should show exactly one callback per tap
4. Checkbox should toggle correctly every time

Fix explanation:
- Use on_release instead of on_active (on_active still bounces)
- Add 500ms debounce via time.monotonic()
- Use intermediate variable in loop to avoid closure bug
"""

import time
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
        self._last_checkbox_time = 0
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
            # IMPORTANT: intermediate variable to avoid closure bug in loop
            cb = checkbox
            checkbox.bind(
                on_release=lambda x, cb=cb, idx=i: self._on_checkbox(cb, idx)
            )
            item.add_widget(checkbox)
            self.root.ids.item_list.add_widget(item)

    def _on_checkbox(self, checkbox, index):
        """Handler with 500ms debounce to filter Android touch bounce."""
        now = time.monotonic()
        if now - self._last_checkbox_time < 0.5:
            return  # Bounce — ignore
        self._last_checkbox_time = now

        print(f"on_release (debounced): Item {index + 1} = {checkbox.active}")


Test().run()
