# views/maechte_view.py
"""
View-Komponente für Mächte und Superkräfte nach dem MVC-Pattern.
Stellt die Benutzerschnittstelle zur Anzeige und Verwaltung von Mächten bereit.
Schaltet kontextabhängig zwischen traditionellem Mächte-Modus und Superkräfte-Modus um.
"""

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty, ListProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton, MDFabButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.progressindicator import MDLinearProgressIndicator

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
from kivymd.uix.selectioncontrol import MDCheckbox

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

# Settings, die den Superkräfte-Modus aktivieren
SUPERKRAEFTE_SETTINGS = [
    "Superkräfte Kompendium",
    "Superkräfte-Kompendium",
    "Superheroes"
]


class MaechteTooltip(MDTooltip):
    """Basis-Klasse für Tooltips in der Mächte-View"""
    tooltip_text = StringProperty()


class TooltipIconButton(MaechteTooltip, MDIconButton):
    """Icon Button mit Tooltip Funktionalität"""
    icon = StringProperty()


# Bei der Factory registrieren
Factory.register('TooltipIconButton', TooltipIconButton)


# KV-Datei laden mit PyInstaller-kompatiblem Pfad
from utils.path_utils import get_application_root
import os
kv_path = os.path.join(get_application_root(), 'views', 'maechte_view.kv')
Builder.load_file(kv_path)


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
        self.bind(index=self.update_color)

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

        dialog_service = get_dialog_service()

        if dialog_service and hasattr(dialog_service, 'macht_dialog_handler'):
            dialog_service.macht_dialog_handler.show_edit_dialog(self.macht_name)
            Logger.debug("MachtItemRow: Bearbeitungsdialog erfolgreich geöffnet")
        else:
            Logger.error("MachtItemRow: Dialog Service oder macht_dialog_handler nicht verfügbar")
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

        charakter = self.controller.charakter
        if charakter.verfuegbare_maechte <= 0:
            self._show_no_powers_dialog()
            return

        if self.maechte_widget:
            self.maechte_widget._on_macht_selected(self.macht_name)
        else:
            Logger.error("MachtItemRow: MaechteWidget nicht verfügbar für Rangprüfung")
            success = self.controller.waehle_macht(self.macht_name)
            if success:
                Logger.debug(f"Macht '{self.macht_name}' ausgewählt.")
                if self.macht:
                    self.macht.ausgewaehlt = True
                    self.line_color = self._get_line_color()
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
                self.line_color = self._get_line_color()
                self.canvas.ask_update()
            self._refresh_ui()
        else:
            Logger.warning(f"Entfernen der Macht '{self.macht_name}' fehlgeschlagen.")

    def update_color(self, *args):
        """Aktualisiert die Hintergrundfarbe bei Indexänderung."""
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


