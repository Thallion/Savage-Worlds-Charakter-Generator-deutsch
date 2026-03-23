# views/ui_components.py
"""
UI-Komponenten und Tab-Klassen extrahiert aus main.py
"""

from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.metrics import dp
from kivy.logger import Logger


class SwipeScreenManager(ScreenManager):
    """
    ScreenManager mit Swipe-Gestenerkennung für Mobile-Modus.

    Erkennt horizontale Wischgesten und ruft einen Callback auf,
    um zum nächsten/vorherigen Tab zu wechseln.
    """
    swipe_enabled = BooleanProperty(False)
    min_swipe_distance = NumericProperty(dp(80))
    max_vertical_drift = NumericProperty(dp(60))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._touch_start_x = None
        self._touch_start_y = None
        self._swipe_callback = None  # Callback(direction) - 'left' oder 'right'

    def on_touch_down(self, touch):
        if self.swipe_enabled and self.collide_point(*touch.pos):
            self._touch_start_x = touch.x
            self._touch_start_y = touch.y
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.swipe_enabled and self._touch_start_x is not None:
            dx = touch.x - self._touch_start_x
            dy = abs(touch.y - self._touch_start_y)

            # Horizontaler Swipe: genug horizontal, wenig vertikal
            if abs(dx) > self.min_swipe_distance and dy < self.max_vertical_drift:
                # Laufende Transition abbrechen bevor ein neuer Wechsel getriggert wird
                if hasattr(self, '_anim_progress') and self._anim_progress is not None:
                    try:
                        from kivy.uix.screenmanager import NoTransition
                        self.transition = NoTransition()
                    except Exception:
                        pass
                if self._swipe_callback:
                    direction = 'right' if dx > 0 else 'left'
                    self._swipe_callback(direction)

            self._touch_start_x = None
            self._touch_start_y = None

        return super().on_touch_up(touch)


from kivymd.uix.tab import MDTabsItem, MDTabsItemText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle


