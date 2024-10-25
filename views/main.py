from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.event import EventDispatcher
# from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
# from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
#from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
# from kivy.uix.checkbox import CheckBox
# from kivy.uix.anchorlayout import AnchorLayout
# from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
# from kivy.uix.filechooser import FileChooserListView
# from kivy.uix.popup import Popup
# from kivy.uix.widget import Widget
# from kivy.uix.screenmanager import ScreenManager, Screen
# from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
import sys, os, ctypes, math, json, functools, unittest
from functools import partial

from kivy.logger import Logger, LOG_LEVELS

# Setze Kivy Logger-Level auf DEBUG
Logger.setLevel(LOG_LEVELS['debug'])
Logger.info("Kivy Logger auf DEBUG-Level gesetzt.")

# Füge den übergeordneten Ordner zum sys.path hinzu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
Logger.info("Parent directory added to sys.path.")

# Importieren der benutzerdefinierten Module
from controllers.decorators import Fehlerbehandlung
from controllers.charakter_controller import CharakterController
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.charakter import Waffe, Ruestung


# Laden der main.kv Datei
current_dir = os.path.dirname(os.path.abspath(__file__))
kv_path = os.path.join(current_dir, 'main.kv')
Builder.load_file(kv_path)
Logger.info("main.kv file loaded.")

# Definition des RootWidget
class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.bind_tab_switch, 0)

    def bind_tab_switch(self, dt):
        tabbed_panel = self.ids.main_tabbed_panel
        tabbed_panel.bind(on_switch_to=self.on_tab_switch)

    def on_tab_switch(self, instance, switch_to, *args):
        if switch_to.text == 'Charakter':
            Logger.debug("Charakterbogen-Tab ausgewählt. Aktualisiere Übersicht.")
            charakterbogen_widget = switch_to.ids.charakterbogen_widget if hasattr(switch_to, 'ids') else switch_to.children[0]
            charakterbogen_widget.update_overview(0)

# Definition der LeftAlignedLabel-Klasse
class LeftAlignedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = 'left'
        self.valign = 'middle'
        self.text_size = (self.width, None)
        self.bind(width=self._update_text_size)

    def _update_text_size(self, *args):
        self.text_size = (self.width, None)

class GenerationPointsBar(BoxLayout):
    charakter = ObjectProperty(None)  # Verweis auf das Charakter-Objekt
    attribut_text = StringProperty("")  # Text für Attribut-Punkte
    faehigkeiten_text = StringProperty("")  # Text für Fähigkeiten-Punkte
    aufstiege_text = StringProperty("")  # Kombiniertes Text für Aufstiege
    maechte_text = StringProperty("")  # Text für Mächte
    machtpunkte_text = StringProperty("")  # Text für Machtpunkte
    vermoegen_text = StringProperty("")  # Text für Vermögen
    zusaetzliche_talente_text = StringProperty("")  # Text für zusätzliche Talente
    gesamt_handicap_punkte_text = StringProperty("")  # Text für Gesamt-Handicap-Punkte
    gewicht_text = StringProperty("")  # Kombiniertes Text für Gewicht
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(charakter=self.on_charakter)
        Logger.debug("GenerationPointsBar initialisiert.")

    def on_charakter(self, instance, charakter):
        if charakter:
            Logger.debug("Charakter wurde gesetzt in GenerationPointsBar.")
            # Initialisieren der Text-Properties
            self.attribut_text = f"Attribute-Punkte: {charakter.verbleibende_attributsteigerungen} / {charakter.maximale_attributsteigerungen}"
            self.faehigkeiten_text = f"Fähigkeiten-Punkte: {charakter.verbleibende_fertigkeitssteigerungen} / {charakter.maximale_fertigkeitssteigerungen}"
            self.aufstiege_text = f"Aufstiege: {charakter.verbleibende_aufstiege} / {charakter.aufstiege_gesamt}"
            self.maechte_text = f"Mächte: {charakter.verfuegbare_maechte}"
            self.machtpunkte_text = f"Machtpunkte: {charakter.machtpunkte}"
            self.vermoegen_text = f"Vermögen: {charakter.vermoegen} G"
            self.zusaetzliche_talente_text = f"Talent-Punkte: {charakter.zusaetzliche_talente}"
            self.gesamt_handicap_punkte_text = f"Handicap-Punkte: {charakter.gesamt_handicap_punkte}"
            self.gewicht_text = f"Gewicht: {charakter.gesamtgewicht} / {charakter.maximale_traglast} kg"

            # Bindings zu den Änderungen der Charakter-Properties
            charakter.bind(verbleibende_attributsteigerungen=self.update_attribut_text)
            charakter.bind(maximale_attributsteigerungen=self.update_attribut_text)
            charakter.bind(verbleibende_fertigkeitssteigerungen=self.update_faehigkeiten_text)
            charakter.bind(maximale_fertigkeitssteigerungen=self.update_faehigkeiten_text)
            charakter.bind(verbleibende_aufstiege=self.update_aufstiege_text)
            charakter.bind(aufstiege_gesamt=self.update_aufstiege_text)
            charakter.bind(verfuegbare_maechte=self.update_maechte_text)
            charakter.bind(machtpunkte=self.update_machtpunkte_text)
            charakter.bind(vermoegen=self.update_vermoegen_text)
            charakter.bind(zusaetzliche_talente=self.update_zusaetzliche_talente_text)
            charakter.bind(gesamt_handicap_punkte=self.update_gesamt_handicap_punkte_text)
            charakter.bind(gesamtgewicht=self.update_gewicht_text)
            charakter.bind(maximale_traglast=self.update_gewicht_text)

            Logger.info("GenerationPointsBar ist mit Charakter verbunden.")
        else:
            Logger.warning("GenerationPointsBar: Charakter ist None.")

    def update_attribut_text(self, instance, value):
        self.attribut_text = f"Attribute-Punkte: {self.charakter.verbleibende_attributsteigerungen} / {self.charakter.maximale_attributsteigerungen}"
        Logger.debug(f"Attribut-Punkte aktualisiert: {self.attribut_text}")

    def update_faehigkeiten_text(self, instance, value):
        self.faehigkeiten_text = f"Fähigkeiten-Punkte: {self.charakter.verbleibende_fertigkeitssteigerungen} / {self.charakter.maximale_fertigkeitssteigerungen}"
        Logger.debug(f"Fähigkeiten-Punkte aktualisiert: {self.faehigkeiten_text}")

    def update_aufstiege_text(self, instance, value):
        self.aufstiege_text = f"Aufstiege: {self.charakter.verbleibende_aufstiege} / {self.charakter.aufstiege_gesamt}"
        Logger.debug(f"Aufstiege aktualisiert: {self.aufstiege_text}")

    def update_maechte_text(self, instance, value):
        self.maechte_text = f"Mächte-Punkte: {value}"
        Logger.debug(f"Mächte aktualisiert: {self.maechte_text}")

    def update_machtpunkte_text(self, instance, value):
        self.machtpunkte_text = f"Machtpunkte: {value}"
        Logger.debug(f"Machtpunkte aktualisiert: {self.machtpunkte_text}")

    def update_vermoegen_text(self, instance, value):
        self.vermoegen_text = f"Vermögen: {value} G"
        Logger.debug(f"Vermögen aktualisiert: {self.vermoegen_text}")

    def update_zusaetzliche_talente_text(self, instance, value):
        self.zusaetzliche_talente_text = f"Talent-Punkte: {value}"
        Logger.debug(f"Zusätzliche Talente aktualisiert: {self.zusaetzliche_talente_text}")

    def update_gesamt_handicap_punkte_text(self, instance, value):
        self.gesamt_handicap_punkte_text = f"Handicap-Punkte: {value}"
        Logger.debug(f"Gesamt-Handicap-Punkte aktualisiert: {self.gesamt_handicap_punkte_text}")

    def update_gewicht_text(self, instance, value):
        self.gewicht_text = f"Gewicht: {self.charakter.gesamtgewicht} / {self.charakter.maximale_traglast} kg"
        Logger.debug(f"Gewicht aktualisiert: {self.gewicht_text}")

