# views/voelker_view.py - Erweiterte Version für alle Völker-Wahlmöglichkeiten
"""
View-Komponente für Völker nach dem MVC-Pattern.
Stellt die Benutzerschnittstelle zur Anzeige und Verwaltung von Völkern bereit.
VOLLSTÄNDIG ERWEITERT: Mit allen Völker-spezifischen Wahlmöglichkeiten
"""

from kivy.lang import Builder
from kivy.app import App
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer
)
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, DictProperty
from kivy.metrics import dp
import logging

# Logger konfigurieren
Logger = logging.getLogger(__name__)

# Konstanten für bessere Lesbarkeit und Wartbarkeit
DEFAULT_TALENT_TEXT = 'Wähle ein freies Talent'
DEFAULT_ATTRIBUT_TEXT = 'Wähle ein Attribut'
DEFAULT_FERTIGKEIT_TEXT = 'Wähle eine Fertigkeit'
NO_TALENT_AVAILABLE_TEXT = 'Keine freien Talente verfügbar'
NO_ATTRIBUT_AVAILABLE_TEXT = 'Keine Attribute verfügbar'
NO_FERTIGKEIT_AVAILABLE_TEXT = 'Keine Fertigkeiten verfügbar'
CHECKBOX_WIDTH = 50
VOLK_LABEL_WIDTH = 200  # Reduziert für mehr Platz
TALENT_LABEL_WIDTH = dp(150)  
ATTRIBUT_LABEL_WIDTH = dp(150)  
FERTIGKEIT_LABEL_WIDTH = dp(150)  # Neu für Fertigkeiten
ROW_HEIGHT = 40
INFO_ROW_HEIGHT = 25
PADDING_LEFT = 40

# KV-String
KV_STRING = '''
<VoelkerWidget>:
    orientation: 'vertical'
    padding: 20
    spacing: 10
    md_bg_color: self.theme_cls.backgroundColor  

    ScrollView:
        size_hint: (1, 1)
        do_scroll_x: False
        do_scroll_y: True

        MDGridLayout:
            id: voelker_checkbox_container
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: 10
            padding: 10

            MDLabel:
                text: "Völker"
                size_hint_y: None
                height: 30
                halign: 'left'

            MDGridLayout:
                id: voelker_content_container
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
                padding: (0, 10, 0, 10)
'''

Builder.load_string(KV_STRING)


class VoelkerWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Völkern.
    VOLLSTÄNDIG ERWEITERT: Mit allen Völker-spezifischen Wahlmöglichkeiten
    """
    controller = ObjectProperty()
    
    # Properties für die verschiedenen Wahlmöglichkeiten der Völker
    voelker_auswahlen = DictProperty({})  # Speichert alle Auswahlen pro Volk

    def __init__(self, **kwargs):
        """Initialisiert das VoelkerWidget und setzt Grundkonfiguration."""
        super().__init__(**kwargs)
        self._initialize_controller()
        self.dropdown_menu = None
        self.voraussetzungs_dialog = None
        
        # Initialisiere Völker-Auswahlen
        self.voelker_auswahlen = {}
        
        Clock.schedule_once(self._setup_ui)

    def _initialize_controller(self):
        """Initialisiert die Verbindung zum Controller."""
        app = App.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None
        
        if not self.controller:
            Logger.error("VoelkerWidget: Controller nicht gefunden")
            return
            
        Logger.debug(f"VoelkerWidget initialisiert mit controller: {self.controller}")
        
        # Event-Bindung für Charakteränderungen
        if hasattr(self.controller, 'charakter'):
            self.controller.charakter.bind(on_charakter_change=self.aktualisiere_ui)

    def _setup_ui(self, dt):
        """Initialisierung der UI nach dem Laden des Widgets."""
        Logger.debug("VoelkerWidget: Setup UI gestartet")
        self.aktualisiere_ui()

    def _get_freie_talente(self):
        """Gibt eine alphabetisch sortierte Liste von freien Talenten zurück."""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return [NO_TALENT_AVAILABLE_TEXT]
                
        frei_talente = []
        for name, talent in self.controller.charakter.talente.items():
            if talent.aktiv and not talent.ausgewaehlt:
                frei_talente.append(name)
        
        frei_talente.sort()
        
        if not frei_talente:
            frei_talente = [NO_TALENT_AVAILABLE_TEXT]
            
        return frei_talente

    def _get_verfuegbare_attribute(self):
        """Gibt eine Liste der verfügbaren Attribute für die Erhöhung zurück."""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return [NO_ATTRIBUT_AVAILABLE_TEXT]
        
        standard_attribute = [
            "Stärke", "Geschicklichkeit", "Konstitution", "Verstand", "Willenskraft"
        ]
        
        verfuegbare_attribute = []
        charakter = self.controller.charakter
        
        for attribut_name in standard_attribute:
            if attribut_name in charakter.attribute:
                attribut = charakter.attribute[attribut_name]
                if attribut.wert == 4 and attribut.modifier == 0:
                    verfuegbare_attribute.append(attribut_name)
        
        if not verfuegbare_attribute:
            verfuegbare_attribute = [NO_ATTRIBUT_AVAILABLE_TEXT]
        
        return verfuegbare_attribute

    def _get_verstandsbasierte_fertigkeiten(self):
        """Gibt eine Liste der verstandsbasierten Fertigkeiten zurück."""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            return [NO_FERTIGKEIT_AVAILABLE_TEXT]
        
        charakter = self.controller.charakter
        verstandsbasierte_fertigkeiten = []
        
        # Alle Fertigkeiten durchgehen und prüfen, ob sie verstandsbasiert sind
        for fert_name, fertigkeit in charakter.fertigkeiten.items():
            if (hasattr(fertigkeit, 'attribut') and 
                fertigkeit.attribut and 
                fertigkeit.attribut.attribut_name == 'Verstand'):
                verstandsbasierte_fertigkeiten.append(fert_name)
        
        verstandsbasierte_fertigkeiten.sort()
        
        if not verstandsbasierte_fertigkeiten:
            verstandsbasierte_fertigkeiten = [NO_FERTIGKEIT_AVAILABLE_TEXT]
        
        return verstandsbasierte_fertigkeiten

    def _ist_savage_pathfinder_aktiv(self):
        """Prüft, ob das aktuelle Setting Savage Pathfinder ist."""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            return False
        
        try:
            return self.controller.charakter.ist_savage_pathfinder_setting()
        except Exception as e:
            Logger.error(f"Fehler bei Savage Pathfinder-Prüfung: {e}")
            return False

    def show_talent_search_dialog(self, button, volk_name):
        """Zeigt einen Dialog mit Suchfunktion für die Talentauswahl an."""
        self._show_auswahl_dialog(
            titel="Talent auswählen",
            items=self._get_freie_talente(),
            callback=lambda talent: self._on_talent_select(talent, volk_name),
            search_hint="Talent suchen..."
        )

    def show_attribut_search_dialog(self, button, volk_name):
        """Zeigt einen Dialog für die Attributauswahl an."""
        self._show_auswahl_dialog(
            titel="Attribut auswählen (W4 auf W6 erhöhen)",
            items=self._get_verfuegbare_attribute(),
            callback=lambda attribut: self._on_attribut_select(attribut, volk_name),
            search_hint=None  # Kein Suchfeld für Attribute nötig
        )

    def show_fertigkeit_search_dialog(self, button, volk_name):
        """Zeigt einen Dialog für die Fertigkeitauswahl an."""
        self._show_auswahl_dialog(
            titel="Verstandsbasierte Fertigkeit auswählen",
            items=self._get_verstandsbasierte_fertigkeiten(),
            callback=lambda fertigkeit: self._on_fertigkeit_select(fertigkeit, volk_name),
            search_hint="Fertigkeit suchen..."
        )

    def _show_auswahl_dialog(self, titel, items, callback, search_hint=None):
        """
        Universeller Dialog für Auswahlen mit optionaler Suchfunktion.
        
        Args:
            titel: Titel des Dialogs
            items: Liste der verfügbaren Optionen
            callback: Callback-Funktion für die Auswahl
            search_hint: Hinweistext für Suchfeld (None = kein Suchfeld)
        """
        # Dialog-Content erstellen
        content = MDBoxLayout(
            orientation='vertical', 
            size_hint_y=None,
            height="400dp" if search_hint else "300dp",
            spacing="12dp",
            padding="24dp"
        )
        
        # Optional: Suchfeld erstellen
        search_field = None
        if search_hint:
            search_field = MDTextField(
                mode="outlined",
                children=[MDTextFieldHintText(text=search_hint)]
            )
            content.add_widget(search_field)
        
        # ScrollView für die Liste erstellen
        scroll = MDScrollView(
            size_hint=(1, None),
            height="300dp" if search_hint else "250dp"
        )
        
        # Liste erstellen
        item_list = MDList()
        scroll.add_widget(item_list)
        content.add_widget(scroll)
        
        # Dialog erstellen
        dialog = MDDialog()
        dialog.add_widget(MDDialogHeadlineText(text=titel))
        dialog.add_widget(MDDialogContentContainer(content, orientation="vertical"))
        dialog.add_widget(MDDialogButtonContainer(
            MDButton(
                style="text",
                on_release=lambda x: dialog.dismiss(),
                children=[MDButtonText(text="Abbrechen")]
            ),
            spacing="8dp",
        ))
        
        all_items = items.copy()  # Für die Suche
        
        # Funktion zum Hinzufügen eines Items zur Liste
        def add_item_to_list(item_name):
            item = MDListItem(on_release=lambda x: select_item(item_name))
            item.add_widget(MDListItemHeadlineText(text=item_name))
            item_list.add_widget(item)
        
        # Funktion zum Auswählen eines Items
        def select_item(item_name):
            invalid_items = [NO_TALENT_AVAILABLE_TEXT, NO_ATTRIBUT_AVAILABLE_TEXT, 
                           NO_FERTIGKEIT_AVAILABLE_TEXT, "Keine Treffer gefunden"]
            if item_name not in invalid_items:
                callback(item_name)
            dialog.dismiss()
        
        # Optional: Funktion zum Filtern basierend auf der Sucheingabe
        if search_field:
            def filter_items(instance, value):
                item_list.clear_widgets()
                search_text = value.lower().strip()
                
                filtered_items = []
                if search_text:
                    filtered_items = [t for t in all_items if search_text in t.lower()]
                else:
                    filtered_items = all_items
                
                filtered_items.sort()
                
                if filtered_items:
                    for item in filtered_items:
                        add_item_to_list(item)
                else:
                    add_item_to_list("Keine Treffer gefunden")
            
            search_field.bind(text=filter_items)
        
        # Initial alle Items anzeigen
        for item in items:
            add_item_to_list(item)
        
        dialog.open()

    def _on_talent_select(self, talent_name, volk_name):
        """Wird aufgerufen, wenn ein Talent ausgewählt wird."""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return
                
        if talent_name == NO_TALENT_AVAILABLE_TEXT:
            return

        charakter = self.controller.charakter
        
        # Freies Talent für das spezifische Volk auswählen
        result = self._waehle_freies_talent(talent_name)
        
        if result == "needs_voraussetzungen_confirmation":
            fehlermeldungen = charakter.temp_voraussetzungs_fehler
            self._show_voraussetzungen_dialog(talent_name, fehlermeldungen, volk_name)
            return
        
        if result is True:
            # Speichere die Auswahl für das Volk
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            self.voelker_auswahlen[volk_name]['talent'] = talent_name
            
            Logger.info(f"Freies Talent '{talent_name}' für {volk_name} ausgewählt.")
            charakter.dispatch('on_charakter_change')

    def _on_attribut_select(self, attribut_name, volk_name):
        """Wird aufgerufen, wenn ein Attribut ausgewählt wird."""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            return
                
        if attribut_name == NO_ATTRIBUT_AVAILABLE_TEXT:
            return

        charakter = self.controller.charakter
        
        # Prüfen, ob das Attribut auf W4 steht und erhöhen
        if attribut_name in charakter.attribute:
            attribut = charakter.attribute[attribut_name]
            if attribut.wert == 4 and attribut.modifier == 0:
                attribut.wuerfel.value = 6
                
                # Speichere die Auswahl für das Volk
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}
                self.voelker_auswahlen[volk_name]['attribut'] = attribut_name
                
                Logger.info(f"Attribut '{attribut_name}' für {volk_name} von W4 auf W6 erhöht.")
                charakter.berechne_abgeleitete_werte()
                charakter.dispatch('on_charakter_change')

    def _on_fertigkeit_select(self, fertigkeits_name, volk_name):
        """Wird aufgerufen, wenn eine Fertigkeit ausgewählt wird."""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            return
                
        if fertigkeits_name == NO_FERTIGKEIT_AVAILABLE_TEXT:
            return

        charakter = self.controller.charakter
        
        # Fertigkeit von W4-2 auf W4+0 setzen
        if fertigkeits_name in charakter.fertigkeiten:
            fertigkeit = charakter.fertigkeiten[fertigkeits_name]
            if fertigkeit.wert == 4 and fertigkeit.modifier == -2:
                fertigkeit.wuerfel.modifier = 0
                
                # Speichere die Auswahl für das Volk
                if volk_name not in self.voelker_auswahlen:
                    self.voelker_auswahlen[volk_name] = {}
                self.voelker_auswahlen[volk_name]['fertigkeit'] = fertigkeits_name
                
                Logger.info(f"Fertigkeit '{fertigkeits_name}' für {volk_name} auf W4 gesetzt.")
                charakter.dispatch('on_charakter_change')

    def _waehle_freies_talent(self, talent_name):
        """Hilfsmethode zum Auswählen eines freien Talents."""
        charakter = self.controller.charakter
        
        if hasattr(charakter, 'waehle_freies_talent'):
            return charakter.waehle_freies_talent(talent_name)
        elif hasattr(self.controller, 'waehle_freies_talent'):
            return self.controller.waehle_freies_talent(talent_name)
        else:
            # Fallback auf talent_funktionen
            from functions.talent_funktionen import waehle_freies_talent
            return waehle_freies_talent(charakter, talent_name)

    def _show_voraussetzungen_dialog(self, talent_name, fehlermeldungen, volk_name):
        """Zeigt einen Dialog für nicht erfüllte Voraussetzungen an."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            padding="12dp",
            size_hint_y=None,
            height="200dp"
        )
        
        warning_text = f"Talent '{talent_name}' erfüllt nicht alle Voraussetzungen:\n\n"
        for error in fehlermeldungen:
            warning_text += f"• {error}\n"
        warning_text += "\nTrotzdem auswählen?"
        
        warning_label = MDLabel(
            text=warning_text,
            halign="left",
            valign="top",
            theme_text_color="Error"
        )
        content.add_widget(warning_label)
        
        self.voraussetzungs_dialog = MDDialog(
            MDDialogHeadlineText(text="Voraussetzungen nicht erfüllt"),
            MDDialogContentContainer(content, orientation="vertical"),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self._dismiss_voraussetzungs_dialog(),
                ),
                MDButton(
                    MDButtonText(text="Trotzdem auswählen"),
                    style="text",
                    on_release=lambda x: self._confirm_talent_selection(talent_name, volk_name),
                ),
                spacing="8dp",
            ),
        )
        
        self.voraussetzungs_dialog.open()

    def _dismiss_voraussetzungs_dialog(self):
        """Schließt den Voraussetzungen-Dialog."""
        if self.voraussetzungs_dialog:
            self.voraussetzungs_dialog.dismiss()
            self.voraussetzungs_dialog = None

    def _confirm_talent_selection(self, talent_name, volk_name):
        """Bestätigt die Auswahl eines Talents trotz nicht erfüllter Voraussetzungen."""
        self._dismiss_voraussetzungs_dialog()
        
        charakter = self.controller.charakter
        charakter.ignore_voraussetzungen = True
        
        erfolg = self._waehle_freies_talent(talent_name)
        
        if erfolg:
            if volk_name not in self.voelker_auswahlen:
                self.voelker_auswahlen[volk_name] = {}
            self.voelker_auswahlen[volk_name]['talent'] = talent_name
            
            Logger.info(f"Freies Talent '{talent_name}' für {volk_name} ausgewählt (Voraussetzungen ignoriert).")
            charakter.dispatch('on_charakter_change')

    def aktualisiere_ui(self, *args):
        """Aktualisiert die UI basierend auf dem aktuellen Zustand des Charakters."""
        Logger.debug("VoelkerWidget: aktualisiere_ui aufgerufen")
        
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return
            
        try:
            container = self.ids.voelker_content_container
            container.clear_widgets()

            charakter = self.controller.charakter
            
            # Sicherstellen, dass alle Völker in voelker_selected existieren
            for volk_name in charakter.voelker:
                if volk_name not in charakter.voelker_selected:
                    charakter.voelker_selected[volk_name] = False
            
            # Völker anzeigen
            for volk_name, volk in charakter.voelker.items():
                self._add_volk_row(container, volk_name, volk)
                self._add_volk_details(container, volk)

        except Exception as e:
            Logger.error(f"Fehler in aktualisiere_ui: {e}", exc_info=True)

    def _add_volk_row(self, container, volk_name, volk):
        """Fügt eine Zeile für ein Volk zum Container hinzu."""
        # Hauptzeile für das Volk erstellen
        row_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ROW_HEIGHT,
            spacing=10,
            adaptive_height=True
        )

        # Volk-Name Label
        label = MDLabel(
            text=volk_name,
            halign='left',
            size_hint_x=None,
            width=VOLK_LABEL_WIDTH,
            theme_text_color="Primary"
        )

        # Checkbox für die Auswahl
        charakter = self.controller.charakter
        is_active = charakter.voelker_selected.get(volk_name, False)
        
        checkbox = MDCheckbox(
            active=is_active,
            size_hint_x=None,
            width=CHECKBOX_WIDTH,
            selected_color=self.theme_cls.primary_color
        )
        checkbox.voelker_name = volk_name
        checkbox.bind(active=lambda instance, value, volk_name=volk_name: 
                    self._on_checkbox_active(instance, value, volk_name))

        row_layout.add_widget(label)
        row_layout.add_widget(checkbox)

        # Völker-spezifische UI-Elemente hinzufügen
        self._add_volk_specific_ui(row_layout, volk_name, volk, is_active)

        container.add_widget(row_layout)

    def _add_volk_specific_ui(self, row_layout, volk_name, volk, is_active):
        """
        Fügt völker-spezifische UI-Elemente hinzu basierend auf den Wahlmöglichkeiten.
        
        Args:
            row_layout: Layout, zu dem die Elemente hinzugefügt werden
            volk_name: Name des Volks
            volk: Volk-Objekt
            is_active: Ob das Volk aktuell ausgewählt ist
        """
        auswahl = self.voelker_auswahlen.get(volk_name, {})
        
        # Freies Talent (Menschen, Halbelfen haben das nicht über effects)
        if (volk_name == "Mensch" or 
            (hasattr(volk, 'has_wahlmoeglichkeit') and volk.has_wahlmoeglichkeit('freies_talent'))):
            
            talent_text = auswahl.get('talent', DEFAULT_TALENT_TEXT)
            talent_label = MDLabel(
                text=talent_text,
                size_hint_x=None,
                width=TALENT_LABEL_WIDTH
            )
            
            talent_button = MDIconButton(
                icon="menu-down",
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                on_release=lambda x, vn=volk_name: self.show_talent_search_dialog(x, vn),
                disabled=not is_active
            )
            
            row_layout.add_widget(talent_label)
            row_layout.add_widget(talent_button)

        # Freies Attribut (Menschen in Savage Pathfinder, Halbelfen)
        if ((volk_name == "Mensch" and self._ist_savage_pathfinder_aktiv()) or
            volk_name == "Halbelf" or
            (hasattr(volk, 'has_wahlmoeglichkeit') and volk.has_wahlmoeglichkeit('freies_attribut'))):
            
            attribut_text = auswahl.get('attribut', DEFAULT_ATTRIBUT_TEXT)
            attribut_label = MDLabel(
                text=attribut_text,
                size_hint_x=None,
                width=ATTRIBUT_LABEL_WIDTH
            )
            
            attribut_button = MDIconButton(
                icon="menu-down",
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                on_release=lambda x, vn=volk_name: self.show_attribut_search_dialog(x, vn),
                disabled=not is_active
            )
            
            row_layout.add_widget(attribut_label)
            row_layout.add_widget(attribut_button)

        # Freie verstandsbasierte Fertigkeit (Gnome)
        if (volk_name == "Gnom" or
            (hasattr(volk, 'has_wahlmoeglichkeit') and volk.has_wahlmoeglichkeit('freie_verstandsfertigkeit'))):
            
            fertigkeit_text = auswahl.get('fertigkeit', DEFAULT_FERTIGKEIT_TEXT)
            fertigkeit_label = MDLabel(
                text=fertigkeit_text,
                size_hint_x=None,
                width=FERTIGKEIT_LABEL_WIDTH
            )
            
            fertigkeit_button = MDIconButton(
                icon="menu-down",
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                on_release=lambda x, vn=volk_name: self.show_fertigkeit_search_dialog(x, vn),
                disabled=not is_active
            )
            
            row_layout.add_widget(fertigkeit_label)
            row_layout.add_widget(fertigkeit_button)

    def _add_volk_details(self, container, volk):
        """Fügt Detailinformationen für ein Volk zum Container hinzu."""
        detail_categories = [
            ('Handicaps', volk.handicaps),
            ('Talente', volk.talente),
            ('Besonderheiten', volk.besonderheiten)
        ]
        
        for category, items in detail_categories:
            if items:
                self._add_detail_items(container, items)

    def _add_detail_items(self, container, items):
        """Fügt Detaileinträge zum Container hinzu."""
        for item in items:
            detail_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=INFO_ROW_HEIGHT,
                spacing=5,
                padding=(PADDING_LEFT, 0)
            )

            detail_label = MDLabel(
                text=item,
                halign='left',
                theme_text_color="Secondary",
                size_hint_x=None,
                width=1000
            )

            detail_row.add_widget(detail_label)
            container.add_widget(detail_row)

    def _remove_volk_auswahl(self, volk_name):
        """Entfernt alle Auswahlen für ein bestimmtes Volk."""
        if volk_name not in self.voelker_auswahlen:
            return
            
        charakter = self.controller.charakter
        auswahl = self.voelker_auswahlen[volk_name]
        
        # Talent entfernen
        if 'talent' in auswahl:
            talent_name = auswahl['talent']
            if talent_name in charakter.selected_talente:
                charakter.selected_talente.remove(talent_name)
                if talent_name in charakter.talente:
                    charakter.talente[talent_name].ausgewaehlt = False
                Logger.info(f"Freies Talent '{talent_name}' von '{volk_name}' entfernt.")
        
        # Attribut zurücksetzen
        if 'attribut' in auswahl:
            attribut_name = auswahl['attribut']
            if attribut_name in charakter.attribute:
                attribut = charakter.attribute[attribut_name]
                if attribut.wert == 6 and attribut.modifier == 0:
                    attribut.wuerfel.value = 4
                    Logger.info(f"Attribut '{attribut_name}' von '{volk_name}' auf W4 zurückgesetzt.")
        
        # Fertigkeit zurücksetzen
        if 'fertigkeit' in auswahl:
            fertigkeit_name = auswahl['fertigkeit']
            if fertigkeit_name in charakter.fertigkeiten:
                fertigkeit = charakter.fertigkeiten[fertigkeit_name]
                fertigkeit.wuerfel.modifier = -2  # Zurück auf W4-2
                Logger.info(f"Fertigkeit '{fertigkeit_name}' von '{volk_name}' auf W4-2 zurückgesetzt.")
        
        # Auswahl aus Dictionary entfernen
        del self.voelker_auswahlen[volk_name]

    def _on_checkbox_active(self, instance, value, selected_volk_name):
        """Ereignishandler für Checkbox-Änderungen."""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return
            
        charakter = self.controller.charakter
        
        # Verhindern, dass alle Völker abgewählt werden
        if not value:
            aktive_voelker = [k for k, v in charakter.voelker_selected.items() if v]
            if len(aktive_voelker) <= 1 and selected_volk_name in aktive_voelker:
                Logger.debug(f"Abwählen des letzten Volks '{selected_volk_name}' verhindert")
                Clock.schedule_once(lambda dt: self.aktualisiere_ui(), 0.1)
                return
        
        if value:
            # Entferne Auswahlen aller anderen Völker
            for volk_name in list(self.voelker_auswahlen.keys()):
                if volk_name != selected_volk_name:
                    self._remove_volk_auswahl(volk_name)
            
            # Alle Völker deaktivieren
            for volk_name in charakter.voelker_selected:
                charakter.voelker_selected[volk_name] = False
                if volk_name in charakter.voelker:
                    charakter.voelker[volk_name].ausgewaehlt = False
            
            # Das ausgewählte Volk aktivieren
            charakter.voelker_selected[selected_volk_name] = True
            if selected_volk_name in charakter.voelker:
                charakter.voelker[selected_volk_name].ausgewaehlt = True
                
                # Völker-Effekte anwenden
                volk = charakter.voelker[selected_volk_name]
                if hasattr(volk, 'apply_effects_to_charakter'):
                    volk.apply_effects_to_charakter(charakter)
                    
        else:
            # Auswahlen für das abgewählte Volk entfernen
            self._remove_volk_auswahl(selected_volk_name)
            
            # Das Volk deaktivieren
            charakter.voelker_selected[selected_volk_name] = False
            if selected_volk_name in charakter.voelker:
                charakter.voelker[selected_volk_name].ausgewaehlt = False
                
                # Völker-Effekte entfernen
                volk = charakter.voelker[selected_volk_name]
                if hasattr(volk, 'remove_effects_from_charakter'):
                    volk.remove_effects_from_charakter(charakter)
                
            # Mensch als Standard setzen
            charakter.voelker_selected["Mensch"] = True
            if "Mensch" in charakter.voelker:
                charakter.voelker["Mensch"].ausgewaehlt = True
        
        # Event auslösen und UI aktualisieren
        charakter.berechne_abgeleitete_werte()
        charakter.dispatch('on_charakter_change')
        
        Logger.info(f"Volk '{selected_volk_name}' gesetzt auf {value}")
        Clock.schedule_once(lambda dt: self.aktualisiere_ui(), 0.1)