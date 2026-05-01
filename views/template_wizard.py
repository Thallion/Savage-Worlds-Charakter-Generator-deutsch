# views/template_wizard.py
"""
Template-Wizard für benutzerfreundliche Template-Erstellung
Mehrstufiger Dialog zum Erstellen von Charakter-Templates
"""

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.divider import MDDivider
from views.ui_components import TextFieldScrollView

from kivy.logger import Logger
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, DictProperty, ListProperty

import json
import os
import time
from datetime import datetime
from pathlib import Path

from services.service_container import service_container
from utils.path_utils import get_application_root


class TemplateWizardDialog:
    """
    Haupt-Wizard-Klasse für die Template-Erstellung
    Verwaltet den mehrstufigen Dialog-Prozess
    """
    
    def __init__(self, callback=None):
        self.app = MDApp.get_running_app()
        self.callback = callback
        self.current_step = 0
        self.template_data = {}
        self.dialog = None
        
        # Wizard-Schritte definieren
        self.steps = [
            {"title": "Allgemeine Daten", "handler": self._create_general_step},
            {"title": "Attribute", "handler": self._create_attributes_step},
            {"title": "Fertigkeiten", "handler": self._create_skills_step},
            {"title": "Handicaps", "handler": self._create_handicaps_step},
            {"title": "Talente", "handler": self._create_edges_step},
            {"title": "Mächte", "handler": self._create_powers_step},
            {"title": "Ausrüstung", "handler": self._create_equipment_step},
            {"title": "Aufstiege", "handler": self._create_advances_step},
            {"title": "Vorschau & Speichern", "handler": self._create_preview_step}
        ]
        
        # Initialisiere Template-Daten mit Standardwerten
        self._initialize_template_data()
    
    def _initialize_template_data(self):
        """Initialisiert Template-Daten mit Standardwerten"""
        self.template_data = {
            "name": "",
            "description": "",
            "setting": "SWAE",
            "race": "Mensch",
            "profile": {
                "age": "",
                "gender": "",
                "concept": "",
                "languages": "",
                "rank": "Anfänger"
            },
            "starting_capital": 500,
            "starting_attribute_points": 5,
            "starting_skill_points": 12,
            "starting_advances": 0,
            "advances_to_apply": [],
            "race_choices": {},
            "attributes": {
                "Stärke": 4,
                "Geschicklichkeit": 4,
                "Konstitution": 4,
                "Verstand": 4,
                "Willenskraft": 4
            },
            "skills": {},
            "handicaps": [],
            "edges": [],
            "powers": [],
            "power_points": 0,
            "equipment": [],
            "custom_equipment": [],
            "generation_options": {
                "strict_point_allocation": False,
                "allow_over_attribute": True,
                "auto_save": True,
                "save_path": "auto_generated/wizard",
                "complete_character_generation": True
            }
        }
    
    def start_wizard(self):
        """Startet den Template-Wizard"""
        Logger.info("Template-Wizard gestartet")
        self.current_step = 0
        self._show_current_step()
    
    def _show_current_step(self):
        """Zeigt den aktuellen Wizard-Schritt"""
        if self.current_step >= len(self.steps):
            self._finish_wizard()
            return
        
        step = self.steps[self.current_step]
        Logger.info(f"Zeige Wizard-Schritt {self.current_step + 1}: {step['title']}")
        
        # Dialog schließen falls bereits offen
        if self.dialog:
            self.dialog.dismiss()
        
        # Erstelle Schritt-Inhalt
        content = step['handler']()
        
        # Navigation Buttons
        nav_layout = MDBoxLayout(
            orientation="horizontal",
            spacing="8dp",
            size_hint_y=None,
            height="50dp",
            adaptive_height=True
        )
        
        # Zurück Button (außer bei erstem Schritt)
        if self.current_step > 0:
            back_btn = MDButton(
                style="outlined",
                on_release=self._previous_step
            )
            back_btn.add_widget(MDButtonIcon(icon="arrow-left"))
            back_btn.add_widget(MDButtonText(text="Zurück"))
            nav_layout.add_widget(back_btn)
        
        # Weiter/Fertig Button
        is_last_step = self.current_step == len(self.steps) - 1
        next_btn = MDButton(
            style="filled",
            on_release=self._finish_wizard if is_last_step else self._next_step
        )
        next_btn.add_widget(MDButtonIcon(icon="check" if is_last_step else "arrow-right"))
        next_btn.add_widget(MDButtonText(text="Template erstellen" if is_last_step else "Weiter"))
        nav_layout.add_widget(next_btn)
        
        # Hauptlayout
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height=self._calculate_dialog_height()
        )
        
        # Progress Indicator
        progress_text = f"Schritt {self.current_step + 1} von {len(self.steps)}"
        progress_label = MDLabel(
            text=progress_text,
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        main_layout.add_widget(progress_label)
        
        # Schritt-Inhalt
        main_layout.add_widget(content)
        main_layout.add_widget(MDDivider())
        main_layout.add_widget(nav_layout)
        
        # Dialog erstellen (KivyMD 2.0.1 Format)
        self.dialog = MDDialog(
            MDDialogHeadlineText(text=f"Template-Wizard: {step['title']}"),
            MDDialogContentContainer(main_layout),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=self._cancel_wizard
                )
            ),
            size_hint=(0.9, 0.7),
            auto_dismiss=False,
        )

        self.dialog.open()
    
    def _calculate_dialog_height(self):
        """Berechnet optimale Dialog-Höhe basierend auf Schritt"""
        base_height = "400dp"
        if self.current_step in [2, 3, 4]:  # Skills, Handicaps, Edges - mehr Platz
            base_height = "600dp"
        elif self.current_step == 7:  # Aufstiege - mehr Platz
            base_height = "600dp"
        elif self.current_step == 8:  # Preview - noch mehr Platz
            base_height = "700dp"
        return base_height
    
    def _create_general_step(self):
        """Erstellt Schritt 1: Allgemeine Daten"""
        layout = TextFieldScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height=self._get_content_height()
        )
        
        # Name
        self.name_field = MDTextField(
            MDTextFieldHintText(text="Charakter-Name"),
            mode="outlined",
            text=self.template_data.get("name", "")
        )
        self.name_field.bind(text=self._update_name)
        content.add_widget(self.name_field)

        # Beschreibung
        self.description_field = MDTextField(
            MDTextFieldHintText(text="Beschreibung"),
            mode="outlined",
            text=self.template_data.get("description", ""),
            multiline=True
        )
        self.description_field.bind(text=self._update_description)
        content.add_widget(self.description_field)

        # Setting Dropdown
        self._create_setting_dropdown()
        setting_label = MDLabel(text="Setting:", size_hint_y=None, height="30dp")
        self.setting_button = MDButton(
            style="outlined",
            on_release=self._open_setting_menu
        )
        self.setting_button.add_widget(MDButtonText(text=self.template_data.get("setting", "SWAE")))
        content.add_widget(setting_label)
        content.add_widget(self.setting_button)

        # Volk Dropdown
        self._create_race_dropdown()
        race_label = MDLabel(text="Abstammung:", size_hint_y=None, height="30dp")
        self.race_button = MDButton(
            style="outlined",
            on_release=self._open_race_menu
        )
        self.race_button.add_widget(MDButtonText(text=self.template_data.get("race", "Mensch")))
        content.add_widget(race_label)
        content.add_widget(self.race_button)

        # Profile Felder
        profile = self.template_data.get("profile", {})

        self.concept_field = MDTextField(
            MDTextFieldHintText(text="Konzept"),
            mode="outlined",
            text=profile.get("concept", "")
        )
        self.concept_field.bind(text=self._update_concept)
        content.add_widget(self.concept_field)

        self.gender_field = MDTextField(
            MDTextFieldHintText(text="Geschlecht"),
            mode="outlined",
            text=profile.get("gender", "")
        )
        self.gender_field.bind(text=self._update_gender)
        content.add_widget(self.gender_field)
        
        layout.add_widget(content)
        return layout
    
    def _create_attributes_step(self):
        """Erstellt Schritt 2: Attribute"""
        layout = TextFieldScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height=self._get_content_height()
        )
        
        # Info-Text
        info_label = MDLabel(
            text="Setze die gewünschten Attributswerte (W4=4, W6=6, W8=8, W10=10, W12=12)",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="40dp"
        )
        content.add_widget(info_label)
        
        # Attribut-Eingaben
        self.attribute_fields = {}
        attributes = ["Stärke", "Geschicklichkeit", "Konstitution", "Verstand", "Willenskraft"]
        
        for attr in attributes:
            attr_layout = MDBoxLayout(
                orientation="horizontal",
                spacing="8dp",
                size_hint_y=None,
                height="50dp"
            )
            
            label = MDLabel(
                text=f"{attr}:",
                size_hint_x=0.4
            )
            
            field = MDTextField(
                MDTextFieldHintText(text=f"W4-W12"),
                mode="outlined",
                text=str(self.template_data["attributes"].get(attr, 4)),
                input_filter="int",
                size_hint_x=0.6
            )
            field.bind(text=lambda instance, value, attr=attr: self._update_attribute(attr, value))
            
            self.attribute_fields[attr] = field
            attr_layout.add_widget(label)
            attr_layout.add_widget(field)
            content.add_widget(attr_layout)
        
        # Punkte-Info
        self.points_info = MDLabel(
            text="",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        content.add_widget(self.points_info)
        self._update_attribute_points()
        
        layout.add_widget(content)
        return layout
    
    def _create_skills_step(self):
        """Erstellt Schritt 3: Fertigkeiten"""
        layout = TextFieldScrollView()

        # Verfügbare Fertigkeiten holen
        skills = self._get_available_skills()
        self.skill_fields = {}

        # Content-Höhe dynamisch berechnen
        content_height = max(800, 80 + len(skills) * 53)

        content = MDBoxLayout(
            orientation="vertical",
            spacing="8dp",
            size_hint_y=None,
            height=f"{content_height}dp"
        )

        # Info-Text
        info_label = MDLabel(
            text=f"Wähle Fertigkeiten aus und setze ihre Werte ({len(skills)} verfügbar)",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        content.add_widget(info_label)
        
        for skill in skills:
            skill_layout = MDBoxLayout(
                orientation="horizontal",
                spacing="8dp",
                size_hint_y=None,
                height="45dp"
            )
            
            # Checkbox
            checkbox = MDCheckbox(
                size_hint_x=None,
                width="40dp",
                active=skill in self.template_data["skills"],
                on_active=lambda instance, value, skill=skill: self._toggle_skill(skill, value)
            )
            
            # Label
            label = MDLabel(
                text=skill,
                size_hint_x=0.5
            )
            
            # Wert-Eingabe
            field = MDTextField(
                MDTextFieldHintText(text="Wert"),
                mode="outlined",
                text=str(self.template_data["skills"].get(skill, 4)),
                input_filter="int",
                size_hint_x=0.3,
                disabled=skill not in self.template_data["skills"]
            )
            field.bind(text=lambda instance, value, skill=skill: self._update_skill(skill, value))
            
            self.skill_fields[skill] = (checkbox, field)
            skill_layout.add_widget(checkbox)
            skill_layout.add_widget(label)
            skill_layout.add_widget(field)
            content.add_widget(skill_layout)
        
        layout.add_widget(content)
        return layout
    
    def _create_handicaps_step(self):
        """Erstellt Schritt 4: Handicaps"""
        layout = MDScrollView()

        # Verfügbare Handicaps holen
        handicaps = self._get_available_handicaps()
        self.handicap_checkboxes = {}
        self._available_handicaps = handicaps

        # Content-Höhe dynamisch berechnen
        num_handicaps = len(handicaps)
        content_height = max(600, 100 + num_handicaps * 45)

        content = MDBoxLayout(
            orientation="vertical",
            spacing="8dp",
            size_hint_y=None,
            height=f"{content_height}dp"
        )

        # Punkte-Anzeige oben
        self.handicap_points_label = MDLabel(
            text=f"Handicap-Punkte: {self._get_handicap_points()} / 4",
            theme_text_color="Secondary",
            bold=True,
            size_hint_y=None,
            height="35dp"
        )
        content.add_widget(self.handicap_points_label)

        info_label = MDLabel(
            text="Wähle Handicaps (leicht = 1 Pkt, schwer = 2 Pkt, max. 4 Pkt)",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        content.add_widget(info_label)
        content.add_widget(MDDivider())

        # Sortiert nach Name alphabetisch
        sorted_keys = sorted(handicaps.keys(), key=lambda k: (handicaps[k]["name"], handicaps[k]["stufe"]))

        for key in sorted_keys:
            h = handicaps[key]
            handicap_layout = MDBoxLayout(
                orientation="horizontal",
                spacing="8dp",
                size_hint_y=None,
                height="40dp"
            )

            # Prüfe ob dieses Handicap bereits ausgewählt ist
            is_selected = any(
                sel.get("key") == key for sel in self.template_data["handicaps"]
            ) if self.template_data["handicaps"] else False

            checkbox = MDCheckbox(
                size_hint_x=None,
                width="40dp",
                active=is_selected,
                on_active=lambda instance, value, k=key: self._toggle_handicap(k, value)
            )

            # Label mit Name, Stufe und Punkten
            stufe_label = "leicht" if h["stufe"] == "leicht" else "schwer"
            punkte = h["punkte"]
            label = MDLabel(
                text=f"{h['name']} ({stufe_label}) - {punkte} Pkt",
                size_hint_x=0.8
            )

            # Info-Button für Beschreibung
            info_btn = MDButton(
                style="text",
                size_hint_x=None,
                width="40dp",
                on_release=lambda instance, name=h["name"], desc=h["beschreibung"]: self._show_handicap_description(name, desc)
            )
            info_btn.add_widget(MDButtonIcon(icon="information-outline"))

            self.handicap_checkboxes[key] = checkbox
            handicap_layout.add_widget(checkbox)
            handicap_layout.add_widget(label)
            handicap_layout.add_widget(info_btn)
            content.add_widget(handicap_layout)

        layout.add_widget(content)
        return layout
    
    def _create_edges_step(self):
        """Erstellt Schritt 5: Talente"""
        layout = MDScrollView()

        # Verfügbare Talente holen
        edges = self._get_available_edges()
        self.edge_checkboxes = {}

        # Content-Höhe dynamisch berechnen
        content_height = max(800, 80 + len(edges) * 48)

        content = MDBoxLayout(
            orientation="vertical",
            spacing="8dp",
            size_hint_y=None,
            height=f"{content_height}dp"
        )

        info_label = MDLabel(
            text=f"Wähle Talente für deinen Charakter ({len(edges)} verfügbar)",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        content.add_widget(info_label)

        # Alphabetisch sortieren
        edges = sorted(edges)

        for edge in edges:
            edge_layout = MDBoxLayout(
                orientation="horizontal",
                spacing="8dp",
                size_hint_y=None,
                height="40dp"
            )
            
            checkbox = MDCheckbox(
                size_hint_x=None,
                width="40dp",
                active=edge in self.template_data["edges"],
                on_active=lambda instance, value, edge=edge: self._toggle_edge(edge, value)
            )
            
            label = MDLabel(text=edge)
            
            self.edge_checkboxes[edge] = checkbox
            edge_layout.add_widget(checkbox)
            edge_layout.add_widget(label)
            content.add_widget(edge_layout)
        
        layout.add_widget(content)
        return layout
    
    def _create_powers_step(self):
        """Erstellt Schritt 6: Mächte"""
        layout = TextFieldScrollView()

        # Mächte vorab holen für Höhenberechnung
        powers = self._get_available_powers()

        # Content-Höhe dynamisch berechnen
        content_height = max(500, 120 + len(powers) * 48)

        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height=f"{content_height}dp"
        )

        info_label = MDLabel(
            text=f"Wähle Mächte (nur für arkane Charaktere, {len(powers)} verfügbar)",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        content.add_widget(info_label)
        
        # Machtpunkte
        self.power_points_field = MDTextField(
            MDTextFieldHintText(text="Machtpunkte"),
            mode="outlined",
            text=str(self.template_data.get("power_points", 0)),
            input_filter="int"
        )
        self.power_points_field.bind(text=self._update_power_points)
        content.add_widget(self.power_points_field)
        
        # Verfügbare Mächte (bereits oben geladen)
        self.power_checkboxes = {}
        
        for power in powers:
            power_layout = MDBoxLayout(
                orientation="horizontal",
                spacing="8dp",
                size_hint_y=None,
                height="40dp"
            )
            
            checkbox = MDCheckbox(
                size_hint_x=None,
                width="40dp",
                active=power in self.template_data["powers"],
                on_active=lambda instance, value, power=power: self._toggle_power(power, value)
            )
            
            label = MDLabel(text=power)
            
            self.power_checkboxes[power] = checkbox
            power_layout.add_widget(checkbox)
            power_layout.add_widget(label)
            content.add_widget(power_layout)
        
        layout.add_widget(content)
        return layout
    
    def _create_equipment_step(self):
        """Erstellt Schritt 7: Ausrüstung"""
        layout = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height=self._get_content_height()
        )
        
        info_label = MDLabel(
            text="Startausrüstung auswählen",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        content.add_widget(info_label)
        
        # Startkapital
        self.capital_field = MDTextField(
            MDTextFieldHintText(text="Startkapital"),
            mode="outlined",
            text=str(self.template_data.get("starting_capital", 500)),
            input_filter="int"
        )
        self.capital_field.bind(text=self._update_capital)
        content.add_widget(self.capital_field)

        # Equipment Text-Liste (vereinfacht)
        self.equipment_field = MDTextField(
            MDTextFieldHintText(text="Ausrüstung (eine pro Zeile)"),
            mode="outlined",
            text="\n".join(self.template_data.get("equipment", [])),
            multiline=True
        )
        self.equipment_field.bind(text=self._update_equipment)
        content.add_widget(self.equipment_field)
        
        layout.add_widget(content)
        return layout
    
    # ------------------------------------------------------------------
    # Schritt: Aufstiege
    # ------------------------------------------------------------------
    def _create_advances_step(self):
        """Erstellt Schritt 8: Aufstiege (starting_advances + advances_to_apply)."""
        layout = TextFieldScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter('height'))

        intro = MDLabel(
            text="Aufstiege für Veteran/Erfahren etc. festlegen (0 = reiner Anfänger).",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="40dp",
        )
        content.add_widget(intro)

        # starting_advances
        self.starting_advances_field = MDTextField(
            MDTextFieldHintText(text="Anzahl Aufstiege (0-20)"),
            mode="outlined",
            text=str(self.template_data.get("starting_advances", 0)),
            input_filter="int",
            size_hint_y=None,
            height="56dp",
        )
        def _set_starting_advances(instance, value):
            try:
                n = max(0, min(20, int(value))) if value else 0
            except ValueError:
                n = 0
            self.template_data["starting_advances"] = n
        self.starting_advances_field.bind(text=_set_starting_advances)
        content.add_widget(self.starting_advances_field)

        # Container für die Liste der advances_to_apply
        self._advances_container = MDBoxLayout(
            orientation="vertical",
            spacing="6dp",
            size_hint_y=None,
        )
        self._advances_container.bind(minimum_height=self._advances_container.setter('height'))
        content.add_widget(self._advances_container)
        self._render_advances_list()

        # Button: Aufstieg hinzufügen
        add_btn = MDButton(style="outlined", size_hint_y=None, height="48dp")
        add_btn.add_widget(MDButtonIcon(icon="plus"))
        add_btn.add_widget(MDButtonText(text="Aufstieg hinzufügen"))
        add_btn.bind(on_release=self._add_advance_entry)
        content.add_widget(add_btn)

        layout.add_widget(content)
        return layout

    def _render_advances_list(self):
        """Rendert die aktuellen advances_to_apply als editierbare Karten."""
        if not hasattr(self, '_advances_container'):
            return
        self._advances_container.clear_widgets()

        advances = self.template_data.get("advances_to_apply", [])
        for index, advance in enumerate(advances):
            row = MDCard(style="outlined", padding="8dp",
                         size_hint_y=None, height="80dp")
            inner = MDBoxLayout(orientation="horizontal", spacing="8dp")

            advance_type = advance.get('type', 'attribute')
            advance_name = advance.get('name', '')

            # Typ-Dropdown (Text-Button)
            type_btn = MDButton(style="outlined", size_hint_x=0.25)
            type_btn.add_widget(MDButtonText(text=advance_type))
            type_btn.bind(on_release=lambda btn, idx=index: self._open_advance_type_menu(btn, idx))
            inner.add_widget(type_btn)

            # Namen-Feld
            name_field = MDTextField(
                MDTextFieldHintText(text="Name (z.B. Stärke / Kämpfen / Heiler)"),
                mode="outlined",
                text=advance_name,
                size_hint_x=0.55,
            )
            name_field.bind(text=lambda instance, value, idx=index: self._update_advance_name(idx, value))
            inner.add_widget(name_field)

            # Löschen-Button
            del_btn = MDButton(style="text", size_hint_x=0.2)
            del_btn.add_widget(MDButtonIcon(icon="delete"))
            del_btn.bind(on_release=lambda btn, idx=index: self._remove_advance_entry(idx))
            inner.add_widget(del_btn)

            row.add_widget(inner)
            self._advances_container.add_widget(row)

    def _open_advance_type_menu(self, caller_btn, index):
        types = ["attribute", "skill", "edge", "power"]
        menu_items = []
        for t in types:
            menu_items.append({
                "text": t,
                "on_release": (lambda t=t, idx=index, b=caller_btn: self._set_advance_type(idx, t, b)),
            })
        menu = MDDropdownMenu(caller=caller_btn, items=menu_items)
        caller_btn._temp_menu = menu
        menu.open()

    def _set_advance_type(self, index, new_type, btn):
        advances = self.template_data.get("advances_to_apply", [])
        if 0 <= index < len(advances):
            advances[index]['type'] = new_type
            if btn.children:
                btn.children[0].text = new_type
        menu = getattr(btn, '_temp_menu', None)
        if menu:
            menu.dismiss()

    def _update_advance_name(self, index, value):
        advances = self.template_data.setdefault("advances_to_apply", [])
        if 0 <= index < len(advances):
            advances[index]['name'] = value

    def _add_advance_entry(self, *_args):
        if not self._nav_debounce_check():
            return
        self.template_data.setdefault("advances_to_apply", []).append({
            "type": "attribute",
            "name": "",
        })
        # Einen Aufstieg mehr → auch starting_advances erhöhen (Komfort)
        current = int(self.template_data.get("starting_advances", 0))
        self.template_data["starting_advances"] = current + 1
        if hasattr(self, 'starting_advances_field'):
            self.starting_advances_field.text = str(self.template_data["starting_advances"])
        self._render_advances_list()

    def _remove_advance_entry(self, index):
        if not self._nav_debounce_check():
            return
        advances = self.template_data.get("advances_to_apply", [])
        if 0 <= index < len(advances):
            advances.pop(index)
            # starting_advances bleibt — Benutzer kann sie manuell anpassen.
            self._render_advances_list()

    def _create_preview_step(self):
        """Erstellt Schritt 9: Vorschau & Speichern"""
        layout = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            size_hint_y=None,
            height=self._get_content_height(extended=True)
        )
        
        # Template-Vorschau
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
        
        # Zusammenfassung
        summary = self._generate_template_summary()
        preview_label = MDLabel(
            text=summary,
            theme_text_color="Primary",
            markup=True
        )
        
        preview_scroll = MDScrollView()
        preview_scroll.add_widget(preview_label)
        preview_content.add_widget(preview_scroll)
        
        preview_card.add_widget(preview_content)
        content.add_widget(preview_card)
        
        # Dateiname
        self.filename_field = MDTextField(
            MDTextFieldHintText(text="Template-Dateiname"),
            mode="outlined",
            text=self._generate_filename()
        )
        self.filename_field.bind(text=self._update_filename)
        content.add_widget(self.filename_field)
        
        layout.add_widget(content)
        return layout
    
    # Event Handler
    def _update_name(self, instance, value):
        self.template_data["name"] = value

    def _update_description(self, instance, value):
        self.template_data["description"] = value
    
    def _update_concept(self, instance, value):
        if "profile" not in self.template_data:
            self.template_data["profile"] = {}
        self.template_data["profile"]["concept"] = value
    
    def _update_gender(self, instance, value):
        if "profile" not in self.template_data:
            self.template_data["profile"] = {}
        self.template_data["profile"]["gender"] = value
    
    def _update_attribute(self, attr, value):
        try:
            val = int(value) if value else 4
            val = max(4, min(12, val))  # Clamp zwischen 4-12
            self.template_data["attributes"][attr] = val
            self._update_attribute_points()
        except ValueError:
            pass
    
    def _update_attribute_points(self):
        """Aktualisiert Attributspunkte-Anzeige"""
        if hasattr(self, 'points_info'):
            total_cost = sum(max(0, val - 4) for val in self.template_data["attributes"].values())
            available = self.template_data.get("starting_attribute_points", 5)
            remaining = available - total_cost
            self.points_info.text = f"Verbraucht: {total_cost} / {available} (Übrig: {remaining})"
    
    def _checkbox_debounce_check(self, key: str) -> bool:
        """Prüft ob ein Checkbox-Event zu schnell hintereinander kommt (Android Touch-Bounce)."""
        now = time.monotonic()
        if not hasattr(self, '_last_checkbox_times'):
            self._last_checkbox_times = {}
        if key in self._last_checkbox_times and (now - self._last_checkbox_times[key]) < 0.5:
            return False
        self._last_checkbox_times[key] = now
        return True

    def _toggle_skill(self, skill, active):
        if not self._checkbox_debounce_check(f"skill_{skill}"):
            return
        if active:
            self.template_data["skills"][skill] = 4
            self.skill_fields[skill][1].disabled = False
        else:
            if skill in self.template_data["skills"]:
                del self.template_data["skills"][skill]
            self.skill_fields[skill][1].disabled = True
    
    def _update_skill(self, skill, value):
        try:
            val = int(value) if value else 4
            val = max(2, min(12, val))
            if skill in self.template_data["skills"]:
                self.template_data["skills"][skill] = val
        except ValueError:
            pass
    
    def _toggle_handicap(self, key, active):
        if not self._checkbox_debounce_check(f"handicap_{key}"):
            return
        if active:
            # Prüfe ob Handicap bereits ausgewählt
            if any(sel.get("key") == key for sel in self.template_data["handicaps"]):
                return

            # Hole Handicap-Daten
            h = self._available_handicaps.get(key, {})
            punkte = h.get("punkte", 1)

            # Prüfe 4-Punkte-Maximum
            current_points = self._get_handicap_points()
            if current_points + punkte > 4:
                # Checkbox wieder deaktivieren
                if key in self.handicap_checkboxes:
                    self.handicap_checkboxes[key].active = False
                self._update_handicap_points()
                return

            self.template_data["handicaps"].append({
                "name": h.get("name", key),
                "stufe": h.get("stufe", "leicht"),
                "key": key
            })
        else:
            self.template_data["handicaps"] = [
                sel for sel in self.template_data["handicaps"]
                if sel.get("key") != key
            ]
        self._update_handicap_points()

    def _get_handicap_points(self):
        """Berechnet aktuelle Handicap-Punkte aus template_data"""
        total = 0
        for h in self.template_data.get("handicaps", []):
            if isinstance(h, dict):
                stufe = h.get("stufe", "leicht")
                total += 2 if stufe == "schwer" else 1
            else:
                total += 1  # Legacy: String-Einträge als 1 Punkt
        return total

    def _update_handicap_points(self):
        """Aktualisiert die Punkte-Anzeige im UI"""
        if hasattr(self, 'handicap_points_label'):
            points = self._get_handicap_points()
            self.handicap_points_label.text = f"Handicap-Punkte: {points} / 4"

    def _show_handicap_description(self, name, beschreibung):
        """Zeigt einen Dialog mit der Handicap-Beschreibung"""
        desc_dialog = MDDialog(
            MDDialogHeadlineText(text=name),
            MDDialogContentContainer(
                MDBoxLayout(
                    MDLabel(
                        text=beschreibung,
                        adaptive_height=True
                    ),
                    orientation="vertical",
                    size_hint_y=None,
                    height="150dp",
                    padding="12dp"
                )
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Schließen"),
                    style="text",
                    on_release=lambda *args: desc_dialog.dismiss()
                )
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        desc_dialog.open()

    def _toggle_edge(self, edge, active):
        if not self._checkbox_debounce_check(f"edge_{edge}"):
            return
        if active:
            if edge not in self.template_data["edges"]:
                self.template_data["edges"].append(edge)
        else:
            if edge in self.template_data["edges"]:
                self.template_data["edges"].remove(edge)
    
    def _toggle_power(self, power, active):
        if not self._checkbox_debounce_check(f"power_{power}"):
            return
        if active:
            if power not in self.template_data["powers"]:
                self.template_data["powers"].append(power)
        else:
            if power in self.template_data["powers"]:
                self.template_data["powers"].remove(power)
    
    def _update_power_points(self, instance, value):
        try:
            self.template_data["power_points"] = int(value) if value else 0
        except ValueError:
            pass
    
    def _update_capital(self, instance, value):
        try:
            self.template_data["starting_capital"] = int(value) if value else 500
        except ValueError:
            pass
    
    def _update_equipment(self, instance, value):
        # Teile bei Newlines und filtere leere Zeilen
        equipment_list = [item.strip() for item in value.split("\n") if item.strip()]
        self.template_data["equipment"] = equipment_list
    
    def _update_filename(self, instance, value):
        self.template_filename = value
    
    # Navigation
    def _save_current_step_data(self):
        """Sichert Daten des aktuellen Schritts aus den UI-Widgets"""
        if self.current_step == 0:
            # Allgemeine Daten
            if hasattr(self, 'name_field') and self.name_field:
                self.template_data["name"] = self.name_field.text or ""
            if hasattr(self, 'description_field') and self.description_field:
                self.template_data["description"] = self.description_field.text or ""
            if hasattr(self, 'concept_field') and self.concept_field:
                self.template_data.setdefault("profile", {})["concept"] = self.concept_field.text or ""
            if hasattr(self, 'gender_field') and self.gender_field:
                self.template_data.setdefault("profile", {})["gender"] = self.gender_field.text or ""
        elif self.current_step == 1:
            # Attribute
            if hasattr(self, 'attribute_fields'):
                for attr, field in self.attribute_fields.items():
                    try:
                        val = int(field.text) if field.text else 4
                        self.template_data["attributes"][attr] = max(4, min(12, val))
                    except ValueError:
                        pass

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
        self._save_current_step_data()
        self.current_step += 1
        self._show_current_step()

    def _previous_step(self, *args):
        if not self._nav_debounce_check():
            return
        self._save_current_step_data()
        self.current_step -= 1
        self._show_current_step()

    def _cancel_wizard(self, *args):
        """Bricht den Wizard ab"""
        if not self._nav_debounce_check():
            return
        if self.dialog:
            self.dialog.dismiss()
        Logger.info("Template-Wizard abgebrochen")

    def _finish_wizard(self, *args):
        """Schließt den Wizard ab und speichert das Template"""
        if not self._nav_debounce_check():
            return
        try:
            # Aktuelle Schritt-Daten sichern
            self._save_current_step_data()

            # Validierung durchführen
            validation_errors = self._validate_template_data()
            if validation_errors:
                error_message = "Bitte korrigieren Sie folgende Fehler:\n\n" + "\n".join(validation_errors)
                self._show_error_dialog(error_message)
                return
            
            filename = getattr(self, 'template_filename', self._generate_filename())
            if not filename.endswith('.json'):
                filename += '.json'
            
            template_path = get_application_root() / 'templates' / filename
            
            # Template speichern
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(self.template_data, f, indent=2, ensure_ascii=False)
            
            Logger.info(f"Template erfolgreich gespeichert: {template_path}")
            
            # Dialog schließen
            if self.dialog:
                self.dialog.dismiss()
            
            # Callback aufrufen
            if self.callback:
                self.callback(template_path, self.template_data)
            
            # Erfolgs-Dialog
            self._show_success_dialog(filename)
            
        except Exception as e:
            Logger.error(f"Fehler beim Speichern des Templates: {e}")
            self._show_error_dialog(str(e))
    
    def _validate_template_data(self):
        """Validiert die Template-Daten - nur Pflichtfelder prüfen"""
        errors = []

        # Nur Name ist wirklich erforderlich
        if not self.template_data.get("name", "").strip():
            errors.append("• Template-Name ist erforderlich")

        return errors
    
    # Hilfsmethoden
    def _get_content_height(self, extended=False):
        """Berechnet die Höhe für Scroll-Content"""
        base_height = "800dp" if extended else "500dp"
        return base_height
    
    def _generate_filename(self):
        """Generiert einen Dateinamen basierend auf Charaktername"""
        name = self.template_data.get("name", "template")
        # Bereinige Name für Dateiname
        clean_name = "".join(c.lower() if c.isalnum() else "_" for c in name)
        return clean_name or "template"
    
    def _generate_template_summary(self):
        """Generiert eine Vorschau-Zusammenfassung"""
        data = self.template_data
        
        summary = f"[b]{data.get('name', 'Unbenannt')}[/b]\\n"
        summary += f"[i]{data.get('description', 'Keine Beschreibung')}[/i]\\n\\n"
        
        summary += f"[b]Setting:[/b] {data.get('setting', 'SWAE')}\\n"
        summary += f"[b]Volk:[/b] {data.get('race', 'Mensch')}\\n"
        
        profile = data.get('profile', {})
        if profile.get('concept'):
            summary += f"[b]Konzept:[/b] {profile['concept']}\\n"
        if profile.get('gender'):
            summary += f"[b]Geschlecht:[/b] {profile['gender']}\\n"
        
        # Attribute
        summary += "\\n[b]Attribute:[/b]\\n"
        for attr, value in data.get('attributes', {}).items():
            summary += f"  • {attr}: W{value}\\n"
        
        # Fertigkeiten
        skills = data.get('skills', {})
        if skills:
            summary += "\\n[b]Fertigkeiten:[/b]\\n"
            for skill, value in skills.items():
                summary += f"  • {skill}: W{value}\\n"
        
        # Handicaps
        handicaps = data.get('handicaps', [])
        if handicaps:
            total_points = self._get_handicap_points()
            summary += f"\\n[b]Handicaps ({total_points} Pkt):[/b]\\n"
            for handicap in handicaps:
                if isinstance(handicap, dict):
                    stufe = handicap.get('stufe', 'leicht')
                    punkte = 2 if stufe == 'schwer' else 1
                    summary += f"  • {handicap['name']} ({stufe}) - {punkte} Pkt\\n"
                else:
                    summary += f"  • {handicap}\\n"
        
        # Talente
        edges = data.get('edges', [])
        if edges:
            summary += f"\\n[b]Talente ({len(edges)}):[/b]\\n"
            for edge in edges:
                summary += f"  • {edge}\\n"
        
        # Mächte
        powers = data.get('powers', [])
        if powers:
            summary += f"\\n[b]Mächte ({len(powers)}):[/b]\\n"
            for power in powers:
                summary += f"  • {power}\\n"
            summary += f"[b]Machtpunkte:[/b] {data.get('power_points', 0)}\\n"
        
        # Ausrüstung
        equipment = data.get('equipment', [])
        if equipment:
            summary += f"\\n[b]Ausrüstung ({len(equipment)}):[/b]\\n"
            for item in equipment[:5]:  # Nur erste 5 anzeigen
                summary += f"  • {item}\\n"
            if len(equipment) > 5:
                summary += f"  ... und {len(equipment) - 5} weitere\\n"
        
        summary += f"\\n[b]Startkapital:[/b] {data.get('starting_capital', 500)}"

        # Volks-Wahlmöglichkeiten
        race_choices = data.get('race_choices', {}) or {}
        if race_choices:
            summary += "\\n\\n[b]Volks-Wahl:[/b]\\n"
            for k, v in race_choices.items():
                summary += f"  • {k}: {v}\\n"

        # Aufstiege
        advances = data.get('advances_to_apply', []) or []
        starting_advances = data.get('starting_advances', 0)
        if starting_advances or advances:
            summary += f"\\n[b]Aufstiege:[/b] {starting_advances} geplant\\n"
            for idx, advance in enumerate(advances, 1):
                summary += f"  • #{idx} {advance.get('type', '?')}: {advance.get('name', '?')}\\n"

        # Abgeleitete Werte (Vorschau)
        derived = self._estimate_derived_values()
        if derived:
            summary += "\\n[b]Abgeleitete Werte (Vorschau):[/b]\\n"
            for label, value in derived.items():
                summary += f"  • {label}: {value}\\n"

        return summary

    def _estimate_derived_values(self):
        """
        Heuristische Vorschau auf Parade, Robustheit, Bewegungsweite, Machtpunkte
        direkt aus den Template-Daten — OHNE einen echten Charakter anzulegen.
        Das ersetzt keine echte Berechnung (die erfolgt beim Generieren), gibt dem
        Benutzer aber eine sinnvolle Abschätzung.
        """
        try:
            attrs = self.template_data.get('attributes', {}) or {}
            skills = self.template_data.get('skills', {}) or {}

            konstitution = int(attrs.get('Konstitution', 4))
            kaempfen = int(skills.get('Kämpfen', 0))
            # Savage Worlds Formeln
            parade = 2 + (kaempfen // 2) if kaempfen else 2
            robustheit = 2 + (konstitution // 2)
            bewegung = 6  # SWAE-Basis, Rassen-Boni nicht berücksichtigt (Vorschau)

            machtpunkte = self.template_data.get('power_points', 0) or 0

            return {
                "Parade (ohne Schild)": parade,
                "Robustheit (ohne Rüstung)": robustheit,
                "Bewegungsweite (Basis)": bewegung,
                "Machtpunkte": machtpunkte,
            }
        except Exception:
            return {}
    
    def _show_success_dialog(self, filename):
        """Zeigt Erfolgs-Dialog"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.show_success_dialog(
                f"Template '{filename}' erstellt."
            )
    
    def _show_error_dialog(self, error_message):
        """Zeigt Fehler-Dialog"""
        dialog_service = service_container.get_dialog_service()
        if dialog_service:
            dialog_service.show_error_dialog(f"Fehler beim Erstellen des Templates:\\n{error_message}")
    
    # Data Provider Methoden
    def _get_available_skills(self):
        """Holt verfügbare Fertigkeiten aus dem aktuellen Setting"""
        try:
            if hasattr(self.app, 'controller') and self.app.controller:
                return list(self.app.controller.charakter.fertigkeiten.keys())
            return ["Athletik", "Kämpfen", "Wahrnehmung", "Heimlichkeit", "Überreden"]  # Fallback
        except:
            return ["Athletik", "Kämpfen", "Wahrnehmung", "Heimlichkeit", "Überreden"]
    
    def _get_available_handicaps(self):
        """Holt verfügbare Handicaps aus dem aktuellen Setting als strukturierte Dicts"""
        try:
            if hasattr(self.app, 'controller') and self.app.controller:
                charakter = self.app.controller.charakter
                handicaps = charakter.handicaps
                if not handicaps:
                    return self._get_fallback_handicaps()
                result = {}
                for key, h in handicaps.items():
                    result[key] = {
                        "key": key,
                        "name": h.name,
                        "stufe": h.stufe,
                        "punkte": h.punkte,
                        "beschreibung": h.beschreibung
                    }
                return result
            return self._get_fallback_handicaps()
        except Exception as e:
            Logger.error(f"Template-Wizard: Fehler beim Laden der Handicaps: {e}")
            return self._get_fallback_handicaps()

    def _get_fallback_handicaps(self):
        """Fallback-Handicaps wenn kein Setting geladen"""
        return {
            "Arrogant (leicht)": {"key": "Arrogant (leicht)", "name": "Arrogant", "stufe": "leicht", "punkte": 1, "beschreibung": "Der Charakter glaubt, er sei besser als andere."},
            "Arrogant (schwer)": {"key": "Arrogant (schwer)", "name": "Arrogant", "stufe": "schwer", "punkte": 2, "beschreibung": "Der Charakter glaubt, er sei besser als andere."},
            "Außenseiter (leicht)": {"key": "Außenseiter (leicht)", "name": "Außenseiter", "stufe": "leicht", "punkte": 1, "beschreibung": "Der Charakter gehört nicht dazu."},
            "Große Klappe (leicht)": {"key": "Große Klappe (leicht)", "name": "Große Klappe", "stufe": "leicht", "punkte": 1, "beschreibung": "Der Charakter redet zu viel."}
        }
    
    def _get_available_edges(self):
        """Holt verfügbare Talente aus dem aktuellen Setting"""
        try:
            if hasattr(self.app, 'controller') and self.app.controller:
                edges = self.app.controller.charakter.talente
                return [e.name for e in edges.values()]
            return ["AH", "Kämpfer", "Gelehrter"]  # Fallback
        except:
            return ["AH", "Kämpfer", "Gelehrter"]
    
    def _get_available_powers(self):
        """Holt verfügbare Mächte aus dem aktuellen Setting"""
        try:
            if hasattr(self.app, 'controller') and self.app.controller:
                powers = self.app.controller.charakter.maechte
                return [p.name for p in powers.values()]
            return ["Feuerball", "Heilung", "Rüstung"]  # Fallback
        except:
            return ["Feuerball", "Heilung", "Rüstung"]
    
    def _create_setting_dropdown(self):
        """Erstellt Setting-Dropdown Menü"""
        settings = ["SWAE", "Fantasy Kompendium", "Deadlands", "HeXXen1773", "Savage Pathfinder"]
        menu_items = []
        for setting in settings:
            menu_items.append({
                "text": setting,
                "on_release": lambda x=setting: self._select_setting(x)
            })
        
        self.setting_menu = MDDropdownMenu(
            caller=None,  # Wird später gesetzt
            items=menu_items
        )
    
    def _create_race_dropdown(self):
        """Erstellt Volk-Dropdown Menü"""
        try:
            if hasattr(self.app, 'controller') and self.app.controller:
                races = list(self.app.controller.charakter.setting.voelker.keys())
            else:
                races = ["Mensch"]  # Fallback
        except:
            races = ["Mensch"]
        
        menu_items = []
        for race in races:
            menu_items.append({
                "text": race,
                "on_release": lambda x=race: self._select_race(x)
            })
        
        self.race_menu = MDDropdownMenu(
            caller=None,  # Wird später gesetzt
            items=menu_items
        )
    
    def _open_setting_menu(self, button):
        self.setting_menu.caller = button
        self.setting_menu.open()
    
    def _open_race_menu(self, button):
        self.race_menu.caller = button
        self.race_menu.open()
    
    def _select_setting(self, setting):
        self.template_data["setting"] = setting
        if hasattr(self, 'setting_button'):
            self.setting_button.children[0].text = setting
        self.setting_menu.dismiss()
    
    def _select_race(self, race):
        self.template_data["race"] = race
        if hasattr(self, 'race_button'):
            self.race_button.children[0].text = race
        self.race_menu.dismiss()

        # Alte Auswahl zurücksetzen (neues Volk = neue Wahlmöglichkeiten)
        self.template_data["race_choices"] = {}

        # Wahlmöglichkeiten des Volks prüfen und ggf. Popup öffnen.
        wahl = self._get_volk_wahlmoeglichkeiten(race)
        if wahl:
            # Kurze Verzögerung, damit das Dropdown-Menü sauber schließt.
            Clock.schedule_once(lambda dt: self._show_race_choices_popup(race, wahl), 0.2)

    # ------------------------------------------------------------------
    # Volks-Wahlmöglichkeiten
    # ------------------------------------------------------------------
    def _get_volk(self, race_name):
        """Holt das Volk-Objekt aus dem aktiven Setting. None bei Fehlschlag."""
        try:
            if hasattr(self.app, 'controller') and self.app.controller:
                voelker = self.app.controller.charakter.setting.voelker
                return voelker.get(race_name)
        except Exception:
            return None
        return None

    def _get_volk_wahlmoeglichkeiten(self, race_name):
        """
        Liefert das wahlmoeglichkeiten-Dict eines Volks (oder leeres Dict).
        Interessante Keys (werden im Popup behandelt):
        - freies_talent, freies_anfaengertalent, freies_anfaenger_talent
        - freies_attribut
        - freies_talent_oder_attribut (Halbelf)
        - attribut_staerke_oder_konstitution (Halbork)
        - freie_verstandsfertigkeit (Engro)
        """
        volk = self._get_volk(race_name)
        if volk is None:
            return {}
        effects = getattr(volk, 'effects', {}) or {}
        return effects.get('wahlmoeglichkeiten', {}) or {}

    def _get_volk_freie_talente(self, race_name):
        """Liste zulässiger Anfänger-Talent-Namen (Fallback: alle Talente)."""
        try:
            if hasattr(self.app, 'controller') and self.app.controller:
                charakter = self.app.controller.charakter
                from functions.volk_funktionen import get_freie_talente
                return get_freie_talente(charakter, nur_verfuegbare=False) or []
        except Exception:
            pass
        return []

    def _show_race_choices_popup(self, race_name, wahl):
        """
        Zeigt ein eigenständiges Popup mit Dropdowns für die relevanten
        Wahlmöglichkeiten des Volks. Die Ergebnisse landen in
        ``template_data['race_choices']``.
        """
        choices = {}  # temporäre Auswahl während der Popup-Sitzung
        # Layout
        content = MDBoxLayout(
            orientation="vertical",
            spacing="8dp",
            size_hint_y=None,
            padding="12dp",
        )
        content.bind(minimum_height=content.setter('height'))

        intro = MDLabel(
            text=f"{race_name} bietet folgende Wahlmöglichkeiten:",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="32dp",
        )
        content.add_widget(intro)

        attribute = ["Stärke", "Geschicklichkeit", "Konstitution", "Verstand", "Willenskraft"]
        talente = self._get_volk_freie_talente(race_name)

        def _add_dropdown(label_text, options, key, default=None):
            """Fügt eine Zeile mit Label + Dropdown-Button hinzu."""
            row = MDBoxLayout(orientation="horizontal", spacing="8dp",
                              size_hint_y=None, height="56dp")
            row.add_widget(MDLabel(text=label_text, size_hint_x=0.5))
            btn = MDButton(style="outlined")
            btn.add_widget(MDButtonText(text=default or "Bitte wählen"))
            if default:
                choices[key] = default

            def _open_menu(instance, opts=options, k=key, b=btn):
                menu_items = []
                for opt in opts:
                    menu_items.append({
                        "text": opt,
                        "on_release": (lambda opt=opt, k=k, b=b: self._race_choice_selected(k, opt, b, choices)),
                    })
                menu = MDDropdownMenu(caller=instance, items=menu_items)
                # Speichere Menü am Button, damit es geschlossen werden kann.
                b._temp_menu = menu
                menu.open()

            btn.bind(on_release=_open_menu)
            row.add_widget(btn)
            content.add_widget(row)

        # Halbork: attribut_staerke_oder_konstitution
        if wahl.get('attribut_staerke_oder_konstitution'):
            _add_dropdown("Bonus-Attribut (Stä/Kon):",
                          ["Stärke", "Konstitution"],
                          "attribut_staerke_oder_konstitution")

        # Halbelf: freies_talent_oder_attribut (2-stufig: Modus + Wert)
        if wahl.get('freies_talent_oder_attribut'):
            _add_dropdown("Wahl zwischen Talent oder Attribut:",
                          ["talent", "attribut"],
                          "freies_talent_oder_attribut_modus")
            # Für Wert zeigen wir beide Optionen (Attribut + Talent-Liste)
            optionen = attribute + list(talente)
            _add_dropdown("Gewählter Wert (Attribut ODER Talent):",
                          optionen,
                          "freies_talent_oder_attribut_wert")

        # Mensch / andere: freies_talent
        if (wahl.get('freies_talent') or wahl.get('freies_anfaengertalent')
                or wahl.get('freies_anfaenger_talent')) and not wahl.get('freies_talent_oder_attribut'):
            if talente:
                _add_dropdown("Freies Anfänger-Talent:",
                              list(talente),
                              "freies_talent")
            else:
                content.add_widget(MDLabel(
                    text="Kein Talent-Katalog verfügbar – bitte im Historie-Log prüfen.",
                    theme_text_color="Error", size_hint_y=None, height="30dp",
                ))

        # freies_attribut
        if wahl.get('freies_attribut') and not wahl.get('freies_talent_oder_attribut'):
            _add_dropdown("Freies Attribut (+1 Würfeltyp):",
                          attribute,
                          "freies_attribut")

        # freie_verstandsfertigkeit (Engro)
        if wahl.get('freie_verstandsfertigkeit'):
            # Verstandsfertigkeiten-Auswahl: wir reichen alle bekannten Skills durch
            skills = self._get_available_skills() or []
            if skills:
                _add_dropdown("Freie Verstandsfertigkeit:",
                              list(skills),
                              "freie_verstandsfertigkeit")

        # Nichts Relevantes? Dann Popup gar nicht erst zeigen.
        if len(content.children) <= 1:  # nur intro-Label
            return

        scroll = TextFieldScrollView(size_hint_y=1)
        scroll.add_widget(content)

        popup_layout = MDBoxLayout(orientation="vertical", size_hint_y=None, height="400dp")
        popup_layout.add_widget(scroll)

        self._race_choices_popup = MDDialog(
            MDDialogHeadlineText(text=f"{race_name}: Volks-Wahlmöglichkeiten"),
            MDDialogContentContainer(popup_layout),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Abbrechen"), style="text",
                         on_release=lambda x: self._race_choices_popup.dismiss()),
                MDButton(MDButtonText(text="Übernehmen"), style="filled",
                         on_release=lambda x: self._confirm_race_choices(choices)),
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self._race_choices_popup.open()

    def _race_choice_selected(self, key, value, button, choices):
        """Callback wenn im Volks-Wahlmöglichkeiten-Popup ein Dropdown-Eintrag gewählt wurde."""
        choices[key] = value
        try:
            # Button-Text aktualisieren (kind[0] ist MDButtonText)
            if button.children:
                button.children[0].text = str(value)
        except Exception:
            pass
        menu = getattr(button, '_temp_menu', None)
        if menu:
            menu.dismiss()

    def _confirm_race_choices(self, choices):
        """Übernimmt die Wahl in template_data und schließt das Popup."""
        self.template_data["race_choices"] = dict(choices)
        # Legacy-Feld ``free_race_edge`` pflegen, damit alte Auto-Generator-Pfade
        # weiterhin funktionieren (wird im Auto-Generator bevorzugt aus race_choices gelesen).
        if 'freies_talent' in choices:
            self.template_data["free_race_edge"] = choices['freies_talent']
        if self._race_choices_popup:
            self._race_choices_popup.dismiss()
            self._race_choices_popup = None


def show_template_wizard(callback=None):
    """Zeigt den Template-Wizard"""
    wizard = TemplateWizardDialog(callback=callback)
    wizard.start_wizard()