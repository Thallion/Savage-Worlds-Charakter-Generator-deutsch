# maechte_view.py
"""
View-Komponente für Mächte nach dem MVC-Pattern.
Stellt die Benutzeroberfläche zur Anzeige und Verwaltung von Mächten bereit.
"""

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.button import MDIconButton
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp

# Konstanten für bessere Lesbarkeit und Wartbarkeit
DEFAULT_SORT_OPTION = 'Name'
DEFAULT_SORT_ORDER = 'asc'
DEFAULT_ROW_HEIGHT = dp(80)
DARK_EVEN_COLOR = [0.2, 0.2, 0.2, 1]
DARK_ODD_COLOR = [0.15, 0.15, 0.15, 1]
LIGHT_EVEN_COLOR = [1, 1, 1, 1]
LIGHT_ODD_COLOR = [0.85, 0.85, 0.85, 1]
SELECTED_LINE_COLOR = [1, 0.65, 0, 1]
UNSELECTED_LINE_COLOR = [0, 0, 0, 0]


class MaechteTooltip(MDTooltip):
    """Basis-Klasse für Tooltips in der Mächte-View"""
    tooltip_text = StringProperty()


class TooltipIconButton(MaechteTooltip, MDIconButton):
    """Icon Button mit Tooltip Funktionalität"""
    icon = StringProperty()


# Bei der Factory registrieren
Factory.register('TooltipIconButton', TooltipIconButton)


# KV-String in eine Konstante - könnte später in eine separate Datei ausgelagert werden
KV_STRING = '''
<TooltipIconButton>
    MDTooltipPlain:
        text: root.tooltip_text

<MaechteWidget>:
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

        MDTextField:
            id: search_input
            hint_text: 'Suche...'
            size_hint_x: 1
            on_text: root.filter_maechte()
            
        # Checkbox für "Nur ausgewählte" hinzufügen
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_x: None
            width: dp(200)
            spacing: dp(5)
            
            MDCheckbox:
                id: only_selected_checkbox
                size_hint: None, None
                size: dp(40), dp(40)
                active: root.only_selected_items
                on_active: root.toggle_only_selected_items(self.active)
                pos_hint: {"center_y": .5}
                
            MDLabel:
                text: "Nur ausgewählte"
                size_hint_y: None
                height: dp(40)
                pos_hint: {"center_y": .5}

    MDLabel:
        text: 'Mächte'
        font_size: dp(24)
        size_hint_y: None
        height: dp(48)
        padding: [20, 10]

    MaechteRecycleView:
        id: recycleview
        viewclass: 'MachtItemRow'
        size_hint_y: 1
        
        RecycleBoxLayout:
            id: layout
            default_size: None, dp(80)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(5)
            padding: dp(20)

<MachtItemRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(80)
    md_bg_color: self._get_background_color()
    line_color: self._get_line_color()
    line_width: 2
    spacing: dp(10)
    padding: dp(10)

    MDLabel:
        text: root.macht_name
        font_size: dp(16)
        size_hint_x: 0.2
        halign: 'left'
        valign: 'middle'

    MDLabel:
        text: root.rang
        font_size: dp(16)
        size_hint_x: 0.05
        halign: 'left'
        valign: 'middle'

    MDLabel:
        text: f"MP: {root.machtpunkte} / RW: {root.reichweite} / Dauer: {root.dauer}"
        font_size: dp(14)
        size_hint_x: 0.15
        halign: 'left'
        valign: 'middle'

    MDFabButton:
        icon: "plus"
        style: "small"
        size_hint: None, None
        size: dp(40), dp(40)
        pos_hint: {"center_y": 0.5}
        on_release: root.waehle_macht()
        disabled: root.macht and root.macht.ausgewaehlt

    MDFabButton:
        icon: "minus"
        style: "small"
        size_hint: None, None
        size: dp(40), dp(40)
        pos_hint: {"center_y": 0.5}
        on_release: root.entferne_macht()
        disabled: not root.macht or not root.macht.ausgewaehlt

    MDLabel:
        text: root.beschreibung
        font_size: dp(14)
        size_hint_x: 0.6
        halign: 'left'
        valign: 'middle'
'''

Builder.load_string(KV_STRING)


