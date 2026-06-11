# functions/volk_core.py
"""
Volk-Kernfunktionen: Volk wählen/abwählen, Status, AH-Erkennung sowie
die internen Zustands-Helfer für Menschen-/Halbelf-Sonderfälle und UI-Refresh.
Teil des aufgeteilten volk_funktionen-Moduls; Fassade: functions/volk_funktionen.py
"""

import logging
import re
from kivy.logger import Logger


# Konstanten
DEFAULT_TALENT_TEXT = 'Wähle ein freies Talent'
DEFAULT_ATTRIBUT_TEXT = 'Wähle ein Attribut'
DEFAULT_FERTIGKEIT_TEXT = 'Wähle eine Fertigkeit'
NO_TALENT_AVAILABLE_TEXT = 'Keine freien Talente verfügbar'

# Matcht "Arkane Fertigkeit: Glaube (Willenskraft)" oder
# "...erhält die arkane Fertigkeit Glaube (Willenskraft) und beginnt..."
_ARKANE_FERTIGKEIT_PATTERN = re.compile(
    r"arkane Fertigkeit:?\s+(.+?)\s*\(", re.IGNORECASE
)
_VORAUSSETZUNG_WUERFEL_PATTERN = re.compile(r"^(.+?)\s+W\d+\+?$")

# Whitelist bekannter arkaner Fertigkeiten (über alle Settings hinweg).
# Wird genutzt um aus den Voraussetzungen die richtige Fertigkeit zu erkennen,
# ohne andere Skill-Voraussetzungen (z.B. "Glücksspiel W6+") fälschlich zu wählen.
_BEKANNTE_ARKANE_FERTIGKEITEN = {
    'Glaube', 'Zaubern', 'Magie', 'Fokus', 'Psionik', 'Hexerei',
    'Verrückte Wissenschaft', 'Alchemie', 'Darbietung',
    'Heldenmagie', 'Runenmagie',
}
# 'Magie' (Willenskraft) = intuitive Zauberfertigkeit der DSA-Traditionen
# (Hexen, Geoden, Zibiljas …), Gegenstück zum akademischen 'Zaubern' (Verstand).

# Hartkodierter Fallback für die Standard-AH-Talente (SWAE-Basis).
# Nur als letzte Reserve, wenn weder Beschreibung noch Voraussetzungen die
# Arkane Fertigkeit eindeutig liefern.
_AH_FERTIGKEIT_FALLBACK = {
    'AH (Wunder)': 'Glaube',
    'AH (Magie)': 'Zaubern',
    'AH (Psionik)': 'Psionik',
    'AH (Begabt)': 'Fokus',
    'AH (Verrückte Wissenschaft)': 'Verrückte Wissenschaft',
}


def _ist_ah_talent(talent_name: str) -> bool:
    """Prüft ob ein Talentname ein Arkaner Hintergrund (AH) Variante ist."""
    if not talent_name:
        return False
    return talent_name.startswith("AH (") or talent_name.startswith("AH:")


def _fertigkeit_aus_voraussetzungen(voraussetzungen):
    """Sucht in den Talent-Voraussetzungen nach einer bekannten Arkanen Fertigkeit.
    Berücksichtigt auch komma-separierte Voraussetzungs-Strings."""
    if not voraussetzungen:
        return None

    eintraege = []
    for v in voraussetzungen:
        if isinstance(v, str):
            eintraege.extend(part.strip() for part in v.split(','))

    for eintrag in eintraege:
        match = _VORAUSSETZUNG_WUERFEL_PATTERN.match(eintrag)
        if not match:
            continue
        name = match.group(1).strip()
        if name in _BEKANNTE_ARKANE_FERTIGKEITEN:
            return name
    return None


