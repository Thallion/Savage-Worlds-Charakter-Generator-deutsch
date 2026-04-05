# views/setting_assistent_view.py
"""
Setting-Assistent für die Erstellung und Bearbeitung von Settings.
Mehrstufiger Wizard mit 4 Schritten:
1. Grundeinstellungen (Name, Beschreibung, Modus)
2. Elemente konfigurieren
3. Zusammenführungs-Konflikte lösen (nur bei Merge)
4. Vorschau & Speichern
"""

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, DictProperty, ListProperty, ObjectProperty
from kivy.utils import platform as kivy_platform
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemTrailingCheckbox
from views.ui_components import TextFieldScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.divider import MDDivider

import os
import sys
import time
from typing import Optional, List, Callable

from models.setting_draft import (
    SettingDraft,
    DraftManager,
    create_empty_draft,
    create_template_draft,
    create_merge_draft
)
from functions.setting_merge import (
    merge_settings,
    get_merge_conflicts,
    calculate_setting_statistics,
    format_statistics_for_display
)
from utils.path_utils import get_application_root

def _is_mobile_layout():
    """Prüft ob Mobile-Layout verwendet werden soll."""
    if kivy_platform in ('android', 'ios'):
        return True
    try:
        from services.service_container import service_container
        config = service_container.get_config_service()
        return config.get('force_mobile_layout', False)
    except Exception:
        return False

_mobile = _is_mobile_layout()
_kv_name = 'setting_assistent_view_mobile.kv' if _mobile else 'setting_assistent_view.kv'
Builder.load_file(os.path.join(os.path.dirname(__file__), _kv_name))


