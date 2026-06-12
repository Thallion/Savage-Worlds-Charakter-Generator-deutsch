"""
Charakterisierungstests für functions/abgeleitete_werte.py

Diese Tests schreiben das IST-Verhalten der abgeleiteten-Werte-Berechnung fest
(Parade, Bewegungsweite, Größe/Robustheit, Bennys, Traglast) und dienen als
Sicherheitsnetz für das Refactoring auf die datengetriebene Effekt-Registry.

Wichtige festgeschriebene Semantik:
- Block + Harter Block sind ADDITIV (zusammen +2 Parade)
- Lieblingswaffe / Absolute Lieblingswaffe sind ALTERNATIV (zusammen nur +2)
- Behände / Flink sind ALTERNATIV (zusammen nur +2 Bewegungsweite)
- Kämpferische Disziplin wirkt nur ohne getragene Rüstung (Torso == 0)
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Pfad zur Projektroot hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.abgeleitete_werte import berechne_abgeleitete_werte


class FakeFertigkeit:
    """Minimale Fertigkeit mit .wert"""
    def __init__(self, wert):
        self.wert = wert


class FakeAttribut:
    """Minimales Attribut mit .wert"""
    def __init__(self, wert):
        self.wert = wert


class FakeHandicap:
    """Minimales Handicap mit .name und .stufe"""
    def __init__(self, name, stufe="leicht"):
        self.name = name
        self.stufe = stufe


class FakeCharakter:
    """Leichter Charakter-Ersatz ohne Kivy-Properties"""
    def __init__(self):
        self.machtpunkte = 0
        self.erschoepfung = 0
        self.vermoegen = 500
        self.waehrungseinheit = "$"
        self.fertigkeiten = {}
        self.attribute = {
            'Stärke': FakeAttribut(4),
            'Konstitution': FakeAttribut(4),
        }
        self.selected_talente = []
        self.selected_handicaps = []
        self.handicaps = {}
        self.voelker = {}
        self.voelker_selected = {}
        self.active_setting_name = 'SWAE'
        self.gesamtgewicht = 0

    def add_handicap(self, name, stufe="leicht"):
        """Handicap anlegen UND auswählen (wie im echten Modell über Key)"""
        self.handicaps[name] = FakeHandicap(name, stufe)
        self.selected_handicaps.append(name)


def mock_volk(bewegungsweite_bonus=0, robustheit_bonus=0,
              groesse_modifikator=0, effects=None):
    """Erzeugt ein Mock-Volk mit der vom Code erwarteten Schnittstelle"""
    volk = Mock()
    volk.name = 'Testvolk'
    volk.get_bewegungsweite_bonus.return_value = bewegungsweite_bonus
    volk.get_robustheit_bonus.return_value = robustheit_bonus
    volk.get_groesse_modifikator.return_value = groesse_modifikator
    volk.effects = effects if effects is not None else {}
    return volk


class TestAbgeleiteteWerte(unittest.TestCase):
    """Charakterisierungstests für berechne_abgeleitete_werte()"""

    def berechne(self, charakter, torso=0):
        """
        Führt die Berechnung mit gepatchten funktionslokalen Importen aus.
        WICHTIG: berechne_gesamt_ruestungsschutz und ist_cyberware_setting
        werden funktionslokal importiert, daher Patch im QUELLmodul.
        """
        with patch('functions.abgeleitete_werte.Logger'), \
             patch('functions.ausruestung_funktionen.berechne_gesamt_ruestungsschutz',
                   return_value={'Torso': torso}) as self.mock_ruestungsschutz, \
             patch('functions.cyberware_funktionen.ist_cyberware_setting',
                   return_value=False) as self.mock_cyberware_check:
            return berechne_abgeleitete_werte(charakter)

    # === PATCH-WIRKSAMKEIT ===

    def test_patches_greifen(self):
        """Negativtest: die funktionslokalen Patches werden wirklich benutzt"""
        charakter = FakeCharakter()
        werte = self.berechne(charakter)
        self.assertNotEqual(werte, {})
        self.mock_ruestungsschutz.assert_called_once_with(charakter)
        self.mock_cyberware_check.assert_called()

    # === PARADE ===

    def test_parade_basis_ohne_kaempfen(self):
        """Ohne Kämpfen-Fertigkeit: Standardwert 4 → Parade 2 + 4//2 = 4"""
        charakter = FakeCharakter()
        werte = self.berechne(charakter)
        self.assertEqual(werte['Parade'], 4)
        self.assertEqual(charakter.parade, 4)

    def test_parade_basis_mit_kaempfen_w6(self):
        """Kämpfen W6 → Parade 2 + 6//2 = 5"""
        charakter = FakeCharakter()
        charakter.fertigkeiten['Kämpfen'] = FakeFertigkeit(6)
        werte = self.berechne(charakter)
        self.assertEqual(werte['Parade'], 5)

    def test_parade_einzeltalente(self):
        """Jedes Parade-Talent einzeln: erwarteter Bonus"""
        erwartete_boni = {
            "Block": 1,
            "Harter Block": 1,
            "Meister aller Waffen": 1,
            "Waffenmeister": 1,
            "Herdritter": 1,
            "Lieblingswaffe": 1,
            "Absolute Lieblingswaffe": 2,
        }
        for talent, bonus in erwartete_boni.items():
            with self.subTest(talent=talent):
                charakter = FakeCharakter()
                charakter.selected_talente = [talent]
                werte = self.berechne(charakter)
                self.assertEqual(werte['Parade'], 4 + bonus)

    def test_parade_block_und_harter_block_additiv(self):
        """Block + Harter Block sind ADDITIV: +2 (Ist-Verhalten)"""
        charakter = FakeCharakter()
        charakter.selected_talente = ["Block", "Harter Block"]
        werte = self.berechne(charakter)
        self.assertEqual(werte['Parade'], 6)

    def test_parade_lieblingswaffe_nicht_kumulativ(self):
        """Lieblingswaffe + Absolute Lieblingswaffe: nur +2 (elif, nicht +3)"""
        charakter = FakeCharakter()
        charakter.selected_talente = ["Lieblingswaffe", "Absolute Lieblingswaffe"]
        werte = self.berechne(charakter)
        self.assertEqual(werte['Parade'], 6)

    # === BEWEGUNGSWEITE ===

    def test_bewegungsweite_standard(self):
        """Ohne Modifikatoren: 6"""
        charakter = FakeCharakter()
        werte = self.berechne(charakter)
        self.assertEqual(werte['Bewegungsweite'], 6)
        self.assertEqual(charakter.bewegungsweite, 6)

    def test_bewegungsweite_handicaps(self):
        """Handicap-Mali: Langsam leicht/schwer, Fettleibig leicht, Alt schwer"""
        faelle = [
            ("Langsam", "leicht", 5),
            ("Langsam", "schwer", 4),
            ("Fettleibig", "leicht", 5),
            ("Alt", "schwer", 5),
            ("Alt", "leicht", 6),  # Alt (leicht) hat KEINEN Bewegungsweite-Effekt
        ]
        for name, stufe, erwartet in faelle:
            with self.subTest(handicap=name, stufe=stufe):
                charakter = FakeCharakter()
                charakter.add_handicap(name, stufe)
                werte = self.berechne(charakter)
                self.assertEqual(werte['Bewegungsweite'], erwartet)

    def test_bewegungsweite_behaende_flink_nicht_kumulativ(self):
        """Behände ODER Flink: +2; beide zusammen ebenfalls nur +2"""
        for talente in (["Behände"], ["Flink"], ["Behände", "Flink"]):
            with self.subTest(talente=talente):
                charakter = FakeCharakter()
                charakter.selected_talente = list(talente)
                werte = self.berechne(charakter)
                self.assertEqual(werte['Bewegungsweite'], 8)

    def test_bewegungsweite_minimum_eins(self):
        """Bewegungsweite fällt nie unter 1"""
        charakter = FakeCharakter()
        volk = mock_volk(bewegungsweite_bonus=-10)
        charakter.voelker = {'Testvolk': volk}
        charakter.voelker_selected = {'Testvolk': True}
        werte = self.berechne(charakter)
        self.assertEqual(werte['Bewegungsweite'], 1)

    def test_bewegungsweite_volk_bonus(self):
        """Volk-Bonus +1 → 7"""
        charakter = FakeCharakter()
        volk = mock_volk(bewegungsweite_bonus=1)
        charakter.voelker = {'Testvolk': volk}
        charakter.voelker_selected = {'Testvolk': True}
        werte = self.berechne(charakter)
        self.assertEqual(werte['Bewegungsweite'], 7)

    # === GRÖSSE / ROBUSTHEIT ===

    def test_robustheit_basis_nach_konstitution(self):
        """Robustheit-Basis = (KON // 2) + 2"""
        for kon_wert, erwartet in ((4, 4), (6, 5), (8, 6), (12, 8)):
            with self.subTest(konstitution=kon_wert):
                charakter = FakeCharakter()
                charakter.attribute['Konstitution'] = FakeAttribut(kon_wert)
                werte = self.berechne(charakter)
                self.assertEqual(charakter.robustheit_basis, erwartet)

    def test_robustheit_talente(self):
        """Robustheit-/Größe-Talente einzeln (Basis KON W4 = 4)"""
        faelle = [
            ("Kräftig", 5, 1),                                # +1 Größe
            ("Raufbold", 5, 0),                               # +1 Robustheit
            ("Schläger", 5, 0),
            ("Jünger Erthas", 5, 0),
            ("AH (Zauberer) Abnorme Blutlinie", 5, 0),
            ("AH (Zauberer) Dämonische Blutlinie", 5, 0),
            ("AH (Zauberer) Drachenblutlinie", 6, 0),         # +2
        ]
        for talent, erwartete_robustheit, erwartete_groesse in faelle:
            with self.subTest(talent=talent):
                charakter = FakeCharakter()
                charakter.selected_talente = [talent]
                werte = self.berechne(charakter)
                self.assertEqual(charakter.robustheit_basis, erwartete_robustheit)
                self.assertEqual(werte['Größe'], erwartete_groesse)

    def test_robustheit_handicaps(self):
        """Fettleibig leicht: +1 Robustheit UND -1 Bewegungsweite; Klein/Schlank"""
        charakter = FakeCharakter()
        charakter.add_handicap("Fettleibig", "leicht")
        werte = self.berechne(charakter)
        self.assertEqual(charakter.robustheit_basis, 5)
        self.assertEqual(werte['Bewegungsweite'], 5)

        charakter = FakeCharakter()
        charakter.add_handicap("Klein", "leicht")
        werte = self.berechne(charakter)
        self.assertEqual(werte['Größe'], -1)
        self.assertEqual(charakter.robustheit_basis, 3)

        # Schlank wirkt stufenunabhängig
        for stufe in ("leicht", "schwer"):
            charakter = FakeCharakter()
            charakter.add_handicap("Schlank", stufe)
            self.berechne(charakter)
            self.assertEqual(charakter.robustheit_basis, 3)

    def test_kaempferische_disziplin_nur_ohne_ruestung(self):
        """Kämpferische Disziplin: +1 Robustheit nur bei Torso == 0"""
        charakter = FakeCharakter()
        charakter.selected_talente = ["Kämpferische Disziplin"]
        self.berechne(charakter, torso=0)
        self.assertEqual(charakter.robustheit_basis, 5)

        charakter = FakeCharakter()
        charakter.selected_talente = ["Kämpferische Disziplin"]
        self.berechne(charakter, torso=2)
        self.assertEqual(charakter.robustheit_basis, 4)
        # Gesamt-Robustheit enthält die Rüstung
        self.assertEqual(charakter.robustheit, 6)
        self.assertEqual(charakter.robustheit_mit_ruestung, "6 (2)")

    def test_robustheit_volk_effekte(self):
        """Volk: Größe-Modifikator und Robustheit-Bonus getrennt addiert"""
        charakter = FakeCharakter()
        volk = mock_volk(robustheit_bonus=1, groesse_modifikator=-1)
        charakter.voelker = {'Testvolk': volk}
        charakter.voelker_selected = {'Testvolk': True}
        werte = self.berechne(charakter)
        self.assertEqual(werte['Größe'], -1)
        # (4//2)+2 + (-1) + 1 = 4
        self.assertEqual(charakter.robustheit_basis, 4)

    # === BENNYS ===

    def test_bennys(self):
        """Basis 3; Glück +1, Großes Glück +1, beide +2; Jung leicht/schwer"""
        charakter = FakeCharakter()
        self.assertEqual(self.berechne(charakter)['Bennys'], 3)

        charakter = FakeCharakter()
        charakter.selected_talente = ["Glück"]
        self.assertEqual(self.berechne(charakter)['Bennys'], 4)

        charakter = FakeCharakter()
        charakter.selected_talente = ["Großes Glück"]
        self.assertEqual(self.berechne(charakter)['Bennys'], 4)

        charakter = FakeCharakter()
        charakter.selected_talente = ["Glück", "Großes Glück"]
        self.assertEqual(self.berechne(charakter)['Bennys'], 5)

        charakter = FakeCharakter()
        charakter.add_handicap("Jung", "leicht")
        self.assertEqual(self.berechne(charakter)['Bennys'], 4)

        charakter = FakeCharakter()
        charakter.add_handicap("Jung", "schwer")
        self.assertEqual(self.berechne(charakter)['Bennys'], 5)

    def test_bennys_volk_auto_talent_glueck(self):
        """Volk mit auto_talente ['Glück'] gibt +1 Benny"""
        charakter = FakeCharakter()
        volk = mock_volk(effects={'auto_talente': ['Glück']})
        charakter.voelker = {'Testvolk': volk}
        charakter.voelker_selected = {'Testvolk': True}
        self.assertEqual(self.berechne(charakter)['Bennys'], 4)

    # === TRAGLAST ===

    def test_traglast(self):
        """Traglast = Stärke × 10; Kräftig +20 (echte berechne_traglast)"""
        charakter = FakeCharakter()
        self.assertEqual(self.berechne(charakter)['Maximale Traglast'], 40)

        charakter = FakeCharakter()
        charakter.attribute['Stärke'] = FakeAttribut(8)
        self.assertEqual(self.berechne(charakter)['Maximale Traglast'], 80)

        charakter = FakeCharakter()
        charakter.selected_talente = ["Kräftig"]
        self.assertEqual(self.berechne(charakter)['Maximale Traglast'], 60)

    # === ERGEBNIS-STRUKTUR UND FEHLERPFAD ===

    def test_ergebnis_enthaelt_alle_schluessel(self):
        """Das Ergebnis-Dict enthält alle erwarteten Schlüssel"""
        charakter = FakeCharakter()
        werte = self.berechne(charakter)
        erwartete_schluessel = {
            'Bewegungsweite', 'Parade', 'Größe', 'Robustheit', 'Machtpunkte',
            'Wunden', 'Erschöpfung', 'Bennys', 'Entschlossenheit',
            'Maximale Traglast', 'Gesamtgewicht',
        }
        self.assertEqual(set(werte.keys()), erwartete_schluessel)

    def test_fehlerpfad_liefert_leeres_dict(self):
        """Interner Fehler → Rückgabe {} (Ist-Verhalten)"""
        charakter = FakeCharakter()
        charakter.fertigkeiten = None  # provoziert AttributeError
        werte = self.berechne(charakter)
        self.assertEqual(werte, {})


