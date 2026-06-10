# functions/volk_zusatzelemente.py
"""
Volk-Zusatzelemente: dynamische Zusatz-Auswahlen (Multi-Slot) inkl.
Reset/Reconcile der Auswahl-Dictionaries.
Teil des aufgeteilten volk_funktionen-Moduls; Fassade: functions/volk_funktionen.py
"""

import logging
import re
from kivy.logger import Logger
from functions.volk_core import (
    NO_ATTRIBUT_AVAILABLE_TEXT,
    _cleanup_voelker_selected,
    hat_volk_wahlmoeglichkeit,
)
from functions.volk_wahlmoeglichkeiten import (
    get_staerkbare_attribute,
    get_verfuegbare_attribute,
    hat_volk_magieaffin,
    waehle_freies_attribut_malus,
)


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
