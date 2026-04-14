"""
Bug: MDDialog expands to full screen on Android
================================================

How to reproduce:
1. Run this code on Android (or a small window to simulate)
2. Tap "Open Dialog"
3. The dialog fills the entire screen instead of being a centered popup

Expected behavior:
- Dialog should appear as a centered popup with reasonable margins

Actual behavior:
- MDDialog defaults to size_hint=(1, 1), filling the entire screen
- On desktop this is less noticeable due to larger screens
- On Android/mobile it makes the dialog look like a new screen, not a popup

Platform: Android (most visible), but affects all platforms
KivyMD version: 2.0.1.dev0 (GitHub master)
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

        # BUG: No size_hint specified — defaults to (1, 1) on Android
        dialog = MDDialog(
            MDDialogHeadlineText(text="Title"),
            MDDialogSupportingText(text="This dialog is full screen on Android."),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Close"),
                    style="text",
                    on_release=lambda x: dialog.dismiss(),
                ),
            ),
        )
        dialog.open()


Test().run()
