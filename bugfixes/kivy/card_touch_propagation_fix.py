"""
Fix: MDCard on_release blocked by interactive children on Android
=================================================================

Workaround: On mobile, use non-interactive display widgets (MDIcon)
instead of MDButton/MDIconButton inside clickable cards.

How to test:
1. Run this code on Android
2. Tap on any card — the card's on_release fires reliably
3. The icon is purely visual and does not capture touches

Fix explanation:
- MDIcon is a non-interactive label widget — touches pass through to parent
- MDButton/MDIconButton are interactive and capture touches before the card
- On mobile: use MDIcon for display, MDButton for actions only
- On desktop: MDButton can be used since mouse clicks are precise
"""

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.utils import platform as kivy_platform
from kivymd.app import MDApp

# Simulate mobile detection
_mobile = kivy_platform == 'android'

KV = """
MDScreen:

    MDScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            spacing: "12dp"
            padding: "16dp"
            adaptive_height: True

            MDLabel:
                text: "Tap on the cards — icons are non-interactive, touch passes through!"
                adaptive_height: True
"""


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel, MDIcon
        from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText

        container = self.root.children[0].children[0]

        for i in range(5):
            card = MDCard(
                style="elevated",
                size_hint_y=None,
                height=dp(72),
                padding=dp(12),
                on_release=lambda x, idx=i: print(f"Card {idx + 1} tapped!"),
            )

            row = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(12),
            )

            if _mobile:
                # FIX: MDIcon is non-interactive — touch passes through to card
                icon = MDIcon(
                    icon="star",
                    size_hint=(None, None),
                    size=(dp(28), dp(28)),
                    pos_hint={"center_y": 0.5},
                )
                row.add_widget(icon)
            else:
                # Desktop: MDButton is fine, mouse clicks are precise
                icon_btn = MDButton(
                    style="tonal",
                    size_hint=(None, None),
                    size=(dp(48), dp(48)),
                )
                icon_btn.add_widget(MDButtonIcon(icon="star"))
                row.add_widget(icon_btn)

            row.add_widget(MDLabel(
                text=f"Card {i + 1} — tap me",
                pos_hint={"center_y": 0.5},
            ))

            card.add_widget(row)
            container.add_widget(card)


Test().run()
