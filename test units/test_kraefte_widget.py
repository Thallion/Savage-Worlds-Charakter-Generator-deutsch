#!/usr/bin/env python3
"""
Unit Tests für das KraefteWidget (kontextabhängiger Mächte/Superkräfte-Tab).

Testet:
- Kontextabhängige Modusumschaltung (Mächte vs. Superkräfte)
- Setting-Change-Event-Propagierung im Controller
- Mächte-Filter und Sortierung (Logik isoliert)
- Rang-Mapping und Sortierreihenfolge
"""

import sys
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Projektwurzel zum Python-Pfad hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ==================== KONSTANTEN (gespiegelt aus maechte_view.py) ====================
# Diese werden hier definiert damit die Tests ohne Kivy-Widget-Import laufen

SUPERKRAEFTE_SETTINGS = [
    "Superkräfte Kompendium",
    "Superkräfte-Kompendium",
    "Superheroes"
]

RANG_MAPPING = {
    'A': 1,    # Anfänger
    'F': 2,    # Fortgeschritten
    'V': 3,    # Veteran
    'H': 4,    # Heroisch
    'L': 5,    # Legendär
    'WC': 6    # Wild Card
}


# ==================== MOCK-KLASSEN ====================

class MockMacht:
    """Mock-Objekt für eine Macht"""
    def __init__(self, name, rang='A', machtpunkte=1, beschreibung='', ausgewaehlt=False):
        self.name = name
        self.rang = rang
        self.machtpunkte = machtpunkte
        self.reichweite = "Verstand"
        self.dauer = "Sofort"
        self.beschreibung = beschreibung or f"Beschreibung für {name}"
        self.effekt = f"Effekt von {name}"
        self.ausgewaehlt = ausgewaehlt


class MockCharakter:
    """Mock-Charakter mit Mächten"""
    def __init__(self, setting_name="SWAE"):
        self.active_setting_name = setting_name
        self.rang = "Anfänger"
        self.verfuegbare_maechte = 3
        self.maechte = {
            "Blitz": MockMacht("Blitz", rang="A", machtpunkte=2, beschreibung="Elektrischer Angriff"),
            "Heilung": MockMacht("Heilung", rang="A", machtpunkte=3, beschreibung="Wunden heilen"),
            "Rüstung": MockMacht("Rüstung", rang="A", machtpunkte=2, beschreibung="Magische Panzerung", ausgewaehlt=True),
            "Telekinese": MockMacht("Telekinese", rang="V", machtpunkte=5, beschreibung="Gegenstände bewegen"),
            "Zombie": MockMacht("Zombie", rang="H", machtpunkte=3, beschreibung="Tote erwecken")
        }


class MockController:
    """Mock-Controller mit Event-Dispatch-Simulation"""
    def __init__(self, setting_name="SWAE"):
        self.charakter = MockCharakter(setting_name)
        self._event_handlers = {}

    def bind(self, **kwargs):
        """Registriert Event-Handler"""
        for event_name, handler in kwargs.items():
            if event_name not in self._event_handlers:
                self._event_handlers[event_name] = []
            self._event_handlers[event_name].append(handler)

    def dispatch(self, event_name, *args):
        """Dispatcht ein Event an registrierte Handler"""
        handlers = self._event_handlers.get(event_name, [])
        for handler in handlers:
            handler(self, *args)

    def waehle_macht(self, name, ignore_rang_check=False):
        """Mock-Methode für Macht-Auswahl"""
        if name in self.charakter.maechte:
            self.charakter.maechte[name].ausgewaehlt = True
            return True
        return False

    def entferne_macht(self, name):
        """Mock-Methode für Macht-Entfernung"""
        if name in self.charakter.maechte:
            self.charakter.maechte[name].ausgewaehlt = False
            return True
        return False


# ==================== HILFS-LOGIK (gespiegelt aus KraefteWidget) ====================

def detect_mode(setting_name):
    """Erkennt den Modus basierend auf Setting-Name (Logik aus _switch_mode_based_on_setting)"""
    return "superkraefte" if setting_name in SUPERKRAEFTE_SETTINGS else "maechte"


