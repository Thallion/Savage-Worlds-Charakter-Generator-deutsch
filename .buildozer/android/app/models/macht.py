import unittest, json
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.event import EventDispatcher
from kivy.logger import Logger, LOG_LEVELS

class Macht(EventDispatcher):
    name = StringProperty("")
    rang = StringProperty("")
    machtpunkte = NumericProperty(0)
    reichweite = StringProperty("")
    dauer = StringProperty("")
    effekt = StringProperty("")
    beschreibung = StringProperty("")
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)
    voraussetzungen = ListProperty([])
    custom = BooleanProperty(False) 

    def __init__(self, name, rang, machtpunkte, reichweite, dauer, effekt='', beschreibung='', voraussetzungen=None, custom=False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.rang = rang
        self.machtpunkte = machtpunkte
        self.reichweite = reichweite
        self.dauer = dauer
        self.effekt = effekt
        self.beschreibung = beschreibung
        self.ausgewaehlt = False
        self.aktiv = True
        self.voraussetzungen = voraussetzungen or []
        self.custom = custom

    def __str__(self):
        return f"{self.name} (Rang: {self.rang}, Machtpunkte: {self.machtpunkte}, Reichweite: {self.reichweite}, Dauer: {self.dauer})"

    def auswaehlen(self):
        if not self.ausgewaehlt:
            self.ausgewaehlt = True
            Logger.debug(f"Macht '{self.name}' wurde ausgewählt.")
            return True
        else:
            Logger.warning(f"Macht '{self.name}' ist bereits ausgewählt.")
            return False

    def abwaehlen(self):
        if self.ausgewaehlt:
            self.ausgewaehlt = False
            Logger.debug(f"Macht '{self.name}' wurde abgewählt.")
            return True
        else:
            Logger.warning(f"Macht '{self.name}' ist nicht ausgewählt.")
            return False


    def voraussetzungen_erfuellt(self, charakter):
        """
        Prüft, ob der Charakter die Voraussetzungen für die Macht erfüllt.
        Da wir die Voraussetzungen vorerst ignorieren, geben wir immer True zurück.
        """
        return True  # Vorläufiger Rückgabewert

    def to_dict(self):
        return {
            'name': self.name,
            'rang': self.rang,
            'machtpunkte': self.machtpunkte,
            'reichweite': self.reichweite,
            'dauer': self.dauer,
            'effekt': self.effekt,
            'beschreibung': self.beschreibung,
            'voraussetzungen': self.voraussetzungen,
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv,
            'custom': self.custom
        }

    @classmethod
    def from_dict_static(cls, data):
        macht = cls(
            name=data.get('name', ''),
            rang=data.get('rang', ''),
            machtpunkte=data.get('machtpunkte', 0),
            reichweite=data.get('reichweite', ''),
            dauer=data.get('dauer', ''),
            effekt=data.get('effekt', ''),
            beschreibung=data.get('beschreibung', ''),
            voraussetzungen=data.get('voraussetzungen', []),
            custom=data.get('custom', False)
        )
        macht.ausgewaehlt = data.get('ausgewaehlt', False)
        macht.aktiv = data.get('aktiv', True)
        return macht

    @classmethod
    def from_dict(cls, data):
        """Alias für from_dict_static zur Kompatibilität."""
        return cls.from_dict_static(data)

    @classmethod
    def from_setting_dict(cls, data):
        """Factory method für Setting-Daten (entspricht from_dict_static)."""
        return cls.from_dict_static(data)