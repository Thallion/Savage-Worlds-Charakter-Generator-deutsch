# ausruestung_view.py
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText, MDIconButton
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.label import MDLabel
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)

class AusruestungTooltip(MDTooltip):
    """Basis-Klasse für Tooltips in der Ausrüstungs-View"""
    tooltip_text = StringProperty()

class TooltipIconButton(AusruestungTooltip, MDButton):
    """Icon Button mit Tooltip Funktionalität"""
    icon = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.style = "filled"
        self.size_hint = (None, None)
        self.size = (dp(40), dp(50))

# Bei der Factory registrieren
Factory.register('TooltipIconButton', TooltipIconButton)

kv = '''
<TooltipIconButton>:
    style: "filled"
    size_hint: None, None
    size: dp(40), dp(40)
    MDButtonIcon:
        icon: root.icon
    MDTooltipPlain:
        text: root.tooltip_text

<AusruestungWidget>:
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
            id: sort_weight_btn
            icon: "sort-ascending" if root.current_sort_option != 'Gewicht' or root.sort_order == 'asc' else "sort-descending"
            tooltip_text: "Nach Gewicht sortieren" if root.current_sort_option != 'Gewicht' or root.sort_order == 'asc' else "Gewicht absteigend sortieren"
            on_release: root.update_sort_option('Gewicht')
            pos_hint: {"center_y": .5}

        TooltipIconButton:
            id: sort_costs_btn
            icon: "sort-ascending" if root.current_sort_option != 'Kosten' or root.sort_order == 'asc' else "sort-descending"
            tooltip_text: "Nach Kosten sortieren" if root.current_sort_option != 'Kosten' or root.sort_order == 'asc' else "Kosten absteigend sortieren"
            on_release: root.update_sort_option('Kosten')
            pos_hint: {"center_y": .5}

        TooltipIconButton:
            id: sort_amount_btn
            icon: "sort-ascending" if root.current_sort_option != 'Menge' or root.sort_order == 'asc' else "sort-descending"
            tooltip_text: "Nach Menge sortieren" if root.current_sort_option != 'Menge' or root.sort_order == 'asc' else "Menge absteigend sortieren"
            on_release: root.update_sort_option('Menge')
            pos_hint: {"center_y": .5}

        TooltipIconButton:
            id: sort_category_btn
            icon: "sort-alphabetical-ascending" if root.current_sort_option != 'Kategorie' or root.sort_order == 'asc' else "sort-alphabetical-descending"
            tooltip_text: "Nach Kategorie sortieren" if root.current_sort_option != 'Kategorie' or root.sort_order == 'asc' else "Kategorie absteigend sortieren"
            on_release: root.update_sort_option('Kategorie')
            pos_hint: {"center_y": .5}

        MDTextField:
            id: search_input
            hint_text: 'Suche...'
            size_hint_x: 1
            on_text: root.filter_ausruestung()

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
        text: 'Ausrüstung'
        font_size: dp(24)
        size_hint_y: None
        height: dp(48)
        padding: [20, 10]

    AusruestungRecycleView:
        id: recycleview
        viewclass: 'AusruestungItemRow'
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

<AusruestungItemRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(60)
    md_bg_color: ([0.2, 0.2, 0.2, 1]) if root.index % 2 == 0 else ([0.15, 0.15, 0.15, 1])
    spacing: dp(10)
    padding: dp(10)

    MDLabel:
        text: root.name
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
        text: f"{root.gewicht} kg"
        font_size: dp(16)
        size_hint_x: 0.1
        halign: 'left'
        valign: 'middle'

    MDLabel:
        text: f"{root.kosten} {root.waehrungseinheit}"
        font_size: dp(16)
        size_hint_x: 0.1
        halign: 'left'
        valign: 'middle'

    MDLabel:
        text: str(root.menge)
        font_size: dp(16)
        size_hint_x: 0.1
        halign: 'left'
        valign: 'middle'

    MDButton:
        style: "filled"
        size_hint: None, None
        size: dp(40), dp(40)
        pos_hint: {"center_y": 0.5}
        on_release: root.kaufen_ausruestung()
        MDButtonIcon:
            icon: "plus"

    MDButton:
        style: "filled"
        size_hint: None, None
        size: dp(40), dp(40)
        pos_hint: {"center_y": 0.5}
        on_release: root.verkaufen_ausruestung()
        MDButtonIcon:
            icon: "minus"
'''

Builder.load_string(kv)

