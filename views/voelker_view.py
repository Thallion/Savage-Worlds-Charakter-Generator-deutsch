# views/voelker_view.py
"""
View-Komponente für Völker nach dem MVC-Pattern.
Stellt die Benutzerschnittstelle zur Anzeige und Verwaltung von Völkern bereit.
"""

from kivy.lang import Builder
from kivy.app import App
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDListItem
from kivymd.uix.button import MDIconButton
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.metrics import dp
import logging

# Logger konfigurieren
Logger = logging.getLogger(__name__)

# Konstanten für bessere Lesbarkeit und Wartbarkeit
DEFAULT_TALENT_TEXT = 'Wähle ein freies Talent'
DEFAULT_VOLK = 'Mensch'
NO_TALENT_AVAILABLE_TEXT = 'Keine freien Talente verfügbar'
CHECKBOX_WIDTH = 50
VOLK_LABEL_WIDTH = 300
TALENT_LABEL_WIDTH = dp(200)
ROW_HEIGHT = 40
INFO_ROW_HEIGHT = 25
PADDING_LEFT = 40

# KV-String - könnte später in eine separate Datei ausgelagert werden
KV_STRING = '''
<VoelkerWidget>:
    orientation: 'vertical'
    padding: 20
    spacing: 10
    md_bg_color: self.theme_cls.backgroundColor  

    ScrollView:
        size_hint: (1, 1)
        do_scroll_x: False
        do_scroll_y: True

        MDGridLayout:
            id: voelker_checkbox_container
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: 10
            padding: 10

            MDLabel:
                text: "Völker"
                size_hint_y: None
                height: 30
                halign: 'left'

            MDGridLayout:
                id: voelker_content_container
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
                padding: (0, 10, 0, 10)
'''

Builder.load_string(KV_STRING)


