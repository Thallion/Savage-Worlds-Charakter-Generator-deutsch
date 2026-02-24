# functions/statblock_generator.py
"""
Statblock Generator für Savage Worlds Charaktere
Erstellt eine kompakte Textdarstellung des Charakters
"""

from kivy.logger import Logger
from functions.superkraft_funktionen import ist_superkraefte_setting


def generate_character_statblock(charakter):
    """
    Generiert einen Statblock für den gegebenen Charakter
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        str: Formatierter Statblock als Text
    """
    try:
        # Charaktername
        char_name = charakter.profil_daten.get("Name", "Unbenannter Charakter")
        
        # Volk ermitteln
        volk_text = _format_race(charakter)
        
        # Attribute sammeln und formatieren
        attribute_text = _format_attributes(charakter)
        
        # Fertigkeiten sammeln und formatieren (nur Fertigkeiten über W4)
        fertigkeiten_text = _format_skills(charakter)
        
        # Abgeleitete Werte
        pace = charakter.bewegungsweite
        parry = charakter.parade
        toughness = charakter.robustheit
        
        # Handicaps formatieren
        handicaps_text = _format_handicaps(charakter)
        
        # Talente formatieren
        talente_text = _format_edges(charakter)
        
        # Mächte / Superkräfte formatieren
        maechte_text = _format_powers(charakter)
        superkraefte_text = _format_superkraefte(charakter)

        # Ausrüstung formatieren
        gear_text = _format_gear(charakter)
        
        # Statblock zusammenbauen
        statblock_lines = [
            f"{char_name}",
        ]
        
        # Volk hinzufügen wenn vorhanden
        if volk_text:
            statblock_lines.append(f"Volk: {volk_text}")
        
        statblock_lines.extend([
            f"Attribute: {attribute_text}",
            f"Fertigkeiten: {fertigkeiten_text}",
            f"Bewegungsweite: {pace}; Parade: {parry}; Robustheit: {toughness}"
        ])
        
        # Nur hinzufügen wenn vorhanden
        if handicaps_text:
            statblock_lines.append(f"Handicaps: {handicaps_text}")
            
        if talente_text:
            statblock_lines.append(f"Talente: {talente_text}")
            
        if maechte_text:
            statblock_lines.append(f"Mächte: {maechte_text}")

        if superkraefte_text:
            statblock_lines.append(f"Superkräfte: {superkraefte_text}")

        if gear_text:
            statblock_lines.append(f"Ausrüstung: {gear_text}")
        
        return "\n".join(statblock_lines)
        
    except Exception as e:
        Logger.error(f"Fehler beim Generieren des Statblocks: {str(e)}")
        return f"Fehler beim Generieren des Statblocks: {str(e)}"


def _format_race(charakter):
    """Formatiert das ausgewählte Volk für den Statblock"""
    try:
        # Suche nach ausgewähltem Volk
        if hasattr(charakter, 'voelker_selected'):
            for volk_name, selected in charakter.voelker_selected.items():
                if selected and volk_name in charakter.voelker:
                    volk = charakter.voelker[volk_name]
                    return volk.name
        
        # Fallback: Suche direkt in den Völkern nach ausgewähltem
        if hasattr(charakter, 'voelker'):
            for volk_name, volk in charakter.voelker.items():
                if hasattr(volk, 'ausgewaehlt') and volk.ausgewaehlt:
                    return volk.name
        
        # Kein Volk gefunden
        return ""
        
    except Exception as e:
        Logger.error(f"Fehler beim Formatieren des Volkes: {str(e)}")
        return ""


def _format_attributes(charakter):
    """Formatiert die Attribute für den Statblock"""
    try:
        attribute_parts = []
        
        # Standard-Attribute in fester Reihenfolge
        standard_attributes = ['Beweglichkeit', 'Verstand', 'Geist', 'Stärke', 'Konstitution']
        
        for attr_name in standard_attributes:
            if attr_name in charakter.attribute:
                attr = charakter.attribute[attr_name]
                die_type = f"W{attr.wert}"
                if attr.wuerfel.modifier > 0:
                    die_type += f"+{attr.wuerfel.modifier}"
                attribute_parts.append(f"{attr_name} {die_type}")
        
        # Weitere Attribute hinzufügen, die nicht in der Standard-Liste stehen
        for attr_name, attr in charakter.attribute.items():
            if attr_name not in standard_attributes:
                die_type = f"W{attr.wert}"
                if attr.wuerfel.modifier > 0:
                    die_type += f"+{attr.wuerfel.modifier}"
                attribute_parts.append(f"{attr_name} {die_type}")
        
        return ", ".join(attribute_parts)
        
    except Exception as e:
        Logger.error(f"Fehler beim Formatieren der Attribute: {str(e)}")
        return "Fehler beim Laden der Attribute"


def _format_skills(charakter):
    """Formatiert die Fertigkeiten für den Statblock (nur über W4)"""
    try:
        skill_parts = []
        
        # Sortiere Fertigkeiten alphabetisch
        sorted_skills = sorted(charakter.fertigkeiten.items())
        
        for skill_name, skill in sorted_skills:
            # Nur Fertigkeiten über W4 anzeigen
            if skill.wert > 4:
                die_type = f"W{skill.wert}"
                if skill.wuerfel.modifier > 0:
                    die_type += f"+{skill.wuerfel.modifier}"
                skill_parts.append(f"{skill_name} {die_type}")
        
        return ", ".join(skill_parts) if skill_parts else "Keine Fertigkeiten über W4"
        
    except Exception as e:
        Logger.error(f"Fehler beim Formatieren der Fertigkeiten: {str(e)}")
        return "Fehler beim Laden der Fertigkeiten"


