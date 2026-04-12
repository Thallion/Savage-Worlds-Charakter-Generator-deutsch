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
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.list import MDListItemTrailingCheckbox

from models.volk import Volk
from functions.volkseigenarten_funktionen import (
    lade_volkseigenarten_config,
    berechne_punktestand,
    ist_punktestand_gueltig,
    get_eigenart_by_id,
    validiere_eigenart_auswahl,
    eigenart_zu_effekte,
    eigenart_zu_besonderheiten,
    validiere_volk_erstellung,
    lade_eigenarten_fuer_bearbeitung,
    formatiere_punkte_anzeige,
    START_PUNKTE
)

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
            {"Title": "Positive Volkseigenarten", "handler": self._create_positive_step},
            {"Title": "Negative Volkseigenarten", "handler": self._create_negative_step},
            {"Title": "Vorschau & Speichern", "handler": self._create_preview_step}
        ]
    
    def _load_volk_for_editing(self, volk):
        """Lädt ein Volk für die Bearbeitung"""
        volk_dict = {
            'name': volk.name,
            'beschreibung': '',
            'eigenarten': getattr(volk, 'eigenarten', [])
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
            self.dialog.dismiss()
        
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
            progress_text += " (Neues Volk)"
        
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
        
        title = "Volk erstellen" if not self.edit_volk else f"Volk bearbeiten: {self.edit_volk.name}"
        
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
            text=f"Volkseigenarten-System: Starte mit {START_PUNKTE} Punkten für positive Eigenarten.",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="40dp"
        )
        content.add_widget(info_label)
        
        self.name_field = MDTextField(
            MDTextFieldHintText(text="Volk-Name *"),
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

        title = "Positive Volkseigenarten" if eigenart_typ == 'positive' else "Negative Volkseigenarten"

        label = MDLabel(
            text=f"{title} auswählen",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(label)

        # Punktestand-Info
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

        # Button zum Öffnen des Checkbox-Popups
        btn = MDButton(style="tonal", size_hint_y=None, height=dp(48))
        btn.add_widget(MDButtonText(text=f"{title} auswählen..."))
        btn.bind(on_release=lambda x: self._show_eigenarten_popup(eigenart_typ))
        layout.add_widget(btn)

        # Aktuelle Auswahl anzeigen
        auswahl = self.positive_eigenarten if eigenart_typ == 'positive' else self.negative_eigenarten
        if auswahl:
            auswahl_text = ", ".join([e.get('name', e.get('id', '')) for e in auswahl])
            auswahl_label = MDLabel(
                text=f"Ausgewählt: {auswahl_text}",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(48)
            )
            layout.add_widget(auswahl_label)

        return layout

    def _show_eigenarten_popup(self, eigenart_typ):
        """Zeigt separates Popup für Eigenarten-Checkboxen (eigener ScrollView)"""
        if self._wizard_finished:
            return
        from kivy.core.window import Window

        config = lade_volkseigenarten_config()
        eigenarten = config.get(eigenart_typ, [])
        aktuelle_auswahl = self.positive_eigenarten if eigenart_typ == 'positive' else self.negative_eigenarten
        title = "Positive Volkseigenarten" if eigenart_typ == 'positive' else "Negative Volkseigenarten"

        # Hauptlayout mit fester Höhe
        popup_height = min(Window.height * 0.7, dp(400))
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=popup_height
        )

        # Liste für Checkboxen
        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        if _mobile:
            list_layout.padding = [0, 0, dp(32), 0]

        for eigenart in eigenarten:
            eigenart_id = eigenart.get('id')
            aktuelle_anzahl = sum(1 for e in aktuelle_auswahl if e.get('id') == eigenart_id)
            max_auswahl = eigenart.get('max_auswahl', 1)

            kosten = eigenart.get('kosten', 2)
            kosten_text = f" [{kosten} EP]"
            if max_auswahl == 0:
                max_text = " (U)"
            elif max_auswahl > 1:
                max_text = f" ({aktuelle_anzahl}/{max_auswahl})"
            else:
                max_text = ""

            list_item = MDListItem(size_hint_y=None, height=dp(56))
            list_item.add_widget(MDListItemHeadlineText(
                text=f"{eigenart.get('name', eigenart_id)}{kosten_text}{max_text}"
            ))
            if eigenart.get('beschreibung'):
                list_item.add_widget(MDListItemSupportingText(
                    text=eigenart.get('beschreibung', '')
                ))

            checkbox = MDListItemTrailingCheckbox(active=aktuelle_anzahl > 0)
            cb = checkbox
            e_id = eigenart_id
            e_typ = eigenart_typ
            checkbox.bind(on_release=lambda x, cb=cb, eid=e_id, et=e_typ: self._on_eigenart_checkbox_clicked(eid, et, cb))
            list_item.add_widget(checkbox)
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
            summary += f"[b]Positive Volkseigenarten ({len(self.positive_eigenarten)}):[/b]\n"
            for e in self.positive_eigenarten:
                auswahl_text = ""
                if e.get('optionen', {}).get('ausgewaehlt'):
                    auswahl_text = f" → {e['optionen']['ausgewaehlt']}"
                summary += f"  • {e.get('name', e.get('id'))} [{e.get('kosten', 0)} EP]{auswahl_text}\n"
        else:
            summary += "[b]Positive Volkseigenarten:[/b] Keine\n"

        summary += "\n"

        if self.negative_eigenarten:
            summary += f"[b]Negative Volkseigenarten ({len(self.negative_eigenarten)}):[/b]\n"
            for e in self.negative_eigenarten:
                auswahl_text = ""
                if e.get('optionen', {}).get('ausgewaehlt'):
                    auswahl_text = f" → {e['optionen']['ausgewaehlt']}"
                summary += f"  • {e.get('name', e.get('id'))} [{e.get('kosten', 0)} EP]{auswahl_text}\n"
        else:
            summary += "[b]Negative Volkseigenarten:[/b] Keine\n"
        
        return summary
    
    def _update_name(self, instance, value):
        self.wizard_data['name'] = value
    
    def _update_beschreibung(self, instance, value):
        self.wizard_data['beschreibung'] = value
    
    def _toggle_eigenart(self, eigenart_id, eigenart_typ, active, checkbox=None):
        """Toggle eine Eigenart-Auswahl. Bei Eigenarten mit Optionen wird ein Zwischen-Dialog gezeigt."""
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
                # Deep-copy der Optionen damit jede Auswahl eigene Daten hat
                if 'optionen' in eigenart_copy:
                    eigenart_copy['optionen'] = dict(eigenart_copy['optionen'])

                # Hat die Eigenart Optionen? → Zwischen-Dialog zeigen
                if eigenart_copy.get('optionen'):
                    self._show_optionen_dialog(eigenart_copy, liste, checkbox)
                else:
                    liste.append(eigenart_copy)
        else:
            self._remove_eigenart(eigenart_id, liste)
    
    def _on_eigenart_checkbox_clicked(self, eigenart_id, eigenart_typ, checkbox):
        """Handler für Checkbox-Klick mit Debounce."""
        now = time.monotonic()
        if hasattr(self, '_last_eigenart_toggle_time') and (now - self._last_eigenart_toggle_time) < 0.5:
            return
        self._last_eigenart_toggle_time = now
        self._toggle_eigenart(eigenart_id, eigenart_typ, checkbox.active, checkbox=checkbox)
    
    def _show_optionen_dialog(self, eigenart, liste, checkbox=None):
        """Zeigt einen Zwischen-Dialog fuer Eigenart-Optionen (Attribut-/Fertigkeits-Auswahl oder Texteingabe).
        Blendet das Eigenarten-Popup temporär aus um Überlappung zu vermeiden."""
        optionen = eigenart.get('optionen', {})
        typ = optionen.get('typ', '')
        eigenart_name = eigenart.get('name', eigenart.get('id', ''))

        # Eigenarten-Popup temporär ausblenden um Überlappung zu vermeiden
        if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
            self._eigenarten_popup.opacity = 0

        def _on_cancel(dialog_ref):
            """Abbrechen: Checkbox zuruecksetzen, Eigenart nicht hinzufuegen."""
            dialog_ref.dismiss()
            if checkbox:
                checkbox.active = False

        if typ == 'text_eingabe':
            self._show_text_optionen_dialog(eigenart, liste, checkbox, optionen, eigenart_name)
        elif typ == 'talent_auswahl':
            self._show_talent_optionen_dialog(eigenart, liste, checkbox, optionen, eigenart_name)
        elif typ in ('attribut_auswahl', 'grundfertigkeit_auswahl', 'nicht_grundfertigkeit_auswahl'):
            self._show_liste_optionen_dialog(eigenart, liste, checkbox, optionen, typ, eigenart_name)
        else:
            # Unbekannter Typ - einfach hinzufuegen
            liste.append(eigenart)
            # Eigenarten-Popup wieder einblenden
            if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
                self._eigenarten_popup.opacity = 1

    def _restore_eigenarten_popup(self):
        """Blendet das Eigenarten-Popup nach Schließen eines Unter-Dialogs wieder ein."""
        if hasattr(self, '_eigenarten_popup') and self._eigenarten_popup:
            self._eigenarten_popup.opacity = 1

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
        """Dialog zur Auswahl eines freien Talents für Volkseigenart."""
        import time
        
        from functions.volk_funktionen import get_freie_talente
        
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            charakter = app.controller.charakter
        except Exception:
            Logger.warning("Kein Charakter für Talent-Auswahl gefunden")
            liste.append(eigenart)
            return
        
        talente = get_freie_talente(charakter, nur_verfuegbare=True)
        if not talente or (len(talente) == 1 and "Keine" in talente[0]):
            Logger.warning("Keine freien Talente verfügbar für Volkseigenart")
            liste.append(eigenart)
            return
        
        beschreibung = optionen.get('beschreibung', 'Wähle ein freies Anfängertalent:')
        standard = optionen.get('standard', talente[0] if talente else None)
        selected = [standard]
        self._last_talent_click = 0

        content = MDBoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None, adaptive_height=True)

        content.add_widget(MDLabel(
            text=beschreibung,
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(24)
        ))

        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        if _mobile:
            list_layout.padding = [0, 0, dp(32), 0]
        radio_checkboxes = {}

        for item_name in talente:
            list_item = MDListItem(size_hint_y=None, height=dp(56) if _mobile else dp(48))
            list_item.add_widget(MDListItemHeadlineText(text=item_name))
            radio_cb = MDListItemTrailingCheckbox(
                active=(item_name == standard),
                group=f"optionen_{eigenart.get('id', '')}"
            )
            r_cb = radio_cb
            i_name = item_name
            list_item.bind(on_release=lambda x, name=i_name: self._select_talent_option(name, selected, radio_checkboxes))
            radio_cb.bind(on_release=lambda x, cb=r_cb, name=i_name: self._on_talent_radio_clicked(name, selected, radio_checkboxes, cb))
            list_item.add_widget(radio_cb)
            list_layout.add_widget(list_item)
            radio_checkboxes[item_name] = radio_cb

        scroll = MDScrollView(size_hint_y=None, height=landscape_height(200, 0.35),
                              bar_width=dp(20) if _mobile else dp(15), bar_margin=dp(8) if _mobile else dp(4))
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
                Logger.info(f"Freies Talent '{selected[0]}' für Volkseigenart gewählt")

        def _on_cancel(x):
            dialog.dismiss()
            self._restore_eigenarten_popup()
            if checkbox:
                checkbox.active = False

        dialog = MDDialog(
            MDDialogHeadlineText(text=f"{eigenart_name} — Talent wählen"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text", on_release=_on_cancel),
                MDButton(MDButtonText(text="Bestätigen"), style="filled", on_release=_on_confirm),
            ),
            size_hint=(0.85, None),
        )
        dialog.open()
    
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
                self._show_error("Bitte gib einen Namen für das Volk ein.")
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
                del charakter.voelker[self.edit_volk.name]
                Logger.info(f"Altes Volk '{self.edit_volk.name}' für Bearbeitung entfernt")
            
            if volk_name in charakter.voelker:
                self._show_error(f"Volk '{volk_name}' existiert bereits.")
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

            if self.dialog:
                self.dialog.dismiss()

            self._show_success(f"Volk '{volk_name}' wurde {'aktualisiert' if self.edit_volk else 'erstellt'}.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()

            if self.callback:
                self.callback(volk_name, new_volk)

            Logger.info(f"Volk '{volk_name}' erfolgreich {'aktualisiert' if self.edit_volk else 'erstellt'}.")

        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Volks: {e}")
            self._show_error(f"Fehler beim Speichern: {e}")
    
    def _show_freies_talent_popup(self, volk_name):
        """Zeigt ein separates Popup zur Auswahl eines freien Talents nach Volk-Erstellung."""
        import time
        try:
            app = App.get_running_app()
            charakter = app.controller.charakter
            from functions.volk_funktionen import get_freie_talente, waehle_freies_talent, NO_TALENT_AVAILABLE_TEXT

            talente = get_freie_talente(charakter, nur_verfuegbare=True)
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

            info_label = MDLabel(
                text=f"Volk '{volk_name}' hat ein freies Talent.\nBitte wähle ein Anfängertalent:",
                font_style="Body", theme_text_color="Secondary",
                size_hint_y=None, height=dp(48)
            )
            content.add_widget(info_label)

            # Suchfeld
            search_field = MDTextField(mode="outlined", size_hint_y=None, height=dp(56))
            search_field.add_widget(MDTextFieldHintText(text="Talent suchen..."))
            content.add_widget(search_field)

            # Scrollbare Talentliste
            from kivy.core.window import Window
            scroll_height = min(dp(300), Window.height * 0.4)
            scroll = MDScrollView(size_hint=(1, None), height=scroll_height, do_scroll_x=False)
            if _mobile:
                scroll.bar_width = dp(20)
                scroll.bar_margin = dp(8)
                scroll.scroll_type = ['bars', 'content']
            talent_list = MDList(size_hint_y=None)
            talent_list.bind(minimum_height=talent_list.setter('height'))
            if _mobile:
                talent_list.padding = [0, 0, dp(32), 0]
            scroll.add_widget(talent_list)
            content.add_widget(scroll)

            def populate_talent_list(*args):
                talent_list.clear_widgets()
                search_text = search_field.text.lower() if search_field.text else ""
                for talent_name in talente:
                    if search_text and search_text not in talent_name.lower():
                        continue
                    is_sel = (self._talent_selected == talent_name)
                    item = MDListItem(
                        size_hint_y=None, height=dp(48),
                        md_bg_color=app.theme_cls.primaryContainerColor if is_sel else [0, 0, 0, 0],
                    )
                    t_name = talent_name
                    item.bind(on_release=lambda x, n=t_name: _select_talent(n))
                    item.add_widget(MDListItemHeadlineText(text=talent_name))
                    talent_list.add_widget(item)

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
                    success = waehle_freies_talent(charakter, volk_name, self._talent_selected)
                    if success:
                        Logger.info(f"Freies Talent '{self._talent_selected}' für Volk '{volk_name}' gewählt")
                        # VoelkerWidget UI aktualisieren
                        try:
                            widget = app.get_widget_by_tab_text('Völker', 'voelker_widget')
                            if widget:
                                widget.voelker_auswahlen.setdefault(volk_name, {})
                                widget.voelker_auswahlen[volk_name]['freies_talent'] = self._talent_selected
                                widget.aktualisiere_ui()
                        except Exception:
                            pass
                    if self._talent_popup:
                        self._talent_popup.dismiss()
                else:
                    from services.service_container import service_container
                    ds = service_container.get_dialog_service()
                    if ds:
                        ds.show_warning_dialog("Bitte wähle ein Talent aus.")

            search_field.bind(text=populate_talent_list)
            populate_talent_list()

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
                self.show_error(f"Volk '{volk_name}' nicht gefunden.")
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
        """Callback nach erfolgreicher Volk-Erstellung/Bearbeitung — wählt das Volk automatisch aus"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Völker', 'voelker_widget')
                if widget and hasattr(widget, '_select_volk_from_dropdown'):
                    widget._select_volk_from_dropdown(volk_name)
                    Logger.info(f"Neues Volk '{volk_name}' automatisch ausgewählt")
                    return
        except Exception as e:
            Logger.error(f"Fehler bei Auto-Auswahl des neuen Volks: {e}")
        self._refresh_volk_view()

    def show_delete_dialog(self):
        """Zeigt das Two-Phase Popup zum Löschen von Völkern."""
        import time
        from kivymd.uix.list import MDListItemTrailingCheckbox

        voelker = self.get_all_voelker()
        if not voelker:
            self.show_error("Keine Völker zum Löschen verfügbar.")
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
            MDDialogHeadlineText(text="Volk löschen"),
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
            self.show_error("Bitte wähle mindestens ein Volk zum Löschen aus.")
            return

        self._pending_delete_items = selected
        self._delete_popup.dismiss()
        self._show_delete_confirmation_popup(
            selected_items=selected, item_type="Volk", on_confirm=self._confirm_delete_volk
        )

    def save_volk(self, *args):
        """Speichert ein neues Volk"""
        if not self.dialog_content:
            Logger.error("Dialog-Content nicht gefunden")
            return

        name = self.dialog_content.ids.name_input.text.strip()

        if not name:
            self.show_error("Der Name des Volkes darf nicht leer sein.")
            return

        handicaps = [h.strip() for h in self.dialog_content.ids.handicaps_input.text.split(',') if h.strip()]
        talente = [t.strip() for t in self.dialog_content.ids.talente_input.text.split(',') if t.strip()]
        besonderheiten = [b.strip() for b in self.dialog_content.ids.besonderheiten_input.text.split(',') if b.strip()]

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            if name in charakter.voelker:
                self.show_error(f"Volk '{name}' existiert bereits.")
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
                self.show_error("Bitte wähle mindestens ein Volk zum Löschen aus.")
                return

            app = App.get_running_app()
            charakter = app.controller.charakter

            for volk_name in selected:
                if volk_name in charakter.voelker:
                    if charakter.voelker[volk_name].ausgewaehlt:
                        Logger.warning(f"Volk '{volk_name}' ist ausgewählt und kann nicht gelöscht werden.")
                        continue

                    del charakter.voelker[volk_name]
                    Logger.info(f"Volk '{volk_name}' wurde gelöscht.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_volk_view()
            self._show_success_snackbar(f"{len(selected)} Volk/Völker gelöscht")

            Logger.info(f"{len(selected)} Volk/Völker wurde(n) gelöscht.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Völker: {e}")
            self.show_error("Fehler beim Löschen der Völker")

    def _confirm_delete_volk(self):
        """Phase 2: Führt das tatsächliche Löschen nach Bestätigung durch"""
        if not hasattr(self, '_pending_delete_items') or not self._pending_delete_items:
            return

        selected = self._pending_delete_items
        self._pending_delete_items = None

        try:
            app = App.get_running_app()
            charakter = app.controller.charakter

            for volk_name in selected:
                if volk_name in charakter.voelker:
                    if charakter.voelker[volk_name].ausgewaehlt:
                        Logger.warning(f"Volk '{volk_name}' ist ausgewählt und kann nicht gelöscht werden.")
                        continue

                    del charakter.voelker[volk_name]
                    Logger.info(f"Volk '{volk_name}' wurde gelöscht.")

            if hasattr(app, 'einstellungen_widget'):
                app.einstellungen_widget.aktualisiere_ui()
            self._refresh_volk_view()
            self._show_success_snackbar(f"{len(selected)} Volk/Völker gelöscht")

            Logger.info(f"{len(selected)} Volk/Völker wurde(n) gelöscht.")
            self.dismiss_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Löschen der Völker: {e}")
            self.show_error("Fehler beim Löschen der Völker")

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

        self._delete_confirm_popup = MDDialog(
            MDDialogHeadlineText(text=f"{item_type} löschen?"),
            MDDialogContentContainer(main_content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self._delete_confirm_popup.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Löschen"),
                    style="filled",
                    on_release=lambda x: (
                        self._delete_confirm_popup.dismiss(),
                        on_confirm()
                    )
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
            Logger.debug(f"Volk-Widget nicht gefunden: {e}")

    def _show_success_snackbar(self, message):
        """Zeigt eine Erfolgs-Snackbar an"""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass
