# functions/volk_funktionen.py
"""
Volk-Funktionen zur Trennung von Geschäftslogik und UI.
Enthält alle Volk-spezifischen Operationen und Berechnungen.
"""

import logging
from kivy.logger import Logger

# Konstanten
DEFAULT_TALENT_TEXT = 'Wähle ein freies Talent'
DEFAULT_ATTRIBUT_TEXT = 'Wähle ein Attribut'  
DEFAULT_FERTIGKEIT_TEXT = 'Wähle eine Fertigkeit'
NO_TALENT_AVAILABLE_TEXT = 'Keine freien Talente verfügbar'
NO_ATTRIBUT_AVAILABLE_TEXT = 'Keine Attribute verfügbar'
NO_FERTIGKEIT_AVAILABLE_TEXT = 'Keine Fertigkeiten verfügbar'


def waehle_volk(charakter, volk_name):
    """
    Wählt ein Volk für den Charakter aus und wendet alle Effekte an.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des zu wählenden Volks
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.info(f"=== Wähle Volk '{volk_name}' für Charakter ===")
        
        # Prüfen ob Volk existiert
        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            Logger.error(f"Volk '{volk_name}' nicht gefunden")
            return False
        
        # Sicherstellen, dass voelker_selected existiert und aktuell ist
        if not hasattr(charakter, 'voelker_selected'):
            charakter.voelker_selected = {}
        
        # Verwaiste Einträge aus voelker_selected entfernen
        _cleanup_voelker_selected(charakter)
            
        # Vorheriges Volk abwählen und Effekte entfernen
        altes_volk = get_selected_volk(charakter)
        if altes_volk:
            Logger.info(f"Entferne Effekte von vorherigem Volk: {altes_volk.name}")
            altes_volk.remove_effects_from_charakter(charakter)
            altes_volk.ausgewaehlt = False
            charakter.voelker_selected[altes_volk.name] = False
        
        # Alle anderen Völker abwählen (nur die, die auch existieren)
        for name in list(charakter.voelker_selected.keys()):  # Liste erstellen um während Iteration zu ändern
            if name != volk_name:
                charakter.voelker_selected[name] = False
                # Nur abwählen wenn das Volk auch existiert
                if name in charakter.voelker:
                    charakter.voelker[name].ausgewaehlt = False
                else:
                    Logger.warning(f"Volk '{name}' in voelker_selected aber nicht in voelker - entferne verwaisten Eintrag")
                    del charakter.voelker_selected[name]
        
        # Neues Volk auswählen
        neues_volk = charakter.voelker[volk_name]
        neues_volk.ausgewaehlt = True
        charakter.voelker_selected[volk_name] = True
        
        # Volk-Effekte anwenden
        Logger.info(f"Wende Effekte von neuem Volk an: {volk_name}")
        success = neues_volk.apply_effects_to_charakter(charakter)
        
        if success:
            # Abgeleitete Werte neu berechnen
            if hasattr(charakter, 'berechne_abgeleitete_werte'):
                charakter.berechne_abgeleitete_werte()
            
            Logger.info(f"Volk '{volk_name}' erfolgreich ausgewählt")
            return True
        else:
            Logger.error(f"Fehler beim Anwenden der Volk-Effekte für '{volk_name}'")
            return False
            
    except Exception as e:
        Logger.error(f"Fehler bei Volk-Auswahl '{volk_name}': {e}", exc_info=True)
        return False


def _cleanup_voelker_selected(charakter):
    """
    Bereinigt verwaiste Einträge in voelker_selected.
    Entfernt Völker die nicht mehr in voelker existieren.
    
    Args:
        charakter: Das Charakterobjekt
    """
    try:
        if not hasattr(charakter, 'voelker_selected') or not hasattr(charakter, 'voelker'):
            return
        
        # Verwaiste Einträge finden
        verwaiste_eintraege = []
        for volk_name in charakter.voelker_selected:
            if volk_name not in charakter.voelker:
                verwaiste_eintraege.append(volk_name)
        
        # Verwaiste Einträge entfernen
        for volk_name in verwaiste_eintraege:
            Logger.warning(f"Entferne verwaisten voelker_selected Eintrag: '{volk_name}'")
            del charakter.voelker_selected[volk_name]
        
        # Fehlende Einträge hinzufügen
        for volk_name in charakter.voelker:
            if volk_name not in charakter.voelker_selected:
                charakter.voelker_selected[volk_name] = False
                Logger.debug(f"Füge fehlenden voelker_selected Eintrag hinzu: '{volk_name}'")
        
    except Exception as e:
        Logger.error(f"Fehler bei voelker_selected Bereinigung: {e}")


def abwaehlen_volk(charakter, volk_name):
    """
    Wählt ein Volk ab und entfernt alle Effekte.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des abzuwählenden Volks
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.info(f"=== Wähle Volk '{volk_name}' ab ===")
        
        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            Logger.error(f"Volk '{volk_name}' nicht gefunden")
            return False
        
        # Bereinigung durchführen
        _cleanup_voelker_selected(charakter)
            
        volk = charakter.voelker[volk_name]
        
        # Effekte entfernen
        success = volk.remove_effects_from_charakter(charakter)
        
        if success:
            # Volk abwählen
            volk.ausgewaehlt = False
            charakter.voelker_selected[volk_name] = False
            
            # Abgeleitete Werte neu berechnen
            if hasattr(charakter, 'berechne_abgeleitete_werte'):
                charakter.berechne_abgeleitete_werte()
            
            Logger.info(f"Volk '{volk_name}' erfolgreich abgewählt")
            return True
        else:
            Logger.error(f"Fehler beim Entfernen der Volk-Effekte für '{volk_name}'")
            return False
            
    except Exception as e:
        Logger.error(f"Fehler beim Abwählen von Volk '{volk_name}': {e}", exc_info=True)
        return False


