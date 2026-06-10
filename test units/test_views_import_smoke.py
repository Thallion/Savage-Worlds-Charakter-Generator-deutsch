# test units/test_views_import_smoke.py
"""
Import-Smoke-Tests für alle View-Module.

Sicherheitsnetz für Refactorings (Datei-Splits, Mixin-Auszüge):
- Jedes Modul in views/ muss headless importierbar sein.
- Zentrale Klassen müssen unter ihrem erwarteten Namen im erwarteten Modul
  existieren (fängt verlorene Klassen und kaputte Re-Exports beim Split ab).

Die KV-Dateien werden dabei real über Builder.load_file geladen, damit
Fehler in den KV-Regeln (z.B. doppeltes Laden nach einem Split) auffallen.
"""

import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Headless-Umgebung BEVOR Kivy importiert wird (wie .claude driver / Skill)
os.environ.setdefault('KIVY_NO_ARGS', '1')
os.environ.setdefault('KIVY_NO_CONSOLELOG', '1')
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# KivyMD Chip-Modul hat einen Metaclass-Konflikt - vor allem anderen mocken
for _mod in ['kivymd.uix.chip', 'kivymd.uix.chip.chip']:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

# Erwartete zentrale Klassen je View-Modul (Modulname -> Klassennamen).
# Bei Datei-Splits müssen diese Namen per Re-Export erhalten bleiben.
ERWARTETE_KLASSEN = {
    'views.ausruestung_popup': ['AusruestungDialogContent', 'DeleteAusruestungDialogContent', 'AusruestungDialogHandler'],
    'views.ausruestung_view': ['AusruestungWidget'],
    'views.charakter_verwaltung_widget': ['CharakterVerwaltungWidget'],
    'views.charakterbogen_view': ['CharakterbogenWidget'],
    'views.fertigkeit_popup': ['FertigkeitDialogContent', 'DeleteFertigkeitDialogContent', 'FertigkeitDialogHandler'],
    'views.handicap_popup': ['HandicapDialogContent', 'DeleteHandicapDialogContent', 'HandicapDialogHandler'],
    'views.macht_popup': ['MachtDialogContent', 'DeleteMachtDialogContent', 'MachtDialogHandler'],
    'views.ruestung_popup': ['RuestungDialogContent', 'DeleteRuestungDialogContent', 'RuestungDialogHandler'],
    'views.schild_popup': ['SchildDialogContent', 'DeleteSchildDialogContent', 'SchildDialogHandler'],
    'views.setting_assistent_view': ['SettingAssistentWizard', 'SettingAssistentDialogHandler'],
    'views.superkraft_popup': ['SuperkraftAuswahlContent', 'SuperkraftKonfigContent', 'SuperkraftDialogHandler'],
    'views.talent_popup': ['TalentDialogContent', 'DeleteTalentDialogContent', 'TalentDialogHandler'],
    'views.template_wizard': ['TemplateWizardDialog'],
    'views.voelker_view': ['VoelkerWidget'],
    'views.volk_popup': ['VolkGeneratorWizard', 'VolkDialogHandler'],
    'views.waffe_popup': ['WaffeDialogContent', 'DeleteWaffeDialogContent', 'WaffeDialogHandler'],
}


def _alle_view_module():
    """Alle importierbaren Modulnamen unter views/ (ohne __init__)."""
    views_dir = PROJECT_ROOT / 'views'
    return sorted(
        f'views.{p.stem}'
        for p in views_dir.glob('*.py')
        if p.stem != '__init__'
    )


class TestViewsImportSmoke(unittest.TestCase):
    """Importiert jedes View-Modul headless und prüft zentrale Klassen."""

    def test_01_alle_view_module_importierbar(self):
        """Jedes Modul in views/ lässt sich ohne laufende App importieren."""
        fehler = []
        for modulname in _alle_view_module():
            try:
                importlib.import_module(modulname)
            except Exception as e:
                fehler.append(f'{modulname}: {type(e).__name__}: {e}')
        self.assertEqual(fehler, [], 'Nicht importierbare View-Module:\n' + '\n'.join(fehler))

    def test_02_zentrale_klassen_vorhanden(self):
        """Zentrale Klassen existieren unter ihrem erwarteten Namen/Modul."""
        fehler = []
        for modulname, klassen in sorted(ERWARTETE_KLASSEN.items()):
            try:
                modul = importlib.import_module(modulname)
            except Exception as e:
                fehler.append(f'{modulname}: Import fehlgeschlagen: {e}')
                continue
            for klasse in klassen:
                if not hasattr(modul, klasse):
                    fehler.append(f'{modulname}: Klasse {klasse} fehlt')
        self.assertEqual(fehler, [], 'Fehlende zentrale Klassen:\n' + '\n'.join(fehler))

    def test_03_dialog_service_import_funktioniert(self):
        """services/dialog_service.py erreicht seine View-Importe (z.B. VolkDialogHandler)."""
        import services.dialog_service  # noqa: F401 - reiner Import-Smoke


if __name__ == '__main__':
    unittest.main()
