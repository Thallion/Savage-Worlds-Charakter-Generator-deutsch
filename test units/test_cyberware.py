# test units/test_cyberware.py
"""
Tests für das Cyberware-System (Sprint 1: Grundlagen).
Testet:
- CyberwareInstallation Model (models/cyberware.py)
- Cyberware-Funktionen (functions/cyberware_funktionen.py)
- Charakter-Integration (Properties, Persistenz, abgeleitete Werte)
"""
import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch, PropertyMock

# Kivy-Headless-Modus
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_LOG_LEVEL'] = 'critical'

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cyberware import CyberwareInstallation
from models.wuerfel import Wuerfel
import functions.cyberware_funktionen as cwf


# ======================== CYBERWARE INSTALLATION MODEL TESTS ========================

class TestCyberwareInstallation(unittest.TestCase):
    """Tests für die CyberwareInstallation-Klasse"""

    def test_erstellen_standard(self):
        """Neue Installation hat korrekte Standardwerte."""
        inst = CyberwareInstallation()
        self.assertEqual(inst.name, "")
        self.assertEqual(inst.stress, 0)
        self.assertEqual(inst.max_installationen, -1)
        self.assertFalse(inst.installiert)
        self.assertTrue(inst.aktiv)
        self.assertNotEqual(inst.installations_id, "")
        self.assertEqual(inst.konfiguration, {})

    def test_erstellen_mit_werten(self):
        """Installation mit expliziten Werten."""
        inst = CyberwareInstallation(
            name="Cyberware: Panzerung",
            beschreibung="Subdermale Platten",
            unterkategorie="Defensiv",
            stress=1,
            max_installationen=3,
            kosten=5000,
            effekte={"panzerung_bonus": 2}
        )
        self.assertEqual(inst.name, "Cyberware: Panzerung")
        self.assertEqual(inst.unterkategorie, "Defensiv")
        self.assertEqual(inst.stress, 1)
        self.assertEqual(inst.max_installationen, 3)
        self.assertEqual(inst.kosten, 5000)
        self.assertEqual(inst.effekte['panzerung_bonus'], 2)

    def test_to_dict(self):
        """Serialisierung enthält alle Felder."""
        inst = CyberwareInstallation(
            name="Test",
            stress=2,
            kosten=5000,
            effekte={"test": True}
        )
        inst.installiert = True
        inst.konfiguration = {"attribut": "Stärke"}

        d = inst.to_dict()
        self.assertEqual(d['name'], "Test")
        self.assertEqual(d['stress'], 2)
        self.assertEqual(d['kosten'], 5000)
        self.assertTrue(d['installiert'])
        self.assertEqual(d['konfiguration']['attribut'], "Stärke")
        self.assertEqual(d['effekte']['test'], True)

    def test_from_dict_roundtrip(self):
        """Serialisierung und Deserialisierung sind identisch."""
        original = CyberwareInstallation(
            name="Cyberware: Robustheit",
            beschreibung="+1 Robustheit",
            unterkategorie="Defensiv",
            stress=1,
            max_installationen=3,
            kosten=5000,
            effekte={"robustheit_bonus": 1}
        )
        original.installiert = True
        original.konfiguration = {"test": "wert"}

        d = original.to_dict()
        geladen = CyberwareInstallation.from_dict(d)

        self.assertEqual(geladen.name, original.name)
        self.assertEqual(geladen.stress, original.stress)
        self.assertEqual(geladen.max_installationen, original.max_installationen)
        self.assertEqual(geladen.kosten, original.kosten)
        self.assertTrue(geladen.installiert)
        self.assertEqual(geladen.konfiguration['test'], "wert")
        self.assertEqual(geladen.effekte['robustheit_bonus'], 1)

    def test_from_setting_dict(self):
        """Erstellen aus Setting-JSON-Format."""
        setting_data = {
            "name": "Cyberware: Schmerzhemmer",
            "kategorie": "Cyberware",
            "unterkategorie": "Defensiv",
            "gewicht": 0,
            "kosten": 5000,
            "stress": 2,
            "max_installationen": 3,
            "setting": "scifi",
            "beschreibung": "Ignoriert 1 Punkt Wund-/Erschöpfungsabzüge",
            "effekte": {"wund_ignorieren": 1},
            "aktiv": True
        }
        inst = CyberwareInstallation.from_setting_dict(setting_data)
        self.assertEqual(inst.name, "Cyberware: Schmerzhemmer")
        self.assertEqual(inst.stress, 2)
        self.assertEqual(inst.max_installationen, 3)
        self.assertEqual(inst.kosten, 5000)
        self.assertEqual(inst.effekte['wund_ignorieren'], 1)
        self.assertFalse(inst.installiert)  # Aus Setting = nicht installiert

    def test_str_repr(self):
        """String-Repräsentationen sind informativ."""
        inst = CyberwareInstallation(name="Test", stress=2)
        self.assertIn("Test", str(inst))
        self.assertIn("2", str(inst))
        self.assertIn("Test", repr(inst))


# ======================== CYBERWARE FUNKTIONEN TESTS ========================

