# views/eigenschaften_view.py

from kivy.lang import Builder
from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.event import EventDispatcher
from kivy.clock import Clock
import logging
from kivy.logger import Logger, LOG_LEVELS
from kivy.metrics import dp
from kivy.factory import Factory

# KivyMD Imports
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.gridlayout import MDGridLayout

# Importieren der benutzerdefinierten Module
from controllers.decorators import Fehlerbehandlung
from controllers.charakter_controller import CharakterController

kv = '''
<EigenschaftenWidget>:
    attribute_layout: attribute_layout
    fertigkeiten_layout: fertigkeiten_layout

    MDScrollView:
        size_hint: (1, 1)
        do_scroll_x: False
        do_scroll_y: True

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: "20dp"
            spacing: "10dp"

            MDLabel:
                text: 'Attribute'
                size_hint: (1, None)
                height: "40dp"
                halign: 'left'
                valign: 'middle'

            MDBoxLayout:
                id: attribute_layout
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height

            MDLabel:
                text: 'Fertigkeiten'
                size_hint: (1, None)
                height: "40dp"
                halign: 'left'
                valign: 'middle'

            MDBoxLayout:
                size_hint_y: None
                height: "40dp"
                spacing: "10dp"

                MDLabel:
                    id: sort_spinner
                    text: 'Sortieren nach'
                    size_hint_x: 0.4
                    on_touch_down: 
                        if self.collide_point(*args[1].pos): root.show_sort_menu()

                MDLabel:
                    id: aktiv_spinner
                    text: 'Alle Fertigkeiten'
                    size_hint_x: 0.4
                    on_touch_down:
                        if self.collide_point(*args[1].pos): root.show_filter_menu()

            MDBoxLayout:
                id: fertigkeiten_layout
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height

<EigenschaftenItemRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: "40dp"
    spacing: "5dp"
    adaptive_height: True

    MDLabel:
        text: root.item_type == 'fertigkeit' and root.item_obj and root.item_obj.attribut \
              and f"{root.item_name} ({root.item_obj.attribut.attribut_name})" or root.item_name
        size_hint_x: None
        width: "350dp"
        halign: 'left'
        valign: 'middle'

    # Würfel-Icon-Gruppe
    MDBoxLayout:
        size_hint_x: None
        width: "120dp"
        spacing: "2dp"
        padding: ["10dp", "0dp"]
        
        MDIconButton:
            icon: root.dice_icon
            style: "standard"
            
        MDIconButton:
            icon: root.modifier_sign
            style: "standard"
            opacity: 1 if root.has_modifier else 0
            disabled: not root.has_modifier
            
        MDIconButton:
            icon: root.modifier_value_icon
            style: "standard"
            opacity: 1 if root.has_modifier else 0
            disabled: not root.has_modifier

    MDBoxLayout:
        size_hint_x: None
        width: "50dp"
        padding: ["30dp", "0dp"]

        MDIconButton:
            icon: "arrow-up-thick"
            style: "standard"
            on_release: root.steigere_eigenschaft()

        MDIconButton:
            icon: "arrow-down-thick"
            style: "standard"
            on_release: root.senke_eigenschaft()
'''

Builder.load_string(kv)

