def ist_talent_mit_handicaps_kompatibel(charakter, talent_name):
    """
    Prüft, ob ein Talent mit den ausgewählten Handicaps kompatibel ist.
    
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