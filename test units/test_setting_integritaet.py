# -*- coding: utf-8 -*-
"""
Daten-Integritätstests für alle settings/*.json

Prüft jede Setting-Datei auf:
1. Pflichtfelder (Talente, Handicaps, Mächte)
2. Fertigkeit → Attribut-Referenzen (inkl. Strukturvarianten:
   Werte als Liste ODER Dict mit 'original'; fehlender attribute-Block
   wie bei 50 Fathoms → Standard-5-Fallback)
3. Volk-auto_*-Referenzen gegen die LAUFZEIT-Bedingung aus
   models/volk.py (auto_talente/auto_handicaps/auto_mächte werden dort
   sonst STUMM übersprungen — genau diese Bug-Klasse fängt der Test)
4. Talent-Voraussetzungen mit dem ECHTEN Parser
   (TalentManager.pruefe_voraussetzungen) im Maximal-Zustand:
   alle Würfel W12, Rang Legendär, alle Talente gewählt — jede dann noch
   verbleibende Meldung ist ein Referenz-Verstoß.
   Ausnahme: "Handicap:"/"Volk:"/"Volk-Eigenschaft:"-Präfixe melden im
   Maximal-Zustand immer "wird vorausgesetzt"; ihre Existenz wird separat
   statisch geprüft.

Bestandsverstöße stehen in setting_integritaet_whitelist.py.
Die Whitelist darf nur schrumpfen: neue Verstöße UND nicht mehr
auftretende Whitelist-Einträge lassen den Test fehlschlagen.
"""

import json
import unittest
import sys
from pathlib import Path

# Pfad zur Projektroot hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

from models.charakter import Charakter
from functions.setting_funktionen import CustomElementManager
from functions.talent_funktionen import get_talent_manager
from setting_integritaet_whitelist import BEKANNTE_VERSTOESSE

SETTINGS_VERZ = project_root / "settings"

# Fallback, wenn ein Setting keinen attribute-Block hat (z.B. 50 Fathoms)
STANDARD_ATTRIBUTE = {
    "Geschicklichkeit", "Stärke", "Konstitution", "Verstand", "Willenskraft",
}

GUELTIGE_STUFEN = {"leicht", "schwer"}

# Meldungen der separat statisch geprüften Präfix-Checker
IGNORIERTE_MELDUNGS_MUSTER = ("Handicap '", "Volk '", "Volk-Eigenschaft '")

TALENT_PFLICHTFELDER = ("name", "kategorie", "rang", "voraussetzungen", "beschreibung")
HANDICAP_PFLICHTFELDER = ("name", "stufe", "punkte")
MACHT_PFLICHTFELDER = ("name", "rang")


def baue_max_charakter(setting):
    """Headless Charakter im Maximal-Zustand (Muster: test_kompendium_cleric)."""
    charakter = Charakter(active_setting_name=setting, char_name="Integrität")
    charakter.custom_element_manager = CustomElementManager(
        charakter, setting_name=setting
    )
    charakter.custom_element_manager.set_active_setting(setting)
    charakter.active_setting_name = setting

    charakter.rang = "Legendär"
    for attribut in charakter.attribute.values():
        attribut.wuerfel.value = 12
        attribut.wuerfel.modifier = 0
    for fertigkeit in charakter.fertigkeiten.values():
        fertigkeit.wuerfel.value = 12
        fertigkeit.wuerfel.modifier = 0
    for name, talent in charakter.talente.items():
        talent.ausgewaehlt = True
        if name not in charakter.selected_talente:
            charakter.selected_talente.append(name)
    return charakter


def pruefe_pflichtfelder(daten):
    verstoesse = []
    for key, talent in daten.get('talente', {}).items():
        for feld in TALENT_PFLICHTFELDER:
            if feld not in talent:
                verstoesse.append(f"Talent '{key}': Feld '{feld}' fehlt")
        if not isinstance(talent.get('voraussetzungen', []), list):
            verstoesse.append(f"Talent '{key}': voraussetzungen ist keine Liste")
    for key, handicap in daten.get('handicaps', {}).items():
        for feld in HANDICAP_PFLICHTFELDER:
            if feld not in handicap:
                verstoesse.append(f"Handicap '{key}': Feld '{feld}' fehlt")
    for key, macht in daten.get('maechte', {}).items():
        for feld in MACHT_PFLICHTFELDER:
            if feld not in macht:
                verstoesse.append(f"Macht '{key}': Feld '{feld}' fehlt")
    return verstoesse


def pruefe_fertigkeit_attribut_referenzen(daten):
    verstoesse = []
    attribute = set(daten.get('attribute', {}).keys()) or set(STANDARD_ATTRIBUTE)
    for fert, wert in daten.get('fertigkeiten_daten', {}).items():
        # Strukturvarianten: Liste ODER Dict mit 'original' (Savage Aventurien)
        attrs = wert if isinstance(wert, list) else wert.get('original', [])
        for attr in attrs:
            if attr not in attribute:
                verstoesse.append(
                    f"Fertigkeit '{fert}' → unbekanntes Attribut '{attr}'"
                )
    return verstoesse


def pruefe_volk_auto_referenzen(charakter):
    """Repliziert die Lookup-Bedingung aus models/volk.py (apply_effects_to_charakter)."""
    verstoesse = []
    for volk_name, volk in charakter.voelker.items():
        effects = getattr(volk, 'effects', {}) or {}
        for talent in effects.get('auto_talente', []):
            if talent not in charakter.talente:
                verstoesse.append(
                    f"Volk '{volk_name}': auto_talent '{talent}' existiert nicht"
                )
        for handicap in effects.get('auto_handicaps', []):
            if handicap not in charakter.handicaps:
                verstoesse.append(
                    f"Volk '{volk_name}': auto_handicap '{handicap}' existiert nicht"
                )
        for macht in effects.get('auto_mächte', []):
            if macht not in charakter.maechte:
                verstoesse.append(
                    f"Volk '{volk_name}': auto_macht '{macht}' existiert nicht"
                )
    return verstoesse


