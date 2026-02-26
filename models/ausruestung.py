from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, DictProperty, ListProperty
from kivy.event import EventDispatcher
from kivy.logger import Logger, LOG_LEVELS
import logging

# Setze Kivy Logger-Level auf DEBUG
Logger.setLevel(LOG_LEVELS['debug'])
Logger.info("Kivy Logger auf DEBUG-Level gesetzt.")

class Ausruestung(EventDispatcher):
    name = StringProperty("")
    kategorie = StringProperty("")  # Kategorie als Property definieren
    gewicht = NumericProperty(0)
    kosten = NumericProperty(0)
    setting = StringProperty("")
    beschreibung = StringProperty("")
    menge = NumericProperty(0)
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)
    angelegt = BooleanProperty(False)
    custom = BooleanProperty(False)

    # Cyberware-spezifische Felder (nur für kategorie == "Cyberware" relevant)
    stress = NumericProperty(0)
    max_installationen = NumericProperty(-1)
    unterkategorie = StringProperty("")
    effekte = DictProperty({})

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.kategorie = kwargs.get('kategorie', 'Allgemein')
        self.gewicht = kwargs.get('gewicht', 0)
        self.kosten = kwargs.get('kosten', 0)
        self.setting = kwargs.get('setting', '')
        self.beschreibung = kwargs.get('beschreibung', '')
        self.menge = kwargs.get('menge', 0)
        self.ausgewaehlt = kwargs.get('ausgewaehlt', False)
        self.aktiv = kwargs.get('aktiv', True)
        self.angelegt = kwargs.get('angelegt', False)
        self.custom = kwargs.get('custom', False)
        # Cyberware-Felder
        self.stress = kwargs.get('stress', 0)
        self.max_installationen = kwargs.get('max_installationen', -1)
        self.unterkategorie = kwargs.get('unterkategorie', '')
        self.effekte = kwargs.get('effekte', {})

    def __str__(self):
        return f"{self.name} (Setting: {self.setting}, Kosten: {self.kosten}, Gewicht: {self.gewicht}, Menge: {self.menge})"

    def erhoehe_menge(self, anzahl=1):
        self.menge += anzahl
        if self.menge > 0:
            self.ausgewaehlt = True
        logging.debug(f"Menge von '{self.name}' erhöht auf {self.menge}.")

    def verringere_menge(self, anzahl=1):
        self.menge = max(0, self.menge - anzahl)
        if self.menge == 0:
            self.ausgewaehlt = False
        logging.debug(f"Menge von '{self.name}' verringert auf {self.menge}.")

    def setze_beschreibung(self, beschreibung):
        self.beschreibung = beschreibung

    def toggle_angelegt(self):
        self.angelegt = not self.angelegt

    @classmethod
    def from_dict_static(cls, data):
        return cls(
            name=data.get('name', ''),
            kategorie=data.get('kategorie', 'Allgemein'),
            gewicht=data.get('gewicht', 0),
            kosten=data.get('kosten', 0),
            setting=data.get('setting', ''),
            beschreibung=data.get('beschreibung', ''),
            menge=data.get('menge', 0),
            ausgewaehlt=data.get('ausgewaehlt', False),
            aktiv=data.get('aktiv', True),
            stress=data.get('stress', 0),
            max_installationen=data.get('max_installationen', -1),
            unterkategorie=data.get('unterkategorie', ''),
            effekte=data.get('effekte', {}),
        )

    @classmethod
    def from_character_dict(cls, data, base_item):
        instance = cls(
            name=base_item.name,
            kategorie=base_item.kategorie,
            gewicht=base_item.gewicht,
            kosten=base_item.kosten,           
            setting=base_item.setting,
            beschreibung=base_item.beschreibung,
            aktiv=base_item.aktiv,
        )
        instance.menge = data.get('menge', 0)
        instance.ausgewaehlt = data.get('ausgewaehlt', False)
        instance.angelegt = data.get('angelegt', False)
        return instance

    def to_setting_dict(self):
        # Speichern der Basisdaten für das Setting
        return {
            'name': self.name,
            'kategorie': self.kategorie,
            'gewicht': self.gewicht,
            'kosten': self.kosten,
            'setting': self.setting,
            'beschreibung': self.beschreibung,
            'aktiv': self.aktiv,
            # Charakterbezogene Daten werden nicht gespeichert
        }

    def to_dict(self):
        return {
            'name': self.name,
            'kategorie': self.kategorie,
            'gewicht': self.gewicht,
            'kosten': self.kosten,
            'setting': self.setting,
            'beschreibung': self.beschreibung,
            'menge': self.menge,
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv,
            'angelegt': self.angelegt
        }

    @classmethod
    def from_setting_dict(cls, data):
        try:
            gewicht = data.get('gewicht')
            if gewicht is None:
                Logger.warning(f"Gewicht für '{data.get('name', 'Unbekannt')}' ist None. Setze auf 0.")
                gewicht = 0
            kosten = data.get('kosten')
            if kosten is None:
                Logger.warning(f"Kosten für '{data.get('name', 'Unbekannt')}' sind None. Setze auf 0.")
                kosten = 0

            return cls(
                name=data.get('name', ''),
                kategorie=data.get('kategorie', 'Allgemein'),
                gewicht=gewicht,
                kosten=kosten,
                setting=data.get('setting', ''),
                beschreibung=data.get('beschreibung', ''),
                stress=data.get('stress', 0),
                max_installationen=data.get('max_installationen', -1),
                unterkategorie=data.get('unterkategorie', ''),
                effekte=data.get('effekte', {}),
            )
        except Exception as e:
            Logger.error(f"Fehler beim Erstellen von Ausruestung '{data.get('name', 'Unbekannt')}' aus Daten: {e}")
            return None
   
