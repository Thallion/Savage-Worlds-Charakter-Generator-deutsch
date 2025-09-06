def ist_talent_mit_handicaps_kompatibel(charakter, talent_name):
    """
    Prüft, ob ein Talent mit den ausgewählten Handicaps kompatibel ist.
    ERWEITERT: Mit Savage Pathfinder Support
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name: Der Name des zu prüfenden Talents
        
    Returns:
        (bool, str): (Ist kompatibel?, Fehlermeldung falls nicht)
    """
    # Reich/Stinkreich und Arm sind nicht kompatibel
    if talent_name in ["Reich", "Stinkreich"]:
        for handicap_key in charakter.selected_handicaps:
            if handicap_key in charakter.handicaps:
                handicap = charakter.handicaps[handicap_key]
                if handicap.name == "Arm":
                    return False, f"Das Talent '{talent_name}' ist nicht mit dem Handicap 'Arm' kombinierbar."
    
    # Weitere Inkompatibilitätsregeln könnten hier hinzugefügt werden
    
    return True, ""

def ist_handicap_mit_talenten_kompatibel(charakter, handicap_name):
    """
    Prüft, ob ein Handicap mit den ausgewählten Talenten kompatibel ist.
    ERWEITERT: Mit Savage Pathfinder Support
    
    Args:
        charakter: Das Charakter-Objekt
        handicap_name: Der Name des zu prüfenden Handicaps
        
    Returns:
        (bool, str): (Ist kompatibel?, Fehlermeldung falls nicht)
    """
    handicap = charakter.handicaps.get(handicap_name)
    if handicap and handicap.name == "Arm":
        if "Reich" in charakter.selected_talente or "Stinkreich" in charakter.selected_talente:
            return False, f"Das Handicap 'Arm' ist nicht mit den Talenten 'Reich' oder 'Stinkreich' kombinierbar."
    
    # Weitere Inkompatibilitätsregeln könnten hier hinzugefügt werden
    
    return True, ""

def pruefe_pathfinder_talent_limits(charakter, talent_name):
    """
    NEU: Prüft Pathfinder-spezifische Talent-Limits und -Regeln.
    
    Args:
        charakter: Das Charakter-Objekt
        talent_name: Der Name des zu prüfenden Talents
        
    Returns:
        (bool, str): (Ist erlaubt?, Fehlermeldung falls nicht)
    """
    from functions.talent_funktionen import (
        ist_savage_pathfinder_setting, 
        ist_pathfinder_kostenloses_talent,
        hat_bereits_kostenloses_pathfinder_talent
    )
    
    # Nur für Savage Pathfinder relevant
    if not ist_savage_pathfinder_setting(charakter):
        return True, ""
    
    # Prüfe, ob es sich um ein kostenloses Pathfinder-Talent handelt
    if talent_name in charakter.talente:
        talent = charakter.talente[talent_name]
        
        # Wenn das Talent kostenlos wählbar ist (Klasse/Hintergrund/Experte)
        if ist_pathfinder_kostenloses_talent(talent):
            # Während der Charaktererstellung
            if not charakter.char_gen_completed:
                # Prüfe, ob bereits ein kostenloses Talent gewählt wurde
                if hat_bereits_kostenloses_pathfinder_talent(charakter):
                    return False, (
                        f"In Savage Pathfinder kann während der Charaktererstellung nur "
                        f"ein Klassen-, Hintergrund- oder Experte-Talent kostenlos gewählt werden. "
                        f"Sie haben bereits {getattr(charakter, 'pathfinder_kostenlose_talente_gewaehlt', 0)} "
                        f"kostenlose(s) Talent(e) gewählt."
                    )
                else:
                    # Kann kostenlos gewählt werden
                    return True, "Kann als kostenloses Pathfinder-Talent gewählt werden."
            else:
                # Nach der Charaktererstellung normale Kosten
                return True, "Normale Kosten nach der Charaktererstellung."
    
    return True, ""

