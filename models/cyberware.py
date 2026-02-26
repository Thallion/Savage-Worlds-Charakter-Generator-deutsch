# models/cyberware.py
"""
Datenmodell für Cyberware-Installationen im SciFi Kompendium.
Cyberware sind kybernetische Implantate mit Stress-Kosten.
Jede Installation hat einen Stresswert, der gegen das Stresslimit
des Charakters gerechnet wird.
"""
import uuid
from kivy.properties import (
    NumericProperty, StringProperty, BooleanProperty,
    DictProperty, ListProperty
)
from kivy.event import EventDispatcher
from kivy.logger import Logger


class CyberwareInstallation(EventDispatcher):
    """
    Repräsentiert eine einzelne Cyberware-Installation eines Charakters.

    Jede Installation hat:
    - Stress-Kosten die gegen das Stresslimit zählen
    - Eine maximale Installationsanzahl (-1 = unbegrenzt)
    - Maschinenlesbare Spieleffekte
    - Optionale Konfiguration (z.B. welches Attribut bei Attributerhöhung)
    """
    name = StringProperty("")
    beschreibung = StringProperty("")
    unterkategorie = StringProperty("")
    stress = NumericProperty(0)
    max_installationen = NumericProperty(-1)
    kosten = NumericProperty(0)
    effekte = DictProperty({})
    installiert = BooleanProperty(False)
    aktiv = BooleanProperty(True)
    installations_id = StringProperty("")
    installations_datum = StringProperty("")
    konfiguration = DictProperty({})

    def __init__(self, name="", beschreibung="", unterkategorie="",
                 stress=0, max_installationen=-1, kosten=0,
                 effekte=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.beschreibung = beschreibung
        self.unterkategorie = unterkategorie
        self.stress = stress
        self.max_installationen = max_installationen
        self.kosten = kosten
        self.effekte = effekte or {}
        self.installiert = False
        self.aktiv = True
        self.installations_id = str(uuid.uuid4())
        self.installations_datum = ""
        self.konfiguration = {}

    def to_dict(self):
        """Serialisiert die CyberwareInstallation für Speicherung."""
        return {
            'name': self.name,
            'beschreibung': self.beschreibung,
            'unterkategorie': self.unterkategorie,
            'stress': self.stress,
            'max_installationen': self.max_installationen,
            'kosten': self.kosten,
            'effekte': dict(self.effekte),
            'installiert': self.installiert,
            'aktiv': self.aktiv,
            'installations_id': self.installations_id,
            'installations_datum': self.installations_datum,
            'konfiguration': dict(self.konfiguration),
        }

    @classmethod
    def from_dict(cls, data):
        """Erstellt eine CyberwareInstallation aus einem gespeicherten Dictionary."""
        installation = cls(
            name=data.get('name', ''),
            beschreibung=data.get('beschreibung', ''),
            unterkategorie=data.get('unterkategorie', ''),
            stress=data.get('stress', 0),
            max_installationen=data.get('max_installationen', -1),
            kosten=data.get('kosten', 0),
            effekte=data.get('effekte', {}),
        )
        installation.installiert = data.get('installiert', False)
        installation.aktiv = data.get('aktiv', True)
        installation.installations_id = data.get('installations_id', str(uuid.uuid4()))
        installation.installations_datum = data.get('installations_datum', '')
        installation.konfiguration = data.get('konfiguration', {})
        return installation

    @classmethod
    def from_setting_dict(cls, data):
        """Erstellt eine CyberwareInstallation aus Setting-JSON-Daten.

        Setting-Format (aus SciFi Kompendium.json):
        {
            "name": "Cyberware: Panzerung",
            "kategorie": "Cyberware",
            "unterkategorie": "Defensiv",
            "gewicht": 0,
            "kosten": 5000,
            "stress": 1,
            "max_installationen": 3,
            "setting": "scifi",
            "beschreibung": "...",
            "effekte": {...},
            "aktiv": true
        }
        """
        return cls(
            name=data.get('name', ''),
            beschreibung=data.get('beschreibung', ''),
            unterkategorie=data.get('unterkategorie', ''),
            stress=data.get('stress', 0),
            max_installationen=data.get('max_installationen', -1),
            kosten=data.get('kosten', 0),
            effekte=data.get('effekte', {}),
        )

    def __str__(self):
        status = "installiert" if self.installiert else "verfügbar"
        return f"{self.name} (Stress: {self.stress}, {status})"

    def __repr__(self):
        return (f"CyberwareInstallation(name='{self.name}', stress={self.stress}, "
                f"installiert={self.installiert})")
