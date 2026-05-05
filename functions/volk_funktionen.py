# functions/volk_funktionen.py
"""
Volk-Funktionen zur Trennung von Geschäftslogik und UI.
Enthält alle Volk-spezifischen Operationen und Berechnungen.
ERWEITERT: Spezielle Behandlung für Menschen - nur ein freies Attribut gleichzeitig
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
    'Glaube', 'Zaubern', 'Fokus', 'Psionik', 'Hexerei',
    'Verrückte Wissenschaft', 'Alchemie', 'Darbietung',
    'Heldenmagie', 'Runenmagie',
}

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
        
        # Spezialbehandlung für Menschen
        if volk_name.lower() in ["mensch", "menschen", "human"]:
            if wahlmoeglichkeit_typ in ['freies_talent', 'freies_anfaengertalent']:
                Logger.debug(f"Menschen-Spezialbehandlung: freies Talent für '{volk_name}'")
                return True
            elif wahlmoeglichkeit_typ == 'freies_attribut':
                Logger.debug(f"Menschen-Spezialbehandlung: freies Attribut für '{volk_name}'")
                return True
        
        Logger.debug(f"Keine Wahlmöglichkeit '{wahlmoeglichkeit_typ}' für '{volk_name}' gefunden")
        return False
        
    except Exception as e:
        Logger.error(f"Fehler bei Wahlmöglichkeits-Prüfung für '{volk_name}': {e}")
        return False


def get_freie_talente(charakter, nur_verfuegbare=True):
    """
    Gibt eine Liste aller verfügbaren freien Talente zurück.

    Args:
        charakter: Das Charakterobjekt
        nur_verfuegbare: Wenn True, nur Talente mit erfüllten Voraussetzungen

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

            #Logger.debug(f"Talent '{name}': aktiv={aktiv}, ausgewaehlt={ausgewaehlt}")

            # Talent ist frei wenn es aktiv aber nicht ausgewählt ist
            if aktiv and not ausgewaehlt:
                if nur_verfuegbare:
                    from functions.talent_funktionen import pruefe_voraussetzungen, is_talent_rang_hoeher_als_charakter
                    if pruefe_voraussetzungen(charakter, talent):
                        continue
                    if is_talent_rang_hoeher_als_charakter(charakter, talent.rang):
                        continue
                frei_talente.append(name)
        
        #Logger.debug(f"Gefundene freie Talente: {frei_talente}")
        
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


def get_absenkbare_attribute(charakter):
    """
    Gibt eine Liste der Attribute zurück, die noch um einen Würfeltyp gesenkt
    werden können (Wert >= 6 → W6, W8, W10, W12, ...).

    Args:
        charakter: Das Charakterobjekt

    Returns:
        list: Liste der absenkbaren Attribut-Namen
    """
    try:
        if not hasattr(charakter, 'attribute') or not charakter.attribute:
            return []
        result = [name for name, attr in charakter.attribute.items()
                  if hasattr(attr, 'wert') and attr.wert >= 6]
        result.sort()
        Logger.debug(f"Absenkbare Attribute: {result}")
        return result
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen der absenkbaren Attribute: {e}")
        return []


def get_staerkbare_attribute(charakter):
    """
    Gibt eine Liste der Attribute zurück, die als Attributsschwäche in Frage
    kommen: base Würfel = W4 und noch kein malus-2 Modifier darauf.

    Args:
        charakter: Das Charakterobjekt

    Returns:
        list: Liste der für Attributsschwäche geeigneten Attribut-Namen
    """
    try:
        if not hasattr(charakter, 'attribute') or not charakter.attribute:
            return []
        result = []
        for name, attr in charakter.attribute.items():
            if not hasattr(attr, 'wert') or attr.wert != 4:
                continue
            mod = getattr(attr, 'modifier', 0) if hasattr(attr, 'modifier') else 0
            if mod >= 0:
                result.append(name)
        result.sort()
        Logger.debug(f"Attributsschwäche-kompatible Attribute: {result}")
        return result
    except Exception as e:
        Logger.error(f"Fehler bei Attributsschwäche-Kompatibilitätsprüfung: {e}")
        return []


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
                if attribut and hasattr(attribut, 'attribut_name'):
                    attribut_name = attribut.attribut_name.lower()
                    if attribut_name in ['verstand', 'intelligence', 'smarts']:
                        fertigkeiten_liste.append(name)
                elif attribut and isinstance(attribut, str):
                    # Fallback für String-Attribute
                    if attribut.lower() in ['verstand', 'intelligence', 'smarts']:
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