def _erstelle_mock_charakter(willenskraft=6, konstitution=6,
                              selected_talente=None, selected_handicaps=None):
    """Erstellt einen Mock-Charakter für Cyberware-Tests."""
    charakter = MagicMock()
    charakter.active_setting_name = "SciFi Kompendium"

    # Attribute
    attr_will = MagicMock()
    attr_will.wert = willenskraft
    attr_kon = MagicMock()
    attr_kon.wert = konstitution
    charakter.attribute = {
        'Willenskraft': attr_will,
        'Konstitution': attr_kon
    }

    # Talente
    charakter.selected_talente = selected_talente or []
    charakter.talente = {}
    for name in charakter.selected_talente:
        talent = MagicMock()
        talent.cyberware_effekte = cwf._get_bekannte_talent_effekte(name)
        charakter.talente[name] = talent

    # Handicaps
    charakter.selected_handicaps = selected_handicaps or []
    charakter.handicaps = {}
    for name in charakter.selected_handicaps:
        handicap = MagicMock()
        handicap.cyberware_effekte = cwf._get_bekannte_handicap_effekte(name)
        charakter.handicaps[name] = handicap

    # Cyberware
    charakter.cyberware_verfuegbar = {}
    charakter.cyberware_installationen = {}
    charakter.cyberware_stress_aktuell = 0
    charakter.cyberware_stresslimit = 0
    charakter.cyberware_stress_maximum = 0
    charakter.selected_cyberware = []

    return charakter


class TestCyberwareFunktionen(unittest.TestCase):
    """Tests für die Cyberware-Kernlogik"""

    def test_ist_cyberware_setting(self):
        """SciFi Kompendium ist ein Cyberware-Setting."""
        self.assertTrue(cwf.ist_cyberware_setting("SciFi Kompendium"))
        self.assertFalse(cwf.ist_cyberware_setting("SWAE"))
        self.assertFalse(cwf.ist_cyberware_setting("Deadlands"))

    def test_stresslimit_basis(self):
        """Stresslimit = min(Wil, Kon) / 2."""
        charakter = _erstelle_mock_charakter(willenskraft=8, konstitution=6)
        # min(8, 6) / 2 = 3
        self.assertEqual(cwf.berechne_stresslimit(charakter), 3)

    def test_stresslimit_gleiche_attribute(self):
        """Stresslimit bei gleichen Attributen."""
        charakter = _erstelle_mock_charakter(willenskraft=8, konstitution=8)
        # min(8, 8) / 2 = 4
        self.assertEqual(cwf.berechne_stresslimit(charakter), 4)

    def test_stresslimit_mit_talent_bonus(self):
        """Kybernetische Toleranz erhöht Stresslimit um +2."""
        charakter = _erstelle_mock_charakter(
            willenskraft=8, konstitution=6,
            selected_talente=["Kybernetische Toleranz"]
        )
        # min(8, 6) / 2 + 2 = 5
        self.assertEqual(cwf.berechne_stresslimit(charakter), 5)

    def test_stresslimit_mit_cyber_samurai(self):
        """Cyber-Samurai + Toleranz = +4 auf Stresslimit."""
        charakter = _erstelle_mock_charakter(
            willenskraft=8, konstitution=6,
            selected_talente=["Kybernetische Toleranz", "Cyber-Samurai"]
        )
        # min(8, 6) / 2 + 2 + 2 = 7
        self.assertEqual(cwf.berechne_stresslimit(charakter), 7)

    def test_stresslimit_mit_cyborg(self):
        """Cyborg erhöht Stresslimit um +4."""
        charakter = _erstelle_mock_charakter(
            willenskraft=6, konstitution=6,
            selected_talente=["Cyborg"]
        )
        # min(6, 6) / 2 + 4 = 7
        self.assertEqual(cwf.berechne_stresslimit(charakter), 7)

    def test_stresslimit_mit_handicap_malus(self):
        """Kybernetische Abstoßung reduziert Stresslimit um 2."""
        charakter = _erstelle_mock_charakter(
            willenskraft=8, konstitution=6,
            selected_handicaps=["Kybernetische Abstoßung"]
        )
        # min(8, 6) / 2 - 2 = 1
        self.assertEqual(cwf.berechne_stresslimit(charakter), 1)

    def test_stresslimit_nicht_unter_null(self):
        """Stresslimit kann nicht unter 0 fallen."""
        charakter = _erstelle_mock_charakter(
            willenskraft=4, konstitution=4,
            selected_handicaps=["Kybernetische Abstoßung"]
        )
        # min(4, 4) / 2 - 2 = 0
        self.assertEqual(cwf.berechne_stresslimit(charakter), 0)

    def test_stress_maximum_basis(self):
        """Stress-Maximum = min(Wil, Kon)."""
        charakter = _erstelle_mock_charakter(willenskraft=8, konstitution=6)
        # min(8, 6) = 6
        self.assertEqual(cwf.berechne_stress_maximum(charakter), 6)

    def test_stress_maximum_mit_talent(self):
        """Kybernetische Toleranz erhöht Maximum um +2."""
        charakter = _erstelle_mock_charakter(
            willenskraft=8, konstitution=6,
            selected_talente=["Kybernetische Toleranz"]
        )
        # min(8, 6) + 2 = 8
        self.assertEqual(cwf.berechne_stress_maximum(charakter), 8)

    def test_stress_aktuell_leer(self):
        """Ohne Installationen ist Stress 0."""
        charakter = _erstelle_mock_charakter()
        self.assertEqual(cwf.berechne_stress_aktuell(charakter), 0)

    def test_stress_aktuell_mit_installationen(self):
        """Stress summiert sich aus installierten Cyberware."""
        charakter = _erstelle_mock_charakter()
        inst1 = CyberwareInstallation(name="A", stress=2)
        inst1.installiert = True
        inst2 = CyberwareInstallation(name="B", stress=3)
        inst2.installiert = True
        charakter.cyberware_installationen = {"1": inst1, "2": inst2}
        self.assertEqual(cwf.berechne_stress_aktuell(charakter), 5)