class AusruestungRecycleView(MDRecycleView):
    """RecycleView für die effiziente Darstellung der Ausruestung-Liste"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        Logger.debug("AusruestungRecycleView: Initialisiert")

class KaufDialogContent(MDBoxLayout):
    """Content-Widget für den Kauf-Dialog"""
    def __init__(self, name, preis, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = "12dp"
        self.padding = "12dp"
        self.size_hint_y = None
        self.height = "200dp"
        
        # Textfelder als Properties speichern
        self.anzahl_field = MDTextField(
            mode="outlined",
            text="1",
            input_filter="int",
            children=[
                MDTextFieldHintText(
                    text="Anzahl"
                )
            ]
        )
        self.add_widget(self.anzahl_field)
        
        self.preis_field = MDTextField(
            mode="outlined",
            text=str(preis),
            input_filter="float",
            children=[
                MDTextFieldHintText(
                    text="Preis pro Stück (optional)"
                )
            ]
        )
        self.add_widget(self.preis_field)

class VerkaufDialogContent(KaufDialogContent):
    """Content-Widget für den Verkauf-Dialog - erbt von KaufDialogContent"""
    pass# ausruestung_view.py

class AusruestungItemRow(MDBoxLayout):
    """Einzelne Zeile in der Ausrüstungs-Liste"""
    index = NumericProperty(0)
    name = StringProperty("")
    kategorie = StringProperty("")
    gewicht = NumericProperty(0)
    kosten = NumericProperty(0)
    menge = NumericProperty(0)
    waehrungseinheit = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(index=self.update_color)
        
    def _aktualisiere_widget(self):
        """Aktualisiert das AusruestungWidget"""
        Logger.debug(f"AusruestungItemRow: Starte Widget-Aktualisierung")
        app = MDApp.get_running_app()
        widget = app.root.ids.ausruestung_widget
        if widget:
            Logger.debug("AusruestungItemRow: AusruestungWidget gefunden, führe refresh aus")
            Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)
        else:
            Logger.error("AusruestungItemRow: AusruestungWidget nicht gefunden")

    def kaufen_ausruestung(self):
        """Kauft eine Ausrüstung"""
        Logger.debug(f"AusruestungItemRow: Start kaufen_ausruestung für {self.name}")
        try:
            dialog_content = KaufDialogContent(name=self.name, preis=self.kosten)
            self.dialog = MDDialog(
                MDDialogHeadlineText(
                    text=f"Kaufen von {self.name}",
                ),
                MDDialogContentContainer(
                    dialog_content,
                    orientation="vertical",
                ),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="Abbrechen"),
                        style="text",
                        on_release=lambda x: self.dialog.dismiss(),
                    ),
                    MDButton(
                        MDButtonText(text="Kaufen"),
                        style="text",
                        on_release=lambda x: self._handle_kauf_dialog(dialog_content),
                    ),
                    spacing="8dp",
                ),
            )
            self.dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Kaufen der Ausrüstung: {str(e)}")

    def verkaufen_ausruestung(self):
        """Verkauft eine Ausrüstung"""
        Logger.debug(f"AusruestungItemRow: Start verkaufen_ausruestung für {self.name}")
        try:
            dialog_content = VerkaufDialogContent(name=self.name, preis=self.kosten)
            self.dialog = MDDialog(
                MDDialogHeadlineText(
                    text=f"Verkaufen von {self.name}",
                ),
                MDDialogContentContainer(
                    dialog_content,
                    orientation="vertical",
                ),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="Abbrechen"),
                        style="text",
                        on_release=lambda x: self.dialog.dismiss(),
                    ),
                    MDButton(
                        MDButtonText(text="Verkaufen"),
                        style="text",
                        on_release=lambda x: self._handle_verkauf_dialog(dialog_content),
                    ),
                    spacing="8dp",
                ),
            )
            self.dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Verkaufen der Ausrüstung: {str(e)}")

    def _handle_kauf_dialog(self, content):
        """Verarbeitet den Kauf nach Dialog-Bestätigung"""
        try:
            anzahl = int(content.anzahl_field.text)
            preis = float(content.preis_field.text) if content.preis_field.text else None
            
            if anzahl < 1:
                self.show_error("Die Anzahl muss mindestens 1 sein.")
                return
                
            if preis is not None and preis < 0:
                self.show_error("Der Preis darf nicht negativ sein.")
                return

            app = MDApp.get_running_app()
            success = app.controller.kaufen_ausruestung(
                self.name,
                anzahl=anzahl,
                preis_pro_stueck=preis
            )
            
            if success:
                self.dialog.dismiss()
                # Widget-Aktualisierung über controller
                if hasattr(app, 'root') and hasattr(app.root, 'refresh_current_tab'):
                    app.root.refresh_current_tab()
            else:
                self.show_error("Der Kauf konnte nicht durchgeführt werden.")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten des Kaufs: {str(e)}")
            self.show_error("Ein unerwarteter Fehler ist aufgetreten.")

    def _handle_verkauf_dialog(self, content):
        """Verarbeitet den Verkauf nach Dialog-Bestätigung"""
        try:
            anzahl = int(content.anzahl_field.text)
            preis = float(content.preis_field.text) if content.preis_field.text else None
            
            if anzahl < 1:
                self.show_error("Die Anzahl muss mindestens 1 sein.")
                return
                
            if preis is not None and preis < 0:
                self.show_error("Der Preis darf nicht negativ sein.")
                return

            app = MDApp.get_running_app()
            success = app.controller.verkaufen_ausruestung(
                self.name,
                anzahl=anzahl,
                preis_pro_stueck=preis
            )
            
            if success:
                self.dialog.dismiss()
                # Widget-Aktualisierung über controller
                if hasattr(app, 'root') and hasattr(app.root, 'refresh_current_tab'):
                    app.root.refresh_current_tab()
            else:
                self.show_error("Der Verkauf konnte nicht durchgeführt werden.")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten des Verkaufs: {str(e)}")
            self.show_error("Ein unerwarteter Fehler ist aufgetreten.")

    def show_error(self, message):
        """Zeigt eine Fehlermeldung an"""
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            padding="12dp",
            children=[
                MDLabel(
                    text=message,
                    theme_text_color="Error"
                )
            ]
        )

        error_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Fehler",
            ),
            MDDialogContentContainer(
                content,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDButton(
                    style="text",
                    on_release=lambda x: error_dialog.dismiss(),
                    children=[
                        MDButtonText(text="Schließen")
                    ]
                ),
                spacing="8dp",
            ),
        )
        error_dialog.open()

    def update_color(self, *args):
        """Aktualisiert die Hintergrundfarbe der Zeile"""
        is_dark = self.theme_cls.theme_style == "Dark"
        is_even = self.index % 2 == 0
        
        if is_dark:
            self.md_bg_color = [0.2, 0.2, 0.2, 1] if is_even else [0.15, 0.15, 0.15, 1]
        else:
            self.md_bg_color = [1, 1, 1, 1] if is_even else [0.85, 0.85, 0.85, 1]


class AusruestungWidget(MDBoxLayout):
    """Widget zur Anzeige und Verwaltung von Ausrüstung"""
    kategorien = ListProperty([])
    current_sort_option = StringProperty('Name')  # Standard-Sortieroption
    sort_order = StringProperty('asc')  # Standard-Sortierreihenfolge

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = MDApp.get_running_app().controller
        self.menu = None
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
        self.filter_ausruestung()

    def filter_ausruestung(self, *args):
        """Filtert und sortiert die Ausrüstung"""
        search_term = self.ids.search_input.text.lower()
        selected_kategorie = self.ids.category_label.text.lower()
        
        alle_ausruestung = self.controller.charakter.ausruestung
        filtered_data = []
        
        # Filtern
        for key, ausruestung in alle_ausruestung.items():
            if selected_kategorie != 'alle kategorien' and (ausruestung.kategorie is None or ausruestung.kategorie.lower() != selected_kategorie):
                continue
            if search_term in ausruestung.name.lower() or search_term in ausruestung.beschreibung.lower():
                ausruestung_data = {
                    'viewclass': 'AusruestungItemRow',
                    'index': len(filtered_data),
                    'name': ausruestung.name,
                    'kategorie': ausruestung.kategorie or "Unbekannt",
                    'gewicht': ausruestung.gewicht,
                    'kosten': ausruestung.kosten,
                    'menge': ausruestung.menge,
                    'waehrungseinheit': self.controller.charakter.waehrungseinheit
                }
                filtered_data.append(ausruestung_data)

        # Sortieren
        if self.current_sort_option == 'Name':
            filtered_data.sort(key=lambda x: x['name'].lower(),
                             reverse=(self.sort_order == 'desc'))
        elif self.current_sort_option == 'Gewicht':
            filtered_data.sort(key=lambda x: x['gewicht'],
                             reverse=(self.sort_order == 'desc'))
        elif self.current_sort_option == 'Kategorie':
            filtered_data.sort(key=lambda x: x['kategorie'].lower(),
                             reverse=(self.sort_order == 'desc'))

        # Index nach Sortierung aktualisieren
        for i, item in enumerate(filtered_data):
            item['index'] = i

        self.ids.recycleview.data = filtered_data
        Logger.debug(f"Ausrüstung gefiltert und sortiert: {len(filtered_data)} Einträge")

    def post_init(self, dt):
        """Initialisierung nach dem Laden des Widgets"""
        alle_ausruestung = self.controller.charakter.ausruestung
        Logger.debug(f"AusruestungWidget: Lade {len(alle_ausruestung)} Ausrüstungsteile")
        self.kategorien = sorted(list(set(ausruestung.kategorie for ausruestung in alle_ausruestung.values() if ausruestung.kategorie)))
        Logger.debug(f"AusruestungWidget: Gefundene Kategorien: {self.kategorien}")
        self.filter_ausruestung()

    def refresh_widget(self):
        """Leert das Widget und lädt die Daten neu"""
        self.ids.recycleview.data = []
        alle_ausruestung = self.controller.charakter.ausruestung
        self.kategorien = sorted(list(set(ausruestung.kategorie for ausruestung in alle_ausruestung.values() if ausruestung.kategorie)))
        self.filter_ausruestung()

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
        self.filter_ausruestung()