class KraefteWidget(MDBoxLayout):
    """
    Kontextabhängiges Widget zur Anzeige und Verwaltung von Mächten oder Superkräften.
    Schaltet basierend auf dem aktiven Setting zwischen beiden Modi um.

    Im Mächte-Modus werden die KV-definierten UI-Kinder (Suche, Sort, RecycleView) genutzt.
    Im Superkräfte-Modus werden diese versteckt und eine SuperkraefteSubview angezeigt.
    """
    current_sort_option = StringProperty(DEFAULT_SORT_OPTION)
    sort_order = StringProperty(DEFAULT_SORT_ORDER)
    only_selected_items = BooleanProperty(False)
    current_mode = StringProperty("maechte")  # "maechte" oder "superkraefte"

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
        """Initialisiert das KraefteWidget und setzt Grundkonfiguration."""
        super().__init__(**kwargs)
        self._initialize_controller()
        self.dialog = None
        self._maechte_children = []  # Gespeicherte KV-Kinder für Moduswechsel
        self._superkraefte_view = None  # Aktive Superkräfte-View
        Clock.schedule_once(self.post_init, 0)
        Clock.schedule_once(self._check_initial_setting, 0.5)

    def _initialize_controller(self):
        """Initialisiert die Verbindung zum Controller."""
        app = MDApp.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None

        if not self.controller:
            Logger.error("KraefteWidget: Controller nicht gefunden")
        else:
            self.controller.bind(on_setting_changed=self._on_setting_changed_event)

    def _check_initial_setting(self, dt):
        """Prüft das initiale Setting und setzt den entsprechenden Modus."""
        if self.controller and hasattr(self.controller, 'charakter'):
            setting_name = getattr(self.controller.charakter, 'active_setting_name', '')
            if setting_name:
                self._switch_mode_based_on_setting(setting_name)

    def _on_setting_changed_event(self, instance, setting_name):
        """
        Callback für gebundenes on_setting_changed Event vom Controller.
        (Externe Callbacks erhalten instance als erstes Argument)
        """
        Logger.info(f"KraefteWidget: Setting geändert zu '{setting_name}'")
        self._switch_mode_based_on_setting(setting_name)

    def _switch_mode_based_on_setting(self, setting_name):
        """Schaltet zwischen Mächte- und Superkräfte-Modus basierend auf Setting."""
        new_mode = "superkraefte" if setting_name in SUPERKRAEFTE_SETTINGS else "maechte"

        if self.current_mode != new_mode:
            Logger.info(f"KraefteWidget: Wechsle von '{self.current_mode}' zu '{new_mode}'-Modus")
            self.current_mode = new_mode
            self._rebuild_view_for_mode()

    def _rebuild_view_for_mode(self):
        """Baut die View für den aktuellen Modus um."""
        try:
            if self.current_mode == "superkraefte":
                self._switch_to_superkraefte()
            else:
                self._switch_to_maechte()
        except Exception as e:
            Logger.error(f"Fehler beim Modus-Wechsel: {e}")

    def _switch_to_superkraefte(self):
        """Wechselt in den Superkräfte-Modus: KV-Kinder verstecken, Superkräfte-View anzeigen."""
        # KV-Kinder speichern und entfernen
        if not self._maechte_children:
            self._maechte_children = list(self.children)

        for child in self._maechte_children:
            if child in self.children:
                self.remove_widget(child)

        # Superkräfte-View erstellen und hinzufügen
        if self._superkraefte_view is None:
            self._superkraefte_view = SuperkraefteSubview(controller=self.controller)
        self.add_widget(self._superkraefte_view)
        Logger.info("KraefteWidget: Superkräfte-View aktiviert")

    def _switch_to_maechte(self):
        """Wechselt in den Mächte-Modus: Superkräfte-View entfernen, KV-Kinder wiederherstellen."""
        # Superkräfte-View entfernen
        if self._superkraefte_view and self._superkraefte_view in self.children:
            self.remove_widget(self._superkraefte_view)
            self._superkraefte_view = None

        # KV-Kinder wiederherstellen (in umgekehrter Reihenfolge, da Kivy children reversed speichert)
        if self._maechte_children:
            for child in reversed(self._maechte_children):
                if child not in self.children:
                    self.add_widget(child)
            self._maechte_children = []

        Logger.info("KraefteWidget: Mächte-View aktiviert")

    # ==================== MÄCHTE-FUNKTIONALITÄT ====================

    def toggle_only_selected_items(self):
        """
        Schaltet den Filter für 'Nur ausgewählte Elemente' um.
        Event-Handler für den Button (Android Checkbox Workaround).
        """
        self.only_selected_items = not self.only_selected_items
        self.filter_maechte()
        Logger.debug(f"Filter 'Nur ausgewählte Mächte' gesetzt auf: {self.only_selected_items}")

    def update_sort_option(self, option):
        """
        Aktualisiert die Sortieroptionen und -reihenfolge.
        Event-Handler für die Sortier-Buttons.
        """
        if self.current_sort_option == option:
            self.sort_order = 'desc' if self.sort_order == 'asc' else 'asc'
        else:
            self.current_sort_option = option
            self.sort_order = 'asc'

        Logger.debug(f"Sortierung aktualisiert: {self.current_sort_option}, {self.sort_order}")
        self.filter_maechte()

    def filter_maechte(self, *args):
        """
        Filtert und sortiert die Mächte.
        Event-Handler für Änderungen am Suchtext oder Filter.
        """
        if self.current_mode != "maechte":
            return

        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("MaechteWidget: Controller oder Charakter nicht verfügbar")
            return

        if not hasattr(self.ids, 'search_input') or not hasattr(self.ids, 'recycleview'):
            Logger.debug("MaechteWidget: IDs noch nicht verfügbar (Post-Init?)")
            return

        search_term = self.ids.search_input.text.lower()

        alle_maechte = self.controller.charakter.maechte

        filtered_data = self._filter_maechte_data(alle_maechte, search_term)
        filtered_data = self._sort_maechte_data(filtered_data)

        for i, item in enumerate(filtered_data):
            item['index'] = i

        self.ids.recycleview.data = filtered_data
        Logger.debug(f"Mächte gefiltert und sortiert: {len(filtered_data)} Einträge")

    def _filter_maechte_data(self, alle_maechte, search_term):
        """Filtert die Macht-Daten nach Suchbegriff und Auswahlstatus."""
        filtered_data = []

        for macht in alle_maechte.values():
            if self.only_selected_items and not macht.ausgewaehlt:
                continue

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
        """Sortiert die Macht-Daten nach den aktuellen Sortierkriterien."""
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
        if self.current_mode == "maechte":
            self.filter_maechte()
        Logger.debug("KraefteWidget: Post-Init abgeschlossen")

    def refresh_widget(self):
        """
        Leert das Widget und lädt die Daten neu.
        Wird aufgerufen, wenn sich die Mächte/Superkräfte ändern.
        """
        if self.current_mode == "maechte":
            if hasattr(self.ids, 'recycleview'):
                self.ids.recycleview.data = []
            self.filter_maechte()
        elif self.current_mode == "superkraefte" and self._superkraefte_view:
            if hasattr(self._superkraefte_view, 'refresh_widget'):
                self._superkraefte_view.refresh_widget()
        Logger.debug("KraefteWidget: Widget aktualisiert")

    # ==================== RANGPRÜFUNG ====================

    def _on_macht_selected(self, macht_name):
        """
        Wird aufgerufen, wenn eine Macht ausgewählt wird.
        Prüft den Rang und zeigt ggf. einen Warnhinweis an.
        """
        result = self.controller.waehle_macht(macht_name)
        if result == "needs_rang_confirmation":
            self._show_rang_warning_dialog(macht_name)
        elif result:
            Logger.debug(f"Macht '{macht_name}' erfolgreich ausgewählt")
            self.refresh_widget()
        else:
            Logger.warning(f"Fehler beim Auswählen der Macht '{macht_name}'")
            self.refresh_widget()

    def _show_rang_warning_dialog(self, macht_name):
        """Zeigt einen Dialog zur Warnung vor der Auswahl einer Macht mit höherem Rang an."""
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
        """Führt die Machtauswahl mit ignorierter Rangprüfung durch."""
        self.close_dialog()
        result = self.controller.waehle_macht(macht_name, ignore_rang_check=True)
        if result:
            Logger.info(f"Macht '{macht_name}' trotz Rangunterschied ausgewählt")
            self.refresh_widget()
        else:
            Logger.warning(f"Fehler beim Auswählen der Macht '{macht_name}' trotz ignorierter Rangprüfung.")
            self.refresh_widget()