def extrahiere_arkane_fertigkeit_aus_ah(talent):
    """
    Ermittelt die Arkane Fertigkeit eines AH-Talents anhand mehrerer Quellen:
    1. Beschreibung ("Arkane Fertigkeit: X" oder "...erhält die arkane Fertigkeit X (...)")
    2. Voraussetzungen mit Whitelist bekannter Arkaner Fertigkeiten
    3. Hartkodierter Fallback für die SWAE-Standard-AHs

    Returns:
        str oder None: Name der Arkanen Fertigkeit
    """
    if not talent:
        return None

    beschreibung = getattr(talent, 'beschreibung', '') or ''
    match = _ARKANE_FERTIGKEIT_PATTERN.search(beschreibung)
    if match:
        return match.group(1).strip()

    fertigkeit = _fertigkeit_aus_voraussetzungen(getattr(talent, 'voraussetzungen', None))
    if fertigkeit:
        return fertigkeit

    talent_name = getattr(talent, 'name', '') or ''
    return _AH_FERTIGKEIT_FALLBACK.get(talent_name)
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
            
            # NEUE LOGIK: Spezielle Behandlung für Menschen beim Volk-Wechsel
            if altes_volk.name.lower() in ["mensch", "menschen", "human"]:
                # Nur resetten wenn das Volk die entsprechenden Wahlmöglichkeiten hat
                if hasattr(altes_volk, 'effects') and altes_volk.effects.get('wahlmoeglichkeiten', {}).get('freies_attribut', False):
                    _reset_menschen_freies_attribut(charakter)
                if hasattr(altes_volk, 'effects') and (altes_volk.effects.get('wahlmoeglichkeiten', {}).get('freies_talent', False) or 
                                                        altes_volk.effects.get('wahlmoeglichkeiten', {}).get('freies_anfaengertalent', False)):
                    _reset_menschen_freies_talent(charakter)
                    
            # NEUE LOGIK: Spezielle Behandlung für Halbelfen beim Volk-Wechsel
            if altes_volk.name.lower() in ["halbelf", "halbelfen"]:
                _reset_halbelf_auswahlen(charakter)
                
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
            
            # Event für UI-Update auslösen
            if hasattr(charakter, 'dispatch'):
                Logger.debug(f"VOLK_FUNKTIONEN: Dispatching on_charakter_change event for charakter {id(charakter)}")
                charakter.dispatch('on_charakter_change')
                
                # ZUSÄTZLICHE SICHERSTELLUNG: Explizites Update über Clock
                from kivy.clock import Clock
                from kivy.app import App
                
                def trigger_ui_update(dt):
                    """Explizite UI-Aktualisierung als Fallback"""
                    try:
                        app = App.get_running_app()
                        if hasattr(app, 'controller') and app.controller:
                            Logger.debug("VOLK_FUNKTIONEN: Triggering explicit UI update")
                            app.controller.dispatch('on_charakter_updated')
                    except Exception as e:
                        Logger.error(f"Fehler bei explizitem UI-Update: {e}")
                
                # Kurze Verzögerung um sicherzustellen dass alle Events processed sind
                Clock.schedule_once(trigger_ui_update, 0.1)
            else:
                Logger.error("VOLK_FUNKTIONEN: Charakter hat keine dispatch-Methode!")
            
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
    ERWEITERT: Spezielle Behandlung für Menschen-Attribut-Reset.
    
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
        
        # NEUE LOGIK: Spezielle Behandlung für Menschen
        if volk_name.lower() in ["mensch", "menschen", "human"]:
            # Nur resetten wenn das Volk die entsprechenden Wahlmöglichkeiten hat
            if hasattr(volk, 'effects') and volk.effects.get('wahlmoeglichkeiten', {}).get('freies_attribut', False):
                _reset_menschen_freies_attribut(charakter)
            if hasattr(volk, 'effects') and (volk.effects.get('wahlmoeglichkeiten', {}).get('freies_talent', False) or 
                                             volk.effects.get('wahlmoeglichkeiten', {}).get('freies_anfaengertalent', False)):
                _reset_menschen_freies_talent(charakter)
                
        # NEUE LOGIK: Spezielle Behandlung für Halbelfen
        if volk_name.lower() in ["halbelf", "halbelfen"]:
            _reset_halbelf_auswahlen(charakter)
        
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
    ERWEITERT: Bessere Goblin-Erkennung und Menschen-Attribut-Support.
    
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
        
        # DEBUG: Volk-Struktur ausgeben
        Logger.debug(f"=== DEBUG: Volk '{volk_name}' Wahlmöglichkeits-Prüfung ===")
        if hasattr(volk, 'effects'):
            wahlmoeglichkeiten = volk.effects.get('wahlmoeglichkeiten', {})
            Logger.debug(f"Wahlmöglichkeiten für '{volk_name}': {wahlmoeglichkeiten}")
        else:
            Logger.debug(f"Volk '{volk_name}' hat keine effects")
        
        # ERWEITERT: Goblin-spezifische Behandlung ZUERST
        if wahlmoeglichkeit_typ in ['freies_talent', 'freies_anfaengertalent']:
            # Direkte Goblin-Prüfung
            if volk_name.lower() in ["goblin", "goblins"]:
                Logger.debug(f"GOBLIN CHECK: Prüfe freies Talent für '{volk_name}'")
                
                if hasattr(volk, 'effects'):
                    wahlmoeglichkeiten = volk.effects.get('wahlmoeglichkeiten', {})
                    
                    # ERWEITERT: Mehrere Varianten prüfen
                    if (wahlmoeglichkeiten.get('freies_anfaenger_talent', False) or 
                        wahlmoeglichkeiten.get('freies_talent', False) or
                        wahlmoeglichkeiten.get('freies_anfaengertalent', False)):
                        Logger.info(f"✅ GOBLIN: Freies Talent verfügbar für '{volk_name}'")
                        return True
                    else:
                        Logger.warning(f"❌ GOBLIN: Keine Talent-Wahlmöglichkeit gefunden für '{volk_name}'. Wahlmöglichkeiten: {wahlmoeglichkeiten}")
                else:
                    Logger.warning(f"❌ GOBLIN: Keine effects für '{volk_name}'")
                return False  # Expliziter Return für Goblin
        
        # Spezifische Völker-Wahlmöglichkeiten prüfen (nur basierend auf JSON)
        # Keine harten Volk-Namen-Checks mehr - verlassen wir uns auf die effects/wahlmoeglichkeiten
        
        # Direkte Prüfung über Volk-Methode
        if hasattr(volk, 'has_wahlmoeglichkeit'):
            result = volk.has_wahlmoeglichkeit(wahlmoeglichkeit_typ)
            Logger.debug(f"Volk-Methode has_wahlmoeglichkeit für '{volk_name}': {result}")
            if result:
                return True
            # Bei False: Weiter zu Fallback-Checks (z.B. Menschen-Spezialbehandlung)

        # Fallback: Prüfung über effects
        if hasattr(volk, 'effects'):
            wahlmoeglichkeiten = volk.effects.get('wahlmoeglichkeiten', {})
            
            # Standard-Checks
            if wahlmoeglichkeiten.get(wahlmoeglichkeit_typ, False):
                Logger.debug(f"Standard-Check erfolgreich für '{volk_name}': {wahlmoeglichkeit_typ}")
                return True
            
            # ERWEITERT: Halbork-spezifische Checks  
            if wahlmoeglichkeit_typ == 'freies_attribut':
                if wahlmoeglichkeiten.get('attribut_staerke_oder_konstitution', False):
                    Logger.debug(f"Halbork-Spezialbehandlung: Attribut-Wahl für '{volk_name}'")
                    return True
                    
                # Halbelf hat freies_talent_oder_attribut (kann Attribut wählen)
                if wahlmoeglichkeiten.get('freies_talent_oder_attribut', False):
                    Logger.debug(f"Halbelf-Spezialbehandlung: freies Attribut für '{volk_name}'")
                    return True
        
        # Spezialbehandlung für Menschen: nur freies Talent (kein freies Attribut in SWAE/Standard)
        if volk_name.lower() in ["mensch", "menschen", "human"]:
            if wahlmoeglichkeit_typ in ['freies_talent', 'freies_anfaengertalent']:
                Logger.debug(f"Menschen-Spezialbehandlung: freies Talent für '{volk_name}'")
                return True
        
        Logger.debug(f"Keine Wahlmöglichkeit '{wahlmoeglichkeit_typ}' für '{volk_name}' gefunden")
        return False
        
    except Exception as e:
        Logger.error(f"Fehler bei Wahlmöglichkeits-Prüfung für '{volk_name}': {e}")
        return False


