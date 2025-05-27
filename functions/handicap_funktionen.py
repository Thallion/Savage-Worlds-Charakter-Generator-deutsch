"""
Modul für die Verwaltung von Handicaps im Charakter.
Dieses Modul enthält Funktionen zur Verwaltung von Handicaps, einschließlich
des Auswahlens, Abwählens und Speicherns benutzerdefinierter Handicaps.
"""

import json
import os
from kivy.logger import Logger
from models.handicap import Handicap


def initialisiere_handicaps(charakter, handicap_daten):
    """
    Initialisiert die Handicaps des Charakters basierend auf der bereitgestellten Liste.
    
    Args:
        charakter: Das Charakter-Objekt, dem die Handicaps hinzugefügt werden sollen
        handicap_daten: Die Handicap-Daten als Liste von Dictionaries
    """
    charakter.handicaps = {}
    try:
        for daten in handicap_daten:
            name = daten.get('Name', '')
            stufe = daten.get('Stufe', '').lower()
            beschreibung = daten.get('Beschreibung', 'Keine Beschreibung verfügbar')

            # Immer ein eindeutiger Schlüssel mit Name und Stufe
            name_key = f"{name} ({stufe})"

            # Initialisiere das Handicap
            handicap = charakter.Handicap(
                name=name,  # Name ohne Stufe
                stufe=stufe,
                beschreibung=beschreibung
            )
            charakter.handicaps[name_key] = handicap
        Logger.debug("Handicaps erfolgreich initialisiert.")
    except Exception as e:
        Logger.error(f"Fehler bei der Initialisierung der Handicaps: {e}")


