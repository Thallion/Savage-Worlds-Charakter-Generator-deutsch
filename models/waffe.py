# models/waffe.py
from kivy.properties import StringProperty, BooleanProperty, DictProperty
from models.ausruestung import Ausruestung
from kivy.logger import Logger
import logging

class Waffe(Ausruestung):
    typ = StringProperty("")  # 'Nahkampf' oder 'Fernkampf'
    mindeststaerke = StringProperty("")
    angelegt = BooleanProperty(False)
    eigenschaften = DictProperty({})  # Um Eigenschaften zu speichern
    ausgewaehlt = BooleanProperty(False)
    custom = BooleanProperty(False)

    def __init__(
        self,
        name,
        gewicht,
        kosten,
        setting,
        typ,
        mindeststaerke='W4',
        beschreibung='',
        eigenschaften=None,
        menge=0,
        ausgewaehlt=False,
        aktiv=True,
        angelegt=False,
        kategorie='Waffe',
        **kwargs
    ):
        super().__init__(
            name=name,
            gewicht=gewicht,
            kosten=kosten,
            setting=setting,
            beschreibung=beschreibung,
            menge=menge,
            ausgewaehlt=ausgewaehlt,
            aktiv=aktiv,
            angelegt=angelegt,
            kategorie=kategorie,
            **kwargs  # Weitere zusätzliche Keyword-Argumente
        )
        self.typ = typ
        self.mindeststaerke = mindeststaerke
        self.eigenschaften = eigenschaften or {}
        self.custom = kwargs.get('custom', False)
        self.bind(angelegt=self.on_angelegt_changed)
        # Logger.debug(f"Waffe '{self.name}' initialisiert mit Typ: {self.typ}, Mindeststärke: {self.mindeststaerke}.")

    
    def berechne_gewicht(self):
        if self.angelegt:
            return self.gewicht / 2
        return self.gewicht
    
    def kann_angelegt_werden(self, charakter):
        """
        Prüft, ob der Charakter die Mindeststärke für die Waffe erfüllt.
        Berücksichtigt das Talent "Kräftig".
        
        Args:
            charakter: Das Charakter-Objekt
            
        Returns:
            bool: True wenn die Mindeststärke erfüllt ist, sonst False
        """
        mindeststaerke_num = self.convert_staerke_to_num(self.mindeststaerke)
        
        # Effektive Stärke mit Berücksichtigung von "Kräftig"
        if hasattr(charakter, 'get_effektive_staerke'):
            charakter_staerke_num = charakter.get_effektive_staerke(fuer_ausruestung=True)
        else:
            # Fallback für Abwärtskompatibilität
            charakter_staerke_num = self.convert_staerke_to_num(charakter.attribute['Stärke'].wert)
            
            # Prüfen, ob der Charakter das Talent "Kräftig" hat
            if "Kräftig" in charakter.selected_talente:
                # Einen Würfeltyp höher für Ausrüstung
                if charakter_staerke_num == 4:
                    charakter_staerke_num = 6
                elif charakter_staerke_num == 6:
                    charakter_staerke_num = 8
                elif charakter_staerke_num == 8:
                    charakter_staerke_num = 10
                elif charakter_staerke_num == 10:
                    charakter_staerke_num = 12
        
        return charakter_staerke_num >= mindeststaerke_num

    def anlegen(self, charakter):
        """
        Legt die Waffe an, unabhängig von der Mindeststärke.
        Gibt nur eine Warnung aus, wenn die Mindeststärke nicht erfüllt ist.
        
        Args:
            charakter: Das Charakterobjekt, dem die Waffe angelegt werden soll
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

    def toggle_angelegt(self, charakter=None):
        """
        Schaltet den Anlege-Status der Waffe um, prüft bei Bedarf die Mindeststärke.
        
        Args:
            charakter: Optional - Der Charakter, für den die Waffe angelegt werden soll
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
            gewicht=data.get('gewicht', 0),
            kosten=data.get('kosten', 0),
            setting=data.get('setting', ''),
            typ=data.get('typ', ''),
            mindeststaerke=data.get('mindeststaerke', 'W4'),
            beschreibung=data.get('beschreibung', ''),
            eigenschaften=data.get('eigenschaften', {}),
            menge=data.get('menge', 0),
            ausgewaehlt=data.get('ausgewaehlt', False),
            aktiv=data.get('aktiv', True),
            angelegt=data.get('angelegt', False),
            kategorie=data.get('kategorie', 'Waffe')
        )

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'typ': self.typ,
            'menge': self.menge,
            'mindeststaerke': self.mindeststaerke,
            'eigenschaften': self.eigenschaften,
            'angelegt': self.angelegt
        })
        return data

    def to_setting_dict(self):
        """Speichert die Waffe-spezifischen Basisdaten für das Setting."""
        data = super().to_setting_dict()
        data.update({
            'typ': self.typ,
            'mindeststaerke': self.mindeststaerke,
            'eigenschaften': self.eigenschaften,
            # Fügen Sie weitere waffenrelevante Attribute hinzu
        })
        return data

    @classmethod
    def from_setting_dict(cls, data):
        return cls(
            name=data.get('name', ''),
            gewicht=data.get('gewicht', 0),
            kosten=data.get('kosten', 0),
            setting=data.get('setting', ''),
            typ=data.get('typ', ''),
            mindeststaerke=data.get('mindeststaerke', 'W4'),
            beschreibung=data.get('beschreibung', ''),
            eigenschaften=data.get('eigenschaften', {}),
            kategorie=data.get('kategorie', 'Waffe'),
            # Charakterbezogene Daten werden nicht geladen
        )
