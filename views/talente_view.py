# talente_view.py
"""
View-Komponente für Talente nach dem MVC-Pattern.
Stellt die Benutzeroberfläche zur Anzeige und Verwaltung von Talenten bereit.
"""

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.button import MDIconButton
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp

# Konstanten für bessere Lesbarkeit und Wartbarkeit
DEFAULT_SORT_OPTION = 'Name'
DEFAULT_SORT_ORDER = 'asc'
ALL_CATEGORIES_TEXT = 'Alle Kategorien'
DEFAULT_ROW_HEIGHT = dp(60)
DARK_EVEN_COLOR = [0.2, 0.2, 0.2, 1]
DARK_ODD_COLOR = [0.15, 0.15, 0.15, 1]
LIGHT_EVEN_COLOR = [1, 1, 1, 1]
LIGHT_ODD_COLOR = [0.85, 0.85, 0.85, 1]
SELECTED_LINE_COLOR = [1, 0.65, 0, 1]
UNSELECTED_LINE_COLOR = [0, 0, 0, 0]

# Rang-Mapping für Sortierung (als Konstante auf Modulebene)
RANG_MAPPING = {
    'A': 1,    # Anfänger
    'F': 2,    # Fortgeschritten
    'V': 3,    # Veteran
    'H': 4,    # Heroisch
    'L': 5,    # Legendär
    'WC': 6    # Wild Card oder spezieller Rang
}


class TalenteTooltip(MDTooltip):
    """Basis-Klasse für Tooltips in der Talente-View"""
    tooltip_text = StringProperty()


class TooltipIconButton(TalenteTooltip, MDIconButton):
    """Icon Button mit Tooltip Funktionalität"""
    icon = StringProperty()


# Bei der Factory registrieren
Factory.register('TooltipIconButton', TooltipIconButton)


# KV-String in eine Konstante - könnte später in eine separate Datei ausgelagert werden
KV_STRING = '''
<TooltipIconButton>
    MDTooltipPlain:
        text: root.tooltip_text

<TalenteWidget>:
    orientation: 'vertical'
    md_bg_color: self.theme_cls.backgroundColor  
    
    MDBoxLayout:
        size_hint_y: None
        height: 100
        padding: [20, 5]
        spacing: 5

        TooltipIconButton:
            id: sort_name_btn
            icon: "sort-alphabetical-ascending" if root.current_sort_option != 'Name' or root.sort_order == 'asc' else "sort-alphabetical-descending"
            tooltip_text: "Nach Namen sortieren" if root.current_sort_option != 'Name' or root.sort_order == 'asc' else "Namen absteigend sortieren"
            on_release: root.update_sort_option('Name')
            pos_hint: {"center_y": .5}

        TooltipIconButton:
            id: sort_rank_btn
            icon: "sort-ascending" if root.current_sort_option != 'Rang' or root.sort_order == 'asc' else "sort-descending"
            tooltip_text: "Nach Rang sortieren" if root.current_sort_option != 'Rang' or root.sort_order == 'asc' else "Rang absteigend sortieren"
            on_release: root.update_sort_option('Rang')
            pos_hint: {"center_y": .5}

        TooltipIconButton:
            id: sort_category_btn
            icon: "sort-reverse-variant" if root.current_sort_option != 'Kategorie' or root.sort_order == 'asc' else "sort-variant"
            tooltip_text: "Nach Kategorie sortieren" if root.current_sort_option != 'Kategorie' or root.sort_order == 'asc' else "Kategorie absteigend sortieren"
            on_release: root.update_sort_option('Kategorie')
            pos_hint: {"center_y": .5}

        MDTextField:
            id: search_input
            hint_text: 'Suche...'
            size_hint_x: 1
            on_text: root.filter_talente()

        TooltipIconButton:
            icon: "filter"
            tooltip_text: "Nach Kategorie filtern"
            on_release: root.open_category_menu()
            pos_hint: {"center_y": .5}

        MDLabel:
            id: category_label
            text: 'Alle Kategorien'
            size_hint_x: 1

    MDLabel:
        text: 'Talente'
        font_size: dp(24)
        size_hint_y: None
        height: dp(48)
        padding: [20, 10]

    TalenteRecycleView:
        id: recycleview
        viewclass: 'TalentItemRow'
        size_hint_y: 1
        
        RecycleBoxLayout:
            id: layout
            default_size: None, dp(60)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(5)
            padding: dp(20)

<TalentItemRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(60)
    md_bg_color: self._get_background_color()
    line_color: self._get_line_color()
    line_width: 2
    spacing: dp(10)
    padding: dp(10)

    MDLabel:
        text: root.talent_name
        font_size: dp(16)
        size_hint_x: 0.2
        halign: 'left'
        valign: 'middle'

    MDLabel:
        text: root.kategorie.capitalize() if root.kategorie else "Unbekannt"
        font_size: dp(16)
        size_hint_x: 0.1
        halign: 'left'
        valign: 'middle'

    MDLabel:
        text: root.rang
        font_size: dp(16)
        size_hint_x: 0.1
        halign: 'left'
        valign: 'middle'

    MDFabButton:
        icon: "plus"
        style: "small"
        size_hint: None, None
        size: dp(40), dp(40)
        pos_hint: {"center_y": 0.5}
        on_release: root.waehle_talent()
        disabled: root.ausgewaehlt

    MDFabButton:
        icon: "minus"
        style: "small"
        size_hint: None, None
        size: dp(40), dp(40)
        pos_hint: {"center_y": 0.5}
        on_release: root.entferne_talent()
        disabled: not root.ausgewaehlt

    MDLabel:
        text: root.beschreibung
        font_size: dp(16)
        size_hint_x: 0.5
        halign: 'left'
        valign: 'middle'
'''

