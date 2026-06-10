# views/voelker_view_halbelf.py
"""
Halbelf-Sonderfall der Völker-View: Entweder/Oder-Auswahl (freies Talent
ODER freies Attribut).
Mixin von VoelkerWidget (views/voelker_view.py) — nur Methoden, kein eigener State.
"""

import logging

from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

from functions.volk_funktionen import (
    get_freie_talente,
    waehle_halbelf_talent,
    waehle_halbelf_attribut,
    NO_TALENT_AVAILABLE_TEXT,
)

from utils.platform_utils import is_mobile_layout
_mobile = is_mobile_layout()

Logger = logging.getLogger(__name__)


class HalbelfMixin:

    # === NEUE METHODEN FÜR ERWEITERTE VÖLKER-WAHLMÖGLICHKEITEN ===

    def _create_halbelf_entweder_oder_section(self):
        """
        NEUE: Erstellt spezielle Halbelf ENTWEDER/ODER Sektion.
        Halbelf kann ENTWEDER freies Talent ODER Geschicklichkeit +2 wählen.
        """
        try:
            # Aktuelle Auswahl prüfen
            current_wahl = self.voelker_auswahlen.get(self.selected_volk_name, {}).get('halbelf_wahl', None)
            hat_talent = current_wahl and current_wahl.startswith('Talent: ')
            hat_attribut = current_wahl == 'Geschicklichkeit W6'

            # Kompaktere Werte für Mobile
            _pad = dp(10) if _mobile else dp(14)
            _spacing = dp(6) if _mobile else dp(10)
            _btn_spacing = dp(10) if _mobile else dp(20)
            _btn_height = dp(40) if _mobile else dp(48)
            _row_height = dp(44) if _mobile else dp(55)
            _title_height = dp(30) if _mobile else dp(40)

            # Hauptcontainer für die Sektion
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

            # Titel der Sektion mit reduzierter Schriftgröße
            titel_label = MDLabel(
                text="Erbe (ENTWEDER freies Talent ODER Geschicklichkeit W4 -> W6):",
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

            # Zwei Buttons für die Auswahl
            buttons_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=_row_height,
                spacing=_btn_spacing
            )

            # Button 1: Freies Talent - filled wenn ausgewählt
            talent_button = MDButton(
                style="filled" if hat_talent else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=_btn_height,
                on_release=lambda x: self._halbelf_waehle_talent()
            )
            talent_button.add_widget(MDButtonText(text="Freies Talent"))

            # Button 2: Geschicklichkeit +2 - filled wenn ausgewählt
            attribut_button = MDButton(
                style="filled" if hat_attribut else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=_btn_height,
                on_release=lambda x: self._halbelf_waehle_attribut()
            )
            attribut_button.add_widget(MDButtonText(text="Geschicklichkeit W6"))

            buttons_row.add_widget(talent_button)
            buttons_row.add_widget(attribut_button)

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

            Logger.debug(f"Halbelf ENTWEDER/ODER Sektion erstellt (Auswahl: {current_wahl})")
            return section_card

        except Exception as e:
            Logger.error(f"Fehler beim Erstellen der Halbelf ENTWEDER/ODER Sektion: {e}")
            # Fallback: Leere Card zurückgeben
            return MDCard(size_hint_x=1, size_hint_y=None, height=dp(50))

    def _halbelf_waehle_talent(self):
        """NEUE: Halbelf wählt freies Talent (ENTWEDER-Option)."""
        try:
            Logger.debug("Halbelf: Freies Talent-Option ausgewählt")

            charakter = self.controller.charakter
            freie_talente = get_freie_talente(charakter)

            if not freie_talente or freie_talente == [NO_TALENT_AVAILABLE_TEXT]:
                Logger.warning("Keine freien Talente für Halbelf verfügbar")
                return

            # Zeige Talent-Auswahl Dialog mit Filter-Button
            self._show_search_dialog(
                freie_talente,
                lambda talent: self._halbelf_talent_selected(talent),
                None,
                get_options_func=lambda: get_freie_talente(charakter),
                get_alle_items_func=lambda: get_freie_talente(charakter, nur_verfuegbare=False)
            )
            
        except Exception as e:
            Logger.error(f"Fehler bei Halbelf Talent-Wahl: {e}", exc_info=True)

    def _halbelf_waehle_attribut(self):
        """NEUE: Halbelf wählt Geschicklichkeit +2 (ODER-Option)."""
        try:
            Logger.debug("Halbelf: Geschicklichkeit +2 Option ausgewählt")
            
            charakter = self.controller.charakter
            success = waehle_halbelf_attribut(charakter, self.selected_volk_name)
            
            if success:
                # UI-lokale Auswahl speichern
                if self.selected_volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[self.selected_volk_name] = {}
                self.voelker_auswahlen[self.selected_volk_name]['halbelf_wahl'] = 'Geschicklichkeit W6'
                
                Logger.info(f"Halbelf '{self.selected_volk_name}' hat Geschicklichkeit +2 gewählt")
                
                # UI aktualisieren - zeige Bestätigung statt erneutem Dropdown
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            else:
                Logger.error("Fehler beim Anwenden des Geschicklichkeits-Bonus für Halbelf")
            
        except Exception as e:
            Logger.error(f"Fehler bei Halbelf Attribut-Wahl: {e}", exc_info=True)

    def _halbelf_talent_selected(self, talent_name):
        """NEUE: Callback für Halbelf Talent-Auswahl."""
        try:
            Logger.debug(f"Halbelf Talent ausgewählt: {talent_name}")
            
            charakter = self.controller.charakter
            success = waehle_halbelf_talent(charakter, self.selected_volk_name, talent_name)
            
            if success:
                # UI-lokale Auswahl speichern
                if self.selected_volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[self.selected_volk_name] = {}
                self.voelker_auswahlen[self.selected_volk_name]['halbelf_wahl'] = f'Talent: {talent_name}'
                
                Logger.info(f"Halbelf '{self.selected_volk_name}' hat Talent '{talent_name}' gewählt")
                
                # UI aktualisieren
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            else:
                Logger.error(f"Fehler beim Auswählen des Talents '{talent_name}' für Halbelf")
            
        except Exception as e:
            Logger.error(f"Fehler bei Halbelf Talent-Auswahl: {e}", exc_info=True)