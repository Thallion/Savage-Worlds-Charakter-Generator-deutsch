# ausruestung_view.py
"""
View-Komponente für die Ausrüstung nach dem MVC-Pattern.
Bietet Darstellung und Interaktion mit der Ausrüstung des Charakters.
"""

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)

# Konstanten für bessere Wartbarkeit
DEFAULT_SORT_OPTION = 'Name'
DEFAULT_SORT_ORDER = 'asc'
ALL_CATEGORIES_TEXT = 'Alle Kategorien'
DEFAULT_ROW_HEIGHT = dp(60)
DIALOG_HEIGHT = "200dp"
BUTTON_SIZE = (dp(40), dp(40))
ERROR_DIALOG_TITLE = "Fehler"
MIN_AMOUNT = 1


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
        self.size = BUTTON_SIZE


# Bei der Factory registrieren
Factory.register('TooltipIconButton', TooltipIconButton)


# KV-String in eine Konstante, könnte später in eine separate Datei ausgelagert werden
KV_STRING = '''
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

        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_x: None
            width: dp(200)
            spacing: dp(5)
            
            MDCheckbox:
                id: only_owned_checkbox
                size_hint: None, None
                size: dp(40), dp(40)
                active: root.only_owned_items
                on_active: root.toggle_only_owned_items(self.active)
                pos_hint: {"center_y": .5}
                
            MDLabel:
                text: "Nur vorhandene"
                size_hint_y: None
                height: dp(40)
                pos_hint: {"center_y": .5}

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

Builder.load_string(KV_STRING)


class AusruestungRecycleView(MDRecycleView):
    """
    RecycleView für die effiziente Darstellung der Ausruestung-Liste.
    Implementiert die View-Komponente des MVC-Patterns.
    """
    parent_view = ObjectProperty(None)  # Referenz auf das übergeordnete AusruestungWidget
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        Logger.debug("AusruestungRecycleView: Initialisiert")
        # Warten bis Widget fertig geladen ist, dann parent_view setzen
        Clock.schedule_once(self._find_parent_view, 0)
    
    def _find_parent_view(self, dt):
        """Findet und speichert Referenz auf das übergeordnete AusruestungWidget"""
        current = self.parent
        while current:
            if isinstance(current, AusruestungWidget):
                self.parent_view = current
                Logger.debug("AusruestungRecycleView: parent_view gesetzt")
                break
            current = current.parent


class DialogContentBase(MDBoxLayout):
    """Basis-Klasse für Dialog-Inhalte"""
    def __init__(self, name, preis, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = "12dp"
        self.padding = "12dp"
        self.size_hint_y = None
        self.height = DIALOG_HEIGHT
        
        self._setup_fields(preis)

    def _setup_fields(self, preis):
        """Erstellt die Eingabefelder für den Dialog"""
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

    def get_values(self):
        """Gibt die eingegebenen Werte zurück"""
        try:
            anzahl = int(self.anzahl_field.text)
            preis = float(self.preis_field.text) if self.preis_field.text else None
            return anzahl, preis
        except ValueError:
            return None, None

    def validate(self):
        """Validiert die Eingaben"""
        anzahl, preis = self.get_values()
        
        if anzahl is None:
            return False, "Bitte geben Sie eine gültige Anzahl ein."
        
        if anzahl < MIN_AMOUNT:
            return False, f"Die Anzahl muss mindestens {MIN_AMOUNT} sein."
            
        if preis is not None and preis < 0:
            return False, "Der Preis darf nicht negativ sein."
            
        return True, None


class KaufDialogContent(DialogContentBase):
    """Content-Widget für den Kauf-Dialog"""
    pass


class VerkaufDialogContent(DialogContentBase):
    """Content-Widget für den Verkauf-Dialog"""
    pass


class AusruestungItemRow(MDBoxLayout):
    """
    Einzelne Zeile in der Ausrüstungs-Liste.
    Teil der View-Komponente des MVC-Patterns.
    """
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
        self.dialog = None

    def _get_controller(self):
        """Hilfsmethode zum Abrufen des Controllers"""
        app = MDApp.get_running_app()
        return app.controller if hasattr(app, 'controller') else None

    def _refresh_ui(self):
        """
        Aktualisiert die UI nach einer Transaktion.
        Findet das übergeordnete AusruestungWidget und aktualisiert es direkt.
        """
        # Versuche zuerst, das übergeordnete AusruestungWidget zu finden
        parent_widget = self.get_root_ausruestung_widget()
        if parent_widget:
            Logger.debug(f"AusruestungItemRow: Aktualisiere übergeordnetes AusruestungWidget")
            Clock.schedule_once(lambda dt: parent_widget.refresh_widget(), 0)
            return
            
        # Fallback: Versuche, über das Root-Widget der App zu aktualisieren
        app = MDApp.get_running_app()
        if hasattr(app, 'root') and hasattr(app.root, 'refresh_current_tab'):
            Logger.debug(f"AusruestungItemRow: Aktualisiere über app.root.refresh_current_tab()")
            app.root.refresh_current_tab()
        else:
            # Letzte Option: Suche über app.get_widget_by_tab_text
            Logger.debug(f"AusruestungItemRow: Versuche Aktualisierung über app.get_widget_by_tab_text()")
            if hasattr(app, 'get_widget_by_tab_text'):
                widget = app.get_widget_by_tab_text('Ausrüstung', 'ausruestung_widget')
                if widget:
                    Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)
                else:
                    Logger.error("AusruestungItemRow: Konnte kein AusruestungWidget finden")

    def get_root_ausruestung_widget(self):
        """
        Findet das übergeordnete AusruestungWidget in der Widget-Hierarchie.
        
        Returns:
            AusruestungWidget oder None, wenn keines gefunden wurde
        """
        current = self.parent
        while current:
            if isinstance(current, AusruestungWidget):
                return current
                
            # Bei RecycleView ist der eigentliche Parent nicht direkt parent
            if hasattr(current, 'parent_view') and current.parent_view:
                return current.parent_view
                
            current = current.parent
        
        # Alternativ versuchen wir, vom Controller her zu finden
        app = MDApp.get_running_app()
        if hasattr(app, 'root') and hasattr(app.root, 'ids'):
            # Prüfe, ob ausruestung_widget direkt in den IDs vorhanden ist
            if hasattr(app.root.ids, 'ausruestung_widget'):
                return app.root.ids.ausruestung_widget
        
        return None
        
    def kaufen_ausruestung(self):
        """
        Zeigt einen Dialog an, um eine Ausrüstung zu kaufen.
        Event-Handler für den Plus-Button.
        """
        Logger.debug(f"AusruestungItemRow: Start kaufen_ausruestung für {self.name}")
        try:
            dialog_content = KaufDialogContent(name=self.name, preis=self.kosten)
            self._show_transaction_dialog(
                title=f"Kaufen von {self.name}",
                content=dialog_content,
                action_text="Kaufen",
                action_handler=self._handle_kauf_dialog
            )
        except Exception as e:
            Logger.error(f"Fehler beim Kaufen der Ausrüstung: {str(e)}")
            self.show_error(f"Ein Fehler ist aufgetreten: {str(e)}")

    def verkaufen_ausruestung(self):
        """
        Zeigt einen Dialog an, um eine Ausrüstung zu verkaufen.
        Event-Handler für den Minus-Button.
        """
        Logger.debug(f"AusruestungItemRow: Start verkaufen_ausruestung für {self.name}")
        try:
            dialog_content = VerkaufDialogContent(name=self.name, preis=self.kosten)
            self._show_transaction_dialog(
                title=f"Verkaufen von {self.name}",
                content=dialog_content,
                action_text="Verkaufen",
                action_handler=self._handle_verkauf_dialog
            )
        except Exception as e:
            Logger.error(f"Fehler beim Verkaufen der Ausrüstung: {str(e)}")
            self.show_error(f"Ein Fehler ist aufgetreten: {str(e)}")

    def _show_transaction_dialog(self, title, content, action_text, action_handler):
        """
        Zeigt einen Dialog für eine Transaktion an.
        Extrahiert gemeinsamen Code aus kaufen_ausruestung und verkaufen_ausruestung.
        """
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text=title,
            ),
            MDDialogContentContainer(
                content,
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
                    MDButtonText(text=action_text),
                    style="text",
                    on_release=lambda x: action_handler(content),
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def _handle_kauf_dialog(self, content):
        """
        Verarbeitet den Kauf nach Dialog-Bestätigung.
        Ruft die entsprechende Controller-Methode auf.
        """
        try:
            # Validiere Eingaben
            is_valid, error_message = content.validate()
            if not is_valid:
                self.show_error(error_message)
                return

            anzahl, preis = content.get_values()
            
            # Controller-Operation ausführen
            controller = self._get_controller()
            if not controller:
                self.show_error("Controller nicht gefunden.")
                return
                
            success = controller.kaufen_ausruestung(
                self.name,
                anzahl=anzahl,
                preis_pro_stueck=preis
            )

            if success:
                self.dialog.dismiss()
                self._refresh_ui()
            else:
                self.show_error("Der Kauf konnte nicht durchgeführt werden.")

        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten des Kaufs: {str(e)}")
            self.show_error("Ein unerwarteter Fehler ist aufgetreten.")

    def _handle_verkauf_dialog(self, content):
        """
        Verarbeitet den Verkauf nach Dialog-Bestätigung.
        Ruft die entsprechende Controller-Methode auf.
        """
        try:
            # Validiere Eingaben
            is_valid, error_message = content.validate()
            if not is_valid:
                self.show_error(error_message)
                return

            anzahl, preis = content.get_values()
            
            # Controller-Operation ausführen
            controller = self._get_controller()
            if not controller:
                self.show_error("Controller nicht gefunden.")
                return
                
            success = controller.verkaufen_ausruestung(
                self.name,
                anzahl=anzahl,
                preis_pro_stueck=preis
            )

            if success:
                self.dialog.dismiss()
                self._refresh_ui()
            else:
                self.show_error("Der Verkauf konnte nicht durchgeführt werden.")

        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten des Verkaufs: {str(e)}")
            self.show_error("Ein unerwarteter Fehler ist aufgetreten.")

    def show_error(self, message):
        """Zeigt eine Fehlermeldung in einem Dialog an"""
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
                text=ERROR_DIALOG_TITLE,
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
        """Aktualisiert die Hintergrundfarbe der Zeile basierend auf Index und Theme"""
        is_dark = self.theme_cls.theme_style == "Dark"
        is_even = self.index % 2 == 0

        if is_dark:
            self.md_bg_color = [0.2, 0.2, 0.2, 1] if is_even else [0.15, 0.15, 0.15, 1]
        else:
            self.md_bg_color = [1, 1, 1, 1] if is_even else [0.85, 0.85, 0.85, 1]


class AusruestungWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Ausrüstung.
    Hauptkomponente der View im MVC-Pattern.
    """
    kategorien = ListProperty([])
    current_sort_option = StringProperty(DEFAULT_SORT_OPTION)
    sort_order = StringProperty(DEFAULT_SORT_ORDER)
    only_owned_items = BooleanProperty(False)  # Neue Property für den Filter "Nur vorhandene"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_controller()
        self.menu = None
        Clock.schedule_once(self.post_init, 0)

    def _initialize_controller(self):
        """Initialisiert die Verbindung zum Controller"""
        app = MDApp.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None
        if not self.controller:
            Logger.error("AusruestungWidget: Controller nicht gefunden")

    def toggle_only_owned_items(self, value):
        """
        Schaltet den Filter für 'Nur vorhandene Gegenstände' um.
        Event-Handler für die Checkbox.
        """
        self.only_owned_items = value
        self.filter_ausruestung()
        Logger.debug(f"Filter 'Nur vorhandene Gegenstände' gesetzt auf: {value}")

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
        self.filter_ausruestung()

    def filter_ausruestung(self, *args):
        """
        Filtert und sortiert die Ausrüstung.
        Event-Handler für Änderungen an Filterkriterien.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.warning("AusruestungWidget: Controller oder Charakter nicht verfügbar")
            return
            
        search_term = self.ids.search_input.text.lower()
        selected_kategorie = self.ids.category_label.text.lower()

        # Ausrüstung vom Modell abrufen
        alle_ausruestung = self.controller.charakter.ausruestung
        
        # Filterliste erstellen
        filtered_data = self._filter_ausruestung_data(
            alle_ausruestung, 
            search_term, 
            selected_kategorie
        )
        
        # Sortieren
        filtered_data = self._sort_ausruestung_data(filtered_data)
        
        # Index nach Sortierung aktualisieren
        for i, item in enumerate(filtered_data):
            item['index'] = i

        # Daten an RecycleView übergeben
        self.ids.recycleview.data = filtered_data
        Logger.debug(f"Ausrüstung gefiltert und sortiert: {len(filtered_data)} Einträge")

    def _filter_ausruestung_data(self, alle_ausruestung, search_term, selected_kategorie):
        """
        Filtert die Ausrüstungsdaten nach Suchbegriff, Kategorie und ggf. Mengenflag.
        Extrahiert die Filterlogik aus filter_ausruestung.
        """
        filtered_data = []
        
        for key, ausruestung in alle_ausruestung.items():
            # Filter für "Nur vorhandene Gegenstände"
            if self.only_owned_items and ausruestung.menge <= 0:
                continue
                
            # Kategorie-Filter
            if (selected_kategorie != ALL_CATEGORIES_TEXT.lower() and 
                (ausruestung.kategorie is None or ausruestung.kategorie.lower() != selected_kategorie)):
                continue
                
            # Suchbegriff-Filter
            if search_term and not (search_term in ausruestung.name.lower() or 
                search_term in ausruestung.beschreibung.lower()):
                continue
                
            # Gegenstand zur gefilterten Liste hinzufügen
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
                
        return filtered_data

    def _sort_ausruestung_data(self, data):
        """
        Sortiert die Ausrüstungsdaten nach den aktuellen Sortierkriterien.
        Extrahiert die Sortierlogik aus filter_ausruestung.
        """
        reverse_order = (self.sort_order == 'desc')
        
        # Definiere ein Mapping von Sortieroptionen zu Schlüsselfunktionen
        sort_key_mapping = {
            'Name': lambda x: x['name'].lower(),
            'Gewicht': lambda x: x['gewicht'],
            'Kosten': lambda x: x['kosten'],
            'Menge': lambda x: x['menge'],
            'Kategorie': lambda x: x['kategorie'].lower()
        }
        
        # Wähle die passende Schlüsselfunktion und sortiere
        sort_key = sort_key_mapping.get(self.current_sort_option)
        if sort_key:
            data.sort(key=sort_key, reverse=reverse_order)
            
        return data

    def post_init(self, dt):
        """
        Initialisierung nach dem Laden des Widgets.
        Wird einmalig durch Clock.schedule_once aufgerufen.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.warning("AusruestungWidget: Controller oder Charakter nicht verfügbar")
            return
            
        # Ausrüstung vom Modell abrufen
        alle_ausruestung = self.controller.charakter.ausruestung
        Logger.debug(f"AusruestungWidget: Lade {len(alle_ausruestung)} Ausrüstungsteile")
        
        # Kategorien extrahieren
        self._update_kategorien(alle_ausruestung)
        
        # Initiale Filterung und Anzeige
        self.filter_ausruestung()

    def _update_kategorien(self, ausruestung_dict):
        """
        Aktualisiert die Liste der verfügbaren Kategorien.
        Extrahiert die Kategorie-Logik aus post_init und refresh_widget.
        """
        self.kategorien = sorted(list(set(
            ausruestung.kategorie 
            for ausruestung in ausruestung_dict.values() 
            if ausruestung.kategorie
        )))
        Logger.debug(f"AusruestungWidget: Gefundene Kategorien: {self.kategorien}")

    def refresh_widget(self):
        """
        Leert das Widget und lädt die Daten neu.
        Wird aufgerufen, wenn sich die Ausrüstung ändert.
        """
        Logger.debug("AusruestungWidget: Start refresh_widget")
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.warning("AusruestungWidget: Controller oder Charakter nicht verfügbar")
            return
            
        # Daten zurücksetzen
        self.ids.recycleview.data = []
        
        # Ausrüstung vom Modell abrufen
        alle_ausruestung = self.controller.charakter.ausruestung
        
        # Kategorien aktualisieren
        self._update_kategorien(alle_ausruestung)
        
        # Neu filtern und anzeigen
        self.filter_ausruestung()
        
        Logger.debug("AusruestungWidget: refresh_widget abgeschlossen")

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
        self.filter_ausruestung()