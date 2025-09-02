# views/charakterbogen_view.py
"""
View-Komponente für den Charakterbogen nach dem MVC-Pattern.
Stellt die Benutzerschnittstelle zur Anzeige der Charakterdaten bereit.
"""

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

# Domänenspezifische Imports
from controllers.decorators import Fehlerbehandlung
from controllers.charakter_controller import CharakterController
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild

# Konstanten für bessere Lesbarkeit und Wartbarkeit
LABEL_FONT_SIZE = '16sp'
HEADER_FONT_SIZE = '18sp'
SUBHEADER_FONT_SIZE = '15sp'
ROW_HEIGHT = 20
GRID_WIDTH = dp(250)
LABEL_WIDTH = 250
GRID_HEIGHT = dp(30)
DICE_LAYOUT_WIDTH = dp(120)
INFO_PADDING = 5

# KV-Datei laden
Builder.load_file('/home/jean/Dokumente/GitHub/Savage-Worlds-Charakter-Generator-deutsch/views/charakterbogen_view.kv')

class LeftAlignedLabel(MDLabel):
    """Spezielles Label mit linksbündiger Ausrichtung."""
    
    def __init__(self, **kwargs):
        """Initialisiert das LeftAlignedLabel mit linksbündiger Ausrichtung."""
        super().__init__(**kwargs)
        self.halign = 'left'
        self.valign = 'middle'
        self.text_size = (self.width, None)
        self.bind(width=self._update_text_size)

    def _update_text_size(self, *args):
        """Aktualisiert die Textgröße basierend auf der Breite."""
        self.text_size = (self.width, None)


