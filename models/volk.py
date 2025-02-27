import unittest, json
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.event import EventDispatcher
from kivy.logger import Logger, LOG_LEVELS

class Volk(EventDispatcher):
    name = StringProperty("")
    handicaps = ListProperty([])
    talente = ListProperty([])
    besonderheiten = ListProperty([])
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)
    custom = BooleanProperty(False)

    def __init__(self, name, handicaps=None, talente=None, besonderheiten=None, custom=False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.handicaps = handicaps or []
        self.talente = talente or []
        self.besonderheiten = besonderheiten or []
        self.ausgewaehlt = False
        self.aktiv = True
        self.custom = custom

    def __str__(self):
        return f"{self.name} (Handicaps: {', '.join(self.handicaps)}, Talente: {', '.join(self.talente)}, Besonderheiten: {', '.join(self.besonderheiten)})"

    def auswaehlen(self):
        if not self.ausgewaehlt:
            self.ausgewaehlt = True
            Logger.debug(f"Volk '{self.name}' wurde ausgewählt.")
            return True
        else:
            Logger.warning(f"Volk '{self.name}' ist bereits ausgewählt.")
            return False

    def abwaehlen(self):
        if self.ausgewaehlt:
            self.ausgewaehlt = False
            Logger.debug(f"Volk '{self.name}' wurde abgewählt.")
            return True
        else:
            Logger.warning(f"Volk '{self.name}' ist nicht ausgewählt.")
            return False

    def to_dict(self):
        return {
            'name': self.name,
            'handicaps': self.handicaps,
            'talente': self.talente,
            'besonderheiten': self.besonderheiten,
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv,
            'custom': self.custom
        }

    def to_setting_dict(self):
        return {
            'name': self.name,
            'handicaps': self.handicaps,
            'talente': self.talente,
            'besonderheiten': self.besonderheiten,
            'aktiv': self.aktiv,
            'custom': self.custom
        }

    @classmethod
    def from_dict(cls, data):
        volk = cls(
            name=data.get('name', ''),
            handicaps=data.get('handicaps', []),
            talente=data.get('talente', []),
            besonderheiten=data.get('besonderheiten', []),
            custom=data.get('custom', False)
        )
        volk.ausgewaehlt = data.get('ausgewaehlt', False)
        volk.aktiv = data.get('aktiv', True)
        return volk


