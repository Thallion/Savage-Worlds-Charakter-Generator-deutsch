# functions/ausruestung_funktionen.py

from kivy.logger import Logger
from typing import Optional, Dict, List, Any

# Import der Konfiguration
from config.ausruestung_config import (
    AusruestungKategorien,
    RuestungsKoerperteile,
    TraglastKonstanten,
    LogMessages,
    StaerkeWerte
)

# Import der Models
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild
from models.ausruestung import Ausruestung


def kaufen(charakter, item: Ausruestung, anzahl: int = 1, preis_pro_stueck: Optional[float] = None) -> bool:
    """
    Kauft einen Ausrüstungsgegenstand für einen Charakter.
    
    Args:
        charakter: Das Charakterobjekt, das die Ausrüstung kauft
        item: Das zu kaufende Ausrüstungsobjekt
        anzahl: Wie viele Einheiten gekauft werden sollen
        preis_pro_stueck: Optionaler benutzerdefinierter Preis
    
    Returns:
        bool: True bei Erfolg, False bei Fehlschlag
    """
    preis_pro_stueck = preis_pro_stueck or item.kosten
    gesamtpreis = preis_pro_stueck * anzahl

    # Vermögensprüfung
    if charakter.vermoegen < gesamtpreis:
        Logger.warning(LogMessages.NICHT_GENUEGEND_VERMOEGEN.format(
            anzahl=anzahl, name=item.name
        ))
        return False

    # Transaktion durchführen
    charakter.vermoegen -= gesamtpreis
    item.erhoehe_menge(anzahl)
    Logger.debug(LogMessages.KAUF_ERFOLGREICH.format(
        anzahl=anzahl, 
        name=item.name, 
        preis=gesamtpreis, 
        vermoegen=charakter.vermoegen
    ))

    # Gewicht und Traglast berechnen
    _pruefe_traglast(charakter)

    # Item zu Ausrüstung hinzufügen
    _item_zu_ausruestung_hinzufuegen(charakter, item)

    charakter.berechne_abgeleitete_werte()
    return True


def verkaufen(charakter, item: Ausruestung, anzahl: int = 1, preis_pro_stueck: Optional[float] = None) -> bool:
    """
    Verkauft einen Ausrüstungsgegenstand eines Charakters.
    
    Args:
        charakter: Das Charakterobjekt, das die Ausrüstung verkauft
        item: Das zu verkaufende Ausrüstungsobjekt
        anzahl: Wie viele Einheiten verkauft werden sollen
        preis_pro_stueck: Optionaler benutzerdefinierter Preis
    
    Returns:
        bool: True bei Erfolg, False bei Fehlschlag
    """
    # Verfügbarkeitsprüfung
    if item.menge < anzahl:
        Logger.warning(LogMessages.NICHT_GENUEGEND_MENGE.format(
            name=item.name,
            verfuegbar=item.menge,
            angefordert=anzahl
        ))
        return False

    # Transaktion durchführen
    preis_pro_stueck = preis_pro_stueck or (item.kosten * 0.5)  # 50% des Kaufpreises
    gesamtpreis = preis_pro_stueck * anzahl
    charakter.vermoegen += gesamtpreis
    item.verringere_menge(anzahl)
    
    Logger.debug(LogMessages.VERKAUF_ERFOLGREICH.format(
        anzahl=anzahl,
        name=item.name,
        preis=gesamtpreis,
        vermoegen=charakter.vermoegen
    ))

    # Item entfernen wenn Menge 0
    if item.menge <= 0:
        _item_aus_ausruestung_entfernen(charakter, item)

    # Gewicht und abgeleitete Werte neu berechnen
    charakter.berechne_gesamtgewicht()
    charakter.berechne_abgeleitete_werte()
    
    return True


