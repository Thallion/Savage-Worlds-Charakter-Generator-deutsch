# views/eigenschaften_view.py

from kivy.lang import Builder
from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty
from kivy.clock import Clock, mainthread
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.cache import Cache
from threading import Thread
from kivy.uix.modalview import ModalView
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.widget import Widget

# KivyMD Imports
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDButton, MDIconButton, MDFabButton, MDButtonText
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator.progressindicator import MDCircularProgressIndicator  # Aktualisierter Import für 2.0.1

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer
)

# Cache für Würfel-Icons einrichten
Cache.register('wuerfel_icons', limit=20)

# Domänen-spezifische Konstanten
SORTIER_OPTIONEN = {
    "NAME_ASC": "Name (aufsteigend)",
    "NAME_DESC": "Name (absteigend)",
    "WERT_ASC": "Wert (aufsteigend)",
    "WERT_DESC": "Wert (absteigend)"
}

FILTER_OPTIONEN = {
    "ALLE": "Alle Fertigkeiten",
    "AKTIV": "Aktiviert",
    "INAKTIV": "Nicht Aktiviert"
}

# KV-Datei laden
Builder.load_file('views/eigenschaften_view.kv')

# Kein Dialog mehr benötigt, stattdessen nur der Indicator


# Modifikation in der IconCache-Klasse

class IconCache:
    """
    Cache für häufig verwendete Icons, um wiederholtes Laden zu vermeiden.
    Implements Singleton-Pattern für effizientes Resource-Management.
    """
    # Vorberechnete Icons für häufige Werte 
    _DICE_ICONS = {
        4: "dice-d4", 
        6: "dice-d6", 
        8: "dice-d8", 
        10: "dice-d10", 
        12: "dice-d12"
    }
    
    _MODIFIER_ICONS = {
        0: "numeric-0",
        1: "numeric-1",
        2: "numeric-2",
        3: "numeric-3",
        4: "numeric-4",
        5: "numeric-5",
        6: "numeric-6",
        7: "numeric-7",
        8: "numeric-8",
        9: "numeric-9",
        10: "numeric-10"
    }
    
    _MODIFIER_SIGNS = {
        True: "plus",  # positiver Modifier
        False: "minus"  # negativer Modifier
    }
    
    @classmethod
    def get_dice_icon(cls, wert):
        """Gibt ein gecachtes Würfel-Icon für einen Würfelwert zurück"""
        cache_key = f"dice_{wert}"
        
        icon = Cache.get('wuerfel_icons', cache_key)
        if icon:
            return icon
        
        icon = cls._DICE_ICONS.get(wert, f"dice-d{wert}")
        Cache.append('wuerfel_icons', cache_key, icon)
        return icon

    @classmethod
    def get_modifier_icon(cls, modifier):
        """
        Gibt ein gecachtes numerisches Icon für einen Modifier zurück.
        Bei zweistelligen Zahlen wird nur die erste Ziffer zurückgegeben.
        
        Returns:
            str: Der Icon-Name für den Modifikator
        """
        abs_mod = abs(modifier)
        
        # Für einstellige und 10 direkt zurückgeben
        if abs_mod <= 10:
            cache_key = f"mod_{abs_mod}"
            icon = Cache.get('wuerfel_icons', cache_key)
            if icon:
                return icon
                
            icon = cls._MODIFIER_ICONS.get(abs_mod, f"numeric-{abs_mod}")
            Cache.append('wuerfel_icons', cache_key, icon)
            return icon
        
        # Bei zweistelligen Zahlen die erste Ziffer zurückgeben
        first_digit = abs_mod // 10
        cache_key = f"mod_{first_digit}"
        icon = Cache.get('wuerfel_icons', cache_key)
        if icon:
            return icon
            
        icon = cls._MODIFIER_ICONS.get(first_digit, f"numeric-{first_digit}")
        Cache.append('wuerfel_icons', cache_key, icon)
        return icon
    
    @classmethod
    def get_second_digit_icon(cls, modifier):
        """
        Gibt ein gecachtes numerisches Icon für die zweite Ziffer eines zweistelligen Modifikators zurück.
        
        Returns:
            str: Der Icon-Name für die zweite Ziffer, oder None wenn einstellig
        """
        abs_mod = abs(modifier)
        
        # Wenn einstellig oder genau 10, keine zweite Ziffer
        if abs_mod <= 10:
            return None
            
        # Bei zweistelligen Zahlen die zweite Ziffer zurückgeben
        second_digit = abs_mod % 10
        cache_key = f"mod_{second_digit}"
        
        icon = Cache.get('wuerfel_icons', cache_key)
        if icon:
            return icon
            
        icon = cls._MODIFIER_ICONS.get(second_digit, f"numeric-{second_digit}")
        Cache.append('wuerfel_icons', cache_key, icon)
        return icon
        
    @classmethod
    def get_modifier_sign(cls, is_positive):
        """Gibt das entsprechende Vorzeichen-Icon zurück"""
        return cls._MODIFIER_SIGNS[is_positive]


class EigenschaftenWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Bearbeitung von Attributen und Fertigkeiten eines Charakters.
    Optimiert für schnellere Render-Performance mit Threading und UI-Feedback.
    """
    _update_ausstehend = False
    _thread = None
    char_gen_completed = BooleanProperty(False)


    def __init__(self, **kwargs):
        """Initialisiert das EigenschaftenWidget mit verzögertem Setup"""
        super().__init__(**kwargs)
        # Initialisiere den Controller aus der App
        app = MDApp.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None

        # Status einmal initial setzen (keine Bindung)
        Clock.schedule_once(self._update_char_gen_status, 0.1)

        # Initialisierung verzögern und Loading-Indicator anzeigen
        self._zeige_lade_indicator()
        Clock.schedule_once(self._verzoegerte_initialisierung, 0.1)

    def _zeige_lade_indicator(self):
        """Zeigt den Ladeindikator direkt im Layout an"""
        if not hasattr(self, '_lade_indicator') or not self._lade_indicator:
            self._lade_indicator = MDCircularProgressIndicator(
                size_hint=(None, None),
                size=(dp(46), dp(46)),
                active=True,
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            self.add_widget(self._lade_indicator)

    def _verzoegerte_initialisierung(self, dt):
        """Führt die Initialisierung in einem separaten Thread aus"""
        self._initialisiere_controller()
        self._initialisiere_sortieroptionen()
        self._initialisiere_menues()
        
        # Starte Thread für das Laden der Daten
        self._thread = Thread(target=self._lade_daten_im_hintergrund)
        self._thread.daemon = True
        self._thread.start()

    def _initialisiere_controller(self):
        """Initialisiert die Controller-Verbindung gemäß MVC-Pattern"""
        app = App.get_running_app()
        self.controller = app.controller
        # Binde an den Charakter-Änderung-Event mit Verzögerung
        self.controller.bind(on_charakter_changed=self._plane_update)
        # Bei Charakter-Laden: Status der Checkbox aktualisieren
        self.controller.bind(on_charakter_loaded=self._update_char_gen_status)

    def _initialisiere_sortieroptionen(self):
        """Initialisiert Sortier- und Filteroptionen"""
        self.sort_order = 'asc'
        self.current_sort_field = 'item_name'
        self.filter_aktiviert = FILTER_OPTIONEN["ALLE"]

    def _initialisiere_menues(self):
        """Initialisiert Dropdown-Menüs (lazy loading)"""
        self.sort_menu = None
        self.filter_menu = None

    def _lade_daten_im_hintergrund(self):
        """Thread-Methode zum Laden und Vorverarbeiten der Daten"""
        try:
            # Zugriff auf Charakterdaten
            charakter = self.controller.charakter
            
            # Attribut-Daten vorverarbeiten
            attribute_liste = list(charakter.attribute.values())
            attribute_widgets = []
            
            # Vorbereite Attribute-Widgets
            for attribut in attribute_liste:
                item = {
                    'item_name': attribut.attribut_name,
                    'item_obj': attribut,
                    'item_type': 'attribute',
                    'controller': self.controller,
                    'dice_icon': IconCache.get_dice_icon(attribut.wert),
                    'modifier_sign': IconCache.get_modifier_sign(attribut.modifier > 0),
                    'modifier_value_icon': IconCache.get_modifier_icon(attribut.modifier),
                    'has_modifier': attribut.modifier != 0
                }
                attribute_widgets.append(item)
            
            # Fertigkeiten vorverarbeiten
            fertigkeiten_liste = self._hole_gefilterte_fertigkeiten(charakter)
            fertigkeiten_liste = self._sortiere_fertigkeiten(fertigkeiten_liste)
            
            # Fertigkeiten-Widgets vorbereiten
            fertigkeiten_widgets = []
            for fertigkeit in fertigkeiten_liste:
                item = {
                    'item_name': fertigkeit.fertigkeit_name,
                    'item_obj': fertigkeit,
                    'item_type': 'fertigkeit',
                    'controller': self.controller,
                    'dice_icon': IconCache.get_dice_icon(fertigkeit.wert),
                    'modifier_sign': IconCache.get_modifier_sign(fertigkeit.modifier > 0),
                    'modifier_value_icon': IconCache.get_modifier_icon(fertigkeit.modifier),
                    'has_modifier': fertigkeit.modifier != 0
                }
                fertigkeiten_widgets.append(item)
            
            # Aufbereitet Daten an den Hauptthread senden
            self._aktualisiere_ui_im_hauptthread(attribute_widgets, fertigkeiten_widgets)
            
        except Exception as e:
            Logger.error(f"Fehler beim Laden der Daten im Hintergrund: {e}")
            # Fehler behandeln und Indicator entfernen
            self._entferne_lade_indicator()
    
    @mainthread
    def _aktualisiere_ui_im_hauptthread(self, attribute_widgets, fertigkeiten_widgets):
        """Aktualisiert die UI im Hauptthread mit den vorbereiteten Daten"""
        # Entferne Lade-Indicator
        self._entferne_lade_indicator()
        
        # Füge Attribute-Widgets hinzu
        if hasattr(self, 'attribute_layout'):
            self.attribute_layout.clear_widgets()
            for widget_data in attribute_widgets:
                item = EigenschaftenItemRow(**widget_data)
                self.attribute_layout.add_widget(item)
        
        # Füge Fertigkeiten-Widgets hinzu (mit Lazy-Loading)
        if hasattr(self, 'fertigkeiten_layout'):
            self.fertigkeiten_layout.clear_widgets()
            self._fuege_fertigkeiten_widget_hinzu_mit_lazy_loading(fertigkeiten_widgets)
    
    def _fuege_fertigkeiten_widget_hinzu_mit_lazy_loading(self, fertigkeiten_widgets):
        """Fügt Fertigkeiten-Widgets stufenweise hinzu, um UI-Ruckler zu vermeiden"""
        BATCH_SIZE = 30  # Anzahl der Widgets pro Batch
        
        if not fertigkeiten_widgets:
            return
            
        batch = fertigkeiten_widgets[:BATCH_SIZE]
        rest = fertigkeiten_widgets[BATCH_SIZE:]
        
        # Aktuellen Batch hinzufügen
        for widget_data in batch:
            item = EigenschaftenItemRow(**widget_data)
            self.fertigkeiten_layout.add_widget(item)
        
        # Rest verzögert laden
        if rest:
            Clock.schedule_once(
                lambda dt: self._fuege_fertigkeiten_widget_hinzu_mit_lazy_loading(rest), 
                0.05
            )
    
    @mainthread
    def _entferne_lade_indicator(self):
        """Entfernt den Ladeindikator aus dem Layout"""
        if hasattr(self, '_lade_indicator') and self._lade_indicator:
            self.remove_widget(self._lade_indicator)
            self._lade_indicator = None

    def _erstelle_sort_menu(self):
        """Erstellt das Sortier-Menü mit allen Optionen"""
        menu_items = [
            {
                "text": option,
                "on_release": lambda x=option: self._setze_sort_option(x),
            } for option in SORTIER_OPTIONEN.values()
        ]

        self.sort_menu = MDDropdownMenu(
            caller=self.ids.sort_spinner,
            items=menu_items,
            width_mult=4,
        )

    def _erstelle_filter_menu(self):
        """Erstellt das Filter-Menü mit allen Optionen"""
        menu_items = [
            {
                "text": option,
                "on_release": lambda x=option: self._setze_filter_option(x),
            } for option in FILTER_OPTIONEN.values()
        ]

        self.filter_menu = MDDropdownMenu(
            caller=self.ids.aktiv_spinner,
            items=menu_items,
            width_mult=4,
        )

    def show_sort_menu(self, *args):
        """Zeigt das Sortier-Menü an"""
        if not self.sort_menu:
            self._erstelle_sort_menu()
        self.sort_menu.open()

    def show_filter_menu(self, *args):
        """Zeigt das Filter-Menü an"""
        if not self.filter_menu:
            self._erstelle_filter_menu()
        self.filter_menu.open()

    def _setze_sort_option(self, text):
        """Setzt die Sortieroption und aktualisiert die Anzeige"""
        self.ids.sort_spinner.text = text
        self.sort_menu.dismiss()
        self._aktualisiere_sort_option()

    def _setze_filter_option(self, text):
        """Setzt die Filteroption und aktualisiert die Anzeige"""
        self.ids.aktiv_spinner.text = text
        self.filter_menu.dismiss()
        self._aktualisiere_filter_option()

    def on_kv_post(self, base_widget):
        """Wird aufgerufen, nachdem die .kv-Datei geladen wurde"""
        pass  # Nicht mehr benötigt, da Initialisierung bereits in __init__ erfolgt

    def _plane_update(self, instance, *args):
        """
        Plant ein Update des Widgets zu einem späteren Zeitpunkt.
        Zeigt den Lade-Indicator an, wenn ein vollständiges Update angefordert wird.
        """
        if not self._update_ausstehend:
            self._update_ausstehend = True
            self._zeige_lade_indicator()
            # Verzögert ausführen
            Clock.schedule_once(self._starte_update_thread, 0.05)

    def _starte_update_thread(self, dt):
        """Startet einen Thread für das Daten-Update"""
        self._update_ausstehend = False
        
        # Sicherstellen, dass kein anderer Thread läuft
        if self._thread and self._thread.is_alive():
            # Warten, bis der Thread beendet ist - sollte normalerweise nicht vorkommen
            self._thread.join(0.5) 
        
        # Neuen Thread starten
        self._thread = Thread(target=self._lade_daten_im_hintergrund)
        self._thread.daemon = True
        self._thread.start()

    def _aktualisiere_sort_option(self):
        """Aktualisiert die Sortieroptionen basierend auf der Auswahl"""
        selected_text = self.ids.sort_spinner.text
        
        # Parse die ausgewählte Option
        if ' (aufsteigend)' in selected_text:
            sort_option = selected_text.replace(' (aufsteigend)', '')
            sort_order = 'asc'
        elif ' (absteigend)' in selected_text:
            sort_option = selected_text.replace(' (absteigend)', '')
            sort_order = 'desc'
        else:
            sort_option = selected_text
            sort_order = 'asc'

        # Mapping der Sortieroption zum Feldnamen
        sort_field_mapping = {
            'Name': 'item_name',
            'Wert': 'wert'
        }

        self.current_sort_field = sort_field_mapping.get(sort_option, 'item_name')
        self.sort_order = sort_order

        # Plane ein Update mit Thread
        self._plane_update(None)

    def _aktualisiere_filter_option(self):
        """Aktualisiert die Filteroptionen basierend auf der Auswahl"""
        self.filter_aktiviert = self.ids.aktiv_spinner.text

        # Plane ein Update mit Thread
        self._plane_update(None)

    def update_eigenschaften(self):
        """Öffentliche API-Methode für den Controller"""
        self._plane_update(None)
    
    def _hole_gefilterte_fertigkeiten(self, charakter):
        """Wendet Filter auf die Fertigkeiten-Liste an (Thread-sicher)"""
        fertigkeiten_liste = list(charakter.fertigkeiten.values())
        
        # Filterung anwenden
        if self.filter_aktiviert == FILTER_OPTIONEN["AKTIV"]:
            return [f for f in fertigkeiten_liste if f.modifier != -2]
        elif self.filter_aktiviert == FILTER_OPTIONEN["INAKTIV"]:
            return [f for f in fertigkeiten_liste if f.modifier == -2]
        
        # Keine Filterung für "Alle Fertigkeiten"
        return fertigkeiten_liste
    
    def _sortiere_fertigkeiten(self, fertigkeiten_liste):
        """Sortiert die Fertigkeiten-Liste (Thread-sicher)"""
        reverse = (self.sort_order == 'desc')
        
        if self.current_sort_field == 'item_name':
            return sorted(fertigkeiten_liste, 
                         key=lambda f: f.fertigkeit_name.lower(), 
                         reverse=reverse)
        elif self.current_sort_field == 'wert':
            return sorted(fertigkeiten_liste,
                         key=lambda f: (f.wert if f.wert is not None else 0), 
                         reverse=reverse)
        else:
            # Standardmäßig nach Name sortieren
            return sorted(fertigkeiten_liste, 
                         key=lambda f: f.fertigkeit_name.lower(), 
                         reverse=reverse)

    def toggle_char_gen_completed(self, value):
        """Umschaltet den Charakter-Generierungsstatus."""
        if self.controller and self.controller.charakter:
            self.controller.charakter.char_gen_completed = value
            Logger.debug(f"Charakter-Generierungsstatus geändert: {value}")

    def _update_char_gen_status(self, *args):
        if self.controller and self.controller.charakter:
            self.char_gen_completed = self.controller.charakter.char_gen_completed

class EigenschaftenItemRow(MDBoxLayout):
    """
    Einzelne Zeile für ein Attribut oder eine Fertigkeit.
    Optimiert für Rendering-Performance.
    """
    # Properties für Datenbindung
    item_name = StringProperty('')
    item_obj = ObjectProperty(None)
    item_type = StringProperty('')
    controller = ObjectProperty(None)
    
    # Icons (voroptimiert in der __init__)
    dice_icon = StringProperty('dice-d6')
    modifier_sign = StringProperty('minus')
    modifier_value_icon = StringProperty('numeric-1')
    second_digit_icon = StringProperty('numeric-0')  # Neu: Icon für die zweite Ziffer
    has_modifier = BooleanProperty(False)
    has_second_digit = BooleanProperty(False)  # Neu: Zeigt an, ob eine zweite Ziffer vorhanden ist
    
    # Dictionary zum Cachen von eigenschaften
    eigenschaften_cache = DictProperty({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Werte sofort bei der Initialisierung vorberechnen
        if self.item_obj:
            self._update_eigenschaften_cache()
            # Bindings mit Verzögerung einrichten
            self.item_obj.bind(wert=self._plane_update)
            self.item_obj.bind(modifier=self._plane_update)
    
    def _update_eigenschaften_cache(self):
        """Aktualisiert den Cache der Eigenschaften"""
        if not self.item_obj:
            return
            
        self.eigenschaften_cache.update({
            'wert': self.item_obj.wert,
            'modifier': self.item_obj.modifier,
        })
        
    def _plane_update(self, instance, value):
        """Plant ein Update mit Verzögerung"""
        # Prüfen, ob sich relevante Werte tatsächlich geändert haben
        if (self.eigenschaften_cache.get('wert') != self.item_obj.wert or
            self.eigenschaften_cache.get('modifier') != self.item_obj.modifier):
            # Nur bei Änderung aktualisieren
            Clock.schedule_once(self._verzoeges_update, 0.05)
    
    def _verzoeges_update(self, dt):
        """Führt ein verzögertes Update der Anzeige aus"""
        self._update_eigenschaften_cache()
        self.update_dice_display()

    def update_dice_display(self):
        """Aktualisiert die Würfel-Icons effizient aus dem Cache"""
        if not self.item_obj:
            return
            
        # Werte aus dem Cache oder direkt aus dem Objekt holen
        wert = self.eigenschaften_cache.get('wert', self.item_obj.wert)
        modifier = self.eigenschaften_cache.get('modifier', self.item_obj.modifier)
        
        # Optimierte Icon-Zuweisung
        self.dice_icon = IconCache.get_dice_icon(wert)
        
        # Modifier-Anzeige
        if modifier != 0:
            self.has_modifier = True
            is_positive = modifier > 0
            self.modifier_sign = IconCache.get_modifier_sign(is_positive)
            self.modifier_value_icon = IconCache.get_modifier_icon(modifier)
            
            # Prüfen, ob zweistellig und zweites Icon setzen
            second_digit_icon = IconCache.get_second_digit_icon(modifier)
            if second_digit_icon:
                self.second_digit_icon = second_digit_icon
                self.has_second_digit = True
            else:
                self.has_second_digit = False
        else:
            self.has_modifier = False
            self.has_second_digit = False

    def steigere_eigenschaft(self):
        """Erhöht den Wert einer Eigenschaft über den Controller."""
        if not self.controller:
            Logger.error("EigenschaftenItemRow: controller ist nicht gesetzt")
            return
                
        if self.item_type == 'attribute':
            self.controller.steigere_attribut(self.item_name)
        elif self.item_type == 'fertigkeit':
            result = self.controller.steigere_fertigkeit(self.item_name)
            if result == "needs_confirmation":
                self._show_double_cost_dialog()
        else:
            Logger.warning(f"Unbekannter Eigenschaftstyp: {self.item_type}")

    def _show_double_cost_dialog(self):
        """Zeigt einen Dialog zur Bestätigung der doppelten Kosten an."""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        # Label mit ausreichender Höhe und ohne Größenbeschränkung
        warning_label = MDLabel(
            text="Vorsicht doppelte Kosten, wenn die Fertigkeit das zugehörige Attribut übersteigt! Trotzdem steigern?",
            size_hint_y=None,
            height=dp(80),  # Mehr Höhe für den Text
            theme_text_color="Secondary",  # Sicherstellen, dass der Text gut sichtbar ist
            halign="left",
            valign="middle"
        )
        content.add_widget(warning_label)
        
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text="Kosten-Warnung",
            ),
            MDDialogContentContainer(
                content,
                orientation="vertical",
                padding=dp(0),  # Weniger Padding im Container
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Abbrechen"),
                    style="text",
                    on_release=lambda x: self.close_dialog(),
                ),
                MDButton(
                    MDButtonText(text="Ja"),
                    style="text",
                    on_release=lambda x: self._confirm_double_cost(),
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def close_dialog(self):
        """Schließt den Dialog."""
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()

    def _confirm_double_cost(self):
        """Führt die Steigerung mit bestätigten doppelten Kosten durch."""
        self.close_dialog()
        self.controller.steigere_fertigkeit(self.item_name, confirm_double_cost=True)

    def senke_eigenschaft(self):
        """Verringert den Wert einer Eigenschaft über den Controller."""
        if not self.controller:
            Logger.error("EigenschaftenItemRow: controller ist nicht gesetzt")
            return
            
        if self.item_type == 'attribute':
            self.controller.senke_attribut(self.item_name)
        elif self.item_type == 'fertigkeit':
            self.controller.senke_fertigkeit(self.item_name)
        else:
            Logger.warning(f"Unbekannter Eigenschaftstyp: {self.item_type}")