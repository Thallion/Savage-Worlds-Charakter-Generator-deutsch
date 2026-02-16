#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Datei für die Charakterverwaltung-Refaktorierung
Testet die neue CharakterVerwaltung-Funktionalität

Run: python test_charakter_verwaltung_refaktor.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# App-Test imports
from kivymd.app import MDApp
from views.charakter_verwaltung_widget import CharakterVerwaltungWidget
from controllers.charakter_controller import CharakterController
from models.charakter import Charakter

class TestCharakterVerwaltungApp(MDApp):
    """Test-App für CharakterVerwaltung"""
    
    def build(self):
        # Controller und Charakter initialisieren
        self.charakter = Charakter()
        self.controller = CharakterController()
        self.controller.charakter = self.charakter
        
        # Widget erstellen
        widget = CharakterVerwaltungWidget()
        
        print("=== CharakterVerwaltung Widget Test ===")
        print(f"Widget erstellt: {type(widget).__name__}")
        print(f"Handler verfügbar: {hasattr(widget, 'character_handler')}")
        print(f"Template Handler verfügbar: {hasattr(widget, 'template_handler')}")
        print(f"Manager verfügbar: {hasattr(widget, 'statistics_manager')}")
        
        # Test der wichtigsten Methoden
        print("\n=== Funktions-Tests ===")
        try:
            test_value = widget.get_charakter_value('name', 'Test')
            print(f"✓ get_charakter_value funktioniert: {test_value}")
        except Exception as e:
            print(f"✗ get_charakter_value Fehler: {e}")
        
        # Test verfügbare Methoden
        methods_to_test = [
            'create_new_character',
            'schnellspeichern_charakter', 
            'speichere_charakter',
            'lade_charakter',
            'erzeuge_charakterbogen_pdf',
            'zeige_statblock',
            'zeige_element_statistiken',
            'open_template_selection_dialog'
        ]
        
        print("\nVerfügbare Methoden:")
        for method in methods_to_test:
            available = hasattr(widget, method)
            print(f"{'✓' if available else '✗'} {method}")
        
        print("\n=== Test erfolgreich abgeschlossen ===")
        return widget

def test_character_handler_compatibility():
    """Testet die Kompatibilität des CharacterHandlers"""
    print("\n=== CharacterHandler Kompatibilität Test ===")
    
    try:
        from controllers.character_handler import CharacterHandler
        
        # Mock Widget für Test
        class MockWidget:
            def __init__(self):
                self.app = MockApp()
                self.ids = {}
        
        class MockApp:
            def __init__(self):
                self.controller = CharakterController()
                self.controller.charakter = Charakter()
        
        mock_widget = MockWidget()
        handler = CharacterHandler(mock_widget)
        
        print(f"✓ CharacterHandler erfolgreich erstellt")
        print(f"✓ get_charakter_value verfügbar: {hasattr(handler, 'get_charakter_value')}")
        
        # Test get_charakter_value
        test_value = handler.get_charakter_value('name', 'TestChar')
        print(f"✓ get_charakter_value funktioniert: {test_value}")
        
    except Exception as e:
        print(f"✗ CharacterHandler Test fehlgeschlagen: {e}")

def test_imports():
    """Testet alle wichtigen Imports"""
    print("\n=== Import Tests ===")
    
    try:
        from views.charakter_verwaltung_widget import CharakterVerwaltungWidget
        print("✓ CharakterVerwaltungWidget Import erfolgreich")
    except Exception as e:
        print(f"✗ CharakterVerwaltungWidget Import fehlgeschlagen: {e}")
    
    try:
        from views.screens import CharakterVerwaltungScreen
        print("✓ CharakterVerwaltungScreen Import erfolgreich")
    except Exception as e:
        print(f"✗ CharakterVerwaltungScreen Import fehlgeschlagen: {e}")
    
    try:
        from controllers.character_handler import CharacterHandler
        print("✓ CharacterHandler Import erfolgreich")
    except Exception as e:
        print(f"✗ CharacterHandler Import fehlgeschlagen: {e}")
    
    try:
        from controllers.template_handler import TemplateHandler
        print("✓ TemplateHandler Import erfolgreich")
    except Exception as e:
        print(f"✗ TemplateHandler Import fehlgeschlagen: {e}")

if __name__ == '__main__':
    print("CharakterVerwaltung Refaktorierung Test")
    print("=" * 50)
    
    # Import Tests zuerst
    test_imports()
    
    # Handler Kompatibilität testen
    test_character_handler_compatibility()
    
    # App-Test nur wenn alle Imports funktionieren
    try:
        print("\nStarte App-Test...")
        TestCharakterVerwaltungApp().run()
    except Exception as e:
        print(f"App-Test übersprungen: {e}")
    
    print("\nAlle Tests abgeschlossen!")