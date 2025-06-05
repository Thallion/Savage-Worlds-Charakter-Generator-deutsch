"""
Modul für die Verwaltung von Talenten im Charakter.
Dieses Modul enthält Funktionen zur Verwaltung von Talenten, einschließlich
des Auswahlens, Abwählens und Überprüfens der Voraussetzungen.
ERWEITERT: Mit Savage Pathfinder Support für kostenlose Klassen-/Hintergrund-/Experte-Talente
"""

from kivy.logger import Logger
from models.talent import Talent
from functions.macht_funktionen import entferne_macht
import re

# Liste der Talente, die nicht mehrfach ausgewählt werden können
NICHT_DUPLIZIERBARE_TALENTE = [
    "Glück", "Großes Glück", "Reich", "Stinkreich", 
    "Kräftig", "Riesenwuchs", "Klein", "Zäh", "Sehr zäh",
    "Arkaner Hintergrund: Gaben", "Arkaner Hintergrund: Magie", 
    "Arkaner Hintergrund: Psionik", "Arkaner Hintergrund: Wunder",
    "Arkaner Widerstand", "Verbesserte Arkane Resistenz",
    "Meister aller Waffen", "Waffenmeister", "Block", "Harter Block",
    "Schwer zu töten", "Schwerer zu töten", "Schnell", "Flink",
    "Raufbold", "Schläger", "Attraktiv", "Sehr attraktiv"
]

# Savage Pathfinder: Kategorien für kostenlose Talente während Charaktererstellung
PATHFINDER_KOSTENLOSE_KATEGORIEN = [
    "Klasse", "Hintergrund", "Experte", "Class", "Background", "Expert"
]


def ist_savage_pathfinder_setting(charakter):
    """
    Prüft, ob das aktuelle Setting Savage Pathfinder ist.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        bool: True wenn Savage Pathfinder, sonst False
    """
    setting_name = getattr(charakter, 'active_setting_name', '').lower()
    return 'pathfinder' in setting_name or setting_name == 'savage pathfinder'


def ist_pathfinder_kostenloses_talent(talent):
    """
    Prüft, ob ein Talent zu den Kategorien gehört, die in Savage Pathfinder 
    während der Charaktererstellung kostenlos gewählt werden können.
    
    Args:
        talent: Das Talent-Objekt
        
    Returns:
        bool: True wenn Klassen-, Hintergrund- oder Experte-Talent, sonst False
    """
    if not hasattr(talent, 'kategorie') or not talent.kategorie:
        return False
        
    return talent.kategorie in PATHFINDER_KOSTENLOSE_KATEGORIEN


def hat_bereits_kostenloses_pathfinder_talent(charakter):
    """
    Prüft, ob bereits ein kostenloses Pathfinder-Talent gewählt wurde.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        bool: True wenn bereits ein kostenloses Talent gewählt wurde
    """
    # Prüfe, ob es ein Attribut gibt, das die Anzahl verfolgt
    if not hasattr(charakter, 'pathfinder_kostenlose_talente_gewaehlt'):
        charakter.pathfinder_kostenlose_talente_gewaehlt = 0
        
    return charakter.pathfinder_kostenlose_talente_gewaehlt >= 1


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


