# functions/ausruestung_funktionen.py

from kivy.logger import Logger
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild

def kaufen(charakter, item, anzahl=1, preis_pro_stueck=None):
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

    if charakter.vermoegen < gesamtpreis:
        Logger.warning(f"Nicht genügend Vermögen, um {anzahl}x {item.name} zu kaufen.")
        return False

    charakter.vermoegen -= gesamtpreis
    item.erhoehe_menge(anzahl)
    Logger.debug(f"{anzahl}x {item.name} gekauft für insgesamt {gesamtpreis}. Neues Vermögen: {charakter.vermoegen}.")

    charakter.berechne_gesamtgewicht()

    maximale_traglast = charakter.berechne_traglast()
    if charakter.gesamtgewicht > maximale_traglast:
        if charakter.erschoepfung < 3:
            charakter.erschoepfung += 1
            Logger.warning(f"Traglast überschritten! Erschöpfung steigt auf {charakter.erschoepfung}.")
        else:
            Logger.warning("Traglast überschritten, Erschöpfung ist bereits maximal.")

    # Hinzufügen zur Ausrüstungsliste, falls nicht bereits vorhanden
    if item.name not in charakter.ausruestung:
        charakter.ausruestung[item.name] = item

    # Hinzufügen zur allgemeinen Ausrüstungsliste
    if item not in charakter.selected_allgemeine_ausruestung:
        charakter.selected_allgemeine_ausruestung.append(item)

    # Hinzufügen zur spezifischen Liste basierend auf der Kategorie
    if item.kategorie == 'Waffe':
        if item not in charakter.selected_waffen:
            charakter.selected_waffen.append(item)
            Logger.debug(f"{item.name} zur ausgewählten Waffenliste hinzugefügt.")
    elif item.kategorie == 'Rüstung':
        if item not in charakter.selected_ruestungen:
            charakter.selected_ruestungen.append(item)
            Logger.debug(f"{item.name} zur ausgewählten Rüstungenliste hinzugefügt.")
    elif item.kategorie == 'Schild':
        if item not in charakter.selected_schilde:
            charakter.selected_schilde.append(item)
            Logger.debug(f"{item.name} zur ausgewählten Schildeliste hinzugefügt.")

    charakter.berechne_abgeleitete_werte()
    return True

def verkaufen(charakter, item, anzahl=1, preis_pro_stueck=None):
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
    if item.menge < anzahl:
        Logger.warning(f"Nicht genügend Menge von '{item.name}' zum Verkaufen.")
        return False

    preis_pro_stueck = preis_pro_stueck or item.kosten
    gesamtpreis = preis_pro_stueck * anzahl

    charakter.vermoegen += gesamtpreis
    item.verringere_menge(anzahl)
    Logger.debug(f"{anzahl}x {item.name} verkauft für insgesamt {gesamtpreis}. Neues Vermögen: {charakter.vermoegen}.")

    charakter.berechne_gesamtgewicht()

    # Entfernen aus der Ausrüstungsliste, wenn Menge 0 ist
    if item.menge <= 0:
        del charakter.ausruestung[item.name]
        Logger.debug(f"{item.name} aus der Charakterausrüstung entfernt.")

        # Entfernen aus spezifischen Listen
        if item in charakter.selected_waffen:
            charakter.selected_waffen.remove(item)
            Logger.debug(f"{item.name} von der ausgewählten Waffenliste entfernt.")
        if item in charakter.selected_ruestungen:
            charakter.selected_ruestungen.remove(item)
            Logger.debug(f"{item.name} von der ausgewählten Rüstungenliste entfernt.")
        if item in charakter.selected_schilde:
            charakter.selected_schilde.remove(item)
            Logger.debug(f"{item.name} von der ausgewählten Schildeliste entfernt.")
        if item in charakter.selected_allgemeine_ausruestung:
            charakter.selected_allgemeine_ausruestung.remove(item)
            Logger.debug(f"{item.name} von der ausgewählten allgemeinen Ausrüstungsliste entfernt.")

    charakter.berechne_abgeleitete_werte()
    return True

def berechne_traglast(charakter):
    """
    Berechnet die maximale Traglast des Charakters basierend auf Stärke.
    
    Args:
        charakter: Das Charakterobjekt, dessen Traglast berechnet werden soll
        
    Returns:
        int: Die maximale Traglast in kg
    """
    try:
        staerke_attribut = charakter.attribute.get('Stärke')
        if staerke_attribut:
            staerke_wert = staerke_attribut.wert
        else:
            staerke_wert = 4  # Standardwert, wenn Stärke nicht vorhanden

        maximale_traglast = staerke_wert * 10  # 10 kg pro Punkt Stärke
        return maximale_traglast

    except Exception as e:
        Logger.error(f"Fehler bei der Berechnung der maximalen Traglast: {e}")
        return 0

