# views/handicaps_view.py
"""
View-Komponente für Handicaps nach dem MVC-Pattern.
Stellt die Benutzerschnittstelle zur Anzeige und Verwaltung von Handicaps bereit.
"""

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton, MDFabButton, MDButtonText

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer
)

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.selectioncontrol import MDCheckbox

# Import für Dialog Service
from services.service_container import get_dialog_service


# Konstanten für bessere Lesbarkeit und Wartbarkeit
DEFAULT_SORT_ORDER = 'name_asc'
ALL_CATEGORIES_TEXT = 'Alle Stufen'
RECYCLEVIEW_ITEM_HEIGHT = dp(80)
DARK_EVEN_COLOR = [0.2, 0.2, 0.2, 1]
DARK_ODD_COLOR = [0.15, 0.15, 0.15, 1]
LIGHT_EVEN_COLOR = [1, 1, 1, 1]
LIGHT_ODD_COLOR = [0.85, 0.85, 0.85, 1]
SELECTED_LINE_COLOR = [1, 0.65, 0, 1]
UNSELECTED_LINE_COLOR = [0, 0, 0, 0]


import os
import sys

# PyInstaller-kompatibles Laden der KV-Datei
def load_kv_file():
    if getattr(sys, 'frozen', False):
        # PyInstaller Bundle
        base_path = sys._MEIPASS
        kv_path = os.path.join(base_path, 'views', 'handicaps_view.kv')
    else:
        # Normale Ausführung
        base_path = os.path.dirname(os.path.dirname(__file__))
        kv_path = os.path.join(base_path, 'views', 'handicaps_view.kv')
    
    if os.path.exists(kv_path):
        Builder.load_file(kv_path)
    else:
        Logger.error(f"handicaps_view: KV-Datei nicht gefunden: {kv_path}")

load_kv_file()


