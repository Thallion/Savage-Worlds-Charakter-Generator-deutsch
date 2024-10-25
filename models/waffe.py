# models/waffe.py
from kivy.properties import StringProperty, BooleanProperty, DictProperty
from models.ausruestung import Ausruestung
from kivy.logger import Logger, LOG_LEVELS
import logging

# Setze Kivy Logger-Level auf DEBUG
Logger.setLevel(LOG_LEVELS['debug'])
Logger.info("Kivy Logger auf DEBUG-Level gesetzt.")

class Waffe(Ausruestung):
    typ = StringProperty("")  # 'Nahkampf' oder 'Fernkampf'
    mindeststaerke = StringProperty("")
    angelegt = BooleanProperty(False)
    eigenschaften = DictProperty({})  # Um Eigenschaften zu speichern

    def __init__(self, name, gewicht, kosten, setting, typ, mindeststaerke='W4', beschreibung='', eigenschaften=None, **kwargs):
        super().__init__(
            name=name,
            gewicht=gewicht,
            kosten=kosten,
            setting=setting,
            beschreibung=beschreibung,
            **kwargs  # 'kategorie' wird über kwargs übergeben
        )
        self.typ = typ
        self.mindeststaerke = mindeststaerke
        self.angelegt = False
        self.eigenschaften = eigenschaften or {}
        self.bind(angelegt=self.on_angelegt_changed)
        Logger.debug(f"Waffe '{self.name}' initialisiert mit Typ: {self.typ}, Mindeststärke: {self.mindeststaerke}.")
    
    def berechne_gewicht(self):
        if self.angelegt:
            return self.gewicht / 2
        return self.gewicht
    
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

    def anlegen(self, charakter):
        if self.kann_angelegt_werden(charakter):
            self.angelegt = True
            logging.debug(f"{self.name} wurde angelegt.")
        else:
            logging.warning(f"{self.name} kann nicht angelegt werden, Mindeststärke nicht erfüllt.")

    def ablegen(self):
        self.angelegt = False
        logging.debug(f"{self.name} wurde abgelegt.")

    def toggle_angelegt(self):
        self.angelegt = not self.angelegt

    def on_angelegt_changed(self, instance, value):
        # Hier können Sie weitere Aktionen durchführen, wenn der Anlege-Status sich ändert
        pass        