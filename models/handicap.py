import unittest, json
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.event import EventDispatcher
from kivy.logger import Logger, LOG_LEVELS

class Handicap(EventDispatcher):
    name = StringProperty("")
    stufe = StringProperty("")
    punkte = NumericProperty(0)
    beschreibung = StringProperty("")
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)
    custom = BooleanProperty(False)
    auto_applied = BooleanProperty(False)

    def __init__(self, name, stufe, beschreibung='', custom=False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.stufe = stufe.lower()
        self.beschreibung = beschreibung if beschreibung else "Keine Beschreibung verfügbar."
        self.ausgewaehlt = False
        self.aktiv = True
        self.custom = custom
        self.auto_applied = False
        self.individuelle_beschreibung = None
        self.update_punkte()

    def update_punkte(self):
        self.punkte = 1 if self.stufe == 'leicht' else 2

    def on_stufe(self, instance, value):
        self.update_punkte()

    def __str__(self):
        return f"{self.name} (Stufe: {self.stufe})"

    def auswaehlen(self):
        self.ausgewaehlt = True
        Logger.debug(f"Handicap '{self.name}' ausgewählt.")

    def abwaehlen(self):
        self.ausgewaehlt = False
        Logger.debug(f"Handicap '{self.name}' abgewählt.")

    def setze_beschreibung(self, beschreibung):
        self.beschreibung = beschreibung

    def clone(self):
        """
        Erstellt eine Kopie dieses Handicaps.
        
        Returns:
            Handicap: Eine neue Instanz mit den gleichen Werten
        """
        h = Handicap(
            name=self.name,
            stufe=self.stufe,
            beschreibung=self.beschreibung,
            custom=self.custom
        )
        h.auto_applied = self.auto_applied
        return h

    def to_dict(self):
        result = {
            'name': self.name,
            'stufe': self.stufe,
            'punkte': self.punkte,
            'beschreibung': self.beschreibung,
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv,
            'custom': self.custom
        }
        if self.auto_applied:
            result['auto_applied'] = True
        return result

    @classmethod
    def from_dict_static(cls, data):
        handicap = cls(
            name=data.get('name', ''),
            stufe=data.get('stufe', ''),
            beschreibung=data.get('beschreibung', '')
        )
        handicap.punkte = data.get('punkte', handicap.punkte)
        handicap.ausgewaehlt = data.get('ausgewaehlt', False)
        handicap.aktiv = data.get('aktiv', True)
        handicap.auto_applied = data.get('auto_applied', False)
        return handicap

    @classmethod
    def from_dict(cls, data):
        """Alias für from_dict_static zur Kompatibilität."""
        return cls.from_dict_static(data)

    @classmethod
    def from_setting_dict(cls, data):
        """Factory method für Setting-Daten (entspricht from_dict_static)."""
        return cls.from_dict_static(data)

    def to_setting_dict(self):
        """Speichert die Handicap-spezifischen Basisdaten für das Setting."""
        data = super().to_setting_dict()
        data.update({
            'name': self.name,
            'stufe': self.stufe,
            'punkte': self.punkte,
            'beschreibung': self.beschreibung,
            'aktiv': self.aktiv,
            'custom': self.custom
        })
        return data           

    @staticmethod
    def parse_handicap_string(handicap_str):
        parts = handicap_str.split('(')
        name = parts[0].strip()
        stufe = parts[1].strip(')').strip() if len(parts) > 1 else ''
        return name, stufe

    @classmethod
    def from_string(cls, handicap_str):
        try:
            name, stufe = cls.parse_handicap_string(handicap_str)
            if not name:
                raise ValueError("Handicap-Name fehlt.")
            return cls(name=name, stufe=stufe)
        except Exception as e:
            Logger.error(f"Fehler beim Parsen des Handicap-Strings '{handicap_str}': {e}")
            return None  # Oder eine Standardinstanz
        

    # In der Handicap-Klasse hinzufügen:
    def update_from_dict(self, data):
        # Aktualisiert ein bestehendes Handicap-Objekt mit den Werten aus data
        self.name = data.get('name', self.name)
        self.stufe = data.get('stufe', self.stufe)
        self.punkte = data.get('punkte', self.punkte)
        self.beschreibung = data.get('beschreibung', self.beschreibung)
        self.ausgewaehlt = data.get('ausgewaehlt', self.ausgewaehlt)
        self.aktiv = data.get('aktiv', self.aktiv)
        self.custom = data.get('custom', self.custom)
        self.update_punkte()


