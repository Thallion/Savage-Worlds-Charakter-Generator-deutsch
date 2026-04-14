"""
Fix: MDDialog steals touch from TextField and ScrollView
=========================================================

Workaround: Use ModalView instead of MDDialog for search dialogs.
ModalView has simpler touch handling that doesn't conflict with children.

How to test:
1. Run this code on Android
2. Tap "Open Search"
3. Tap the search field — keyboard stays open
4. Scroll the list — works smoothly
5. Tap outside (scrim area) or X to close

Fix explanation:
- Replace MDDialog with a custom ModalView-based bottom sheet
- ModalView has transparent touch handling — no stealing from children
- Scrim area handles dismiss, but doesn't interfere with content touches
- Slide-up/down animation for native feel
"""

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

KV = """
MDScreen:

    MDButton:
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: app.show_search()

        MDButtonText:
            text: "Open Search"
"""


class SearchBottomSheet(ModalView):
    """Custom ModalView-based search sheet that doesn't steal touches."""

    def __init__(self, title="Search", items=None, on_select=None, **kwargs):
        kwargs.setdefault('size_hint', (1, 1))
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('background', '')
        kwargs.setdefault('auto_dismiss', False)
        super().__init__(**kwargs)

        self._items = items or []
        self._on_select = on_select

        # Scrim (semi-transparent background)
        scrim = Widget(size_hint=(1, 1))
        scrim.bind(on_touch_down=self._on_scrim_touch)
        self.add_widget(scrim)

        # Sheet card
        self._sheet = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(420),
            pos_hint={'center_x': 0.5},
            md_bg_color=(0.15, 0.15, 0.15, 1),
            radius=[dp(16), dp(16), 0, 0],
            padding=[0, dp(8), 0, 0],
        )

        # Header
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            padding=[dp(16), 0, dp(8), 0],
        )
        header.add_widget(MDIconButton(
            icon="close",
            on_release=lambda x: self.dismiss(),
        ))
        header.add_widget(MDLabel(
            text=title,
            font_style="Title",
            role="medium",
            bold=True,
        ))
        self._sheet.add_widget(header)

        # Search field
        search_box = MDBoxLayout(
            size_hint_y=None,
            height=dp(56),
            padding=[dp(16), 0, dp(16), dp(4)],
        )
        self._search = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(48),
        )
        self._search.add_widget(MDTextFieldHintText(text="Search..."))
        self._search.bind(text=self._filter)
        search_box.add_widget(self._search)
        self._sheet.add_widget(search_box)

        # Scrollable list
        scroll = MDScrollView(do_scroll_x=False)
        self._list = MDList(size_hint_y=None)
        self._list.bind(minimum_height=self._list.setter('height'))
        scroll.add_widget(self._list)
        self._sheet.add_widget(scroll)

        self.add_widget(self._sheet)
        self._sheet.y = -self._sheet.height
        self._populate()

    def open(self, *args, **kwargs):
        super().open(*args, **kwargs)
        Clock.schedule_once(self._animate_open, 0.05)

    def _animate_open(self, dt):
        self._sheet.y = -self._sheet.height
        Animation(y=0, duration=0.25, t='out_cubic').start(self._sheet)

    def _on_scrim_touch(self, widget, touch):
        if touch.y > self._sheet.top:
            self.dismiss()
            return True
        return False

    def _populate(self, filter_text=""):
        self._list.clear_widgets()
        search = filter_text.lower()
        for name in self._items:
            if search and search not in name.lower():
                continue
            item = MDListItem(
                on_release=lambda x, n=name: self._select(n),
                size_hint_y=None,
                height=dp(48),
            )
            item.add_widget(MDListItemHeadlineText(text=name))
            self._list.add_widget(item)

    def _filter(self, instance, text):
        self._populate(text)

    def _select(self, name):
        if self._on_select:
            self._on_select(name)
        self.dismiss()


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def show_search(self):
        items = [f"Item {i + 1}" for i in range(20)]
        sheet = SearchBottomSheet(
            title="Search Items",
            items=items,
            on_select=lambda name: print(f"Selected: {name}"),
        )
        sheet.open()


Test().run()
