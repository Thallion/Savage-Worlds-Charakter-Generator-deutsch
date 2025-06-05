# views/voelker_view.py
"""
View-Komponente für Völker nach dem MVC-Pattern.
Stellt die Benutzerschnittstelle zur Anzeige und Verwaltung von Völkern bereit.
ERWEITERT: Mit Savage Pathfinder Attribut-Auswahl für Menschen
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
from kivy.properties import ObjectProperty, StringProperty
from kivy.metrics import dp
import logging

# Logger konfigurieren
Logger = logging.getLogger(__name__)

# Konstanten für bessere Lesbarkeit und Wartbarkeit
DEFAULT_TALENT_TEXT = 'Wähle ein freies Talent'
DEFAULT_ATTRIBUT_TEXT = 'Wähle ein Attribut'
DEFAULT_VOLK = 'Mensch'
NO_TALENT_AVAILABLE_TEXT = 'Keine freien Talente verfügbar'
NO_ATTRIBUT_AVAILABLE_TEXT = 'Keine Attribute verfügbar'
CHECKBOX_WIDTH = 50
VOLK_LABEL_WIDTH = 250  # Reduziert, um Platz für Attribut-Auswahl zu schaffen
TALENT_LABEL_WIDTH = dp(180)  # Reduziert
ATTRIBUT_LABEL_WIDTH = dp(180)  # Neu hinzugefügt
ROW_HEIGHT = 40
INFO_ROW_HEIGHT = 25
PADDING_LEFT = 40

# KV-String - könnte später in eine separate Datei ausgelagert werden
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
    Hauptkomponente der View im MVC-Pattern.
    ERWEITERT: Mit Savage Pathfinder Attribut-Auswahl
    """
    controller = ObjectProperty()
    aktuelles_talent = StringProperty(DEFAULT_TALENT_TEXT)
    aktuelles_attribut = StringProperty(DEFAULT_ATTRIBUT_TEXT)
    mensch_freies_talent = StringProperty("")  # Property für das freie Talent des Menschen
    mensch_erhoehtes_attribut = StringProperty("")  # Property für das erhöhte Attribut des Menschen

    def __init__(self, **kwargs):
        """Initialisiert das VoelkerWidget und setzt Grundkonfiguration."""
        super().__init__(**kwargs)
        self._initialize_controller()
        self.dropdown_menu = None
        self.voraussetzungs_dialog = None
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
        """
        Gibt eine alphabetisch sortierte Liste von freien Talenten zurück.
        Filtert bereits ausgewählte Talente heraus.
        
        Returns:
            list: Liste der verfügbaren Talente
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return [NO_TALENT_AVAILABLE_TEXT]
                
        # Aktive Talente abrufen und bereits ausgewählte ausfiltern
        frei_talente = []
        for name, talent in self.controller.charakter.talente.items():
            if talent.aktiv and not talent.ausgewaehlt:
                frei_talente.append(name)
        
        # Alphabetisch sortieren
        frei_talente.sort()
        
        if not frei_talente:
            frei_talente = [NO_TALENT_AVAILABLE_TEXT]
            
        return frei_talente

    def _get_verfuegbare_attribute(self):
        """
        Gibt eine Liste der verfügbaren Attribute für die Erhöhung zurück.
        Alle Standard-Attribute können von W4 auf W6 erhöht werden.
        
        Returns:
            list: Liste der verfügbaren Attribute
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return [NO_ATTRIBUT_AVAILABLE_TEXT]
        
        # Standard-Attribute für Savage Worlds
        standard_attribute = [
            "Stärke", 
            "Geschicklichkeit", 
            "Konstitution", 
            "Verstand", 
            "Willenskraft"
        ]
        
        # Prüfen, welche Attribute auf W4 stehen und erhöht werden können
        verfuegbare_attribute = []
        charakter = self.controller.charakter
        
        for attribut_name in standard_attribute:
            if attribut_name in charakter.attribute:
                attribut = charakter.attribute[attribut_name]
                # Nur Attribute mit W4 können auf W6 erhöht werden
                if attribut.wert == 4 and attribut.modifier == 0:
                    verfuegbare_attribute.append(attribut_name)
        
        if not verfuegbare_attribute:
            verfuegbare_attribute = [NO_ATTRIBUT_AVAILABLE_TEXT]
        
        return verfuegbare_attribute

    def _ist_savage_pathfinder_aktiv(self):
        """
        Prüft, ob das aktuelle Setting Savage Pathfinder ist.
        
        Returns:
            bool: True wenn Savage Pathfinder aktiv ist
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            return False
        
        try:
            return self.controller.charakter.ist_savage_pathfinder_setting()
        except Exception as e:
            Logger.error(f"Fehler bei Savage Pathfinder-Prüfung: {e}")
            return False

    def show_talent_search_dialog(self, button):
        """
        Zeigt einen Dialog mit Suchfunktion für die Talentauswahl an.
        
        Args:
            button: Button, der das Menü aufruft
        """
        # Dialog-Content erstellen
        content = MDBoxLayout(
            orientation='vertical', 
            size_hint_y=None,
            height="400dp",
            spacing="12dp",
            padding="24dp"
        )
        
        # Suchfeld erstellen
        search_field = MDTextField(
            mode="outlined",
            children=[
                MDTextFieldHintText(text="Talent suchen...")
            ]
        )
        content.add_widget(search_field)
        
        # ScrollView für die Talentliste erstellen
        scroll = MDScrollView(
            size_hint=(1, None),
            height="300dp"
        )
        
        # Liste für Talente erstellen
        talent_list = MDList()
        scroll.add_widget(talent_list)
        content.add_widget(scroll)
        
        # Talente holen
        freie_talente = self._get_freie_talente()
        all_talents = freie_talente.copy()  # Für die Suche
        
        # Dialog erstellen
        dialog = MDDialog()
        dialog.add_widget(MDDialogHeadlineText(text="Talent auswählen"))
        dialog.add_widget(MDDialogContentContainer(
            content,
            orientation="vertical",
        ))
        dialog.add_widget(MDDialogButtonContainer(
            MDButton(
                style="text",
                on_release=lambda x: dialog.dismiss(),
                children=[
                    MDButtonText(text="Abbrechen")
                ]
            ),
            spacing="8dp",
        ))
        
        # Funktion zum Hinzufügen eines Talents zur Liste
        def add_talent_to_list(talent_name):
            item = MDListItem(
                on_release=lambda x: select_talent(talent_name)
            )
            item.add_widget(MDListItemHeadlineText(
                text=talent_name
            ))
            talent_list.add_widget(item)
        
        # Funktion zum Auswählen eines Talents
        def select_talent(talent_name):
            if talent_name != NO_TALENT_AVAILABLE_TEXT and talent_name != "Keine Treffer gefunden":
                self._on_talent_select(talent_name)
            dialog.dismiss()
        
        # Funktion zum Filtern der Talente basierend auf der Sucheingabe
        def filter_talents(instance, value):
            talent_list.clear_widgets()
            search_text = value.lower().strip()
            
            filtered_talents = []
            if search_text:
                # Filtern nach Suchtext
                filtered_talents = [t for t in all_talents if search_text in t.lower()]
            else:
                # Ohne Suchtext alle anzeigen
                filtered_talents = all_talents
            
            # Sortierte Ergebnisse anzeigen
            filtered_talents.sort()
            
            if filtered_talents:
                for talent in filtered_talents:
                    add_talent_to_list(talent)
            else:
                # Wenn keine Ergebnisse gefunden wurden
                add_talent_to_list("Keine Treffer gefunden")
        
        # Binding für Texteingabe
        search_field.bind(text=filter_talents)
        
        # Initial alle Talente anzeigen
        for talent in freie_talente:
            add_talent_to_list(talent)
        
        dialog.open()

    def show_attribut_search_dialog(self, button):
        """
        Zeigt einen Dialog für die Attributauswahl an.
        
        Args:
            button: Button, der das Menü aufruft
        """
        # Dialog-Content erstellen
        content = MDBoxLayout(
            orientation='vertical', 
            size_hint_y=None,
            height="300dp",
            spacing="12dp",
            padding="24dp"
        )
        
        # ScrollView für die Attributliste erstellen
        scroll = MDScrollView(
            size_hint=(1, None),
            height="250dp"
        )
        
        # Liste für Attribute erstellen
        attribut_list = MDList()
        scroll.add_widget(attribut_list)
        content.add_widget(scroll)
        
        # Attribute holen
        verfuegbare_attribute = self._get_verfuegbare_attribute()
        
        # Dialog erstellen
        dialog = MDDialog()
        dialog.add_widget(MDDialogHeadlineText(text="Attribut auswählen (W4 → W6)"))
        dialog.add_widget(MDDialogContentContainer(
            content,
            orientation="vertical",
        ))
        dialog.add_widget(MDDialogButtonContainer(
            MDButton(
                style="text",
                on_release=lambda x: dialog.dismiss(),
                children=[
                    MDButtonText(text="Abbrechen")
                ]
            ),
            spacing="8dp",
        ))
        
        # Funktion zum Hinzufügen eines Attributs zur Liste
        def add_attribut_to_list(attribut_name):
            item = MDListItem(
                on_release=lambda x: select_attribut(attribut_name)
            )
            item.add_widget(MDListItemHeadlineText(
                text=attribut_name
            ))
            attribut_list.add_widget(item)
        
        # Funktion zum Auswählen eines Attributs
        def select_attribut(attribut_name):
            if attribut_name != NO_ATTRIBUT_AVAILABLE_TEXT:
                self._on_attribut_select(attribut_name)
            dialog.dismiss()
        
        # Alle verfügbaren Attribute anzeigen
        for attribut in verfuegbare_attribute:
            add_attribut_to_list(attribut)
        
        dialog.open()

    def _show_voraussetzungen_dialog(self, talent_name, fehlermeldungen):
        """
        Zeigt einen Dialog an, der vor der Auswahl eines Talents warnt, 
        dessen Voraussetzungen nicht erfüllt sind.
        
        Args:
            talent_name: Name des Talents
            fehlermeldungen: Liste von Fehlermeldungen
        """
        # Dialog-Inhalt erstellen
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            padding="12dp",
            size_hint_y=None,
            height="200dp"
        )
        
        # Warnungstext erstellen
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
        
        # MDDialog mit korrekter KivyMD 2.0.1 Syntax erstellen
        self.voraussetzungs_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Voraussetzungen nicht erfüllt",
            ),
            MDDialogContentContainer(
                content,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self._dismiss_voraussetzungs_dialog(),
                ),
                MDButton(
                    MDButtonText(text="Trotzdem auswählen"),
                    style="text",
                    on_release=lambda x: self._confirm_talent_selection(talent_name),
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
    
    def _confirm_talent_selection(self, talent_name):
        """
        Bestätigt die Auswahl eines Talents, auch wenn die Voraussetzungen nicht erfüllt sind.
        
        Args:
            talent_name: Name des ausgewählten Talents
        """
        self._dismiss_voraussetzungs_dialog()
        
        charakter = self.controller.charakter
        # Wichtig: Flag setzen, um Voraussetzungen zu ignorieren
        charakter.ignore_voraussetzungen = True
        
        # Erneut versuchen, das freie Talent auszuwählen
        # Verwende waehle_freies_talent statt waehle_talent, mit ignore_voraussetzungen=True
        if hasattr(charakter, 'waehle_freies_talent'):
            # Direkte Methode im Charakter
            erfolg = charakter.waehle_freies_talent(talent_name, ignore_voraussetzungen=True)
        elif hasattr(self.controller, 'waehle_freies_talent'):
            # Methode im Controller
            erfolg = self.controller.waehle_freies_talent(talent_name, ignore_voraussetzungen=True)
        else:
            # Fallback auf talent_funktionen
            from functions.talent_funktionen import waehle_freies_talent
            erfolg = waehle_freies_talent(charakter, talent_name, ignore_voraussetzungen=True)
        
        if erfolg:
            self.aktuelles_talent = talent_name
            self.mensch_freies_talent = talent_name
            Logger.info(f"Freies Talent '{talent_name}' für Mensch ausgewählt, trotz nicht erfüllter Voraussetzungen.")
            charakter.dispatch('on_charakter_change')

    def _on_talent_select(self, talent_name):
        """
        Wird aufgerufen, wenn ein Talent aus dem Dialog ausgewählt wird.
        Speichert das ausgewählte Talent als freies Talent des Menschen.
        
        Args:
            talent_name: Name des ausgewählten Talents
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return
                
        if talent_name == NO_TALENT_AVAILABLE_TEXT:
            Logger.info("Keine freien Talente ausgewählt.")
            return

        charakter = self.controller.charakter
        if hasattr(charakter, 'selected_talente') and talent_name in charakter.selected_talente:
            Logger.warning(f"Talent '{talent_name}' ist bereits ausgewählt.")
            return

        # Freies Talent für Menschen auswählen - ohne Kosten
        # Verwende waehle_freies_talent statt waehle_talent
        if hasattr(charakter, 'waehle_freies_talent'):
            # Direkte Methode im Charakter
            result = charakter.waehle_freies_talent(talent_name)
        elif hasattr(self.controller, 'waehle_freies_talent'):
            # Methode im Controller
            result = self.controller.waehle_freies_talent(talent_name)
        else:
            # Fallback auf talent_funktionen
            from functions.talent_funktionen import waehle_freies_talent
            result = waehle_freies_talent(charakter, talent_name)
        
        # Prüfen, ob Voraussetzungen bestätigt werden müssen
        if result == "needs_voraussetzungen_confirmation":
            # Dialog anzeigen mit den Fehlermeldungen
            fehlermeldungen = charakter.temp_voraussetzungs_fehler
            self._show_voraussetzungen_dialog(talent_name, fehlermeldungen)
            return
        
        # Bei Erfolg das Talent merken
        if result is True:
            self.aktuelles_talent = talent_name
            self.mensch_freies_talent = talent_name
            Logger.info(f"Freies Talent '{talent_name}' für Mensch ausgewählt.")
            charakter.dispatch('on_charakter_change')

    def _on_attribut_select(self, attribut_name):
        """
        Wird aufgerufen, wenn ein Attribut aus dem Dialog ausgewählt wird.
        Erhöht das ausgewählte Attribut von W4 auf W6.
        
        Args:
            attribut_name: Name des ausgewählten Attributs
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return
                
        if attribut_name == NO_ATTRIBUT_AVAILABLE_TEXT:
            Logger.info("Kein Attribut ausgewählt.")
            return

        charakter = self.controller.charakter
        
        # Prüfen, ob das Attribut tatsächlich auf W4 steht
        if attribut_name in charakter.attribute:
            attribut = charakter.attribute[attribut_name]
            if attribut.wert == 4 and attribut.modifier == 0:
                # Attribut von W4 auf W6 erhöhen
                attribut.wuerfel.value = 6
                
                # Aktuelles Attribut speichern
                self.aktuelles_attribut = attribut_name
                self.mensch_erhoehtes_attribut = attribut_name
                
                Logger.info(f"Attribut '{attribut_name}' für Mensch von W4 auf W6 erhöht.")
                charakter.berechne_abgeleitete_werte()
                charakter.dispatch('on_charakter_change')
            else:
                Logger.warning(f"Attribut '{attribut_name}' steht nicht auf W4+0, aktuelle Werte: W{attribut.wert}+{attribut.modifier}")
        else:
            Logger.error(f"Attribut '{attribut_name}' nicht gefunden.")

    def aktualisiere_ui(self, *args):
        """
        Aktualisiert die UI basierend auf dem aktuellen Zustand des Charakters.
        Wird bei Änderungen am Charakter aufgerufen.
        """
        Logger.debug("VoelkerWidget: aktualisiere_ui aufgerufen")
        
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return
            
        try:
            container = self.ids.voelker_content_container
            container.clear_widgets()

            # Synchronisiere voelker_selected mit den verfügbaren Völkern
            charakter = self.controller.charakter
            
            # Debug-Ausgabe für Völker
            Logger.debug(f"Völker im Charakter: {list(charakter.voelker.keys())}")
            Logger.debug(f"Ausgewählte Völker: {charakter.voelker_selected}")
            
            # Sicherstellen, dass "Mensch" existiert
            if "Mensch" not in charakter.voelker:
                Logger.warning("ACHTUNG: Volk 'Mensch' fehlt in der Völkerliste des Charakters!")
                # Mensch temporär hinzufügen
                from models.volk import Volk
                mensch_volk = Volk(
                    name="Mensch",
                    handicaps=[],
                    talente=["Freies Talent"],
                    besonderheiten=["Menschen erhalten ein freies Talent ihrer Wahl"]
                )
                charakter.voelker["Mensch"] = mensch_volk
                Logger.info("Volk 'Mensch' wurde temporär hinzugefügt")
            
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
        """
        Fügt eine Zeile für ein Volk zum Container hinzu.
        
        Args:
            container: Container, zu dem die Zeile hinzugefügt wird
            volk_name: Name des Volks
            volk: Volk-Objekt
        """
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

        # Checkbox für die Auswahl - WICHTIG: Zustand aus voelker_selected nehmen, nicht aus volk.ausgewaehlt
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

        # Spezielle UI-Elemente für Menschen
        if volk_name == DEFAULT_VOLK:
            self._add_mensch_specific_ui(row_layout)

        container.add_widget(row_layout)

    def _add_mensch_specific_ui(self, row_layout):
        """
        Fügt spezielle UI-Elemente für Menschen hinzu.
        ERWEITERT: Mit Attribut-Auswahl für Savage Pathfinder
        
        Args:
            row_layout: Layout, zu dem die Elemente hinzugefügt werden
        """
        # Talent-Label
        talent_label = MDLabel(
            text=self.aktuelles_talent,
            size_hint_x=None,
            width=TALENT_LABEL_WIDTH
        )

        # Talent-Auswahlbutton
        talent_button = MDIconButton(
            icon="menu-down",
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            on_release=self.show_talent_search_dialog
        )

        row_layout.add_widget(talent_label)
        row_layout.add_widget(talent_button)

        # Nur für Savage Pathfinder: Attribut-Auswahl hinzufügen
        if self._ist_savage_pathfinder_aktiv():
            # Attribut-Label
            attribut_label = MDLabel(
                text=self.aktuelles_attribut,
                size_hint_x=None,
                width=ATTRIBUT_LABEL_WIDTH
            )

            # Attribut-Auswahlbutton
            attribut_button = MDIconButton(
                icon="menu-down",
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                on_release=self.show_attribut_search_dialog
            )

            row_layout.add_widget(attribut_label)
            row_layout.add_widget(attribut_button)

    def _add_volk_details(self, container, volk):
        """
        Fügt Detailinformationen für ein Volk zum Container hinzu.
        
        Args:
            container: Container, zu dem die Details hinzugefügt werden
            volk: Volk-Objekt
        """
        # Hinzufügen von Zusatzinformationen (Handicaps, Talente, Besonderheiten)
        detail_categories = [
            ('Handicaps', volk.handicaps),
            ('Talente', volk.talente),
            ('Besonderheiten', volk.besonderheiten)
        ]
        
        for category, items in detail_categories:
            if items:
                self._add_detail_items(container, items)

    def _add_detail_items(self, container, items):
        """
        Fügt Detaileinträge zum Container hinzu.
        
        Args:
            container: Container, zu dem die Einträge hinzugefügt werden
            items: Liste der Einträge
        """
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

    def _remove_mensch_talent(self):
        """Entfernt das ausgewählte Talent des Menschen."""
        if self.mensch_freies_talent:
            # Talent entfernen
            self.controller.entferne_talent(self.mensch_freies_talent)
            Logger.info(f"Freies Talent '{self.mensch_freies_talent}' von 'Mensch' entfernt.")
            self.mensch_freies_talent = ""  # Zurücksetzen
            self.aktuelles_talent = DEFAULT_TALENT_TEXT  # Label zurücksetzen

    def _remove_mensch_attribut(self):
        """Setzt das erhöhte Attribut des Menschen zurück."""
        if self.mensch_erhoehtes_attribut:
            charakter = self.controller.charakter
            if self.mensch_erhoehtes_attribut in charakter.attribute:
                attribut = charakter.attribute[self.mensch_erhoehtes_attribut]
                # Attribut von W6 zurück auf W4 setzen
                if attribut.wert == 6 and attribut.modifier == 0:
                    attribut.wuerfel.value = 4
                    Logger.info(f"Attribut '{self.mensch_erhoehtes_attribut}' von 'Mensch' von W6 auf W4 zurückgesetzt.")
                    charakter.berechne_abgeleitete_werte()
            
            self.mensch_erhoehtes_attribut = ""  # Zurücksetzen
            self.aktuelles_attribut = DEFAULT_ATTRIBUT_TEXT  # Label zurücksetzen

    def _on_checkbox_active(self, instance, value, selected_volk_name):
        """
        Ereignishandler für Checkbox-Änderungen.
        
        Args:
            instance: Checkbox-Instance, die das Ereignis ausgelöst hat
            value: Neuer Wert der Checkbox (True/False)
            selected_volk_name: Name des Volks, das mit der Checkbox verknüpft ist
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return
            
        charakter = self.controller.charakter
        
        # Hier liegt das Problem: Wir müssen das Umschalten verhindern, um UI-Rückkopplungen zu vermeiden
        # Nur Ereignisse verarbeiten, die eine Aktivierung sind
        if not value:
            # Verhindern, dass alle Völker abgewählt werden
            aktive_voelker = [k for k, v in charakter.voelker_selected.items() if v]
            if len(aktive_voelker) <= 1 and selected_volk_name in aktive_voelker:
                # Wenn der Benutzer versucht, das letzte aktive Volk abzuwählen, abbrechen
                Logger.debug(f"Abwählen des letzten Volks '{selected_volk_name}' verhindert")
                
                # UI neu laden, um den Checkbox-Zustand zurückzusetzen
                Clock.schedule_once(lambda dt: self.aktualisiere_ui(), 0.1)
                return
        
        # Wenn ein Volk aktiviert wird, alle anderen deaktivieren
        if value:
            # Wenn ein anderes Volk als "Mensch" aktiviert wird, das freie Talent und Attribut von "Mensch" entfernen
            if selected_volk_name != DEFAULT_VOLK and charakter.voelker_selected.get(DEFAULT_VOLK, False):
                self._remove_mensch_talent()
                if self._ist_savage_pathfinder_aktiv():
                    self._remove_mensch_attribut()
            
            # Alle Völker in beiden Dictionaries deaktivieren
            for volk_name in charakter.voelker_selected:
                charakter.voelker_selected[volk_name] = False
                if volk_name in charakter.voelker:
                    charakter.voelker[volk_name].ausgewaehlt = False
            
            # Das ausgewählte Volk aktivieren
            charakter.voelker_selected[selected_volk_name] = True
            if selected_volk_name in charakter.voelker:
                charakter.voelker[selected_volk_name].ausgewaehlt = True
        else:
            # Wenn "Mensch" abgewählt wird, das freie Talent und Attribut entfernen
            if selected_volk_name == DEFAULT_VOLK:
                self._remove_mensch_talent()
                if self._ist_savage_pathfinder_aktiv():
                    self._remove_mensch_attribut()
            
            # Das Volk deaktivieren
            charakter.voelker_selected[selected_volk_name] = False
            if selected_volk_name in charakter.voelker:
                charakter.voelker[selected_volk_name].ausgewaehlt = False
                
            # Mensch als Standard setzen
            charakter.voelker_selected["Mensch"] = True
            if "Mensch" in charakter.voelker:
                charakter.voelker["Mensch"].ausgewaehlt = True
        
        # Event auslösen, um andere Module zu informieren
        charakter.dispatch('on_charakter_change')
        
        # UI aktualisieren
        Logger.info(f"Volk '{selected_volk_name}' gesetzt auf {value}")
        # Verzögerte UI-Aktualisierung, um Rückkopplungseffekte zu vermeiden
        Clock.schedule_once(lambda dt: self.aktualisiere_ui(), 0.1)