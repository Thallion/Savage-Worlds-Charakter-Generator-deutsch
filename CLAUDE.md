# CLAUDE.md - Savage Worlds Charakter-Generator (deutsch)

## Project Overview

A German-language character generator for the **Savage Worlds** tabletop RPG system. Built with Python/Kivy/KivyMD, it supports multiple game settings (SWAE, Deadlands, Fantasy Kompendium, Savage Pathfinder, HeXXen 1773, Sundered Skies, Horror Kompendium, Rippers, SciFi Kompendium, Superkräfte Kompendium, 50 Fathoms, Hellfrost) and runs on Desktop (Windows/Linux/macOS) and Android.

**License:** CC BY-NC-SA 4.0 (non-commercial)
**Current Version:** 0.7.7.6
**Python:** 3.8+ (3.11 recommended)

## Documentation Index

Detaillierte Dokumentation in `docs/`:

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Vollständiger Verzeichnisbaum, Mixin-Modell, Service Container, Event-System, Dialog-Pattern
- **[docs/CODE_CONVENTIONS.md](docs/CODE_CONVENTIONS.md)** — German naming, Import Order, View/KV-Pairing
- **[docs/ANDROID_WORKAROUNDS.md](docs/ANDROID_WORKAROUNDS.md)** — Kivy/Android Fixes (Checkboxen, TextField, MDDialog, Touch-Bounce) — **WICHTIG bei UI-Änderungen!**
- **[docs/TUTORIALS_WIZARDS.md](docs/TUTORIALS_WIZARDS.md)** — Tutorial Service, Character Wizard, Setting Assistant, Template Wizard
- **[docs/TESTING.md](docs/TESTING.md)** — Test-Befehle, Test-Module-Übersicht, Mocking-Konventionen
- **[docs/BUILD.md](docs/BUILD.md)** — Desktop + Android Builds, Build-Specs
- **[docs/DATA_FORMATS.md](docs/DATA_FORMATS.md)** — Character-/Setting-/Template-/Config-JSON
- **[docs/ARCHETYPEN_BUILD.md](docs/ARCHETYPEN_BUILD.md)** — Archetypen-Build-Skripte (`logs/`), Pipeline-Reihenfolge pro Setting, `fill_budget_gaps.py`, Verifikations-Tools

## Quick Reference

```bash
# Run the application
python main.py

# Install dependencies
pip install -r requirements.txt

# Run all tests
python "test units/run_all_tests.py"

# Run a single test module
python -m pytest "test units/test_theme_handler.py"

# Build Linux binary
python build_linux.py

# Build Windows binary
python build_windows.py
```

## Architecture (Kurzfassung)

**Pattern:** Model-View-Controller (MVC) mit Service Container für Dependency Injection.

Top-Level-Struktur:
- `models/` — Datenmodelle (Charakter via Mixins, Talent, Fertigkeit, Volk, …)
- `views/` — Kivy-UI (`*_view.py/.kv`, `*_popup.py/.kv`, `*_view_mobile.kv` für Android)
- `controllers/` — Business Logic (Charakter-Controller, Handler, Undo-Manager)
- `services/` — DI-Services (config, theme, dialog, file_manager, pdf, tutorial, wizard)
- `manager/` — Domain-spezifische Manager (theme, pdf, html, statistics, volk)
- `functions/` — Feature-Logik (talent_funktionen, abgeleitete_werte, setting_merge, …)
- `config/`, `settings/`, `templates/` — JSON-Konfiguration und Spieldaten
- `utils/` — Path/Platform/Logging/HiDPI/Share-Helfer
- `test units/` — Test-Suite (mit Leerzeichen im Namen!)

→ Vollständige Beschreibung: **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

## Key Design Patterns (Bullets)

