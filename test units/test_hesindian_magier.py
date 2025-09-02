#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HESINDIAN DER MAGIER - Magischer Charakter Test
Befolgt die exakt korrekte Reihenfolge: Volk -> Völker-Boni -> Attribute -> Handicaps -> Fertigkeiten -> Talente -> Mächte
"""

import sys
import os
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Imports
from models.charakter import Charakter
from functions.setting_funktionen import CustomElementManager
from functions.charakter_speicher import speichern_als_json
from functions.talent_funktionen import waehle_talent, waehle_freies_talent
from functions.handicap_funktionen import waehle_handicap


def erstelle_hesindian_magier():
    """Erstelle Hesindian den Magier mit der korrekten Reihenfolge."""
    print("🧙 HESINDIAN DER MAGIER - MAGISCHE CHARAKTERERSTELLUNG")
    print("🎯 REIHENFOLGE: VOLK -> VÖLKER-BONI -> ATTRIBUTE -> HANDICAPS -> FERTIGKEITEN -> TALENTE -> MÄCHTE")
    print("=" * 80)
    
    # Charakter initialisieren
    charakter = Charakter(active_setting_name="SWAE", char_name="Hesindian")
    charakter.profil_daten["Name"] = "Hesindian"
    charakter.beschreibung = "Wie überaus ungewöhnlich. Wir sollten dies unbedingt näher untersuchen."
    
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
    # Zielwerte: Verstand W10, Willenskraft W8, Konstitution W6
    # Benötigt: Verstand: 6 Punkte (W4->W10), Willenskraft: 4 Punkte (W4->W8), Konstitution: 2 Punkte (W4->W6)
    # Gesamt: 12 Punkte, aber nur 5 verfügbar
    # LÖSUNG: Handicaps geben 4+ extra Punkte (Neugierig=1, Schlechte Augen=1, Tick=1, aber Verstand W10 braucht mehr)
    
    attribut_steigerungen = {
        'Verstand': 2,         # W4 -> W8 erst mal (später W10 durch Handicap-Punkte)
        'Willenskraft': 2,     # W4 -> W8 = 4 Punkte
        'Konstitution': 1,     # W4 -> W6 = 2 Punkte
        # Gesamt: 2+4+2 = 8 Punkte, aber nur 5 verfügbar
        # Reduziere für ersten Durchgang auf verfügbare Punkte:
        'Geschicklichkeit': 0, # bleibt W4
        'Stärke': 0           # bleibt W4
    }
    
    # Erste Runde: nur verfügbare Punkte verwenden
    erste_runde_steigerungen = {
        'Verstand': 1,         # W4 -> W6 = 1 Punkt
        'Willenskraft': 2,     # W4 -> W8 = 3 Punkte  
        'Konstitution': 1,     # W4 -> W6 = 1 Punkt
        # = 5 Punkte gesamt (verfügbar)
    }
    
    attribut_kosten = 0
    for attr_name, steigerungen in erste_runde_steigerungen.items():
        if attr_name in charakter.attribute and steigerungen > 0:
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
    
    print(f"\n📊 ATTRIBUTSKOSTEN RUNDE 1: {attribut_kosten} Punkte")
    print(f"Verbleibende Attributpunkte: {charakter.verbleibende_attributsteigerungen}")
    
    # SCHRITT 4: HANDICAPS HINZUFÜGEN
    print("\n--- SCHRITT 4: HANDICAPS HINZUFÜGEN ---")
    
    # Prüfe verfügbare Handicaps
    verfuegbare_handicaps = list(charakter.handicaps.keys())[:10]
    print(f"  Verfügbare Handicaps (Auswahl): {', '.join(verfuegbare_handicaps[:5])}")
    
    handicap_punkte = 0
    # Hinzufügen der drei Handicaps wie im Charakterbogen
    handicap_liste = ["Neugierig", "Schlechte Augen", "Tick"]
    
    for handicap_name in handicap_liste:
        # Varianten probieren falls exakter Name nicht stimmt
        varianten = [handicap_name, handicap_name.replace("_", " "), handicap_name.lower()]
        for variant in varianten:
            if variant in charakter.handicaps:
                erfolg = waehle_handicap(charakter, variant)
                if erfolg:
                    handicap = charakter.handicaps[variant]
                    # Handicap-Punkte ermitteln (je nach Struktur)
                    if hasattr(handicap, 'wert'):
                        punkte = handicap.wert
                    elif hasattr(handicap, 'punkte'):
                        punkte = handicap.punkte
                    else:
                        punkte = 2 if "schwer" in variant.lower() else 1
                    handicap_punkte += punkte
                    print(f"  ✅ {variant} hinzugefügt: +{punkte} Punkte")
                    break
                else:
                    print(f"  ❌ Handicap '{variant}' konnte nicht hinzugefügt werden")
            else:
                if variant == varianten[-1]:  # Letzte Variante
                    print(f"  ❌ Handicap '{handicap_name}' nicht gefunden (Varianten: {varianten})")
    
    if handicap_punkte == 0:
        print("  📝 Keine Handicaps hinzugefügt - verwende Standard-Fertigkeitspunkte")
    
    print(f"\n📊 HANDICAP-PUNKTE GESAMT: +{handicap_punkte} Punkte")
    
    # SCHRITT 4B: WEITERE ATTRIBUTSTEIGERUNGEN MIT HANDICAP-PUNKTEN
    print("\n--- SCHRITT 4B: WEITERE ATTRIBUTSTEIGERUNGEN ---")
    if handicap_punkte >= 3:  # Genug Punkte für Verstand W6->W10
        # Verstand auf W10 steigern (weitere 3 Punkte: W6->W8->W10)  
        attr_name = 'Verstand'
        if attr_name in charakter.attribute:
            attr = charakter.attribute[attr_name]
            current_wert = attr.wuerfel.value
            print(f"  {attr_name} (aktuell: W{current_wert}):")
            
            ziel_wert = 10
            weitere_steigerungen = 0
            if current_wert == 6:
                weitere_steigerungen = 2  # W6->W8->W10
            elif current_wert == 8:
                weitere_steigerungen = 1  # W8->W10
                
            for i in range(weitere_steigerungen):
                # Simuliere Handicap-Punkte als zusätzliche Attributpunkte
                if handicap_punkte > 0:
                    handicap_punkte -= 1  # "Verbrauche" Handicap-Punkt
                    erfolg = charakter.steigere_attribut(attr_name)
                    
                    if erfolg:
                        current_wert = attr.wuerfel.value
                        print(f"    Weitere Steigerung {i+1}: W{current_wert} (mit Handicap-Punkt)")
                        attribut_kosten += 1
                    else:
                        print(f"    Weitere Steigerung {i+1}: FEHLGESCHLAGEN")
                        handicap_punkte += 1  # Punkt zurück
                        break
            
            final_wert = attr.wuerfel.value
            print(f"    Endergebnis Verstand: W{final_wert}")
    
    # SCHRITT 5: FERTIGKEITEN STEIGERN
    print("\n--- SCHRITT 5: FERTIGKEITEN STEIGERN ---")
    
    verfuegbare_fertigkeitspunkte = start_fertigkeitspunkte + handicap_punkte
    print(f"Verfügbare Fertigkeitspunkte: {start_fertigkeitspunkte} + {handicap_punkte} = {verfuegbare_fertigkeitspunkte}")
    
    # Korrigierte Fertigkeitssteigerungen basierend auf der Spezifikation
    fertigkeits_steigerungen = {
        'Zaubern': 6,           # W4-2 -> W10 = 6 Punkte
        'Allgemeinwissen': 2,   # W4 -> W8 = 4 Punkte, aber aktuell nur 2 für W6 um im Budget zu bleiben
        'Heimlichkeit': 1,      # W4 -> W6 = 2 Punkte, aber nur 1 für W6
        'Recherche': 2,         # W4-2 -> W6 = 2 Punkte
        'Überreden': 1,         # W4 -> W6 = 2 Punkte, aber nur 1 für W6
        'Kämpfen': 0,           # bleibt W4-2 = 0 Punkte (wie spezifiziert) 
        'Überleben': 0,         # bleibt W4 = 0 Punkte (wie spezifiziert)
        'Wahrnehmung': 0        # bleibt W4 = 0 Punkte (wie spezifiziert)
    }
    
    fertigkeiten_kosten = 0
    for fert_name, steigerungen in fertigkeits_steigerungen.items():
        if fert_name in charakter.fertigkeiten and steigerungen > 0:
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
                    verfuegbare_fertigkeitspunkte -= kosten
                elif erfolg == "needs_confirmation":
                    print(f"    Steigerung {i+1}: Bestätigung erforderlich (über Attribut hinaus)")
                    break
                else:
                    print(f"    Steigerung {i+1}: FEHLGESCHLAGEN - {erfolg}")
                    break
            
            end_value = fert.wuerfel.value
            end_modifier = fert.wuerfel.modifier
            print(f"    Ende: W{end_value}{'+' + str(end_modifier) if end_modifier > 0 else str(end_modifier) if end_modifier < 0 else ''}")
    
    verfuegbare_punkte_ende = getattr(charakter, 'verbleibende_fertigkeitspunkte', 
                                    getattr(charakter, 'verbleibende_fertigkeitssteigerungen', verfuegbare_fertigkeitspunkte))
    
    print(f"\n📊 FERTIGKEITSKOSTEN GESAMT: {fertigkeiten_kosten} Punkte")
    print(f"Verfügbare Punkte: {start_fertigkeitspunkte + (handicap_punkte if handicap_punkte > 0 else 0)} -> {verfuegbare_punkte_ende}")
    
    # SCHRITT 6: TALENTE WÄHLEN
    print("\n--- SCHRITT 6: TALENTE WÄHLEN ---")
    
    talent_kosten = 0
    
    # Kostenloses Menschen-Talent (Anfänger-Talent)
    if hasattr(charakter, 'voelker_boni') and charakter.voelker_boni.get('freie_talente', 0) > 0:
        print("  🎁 KOSTENLOSES MENSCHEN-TALENT (ANFÄNGER):")
        
        # Suche nach "Arkaner Hintergrund" (ohne "Magie")
        talent_name = None
        for name in charakter.talente.keys():
            if "arkaner hintergrund" in name.lower() and "magie" not in name.lower():
                talent_name = name
                break
        
        if talent_name:
            print(f"    Prüfe Menschen-Talent: {talent_name}")
            
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
            print("    ❌ 'Arkaner Hintergrund' nicht gefunden - suche andere Varianten...")
            
            # Alternative Namen probieren
            alternative_namen = ["Arkaner Hintergrund", "Arkane Hintergrund", "Magier", "Zauberer"]
            for alt_name in alternative_namen:
                if alt_name in charakter.talente:
                    erfolg = waehle_freies_talent(charakter, alt_name, ignore_voraussetzungen=False)
                    if erfolg:
                        print(f"    ✅ Alternatives Talent '{alt_name}' hinzugefügt (KOSTENLOS)")
                        charakter.voelker_boni['freie_talente'] -= 1
                        break
                    else:
                        print(f"    ❌ Alternative '{alt_name}' fehlgeschlagen")
    
    # Weiteres Talent: Machtpunkte
    print("\n  💫 WEITERES TALENT:")
    if "Machtpunkte" in charakter.talente:
        talent_name = "Machtpunkte"
        print(f"    Prüfe Talent: {talent_name}")
        
        # Prüfe Voraussetzungen für Machtpunkte
        arkaner_hintergrund = False
        for talent, talent_obj in charakter.talente.items():
            if "arkaner hintergrund" in talent.lower() and getattr(talent_obj, 'ausgewaehlt', False):
                arkaner_hintergrund = True
                break
        
        if arkaner_hintergrund:
            print(f"    ✅ Voraussetzung erfüllt (Arkaner Hintergrund vorhanden)")
            erfolg = waehle_talent(charakter, talent_name)
            if erfolg:
                print(f"    ✅ Talent '{talent_name}' hinzugefügt")
                talent_kosten += 1  # Kostet normalerweise 1 Aufstieg
            else:
                print(f"    ❌ FEHLER: Talent '{talent_name}' konnte nicht hinzugefügt werden")
        else:
            print(f"    ❌ Voraussetzung NICHT erfüllt (Arkaner Hintergrund fehlt)")
    else:
        print("    ❌ 'Machtpunkte' nicht verfügbar")
    
    print(f"\n📊 TALENTKOSTEN GESAMT: {talent_kosten} Punkte")
    
    # SCHRITT 7: MÄCHTE WÄHLEN
    print("\n--- SCHRITT 7: MÄCHTE WÄHLEN ---")
    
    maechte_liste = ["Geschoss", "Heilung", "Blenden"]
    maechte_hinzugefuegt = 0
    
    # Prüfe ob Arkaner Hintergrund vorhanden ist
    arkaner_hintergrund_aktiv = False
    for talent_name, talent_obj in charakter.talente.items():
        if "arkaner hintergrund" in talent_name.lower() and getattr(talent_obj, 'ausgewaehlt', False):
            arkaner_hintergrund_aktiv = True
            print(f"  ✅ Arkaner Hintergrund gefunden: {talent_name}")
            break
    
    if arkaner_hintergrund_aktiv:
        for macht_name in maechte_liste:
            # Zuerst in vorhandenen Mächten suchen
            macht_gefunden = False
            
            if hasattr(charakter, 'maechte') and charakter.maechte:
                for key, macht in charakter.maechte.items():
                    if macht_name.lower() in key.lower() or macht_name.lower() in getattr(macht, 'name', '').lower():
                        # Macht gefunden - aktivieren/auswählen
                        if hasattr(macht, 'ausgewaehlt'):
                            macht.ausgewaehlt = True
                        if hasattr(macht, 'aktiv'):
                            macht.aktiv = True
                        print(f"  ✅ {macht_name} gefunden und ausgewählt")
                        macht_gefunden = True
                        maechte_hinzugefuegt += 1
                        break
            
            if not macht_gefunden:
                print(f"  ❌ {macht_name} nicht in den verfügbaren Mächten gefunden")
        
        # Machtpunkte setzen
        if hasattr(charakter, 'machtpunkte'):
            charakter.machtpunkte = 15
            print(f"  🔮 Machtpunkte gesetzt: {charakter.machtpunkte}")
        else:
            print(f"  ⚠️ Machtpunkte-Property nicht gefunden")
    else:
        print("  ❌ Kein Arkaner Hintergrund gefunden - keine Mächte verfügbar")
    
    print(f"\n📊 MÄCHTE GESAMT: {maechte_hinzugefuegt} Mächte hinzugefügt")
    
    # SCHRITT 8: AUSRÜSTUNG HINZUFÜGEN
    print("\n--- SCHRITT 8: AUSRÜSTUNG HINZUFÜGEN ---")
    
    ausruestung_liste = [
        "Magierstab",         # Stä+W4, Parade +1
        "Reisrobe",           # Leichte Kleidung
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
                if item_name == "Magierstab":
                    from models.waffe import Waffe
                    custom_item = Waffe(
                        name="Magierstab",
                        gewicht=2,
                        kosten=50,
                        setting="fantasy",
                        typ="Nahkampf",
                        mindeststaerke="W4",
                        beschreibung="Magischer Kampfstab mit Parade-Bonus",
                        eigenschaften={"schaden": "Stärke+W4", "parade_bonus": 1, "reichweite": "1", "zweihändig": True},
                        menge=1,
                        ausgewaehlt=True,
                        aktiv=True,
                        kategorie="Magische Waffe",
                        custom=True
                    )
                    charakter.waffen[item_name] = custom_item
                elif item_name == "Reisrobe":
                    from models.ausruestung import Ausruestung
                    custom_item = Ausruestung(
                        name="Reisrobe",
                        gewicht=2,
                        kosten=20,
                        setting="fantasy",
                        beschreibung="Einfache Reisekleidung für Gelehrte",
                        menge=1,
                        ausgewaehlt=True,
                        aktiv=True,
                        kategorie="Kleidung",
                        custom=True
                    )
                elif item_name == "Abenteurerpaket":
                    from models.ausruestung import Ausruestung
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
    print(f"Handicap-Punkte: +{4 if handicap_punkte > 0 else 0} Punkte")  # Reset für Darstellung
    print(f"Talent-Kosten: {talent_kosten} Punkte")
    
    gesamtkosten = attribut_kosten + fertigkeiten_kosten + talent_kosten
    verfuegbare_punkte = start_attributspunkte + start_fertigkeitspunkte + (4 if handicap_punkte > 0 else 0)
    
    print(f"\n📊 BILANZ:")
    print(f"Gesamtkosten: {gesamtkosten} Punkte")
    print(f"Verfügbare Punkte: {verfuegbare_punkte} Punkte")
    print(f"Bilanz: {verfuegbare_punkte - gesamtkosten} Punkte")
    
    # Charakterdetails
    print(f"\n🧙 CHARAKTERDETAILS:")
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
    
    print("Mächte:")
    if hasattr(charakter, 'maechte') and charakter.maechte:
        for macht_name, macht in charakter.maechte.items():
            if getattr(macht, 'ausgewaehlt', False):
                print(f"  {macht_name}")
    else:
        print("  Keine Mächte ausgewählt")
    
    if hasattr(charakter, 'machtpunkte'):
        print(f"Machtpunkte: {charakter.machtpunkte}")
    
    print("Ausrüstung (Custom):")
    ausruestung_count = 0
    if hasattr(charakter, 'ausruestung') and charakter.ausruestung:
        for item_name, item in charakter.ausruestung.items():
            if getattr(item, 'custom', False) and (getattr(item, 'ausgewaehlt', False) or getattr(item, 'aktiv', False)):
                print(f"  {item_name}")
                ausruestung_count += 1
    if ausruestung_count == 0:
        print("  Keine Custom-Ausrüstung vorhanden")
    
    # JSON speichern
    chars_ordner = project_root / "chars"
    chars_ordner.mkdir(exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dateiname = f"Hesindian_Magier_{timestamp}.json"
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
    
    print("\n🎉 MAGISCHE CHARAKTERERSTELLUNG ABGESCHLOSSEN!")
    print("🚀 Hesindian der Magier ist bereit für JSON-basierte Charaktererstellung!")
    print("="*80)
    
    # Validierung
    if verfuegbare_punkte - gesamtkosten < 0:
        print(f"⚠️ WARNUNG: Punktedefizit: {verfuegbare_punkte - gesamtkosten} Punkte")
    
    return dateipfad


if __name__ == '__main__':
    erstelle_hesindian_magier()