def initialisiere_voelker_system(charakter):
    """
    Initialisiert und bereinigt das Völker-System für einen Charakter.
    Sollte nach dem Laden eines Charakters oder Wechseln des Settings aufgerufen werden.
    ERWEITERT: Menschen-spezifisches Attribut-Tracking initialisieren.
    
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
        
        # NEUE LOGIK: Menschen-spezifisches Tracking initialisieren
        if not hasattr(charakter, '_menschen_freies_attribut'):
            charakter._menschen_freies_attribut = None
            
        if not hasattr(charakter, '_menschen_freies_talent'):
            charakter._menschen_freies_talent = None

        if not hasattr(charakter, '_mensch_fertigkeitspunkte_gewaehlt'):
            charakter._mensch_fertigkeitspunkte_gewaehlt = False

        # NEUE LOGIK: Halbelf-spezifisches Tracking initialisieren
        if not hasattr(charakter, '_halbelf_freies_talent'):
            charakter._halbelf_freies_talent = None
            
        if not hasattr(charakter, '_halbelf_attribut_gewaehlt'):
            charakter._halbelf_attribut_gewaehlt = False
        
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


# NEUE HILFSFUNKTIONEN FÜR MENSCHEN-SPEZIFISCHES ATTRIBUT-TRACKING

def _get_menschen_freies_attribut(charakter):
    """
    Gibt das aktuell gewählte freie Attribut für Menschen zurück.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        str oder None: Name des freien Attributs oder None
    """
    try:
        if hasattr(charakter, '_menschen_freies_attribut'):
            return charakter._menschen_freies_attribut
        return None
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen des Menschen-freien-Attributs: {e}")
        return None


def _set_menschen_freies_attribut(charakter, attribut_name):
    """
    Setzt das freie Attribut für Menschen.
    
    Args:
        charakter: Das Charakterobjekt
        attribut_name: Name des freien Attributs
    """
    try:
        charakter._menschen_freies_attribut = attribut_name
        Logger.debug(f"Menschen freies Attribut auf '{attribut_name}' gesetzt")
    except Exception as e:
        Logger.error(f"Fehler beim Setzen des Menschen-freien-Attributs: {e}")


def _reset_menschen_freies_attribut(charakter):
    """
    Setzt das freie Attribut für Menschen zurück.
    
    Args:
        charakter: Das Charakterobjekt
    """
    try:
        aktuelles_attribut = _get_menschen_freies_attribut(charakter)
        
        if aktuelles_attribut and hasattr(charakter, 'attribute'):
            if aktuelles_attribut in charakter.attribute:
                attribut = charakter.attribute[aktuelles_attribut]
                # Nur zurücksetzen wenn es auf W6 erhöht wurde (Standard freier Attribut-Bonus)
                if attribut.wert == 6:
                    attribut.wert = 4
                    Logger.info(f"Menschen freies Attribut '{aktuelles_attribut}' von W6 auf W4 zurückgesetzt")
        
        # Tracking zurücksetzen
        charakter._menschen_freies_attribut = None
        Logger.debug("Menschen freies Attribut-Tracking zurückgesetzt")
        
        # Abgeleitete Werte neu berechnen
        if hasattr(charakter, 'berechne_abgeleitete_werte'):
            charakter.berechne_abgeleitete_werte()
        
        # Event für UI-Update auslösen
        if hasattr(charakter, 'dispatch'):
            charakter.dispatch('on_charakter_change')
            
    except Exception as e:
        Logger.error(f"Fehler beim Zurücksetzen des Menschen-freien-Attributs: {e}")


def _get_menschen_freies_talent(charakter):
    """
    Gibt das aktuell gewählte freie Talent für Menschen zurück.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        str oder None: Name des freien Talents oder None
    """
    try:
        if hasattr(charakter, '_menschen_freies_talent'):
            return charakter._menschen_freies_talent
        return None
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen des Menschen-freien-Talents: {e}")
        return None


def _set_menschen_freies_talent(charakter, talent_name):
    """
    Setzt das freie Talent für Menschen.
    
    Args:
        charakter: Das Charakterobjekt
        talent_name: Name des freien Talents
    """
    try:
        charakter._menschen_freies_talent = talent_name
        Logger.debug(f"Menschen freies Talent auf '{talent_name}' gesetzt")
    except Exception as e:
        Logger.error(f"Fehler beim Setzen des Menschen-freien-Talents: {e}")


def _reset_menschen_freies_talent(charakter):
    """
    Setzt das freie Talent für Menschen zurück.
    
    Args:
        charakter: Das Charakterobjekt
    """
    try:
        aktuelles_talent = _get_menschen_freies_talent(charakter)
        
        if aktuelles_talent and hasattr(charakter, 'talente'):
            if aktuelles_talent in charakter.talente:
                talent = charakter.talente[aktuelles_talent]
                # Talent abwählen
                talent.ausgewaehlt = False
                Logger.info(f"Menschen freies Talent '{aktuelles_talent}' abgewählt")
                
                # Aus selected_talente entfernen
                if hasattr(charakter, 'selected_talente') and aktuelles_talent in charakter.selected_talente:
                    charakter.selected_talente.remove(aktuelles_talent)
                    Logger.debug(f"Talent '{aktuelles_talent}' aus selected_talente entfernt")
        
        # Tracking zurücksetzen
        charakter._menschen_freies_talent = None
        Logger.debug("Menschen freies Talent-Tracking zurückgesetzt")
            
    except Exception as e:
        Logger.error(f"Fehler beim Zurücksetzen des Menschen-freien-Talents: {e}")


def _get_halbelf_freies_talent(charakter):
    """
    Gibt das aktuell gewählte freie Talent für Halbelfen zurück.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        str oder None: Name des freien Talents oder None
    """
    try:
        if hasattr(charakter, '_halbelf_freies_talent'):
            return charakter._halbelf_freies_talent
        return None
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen des Halbelf-freien-Talents: {e}")
        return None


def _set_halbelf_freies_talent(charakter, talent_name):
    """
    Setzt das freie Talent für Halbelfen.
    
    Args:
        charakter: Das Charakterobjekt
        talent_name: Name des freien Talents oder None
    """
    try:
        charakter._halbelf_freies_talent = talent_name
        Logger.debug(f"Halbelf freies Talent auf '{talent_name}' gesetzt")
    except Exception as e:
        Logger.error(f"Fehler beim Setzen des Halbelf-freien-Talents: {e}")


def _get_halbelf_attribut_gewaehlt(charakter):
    """
    Gibt zurück ob der Halbelf bereits das Geschicklichkeits-Attribut gewählt hat.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        bool: True wenn Attribut gewählt wurde
    """
    try:
        if hasattr(charakter, '_halbelf_attribut_gewaehlt'):
            return charakter._halbelf_attribut_gewaehlt
        return False
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen des Halbelf-Attribut-Status: {e}")
        return False


def _set_halbelf_attribut_gewaehlt(charakter, gewaehlt):
    """
    Setzt den Status ob der Halbelf das Geschicklichkeits-Attribut gewählt hat.
    
    Args:
        charakter: Das Charakterobjekt
        gewaehlt: bool - True wenn gewählt
    """
    try:
        charakter._halbelf_attribut_gewaehlt = gewaehlt
        Logger.debug(f"Halbelf Attribut-Status auf '{gewaehlt}' gesetzt")
    except Exception as e:
        Logger.error(f"Fehler beim Setzen des Halbelf-Attribut-Status: {e}")


def _reset_halbelf_auswahlen(charakter):
    """
    Setzt alle Halbelf-Auswahlen zurück (sowohl Talent als auch Attribut).
    
    Args:
        charakter: Das Charakterobjekt
    """
    try:
        # Freies Talent zurücksetzen
        aktuelles_talent = _get_halbelf_freies_talent(charakter)
        if aktuelles_talent and hasattr(charakter, 'talente'):
            if aktuelles_talent in charakter.talente:
                talent = charakter.talente[aktuelles_talent]
                talent.ausgewaehlt = False
                Logger.info(f"Halbelf freies Talent '{aktuelles_talent}' abgewählt")
                
                # Aus selected_talente entfernen
                if hasattr(charakter, 'selected_talente') and aktuelles_talent in charakter.selected_talente:
                    charakter.selected_talente.remove(aktuelles_talent)
                    Logger.debug(f"Talent '{aktuelles_talent}' aus selected_talente entfernt")
        
        # Geschicklichkeits-Attribut zurücksetzen
        if _get_halbelf_attribut_gewaehlt(charakter) and hasattr(charakter, 'attribute'):
            if 'Geschicklichkeit' in charakter.attribute:
                geschicklichkeit = charakter.attribute['Geschicklichkeit']
                if geschicklichkeit.wert == 6:  # Von W6 auf W4 zurücksetzen
                    geschicklichkeit.wert = 4
                    Logger.info("Halbelf Geschicklichkeits-Bonus von W6 auf W4 zurückgesetzt")
        
        # Tracking zurücksetzen
        charakter._halbelf_freies_talent = None
        charakter._halbelf_attribut_gewaehlt = False
        Logger.debug("Halbelf ENTWEDER/ODER-Auswahlen zurückgesetzt")
        
        # Abgeleitete Werte neu berechnen
        if hasattr(charakter, 'berechne_abgeleitete_werte'):
            charakter.berechne_abgeleitete_werte()
        
        # Event für UI-Update auslösen
        if hasattr(charakter, 'dispatch'):
            charakter.dispatch('on_charakter_change')
            
    except Exception as e:
        Logger.error(f"Fehler beim Zurücksetzen der Halbelf-Auswahlen: {e}")


def _force_eigenschaften_update(app):
    """
    Erzwingt ein sofortiges Update der Eigenschaften View.
    Verbesserte Methode mit korrektem Zugriff und Event-System.
    
    Args:
        app: Die Kivy App-Instanz
    """
    try:
        Logger.debug("=== FORCE EIGENSCHAFTEN UPDATE START ===")
        
        # METHODE 1: Direkter Controller-Event (bevorzugt)
        if hasattr(app, 'controller') and app.controller:
            Logger.debug("Verwende Controller-Event für Eigenschaften-Update...")
            app.controller.dispatch('on_charakter_updated')
            Logger.info("✅ Eigenschaften-View via Controller Event aktualisiert")
            return True
        
        # METHODE 2: Direkter Zugriff über app.screens Dictionary
        if hasattr(app, 'screens') and 'Eigenschaften' in app.screens:
            eigenschaften_screen = app.screens['Eigenschaften']
            Logger.debug(f"Eigenschaften Screen gefunden: {type(eigenschaften_screen)}")
            
            # Screen hat ein EigenschaftenWidget
            if hasattr(eigenschaften_screen, 'ids') and hasattr(eigenschaften_screen.ids, 'eigenschaften_widget'):
                eigenschaften_widget = eigenschaften_screen.ids.eigenschaften_widget
                Logger.debug(f"Eigenschaften Widget gefunden: {type(eigenschaften_widget)}")
                
                # Verfügbare Update-Methoden prüfen
                update_methods = [
                    ('update_eigenschaften', 'update_eigenschaften'),
                    ('_plane_update', '_plane_update mit None-Argument'),
                    ('aktualisiere_ui', 'aktualisiere_ui'),
                    ('refresh_widget', 'refresh_widget')
                ]
                
                for method_name, description in update_methods:
                    if hasattr(eigenschaften_widget, method_name):
                        try:
                            method = getattr(eigenschaften_widget, method_name)
                            if method_name == '_plane_update':
                                method(None)  # _plane_update erwartet ein instance-Argument
                            else:
                                method()
                            Logger.info(f"✅ Eigenschaften-View via {description} aktualisiert")
                            return True
                        except Exception as e:
                            Logger.warning(f"⚠️ Fehler bei {method_name}: {e}")
                            continue
                
                Logger.warning("❌ Keine funktionierende Update-Methode für Eigenschaften-Widget gefunden")
                # Debug: Verfügbare Methoden auflisten
                methods = [method for method in dir(eigenschaften_widget) if 'update' in method.lower() or 'aktualis' in method.lower()]
                Logger.debug(f"Verfügbare Update-ähnliche Methoden: {methods}")
                
            else:
                Logger.warning("❌ Eigenschaften-Widget nicht in Screen.ids gefunden")
                if hasattr(eigenschaften_screen, 'ids'):
                    Logger.debug(f"Verfügbare IDs: {list(eigenschaften_screen.ids.keys())}")
        
        # METHODE 3: Fallback über registrierte Widgets in der App
        elif hasattr(app, 'eigenschaften_widget'):
            eigenschaften_widget = app.eigenschaften_widget
            Logger.debug(f"Eigenschaften Widget über App-Attribut gefunden: {type(eigenschaften_widget)}")
            
            if hasattr(eigenschaften_widget, 'update_eigenschaften'):
                eigenschaften_widget.update_eigenschaften()
                Logger.info("✅ Eigenschaften-View via App-Attribut aktualisiert")
                return True
            else:
                Logger.warning("❌ aktualisiere_ui Methode nicht verfügbar über App-Attribut")
        
        else:
            Logger.error("❌ Eigenschaften Screen/Widget nicht gefunden")
            Logger.debug(f"App hat screens: {hasattr(app, 'screens')}")
            if hasattr(app, 'screens'):
                Logger.debug(f"Verfügbare Screens: {list(app.screens.keys())}")
        
        Logger.debug("=== FORCE EIGENSCHAFTEN UPDATE END ===")
        
    except Exception as e:
        Logger.error(f"❌ Fehler beim direkten Eigenschaften-Update: {e}", exc_info=True)


def _force_trigger_ui_refresh(app):
    """
    Triggert ein komplettes UI-Refresh der Eigenschaften View.
    Notfall-Strategie für hartnäckige Update-Probleme.
    
    Args:
        app: Die Kivy App-Instanz
    """
    try:
        Logger.debug("=== FORCE UI REFRESH START ===")
        
        # Direkte Event-Triggerung am Controller
        if hasattr(app, 'controller'):
            controller = app.controller
            
            # Controller-Events direkt dispatchen
            if hasattr(controller, 'dispatch'):
                controller.dispatch('on_charakter_updated')
                Logger.debug("Controller on_charakter_updated Event dispatched")
            
            # Alle registrierten Eigenschaften-Widgets finden und aktualisieren
            if hasattr(app, 'eigenschaften_widget'):
                widget = app.eigenschaften_widget
                if hasattr(widget, '_update_ausstehend'):
                    widget._update_ausstehend = False  # Reset Update-Flag
                if hasattr(widget, '_plane_update'):
                    widget._plane_update(controller)
                    Logger.debug("Direktes _plane_update auf registriertem Widget")
        
        Logger.debug("UI-Refresh abgeschlossen")
        
    except Exception as e:
        Logger.warning(f"UI-Refresh fehlgeschlagen: {e}")


def _get_mensch_fertigkeitspunkte_gewaehlt(charakter):
    """Gibt zurück ob der Mensch Fertigkeitspunkte statt Talent gewählt hat."""
    try:
        if hasattr(charakter, '_mensch_fertigkeitspunkte_gewaehlt'):
            return charakter._mensch_fertigkeitspunkte_gewaehlt
        return False
    except Exception:
        return False


def _set_mensch_fertigkeitspunkte_gewaehlt(charakter, gewaehlt):
    """Setzt den Tracking-Status für Mensch-Fertigkeitspunkte."""
    try:
        charakter._mensch_fertigkeitspunkte_gewaehlt = gewaehlt
        Logger.debug(f"Mensch Fertigkeitspunkte-Wahl auf {gewaehlt} gesetzt")
    except Exception as e:
        Logger.error(f"Fehler beim Setzen der Mensch-Fertigkeitspunkte-Wahl: {e}")


def _reset_mensch_fertigkeitspunkte(charakter):
    """Setzt die Mensch-Fertigkeitspunkte-Wahl zurück (-2 Punkte)."""
    try:
        if _get_mensch_fertigkeitspunkte_gewaehlt(charakter):
            if hasattr(charakter, 'verbleibende_fertigkeitssteigerungen'):
                charakter.verbleibende_fertigkeitssteigerungen -= 2
                Logger.debug(f"Verbleibende Fertigkeitssteigerungen zurückgesetzt auf {charakter.verbleibende_fertigkeitssteigerungen}")
            if hasattr(charakter, 'maximale_fertigkeitssteigerungen'):
                charakter.maximale_fertigkeitssteigerungen -= 2
                Logger.debug(f"Maximale Fertigkeitssteigerungen zurückgesetzt auf {charakter.maximale_fertigkeitssteigerungen}")
            _set_mensch_fertigkeitspunkte_gewaehlt(charakter, False)
            Logger.info("Mensch Fertigkeitspunkte-Wahl zurückgesetzt")
    except Exception as e:
        Logger.error(f"Fehler beim Zurücksetzen der Mensch-Fertigkeitspunkte: {e}")