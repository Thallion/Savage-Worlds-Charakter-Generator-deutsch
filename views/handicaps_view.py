# handicaps_view.py
"""
View-Komponente für Handicaps nach dem MVC-Pattern.
Stellt die Benutzerschnittstelle zur Anzeige und Verwaltung von Handicaps bereit.
"""

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton, MDFabButton, MDButtonText

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer
)

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp


# Konstanten für bessere Lesbarkeit und Wartbarkeit
DEFAULT_SORT_ORDER = 'name_asc'
ALL_CATEGORIES_TEXT = 'Alle Stufen'
RECYCLEVIEW_ITEM_HEIGHT = dp(60)
DARK_EVEN_COLOR = [0.2, 0.2, 0.2, 1]
DARK_ODD_COLOR = [0.15, 0.15, 0.15, 1]
LIGHT_EVEN_COLOR = [1, 1, 1, 1]
LIGHT_ODD_COLOR = [0.85, 0.85, 0.85, 1]
SELECTED_LINE_COLOR = [1, 0.65, 0, 1]
UNSELECTED_LINE_COLOR = [0, 0, 0, 0]


# KV-String - könnte in eine separate Datei ausgelagert werden
KV_STRING = '''
<HandicapsWidget>:
    orientation: 'vertical'
    md_bg_color: self.theme_cls.backgroundColor  
    
    MDBoxLayout:
        size_hint_y: None
        height: 100
        padding: [20, 5]
        spacing: 5

        MDIconButton:
            icon: "sort-alphabetical-ascending" if root.sort_order == 'name_asc' else "sort-alphabetical-descending"
            size_hint_y: 1
            on_release: root.toggle_sort_order()
            tooltip_text: "Namen aufsteigend sortieren" if root.sort_order != 'name_asc' else "Namen absteigend sortieren"

        MDTextField:
            id: search_input
            hint_text: 'Suche...'
            size_hint_x: 1
            on_text: root.filter_handicaps()

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

        MDIconButton:
            icon: "filter"
            size_hint_y: 1
            on_release: root.open_category_menu()
            tooltip_text: "Nach Stufe filtern"

        MDLabel:
            id: category_label
            text: 'Alle Stufen'
            size_hint_x: 1

    MDLabel:
        text: 'Handicaps'
        font_size: dp(24)
        size_hint_y: None
        height: dp(48)
        padding: [20, 10]

    HandicapsRecycleView:
        id: recycleview
        viewclass: 'HandicapItemRow'
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

<HandicapItemRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(60)
    md_bg_color: self._get_background_color()
    line_color: self._get_line_color()
    line_width: 2
    spacing: dp(10)
    padding: dp(10)

    MDLabel:
        text: root.handicap_name
        font_size: dp(16)
        size_hint_x: 0.2
        halign: 'left'
        valign: 'middle'

    MDLabel:
        text: root.stufe.capitalize() if root.stufe else "Unbekannt"
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
        on_release: root.waehle_handicap()
        disabled: root.ausgewaehlt

    MDFabButton:
        icon: "minus"
        style: "small"
        size_hint: None, None
        size: dp(40), dp(40)
        pos_hint: {"center_y": 0.5}
        on_release: root.entferne_handicap()
        disabled: not root.ausgewaehlt

    MDLabel:
        text: root.beschreibung
        font_size: dp(16)
        size_hint_x: 0.6
        halign: 'left'
        valign: 'middle'
'''

Builder.load_string(KV_STRING)


