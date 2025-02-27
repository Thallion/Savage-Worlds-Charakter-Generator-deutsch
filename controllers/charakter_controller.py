# -*- coding: utf-8 -*-
# controllers/charakter_controller.py
from kivy.app import App
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty
from kivy.logger import Logger
from charakter import Charakter
from models.talent import Talent
from models.macht import Macht
import logging
from kivy.config import Config

import functions.fertigkeiten_funktionen

# Logger einrichten
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

class CharakterController(EventDispatcher):
    """
    Der CharakterController ist für die Steuerung und Aktualisierung
    des Charakterobjekts zuständig und kommuniziert mit der UI.
    """
    charakter = ObjectProperty(None)  # Kivy-Property für den Charakter
    current_character_file_path = StringProperty(None)  # Pfad der aktuellen Charakterdatei

    def __init__(self, char_name="", alter="", geschlecht="", konzept="", sprachen="",
                 bennys="3", entschlossenheit="0", beschreibung="", hintergrund=""):
        super().__init__()  # EventDispatcher initialisieren

        # Registrieren von Events
        self.register_event_type('on_charakter_changed')
        self.register_event_type('on_charakter_updated')

        # Erzeuge den Charakter mit allen Profildaten
        # Der Charakter lädt selbständig alle Daten aus dem aktiven Setting (JSON)
        self.charakter = Charakter(
            char_name=char_name,
            alter=alter,
            geschlecht=geschlecht,
            konzept=konzept,
            sprachen=sprachen,
            bennys=bennys,
            entschlossenheit=entschlossenheit,
            beschreibung=beschreibung,
            hintergrund=hintergrund
        )

        logging.debug(f"CharakterController initialisiert mit Charakterobjekt ID {id(self.charakter)}")

        # Binde die update_ui Methode an das on_charakter_change Event des Charakters
        self.charakter.bind(on_charakter_change=self.update_ui)

        Logger.info("CharakterController initialisiert")

    def update_ui(self, *args):
        # Diese Methode wird aufgerufen, wenn sich der Charakter ändert
        self.update_eigenschaften()
        self.dispatch('on_charakter_changed', self.charakter)

    # Methoden zur Attributsteigerung
    def steigere_attribut(self, attribut_name):
        success = self.charakter.steigere_attribut(attribut_name)
        self.charakter.berechne_abgeleitete_werte()
        self.update_charakterbogen()
        self.dispatch('on_charakter_updated')
        return success

    def senke_attribut(self, attribut_name):
        success = self.charakter.senke_attribut(attribut_name)
        self.charakter.berechne_abgeleitete_werte()
        self.update_charakterbogen()
        self.dispatch('on_charakter_updated')
        return success

    # Methoden zur Fertigkeitssteigerung
    def steigere_fertigkeit(self, fertigkeit_name):
        success = self.charakter.steigere_fertigkeit(fertigkeit_name)
        self.charakter.berechne_abgeleitete_werte()
        self.update_charakterbogen()
        self.dispatch('on_charakter_updated')
        return success

    def senke_fertigkeit(self, fertigkeit_name):
        success = self.charakter.senke_fertigkeit(fertigkeit_name)
        self.charakter.berechne_abgeleitete_werte()
        self.update_charakterbogen()
        self.dispatch('on_charakter_updated')
        return success

    def on_charakter_updated(self, *args):
        pass

    # Methoden für Handicaps
    def initialisiere_handicaps(self, handicap_liste):
        self.charakter.initialisiere_handicaps(handicap_liste)
        Logger.info("Handicaps initialisiert.")
        self.update_charakterbogen()

    def waehle_handicap(self, handicap_name):
        success = self.charakter.waehle_handicap(handicap_name)
        self.update_charakterbogen()
        return success

    def entferne_handicap(self, handicap_name):
        success = self.charakter.entferne_handicap(handicap_name)
        self.update_charakterbogen()
        return success

    def aktive_handicaps(self):
        return self.charakter.aktive_handicaps()

    def ausgewaehlte_handicaps(self):
        return self.charakter.ausgewaehlte_handicaps()

    # Methoden für Talente
    # Die Initialisierung der Talente erfolgt nun über den Charakter selbst, basierend auf dem aktiven Setting.
    # Daher wird hier keine externe Methode initialisiere_talente() mehr benötigt.

    def waehle_talent(self, talent_name):
        success = self.charakter.waehle_talent(talent_name)
        self.update_charakterbogen()
        return success

    def entferne_talent(self, talent_name):
        success = self.charakter.entferne_talent(talent_name)
        self.update_charakterbogen()
        return success

    def aktive_talente(self):
        return self.charakter.aktive_talente()

    def ausgewaehlte_talente(self):
        return self.charakter.ausgewaehlte_talente()

    # Methoden für Mächte
    # Die Initialisierung der Mächte erfolgt nun über den Charakter selbst, basierend auf dem aktiven Setting.
    # Daher wird hier keine externe Methode initialisiere_maechte() mehr benötigt.

    def waehle_macht(self, macht_name):
        success = self.charakter.waehle_macht(macht_name)
        self.update_charakterbogen()
        return success

    def entferne_macht(self, macht_name):
        success = self.charakter.entferne_macht(macht_name)
        self.update_charakterbogen()
        return success

    # Methoden für Ausrüstung
    def kaufen_ausruestung(self, item_name, anzahl=1, preis_pro_stueck=None):
        # Prüfen, ob der Gegenstand existiert
        if item_name in self.charakter.ausruestung:
            item = self.charakter.ausruestung[item_name]
        else:
            Logger.warning(f"Ausrüstungsgegenstand '{item_name}' nicht gefunden.")
            return False

        success = self.charakter.kaufen(item, anzahl=anzahl, preis_pro_stueck=preis_pro_stueck)
        if success:
            Logger.debug(f"Ausrüstung '{item.name}' gekauft.")
            self.update_charakterbogen()
        return success

    def verkaufen_ausruestung(self, item_name, anzahl=1, preis_pro_stueck=None):
        # Prüfen, ob der Gegenstand existiert
        if item_name in self.charakter.ausruestung:
            item = self.charakter.ausruestung[item_name]
        else:
            Logger.warning(f"Ausrüstungsgegenstand '{item_name}' nicht gefunden.")
            return False

        erfolg = self.charakter.verkaufen(item, anzahl, preis_pro_stueck)
        if erfolg:
            Logger.debug(f"Ausrüstung '{item.name}' verkauft.")
            self.update_charakterbogen()
        return erfolg

    def update_charakterbogen(self):
        try:
            # Zugriff auf das Charakterbogen-Widget
            charakterbogen_widget = App.get_running_app().root.ids.charakterbogen_widget
            charakterbogen_widget.update_overview()
        except Exception as e:
            pass  # Wenn kein Charakterbogen-Widget vorhanden ist, einfach ignorieren.

    def lade_charakter_von_json(self, dateipfad):
        self.charakter.laden_von_json(dateipfad)
        self.update_charakterbogen()
        self.dispatch('on_charakter_changed', self.charakter)
        self.dispatch('on_charakter_loaded')   
        app = App.get_running_app()
        app.ausruestung_widget.aktualisiere_ausruestung()

    def neuer_charakter(self):
        self.charakter = Charakter()
        self.dispatch('on_charakter_changed', self.charakter)

    def on_charakter_loaded(self):
        pass

    def on_charakter_changed(self, *args):
        self.update_eigenschaften()
        self.update_charakterbogen()

    def update_eigenschaften(self):
        app = App.get_running_app()
        if app:
            eigenschaften_widget = app.get_widget_by_tab_text('Eigenschaften', 'eigenschaften_widget')
            if eigenschaften_widget:
                eigenschaften_widget.update_eigenschaften()
            else:
                Logger.warning("Eigenschaften-Widget nicht gefunden.")
        else:
            Logger.warning("Keine laufende App gefunden.")
