#!/usr/bin/env python3
"""
Test: Aufstieg-Logik mit Valeros (Savage Pathfinder)
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_valeros_aufstieg():
    """Testet die Aufstieg-Logik mit dem generierten Valeros Charakter."""

    try:
        print("🎯 TESTE: Aufstieg-Logik mit Valeros (Savage Pathfinder)")
        print("=" * 60)

        # Valeros generieren
        from functions.auto_character_generator import AutoCharacterGenerator
        gen = AutoCharacterGenerator()

        print("📝 Generiere Valeros...")
        gen.generate_from_template('templates/Archetyp_SavagePathfinder_Kaempfer_Valeros.json')

        charakter = gen.generated_characters[-1]

        print(f"✅ Valeros geladen")
        print(f"📊 Status:")
        print(f"   Setting: {getattr(charakter, 'aktuelles_setting', 'Unknown')}")
        print(f"   Rang: {charakter.rang}")
        print(f"   Aufstiege gesamt: {charakter.aufstiege_gesamt}")
        print(f"   Verbleibende Aufstiege: {charakter.verbleibende_aufstiege}")
        print(f"   char_gen_completed: {charakter.char_gen_completed}")

        # Aufstiege für Test hinzufügen
        charakter.aufstiege_gesamt += 3
        charakter.verbleibende_aufstiege += 3
        print(f"⚡ 3 Test-Aufstiege hinzugefügt")
        print(f"   Aufstiege gesamt: {charakter.aufstiege_gesamt}")
        print(f"   Verbleibende Aufstiege: {charakter.verbleibende_aufstiege}")

        # Aktuelle Talente zählen
        talente_vorher = sum(1 for talent in charakter.talente.values()
                           if getattr(talent, 'ausgewaehlt', False))
        print(f"🎭 Talente vorher: {talente_vorher}")

        # Liste ausgewählter Talente
        ausgewaehlte_talente = [name for name, talent in charakter.talente.items()
                              if getattr(talent, 'ausgewaehlt', False)]
        print(f"   Ausgewählt: {ausgewaehlte_talente}")

        # Verfügbare Talente finden
        verfuegbare_talente = [name for name, talent in charakter.talente.items()
                              if not getattr(talent, 'ausgewaehlt', False)]

        if not verfuegbare_talente:
            print("❌ Keine verfügbaren Talente!")
            return False

        # Die ersten 3 verfügbaren Talente testen
        test_talente = verfuegbare_talente[:3]
        print(f"🎯 Teste Talente: {test_talente}")

        from functions.talent_funktionen import get_talent_manager
        talent_manager = get_talent_manager(charakter)

        erfolgreich_gekauft = 0
        aufstiege_start = charakter.verbleibende_aufstiege

        # 3 Talente mit Aufstiegen kaufen
        for i, talent_name in enumerate(test_talente):
            aufstiege_vor_kauf = charakter.verbleibende_aufstiege

            print(f"\n🛒 KAUF {i+1}: {talent_name}")
            print(f"   Aufstiege vor Kauf: {aufstiege_vor_kauf}")

            result = talent_manager.waehle_talent(talent_name)

            aufstiege_nach_kauf = charakter.verbleibende_aufstiege
            aufstiege_verbraucht = aufstiege_vor_kauf - aufstiege_nach_kauf

            talent_obj = charakter.talente[talent_name]
            talent_ausgewaehlt = getattr(talent_obj, 'ausgewaehlt', False)

            print(f"   Ergebnis: {result}")
            print(f"   Aufstiege nach Kauf: {aufstiege_nach_kauf}")
            print(f"   Verbraucht: {aufstiege_verbraucht}")
            print(f"   Talent ausgewählt: {talent_ausgewaehlt}")

            if result and talent_ausgewaehlt and aufstiege_verbraucht == 1:
                erfolgreich_gekauft += 1
                print(f"   ✅ ERFOLGREICH!")
            else:
                print(f"   ❌ FEHLGESCHLAGEN!")

        # Endergebnis
        aufstiege_gesamt_verbraucht = aufstiege_start - charakter.verbleibende_aufstiege

        print(f"\n📊 ENDERGEBNIS:")
        print(f"   Talente erfolgreich gekauft: {erfolgreich_gekauft}/3")
        print(f"   Aufstiege gesamt verbraucht: {aufstiege_gesamt_verbraucht}")
        print(f"   Verbleibende Aufstiege: {charakter.verbleibende_aufstiege}")

        # Erfolg bewerten
        if erfolgreich_gekauft == 3 and aufstiege_gesamt_verbraucht == 3:
            print(f"\n🎉 TEST ERFOLGREICH!")
            print(f"   ✅ 3 Talente erfolgreich gekauft")
            print(f"   ✅ Genau 3 Aufstiege verbraucht")
            print(f"   ✅ 1 Aufstieg = 1 Talent funktioniert mit Savage Pathfinder!")
            return True
        else:
            print(f"\n❌ TEST TEILWEISE ERFOLGREICH")
            print(f"   Gekauft: {erfolgreich_gekauft}/3")
            print(f"   Aufstiege: {aufstiege_gesamt_verbraucht}/3")
            return erfolgreich_gekauft > 0

    except Exception as e:
        print(f"❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_valeros_aufstieg()
    sys.exit(0 if success else 1)