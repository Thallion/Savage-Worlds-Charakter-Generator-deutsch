"""
Kivy/KivyMD Bugfixes Test App
==============================

Eine übergeordnete Test-App, die alle dokumentierten Kivy/KivyMD Bugs
demonstriert. Jeder Bug kann zwischen "Bug" und "Fix" umgeschaltet werden.

Für Android-Tests mit buildozer:
    cd bugfixes
    buildozer -v android debug
    buildozer android deploy run logcat

Desktop:
    cd bugfixes
    python main.py

Struktur:
- 3 Tabs: Kivy Bugs | KivyMD Bugs | Info
- Jeder Bug ist eine Karte mit Titel, Beschreibung und 2 Buttons (Bug/Fix)
- Klick auf Button startet die entsprechende Demo in einem neuen Screen
- Back-Button kehrt zur Übersicht zurück
"""

import time
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.utils import platform as kivy_platform

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView


# ============================================================================
# Bug-Definitionen
# ============================================================================

BUGS = [
    {
        "id": "scrollview_textfield",
        "category": "kivy",
        "title": "ScrollView Steals TextField Focus",
        "issue": "kivy/kivy#4399, #890, #7320",
        "description": (
            "Kivy's ScrollView uses a scroll_timeout that steals touch events "
            "from MDTextField children. On Android, the keyboard appears briefly "
            "and immediately disappears when tapping a TextField inside a ScrollView."
        ),
        "bug_module": "kivy.scrollview_textfield_focus",
        "fix_module": "kivy.scrollview_textfield_focus_fix",
    },
    {
        "id": "checkbox_bounce",
        "category": "kivy",
        "title": "Checkbox Touch Bounce (Android)",
        "issue": "Android touch events fire 2-3 times",
        "description": (
            "On Android, MDListItemTrailingCheckbox fires on_active multiple times "
            "per tap, causing the checkbox to toggle back to its original state. "
            "Fix: Use on_release with 500ms time-based debounce."
        ),
        "bug_module": "kivy.checkbox_touch_bounce",
        "fix_module": "kivy.checkbox_touch_bounce_fix",
    },
    {
        "id": "mdscrollview_crash",
        "category": "kivy",
        "title": "MDScrollView on_touch_move TypeError",
        "issue": "MDScrollView.convert_overscroll() on None",
        "description": (
            "MDScrollView.on_touch_move crashes with TypeError when last_touch_pos "
            "is None. KivyMD only catches AttributeError. Fix: Monkey-patch to "
            "catch both exception types."
        ),
        "bug_module": "kivy.mdscrollview_touch_move_crash",
        "fix_module": "kivy.mdscrollview_touch_move_crash_fix",
    },
    {
        "id": "textinput_bubble",
        "category": "kivy",
        "title": "TextInput Bubble/Handles Hang (Android)",
        "issue": "PR #142",
        "description": (
            "On Android, the copy/paste bubble and selection handles remain "
            "visible after dismissing dialogs. Fix: Monkey-patch TextInput.__init__ "
            "to disable use_bubble and use_handles on Android."
        ),
        "bug_module": "kivy.textinput_bubble_hang",
        "fix_module": "kivy.textinput_bubble_hang_fix",
    },
    {
        "id": "card_touch",
        "category": "kivy",
        "title": "Card on_release Blocked by Buttons",
        "issue": "Touch propagation mobile",
        "description": (
            "Interactive children (MDButton, MDIconButton) inside MDCard capture "
            "touches on Android, blocking the card's on_release. "
            "Fix: Use MDIcon (non-interactive) for display on mobile."
        ),
        "bug_module": "kivy.card_touch_propagation",
        "fix_module": "kivy.card_touch_propagation_fix",
    },
    {
        "id": "nav_conflict",
        "category": "kivy",
        "title": "Bottom-Nav Delayed After Scroll",
        "issue": "PR #150, #152",
        "description": (
            "Bottom navigation buttons don't respond after scrolling because "
            "on_touch_up is delayed by ScrollView's scroll_timeout. "
            "Fix: Use on_touch_down with debounce and drift tolerance."
        ),
        "bug_module": "kivy.nav_touch_scrollview_conflict",
        "fix_module": "kivy.nav_touch_scrollview_conflict_fix",
    },
    {
        "id": "dialog_fullscreen",
        "category": "kivymd",
        "title": "MDDialog Fullscreen on Android",
        "issue": "KivyMD 2.0.1.dev0",
        "description": (
            "MDDialog defaults to size_hint=(1, 1), filling the entire screen on "
            "Android instead of appearing as a centered popup. "
            "Fix: Always set size_hint=(0.85, None)."
        ),
        "bug_module": "kivymd.dialog_fullscreen_android",
        "fix_module": "kivymd.dialog_fullscreen_android_fix",
    },
    {
        "id": "dialog_touch_stealing",
        "category": "kivymd",
        "title": "MDDialog Steals Touch (Search Dialogs)",
        "issue": "PRs #109, #116, #120, #121",
        "description": (
            "MDDialog's touch handling conflicts with nested TextField/ScrollView, "
            "breaking search dialogs on Android. "
            "Fix: Use ModalView-based SearchBottomSheet instead."
        ),
        "bug_module": "kivymd.dialog_touch_stealing",
        "fix_module": "kivymd.dialog_touch_stealing_fix",
    },
]


