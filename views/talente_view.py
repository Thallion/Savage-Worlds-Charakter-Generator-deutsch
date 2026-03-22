# views/talente_view.py
"""
View-Komponente für Talente nach dem MVC-Pattern.
Stellt die Benutzerschnittstelle zur Anzeige und Verwaltung von Talenten bereit.
Mit Unterstützung für Mehrfachauswahl von Talenten und Bearbeitungsfunktion.
ERWEITERT: Mit Savage Pathfinder Support für kostenlose Klassen-/Hintergrund-/Experte-Talente
"""

import time

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.menu import MDDropdownMenu
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
from kivymd.uix.selectioncontrol import MDCheckbox

# Import der Funktionen für Voraussetzungsprüfung
from functions.talent_funktionen import (
    pruefe_voraussetzungen, 
    is_talent_rang_hoeher_als_charakter, 
    NICHT_DUPLIZIERBARE_TALENTE,
    ist_savage_pathfinder_setting,
    ist_pathfinder_kostenloses_talent,
    hat_bereits_kostenloses_pathfinder_talent,
    waehle_pathfinder_kostenloses_talent
)

# Import für Dialog Service
from services.service_container import get_dialog_service

# Konstanten für bessere Lesbarkeit und Wartbarkeit
DEFAULT_SORT_OPTION = 'Name'
DEFAULT_SORT_ORDER = 'asc'
ALL_CATEGORIES_TEXT = 'Alle Kategorien'
DEFAULT_ROW_HEIGHT = dp(120)
DARK_EVEN_COLOR = [0.2, 0.2, 0.2, 1]
DARK_ODD_COLOR = [0.15, 0.15, 0.15, 1]
LIGHT_EVEN_COLOR = [1, 1, 1, 1]
LIGHT_ODD_COLOR = [0.85, 0.85, 0.85, 1]
SELECTED_LINE_COLOR = [1, 0.65, 0, 1]
UNSELECTED_LINE_COLOR = [0, 0, 0, 0]

# Rang-Mapping für Sortierung (als Konstante auf Modulebene)
RANG_MAPPING = {
    'A': 1,    # Anfänger
    'F': 2,    # Fortgeschritten
    'V': 3,    # Veteran
    'H': 4,    # Heroisch
    'L': 5,    # Legendär
    'WC': 6    # Wild Card oder spezieller Rang
}


class TalenteTooltip(MDTooltip):
    """Basis-Klasse für Tooltips in der Talente-View"""
    tooltip_text = StringProperty()


class TooltipIconButton(TalenteTooltip, MDIconButton):
    """Icon Button mit Tooltip Funktionalität"""
    icon = StringProperty()


class TooltipFabButton(TalenteTooltip, MDFabButton):
    """Fab Button mit Tooltip Funktionalität"""
    icon = StringProperty()


# Bei der Factory registrieren
Factory.register('TooltipIconButton', TooltipIconButton)
Factory.register('TooltipFabButton', TooltipFabButton)


# KV-Datei laden mit PyInstaller-kompatiblem Pfad und Mobile-Unterstützung
from utils.path_utils import get_application_root
from utils.platform_utils import is_mobile_layout
import os

_base_path = str(get_application_root())
_mobile = is_mobile_layout()
_kv_name = 'talente_view_mobile.kv' if _mobile else 'talente_view.kv'
_kv_path = os.path.join(_base_path, 'views', _kv_name)
if not os.path.exists(_kv_path):
    _kv_path = os.path.join(_base_path, 'views', 'talente_view.kv')
Builder.load_file(_kv_path)
Logger.info(f"talente_view: KV-Datei geladen: {os.path.basename(_kv_path)}")

