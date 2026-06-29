import logging

Logger = logging.getLogger(__name__)


class Macht:
    def __init__(self, name, rang, machtpunkte, reichweite, dauer,
                 effekt='', beschreibung='', voraussetzungen=None, custom=False):
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
        self.individuelle_beschreibung = None

    def __str__(self):
        return f"{self.name} (Rang: {self.rang}, Machtpunkte: {self.machtpunkte})"

    def auswaehlen(self):
        if not self.ausgewaehlt:
            self.ausgewaehlt = True
            return True
        return False

    def abwaehlen(self):
        if self.ausgewaehlt:
            self.ausgewaehlt = False
            return True
        return False

    def to_dict(self):
        return {
            'name': self.name,
            'rang': self.rang,
            'machtpunkte': self.machtpunkte,
            'reichweite': self.reichweite,
            'dauer': self.dauer,
            'effekt': self.effekt,
            'beschreibung': self.beschreibung,
            'voraussetzungen': list(self.voraussetzungen),
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv,
            'custom': self.custom,
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
            custom=data.get('custom', False),
        )
        macht.ausgewaehlt = data.get('ausgewaehlt', False)
        macht.aktiv = data.get('aktiv', True)
        return macht

    @classmethod
    def from_dict(cls, data):
        return cls.from_dict_static(data)

    @classmethod
    def from_setting_dict(cls, data):
        return cls.from_dict_static(data)
