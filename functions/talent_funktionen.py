"""
Modul für die Verwaltung von Talenten im Charakter.
Dieses Modul enthält Funktionen zur Verwaltung von Talenten, einschließlich
des Auswahlens, Abwählens und Überprüfens der Voraussetzungen.
"""

from kivy.logger import Logger
from models.talent import Talent
from functions.macht_funktionen import entferne_macht


def initialisiere_talente(charakter, talent_daten):
    """
    Initialisiert die Talente des Charakters basierend auf der bereitgestellten Liste.
    
    Args:
        charakter: Das Charakter-Objekt, dem die Talente hinzugefügt werden sollen
        talent_daten: Die Talent-Daten als Dictionary
    """
    try:
        for kategorie, talente in talent_daten.items():
            for name, daten in talente.items():
                talent = charakter.Talent(
                    name=name,
                    kategorie=kategorie,
                    rang=daten.get('Rang', ''),
                    voraussetzungen=daten.get('Voraussetzungen', []),
                    beschreibung=daten.get('Beschreibung', ''),
                    neue_maechte=daten.get('neue_maechte', 0),
                    machtpunkte=daten.get('machtpunkte', 0)
                )
                charakter.talente[name] = talent
    except Exception as e:
        Logger.error(f"Fehler bei der Initialisierung der Talente: {e}")


def ausgewaehlte_talente(charakter):
    """
    Gibt eine Liste aller ausgewählten Talente zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der ausgewählten Talente
    """
    return [talent for talent in charakter.talente.values() if talent.ausgewaehlt]


def aktive_talente(charakter):
    """
    Gibt eine Liste aller aktiven Talente zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der aktiven Talente
    """
    return [talent for talent in charakter.talente.values() if talent.aktiv]


def get_freie_talente(charakter):
    """
    Gibt eine Liste von Talenten zurück, die als freie Talente ausgewählt werden können.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Liste der Namen von freien Talenten
    """
    frei_talente = []
    for talent in charakter.talente.values():
        if not talent.ausgewaehlt and talent.aktiv:
            frei_talente.append(talent.name)
    # Füge einen Platzhalter hinzu, falls keine freien Talente verfügbar sind
    if not frei_talente:
        frei_talente = ['Keine freien Talente verfügbar']
    return frei_talente