class HandicapsRecycleView(MDRecycleView):
    """
    RecycleView für die effiziente Darstellung der Handicap-Liste.
    Implementiert eine virtualisierte Listenansicht für bessere Performance.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        Logger.debug("HandicapsRecycleView: Initialisiert")


class HandicapItemRow(MDBoxLayout):
    """
    Einzelne Zeile in der Handicap-Liste.
    Repräsentiert ein einzelnes Handicap mit seinen Eigenschaften und Interaktionsmöglichkeiten.
    """
    index = NumericProperty(0)
    name_key = StringProperty("")
    handicap_name = StringProperty("")
    stufe = StringProperty("")
    beschreibung = StringProperty("")
    ausgewaehlt = BooleanProperty(False)

    def __init__(self, **kwargs):
        """Initialisiert die HandicapItemRow und bindet Property-Änderungen an entsprechende Handler."""
        super().__init__(**kwargs)
        self.bind(ausgewaehlt=self.on_ausgewaehlt_changed)
        self.bind(index=self.update_color)  # Wichtig: Farbaktualisierung bei Indexänderung

    def _get_controller(self):
        """Hilfsmethode, um auf den Controller zuzugreifen."""
        app = MDApp.get_running_app()
        return app.controller if hasattr(app, 'controller') else None

    def _refresh_ui(self):
        """Aktualisiert die UI nach einer Änderung am Handicap-Status."""
        Logger.debug(f"HandicapItemRow: Starte Widget-Aktualisierung")
        app = MDApp.get_running_app()
        widget = app.get_widget_by_tab_text('Handicaps', 'handicaps_widget')
        if widget:
            Logger.debug("HandicapItemRow: HandicapsWidget gefunden, führe refresh aus")
            Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)
        else:
            Logger.error("HandicapItemRow: HandicapsWidget nicht gefunden")

    def waehle_handicap(self):
        """
        Wählt ein Handicap aus.
        Prüft vorher, ob das Limit von 4 Punkten bereits erreicht ist und zeigt ggf. einen Warnhinweis.
        """
        Logger.debug(f"HandicapItemRow: Start waehle_handicap für {self.handicap_name}")
        controller = self._get_controller()
        if not controller:
            Logger.error("HandicapItemRow: Controller nicht gefunden")
            return

        # Prüfen, ob bereits das Maximum an Handicap-Punkten erreicht ist
        charakter = controller.charakter
        if charakter.gesamt_handicap_punkte >= 4:
            self._show_max_points_dialog()
            return

        try:
            controller.waehle_handicap(self.name_key)
            # Wenn keine Exception geworfen wurde, war die Aktion erfolgreich
            self.ausgewaehlt = True
            Logger.debug(f"HandicapItemRow: {self.handicap_name} erfolgreich ausgewählt")
            self._refresh_ui()
        except Exception as e:
            Logger.error(f"Fehler beim Auswählen des Handicaps: {str(e)}")

    def _show_max_points_dialog(self):
        """Zeigt einen Dialog an, wenn das Maximum an Handicap-Punkten erreicht ist."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        warning_label = MDLabel(
            text="Das Maximum von 4 Handicap-Punkten ist bereits erreicht! Die Auswirkungen des Handicaps werden angewendet, aber keine weiteren Punkte werden gutgeschrieben.",
            size_hint_y=None,
            height=dp(80),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(warning_label)
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Maximum erreicht",
            ),
            MDDialogContentContainer(
                content,
                orientation="vertical",
                padding=dp(0),
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self.close_dialog(),
                ),
                MDButton(
                    MDButtonText(text="Trotzdem auswählen"),
                    style="text",
                    on_release=lambda x: self._confirm_handicap_selection(),
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def close_dialog(self):
        """Schließt den Dialog."""
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()

    def _confirm_handicap_selection(self):
        """Führt die Handicap-Auswahl trotz voller Punktezahl durch."""
        self.close_dialog()
        controller = self._get_controller()
        if controller:
            controller.waehle_handicap(self.name_key)
            self.ausgewaehlt = True
            self._refresh_ui()

    def entferne_handicap(self):
        """
        Entfernt ein ausgewähltes Handicap.
        Delegiert die Aktion an den Controller und aktualisiert die Ansicht.
        """
        Logger.debug(f"HandicapItemRow: Start entferne_handicap für {self.handicap_name}")
        controller = self._get_controller()
        if not controller:
            Logger.error("HandicapItemRow: Controller nicht gefunden")
            return

        try:
            controller.entferne_handicap(self.name_key)
            # Wenn keine Exception geworfen wurde, war die Aktion erfolgreich
            self.ausgewaehlt = False
            Logger.debug(f"HandicapItemRow: {self.handicap_name} erfolgreich entfernt")
            self._refresh_ui()
        except Exception as e:
            Logger.error(f"Fehler beim Entfernen des Handicaps: {str(e)}")

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
        """Berechnet die Rahmenfarbe basierend auf dem Auswahlstatus."""
        return SELECTED_LINE_COLOR if self.ausgewaehlt else UNSELECTED_LINE_COLOR

    def on_ausgewaehlt_changed(self, instance, value):
        """Event-Handler für Änderungen am ausgewaehlt-Status."""
        Logger.debug(f"HandicapItemRow: ausgewaehlt changed to {value} for {self.handicap_name}")
        # Bei Änderung des Auswahlstatus auch die Umrandung aktualisieren
        self.line_color = self._get_line_color()


class HandicapsWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Handicaps.
    Hauptkomponente der View im MVC-Pattern.
    """
    stufen = ListProperty([])
    sort_order = StringProperty(DEFAULT_SORT_ORDER)
    only_selected_items = BooleanProperty(False)  # Neue Property für den Filter

    def __init__(self, **kwargs):
        """Initialisiert das HandicapsWidget und setzt Grundkonfiguration."""
        super().__init__(**kwargs)
        self._initialize_controller()
        self.menu = None
        Clock.schedule_once(self.post_init, 0)


    def toggle_only_selected_items(self, value):
        """
        Schaltet den Filter für 'Nur ausgewählte Elemente' um.
        Event-Handler für die Checkbox.
        """
        self.only_selected_items = value
        self.filter_handicaps()
        Logger.debug(f"Filter 'Nur ausgewählte Handicaps' gesetzt auf: {value}")

    def _filter_handicaps_data(self, alle_handicaps, search_term, selected_stufe):
        """
        Filtert die Handicap-Daten nach Suchbegriff, Stufe und ggf. Auswahlstatus.
        Extrahiert die Filterlogik aus filter_handicaps.
        """
        filtered_data = []
        
        Logger.debug(f"HandicapsWidget: Filtere Handicaps - Suchterm: {search_term}, Stufe: {selected_stufe}, Nur ausgewählte: {self.only_selected_items}")
        
        for key, handicap in alle_handicaps.items():
            # Filter für "Nur ausgewählte Elemente"
            if self.only_selected_items and not handicap.ausgewaehlt:
                continue
                
            # Stufen-Filter
            if (selected_stufe != ALL_CATEGORIES_TEXT.lower() and 
                (handicap.stufe is None or handicap.stufe.lower() != selected_stufe)):
                continue
                
            # Suchtext-Filter
            if (search_term in handicap.name.lower() or 
                search_term in handicap.beschreibung.lower()):
                
                handicap_data = {
                    'viewclass': 'HandicapItemRow',
                    'index': len(filtered_data),
                    'name_key': key,
                    'handicap_name': handicap.name,
                    'stufe': handicap.stufe,
                    'beschreibung': handicap.beschreibung,
                    'ausgewaehlt': handicap.ausgewaehlt
                }
                filtered_data.append(handicap_data)
                
        return filtered_data

    def _initialize_controller(self):
        """Initialisiert die Verbindung zum Controller."""
        app = MDApp.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None
        
        if not self.controller:
            Logger.error("HandicapsWidget: Controller nicht gefunden")

    def post_init(self, dt):
        """
        Initialisierung nach dem Laden des Widgets.
        Lädt Daten vom Modell und bereitet die Anzeige vor.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("HandicapsWidget: Controller oder Charakter nicht verfügbar")
            return
            
        alle_handicaps = self.controller.charakter.handicaps
        Logger.debug(f"HandicapsWidget: Lade {len(alle_handicaps)} Handicaps")
        
        # Stufen extrahieren und sortieren
        self._update_stufen(alle_handicaps)
        
        # Handicaps filtern und anzeigen
        self.filter_handicaps()

    def _update_stufen(self, handicaps_dict):
        """Aktualisiert die Liste der verfügbaren Handicap-Stufen."""
        self.stufen = sorted(list(set(
            handicap.stufe for handicap in handicaps_dict.values() 
            if handicap.stufe
        )))
        Logger.debug(f"HandicapsWidget: Gefundene Stufen: {self.stufen}")

    def refresh_widget(self):
        """
        Leert das Widget und lädt die Daten neu.
        Wird aufgerufen, wenn sich die Handicaps ändern.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("HandicapsWidget: Controller oder Charakter nicht verfügbar")
            return
            
        # RecycleView leeren
        self.ids.recycleview.data = []
        
        # Stufen neu laden
        alle_handicaps = self.controller.charakter.handicaps
        self._update_stufen(alle_handicaps)
        
        # Filter neu anwenden
        self.filter_handicaps()

    def toggle_sort_order(self):
        """
        Ändert die Sortierreihenfolge und aktualisiert die Anzeige.
        Event-Handler für den Sortierbutton.
        """
        self.sort_order = 'name_desc' if self.sort_order == 'name_asc' else 'name_asc'
        self.filter_handicaps()

    def filter_handicaps(self, *args):
        """
        Filtert die Handicaps basierend auf Suchtext und Kategorie.
        Event-Handler für Änderungen an Suchtext oder Kategorie.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("HandicapsWidget: Controller oder Charakter nicht verfügbar")
            return
            
        search_term = self.ids.search_input.text.lower()
        selected_stufe = self.ids.category_label.text.lower()

        # Handicaps vom Modell abrufen
        alle_handicaps = self.controller.charakter.handicaps
        
        # Gefilterte Liste erstellen
        filtered_data = self._filter_handicaps_data(
            alle_handicaps,
            search_term, 
            selected_stufe
        )
        
        # Sortieren
        filtered_data = self._sort_handicaps_data(filtered_data)
        
        # Index nach Sortierung aktualisieren
        for i, item in enumerate(filtered_data):
            item['index'] = i

        # An RecycleView übergeben
        self.ids.recycleview.data = filtered_data
        Logger.debug(f"HandicapsWidget: {len(filtered_data)} Handicaps gefiltert und sortiert")

    def _sort_handicaps_data(self, data):
        """
        Sortiert die Handicap-Daten nach der aktuellen Sortierreihenfolge.
        Extrahiert die Sortierlogik aus filter_handicaps.
        """
        is_ascending = self.sort_order == 'name_asc'
        data.sort(key=lambda x: x['handicap_name'].lower(), reverse=not is_ascending)
        return data

    def open_category_menu(self):
        """
        Öffnet das Kategorie-Auswahlmenü.
        Event-Handler für den Kategorie-Filter-Button.
        """
        menu_items = [
            {
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_category(x),
            } for i in [ALL_CATEGORIES_TEXT] + self.stufen
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
        self.filter_handicaps()