# ==================== SUPERKRÄFTE SUB-VIEW ====================

class SuperkraefteSubview(MDBoxLayout):
    """
    Sub-View für Superkräfte.
    Implementiert die Superkräfte-UI mit Machtstufen-Header, SKP-Anzeige und Kräfte-Liste.
    """

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.orientation = "vertical"
        self.spacing = dp(10)
        self.padding = dp(10)
        Clock.schedule_once(self._setup_superkraefte_view, 0.1)

    def _setup_superkraefte_view(self, dt):
        """Setzt die Superkräfte-UI auf."""
        try:
            self._create_machtstufe_header()
            self._create_superkraefte_list()
            self._create_action_buttons()
        except Exception as e:
            Logger.error(f"Fehler beim Setup der Superkräfte-View: {e}")

    def _create_machtstufe_header(self):
        """Erstellt den Header mit Machtstufen-Info und SKP-Anzeige."""
        header_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(5),
            size_hint_y=None,
            height=dp(120),
            padding=dp(15)
        )

        # Machtstufen-Zeile
        machtstufe_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
        )

        machtstufe_label = MDLabel(
            text="Machtstufe:",
            size_hint_x=None,
            width=dp(100),
            theme_text_color="Primary"
        )

        machtstufe_value = MDLabel(
            text="III - Four-Color-Helden",
            theme_text_color="Secondary"
        )

        machtstufe_row.add_widget(machtstufe_label)
        machtstufe_row.add_widget(machtstufe_value)
        header_layout.add_widget(machtstufe_row)

        # SKP-Zeile
        skp_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
        )

        skp_label = MDLabel(
            text="SKP:",
            size_hint_x=None,
            width=dp(100),
            theme_text_color="Primary"
        )

        skp_info = MDLabel(
            text="0/45  Obergrenze: 15",
            theme_text_color="Secondary"
        )

        skp_row.add_widget(skp_label)
        skp_row.add_widget(skp_info)
        header_layout.add_widget(skp_row)

        # Fortschrittsbalken
        progress_bar = MDLinearProgressIndicator(
            value=0,
            size_hint_y=None,
            height=dp(6),
            indicator_color=[0.2, 0.8, 0.2, 1]
        )
        header_layout.add_widget(progress_bar)

        self.add_widget(header_layout)

    def _create_superkraefte_list(self):
        """Erstellt die Superkräfte-Liste."""
        list_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=1
        )

        list_header = MDLabel(
            text="Gewählte Superkräfte:",
            theme_text_color="Primary",
            font_style="Title",
            size_hint_y=None,
            height=dp(40)
        )
        list_layout.add_widget(list_header)

        # Platzhalter bis die Superkraft-Daten implementiert sind
        superkraefte_placeholder = MDLabel(
            text="Noch keine Superkräfte gewählt.\n\n"
                  "Klicke auf 'Superkraft hinzufügen' um Kräfte auszuwählen.",
            halign="center",
            theme_text_color="Secondary"
        )
        list_layout.add_widget(superkraefte_placeholder)

        self.add_widget(list_layout)

    def _create_action_buttons(self):
        """Erstellt die Action-Buttons."""
        button_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        add_kraft_button = MDButton(
            MDButtonText(text="+ Superkraft hinzufügen"),
            style="elevated",
            on_release=self._on_add_superkraft
        )

        button_row.add_widget(add_kraft_button)
        self.add_widget(button_row)

    def _on_add_superkraft(self, instance):
        """Event-Handler für 'Superkraft hinzufügen'-Button."""
        Logger.info("Superkraft hinzufügen geklickt")
        self._show_placeholder_dialog()

    def _show_placeholder_dialog(self):
        """Zeigt einen Placeholder-Dialog für Superkraft-Auswahl."""
        dialog = MDDialog(
            MDDialogHeadlineText(text="Superkraft hinzufügen"),
            MDDialogContentContainer(
                MDLabel(
                    text="Superkraft-Auswahl-Dialog\n\nHier wird die Liste aller verfügbaren Superkräfte angezeigt.",
                    halign="center"
                ),
                orientation="vertical"
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Schließen"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                )
            )
        )
        dialog.open()

    def refresh_widget(self):
        """Aktualisiert die Superkräfte-Anzeige."""
        Logger.debug("SuperkraefteSubview: refresh_widget aufgerufen")


# Rückwärtskompatibilität: MaechteWidget als Alias für KraefteWidget
MaechteWidget = KraefteWidget
