# functions/abgeleitete_werte.py

from kivy.logger import Logger
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild

def berechne_abgeleitete_werte(charakter):
    """
    Berechnet die abgeleiteten Werte des Charakters, wie Parade, Robustheit usw.
    Berücksichtigt die Erschöpfung und Talente.
    
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
            
        charakter.parade = parade_basis + parade_bonus
      
        # Debug-Ausgaben zur Fehleridentifikation
        Logger.debug("=== Berechne abgeleitete Werte ===")
        Logger.debug(f"Ausgewählte Handicaps: {charakter.selected_handicaps}")
        for hcap_key in charakter.selected_handicaps:
            if hcap_key in charakter.handicaps:
                hcap = charakter.handicaps[hcap_key]
                Logger.debug(f"- {hcap_key}: Name={hcap.name}, Stufe={hcap.stufe}")
        
        # Handicap-Effekte für Bewegungsweite
        bewegungsweite_malus = 0
        
        # Prüfe auf ausgewählte Handicaps, die Bewegungsweite beeinflussen
        for handicap_key in charakter.selected_handicaps:
            if handicap_key in charakter.handicaps:
                handicap = charakter.handicaps[handicap_key]
                
                # Explizite Abfragen für jeden Handicap-Typ
                if handicap.name == "Langsam":
                    if handicap.stufe == "leicht":
                        bewegungsweite_malus += 1
                        Logger.debug(f"Bewegungsweite -1 durch Langsam (leicht)")
                    elif handicap.stufe == "schwer":
                        bewegungsweite_malus += 2
                        Logger.debug(f"Bewegungsweite -2 durch Langsam (schwer)")
                
                elif handicap.name == "Fettleibig" and handicap.stufe == "leicht":
                    bewegungsweite_malus += 1
                    Logger.debug(f"Bewegungsweite -1 durch Fettleibig (leicht)")
                
                elif handicap.name == "Alt" and handicap.stufe == "schwer":
                    bewegungsweite_malus += 1
                    Logger.debug(f"Bewegungsweite -1 durch Alt (schwer)")
        
        # Bewegungsweite anpassen (nicht unter 1)
        Logger.debug(f"Bewegungsweite-Malus: {bewegungsweite_malus}")
        bewegungsweite = max(1, bewegungsweite - bewegungsweite_malus)
        Logger.debug(f"Resultierende Bewegungsweite: {bewegungsweite}")

        # Sicherstellen, dass bewegungsweite im Charakter-Objekt aktualisiert wird
        charakter.bewegungsweite = bewegungsweite

        # Berechnung der Robustheit
        konstitution_attribut = charakter.attribute.get('Konstitution')
        if konstitution_attribut:
            konstitution_wert = konstitution_attribut.wert
        else:
            konstitution_wert = 4  # Standardwert, wenn Konstitution nicht vorhanden

        # Talent-Boni für Robustheit/Größe
        robustheit_bonus = 0
        
        if "Kräftig" in charakter.selected_talente:
            robustheit_bonus += 1  # Kräftig: +1 Robustheit durch erhöhte Größe
        
        if "Raufbold" in charakter.selected_talente:
            robustheit_bonus += 1  # Raufbold: +1 Robustheit

        if "Schläger" in charakter.selected_talente:
            robustheit_bonus += 1  # Schläger: +1 Robustheit      
            
        # Handicap-Effekte für Robustheit
        for handicap_name in charakter.selected_handicaps:
            if handicap_name in charakter.handicaps:
                handicap = charakter.handicaps[handicap_name]
                
                # Fettleibig (leicht)
                if "Fettleibig" in handicap.name and handicap.stufe == "leicht":
                    robustheit_bonus += 1  # Fettleibig: +1 Robustheit
                
                # Klein (leicht)
                elif "Klein" in handicap.name and handicap.stufe == "leicht":
                    robustheit_bonus -= 1  # Klein: -1 Robustheit
        
        # Basis-Robustheit ohne Rüstung: (Konstitution/2) + 2 + Boni
        charakter.robustheit_basis = (konstitution_wert // 2) + 2 + robustheit_bonus

        # Gesamtrüstungsschutz berechnen
        from functions.ausruestung_funktionen import berechne_gesamt_ruestungsschutz
        gesamt_ruestungsschutz = berechne_gesamt_ruestungsschutz(charakter)
        gesamt_torso = gesamt_ruestungsschutz.get('Torso', 0)

        # Gesamte Robustheit (Basis + Rüstung)
        charakter.robustheit = charakter.robustheit_basis + gesamt_torso

        # String für die Anzeige
        charakter.robustheit_mit_ruestung = f"{charakter.robustheit} ({gesamt_torso})"
        
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
            
        charakter.bennys = bennys  # Aktualisiere Bennys im Charakter-Objekt

        # Maximale Traglast berechnen
        from functions.ausruestung_funktionen import berechne_traglast
        maximale_traglast = berechne_traglast(charakter)
        charakter.maximale_traglast = maximale_traglast

        # Gesamtgewicht berechnen
        from functions.ausruestung_funktionen import berechne_gesamtgewicht
        gesamtgewicht = berechne_gesamtgewicht(charakter)
        charakter.gesamtgewicht = gesamtgewicht

        # Zusammenstellen der abgeleiteten Werte
        abgeleitete_werte = {
            'Bewegungsweite': bewegungsweite,
            'Parade': charakter.parade,
            'Robustheit': f"{charakter.robustheit} ({gesamt_torso})",
            'Machtpunkte': machtpunkte,
            'Wunden': wunden,
            'Erschöpfung': erschoepfung,
            'Bennys': bennys,
            'Entschlossenheit': entschlossenheit,
            'Maximale Traglast': maximale_traglast,
            'Gesamtgewicht': gesamtgewicht
        }

        return abgeleitete_werte

    except Exception as e:
        Logger.error(f"Fehler bei der Berechnung der abgeleiteten Werte: {e}")
        return {}
