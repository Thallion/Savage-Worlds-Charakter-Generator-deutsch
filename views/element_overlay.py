# views/element_overlay.py
"""
Generisches Element-Overlay für Setting-Element-Dialoge.
Ersetzt MDDialog-basierte Popups durch stabiles Slide-In Overlay.
Nimmt beliebige Content-Widgets (z.B. TalentDialogContent) auf.

Enthält auch ElementListContent - ein wiederverwendbares Listen-Widget
mit Suchfeld für Lösch-Dialoge.
"""

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.utils import platform as kivy_platform

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItem, MDListItemLeadingIcon, MDListItemHeadlineText, MDListItemTrailingCheckbox
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon, MDTextFieldHintText

from views.ui_components import TextFieldScrollView


class ElementListContent(MDBoxLayout):
    """
    Wiederverwendbares Listen-Widget mit Suchfeld für Lösch-Dialoge.
    Unterstützt Einzel- und Mehrfach-Auswahl.
    """

    def __init__(self, items, on_select=None, multi_select=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(8)
        self.size_hint_y = None
        self.height = dp(400)

        self._all_items = sorted(items) if items else []
        self._on_select = on_select
        self._multi_select = multi_select
        self._selected_item = None
        self._selected_items = set()
        self._item_widgets = {}
        self._checkboxes = {}

        self._build_ui()

    def _build_ui(self):
        """Erstellt Suchfeld und scrollbare Liste"""
        # Suchfeld
        self._search_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(48),
        )
        self._search_field.add_widget(MDTextFieldLeadingIcon(icon="magnify"))
        self._search_field.add_widget(MDTextFieldHintText(text="Suchen..."))
        self._search_field.bind(text=self._on_search_text)
        self.add_widget(self._search_field)

        # Scrollbare Liste
        scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(15),
            bar_margin=dp(12),
        )
        self._list = MDList(
            size_hint_y=None,
        )
        self._list.bind(minimum_height=self._list.setter("height"))
        scroll.add_widget(self._list)
        self.add_widget(scroll)

        self._populate_list()

    def _populate_list(self, filter_text=""):
        """Baut die Liste auf, optional gefiltert"""
        self._list.clear_widgets()
        self._item_widgets.clear()
        self._checkboxes.clear()
        search = filter_text.lower().strip()

        for item_name in self._all_items:
            if search and search not in item_name.lower():
                continue

            if self._multi_select:
                item = MDListItem(
                    size_hint_y=None,
                    height=dp(48),
                )
                item.add_widget(MDListItemHeadlineText(text=item_name))

                checkbox = MDListItemTrailingCheckbox(
                    active=item_name in self._selected_items,
                )
                checkbox.bind(on_release=lambda x, cb=checkbox, name=item_name: self._on_checkbox_toggled(name, cb))
                item.add_widget(checkbox)
                self._checkboxes[item_name] = checkbox
            else:
                item = MDListItem(
                    on_release=lambda x, name=item_name: self._on_item_selected(name),
                    size_hint_y=None,
                    height=dp(48),
                )
                item.add_widget(MDListItemHeadlineText(text=item_name))

                if item_name == self._selected_item:
                    item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                    item.md_bg_color = self.theme_cls.primaryContainerColor
                else:
                    item.add_widget(MDListItemLeadingIcon(icon="circle-outline"))

            self._list.add_widget(item)
            self._item_widgets[item_name] = item

    def _on_checkbox_toggled(self, item_name, checkbox):
        """Callback wenn eine Checkbox umgeschaltet wird (Mehrfachauswahl)"""
        if checkbox.active:
            self._selected_items.add(item_name)
        else:
            self._selected_items.discard(item_name)
        if self._on_select:
            self._on_select(item_name)

    def _on_item_selected(self, item_name):
        """Callback wenn ein Element ausgewählt wird (Einzel-Auswahl)"""
        self._selected_item = item_name
        if self._on_select:
            self._on_select(item_name)
        self._populate_list(self._search_field.text if self._search_field else "")

    def _on_search_text(self, instance, text):
        """Filtert die Liste bei Texteingabe"""
        self._populate_list(text)

    def get_selected_items(self):
        """Gibt die ausgewählten Elemente zurück (bei Mehrfachauswahl)"""
        return list(self._selected_items)

    def get_selected_item(self):
        """Gibt das ausgewählte Element zurück (bei Einzel-Auswahl)"""
        return self._selected_item


