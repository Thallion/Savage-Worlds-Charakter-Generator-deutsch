# functions/volk_wahlmoeglichkeiten.py
"""
Volk-Wahlmöglichkeiten: freie Talente/Attribute/Fertigkeiten und das
Magieaffin-System (AH-Wahl).
Teil des aufgeteilten volk_funktionen-Moduls; Fassade: functions/volk_funktionen.py
"""

import logging
import re
from kivy.logger import Logger
from functions.volk_core import (
    NO_ATTRIBUT_AVAILABLE_TEXT,
    NO_FERTIGKEIT_AVAILABLE_TEXT,
    NO_TALENT_AVAILABLE_TEXT,
    _force_eigenschaften_update,
    _force_trigger_ui_refresh,
    _get_menschen_freies_attribut,
    _get_menschen_freies_talent,
    _ist_ah_talent,
    _set_menschen_freies_attribut,
    _set_menschen_freies_talent,
    extrahiere_arkane_fertigkeit_aus_ah,
    hat_volk_wahlmoeglichkeit,
)


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
        # WICHTIG: Wuerfel.value direkt setzen, damit Synchronisation mit attribut.wert funktioniert
        if alter_wert == 4:
            attribut.wuerfel.value = 6  # W4 -> W6 (Standard-Völker-Bonus)
        else:
            # Fallback: um einen Würfeltyp erhöhen
            next_values = [4, 6, 8, 10, 12]
            current_idx = next_values.index(attribut.wuerfel.value) if attribut.wuerfel.value in next_values else 0
            if current_idx < len(next_values) - 1:
                attribut.wuerfel.value = next_values[current_idx + 1]
            else:
                # Bei W12: Modifier erhöhen
                attribut.wuerfel.modifier += 1
        
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