class EigenschaftenScreen(BoxLayout):
    pass

class HandicapsScreen(BoxLayout):
    pass

class TalenteScreen(BoxLayout):
    pass

class MaechteScreen(BoxLayout):
    pass

class AusruestungScreen(BoxLayout):
    pass

class EigenschaftenWidget(BoxLayout):
    eigenschaften_layout = ObjectProperty(None)

    @Fehlerbehandlung.handle_errors
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info("Initializing CharakterErstellungsWidget.")
        # Initialisieren des Controllers mit einem Standardnamen
        self.controller = CharakterController(name="Charakter")
        Logger.debug("CharacterController instantiated with name 'Charakter'.")
        # Weisen Sie den Controller dem App-Objekt zu, um globalen Zugriff zu ermöglichen
        App.get_running_app().controller = self.controller
        Logger.debug("CharacterController assigned to App.")
        Clock.schedule_once(self.init_eigenschaften_tab, 0)

    @Fehlerbehandlung.handle_errors
    def init_eigenschaften_tab(self, dt):
        Logger.info("Initializing attributes tab.")
        if self.eigenschaften_layout is not None:
            Logger.debug("eigenschaften_layout is defined. Creating attributes tab.")
            self.create_eigenschaften_tab()
        else:
            Logger.error("eigenschaften_layout is not defined.")

    @Fehlerbehandlung.handle_errors
    def create_eigenschaften_tab(self):
        Logger.info("Creating attributes tab.")
        # Zugriff auf die Unterlayouts über die ids
        attribute_layout = self.ids.attribute_layout
        fertigkeiten_layout = self.ids.fertigkeiten_layout

        # Leeren der Unterlayouts
        attribute_layout.clear_widgets()
        fertigkeiten_layout.clear_widgets()
        Logger.debug("Cleared attribute and fertigkeiten layouts.")

        # Befüllen des Attribute-Layouts
        for item_name, item_obj in self.controller.charakter.attribute.items():
            Logger.debug(f"Creating row for attribute: {item_name}")
            item_row = EigenschaftenItemRow(
                item_name=item_name,
                item_obj=item_obj,
                item_type='attribute',
                controller=self.controller
            )
            attribute_layout.add_widget(item_row)
            Logger.debug(f"Added attribute row for {item_name}.")

        # Befüllen des Fertigkeiten-Layouts
        for item_name, item_obj in self.controller.charakter.fertigkeiten.items():
            Logger.debug(f"Creating row for fertigkeit: {item_name}")
            item_row = EigenschaftenItemRow(
                item_name=item_name,
                item_obj=item_obj,
                item_type='fertigkeiten',
                controller=self.controller
            )
            fertigkeiten_layout.add_widget(item_row)
            Logger.debug(f"Added fertigkeit row for {item_name}.")
        
        Logger.info("Attributes tab successfully created.")

class EigenschaftenItemRow(BoxLayout):
    item_name = StringProperty()
    item_obj = ObjectProperty()
    item_type = StringProperty()
    controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def steigere_eigenschaft(self):
        Logger.info(f"Increasing attribute: {self.item_name} ({self.item_type})")
        if self.item_type == 'attribute':
            success = self.controller.steigere_attribut(self.item_name)
            Logger.debug(f"Increased attribute {self.item_name}: {'Success' if success else 'Failure'}")
        else:
            success = self.controller.steigere_fertigkeit(self.item_name)
            Logger.debug(f"Increased skill {self.item_name}: {'Success' if success else 'Failure'}")

        if success:
            Logger.info(f"Attribute {self.item_name} successfully increased.")
        else:
            Logger.warning(f"Failed to increase attribute {self.item_name}.")

    def senke_eigenschaft(self):
        Logger.info(f"Decreasing attribute: {self.item_name} ({self.item_type})")
        if self.item_type == 'attribute':
            success = self.controller.senke_attribut(self.item_name)
            Logger.debug(f"Decreased attribute {self.item_name}: {'Success' if success else 'Failure'}")
        else:
            success = self.controller.senke_fertigkeit(self.item_name)
            Logger.debug(f"Decreased skill {self.item_name}: {'Success' if success else 'Failure'}")

        if success:
            Logger.info(f"Attribute {self.item_name} successfully decreased.")
        else:
            Logger.warning(f"Failed to decrease attribute {self.item_name}.")