class ElementOverlay(MDBoxLayout):
    """
    Generisches Vollbild-Overlay für Setting-Element-Dialoge.
    Slide-In von rechts, scrollbarer Content-Bereich,
    konfigurierbare Aktion-Buttons.
    """

    _is_open = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self._on_action = None
        self._on_close = None
        self._build_ui()
        # Theme-Farben reaktiv binden
        self.theme_cls.bind(
            backgroundColor=self._update_theme_colors,
            surfaceContainerColor=self._update_theme_colors,
        )
        self._update_theme_colors()

    def _update_theme_colors(self, *args):
        """Aktualisiert alle Theme-abhängigen Farben"""
        self.md_bg_color = self.theme_cls.backgroundColor
        self._top_bar.md_bg_color = self.theme_cls.surfaceContainerColor
        self._bottom_bar.md_bg_color = self.theme_cls.surfaceContainerColor

    def _get_android_padding(self):
        """Ermittelt Top- und Bottom-Padding für Android-Systemleisten"""
        if kivy_platform != 'android':
            return 0, 0
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            top = getattr(app, '_android_top_padding', dp(24))
            bottom = getattr(app, '_android_bottom_padding', dp(24))
            return top, bottom
        except Exception:
            return dp(24), dp(24)

    def _build_ui(self):
        """Erstellt die UI-Struktur programmatisch"""

        # ===== Top-Spacer für Android-Statusbar/Notch =====
        self._top_spacer = MDBoxLayout(
            size_hint_y=None,
            height=0,
        )
        self.add_widget(self._top_spacer)

        # ===== Top-Bar =====
        self._top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            padding=(dp(8), dp(8), dp(16), dp(8)),
            spacing=dp(8),
        )

        back_btn = MDButton(
            style="text",
            on_release=lambda x: self._handle_back(),
        )
        back_btn.add_widget(MDButtonIcon(icon="arrow-left"))
        back_btn.add_widget(MDButtonText(text="Zurück"))
        self._top_bar.add_widget(back_btn)

        self._title_label = MDLabel(
            text="",
            theme_text_color="Primary",
            font_style="Title",
            role="medium",
            bold=True,
            halign="left",
            valign="center",
        )
        self._top_bar.add_widget(self._title_label)

        self.add_widget(self._top_bar)
        self.add_widget(MDDivider())

        # ===== Content-Bereich (scrollbar) =====
        # TextFieldScrollView statt MDScrollView: verhindert Focus-Verlust
        # bei MDTextFields auf Android (Tastatur verschwindet sofort nach Touch)
        self._content_scroll = TextFieldScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(15),
            bar_margin=dp(12),
        )

        self._content_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=(dp(16), dp(16), dp(16), dp(24)),
            size_hint_y=None,
            adaptive_height=True,
        )

        self._content_scroll.add_widget(self._content_box)
        self.add_widget(self._content_scroll)

        # ===== Bottom-Bar =====
        self._bottom_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(80),
            padding=(dp(16), dp(8), dp(16), dp(24)),
            spacing=dp(12),
        )

        self._bottom_bar.add_widget(MDBoxLayout(size_hint_x=1))  # Spacer

        self._cancel_btn = MDButton(
            style="outlined",
            on_release=lambda x: self._handle_back(),
        )
        self._cancel_btn.add_widget(MDButtonText(text="Abbrechen"))
        self._bottom_bar.add_widget(self._cancel_btn)

        self._action_btn = MDButton(
            style="filled",
            on_release=lambda x: self._handle_action(),
        )
        self._action_btn_text = MDButtonText(text="Speichern")
        self._action_btn.add_widget(self._action_btn_text)
        self._bottom_bar.add_widget(self._action_btn)

        self.add_widget(MDDivider())
        self.add_widget(self._bottom_bar)

        # ===== Bottom-Spacer für Android-Navigationsleiste =====
        self._bottom_spacer = MDBoxLayout(
            size_hint_y=None,
            height=0,
            md_bg_color=self.theme_cls.surfaceContainerColor,
        )
        self.add_widget(self._bottom_spacer)

    def open(self, title, content_widget, action_text="Speichern", on_action=None, on_close=None):
        """
        Öffnet das Overlay mit Slide-Animation von rechts.

        Args:
            title (str): Überschrift in der Top-Bar
            content_widget: Beliebiges Kivy-Widget als Inhalt
            action_text (str): Text des Aktion-Buttons
            on_action (callable): Callback beim Klick auf Aktion-Button
            on_close (callable): Optionaler Callback beim Schließen
        """
        if self._is_open:
            return

        self._on_action = on_action
        self._on_close = on_close

        # UI konfigurieren
        self._title_label.text = title
        self._action_btn_text.text = action_text

        # Content einfügen
        self._content_box.clear_widgets()
        self._content_box.add_widget(content_widget)

        # Android-Systemleisten-Padding setzen
        top_pad, bottom_pad = self._get_android_padding()
        self._top_spacer.height = top_pad
        self._bottom_spacer.height = bottom_pad

        # Overlay zum Window hinzufügen
        self.size_hint = (1, 1)
        self.pos = (Window.width, 0)
        Window.add_widget(self)

        # Slide-In Animation
        anim = Animation(pos=(0, 0), duration=0.25, t="out_cubic")
        anim.start(self)
        self._is_open = True

    def close(self):
        """Schließt das Overlay mit Slide-Out Animation nach rechts"""
        if not self._is_open:
            return

        # Keyboard-Fokus freigeben (verhindert Ghost-Keyboards)
        Window.release_all_keyboards()

        anim = Animation(pos=(Window.width, 0), duration=0.2, t="in_cubic")
        anim.bind(on_complete=self._on_close_complete)
        anim.start(self)

    def _on_close_complete(self, *args):
        """Entfernt das Overlay nach der Animation"""
        try:
            Window.remove_widget(self)
        except Exception:
            pass
        self._is_open = False

        # Content-Widget entfernen (verhindert Parent-Konflikte bei Wiederverwendung)
        self._content_box.clear_widgets()

        if self._on_close:
            self._on_close()

    def on_touch_down(self, touch):
        """Konsumiert alle Touch-Events wenn das Overlay offen ist"""
        if self._is_open:
            super().on_touch_down(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        """Verhindert Touch-Move Durchreichung an darunterliegende Widgets"""
        if self._is_open:
            super().on_touch_move(touch)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        """Verhindert Touch-Up Durchreichung an darunterliegende Widgets"""
        if self._is_open:
            super().on_touch_up(touch)
            return True
        return super().on_touch_up(touch)

    def _handle_back(self):
        """Zurück-Button: Overlay schließen"""
        self.close()

    def _handle_action(self):
        """Aktion-Button: Callback aufrufen (mit Doppelklick-Schutz)"""
        if not self._on_action:
            return
        # Doppelklick-Schutz: Button kurz deaktivieren
        self._action_btn.disabled = True
        Clock.schedule_once(lambda dt: setattr(self._action_btn, 'disabled', False), 0.5)
        self._on_action()
