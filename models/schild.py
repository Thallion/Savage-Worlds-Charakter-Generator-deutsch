# models/schild.py
from kivy.properties import NumericProperty, BooleanProperty, StringProperty, DictProperty
from models.ausruestung import Ausruestung
from kivy.logger import Logger
import logging


class Schild(Ausruestung):
    parade = NumericProperty(0)
    deckung = NumericProperty(0)
    mindeststaerke = StringProperty("")
    ausgewaehlt = BooleanProperty(False)

    def __init__(self, name, gewicht, kosten, setting, parade, deckung, mindeststaerke, beschreibung='', menge=0, ausgewaehlt=False, aktiv=True, kategorie='Schild', **kwargs):
        super().__init__(
            name=name,
            gewicht=gewicht,
            kosten=kosten,
            setting=setting,
            beschreibung=beschreibung,
            menge=menge,
            ausgewaehlt=ausgewaehlt,
            aktiv=aktiv,
            kategorie=kategorie,
            **kwargs
        )
        self.parade = parade
        self.deckung = deckung
        self.mindeststaerke = mindeststaerke
        #Logger.debug(f"Schild '{self.name}' initialisiert.")

    def berechne_gewicht(self):
        if self.angelegt:
            return self.gewicht / 2
        return self.gewicht

    def kann_angelegt_werden(self, charakter):
        mindeststaerke_wert = self.mindeststaerke
        charakter_staerke_wert = charakter.attribute['Stärke'].wert

        # Mapping von Würfelwerten zu numerischen Werten
        staerke_mapping = {'W4': 4, 'W6': 6, 'W8': 8, 'W10': 10, 'W12': 12}

        mindeststaerke_num = staerke_mapping.get(mindeststaerke_wert, 4)

        if charakter_staerke_wert >= mindeststaerke_num:
            return True
        else:
            return False

    def toggle_angelegt(self, charakter=None):
        """
        Schaltet den Anlege-Status des Schilds um, prüft bei Bedarf die Mindeststärke.
        
        Args:
            charakter: Optional - Der Charakter, für den das Schild angelegt werden soll
        """
        if charakter:
            # Mit Charakter: Verwende anlegen/ablegen mit korrekter Prüfung
            if not self.angelegt:
                self.anlegen(charakter)
            else:
                self.ablegen()
        else:
            # Ohne Charakter: Altes Verhalten (direkt umschalten)
            self.angelegt = not self.angelegt
            # Event-Handler trotzdem auslösen
            self.on_angelegt_changed(self, self.angelegt)

    def anlegen(self, charakter):
        """
        Legt das Schild an, unabhängig von der Mindeststärke.
        Gibt nur eine Warnung aus, wenn die Mindeststärke nicht erfüllt ist.
        
        Args:
            charakter: Das Charakterobjekt, dem das Schild angelegt werden soll
        """
        self.angelegt = True
        
        # Nur zur Information prüfen, ob die Mindeststärke erfüllt ist
        if not self.kann_angelegt_werden(charakter):
            Logger.debug(f"Warnung: {self.name} wurde angelegt, obwohl Mindeststärke nicht erfüllt ist.")
        else:
            Logger.debug(f"{self.name} wurde angelegt.")

    def ablegen(self):
        self.angelegt = False
        logging.debug(f"{self.name} wurde abgelegt.")

    def to_dict(self):
        data = super().to_setting_dict()
        data.update({
            'menge': self.menge,
            'parade': self.parade,
            'deckung': self.deckung,
            'mindeststaerke': self.mindeststaerke,
            'angelegt': self.angelegt,
            'ausgewaehlt': self.ausgewaehlt, 
        })
        return data

    def to_setting_dict(self):
        """Speichert die Schild-spezifischen Basisdaten für das Setting."""
        data = super().to_setting_dict()
        data.update({
            'parade': self.parade,
            'deckung': self.deckung,
            'mindeststaerke': self.mindeststaerke,
            # 'angelegt' ist charakter-spezifisch und wird nicht gespeichert
        })
        return data

    @classmethod
    def from_setting_dict(cls, data):
        return cls(
            name=data.get('name', ''),
            gewicht=data.get('gewicht', 0),
            kosten=data.get('kosten', 0),
            setting=data.get('setting', ''),
            parade=data.get('parade', 0),
            deckung=data.get('deckung', 0),
            mindeststaerke=data.get('mindeststaerke', 'W4'),
            beschreibung=data.get('beschreibung', ''),
            kategorie=data.get('kategorie', 'Schild'),
            # Charakterbezogene Daten werden nicht geladen
        )

    @classmethod
    def from_dict_static(cls, data):
        return cls(
            name=data.get('name', ''),
            gewicht=data.get('gewicht', 0),
            kosten=data.get('kosten', 0),
            setting=data.get('setting', ''),
            parade=data.get('parade', 0),
            deckung=data.get('deckung', 0),
            mindeststaerke=data.get('mindeststaerke', 'W4'),
            beschreibung=data.get('beschreibung', ''),
            kategorie=data.get('kategorie', 'Schild'),
            menge=data.get('menge', 0),
            ausgewaehlt=data.get('ausgewaehlt', False),
            aktiv=data.get('aktiv', True),
            angelegt=data.get('angelegt', False)
        )