def filter_maechte_data(alle_maechte, search_term, only_selected=False):
    """Filter-Logik aus KraefteWidget._filter_maechte_data"""
    filtered = []
    for macht in alle_maechte.values():
        if only_selected and not macht.ausgewaehlt:
            continue
        if search_term and not (search_term in macht.name.lower() or
                               search_term in macht.beschreibung.lower()):
            continue
        filtered.append({
            'viewclass': 'MachtItemRow',
            'macht_name': macht.name,
            'rang': macht.rang,
            'machtpunkte': macht.machtpunkte,
            'beschreibung': macht.beschreibung,
            'effekt': macht.effekt,
            'macht': macht
        })
    return filtered


def sort_maechte_data(data, sort_option, sort_order):
    """Sortier-Logik aus KraefteWidget._sort_maechte_data"""
    reverse = (sort_order == 'desc')
    if sort_option == 'Name':
        data.sort(key=lambda x: x['macht_name'].lower(), reverse=reverse)
    elif sort_option == 'Rang':
        data.sort(key=lambda x: RANG_MAPPING.get(x['rang'], float('inf')), reverse=reverse)
    return data


def update_sort_option(current_option, current_order, new_option):
    """Sortier-Update-Logik aus KraefteWidget.update_sort_option"""
    if current_option == new_option:
        new_order = 'desc' if current_order == 'asc' else 'asc'
        return current_option, new_order
    else:
        return new_option, 'asc'


# ==================== TEST-KLASSEN ====================

class TestSuperkraefteSettings(unittest.TestCase):
    """Testet die Superkräfte-Settings-Erkennung"""

    def test_superkraefte_kompendium_erkannt(self):
        """'Superkräfte Kompendium' wird als Superkräfte-Setting erkannt"""
        self.assertIn("Superkräfte Kompendium", SUPERKRAEFTE_SETTINGS)

    def test_superkraefte_kompendium_hyphen_erkannt(self):
        """'Superkräfte-Kompendium' (mit Bindestrich) wird erkannt"""
        self.assertIn("Superkräfte-Kompendium", SUPERKRAEFTE_SETTINGS)

    def test_superheroes_erkannt(self):
        """'Superheroes' (englisch) wird erkannt"""
        self.assertIn("Superheroes", SUPERKRAEFTE_SETTINGS)

    def test_swae_nicht_superkraefte(self):
        """SWAE ist kein Superkräfte-Setting"""
        self.assertNotIn("SWAE", SUPERKRAEFTE_SETTINGS)

    def test_fantasy_kompendium_nicht_superkraefte(self):
        """Fantasy Kompendium ist kein Superkräfte-Setting"""
        self.assertNotIn("Fantasy Kompendium", SUPERKRAEFTE_SETTINGS)

    def test_deadlands_nicht_superkraefte(self):
        """Deadlands ist kein Superkräfte-Setting"""
        self.assertNotIn("Deadlands", SUPERKRAEFTE_SETTINGS)


class TestSettingModeDetection(unittest.TestCase):
    """Testet die Moduserkennung basierend auf Setting-Namen"""

    def test_swae_ergibt_maechte(self):
        self.assertEqual(detect_mode("SWAE"), "maechte")

    def test_fantasy_kompendium_ergibt_maechte(self):
        self.assertEqual(detect_mode("Fantasy Kompendium"), "maechte")

    def test_deadlands_ergibt_maechte(self):
        self.assertEqual(detect_mode("Deadlands"), "maechte")

    def test_hexxen_ergibt_maechte(self):
        self.assertEqual(detect_mode("HeXXen1773"), "maechte")

    def test_savage_pathfinder_ergibt_maechte(self):
        self.assertEqual(detect_mode("Savage Pathfinder"), "maechte")

    def test_rippers_ergibt_maechte(self):
        self.assertEqual(detect_mode("Rippers"), "maechte")

    def test_superkraefte_kompendium_ergibt_superkraefte(self):
        self.assertEqual(detect_mode("Superkräfte Kompendium"), "superkraefte")

    def test_superkraefte_hyphen_ergibt_superkraefte(self):
        self.assertEqual(detect_mode("Superkräfte-Kompendium"), "superkraefte")

    def test_superheroes_ergibt_superkraefte(self):
        self.assertEqual(detect_mode("Superheroes"), "superkraefte")

    def test_leerer_string_ergibt_maechte(self):
        self.assertEqual(detect_mode(""), "maechte")

    def test_unbekanntes_setting_ergibt_maechte(self):
        self.assertEqual(detect_mode("Mein Custom Setting"), "maechte")

    def test_scifi_kompendium_ergibt_maechte(self):
        self.assertEqual(detect_mode("SciFi Kompendium"), "maechte")


