# handicaps_view.py
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp

kv = '''
<HandicapsWidget>:
    orientation: 'vertical'
    md_bg_color: self.theme_cls.backgroundColor  
    
    MDBoxLayout:
        size_hint_y: None
        height: 100
        padding: [20, 5]
        spacing: 5

        MDIconButton:
            icon: "sort-alphabetical-ascending"
            size_hint_y: 1
            on_release: root.sortiere_handicaps()

        MDTextField:
            id: search_input
            hint_text: 'Suche...'
            size_hint_x: 1
            on_text: root.filter_handicaps()

        MDIconButton:
            icon: "filter"
            size_hint_y: 1
            on_release: root.open_category_menu()

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

    # RecycleView mit expliziter Größe
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
    # Farblogik
    md_bg_color: ([0.2, 0.2, 0.2, 1]) if root.index % 2 == 0 \
        else ([0.15, 0.15, 0.15, 1])
    line_color: [1, 0.65, 0, 1] if self.ausgewaehlt else (0, 0, 0, 0)    
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

    MDFabButton:
        icon: "minus"
        style: "small"
        size_hint: None, None
        size: dp(40), dp(40)
        pos_hint: {"center_y": 0.5}
        on_release: root.entferne_handicap()

    MDLabel:
        text: root.beschreibung
        font_size: dp(16)
        size_hint_x: 0.6
        halign: 'left'
        valign: 'middle'
'''

Builder.load_string(kv)

