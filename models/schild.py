# models/schild.py
from kivy.properties import NumericProperty, BooleanProperty, StringProperty, DictProperty
from models.ausruestung import Ausruestung
from kivy.logger import Logger, LOG_LEVELS
import logging

# Setze Kivy Logger-Level auf DEBUG
Logger.setLevel(LOG_LEVELS['debug'])
Logger.info("Kivy Logger auf DEBUG-Level gesetzt.")


class Schild(Ausruestung):
    parade = NumericProperty(0)
    deckung = NumericProperty(0)
    mindeststaerke = StringProperty("")

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
        Logger.debug(f"Schild '{self.name}' initialisiert.")



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

    def anlegen(self, charakter):
        if self.kann_angelegt_werden(charakter):
            self.angelegt = True
            logging.debug(f"{self.name} wurde angelegt.")
        else:
            logging.warning(f"{self.name} kann nicht angelegt werden, Mindeststärke nicht erfüllt.")

    def ablegen(self):
        self.angelegt = False
        logging.debug(f"{self.name} wurde abgelegt.")