- **Mixin-Charakter**: `Charakter` ist aus `CharakterProperties`, `CharakterPersistence`, `CharakterEquipment`, `CharakterElements` komponiert
- **Service Container (Singleton)**: Zugriff über `service_container` global; keine direkten Service-Instanzen
- **Event-Driven UI**: `EventDispatcher` mit `on_charakter_changed`, `on_charakter_updated`, `on_charakter_loaded`, `on_charakter_error`
- **Tab-Navigation**: `MDTabsPrimary` mit 11 Tabs (Einstellungen → Info)
- **Dialog/Snackbar**: `MDDialog` für Entscheidungen (immer `size_hint=(0.85, None)`!), `MDSnackbar` via `dialog_service.show_warning_dialog()` / `show_success_dialog()` für nicht-blockierende Hinweise

→ Details: **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

## Code Conventions (Bullets)

- **Domain-Begriffe auf Deutsch**: Eigenschaften, Fertigkeiten, Talente, Handicaps, Mächte, Superkräfte, Ausrüstung, Völker, Würfel
- **Docstrings und Kommentare**: Deutsch
- **Funktions-/Variablennamen**: `snake_case` mit deutschen Domain-Begriffen (`waehle_talent()`, `speichern_als_json()`)
- **Klassen**: `PascalCase` (`Charakter`, `CharakterController`)
- **View/KV-Paare**: Jede Tab/Popup hat `.py` + `.kv`; mobile Layouts in `*_view_mobile.kv` (gleiche Python-Logik)

→ Details: **[docs/CODE_CONVENTIONS.md](docs/CODE_CONVENTIONS.md)**

## Critical Android Rules (KURZ)

Die häufigsten Fallen auf Android — **vollständige Begründung und Code-Beispiele in [docs/ANDROID_WORKAROUNDS.md](docs/ANDROID_WORKAROUNDS.md)**:

- **Checkboxen IMMER in separates Popup** (Solution 3 ist STANDARD). Niemals direkt in einen Dialog mit ScrollView einbetten.
- **`on_release` + 500ms Debounce** für Checkboxen/Buttons. `on_active` funktioniert NICHT zuverlässig.
- **Lambdas in Schleifen**: Intermediate Variable (`cb = checkbox`) verwenden, sonst Closure-Bug.
- **`MDDialog` IMMER mit `size_hint=(0.85, None)`** — nicht `(1, 1)`, sonst Vollbild-Popup auf Android.
- **`MDDialogContentContainer` benötigt feste Höhe** (`size_hint_y=None`, berechnete `height`).
- **`TextFieldScrollView` statt `MDScrollView`** wenn `MDTextField` enthalten ist.
- **`SearchBottomSheet` statt `MDDialog`** für Such-/Filterlisten — auch für Mehrfachauswahl (`multi_select=True`, z.B. Phase 1 der Lösch-Dialoge). In einem `MDDialog` scrollen solche Listen auf Android nicht.

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.8+ |
| GUI Framework | Kivy | >= 2.3.0 |
| UI Library | KivyMD | 2.0.1 (GitHub master) |
| PDF Export | ReportLab | >= 3.6.0 |
| Image Processing | Pillow | >= 8.0.0 |
| Date Utils | python-dateutil | >= 2.8.0 |
| Windows Only | pypiwin32 | >= 223 |

## Important Notes for AI Assistants

