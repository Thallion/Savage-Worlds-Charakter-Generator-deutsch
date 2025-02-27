# models/ruestung.py
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from models.ausruestung import Ausruestung
from kivy.logger import Logger, LOG_LEVELS
import logging

# Setze Kivy Logger-Level auf DEBUG
Logger.setLevel(LOG_LEVELS['debug'])
Logger.info("Kivy Logger auf DEBUG-Level gesetzt.")

class Ruestung(Ausruestung):
    torso = NumericProperty(0)
    arme = NumericProperty(0)
    beine = NumericProperty(0)
    kopf = NumericProperty(0)
    mindeststaerke = StringProperty("")
    angelegt = BooleanProperty(False)
    ausgewaehlt = BooleanProperty(False)

    def __init__(self, name, torso, arme, beine, kopf, mindeststaerke, setting, gewicht, kosten, beschreibung='', menge=0, ausgewaehlt=False, aktiv=True, kategorie='Rüstung', **kwargs):
        super().__init__(
            name=name,
            gewicht=gewicht,
            kosten=kosten,
            setting=setting,
            beschreibung=beschreibung,
            menge=menge,
            mindeststaerke = mindeststaerke,
            ausgewaehlt=ausgewaehlt,
            aktiv=aktiv,
            kategorie=kategorie,
            **kwargs
        )
        self.torso = torso
        self.arme = arme
        self.beine = beine
        self.kopf = kopf
        self.angelegt = False
        self.bind(angelegt=self.on_angelegt_changed)
        self.mindeststaerke = mindeststaerke
        #Logger.debug(f"Rüstung '{self.name}' initialisiert.")

    def berechne_gewicht(self):
        effektives_gewicht = self.gewicht
        if self.angelegt:
            effektives_gewicht /= 2  # Gewicht wird halbiert
        return effektives_gewicht

    def anlegen(self, charakter):
        if self.kann_angelegt_werden(charakter):
            self.angelegt = True
            logging.debug(f"{self.name} wurde angelegt.")
        else:
            logging.warning(f"{self.name} kann nicht angelegt werden, Mindeststärke nicht erfüllt.")

    def ablegen(self):
        self.angelegt = False
        logging.debug(f"{self.name} wurde abgelegt.")

    def kann_angelegt_werden(self, charakter):
        mindeststaerke_wert = self.mindeststaerke
        charakter_staerke_wert = charakter.attribute['Stärke'].wert

        # Mapping von Würfelwerten zu numerischen Werten
        staerke_mapping = {'W4': 4, 'W6': 6, 'W8': 8, 'W10': 10, 'W12': 12, '-': 0}

        mindeststaerke_num = staerke_mapping.get(mindeststaerke_wert, 4)

        if charakter_staerke_wert >= mindeststaerke_num:
            return True
        else:
            return False

    def toggle_angelegt(self):
        self.angelegt = not self.angelegt
        logging.debug(f"Rüstung '{self.name}' angelegt: {self.angelegt}")


    def on_angelegt_changed(self, instance, value):
        # Hier können Sie weitere Aktionen durchführen, wenn der Anlege-Status sich ändert
        pass        

    def convert_staerke_to_num(self, staerke_wert):
        staerke_mapping = {'W4': 4, 'W6': 6, 'W8': 8, 'W10': 10, 'W12': 12, '-': 0}
        return staerke_mapping.get(staerke_wert, 0)    
    
    @classmethod
    def from_dict_static(cls, data):
        return cls(
            name=data.get('name', ''),
            torso=data.get('torso', 0),
            arme=data.get('arme', 0),
            beine=data.get('beine', 0),
            kopf=data.get('kopf', 0),
            mindeststaerke=data.get('mindeststaerke', 'W4'),
            setting=data.get('setting', ''),
            gewicht=data.get('gewicht', 0),
            kosten=data.get('kosten', 0),
            beschreibung=data.get('beschreibung', ''),
            menge=data.get('menge', 0),
            ausgewaehlt=data.get('ausgewaehlt', False),
            aktiv=data.get('aktiv', True),
            angelegt=data.get('angelegt', False),
            kategorie=data.get('kategorie', 'Rüstung')
        )

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'torso': self.torso,
            'arme': self.arme,
            'beine': self.beine,
            'kopf': self.kopf,
            'mindeststaerke': self.mindeststaerke,
            'angelegt': self.angelegt
        })
        return data  

    def to_setting_dict(self):
        """Speichert die Rüstung-spezifischen Basisdaten für das Setting."""
        data = super().to_setting_dict()
        data.update({
            'torso': self.torso,
            'arme': self.arme,
            'beine': self.beine,
            'kopf': self.kopf,
            'mindeststaerke': self.mindeststaerke,
            # 'angelegt' ist charakter-spezifisch und wird nicht gespeichert
        })
        return data  

    @classmethod
    def from_setting_dict(cls, data):
        return cls(
            name=data.get('name', ''),
            torso=data.get('torso', 0),
            arme=data.get('arme', 0),
            beine=data.get('beine', 0),
            kopf=data.get('kopf', 0),
            mindeststaerke=data.get('mindeststaerke', 'W4'),
            setting=data.get('setting', ''),
            gewicht=data.get('gewicht', 0),
            kosten=data.get('kosten', 0),
            beschreibung=data.get('beschreibung', ''),
            kategorie=data.get('kategorie', 'Rüstung'),
            # Charakterbezogene Daten werden nicht geladen
        )