def waehle_freies_talent(charakter, talent_name_key, ignore_voraussetzungen=False):
    """
    Wählt ein Talent als freies Talent ohne Kosten (Aufstiege oder Handicap-Punkte) aus.
    Speziell für Rasseneigenschaften wie das freie Talent der Menschen.
    Wenn das Talent bereits ausgewählt ist, wird eine neue Instanz mit Suffix erstellt.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name_key: Der Name des auszuwählenden Talents
        ignore_voraussetzungen: Flag zum Ignorieren der Voraussetzungsprüfung
        
    Returns:
        str oder bool: "needs_voraussetzungen_confirmation" wenn Voraussetzungen nicht erfüllt sind,
                       "not_duplicatable" wenn Talent nicht duplizierbar ist,
                       True bei Erfolg, False bei Misserfolg
    """
    Logger.info(f"Wähle freies Talent: {talent_name_key}")
    
    # Prüfen, ob das Talent existiert
    if talent_name_key not in charakter.talente:
        Logger.error(f"Talent '{talent_name_key}' existiert nicht.")
        return False
        
    talent = charakter.talente[talent_name_key]
    
    # Prüfe ob dieses spezifische Talent bereits ausgewählt ist (für Mehrfachauswahl)
    if talent.ausgewaehlt:
        # Prüfe ob das Talent duplizierbar ist
        if talent.name in NICHT_DUPLIZIERBARE_TALENTE:
            Logger.warning(f"Talent '{talent.name}' kann nicht mehrfach ausgewählt werden.")
            return "not_duplicatable"
        
        # Erstelle eine neue Instanz für Mehrfachauswahl
        base_key = talent_name_key.split('_')[0] if '_' in talent_name_key and talent_name_key.split('_')[-1].isdigit() else talent_name_key
        suffix = 2
        new_key = f"{base_key}_{suffix}"
        
        # Finde den nächsten freien Suffix
        while new_key in charakter.talente:
            suffix += 1
            new_key = f"{base_key}_{suffix}"
        
        # Erstelle eine Kopie des Talents mit der clone() Methode
        new_talent = talent.clone()
        new_talent.ausgewaehlt = False  # Zurücksetzen für die neue Instanz
        
        # Füge das neue Talent hinzu
        charakter.talente[new_key] = new_talent
        Logger.info(f"Neue Instanz von Talent '{talent.name}' mit Key '{new_key}' erstellt")
        
        # Wähle die neue Instanz aus
        return waehle_freies_talent(charakter, new_key, ignore_voraussetzungen)
        
    # Voraussetzungsprüfung, nur wenn ignore_voraussetzungen nicht gesetzt ist
    if not ignore_voraussetzungen:
        fehlermeldungen = pruefe_voraussetzungen(charakter, talent)
        if fehlermeldungen:
            # Fehlermeldungen als Attribut speichern für UI-Dialog
            charakter.temp_voraussetzungs_fehler = fehlermeldungen
            Logger.debug(f"Rückgabe 'needs_voraussetzungen_confirmation' für freies Talent {talent_name_key}")
            return "needs_voraussetzungen_confirmation"
    
    # Direkt das Talent auswählen, ohne Kosten
    talent.ausgewaehlt = True
    
    # Machtpunkte und verfügbare Mächte erhöhen, falls das Talent diese gewährt
    charakter.verfuegbare_maechte += talent.neue_maechte
    charakter.anzahl_maechte += talent.neue_maechte
    charakter.erhoehe_machtpunkte(talent.machtpunkte)
    
    # Zur Liste der ausgewählten Talente hinzufügen
    if talent_name_key not in charakter.selected_talente:
        charakter.selected_talente.append(talent_name_key)
        
    # Abgeleitete Werte neu berechnen (besonders wichtig für Talent "Kräftig")
    charakter.berechne_abgeleitete_werte()
        
    Logger.info(f"Freies Talent '{talent_name_key}' ohne Kosten ausgewählt.")
    return True


