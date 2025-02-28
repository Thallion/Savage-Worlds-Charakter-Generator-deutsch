"""
Modul für die Verwaltung von Attributen und Fertigkeiten im Charakter.
Dieses Modul enthält Funktionen zur Verwaltung der Charakter-Eigenschaften,
einschließlich der Initialisierung, Steigerung und Senkung von Attributen und Fertigkeiten.
"""

import json
import os
from kivy.logger import Logger
from models.wuerfel import Wuerfel
from models.attribut import Attribut
from models.fertigkeit import Fertigkeit


#-----------------------------------------------
# Attribut-Funktionen
#-----------------------------------------------

def initialisiere_attribute(self):
    """Initialisiert die Basisattribute für den Charakter."""
    # Standard Savage Worlds Attribute
    standard_attribute = {
        "Stärke": {"wert": 4, "modifier": 0},
        "Geschicklichkeit": {"wert": 4, "modifier": 0},
        "Konstitution": {"wert": 4, "modifier": 0},
        "Verstand": {"wert": 4, "modifier": 0},
        "Willenskraft": {"wert": 4, "modifier": 0}
    }
    
    # Attribute erstellen
    self.attribute = {}
    for name, daten in standard_attribute.items():
        attribut = Attribut(
            attribut_name=name,  # This is the key change - using attribut_name parameter
            wert=daten["wert"],
            modifier=daten["modifier"]
        )
        attribut.bind(wert=self.on_attribut_wert_change)
        attribut.bind(modifier=self.on_attribut_modifier_change)
        self.attribute[name] = attribut
    
    self.verbleibende_attributsteigerungen = 5


def get_attribute_dict(charakter):
    """
    Gibt ein Wörterbuch aller Attribute zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        Dictionary mit allen Attributen
    """
    return charakter.attribute


def steigere_attribut(charakter, attribut_name):
    """
    Steigert ein Attribut um eine Stufe.
    
    Args:
        charakter: Das Charakter-Objekt
        attribut_name: Der Name des zu steigernden Attributs
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    def steigern():
        """Führt die eigentliche Steigerung des Attributs durch."""
        attribut.wuerfel.increase()
        Logger.debug(f"Attribut '{attribut_name}' wurde auf W{attribut.wuerfel.value}+{attribut.wuerfel.modifier} gesteigert.")
        charakter.rang = charakter.get_rang(charakter.aufstiege_gesamt)
        charakter.berechne_abgeleitete_werte()
        return True

    attribut = charakter.attribute.get(attribut_name)
    if not attribut:
        Logger.error(f"Attribut '{attribut_name}' existiert nicht.")
        return False

    aktueller_wert = attribut.wuerfel.value
    aktueller_modifier = attribut.wuerfel.modifier
    
    # Bestimme die Kosten basierend auf dem Spielfortschritt
    if charakter.char_gen_completed:
        # Während des Spiels kostet eine Attributsteigerung 2 Aufstiege
        kosten = 2
        if charakter.verbleibende_aufstiege >= kosten:
            charakter.verbleibende_aufstiege -= kosten
            steigern()
            return True
        else:
            Logger.warning("Nicht genügend verbleibende Aufstiege.")
            return False
    else:
        # Während der Charaktergenerierung
        kosten = 1
        if charakter.verbleibende_attributsteigerungen >= kosten:
            charakter.verbleibende_attributsteigerungen -= kosten
            steigern()
            return True
        else:
            Logger.warning("Nicht genügend verbleibende Attributsteigerungen.")
            return False


def senke_attribut(charakter, attribut_name):
    """
    Senkt ein Attribut um eine Stufe.
    
    Args:
        charakter: Das Charakter-Objekt
        attribut_name: Der Name des zu senkenden Attributs
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    def senken():
        """Führt die eigentliche Senkung des Attributs durch."""
        erfolg = attribut.wuerfel.decrease()
        Logger.debug(f"Attribut '{attribut_name}' gesenkt auf W{attribut.wuerfel.value}+{attribut.wuerfel.modifier}")
        charakter.update_char_gen_status()
        charakter.rang = charakter.get_rang(charakter.aufstiege_gesamt)
        charakter.berechne_abgeleitete_werte()
        return erfolg

    attribut = charakter.attribute.get(attribut_name)
    if not attribut:
        Logger.error(f"Attribut '{attribut_name}' existiert nicht.")
        return False

    # Bestimme die Kosten basierend auf dem Spielfortschritt
    if charakter.char_gen_completed:
        # Während des Spiels
        kosten = 2
        if charakter.verbleibende_aufstiege < charakter.aufstiege_gesamt:
            charakter.verbleibende_aufstiege += kosten
            senken()
            return True
        else:
            Logger.warning("Maximum an Aufstiegen erreicht.")
            return False
    else:
        # Während der Charaktergenerierung
        kosten = 1
        if charakter.verbleibende_attributsteigerungen < charakter.maximale_attributsteigerungen:
            charakter.verbleibende_attributsteigerungen += kosten
            senken()
            return True
        else:
            Logger.warning("Maximum an Attributsteigerungen erreicht.")
            return False


