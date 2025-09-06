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

# Import für Dialog Service
from services.service_container import get_dialog_service

# Konstanten
DEFAULT_SORT_OPTION = 'Name'
DEFAULT_SORT_ORDER = 'asc'
ALL_CATEGORIES_TEXT = 'Alle Kategorien'
DEFAULT_ROW_HEIGHT = dp(100)
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
        self._set_background_color()  # THEME-FIX: Hintergrundfarbe setzen

    def _set_background_color(self):
        """Setzt die Hintergrundfarbe basierend auf dem aktuellen Theme"""
        app = MDApp.get_running_app()
        if app and hasattr(app, 'theme_cls'):
            theme_cls = app.theme_cls
            
            # Theme-abhängige Farben für alternierende Zeilen
            if theme_cls.theme_style == "Light":
                # Helle Theme-Farben
                if self.index % 2 == 0:
                    self.md_bg_color = [0.95, 0.95, 0.95, 1]  # Sehr helles Grau
                else:
                    self.md_bg_color = [0.98, 0.98, 0.98, 1]  # Noch heller
            else:
                # Dunkle Theme-Farben (bisherige Farben)
                if self.index % 2 == 0:
                    self.md_bg_color = [0.2, 0.2, 0.2, 1]
                else:
                    self.md_bg_color = [0.15, 0.15, 0.15, 1]
    
    def on_index(self, instance, value):
        """Wird aufgerufen wenn sich der Index ändert - THEME-FIX"""
        self._set_background_color()

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
        
        # Dialog Service über Service Container holen
        dialog_service = get_dialog_service()
        
        if dialog_service:
            # Bestimme den Typ der Ausrüstung und rufe den entsprechenden Handler auf
            controller = self._get_controller()
            if controller and self.name in controller.charakter.ausruestung:
                item = controller.charakter.ausruestung[self.name]
                
                # Typ-spezifische Bearbeitung
                if isinstance(item, Waffe):
                    if hasattr(dialog_service, 'waffe_dialog_handler'):
                        dialog_service.waffe_dialog_handler.show_edit_dialog(self.name)
                        Logger.debug("AusruestungItemRow: Waffe-Bearbeitungsdialog erfolgreich geöffnet")
                    else:
                        Logger.error("AusruestungItemRow: waffe_dialog_handler nicht gefunden")
                elif isinstance(item, Ruestung):
                    if hasattr(dialog_service, 'ruestung_dialog_handler'):
                        dialog_service.ruestung_dialog_handler.show_edit_dialog(self.name)
                        Logger.debug("AusruestungItemRow: Rüstung-Bearbeitungsdialog erfolgreich geöffnet")
                    else:
                        Logger.error("AusruestungItemRow: ruestung_dialog_handler nicht gefunden")
                elif isinstance(item, Schild):
                    if hasattr(dialog_service, 'schild_dialog_handler'):
                        dialog_service.schild_dialog_handler.show_edit_dialog(self.name)
                        Logger.debug("AusruestungItemRow: Schild-Bearbeitungsdialog erfolgreich geöffnet")
                    else:
                        Logger.error("AusruestungItemRow: schild_dialog_handler nicht gefunden")
                else:
                    # Allgemeine Ausrüstung
                    if hasattr(dialog_service, 'ausruestung_dialog_handler'):
                        dialog_service.ausruestung_dialog_handler.show_edit_dialog(self.name)
                        Logger.debug("AusruestungItemRow: Ausrüstung-Bearbeitungsdialog erfolgreich geöffnet")
                    else:
                        Logger.error("AusruestungItemRow: ausruestung_dialog_handler nicht gefunden")
            else:
                Logger.error(f"AusruestungItemRow: Ausrüstung '{self.name}' nicht gefunden")
                if dialog_service:
                    dialog_service.show_error_dialog(f"Ausrüstung '{self.name}' nicht gefunden.")
        else:
            Logger.error("AusruestungItemRow: Dialog Service nicht verfügbar")
            # Fallback-Fehlermeldung
            self.show_error("Der Bearbeitungsdialog konnte nicht geöffnet werden.")

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
            
            # Vermögen vor dem Kauf speichern für Verifikation
            vermoegen_vorher = controller.charakter.vermoegen
            
            success = controller.kaufen_ausruestung(
                self.name,
                anzahl=anzahl,
                preis_pro_stueck=preis
            )
            
            # Vermögen nach dem Kauf prüfen
            vermoegen_nachher = controller.charakter.vermoegen
            expected_cost = (preis or self.kosten) * anzahl
            tatsaechlich_gekauft = (vermoegen_vorher - vermoegen_nachher) == expected_cost

            if success or tatsaechlich_gekauft:
                # Kauf war erfolgreich (entweder Controller sagt ja, oder Vermögen hat sich korrekt geändert)
                self.dialog.dismiss()
                self._refresh_ui()
            else:
                # Kauf ist wirklich fehlgeschlagen - Vermögen unverändert
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
            
            # Vermögen vor dem Verkauf speichern für Verifikation
            vermoegen_vorher = controller.charakter.vermoegen
            
            success = controller.verkaufen_ausruestung(
                self.name,
                anzahl=anzahl,
                preis_pro_stueck=preis
            )
            
            # Vermögen nach dem Verkauf prüfen
            vermoegen_nachher = controller.charakter.vermoegen
            default_verkaufspreis = (self.kosten * 0.5) if hasattr(self, 'kosten') else 0
            expected_income = (preis or default_verkaufspreis) * anzahl
            tatsaechlich_verkauft = (vermoegen_nachher - vermoegen_vorher) == expected_income

            if success or tatsaechlich_verkauft:
                # Verkauf war erfolgreich (entweder Controller sagt ja, oder Vermögen hat sich korrekt geändert)
                self.dialog.dismiss()
                self._refresh_ui()
            else:
                # Verkauf ist wirklich fehlgeschlagen
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

    def show_full_description(self):
        """Zeigt die vollständige Beschreibung der Ausrüstung in einem Dialog an."""
        if not self.beschreibung:
            return
            
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        # Ausrüstungs-Name als Überschrift
        title_label = MDLabel(
            text=f"[b]{self.name}[/b]",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Primary",
            halign="left",
            valign="middle",
            markup=True
        )
        content.add_widget(title_label)
        
        # Vollständige Beschreibung
        desc_label = MDLabel(
            text=self.beschreibung,
            size_hint_y=None,
            theme_text_color="Secondary",
            halign="left",
            valign="top",
            text_size=(dp(400), None),
            markup=True
        )
        desc_label.bind(texture_size=desc_label.setter('size'))
        content.add_widget(desc_label)
        
        description_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Ausrüstung-Beschreibung",
            ),
            MDDialogContentContainer(
                content,
                orientation="vertical",
                padding=dp(0),
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Schließen"),
                    style="text",
                    on_release=lambda x: description_dialog.dismiss(),
                ),
                spacing="8dp",
            ),
        )
        description_dialog.open()


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
                #Logger.debug(f"Verarbeite Item: {name}, Typ: {type(item).__name__}")
                
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
                
                # # Debug-Ausgabe für gefilterte Items
                # if len(filtered_items) < 5:  # Nur die ersten paar für bessere Übersicht
                #     Logger.debug(f"Gefiltert: {item_data['name']}, Kategorie: {item_data['kategorie']}")
            
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
        #self._debug_ausruestung()
        
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

# KV-String mit Theme-Fix - HAUPTÄNDERUNG: md_bg_color entfernt und theme_text_color hinzugefügt!
# KV-Datei laden
# KV-Datei laden mit PyInstaller-kompatiblem Pfad
from utils.path_utils import get_application_root
import os
kv_path = os.path.join(get_application_root(), 'views', 'ausruestung_view.kv')
Builder.load_file(kv_path)