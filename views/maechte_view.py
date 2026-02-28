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


class TooltipFabButton(MaechteTooltip, MDFabButton):
    """Fab Button mit Tooltip Funktionalität"""
    icon = StringProperty()


# Bei der Factory registrieren
Factory.register('TooltipIconButton', TooltipIconButton)
Factory.register('TooltipFabButton', TooltipFabButton)


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
    is_filter_expanded = BooleanProperty(True)
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
        Clock.schedule_once(self._init_filter_collapsed_state, 0.1)

    def toggle_filter_panel(self):
        """Klappt den Filter-Bereich auf oder zu"""
        container = self.ids.get('filter_container')
        if not container:
            return
        if self.is_filter_expanded:
            container.height = 0
            container.opacity = 0
            container.disabled = True
            self.is_filter_expanded = False
        else:
            container.height = dp(120)
            container.opacity = 1
            container.disabled = False
            self.is_filter_expanded = True

    def _init_filter_collapsed_state(self, dt):
        """Im mobilen Modus Filter eingeklappt starten"""
        try:
            from services.service_container import service_container
            config_service = service_container.get_config_service()
            if config_service and config_service.get('mobile_modus', False):
                self.toggle_filter_panel()
        except Exception as e:
            Logger.error(f"Fehler bei Filter-Collapse-Init: {e}")

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
            self._update_tab_text(new_mode)

    def _update_tab_text(self, mode):
        """Aktualisiert den Tab-Text basierend auf dem Modus."""
        try:
            app = MDApp.get_running_app()
            new_text = "Kräfte" if mode == "superkraefte" else "Mächte"
            if hasattr(app, 'tab_items'):
                for tab_item in app.tab_items:
                    for child in tab_item.children:
                        if hasattr(child, 'text') and child.text in ("Mächte", "Kräfte"):
                            child.text = new_text
                            Logger.info(f"KraefteWidget: Tab-Text zu '{new_text}' geändert")
                            return
        except Exception as e:
            Logger.warning(f"Fehler beim Ändern des Tab-Textes: {e}")

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
    Zeigt Machtstufen-Header, SKP-Anzeige, gewählte Kräfte-Liste und Action-Buttons.
    Verwendet den SuperkraftDialogHandler für Auswahl/Konfiguration.
    """

    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.orientation = "vertical"
        self.spacing = dp(10)
        self.padding = dp(10)

        # UI-Referenzen
        self._machtstufe_label = None
        self._skp_label = None
        self._progress_bar = None
        self._krafte_list_box = None
        self._placeholder_label = None

        # Dialog-Handler
        self._dialog_handler = None

        Clock.schedule_once(self._setup_superkraefte_view, 0.1)

    @property
    def dialog_handler(self):
        """Lazy-Init des DialogHandlers."""
        if self._dialog_handler is None:
            from views.superkraft_popup import SuperkraftDialogHandler
            self._dialog_handler = SuperkraftDialogHandler(self.controller)
        return self._dialog_handler

    def _get_charakter(self):
        """Gibt das Charakter-Objekt zurück."""
        if self.controller and hasattr(self.controller, 'charakter'):
            return self.controller.charakter
        return None

    def _setup_superkraefte_view(self, dt):
        """Setzt die Superkräfte-UI auf."""
        try:
            self._create_machtstufe_header()
            self._create_superkraefte_list()
            self._create_action_buttons()
            self.refresh_widget()
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

        self._machtstufe_label = MDButton(
            MDButtonText(text="III - Four-Color-Helden"),
            style="text",
            on_release=self._on_machtstufe_click
        )

        machtstufe_row.add_widget(machtstufe_label)
        machtstufe_row.add_widget(self._machtstufe_label)
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

        self._skp_label = MDLabel(
            text="0/45  Obergrenze: 15",
            theme_text_color="Secondary"
        )

        skp_row.add_widget(skp_label)
        skp_row.add_widget(self._skp_label)
        header_layout.add_widget(skp_row)

        # Fortschrittsbalken
        self._progress_bar = MDLinearProgressIndicator(
            value=0,
            size_hint_y=None,
            height=dp(6),
            indicator_color=[0.2, 0.8, 0.2, 1]
        )
        header_layout.add_widget(self._progress_bar)

        self.add_widget(header_layout)

    def _create_superkraefte_list(self):
        """Erstellt den scrollbaren Bereich für gewählte Superkräfte."""
        from kivymd.uix.scrollview import MDScrollView

        list_header = MDLabel(
            text="Gewählte Superkräfte:",
            theme_text_color="Primary",
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(32)
        )
        self.add_widget(list_header)

        scroll = MDScrollView(size_hint_y=1)
        self._krafte_list_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
            padding=(0, 0, 0, dp(8)),
        )
        self._krafte_list_box.bind(minimum_height=self._krafte_list_box.setter('height'))

        # Platzhalter
        self._placeholder_label = MDLabel(
            text="Noch keine Superkräfte gewählt.\n\n"
                 "Klicke auf '+ Superkraft hinzufügen' um Kräfte auszuwählen.",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(100),
        )
        self._krafte_list_box.add_widget(self._placeholder_label)

        scroll.add_widget(self._krafte_list_box)
        self.add_widget(scroll)

    def _create_action_buttons(self):
        """Erstellt die Action-Buttons."""
        button_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        add_button = MDButton(
            MDButtonText(text="+ Superkraft hinzufügen"),
            style="elevated",
            on_release=self._on_add_superkraft
        )

        button_row.add_widget(add_button)
        self.add_widget(button_row)

    # ==================== EVENT HANDLER ====================

    def _on_add_superkraft(self, instance):
        """Öffnet den Superkraft-Auswahl-Dialog."""
        Logger.info("SuperkraefteSubview: Superkraft hinzufügen")
        self.dialog_handler.show_auswahl_dialog()

    def _on_machtstufe_click(self, instance):
        """Öffnet den Machtstufe-Auswahl-Dialog."""
        Logger.info("SuperkraefteSubview: Machtstufe ändern")
        self.dialog_handler.show_machtstufe_dialog()

    def _on_kraft_entfernen(self, kraft_name):
        """Öffnet den Entfernen-Dialog für eine Superkraft."""
        Logger.info(f"SuperkraefteSubview: Superkraft '{kraft_name}' entfernen")
        self.dialog_handler.show_entfernen_dialog(kraft_name)

    # ==================== REFRESH ====================

    def refresh_widget(self):
        """Aktualisiert die komplette Superkräfte-Anzeige mit aktuellen Charakter-Daten."""
        Logger.debug("SuperkraefteSubview: refresh_widget")
        charakter = self._get_charakter()
        if not charakter:
            return

        self._update_header(charakter)
        self._update_krafte_list(charakter)

    def _update_header(self, charakter):
        """Aktualisiert Machtstufe, SKP und Fortschrittsbalken."""
        stufe = getattr(charakter, 'machtstufe', 'III')
        skp_gesamt = getattr(charakter, 'superkraft_punkte_gesamt', 0)
        skp_verbraucht = getattr(charakter, 'superkraft_punkte_verbraucht', 0)
        obergrenze = getattr(charakter, 'kraftobergrenze', 15)

        # Machtstufen-Namen
        stufen_namen = {
            "I": "I - Pulp-Helden",
            "II": "II - Straßenkämpfer",
            "III": "III - Four-Color-Helden",
            "IV": "IV - Schwere Kaliber",
            "V": "V - Kosmische Beschützer",
        }
        stufen_text = stufen_namen.get(stufe, stufe)

        if self._machtstufe_label:
            # MDButton enthält MDButtonText als Kind
            for child in self._machtstufe_label.children:
                if hasattr(child, 'text'):
                    child.text = stufen_text
                    break

        if self._skp_label:
            verbleibend = skp_gesamt - skp_verbraucht
            self._skp_label.text = (
                f"{skp_verbraucht}/{skp_gesamt}  "
                f"Verfügbar: {verbleibend}  "
                f"Obergrenze: {obergrenze}"
            )

        if self._progress_bar:
            if skp_gesamt > 0:
                prozent = min(100, (skp_verbraucht / skp_gesamt) * 100)
                self._progress_bar.value = prozent
                # Farbe je nach Auslastung
                if prozent > 90:
                    self._progress_bar.indicator_color = [0.8, 0.2, 0.2, 1]
                elif prozent > 70:
                    self._progress_bar.indicator_color = [0.8, 0.8, 0.2, 1]
                else:
                    self._progress_bar.indicator_color = [0.2, 0.8, 0.2, 1]
            else:
                self._progress_bar.value = 0

    def _update_krafte_list(self, charakter):
        """Aktualisiert die Liste der gewählten Superkräfte."""
        if not self._krafte_list_box:
            return

        self._krafte_list_box.clear_widgets()

        import functions.superkraft_funktionen as skf
        ausgewaehlt = skf.ausgewaehlte_superkraefte(charakter)

        if not ausgewaehlt:
            # Platzhalter anzeigen
            self._placeholder_label = MDLabel(
                text="Noch keine Superkräfte gewählt.\n\n"
                     "Klicke auf '+ Superkraft hinzufügen' um Kräfte auszuwählen.",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(100),
            )
            self._krafte_list_box.add_widget(self._placeholder_label)
            return

        for kraft in sorted(ausgewaehlt, key=lambda k: k.name):
            kraft_card = self._create_kraft_card(kraft)
            self._krafte_list_box.add_widget(kraft_card)

    def _create_kraft_card(self, kraft):
        """Erstellt eine Card für eine gewählte Superkraft."""
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            padding=dp(12),
            style="outlined",
        )

        # Obere Zeile: Name + Kosten + Entfernen-Button
        top_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
        )

        name_label = MDLabel(
            text=kraft.name,
            theme_text_color="Primary",
            font_style="Title",
            role="small",
            size_hint_x=0.6,
        )

        kosten_label = MDLabel(
            text=f"{kraft.gesamt_kosten} SKP",
            theme_text_color="Secondary",
            halign="right",
            size_hint_x=0.25,
        )

        entfernen_btn = MDIconButton(
            icon="close-circle-outline",
            style="standard",
            on_release=lambda x, n=kraft.name: self._on_kraft_entfernen(n),
        )

        top_row.add_widget(name_label)
        top_row.add_widget(kosten_label)
        top_row.add_widget(entfernen_btn)
        card.add_widget(top_row)

        # Untere Zeile: Modifikatoren
        if kraft.gewaehlte_modifikatoren:
            mod_namen = [m.name for m in kraft.gewaehlte_modifikatoren]
            mod_text = "Mods: " + ", ".join(mod_namen)
        else:
            mod_text = kraft.beschreibung[:80] + ("..." if len(kraft.beschreibung) > 80 else "")

        detail_label = MDLabel(
            text=mod_text,
            theme_text_color="Secondary",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(24),
        )
        card.add_widget(detail_label)

        return card


# Rückwärtskompatibilität: MaechteWidget als Alias für KraefteWidget
MaechteWidget = KraefteWidget
