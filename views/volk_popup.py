# volk-popup.py
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText
from kivymd.uix.scrollview import MDScrollView
from views.ui_components import TextFieldScrollView
from utils.platform_utils import is_mobile_layout, landscape_height
_mobile = is_mobile_layout()
from kivymd.uix.card import MDCard
from kivymd.uix.divider import MDDivider
from kivy.uix.button import Button
from kivymd.uix.list import MDListItemTrailingCheckbox

from models.volk import Volk
from functions.volkseigenarten_funktionen import (
    get_merged_eigenarten_config,
    berechne_punktestand,
    ist_punktestand_gueltig,
    get_eigenart_by_id,
    eigenart_zu_effekte,
    eigenart_zu_besonderheiten,
    validiere_volk_erstellung,
    lade_eigenarten_fuer_bearbeitung,
    formatiere_punkte_anzeige,
    erstelle_eigenart_dict,
    speichere_custom_eigenart,
    loesche_custom_eigenart,
    stufen_kosten_bereich,
    wende_stufe_an,
    START_PUNKTE
)
from functions.talent_funktionen import pruefe_voraussetzungen, is_talent_rang_hoeher_als_charakter

import os
import sys
import time

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'volk_popup.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'volk_popup.kv')

    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"volk_popup: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()

class VolkDialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

class DeleteVolkDialogContent(MDBoxLayout):
    def __init__(self, voelker_callback=None, menu_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.voelker_callback = voelker_callback
        self.menu_callback = menu_callback
        self.dialog = None

    def open_menu(self, instance_item):
        if not self.voelker_callback:
            return

        voelker = self.voelker_callback()
        if not voelker:
            return

        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_item(x),
            }
            for name in voelker
        ]

        MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
        ).open()

    def select_item(self, text_item):
        if self.menu_callback:
            self.menu_callback(text_item)
        if hasattr(self.ids, 'volk_dropdown'):
            self.ids.volk_dropdown.text = text_item

