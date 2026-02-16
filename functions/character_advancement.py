# functions/character_advancement.py

from kivy.logger import Logger

def update_rang(charakter):
    """
    Aktualisiert den Rang basierend auf den Gesamtaufstiegen.
    
    Args:
        charakter: Das Charakterobjekt, dessen Rang aktualisiert werden soll
    """
    charakter.rang = get_rang(charakter, charakter.aufstiege_gesamt)
    Logger.info(f"Rang aktualisiert: {charakter.rang} (Aufstiege gesamt: {charakter.aufstiege_gesamt})")

def get_rang(charakter, aufstiege_gesamt):
    """
    Bestimmt den Rang basierend auf den Gesamtaufstiegen.
    
    Args:
        charakter: Das Charakterobjekt
        aufstiege_gesamt: Die Anzahl der Gesamtaufstiege
        
    Returns:
        str: Die Bezeichnung des Ranges
    """
    for min_val, max_val, rank_name, rank_num in charakter.rang_mapping:
        if min_val <= aufstiege_gesamt < max_val:
            return rank_name
    return "Unbekannter Rang"

def steigere_attribut(charakter, attribut_name):
    """
    Steigert ein Attribut und zieht entsprechende Kosten ab.
    
    Args:
        charakter: Das Charakterobjekt
        attribut_name: Der Name des zu steigernden Attributs
        
    Returns:
        bool: True bei Erfolg, False bei Fehlschlag
    """
    Logger.debug(f"Steigere Attribut '{attribut_name}'")

    kosten = 1
    Logger.debug(f"Kosten für das Steigern des Attributs: {kosten}")

    Logger.debug(f"Charaktergenerierung abgeschlossen: {charakter.char_gen_completed}")

    def steigern():
        attribut = charakter.attribute.get(attribut_name)
        if attribut:
            attribut.wuerfel.increase()
            Logger.debug(f"Attribut '{attribut_name}' gesteigert auf W{attribut.wuerfel.value}+{attribut.wuerfel.modifier}")
            charakter.update_char_gen_status()  # Aktualisiere den Status
            charakter.rang = get_rang(charakter, charakter.aufstiege_gesamt)
            return True
        else:
            Logger.warning(f"Attribut '{attribut_name}' nicht gefunden im Charakterobjekt mit ID {id(charakter)}.")
            return False

    if charakter.char_gen_completed:
        if charakter.verbleibende_aufstiege >= kosten:
            charakter.verbleibende_aufstiege -= kosten
            charakter.verbleibende_aufstiege = max(charakter.verbleibende_aufstiege, 0)  # Sicherstellen, dass nicht negativ
            return steigern()  # Rückgabe des steigern() Ergebnisses
        else:
            Logger.debug("Nicht genügend `verbleibende_aufstiege`. Wechsel zu `verbleibende_attributsteigerungen`.")
            return False
    else:
        if charakter.verbleibende_attributsteigerungen > 0:
            charakter.verbleibende_attributsteigerungen -= kosten
            charakter.verbleibende_attributsteigerungen = max(charakter.verbleibende_attributsteigerungen, 0)  # Sicherstellen, dass nicht negativ
            return steigern()  # Rückgabe des steigern() Ergebnisses
        else:
            if charakter.verbleibende_handicap_punkte > 1.5:
                success = steigern()
                if success:
                    charakter.verbleibende_handicap_punkte -= 2
                    Logger.info("Attribut mit Handicap-Punkten gesteigert.")
                    return True
                else:
                    return False
            else:
                Logger.warning("Keine Attributsteigerungen mehr verfügbar.")
                return False

