# views/voelker_view_zusatzelemente.py
"""
Zusatzelemente-Subsystem der Völker-View: Inline-Chip-Auswahl, Edit-Dialoge
für Attribute/Fertigkeiten/Magieaffin, Such-Dialog.
Mixin von VoelkerWidget (views/voelker_view.py) — nur Methoden, kein eigener State.
"""

import logging

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList
from kivymd.uix.scrollview import MDScrollView

from functions.volk_funktionen import (
    get_volk_attribut_optionen,
    get_verfuegbare_fertigkeiten,
    waehle_freies_talent,
    waehle_freies_attribut,
    waehle_freie_fertigkeit,
    NO_TALENT_AVAILABLE_TEXT,
    NO_ATTRIBUT_AVAILABLE_TEXT,
    NO_FERTIGKEIT_AVAILABLE_TEXT,
)

from utils.platform_utils import is_mobile_layout
_mobile = is_mobile_layout()

Logger = logging.getLogger(__name__)


class ZusatzelementeMixin:

    def _update_zusatzelemente(self):
        """Zeigt die ausgewählten Zusatzelemente an (aus voelker_auswahlen)."""
        container = self.ids.get('zusatzelemente_container')
        if not container:
            return
        
        container.clear_widgets()
        
        if not self.selected_volk_name:
            return
        
        wahl = self.voelker_auswahlen.get(self.selected_volk_name, {})

        # Collect all selections for this volk.
        # Multi-Slot-Keys liefern eine Zeile pro Listeneintrag mit slot_index;
        # Unique-Keys (halbelf_wahl, vielseitig_wahl, magieaffin) liefern eine
        # Zeile mit slot_index=None.
        selections = []  # Tupel: (label, value, slot_index)

        def _expand(label, value):
            if isinstance(value, list):
                for i, v in enumerate(value):
                    if v:
                        selections.append((label, v, i))
            elif value:
                # Legacy-Skalar in Slot 0 abbilden, damit Edit-Logik einheitlich greift
                selections.append((label, value, 0))

        # Talent (Multi-Slot)
        _expand('Freies Talent', wahl.get('talent'))

        # Halbelf Wahl (Unique)
        if wahl.get('halbelf_wahl'):
            selections.append(('Halbelf Wahl', wahl['halbelf_wahl'], None))

        # Vielseitig Wahl (Mensch, Unique)
        if wahl.get('vielseitig_wahl'):
            selections.append(('Vielseitig Wahl', wahl['vielseitig_wahl'], None))

        # Attribut (Multi-Slot)
        _expand('Freies Attribut', wahl.get('attribut'))

        # Attributs Schwäche (Multi-Slot)
        _expand('Attributs Schwäche', wahl.get('attribut_malus'))

        # Fertigkeit (Multi-Slot)
        _expand('Freie Fertigkeit', wahl.get('fertigkeit'))

        # Magieaffin (zeigt das gewählte AH-Talent + die zugeordnete Arkane Fertigkeit)
        from functions.volk_funktionen import (
            get_aktuelle_magieaffin_fertigkeit,
            get_aktuelles_magieaffin_ah,
            hat_volk_magieaffin,
        )
        if hat_volk_magieaffin(self.controller.charakter, self.selected_volk_name):
            magieaffin_ah = get_aktuelles_magieaffin_ah(self.controller.charakter, self.selected_volk_name)
            magieaffin_fertigkeit = get_aktuelle_magieaffin_fertigkeit(self.controller.charakter, self.selected_volk_name)
            if magieaffin_ah:
                anzeige = f"{magieaffin_ah} ({magieaffin_fertigkeit})" if magieaffin_fertigkeit else magieaffin_ah
                selections.append(('Magieaffin', anzeige, None))
            elif magieaffin_fertigkeit:
                # Backward-Compat: Alte Auswahl ohne AH-Talent
                selections.append(('Magieaffin', magieaffin_fertigkeit, None))
            else:
                selections.append(('Magieaffin', 'Auswählen...', None))
        
        if not selections:
            return
        
        # Create display for selections
        from kivymd.uix.chip import MDChip, MDChipText
        from kivymd.uix.button import MDIconButton
        
        # Wenn ein Label mehrfach erscheint (z.B. zwei "Freies Talent"), Index in der Anzeige nummerieren
        from collections import Counter
        label_counts = Counter(l for l, _, _ in selections)

        for label, value, slot_index in selections:
            row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36), spacing=dp(8))
            display_label = label
            if label_counts[label] > 1 and slot_index is not None:
                display_label = f"{label} {slot_index + 1}"
            label_widget = MDLabel(
                text=f"{display_label}:",
                size_hint_x=None,
                width=dp(120),
                theme_text_color="Secondary",
                halign='left',
            )
            row.add_widget(label_widget)

            # Hintergrundfarbe sicherstellen (nie None)
            if hasattr(self, 'theme_cls') and self.theme_cls:
                bg_color = self.theme_cls.primaryContainerColor
            else:
                bg_color = [0.7, 0.8, 1.0, 1.0]  # hellblau als Fallback

            chip = MDChip(
                MDChipText(text=value),
                type="filter",
                active=True,
                md_bg_color=bg_color,
            )
            row.add_widget(chip)

            # Edit-Button für Talent-Auswahl (nur bei Talenten) und Attribut
            if label in ['Freies Talent', 'Halbelf Wahl', 'Vielseitig Wahl', 'Freies Attribut', 'Attributs Schwäche', 'Freie Fertigkeit', 'Magieaffin']:
                # Elementnamen extrahieren
                element_name = value
                if label == 'Halbelf Wahl' and value.startswith('Talent: '):
                    element_name = value.replace('Talent: ', '')
                elif label == 'Vielseitig Wahl' and value.startswith('Talent: '):
                    element_name = value.replace('Talent: ', '')
                # Edit-Button hinzufügen
                edit_btn = MDIconButton(
                    icon="pencil",
                    size_hint=(None, None),
                    size=(dp(36), dp(36)),
                    pos_hint={"center_y": 0.5}
                )
                btn = edit_btn
                idx = slot_index  # für Lambda-Capture
                if label == 'Freies Attribut':
                    edit_btn.bind(on_release=lambda x, btn=btn, attr=element_name, i=idx: self._on_edit_attribut(attr, slot_index=i))
                elif label == 'Attributs Schwäche':
                    edit_btn.bind(on_release=lambda x, btn=btn, attr=element_name, i=idx: self._on_edit_attribut_malus(attr, slot_index=i))
                elif label == 'Freie Fertigkeit':
                    edit_btn.bind(on_release=lambda x, btn=btn, fert=element_name, i=idx: self._on_edit_fertigkeit(fert, slot_index=i))
                elif label == 'Magieaffin':
                    edit_btn.bind(on_release=lambda x, btn=btn: self._on_edit_magieaffin())
                else:
                    edit_btn.bind(on_release=lambda x, btn=btn, l=label, tn=element_name, i=idx: self._on_edit_zusatzelement(l, tn, slot_index=i))
                row.add_widget(edit_btn)
            
            container.add_widget(row)

    def _on_edit_zusatzelement(self, label, talent_name, slot_index=None):
        """Öffnet das Talent-Auswahl-Overlay zum Bearbeiten eines bereits gewählten Talents.
        slot_index gibt bei Multi-Slot-Talenten an, welcher Slot bearbeitet wird."""
        self._current_edit_slot_index = slot_index
        if not hasattr(self, '_voelker_overlay'):
            Logger.error("VoelkerOverlay nicht initialisiert")
            return
        
        # Talenttyp bestimmen
        talent_typ = None
        if label == 'Freies Talent':
            talent_typ = 'freies_talent'
        elif label == 'Halbelf Wahl':
            talent_typ = 'halbelf_talent'
        elif label == 'Vielseitig Wahl':
            talent_typ = 'mensch_talent'
        else:
            Logger.warning(f"Unbekannter Label für Edit: {label}")
            return
        
        # Overlay für aktuelles Volk vorbereiten
        volk_name = self.selected_volk_name
        if not volk_name:
            Logger.warning("Kein Volk ausgewählt")
            return
        
        self._voelker_overlay._charakter = self.controller.charakter
        self._voelker_overlay._selected_volk = volk_name
        # Overlay-Zustand für Edit-Modus vorbereiten: _selected_extras zurücksetzen und
        # _zusatzelemente_info auf nur das bearbeitete Element begrenzen, damit
        # _all_extras_selected() nach einer Auswahl True zurückgibt.
        self._voelker_overlay._selected_extras = {}
        if talent_typ == 'freies_talent':
            self._voelker_overlay._zusatzelemente_info = {'freie_talente': True}
        elif talent_typ == 'halbelf_talent':
            self._voelker_overlay._zusatzelemente_info = {'halbelf_entweder_oder': True}
        elif talent_typ == 'mensch_talent':
            self._voelker_overlay._zusatzelemente_info = {'menschen_vielseitig': True}
        self._voelker_overlay.on_volk_chosen = self._on_overlay_volk_chosen
        # Talentauswahl direkt öffnen
        self._voelker_overlay._show_talent_selection(talent_typ)

    def _on_edit_attribut(self, attribut_name, slot_index=None):
        """Öffnet einen Dialog zum Bearbeiten des ausgewählten freien Attributs.
        slot_index gibt bei Multi-Slot-Attributen an, welcher Slot bearbeitet wird."""
        self._current_edit_slot_index = slot_index
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.chip import MDChip, MDChipText
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDButton, MDButtonText
        from kivy.metrics import dp
        
        volk_name = self.selected_volk_name
        if not volk_name:
            Logger.warning("Kein Volk ausgewählt")
            return
        
        charakter = self.controller.charakter
        
        # Verfügbare Attribut-Optionen abrufen
        from functions.volk_funktionen import get_volk_attribut_optionen, NO_ATTRIBUT_AVAILABLE_TEXT
        attribut_optionen = get_volk_attribut_optionen(charakter, volk_name)
        
        if not attribut_optionen or attribut_optionen == [NO_ATTRIBUT_AVAILABLE_TEXT]:
            Logger.warning(f"Keine Attribut-Optionen verfügbar für Volk '{volk_name}'")
            return
        
        # Dialog-Content mit Chips
        # Höhe explizit berechnen (MDDialog Fixed Height: size_hint_y=None braucht feste Höhe)
        scroll_height = min(dp(350), len(attribut_optionen) * dp(52))
        content_height = dp(86) + scroll_height  # padding(40) + label(34) + spacing(12) + scroll
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(20),
            size_hint_y=None,
            height=content_height,
        )

        # Info-Label
        info_label = MDLabel(
            text="Wähle ein neues Attribut:",
            bold=True,
            size_hint_y=None,
            height=dp(34),
        )
        content.add_widget(info_label)

        # Chips-Box
        chips_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        chips_box.bind(minimum_height=chips_box.setter('height'))
        
        # Bereits in anderen Slots gewählte Attribute ausblenden, damit der User
        # in diesem Slot kein Duplikat wählt. Den Wert des aktuellen Slots erlauben.
        bereits_gewaehlt = set()
        eintrag_attr = self.voelker_auswahlen.get(volk_name, {}).get('attribut')
        if isinstance(eintrag_attr, list):
            cur_idx = getattr(self, '_current_edit_slot_index', None) or 0
            for i, v in enumerate(eintrag_attr):
                if v and i != cur_idx:
                    bereits_gewaehlt.add(v)

        for attr in sorted(attribut_optionen):
            if attr == NO_ATTRIBUT_AVAILABLE_TEXT:
                continue
            if attr in bereits_gewaehlt:
                continue

            # Chip mit Hervorhebung des aktuell ausgewählten Attributs
            chip_kwargs = {
                'type': "filter",
                'size_hint_y': None,
                'height': dp(40),
                'on_release': lambda x, a=attr: self._on_attribut_chosen(a),
            }
            # Hintergrundfarbe setzen (nie None)
            if hasattr(self, 'theme_cls') and self.theme_cls:
                if attr == attribut_name:
                    chip_kwargs['md_bg_color'] = self.theme_cls.primaryContainerColor
                else:
                    chip_kwargs['md_bg_color'] = self.theme_cls.surfaceColor
            else:
                # Fallback: hellgrau für nicht-ausgewählt, blau für ausgewählt
                if attr == attribut_name:
                    chip_kwargs['md_bg_color'] = [0.7, 0.8, 1.0, 1.0]  # hellblau
                else:
                    chip_kwargs['md_bg_color'] = [0.95, 0.95, 0.95, 1.0]  # hellgrau
            
            chip = MDChip(
                MDChipText(text=attr),
                **chip_kwargs
            )
            chips_box.add_widget(chip)
        
        # ScrollView für viele Optionen
        from kivymd.uix.scrollview import MDScrollView
        scroll = MDScrollView(
            size_hint_y=None,
            height=scroll_height,
            do_scroll_x=False,
        )
        scroll.add_widget(chips_box)
        content.add_widget(scroll)
        
        # Dialog-Buttons
        button_container = MDDialogButtonContainer(
            MDButton(
                MDButtonText(text="Abbrechen"),
                style="text",
                on_release=lambda x: dialog.dismiss(),
            ),
            spacing="8dp",
        )
        
        # Dialog erstellen
        dialog = MDDialog(
            MDDialogHeadlineText(text=f"Attribut für {volk_name} ändern"),
            MDDialogContentContainer(content, orientation="vertical"),
            button_container,
            size_hint=(0.85, None),
        )
        
        self._attribut_dialog = dialog
        dialog.open()
    
    def _on_attribut_chosen(self, attribut_name):
        """Wird aufgerufen wenn ein neues Attribut im Bearbeitungs-Dialog ausgewählt wird.
        Berücksichtigt _current_edit_slot_index für Multi-Slot."""
        from kivy.clock import Clock
        from functions.volk_funktionen import waehle_freies_attribut

        volk_name = self.selected_volk_name
        if not volk_name:
            return

        charakter = self.controller.charakter
        slot_index = getattr(self, '_current_edit_slot_index', None) or 0

        Logger.info(f"[DEBUG] Ändere freies Attribut für '{volk_name}' Slot {slot_index} zu '{attribut_name}'")

        # Alten Wert dieses Slots ermitteln und ggf. zurückrollen.
        eintrag = self.voelker_auswahlen.get(volk_name, {})
        alt = eintrag.get('attribut')
        if isinstance(alt, list):
            alt_wert = alt[slot_index] if 0 <= slot_index < len(alt) else None
        else:
            alt_wert = alt
        if alt_wert and alt_wert != attribut_name:
            # Für Nicht-Mensch-Völker manuell die alte Erhöhung zurücknehmen
            # (waehle_freies_attribut macht das nur für Menschen).
            if volk_name.lower() not in ["mensch", "menschen", "human"]:
                if hasattr(charakter, 'attribute') and alt_wert in charakter.attribute:
                    charakter.attribute[alt_wert].wert = max(4, charakter.attribute[alt_wert].wert - 1)

        success = waehle_freies_attribut(charakter, volk_name, attribut_name)

        if success:
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            aktuell = self.voelker_auswahlen[volk_name].get('attribut')
            if isinstance(aktuell, list):
                # Listen-Update an gewünschtem Slot
                if 0 <= slot_index < len(aktuell):
                    aktuell[slot_index] = attribut_name
                else:
                    aktuell.append(attribut_name)
            else:
                self.voelker_auswahlen[volk_name]['attribut'] = [attribut_name]

            if hasattr(self, '_attribut_dialog') and self._attribut_dialog:
                self._attribut_dialog.dismiss()

            Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)

            Logger.info(f"Freies Attribut für '{volk_name}' Slot {slot_index} erfolgreich geändert zu '{attribut_name}'")
        else:
            Logger.error(f"Fehler beim Ändern des Attributs für '{volk_name}'")

    def _on_edit_attribut_malus(self, attribut_name, slot_index=None):
        """Öffnet einen Dialog zum Bearbeiten der Attributs-Schwäche (Malus).
        slot_index gibt bei Multi-Slot-Schwächen an, welcher Slot bearbeitet wird."""
        self._current_edit_slot_index = slot_index
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.chip import MDChip, MDChipText
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDButton, MDButtonText
        from kivy.metrics import dp

        volk_name = self.selected_volk_name
        if not volk_name:
            Logger.warning("Kein Volk ausgewählt")
            return

        charakter = self.controller.charakter

        # Verfügbare Malus-Attribut-Optionen abrufen (nur W4-Basis-Attribute)
        from functions.volk_funktionen import get_staerkbare_attribute, NO_ATTRIBUT_AVAILABLE_TEXT
        attribut_optionen = get_staerkbare_attribute(charakter)

        if not attribut_optionen or attribut_optionen == [NO_ATTRIBUT_AVAILABLE_TEXT]:
            Logger.warning(f"Keine Attribut-Optionen für Schwäche verfügbar für Volk '{volk_name}'")
            return

        # Höhe explizit berechnen
        scroll_height = min(dp(350), len(attribut_optionen) * dp(52))
        content_height = dp(86) + scroll_height
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(20),
            size_hint_y=None,
            height=content_height,
        )

        info_label = MDLabel(
            text="Wähle ein neues zu schwächendes Attribut:",
            bold=True,
            size_hint_y=None,
            height=dp(34),
        )
        content.add_widget(info_label)

        chips_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        chips_box.bind(minimum_height=chips_box.setter('height'))

        # Bereits in anderen Schwäche-Slots gewählte Attribute ausblenden
        bereits_gewaehlt = set()
        eintrag_malus = self.voelker_auswahlen.get(volk_name, {}).get('attribut_malus')
        if isinstance(eintrag_malus, list):
            cur_idx = getattr(self, '_current_edit_slot_index', None) or 0
            for i, v in enumerate(eintrag_malus):
                if v and i != cur_idx:
                    bereits_gewaehlt.add(v)

        for attr in sorted(attribut_optionen):
            if attr == NO_ATTRIBUT_AVAILABLE_TEXT:
                continue
            if attr in bereits_gewaehlt:
                continue

            chip_kwargs = {
                'type': "filter",
                'size_hint_y': None,
                'height': dp(40),
                'on_release': lambda x, a=attr: self._on_attribut_malus_chosen(a),
            }
            if hasattr(self, 'theme_cls') and self.theme_cls:
                if attr == attribut_name:
                    chip_kwargs['md_bg_color'] = self.theme_cls.primaryContainerColor
                else:
                    chip_kwargs['md_bg_color'] = self.theme_cls.surfaceColor
            else:
                if attr == attribut_name:
                    chip_kwargs['md_bg_color'] = [0.7, 0.8, 1.0, 1.0]
                else:
                    chip_kwargs['md_bg_color'] = [0.95, 0.95, 0.95, 1.0]

            chip = MDChip(
                MDChipText(text=attr),
                **chip_kwargs
            )
            chips_box.add_widget(chip)

        from kivymd.uix.scrollview import MDScrollView
        scroll = MDScrollView(
            size_hint_y=None,
            height=scroll_height,
            do_scroll_x=False,
        )
        scroll.add_widget(chips_box)
        content.add_widget(scroll)

        button_container = MDDialogButtonContainer(
            MDButton(
                MDButtonText(text="Abbrechen"),
                style="text",
                on_release=lambda x: dialog.dismiss(),
            ),
            spacing="8dp",
        )

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"Attributs Schwäche für {volk_name} ändern"),
            MDDialogContentContainer(content, orientation="vertical"),
            button_container,
            size_hint=(0.85, None),
        )

        self._attribut_malus_dialog = dialog
        dialog.open()

    def _on_attribut_malus_chosen(self, attribut_name):
        """Wird aufgerufen, wenn ein neues Schwäche-Attribut ausgewählt wird.
        Berücksichtigt _current_edit_slot_index für Multi-Slot."""
        from kivy.clock import Clock
        from functions.volk_funktionen import waehle_freies_attribut_malus

        volk_name = self.selected_volk_name
        if not volk_name:
            return

        charakter = self.controller.charakter
        slot_index = getattr(self, '_current_edit_slot_index', None) or 0

        # Alten Wert dieses Slots ermitteln und Schwäche zurückrollen
        eintrag = self.voelker_auswahlen.get(volk_name, {})
        alt = eintrag.get('attribut_malus')
        if isinstance(alt, list):
            alte_schwaeche = alt[slot_index] if 0 <= slot_index < len(alt) else None
        else:
            alte_schwaeche = alt

        if alte_schwaeche and alte_schwaeche != attribut_name:
            try:
                if hasattr(charakter, 'attribute') and alte_schwaeche in charakter.attribute:
                    altes_attribut = charakter.attribute[alte_schwaeche]
                    altes_attribut.wuerfel.modifier = 0
                    if hasattr(charakter, 'berechne_abgeleitete_werte'):
                        charakter.berechne_abgeleitete_werte()
            except Exception as e:
                Logger.warning(f"Konnte alte Attributs-Schwäche '{alte_schwaeche}' nicht zurücksetzen: {e}")

        Logger.info(f"[DEBUG] Ändere Attributs-Schwäche für '{volk_name}' Slot {slot_index} zu '{attribut_name}'")
        success = waehle_freies_attribut_malus(charakter, volk_name, attribut_name)

        if success:
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            aktuell = self.voelker_auswahlen[volk_name].get('attribut_malus')
            if isinstance(aktuell, list):
                if 0 <= slot_index < len(aktuell):
                    aktuell[slot_index] = attribut_name
                else:
                    aktuell.append(attribut_name)
            else:
                self.voelker_auswahlen[volk_name]['attribut_malus'] = [attribut_name]

            if hasattr(self, '_attribut_malus_dialog') and self._attribut_malus_dialog:
                self._attribut_malus_dialog.dismiss()

            Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)

            Logger.info(f"Attributs-Schwäche für '{volk_name}' Slot {slot_index} erfolgreich geändert zu '{attribut_name}'")
        else:
            Logger.error(f"Fehler beim Ändern der Attributs-Schwäche für '{volk_name}'")

    def _on_edit_fertigkeit(self, fertigkeit_name, slot_index=None):
        """Öffnet einen Dialog zum Bearbeiten der ausgewählten freien Fertigkeit.
        slot_index gibt bei Multi-Slot-Fertigkeiten an, welcher Slot bearbeitet wird."""
        self._current_edit_slot_index = slot_index
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.chip import MDChip, MDChipText
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.scrollview import MDScrollView
        from kivy.metrics import dp

        volk_name = self.selected_volk_name
        if not volk_name:
            Logger.warning("Kein Volk ausgewählt")
            return

        charakter = self.controller.charakter

        # Verfügbare Fertigkeiten holen — gleiche Quelle wie das Volker-Overlay
        # bei der initialen Auswahl, damit Edit und Erstauswahl konsistent sind.
        from functions.volk_funktionen import get_verfuegbare_fertigkeiten, NO_FERTIGKEIT_AVAILABLE_TEXT
        fertigkeit_optionen = get_verfuegbare_fertigkeiten(charakter, nur_verstand=True)

        if not fertigkeit_optionen or fertigkeit_optionen == [NO_FERTIGKEIT_AVAILABLE_TEXT]:
            Logger.warning(f"Keine Fertigkeit-Optionen verfügbar für Volk '{volk_name}'")
            return

        # Höhe explizit berechnen (MDDialog Fixed Height)
        scroll_height = min(dp(350), len(fertigkeit_optionen) * dp(52))
        content_height = dp(86) + scroll_height
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(20),
            size_hint_y=None,
            height=content_height,
        )

        info_label = MDLabel(
            text="Wähle eine neue Fertigkeit:",
            bold=True,
            size_hint_y=None,
            height=dp(34),
        )
        content.add_widget(info_label)

        chips_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        chips_box.bind(minimum_height=chips_box.setter('height'))

        # Bereits in anderen Slots gewählte Fertigkeiten ausblenden, damit der User
        # in diesem Slot kein Duplikat wählt. Den Wert des aktuellen Slots erlauben.
        bereits_gewaehlt = set()
        eintrag_fert = self.voelker_auswahlen.get(volk_name, {}).get('fertigkeit')
        if isinstance(eintrag_fert, list):
            cur_idx = getattr(self, '_current_edit_slot_index', None) or 0
            for i, v in enumerate(eintrag_fert):
                if v and i != cur_idx:
                    bereits_gewaehlt.add(v)

        for fert in sorted(fertigkeit_optionen):
            if fert == NO_FERTIGKEIT_AVAILABLE_TEXT:
                continue
            if fert in bereits_gewaehlt:
                continue

            chip_kwargs = {
                'type': "filter",
                'size_hint_y': None,
                'height': dp(40),
                'on_release': lambda x, f=fert: self._on_fertigkeit_chosen(f),
            }
            if hasattr(self, 'theme_cls') and self.theme_cls:
                if fert == fertigkeit_name:
                    chip_kwargs['md_bg_color'] = self.theme_cls.primaryContainerColor
                else:
                    chip_kwargs['md_bg_color'] = self.theme_cls.surfaceColor
            else:
                if fert == fertigkeit_name:
                    chip_kwargs['md_bg_color'] = [0.7, 0.8, 1.0, 1.0]
                else:
                    chip_kwargs['md_bg_color'] = [0.95, 0.95, 0.95, 1.0]

            chip = MDChip(MDChipText(text=fert), **chip_kwargs)
            chips_box.add_widget(chip)

        scroll = MDScrollView(
            size_hint_y=None,
            height=scroll_height,
            do_scroll_x=False,
        )
        scroll.add_widget(chips_box)
        content.add_widget(scroll)

        button_container = MDDialogButtonContainer(
            MDButton(
                MDButtonText(text="Abbrechen"),
                style="text",
                on_release=lambda x: dialog.dismiss(),
            ),
            spacing="8dp",
        )

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"Fertigkeit für {volk_name} ändern"),
            MDDialogContentContainer(content, orientation="vertical"),
            button_container,
            size_hint=(0.85, None),
        )

        self._fertigkeit_dialog = dialog
        dialog.open()

    def _on_fertigkeit_chosen(self, fertigkeit_name):
        """Wird aufgerufen wenn eine neue Fertigkeit im Bearbeitungs-Dialog ausgewählt wird.
        Berücksichtigt _current_edit_slot_index für Multi-Slot."""
        from kivy.clock import Clock

        volk_name = self.selected_volk_name
        if not volk_name:
            return

        charakter = self.controller.charakter
        slot_index = getattr(self, '_current_edit_slot_index', None) or 0

        # Alten Wert dieses Slots ermitteln und Bonus zurückrollen.
        # waehle_freie_fertigkeit kennt keine Rückroll-Logik, deshalb hier von Hand:
        # Grundfertigkeit W6 → W4 oder Nicht-Grundfertigkeit W4+0 → W4-2.
        eintrag = self.voelker_auswahlen.get(volk_name, {})
        alt = eintrag.get('fertigkeit')
        if isinstance(alt, list):
            alte_fertigkeit = alt[slot_index] if 0 <= slot_index < len(alt) else None
        else:
            alte_fertigkeit = alt

        if alte_fertigkeit and alte_fertigkeit != fertigkeit_name:
            try:
                if hasattr(charakter, 'fertigkeiten') and alte_fertigkeit in charakter.fertigkeiten:
                    grundfertigkeiten = {
                        "Allgemeinwissen", "Athletik", "Heimlichkeit",
                        "Überreden", "Wahrnehmung",
                    }
                    alte = charakter.fertigkeiten[alte_fertigkeit]
                    if alte_fertigkeit in grundfertigkeiten:
                        if alte.wert == 6 and getattr(alte, 'modifier', 0) == 0:
                            alte.wuerfel.value = 4
                    else:
                        if alte.wert == 4 and getattr(alte, 'modifier', 0) == 0:
                            alte.wuerfel.modifier = -2
            except Exception as e:
                Logger.warning(f"Konnte alte freie Fertigkeit '{alte_fertigkeit}' nicht zurücksetzen: {e}")

        Logger.info(f"[DEBUG] Ändere freie Fertigkeit für '{volk_name}' Slot {slot_index} zu '{fertigkeit_name}'")
        success = waehle_freie_fertigkeit(charakter, volk_name, fertigkeit_name)

        if success:
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            aktuell = self.voelker_auswahlen[volk_name].get('fertigkeit')
            if isinstance(aktuell, list):
                if 0 <= slot_index < len(aktuell):
                    aktuell[slot_index] = fertigkeit_name
                else:
                    aktuell.append(fertigkeit_name)
            else:
                self.voelker_auswahlen[volk_name]['fertigkeit'] = [fertigkeit_name]

            if hasattr(self, '_fertigkeit_dialog') and self._fertigkeit_dialog:
                self._fertigkeit_dialog.dismiss()

            Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)

            Logger.info(f"Freie Fertigkeit für '{volk_name}' Slot {slot_index} erfolgreich geändert zu '{fertigkeit_name}'")
        else:
            Logger.error(f"Fehler beim Ändern der freien Fertigkeit für '{volk_name}'")

    def _on_edit_magieaffin(self):
        """Öffnet einen Dialog zum Auswählen eines Arkanen Hintergrunds (AH) für Magieaffin.
        Das gewählte AH-Talent legt automatisch die zugehörige Arkane Fertigkeit fest."""
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.chip import MDChip, MDChipText
        from kivymd.uix.button import MDButton, MDButtonText
        from kivy.metrics import dp

        volk_name = self.selected_volk_name
        if not volk_name:
            return

        charakter = self.controller.charakter
        from functions.volk_funktionen import get_magieaffin_optionen, get_aktuelles_magieaffin_ah

        ah_optionen = get_magieaffin_optionen(charakter, volk_name)
        aktuelles_ah = get_aktuelles_magieaffin_ah(charakter, volk_name)

        if not ah_optionen:
            from services.service_container import service_container
            ds = service_container.get_dialog_service()
            if ds:
                ds.show_warning_dialog(
                    "Im aktiven Setting ist kein Arkaner Hintergrund (AH) verfügbar. "
                    "Magieaffin kann daher nicht ausgewählt werden."
                )
            else:
                Logger.warning("Magieaffin: Keine AH-Talente im aktiven Setting verfügbar")
            return

        scroll_height = min(dp(350), len(ah_optionen) * dp(52))
        content_height = dp(86) + scroll_height
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(20),
            size_hint_y=None,
            height=content_height,
        )

        info_label = MDLabel(
            text="Wähle einen Arkanen Hintergrund:",
            bold=True,
            size_hint_y=None,
            height=dp(34),
        )
        content.add_widget(info_label)

        chips_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        chips_box.bind(minimum_height=chips_box.setter('height'))

        for ah_name, fertigkeit_name in ah_optionen:
            chip_kwargs = {
                'type': "filter",
                'size_hint_y': None,
                'height': dp(40),
                'on_release': lambda x, ah=ah_name: self._on_magieaffin_chosen(ah),
            }
            if hasattr(self, 'theme_cls') and self.theme_cls:
                if ah_name == aktuelles_ah:
                    chip_kwargs['md_bg_color'] = self.theme_cls.primaryContainerColor
                else:
                    chip_kwargs['md_bg_color'] = self.theme_cls.surfaceColor

            chip = MDChip(
                MDChipText(text=f"{ah_name}  →  {fertigkeit_name}"),
                **chip_kwargs,
            )
            chips_box.add_widget(chip)

        scroll = MDScrollView(size_hint_y=None, height=scroll_height, do_scroll_x=False)
        scroll.add_widget(chips_box)
        content.add_widget(scroll)

        button_container = MDDialogButtonContainer(MDBoxLayout(orientation="horizontal", spacing=dp(8)))
        cancel_btn = MDButton(style="text", on_release=lambda x: self._magieaffin_dialog.dismiss() if hasattr(self, '_magieaffin_dialog') else None)
        cancel_btn.add_widget(MDButtonText(text="Abbrechen"))
        button_container.add_widget(cancel_btn)

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"Magieaffin für {volk_name}"),
            MDDialogContentContainer(content, orientation="vertical"),
            button_container,
            size_hint=(0.85, None),
        )

        self._magieaffin_dialog = dialog
        dialog.open()

    def _on_magieaffin_chosen(self, ah_talent_name):
        """Wird aufgerufen wenn ein AH-Talent im Magieaffin-Dialog ausgewählt wird."""
        from kivy.clock import Clock
        from functions.volk_funktionen import waehle_magieaffin_fertigkeit

        volk_name = self.selected_volk_name
        if not volk_name:
            return

        charakter = self.controller.charakter
        Logger.info(f"[DEBUG] Wähle Magieaffin-AH '{ah_talent_name}' für '{volk_name}'")

        success = waehle_magieaffin_fertigkeit(charakter, volk_name, ah_talent_name)

        if success:
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            self.voelker_auswahlen[volk_name]['magieaffin'] = ah_talent_name

            if hasattr(self, '_magieaffin_dialog') and self._magieaffin_dialog:
                self._magieaffin_dialog.dismiss()

            Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)

            Logger.info(f"Magieaffin-AH für '{volk_name}' erfolgreich auf '{ah_talent_name}' gesetzt")
        else:
            Logger.error(f"Fehler beim Setzen des Magieaffin-AH für '{volk_name}'")

    def _baue_zusatzelement_karte(self, titel):
        """Erstellt Karte + Inhalts-Container mit Titelzeile für eine Zusatzelement-Sektion."""
        # Kompaktere Werte für Mobile
        _pad = dp(10) if _mobile else dp(14)
        _spacing = dp(6) if _mobile else dp(10)

        # Hauptcontainer für die Sektion
        section_card = MDCard(
            size_hint_x=1,
            size_hint_y=None,
            padding=_pad,
            spacing=_spacing,
            elevation=3,
            radius=[12],
            md_bg_color=self.theme_cls.surfaceContainerHighColor,
            style="elevated",
        )

        section_content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=_spacing
        )
        section_content.bind(minimum_height=section_content.setter('height'))
        section_card.bind(minimum_height=section_card.setter('height'))

        # Titel der Sektion
        titel_label = MDLabel(
            text=f"{titel}:",
            font_style="Body",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(24) if _mobile else dp(30),
            halign='left',
            valign='center',
            bold=True
        )
        section_content.add_widget(titel_label)

        return section_card, section_content

    def _baue_zusatzelement_auswahl_zeile(self, current_selection):
        """Zeile mit Chip des bereits gewählten Elements + Ändern-Button (Stift)."""
        from kivymd.uix.chip import MDChip, MDChipText

        auswahl_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10)
        )
        # Hintergrundfarbe sicherstellen (nie None)
        if hasattr(self, 'theme_cls') and self.theme_cls:
            bg_color = self.theme_cls.primaryContainerColor
        else:
            bg_color = [0.7, 0.8, 1.0, 1.0]  # hellblau als Fallback

        selected_chip = MDChip(
            MDChipText(text=current_selection),
            type="filter",
            active=True,
            md_bg_color=bg_color,
        )
        auswahl_row.add_widget(selected_chip)

        # Ändern-Button
        aendern_button = MDIconButton(
            icon="pencil",
            size_hint=(None, None),
            size=(dp(44), dp(44)),
        )
        auswahl_row.add_widget(aendern_button)

        return auswahl_row, aendern_button

    def _create_zusatzelement_section(self, titel, volk_name, auswahl_typ, get_options_func, select_func, placeholder_text, get_alle_items_func=None):
        """Erstellt eine Sektion für Zusatzelemente mit Inline-Chip-Auswahl.
        Ersetzt den bisherigen Dialog-basierten Ansatz für bessere Android-Kompatibilität."""
        from kivymd.uix.chip import MDChip, MDChipText
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

        section_card, section_content = self._baue_zusatzelement_karte(titel)

        # Aktuell ausgewählten Text ermitteln
        current_selection = self.voelker_auswahlen.get(volk_name, {}).get(auswahl_typ, None)

        # Ausgewähltes Element anzeigen (wenn vorhanden)
        aendern_button = None
        if current_selection and current_selection != placeholder_text:
            auswahl_row, aendern_button = self._baue_zusatzelement_auswahl_zeile(current_selection)
            section_content.add_widget(auswahl_row)

        # Suchfeld
        search_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(56),
            size_hint_x=1
        )
        search_field.add_widget(MDTextFieldHintText(text="Suchen..."))

        # Filter-Toggle State
        filter_state = {'nur_verfuegbare': True}

        # Suchzeile mit optionalem Filter-Button
        search_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            spacing=dp(10)
        )
        search_row.add_widget(search_field)

        if get_alle_items_func:
            filter_button = MDIconButton(
                icon="filter",
                style="tonal",
                size_hint=(None, None),
                size=(dp(56), dp(56))
            )
            search_row.add_widget(filter_button)

        # Scrollbare Chip-Liste
        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=dp(200),
        )

        chips_container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(6),
            padding=[0, dp(4), 0, dp(4)]
        )
        chips_container.bind(minimum_height=chips_container.setter('height'))

        def populate_chips(item_list):
            """Befüllt den Container mit Chips."""
            chips_container.clear_widgets()
            search_text = search_field.text.lower() if search_field.text else ""
            for item in sorted(item_list):
                if not item or not str(item).strip():
                    continue
                if item in [NO_TALENT_AVAILABLE_TEXT, NO_ATTRIBUT_AVAILABLE_TEXT, NO_FERTIGKEIT_AVAILABLE_TEXT]:
                    continue
                if search_text and search_text not in str(item).lower():
                    continue
                is_selected = (str(item) == current_selection)
                # Hintergrundfarbe sicherstellen (nie None)
                if hasattr(self, 'theme_cls') and self.theme_cls:
                    bg_color = self.theme_cls.primaryContainerColor if is_selected else self.theme_cls.surfaceColor
                else:
                    # Fallback-Farben
                    bg_color = [0.7, 0.8, 1.0, 1.0] if is_selected else [0.95, 0.95, 0.95, 1.0]
                
                chip = MDChip(
                    MDChipText(text=str(item)),
                    type="filter",
                    active=is_selected,
                    md_bg_color=bg_color,
                    size_hint_y=None,
                    height=dp(40),
                    on_release=lambda x, selected_item=item: self._on_chip_selected(select_func, selected_item)
                )
                chips_container.add_widget(chip)

            if not chips_container.children:
                chips_container.add_widget(MDLabel(
                    text="Keine Einträge gefunden",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(40),
                    halign='center'
                ))

        # Initiale Chips anzeigen
        options = get_options_func()
        populate_chips(options)

        scroll_view.add_widget(chips_container)

        # Such-Funktionalität
        def filter_items(instance, text):
            if filter_state['nur_verfuegbare']:
                current_items = get_options_func()
            else:
                current_items = get_alle_items_func() if get_alle_items_func else get_options_func()
            populate_chips(current_items)

        search_field.bind(text=filter_items)

        # Filter-Toggle
        if get_alle_items_func:
            def toggle_filter(instance):
                filter_state['nur_verfuegbare'] = not filter_state['nur_verfuegbare']
                if filter_state['nur_verfuegbare']:
                    filter_button.icon = "filter"
                    filter_button.style = "tonal"
                    current_items = get_options_func()
                else:
                    filter_button.icon = "filter-off"
                    filter_button.style = "outlined"
                    current_items = get_alle_items_func()
                populate_chips(current_items)

            filter_button.bind(on_release=toggle_filter)

        # Aufklapp-Logik: Suchfeld + Chips zunächst versteckt wenn bereits ausgewählt
        expandable_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(8)
        )
        expandable_box.bind(minimum_height=expandable_box.setter('height'))
        expandable_box.add_widget(search_row)
        expandable_box.add_widget(scroll_view)

        if current_selection and current_selection != placeholder_text:
            # Versteckt starten - nur Ändern-Button sichtbar
            expandable_box.opacity = 0
            expandable_box.disabled = True
            expandable_box.size_hint_y = None
            expandable_box.height = 0

            def toggle_expand(instance):
                if expandable_box.height == 0:
                    expandable_box.opacity = 1
                    expandable_box.disabled = False
                    expandable_box.size_hint_y = None
                    expandable_box.bind(minimum_height=expandable_box.setter('height'))
                    # Höhe neu berechnen
                    expandable_box.height = search_row.height + scroll_view.height + dp(8)
                else:
                    expandable_box.opacity = 0
                    expandable_box.disabled = True
                    expandable_box.height = 0

            aendern_button.bind(on_release=toggle_expand)

        section_content.add_widget(expandable_box)
        section_card.add_widget(section_content)

        return section_card

    def _on_chip_selected(self, select_func, item):
        """Behandelt die Auswahl eines Chips in der Inline-Auswahl."""
        try:
            Logger.debug(f"Chip ausgewählt: {item}")
            Window.release_all_keyboards()
            if select_func:
                select_func(item)
        except Exception as e:
            Logger.error(f"Fehler bei Chip-Auswahl: {e}", exc_info=True)

    def _show_dropdown_menu(self, items, callback, caller, get_options_func=None, get_alle_items_func=None):
        """Zeigt ein verbessertes Dialog-Menü mit Suchfeld."""
        # Items validieren
        Logger.debug(f"Dialog-Items: {items}")

        if not items:
            Logger.warning("Keine Items für Dialog verfügbar")
            return

        if len(items) == 1 and items[0] in [NO_TALENT_AVAILABLE_TEXT, NO_ATTRIBUT_AVAILABLE_TEXT, NO_FERTIGKEIT_AVAILABLE_TEXT]:
            Logger.warning(f"Nur Fehlermeldung verfügbar: {items[0]}")
            return

        try:
            # Erstelle Search-Dialog statt Dropdown
            self._show_search_dialog(items, callback, caller, get_options_func=get_options_func, get_alle_items_func=get_alle_items_func)

        except Exception as e:
            Logger.error(f"Fehler beim Erstellen des Dialog-Menüs: {e}", exc_info=True)

    def _show_search_dialog(self, items, callback, caller, get_options_func=None, get_alle_items_func=None):
        """Zeigt einen erweiterten Dialog mit Suchfeld für Talent/Attribut/Fertigkeiten-Auswahl.
        Aufbau wie Setting-Wechsel-Dialog für Android-Kompatibilität."""
        from kivymd.uix.dialog import (
            MDDialog, MDDialogHeadlineText,
            MDDialogContentContainer
        )
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
        from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
        from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
        from kivymd.uix.scrollview import MDScrollView

        try:
            # State für Filter-Toggle
            filter_state = {'nur_verfuegbare': True}

            # Hauptcontainer für den Dialog
            dialog_content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            dialog_content.bind(minimum_height=dialog_content.setter('height'))

            # Suchzeile mit optionalem Filter-Button
            search_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(56),
                spacing=dp(10)
            )

            # Suchfeld
            search_field = MDTextField(
                mode="outlined",
                size_hint_y=None,
                height=dp(56),
                size_hint_x=1
            )
            search_hint = MDTextFieldHintText(text="Suchen...")
            search_field.add_widget(search_hint)
            search_row.add_widget(search_field)

            # Filter-Button nur anzeigen wenn alle-Items-Funktion vorhanden
            if get_alle_items_func and get_options_func:
                filter_button = MDIconButton(
                    icon="filter",
                    style="tonal",
                    size_hint=(None, None),
                    size=(dp(56), dp(56))
                )
                search_row.add_widget(filter_button)

            # Scrollbare Liste
            scroll_view = MDScrollView(
                size_hint=(1, None),
                height=dp(250),
            )

            # Container für Liste
            list_container = MDBoxLayout(
                orientation='horizontal',
                size_hint=(1, None)
            )
            list_container.bind(minimum_height=list_container.setter('height'))

            items_list = MDList(
                size_hint_y=None,
                size_hint_x=1
            )
            items_list.bind(minimum_height=items_list.setter('height'))

            def populate_list(item_list):
                """Befüllt die Liste mit Items."""
                items_list.clear_widgets()
                search_text = search_field.text.lower() if search_field.text else ""
                for item in sorted(item_list):
                    if item and str(item).strip():
                        if search_text and search_text not in str(item).lower():
                            continue
                        list_item = MDListItem(
                            size_hint_y=None,
                            height=dp(48),
                            on_release=lambda x, selected_item=item: self._defocus_and_call(lambda: self._on_search_dialog_item_selected(callback, selected_item))
                        )
                        list_item.add_widget(MDListItemHeadlineText(text=str(item)))
                        items_list.add_widget(list_item)

            # Initiale Items anzeigen
            populate_list(items)

            # Container zusammenbauen
            list_container.add_widget(items_list)
            list_container.add_widget(MDBoxLayout(size_hint_x=None, width=dp(20)))
            scroll_view.add_widget(list_container)
            list_container.bind(minimum_height=list_container.setter('height'))

            # Such-Funktionalität
            def filter_items(instance, text):
                if filter_state['nur_verfuegbare']:
                    current_items = get_options_func() if get_options_func else items
                else:
                    current_items = get_alle_items_func() if get_alle_items_func else items
                populate_list(current_items)

            search_field.bind(text=filter_items)

            # Filter-Toggle Funktionalität
            if get_alle_items_func and get_options_func:
                def toggle_filter(instance):
                    filter_state['nur_verfuegbare'] = not filter_state['nur_verfuegbare']
                    if filter_state['nur_verfuegbare']:
                        filter_button.icon = "filter"
                        filter_button.style = "tonal"
                        current_items = get_options_func()
                    else:
                        filter_button.icon = "filter-off"
                        filter_button.style = "outlined"
                        current_items = get_alle_items_func()
                    populate_list(current_items)
                    Logger.debug(f"Filter-Toggle: nur_verfuegbare={filter_state['nur_verfuegbare']}")

                filter_button.bind(on_release=toggle_filter)

            # Container zusammenbauen
            dialog_content.add_widget(search_row)
            dialog_content.add_widget(scroll_view)

            # Buttons innerhalb des Content-Containers (wie Setting-Wechsel-Dialog)
            button_row = MDBoxLayout(
                orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8)
            )
            button_row.add_widget(MDBoxLayout(size_hint_x=1))
            button_row.add_widget(MDButton(
                MDButtonText(text="Abbrechen"), style="text",
                on_release=lambda x: self._defocus_and_call(self.search_dialog.dismiss),
            ))
            dialog_content.add_widget(button_row)

            # Dialog erstellen - auto_dismiss=False für Android-Kompatibilität
            self.search_dialog = MDDialog(
                MDDialogHeadlineText(text="Auswahl treffen"),
                MDDialogContentContainer(
                    dialog_content,
                    orientation="vertical",
                    padding=dp(0),
                ),
                size_hint=(0.85, None),
                auto_dismiss=False,
            )

            self.search_dialog.open()
            Logger.debug(f"Search-Dialog erfolgreich geöffnet mit {len(items)} Items")

        except Exception as e:
            Logger.error(f"Fehler beim Search-Dialog: {e}", exc_info=True)

    def _on_search_dialog_item_selected(self, callback, item):
        """Behandelt die Auswahl eines Items im Search-Dialog."""
        try:
            Logger.debug(f"Search-Dialog-Item ausgewählt: {item}")
            
            if hasattr(self, 'search_dialog'):
                self.search_dialog.dismiss()
                
            # Überprüfen ob es sich um eine Fehlermeldung handelt
            if item in [NO_TALENT_AVAILABLE_TEXT, NO_ATTRIBUT_AVAILABLE_TEXT, NO_FERTIGKEIT_AVAILABLE_TEXT]:
                Logger.warning(f"Fehlermeldung ausgewählt: {item}")
                return
                
            # Callback ausführen
            if callback:
                callback(item)
                Logger.debug(f"Callback für Item '{item}' ausgeführt")
            else:
                Logger.warning("Kein Callback für Dialog-Auswahl definiert")
                
        except Exception as e:
            Logger.error(f"Fehler bei Search-Dialog-Auswahl: {e}", exc_info=True)

    # === AUSWAHL-FUNKTIONEN (rufen jetzt volk_funktionen.py auf) ===
    
    def _select_talent(self, volk_name, talent_name):
        """Wählt ein Talent aus (UI-Wrapper für Geschäftslogik)."""
        try:
            charakter = self.controller.charakter
            
            # Geschäftslogik aufrufen
            success = waehle_freies_talent(charakter, volk_name, talent_name)
            
            if success:
                # UI-lokale Auswahl speichern für Anzeige (an Liste anhängen)
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}
                liste = self.voelker_auswahlen[volk_name].setdefault('talent', [])
                if not isinstance(liste, list):
                    liste = [liste]
                    self.voelker_auswahlen[volk_name]['talent'] = liste
                liste.append(talent_name)

                # UI aktualisieren
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)

        except Exception as e:
            Logger.error(f"Fehler bei Talent-Auswahl (UI): {e}", exc_info=True)

    def _select_attribut(self, volk_name, attribut_name):
        """Wählt ein Attribut aus (UI-Wrapper für Geschäftslogik)."""
        try:
            charakter = self.controller.charakter

            # Geschäftslogik aufrufen
            success = waehle_freies_attribut(charakter, volk_name, attribut_name)

            if success:
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}
                liste = self.voelker_auswahlen[volk_name].setdefault('attribut', [])
                if not isinstance(liste, list):
                    liste = [liste]
                    self.voelker_auswahlen[volk_name]['attribut'] = liste
                liste.append(attribut_name)

                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)

        except Exception as e:
            Logger.error(f"Fehler bei Attribut-Auswahl (UI): {e}", exc_info=True)

    def _select_fertigkeit(self, volk_name, fertigkeit_name):
        """Wählt eine Fertigkeit aus (UI-Wrapper für Geschäftslogik)."""
        try:
            charakter = self.controller.charakter

            # Geschäftslogik aufrufen
            success = waehle_freie_fertigkeit(charakter, volk_name, fertigkeit_name)

            if success:
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}
                liste = self.voelker_auswahlen[volk_name].setdefault('fertigkeit', [])
                if not isinstance(liste, list):
                    liste = [liste]
                    self.voelker_auswahlen[volk_name]['fertigkeit'] = liste
                liste.append(fertigkeit_name)
                
                # UI aktualisieren  
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
                
        except Exception as e:
            Logger.error(f"Fehler bei Fertigkeiten-Auswahl (UI): {e}", exc_info=True)
