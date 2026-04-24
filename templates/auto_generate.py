#!/usr/bin/env python3
"""
Auto Character Generator Test Script
Generiert den Archetyp "Bastlerin Clementine" aus dem Template.
"""

import sys
import os
from pathlib import Path

def main():
    """Hauptfunktion zum Generieren des Charakters."""
    try:
        # Import der AutoCharacterGenerator Klasse
        from functions.auto_character_generator import AutoCharacterGenerator

        # Template-Pfad
        template_path = 'Archetyp_SWAE_Bastlerin_Clementine.json'

        # Prüfen ob Template existiert
        if not os.path.exists(template_path):
            print(f"❌ Template-Datei nicht gefunden: {template_path}")
            return 1

        print("🎯 Starte Charaktergenerierung...")
        print(f"📄 Template: {template_path}")
        print("=" * 80)

        # Generator instanziieren und ausführen
        generator = AutoCharacterGenerator()
        generator.generate_from_template(template_path)

        print("=" * 80)
        print("✅ Charaktergenerierung erfolgreich abgeschlossen!")

        # Zeige wo die Datei gespeichert wurde
        chars_dir = Path("../chars/auto_generated")
        if chars_dir.exists():
            clementine_dirs = list(chars_dir.glob("*Clementine*"))
            if clementine_dirs:
                latest_dir = max(clementine_dirs, key=os.path.getctime)
                json_files = list(latest_dir.glob("*.json"))
                if json_files:
                    latest_file = max(json_files, key=os.path.getctime)
                    print(f"💾 Charakter gespeichert: {latest_file}")

        return 0

    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("💡 Stelle sicher, dass du im richtigen Verzeichnis bist und alle Dependencies installiert sind.")
        return 1

    except FileNotFoundError as e:
        print(f"❌ Datei nicht gefunden: {e}")
        return 1

    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)