class HandicapsWidget(BoxLayout):
    handicaps_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info("Initializing HandicapsWidget.")
        self.orientation = 'vertical'
        
        # Initialize sort_order
        self.sort_order = 'name_asc'

        # Zugriff auf den Controller
        self.controller = App.get_running_app().controller
        self.stufe = list(set(handicap.stufe for handicap in self.controller.charakter.handicaps.values()))

        # Initialisieren der Handicaps nach dem Aufbau des Widget-Baums
        Clock.schedule_once(self.post_init, 0)

    def post_init(self, dt):
        try:
            from data.handicap_daten import handicap_liste
        except ImportError as e:
            Logger.error(f"Failed to import handicap_liste: {e}")
            handicap_liste = []

        Logger.debug(f"Typ von handicap_liste: {type(handicap_liste)}")
        if isinstance(handicap_liste, (list, dict)) and len(handicap_liste) > 0:
            Logger.debug(f"Typ von handicap_liste[0]: {type(handicap_liste[0])}")
        else:
            Logger.warning("handicap_liste is empty or not a list/dict.")

        if hasattr(self.controller, 'initialisiere_handicaps'):
            self.controller.initialisiere_handicaps(handicap_liste)
        else:
            Logger.error("Controller does not have 'initialisiere_handicaps' method.")
        self.filter_handicaps()
        self.create_handicaps_tab()

    def create_handicaps_tab(self):
        Logger.info("Creating Handicaps tab.")
        # Zugriff auf das Handicaps-Layout und das Items-Layout
        handicaps_layout = self.ids.handicaps_layout
        handicaps_items_layout = self.ids.handicaps_items_layout

        self.create_handicaps_subtab()

    def sortiere_handicaps(self):
        # Umschalten der Sortierreihenfolge
        if hasattr(self, 'sort_order') and self.sort_order == 'name_asc':
            self.sort_order = 'name_desc'
        else:
            self.sort_order = 'name_asc'
        self.create_handicaps_subtab()

    def filter_handicaps(self):
        search_term = self.ids.search_input.text.lower()
        selected_category = self.ids.category_spinner.text.lower()  # Konvertierung in Kleinbuchstaben
        handicaps_items_layout = self.ids.handicaps_items_layout
        handicaps_items_layout.clear_widgets()

        alle_handicaps = self.controller.charakter.handicaps

        # Filtern der Handicaps nach Suchbegriff und Kategorie
        filtered_handicaps = []
        for handicap in alle_handicaps.values():
            # Vergleich in Kleinbuchstaben, um Groß-/Kleinschreibung zu ignorieren
            if selected_category != 'alle kategorien' and handicap.stufe != selected_category:
                Logger.debug(f"Handicap '{handicap.name}' ausgeschlossen aufgrund der Stufe '{handicap.stufe}'")
                continue
            if search_term in handicap.name.lower() or search_term in handicap.beschreibung.lower():
                filtered_handicaps.append(handicap)
                Logger.debug(f"Handicap '{handicap.name}' passt zum Suchbegriff '{search_term}'")

        Logger.debug(f"Anzahl gefilterte Handicaps: {len(filtered_handicaps)}")

        # Sortieren nach Name
        if self.sort_order == 'name_desc':
            filtered_handicaps.sort(key=lambda h: h.name, reverse=True)
            Logger.debug("Sortierreihenfolge: Absteigend")
        else:
            filtered_handicaps.sort(key=lambda h: h.name)
            Logger.debug("Sortierreihenfolge: Aufsteigend")

        # Hinzufügen der gefilterten Handicaps
        for handicap in filtered_handicaps:
            if hasattr(handicap, 'stufe'):
                stufe = handicap.stufe.capitalize()  # Für bessere Anzeige
                Logger.debug(f"Adding Handicap: {handicap.name}, Stufe: {stufe}")
            else:
                stufe = "Unbekannt"
                Logger.warning(f"Handicap '{handicap.name}' hat keine 'Stufe'.")
            item_row = HandicapItemRow(
                name_key=handicap.name,  # Beibehaltung der Originalschreibung für die UI
                handicap=handicap,
                controller=self.controller,
                handicaps_widget=self
            )
            handicaps_items_layout.add_widget(item_row)
            Logger.debug(f"Added row for {handicap.name} to handicaps items layout.")
        Logger.info("Handicaps erfolgreich gefiltert und geladen.")


    def create_handicaps_subtab(self):
        Logger.info("Creating handicaps subtab.")
        handicaps_items_layout = self.ids.handicaps_items_layout
        handicaps_items_layout.clear_widgets()
        alle_handicaps = self.controller.charakter.handicaps

        if not alle_handicaps:
            no_data_label = Label(text="Keine Handicaps verfügbar.", size_hint_y=None, height=40)
            handicaps_items_layout.add_widget(no_data_label)
            Logger.info("No handicaps to display.")
            return

        # Sortieren der Handicaps
        sortierte_handicaps = sorted(
            alle_handicaps.items(),
            key=lambda item: item[0],
            reverse=(self.sort_order == 'name_desc')
        )

        for name_key, handicap in sortierte_handicaps:
            item_row = HandicapItemRow(
                name_key=name_key,
                handicap=handicap,
                controller=self.controller,
                handicaps_widget=self
            )
            handicaps_items_layout.add_widget(item_row)
            Logger.debug(f"Added row for {name_key} to handicaps items layout.")

        Logger.info("Handicaps subtab successfully created.")


    def update_handicaps_tab(self):
        Logger.info("Updating handicaps tab.")
        self.create_handicaps_subtab()
        Logger.debug("Handicaps tab updated.")

class HandicapItemRow(BoxLayout):
    name_key = StringProperty()
    handicap = ObjectProperty()
    controller = ObjectProperty()
    beschreibung = StringProperty()
    handicaps_widget = ObjectProperty()

    def __init__(self, name_key, handicap, controller, handicaps_widget, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 10
        self.size_hint_y = None
        self.height = 40  # Adjust this value as needed

        # Main content (name, stufe, beschreibung)
        content_layout = BoxLayout(orientation='horizontal', size_hint_x=0.9)
        content_layout.add_widget(Label(text=handicap.name, size_hint_x=0.3, halign='left', valign='middle', text_size=(None, None)))
        
        stufe_text = handicap.stufe.capitalize() if hasattr(handicap, 'stufe') else "Unbekannt"
        content_layout.add_widget(Label(text=stufe_text, size_hint_x=0.2, halign='left', valign='middle', text_size=(None, None)))
        
        content_layout.add_widget(Label(text=handicap.beschreibung, size_hint_x=0.5, halign='left', valign='middle', text_size=(None, None)))

        self.add_widget(content_layout)

        # Buttons layout
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_x=0.1, spacing=5)
        add_button = Button(text="+", size_hint=(None, None), size=(30, 30))
        add_button.bind(on_release=lambda instance: controller.waehle_handicap(name_key))
        buttons_layout.add_widget(add_button)

        remove_button = Button(text="-", size_hint=(None, None), size=(30, 30))
        remove_button.bind(on_release=lambda instance: controller.entferne_handicap(name_key))
        buttons_layout.add_widget(remove_button)

        self.add_widget(buttons_layout)       

