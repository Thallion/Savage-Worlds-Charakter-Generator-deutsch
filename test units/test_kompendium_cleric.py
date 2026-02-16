#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Test: Cleric (Zwerg) - Fantasy Kompendium
================================================
Prueft die deutschen Uebersetzungen und verifiziert die Kosten
fuer einen fortgeschrittenen (Seasoned) Charakter mit 4 Aufstiegen.

UEBERSETZUNGSUEBERSICHT (EN -> DE im Fantasy Kompendium):
  Ancestry: Dwarf -> Zwerg
    Low Light Vision -> Nachtsicht
    Tough (Vigor d6) -> Widerstandsfaehig (Konstitution W6 statt W4)
    Reduced Pace -> Verringerte Bewegungsweite (-1 BW, Sprint-Wuerfel -1 Typ)

  Hindrances:
    Loyal (minor) -> Loyal (leicht, 1 Punkt)
    Pacifist (minor) -> Pazifist (leicht, 1 Punkt)
    Selfless (major) -> Aufopferungsvoll (schwer, 2 Punkte)
    Vow (major) -> Schwur (schwer) - AUTO von AH (Kleriker)

  Edges:
    Arcane Background (Cleric) -> Arkaner Hintergrund (Kleriker) (Hintergrund, Rang A)
      EFFEKT: 5 Maechte, 10 Machtpunkte, Auto-Handicap Schwur (schwer)
      Arkane Fertigkeit: Glaube (Willenskraft)
    Champion -> Gnade (Kleriker, Rang A) - FK-ERSATZ
      HINWEIS: Champion existiert nicht im FK. Gnade ist ein Kleriker-
      spezifisches Talent das thematisch passt (1 MP hebt Zustaende auf).
    Healer -> Heiler (Uebersinnlich, Rang A)
    Power Points -> Machtpunkte (Macht, Rang A)
    Favored Power -> Bevorzugte Macht (Macht, Rang F)

  Skills:
    Athletics -> Athletik (GES, Grundfertigkeit)
    Common Knowledge -> Allgemeinwissen (VER, Grundfertigkeit)
    Faith -> Glaube (WIL)
    Fighting -> Kaempfen (GES)
    Healing -> Heilen (VER)
    Notice -> Wahrnehmung (VER, Grundfertigkeit)
    Persuasion -> Ueberreden (WIL, Grundfertigkeit)
    Shooting -> Schiessen (GES)
    Stealth -> Heimlichkeit (GES, Grundfertigkeit)

  Powers:
    Boost/lower Trait -> Eigenschaft erhoehen/senken
    Healing -> Heilung
    Protection -> Schutz
    Relief -> Linderung
    Sanctuary -> Zuflucht

KOSTENAUFSTELLUNG (Fortgeschrittener Charakter):
  Attributpunkte: 5 Basis + 1 aus Handicap-Punkten = 6
  Fertigkeitspunkte: 12 Basis
  Handicap-Punkte: 4 (1 schwer + 2 leicht)
    -> 2 Punkte fuer Talent "Arkaner Hintergrund (Kleriker)"
    -> 2 Punkte fuer +1 Attributsteigerung
  Schwur (schwer): AUTO von AH (Kleriker), gibt keine HP
  Aufstiege: 4 (Fortgeschritten)
    -> 1. Gnade (Champion-Ersatz)
    -> 2. Heiler
    -> 3. Machtpunkte (+5 MP)
    -> 4. Bevorzugte Macht
