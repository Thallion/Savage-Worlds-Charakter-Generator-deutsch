# ausruestung_view.py

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty, BooleanProperty, DictProperty
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

# Wichtig: Importe für die Typprüfung
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild

# Konstanten
DEFAULT_SORT_OPTION = 'Name'
DEFAULT_SORT_ORDER = 'asc'
ALL_CATEGORIES_TEXT = 'Alle Kategorien'
DEFAULT_ROW_HEIGHT = dp(70)
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
    beschreibung = StringProperty("")
    details = StringProperty("")  # Weitere Details

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def _get_controller(self):
        """Hilfsmethode zum Abrufen des Controllers"""
        app = MDApp.get_running_app()
        return app.controller if hasattr(app, 'controller') else None

    def _refresh_ui(self):
        """Aktualisiert die UI nach einer Transaktion"""
        parent_widget = self.get_root_ausruestung_widget()
        if parent_widget:
            Clock.schedule_once(lambda dt: parent_widget.refresh_widget(), 0)
            return
            
        # Fallbacks
        app = MDApp.get_running_app()
        if hasattr(app, 'root') and hasattr(app.root, 'refresh_current_tab'):
            app.root.refresh_current_tab()
        elif hasattr(app, 'get_widget_by_tab_text'):
            widget = app.get_widget_by_tab_text('Ausrüstung', 'ausruestung_widget')
            if widget:
                Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)

    def get_root_ausruestung_widget(self):
        """Findet das übergeordnete AusruestungWidget"""
        current = self.parent
        while current:
            if isinstance(current, AusruestungWidget):
                return current
                
            if hasattr(current, 'parent_view') and current.parent_view:
                return current.parent_view
                
            current = current.parent
        
        # Alternative Suche
        app = MDApp.get_running_app()
        if hasattr(app, 'root') and hasattr(app.root, 'ids'):
            if hasattr(app.root.ids, 'ausruestung_widget'):
                return app.root.ids.ausruestung_widget
        
        return None
        
    def kaufen_ausruestung(self):
        """Zeigt einen Dialog zum Kaufen an"""
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
        """Zeigt einen Dialog zum Verkaufen an"""
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

    def bearbeite_ausruestung(self):
        """Öffnet den Bearbeitungsdialog für das Ausrüstungsteil."""
        Logger.debug(f"AusruestungItemRow: Bearbeite Ausrüstung '{self.name}'")
        
        app = MDApp.get_running_app()
        if hasattr(app, 'einstellungen_widget'):
            einstellungen_widget = app.einstellungen_widget
            
            # Bestimme den Typ der Ausrüstung und rufe den entsprechenden Handler auf
            controller = self._get_controller()
            if controller and self.name in controller.charakter.ausruestung:
                item = controller.charakter.ausruestung[self.name]
                
                # Typ-spezifische Bearbeitung
                from models.waffe import Waffe
                from models.ruestung import Ruestung
                from models.schild import Schild
                
                if isinstance(item, Waffe):
                    if hasattr(einstellungen_widget, 'waffe_dialog_handler'):
                        einstellungen_widget.waffe_dialog_handler.show_edit_dialog(self.name)
                    else:
                        Logger.error("AusruestungItemRow: waffe_dialog_handler nicht gefunden")
                elif isinstance(item, Ruestung):
                    if hasattr(einstellungen_widget, 'ruestung_dialog_handler'):
                        einstellungen_widget.ruestung_dialog_handler.show_edit_dialog(self.name)
                    else:
                        Logger.error("AusruestungItemRow: ruestung_dialog_handler nicht gefunden")
                elif isinstance(item, Schild):
                    if hasattr(einstellungen_widget, 'schild_dialog_handler'):
                        einstellungen_widget.schild_dialog_handler.show_edit_dialog(self.name)
                    else:
                        Logger.error("AusruestungItemRow: schild_dialog_handler nicht gefunden")
                else:
                    # Allgemeine Ausrüstung
                    if hasattr(einstellungen_widget, 'ausruestung_dialog_handler'):
                        einstellungen_widget.ausruestung_dialog_handler.show_edit_dialog(self.name)
                    else:
                        Logger.error("AusruestungItemRow: ausruestung_dialog_handler nicht gefunden")
            else:
                Logger.error(f"AusruestungItemRow: Ausrüstung '{self.name}' nicht gefunden")
        else:
            Logger.error("AusruestungItemRow: einstellungen_widget nicht gefunden")

    def _show_transaction_dialog(self, title, content, action_text, action_handler):
        """Zeigt einen Transaktionsdialog an"""
        self.dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content, orientation="vertical"),
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
        """Verarbeitet den Kauf"""
        try:
            is_valid, error_message = content.validate()
            if not is_valid:
                self.show_error(error_message)
                return

            anzahl, preis = content.get_values()
            
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
                self.show_error(
                    f"Nicht genügend Geld vorhanden für den Kauf von {anzahl}x {self.name}.",
                    "Nicht genügend Geld"
                )

        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten des Kaufs: {str(e)}")
            self.show_error("Ein unerwarteter Fehler ist aufgetreten.")

    def _handle_verkauf_dialog(self, content):
        """Verarbeitet den Verkauf"""
        try:
            is_valid, error_message = content.validate()
            if not is_valid:
                self.show_error(error_message)
                return

            anzahl, preis = content.get_values()
            
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

        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten des Verkaufs: {str(e)}")
            self.show_error("Ein unerwarteter Fehler ist aufgetreten.")

    def show_error(self, message, title=ERROR_DIALOG_TITLE):
        """Zeigt einen Fehlerdialog an"""
        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            padding="12dp",
            adaptive_height=True
        )
        
        error_label = MDLabel(
            text=message,
            theme_text_color="Error",
            size_hint_y=None,
            height=dp(80),
            halign="left",
            valign="middle"
        )
        content.add_widget(error_label)

        error_dialog = MDDialog(
            MDDialogHeadlineText(
                text=title,
            ),
            MDDialogContentContainer(
                content,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Schließen"),
                    style="text",
                    on_release=lambda x: error_dialog.dismiss(),
                ),
                spacing="8dp",
            ),
        )
        error_dialog.open()