class TestCyberwareInstallation_Funktionen(unittest.TestCase):
    """Tests für Installation/Deinstallation"""

    def setUp(self):
        self.charakter = _erstelle_mock_charakter(willenskraft=8, konstitution=6)
        # Verfügbare Cyberware eintragen
        panzerung = CyberwareInstallation(
            name="Cyberware: Panzerung",
            stress=1,
            max_installationen=3,
            kosten=5000,
            effekte={"panzerung_bonus": 2}
        )
        aktion = CyberwareInstallation(
            name="Cyberware: Zusätzliche Aktion",
            stress=5,
            max_installationen=1,
            kosten=10000,
            effekte={"mehrfachaktion_ignorieren": 2}
        )
        self.charakter.cyberware_verfuegbar = {
            "Cyberware: Panzerung": panzerung,
            "Cyberware: Zusätzliche Aktion": aktion,
        }

    def test_initialisiere_cyberware(self):
        """Cyberware wird aus Ausrüstungsdaten gefiltert."""
        charakter = _erstelle_mock_charakter()
        ausruestung = {
            "Cyberware: Panzerung": {
                "name": "Cyberware: Panzerung",
                "kategorie": "Cyberware",
                "stress": 1,
                "max_installationen": 3,
                "kosten": 5000,
                "effekte": {"panzerung_bonus": 2}
            },
            "Lasergewehr": {
                "name": "Lasergewehr",
                "kategorie": "Waffe",
                "kosten": 3000,
            }
        }
        cwf.initialisiere_cyberware(charakter, ausruestung)
        self.assertEqual(len(charakter.cyberware_verfuegbar), 1)
        self.assertIn("Cyberware: Panzerung", charakter.cyberware_verfuegbar)

    def test_validiere_installation_ok(self):
        """Gültige Installation wird akzeptiert."""
        ok, msg = cwf.validiere_installation(self.charakter, "Cyberware: Panzerung")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_validiere_installation_nicht_vorhanden(self):
        """Nicht vorhandene Cyberware wird abgelehnt."""
        ok, msg = cwf.validiere_installation(self.charakter, "Cyberware: Nichtexistent")
        self.assertFalse(ok)
        self.assertIn("nicht verfügbar", msg)

    def test_validiere_installation_stress_ueberschritten(self):
        """Installation über Stress-Maximum wird abgelehnt."""
        # Maximum ist min(8, 6) = 6, Zusätzliche Aktion hat Stress 5
        # Erst installiere etwas mit Stress 2 um nahe ans Maximum zu kommen
        inst = CyberwareInstallation(name="X", stress=2)
        inst.installiert = True
        self.charakter.cyberware_installationen = {"x": inst}
        # Jetzt haben wir Stress 2, Maximum 6, Zusätzliche Aktion hat 5 → 2+5=7 > 6
        ok, msg = cwf.validiere_installation(self.charakter, "Cyberware: Zusätzliche Aktion")
        self.assertFalse(ok)
        self.assertIn("Maximum", msg)

    def test_installiere_cyberware_erfolgreich(self):
        """Erfolgreiche Installation."""
        ok, msg = cwf.installiere_cyberware(self.charakter, "Cyberware: Panzerung")
        self.assertTrue(ok)
        self.assertIn("erfolgreich", msg)
        self.assertEqual(len(self.charakter.cyberware_installationen), 1)

    def test_installiere_cyberware_mit_konfiguration(self):
        """Installation mit Konfiguration (z.B. Attributerhöhung)."""
        attr = CyberwareInstallation(
            name="Cyberware: Attributerhöhung",
            stress=2,
            max_installationen=-1,
            kosten=5000,
            effekte={"attribut_erhoehung": True}
        )
        self.charakter.cyberware_verfuegbar["Cyberware: Attributerhöhung"] = attr

        ok, msg = cwf.installiere_cyberware(
            self.charakter, "Cyberware: Attributerhöhung",
            konfiguration={"attribut": "Stärke"}
        )
        self.assertTrue(ok)
        # Prüfe dass Konfiguration gespeichert wurde
        inst = list(self.charakter.cyberware_installationen.values())[0]
        self.assertEqual(inst.konfiguration['attribut'], "Stärke")

    def test_installiere_max_erreicht(self):
        """Max-Installationen werden respektiert."""
        # Panzerung hat max_installationen=3, also 3× installieren
        for i in range(3):
            ok, _ = cwf.installiere_cyberware(self.charakter, "Cyberware: Panzerung")
            self.assertTrue(ok)
        # 4. Installation sollte fehlschlagen
        ok, msg = cwf.installiere_cyberware(self.charakter, "Cyberware: Panzerung")
        self.assertFalse(ok)
        self.assertIn("Maximum", msg)

    def test_deinstalliere_cyberware(self):
        """Deinstallation entfernt die Cyberware."""
        cwf.installiere_cyberware(self.charakter, "Cyberware: Panzerung")
        inst_id = list(self.charakter.cyberware_installationen.keys())[0]

        ok, msg, kosten = cwf.deinstalliere_cyberware(self.charakter, inst_id)
        self.assertTrue(ok)
        self.assertEqual(kosten, 1250)  # 5000 * 0.25
        self.assertEqual(len(self.charakter.cyberware_installationen), 0)

    def test_deinstalliere_nicht_vorhanden(self):
        """Deinstallation nicht vorhandener ID schlägt fehl."""
        ok, msg, kosten = cwf.deinstalliere_cyberware(self.charakter, "fake-id")
        self.assertFalse(ok)
        self.assertEqual(kosten, 0)

    def test_nebenwirkungen_berechnung(self):
        """Nebenwirkungen werden korrekt erkannt."""
        charakter = _erstelle_mock_charakter(willenskraft=6, konstitution=6)
        # Stresslimit = 3, Maximum = 6
        # Installiere 4 Stress → über Limit
        inst = CyberwareInstallation(name="X", stress=4)
        inst.installiert = True
        charakter.cyberware_installationen = {"x": inst}

        result = cwf.berechne_nebenwirkungen(charakter)
        self.assertTrue(result['hat_nebenwirkungen'])
        self.assertEqual(result['ueber_limit'], 1)  # 4 - 3 = 1
        self.assertFalse(result['ueber_maximum'])  # 4 <= 6

    def test_get_installierte_cyberware(self):
        """Nur installierte Cyberware wird zurückgegeben."""
        inst1 = CyberwareInstallation(name="A", stress=1)
        inst1.installiert = True
        inst2 = CyberwareInstallation(name="B", stress=2)
        inst2.installiert = False
        charakter = _erstelle_mock_charakter()
        charakter.cyberware_installationen = {"1": inst1, "2": inst2}

        installiert = cwf.get_installierte_cyberware(charakter)
        self.assertEqual(len(installiert), 1)
        self.assertEqual(installiert[0].name, "A")

    def test_get_aktive_cyberware(self):
        """Nur aktive + installierte Cyberware wird zurückgegeben."""
        inst1 = CyberwareInstallation(name="A", stress=1)
        inst1.installiert = True
        inst1.aktiv = True
        inst2 = CyberwareInstallation(name="B", stress=2)
        inst2.installiert = True
        inst2.aktiv = False
        charakter = _erstelle_mock_charakter()
        charakter.cyberware_installationen = {"1": inst1, "2": inst2}

        aktive = cwf.get_aktive_cyberware(charakter)
        self.assertEqual(len(aktive), 1)
        self.assertEqual(aktive[0].name, "A")


