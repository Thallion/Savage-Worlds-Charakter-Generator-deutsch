import logging

Logger = logging.getLogger(__name__)


class Wuerfel:
    VALID_VALUES = [4, 6, 8, 10, 12]
    STUFEN = {4: 1, 6: 2, 8: 3, 10: 4, 12: 5}

    def __init__(self, value=4, modifier=0, typ="attribut"):
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
        if self.value == 12 and self.modifier >= 2:
            self.modifier += 1
            Logger.warning(f"Maximaler Würfelwert (W12+2) überschritten. Neuer Wert: W{self.value}+{self.modifier}")
            return True
        elif self.value == 12 and self.modifier < 2:
            self.modifier += 1
            return True
        elif self.value == 4 and self.modifier == -2:
            self.modifier += 2
            return True
        elif self.value < 12:
            next_value = self.value + 2
            if next_value in self.VALID_VALUES:
                self.value = next_value
                return True

        Logger.warning(f"Unerwarteter Fall beim Steigern des Würfels: {self}")
        return True

    def decrease(self):
        if self.value == 12 and self.modifier > 0:
            self.modifier -= 1
            return True
        elif self.value > 4:
            previous_value = self.value - 2
            if previous_value in self.VALID_VALUES:
                self.value = previous_value
                return True
        elif self.value == 4:
            if self.typ == "fertigkeit" and self.modifier > -2:
                self.modifier -= 2
                return True
            else:
                Logger.warning(f"Der Würfel kann nicht weiter gesenkt werden: {self}")
                return False
        else:
            Logger.warning(f"Der Würfel kann nicht weiter gesenkt werden: {self}")
            return False

    def to_dict(self):
        return {
            'value': self.value,
            'modifier': self.modifier,
            'typ': self.typ,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            value=data.get('value', 4),
            modifier=data.get('modifier', 0),
            typ=data.get('typ', 'attribut'),
        )
