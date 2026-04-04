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
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemTrailingCheckbox
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.divider import MDDivider

import os
import sys
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

Builder.load_file(os.path.join(os.path.dirname(__file__), 'setting_assistent_view.kv'))


class SettingAssistentWizard:
    """
    Haupt-Wizard-Klasse für die Setting-Erstellung.
    Verwaltet den mehrstufigen Prozess.
    """
    
    MODES = {
        "empty": {"label": "Leer starten", "icon": "file-outline", "description": "Komplett leeres Setting erstellen"},
        "template": {"label": "Vorlage verwenden", "icon": "file-document-outline", "description": "Auf bestehendem Setting aufbauen"},
        "merge": {"label": "Zusammenführen", "icon": "merge", "description": "Mehrere Settings kombinieren"},
        "extract": {"label": "Aus Charakter", "icon": "account-outline", "description": "Aus aktuellem Charakter extrahieren"}
    }
    
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
        
        self.steps = [
            {"title": "Name & Beschreibung", "handler": self._create_step_name},
            {"title": "Modus & Basis", "handler": self._create_step_modus},
            {"title": "Elemente konfigurieren", "handler": self._create_step_elemente},
            {"title": "Vorschau & Speichern", "handler": self._create_step_vorschau}
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
        Logger.info(f"Zeige Wizard-Schritt {self.current_step}: {step['title']}")
        
        if self.dialog:
            self.dialog.dismiss()
        
        content = step['handler']()
        
        nav_layout = MDBoxLayout(
            orientation="horizontal",
            spacing="8dp",
            size_hint_y=None,
            height="50dp"
        )
        
        if self.current_step > 1:
            back_btn = MDButton(style="outlined", on_release=self._previous_step)
            back_btn.add_widget(MDButtonIcon(icon="arrow-left"))
            back_btn.add_widget(MDButtonText(text="Zurück"))
            nav_layout.add_widget(back_btn)
        
        cancel_btn = MDButton(style="text", on_release=self._cancel_wizard)
        cancel_btn.add_widget(MDButtonText(text="Abbrechen"))
        nav_layout.add_widget(cancel_btn)
        
        save_draft_btn = MDButton(style="tonal", on_release=self._save_draft_only)
        save_draft_btn.add_widget(MDButtonText(text="Entwurf speichern"))
        nav_layout.add_widget(save_draft_btn)
        
        is_last_step = self.current_step >= self._get_total_steps()
        next_btn = MDButton(style="filled", on_release=self._finish_wizard if is_last_step else self._next_step)
        next_btn.add_widget(MDButtonIcon(icon="check" if is_last_step else "arrow-right"))
        next_btn.add_widget(MDButtonText(text="Speichern" if is_last_step else "Weiter"))
        nav_layout.add_widget(next_btn)
        
        main_layout = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="750dp")
        
        progress_text = f"Schritt {self.current_step} von {self._get_total_steps()}"
        if self.edit_draft:
            progress_text += " (Bearbeiten)"
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
        
        title = "Setting erstellen" if not self.edit_draft else f"Setting bearbeiten: {self.edit_draft.name}"
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(main_layout),
            size_hint=(0.9, 0.9),
            auto_dismiss=False,
        )
        self.dialog.open()
    
    def _create_step_name(self):
        """Schritt 1: Name & Beschreibung"""
        layout = MDScrollView(size_hint_y=1, bar_width=dp(12), bar_margin=dp(12))
        content = MDBoxLayout(orientation="vertical", spacing="16dp", size_hint_y=None, height="500dp")
        
        name_label = MDLabel(text="Name des Settings *", theme_text_color="Primary", bold=True)
        content.add_widget(name_label)
        
        self.name_field = MDTextField(mode="outlined", text=self.draft.name)
        self.name_field.add_widget(MDTextFieldHintText(text="Name (max. 50 Zeichen)"))
        self.name_field.bind(text=self._update_name)
        content.add_widget(self.name_field)
        
        desc_label = MDLabel(text="Beschreibung", theme_text_color="Primary", bold=True)
        content.add_widget(desc_label)
        
        self.desc_field = MDTextField(mode="outlined", text=self.draft.description, multiline=True, size_hint_y=None, height="150dp")
        self.desc_field.add_widget(MDTextFieldHintText(text="Kurze Beschreibung (optional)"))
        self.desc_field.bind(text=self._update_description)
        content.add_widget(self.desc_field)
        
        layout.add_widget(content)
        return layout
    
    def _create_step_modus(self):
        """Schritt 2: Modus & Basis-Setting Auswahl"""
        layout = MDScrollView(size_hint_y=1, bar_width=dp(12), bar_margin=dp(12))
        content = MDBoxLayout(orientation="vertical", spacing="16dp", size_hint_y=None, height="850dp")
        
        mode_label = MDLabel(text="Modus wählen", theme_text_color="Primary", bold=True)
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
        self.setting_selection_box = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height="300dp"
        )
        self._update_setting_selection_ui()
        content.add_widget(self.setting_selection_box)
    
    def _update_setting_selection_ui(self):
        """Aktualisiert die Setting-Auswahl-UI basierend auf dem gewählten Modus."""
        self.setting_selection_box.clear_widgets()
        
        mode = self.draft.mode
        
        if mode == "empty":
            info = MDLabel(
                text="Keine Basiseinstellungen erforderlich.",
                theme_text_color="Secondary"
            )
            self.setting_selection_box.add_widget(info)
            self.setting_selection_box.height = "50dp"
            return
        
        if mode == "template":
            self.setting_selection_box.height = "300dp"
            label = MDLabel(text="Basis-Setting wählen:", bold=True)
            self.setting_selection_box.add_widget(label)
            
            self.template_setting_dropdown = self._create_setting_dropdown()
            self.setting_selection_box.add_widget(self.template_setting_dropdown)
            
        elif mode == "merge":
            self.setting_selection_box.height = "300dp"
            label = MDLabel(text="Settings zum Zusammenführen wählen:", bold=True)
            self.setting_selection_box.add_widget(label)
            
            self.merge_setting_list = self._create_merge_setting_list()
            self.setting_selection_box.add_widget(self.merge_setting_list)
        
        elif mode == "extract":
            info = MDLabel(
                text="Das aktuelle Setting wird als Basis verwendet.",
                theme_text_color="Secondary"
            )
            self.setting_selection_box.add_widget(info)
            self.setting_selection_box.height = "50dp"
    
    def _create_setting_dropdown(self) -> MDCard:
        """Erstellt eine Liste für die Template-Auswahl mit Checkboxen."""
        card = MDCard(style="outlined", padding="12dp", size_hint_y=None, height="250dp")
        
        try:
            from models.charakter import Charakter
            from functions.setting_funktionen import CustomElementManager
            charakter = Charakter()
            manager = CustomElementManager(charakter)
            available_settings = list(manager.settings.keys())
            available_settings.sort()
        except Exception:
            available_settings = ["SWAE", "Deadlands", "Fantasy Kompendium"]
        
        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        self.template_setting_checkboxes = {}
        for setting_name in available_settings:
            is_selected = setting_name in self.draft.base_settings
            list_item = MDListItem(
                size_hint_y=None,
                height=dp(48)
            )
            list_item.add_widget(MDListItemHeadlineText(text=setting_name))
            checkbox = MDListItemTrailingCheckbox(
                active=is_selected,
                on_active=lambda inst, val, s=setting_name: self._select_template_setting(s, val)
            )
            list_item.add_widget(checkbox)
            list_layout.add_widget(list_item)
            self.template_setting_checkboxes[setting_name] = checkbox
        
        scroll = MDScrollView(size_hint_y=1, bar_width=dp(12), bar_margin=dp(8))
        scroll.add_widget(list_layout)
        card.add_widget(scroll)
        
        return card
    
    def _create_merge_setting_list(self) -> MDCard:
        """Erstellt eine Liste für die Merge-Auswahl mit Checkboxen."""
        card = MDCard(style="outlined", padding="12dp", size_hint_y=None, height="250dp")
        
        try:
            from models.charakter import Charakter
            from functions.setting_funktionen import CustomElementManager
            charakter = Charakter()
            manager = CustomElementManager(charakter)
            available_settings = list(manager.settings.keys())
            available_settings.sort()
        except Exception:
            available_settings = ["SWAE", "Deadlands", "Fantasy Kompendium"]
        
        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for setting_name in available_settings:
            is_selected = setting_name in self.draft.base_settings
            list_item = MDListItem()
            list_item.add_widget(MDListItemHeadlineText(text=setting_name))
            checkbox = MDListItemTrailingCheckbox(
                active=is_selected,
                on_active=lambda inst, val, s=setting_name: self._toggle_merge_setting(s, val)
            )
            list_item.add_widget(checkbox)
            list_layout.add_widget(list_item)
        
        scroll = MDScrollView(size_hint_y=1, bar_width=dp(12), bar_margin=dp(8))
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
    
    def _create_mode_card(self, mode_id: str, mode_info: dict) -> tuple:
        """Erstellt eine Mode-Auswahlkarte. Gibt (card, checkbox) zurück."""
        card = MDCard(
            style="elevated",
            padding="12dp",
            size_hint_y=None,
            height="90dp",
            on_release=lambda x: self._select_mode(mode_id)
        )
        
        is_selected = self.draft.mode == mode_id
        
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
        layout = MDScrollView(size_hint_y=1, bar_width=dp(12), bar_margin=dp(12))
        content = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="680dp")
        
        info_label = MDLabel(
            text="Wähle die Kategorien und Elemente für dein Setting aus.",
            theme_text_color="Secondary"
        )
        content.add_widget(info_label)
        
        stats = calculate_setting_statistics(self.draft.setting_data)
        stats_text = format_statistics_for_display(stats)
        
        stats_card = MDCard(style="elevated", padding="12dp", size_hint_y=None, height="180dp")
        stats_content = MDLabel(text=stats_text, markup=True)
        stats_card.add_widget(stats_content)
        content.add_widget(stats_card)
        
        tabs_label = MDLabel(
            text="Verfügbare Kategorien (klicken für Details):",
            theme_text_color="Primary",
            bold=True
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
        card = MDCard(
            style="elevated",
            padding="12dp",
            size_hint_y=None,
            height="70dp",
            on_release=lambda x: self._open_category_editor(cat_id, cat_name)
        )
        
        card_content = MDBoxLayout(orientation="horizontal", spacing="12dp")
        
        icon_btn = MDButton(style="tonal", size_hint_x=None, width="48dp", height="48dp")
        icon_btn.add_widget(MDButtonIcon(icon=cat_icon))
        card_content.add_widget(icon_btn)
        
        info_layout = MDBoxLayout(orientation="vertical", size_hint_x=1)
        
        title = MDLabel(text=cat_name, bold=True, size_hint_y=None, height="24dp")
        info_layout.add_widget(title)
        
        gesamt = stats.get("gesamt", 0)
        aktiv = stats.get("aktiv", 0)
        inaktiv = stats.get("inaktiv", 0)
        
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
        
        content = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="500dp")
        
        list_layout = MDList(size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for item_name in items[:50]:
            list_item = MDListItem(
                size_hint_y=None,
                height=dp(48)
            )
            list_item.add_widget(MDListItemHeadlineText(text=str(item_name)))
            
            is_active = True
            if isinstance(category_data, dict) and isinstance(category_data.get(item_name), dict):
                is_active = category_data.get(item_name, {}).get("aktiv", True)
            
            checkbox = MDListItemTrailingCheckbox(
                active=is_active,
                on_active=lambda inst, val, item=item_name, cid=cat_id: self._toggle_category_item(cid, item, val)
            )
            list_item.add_widget(checkbox)
            list_layout.add_widget(list_item)
        
        scroll = MDScrollView(size_hint_y=1, bar_width=dp(12), bar_margin=dp(8))
        scroll.add_widget(list_layout)
        content.add_widget(scroll)
        
        dialog = MDDialog(
            MDDialogHeadlineText(text=f"{cat_name} bearbeiten"),
            MDDialogContentContainer(content),
            size_hint=(0.9, 0.7),
        )
        
        cancel_btn = MDButton(MDButtonText(text="Abbrechen"), style="text")
        cancel_btn.bind(on_release=lambda x: dialog.dismiss())
        
        confirm_btn = MDButton(MDButtonText(text="Bestätigen"), style="filled")
        confirm_btn.bind(on_release=lambda x: self._on_category_confirm(dialog))
        
        dialog.add_widget(cancel_btn)
        dialog.add_widget(confirm_btn)
        
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
    
    def _resolve_conflict(self, index: int, resolution: str):
        """Löst einen Konflikt auf."""
        Logger.info(f"Konflikt {index} gelöst mit: {resolution}")
        self.draft.conflicts_resolved += 1
    
    def _create_step_vorschau(self):
        """Schritt 4: Vorschau & Speichern"""
        layout = MDScrollView(size_hint_y=1, bar_width=dp(12), bar_margin=dp(12))
        content = MDBoxLayout(orientation="vertical", spacing="16dp", size_hint_y=None, height="680dp")
        
        preview_card = MDCard(style="elevated", padding="16dp", size_hint_y=None, height="400dp")
        
        preview_content = MDBoxLayout(orientation="vertical", spacing="8dp")
        
        name_label = MDLabel(text=f"[b]{self.draft.name}[/b]", markup=True, size_hint_y=None, height="30dp")
        preview_content.add_widget(name_label)
        
        if self.draft.description:
            desc_label = MDLabel(text=f"[i]{self.draft.description}[/i]", markup=True, theme_text_color="Secondary")
            preview_content.add_widget(desc_label)
        
        mode_label = MDLabel(
            text=f"Modus: {self.MODES.get(self.draft.mode, {}).get('label', self.draft.mode)}",
            theme_text_color="Secondary"
        )
        preview_content.add_widget(mode_label)
        
        if self.draft.base_settings:
            bases = ", ".join(self.draft.base_settings)
            bases_label = MDLabel(text=f"Basierend auf: {bases}", theme_text_color="Secondary")
            preview_content.add_widget(bases_label)
        
        preview_content.add_widget(MDDivider())
        
        stats = calculate_setting_statistics(self.draft.setting_data)
        stats_text = format_statistics_for_display(stats)
        stats_label = MDLabel(text=stats_text, markup=True)
        preview_content.add_widget(stats_label)
        
        preview_card.add_widget(preview_content)
        content.add_widget(preview_card)
        
        validation = self._validate_draft()
        if not validation["is_valid"]:
            error_card = MDCard(style="elevated", padding="12dp", md_bg_color=(1, 0, 0, 0.1))
            error_content = MDLabel(
                text="[color=ff4444]Fehler:[/color] " + "\n".join(validation["errors"]),
                markup=True,
                theme_text_color="Error"
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
    
    def _next_step(self, *args):
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
        self.current_step -= 1
        self.draft.current_step = self.current_step
        self._show_current_step()
    
    def _cancel_wizard(self, *args):
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
        
        content = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="400dp")
        
        scroll = MDScrollView(size_hint_y=1)
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
        
        dialog = MDDialog(
            MDDialogHeadlineText(text="Gespeicherte Entwürfe"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Schließen"), style="text", on_release=lambda x: dialog.dismiss())
            ),
            size_hint=(0.9, 0.7),
        )
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
