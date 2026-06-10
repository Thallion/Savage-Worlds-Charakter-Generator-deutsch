# tests/test_archetypen_sync.py
"""
Unit Tests für die Archetypen-Synchronisation (utils/archetypen_sync.py).
Testet Mojibake-Reparatur, Quellen-Auswahl und Datei-Synchronisation.
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.archetypen_sync import (
    repariere_mojibake_name,
    zaehle_archetypen,
    finde_beste_quelle,
    sync_archetypen,
)


class TestRepariereMojibakeName(unittest.TestCase):
    """Tests für die Reparatur von Latin-1/UTF-8-Mojibake in Dateinamen."""

    def test_mojibake_umlaut_wird_repariert(self):
        """'Ã¤' (jtar-Mojibake für 'ä') wird zurückkonvertiert."""
        self.assertEqual(
            repariere_mojibake_name('Archetyp_Deadlands_KopfgeldjÃ¤ger_A.json'),
            'Archetyp_Deadlands_Kopfgeldjäger_A.json',
        )

    def test_mojibake_oe_und_ue(self):
        """Auch 'Ã¶' und 'Ã¼' werden repariert."""
        self.assertEqual(repariere_mojibake_name('SalonschÃ¶nheit.json'), 'Salonschönheit.json')
        self.assertEqual(repariere_mojibake_name('VerrÃ¼ckte.json'), 'Verrückte.json')

    def test_ascii_name_unveraendert(self):
        """Reine ASCII-Namen bleiben unverändert."""
        self.assertEqual(
            repariere_mojibake_name('Archetyp_SWAE_Soldat_A.json'),
            'Archetyp_SWAE_Soldat_A.json',
        )

    def test_echter_umlaut_unveraendert(self):
        """Korrekte Umlaute lösen UnicodeDecodeError aus und bleiben erhalten."""
        self.assertEqual(
            repariere_mojibake_name('Kopfgeldjäger.json'),
            'Kopfgeldjäger.json',
        )

    def test_surrogate_unveraendert(self):
        """Surrogate-Escapes (nicht dekodierbare Bytes) bleiben unverändert."""
        name = 'Kopfgeldj\udcc3\udca4ger.json'
        self.assertEqual(repariere_mojibake_name(name), name)

    def test_java_signed_byte_mojibake_wird_repariert(self):
        """jtar castet signierte Bytes zu chars: 0xC3 → U+FFC3 (real auf Android)."""
        name = 'Archetyp_Savage_Pathfinder_Mￃﾶnch_Sajan_A.json'
        self.assertEqual(
            repariere_mojibake_name(name),
            'Archetyp_Savage_Pathfinder_Mönch_Sajan_A.json',
        )

    def test_java_signed_byte_mojibake_ungueltig_bleibt(self):
        """Nicht als UTF-8 dekodierbare Byte-Folgen bleiben unverändert."""
        name = 'Datei_ￃX.json'  # 0xC3 ohne Folgebyte ist kein gültiges UTF-8
        self.assertEqual(repariere_mojibake_name(name), name)


class TestZaehleArchetypen(unittest.TestCase):
    """Tests für das Zählen von Archetypen-JSONs."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_zaehlt_json_rekursiv(self):
        (self.tmp / 'a.json').write_text('{}')
        (self.tmp / 'sub').mkdir()
        (self.tmp / 'sub' / 'b.json').write_text('{}')
        (self.tmp / 'c.txt').write_text('x')
        self.assertEqual(zaehle_archetypen(self.tmp), 2)

    def test_nicht_existierendes_verzeichnis(self):
        self.assertEqual(zaehle_archetypen(self.tmp / 'gibtsnicht'), 0)

    def test_datei_statt_verzeichnis(self):
        f = self.tmp / 'datei.json'
        f.write_text('{}')
        self.assertEqual(zaehle_archetypen(f), 0)