class CharakterbogenWidget(MDBoxLayout):
    """
    Widget zur Anzeige des vollständigen Charakterbogens.
    Stellt alle Charakterdaten in einer übersichtlichen Form dar.
    """
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
    controller = ObjectProperty(None)

    def __init__(self, **kwargs):
        """Initialisiert das CharakterbogenWidget und lädt die Daten."""
        super().__init__(**kwargs)
        self._initialize_controller()
        
        # Initiale Übersicht erstellen
        Clock.schedule_once(self.update_overview, 0)
        
        Logger.info("CharakterbogenWidget initialisiert.")

    def _initialize_controller(self):
        """Initialisiert die Verbindung zum Controller und holt den Charakter."""
        app = App.get_running_app()
        self.controller = app.controller if hasattr(app, 'controller') else None
        
        if not self.controller:
            Logger.error("CharakterbogenWidget: Controller nicht gefunden")
            return
            
        # Binde an Controller-Events für Charakteränderungen
        self.controller.bind(charakter=self._on_controller_charakter_changed)
        
        # Setze initialen Charakter
        self.charakter = self.controller.charakter

    def _on_controller_charakter_changed(self, instance, new_charakter):
        """
        Wird aufgerufen, wenn sich der Charakter im Controller ändert.
        Aktualisiert die lokale Referenz und das UI.
        """
        Logger.info("CharakterbogenWidget: Neuer Charakter vom Controller erhalten")
        
        # Alte Charakter-Bindings entfernen, falls vorhanden
        if self.charakter:
            try:
                self.charakter.unbind(on_charakter_change=self._on_charakter_change)
            except:
                pass  # Ignoriere Fehler beim Unbind
        
        # Neuen Charakter setzen
        self.charakter = new_charakter
        
        # An neue Charakter-Events binden
        if self.charakter:
            self.charakter.bind(on_charakter_change=self._on_charakter_change)
        
        # UI vollständig aktualisieren
        Clock.schedule_once(self.update_overview, 0.1)

    def _on_charakter_change(self, *args):
        """Wird aufgerufen, wenn sich Charakterdaten ändern."""
        Clock.schedule_once(self.update_overview, 0.1)

    def _create_dice_layout(self, wert, modifier=0):
        """
        Erstellt ein BoxLayout mit Würfel-Icons und Modifikatoren.
        
        Args:
            wert: Der Würfelwert (4, 6, 8, etc.)
            modifier: Der Modifikator (+1, -2, etc.)
            
        Returns:
            MDBoxLayout: Layout mit den Würfel-Icons
        """
        layout = MDBoxLayout(
            orientation='horizontal', 
            size_hint_x=None,
            width=DICE_LAYOUT_WIDTH,
            spacing=dp(2),
            padding=["10dp", "0dp"]
        )

        # Würfel Icon
        dice_button = MDIconButton(
            icon=f"dice-d{wert}",
            style="standard"
        )
        layout.add_widget(dice_button)

        # Modifikator-Icons nur anzeigen, wenn ein Modifikator vorhanden ist
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
        """
        Aktualisiert die gesamte Charakterübersicht.
        Ruft die spezialisierten Update-Methoden für jeden Abschnitt auf.
        """
        Logger.debug("Aktualisiere die Charakterübersicht.")
        if not self.charakter:
            Logger.warning("CharakterbogenWidget: Kein Charakter zum Aktualisieren der Übersicht.")
            return

        # Aktualisierung der einzelnen Sektionen
        self._update_profil_section()
        self._update_volk_section()
        self._update_attribute_section()
        self._update_fertigkeiten_section()
        self._update_abgeleitete_werte_section()
        self._update_handicaps_section()
        self._update_talente_section()
        self._update_maechte_section()
        self._update_ausruestung_section()
        self._update_waffen_section()
        self._update_schilde_section()
        self._update_ruestungen_section()

    def _update_profil_section(self):
        """
        Aktualisiert den Profil-Abschnitt des Charakterbogens.
        Zeigt die grundlegenden Charakterdaten an.
        """
        profil_data = self.charakter.profil_daten

        # Lösche vorhandene Widgets im Profil-Abschnitt
        profil_section = self.ids.profil_section
        profil_section.clear_widgets()

        # Erstelle und füge Widgets für jedes Profil-Datenfeld hinzu
        for key, value in profil_data.items():
            profil_section.add_widget(LeftAlignedLabel(
                text=f"{key}: {value}",
                font_size=SUBHEADER_FONT_SIZE,
                size_hint_y=None,
                padding=INFO_PADDING,
                height=ROW_HEIGHT
            ))

    def _update_volk_section(self):
        """
        Aktualisiert den Volks-Abschnitt des Charakterbogens.
        Zeigt Informationen zum gewählten Volk an.
        """
        volk_section = self.ids.volk_section
        volk_section.clear_widgets()

        # Finde den Namen des ausgewählten Volkes
        selected_volk_name = None
        for volk_name, aktiv in self.charakter.voelker_selected.items():
            if aktiv:
                selected_volk_name = volk_name
                break

        if not selected_volk_name:
            # Kein Volk ausgewählt
            volk_section.add_widget(LeftAlignedLabel(
                text="Kein Volk ausgewählt.",
                font_size=LABEL_FONT_SIZE,
                size_hint_y=None,
                height=ROW_HEIGHT
            ))
            return

        # Füge den Namen des Volkes hinzu
        volk_name_label = LeftAlignedLabel(
            text=f"Volk: {selected_volk_name}",
            font_size=HEADER_FONT_SIZE,
            bold=True,
            size_hint_y=None,
            height=ROW_HEIGHT
        )
        volk_section.add_widget(volk_name_label)

        # Holen der Volk-Daten aus charakter.voelker
        selected_volk = self.charakter.voelker.get(selected_volk_name)
        if not selected_volk:
            Logger.warning(f"Keine Daten für Volk '{selected_volk_name}' gefunden.")
            volk_section.add_widget(LeftAlignedLabel(
                text="Keine Daten für das ausgewählte Volk vorhanden.",
                font_size=SUBHEADER_FONT_SIZE,
                size_hint_y=None,
                padding=INFO_PADDING,
                height=ROW_HEIGHT
            ))
            return

        # Volkseigenschaften anzeigen
        self._add_volk_eigenschaften(volk_section, "Talente", selected_volk.talente)
        self._add_volk_eigenschaften(volk_section, "Handicaps", selected_volk.handicaps)
        self._add_volk_eigenschaften(volk_section, "Besonderheiten", selected_volk.besonderheiten)

    def _add_volk_eigenschaften(self, container, titel, eigenschaften_liste):
        """
        Fügt eine Liste von Volk-Eigenschaften zum Container hinzu.
        
        Args:
            container: Der Container, zu dem die Eigenschaften hinzugefügt werden sollen
            titel: Die Überschrift für die Eigenschaften
            eigenschaften_liste: Liste der anzuzeigenden Eigenschaften
        """
        if not eigenschaften_liste:
            return
            
        # Überschrift
        container.add_widget(LeftAlignedLabel(
            text=f"{titel}:",
            font_size=SUBHEADER_FONT_SIZE,
            bold=True,
            size_hint_y=None,
            height=ROW_HEIGHT
        ))
        
        # Eigenschaften
        for eigenschaft in eigenschaften_liste:
            container.add_widget(LeftAlignedLabel(
                text=f"- {eigenschaft}",
                font_size=SUBHEADER_FONT_SIZE,
                size_hint_y=None,
                padding=INFO_PADDING,
                height=ROW_HEIGHT
            ))

    def _update_attribute_section(self):
        """
        Aktualisiert den Attribut-Abschnitt des Charakterbogens.
        Zeigt alle Attribute mit ihren Werten und Modifikatoren an.
        """
        attribut_grid = self.ids.attribut_grid
        attribut_grid.clear_widgets()

        # Attribute anzeigen
        for attribut in self.charakter.attribute.values():
            # Überspringe deaktivierte Attribute
            if attribut.modifier == -2:
                continue

            attribut_grid.add_widget(MDLabel(
                text=attribut.attribut_name,
                font_size=LABEL_FONT_SIZE,
                size_hint_x=None,
                width=GRID_WIDTH,
                size_hint_y=None,
                height=GRID_HEIGHT,
                halign='left'
            ))

            dice_layout = self._create_dice_layout(attribut.wert, attribut.modifier)
            attribut_grid.add_widget(dice_layout)

    def _update_fertigkeiten_section(self):
        """
        Aktualisiert den Fertigkeiten-Abschnitt des Charakterbogens.
        Zeigt alle aktiven Fertigkeiten mit ihren Werten und Modifikatoren an.
        """
        fertigkeit_grid = self.ids.fertigkeit_grid
        fertigkeit_grid.clear_widgets()

        # Fertigkeiten anzeigen
        for fertigkeit in self.charakter.fertigkeiten.values():
            # Überspringe deaktivierte oder nicht relevante Fertigkeiten
            if fertigkeit.modifier == -2:
                continue

            if fertigkeit.modifier == 0 and fertigkeit.wert not in [4, 6, 8, 10, 12]:
                continue

            fertigkeit_grid.add_widget(MDLabel(
                text=fertigkeit.fertigkeit_name,
                font_size=LABEL_FONT_SIZE,
                size_hint_x=None,
                width=GRID_WIDTH,
                size_hint_y=None,
                height=GRID_HEIGHT,
                halign='left'
            ))

            dice_layout = self._create_dice_layout(fertigkeit.wert, fertigkeit.modifier)
            fertigkeit_grid.add_widget(dice_layout)

    def _update_handicaps_section(self):
        """
        Aktualisiert den Handicaps-Abschnitt des Charakterbogens.
        Zeigt alle ausgewählten Handicaps an.
        """
        handicaps_section = self.ids.handicaps_section
        handicaps_section.clear_widgets()
        
        # Ausgewählte Handicaps anzeigen
        for handicap_name_key in self.charakter.selected_handicaps:
            handicap = self.charakter.handicaps.get(handicap_name_key)
            if handicap:
                handicaps_section.add_widget(LeftAlignedLabel(
                    text=f"{handicap.name} ({handicap.stufe})",
                    font_size=LABEL_FONT_SIZE,
                    size_hint_y=None,
                    height=ROW_HEIGHT
                ))
            else:
                Logger.warning(f"Handicap '{handicap_name_key}' nicht in charakter.handicaps gefunden.")

    def _update_talente_section(self):
            """
            Aktualisiert den Talente-Abschnitt des Charakterbogens.
            Zeigt alle ausgewählten Talente an, inklusive mehrfacher Instanzen.
            """
            talente_section = self.ids.talente_section
            talente_section.clear_widgets()
            
            # Ausgewählte Talente anzeigen
            for talent_name_key in self.charakter.selected_talente:
                talent = self.charakter.talente.get(talent_name_key)
                if talent:
                    # Anzeigename für mehrfache Instanzen anpassen
                    display_name = talent.name
                    if '_' in talent_name_key and talent_name_key.split('_')[-1].isdigit():
                        instance_num = talent_name_key.split('_')[-1]
                        display_name = f"{talent.name} (#{instance_num})"
                    
                    talente_section.add_widget(LeftAlignedLabel(
                        text=display_name,
                        font_size=LABEL_FONT_SIZE,
                        size_hint_y=None,
                        height=ROW_HEIGHT
                    ))
                else:
                    Logger.warning(f"Talent '{talent_name_key}' nicht in charakter.talente gefunden.")

    def _update_maechte_section(self):
        """
        Aktualisiert den Mächte-Abschnitt des Charakterbogens.
        Zeigt alle ausgewählten Mächte mit ihren Eigenschaften an.
        """
        maechte_section = self.ids.maechte_section
        maechte_section.clear_widgets()
        
        # Ausgewählte Mächte anzeigen
        for macht_name_key in self.charakter.selected_maechte:
            macht = self.charakter.maechte.get(macht_name_key)
            if macht:
                maechte_section.add_widget(LeftAlignedLabel(
                    text=(f"{macht.name}, Rang: {macht.rang}, Machtpunkte: {macht.machtpunkte}, "
                          f"Reichweite: {macht.reichweite}, Dauer: {macht.dauer}, Effekt: {macht.effekt}"),
                    font_size=LABEL_FONT_SIZE,
                    size_hint_y=None,
                    height=ROW_HEIGHT
                ))
            else:
                Logger.warning(f"Macht '{macht_name_key}' nicht in charakter.maechte gefunden.")

    def _update_ausruestung_section(self):
        """
        Aktualisiert den Ausrüstungs-Abschnitt des Charakterbogens.
        Zeigt alle ausgewählten Ausrüstungsgegenstände an.
        """
        ausruestung_section = self.ids.ausruestung_section
        ausruestung_section.clear_widgets()

        # Alle ausgewählte Ausrüstung anzeigen
        alle_ausruestung = [item for item in self.charakter.ausruestung.values() if item.ausgewaehlt]

        for item in alle_ausruestung:
            item_text = f"{item.name} x{item.menge}"
            item_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=45)
            item_label = LeftAlignedLabel(
                text=item_text,
                font_size=LABEL_FONT_SIZE,
                size_hint_x=0.8
            )

            # Spezielle Behandlung für anlegbare Gegenstände
            if self._is_equippable_item(item):
                button_text = "Ablegen" if item.angelegt else "Anlegen"
                toggle_button = MDButton(style="filled")
                toggle_button.add_widget(MDButtonText(
                    text=button_text
                ))
                toggle_button.bind(on_press=partial(self._toggle_item, item))
                item_layout.add_widget(item_label)
                item_layout.add_widget(toggle_button)
            else:
                # Keine Möglichkeit zum Anlegen für allgemeine Ausrüstung -> kein Button
                item_layout.add_widget(item_label)

            ausruestung_section.add_widget(item_layout)

    def _is_equippable_item(self, item):
        """
        Prüft, ob ein Gegenstand anlegbar ist.
        
        Args:
            item: Der zu prüfende Gegenstand
            
        Returns:
            bool: True wenn anlegbar, sonst False
        """
        return (isinstance(item, Waffe) or 
                isinstance(item, Ruestung) or 
                isinstance(item, Schild))

    def _update_waffen_section(self):
        """
        Aktualisiert den Waffen-Abschnitt des Charakterbogens.
        Zeigt alle angelegten Waffen mit ihren Eigenschaften an.
        """
        waffen_section = self.ids.waffen_section
        waffen_section.clear_widgets()
        
        # Angelegte Waffen anzeigen
        waffen = self._get_equipped_items_of_type(Waffe)

        for waffe in waffen:
            eigenschaften = waffe.eigenschaften
            eigenschaften_text = self._format_waffen_eigenschaften(eigenschaften)

            waffe_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=ROW_HEIGHT)
            weapon_label = LeftAlignedLabel(
                text=f"{waffe.name}, {eigenschaften_text}",
                font_size=LABEL_FONT_SIZE,
                size_hint_x=0.8
            )

            waffe_layout.add_widget(weapon_label)
            waffen_section.add_widget(waffe_layout)

    def _format_waffen_eigenschaften(self, eigenschaften):
        """
        Formatiert die Eigenschaften einer Waffe als Text.
        
        Args:
            eigenschaften: Dictionary mit den Waffeneigenschaften
            
        Returns:
            str: Formatierter Text
        """
        return (
            f"Schaden: {eigenschaften.get('Schaden', '-')}, "
            f"Reichweite: {eigenschaften.get('Reichweite', '-')}, "
            f"FR: {eigenschaften.get('FR', '-')}, "
            f"Schuss: {eigenschaften.get('Schuss', '-')}, "
            f"PB: {eigenschaften.get('PB', '-')}"
        )

    def _update_schilde_section(self):
        """
        Aktualisiert den Schilde-Abschnitt des Charakterbogens.
        Zeigt alle angelegten Schilde mit ihren Eigenschaften an.
        """
        schilde_section = self.ids.schilde_section
        schilde_section.clear_widgets()
        
        # Angelegte Schilde anzeigen
        schilde = self._get_equipped_items_of_type(Schild)

        for schild in schilde:
            schild_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=ROW_HEIGHT)
            schild_label = LeftAlignedLabel(
                text=(f"{schild.name}, Parade={schild.parade}, Deckung={schild.deckung}, "
                      f"Mindeststärke={schild.mindeststaerke}"),
                font_size=LABEL_FONT_SIZE,
                size_hint_x=0.8
            )

            schild_layout.add_widget(schild_label)
            schilde_section.add_widget(schild_layout)

    def _update_ruestungen_section(self):
        """
        Aktualisiert den Rüstungs-Abschnitt des Charakterbogens.
        Zeigt alle angelegten Rüstungen und den Gesamtrüstungsschutz an.
        """
        ruestungen_section = self.ids.ruestungen_section
        ruestungen_section.clear_widgets()
        
        # Angelegte Rüstungen anzeigen
        ruestungen = self._get_equipped_items_of_type(Ruestung)

        for ruestung in ruestungen:
            ruestung_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=ROW_HEIGHT)
            armor_label = LeftAlignedLabel(
                text=self._format_ruestung_text(ruestung),
                font_size=LABEL_FONT_SIZE,
                size_hint_x=0.8
            )

            ruestung_layout.add_widget(armor_label)
            ruestungen_section.add_widget(ruestung_layout)
        
        # Gesamtrüstungsschutz anzeigen
        gesamt_rs = self.charakter.berechne_gesamt_ruestungsschutz()
        gesamt_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=ROW_HEIGHT)
        
        gesamt_text = (
            f"Gesamtrüstung: Torso={gesamt_rs['Torso']}, Arme={gesamt_rs['Arme']}, "
            f"Beine={gesamt_rs['Beine']}, Kopf={gesamt_rs['Kopf']}"
        )
        
        gesamt_label = LeftAlignedLabel(
            text=gesamt_text,
            font_size=LABEL_FONT_SIZE,
            bold=True,
            size_hint_x=0.8
        )
        
        gesamt_layout.add_widget(gesamt_label)
        ruestungen_section.add_widget(gesamt_layout)

    def _format_ruestung_text(self, ruestung):
        """
        Formatiert die Informationen einer Rüstung als Text.
        
        Args:
            ruestung: Das Rüstungs-Objekt
            
        Returns:
            str: Formatierter Text
        """
        return (
            f"{ruestung.name}, Torso={ruestung.torso}, Arme={ruestung.arme}, "
            f"Beine={ruestung.beine}, Kopf={ruestung.kopf}, "
            f"Mindeststärke={ruestung.mindeststaerke}"
        )

    def _get_equipped_items_of_type(self, item_type):
        """
        Sammelt alle angelegten Gegenstände eines bestimmten Typs.
        
        Args:
            item_type: Der zu suchende Typ (Waffe, Ruestung, Schild)
            
        Returns:
            list: Liste der angelegten Gegenstände des angegebenen Typs
        """
        return [
            item for item in self.charakter.ausruestung.values()
            if isinstance(item, item_type) and item.angelegt
        ]

    def _toggle_item(self, item, instance):
        """
        Wechselt zwischen Anlegen und Ablegen eines Gegenstands.
        
        Args:
            item: Der betroffene Gegenstand
            instance: Die Button-Instanz, die das Event ausgelöst hat
        """
        if item.angelegt:
            item.ablegen()
        else:
            item.anlegen(self.charakter)
            
        # UI aktualisieren
        self.update_overview(0)
        
        # Abgeleitete Werte neu berechnen
        self.charakter.berechne_abgeleitete_werte()
        
    def _update_abgeleitete_werte_section(self):
        """
        Aktualisiert den Abschnitt mit den abgeleiteten Werten.
        Zeigt Parade, Robustheit, Bewegungsweite etc. an.
        """
        abgeleitete_werte_grid = self.ids.abgeleitete_werte_grid
        abgeleitete_werte_grid.clear_widgets()
        
        # Liste der anzuzeigenden abgeleiteten Werte
        werte = [
            ("Bewegungsweite", str(self.charakter.bewegungsweite)),
            ("Parade", str(self.charakter.parade)),
            ("Robustheit", self.charakter.robustheit_mit_ruestung),
            ("Machtpunkte", str(self.charakter.machtpunkte)),
            ("Wunden", str(self.charakter.wunden)),
            ("Erschöpfung", str(self.charakter.erschoepfung)),
            ("Bennys", str(self.charakter.bennys)),
            ("Entschlossenheit", str(self.charakter.entschlossenheit)),
            ("Vermögen", f"{self.charakter.vermoegen} {self.charakter.waehrungseinheit}"),
            ("Traglast", f"{self.charakter.gesamtgewicht}/{self.charakter.maximale_traglast} kg")
        ]
        
        # Werte anzeigen
        for name, wert in werte:
            abgeleitete_werte_grid.add_widget(MDLabel(
                text=name,
                font_size=LABEL_FONT_SIZE,
                size_hint_x=None,
                width=GRID_WIDTH,
                size_hint_y=None,
                height=GRID_HEIGHT,
                halign='left'
            ))
            
            abgeleitete_werte_grid.add_widget(MDLabel(
                text=wert,
                font_size=LABEL_FONT_SIZE,
                size_hint_x=None,
                width=GRID_WIDTH,
                size_hint_y=None,
                height=GRID_HEIGHT,
                halign='left'
            ))

    def cleanup(self):
        """Bereinigt das Widget beim Beenden"""
        try:
            # Controller-Bindings entfernen
            if self.controller:
                self.controller.unbind(charakter=self._on_controller_charakter_changed)
            
            # Charakter-Bindings entfernen
            if self.charakter:
                self.charakter.unbind(on_charakter_change=self._on_charakter_change)
            
            Logger.info("CharakterbogenWidget bereinigt")
        except Exception as e:
            Logger.error(f"Fehler beim Bereinigen des CharakterbogenWidgets: {str(e)}")