class SettingAssistentWizard:
    """
    Haupt-Wizard-Klasse für die Setting-Erstellung.
    Verwaltet den mehrstufigen Prozess.
    """
    
    MODES_DESKTOP = {
        "empty": {"label": "Leer starten", "icon": "file-outline", "description": "Komplett leeres Setting erstellen"},
        "template": {"label": "Vorlage verwenden", "icon": "file-document-outline", "description": "Auf bestehendem Setting aufbauen"},
        "merge": {"label": "Zusammenführen", "icon": "merge", "description": "Mehrere Settings kombinieren"},
        "extract": {"label": "Aus Charakter", "icon": "account-outline", "description": "Aus aktuellem Charakter extrahieren"}
    }
    
    MODES_MOBILE = {
        "empty": {"label": "Leer", "icon": "file-outline", "description": "Neues Setting"},
        "template": {"label": "Vorlage", "icon": "file-document-outline", "description": "Auf bestehendem Setting"},
        "merge": {"label": "Zusammenführen", "icon": "merge", "description": "Mehrere kombinieren"},
        "extract": {"label": "Charakter", "icon": "account-outline", "description": "Aus Charakter"}
    }
    
    MODES = MODES_MOBILE if _mobile else MODES_DESKTOP
    
    def __init__(self, controller, callback: Optional[Callable] = None, edit_draft: Optional[SettingDraft] = None):
        self.controller = controller
        self.callback = callback
        self.edit_draft = edit_draft
        self.current_step = 1
        self.dialog = None
        
        self.draft_manager = DraftManager()
        
        self.draft = edit_draft
        if not self.draft:
            self.draft = SettingDraft(
                name="",
                mode="template",
                description="",
                current_step=1
            )
        
        if _mobile:
            self.steps = [
                {"Title": "Name", "handler": self._create_step_name},
                {"Title": "Modus", "handler": self._create_step_modus},
                {"Title": "Elemente", "handler": self._create_step_elemente},
                {"Title": "Vorschau", "handler": self._create_step_vorschau}
            ]
        else:
            self.steps = [
                {"Title": "Name & Beschreibung", "handler": self._create_step_name},
                {"Title": "Modus & Basis", "handler": self._create_step_modus},
                {"Title": "Elemente konfigurieren", "handler": self._create_step_elemente},
                {"Title": "Vorschau & Speichern", "handler": self._create_step_vorschau}
            ]
    
    def _get_total_steps(self) -> int:
        """Berechnet die Gesamtanzahl der Schritte basierend auf dem Modus."""
        return len(self.steps)
    
    def start_wizard(self):
        """Startet den Wizard."""
        Logger.info("Setting-Assistent Wizard gestartet")
        self.current_step = 1
        self._show_current_step()
    
    def _show_current_step(self):
        """Zeigt den aktuellen Schritt."""
        step_index = self.current_step - 1
        total = self._get_total_steps()
        
        if self.current_step > total:
            self._finish_wizard()
            return
        
        if step_index >= len(self.steps):
            self._finish_wizard()
            return
        
        step = self.steps[step_index]
        Logger.info(f"Zeige Wizard-Schritt {self.current_step}: {step['Title']}")
        
        if self.dialog:
            self.dialog.dismiss()
        
        content = step['handler']()
        
        if _mobile:
            nav_height = dp(40)
            nav_spacing = dp(4)
        else:
            nav_height = "50dp"
            nav_spacing = "12dp"
        nav_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=nav_spacing,
            size_hint_y=None,
            height=nav_height
        )
        
        if self.current_step > 1:
            back_btn = MDButton(style="text", on_release=self._previous_step, size_hint_x=None, width=dp(40))
            back_btn.add_widget(MDButtonIcon(icon="arrow-left"))
            nav_layout.add_widget(back_btn)
        
        if _mobile:
            cancel_btn = MDButton(style="text", on_release=self._cancel_wizard, size_hint_x=None, width=dp(40))
            cancel_btn.add_widget(MDButtonIcon(icon="close"))
        else:
            cancel_btn = MDButton(style="text", on_release=self._cancel_wizard, size_hint_x=None, width=dp(80))
            cancel_btn.add_widget(MDButtonText(text="Abbrechen"))
        nav_layout.add_widget(cancel_btn)
        
        if _mobile:
            save_draft_btn = MDButton(style="text", on_release=self._save_draft_only, size_hint_x=None, width=dp(40))
            save_draft_btn.add_widget(MDButtonIcon(icon="content-save-outline"))
        else:
            save_draft_btn = MDButton(style="text", on_release=self._save_draft_only, size_hint_x=None, width=dp(100))
            save_draft_btn.add_widget(MDButtonText(text="Entwurf speichern"))
        nav_layout.add_widget(save_draft_btn)
        
        spacer = MDBoxLayout(size_hint_x=1)
        nav_layout.add_widget(spacer)
        
        is_last_step = self.current_step >= self._get_total_steps()
        if _mobile:
            next_icon = "check" if is_last_step else "arrow-right"
            next_btn = MDButton(style="text", on_release=self._finish_wizard if is_last_step else self._next_step, size_hint_x=None, width=dp(40))
            next_btn.add_widget(MDButtonIcon(icon=next_icon))
        else:
            next_btn = MDButton(style="text", on_release=self._finish_wizard if is_last_step else self._next_step, size_hint_x=None, width=dp(80))
            next_btn.add_widget(MDButtonIcon(icon="check" if is_last_step else "arrow-right"))
            next_btn.add_widget(MDButtonText(text="Speichern" if is_last_step else "Weiter"))
        nav_layout.add_widget(next_btn)
        
        if _mobile:
            main_layout_spacing = dp(6)
            # Dynamische Höhe: Fensterhöhe * 0.95 (Dialog) - Headline(~dp(56)) - Padding(~dp(24))
            from kivy.core.window import Window
            main_layout_height = Window.height * 0.95 - dp(80)
        else:
            main_layout_spacing = "12dp"
            main_layout_height = "750dp"
        main_layout = MDBoxLayout(orientation="vertical", spacing=main_layout_spacing, size_hint_y=None, height=main_layout_height)
        
        if _mobile:
            progress_text = f"Schritt {self.current_step}/{self._get_total_steps()}"
        else:
            progress_text = f"Schritt {self.current_step} von {self._get_total_steps()}"
        if self.edit_draft:
            progress_text += " (Bearbeiten)"
        if _mobile:
            progress_height = dp(20)
        else:
            progress_height = "30dp"
        progress_label = MDLabel(
            text=progress_text,
            theme_text_color="Secondary",
            size_hint_y=None,
            height=progress_height
        )
        main_layout.add_widget(progress_label)
        main_layout.add_widget(content)
        main_layout.add_widget(MDDivider())
        main_layout.add_widget(nav_layout)
        
        title = "Setting erstellen" if not self.edit_draft else f"Setting bearbeiten: {self.edit_draft.name}"
        
        dialog_size_hint = (0.95, 0.95) if _mobile else (0.9, 0.9)
        self.dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(main_layout),
            size_hint=dialog_size_hint,
            auto_dismiss=False,
        )
        self.dialog.open()
    
    def _create_step_name(self):
        """Schritt 1: Name & Beschreibung"""
        if _mobile:
            bar_width = dp(8)
            bar_margin = dp(8)
            content_height = dp(180)
            content_spacing = dp(4)
        else:
            bar_width = dp(12)
            bar_margin = dp(12)
            content_height = "500dp"
            content_spacing = "16dp"
        layout = TextFieldScrollView(size_hint_y=1, bar_width=bar_width, bar_margin=bar_margin)
        content = MDBoxLayout(orientation="vertical", spacing=content_spacing, size_hint_y=None, height=content_height)
        
        if _mobile:
            name_label_text = "Name *"
            name_height = dp(20)
        else:
            name_label_text = "Name des Settings *"
            name_height = "24dp"
        name_label = MDLabel(text=name_label_text, theme_text_color="Primary", bold=True, size_hint_y=None, height=name_height)
        content.add_widget(name_label)
        
        if _mobile:
            name_height_field = dp(48)
            name_hint = "Name"
        else:
            name_height_field = "56dp"
            name_hint = "Name (max. 50 Zeichen)"
        self.name_field = MDTextField(mode="outlined", text=self.draft.name, size_hint_y=None, height=name_height_field)
        self.name_field.add_widget(MDTextFieldHintText(text=name_hint))
        self.name_field.bind(text=self._update_name)
        content.add_widget(self.name_field)
        
        if _mobile:
            desc_height = dp(20)
        else:
            desc_height = "24dp"
        desc_label = MDLabel(text="Beschreibung", theme_text_color="Primary", bold=True, size_hint_y=None, height=desc_height)
        content.add_widget(desc_label)
        
        if _mobile:
            desc_height_field = dp(60)
            desc_hint = "Beschreibung"
        else:
            desc_height_field = "150dp"
            desc_hint = "Kurze Beschreibung (optional)"
        self.desc_field = MDTextField(mode="outlined", text=self.draft.description, multiline=True, size_hint_y=None, height=desc_height_field)
        self.desc_field.add_widget(MDTextFieldHintText(text=desc_hint))
        self.desc_field.bind(text=self._update_description)
        content.add_widget(self.desc_field)
        
        layout.add_widget(content)
        return layout
    
    def _create_step_modus(self):
        """Schritt 2: Modus & Basis-Setting Auswahl"""
        if _mobile:
            bar_width = dp(12)
            bar_margin = dp(12)
            content_height = dp(350)
            content_spacing = dp(4)
            mode_label_text = "Modus:"
            mode_label_height = dp(20)
        else:
            bar_width = dp(12)
            bar_margin = dp(12)
            content_height = "850dp"
            content_spacing = "16dp"
            mode_label_text = "Modus wählen"
            mode_label_height = "24dp"
        layout = TextFieldScrollView(size_hint_y=1, bar_width=bar_width, bar_margin=bar_margin)
        content = MDBoxLayout(orientation="vertical", spacing=content_spacing, size_hint_y=None, height=content_height)
        
        mode_label = MDLabel(text=mode_label_text, theme_text_color="Primary", bold=True, size_hint_y=None, height=mode_label_height)
        content.add_widget(mode_label)
        
        self.mode_cards = {}
        self.mode_checkboxes = {}
        for mode_id, mode_info in self.MODES.items():
            card, checkbox = self._create_mode_card(mode_id, mode_info)
            self.mode_cards[mode_id] = card
            self.mode_checkboxes[mode_id] = checkbox
            content.add_widget(card)
        
        self._create_setting_selection_section(content)
        
        layout.add_widget(content)
        return layout
    
    def _create_setting_selection_section(self, content):
        """Erstellt den Abschnitt für die Setting-Auswahl basierend auf dem Modus."""
        if _mobile:
            box_spacing = dp(4)
            box_height = dp(150)
        else:
            box_spacing = "12dp"
            box_height = "300dp"
        self.setting_selection_box = MDBoxLayout(
            orientation="vertical",
            spacing=box_spacing,
            size_hint_y=None,
            height=box_height
        )
        self._update_setting_selection_ui()
        content.add_widget(self.setting_selection_box)
    
    def _update_setting_selection_ui(self):
        """Aktualisiert die Setting-Auswahl-UI basierend auf dem gewählten Modus."""
        self.setting_selection_box.clear_widgets()
        
        mode = self.draft.mode
        
        if mode == "empty":
            if _mobile:
                info_text = "Keine Basiseinstellungen."
                info_height = dp(30)
                box_height = dp(30)
            else:
                info_text = "Keine Basiseinstellungen erforderlich."
                info_height = "24dp"
                box_height = "50dp"
            info = MDLabel(
                text=info_text,
                theme_text_color="Secondary",
                size_hint_y=None,
                height=info_height
            )
            self.setting_selection_box.add_widget(info)
            self.setting_selection_box.height = box_height
            return
        
        if mode == "template":
            self.setting_selection_box.height = dp(120) if _mobile else "300dp"
            if _mobile:
                label_text = "Basis:"
                label_height = dp(20)
            else:
                label_text = "Basis-Setting wählen:"
                label_height = "24dp"
            label = MDLabel(text=label_text, bold=True, size_hint_y=None, height=label_height)
            self.setting_selection_box.add_widget(label)
            
            self.template_setting_dropdown = self._create_setting_dropdown()
            self.setting_selection_box.add_widget(self.template_setting_dropdown)
            
        elif mode == "merge":
            self.setting_selection_box.height = dp(120) if _mobile else "300dp"
            if _mobile:
                label_text = "Merge:"
                label_height = dp(20)
            else:
                label_text = "Settings zum Zusammenführen wählen:"
                label_height = "24dp"
            label = MDLabel(text=label_text, bold=True, size_hint_y=None, height=label_height)
            self.setting_selection_box.add_widget(label)
            
            self.merge_setting_list = self._create_merge_setting_list()
            self.setting_selection_box.add_widget(self.merge_setting_list)
        
        elif mode == "extract":
            if _mobile:
                info_text = "Aktuelles Setting als Basis."
                info_height = dp(30)
                box_height = dp(30)
            else:
                info_text = "Das aktuelle Setting wird als Basis verwendet."
                info_height = "24dp"
                box_height = "50dp"
            info = MDLabel(
                text=info_text,
                theme_text_color="Secondary",
                size_hint_y=None,
                height=info_height
            )
            self.setting_selection_box.add_widget(info)
            self.setting_selection_box.height = box_height
    
    def _create_setting_dropdown(self) -> MDCard:
        """Erstellt eine Liste für die Template-Auswahl mit Checkboxen."""
        try:
            from models.charakter import Charakter
            from functions.setting_funktionen import CustomElementManager
            charakter = Charakter()
            manager = CustomElementManager(charakter)
            available_settings = list(manager.settings.keys())
            available_settings.sort()
        except Exception:
            available_settings = ["SWAE", "Deadlands", "Fantasy Kompendium"]
        
        num_items = len(available_settings)
        item_height = dp(40) if _mobile else dp(48)
        list_height = num_items * item_height + dp(16)
        max_list_height = dp(200) if _mobile else "300dp"
        card_height = min(list_height, max_list_height)
        
        card_padding = dp(4) if _mobile else "12dp"
        card = MDCard(style="outlined", padding=card_padding, size_hint_y=None, height=card_height)
        
        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        self.template_setting_checkboxes = {}
        for setting_name in available_settings:
            is_selected = setting_name in self.draft.base_settings
            item_height = dp(36) if _mobile else dp(48)
            list_item = MDListItem(
                size_hint_y=None,
                height=item_height
            )
            list_item.add_widget(MDListItemHeadlineText(text=setting_name))
            checkbox = MDListItemTrailingCheckbox(
                active=is_selected,
            )
            checkbox.bind(on_release=lambda inst, cb=checkbox, s=setting_name: self._on_template_checkbox_clicked(s, cb))
            list_item.add_widget(checkbox)
            list_layout.add_widget(list_item)
            self.template_setting_checkboxes[setting_name] = checkbox
        
        scroll = TextFieldScrollView(size_hint_y=1, bar_width=dp(8) if _mobile else dp(12), bar_margin=dp(4) if _mobile else dp(8))
        scroll.add_widget(list_layout)
        card.add_widget(scroll)
        
        return card
    
    def _create_merge_setting_list(self) -> MDCard:
        """Erstellt eine Liste für die Merge-Auswahl mit Checkboxen."""
        try:
            from models.charakter import Charakter
            from functions.setting_funktionen import CustomElementManager
            charakter = Charakter()
            manager = CustomElementManager(charakter)
            available_settings = list(manager.settings.keys())
            available_settings.sort()
        except Exception:
            available_settings = ["SWAE", "Deadlands", "Fantasy Kompendium"]
        
        num_items = len(available_settings)
        item_height = dp(40) if _mobile else dp(48)
        list_height = num_items * item_height + dp(16)
        max_list_height = dp(200) if _mobile else "300dp"
        card_height = min(list_height, max_list_height)
        
        card_padding = dp(4) if _mobile else "12dp"
        card = MDCard(style="outlined", padding=card_padding, size_hint_y=None, height=card_height)
        
        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for setting_name in available_settings:
            is_selected = setting_name in self.draft.base_settings
            item_height = dp(36) if _mobile else dp(48)
            list_item = MDListItem(size_hint_y=None, height=item_height)
            list_item.add_widget(MDListItemHeadlineText(text=setting_name))
            checkbox = MDListItemTrailingCheckbox(
                active=is_selected,
            )
            checkbox.bind(on_release=lambda inst, cb=checkbox, s=setting_name: self._on_merge_checkbox_clicked(s, cb))
            list_item.add_widget(checkbox)
            list_layout.add_widget(list_item)
        
        scroll = TextFieldScrollView(size_hint_y=1, bar_width=dp(8) if _mobile else dp(12), bar_margin=dp(4) if _mobile else dp(8))
        scroll.add_widget(list_layout)
        card.add_widget(scroll)
        
        return card
    
    def _select_template_setting(self, setting_name: str, is_selected: bool):
        """Wählt ein Template-Setting aus (nur einer möglich)."""
        if is_selected:
            self.draft.base_settings = [setting_name]
            self._update_template_checkboxes()
        elif setting_name in self.draft.base_settings:
            self.draft.base_settings.remove(setting_name)
    
    def _update_template_checkboxes(self):
        """Aktualisiert die Template-Checkboxen (nur einer aktiv)."""
        if hasattr(self, 'template_setting_checkboxes'):
            selected = self.draft.base_settings[0] if self.draft.base_settings else None
            for name, checkbox in self.template_setting_checkboxes.items():
                checkbox.active = (name == selected)
    
    def _toggle_merge_setting(self, setting_name: str, is_selected: bool):
        """Toggled ein Setting für das Merge."""
        if is_selected:
            if setting_name not in self.draft.base_settings:
                self.draft.base_settings.append(setting_name)
        else:
            if setting_name in self.draft.base_settings:
                self.draft.base_settings.remove(setting_name)
    
    def _on_template_checkbox_clicked(self, setting_name: str, checkbox):
        """Handler für Checkbox-Klick mit Debounce (Template-Modus)."""
        now = time.monotonic()
        if hasattr(self, '_last_template_checkbox_time') and (now - self._last_template_checkbox_time) < 0.5:
            return
        self._last_template_checkbox_time = now
        self._select_template_setting(setting_name, checkbox.active)
    
    def _on_merge_checkbox_clicked(self, setting_name: str, checkbox):
        """Handler für Checkbox-Klick mit Debounce (Merge-Modus)."""
        now = time.monotonic()
        if hasattr(self, '_last_merge_checkbox_time') and (now - self._last_merge_checkbox_time) < 0.5:
            return
        self._last_merge_checkbox_time = now
        self._toggle_merge_setting(setting_name, checkbox.active)
    
    def _create_mode_card(self, mode_id: str, mode_info: dict) -> tuple:
        """Erstellt eine Mode-Auswahlkarte. Gibt (card, checkbox) zurück."""
        if _mobile:
            card_height = dp(56)
            card_padding = dp(8)
        else:
            card_height = "90dp"
            card_padding = "12dp"
        
        card = MDCard(
            style="elevated",
            padding=card_padding,
            size_hint_y=None,
            height=card_height,
            on_release=lambda x: self._select_mode(mode_id)
        )
        
        is_selected = self.draft.mode == mode_id
        
        if _mobile:
            card_content = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=1)

            # Nicht-interaktives Icon damit Touch zur Karte durchgeht
            icon_label = MDIcon(
                icon=mode_info["icon"],
                size_hint_x=None,
                width=dp(32),
                halign="center",
                valign="center",
                theme_text_color="Primary"
            )
            card_content.add_widget(icon_label)

            title = MDLabel(
                text=mode_info["label"],
                bold=True,
                size_hint_x=1,
                halign="left",
                valign="center"
            )
            card_content.add_widget(title)

            checkbox = MDListItemTrailingCheckbox(active=is_selected, size_hint_x=None, width=dp(40))
            checkbox.disabled = True
            card_content.add_widget(checkbox)
        else:
            card_content = MDBoxLayout(orientation="vertical", spacing="4dp")
            
            header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="28dp")
            
            title = MDLabel(
                text=mode_info["label"],
                bold=True,
                size_hint_x=1,
                halign="left"
            )
            header.add_widget(title)
            
            checkbox = MDListItemTrailingCheckbox(active=is_selected, size_hint_x=None, width="40dp")
            checkbox.disabled = True
            header.add_widget(checkbox)
            
            card_content.add_widget(header)
            
            desc = MDLabel(
                text=mode_info["description"],
                theme_text_color="Secondary",
                font_style="Body"
            )
            card_content.add_widget(desc)
        
        card.add_widget(card_content)
        
        if is_selected:
            card.md_bg_color = App.get_running_app().theme_cls.primaryContainerColor
        else:
            card.md_bg_color = App.get_running_app().theme_cls.surfaceContainerLowColor
        
        return card, checkbox
    
    def _select_mode(self, mode_id: str):
        """Wählt einen Modus aus."""
        self.draft.mode = mode_id
        self._update_mode_selection()
        if hasattr(self, 'setting_selection_box'):
            self._update_setting_selection_ui()
    
    def _update_mode_selection(self):
        """Aktualisiert die Modus-Auswahl-UI."""
        app = App.get_running_app()
        for mode_id, card in self.mode_cards.items():
            is_selected = self.draft.mode == mode_id
            card.md_bg_color = (
                app.theme_cls.primaryContainerColor
                if is_selected
                else app.theme_cls.surfaceContainerLowColor
            )
            if mode_id in self.mode_checkboxes:
                self.mode_checkboxes[mode_id].active = is_selected
    
    def _create_step_elemente(self):
        """Schritt 2: Elemente konfigurieren (Tab-basiert)"""
        if _mobile:
            bar_width = dp(8)
            bar_margin = dp(4)
            content_height = dp(550)
            content_spacing = dp(6)
        else:
            bar_width = dp(12)
            bar_margin = dp(12)
            content_height = "680dp"
            content_spacing = "12dp"
        layout = TextFieldScrollView(size_hint_y=1, bar_width=bar_width, bar_margin=bar_margin)
        content = MDBoxLayout(orientation="vertical", spacing=content_spacing, size_hint_y=None, height=content_height)

        stats = calculate_setting_statistics(self.draft.setting_data)
        stats_text = format_statistics_for_display(stats)

        if _mobile:
            # Höhe dynamisch: ~dp(16) pro Statistik-Zeile + Padding
            num_lines = len(stats) if stats else 1
            stats_height = dp(12 + num_lines * 16)
            stats_padding = dp(6)
            stats_font = "11sp"
        else:
            stats_height = "180dp"
            stats_padding = "12dp"
            stats_font = "14sp"
            info_label = MDLabel(
                text="Wähle die Kategorien und Elemente für dein Setting aus.",
                theme_text_color="Secondary",
                size_hint_y=None,
                height="24dp"
            )
            content.add_widget(info_label)
        stats_card = MDCard(style="elevated", padding=stats_padding, size_hint_y=None, height=stats_height)
        stats_content = MDLabel(text=stats_text, markup=True, font_size=stats_font)
        stats_card.add_widget(stats_content)
        content.add_widget(stats_card)

        if not _mobile:
            tabs_label = MDLabel(
                text="Verfügbare Kategorien (klicken für Details):",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height="24dp"
            )
            content.add_widget(tabs_label)
        
        categories = [
            ("voelker", "Völker", "account-group"),
            ("fertigkeiten", "Fertigkeiten", "school"),
            ("talente", "Talente", "star"),
            ("handicaps", "Handicaps", "alert-circle"),
            ("maechte", "Mächte", "magic-staff"),
            ("ausruestung", "Ausrüstung", "sword"),
        ]
        
        for cat_id, cat_name, cat_icon in categories:
            cat_card = self._create_category_card(cat_id, cat_name, cat_icon, stats.get(cat_name, {}))
            content.add_widget(cat_card)
        
        layout.add_widget(content)
        return layout
    
    def _create_category_card(self, cat_id: str, cat_name: str, cat_icon: str, stats: dict) -> MDCard:
        """Erstellt eine Kategorie-Karte für Schritt 2."""
        if _mobile:
            card_height = dp(56)
            card_padding = [dp(6), dp(4), dp(6), dp(4)]
            icon_size = dp(28)
            card_spacing = dp(6)
        else:
            card_height = "70dp"
            card_padding = "12dp"
            icon_size = "48dp"
            card_spacing = "8dp"

        card = MDCard(
            style="elevated",
            padding=card_padding,
            size_hint_y=None,
            height=card_height,
            on_release=lambda x: self._open_category_editor(cat_id, cat_name)
        )

        card_content = MDBoxLayout(orientation="horizontal", spacing=card_spacing)

        if _mobile:
            # Nicht-interaktives Icon (MDLabel) statt MDButton, damit Touch zur Karte durchgeht
            icon_label = MDIcon(
                icon=cat_icon,
                size_hint_x=None,
                width=icon_size,
                halign="center",
                valign="center",
                theme_text_color="Primary"
            )
            card_content.add_widget(icon_label)
        else:
            icon_btn = MDButton(style="tonal", size_hint_x=None, width=icon_size, height=icon_size)
            icon_btn.add_widget(MDButtonIcon(icon=cat_icon))
            card_content.add_widget(icon_btn)

        info_layout = MDBoxLayout(orientation="vertical", size_hint_x=1)

        gesamt = stats.get("gesamt", 0)
        aktiv = stats.get("aktiv", 0)
        inaktiv = stats.get("inaktiv", 0)

        if _mobile:
            title = MDLabel(text=cat_name, bold=True, size_hint_y=None, height=dp(20), font_style="Body", role="medium")
            info_layout.add_widget(title)

            if gesamt > 0:
                detail_text = f"{aktiv}/{gesamt} aktiv"
            else:
                detail_text = "Keine"
            detail = MDLabel(
                text=detail_text,
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(16),
                font_style="Body",
                role="small"
            )
            info_layout.add_widget(detail)
        else:
            title = MDLabel(text=cat_name, bold=True, size_hint_y=None, height="24dp")
            info_layout.add_widget(title)

            if gesamt > 0:
                detail = MDLabel(
                    text=f"{aktiv} aktiv / {inaktiv} inaktiv / {gesamt} gesamt",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height="20dp"
                )
            else:
                detail = MDLabel(
                    text="Keine Elemente",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height="20dp"
                )
            info_layout.add_widget(detail)

        card_content.add_widget(info_layout)

        if _mobile:
            # Nicht-interaktiver Pfeil (MDIcon) statt MDButton
            arrow_icon = MDIcon(
                icon="chevron-right",
                size_hint_x=None,
                width=dp(24),
                halign="center",
                theme_text_color="Secondary"
            )
            card_content.add_widget(arrow_icon)
        else:
            arrow = MDButton(style="text", size_hint_x=None, width="40dp")
            arrow.add_widget(MDButtonIcon(icon="chevron-right"))
            card_content.add_widget(arrow)

        card.add_widget(card_content)

        return card
    
    def _open_category_editor(self, cat_id: str, cat_name: str):
        """Öffnet den Editor für eine Kategorie."""
        Logger.info(f"Öffne Editor für Kategorie: {cat_name}")
        self._show_category_dialog(cat_id, cat_name)
    
    def _show_category_dialog(self, cat_id: str, cat_name: str):
        """Zeigt einen Dialog zum Bearbeiten einer Kategorie."""
        category_data = self.draft.setting_data.get(cat_id, {})

        if cat_id == "fertigkeiten" and not category_data:
            category_data = self.draft.setting_data.get("fertigkeiten_daten", {})

        if isinstance(category_data, dict):
            items = list(category_data.keys())
        elif isinstance(category_data, list):
            items = category_data
        else:
            items = []

        if _mobile:
            content_height = dp(350)
            content_spacing = dp(4)
            item_height = dp(40)
            max_items = 100
        else:
            content_height = "500dp"
            content_spacing = "12dp"
            item_height = dp(48)
            max_items = 50

        content = MDBoxLayout(orientation="vertical", spacing=content_spacing, size_hint_y=None, height=content_height)

        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))

        for item_name in items[:max_items]:
            list_item = MDListItem(
                size_hint_y=None,
                height=item_height
            )
            list_item.add_widget(MDListItemHeadlineText(text=str(item_name)))

            is_active = True
            if isinstance(category_data, dict) and isinstance(category_data.get(item_name), dict):
                is_active = category_data.get(item_name, {}).get("aktiv", True)

            checkbox = MDListItemTrailingCheckbox(
                active=is_active,
            )
            checkbox.bind(on_active=lambda inst, value, item=item_name, cid=cat_id: self._on_category_checkbox_clicked(cid, item, value))
            list_item.add_widget(checkbox)
            list_layout.add_widget(list_item)

        scroll = TextFieldScrollView(size_hint_y=1, bar_width=dp(8) if _mobile else dp(12), bar_margin=dp(4) if _mobile else dp(8))
        scroll.add_widget(list_layout)
        content.add_widget(scroll)

        dialog_size = (0.95, 0.85) if _mobile else (0.9, 0.7)

        btn_container = MDDialogButtonContainer()

        if _mobile:
            cancel_btn = MDButton(style="text", size_hint_x=None, width=dp(40))
            cancel_btn.add_widget(MDButtonIcon(icon="close"))

            confirm_btn = MDButton(style="text", size_hint_x=None, width=dp(40))
            confirm_btn.add_widget(MDButtonIcon(icon="check"))
        else:
            cancel_btn = MDButton(MDButtonText(text="Abbrechen"), style="text")
            confirm_btn = MDButton(MDButtonText(text="Bestätigen"), style="filled")

        dialog = MDDialog(
            MDDialogHeadlineText(text=cat_name),
            MDDialogContentContainer(content),
            btn_container,
            size_hint=dialog_size,
        )

        cancel_btn.bind(on_release=lambda x: dialog.dismiss())
        confirm_btn.bind(on_release=lambda x: self._on_category_confirm(dialog))
        btn_container.add_widget(cancel_btn)
        btn_container.add_widget(confirm_btn)

        dialog.open()
    
    def _on_category_confirm(self, dialog):
        """Bestätigt die Kategorie-Änderungen."""
        dialog.dismiss()
        self._refresh_elemente_step()
    
    def _refresh_elemente_step(self):
        """Aktualisiert den Elemente-Schritt (Statistiken)."""
        if self.current_step == 3:
            self._show_current_step()
    
    def _toggle_category_item(self, cat_id: str, item_name: str, is_active: bool):
        """Toggled den Aktiv-Status eines Elements."""
        if cat_id in self.draft.setting_data:
            if isinstance(self.draft.setting_data[cat_id], dict):
                if item_name in self.draft.setting_data[cat_id]:
                    if isinstance(self.draft.setting_data[cat_id][item_name], dict):
                        self.draft.setting_data[cat_id][item_name]["aktiv"] = is_active
                    else:
                        self.draft.setting_data[cat_id][item_name] = {"aktiv": is_active}
    
    def _on_category_checkbox_clicked(self, cat_id: str, item_name: str, value: bool):
        """Handler für Checkbox-Klick (Kategorie-Editor, on_active)."""
        self._toggle_category_item(cat_id, item_name, value)
    
    def _resolve_conflict(self, index: int, resolution: str):
        """Löst einen Konflikt auf."""
        Logger.info(f"Konflikt {index} gelöst mit: {resolution}")
        self.draft.conflicts_resolved += 1
    
    def _create_step_vorschau(self):
        """Schritt 4: Vorschau & Speichern"""
        if _mobile:
            bar_width = dp(8)
            bar_margin = dp(4)
            content_height = dp(350)
            content_spacing = dp(6)
        else:
            bar_width = dp(12)
            bar_margin = dp(12)
            content_height = "680dp"
            content_spacing = "16dp"
        layout = TextFieldScrollView(size_hint_y=1, bar_width=bar_width, bar_margin=bar_margin)
        content = MDBoxLayout(orientation="vertical", spacing=content_spacing, size_hint_y=None, height=content_height)
        
        stats = calculate_setting_statistics(self.draft.setting_data)
        stats_text = format_statistics_for_display(stats)

        if _mobile:
            # Kompakte Vorschau: Name, Modus, ggf. Basis, Divider, Stats + Padding
            num_stats = len(stats) if stats else 0
            preview_height = dp(70 + num_stats * 18)
            if self.draft.base_settings:
                preview_height += dp(20)
            preview_padding = dp(8)
            preview_spacing = dp(4)
        else:
            preview_height = "400dp"
            preview_padding = "16dp"
            preview_spacing = "8dp"
        preview_card = MDCard(style="elevated", padding=preview_padding, size_hint_y=None, height=preview_height)

        preview_content = MDBoxLayout(orientation="vertical", spacing=preview_spacing)

        if _mobile:
            name_label = MDLabel(
                text=f"[b]{self.draft.name or 'Unbenannt'}[/b]",
                markup=True, size_hint_y=None, height=dp(22),
                font_style="Body", role="large"
            )
            preview_content.add_widget(name_label)

            mode_text = self.MODES.get(self.draft.mode, {}).get('label', self.draft.mode)
            mode_label = MDLabel(
                text=f"Modus: {mode_text}",
                theme_text_color="Secondary",
                size_hint_y=None, height=dp(18),
                font_style="Body", role="small"
            )
            preview_content.add_widget(mode_label)

            if self.draft.base_settings:
                bases = ", ".join(self.draft.base_settings)
                bases_label = MDLabel(
                    text=f"Basis: {bases}",
                    theme_text_color="Secondary",
                    size_hint_y=None, height=dp(18),
                    font_style="Body", role="small"
                )
                preview_content.add_widget(bases_label)

            preview_content.add_widget(MDDivider())
            stats_label = MDLabel(
                text=stats_text, markup=True,
                size_hint_y=None, height=dp(num_stats * 18),
                font_size="11sp"
            )
            preview_content.add_widget(stats_label)
        else:
            name_label = MDLabel(text=f"[b]{self.draft.name or 'Unbenannt'}[/b]", markup=True, size_hint_y=None, height="30dp")
            preview_content.add_widget(name_label)

            mode_text = self.MODES.get(self.draft.mode, {}).get('label', self.draft.mode)
            mode_label = MDLabel(
                text=f"Modus: {mode_text}",
                theme_text_color="Secondary",
                size_hint_y=None,
                height="24dp"
            )
            preview_content.add_widget(mode_label)

            if self.draft.description:
                desc_label = MDLabel(text=f"[i]{self.draft.description}[/i]", markup=True, theme_text_color="Secondary")
                preview_content.add_widget(desc_label)

            if self.draft.base_settings:
                bases = ", ".join(self.draft.base_settings)
                bases_label = MDLabel(text=f"Basierend auf: {bases}", theme_text_color="Secondary")
                preview_content.add_widget(bases_label)

            preview_content.add_widget(MDDivider())
            stats_label = MDLabel(text=stats_text, markup=True)
            preview_content.add_widget(stats_label)

        preview_card.add_widget(preview_content)
        content.add_widget(preview_card)
        
        validation = self._validate_draft()
        if not validation["is_valid"]:
            if _mobile:
                error_padding = dp(8)
                error_height = dp(60)
                error_font = "12sp"
                error_text = ", ".join(validation["errors"])
            else:
                error_padding = "12dp"
                error_height = "100dp"
                error_font = "14sp"
                error_text = "\n".join(validation["errors"])
            error_card = MDCard(style="elevated", padding=error_padding, md_bg_color=(1, 0, 0, 0.1), size_hint_y=None, height=error_height)
            error_content = MDLabel(
                text="[color=ff4444]Fehler:[/color] " + error_text,
                markup=True,
                theme_text_color="Error",
                font_size=error_font
            )
            error_card.add_widget(error_content)
            content.add_widget(error_card)
        
        layout.add_widget(content)
        return layout
    
    def _validate_draft(self) -> dict:
        """Validiert den Draft."""
        errors = []
        
        if not self.draft.name.strip():
            errors.append("• Setting-Name ist erforderlich")
        elif len(self.draft.name) > 50:
            errors.append("• Setting-Name darf maximal 50 Zeichen haben")
        
        if self.draft.mode == "template" and not self.draft.base_settings:
            errors.append("• Bitte wähle ein Basis-Setting aus")
        
        if self.draft.mode == "merge" and len(self.draft.base_settings) < 2:
            errors.append("• Mergen erfordert mindestens 2 Settings")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def _update_name(self, instance, value):
        self.draft.name = value[:50]
    
    def _update_description(self, instance, value):
        self.draft.description = value[:200]
    
    def _nav_debounce_check(self) -> bool:
        """Prüft ob ein Navigations-Event zu schnell hintereinander kommt (Android Touch-Bounce)."""
        now = time.monotonic()
        if hasattr(self, '_last_nav_time') and (now - self._last_nav_time) < 0.5:
            return False
        self._last_nav_time = now
        return True

    def _next_step(self, *args):
        if not self._nav_debounce_check():
            return
        if self.current_step == 1:
            validation = self._validate_basic_settings()
            if not validation["is_valid"]:
                self._show_error("\n".join(validation["errors"]))
                return
        
        if self.current_step == 2:
            self._initialize_draft_data()
        
        self.current_step += 1
        self.draft.current_step = self.current_step
        self._show_current_step()
    
    def _validate_basic_settings(self) -> dict:
        """Validiert die Grundeinstellungen."""
        errors = []
        
        if not self.draft.name.strip():
            errors.append("• Setting-Name ist erforderlich")
        elif len(self.draft.name) > 50:
            errors.append("• Setting-Name darf maximal 50 Zeichen haben")
        
        return {"is_valid": len(errors) == 0, "errors": errors}
    
    def _initialize_draft_data(self):
        """Initialisiert die Draft-Daten basierend auf dem Modus."""
        if self.draft.mode == "empty":
            empty_data = create_empty_draft(self.draft.name, self.draft.description)
            self.draft.setting_data = empty_data.setting_data
        elif self.draft.mode == "template":
            template_data = create_template_draft(
                self.draft.name,
                self.draft.base_settings[0] if self.draft.base_settings else "SWAE",
                self.draft.description
            )
            self.draft.setting_data = template_data.setting_data
        elif self.draft.mode == "merge":
            merged_data = create_merge_draft(
                self.draft.name,
                self.draft.base_settings,
                self.draft.description
            )
            self.draft.setting_data = merged_data.setting_data
    
    def _previous_step(self, *args):
        if not self._nav_debounce_check():
            return
        self.current_step -= 1
        self.draft.current_step = self.current_step
        self._show_current_step()
    
    def _cancel_wizard(self, *args):
        if not self._nav_debounce_check():
            return
        if self.dialog:
            self.dialog.dismiss()
        Logger.info("Setting-Assistent Wizard abgebrochen")
    
    def _save_draft_only(self, *args):
        """Speichert nur den Draft, ohne den Wizard zu schließen."""
        self.draft.current_step = self.current_step
        if self.draft_manager.save_draft(self.draft):
            self._show_success("Entwurf gespeichert!")
        else:
            self._show_error("Fehler beim Speichern des Entwurfs")
    
    def _finish_wizard(self, *args):
        """Schließt den Wizard ab und speichert das Setting."""
        if not self._nav_debounce_check():
            return
        validation = self._validate_draft()
        if not validation["is_valid"]:
            self._show_error("\n".join(validation["errors"]))
            return
        
        try:
            final_setting = self.draft.to_final_setting()
            
            from functions.setting_funktionen import CustomElementManager
            from models.charakter import Charakter
            
            dummy = Charakter()
            manager = CustomElementManager(dummy)
            manager.save_setting(self.draft.name, final_setting)
            
            if self.edit_draft:
                self.draft_manager.delete_draft(self.edit_draft.name)
            
            if self.dialog:
                self.dialog.dismiss()
            
            self._show_success(f"Setting '{self.draft.name}' wurde {'aktualisiert' if self.edit_draft else 'erstellt'}.")
            
            if self.callback:
                self.callback(self.draft.name, final_setting)
            
            Logger.info(f"Setting '{self.draft.name}' erfolgreich gespeichert.")
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Settings: {e}")
            self._show_error(f"Fehler beim Speichern: {e}")
    
    def _show_error(self, message: str):
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_warning_dialog(message)
        except Exception:
            pass
    
    def _show_success(self, message: str):
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog(message)
        except Exception:
            pass