def _format_handicaps(charakter):
    """Formatiert die Handicaps für den Statblock"""
    try:
        handicap_parts = []
        
        for handicap_key in charakter.selected_handicaps:
            if handicap_key in charakter.handicaps:
                handicap = charakter.handicaps[handicap_key]
                # Füge Stufe hinzu wenn nicht "normal"
                if hasattr(handicap, 'stufe') and handicap.stufe and handicap.stufe.lower() not in ['normal', '']:
                    handicap_parts.append(f"{handicap.name} ({handicap.stufe})")
                else:
                    handicap_parts.append(handicap.name)
        
        return ", ".join(handicap_parts)
        
    except Exception as e:
        Logger.error(f"Fehler beim Formatieren der Handicaps: {str(e)}")
        return ""


def _format_edges(charakter):
    """Formatiert die Talente für den Statblock"""
    try:
        talent_parts = []
        
        for talent_key in charakter.selected_talente:
            if talent_key in charakter.talente:
                talent = charakter.talente[talent_key]
                talent_parts.append(talent.name)
        
        return ", ".join(talent_parts)
        
    except Exception as e:
        Logger.error(f"Fehler beim Formatieren der Talente: {str(e)}")
        return ""


def _format_powers(charakter):
    """Formatiert die Mächte für den Statblock"""
    try:
        macht_parts = []
        
        for macht_key in charakter.selected_maechte:
            if macht_key in charakter.maechte:
                macht = charakter.maechte[macht_key]
                macht_parts.append(macht.name)
        
        # Machtpunkte hinzufügen wenn Mächte vorhanden sind
        if macht_parts and hasattr(charakter, 'machtpunkte') and charakter.machtpunkte > 0:
            macht_text = ", ".join(macht_parts)
            return f"{macht_text} ({charakter.machtpunkte} Machtpunkte)"
        elif macht_parts:
            return ", ".join(macht_parts)
        else:
            return ""
        
    except Exception as e:
        Logger.error(f"Fehler beim Formatieren der Mächte: {str(e)}")
        return ""


def _format_superkraefte(charakter):
    """Formatiert die Superkräfte für den Statblock"""
    try:
        if not ist_superkraefte_setting(charakter.active_setting_name):
            return ""

        kraft_parts = []
        for kraft_name in charakter.selected_superkraefte:
            if kraft_name in charakter.superkraefte:
                kraft = charakter.superkraefte[kraft_name]
                kosten = kraft.gesamt_kosten
                modifikatoren = [m.name for m in kraft.gewaehlte_modifikatoren]
                if modifikatoren:
                    kraft_parts.append(f"{kraft.name} [{kosten} SKP, {', '.join(modifikatoren)}]")
                else:
                    kraft_parts.append(f"{kraft.name} [{kosten} SKP]")

        if kraft_parts:
            skp_gesamt = charakter.superkraft_punkte_gesamt
            skp_verbraucht = charakter.superkraft_punkte_verbraucht
            kraft_text = ", ".join(kraft_parts)
            return f"{kraft_text} (Machtstufe {charakter.machtstufe}, {skp_verbraucht}/{skp_gesamt} SKP)"
        else:
            return ""

    except Exception as e:
        Logger.error(f"Fehler beim Formatieren der Superkräfte: {str(e)}")
        return ""


def _format_gear(charakter):
    """Formatiert die wichtigste Ausrüstung für den Statblock"""
    try:
        gear_parts = []
        
        # Waffen hinzufügen
        for waffe in charakter.selected_waffen:
            if hasattr(waffe, 'menge') and waffe.menge > 1:
                gear_parts.append(f"{waffe.name} ({waffe.menge}x)")
            else:
                gear_parts.append(waffe.name)
        
        # Rüstungen hinzufügen
        for ruestung in charakter.selected_ruestungen:
            gear_parts.append(ruestung.name)
        
        # Schilde hinzufügen
        for schild in charakter.selected_schilde:
            gear_parts.append(schild.name)
        
        # Wichtige allgemeine Ausrüstung hinzufügen (begrenzt auf die ersten 5)
        wichtige_ausruestung = []
        for item in charakter.selected_allgemeine_ausruestung[:5]:
            if hasattr(item, 'menge') and item.menge > 1:
                wichtige_ausruestung.append(f"{item.name} ({item.menge}x)")
            else:
                wichtige_ausruestung.append(item.name)
        
        gear_parts.extend(wichtige_ausruestung)
        
        # Wenn mehr als 8 Gegenstände, kürze ab
        if len(gear_parts) > 8:
            gear_parts = gear_parts[:8]
            gear_parts.append("...")
        
        return ", ".join(gear_parts)
        
    except Exception as e:
        Logger.error(f"Fehler beim Formatieren der Ausrüstung: {str(e)}")
        return ""


def copy_statblock_to_clipboard(statblock_text):
    """
    Kopiert den Statblock in die Zwischenablage (falls möglich)
    
    Args:
        statblock_text (str): Der zu kopierende Text
        
    Returns:
        bool: True wenn erfolgreich, False wenn fehlgeschlagen
    """
    try:
        # Versuche verschiedene Clipboard-Implementierungen
        try:
            # Kivy Clipboard (funktioniert auf den meisten Plattformen)
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(statblock_text)
            return True
        except:
            pass
        
        try:
            # Pyperclip als Fallback
            import pyperclip
            pyperclip.copy(statblock_text)
            return True
        except ImportError:
            pass
        
        Logger.warning("Clipboard-Funktionalität nicht verfügbar")
        return False
        
    except Exception as e:
        Logger.error(f"Fehler beim Kopieren in die Zwischenablage: {str(e)}")
        return False