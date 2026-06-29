from .wuerfel import Wuerfel


class Attribut:
    def __init__(self, attribut_name, wert=4, modifier=0):
        self.attribut_name = attribut_name
        self.wuerfel = Wuerfel(wert, modifier=modifier, typ='attribut')
        self.aktiv = True
        self.ausgewaehlt = False

    @property
    def wert(self):
        return self.wuerfel.value

    @wert.setter
    def wert(self, value):
        self.wuerfel.value = value

    @property
    def modifier(self):
        return self.wuerfel.modifier

    @modifier.setter
    def modifier(self, value):
        self.wuerfel.modifier = value

    def __str__(self):
        return f"{self.attribut_name}: {self.wuerfel}"

    def to_dict(self):
        return {
            'attribut_name': self.attribut_name,
            'wert': self.wert,
            'modifier': self.modifier,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            attribut_name=data.get('attribut_name', ''),
            wert=data.get('wert', 4),
            modifier=data.get('modifier', 0),
        )

    @classmethod
    def from_dict_static(cls, data):
        return cls.from_dict(data)