def pruefe_pathfinder_charaktererstellung_abschluss(charakter):
    """
    NEU: Prüft, ob die Pathfinder-Charaktererstellung korrekt abgeschlossen werden kann.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        (bool, list): (Kann abgeschlossen werden?, Liste der Warnungen/Hinweise)
    """
    from functions.talent_funktionen import ist_savage_pathfinder_setting
    
    warnungen = []
    kann_abgeschlossen_werden = True
    
    # Nur für Savage Pathfinder relevant
    if not ist_savage_pathfinder_setting(charakter):
        return True, []
    
    # Nur während der Charaktererstellung relevant
    if charakter.char_gen_completed:
        return True, []
    
    # Prüfe, ob kostenlose Pathfinder-Talente verfügbar sind
    kostenlose_verwendet = getattr(charakter, 'pathfinder_kostenlose_talente_gewaehlt', 0)
    
    # Hinweis, wenn noch kein kostenloses Talent gewählt wurde
    if kostenlose_verwendet == 0:
        # Prüfe, ob kostenlose Talente verfügbar sind
        verfuegbare_kostenlose_talente = []
        for name, talent in charakter.talente.items():
            if (hasattr(talent, 'kategorie') and 
                talent.kategorie in ["Klasse", "Hintergrund", "Experte", "Class", "Background", "Expert"] and
                not talent.ausgewaehlt):
                verfuegbare_kostenlose_talente.append(talent.name)
        
        if verfuegbare_kostenlose_talente:
            warnungen.append(
                f"HINWEIS: Sie können noch ein Klassen-, Hintergrund- oder Experte-Talent "
                f"kostenlos wählen. Verfügbare Talente: {', '.join(verfuegbare_kostenlose_talente[:5])}"
                f"{'...' if len(verfuegbare_kostenlose_talente) > 5 else ''}"
            )
            # Kann trotzdem abgeschlossen werden, ist nur ein Hinweis
        else:
            warnungen.append(
                "INFO: Keine kostenlosen Pathfinder-Talente (Klasse/Hintergrund/Experte) verfügbar."
            )
    else:
        warnungen.append(
            f"INFO: {kostenlose_verwendet} kostenlose(s) Pathfinder-Talent(e) wurde(n) gewählt."
        )
    
    return kann_abgeschlossen_werden, warnungen

def get_pathfinder_kompatibilitaets_info(charakter):
    """
    NEU: Gibt umfassende Pathfinder-Kompatibilitätsinformationen zurück.
    
    Args:
        charakter: Das Charakter-Objekt
        
    Returns:
        dict: Dictionary mit Kompatibilitätsinformationen
    """
    from functions.talent_funktionen import ist_savage_pathfinder_setting
    
    info = {
        'ist_pathfinder': ist_savage_pathfinder_setting(charakter),
        'kostenlose_talente_gewaehlt': getattr(charakter, 'pathfinder_kostenlose_talente_gewaehlt', 0),
        'char_gen_completed': charakter.char_gen_completed,
        'kann_abgeschlossen_werden': True,
        'warnungen': [],
        'verfuegbare_kostenlose_talente': []
    }
    
    if info['ist_pathfinder'] and not info['char_gen_completed']:
        # Charaktererstellungs-Prüfung
        kann_abgeschlossen, warnungen = pruefe_pathfinder_charaktererstellung_abschluss(charakter)
        info['kann_abgeschlossen_werden'] = kann_abgeschlossen
        info['warnungen'] = warnungen
        
        # Verfügbare kostenlose Talente sammeln
        for name, talent in charakter.talente.items():
            if (hasattr(talent, 'kategorie') and 
                talent.kategorie in ["Klasse", "Hintergrund", "Experte", "Class", "Background", "Expert"] and
                not talent.ausgewaehlt):
                info['verfuegbare_kostenlose_talente'].append({
                    'name': talent.name,
                    'kategorie': talent.kategorie,
                    'beschreibung': getattr(talent, 'beschreibung', ''),
                    'key': name
                })
    
    return info