def senke_attribut(charakter, attribut_name):
    """
    Senkt ein Attribut und gibt entsprechende Punkte zurück.
    
    Args:
        charakter: Das Charakterobjekt
        attribut_name: Der Name des zu senkenden Attributs
        
    Returns:
        bool: True bei Erfolg, False bei Fehlschlag
    """
    Logger.debug(f"Senke Attribut '{attribut_name}'")

    kosten = 1
    Logger.debug(f"Gutschrift für das Senken des Attributs: {kosten}")

    Logger.debug(f"Charaktergenerierung abgeschlossen: {charakter.char_gen_completed}")

    def senken():
        attribut = charakter.attribute.get(attribut_name)
        if attribut:
            attribut.wuerfel.decrease()
            Logger.debug(f"Attribut '{attribut_name}' gesenkt auf W{attribut.wuerfel.value}+{attribut.wuerfel.modifier}")
            charakter.update_char_gen_status()  # Aktualisiere den Status
            charakter.rang = get_rang(charakter, charakter.aufstiege_gesamt)
        else:
            Logger.warning(f"Attribut '{attribut_name}' nicht gefunden im Charakterobjekt mit ID {id(charakter)}.")
        return False

    if charakter.char_gen_completed:
        if charakter.verbleibende_aufstiege < charakter.aufstiege_gesamt:
            charakter.verbleibende_aufstiege += 1
            senken()  # Direkter Aufruf der inneren Funktion
        else:
            Logger.debug("Maximum Aufstiege erreicht.")
            return False
    else:
        if charakter.verbleibende_handicap_punkte < charakter.gesamt_handicap_punkte:
            charakter.verbleibende_handicap_punkte += kosten                
            senken()
        else:
            if charakter.verbleibende_attributsteigerungen < charakter.maximale_attributsteigerungen:
                charakter.verbleibende_attributsteigerungen += kosten
                senken()  # Direkter Aufruf der inneren Funktion
            else:
                Logger.warning("Maximum Attributspunkte erreicht.")
                return False

def increase_aufstiege(charakter):
    """
    Erhöht die Aufstiege des Charakters.
    
    Args:
        charakter: Das Charakterobjekt, dessen Aufstiege erhöht werden sollen
    """
    charakter.aufstiege_gesamt += 1
    charakter.verbleibende_aufstiege += 1
    Logger.debug(f"Aufstiege erhöht: Aufstiege gesamt = {charakter.aufstiege_gesamt}, Verbleibende Aufstiege = {charakter.verbleibende_aufstiege}")
    # Rang neu setzen und speichern
    charakter.rang = get_rang(charakter, charakter.aufstiege_gesamt)

def erhoehe_startkapital(charakter):
    """
    Erhöht das Startkapital des Charakters um das Setting-spezifische Startgeld.
    
    Args:
        charakter: Das Charakterobjekt, dessen Startkapital erhöht werden soll
    """
    if charakter.verbleibende_handicap_punkte > 0:
        # Setting-spezifisches Startgeld ermitteln
        setting_startgeld = _get_setting_startgeld(charakter)
        charakter.vermoegen += setting_startgeld
        charakter.verbleibende_handicap_punkte -= 1
        Logger.info(f"Startkapital um {setting_startgeld} erhöht. Neues Vermögen: {charakter.vermoegen}")
    else:
        Logger.warning("Keine Handicap-Punkte mehr verfügbar.")


def _get_setting_startgeld(charakter):
    """
    Ermittelt das Setting-spezifische Startgeld.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        int: Das Startgeld aus dem aktiven Setting oder Default-Wert
    """
    try:
        # Aktives Setting abrufen
        if hasattr(charakter, 'custom_element_manager') and charakter.custom_element_manager:
            active_setting = charakter.custom_element_manager.get_active_setting()
            if active_setting and 'startgeld' in active_setting:
                setting_startgeld = active_setting['startgeld']
                Logger.debug(f"Setting-spezifisches Startgeld gefunden: {setting_startgeld}")
                return setting_startgeld
        
        # Fallback auf Default-Wert aus Charakter oder Standard
        default_startgeld = getattr(charakter, 'startkapital', 500)
        Logger.debug(f"Verwende Default-Startgeld: {default_startgeld}")
        return default_startgeld
        
    except Exception as e:
        Logger.warning(f"Fehler beim Ermitteln des Setting-Startgelds: {e}")
        # Sicherheits-Fallback
        return 500


def decrease_aufstiege(charakter):
    """
    Verringert die Aufstiege des Charakters.
    
    Args:
        charakter: Das Charakterobjekt, dessen Aufstiege verringert werden sollen
    """
    charakter.aufstiege_gesamt -= 1
    charakter.aufstiege_gesamt = max(charakter.aufstiege_gesamt, 0)  # Sicherstellen, dass nicht negativ
    charakter.verbleibende_aufstiege -= 1
    charakter.verbleibende_aufstiege = max(charakter.verbleibende_aufstiege, 0)  # Sicherstellen, dass nicht negativ
    Logger.debug(f"Aufstiege verringert: Aufstiege gesamt = {charakter.aufstiege_gesamt}, Verbleibende Aufstiege = {charakter.verbleibende_aufstiege}")
    # Rang neu setzen und speichern
    charakter.rang = get_rang(charakter, charakter.aufstiege_gesamt)