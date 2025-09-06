#!/usr/bin/env python3
"""
Test um zu prüfen ob der Kauf wirklich stattfindet bei unzureichendem Vermögen
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_vermoegensbuchungen():
    print("🔍 Test: Vermögensbuchungen bei Käufen")
    print("=" * 50)
    
    print("Starte die App und teste folgende Schritte:")
    print("1. Notiere das aktuelle Vermögen des Charakters")
    print("2. Versuche etwas zu kaufen, was teurer ist als das Vermögen")
    print("3. Prüfe ob:")
    print("   a) Eine Fehlermeldung angezeigt wird")
    print("   b) Das Vermögen UNVERÄNDERT bleibt") 
    print("   c) Das Item NICHT zur Ausrüstung hinzugefügt wird")
    print()
    print("Wenn alle 3 Punkte erfüllt sind, funktioniert der Code korrekt!")
    print("Wenn das Vermögen sinkt oder das Item hinzugefügt wird, gibt es einen Bug.")
    print()
    print("Erwartetes Verhalten bei unzureichendem Vermögen:")
    print("✅ Fehlermeldung wird angezeigt")
    print("✅ Vermögen bleibt unverändert")
    print("✅ Item wird NICHT zur Ausrüstung hinzugefügt")
    print("✅ Kauf-Dialog wird NICHT geschlossen")
    print()
    print("Mögliche Ursachen für deine Beobachtung:")
    print("1. Du siehst die Log-Warning im Hintergrund")
    print("2. Du interpretierst den UI-Fehlerdialog als 'Kauf findet statt'")
    print("3. Es gibt einen anderen Bug in der UI-Anzeige")
    print("4. Das Vermögen wird korrekt reduziert, aber falsch angezeigt")

if __name__ == "__main__":
    test_vermoegensbuchungen()