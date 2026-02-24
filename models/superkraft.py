# models/superkraft.py
"""
Datenmodell für Superkräfte im Superkräfte-Kompendium.
Superkräfte unterscheiden sich von normalen Mächten:
- Kosten in Superkraftpunkten (SKP) statt Machtpunkten
- Variable Kostenstrukturen (fest, Bereich, speziell)
- Modifikatoren die Kosten erhöhen/senken
- Kraftobergrenze pro Machtstufe
"""
from kivy.properties import (
    NumericProperty, StringProperty, BooleanProperty,
    DictProperty, ListProperty
)
from kivy.event import EventDispatcher
from kivy.logger import Logger


class SuperkraftModifikator:
    """Ein gewählter Modifikator für eine Superkraft"""

    def __init__(self, name, kosten, beschreibung=""):
        self.name = name
        self.kosten = kosten  # int oder str (z.B. "2/4")
        self.beschreibung = beschreibung

    def get_effektive_kosten(self):
        """Gibt die effektiven Kosten als int zurück.
        Bei String-Kosten (z.B. '2/4') wird der erste Wert verwendet."""
        if isinstance(self.kosten, (int, float)):
            return int(self.kosten)
        if isinstance(self.kosten, str):
            # Versuche den ersten numerischen Wert zu extrahieren
            try:
                erster_wert = self.kosten.split('/')[0].strip()
                # Entferne nicht-numerische Zeichen (z.B. "1 pro 2 PB" → 1)
                ziffern = ''
                negativ = False
                for ch in erster_wert:
                    if ch == '-' and not ziffern:
                        negativ = True
                    elif ch.isdigit():
                        ziffern += ch
                    elif ziffern:
                        break
                if ziffern:
                    wert = int(ziffern)
                    return -wert if negativ else wert
            except (ValueError, IndexError):
                pass
        return 0

    def to_dict(self):
        return {
            'name': self.name,
            'kosten': self.kosten,
            'beschreibung': self.beschreibung,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name', ''),
            kosten=data.get('kosten', 0),
            beschreibung=data.get('beschreibung', ''),
        )


