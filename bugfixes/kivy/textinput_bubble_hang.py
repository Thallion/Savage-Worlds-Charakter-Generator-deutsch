"""
Bug: Android TextInput Bubble/Handles bleibt nach Dialog hängen
================================================================

PR: Thallion/Savage-Worlds-Charakter-Generator-deutsch#142

How to reproduce:
1. Run this code on Android
2. Tap a TextField to focus it
3. The Kivy copy/paste bubble and selection handles appear
4. Tap "Open Dialog" — the dialog opens
5. Close the dialog
6. The bubble/handles from step 3 are still visible and stuck on screen
7. They cannot be dismissed and overlap other UI elements

Expected behavior:
- Bubble/handles should disappear when the TextField loses focus
- They should not persist across dialog open/close

Actual behavior:
- Kivy's TextInput.use_bubble and use_handles create floating widgets
- These widgets are not properly cleaned up when focus changes on Android
- After dialog dismiss, the bubble/handles remain as orphaned widgets

Platform: Android only (desktop doesn't show this behavior)
"""

from kivy.lang import Builder
from kivymd.app import MDApp

KV = """
MDScreen:

    MDBoxLayout:
        orientation: "vertical"
        spacing: "16dp"
        padding: "16dp"

        MDLabel:
            text: "1. Tap a TextField\\n2. Open Dialog\\n3. Close Dialog\\n4. Bubble/handles are stuck"
            adaptive_height: True

        MDTextField:
            mode: "outlined"
            size_hint_y: None
            height: "56dp"
            MDTextFieldHintText:
                text: "Tap here first"

        MDTextField:
            mode: "outlined"
            size_hint_y: None
            height: "56dp"
            MDTextFieldHintText:
                text: "Or here"

        MDButton:
            pos_hint: {"center_x": .5}
            on_release: app.show_dialog()
            MDButtonText:
                text: "Open Dialog"

        Widget:
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

        dialog = MDDialog(
            MDDialogHeadlineText(text="Test Dialog"),
            MDDialogSupportingText(text="Close this and check for stuck bubble/handles."),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Close"),
                    style="text",
                    on_release=lambda x: dialog.dismiss(),
                ),
            ),
            size_hint=(0.85, None),
        )
        dialog.open()


Test().run()