def talent_auswaehlen(charakter, talent_name_key):
    """
    Wählt ein Talent aus und führt die entsprechenden Anpassungen am Charakter durch.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name_key: Der Name des auszuwählenden Talents
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    talent = charakter.talente.get(talent_name_key)
    if talent:
        if not talent.ausgewaehlt:
            if talent.voraussetzungen_erfuellt(charakter):
                talent.auswaehlen(charakter)
                charakter.verfuegbare_maechte += talent.neue_maechte
                charakter.erhoehe_machtpunkte(talent.machtpunkte)
                charakter.selected_talente.append(talent_name_key)
                Logger.info(f"Talent '{talent_name_key}' ausgewählt.")
                return True
            else:
                Logger.warning(f"Voraussetzungen für Talent '{talent_name_key}' nicht erfüllt.")
        else:
            Logger.warning(f"Talent '{talent_name_key}' ist bereits ausgewählt.")
    else:
        Logger.error(f"Talent '{talent_name_key}' existiert nicht.")
    return False


def is_talent_rang_hoeher_als_charakter(charakter, talent_rang):
    """
    Prüft, ob der Rang des Talents höher ist als der des Charakters.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_rang: Der Rang des Talents als String
        
    Returns:
        bool: True, wenn der Talent-Rang höher ist, sonst False
    """
    # Verbesserte Rangordnung mit verschiedenen Schreibweisen
    rang_werte = {
        # Vollständige Namen (Kleinbuchstaben)
        "anfänger": 1,
        "fortgeschritten": 2, 
        "veteran": 3,
        "heroisch": 4,
        "legendär": 5,
        
        # Abkürzungen
        "a": 1,
        "f": 2,
        "v": 3, 
        "h": 4,
        "l": 5,
        
        # Englische Bezeichnungen (falls verwendet)
        "novice": 1,
        "seasoned": 2,
        "veteran": 3,
        "heroic": 4,
        "legendary": 5
    }
    
    # Debug-Ausgaben für bessere Fehlerdiagnose
    Logger.debug(f"Rangprüfung - Charakter-Rang: '{charakter.rang}', Talent-Rang: '{talent_rang}'")
    
    # Normalisieren und besser extrahieren
    # 1. Auf Kleinbuchstaben konvertieren
    # 2. Nur den ersten Buchstaben verwenden, wenn keine Übereinstimmung gefunden wird
    charakter_rang = charakter.rang.lower()
    talent_rang = talent_rang.lower() if talent_rang else "a"  # Fallback auf Anfänger
    
    # Rang-Werte abrufen
    charakter_rang_wert = rang_werte.get(charakter_rang, -1)
    talent_rang_wert = rang_werte.get(talent_rang, -1)
    
    # Wenn keine direkte Übereinstimmung, versuche ersten Buchstaben
    if charakter_rang_wert == -1:
        charakter_rang_wert = rang_werte.get(charakter_rang[0] if charakter_rang else "a", 1)
        
    if talent_rang_wert == -1:
        talent_rang_wert = rang_werte.get(talent_rang[0] if talent_rang else "a", 1)
    
    # Debug-Ausgaben der numerischen Werte
    Logger.debug(f"Rangprüfung - Charakter-Wert: {charakter_rang_wert}, Talent-Wert: {talent_rang_wert}")
    
    # Vergleich durchführen und Ergebnis loggen
    is_higher = talent_rang_wert > charakter_rang_wert
    Logger.debug(f"Rangprüfung - Ergebnis: {is_higher} (Talent-Rang {'>' if is_higher else '<='} Charakter-Rang)")
    
    return is_higher


def waehle_talent(charakter, talent_name_key, ignore_rang_check=False):
    """
    Wählt ein Talent aus und verrechnet die Kosten entweder mit Handicap-Punkten oder Aufstiegen.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name_key: Der Name des auszuwählenden Talents
        ignore_rang_check: Flag, um die Rang-Prüfung zu überspringen (für UI-Bestätigung)
        
    Returns:
        str oder bool: "needs_rang_confirmation" wenn der Rang zu niedrig ist,
                       True bei Erfolg, False bei Misserfolg
    """
    # Prüfen, ob das Talent existiert
    if talent_name_key not in charakter.talente:
        Logger.error(f"Talent '{talent_name_key}' existiert nicht.")
        return False
        
    talent = charakter.talente[talent_name_key]
    
    # Rang-Prüfung
    if not ignore_rang_check and is_talent_rang_hoeher_als_charakter(charakter, talent.rang):
        return "needs_rang_confirmation"
    
    if charakter.verbleibende_handicap_punkte > 1.5:
        erfolg = talent_auswaehlen(charakter, talent_name_key)
        if erfolg:
            charakter.verbleibende_handicap_punkte -= 2
            return True
    else:
        if charakter.verbleibende_aufstiege > 0:
            erfolg = talent_auswaehlen(charakter, talent_name_key)
            if erfolg:
                charakter.verbleibende_aufstiege -= 1
                charakter.update_char_gen_status()
                return True
        else:    
            Logger.warning(f"Keine verbleibenden Aufstiege übrig.")
    return False

def entferne_talent(charakter, talent_name_key):
    """
    Entfernt ein ausgewähltes Talent und führt die entsprechenden Anpassungen am Charakter durch.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name_key: Der Name des zu entfernenden Talents
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    def talent_abwaehlen():
        talent.abwaehlen(charakter)
        charakter.verfuegbare_maechte -= talent.neue_maechte
        charakter.verfuegbare_maechte = max(charakter.verfuegbare_maechte, 0)  # Nicht negativ
        charakter.senke_machtpunkte(talent.machtpunkte)
        if talent_name_key in charakter.selected_talente:
            charakter.selected_talente.remove(talent_name_key)
        Logger.debug(f"Talent '{talent_name_key}' entfernt.")
        
        # Wenn der Arkane Hintergrund abgewählt wird, müssen auch alle Mächte abgewählt werden
        if talent.neue_maechte > 0:
            # Kopie der Liste erstellen, da sich diese während der Iteration ändert
            selected_maechte_copy = charakter.selected_maechte.copy()
            for macht_name in selected_maechte_copy:
                # Jede Macht abwählen ohne verfuegbare_maechte anzupassen
                entferne_macht(charakter, macht_name, adjust_verfuegbare_maechte=False)
            Logger.info(f"Alle Mächte durch Abwahl des Arkanen Hintergrunds '{talent_name_key}' entfernt.")
        
        return True

    if talent_name_key in charakter.talente:
        talent = charakter.talente[talent_name_key]
        Logger.info(f"talent ausgewaehlt {talent.ausgewaehlt}")
        if talent.ausgewaehlt:
            if charakter.char_gen_completed:
                talent_abwaehlen()
                charakter.verbleibende_aufstiege += 1  # Rückerstattung der Aufstiegs-Punkte                    
                charakter.update_char_gen_status()  # Aktualisiere den Status
                return True
            else:
                talent_abwaehlen() 
                charakter.verbleibende_handicap_punkte += 2
                # Nicht mehr als 4 Handicap-Punkte
                charakter.verbleibende_handicap_punkte = min(charakter.verbleibende_handicap_punkte, 4)
                return True                                  
        else:
            Logger.warning(f"Talent '{talent_name_key}' ist nicht ausgewählt.")
    else:
        Logger.error(f"Talent '{talent_name_key}' existiert nicht.")  
    return False        


