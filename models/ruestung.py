# models/ruestung.py
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from models.ausruestung import Ausruestung
from kivy.logger import Logger
import logging

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
        """
        Legt die Rüstung an, unabhängig von der Mindeststärke.
        Gibt nur eine Warnung aus, wenn die Mindeststärke nicht erfüllt ist.
        
        Args:
            charakter: Das Charakterobjekt, dem die Rüstung angelegt werden soll
        """
        self.angelegt = True
        
        # Nur zur Information prüfen, ob die Mindeststärke erfüllt ist
        if not self.kann_angelegt_werden(charakter):
            Logger.warning(f"{self.name} wurde angelegt, obwohl Mindeststärke nicht erfüllt ist.")
        else:
            Logger.debug(f"{self.name} wurde angelegt.")

    def ablegen(self):
        self.angelegt = False
        logging.debug(f"{self.name} wurde abgelegt.")

    def kann_angelegt_werden(self, charakter):
        """
        Prüft, ob der Charakter die Mindeststärke für die Rüstung erfüllt.
        Berücksichtigt das Talent "Kräftig".
        
        Args:
            charakter: Das Charakter-Objekt
            
        Returns:
            bool: True wenn die Mindeststärke erfüllt ist, sonst False
        """
        mindeststaerke_wert = self.mindeststaerke
        
        # Effektive Stärke mit Berücksichtigung von "Kräftig"
        if hasattr(charakter, 'get_effektive_staerke'):
            charakter_staerke_wert = charakter.get_effektive_staerke(fuer_ausruestung=True)
        else:
            charakter_staerke_wert = charakter.attribute['Stärke'].wert
            
            # Prüfen, ob der Charakter das Talent "Kräftig" hat
            if "Kräftig" in charakter.selected_talente:
                # Stärke um einen Würfeltyp erhöhen
                if charakter_staerke_wert == 4:
                    charakter_staerke_wert = 6
                elif charakter_staerke_wert == 6:
                    charakter_staerke_wert = 8
                elif charakter_staerke_wert == 8:
                    charakter_staerke_wert = 10
                elif charakter_staerke_wert == 10:
                    charakter_staerke_wert = 12
        
        # Mapping von Würfelwerten zu numerischen Werten
        staerke_mapping = {'W4': 4, 'W6': 6, 'W8': 8, 'W10': 10, 'W12': 12, '-': 0}
        
        mindeststaerke_num = staerke_mapping.get(mindeststaerke_wert, 0)
        
        return charakter_staerke_wert >= mindeststaerke_num

    def toggle_angelegt(self, charakter=None):
        """
        Schaltet den Anlege-Status der Rüstung um, prüft bei Bedarf die Mindeststärke.
        
        Args:
            charakter: Optional - Der Charakter, für den die Rüstung angelegt werden soll
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