class TalenteRecycleView(MDRecycleView):
    """RecycleView für Talente"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []  # Initialer leerer Datensatz
        
        # Debug-Ausgabe für RecycleView
        Logger.debug("TalenteRecycleView initialisiert")
        
    def update_data(self, data):
        """Aktualisiert die Daten im RecycleView"""
        # Debug-Ausgabe vor der Aktualisierung
        if data and 'controller' in data[0]:
            Logger.debug(f"TalenteRecycleView: Controller in Daten vorhanden für {len(data)} Einträge")
        else:
            Logger.error("TalenteRecycleView: Controller fehlt in den Daten!")
            
        self.data = data


class TalentItemRow(MDBoxLayout):
    """
    Einzelne Zeile in der Talente-Liste.
    Repräsentiert ein einzelnes Talent mit seinen Eigenschaften und Interaktionsmöglichkeiten.
    ERWEITERT: Mit Savage Pathfinder Support für kostenlose Talente
    """
    index = NumericProperty(0)
    name_key = StringProperty("")
    talent_name = StringProperty("")
    kategorie = StringProperty("")
    rang = StringProperty("")
    beschreibung = StringProperty("")
    voraussetzungen = StringProperty("")
    ausgewaehlt = BooleanProperty(False)
    controller = ObjectProperty(None)

    def __init__(self, **kwargs):
        """Initialisiert die TalentItemRow und bindet Property-Änderungen an entsprechende Handler."""
        super().__init__(**kwargs)
        self.bind(ausgewaehlt=self.on_ausgewaehlt_changed)
        self.bind(index=self.update_color)  # Wichtig: Farbaktualisierung bei Indexänderung
        self.dialog = None
        self.voraussetzungen_dialog = None
        self.rang_dialog = None
        self.pathfinder_dialog = None  # NEU: Dialog für kostenlose Pathfinder-Talente
        Logger.debug(f"TalentItemRow.__init__: Controller gesetzt: {self.controller is not None}")

    def _get_controller(self):
        """Hilfsmethode, um auf den Controller zuzugreifen."""
        app = MDApp.get_running_app()
        return app.controller if hasattr(app, 'controller') else None
        
    def _get_talente_widget(self):
        """Hilfsmethode, um auf das TalenteWidget zuzugreifen."""
        app = MDApp.get_running_app()
        return app.get_widget_by_tab_text('Talente', 'talente_widget')

    def _refresh_ui(self):
        """
        Aktualisiert das TalenteWidget nach einer Änderung.
        Vereinheitlichte Methode zum Aufrufen der Widget-Aktualisierung.
        """
        widget = self._get_talente_widget()
        if widget:
            Logger.debug("TalentItemRow: TalenteWidget gefunden, führe refresh aus")
            Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)
        else:
            Logger.error("TalentItemRow: TalenteWidget nicht gefunden")

    def bearbeite_talent(self):
        """Öffnet den Bearbeitungsdialog für das Talent."""
        Logger.debug(f"TalentItemRow: Bearbeite Talent '{self.talent_name}' mit Key '{self.name_key}'")
        
        # Dialog Service über Service Container holen
        dialog_service = get_dialog_service()
        if dialog_service and hasattr(dialog_service, 'talent_dialog_handler'):
            dialog_service.talent_dialog_handler.show_edit_dialog(self.name_key)
            Logger.debug("TalentItemRow: Bearbeitungsdialog erfolgreich geöffnet")
        else:
            Logger.error("TalentItemRow: Dialog Service oder talent_dialog_handler nicht verfügbar")
            # Fallback-Fehlermeldung für den Benutzer
            if dialog_service:
                dialog_service.show_error_dialog(
                    "Der Bearbeitungsdialog konnte nicht geöffnet werden. "
                    "Bitte versuchen Sie es später erneut."
                )

    def waehle_talent(self):
        """
        Wählt ein Talent aus.
        Prüft, ob das Talent duplizierbar ist und zeigt ggf. einen Dialog.
        ERWEITERT: Unterstützt kostenlose Pathfinder-Talente.
        """
        # Debounce: Verhindert Doppelauswahl durch mehrfache Touch-Events auf Android
        now = time.monotonic()
        if hasattr(self, '_last_waehle_time') and (now - self._last_waehle_time) < 0.5:
            Logger.debug("TalentItemRow: Doppelklick-Schutz aktiv, ignoriere")
            return
        self._last_waehle_time = now

        Logger.debug(f"TalentItemRow: Start waehle_talent für {self.talent_name}")
        controller = self._get_controller()
        if not controller:
            Logger.error("TalentItemRow: Controller nicht gefunden")
            return

        # Extrahiere den Basis-Namen des Talents (ohne Suffix)
        base_name = self.talent_name.split(' (#')[0] if ' (#' in self.talent_name else self.talent_name

        # Prüfen, ob das Talent bereits ausgewählt ist und nicht duplizierbar
        if self.ausgewaehlt and base_name in NICHT_DUPLIZIERBARE_TALENTE:
            self._show_not_duplicatable_dialog()
            return

        try:
            result = controller.waehle_talent(self.name_key, ignore_rang_check=False)
            
            if result == "not_duplicatable":
                self._show_not_duplicatable_dialog()
            elif result == "needs_rang_confirmation":
                self._show_rang_confirmation_dialog()
            elif result == "needs_voraussetzungen_confirmation":
                self._show_voraussetzungen_confirmation_dialog()
            elif result == "pathfinder_kostenlos_angeboten":  # NEU: Pathfinder kostenlos
                self._show_pathfinder_kostenlos_dialog()
            elif result:
                self.ausgewaehlt = True
                Logger.debug(f"TalentItemRow: {self.talent_name} erfolgreich ausgewählt")
                self._refresh_ui()
            else:
                # result == False: Keine Punkte/Aufstiege übrig
                self._show_talent_warnung()
        except Exception as e:
            Logger.error(f"Fehler beim Auswählen des Talents: {str(e)}")

    def _show_talent_warnung(self):
        """Zeigt eine Snackbar-Warnung wenn keine Punkte/Aufstiege für Talente übrig sind."""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_warning_dialog(
                    "Keine verbleibenden Aufstiege oder Handicap-Punkte übrig."
                )
        except Exception as e:
            Logger.error(f"Warnung konnte nicht angezeigt werden: {e}")

    def _show_pathfinder_kostenlos_dialog(self):
        """
        NEU: Zeigt einen Dialog für kostenlose Pathfinder-Talente an.
        """
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        # Haupttext
        info_label = MDLabel(
            text=f"Das Talent '{self.talent_name}' ist ein Klassen-, Hintergrund- oder Experte-Talent und kann in Savage Pathfinder während der Charaktererstellung kostenlos gewählt werden.",
            size_hint_y=None,
            height=dp(80),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(info_label)
        
        # Frage
        question_label = MDLabel(
            text="Möchten Sie dieses Talent kostenlos wählen oder mit den normalen Kosten (2 Handicap-Punkte oder 1 Aufstieg)?",
            size_hint_y=None,
            height=dp(60),
            theme_text_color="Primary",
            halign="left",
            valign="middle"
        )
        content.add_widget(question_label)
        
        self.pathfinder_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Kostenloses Pathfinder-Talent",
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
                    on_release=lambda x: self.pathfinder_dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Normale Kosten"),
                    style="text",
                    on_release=lambda x: self._waehle_talent_mit_kosten(),
                ),
                MDButton(
                    MDButtonText(text="Kostenlos wählen"),
                    style="text",
                    on_release=lambda x: self._waehle_talent_kostenlos(),
                ),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self.pathfinder_dialog.open()

    def _waehle_talent_kostenlos(self):
        """
        NEU: Wählt das Talent kostenlos als Pathfinder-Talent aus.
        """
        # Debounce: Verhindert Doppelauswahl durch mehrfache Touch-Events auf Android
        now = time.monotonic()
        if hasattr(self, '_last_kostenlos_time') and (now - self._last_kostenlos_time) < 0.5:
            return
        self._last_kostenlos_time = now
        self.pathfinder_dialog.dismiss()
        controller = self._get_controller()
        if controller:
            # Verwende die spezielle Pathfinder-Funktion
            result = waehle_pathfinder_kostenloses_talent(
                controller.charakter, 
                self.name_key, 
                ignore_voraussetzungen=True  # Voraussetzungen können ignoriert werden
            )
            
            if result == "needs_voraussetzungen_confirmation":
                self._show_voraussetzungen_confirmation_dialog()
            elif result == "already_used":
                self._show_error_dialog("Es wurde bereits ein kostenloses Pathfinder-Talent gewählt.")
            elif result == "not_pathfinder_category":
                self._show_error_dialog("Dieses Talent gehört nicht zu den kostenlosen Kategorien.")
            elif result:
                self.ausgewaehlt = True
                Logger.info(f"TalentItemRow: {self.talent_name} kostenlos als Pathfinder-Talent ausgewählt")
                self._refresh_ui()
            else:
                self._show_error_dialog("Das Talent konnte nicht kostenlos ausgewählt werden.")

    def _waehle_talent_mit_kosten(self):
        """
        NEU: Wählt das Talent mit normalen Kosten aus (bypassed die kostenlose Option).
        """
        # Debounce: Verhindert Doppelauswahl durch mehrfache Touch-Events auf Android
        now = time.monotonic()
        if hasattr(self, '_last_mit_kosten_time') and (now - self._last_mit_kosten_time) < 0.5:
            return
        self._last_mit_kosten_time = now
        self.pathfinder_dialog.dismiss()
        controller = self._get_controller()
        if controller:
            # Normale Talent-Auswahl durchführen, aber Rang-Check ignorieren da bereits geprüft
            if controller.charakter.verbleibende_handicap_punkte > 1.5:
                # Mit Handicap-Punkten
                from functions.talent_funktionen import talent_auswaehlen
                erfolg = talent_auswaehlen(controller.charakter, self.name_key, skip_prereq_check=False)
                if erfolg:
                    controller.charakter.verbleibende_handicap_punkte -= 2
                    self.ausgewaehlt = True
                    controller.charakter.berechne_abgeleitete_werte()
                    self._refresh_ui()
                    Logger.info(f"TalentItemRow: {self.talent_name} mit Handicap-Punkten ausgewählt")
                else:
                    self._show_error_dialog("Das Talent konnte nicht mit Handicap-Punkten ausgewählt werden.")
            elif controller.charakter.verbleibende_aufstiege > 0:
                # Mit Aufstiegen
                from functions.talent_funktionen import talent_auswaehlen
                erfolg = talent_auswaehlen(controller.charakter, self.name_key, skip_prereq_check=False)
                if erfolg:
                    controller.charakter.verbleibende_aufstiege -= 1
                    controller.charakter.update_char_gen_status()
                    self.ausgewaehlt = True
                    controller.charakter.berechne_abgeleitete_werte()
                    self._refresh_ui()
                    Logger.info(f"TalentItemRow: {self.talent_name} mit Aufstiegen ausgewählt")
                else:
                    self._show_error_dialog("Das Talent konnte nicht mit Aufstiegen ausgewählt werden.")
            else:
                self._show_error_dialog("Keine Handicap-Punkte oder Aufstiege verfügbar.")

    def _show_not_duplicatable_dialog(self):
        """Zeigt einen Dialog an, wenn ein Talent nicht mehrfach ausgewählt werden kann."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        warning_label = MDLabel(
            text=f"Das Talent '{self.talent_name}' kann nicht mehrfach ausgewählt werden.",
            size_hint_y=None,
            height=dp(60),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(warning_label)
        
        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Talent nicht duplizierbar",
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
                    on_release=lambda x: dialog.dismiss(),
                ),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        dialog.open()

    def _show_rang_confirmation_dialog(self):
        """Zeigt einen Dialog für Rang-Bestätigung."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        warning_label = MDLabel(
            text=f"Das Talent '{self.talent_name}' hat einen höheren Rang als dein Charakter. Trotzdem auswählen?",
            size_hint_y=None,
            height=dp(60),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(warning_label)
        
        self.rang_dialog = MDDialog(
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
                    on_release=lambda x: self.rang_dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Trotzdem auswählen"),
                    style="text",
                    on_release=lambda x: self._confirm_talent_with_higher_rang(),
                ),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self.rang_dialog.open()

    def _show_voraussetzungen_confirmation_dialog(self):
        """Zeigt einen Dialog für nicht erfüllte Voraussetzungen."""
        controller = self._get_controller()
        if not controller:
            return
            
        # Hole die Fehlermeldungen aus dem temporären Attribut
        fehlermeldungen = getattr(controller.charakter, 'temp_voraussetzungs_fehler', [])
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        # Haupttext
        main_label = MDLabel(
            text="Die Voraussetzungen für dieses Talent sind nicht erfüllt:",
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(main_label)
        
        # Fehlermeldungen
        for fehler in fehlermeldungen:
            fehler_label = MDLabel(
                text=f"• {fehler}",
                size_hint_y=None,
                height=dp(25),
                theme_text_color="Error",
                halign="left",
                valign="middle"
            )
            content.add_widget(fehler_label)
        
        # Frage
        frage_label = MDLabel(
            text="\nTrotzdem auswählen?",
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(frage_label)
        
        self.voraussetzungen_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Voraussetzungen nicht erfüllt",
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
                    on_release=lambda x: self.voraussetzungen_dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Trotzdem auswählen"),
                    style="text",
                    on_release=lambda x: self._confirm_talent_without_voraussetzungen(),
                ),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self.voraussetzungen_dialog.open()

    def _confirm_talent_with_higher_rang(self):
        """Bestätigt die Auswahl eines Talents mit höherem Rang."""
        # Debounce: Verhindert Doppelauswahl durch mehrfache Touch-Events auf Android
        now = time.monotonic()
        if hasattr(self, '_last_confirm_time') and (now - self._last_confirm_time) < 0.5:
            return
        self._last_confirm_time = now

        self.rang_dialog.dismiss()
        controller = self._get_controller()
        if controller:
            result = controller.waehle_talent(self.name_key, ignore_rang_check=True)
            if result == "needs_voraussetzungen_confirmation":
                self._show_voraussetzungen_confirmation_dialog()
            elif result == "pathfinder_kostenlos_angeboten":  # NEU: Kann auch nach Rang-Bestätigung auftreten
                self._show_pathfinder_kostenlos_dialog()
            elif result:
                self.ausgewaehlt = True
                self._refresh_ui()
            elif result is False:
                self._show_talent_warnung()

    def _confirm_talent_without_voraussetzungen(self):
        """Bestätigt die Auswahl eines Talents ohne erfüllte Voraussetzungen."""
        # Debounce: Verhindert Doppelauswahl durch mehrfache Touch-Events auf Android
        now = time.monotonic()
        if hasattr(self, '_last_confirm_time') and (now - self._last_confirm_time) < 0.5:
            return
        self._last_confirm_time = now

        self.voraussetzungen_dialog.dismiss()
        controller = self._get_controller()
        if controller:
            result = controller.waehle_talent(self.name_key, ignore_rang_check=True, ignore_voraussetzungen=True)
            if result:
                self.ausgewaehlt = True
                self._refresh_ui()
            elif result is False:
                self._show_talent_warnung()

    def entferne_talent(self):
        """
        Entfernt ein ausgewähltes Talent.
        Delegiert die Aktion an den Controller und aktualisiert die Ansicht.
        """
        # Debounce: Verhindert Doppelklick auf Android
        now = time.monotonic()
        if hasattr(self, '_last_entferne_time') and (now - self._last_entferne_time) < 0.5:
            return
        self._last_entferne_time = now

        Logger.debug(f"TalentItemRow: Start entferne_talent für {self.talent_name}")
        controller = self._get_controller()
        if not controller:
            Logger.error("TalentItemRow: Controller nicht gefunden")
            return

        try:
            controller.entferne_talent(self.name_key)
            self.ausgewaehlt = False
            Logger.debug(f"TalentItemRow: {self.talent_name} erfolgreich entfernt")
            self._refresh_ui()
        except Exception as e:
            Logger.error(f"Fehler beim Entfernen des Talents: {str(e)}")

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
        """Berechnet die Rahmenfarbe basierend auf dem Auswahlstatus."""
        return SELECTED_LINE_COLOR if self.ausgewaehlt else UNSELECTED_LINE_COLOR

    def on_ausgewaehlt_changed(self, instance, value):
        """Event-Handler für Änderungen am ausgewaehlt-Status."""
        Logger.debug(f"TalentItemRow: ausgewaehlt changed to {value} for {self.talent_name}")
        # Bei Änderung des Auswahlstatus auch die Umrandung aktualisieren
        self.line_color = self._get_line_color()

    def show_error_dialog(self, message):
        """
        Zeigt einen Fehlerdialog mit der angegebenen Nachricht an.
        
        Args:
            message (str): Die anzuzeigende Fehlermeldung
        """
        self._show_error_dialog(message)

    def _show_error_dialog(self, message):
        """
        Zeigt einen Fehlerdialog mit der angegebenen Nachricht an.
        
        Args:
            message (str): Die anzuzeigende Fehlermeldung
        """
        try:
            error_dialog = MDDialog(
                MDDialogHeadlineText(text="Fehler"),
                MDBoxLayout(
                    orientation="vertical",
                    spacing=dp(10),
                    padding=dp(20),
                    adaptive_height=True,
                    children=[
                        MDLabel(
                            text=message,
                            size_hint_y=None,
                            height=dp(60)
                        )
                    ]
                ),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(text="OK"),
                        style="text",
                        on_release=lambda x: error_dialog.dismiss()
                    ),
                    spacing="8dp",
                ),
                auto_dismiss=False,
            )
            error_dialog.open()
        except Exception as e:
            Logger.error(f"Fehler beim Anzeigen des Fehlerdialogs: {e}")

    def show_full_description(self):
        """Zeigt die vollständige Beschreibung in einem Dialog an."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        # Talent-Name als Überschrift
        title_label = MDLabel(
            text=f"[b]{self.talent_name}[/b]",
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
                text="Talent-Beschreibung",
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
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        description_dialog.open()

    def close_dialog(self):
        """Schließt aktive Dialoge."""
        for dialog_attr in ['dialog', 'voraussetzungen_dialog', 'rang_dialog', 'pathfinder_dialog']:
            if hasattr(self, dialog_attr) and getattr(self, dialog_attr):
                getattr(self, dialog_attr).dismiss()


class TalenteWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Talenten.
    Hauptkomponente der View im MVC-Pattern.
    """
    kategorien = ListProperty([])
    current_sort_option = StringProperty(DEFAULT_SORT_OPTION)
    sort_order = StringProperty(DEFAULT_SORT_ORDER)
    only_selected_items = BooleanProperty(False)  # Property für den Filter
    only_available_talents = BooleanProperty(False)
    is_filter_expanded = BooleanProperty(True)

    def __init__(self, **kwargs):
        """Initialisiert das TalenteWidget und setzt Grundkonfiguration."""
        super().__init__(**kwargs)
        self._initialize_controller()
        self.menu = None
        self.dialog = None
        Clock.schedule_once(self.post_init, 0)
        Clock.schedule_once(self._init_filter_collapsed_state, 0.1)

    def toggle_filter_panel(self):
        """Klappt den Filter-Bereich auf oder zu (Android-kompatibel, kein disabled)"""
        container = self.ids.get('filter_container')
        if not container:
            return
        if self.is_filter_expanded:
            container.height = 0
            container.opacity = 0
            self.is_filter_expanded = False
        else:
            container.height = dp(120)
            container.opacity = 1
            self.is_filter_expanded = True

    def _init_filter_collapsed_state(self, dt):
        """Im mobilen Modus Filter eingeklappt starten (nur wenn Toggle-Button vorhanden)"""
        try:
            # Nur einklappen wenn ein Toggle-Button zum Aufklappen existiert (Desktop-KV)
            if not self.ids.get('filter_chevron'):
                return
            from services.service_container import service_container
            config_service = service_container.get_config_service()
            if config_service and config_service.get('mobile_modus', False):
                self.toggle_filter_panel()
        except Exception as e:
            Logger.error(f"Fehler bei Filter-Collapse-Init: {e}")

    def toggle_only_selected_items(self):
        """
        Schaltet den Filter für 'Nur ausgewählte Elemente' um.
        Event-Handler für den Button (Android Checkbox Workaround).
        """
        self.only_selected_items = not self.only_selected_items
        self.filter_talente()
        Logger.debug(f"Filter 'Nur ausgewählte Talente' gesetzt auf: {self.only_selected_items}")

    def toggle_only_available_talents(self):
        """
        Schaltet den Filter für 'Nur Talente mit erfüllten Voraussetzungen' um.
        Event-Handler für den Button (Android Checkbox Workaround).
        """
        self.only_available_talents = not self.only_available_talents
        self.refresh_widget()
        Logger.debug(f"Filter 'Nur verfügbare Talente' gesetzt auf: {self.only_available_talents}")

    def _filter_talente_data(self, alle_talente, search_term, selected_kategorie):
        """
        Filtert die Talent-Daten nach Suchbegriff, Kategorie und ggf. Auswahlstatus.
        Extrahiert die Filterlogik aus filter_talente.
        """
        filtered_data = []
        
        for key, talent in alle_talente.items():
            # Filter für "Nur ausgewählte Elemente"
            if self.only_selected_items and not talent.ausgewaehlt:
                continue
            
            # Filter für "Nur verfügbare Talente anzeigen"
            if self.only_available_talents and not talent.ausgewaehlt:
                # Prüfe Voraussetzungen
                fehlermeldungen = pruefe_voraussetzungen(self.controller.charakter, talent)
                
                # Prüfe Rang
                rang_zu_hoch = is_talent_rang_hoeher_als_charakter(
                    self.controller.charakter, 
                    talent.rang
                )
                
                # Wenn Voraussetzungen nicht erfüllt oder Rang zu hoch, überspringen
                if fehlermeldungen or rang_zu_hoch:
                    continue
                
            # Kategorie-Filter
            if (selected_kategorie != ALL_CATEGORIES_TEXT.lower() and 
                (talent.kategorie is None or talent.kategorie.lower() != selected_kategorie)):
                continue
                
            # Suchtext-Filter (verarbeite auch leeren Suchtext)
            if not search_term or (
                search_term in talent.name.lower() or 
                search_term in talent.beschreibung.lower()
            ):
                # Anzeigename anpassen für mehrfache Instanzen
                display_name = talent.name
                if '_' in key and key.split('_')[-1].isdigit():
                    instance_num = key.split('_')[-1]
                    display_name = f"{talent.name} (#{instance_num})"
                
                # Voraussetzungen formatieren
                voraussetzungen_text = self._formatiere_voraussetzungen(talent)
                
                talent_data = {
                    'viewclass': 'TalentItemRow',
                    'index': len(filtered_data),
                    'name_key': key,
                    'talent_name': display_name,
                    'kategorie': talent.kategorie,
                    'rang': talent.rang,
                    'beschreibung': talent.beschreibung,
                    'voraussetzungen': voraussetzungen_text,
                    'ausgewaehlt': talent.ausgewaehlt,
                    'controller': self.controller
                }
                filtered_data.append(talent_data)
                
        return filtered_data
        
    def _formatiere_voraussetzungen(self, talent):
        """
        Formatiert die Voraussetzungen eines Talents in einen lesbaren String.
        Unterstützt Markup für bessere Lesbarkeit.
        
        Args:
            talent: Das Talent-Objekt mit Voraussetzungen
            
        Returns:
            str: Formatierter String der Voraussetzungen mit Markup
        """
        # Prüfen, ob das Talent Voraussetzungen hat
        if not hasattr(talent, 'voraussetzungen') or not talent.voraussetzungen:
            return "-"
            
        # Je nach Datentyp der Voraussetzungen formatieren
        try:
            if isinstance(talent.voraussetzungen, str):
                return talent.voraussetzungen
            elif isinstance(talent.voraussetzungen, list):
                # Liste in mehrzeiliges Format mit Bulletpoints umwandeln
                return "\n• ".join([""] + [str(item) for item in talent.voraussetzungen])
            elif isinstance(talent.voraussetzungen, dict):
                # Dictionary in mehrzeiliges Format umwandeln
                result = []
                for key, value in talent.voraussetzungen.items():
                    if isinstance(value, (list, tuple)):
                        items = [str(v) for v in value]
                        result.append(f"[b]{key}:[/b] {', '.join(items)}")
                    else:
                        result.append(f"[b]{key}:[/b] {value}")
                return "\n".join(result)
            else:
                # Fallback für andere Typen
                return str(talent.voraussetzungen)
        except Exception as e:
            Logger.error(f"Fehler beim Formatieren der Voraussetzungen: {e}")
            return "-"

    def _initialize_controller(self):
        """Initialisiert die Verbindung zum Controller."""
        app = MDApp.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None
        
        if not self.controller:
            Logger.error("TalenteWidget: Controller nicht gefunden")

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
        self.filter_talente()

    def filter_talente(self, *args):
        """
        Filtert und sortiert die Talente.
        Event-Handler für Änderungen an Suchtext oder Kategorie.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("TalenteWidget: Controller oder Charakter nicht verfügbar")
            return
            
        search_input = self.ids.get('search_input')
        category_label = self.ids.get('category_label')
        search_term = search_input.text.lower() if search_input else ''
        selected_kategorie = category_label.text.lower() if category_label else 'alle kategorien'

        # Talente vom Modell abrufen
        alle_talente = self.controller.charakter.talente
        
        # Gefilterte Liste erstellen
        filtered_data = self._filter_talente_data(
            alle_talente,
            search_term, 
            selected_kategorie
        )
        
        # Sortieren
        filtered_data = self._sort_talente_data(filtered_data)
        
        # Index nach Sortierung aktualisieren
        for i, item in enumerate(filtered_data):
            item['index'] = i

        # An RecycleView übergeben
        self.ids.recycleview.data = filtered_data
        Logger.debug(f"Talente gefiltert und sortiert: {len(filtered_data)} Einträge")

    def _sort_talente_data(self, data):
        """
        Sortiert die Talent-Daten nach den aktuellen Sortierkriterien.
        Extrahiert die Sortierlogik aus filter_talente.
        """
        reverse_order = (self.sort_order == 'desc')
        
        # Sortieren nach dem ausgewählten Kriterium
        if self.current_sort_option == 'Name':
            data.sort(key=lambda x: x['talent_name'].lower(), reverse=reverse_order)
        elif self.current_sort_option == 'Rang':
            # Für erste Zeichenbasierte Sortierung
            data.sort(key=lambda x: RANG_MAPPING.get(x['rang'][0] if x['rang'] else 'A', float('inf')), reverse=reverse_order)
        elif self.current_sort_option == 'Kategorie':
            data.sort(key=lambda x: (x['kategorie'] or '').lower(), reverse=reverse_order)
            
        return data

    def post_init(self, dt):
        """
        Initialisierung nach dem Laden des Widgets.
        Wird einmalig durch Clock.schedule_once aufgerufen.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("TalenteWidget: Controller oder Charakter nicht verfügbar")
            return
            
        alle_talente = self.controller.charakter.talente
        Logger.debug(f"TalenteWidget: Lade {len(alle_talente)} Talente")
        
        # Kategorien extrahieren und sortieren
        self._update_kategorien(alle_talente)
        
        # Talente filtern und anzeigen
        self.filter_talente()

    def _update_kategorien(self, talente_dict):
        """Aktualisiert die Liste der verfügbaren Talent-Kategorien."""
        self.kategorien = sorted(list(set(
            talent.kategorie for talent in talente_dict.values() 
            if talent.kategorie
        )))
        Logger.debug(f"TalenteWidget: Gefundene Kategorien: {self.kategorien}")

    def refresh_widget(self):
        """
        Leert das Widget und lädt die Daten neu.
        Wird aufgerufen, wenn sich die Talente ändern.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("TalenteWidget: Controller oder Charakter nicht verfügbar")
            return
            
        # RecycleView leeren
        self.ids.recycleview.data = []
        
        # Kategorien neu laden
        alle_talente = self.controller.charakter.talente
        self._update_kategorien(alle_talente)
        
        # Filter neu anwenden
        self.filter_talente()

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
        caller = self.ids.get('category_label') or self.ids.get('only_selected_button')
        self.menu = MDDropdownMenu(
            caller=caller,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def set_category(self, text):
        """
        Setzt die ausgewählte Kategorie und aktualisiert die Anzeige.
        Event-Handler für die Kategorie-Auswahl im Menü.
        """
        category_label = self.ids.get('category_label')
        if category_label:
            category_label.text = text
        self.menu.dismiss()
        self.filter_talente()