def _volk_hat_eigenschaft(charakter, eigenschaft):
    for volk in charakter.voelker.values():
        spez = (getattr(volk, 'effects', {}) or {}).get('spezielle_effekte', {})
        if isinstance(spez, dict) and spez.get(eigenschaft):
            return True
        if isinstance(spez, list) and any(
            e.get('typ') == eigenschaft and e.get('wert') for e in spez
        ):
            return True
    return False


def pruefe_praefix_voraussetzungen(daten, charakter):
    """Statische Existenzprüfung für Handicap:/Volk:/Volk-Eigenschaft:-Präfixe."""
    verstoesse = []
    for t_key, talent in daten.get('talente', {}).items():
        for voraussetzung in talent.get('voraussetzungen', []):
            if not isinstance(voraussetzung, str):
                continue
            if voraussetzung.startswith("Handicap: "):
                praefix = voraussetzung[len("Handicap: "):]
                if not any(k.startswith(praefix) for k in charakter.handicaps):
                    verstoesse.append(
                        f"Talent '{t_key}': {voraussetzung} (kein Handicap-Key passt)"
                    )
            elif voraussetzung.startswith("Volk: "):
                volk_name = voraussetzung[len("Volk: "):]
                if volk_name not in charakter.voelker:
                    verstoesse.append(
                        f"Talent '{t_key}': {voraussetzung} (Volk fehlt)"
                    )
            elif voraussetzung.startswith("Volk-Eigenschaft: "):
                eigenschaft = voraussetzung[len("Volk-Eigenschaft: "):]
                if not _volk_hat_eigenschaft(charakter, eigenschaft):
                    verstoesse.append(
                        f"Talent '{t_key}': {voraussetzung} (keine Volk-Eigenschaft)"
                    )
    return verstoesse


def pruefe_talent_voraussetzungen(charakter):
    """Parser-Lauf im Maximal-Zustand: jede Meldung ist ein Referenz-Verstoß."""
    verstoesse = []
    manager = get_talent_manager(charakter)
    for t_key, talent in charakter.talente.items():
        for meldung in manager.pruefe_voraussetzungen(talent):
            if any(meldung.startswith(m) for m in IGNORIERTE_MELDUNGS_MUSTER):
                continue
            verstoesse.append(f"Talent '{t_key}': {meldung}")
    return verstoesse


def sammle_verstoesse(setting, daten):
    charakter = baue_max_charakter(setting)
    verstoesse = []
    verstoesse += pruefe_pflichtfelder(daten)
    verstoesse += pruefe_fertigkeit_attribut_referenzen(daten)
    verstoesse += pruefe_volk_auto_referenzen(charakter)
    verstoesse += pruefe_praefix_voraussetzungen(daten, charakter)
    verstoesse += pruefe_talent_voraussetzungen(charakter)
    return set(verstoesse)


class TestSettingIntegritaet(unittest.TestCase):
    """Referenzielle Integrität aller Setting-Dateien"""

    @classmethod
    def setUpClass(cls):
        cls.setting_dateien = sorted(SETTINGS_VERZ.glob("*.json"))

    def test_settings_vorhanden(self):
        """Es gibt Setting-Dateien und für jede eine Whitelist-Sektion"""
        self.assertGreaterEqual(len(self.setting_dateien), 13)
        namen = {p.stem for p in self.setting_dateien}
        verwaiste_whitelist = set(BEKANNTE_VERSTOESSE) - namen
        self.assertEqual(
            verwaiste_whitelist, set(),
            f"Whitelist-Sektionen ohne Setting-Datei: {verwaiste_whitelist}"
        )

    def test_handicap_stufen_gueltig(self):
        """Alle Handicap-Stufen sind 'leicht' oder 'schwer' (harte Regel)"""
        for pfad in self.setting_dateien:
            with self.subTest(setting=pfad.stem):
                with open(pfad, encoding='utf-8') as f:
                    daten = json.load(f)
                stufen = {
                    h.get('stufe') for h in daten.get('handicaps', {}).values()
                    if 'stufe' in h
                }
                self.assertLessEqual(
                    stufen, GUELTIGE_STUFEN,
                    f"Ungültige Handicap-Stufen: {stufen - GUELTIGE_STUFEN}"
                )

    def test_referenzielle_integritaet(self):
        """Alle Verstöße == Whitelist (in beide Richtungen, pro Setting)"""
        for pfad in self.setting_dateien:
            setting = pfad.stem
            with self.subTest(setting=setting):
                with open(pfad, encoding='utf-8') as f:
                    daten = json.load(f)
                aktuell = sammle_verstoesse(setting, daten)
                erwartet = BEKANNTE_VERSTOESSE.get(setting, set())

                neue = aktuell - erwartet
                self.assertEqual(
                    neue, set(),
                    "NEUE Integritätsverstöße (in den Setting-Daten beheben, "
                    f"NICHT in die Whitelist eintragen!):\n  "
                    + "\n  ".join(sorted(neue))
                )

                behoben = erwartet - aktuell
                self.assertEqual(
                    behoben, set(),
                    "Whitelist-Einträge sind behoben und müssen aus "
                    f"setting_integritaet_whitelist.py entfernt werden:\n  "
                    + "\n  ".join(sorted(behoben))
                )


if __name__ == '__main__':
    unittest.main()
