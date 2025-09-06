# models/fertigkeit.py

from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, NumericProperty
from kivy.event import EventDispatcher
from models.wuerfel import Wuerfel
from kivy.logger import Logger

class Fertigkeit(EventDispatcher): 
    fertigkeit_name = StringProperty("")
    grundfertigkeit = BooleanProperty(False)
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)
    wuerfel = ObjectProperty(None)
    attribut = ObjectProperty(None)
    wert = NumericProperty(0)
    modifier = NumericProperty(0)
    custom = BooleanProperty(False)

    def __init__(self, fertigkeit_name, attribut, grundfertigkeit=False, custom=False, **kwargs):
        super().__init__(**kwargs)
        self.fertigkeit_name = fertigkeit_name
        self.attribut = attribut
        self.grundfertigkeit = grundfertigkeit
        initial_modifier = 0 if grundfertigkeit else -2
        self.wuerfel = Wuerfel(4, modifier=initial_modifier, typ='fertigkeit')
        self.ausgewaehlt = self.grundfertigkeit
        self.aktiv = True
        self.custom = custom

        if self.wuerfel.modifier == -2 and not self.grundfertigkeit:
            self.ausgewaehlt = False

        self.wert = self.wuerfel.value
        self.modifier = self.wuerfel.modifier

        # Binde Änderungen des Wuerfel-Objekts an die Fertigkeit
        self.wuerfel.bind(value=self.on_wuerfel_value_change)
        self.wuerfel.bind(modifier=self.on_wuerfel_modifier_change)

    def on_wuerfel_value_change(self, instance, value):
        self.wert = value

    def on_wuerfel_modifier_change(self, instance, value):
        self.modifier = value

    def __str__(self):
        fertigkeit_type = "Grundfertigkeit" if self.grundfertigkeit else "Nicht-Grundfertigkeit"
        return f"{self.fertigkeit_name}: {self.wuerfel} ({fertigkeit_type})"

    def to_dict(self):
        return {
            'fertigkeit_name': self.fertigkeit_name,
            'grundfertigkeit': self.grundfertigkeit,
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv,
            'wuerfel': self.wuerfel.to_dict(),
            'attribut': self.attribut.attribut_name if self.attribut else None,
            'custom': self.custom
        }

    def from_dict(self, data, attribute_dict, overwrite_wert=True):
        self.fertigkeit_name = data.get('fertigkeit_name', self.fertigkeit_name)
        attribut_name = data.get('attribut', '')
        self.attribut = attribute_dict.get(attribut_name, self.attribut)
        self.grundfertigkeit = data.get('grundfertigkeit', self.grundfertigkeit)
        self.ausgewaehlt = data.get('ausgewaehlt', self.ausgewaehlt)
        self.aktiv = data.get('aktiv', self.aktiv)
        
        if overwrite_wert:
            self.wuerfel.value = data.get('wuerfel', {}).get('value', self.wuerfel.value)
            self.wert = self.wuerfel.value
        
        self.wuerfel.modifier = data.get('wuerfel', {}).get('modifier', self.wuerfel.modifier)
        self.modifier = self.wuerfel.modifier

    @classmethod
    def from_dict_static(cls, data, attribute_dict, overwrite_wert=True):
        if not isinstance(data, dict):
            Logger.error(f"Ungültige Datenstruktur für Fertigkeit: {data}")
            return None

        fertigkeit_name = data.get('fertigkeit_name', '')
        attribut_name = data.get('attribut', '')
        attribut_obj = attribute_dict.get(attribut_name)

        if attribut_obj is None:
            Logger.error(f"Attribut '{attribut_name}' für Fertigkeit '{fertigkeit_name}' nicht gefunden.")
            return None

        fertigkeit = cls(
            fertigkeit_name=fertigkeit_name,
            attribut=attribut_obj,
            grundfertigkeit=data.get('grundfertigkeit', False)
        )
        fertigkeit.ausgewaehlt = data.get('ausgewaehlt', False)
        fertigkeit.aktiv = data.get('aktiv', True)

        if overwrite_wert:
            fertigkeit.wuerfel = Wuerfel.from_dict(data.get('wuerfel', {}))
        else:
            fertigkeit.wuerfel.modifier = data.get('wuerfel', {}).get('modifier', fertigkeit.wuerfel.modifier)
        
        fertigkeit.wert = fertigkeit.wuerfel.value
        fertigkeit.modifier = fertigkeit.wuerfel.modifier

        # Binde Änderungen des Wuerfel-Objekts an die Fertigkeit
        fertigkeit.wuerfel.bind(value=fertigkeit.on_wuerfel_value_change)
        fertigkeit.wuerfel.bind(modifier=fertigkeit.on_wuerfel_modifier_change)

        return fertigkeit


    def to_dict_with_reset_wuerfel(self):
        reset_wuerfel = Wuerfel(4, modifier=0 if self.grundfertigkeit else -2, typ='fertigkeit')
        return {
            'fertigkeit_name': self.fertigkeit_name,
            'grundfertigkeit': self.grundfertigkeit,
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv,
            'wuerfel': reset_wuerfel.to_dict(),
            'attribut': self.attribut.attribut_name if self.attribut else None,
        }