def berechne_gesamt_ruestungsschutz(charakter) -> Dict[str, int]:
    """
    Berechnet den Gesamtrüstungsschutz für jede Körperregion.
    
    Args:
        charakter: Das Charakterobjekt, dessen Rüstungsschutz berechnet werden soll
        
    Returns:
        dict: Ein Dictionary mit dem Gesamtrüstungsschutz für jede Körperregion
    """
    # Initialisiere mit Standard-Schutzwerten
    gesamt_schutz = RuestungsKoerperteile.standard_schutz()

    # Durchsuche alle Ausrüstungsgegenstände
    for item in charakter.ausruestung.values():
        if item is not None and isinstance(item, Ruestung) and item.angelegt and item.ausgewaehlt:
            gesamt_schutz[RuestungsKoerperteile.TORSO] += item.torso
            gesamt_schutz[RuestungsKoerperteile.ARME] += item.arme
            gesamt_schutz[RuestungsKoerperteile.BEINE] += item.beine
            gesamt_schutz[RuestungsKoerperteile.KOPF] += item.kopf
            
            Logger.debug(LogMessages.RUESTUNG_ZU_GESAMT.format(
                name=item.name,
                torso=item.torso,
                arme=item.arme,
                beine=item.beine,
                kopf=item.kopf
            ))
    
    Logger.debug(LogMessages.GESAMTRUESTUNG_BERECHNET.format(schutz=gesamt_schutz))
    return gesamt_schutz


def get_item_by_name(charakter, item_name: str) -> Optional[Ausruestung]:
    """
    Findet ein Ausrüstungsteil anhand des Namens.
    
    Args:
        charakter: Das Charakterobjekt, in dem gesucht werden soll
        item_name: Der Name des zu suchenden Items
        
    Returns:
        object or None: Das gefundene Item oder None wenn nicht gefunden
    """
    # Durchsuche alle ausgewählten Kategorien
    for item_liste in [
        charakter.selected_waffen,
        charakter.selected_schilde,
        charakter.selected_ruestungen,
        charakter.selected_allgemeine_ausruestung
    ]:
        for item in item_liste:
            if item.name == item_name:
                return item
    
    return None


def berechne_gesamtkosten(charakter) -> float:
    """
    Berechnet die Gesamtkosten der ausgewählten Ausrüstung.
    
    Args:
        charakter: Das Charakterobjekt, dessen Ausrüstungskosten berechnet werden sollen
        
    Returns:
        float: Die Gesamtkosten der Ausrüstung
    """
    gesamtkosten = 0.0
    
    # Alle Ausrüstungsgegenstände durchgehen
    for ausr in charakter.ausruestung.values():
        if ausr is not None and ausr.ausgewaehlt:
            gesamtkosten += ausr.kosten * ausr.menge
    
    # Falls separate Listen existieren (für Rückwärtskompatibilität)
    for liste_name in ['waffen', 'ruestungen', 'schilde']:
        if hasattr(charakter, liste_name):
            liste = getattr(charakter, liste_name)
            for item_name, item in liste.items():
                if item.ausgewaehlt:
                    gesamtkosten += item.kosten * item.menge
    
    return gesamtkosten


def anpassen_vermoegen_bei_handicap_arm(charakter, wird_ausgewaehlt: bool) -> None:
    """
    Passt das Vermögen bei Auswahl/Abwahl des Handicaps "Arm" an.
    
    Args:
        charakter: Das Charakter-Objekt
        wird_ausgewaehlt: True, wenn das Handicap ausgewählt wird, False, wenn es abgewählt wird
    """
    if wird_ausgewaehlt:
        # Arm wird ausgewählt -> Vermögen halbieren
        charakter.vermoegen = charakter.vermoegen // 2
        Logger.info(LogMessages.HANDICAP_ARM_AKTIVIERT.format(
            vermoegen=charakter.vermoegen
        ))
    else:
        # Arm wird abgewählt -> Vermögen wiederherstellen
        multiplikator = _berechne_vermoegen_multiplikator(charakter)
        charakter.vermoegen = charakter.startkapital * multiplikator
        Logger.info(LogMessages.HANDICAP_ARM_DEAKTIVIERT.format(
            vermoegen=charakter.vermoegen
        ))