def waehle_handicap(charakter, handicap_name_key):
    """
    Wählt ein Handicap aus und verrechnet die Handicap-Punkte.
    
    Args:
        charakter: Das Charakter-Objekt
        handicap_name_key: Der Schlüssel des Handicaps in der handicaps-Dictionary
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if handicap_name_key in charakter.handicaps:
        handicap = charakter.handicaps[handicap_name_key]
        if not handicap.ausgewaehlt:
            neue_gesamtpunkte = charakter.gesamt_handicap_punkte + handicap.punkte     
            Logger.info(f"neue_gesamtpunkte '{neue_gesamtpunkte} Kosten: {handicap.punkte} Gesamt {charakter.gesamt_handicap_punkte}")
            if neue_gesamtpunkte <= 4:           
                handicap.auswaehlen()
                charakter.gesamt_handicap_punkte = neue_gesamtpunkte
                charakter.verbleibende_handicap_punkte += handicap.punkte  
                charakter.verbleibende_handicap_punkte = min(charakter.verbleibende_handicap_punkte, 4) 
                charakter.selected_handicaps.append(handicap_name_key)
                
                # Handicap-spezifische Effekte anwenden
                _apply_handicap_effects(charakter, handicap)
                
                Logger.info(f"Handicap '{handicap_name_key}' ausgewählt.")
                Logger.info(f"verbleibend '{charakter.verbleibende_handicap_punkte} Kosten: {handicap.punkte} Gesamt {charakter.gesamt_handicap_punkte}")
                charakter.selected_handicaps = charakter.selected_handicaps  # Neu zuweisen
                
                # Abgeleitete Werte neu berechnen
                charakter.berechne_abgeleitete_werte()
                
                return True
            else:
                handicap.auswaehlen()
                charakter.selected_handicaps.append(handicap_name_key)
                
                # Handicap-spezifische Effekte anwenden
                _apply_handicap_effects(charakter, handicap)
                
                if neue_gesamtpunkte == 5:
                    charakter.gesamt_handicap_punkte = 4
                    charakter.verbleibende_handicap_punkte += handicap.punkte 
                    charakter.verbleibende_handicap_punkte = min(charakter.verbleibende_handicap_punkte, 4)
                    Logger.info(f"verbleibend '{charakter.verbleibende_handicap_punkte} Kosten: {handicap.punkte} Gesamt {charakter.gesamt_handicap_punkte}")
                    charakter.selected_handicaps = charakter.selected_handicaps  # Neu zuweisen 
                    Logger.warning(f"Handicap '{handicap_name_key}' ausgewählt. Handicap-punkte nicht erhöht, da Maximum von 4 erreicht.")
                    Logger.info(f"Handicap '{handicap_name_key}' ausgewählt.")
                    
                    # Abgeleitete Werte neu berechnen
                    charakter.berechne_abgeleitete_werte()
                    
                    return True
                else:
                    Logger.warning(f"Handicap '{handicap_name_key}' ausgewählt. Handicap-punkte nicht erhöht, da Maximum von 4 erreicht.")
                    charakter.selected_handicaps = charakter.selected_handicaps  # Neu zuweisen  
                    Logger.info(f"Handicap '{handicap_name_key}' ausgewählt.")
                    charakter.verbleibende_handicap_punkte = min(charakter.verbleibende_handicap_punkte, 4)
                    
                    # Abgeleitete Werte neu berechnen
                    charakter.berechne_abgeleitete_werte()
                    
                    return True                  
        else:
            Logger.warning(f"Handicap '{handicap_name_key}' ist bereits ausgewählt.")
    else:
        Logger.error(f"Handicap '{handicap_name_key}' existiert nicht.")
    return False

def _apply_handicap_effects(charakter, handicap):
    """
    Wendet die Effekte eines Handicaps auf den Charakter an.
    
    Args:
        charakter: Das Charakter-Objekt
        handicap: Das Handicap-Objekt
    """
    # Alt (schwer) - Mehr Fertigkeitspunkte
    if "Alt" in handicap.name and handicap.stufe == "schwer":
        charakter.verbleibende_fertigkeitssteigerungen += 5
        charakter.maximale_fertigkeitssteigerungen += 5
        Logger.info(f"Handicap 'Alt (schwer)': +5 Fertigkeitssteigerungen")
    
    # Arm (leicht) - Halbiertes Vermögen
    elif "Arm" in handicap.name and handicap.stufe == "leicht":
        # Anstatt direkt das Vermögen zu ändern, verwenden wir die neue Funktion
        from functions.ausruestung_funktionen import anpassen_vermoegen_bei_handicap_arm
        anpassen_vermoegen_bei_handicap_arm(charakter, True)  # True = wird ausgewählt
    
    # Jung (leicht/schwer) - Anpassung der Steigerungen
    elif "Jung" in handicap.name:
        if handicap.stufe == "leicht":
            charakter.verbleibende_attributsteigerungen = 4
            charakter.maximale_attributsteigerungen = 4
            charakter.verbleibende_fertigkeitssteigerungen = 10
            charakter.maximale_fertigkeitssteigerungen = 10
            Logger.info(f"Handicap 'Jung (leicht)': Attributsteigerungen=4, Fertigkeitssteigerungen=10")
        elif handicap.stufe == "schwer":
            charakter.verbleibende_attributsteigerungen = 3
            charakter.maximale_attributsteigerungen = 3
            charakter.verbleibende_fertigkeitssteigerungen = 10
            charakter.maximale_fertigkeitssteigerungen = 10
            Logger.info(f"Handicap 'Jung (schwer)': Attributsteigerungen=3, Fertigkeitssteigerungen=10")


def entferne_handicap(charakter, handicap_name_key):
    """
    Entfernt ein Handicap. Nach der Charaktergenerierung kostet dies Aufstiege.
    Leichte Handicaps kosten 1 Aufstieg, schwere 2 Aufstiege.
    Schwere Handicaps können für 1 Aufstieg zu leichten reduziert werden.
    
    Args:
        charakter: Das Charakter-Objekt
        handicap_name_key: Der Schlüssel des Handicaps in der handicaps-Dictionary
        
    Returns:
        True bei Erfolg, False bei Misserfolg, 
        "needs_advancement_X" wenn X Aufstiege benötigt werden,
        "can_reduce" wenn das Handicap reduziert werden kann
    """
    if handicap_name_key in charakter.handicaps:
        handicap = charakter.handicaps[handicap_name_key]
        if handicap.ausgewaehlt:
            # Prüfen ob Charaktergenerierung abgeschlossen ist
            if charakter.char_gen_completed:
                # Bestimme Kosten basierend auf Handicap-Stufe
                kosten = 1 if handicap.stufe == "leicht" else 2
                
                # Prüfe ob ein leichtes Handicap mit gleichem Namen existiert
                kann_reduziert_werden = False
                if handicap.stufe == "schwer":
                    # Suche nach einem leichten Handicap mit gleichem Namen
                    leichtes_handicap_key = f"{handicap.name} (leicht)"
                    if leichtes_handicap_key in charakter.handicaps:
                        kann_reduziert_werden = True
                
                # Nach der Charaktergenerierung kostet das Entfernen Aufstiege
                if charakter.verbleibende_aufstiege >= kosten:
                    # Aufstieg abziehen
                    charakter.verbleibende_aufstiege -= kosten
                    Logger.info(f"Handicap '{handicap_name_key}' mit {kosten} Aufstieg(en) entfernt. Verbleibende Aufstiege: {charakter.verbleibende_aufstiege}")
                else:
                    # Nicht genug Aufstiege
                    if kann_reduziert_werden and charakter.verbleibende_aufstiege >= 1:
                        # Kann auf leicht reduziert werden
                        Logger.info(f"Handicap '{handicap_name_key}' kann für 1 Aufstieg auf leicht reduziert werden.")
                        return "can_reduce"
                    else:
                        Logger.warning(f"Nicht genügend Aufstiege verfügbar. Benötigt: {kosten}, Verfügbar: {charakter.verbleibende_aufstiege}")
                        return f"needs_advancement_{kosten}"
            else:
                # Während der Charaktergenerierung normale Behandlung
                charakter.gesamt_handicap_punkte -= handicap.punkte
                charakter.gesamt_handicap_punkte = max(charakter.gesamt_handicap_punkte, 0)
                charakter.verbleibende_handicap_punkte -= handicap.punkte
                charakter.verbleibende_handicap_punkte = max(charakter.verbleibende_handicap_punkte, 0)
            
            # Handicap abwählen
            handicap.abwaehlen()
            
            # Handicap-spezifische Effekte rückgängig machen
            _remove_handicap_effects(charakter, handicap)
            
            Logger.info(f"Handicap '{handicap_name_key}' entfernt.")
            if handicap_name_key in charakter.selected_handicaps:
                charakter.selected_handicaps.remove(handicap_name_key)
                charakter.selected_handicaps = charakter.selected_handicaps  # Neu zuweisen
            
            # Abgeleitete Werte neu berechnen
            charakter.berechne_abgeleitete_werte()
            
            return True
        else:
            Logger.warning(f"Handicap '{handicap_name_key}' ist nicht ausgewählt.")
    else:
        Logger.error(f"Handicap '{handicap_name_key}' existiert nicht.")
    return False


def reduziere_handicap(charakter, handicap_name_key):
    """
    Reduziert ein schweres Handicap zu einem leichten Handicap.
    Kostet 1 Aufstieg nach der Charaktergenerierung.
    
    Args:
        charakter: Das Charakter-Objekt
        handicap_name_key: Der Schlüssel des schweren Handicaps
        
    Returns:
        True bei Erfolg, False bei Misserfolg, "needs_advancement" wenn Aufstieg fehlt
    """
    if handicap_name_key not in charakter.handicaps:
        Logger.error(f"Handicap '{handicap_name_key}' existiert nicht.")
        return False
        
    handicap = charakter.handicaps[handicap_name_key]
    
    if not handicap.ausgewaehlt:
        Logger.warning(f"Handicap '{handicap_name_key}' ist nicht ausgewählt.")
        return False
        
    if handicap.stufe != "schwer":
        Logger.warning(f"Handicap '{handicap_name_key}' ist nicht schwer und kann nicht reduziert werden.")
        return False
    
    # Prüfe ob leichtes Handicap existiert
    leichtes_handicap_key = f"{handicap.name} (leicht)"
    if leichtes_handicap_key not in charakter.handicaps:
        Logger.error(f"Kein leichtes Handicap '{leichtes_handicap_key}' gefunden.")
        return False
    
    leichtes_handicap = charakter.handicaps[leichtes_handicap_key]
    
    # Nach Charaktergenerierung kostet es 1 Aufstieg
    if charakter.char_gen_completed:
        if charakter.verbleibende_aufstiege < 1:
            Logger.warning("Nicht genügend Aufstiege für Handicap-Reduzierung.")
            return "needs_advancement"
        charakter.verbleibende_aufstiege -= 1
    else:
        # Während der Charaktergenerierung: Punkte anpassen
        # Schweres Handicap gibt 2 Punkte, leichtes 1 Punkt
        # Differenz = 1 Punkt weniger
        charakter.gesamt_handicap_punkte -= 1
        charakter.gesamt_handicap_punkte = max(charakter.gesamt_handicap_punkte, 0)
        charakter.verbleibende_handicap_punkte -= 1
        charakter.verbleibende_handicap_punkte = max(charakter.verbleibende_handicap_punkte, 0)
    
    # Schweres Handicap entfernen
    handicap.abwaehlen()
    _remove_handicap_effects(charakter, handicap)
    if handicap_name_key in charakter.selected_handicaps:
        charakter.selected_handicaps.remove(handicap_name_key)
    
    # Leichtes Handicap aktivieren
    leichtes_handicap.auswaehlen()
    _apply_handicap_effects(charakter, leichtes_handicap)
    if leichtes_handicap_key not in charakter.selected_handicaps:
        charakter.selected_handicaps.append(leichtes_handicap_key)
    
    # Listen neu zuweisen für UI-Update
    charakter.selected_handicaps = charakter.selected_handicaps
    
    # Abgeleitete Werte neu berechnen
    charakter.berechne_abgeleitete_werte()
    
    Logger.info(f"Handicap '{handicap.name}' von schwer auf leicht reduziert.")
    
    return True


def _remove_handicap_effects(charakter, handicap):
    """
    Macht die Effekte eines Handicaps rückgängig.
    
    Args:
        charakter: Das Charakter-Objekt
        handicap: Das Handicap-Objekt
    """
    # Alt (schwer) - Mehr Fertigkeitspunkte
    if "Alt" in handicap.name and handicap.stufe == "schwer":
        charakter.verbleibende_fertigkeitssteigerungen -= 5
        charakter.maximale_fertigkeitssteigerungen -= 5
        charakter.verbleibende_fertigkeitssteigerungen = max(charakter.verbleibende_fertigkeitssteigerungen, 0)
        Logger.info(f"Handicap 'Alt (schwer)' entfernt: -5 Fertigkeitssteigerungen")
    
    # Arm (leicht) - Halbiertes Vermögen
    elif "Arm" in handicap.name and handicap.stufe == "leicht":
        # Anstatt direkt das Vermögen zu ändern, verwenden wir die neue Funktion
        from functions.ausruestung_funktionen import anpassen_vermoegen_bei_handicap_arm
        anpassen_vermoegen_bei_handicap_arm(charakter, False)  # False = wird abgewählt
    
    # Jung (leicht/schwer) - Anpassung der Steigerungen
    elif "Jung" in handicap.name:
        # Zurück zu den Standardwerten
        charakter.verbleibende_attributsteigerungen = 5
        charakter.maximale_attributsteigerungen = 5
        charakter.verbleibende_fertigkeitssteigerungen = 12
        charakter.maximale_fertigkeitssteigerungen = 12
        Logger.info(f"Handicap 'Jung' entfernt: Steigerungen auf Standardwerte zurückgesetzt")

def aktive_handicaps(charakter):
    """
    Gibt eine Liste aller aktiven Handicaps zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der aktiven Handicaps
    """
    return [handicap for handicap in charakter.handicaps.values() if handicap.aktiv]


def ausgewaehlte_handicaps(charakter):
    """
    Gibt eine Liste aller ausgewählten Handicaps zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der ausgewählten Handicaps
    """
    return [handicap for handicap in charakter.handicaps.values() if handicap.ausgewaehlt]


def add_handicap(charakter, handicap):
    """
    Fügt ein neues Handicap hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
        handicap: Das hinzuzufügende Handicap-Objekt
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if handicap.name in charakter.handicaps:
        Logger.warning(f"Handicap '{handicap.name}' existiert bereits.")
        return False
    charakter.handicaps[handicap.name] = handicap
    Logger.info(f"Handicap '{handicap.name}' hinzugefügt.")
    save_custom_handicaps(charakter)
    return True


