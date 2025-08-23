"""
Konfigurationsdatei für Ausrüstungs-bezogene Konstanten und Einstellungen.
Zentralisiert alle hardcodierten Werte für bessere Wartbarkeit.
"""

from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class AusruestungKategorien:
    """Definiert die verfügbaren Ausrüstungskategorien."""
    WAFFE = "Waffe"
    RUESTUNG = "Rüstung" 
    SCHILD = "Schild"
    ALLGEMEIN = "Allgemein"
    
    @classmethod
    def alle(cls) -> List[str]:
        """Gibt alle Kategorien als Liste zurück."""
        return [cls.WAFFE, cls.RUESTUNG, cls.SCHILD, cls.ALLGEMEIN]
    
    @classmethod
    def ist_gueltig(cls, kategorie: str) -> bool:
        """Prüft ob eine Kategorie gültig ist."""
        return kategorie in cls.alle()


@dataclass
class RuestungsKoerperteile:
    """Definiert die Körperteile für Rüstungsschutz."""
    TORSO = "Torso"
    ARME = "Arme"
    BEINE = "Beine"
    KOPF = "Kopf"
    
    @classmethod
    def alle(cls) -> List[str]:
        """Gibt alle Körperteile als Liste zurück."""
        return [cls.TORSO, cls.ARME, cls.BEINE, cls.KOPF]
    
    @classmethod
    def standard_schutz(cls) -> Dict[str, int]:
        """Gibt Standard-Schutzwerte zurück."""
        return {
            cls.TORSO: 0,
            cls.ARME: 0,
            cls.BEINE: 0,
            cls.KOPF: 0
        }


@dataclass
class WaffenEigenschaften:
    """Definiert die Standard-Eigenschaften von Waffen."""
    SCHADEN = "Schaden"
    REICHWEITE = "Reichweite"
    FEUERRATE = "FR"
    SCHUSS = "Schuss"
    PANZERBRECHER = "PB"
    
    @classmethod
    def standard_eigenschaften(cls) -> Dict[str, str]:
        """Gibt Standard-Eigenschaften für neue Waffen zurück."""
        return {
            cls.SCHADEN: "-",
            cls.REICHWEITE: "-",
            cls.FEUERRATE: "-",
            cls.SCHUSS: "-",
            cls.PANZERBRECHER: "-"
        }


@dataclass
class SchildEigenschaften:
    """Definiert die Standard-Eigenschaften von Schilden."""
    PARADE = "parade"
    DECKUNG = "deckung"
    MINDESTSTAERKE = "mindeststaerke"
    
    @classmethod
    def standard_eigenschaften(cls) -> Dict[str, Any]:
        """Gibt Standard-Eigenschaften für neue Schilde zurück."""
        return {
            cls.PARADE: 0,
            cls.DECKUNG: 0,
            cls.MINDESTSTAERKE: "W4"
        }


@dataclass 
class StaerkeWerte:
    """Definiert die möglichen Stärke-Würfelwerte."""
    W4 = "W4"
    W6 = "W6"
    W8 = "W8"
    W10 = "W10"
    W12 = "W12"
    KEINE = "-"
    
    MAPPING = {
        W4: 4,
        W6: 6,
        W8: 8,
        W10: 10,
        W12: 12,
        KEINE: 0
    }
    
    @classmethod
    def zu_nummer(cls, wert: str) -> int:
        """Konvertiert einen Stärkewert zu seiner numerischen Repräsentation."""
        return cls.MAPPING.get(wert, 0)
    
    @classmethod
    def ist_gueltig(cls, wert: str) -> bool:
        """Prüft ob ein Stärkewert gültig ist."""
        return wert in cls.MAPPING


@dataclass
class TraglastKonstanten:
    """Konstanten für die Traglast-Berechnung."""
    MAX_ERSCHOEPFUNG = 3
    STANDARD_MULTIPLIKATOR = 1
    
    # Multiplikatoren für Talente
    TALENT_MULTIPLIKATOREN = {
        "Stinkreich": 5,
        "Reich": 3
    }


# Logging-Nachrichten als Konstanten
class LogMessages:
    """Zentrale Sammlung von Log-Nachrichten."""
    
    # Erfolg
    KAUF_ERFOLGREICH = "{anzahl}x {name} gekauft für insgesamt {preis}. Neues Vermögen: {vermoegen}."
    VERKAUF_ERFOLGREICH = "{anzahl}x {name} verkauft für insgesamt {preis}. Neues Vermögen: {vermoegen}."
    ITEM_ZU_LISTE_HINZUGEFUEGT = "{name} zur ausgewählten {liste} hinzugefügt."
    RUESTUNG_ANGELEGT = "Rüstung '{name}' angelegt."
    RUESTUNG_ABGELEGT = "Rüstung '{name}' abgelegt."
    
    # Warnungen
    NICHT_GENUEGEND_VERMOEGEN = "Nicht genügend Vermögen, um {anzahl}x {name} zu kaufen."
    NICHT_GENUEGEND_MENGE = "Nicht genügend {name} vorhanden. Verfügbar: {verfuegbar}, angefordert: {angefordert}."
    TRAGLAST_UEBERSCHRITTEN = "Traglast überschritten! Erschöpfung steigt auf {erschoepfung}."
    TRAGLAST_MAXIMAL = "Traglast überschritten, Erschöpfung ist bereits maximal."
    ELEMENT_EXISTIERT_NICHT = "Element '{name}' vom Typ '{typ}' existiert nicht."
    MINDESTSTAERKE_NICHT_ERFUELLT = "Mindeststärke für '{name}' nicht erfüllt. Benötigt: {benoetigt}, vorhanden: {vorhanden}"
    
    # Info
    ELEMENTE_GELADEN = "{anzahl} {typ} geladen."
    HANDICAP_ARM_AKTIVIERT = "Handicap 'Arm' ausgewählt: Vermögen halbiert auf {vermoegen}"
    HANDICAP_ARM_DEAKTIVIERT = "Handicap 'Arm' abgewählt: Vermögen wiederhergestellt auf {vermoegen}"
    TALENT_REICH_AKTIVIERT = "Talent '{name}' ausgewählt: Vermögen erhöht auf {vermoegen}"
    TALENT_REICH_DEAKTIVIERT = "Talent '{name}' abgewählt: Vermögen wiederhergestellt auf {vermoegen}"
    
    # Fehler
    FEHLER_BEIM_LADEN = "Fehler beim Laden des Ausrüstungsgegenstands '{name}': {error}"
    FEHLER_ALLGEMEIN = "Fehler bei {operation}: {error}"
    
    # Debug
    RUESTUNG_ZU_GESAMT = "Rüstung '{name}' wird zur Gesamtrüstung gezählt: Torso={torso}, Arme={arme}, Beine={beine}, Kopf={kopf}"
    GESAMTRUESTUNG_BERECHNET = "Gesamtrüstungsschutz berechnet: {schutz}"


# Export aller Konfigurationen
__all__ = [
    'AusruestungKategorien',
    'RuestungsKoerperteile',
    'WaffenEigenschaften',
    'SchildEigenschaften',
    'StaerkeWerte',
    'TraglastKonstanten',
    'LogMessages'
]