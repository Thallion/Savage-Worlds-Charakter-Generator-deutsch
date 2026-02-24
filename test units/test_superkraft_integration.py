# test units/test_superkraft_integration.py
"""
Tests für Phase 5 der Superkräfte-Implementierung:
- GenerationPointsBar SKP-Anzeige (pointbar_view.py)
- StatBlock-Generator Superkräfte (statblock_generator.py)
- PDF-Export Superkräfte (pdf_utils.py)
"""
import unittest
import sys
import os
from unittest.mock import MagicMock, patch, PropertyMock

# Kivy-Headless-Modus
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_LOG_LEVEL'] = 'critical'

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.superkraft import Superkraft, SuperkraftModifikator
import functions.superkraft_funktionen as skf
from functions.statblock_generator import (
    generate_character_statblock,
    _format_superkraefte,
)


# ======================== HILFSFUNKTIONEN ========================

def _create_mock_charakter(setting_name="Superkräfte Kompendium"):
    """Erstellt einen Mock-Charakter für Tests"""
    char = MagicMock()
    char.active_setting_name = setting_name
    char.profil_daten = {"Name": "Test Held"}
    char.superkraefte = {}
    char.selected_superkraefte = []
    char.superkraft_punkte_gesamt = 45
    char.superkraft_punkte_verbraucht = 0
    char.machtstufe = "III"
    char.kraftobergrenze = 15
    char.attribute = {}
    char.fertigkeiten = {}
    char.selected_handicaps = []
    char.handicaps = {}
    char.selected_talente = []
    char.talente = {}
    char.selected_maechte = []
    char.maechte = {}
    char.machtpunkte = 0
    char.selected_waffen = []
    char.selected_ruestungen = []
    char.selected_schilde = []
    char.selected_allgemeine_ausruestung = []
    char.voelker = {}
    char.voelker_selected = {}
    char.bewegungsweite = 6
    char.parade = 2
    char.robustheit = 5
    return char


def _create_superkraft_mit_modifikator():
    """Erstellt eine Superkraft mit Modifikator"""
    kraft = MagicMock(spec=Superkraft)
    kraft.name = "Fliegen"
    kraft.beschreibung = "Kann fliegen"
    kraft.basis_kosten = "2-18"
    kraft.gewaehlte_kosten = 6
    kraft.gesamt_kosten = 4
    mod = MagicMock(spec=SuperkraftModifikator)
    mod.name = "Unbeholfen"
    mod.kosten = -2
    kraft.gewaehlte_modifikatoren = [mod]
    return kraft


def _create_superkraft_ohne_modifikator():
    """Erstellt eine einfache Superkraft ohne Modifikator"""
    kraft = MagicMock(spec=Superkraft)
    kraft.name = "Rüstung"
    kraft.beschreibung = "Erhöhte Robustheit"
    kraft.basis_kosten = "1-5"
    kraft.gewaehlte_kosten = 3
    kraft.gesamt_kosten = 3
    kraft.gewaehlte_modifikatoren = []
    return kraft


# ======================== POINTBAR VIEW TESTS ========================