def waehle_freies_talent(charakter, volk_name, talent_name, ignore_voraussetzungen=False):
    """
    Wählt ein freies Talent für ein Volk aus.
    ERWEITERT: Spezielle Behandlung für Menschen - nur ein Talent gleichzeitig.
    Nutzt talent_funktionen.waehle_freies_talent für AH-Aktivierung etc.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        talent_name: Name des zu wählenden Talents
        ignore_voraussetzungen: Voraussetzungsprüfung überspringen (default: False)
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
        str: "needs_voraussetzungen_confirmation" wenn Voraussetzungen nicht erfüllt
    """
    try:
        Logger.debug(f"Wähle freies Talent '{talent_name}' für Volk '{volk_name}' (ignore_voraussetzungen={ignore_voraussetzungen})")
        
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
        
        # NEUE LOGIK: Spezielle Behandlung für Menschen (nur wenn sie freie Talent-Wahlmöglichkeit haben)
        if (volk_name.lower() in ["mensch", "menschen", "human"] and 
            (hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_talent') or 
             hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_anfaengertalent'))):
            # Prüfen ob bereits ein anderes freies Talent gewählt wurde
            aktuelles_freies_talent = _get_menschen_freies_talent(charakter)
            
            if aktuelles_freies_talent and aktuelles_freies_talent != talent_name:
                Logger.info(f"Menschen: Setze vorheriges freies Talent '{aktuelles_freies_talent}' zurück")
                # Vorheriges Talent abwählen (inkl. AH-Effekte, Mächte, Machtpunkte)
                from functions.talent_funktionen import talent_abwaehlen
                talent_abwaehlen(charakter, aktuelles_freies_talent)
            
            # Neues freies Talent setzen (nach erfolgreicher Auswahl)
            _set_menschen_freies_talent(charakter, talent_name)
        
        # Talent über talent_funktionen.waehle_freies_talent auswählen (berücksichtigt AH, Mächte, Auto-Handicaps etc.)
        from functions.talent_funktionen import waehle_freies_talent as talent_waehle_freies_talent
        result = talent_waehle_freies_talent(charakter, talent_name, ignore_voraussetzungen)
        
        # Wenn result "needs_voraussetzungen_confirmation" ist, müssen wir das temporär gesetzte Talent wieder zurücksetzen?
        # talent_waehle_freies_talent hat das Talent noch nicht ausgewählt, also kein Zurücksetzen nötig.
        # Fehlermeldungen wurden bereits in charakter.temp_voraussetzungs_fehler gespeichert.
        if result == "needs_voraussetzungen_confirmation":
            Logger.debug(f"Voraussetzungen nicht erfüllt für Talent '{talent_name}', Rückgabe 'needs_voraussetzungen_confirmation'")
            # Menschen-Tracking zurücksetzen, da wir das Talent nicht gewählt haben
            if (volk_name.lower() in ["mensch", "menschen", "human"] and 
                (hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_talent') or 
                 hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_anfaengertalent'))):
                _set_menschen_freies_talent(charakter, None)
            return "needs_voraussetzungen_confirmation"
        
        # Erfolg
        if result:
            Logger.info(f"Freies Talent '{talent_name}' für Volk '{volk_name}' erfolgreich ausgewählt")
            return True
        else:
            Logger.error(f"Fehler bei der Auswahl des freien Talents '{talent_name}'")
            return False
        
    except Exception as e:
        Logger.error(f"Fehler bei freier Talent-Auswahl: {e}", exc_info=True)
        return False


def waehle_freies_attribut(charakter, volk_name, attribut_name):
    """
    Wählt ein freies Attribut für ein Volk aus und erhöht es.
    ERWEITERT: Spezielle Behandlung für Menschen - nur ein Attribut gleichzeitig.
    
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
        
        # NEUE LOGIK: Spezielle Behandlung für Menschen (nur wenn sie freie Attribut-Wahlmöglichkeit haben)
        if (volk_name.lower() in ["mensch", "menschen", "human"] and 
            hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_attribut')):
            # Prüfen ob bereits ein anderes freies Attribut gewählt wurde
            aktuelles_freies_attribut = _get_menschen_freies_attribut(charakter)
            
            if aktuelles_freies_attribut and aktuelles_freies_attribut != attribut_name:
                Logger.info(f"Menschen: Setze vorheriges freies Attribut '{aktuelles_freies_attribut}' zurück")
                # Vorheriges Attribut von W6 auf W4 zurücksetzen
                vorheriges_attribut = charakter.attribute[aktuelles_freies_attribut]
                if vorheriges_attribut.wert == 6:  # Nur wenn es durch freies Attribut erhöht wurde
                    vorheriges_attribut.wert = 4
                    Logger.debug(f"Attribut '{aktuelles_freies_attribut}' von W6 auf W4 zurückgesetzt")
            
            # Neues freies Attribut setzen
            _set_menschen_freies_attribut(charakter, attribut_name)
        
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
        
        # Event für UI-Update auslösen
        if hasattr(charakter, 'dispatch'):
            charakter.dispatch('on_charakter_change')
        
        # Zusätzlich direkte Eigenschaften-View-Update erzwingen
        try:
            from kivy.app import App
            from kivy.clock import Clock
            app = App.get_running_app()
            if hasattr(app, 'controller') and hasattr(app.controller, 'charakter'):
                # KONSOLIDIERT: Sequenzielle Logik statt kaskadierter Delays (0.05+0.2+0.1s → 0s)
                def consolidated_update_sequence(dt):
                    """Konsolidierte Update-Sequenz statt mehrerer Clock-Calls."""
                    try:
                        # Eigenschaften-Updates (war 2x mit 0.05s und 0.2s delay)
                        _force_eigenschaften_update(app)
                        _force_eigenschaften_update(app)  # Doppelt für Robustheit

                        # UI-Refresh (war separater 0.1s delay)
                        _force_trigger_ui_refresh(app)

                        Logger.debug("VOLK_FUNKTIONEN: Konsolidierte Update-Sequenz abgeschlossen")
                    except Exception as e:
                        Logger.warning(f"Konsolidierte Update-Sequenz fehlgeschlagen: {e}")

                # Einziger Clock-Call statt 3 kaskadierten
                Clock.schedule_once(consolidated_update_sequence, 0)
        except Exception as e:
            Logger.warning(f"Direktes Eigenschaften-Update fehlgeschlagen: {e}")

        return True
        
    except Exception as e:
        Logger.error(f"Fehler bei freier Attribut-Auswahl: {e}", exc_info=True)
        return False


def waehle_freies_attribut_malus(charakter, volk_name, attribut_name):
    """
    Wählt ein freies Attribut für ein Volk aus und senkt es per Attributsschwäche.
    Attributsschwäche: W4 bleibt W4, aber Modifier = -2.

    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        attribut_name: Name des zu schwächenden Attributs

    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.debug(f"Wähle freies Attribut-Malus '{attribut_name}' für Volk '{volk_name}'")

        if attribut_name in [NO_ATTRIBUT_AVAILABLE_TEXT, "Keine Attribute verfügbar"]:
            Logger.warning("Ungültiges Attribut für Malus ausgewählt")
            return False

        # Prüfen ob Attribut existiert
        if not hasattr(charakter, 'attribute') or attribut_name not in charakter.attribute:
            Logger.error(f"Attribut '{attribut_name}' nicht gefunden")
            return False

        attribut = charakter.attribute[attribut_name]

        # Attributsabzug: Würfelwert bleibt W4, Modifier wird auf den gewählten Wert gesetzt
        malus_wert = -2  # Standardwert
        if volk_name in charakter.voelker:
            volk = charakter.voelker[volk_name]
            if hasattr(volk, 'effects'):
                malus_wert = volk.effects.get('attribut_malus_wert', -2)
        attribut.wuerfel.modifier = malus_wert
        Logger.info(f"Attributsabzug '{attribut_name}' für Volk '{volk_name}': W4{malus_wert:+d}")

        # Abgeleitete Werte neu berechnen
        if hasattr(charakter, 'berechne_abgeleitete_werte'):
            charakter.berechne_abgeleitete_werte()

        # Event für UI-Update auslösen
        if hasattr(charakter, 'dispatch'):
            charakter.dispatch('on_charakter_change')

        # Direkte Eigenschaften-View-Update erzwingen
        try:
            from kivy.app import App
            from kivy.clock import Clock
            app = App.get_running_app()
            if hasattr(app, 'controller') and hasattr(app.controller, 'charakter'):
                def consolidated_update_sequence(dt):
                    try:
                        _force_eigenschaften_update(app)
                        _force_eigenschaften_update(app)
                        _force_trigger_ui_refresh(app)
                        Logger.debug("VOLK_FUNKTIONEN: Malus-Konsolidierte Update-Sequenz abgeschlossen")
                    except Exception as e:
                        Logger.warning(f"Malus-Konsolidierte Update-Sequenz fehlgeschlagen: {e}")

                Clock.schedule_once(consolidated_update_sequence, 0)
        except Exception as e:
            Logger.warning(f"Direktes Eigenschaften-Update für Malus fehlgeschlagen: {e}")

        return True

    except Exception as e:
        Logger.error(f"Fehler bei freier Attribut-Malus-Auswahl: {e}", exc_info=True)
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


def waehle_magieaffin_fertigkeit(charakter, volk_name, ah_talent_name):
    """
    Wählt einen Arkanen Hintergrund (AH) für Magieaffin aus.
    Setzt das gewählte AH-Talent und erhöht die in der Talent-Beschreibung
    angegebene Arkane Fertigkeit von W4-2 auf W4+0.

    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        ah_talent_name: Name des AH-Talents (z.B. "AH (Wunder)")

    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.debug(f"Wähle Magieaffin-AH '{ah_talent_name}' für Volk '{volk_name}'")

        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            Logger.error(f"Volk '{volk_name}' nicht gefunden")
            return False

        if not hasattr(charakter, 'talente') or ah_talent_name not in charakter.talente:
            Logger.warning(f"AH-Talent '{ah_talent_name}' nicht im Charakter")
            return False

        ah_talent = charakter.talente[ah_talent_name]
        if not _ist_ah_talent(ah_talent_name):
            Logger.warning(f"Talent '{ah_talent_name}' ist kein AH-Talent")
            return False

        fertigkeit_name = extrahiere_arkane_fertigkeit_aus_ah(ah_talent)
        if not fertigkeit_name:
            Logger.warning(
                f"Konnte Arkane Fertigkeit nicht aus '{ah_talent_name}' "
                f"extrahieren (Beschreibung: {getattr(ah_talent, 'beschreibung', '')!r})"
            )
            return False

        volk = charakter.voelker[volk_name]

        # Vorherige Magieaffin-Auswahl zurücksetzen falls vorhanden
        _reset_magieaffin(charakter, volk_name)

        # Arkane Fertigkeit erhöhen: W4-2 -> W4+0 (Nicht-Grundfertigkeit)
        if fertigkeit_name in charakter.fertigkeiten:
            fertigkeit = charakter.fertigkeiten[fertigkeit_name]
            if hasattr(fertigkeit, 'wuerfel') and hasattr(fertigkeit.wuerfel, 'modifier'):
                alter_modifier = fertigkeit.wuerfel.modifier
                fertigkeit.wuerfel.modifier = 0  # W4-2 -> W4+0
                Logger.info(f"Magieaffin: '{fertigkeit_name}' von W4{alter_modifier:+d} auf W4+0 erhöht")
            else:
                Logger.warning(f"Magieaffin: Würfel-Objekt nicht gefunden für '{fertigkeit_name}'")
        else:
            Logger.warning(f"Magieaffin: Fertigkeit '{fertigkeit_name}' nicht im Charakter gefunden")

        # Magieaffin-Auswahl im Volk speichern (sowohl AH-Talent als auch Fertigkeit)
        if 'magieaffin_auswahl' not in volk.effects:
            volk.effects['magieaffin_auswahl'] = {}
        volk.effects['magieaffin_auswahl']['ah_talent'] = ah_talent_name
        volk.effects['magieaffin_auswahl']['fertigkeit'] = fertigkeit_name

        # Gewähltes AH-Talent automatisch auswählen
        if not ah_talent.ausgewaehlt:
            ah_talent.ausgewaehlt = True
            if ah_talent_name not in charakter.selected_talente:
                charakter.selected_talente.append(ah_talent_name)
            Logger.info(f"Magieaffin: AH-Talent '{ah_talent_name}' automatisch ausgewählt")

        # Abgeleitete Werte neu berechnen
        if hasattr(charakter, 'berechne_abgeleitete_werte'):
            charakter.berechne_abgeleitete_werte()

        # Event für UI-Update auslösen
        if hasattr(charakter, 'dispatch'):
            charakter.dispatch('on_charakter_change')

        try:
            from kivy.app import App
            from kivy.clock import Clock
            app = App.get_running_app()
            if hasattr(app, 'controller') and hasattr(app.controller, 'charakter'):
                def consolidated_update_sequence(dt):
                    try:
                        _force_eigenschaften_update(app)
                        _force_eigenschaften_update(app)
                        _force_trigger_ui_refresh(app)
                    except Exception as e:
                        Logger.warning(f"Konsolidierte Update-Sequenz fehlgeschlagen: {e}")
                Clock.schedule_once(consolidated_update_sequence, 0)
        except Exception as e:
            Logger.warning(f"Direktes Eigenschaften-Update fehlgeschlagen: {e}")

        return True

    except Exception as e:
        Logger.error(f"Fehler bei Magieaffin-Auswahl: {e}", exc_info=True)
        return False


def _reset_magieaffin(charakter, volk_name):
    """Setzt die Magieaffin-Auswahl zurück (AH-Talent abwählen, Fertigkeit auf W4-2)."""
    try:
        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            return

        volk = charakter.voelker[volk_name]
        auswahl = volk.effects.get('magieaffin_auswahl', {})
        alte_fertigkeit = auswahl.get('fertigkeit')
        altes_ah_talent = auswahl.get('ah_talent')

        if not alte_fertigkeit and not altes_ah_talent:
            return

        Logger.info(
            f"Setze Magieaffin zurück für Volk '{volk_name}' "
            f"(AH={altes_ah_talent!r}, Fertigkeit={alte_fertigkeit!r})"
        )

        # Arkane Fertigkeit zurücksetzen: W4+0 -> W4-2
        if alte_fertigkeit and alte_fertigkeit in charakter.fertigkeiten:
            fertigkeit = charakter.fertigkeiten[alte_fertigkeit]
            if hasattr(fertigkeit, 'wuerfel') and hasattr(fertigkeit.wuerfel, 'modifier'):
                if fertigkeit.wuerfel.modifier == 0:
                    fertigkeit.wuerfel.modifier = -2
                    Logger.debug(f"Magieaffin: '{alte_fertigkeit}' von W4+0 auf W4-2 zurückgesetzt")

        # AH-Talent abwählen (entweder das gespeicherte oder Fallback auf das generische)
        ziel_talent = altes_ah_talent or 'Arkaner Hintergrund'
        if ziel_talent in charakter.talente:
            ah_talent = charakter.talente[ziel_talent]
            if ah_talent.ausgewaehlt and ziel_talent in charakter.selected_talente:
                ah_talent.ausgewaehlt = False
                charakter.selected_talente.remove(ziel_talent)
                Logger.debug(f"Magieaffin: AH-Talent '{ziel_talent}' entfernt")

    except Exception as e:
        Logger.error(f"Fehler beim Zurücksetzen von Magieaffin: {e}")


def get_magieaffin_optionen(charakter, volk_name):
    """
    Gibt die für Magieaffin verfügbaren Arkanen Hintergrund Talente (AH) zurück.
    Jedes AH-Talent legt seine Arkane Fertigkeit selbst fest (z.B. AH (Wunder) -> Glaube).

    Returns:
        list: Liste von Tupeln (ah_talent_name, arkane_fertigkeit_name), alphabetisch sortiert
    """
    if not hasattr(charakter, 'talente') or not charakter.talente:
        return []

    ah_talente = []
    for name, talent in charakter.talente.items():
        if not _ist_ah_talent(name):
            continue
        if not getattr(talent, 'aktiv', True):
            continue
        fertigkeit = extrahiere_arkane_fertigkeit_aus_ah(talent)
        if fertigkeit:
            ah_talente.append((name, fertigkeit))

    ah_talente.sort(key=lambda x: x[0])
    return ah_talente


def get_aktuelle_magieaffin_fertigkeit(charakter, volk_name):
    """Gibt die aktuell gewählte Arkane Fertigkeit für Magieaffin zurück."""
    try:
        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            return None
        volk = charakter.voelker[volk_name]
        return volk.effects.get('magieaffin_auswahl', {}).get('fertigkeit')
    except Exception:
        return None


def get_aktuelles_magieaffin_ah(charakter, volk_name):
    """Gibt das aktuell gewählte AH-Talent für Magieaffin zurück (oder None)."""
    try:
        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            return None
        volk = charakter.voelker[volk_name]
        return volk.effects.get('magieaffin_auswahl', {}).get('ah_talent')
    except Exception:
        return None


def hat_volk_magieaffin(charakter, volk_name):
    """Prüft ob ein Volk die Magieaffin-Eigenart hat."""
    try:
        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            return False
        volk = charakter.voelker[volk_name]
        if not hasattr(volk, 'effects'):
            return False
        spezielle_effekte = volk.effects.get('spezielle_effekte', [])
        if not spezielle_effekte:
            return False
        return any(
            (isinstance(e, dict) and e.get('typ') == 'magieaffin' and e.get('wert')) or
            (isinstance(e, str) and 'magieaffin' in e.lower())
            for e in spezielle_effekte
        )
    except Exception:
        return False


def get_volk_attribut_optionen(charakter, volk_name):
    """
    Gibt die verfügbaren Attribut-Optionen für ein Volk zurück.
    Manche Völker haben Wahlmöglichkeiten zwischen verschiedenen Attributen.
    ERWEITERT: Support für Halbork, Halbelf und Menschen.

    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks

    Returns:
        list: Liste der verfügbaren Attribut-Optionen
    """
    try:
        Logger.debug(f"[GET_VOLK_ATTRIBUT_OPTIONEN] Start für volk_name='{volk_name}'")
        Logger.debug(f"[GET_VOLK_ATTRIBUT_OPTIONEN] hasattr(charakter, 'voelker')={hasattr(charakter, 'voelker')}")
        if hasattr(charakter, 'voelker'):
            Logger.debug(f"[GET_VOLK_ATTRIBUT_OPTIONEN] volk_name in charakter.voelker: {volk_name in charakter.voelker}")

        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            Logger.warning(f"Volk '{volk_name}' nicht gefunden bei Attribut-Optionen-Abfrage")
            return [NO_ATTRIBUT_AVAILABLE_TEXT]

        volk = charakter.voelker[volk_name]
        Logger.debug(f"[GET_VOLK_ATTRIBUT_OPTIONEN] volk gefunden, hasattr(volk, 'effects')={hasattr(volk, 'effects')}")

        # Prüfe effects/wahlmoeglichkeiten für spezifische Attribut-Optionen
        if hasattr(volk, 'effects'):
            wahlmoeglichkeiten = volk.effects.get('wahlmoeglichkeiten', {})
            Logger.debug(f"[GET_VOLK_ATTRIBUT_OPTIONEN] wahlmoeglichkeiten = {wahlmoeglichkeiten}")
            
            # Halbork: Attribut Stärke oder Konstitution wählen
            if wahlmoeglichkeiten.get('attribut_staerke_oder_konstitution', False):
                Logger.debug(f"Halbork Attribut-Optionen: Stärke oder Konstitution")
                return ["Stärke", "Konstitution"]
            
            # Prüfe auf freies_talent_oder_attribut (z.B. SWAE Halbelf)
            if wahlmoeglichkeiten.get('freies_talent_oder_attribut', False):
                # ENTWEDER/ODER Wahl: Für Halbelf ist das Attribut Geschicklichkeit
                if volk_name.lower() in ["halbelf", "halbelfen"]:
                    Logger.debug(f"Halbelf Attribut-Option (ENTWEDER/ODER): Geschicklichkeit")
                    return ["Geschicklichkeit"]
                # Anderes Volk mit diesem Schlüssel? Unwahrscheinlich, aber Fallback
                return get_verfuegbare_attribute(charakter)
            
            # Prüfe auf freies_attribut (ohne freies_talent_oder_attribut)
            if wahlmoeglichkeiten.get('freies_attribut', False):
                # freies_attribut: true bedeutet freie Auswahl eines Attributs (alle Attribute)
                # Nur wenn auch freies_talent_oder_attribut vorhanden, ist es SWAE Halbelf mit festem Attribut
                # Aber das wird oben bereits abgefangen (freies_talent_oder_attribut)
                # Also: freies_attribut: true -> alle Attribute
                Logger.debug(f"Freies Attribut verfügbar für '{volk_name}' -> alle Attribute")
                return get_verfuegbare_attribute(charakter)
        
        # Fallback: Alte Volk-Namen-basierte Prüfung (nur wenn effects nicht vorhanden)
        if not hasattr(volk, 'effects'):
            if volk_name.lower() in ["halbork", "halborks"]:
                # Halborks können zwischen Stärke und Konstitution wählen
                Logger.warning(f"Halbork Attribut-Optionen (Fallback ohne effects): Stärke oder Konstitution")
                return ["Stärke", "Konstitution"]
            
            elif volk_name.lower() in ["halbelf", "halbelfen"]:
                # Halbelfen können Geschicklichkeit wählen (als Teil der ENTWEDER/ODER Wahl)
                Logger.warning(f"Halbelf Attribut-Option (Fallback ohne effects): Geschicklichkeit")
                return ["Geschicklichkeit"]
        
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
    ERWEITERT: Bessere Debug-Ausgabe für Goblin und Menschen-Support.
    
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
            'attribut_optionen': [],
            'halbelf_entweder_oder': False,
            'menschen_vielseitig': False,
            'beide_optionen': False,  # Talent UND Attribut (z.B. Savage Pathfinder Mensch)
            # Multi-Slot-Erweiterung: Slot-Listen pro Wahlmöglichkeitstyp.
            # Jeder Eintrag entspricht einer Eigenart-Instanz, die der User belegen muss.
            'slots': {}
        }
        
        # Prüfen ob Volk existiert
        if not hasattr(charakter, 'voelker') or volk_name not in charakter.voelker:
            Logger.warning(f"Volk '{volk_name}' nicht gefunden bei Zusatzelemente-Abfrage")
            return zusatzelemente
        
        # Bereinigung durchführen
        _cleanup_voelker_selected(charakter)
        
        Logger.debug(f"=== ZUSATZELEMENTE DEBUG für '{volk_name}' ===")
        
        # ERWEITERT: Prüfe ob Volk ENTWEDER/ODER Wahlmöglichkeit hat (z.B. Halbelf in einigen Settings)
        volk = charakter.voelker[volk_name]
        if hasattr(volk, 'effects'):
            wahlmoeglichkeiten = volk.effects.get('wahlmoeglichkeiten', {})
            if wahlmoeglichkeiten.get('freies_talent_oder_attribut', False):
                zusatzelemente['halbelf_entweder_oder'] = True
                Logger.debug(f"ENTWEDER/ODER Wahlmöglichkeit verfügbar für '{volk_name}' (freies_talent_oder_attribut)")
                return zusatzelemente  # Spezielle Sektion
        
        # ERWEITERT: Menschen-Vielseitig (freies Talent ODER 2 Fertigkeitspunkte)
        if hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_talent_oder_fertigkeitspunkte'):
            zusatzelemente['menschen_vielseitig'] = True
            Logger.debug(f"Menschen Vielseitig Wahlmöglichkeit verfügbar für '{volk_name}'")
            return zusatzelemente  # Früher Return - spezielle Sektion

        # ERWEITERT: Goblin-spezifische Debug-Ausgabe
        if volk_name.lower() in ["goblin", "goblins"]:
            Logger.debug(f"🔍 GOBLIN SPEZIAL-CHECK für '{volk_name}'")
            
            # Alle Wahlmöglichkeiten-Varianten prüfen
            freies_talent_check1 = hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_talent')
            freies_talent_check2 = hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_anfaengertalent')
            
            Logger.debug(f"GOBLIN freies_talent: {freies_talent_check1}")
            Logger.debug(f"GOBLIN freies_anfaengertalent: {freies_talent_check2}")
            
            if freies_talent_check1 or freies_talent_check2:
                zusatzelemente['freie_talente'] = True
                Logger.info(f"✅ GOBLIN: Freie Talente aktiviert für '{volk_name}'")
            else:
                Logger.warning(f"❌ GOBLIN: Keine freien Talente erkannt für '{volk_name}'")
        
        # Counts pro Wahlmöglichkeit aus den Volk-Effekten holen (Multi-Slot-Quelle).
        volk_obj = charakter.voelker.get(volk_name)
        wm_counts = {}
        if volk_obj and hasattr(volk_obj, 'effects'):
            wm_counts = volk_obj.effects.get('wahlmoeglichkeiten_counts', {}) or {}

        def _slot_count(typ, fallback_flag):
            """Anzahl der Slots für eine Wahlmöglichkeit. Counts haben Vorrang,
            sonst 1 wenn das Legacy-Flag gesetzt ist, sonst 0."""
            n = wm_counts.get(typ, 0)
            if n:
                return n
            return 1 if fallback_flag else 0

        # Standard-Wahlmöglichkeiten prüfen
        if not zusatzelemente['freie_talente']:  # Nur wenn nicht bereits durch Goblin gesetzt
            if hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_talent') or \
               hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freies_anfaengertalent'):
                zusatzelemente['freie_talente'] = True
                Logger.debug(f"Standard: Freie Talente verfügbar für '{volk_name}'")

        # Slot-Liste für freie Talente (auch bei Goblin-Pfad).
        n_talent = _slot_count('freies_talent', zusatzelemente['freie_talente'])
        if n_talent:
            zusatzelemente['slots']['freies_talent'] = [
                {'index': i, 'value': None} for i in range(n_talent)
            ]

        # Attribut-Optionen abrufen (für Bonus)
        attribut_optionen = get_volk_attribut_optionen(charakter, volk_name)
        Logger.debug(f"[GET_VOLK_ZUSATZELEMENTE] attribut_optionen = {attribut_optionen}")
        if attribut_optionen and attribut_optionen != [NO_ATTRIBUT_AVAILABLE_TEXT]:
            zusatzelemente['freies_attribut'] = attribut_optionen[0] if attribut_optionen else True
            zusatzelemente['attribut_optionen'] = attribut_optionen
            Logger.debug(f"Attribut-Optionen verfügbar für '{volk_name}': {attribut_optionen}")
            n_attr = _slot_count('freies_attribut', True)
            if n_attr:
                zusatzelemente['slots']['freies_attribut'] = [
                    {'index': i, 'value': None, 'options': list(attribut_optionen)}
                    for i in range(n_attr)
                ]

        # Attribut-Malus-Optionen abrufen (separater Key)
        # Attributsschwäche erlaubt nur W4-Attribute (Basis-Wert ohne Malus),
        # die dann auf W4-2 gesenkt werden.
        if volk_name in charakter.voelker:
            volk = charakter.voelker[volk_name]
            if hasattr(volk, 'effects'):
                wahlmoeglichkeiten = volk.effects.get('wahlmoeglichkeiten', {})
                if wahlmoeglichkeiten.get('freies_attribut_malus', False):
                    malus_optionen = get_staerkbare_attribute(charakter)
                    if malus_optionen:
                        zusatzelemente['freies_attribut_malus'] = malus_optionen[0] if malus_optionen else True
                        zusatzelemente['attribut_malus_optionen'] = malus_optionen
                        Logger.debug(f"Attribut-Malus-Optionen verfügbar für '{volk_name}': {malus_optionen}")
                        n_malus = _slot_count('freies_attribut_malus', True)
                        if n_malus:
                            zusatzelemente['slots']['freies_attribut_malus'] = [
                                {'index': i, 'value': None, 'options': list(malus_optionen)}
                                for i in range(n_malus)
                            ]

        if hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freie_verstandsfertigkeit') or \
           hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freie_grundfertigkeit') or \
           hat_volk_wahlmoeglichkeit(charakter, volk_name, 'freie_nicht_grundfertigkeit'):
            zusatzelemente['freie_fertigkeiten'] = True
            Logger.debug(f"Freie Fertigkeiten verfügbar für '{volk_name}'")

        # Slots für freie Fertigkeiten (Grund- und Nicht-Grund werden im Overlay
        # weiter aufgeschlüsselt, hier nur die Gesamtzahl als 'freie_fertigkeit').
        n_fert = _slot_count('freie_grundfertigkeit', False) + \
                 _slot_count('freie_nicht_grundfertigkeit', False)
        if not n_fert and zusatzelemente['freie_fertigkeiten']:
            n_fert = 1
        if n_fert:
            zusatzelemente['slots']['freie_fertigkeit'] = [
                {'index': i, 'value': None} for i in range(n_fert)
            ]

        # Magieaffin-Eigenart prüfen
        if hat_volk_magieaffin(charakter, volk_name):
            zusatzelemente['magieaffin'] = True
            Logger.debug(f"Magieaffin verfügbar für '{volk_name}'")

        Logger.debug(f"=== FINALE Zusatzelemente für '{volk_name}': {zusatzelemente} ===")
        return zusatzelemente
        
    except Exception as e:
        Logger.error(f"Fehler beim Abrufen der Zusatzelemente für '{volk_name}': {e}")
        return {
            'freie_talente': False,
            'freie_attribute': False,
            'freie_fertigkeiten': False,
            'attribut_optionen': [],
            'halbelf_entweder_oder': False,
            'menschen_vielseitig': False
        }


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

        def _as_list(v):
            """Akzeptiert sowohl Listen (neue Multi-Slot-Form) als auch Skalare (Legacy)."""
            if v is None:
                return []
            if isinstance(v, list):
                return [x for x in v if x]
            return [v]

        # Alle Auswahlen zurücksetzen
        for auswahl_typ, auswahl_wert in auswahl.items():
            werte = _as_list(auswahl_wert)
            for wert in werte:
                if auswahl_typ == 'talent':
                    # Talent abwählen
                    if hasattr(charakter, 'selected_talente') and wert in charakter.selected_talente:
                        charakter.selected_talente.remove(wert)
                    if hasattr(charakter, 'talente') and wert in charakter.talente:
                        charakter.talente[wert].ausgewaehlt = False

                elif auswahl_typ == 'attribut':
                    # Attribut-Erhöhung rückgängig machen
                    if hasattr(charakter, 'attribute') and wert in charakter.attribute:
                        charakter.attribute[wert].wert -= 1

                elif auswahl_typ == 'attribut_malus':
                    # Attribut-Schwächung rückgängig machen (Umkehr von waehle_freies_attribut_malus)
                    if hasattr(charakter, 'attribute') and wert in charakter.attribute:
                        attr = charakter.attribute[wert]
                        if attr.wert >= 10:
                            attr.wert += 2
                        else:
                            attr.wert += 1

                elif auswahl_typ == 'fertigkeit':
                    # Fertigkeits-Erhöhung rückgängig machen
                    if hasattr(charakter, 'fertigkeiten') and wert in charakter.fertigkeiten:
                        charakter.fertigkeiten[wert].wert -= 1
        
        # Auswahl aus Dictionary entfernen
        del auswahlen_dict[volk_name]
        
        Logger.debug(f"Auswahlen für Volk '{volk_name}' zurückgesetzt")
        return True
        
    except Exception as e:
        Logger.error(f"Fehler beim Zurücksetzen der Auswahlen für '{volk_name}': {e}")
        return False


def reconcile_volk_auswahlen(charakter, volk_name, auswahlen_dict, slot_targets):
    """
    Trimmt Auswahlen so, dass jede Liste höchstens so lang ist wie die neue
    Slot-Anzahl pro Typ. Überzählige Werte werden zurückgerollt (Attribut wieder
    senken, Talent abwählen, etc.).

    Wird gerufen, wenn der User ein bestehendes Custom-Volk editiert und
    `max_auswahl` reduziert, sodass weniger Slots verbleiben als bisher belegt.

    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        auswahlen_dict: voelker_auswahlen-Dict (wird mutiert)
        slot_targets: Dict {auswahl_typ: max_slots} - z.B. {'attribut': 1, 'talent': 2}
    """
    if volk_name not in auswahlen_dict:
        return

    auswahl = auswahlen_dict[volk_name]
    for typ, target in slot_targets.items():
        werte = auswahl.get(typ)
        if not isinstance(werte, list):
            continue
        if len(werte) <= target:
            continue
        # Überzählige Werte zurückrollen
        ueberschuss = werte[target:]
        for wert in ueberschuss:
            if not wert:
                continue
            if typ == 'talent':
                if hasattr(charakter, 'selected_talente') and wert in charakter.selected_talente:
                    charakter.selected_talente.remove(wert)
                if hasattr(charakter, 'talente') and wert in charakter.talente:
                    charakter.talente[wert].ausgewaehlt = False
            elif typ == 'attribut':
                if hasattr(charakter, 'attribute') and wert in charakter.attribute:
                    charakter.attribute[wert].wert -= 1
            elif typ == 'attribut_malus':
                if hasattr(charakter, 'attribute') and wert in charakter.attribute:
                    attr = charakter.attribute[wert]
                    attr.wert += 2 if attr.wert >= 10 else 1
            elif typ == 'fertigkeit':
                if hasattr(charakter, 'fertigkeiten') and wert in charakter.fertigkeiten:
                    charakter.fertigkeiten[wert].wert -= 1
        auswahl[typ] = werte[:target]


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


# NEUE FUNKTIONEN für Halbelf ENTWEDER/ODER Logik

def waehle_halbelf_talent(charakter, volk_name, talent_name, ignore_voraussetzungen=False):
    """
    Wählt ein freies Talent für Halbelf aus (ENTWEDER-Teil der Wahl).
    ERWEITERT: Verhindert Mehrfachauswahl und setzt Attribut-Wahl zurück.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks (sollte Halbelf sein)
        talent_name: Name des zu wählenden Talents
        ignore_voraussetzungen: Voraussetzungsprüfung überspringen (default: False)
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
        str: "needs_voraussetzungen_confirmation" wenn Voraussetzungen nicht erfüllt
    """
    try:
        Logger.debug(f"Halbelf wählt freies Talent '{talent_name}' für Volk '{volk_name}' (ignore_voraussetzungen={ignore_voraussetzungen})")
        
        if volk_name.lower() not in ["halbelf", "halbelfen"]:
            Logger.error(f"Halbelf-Talent-Wahl nur für Halbelfen, nicht für '{volk_name}'")
            return False
        
        # NEUE LOGIK: Prüfen ob bereits ein Talent gewählt wurde
        aktuelles_talent = _get_halbelf_freies_talent(charakter)
        if aktuelles_talent and aktuelles_talent != talent_name:
            Logger.info(f"Halbelf: Setze vorheriges freies Talent '{aktuelles_talent}' zurück")
            # Vorheriges Talent abwählen (inkl. AH-Effekte, Mächte, Machtpunkte)
            from functions.talent_funktionen import talent_abwaehlen
            talent_abwaehlen(charakter, aktuelles_talent)
        
        # NEUE LOGIK: Wenn Attribut bereits gewählt wurde, zurücksetzen (ENTWEDER/ODER)
        if _get_halbelf_attribut_gewaehlt(charakter):
            Logger.info("Halbelf: Setze Geschicklichkeits-Bonus zurück (ENTWEDER/ODER)")
            if hasattr(charakter, 'attribute') and 'Geschicklichkeit' in charakter.attribute:
                geschicklichkeit = charakter.attribute['Geschicklichkeit']
                if geschicklichkeit.wert == 6:  # Von W6 auf W4 zurücksetzen
                    geschicklichkeit.wert = 4
                    Logger.debug("Geschicklichkeit von W6 auf W4 zurückgesetzt")
            _set_halbelf_attribut_gewaehlt(charakter, False)
        
        # Standard Talent-Auswahl durchführen
        result = waehle_freies_talent(charakter, volk_name, talent_name, ignore_voraussetzungen)
        
        if result is True:
            # Markiere, dass Halbelf die Talent-Option gewählt hat
            _set_halbelf_freies_talent(charakter, talent_name)
            Logger.info(f"Halbelf '{volk_name}' hat freies Talent '{talent_name}' gewählt")
            return True
        elif result == "needs_voraussetzungen_confirmation":
            return "needs_voraussetzungen_confirmation"
        
        return False
        
    except Exception as e:
        Logger.error(f"Fehler bei Halbelf-Talent-Auswahl: {e}", exc_info=True)
        return False


def waehle_halbelf_attribut(charakter, volk_name):
    """
    Wählt den Geschicklichkeits-Bonus für Halbelf aus (ODER-Teil der Wahl).
    ERWEITERT: Verhindert Mehrfachauswahl und setzt Talent-Wahl zurück.
    
    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks (sollte Halbelf sein)
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.debug(f"Halbelf wählt Geschicklichkeits-Bonus für Volk '{volk_name}'")
        
        if volk_name.lower() not in ["halbelf", "halbelfen"]:
            Logger.error(f"Halbelf-Attribut-Wahl nur für Halbelfen, nicht für '{volk_name}'")
            return False
        
        # NEUE LOGIK: Prüfen ob bereits Attribut gewählt wurde
        if _get_halbelf_attribut_gewaehlt(charakter):
            Logger.info("Halbelf: Geschicklichkeits-Bonus bereits gewählt")
            return True  # Bereits gewählt, nichts zu tun
        
        # NEUE LOGIK: Wenn Talent bereits gewählt wurde, zurücksetzen (ENTWEDER/ODER)
        aktuelles_talent = _get_halbelf_freies_talent(charakter)
        if aktuelles_talent:
            Logger.info(f"Halbelf: Setze vorheriges freies Talent '{aktuelles_talent}' zurück (ENTWEDER/ODER)")
            # Talent abwählen
            if aktuelles_talent in charakter.talente:
                talent = charakter.talente[aktuelles_talent]
                talent.ausgewaehlt = False
                
                # Aus selected_talente entfernen
                if hasattr(charakter, 'selected_talente') and aktuelles_talent in charakter.selected_talente:
                    charakter.selected_talente.remove(aktuelles_talent)
                    Logger.debug(f"Talent '{aktuelles_talent}' aus selected_talente entfernt")
            _set_halbelf_freies_talent(charakter, None)
        
        # Geschicklichkeits-Bonus anwenden
        success = waehle_freies_attribut(charakter, volk_name, "Geschicklichkeit")
        
        if success:
            # Markiere, dass Halbelf die Attribut-Option gewählt hat
            _set_halbelf_attribut_gewaehlt(charakter, True)
            Logger.info(f"Halbelf '{volk_name}' hat Geschicklichkeits-Bonus gewählt")
            return True
        
        return False
        
    except Exception as e:
        Logger.error(f"Fehler bei Halbelf-Attribut-Auswahl: {e}", exc_info=True)
        return False


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


# NEUE FUNKTIONEN für Menschen-Vielseitig (freies Talent ODER 2 Fertigkeitspunkte)

def waehle_mensch_talent(charakter, volk_name, talent_name, ignore_voraussetzungen=False):
    """
    Wählt ein freies Talent für einen Menschen aus (Vielseitig ENTWEDER-Teil).
    Setzt ggf. vorherige Fertigkeitspunkte-Wahl zurück.

    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks
        talent_name: Name des zu wählenden Talents
        ignore_voraussetzungen: Voraussetzungsprüfung überspringen (default: False)

    Returns:
        bool: True bei Erfolg, False bei Fehler
        str: "needs_voraussetzungen_confirmation" wenn Voraussetzungen nicht erfüllt
    """
    try:
        Logger.debug(f"Mensch Vielseitig: Wähle freies Talent '{talent_name}' für '{volk_name}' (ignore_voraussetzungen={ignore_voraussetzungen})")

        # Fertigkeitspunkte-Wahl zurücksetzen falls vorhanden
        if _get_mensch_fertigkeitspunkte_gewaehlt(charakter):
            Logger.info("Mensch Vielseitig: Setze Fertigkeitspunkte-Wahl zurück (ENTWEDER/ODER)")
            _reset_mensch_fertigkeitspunkte(charakter)

        # Standard freies Talent auswählen
        result = waehle_freies_talent(charakter, volk_name, talent_name, ignore_voraussetzungen)

        if result is True:
            Logger.info(f"Mensch Vielseitig: Talent '{talent_name}' gewählt für '{volk_name}'")

        return result

    except Exception as e:
        Logger.error(f"Fehler bei Mensch-Vielseitig-Talent-Auswahl: {e}", exc_info=True)
        return False


def waehle_mensch_fertigkeitspunkte(charakter, volk_name):
    """
    Wählt +2 Fertigkeitspunkte für einen Menschen aus (Vielseitig ODER-Teil).
    Setzt ggf. vorherige Talent-Wahl zurück.

    Args:
        charakter: Das Charakterobjekt
        volk_name: Name des Volks

    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        Logger.debug(f"Mensch Vielseitig: Wähle +2 Fertigkeitspunkte für '{volk_name}'")

        # Bereits gewählt?
        if _get_mensch_fertigkeitspunkte_gewaehlt(charakter):
            Logger.info("Mensch Vielseitig: Fertigkeitspunkte bereits gewählt")
            return True

        # Talent-Wahl zurücksetzen falls vorhanden
        aktuelles_talent = _get_menschen_freies_talent(charakter)
        if aktuelles_talent:
            Logger.info(f"Mensch Vielseitig: Setze Talent '{aktuelles_talent}' zurück (ENTWEDER/ODER)")
            _reset_menschen_freies_talent(charakter)

        # +2 Fertigkeitspunkte gewähren
        if hasattr(charakter, 'verbleibende_fertigkeitssteigerungen'):
            charakter.verbleibende_fertigkeitssteigerungen += 2
            Logger.debug(f"Verbleibende Fertigkeitssteigerungen erhöht auf {charakter.verbleibende_fertigkeitssteigerungen}")
        if hasattr(charakter, 'maximale_fertigkeitssteigerungen'):
            charakter.maximale_fertigkeitssteigerungen += 2
            Logger.debug(f"Maximale Fertigkeitssteigerungen erhöht auf {charakter.maximale_fertigkeitssteigerungen}")

        # Tracking setzen
        _set_mensch_fertigkeitspunkte_gewaehlt(charakter, True)

        Logger.info(f"Mensch Vielseitig: +2 Fertigkeitspunkte gewählt für '{volk_name}'")
        return True

    except Exception as e:
        Logger.error(f"Fehler bei Mensch-Vielseitig-Fertigkeitspunkte-Auswahl: {e}", exc_info=True)
        return False


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