def anpassen_vermoegen_bei_talent_reich(charakter, talent_name: str, wird_ausgewaehlt: bool) -> None:
    """
    Passt das Vermögen bei Auswahl/Abwahl der Talente "Reich" oder "Stinkreich" an.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name: Name des Talents ("Reich" oder "Stinkreich")
        wird_ausgewaehlt: True, wenn das Talent ausgewählt wird, False, wenn es abgewählt wird
    """
    # Prüfen ob "Arm" aktiv ist
    if "Arm" in charakter.selected_handicaps:
        return  # Keine Änderung bei aktivem "Arm" Handicap
    
    if wird_ausgewaehlt:
        # Talent wird ausgewählt
        multiplikator = TraglastKonstanten.TALENT_MULTIPLIKATOREN.get(
            talent_name, 
            TraglastKonstanten.STANDARD_MULTIPLIKATOR
        )
        charakter.vermoegen = charakter.startkapital * multiplikator
        Logger.info(LogMessages.TALENT_REICH_AKTIVIERT.format(
            name=talent_name,
            vermoegen=charakter.vermoegen
        ))
    else:
        # Talent wird abgewählt
        multiplikator = _berechne_vermoegen_multiplikator(charakter, exclude_talent=talent_name)
        charakter.vermoegen = charakter.startkapital * multiplikator
        Logger.info(LogMessages.TALENT_REICH_DEAKTIVIERT.format(
            name=talent_name,
            vermoegen=charakter.vermoegen
        ))


def erstelle_item_nach_kategorie(item_dict: Dict[str, Any]) -> Ausruestung:
    """
    Erstellt ein Item-Objekt basierend auf der Kategorie.
    
    Args:
        item_dict: Dictionary mit Item-Daten
        
    Returns:
        Ausruestung: Das erstellte Item-Objekt
    """
    kategorie = item_dict.get('kategorie', AusruestungKategorien.ALLGEMEIN)
    
    kategorie_zu_klasse = {
        AusruestungKategorien.WAFFE: Waffe,
        AusruestungKategorien.RUESTUNG: Ruestung,
        AusruestungKategorien.SCHILD: Schild,
        AusruestungKategorien.ALLGEMEIN: Ausruestung
    }
    
    klasse = kategorie_zu_klasse.get(kategorie, Ausruestung)
    return klasse.from_setting_dict(item_dict)


# --- Private Hilfsfunktionen ---