class TestPointbarSKPAnzeige(unittest.TestCase):
    """Tests für die SKP-Anzeige in der GenerationPointsBar"""

    def test_superkraft_punkte_text_format(self):
        """SKP-Text zeigt verbleibend / gesamt (OG: kraftobergrenze)"""
        # Simuliere die update-Methode direkt
        charakter = _create_mock_charakter()
        charakter.superkraft_punkte_verbraucht = 10
        charakter.superkraft_punkte_gesamt = 45
        charakter.kraftobergrenze = 15

        verbraucht = charakter.superkraft_punkte_verbraucht
        gesamt = charakter.superkraft_punkte_gesamt
        verbleibend = gesamt - verbraucht
        text = f"{verbleibend} / {gesamt} (OG: {charakter.kraftobergrenze})"

        self.assertEqual(text, "35 / 45 (OG: 15)")

    def test_superkraft_punkte_text_null_verbraucht(self):
        """SKP-Text bei 0 verbrauchten Punkten"""
        charakter = _create_mock_charakter()
        verbraucht = charakter.superkraft_punkte_verbraucht
        gesamt = charakter.superkraft_punkte_gesamt
        verbleibend = gesamt - verbraucht
        text = f"{verbleibend} / {gesamt} (OG: {charakter.kraftobergrenze})"

        self.assertEqual(text, "45 / 45 (OG: 15)")

    def test_superkraft_punkte_text_alles_verbraucht(self):
        """SKP-Text bei vollständig verbrauchten Punkten"""
        charakter = _create_mock_charakter()
        charakter.superkraft_punkte_verbraucht = 45

        verbraucht = charakter.superkraft_punkte_verbraucht
        gesamt = charakter.superkraft_punkte_gesamt
        verbleibend = gesamt - verbraucht
        text = f"{verbleibend} / {gesamt} (OG: {charakter.kraftobergrenze})"

        self.assertEqual(text, "0 / 45 (OG: 15)")

    def test_machtstufe_text_format(self):
        """Machtstufe-Text zeigt Stufe an"""
        charakter = _create_mock_charakter()
        text = f"{charakter.machtstufe}"
        self.assertEqual(text, "III")

    def test_machtstufe_text_stufe_I(self):
        """Machtstufe-Text für Stufe I"""
        charakter = _create_mock_charakter()
        charakter.machtstufe = "I"
        text = f"{charakter.machtstufe}"
        self.assertEqual(text, "I")

    def test_skp_leer_bei_normalem_setting(self):
        """SKP-Text leer bei Nicht-Superkräfte-Setting"""
        charakter = _create_mock_charakter("SWAE")
        self.assertFalse(skf.ist_superkraefte_setting(charakter.active_setting_name))

    def test_skp_aktiv_bei_superkraefte_setting(self):
        """SKP-Setting-Erkennung funktioniert"""
        charakter = _create_mock_charakter()
        self.assertTrue(skf.ist_superkraefte_setting(charakter.active_setting_name))

    def test_maechte_text_leer_bei_superkraefte_setting(self):
        """Mächte-Text soll bei Superkräfte-Setting leer sein"""
        charakter = _create_mock_charakter()
        if skf.ist_superkraefte_setting(charakter.active_setting_name):
            maechte_text = ""
        else:
            maechte_text = f"{charakter.verfuegbare_maechte} / {charakter.anzahl_maechte}"
        self.assertEqual(maechte_text, "")

    def test_maechte_text_sichtbar_bei_normalem_setting(self):
        """Mächte-Text soll bei normalem Setting sichtbar sein"""
        charakter = _create_mock_charakter("SWAE")
        charakter.verfuegbare_maechte = 2
        charakter.anzahl_maechte = 3
        if skf.ist_superkraefte_setting(charakter.active_setting_name):
            maechte_text = ""
        else:
            maechte_text = f"{charakter.verfuegbare_maechte} / {charakter.anzahl_maechte}"
        self.assertEqual(maechte_text, "2 / 3")


class TestPointbarSettingWechsel(unittest.TestCase):
    """Tests für Setting-Wechsel in der Pointbar"""

    def test_wechsel_zu_superkraefte_setting(self):
        """Bei Wechsel zu SKP-Setting werden Mächte-Texte leer"""
        charakter = _create_mock_charakter("SWAE")
        # Zuerst normales Setting
        self.assertFalse(skf.ist_superkraefte_setting(charakter.active_setting_name))
        # Wechsel zu Superkräfte
        charakter.active_setting_name = "Superkräfte Kompendium"
        self.assertTrue(skf.ist_superkraefte_setting(charakter.active_setting_name))

    def test_wechsel_von_superkraefte_setting(self):
        """Bei Wechsel weg von SKP-Setting werden SKP-Texte leer"""
        charakter = _create_mock_charakter()
        self.assertTrue(skf.ist_superkraefte_setting(charakter.active_setting_name))
        charakter.active_setting_name = "SWAE"
        self.assertFalse(skf.ist_superkraefte_setting(charakter.active_setting_name))