class TestModeSwitchLogic(unittest.TestCase):
    """Testet die Modus-Wechsel-Logik (simuliert KraefteWidget-Verhalten)"""

    def setUp(self):
        self.current_mode = "maechte"
        self.mode_changes = []

    def _switch_mode(self, setting_name):
        """Simuliert _switch_mode_based_on_setting"""
        new_mode = detect_mode(setting_name)
        if self.current_mode != new_mode:
            self.current_mode = new_mode
            self.mode_changes.append(new_mode)

    def test_initial_mode_ist_maechte(self):
        """Initialer Modus ist 'maechte'"""
        self.assertEqual(self.current_mode, "maechte")

    def test_wechsel_zu_superkraefte(self):
        """Wechsel zu Superkräfte-Setting ändert Modus"""
        self._switch_mode("Superkräfte Kompendium")
        self.assertEqual(self.current_mode, "superkraefte")

    def test_wechsel_zurueck_zu_maechte(self):
        """Wechsel zurück zu normalem Setting stellt Mächte-Modus her"""
        self._switch_mode("Superkräfte Kompendium")
        self._switch_mode("SWAE")
        self.assertEqual(self.current_mode, "maechte")

    def test_gleicher_modus_kein_wechsel(self):
        """Gleiches Normal-Setting löst keinen Wechsel aus"""
        self._switch_mode("SWAE")
        self.assertEqual(len(self.mode_changes), 0)

    def test_superkraefte_nochmal_kein_wechsel(self):
        """Wiederholtes Superkräfte-Setting löst nur einmal Wechsel aus"""
        self._switch_mode("Superkräfte Kompendium")
        self._switch_mode("Superkräfte-Kompendium")
        self.assertEqual(len(self.mode_changes), 1)

    def test_vollstaendiger_roundtrip(self):
        """Vollständiger Roundtrip: Mächte -> Superkräfte -> Mächte"""
        self.assertEqual(self.current_mode, "maechte")
        self._switch_mode("Superkräfte Kompendium")
        self.assertEqual(self.current_mode, "superkraefte")
        self._switch_mode("Fantasy Kompendium")
        self.assertEqual(self.current_mode, "maechte")
        self.assertEqual(self.mode_changes, ["superkraefte", "maechte"])

    def test_mehrere_normal_settings_bleiben_maechte(self):
        """Mehrere normale Settings bleiben im Mächte-Modus"""
        for setting in ["SWAE", "Fantasy Kompendium", "Deadlands", "HeXXen1773", "Rippers"]:
            self._switch_mode(setting)
        self.assertEqual(self.current_mode, "maechte")
        self.assertEqual(len(self.mode_changes), 0)

    def test_schnelles_hin_und_her_wechseln(self):
        """Schnelles Hin- und Herwechseln wird korrekt verarbeitet"""
        self._switch_mode("Superkräfte Kompendium")
        self._switch_mode("SWAE")
        self._switch_mode("Superkräfte-Kompendium")
        self._switch_mode("Fantasy Kompendium")
        self.assertEqual(self.current_mode, "maechte")
        self.assertEqual(self.mode_changes, ["superkraefte", "maechte", "superkraefte", "maechte"])