#-----------------------------------------------
# Fertigkeiten-Funktionen
#-----------------------------------------------

def initialisiere_fertigkeiten(charakter):
    """
    Initialisiert die Fertigkeiten des Charakters basierend auf den in fertigkeiten_daten definierten Fertigkeiten.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    # Definiere Grundfertigkeiten
    grundfertigkeiten = [
        "Allgemeinwissen",
        "Athletik",
        "Heimlichkeit",
        "Überreden",
        "Wahrnehmung",
    ]

    # Erstellen einer Menge der Fertigkeitenamen aus fertigkeiten_daten
    fertigkeiten_namen_in_daten = set(charakter.fertigkeiten_daten.keys())
    # Erstellen einer Liste der aktuellen Fertigkeitenamen
    fertigkeiten_namen_aktuell = set(charakter.fertigkeiten.keys())

    # Aktualisieren oder Erstellen von Fertigkeiten
    for fertigkeit_name, attribut_set in charakter.fertigkeiten_daten.items():
        if isinstance(attribut_set, set) and len(attribut_set) == 1:
            attribut_name = next(iter(attribut_set))
        else:
            Logger.error(f"Fertigkeit '{fertigkeit_name}' hat eine ungültige Attribut-Zuweisung.")
            continue

        attribut_obj = charakter.attribute.get(attribut_name)
        if attribut_obj is None:
            Logger.error(f"Attribut '{attribut_name}' für Fertigkeit '{fertigkeit_name}' nicht gefunden.")
            continue

        ist_grundfertigkeit = fertigkeit_name in grundfertigkeiten

        if fertigkeit_name in charakter.fertigkeiten:
            # Bestehende Fertigkeit aktualisieren
            fertigkeit = charakter.fertigkeiten[fertigkeit_name]
            fertigkeit.attribut = attribut_obj
            fertigkeit.grundfertigkeit = ist_grundfertigkeit
        else:
            # Neue Fertigkeit erstellen
            fertigkeit = Fertigkeit(
                fertigkeit_name=fertigkeit_name,
                attribut=attribut_obj,
                grundfertigkeit=ist_grundfertigkeit,
            )
            fertigkeit.bind(wert=charakter.on_fertigkeit_wert_change)
            fertigkeit.bind(wert=charakter.on_fertigkeit_modifier_change)
            charakter.fertigkeiten[fertigkeit_name] = fertigkeit

    # Entfernen von Fertigkeiten, die nicht mehr in fertigkeiten_daten vorhanden sind
    fertigkeiten_zu_entfernen = fertigkeiten_namen_aktuell - fertigkeiten_namen_in_daten
    for fertigkeit_name in fertigkeiten_zu_entfernen:
        del charakter.fertigkeiten[fertigkeit_name]
        Logger.info(f"Fertigkeit '{fertigkeit_name}' wurde entfernt, da sie nicht im geladenen Setting vorhanden ist.")


def steigere_fertigkeit(charakter, fertigkeit_name):
    """
    Steigert eine Fertigkeit um eine Stufe.
    
    Args:
        charakter: Das Charakter-Objekt
        fertigkeit_name: Der Name der zu steigernden Fertigkeit
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    fertigkeit = charakter.fertigkeiten.get(fertigkeit_name)
    if not fertigkeit:
        Logger.error(f"Fertigkeit '{fertigkeit_name}' existiert nicht.")
        return False
        
    zugehoeriges_attribut = fertigkeit.attribut
    aktueller_total_value = fertigkeit.wuerfel.value + fertigkeit.wuerfel.modifier
    attribut_total_value = zugehoeriges_attribut.wuerfel.value + zugehoeriges_attribut.wuerfel.modifier

    # Bestimme den neuen Wert und Modifier nach der Steigerung
    if fertigkeit.wuerfel.value == 4 and fertigkeit.wuerfel.modifier == -2:
        neuer_wert = fertigkeit.wuerfel.value
        neuer_modifier = fertigkeit.wuerfel.modifier + 2
    elif fertigkeit.wuerfel.value < 12:
        neuer_wert = fertigkeit.wuerfel.value + 2
        neuer_modifier = fertigkeit.wuerfel.modifier
    elif fertigkeit.wuerfel.value == 12 and fertigkeit.wuerfel.modifier < 2:
        neuer_wert = fertigkeit.wuerfel.value
        neuer_modifier = fertigkeit.wuerfel.modifier + 1
    else:
        Logger.warning(f"Fertigkeit '{fertigkeit_name}' kann nicht weiter gesteigert werden.")
        return False

    neuer_total_value = neuer_wert + neuer_modifier

    # Bestimme die Kosten
    if charakter.char_gen_completed:
        if neuer_total_value > attribut_total_value:
            kosten = 1
        else:
            kosten = 0.5
    else:            
        if neuer_total_value > attribut_total_value:
            kosten = 2
        else:
            kosten = 1

    def steigern():
        """Führt die eigentliche Steigerung der Fertigkeit durch."""
        erfolg = fertigkeit.wuerfel.increase()
        if erfolg:
            fertigkeit.ausgewaehlt = True
            Logger.debug(f"Fertigkeit '{fertigkeit_name}' gesteigert auf W{fertigkeit.wuerfel.value}+{fertigkeit.wuerfel.modifier}")
            charakter.rang = charakter.get_rang(charakter.aufstiege_gesamt)                
            return True                
        else:
            Logger.warning(f"Fertigkeit '{fertigkeit_name}' kann nicht weiter gesteigert werden.")
            return False 

    if charakter.char_gen_completed:
        if charakter.verbleibende_aufstiege >= kosten:
            charakter.verbleibende_aufstiege -= kosten
            steigern()
            return True
        else:
            Logger.warning("Nicht genügend verbleibende Aufstiege.")
            return False
    else:
        if charakter.verbleibende_fertigkeitssteigerungen >= kosten:
            charakter.verbleibende_fertigkeitssteigerungen -= kosten
            steigern()
            return True
        else:
            if charakter.verbleibende_handicap_punkte > 0.5:
                erfolg = steigern()
                if erfolg:
                    charakter.verbleibende_handicap_punkte -= 1
                    Logger.info("Fertigkeit mit Handicap-Punkten gesteigert.")
                    return True
                return False
            else:
                Logger.warning("Nicht genügend verbleibende Fertigkeitssteigerungen.")
                return False