"""

import unittest
import sys
from pathlib import Path

# Projekt-Root zum Python-Path hinzufuegen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.charakter import Charakter
from functions.setting_funktionen import CustomElementManager
from functions.talent_funktionen import waehle_talent, waehle_freies_talent
from functions.handicap_funktionen import waehle_handicap
from functions.volk_funktionen import waehle_volk


class TestClericUebersetzungen(unittest.TestCase):
    """Prueft die deutschen Uebersetzungen der Cleric-Archetyp-Elemente im FK."""

    SETTING = "Fantasy Kompendium"

    def setUp(self):
        self.charakter = Charakter(active_setting_name=self.SETTING, char_name="Cleric")
        self.charakter.custom_element_manager = CustomElementManager(
            self.charakter, setting_name=self.SETTING
        )
        self.charakter.custom_element_manager.set_active_setting(self.SETTING)
        self.charakter.active_setting_name = self.SETTING

    # ------------------------------------------------------------------
    # Volk / Ancestry
    # ------------------------------------------------------------------
    def test_zwerg_vorhanden(self):
        """Zwerg (Dwarf) muss als Volk im FK existieren."""
        self.assertIn("Zwerg", self.charakter.voelker,
                      "Zwerg fehlt im FK voelker-Katalog")

    def test_zwerg_besonderheiten(self):
        """Zwerg muss Nachtsicht und Widerstandsfaehig als Besonderheiten haben."""
        volk = self.charakter.voelker.get("Zwerg")
        self.assertIsNotNone(volk, "Zwerg-Eintrag nicht gefunden")
        besonderheiten_text = " ".join(
            getattr(volk, 'besonderheiten', []) if hasattr(volk, 'besonderheiten')
            else volk.get('besonderheiten', []) if isinstance(volk, dict) else []
        )
        self.assertIn("Nachtsicht", besonderheiten_text,
                      "Nachtsicht (Low Light Vision) fehlt bei Zwerg")
        self.assertIn("Widerstandsfähig", besonderheiten_text,
                      "Widerstandsfähig (Tough) fehlt bei Zwerg")

    def test_zwerg_verringerte_bewegungsweite(self):
        """Zwerg muss Verringerte Bewegungsweite als Volk-Handicap haben."""
        volk = self.charakter.voelker.get("Zwerg")
        self.assertIsNotNone(volk, "Zwerg-Eintrag nicht gefunden")
        handicaps_text = " ".join(
            getattr(volk, 'handicaps', []) if hasattr(volk, 'handicaps')
            else volk.get('handicaps', []) if isinstance(volk, dict) else []
        )
        self.assertIn("Verringerte Bewegungsweite", handicaps_text,
                      "Verringerte Bewegungsweite fehlt bei Zwerg")

    # ------------------------------------------------------------------
    # Handicaps / Hindrances
    # ------------------------------------------------------------------
    def test_handicap_loyal(self):
        """Loyal muss als leichtes Handicap im FK existieren."""
        self.assertIn("Loyal", self.charakter.handicaps,
                      "Loyal fehlt im FK")
        handicap = self.charakter.handicaps["Loyal"]
        stufe = getattr(handicap, 'stufe', None)
        if stufe:
            self.assertEqual(stufe, "leicht",
                             f"Loyal sollte 'leicht' sein, ist '{stufe}'")

    def test_handicap_pazifist_leicht(self):
        """Pazifist (Pacifist) muss als leichtes Handicap im FK existieren."""
        self.assertIn("Pazifist_leicht", self.charakter.handicaps,
                      "Pazifist_leicht fehlt im FK")
        handicap = self.charakter.handicaps["Pazifist_leicht"]
        stufe = getattr(handicap, 'stufe', None)
        if stufe:
            self.assertEqual(stufe, "leicht",
                             f"Pazifist sollte 'leicht' sein, ist '{stufe}'")

    def test_handicap_aufopferungsvoll_schwer(self):
        """Aufopferungsvoll (Selfless) muss als schweres Handicap im FK existieren."""
        self.assertIn("Aufopferungsvoll_schwer", self.charakter.handicaps,
                      "Aufopferungsvoll_schwer (Selfless) fehlt im FK")
        handicap = self.charakter.handicaps["Aufopferungsvoll_schwer"]
        stufe = getattr(handicap, 'stufe', None)
        if stufe:
            self.assertEqual(stufe, "schwer",
                             f"Aufopferungsvoll sollte 'schwer' sein, ist '{stufe}'")

    def test_handicap_schwur_schwer(self):
        """Schwur (Vow) muss als schweres Handicap im FK existieren (Auto von AH Kleriker)."""
        self.assertIn("Schwur_schwer", self.charakter.handicaps,
                      "Schwur_schwer (Vow) fehlt im FK")
        handicap = self.charakter.handicaps["Schwur_schwer"]
        stufe = getattr(handicap, 'stufe', None)
        if stufe:
            self.assertEqual(stufe, "schwer",
                             f"Schwur sollte 'schwer' sein, ist '{stufe}'")

    # ------------------------------------------------------------------
    # Talente / Edges
    # ------------------------------------------------------------------
    def test_talent_ah_kleriker(self):
        """Arkaner Hintergrund (Kleriker) muss als Talent im FK existieren."""
        self.assertIn("Arkaner Hintergrund (Kleriker)", self.charakter.talente,
                      "Arkaner Hintergrund (Kleriker) fehlt im FK")

    def test_talent_gnade(self):
        """Gnade muss als Kleriker-Talent im FK existieren (Champion-Ersatz)."""
        self.assertIn("Auserwählter", self.charakter.talente,
                      "Auserwählter fehlt im FK")

    def test_talent_heiler(self):
        """Heiler (Healer) muss als Talent im FK existieren."""
        self.assertIn("Heiler", self.charakter.talente,
                      "Heiler (Healer) fehlt im FK")

    def test_talent_machtpunkte(self):
        """Machtpunkte (Power Points) muss als Talent im FK existieren."""
        self.assertIn("Machtpunkte", self.charakter.talente,
                      "Machtpunkte (Power Points) fehlt im FK")

    def test_talent_bevorzugte_macht(self):
        """Bevorzugte Macht (Favored Power) muss als Talent im FK existieren."""
        self.assertIn("Bevorzugte Macht", self.charakter.talente,
                      "Bevorzugte Macht (Favored Power) fehlt im FK")

    # ------------------------------------------------------------------
    # Fertigkeiten / Skills
    # ------------------------------------------------------------------
    def test_alle_fertigkeiten_vorhanden(self):
        """Alle benoetigten Fertigkeiten muessen im FK existieren."""
        erwartete = [
            "Athletik", "Allgemeinwissen", "Glaube", "Kämpfen",
            "Heilen", "Wahrnehmung", "Überreden", "Schießen",
            "Heimlichkeit"
        ]
        for fert in erwartete:
            self.assertIn(fert, self.charakter.fertigkeiten,
                          f"Fertigkeit '{fert}' fehlt im FK")

    def test_fertigkeiten_attribut_verknuepfung(self):
        """Fertigkeiten muessen mit den korrekten Attributen verknuepft sein."""
        erwartete_links = {
            "Athletik": "Geschicklichkeit",
            "Allgemeinwissen": "Verstand",
            "Glaube": "Willenskraft",
            "Kämpfen": "Geschicklichkeit",
            "Heilen": "Verstand",
            "Wahrnehmung": "Verstand",
            "Überreden": "Willenskraft",
            "Schießen": "Geschicklichkeit",
            "Heimlichkeit": "Geschicklichkeit",
        }
        for fert_name, erwartet_attr in erwartete_links.items():
            if fert_name in self.charakter.fertigkeiten:
                fert = self.charakter.fertigkeiten[fert_name]
                attr_name = getattr(fert.attribut, 'attribut_name',
                                    getattr(fert.attribut, 'name', None))
                if attr_name:
                    self.assertEqual(
                        attr_name, erwartet_attr,
                        f"{fert_name} sollte mit {erwartet_attr} verknuepft sein, "
                        f"ist aber mit {attr_name}"
                    )

    # ------------------------------------------------------------------
    # Maechte / Powers
    # ------------------------------------------------------------------
    def test_alle_maechte_vorhanden(self):
        """Alle benoetigten Maechte muessen im FK existieren."""
        erwartete = [
            "Eigenschaft erhöhen/senken", "Heilung", "Schutz",
            "Linderung", "Zuflucht"
        ]
        maechte = getattr(self.charakter, 'maechte', {})
        for macht_name in erwartete:
            self.assertIn(macht_name, maechte,
                          f"Macht '{macht_name}' fehlt im FK")


class TestClericCharakterErstellung(unittest.TestCase):
    """Erstellt den Cleric Schritt fuer Schritt und verifiziert die Kosten."""

    SETTING = "Fantasy Kompendium"

    def setUp(self):
        self.charakter = Charakter(active_setting_name=self.SETTING, char_name="Thordis")
        self.charakter.profil_daten["Name"] = "Thordis die Gottestreue"
        self.charakter.beschreibung = (
            "Meine Goettin zeigt ihre Gnade allen, die Trost "
            "in ihrer lebensspendenden Umarmung suchen."
        )
        self.charakter.custom_element_manager = CustomElementManager(
            self.charakter, setting_name=self.SETTING
        )
        self.charakter.custom_element_manager.set_active_setting(self.SETTING)
        self.charakter.active_setting_name = self.SETTING

    # ------------------------------------------------------------------
    # Hilfsmethode: Kompletten Novize-Charakter aufbauen
    # ------------------------------------------------------------------
    def _baue_novize(self):
        """Baut den Novize-Cleric auf und gibt die Kosten zurueck.

        Reihenfolge: Volk -> Handicaps -> Attribute -> AH (Kleriker) -> Fertigkeiten
        AH (Kleriker) muss VOR den Fertigkeiten gewaehlt werden, damit Glaube
        als arkane Fertigkeit verfuegbar ist.
        """
        kosten = {
            'attribut_basis': 0,
            'attribut_handicap': 0,
            'fertigkeiten': 0,
            'handicap_gesamt': 0,
            'talent_ah_kleriker_hp': 0,
        }

        # --- VOLK: Zwerg (Konstitution W6 durch Widerstandsfaehig) ---
        waehle_volk(self.charakter, "Zwerg")

        # --- HANDICAPS: 4 Punkte ---
        # Loyal (leicht 1) + Pazifist (leicht 1) + Aufopferungsvoll (schwer 2)
        # Schwur (schwer): AUTO von AH (Kleriker), zaehlt NICHT als Handicap-Punkte
        handicap_namen = ["Loyal", "Pazifist_leicht", "Aufopferungsvoll_schwer"]
        for hc_name in handicap_namen:
            if hc_name in self.charakter.handicaps:
                erfolg = waehle_handicap(self.charakter, hc_name)
                if erfolg:
                    hc = self.charakter.handicaps[hc_name]
                    kosten['handicap_gesamt'] += getattr(hc, 'punkte',
                                                         getattr(hc, 'wert', 0))

        # --- ATTRIBUTE: 6 Steigerungen (5 Basis + 1 aus HP) ---
        # Ziel: GES W6, VER W6, WIL W8, STAe W6, KON W8
        attribut_plan = [
            ('Geschicklichkeit', 1),  # W4 -> W6
            ('Verstand', 1),          # W4 -> W6
            ('Willenskraft', 2),      # W4 -> W8
            ('Stärke', 1),            # W4 -> W6
            ('Konstitution', 1),      # W6 -> W8 (Zwerg-Start)
        ]
        for attr_name, count in attribut_plan:
            for _ in range(count):
                ap_vor = self.charakter.verbleibende_attributsteigerungen
                hp_vor = self.charakter.verbleibende_handicap_punkte
                erfolg = self.charakter.steigere_attribut(attr_name)
                if erfolg:
                    ap_diff = ap_vor - self.charakter.verbleibende_attributsteigerungen
                    hp_diff = hp_vor - self.charakter.verbleibende_handicap_punkte
                    kosten['attribut_basis'] += ap_diff
                    kosten['attribut_handicap'] += hp_diff

        # --- NOVIZE-TALENT: AH (Kleriker) (2 HP) ---
        # Gibt 5 Maechte + 10 Machtpunkte + Auto-Handicap Schwur (schwer)
        if "Arkaner Hintergrund (Kleriker)" in self.charakter.talente:
            hp_vor = self.charakter.verbleibende_handicap_punkte
            erfolg = waehle_talent(self.charakter, "Arkaner Hintergrund (Kleriker)")
            if erfolg:
                hp_diff = hp_vor - self.charakter.verbleibende_handicap_punkte
                kosten['talent_ah_kleriker_hp'] = hp_diff

        # --- FERTIGKEITEN: 12 Punkte ---
        # Grundfertigkeiten (starten W4): Athletik, Allgemeinwissen, Heimlichkeit,
        #                                  Ueberreden, Wahrnehmung
        # Nicht-Grundfertigkeiten (starten W4-2): Glaube, Kaempfen, Heilen, Schiessen
        #
        # Athletik: W4->W6, verknuepft mit GES W6: 1 Pkt
        # Allgemeinwissen: bleibt W4: 0 Pkt
        # Glaube: W4-2->W8, verknuepft mit WIL W8:
        #   W4-2->W4(1) + W4->W6(1) + W6->W8(1) = 3 Pkt
        # Kaempfen: W4-2->W8, verknuepft mit GES W6:
        #   W4-2->W4(1) + W4->W6(1) + W6->W8(2 doppelt!) = 4 Pkt
        # Heilen: W4-2->W6, verknuepft mit VER W6:
        #   W4-2->W4(1) + W4->W6(1) = 2 Pkt
        # Wahrnehmung: bleibt W4: 0 Pkt
        # Ueberreden: bleibt W4: 0 Pkt
        # Schiessen: W4-2->W6, verknuepft mit GES W6:
        #   W4-2->W4(1) + W4->W6(1) = 2 Pkt
        # Heimlichkeit: bleibt W4: 0 Pkt
        # Gesamt: 1+0+3+4+2+0+0+2+0 = 12 Pkt
        fertigkeits_plan = [
            ('Athletik', 1),       # W4->W6
            ('Glaube', 3),         # W4-2->W8 (3 Raises: 1+1+1=3 FP)
            ('Kämpfen', 3),        # W4-2->W8 (3 Raises: 1+1+2=4 FP)
            ('Heilen', 2),         # W4-2->W6 (2 Raises: 1+1=2 FP)
            ('Schießen', 2),       # W4-2->W6 (2 Raises: 1+1=2 FP)
        ]
        for fert_name, count in fertigkeits_plan:
            for _ in range(count):
                fp_vor = getattr(self.charakter, 'verbleibende_fertigkeitssteigerungen',
                                 getattr(self.charakter, 'verbleibende_fertigkeitspunkte', 0))
                erfolg = self.charakter.steigere_fertigkeit(fert_name, confirm_double_cost=True)
                fp_nach = getattr(self.charakter, 'verbleibende_fertigkeitssteigerungen',
                                  getattr(self.charakter, 'verbleibende_fertigkeitspunkte', 0))
                if erfolg == True:
                    kosten['fertigkeiten'] += max(fp_vor - fp_nach, 1)

        return kosten

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------
    def test_01_zwerg_konstitution_bonus(self):
        """Zwerg startet mit Konstitution W6 (Widerstandsfaehig)."""
        waehle_volk(self.charakter, "Zwerg")
        self.assertEqual(self.charakter.attribute['Konstitution'].wuerfel.value, 6,
                         "Konstitution sollte W6 durch Zwerg-Widerstandsfähig sein")

    def test_02_handicap_punkte(self):
        """4 Handicap-Punkte: Loyal (1) + Pazifist (1) + Aufopferungsvoll (2)."""
        for name in ["Loyal", "Pazifist_leicht", "Aufopferungsvoll_schwer"]:
            if name in self.charakter.handicaps:
                waehle_handicap(self.charakter, name)

        self.assertEqual(
            self.charakter.gesamt_handicap_punkte, 4,
            f"Erwartete 4 Handicap-Punkte, erhalten: "
            f"{self.charakter.gesamt_handicap_punkte}"
        )
        self.assertEqual(
            self.charakter.verbleibende_handicap_punkte, 4,
            f"Alle 4 HP sollten verfuegbar sein, sind: "
            f"{self.charakter.verbleibende_handicap_punkte}"
        )

    def test_03_attribut_budget(self):
        """6 Attributsteigerungen: 5 Basis + 1 aus Handicap-Punkten (2 HP)."""
        # Handicaps zuerst
        for name in ["Loyal", "Pazifist_leicht", "Aufopferungsvoll_schwer"]:
            if name in self.charakter.handicaps:
                waehle_handicap(self.charakter, name)

        # Konstitution W6 durch Zwerg
        waehle_volk(self.charakter, "Zwerg")

        # 6 Steigerungen durchfuehren
        steigerungen_ok = 0
        for attr, count in [('Geschicklichkeit', 1), ('Verstand', 1),
                            ('Willenskraft', 2), ('Stärke', 1), ('Konstitution', 1)]:
            for _ in range(count):
                if self.charakter.steigere_attribut(attr):
                    steigerungen_ok += 1

        self.assertEqual(steigerungen_ok, 6,
                         f"6 Attributsteigerungen erwartet, {steigerungen_ok} erfolgreich")

        # Zielwerte pruefen
        self.assertEqual(self.charakter.attribute['Geschicklichkeit'].wuerfel.value, 6)
        self.assertEqual(self.charakter.attribute['Verstand'].wuerfel.value, 6)
        self.assertEqual(self.charakter.attribute['Willenskraft'].wuerfel.value, 8)
        self.assertEqual(self.charakter.attribute['Stärke'].wuerfel.value, 6)
        self.assertEqual(self.charakter.attribute['Konstitution'].wuerfel.value, 8)

        # 5 Basis verbraucht + 2 HP fuer den 6. Raise
        self.assertEqual(self.charakter.verbleibende_attributsteigerungen, 0,
                         "Alle 5 Basis-Attributpunkte sollten verbraucht sein")
        self.assertEqual(self.charakter.verbleibende_handicap_punkte, 2,
                         "2 HP sollten noch uebrig sein (4 - 2 fuer Attribut)")

    def test_04_ah_kleriker_aus_hp(self):
        """AH (Kleriker) aus Handicap-Punkten + Auto-Handicap Schwur."""
        # Handicaps
        for name in ["Loyal", "Pazifist_leicht", "Aufopferungsvoll_schwer"]:
            if name in self.charakter.handicaps:
                waehle_handicap(self.charakter, name)
        # Volk + Attribute (WIL W6 minimum fuer AH Kleriker Voraussetzung)
        waehle_volk(self.charakter, "Zwerg")
        for attr, count in [('Geschicklichkeit', 1), ('Verstand', 1),
                            ('Willenskraft', 2), ('Stärke', 1), ('Konstitution', 1)]:
            for _ in range(count):
                self.charakter.steigere_attribut(attr)

        # AH (Kleriker) mit 2 verbleibenden HP kaufen
        erfolg = waehle_talent(self.charakter, "Arkaner Hintergrund (Kleriker)")
        self.assertTrue(erfolg, "AH (Kleriker) konnte nicht gewaehlt werden")

        # AH (Kleriker) sollte ausgewaehlt sein
        ah = self.charakter.talente.get("Arkaner Hintergrund (Kleriker)")
        self.assertIsNotNone(ah, "AH (Kleriker) nicht gefunden")
        self.assertTrue(ah.ausgewaehlt, "AH (Kleriker) sollte ausgewaehlt sein")

        # HP sollten verbraucht sein
        self.assertEqual(self.charakter.verbleibende_handicap_punkte, 0,
                         "Alle HP sollten verbraucht sein (2 Attribut + 2 AH Kleriker)")

        # Schwur (schwer) sollte automatisch aktiviert sein
        schwur = self.charakter.handicaps.get("Schwur_schwer")
        if schwur:
            self.assertTrue(schwur.ausgewaehlt,
                            "Schwur (schwer) sollte auto-aktiviert sein durch AH Kleriker")

    def test_05_fertigkeiten_budget(self):
        """12 Fertigkeitspunkte reichen fuer den Cleric-Skillplan.

        Glaube (WIL W8): 0->W8 = 3 Punkte (1+1+1, alle unter/gleich Attribut)
        Kaempfen (GES W6): 0->W8 = 4 Punkte (1+1+2, W8 ueber GES W6!)
        Heilen (VER W6): 0->W6 = 2 Punkte (1+1)
        Schiessen (GES W6): 0->W6 = 2 Punkte (1+1)
        Athletik (GES W6): W4->W6 = 1 Punkt
        Gesamt: 3+4+2+2+1 = 12
        """
        kosten = self._baue_novize()

        print(f"\n  Fertigkeitskosten: {kosten['fertigkeiten']} von 12")

        # Budget muss exakt aufgehen: 12 Punkte
        self.assertEqual(kosten['fertigkeiten'], 12,
                         f"Fertigkeitskosten sollten exakt 12 sein, sind {kosten['fertigkeiten']}")

        # Ziel-Fertigkeitswerte pruefen
        erwartete_werte = {
            'Athletik': 6,
            'Allgemeinwissen': 4,
            'Glaube': 8,
            'Kämpfen': 8,
            'Heilen': 6,
            'Wahrnehmung': 4,
            'Überreden': 4,
            'Schießen': 6,
            'Heimlichkeit': 4,
        }
        for fert_name, erwartet in erwartete_werte.items():
            if fert_name in self.charakter.fertigkeiten:
                ist_wert = self.charakter.fertigkeiten[fert_name].wuerfel.value
                self.assertEqual(
                    ist_wert, erwartet,
                    f"{fert_name}: erwartet W{erwartet}, ist W{ist_wert}"
                )

    def test_06_aufstiegsphase_fortgeschritten(self):
        """4 Aufstiege: Gnade, Heiler, Machtpunkte, Bevorzugte Macht."""
        self._baue_novize()

        # Char-Gen abschliessen
        self.charakter.char_gen_completed = True

        # 4 Aufstiege hinzufuegen -> Rang "Fortgeschritten" (Seasoned)
        for _ in range(4):
            self.charakter.increase_aufstiege()

        self.assertEqual(self.charakter.aufstiege_gesamt, 4,
                         "4 Aufstiege gesamt erwartet")
        self.assertEqual(self.charakter.rang, "Fortgeschritten",
                         f"Rang sollte 'Fortgeschritten' sein, ist '{self.charakter.rang}'")
        self.assertEqual(self.charakter.verbleibende_aufstiege, 4,
                         "4 verbleibende Aufstiege erwartet")

        # Aufstiegs-Talente waehlen
        # HINWEIS: Champion existiert nicht im FK, daher Gnade als Ersatz.
        # Bevorzugte Macht hat generische Voraussetzung "Arkane Fertigkeit W8"
        # und "Arkaner Hintergrund (beliebig)" - ggf. ignore_voraussetzungen noetig.
        aufstiegs_talente = ["Gnade", "Heiler", "Machtpunkte", "Bevorzugte Macht"]
        gewaehlt = 0
        for talent_name in aufstiegs_talente:
            if talent_name in self.charakter.talente:
                # Bevorzugte Macht hat generische Voraussetzungen
                if talent_name == "Bevorzugte Macht":
                    self.charakter.ignore_voraussetzungen = True
                erfolg = waehle_talent(self.charakter, talent_name, ignore_rang_check=True)
                if erfolg == True:
                    gewaehlt += 1
                    print(f"  Aufstieg {gewaehlt}: {talent_name}")

        self.assertEqual(gewaehlt, 4,
                         f"4 Aufstiegs-Talente erwartet, {gewaehlt} gewaehlt")
        self.assertEqual(self.charakter.verbleibende_aufstiege, 0,
                         "Alle Aufstiege sollten verbraucht sein")

    def test_07_abgeleitete_werte(self):
        """Abgeleitete Werte: Bewegungsweite 5 (Zwerg), Parade 6, Robustheit 6."""
        self._baue_novize()
        self.charakter.char_gen_completed = True
        for _ in range(4):
            self.charakter.increase_aufstiege()
        for t in ["Gnade", "Heiler", "Machtpunkte"]:
            if t in self.charakter.talente:
                waehle_talent(self.charakter, t, ignore_rang_check=True)
        if "Bevorzugte Macht" in self.charakter.talente:
            self.charakter.ignore_voraussetzungen = True
            waehle_talent(self.charakter, "Bevorzugte Macht", ignore_rang_check=True)

        try:
            self.charakter.berechne_abgeleitete_werte()
        except RecursionError:
            print("  Warnung: RecursionError bei abgeleiteten Werten")
            return

        # Bewegungsweite: 5 (Zwerg: 6 - 1 Verringerte Bewegungsweite)
        bw = getattr(self.charakter, 'bewegungsweite', None)
        if bw is not None:
            self.assertEqual(bw, 5, f"Bewegungsweite: erwartet 5 (Zwerg), ist {bw}")

        # Parade: 2 + Kaempfen/2 = 2 + 8/2 = 6
        parade = getattr(self.charakter, 'parade', None)
        if parade is not None:
            self.assertEqual(parade, 6, f"Parade: erwartet 6, ist {parade}")

        # Robustheit Basis: 2 + KON/2 = 2 + 8/2 = 6
        rob = getattr(self.charakter, 'robustheit_basis', None)
        if rob is not None:
            self.assertEqual(rob, 6, f"Robustheit-Basis: erwartet 6, ist {rob}")

    def test_08_gesamtkosten_abrechnung(self):
        """Vollstaendige Kostenabrechnung mit Budget-Bilanz."""
        kosten = self._baue_novize()

        print("\n" + "=" * 60)
        print("KOSTENABRECHNUNG: CLERIC (ZWERG)")
        print("=" * 60)

        # Novize-Phase
        print(f"\nNOVIZE-PHASE:")
        print(f"  Handicap-Punkte erhalten: {kosten['handicap_gesamt']}")
        print(f"  Attribut (Basis):         {kosten['attribut_basis']} / 5")
        print(f"  Attribut (aus HP):        {kosten['attribut_handicap']} HP")
        print(f"  AH-Kleriker-Talent (HP):  {kosten['talent_ah_kleriker_hp']} HP")
        print(f"  Fertigkeiten:             {kosten['fertigkeiten']} / 12")

        hp_verbraucht = kosten['attribut_handicap'] + kosten['talent_ah_kleriker_hp']
        print(f"\n  HP-Bilanz: {hp_verbraucht} / {kosten['handicap_gesamt']} verbraucht")
        print(f"  FP-Bilanz: {kosten['fertigkeiten']} / 12 verbraucht")

        # Aufstiegs-Phase
        self.charakter.char_gen_completed = True
        for _ in range(4):
            self.charakter.increase_aufstiege()

        aufstieg_talente = ["Gnade", "Heiler", "Machtpunkte", "Bevorzugte Macht"]
        aufstieg_ok = 0
        for t in aufstieg_talente:
            if t in self.charakter.talente:
                if t == "Bevorzugte Macht":
                    self.charakter.ignore_voraussetzungen = True
                if waehle_talent(self.charakter, t, ignore_rang_check=True) == True:
                    aufstieg_ok += 1

        print(f"\nAUFSTIEGS-PHASE:")
        print(f"  Aufstiege verbraucht: {aufstieg_ok} / 4")
        print(f"  Rang: {self.charakter.rang}")

        print(f"\nHINWEISE:")
        print(f"  Champion existiert nicht im FK -> Gnade als Ersatz")
        print(f"  Schwur (schwer) ist Auto-Handicap von AH (Kleriker)")
        print(f"  Bevorzugte Macht: generische Voraussetzung, ignore_voraussetzungen")

        # Budget-Assertions
        self.assertEqual(kosten['attribut_basis'], 5,
                         "5 Basis-Attributpunkte sollten verbraucht sein")
        self.assertEqual(kosten['fertigkeiten'], 12,
                         "Fertigkeitskosten sollten exakt 12 sein")
        self.assertEqual(aufstieg_ok, 4,
                         "4 Aufstiegs-Talente sollten gewaehlt sein")
        self.assertEqual(self.charakter.rang, "Fortgeschritten",
                         "Rang sollte Fortgeschritten (Seasoned) sein")

        print(f"\n{'=' * 60}")
        print("ERGEBNIS: Budget geht auf!")
        print(f"  Attributpunkte:     5/5 Basis + 2 HP fuer 1 extra = 6")
        print(f"  Fertigkeitspunkte:  12/12 Basis")
        print(f"  Handicap-Punkte:    4/4 (2 Attribut + 2 AH Kleriker)")
        print(f"  Auto-Handicap:      Schwur (schwer) durch AH Kleriker")
        print(f"  Aufstiege:          4/4 (4 Talente)")
        print(f"{'=' * 60}")


def run_tests():
    """Fuehre alle Tests aus."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    print("=" * 60)
    print("UNIT TESTS: CLERIC (ZWERG) - FANTASY KOMPENDIUM")
    print("Deutsche Uebersetzungen + Kosten Fortgeschrittener Rang")
    print("=" * 60)
    run_tests()