class Superkraft(EventDispatcher):
    """
    Repräsentiert eine Superkraft eines Charakters.

    Unterschied zu Macht:
    - Kosten sind in SKP (Superkraftpunkten) statt Machtpunkten
    - Kosten können variabel sein (z.B. "2-18" für Fliegen)
    - Modifikatoren verändern die Gesamtkosten
    - Kraftobergrenze begrenzt die maximalen SKP pro Kraft
    """
    name = StringProperty("")
    beschreibung = StringProperty("")
    basis_kosten = StringProperty("")  # Original-Kosten aus dem Setting (z.B. "2-18", "speziell", "3")
    gewaehlte_kosten = NumericProperty(0)  # Gewählte Basis-SKP (z.B. 6 für "Fliegen BW 48")
    ausgewaehlt = BooleanProperty(False)
    aktiv = BooleanProperty(True)

    def __init__(self, name="", kosten="", beschreibung="",
                 verfuegbare_modifikatoren=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.basis_kosten = str(kosten)
        self.beschreibung = beschreibung
        self.gewaehlte_kosten = 0
        self.ausgewaehlt = False
        self.aktiv = True

        # Verfügbare Modifikatoren (aus dem Setting-JSON)
        self.verfuegbare_modifikatoren = verfuegbare_modifikatoren or {}

        # Gewählte Modifikatoren (Liste von SuperkraftModifikator)
        self.gewaehlte_modifikatoren = []

    @property
    def gesamt_kosten(self):
        """Berechnet die Gesamtkosten: gewählte Basiskosten + Modifikator-Kosten"""
        total = self.gewaehlte_kosten
        for mod in self.gewaehlte_modifikatoren:
            total += mod.get_effektive_kosten()
        return max(0, total)  # Kosten können nicht unter 0 fallen

    def hat_variable_kosten(self):
        """Prüft ob die Kraft variable Kosten hat (z.B. '2-18', 'speziell', '2/4')"""
        kosten_str = self.basis_kosten.strip()
        if not kosten_str:
            return True
        # Prüfe auf Bereichs-Format "X-Y"
        if '-' in kosten_str and kosten_str[0] != '-':
            return True
        # Prüfe auf Alternativ-Format "X/Y"
        if '/' in kosten_str:
            return True
        # "speziell" ist immer variabel
        if kosten_str.lower() == 'speziell':
            return True
        return False

    def get_kosten_bereich(self):
        """Gibt den Kostenbereich als Tuple (min, max) zurück.
        Bei festen Kosten: (kosten, kosten)
        Bei Bereich: (min, max)
        Bei 'speziell': (0, 0)"""
        kosten_str = self.basis_kosten.strip()

        if not kosten_str or kosten_str.lower() == 'speziell':
            return (0, 0)

        # Bereich "X-Y"
        if '-' in kosten_str and kosten_str[0] != '-':
            teile = kosten_str.split('-')
            try:
                return (int(teile[0].strip()), int(teile[1].strip()))
            except (ValueError, IndexError):
                return (0, 0)

        # Alternativ "X/Y"
        if '/' in kosten_str:
            teile = kosten_str.split('/')
            try:
                werte = [int(t.strip()) for t in teile if t.strip().lstrip('-').isdigit()]
                if werte:
                    return (min(werte), max(werte))
            except ValueError:
                return (0, 0)

        # Feste Kosten
        try:
            k = int(kosten_str)
            return (k, k)
        except ValueError:
            return (0, 0)

    def get_feste_kosten(self):
        """Gibt die festen Kosten zurück (int), oder 0 bei variablen Kosten."""
        if self.hat_variable_kosten():
            return 0
        try:
            return int(self.basis_kosten.strip())
        except (ValueError, TypeError):
            return 0

    def waehle_modifikator(self, mod_name, mod_kosten=None, mod_beschreibung=None):
        """Fügt einen Modifikator zur Superkraft hinzu.

        Args:
            mod_name: Name des Modifikators
            mod_kosten: Kosten des Modifikators (wenn None, aus verfuegbare_modifikatoren)
            mod_beschreibung: Beschreibung (wenn None, aus verfuegbare_modifikatoren)

        Returns:
            bool: True bei Erfolg
        """
        if mod_kosten is None and mod_name in self.verfuegbare_modifikatoren:
            mod_data = self.verfuegbare_modifikatoren[mod_name]
            mod_kosten = mod_data.get('kosten', 0)
            mod_beschreibung = mod_data.get('beschreibung', '')

        if mod_kosten is None:
            Logger.warning(f"Superkraft '{self.name}': Modifikator '{mod_name}' nicht gefunden")
            return False

        mod = SuperkraftModifikator(mod_name, mod_kosten, mod_beschreibung or "")
        self.gewaehlte_modifikatoren.append(mod)
        Logger.debug(f"Superkraft '{self.name}': Modifikator '{mod_name}' hinzugefügt (Kosten: {mod_kosten})")
        return True

    def entferne_modifikator(self, mod_name):
        """Entfernt einen gewählten Modifikator.

        Args:
            mod_name: Name des zu entfernenden Modifikators

        Returns:
            bool: True wenn entfernt
        """
        for i, mod in enumerate(self.gewaehlte_modifikatoren):
            if mod.name == mod_name:
                self.gewaehlte_modifikatoren.pop(i)
                Logger.debug(f"Superkraft '{self.name}': Modifikator '{mod_name}' entfernt")
                return True
        return False

    def auswaehlen(self, kosten=None):
        """Wählt die Superkraft aus.

        Args:
            kosten: Die gewählten Basis-SKP (bei variablen Kosten erforderlich)

        Returns:
            bool: True bei Erfolg
        """
        if self.ausgewaehlt:
            Logger.warning(f"Superkraft '{self.name}' ist bereits ausgewählt.")
            return False

        if kosten is not None:
            self.gewaehlte_kosten = kosten
        elif not self.hat_variable_kosten():
            self.gewaehlte_kosten = self.get_feste_kosten()

        self.ausgewaehlt = True
        Logger.debug(f"Superkraft '{self.name}' ausgewählt (Kosten: {self.gesamt_kosten} SKP)")
        return True

    def abwaehlen(self):
        """Wählt die Superkraft ab und setzt alle Werte zurück."""
        if not self.ausgewaehlt:
            Logger.warning(f"Superkraft '{self.name}' ist nicht ausgewählt.")
            return False

        self.ausgewaehlt = False
        self.gewaehlte_kosten = 0
        self.gewaehlte_modifikatoren = []
        Logger.debug(f"Superkraft '{self.name}' abgewählt")
        return True

    def to_dict(self):
        """Serialisiert die Superkraft für Speicherung."""
        return {
            'name': self.name,
            'basis_kosten': self.basis_kosten,
            'beschreibung': self.beschreibung,
            'gewaehlte_kosten': self.gewaehlte_kosten,
            'ausgewaehlt': self.ausgewaehlt,
            'aktiv': self.aktiv,
            'gewaehlte_modifikatoren': [mod.to_dict() for mod in self.gewaehlte_modifikatoren],
            'verfuegbare_modifikatoren': self.verfuegbare_modifikatoren,
        }

    @classmethod
    def from_dict(cls, data):
        """Erstellt eine Superkraft aus einem Dictionary."""
        kraft = cls(
            name=data.get('name', ''),
            kosten=data.get('basis_kosten', data.get('kosten', '')),
            beschreibung=data.get('beschreibung', ''),
            verfuegbare_modifikatoren=data.get('verfuegbare_modifikatoren',
                                                data.get('modifikatoren', {})),
        )
        kraft.gewaehlte_kosten = data.get('gewaehlte_kosten', 0)
        kraft.ausgewaehlt = data.get('ausgewaehlt', False)
        kraft.aktiv = data.get('aktiv', True)

        # Gewählte Modifikatoren laden
        for mod_data in data.get('gewaehlte_modifikatoren', []):
            kraft.gewaehlte_modifikatoren.append(
                SuperkraftModifikator.from_dict(mod_data)
            )

        return kraft

    @classmethod
    def from_setting_dict(cls, data):
        """Erstellt eine Superkraft aus Setting-JSON-Daten.

        Setting-Format:
        {
            "name": "Fliegen",
            "kosten": "2-18",
            "beschreibung": "...",
            "modifikatoren": {"Unbeholfen": {"kosten": -2, "beschreibung": "..."}},
            "ausgewaehlt": false,
            "aktiv": true
        }
        """
        return cls(
            name=data.get('name', ''),
            kosten=data.get('kosten', ''),
            beschreibung=data.get('beschreibung', ''),
            verfuegbare_modifikatoren=data.get('modifikatoren', {}),
        )

    def __str__(self):
        mod_text = ""
        if self.gewaehlte_modifikatoren:
            mod_namen = [m.name for m in self.gewaehlte_modifikatoren]
            mod_text = f", Modifikatoren: {', '.join(mod_namen)}"
        return f"{self.name} (SKP: {self.gesamt_kosten}{mod_text})"

    def __repr__(self):
        return f"Superkraft(name='{self.name}', kosten='{self.basis_kosten}', ausgewaehlt={self.ausgewaehlt})"
