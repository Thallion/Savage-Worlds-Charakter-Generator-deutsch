# talente_view.py
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.button import MDIconButton
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp

class TalenteTooltip(MDTooltip):
    """Basis-Klasse für Tooltips in der Talente-View"""
    tooltip_text = StringProperty()

class TooltipIconButton(TalenteTooltip, MDIconButton):
    """Icon Button mit Tooltip Funktionalität"""
    icon = StringProperty()

# Bei der Factory registrieren
Factory.register('TooltipIconButton', TooltipIconButton)

kv = '''
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
    md_bg_color: ([0.2, 0.2, 0.2, 1]) if root.index % 2 == 0 else ([0.15, 0.15, 0.15, 1])
    line_color: [1, 0.65, 0, 1] if self.ausgewaehlt else (0, 0, 0, 0)
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

    MDFabButton:
        icon: "minus"
        style: "small"
        size_hint: None, None
        size: dp(40), dp(40)
        pos_hint: {"center_y": 0.5}
        on_release: root.entferne_talent()

    MDLabel:
        text: root.beschreibung
        font_size: dp(16)
        size_hint_x: 0.5
        halign: 'left'
        valign: 'middle'
'''

Builder.load_string(kv)

class TalenteRecycleView(MDRecycleView):
    """RecycleView für die effiziente Darstellung der Talente-Liste"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        Logger.debug("TalenteRecycleView: Initialisiert")

class TalentItemRow(MDBoxLayout):
    """Einzelne Zeile in der Talente-Liste"""
    index = NumericProperty(0)
    name_key = StringProperty("")
    talent_name = StringProperty("")
    kategorie = StringProperty("")
    rang = StringProperty("")
    beschreibung = StringProperty("")
    ausgewaehlt = ObjectProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(index=self.update_color)
        self.bind(ausgewaehlt=self.on_ausgewaehlt_changed)
        
    def _aktualisiere_widget(self):
        """Aktualisiert das TalenteWidget"""
        Logger.debug(f"TalentItemRow: Starte Widget-Aktualisierung")
        app = MDApp.get_running_app()
        widget = app.get_widget_by_tab_text('Talente', 'talente_widget')
        if widget:
            Logger.debug("TalentItemRow: TalenteWidget gefunden, führe refresh aus")
            Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)
        else:
            Logger.error("TalentItemRow: TalenteWidget nicht gefunden")

    def waehle_talent(self):
        """Wählt ein Talent aus"""
        Logger.debug(f"TalentItemRow: Start waehle_talent für {self.talent_name}")
        app = MDApp.get_running_app()
        try:
            app.controller.waehle_talent(self.name_key)
            self.ausgewaehlt = True
            Logger.debug(f"TalentItemRow: {self.talent_name} erfolgreich ausgewählt")
            self._aktualisiere_widget()
        except Exception as e:
            Logger.error(f"Fehler beim Auswählen des Talents: {str(e)}")

    def entferne_talent(self):
        """Entfernt ein ausgewähltes Talent"""
        Logger.debug(f"TalentItemRow: Start entferne_talent für {self.talent_name}")
        app = MDApp.get_running_app()
        try:
            app.controller.entferne_talent(self.name_key)
            self.ausgewaehlt = False
            Logger.debug(f"TalentItemRow: {self.talent_name} erfolgreich entfernt")
            self._aktualisiere_widget()
        except Exception as e:
            Logger.error(f"Fehler beim Entfernen des Talents: {str(e)}")

    def update_color(self, *args):
        """Aktualisiert die Hintergrundfarbe der Zeile"""
        is_dark = self.theme_cls.theme_style == "Dark"
        is_even = self.index % 2 == 0
        
        if is_dark:
            self.md_bg_color = [0.2, 0.2, 0.2, 1] if is_even else [0.15, 0.15, 0.15, 1]
        else:
            self.md_bg_color = [1, 1, 1, 1] if is_even else [0.85, 0.85, 0.85, 1]

    def on_ausgewaehlt_changed(self, instance, value):
        """Debug-Methode um Änderungen am ausgewaehlt-Status zu verfolgen"""
        Logger.debug(f"TalentItemRow: ausgewaehlt changed to {value} for {self.talent_name}")
            
class TalenteWidget(MDBoxLayout):
    """Widget zur Anzeige und Verwaltung von Talenten"""
    kategorien = ListProperty([])
    current_sort_option = StringProperty('Name')  # Standard-Sortieroption
    sort_order = StringProperty('asc')  # Standard-Sortierreihenfolge

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = MDApp.get_running_app().controller
        self.menu = None
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
        self.filter_talente()

    def filter_talente(self, *args):
        """Filtert und sortiert die Talente"""
        search_term = self.ids.search_input.text.lower()
        selected_kategorie = self.ids.category_label.text.lower()
        
        alle_talente = self.controller.charakter.talente
        filtered_data = []
        
        # Filtern
        for key, talent in alle_talente.items():
            if selected_kategorie != 'alle kategorien' and (talent.kategorie is None or talent.kategorie.lower() != selected_kategorie):
                continue
            if search_term in talent.name.lower() or search_term in talent.beschreibung.lower():
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

        # Sortieren
        if self.current_sort_option == 'Name':
            filtered_data.sort(key=lambda x: x['talent_name'].lower(),
                             reverse=(self.sort_order == 'desc'))
        elif self.current_sort_option == 'Rang':
            filtered_data.sort(key=lambda x: self.RANG_MAPPING.get(x['rang'], float('inf')),
                             reverse=(self.sort_order == 'desc'))
        elif self.current_sort_option == 'Kategorie':
            filtered_data.sort(key=lambda x: (x['kategorie'] or '').lower(),
                             reverse=(self.sort_order == 'desc'))

        # Index nach Sortierung setzen
        for i, item in enumerate(filtered_data):
            item['index'] = i

        self.ids.recycleview.data = filtered_data
        Logger.debug(f"Talente gefiltert und sortiert: {len(filtered_data)} Einträge")

    def post_init(self, dt):
        """Initialisierung nach dem Laden des Widgets"""
        alle_talente = self.controller.charakter.talente
        Logger.debug(f"TalenteWidget: Lade {len(alle_talente)} Talente")
        self.kategorien = sorted(list(set(talent.kategorie for talent in alle_talente.values() if talent.kategorie)))
        Logger.debug(f"TalenteWidget: Gefundene Kategorien: {self.kategorien}")
        self.filter_talente()

    def refresh_widget(self):
        """Leert das Widget und lädt die Daten neu"""
        self.ids.recycleview.data = []
        alle_talente = self.controller.charakter.talente
        self.kategorien = sorted(list(set(talent.kategorie for talent in alle_talente.values() if talent.kategorie)))
        self.filter_talente()

    def sortiere_talente(self):
        """Ändert die Sortierreihenfolge und aktualisiert die Anzeige"""
        self.sort_order = 'name_desc' if self.sort_order == 'name_asc' else 'name_asc'
        self.filter_talente()

    def open_category_menu(self):
        """Öffnet das Kategorie-Auswahlmenü"""
        menu_items = [
            {
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_category(x),
            } for i in ['Alle Kategorien'] + self.kategorien
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
        self.filter_talente()