def remove_handicap(charakter, handicap_name):
    """
    Entfernt ein Handicap vollständig aus der Liste (nicht nur abwählen).
    
    Args:
        charakter: Das Charakter-Objekt
        handicap_name: Der Name des zu entfernenden Handicaps
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if handicap_name in charakter.handicaps:
        del charakter.handicaps[handicap_name]
        Logger.info(f"Handicap '{handicap_name}' entfernt.")
        save_custom_handicaps(charakter)
        return True
    Logger.warning(f"Handicap '{handicap_name}' existiert nicht.")
    return False


def save_custom_handicaps(charakter):
    """
    Speichert die benutzerdefinierten Handicaps in einer JSON-Datei.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    # Finde die benutzerdefinierten Handicaps
    custom_handicaps = {
        name: handicap.to_dict()
        for name, handicap in charakter.handicaps.items()
        if getattr(handicap, 'custom', False)
    }
    if custom_handicaps:
        custom_handicaps_file = os.path.join(os.path.dirname(__file__), 'custom_handicaps.json')
        try:
            with open(custom_handicaps_file, 'w', encoding='utf-8') as f:
                json.dump(custom_handicaps, f, ensure_ascii=False, indent=4)
            Logger.info(f"Benutzerdefinierte Handicaps wurden in {custom_handicaps_file} gespeichert.")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der benutzerdefinierten Handicaps: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Handicaps zum Speichern.")


def load_custom_handicaps(charakter):
    """
    Lädt die benutzerdefinierten Handicaps aus einer JSON-Datei und fügt sie der Handicaps-Liste hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    custom_handicaps_file = os.path.join(os.path.dirname(__file__), 'custom_handicaps.json')
    if os.path.exists(custom_handicaps_file):
        try:
            with open(custom_handicaps_file, 'r', encoding='utf-8') as f:
                custom_handicaps_data = json.load(f)
            for name, data in custom_handicaps_data.items():
                handicap = Handicap.from_dict_static(data)
                if handicap:
                    charakter.handicaps[name] = handicap
            Logger.info(f"Benutzerdefinierte Handicaps wurden aus {custom_handicaps_file} geladen.")
        except Exception as e:
            Logger.error(f"Fehler beim Laden der benutzerdefinierten Handicaps: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Handicaps zum Laden gefunden.")