# ======================== SETTING JSON TESTS ========================

class TestSciFiKompendiumJSON(unittest.TestCase):
    """Tests für die SciFi Kompendium JSON-Daten."""

    @classmethod
    def setUpClass(cls):
        """Lade SciFi Kompendium JSON einmalig."""
        json_pfad = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'settings', 'SciFi Kompendium.json'
        )
        with open(json_pfad, 'r', encoding='utf-8') as f:
            cls.setting_data = json.load(f)

    def test_cyberware_items_vorhanden(self):
        """Mindestens 40 Cyberware-Items sind in der Ausrüstung."""
        ausruestung = self.setting_data.get('ausruestung', {})
        cyberware = {k: v for k, v in ausruestung.items()
                     if v.get('kategorie') == 'Cyberware'}
        self.assertGreaterEqual(len(cyberware), 40)

    def test_cyberware_items_haben_stress_feld(self):
        """Alle Cyberware-Items haben ein 'stress'-Feld."""
        ausruestung = self.setting_data.get('ausruestung', {})
        for name, item in ausruestung.items():
            if item.get('kategorie') == 'Cyberware':
                self.assertIn('stress', item,
                              f"'{name}' fehlt das 'stress'-Feld")

    def test_cyberware_items_haben_max_installationen(self):
        """Alle Cyberware-Items haben ein 'max_installationen'-Feld."""
        ausruestung = self.setting_data.get('ausruestung', {})
        for name, item in ausruestung.items():
            if item.get('kategorie') == 'Cyberware':
                self.assertIn('max_installationen', item,
                              f"'{name}' fehlt 'max_installationen'")

    def test_cyberware_items_haben_unterkategorie(self):
        """Alle Cyberware-Items haben eine 'unterkategorie'."""
        ausruestung = self.setting_data.get('ausruestung', {})
        erlaubte = {"Körper", "Defensiv", "Offensiv", "Fortbewegung"}
        for name, item in ausruestung.items():
            if item.get('kategorie') == 'Cyberware':
                self.assertIn('unterkategorie', item,
                              f"'{name}' fehlt 'unterkategorie'")
                self.assertIn(item['unterkategorie'], erlaubte,
                              f"'{name}' hat ungültige Unterkategorie '{item['unterkategorie']}'")

    def test_cyberware_items_haben_effekte(self):
        """Alle Cyberware-Items haben ein 'effekte'-Feld."""
        ausruestung = self.setting_data.get('ausruestung', {})
        for name, item in ausruestung.items():
            if item.get('kategorie') == 'Cyberware':
                self.assertIn('effekte', item,
                              f"'{name}' fehlt das 'effekte'-Feld")

    def test_talente_haben_cyberware_effekte(self):
        """Cyberware-Talente haben 'cyberware_effekte'."""
        talente = self.setting_data.get('talente', {})
        for talent_name in ['Kybernetische Toleranz', 'Cyber-Samurai', 'Cyborg']:
            self.assertIn(talent_name, talente, f"Talent '{talent_name}' fehlt")
            self.assertIn('cyberware_effekte', talente[talent_name],
                          f"Talent '{talent_name}' fehlt 'cyberware_effekte'")

    def test_handicaps_haben_cyberware_effekte(self):
        """Cyberware-Handicaps haben 'cyberware_effekte'."""
        handicaps = self.setting_data.get('handicaps', {})
        for handicap_name in ['Kybernetische Abstoßung', 'Kybernetische Empfindlichkeit',
                               'Kybernetische Nebenwirkungen']:
            self.assertIn(handicap_name, handicaps, f"Handicap '{handicap_name}' fehlt")
            self.assertIn('cyberware_effekte', handicaps[handicap_name],
                          f"Handicap '{handicap_name}' fehlt 'cyberware_effekte'")

    def test_nebenwirkungen_tabelle_vorhanden(self):
        """Die Nebenwirkungen-Tabelle existiert und hat alle Einträge."""
        self.assertIn('cyberware_nebenwirkungen', self.setting_data)
        nebenwirkungen = self.setting_data['cyberware_nebenwirkungen']
        # Soll W20-Ergebnisse 1-20 abdecken
        self.assertGreaterEqual(len(nebenwirkungen), 12)
        # Prüfe einige bekannte Einträge
        self.assertIn('1', nebenwirkungen)
        self.assertIn('20', nebenwirkungen)
        self.assertEqual(nebenwirkungen['1']['name'], 'Systemüberlastung')
        self.assertEqual(nebenwirkungen['20']['name'], 'Innere Blutungen')

    def test_stressfreie_cyberware(self):
        """Kommunikation, EMP-Abschirmung und Ersatzgliedmaße (geklont) haben Stress 0."""
        ausruestung = self.setting_data.get('ausruestung', {})
        stressfreie = ['Cyberware: Kommunikation', 'Cyberware: EMP-Abschirmung',
                       'Cyberware: Ersatzgliedmaße (geklont)']
        for name in stressfreie:
            self.assertIn(name, ausruestung, f"'{name}' fehlt in Ausrüstung")
            self.assertEqual(ausruestung[name]['stress'], 0,
                            f"'{name}' sollte Stress 0 haben")

    def test_bekannte_items_korrekt(self):
        """Prüfe spezifische Items auf korrekte Werte."""
        ausruestung = self.setting_data.get('ausruestung', {})

        # Panzerung: Stress 1, Max 3, 5000 Kosten
        panzerung = ausruestung['Cyberware: Panzerung']
        self.assertEqual(panzerung['stress'], 1)
        self.assertEqual(panzerung['max_installationen'], 3)
        self.assertEqual(panzerung['kosten'], 5000)

        # Zusätzliche Aktion: Stress 5, Max 1, 10000 Kosten
        aktion = ausruestung['Cyberware: Zusätzliche Aktion']
        self.assertEqual(aktion['stress'], 5)
        self.assertEqual(aktion['max_installationen'], 1)
        self.assertEqual(aktion['kosten'], 10000)

        # Beinverbesserung: Stress 2, Max -1, 10000 Kosten
        bein = ausruestung['Cyberware: Beinverbesserung']
        self.assertEqual(bein['stress'], 2)
        self.assertEqual(bein['max_installationen'], -1)
        self.assertEqual(bein['kosten'], 10000)