def get_selected_volk(charakter):
    """
    Gibt das aktuell ausgewählte Volk zurück.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        Volk oder None: Das ausgewählte Volk oder None
    """
    try:
        if not hasattr(charakter, 'voelker_selected') or not hasattr(charakter, 'voelker'):
            return None
        
        # Bereinigung durchführen
        _cleanup_voelker_selected(charakter)
            
        for volk_name, ist_ausgewaehlt in charakter.voelker_selected.items():
            if ist_ausgewaehlt and volk_name in charakter.voelker:
                return charakter.voelker[volk_name]
                
        return None
        
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen des ausgewählten Volks: {e}")
        return None


def hat_volk_wahlmoeglichkeit(charakter, volk_name, wahlmoeglichkeit_typ):
    """
    Prüft ob ein Volk eine bestimmte Wahlmöglichkeit hat.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        wahlmoeglichkeit_typ: Typ der Wahlmöglichkeit ('freies_talent', 'freies_attribut', etc.)
        
    Returns:
        bool: True wenn Wahlmöglichkeit vorhanden
    """
    try:
        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            Logger.warning(f"Volk '{volk_name}' nicht gefunden bei Wahlmöglichkeits-Prüfung")
            return False
        
        # Bereinigung durchführen
        _cleanup_voelker_selected(charakter)
            
        volk = charakter.voelker[volk_name]
        
        # Spezifische Völker-Wahlmöglichkeiten prüfen
        if wahlmoeglichkeit_typ == 'freies_attribut':
            # Halborks haben immer Attribut-Wahlmöglichkeiten (Stärke oder Konstitution)
            if volk_name.lower() in ["halbork", "halborks"]:
                Logger.debug(f"Halbork-Spezialbehandlung: freies Attribut für '{volk_name}'")
                return True
            
            # Halbelfen haben oft freie Attribut-Wahlmöglichkeiten
            if volk_name.lower() in ["halbelf", "halbelfen"]:
                Logger.debug(f"Halbelf-Spezialbehandlung: freies Attribut für '{volk_name}'")
                return True
        
        # Direkte Prüfung über Volk-Methode
        if hasattr(volk, 'has_wahlmoeglichkeit'):
            return volk.has_wahlmoeglichkeit(wahlmoeglichkeit_typ)
        
        # Fallback: Prüfung über effects
        if hasattr(volk, 'effects'):
            return volk.effects.get('wahlmoeglichkeiten', {}).get(wahlmoeglichkeit_typ, False)
        
        # Spezialbehandlung für Menschen (freies Anfängertalent)
        if wahlmoeglichkeit_typ in ['freies_talent', 'freies_anfaengertalent']:
            if volk_name.lower() in ["mensch", "menschen", "human"]:
                Logger.debug(f"Menschen-Spezialbehandlung: freies Talent für '{volk_name}'")
                return True
        
        return False
        
    except Exception as e:
        Logger.error(f"Fehler bei Wahlmöglichkeits-Prüfung für '{volk_name}': {e}")
        return False