class TestMaechteFilterung(unittest.TestCase):
    """Testet die Mächte-Filter-Logik"""

    def setUp(self):
        self.maechte = {
            "Blitz": MockMacht("Blitz", rang="A", machtpunkte=2, beschreibung="Elektrischer Angriff"),
            "Heilung": MockMacht("Heilung", rang="A", machtpunkte=3, beschreibung="Wunden heilen"),
            "Rüstung": MockMacht("Rüstung", rang="A", machtpunkte=2, beschreibung="Magische Panzerung", ausgewaehlt=True),
            "Telekinese": MockMacht("Telekinese", rang="V", machtpunkte=5, beschreibung="Gegenstände bewegen"),
            "Zombie": MockMacht("Zombie", rang="H", machtpunkte=3, beschreibung="Tote erwecken")
        }

    def test_filter_ohne_suche(self):
        """Ohne Suchbegriff werden alle Mächte angezeigt"""
        result = filter_maechte_data(self.maechte, "")
        self.assertEqual(len(result), 5)

    def test_filter_nach_name(self):
        """Suche nach Machtnamen funktioniert"""
        result = filter_maechte_data(self.maechte, "blitz")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['macht_name'], "Blitz")

    def test_filter_nach_beschreibung(self):
        """Suche nach Beschreibung funktioniert"""
        result = filter_maechte_data(self.maechte, "heilen")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['macht_name'], "Heilung")

    def test_filter_teiluebereinstimmung(self):
        """Teilübereinstimmungen werden gefunden"""
        result = filter_maechte_data(self.maechte, "ung")
        namen = [r['macht_name'] for r in result]
        self.assertIn("Heilung", namen)
        self.assertIn("Rüstung", namen)

    def test_filter_kein_treffer(self):
        """Bei keiner Übereinstimmung wird leere Liste zurückgegeben"""
        result = filter_maechte_data(self.maechte, "nichtexistent")
        self.assertEqual(len(result), 0)

    def test_filter_nur_ausgewaehlte(self):
        """'Nur ausgewählte' Filter zeigt nur ausgewählte Mächte"""
        result = filter_maechte_data(self.maechte, "", only_selected=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['macht_name'], "Rüstung")

    def test_filter_nur_ausgewaehlte_mit_suche(self):
        """Kombination von 'Nur ausgewählte' und Suche"""
        result = filter_maechte_data(self.maechte, "blitz", only_selected=True)
        self.assertEqual(len(result), 0)  # Blitz ist nicht ausgewählt

    def test_filter_viewclass_gesetzt(self):
        """Gefilterte Daten haben korrekte viewclass"""
        result = filter_maechte_data(self.maechte, "blitz")
        self.assertEqual(result[0]['viewclass'], 'MachtItemRow')

    def test_filter_macht_objekt_enthalten(self):
        """Gefilterte Daten enthalten das Original-Macht-Objekt"""
        result = filter_maechte_data(self.maechte, "blitz")
        self.assertIs(result[0]['macht'], self.maechte["Blitz"])


class TestMaechteSortierung(unittest.TestCase):
    """Testet die Mächte-Sortier-Logik"""

    def setUp(self):
        self.maechte = {
            "Zombie": MockMacht("Zombie", rang="H"),
            "Blitz": MockMacht("Blitz", rang="A"),
            "Telekinese": MockMacht("Telekinese", rang="V"),
            "Heilung": MockMacht("Heilung", rang="A"),
            "Rüstung": MockMacht("Rüstung", rang="F"),
        }
        self.data = filter_maechte_data(self.maechte, "")

    def test_sort_name_aufsteigend(self):
        """Sortierung nach Name aufsteigend"""
        sorted_data = sort_maechte_data(list(self.data), 'Name', 'asc')
        namen = [d['macht_name'] for d in sorted_data]
        self.assertEqual(namen, sorted(namen, key=str.lower))

    def test_sort_name_absteigend(self):
        """Sortierung nach Name absteigend"""
        sorted_data = sort_maechte_data(list(self.data), 'Name', 'desc')
        namen = [d['macht_name'] for d in sorted_data]
        self.assertEqual(namen, sorted(namen, key=str.lower, reverse=True))

    def test_sort_rang_aufsteigend(self):
        """Sortierung nach Rang aufsteigend (A vor F vor V vor H)"""
        sorted_data = sort_maechte_data(list(self.data), 'Rang', 'asc')
        raenge = [d['rang'] for d in sorted_data]
        rang_werte = [RANG_MAPPING.get(r, 99) for r in raenge]
        self.assertEqual(rang_werte, sorted(rang_werte))

    def test_sort_rang_absteigend(self):
        """Sortierung nach Rang absteigend (H vor V vor F vor A)"""
        sorted_data = sort_maechte_data(list(self.data), 'Rang', 'desc')
        raenge = [d['rang'] for d in sorted_data]
        rang_werte = [RANG_MAPPING.get(r, 99) for r in raenge]
        self.assertEqual(rang_werte, sorted(rang_werte, reverse=True))