class EigenschaftenWidget(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self.controller = app.controller
        # Binde an den Charakter-Änderung
        self.controller.bind(on_charakter_changed=self.on_charakter_changed)

        # Initialisiere Sorting und Filtering Optionen
        self.sort_order = 'asc'
        self.current_sort_field = 'item_name'
        self.filter_aktiviert = 'Alle Fertigkeiten'
        
        # Dropdown Menüs erstellen
        self.sort_menu = None
        self.filter_menu = None

    def create_sort_menu(self):
        """Erstellt das Sortier-Menü"""
        menu_items = [
            {
                "text": item,
                "on_release": lambda x=item: self.set_sort_option(x),
            } for item in ["Name (aufsteigend)", "Name (absteigend)", 
                         "Wert (aufsteigend)", "Wert (absteigend)"]
        ]
        
        self.sort_menu = MDDropdownMenu(
            caller=self.ids.sort_spinner,
            items=menu_items,
            width_mult=4,
        )

    def create_filter_menu(self):
        """Erstellt das Filter-Menü"""
        menu_items = [
            {
                "text": item,
                "on_release": lambda x=item: self.set_filter_option(x),
            } for item in ["Alle Fertigkeiten", "Aktiviert", "Nicht Aktiviert"]
        ]
        
        self.filter_menu = MDDropdownMenu(
            caller=self.ids.aktiv_spinner,
            items=menu_items,
            width_mult=4,
        )

    def show_sort_menu(self, *args):
        """Zeigt das Sortier-Menü an"""
        if not self.sort_menu:
            self.create_sort_menu()
        self.sort_menu.open()

    def show_filter_menu(self, *args):
        """Zeigt das Filter-Menü an"""
        if not self.filter_menu:
            self.create_filter_menu()
        self.filter_menu.open()

    def set_sort_option(self, text):
        """Setzt die Sortieroption und aktualisiert die Anzeige"""
        self.ids.sort_spinner.text = text
        self.sort_menu.dismiss()
        self.update_sort_option()

    def set_filter_option(self, text):
        """Setzt die Filteroption und aktualisiert die Anzeige"""
        self.ids.aktiv_spinner.text = text
        self.filter_menu.dismiss()
        self.update_filter_option()

    def on_kv_post(self, base_widget):
        # Diese Methode wird aufgerufen, nachdem die .kv-Datei geladen wurde
        self.update_eigenschaften()

    def on_charakter_changed(self, instance, *args):
        # Aktualisiere die Eigenschaften, wenn der Charakter im Controller geändert wird
        self.update_eigenschaften()

    def update_sort_option(self):
        selected_text = self.ids.sort_spinner.text
        if ' (aufsteigend)' in selected_text:
            sort_option = selected_text.replace(' (aufsteigend)', '')
            sort_order = 'asc'
        elif ' (absteigend)' in selected_text:
            sort_option = selected_text.replace(' (absteigend)', '')
            sort_order = 'desc'
        else:
            sort_option = selected_text
            sort_order = 'asc'

        # Map the sort option to the field name
        sort_field_mapping = {
            'Name': 'item_name',
            'Wert': 'wert'
        }

        self.current_sort_field = sort_field_mapping.get(sort_option, 'item_name')
        self.sort_order = sort_order

        Logger.debug(f"Sortieroption aktualisiert: Feld={self.current_sort_field}, Reihenfolge={self.sort_order}")

        # Aktualisieren der Fertigkeiten
        self.update_eigenschaften()

    def update_filter_option(self):
        self.filter_aktiviert = self.ids.aktiv_spinner.text
        Logger.debug(f"Filteroption aktualisiert: Aktiviert={self.filter_aktiviert}")
        # Aktualisieren der Fertigkeiten
        self.update_eigenschaften()

    def update_eigenschaften(self):
        charakter = self.controller.charakter  # Direkt aus dem Controller beziehen

        # Überprüfe, ob attribute_layout initialisiert ist
        if self.attribute_layout is None or self.fertigkeiten_layout is None:
            Logger.error("EigenschaftenWidget: attribute_layout oder fertigkeiten_layout ist None")
            return

        # Zuerst leeren wir die Layouts
        self.attribute_layout.clear_widgets()
        self.fertigkeiten_layout.clear_widgets()

        # Attribute hinzufügen
        for attribut in charakter.attribute.values():
            item = EigenschaftenItemRow(
                item_name=attribut.attribut_name,
                item_obj=attribut,
                item_type='attribute',
                controller=self.controller
            )
            self.attribute_layout.add_widget(item)

        # Fertigkeiten hinzufügen

        # Fertigkeiten sammeln
        fertigkeiten_liste = list(charakter.fertigkeiten.values())

        # Filtern nach 'filter_aktiviert'
        if self.filter_aktiviert == 'Aktiviert':
            fertigkeiten_liste = [f for f in fertigkeiten_liste if f.modifier != -2]
        elif self.filter_aktiviert == 'Nicht Aktiviert':
            fertigkeiten_liste = [f for f in fertigkeiten_liste if f.modifier == -2]
        # else 'Alle Fertigkeiten', keine Filterung

        # Sortieren
        reverse = (self.sort_order == 'desc')
        if self.current_sort_field == 'item_name':
            fertigkeiten_liste.sort(key=lambda f: f.fertigkeit_name.lower(), reverse=reverse)
        elif self.current_sort_field == 'wert':
            # Sortieren nach dem numerischen Wert des Attributs 'wert'
            fertigkeiten_liste.sort(key=lambda f: (f.wert if f.wert is not None else 0), reverse=reverse)
        else:
            # Standardmäßig nach Name sortieren
            fertigkeiten_liste.sort(key=lambda f: f.fertigkeit_name.lower(), reverse=reverse)

        # Jetzt die sortierten und gefilterten Fertigkeiten hinzufügen
        for fertigkeit in fertigkeiten_liste:
            item = EigenschaftenItemRow(
                item_name=fertigkeit.fertigkeit_name,
                item_obj=fertigkeit,
                item_type='fertigkeit',
                controller=self.controller
            )
            self.fertigkeiten_layout.add_widget(item)

        Logger.info("EigenschaftenWidget: Eigenschaften aktualisiert.")

class EigenschaftenItemRow(MDBoxLayout):
    item_name = StringProperty('')
    item_obj = ObjectProperty(None)
    item_type = StringProperty('')
    controller = ObjectProperty(None)
    dice_icon = StringProperty('dice-d6')  # Standard-Icon
    modifier_sign = StringProperty('minus')
    modifier_value_icon = StringProperty('numeric-1')
    has_modifier = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_dice_display()
        if self.item_obj:
            self.item_obj.bind(wert=self.on_item_obj_changed)
            self.item_obj.bind(modifier=self.on_item_obj_changed)

    def on_item_obj_changed(self, instance, value):
        self.update_dice_display()

    def update_dice_display(self):
        """Aktualisiert die Würfel-Icons basierend auf dem Wert"""
        if self.item_obj:
            # Würfel-Icon setzen
            self.dice_icon = f"dice-d{self.item_obj.wert}"
            
            # Modifier-Anzeige aktualisieren
            if self.item_obj.modifier != 0:
                self.has_modifier = True
                self.modifier_sign = "plus" if self.item_obj.modifier > 0 else "minus"
                # Setze das numerische Icon basierend auf dem Modifier-Wert
                abs_modifier = abs(self.item_obj.modifier)
                self.modifier_value_icon = f"numeric-{abs_modifier}"
            else:
                self.has_modifier = False

    def steigere_eigenschaft(self):
        if self.item_type == 'attribute':
            self.controller.steigere_attribut(self.item_name)
        elif self.item_type == 'fertigkeit':
            self.controller.steigere_fertigkeit(self.item_name)
        else:
            Logger.warning(f"Unbekannter Typ: {self.item_type}")

    def senke_eigenschaft(self):
        if self.item_type == 'attribute':
            self.controller.senke_attribut(self.item_name)
        elif self.item_type == 'fertigkeit':
            self.controller.senke_fertigkeit(self.item_name)
        else:
            Logger.warning(f"Unbekannter Typ: {self.item_type}")