# ======================== INTEGRATION TESTS ========================

class TestCyberwareIntegration(unittest.TestCase):
    """Integrationstests für das Cyberware-System."""

    def test_persistenz_roundtrip(self):
        """Cyberware-Installationen überleben Speichern/Laden."""
        # Erstelle Installation
        original = CyberwareInstallation(
            name="Cyberware: Panzerung",
            stress=1,
            max_installationen=3,
            kosten=5000,
            effekte={"panzerung_bonus": 2}
        )
        original.installiert = True
        original.installations_datum = "2026-02-25"
        original.konfiguration = {}

        # Serialisierung
        data = original.to_dict()
        json_str = json.dumps(data, ensure_ascii=False)

        # Deserialisierung
        geladen_data = json.loads(json_str)
        geladen = CyberwareInstallation.from_dict(geladen_data)

        self.assertEqual(geladen.name, "Cyberware: Panzerung")
        self.assertEqual(geladen.stress, 1)
        self.assertTrue(geladen.installiert)
        self.assertEqual(geladen.installations_datum, "2026-02-25")
        self.assertEqual(geladen.effekte['panzerung_bonus'], 2)

    def test_komplettes_stressbeispiel_aus_regelbuch(self):
        """Regelbeispiel: Wil W8, Kon W6 → Limit 3, Maximum 6."""
        charakter = _erstelle_mock_charakter(willenskraft=8, konstitution=6)
        self.assertEqual(cwf.berechne_stresslimit(charakter), 3)
        self.assertEqual(cwf.berechne_stress_maximum(charakter), 6)

    def test_talent_kombination_maximal(self):
        """Alle drei Talente zusammen: +8 auf Limit und Maximum."""
        charakter = _erstelle_mock_charakter(
            willenskraft=8, konstitution=8,
            selected_talente=["Kybernetische Toleranz", "Cyber-Samurai", "Cyborg"]
        )
        # Limit: min(8,8)/2 + 2 + 2 + 4 = 12
        self.assertEqual(cwf.berechne_stresslimit(charakter), 12)
        # Maximum: min(8,8) + 2 + 2 + 4 = 16
        self.assertEqual(cwf.berechne_stress_maximum(charakter), 16)


# ======================== CYBERWARE EFFEKTE TESTS ========================