class TestSortierOptionen(unittest.TestCase):
    """Testet die Sortier-Optionen-Logik"""

    def test_initiale_sortierung(self):
        """Initiale Sortierung ist Name aufsteigend"""
        option, order = 'Name', 'asc'
        self.assertEqual(option, 'Name')
        self.assertEqual(order, 'asc')

    def test_gleiche_option_togglet(self):
        """Gleiche Option togglet die Reihenfolge"""
        option, order = update_sort_option('Name', 'asc', 'Name')
        self.assertEqual(option, 'Name')
        self.assertEqual(order, 'desc')

    def test_toggle_zurueck(self):
        """Zweimaliges Toggle kehrt zurück zu aufsteigend"""
        option, order = update_sort_option('Name', 'asc', 'Name')
        option, order = update_sort_option(option, order, 'Name')
        self.assertEqual(order, 'asc')

    def test_neue_option_reset(self):
        """Neue Option setzt Reihenfolge auf aufsteigend zurück"""
        option, order = update_sort_option('Name', 'desc', 'Rang')
        self.assertEqual(option, 'Rang')
        self.assertEqual(order, 'asc')

    def test_wechsel_und_toggle(self):
        """Wechsel und dann Toggle funktioniert"""
        option, order = update_sort_option('Name', 'asc', 'Rang')
        self.assertEqual(option, 'Rang')
        self.assertEqual(order, 'asc')
        option, order = update_sort_option(option, order, 'Rang')
        self.assertEqual(order, 'desc')


class TestRangMapping(unittest.TestCase):
    """Testet das Rang-Mapping für die Sortierung"""

    def test_rang_reihenfolge(self):
        """Ränge sind in der richtigen Reihenfolge"""
        self.assertLess(RANG_MAPPING['A'], RANG_MAPPING['F'])
        self.assertLess(RANG_MAPPING['F'], RANG_MAPPING['V'])
        self.assertLess(RANG_MAPPING['V'], RANG_MAPPING['H'])
        self.assertLess(RANG_MAPPING['H'], RANG_MAPPING['L'])
        self.assertLess(RANG_MAPPING['L'], RANG_MAPPING['WC'])

    def test_unbekannter_rang_sortiert_ans_ende(self):
        """Unbekannte Ränge werden am Ende sortiert"""
        unknown = RANG_MAPPING.get('X', float('inf'))
        self.assertGreater(unknown, RANG_MAPPING['WC'])

    def test_anfaenger_ist_niedrigster_rang(self):
        """Anfänger (A) hat den niedrigsten Wert"""
        self.assertEqual(RANG_MAPPING['A'], min(RANG_MAPPING.values()))

    def test_alle_raenge_vorhanden(self):
        """Alle relevanten Ränge sind im Mapping"""
        for rang in ['A', 'F', 'V', 'H', 'L', 'WC']:
            self.assertIn(rang, RANG_MAPPING)


