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
        Logger.debug(f"Rüstung '{self.name}' initialisiert.")

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
        mindeststaerke_wert = self.mindeststärke
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

    def on_angelegt_changed(self, instance, value):
        # Hier können Sie weitere Aktionen durchführen, wenn der Anlege-Status sich ändert
        pass        