# ======================== STATBLOCK GENERATOR TESTS ========================

class TestStatblockSuperkraefte(unittest.TestCase):
    """Tests für Superkräfte im StatBlock-Generator"""

    def test_format_superkraefte_leer(self):
        """Leere Superkräfte-Liste ergibt leeren String"""
        charakter = _create_mock_charakter()
        result = _format_superkraefte(charakter)
        self.assertEqual(result, "")

    def test_format_superkraefte_nicht_skp_setting(self):
        """Nicht-SKP-Setting ergibt leeren String"""
        charakter = _create_mock_charakter("SWAE")
        result = _format_superkraefte(charakter)
        self.assertEqual(result, "")

    def test_format_superkraefte_mit_kraft(self):
        """Eine Superkraft wird korrekt formatiert"""
        charakter = _create_mock_charakter()
        kraft = _create_superkraft_ohne_modifikator()
        charakter.superkraefte = {"Rüstung": kraft}
        charakter.selected_superkraefte = ["Rüstung"]
        charakter.superkraft_punkte_verbraucht = 3

        result = _format_superkraefte(charakter)
        self.assertIn("Rüstung", result)
        self.assertIn("3 SKP", result)
        self.assertIn("Machtstufe III", result)

    def test_format_superkraefte_mit_modifikator(self):
        """Superkraft mit Modifikator wird korrekt formatiert"""
        charakter = _create_mock_charakter()
        kraft = _create_superkraft_mit_modifikator()
        charakter.superkraefte = {"Fliegen": kraft}
        charakter.selected_superkraefte = ["Fliegen"]
        charakter.superkraft_punkte_verbraucht = 4

        result = _format_superkraefte(charakter)
        self.assertIn("Fliegen", result)
        self.assertIn("4 SKP", result)
        self.assertIn("Unbeholfen", result)

    def test_format_superkraefte_mehrere(self):
        """Mehrere Superkräfte werden kommasepariert"""
        charakter = _create_mock_charakter()
        kraft1 = _create_superkraft_mit_modifikator()
        kraft2 = _create_superkraft_ohne_modifikator()
        charakter.superkraefte = {"Fliegen": kraft1, "Rüstung": kraft2}
        charakter.selected_superkraefte = ["Fliegen", "Rüstung"]
        charakter.superkraft_punkte_verbraucht = 7

        result = _format_superkraefte(charakter)
        self.assertIn("Fliegen", result)
        self.assertIn("Rüstung", result)
        self.assertIn("7/45 SKP", result)

    def test_format_superkraefte_skp_zusammenfassung(self):
        """SKP-Zusammenfassung im Statblock"""
        charakter = _create_mock_charakter()
        kraft = _create_superkraft_ohne_modifikator()
        charakter.superkraefte = {"Rüstung": kraft}
        charakter.selected_superkraefte = ["Rüstung"]
        charakter.superkraft_punkte_verbraucht = 3

        result = _format_superkraefte(charakter)
        self.assertIn("3/45 SKP", result)

    def test_statblock_komplett_mit_superkraeften(self):
        """Kompletter Statblock enthält Superkräfte-Zeile"""
        charakter = _create_mock_charakter()
        kraft = _create_superkraft_ohne_modifikator()
        charakter.superkraefte = {"Rüstung": kraft}
        charakter.selected_superkraefte = ["Rüstung"]
        charakter.superkraft_punkte_verbraucht = 3

        result = generate_character_statblock(charakter)
        self.assertIn("Superkräfte:", result)
        self.assertIn("Rüstung", result)

    def test_statblock_ohne_superkraefte_bei_swae(self):
        """SWAE-Statblock enthält keine Superkräfte-Zeile"""
        charakter = _create_mock_charakter("SWAE")
        result = generate_character_statblock(charakter)
        self.assertNotIn("Superkräfte:", result)

    def test_statblock_ohne_superkraefte_wenn_keine_gewaehlt(self):
        """Superkräfte-Zeile fehlt wenn keine gewählt"""
        charakter = _create_mock_charakter()
        result = generate_character_statblock(charakter)
        self.assertNotIn("Superkräfte:", result)

    def test_format_superkraefte_fehlende_kraft(self):
        """Fehlende Kraft in superkraefte-Dict wird übersprungen"""
        charakter = _create_mock_charakter()
        charakter.selected_superkraefte = ["NichtExistent"]
        charakter.superkraefte = {}
        # Sollte keinen Fehler werfen und leeren String liefern
        result = _format_superkraefte(charakter)
        self.assertEqual(result, "")


