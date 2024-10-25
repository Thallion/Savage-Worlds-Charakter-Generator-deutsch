import logging, unittest, json
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.event import EventDispatcher

class Handicap(EventDispatcher):
    name = StringProperty("")
    stufe = StringProperty("")
    punkte = NumericProperty(0)
    beschreibung = StringProperty("")
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)

    def __init__(self, name, stufe, beschreibung='', **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.stufe = stufe.lower()
        self.beschreibung = beschreibung
        self.ausgewaehlt = False
        self.aktiv = True
        self.update_punkte()

    def update_punkte(self):
        self.punkte = 1 if self.stufe == 'leicht' else 2

    def on_stufe(self, instance, value):
        self.update_punkte()

    def __str__(self):
        return f"{self.name} (Stufe: {self.stufe})"

    def auswaehlen(self):
        self.ausgewaehlt = True
        logging.debug(f"Handicap '{self.name}' ausgewählt.")

    def abwaehlen(self):
        self.ausgewaehlt = False
        logging.debug(f"Handicap '{self.name}' abgewählt.")

    def setze_beschreibung(self, beschreibung):
        self.beschreibung = beschreibung
