import logging

Logger = logging.getLogger(__name__)


class Talent:
    def __init__(self, name, kategorie, rang, voraussetzungen, beschreibung='',
                 neue_maechte=0, machtpunkte=0, custom=False,
                 auto_handicaps=None, auto_talente=None, auto_maechte=None, effekt=None):
        self.name = name
        self.kategorie = kategorie
        self.rang = rang
        self.voraussetzungen = voraussetzungen
        self.beschreibung = beschreibung
        self.neue_maechte = neue_maechte
        self.machtpunkte = machtpunkte
        self.ausgewaehlt = False
        self.aktiv = True
        self.custom = custom
        self.auto_handicaps = auto_handicaps or []
        self.auto_talente = auto_talente or []
        self.auto_maechte = auto_maechte or []
        self.effekt = effekt or {}
        self.individuelle_beschreibung = None

    def __str__(self):
        return f"{self.name} ({self.kategorie}, Rang: {self.rang})"

    def voraussetzungen_erfuellt(self, charakter):
        from gamelogic.functions.talent_funktionen import pruefe_voraussetzungen
        fehlermeldungen = pruefe_voraussetzungen(charakter, self)
        return len(fehlermeldungen) == 0

    def clone(self):
        return Talent(
            name=self.name,
            kategorie=self.kategorie,
            rang=self.rang,
            voraussetzungen=list(self.voraussetzungen),
            beschreibung=self.beschreibung,
            neue_maechte=self.neue_maechte,
            machtpunkte=self.machtpunkte,
            custom=self.custom,
            auto_handicaps=list(self.auto_handicaps),
            auto_talente=list(self.auto_talente),
            auto_maechte=list(self.auto_maechte),
            effekt=dict(self.effekt) if self.effekt else {},
        )

    def to_dict(self):
        result = {
            'name': self.name,
            'kategorie': self.kategorie,
            'rang': self.rang,
            'voraussetzungen': list(self.voraussetzungen),
            'beschreibung': self.beschreibung,
            'neue_maechte': self.neue_maechte,
            'machtpunkte': self.machtpunkte,
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv,
        }
        if self.auto_handicaps:
            result['auto_handicaps'] = list(self.auto_handicaps)
        if self.auto_talente:
            result['auto_talente'] = list(self.auto_talente)
        if self.auto_maechte:
            result['auto_maechte'] = list(self.auto_maechte)
        if self.effekt:
            result['effekt'] = dict(self.effekt)
        return result

    @classmethod
    def from_dict_static(cls, data):
        talent = cls(
            name=data.get('name', ''),
            kategorie=data.get('kategorie', ''),
            rang=data.get('rang', ''),
            voraussetzungen=data.get('voraussetzungen', []),
            beschreibung=data.get('beschreibung', ''),
            neue_maechte=data.get('neue_maechte', 0),
            machtpunkte=data.get('machtpunkte', 0),
            custom=data.get('custom', False),
            auto_handicaps=data.get('auto_handicaps', []),
            auto_talente=data.get('auto_talente', []),
            auto_maechte=data.get('auto_maechte', []),
            effekt=data.get('effekt', {}),
        )
        talent.ausgewaehlt = data.get('ausgewaehlt', False)
        talent.aktiv = data.get('aktiv', True)
        return talent

    @classmethod
    def from_dict(cls, data):
        return cls.from_dict_static(data)

    @classmethod
    def from_setting_dict(cls, data):
        return cls.from_dict_static(data)