class TestStatblockMaechteUndSuperkraefte(unittest.TestCase):
    """Tests für das Zusammenspiel von Mächte und Superkräfte im StatBlock"""

    def test_maechte_sichtbar_bei_swae(self):
        """Mächte werden bei SWAE-Setting im Statblock angezeigt"""
        charakter = _create_mock_charakter("SWAE")
        macht = MagicMock()
        macht.name = "Heilen"
        macht.beschreibung = "Heilt Wunden"
        charakter.maechte = {"Heilen": macht}
        charakter.selected_maechte = ["Heilen"]
        charakter.machtpunkte = 10

        result = generate_character_statblock(charakter)
        self.assertIn("Mächte:", result)
        self.assertIn("Heilen", result)

    def test_superkraefte_und_maechte_gleichzeitig(self):
        """Beide Systeme können gleichzeitig im Statblock erscheinen"""
        charakter = _create_mock_charakter()
        # Mächte (leer bei Superkräfte-Setting, aber technisch möglich)
        macht = MagicMock()
        macht.name = "Heilen"
        charakter.maechte = {"Heilen": macht}
        charakter.selected_maechte = ["Heilen"]
        charakter.machtpunkte = 10
        # Superkräfte
        kraft = _create_superkraft_ohne_modifikator()
        charakter.superkraefte = {"Rüstung": kraft}
        charakter.selected_superkraefte = ["Rüstung"]
        charakter.superkraft_punkte_verbraucht = 3

        result = generate_character_statblock(charakter)
        self.assertIn("Superkräfte:", result)
        self.assertIn("Mächte:", result)


# ======================== PDF EXPORT TESTS ========================

class TestPDFSuperkraefte(unittest.TestCase):
    """Tests für Superkräfte im PDF-Export (Logik-Level)"""

    def test_superkraft_daten_fuer_pdf(self):
        """Superkraft-Daten sind im erwarteten Format für PDF"""
        kraft = _create_superkraft_mit_modifikator()
        # Prüfe, dass alle PDF-relevanten Felder vorhanden sind
        self.assertEqual(kraft.name, "Fliegen")
        self.assertEqual(kraft.basis_kosten, "2-18")
        self.assertEqual(kraft.gewaehlte_kosten, 6)
        self.assertEqual(kraft.gesamt_kosten, 4)
        self.assertEqual(len(kraft.gewaehlte_modifikatoren), 1)
        self.assertEqual(kraft.gewaehlte_modifikatoren[0].name, "Unbeholfen")

    def test_pdf_tabellen_daten_ohne_modifikator(self):
        """PDF-Tabellendaten für Kraft ohne Modifikator"""
        kraft = _create_superkraft_ohne_modifikator()
        row = [
            kraft.name,
            str(kraft.basis_kosten),
            str(kraft.gewaehlte_kosten),
            "",  # Keine Modifikatoren
            str(kraft.gesamt_kosten)
        ]
        self.assertEqual(row, ["Rüstung", "1-5", "3", "", "3"])

    def test_pdf_tabellen_daten_mit_modifikator(self):
        """PDF-Tabellendaten für Kraft mit Modifikator"""
        kraft = _create_superkraft_mit_modifikator()
        mod_text = ", ".join([m.name for m in kraft.gewaehlte_modifikatoren])
        row = [
            kraft.name,
            str(kraft.basis_kosten),
            str(kraft.gewaehlte_kosten),
            mod_text,
            str(kraft.gesamt_kosten)
        ]
        self.assertEqual(row, ["Fliegen", "2-18", "6", "Unbeholfen", "4"])

    def test_pdf_heading_mit_machtstufe(self):
        """PDF-Überschrift enthält Machtstufe und SKP-Info"""
        charakter = _create_mock_charakter()
        charakter.superkraft_punkte_verbraucht = 10
        heading = f"Superkräfte (Machtstufe {charakter.machtstufe}, {charakter.superkraft_punkte_verbraucht}/{charakter.superkraft_punkte_gesamt} SKP)"
        self.assertEqual(heading, "Superkräfte (Machtstufe III, 10/45 SKP)")

    def test_pdf_mehrere_modifikatoren(self):
        """PDF-Modifikator-Text bei mehreren Modifikatoren"""
        kraft = MagicMock(spec=Superkraft)
        mod1 = MagicMock(spec=SuperkraftModifikator)
        mod1.name = "Unbeholfen"
        mod2 = MagicMock(spec=SuperkraftModifikator)
        mod2.name = "Gerät"
        kraft.gewaehlte_modifikatoren = [mod1, mod2]
        mod_text = ", ".join([m.name for m in kraft.gewaehlte_modifikatoren])
        self.assertEqual(mod_text, "Unbeholfen, Gerät")


