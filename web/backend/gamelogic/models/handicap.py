import logging

Logger = logging.getLogger(__name__)


class Handicap:
    def __init__(self, name, stufe, beschreibung='', custom=False):
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

    def __str__(self):
        return f"{self.name} (Stufe: {self.stufe})"

    def auswaehlen(self):
        self.ausgewaehlt = True

    def abwaehlen(self):
        self.ausgewaehlt = False

    def clone(self):
        h = Handicap(
            name=self.name,
            stufe=self.stufe,
            beschreibung=self.beschreibung,
            custom=self.custom,
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
            'custom': self.custom,
        }
        if self.auto_applied:
            result['auto_applied'] = True
        return result

    @classmethod
    def from_dict_static(cls, data):
        handicap = cls(
            name=data.get('name', ''),
            stufe=data.get('stufe', ''),
            beschreibung=data.get('beschreibung', ''),
        )
        handicap.punkte = data.get('punkte', handicap.punkte)
        handicap.ausgewaehlt = data.get('ausgewaehlt', False)
        handicap.aktiv = data.get('aktiv', True)
        handicap.auto_applied = data.get('auto_applied', False)
        return handicap

    @classmethod
    def from_dict(cls, data):
        return cls.from_dict_static(data)

    @classmethod
    def from_setting_dict(cls, data):
        return cls.from_dict_static(data)

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
            return None

    def update_from_dict(self, data):
        self.name = data.get('name', self.name)
        self.stufe = data.get('stufe', self.stufe)
        self.punkte = data.get('punkte', self.punkte)
        self.beschreibung = data.get('beschreibung', self.beschreibung)
        self.ausgewaehlt = data.get('ausgewaehlt', self.ausgewaehlt)
        self.aktiv = data.get('aktiv', self.aktiv)
        self.custom = data.get('custom', self.custom)
        self.update_punkte()
