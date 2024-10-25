# data/initialisiere_ausruestung.py
import logging
from kivy.logger import Logger

from models.ausruestung import Ausruestung
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild

from data.ausruestung_daten import ausruestung_daten
from data.waffen_daten import waffen_daten
from data.ruestung_daten import ruestung_daten
from data.schilde_daten import schilde_daten


def initialisiere_allgemeine_ausruestung():
    ausruestung = {}
    Logger.info("Beginne mit der Initialisierung der allgemeinen Ausrüstung.")
    for name, daten in ausruestung_daten.items():
        try:
            # Sicherstellen, dass 'Kategorie' gesetzt ist und nicht leer ist
            kategorie = daten.get('Kategorie', 'Allgemein').strip() or 'Allgemein'
            item = Ausruestung(
                name=name,
                gewicht=daten.get('Gewicht', 0),
                kosten=daten.get('Kosten', 0),
                setting=daten.get('Setting', ''),
                beschreibung=daten.get('Anmerkungen', ''),
                menge=daten.get('Menge', 0),
                ausgewaehlt=daten.get('Ausgewaehlt', False),
                aktiv=daten.get('Aktiv', True),
                kategorie=kategorie
            )
            ausruestung[name] = item
            Logger.debug(f"Allgemeine Ausrüstung initialisiert und hinzugefügt: {name} (Kategorie: {kategorie})")
        except Exception as e:
            Logger.error(f"Fehler beim Initialisieren der allgemeinen Ausrüstung '{name}': {e}")
    Logger.info("Abgeschlossen mit der Initialisierung der allgemeinen Ausrüstung.")
    return ausruestung


def initialisiere_waffen():
    ausruestung = {}
    Logger.info("Beginne mit der Initialisierung der Waffen.")
    for name, daten in waffen_daten.items():
        try:
            kategorie = daten.get('Kategorie', 'Waffe').strip() or 'Waffe'
            waffe = Waffe(
                name=name,
                gewicht=daten.get('Gewicht', 0),
                kosten=daten.get('Kosten', 0),
                setting=daten.get('Setting', ''),
                typ=daten.get('Typ', ''),
                mindeststaerke=daten.get('Mindeststärke', 'W4'),
                beschreibung=daten.get('Beschreibung', ''),
                eigenschaften=daten.get('Eigenschaften', {}),
                menge=daten.get('Menge', 0),
                ausgewaehlt=daten.get('Ausgewaehlt', False),
                aktiv=daten.get('Aktiv', True),
                kategorie=kategorie
            )
            ausruestung[name] = waffe
            Logger.debug(f"Waffe initialisiert und hinzugefügt: {name} (Kategorie: {kategorie})")
        except Exception as e:
            Logger.error(f"Fehler beim Initialisieren der Waffe '{name}': {e}")
    Logger.info("Abgeschlossen mit der Initialisierung der Waffen.")
    return ausruestung


def initialisiere_ruestungen():
    ausruestung = {}
    Logger.info("Beginne mit der Initialisierung der Rüstungen.")
    for name, daten in ruestung_daten.items():
        try:
            kategorie = daten.get('Kategorie', 'Rüstung').strip() or 'Rüstung'
            ruestung = Ruestung(
                name=name,
                torso=daten.get('Torso', 0),
                arme=daten.get('Arme', 0),
                beine=daten.get('Beine', 0),
                kopf=daten.get('Kopf', 0),
                mindeststaerke=daten.get('Mindeststärke', 'W4'),
                setting=daten.get('Setting', ''),
                gewicht=daten.get('Gewicht', 0),
                kosten=daten.get('Kosten', 0),
                beschreibung=daten.get('Anmerkungen', ''),
                menge=daten.get('Menge', 0),
                ausgewaehlt=daten.get('Ausgewaehlt', False),
                aktiv=daten.get('Aktiv', True),
                kategorie=kategorie
            )
            ausruestung[name] = ruestung
            Logger.debug(f"Rüstung initialisiert und hinzugefügt: {name} (Kategorie: {kategorie})")
        except Exception as e:
            Logger.error(f"Fehler beim Initialisieren der Rüstung '{name}': {e}")
    Logger.info("Abgeschlossen mit der Initialisierung der Rüstungen.")
    return ausruestung


def initialisiere_schilde():
    ausruestung = {}
    Logger.info("Beginne mit der Initialisierung der Schilde.")
    for name, daten in schilde_daten.items():
        try:
            kategorie = daten.get('Kategorie', 'Schild').strip() or 'Schild'
            schild = Schild(
                name=name,
                gewicht=daten.get('Gewicht', 0),
                kosten=daten.get('Kosten', 0),
                setting=daten.get('Setting', ''),
                parade=daten.get('Parade', 0),
                deckung=daten.get('Deckung', 0),
                mindeststaerke=daten.get('Mindeststärke', ''),
                beschreibung=daten.get('Anmerkungen', ''),
                menge=daten.get('Menge', 0),
                ausgewaehlt=daten.get('Ausgewaehlt', False),
                aktiv=daten.get('Aktiv', True),
                kategorie=kategorie
            )
            ausruestung[name] = schild
            Logger.debug(f"Schild initialisiert und hinzugefügt: {name} (Kategorie: {kategorie})")
        except Exception as e:
            Logger.error(f"Fehler beim Initialisieren des Schildes '{name}': {e}")
    Logger.info("Abgeschlossen mit der Initialisierung der Schilde.")
    return ausruestung


def initialisiere_ausruestung():
    ausruestung = {}
    Logger.info("Start der Ausrüstungsinitialisierung.")
    
    # Allgemeine Ausrüstung
    Logger.info("Initialisiere allgemeine Ausrüstung.")
    allgemeine_ausruestung = initialisiere_allgemeine_ausruestung()
    ausruestung.update(allgemeine_ausruestung)
    Logger.info(f"Allgemeine Ausrüstung hinzugefügt: {len(allgemeine_ausruestung)} Gegenstände.")
    
    # Waffen
    Logger.info("Initialisiere Waffen.")
    waffen = initialisiere_waffen()
    ausruestung.update(waffen)
    Logger.info(f"Waffen hinzugefügt: {len(waffen)} Gegenstände.")
    
    # Rüstungen
    Logger.info("Initialisiere Rüstungen.")
    ruestungen = initialisiere_ruestungen()
    ausruestung.update(ruestungen)
    Logger.info(f"Rüstungen hinzugefügt: {len(ruestungen)} Gegenstände.")
    
    # Schilde
    Logger.info("Initialisiere Schilde.")
    schilde = initialisiere_schilde()
    ausruestung.update(schilde)
    Logger.info(f"Schilde hinzugefügt: {len(schilde)} Gegenstände.")
    
    Logger.info(f"Gesamtanzahl der initialisierten Ausrüstungsgegenstände: {len(ausruestung)}")
    return ausruestung
