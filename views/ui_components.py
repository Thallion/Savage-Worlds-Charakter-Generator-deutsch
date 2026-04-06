# views/ui_components.py
"""
UI-Komponenten und Tab-Klassen extrahiert aus main.py
"""

from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.metrics import dp
from kivy.logger import Logger

from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField

from utils.platform_utils import is_mobile_layout, landscape_height

_mobile = is_mobile_layout()


class TextFieldScrollView(MDScrollView):
    """
    MDScrollView mit Workaround für TextField-Focus auf Android.

    Problem: Kivy's ScrollView fängt Touch-Events ab und verwendet einen
    scroll_timeout (55-200ms), um Scroll von Tap zu unterscheiden. Während
    dieses Timeouts wird der Touch nicht an Kinder weitergegeben. Das stört
    die Focus-Verwaltung von MDTextField - die Android-Tastatur erscheint
    kurz und verschwindet sofort wieder.

    Lösung: Touch-Position tracken und bei touch_up (nachdem ScrollView
    ihre Entscheidung getroffen hat) den Focus auf das getroffene TextField
    erzwingen, falls es ein Tap war (kein Scroll).

    Referenz: kivy/kivy#4399, kivy/kivy#890, kivy/kivy#7320
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pending_textfield = None
        self._touch_start_pos = None

    def on_touch_down(self, touch):
        self._pending_textfield = None
        self._touch_start_pos = None

        if self.collide_point(*touch.pos):
            target = self._find_textfield_at(self, touch.pos)
            if target and not target.disabled:
                self._pending_textfield = target
                self._touch_start_pos = (touch.x, touch.y)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        result = super().on_touch_up(touch)
        field = self._pending_textfield
        start = self._touch_start_pos

        if field and start and not field.disabled:
            # Prüfe ob es ein Tap war (kein Scroll-Gesture)
            dx = abs(touch.x - start[0])
            dy = abs(touch.y - start[1])
            if dx < dp(30) and dy < dp(30):
                # Tap erkannt - Focus erzwingen nach aktuellem Frame
                # und nochmals nach kurzem Delay als Absicherung
                Clock.schedule_once(lambda dt: self._ensure_focus(field), 0)
                Clock.schedule_once(lambda dt: self._ensure_focus(field), 0.1)

        self._pending_textfield = None
        self._touch_start_pos = None
        return result

    def _find_textfield_at(self, widget, pos):
        """Sucht rekursiv nach einem MDTextField unter der Touch-Position.

        Verwendet Window-Koordinaten (pos) und wandelt diese pro Kind in
        lokale Koordinaten um. Sammelt alle treffenden TextFields und
        gibt das oberste (höchste y-Position auf dem Bildschirm) zurück,
        um bei überlappenden Kollisionen das visuell richtige Feld zu wählen.
        """
        hits = []
        self._collect_textfields_at(widget, pos, hits)
        if not hits:
            return None
        if len(hits) == 1:
            return hits[0]
        # Bei mehreren Treffern: das Feld wählen, dessen Bildschirm-Position
        # am nächsten an der Touch-Position liegt (Y-Achse)
        best = None
        best_dist = float('inf')
        for field in hits:
            # Mittelpunkt des Feldes in Window-Koordinaten
            field_center_y = field.to_window(field.center_x, field.center_y)[1]
            dist = abs(pos[1] - field_center_y)
            if dist < best_dist:
                best_dist = dist
                best = field
        return best

    def _collect_textfields_at(self, widget, pos, hits):
        """Sammelt alle MDTextFields unter der Touch-Position."""
        for child in widget.children:
            if not hasattr(child, 'collide_point') or not hasattr(child, 'to_widget'):
                continue
            local_pos = child.to_widget(*pos)
            if not child.collide_point(*local_pos):
                continue
            if isinstance(child, MDTextField):
                hits.append(child)
            self._collect_textfields_at(child, pos, hits)

    def _ensure_focus(self, field):
        """Stellt den Focus wieder her, falls ScrollView ihn gestohlen hat."""
        if field and not field.focus and not field.disabled:
            field.focus = True


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
                anim_progress = getattr(self, '_anim_progress', None)
                if anim_progress is not None:
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
        scrim.bind(on_touch_down=self._on_scrim_touch)  # type: ignore[attr-defined]
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
            height=landscape_height(420) + bottom_pad,
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

        # Scrollbare Liste - MDList direkt in ScrollView ohne horizontalen Wrapper
        scroll_view = MDScrollView(
            size_hint=(1, 1),
            bar_width=dp(20) if _mobile else dp(8),
            bar_margin=dp(4) if _mobile else dp(0),
            do_scroll_x=False,
        )
        if _mobile:
            scroll_view.scroll_type = ['bars', 'content']
            scroll_view.scroll_timeout = 200
            scroll_view.scroll_distance = dp(20)
        self._items_list = MDList(size_hint_y=None)
        self._items_list.bind(minimum_height=self._items_list.setter('height'))
        scroll_view.add_widget(self._items_list)
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
        """Wählt einen Eintrag aus und bestätigt sofort (schließt das Sheet)."""
        self._selected = name
        self._confirm()

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