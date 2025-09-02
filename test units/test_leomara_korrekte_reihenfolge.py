#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KORREKTE REIHENFOLGE Unit Test für die Erstellung des Charakters "Leomara, die Kriegerin"
Befolgt die exakt korrekte Reihenfolge: Volk -> Völker-Boni -> Attribute -> Handicaps -> Fertigkeiten -> Talente
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


class TestLeomaraKorrekteReihenfolge(unittest.TestCase):
    """KORREKTE REIHENFOLGE Test für die Erstellung von Leomara, der Kriegerin - Perfekte API-Methoden."""
    
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
    
    def test_01_volk_waehlen(self):
        """SCHRITT 1: Volk wählen (Mensch ist bereits Standard)."""
        print("\n--- SCHRITT 1: VOLK WÄHLEN ---")
        
        # Mensch ist bereits als Standard-Volk gesetzt
        aktuelles_volk = getattr(self.charakter, 'volk', None)
        if hasattr(aktuelles_volk, 'name'):
            volk_name = aktuelles_volk.name
        else:
            # Fallback: Prüfe völker Dictionary
            for name, volk in self.charakter.voelker.items():
                if getattr(volk, 'ausgewaehlt', False):
                    volk_name = name
                    break
            else:
                volk_name = "Mensch"  # Standard-Fallback
        
        print(f"  ✅ Volk gewählt: {volk_name}")
        
        # Völker-Eigenschaften anzeigen
        if volk_name in self.charakter.voelker:
            volk = self.charakter.voelker[volk_name]
            print(f"  📋 Völker-Eigenschaften:")
            if hasattr(volk, 'beschreibung'):
                print(f"    Beschreibung: {volk.beschreibung[:100]}...")
        
        # Validierung
        self.assertEqual(volk_name, "Mensch")
        return volk_name
    
    def test_02_voelker_boni_anwenden(self):
        """SCHRITT 2: Völker-spezifische Boni anwenden (kostenlose Talente/Fertigkeiten)."""
        print("\n--- SCHRITT 2: VÖLKER-BONI ANWENDEN ---")
        
        # Volk aus Schritt 1
        volk_name = self.test_01_volk_waehlen()
        
        print(f"  Prüfe Völker-Boni für {volk_name}:")
        
        # Mensch bekommt 1 kostenloses Talent (wird später in Schritt 6 gewählt)
        if volk_name == "Mensch":
            print("  🎁 Menschen-Bonus: 1 kostenloses Talent (wird in Schritt 6 gewählt)")
            print("  📝 Hinweis: Menschen haben keine kostenlosen Fertigkeiten")
            
            # Menschen-Bonus für späteren Gebrauch markieren
            if not hasattr(self.charakter, 'voelker_boni'):
                self.charakter.voelker_boni = {}
            self.charakter.voelker_boni['freie_talente'] = 1
        
        print(f"  ✅ Völker-Boni für {volk_name} vorbereitet")
        return True
    
    def test_03_attribute_steigern(self):
        """SCHRITT 3: Attribute mit echten API-Methoden steigern."""
        print("\n--- SCHRITT 3: ATTRIBUTE STEIGERN ---")
        
        # Vorherige Schritte
        self.test_02_voelker_boni_anwenden()
        
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
        
        # Validierung
        self.assertEqual(self.charakter.attribute['Geschicklichkeit'].wuerfel.value, 6)
        self.assertEqual(self.charakter.attribute['Konstitution'].wuerfel.value, 6) 
        self.assertEqual(self.charakter.attribute['Stärke'].wuerfel.value, 6)
        self.assertEqual(self.charakter.attribute['Verstand'].wuerfel.value, 4)  # Bleibt W4
        self.assertEqual(self.charakter.attribute['Willenskraft'].wuerfel.value, 8)
        self.assertEqual(attribut_kosten, 5)  # 1+1+1+2 = 5 Punkte
        
        return attribut_kosten
    
    def test_04_handicaps_hinzufuegen(self):
        """SCHRITT 4: Handicaps hinzufügen (geben zusätzliche Punkte)."""
        print("\n--- SCHRITT 4: HANDICAPS HINZUFÜGEN ---")
        
        # Vorherige Schritte
        self.test_03_attribute_steigern()
        
        # Verfügbare SWAE-Handicaps prüfen und hinzufügen
        handicaps_to_add = []
        
        # Prüfe welche Handicaps verfügbar sind
        verfuegbare_handicaps = list(self.charakter.handicaps.keys())[:5]  # Erste 5 zur Übersicht
        print(f"  Verfügbare Handicaps (Auswahl): {', '.join(verfuegbare_handicaps)}")
        
        # Wähle sinnvolle Handicaps für eine Kriegerin
        for handicap_name in ["Loyal", "Ehrencodex", "Überheblich"]:
            if handicap_name in self.charakter.handicaps:
                handicaps_to_add.append(handicap_name)
                break  # Nur ein Handicap für den Test
        
        if not handicaps_to_add:
            # Fallback: Erstes verfügbares Handicap nehmen
            if verfuegbare_handicaps:
                handicaps_to_add = [verfuegbare_handicaps[0]]
        
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
        
        # Wenn keine Handicaps hinzugefügt werden konnten
        if handicap_punkte == 0:
            print("  📝 Hinweis: Keine Handicaps hinzugefügt - verwende Standard-Fertigkeitspunkte")
        
        print(f"\n📊 HANDICAP-PUNKTE GESAMT: +{handicap_punkte} Punkte")
        return handicap_punkte
    
    def test_05_fertigkeiten_steigern(self):
        """SCHRITT 5: Fertigkeiten steigern (NACH Attributen und Handicaps)."""
        print("\n--- SCHRITT 5: FERTIGKEITEN STEIGERN ---")
        
        # Vorherige Schritte
        handicap_punkte = self.test_04_handicaps_hinzufuegen()
        
        # Verfügbare Fertigkeitspunkte berechnen
        verfuegbare_punkte_start = self.start_fertigkeitspunkte + handicap_punkte
        print(f"Verfügbare Fertigkeitspunkte: {self.start_fertigkeitspunkte} (Start) + {handicap_punkte} (Handicaps) = {verfuegbare_punkte_start}")
        
        # Fertigkeits-Steigerungen (nach Attribut-Steigerung)
        fertigkeits_steigerungen = {
            'Kämpfen': 2,           # W4-2 -> W6 (nach Geschicklichkeit W6) = 2 Punkte
            'Einschüchtern': 2,     # W4-2 -> W6 (nach Willenskraft W8) = 2 Punkte  
            'Überreden': 2,         # W4-2 -> W6 (nach Willenskraft W8) = 2 Punkte
            'Wahrnehmung': 1        # W4 -> W6 (nach Verstand W4, Grundfertigkeit) = 2 Punkte (doppelt wegen > Attribut)
        }
        
        fertigkeiten_kosten = 0
        aktuelle_punkte = getattr(self.charakter, 'verbleibende_fertigkeitspunkte', 
                                 getattr(self.charakter, 'verbleibende_fertigkeitssteigerungen', verfuegbare_punkte_start))
        
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
        
        return fertigkeiten_kosten
    
    def test_06_talente_waehlen(self):
        """SCHRITT 6: Talente wählen (kostenpflichtige + kostenlose Völker-Talente)."""
        print("\n--- SCHRITT 6: TALENTE WÄHLEN ---")
        
        # Vorherige Schritte
        fertigkeiten_kosten = self.test_05_fertigkeiten_steigern()
        
        talent_kosten = 0
        
        # A) Kostenloses Menschen-Talent (aus Schritt 2)
        if hasattr(self.charakter, 'voelker_boni') and self.charakter.voelker_boni.get('freie_talente', 0) > 0:
            print("  🎁 KOSTENLOSES MENSCHEN-TALENT:")
            
            # Verfügbare Talente in SWAE prüfen  
            if "Anführer" in self.charakter.talente:
                talent_name = "Anführer"
                willenskraft_wert = self.charakter.attribute['Willenskraft'].wuerfel.value
                
                print(f"    Prüfe Menschen-Talent: {talent_name}")
                print(f"    Voraussetzung: Willenskraft W8, aktuell: W{willenskraft_wert}")
                
                if willenskraft_wert >= 8:
                    print(f"    ✅ Voraussetzung erfüllt")
                    
                    # Echte API-Methode für kostenloses Talent verwenden
                    erfolg = waehle_freies_talent(self.charakter, talent_name, ignore_voraussetzungen=False)
                    if erfolg:
                        # Als Menschen-freies Talent markieren
                        if not hasattr(self.charakter, 'voelker_talente'):
                            self.charakter.voelker_talente = {}
                        self.charakter.voelker_talente['Mensch'] = talent_name
                        
                        print(f"    ✅ Menschen-Talent '{talent_name}' hinzugefügt (KOSTENLOS)")
                        
                        # Kostenloses Talent verbraucht
                        self.charakter.voelker_boni['freie_talente'] -= 1
                    else:
                        print(f"    ❌ FEHLER: Talent '{talent_name}' konnte nicht hinzugefügt werden")
                else:
                    print(f"    ❌ Voraussetzung NICHT erfüllt")
            else:
                print("    ⚠️ Talent 'Anführer' nicht verfügbar")
        
        # B) Kostenpflichtige Talente (falls gewünscht und Punkte vorhanden)
        print(f"\n  💰 KOSTENPFLICHTIGE TALENTE:")
        print("  📝 Hinweis: Für diesen Test verzichten wir auf kostenpflichtige Talente")
        print("  📝 Grund: Fokus auf korrekte Reihenfolge und API-Verwendung")
        
        print(f"\n📊 TALENTKOSTEN GESAMT: {talent_kosten} Punkte")
        return talent_kosten
    
    def test_07_vollstaendigen_charakter_erstellen_und_speichern(self):
        """SCHRITT 7: Erstelle den vollständigen Leomara-Charakter mit korrekter Reihenfolge und speichere als JSON."""
        print("\n" + "="*80)
        print("VOLLSTÄNDIGE CHARAKTERERSTELLUNG: LEOMARA, DIE KRIEGERIN")
        print("🎯 KORREKTE REIHENFOLGE: VOLK -> VÖLKER-BONI -> ATTRIBUTE -> HANDICAPS -> FERTIGKEITEN -> TALENTE")
        print("="*80)
        
        # Alle Schritte in korrekter Reihenfolge durchführen
        volk_name = self.test_01_volk_waehlen()
        voelker_boni = self.test_02_voelker_boni_anwenden()
        attribut_kosten = self.test_03_attribute_steigern()
        handicap_punkte = self.test_04_handicaps_hinzufuegen()
        fertigkeiten_kosten = self.test_05_fertigkeiten_steigern()
        talent_kosten = self.test_06_talente_waehlen()
        
        # Berechnete Werte aktualisieren
        print("\n🎯 FINALE BERECHNUNG...")
        self.charakter.berechne_abgeleitete_werte()
        
        # Finale Kostenzusammenfassung
        print("\n" + "="*80)
        print("📊 FINALE CHARAKTERZUSAMMENFASSUNG (KORREKTE REIHENFOLGE)")
        print("="*80)
        print(f"Charakter: {self.charakter.profil_daten.get('Name', 'Unbenannt')}")
        print(f"Setting: {self.charakter.active_setting_name}")
        print(f"Volk: {volk_name}")
        
        print(f"\n💰 KOSTENÜBERSICHT:")
        print(f"Attribute-Kosten: {attribut_kosten} Punkte")
        print(f"Fertigkeiten-Kosten: {fertigkeiten_kosten} Punkte") 
        print(f"Handicap-Punkte: +{handicap_punkte} Punkte")
        print(f"Talent-Kosten: {talent_kosten} Punkte")
        
        gesamtkosten = attribut_kosten + fertigkeiten_kosten + talent_kosten
        verfuegbare_punkte = self.start_attributspunkte + self.start_fertigkeitspunkte + handicap_punkte
        
        print(f"\n📊 BILANZ:")
        print(f"Gesamtkosten: {gesamtkosten} Punkte")
        print(f"Verfügbare Punkte: {verfuegbare_punkte} Punkte")
        print(f"Bilanz: {verfuegbare_punkte - gesamtkosten} Punkte")
        
        # Charakterdetails anzeigen
        print(f"\n👤 CHARAKTERDETAILS:")
        print(f"Attribute:")
        for attr_name, attr in self.charakter.attribute.items():
            print(f"  {attr_name}: {attr.wuerfel}")
        
        print(f"Fertigkeiten (nur gesteigerte):")
        for fert_name, fert in self.charakter.fertigkeiten.items():
            if fert.wuerfel.value > 4 or fert.wuerfel.modifier > -2:
                print(f"  {fert_name}: {fert.wuerfel}")
        
        # Charakter als JSON speichern
        chars_ordner = project_root / "chars"
        chars_ordner.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dateiname = f"Leomara_KorrekteReihenfolge_{timestamp}.json"
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
        print("🚀 Diese Reihenfolge ist perfekt für JSON-basierte Charaktererstellung!")
        print("="*80)
        
        # Validierung der finalen Bilanz
        self.assertGreaterEqual(verfuegbare_punkte - gesamtkosten, 0, 
                               f"Punktedefizit: Ausgaben ({gesamtkosten}) > Einnahmen ({verfuegbare_punkte})")
        
        return dateipfad


def run_tests():
    """Führe alle Tests aus."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    print("🧪 STARTE KORREKTE REIHENFOLGE UNIT TESTS FÜR LEOMARA, DIE KRIEGERIN")
    print("🎯 REIHENFOLGE: VOLK -> VÖLKER-BONI -> ATTRIBUTE -> HANDICAPS -> FERTIGKEITEN -> TALENTE")
    print("=" * 80)
    run_tests()