def berechne_gesamtgewicht(charakter):
    """
    Berechnet das Gesamtgewicht aller ausgewählten Ausrüstungsgegenstände.
    Berücksichtigt die Menge und ob Gegenstände angelegt sind (halbes Gewicht).
    
    Args:
        charakter: Das Charakterobjekt, dessen Ausrüstungsgewicht berechnet werden soll
        
    Returns:
        float: Das Gesamtgewicht in kg
    """
    gesamtgewicht = 0

    # Normale Ausrüstung
    for item in charakter.ausruestung.values():
        if item.menge > 0:
            gesamtgewicht += item.gewicht * item.menge

    # Waffen
    for waffe in charakter.waffen.values() if hasattr(charakter, 'waffen') else []:
        if waffe.menge > 0:
            gewicht = waffe.berechne_gewicht() * waffe.menge
            gesamtgewicht += gewicht

    # Rüstungen
    for ruestung in charakter.ruestungen.values() if hasattr(charakter, 'ruestungen') else []:
        if ruestung.menge > 0:
            gewicht = ruestung.berechne_gewicht() * ruestung.menge
            gesamtgewicht += gewicht

    # Schilde
    for schild in charakter.schilde.values() if hasattr(charakter, 'schilde') else []:
        if schild.menge > 0:
            gewicht = schild.berechne_gewicht() * schild.menge
            gesamtgewicht += gewicht

    charakter.gesamtgewicht = gesamtgewicht
    return gesamtgewicht

def berechne_gesamt_ruestungsschutz(charakter):
    """
    Berechnet den Gesamtrüstungsschutz des Charakters.
    
    Args:
        charakter: Das Charakterobjekt, dessen Rüstungsschutz berechnet werden soll
        
    Returns:
        dict: Ein Dictionary mit dem Gesamtrüstungsschutz für jede Körperregion
    """
    gesamt_torso = 0
    gesamt_arme = 0
    gesamt_beine = 0
    gesamt_kopf = 0

    for ruestung in charakter.selected_allgemeine_ausruestung:
        if isinstance(ruestung, Ruestung) and ruestung.angelegt:
            gesamt_torso += ruestung.torso
            gesamt_arme += ruestung.arme
            gesamt_beine += ruestung.beine
            gesamt_kopf += ruestung.kopf

    ruestungsschutz = {
        'Torso': gesamt_torso,
        'Arme': gesamt_arme,
        'Beine': gesamt_beine,
        'Kopf': gesamt_kopf
    }
    return ruestungsschutz

def get_item_by_name(charakter, item_name):
    """
    Findet ein Ausrüstungsteil anhand des Namens.
    
    Args:
        charakter: Das Charakterobjekt, in dem gesucht werden soll
        item_name: Der Name des zu suchenden Items
        
    Returns:
        object or None: Das gefundene Item oder None wenn nicht gefunden
    """
    # Prüfen in Waffen
    for item in charakter.selected_waffen:
        if item.name == item_name:
            return item
    # Prüfen in Schilde
    for item in charakter.selected_schilde:
        if item.name == item_name:
            return item                
    # Prüfen in Rüstungen
    for item in charakter.selected_ruestungen:
        if item.name == item_name:
            return item
    # Prüfen in allgemeiner Ausrüstung
    for item in charakter.selected_allgemeine_ausruestung:
        if item.name == item_name:
            return item
    return None

def berechne_gesamtkosten(charakter):
    """
    Berechnet die Gesamtkosten der ausgewählten Ausrüstung.
    
    Args:
        charakter: Das Charakterobjekt, dessen Ausrüstungskosten berechnet werden sollen
        
    Returns:
        float: Die Gesamtkosten der Ausrüstung
    """
    gesamtkosten = 0
    for ausr in charakter.ausruestung.values():
        if ausr.ausgewaehlt:
            gesamtkosten += ausr.kosten * ausr.menge
    for waffe in charakter.waffen.values() if hasattr(charakter, 'waffen') else []:
        if waffe.ausgewaehlt:
            gesamtkosten += waffe.kosten * waffe.menge
    for ruestung in charakter.ruestungen.values() if hasattr(charakter, 'ruestungen') else []:
        if ruestung.ausgewaehlt:
            gesamtkosten += ruestung.kosten * ruestung.menge
    for schild in charakter.schilde.values() if hasattr(charakter, 'schilde') else []:
        if schild.ausgewaehlt:
            gesamtkosten += schild.kosten * schild.menge
    return gesamtkosten