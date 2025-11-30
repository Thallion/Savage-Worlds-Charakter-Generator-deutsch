#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup und Test Script für die Charakterverwaltung-Refaktorierung
Erstellt automatische Backups und führt Tests durch
"""

import os
import shutil
import datetime
import sys

def create_backup():
    """Erstellt Backup-Ordner mit allen wichtigen Dateien"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_refaktor_{timestamp}"
    
    print(f"Erstelle Backup in: {backup_dir}")
    
    # Backup-Ordner erstellen
    os.makedirs(backup_dir, exist_ok=True)
    
    # Wichtige Dateien für Backup
    files_to_backup = [
        "main.py.backup",
        "views/einstellungen_widget.py.backup",
        "main.kv",
        "views/einstellungen_widget.kv",
        "views/screens.py",
        "controllers/character_handler.py",
        "controllers/template_handler.py"
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            dest_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, dest_path)
            print(f"✓ Backup erstellt: {file_path}")
        else:
            print(f"⚠ Datei nicht gefunden: {file_path}")
    
    # README für Backup erstellen
    readme_content = f"""
# Backup der Charakterverwaltung-Refaktorierung
Erstellt am: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Was wurde refaktoriert:
1. CharakterVerwaltungWidget aus EinstellungenWidget ausgegliedert
2. Neuer Tab "Charakterverwaltung" mit Icon "account-multiple"
3. CharakterVerwaltungScreen in screens.py hinzugefügt
4. main.py um neuen Tab erweitert
5. Charakterverwaltungs-Funktionen aus EinstellungenWidget entfernt

## Betroffene Dateien:
- main.py: Neuer Tab hinzugefügt
- main.kv: CharakterVerwaltungScreen hinzugefügt
- views/charakter_verwaltung_widget.py: NEUE DATEI
- views/charakter_verwaltung_widget.kv: NEUE DATEI
- views/screens.py: CharakterVerwaltungScreen hinzugefügt
- views/einstellungen_widget.py: Charakterverwaltungs-Funktionen entfernt
- views/einstellungen_widget.kv: Charakterverwaltungs-UI entfernt

## Neue Funktionen:
- create_new_character
- schnellspeichern_charakter  
- speichere_charakter
- lade_charakter
- erzeuge_charakterbogen_pdf
- zeige_statblock
- zeige_element_statistiken
- Template-Management

## Rückgängig machen:
1. Backup-Dateien zurückkopieren
2. views/charakter_verwaltung_widget.* löschen
3. CharakterVerwaltungScreen aus screens.py entfernen
4. Tab aus main.py entfernen
"""
    
    with open(os.path.join(backup_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"✓ Backup erfolgreich erstellt in: {backup_dir}")
    return backup_dir

def run_tests():
    """Führt Tests für die Refaktorierung durch"""
    print("\n=== Führe Tests durch ===")
    
    # Test 1: Alle neuen Dateien vorhanden
    required_files = [
        "views/charakter_verwaltung_widget.py",
        "views/charakter_verwaltung_widget.kv"
    ]
    
    print("\nTest 1: Neue Dateien vorhanden")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} FEHLT!")
    
    # Test 2: Import-Tests
    print("\nTest 2: Import Tests")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from views.charakter_verwaltung_widget import CharakterVerwaltungWidget
        print("✓ CharakterVerwaltungWidget Import")
        
        from views.screens import CharakterVerwaltungScreen
        print("✓ CharakterVerwaltungScreen Import")
        
    except Exception as e:
        print(f"✗ Import Fehler: {e}")
    
    # Test 3: KV-Datei Syntax
    print("\nTest 3: KV-Datei Syntax")
    try:
        from kivy.lang import Builder
        Builder.load_file("views/charakter_verwaltung_widget.kv")
        print("✓ charakter_verwaltung_widget.kv Syntax OK")
    except Exception as e:
        print(f"✗ KV-Syntax Fehler: {e}")
    
    # Test 4: Widget erstellen
    print("\nTest 4: Widget Erstellung")
    try:
        widget = CharakterVerwaltungWidget()
        print("✓ CharakterVerwaltungWidget erfolgreich erstellt")
        
        # Test wichtige Methoden
        methods = ['create_new_character', 'speichere_charakter', 'lade_charakter']
        for method in methods:
            if hasattr(widget, method):
                print(f"✓ Methode {method} verfügbar")
            else:
                print(f"✗ Methode {method} FEHLT!")
                
    except Exception as e:
        print(f"✗ Widget Erstellung fehlgeschlagen: {e}")

def check_main_files():
    """Überprüft ob main.py und main.kv korrekt aktualisiert wurden"""
    print("\n=== Überprüfe main.py und main.kv ===")
    
    # Check main.py
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            main_content = f.read()
        
        if "CharakterVerwaltungScreen" in main_content:
            print("✓ CharakterVerwaltungScreen in main.py importiert")
        else:
            print("✗ CharakterVerwaltungScreen NICHT in main.py importiert")
        
        if "account-multiple" in main_content:
            print("✓ account-multiple Icon in main.py definiert")
        else:
            print("✗ account-multiple Icon NICHT in main.py definiert")
            
    except Exception as e:
        print(f"✗ main.py Überprüfung fehlgeschlagen: {e}")
    
    # Check main.kv  
    try:
        with open("main.kv", "r", encoding="utf-8") as f:
            kv_content = f.read()
        
        if "<CharakterVerwaltungScreen>" in kv_content:
            print("✓ CharakterVerwaltungScreen in main.kv definiert")
        else:
            print("✗ CharakterVerwaltungScreen NICHT in main.kv definiert")
            
    except Exception as e:
        print(f"✗ main.kv Überprüfung fehlgeschlagen: {e}")

if __name__ == "__main__":
    print("Charakterverwaltung Refaktorierung - Backup und Test")
    print("=" * 60)
    
    # Backup erstellen
    backup_dir = create_backup()
    
    # Tests durchführen
    run_tests()
    
    # Haupt-Dateien überprüfen
    check_main_files()
    
    print(f"\n=== Zusammenfassung ===")
    print(f"Backup erstellt in: {backup_dir}")
    print("Tests abgeschlossen!")
    print("\nNächste Schritte:")
    print("1. App starten und neuen 'Charakterverwaltung' Tab testen")
    print("2. Alle Charakterverwaltungs-Funktionen testen")
    print("3. Bei Problemen: Backup-Dateien zurückkopieren")