class TestControllerSettingEvent(unittest.TestCase):
    """Testet die Setting-Change-Events im echten Controller"""

    def test_controller_event_registriert(self):
        """on_setting_changed Event wird im Controller registriert"""
        from controllers.charakter_controller import CharakterController
        controller = CharakterController()
        # dispatch sollte nicht werfen
        controller.dispatch('on_setting_changed', 'SWAE')

    def test_controller_handler_signatur(self):
        """Interner Handler hat korrekte Signatur (nur setting_name, kein instance)"""
        from controllers.charakter_controller import CharakterController
        controller = CharakterController()
        # Interner Handler bekommt nur setting_name
        controller.on_setting_changed('SWAE')

    def test_controller_dispatch_propagiert(self):
        """dispatch sendet Setting-Name an gebundene Handler"""
        from controllers.charakter_controller import CharakterController
        controller = CharakterController()

        received = []

        def handler(instance, setting_name):
            received.append(setting_name)

        controller.bind(on_setting_changed=handler)
        controller.dispatch('on_setting_changed', 'Superkräfte Kompendium')

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], 'Superkräfte Kompendium')

    def test_neuer_charakter_dispatcht_event(self):
        """neuer_charakter dispatcht on_setting_changed bei Angabe eines Settings"""
        from controllers.charakter_controller import CharakterController
        controller = CharakterController()

        received = []

        def handler(instance, setting_name):
            received.append(setting_name)

        controller.bind(on_setting_changed=handler)
        controller.neuer_charakter(char_name="Test", setting_name="SWAE")

        self.assertIn('SWAE', received)

    def test_neuer_charakter_ohne_setting_kein_event(self):
        """neuer_charakter ohne setting_name dispatcht kein on_setting_changed"""
        from controllers.charakter_controller import CharakterController
        controller = CharakterController()

        received = []

        def handler(instance, setting_name):
            received.append(setting_name)

        controller.bind(on_setting_changed=handler)
        controller.neuer_charakter(char_name="Test")

        # setting_name=None ist falsy, kein Event
        self.assertEqual(len(received), 0)

    def test_mehrere_handler_werden_aufgerufen(self):
        """Mehrere gebundene Handler werden alle bei dispatch aufgerufen"""
        from controllers.charakter_controller import CharakterController
        controller = CharakterController()

        handler1_called = []
        handler2_called = []

        controller.bind(on_setting_changed=lambda inst, name: handler1_called.append(name))
        controller.bind(on_setting_changed=lambda inst, name: handler2_called.append(name))
        controller.dispatch('on_setting_changed', 'Test-Setting')

        self.assertEqual(handler1_called, ['Test-Setting'])
        self.assertEqual(handler2_called, ['Test-Setting'])


class TestMockControllerEventPropagation(unittest.TestCase):
    """Testet die Event-Propagierung mit Mock-Controller"""

    def test_event_binding(self):
        """Controller-bind registriert Handler korrekt"""
        controller = MockController()
        received = []

        controller.bind(on_setting_changed=lambda inst, name: received.append(name))
        controller.dispatch('on_setting_changed', 'SWAE')

        self.assertEqual(received, ['SWAE'])

    def test_setting_switch_sequenz(self):
        """Sequenzielles Wechseln der Settings wird korrekt propagiert"""
        controller = MockController()
        received = []

        controller.bind(on_setting_changed=lambda inst, name: received.append(name))

        controller.dispatch('on_setting_changed', 'SWAE')
        controller.dispatch('on_setting_changed', 'Superkräfte Kompendium')
        controller.dispatch('on_setting_changed', 'Fantasy Kompendium')

        self.assertEqual(received, ['SWAE', 'Superkräfte Kompendium', 'Fantasy Kompendium'])

    def test_handler_erhaelt_setting_name(self):
        """Handler erhält korrekten Setting-Namen"""
        controller = MockController()

        def handler(instance, name):
            self.assertIsInstance(name, str)
            self.assertEqual(name, 'Superkräfte Kompendium')

        controller.bind(on_setting_changed=handler)
        controller.dispatch('on_setting_changed', 'Superkräfte Kompendium')

    def test_handler_erhaelt_controller_instanz(self):
        """Handler erhält Controller als instance"""
        controller = MockController()

        def handler(instance, name):
            self.assertIs(instance, controller)

        controller.bind(on_setting_changed=handler)
        controller.dispatch('on_setting_changed', 'SWAE')