def add_talent(charakter, talent):
    """
    Fügt ein Talent zur aktiven Einstellung hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
        talent: Das hinzuzufügende Talent-Objekt
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    charakter.talente[talent.name] = talent
    charakter.custom_element_manager.update_element('talente', talent.name, talent.to_dict())
    return True


def remove_talent(charakter, talent_name):
    """
    Entfernt ein Talent aus der aktiven Einstellung.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name: Der Name des zu entfernenden Talents
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if talent_name in charakter.talente:
        del charakter.talente[talent_name]
        charakter.custom_element_manager.remove_element('talente', talent_name)
        return True
    return False


def save_custom_talents(charakter):
    """
    Speichert die benutzerdefinierten Talente in einer JSON-Datei.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    import json
    import os
    
    # Finde die benutzerdefinierten Talente
    custom_talente = {name: talent.to_dict() for name, talent in charakter.talente.items() if getattr(talent, 'custom', False)}
    if custom_talente:
        custom_talente_file = os.path.join(os.path.dirname(__file__), 'custom_talente.json')
        try:
            with open(custom_talente_file, 'w', encoding='utf-8') as f:
                json.dump(custom_talente, f, ensure_ascii=False, indent=4)
            Logger.info(f"Benutzerdefinierte Talente wurden in {custom_talente_file} gespeichert.")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der benutzerdefinierten Talente: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Talente zum Speichern.")


def load_custom_talents(charakter):
    """
    Lädt die benutzerdefinierten Talente aus einer JSON-Datei und fügt sie der Talentliste hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    import json
    import os
    
    custom_talente_file = os.path.join(os.path.dirname(__file__), 'custom_talente.json')
    if os.path.exists(custom_talente_file):
        try:
            with open(custom_talente_file, 'r', encoding='utf-8') as f:
                custom_talents_data = json.load(f)
            for name, data in custom_talents_data.items():
                talent = Talent.from_dict_static(data)
                charakter.talente[name] = talent
            Logger.info(f"Benutzerdefinierte Talente wurden aus {custom_talente_file} geladen.")
        except Exception as e:
            Logger.error(f"Fehler beim Laden der benutzerdefinierten Talente: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Talente zum Laden gefunden.")