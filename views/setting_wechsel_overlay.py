# views/setting_wechsel_overlay.py
"""
Setting-Wechsel Overlay - Ersetzt den fehlerhaften MDDialog-Popup.
Verwendet Kivy Animation + einfache Widgets statt MDDialog.
Slide-In von rechts, scrollbare Setting-Liste, inline Merge/Replace-Auswahl.
"""

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.utils import platform as kivy_platform

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.card import MDCard
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon, MDListItemSupportingText
from kivymd.uix.scrollview import MDScrollView

import os
from utils.path_utils import get_application_root

_base_path = str(get_application_root())
_kv_path = os.path.join(_base_path, 'views', 'setting_wechsel_overlay.kv')
if os.path.exists(_kv_path):
    Builder.load_file(_kv_path)


class SettingWechselOverlay(MDBoxLayout):
    """
    Vollbild-Overlay für Setting-Wechsel.
    Wird direkt zum Window hinzugefügt und gleitet von rechts herein.
    Komplett ohne MDDialog - verwendet nur stabile Basis-Widgets.
    """

    current_setting = StringProperty("")
    available_settings = ListProperty([])
    on_setting_chosen = ObjectProperty(None)  # Callback: (setting_name, merge_mode)

    # Interner Zustand
    _selected_setting = StringProperty("")
    _phase = StringProperty("select")  # "select" oder "merge"
    _is_open = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self._build_ui()

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
        self.md_bg_color = self.theme_cls.backgroundColor

        # ===== Top-Spacer für Android-Statusbar/Notch =====
        self._top_spacer = MDBoxLayout(
            size_hint_y=None,
            height=0,
        )
        self.add_widget(self._top_spacer)

        # ===== Top-Bar =====
        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            padding=(dp(8), dp(8), dp(16), dp(8)),
            spacing=dp(8),
            md_bg_color=self.theme_cls.surfaceContainerColor,
        )

        back_btn = MDButton(
            style="text",
            on_release=lambda x: self._handle_back(),
        )
        back_btn.add_widget(MDButtonIcon(icon="arrow-left"))
        back_btn.add_widget(MDButtonText(text="Zurück"))
        top_bar.add_widget(back_btn)

        self._title_label = MDLabel(
            text="Setting wechseln",
            theme_text_color="Primary",
            font_style="Title",
            role="medium",
            bold=True,
            halign="left",
            valign="center",
        )
        top_bar.add_widget(self._title_label)

        self.add_widget(top_bar)
        self.add_widget(MDDivider())

        # ===== Content-Bereich =====
        content_scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(15),
        )

        self._content_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=(dp(16), dp(16), dp(16), dp(24)),
            size_hint_y=None,
            adaptive_height=True,
        )

        content_scroll.add_widget(self._content_box)
        self.add_widget(content_scroll)

        # ===== Bottom-Spacer für Android-Navigationsleiste =====
        self._bottom_spacer = MDBoxLayout(
            size_hint_y=None,
            height=0,
        )
        self.add_widget(self._bottom_spacer)

    def open(self, current_setting, available_settings, on_setting_chosen):
        """
        Öffnet das Overlay mit Slide-Animation von rechts.

        Args:
            current_setting (str): Name des aktuellen Settings
            available_settings (list): Liste aller verfügbaren Setting-Namen
            on_setting_chosen (callable): Callback(setting_name, merge_mode)
                                          merge_mode ist 'merge' oder 'replace'
        """
        if self._is_open:
            return

        self.current_setting = current_setting
        self.available_settings = sorted(available_settings)
        self.on_setting_chosen = on_setting_chosen
        self._selected_setting = ""
        self._phase = "select"

        # UI aufbauen
        self._build_select_phase()

        # Android-Systemleisten-Padding setzen
        top_pad, bottom_pad = self._get_android_padding()
        self._top_spacer.height = top_pad
        self._bottom_spacer.height = bottom_pad

        # Overlay zum Window hinzufügen
        self.size_hint = (1, 1)
        self.pos = (Window.width, 0)  # Startet rechts außerhalb
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
        """Zurück-Button: Phase zurück oder Overlay schließen"""
        if self._phase == "merge":
            self._phase = "select"
            self._build_select_phase()
        else:
            self.close()

    # ==================== Phase 1: Setting-Auswahl ====================

    def _build_select_phase(self):
        """Baut die Setting-Auswahl-Ansicht auf"""
        self._content_box.clear_widgets()
        self._title_label.text = "Setting wechseln"

        # Info-Card: aktuelles Setting
        info_card = MDCard(
            style="elevated",
            size_hint_y=None,
            padding=dp(16),
            md_bg_color=self.theme_cls.primaryContainerColor,
        )
        info_card.bind(minimum_height=info_card.setter("height"))

        info_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            adaptive_height=True,
        )
        info_box.add_widget(MDListItemLeadingIcon(icon="cog"))
        info_label = MDLabel(
            text=f"Aktuelles Setting: [b]{self.current_setting}[/b]",
            markup=True,
            adaptive_height=True,
        )
        info_box.add_widget(info_label)
        info_card.add_widget(info_box)
        self._content_box.add_widget(info_card)

        # Überschrift
        self._content_box.add_widget(MDLabel(
            text="Wähle ein neues Setting:",
            theme_text_color="Secondary",
            font_style="Body",
            role="large",
            size_hint_y=None,
            height=dp(36),
        ))

        # Setting-Liste
        settings_list = MDList(
            size_hint_y=None,
        )
        settings_list.bind(minimum_height=settings_list.setter("height"))

        for setting_name in self.available_settings:
            is_current = (setting_name == self.current_setting)

            item = MDListItem(
                size_hint_y=None,
                height=dp(56),
                on_release=lambda x, s=setting_name: self._on_setting_selected(s),
            )

            if is_current:
                item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                item.add_widget(MDListItemHeadlineText(text=setting_name))
                item.add_widget(MDListItemSupportingText(text="(aktiv)"))
                item.md_bg_color = self.theme_cls.surfaceContainerColor
            else:
                item.add_widget(MDListItemLeadingIcon(icon="swap-horizontal"))
                item.add_widget(MDListItemHeadlineText(text=setting_name))

            settings_list.add_widget(item)

        self._content_box.add_widget(settings_list)

    def _on_setting_selected(self, setting_name):
        """Wird aufgerufen wenn ein Setting ausgewählt wird"""
        if setting_name == self.current_setting:
            return  # Bereits aktives Setting ignorieren

        self._selected_setting = setting_name
        self._phase = "merge"
        self._build_merge_phase()

    # ==================== Phase 2: Merge/Replace-Auswahl ====================

    def _build_merge_phase(self):
        """Baut die Merge/Replace-Auswahl auf"""
        self._content_box.clear_widgets()
        self._title_label.text = f"Zu '{self._selected_setting}' wechseln"

        # Info-Text
        self._content_box.add_widget(MDLabel(
            text=f"Wie möchtest du zu Setting [b]{self._selected_setting}[/b] wechseln?",
            markup=True,
            adaptive_height=True,
            size_hint_y=None,
        ))

        # Merge-Option
        merge_card = self._create_option_card(
            icon="merge",
            title="Zusammenführen",
            description=(
                "Behält deine ausgewählten Elemente (Talente, Handicaps, etc.) "
                "und fügt neue Elemente aus dem neuen Setting hinzu."
            ),
            on_click=lambda: self._apply_choice("merge"),
            color=self.theme_cls.primaryContainerColor,
        )
        self._content_box.add_widget(merge_card)

        # Replace-Option
        replace_card = self._create_option_card(
            icon="swap-horizontal-bold",
            title="Ersetzen",
            description=(
                "Lädt das Setting komplett neu. Ausgewählte Elemente "
                "gehen verloren und werden durch die des neuen Settings ersetzt."
            ),
            on_click=lambda: self._apply_choice("replace"),
            color=self.theme_cls.surfaceContainerColor,
        )
        self._content_box.add_widget(replace_card)

        # Abbrechen-Button
        cancel_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            padding=(0, dp(8), 0, 0),
        )
        cancel_box.add_widget(MDBoxLayout(size_hint_x=1))  # Spacer

        cancel_btn = MDButton(
            style="outlined",
            on_release=lambda x: self._handle_back(),
        )
        cancel_btn.add_widget(MDButtonIcon(icon="arrow-left"))
        cancel_btn.add_widget(MDButtonText(text="Zurück zur Auswahl"))
        cancel_box.add_widget(cancel_btn)

        cancel_box.add_widget(MDBoxLayout(size_hint_x=1))  # Spacer
        self._content_box.add_widget(cancel_box)

    def _create_option_card(self, icon, title, description, on_click, color):
        """Erstellt eine klickbare Options-Card für Merge/Replace"""
        card = MDCard(
            style="elevated",
            size_hint_y=None,
            padding=dp(20),
            md_bg_color=color,
            ripple_behavior=True,
            on_release=lambda x: on_click(),
        )
        card.bind(minimum_height=card.setter("height"))

        card_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            adaptive_height=True,
        )

        # Titel-Zeile mit Icon
        title_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(40),
        )
        title_row.add_widget(MDListItemLeadingIcon(icon=icon))
        title_row.add_widget(MDLabel(
            text=title,
            font_style="Title",
            role="medium",
            bold=True,
            valign="center",
        ))
        card_content.add_widget(title_row)

        # Beschreibung
        desc_label = MDLabel(
            text=description,
            theme_text_color="Secondary",
            font_style="Body",
            role="medium",
            adaptive_height=True,
        )
        card_content.add_widget(desc_label)

        card.add_widget(card_content)
        return card

    def _apply_choice(self, merge_mode):
        """Wendet die Auswahl an und schließt das Overlay"""
        setting_name = self._selected_setting
        callback = self.on_setting_chosen

        self.close()

        # Callback verzögert aufrufen, damit die Animation abgeschlossen ist
        if callback and setting_name:
            Clock.schedule_once(
                lambda dt: callback(setting_name, merge_mode), 0.25
            )