def _erstelle_mock_fertigkeit(value=4, modifier=0, grundfertigkeit=True):
    """Erstellt eine Mock-Fertigkeit mit echtem Wuerfel-Objekt."""
    fert = MagicMock()
    fert.wuerfel = Wuerfel(value, modifier=modifier, typ='fertigkeit')
    fert.grundfertigkeit = grundfertigkeit
    fert.wert = value
    return fert


def _erstelle_mock_charakter_mit_fertigkeiten(willenskraft=6, konstitution=6,
                                                staerke=6, geschicklichkeit=6,
                                                verstand=6):
    """Erstellt einen erweiterten Mock-Charakter mit Attributen und echten Wuerfel-Fertigkeiten."""
    charakter = _erstelle_mock_charakter(willenskraft=willenskraft, konstitution=konstitution)

    # Weitere Attribute mit echtem Wuerfel
    attr_str = MagicMock()
    attr_str.wert = staerke
    attr_str.wuerfel = MagicMock()
    attr_str.wuerfel.value = staerke
    attr_ges = MagicMock()
    attr_ges.wert = geschicklichkeit
    attr_ges.wuerfel = MagicMock()
    attr_ges.wuerfel.value = geschicklichkeit
    attr_ver = MagicMock()
    attr_ver.wert = verstand
    attr_ver.wuerfel = MagicMock()
    attr_ver.wuerfel.value = verstand

    # Auch Willenskraft und Konstitution mit wuerfel.value
    charakter.attribute['Willenskraft'].wuerfel = MagicMock()
    charakter.attribute['Willenskraft'].wuerfel.value = willenskraft
    charakter.attribute['Konstitution'].wuerfel = MagicMock()
    charakter.attribute['Konstitution'].wuerfel.value = konstitution

    charakter.attribute['Stärke'] = attr_str
    charakter.attribute['Geschicklichkeit'] = attr_ges
    charakter.attribute['Verstand'] = attr_ver

    # Fertigkeiten mit echten Wuerfel-Objekten
    charakter.fertigkeiten = {
        'Athletik': _erstelle_mock_fertigkeit(6, 0, True),
        'Wahrnehmung': _erstelle_mock_fertigkeit(6, 0, True),
        'Kämpfen': _erstelle_mock_fertigkeit(6, 0, True),
        'Auftreten': _erstelle_mock_fertigkeit(4, -2, False),  # Nicht-Grundfertigkeit: W4-2
        'Überreden': _erstelle_mock_fertigkeit(4, -2, False),  # Nicht-Grundfertigkeit: W4-2
    }

    charakter.berechne_abgeleitete_werte = MagicMock()
    return charakter


