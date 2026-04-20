#!/usr/bin/env python3
"""
Unit Tests für Lazy-Service-Initialisierung (services/service_container.py).

Tests zu Plan-Schritt 3 der Android-Performance-Optimierung:
- Kern-Services sind nach initialize() sofort verfügbar.
- Nicht-kritische Services sind nach initialize() NICHT instanziiert.
- Erster Zugriff auf Lazy-Service erzeugt Instanz via Factory.
- Zweiter Zugriff liefert dieselbe Instanz (Idempotenz).
- is_service_loaded unterscheidet eager/lazy korrekt.
- Factory-Fehler blockieren ServiceContainer nicht.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:  # pragma: no cover
    import kivy  # noqa: F401
    _KIVY_AVAILABLE = True
except Exception:
    _KIVY_AVAILABLE = False


@unittest.skipUnless(_KIVY_AVAILABLE, "Kivy nicht verfügbar")
class TestLazyServices(unittest.TestCase):
    """Testet die Lazy-Service-Erzeugung im ServiceContainer."""

    def setUp(self):
        # Singleton-State zwischen Tests zurücksetzen
        from services.service_container import ServiceContainer
        ServiceContainer._services = {}
        ServiceContainer._lazy_factories = {}
        self.container = ServiceContainer()

    def tearDown(self):
        from services.service_container import ServiceContainer
        ServiceContainer._services = {}
        ServiceContainer._lazy_factories = {}

    def _init_container(self, with_controller=True):
        """Initialisiert den Container mit gemockten Service-Klassen."""
        controller = MagicMock() if with_controller else None
        # App.get_running_app() gibt None zurück → kein Dialog-Service
        with patch('services.service_container.App') as mock_app:
            mock_app.get_running_app.return_value = None
            self.container.initialize(controller)

    # ---------- Eager Services ----------

    def test_core_services_are_eager(self):
        """ConfigService, EventService, ThemeService, WizardService sofort verfügbar."""
        self._init_container()
        for name in ('config', 'event', 'theme', 'wizard'):
            self.assertTrue(
                self.container.is_service_loaded(name),
                f"Kernservice '{name}' sollte eager sein"
            )

    def test_file_manager_eager_with_controller(self):
        """FileManagerService wird eager erzeugt, wenn Controller vorhanden."""
        self._init_container(with_controller=True)
        self.assertTrue(self.container.is_service_loaded('file_manager'))
        self.assertTrue(self.container.is_service_loaded('charakter_controller'))

    # ---------- Lazy Services ----------

    def test_lazy_services_not_loaded_after_init(self):
        """backup, tutorial, pdf, html sind nach init NICHT instanziiert."""
        self._init_container()
        for name in ('backup', 'tutorial', 'pdf', 'html'):
            self.assertFalse(
                self.container.is_service_loaded(name),
                f"Lazy-Service '{name}' darf nach init nicht geladen sein"
            )
            self.assertTrue(
                self.container.is_service_available(name),
                f"Lazy-Service '{name}' sollte verfügbar (via Factory) sein"
            )

    def test_lazy_service_is_created_on_first_access(self):
        """Erster Zugriff erzeugt Lazy-Service."""
        self._init_container()
        service = self.container.get_service('backup')
        self.assertIsNotNone(service)
        self.assertTrue(self.container.is_service_loaded('backup'))

    def test_lazy_service_is_idempotent(self):
        """Zweiter Zugriff liefert dieselbe Instanz (Factory nur 1x)."""
        self._init_container()
        first = self.container.get_service('tutorial')
        second = self.container.get_service('tutorial')
        self.assertIs(first, second)

    def test_lazy_factory_removed_after_first_call(self):
        """Nach erstem Zugriff ist die Factory weg (kein doppeltes Erzeugen möglich)."""
        self._init_container()
        _ = self.container.get_service('pdf')
        self.assertNotIn('pdf', self.container._lazy_factories)
        self.assertIn('pdf', self.container._services)

    def test_get_backup_service_triggers_lazy_init(self):
        """Convenience-Getter erzeugt Lazy-Service korrekt."""
        self._init_container()
        self.assertFalse(self.container.is_service_loaded('backup'))
        service = self.container.get_backup_service()
        self.assertIsNotNone(service)
        self.assertTrue(self.container.is_service_loaded('backup'))

    # ---------- Fehlerbehandlung ----------

    def test_factory_error_returns_none_and_does_not_crash(self):
        """Wenn eine Factory eine Exception wirft, bekommt der Caller None zurück."""
        self._init_container()
        self.container._lazy_factories['broken'] = lambda: (_ for _ in ()).throw(
            RuntimeError("boom")
        )
        result = self.container.get_service('broken')
        self.assertIsNone(result)
        # Weitere Services dürfen weiterhin funktionieren
        self.assertIsNotNone(self.container.get_service('config'))

    def test_unknown_service_returns_none(self):
        """Unbekannter Service-Name liefert None ohne Crash."""
        self._init_container()
        self.assertIsNone(self.container.get_service('does_not_exist'))

    # ---------- Status & Available ----------

    def test_get_service_status_includes_lazy(self):
        """get_service_status zeigt Lazy-Services als False, Eager als True."""
        self._init_container()
        status = self.container.get_service_status()
        self.assertTrue(status.get('config'))
        self.assertFalse(status.get('backup'))
        self.assertFalse(status.get('tutorial'))
        self.assertFalse(status.get('pdf'))
        self.assertFalse(status.get('html'))

    def test_is_service_available_true_for_lazy(self):
        """is_service_available gibt True auch für nicht-instanziierte Lazy-Services."""
        self._init_container()
        self.assertTrue(self.container.is_service_available('backup'))
        self.assertTrue(self.container.is_service_available('tutorial'))
        self.assertTrue(self.container.is_service_available('pdf'))
        self.assertTrue(self.container.is_service_available('html'))

    def test_is_service_available_false_for_unknown(self):
        """is_service_available gibt False für unbekannte Services."""
        self._init_container()
        self.assertFalse(self.container.is_service_available('unknown_svc'))


if __name__ == "__main__":
    unittest.main()