class MaechteRecycleView(MDRecycleView):
    """
    RecycleView für die effiziente Darstellung der Mächte-Liste.
    Implementiert eine virtualisierte Listenansicht für bessere Performance.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        Logger.debug("MaechteRecycleView: Initialisiert")


class MachtItemRow(MDBoxLayout):
    """
    Einzelne Zeile in der Mächte-Liste.
    Repräsentiert eine einzelne Macht mit ihren Eigenschaften und Interaktionsmöglichkeiten.
    """
    index = NumericProperty(0)
    macht_name = StringProperty("")
    rang = StringProperty("")
    machtpunkte = NumericProperty(0)
    reichweite = StringProperty("")
    dauer = StringProperty("")
    effekt = StringProperty("")
    beschreibung = StringProperty("")
    macht = ObjectProperty(None)
    maechte_widget = ObjectProperty(None)

    def __init__(self, **kwargs):
        """Initialisiert die MachtItemRow und holt den Controller-Zugriff."""
        self._initialize_controller()
        super().__init__(**kwargs)
        self.bind(index=self.update_color)  # Wichtig: Farbaktualisierung bei Indexänderung

    def _initialize_controller(self):
        """Initialisiert die Verbindung zum Controller."""
        app = MDApp.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None
        
        if not self.controller:
            Logger.error("MachtItemRow: Controller nicht gefunden")

    def _refresh_ui(self):
        """Aktualisiert die UI nach einer Änderung am Macht-Status."""
        Logger.debug(f"MachtItemRow: Starte Widget-Aktualisierung")
        app = MDApp.get_running_app()
        widget = app.get_widget_by_tab_text('Mächte', 'maechte_widget')
        if widget:
            Logger.debug("MachtItemRow: MaechteWidget gefunden, führe refresh aus")
            Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)
        else:
            Logger.error("MachtItemRow: MaechteWidget nicht gefunden")

    def waehle_macht(self):
        """
        Wählt eine Macht aus.
        Delegiert die Aktion an den Controller und aktualisiert die Ansicht.
        """
        if not self.controller:
            Logger.error("MachtItemRow: Controller nicht gefunden")
            return

        success = self.controller.waehle_macht(self.macht_name)
        if success:
            Logger.debug(f"Macht '{self.macht_name}' ausgewählt.")
            if self.macht:
                self.macht.ausgewaehlt = True
                self.line_color = self._get_line_color()  # Umrandung aktualisieren
                self.canvas.ask_update()
            self._refresh_ui()
        else:
            Logger.warning(f"Auswahl der Macht '{self.macht_name}' fehlgeschlagen.")

    def entferne_macht(self):
        """
        Entfernt eine ausgewählte Macht.
        Delegiert die Aktion an den Controller und aktualisiert die Ansicht.
        """
        if not self.controller:
            Logger.error("MachtItemRow: Controller nicht gefunden")
            return
            
        success = self.controller.entferne_macht(self.macht_name)
        if success:
            Logger.debug(f"Macht '{self.macht_name}' entfernt.")
            if self.macht:
                self.macht.ausgewaehlt = False
                self.line_color = self._get_line_color()  # Umrandung aktualisieren
                self.canvas.ask_update()
            self._refresh_ui()
        else:
            Logger.warning(f"Entfernen der Macht '{self.macht_name}' fehlgeschlagen.")

    def update_color(self, *args):
        """Aktualisiert die Hintergrundfarbe bei Indexänderung."""
        # Die Canvas-Farben aktualisieren
        self.md_bg_color = self._get_background_color()
        self.line_color = self._get_line_color()

    def _get_background_color(self):
        """Berechnet die Hintergrundfarbe basierend auf Theme und Index."""
        is_dark = self.theme_cls.theme_style == "Dark"
        is_even = self.index % 2 == 0

        if is_dark:
            return DARK_EVEN_COLOR if is_even else DARK_ODD_COLOR
        else:
            return LIGHT_EVEN_COLOR if is_even else LIGHT_ODD_COLOR

    def _get_line_color(self):
        """Berechnet die Rahmenfarbe basierend auf dem Auswahlstatus der Macht."""
        if self.macht and self.macht.ausgewaehlt:
            return SELECTED_LINE_COLOR
        return UNSELECTED_LINE_COLOR


class MaechteWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Mächten.
    Hauptkomponente der View im MVC-Pattern.
    """
    current_sort_option = StringProperty(DEFAULT_SORT_OPTION)
    sort_order = StringProperty(DEFAULT_SORT_ORDER)
    only_selected_items = BooleanProperty(False)  # Neue Property für den Filter

    # Mapping für Ränge, um numerische Sortierung zu ermöglichen
    RANG_MAPPING = {
        'A': 1,    # Anfänger
        'F': 2,    # Fortgeschritten
        'V': 3,    # Veteran
        'H': 4,    # Heroisch
        'L': 5,    # Legendär
        'WC': 6    # Wild Card oder spezieller Rang
    }

    def __init__(self, **kwargs):
        """Initialisiert das MaechteWidget und setzt Grundkonfiguration."""
        super().__init__(**kwargs)
        self._initialize_controller()
        Clock.schedule_once(self.post_init, 0)

    def toggle_only_selected_items(self, value):
        """
        Schaltet den Filter für 'Nur ausgewählte Elemente' um.
        Event-Handler für die Checkbox.
        """
        self.only_selected_items = value
        self.filter_maechte()
        Logger.debug(f"Filter 'Nur ausgewählte Mächte' gesetzt auf: {value}")

    def _initialize_controller(self):
        """Initialisiert die Verbindung zum Controller."""
        app = MDApp.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None
        
        if not self.controller:
            Logger.error("MaechteWidget: Controller nicht gefunden")

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
        self.filter_maechte()

    def filter_maechte(self, *args):
        """
        Filtert und sortiert die Mächte.
        Event-Handler für Änderungen am Suchtext oder Filter.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("MaechteWidget: Controller oder Charakter nicht verfügbar")
            return
            
        search_term = self.ids.search_input.text.lower()

        # Mächte vom Modell abrufen
        alle_maechte = self.controller.charakter.maechte
        
        # Gefilterte Liste erstellen
        filtered_data = self._filter_maechte_data(alle_maechte, search_term)
        
        # Sortieren
        filtered_data = self._sort_maechte_data(filtered_data)
        
        # Index nach Sortierung aktualisieren
        for i, item in enumerate(filtered_data):
            item['index'] = i

        # An RecycleView übergeben
        self.ids.recycleview.data = filtered_data
        Logger.debug(f"Mächte gefiltert und sortiert: {len(filtered_data)} Einträge")

    def _filter_maechte_data(self, alle_maechte, search_term):
        """
        Filtert die Macht-Daten nach Suchbegriff und Auswahlstatus.
        """
        filtered_data = []
        
        Logger.debug(f"MaechteWidget: Filtere Mächte - Suchterm: {search_term}, Nur ausgewählte: {self.only_selected_items}")
        
        for macht in alle_maechte.values():
            # Filter für "Nur ausgewählte Elemente"
            if self.only_selected_items and not macht.ausgewaehlt:
                continue
                
            # Suchtext-Filter
            if search_term and not (search_term in macht.name.lower() or 
                                   search_term in macht.beschreibung.lower()):
                continue
                
            macht_data = {
                'viewclass': 'MachtItemRow',
                'macht_name': macht.name,
                'rang': macht.rang,
                'machtpunkte': macht.machtpunkte,
                'reichweite': macht.reichweite,
                'dauer': macht.dauer,
                'beschreibung': macht.beschreibung,
                'effekt': macht.effekt,
                'macht': macht,
                'maechte_widget': self
            }
            filtered_data.append(macht_data)
                
        return filtered_data

    def _sort_maechte_data(self, data):
        """
        Sortiert die Macht-Daten nach den aktuellen Sortierkriterien.
        Extrahiert die Sortierlogik aus filter_maechte.
        """
        reverse_order = (self.sort_order == 'desc')
        
        if self.current_sort_option == 'Name':
            data.sort(key=lambda x: x['macht_name'].lower(), reverse=reverse_order)
        elif self.current_sort_option == 'Rang':
            data.sort(key=lambda x: self.RANG_MAPPING.get(x['rang'], float('inf')), 
                     reverse=reverse_order)
            
        return data

    def post_init(self, dt):
        """
        Initialisierung nach dem Laden des Widgets.
        Wird einmalig durch Clock.schedule_once aufgerufen.
        """
        self.filter_maechte()
        Logger.debug("MaechteWidget: Post-Init abgeschlossen")

    def refresh_widget(self):
        """
        Leert das Widget und lädt die Daten neu.
        Wird aufgerufen, wenn sich die Mächte ändern.
        """
        # RecycleView leeren
        self.ids.recycleview.data = []
        
        # Neu filtern und anzeigen
        self.filter_maechte()
        Logger.debug("MaechteWidget: Widget aktualisiert")