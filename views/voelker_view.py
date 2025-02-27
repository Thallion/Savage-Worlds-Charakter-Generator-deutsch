# views/voelker_view.py

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

Logger = logging.getLogger(__name__)

kv = '''
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

Builder.load_string(kv)

class VoelkerWidget(MDBoxLayout):
    controller = ObjectProperty()
    aktuelles_talent = StringProperty('Wähle ein freies Talent')
    dropdown_menu = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = App.get_running_app().controller
        Logger.debug("VoelkerWidget initialisiert mit controller: {}".format(self.controller))
        self.controller.charakter.bind(on_charakter_change=self.aktualisiere_ui)
        Clock.schedule_once(self.setup_checkboxes)

    def setup_checkboxes(self, dt):
        Logger.debug("setup_checkboxes aufgerufen")
        self.aktualisiere_ui()

    def create_menu_items(self):
        """Erstellt die Menüeinträge für das Dropdown"""
        talente = self.get_freie_talente()
        return [
            {
                "text": talent,
                "height": dp(56),
                "on_release": lambda x=talent: self.on_talent_select(x),
            } for talent in talente
        ]

    def show_talent_menu(self, button):
        """Zeigt das Dropdown-Menü für Talente an"""
        if not self.dropdown_menu:
            self.dropdown_menu = MDDropdownMenu(
                caller=button,
                items=self.create_menu_items(),
                width_mult=4,
                max_height=dp(200),
            )
        self.dropdown_menu.open()

    def on_talent_select(self, talent_name):
        """Wird aufgerufen, wenn ein Talent aus dem Dropdown ausgewählt wird"""
        if talent_name == 'Keine freien Talente verfügbar':
            Logger.info("Keine freien Talente ausgewählt.")
            self.dropdown_menu.dismiss()
            return

        if talent_name in self.controller.charakter.selected_talente:
            Logger.warning(f"Talent '{talent_name}' ist bereits ausgewählt.")
            self.dropdown_menu.dismiss()
            return

        self.aktuelles_talent = talent_name
        self.controller.charakter.talent_auswaehlen(talent_name)
        self.controller.charakter.dispatch('on_charakter_change')
        self.dropdown_menu.dismiss()

    def aktualisiere_ui(self, *args):
        Logger.debug("aktualisiere_ui aufgerufen")
        try:
            container = self.ids.voelker_content_container
            container.clear_widgets()

            for volk_name, volk in self.controller.charakter.voelker.items():
                h_layout = MDBoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=40,
                    spacing=10,
                    adaptive_height=True
                )

                label = MDLabel(
                    text=volk_name,
                    halign='left',
                    size_hint_x=None,
                    width=300,
                    theme_text_color="Primary"
                )

                is_active = volk.ausgewaehlt
                checkbox = MDCheckbox(
                    active=is_active,
                    size_hint_x=None,
                    width=50,
                    selected_color=self.theme_cls.primary_color
                )
                checkbox.voelker_name = volk_name
                checkbox.bind(active=lambda instance, value, volk_name=volk_name: 
                            self.on_checkbox_active(instance, value, volk_name))

                h_layout.add_widget(label)
                h_layout.add_widget(checkbox)

                # Füge Dropdown für Menschen hinzu
                if volk_name == 'Mensch':
                    talent_button = MDIconButton(
                        icon="menu-down",
                        size_hint=(None, None),
                        size=(dp(48), dp(48)),
                        on_release=self.show_talent_menu
                    )
                    
                    talent_label = MDLabel(
                        text=self.aktuelles_talent,
                        size_hint_x=None,
                        width=dp(200)
                    )
                    
                    h_layout.add_widget(talent_label)
                    h_layout.add_widget(talent_button)

                container.add_widget(h_layout)
                self.add_additional_info(container, volk)

        except Exception as e:
            Logger.error(f"Fehler in aktualisiere_ui: {e}", exc_info=True)

    def get_freie_talente(self):
        """Gibt eine Liste von freien Talenten zurück"""
        frei_talente = self.controller.charakter.get_freie_talente()
        if not frei_talente:
            frei_talente = ['Keine freien Talente verfügbar']
        return frei_talente

    def add_additional_info(self, container, volk):
        # Methode zum Hinzufügen von Zusatzinformationen (Handicaps, Talente, etc.)
        for info_type, items in [
            ('Handicaps', volk.handicaps),
            ('Talente', volk.talente),
            ('Besonderheiten', volk.besonderheiten)
        ]:
            if items:
                for item in items:
                    info_layout = MDBoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=25,
                        spacing=5,
                        padding=(40, 0)
                    )
                    
                    info_label = MDLabel(
                        text=item,
                        halign='left',
                        theme_text_color="Secondary",
                        size_hint_x=None,
                        width=1000
                    )
                    
                    info_layout.add_widget(info_label)
                    container.add_widget(info_layout)

    def on_checkbox_active(self, instance, value, selected_volk_name):
        if value:
            # Deaktiviere alle anderen Checkboxes
            container = self.ids.voelker_content_container
            for child in container.children:
                if isinstance(child, MDBoxLayout):
                    for widget in child.children:
                        if isinstance(widget, MDCheckbox) and widget != instance:
                            widget.active = False
                            volk_text = widget.voelker_name
                            self.controller.charakter.voelker_selected[volk_text] = False
                            volk_obj = self.controller.charakter.voelker.get(volk_text)
                            if volk_obj:
                                volk_obj.abwaehlen()
            
            self.controller.charakter.voelker_selected[selected_volk_name] = True
            selected_volk = self.controller.charakter.voelker.get(selected_volk_name)
            if selected_volk:
                selected_volk.auswaehlen()
        else:
            self.controller.charakter.voelker_selected[selected_volk_name] = False
            volk_obj = self.controller.charakter.voelker.get(selected_volk_name)
            if volk_obj:
                volk_obj.abwaehlen()
            
            if not any(self.controller.charakter.voelker_selected.values()):
                self.controller.charakter.voelker_selected["Mensch"] = True
                if "Mensch" in self.controller.charakter.voelker:
                    self.controller.charakter.voelker["Mensch"].auswaehlen()
                self.aktualisiere_ui()

        Logger.info(f"Volk '{selected_volk_name}' gesetzt auf {value}")
        self.controller.charakter.dispatch('on_charakter_change')