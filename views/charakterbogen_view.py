# views/charakterbogen_view.py

from kivy.lang import Builder
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.logger import Logger
from functools import partial
from kivy.metrics import dp
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout

# KivyMD Imports
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton, MDButtonText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.gridlayout import MDGridLayout

# Importieren der benutzerdefinierten Module
from controllers.decorators import Fehlerbehandlung
from controllers.charakter_controller import CharakterController
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild

kv = '''
<CharakterbogenWidget>:
    orientation: 'vertical'
    padding: 10
    spacing: 10

    MDScrollView:
        do_scroll_x: False
        do_scroll_y: True

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: 10
            padding: 10   

            # Überschrift Profil
            LeftAlignedLabel:
                text: "Charakter"
                font_size: '18sp'
                bold: True
                size_hint_y: None
                height: 30
                spacing: 10
                padding: 10 

            # Profil-Abschnitt, der die Profildaten dynamisch anzeigt
            MDBoxLayout:
                id: profil_section
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
                padding: 10    

            # Überschrift Attribute
            LeftAlignedLabel:
                text: "Attribute"
                font_size: '18sp'
                bold: True
                size_hint_y: None
                height: 20
                spacing: 5
                padding: 10 

            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
                padding: 10               

                MDGridLayout:
                    id: attribut_grid
                    cols: 2
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: 20
                    spacing: 5  # Entfernt den Abstand zwischen den Widgets
                    padding: 10  # Entfernt die Einrückung

            # Überschrift Fertigkeiten
            LeftAlignedLabel:
                text: "Fertigkeiten"
                font_size: '18sp'
                bold: True
                size_hint_y: None
                height: 20
                spacing: 5
                padding: 10 

            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
                padding: 10   

                MDGridLayout:
                    id: fertigkeit_grid
                    cols: 2
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: 20
                    spacing: 5
                    padding: 10

            # Abgeleitete Werte Abschnitt
            LeftAlignedLabel:
                text: "Abgeleitete Werte:"
                font_size: '18sp'
                bold: True
                size_hint_y: None
                height: 30
                spacing: 10
                padding: 10 

            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
                padding: 10   

                MDGridLayout:
                    id: abgeleitete_werte_grid
                    cols: 2
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: 30
                    spacing: 10
                    padding: 10 

            # Volk Abschnitt

            MDBoxLayout:
                id: volk_section
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
                padding: 10   

            # Handicaps Abschnitt
            LeftAlignedLabel:
                text: "Handicaps:"
                font_size: '18sp'
                bold: True
                size_hint_y: None
                height: 30
                spacing: 10
                padding: 10 

            MDBoxLayout:
                id: handicaps_section
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
                padding: 10   

            # Talente Abschnitt
            LeftAlignedLabel:
                text: "Talente:"
                font_size: '18sp'
                bold: True
                size_hint_y: None
                height: 30
                spacing: 10
                padding: 10 

            MDBoxLayout:
                id: talente_section
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
                padding: 10   

            # Mächte Abschnitt
            LeftAlignedLabel:
                text: "Mächte:"
                font_size: '18sp'
                bold: True
                size_hint_y: None
                height: 30
                spacing: 10
                padding: 10 

            MDBoxLayout:
                id: maechte_section
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
                padding: 10   

            # Ausrüstung Abschnitt
            LeftAlignedLabel:
                text: "Ausrüstung:"
                font_size: '18sp'
                bold: True
                size_hint_y: None
                height: 30
                spacing: 10
                padding: 10 

            MDBoxLayout:
                id: ausruestung_section
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
                padding: 10   

            # Waffen Abschnitt
            LeftAlignedLabel:
                text: "Waffen:"
                font_size: '18sp'
                bold: True
                size_hint_y: None
                height: 30
                spacing: 10
                padding: 10 

            MDBoxLayout:
                id: waffen_section
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
                padding: 10   

            # Schilde Abschnitt
            LeftAlignedLabel:
                text: "Schild:"
                font_size: '18sp'
                bold: True
                size_hint_y: None
                height: 30
                spacing: 10
                padding: 10 

            MDBoxLayout:
                id: schilde_section
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
                padding: 10  

            # Rüstungen Abschnitt
            LeftAlignedLabel:
                text: "Rüstungen:"
                font_size: '18sp'
                bold: True
                size_hint_y: None
                height: 30
                spacing: 10
                padding: 10 

            MDBoxLayout:
                id: ruestungen_section
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10
                padding: 10   

<WeaponItem@MDBoxLayout>:
    weapon: None
    weapon_text: ''
    button_text: ''
    orientation: 'horizontal'
    size_hint_y: None
    height: 30
    MDLabel:
        text: root.weapon_text
        size_hint_x: 0.8
    MDButton:
        text: root.button_text
        size_hint_x: 0.2
        on_press: root.on_button_press()

<ArmorItem@MDBoxLayout>:
    armor: None
    armor_text: ''
    button_text: ''
    orientation: 'horizontal'
    size_hint_y: None
    height: 30
    MDLabel:
        text: root.armor_text
        size_hint_x: 0.8
    MDButton:
        text: root.button_text
        size_hint_x: 0.2
        on_press: root.on_button_press()

<EquipmentItem@MDBoxLayout>:
    item: None
    item_text: ''
    button_text: ''
    root_widget: None
    orientation: 'horizontal'
    size_hint_y: None
    height: 30

    MDLabel:
        text: root.item_text
        size_hint_x: 0.8

    MDButton:
        text: root.button_text
        size_hint_x: 0.2
        on_press: root.on_button_press()
'''

