# views/maechte_view.py
"""
View-Komponente für Mächte nach dem MVC-Pattern.
Stellt die Benutzerschnittstelle zur Anzeige und Verwaltung von Mächten bereit.
"""

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty, ListProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton, MDFabButton, MDButtonText

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer
)

from kivy.factory import Factory
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp

# Import für Dialog Service
from services.service_container import get_dialog_service

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


# KV-Datei laden
Builder.load_file('/home/jean/Dokumente/GitHub/Savage-Worlds-Charakter-Generator-deutsch/views/maechte_view.kv')


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

    def bearbeite_macht(self):
        """Öffnet den Bearbeitungsdialog für die Macht."""
        Logger.debug(f"MachtItemRow: Bearbeite Macht '{self.macht_name}'")
        
        # Dialog Service über Service Container holen
        dialog_service = get_dialog_service()
        
        if dialog_service and hasattr(dialog_service, 'macht_dialog_handler'):
            dialog_service.macht_dialog_handler.show_edit_dialog(self.macht_name)
            Logger.debug("MachtItemRow: Bearbeitungsdialog erfolgreich geöffnet")
        else:
            Logger.error("MachtItemRow: Dialog Service oder macht_dialog_handler nicht verfügbar")
            # Fallback-Fehlermeldung für den Benutzer
            if dialog_service:
                dialog_service.show_error_dialog(
                    "Der Bearbeitungsdialog konnte nicht geöffnet werden. "
                    "Bitte versuchen Sie es später erneut."
                )

    def waehle_macht(self):
        """
        Wählt eine Macht aus.
        Prüft vorher, ob genügend verfügbare Mächte vorhanden sind und leitet die Auswahl 
        an das Hauptwidget zur Rangprüfung weiter.
        """
        if not self.controller:
            Logger.error("MachtItemRow: Controller nicht gefunden")
            return

        # Prüfen, ob genügend verfügbare Mächte vorhanden sind
        charakter = self.controller.charakter
        if charakter.verfuegbare_maechte <= 0:
            self._show_no_powers_dialog()
            return

        # Delegation an das MaechteWidget für Rangprüfung
        if self.maechte_widget:
            self.maechte_widget._on_macht_selected(self.macht_name)
        else:
            Logger.error("MachtItemRow: MaechteWidget nicht verfügbar für Rangprüfung")
            # Fallback zur direkten Kontrollernutzung
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

    def _show_no_powers_dialog(self):
        """Zeigt einen Dialog an, wenn keine verfügbaren Mächte mehr vorhanden sind."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        warning_label = MDLabel(
            text="Keine verfügbaren Mächte mehr zum Auswählen! Du musst erst weitere Mächte durch Talente oder Aufstiege erwerben.",
            size_hint_y=None,
            height=dp(80),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(warning_label)
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Keine Mächte verfügbar",
            ),
            MDDialogContentContainer(
                content,
                orientation="vertical",
                padding=dp(0),
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda x: self.close_dialog(),
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def close_dialog(self):
        """Schließt den Dialog."""
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()

    def show_full_description(self):
        """Zeigt die vollständige Beschreibung der Macht in einem Dialog an."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        # Macht-Name als Überschrift
        title_label = MDLabel(
            text=f"[b]{self.macht_name}[/b]",
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
                text="Macht-Beschreibung",
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
    only_selected_items = BooleanProperty(False)  # Property för den Filter

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
        self.dialog = None  # Dialog-Referenz für Rangprüfung
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
        
    # NEU HINZUGEFÜGTE METHODEN FÜR DIE RANGPRÜFUNG

    def _on_macht_selected(self, macht_name):
        """
        Wird aufgerufen, wenn eine Macht ausgewählt wird.
        Prüft den Rang und zeigt ggf. einen Warnhinweis an.
        
        Args:
            macht_name (str): Name der auszuwählenden Macht
        """
        result = self.controller.waehle_macht(macht_name)
        if result == "needs_rang_confirmation":
            self._show_rang_warning_dialog(macht_name)
        elif result:
            # Macht erfolgreich ausgewählt
            Logger.debug(f"Macht '{macht_name}' erfolgreich ausgewählt")
            self.refresh_widget()
        else:
            # Fehler beim Auswählen der Macht
            Logger.warning(f"Fehler beim Auswählen der Macht '{macht_name}'")
            self.refresh_widget()  # UI trotzdem aktualisieren

    def _show_rang_warning_dialog(self, macht_name):
        """
        Zeigt einen Dialog zur Warnung vor der Auswahl einer Macht mit höherem Rang an.
        
        Args:
            macht_name (str): Name der Macht mit Rangprüfungswarnung
        """
        macht = self.controller.charakter.maechte.get(macht_name)
        if not macht:
            Logger.error(f"Macht '{macht_name}' für Dialog nicht gefunden.")
            return
            
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        warning_label = MDLabel(
            text=f"Die Macht '{macht_name}' (Rang: {macht.rang}) erfordert einen höheren Rang als deinen aktuellen ({self.controller.charakter.rang}). Möchtest du sie trotzdem auswählen?",
            size_hint_y=None,
            height=dp(80),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(warning_label)
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Rang-Warnung",
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
                    on_release=lambda x: self._confirm_macht_selection(macht_name),
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def close_dialog(self):
        """Schließt den Dialog und aktualisiert die UI."""
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            self.refresh_widget()
            
    def _confirm_macht_selection(self, macht_name):
        """
        Führt die Machtauswahl mit ignorierter Rangprüfung durch.
        
        Args:
            macht_name (str): Name der Macht, die trotz Rangunterschied ausgewählt werden soll
        """
        self.close_dialog()
        # Den Controller mit dem ignore_rang_check Flag aufrufen
        result = self.controller.waehle_macht(macht_name, ignore_rang_check=True)
        if result:
            # Macht erfolgreich ausgewählt
            Logger.info(f"Macht '{macht_name}' trotz Rangunterschied ausgewählt")
            self.refresh_widget()
        else:
            # Fehler beim Auswählen der Macht
            Logger.warning(f"Fehler beim Auswählen der Macht '{macht_name}' trotz ignorierter Rangprüfung.")
            self.refresh_widget()