class TestEffektRegistry(unittest.TestCase):
    """Smoke-Test: config/abgeleitete_effekte.json lädt und ist vollständig.

    Schlägt dieser Test fehl, fällt die Registry zur Laufzeit auf ein leeres
    Dict zurück und ALLE Talent-/Handicap-Effekte auf abgeleitete Werte
    verschwinden stillschweigend.
    """

    ERWARTETE_TALENTE = {
        "Block": {"parade": 1},
        "Harter Block": {"parade": 1},
        "Meister aller Waffen": {"parade": 1},
        "Waffenmeister": {"parade": 1},
        "Herdritter": {"parade": 1},
        "Lieblingswaffe": {"parade": 1},
        "Absolute Lieblingswaffe": {"parade": 2},
        "Behände": {"bewegungsweite": 2},
        "Flink": {"bewegungsweite": 2},
        "Kräftig": {"groesse": 1, "traglast_kg": 20},
        "Raufbold": {"robustheit": 1},
        "Schläger": {"robustheit": 1},
        "Jünger Erthas": {"robustheit": 1},
        "AH (Zauberer) Abnorme Blutlinie": {"robustheit": 1},
        "AH (Zauberer) Dämonische Blutlinie": {"robustheit": 1},
        "AH (Zauberer) Drachenblutlinie": {"robustheit": 2},
        "Kämpferische Disziplin": {"robustheit": 1},
        "Glück": {"bennys": 1},
        "Großes Glück": {"bennys": 1},
    }
    ERWARTETE_HANDICAPS = {"Langsam", "Fettleibig", "Alt", "Klein", "Schlank", "Jung"}

    def test_registry_laedt_und_ist_vollstaendig(self):
        """Alle 19 Talente und 6 Handicaps mit erwarteten Werten vorhanden"""
        from functions.effekt_registry import lade_abgeleitete_effekte
        registry = lade_abgeleitete_effekte()

        talente = registry.get('talente', {})
        for name, erwartete_werte in self.ERWARTETE_TALENTE.items():
            self.assertIn(name, talente, f"Talent '{name}' fehlt in der Registry")
            for wert, bonus in erwartete_werte.items():
                self.assertEqual(
                    talente[name].get(wert), bonus,
                    f"Talent '{name}': {wert} erwartet {bonus}"
                )

        self.assertEqual(set(registry.get('handicaps', {})), self.ERWARTETE_HANDICAPS)

    def test_nicht_kumulativ_gruppen(self):
        """Lieblingswaffe-Paar und Behände/Flink sind als Gruppen markiert"""
        from functions.effekt_registry import lade_abgeleitete_effekte
        talente = lade_abgeleitete_effekte()['talente']
        self.assertEqual(talente['Lieblingswaffe'].get('nicht_kumulativ_gruppe'),
                         talente['Absolute Lieblingswaffe'].get('nicht_kumulativ_gruppe'))
        self.assertEqual(talente['Behände'].get('nicht_kumulativ_gruppe'),
                         talente['Flink'].get('nicht_kumulativ_gruppe'))
        self.assertIsNotNone(talente['Behände'].get('nicht_kumulativ_gruppe'))
        # Block-Paar ist BEWUSST additiv (keine Gruppe)
        self.assertIsNone(talente['Block'].get('nicht_kumulativ_gruppe'))
        self.assertIsNone(talente['Harter Block'].get('nicht_kumulativ_gruppe'))

    def test_bedingung_kaempferische_disziplin(self):
        """Kämpferische Disziplin trägt die Rüstungs-Bedingung"""
        from functions.effekt_registry import lade_abgeleitete_effekte
        talente = lade_abgeleitete_effekte()['talente']
        self.assertEqual(talente['Kämpferische Disziplin'].get('bedingung'),
                         'keine_getragene_ruestung')


if __name__ == '__main__':
    unittest.main()