class VolkGeneratorWizard:
    """
    Mehrstufiger Wizard für die Erstellung und Bearbeitung von Völkern
    mit Volkseigenarten nach dem Savage Worlds Punktesystem.
    """
    
    def __init__(self, controller, callback=None, edit_volk=None):
        self.controller = controller
        self.callback = callback
        self.edit_volk = edit_volk
        self.current_step = 0
        self.dialog = None
        
        self.positive_eigenarten = []
        self.negative_eigenarten = []
        
        self._wizard_finished = False
        self._filter_nur_verfuegbar = True  # Filter für Talent-Auswahl

        self.wizard_data = {
            'name': '',
            'beschreibung': '',
            'positive': [],
            'negative': []
        }
        
        if edit_volk:
            self._load_volk_for_editing(edit_volk)
        
        self.steps = [
            {"Title": "Name & Grundlagen", "handler": self._create_name_step},
            {"Title": "Positive Abstammungseigenarten", "handler": self._create_positive_step},
            {"Title": "Negative Abstammungseigenarten", "handler": self._create_negative_step},
            {"Title": "Vorschau & Speichern", "handler": self._create_preview_step}
        ]
    
    def _load_volk_for_editing(self, volk):
        """Lädt ein Volk für die Bearbeitung"""
        volk_dict = {
            'name': volk.name,
            'beschreibung': '',
            'eigenarten': volk.effects.get('eigenarten', [])
        }
        self.positive_eigenarten, self.negative_eigenarten = lade_eigenarten_fuer_bearbeitung(volk_dict)
        self.wizard_data['name'] = volk.name
    
    def start_wizard(self):
        """Startet den Wizard"""
        Logger.info("Volkseigenarten-Wizard gestartet")
        self.current_step = 0
        self._show_current_step()
    
    def _show_current_step(self):
        """Zeigt den aktuellen Wizard-Schritt"""
        self._navigating = True
        try:
            self.__show_current_step_inner()
        finally:
            # Flag nach kurzem Delay zurücksetzen (Android Touch-Events abklingen lassen)
            Clock.schedule_once(lambda dt: setattr(self, '_navigating', False), 0.3)

    def __show_current_step_inner(self):
        """Innere Implementierung von _show_current_step"""
        if self.current_step >= len(self.steps):
            self._finish_wizard()
            return

        step = self.steps[self.current_step]
        Logger.info(f"Zeige Wizard-Schritt {self.current_step + 1}: {step['Title']}")

        if self.dialog:
            old_dialog = self.dialog
            self.dialog = None
            old_dialog.dismiss()

        content = step['handler']()
        
        nav_layout = MDBoxLayout(
            orientation="horizontal",
            spacing="8dp",
            size_hint_y=None,
            height="50dp",
            adaptive_height=True
        )

        if self.current_step > 0:
            back_btn = MDButton(style="text", on_release=self._previous_step, size_hint_x=None, width=dp(40))
            back_btn.add_widget(MDButtonIcon(icon="arrow-left"))
            if not _mobile:
                back_btn.add_widget(MDButtonText(text="Zurück"))
            nav_layout.add_widget(back_btn)

        if _mobile:
            cancel_btn = MDButton(style="text", on_release=self._cancel_wizard, size_hint_x=None, width=dp(40))
            cancel_btn.add_widget(MDButtonIcon(icon="close"))
        else:
            cancel_btn = MDButton(style="text", on_release=self._cancel_wizard)
            cancel_btn.add_widget(MDButtonText(text="Abbrechen"))
        nav_layout.add_widget(cancel_btn)

        spacer = MDBoxLayout(size_hint_x=1)
        nav_layout.add_widget(spacer)

        is_last_step = self.current_step == len(self.steps) - 1
        if _mobile:
            next_icon = "check" if is_last_step else "arrow-right"
            next_btn = MDButton(
                style="filled",
                on_release=self._finish_wizard if is_last_step else self._next_step,
                size_hint_x=None, width=dp(48)
            )
            next_btn.add_widget(MDButtonIcon(icon=next_icon))
        else:
            next_btn = MDButton(
                style="filled",
                on_release=self._finish_wizard if is_last_step else self._next_step
            )
            next_btn.add_widget(MDButtonIcon(icon="check" if is_last_step else "arrow-right"))
            next_btn.add_widget(MDButtonText(text="Speichern" if is_last_step else "Weiter"))
        nav_layout.add_widget(next_btn)
        
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height="650dp"
        )
        
        progress_text = f"Schritt {self.current_step + 1} von {len(self.steps)}"
        if self.edit_volk:
            progress_text += " (Bearbeiten)"
        else:
            progress_text += " (Neue Abstammung)"
        
        progress_label = MDLabel(
            text=progress_text,
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        main_layout.add_widget(progress_label)
        main_layout.add_widget(content)
        main_layout.add_widget(MDDivider())
        main_layout.add_widget(nav_layout)
        
        title = "Abstammung erstellen" if not self.edit_volk else f"Abstammung bearbeiten: {self.edit_volk.name}"
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(main_layout),
            size_hint=(0.9, 0.85),
            auto_dismiss=False,
        )

        self.dialog.open()

        # Schritt 1: Name-Feld explizit fokussieren (verhindert Fokus-Sprung zu Beschreibung)
        if self.current_step == 0 and hasattr(self, 'name_field'):
            Clock.schedule_once(lambda dt: setattr(self.name_field, 'focus', True), 0.3)
    
    def _create_name_step(self):
        """Erstellt Schritt 1: Name & Grundlagen"""
        layout = TextFieldScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height="350dp"
        )
        
        info_label = MDLabel(
            text=f"Abstammungseigenarten-System: Starte mit {START_PUNKTE} Punkten für positive Eigenarten.",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="40dp"
        )
        content.add_widget(info_label)
        
        self.name_field = MDTextField(
            MDTextFieldHintText(text="Name der Abstammung *"),
            mode="outlined",
            text=self.wizard_data.get('name', '')
        )
        self.name_field.bind(text=self._update_name)
        content.add_widget(self.name_field)
        
        self.beschreibung_field = MDTextField(
            MDTextFieldHintText(text="Beschreibung (optional)"),
            mode="outlined",
            text=self.wizard_data.get('beschreibung', ''),
            multiline=True
        )
        self.beschreibung_field.bind(text=self._update_beschreibung)
        content.add_widget(self.beschreibung_field)
        
        layout.add_widget(content)
        return layout
    
    def _create_positive_step(self):
        """Erstellt Schritt 2: Positive Volkseigenarten (Button öffnet Popup)"""
        return self._create_eigenarten_button_step('positive')

    def _create_negative_step(self):
        """Erstellt Schritt 3: Negative Volkseigenarten (Button öffnet Popup)"""
        return self._create_eigenarten_button_step('negative')

    def _create_eigenarten_button_step(self, eigenart_typ):
        """Erstellt Wizard-Schritt mit Button, der das Eigenarten-Popup öffnet"""
        layout = MDBoxLayout(orientation="vertical", spacing=dp(16), padding=dp(16))

        title = "Positive Abstammungseigenarten" if eigenart_typ == 'positive' else "Negative Abstammungseigenarten"

        label = MDLabel(
            text=f"{title} auswählen",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(label)

        punkte_status = berechne_punktestand(self.positive_eigenarten + self.negative_eigenarten)
        if eigenart_typ == 'positive':
            punkte_text = f"Punkte: {START_PUNKTE} Startpunkte verfügbar für positive Eigenarten"
        else:
            if punkte_status['positive_kosten'] > START_PUNKTE:
                fehlende = punkte_status['positive_kosten'] - START_PUNKTE
                punkte_text = f"Müssen {fehlende} EP durch negative Eigenarten ausgeglichen werden"
            else:
                punkte_text = f"Positive Eigenarten kosten {punkte_status['positive_kosten']} EP (von {START_PUNKTE} abgezogen)"

        punkte_label = MDLabel(
            text=punkte_text,
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(24)
        )
        layout.add_widget(punkte_label)

        btn = MDButton(style="tonal", size_hint_y=None, height=dp(48))
        btn.add_widget(MDButtonText(text=f"{title} auswählen..."))
        btn.bind(on_release=lambda x: self._show_eigenarten_popup(eigenart_typ))
        layout.add_widget(btn)

        auswahl = self.positive_eigenarten if eigenart_typ == 'positive' else self.negative_eigenarten
        if auswahl:
            items_label = MDLabel(
                text=f"Ausgewählt ({len(auswahl)}):",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height=dp(24)
            )
            layout.add_widget(items_label)

            items_scroll = MDScrollView(size_hint_y=1, bar_width=dp(12), bar_margin=dp(4))
            items_content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(6),
                size_hint_y=None,
                height=dp(len(auswahl) * dp(42))
            )
            items_content.bind(minimum_height=items_content.setter('height'))

            for eigenart in auswahl:
                item_row = self._build_wizard_eigenart_row(eigenart, eigenart_typ)
                items_content.add_widget(item_row)

            items_scroll.add_widget(items_content)
            layout.add_widget(items_scroll)

        return layout

    def _build_wizard_eigenart_row(self, eigenart, eigenart_typ):
        """Erstellt eine Einzelzeile für eine Eigenart im Wizard mit ×-Button."""
        from kivymd.uix.button import MDIconButton

        row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(36),
            padding=(dp(4), 0, 0, 0)
        )

        eid = eigenart.get('id', '')
        name = eigenart.get('name', eid)
        kosten = eigenart.get('kosten', 0)

        detail_parts = []
        if eigenart.get('stufen'):
            stufe = eigenart.get('ausgewaehlte_stufe', 0)
            if isinstance(stufe, int):
                detail_parts.append(f"Stufe {stufe + 1}")
            elif isinstance(stufe, dict) and 'label' in stufe:
                detail_parts.append(f"Stufe: {stufe['label']}")
        if eigenart.get('optionen', {}).get('ausgewaehlt'):
            detail_parts.append(eigenart['optionen']['ausgewaehlt'])
        if eigenart.get('optionen', {}).get('rang') is not None:
            rang_names = ["Anfänger", "Erfahren", "Veteran", "Heroisch", "Held"]
            detail_parts.append(f"Rang: {rang_names[eigenart['optionen']['rang']]}")

        if detail_parts:
            full_text = f"{name} [{kosten} EP] — {' / '.join(detail_parts)}"
        else:
            full_text = f"{name} [{kosten} EP]"

        text_label = MDLabel(
            text=full_text,
            theme_text_color="Secondary",
            size_hint_x=1,
            valign="middle",
            halign="left"
        )
        row.add_widget(text_label)

        remove_btn = MDIconButton(
            icon="close",
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            pos_hint={"center_y": 0.5}
        )
        e = eigenart
        et = eigenart_typ
        remove_btn.bind(
            on_release=lambda x, eig=e, typ=et: self._on_wizard_remove_eigenart(eig, typ)
        )
        row.add_widget(remove_btn)

        return row

    def _on_wizard_remove_eigenart(self, eigenart, eigenart_typ):
        """Entfernt eine einzelne Eigenart-Instanz aus dem Wizard."""
        liste = self.positive_eigenarten if eigenart_typ == 'positive' else self.negative_eigenarten
        if eigenart in liste:
            liste.remove(eigenart)
        self._show_current_step()

    def _show_eigenarten_popup(self, eigenart_typ):
        """Zeigt separates Popup für Eigenarten-Checkboxen (eigener ScrollView)"""
        if self._wizard_finished:
            return

        self._eigenarten_popup_typ = eigenart_typ

        if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
            self._eigenarten_popup.dismiss()

        from kivy.core.window import Window

        config = get_merged_eigenarten_config()
        eigenarten = config.get(eigenart_typ, [])
        aktuelle_auswahl = self.positive_eigenarten if eigenart_typ == 'positive' else self.negative_eigenarten
        title = "Positive Abstammungseigenarten" if eigenart_typ == 'positive' else "Negative Abstammungseigenarten"

        popup_height = min(Window.height * 0.75, dp(420))
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=popup_height
        )

        btn_text = "Neue Eigenart erstellen..."
        create_btn = MDButton(style="tonal", size_hint_y=None, height=dp(48))
        create_btn.add_widget(MDButtonText(text=btn_text))
        create_btn.bind(on_release=lambda x: self._show_create_eigenart_dialog(eigenart_typ))
        content.add_widget(create_btn)

        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        if _mobile:
            list_layout.padding = [0, 0, dp(32), 0]

        # WIDGET-TRACKING: Stepper-Widgets für direkte Updates
        self._stepper_widgets = {}

        for eigenart in eigenarten:
            eigenart_id = eigenart.get('id')
            aktuelle_anzahl = sum(1 for e in aktuelle_auswahl if e.get('id') == eigenart_id)
            max_auswahl = eigenart.get('max_auswahl', 1)

            voraussetzung = eigenart.get('voraussetzung')
            if voraussetzung == 'setting_hat_superkraefte':
                try:
                    from kivymd.app import MDApp
                    app = MDApp.get_running_app()
                    if app and hasattr(app, 'controller') and app.controller:
                        setting_name = getattr(app.controller.charakter, 'setting_name', '')
                        from functions.superkraft_funktionen import ist_superkraefte_setting
                        if not ist_superkraefte_setting(setting_name):
                            continue
                except Exception:
                    pass

            stufen_bereich = stufen_kosten_bereich(eigenart)
            if stufen_bereich:
                min_k, max_k = stufen_bereich
                if min_k == max_k:
                    kosten_text = f" [{min_k} EP]"
                else:
                    kosten_text = f" [{min_k}–{max_k} EP]"
            else:
                kosten = eigenart.get('kosten', 2)
                kosten_text = f" [{kosten} EP]"

            if max_auswahl == 0:
                max_text = " (U)"
            elif max_auswahl > 1:
                max_text = f" ({aktuelle_anzahl}/{max_auswahl})"
            else:
                max_text = ""
            if eigenart.get('custom'):
                max_text += " [Eigene]"

            list_item = MDListItem(size_hint_y=None, height=dp(56))
            list_item.add_widget(MDListItemHeadlineText(
                text=f"{eigenart.get('name', eigenart_id)}{kosten_text}{max_text}"
            ))
            if eigenart.get('beschreibung'):
                list_item.add_widget(MDListItemSupportingText(
                    text=eigenart.get('beschreibung', '')
                ))

            if max_auswahl == 1:
                checkbox = MDListItemTrailingCheckbox(active=aktuelle_anzahl > 0)
                cb = checkbox
                e_id = eigenart_id
                e_typ = eigenart_typ
                checkbox.bind(on_release=lambda x, cb=cb, eid=e_id, et=e_typ: self._on_eigenart_checkbox_clicked(eid, et, cb))

                if eigenart.get('custom') and aktuelle_anzahl == 0:
                    from kivymd.uix.button import MDIconButton
                    delete_btn = MDIconButton(
                        icon="delete",
                        style="tonal",
                        size_hint=(None, None),
                        size=(dp(32), dp(32)),
                        pos_hint={"center_y": 0.5}
                    )
                    del_id = eigenart_id
                    del_typ = eigenart_typ
                    delete_btn.bind(on_release=lambda x, did=del_id, dt=del_typ: self._delete_custom_eigenart(did, dt))
                    list_item.add_widget(delete_btn)

                list_item.add_widget(checkbox)
            else:
                minus_btn = Button(
                    text="-",
                    font_size="18sp",
                    size_hint=(None, None),
                    size=(dp(36), dp(36)),
                    pos_hint={"center_y": 0.5},
                    background_normal='',
                    background_down='',
                    background_color=(0.4, 0.4, 0.4, 1) if aktuelle_anzahl == 0 else (0.2, 0.5, 0.8, 1),
                    disabled=aktuelle_anzahl == 0,
                    disabled_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x, eid=eigenart_id, et=eigenart_typ: self._on_stepper_minus(eid, et)
                )

                count_label = MDLabel(
                    text=str(aktuelle_anzahl),
                    size_hint=(None, None),
                    size=(dp(24), dp(24)),
                    pos_hint={"center_y": 0.5},
                    halign="center"
                )

                plus_btn = Button(
                    text="+",
                    font_size="18sp",
                    size_hint=(None, None),
                    size=(dp(36), dp(36)),
                    pos_hint={"center_y": 0.5},
                    background_normal='',
                    background_down='',
                    background_color=(0.4, 0.4, 0.4, 1) if (max_auswahl != 0 and aktuelle_anzahl >= max_auswahl) else (0.2, 0.7, 0.3, 1),
                    disabled=(max_auswahl != 0 and aktuelle_anzahl >= max_auswahl),
                    disabled_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x, eid=eigenart_id, et=eigenart_typ: self._on_stepper_plus(eid, et)
                )

                stepper_box = MDBoxLayout(
                    orientation="horizontal",
                    size_hint=(None, None),
                    size=(dp(100), dp(36)),
                    pos_hint={"center_y": 0.5},
                    spacing=dp(4)
                )
                stepper_box.add_widget(minus_btn)
                stepper_box.add_widget(count_label)
                stepper_box.add_widget(plus_btn)

                list_item.add_widget(stepper_box)

                # TRACKING: Stepper-Widgets für späteres Update speichern
                self._stepper_widgets[eigenart_id] = {
                    'minus': minus_btn,
                    'count': count_label,
                    'plus': plus_btn,
                    'box': stepper_box,
                    'item': list_item,
                    'max_auswahl': max_auswahl
                }

            list_layout.add_widget(list_item)

        scroll = MDScrollView(do_scroll_x=False, do_scroll_y=True, bar_width=dp(20) if _mobile else dp(15), bar_margin=dp(8) if _mobile else dp(4))
        if _mobile:
            scroll.scroll_type = ['bars', 'content']
        scroll.add_widget(list_layout)
        content.add_widget(scroll)

        cancel_btn = MDButton(
            style="text",
            on_release=lambda x: self._cancel_eigenarten_popup()
        )
        cancel_btn.add_widget(MDButtonIcon(icon="close"))
        if not _mobile:
            cancel_btn.add_widget(MDButtonText(text="Abbrechen"))

        confirm_btn = MDButton(
            style="filled",
            on_release=lambda x: self._close_eigenarten_popup(eigenart_typ)
        )
        confirm_btn.add_widget(MDButtonIcon(icon="check"))
        if not _mobile:
            confirm_btn.add_widget(MDButtonText(text="Übernehmen"))

        self._eigenarten_popup = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                cancel_btn,
                confirm_btn,
            ),
            size_hint=(0.9, None),
        )
        self._eigenarten_popup.open()

    def _cancel_eigenarten_popup(self):
        """Schließt das Eigenarten-Popup OHNE die Auswahl zu übernehmen (Abbrechen)."""
        if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
            self._eigenarten_popup.dismiss()

    def _show_create_eigenart_dialog(self, eigenart_typ):
        """Zeigt einen Dialog zum Erstellen einer neuen benutzerdefinierten Volkseigenart.
        Blendet das Eigenarten-Popup temporär aus um Überlappung zu vermeiden."""
        import time as time_mod

        # Eigenarten-Popup temporär ausblenden
        if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
            self._eigenarten_popup.opacity = 0

        is_positive = eigenart_typ == 'positive'
        titel_text = "Neuen Abstammungsvorteil erstellen" if is_positive else "Neuen Abstammungsnachteil erstellen"

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(240),
            padding=dp(8)
        )

        # Name-Feld
        name_field = MDTextField(mode="outlined", size_hint_y=None, height=dp(56))
        name_field.add_widget(MDTextFieldHintText(text="Name der Eigenart *"))
        content.add_widget(name_field)

        # EP-Kosten-Feld
        kosten_field = MDTextField(mode="outlined", size_hint_y=None, height=dp(56),
                                   text="2" if is_positive else "-2",
                                   input_filter="int")
        kosten_field.add_widget(MDTextFieldHintText(text="EP-Kosten (z.B. 2, -2)"))
        content.add_widget(kosten_field)

        # Beschreibung-Feld
        beschr_field = MDTextField(mode="outlined", size_hint_y=None, height=dp(56))
        beschr_field.add_widget(MDTextFieldHintText(text="Beschreibung (wird im Charakterbogen angezeigt)"))
        content.add_widget(beschr_field)

        def _on_cancel(x):
            dialog.dismiss()
            self._restore_eigenarten_popup()

        def _on_save(x):
            name = name_field.text.strip()
            if not name:
                self._show_error("Bitte gib einen Namen für die Eigenart ein.")
                return

            try:
                kosten = int(kosten_field.text.strip())
            except ValueError:
                kosten = 2 if is_positive else -2

            if is_positive and kosten <= 0:
                kosten = 2
            elif not is_positive and kosten >= 0:
                kosten = -2

            beschreibung = beschr_field.text.strip()

            eigenart = erstelle_eigenart_dict(
                name=name,
                kosten=kosten,
                effekt_typ='spezieller_effekt',
                beschreibung=beschreibung if beschreibung else None,
            )

            speichere_custom_eigenart(eigenart, eigenart_typ)

            # Altes Eigenarten-Popup schließen (war mit opacity=0 ausgeblendet)
            if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
                self._eigenarten_popup.dismiss()

            dialog.dismiss()

            # Eigenarten-Popup mit aktualisierter Liste neu aufbauen
            Clock.schedule_once(lambda dt: self._show_eigenarten_popup(eigenart_typ), 0.35)

        dialog = MDDialog(
            MDDialogHeadlineText(text=titel_text),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text", on_release=_on_cancel),
                MDButton(MDButtonText(text="Erstellen"), style="filled", on_release=_on_save),
            ),
            size_hint=(0.85, None),
        )
        dialog.open()

    def _delete_custom_eigenart(self, eigenart_id, eigenart_typ):
        """Löscht eine benutzerdefinierte Eigenart nach Bestätigung."""
        def _on_confirm(x):
            loesche_custom_eigenart(eigenart_id, eigenart_typ)
            dialog.dismiss()
            # Eigenarten-Popup neu aufbauen
            Clock.schedule_once(lambda dt: self._show_eigenarten_popup(eigenart_typ), 0.35)

        def _on_cancel(x):
            dialog.dismiss()

        eigenart = get_eigenart_by_id(eigenart_id, eigenart_typ)
        name = eigenart.get('name', eigenart_id) if eigenart else eigenart_id

        del_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(60),
            padding=dp(16)
        )
        del_content.add_widget(
            MDLabel(text=f"Möchtest du die Eigenart '[b]{name}[/b]' wirklich löschen?",
                    markup=True, size_hint_y=None, height=dp(40),
                    adaptive_height=True)
        )

        dialog = MDDialog(
            MDDialogHeadlineText(text="Eigenart löschen"),
            MDDialogContentContainer(del_content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text", on_release=_on_cancel),
                MDButton(MDButtonText(text="Löschen"), style="filled", on_release=_on_confirm),
            ),
            size_hint=(0.85, None),
        )
        dialog.open()

    def _close_eigenarten_popup(self, eigenart_typ):
        """Schließt das Eigenarten-Popup und aktualisiert den Wizard-Schritt"""
        if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
            self._eigenarten_popup.dismiss()
        if self._wizard_finished:
            return
        # Wizard-Schritt nach kurzer Verzögerung neu aufbauen —
        # verhindert Touch-Propagation auf Android (Schließen-Touch wird sonst
        # an den neuen "Eigenarten auswählen"-Button weitergeleitet und öffnet
        # das Popup sofort wieder).
        Clock.schedule_once(lambda dt: self._show_current_step(), 0.35)
    
    def _create_preview_step(self):
        """Erstellt Schritt 4: Vorschau & Speichern"""
        layout = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height="650dp"
        )
        
        preview_card = MDCard(
            style="elevated",
            padding="12dp",
            size_hint_y=None,
            height="500dp"
        )
        
        preview_content = MDBoxLayout(
            orientation="vertical",
            spacing="8dp"
        )
        
        summary = self._generate_preview_summary()
        preview_label = MDLabel(
            text=summary,
            theme_text_color="Primary",
            markup=True,
            size_hint_y=None,
            height="480dp"
        )
        
        preview_scroll = MDScrollView()
        preview_scroll.add_widget(preview_label)
        preview_content.add_widget(preview_scroll)
        
        preview_card.add_widget(preview_content)
        content.add_widget(preview_card)
        
        validation = validiere_volk_erstellung(
            self.wizard_data['name'],
            self.positive_eigenarten,
            self.negative_eigenarten
        )
        
        if not validation['ist_gueltig']:
            error_label = MDLabel(
                text="[color=ff0000]Fehler:[/color] " + "\n".join(validation['fehler']),
                theme_text_color="Error",
                markup=True,
                size_hint_y=None,
                height="60dp"
            )
            content.add_widget(error_label)
        elif validation['warnungen']:
            warn_label = MDLabel(
                text="[color=ffaa00]Warnungen:[/color] " + "\n".join(validation['warnungen']),
                theme_text_color="Secondary",
                markup=True,
                size_hint_y=None,
                height="40dp"
            )
            content.add_widget(warn_label)
        
        layout.add_widget(content)
        return layout
    
    def _generate_preview_summary(self):
        """Generiert eine Vorschau-Zusammenfassung"""
        name = self.wizard_data.get('name', 'Unbenannt') or 'Unbenannt'
        beschreibung = self.wizard_data.get('beschreibung', '')
        
        summary = f"[b]{name}[/b]\n"
        if beschreibung:
            summary += f"[i]{beschreibung}[/i]\n"
        summary += "\n"
        
        punkte_status = berechne_punktestand(self.positive_eigenarten + self.negative_eigenarten)
        summary += f"[b]Punkte:[/b] {punkte_status['positive_kosten']} EP positive / {START_PUNKTE} Startpunkte\n"
        if punkte_status['negative_punkte'] > 0:
            summary += f"[b]Ausgleich:[/b] +{punkte_status['negative_punkte']} EP durch negative Eigenarten\n"
        summary += "\n"
        
        if self.positive_eigenarten:
            summary += f"[b]Positive Abstammungseigenarten ({len(self.positive_eigenarten)}):[/b]\n"
            for e in self.positive_eigenarten:
                auswahl_text = ""
                if e.get('optionen', {}).get('ausgewaehlt'):
                    auswahl_text = f" → {e['optionen']['ausgewaehlt']}"
                summary += f"  • {e.get('name', e.get('id'))} [{e.get('kosten', 0)} EP]{auswahl_text}\n"
        else:
            summary += "[b]Positive Abstammungseigenarten:[/b] Keine\n"

        summary += "\n"

        if self.negative_eigenarten:
            summary += f"[b]Negative Abstammungseigenarten ({len(self.negative_eigenarten)}):[/b]\n"
            for e in self.negative_eigenarten:
                auswahl_text = ""
                if e.get('optionen', {}).get('ausgewaehlt'):
                    auswahl_text = f" → {e['optionen']['ausgewaehlt']}"
                summary += f"  • {e.get('name', e.get('id'))} [{e.get('kosten', 0)} EP]{auswahl_text}\n"
        else:
            summary += "[b]Negative Abstammungseigenarten:[/b] Keine\n"
        
        return summary
    
    def _update_name(self, instance, value):
        self.wizard_data['name'] = value
    
    def _update_beschreibung(self, instance, value):
        self.wizard_data['beschreibung'] = value
    
    def _toggle_eigenart(self, eigenart_id, eigenart_typ, active, checkbox=None):
        """Toggle eine Eigenart-Auswahl. Bei Eigenarten mit Optionen wird ein Zwischen-Dialog gezeigt.
        Für Mehrfachauswahl (max_auswahl != 1) wird diese Methode nicht verwendet - dafür
        gibt es _increment_eigenart und _decrement_eigenart."""
        volle_eigenart = get_eigenart_by_id(eigenart_id, eigenart_typ)
        if not volle_eigenart:
            return

        if eigenart_typ == 'positive':
            liste = self.positive_eigenarten
        else:
            liste = self.negative_eigenarten

        if active:
            if eigenart_id not in [e.get('id') for e in liste]:
                eigenart_copy = dict(volle_eigenart)
                if 'optionen' in eigenart_copy:
                    eigenart_copy['optionen'] = dict(eigenart_copy['optionen'])

                if eigenart_copy.get('stufen') or eigenart_copy.get('optionen'):
                    self._show_optionen_dialog(eigenart_copy, liste, checkbox)
                else:
                    liste.append(eigenart_copy)
        else:
            self._remove_eigenart(eigenart_id, liste)

    def _increment_eigenart(self, eigenart_id, eigenart_typ):
        """Fügt eine weitere Instanz der Eigenart hinzu (für Mehrfachauswahl).
        Zeigt den Optionen-Dialog falls nötig."""
        volle_eigenart = get_eigenart_by_id(eigenart_id, eigenart_typ)
        if not volle_eigenart:
            return

        if eigenart_typ == 'positive':
            liste = self.positive_eigenarten
        else:
            liste = self.negative_eigenarten

        aktuelle_anzahl = sum(1 for e in liste if e.get('id') == eigenart_id)
        max_auswahl = volle_eigenart.get('max_auswahl', 1)

        if max_auswahl != 0 and aktuelle_anzahl >= max_auswahl:
            return

        eigenart_copy = dict(volle_eigenart)
        if 'optionen' in eigenart_copy:
            eigenart_copy['optionen'] = dict(eigenart_copy['optionen'])

        if eigenart_copy.get('stufen') or eigenart_copy.get('optionen'):
            self._show_optionen_dialog(eigenart_copy, liste, None)
        else:
            liste.append(eigenart_copy)

    def _decrement_eigenart(self, eigenart_id, eigenart_typ):
        """Entfernt eine Instanz der Eigenart (für Mehrfachauswahl)."""
        if eigenart_typ == 'positive':
            liste = self.positive_eigenarten
        else:
            liste = self.negative_eigenarten

        self._remove_eigenart(eigenart_id, liste)

    def _on_eigenart_checkbox_clicked(self, eigenart_id, eigenart_typ, checkbox):
        """Handler für Checkbox-Klick mit Debounce."""
        now = time.monotonic()
        if hasattr(self, '_last_eigenart_toggle_time') and (now - self._last_eigenart_toggle_time) < 0.5:
            return
        self._last_eigenart_toggle_time = now
        self._toggle_eigenart(eigenart_id, eigenart_typ, checkbox.active, checkbox=checkbox)

    def _on_stepper_plus(self, eigenart_id, eigenart_typ):
        """Handler für Stepper +-Button mit Debounce."""
        now = time.monotonic()
        if hasattr(self, '_last_stepper_time') and (now - self._last_stepper_time) < 0.5:
            return
        self._last_stepper_time = now
        self._increment_eigenart(eigenart_id, eigenart_typ)
        self._refresh_stepper_in_place(eigenart_id, eigenart_typ)

    def _on_stepper_minus(self, eigenart_id, eigenart_typ):
        """Handler für Stepper --Button mit Debounce."""
        now = time.monotonic()
        if hasattr(self, '_last_stepper_time') and (now - self._last_stepper_time) < 0.5:
            return
        self._last_stepper_time = now
        self._decrement_eigenart(eigenart_id, eigenart_typ)
        self._refresh_stepper_in_place(eigenart_id, eigenart_typ)

    def _refresh_stepper_in_place(self, eigenart_id, eigenart_typ):
        """Aktualisiert Stepper-Widgets direkt via Widget-Tracking."""
        if not hasattr(self, '_stepper_widgets') or eigenart_id not in self._stepper_widgets:
            return
        aktuelle_auswahl = self.positive_eigenarten if eigenart_typ == 'positive' else self.negative_eigenarten
        neue_anzahl = sum(1 for e in aktuelle_auswahl if e.get('id') == eigenart_id)
        widget_data = self._stepper_widgets[eigenart_id]
        max_auswahl = widget_data['max_auswahl']
        list_item = widget_data['item']
        stepper_box = widget_data['box']
        minus_btn = widget_data['minus']
        count_lbl = widget_data['count']
        plus_btn = widget_data['plus']

        count_lbl.text = str(neue_anzahl)

        is_zero = (neue_anzahl == 0)
        minus_btn.disabled = is_zero
        minus_btn.background_color = (0.4, 0.4, 0.4, 1) if is_zero else (0.2, 0.5, 0.8, 1)

        is_maxed = (max_auswahl != 0 and neue_anzahl >= max_auswahl)
        plus_btn.disabled = is_maxed
        plus_btn.background_color = (0.4, 0.4, 0.4, 1) if is_maxed else (0.2, 0.7, 0.3, 1)

        # Max-Text im Headline aktualisieren
        headline = list_item.children[1] if len(list_item.children) > 1 else None
        if isinstance(headline, MDListItemHeadlineText):
            eigenart = get_eigenart_by_id(eigenart_id, eigenart_typ)
            if eigenart:
                stufen_bereich = stufen_kosten_bereich(eigenart)
                if stufen_bereich:
                    min_k, max_k = stufen_bereich
                    kosten_text = f" [{min_k} EP]" if min_k == max_k else f" [{min_k}–{max_k} EP]"
                else:
                    k = eigenart.get('kosten', 2)
                    kosten_text = f" [{k} EP]"
                if max_auswahl > 1:
                    max_text = f" ({neue_anzahl}/{max_auswahl})"
                else:
                    max_text = ""
                if eigenart.get('custom'):
                    max_text += " [Eigene]"
                headline.text = f"{eigenart.get('name', eigenart_id)}{kosten_text}{max_text}"

        list_layout = list_item.parent
        if list_layout and hasattr(list_layout, 'reset_property'):
            try:
                list_layout.reset_property('height')
            except Exception:
                pass

    def _show_optionen_dialog(self, eigenart, liste, checkbox=None):
        """Zeigt einen Zwischen-Dialog fuer Eigenart-Optionen (Stufen, Attribut-/Fertigkeits-Auswahl, Texteingabe).
        Blendet das Eigenarten-Popup temporär aus um Überlappung zu vermeiden.
        Wenn optionen.auswahl_verzoegert=true, wird die Auswahl verzögert - die Eigenart wird
        nur zur Liste hinzugefügt, die eigentliche Auswahl (Attribut, Fertigkeit, etc.)
        erfolgt später im Völker-Tab bei der Zuweisung des Volkes zum Charakter."""
        optionen = eigenart.get('optionen', {})
        typ = optionen.get('typ', '')
        eigenart_name = eigenart.get('name', eigenart.get('id', ''))

        # Auswahl verzögern? Dann Eigenart nur hinzufügen, keine weiteren Dialoge
        if optionen.get('auswahl_verzoegert'):
            liste.append(eigenart)
            if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
                self._eigenarten_popup.opacity = 1
            return

        # Eigenarten-Popup temporär ausblenden um Überlappung zu vermeiden
        if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
            self._eigenarten_popup.opacity = 0

        def _on_cancel(dialog_ref):
            """Abbrechen: Checkbox zuruecksetzen, Eigenart nicht hinzuzuegen."""
            dialog_ref.dismiss()
            if checkbox:
                checkbox.active = False

        # Stufen-Eigenart hat Vorrang: erst Stufe wählen, dann ggf. weitere Optionen
        if eigenart.get('stufen'):
            self._show_stufen_dialog(eigenart, liste, checkbox, eigenart_name)
        elif typ == 'text_eingabe':
            self._show_text_optionen_dialog(eigenart, liste, checkbox, optionen, eigenart_name)
        elif typ == 'talent_auswahl':
            self._show_talent_optionen_dialog(eigenart, liste, checkbox, optionen, eigenart_name)
        elif typ == 'macht_auswahl':
            self._show_macht_optionen_dialog(eigenart, liste, checkbox, optionen, eigenart_name)
        elif typ == 'talent_rang_auswahl':
            self._show_talent_rang_optionen_dialog(eigenart, liste, checkbox, optionen, eigenart_name)
        elif typ == 'superkraft_auswahl':
            self._show_superkraft_optionen_dialog(eigenart, liste, checkbox, optionen, eigenart_name)
        elif typ in ('attribut_auswahl', 'grundfertigkeit_auswahl', 'nicht_grundfertigkeit_auswahl',
                     'magieaffin_auswahl'):
            self._show_liste_optionen_dialog(eigenart, liste, checkbox, optionen, typ, eigenart_name)
        else:
            # Unbekannter Typ - einfach hinzufuegen
            liste.append(eigenart)
            # Eigenarten-Popup wieder einblenden
            if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
                self._eigenarten_popup.opacity = 1

    def _restore_eigenarten_popup(self):
        """Blendet das Eigenarten-Popup nach Schließen eines Unter-Dialogs wieder ein.
        Das Popup wird bei Bedarf komplett neu aufgebaut um Stepper-Zähler zu aktualisieren."""
        if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
            popup_typ = getattr(self, '_eigenarten_popup_typ', None)
            self._eigenarten_popup.dismiss()
            if popup_typ:
                Clock.schedule_once(lambda dt: self._show_eigenarten_popup(popup_typ), 0.15)

    def _refresh_eigenarten_popup(self, eigenart_typ):
        """Schließt das Eigenarten-Popup und öffnet es neu mit aktualisierten Daten."""
        if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
            self._eigenarten_popup.dismiss()
            Clock.schedule_once(lambda dt: self._show_eigenarten_popup(eigenart_typ), 0.3)

    def _show_text_optionen_dialog(self, eigenart, liste, checkbox, optionen, eigenart_name):
        """Dialog mit Texteingabe fuer Eigenart-Optionen (z.B. Immunität, Abhängigkeit)."""
        platzhalter = optionen.get('platzhalter', 'Eingabe...')
        beschreibung = optionen.get('beschreibung', '')

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, adaptive_height=True)

        if beschreibung:
            content.add_widget(MDLabel(
                text=beschreibung,
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(24)
            ))

        text_field = MDTextField(size_hint_x=1)
        text_field.add_widget(MDTextFieldHintText(text=platzhalter))
        content.add_widget(text_field)

        def _on_confirm(x):
            wert = text_field.text.strip()
            if not wert:
                return
            eigenart['optionen']['ausgewaehlt'] = wert
            liste.append(eigenart)
            dialog.dismiss()
            self._restore_eigenarten_popup()

        def _on_cancel(x):
            dialog.dismiss()
            self._restore_eigenarten_popup()
            if checkbox:
                checkbox.active = False

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"{eigenart_name} — Auswahl"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text", on_release=_on_cancel),
                MDButton(MDButtonText(text="Bestätigen"), style="filled", on_release=_on_confirm),
            ),
            size_hint=(0.85, None),
        )
        dialog.open()

    def _show_talent_optionen_dialog(self, eigenart, liste, checkbox, optionen, eigenart_name):
        """Dialog zur Auswahl eines freien Talents für Volkseigenart mit Filter-Toggle und Warn-Icons."""
        import time
        from kivy.core.window import Window
        
        from functions.volk_funktionen import get_freie_talente
        
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            charakter = app.controller.charakter
        except Exception:
            Logger.warning("Kein Charakter für Talent-Auswahl gefunden")
            liste.append(eigenart)
            return
        
        # Talente mit aktuellem Filter laden
        talente = get_freie_talente(charakter, nur_verfuegbare=self._filter_nur_verfuegbar)
        if not talente or (len(talente) == 1 and "Keine" in talente[0]):
            Logger.warning("Keine freien Talente verfügbar für Volkseigenart")
            liste.append(eigenart)
            return
        
        beschreibung = optionen.get('beschreibung', 'Wähle ein freies Anfängertalent:')
        standard = optionen.get('standard', talente[0] if talente else None)
        selected = [standard]
        self._last_talent_click = 0

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            padding=[dp(16), dp(8), dp(16), dp(8)]
        )

        # Header mit Titel und Filter-Button
        header_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8),
            padding=[0, 0, 0, 0]
        )
        title_label = MDLabel(
            text=beschreibung,
            font_style="Body",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(48),
            size_hint_x=0.85,
            halign="left",
            valign="center"
        )
        header_box.add_widget(title_label)
        
        # Filter-Toggle-Button
        from kivymd.uix.button import MDIconButton
        self._filter_btn = MDIconButton(
            icon="filter" if self._filter_nur_verfuegbar else "filter-off",
            style="tonal" if self._filter_nur_verfuegbar else "outlined",
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={"center_y": 0.5}
        )
        # Debounce für Android
        btn = self._filter_btn
        self._filter_btn.bind(on_release=lambda x, btn=btn: self._on_filter_toggle_talent(btn))
        header_box.add_widget(self._filter_btn)
        
        content.add_widget(header_box)

        # Suchfeld
        search_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(56)
        )
        search_field.add_widget(MDTextFieldHintText(text="Talent suchen..."))
        content.add_widget(search_field)

        # Höhenberechnung für ScrollView
        content_fixed = dp(48) + dp(56) + dp(32)  # Header + Suchfeld + Spacing/Padding
        dialog_chrome = dp(160)  # Headline + Buttons + internes Padding
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
        radio_checkboxes = {}

        def populate_talents(*args):
            talent_list.clear_widgets()
            radio_checkboxes.clear()
            search_text = search_field.text.lower() if search_field.text else ""
            # Talente mit aktuellem Filter neu laden
            aktuell_talente = get_freie_talente(charakter, nur_verfuegbare=self._filter_nur_verfuegbar)
            for talent_name in sorted(aktuell_talente):
                if not talent_name or not str(talent_name).strip():
                    continue
                if search_text and search_text not in str(talent_name).lower():
                    continue

                list_item = MDListItem(
                    size_hint_y=None,
                    height=dp(56) if _mobile else dp(48)
                )
                
                # Warnicon wenn Voraussetzungen nicht erfüllt (nur bei "Alle anzeigen")
                if not self._filter_nur_verfuegbar:
                    talent_obj = charakter.talente.get(talent_name)
                    if talent_obj:
                        if not pruefe_voraussetzungen(charakter, talent_obj) or is_talent_rang_hoeher_als_charakter(charakter, talent_obj.rang):
                            from kivymd.uix.label import MDIcon
                            warn_icon = MDIcon(
                                icon="alert-circle-outline",
                                theme_text_color="Error",
                                size_hint=(None, None),
                                size=(dp(24), dp(24)),
                                pos_hint={"center_y": 0.5}
                            )
                            list_item.add_widget(warn_icon)
                
                list_item.add_widget(MDListItemHeadlineText(text=str(talent_name)))
                
                radio_cb = MDListItemTrailingCheckbox(
                    active=(talent_name == selected[0]),
                    group=f"optionen_{eigenart.get('id', '')}"
                )
                r_cb = radio_cb
                i_name = talent_name
                list_item.bind(on_release=lambda x, name=i_name: self._select_talent_option(name, selected, radio_checkboxes))
                radio_cb.bind(on_release=lambda x, cb=r_cb, name=i_name: self._on_talent_radio_clicked(name, selected, radio_checkboxes, cb))
                list_item.add_widget(radio_cb)
                talent_list.add_widget(list_item)
                radio_checkboxes[talent_name] = radio_cb
        
        # Für Filter-Button zugreifbar machen
        self._populate_talents_func = populate_talents

        search_field.bind(text=populate_talents)
        populate_talents()

        scroll.add_widget(talent_list)
        content.add_widget(scroll)
        content.height = content_fixed + scroll_height

        dialog_height = min(content.height + dialog_chrome, max_dialog_height)
        
        def _on_confirm(x):
            if selected[0]:
                eigenart['optionen']['ausgewaehlt'] = selected[0]
                liste.append(eigenart)
                dialog.dismiss()
                self._restore_eigenarten_popup()
                Logger.info(f"Freies Talent '{selected[0]}' für Volkseigenart gewählt")

        def _on_cancel(x):
            dialog.dismiss()
            self._restore_eigenarten_popup()
            if checkbox:
                checkbox.active = False

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"{eigenart_name} — Talent wählen"),
            MDDialogContentContainer(content, orientation="vertical"),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text", on_release=_on_cancel),
                MDButton(MDButtonText(text="Bestätigen"), style="filled", on_release=_on_confirm),
            ),
            size_hint=(0.85, None),
            height=dialog_height,
        )
        dialog.open()
    
    def _on_filter_toggle_talent(self, button):
        """Toggle-Filter für 'nur verfügbare Talente' mit Debounce."""
        now = time.monotonic()
        if hasattr(self, '_last_filter_toggle') and (now - self._last_filter_toggle) < 0.5:
            return
        self._last_filter_toggle = now
        
        self._filter_nur_verfuegbar = not self._filter_nur_verfuegbar
        button.icon = "filter" if self._filter_nur_verfuegbar else "filter-off"
        button.style = "tonal" if self._filter_nur_verfuegbar else "outlined"
        Logger.debug(f"Filter umgeschaltet auf nur_verfuegbar={self._filter_nur_verfuegbar}")
        
        # Talentliste neu aufbauen
        if hasattr(self, '_populate_talents_func'):
            self._populate_talents_func()
    
    def _select_talent_option(self, name, selected, radio_checkboxes):
        """Wählt eine Option in der Radio-Liste aus (Klick auf ListItem)."""
        selected[0] = name
        for item_name, cb in radio_checkboxes.items():
            cb.active = (item_name == name)

    def _on_talent_radio_clicked(self, name, selected, radio_checkboxes, clicked_cb):
        """Handler für Talent-Radio-Checkbox Klick mit Debounce."""
        now = time.monotonic()
        if hasattr(self, '_last_talent_click') and (now - self._last_talent_click) < 0.5:
            return
        self._last_talent_click = now
        self._select_talent_option(name, selected, radio_checkboxes)

    def _show_liste_optionen_dialog(self, eigenart, liste, checkbox, optionen, typ, eigenart_name):
        """Dialog mit Auswahlliste fuer Eigenart-Optionen (Attribute, Fertigkeiten)."""
        # Auswahl-Items bestimmen
        if typ == 'attribut_auswahl':
            items = optionen.get('attribute', ['Stärke', 'Geschicklichkeit', 'Konstitution', 'Verstand', 'Willenskraft'])
        elif typ == 'grundfertigkeit_auswahl':
            items = optionen.get('fertigkeiten', ['Athletik', 'Heimlichkeit', 'Überreden', 'Wahrnehmung', 'Allgemeinwissen'])
        elif typ == 'nicht_grundfertigkeit_auswahl':
            items = self._get_nicht_grundfertigkeiten()
        else:
            items = []

        if not items:
            liste.append(eigenart)
            return

        standard = optionen.get('standard', items[0] if items else None)
        selected = [standard]

        content = MDBoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None, height=dp(min(len(items) * 56, 300)))

        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        if _mobile:
            list_layout.padding = [0, 0, dp(32), 0]
        radio_checkboxes = {}

        for item_name in items:
            list_item = MDListItem(size_hint_y=None, height=dp(56) if _mobile else dp(48))
            list_item.add_widget(MDListItemHeadlineText(text=item_name))
            radio_cb = MDListItemTrailingCheckbox(
                active=(item_name == standard),
                group=f"optionen_{eigenart.get('id', '')}"
            )
            r_cb = radio_cb
            i_name = item_name
            list_item.bind(on_release=lambda x, name=i_name: self._select_option(name, selected, radio_checkboxes))
            radio_cb.bind(on_release=lambda x, cb=r_cb, name=i_name: self._on_option_radio_clicked(name, selected, radio_checkboxes, cb))
            list_item.add_widget(radio_cb)
            list_layout.add_widget(list_item)
            radio_checkboxes[item_name] = radio_cb

        scroll = MDScrollView(size_hint_y=1, bar_width=dp(20) if _mobile else dp(15), bar_margin=dp(8) if _mobile else dp(4))
        if _mobile:
            scroll.scroll_type = ['bars', 'content']
        scroll.add_widget(list_layout)
        content.add_widget(scroll)

        def _on_confirm(x):
            if selected[0]:
                eigenart['optionen']['ausgewaehlt'] = selected[0]
                liste.append(eigenart)
                dialog.dismiss()
                self._restore_eigenarten_popup()

        def _on_cancel(x):
            dialog.dismiss()
            self._restore_eigenarten_popup()
            if checkbox:
                checkbox.active = False

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"{eigenart_name} — Auswahl"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text", on_release=_on_cancel),
                MDButton(MDButtonText(text="Bestätigen"), style="filled", on_release=_on_confirm),
            ),
            size_hint=(0.85, None),
        )
        dialog.open()

    def _select_option(self, name, selected, radio_checkboxes):
        """Wählt eine Option in der Radio-Liste aus (Klick auf ListItem)."""
        selected[0] = name
        for item_name, cb in radio_checkboxes.items():
            cb.active = (item_name == name)

    def _on_option_radio_clicked(self, name, selected, radio_checkboxes, clicked_cb):
        """Handler fuer Radio-Checkbox Klick mit Debounce."""
        now = time.monotonic()
        if hasattr(self, '_last_option_radio_time') and (now - self._last_option_radio_time) < 0.5:
            return
        self._last_option_radio_time = now
        self._select_option(name, selected, radio_checkboxes)

    def _show_stufen_dialog(self, eigenart, liste, checkbox, eigenart_name):
        """Dialog zur Auswahl einer Stufe einer Stufen-Eigenart (z.B. Fliegen 2/4/6 EP).
        Übernimmt nach Bestätigung kosten und effekt aus der gewählten Stufe."""
        stufen = eigenart.get('stufen') or []
        if not stufen:
            liste.append(eigenart)
            self._restore_eigenarten_popup()
            return

        # Vorauswahl: wenn die Eigenart bereits eine Stufe trägt, diese vorselektieren
        vorhandene = eigenart.get('ausgewaehlte_stufe') or {}
        standard_index = 0
        for i, s in enumerate(stufen):
            if vorhandene.get('label') and s.get('label') == vorhandene.get('label'):
                standard_index = i
                break
            if vorhandene.get('kosten') is not None and s.get('kosten') == vorhandene.get('kosten'):
                standard_index = i
                break

        selected_index = [standard_index]

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
            height=dp(min(len(stufen) * 64, 320)),
        )

        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        if _mobile:
            list_layout.padding = [0, 0, dp(32), 0]
        radio_checkboxes = {}

        for index, stufe in enumerate(stufen):
            label = stufe.get('label', f"Stufe {index + 1}")
            kosten = stufe.get('kosten', 0)
            zeile_text = f"{label}  ·  {kosten} EP"

            list_item = MDListItem(size_hint_y=None, height=dp(64) if _mobile else dp(56))
            list_item.add_widget(MDListItemHeadlineText(text=zeile_text))
            radio_cb = MDListItemTrailingCheckbox(
                active=(index == standard_index),
                group=f"stufen_{eigenart.get('id', '')}"
            )
            r_cb = radio_cb
            i = index
            list_item.bind(on_release=lambda x, idx=i: self._select_stufe(idx, stufen, selected_index, radio_checkboxes))
            radio_cb.bind(on_release=lambda x, cb=r_cb, idx=i: self._on_stufe_radio_clicked(idx, stufen, selected_index, radio_checkboxes, cb))
            list_item.add_widget(radio_cb)
            list_layout.add_widget(list_item)
            radio_checkboxes[index] = radio_cb

        scroll = MDScrollView(size_hint_y=1, bar_width=dp(20) if _mobile else dp(15), bar_margin=dp(8) if _mobile else dp(4))
        if _mobile:
            scroll.scroll_type = ['bars', 'content']
        scroll.add_widget(list_layout)
        content.add_widget(scroll)

        def _on_confirm(x):
            chosen_idx = selected_index[0]
            if chosen_idx is None or chosen_idx < 0 or chosen_idx >= len(stufen):
                return
            wende_stufe_an(eigenart, stufen[chosen_idx])
            dialog.dismiss()
            # Hat die Eigenart zusätzlich Optionen? → Optionen-Dialog anschließen
            optionen = eigenart.get('optionen', {})
            opt_typ = optionen.get('typ', '')
            if opt_typ == 'text_eingabe':
                self._show_text_optionen_dialog(eigenart, liste, checkbox, optionen, eigenart_name)
            elif opt_typ == 'talent_auswahl':
                self._show_talent_optionen_dialog(eigenart, liste, checkbox, optionen, eigenart_name)
            elif opt_typ in ('attribut_auswahl', 'grundfertigkeit_auswahl', 'nicht_grundfertigkeit_auswahl'):
                self._show_liste_optionen_dialog(eigenart, liste, checkbox, optionen, opt_typ, eigenart_name)
            else:
                liste.append(eigenart)
                self._restore_eigenarten_popup()

        def _on_cancel(x):
            dialog.dismiss()
            self._restore_eigenarten_popup()
            if checkbox:
                checkbox.active = False

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"{eigenart_name} — Stufe wählen"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text", on_release=_on_cancel),
                MDButton(MDButtonText(text="Bestätigen"), style="filled", on_release=_on_confirm),
            ),
            size_hint=(0.85, None),
        )
        dialog.open()

    def _select_stufe(self, index, stufen, selected_index, radio_checkboxes):
        """Wählt eine Stufe in der Radio-Liste aus."""
        if index < 0 or index >= len(stufen):
            return
        selected_index[0] = index
        for i, cb in radio_checkboxes.items():
            cb.active = (i == index)

    def _on_stufe_radio_clicked(self, index, stufen, selected_index, radio_checkboxes, clicked_cb):
        """Handler für Stufen-Radio-Checkbox Klick mit Debounce (Android Touch-Bounce)."""
        now = time.monotonic()
        if hasattr(self, '_last_stufe_radio_time') and (now - self._last_stufe_radio_time) < 0.5:
            return
        self._last_stufe_radio_time = now
        self._select_stufe(index, stufen, selected_index, radio_checkboxes)

    def _get_nicht_grundfertigkeiten(self):
        """Lädt Nicht-Grundfertigkeiten aus dem aktiven Setting des Charakters."""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            if app and hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                grundfertigkeiten = {'Allgemeinwissen', 'Athletik', 'Heimlichkeit', 'Überreden', 'Wahrnehmung'}
                alle_fertigkeiten = []
                for fert in charakter.fertigkeiten:
                    if fert.fertigkeit_name not in grundfertigkeiten:
                        alle_fertigkeiten.append(fert.fertigkeit_name)
                if alle_fertigkeiten:
                    return sorted(alle_fertigkeiten)
        except Exception as e:
            Logger.warning(f"volk_popup: Fehler beim Laden der Fertigkeiten: {e}")
        # Fallback: Häufige SWAE Nicht-Grundfertigkeiten
        return ['Kämpfen', 'Schießen', 'Heilung', 'Einschüchtern', 'Provozieren',
                'Reparieren', 'Recherche', 'Reiten', 'Steuern', 'Überleben', 'Zaubern']

    def _show_macht_optionen_dialog(self, eigenart, liste, checkbox, optionen, eigenart_name):
        """Dialog zur Auswahl einer Macht für volk_macht."""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            charakter = app.controller.charakter
        except Exception:
            Logger.warning("Kein Charakter für Macht-Auswahl gefunden")
            liste.append(eigenart)
            return

        all_maechte = getattr(charakter, 'maechte', {})
        if not all_maechte:
            Logger.warning("Keine Mächte verfügbar")
            liste.append(eigenart)
            return

        items = sorted(all_maechte.keys())
        standard = items[0] if items else None
        selected = [standard]

        content = MDBoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None, height=dp(min(len(items) * 56, 300)))

        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        if _mobile:
            list_layout.padding = [0, 0, dp(32), 0]
        radio_checkboxes = {}

        for item_name in items:
            list_item = MDListItem(size_hint_y=None, height=dp(56) if _mobile else dp(48))
            list_item.add_widget(MDListItemHeadlineText(text=item_name))
            radio_cb = MDListItemTrailingCheckbox(
                active=(item_name == standard),
                group=f"optionen_{eigenart.get('id', '')}"
            )
            r_cb = radio_cb
            i_name = item_name
            list_item.bind(on_release=lambda x, name=i_name: self._select_option(name, selected, radio_checkboxes))
            radio_cb.bind(on_release=lambda x, cb=r_cb, name=i_name: self._on_option_radio_clicked(name, selected, radio_checkboxes, cb))
            list_item.add_widget(radio_cb)
            list_layout.add_widget(list_item)
            radio_checkboxes[item_name] = radio_cb

        scroll = MDScrollView(size_hint_y=1, bar_width=dp(20) if _mobile else dp(15), bar_margin=dp(8) if _mobile else dp(4))
        if _mobile:
            scroll.scroll_type = ['bars', 'content']
        scroll.add_widget(list_layout)
        content.add_widget(scroll)

        def _on_confirm(x):
            if selected[0]:
                eigenart['optionen']['ausgewaehlt'] = selected[0]
                liste.append(eigenart)
                dialog.dismiss()
                self._restore_eigenarten_popup()

        def _on_cancel(x):
            dialog.dismiss()
            self._restore_eigenarten_popup()
            if checkbox:
                checkbox.active = False

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"{eigenart_name} — Macht wählen"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text", on_release=_on_cancel),
                MDButton(MDButtonText(text="Bestätigen"), style="filled", on_release=_on_confirm),
            ),
            size_hint=(0.85, None),
        )
        dialog.open()

    def _show_talent_rang_optionen_dialog(self, eigenart, liste, checkbox, optionen, eigenart_name):
        """Dialog zur Auswahl eines Talents mit Rang für volk_talent."""
        from functions.volk_funktionen import get_freie_talente

        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            charakter = app.controller.charakter
        except Exception:
            Logger.warning("Kein Charakter für Talent-Auswahl gefunden")
            liste.append(eigenart)
            return

        talente = get_freie_talente(charakter, nur_verfuegbare=False)
        if not talente or (len(talente) == 1 and "Keine" in talente[0]):
            Logger.warning("Keine Talente verfügbar für volk_talent")
            liste.append(eigenart)
            return

        beschreibung = optionen.get('beschreibung', 'Wähle ein Talent:')
        standard = talente[0] if talente else None
        selected_talent = [standard]
        selected_rang = [1]  # 0=Anfänger, 1=Erfahren, 2=Veteran, 3=Heroisch, 4=Held
        self._last_talent_click = 0

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            padding=[dp(16), dp(8), dp(16), dp(8)]
        )

        content.add_widget(MDLabel(
            text=beschreibung,
            font_style="Body",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(24)
        ))

        talent_items = sorted(talente)
        talent_list_layout = MDList(size_hint_y=None)
        talent_list_layout.bind(minimum_height=talent_list_layout.setter('height'))
        if _mobile:
            talent_list_layout.padding = [0, 0, dp(32), 0]
        talent_radio_checkboxes = {}

        for t_name in talent_items:
            list_item = MDListItem(size_hint_y=None, height=dp(56) if _mobile else dp(48))
            list_item.add_widget(MDListItemHeadlineText(text=t_name))
            radio_cb = MDListItemTrailingCheckbox(
                active=(t_name == standard),
                group=f"talent_{eigenart.get('id', '')}"
            )
            r_cb = radio_cb
            t = t_name
            list_item.bind(on_release=lambda x, name=t: self._select_talent_rang_option(name, selected_talent, talent_radio_checkboxes))
            radio_cb.bind(on_release=lambda x, cb=r_cb, name=t: self._on_talent_radio_clicked(name, selected_talent, talent_radio_checkboxes, cb))
            list_item.add_widget(radio_cb)
            talent_list_layout.add_widget(list_item)
            talent_radio_checkboxes[t_name] = radio_cb

        talent_scroll = MDScrollView(size_hint_y=1, bar_width=dp(20) if _mobile else dp(15), bar_margin=dp(8) if _mobile else dp(4))
        if _mobile:
            talent_scroll.scroll_type = ['bars', 'content']
        talent_scroll.add_widget(talent_list_layout)
        content.add_widget(talent_scroll)

        rang_label = MDLabel(
            text="Rang:",
            font_style="Body",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(24)
        )
        content.add_widget(rang_label)

        rang_items = ["Anfänger", "Erfahren", "Veteran", "Heroisch", "Held"]
        rang_list_layout = MDList(size_hint_y=None)
        rang_list_layout.bind(minimum_height=rang_list_layout.setter('height'))
        rang_radio_checkboxes = {}

        for idx, rang_name in enumerate(rang_items):
            list_item = MDListItem(size_hint_y=None, height=dp(48))
            list_item.add_widget(MDListItemHeadlineText(text=rang_name))
            radio_cb = MDListItemTrailingCheckbox(
                active=(idx == 1),
                group=f"rang_{eigenart.get('id', '')}"
            )
            r_cb = radio_cb
            i = idx
            list_item.bind(on_release=lambda x, index=i: self._select_rang_option(index, selected_rang, rang_radio_checkboxes))
            radio_cb.bind(on_release=lambda x, cb=r_cb, index=i: self._on_rang_radio_clicked(index, selected_rang, rang_radio_checkboxes, cb))
            list_item.add_widget(radio_cb)
            rang_list_layout.add_widget(list_item)
            rang_radio_checkboxes[idx] = radio_cb

        rang_scroll = MDScrollView(size_hint_y=None, bar_width=dp(15), bar_margin=dp(4), height=dp(150))
        rang_scroll.add_widget(rang_list_layout)
        content.add_widget(rang_scroll)

        def _on_confirm(x):
            eigenart['optionen']['ausgewaehlt'] = selected_talent[0]
            eigenart['optionen']['rang'] = selected_rang[0]
            eigenart['kosten'] = 2 + selected_rang[0]
            liste.append(eigenart)
            dialog.dismiss()
            self._restore_eigenarten_popup()

        def _on_cancel(x):
            dialog.dismiss()
            self._restore_eigenarten_popup()
            if checkbox:
                checkbox.active = False

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"{eigenart_name} — Talent & Rang"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text", on_release=_on_cancel),
                MDButton(MDButtonText(text="Bestätigen"), style="filled", on_release=_on_confirm),
            ),
            size_hint=(0.85, None),
        )
        dialog.open()

    def _select_talent_rang_option(self, name, selected, radio_checkboxes):
        selected[0] = name
        for item_name, cb in radio_checkboxes.items():
            cb.active = (item_name == name)

    def _on_talent_radio_clicked(self, name, selected, radio_checkboxes, clicked_cb):
        now = time.monotonic()
        if hasattr(self, '_last_option_radio_time') and (now - self._last_option_radio_time) < 0.5:
            return
        self._last_option_radio_time = now
        self._select_talent_rang_option(name, selected, radio_checkboxes)

    def _select_rang_option(self, index, selected_rang, radio_checkboxes):
        selected_rang[0] = index
        for idx, cb in radio_checkboxes.items():
            cb.active = (idx == index)

    def _on_rang_radio_clicked(self, index, selected_rang, radio_checkboxes, clicked_cb):
        now = time.monotonic()
        if hasattr(self, '_last_option_radio_time') and (now - self._last_option_radio_time) < 0.5:
            return
        self._last_option_radio_time = now
        self._select_rang_option(index, selected_rang, radio_checkboxes)

    def _show_superkraft_optionen_dialog(self, eigenart, liste, checkbox, optionen, eigenart_name):
        """Dialog zur Auswahl einer Superkraft für volk_superkraft."""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            charakter = app.controller.charakter
        except Exception:
            Logger.warning("Kein Charakter für Superkraft-Auswahl gefunden")
            liste.append(eigenart)
            return

        alle_kraefte = getattr(charakter, 'superkraefte', {})
        if not alle_kraefte:
            Logger.warning("Keine Superkräfte verfügbar")
            liste.append(eigenart)
            return

        items = sorted(alle_kraefte.keys())
        standard = items[0] if items else None
        selected = [standard]

        content = MDBoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None, height=dp(min(len(items) * 56, 300)))

        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        if _mobile:
            list_layout.padding = [0, 0, dp(32), 0]
        radio_checkboxes = {}

        for item_name in items:
            kraft = alle_kraefte[item_name]
            kosten = getattr(kraft, 'kosten', 0)
            zeile = f"{item_name} ({kosten} SKP)"
            list_item = MDListItem(size_hint_y=None, height=dp(56) if _mobile else dp(48))
            list_item.add_widget(MDListItemHeadlineText(text=zeile))
            radio_cb = MDListItemTrailingCheckbox(
                active=(item_name == standard),
                group=f"optionen_{eigenart.get('id', '')}"
            )
            r_cb = radio_cb
            i_name = item_name
            list_item.bind(on_release=lambda x, name=i_name: self._select_option(name, selected, radio_checkboxes))
            radio_cb.bind(on_release=lambda x, cb=r_cb, name=i_name: self._on_option_radio_clicked(name, selected, radio_checkboxes, cb))
            list_item.add_widget(radio_cb)
            list_layout.add_widget(list_item)
            radio_checkboxes[item_name] = radio_cb

        scroll = MDScrollView(size_hint_y=1, bar_width=dp(20) if _mobile else dp(15), bar_margin=dp(8) if _mobile else dp(4))
        if _mobile:
            scroll.scroll_type = ['bars', 'content']
        scroll.add_widget(list_layout)
        content.add_widget(scroll)

        def _on_confirm(x):
            if selected[0]:
                kraft = alle_kraefte.get(selected[0])
                kosten = getattr(kraft, 'kosten', 0) if kraft else 0
                eigenart['optionen']['ausgewaehlt'] = selected[0]
                eigenart['optionen']['punkte_kosten'] = kosten
                eigenart['kosten'] = 2 + kosten
                liste.append(eigenart)
                dialog.dismiss()
                self._restore_eigenarten_popup()

        def _on_cancel(x):
            dialog.dismiss()
            self._restore_eigenarten_popup()
            if checkbox:
                checkbox.active = False

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"{eigenart_name} — Superkraft wählen"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text", on_release=_on_cancel),
                MDButton(MDButtonText(text="Bestätigen"), style="filled", on_release=_on_confirm),
            ),
            size_hint=(0.85, None),
        )
        dialog.open()

    def _remove_eigenart(self, eigenart_id, liste):
        """Entfernt eine Eigenart aus der Liste"""
        for i, e in enumerate(liste):
            if e.get('id') == eigenart_id:
                liste.pop(i)
                break
    
    def _nav_debounce_check(self) -> bool:
        """Prüft ob ein Navigations-Event zu schnell hintereinander kommt (Android Touch-Bounce)."""
        # Flag-basierter Guard: verhindert doppelte Navigation während _show_current_step läuft
        if getattr(self, '_navigating', False):
            return False
        now = time.monotonic()
        if hasattr(self, '_last_nav_time') and (now - self._last_nav_time) < 0.5:
            return False
        self._last_nav_time = now
        return True

    def _next_step(self, *args):
        if not self._nav_debounce_check():
            return
        if self.current_step == 0:
            if not self.wizard_data.get('name', '').strip():
                self._show_error("Bitte gib einen Namen für die Abstammung ein.")
                return
        self.current_step += 1
        self._show_current_step()

    def _previous_step(self, *args):
        if not self._nav_debounce_check():
            return
        self.current_step -= 1
        self._show_current_step()

    def _cancel_wizard(self, *args):
        if not self._nav_debounce_check():
            return
        self._wizard_finished = True
        # Offenes Eigenarten-Popup schließen, falls noch vorhanden
        if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
            self._eigenarten_popup.dismiss()
            self._eigenarten_popup = None
        if self.dialog:
            self.dialog.dismiss()
        Logger.info("Volkseigenarten-Wizard abgebrochen")

    def _finish_wizard(self, *args):
        if not self._nav_debounce_check():
            return
        self._wizard_finished = True
        # Offenes Eigenarten-Popup schließen, falls noch vorhanden
        if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
            self._eigenarten_popup.dismiss()
            self._eigenarten_popup = None
        validation = validiere_volk_erstellung(
            self.wizard_data['name'],
            self.positive_eigenarten,
            self.negative_eigenarten
        )
        
        if not validation['ist_gueltig']:
            self._show_error("\n".join(validation['fehler']))
            return
        
        try:
            effects = eigenart_zu_effekte(self.positive_eigenarten, self.negative_eigenarten)
            besonderheiten = eigenart_zu_besonderheiten(self.positive_eigenarten, self.negative_eigenarten)
            
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            volk_name = self.wizard_data['name'].strip()
            
            if self.edit_volk:
                alter_name = self.edit_volk.name
                del charakter.voelker[alter_name]
                # Pro-Volk-Auswahlen unter altem Namen mitnehmen, falls Volk umbenannt wird
                self._renamed_from = alter_name
                Logger.info(f"Altes Volk '{alter_name}' für Bearbeitung entfernt")
            
            if volk_name in charakter.voelker:
                self._show_error(f"Abstammung '{volk_name}' existiert bereits.")
                return
            
            new_volk = Volk(
                name=volk_name,
                handicaps=[],
                talente=effects.get('auto_talente', []),
                besonderheiten=besonderheiten,
                custom=True,
                effects=effects
            )
            
            charakter.voelker[volk_name] = new_volk

            # Beim Editieren: bestehende Pro-Charakter-Auswahlen mit den neuen
            # Slot-Anzahlen abgleichen, damit reduzierte max_auswahl-Werte
            # überzählige Auswahlen sauber zurückrollen.
            if self.edit_volk:
                # Falls der Volk-Name geändert wurde, Auswahlen-Eintrag umbenennen
                alter_name = getattr(self, '_renamed_from', None)
                if alter_name and alter_name != volk_name and hasattr(charakter, 'voelker_auswahlen'):
                    if alter_name in charakter.voelker_auswahlen:
                        charakter.voelker_auswahlen[volk_name] = charakter.voelker_auswahlen.pop(alter_name)
                try:
                    from functions.volk_funktionen import reconcile_volk_auswahlen
                    counts = effects.get('wahlmoeglichkeiten_counts', {}) or {}
                    slot_targets = {
                        'talent':         counts.get('freies_talent', 0),
                        'attribut':       counts.get('freies_attribut', 0),
                        'attribut_malus': counts.get('freies_attribut_malus', 0),
                        'fertigkeit':     (counts.get('freie_grundfertigkeit', 0)
                                           + counts.get('freie_nicht_grundfertigkeit', 0)),
                    }
                    if hasattr(charakter, 'voelker_auswahlen'):
                        reconcile_volk_auswahlen(
                            charakter, volk_name, charakter.voelker_auswahlen, slot_targets
                        )
                except Exception as e:
                    Logger.warning(f"reconcile_volk_auswahlen fehlgeschlagen: {e}")

            if self.dialog:
                old_dialog = self.dialog
                self.dialog = None
                old_dialog.dismiss()

            self._show_success(f"Abstammung '{volk_name}' wurde {'aktualisiert' if self.edit_volk else 'erstellt'}.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            if self.callback:
                self.callback(volk_name, new_volk)

            Logger.info(f"Volk '{volk_name}' erfolgreich {'aktualisiert' if self.edit_volk else 'erstellt'}.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Volks: {e}")
            self._show_error(f"Fehler beim Speichern: {e}")
    
    def _show_freies_talent_popup(self, volk_name):
        """Zeigt separates Popup zur Auswahl eines freien Talents mit Filter-Toggle und Warn-Icons."""
        import time
        from kivy.core.window import Window
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            from functions.volk_funktionen import get_freie_talente, waehle_freies_talent, NO_TALENT_AVAILABLE_TEXT

            # Talente mit aktuellem Filter laden
            talente = get_freie_talente(charakter, nur_verfuegbare=self._filter_nur_verfuegbar)
            if not talente or talente == [NO_TALENT_AVAILABLE_TEXT]:
                Logger.warning("Keine freien Talente verfügbar")
                return

            self._talent_popup = None
            self._talent_selected = None
            self._last_talent_click = 0

            content = MDBoxLayout(
                orientation="vertical", spacing=dp(8),
                size_hint_y=None, padding=[dp(16), dp(8), dp(16), dp(8)]
            )
            content.bind(minimum_height=content.setter('height'))

            # Header mit Titel und Filter-Button
            header_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(48),
                spacing=dp(8),
                padding=[0, 0, 0, 0]
            )
            title_label = MDLabel(
                text=f"Abstammung '{volk_name}' hat ein freies Talent.\nBitte wähle ein Anfängertalent:",
                font_style="Body",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(48),
                size_hint_x=0.85,
                halign="left",
                valign="center"
            )
            header_box.add_widget(title_label)
            
            # Filter-Toggle-Button
            from kivymd.uix.button import MDIconButton
            self._filter_btn = MDIconButton(
                icon="filter" if self._filter_nur_verfuegbar else "filter-off",
                style="tonal" if self._filter_nur_verfuegbar else "outlined",
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                pos_hint={"center_y": 0.5}
            )
            # Debounce für Android
            btn = self._filter_btn
            self._filter_btn.bind(on_release=lambda x, btn=btn: self._on_filter_toggle_talent(btn))
            header_box.add_widget(self._filter_btn)
            
            content.add_widget(header_box)

            # Suchfeld
            search_field = MDTextField(mode="outlined", size_hint_y=None, height=dp(56))
            search_field.add_widget(MDTextFieldHintText(text="Talent suchen..."))
            content.add_widget(search_field)

            # Höhenberechnung für ScrollView
            content_fixed = dp(48) + dp(56) + dp(32)  # Header + Suchfeld + Spacing/Padding
            dialog_chrome = dp(160)  # Headline + Buttons + internes Padding
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

            def populate_talent_list(*args):
                talent_list.clear_widgets()
                search_text = search_field.text.lower() if search_field.text else ""
                # Talente mit aktuellem Filter neu laden
                aktuell_talente = get_freie_talente(charakter, nur_verfuegbare=self._filter_nur_verfuegbar)
                for talent_name in sorted(aktuell_talente):
                    if not talent_name or not str(talent_name).strip():
                        continue
                    if search_text and search_text not in str(talent_name).lower():
                        continue

                    list_item = MDListItem(
                        size_hint_y=None,
                        height=dp(56) if _mobile else dp(48)
                    )
                    
                    # Warnicon wenn Voraussetzungen nicht erfüllt (nur bei "Alle anzeigen")
                    if not self._filter_nur_verfuegbar:
                        talent_obj = charakter.talente.get(talent_name)
                        if talent_obj:
                            if not pruefe_voraussetzungen(charakter, talent_obj) or is_talent_rang_hoeher_als_charakter(charakter, talent_obj.rang):
                                from kivymd.uix.label import MDIcon
                                warn_icon = MDIcon(
                                    icon="alert-circle-outline",
                                    theme_text_color="Error",
                                    size_hint=(None, None),
                                    size=(dp(24), dp(24)),
                                    pos_hint={"center_y": 0.5}
                                )
                                list_item.add_widget(warn_icon)
                    
                    list_item.add_widget(MDListItemHeadlineText(text=str(talent_name)))
                    
                    # Auswahl-Hintergrund
                    is_sel = (self._talent_selected == talent_name)
                    if is_sel:
                        list_item.md_bg_color = app.theme_cls.primaryContainerColor
                    
                    t_name = talent_name
                    list_item.bind(on_release=lambda x, n=t_name: _select_talent(n))
                    talent_list.add_widget(list_item)
            
            # Für Filter-Button zugreifbar machen
            self._populate_talents_func = populate_talent_list

            def _select_talent(talent_name):
                now = time.monotonic()
                if now - self._last_talent_click < 0.5:
                    return
                self._last_talent_click = now
                self._talent_selected = talent_name
                populate_talent_list()

            def _confirm_talent(*args):
                now = time.monotonic()
                if now - self._last_talent_click < 0.5:
                    return
                self._last_talent_click = now
                if self._talent_selected:
                    result = waehle_freies_talent(charakter, volk_name, self._talent_selected)
                    if result == "needs_voraussetzungen_confirmation":
                        # Voraussetzungen nicht erfüllt -> Bestätigungsdialog zeigen
                        self._show_voraussetzungen_confirmation_dialog(volk_name, self._talent_selected, charakter)
                    elif result:
                        Logger.info(f"Freies Talent '{self._talent_selected}' für Volk '{volk_name}' gewählt")
                        # VoelkerWidget UI aktualisieren - Talent an die Multi-Slot-Liste anhängen.
                        # Schlüsselname 'talent' ist konsistent mit dem restlichen Völker-Tab.
                        try:
                            widget = app.get_widget_by_tab_text('Völker', 'voelker_widget')
                            if widget:
                                eintrag = widget.voelker_auswahlen.setdefault(volk_name, {})
                                aktuell = eintrag.get('talent')
                                if isinstance(aktuell, list):
                                    if self._talent_selected not in aktuell:
                                        aktuell.append(self._talent_selected)
                                else:
                                    eintrag['talent'] = (
                                        [aktuell, self._talent_selected]
                                        if aktuell and aktuell != self._talent_selected
                                        else [self._talent_selected]
                                    )
                                widget.aktualisiere_ui()
                        except Exception:
                            pass
                        if self._talent_popup:
                            self._talent_popup.dismiss()
                    else:
                        # Fehler (z.B. bereits gewählt)
                        from services.service_container import service_container
                        ds = service_container.get_dialog_service()
                        if ds:
                            ds.show_warning_dialog("Das Talent konnte nicht gewählt werden.")
                else:
                    from services.service_container import service_container
                    ds = service_container.get_dialog_service()
                    if ds:
                        ds.show_warning_dialog("Bitte wähle ein Talent aus.")

            search_field.bind(text=populate_talent_list)
            populate_talent_list()

            scroll.add_widget(talent_list)
            content.add_widget(scroll)
            content.height = content_fixed + scroll_height

            dialog_height = min(content.height + dialog_chrome, max_dialog_height)
            self._talent_popup = MDDialog(
                MDDialogHeadlineText(text="Freies Talent wählen"),
                MDDialogContentContainer(content, orientation="vertical"),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(text="Überspringen"), style="text",
                        on_release=lambda x: self._talent_popup.dismiss()
                    ),
                    MDButton(
                        MDButtonText(text="Auswählen"), style="filled",
                        on_release=_confirm_talent
                    ),
                ),
                size_hint=(0.85, None),
                height=dialog_height,
            )
            self._talent_popup.open()

        except Exception as e:
            Logger.error(f"Fehler beim Anzeigen des Talent-Popups: {e}")

    def _show_error(self, message):
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_warning_dialog(message)
        except Exception:
            pass

    def _show_success(self, message):
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass


class VolkDialogHandler:
    def __init__(self, controller):
        self.controller = controller
        self.overlay = None
        self.selected_volk = None
        self.dialog_content = None

    def _get_overlay(self):
        from views.element_overlay import ElementOverlay
        if not self.overlay:
            self.overlay = ElementOverlay()
        return self.overlay

    def show_add_dialog(self):
        """Zeigt den Wizard zum Erstellen eines neuen Volkes"""
        wizard = VolkGeneratorWizard(
            controller=self.controller,
            callback=self._on_volk_created
        )
        wizard.start_wizard()

    def show_edit_dialog(self, volk_name):
        """Zeigt den Wizard zum Bearbeiten eines Volkes"""
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            
            if volk_name not in charakter.voelker:
                self.show_error(f"Abstammung '{volk_name}' nicht gefunden.")
                return
            
            volk = charakter.voelker[volk_name]
            
            wizard = VolkGeneratorWizard(
                controller=self.controller,
                callback=self._on_volk_created,
                edit_volk=volk
            )
            wizard.start_wizard()
            
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Bearbeiten-Dialogs: {e}")
            self.show_error("Fehler beim Öffnen des Bearbeiten-Dialogs")

    def _on_volk_created(self, volk_name, volk_obj):
        """Callback nach erfolgreicher Volk-Erstellung/Bearbeitung.
        Wählt das Volk aus und öffnet das Zusatzelement-Overlay (Phase 2),
        damit der Benutzer freie Talente/Attribute sofort auswählen kann."""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Völker', 'voelker_widget')
                if widget and hasattr(widget, 'open_volk_dropdown'):
                    widget.open_volk_dropdown()
                    Logger.info(f"Neues Volk '{volk_name}' erstellt — Overlay geöffnet")
                    
                    # Force refresh of Eigenschaften view after overlay animation completes
                    # This ensures dice icons are properly updated when Volkseigenarten
                    # modify attributes
                    from kivy.clock import Clock
                    Clock.schedule_once(self._force_eigenschaften_refresh, 0.5)
                    return
        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Overlays für neues Volk: {e}")
        self._refresh_volk_view()

    def _force_eigenschaften_refresh(self, dt):
        """Erzwingt ein UI-Refresh der Eigenschaften-View nach Volkseigenarten-Änderungen."""
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'controller') and app.controller:
                app.controller.dispatch('on_charakter_updated')
                Logger.debug("Eigenschaften-View Refresh nach Volkseigenarten erzwungen")
        except Exception as e:
            Logger.error(f"Fehler beim Erzwingen des Eigenschaften-Refresh: {e}")

    def show_delete_dialog(self):
        """Zeigt das Two-Phase Popup zum Löschen von Völkern."""
        import time
        from kivymd.uix.list import MDListItemTrailingCheckbox

        voelker = self.get_all_voelker()
        if not voelker:
            self.show_error("Keine Abstammungen zum Löschen verfügbar.")
            return

        self._volk_checkboxes = {}
        self._volk_last_cb_times = {}

        content = MDList(size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        def create_checkbox(item_name):
            item = MDListItem(size_hint_y=None, height=dp(48))
            item.add_widget(MDListItemSupportingText(text=item_name))

            checkbox = MDListItemTrailingCheckbox()
            cb = checkbox

            def on_release_checkbox(inst, cb=cb, name=item_name):
                now = time.monotonic()
                key = f"cb_{name}"
                if key in self._volk_last_cb_times and (now - self._volk_last_cb_times[key]) < 0.5:
                    return
                self._volk_last_cb_times[key] = now

            checkbox.bind(on_release=on_release_checkbox)
            item.add_widget(checkbox)
            content.add_widget(item)
            self._volk_checkboxes[item_name] = checkbox

        for volk_name in sorted(voelker):
            create_checkbox(volk_name)

        scroll_height = min(len(voelker) * dp(48), dp(250))
        scroll = MDScrollView(
            size_hint=(1, None),
            height=scroll_height,
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(15),
            bar_margin=dp(4),
        )
        scroll.add_widget(content)

        main_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            padding=dp(16),
            height=scroll_height + dp(80),
        )

        search_field = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(56),
            hint_text="Suchen...",
        )
        search_field.add_widget(MDTextFieldHintText(text="Suchen..."))
        main_content.add_widget(search_field)
        main_content.add_widget(scroll)

        def populate_list(search_text):
            content.clear_widgets()
            for volk_name in sorted(voelker):
                if search_text and search_text.lower() not in volk_name.lower():
                    continue
                if volk_name in self._volk_checkboxes:
                    item = MDListItem(size_hint_y=None, height=dp(48))
                    item.add_widget(MDListItemSupportingText(text=volk_name))
                    cb_existing = self._volk_checkboxes[volk_name]
                    if cb_existing.parent:
                        cb_existing.parent.remove_widget(cb_existing)
                    item.add_widget(cb_existing)
                    content.add_widget(item)
                else:
                    create_checkbox(volk_name)

        search_field.bind(text=lambda instance, value: populate_list(value))
        populate_list("")

        self._delete_popup = MDDialog(
            MDDialogHeadlineText(text="Abstammung löschen"),
            MDDialogContentContainer(main_content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text",
                         on_release=lambda x: self._delete_popup.dismiss()),
                MDButton(MDButtonText(text="Weiter"), style="filled",
                         on_release=self._on_delete_action_clicked),
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self._delete_popup.open()

    def _on_delete_action_clicked(self, *args):
        """Phase 1: Sammelt ausgewählte Items und zeigt Bestätigungs-Popup."""
        selected = [name for name, cb in self._volk_checkboxes.items() if cb.active]

        if not selected:
            self.show_error("Bitte wähle mindestens eine Abstammung zum Löschen aus.")
            return

        self._pending_delete_items = selected
        self._delete_popup.dismiss()
        self._show_delete_confirmation_popup(
            selected_items=selected, item_type="Abstammung", on_confirm=self._confirm_delete_volk
        )

    def save_volk(self, *args):
        """Speichert ein neues Volk"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name der Abstammung darf nicht leer sein.")
            return

        handicaps = [h.strip() for h in self.dialog_content.ids.handicaps_input.text.split(',') if h.strip()]
        talente = [t.strip() for t in self.dialog_content.ids.talente_input.text.split(',') if t.strip()]
        besonderheiten = [b.strip() for b in self.dialog_content.ids.besonderheiten_input.text.split(',') if b.strip()]

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            if name in charakter.voelker:
                self.show_error(f"Abstammung '{name}' existiert bereits.")
                return

            new_volk = Volk(
                name=name,
                handicaps=handicaps,
                talente=talente,
                besonderheiten=besonderheiten,
                custom=True
            )

            charakter.voelker[name] = new_volk

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            self.dismiss_dialog()
            Logger.info(f"Volk '{name}' wurde hinzugefügt.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Volks: {e}")
            self.show_error("Fehler beim Speichern des Volks")

    def delete_volk(self, *args):
        """Löscht die ausgewählten Völker"""
        try:
            if not self.dialog_content:
                self.show_error("Dialog-Content nicht gefunden.")
                return

            selected = self.dialog_content.get_selected_items()
            if not selected:
                self.show_error("Bitte wähle mindestens eine Abstammung zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter

            deleted_count = 0
            skipped_count = 0
            for volk_name in selected:
                if volk_name in charakter.voelker:
                    if charakter.voelker[volk_name].ausgewaehlt:
                        Logger.warning(f"Volk '{volk_name}' ist ausgewählt und kann nicht gelöscht werden.")
                        skipped_count += 1
                        continue

                    del charakter.voelker[volk_name]
                    Logger.info(f"Volk '{volk_name}' wurde gelöscht.")
                    deleted_count += 1

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_volk_view()

            if deleted_count > 0 and skipped_count > 0:
                self._show_success_snackbar(
                    f"{deleted_count} Volk/Völker gelöscht, {skipped_count} übersprungen (aktuell ausgewählt)"
                )
            elif deleted_count > 0:
                self._show_success_snackbar(f"{deleted_count} Abstammung(en) gelöscht")
            else:
                self.show_error(
                    "Kein Volk konnte gelöscht werden.\n"
                    "Wähle das aktuell ausgewählte Volk zuerst ab, bevor du es löschst."
                )

            Logger.info(f"{deleted_count} Volk/Völker gelöscht, {skipped_count} übersprungen.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Völker: {e}")
            self.show_error("Fehler beim Löschen der Abstammungen")

    def _confirm_delete_volk(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch"""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            deleted_count = 0
            skipped_count = 0
            for volk_name in selected:
                if volk_name in charakter.voelker:
                    if charakter.voelker[volk_name].ausgewaehlt:
                        Logger.warning(f"Volk '{volk_name}' ist ausgewählt und kann nicht gelöscht werden.")
                        skipped_count += 1
                        continue

                    del charakter.voelker[volk_name]
                    Logger.info(f"Volk '{volk_name}' wurde gelöscht.")
                    deleted_count += 1

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_volk_view()

            if deleted_count > 0 and skipped_count > 0:
                self._show_success_snackbar(
                    f"{deleted_count} Volk/Völker gelöscht, {skipped_count} übersprungen (aktuell ausgewählt)"
                )
            elif deleted_count > 0:
                self._show_success_snackbar(f"{deleted_count} Abstammung(en) gelöscht")
            else:
                self.show_error(
                    "Kein Volk konnte gelöscht werden.\n"
                    "Wähle das aktuell ausgewählte Volk zuerst ab, bevor du es löschst."
                )

            Logger.info(f"{deleted_count} Volk/Völker gelöscht, {skipped_count} übersprungen.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Völker: {e}")
            self.show_error("Fehler beim Löschen der Abstammungen")

    def _show_delete_confirmation_popup(self, selected_items, item_type, on_confirm):
        """Zeigt separates Bestätigungs-Popup OHNE Checkboxen (Two-Phase Pattern)."""
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText
        from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
        from kivymd.uix.button import MDButton, MDButtonText
        from kivy.metrics import dp

        content = MDList(size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        for item_name in selected_items:
            list_item = MDListItem(size_hint_y=None, height=dp(48))
            list_item.add_widget(MDListItemSupportingText(text=item_name))
            content.add_widget(list_item)

        scroll = MDScrollView(do_scroll_x=False, do_scroll_y=True, bar_width=dp(15))
        scroll.add_widget(content)

        list_height = min(dp(48) * len(selected_items), dp(200))
        content.size_hint_y = None
        content.height = list_height

        main_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(80) + list_height,
            padding=dp(16)
        )
        main_content.add_widget(scroll)

        def _dismiss_confirm_popup(*_):
            """Schließt das Bestätigungs-Popup robust (doppelter Versuch)."""
            popup = getattr(self, '_delete_confirm_popup', None)
            if popup is None:
                return
            try:
                popup.dismiss()
            except Exception as e:
                Logger.warning(f"Fehler beim Schließen des Lösch-Dialogs: {e}")

        def _on_cancel(x):
            _dismiss_confirm_popup()
            Clock.schedule_once(_dismiss_confirm_popup, 0.15)

        def _on_confirm_release(x):
            # Dialog zuerst schließen, dann die eigentliche Aktion verzögert
            # ausführen. Auf Android kann das synchrone Aufrufen von
            # on_confirm() (mit UI-Refresh) die Dismiss-Animation unterbrechen
            # und den Dialog in einem inkonsistenten Zustand hinterlassen.
            _dismiss_confirm_popup()
            Clock.schedule_once(_dismiss_confirm_popup, 0.15)
            Clock.schedule_once(lambda dt: on_confirm(), 0.2)

        self._delete_confirm_popup = MDDialog(
            MDDialogHeadlineText(text=f"{item_type} löschen?"),
            MDDialogContentContainer(main_content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=_on_cancel,
                ),
                MDButton(
                    MDButtonText(text="Löschen"),
                    style="filled",
                    on_release=_on_confirm_release,
                ),
            ),
            size_hint=(0.85, None),
        )
        self._delete_confirm_popup.open()

    def on_volk_select(self, volk_name):
        """Callback wenn ein Volk im Dropdown ausgewählt wurde"""
        self.selected_volk = volk_name
        # Dialog-Content aktualisieren wenn vorhanden
        if (self.dialog_content and
            hasattr(self.dialog_content.ids, 'selected_volk_text')):
            self.dialog_content.ids.selected_volk_text.text = volk_name
            Logger.info(f"Volk '{volk_name}' wurde ausgewählt.")
        else:
            Logger.debug("Dialog-Content nicht verfügbar für Textaktualisierung")

    def dismiss_dialog(self, *args):
        """Schließt den aktiven Dialog"""
        if self.overlay and self.overlay._is_open:
            self.overlay.close()
        self.dialog_content = None
        self.selected_volk = None

    def show_error(self, message):
        """Zeigt eine Fehlermeldung an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_warning_dialog(message)
                return
        except Exception:
            pass
        Logger.error(f"Volk-Fehler: {message}")

    def get_all_voelker(self):
        """Gibt eine Liste aller verfügbaren Völker zurück"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller') and app.controller:
                charakter = app.controller.charakter
                return list(charakter.voelker.keys())
        except Exception as e:
            Logger.error(f"Fehler beim Abrufen der Völker: {e}")
        return []

    def _refresh_volk_view(self):
        """Aktualisiert das Volk-Widget nach Lösch-Operationen"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Völker', 'voelker_widget')
                if widget and hasattr(widget, 'aktualisiere_ui'):
                    widget.aktualisiere_ui()
                elif widget and hasattr(widget, 'refresh'):
                    widget.refresh()
                elif widget and hasattr(widget, 'refresh_widget'):
                    widget.refresh_widget()
        except Exception as e:
            Logger.warning(f"Volk-Widget nicht gefunden: {e}")

    def _show_success_snackbar(self, message):
        """Zeigt eine Erfolgs-Snackbar an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass
