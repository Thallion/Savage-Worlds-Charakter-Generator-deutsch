"""
Fix: Android TextInput Bubble/Handles bleibt nach Dialog hängen
================================================================

Workaround: Monkey-patch TextInput.__init__ to globally disable
use_bubble and use_handles on Android.

How to test:
1. Run this code on Android
2. Tap a TextField → no bubble/handles appear
3. Open and close dialog
4. No orphaned widgets on screen

Fix explanation:
- Patch TextInput.__init__ to set use_bubble=False and use_handles=False
- Only applied on Android (platform check)
- Copy/paste still works via the Android system keyboard's clipboard button
"""

from kivy.lang import Builder
from kivy.utils import platform as kivy_platform
from kivymd.app import MDApp

# --- Monkey-Patch: Disable bubble/handles on Android ---
if kivy_platform == 'android':
    from kivy.uix.textinput import TextInput as _TextInput
    _orig_init = _TextInput.__init__

    def _patched_init(self, **kwargs):
        kwargs.setdefault('use_bubble', False)
        kwargs.setdefault('use_handles', False)
        _orig_init(self, **kwargs)

    _TextInput.__init__ = _patched_init

KV = """
MDScreen:

    MDBoxLayout:
        orientation: "vertical"
        spacing: "16dp"
        padding: "16dp"

        MDLabel:
            text: "Tap TextFields, open/close dialog — no stuck widgets!"
            adaptive_height: True

        MDTextField:
            mode: "outlined"
            size_hint_y: None
            height: "56dp"
            MDTextFieldHintText:
                text: "No bubble on Android"

        MDTextField:
            mode: "outlined"
            size_hint_y: None
            height: "56dp"
            MDTextFieldHintText:
                text: "No handles on Android"

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
            MDDialogSupportingText(text="No bubble/handles stuck after close!"),
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