class DialogContentBase(MDBoxLayout):
    """Basis-Klasse für Dialog-Inhalte"""
    def __init__(self, name, preis, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = "12dp"
        self.padding = "12dp"
        self.size_hint_y = None
        self.height = DIALOG_HEIGHT
        
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


class AusruestungWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Ausrüstung.
    """
    kategorien = ListProperty([])
    current_sort_option = StringProperty(DEFAULT_SORT_OPTION)
    sort_order = StringProperty(DEFAULT_SORT_ORDER)
    only_owned_items = BooleanProperty(False)

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
        """Schaltet den Filter für vorhandene Gegenstände um"""
        self.only_owned_items = value
        self.filter_ausruestung()

    def update_sort_option(self, option):
        """Aktualisiert die Sortieroptionen"""
        if self.current_sort_option == option:
            self.sort_order = 'desc' if self.sort_order == 'asc' else 'asc'
        else:
            self.current_sort_option = option
            self.sort_order = 'asc'

        self.filter_ausruestung()

    def filter_ausruestung(self, *args):
        """Filtert und sortiert die Ausrüstungsgegenstände"""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            self.set_debug_message("Controller oder Charakter nicht verfügbar")
            return
            
        search_term = self.ids.search_input.text.lower()
        selected_kategorie = self.ids.category_label.text.lower()

        # Ausrüstung vom Modell abrufen
        alle_ausruestung = self.controller.charakter.ausruestung
        
        # Logging für Debugging
        Logger.debug(f"Ausrüstung filtern: {len(alle_ausruestung)} Gegenstände insgesamt")
        
        if not alle_ausruestung:
            self.set_debug_message("Keine Ausrüstungsgegenstände vorhanden!")
            self.ids.recycleview.data = []
            return

        try:
            # Daten filtern
            filtered_items = []
            
            for name, item in alle_ausruestung.items():
                # Debug-Ausgabe für jedes Item
                Logger.debug(f"Verarbeite Item: {name}, Typ: {type(item).__name__}")
                
                # Filter: Nur vorhandene Gegenstände
                if self.only_owned_items and getattr(item, 'menge', 0) <= 0:
                    continue
                    
                # Filter: Kategorie
                if selected_kategorie != ALL_CATEGORIES_TEXT.lower():
                    item_kategorie = getattr(item, 'kategorie', '').lower()
                    if not item_kategorie or item_kategorie != selected_kategorie:
                        continue
                    
                # Filter: Suchbegriff
                if search_term:
                    name_match = search_term in name.lower()
                    beschreibung = getattr(item, 'beschreibung', '')
                    beschreibung_match = search_term in beschreibung.lower() if beschreibung else False
                    if not (name_match or beschreibung_match):
                        continue
                
                # Extrahiere detaillierte Informationen je nach Ausrüstungstyp
                details = self._get_detail_text(item)
                
                # RecycleView-Zeilendaten erstellen
                item_data = {
                    'viewclass': 'AusruestungItemRow',
                    'index': len(filtered_items),
                    'name': name,
                    'kategorie': getattr(item, 'kategorie', 'Unbekannt'),
                    'gewicht': getattr(item, 'gewicht', 0),
                    'kosten': getattr(item, 'kosten', 0),
                    'menge': getattr(item, 'menge', 0),
                    'waehrungseinheit': self.controller.charakter.waehrungseinheit,
                    'beschreibung': getattr(item, 'beschreibung', ''),
                    'details': details
                }
                
                filtered_items.append(item_data)
                
                # Debug-Ausgabe für gefilterte Items
                if len(filtered_items) < 5:  # Nur die ersten paar für bessere Übersicht
                    Logger.debug(f"Gefiltert: {item_data['name']}, Kategorie: {item_data['kategorie']}")
            
            # Sortieren
            self._sort_items(filtered_items)
            
            # Index neu setzen (wichtig für Streifenmuster)
            for i, item in enumerate(filtered_items):
                item['index'] = i
            
            # Debug-Ausgabe vor dem Setzen der Daten
            Logger.debug(f"Setze {len(filtered_items)} Gegenstände in die RecycleView")
            
            # RecycleView vollständig leeren und neu befüllen
            self.ids.recycleview.data = []
            self.ids.recycleview.data = filtered_items
            
            # Debug-Info
            if not filtered_items:
                self.set_debug_message(f"Keine Ergebnisse für Suche: '{search_term}', Kategorie: '{selected_kategorie}'")
            else:
                self.clear_debug_message()
                
            Logger.debug(f"Ausrüstung gefiltert: {len(filtered_items)} Ergebnisse")
            
        except Exception as e:
            Logger.error(f"Fehler beim Filtern der Ausrüstung: {str(e)}", exc_info=True)
            self.set_debug_message(f"Fehler beim Filtern: {str(e)}")

    def _get_detail_text(self, ausruestung):
        """Extrahiert spezifische Details je nach Ausrüstungstyp"""
        details = []
        
        try:
            # Sicherere Typprüfung
            is_waffe = 'typ' in dir(ausruestung) and 'mindeststaerke' in dir(ausruestung) and not ('torso' in dir(ausruestung))
            is_ruestung = 'torso' in dir(ausruestung) and 'arme' in dir(ausruestung)
            is_schild = 'parade' in dir(ausruestung) and 'deckung' in dir(ausruestung)
            
            # Spezifische Details je nach Typ
            if is_waffe:
                typ = getattr(ausruestung, 'typ', '')
                if typ:
                    details.append(f"Typ: {typ}")
                
                mindeststaerke = getattr(ausruestung, 'mindeststaerke', '')
                if mindeststaerke:
                    details.append(f"Mindeststärke: {mindeststaerke}")
                
                if hasattr(ausruestung, 'eigenschaften'):
                    eigenschaften = getattr(ausruestung, 'eigenschaften', {})
                    for key, value in eigenschaften.items():
                        if value and value != "-":
                            details.append(f"{key}: {value}")
            
            elif is_ruestung:
                schutz_details = []
                if getattr(ausruestung, 'torso', 0) > 0:
                    schutz_details.append(f"Torso: {ausruestung.torso}")
                if getattr(ausruestung, 'arme', 0) > 0:
                    schutz_details.append(f"Arme: {ausruestung.arme}")
                if getattr(ausruestung, 'beine', 0) > 0:
                    schutz_details.append(f"Beine: {ausruestung.beine}")
                if getattr(ausruestung, 'kopf', 0) > 0:
                    schutz_details.append(f"Kopf: {ausruestung.kopf}")
                if schutz_details:
                    details.append(" | ".join(schutz_details))
                
                mindeststaerke = getattr(ausruestung, 'mindeststaerke', '')
                if mindeststaerke:
                    details.append(f"Mindeststärke: {mindeststaerke}")
            
            elif is_schild:
                parade = getattr(ausruestung, 'parade', 0)
                if parade:
                    details.append(f"Parade: {parade}")
                
                deckung = getattr(ausruestung, 'deckung', 0)
                if deckung:
                    details.append(f"Deckung: {deckung}")
                
                mindeststaerke = getattr(ausruestung, 'mindeststaerke', '')
                if mindeststaerke:
                    details.append(f"Mindeststärke: {mindeststaerke}")
        
        except Exception as e:
            Logger.error(f"Fehler bei der Extraktion von Details: {str(e)}")
        
        return " | ".join(details)

    def _sort_items(self, data):
        """Sortiert die Ausrüstungsdaten nach aktuellem Kriterium"""
        reverse_order = (self.sort_order == 'desc')
        
        sort_key_mapping = {
            'Name': lambda x: x['name'].lower(),
            'Gewicht': lambda x: float(x['gewicht']),
            'Kosten': lambda x: float(x['kosten']),
            'Menge': lambda x: int(x['menge']),
            'Kategorie': lambda x: x['kategorie'].lower()
        }
        
        sort_key = sort_key_mapping.get(self.current_sort_option)
        if sort_key:
            data.sort(key=sort_key, reverse=reverse_order)

    def _debug_ausruestung(self):
        """Zeigt Debug-Informationen über alle Ausrüstungsgegenstände"""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.debug("Debug: Kein Controller oder Charakter verfügbar")
            return
            
        ausruestung = self.controller.charakter.ausruestung
        Logger.debug(f"Debug: {len(ausruestung)} Ausrüstungsgegenstände insgesamt")
        
        for name, item in ausruestung.items():
            Logger.debug(f"Debug Item: '{name}', Typ: {type(item).__name__}, Attribute: {dir(item)[:10]}...")

    def post_init(self, dt):
        """Initialisierung nach dem Laden des Widgets"""
        if not self.controller or not hasattr(self.controller, 'charakter'):
            self.set_debug_message("Controller oder Charakter nicht verfügbar")
            return
            
        # Debug-Ausgabe für Ausrüstung
        self._debug_ausruestung()
        
        # Ausrüstung abrufen und Kategorien aktualisieren
        alle_ausruestung = self.controller.charakter.ausruestung
        self._update_kategorien(alle_ausruestung)
        
        # Initiale Filterung
        self.filter_ausruestung()

    def _update_kategorien(self, ausruestung_dict):
        """Aktualisiert die Liste der verfügbaren Kategorien"""
        unique_kategorien = set()
        
        for ausruestung in ausruestung_dict.values():
            if hasattr(ausruestung, 'kategorie') and ausruestung.kategorie:
                unique_kategorien.add(ausruestung.kategorie)
        
        self.kategorien = sorted(list(unique_kategorien))
        Logger.debug(f"Gefundene Kategorien: {self.kategorien}")

    def refresh_widget(self):
        """Aktualisiert das Widget vollständig"""
        Logger.debug("AusruestungWidget: Starte refresh_widget")
        
        if not self.controller or not hasattr(self.controller, 'charakter'):
            self.set_debug_message("Controller oder Charakter nicht verfügbar")
            return
            
        # RecycleView-Daten komplett zurücksetzen
        if hasattr(self.ids, 'recycleview'):
            self.ids.recycleview.data = []
        
        # Ausrüstung abrufen und Kategorien aktualisieren
        alle_ausruestung = self.controller.charakter.ausruestung
        self._update_kategorien(alle_ausruestung)
        
        # Filterung erneut anwenden
        self.filter_ausruestung()

    def open_category_menu(self):
        """Öffnet das Kategorie-Auswahlmenü"""
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
        """Setzt die ausgewählte Kategorie und aktualisiert die Anzeige"""
        self.ids.category_label.text = text
        self.menu.dismiss()
        self.filter_ausruestung()

    def set_debug_message(self, message):
        """Setzt eine Debug-Nachricht im UI"""
        if hasattr(self.ids, 'debug_label'):
            self.ids.debug_label.text = message
            Logger.debug(f"Debug-Nachricht: {message}")

    def clear_debug_message(self):
        """Löscht die Debug-Nachricht"""
        if hasattr(self.ids, 'debug_label'):
            self.ids.debug_label.text = ""


# Bei der Factory registrieren
Factory.register('TooltipIconButton', TooltipIconButton)
Factory.register('AusruestungItemRow', AusruestungItemRow)

# KV-String mit korrigiertem Layout - Hauptänderung hier!
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
    md_bg_color: app.theme_cls.backgroundColor
    
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

    # Diagnostische Information anzeigen
    MDLabel:
        id: debug_label
        text: ''
        size_hint_y: None
        height: dp(30) if self.text else 0
        color: 1, 0, 0, 1
        halign: 'center'

    # Verbesserte RecycleView
    MDRecycleView:
        id: recycleview
        viewclass: 'AusruestungItemRow'
        size_hint_y: 1
        
        RecycleBoxLayout:
            id: layout
            default_size: None, dp(120)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(10)
            padding: [dp(5), dp(10), dp(15), dp(10)]

<AusruestungItemRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(120)  # Etwas höher für bessere Darstellung
    spacing: dp(5)
    padding: [dp(5), dp(5), dp(60), dp(5)]
    md_bg_color: [0.2, 0.2, 0.2, 1] if self.index % 2 == 0 else [0.15, 0.15, 0.15, 1]
    
    # Hauptcontainer für Name, Beschreibung und Details - KORRIGIERT!
    MDBoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.35
        spacing: dp(2)
        padding: [0, dp(5), 0, dp(5)]
        
        # Name - größer und fett
        MDLabel:
            text: root.name
            font_size: dp(14)
            bold: True
            size_hint_y: None
            height: dp(20)
            halign: 'left'
            valign: 'middle'
            text_size: self.width, None
            
        # Beschreibung - nur wenn vorhanden
        MDLabel:
            text: root.beschreibung if root.beschreibung else ""
            font_size: dp(11)
            theme_text_color: "Secondary"
            size_hint_y: None
            height: dp(16) if root.beschreibung else 0
            opacity: 1 if root.beschreibung else 0
            halign: 'left'
            valign: 'middle'
            text_size: self.width, None
            
        # Details - nur wenn vorhanden  
        MDLabel:
            text: root.details if root.details else ""
            font_size: dp(11)
            theme_text_color: "Secondary"
            size_hint_y: None
            height: dp(40) if root.details else 0  # Mehr Platz für Details
            opacity: 1 if root.details else 0
            halign: 'left'
            valign: 'top'
            text_size: self.width, None
            text_color: [0.8, 0.8, 0.8, 1]  # Etwas heller für bessere Lesbarkeit
    
    # Kategorie
    MDLabel:
        text: root.kategorie.capitalize() if root.kategorie else "Unbekannt"
        font_size: dp(14)
        size_hint_x: 0.12
        halign: 'left'
        valign: 'middle'
        pos_hint: {'center_y': 0.5}
        text_size: self.width, None
        shorten: True
    
    # Gewicht
    MDLabel:
        text: f"{root.gewicht} kg"
        font_size: dp(14)
        size_hint_x: 0.08
        halign: 'left'
        valign: 'middle'
        pos_hint: {'center_y': 0.5}
    
    # Kosten
    MDLabel:
        text: f"{root.kosten} {root.waehrungseinheit}"
        font_size: dp(14)
        size_hint_x: 0.12
        halign: 'left'
        valign: 'middle'
        pos_hint: {'center_y': 0.5}
        text_size: self.width, None
        shorten: True
    
    # Menge
    MDLabel:
        text: str(root.menge)
        font_size: dp(14)
        size_hint_x: 0.04
        halign: 'center'
        valign: 'middle'
        pos_hint: {'center_y': 0.5}
    
    # Buttons
    AnchorLayout:
        anchor_x: 'right'
        anchor_y: 'center'
        size_hint_x: None
        width: dp(140)
        
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint: None, None
            size: dp(140), dp(35)
            spacing: dp(5)
            
            MDButton:
                style: "filled"
                size_hint: None, None
                size: dp(35), dp(35)
                on_release: root.kaufen_ausruestung()
                MDButtonIcon:
                    icon: "plus"
            
            MDButton:
                style: "filled"
                size_hint: None, None
                size: dp(35), dp(35)
                on_release: root.verkaufen_ausruestung()
                MDButtonIcon:
                    icon: "minus"
            
            MDButton:
                style: "filled"
                size_hint: None, None
                size: dp(35), dp(35)
                on_release: root.bearbeite_ausruestung()
                MDButtonIcon:
                    icon: "pencil"
'''

# KV-String laden
Builder.load_string(KV_STRING)