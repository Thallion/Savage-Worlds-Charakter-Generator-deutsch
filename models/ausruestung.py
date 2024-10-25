from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.event import EventDispatcher
from kivy.logger import Logger, LOG_LEVELS
import logging

# Setze Kivy Logger-Level auf DEBUG
Logger.setLevel(LOG_LEVELS['debug'])
Logger.info("Kivy Logger auf DEBUG-Level gesetzt.")

class Ausruestung(EventDispatcher):
    name = StringProperty("")
    kategorie = StringProperty("")  # Kategorie als Property definieren
    gewicht = NumericProperty(0)
    kosten = NumericProperty(0)
    setting = StringProperty("")
    beschreibung = StringProperty("")
    menge = NumericProperty(0)
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)
    angelegt = BooleanProperty(False)

    def __str__(self):
        return f"{self.name} (Setting: {self.setting}, Kosten: {self.kosten}, Gewicht: {self.gewicht}, Menge: {self.menge})"

    def erhoehe_menge(self, anzahl=1):
        self.menge += anzahl
        if self.menge > 0:
            self.ausgewaehlt = True
        logging.debug(f"Menge von '{self.name}' erhöht auf {self.menge}.")

    def verringere_menge(self, anzahl=1):
        self.menge = max(0, self.menge - anzahl)
        if self.menge == 0:
            self.ausgewaehlt = False
        logging.debug(f"Menge von '{self.name}' verringert auf {self.menge}.")

    def setze_beschreibung(self, beschreibung):
        self.beschreibung = beschreibung

    def toggle_angelegt(self):
        self.angelegt = not self.angelegt