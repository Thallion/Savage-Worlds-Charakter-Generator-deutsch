"""
Bug: MDCard on_release blocked by interactive children on Android
=================================================================

CLAUDE.md: "Touch Propagation in Cards (Mobile)"
PRs: #135

How to reproduce:
1. Run this code on Android
2. Tap on a card (anywhere except the icon button)
3. The card's on_release may or may not fire
4. Tap directly on the icon button inside the card
5. The icon button captures the touch — card's on_release does NOT fire

Expected behavior:
- Tapping anywhere on the card should trigger the card's action
- OR: The icon should be non-interactive and let the touch pass through

Actual behavior:
- MDButton/MDIconButton inside MDCard capture on_touch_down
- This prevents the touch from reaching the card's on_release handler
- On desktop this is less noticeable because mouse clicks are more precise
- On Android, finger taps have larger hit areas and often land on child widgets

Platform: Android (touch screens with imprecise tap areas)
"""

from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp

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
                text: "Tap on the cards — icon buttons steal the touch on Android."
                adaptive_height: True
"""


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
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

            # BUG: MDButton/MDIconButton captures touch, blocking card's on_release
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