def senke_fertigkeit(charakter, fertigkeit_name):
    """
    Senkt eine Fertigkeit um eine Stufe und gibt die entsprechenden Steigerungen zurück.
    Grundfertigkeiten dürfen nicht von W4+0 auf W4-2 gesenkt werden.
    
    Args:
        charakter: Das Charakter-Objekt
        fertigkeit_name: Der Name der zu senkenden Fertigkeit
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    grundfertigkeiten = [
        "Allgemeinwissen",
        "Athletik",
        "Heimlichkeit",
        "Überreden",
        "Wahrnehmung",
    ]

    def senken():
        """Führt die eigentliche Senkung der Fertigkeit durch."""
        fertigkeit.wuerfel.decrease()
        Logger.debug(f"Fertigkeit '{fertigkeit_name}' gesenkt auf W{fertigkeit.wuerfel.value}+{fertigkeit.wuerfel.modifier}")
        charakter.update_char_gen_status()  # Aktualisiere den Status
        charakter.rang = charakter.get_rang(charakter.aufstiege_gesamt)

    fertigkeit = charakter.fertigkeiten.get(fertigkeit_name)
    if not fertigkeit:
        Logger.error(f"Fertigkeit '{fertigkeit_name}' existiert nicht.")
        return False
        
    # Überprüfung, ob die Fertigkeit eine Grundfertigkeit ist und ob sie bereits den Mindestmodifier hat
    if fertigkeit_name in grundfertigkeiten and fertigkeit.wuerfel.value == 4 and fertigkeit.wuerfel.modifier == 0:
        Logger.warning(f"Grundfertigkeit '{fertigkeit_name}' kann nicht von W4+0 auf W4-2 gesenkt werden.")
        return False

    zugehoeriges_attribut = fertigkeit.attribut

    # Bestimme die Kosten
    if charakter.char_gen_completed: 
        kosten = 0.5
        if fertigkeit.wuerfel.value > zugehoeriges_attribut.wuerfel.value:
            kosten = 1
    else:
        kosten = 1
        if fertigkeit.wuerfel.value > zugehoeriges_attribut.wuerfel.value:
            kosten = 2                 

    vorheriger_wert = fertigkeit.wuerfel.value
    vorheriger_modifier = fertigkeit.wuerfel.modifier

    if charakter.char_gen_completed:
        if charakter.verbleibende_aufstiege < charakter.aufstiege_gesamt:
            charakter.verbleibende_aufstiege += kosten
            senken()
            return True
        else:
            Logger.debug("Maximum Aufstiege erreicht.")
            return False
    else:
        if charakter.verbleibende_handicap_punkte < charakter.gesamt_handicap_punkte:
            charakter.verbleibende_handicap_punkte += kosten
            senken()
            return True
        else:
            if charakter.verbleibende_fertigkeitssteigerungen < charakter.maximale_fertigkeitssteigerungen:
                charakter.verbleibende_fertigkeitssteigerungen += kosten
                senken()
                return True
            else:
                Logger.warning("Maximum Fertigkeitspunkte erreicht.")
                return False


def add_fertigkeit(charakter, fertigkeit):
    """
    Fügt eine neue Fertigkeit hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
        fertigkeit: Das Fertigkeit-Objekt
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if fertigkeit.fertigkeit_name in charakter.fertigkeiten:
        Logger.warning(f"Fertigkeit '{fertigkeit.fertigkeit_name}' existiert bereits.")
        return False
    charakter.fertigkeiten[fertigkeit.fertigkeit_name] = fertigkeit
    Logger.info(f"Fertigkeit '{fertigkeit.fertigkeit_name}' hinzugefügt.")
    save_custom_fertigkeiten(charakter)
    return True