class TalentItemRow(BoxLayout):
    talent_name = StringProperty("")
    beschreibung = StringProperty("")
    talent = ObjectProperty(None)

    def __init__(self, talent_name, beschreibung, talent, **kwargs):
        super().__init__(**kwargs)
        self.talent_name = talent_name
        self.beschreibung = beschreibung
        self.talent = talent
        self.controller = App.get_running_app().controller

        if self.talent is None:
            Logger.error(f"TalentItemRow für '{self.talent_name}' wurde mit 'None' Talent erstellt.")
        else:
            Logger.debug(f"TalentItemRow für '{self.talent_name}' erfolgreich erstellt.")

    def waehle_talent(self):
        self.controller.waehle_talent(self.talent_name)

    def entferne_talent(self):
        self.controller.entferne_talent(self.talent_name)

class TalenteWidget(BoxLayout):
    talente_items_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info("Initializing TalenteWidget.")
        self.orientation = 'vertical'
        
        # Initialize sort_order
        self.sort_order = 'name_asc'

        # Zugriff auf den Controller
        self.controller = App.get_running_app().controller
        self.kategorien = list(set(talent.kategorie for talent in self.controller.charakter.talente.values()))
        self.kategorien.sort()

        # Initialisieren der Talente nach dem Aufbau des Widget-Baums
        Clock.schedule_once(self.post_init, 0)

    def post_init(self, dt):
        try:
            from data.talent_daten import talent_daten  # Annahme: talent_daten ist ein Dictionary
        except ImportError as e:
            Logger.error(f"Failed to import talent_daten: {e}")
            talent_daten = {}

        Logger.debug(f"Typ von talent_daten: {type(talent_daten)}")
        if isinstance(talent_daten, dict) and talent_daten:
            Logger.debug("talent_daten erfolgreich importiert.")
        else:
            Logger.warning("talent_daten ist leer oder kein Dictionary.")

        if hasattr(self.controller, 'initialisiere_talente'):
            self.controller.initialisiere_talente(talent_daten)
        else:
            Logger.error("Controller hat keine Methode 'initialisiere_talente'.")
        self.filter_talente()
        self.create_talente_tab()

    def create_talente_tab(self):
        Logger.info("Creating Talente tab.")
        # Zugriff auf das Talente-Layout und das Items-Layout
        talente_layout = self.ids.talente_layout
        talente_items_layout = self.ids.talente_items_layout

        self.create_talente_subtab()

    def sortiere_talente(self):
        # Umschalten der Sortierreihenfolge
        if self.sort_order == 'name_asc':
            self.sort_order = 'name_desc'
        else:
            self.sort_order = 'name_asc'
        Logger.debug(f"Sortierreihenfolge geändert zu: {self.sort_order}")
        self.create_talente_subtab()

    def filter_talente(self):
        search_term = self.ids.search_input.text.lower()
        selected_kategorie = self.ids.category_spinner.text.lower()
        talente_items_layout = self.ids.talente_items_layout
        talente_items_layout.clear_widgets()

        alle_talente = self.controller.charakter.talente

        # Filtern der Talente nach Suchbegriff und Kategorie
        filtered_talente = []
        for talent in alle_talente.values():
            if selected_kategorie != 'alle kategorien' and (talent.kategorie is None or talent.kategorie.lower() != selected_kategorie):
                Logger.debug(f"Talent '{talent.name}' ausgeschlossen aufgrund der Kategorie '{talent.kategorie}'")
                continue
            if (search_term in talent.name.lower()) or (search_term in talent.beschreibung.lower()):
                filtered_talente.append(talent)
                Logger.debug(f"Talent '{talent.name}' passt zum Suchbegriff '{search_term}'")

        Logger.debug(f"Anzahl gefilterte Talente: {len(filtered_talente)}")

        # Sortieren nach Name
        if self.sort_order == 'name_desc':
            filtered_talente.sort(key=lambda t: t.name, reverse=True)
            Logger.debug("Sortierreihenfolge: Absteigend")
        else:
            filtered_talente.sort(key=lambda t: t.name)
            Logger.debug("Sortierreihenfolge: Aufsteigend")

        # Hinzufügen der gefilterten Talente
        for talent in filtered_talente:
            category_display = talent.kategorie.capitalize() if talent.kategorie else "Unbekannt"
            Logger.debug(f"Adding Talent: {talent.name}, Kategorie: {category_display}")
            talent_item = TalentItemRow(
                talent_name=talent.name,
                beschreibung=talent.beschreibung,
                talent=talent
            )
            talente_items_layout.add_widget(talent_item)
        Logger.info("Talente erfolgreich gefiltert und geladen.")

    def create_talente_subtab(self):
        Logger.info("Creating Talente subtab.")
        talente_items_layout = self.ids.talente_items_layout
        talente_items_layout.clear_widgets()
        alle_talente = self.controller.charakter.talente

        if not alle_talente:
            no_data_label = Label(text="Keine Talente verfügbar.", size_hint_y=None, height=40)
            talente_items_layout.add_widget(no_data_label)
            Logger.info("No talents to display.")
            return

        # Sortieren der Talente
        sortierte_talente = sorted(
            alle_talente.values(),
            key=lambda talent: talent.name,
            reverse=(self.sort_order == 'name_desc')
        )

        for talent in sortierte_talente:
            talent_item = TalentItemRow(
                talent_name=talent.name,
                beschreibung=talent.beschreibung,
                talent=talent
            )
            talente_items_layout.add_widget(talent_item)
            Logger.debug(f"Added row for {talent.name} to talente items layout.")

        Logger.info("Talente subtab erfolgreich erstellt.")

    def update_talente_tab(self):
        Logger.info("Updating Talente tab.")
        self.create_talente_subtab()
        Logger.debug("Talente tab updated.")