def get_freie_talente(charakter):
    """
    Gibt eine Liste aller verfügbaren freien Talente zurück.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        list: Liste der verfügbaren Talente
    """
    try:
        if not hasattr(charakter, 'talente') or not charakter.talente:
            Logger.warning("Keine Talente im Charakter gefunden")
            return [NO_TALENT_AVAILABLE_TEXT]
        
        frei_talente = []
        
        Logger.debug(f"Analysiere {len(charakter.talente)} Talente")
        
        for name, talent in charakter.talente.items():
            # Talent-Status prüfen
            aktiv = getattr(talent, 'aktiv', False)
            ausgewaehlt = getattr(talent, 'ausgewaehlt', False)
            
            Logger.debug(f"Talent '{name}': aktiv={aktiv}, ausgewaehlt={ausgewaehlt}")
            
            # Talent ist frei wenn es aktiv aber nicht ausgewählt ist
            if aktiv and not ausgewaehlt:
                frei_talente.append(name)
        
        Logger.debug(f"Gefundene freie Talente: {frei_talente}")
        
        # Alphabetisch sortieren
        frei_talente.sort()
        
        return frei_talente if frei_talente else [NO_TALENT_AVAILABLE_TEXT]
        
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen freier Talente: {e}", exc_info=True)
        return [NO_TALENT_AVAILABLE_TEXT]


def get_verfuegbare_attribute(charakter):
    """
    Gibt eine Liste aller verfügbaren Attribute zurück.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        list: Liste der verfügbaren Attribute
    """
    try:
        if not hasattr(charakter, 'attribute') or not charakter.attribute:
            Logger.warning("Keine Attribute im Charakter gefunden")
            return [NO_ATTRIBUT_AVAILABLE_TEXT]
        
        attribute_liste = list(charakter.attribute.keys())
        attribute_liste.sort()
        
        Logger.debug(f"Verfügbare Attribute: {attribute_liste}")
        return attribute_liste
        
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen der Attribute: {e}", exc_info=True)
        return [NO_ATTRIBUT_AVAILABLE_TEXT]


