# maechte_view.py
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.button import MDIconButton
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp

class MaechteTooltip(MDTooltip):
    """Basis-Klasse für Tooltips in der Mächte-View"""
    tooltip_text = StringProperty()

class TooltipIconButton(MaechteTooltip, MDIconButton):
    """Icon Button mit Tooltip Funktionalität"""
    icon = StringProperty()

# Bei der Factory registrieren
Factory.register('TooltipIconButton', TooltipIconButton)

kv = '''
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
    md_bg_color: ([0.2, 0.2, 0.2, 1]) if root.index % 2 == 0 else ([0.15, 0.15, 0.15, 1])
    line_color: [1, 0.65, 0, 1] if root.macht and root.macht.ausgewaehlt else [0, 0, 0, 0]
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

    MDFabButton:
        icon: "minus"
        style: "small"
        size_hint: None, None
        size: dp(40), dp(40)
        pos_hint: {"center_y": 0.5}
        on_release: root.entferne_macht()

    MDLabel:
        text: root.beschreibung
        font_size: dp(14)
        size_hint_x: 0.6
        halign: 'left'
        valign: 'middle'
'''

Builder.load_string(kv)

class MaechteRecycleView(MDRecycleView):
    """RecycleView für die effiziente Darstellung der Mächte-Liste"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        Logger.debug("MaechteRecycleView: Initialisiert")

class MachtItemRow(MDBoxLayout):
    """Einzelne Zeile in der Mächte-Liste"""
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
        self.controller = MDApp.get_running_app().controller
        super().__init__(**kwargs)
        self.bind(index=self.update_color)

    def _aktualisiere_widget(self):
        """Aktualisiert das MaechteWidget"""
        Logger.debug(f"MachtItemRow: Starte Widget-Aktualisierung")
        app = MDApp.get_running_app()
        widget = app.get_widget_by_tab_text('Mächte', 'maechte_widget')
        if widget:
            Logger.debug("MachtItemRow: MaechteWidget gefunden, führe refresh aus")
            Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)
        else:
            Logger.error("MachtItemRow: MaechteWidget nicht gefunden")

    def waehle_macht(self):
        """Wählt eine Macht aus"""
        success = self.controller.waehle_macht(self.macht_name)
        if success:
            Logger.debug(f"Macht '{self.macht_name}' ausgewählt.")
            self.macht.ausgewaehlt = True
            self.canvas.ask_update()
            self._aktualisiere_widget()
        else:
            Logger.warning(f"Auswahl der Macht '{self.macht_name}' fehlgeschlagen.")

    def entferne_macht(self):
        """Entfernt eine ausgewählte Macht"""
        success = self.controller.entferne_macht(self.macht_name)
        if success:
            Logger.debug(f"Macht '{self.macht_name}' entfernt.")
            self.macht.ausgewaehlt = False
            self.canvas.ask_update()
            self._aktualisiere_widget()
        else:
            Logger.warning(f"Entfernen der Macht '{self.macht_name}' fehlgeschlagen.")


    def update_color(self, *args):
        """Aktualisiert die Hintergrundfarbe der Zeile"""
        is_dark = self.theme_cls.theme_style == "Dark"
        is_even = self.index % 2 == 0
        
        if is_dark:
            self.md_bg_color = [0.2, 0.2, 0.2, 1] if is_even else [0.15, 0.15, 0.15, 1]
        else:
            self.md_bg_color = [1, 1, 1, 1] if is_even else [0.85, 0.85, 0.85, 1]
            
class MaechteWidget(MDBoxLayout):
    """Widget zur Anzeige und Verwaltung von Mächten"""
    current_sort_option = StringProperty('Name')  # Standard-Sortieroption
    sort_order = StringProperty('asc')  # Standard-Sortierreihenfolge

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = MDApp.get_running_app().controller
        # RANG_MAPPING für die Sortierung nach Rang
        self.RANG_MAPPING = {
            'A': 1,    # Anfänger
            'F': 2,    # Fortgeschritten
            'V': 3,    # Veteran
            'H': 4,    # Heroisch
            'L': 5,    # Legendär
            'WC': 6    # Wild Card oder spezieller Rang
        }
        Clock.schedule_once(self.post_init, 0)

    def update_sort_option(self, option):
        """Aktualisiert die Sortieroptionen und -reihenfolge"""
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
        """Filtert und sortiert die Mächte"""
        search_term = self.ids.search_input.text.lower()
        
        alle_maechte = self.controller.charakter.maechte
        filtered_data = []
        
        # Filtern
        for macht in alle_maechte.values():
            if search_term and not (search_term in macht.name.lower() or search_term in macht.beschreibung.lower()):
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

        # Sortieren
        if self.current_sort_option == 'Name':
            filtered_data.sort(key=lambda x: x['macht_name'].lower(),
                             reverse=(self.sort_order == 'desc'))
        elif self.current_sort_option == 'Rang':
            filtered_data.sort(key=lambda x: self.RANG_MAPPING.get(x['rang'], float('inf')),
                             reverse=(self.sort_order == 'desc'))

        # Index nach Sortierung setzen
        for i, item in enumerate(filtered_data):
            item['index'] = i

        self.ids.recycleview.data = filtered_data
        Logger.debug(f"Mächte gefiltert und sortiert: {len(filtered_data)} Einträge")

    def post_init(self, dt):
        """Initialisierung nach dem Laden des Widgets"""
        self.filter_maechte()
        Logger.debug("MaechteWidget: Post-Init abgeschlossen")

    def refresh_widget(self):
        """Leert das Widget und lädt die Daten neu"""
        self.ids.recycleview.data = []
        self.filter_maechte()
        Logger.debug("MaechteWidget: Widget aktualisiert")