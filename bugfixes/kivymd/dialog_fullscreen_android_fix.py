"""
Fix: MDDialog expands to full screen on Android
================================================

Workaround: Always set size_hint=(0.85, None) on MDDialog.

How to test:
1. Run this code on Android (or a small window)
2. Tap "Open Dialog"
3. The dialog appears as a centered popup with margins — not fullscreen

Fix explanation:
- MDDialog defaults to size_hint=(1, 1) which fills the entire screen
- Setting size_hint=(0.85, None) constrains width to 85% and auto-heights
- This makes the dialog look like a proper popup on all screen sizes
- Use 0.85 or similar values (0.8, 0.9) — never leave it at default (1, 1)
"""

from kivy.lang import Builder
from kivymd.app import MDApp

KV = """
MDScreen:

    MDButton:
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: app.show_dialog()

        MDButtonText:
            text: "Open Dialog"
"""


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def show_dialog(self):
        from kivymd.uix.dialog import (
            MDDialog,
            MDDialogHeadlineText,
            MDDialogSupportingText,
            MDDialogButtonContainer,
        )
        from kivymd.uix.button import MDButton, MDButtonText

        # FIX: Always specify size_hint=(0.85, None)
        dialog = MDDialog(
            MDDialogHeadlineText(text="Title"),
            MDDialogSupportingText(
                text="This dialog is correctly sized — not fullscreen!"
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Close"),
                    style="text",
                    on_release=lambda x: dialog.dismiss(),
                ),
            ),
            size_hint=(0.85, None),  # <-- THE FIX
        )
        dialog.open()


Test().run()