class TestCyberwareEffekte(unittest.TestCase):
    """Tests für Cyberware-Effekte (Sprint 2)."""

    def test_appliziere_robustheit_bonus(self):
        """Robustheit-Bonus wird korrekt über abgeleitete Werte berechnet."""
        from functions.abgeleitete_werte import _berechne_cyberware_robustheit_bonus
        charakter = _erstelle_mock_charakter()
        charakter.active_setting_name = "SciFi Kompendium"

        inst = CyberwareInstallation(name="Cyberware: Robustheit", stress=1,
                                      effekte={"robustheit_bonus": 1})
        inst.installiert = True
        inst.aktiv = True
        charakter.cyberware_installationen = {"1": inst}

        bonus = _berechne_cyberware_robustheit_bonus(charakter)
        self.assertEqual(bonus, 1)

    def test_appliziere_panzerung_bonus(self):
        """Natürliche Panzerung wird korrekt über abgeleitete Werte berechnet."""
        from functions.abgeleitete_werte import _berechne_cyberware_natuerliche_panzerung
        charakter = _erstelle_mock_charakter()
        charakter.active_setting_name = "SciFi Kompendium"

        inst = CyberwareInstallation(name="Cyberware: Panzerung", stress=1,
                                      effekte={"panzerung_bonus": 2, "natuerliche_panzerung": True})
        inst.installiert = True
        inst.aktiv = True
        charakter.cyberware_installationen = {"1": inst}

        panzerung = _berechne_cyberware_natuerliche_panzerung(charakter)
        self.assertEqual(panzerung, 2)

    def test_appliziere_bewegungsweite_bonus(self):
        """BW-Bonus wird korrekt über abgeleitete Werte berechnet."""
        from functions.abgeleitete_werte import _berechne_cyberware_bewegungsweite_bonus
        charakter = _erstelle_mock_charakter()
        charakter.active_setting_name = "SciFi Kompendium"

        inst = CyberwareInstallation(name="Cyberware: Beinverbesserung", stress=2,
                                      effekte={"bewegungsweite_bonus": 2})
        inst.installiert = True
        inst.aktiv = True
        charakter.cyberware_installationen = {"1": inst}

        bonus = _berechne_cyberware_bewegungsweite_bonus(charakter)
        self.assertEqual(bonus, 2)

    def test_appliziere_attribut_erhoehung(self):
        """Attributerhöhung steigert den Würfeltyp um eine Stufe."""
        charakter = _erstelle_mock_charakter_mit_fertigkeiten(staerke=6)

        inst = CyberwareInstallation(name="Cyberware: Attributerhöhung", stress=2,
                                      effekte={"attribut_erhoehung": True})
        inst.installiert = True
        inst.konfiguration = {"attribut": "Stärke"}

        cwf.appliziere_cyberware_effekte(charakter, inst)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.value, 8)

    def test_appliziere_fertigkeit_bonus_waehlbar(self):
        """Wählbarer Fertigkeitsbonus erhöht die gewählte Fertigkeit."""
        charakter = _erstelle_mock_charakter_mit_fertigkeiten()

        inst = CyberwareInstallation(
            name="Cyberware: Fertigkeitsbonus", stress=1,
            effekte={"fertigkeit_bonus": {"fertigkeit": "waehlbar", "bonus": 1, "max_bonus": 2}}
        )
        inst.installiert = True
        inst.konfiguration = {"fertigkeit": "Athletik"}

        cwf.appliziere_cyberware_effekte(charakter, inst)
        self.assertEqual(charakter.fertigkeiten['Athletik'].wuerfel.value, 8)

    def test_appliziere_fertigkeit_bonus_fest(self):
        """Fester Fertigkeitsbonus (z.B. Attraktiv) erhöht benannte Fertigkeiten.
        Auftreten/Überreden starten bei W4-2 → +1 setzt Modifier auf 0 (nicht Würfeltyp hoch)."""
        charakter = _erstelle_mock_charakter_mit_fertigkeiten()
        # Prüfe Ausgangslage: W4-2
        self.assertEqual(charakter.fertigkeiten['Auftreten'].wuerfel.value, 4)
        self.assertEqual(charakter.fertigkeiten['Auftreten'].wuerfel.modifier, -2)

        inst = CyberwareInstallation(
            name="Cyberware: Attraktiv", stress=1,
            effekte={"fertigkeit_bonus": {"fertigkeiten": ["Auftreten", "Überreden"], "bonus": 1, "max_bonus": 2}}
        )
        inst.installiert = True

        cwf.appliziere_cyberware_effekte(charakter, inst)
        # W4-2 + 1 increase → W4 (modifier 0)
        self.assertEqual(charakter.fertigkeiten['Auftreten'].wuerfel.value, 4)
        self.assertEqual(charakter.fertigkeiten['Auftreten'].wuerfel.modifier, 0)
        self.assertEqual(charakter.fertigkeiten['Überreden'].wuerfel.value, 4)
        self.assertEqual(charakter.fertigkeiten['Überreden'].wuerfel.modifier, 0)

    def test_appliziere_talent_gewaehrt(self):
        """Talent wird zu selected_talente hinzugefügt."""
        charakter = _erstelle_mock_charakter_mit_fertigkeiten()
        charakter.selected_talente = []

        inst = CyberwareInstallation(
            name="Cyberware: Bedrohungseinschätzer", stress=2,
            effekte={"talent_gewaehrt": "Sechster Sinn"}
        )
        inst.installiert = True

        cwf.appliziere_cyberware_effekte(charakter, inst)
        self.assertIn("Sechster Sinn", charakter.selected_talente)

    def test_entferne_effekte_bei_deinstallation(self):
        """Alle Effekte werden bei Deinstallation rückgängig gemacht."""
        charakter = _erstelle_mock_charakter_mit_fertigkeiten(staerke=8)
        charakter.selected_talente = []

        # Attributerhöhung
        inst_attr = CyberwareInstallation(
            name="Cyberware: Attributerhöhung", stress=2,
            effekte={"attribut_erhoehung": True}
        )
        inst_attr.installiert = True
        inst_attr.konfiguration = {"attribut": "Stärke"}

        # Talent
        inst_talent = CyberwareInstallation(
            name="Cyberware: Bedrohungseinschätzer", stress=2,
            effekte={"talent_gewaehrt": "Sechster Sinn"}
        )
        inst_talent.installiert = True

        # Anwenden
        cwf.appliziere_cyberware_effekte(charakter, inst_attr)
        cwf.appliziere_cyberware_effekte(charakter, inst_talent)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.value, 10)
        self.assertIn("Sechster Sinn", charakter.selected_talente)

        # Entfernen
        cwf.entferne_cyberware_effekte(charakter, inst_attr)
        cwf.entferne_cyberware_effekte(charakter, inst_talent)
        self.assertEqual(charakter.attribute['Stärke'].wuerfel.value, 8)
        self.assertNotIn("Sechster Sinn", charakter.selected_talente)

    def test_braucht_konfiguration_attribut(self):
        """Attributerhöhung braucht Konfiguration."""
        charakter = _erstelle_mock_charakter()
        attr = CyberwareInstallation(
            name="Cyberware: Attributerhöhung", stress=2,
            effekte={"attribut_erhoehung": True}
        )
        charakter.cyberware_verfuegbar = {"Cyberware: Attributerhöhung": attr}

        result = cwf.braucht_konfiguration("Cyberware: Attributerhöhung", charakter)
        self.assertIsNotNone(result)
        self.assertEqual(result['typ'], 'attribut')
        self.assertIn('Stärke', result['optionen'])

    def test_braucht_konfiguration_nicht_bei_panzerung(self):
        """Panzerung braucht keine Konfiguration."""
        charakter = _erstelle_mock_charakter()
        panzerung = CyberwareInstallation(
            name="Cyberware: Panzerung", stress=1,
            effekte={"panzerung_bonus": 2, "natuerliche_panzerung": True}
        )
        charakter.cyberware_verfuegbar = {"Cyberware: Panzerung": panzerung}

        result = cwf.braucht_konfiguration("Cyberware: Panzerung", charakter)
        self.assertIsNone(result)

    def test_mehrfache_robustheit_kumulativ(self):
        """3× Robustheit = +3 Robustheit-Bonus."""
        from functions.abgeleitete_werte import _berechne_cyberware_robustheit_bonus
        charakter = _erstelle_mock_charakter()
        charakter.active_setting_name = "SciFi Kompendium"

        installationen = {}
        for i in range(3):
            inst = CyberwareInstallation(name="Cyberware: Robustheit", stress=1,
                                          effekte={"robustheit_bonus": 1})
            inst.installiert = True
            inst.aktiv = True
            installationen[str(i)] = inst
        charakter.cyberware_installationen = installationen

        bonus = _berechne_cyberware_robustheit_bonus(charakter)
        self.assertEqual(bonus, 3)

    def test_appliziere_athletik_bonus(self):
        """Athletik-Bonus wird direkt angewendet."""
        charakter = _erstelle_mock_charakter_mit_fertigkeiten()

        inst = CyberwareInstallation(
            name="Cyberware: Zusätzliche Gliedmaßen", stress=2,
            effekte={"athletik_bonus": 1}
        )
        inst.installiert = True

        cwf.appliziere_cyberware_effekte(charakter, inst)
        self.assertEqual(charakter.fertigkeiten['Athletik'].wuerfel.value, 8)

    def test_appliziere_wahrnehmung_bonus(self):
        """Wahrnehmung-Bonus wird direkt angewendet."""
        charakter = _erstelle_mock_charakter_mit_fertigkeiten()

        inst = CyberwareInstallation(
            name="Cyberware: Verbesserte Sicht", stress=1,
            effekte={"wahrnehmung_bonus": 1}
        )
        inst.installiert = True

        cwf.appliziere_cyberware_effekte(charakter, inst)
        self.assertEqual(charakter.fertigkeiten['Wahrnehmung'].wuerfel.value, 8)

    def test_traglast_bonus(self):
        """Traglast-Bonus wird über abgeleitete Werte berechnet."""
        from functions.abgeleitete_werte import _berechne_cyberware_traglast_bonus
        charakter = _erstelle_mock_charakter()
        charakter.active_setting_name = "SciFi Kompendium"

        inst = CyberwareInstallation(name="Cyberware: Maultier", stress=1,
                                      effekte={"traglast_staerke_bonus": 1})
        inst.installiert = True
        inst.aktiv = True
        charakter.cyberware_installationen = {"1": inst}

        bonus = _berechne_cyberware_traglast_bonus(charakter)
        self.assertEqual(bonus, 20)  # +1 Würfeltyp = +20 kg

    def test_fertigkeit_w4_minus2_korrekt_erhoehen(self):
        """Bei W4-2 (Nicht-Grundfertigkeit) setzt +1 Bonus den Modifier auf 0, nicht den Würfeltyp hoch."""
        charakter = _erstelle_mock_charakter_mit_fertigkeiten()
        # Auftreten startet bei W4-2
        self.assertEqual(charakter.fertigkeiten['Auftreten'].wuerfel.value, 4)
        self.assertEqual(charakter.fertigkeiten['Auftreten'].wuerfel.modifier, -2)

        inst = CyberwareInstallation(
            name="Cyberware: Fertigkeitsbonus", stress=1,
            effekte={"fertigkeit_bonus": {"fertigkeit": "waehlbar", "bonus": 1, "max_bonus": 2}}
        )
        inst.installiert = True
        inst.konfiguration = {"fertigkeit": "Auftreten"}

        cwf.appliziere_cyberware_effekte(charakter, inst)
        # W4-2 → W4 (modifier 0), NICHT W6
        self.assertEqual(charakter.fertigkeiten['Auftreten'].wuerfel.value, 4)
        self.assertEqual(charakter.fertigkeiten['Auftreten'].wuerfel.modifier, 0)

    def test_fertigkeit_w4_minus2_und_zurueck(self):
        """W4-2 → +1 → W4 → -1 → W4-2 (Rückgängig korrekt)."""
        charakter = _erstelle_mock_charakter_mit_fertigkeiten()

        inst = CyberwareInstallation(
            name="Cyberware: Fertigkeitsbonus", stress=1,
            effekte={"fertigkeit_bonus": {"fertigkeit": "waehlbar", "bonus": 1, "max_bonus": 2}}
        )
        inst.installiert = True
        inst.konfiguration = {"fertigkeit": "Auftreten"}

        cwf.appliziere_cyberware_effekte(charakter, inst)
        self.assertEqual(charakter.fertigkeiten['Auftreten'].wuerfel.modifier, 0)

        cwf.entferne_cyberware_effekte(charakter, inst)
        self.assertEqual(charakter.fertigkeiten['Auftreten'].wuerfel.value, 4)
        self.assertEqual(charakter.fertigkeiten['Auftreten'].wuerfel.modifier, -2)

    def test_nicht_cyberware_setting_kein_bonus(self):
        """In Nicht-Cyberware-Settings gibt es keine Boni."""
        from functions.abgeleitete_werte import _berechne_cyberware_robustheit_bonus
        charakter = _erstelle_mock_charakter()
        charakter.active_setting_name = "SWAE"

        inst = CyberwareInstallation(name="Cyberware: Robustheit", stress=1,
                                      effekte={"robustheit_bonus": 1})
        inst.installiert = True
        inst.aktiv = True
        charakter.cyberware_installationen = {"1": inst}

        bonus = _berechne_cyberware_robustheit_bonus(charakter)
        self.assertEqual(bonus, 0)


if __name__ == '__main__':
    unittest.main()