1. **German domain language**: Always use German for game-domain terms in code (Charakter, Talent, Fertigkeit, etc.). Comments and docstrings should be in German.
2. **Kivy property system**: Character model uses Kivy `ObjectProperty`, `StringProperty`, `NumericProperty`, etc. Changes propagate to UI via Kivy bindings.
3. **KivyMD 2.0.1**: The project uses the development version from GitHub master, not the stable PyPI release. Widget APIs may differ from KivyMD docs.
4. **Mixin architecture**: When modifying the `Charakter` class, identify which mixin owns the functionality before editing.
5. **Service container**: Access services through `service_container` singleton, not by creating new instances.
6. **View/KV pairs**: When adding or modifying UI, update both the `.py` and `.kv` files. If a `*_view_mobile.kv` exists for the view, update it too.
7. **Config files are gitignored**: `config/app_config.json` and custom config files are in `.gitignore`. Don't rely on their committed state.
8. **Test directory has a space**: The test directory is `test units/` (with a space). Use quotes in paths.
9. **No CI pipeline in repo**: There are no GitHub Actions workflow files committed; builds are done locally.
10. **Character files are gitignored**: `chars/` directory is in `.gitignore`.
11. **Superkräfte system**: Super powers (Superkräfte) with dedicated models, views, and functions. The Superkräfte Kompendium provides specialized super hero character creation.
12. **MDDialog size_hint**: All MDDialog instances must use `size_hint=(0.85, None)` (or similar constrained values) to prevent full-screen popups on Android. Never use the default `(1, 1)`.
13. **Snackbar for feedback**: Use `dialog_service.show_warning_dialog()` / `show_success_dialog()` for non-blocking user feedback (these internally use MDSnackbar). Reserve `show_error_dialog()` for errors requiring user acknowledgment.
14. **Tutorial System**: Tutorial content is defined in `config/tutorial_config.json`. When adding new UI features, consider adding corresponding tutorial hints. The tutorial service manages display state automatically.
15. **Wizard Integration**: Multi-step processes should use the wizard service pattern for consistent UX. Each wizard step should have proper validation and clear navigation.
16. **Setting Assistant**: For advanced setting modification, use the setting assistant rather than direct JSON editing. The assistant handles validation and conflict resolution automatically.
17. **Checkboxen IMMER in separates Popup**: Checkboxen dürfen NIEMALS direkt in einen bestehenden Dialog eingebettet werden. Sie müssen IMMER in ein eigenes separates Popup mit eigenem ScrollView ausgegliedert werden. Erst Optionen-Popup zeigen → Werte in temp-Variablen speichern → Popup schließen → dann Aktions-Dialog zeigen. Siehe **[docs/ANDROID_WORKAROUNDS.md](docs/ANDROID_WORKAROUNDS.md)** (Solution 3). Vorlagen: Setting-Auswahl (Neuer Charakter), Modus-Auswahl (Setting Assistent), Elemente-Auswahl (Setting Assistent), Volkseigenarten (volk_popup.py), HTML-Export (html_manager.py).
18. **Effekt-Registry für abgeleitete Werte**: Talent-/Handicap-Effekte auf Parade, Bewegungsweite, Größe, Robustheit, Bennys und Traglast gehören in `config/abgeleitete_effekte.json` (geladen via `functions/effekt_registry.py`), NICHT als hartcodierte Namensvergleiche in den Code. Semantik: additiv; `nicht_kumulativ_gruppe` = nur Gruppen-Maximum zählt; `bedingung` = geschlossene Code-Menge (derzeit `keine_getragene_ruestung`); `pro_setting` ersetzt für ein Setting den kompletten Stufen-Block (gleichnamige Handicaps bedeuten je nach Setting Verschiedenes). Größe wirkt entweder über `groesse_modifikator` des Volkes ODER über ein Handicap — nie über beides. Absicherung: `test units/test_abgeleitete_werte.py`.
19. **Setting-Daten-Integrität**: `test units/test_setting_integritaet.py` prüft alle `settings/*.json` auf referenzielle Integrität. Die Whitelist in `setting_integritaet_whitelist.py` darf NUR SCHRUMPFEN — neue Verstöße in den Daten beheben, nicht whitelisten.
20. **Natürliche Waffen**: Klauen, Biss, Hörner und waffenlose Schläge aus Abstammung und Talenten werden NICHT fortgeschrieben, sondern in `functions/natuerliche_waffen.py` bei jeder Änderung neu abgeleitet und mit dem Inventar abgeglichen (kostenlos, gewichtslos). Regeln gehören in `config/natuerliche_waffen_config.json`, die Ausrüstungs-Einträge (Unterkategorie `Natürliche Waffe`) in ALLE `settings/*.json`. Synchronisiert wird bei Volk-Wahl/-Abwahl, Talent-Wahl/-Abwahl und beim Laden.
21. **Datenmigrationen für Bestandscharaktere**: Regeländerungen, die gespeicherte Werte betreffen, gehören in `functions/charakter_migration.py` (läuft in `from_dict` auf dem rohen Save-Dict). Reine Umbenennungen sind wiederholbar; Wertkorrekturen brauchen eine ID in `MIGRATIONS_IDS` und werden in `daten['migrationen']` vermerkt, damit sie genau einmal laufen.
