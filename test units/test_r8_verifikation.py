"""
Tests für die R8-Keep-Regel-Verifikation aus build_fixes.py.

Hintergrund: Der gesamte Java-Layer der App wird ausschließlich über JNI
(SDL2, CPython) und Reflection (pyjnius) erreicht. R8 sieht diese Zugriffe
nicht. Entfernt oder umbenennt es etwas, stürzt die App ab — aber NUR im
Release-Build, den kein lokaler Debug-Lauf abdeckt.

Diese Tests sichern, dass der Prüfer echte Verletzungen tatsächlich meldet
und die von R8 selbst erzeugten Synthetik-Namen NICHT fälschlich anmeckert.
Ein Prüfer, der immer "OK" sagt, wäre schlimmer als keiner.
"""

import unittest
from pathlib import Path
import sys
import tempfile

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from build_fixes import (  # noqa: E402
    _lies_keep_regeln,
    _parse_mapping,
    _ist_geschuetzt,
    verify_r8_keep_rules,
)
import build_fixes  # noqa: E402


def schreibe(inhalt, suffix=".txt"):
    """Schreibt Inhalt in eine temporäre Datei und gibt den Pfad zurück."""
    f = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False)
    f.write(inhalt)
    f.close()
    return Path(f.name)


class TestKeepRegelnLesen(unittest.TestCase):
    """-keep-Regeln werden aus proguard-rules.pro gelesen, nicht dupliziert."""

    def test_paketpraefixe_und_einzelklassen(self):
        pfad = schreibe(
            "# Kommentar\n"
            "-keep class org.libsdl.app.** { *; }\n"
            "-keep class org.jnius.** { *; }\n"
            "-keep class androidx.core.content.FileProvider { *; }\n"
            "-keepclasseswithmembernames class * {\n    native <methods>;\n}\n"
            "-keepattributes Signature\n",
            ".pro",
        )
        praefixe, exakte = _lies_keep_regeln(pfad)
        self.assertIn("org.libsdl.app.", praefixe)
        self.assertIn("org.jnius.", praefixe)
        self.assertIn("androidx.core.content.FileProvider", exakte)
        # Die Wildcard-Regel `class *` darf NICHT als Einzelklasse gelten
        self.assertNotIn("*", exakte)

    def test_echte_projektdatei_liefert_regeln(self):
        """Die real ausgelieferte Regeldatei muss parsebar sein."""
        praefixe, exakte = _lies_keep_regeln()
        self.assertIn("org.kivy.android.", praefixe)
        self.assertIn("org.libsdl.app.", praefixe)
        self.assertIn("org.jnius.", praefixe)
        self.assertIn("androidx.core.content.FileProvider", exakte)

    def test_ist_geschuetzt(self):
        praefixe, exakte = {"org.kivy.android."}, {"androidx.core.content.FileProvider"}
        self.assertTrue(_ist_geschuetzt("org.kivy.android.PythonActivity", praefixe, exakte))
        self.assertTrue(_ist_geschuetzt("androidx.core.content.FileProvider", praefixe, exakte))
        self.assertFalse(_ist_geschuetzt("androidx.core.app.NotificationCompat", praefixe, exakte))


class TestMappingParser(unittest.TestCase):
    """mapping.txt hat mehrere Zeilenformate — alle müssen korrekt landen."""

    MAPPING = (
        "org.kivy.android.PythonActivity -> org.kivy.android.PythonActivity:\n"
        '# {"id":"sourceFile","fileName":"PythonActivity.java"}\n'
        "    1:3:void onNewIntent(android.content.Intent):100:100 -> onNewIntent\n"
        "    java.lang.String mField -> mField\n"
        "    1:1:void <init>():10:10 -> <init>\n"
        "    3:3:android.net.Uri foo.Fremd.methode(java.io.File):849:849 -> getUriForFile\n"
        "org.libsdl.app.SDLActivity -> d.a:\n"
        "    1:2:void nativeSetenv(java.lang.String):5 -> a\n"
    )

    def setUp(self):
        self.eintraege = _parse_mapping(schreibe(self.MAPPING))

    def test_klassen_erkannt(self):
        self.assertIn("org.kivy.android.PythonActivity", self.eintraege)
        self.assertEqual(self.eintraege["org.libsdl.app.SDLActivity"][0], "d.a")

    def test_methode_mit_zeilennummern(self):
        member = self.eintraege["org.kivy.android.PythonActivity"][1]
        self.assertEqual(member.get("onNewIntent"), "onNewIntent")

    def test_feld_ohne_zeilennummern(self):
        member = self.eintraege["org.kivy.android.PythonActivity"][1]
        self.assertEqual(member.get("mField"), "mField")

    def test_inline_frame_fremder_klasse_wird_ignoriert(self):
        """Zeilen mit qualifiziertem Namen gehören einer ANDEREN Klasse.

        Würden sie der umgebenden Klasse zugeordnet, entstünden Fehlalarme.
        """
        member = self.eintraege["org.kivy.android.PythonActivity"][1]
        self.assertNotIn("foo.Fremd.methode", member)
        self.assertNotIn("getUriForFile", member)