def get_verfuegbare_fertigkeiten(charakter, nur_verstand=True):
    """
    Gibt eine Liste aller verfügbaren Fertigkeiten zurück.
    
    Args:
        charakter: Das Charakterobjekt
        nur_verstand: Nur verstandsbasierte Fertigkeiten zurückgeben
        
    Returns:
        list: Liste der verfügbaren Fertigkeiten
    """
    try:
        if not hasattr(charakter, 'fertigkeiten') or not charakter.fertigkeiten:
            Logger.warning("Keine Fertigkeiten im Charakter gefunden")
            return [NO_FERTIGKEIT_AVAILABLE_TEXT]
        
        fertigkeiten_liste = []
        
        Logger.debug(f"Analysiere {len(charakter.fertigkeiten)} Fertigkeiten")
        
        for name, fertigkeit in charakter.fertigkeiten.items():
            attribut = getattr(fertigkeit, 'attribut', None)
            Logger.debug(f"Fertigkeit '{name}': Attribut={attribut}")
            
            if nur_verstand:
                # Nur verstandsbasierte Fertigkeiten
                if attribut and attribut.lower() in ['verstand', 'intelligence', 'smarts']:
                    fertigkeiten_liste.append(name)
            else:
                # Alle Fertigkeiten
                fertigkeiten_liste.append(name)
        
        Logger.debug(f"Gefundene Fertigkeiten: {fertigkeiten_liste}")
        
        fertigkeiten_liste.sort()
        return fertigkeiten_liste if fertigkeiten_liste else [NO_FERTIGKEIT_AVAILABLE_TEXT]
        
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen der Fertigkeiten: {e}", exc_info=True)
        return [NO_FERTIGKEIT_AVAILABLE_TEXT]


def waehle_freies_talent(charakter, volk_name, talent_name):
    """
    Wählt ein freies Talent für ein Volk aus.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        talent_name: Name des zu wählenden Talents
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.debug(f"Wähle freies Talent '{talent_name}' für Volk '{volk_name}'")
        
        if talent_name in [NO_TALENT_AVAILABLE_TEXT, "Keine freien Talente verfügbar"]:
            Logger.warning("Ungültiges Talent ausgewählt")
            return False
        
        # Prüfen ob Talent existiert und verfügbar ist
        if not hasattr(charakter, 'talente') or talent_name not in charakter.talente:
            Logger.error(f"Talent '{talent_name}' nicht gefunden")
            return False
        
        talent = charakter.talente[talent_name]
        
        if not getattr(talent, 'aktiv', False):
            Logger.error(f"Talent '{talent_name}' ist nicht aktiv")
            return False
        
        if getattr(talent, 'ausgewaehlt', False):
            Logger.warning(f"Talent '{talent_name}' ist bereits ausgewählt")
            return False
        
        # Talent auswählen
        talent.ausgewaehlt = True
        
        # Zu selected_talente hinzufügen
        if hasattr(charakter, 'selected_talente'):
            if talent_name not in charakter.selected_talente:
                charakter.selected_talente.append(talent_name)
                Logger.debug(f"Talent '{talent_name}' zu selected_talente hinzugefügt")
        
        Logger.info(f"Freies Talent '{talent_name}' für Volk '{volk_name}' erfolgreich ausgewählt")
        return True
        
    except Exception as e:
        Logger.error(f"Fehler bei freier Talent-Auswahl: {e}", exc_info=True)
        return False


def waehle_freies_attribut(charakter, volk_name, attribut_name):
    """
    Wählt ein freies Attribut für ein Volk aus und erhöht es.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        attribut_name: Name des zu erhöhenden Attributs
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.debug(f"Wähle freies Attribut '{attribut_name}' für Volk '{volk_name}'")
        
        if attribut_name in [NO_ATTRIBUT_AVAILABLE_TEXT, "Keine Attribute verfügbar"]:
            Logger.warning("Ungültiges Attribut ausgewählt")
            return False
        
        # Prüfen ob Attribut existiert
        if not hasattr(charakter, 'attribute') or attribut_name not in charakter.attribute:
            Logger.error(f"Attribut '{attribut_name}' nicht gefunden")
            return False
        
        attribut = charakter.attribute[attribut_name]
        alter_wert = attribut.wert
        
        # Attribut um einen Würfeltyp erhöhen (W4 -> W6, etc.)
        # Für Völker-Boni normalerweise W4 -> W6 (+2)
        if alter_wert == 4:
            attribut.wert = 6  # W4 -> W6 (Standard-Völker-Bonus)
        else:
            attribut.wert += 1  # Fallback: um einen Würfeltyp erhöhen
        
        Logger.info(f"Freies Attribut '{attribut_name}' für Volk '{volk_name}' von W{alter_wert} auf W{attribut.wert} erhöht")
        
        # Abgeleitete Werte neu berechnen
        if hasattr(charakter, 'berechne_abgeleitete_werte'):
            charakter.berechne_abgeleitete_werte()
        
        return True
        
    except Exception as e:
        Logger.error(f"Fehler bei freier Attribut-Auswahl: {e}", exc_info=True)
        return False


