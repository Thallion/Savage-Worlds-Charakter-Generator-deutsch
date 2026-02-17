import logging, unittest, json
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.event import EventDispatcher

class Talent(EventDispatcher):
    name = StringProperty("")
    kategorie = StringProperty("")
    rang = StringProperty("")
    voraussetzungen = ListProperty([])
    beschreibung = StringProperty("")
    neue_maechte = NumericProperty(0)
    machtpunkte = NumericProperty(0)
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)
    custom = BooleanProperty(False)  # Neue Eigenschaft
    auto_handicaps = ListProperty([])
    auto_talente = ListProperty([])

    def __init__(self, name, kategorie, rang, voraussetzungen, beschreibung='', neue_maechte=0, machtpunkte=0, custom=False, auto_handicaps=None, auto_talente=None, **kwargs):
        super().__init__(**kwargs)
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
        self.individuelle_beschreibung = None

    def __str__(self):
        return f"{self.name} ({self.kategorie}, Rang: {self.rang})"

    def auswaehlen(self, charakter):
        if not self.ausgewaehlt:
            if self.voraussetzungen_erfuellt(charakter):
                self.ausgewaehlt = True
                # Erhöhe verfügbare Mächte und Machtpunkte, falls das Talent dies gewährt
                # charakter.verfuegbare_maechte += self.neue_maechte
                # charakter.erhoehe_machtpunkte(self.machtpunkte)
                logging.debug(f"Talent '{self.name}' ausgewählt. Verfügbare Mächte: {charakter.verfuegbare_maechte}, Machtpunkte: {charakter.machtpunkte}")
            else:
                logging.warning(f"Voraussetzungen für Talent '{self.name}' nicht erfüllt.")
        else:
            logging.warning(f"Talent '{self.name}' ist bereits ausgewählt.")

    def abwaehlen(self, charakter):
        if self.ausgewaehlt:
            self.ausgewaehlt = False
            # Verringere verfügbare Mächte und Machtpunkte, falls das Talent dies gewährt
            # charakter.verfuegbare_maechte -= self.neue_maechte
            # charakter.senke_machtpunkte(self.machtpunkte)
            logging.debug(f"Talent '{self.name}' abgewählt. Verfügbare Mächte: {charakter.verfuegbare_maechte}, Machtpunkte: {charakter.machtpunkte}")
        else:
            logging.warning(f"Talent '{self.name}' ist nicht ausgewählt.")

    def voraussetzungen_erfuellt(self, charakter):
        """
        Prüft, ob der Charakter die Voraussetzungen für das Talent erfüllt.
        
        Args:
            charakter: Das Charakter-Objekt
            
        Returns:
            bool: True wenn alle Voraussetzungen erfüllt sind, sonst False
        """
        from functions.talent_funktionen import pruefe_voraussetzungen
        fehlermeldungen = pruefe_voraussetzungen(charakter, self)
        return len(fehlermeldungen) == 0
    
    def clone(self):
        """
        Erstellt eine Kopie dieses Talents.
        
        Returns:
            Talent: Eine neue Instanz mit den gleichen Werten
        """
        return Talent(
            name=self.name,
            kategorie=self.kategorie,
            rang=self.rang,
            voraussetzungen=list(self.voraussetzungen),  # Kopie der Liste
            beschreibung=self.beschreibung,
            neue_maechte=self.neue_maechte,
            machtpunkte=self.machtpunkte,
            custom=self.custom,
            auto_handicaps=list(self.auto_handicaps),
            auto_talente=list(self.auto_talente)
        )

    def setze_beschreibung(self, beschreibung):
        self.beschreibung = beschreibung

    def to_dict(self):
        result = {
            'name': self.name,
            'kategorie': self.kategorie,
            'rang': self.rang,
            'voraussetzungen': self.voraussetzungen,
            'beschreibung': self.beschreibung,
            'neue_maechte': self.neue_maechte,
            'machtpunkte': self.machtpunkte,
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv
        }
        if self.auto_handicaps:
            result['auto_handicaps'] = list(self.auto_handicaps)
        if self.auto_talente:
            result['auto_talente'] = list(self.auto_talente)
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
            auto_talente=data.get('auto_talente', [])
        )
        talent.ausgewaehlt = data.get('ausgewaehlt', False)
        talent.aktiv = data.get('aktiv', True)
        return talent

    @classmethod
    def from_dict(cls, data):
        """Alias für from_dict_static zur Kompatibilität."""
        return cls.from_dict_static(data)

    @classmethod
    def from_setting_dict(cls, data):
        """Factory method für Setting-Daten (entspricht from_dict_static)."""
        return cls.from_dict_static(data)