class SearchBottomSheet(ModalView):
    """
    Eigenes Bottom-Sheet mit Suchfeld und Liste für Android-kompatible Auswahl.
    Verwendet ModalView statt MDDialog, um das Touch-Stealing-Problem zu vermeiden.

    Verwendung:
        sheet = SearchBottomSheet(
            title="Volk auswählen",
            items=["Mensch", "Elf", "Zwerg"],
            selected=current_selection,
            on_confirm=lambda name: print(f"Gewählt: {name}"),
            on_cancel=lambda: print("Abgebrochen"),
            search_hint="Volk suchen...",
        )
        sheet.open()
    """

    def __init__(self, title="Auswählen", items=None, selected=None,
                 on_confirm=None, on_cancel=None, search_hint="Suchen...",
                 allow_none=False, none_label="Keine Auswahl", **kwargs):
        # ModalView-Einstellungen: transparenter Hintergrund, kein auto_dismiss-Bereich-Problem
        kwargs.setdefault('size_hint', (1, 1))
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('background', '')
        kwargs.setdefault('auto_dismiss', False)
        super().__init__(**kwargs)

        self._items = items or []
        self._selected = selected
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self._allow_none = allow_none
        self._none_label = none_label

        # Scrim (halbtransparenter Hintergrund) - Klick schließt das Sheet
        scrim = Widget(size_hint=(1, 1))
        scrim.bind(on_touch_down=self._on_scrim_touch)
        self.add_widget(scrim)

        # Sheet-Card (untere Hälfte)
        from kivymd.app import MDApp
        from kivy.utils import platform as kivy_platform
        app = MDApp.get_running_app()
        theme = app.theme_cls if app else None

        # Bottom-Padding für Android-Navigationsleiste
        bottom_pad = dp(48) if kivy_platform == 'android' else 0

        self._sheet = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(420) + bottom_pad,
            pos_hint={'center_x': 0.5},
            md_bg_color=theme.surfaceContainerColor if theme else (0.15, 0.15, 0.15, 1),
            radius=[dp(16), dp(16), 0, 0],
            padding=[0, dp(8), 0, bottom_pad],
        )

        # Drag-Handle (visueller Balken)
        handle_container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(20),
            padding=[0, dp(8), 0, dp(4)],
        )
        handle_bar = MDBoxLayout(
            size_hint=(None, None),
            size=(dp(32), dp(4)),
            pos_hint={'center_x': 0.5},
            md_bg_color=(0.5, 0.5, 0.5, 1),
            radius=[dp(2)],
        )
        handle_container.add_widget(handle_bar)
        self._sheet.add_widget(handle_container)

        # Header: Titel + Bestätigen-Button
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            padding=[dp(16), 0, dp(8), 0],
            spacing=dp(8),
        )
        header.add_widget(MDIconButton(
            icon="close",
            on_release=lambda x: self._cancel(),
            pos_hint={'center_y': 0.5},
        ))
        header.add_widget(MDLabel(
            text=title,
            font_style="Title",
            role="medium",
            bold=True,
            size_hint_x=1,
            pos_hint={'center_y': 0.5},
        ))
        confirm_btn = MDIconButton(
            icon="check",
            on_release=lambda x: self._confirm(),
            pos_hint={'center_y': 0.5},
        )
        header.add_widget(confirm_btn)
        self._sheet.add_widget(header)

        # Suchfeld
        search_container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(56),
            padding=[dp(16), 0, dp(16), dp(4)],
        )
        self._search_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(48),
            size_hint_x=1,
        )
        self._search_field.add_widget(MDTextFieldHintText(text=search_hint))
        self._search_field.bind(text=self._filter_list)
        search_container.add_widget(self._search_field)
        self._sheet.add_widget(search_container)

        # Scrollbare Liste
        scroll_view = MDScrollView(
            size_hint=(1, 1),
            bar_width=dp(8),
        )
        scroll_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
        )
        self._items_list = MDList(size_hint_y=None, size_hint_x=1)
        self._items_list.bind(minimum_height=self._items_list.setter('height'))
        scroll_layout.add_widget(self._items_list)
        # Touch-Zone rechts für zuverlässiges Scrollen auf Android
        scroll_layout.add_widget(MDBoxLayout(size_hint_x=None, width=dp(20)))
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
        scroll_view.add_widget(scroll_layout)
        self._sheet.add_widget(scroll_view)

        self.add_widget(self._sheet)

        # Initial-Position: unter dem Bildschirm (für Slide-Animation)
        self._sheet.y = -self._sheet.height

        # Liste befüllen
        self._populate_list()

    def open(self, *args, **kwargs):
        """Öffnet das Sheet mit Slide-Up-Animation."""
        super().open(*args, **kwargs)
        # Scrim einblenden + Sheet hochschieben
        Clock.schedule_once(self._animate_open, 0.05)

    def _animate_open(self, dt):
        """Slide-Up-Animation für das Sheet."""
        self._sheet.y = -self._sheet.height
        anim = Animation(y=0, duration=0.25, t='out_cubic')
        anim.start(self._sheet)

    def _on_scrim_touch(self, widget, touch):
        """Schließt bei Touch auf den Scrim-Bereich (oberhalb des Sheets)."""
        if touch.y > self._sheet.top:
            self._cancel()
            return True
        return False

    def _populate_list(self, *args):
        """Befüllt die Liste, gefiltert nach Suchtext."""
        self._items_list.clear_widgets()
        search_text = self._search_field.text.lower() if self._search_field.text else ""

        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        theme = app.theme_cls if app else None

        # "Keine Auswahl" Option
        if self._allow_none:
            if not search_text or search_text in self._none_label.lower():
                is_sel = self._selected is None
                item = MDListItem(
                    size_hint_y=None,
                    height=dp(48),
                    on_release=lambda x: self._select(None),
                    md_bg_color=theme.primaryContainerColor if (is_sel and theme) else [0, 0, 0, 0],
                )
                if is_sel:
                    item.add_widget(MDListItemLeadingIcon(
                        icon="check-circle",
                        theme_icon_color="Custom",
                        icon_color=theme.primaryColor if theme else (1, 1, 1, 1),
                    ))
                headline = MDListItemHeadlineText(text=self._none_label)
                if is_sel:
                    headline.bold = True
                item.add_widget(headline)
                self._items_list.add_widget(item)

        # Einträge
        for name in self._items:
            if search_text and search_text not in name.lower():
                continue
            is_sel = (self._selected == name)
            item = MDListItem(
                size_hint_y=None,
                height=dp(48),
                on_release=lambda x, n=name: self._select(n),
                md_bg_color=theme.primaryContainerColor if (is_sel and theme) else [0, 0, 0, 0],
            )
            if is_sel:
                item.add_widget(MDListItemLeadingIcon(
                    icon="check-circle",
                    theme_icon_color="Custom",
                    icon_color=theme.primaryColor if theme else (1, 1, 1, 1),
                ))
            headline = MDListItemHeadlineText(text=name)
            if is_sel:
                headline.bold = True
            item.add_widget(headline)
            self._items_list.add_widget(item)

    def _filter_list(self, *args):
        """Filtert die Liste bei Texteingabe."""
        self._populate_list()

    def _select(self, name):
        """Markiert einen Eintrag als ausgewählt."""
        self._selected = name
        self._populate_list()

    def _confirm(self):
        """Bestätigt die Auswahl und schließt das Sheet."""
        anim = Animation(y=-self._sheet.height, duration=0.2, t='in_cubic')
        anim.bind(on_complete=lambda *a: self._finish_confirm())
        anim.start(self._sheet)

    def _finish_confirm(self):
        self.dismiss()
        if self._on_confirm:
            self._on_confirm(self._selected)

    def _cancel(self):
        """Bricht ab und schließt das Sheet."""
        anim = Animation(y=-self._sheet.height, duration=0.2, t='in_cubic')
        anim.bind(on_complete=lambda *a: self._finish_cancel())
        anim.start(self._sheet)

    def _finish_cancel(self):
        self.dismiss()
        if self._on_cancel:
            self._on_cancel()


class CustomTabsItem(MDTabsItem):
    """
    Eine benutzerdefinierte MDTabsItem-Klasse, die ein 'title'-Attribut hinzufügt.
    """
    title = StringProperty("")

    def __init__(self, **kwargs):
        # Pop 'title' aus kwargs, um es nicht an die Basisklasse weiterzugeben
        self.title = kwargs.pop('title', "")
        super().__init__(**kwargs)
        # Setze das 'title' Attribut basierend auf 'MDTabsItemText'
        for child in self.children:
            if isinstance(child, MDTabsItemText):
                self.title = child.text
                break