Builder.load_string(kv)

# Definition der LeftAlignedLabel-Klasse
class LeftAlignedLabel(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = 'left'
        self.valign = 'middle'
        self.text_size = (self.width, None)
        self.bind(width=self._update_text_size)

    def _update_text_size(self, *args):
        self.text_size = (self.width, None)

class CharakterbogenWidget(MDBoxLayout):
    # ObjectProperties für die Widgets
    attribut_grid = ObjectProperty(None)
    fertigkeit_grid = ObjectProperty(None)
    handicaps_section = ObjectProperty(None)
    talente_section = ObjectProperty(None)
    maechte_section = ObjectProperty(None)
    ausruestung_section = ObjectProperty(None)
    waffen_section = ObjectProperty(None)
    ruestungen_section = ObjectProperty(None)
    profil_section = ObjectProperty(None)
    volk_section = ObjectProperty(None)
    abgeleitete_werte_grid = ObjectProperty(None)
    schilde_section = ObjectProperty(None)

    # Speichern des aktuellen Charakters
    charakter = ObjectProperty(None)
    bindings_established = False  # Um zu wissen, ob die Bindings bereits eingerichtet wurden

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = App.get_running_app().controller
        self.charakter = self.controller.charakter

        # Initiale Übersicht erstellen
        Clock.schedule_once(self.update_overview, 0)

        Logger.info("CharakterbogenWidget initialisiert.")

    def create_dice_layout(self, wert, modifier=0):
        """
        Erstellt ein BoxLayout mit Würfel-Icons und Modifikatoren
        """
        layout = MDBoxLayout(
            orientation='horizontal', 
            size_hint_x=None,
            width=dp(120),
            spacing=dp(2),
            padding=["10dp", "0dp"]
        )
        
        # Würfel Icon
        dice_button = MDIconButton(
            icon=f"dice-d{wert}",
            style="standard"
        )
        layout.add_widget(dice_button)
        
        if modifier != 0:
            # Vorzeichen Icon
            sign_button = MDIconButton(
                icon="plus" if modifier > 0 else "minus",
                style="standard"
            )
            layout.add_widget(sign_button)
            
            # Zahlenwert Icon
            value_button = MDIconButton(
                icon=f"numeric-{abs(modifier)}",
                style="standard"
            )
            layout.add_widget(value_button)
            
        return layout

    def update_overview(self, *args):
        # Aktualisieren Sie die Übersicht basierend auf dem aktuellen Charakter
        Logger.debug("Aktualisiere die Charakterübersicht.")
        charakter = self.charakter
        if not charakter:
            Logger.warning("CharakterbogenWidget: Kein Charakter zum Aktualisieren der Übersicht.")
            return

        # Zugriff auf die GridLayouts via IDs
        attribut_grid = self.ids.attribut_grid
        fertigkeit_grid = self.ids.fertigkeit_grid

        # Profil-Abschnitt aktualisieren
        self.update_profil_section()
        self.update_volk_section()

        # Leeren der bestehenden Einträge (nur die dynamischen)
        attribut_grid.clear_widgets()
        fertigkeit_grid.clear_widgets()

        # Attribute aktualisieren
        for attribut in charakter.attribute.values():
            if attribut.modifier == -2:
                continue  # Item ausblenden

            attribut_grid.add_widget(MDLabel(
                text=attribut.attribut_name,
                font_size="16sp",  # Statt font_style
                size_hint_x=None,
                width=dp(250),
                size_hint_y=None,
                height=dp(40),
                halign='left'
            ))

            dice_layout = self.create_dice_layout(attribut.wert, attribut.modifier)
            attribut_grid.add_widget(dice_layout)

        # Fertigkeiten aktualisieren
        for fertigkeit in charakter.fertigkeiten.values():
            if fertigkeit.modifier == -2:
                continue

            if fertigkeit.modifier == 0 and fertigkeit.wert not in [4, 6, 8, 10, 12]:
                continue

            fertigkeit_grid.add_widget(MDLabel(
                text=fertigkeit.fertigkeit_name,
                font_size="16sp",  # Statt font_style
                size_hint_x=None,
                width=dp(250),
                size_hint_y=None,
                height=dp(40),
                halign='left'
            ))

            dice_layout = self.create_dice_layout(fertigkeit.wert, fertigkeit.modifier)
            fertigkeit_grid.add_widget(dice_layout)

        # Handicaps Abschnitt
        handicaps_section = self.ids.handicaps_section
        handicaps_section.clear_widgets()
        handicaps = charakter.selected_handicaps
        for handicap_name_key in handicaps:
            handicap = charakter.handicaps.get(handicap_name_key)
            if handicap:
                handicaps_section.add_widget(LeftAlignedLabel(
                    text=f"{handicap.name} ({handicap.stufe})",
                    font_size='16sp',
                    size_hint_y=None,
                    height=30
                ))
            else:
                Logger.warning(f"Handicap '{handicap_name_key}' nicht in charakter.handicaps gefunden.")

        # Talente Abschnitt
        talente_section = self.ids.talente_section
        talente_section.clear_widgets()
        talente = charakter.selected_talente
        for talent_name_key in talente:
            talent = charakter.talente.get(talent_name_key)
            if talent:
                talente_section.add_widget(LeftAlignedLabel(
                    text=f"{talent.name}",
                    font_size='16sp',
                    size_hint_y=None,
                    height=30
                ))
            else:
                Logger.warning(f"Talent '{talent_name_key}' nicht in charakter.talente gefunden.")

        # Mächte Abschnitt
        maechte_section = self.ids.maechte_section
        maechte_section.clear_widgets()
        maechte = charakter.selected_maechte
        for macht_name_key in maechte:
            macht = charakter.maechte.get(macht_name_key)
            if macht:
                maechte_section.add_widget(LeftAlignedLabel(
                    text=f"{macht.name}, Rang: {macht.rang}, Machtpunkte: {macht.machtpunkte}, "
                        f"Reichweite: {macht.reichweite}, Dauer: {macht.dauer}, Effekt: {macht.effekt}",
                    font_size='16sp',
                    size_hint_y=None,
                    height=30
                ))
            else:
                Logger.warning(f"Macht '{macht_name_key}' nicht in charakter.maechte gefunden.")

        # Ausrüstung Abschnitt
        ausruestung_section = self.ids.ausruestung_section
        ausruestung_section.clear_widgets()

        alle_ausruestung = [item for item in charakter.ausruestung.values() if item.ausgewaehlt]

        for item in alle_ausruestung:
            item_text = f"{item.name} x{item.menge}"
            item_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=45)
            item_label = LeftAlignedLabel(
                text=item_text,
                font_size='16sp',
                size_hint_x=0.8
            )

            if isinstance(item, Waffe) or isinstance(item, Ruestung) or isinstance(item, Schild):
                button_text = "Anlegen" if not item.angelegt else "Ablegen"
                toggle_button = MDButton(style="filled")
                toggle_button.add_widget(MDButtonText(
                    text=button_text
                ))
                toggle_button.bind(on_press=partial(self.toggle_item, item))
                item_layout.add_widget(item_label)
                item_layout.add_widget(toggle_button)
            else:
                # Keine Möglichkeit zum Anlegen für allgemeine Ausrüstung -> kein Button
                item_layout.add_widget(item_label)

            ausruestung_section.add_widget(item_layout)

        # Waffen Abschnitt
        waffen_section = self.ids.waffen_section
        waffen_section.clear_widgets()
        # Filtere alle angelegten Waffen aus ausruestung
        waffen = [w for w in charakter.ausruestung.values() if isinstance(w, Waffe) and w.angelegt]

        for waffe in waffen:
            waffe_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            eigenschaften = waffe.eigenschaften
            eigenschaften_text = (
                f"Schaden: {eigenschaften.get('Schaden', '-')}, "
                f"Reichweite: {eigenschaften.get('Reichweite', '-')}, "
                f"FR: {eigenschaften.get('FR', '-')}, "
                f"Schuss: {eigenschaften.get('Schuss', '-')}, "
                f"PB: {eigenschaften.get('PB', '-')}"
            )

            weapon_label = LeftAlignedLabel(
                text=f"{waffe.name}, {eigenschaften_text}",
                font_size='16sp',
                size_hint_x=0.8
            )

            waffe_layout.add_widget(weapon_label)
            waffen_section.add_widget(waffe_layout)

        # Schilde Abschnitt
        schilde_section = self.ids.schilde_section
        schilde_section.clear_widgets()
        schilde = [s for s in charakter.ausruestung.values() if isinstance(s, Schild) and s.angelegt]

        for schild in schilde:
            schild_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=30)

            schild_label = LeftAlignedLabel(
                text=f"{schild.name}, Parade={schild.parade}, Deckung={schild.deckung}, Mindeststärke={schild.mindeststaerke}",
                font_size='16sp',
                size_hint_x=0.8
            )

            schild_layout.add_widget(schild_label)
            schilde_section.add_widget(schild_layout)

        # Rüstungen Abschnitt
        ruestungen_section = self.ids.ruestungen_section
        ruestungen_section.clear_widgets()
        ruestungen = [r for r in charakter.ausruestung.values() if isinstance(r, Ruestung) and r.angelegt]

        for ruestung in ruestungen:
            ruestung_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=30)

            armor_label = LeftAlignedLabel(
                text=(
                    f"{ruestung.name}, Schutz: "
                    f"Torso={ruestung.torso}, Arme={ruestung.arme}, "
                    f"Beine={ruestung.beine}, Kopf={ruestung.kopf}"
                ),
                font_size='16sp',
                size_hint_x=0.8
            )

            ruestung_layout.add_widget(armor_label)
            ruestungen_section.add_widget(ruestung_layout)

        # Gesamten Rüstungsschutz berechnen
        gesamt_ruestungsschutz = charakter.berechne_gesamt_ruestungsschutz()

        # Text für den Gesamt-Rüstungsschutz erstellen
        gesamt_schutz_text = (
            f"Gesamter Rüstungsschutz: "
            f"Torso={gesamt_ruestungsschutz['Torso']}, "
            f"Arme={gesamt_ruestungsschutz['Arme']}, "
            f"Beine={gesamt_ruestungsschutz['Beine']}, "
            f"Kopf={gesamt_ruestungsschutz['Kopf']}"
        )

        # Label für den Gesamt-Rüstungsschutz erstellen
        gesamt_schutz_label = LeftAlignedLabel(
            text=gesamt_schutz_text,
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=30
        )

        ruestungen_section.add_widget(gesamt_schutz_label)

        # Abgeleitete Werte Abschnitt
        abgeleitete_werte_grid = self.ids.abgeleitete_werte_grid
        abgeleitete_werte_grid.clear_widgets()

        abgeleitete_werte = {
            'Bewegungsweite': charakter.bewegungsweite,
            'Parade': charakter.parade,
            'Robustheit': charakter.robustheit_mit_ruestung,
            'Machtpunkte': charakter.machtpunkte,
            'Wunden': charakter.wunden,
            'Erschöpfung': charakter.erschoepfung,
            'Bennys': charakter.bennys,
            'Entschlossenheit': charakter.entschlossenheit,
            'Maximale Traglast': f"{charakter.gesamtgewicht} / {charakter.maximale_traglast} kg",
        }

        for key, value in abgeleitete_werte.items():
            abgeleitet_label = LeftAlignedLabel(
                text=f"{key}:",
                size_hint_x=None,
                width=250,
                size_hint_y=None,
                height=30
            )
            wert_label = LeftAlignedLabel(
                text=str(value),
                size_hint_x=None,
                width=250,
                size_hint_y=None,
                height=30
            )
            abgeleitete_werte_grid.add_widget(abgeleitet_label)
            abgeleitete_werte_grid.add_widget(wert_label)


    def update_profil_section(self):
        """Zeigt die Profildaten des Charakters als Label ohne Eingabefelder an."""
        charakter = self.charakter
        profil_data = charakter.profil_daten

        # Lösche vorhandene Widgets im Profil-Abschnitt
        profil_section = self.ids.profil_section
        profil_section.clear_widgets()

        # Erstelle und füge Widgets für jedes Profil-Datenfeld hinzu
        for key, value in profil_data.items():
            profil_section.add_widget(LeftAlignedLabel(
                text=f"{key}: {value}",
                font_size='15sp',
                size_hint_y=None,
                padding=10,
                height=30
            ))

    def update_volk_section(self):
        """Zeigt die Informationen zum ausgewählten Volk im Charakterbogen an."""
        charakter = self.charakter
        volk_section = self.ids.volk_section
        volk_section.clear_widgets()

        # Finde den Namen des ausgewählten Volkes
        selected_volk_name = None
        for volk_name, aktiv in charakter.voelker_selected.items():
            if aktiv:
                selected_volk_name = volk_name
                break

        if not selected_volk_name:
            # Kein Volk ausgewählt
            volk_section.add_widget(LeftAlignedLabel(
                text="Kein Volk ausgewählt.",
                font_size='16sp',
                size_hint_y=None,
                height=30
            ))
            return

        # Füge den Namen des Volkes hinzu
        volk_name_label = LeftAlignedLabel(
            text=f"Volk: {selected_volk_name}",
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=30
        )
        volk_section.add_widget(volk_name_label)

        # Holen der Volk-Daten aus charakter.voelker
        selected_volk = charakter.voelker.get(selected_volk_name)
        if not selected_volk:
            Logger.warning(f"Keine Daten für Volk '{selected_volk_name}' gefunden.")
            volk_section.add_widget(LeftAlignedLabel(
                text="Keine Daten für das ausgewählte Volk vorhanden.",
                font_size='15sp',
                size_hint_y=None,
                padding=10,
                height=30
            ))
            return

        # Talente anzeigen
        talente = selected_volk.talente
        if talente:
            talente_label = LeftAlignedLabel(
                text="Talente:",
                font_size='15sp',
                bold=True,
                size_hint_y=None,
                height=30
            )
            volk_section.add_widget(talente_label)
            for talent in talente:
                volk_section.add_widget(LeftAlignedLabel(
                    text=f"- {talent}",
                    font_size='15sp',
                    size_hint_y=None,
                    padding=10,
                    height=30
                ))

        # Handicaps anzeigen
        handicaps = selected_volk.handicaps
        if handicaps:
            handicaps_label = LeftAlignedLabel(
                text="Handicaps:",
                font_size='15sp',
                bold=True,
                size_hint_y=None,
                height=30
            )
            volk_section.add_widget(handicaps_label)
            for handicap in handicaps:
                volk_section.add_widget(LeftAlignedLabel(
                    text=f"- {handicap}",
                    font_size='15sp',
                    size_hint_y=None,
                    padding=10,
                    height=30
                ))

        # Besonderheiten anzeigen
        besonderheiten = selected_volk.besonderheiten
        if besonderheiten:
            besonderheiten_label = LeftAlignedLabel(
                text="Besonderheiten:",
                font_size='15sp',
                bold=True,
                size_hint_y=None,
                height=30
            )
            volk_section.add_widget(besonderheiten_label)
            for besonderheit in besonderheiten:
                volk_section.add_widget(LeftAlignedLabel(
                    text=f"- {besonderheit}",
                    font_size='15sp',
                    size_hint_y=None,
                    padding=10,
                    height=30
                ))

    def toggle_item(self, item, instance):
        # Finden des entsprechenden Objekts in den Charakterdatenstrukturen
        charakter = self.charakter

        # Prüfen, ob das Item eine Waffe, Rüstung oder Schild ist
        if isinstance(item, Waffe):
            item_list = charakter.selected_waffen
        elif isinstance(item, Ruestung):
            item_list = charakter.selected_ruestungen
        elif isinstance(item, Schild):
            item_list = charakter.selected_schilde
        else:
            item_list = charakter.selected_allgemeine_ausruestung

        # Suchen des entsprechenden Objekts in der Liste
        for charakter_item in item_list:
            if charakter_item.name == item.name:
                # Toggle 'angelegt' Status
                charakter_item.toggle_angelegt()
                break
        else:
            Logger.warning(f"Item '{item.name}' nicht in den Charakterdaten gefunden.")

        charakter.berechne_abgeleitete_werte()
        self.update_overview(0)