def _pruefe_traglast(charakter) -> None:
    """
    Prüft die Traglast und passt Erschöpfung an.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    charakter.berechne_gesamtgewicht()
    maximale_traglast = charakter.berechne_traglast()
    
    if charakter.gesamtgewicht > maximale_traglast:
        if charakter.erschoepfung < TraglastKonstanten.MAX_ERSCHOEPFUNG:
            charakter.erschoepfung += 1
            Logger.warning(LogMessages.TRAGLAST_UEBERSCHRITTEN.format(
                erschoepfung=charakter.erschoepfung
            ))
        else:
            Logger.warning(LogMessages.TRAGLAST_MAXIMAL)


def _item_zu_ausruestung_hinzufuegen(charakter, item: Ausruestung) -> None:
    """
    Fügt ein Item zur Ausrüstung und den entsprechenden Listen hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
        item: Das hinzuzufügende Item
    """
    # Zur Hauptausrüstungsliste hinzufügen
    if item.name not in charakter.ausruestung:
        charakter.ausruestung[item.name] = item

    # Zur allgemeinen Ausrüstungsliste hinzufügen
    if item not in charakter.selected_allgemeine_ausruestung:
        charakter.selected_allgemeine_ausruestung.append(item)

    # Zur spezifischen Liste basierend auf der Kategorie hinzufügen
    _item_zu_kategorie_liste_hinzufuegen(charakter, item)


def _item_zu_kategorie_liste_hinzufuegen(charakter, item: Ausruestung) -> None:
    """
    Fügt ein Item zur entsprechenden Kategorie-Liste hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
        item: Das hinzuzufügende Item
    """
    kategorie_zu_liste = {
        AusruestungKategorien.WAFFE: ('selected_waffen', 'Waffenliste'),
        AusruestungKategorien.RUESTUNG: ('selected_ruestungen', 'Rüstungenliste'),
        AusruestungKategorien.SCHILD: ('selected_schilde', 'Schildeliste')
    }
    
    if item.kategorie in kategorie_zu_liste:
        liste_name, liste_beschreibung = kategorie_zu_liste[item.kategorie]
        liste = getattr(charakter, liste_name)
        
        if item not in liste:
            liste.append(item)
            Logger.debug(LogMessages.ITEM_ZU_LISTE_HINZUGEFUEGT.format(
                name=item.name,
                liste=liste_beschreibung
            ))


def _item_aus_ausruestung_entfernen(charakter, item: Ausruestung) -> None:
    """
    Entfernt ein Item aus der Ausrüstung und allen Listen.
    
    Args:
        charakter: Das Charakter-Objekt
        item: Das zu entfernende Item
    """
    # Aus Hauptausrüstung entfernen
    if item.name in charakter.ausruestung:
        del charakter.ausruestung[item.name]
    
    # Aus allgemeiner Liste entfernen
    if item in charakter.selected_allgemeine_ausruestung:
        charakter.selected_allgemeine_ausruestung.remove(item)
    
    # Aus kategoriespezifischen Listen entfernen
    kategorie_listen = {
        AusruestungKategorien.WAFFE: 'selected_waffen',
        AusruestungKategorien.RUESTUNG: 'selected_ruestungen',
        AusruestungKategorien.SCHILD: 'selected_schilde'
    }
    
    if item.kategorie in kategorie_listen:
        liste_name = kategorie_listen[item.kategorie]
        liste = getattr(charakter, liste_name)
        if item in liste:
            liste.remove(item)


def _berechne_vermoegen_multiplikator(charakter, exclude_talent: Optional[str] = None) -> int:
    """
    Berechnet den Vermögens-Multiplikator basierend auf aktiven Talenten.
    
    Args:
        charakter: Das Charakter-Objekt
        exclude_talent: Optional - Talent das bei der Berechnung ignoriert werden soll
        
    Returns:
        int: Der berechnete Multiplikator
    """
    multiplikator = TraglastKonstanten.STANDARD_MULTIPLIKATOR
    
    for talent_name, talent_mult in TraglastKonstanten.TALENT_MULTIPLIKATOREN.items():
        if talent_name != exclude_talent and talent_name in charakter.selected_talente:
            multiplikator = max(multiplikator, talent_mult)
    
    return multiplikator


def berechne_gesamtgewicht(charakter):
    """
    DEPRECATED: Diese Funktion existiert für Rückwärtskompatibilität.
    Nutze stattdessen charakter.berechne_gesamtgewicht() Methode.
    
    Berücksichtigt nur ausgewählte Ausrüstung mit Menge > 0.
    """
    try:
        # Verwende die korrigierte Methode für konsistente Berechnung
        return charakter.berechne_gesamtgewicht()
    except (AttributeError, TypeError):
        return 0


def berechne_traglast(charakter):
    """
    DEPRECATED: Diese Funktion existiert für Rückwärtskompatibilität.  
    Nutze stattdessen charakter.berechne_traglast().
    
    Berechnet die maximale Traglast basierend auf Stärke-Attribut.
    Beim Talent "Kräftig" wird die Traglast um 20 kg erhöht.
    """
    try:
        staerke_attribut = charakter.attribute.get('Stärke')
        if staerke_attribut:
            staerke_wert = staerke_attribut.wert
        else:
            staerke_wert = 4  # Standardwert, wenn Stärke nicht vorhanden

        maximale_traglast = staerke_wert * 10  # 10 kg pro Punkt Stärke
        
        # Bonus für das Talent "Kräftig" hinzufügen
        if "Kräftig" in charakter.selected_talente:
            maximale_traglast += 20  # +20 kg Traglast bei Kräftig
        
        return maximale_traglast

    except Exception as e:
        Logger.error(f"Fehler bei der Berechnung der maximalen Traglast: {e}")
        return 40  # Fallback-Wert (Stärke W4 * 10)


# Export der öffentlichen Funktionen
__all__ = [
    'kaufen',
    'verkaufen',
    'berechne_gesamt_ruestungsschutz',
    'get_item_by_name',
    'berechne_gesamtkosten',
    'anpassen_vermoegen_bei_handicap_arm',
    'anpassen_vermoegen_bei_talent_reich',
    'erstelle_item_nach_kategorie',
    'berechne_gesamtgewicht',  # Deprecated
    'berechne_traglast'        # Deprecated
]