# functions/abgeleitete_werte.py - Erweiterte Version mit Völker-Effekten

from kivy.logger import Logger
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild

def berechne_abgeleitete_werte(charakter):
    """
    Berechnet die abgeleiteten Werte des Charakters, wie Parade, Robustheit usw.
    ERWEITERT: Berücksichtigt Völker-Effekte, Erschöpfung, Talente und natürliche Panzerung.
    
    Args:
        charakter: Das Charakterobjekt, dessen Werte berechnet werden sollen
        
    Returns:
        dict: Ein Dictionary mit allen abgeleiteten Werten
    """
    try:
        # Standardwerte
        bewegungsweite = 6
        bennys = 3  # Basis-Bennys
        entschlossenheit = 0
        machtpunkte = charakter.machtpunkte  # Machtpunkte aus dem Charakter übernehmen
        wunden = 0  # Kann später durch Spielereignisse verändert werden
        erschoepfung = charakter.erschoepfung  # Aktuelle Erschöpfung

        # Vermögen wird nicht mehr hier berechnet, nur angezeigt
        vermoegen_text = f"{charakter.vermoegen} {charakter.waehrungseinheit}"

        # Berechnung der Parade
        kaempfen_fertigkeit = charakter.fertigkeiten.get('Kämpfen')
        if kaempfen_fertigkeit:
            kaempfen_wert = kaempfen_fertigkeit.wert
        else:
            kaempfen_wert = 4  # Standardwert, wenn Kämpfen nicht vorhanden
            
        parade_basis = 2 + kaempfen_wert // 2
        parade_bonus = 0
        
        # Talent-Boni für Parade
        if "Block" in charakter.selected_talente:
            parade_bonus += 1  # Block: +1 Parade
        
        if "Harter Block" in charakter.selected_talente:
            # Harter Block ersetzt Block (nicht kumulativ)
            parade_bonus += 1  # Harter Block: +1 Parade
        
        if "Meister aller Waffen" in charakter.selected_talente:
            parade_bonus += 1  # Meister aller Waffen: +1 Parade
        
        if "Waffenmeister" in charakter.selected_talente:
            parade_bonus += 1  # Waffenmeister: +1 Parade

        if "Herdritter" in charakter.selected_talente:
            parade_bonus += 1  # Herdritter (Hellfrost): +1 Parade

        charakter.parade = parade_basis + parade_bonus
      
        # Debug-Ausgaben zur Fehleridentifikation
        #Logger.debug("=== Berechne abgeleitete Werte ===")
        #Logger.debug(f"Ausgewählte Handicaps: {charakter.selected_handicaps}")
        for hcap_key in charakter.selected_handicaps:
            if hcap_key in charakter.handicaps:
                hcap = charakter.handicaps[hcap_key]
                #Logger.debug(f"- {hcap_key}: Name={hcap.name}, Stufe={hcap.stufe}")
        
        # === BEWEGUNGSWEITE BERECHNUNG ===
        bewegungsweite_malus = 0
        
        # 1. Handicap-Effekte für Bewegungsweite
        for handicap_key in charakter.selected_handicaps:
            if handicap_key in charakter.handicaps:
                handicap = charakter.handicaps[handicap_key]
                
                # Explizite Abfragen für jeden Handicap-Typ
                if handicap.name == "Langsam":
                    if handicap.stufe == "leicht":
                        bewegungsweite_malus += 1
                        #Logger.debug(f"Bewegungsweite -1 durch Langsam (leicht)")
                    elif handicap.stufe == "schwer":
                        bewegungsweite_malus += 2
                        #Logger.debug(f"Bewegungsweite -2 durch Langsam (schwer)")
                
                elif handicap.name == "Fettleibig" and handicap.stufe == "leicht":
                    bewegungsweite_malus += 1
                    #Logger.debug(f"Bewegungsweite -1 durch Fettleibig (leicht)")
                
                elif handicap.name == "Alt" and handicap.stufe == "schwer":
                    bewegungsweite_malus += 1
                    #Logger.debug(f"Bewegungsweite -1 durch Alt (schwer)")

        # 2. Völker-Effekte für Bewegungsweite
        voelker_bewegungsweite_bonus = _berechne_voelker_bewegungsweite_bonus(charakter)
        bewegungsweite_malus -= voelker_bewegungsweite_bonus  # Bonus ist negativ bei Malus

        # 2b. Cyberware-Effekte für Bewegungsweite
        cyberware_bw_bonus = _berechne_cyberware_bewegungsweite_bonus(charakter)
        bewegungsweite_malus -= cyberware_bw_bonus
        
        # Bewegungsweite anpassen (nicht unter 1)
        #Logger.debug(f"Bewegungsweite-Malus gesamt: {bewegungsweite_malus}")
        bewegungsweite = max(1, bewegungsweite - bewegungsweite_malus)
        #Logger.debug(f"Resultierende Bewegungsweite: {bewegungsweite}")

        # Sicherstellen, dass bewegungsweite im Charakter-Objekt aktualisiert wird
        charakter.bewegungsweite = bewegungsweite

        # === ROBUSTHEIT BERECHNUNG ===
        konstitution_attribut = charakter.attribute.get('Konstitution')
        if konstitution_attribut:
            konstitution_wert = konstitution_attribut.wert
        else:
            konstitution_wert = 4  # Standardwert, wenn Konstitution nicht vorhanden

        # Größe und Robustheit getrennt führen:
        # - groesse: Mensch = 0; Volks-Größe + Größe-relevante Talente/Handicaps
        # - robustheit_bonus: echte Robustheit-Boni (Talente Raufbold/Schläger/Jünger Erthas, Fettleibig, Cyberware, Volk-Rest)
        # Endformel: robustheit_basis = (KON//2) + 2 + groesse + robustheit_bonus
        groesse = 0
        robustheit_bonus = 0

        # Talent-Effekte
        if "Kräftig" in charakter.selected_talente:
            groesse += 1  # Kräftig erhöht die Größe (und damit Robustheit) um 1

        if "Raufbold" in charakter.selected_talente:
            robustheit_bonus += 1  # Raufbold: +1 Robustheit (kein Größe-Effekt)

        if "Schläger" in charakter.selected_talente:
            robustheit_bonus += 1  # Schläger: +1 Robustheit (kein Größe-Effekt)

        if "Jünger Erthas" in charakter.selected_talente:
            robustheit_bonus += 1  # Jünger Erthas (Hellfrost): +1 Robustheit

        # Handicap-Effekte
        for handicap_name in charakter.selected_handicaps:
            if handicap_name in charakter.handicaps:
                handicap = charakter.handicaps[handicap_name]

                # Fettleibig (leicht): +1 Robustheit (Körperfett, kein Größenwachstum)
                if "Fettleibig" in handicap.name and handicap.stufe == "leicht":
                    robustheit_bonus += 1

                # Klein (leicht): -1 Größe (und damit -1 Robustheit)
                elif "Klein" in handicap.name and handicap.stufe == "leicht":
                    groesse -= 1

        # Völker-Effekte: Größe und Robustheit-Bonus getrennt
        voelker_groesse = _berechne_voelker_groesse(charakter)
        groesse += voelker_groesse

        voelker_robustheit_bonus = _berechne_voelker_robustheit_bonus(charakter)
        robustheit_bonus += voelker_robustheit_bonus

        # Cyberware-Effekte für Robustheit (kein Größe-Effekt)
        cyberware_robustheit_bonus = _berechne_cyberware_robustheit_bonus(charakter)
        robustheit_bonus += cyberware_robustheit_bonus

        # Größe als abgeleiteten Wert speichern
        charakter.groesse = groesse

        # Basis-Robustheit ohne Rüstung: (Konstitution/2) + 2 + Größe + Robustheit-Bonus
        charakter.robustheit_basis = (konstitution_wert // 2) + 2 + groesse + robustheit_bonus

        # Gesamtrüstungsschutz berechnen (inklusive natürlicher Panzerung)
        from functions.ausruestung_funktionen import berechne_gesamt_ruestungsschutz
        gesamt_ruestungsschutz = berechne_gesamt_ruestungsschutz(charakter)
        gesamt_torso = gesamt_ruestungsschutz.get('Torso', 0)
        
        # 4. Natürliche Panzerung aus Völker-Effekten hinzufügen
        natuerliche_panzerung = _berechne_voelker_natuerliche_panzerung(charakter)
        gesamt_torso += natuerliche_panzerung

        # 4b. Natürliche Panzerung aus Cyberware
        cyberware_panzerung = _berechne_cyberware_natuerliche_panzerung(charakter)
        gesamt_torso += cyberware_panzerung
        
        Logger.debug(f"Rüstungsschutz: Normal={gesamt_ruestungsschutz.get('Torso', 0)}, Natürlich={natuerliche_panzerung}, Cyberware={cyberware_panzerung}, Gesamt={gesamt_torso}")

        # Gesamte Robustheit (Basis + Rüstung)
        charakter.robustheit = charakter.robustheit_basis + gesamt_torso

        # String für die Anzeige
        charakter.robustheit_mit_ruestung = f"{charakter.robustheit} ({gesamt_torso})"
        
        # === BENNYS BERECHNUNG ===
        # Talente für Bennys
        if "Glück" in charakter.selected_talente:
            bennys += 1  # Glück: +1 Benny
        
        if "Großes Glück" in charakter.selected_talente:
            bennys += 1  # Großes Glück: +1 Bennys
            
        # Handicap-Effekte für Bennys
        for handicap_name in charakter.selected_handicaps:
            if handicap_name in charakter.handicaps:
                handicap = charakter.handicaps[handicap_name]
                
                # Jung (leicht oder schwer)
                if "Jung" in handicap.name:
                    if handicap.stufe == "leicht":
                        bennys += 1  # Jung (leicht): +1 Benny
                    elif handicap.stufe == "schwer":
                        bennys += 2  # Jung (schwer): +2 Bennys

        # Völker-Effekte für Bennys (z.B. Halbling Glück)
        voelker_benny_bonus = _berechne_voelker_benny_bonus(charakter)
        bennys += voelker_benny_bonus
            
        charakter.bennys = bennys  # Aktualisiere Bennys im Charakter-Objekt

        # Maximale Traglast berechnen (inkl. Cyberware-Bonus)
        from functions.ausruestung_funktionen import berechne_traglast
        maximale_traglast = berechne_traglast(charakter)
        cyberware_traglast_bonus = _berechne_cyberware_traglast_bonus(charakter)
        maximale_traglast += cyberware_traglast_bonus
        charakter.maximale_traglast = maximale_traglast

        # Gesamtgewicht wird automatisch über die Property berechnet - keine manuelle Zuweisung nötig

        # === CYBERWARE STRESS BERECHNUNG ===
        from functions.cyberware_funktionen import ist_cyberware_setting
        if ist_cyberware_setting(charakter.active_setting_name):
            from functions.cyberware_funktionen import (
                berechne_stresslimit, berechne_stress_maximum, berechne_stress_aktuell
            )
            charakter.cyberware_stresslimit = berechne_stresslimit(charakter)
            charakter.cyberware_stress_maximum = berechne_stress_maximum(charakter)
            charakter.cyberware_stress_aktuell = berechne_stress_aktuell(charakter)

        # Zusammenstellen der abgeleiteten Werte
        abgeleitete_werte = {
            'Bewegungsweite': bewegungsweite,
            'Parade': charakter.parade,
            'Größe': groesse,
            'Robustheit': f"{charakter.robustheit} ({gesamt_torso})",
            'Machtpunkte': machtpunkte,
            'Wunden': wunden,
            'Erschöpfung': erschoepfung,
            'Bennys': bennys,
            'Entschlossenheit': entschlossenheit,
            'Maximale Traglast': maximale_traglast,
            'Gesamtgewicht': charakter.gesamtgewicht
        }

        return abgeleitete_werte

    except Exception as e:
        Logger.error(f"Fehler bei der Berechnung der abgeleiteten Werte: {e}")
        return {}


def _berechne_voelker_bewegungsweite_bonus(charakter):
    """
    Berechnet den Bewegungsweite-Bonus durch das ausgewählte Volk.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        int: Bewegungsweite-Bonus (kann negativ sein)
    """
    bewegungsweite_bonus = 0
    
    try:
        # Finde das ausgewählte Volk
        ausgewaehltes_volk = None
        for volk_name, ist_ausgewaehlt in charakter.voelker_selected.items():
            if ist_ausgewaehlt and volk_name in charakter.voelker:
                ausgewaehltes_volk = charakter.voelker[volk_name]
                break
        
        if ausgewaehltes_volk:
            bewegungsweite_bonus = ausgewaehltes_volk.get_bewegungsweite_bonus()
            Logger.debug(f"Völker-Bewegungsweite-Bonus von {ausgewaehltes_volk.name}: {bewegungsweite_bonus}")
    
    except Exception as e:
        Logger.error(f"Fehler bei Völker-Bewegungsweite-Berechnung: {e}")
    
    return bewegungsweite_bonus


def _berechne_voelker_robustheit_bonus(charakter):
    """
    Berechnet den echten Robustheit-Bonus des ausgewählten Volks (ohne Größe-Anteil).

    Args:
        charakter: Das Charakterobjekt

    Returns:
        int: Robustheit-Bonus (kann negativ sein)
    """
    robustheit_bonus = 0

    try:
        # Finde das ausgewählte Volk
        ausgewaehltes_volk = None
        for volk_name, ist_ausgewaehlt in charakter.voelker_selected.items():
            if ist_ausgewaehlt and volk_name in charakter.voelker:
                ausgewaehltes_volk = charakter.voelker[volk_name]
                break

        if ausgewaehltes_volk:
            robustheit_bonus = ausgewaehltes_volk.get_robustheit_bonus()
            groesse_mod = ausgewaehltes_volk.get_groesse_modifikator()
            Logger.debug(f"Völker-Robustheit-Bonus von {ausgewaehltes_volk.name}: {robustheit_bonus}")
            # Sanity-Check: doppelte Codierung detektieren (rb != 0 UND groesse != 0)
            if robustheit_bonus != 0 and groesse_mod != 0:
                Logger.warning(
                    f"Volk {ausgewaehltes_volk.name} hat sowohl robustheit_bonus={robustheit_bonus} "
                    f"als auch groesse_modifikator={groesse_mod}. Beide werden auf Robustheit "
                    f"addiert (legitim z.B. bei Vampir/Flickenmonster). Falls das eine Doppelung "
                    f"durch Altdaten ist, bitte Setting-JSON migrieren."
                )

    except Exception as e:
        Logger.error(f"Fehler bei Völker-Robustheit-Berechnung: {e}")

    return robustheit_bonus


def _berechne_voelker_groesse(charakter):
    """
    Berechnet den Größe-Modifikator durch das ausgewählte Volk.
    Mensch = 0, Halbling = -1, Halbriese = +3 etc.

    Args:
        charakter: Das Charakterobjekt

    Returns:
        int: Größe-Modifikator (kann negativ sein)
    """
    groesse_modifikator = 0

    try:
        ausgewaehltes_volk = None
        for volk_name, ist_ausgewaehlt in charakter.voelker_selected.items():
            if ist_ausgewaehlt and volk_name in charakter.voelker:
                ausgewaehltes_volk = charakter.voelker[volk_name]
                break

        if ausgewaehltes_volk:
            groesse_modifikator = ausgewaehltes_volk.get_groesse_modifikator()
            if groesse_modifikator != 0:
                Logger.debug(f"Völker-Größe-Modifikator von {ausgewaehltes_volk.name}: {groesse_modifikator:+d}")

    except Exception as e:
        Logger.error(f"Fehler bei Völker-Größe-Berechnung: {e}")

    return groesse_modifikator


def _berechne_voelker_natuerliche_panzerung(charakter):
    """
    NEU: Berechnet die natürliche Panzerung durch das ausgewählte Volk.
    Diese wird zum Rüstungsschutz addiert, nicht zur Basis-Robustheit.
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        int: Natürliche Panzerung (immer >= 0)
    """
    natuerliche_panzerung = 0
    
    try:
        # Finde das ausgewählte Volk
        ausgewaehltes_volk = None
        for volk_name, ist_ausgewaehlt in charakter.voelker_selected.items():
            if ist_ausgewaehlt and volk_name in charakter.voelker:
                ausgewaehltes_volk = charakter.voelker[volk_name]
                break
        
        if ausgewaehltes_volk:
            # Prüfe auf natürliche Panzerung in den speziellen Effekten
            spezielle_effekte = ausgewaehltes_volk.effects.get('spezielle_effekte', {})

            if isinstance(spezielle_effekte, list):
                # Neues Listen-Format vom Volksgenerator: [{'typ': 'panzerung_2', 'wert': True}]
                for effekt in spezielle_effekte:
                    if effekt.get('typ') == 'panzerung_bonus':
                        natuerliche_panzerung = effekt.get('wert', 0)
                    elif effekt.get('typ') == 'panzerung_2' and effekt.get('wert'):
                        natuerliche_panzerung = 2
                    elif effekt.get('typ') == 'panzerung_1' and effekt.get('wert'):
                        natuerliche_panzerung = 1
            elif isinstance(spezielle_effekte, dict):
                # Altes Dict-Format von _parse_effects_from_text
                if spezielle_effekte.get('panzerung_bonus'):
                    natuerliche_panzerung = spezielle_effekte.get('panzerung_bonus', 0)
                elif spezielle_effekte.get('panzerung_2', False):
                    natuerliche_panzerung = 2
                elif spezielle_effekte.get('panzerung_1', False):
                    natuerliche_panzerung = 1

            if natuerliche_panzerung > 0:
                Logger.debug(f"Natürliche Panzerung +{natuerliche_panzerung} von {ausgewaehltes_volk.name}")
    
    except Exception as e:
        Logger.error(f"Fehler bei Berechnung natürlicher Panzerung: {e}")
    
    return natuerliche_panzerung


def _berechne_cyberware_robustheit_bonus(charakter):
    """
    Berechnet den Robustheit-Bonus durch aktive Cyberware.
    Summiert 'robustheit_bonus' aller aktiven Installationen.

    Args:
        charakter: Das Charakterobjekt

    Returns:
        int: Cyberware-Robustheit-Bonus
    """
    bonus = 0
    try:
        from functions.cyberware_funktionen import ist_cyberware_setting, get_aktive_cyberware
        if not ist_cyberware_setting(getattr(charakter, 'active_setting_name', '')):
            return 0
        for inst in get_aktive_cyberware(charakter):
            bonus += inst.effekte.get('robustheit_bonus', 0)
        if bonus:
            Logger.debug(f"Cyberware-Robustheit-Bonus: +{bonus}")
    except Exception as e:
        Logger.error(f"Fehler bei Cyberware-Robustheit-Berechnung: {e}")
    return bonus


def _berechne_cyberware_natuerliche_panzerung(charakter):
    """
    Berechnet die natürliche Panzerung durch aktive Cyberware.
    Summiert 'panzerung_bonus' aller aktiven Installationen mit 'natuerliche_panzerung: true'.

    Args:
        charakter: Das Charakterobjekt

    Returns:
        int: Cyberware-Panzerungsbonus
    """
    panzerung = 0
    try:
        from functions.cyberware_funktionen import ist_cyberware_setting, get_aktive_cyberware
        if not ist_cyberware_setting(getattr(charakter, 'active_setting_name', '')):
            return 0
        for inst in get_aktive_cyberware(charakter):
            if inst.effekte.get('natuerliche_panzerung'):
                panzerung += inst.effekte.get('panzerung_bonus', 0)
        # Beachte max_kumulativ (Standard: 10 mit getragener Panzerung)
        if panzerung:
            Logger.debug(f"Cyberware-Natürliche-Panzerung: +{panzerung}")
    except Exception as e:
        Logger.error(f"Fehler bei Cyberware-Panzerung-Berechnung: {e}")
    return panzerung


def _berechne_cyberware_bewegungsweite_bonus(charakter):
    """
    Berechnet den Bewegungsweite-Bonus durch aktive Cyberware.
    Summiert 'bewegungsweite_bonus' aller aktiven Installationen.

    Args:
        charakter: Das Charakterobjekt

    Returns:
        int: Cyberware-Bewegungsweite-Bonus
    """
    bonus = 0
    try:
        from functions.cyberware_funktionen import ist_cyberware_setting, get_aktive_cyberware
        if not ist_cyberware_setting(getattr(charakter, 'active_setting_name', '')):
            return 0
        for inst in get_aktive_cyberware(charakter):
            bonus += inst.effekte.get('bewegungsweite_bonus', 0)
        if bonus:
            Logger.debug(f"Cyberware-Bewegungsweite-Bonus: +{bonus}")
    except Exception as e:
        Logger.error(f"Fehler bei Cyberware-Bewegungsweite-Berechnung: {e}")
    return bonus


def _berechne_cyberware_traglast_bonus(charakter):
    """
    Berechnet den Traglast-Bonus durch aktive Cyberware.
    'traglast_staerke_bonus' wird als virtueller Stärke-Bonus umgerechnet:
    +1 Würfeltyp = +20 Traglast (2 Stärke-Punkte × 10 kg).

    Args:
        charakter: Das Charakterobjekt

    Returns:
        int: Cyberware-Traglast-Bonus in kg
    """
    bonus = 0
    try:
        from functions.cyberware_funktionen import ist_cyberware_setting, get_aktive_cyberware
        if not ist_cyberware_setting(getattr(charakter, 'active_setting_name', '')):
            return 0
        for inst in get_aktive_cyberware(charakter):
            staerke_bonus = inst.effekte.get('traglast_staerke_bonus', 0)
            bonus += staerke_bonus * 20  # +1 Würfeltyp = +2 Stärke = +20 Traglast
        if bonus:
            Logger.debug(f"Cyberware-Traglast-Bonus: +{bonus} kg")
    except Exception as e:
        Logger.error(f"Fehler bei Cyberware-Traglast-Berechnung: {e}")
    return bonus


def _berechne_voelker_benny_bonus(charakter):
    """
    Berechnet den Benny-Bonus durch das ausgewählte Volk (z.B. Halbling mit Glück-Talent).
    
    Args:
        charakter: Das Charakterobjekt
        
    Returns:
        int: Benny-Bonus
    """
    benny_bonus = 0
    
    try:
        # Finde das ausgewählte Volk
        ausgewaehltes_volk = None
        for volk_name, ist_ausgewaehlt in charakter.voelker_selected.items():
            if ist_ausgewaehlt and volk_name in charakter.voelker:
                ausgewaehltes_volk = charakter.voelker[volk_name]
                break
        
        if ausgewaehltes_volk:
            # Prüfe auf automatische Talente, die Bennys geben
            auto_talente = ausgewaehltes_volk.effects.get('auto_talente', [])
            if 'Glück' in auto_talente:
                benny_bonus += 1
                Logger.debug(f"Völker-Benny-Bonus von {ausgewaehltes_volk.name}: +1 (Glück)")
    
    except Exception as e:
        Logger.error(f"Fehler bei Völker-Benny-Berechnung: {e}")
    
    return benny_bonus