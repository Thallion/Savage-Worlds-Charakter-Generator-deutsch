# functions/abgeleitete_werte.py

from kivy.logger import Logger
from models.waffe import Waffe
from models.ruestung import Ruestung
from models.schild import Schild

def berechne_abgeleitete_werte(charakter):
    """
    Berechnet die abgeleiteten Werte des Charakters, wie Parade, Robustheit usw.
    Berücksichtigt die Erschöpfung.
    
    Args:
        charakter: Das Charakterobjekt, dessen Werte berechnet werden sollen
        
    Returns:
        dict: Ein Dictionary mit allen abgeleiteten Werten
    """
    try:
        # Standardwerte
        bewegungsweite = 6
        bennys = 3
        entschlossenheit = 0
        machtpunkte = charakter.machtpunkte  # Machtpunkte aus dem Charakter übernehmen
        wunden = 0  # Kann später durch Spielereignisse verändert werden
        erschoepfung = charakter.erschoepfung  # Aktuelle Erschöpfung

        # Berechnung der Parade
        kaempfen_fertigkeit = charakter.fertigkeiten.get('Kämpfen')
        if kaempfen_fertigkeit:
            kaempfen_wert = kaempfen_fertigkeit.wert
        else:
            kaempfen_wert = 4  # Standardwert, wenn Kämpfen nicht vorhanden
            
        charakter.parade = 2 + kaempfen_wert // 2

        # Berechnung der Robustheit
        konstitution_attribut = charakter.attribute.get('Konstitution')
        if konstitution_attribut:
            konstitution_wert = konstitution_attribut.wert
        else:
            konstitution_wert = 4  # Standardwert, wenn Konstitution nicht vorhanden

        # Basis-Robustheit ohne Rüstung
        charakter.robustheit_basis = (konstitution_wert // 2) + 2

        # Gesamtrüstungsschutz berechnen
        from functions.ausruestung_funktionen import berechne_gesamt_ruestungsschutz
        gesamt_ruestungsschutz = berechne_gesamt_ruestungsschutz(charakter)
        gesamt_torso = gesamt_ruestungsschutz.get('Torso', 0)

        # Gesamte Robustheit (Basis + Rüstung)
        charakter.robustheit = charakter.robustheit_basis + gesamt_torso

        # String für die Anzeige
        charakter.robustheit_mit_ruestung = f"{charakter.robustheit} ({gesamt_torso})"

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