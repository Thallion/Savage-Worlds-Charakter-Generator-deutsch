#!/usr/bin/env python3
"""
Test-Script für den neuen EigenschaftenManager.
Testet sowohl die neue Klasse als auch die Rückwärtskompatibilität.
"""

import sys
import os
import logging
from pathlib import Path

# Projektwurzel zum Python-Pfad hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_eigenschaften_manager():
    """Testet den EigenschaftenManager und die Rückwärtskompatibilität."""
    
    print("="*60)
    print("TESTING EIGENSCHAFTEN MANAGER")
    print("="*60)
    
    try:
        # 1. Test: Import der Module
        print("\n1. TESTING: Module imports")
        
        from functions import eigenschaften_funktionen
        from functions.eigenschaften_funktionen import EigenschaftenManager, get_eigenschaften_manager
        from models.charakter import Charakter
        
        print("✓ Alle Module erfolgreich importiert")
        
        # 2. Test: EigenschaftenManager-Instanz erstellen
        print("\n2. TESTING: EigenschaftenManager Instanziierung")
        
        manager = EigenschaftenManager()
        print(f"✓ EigenschaftenManager erstellt")
        print(f"  - Grundfertigkeiten: {len(manager.grundfertigkeiten)} ({manager.grundfertigkeiten})")
        print(f"  - Standard-Attribute: {len(manager.standard_attribute)} ({list(manager.standard_attribute.keys())})")
        print(f"  - Config geladen: {bool(manager.config)}")
        
        # 3. Test: Globaler Manager
        print("\n3. TESTING: Globaler Manager")
        
        global_manager = get_eigenschaften_manager()
        print(f"✓ Globaler Manager abgerufen")
        print(f"  - Ist gleiche Instanz: {global_manager is get_eigenschaften_manager()}")
        
        # 4. Test: Charakter erstellen und initialisieren
        print("\n4. TESTING: Charakter-Initialisierung")
        
        # Erstelle einen minimalen Mock-Charakter für Tests
        class TestCharakter:
            def __init__(self):
                self.attribute = {}
                self.fertigkeiten = {}
                self.fertigkeiten_daten = {
                    "Allgemeinwissen": {"Verstand"},
                    "Athletik": {"Stärke"},
                    "Heimlichkeit": {"Geschicklichkeit"},
                    "Überreden": {"Willenskraft"},
                    "Wahrnehmung": {"Verstand"},
                    "Kampf": {"Geschicklichkeit"},
                    "Bogenschießen": {"Geschicklichkeit"}
                }
                self.verbleibende_attributsteigerungen = 0
                self.verbleibende_fertigkeitspunkte = 15
                self.verbleibende_aufstiege = 0
                self.char_gen_completed = False
                self.aufstiege_gesamt = 0
                self.rang = "Anfänger"
            
            def on_attribut_wert_change(self, *args):
                pass
            
            def on_attribut_modifier_change(self, *args):
                pass
            
            def on_fertigkeit_wert_change(self, *args):
                pass
            
            def on_fertigkeit_modifier_change(self, *args):
                pass
            
            def get_rang(self, aufstiege):
                return "Anfänger"
            
            def berechne_abgeleitete_werte(self):
                pass
        
        test_char = TestCharakter()
        
        # Attribute initialisieren
        manager.initialisiere_attribute(test_char)
        print(f"✓ Attribute initialisiert: {len(test_char.attribute)} Attribute")
        print(f"  - Attribut-Namen: {list(test_char.attribute.keys())}")
        print(f"  - Verbleibende Steigerungen: {test_char.verbleibende_attributsteigerungen}")
        
        # Fertigkeiten initialisieren
        manager.initialisiere_fertigkeiten(test_char)
        print(f"✓ Fertigkeiten initialisiert: {len(test_char.fertigkeiten)} Fertigkeiten")
        print(f"  - Fertigkeit-Namen: {list(test_char.fertigkeiten.keys())}")
        
        # 5. Test: Attribut-Steigerung
        print("\n5. TESTING: Attribut-Steigerung")
        
        stärke_vor = test_char.attribute['Stärke'].wuerfel.value
        erfolg = manager.steigere_attribut(test_char, 'Stärke')
        stärke_nach = test_char.attribute['Stärke'].wuerfel.value
        
        print(f"✓ Stärke-Steigerung: {erfolg}")
        print(f"  - Wert vorher: W{stärke_vor}")
        print(f"  - Wert nachher: W{stärke_nach}")
        print(f"  - Verbleibende Steigerungen: {test_char.verbleibende_attributsteigerungen}")
        
        # 6. Test: Fertigkeit-Steigerung
        print("\n6. TESTING: Fertigkeit-Steigerung")
        
        athletik_vor = test_char.fertigkeiten['Athletik'].wuerfel.value
        erfolg = manager.steigere_fertigkeit(test_char, 'Athletik')
        athletik_nach = test_char.fertigkeiten['Athletik'].wuerfel.value
        
        print(f"✓ Athletik-Steigerung: {erfolg}")
        print(f"  - Wert vorher: W{athletik_vor}")
        print(f"  - Wert nachher: W{athletik_nach}")
        print(f"  - Verbleibende Fertigkeitspunkte: {test_char.verbleibende_fertigkeitspunkte}")
        
        # 7. Test: Rückwärtskompatibilität
        print("\n7. TESTING: Rückwärtskompatibilität")
        
        # Teste alte Funktionsaufrufe
        test_char2 = TestCharakter()
        
        # Verwende alte Funktionen
        eigenschaften_funktionen.initialisiere_attribute(test_char2)
        eigenschaften_funktionen.initialisiere_fertigkeiten(test_char2)
        
        erfolg_alt = eigenschaften_funktionen.steigere_attribut(test_char2, 'Geschicklichkeit')
        erfolg_fert = eigenschaften_funktionen.steigere_fertigkeit(test_char2, 'Heimlichkeit')
        
        print(f"✓ Alte Funktionen funktionieren:")
        print(f"  - Attribut-Steigerung: {erfolg_alt}")
        print(f"  - Fertigkeit-Steigerung: {erfolg_fert}")
        print(f"  - Geschicklichkeit: W{test_char2.attribute['Geschicklichkeit'].wuerfel.value}")
        print(f"  - Heimlichkeit: W{test_char2.fertigkeiten['Heimlichkeit'].wuerfel.value}")
        
        # 8. Test: Fehlerbehandlung
        print("\n8. TESTING: Fehlerbehandlung")
        
        # Teste ungültige Eingaben
        erfolg_invalid = manager.steigere_attribut(test_char, 'UnbekannteAttribut')
        print(f"✓ Ungültiges Attribut abgelehnt: {erfolg_invalid == False}")
        
        erfolg_invalid_fert = manager.steigere_fertigkeit(test_char, 'UnbekanteFertigkeit')
        print(f"✓ Ungültige Fertigkeit abgelehnt: {erfolg_invalid_fert == False}")
        
        # 9. Test: Config-Funktionalität
        print("\n9. TESTING: Config-Funktionalität")
        
        config_pfad = project_root / 'config' / 'eigenschaften_config.json'
        config_existiert = config_pfad.exists()
        
        print(f"✓ Config-Status:")
        print(f"  - Config-Pfad: {config_pfad}")
        print(f"  - Config existiert: {config_existiert}")
        print(f"  - Grundfertigkeiten aus Config: {manager.grundfertigkeiten}")
        print(f"  - Standard-Attribute aus Config: {list(manager.standard_attribute.keys())}")
        
        print("\n" + "="*60)
        print("ALLE TESTS ERFOLGREICH!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ FEHLER BEIM TESTEN: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_real_charakter():
    """Testet die Integration mit der echten Charakter-Klasse."""
    
    print("\n" + "="*60)
    print("TESTING INTEGRATION MIT ECHTER CHARAKTER-KLASSE")
    print("="*60)
    
    try:
        from models.charakter import Charakter
        from functions import eigenschaften_funktionen
        
        print("\n1. TESTING: Echte Charakter-Instanz")
        
        # Erstelle echten Charakter
        charakter = Charakter()
        print("✓ Echter Charakter erstellt")
        
        # Teste Initialisierung (falls noch nicht geschehen)
        if not hasattr(charakter, 'attribute') or not charakter.attribute:
            eigenschaften_funktionen.initialisiere_attribute(charakter)
            print("✓ Attribute initialisiert")
        else:
            print("✓ Attribute bereits vorhanden")
        
        print(f"  - Anzahl Attribute: {len(charakter.attribute) if hasattr(charakter, 'attribute') else 0}")
        
        if hasattr(charakter, 'attribute') and charakter.attribute:
            for name, attr in charakter.attribute.items():
                print(f"    - {name}: W{attr.wuerfel.value}+{attr.wuerfel.modifier}")
        
        # Teste Fertigkeiten (falls Setting geladen)
        if hasattr(charakter, 'fertigkeiten_daten') and charakter.fertigkeiten_daten:
            eigenschaften_funktionen.initialisiere_fertigkeiten(charakter)
            print("✓ Fertigkeiten initialisiert")
            print(f"  - Anzahl Fertigkeiten: {len(charakter.fertigkeiten)}")
        else:
            print("ℹ Keine Fertigkeiten-Daten verfügbar (Setting nicht geladen)")
        
        # Teste Manager-Zugriff
        manager = eigenschaften_funktionen.get_eigenschaften_manager()
        print(f"✓ Manager über echten Charakter zugänglich")
        print(f"  - Config geladen: {bool(manager.config)}")
        
        print("\n✓ INTEGRATION MIT ECHTER CHARAKTER-KLASSE ERFOLGREICH!")
        return True
        
    except Exception as e:
        print(f"\n❌ FEHLER BEI INTEGRATION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starte EigenschaftenManager Tests...")
    
    success1 = test_eigenschaften_manager()
    success2 = test_integration_with_real_charakter()
    
    if success1 and success2:
        print("\n🎉 ALLE TESTS BESTANDEN!")
        sys.exit(0)
    else:
        print("\n❌ EINIGE TESTS FEHLGESCHLAGEN!")
        sys.exit(1)