class MachtItemRow(BoxLayout):
    macht_name = StringProperty("")
    rang = StringProperty("")
    machtpunkte = NumericProperty(0)
    reichweite = StringProperty("")
    dauer = StringProperty("")
    effekt = StringProperty("")
    anmerkungen = StringProperty("")
    macht = ObjectProperty(None)
    maechte_widget = ObjectProperty(None)  # Referenz auf das übergeordnete MaechteWidget

    def __init__(self, macht_name, rang, machtpunkte, reichweite, dauer, effekt, anmerkungen, macht, maechte_widget, **kwargs):
        super().__init__(**kwargs)
        self.macht_name = macht_name
        self.rang = rang
        self.machtpunkte = machtpunkte
        self.reichweite = reichweite
        self.dauer = dauer
        self.effekt = effekt
        self.anmerkungen = anmerkungen
        self.macht = macht
        self.maechte_widget = maechte_widget

        if self.macht is None:
            Logger.error(f"MachtItemRow für '{self.macht_name}' wurde mit 'None' Macht erstellt.")
        else:
            Logger.debug(f"MachtItemRow für '{self.macht_name}' erfolgreich erstellt.")

    def waehle_macht(self):
        Logger.info(f"Auswählen der Macht: {self.macht_name}")
        success = self.maechte_widget.controller.waehle_macht(self.macht_name)
        if success:
            Logger.debug(f"Macht '{self.macht_name}' ausgewählt.")
        else:
            Logger.warning(f"Auswahl der Macht '{self.macht_name}' fehlgeschlagen.")
        if self.maechte_widget:
            self.maechte_widget.filter_maechte()
        else:
            Logger.error("Keine Referenz zu MaechteWidget vorhanden.")

    def entferne_macht(self):
        Logger.info(f"Entfernen der Macht: {self.macht_name}")
        success = self.maechte_widget.controller.entferne_macht(self.macht_name)
        if success:
            Logger.debug(f"Macht '{self.macht_name}' entfernt.")
        else:
            Logger.warning(f"Entfernen der Macht '{self.macht_name}' fehlgeschlagen.")
        if self.maechte_widget:
            self.maechte_widget.filter_maechte()
        else:
            Logger.error("Keine Referenz zu MaechteWidget vorhanden.")

class MaechteWidget(BoxLayout):
    maechte_items_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info("Initializing MaechteWidget.")
        self.orientation = 'vertical'
        
        # Initialize sort_order
        self.sort_order = {'name': 'asc', 'rang': 'asc'}

        # Zugriff auf den Controller
        self.controller = App.get_running_app().controller
        self.ränge = sorted(list(set(macht.rang for macht in self.controller.charakter.maechte.values())))

        # Initialisieren der Mächte nach dem Aufbau des Widget-Baums
        Clock.schedule_once(self.post_init, 0)

    def post_init(self, dt):
        try:
            from data.maechte_daten import maechte_daten  # Korrekte Datenreferenz
        except ImportError as e:
            Logger.error(f"Failed to import maechte_daten: {e}")
            maechte_daten = {}

        Logger.debug(f"Typ von maechte_daten: {type(maechte_daten)}")
        if isinstance(maechte_daten, dict) and maechte_daten:
            Logger.debug("maechte_daten erfolgreich importiert.")
        else:
            Logger.warning("maechte_daten ist leer oder kein Dictionary.")

        if hasattr(self.controller, 'initialisiere_maechte'):
            self.controller.initialisiere_maechte(maechte_daten)
        else:
            Logger.error("Controller hat keine Methode 'initialisiere_maechte'.")
        self.filter_maechte()
        self.create_maechte_tab()

    def create_maechte_tab(self):
        Logger.info("Creating Maechte tab.")
        self.create_maechte_subtab()

    def sortiere_maechte_nach_name(self):
        # Umschalten der Sortierreihenfolge für Namen
        if self.sort_order['name'] == 'asc':
            self.sort_order['name'] = 'desc'
        else:
            self.sort_order['name'] = 'asc'
        Logger.debug(f"Sortierreihenfolge für Name geändert zu: {self.sort_order['name']}")
        self.filter_maechte()

    def sortiere_maechte_nach_rang(self):
        # Umschalten der Sortierreihenfolge für Rang
        if self.sort_order['rang'] == 'asc':
            self.sort_order['rang'] = 'desc'
        else:
            self.sort_order['rang'] = 'asc'
        Logger.debug(f"Sortierreihenfolge für Rang geändert zu: {self.sort_order['rang']}")
        self.filter_maechte()

    def filter_maechte(self):
        search_term = self.ids.maechte_search_input.text.lower()
        # Da wir keine Spinner mehr haben, sort_order wird bereits durch die Sortier-Buttons aktualisiert
        maechte_items_layout = self.maechte_items_layout
        maechte_items_layout.clear_widgets()

        alle_maechte = self.controller.charakter.maechte

        # Filtern der Mächte nach Suchbegriff
        filtered_maechte = []
        for macht in alle_maechte.values():
            if (search_term in macht.name.lower()) or (search_term in macht.effekt.lower()):
                filtered_maechte.append(macht)
                Logger.debug(f"Macht '{macht.name}' passt zum Suchbegriff '{search_term}'")

        Logger.debug(f"Anzahl gefilterte Mächte: {len(filtered_maechte)}")

        # Sortieren
        # Zuerst nach Rang, dann nach Name, basierend auf self.sort_order
        if self.sort_order['rang'] == 'desc':
            filtered_maechte.sort(key=lambda m: m.rang, reverse=True)
            Logger.debug("Sortieren nach Rang absteigend")
        else:
            filtered_maechte.sort(key=lambda m: m.rang)
            Logger.debug("Sortieren nach Rang aufsteigend")

        if self.sort_order['name'] == 'desc':
            filtered_maechte.sort(key=lambda m: m.name, reverse=True)
            Logger.debug("Sortieren nach Name absteigend")
        else:
            filtered_maechte.sort(key=lambda m: m.name)
            Logger.debug("Sortieren nach Name aufsteigend")

        # Hinzufügen der gefilterten und sortierten Mächte
        for macht in filtered_maechte:
            macht_item = MachtItemRow(
                macht_name=macht.name,
                rang=macht.rang,
                machtpunkte=macht.machtpunkte,
                reichweite=macht.reichweite,
                dauer=macht.dauer,
                effekt=macht.effekt,
                anmerkungen=macht.anmerkungen,
                macht=macht,
                maechte_widget=self  # Referenz übergeben
            )
            maechte_items_layout.add_widget(macht_item)
            Logger.debug(f"Added row for {macht.name} to maechte items layout.")
        Logger.info("Mächte erfolgreich gefiltert und geladen.")

    def create_maechte_subtab(self):
        Logger.info("Creating Mächte subtab.")
        self.filter_maechte()

    def update_maechte_tab(self):
        Logger.info("Updating Mächte tab.")
        self.filter_maechte()
        Logger.debug("Mächte tab updated.")