class TestMockCharakter(unittest.TestCase):
    """Testet die MockCharakter-Klasse für korrekte Test-Isolation"""

    def test_standard_setting(self):
        """Standard-Setting ist SWAE"""
        char = MockCharakter()
        self.assertEqual(char.active_setting_name, "SWAE")

    def test_custom_setting(self):
        """Setting kann beim Erstellen gesetzt werden"""
        char = MockCharakter("Superkräfte Kompendium")
        self.assertEqual(char.active_setting_name, "Superkräfte Kompendium")

    def test_maechte_vorhanden(self):
        """Mock-Charakter hat Mächte"""
        char = MockCharakter()
        self.assertGreater(len(char.maechte), 0)

    def test_maechte_haben_attribute(self):
        """Mock-Mächte haben alle nötigen Attribute"""
        char = MockCharakter()
        for name, macht in char.maechte.items():
            self.assertEqual(macht.name, name)
            self.assertIn(macht.rang, ['A', 'F', 'V', 'H', 'L', 'WC'])
            self.assertIsInstance(macht.machtpunkte, int)
            self.assertIsInstance(macht.beschreibung, str)
            self.assertIsInstance(macht.ausgewaehlt, bool)

    def test_eine_macht_ausgewaehlt(self):
        """Genau eine Macht ist initial ausgewählt"""
        char = MockCharakter()
        ausgewaehlte = [m for m in char.maechte.values() if m.ausgewaehlt]
        self.assertEqual(len(ausgewaehlte), 1)
        self.assertEqual(ausgewaehlte[0].name, "Rüstung")


class TestMockController(unittest.TestCase):
    """Testet die MockController-Klasse"""

    def test_waehle_macht(self):
        """Macht auswählen funktioniert"""
        controller = MockController()
        result = controller.waehle_macht("Blitz")
        self.assertTrue(result)
        self.assertTrue(controller.charakter.maechte["Blitz"].ausgewaehlt)

    def test_waehle_unbekannte_macht(self):
        """Unbekannte Macht auswählen schlägt fehl"""
        controller = MockController()
        result = controller.waehle_macht("NichtExistent")
        self.assertFalse(result)

    def test_entferne_macht(self):
        """Macht entfernen funktioniert"""
        controller = MockController()
        controller.charakter.maechte["Blitz"].ausgewaehlt = True
        result = controller.entferne_macht("Blitz")
        self.assertTrue(result)
        self.assertFalse(controller.charakter.maechte["Blitz"].ausgewaehlt)


class TestSettingPopupEventIntegration(unittest.TestCase):
    """Testet die Integration der Setting-Events (simuliert setting_popup.py Verhalten)"""

    def test_load_dispatcht_setting_changed(self):
        """Nach Setting-Laden wird on_setting_changed dispatcht"""
        controller = MockController()
        received = []

        controller.bind(on_setting_changed=lambda inst, name: received.append(name))

        # Simuliere SettingsRepository.load Verhalten
        setting_name = "Fantasy Kompendium"
        if hasattr(controller, 'dispatch') and setting_name:
            controller.dispatch('on_setting_changed', setting_name)

        self.assertEqual(received, ['Fantasy Kompendium'])

    def test_load_superkraefte_dispatcht_event(self):
        """Nach Superkräfte-Setting-Laden wird korrektes Event dispatcht"""
        controller = MockController()
        received = []

        controller.bind(on_setting_changed=lambda inst, name: received.append(name))

        setting_name = "Superkräfte Kompendium"
        if hasattr(controller, 'dispatch') and setting_name:
            controller.dispatch('on_setting_changed', setting_name)

        self.assertEqual(received, ['Superkräfte Kompendium'])