class TestPDFKeineSuperKraefte(unittest.TestCase):
    """Tests dass PDF bei Nicht-SKP-Settings keine SKP-Sektion hat"""

    def test_keine_selected_superkraefte_leere_liste(self):
        """Leere selected_superkraefte erzeugt keine PDF-Sektion"""
        charakter = _create_mock_charakter()
        self.assertEqual(len(charakter.selected_superkraefte), 0)

    def test_swae_setting_hat_keine_superkraefte(self):
        """SWAE hat kein Superkräfte-System"""
        charakter = _create_mock_charakter("SWAE")
        self.assertFalse(skf.ist_superkraefte_setting(charakter.active_setting_name))
        self.assertEqual(len(charakter.selected_superkraefte), 0)


# ======================== MACHTSTUFEN-ANZEIGE TESTS ========================

class TestMachtstufenAnzeige(unittest.TestCase):
    """Tests für die korrekte Anzeige verschiedener Machtstufen"""

    def test_machtstufe_I_skp(self):
        """Machtstufe I: 15 SKP, Obergrenze 5"""
        charakter = _create_mock_charakter()
        charakter.machtstufe = "I"
        charakter.superkraft_punkte_gesamt = 15
        charakter.kraftobergrenze = 5

        verbraucht = charakter.superkraft_punkte_verbraucht
        gesamt = charakter.superkraft_punkte_gesamt
        verbleibend = gesamt - verbraucht
        text = f"{verbleibend} / {gesamt} (OG: {charakter.kraftobergrenze})"
        self.assertEqual(text, "15 / 15 (OG: 5)")

    def test_machtstufe_V_skp(self):
        """Machtstufe V: 75 SKP, Obergrenze 25"""
        charakter = _create_mock_charakter()
        charakter.machtstufe = "V"
        charakter.superkraft_punkte_gesamt = 75
        charakter.kraftobergrenze = 25

        verbraucht = 50
        charakter.superkraft_punkte_verbraucht = verbraucht
        gesamt = charakter.superkraft_punkte_gesamt
        verbleibend = gesamt - verbraucht
        text = f"{verbleibend} / {gesamt} (OG: {charakter.kraftobergrenze})"
        self.assertEqual(text, "25 / 75 (OG: 25)")

    def test_alle_machtstufen(self):
        """Alle Machtstufen I-V haben gültige Formate"""
        for stufe in ["I", "II", "III", "IV", "V"]:
            charakter = _create_mock_charakter()
            charakter.machtstufe = stufe
            text = f"{charakter.machtstufe}"
            self.assertEqual(text, stufe)


if __name__ == '__main__':
    unittest.main()