def waehle_freie_fertigkeit(charakter, volk_name, fertigkeit_name):
    """
    Wählt eine freie Fertigkeit für ein Volk aus und erhöht sie.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        fertigkeit_name: Name der zu erhöhenden Fertigkeit
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.debug(f"Wähle freie Fertigkeit '{fertigkeit_name}' für Volk '{volk_name}'")
        
        if fertigkeit_name in [NO_FERTIGKEIT_AVAILABLE_TEXT, "Keine Fertigkeiten verfügbar"]:
            Logger.warning("Ungültige Fertigkeit ausgewählt")
            return False
        
        # Prüfen ob Fertigkeit existiert
        if not hasattr(charakter, 'fertigkeiten') or fertigkeit_name not in charakter.fertigkeiten:
            Logger.error(f"Fertigkeit '{fertigkeit_name}' nicht gefunden")
            return False
        
        fertigkeit = charakter.fertigkeiten[fertigkeit_name]
        alter_wert = fertigkeit.wert
        alter_modifier = getattr(fertigkeit, 'modifier', 0)
        
        # Prüfen ob es eine Grundfertigkeit ist
        grundfertigkeiten = [
            "Allgemeinwissen", "Athletik", "Heimlichkeit", 
            "Überreden", "Wahrnehmung"
        ]
        
        if fertigkeit_name in grundfertigkeiten:
            # Grundfertigkeit: W4 -> W6 (Würfelwert erhöhen)
            if alter_wert == 4:
                fertigkeit.wert = 6  # W4 -> W6 (Standard-Völker-Bonus)
            else:
                fertigkeit.wert += 1  # Fallback
            Logger.info(f"Freie Grundfertigkeit '{fertigkeit_name}' für Volk '{volk_name}' von W{alter_wert} auf W{fertigkeit.wert} erhöht")
        else:
            # Nicht-Grundfertigkeit: W4-2 -> W4+0 (Modifier erhöhen)
            if hasattr(fertigkeit, 'wuerfel') and hasattr(fertigkeit.wuerfel, 'modifier'):
                if alter_modifier == -2:
                    fertigkeit.wuerfel.modifier = 0  # W4-2 -> W4+0
                else:
                    fertigkeit.wuerfel.modifier += 2  # Fallback: +2 Modifier
                Logger.info(f"Freie Nicht-Grundfertigkeit '{fertigkeit_name}' für Volk '{volk_name}' Modifier von {alter_modifier:+d} auf {fertigkeit.wuerfel.modifier:+d} erhöht")
            else:
                # Fallback: Würfelwert erhöhen
                fertigkeit.wert += 1
                Logger.info(f"Freie Fertigkeit '{fertigkeit_name}' für Volk '{volk_name}' von W{alter_wert} auf W{fertigkeit.wert} erhöht (Fallback)")
        
        return True
        
    except Exception as e:
        Logger.error(f"Fehler bei freier Fertigkeiten-Auswahl: {e}", exc_info=True)
        return False


def get_volk_attribut_optionen(charakter, volk_name):
    """
    Gibt die verfügbaren Attribut-Optionen für ein Volk zurück.
    Manche Völker haben Wahlmöglichkeiten zwischen verschiedenen Attributen.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        
    Returns:
        list: Liste der verfügbaren Attribut-Optionen
    """
    try:
        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            Logger.warning(f"Volk '{volk_name}' nicht gefunden bei Attribut-Optionen-Abfrage")
            return [NO_ATTRIBUT_AVAILABLE_TEXT]
        
        volk = charakter.voelker[volk_name]
        
        # Spezifische Völker-Wahlmöglichkeiten prüfen
        if volk_name.lower() in ["halbork", "halborks"]:
            # Halborks können zwischen Stärke und Konstitution wählen
            return ["Stärke", "Konstitution"]
        
        elif volk_name.lower() in ["halbelf", "halbelfen"]:
            # Halbelfen können oft ein freies Attribut wählen
            return get_verfuegbare_attribute(charakter)
            
        elif volk_name.lower() in ["mensch", "menschen", "human"]:
            # Menschen können oft ein freies Attribut wählen (abhängig vom Setting)
            return get_verfuegbare_attribute(charakter)
        
        # Prüfe ob das Volk generell freie Attribut-Wahlmöglichkeiten hat
        if hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_attribut'):
            return get_verfuegbare_attribute(charakter)
        
        # Fallback: keine Attribut-Wahlmöglichkeiten
        return [NO_ATTRIBUT_AVAILABLE_TEXT]
        
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen der Attribut-Optionen für '{volk_name}': {e}")
        return [NO_ATTRIBUT_AVAILABLE_TEXT]


def get_volk_zusatzelemente(charakter, volk_name):
    """
    Gibt eine Liste der verfügbaren Zusatzelemente für ein Volk zurück.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        
    Returns:
        dict: Dictionary mit verfügbaren Zusatzelementen
    """
    try:
        zusatzelemente = {
            'freie_talente': False,
            'freie_attribute': False,
            'freie_fertigkeiten': False,
            'attribut_optionen': []
        }
        
        # Prüfen ob Volk existiert
        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            Logger.warning(f"Volk '{volk_name}' nicht gefunden bei Zusatzelemente-Abfrage")
            return zusatzelemente
        
        # Bereinigung durchführen
        _cleanup_voelker_selected(charakter)
        
        # Verschiedene Wahlmöglichkeiten prüfen
        if hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_talent') or \
           hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_anfaengertalent'):
            zusatzelemente['freie_talente'] = True
            Logger.debug(f"Freie Talente verfügbar für '{volk_name}'")
        
        # Attribut-Optionen abrufen
        attribut_optionen = get_volk_attribut_optionen(charakter, volk_name)
        if attribut_optionen and attribut_optionen != [NO_ATTRIBUT_AVAILABLE_TEXT]:
            zusatzelemente['freie_attribute'] = True
            zusatzelemente['attribut_optionen'] = attribut_optionen
            Logger.debug(f"Attribut-Optionen verfügbar für '{volk_name}': {attribut_optionen}")
            
        if hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freie_verstandsfertigkeit'):
            zusatzelemente['freie_fertigkeiten'] = True
            Logger.debug(f"Freie Fertigkeiten verfügbar für '{volk_name}'")
        
        Logger.debug(f"Zusatzelemente für Volk '{volk_name}': {zusatzelemente}")
        return zusatzelemente
        
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen der Zusatzelemente für '{volk_name}': {e}")
        return {'freie_talente': False, 'freie_attribute': False, 'freie_fertigkeiten': False, 'attribut_optionen': []}


def reset_volk_auswahlen(charakter, volk_name, auswahlen_dict):
    """
    Setzt alle Auswahlen für ein Volk zurück.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        auswahlen_dict: Dictionary mit den aktuellen Auswahlen
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        if volk_name not in auswahlen_dict:
            return True
        
        # Bereinigung durchführen
        _cleanup_voelker_selected(charakter)
            
        auswahl = auswahlen_dict[volk_name]
        
        # Alle Auswahlen zurücksetzen
        for auswahl_typ, auswahl_wert in auswahl.items():
            if auswahl_typ == 'talent':
                # Talent abwählen
                if hasattr(charakter, 'selected_talente') and auswahl_wert in charakter.selected_talente:
                    charakter.selected_talente.remove(auswahl_wert)
                    
                if hasattr(charakter, 'talente') and auswahl_wert in charakter.talente:
                    charakter.talente[auswahl_wert].ausgewaehlt = False
                    
            elif auswahl_typ == 'attribut':
                # Attribut-Erhöhung rückgängig machen
                if hasattr(charakter, 'attribute') and auswahl_wert in charakter.attribute:
                    charakter.attribute[auswahl_wert].wert -= 1
                    
            elif auswahl_typ == 'fertigkeit':
                # Fertigkeits-Erhöhung rückgängig machen
                if hasattr(charakter, 'fertigkeiten') and auswahl_wert in charakter.fertigkeiten:
                    charakter.fertigkeiten[auswahl_wert].wert -= 1
        
        # Auswahl aus Dictionary entfernen
        del auswahlen_dict[volk_name]
        
        Logger.debug(f"Auswahlen für Volk '{volk_name}' zurückgesetzt")
        return True
        
    except Exception as e:
        Logger.error(f"Fehler beim Zurücksetzen der Auswahlen für '{volk_name}': {e}")
        return False


