# views/voelker_view.py - UI-Komponente mit ausgelagerter Geschäftslogik
"""
View-Komponente für Völker nach dem MVC-Pattern.
ÜBERARBEITET: UI-Darstellung getrennt von Geschäftslogik (volk_funktionen.py)
"""

from kivy.lang import Builder
from kivy.app import App
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDIconButton
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
    DEFAULT_TALENT_TEXT, DEFAULT_ATTRIBUT_TEXT, DEFAULT_FERTIGKEIT_TEXT,
    NO_TALENT_AVAILABLE_TEXT, NO_ATTRIBUT_AVAILABLE_TEXT, NO_FERTIGKEIT_AVAILABLE_TEXT
)

# Logger konfigurieren
Logger = logging.getLogger(__name__)

# KV-String mit noch mehr Padding für Scrollleisten
KV_STRING = '''
<VoelkerWidget>:
    orientation: 'vertical'
    padding: [dp(20), dp(15), dp(20), dp(15)]
    spacing: dp(20)
    md_bg_color: self.theme_cls.backgroundColor

    MDLabel:
        text: "Völker"
        size_hint_y: None
        height: dp(50)
        halign: 'left'
        font_style: "Headline"
        theme_text_color: "Primary"

    # Völker-Chips Container - Noch mehr Padding für Scrollleisten
    MDCard:
        size_hint_y: None
        height: dp(160)
        padding: [dp(25), dp(20), dp(50), dp(20)]  # Noch mehr Padding rechts
        elevation: 2
        radius: [10]
        md_bg_color: self.theme_cls.surfaceContainerLowColor
        style: "elevated"

        ScrollView:
            size_hint: (1, 1)
            do_scroll_x: True
            do_scroll_y: False
            bar_width: dp(10)  # Schmalere Scrollleiste
            bar_margin: dp(15)  # Mehr Abstand
            scroll_type: ['bars']

            MDGridLayout:
                id: chips_layout
                cols: 1  # Wird dynamisch angepasst
                size_hint_x: None
                width: self.minimum_width
                spacing: dp(15)
                padding: [dp(15), dp(20), dp(40), dp(20)]  # Noch mehr Padding rechts
                adaptive_height: True

    # Zusatzelemente Container
    MDBoxLayout:
        id: zusatzelemente_container
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        spacing: dp(20)

    # Ausgewähltes Volk Details Container - Mehr Padding für Scrollleisten
    ScrollView:
        size_hint: (1, 1)
        do_scroll_x: False
        do_scroll_y: True
        bar_width: dp(10)  # Schmalere Scrollleiste
        bar_margin: dp(20)  # Noch mehr Abstand
        scroll_type: ['bars']

        MDBoxLayout:
            id: selected_volk_container
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(25)
            padding: [0, dp(20), dp(50), dp(30)]  # Noch mehr Padding rechts
'''

Builder.load_string(KV_STRING)


class VoelkerWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Völkern.
    ÜBERARBEITET: Reine UI-Komponente, Geschäftslogik in volk_funktionen.py
    """
    controller = ObjectProperty(None)
    voelker_auswahlen = DictProperty({})
    selected_volk_name = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.voelker_auswahlen = {}
        self.selected_volk_name = None
        self.dropdown_menu = None
        
        # Controller aus der App initialisieren
        Clock.schedule_once(self._initialize_controller, 0)
        Clock.schedule_once(self.aktualisiere_ui, 0.1)

    def set_controller(self, controller):
        """Setzt den Controller für das Widget."""
        self.controller = controller
        if controller and hasattr(controller, 'charakter'):
            controller.charakter.bind(on_charakter_change=self.aktualisiere_ui)
            self.aktualisiere_ui()

    def _initialize_controller(self, dt=None):
        """Initialisiert die Verbindung zum Controller aus der App."""
        try:
            app = App.get_running_app()
            if hasattr(app, 'controller'):
                self.controller = app.controller
                if hasattr(self.controller, 'charakter'):
                    self.controller.charakter.bind(on_charakter_change=self.aktualisiere_ui)
                Logger.debug("VoelkerWidget: Controller erfolgreich initialisiert")
            else:
                Logger.warning("VoelkerWidget: Kein Controller in der App gefunden")
                Clock.schedule_once(self._initialize_controller, 1.0)
        except Exception as e:
            Logger.error(f"VoelkerWidget: Fehler bei Controller-Initialisierung: {e}")
            Clock.schedule_once(self._initialize_controller, 1.0)

    def aktualisiere_ui(self, *args):
        """Aktualisiert die gesamte UI basierend auf den aktuellen Charakterdaten."""
        Logger.debug("VoelkerWidget: aktualisiere_ui aufgerufen")
        
        try:
            # Controller-Verfügbarkeit prüfen
            if not self.controller or not hasattr(self.controller, 'charakter'):
                Logger.warning("VoelkerWidget: Controller nicht verfügbar - Retry in 1s")
                Clock.schedule_once(self.aktualisiere_ui, 1.0)
                return
                
            # UI-Container prüfen
            if not hasattr(self, 'ids') or 'chips_layout' not in self.ids:
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

            # UI-Komponenten aktualisieren
            self._update_voelker_chips()
            self._update_zusatzelemente()
            self._update_selected_volk_details()
                
            Logger.debug(f"VoelkerWidget: UI erfolgreich aktualisiert mit {len(charakter.voelker)} Völkern")

        except Exception as e:
            Logger.error(f"Fehler in aktualisiere_ui: {e}", exc_info=True)

    def _show_no_data_message(self):
        """Zeigt eine Nachricht an, wenn keine Völker-Daten verfügbar sind."""
        for container_id in ['chips_layout', 'zusatzelemente_container', 'selected_volk_container']:
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

    def _update_voelker_chips(self):
        """Aktualisiert die MDChips für die Völker-Auswahl."""
        chips_layout = self.ids.chips_layout
        chips_layout.clear_widgets()
        
        charakter = self.controller.charakter
        voelker_count = len(charakter.voelker)
        
        # Optimale Anzahl Spalten für Grid-Layout berechnen
        if voelker_count <= 8:
            cols = min(voelker_count, 8)  # Eine Zeile für wenige Völker
        else:
            cols = max(6, (voelker_count + 1) // 2)  # Zwei Zeilen für viele Völker
        
        chips_layout.cols = cols
        
        # Einheitliche Chip-Breite berechnen
        max_chip_width = dp(140)  # Feste Breite für bessere Anordnung
        total_width = (max_chip_width * cols) + (dp(15) * (cols - 1)) + dp(60)
        chips_layout.width = total_width
        
        for volk_name in sorted(charakter.voelker.keys()):  # Alphabetisch sortiert
            ist_ausgewaehlt = charakter.voelker_selected.get(volk_name, False)
            
            # Chip erstellen
            chip = MDChip(
                size_hint_x=None,
                size_hint_y=None,
                width=max_chip_width,
                height=dp(45),
                radius=dp(22),
                elevation=4 if ist_ausgewaehlt else 2,
                md_bg_color=self.theme_cls.primaryColor if ist_ausgewaehlt else self.theme_cls.surfaceContainerColor,
                on_release=lambda x, name=volk_name: self._on_volk_chip_selected(name)
            )
            
            # Chip-Text
            chip_text = MDChipText(
                text=volk_name,
                theme_text_color="Custom" if ist_ausgewaehlt else "Primary",
                text_color=(1, 1, 1, 1) if ist_ausgewaehlt else None
            )
            
            chip.add_widget(chip_text)
            chips_layout.add_widget(chip)

    def _on_volk_chip_selected(self, volk_name):
        """Behandelt die Auswahl eines Völker-Chips."""
        try:
            charakter = self.controller.charakter
            
            # Prüfen ob bereits ausgewählt
            current_selection = charakter.voelker_selected.get(volk_name, False)
            
            if current_selection:
                # Bereits ausgewählt - abwählen
                success = abwaehlen_volk(charakter, volk_name)
                if success:
                    self.selected_volk_name = None
                    # Auswahlen zurücksetzen
                    reset_volk_auswahlen(charakter, volk_name, self.voelker_auswahlen)
                    Logger.info(f"Volk '{volk_name}' abgewählt")
                else:
                    Logger.error(f"Fehler beim Abwählen von Volk '{volk_name}'")
                    return
            else:
                # Nicht ausgewählt - auswählen
                success = waehle_volk(charakter, volk_name)
                if success:
                    self.selected_volk_name = volk_name
                    Logger.info(f"Volk '{volk_name}' ausgewählt")
                else:
                    Logger.error(f"Fehler beim Auswählen von Volk '{volk_name}'")
                    return
            
            # UI-Updates mit leichter Verzögerung für bessere Performance
            Clock.schedule_once(lambda dt: self._update_voelker_chips(), 0.1)
            Clock.schedule_once(lambda dt: self._update_zusatzelemente(), 0.1)
            Clock.schedule_once(lambda dt: self._update_selected_volk_details(), 0.1)
            
        except Exception as e:
            Logger.error(f"Fehler bei Volk-Auswahl: {e}", exc_info=True)

    def _update_zusatzelemente(self):
        """Aktualisiert die Zusatzelemente-Bereiche."""
        zusatzelemente_container = self.ids.zusatzelemente_container
        zusatzelemente_container.clear_widgets()
        
        if not self.selected_volk_name:
            return
            
        charakter = self.controller.charakter
        
        # Verfügbare Zusatzelemente von der Geschäftslogik abrufen
        zusatzelemente = get_volk_zusatzelemente(charakter, self.selected_volk_name)
        
        sections_added = 0
        
        # Freie Talente Sektion
        if zusatzelemente.get('freie_talente', False):
            talent_section = self._create_zusatzelement_section(
                "Freies Anfängertalent",
                self.selected_volk_name,
                'talent',
                lambda: get_freie_talente(charakter),
                lambda talent: self._select_talent(self.selected_volk_name, talent),
                "Wähle ein freies Anfängertalent"
            )
            zusatzelemente_container.add_widget(talent_section)
            sections_added += 1

        # Erhöhte Attribute Sektion - verwende spezifische Attribut-Optionen
        if zusatzelemente.get('freie_attribute', False):
            attribut_optionen = zusatzelemente.get('attribut_optionen', [])
            
            # Bestimme den Titel basierend auf der Anzahl der Optionen
            if len(attribut_optionen) == 2:
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

    def _create_zusatzelement_section(self, titel, volk_name, auswahl_typ, get_options_func, select_func, placeholder_text):
        """Erstellt eine Sektion für Zusatzelemente."""
        
        # Hauptcontainer für die Sektion
        section_card = MDCard(
            size_hint_y=None,
            height=dp(140),
            padding=dp(25),
            spacing=dp(15),
            elevation=3,
            radius=[12],
            md_bg_color=self.theme_cls.surfaceContainerHighColor,
            style="elevated"
        )
        
        section_content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(90),
            spacing=dp(15)
        )
        
        # Titel der Sektion
        titel_label = MDLabel(
            text=f"{titel}:",
            font_style="Title",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(35),
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
        
        # Auswahl-Text
        auswahl_label = MDLabel(
            text=current_selection,
            font_style="Body",
            theme_text_color=text_color,
            size_hint_x=0.7,
            halign='left',
            valign='center'
        )
        auswahl_label.bind(size=lambda instance, size: setattr(instance, 'text_size', (size[0], None)))
        
        # Dropdown-Button
        dropdown_button = MDIconButton(
            icon="chevron-down",
            size_hint=(None, None),
            size=(dp(55), dp(55)),
            on_release=lambda x: self._show_dropdown_menu(
                get_options_func(),
                select_func,
                dropdown_button
            )
        )
        
        auswahl_row.add_widget(auswahl_label)
        auswahl_row.add_widget(dropdown_button)
        
        section_content.add_widget(titel_label)
        section_content.add_widget(auswahl_row)
        
        section_card.add_widget(section_content)
        
        return section_card

    def _show_dropdown_menu(self, items, callback, caller):
        """Zeigt ein verbessertes Dialog-Menü mit Suchfeld."""
        if hasattr(self, 'dropdown_menu') and self.dropdown_menu:
            self.dropdown_menu.dismiss()
        
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
            self._show_search_dialog(items, callback, caller)
            
        except Exception as e:
            Logger.error(f"Fehler beim Erstellen des Dialog-Menüs: {e}", exc_info=True)

    def _show_search_dialog(self, items, callback, caller):
        """Zeigt einen erweiterten Dialog mit Suchfeld für Talent/Attribut/Fertigkeiten-Auswahl."""
        from kivymd.uix.dialog import (
            MDDialog, MDDialogHeadlineText, MDDialogButtonContainer, 
            MDDialogContentContainer
        )
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
        from kivymd.uix.scrollview import MDScrollView
        
        try:
            # Hauptcontainer für den Dialog
            dialog_content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                adaptive_height=True
            )
            
            # Suchfeld
            search_field = MDTextField(
                mode="outlined",
                size_hint_y=None,
                height=dp(56)
            )
            search_hint = MDTextFieldHintText(text="Suchen...")
            search_field.add_widget(search_hint)
            
            # Scrollbare Liste
            scroll_view = MDScrollView(
                size_hint_y=None,
                height=dp(300)
            )
            
            items_list = MDList(
                adaptive_height=True
            )
            
            # Items zur Liste hinzufügen
            for item in sorted(items):
                if item and str(item).strip():
                    list_item = MDListItem(
                        adaptive_height=True,
                        on_release=lambda x, selected_item=item: self._on_search_dialog_item_selected(callback, selected_item)
                    )
                    list_item.add_widget(MDListItemHeadlineText(text=str(item)))
                    items_list.add_widget(list_item)
            
            scroll_view.add_widget(items_list)
            
            # Such-Funktionalität
            def filter_items(instance, text):
                items_list.clear_widgets()
                search_text = text.lower()
                
                filtered_items = [item for item in sorted(items) 
                                if item and search_text in str(item).lower()]
                
                for item in filtered_items:
                    list_item = MDListItem(
                        adaptive_height=True,
                        on_release=lambda x, selected_item=item: self._on_search_dialog_item_selected(callback, selected_item)
                    )
                    list_item.add_widget(MDListItemHeadlineText(text=str(item)))
                    items_list.add_widget(list_item)
            
            search_field.bind(text=filter_items)
            
            # Container zusammenbauen
            dialog_content.add_widget(search_field)
            dialog_content.add_widget(scroll_view)
            
            # Dialog erstellen
            self.search_dialog = MDDialog(
                MDDialogHeadlineText(text="Auswahl treffen"),
                MDDialogContentContainer(
                    dialog_content,
                    orientation="vertical",
                    padding=dp(0),
                ),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(text="Abbrechen"),
                        style="text",
                        on_release=lambda x: self.search_dialog.dismiss(),
                    ),
                    spacing="8dp",
                ),
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

    def _on_dropdown_item_selected(self, callback, item):
        """Behandelt die Auswahl eines Dropdown-Items."""
        try:
            Logger.debug(f"Dropdown-Item ausgewählt: {item}")
            
            if self.dropdown_menu:
                self.dropdown_menu.dismiss()
                
            # Überprüfen ob es sich um eine Fehlermeldung handelt
            if item in [NO_TALENT_AVAILABLE_TEXT, NO_ATTRIBUT_AVAILABLE_TEXT, NO_FERTIGKEIT_AVAILABLE_TEXT]:
                Logger.warning(f"Fehlermeldung ausgewählt: {item}")
                return
                
            # Callback ausführen
            if callback:
                callback(item)
                Logger.debug(f"Callback für Item '{item}' ausgeführt")
            else:
                Logger.warning("Kein Callback für Dropdown-Auswahl definiert")
                
        except Exception as e:
            Logger.error(f"Fehler bei Dropdown-Auswahl: {e}", exc_info=True)

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
            placeholder = MDLabel(
                text="Wähle ein Volk aus den Chips oben aus",
                halign='center',
                theme_text_color="Secondary",
                font_style="Body",
                size_hint_y=None,
                height=dp(60)
            )
            selected_volk_container.add_widget(placeholder)
            return
            
        charakter = self.controller.charakter
        volk = charakter.voelker.get(self.selected_volk_name)
        
        if not volk:
            error_label = MDLabel(
                text=f"Fehler: Volk '{self.selected_volk_name}' nicht gefunden",
                halign='center',
                theme_text_color="Error",
                font_style="Body",
                size_hint_y=None,
                height=dp(60)
            )
            selected_volk_container.add_widget(error_label)
            return

        try:
            # Volk-Details Cards erstellen
            volk_details = self._create_volk_details_cards(self.selected_volk_name, volk)
            for card in volk_details:
                selected_volk_container.add_widget(card)
                
            Logger.debug(f"Volk-Details für '{self.selected_volk_name}' erfolgreich angezeigt")
            
        except Exception as e:
            Logger.error(f"Fehler bei Volk-Details-Erstellung: {e}", exc_info=True)
            error_label = MDLabel(
                text=f"Fehler beim Laden der Volk-Details: {str(e)}",
                halign='center',
                theme_text_color="Error",
                font_style="Body",
                size_hint_y=None,
                height=dp(60)
            )
            selected_volk_container.add_widget(error_label)

    def _create_volk_details_cards(self, volk_name, volk):
        """Erstellt Cards mit den Details des ausgewählten Volks."""
        cards = []
        
        try:
            # Header-Card
            header_card = self._create_header_card(volk_name)
            cards.append(header_card)
            
            # Detail-Cards für verfügbare Eigenschaften
            properties = [
                ('handicaps', 'Handicaps', 'error'),
                ('talente', 'Talente', 'success'),
                ('besonderheiten', 'Besonderheiten', 'info')
            ]
            
            for prop_name, title, card_type in properties:
                content = getattr(volk, prop_name, None)
                if content and self._is_valid_content(content):
                    detail_card = self._create_detail_card(title, content, card_type)
                    cards.append(detail_card)
            
            # Falls keine Detail-Cards erstellt wurden
            if len(cards) == 1:  # Nur Header-Card
                info_card = self._create_info_card()
                cards.append(info_card)
                
        except Exception as e:
            Logger.error(f"Fehler bei Card-Erstellung für '{volk_name}': {e}")
            # Minimal-Fallback
            fallback_card = MDLabel(
                text=f"Fehler beim Laden der Details für {volk_name}",
                halign='center',
                theme_text_color="Error",
                size_hint_y=None,
                height=dp(60)
            )
            cards = [fallback_card]
        
        return cards

    def _create_header_card(self, volk_name):
        """Erstellt die Header-Card für das Volk."""
        header_card = MDCard(
            size_hint_y=None,
            height=dp(90),
            padding=dp(25),
            elevation=4,
            radius=[12],
            md_bg_color=self.theme_cls.primaryColor,
            style="elevated"
        )
        
        header_label = MDLabel(
            text=volk_name,
            font_style="Headline",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='center'
        )
        
        header_card.add_widget(header_label)
        return header_card

    def _create_detail_card(self, titel, content, card_type="info"):
        """Erstellt eine Detail-Card für Volk-Eigenschaften."""
        
        # Card-Farben
        color_mapping = {
            "error": self.theme_cls.errorContainerColor,
            "success": self.theme_cls.surfaceContainerHighColor,
            "info": self.theme_cls.surfaceContainerColor
        }
        bg_color = color_mapping.get(card_type, self.theme_cls.surfaceContainerColor)
        
        # Text formatieren
        formatted_text = self._format_content(content)
        
        # Höhe berechnen
        estimated_lines = max(formatted_text.count('\n') + 1, len(formatted_text) // 50 + 1, 2)
        card_height = dp(80) + (estimated_lines * dp(30))
        card_height = max(card_height, dp(130))
        card_height = min(card_height, dp(450))
        
        # Card erstellen
        detail_card = MDCard(
            size_hint_y=None,
            height=card_height,
            padding=dp(30),
            spacing=dp(20),
            elevation=3,
            radius=[12],
            md_bg_color=bg_color,
            style="elevated"
        )
        
        card_content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=card_height - dp(60),
            spacing=dp(20)
        )
        
        # Titel
        title_label = MDLabel(
            text=f"{titel}:",
            font_style="Title",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(35),
            halign='left',
            bold=True
        )
        
        # Inhalt
        content_label = MDLabel(
            text=formatted_text,
            font_style="Body",
            theme_text_color="Primary",
            size_hint_y=None,
            height=card_height - dp(95),
            halign='left',
            valign='top',
            text_size=(None, None)
        )
        
        # Text-Wrapping
        content_label.bind(size=lambda instance, size: setattr(
            instance, 'text_size', (max(size[0] - dp(60), dp(200)), None)
        ))
        
        card_content.add_widget(title_label)
        card_content.add_widget(content_label)
        detail_card.add_widget(card_content)
        
        return detail_card

    def _create_info_card(self):
        """Erstellt eine Info-Card für fehlende Details."""
        info_card = MDCard(
            size_hint_y=None,
            height=dp(100),
            padding=dp(25),
            elevation=2,
            radius=[12],
            md_bg_color=self.theme_cls.surfaceContainerLowColor,
            style="elevated"
        )
        
        info_label = MDLabel(
            text="Keine weiteren Details verfügbar",
            font_style="Body",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(50),
            halign='center',
            valign='center'
        )
        
        info_card.add_widget(info_label)
        return info_card

    def _is_valid_content(self, content):
        """Prüft ob der Inhalt gültig und nicht leer ist."""
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
                return "\n".join([f"• {item}" for item in valid_items])
            else:
                text = str(content).strip()
                if not text:
                    return "Keine Details verfügbar"
                
                # Lange kommaseparierte Listen formatieren
                if ", " in text and len(text) > 80:
                    parts = [part.strip() for part in text.split(", ") if part.strip()]
                    return "\n".join([f"• {part}" for part in parts])
                
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
                    return "\n".join(sentences) if len(sentences) > 1 else text
                
                return text
        except Exception as e:
            Logger.error(f"Fehler beim Formatieren des Inhalts: {e}")
            return "Fehler beim Anzeigen der Details"