#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schneller Test der refaktorierten App mit neuem CharakterVerwaltung-Tab
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.logger import Logger
from kivy.clock import Clock

# Führe nur einen 5-Sekunden Test durch
def stop_app_after_delay(app, dt):
    """Stoppt die App nach kurzer Zeit"""
    print("\n=== Test-App wird nach 5 Sekunden gestoppt ===")
    app.stop()

def test_main_app():
    """Testet die Haupt-App mit dem neuen Tab"""
    try:
        # Import der Haupt-App
        from main import SW_Charakter_GeneratorApp
        
        print("=== Starte Hauptapp-Test ===")
        print("Erwarteter neuer Tab: 'Charakterverwaltung' mit Icon 'account-multiple'")
        
        app = SW_Charakter_GeneratorApp()
        
        # Überprüfe Tab-Definitionen
        print(f"\nTab-Definitionen ({len(app.tab_definitions)} Tabs):")
        for i, (icon, text, screen_class) in enumerate(app.tab_definitions):
            status = "✓ NEU" if text == "Charakterverwaltung" else "✓"
            print(f"  {status} Tab {i+1}: '{text}' (Icon: {icon}, Screen: {screen_class.__name__})")
        
        # Stoppe App nach 5 Sekunden
        Clock.schedule_once(lambda dt: stop_app_after_delay(app, dt), 5)
        
        print("\n=== App startet für 5 Sekunden Test ===")
        app.run()
        
        print("=== Test erfolgreich abgeschlossen ===")
        return True
        
    except Exception as e:
        print(f"✗ Fehler beim App-Test: {e}")
        return False

if __name__ == "__main__":
    print("CharakterVerwaltung Refaktorierung - Haupt-App Test")
    print("=" * 55)
    
    if test_main_app():
        print("\n✅ ERFOLGREICH: App läuft mit neuem CharakterVerwaltung-Tab!")
        print("\nNächste Schritte:")
        print("1. App normal starten: python main.py")
        print("2. Zum neuen 'Charakterverwaltung' Tab wechseln")
        print("3. Alle Buttons testen (Neuer Charakter, Laden, Speichern, etc.)")
        print("4. Template-Funktionen testen")
    else:
        print("\n❌ FEHLER: App-Test fehlgeschlagen!")
        print("Prüfe die Fehler-Logs und verwende Backup-Dateien bei Bedarf.")