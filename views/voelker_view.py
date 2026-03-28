# views/voelker_view.py - UI-Komponente mit MDDropdownMenu
"""
View-Komponente für Völker nach dem MVC-Pattern.
ÜBERARBEITET: UI-Darstellung getrennt von Geschäftslogik (volk_funktionen.py)
KORRIGIERT: KivyMD 2.0.1 Kompatibilität (adaptive_height entfernt)
NEU: MDDropdownMenu für platzsparende Völker-Auswahl
"""

from kivy.lang import Builder
from kivy.app import App
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import ObjectProperty, DictProperty
from kivy.metrics import dp
import logging

# Import der ausgelagerten Geschäftslogik
from functions.volk_funktionen import (
    waehle_volk, abwaehlen_volk, get_selected_volk,
    hat_volk_wahlmoeglichkeit, get_volk_zusatzelemente, get_volk_attribut_optionen,
    get_freie_talente, get_verfuegbare_attribute, get_verfuegbare_fertigkeiten,
    waehle_freies_talent, waehle_freies_attribut, waehle_freie_fertigkeit,
    reset_volk_auswahlen, initialisiere_voelker_system, get_voelker_status_info,
    waehle_halbelf_talent, waehle_halbelf_attribut,  # NEUE: Halbelf-spezifische Funktionen
    waehle_mensch_talent, waehle_mensch_fertigkeitspunkte,  # NEUE: Menschen-Vielseitig-Funktionen
    DEFAULT_TALENT_TEXT, DEFAULT_ATTRIBUT_TEXT, DEFAULT_FERTIGKEIT_TEXT,
    NO_TALENT_AVAILABLE_TEXT, NO_ATTRIBUT_AVAILABLE_TEXT, NO_FERTIGKEIT_AVAILABLE_TEXT
)

# Logger konfigurieren
Logger = logging.getLogger(__name__)

# KV-Datei laden mit PyInstaller-kompatiblem Pfad und Mobile-Unterstützung
from utils.path_utils import get_application_root
from utils.platform_utils import is_mobile_layout
import os

_base_path = str(get_application_root())
_mobile = is_mobile_layout()
_kv_name = 'voelker_view_mobile.kv' if _mobile else 'voelker_view.kv'
_kv_path = os.path.join(_base_path, 'views', _kv_name)
if not os.path.exists(_kv_path):
    _kv_path = os.path.join(_base_path, 'views', 'voelker_view.kv')
Builder.load_file(_kv_path)
Logger.info(f"voelker_view: KV-Datei geladen: {os.path.basename(_kv_path)}")


class VoelkerWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Völkern.
    ÜBERARBEITET: Reine UI-Komponente, Geschäftslogik in volk_funktionen.py
    NEU: Verwendet MDDropdownMenu für platzsparende Völker-Auswahl
    """
    controller = ObjectProperty(None)
    voelker_auswahlen = DictProperty({})
    selected_volk_name = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.voelker_auswahlen = {}
        self.selected_volk_name = None
        self.volk_dropdown_menu = None  # Für das Dropdown-Menü
        self.search_dialog = None  # Für Such-Dialoge
        
        # Controller aus der App initialisieren
        Clock.schedule_once(self._initialize_controller, 0)
        Clock.schedule_once(self.aktualisiere_ui, 0.1)

    def set_controller(self, controller):
        """Setzt den Controller für das Widget."""
        self.controller = controller
        if controller and hasattr(controller, 'charakter'):
            controller.charakter.bind(on_charakter_change=self.aktualisiere_ui)
            self.aktualisiere_ui()

    def _defocus_and_call(self, callback):
        """Defokussiert alle TextFields und ruft callback verzögert auf.
        Behebt Android-Problem: TextField-Fokus schluckt Button-Touch-Events."""
        Window.release_all_keyboards()
        Clock.schedule_once(lambda dt: callback(), 0.1)

    def _initialize_controller(self, dt=None):
        """Initialisiert die Verbindung zum Controller aus der App."""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller'):
                self.set_controller(app.controller)
            else:
                Logger.warning("VoelkerWidget: App-Controller noch nicht verfügbar")
                Clock.schedule_once(self._initialize_controller, 1.0)
        except Exception as e:
            Logger.error(f"Fehler bei Controller-Initialisierung: {e}")

    def open_volk_dropdown(self):
        """Öffnet den Völker-Auswahl-Dialog.
        Verwendet show_choice_dialog wie beim Setting-Wechsel."""
        try:
            if not self.controller or not hasattr(self.controller, 'charakter'):
                Logger.warning("Controller nicht verfügbar")
                return

            charakter = self.controller.charakter

            if not hasattr(charakter, 'voelker') or not charakter.voelker:
                Logger.warning("Keine Völker verfügbar")
                return

            self._show_volk_choice_dialog()

        except Exception as e:
            Logger.error(f"Fehler beim Öffnen des Völker-Dialogs: {e}", exc_info=True)

    def _show_volk_choice_dialog(self):
        """Zeigt einen Auswahl-Dialog für Völker, analog zum Setting-Wechsel-Dialog.
        Verwendet dialog_service.show_choice_dialog() für zuverlässiges Scrolling."""
        try:
            from services.service_container import service_container

            charakter = self.controller.charakter
            voelker_namen = sorted(charakter.voelker.keys())

            # Auswahloptionen aufbauen: "Kein Volk" + alle Völker
            choices = [("Kein Volk", None)]
            for name in voelker_namen:
                choices.append((name, name))

            current_volk = self.selected_volk_name or "Keins"
            message = f"Aktuelles Volk: {current_volk}\n\nWähle ein Volk:"

            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_choice_dialog(
                    message,
                    "Volk auswählen",
                    choices,
                    self._on_volk_choice_made
                )
            Logger.debug(f"Völker-Dialog geöffnet mit {len(voelker_namen)} Völkern")

        except Exception as e:
            Logger.error(f"Fehler bei Völker-Dialog: {e}", exc_info=True)

    def _on_volk_choice_made(self, chosen_volk):
        """Verarbeitet die Völker-Auswahl aus dem Dialog."""
        if chosen_volk != self.selected_volk_name:
            self._select_volk_from_dropdown(chosen_volk)

    def _on_volk_popup_selected(self, volk_name):
        """Behandelt die Auswahl eines Volkes im Popup-Dialog."""
        try:
            if hasattr(self, 'volk_search_dialog') and self.volk_search_dialog:
                self.volk_search_dialog.dismiss()
                self.volk_search_dialog = None
            self._select_volk_from_dropdown(volk_name)
        except Exception as e:
            Logger.error(f"Fehler bei Völker-Popup-Auswahl: {e}", exc_info=True)

    def _select_volk_from_dropdown(self, volk_name):
        """Behandelt die Völker-Auswahl aus dem Popup/Dropdown."""
        try:
            
            charakter = self.controller.charakter
            
            # Aktuell ausgewähltes Volk ermitteln
            current_volk = None
            for name, selected in charakter.voelker_selected.items():
                if selected:
                    current_volk = name
                    break
            
            # Wenn "Kein Volk" ausgewählt
            if volk_name is None:
                if current_volk:
                    # Aktuelles Volk abwählen
                    success = abwaehlen_volk(charakter, current_volk)
                    if success:
                        self.selected_volk_name = None
                        reset_volk_auswahlen(charakter, current_volk, self.voelker_auswahlen)
                        self._update_dropdown_text("Kein Volk ausgewählt")
                        Logger.info("Kein Volk ausgewählt")
                        
                        # UI aktualisieren
                        Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
                        Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)
                return
            
            # Neues Volk auswählen
            if current_volk == volk_name:
                Logger.info(f"Volk '{volk_name}' ist bereits ausgewählt")
                return
            
            # Altes Volk abwählen (falls vorhanden)
            if current_volk:
                abwaehlen_volk(charakter, current_volk)
                reset_volk_auswahlen(charakter, current_volk, self.voelker_auswahlen)
            
            # Neues Volk auswählen
            Logger.debug(f"VOELKER_VIEW: Using charakter {id(charakter)} to select volk {volk_name}")
            success = waehle_volk(charakter, volk_name)
            if success:
                self.selected_volk_name = volk_name
                self._update_dropdown_text(volk_name)
                Logger.info(f"Volk '{volk_name}' ausgewählt")
                
                # UI aktualisieren
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
                Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)
            else:
                Logger.error(f"Fehler beim Auswählen von Volk '{volk_name}'")
                
        except Exception as e:
            Logger.error(f"Fehler bei Völker-Auswahl aus Dropdown: {e}", exc_info=True)

    def _update_dropdown_text(self, text):
        """Aktualisiert den Text des Auswahl-Buttons."""
        try:
            if 'selected_volk_text' in self.ids:
                self.ids.selected_volk_text.text = text
        except Exception as e:
            Logger.error(f"Fehler beim Aktualisieren des Dropdown-Texts: {e}")

    # === MOBILE INLINE-LISTE METHODEN ===

    def _populate_voelker_liste(self):
        """Befüllt die Inline-Völker-Liste (nur Mobile)."""
        if not _mobile:
            return
        try:
            if 'voelker_liste_container' not in self.ids:
                return

            container = self.ids.voelker_liste_container
            container.clear_widgets()

            if not self.controller or not hasattr(self.controller, 'charakter'):
                return

            charakter = self.controller.charakter
            if not hasattr(charakter, 'voelker') or not charakter.voelker:
                return

            # Suchtext ermitteln
            search_text = ""
            if 'search_input' in self.ids and self.ids.search_input.text:
                search_text = self.ids.search_input.text.lower()

            # "Kein Volk" Option
            if not search_text or "kein" in search_text:
                is_selected = self.selected_volk_name is None
                item = self._create_volk_list_item("Kein Volk", is_selected, volk_name=None)
                container.add_widget(item)

            # Alle Völker alphabetisch sortiert
            for volk_name in sorted(charakter.voelker.keys()):
                if search_text and search_text not in volk_name.lower():
                    continue
                is_selected = (self.selected_volk_name == volk_name)
                item = self._create_volk_list_item(volk_name, is_selected, volk_name=volk_name)
                container.add_widget(item)

        except Exception as e:
            Logger.error(f"Fehler beim Befüllen der Völker-Liste: {e}", exc_info=True)

    def filter_voelker(self):
        """Filtert die Völker-Liste basierend auf dem Suchfeld (Mobile)."""
        self._populate_voelker_liste()

    def _create_volk_list_item(self, display_name, is_selected, volk_name=None):
        """Erstellt ein einzelnes Listenelement für die Völker-Inline-Liste.
        Nutzt MDListItem statt MDCard für zuverlässiges Scrolling auf Android."""
        from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon

        list_item = MDListItem(
            size_hint_y=None,
            height=dp(44),
            on_release=lambda x, vn=volk_name: self._select_volk_from_dropdown(vn),
            md_bg_color=self.theme_cls.primaryContainerColor if is_selected else self.theme_cls.surfaceContainerLowColor,
        )

        if is_selected:
            list_item.add_widget(MDListItemLeadingIcon(
                icon="check-circle",
                theme_icon_color="Custom",
                icon_color=self.theme_cls.primaryColor,
            ))

        headline = MDListItemHeadlineText(
            text=display_name,
        )
        if is_selected:
            headline.bold = True
        list_item.add_widget(headline)

        return list_item

    def aktualisiere_ui(self, dt=None):
        """Aktualisiert die gesamte UI basierend auf den aktuellen Charakter-Daten."""
        Logger.debug("VoelkerWidget: aktualisiere_ui aufgerufen")
        
        try:
            # Controller-Verfügbarkeit prüfen
            if not self.controller or not hasattr(self.controller, 'charakter'):
                Logger.warning("VoelkerWidget: Controller nicht verfügbar - Retry in 1s")
                Clock.schedule_once(self.aktualisiere_ui, 1.0)
                return
                
            # UI-Container prüfen
            if not hasattr(self, 'ids'):
                Logger.debug("VoelkerWidget: UI-Container noch nicht verfügbar")
                Clock.schedule_once(self.aktualisiere_ui, 0.5)
                return

            charakter = self.controller.charakter
            
            # Völker-Daten prüfen
            if not hasattr(charakter, 'voelker') or not charakter.voelker:
                self._show_no_data_message()
                return
            
            # Völker-System initialisieren und bereinigen
            initialisiere_voelker_system(charakter)
            
            # Debug-Informationen ausgeben
            status = get_voelker_status_info(charakter)
            Logger.debug(f"Völker-Status: {status}")

            # Aktuell ausgewähltes Volk ermitteln
            selected_volk = get_selected_volk(charakter)
            self.selected_volk_name = selected_volk.name if selected_volk else None

            # Auswahl-Button-Text aktualisieren
            if self.selected_volk_name:
                self._update_dropdown_text(self.selected_volk_name)
            else:
                self._update_dropdown_text("Kein Volk ausgewählt")

            # UI-Komponenten aktualisieren
            self._update_zusatzelemente()
            self._update_selected_volk_details()
                
            Logger.debug(f"VoelkerWidget: UI erfolgreich aktualisiert mit {len(charakter.voelker)} Völkern")

        except Exception as e:
            Logger.error(f"Fehler in aktualisiere_ui: {e}", exc_info=True)

    def _show_no_data_message(self):
        """Zeigt eine Nachricht an, wenn keine Völker-Daten verfügbar sind."""
        if _mobile:
            # Inline-Liste leeren
            if 'voelker_liste_container' in self.ids:
                self.ids.voelker_liste_container.clear_widgets()
        else:
            # Dropdown-Text aktualisieren
            self._update_dropdown_text("Keine Völker verfügbar")

        # Container leeren
        for container_id in ['zusatzelemente_container', 'selected_volk_container']:
            if container_id in self.ids:
                self.ids[container_id].clear_widgets()
        
        if 'selected_volk_container' in self.ids:
            placeholder = MDLabel(
                text="Keine Völker-Daten verfügbar",
                halign='center',
                theme_text_color="Secondary",
                font_style="Body",
                size_hint_y=None,
                height=dp(100)
            )
            self.ids.selected_volk_container.add_widget(placeholder)

    def _update_zusatzelemente(self):
        """ERWEITERT: Aktualisiert die Zusatzelemente-Bereiche inkl. neuer Völker-Wahlmöglichkeiten."""
        zusatzelemente_container = self.ids.zusatzelemente_container
        zusatzelemente_container.clear_widgets()
        
        if not self.selected_volk_name:
            return
            
        charakter = self.controller.charakter
        
        # Verfügbare Zusatzelemente von der Geschäftslogik abrufen
        zusatzelemente = get_volk_zusatzelemente(charakter, self.selected_volk_name)
        
        sections_added = 0
        
        # NEUE: Halbelf spezielle ENTWEDER/ODER Sektion
        if zusatzelemente.get('halbelf_entweder_oder', False):
            halbelf_section = self._create_halbelf_entweder_oder_section()
            zusatzelemente_container.add_widget(halbelf_section)
            sections_added += 1
            Logger.debug(f"Halbelf ENTWEDER/ODER Sektion erstellt für '{self.selected_volk_name}'")
            return  # Früher Return für Halbelf - keine weiteren Sektionen

        # NEUE: Menschen-Vielseitig ENTWEDER/ODER Sektion
        if zusatzelemente.get('menschen_vielseitig', False):
            vielseitig_section = self._create_menschen_vielseitig_section()
            zusatzelemente_container.add_widget(vielseitig_section)
            sections_added += 1
            Logger.debug(f"Menschen Vielseitig Sektion erstellt für '{self.selected_volk_name}'")
            return  # Früher Return - spezielle Sektion

        # Freie Talente Sektion (inkl. Goblin)
        if zusatzelemente.get('freie_talente', False):
            # ERWEITERT: Volk-spezifische Titel
            if self.selected_volk_name.lower() in ["goblin", "goblins"]:
                titel = "Überlebenskünstler (Freies Anfängertalent)"
            else:
                titel = "Freies Anfängertalent"
                
            talent_section = self._create_zusatzelement_section(
                titel,
                self.selected_volk_name,
                'talent',
                lambda: get_freie_talente(charakter),
                lambda talent: self._select_talent(self.selected_volk_name, talent),
                "Wähle ein freies Anfängertalent",
                get_alle_items_func=lambda: get_freie_talente(charakter, nur_verfuegbare=False)
            )
            zusatzelemente_container.add_widget(talent_section)
            sections_added += 1

        # ERWEITERT: Attribute Sektion mit verbessertem Titel
        if zusatzelemente.get('freie_attribute', False):
            attribut_optionen = zusatzelemente.get('attribut_optionen', [])
            
            # ERWEITERT: Volk-spezifische Titel
            if self.selected_volk_name.lower() in ["halbork", "halborks"]:
                titel = "Abgehärtet (Stärke oder Konstitution)"
            elif len(attribut_optionen) == 2:
                titel = f"Attribut wählen ({' oder '.join(attribut_optionen)})"
            elif len(attribut_optionen) > 2:
                titel = "Freies Attribut"
            else:
                titel = "Freies Attribut"
            
            attribut_section = self._create_zusatzelement_section(
                titel,
                self.selected_volk_name,
                'attribut',
                lambda: attribut_optionen,  # Verwende spezifische Optionen
                lambda attribut: self._select_attribut(self.selected_volk_name, attribut),
                "Wähle ein Attribut"
            )
            zusatzelemente_container.add_widget(attribut_section)
            sections_added += 1

        # Verstandsbasierte Fertigkeiten Sektion
        if zusatzelemente.get('freie_fertigkeiten', False):
            fertigkeit_section = self._create_zusatzelement_section(
                "Verstandsbasierte Fertigkeit",
                self.selected_volk_name,
                'fertigkeit',
                lambda: get_verfuegbare_fertigkeiten(charakter, nur_verstand=True),
                lambda fertigkeit: self._select_fertigkeit(self.selected_volk_name, fertigkeit),
                "Wähle eine Fertigkeit"
            )
            zusatzelemente_container.add_widget(fertigkeit_section)
            sections_added += 1
            
        Logger.debug(f"Zusatzelemente für Volk '{self.selected_volk_name}' aktualisiert - {sections_added} Sektionen")
        
        # Debug-Info für Attribut-Optionen ausgeben
        if zusatzelemente.get('freie_attribute', False):
            Logger.info(f"Volk '{self.selected_volk_name}' hat Attribut-Optionen: {zusatzelemente.get('attribut_optionen', [])}")

    def _create_zusatzelement_section(self, titel, volk_name, auswahl_typ, get_options_func, select_func, placeholder_text, get_alle_items_func=None):
        """Erstellt eine Sektion für Zusatzelemente."""
        # Hauptcontainer für die Sektion
        section_card = MDCard(
            size_hint_x=1,
            size_hint_y=None,
            padding=dp(14),
            spacing=dp(10),
            elevation=3,
            radius=[12],
            md_bg_color=self.theme_cls.surfaceContainerHighColor,
            style="elevated",
        )

        section_content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10)
        )
        section_content.bind(minimum_height=section_content.setter('height'))
        section_card.bind(minimum_height=section_card.setter('height'))
        
        # Titel der Sektion
        titel_label = MDLabel(
            text=f"{titel}:",
            font_style="Body",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='center',
            bold=True
        )
        
        # Auswahl-Bereich
        auswahl_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(55),
            spacing=dp(20)
        )
        
        # Aktuell ausgewählten Text ermitteln
        current_selection = self.voelker_auswahlen.get(volk_name, {}).get(auswahl_typ, placeholder_text)
        text_color = "Primary" if current_selection != placeholder_text else "Secondary"
        
        # Auswahl-Text mit dynamischer Höhe
        auswahl_label = MDLabel(
            text=current_selection,
            font_style="Body",
            theme_text_color=text_color,
            size_hint_x=0.7,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        auswahl_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
        auswahl_label.bind(text_size=lambda instance, size: setattr(instance, 'height', max(dp(30), instance.texture_size[1])))
        
        # Dropdown-Button
        dropdown_button = MDIconButton(
            icon="chevron-down",
            size_hint=(None, None),
            size=(dp(55), dp(55)),
            on_release=lambda x: self._show_dropdown_menu(
                get_options_func(),
                select_func,
                dropdown_button,
                get_options_func=get_options_func,
                get_alle_items_func=get_alle_items_func
            )
        )
        
        auswahl_row.add_widget(auswahl_label)
        auswahl_row.add_widget(dropdown_button)
        
        section_content.add_widget(titel_label)
        section_content.add_widget(auswahl_row)
        
        section_card.add_widget(section_content)
        
        return section_card

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
                # UI-lokale Auswahl speichern für Anzeige
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}
                self.voelker_auswahlen[volk_name]['talent'] = talent_name
                
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
                # UI-lokale Auswahl speichern für Anzeige
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}
                self.voelker_auswahlen[volk_name]['attribut'] = attribut_name
                
                # UI aktualisieren
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
                # UI-lokale Auswahl speichern für Anzeige
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}
                self.voelker_auswahlen[volk_name]['fertigkeit'] = fertigkeit_name
                
                # UI aktualisieren  
                Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
                
        except Exception as e:
            Logger.error(f"Fehler bei Fertigkeiten-Auswahl (UI): {e}", exc_info=True)

    def _update_selected_volk_details(self):
        """Aktualisiert die Details des ausgewählten Volks."""
        selected_volk_container = self.ids.selected_volk_container
        selected_volk_container.clear_widgets()
        
        if not self.selected_volk_name:
            return
        
        charakter = self.controller.charakter
        
        if self.selected_volk_name not in charakter.voelker:
            Logger.warning(f"Volk '{self.selected_volk_name}' nicht in voelker gefunden")
            return
        
        volk_obj = charakter.voelker[self.selected_volk_name]  # Das ist ein Volk-Objekt
        
        # Titel mit reduzierter Schriftgröße
        title_label = MDLabel(
            text=self.selected_volk_name,
            font_style="Title",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(35),
            halign='left',
            valign='center',
            bold=True
        )
        selected_volk_container.add_widget(title_label)
        
        # Details strukturiert anzeigen - KORRIGIERT: Direkter Zugriff auf Objekt-Attribute
        detail_sections = [
            ('Handicaps', getattr(volk_obj, 'handicaps', [])),
            ('Besonderheiten', getattr(volk_obj, 'besonderheiten', [])),
            ('Talente', getattr(volk_obj, 'talente', [])),
        ]
        
        # Beschreibung nur hinzufügen, wenn sie existiert
        if hasattr(volk_obj, 'beschreibung'):
            detail_sections.append(('Beschreibung', getattr(volk_obj, 'beschreibung', '')))
        
        for section_title, content in detail_sections:
            if self._has_valid_content(content):
                # Sektion-Titel mit reduzierter Schriftgröße
                section_label = MDLabel(
                    text=f"{section_title}:",
                    font_style="Body",
                    theme_text_color="Primary",
                    size_hint_y=None,
                    height=dp(28),
                    halign='left',
                    valign='center',
                    bold=True
                )
                selected_volk_container.add_widget(section_label)

                # Sektion-Inhalt mit dynamischer Höhe
                formatted_text = self._format_content(content)
                content_label = MDLabel(
                    text=formatted_text,
                    font_style="Body",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(40),
                    halign='left',
                    valign='top',
                    markup=True
                )

                def _update_label_height(label, *args):
                    """Setzt text_size und berechnet Höhe nach Layout-Pass"""
                    if label.width > 0:
                        label.text_size = (label.width - dp(10), None)
                        label.texture_update()
                        label.height = max(dp(30), label.texture_size[1] + dp(10))

                # Erst nach dem nächsten Frame, wenn width bekannt ist
                content_label.bind(
                    width=lambda inst, w: Clock.schedule_once(lambda dt: _update_label_height(inst), 0)
                )

                selected_volk_container.add_widget(content_label)

    def _has_valid_content(self, content):
        """Prüft, ob Content valid und nicht leer ist."""
        if content is None:
            return False
        if isinstance(content, list):
            return len(content) > 0 and any(item and str(item).strip() for item in content)
        if isinstance(content, str):
            return content.strip() != ""
        return bool(content)

    def _format_content(self, content):
        """Formatiert den Inhalt für bessere Darstellung."""
        try:
            if isinstance(content, list):
                valid_items = [str(item).strip() for item in content if item and str(item).strip()]
                if not valid_items:
                    return "Keine Details verfügbar"
                # VERBESSERT: Mehr Abstand zwischen Bulletpoints
                return "\n\n".join([f"• {item}" for item in valid_items])  # Doppelte Leerzeile für besseren Abstand
            else:
                text = str(content).strip()
                if not text:
                    return "Keine Details verfügbar"
                
                # Lange kommaseparierte Listen formatieren
                if ", " in text and len(text) > 80:
                    parts = [part.strip() for part in text.split(", ") if part.strip()]
                    # VERBESSERT: Mehr Abstand zwischen Bulletpoints
                    return "\n\n".join([f"• {part}" for part in parts])  # Doppelte Leerzeile
                
                # Lange Texte bei Satzzeichen umbrechen
                if len(text) > 100:
                    sentences = []
                    current = ""
                    for char in text:
                        current += char
                        if char in '.!?' and len(current) > 40:
                            sentences.append(current.strip())
                            current = ""
                    if current.strip():
                        sentences.append(current.strip())
                    # VERBESSERT: Bessere Formatierung für Sätze
                    return "\n\n".join(sentences) if len(sentences) > 1 else text
                
                return text
        except Exception as e:
            Logger.error(f"Fehler beim Formatieren des Inhalts: {e}")
            return "Fehler beim Anzeigen der Details"

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

            # Hauptcontainer für die Sektion
            section_card = MDCard(
                size_hint_x=1,
                size_hint_y=None,
                padding=dp(14),
                elevation=3,
                radius=[12],
                md_bg_color=self.theme_cls.surfaceContainerHighColor,
                style="elevated",
            )
            section_card.bind(minimum_height=section_card.setter('height'))

            section_content = MDBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                spacing=dp(10)
            )
            section_content.bind(minimum_height=section_content.setter('height'))

            # Titel der Sektion mit reduzierter Schriftgröße
            titel_label = MDLabel(
                text="Erbe (ENTWEDER freies Talent ODER Geschicklichkeit W4 -> W6):",
                font_style="Body",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(40),
                halign='left',
                valign='top',
                bold=True
            )
            titel_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
            titel_label.bind(text_size=lambda instance, size: setattr(instance, 'height', max(dp(40), instance.texture_size[1] + dp(10))))

            # Zwei Buttons für die Auswahl
            buttons_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(55),
                spacing=dp(20)
            )

            # Button 1: Freies Talent - filled wenn ausgewählt
            talent_button = MDButton(
                style="filled" if hat_talent else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=dp(48),
                on_release=lambda x: self._halbelf_waehle_talent()
            )
            talent_button.add_widget(MDButtonText(text="Freies Talent"))

            # Button 2: Geschicklichkeit +2 - filled wenn ausgewählt
            attribut_button = MDButton(
                style="filled" if hat_attribut else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=dp(48),
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
                    height=dp(30),
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

            # Hauptcontainer
            section_card = MDCard(
                size_hint_x=1,
                size_hint_y=None,
                padding=dp(14),
                elevation=3,
                radius=[12],
                md_bg_color=self.theme_cls.surfaceContainerHighColor,
                style="elevated",
            )
            section_card.bind(minimum_height=section_card.setter('height'))

            section_content = MDBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                spacing=dp(10)
            )
            section_content.bind(minimum_height=section_content.setter('height'))

            # Titel
            titel_label = MDLabel(
                text="Vielseitig (ENTWEDER freies Talent ODER +2 Fertigkeitspunkte):",
                font_style="Body",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(40),
                halign='left',
                valign='top',
                bold=True
            )
            titel_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
            titel_label.bind(text_size=lambda instance, size: setattr(instance, 'height', max(dp(40), instance.texture_size[1] + dp(10))))

            # Zwei Buttons
            buttons_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(55),
                spacing=dp(20)
            )

            # Button 1: Freies Talent
            talent_button = MDButton(
                style="filled" if hat_talent else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=dp(48),
                on_release=lambda x: self._mensch_vielseitig_waehle_talent()
            )
            talent_button.add_widget(MDButtonText(text="Freies Talent"))

            # Button 2: +2 Fertigkeitspunkte
            fp_button = MDButton(
                style="filled" if hat_fertigkeitspunkte else "outlined",
                size_hint_x=0.5,
                size_hint_y=None,
                height=dp(48),
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
                    height=dp(30),
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