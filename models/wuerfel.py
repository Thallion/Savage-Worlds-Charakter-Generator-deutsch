from kivy.properties import NumericProperty, StringProperty
from kivy.event import EventDispatcher
from kivy.logger import Logger, LOG_LEVELS

class Wuerfel(EventDispatcher):
    """
    Klasse zur Darstellung eines Würfelwerts mit Modifikatoren und Stufen.
    """

    value = NumericProperty(4)
    modifier = NumericProperty(0)
    typ = StringProperty("attribut")  # Standardwert

    VALID_VALUES = [4, 6, 8, 10, 12]
    STUFEN = {4: 1, 6: 2, 8: 3, 10: 4, 12: 5}

    def __init__(self, value=4, modifier=0, typ="attribut", **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_change')  # Registrierung des Events
        if value not in self.VALID_VALUES:
            raise ValueError(f"Ungültiger Würfelwert: {value}. Erwartet: {self.VALID_VALUES}")
        if not isinstance(modifier, int):
            raise TypeError(f"Modifikator muss eine Ganzzahl sein, erhalten: {type(modifier)}")
        self.value = value
        self.modifier = modifier
        self.typ = typ

    def __str__(self):
        if self.modifier > 0:
            return f"W{self.value}+{self.modifier}"
        elif self.modifier < 0:
            return f"W{self.value}{self.modifier}"
        else:
            return f"W{self.value}"

    @property
    def stufe(self):
        base_stufe = self.STUFEN.get(self.value, 0)
        additional = self.modifier if self.value == 12 else 0
        return base_stufe + additional

    @property
    def total_value(self):
        return self.value + self.modifier if self.value == 12 else self.value

    def increase(self):
        if self.value == 12 and self.modifier < 2:
            self.modifier += 1
            #Logger.debug(f"Würfel erhöht: {self}")
            self.dispatch('on_change')
            return True
        elif self.value == 4 and self.modifier == -2:
            self.modifier += 2
            #Logger.debug(f"Würfel erhöht: {self}")
            self.dispatch('on_change')
            return True
        elif self.value < 12:
            next_value = self.value + 2
            if next_value in self.VALID_VALUES:
                self.value = next_value
                #Logger.debug(f"Würfel erhöht: {self}")
                self.dispatch('on_change')
                return True
        Logger.warning(f"Der Würfel kann nicht weiter gesteigert werden: {self}")
        return False

    def decrease(self):
        if self.value == 12 and self.modifier > 0:
            self.modifier -= 1
            #Logger.debug(f"Würfel gesenkt: {self}")
            self.dispatch('on_change')
            return True
        elif self.value > 4:
            previous_value = self.value - 2
            if previous_value in self.VALID_VALUES:
                self.value = previous_value
                #Logger.debug(f"Würfel gesenkt: {self}")
                self.dispatch('on_change')
                return True
        elif self.value == 4:
            if self.typ == "fertigkeit" and self.modifier > -2:
                self.modifier -= 2
                #Logger.debug(f"Würfel gesenkt: {self}")
                self.dispatch('on_change')
                return True
            else:
                Logger.warning(f"Der Würfel kann nicht weiter gesenkt werden: {self}")
                return False
        else:
            Logger.warning(f"Der Würfel kann nicht weiter gesenkt werden: {self}")
            return False

    def on_change(self, *args):
        pass

    def to_dict(self):
        return {
            'value': self.value,
            'modifier': self.modifier,
            'typ': self.typ
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            value=data.get('value', 0),
            modifier=data.get('modifier', 0),
            typ=data.get('typ', '')
        )