def remove_fertigkeit(charakter, fertigkeit_name):
    """
    Entfernt eine Fertigkeit.
    
    Args:
        charakter: Das Charakter-Objekt
        fertigkeit_name: Der Name der zu entfernenden Fertigkeit
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    if fertigkeit_name in charakter.fertigkeiten:
        del charakter.fertigkeiten[fertigkeit_name]
        Logger.info(f"Fertigkeit '{fertigkeit_name}' entfernt.")
        save_custom_fertigkeiten(charakter)
        return True
    Logger.warning(f"Fertigkeit '{fertigkeit_name}' existiert nicht.")
    return False


def save_custom_fertigkeiten(charakter):
    """
    Speichert die benutzerdefinierten Fertigkeiten in einer JSON-Datei.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    # Finde die benutzerdefinierten Fertigkeiten
    custom_fertigkeiten = {
        name: fertigkeit.to_dict()
        for name, fertigkeit in charakter.fertigkeiten.items()
        if getattr(fertigkeit, 'custom', False)
    }
    if custom_fertigkeiten:
        custom_fertigkeiten_file = os.path.join(os.path.dirname(__file__), 'custom_fertigkeiten.json')
        try:
            with open(custom_fertigkeiten_file, 'w', encoding='utf-8') as f:
                json.dump(custom_fertigkeiten, f, ensure_ascii=False, indent=4)
            Logger.info(f"Benutzerdefinierte Fertigkeiten wurden in {custom_fertigkeiten_file} gespeichert.")
        except Exception as e:
            Logger.error(f"Fehler beim Speichern der benutzerdefinierten Fertigkeiten: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Fertigkeiten zum Speichern.")


def load_custom_fertigkeiten(charakter):
    """
    Lädt die benutzerdefinierten Fertigkeiten aus einer JSON-Datei und fügt sie der Fertigkeiten-Liste hinzu.
    
    Args:
        charakter: Das Charakter-Objekt
    """
    custom_fertigkeiten_file = os.path.join(os.path.dirname(__file__), 'custom_fertigkeiten.json')
    if os.path.exists(custom_fertigkeiten_file):
        try:
            with open(custom_fertigkeiten_file, 'r', encoding='utf-8') as f:
                custom_fertigkeiten_data = json.load(f)
            attribute_dict = charakter.get_attribute_dict()  # Methode zur Beschaffung der Attribute
            for name, data in custom_fertigkeiten_data.items():
                fertigkeit = Fertigkeit.from_dict_static(data, attribute_dict)
                if fertigkeit:
                    charakter.fertigkeiten[name] = fertigkeit
            Logger.info(f"Benutzerdefinierte Fertigkeiten wurden aus {custom_fertigkeiten_file} geladen.")
        except Exception as e:
            Logger.error(f"Fehler beim Laden der benutzerdefinierten Fertigkeiten: {e}")
    else:
        Logger.info("Keine benutzerdefinierten Fertigkeiten zum Laden gefunden.")