# ============================================================================
# Demo Runner — startet einzelne Bug-Demos im gleichen Prozess
# ============================================================================

def run_demo_module(module_path):
    """
    Führt den Code einer Bug-Datei in einem isolierten Namespace aus.
    Entfernt den Test().run() Aufruf, damit die App nicht neu startet.
    Stattdessen wird das Root-Widget zurückgegeben.
    """
    import importlib
    import os
    import sys

    # Pfad: bugfixes/kivy/xxx.py oder bugfixes/kivymd/xxx.py
    parts = module_path.split(".")
    file_path = os.path.join(os.path.dirname(__file__), *parts) + ".py"

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Entferne den Test().run() Aufruf — wir extrahieren nur das KV/die Klasse
    code = code.replace("Test().run()", "pass")

    # Führe den Code in einem isolierten Namespace aus
    namespace = {"__name__": "__demo__", "__file__": file_path}
    try:
        exec(code, namespace)
    except Exception as e:
        from kivy.logger import Logger
        Logger.error(f"Demo load error: {e}")
        return None

    # Extrahiere das Root-Widget aus der Test-Klasse
    test_cls = namespace.get("Test")
    if test_cls is None:
        return None

    # Instantiate ohne run() — rufe nur build() auf
    try:
        instance = test_cls.__new__(test_cls)
        # Vorsichtiges Init: build() braucht nicht immer eine volle MDApp
        root = test_cls.build(instance)
        # Falls on_start definiert ist, ausführen
        on_start = getattr(instance, "on_start", None)
        if callable(on_start):
            # Root temporär als self.root setzen für on_start
            instance.root = root
            try:
                on_start()
            except Exception:
                pass
        return root
    except Exception as e:
        from kivy.logger import Logger
        Logger.error(f"Demo build error: {e}")
        return None


# ============================================================================
# UI
# ============================================================================

KV = """
#:import dp kivy.metrics.dp

ScreenManager:
    id: sm

    Screen:
        name: "overview"

        MDBoxLayout:
            orientation: "vertical"

            MDBoxLayout:
                size_hint_y: None
                height: "56dp"
                md_bg_color: app.theme_cls.primaryContainerColor
                padding: "12dp"
                spacing: "8dp"

                MDLabel:
                    text: "Kivy / KivyMD Bugfixes Test App"
                    font_style: "Title"
                    role: "medium"
                    bold: True
                    pos_hint: {"center_y": 0.5}

            MDBoxLayout:
                id: tab_bar
                orientation: "horizontal"
                size_hint_y: None
                height: "48dp"
                md_bg_color: app.theme_cls.surfaceContainerColor
                spacing: "4dp"
                padding: "4dp"

            MDScrollView:
                id: content_scroll
                do_scroll_x: False

                MDBoxLayout:
                    id: content_box
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: "12dp"
                    padding: "16dp"

    Screen:
        name: "demo"

        MDBoxLayout:
            orientation: "vertical"

            MDBoxLayout:
                size_hint_y: None
                height: "56dp"
                md_bg_color: app.theme_cls.primaryContainerColor
                padding: "8dp"
                spacing: "8dp"

                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": 0.5}
                    on_release: app.back_to_overview()

                MDLabel:
                    id: demo_title
                    text: ""
                    font_style: "Title"
                    role: "small"
                    bold: True
                    pos_hint: {"center_y": 0.5}

            MDBoxLayout:
                id: demo_container
                orientation: "vertical"
"""


class BugCard(MDCard):
    """Karte für einen einzelnen Bug mit Bug/Fix Buttons."""

    def __init__(self, bug, on_run, **kwargs):
        kwargs.setdefault("style", "elevated")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("padding", dp(16))
        kwargs.setdefault("radius", [dp(12)])
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self._on_run = on_run
        self._bug = bug

        # Title
        self.add_widget(MDLabel(
            text=bug["title"],
            font_style="Title",
            role="small",
            bold=True,
            size_hint_y=None,
            height=dp(28),
        ))

        # Issue reference
        self.add_widget(MDLabel(
            text=f"Ref: {bug['issue']}",
            font_style="Label",
            role="small",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20),
        ))

        # Description
        desc = MDLabel(
            text=bug["description"],
            font_style="Body",
            role="medium",
            size_hint_y=None,
        )
        desc.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(8)))
        self.add_widget(desc)

        # Buttons
        btn_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8),
            padding=[0, dp(8), 0, 0],
        )

        bug_btn = MDButton(
            style="outlined",
            on_release=lambda x: self._run("bug"),
        )
        bug_btn.add_widget(MDButtonText(text="Show Bug"))
        btn_row.add_widget(bug_btn)

        fix_btn = MDButton(
            style="filled",
            on_release=lambda x: self._run("fix"),
        )
        fix_btn.add_widget(MDButtonText(text="Show Fix"))
        btn_row.add_widget(fix_btn)

        self.add_widget(btn_row)

        # Fixed height calculation
        self.bind(minimum_height=self.setter("height"))

    def _run(self, variant):
        if self._on_run:
            self._on_run(self._bug, variant)


