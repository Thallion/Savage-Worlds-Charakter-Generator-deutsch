# views/voelker_view_mensch.py
"""
Menschen-Vielseitig-Sonderfall der Völker-View: freies Talent ODER
Fertigkeitspunkte.
Mixin von VoelkerWidget (views/voelker_view.py) — nur Methoden, kein eigener State.
"""

import logging

from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu

from functions.volk_funktionen import (
    get_freie_talente,
    waehle_mensch_talent,
    waehle_mensch_fertigkeitspunkte,
    NO_TALENT_AVAILABLE_TEXT,
)

from utils.platform_utils import is_mobile_layout
_mobile = is_mobile_layout()

Logger = logging.getLogger(__name__)


class MenschenVielseitigMixin:

    def _create_menschen_vielseitig_section(self):
        """
        Erstellt spezielle Menschen-Vielseitig ENTWEDER/ODER Sektion.
        Mensch kann ENTWEDER freies Talent ODER +2 Fertigkeitspunkte wählen.
        """
        try:
            from functions.volk_funktionen import (
                _get_menschen_freies_talent, _get_mensch_fertigkeitspunkte_gewaehlt
            )

            charakter = self.controller.charakter

            # Aktuelle Auswahl prüfen
            current_wahl = self.voelker_auswahlen.get(self.selected_volk_name, {}).get('vielseitig_wahl', None)
            hat_talent = current_wahl and current_wahl.startswith('Talent: ')
            hat_fertigkeitspunkte = current_wahl == '+2 Fertigkeitspunkte'

            # Kompaktere Werte für Mobile
            _pad = dp(10) if _mobile else dp(14)
            _spacing = dp(6) if _mobile else dp(10)
            _btn_spacing = dp(10) if _mobile else dp(20)
            _btn_height = dp(40) if _mobile else dp(48)
            _row_height = dp(44) if _mobile else dp(55)
            _title_height = dp(30) if _mobile else dp(40)

            # Hauptcontainer
            section_card = MDCard(
                size_hint_x=1,
                size_hint_y=None,
                padding=_pad,
                elevation=3,
                radius=[12],
                md_bg_color=self.theme_cls.surfaceContainerHighColor,
                style="elevated",
            )
            section_card.bind(minimum_height=section_card.setter('height'))

            section_content = MDBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                spacing=_spacing
            )
            section_content.bind(minimum_height=section_content.setter('height'))

            # Titel
            titel_label = MDLabel(
                text="Vielseitig (ENTWEDER freies Talent ODER +2 Fertigkeitspunkte):",
                font_style="Body",
                theme_text_color="Primary",
                size_hint_y=None,
                height=_title_height,
                halign='left',
                valign='top',
                bold=True
            )
            titel_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
            titel_label.bind(text_size=lambda instance, size: setattr(instance, 'height', max(_title_height, instance.texture_size[1] + dp(6))))

            # Zwei Buttons
            buttons_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=_row_height,
                spacing=_btn_spacing
            )

            # Button 1: Freies Talent
            talent_button = MDButton(
                style="filled" if hat_talent else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=_btn_height,
                on_release=lambda x: self._mensch_vielseitig_waehle_talent()
            )
            talent_button.add_widget(MDButtonText(text="Freies Talent"))

            # Button 2: +2 Fertigkeitspunkte
            fp_button = MDButton(
                style="filled" if hat_fertigkeitspunkte else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=_btn_height,
                on_release=lambda x: self._mensch_vielseitig_waehle_fertigkeitspunkte()
            )
            fp_button.add_widget(MDButtonText(text="+2 Fertigkeitspunkte"))

            buttons_row.add_widget(talent_button)
            buttons_row.add_widget(fp_button)

            section_content.add_widget(titel_label)
            section_content.add_widget(buttons_row)

            # Aktuelle Auswahl anzeigen
            if current_wahl:
                auswahl_label = MDLabel(
                    text=f"Gewählt: {current_wahl}",
                    font_style="Body",
                    theme_text_color="Primary",
                    size_hint_y=None,
                    height=dp(24) if _mobile else dp(30),
                    halign='left',
                    valign='center',
                    bold=True
                )
                section_content.add_widget(auswahl_label)

            section_card.add_widget(section_content)

            Logger.debug(f"Menschen Vielseitig Sektion erstellt (Auswahl: {current_wahl})")
            return section_card

        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der Menschen-Vielseitig Sektion: {e}")
            return MDCard(size_hint_x=1, size_hint_y=None, height=dp(50))

    def _mensch_vielseitig_waehle_talent(self):
        """Menschen-Vielseitig: Wählt freies Talent (ENTWEDER-Option)."""
        try:
            Logger.debug("Mensch Vielseitig: Freies Talent-Option ausgewählt")

            charakter = self.controller.charakter
            freie_talente = get_freie_talente(charakter)

            if not freie_talente or freie_talente == [NO_TALENT_AVAILABLE_TEXT]:
                Logger.warning("Keine freien Talente verfügbar")
                return

            # Dropdown-Menü für Talent-Auswahl erstellen
            menu_items = []
            for talent in freie_talente:
                menu_items.append({
                    "text": talent,
                    "on_release": lambda t=talent: self._mensch_vielseitig_talent_gewaehlt(t)
                })

            self._talent_menu = MDDropdownMenu(
                caller=self.ids.zusatzelemente_container,
                items=menu_items,
                width_mult=4,
                max_height=dp(300)
            )
            self._talent_menu.open()

        except Exception as e:
            Logger.error(f"Fehler bei Mensch-Vielseitig-Talent-Auswahl: {e}")

    def _mensch_vielseitig_talent_gewaehlt(self, talent_name):
        """Callback wenn Talent aus Dropdown gewählt wird."""
        try:
            if hasattr(self, '_talent_menu'):
                self._talent_menu.dismiss()

            charakter = self.controller.charakter
            success = waehle_mensch_talent(charakter, self.selected_volk_name, talent_name)

            if success:
                # Auswahl im Dictionary speichern
                if self.selected_volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[self.selected_volk_name] = {}
                self.voelker_auswahlen[self.selected_volk_name]['vielseitig_wahl'] = f"Talent: {talent_name}"

                # UI aktualisieren
                self._update_zusatzelemente()

                # Controller informieren
                if hasattr(self.controller, 'dispatch'):
                    self.controller.dispatch('on_charakter_updated')

        except Exception as e:
            Logger.error(f"Fehler bei Mensch-Vielseitig-Talent-Callback: {e}")

    def _mensch_vielseitig_waehle_fertigkeitspunkte(self):
        """Menschen-Vielseitig: Wählt +2 Fertigkeitspunkte (ODER-Option)."""
        try:
            Logger.debug("Mensch Vielseitig: +2 Fertigkeitspunkte-Option ausgewählt")

            charakter = self.controller.charakter
            success = waehle_mensch_fertigkeitspunkte(charakter, self.selected_volk_name)

            if success:
                # Auswahl im Dictionary speichern
                if self.selected_volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[self.selected_volk_name] = {}
                self.voelker_auswahlen[self.selected_volk_name]['vielseitig_wahl'] = '+2 Fertigkeitspunkte'

                # UI aktualisieren
                self._update_zusatzelemente()

                # Controller informieren
                if hasattr(self.controller, 'dispatch'):
                    self.controller.dispatch('on_charakter_updated')

        except Exception as e:
            Logger.error(f"Fehler bei Mensch-Vielseitig-Fertigkeitspunkte-Callback: {e}")
