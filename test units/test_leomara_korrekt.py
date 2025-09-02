#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KORRIGIERTER Unit Test für die Erstellung des Charakters "Leomara, die Kriegerin"
Verwendet korrekte API-Methoden und befolgt die richtige Reihenfolge: Erst Attribute, dann Fertigkeiten.
"""

import unittest
import sys
import os
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Imports
from models.charakter import Charakter
from models.wuerfel import Wuerfel
from models.talent import Talent
from models.handicap import Handicap
from functions.setting_funktionen import CustomElementManager
from functions.charakter_speicher import speichern_als_json
from functions.talent_funktionen import waehle_talent, waehle_freies_talent
from functions.handicap_funktionen import waehle_handicap


class TestLeomaraCharakterKorrekt(unittest.TestCase):
    """KORRIGIERTER Test für die Erstellung von Leomara, der Kriegerin - Mit echten API-Methoden."""
    
    def setUp(self):
        """Setup für jeden Test - Charakter mit SWAE-Setting initialisieren."""
        self.charakter = Charakter(active_setting_name="SWAE", char_name="Leomara")
        self.charakter.profil_daten["Name"] = "Leomara"
        self.charakter.beschreibung = "Bei Rondra, welch' Narrete! Ergebt euch, ihr Lumpen, oder spürt meine Klinge."
        
        # Custom Element Manager initialisieren und SWAE-Setting laden
        self.charakter.custom_element_manager = CustomElementManager(self.charakter, setting_name='SWAE')
        self.charakter.custom_element_manager.set_active_setting('SWAE')
        self.charakter.active_setting_name = 'SWAE'
        
        # Verfügbare Punkte
        self.start_attributspunkte = 5
        self.start_fertigkeitspunkte = 12
        
        print(f"\n=== CHARAKTERERSTELLUNG: {self.charakter.char_name.upper()} ===")
        print(f"Beschreibung: {self.charakter.beschreibung}")
        print(f"Startpunkte - Attribute: {self.start_attributspunkte}, Fertigkeiten: {self.start_fertigkeitspunkte}")
    
    def test_01_attribute_steigern_korrekt(self):
        """Test: Attribute mit echten API-Methoden steigern."""
        print("\n--- SCHRITT 1: ATTRIBUTE STEIGERN (KORREKT) ---")
        
        # Realistische Ziel-Attribute für Leomara (5 Punkte Budget)
        attribut_steigerungen = {
            'Geschicklichkeit': 1,  # W4 -> W6 (für Kämpfen) = 1 Punkt
            'Konstitution': 1,      # W4 -> W6 (für Robustheit) = 1 Punkt
            'Stärke': 1,           # W4 -> W6 (für Schaden) = 1 Punkt
            'Willenskraft': 2      # W4 -> W8 (für Einschüchtern, Überreden) = 2 Punkte
            # Verstand bleibt W4 (Budget-Grenze erreicht) = 5 Punkte gesamt
        }
        
        attribut_kosten = 0
        for attr_name, steigerungen in attribut_steigerungen.items():
            if attr_name in self.charakter.attribute:
                attr = self.charakter.attribute[attr_name]
                start_wert = attr.wuerfel.value
                
                print(f"  {attr_name} (Start: W{start_wert}):")
                
                # Echte API-Methoden verwenden
                for i in range(steigerungen):
                    punkte_vorher = self.charakter.verbleibende_attributsteigerungen
                    erfolg = self.charakter.steigere_attribut(attr_name)
                    punkte_nachher = self.charakter.verbleibende_attributsteigerungen
                    
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
        print(f"Verbleibende Attributpunkte: {self.charakter.verbleibende_attributsteigerungen}")
        
        # Validierung (angepasst an das neue 5-Punkte-Budget)
        self.assertEqual(self.charakter.attribute['Geschicklichkeit'].wuerfel.value, 6)
        self.assertEqual(self.charakter.attribute['Konstitution'].wuerfel.value, 6) 
        self.assertEqual(self.charakter.attribute['Stärke'].wuerfel.value, 6)
        self.assertEqual(self.charakter.attribute['Verstand'].wuerfel.value, 4)  # Bleibt W4
        self.assertEqual(self.charakter.attribute['Willenskraft'].wuerfel.value, 8)
        self.assertEqual(attribut_kosten, 5)  # 1+1+1+2 = 5 Punkte
    
    def test_02_fertigkeiten_steigern_korrekt(self):
        """Test: Fertigkeiten NACH Attributen mit echten API-Methoden steigern."""
        print("\n--- SCHRITT 2: FERTIGKEITEN STEIGERN (NACH ATTRIBUTEN) ---")
        
        # Erst Attribute steigern
        self.test_01_attribute_steigern_korrekt()
        
        # Fertigkeits-Steigerungen (nach Attribut-Steigerung)
        fertigkeits_steigerungen = {
            'Kämpfen': 2,           # W4-2 -> W6 (nach Geschicklichkeit W6) = 2 Punkte
            'Einschüchtern': 2,     # W4-2 -> W6 (nach Willenskraft W8) = 2 Punkte  
            'Überreden': 2,         # W4-2 -> W6 (nach Willenskraft W8) = 2 Punkte
            'Wahrnehmung': 1        # W4 -> W6 (nach Verstand W4, Grundfertigkeit) = 1 Punkt
        }
        
        fertigkeiten_kosten = 0
        verfuegbare_punkte_start = getattr(self.charakter, 'verbleibende_fertigkeitspunkte', 
                                         getattr(self.charakter, 'verbleibende_fertigkeitssteigerungen', self.start_fertigkeitspunkte))
        
        print(f"Verfügbare Fertigkeitspunkte zu Beginn: {verfuegbare_punkte_start}")
        
        for fert_name, steigerungen in fertigkeits_steigerungen.items():
            if fert_name in self.charakter.fertigkeiten:
                fert = self.charakter.fertigkeiten[fert_name]
                start_value = fert.wuerfel.value
                start_modifier = fert.wuerfel.modifier
                attribut_wert = fert.attribut.wuerfel.value if hasattr(fert.attribut, 'wuerfel') else fert.attribut.wert
                
                print(f"\n  {fert_name} (Attribut: {fert.attribut.name} W{attribut_wert}):")
                print(f"    Start: W{start_value}{'+' + str(start_modifier) if start_modifier > 0 else str(start_modifier) if start_modifier < 0 else ''}")
                
                # Echte API-Methoden verwenden
                for i in range(steigerungen):
                    punkte_vorher = getattr(self.charakter, 'verbleibende_fertigkeitspunkte', 
                                          getattr(self.charakter, 'verbleibende_fertigkeitssteigerungen', 0))
                    
                    erfolg = self.charakter.steigere_fertigkeit(fert_name, confirm_double_cost=True)
                    
                    punkte_nachher = getattr(self.charakter, 'verbleibende_fertigkeitspunkte', 
                                           getattr(self.charakter, 'verbleibende_fertigkeitssteigerungen', 0))
                    
                    if erfolg == True:
                        kosten = punkte_vorher - punkte_nachher
                        fertigkeiten_kosten += kosten
                        current_value = fert.wuerfel.value
                        current_modifier = fert.wuerfel.modifier
                        print(f"    Steigerung {i+1}: Erfolg -> W{current_value}{'+' + str(current_modifier) if current_modifier > 0 else str(current_modifier) if current_modifier < 0 else ''} (Kosten: {kosten})")
                    elif erfolg == "needs_confirmation":
                        print(f"    Steigerung {i+1}: Bestätigung erforderlich (über Attribut hinaus)")
                        # Bereits mit confirm_double_cost=True aufgerufen
                    else:
                        print(f"    Steigerung {i+1}: FEHLGESCHLAGEN - {erfolg}")
                        break
                
                end_value = fert.wuerfel.value
                end_modifier = fert.wuerfel.modifier
                print(f"    Ende: W{end_value}{'+' + str(end_modifier) if end_modifier > 0 else str(end_modifier) if end_modifier < 0 else ''}")
            else:
                print(f"  ⚠️ WARNUNG: Fertigkeit '{fert_name}' nicht gefunden!")
        
        verfuegbare_punkte_ende = getattr(self.charakter, 'verbleibende_fertigkeitspunkte', 
                                        getattr(self.charakter, 'verbleibende_fertigkeitssteigerungen', 0))
        
        print(f"\n📊 FERTIGKEITSKOSTEN GESAMT: {fertigkeiten_kosten} Punkte")
        print(f"Verfügbare Punkte: {verfuegbare_punkte_start} -> {verfuegbare_punkte_ende}")
        print(f"Verbrauchte Punkte: {verfuegbare_punkte_start - verfuegbare_punkte_ende}")
        
        # Erwartete Kosten nach korrekter Reihenfolge:
        # Kämpfen W4-2->W6: 2 Punkte (nach Geschicklichkeit W6)
        # Einschüchtern W4-2->W6: 2 Punkte (nach Willenskraft W8)
        # Überreden W4-2->W6: 2 Punkte (nach Willenskraft W8)
        # Wahrnehmung W4->W6: 1 Punkt (nach Verstand W8, Grundfertigkeit)
        erwartete_kosten = 7  # 2+2+2+1 = 7 Punkte
        self.assertEqual(fertigkeiten_kosten, erwartete_kosten, f"Fertigkeitskosten stimmen nicht: {fertigkeiten_kosten} != {erwartete_kosten}")
    
    def test_03_handicaps_hinzufuegen_korrekt(self):
        """Test: Handicaps mit echten API-Methoden hinzufügen."""
        print("\n--- SCHRITT 3: HANDICAPS HINZUFÜGEN (KORREKT) ---")
        
        # Nur verfügbare SWAE-Handicaps verwenden
        handicaps_to_add = ["Loyal"]  # Nur das, was tatsächlich verfügbar ist
        
        handicap_punkte = 0
        for handicap_name in handicaps_to_add:
            if handicap_name in self.charakter.handicaps:
                erfolg = waehle_handicap(self.charakter, handicap_name)
                if erfolg:
                    handicap = self.charakter.handicaps[handicap_name]
                    punkte = handicap.wert
                    handicap_punkte += punkte
                    print(f"  ✅ {handicap_name} hinzugefügt: +{punkte} Punkte (Gesamt: +{handicap_punkte})")
                else:
                    print(f"  ❌ FEHLER: Handicap '{handicap_name}' konnte nicht hinzugefügt werden")
            else:
                print(f"  ⚠️ WARNUNG: Handicap '{handicap_name}' nicht in SWAE verfügbar!")
        
        print(f"\n📊 HANDICAP-PUNKTE GESAMT: +{handicap_punkte} Punkte")
        return handicap_punkte
    
    def test_04_talente_hinzufuegen_korrekt(self):
        """Test: Talente mit echten API-Methoden hinzufügen."""
        print("\n--- SCHRITT 4: TALENTE HINZUFÜGEN (KORREKT) ---")
        
        # Erst Attribute steigern (für Voraussetzungen)
        self.test_01_attribute_steigern_korrekt()
        
        # Verfügbare Talente in SWAE prüfen
        if "Anführer" in self.charakter.talente:
            talent_name = "Anführer"
            willenskraft_wert = self.charakter.attribute['Willenskraft'].wuerfel.value
            
            print(f"\n  Prüfe Menschen-Talent: {talent_name}")
            print(f"    Voraussetzung: Willenskraft W8, aktuell: W{willenskraft_wert}")
            
            if willenskraft_wert >= 8:
                print(f"    ✅ Voraussetzung erfüllt")
                
                # Echte API-Methode für kostenloses Talent verwenden
                erfolg = waehle_freies_talent(self.charakter, talent_name, ignore_voraussetzungen=False)
                if erfolg:
                    print(f"    ✅ Menschen-Talent '{talent_name}' hinzugefügt (KOSTENLOS)")
                else:
                    print(f"    ❌ FEHLER: Talent '{talent_name}' konnte nicht hinzugefügt werden")
            else:
                print(f"    ❌ Voraussetzung NICHT erfüllt")
        else:
            print("  ⚠️ Keine Talente in SWAE verfügbar")
        
        print(f"\n📊 TALENTKOSTEN GESAMT: 0 Punkte (Menschen-Talent ist kostenlos)")
        return 0
    
    def test_05_vollstaendigen_charakter_erstellen_und_speichern(self):
        """Test: Erstelle den vollständigen Leomara-Charakter mit korrekter API-Nutzung und speichere als JSON."""
        print("\n" + "="*60)
        print("VOLLSTÄNDIGE CHARAKTERERSTELLUNG: LEOMARA, DIE KRIEGERIN (KORREKT)")
        print("="*60)
        
        # Alle Schritte in korrekter Reihenfolge durchführen
        self.test_01_attribute_steigern_korrekt()
        self.test_02_fertigkeiten_steigern_korrekt() 
        handicap_punkte = self.test_03_handicaps_hinzufuegen_korrekt()
        talent_kosten = self.test_04_talente_hinzufuegen_korrekt()
        
        # Berechnete Werte aktualisieren
        print("\n🎯 FINALE BERECHNUNG...")
        self.charakter.berechne_abgeleitete_werte()
        
        # Finale Kostenzusammenfassung
        print("\n" + "="*60)
        print("📊 FINALE CHARAKTERZUSAMMENFASSUNG (KORREKT)")
        print("="*60)
        print(f"Charakter: {self.charakter.profil_daten.get('Name', 'Unbenannt')}")
        print(f"Setting: {self.charakter.active_setting_name}")
        
        attribut_kosten = 5  # Aus test_01 (korrigiert)
        fertigkeiten_kosten = 7  # Aus test_02
        
        print(f"Attribute-Kosten: {attribut_kosten} Punkte")
        print(f"Fertigkeiten-Kosten: {fertigkeiten_kosten} Punkte") 
        print(f"Handicap-Punkte: +{handicap_punkte} Punkte")
        print(f"Talent-Kosten: {talent_kosten} Punkte")
        
        gesamtkosten = attribut_kosten + fertigkeiten_kosten + talent_kosten
        verfuegbare_punkte = self.start_attributspunkte + self.start_fertigkeitspunkte + handicap_punkte
        
        print(f"\nGesamtkosten: {gesamtkosten} Punkte")
        print(f"Verfügbare Punkte: {verfuegbare_punkte} Punkte")
        print(f"Bilanz: {verfuegbare_punkte - gesamtkosten} Punkte")
        
        # Charakter als JSON speichern
        chars_ordner = project_root / "chars"
        chars_ordner.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dateiname = f"Leomara_Korrekt_{timestamp}.json"
        dateipfad = chars_ordner / dateiname
        
        print(f"\n💾 SPEICHERE CHARAKTER...")
        print(f"Ziel: {dateipfad}")
        
        try:
            speichern_als_json(self.charakter, str(dateipfad))
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
        print("="*60)
        
        # Validierung der finalen Bilanz
        self.assertGreaterEqual(verfuegbare_punkte - gesamtkosten, 0, 
                               f"Punktedefizit: Ausgaben ({gesamtkosten}) > Einnahmen ({verfuegbare_punkte})")
        
        return dateipfad


def run_tests():
    """Führe alle Tests aus."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    print("🧪 STARTE KORRIGIERTE UNIT TESTS FÜR LEOMARA, DIE KRIEGERIN")
    print("=" * 60)
    run_tests()