class VoelkerWidget(MDBoxLayout):
    """
    Widget zur Anzeige und Verwaltung von Völkern.
    Hauptkomponente der View im MVC-Pattern.
    """
    controller = ObjectProperty()
    aktuelles_talent = StringProperty(DEFAULT_TALENT_TEXT)

    def __init__(self, **kwargs):
        """Initialisiert das VoelkerWidget und setzt Grundkonfiguration."""
        super().__init__(**kwargs)
        self._initialize_controller()
        self.dropdown_menu = None
        Clock.schedule_once(self._setup_ui)

    def _initialize_controller(self):
        """Initialisiert die Verbindung zum Controller."""
        app = App.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None
        
        if not self.controller:
            Logger.error("VoelkerWidget: Controller nicht gefunden")
            return
            
        Logger.debug(f"VoelkerWidget initialisiert mit controller: {self.controller}")
        
        # Event-Bindung für Charakteränderungen
        if hasattr(self.controller, 'charakter'):
            self.controller.charakter.bind(on_charakter_change=self.aktualisiere_ui)

    def _setup_ui(self, dt):
        """Initialisierung der UI nach dem Laden des Widgets."""
        Logger.debug("VoelkerWidget: Setup UI gestartet")
        self.aktualisiere_ui()

    def _create_menu_items(self):
        """
        Erstellt die Menüeinträge für das Dropdown-Menü zur Talentauswahl.
        
        Returns:
            list: Liste mit Menüeinträgen
        """
        talente = self._get_freie_talente()
        return [
            {
                "text": talent,
                "height": dp(56),
                "on_release": lambda x=talent: self._on_talent_select(x),
            } for talent in talente
        ]

    def show_talent_menu(self, button):
        """
        Zeigt das Dropdown-Menü für Talente an.
        
        Args:
            button: Button, der das Menü aufruft
        """
        # Menü neu erstellen, um die aktuelle Liste der Talente zu haben
        self.dropdown_menu = MDDropdownMenu(
            caller=button,
            items=self._create_menu_items(),
            width_mult=4,
            max_height=dp(200),
        )
        self.dropdown_menu.open()

    def _on_talent_select(self, talent_name):
        """
        Wird aufgerufen, wenn ein Talent aus dem Dropdown ausgewählt wird.
        
        Args:
            talent_name: Name des ausgewählten Talents
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            self.dropdown_menu.dismiss()
            return
            
        if talent_name == NO_TALENT_AVAILABLE_TEXT:
            Logger.info("Keine freien Talente ausgewählt.")
            self.dropdown_menu.dismiss()
            return

        charakter = self.controller.charakter
        if hasattr(charakter, 'selected_talente') and talent_name in charakter.selected_talente:
            Logger.warning(f"Talent '{talent_name}' ist bereits ausgewählt.")
            self.dropdown_menu.dismiss()
            return

        self.aktuelles_talent = talent_name
        charakter.talent_auswaehlen(talent_name)
        charakter.dispatch('on_charakter_change')
        self.dropdown_menu.dismiss()

    def aktualisiere_ui(self, *args):
        """
        Aktualisiert die UI basierend auf dem aktuellen Zustand des Charakters.
        Wird bei Änderungen am Charakter aufgerufen.
        """
        Logger.debug("VoelkerWidget: aktualisiere_ui aufgerufen")
        
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return
            
        try:
            container = self.ids.voelker_content_container
            container.clear_widgets()

            # Völker anzeigen
            for volk_name, volk in self.controller.charakter.voelker.items():
                self._add_volk_row(container, volk_name, volk)
                self._add_volk_details(container, volk)

        except Exception as e:
            Logger.error(f"Fehler in aktualisiere_ui: {e}", exc_info=True)

    def _add_volk_row(self, container, volk_name, volk):
        """
        Fügt eine Zeile für ein Volk zum Container hinzu.
        
        Args:
            container: Container, zu dem die Zeile hinzugefügt wird
            volk_name: Name des Volks
            volk: Volk-Objekt
        """
        # Hauptzeile für das Volk erstellen
        row_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ROW_HEIGHT,
            spacing=10,
            adaptive_height=True
        )

        # Volk-Name Label
        label = MDLabel(
            text=volk_name,
            halign='left',
            size_hint_x=None,
            width=VOLK_LABEL_WIDTH,
            theme_text_color="Primary"
        )

        # Checkbox für die Auswahl
        is_active = volk.ausgewaehlt
        checkbox = MDCheckbox(
            active=is_active,
            size_hint_x=None,
            width=CHECKBOX_WIDTH,
            selected_color=self.theme_cls.primary_color
        )
        checkbox.voelker_name = volk_name
        checkbox.bind(active=lambda instance, value, volk_name=volk_name: 
                    self._on_checkbox_active(instance, value, volk_name))

        row_layout.add_widget(label)
        row_layout.add_widget(checkbox)

        # Spezielle UI-Elemente für Menschen
        if volk_name == DEFAULT_VOLK:
            self._add_mensch_specific_ui(row_layout)

        container.add_widget(row_layout)

    def _add_mensch_specific_ui(self, row_layout):
        """
        Fügt spezielle UI-Elemente für Menschen hinzu.
        
        Args:
            row_layout: Layout, zu dem die Elemente hinzugefügt werden
        """
        # Talent-Label
        talent_label = MDLabel(
            text=self.aktuelles_talent,
            size_hint_x=None,
            width=TALENT_LABEL_WIDTH
        )

        # Talent-Auswahlbutton
        talent_button = MDIconButton(
            icon="menu-down",
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            on_release=self.show_talent_menu
        )

        row_layout.add_widget(talent_label)
        row_layout.add_widget(talent_button)

    def _add_volk_details(self, container, volk):
        """
        Fügt Detailinformationen für ein Volk zum Container hinzu.
        
        Args:
            container: Container, zu dem die Details hinzugefügt werden
            volk: Volk-Objekt
        """
        # Hinzufügen von Zusatzinformationen (Handicaps, Talente, Besonderheiten)
        detail_categories = [
            ('Handicaps', volk.handicaps),
            ('Talente', volk.talente),
            ('Besonderheiten', volk.besonderheiten)
        ]
        
        for category, items in detail_categories:
            if items:
                self._add_detail_items(container, items)

    def _add_detail_items(self, container, items):
        """
        Fügt Detaileinträge zum Container hinzu.
        
        Args:
            container: Container, zu dem die Einträge hinzugefügt werden
            items: Liste der Einträge
        """
        for item in items:
            detail_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=INFO_ROW_HEIGHT,
                spacing=5,
                padding=(PADDING_LEFT, 0)
            )

            detail_label = MDLabel(
                text=item,
                halign='left',
                theme_text_color="Secondary",
                size_hint_x=None,
                width=1000
            )

            detail_row.add_widget(detail_label)
            container.add_widget(detail_row)

    def _get_freie_talente(self):
        """
        Gibt eine Liste von freien Talenten zurück.
        
        Returns:
            list: Liste der verfügbaren Talente
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return [NO_TALENT_AVAILABLE_TEXT]
            
        frei_talente = self.controller.charakter.get_freie_talente()
        if not frei_talente:
            frei_talente = [NO_TALENT_AVAILABLE_TEXT]
            
        return frei_talente

    def _on_checkbox_active(self, instance, value, selected_volk_name):
        """
        Ereignishandler für Checkbox-Änderungen.
        
        Args:
            instance: Checkbox-Instance, die das Ereignis ausgelöst hat
            value: Neuer Wert der Checkbox (True/False)
            selected_volk_name: Name des Volks, das mit der Checkbox verknüpft ist
        """
        if not self.controller or not hasattr(self.controller, 'charakter'):
            Logger.error("VoelkerWidget: Controller oder Charakter nicht verfügbar")
            return
            
        charakter = self.controller.charakter
        
        if value:
            # Aktivierung eines Volks
            self._deactivate_other_voelker(instance)
            self._activate_volk(selected_volk_name)
        else:
            # Deaktivierung eines Volks
            self._deactivate_volk(selected_volk_name)
            
            # Wenn kein Volk ausgewählt ist, setze Mensch als Standard
            if not any(charakter.voelker_selected.values()):
                self._set_default_volk()

        Logger.info(f"Volk '{selected_volk_name}' gesetzt auf {value}")
        charakter.dispatch('on_charakter_change')

    def _deactivate_other_voelker(self, active_checkbox):
        """
        Deaktiviert alle anderen Völker-Checkboxen.
        
        Args:
            active_checkbox: Die aktive Checkbox, die nicht deaktiviert werden soll
        """
        charakter = self.controller.charakter
        container = self.ids.voelker_content_container
        
        for child in container.children:
            if isinstance(child, MDBoxLayout):
                for widget in child.children:
                    if isinstance(widget, MDCheckbox) and widget != active_checkbox:
                        widget.active = False
                        volk_name = widget.voelker_name
                        charakter.voelker_selected[volk_name] = False
                        volk_obj = charakter.voelker.get(volk_name)
                        if volk_obj:
                            volk_obj.abwaehlen()

    def _activate_volk(self, volk_name):
        """
        Aktiviert ein Volk.
        
        Args:
            volk_name: Name des zu aktivierenden Volks
        """
        charakter = self.controller.charakter
        charakter.voelker_selected[volk_name] = True
        
        volk_obj = charakter.voelker.get(volk_name)
        if volk_obj:
            volk_obj.auswaehlen()

    def _deactivate_volk(self, volk_name):
        """
        Deaktiviert ein Volk.
        
        Args:
            volk_name: Name des zu deaktivierenden Volks
        """
        charakter = self.controller.charakter
        charakter.voelker_selected[volk_name] = False
        
        volk_obj = charakter.voelker.get(volk_name)
        if volk_obj:
            volk_obj.abwaehlen()

    def _set_default_volk(self):
        """Setzt das Standard-Volk (Mensch) als ausgewählt."""
        charakter = self.controller.charakter
        charakter.voelker_selected[DEFAULT_VOLK] = True
        
        if DEFAULT_VOLK in charakter.voelker:
            charakter.voelker[DEFAULT_VOLK].auswaehlen()
            
        self.aktualisiere_ui()