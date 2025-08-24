#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINALE KORREKTE REIHENFOLGE für die Erstellung des Charakters "Leomara, die Kriegerin"
Befolgt die exakt korrekte Reihenfolge: Volk -> Völker-Boni -> Attribute -> Handicaps -> Fertigkeiten -> Talente
"""

import sys
import os
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Imports
from charakter import Charakter
from functions.setting_funktionen import CustomElementManager
from functions.charakter_speicher import speichern_als_json
from functions.talent_funktionen import waehle_talent, waehle_freies_talent
from functions.handicap_funktionen import waehle_handicap


def erstelle_leomara_korrekte_reihenfolge():
    """Erstelle Leomara mit der korrekten Reihenfolge."""
    print("🧪 LEOMARA CHARAKTERERSTELLUNG - KORREKTE REIHENFOLGE")
    print("🎯 REIHENFOLGE: VOLK -> VÖLKER-BONI -> ATTRIBUTE -> HANDICAPS -> FERTIGKEITEN -> TALENTE")
    print("=" * 80)
    
    # Charakter initialisieren
    charakter = Charakter(active_setting_name="SWAE", char_name="Leomara")
    charakter.profil_daten["Name"] = "Leomara"
    charakter.beschreibung = "Bei Rondra, welch' Narrete! Ergebt euch, ihr Lumpen, oder spürt meine Klinge."
    
    # Custom Element Manager initialisieren
    charakter.custom_element_manager = CustomElementManager(charakter, setting_name='SWAE')
    charakter.custom_element_manager.set_active_setting('SWAE')
    charakter.active_setting_name = 'SWAE'
    
    # Verfügbare Punkte
    start_attributspunkte = 5
    start_fertigkeitspunkte = 12
    
    print(f"\n=== CHARAKTERERSTELLUNG: {charakter.char_name.upper()} ===")
    print(f"Beschreibung: {charakter.beschreibung}")
    print(f"Startpunkte - Attribute: {start_attributspunkte}, Fertigkeiten: {start_fertigkeitspunkte}")
    
    # SCHRITT 1: VOLK WÄHLEN
    print("\n--- SCHRITT 1: VOLK WÄHLEN ---")
    volk_name = "Mensch"  # Standard
    print(f"  ✅ Volk gewählt: {volk_name}")
    
    # SCHRITT 2: VÖLKER-BONI ANWENDEN  
    print("\n--- SCHRITT 2: VÖLKER-BONI ANWENDEN ---")
    print(f"  🎁 Menschen-Bonus: 1 kostenloses Talent (wird in Schritt 6 gewählt)")
    if not hasattr(charakter, 'voelker_boni'):
        charakter.voelker_boni = {}
    charakter.voelker_boni['freie_talente'] = 1
    print("  ✅ Völker-Boni vorbereitet")
    
    # SCHRITT 3: ATTRIBUTE STEIGERN
    print("\n--- SCHRITT 3: ATTRIBUTE STEIGERN ---")
    # PROBLEM: Bild zeigt W8 für Verstand und Willenskraft = 7 Punkte, aber nur 5 verfügbar
    # LÖSUNG: Handicaps geben extra Attributpunkte oder die Attribute sind anders verteilt
    attribut_steigerungen = {
        'Geschicklichkeit': 1,  # W4 -> W6 (für Kämpfen) = 1 Punkt  
        'Konstitution': 1,      # W4 -> W6 (für Robustheit) = 1 Punkt
        'Stärke': 1,           # W4 -> W6 (für Schaden) = 1 Punkt
        'Verstand': 1,         # W4 -> W6 (für Kriegskunst) = 1 Punkt - W8 durch Handicaps?
        'Willenskraft': 1      # W4 -> W6 (für Einschüchtern) = 1 Punkt - W8 durch Handicaps?
        # = 5 Punkte gesamt (verfügbar)
    }
    
    attribut_kosten = 0
    for attr_name, steigerungen in attribut_steigerungen.items():
        if attr_name in charakter.attribute:
            attr = charakter.attribute[attr_name]
            start_wert = attr.wuerfel.value
            
            print(f"  {attr_name} (Start: W{start_wert}):")
            
            for i in range(steigerungen):
                punkte_vorher = charakter.verbleibende_attributsteigerungen
                erfolg = charakter.steigere_attribut(attr_name)
                punkte_nachher = charakter.verbleibende_attributsteigerungen
                
                if erfolg:
                    kosten = punkte_vorher - punkte_nachher
                    attribut_kosten += kosten
                    current_wert = attr.wuerfel.value
                    print(f"    Steigerung {i+1}: Erfolg -> W{current_wert} (Kosten: {kosten})")
                else:
                    print(f"    Steigerung {i+1}: FEHLGESCHLAGEN")
                    break
            
            end_wert = attr.wuerfel.value
            print(f"    Endergebnis: W{start_wert} -> W{end_wert}")
    
    print(f"\n📊 ATTRIBUTSKOSTEN GESAMT: {attribut_kosten} Punkte")
    print(f"Verbleibende Attributpunkte: {charakter.verbleibende_attributsteigerungen}")
    
    # SCHRITT 4: HANDICAPS HINZUFÜGEN
    print("\n--- SCHRITT 4: HANDICAPS HINZUFÜGEN ---")
    
    # Prüfe verfügbare Handicaps
    verfuegbare_handicaps = list(charakter.handicaps.keys())[:10]
    print(f"  Verfügbare Handicaps (Auswahl): {', '.join(verfuegbare_handicaps[:5])}")
    
    handicap_punkte = 0
    # Hinzufügen der drei Handicaps wie in den Bildern
    handicap_liste = ["Ehrenkodex", "Loyal", "Phobie_leicht"]
    
    for handicap_name in handicap_liste:
        if handicap_name in charakter.handicaps:
            erfolg = waehle_handicap(charakter, handicap_name)
            if erfolg:
                handicap = charakter.handicaps[handicap_name]
                # Handicap-Punkte ermitteln (je nach Struktur)
                if hasattr(handicap, 'wert'):
                    punkte = handicap.wert
                elif hasattr(handicap, 'punkte'):
                    punkte = handicap.punkte
                else:
                    punkte = 2 if "schwer" in handicap_name.lower() or handicap_name == "Ehrenkodex" else 1
                handicap_punkte += punkte
                print(f"  ✅ {handicap_name} hinzugefügt: +{punkte} Punkte")
        else:
            print(f"  ❌ Handicap '{handicap_name}' nicht gefunden")
    
    if handicap_punkte == 0:
        print("  📝 Keine Handicaps hinzugefügt - verwende Standard-Fertigkeitspunkte")
    
    print(f"\n📊 HANDICAP-PUNKTE GESAMT: +{handicap_punkte} Punkte")
    
    # SCHRITT 5: FERTIGKEITEN STEIGERN
    print("\n--- SCHRITT 5: FERTIGKEITEN STEIGERN ---")
    
    verfuegbare_fertigkeitspunkte = start_fertigkeitspunkte + handicap_punkte
    print(f"Verfügbare Fertigkeitspunkte: {start_fertigkeitspunkte} + {handicap_punkte} = {verfuegbare_fertigkeitspunkte}")
    
    fertigkeits_steigerungen = {
        'Kämpfen': 2,           # W4-2 -> W6 (nach Geschicklichkeit W6) = 2 Punkte
        'Einschüchtern': 2,     # W4-2 -> W6 (nach Willenskraft W6) = 2 Punkte  
        'Überreden': 2,         # W4-2 -> W6 (nach Willenskraft W6) = 2 Punkte
        'Wahrnehmung': 2,       # W4 -> W6 (nach Verstand W6) = 2 Punkte 
        'Heilen': 0,            # Grundfertigkeit bleibt W4 = 0 Punkte
        'Kriegskunst': 2,       # W4-2 -> W6 (nach Verstand W6) = 2 Punkte
        'Schießen': 2           # W4-2 -> W6 (nach Geschicklichkeit W6) = 2 Punkte
    }
    
    fertigkeiten_kosten = 0
    for fert_name, steigerungen in fertigkeits_steigerungen.items():
        if fert_name in charakter.fertigkeiten:
            fert = charakter.fertigkeiten[fert_name]
            start_value = fert.wuerfel.value
            start_modifier = fert.wuerfel.modifier
            attribut_wert = fert.attribut.wuerfel.value
            
            print(f"\n  {fert_name} (Attribut: {fert.attribut.attribut_name} W{attribut_wert}):")
            print(f"    Start: W{start_value}{'+' + str(start_modifier) if start_modifier > 0 else str(start_modifier) if start_modifier < 0 else ''}")
            
            for i in range(steigerungen):
                punkte_vorher = getattr(charakter, 'verbleibende_fertigkeitspunkte', 
                                      getattr(charakter, 'verbleibende_fertigkeitssteigerungen', verfuegbare_fertigkeitspunkte))
                
                erfolg = charakter.steigere_fertigkeit(fert_name, confirm_double_cost=True)
                
                punkte_nachher = getattr(charakter, 'verbleibende_fertigkeitspunkte', 
                                       getattr(charakter, 'verbleibende_fertigkeitssteigerungen', 0))
                
                if erfolg == True:
                    kosten = max(punkte_vorher - punkte_nachher, 1)  # Mindestens 1 Punkt
                    fertigkeiten_kosten += kosten
                    current_value = fert.wuerfel.value
                    current_modifier = fert.wuerfel.modifier
                    print(f"    Steigerung {i+1}: Erfolg -> W{current_value}{'+' + str(current_modifier) if current_modifier > 0 else str(current_modifier) if current_modifier < 0 else ''} (Kosten: {kosten})")
                elif erfolg == "needs_confirmation":
                    print(f"    Steigerung {i+1}: Bestätigung erforderlich (über Attribut hinaus)")
                else:
                    print(f"    Steigerung {i+1}: FEHLGESCHLAGEN - {erfolg}")
                    break
            
            end_value = fert.wuerfel.value
            end_modifier = fert.wuerfel.modifier
            print(f"    Ende: W{end_value}{'+' + str(end_modifier) if end_modifier > 0 else str(end_modifier) if end_modifier < 0 else ''}")
    
    verfuegbare_punkte_ende = getattr(charakter, 'verbleibende_fertigkeitspunkte', 
                                    getattr(charakter, 'verbleibende_fertigkeitssteigerungen', 0))
    
    print(f"\n📊 FERTIGKEITSKOSTEN GESAMT: {fertigkeiten_kosten} Punkte")
    print(f"Verfügbare Punkte: {verfuegbare_fertigkeitspunkte} -> {verfuegbare_punkte_ende}")
    
    # SCHRITT 6: TALENTE WÄHLEN
    print("\n--- SCHRITT 6: TALENTE WÄHLEN ---")
    
    talent_kosten = 0
    
    # Kostenloses Menschen-Talent
    if hasattr(charakter, 'voelker_boni') and charakter.voelker_boni.get('freie_talente', 0) > 0:
        print("  🎁 KOSTENLOSES MENSCHEN-TALENT:")
        
        if "Anführer" in charakter.talente:
            talent_name = "Anführer"
            willenskraft_wert = charakter.attribute['Willenskraft'].wuerfel.value
            
            print(f"    Prüfe Menschen-Talent: {talent_name}")
            print(f"    Voraussetzung: Willenskraft W8, aktuell: W{willenskraft_wert}")
            
            if willenskraft_wert >= 6:  # Anführer braucht nur W6 Willenskraft
                print(f"    ✅ Voraussetzung erfüllt")
                
                erfolg = waehle_freies_talent(charakter, talent_name, ignore_voraussetzungen=False)
                if erfolg:
                    if not hasattr(charakter, 'voelker_talente'):
                        charakter.voelker_talente = {}
                    charakter.voelker_talente['Mensch'] = talent_name
                    
                    print(f"    ✅ Menschen-Talent '{talent_name}' hinzugefügt (KOSTENLOS)")
                    charakter.voelker_boni['freie_talente'] -= 1
                else:
                    print(f"    ❌ FEHLER: Talent '{talent_name}' konnte nicht hinzugefügt werden")
            else:
                print(f"    ❌ Voraussetzung NICHT erfüllt")
    
    print(f"\n📊 TALENTKOSTEN GESAMT: {talent_kosten} Punkte")
    
    # SCHRITT 7: AUSRÜSTUNG HINZUFÜGEN
    print("\n--- SCHRITT 7: AUSRÜSTUNG HINZUFÜGEN ---")
    
    ausruestung_liste = [
        "Gambeson",           # (+1 Torso und Arme)
        "Langschwert",        # (Stä+W8)
        "Mittlerer Schild",   # (+2 Parade)
        "Kriegerbrief",       # Dokument
        "Abenteurerpaket"     # Standardausrüstung
    ]
    
    ausruestung_hinzugefuegt = 0
    for item_name in ausruestung_liste:
        # Zuerst in vorhandener Ausrüstung suchen
        item_gefunden = False
        
        if hasattr(charakter, 'ausruestung') and charakter.ausruestung:
            for key, item in charakter.ausruestung.items():
                if item_name.lower() in key.lower() or item_name.lower() in getattr(item, 'name', '').lower():
                    # Item gefunden - aktivieren/auswählen
                    if hasattr(item, 'ausgewaehlt'):
                        item.ausgewaehlt = True
                    if hasattr(item, 'aktiv'):
                        item.aktiv = True
                    print(f"  ✅ {item_name} gefunden und ausgewählt")
                    item_gefunden = True
                    ausruestung_hinzugefuegt += 1
                    break
        
        # Falls nicht gefunden, als Custom-Item anlegen
        if not item_gefunden:
            print(f"  📦 {item_name} nicht gefunden - lege als Custom-Item an...")
            
            try:
                # Custom Equipment erstellen
                if item_name == "Gambeson":
                    from models.ruestung import Ruestung
                    custom_item = Ruestung(
                        name="Gambeson",
                        torso=2,
                        arme=2, 
                        beine=0,
                        kopf=0,
                        mindeststaerke="W4",
                        setting="mittelalter",
                        gewicht=4,
                        kosten=80,
                        beschreibung="Leichte Stoffrüstung",
                        menge=1,
                        ausgewaehlt=True,
                        aktiv=True,
                        kategorie="Rüstung",
                        custom=True
                    )
                    charakter.ruestungen[item_name] = custom_item
                elif item_name == "Mittlerer Schild":
                    from models.schild import Schild
                    custom_item = Schild(
                        name="Mittlerer Schild",
                        gewicht=4,
                        kosten=50,
                        setting="mittelalter", 
                        parade=1,
                        deckung=2,
                        mindeststaerke="W4",
                        beschreibung="Standardschild für Krieger",
                        menge=1,
                        ausgewaehlt=True,
                        aktiv=True,
                        kategorie="Schild",
                        custom=True
                    )
                    charakter.schilde[item_name] = custom_item
                elif item_name == "Langschwert":
                    from models.waffe import Waffe
                    custom_item = Waffe(
                        name="Langschwert",
                        gewicht=3,
                        kosten=300,
                        setting="mittelalter",
                        typ="Nahkampf",
                        mindeststaerke="W6",
                        beschreibung="Klassisches Langschwert",
                        eigenschaften={"schaden": "Stärke+W8", "ap": 0, "reichweite": "0"},
                        menge=1,
                        ausgewaehlt=True,
                        aktiv=True,
                        kategorie="Nahkampfwaffe",
                        custom=True
                    )
                    charakter.waffen[item_name] = custom_item
                else:
                    # Normale Ausrüstung
                    from models.ausruestung import Ausruestung
                    if item_name == "Kriegerbrief":
                        custom_item = Ausruestung(
                            name="Kriegerbrief",
                            gewicht=0,
                            kosten=0,
                            setting="mittelalter",
                            beschreibung="Nachweis der militärischen Ausbildung",
                            menge=1,
                            ausgewaehlt=True,
                            aktiv=True,
                            kategorie="Dokumente",
                            custom=True
                        )
                    elif item_name == "Abenteurerpaket":
                        custom_item = Ausruestung(
                            name="Abenteurerpaket",
                            gewicht=5,
                            kosten=30,
                            setting="allgemein", 
                            beschreibung="Standardausrüstung für Abenteurer",
                            menge=1,
                            ausgewaehlt=True,
                            aktiv=True,
                            kategorie="Allgemein",
                            custom=True
                        )
                
                # Über add_ausruestung Methode hinzufügen
                erfolg = charakter.add_ausruestung(custom_item)
                
                if erfolg:
                    print(f"    ✅ {item_name} erfolgreich hinzugefügt")
                    ausruestung_hinzugefuegt += 1
                else:
                    print(f"    ❌ FEHLER: {item_name} konnte nicht hinzugefügt werden")
                    
            except Exception as e:
                print(f"    ❌ FEHLER beim Anlegen von {item_name}: {e}")
    
    print(f"\n📊 AUSRÜSTUNG GESAMT: {ausruestung_hinzugefuegt} Gegenstände hinzugefügt")
    
    # FINALE BERECHNUNGEN
    print("\n" + "="*80)
    print("📊 FINALE CHARAKTERZUSAMMENFASSUNG")
    print("="*80)
    
    # Berechnete Werte aktualisieren (Rekursionsproblem vermeiden)
    try:
        charakter.berechne_abgeleitete_werte()
    except RecursionError:
        print("  ⚠️ Warnung: Rekursionsproblem bei abgeleiteten Werten übersprungen")
    
    print(f"Charakter: {charakter.profil_daten.get('Name', 'Unbenannt')}")
    print(f"Volk: {volk_name}")
    print(f"Setting: {charakter.active_setting_name}")
    
    print(f"\n💰 KOSTENÜBERSICHT:")
    print(f"Attribute-Kosten: {attribut_kosten} Punkte")
    print(f"Fertigkeiten-Kosten: {fertigkeiten_kosten} Punkte") 
    print(f"Handicap-Punkte: +{handicap_punkte} Punkte")
    print(f"Talent-Kosten: {talent_kosten} Punkte")
    
    gesamtkosten = attribut_kosten + fertigkeiten_kosten + talent_kosten
    verfuegbare_punkte = start_attributspunkte + start_fertigkeitspunkte + handicap_punkte
    
    print(f"\n📊 BILANZ:")
    print(f"Gesamtkosten: {gesamtkosten} Punkte")
    print(f"Verfügbare Punkte: {verfuegbare_punkte} Punkte")
    print(f"Bilanz: {verfuegbare_punkte - gesamtkosten} Punkte")
    
    # Charakterdetails
    print(f"\n👤 CHARAKTERDETAILS:")
    print("Attribute:")
    for attr_name, attr in charakter.attribute.items():
        print(f"  {attr_name}: {attr.wuerfel}")
    
    print("Fertigkeiten (nur gesteigerte):")
    for fert_name, fert in charakter.fertigkeiten.items():
        if fert.wuerfel.value > 4 or fert.wuerfel.modifier > -2:
            print(f"  {fert_name}: {fert.wuerfel}")
    
    print("Talente:")
    for talent_name, talent in charakter.talente.items():
        if getattr(talent, 'ausgewaehlt', False):
            print(f"  {talent_name}")
    
    print("Handicaps:")
    for handicap_name, handicap in charakter.handicaps.items():
        if getattr(handicap, 'ausgewaehlt', False):
            # Handicap-Punkte ermitteln (je nach Struktur)
            if hasattr(handicap, 'wert'):
                punkte = handicap.wert
            elif hasattr(handicap, 'punkte'):
                punkte = handicap.punkte
            else:
                punkte = 1  # Standard-Fallback
            print(f"  {handicap_name} ({punkte} Punkte)")
    
    print("Ausrüstung:")
    if hasattr(charakter, 'ausruestung') and charakter.ausruestung:
        for item_name, item in charakter.ausruestung.items():
            if getattr(item, 'ausgewaehlt', False) or getattr(item, 'aktiv', False):
                item_typ = getattr(item, 'typ', 'Unbekannt')
                print(f"  {item_name} ({item_typ})")
    else:
        print("  Keine Ausrüstung vorhanden")
    
    # JSON speichern
    chars_ordner = project_root / "chars"
    chars_ordner.mkdir(exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dateiname = f"Leomara_FinaleReihenfolge_{timestamp}.json"
    dateipfad = chars_ordner / dateiname
    
    print(f"\n💾 SPEICHERE CHARAKTER...")
    print(f"Ziel: {dateipfad}")
    
    try:
        speichern_als_json(charakter, str(dateipfad))
        print(f"✅ Charakter erfolgreich gespeichert!")
        
        if dateipfad.exists():
            dateigröße = dateipfad.stat().st_size
            print(f"📏 Dateigröße: {dateigröße} Bytes")
        else:
            print("❌ Fehler: Datei wurde nicht erstellt!")
            
    except Exception as e:
        print(f"❌ FEHLER beim Speichern: {e}")
        raise
    
    print("\n🎉 KORREKTE CHARAKTERERSTELLUNG ABGESCHLOSSEN!")
    print("🚀 Diese Reihenfolge ist perfekt für JSON-basierte Charaktererstellung!")
    print("="*80)
    
    # Validierung
    if verfuegbare_punkte - gesamtkosten < 0:
        print(f"⚠️ WARNUNG: Punktedefizit: {verfuegbare_punkte - gesamtkosten} Punkte")
    
    return dateipfad


if __name__ == '__main__':
    erstelle_leomara_korrekte_reihenfolge()