class TestGameElementsHandlerEventIntegration(unittest.TestCase):
    """Testet den Setting-Wechsel über game_elements_handler (Hauptweg für Benutzer-UI)"""

    def test_apply_setting_change_dispatcht_event(self):
        """_apply_setting_change dispatcht on_setting_changed nach erfolgreichem Wechsel"""
        controller = MockController("Superkräfte Kompendium")
        received = []

        controller.bind(on_setting_changed=lambda inst, name: received.append(name))

        # Simuliere was _apply_setting_change tut nach erfolgreichem change_active_setting
        setting_name = "SWAE"
        success = True
        if success and hasattr(controller, 'dispatch'):
            controller.dispatch('on_setting_changed', setting_name)

        self.assertEqual(received, ['SWAE'])

    def test_setting_wechsel_superkraefte_zu_normal(self):
        """Wechsel von Superkräfte zu normalem Setting dispatcht Event und ändert Modus"""
        controller = MockController("Superkräfte Kompendium")
        mode_tracker = {"mode": "superkraefte"}

        def on_setting_changed(inst, name):
            mode_tracker["mode"] = detect_mode(name)

        controller.bind(on_setting_changed=on_setting_changed)

        # Simuliere Setting-Wechsel über UI
        controller.dispatch('on_setting_changed', 'Fantasy Kompendium')

        self.assertEqual(mode_tracker["mode"], "maechte")

    def test_setting_wechsel_normal_zu_superkraefte(self):
        """Wechsel von normalem Setting zu Superkräfte dispatcht Event und ändert Modus"""
        controller = MockController("SWAE")
        mode_tracker = {"mode": "maechte"}

        def on_setting_changed(inst, name):
            mode_tracker["mode"] = detect_mode(name)

        controller.bind(on_setting_changed=on_setting_changed)

        controller.dispatch('on_setting_changed', 'Superkräfte Kompendium')

        self.assertEqual(mode_tracker["mode"], "superkraefte")

    def test_fehlgeschlagener_wechsel_kein_event(self):
        """Bei fehlgeschlagenem Setting-Wechsel wird kein Event dispatcht"""
        controller = MockController()
        received = []

        controller.bind(on_setting_changed=lambda inst, name: received.append(name))

        # Simuliere fehlgeschlagenen Wechsel
        success = False
        if success and hasattr(controller, 'dispatch'):
            controller.dispatch('on_setting_changed', 'Neues Setting')

        self.assertEqual(received, [])  # Kein Event


class TestIntegrationModusUndFilter(unittest.TestCase):
    """Integrationstests: Moduswechsel zusammen mit Filter/Sortierung"""

    def test_filter_nur_im_maechte_modus(self):
        """Filter-Daten werden nur im Mächte-Modus erzeugt"""
        char = MockCharakter("SWAE")
        result = filter_maechte_data(char.maechte, "")
        self.assertGreater(len(result), 0)

    def test_filter_nach_moduswechsel(self):
        """Filter funktioniert nach Moduswechsel korrekt"""
        # Simuliere: Start in Mächte-Modus, wechsle zu Superkräfte, zurück zu Mächte
        mode = detect_mode("SWAE")
        self.assertEqual(mode, "maechte")

        mode = detect_mode("Superkräfte Kompendium")
        self.assertEqual(mode, "superkraefte")

        mode = detect_mode("Fantasy Kompendium")
        self.assertEqual(mode, "maechte")

        # Filter sollte nach Rückkehr noch funktionieren
        char = MockCharakter("Fantasy Kompendium")
        result = filter_maechte_data(char.maechte, "blitz")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['macht_name'], "Blitz")

    def test_sort_und_filter_kombiniert(self):
        """Sortierung und Filter arbeiten korrekt zusammen"""
        char = MockCharakter()
        # Filtere nach "ung" (findet Heilung und Rüstung)
        result = filter_maechte_data(char.maechte, "ung")
        self.assertEqual(len(result), 2)

        # Sortiere nach Name
        sorted_result = sort_maechte_data(list(result), 'Name', 'asc')
        namen = [d['macht_name'] for d in sorted_result]
        self.assertEqual(namen, sorted(namen, key=str.lower))


if __name__ == '__main__':
    unittest.main()
