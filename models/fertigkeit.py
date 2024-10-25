# models/fertigkeit.py

from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.event import EventDispatcher
from models.wuerfel import Wuerfel

class Fertigkeit(EventDispatcher): 
    """
    Klasse zur Darstellung einer Fertigkeit eines Charakters.
    """

    name = StringProperty("")
    grundfertigkeit = BooleanProperty(False)
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)
    wuerfel = ObjectProperty(None)
    attribut = ObjectProperty(None)

    def __init__(self, name, attribut, grundfertigkeit=False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.attribut = attribut
        self.grundfertigkeit = grundfertigkeit
        # Modifikator ist -2, wenn keine Grundfertigkeit und Wert W4
        initial_modifier = 0 if grundfertigkeit else -2
        self.wuerfel = Wuerfel(4, modifier=initial_modifier, typ='fertigkeit')
        self.ausgewaehlt = self.grundfertigkeit  # Grundfertigkeiten sind standardmäßig ausgewählt
        self.aktiv = True  # Standardmäßig aktiv

        # Wenn Modifikator -2 und keine Grundfertigkeit, dann ausgewaehlt automatisch auf False setzen
        if self.wuerfel.modifier == -2 and not self.grundfertigkeit:
            self.ausgewaehlt = False

    def __str__(self):
        fertigkeit_type = "Grundfertigkeit" if self.grundfertigkeit else "Nicht-Grundfertigkeit"
        return f"{self.name}: {self.wuerfel} ({fertigkeit_type})"

    @property
    def wert(self):
        return self.wuerfel.value

    @property
    def modifier(self):
        return self.wuerfel.modifier
