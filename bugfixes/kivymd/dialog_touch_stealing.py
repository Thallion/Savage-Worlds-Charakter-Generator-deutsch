"""
Bug: MDDialog steals touch from TextField and ScrollView
=========================================================

PRs: #109, #116, #120, #121

How to reproduce:
1. Run this code on Android
2. Tap "Open Search Dialog"
3. Try to tap the search TextField inside the dialog
4. The keyboard appears briefly and immediately disappears
5. Try to scroll the list — very difficult/impossible

Expected behavior:
- TextField inside dialog should focus reliably
- List inside dialog should scroll smoothly

Actual behavior:
- MDDialog's internal touch handling conflicts with TextField focus
- MDDialog captures touches meant for child ScrollView
- The combination of MDDialog + TextField + ScrollView is unreliable on Android
- This is a combination of the ScrollView steal bug AND dialog touch handling

Root cause:
- MDDialog has its own touch handling for dismiss-on-outside-tap
- This conflicts with ScrollView's scroll_timeout touch handling
- Together they create a "touch stealing" chain that breaks child widgets

Platform: Android (touch screens), partially visible on desktop
KivyMD version: 2.0.1.dev0 (GitHub master)
"""

from kivy.lang import Builder
from kivymd.app import MDApp

KV = """
MDScreen:

    MDButton:
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: app.show_search_dialog()

        MDButtonText:
            text: "Open Search Dialog"
"""


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def show_search_dialog(self):
        from kivy.metrics import dp
        from kivymd.uix.dialog import (
            MDDialog,
            MDDialogHeadlineText,
            MDDialogContentContainer,
            MDDialogButtonContainer,
        )
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
        from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
        from kivymd.uix.scrollview import MDScrollView

        # Build search content
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(400),
            padding=dp(16),
        )

        # Search field
        search = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(48),
        )
        search.add_widget(MDTextFieldHintText(text="Search..."))
        content.add_widget(search)

        # Scrollable list
        scroll = MDScrollView(do_scroll_x=False)
        item_list = MDList(size_hint_y=None)
        item_list.bind(minimum_height=item_list.setter("height"))

        for i in range(20):
            item = MDListItem(size_hint_y=None, height=dp(48))
            item.add_widget(MDListItemHeadlineText(text=f"Item {i + 1}"))
            item_list.add_widget(item)

        scroll.add_widget(item_list)
        content.add_widget(scroll)

        dialog = MDDialog(
            MDDialogHeadlineText(text="Search"),
            MDDialogContentContainer(content),
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