Builder.load_string(KV_STRING)


class TalenteRecycleView(MDRecycleView):
    """
    RecycleView für die effiziente Darstellung der Talente-Liste.
    Implementiert eine virtualisierte Listenansicht für bessere Performance.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        Logger.debug("TalenteRecycleView: Initialisiert")


class TalentItemRow(MDBoxLayout):
    """
    Einzelne Zeile in der Talente-Liste.
    Repräsentiert ein einzelnes Talent mit seinen Eigenschaften und Interaktionsmöglichkeiten.
    """
    index = NumericProperty(0)
    name_key = StringProperty("")
    talent_name = StringProperty("")
    kategorie = StringProperty("")
    rang = StringProperty("")
    beschreibung = StringProperty("")
    ausgewaehlt = BooleanProperty(False)

    def __init__(self, **kwargs):
        """Initialisiert die TalentItemRow und bindet Property-Änderungen an entsprechende Handler."""
        super().__init__(**kwargs)
        self.bind(ausgewaehlt=self.on_ausgewaehlt_changed)

    def _get_controller(self):
        """Hilfsmethode, um auf den Controller zuzugreifen."""
        app = MDApp.get_running_app()
        return app.controller if hasattr(app, 'controller') else None

    def _refresh_ui(self):
        """Aktualisiert die UI nach einer Änderung am Talent-Status."""
        Logger.debug(f"TalentItemRow: Starte Widget-Aktualisierung")
        app = MDApp.get_running_app()
        widget = app.get_widget_by_tab_text('Talente', 'talente_widget')
        if widget:
            Logger.debug("TalentItemRow: TalenteWidget gefunden, führe refresh aus")
            Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)
        else:
            Logger.error("TalentItemRow: TalenteWidget nicht gefunden")

    def waehle_talent(self):
        """
        Wählt ein Talent aus.
        Delegiert die Aktion an den Controller und aktualisiert die Ansicht.
        """
        Logger.debug(f"TalentItemRow: Start waehle_talent für {self.talent_name}")
        controller = self._get_controller()
        if not controller:
            Logger.error("TalentItemRow: Controller nicht gefunden")
            return

        try:
            controller.waehle_talent(self.name_key)
            self.ausgewaehlt = True
            Logger.debug(f"TalentItemRow: {self.talent_name} erfolgreich ausgewählt")
            self._refresh_ui()
        except Exception as e:
            Logger.error(f"Fehler beim Auswählen des Talents: {str(e)}")

    def entferne_talent(self):
        """
        Entfernt ein ausgewähltes Talent.
        Delegiert die Aktion an den Controller und aktualisiert die Ansicht.
        """
        Logger.debug(f"TalentItemRow: Start entferne_talent für {self.talent_name}")
        controller = self._get_controller()
        if not controller:
            Logger.error("TalentItemRow: Controller nicht gefunden")
            return

        try:
            controller.entferne_talent(self.name_key)
            self.ausgewaehlt = False
            Logger.debug(f"TalentItemRow: {self.talent_name} erfolgreich entfernt")
            self._refresh_ui()
        except Exception as e:
            Logger.error(f"Fehler beim Entfernen des Talents: {str(e)}")

    def _get_background_color(self):
        """Berechnet die Hintergrundfarbe basierend auf Theme und Index."""
        is_dark = self.theme_cls.theme_style == "Dark"
        is_even = self.index % 2 == 0

        if is_dark:
            return DARK_EVEN_COLOR if is_even else DARK_ODD_COLOR
        else:
            return LIGHT_EVEN_COLOR if is_even else LIGHT_ODD_COLOR

    def _get_line_color(self):
        """Berechnet die Rahmenfarbe basierend auf dem Auswahlstatus."""
        return SELECTED_LINE_COLOR if self.ausgewaehlt else UNSELECTED_LINE_COLOR

    def on_ausgewaehlt_changed(self, instance, value):
        """Event-Handler für Änderungen am ausgewaehlt-Status."""
        Logger.debug(f"TalentItemRow: ausgewaehlt changed to {value} for {self.talent_name}")


class TalenteWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Talenten.
    Hauptkomponente der View im MVC-Pattern.
    """
    kategorien = ListProperty([])
    current_sort_option = StringProperty(DEFAULT_SORT_OPTION)
    sort_order = StringProperty(DEFAULT_SORT_ORDER)

    def __init__(self, **kwargs):
        """Initialisiert das TalenteWidget und setzt Grundkonfiguration."""
        super().__init__(**kwargs)
        self._initialize_controller()
        self.menu = None
        Clock.schedule_once(self.post_init, 0)

    def _initialize_controller(self):
        """Initialisiert die Verbindung zum Controller."""
        app = MDApp.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None
        
        if not self.controller:
            Logger.error("TalenteWidget: Controller nicht gefunden")

    def update_sort_option(self, option):
        """
        Aktualisiert die Sortieroptionen und -reihenfolge.
        Event-Handler für die Sortier-Buttons.
        """
        if self.current_sort_option == option:
            # Wenn die gleiche Option nochmal geklickt wird, Reihenfolge umkehren
            self.sort_order = 'desc' if self.sort_order == 'asc' else 'asc'
        else:
            # Bei neuer Option immer aufsteigend beginnen
            self.current_sort_option = option
            self.sort_order = 'asc'

        Logger.debug(f"Sortierung aktualisiert: {self.current_sort_option}, {self.sort_order}")
        self.filter_talente()

    def filter_talente(self, *args):
        """
        Filtert und sortiert die Talente.
        Event-Handler für Änderungen an Suchtext oder Kategorie.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("TalenteWidget: Controller oder Charakter nicht verfügbar")
            return
            
        search_term = self.ids.search_input.text.lower()
        selected_kategorie = self.ids.category_label.text.lower()

        # Talente vom Modell abrufen
        alle_talente = self.controller.charakter.talente
        
        # Gefilterte Liste erstellen
        filtered_data = self._filter_talente_data(
            alle_talente,
            search_term, 
            selected_kategorie
        )
        
        # Sortieren
        filtered_data = self._sort_talente_data(filtered_data)
        
        # Index nach Sortierung aktualisieren
        for i, item in enumerate(filtered_data):
            item['index'] = i

        # An RecycleView übergeben
        self.ids.recycleview.data = filtered_data
        Logger.debug(f"Talente gefiltert und sortiert: {len(filtered_data)} Einträge")

    def _filter_talente_data(self, alle_talente, search_term, selected_kategorie):
        """
        Filtert die Talent-Daten nach Suchbegriff und Kategorie.
        Extrahiert die Filterlogik aus filter_talente.
        """
        filtered_data = []
        
        for key, talent in alle_talente.items():
            # Kategorie-Filter
            if (selected_kategorie != ALL_CATEGORIES_TEXT.lower() and 
                (talent.kategorie is None or talent.kategorie.lower() != selected_kategorie)):
                continue
                
            # Suchtext-Filter
            if (search_term in talent.name.lower() or 
                search_term in talent.beschreibung.lower()):
                
                talent_data = {
                    'viewclass': 'TalentItemRow',
                    'name_key': key,
                    'talent_name': talent.name,
                    'kategorie': talent.kategorie,
                    'rang': talent.rang,
                    'beschreibung': talent.beschreibung,
                    'ausgewaehlt': talent.ausgewaehlt
                }
                filtered_data.append(talent_data)
                
        return filtered_data

    def _sort_talente_data(self, data):
        """
        Sortiert die Talent-Daten nach den aktuellen Sortierkriterien.
        Extrahiert die Sortierlogik aus filter_talente.
        """
        reverse_order = (self.sort_order == 'desc')
        
        # Sortieren nach dem ausgewählten Kriterium
        if self.current_sort_option == 'Name':
            data.sort(key=lambda x: x['talent_name'].lower(), reverse=reverse_order)
        elif self.current_sort_option == 'Rang':
            data.sort(key=lambda x: RANG_MAPPING.get(x['rang'], float('inf')), reverse=reverse_order)
        elif self.current_sort_option == 'Kategorie':
            data.sort(key=lambda x: (x['kategorie'] or '').lower(), reverse=reverse_order)
            
        return data

    def post_init(self, dt):
        """
        Initialisierung nach dem Laden des Widgets.
        Wird einmalig durch Clock.schedule_once aufgerufen.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("TalenteWidget: Controller oder Charakter nicht verfügbar")
            return
            
        alle_talente = self.controller.charakter.talente
        Logger.debug(f"TalenteWidget: Lade {len(alle_talente)} Talente")
        
        # Kategorien extrahieren und sortieren
        self._update_kategorien(alle_talente)
        
        # Talente filtern und anzeigen
        self.filter_talente()

    def _update_kategorien(self, talente_dict):
        """Aktualisiert die Liste der verfügbaren Talent-Kategorien."""
        self.kategorien = sorted(list(set(
            talent.kategorie for talent in talente_dict.values() 
            if talent.kategorie
        )))
        Logger.debug(f"TalenteWidget: Gefundene Kategorien: {self.kategorien}")

    def refresh_widget(self):
        """
        Leert das Widget und lädt die Daten neu.
        Wird aufgerufen, wenn sich die Talente ändern.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("TalenteWidget: Controller oder Charakter nicht verfügbar")
            return
            
        # RecycleView leeren
        self.ids.recycleview.data = []
        
        # Kategorien neu laden
        alle_talente = self.controller.charakter.talente
        self._update_kategorien(alle_talente)
        
        # Filter neu anwenden
        self.filter_talente()

    def open_category_menu(self):
        """
        Öffnet das Kategorie-Auswahlmenü.
        Event-Handler für den Kategorie-Filter-Button.
        """
        menu_items = [
            {
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_category(x),
            } for i in [ALL_CATEGORIES_TEXT] + self.kategorien
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.category_label,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def set_category(self, text):
        """
        Setzt die ausgewählte Kategorie und aktualisiert die Anzeige.
        Event-Handler für die Kategorie-Auswahl im Menü.
        """
        self.ids.category_label.text = text
        self.menu.dismiss()
        self.filter_talente()