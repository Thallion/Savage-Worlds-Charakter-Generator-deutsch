# models/attribut.py

from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.event import EventDispatcher
from models.wuerfel import Wuerfel
import logging

class Attribut(EventDispatcher):
    attribut_name = StringProperty("")
    wert = NumericProperty(0)
    modifier = NumericProperty(0)
    wuerfel = ObjectProperty(None)
    aktiv = BooleanProperty(True)
    ausgewaehlt = BooleanProperty(False)

    def __init__(self, attribut_name, wert=4, modifier=0, **kwargs):
        super().__init__(**kwargs)
        self.attribut_name = attribut_name
        self.wuerfel = Wuerfel(wert, modifier=modifier, typ='attribut')
        self.wert = self.wuerfel.value
        self.modifier = self.wuerfel.modifier

        # Binde Änderungen des Wuerfel-Objekts an das Attribut
        self.wuerfel.bind(value=self.on_wuerfel_value_change)
        self.wuerfel.bind(modifier=self.on_wuerfel_modifier_change)

    def on_wuerfel_value_change(self, instance, value):
        self.wert = value

    def on_wuerfel_modifier_change(self, instance, value):
        self.modifier = value

    def __str__(self):
        return f"{self.attribut_name}: W{self.wert}+{self.modifier}"

    def to_dict(self):
        return {
            'attribut_name': self.attribut_name,
            'wert': self.wert,
            'modifier': self.modifier
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            attribut_name=data.get('attribut_name', ''),
            wert=data.get('wert', 0),
            modifier=data.get('modifier', 0)
        )

    @classmethod
    def from_dict_static(cls, data):
        attribut_name = data['attribut_name']
        wert = data['wert']
        modifier = data['modifier']
        attribut = cls(
            attribut_name=attribut_name,
            wert=wert,
            modifier=modifier
        )
        return attribut