def waehle_pathfinder_kostenloses_talent(charakter, talent_name_key, ignore_voraussetzungen=False):
    """
    Wählt ein Klassen-, Hintergrund- oder Experte-Talent in Savage Pathfinder kostenlos aus.
    Nur während der Charaktererstellung (char_gen_completed = False) und nur einmal möglich.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name_key: Der Name des auszuwählenden Talents
        ignore_voraussetzungen: Flag zum Ignorieren der Voraussetzungsprüfung
        
    Returns:
        str oder bool: "needs_voraussetzungen_confirmation" wenn Voraussetzungen nicht erfüllt sind,
                       "not_duplicatable" wenn Talent nicht duplizierbar ist,
                       "already_used" wenn bereits ein kostenloses Talent gewählt wurde,
                       "not_pathfinder_category" wenn falsche Kategorie,
                       True bei Erfolg, False bei Misserfolg
    """
    Logger.info(f"Wähle kostenloses Pathfinder-Talent: {talent_name_key}")
    
    # Prüfen, ob das Talent existiert
    if talent_name_key not in charakter.talente:
        Logger.error(f"Talent '{talent_name_key}' existiert nicht.")
        return False
        
    talent = charakter.talente[talent_name_key]
    
    # Prüfen, ob es sich um die richtige Kategorie handelt
    if not ist_pathfinder_kostenloses_talent(talent):
        Logger.warning(f"Talent '{talent.name}' gehört nicht zu den kostenlosen Kategorien (Klasse/Hintergrund/Experte).")
        return "not_pathfinder_category"
    
    # Prüfen, ob bereits ein kostenloses Talent gewählt wurde
    if hat_bereits_kostenloses_pathfinder_talent(charakter):
        Logger.warning("Es wurde bereits ein kostenloses Pathfinder-Talent gewählt.")
        return "already_used"
    
    # Prüfe ob dieses spezifische Talent bereits ausgewählt ist (für Mehrfachauswahl)
    if talent.ausgewaehlt:
        # Prüfe ob das Talent duplizierbar ist
        if talent.name in NICHT_DUPLIZIERBARE_TALENTE:
            Logger.warning(f"Talent '{talent.name}' kann nicht mehrfach ausgewählt werden.")
            return "not_duplicatable"
        
        # Erstelle eine neue Instanz für Mehrfachauswahl
        base_key = talent_name_key.split('_')[0] if '_' in talent_name_key and talent_name_key.split('_')[-1].isdigit() else talent_name_key
        suffix = 2
        new_key = f"{base_key}_{suffix}"
        
        # Finde den nächsten freien Suffix
        while new_key in charakter.talente:
            suffix += 1
            new_key = f"{base_key}_{suffix}"
        
        # Erstelle eine Kopie des Talents mit der clone() Methode
        new_talent = talent.clone()
        new_talent.ausgewaehlt = False  # Zurücksetzen für die neue Instanz
        
        # Füge das neue Talent hinzu
        charakter.talente[new_key] = new_talent
        Logger.info(f"Neue Instanz von Talent '{talent.name}' mit Key '{new_key}' erstellt")
        
        # Wähle die neue Instanz aus
        return waehle_pathfinder_kostenloses_talent(charakter, new_key, ignore_voraussetzungen)
        
    # Voraussetzungsprüfung, nur wenn ignore_voraussetzungen nicht gesetzt ist
    if not ignore_voraussetzungen:
        fehlermeldungen = pruefe_voraussetzungen(charakter, talent)
        if fehlermeldungen:
            # Fehlermeldungen als Attribut speichern für UI-Dialog
            charakter.temp_voraussetzungs_fehler = fehlermeldungen
            Logger.debug(f"Rückgabe 'needs_voraussetzungen_confirmation' für kostenloses Pathfinder-Talent {talent_name_key}")
            return "needs_voraussetzungen_confirmation"
    
    # Direkt das Talent auswählen, ohne Kosten
    talent.ausgewaehlt = True
    
    # Machtpunkte und verfügbare Mächte erhöhen, falls das Talent diese gewährt
    charakter.verfuegbare_maechte += talent.neue_maechte
    charakter.anzahl_maechte += talent.neue_maechte
    charakter.erhoehe_machtpunkte(talent.machtpunkte)
    
    # Zur Liste der ausgewählten Talente hinzufügen
    if talent_name_key not in charakter.selected_talente:
        charakter.selected_talente.append(talent_name_key)
    
    # Zähler für kostenlose Pathfinder-Talente erhöhen
    if not hasattr(charakter, 'pathfinder_kostenlose_talente_gewaehlt'):
        charakter.pathfinder_kostenlose_talente_gewaehlt = 0
    charakter.pathfinder_kostenlose_talente_gewaehlt += 1
        
    # Abgeleitete Werte neu berechnen
    charakter.berechne_abgeleitete_werte()
        
    Logger.info(f"Kostenloses Pathfinder-Talent '{talent_name_key}' ausgewählt.")
    return True


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