class HandicapsRecycleView(MDRecycleView):
    """
    RecycleView für die effiziente Darstellung der Handicap-Liste.
    Implementiert eine virtualisierte Listenansicht für bessere Performance.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        Logger.debug("HandicapsRecycleView: Initialisiert")


class HandicapItemRow(MDBoxLayout):
    """
    Einzelne Zeile in der Handicap-Liste.
    Repräsentiert ein einzelnes Handicap mit seinen Eigenschaften und Interaktionsmöglichkeiten.
    """
    index = NumericProperty(0)
    name_key = StringProperty("")
    handicap_name = StringProperty("")
    stufe = StringProperty("")
    beschreibung = StringProperty("")
    ausgewaehlt = BooleanProperty(False)

    NICHT_DUPLIZIERBARE_HANDICAPS = [
        "Alt", "Jung", "Blind", "Einarmig", "Einäugig", "Stumm", 
        "Analphabet", "Klein", "Fettleibig", "Langsam"
    ]

    def __init__(self, **kwargs):
        """Initialisiert die HandicapItemRow und bindet Property-Änderungen an entsprechende Handler."""
        super().__init__(**kwargs)
        self.bind(ausgewaehlt=self.on_ausgewaehlt_changed)
        self.bind(index=self.update_color)  # Wichtig: Farbaktualisierung bei Indexänderung

    def _get_controller(self):
        """Hilfsmethode, um auf den Controller zuzugreifen."""
        app = MDApp.get_running_app()
        return app.controller if hasattr(app, 'controller') else None

    def _refresh_ui(self):
        """Aktualisiert die UI nach einer Änderung am Handicap-Status."""
        Logger.debug(f"HandicapItemRow: Starte Widget-Aktualisierung")
        app = MDApp.get_running_app()
        widget = app.get_widget_by_tab_text('Handicaps', 'handicaps_widget')
        if widget:
            Logger.debug("HandicapItemRow: HandicapsWidget gefunden, führe refresh aus")
            Clock.schedule_once(lambda dt: widget.refresh_widget(), 0)
        else:
            Logger.error("HandicapItemRow: HandicapsWidget nicht gefunden")

    def bearbeite_handicap(self):
        """Öffnet den Bearbeitungsdialog für das Handicap."""
        Logger.debug(f"HandicapItemRow: Bearbeite Handicap '{self.handicap_name}' mit Key '{self.name_key}'")
        
        # Dialog Service über Service Container holen
        dialog_service = get_dialog_service()
        if dialog_service and hasattr(dialog_service, 'handicap_dialog_handler'):
            dialog_service.handicap_dialog_handler.show_edit_dialog(self.name_key)
            Logger.debug("HandicapItemRow: Bearbeitungsdialog erfolgreich geöffnet")
        else:
            Logger.error("HandicapItemRow: Dialog Service oder handicap_dialog_handler nicht verfügbar")
            # Fallback-Fehlermeldung für den Benutzer
            if dialog_service:
                dialog_service.show_error_dialog(
                    "Der Bearbeitungsdialog konnte nicht geöffnet werden. "
                    "Bitte versuchen Sie es später erneut."
                )

    def waehle_handicap(self):
        """
        Wählt ein Handicap aus.
        Prüft vorher, ob das Limit von 4 Punkten bereits erreicht ist und zeigt ggf. einen Warnhinweis.
        """
        Logger.debug(f"HandicapItemRow: Start waehle_handicap für {self.handicap_name}")
        controller = self._get_controller()
        if not controller:
            Logger.error("HandicapItemRow: Controller nicht gefunden")
            return

        # Prüfen, ob das Handicap bereits ausgewählt ist und nicht duplizierbar
        if self.ausgewaehlt and self.handicap_name in self.NICHT_DUPLIZIERBARE_HANDICAPS:
            self._show_not_duplicatable_dialog()
            return

        # Prüfen, ob bereits das Maximum an Handicap-Punkten erreicht ist
        charakter = controller.charakter
        if charakter.gesamt_handicap_punkte >= 4:
            self._show_max_points_dialog()
            return

        try:
            controller.waehle_handicap(self.name_key)
            # Wenn keine Exception geworfen wurde, war die Aktion erfolgreich
            if not self.ausgewaehlt:  # Nur wenn es noch nicht ausgewählt war
                self.ausgewaehlt = True
            Logger.debug(f"HandicapItemRow: {self.handicap_name} erfolgreich ausgewählt")
            self._refresh_ui()
        except Exception as e:
            Logger.error(f"Fehler beim Auswählen des Handicaps: {str(e)}")

    def _show_not_duplicatable_dialog(self):
        """Zeigt einen Dialog an, wenn ein Handicap nicht mehrfach ausgewählt werden kann."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        warning_label = MDLabel(
            text=f"Das Handicap '{self.handicap_name}' kann nicht mehrfach ausgewählt werden.",
            size_hint_y=None,
            height=dp(60),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(warning_label)
        
        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Handicap nicht duplizierbar",
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
        )
        dialog.open()

    def _show_max_points_dialog(self):
        """Zeigt einen Dialog an, wenn das Maximum an Handicap-Punkten erreicht ist."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        warning_label = MDLabel(
            text="Das Maximum von 4 Handicap-Punkten ist bereits erreicht! Die Auswirkungen des Handicaps werden angewendet, aber keine weiteren Punkte werden gutgeschrieben.",
            size_hint_y=None,
            height=dp(80),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(warning_label)
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Maximum erreicht",
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
                    on_release=lambda x: self._confirm_handicap_selection(),
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def close_dialog(self):
        """Schließt den Dialog."""
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()

    def _confirm_handicap_selection(self):
        """Führt die Handicap-Auswahl trotz voller Punktezahl durch."""
        self.close_dialog()
        controller = self._get_controller()
        if controller:
            controller.waehle_handicap(self.name_key)
            self.ausgewaehlt = True
            self._refresh_ui()

    def entferne_handicap(self):
        """
        Entfernt ein ausgewähltes Handicap.
        Nach der Charaktergenerierung kostet dies Aufstiege.
        Bei schweren Handicaps mit leichter Version werden beide Optionen angeboten.
        """
        Logger.debug(f"HandicapItemRow: Start entferne_handicap für {self.handicap_name}")
        controller = self._get_controller()
        if not controller:
            Logger.error("HandicapItemRow: Controller nicht gefunden")
            return

        # Direkt versuchen zu entfernen - die Logik entscheidet, ob ein Dialog angezeigt wird
        self._try_remove_handicap()

    def _show_remove_or_reduce_dialog(self):
        """Zeigt einen Dialog mit Optionen zum kompletten Entfernen oder Reduzieren."""
        charakter = self._get_controller().charakter
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(20),
            adaptive_height=True
        )
        
        info_label = MDLabel(
            text=f"Wähle eine Option für das Handicap '{self.handicap_name} (schwer)':",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(info_label)
        
        # Option 1: Komplett entfernen
        remove_text = f"• Komplett entfernen für 2 Aufstiege"
        if charakter.verbleibende_aufstiege < 2:
            remove_text += " (nicht genug Aufstiege)"
        
        remove_label = MDLabel(
            text=remove_text,
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Secondary" if charakter.verbleibende_aufstiege >= 2 else "Error",
            halign="left",
            valign="middle"
        )
        content.add_widget(remove_label)
        
        # Option 2: Auf leicht reduzieren
        reduce_text = f"• Auf leicht reduzieren für 1 Aufstieg"
        if charakter.verbleibende_aufstiege < 1:
            reduce_text += " (nicht genug Aufstiege)"
        
        reduce_label = MDLabel(
            text=reduce_text,
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Secondary" if charakter.verbleibende_aufstiege >= 1 else "Error",
            halign="left",
            valign="middle"
        )
        content.add_widget(reduce_label)
        
        # Verfügbare Aufstiege anzeigen
        aufstiege_label = MDLabel(
            text=f"\nVerbleibende Aufstiege: {charakter.verbleibende_aufstiege}",
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Primary",
            halign="left",
            valign="middle"
        )
        content.add_widget(aufstiege_label)
        
        # Button-Container
        button_container = MDDialogButtonContainer(spacing="8dp")
        
        # Abbrechen-Button
        button_container.add_widget(
            MDButton(
                MDButtonText(text="Abbrechen"),
                style="text",
                on_release=lambda x: self.close_remove_reduce_dialog(),
            )
        )
        
        # Reduzieren-Button (nur wenn genug Aufstiege)
        if charakter.verbleibende_aufstiege >= 1:
            button_container.add_widget(
                MDButton(
                    MDButtonText(text="Auf leicht reduzieren"),
                    style="text",
                    on_release=lambda x: self._confirm_reduce_handicap_from_dialog(),
                )
            )
        
        # Entfernen-Button (nur wenn genug Aufstiege)
        if charakter.verbleibende_aufstiege >= 2:
            button_container.add_widget(
                MDButton(
                    MDButtonText(text="Komplett entfernen"),
                    style="text",
                    on_release=lambda x: self._confirm_remove_handicap_from_dialog(),
                )
            )
        
        self.remove_reduce_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Handicap entfernen oder reduzieren?",
            ),
            MDDialogContentContainer(
                content,
                orientation="vertical",
                padding=dp(0),
            ),
            button_container
        )
        self.remove_reduce_dialog.open()

    def close_remove_reduce_dialog(self):
        """Schließt den Entfernen/Reduzieren-Dialog."""
        if hasattr(self, 'remove_reduce_dialog') and self.remove_reduce_dialog:
            self.remove_reduce_dialog.dismiss()

    def _confirm_remove_handicap_from_dialog(self):
        """Bestätigt das komplette Entfernen des Handicaps aus dem Dialog."""
        self.close_remove_reduce_dialog()
        controller = self._get_controller()
        if controller:
            # NEU: force_remove=True übergeben
            result = controller.entferne_handicap(self.name_key, force_remove=True)
            
            if isinstance(result, str) and result.startswith("needs_advancement_"):
                # Extrahiere die benötigten Aufstiege
                kosten = int(result.split("_")[2])
                self._show_no_advancement_dialog(kosten)
            elif result:
                # Erfolgreich entfernt
                self.ausgewaehlt = False
                Logger.debug(f"HandicapItemRow: {self.handicap_name} erfolgreich entfernt")
                self._refresh_ui()
            else:
                Logger.error(f"Handicap konnte nicht entfernt werden")

    def _confirm_reduce_handicap_from_dialog(self):
        """Bestätigt das Reduzieren des Handicaps aus dem Dialog."""
        self.close_remove_reduce_dialog()
        controller = self._get_controller()
        if controller:
            result = controller.reduziere_handicap(self.name_key)
            if result:
                Logger.debug(f"Handicap '{self.handicap_name}' erfolgreich reduziert")
                self._refresh_ui()
            else:
                Logger.error("Fehler beim Reduzieren des Handicaps")

    def _try_remove_handicap(self):
        """Versucht das Handicap zu entfernen (alte Logik)."""
        controller = self._get_controller()
        if not controller:
            return
            
        try:
            result = controller.entferne_handicap(self.name_key)
            
            if result == "has_both_options":
                # NEU: Bei schweren Handicaps mit leichter Version Dialog zeigen
                self._show_remove_or_reduce_dialog()
            elif isinstance(result, str) and result.startswith("needs_advancement_"):
                # Extrahiere die benötigten Aufstiege
                kosten = int(result.split("_")[2])
                self._show_no_advancement_dialog(kosten)
            elif result == "can_reduce":
                # Zeige Dialog für Reduzierungsoption
                self._show_reduce_dialog()
            elif result:
                # Erfolgreich entfernt
                self.ausgewaehlt = False
                Logger.debug(f"HandicapItemRow: {self.handicap_name} erfolgreich entfernt")
                self._refresh_ui()
            else:
                Logger.error(f"Handicap konnte nicht entfernt werden")
        except Exception as e:
            Logger.error(f"Fehler beim Entfernen des Handicaps: {str(e)}")

    def _show_no_advancement_dialog(self, kosten):
        """Zeigt einen Dialog an, wenn nicht genügend Aufstiege verfügbar sind."""
        charakter = self._get_controller().charakter
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        kosten_text = f"{kosten} Aufstieg" if kosten == 1 else f"{kosten} Aufstiege"
        
        warning_label = MDLabel(
            text=f"Du benötigst {kosten_text}, um das Handicap '{self.handicap_name}' zu entfernen.\n\nVerbleibende Aufstiege: {charakter.verbleibende_aufstiege}",
            size_hint_y=None,
            height=dp(80),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(warning_label)
        
        self.advancement_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Aufstiege erforderlich",
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
                    on_release=lambda x: self.close_advancement_dialog(),
                ),
                spacing="8dp",
            ),
        )
        self.advancement_dialog.open()
    
    def _show_reduce_dialog(self):
        """Zeigt einen Dialog für die Option, ein schweres Handicap zu reduzieren."""
        charakter = self._get_controller().charakter
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        info_label = MDLabel(
            text=f"Du hast nicht genügend Aufstiege, um das schwere Handicap '{self.handicap_name}' komplett zu entfernen.\n\nDu kannst es aber für 1 Aufstieg auf ein leichtes Handicap reduzieren.\n\nVerbleibende Aufstiege: {charakter.verbleibende_aufstiege}",
            size_hint_y=None,
            height=dp(100),
            theme_text_color="Secondary",
            halign="left",
            valign="middle"
        )
        content.add_widget(info_label)
        
        self.reduce_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Handicap reduzieren?",
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
                    on_release=lambda x: self.close_reduce_dialog(),
                ),
                MDButton(
                    MDButtonText(text="Auf leicht reduzieren"),
                    style="text",
                    on_release=lambda x: self._confirm_reduce_handicap(),
                ),
                spacing="8dp",
            ),
        )
        self.reduce_dialog.open()
    
    def close_reduce_dialog(self):
        """Schließt den Reduzierungs-Dialog."""
        if hasattr(self, 'reduce_dialog') and self.reduce_dialog:
            self.reduce_dialog.dismiss()
    
    def _confirm_reduce_handicap(self):
        """Führt die Reduzierung des Handicaps durch."""
        self.close_reduce_dialog()
        controller = self._get_controller()
        if controller:
            result = controller.reduziere_handicap(self.name_key)
            if result == "needs_advancement":
                self._show_no_advancement_dialog(1)
            elif result:
                Logger.debug(f"Handicap '{self.handicap_name}' erfolgreich reduziert")
                self._refresh_ui()
            else:
                Logger.error("Fehler beim Reduzieren des Handicaps")
    
    def close_advancement_dialog(self):
        """Schließt den Aufstiegs-Dialog."""
        if hasattr(self, 'advancement_dialog') and self.advancement_dialog:
            self.advancement_dialog.dismiss()

    def show_full_description(self):
        """Zeigt die vollständige Beschreibung des Handicaps in einem Dialog an."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        # Handicap-Name als Überschrift
        title_label = MDLabel(
            text=f"[b]{self.handicap_name}[/b]",
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
                text="Handicap-Beschreibung",
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
        Logger.debug(f"HandicapItemRow: ausgewaehlt changed to {value} for {self.handicap_name}")
        # Bei Änderung des Auswahlstatus auch die Umrandung aktualisieren
        self.line_color = self._get_line_color()


class HandicapsWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Handicaps.
    Hauptkomponente der View im MVC-Pattern.
    """
    stufen = ListProperty([])
    sort_order = StringProperty(DEFAULT_SORT_ORDER)
    only_selected_items = BooleanProperty(False)  # Neue Property für den Filter

    def __init__(self, **kwargs):
        """Initialisiert das HandicapsWidget und setzt Grundkonfiguration."""
        super().__init__(**kwargs)
        self._initialize_controller()
        self.menu = None
        Clock.schedule_once(self.post_init, 0)


    def toggle_only_selected_items(self):
        """
        Schaltet den Filter für 'Nur ausgewählte Elemente' um.
        Event-Handler für den Button (Android Checkbox Workaround).
        """
        self.only_selected_items = not self.only_selected_items
        if self.only_selected_items:
            Logger.debug(f"Filter 'Nur ausgewählte Handicaps' aktiviert")
        else:
            Logger.debug(f"Filter 'Nur ausgewählte Handicaps' deaktiviert")
        
        self.filter_handicaps()

    def _filter_handicaps_data(self, alle_handicaps, search_term, selected_stufe):
        """
        Filtert die Handicap-Daten nach Suchbegriff, Stufe und ggf. Auswahlstatus.
        Extrahiert die Filterlogik aus filter_handicaps.
        """
        filtered_data = []
        
        Logger.debug(f"HandicapsWidget: Filtere Handicaps - Suchterm: {search_term}, Stufe: {selected_stufe}, Nur ausgewählte: {self.only_selected_items}")
        
        for key, handicap in alle_handicaps.items():
            # Filter für "Nur ausgewählte Elemente"
            if self.only_selected_items and not handicap.ausgewaehlt:
                continue
                
            # Stufen-Filter
            if (selected_stufe != ALL_CATEGORIES_TEXT.lower() and 
                (handicap.stufe is None or handicap.stufe.lower() != selected_stufe)):
                continue
                
            # Suchtext-Filter
            if (search_term in handicap.name.lower() or 
                search_term in handicap.beschreibung.lower()):
                
                # Anzeigename anpassen für mehrfache Instanzen
                display_name = handicap.name
                if '_' in key and key.split('_')[-1].isdigit():
                    instance_num = key.split('_')[-1]
                    display_name = f"{handicap.name} (#{instance_num})"
                
                handicap_data = {
                    'viewclass': 'HandicapItemRow',
                    'index': len(filtered_data),
                    'name_key': key,
                    'handicap_name': display_name,  # Verwende den angepassten Namen
                    'stufe': handicap.stufe,
                    'beschreibung': handicap.beschreibung,
                    'ausgewaehlt': handicap.ausgewaehlt
                }
                filtered_data.append(handicap_data)
                
        return filtered_data

    def _initialize_controller(self):
        """Initialisiert die Verbindung zum Controller."""
        app = MDApp.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None
        
        if not self.controller:
            Logger.error("HandicapsWidget: Controller nicht gefunden")

    def post_init(self, dt):
        """
        Initialisierung nach dem Laden des Widgets.
        Lädt Daten vom Modell und bereitet die Anzeige vor.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("HandicapsWidget: Controller oder Charakter nicht verfügbar")
            return
            
        alle_handicaps = self.controller.charakter.handicaps
        Logger.debug(f"HandicapsWidget: Lade {len(alle_handicaps)} Handicaps")
        
        # Stufen extrahieren und sortieren
        self._update_stufen(alle_handicaps)
        
        # Handicaps filtern und anzeigen
        self.filter_handicaps()

    def _update_stufen(self, handicaps_dict):
        """Aktualisiert die Liste der verfügbaren Handicap-Stufen."""
        self.stufen = sorted(list(set(
            handicap.stufe for handicap in handicaps_dict.values() 
            if handicap.stufe
        )))
        Logger.debug(f"HandicapsWidget: Gefundene Stufen: {self.stufen}")

    def refresh_widget(self):
        """
        Leert das Widget und lädt die Daten neu.
        Wird aufgerufen, wenn sich die Handicaps ändern.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("HandicapsWidget: Controller oder Charakter nicht verfügbar")
            return
            
        # RecycleView leeren
        self.ids.recycleview.data = []
        
        # Stufen neu laden
        alle_handicaps = self.controller.charakter.handicaps
        self._update_stufen(alle_handicaps)
        
        # Filter neu anwenden
        self.filter_handicaps()

    def toggle_sort_order(self):
        """
        Ändert die Sortierreihenfolge und aktualisiert die Anzeige.
        Event-Handler für den Sortierbutton.
        """
        self.sort_order = 'name_desc' if self.sort_order == 'name_asc' else 'name_asc'
        self.filter_handicaps()

    def filter_handicaps(self, *args):
        """
        Filtert die Handicaps basierend auf Suchtext und Kategorie.
        Event-Handler für Änderungen an Suchtext oder Kategorie.
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("HandicapsWidget: Controller oder Charakter nicht verfügbar")
            return
            
        search_term = self.ids.search_input.text.lower()
        selected_stufe = self.ids.category_label.text.lower()

        # Handicaps vom Modell abrufen
        alle_handicaps = self.controller.charakter.handicaps
        
        # Gefilterte Liste erstellen
        filtered_data = self._filter_handicaps_data(
            alle_handicaps,
            search_term, 
            selected_stufe
        )
        
        # Sortieren
        filtered_data = self._sort_handicaps_data(filtered_data)
        
        # Index nach Sortierung aktualisieren
        for i, item in enumerate(filtered_data):
            item['index'] = i

        # An RecycleView übergeben
        self.ids.recycleview.data = filtered_data
        Logger.debug(f"HandicapsWidget: {len(filtered_data)} Handicaps gefiltert und sortiert")

    def _sort_handicaps_data(self, data):
        """
        Sortiert die Handicap-Daten nach der aktuellen Sortierreihenfolge.
        Extrahiert die Sortierlogik aus filter_handicaps.
        """
        is_ascending = self.sort_order == 'name_asc'
        data.sort(key=lambda x: x['handicap_name'].lower(), reverse=not is_ascending)
        return data

    def open_category_menu(self):
        """
        Öffnet das Kategorie-Auswahlmenü.
        Event-Handler für den Kategorie-Filter-Button.
        """
        menu_items = [
            {
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_category(x),
            } for i in [ALL_CATEGORIES_TEXT] + self.stufen
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
        self.filter_handicaps()