class HandicapsRecycleView(MDRecycleView):
    """RecycleView für die effiziente Darstellung der Handicap-Liste"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        Logger.debug("HandicapsRecycleView: Initialisiert")

class HandicapItemRow(MDBoxLayout):
    """Einzelne Zeile in der Handicap-Liste"""
    index = NumericProperty(0)
    name_key = StringProperty("")
    handicap_name = StringProperty("")
    stufe = StringProperty("")
    beschreibung = StringProperty("")
    ausgewaehlt = ObjectProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(index=self.update_color)
        self.bind(ausgewaehlt=self.on_ausgewaehlt_changed)
        
    def _aktualisiere_widget(self):
        """Aktualisiert das HandicapsWidget"""
        Logger.debug(f"HandicapItemRow: Starte Widget-Aktualisierung")
        app = MDApp.get_running_app()
        widget = app.get_widget_by_tab_text('Handicaps', 'handicaps_widget')
        if widget:
            Logger.debug("HandicapItemRow: HandicapsWidget gefunden, führe refresh aus")
            Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)
        else:
            Logger.error("HandicapItemRow: HandicapsWidget nicht gefunden")

    def waehle_handicap(self):
        """Wählt ein Handicap aus"""
        Logger.debug(f"HandicapItemRow: Start waehle_handicap für {self.handicap_name}")
        app = MDApp.get_running_app()
        try:
            app.controller.waehle_handicap(self.name_key)
            # Wenn keine Exception geworfen wurde, war die Aktion erfolgreich
            self.ausgewaehlt = True
            Logger.debug(f"HandicapItemRow: {self.handicap_name} erfolgreich ausgewählt")
            self._aktualisiere_widget()
        except Exception as e:
            Logger.error(f"Fehler beim Auswählen des Handicaps: {str(e)}")

    def entferne_handicap(self):
        """Entfernt ein ausgewähltes Handicap"""
        Logger.debug(f"HandicapItemRow: Start entferne_handicap für {self.handicap_name}")
        app = MDApp.get_running_app()
        try:
            app.controller.entferne_handicap(self.name_key)
            # Wenn keine Exception geworfen wurde, war die Aktion erfolgreich
            self.ausgewaehlt = False
            Logger.debug(f"HandicapItemRow: {self.handicap_name} erfolgreich entfernt")
            self._aktualisiere_widget()
        except Exception as e:
            Logger.error(f"Fehler beim Entfernen des Handicaps: {str(e)}")

    def update_color(self, *args):
            """Aktualisiert die Hintergrundfarbe der Zeile"""
            is_dark = self.theme_cls.theme_style == "Dark"
            is_even = self.index % 2 == 0
            
            if is_dark:
                # Dunkles Theme bleibt unverändert
                self.md_bg_color = [0.2, 0.2, 0.2, 1] if is_even else [0.15, 0.15, 0.15, 1]
            else:
                # Helles Theme mit erhöhtem Kontrast
                self.md_bg_color = [1, 1, 1, 1] if is_even else [0.85, 0.85, 0.85, 1]  # Weiß vs. Hellgrau

    def get_row_colors(self):
        """Berechnet die Zeilenfarben basierend auf dem Theme und Auswahlstatus"""
        is_dark = self.theme_cls.theme_style == "Dark"
        is_even = self.index % 2 == 0
        
        if is_dark:
            # Dunkles Theme bleibt unverändert
            base_color = [0.2, 0.2, 0.2, 1] if is_even else [0.15, 0.15, 0.15, 1]
        else:
            # Helles Theme mit erhöhtem Kontrast
            base_color = [1, 1, 1, 1] if is_even else [0.85, 0.85, 0.85, 1]  # Weiß vs. Hellgrau

    def on_ausgewaehlt_changed(self, instance, value):
        """Debug-Methode um Änderungen am ausgewaehlt-Status zu verfolgen"""
        Logger.debug(f"HandicapItemRow: ausgewaehlt changed to {value} for {self.handicap_name}")
            
class HandicapsWidget(MDBoxLayout):
    """Widget zur Anzeige und Verwaltung von Handicaps"""
    stufen = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sort_order = 'name_asc'
        self.controller = MDApp.get_running_app().controller
        self.menu = None
        Clock.schedule_once(self.post_init, 0)

    def post_init(self, dt):
        """Initialisierung nach dem Laden des Widgets"""
        alle_handicaps = self.controller.charakter.handicaps
        Logger.debug(f"HandicapsWidget: Lade {len(alle_handicaps)} Handicaps")
        self.stufen = sorted(list(set(handicap.stufe for handicap in alle_handicaps.values() if handicap.stufe)))
        Logger.debug(f"HandicapsWidget: Gefundene Stufen: {self.stufen}")
        self.filter_handicaps()

    def refresh_widget(self):
        """Leert das Widget und lädt die Daten neu"""
        # RecycleView leeren
        self.ids.recycleview.data = []
        # Stufen neu laden
        alle_handicaps = self.controller.charakter.handicaps
        self.stufen = sorted(list(set(handicap.stufe for handicap in alle_handicaps.values() if handicap.stufe)))
        # Filter neu anwenden
        self.filter_handicaps()

    def filter_handicaps(self, *args):
        """Filtert die Handicaps basierend auf Suchtext und Kategorie"""
        search_term = self.ids.search_input.text.lower()
        selected_stufe = self.ids.category_label.text.lower()
        
        alle_handicaps = self.controller.charakter.handicaps
        filtered_data = []
        
        Logger.debug(f"HandicapsWidget: Filtere Handicaps - Suchterm: {search_term}, Stufe: {selected_stufe}")
        
        for key, handicap in alle_handicaps.items():
            if selected_stufe != 'alle stufen' and (handicap.stufe is None or handicap.stufe.lower() != selected_stufe):
                continue
            if search_term in handicap.name.lower() or search_term in handicap.beschreibung.lower():
                #Logger.debug(f"HandicapsWidget: Füge Handicap hinzu - {handicap.name}")
                filtered_data.append({
                    'viewclass': 'HandicapItemRow',
                    'index': len(filtered_data),
                    'name_key': key,
                    'handicap_name': handicap.name,
                    'stufe': handicap.stufe,
                    'beschreibung': handicap.beschreibung,
                    'ausgewaehlt': handicap.ausgewaehlt
                })
        
        Logger.debug(f"HandicapsWidget: {len(filtered_data)} Handicaps gefiltert")
        self.ids.recycleview.data = filtered_data

    def sortiere_handicaps(self):
        """Ändert die Sortierreihenfolge und aktualisiert die Anzeige"""
        self.sort_order = 'name_desc' if self.sort_order == 'name_asc' else 'name_asc'
        self.filter_handicaps()

    def open_category_menu(self):
        """Öffnet das Kategorie-Auswahlmenü"""
        menu_items = [
            {
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_category(x),
            } for i in ['Alle Stufen'] + self.stufen
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.category_label,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def set_category(self, text):
        """Setzt die ausgewählte Kategorie und aktualisiert die Anzeige"""
        self.ids.category_label.text = text
        self.menu.dismiss()
        self.filter_handicaps()
     