def talent_auswaehlen(charakter, talent_name_key, skip_prereq_check=False):
    """
    Wählt ein Talent aus und führt die entsprechenden Anpassungen am Charakter durch.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name_key: Der Name des auszuwählenden Talents
        skip_prereq_check: Voraussetzungsprüfung überspringen (default: False)
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    talent = charakter.talente.get(talent_name_key)
    if talent:
        if not talent.ausgewaehlt:
            # WICHTIG: Hier die Bedingung anpassen
            # Wenn skip_prereq_check True ist, überspringen wir die Voraussetzungsprüfung vollständig
            if skip_prereq_check or talent.voraussetzungen_erfuellt(charakter):
                # Talent auswählen und Anpassungen vornehmen
                talent.ausgewaehlt = True
                charakter.verfuegbare_maechte += talent.neue_maechte
                charakter.anzahl_maechte += talent.neue_maechte
                charakter.erhoehe_machtpunkte(talent.machtpunkte)
                if talent_name_key not in charakter.selected_talente:
                    charakter.selected_talente.append(talent_name_key)
                
                # Spezielle Anpassungen für Reich/Stinkreich
                if talent_name_key in ["Reich", "Stinkreich"]:
                    from functions.ausruestung_funktionen import anpassen_vermoegen_bei_talent_reich
                    anpassen_vermoegen_bei_talent_reich(charakter, talent_name_key, True)  # True = wird ausgewählt
                
                Logger.info(f"Talent '{talent_name_key}' ausgewählt.")
                
                # Abgeleitete Werte neu berechnen (ohne Vermögensberechnung)
                charakter.berechne_abgeleitete_werte()
                
                return True
            else:
                pass
                #Logger.warning(f"Voraussetzungen für Talent '{talent_name_key}' nicht erfüllt.")
        else:
            Logger.warning(f"Talent '{talent_name_key}' ist bereits ausgewählt.")
    else:
        Logger.error(f"Talent '{talent_name_key}' existiert nicht.")
    return False


def pruefe_voraussetzungen(charakter, talent):
    """
    Prüft alle Voraussetzungen eines Talents und gibt eine Liste von Fehlermeldungen zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        talent: Das Talent-Objekt
        
    Returns:
        list: Liste von Fehlermeldungen, leer wenn alle Voraussetzungen erfüllt sind
    """
    fehlermeldungen = []
    
    # Debug-Ausgabe der Voraussetzungen
    #Logger.debug(f"Prüfe Voraussetzungen für Talent '{talent.name}': {talent.voraussetzungen}")
    
    for voraussetzung in talent.voraussetzungen:
        # Spezialfall: AH (Arkaner Hintergrund)
        if voraussetzung == "AH":
            # Prüfe, ob ein Arkaner Hintergrund vorhanden ist
            hat_arkanen_hintergrund = False
            for talent_name, talent_obj in charakter.talente.items():
                if "Arkaner Hintergrund" in talent_name and talent_obj.ausgewaehlt:
                    hat_arkanen_hintergrund = True
                    break
                    
            if not hat_arkanen_hintergrund:
                fehlermeldungen.append("Ein beliebiger Arkaner Hintergrund (AH) wird vorausgesetzt.")
            
            continue
            
        # Attributvoraussetzung (z.B. "STÄ W8")
        attribut_match = re.match(r'^([A-ZÄÖÜ]+)\s+W(\d+)$', voraussetzung)
        if attribut_match:
            attribut_kuerzel = attribut_match.group(1)
            wuerfel_wert = int(attribut_match.group(2))
            
            # Attributkürzel zu vollständigem Namen umwandeln
            attribut_mapping = {
                'STÄ': 'Stärke',
                'GES': 'Geschicklichkeit',
                'KON': 'Konstitution',
                'VER': 'Verstand',
                'WIL': 'Willenskraft'
            }
            attribut_name = attribut_mapping.get(attribut_kuerzel, attribut_kuerzel)
            
            attribut = charakter.attribute.get(attribut_name)
            if not attribut:
                fehlermeldungen.append(f"Attribut '{attribut_name}' nicht gefunden.")
                continue
            
            if attribut.wert < wuerfel_wert:
                fehlermeldungen.append(f"Attribut '{attribut_name}' muss mindestens W{wuerfel_wert} sein (aktuell W{attribut.wert}).")
            
            continue
        
        # Fertigkeitsvoraussetzung (z.B. "Kämpfen W8")
        fertigkeit_match = re.match(r'^(.+?)\s+W(\d+)$', voraussetzung)
        if fertigkeit_match and not attribut_match:  # Nicht bereits als Attribut erkannt
            fertigkeit_name = fertigkeit_match.group(1)
            wuerfel_wert = int(fertigkeit_match.group(2))
            
            fertigkeit = charakter.fertigkeiten.get(fertigkeit_name)
            if not fertigkeit:
                fehlermeldungen.append(f"Fertigkeit '{fertigkeit_name}' nicht gefunden.")
                continue
            
            if fertigkeit.wert < wuerfel_wert:
                fehlermeldungen.append(f"Fertigkeit '{fertigkeit_name}' muss mindestens W{wuerfel_wert} sein (aktuell W{fertigkeit.wert}).")
            
            continue
        
        # Talentvoraussetzung (z.B. "Glück")
        talent_name = voraussetzung  # Annahme: Wenn keine spezielle Formatierung, handelt es sich um ein Talent
        
        talent_obj = charakter.talente.get(talent_name)
        if not talent_obj:
            fehlermeldungen.append(f"Vorausgesetztes Talent '{talent_name}' wurde nicht gefunden.")
            continue
        
        if not talent_obj.ausgewaehlt:
            fehlermeldungen.append(f"Vorausgesetztes Talent '{talent_name}' muss ausgewählt sein.")
    
    # # Debug-Ausgabe der gefundenen Fehlermeldungen
    # if fehlermeldungen:
    #     Logger.debug(f"Voraussetzungen für Talent '{talent.name}' nicht erfüllt: {fehlermeldungen}")
    
    return fehlermeldungen


def waehle_talent(charakter, talent_name_key, ignore_rang_check=False):
    """
    Wählt ein Talent aus und verrechnet die Kosten entweder mit Handicap-Punkten oder Aufstiegen.
    ERWEITERT: Unterstützt kostenlose Pathfinder-Talente während der Charaktererstellung.
    Wenn das Talent bereits ausgewählt ist, wird eine neue Instanz mit Suffix erstellt.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name_key: Der Name des auszuwählenden Talents
        ignore_rang_check: Flag, um die Rang-Prüfung zu überspringen (für UI-Bestätigung)
        
    Returns:
        str oder bool: "needs_rang_confirmation" wenn der Rang zu niedrig ist,
                       "needs_voraussetzungen_confirmation" wenn Voraussetzungen nicht erfüllt sind,
                       "not_duplicatable" wenn Talent nicht duplizierbar ist,
                       "pathfinder_kostenlos_angeboten" wenn kostenloses Pathfinder-Talent möglich ist,
                       True bei Erfolg, False bei Misserfolg
    """
    # Prüfen, ob das Talent existiert
    if talent_name_key not in charakter.talente:
        Logger.error(f"Talent '{talent_name_key}' existiert nicht.")
        return False
        
    talent = charakter.talente[talent_name_key]
    
    # NEUE LOGIK: Savage Pathfinder kostenlose Talente während Charaktererstellung
    if (ist_savage_pathfinder_setting(charakter) and 
        not charakter.char_gen_completed and 
        ist_pathfinder_kostenloses_talent(talent) and 
        not hat_bereits_kostenloses_pathfinder_talent(charakter)):
        
        Logger.info(f"Pathfinder-Talent '{talent_name_key}' kann kostenlos gewählt werden.")
        return "pathfinder_kostenlos_angeboten"
    
    # Prüfe ob dieses spezifische Talent bereits ausgewählt ist (für Mehrfachauswahl)
    if talent.ausgewaehlt:
        # Prüfe ob das Talent duplizierbar ist
        if talent.name in NICHT_DUPLIZIERBARE_TALENTE:
            Logger.warning(f"Talent '{talent.name}' kann nicht mehrfach ausgewählt werden.")
            return "not_duplicatable"

        # Erstelle eine neue Instanz für Mehrfachauswahl
        base_key = talent_name_key.split('_')[0] if '_' in talent_name_key and talent_name_key.split('_')[-1].isdigit() else talent_name_key
        suffix = 2
        new_key = f"{base_key}_{suffix}"
        
        # Finde den nächsten freien Suffix
        while new_key in charakter.talente:
            suffix += 1
            new_key = f"{base_key}_{suffix}"
        
        # Erstelle eine Kopie des Talents mit der clone() Methode
        new_talent = talent.clone()
        new_talent.ausgewaehlt = False  # Zurücksetzen für die neue Instanz
        
        # Füge das neue Talent hinzu
        charakter.talente[new_key] = new_talent
        Logger.info(f"Neue Instanz von Talent '{talent.name}' mit Key '{new_key}' erstellt")
        
        # Wähle die neue Instanz aus
        return waehle_talent(charakter, new_key, ignore_rang_check)
    
    # WICHTIG: Prüfe erst Rang, dann Voraussetzungen - priorisiere Rangwarnung
    # Rang-Prüfung
    if not ignore_rang_check and is_talent_rang_hoeher_als_charakter(charakter, talent.rang):
        # Wenn Rang nicht passt, nur Rangwarnung zurückgeben, weitere Prüfungen überspringen
        return "needs_rang_confirmation"
    
    # Voraussetzungsprüfung, nur wenn Rang ok ist und ignore_voraussetzungen-Flag nicht gesetzt ist
    if not hasattr(charakter, 'ignore_voraussetzungen') or not charakter.ignore_voraussetzungen:
        fehlermeldungen = pruefe_voraussetzungen(charakter, talent)
        if fehlermeldungen:
            # Fehlermeldungen als Attribut speichern für UI-Dialog
            charakter.temp_voraussetzungs_fehler = fehlermeldungen
            Logger.debug(f"Rückgabe 'needs_voraussetzungen_confirmation' für {talent_name_key}")
            return "needs_voraussetzungen_confirmation"
    
    # Hier wird das Talent ausgewählt, entweder mit Handicap-Punkten oder Aufstiegen
    # Option 1: Auswahl mit Handicap-Punkten
    if charakter.verbleibende_handicap_punkte > 1.5:
        # Wenn das ignore_voraussetzungen-Flag gesetzt ist, übergeben wir True für skip_prereq_check
        skip_prereq = hasattr(charakter, 'ignore_voraussetzungen') and charakter.ignore_voraussetzungen
        erfolg = talent_auswaehlen(charakter, talent_name_key, skip_prereq_check=skip_prereq)
        
        if erfolg:
            charakter.verbleibende_handicap_punkte -= 2
            # Reset für zukünftige Prüfungen
            if hasattr(charakter, 'ignore_voraussetzungen'):
                charakter.ignore_voraussetzungen = False
                Logger.debug(f"Flag ignore_voraussetzungen zurückgesetzt nach Auswahl von '{talent_name_key}'")
            
            # Abgeleitete Werte neu berechnen (besonders wichtig für Talent "Kräftig")
            charakter.berechne_abgeleitete_werte()
            
            return True

    # Option 2: Auswahl mit Aufstiegen
    else:
        if charakter.verbleibende_aufstiege > 0:
            # Wenn das ignore_voraussetzungen-Flag gesetzt ist, übergeben wir True für skip_prereq_check
            skip_prereq = hasattr(charakter, 'ignore_voraussetzungen') and charakter.ignore_voraussetzungen
            erfolg = talent_auswaehlen(charakter, talent_name_key, skip_prereq_check=skip_prereq)
            
            if erfolg:
                charakter.verbleibende_aufstiege -= 1
                charakter.update_char_gen_status()
                # Reset für zukünftige Prüfungen
                if hasattr(charakter, 'ignore_voraussetzungen'):
                    charakter.ignore_voraussetzungen = False
                    Logger.debug(f"Flag ignore_voraussetzungen zurückgesetzt nach Auswahl von '{talent_name_key}'")
                
                # Abgeleitete Werte neu berechnen (besonders wichtig für Talent "Kräftig")
                charakter.berechne_abgeleitete_werte()
                
                return True
        else:    
            Logger.warning(f"Keine verbleibenden Aufstiege übrig.")
    
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
    #Logger.debug(f"Rangprüfung - Charakter-Rang: '{charakter.rang}', Talent-Rang: '{talent_rang}'")
    
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
    #Logger.debug(f"Rangprüfung - Charakter-Wert: {charakter_rang_wert}, Talent-Wert: {talent_rang_wert}")
    
    # Vergleich durchführen und Ergebnis loggen
    is_higher = talent_rang_wert > charakter_rang_wert
    #Logger.debug(f"Rangprüfung - Ergebnis: {is_higher} (Talent-Rang {'>' if is_higher else '<='} Charakter-Rang)")
    
    return is_higher


def entferne_talent(charakter, talent_name_key):
    """
    Entfernt ein ausgewähltes Talent und führt die entsprechenden Anpassungen am Charakter durch.
    ERWEITERT: Berücksichtigt kostenlose Pathfinder-Talente.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name_key: Der Name des zu entfernenden Talents
        
    Returns:
        True bei Erfolg, False bei Misserfolg
    """
    def talent_abwaehlen():
        talent.abwaehlen(charakter)
        charakter.verfuegbare_maechte -= talent.neue_maechte
        charakter.anzahl_maechte -= talent.neue_maechte
        charakter.verfuegbare_maechte = max(charakter.verfuegbare_maechte, 0)  # Nicht negativ
        charakter.senke_machtpunkte(talent.machtpunkte)
        
        # Spezielle Anpassungen für Reich/Stinkreich
        if talent_name_key in ["Reich", "Stinkreich"]:
            from functions.ausruestung_funktionen import anpassen_vermoegen_bei_talent_reich
            anpassen_vermoegen_bei_talent_reich(charakter, talent_name_key, False)  # False = wird abgewählt
        
        if talent_name_key in charakter.selected_talente:
            charakter.selected_talente.remove(talent_name_key)
        Logger.debug(f"Talent '{talent_name_key}' entfernt.")
        
        # Abgeleitete Werte neu berechnen (ohne Vermögensberechnung)
        charakter.berechne_abgeleitete_werte()
        
        return True

    if talent_name_key in charakter.talente:
        talent = charakter.talente[talent_name_key]
        Logger.info(f"talent ausgewaehlt {talent.ausgewaehlt}")
        if talent.ausgewaehlt:
            
            # NEUE LOGIK: Prüfe, ob es ein kostenloses Pathfinder-Talent war
            war_kostenloses_pathfinder_talent = (
                ist_savage_pathfinder_setting(charakter) and 
                ist_pathfinder_kostenloses_talent(talent) and
                hasattr(charakter, 'pathfinder_kostenlose_talente_gewaehlt') and
                charakter.pathfinder_kostenlose_talente_gewaehlt > 0
            )
            
            if charakter.char_gen_completed:
                talent_abwaehlen()
                # Bei kostenlosen Pathfinder-Talenten keine Rückerstattung
                if not war_kostenloses_pathfinder_talent:
                    charakter.verbleibende_aufstiege += 1  # Rückerstattung der Aufstiegs-Punkte                    
                charakter.update_char_gen_status()  # Aktualisiere den Status
                
                # Pathfinder-Zähler verringern, falls es ein kostenloses war
                if war_kostenloses_pathfinder_talent:
                    charakter.pathfinder_kostenlose_talente_gewaehlt -= 1
                    
                return True
            else:
                talent_abwaehlen() 
                
                # Bei kostenlosen Pathfinder-Talenten keine Handicap-Punkte-Rückerstattung
                if not war_kostenloses_pathfinder_talent:
                    charakter.verbleibende_handicap_punkte += 2
                    # Nicht mehr als 4 Handicap-Punkte
                    charakter.verbleibende_handicap_punkte = min(charakter.verbleibende_handicap_punkte, 4)
                
                # Pathfinder-Zähler verringern, falls es ein kostenloses war
                if war_kostenloses_pathfinder_talent:
                    charakter.pathfinder_kostenlose_talente_gewaehlt -= 1
                    
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