class TabButton(MDButton):
    """Tab-Button für die Kategorie-Navigation mit Debounce."""

    def __init__(self, label, on_tap, **kwargs):
        kwargs.setdefault("style", "text")
        kwargs.setdefault("size_hint_x", 1)
        super().__init__(**kwargs)
        self.add_widget(MDButtonText(text=label))
        self._on_tap = on_tap
        self._last_tap = 0
        self.bind(on_release=self._handle_release)

    def _handle_release(self, *args):
        # 500ms Debounce für Android Touch-Bounce
        now = time.monotonic()
        if now - self._last_tap < 0.5:
            return
        self._last_tap = now
        if self._on_tap:
            self._on_tap()


class BugfixTestApp(MDApp):

    current_category = "kivy"

    def build(self):
        self.title = "Kivy Bugfixes Test"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Deeppurple"
        return Builder.load_string(KV)

    def on_start(self):
        self._build_tabs()
        self._show_category("kivy")

    def _build_tabs(self):
        tab_bar = self.root.get_screen("overview").ids.tab_bar
        tab_bar.clear_widgets()

        tab_bar.add_widget(TabButton(
            "Kivy Bugs",
            on_tap=lambda: self._show_category("kivy"),
        ))
        tab_bar.add_widget(TabButton(
            "KivyMD Bugs",
            on_tap=lambda: self._show_category("kivymd"),
        ))
        tab_bar.add_widget(TabButton(
            "Info",
            on_tap=lambda: self._show_category("info"),
        ))

    def _show_category(self, category):
        self.current_category = category
        content_box = self.root.get_screen("overview").ids.content_box
        content_box.clear_widgets()

        if category == "info":
            self._build_info(content_box)
            return

        # Filter bugs by category
        filtered = [b for b in BUGS if b["category"] == category]
        for bug in filtered:
            card = BugCard(bug, on_run=self._run_demo)
            content_box.add_widget(card)

    def _build_info(self, container):
        """Info-Tab mit Beschreibung der App und Hinweisen."""
        info_text = (
            "This app demonstrates documented Kivy and KivyMD bugs encountered "
            "in the Savage Worlds Character Generator.\n\n"
            "Each bug card has two buttons:\n"
            "  - Show Bug: demonstrates the broken behavior\n"
            "  - Show Fix: demonstrates the workaround\n\n"
            "Sources in bugfixes/kivy/ and bugfixes/kivymd/ are standalone "
            "minimal code examples that can be copy-pasted into a Kivy issue "
            "report.\n\n"
            "For Android testing, build with:\n"
            "  cd bugfixes\n"
            "  buildozer -v android debug\n"
            "  buildozer android deploy run logcat\n\n"
            "Platform: " + kivy_platform + "\n"
            "Window size: " + f"{Window.size[0]}x{Window.size[1]}"
        )

        card = MDCard(
            style="elevated",
            orientation="vertical",
            size_hint_y=None,
            padding=dp(16),
            radius=[dp(12)],
        )
        label = MDLabel(
            text=info_text,
            font_style="Body",
            role="medium",
            size_hint_y=None,
        )
        label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(16)))
        card.add_widget(label)
        card.bind(minimum_height=card.setter("height"))
        container.add_widget(card)

    def _run_demo(self, bug, variant):
        """Startet die Bug- oder Fix-Demo in einem eigenen Screen."""
        module_path = bug["bug_module"] if variant == "bug" else bug["fix_module"]

        demo_screen = self.root.get_screen("demo")
        demo_screen.ids.demo_title.text = f"{bug['title']} ({variant.upper()})"

        container = demo_screen.ids.demo_container
        container.clear_widgets()

        root_widget = run_demo_module(module_path)
        if root_widget is None:
            container.add_widget(MDLabel(
                text=f"Failed to load demo: {module_path}",
                halign="center",
                pos_hint={"center_y": 0.5},
            ))
        else:
            # Falls das Widget bereits einen Parent hat (unwahrscheinlich), abkoppeln
            if root_widget.parent:
                root_widget.parent.remove_widget(root_widget)
            container.add_widget(root_widget)

        self.root.transition = SlideTransition(direction="left")
        self.root.current = "demo"

    def back_to_overview(self):
        demo_screen = self.root.get_screen("demo")
        demo_screen.ids.demo_container.clear_widgets()
        self.root.transition = SlideTransition(direction="right")
        self.root.current = "overview"


if __name__ == "__main__":
    BugfixTestApp().run()