class TestFindeBesteQuelle(unittest.TestCase):
    """Tests für die Auswahl der besten Archetypen-Quelle."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.ziel = self.tmp / 'user' / 'Archetypen'
        self.ziel.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _mache_quelle(self, name, anzahl):
        quelle = self.tmp / name
        quelle.mkdir(parents=True)
        for i in range(anzahl):
            (quelle / f'archetyp_{i}.json').write_text('{}')
        return quelle

    def test_quelle_mit_meisten_jsons_gewinnt(self):
        """Nicht der erste existierende Kandidat, sondern der vollste gewinnt."""
        alt = self._mache_quelle('alt', 12)
        bundle = self._mache_quelle('bundle', 214)
        quelle, anzahl = finde_beste_quelle([alt, bundle], self.ziel)
        self.assertEqual(quelle, bundle)
        self.assertEqual(anzahl, 214)

    def test_ziel_selbst_wird_uebersprungen(self):
        """Das Zielverzeichnis darf nie als Quelle gewählt werden."""
        for i in range(12):
            (self.ziel / f'alt_{i}.json').write_text('{}')
        quelle, anzahl = finde_beste_quelle([self.ziel], self.ziel)
        self.assertIsNone(quelle)
        self.assertEqual(anzahl, 0)

    def test_keine_kandidaten(self):
        quelle, anzahl = finde_beste_quelle(
            [self.tmp / 'gibtsnicht1', self.tmp / 'gibtsnicht2'], self.ziel
        )
        self.assertIsNone(quelle)
        self.assertEqual(anzahl, 0)


class TestSyncArchetypen(unittest.TestCase):
    """Tests für die eigentliche Datei-Synchronisation."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.quelle = self.tmp / 'bundle'
        self.quelle.mkdir()
        self.ziel = self.tmp / 'user' / 'Archetypen'

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_fehlende_dateien_werden_kopiert(self):
        (self.quelle / 'a.json').write_text('{"a": 1}')
        (self.quelle / 'b.json').write_text('{"b": 2}')
        statistik = sync_archetypen(self.quelle, self.ziel)
        self.assertEqual(statistik['kopiert'], 2)
        self.assertTrue((self.ziel / 'a.json').exists())
        self.assertTrue((self.ziel / 'b.json').exists())

    def test_gleiche_groesse_wird_uebersprungen(self):
        (self.quelle / 'a.json').write_text('{"a": 1}')
        sync_archetypen(self.quelle, self.ziel)
        statistik = sync_archetypen(self.quelle, self.ziel)
        self.assertEqual(statistik['kopiert'], 0)
        self.assertEqual(statistik['vorhanden'], 1)

    def test_geaenderte_groesse_wird_aktualisiert(self):
        (self.quelle / 'a.json').write_text('{"a": 1}')
        sync_archetypen(self.quelle, self.ziel)
        (self.quelle / 'a.json').write_text('{"a": 1, "neu": true}')
        statistik = sync_archetypen(self.quelle, self.ziel)
        self.assertEqual(statistik['kopiert'], 1)
        self.assertEqual((self.ziel / 'a.json').read_text(), '{"a": 1, "neu": true}')

    def test_mojibake_name_wird_repariert(self):
        """Eine Mojibake-Datei aus der APK-Extraktion landet mit korrektem Namen im Ziel."""
        (self.quelle / 'KopfgeldjÃ¤ger.json').write_text('{}')
        statistik = sync_archetypen(self.quelle, self.ziel)
        self.assertEqual(statistik['repariert'], 1)
        self.assertTrue((self.ziel / 'Kopfgeldjäger.json').exists())
        self.assertFalse((self.ziel / 'KopfgeldjÃ¤ger.json').exists())

    def test_alte_mojibake_variante_im_ziel_wird_entfernt(self):
        """Wurde früher die Mojibake-Variante kopiert, wird sie aufgeräumt."""
        self.ziel.mkdir(parents=True)
        (self.ziel / 'KopfgeldjÃ¤ger.json').write_text('{}')
        (self.quelle / 'KopfgeldjÃ¤ger.json').write_text('{}')
        sync_archetypen(self.quelle, self.ziel)
        self.assertTrue((self.ziel / 'Kopfgeldjäger.json').exists())
        self.assertFalse((self.ziel / 'KopfgeldjÃ¤ger.json').exists())

    def test_unterverzeichnisse(self):
        sub = self.quelle / 'Setting'
        sub.mkdir()
        (sub / 'a.json').write_text('{}')
        statistik = sync_archetypen(self.quelle, self.ziel)
        self.assertEqual(statistik['kopiert'], 1)
        self.assertTrue((self.ziel / 'Setting' / 'a.json').exists())


if __name__ == '__main__':
    unittest.main()
