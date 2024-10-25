import logging, unittest, json
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.event import EventDispatcher

class Talent(EventDispatcher):
    name = StringProperty("")
    kategorie = StringProperty("")
    rang = StringProperty("")
    voraussetzungen = ListProperty([])
    beschreibung = StringProperty("")
    neue_maechte = NumericProperty(0)
    machtpunkte = NumericProperty(0)
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)

    def __init__(self, name, kategorie, rang, voraussetzungen, beschreibung='', neue_maechte=0, machtpunkte=0, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.kategorie = kategorie
        self.rang = rang
        self.voraussetzungen = voraussetzungen
        self.beschreibung = beschreibung
        self.neue_maechte = neue_maechte
        self.machtpunkte = machtpunkte
        self.ausgewaehlt = False
        self.aktiv = True

    def __str__(self):
        return f"{self.name} ({self.kategorie}, Rang: {self.rang})"

    def auswaehlen(self, charakter):
        if not self.ausgewaehlt:
            if self.voraussetzungen_erfuellt(charakter):
                self.ausgewaehlt = True
                # Erhöhe verfügbare Mächte und Machtpunkte, falls das Talent dies gewährt
                # charakter.verfuegbare_maechte += self.neue_maechte
                # charakter.erhoehe_machtpunkte(self.machtpunkte)
                logging.debug(f"Talent '{self.name}' ausgewählt. Verfügbare Mächte: {charakter.verfuegbare_maechte}, Machtpunkte: {charakter.machtpunkte}")
            else:
                logging.warning(f"Voraussetzungen für Talent '{self.name}' nicht erfüllt.")
        else:
            logging.warning(f"Talent '{self.name}' ist bereits ausgewählt.")

    def abwaehlen(self, charakter):
        if self.ausgewaehlt:
            self.ausgewaehlt = False
            # Verringere verfügbare Mächte und Machtpunkte, falls das Talent dies gewährt
            # charakter.verfuegbare_maechte -= self.neue_maechte
            # charakter.senke_machtpunkte(self.machtpunkte)
            logging.debug(f"Talent '{self.name}' abgewählt. Verfügbare Mächte: {charakter.verfuegbare_maechte}, Machtpunkte: {charakter.machtpunkte}")
        else:
            logging.warning(f"Talent '{self.name}' ist nicht ausgewählt.")

    def voraussetzungen_erfuellt(self, charakter):
        # Hier implementieren wir die Logik zur Überprüfung der Voraussetzungen
        for voraussetzung in self.voraussetzungen:
            if not charakter.erfuellt_voraussetzung(voraussetzung):
                return False
        return True

    def setze_beschreibung(self, beschreibung):
        self.beschreibung = beschreibung
