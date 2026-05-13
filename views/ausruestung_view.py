# ausruestung_view.py

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty, BooleanProperty, DictProperty
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText, MDFabButton
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.label import MDLabel
from kivy.uix.checkbox import CheckBox
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
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

# Import für detailliertes Logging
from utils.logging_setup import log_transaction, log_android_event

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
    
    # Klassenattribut für Caching der Hintergrundfarben
    _color_cache = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self._dialog_processing = False  # Android Dialog-Schutz
        self._set_background_color()  # THEME-FIX: Hintergrundfarbe setzen

    def _get_background_color(self):
        """Berechnet die Hintergrundfarbe basierend auf Theme und Index."""
        app = MDApp.get_running_app()
        if not app or not hasattr(app, 'theme_cls'):
            return [0, 0, 0, 1]  # Fallback
        
        theme_style = app.theme_cls.theme_style
        is_even = self.index % 2 == 0
        key = (theme_style, is_even)
        
        if key not in self._color_cache:
            if theme_style == "Light":
                if is_even:
                    color = [0.95, 0.95, 0.95, 1]  # Sehr helles Grau
                else:
                    color = [0.98, 0.98, 0.98, 1]  # Noch heller
            else:
                if is_even:
                    color = [0.2, 0.2, 0.2, 1]
                else:
                    color = [0.15, 0.15, 0.15, 1]
            self._color_cache[key] = color
            
        return self._color_cache[key]
    
    def _set_background_color(self):
        """Setzt die Hintergrundfarbe basierend auf dem aktuellen Theme"""
        self.md_bg_color = self._get_background_color()
    
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
        """Zeigt einen Dialog zum Kaufen an. Bei Cyberware wird ein spezieller
        Konfigurationsdialog mit flexiblem Preisfeld angezeigt."""
        try:
            controller = self._get_controller()
            if controller:
                # Alle Cyberware-Items bekommen den Konfigurationsdialog (mit Preisfeld)
                from functions.cyberware_funktionen import ist_cyberware_setting, braucht_konfiguration
                charakter = controller.charakter
                if ist_cyberware_setting(charakter.active_setting_name):
                    item = charakter.ausruestung.get(self.name)
                    if item and getattr(item, 'kategorie', '') == 'Cyberware':
                        konfig_info = braucht_konfiguration(self.name, charakter)
                        # konfig_info ist None bei Items ohne Auswahl (z.B. Panzerung)
                        self._erstelle_cyberware_konfiguration_dialog(konfig_info)
                        return

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
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self.dialog.open()

    def _erstelle_cyberware_konfiguration_dialog(self, konfig_info):
        """
        Zeigt einen Konfigurationsdialog für Cyberware an (z.B. Attribut-/Fertigkeitswahl).
        Enthält ein Preisfeld wie der normale Kauf-Dialog.
        Nach Bestätigung wird der Kauf mit der gewählten Konfiguration ausgeführt.

        Args:
            konfig_info: Dict mit {"typ", "optionen", "label"} oder None für reine Preisanpassung
        """
        from kivymd.uix.button import MDButton, MDButtonText

        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            padding="12dp",
            adaptive_height=True,
            size_hint_y=None,
            height=landscape_height(250, 0.4),
        )

        # Speichere die aktuelle Auswahl
        ausgewaehlter_wert = {"wert": None}

        if konfig_info:
            # Label
            content.add_widget(MDLabel(
                text=konfig_info['label'],
                size_hint_y=None,
                height=dp(30),
                halign="left",
            ))

            # Auswahlfeld (MDDropdownMenu über einen Button)
            auswahl_button = MDButton(
                style="outlined",
                size_hint_x=1,
                size_hint_y=None,
                height=dp(48),
            )
            auswahl_text = MDButtonText(text="-- Bitte wählen --")
            auswahl_button.add_widget(auswahl_text)
            content.add_widget(auswahl_button)

            # Dropdown-Menü erstellen
            menu_items = []
            for option in konfig_info['optionen']:
                menu_items.append({
                    "text": option,
                    "on_release": lambda x=option: _waehle_option(x),
                })

            menu = MDDropdownMenu(
                caller=auswahl_button,
                items=menu_items,
            )

            def _waehle_option(option):
                ausgewaehlter_wert["wert"] = option
                auswahl_text.text = option
                menu.dismiss()

            auswahl_button.bind(on_release=lambda x: menu.open())

        # Preisfeld (bearbeitbar wie beim normalen Kauf-Dialog)
        preis_field = MDTextField(
            mode="outlined",
            text=str(self.kosten),
            input_filter="float",
        )
        preis_field.add_widget(MDTextFieldHintText(text="Preis (optional anpassbar)"))
        content.add_widget(preis_field)

        def _handle_konfiguration_kauf(*args):
            if konfig_info and not ausgewaehlter_wert["wert"]:
                self.show_error("Bitte eine Auswahl treffen.")
                return

            # Preis auslesen
            preis = None
            try:
                if preis_field.text:
                    preis = float(preis_field.text)
            except ValueError:
                pass

            # Konfiguration bauen
            konfiguration = {}
            if konfig_info:
                if konfig_info['typ'] == 'attribut':
                    konfiguration['attribut'] = ausgewaehlter_wert["wert"]
                elif konfig_info['typ'] == 'fertigkeit':
                    konfiguration['fertigkeit'] = ausgewaehlter_wert["wert"]
                elif konfig_info['typ'] == 'talent':
                    konfiguration['talent'] = ausgewaehlter_wert["wert"]

            # Dialog schließen und Kauf mit Konfiguration durchführen
            if self.dialog:
                self.dialog.dismiss()
                self.dialog = None
            self._kaufe_mit_konfiguration(konfiguration, preis_pro_stueck=preis)

        self.dialog = MDDialog(
            MDDialogHeadlineText(text=f"{self.name} konfigurieren"),
            MDDialogContentContainer(content, orientation="vertical"),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self.dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Installieren"),
                    style="text",
                    on_release=_handle_konfiguration_kauf,
                ),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        self.dialog.open()

    def _kaufe_mit_konfiguration(self, konfiguration, preis_pro_stueck=None):
        """Führt den Cyberware-Kauf mit der gewählten Konfiguration und optionalem Preis durch."""
        if self._dialog_processing:
            return
        self._dialog_processing = True
        try:
            controller = self._get_controller()
            if not controller:
                self.show_error("Controller nicht gefunden.")
                return

            effektiver_preis = preis_pro_stueck or self.kosten
            vermoegen_vorher = controller.charakter.vermoegen
            log_transaction("KAUF_START", self.name, 1, effektiver_preis, True,
                          f"Vermögen vorher: {vermoegen_vorher}, Mit Konfiguration: {konfiguration}")

            success = controller.kaufen_ausruestung(
                self.name,
                anzahl=1,
                preis_pro_stueck=preis_pro_stueck,
                konfiguration=konfiguration
            )

            vermoegen_nachher = controller.charakter.vermoegen
            log_transaction("KAUF_RESULT", self.name, 1, effektiver_preis, success,
                          f"Vermögen nachher: {vermoegen_nachher}")

            if success or vermoegen_nachher != vermoegen_vorher:
                Logger.debug(f"Cyberware-Kauf mit Konfiguration erfolgreich: {self.name}")
                self._refresh_ui()
                self._zeige_cyberware_feedback(controller, self.name)
            else:
                Logger.debug(f"Cyberware-Kauf fehlgeschlagen: {self.name}")
                self._refresh_ui()
                self._zeige_cyberware_kauf_fehler(controller, self.name)
                # Vermögen-Warnung nur bei tatsächlich nicht ausreichendem Vermögen
                if controller.charakter.vermoegen < effektiver_preis:
                    self._show_kauf_warnung(1)
        except Exception as e:
            Logger.error(f"Fehler beim konfigurierten Cyberware-Kauf: {e}")
            self.show_error("Ein unerwarteter Fehler ist aufgetreten.")
        finally:
            self._dialog_processing = False

    def _handle_kauf_dialog(self, content):
        """Verarbeitet den Kauf"""
        # Android Dialog-Schutz: Verhindern von mehrfacher Ausführung
        if self._dialog_processing:
            Logger.debug(f"Kauf-Dialog für {self.name} bereits in Bearbeitung - ignoriert")
            log_android_event("KAUF_DIALOG_BLOCKED", f"Dialog für {self.name} bereits in Bearbeitung")
            return
        
        self._dialog_processing = True
        log_android_event("KAUF_DIALOG_START", f"Starte Kaufabwicklung für {self.name}")
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
            expected_cost = (preis or self.kosten) * anzahl
            
            log_transaction("KAUF_START", self.name, anzahl, preis or self.kosten, True, 
                          f"Vermögen vorher: {vermoegen_vorher}, Erwartete Kosten: {expected_cost}")
            
            success = controller.kaufen_ausruestung(
                self.name,
                anzahl=anzahl,
                preis_pro_stueck=preis
            )
            
            # Vermögen nach dem Kauf prüfen
            vermoegen_nachher = controller.charakter.vermoegen
            tatsaechlich_gekauft = (vermoegen_vorher - vermoegen_nachher) == expected_cost

            Logger.debug(f"Kauf-Debug: success={success}, vermögen_vorher={vermoegen_vorher}, vermögen_nachher={vermoegen_nachher}")
            log_transaction("KAUF_RESULT", self.name, anzahl, preis or self.kosten, success, 
                          f"Vermögen nachher: {vermoegen_nachher}, Controller Success: {success}, Tatsächlich gekauft: {tatsaechlich_gekauft}")
            
            if success:
                # Controller bestätigt erfolgreichen Kauf
                Logger.debug(f"Kauf erfolgreich bestätigt für {self.name}")
                if self.dialog:
                    self.dialog.dismiss()
                    self.dialog = None
                self._refresh_ui()
                # Cyberware-Stress-Feedback nach erfolgreichem Kauf
                self._zeige_cyberware_feedback(controller, self.name)
            elif vermoegen_nachher != vermoegen_vorher:
                # Vermögen hat sich geändert - Kauf war tatsächlich erfolgreich
                Logger.debug(f"Android: Kauf von {self.name} war erfolgreich (Vermögen: {vermoegen_vorher} -> {vermoegen_nachher})")
                if self.dialog:
                    self.dialog.dismiss()
                    self.dialog = None
                self._refresh_ui()
                # Cyberware-Stress-Feedback auch in diesem Zweig
                self._zeige_cyberware_feedback(controller, self.name)
            else:
                # Kauf war nicht erfolgreich
                Logger.debug(f"Kauf fehlgeschlagen für {self.name} - Vermögen unverändert")
                if self.dialog:
                    self.dialog.dismiss()
                    self.dialog = None
                self._refresh_ui()
                # Cyberware: Zeige spezifische Fehlermeldung bei Stress-Überschreitung
                self._zeige_cyberware_kauf_fehler(controller, self.name)
                # Snackbar-Warnung nur bei tatsächlich nicht ausreichendem Vermögen
                aktueller_preis = preis or self.kosten
                if controller.charakter.vermoegen < aktueller_preis * anzahl:
                    self._show_kauf_warnung(anzahl)

        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten des Kaufs: {str(e)}")
            self.show_error("Ein unerwarteter Fehler ist aufgetreten.")
        finally:
            self._dialog_processing = False

    def _handle_verkauf_dialog(self, content):
        """Verarbeitet den Verkauf"""
        # Android Dialog-Schutz: Verhindern von mehrfacher Ausführung
        if self._dialog_processing:
            Logger.debug(f"Verkauf-Dialog für {self.name} bereits in Bearbeitung - ignoriert")
            log_android_event("VERKAUF_DIALOG_BLOCKED", f"Dialog für {self.name} bereits in Bearbeitung")
            return
        
        self._dialog_processing = True
        log_android_event("VERKAUF_DIALOG_START", f"Starte Verkaufsabwicklung für {self.name}")
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
            default_verkaufspreis = (self.kosten * 0.5) if hasattr(self, 'kosten') else 0
            expected_income = (preis or default_verkaufspreis) * anzahl
            
            log_transaction("VERKAUF_START", self.name, anzahl, preis or default_verkaufspreis, True, 
                          f"Vermögen vorher: {vermoegen_vorher}, Erwartetes Einkommen: {expected_income}")
            
            success = controller.verkaufen_ausruestung(
                self.name,
                anzahl=anzahl,
                preis_pro_stueck=preis
            )
            
            # Vermögen nach dem Verkauf prüfen
            vermoegen_nachher = controller.charakter.vermoegen
            tatsaechlich_verkauft = (vermoegen_nachher - vermoegen_vorher) == expected_income

            Logger.debug(f"Verkauf-Debug: success={success}, vermögen_vorher={vermoegen_vorher}, vermögen_nachher={vermoegen_nachher}")
            log_transaction("VERKAUF_RESULT", self.name, anzahl, preis or default_verkaufspreis, success, 
                          f"Vermögen nachher: {vermoegen_nachher}, Controller Success: {success}, Tatsächlich verkauft: {tatsaechlich_verkauft}")
            
            if success:
                # Controller bestätigt erfolgreichen Verkauf
                Logger.debug(f"Verkauf erfolgreich bestätigt für {self.name}")
                if self.dialog:
                    self.dialog.dismiss()
                    self.dialog = None
                self._refresh_ui()
            elif vermoegen_nachher != vermoegen_vorher:
                # Vermögen hat sich geändert - Verkauf war tatsächlich erfolgreich
                Logger.debug(f"Android: Verkauf von {self.name} war erfolgreich (Vermögen: {vermoegen_vorher} -> {vermoegen_nachher})")
                if self.dialog:
                    self.dialog.dismiss()
                    self.dialog = None
                self._refresh_ui()
            else:
                # Verkauf war nicht erfolgreich - prüfe ob es durch Android-Debouncing verhindert wurde
                Logger.debug(f"Verkauf fehlgeschlagen für {self.name} - Vermögen unverändert")
                # Bei Android-Debouncing: Kein Fehler zeigen, Dialog schließen
                if self.dialog:
                    self.dialog.dismiss()
                    self.dialog = None
                self._refresh_ui()
                # Nur echte Fehler anzeigen - nicht bei Android-Debouncing

        except Exception as e:
            Logger.error(f"Fehler beim Verarbeiten des Verkaufs: {str(e)}")
            self.show_error("Ein unerwarteter Fehler ist aufgetreten.")
        finally:
            self._dialog_processing = False

    def _zeige_cyberware_feedback(self, controller, item_name):
        """Zeigt nach erfolgreichem Cyberware-Kauf ein Stress-Info-Popup."""
        try:
            from functions.cyberware_funktionen import ist_cyberware_setting, berechne_nebenwirkungen
            charakter = controller.charakter
            if not ist_cyberware_setting(charakter.active_setting_name):
                return

            item = charakter.ausruestung.get(item_name)
            if not item or getattr(item, 'kategorie', '') != 'Cyberware':
                return

            stress_aktuell = charakter.cyberware_stress_aktuell
            stresslimit = charakter.cyberware_stresslimit
            stress_max = charakter.cyberware_stress_maximum
            nebenwirkungen = berechne_nebenwirkungen(charakter)

            if nebenwirkungen.get('ueber_maximum'):
                # Katastrophal: über hartem Maximum
                self._zeige_cyberware_status_dialog(
                    title="Stress-Maximum überschritten!",
                    message=(f"Cyberware-Stress: {stress_aktuell} / {stress_max}\n\n"
                             f"Das harte Maximum ist überschritten!\n"
                             f"Das Implantat kann nicht stabil betrieben werden."),
                    warnung=True
                )
            elif nebenwirkungen.get('hat_nebenwirkungen'):
                # Warnung: über Stresslimit
                ueber = nebenwirkungen.get('ueber_limit', 0)
                self._zeige_cyberware_status_dialog(
                    title="Stresslimit überschritten",
                    message=(f"Cyberware-Stress: {stress_aktuell} / {stresslimit} (Max: {stress_max})\n\n"
                             f"Stresslimit um {ueber} überschritten!\n"
                             f"Eine Nebenwirkung aus der Tabelle ist fällig."),
                    warnung=True
                )
            else:
                # Info: alles im grünen Bereich
                verbleibend = stresslimit - stress_aktuell
                self._zeige_cyberware_status_dialog(
                    title="Cyberware installiert",
                    message=(f"Cyberware-Stress: {stress_aktuell} / {stresslimit} (Max: {stress_max})\n\n"
                             f"Noch {verbleibend} Stress frei bis zum Limit."),
                    warnung=False
                )
        except Exception as e:
            Logger.error(f"Fehler beim Cyberware-Feedback: {e}")

    def _zeige_cyberware_kauf_fehler(self, controller, item_name):
        """Zeigt eine Fehlermeldung wenn der Cyberware-Kauf fehlgeschlagen ist."""
        try:
            from functions.cyberware_funktionen import ist_cyberware_setting
            charakter = controller.charakter
            if not ist_cyberware_setting(charakter.active_setting_name):
                return

            item = charakter.ausruestung.get(item_name)
            if not item or getattr(item, 'kategorie', '') != 'Cyberware':
                return

            stress_aktuell = charakter.cyberware_stress_aktuell
            stress_max = charakter.cyberware_stress_maximum
            item_stress = getattr(item, 'stress', 0)
            max_inst = getattr(item, 'max_installationen', -1)

            # Prüfe welcher Grund vorliegt
            if stress_aktuell + item_stress > stress_max:
                self._zeige_cyberware_status_dialog(
                    title="Installation nicht möglich",
                    message=(f"Stress-Maximum würde überschritten!\n\n"
                             f"Aktueller Stress: {stress_aktuell}\n"
                             f"Implantat-Stress: {item_stress}\n"
                             f"Stress-Maximum: {stress_max}\n\n"
                             f"Das Implantat kann nicht installiert werden."),
                    warnung=True
                )
            elif max_inst != -1:
                from functions.cyberware_funktionen import _zaehle_installationen
                aktuelle = _zaehle_installationen(charakter, item_name)
                if aktuelle >= max_inst:
                    self._zeige_cyberware_status_dialog(
                        title="Installation nicht möglich",
                        message=(f"Maximale Installationen erreicht!\n\n"
                                 f"'{item_name}' kann maximal {max_inst}× installiert werden.\n"
                                 f"Bereits installiert: {aktuelle}"),
                        warnung=True
                    )
        except Exception as e:
            Logger.error(f"Fehler beim Cyberware-Kauf-Fehler-Dialog: {e}")

    def _zeige_cyberware_status_dialog(self, title, message, warnung=False):
        """Zeigt einen Cyberware-Status-Dialog an."""
        from kivymd.uix.dialog import (
            MDDialog, MDDialogHeadlineText,
            MDDialogContentContainer, MDDialogButtonContainer
        )
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout

        content = MDBoxLayout(
            orientation="vertical",
            spacing="12dp",
            padding="12dp",
            adaptive_height=True
        )

        label = MDLabel(
            text=message,
            theme_text_color="Error" if warnung else "Primary",
            size_hint_y=None,
            height=dp(120),
            halign="left",
            valign="top"
        )
        content.add_widget(label)

        status_dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogContentContainer(content, orientation="vertical"),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Verstanden"),
                    style="text",
                    on_release=lambda x: status_dialog.dismiss(),
                ),
                spacing="8dp",
            ),
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        status_dialog.open()

    def _show_kauf_warnung(self, anzahl=1):
        """Zeigt eine Snackbar-Warnung wenn der Kauf fehlschlägt."""
        try:
            from services.service_container import service_container
            dialog_service = service_container.get_dialog_service()
            if dialog_service:
                dialog_service.show_warning_dialog(
                    f"Nicht genug Vermögen für {anzahl}x {self.name}."
                )
        except Exception as e:
            Logger.error(f"Warnung konnte nicht angezeigt werden: {e}")

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
            size_hint=(0.85, None),
            auto_dismiss=False,
        )
        error_dialog.open()

    def show_full_description(self):
        """Zeigt die vollständige Beschreibung der Ausrüstung in einem Dialog an."""
        if not self.beschreibung:
            return

        # Responsive Textbreite basierend auf Fensterbreite
        text_width = min(dp(400), Window.width * 0.85 - dp(60))

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
            text_size=(text_width, None),
            markup=True
        )
        desc_label.bind(texture_size=desc_label.setter('size'))
        content.add_widget(desc_label)

        # ScrollView für lange Beschreibungen (Android-kompatibel)
        max_content_height = min(dp(400), Window.height * 0.6)
        scroll = ScrollView(
            size_hint_y=None,
            height=max_content_height,
            do_scroll_x=False,
        )
        scroll.add_widget(content)

        description_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Ausrüstung-Beschreibung",
            ),
            MDDialogContentContainer(
                scroll,
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
            auto_dismiss=True,
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

    # Debounce-Latenz fürs Filtern beim Tippen — verhindert auf Android,
    # dass jeder Tastendruck einen RecycleView-Refresh und damit einen
    # Layout-Pass auslöst, der die IME-Verbindung zur Soft-Tastatur stört
    # (Symptom: Backspace im Suchfeld bleibt wirkungslos).
    _FILTER_DEBOUNCE_S = 0.25

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

    def toggle_only_owned_items(self):
        """
        Schaltet den Filter für vorhandene Gegenstände um.
        Event-Handler für den Button (Android Checkbox Workaround).
        """
        self.only_owned_items = not self.only_owned_items
        self._apply_filter()

    def update_sort_option(self, option):
        """Aktualisiert die Sortieroptionen"""
        if self.current_sort_option == option:
            self.sort_order = 'desc' if self.sort_order == 'asc' else 'asc'
        else:
            self.current_sort_option = option
            self.sort_order = 'asc'

        self._apply_filter()

    def filter_ausruestung(self, *args):
        """
        Plant das Filtern verzögert (Debounce gegen Fokus-Verlust auf
        Android beim Tippen). Sofortige Filteranwendung erfolgt über
        _apply_filter() direkt.
        """
        existing = getattr(self, '_filter_event', None)
        if existing is not None:
            existing.cancel()
        self._filter_event = Clock.schedule_once(
            self._apply_filter, self._FILTER_DEBOUNCE_S
        )

    def _restore_search_focus(self, field):
        """Stellt den Fokus auf dem Suchfeld wieder her, falls verloren."""
        if field and not field.focus:
            field.focus = True

    def _apply_filter(self, _dt=0):
        """Filtert und sortiert die Ausrüstungsgegenstände (synchron)."""
        self._filter_event = None
        if not self.controller or not hasattr(self.controller, 'charakter'):
            self.set_debug_message("Controller oder Charakter nicht verfügbar")
            return

        search_input = self.ids.get('search_input')
        category_label = self.ids.get('category_label')
        search_term = search_input.text.lower() if search_input else ''
        selected_kategorie = category_label.text.lower() if category_label else 'alle kategorien'

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

            # Fokus-Sicherheitsnetz: Der RecycleView-Refresh kann auf Android
            # die IME-Verbindung kurz unterbrechen. Bei aktivem Filtertext den
            # Fokus auf nächstem Frame wiederherstellen.
            if search_input and search_input.text:
                Clock.schedule_once(
                    lambda dt: self._restore_search_focus(search_input), 0
                )
            
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
            
            # Cyberware-spezifische Details
            is_cyberware = getattr(ausruestung, 'kategorie', '') == 'Cyberware'
            if is_cyberware:
                stress = getattr(ausruestung, 'stress', None)
                if stress is not None:
                    details.append(f"Stress: {stress}")
                max_inst = getattr(ausruestung, 'max_installationen', -1)
                if max_inst == -1:
                    details.append("Max: unbegrenzt")
                elif max_inst > 0:
                    details.append(f"Max: {max_inst}")
                unterkategorie = getattr(ausruestung, 'unterkategorie', '')
                if unterkategorie:
                    details.append(f"[{unterkategorie}]")
                return " | ".join(details)

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

        # Initiale Filterung (sofort, kein Debounce beim Init)
        self._apply_filter()

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

        # Filterung erneut anwenden (sofort, da explizite UI-Aktualisierung nach Datenänderung)
        self._apply_filter()

    def open_category_menu(self):
        """Öffnet das Kategorie-Auswahlmenü.

        Verwendet scrollbares SearchBottomSheet mit Suche (für Settings mit vielen Kategorien).
        """
        from views.ui_components import SearchBottomSheet
        current_label = self.ids.get('category_label')
        current = current_label.text if current_label else ALL_CATEGORIES_TEXT
        sheet = SearchBottomSheet(
            title="Kategorie wählen",
            items=[ALL_CATEGORIES_TEXT] + list(self.kategorien),
            selected=current,
            on_confirm=lambda name: self.set_category(name) if name else None,
            search_hint="Kategorie suchen...",
        )
        sheet.open()

    def set_category(self, text):
        """Setzt die ausgewählte Kategorie und aktualisiert die Anzeige"""
        category_label = self.ids.get('category_label')
        if category_label:
            category_label.text = text
        self._apply_filter()

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
class TooltipFabButton(AusruestungTooltip, MDFabButton):
    """Fab Button mit Tooltip Funktionalität"""
    icon = StringProperty()


Factory.register('TooltipIconButton', TooltipIconButton)
Factory.register('TooltipFabButton', TooltipFabButton)
Factory.register('AusruestungItemRow', AusruestungItemRow)

# KV-Datei laden mit PyInstaller-kompatiblem Pfad und Mobile-Unterstützung
from utils.path_utils import get_application_root
from utils.platform_utils import is_mobile_layout, landscape_height
import os

_base_path = str(get_application_root())
_mobile = is_mobile_layout()
_kv_name = 'ausruestung_view_mobile.kv' if _mobile else 'ausruestung_view.kv'
_kv_path = os.path.join(_base_path, 'views', _kv_name)
if not os.path.exists(_kv_path):
    _kv_path = os.path.join(_base_path, 'views', 'ausruestung_view.kv')
Builder.load_file(_kv_path)
Logger.info(f"ausruestung_view: KV-Datei geladen: {os.path.basename(_kv_path)}")