def show_setting_assistent(controller, callback: Optional[Callable] = None, edit_draft: Optional[SettingDraft] = None):
    """Zeigt den Setting-Assistenten."""
    wizard = SettingAssistentWizard(controller, callback=callback, edit_draft=edit_draft)
    wizard.start_wizard()


class SettingAssistentDialogHandler:
    """Handler für den Setting-Assistenten."""
    
    def __init__(self, controller):
        self.controller = controller
    
    def show_assistent(self, edit_draft: Optional[SettingDraft] = None):
        """Zeigt den Setting-Assistenten."""
        show_setting_assistent(self.controller, edit_draft=edit_draft)
    
    def show_drafts_overview(self):
        """Zeigt eine Übersicht aller Drafts."""
        manager = DraftManager()
        drafts = manager.list_drafts()

        if not drafts:
            self._show_no_drafts_message()
            return

        if _mobile:
            content_height = dp(300)
            content_spacing = dp(4)
            dialog_size = (0.95, 0.7)
        else:
            content_height = "400dp"
            content_spacing = "12dp"
            dialog_size = (0.9, 0.7)

        content = MDBoxLayout(orientation="vertical", spacing=content_spacing, size_hint_y=None, height=content_height)

        scroll = TextFieldScrollView(size_hint_y=1)
        list_container = MDList(size_hint_y=None)
        list_container.bind(minimum_height=list_container.setter('height'))

        for draft in drafts:
            list_item = MDListItem(
                on_release=lambda x, d=draft: self._open_draft(d)
            )
            list_item.add_widget(MDListItemHeadlineText(text=draft.name))

            info_text = f"{draft.mode} • Schritt {draft.current_step}"
            list_item.add_widget(MDListItemSupportingText(text=info_text))

            delete_btn = MDButton(
                style="text",
                size_hint_x=None,
                width="40dp",
                on_release=lambda b, d=draft: self._delete_draft(d)
            )
            delete_btn.add_widget(MDButtonIcon(icon="delete"))
            list_item.add_widget(delete_btn)

            list_container.add_widget(list_item)

        scroll.add_widget(list_container)
        content.add_widget(scroll)

        if _mobile:
            close_btn = MDButton(style="text", size_hint_x=None, width=dp(40))
            close_btn.add_widget(MDButtonIcon(icon="close"))
        else:
            close_btn = MDButton(MDButtonText(text="Schließen"), style="text")

        dialog = MDDialog(
            MDDialogHeadlineText(text="Entwürfe" if _mobile else "Gespeicherte Entwürfe"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(close_btn),
            size_hint=dialog_size,
        )
        close_btn.bind(on_release=lambda x: dialog.dismiss())
        dialog.open()
    
    def _show_no_drafts_message(self):
        """Zeigt eine Meldung wenn keine Drafts existieren."""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_success_dialog("Keine gespeicherten Entwürfe vorhanden.")
        except Exception:
            pass
    
    def _open_draft(self, draft: SettingDraft):
        """Öffnet einen Draft im Wizard."""
        self.show_assistent(edit_draft=draft)
    
    def _delete_draft(self, draft: SettingDraft):
        """Löscht einen Draft."""
        manager = DraftManager()
        manager.delete_draft(draft.name)
        self._show_success(f"Entwurf '{draft.name}' gelöscht.")
