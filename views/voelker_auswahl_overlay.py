# views/voelker_auswahl_overlay.py
"""
Völker-Auswahl Overlay - Ersetzt den MDDialog-Popup.
Slide-In von rechts, scrollbare Völker-Liste mit Suchfeld,
optionale Phase 2 für Zusatzelemente (freie Talente, Halbelf ENTWEDER/ODER, etc.).
"""

import time

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty, ObjectProperty, DictProperty
from kivy.utils import platform as kivy_platform

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon, MDFabButton
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon, MDListItemSupportingText, MDListItemTrailingCheckbox
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

from views.ui_components import TextFieldScrollView
from utils.platform_utils import is_mobile_layout

_mobile = is_mobile_layout()


class VoelkerAuswahlOverlay(MDBoxLayout):
    """
    Vollbild-Overlay für Völker-Auswahl.
    Phase 1: Volk aus Liste wählen (mit Suchfeld).
    Phase 2: Zusatzelemente auswählen (freie Talente, Halbelf, Menschen, etc.).
    """

    current_volk = StringProperty("")
    available_voelker = ListProperty([])
    on_volk_chosen = ObjectProperty(None)  # Callback: (volk_name, zusatzelemente_dict)

    # Interner Zustand
    _selected_volk = StringProperty("")
    _phase = StringProperty("select")  # "select" oder "extras"
    _is_open = False
    _charakter = ObjectProperty(None, allownone=True)
    _zusatzelemente_info = DictProperty({})

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
            text="Volk auswählen",
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
        # TextFieldScrollView: verhindert Focus-Verlust bei Suchfeld auf Android
        content_scroll = TextFieldScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(20) if _mobile else dp(12),
            bar_margin=dp(8) if _mobile else dp(4),
        )
        if _mobile:
            content_scroll.scroll_type = ['bars', 'content']

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

    def open(self, current_volk, available_voelker, charakter, on_volk_chosen):
        """
        Öffnet das Overlay mit Slide-Animation von rechts.

        Args:
            current_volk (str): Name des aktuell ausgewählten Volks (oder "")
            available_voelker (list): Liste aller verfügbaren Volk-Namen
            charakter: Das Charakterobjekt (für Zusatzelemente-Abfragen)
            on_volk_chosen (callable): Callback(volk_name, zusatzelemente_dict)
        """
        if self._is_open:
            return

        self.current_volk = current_volk or ""
        self.available_voelker = sorted(available_voelker)
        self._charakter = charakter
        self.on_volk_chosen = on_volk_chosen
        self._selected_volk = ""
        self._phase = "select"

        # UI aufbauen
        self._build_select_phase()

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
        if self._phase == "extras":
            self._phase = "select"
            self._build_select_phase()
        else:
            self.close()

    # ==================== Phase 1: Volk-Auswahl ====================

    def _build_select_phase(self):
        """Baut die Volk-Auswahl-Ansicht auf"""
        self._content_box.clear_widgets()
        self._title_label.text = "Volk auswählen"

        # Info-Card: aktuelles Volk
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
        info_box.add_widget(MDListItemLeadingIcon(icon="account-group"))
        volk_text = self.current_volk if self.current_volk else "Keins"
        info_label = MDLabel(
            text=f"Aktuelles Volk: [b]{volk_text}[/b]",
            markup=True,
            adaptive_height=True,
        )
        info_box.add_widget(info_label)
        info_card.add_widget(info_box)
        self._content_box.add_widget(info_card)

        # Suchfeld
        self._search_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(56),
            size_hint_x=1,
        )
        self._search_field.add_widget(MDTextFieldHintText(text="Volk suchen..."))
        self._search_field.bind(text=lambda *args: self._populate_voelker_list())
        self._content_box.add_widget(self._search_field)

        # Völker-Liste
        self._voelker_list = MDList(
            size_hint_y=None,
        )
        self._voelker_list.bind(minimum_height=self._voelker_list.setter("height"))
        self._content_box.add_widget(self._voelker_list)

        self._populate_voelker_list()

    def _populate_voelker_list(self):
        """Befüllt die Völker-Liste, gefiltert nach Suchtext"""
        self._voelker_list.clear_widgets()
        search_text = ""
        if hasattr(self, '_search_field') and self._search_field.text:
            search_text = self._search_field.text.lower()

        # "Kein Volk" Option
        if not search_text or "kein" in search_text:
            is_none_selected = not self.current_volk
            item = MDListItem(
                size_hint_y=None,
                height=dp(56),
                on_release=lambda x: self._on_volk_selected(None),
            )
            if is_none_selected:
                item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                item.md_bg_color = self.theme_cls.surfaceContainerColor
            else:
                item.add_widget(MDListItemLeadingIcon(icon="close-circle-outline"))
            headline = MDListItemHeadlineText(text="Kein Volk")
            if is_none_selected:
                headline.bold = True
            item.add_widget(headline)
            self._voelker_list.add_widget(item)

        # Alle Völker
        for volk_name in self.available_voelker:
            if search_text and search_text not in volk_name.lower():
                continue

            is_current = (volk_name == self.current_volk)

            item = MDListItem(
                size_hint_y=None,
                height=dp(56),
                on_release=lambda x, v=volk_name: self._on_volk_selected(v),
            )

            if is_current:
                item.add_widget(MDListItemLeadingIcon(icon="check-circle"))
                item.add_widget(MDListItemHeadlineText(text=volk_name, bold=True))
                item.add_widget(MDListItemSupportingText(text="(aktiv)"))
                item.md_bg_color = self.theme_cls.surfaceContainerColor
            else:
                item.add_widget(MDListItemLeadingIcon(icon="account"))
                item.add_widget(MDListItemHeadlineText(text=volk_name))

            self._voelker_list.add_widget(item)

    def _on_volk_selected(self, volk_name):
        """Wird aufgerufen wenn ein Volk ausgewählt wird"""
        # "Kein Volk" → sofort übernehmen
        if volk_name is None:
            self._apply_choice(None, {})
            return

        # Bereits aktives Volk → ignorieren
        if volk_name == self.current_volk:
            return

        self._selected_volk = volk_name

        # Prüfe ob Phase 2 nötig ist
        from functions.volk_funktionen import get_volk_zusatzelemente
        zusatzelemente = get_volk_zusatzelemente(self._charakter, volk_name)
        self._zusatzelemente_info = zusatzelemente

        hat_extras = (
            zusatzelemente.get('halbelf_entweder_oder', False) or
            zusatzelemente.get('menschen_vielseitig', False) or
            zusatzelemente.get('freie_talente', False) or
            zusatzelemente.get('freie_attribute', False) or
            zusatzelemente.get('freie_fertigkeiten', False)
        )

        if hat_extras:
            self._phase = "extras"
            self._build_extras_phase()
        else:
            # Keine Zusatzelemente → sofort übernehmen
            self._apply_choice(volk_name, {})

    # ==================== Phase 2: Zusatzelemente ====================

    def _build_extras_phase(self):
        """Baut die Zusatzelemente-Auswahl auf"""
        self._content_box.clear_widgets()
        self._title_label.text = f"{self._selected_volk} – Optionen"

        info = self._zusatzelemente_info

        # Halbelf ENTWEDER/ODER
        if info.get('halbelf_entweder_oder', False):
            self._build_halbelf_section()
            return

        # Menschen Vielseitig
        if info.get('menschen_vielseitig', False):
            self._build_menschen_section()
            return

        # Generische Zusatzelemente (freie Talente, Attribute, Fertigkeiten)
        self._build_generic_extras_section()

    def _build_halbelf_section(self):
        """Halbelf: Freies Talent ODER +1 Geschicklichkeit"""
        self._content_box.add_widget(MDLabel(
            text="Wähle eine der folgenden Optionen:",
            adaptive_height=True,
            size_hint_y=None,
        ))

        # Option 1: Freies Talent
        talent_card = self._create_option_card(
            icon="star",
            title="Freies Anfängertalent",
            description="Wähle ein freies Anfängertalent aus der Liste.",
            on_click=lambda: self._show_talent_selection('halbelf_talent'),
            color=self.theme_cls.primaryContainerColor,
        )
        self._content_box.add_widget(talent_card)

        # Option 2: +1 Geschicklichkeit
        attr_card = self._create_option_card(
            icon="arm-flex",
            title="+1 Geschicklichkeit",
            description="Erhöht die Geschicklichkeit um eine Würfelstufe.",
            on_click=lambda: self._apply_choice(self._selected_volk, {'halbelf_attribut': True}),
            color=self.theme_cls.surfaceContainerColor,
        )
        self._content_box.add_widget(attr_card)

        self._add_back_button()

    def _build_menschen_section(self):
        """Menschen: Freies Talent ODER 2 Fertigkeitspunkte"""
        self._content_box.add_widget(MDLabel(
            text="Vielseitig – Wähle eine der folgenden Optionen:",
            adaptive_height=True,
            size_hint_y=None,
            bold=True,
        ))

        # Option 1: Freies Talent
        talent_card = self._create_option_card(
            icon="star",
            title="Freies Anfängertalent",
            description="Wähle ein freies Anfängertalent aus der Liste.",
            on_click=lambda: self._show_talent_selection('mensch_talent'),
            color=self.theme_cls.primaryContainerColor,
        )
        self._content_box.add_widget(talent_card)

        # Option 2: 2 Fertigkeitspunkte
        fert_card = self._create_option_card(
            icon="school",
            title="2 Fertigkeitspunkte",
            description="Erhalte 2 zusätzliche Fertigkeitspunkte bei der Charaktererstellung.",
            on_click=lambda: self._apply_choice(self._selected_volk, {'mensch_fertigkeitspunkte': True}),
            color=self.theme_cls.surfaceContainerColor,
        )
        self._content_box.add_widget(fert_card)

        self._add_back_button()

    def _build_generic_extras_section(self):
        """Generische Zusatzelemente: freie Talente, Attribute, Fertigkeiten"""
        info = self._zusatzelemente_info

        # Info-Text
        self._content_box.add_widget(MDLabel(
            text=f"Optionen für [b]{self._selected_volk}[/b]:",
            markup=True,
            adaptive_height=True,
            size_hint_y=None,
        ))

        # Freie Talente
        if info.get('freie_talente', False):
            talent_card = self._create_option_card(
                icon="star",
                title="Freies Anfängertalent",
                description="Wähle ein freies Anfängertalent aus der verfügbaren Liste.",
                on_click=lambda: self._show_talent_selection('freies_talent'),
                color=self.theme_cls.primaryContainerColor,
            )
            self._content_box.add_widget(talent_card)

        # Freie Attribute
        if info.get('freie_attribute', False):
            attribut_optionen = info.get('attribut_optionen', [])
            if len(attribut_optionen) <= 4:
                # Wenige Optionen → als Cards anzeigen
                self._content_box.add_widget(MDLabel(
                    text="Freies Attribut:",
                    bold=True,
                    adaptive_height=True,
                    size_hint_y=None,
                ))
                for attr in attribut_optionen:
                    attr_card = self._create_option_card(
                        icon="arm-flex",
                        title=attr,
                        description=f"+1 Würfelstufe auf {attr}",
                        on_click=lambda a=attr: self._apply_choice(
                            self._selected_volk, {'freies_attribut': a}),
                        color=self.theme_cls.surfaceContainerColor,
                    )
                    self._content_box.add_widget(attr_card)
            else:
                # Viele Optionen → als Chip-Liste
                self._show_chip_selection(
                    "Freies Attribut wählen:",
                    attribut_optionen,
                    lambda attr: self._apply_choice(
                        self._selected_volk, {'freies_attribut': attr}),
                )

        # Freie Fertigkeiten
        if info.get('freie_fertigkeiten', False):
            from functions.volk_funktionen import get_verfuegbare_fertigkeiten
            fertigkeiten = get_verfuegbare_fertigkeiten(self._charakter, nur_verstand=True)
            self._show_chip_selection(
                "Verstandsbasierte Fertigkeit wählen:",
                fertigkeiten,
                lambda fert: self._apply_choice(
                    self._selected_volk, {'freie_fertigkeit': fert}),
            )

        self._add_back_button()

    # ==================== Talent-Auswahl (Sub-Phase) ====================

    def _show_talent_selection(self, talent_typ):
        """Zeigt eine durchsuchbare Talent-Auswahl mit Checkboxen als separates Popup"""
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
        from kivy.core.window import Window
        
        from functions.volk_funktionen import get_freie_talente
        talente = get_freie_talente(self._charakter)
        Logger.debug(f"Talent-Auswahl für {self._selected_volk}: {len(talente)} Talente gefunden, typ={talent_typ}")
        
        if not talente or (len(talente) == 1 and "Keine" in talente[0]):
            self._show_no_talente_message()
            return

        self._talent_selected = None
        self._last_talent_click = 0
        selected_talent = [None]
        checkboxes = {}

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            padding=[dp(16), dp(8), dp(16), dp(8)]
        )

        info_label = MDLabel(
            text=f"Wähle ein freies Anfängertalent für {self._selected_volk}:",
            font_style="Body",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(info_label)

        search_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(56)
        )
        search_field.add_widget(MDTextFieldHintText(text="Talent suchen..."))
        content.add_widget(search_field)

        # Feste Höhen: Info-Label(48) + Suchfeld(56) + Spacing/Padding(32)
        content_fixed = dp(48) + dp(56) + dp(32)
        # Dialog-Chrome: Headline(56) + Buttons(64) + internes Padding(40)
        dialog_chrome = dp(160)
        # Maximale Dialog-Höhe: 80% des Bildschirms
        max_dialog_height = Window.height * 0.8
        scroll_height = min(dp(350), max_dialog_height - content_fixed - dialog_chrome)
        scroll_height = max(scroll_height, dp(150))

        scroll = TextFieldScrollView(
            size_hint=(1, None),
            height=scroll_height,
            do_scroll_x=False,
            bar_width=dp(20) if _mobile else dp(12),
            bar_margin=dp(8) if _mobile else dp(4)
        )
        scroll.scroll_type = ['bars', 'content']

        talent_list = MDList(size_hint_y=None)
        talent_list.bind(minimum_height=talent_list.setter('height'))
        if _mobile:
            talent_list.padding = [0, 0, dp(32), 0]

        def populate_talents(*args):
            talent_list.clear_widgets()
            checkboxes.clear()
            search_text = search_field.text.lower() if search_field.text else ""
            for talent_name in sorted(talente):
                if not talent_name or not str(talent_name).strip():
                    continue
                if search_text and search_text not in str(talent_name).lower():
                    continue

                row = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(56),
                    spacing=dp(8),
                    padding=[dp(4), dp(4), dp(8), dp(4)]
                )

                # Info-Button für Talent-Beschreibung
                info_btn = MDFabButton(
                    icon="information-outline",
                    style="small",
                    size_hint=(None, None),
                    size=(dp(36), dp(36)),
                    pos_hint={"center_y": 0.5}
                )
                t_info = talent_name
                info_btn.bind(on_release=lambda x, t=t_info: self._show_talent_info(t))
                row.add_widget(info_btn)

                # Talent-Name
                name_label = MDLabel(
                    text=str(talent_name),
                    halign="left",
                    valign="center",
                )
                row.add_widget(name_label)

                # Checkbox (Radio-Style Auswahl)
                checkbox = MDCheckbox(
                    size_hint=(None, None),
                    size=(dp(48), dp(48)),
                    pos_hint={"center_y": 0.5}
                )
                cb = checkbox
                t_name = talent_name
                checkbox.bind(on_release=lambda x, cb=cb, t=t_name: self._on_talent_checkbox_clicked(talent_typ, t, cb, checkboxes, selected_talent))
                row.add_widget(checkbox)
                talent_list.add_widget(row)
                checkboxes[talent_name] = checkbox

        def on_confirm(*args):
            if selected_talent[0]:
                self._on_talent_chosen(talent_typ, selected_talent[0])
                if hasattr(self, '_talent_selection_popup'):
                    self._talent_selection_popup.dismiss()
            else:
                from services.service_container import service_container
                ds = service_container.get_dialog_service()
                if ds:
                    ds.show_warning_dialog("Bitte wähle ein Talent aus.")

        search_field.bind(text=populate_talents)
        populate_talents()

        scroll.add_widget(talent_list)
        content.add_widget(scroll)
        content.height = content_fixed + scroll_height

        dialog_height = min(content.height + dialog_chrome, max_dialog_height)
        self._talent_selection_popup = MDDialog(
            MDDialogHeadlineText(text="Freies Talent wählen"),
            MDDialogContentContainer(content, orientation="vertical"),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"), style="text",
                    on_release=lambda x: self._talent_selection_popup.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Auswählen"), style="filled",
                    on_release=on_confirm
                ),
            ),
            size_hint=(0.85, None),
            height=dialog_height,
        )
        self._talent_selection_popup.open()

    def _show_no_talente_message(self):
        """Zeigt eine Meldung wenn keine Talente verfügbar sind"""
        self._content_box.clear_widgets()
        self._title_label.text = f"{self._selected_volk} – Talent wählen"
        
        self._content_box.add_widget(MDLabel(
            text="Keine freien Talente verfügbar.",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(48),
        ))
        self._add_back_button()

    def _on_talent_checkbox_clicked(self, talent_typ, talent_name, checkbox, checkboxes, selected_container):
        """Handler für Talent-Checkbox mit Debounce (Radio-Style)"""
        now = time.monotonic()
        if hasattr(self, '_last_talent_click') and (now - self._last_talent_click) < 0.5:
            return
        self._last_talent_click = now

        Logger.debug(f"Talent-Checkbox geklickt: {talent_name}")
        selected_container[0] = talent_name
        
        for name, cb in checkboxes.items():
            cb.active = (name == talent_name)

    def _on_talent_chosen(self, talent_typ, talent_name):
        """Talent aus der Liste gewählt"""
        Logger.debug(f"Talent bestätigt: {talent_name} (typ: {talent_typ})")
        extras = {}
        if talent_typ == 'halbelf_talent':
            extras = {'halbelf_talent': talent_name}
        elif talent_typ == 'mensch_talent':
            extras = {'mensch_talent': talent_name}
        elif talent_typ == 'freies_talent':
            extras = {'freies_talent': talent_name}

        self._apply_choice(self._selected_volk, extras)

    def _show_talent_info(self, talent_name):
        """Zeigt die Beschreibung eines Talents in einem Info-Dialog an."""
        talent = self._charakter.talente.get(talent_name) if hasattr(self._charakter, 'talente') else None
        beschreibung = getattr(talent, 'beschreibung', '') if talent else ''

        if not beschreibung:
            beschreibung = "Keine Beschreibung verfügbar."

        text_width = min(dp(400), Window.width * 0.85 - dp(60))

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )

        desc_label = MDLabel(
            text=beschreibung,
            size_hint_y=None,
            theme_text_color="Secondary",
            halign="left",
            valign="top",
            text_size=(text_width, None),
            markup=True
        )
        desc_label.bind(texture_size=desc_label.setter('size'))
        content.add_widget(desc_label)

        max_content_height = min(dp(400), Window.height * 0.6)
        scroll = MDScrollView(
            size_hint_y=None,
            height=max_content_height,
            do_scroll_x=False,
        )
        scroll.add_widget(content)

        info_dialog = MDDialog(
            MDDialogHeadlineText(text=str(talent_name)),
            MDDialogContentContainer(
                scroll,
                orientation="vertical",
                padding=dp(0),
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Schließen"),
                    style="text",
                    on_release=lambda x: info_dialog.dismiss(),
                ),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=True,
        )
        info_dialog.open()

    # ==================== Hilfsfunktionen ====================

    def _show_chip_selection(self, label_text, items, on_select):
        """Zeigt eine Chip-basierte Auswahl inline"""
        self._content_box.add_widget(MDLabel(
            text=label_text,
            bold=True,
            adaptive_height=True,
            size_hint_y=None,
        ))

        chips_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
        )
        chips_box.bind(minimum_height=chips_box.setter("height"))

        for item in sorted(items):
            if not item or not str(item).strip():
                continue
            chip = MDChip(
                MDChipText(text=str(item)),
                type="filter",
                size_hint_y=None,
                height=dp(40),
                on_release=lambda x, i=item: on_select(i),
            )
            chips_box.add_widget(chip)

        self._content_box.add_widget(chips_box)

    def _create_option_card(self, icon, title, description, on_click, color):
        """Erstellt eine klickbare Options-Card"""
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

    def _add_back_button(self):
        """Fügt einen Zurück-Button am Ende hinzu"""
        back_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            padding=(0, dp(8), 0, 0),
        )
        back_box.add_widget(MDBoxLayout(size_hint_x=1))

        back_btn = MDButton(
            style="outlined",
            on_release=lambda x: self._handle_back(),
        )
        back_btn.add_widget(MDButtonIcon(icon="arrow-left"))
        back_btn.add_widget(MDButtonText(text="Zurück zur Auswahl"))
        back_box.add_widget(back_btn)

        back_box.add_widget(MDBoxLayout(size_hint_x=1))
        self._content_box.add_widget(back_box)

    def _apply_choice(self, volk_name, zusatzelemente):
        """Wendet die Auswahl an und schließt das Overlay"""
        callback = self.on_volk_chosen

        self.close()

        # Callback verzögert aufrufen, damit die Animation abgeschlossen ist
        if callback:
            Clock.schedule_once(
                lambda dt: callback(volk_name, zusatzelemente), 0.25
            )