class AusruestungItemRow(BoxLayout):
    name = StringProperty("")
    kategorie = StringProperty("")
    gewicht = NumericProperty(0)
    kosten = NumericProperty(0)
    menge = NumericProperty(0)
    ausruestung = ObjectProperty(None)
    ausruestung_widget = ObjectProperty(None)

    def __init__(self, name, kategorie, gewicht, kosten, menge, ausruestung, ausruestung_widget, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.kategorie = kategorie
        self.gewicht = gewicht
        self.kosten = kosten
        self.menge = menge
        self.ausruestung = ausruestung
        self.ausruestung_widget = ausruestung_widget
        Logger.debug(f"AusruestungItemRow erstellt: {self.name}, Kategorie: {self.kategorie}, Gewicht: {self.gewicht}, Kosten: {self.kosten}, Menge: {self.menge}")
    
        # Bindings für automatische Aktualisierung der Anzeige
        self.ausruestung.bind(menge=self.on_menge_change)

    def on_menge_change(self, instance, value):
        self.menge = value
        self.ausruestung_widget.controller.charakter.berechne_gesamtgewicht()
        self.ausruestung_widget.filter_ausruestung()

    def kaufen_ausruestung(self):
        Logger.info(f"Kaufen der Ausrüstung: {self.name}")
        success = self.ausruestung_widget.controller.kaufen_ausruestung(self.name, anzahl=1)
        if success:
            Logger.debug(f"Ausrüstung '{self.name}' gekauft.")
        else:
            Logger.warning(f"Ausrüstung '{self.name}' konnte nicht gekauft werden.")

    def verkaufen_ausruestung(self):
        Logger.info(f"Verkaufen der Ausrüstung: {self.name}")
        success = self.ausruestung_widget.controller.verkaufen_ausruestung(self.name, anzahl=1)
        if success:
            Logger.debug(f"Ausrüstung '{self.name}' verkauft.")
        else:
            Logger.warning(f"Ausrüstung '{self.name}' konnte nicht verkauft werden.")

class AusruestungWidget(BoxLayout):
    ausruestung_items_layout = ObjectProperty(None)
    search_input = ObjectProperty(None)
    category_spinner = ObjectProperty(None)  # Spinner-Property hinzufügen

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info("Initializing AusruestungWidget.")
        self.orientation = 'vertical'
        
        # Initialize sort_order and current_sort_field
        self.sort_order = {
            'name': 'asc',
            'gewicht': 'asc',
            'kosten': 'asc',
            'menge': 'asc'
        }
        self.current_sort_field = 'name'  # Default sort by name

        # Zugriff auf den Controller
        self.controller = App.get_running_app().controller
        self.ausruestung_liste = sorted(list(self.controller.charakter.ausruestung_daten.values()), key=lambda x: x.name)
        #Logger.debug(f"Anzahl der Ausrüstungsgegenstände im Controller: {len(self.ausruestung_liste)}")

        # Initialisieren der Ausrüstung nach dem Aufbau des Widget-Baums
        Clock.schedule_once(self.post_init, 0)

    def post_init(self, dt):
        #Logger.debug(f"Typ von ausruestung_liste: {type(self.ausruestung_liste)}")
        if isinstance(self.ausruestung_liste, list) and self.ausruestung_liste:
            Logger.debug("Ausrüstungsliste erfolgreich initialisiert.")
            if len(self.ausruestung_liste) > 0:
                erster_ausruestung = self.ausruestung_liste[0]
                #logger.debug(f"Erster Ausrüstungsgegenstand: {erster_ausruestung.name}, Kategorie: {erster_ausruestung.kategorie}")
        else:
            Logger.warning("Ausrüstungsliste ist leer oder kein Listentyp.")

        # Aufrufen der Methode zur Überprüfung der Kategorien
        #self.print_ausruestung_kategorien()

        self.create_ausruestung_tab()

    def create_ausruestung_tab(self):
        Logger.info("Creating Ausruestung tab.")
        # Header hinzufügen
        header = BoxLayout(size_hint_y=None, height=30)
        header.add_widget(Label(text="Name", size_hint_x=0.3))
        header.add_widget(Label(text="Kategorie", size_hint_x=0.2))
        header.add_widget(Label(text="Gewicht", size_hint_x=0.15))
        header.add_widget(Label(text="Kosten", size_hint_x=0.15))
        header.add_widget(Label(text="Menge", size_hint_x=0.15))
        self.ausruestung_items_layout.add_widget(header)
        Logger.debug("Header für Ausrüstungsübersicht hinzugefügt.")
        self.filter_ausruestung()

    def sortiere_ausruestung_nach_field(self, field):
        # Umschalten der Sortierreihenfolge für das ausgewählte Feld
        if self.sort_order[field] == 'asc':
            self.sort_order[field] = 'desc'
        else:
            self.sort_order[field] = 'asc'
        #Logger.debug(f"Sortierreihenfolge für {field} geändert zu: {self.sort_order[field]}")

        # Setze das aktuelle Sortierfeld
        self.current_sort_field = field

        # Setze die Sortierreihenfolge für andere Felder zurück auf 'asc'
        for f in self.sort_order:
            if f != field:
                self.sort_order[f] = 'asc'

        # Filter und sortiere die Ausrüstungsliste
        self.filter_ausruestung()

    def sortiere_ausruestung_nach_name(self):
        self.sortiere_ausruestung_nach_field('name')

    def sortiere_ausruestung_nach_gewicht(self):
        self.sortiere_ausruestung_nach_field('gewicht')

    def sortiere_ausruestung_nach_kosten(self):
        self.sortiere_ausruestung_nach_field('kosten')

    def sortiere_ausruestung_nach_menge(self):
        self.sortiere_ausruestung_nach_field('menge')

    def filter_ausruestung(self):
        if not self.ausruestung_items_layout:
            Logger.error("ausruestung_items_layout ist None. Überprüfe die .kv-Datei und die Property-Zuordnung.")
            return

        search_term = self.search_input.text.lower() if self.search_input else ""
        selected_category = self.category_spinner.text if self.category_spinner else "Alle Kategorien"
        Logger.debug(f"Suchbegriff für Ausrüstung: '{search_term}'")
        Logger.debug(f"Ausgewählte Kategorie: '{selected_category}'")

        # Clear aktuelle Widgets
        self.ausruestung_items_layout.clear_widgets()
        Logger.debug("Ausrüstungsübersicht gelöscht.")

        # Hinzufügen des Headers wieder
        header = BoxLayout(size_hint_y=None, height=30)
        header.add_widget(Label(text="Name", size_hint_x=0.3))
        header.add_widget(Label(text="Kategorie", size_hint_x=0.2))
        header.add_widget(Label(text="Gewicht", size_hint_x=0.15))
        header.add_widget(Label(text="Kosten", size_hint_x=0.15))
        header.add_widget(Label(text="Menge", size_hint_x=0.15))
        self.ausruestung_items_layout.add_widget(header)
        Logger.debug("Header für Ausrüstungsübersicht wieder hinzugefügt.")

        # Filtern der Ausrüstung nach Suchbegriff und Kategorie
        gefilterte_ausruestung = []
        for ausr in self.controller.charakter.ausruestung_daten.values():
            passt_suche = search_term in ausr.name.lower() or search_term in ausr.beschreibung.lower()
            passt_kategorie = (selected_category == "Alle Kategorien") or (ausr.kategorie == selected_category)
            if passt_suche and passt_kategorie:
                gefilterte_ausruestung.append(ausr)
                #Logger.debug(f"Ausrüstung '{ausr.name}' passt zum Suchbegriff '{search_term}' und Kategorie '{selected_category}'")

        #Logger.debug(f"Anzahl gefilterte Ausrüstungen: {len(gefilterte_ausruestung)}")

        # Sortiere nach dem aktuellen Sortierfeld
        reverse = (self.sort_order[self.current_sort_field] == 'desc')
        gefilterte_ausruestung.sort(key=lambda x: getattr(x, self.current_sort_field), reverse=reverse)
        #Logger.debug(f"Sortiert nach {self.current_sort_field} {'absteigend' if reverse else 'aufsteigend'}")

        # Hinzufügen der gefilterten und sortierten Ausrüstungen
        for ausr in gefilterte_ausruestung:
            ausruestung_item = AusruestungItemRow(
                name=ausr.name,
                kategorie=ausr.kategorie,        # Hinzugefügtes Argument
                gewicht=ausr.gewicht,
                kosten=ausr.kosten,
                menge=ausr.menge,
                ausruestung=ausr,
                ausruestung_widget=self
            )
            self.ausruestung_items_layout.add_widget(ausruestung_item)
            #Logger.debug(f"Ausrüstung '{ausr.name}' (Kategorie: {ausr.kategorie}) zur Ausrüstungsübersicht hinzugefügt.")

        Logger.info("Ausrüstungen erfolgreich gefiltert und geladen.")

    # def print_ausruestung_kategorien(self):
    #     Logger.debug("Überprüfe alle Kategorien der Ausrüstungsgegenstände:")
    #     for ausr in self.ausruestung_liste:
    #         Logger.debug(f"Ausrüstung '{ausr.name}' hat die Kategorie '{ausr.kategorie}'")


# Definition des CharakterbogenWidgets
class CharakterbogenWidget(BoxLayout):
    attribut_grid = ObjectProperty(None)
    fertigkeit_grid = ObjectProperty(None)
    handicaps_section = ObjectProperty(None)
    talente_section = ObjectProperty(None)
    maechte_section = ObjectProperty(None)
    ausruestung_section = ObjectProperty(None)
    waffen_section = ObjectProperty(None)
    ruestung_section = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Zugriff auf den Controller
        self.controller = App.get_running_app().controller
        self.controller.charakter.bind(selected_ausruestung=self.on_ausruestung_changed)
        Logger.info("CharakterbogenWidget initialisiert.")
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        # Bindings erstellen
        self.bind_overview()
        # Initiale Übersicht erstellen
        Clock.schedule_once(self.update_overview, 0)


    def on_ausruestung_changed(self, instance, value):
        Logger.debug("Ausrüstung hat sich geändert, aktualisiere Übersicht.")
        self.update_overview(0)

    def bind_overview(self):
        charakter = self.controller.charakter
        charakter.bind(attribute=lambda instance, value: self.update_overview(0))
        charakter.bind(fertigkeiten=lambda instance, value: self.update_overview(0))
        charakter.bind(selected_handicaps=lambda instance, value: self.update_overview(0))
        charakter.bind(selected_talente=lambda instance, value: self.update_overview(0))
        charakter.bind(selected_maechte=lambda instance, value: self.update_overview(0))
        charakter.bind(selected_ausruestung=lambda instance, value: self.update_overview(0))
        charakter.bind(selected_waffen=lambda instance, value: self.update_overview(0))
        charakter.bind(selected_ruestungen=lambda instance, value: self.update_overview(0))


    def create_mod_text(self, modifier):
        """
        Erstellt den Text für den Modifier.
        """
        if modifier > 0:
            return f"({modifier:+})"
        elif modifier < 0:
            return f"({modifier:+})"
        else:
            return ""

    def update_overview(self, dt):
        Logger.debug("Aktualisiere die Charakterübersicht.")
        charakter = self.controller.charakter

        # Zugriff auf die GridLayouts via IDs
        attribut_grid = self.ids.attribut_grid
        fertigkeit_grid = self.ids.fertigkeit_grid

        # Leeren der bestehenden Einträge (nur die dynamischen)
        attribut_grid.clear_widgets()
        fertigkeit_grid.clear_widgets()

        # Hinzufügen der Überschrift erneut
        attribut_grid.add_widget(LeftAlignedLabel(
            text="Attribute",
            bold=True,
            font_size='18sp',
            size_hint_y=None,
            height=30
        ))

        fertigkeit_grid.add_widget(LeftAlignedLabel(
            text="Fertigkeiten",
            bold=True,
            font_size='18sp',
            size_hint_y=None,
            height=30
        ))

        # Hinzufügen der Attribute
        for attribut in charakter.attribute.values():
            if attribut.modifier == -2:
                Logger.debug(f"Attribut '{attribut.name}' mit Modifier -2 wird ausgeblendet.")
                continue  # Item komplett ausblenden

            # Bereite den Wert und den Modifikator vor
            wert_text = f"W{attribut.wert}"
            mod_text = self.create_mod_text(attribut.modifier)

            if attribut.modifier == 0:
                combined_text = f"{attribut.name}: {wert_text}"
            else:
                combined_text = f"{attribut.name}: {wert_text} {mod_text}"

            # Hinzufügen des kombinierten Labels
            attribut_grid.add_widget(LeftAlignedLabel(
                text=combined_text,
                font_size='16sp',
                size_hint_y=None,
                height=25
            ))

        # Hinzufügen der Fertigkeiten
        for fertigkeit in charakter.fertigkeiten.values():
            if fertigkeit.modifier == -2:
                Logger.debug(f"Fertigkeit '{fertigkeit.name}' mit Modifier -2 wird ausgeblendet.")
                continue  # Item komplett ausblenden

            # Nur bestimmte Werte anzeigen, wenn Modifikator 0
            if fertigkeit.modifier == 0 and fertigkeit.wert not in [4, 6, 8, 10, 12]:
                Logger.debug(f"Fertigkeit '{fertigkeit.name}' wird ausgeblendet, da Wert {fertigkeit.wert} nicht in [4, 6, 8, 10, 12] ist und Modifier 0.")
                continue

            wert_text = f"W{fertigkeit.wert}"
            mod_text = self.create_mod_text(fertigkeit.modifier)

            if fertigkeit.modifier == 0:
                combined_text = f"{fertigkeit.name}: {wert_text}"
            else:
                combined_text = f"{fertigkeit.name}: {wert_text} {mod_text}"

            # Hinzufügen des kombinierten Labels
            fertigkeit_grid.add_widget(LeftAlignedLabel(
                text=combined_text,
                font_size='16sp',
                size_hint_y=None,
                height=25
            ))

        # Handicaps Abschnitt
        handicaps_section = self.ids.handicaps_section
        handicaps_section.clear_widgets()
        handicaps = charakter.selected_handicaps
        Logger.debug(f"Gefundene Handicaps: {len(handicaps)}")
        for handicap in handicaps:
            Logger.debug(f"Füge Handicap hinzu: {handicap.name}")
            handicaps_section.add_widget(LeftAlignedLabel(
                text=f"{handicap.name} (Stufe {handicap.stufe}): {handicap.beschreibung}",
                font_size='16sp',
                size_hint_y=None,
                height=25
            ))

        # Talente Abschnitt
        talente_section = self.ids.talente_section
        talente_section.clear_widgets()
        talente = charakter.selected_talente
        Logger.debug(f"Gefundene Talente: {len(talente)}")
        for talent in talente:
            Logger.debug(f"Füge Talent hinzu: {talent.name}")
            talente_section.add_widget(LeftAlignedLabel(
                text=f"{talent.name}: {talent.beschreibung}",
                font_size='16sp',
                size_hint_y=None,
                height=25
            ))

        # Mächte Abschnitt
        maechte_section = self.ids.maechte_section
        maechte_section.clear_widgets()
        maechte = charakter.selected_maechte
        Logger.debug(f"Gefundene Mächte: {len(maechte)}")
        for macht in maechte:
            maechte_section.add_widget(LeftAlignedLabel(
                text=f"{macht.name}, Rang: {macht.rang}, Machtpunkte: {macht.machtpunkte}, "
                    f"Reichweite: {macht.reichweite}, Dauer: {macht.dauer}, Effekt: {macht.effekt}",
                font_size='16sp',
                size_hint_y=None,
                height=25
            ))

        # Ausrüstung Abschnitt
        ausruestung_section = self.ids.ausruestung_section
        ausruestung_section.clear_widgets()
        ausruestung = self.controller.charakter.selected_ausruestung
        for item in ausruestung:
            button_text = ""
            if isinstance(item, (Waffe, Ruestung)):
                button_text = "Anlegen" if not item.angelegt else "Ablegen"
            else:
                button_text = ""
            item_text = f"{item.name} x{item.menge}"

            # Erstelle ein Layout für das Ausrüstungsitem
            item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)

            # Label für das Ausrüstungsitem
            item_label = LeftAlignedLabel(
                text=item_text,
                font_size='16sp',
                size_hint_x=0.8
            )

            # Button zum Anlegen/Ablegen, falls erforderlich
            if button_text:
                toggle_button = Button(
                    text=button_text,
                    size_hint_x=0.2
                )
                # Verwende functools.partial, um die Methode zu binden
                from functools import partial
                toggle_button.bind(on_press=partial(self.toggle_item, item))
                item_layout.add_widget(item_label)
                item_layout.add_widget(toggle_button)
            else:
                # Falls kein Button benötigt wird
                item_layout.add_widget(item_label)

            ausruestung_section.add_widget(item_layout)

        # Waffen Abschnitt (Angepasst)
        waffen_section = self.ids.waffen_section
        waffen_section.clear_widgets()

        waffen = [w for w in self.controller.charakter.selected_waffen if w.angelegt]
        for waffe in waffen:
            waffe_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)

            eigenschaften = waffe.eigenschaften
            eigenschaften_text = f"Schaden: {eigenschaften.get('Schaden', '-')}, Reichweite: {eigenschaften.get('Reichweite', '-')}, FR: {eigenschaften.get('FR', '-')}, Schuss: {eigenschaften.get('Schuss', '-')}, PB: {eigenschaften.get('PB', '-')}"

            weapon_label = LeftAlignedLabel(
                text=f"{waffe.name}, {eigenschaften_text}",
                font_size='16sp',
                size_hint_x=0.8
            )

            # Optional: Weitere Informationen oder Buttons hinzufügen
            waffe_layout.add_widget(weapon_label)
            waffen_section.add_widget(waffe_layout)

        # Rüstungen Abschnitt
        ruestungen_section = self.ids.ruestungen_section
        ruestungen_section.clear_widgets()
        ruestungen = [r for r in self.controller.charakter.selected_ruestungen if r.angelegt]
        for ruestung in ruestungen:
            ruestung_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)

            armor_label = LeftAlignedLabel(
                text=f"{ruestung.name}, Schutz: Torso={ruestung.torso}, Arme={ruestung.arme}, Beine={ruestung.beine}, Kopf={ruestung.kopf}",
                font_size='16sp',
                size_hint_x=0.8
            )

            # Optional: Weitere Informationen oder Buttons hinzufügen
            ruestung_layout.add_widget(armor_label)
            ruestungen_section.add_widget(ruestung_layout)


    def toggle_item(self, item, instance):
        item.toggle_angelegt()
        self.controller.charakter.berechne_abgeleitete_werte()
        self.update_overview(0)

    def toggle_waffe(self, waffe, instance):
        waffe.toggle_angelegt()
        self.controller.charakter.berechne_abgeleitete_werte()
        self.update_overview(0)

    def toggle_ruestung(self, ruestung, instance):
        ruestung.toggle_angelegt()
        self.controller.charakter.berechne_abgeleitete_werte()
        self.update_overview(0)

    def update_abgeleitete_werte(self):
        self.controller.charakter.berechne_abgeleitete_werte()
        self.update_overview(0)


        Logger.debug("Charakterübersicht aktualisiert.")

# Definition der App-Klasse
class CharakterErstellungApp(App):
    controller = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info("Initialisiere CharakterController.")
        self.controller = CharakterController(name="Charakter")  # Initialisieren des Controllers

    def build(self):
        Logger.info("Building the main application.")
        # Laden Sie die .kv-Datei manuell nach der Initialisierung des Controllers
        return RootWidget()

if __name__ == '__main__':
    Logger.info("Starting CharakterErstellungApp.")
    CharakterErstellungApp().run()

