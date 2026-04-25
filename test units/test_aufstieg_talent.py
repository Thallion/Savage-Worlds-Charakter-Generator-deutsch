#!/usr/bin/env python3
"""
Test: Funktioniert 1 Aufstieg = 1 Talent nach char_gen_completed?
"""

import sys
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_aufstieg_talent():
    """Testet ob 1 Aufstieg = 1 Talent nach Charaktererstellung funktioniert."""

    try:
        print("🎯 TESTE: 1 Aufstieg = 1 Talent")
        print("=" * 50)

        # Charakter erstellen
        from functions.auto_character_generator import AutoCharacterGenerator
        gen = AutoCharacterGenerator()

        # Einfachen Charakter generieren
        print("📝 Generiere Basis-Charakter...")
        gen.generate_from_template('templates/Archetyp_SWAE_Bastlerin_Clementine.json')

        # Den letzten generierten Charakter aus dem Generator holen
        if not gen.generated_characters:
            print("❌ Kein Charakter wurde generiert!")
            return False

        charakter = gen.generated_characters[-1]  # Letzter generierter Charakter

        print(f"✅ Charakter geladen: {getattr(charakter, 'name', 'Clementine')}")
        print(f"📊 Aktueller Status:")
        print(f"   Rang: {charakter.rang}")
        print(f"   Aufstiege gesamt: {charakter.aufstiege_gesamt}")
        print(f"   Verbleibende Aufstiege: {charakter.verbleibende_aufstiege}")
        print(f"   char_gen_completed: {charakter.char_gen_completed}")

        # Sicherstellen dass char_gen_completed = True
        if not charakter.char_gen_completed:
            charakter.char_gen_completed = True
            print("🔧 char_gen_completed auf True gesetzt")

        # Aufstiege hinzufügen für Test
        charakter.aufstiege_gesamt += 2
        charakter.verbleibende_aufstiege += 2
        print(f"⚡ 2 Test-Aufstiege hinzugefügt")
        print(f"   Aufstiege gesamt: {charakter.aufstiege_gesamt}")
        print(f"   Verbleibende Aufstiege: {charakter.verbleibende_aufstiege}")

        # Anzahl Talente vor dem Test
        talente_vorher = sum(1 for talent in charakter.talente.values()
                           if getattr(talent, 'ausgewaehlt', False))
        print(f"🎭 Talente vorher: {talente_vorher}")

        # Talent mit Aufstieg kaufen
        print("\n🛒 KAUFE TALENT MIT AUFSTIEG...")
        from functions.talent_funktionen import get_talent_manager

        talent_manager = get_talent_manager(charakter)

        # Ein Talent wählen das noch nicht ausgewählt ist
        verfuegbare_talente = [name for name, talent in charakter.talente.items()
                              if not getattr(talent, 'ausgewaehlt', False)]

        if not verfuegbare_talente:
            print("❌ Keine verfügbaren Talente gefunden!")
            return False

        test_talent = verfuegbare_talente[0]
        print(f"🎯 Wähle Talent: {test_talent}")

        aufstiege_vorher = charakter.verbleibende_aufstiege

        # Talent kaufen
        result = talent_manager.waehle_talent(test_talent)

        aufstiege_nachher = charakter.verbleibende_aufstiege
        aufstiege_verbraucht = aufstiege_vorher - aufstiege_nachher

        print(f"\n📊 ERGEBNIS:")
        print(f"   Talent gekauft: {result}")
        print(f"   Aufstiege vorher: {aufstiege_vorher}")
        print(f"   Aufstiege nachher: {aufstiege_nachher}")
        print(f"   Aufstiege verbraucht: {aufstiege_verbraucht}")

        # Prüfen ob Talent ausgewählt wurde
        talent_obj = charakter.talente[test_talent]
        talent_ausgewaehlt = getattr(talent_obj, 'ausgewaehlt', False)
        print(f"   Talent ausgewählt: {talent_ausgewaehlt}")

        # Erfolg prüfen
        if result and talent_ausgewaehlt and aufstiege_verbraucht == 1:
            print("\n✅ TEST ERFOLGREICH!")
            print("   ✅ Talent wurde gekauft")
            print("   ✅ Genau 1 Aufstieg wurde verbraucht")
            print("   ✅ 1 Aufstieg = 1 Talent funktioniert korrekt!")
            return True
        else:
            print("\n❌ TEST FEHLGESCHLAGEN!")
            if not result:
                print("   ❌ waehle_talent() gab False zurück")
            if not talent_ausgewaehlt:
                print("   ❌ Talent wurde nicht als ausgewählt markiert")
            if aufstiege_verbraucht != 1:
                print(f"   ❌ Falsche Anzahl Aufstiege verbraucht: {aufstiege_verbraucht} statt 1")
            return False

    except Exception as e:
        print(f"❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_aufstieg_talent()
    sys.exit(0 if success else 1)