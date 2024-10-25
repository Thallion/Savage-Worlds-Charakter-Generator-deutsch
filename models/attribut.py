# models/attribut.py

from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.event import EventDispatcher
from models.wuerfel import Wuerfel

class Attribut(EventDispatcher):
    """
    Klasse zur Darstellung eines einzelnen Attributs eines Charakters.
    """

    name = StringProperty("")
    wuerfel = ObjectProperty(None)
    ausgewaehlt = BooleanProperty(True)
    aktiv = BooleanProperty(True)

    def __init__(self, name, wert=4, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.wuerfel = Wuerfel(wert)
        self.ausgewaehlt = True  # Standardmäßig ausgewählt
        self.aktiv = True  # Standardmäßig aktiv

    def __str__(self):
        return f"{self.name}: {self.wuerfel}"

    @property
    def wert(self):
        return self.wuerfel.value

    @property
    def modifier(self):
        return self.wuerfel.modifier