def initialisiere_voelker_system(charakter):
    """
    Initialisiert und bereinigt das Völker-System für einen Charakter.
    Sollte nach dem Laden eines Charakters oder Wechseln des Settings aufgerufen werden.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.info("=== Initialisiere Völker-System ===")
        
        # Sicherstellen, dass voelker_selected existiert
        if not hasattr(charakter, 'voelker_selected'):
            charakter.voelker_selected = {}
        
        # Bereinigung durchführen
        _cleanup_voelker_selected(charakter)
        
        # Aktuell ausgewähltes Volk finden und validieren
        selected_volk = get_selected_volk(charakter)
        if selected_volk:
            Logger.info(f"Aktuell ausgewähltes Volk: {selected_volk.name}")
            
            # Prüfen ob Volk-Effekte korrekt angewendet sind
            if not selected_volk.ausgewaehlt:
                Logger.warning(f"Volk {selected_volk.name} ist ausgewählt aber nicht als ausgewaehlt markiert - korrigiere")
                selected_volk.ausgewaehlt = True
        else:
            Logger.info("Kein Volk aktuell ausgewählt")
        
        Logger.info("=== Völker-System erfolgreich initialisiert ===")
        return True
        
    except Exception as e:
        Logger.error(f"Fehler bei Völker-System-Initialisierung: {e}")
        return False


def get_voelker_status_info(charakter):
    """
    Gibt detaillierte Status-Informationen über das Völker-System zurück.
    Hilfreich für Debugging.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        dict: Status-Informationen
    """
    try:
        status = {
            'voelker_gesamt': 0,
            'voelker_selected_gesamt': 0,
            'ausgewaehltes_volk': None,
            'verwaiste_eintraege': [],
            'fehlende_eintraege': []
        }
        
        if hasattr(charakter, 'voelker'):
            status['voelker_gesamt'] = len(charakter.voelker)
        
        if hasattr(charakter, 'voelker_selected'):
            status['voelker_selected_gesamt'] = len(charakter.voelker_selected)
            
            # Verwaiste Einträge finden
            for volk_name in charakter.voelker_selected:
                if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
                    status['verwaiste_eintraege'].append(volk_name)
        
        # Fehlende Einträge finden
        if hasattr(charakter, 'voelker') and hasattr(charakter, 'voelker_selected'):
            for volk_name in charakter.voelker:
                if volk_name not in charakter.voelker_selected:
                    status['fehlende_eintraege'].append(volk_name)
        
        # Ausgewähltes Volk
        selected_volk = get_selected_volk(charakter)
        if selected_volk:
            status['ausgewaehltes_volk'] = selected_volk.name
        
        return status
        
    except Exception as e:
        Logger.error(f"Fehler bei Status-Abfrage: {e}")
        return {}