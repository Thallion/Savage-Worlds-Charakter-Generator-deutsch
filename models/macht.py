import logging, unittest, json
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.event import EventDispatcher

class Macht(EventDispatcher):
    name = StringProperty("")
    rang = StringProperty("")
    machtpunkte = NumericProperty(0)
    reichweite = StringProperty("")
    dauer = StringProperty("")
    effekt = StringProperty("")
    anmerkungen = StringProperty("")
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)
    voraussetzungen = ListProperty([])

    def __init__(self, name, rang, machtpunkte, reichweite, dauer, effekt='', anmerkungen='', voraussetzungen=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.rang = rang
        self.machtpunkte = machtpunkte
        self.reichweite = reichweite
        self.dauer = dauer
        self.effekt = effekt
        self.anmerkungen = anmerkungen
        self.ausgewaehlt = False
        self.aktiv = True
        self.voraussetzungen = voraussetzungen or []

    def __str__(self):
        return f"{self.name} (Rang: {self.rang}, Machtpunkte: {self.machtpunkte}, Reichweite: {self.reichweite}, Dauer: {self.dauer})"

    def auswaehlen(self):
        if not self.ausgewaehlt:
            self.ausgewaehlt = True
            logging.debug(f"Macht '{self.name}' wurde ausgewählt.")
            return True
        else:
            logging.warning(f"Macht '{self.name}' ist bereits ausgewählt.")
            return False

    def abwaehlen(self):
        if self.ausgewaehlt:
            self.ausgewaehlt = False
            logging.debug(f"Macht '{self.name}' wurde abgewählt.")
            return True
        else:
            logging.warning(f"Macht '{self.name}' ist nicht ausgewählt.")
            return False


    def voraussetzungen_erfuellt(self, charakter):
        """
        Prüft, ob der Charakter die Voraussetzungen für die Macht erfüllt.
        Da wir die Voraussetzungen vorerst ignorieren, geben wir immer True zurück.
        """
        return True  # Vorläufiger Rückgabewert