class TestVerifikation(unittest.TestCase):
    """Der Prüfer muss echte Verletzungen melden — und nur die."""

    def setUp(self):
        # DEX-Teil neutralisieren: hier wird ausschließlich mapping.txt geprüft
        self._orig = build_fixes._finde_release_dex
        build_fixes._finde_release_dex = lambda: None

    def tearDown(self):
        build_fixes._finde_release_dex = self._orig

    def _pruefe(self, mapping_text):
        return verify_r8_keep_rules(schreibe(mapping_text))

    def test_sauberes_mapping_ohne_befund(self):
        probleme = self._pruefe(
            "org.kivy.android.PythonActivity -> org.kivy.android.PythonActivity:\n"
            "    1:3:void onNewIntent(android.content.Intent):1:1 -> onNewIntent\n"
        )
        self.assertEqual(probleme, [])

    def test_umbenannte_klasse_wird_gemeldet(self):
        probleme = self._pruefe("org.jnius.NativeInvocationHandler -> d.b:\n")
        self.assertEqual(len(probleme), 1)
        self.assertIn("Klasse umbenannt", probleme[0])
        self.assertIn("org.jnius.NativeInvocationHandler", probleme[0])

    def test_umbenanntes_member_wird_gemeldet(self):
        probleme = self._pruefe(
            "org.renpy.android.ResourceManager -> org.renpy.android.ResourceManager:\n"
            "    1:3:int getIdentifier(java.lang.String,java.lang.String):1:1 -> a\n"
        )
        self.assertEqual(len(probleme), 1)
        self.assertIn("Member umbenannt", probleme[0])
        self.assertIn("getIdentifier", probleme[0])

    def test_ungeschuetzte_klasse_darf_umbenannt_werden(self):
        """Nur was eine Keep-Regel abdeckt, wird geprüft — sonst meckert
        der Prüfer bei jeder normalen R8-Optimierung."""
        probleme = self._pruefe("androidx.core.app.NotificationCompat -> a.b:\n")
        self.assertEqual(probleme, [])

    def test_synthetik_klasse_ist_kein_fehler(self):
        """$$ExternalSynthetic-Klassen erzeugt R8 selbst."""
        probleme = self._pruefe(
            "org.libsdl.app.SDLAudioManager$$ExternalSyntheticLambda17 -> org.libsdl.app.b:\n"
        )
        self.assertEqual(probleme, [])

    def test_synthetik_member_ist_kein_fehler(self):
        """$r8$lambda$/lambda$/access$ sind Synthetik-Member ohne Quellcode-
        Entsprechung. Ein echter Release-Build produziert sie — würden sie
        gemeldet, wäre der Prüfer wegen Dauerfehlalarm wertlos."""
        probleme = self._pruefe(
            "org.libsdl.app.SDLAudioManager -> org.libsdl.app.SDLAudioManager:\n"
            "    1:1:void $r8$lambda$Sc4HU9POzDZcYsdvTGLa_SiSTTA():0:0 -> a\n"
            "    1:1:void lambda$audioOpen$0():0:0 -> b\n"
            "    1:5:java.lang.String access$000(java.lang.String):1:1 -> c\n"
        )
        self.assertEqual(probleme, [])

    def test_fehlende_mapping_datei_meldet_keinen_falschen_erfolg(self):
        """Ohne mapping.txt (Debug-Build) darf nichts behauptet werden."""
        probleme = verify_r8_keep_rules(Path("/nicht/vorhanden/mapping.txt"))
        self.assertEqual(probleme, [])


class TestDexEinstiegspunkte(unittest.TestCase):
    """Der DEX-Teil prüft Existenz — das kann mapping.txt nicht leisten,
    weil R8 dort nicht jedes überlebende Member listet."""

    SAUBER = "org.jnius.NativeInvocationHandler -> org.jnius.NativeInvocationHandler:\n"

    def setUp(self):
        self._orig = build_fixes._finde_release_dex

    def tearDown(self):
        build_fixes._finde_release_dex = self._orig

    def _mit_dex(self, klassen):
        build_fixes._finde_release_dex = lambda: (Path("test.aab"), klassen)
        return verify_r8_keep_rules(schreibe(self.SAUBER))

    def test_fehlende_klasse_wird_gemeldet(self):
        vollstaendig = {
            k: set(v) for k, v in build_fixes.R8_REFLEKTIONS_EINSTIEGSPUNKTE.items()
        }
        del vollstaendig["org.jnius.NativeInvocationHandler"]
        probleme = self._mit_dex(vollstaendig)
        self.assertTrue(any("Klasse fehlt im DEX" in p for p in probleme))

    def test_fehlendes_member_wird_gemeldet(self):
        vollstaendig = {
            k: set(v) for k, v in build_fixes.R8_REFLEKTIONS_EINSTIEGSPUNKTE.items()
        }
        vollstaendig["androidx.core.content.FileProvider"].discard("getUriForFile")
        probleme = self._mit_dex(vollstaendig)
        self.assertTrue(any("getUriForFile" in p for p in probleme))

    def test_vollstaendiger_dex_ohne_befund(self):
        vollstaendig = {
            k: set(v) for k, v in build_fixes.R8_REFLEKTIONS_EINSTIEGSPUNKTE.items()
        }
        self.assertEqual(self._mit_dex(vollstaendig), [])


if __name__ == "__main__":
    unittest.main()
