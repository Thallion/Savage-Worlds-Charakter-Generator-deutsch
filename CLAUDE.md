# CLAUDE.md - Savage Worlds Charakter-Generator (deutsch)

## Project Overview

A German-language character generator for the **Savage Worlds** tabletop RPG system. Built with Python/Kivy/KivyMD, it supports multiple game settings (SWAE, Deadlands, Fantasy Kompendium, Savage Pathfinder, HeXXen 1773, Sundered Skies) and runs on Desktop (Windows/Linux/macOS) and Android.

**License:** CC BY-NC-SA 4.0 (non-commercial)
**Current Version:** 0.5.7.4
**Python:** 3.8+ (3.11 recommended)

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

## Architecture

**Pattern:** Model-View-Controller (MVC) with Service Container for dependency injection.

```
main.py                    # Entry point - SW_Charakter_GeneratorApp(MDApp)
main.kv                    # Root Kivy layout
│
├── models/                # Data models (game entities)
│   ├── charakter.py       # Main character class (composed from mixins)
│   ├── charakter_properties.py   # Character properties mixin
│   ├── charakter_persistence.py  # Save/load mixin
│   ├── charakter_equipment.py    # Equipment management mixin
│   ├── charakter_elements.py     # Character elements mixin
│   ├── attribut.py        # Attributes (Stärke, Geschicklichkeit, etc.)
│   ├── fertigkeit.py      # Skills
│   ├── talent.py          # Edges/Talents
│   ├── macht.py           # Powers
│   ├── handicap.py        # Hindrances
│   ├── volk.py            # Races/Species
│   ├── waffe.py           # Weapons
│   ├── ruestung.py        # Armor
│   ├── schild.py          # Shields
│   ├── ausruestung.py     # Equipment base
│   ├── wuerfel.py         # Dice mechanics
│   └── settingregeln.py   # Setting-specific rules
│
├── views/                 # UI components (Kivy widgets + .kv layouts)
│   ├── screens.py         # Screen class definitions
│   ├── ui_components.py   # Shared UI components
│   ├── *_view.py/.kv      # Tab screens (profil, voelker, eigenschaften, etc.)
│   ├── *_popup.py/.kv     # Modal dialogs (talent, handicap, macht, waffe, etc.)
│   ├── pointbar_view.py   # Generation points progress bar
│   ├── historie_view.py   # Change history widget
│   └── einstellungen_widget.py  # Settings widget
│
├── controllers/           # Business logic
│   ├── charakter_controller.py  # Main controller (EventDispatcher)
│   ├── character_handler.py     # Character operations handler
│   ├── template_handler.py      # Template system
│   ├── game_elements_handler.py # Game element dialogs
│   └── decorators.py            # Utility decorators
│
├── services/              # Dependency-injected services
│   ├── service_container.py     # Singleton DI container
│   ├── config_service.py        # App configuration
│   ├── theme_service.py         # Theme management
│   ├── event_service.py         # Event/signal bus
│   ├── file_manager_service.py  # File I/O
│   ├── pdf_service.py           # PDF export
│   └── dialog_service.py        # Dialog management
│
├── manager/               # Domain-specific managers
│   ├── theme_manager.py         # Theme styling
│   ├── pdf_manager.py           # PDF generation
│   ├── statistics_manager.py    # Character stat calculations
│   └── volk_manager.py          # Race/species management
│
├── functions/             # Feature-specific utility functions
│   ├── auto_character_generator.py  # Auto-generation from templates
│   ├── talent_funktionen.py    # Talent selection logic
│   ├── handicap_funktionen.py  # Handicap selection logic
│   ├── macht_funktionen.py     # Power selection logic
│   ├── volk_funktionen.py      # Race/species functions
│   ├── ausruestung_funktionen.py    # Equipment functions
│   ├── eigenschaften_funktionen.py  # Attribute functions
│   ├── abgeleitete_werte.py    # Derived value calculations
│   ├── setting_funktionen.py   # Setting-specific logic
│   ├── character_advancement.py # Advancement rules
│   ├── statblock_generator.py  # Stat block generation
│   └── kompatibilitaets_pruefung.py # Compatibility checks
│
├── config/                # Configuration files (JSON)
│   ├── app_config.json          # App settings (theme, window, auto-save)
│   ├── eigenschaften_config.json # Attribute system config
│   ├── handicap_config.json     # Handicap cost config
│   ├── talent_config.json       # Talent system config
│   ├── macht_config.json        # Powers config
│   └── ausruestung_config.py    # Equipment config (Python module)
│
├── settings/              # Game setting data (JSON)
│   ├── SWAE.json                # Savage Worlds Adventure Edition
│   ├── Deadlands.json
│   ├── Fantasy Kompendium.json
│   ├── Savage Pathfinder.json
│   ├── HeXXen1773.json
│   └── Sundered Skies + FK.json
│
├── templates/             # Character templates (JSON)
│   ├── character_template_schema.json  # Validation schema
│   └── *.json                   # Named character archetypes
│
├── chars/                 # Saved characters (JSON + PDF exports)
├── assets/                # Static resources (images)
├── utils/                 # Utility modules (paths, PDF, logging)
└── test units/            # Test suite (unittest)
```

## Key Design Patterns

### Mixin-Based Character Model
The `Charakter` class in `models/charakter.py` is composed from four mixins:
- `CharakterProperties` - core character properties (Kivy properties)
- `CharakterPersistence` - JSON save/load
- `CharakterEquipment` - weapons, armor, shields
- `CharakterElements` - talents, handicaps, powers, skills

### Service Container (Singleton DI)
`services/service_container.py` provides a singleton `ServiceContainer` that manages all services. Access via `service_container` global instance. Services include: config, event, theme, file_manager, pdf, dialog, and the charakter_controller itself.

### Event-Driven UI
The controller uses Kivy `EventDispatcher` with custom events:
- `on_charakter_changed` - character data modified
- `on_charakter_updated` - UI refresh needed
- `on_charakter_loaded` - character loaded from file
- `on_charakter_error` - error during operation

### Tab-Based Navigation
The app uses `MDTabsPrimary` with 11 tabs: Einstellungen (Settings), Voelker (Races), Profil (Profile), Eigenschaften (Attributes), Handicaps, Talente (Talents/Edges), Maechte (Powers), Ausruestung (Equipment), Charakterbogen (Character Sheet), Historie (History), Info.

## Code Conventions

### Language
- **Domain terms are in German**: Eigenschaften (attributes), Fertigkeiten (skills), Talente (edges/talents), Handicaps (hindrances), Mächte (powers), Ausrüstung (equipment), Völker (races), Würfel (dice)
- **Docstrings and comments** are written in German
- **Variable and function names** use German for domain concepts: `waehle_talent()`, `speichern_als_json()`, `charakter`, `fertigkeit`
- **Module/file names** mix German domain terms with English structure: `charakter_controller.py`, `talent_funktionen.py`

### Naming
- **Classes:** PascalCase - `Charakter`, `CharakterController`, `TalenteWidget`
- **Functions/Methods:** snake_case - `lade_charakter()`, `aktualisiere_punkte()`
- **Files:** snake_case - `charakter_controller.py`, `auto_character_generator.py`
- **Constants:** UPPER_SNAKE_CASE

### Import Order
1. Standard library imports
2. Kivy/KivyMD imports
3. Project imports grouped by layer (models, controllers, views, services, functions, utils)

### View Files
Each view tab has a paired `.py` and `.kv` file (e.g., `profil_view.py` + `profil_view.kv`). Popups follow the same pattern (`talent_popup.py` + `talent_popup.kv`).

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

## Testing

Tests are in `test units/` using Python's `unittest` framework with mocking for Kivy/KivyMD components.

```bash
# Run all tests
python "test units/run_all_tests.py"

# Run a specific test module
python -m unittest "test units.test_theme_handler"

# Run a specific test case
python "test units/run_all_tests.py" test_theme_handler.TestThemeHandler.test_init
```

### Test Modules
- `test_theme_handler.py` - Theme service tests
- `test_character_handler.py` - Character operations tests
- `test_template_handler.py` - Template system tests
- `test_game_elements_handler.py` - Game element dialog tests
- `test_einstellungen_widget.py` - Settings widget integration tests
- `test_ausruestung_config.py` - Equipment configuration tests
- `test_ausruestung_funktionen.py` - Equipment function tests
- `test_auto_generator.py` - Auto character generation tests
- `test_eigenschaften_manager.py` - Attribute manager tests
- `test_talent_manager.py` - Talent manager tests
- `test_setting_funktionen.py` - Setting functions tests
- `test_leomara_*.py` / `test_hesindian_magier.py` - Character-specific regression tests
- `test_app_integration.py` - Application integration tests

### Testing Conventions
- Tests mock Kivy/KivyMD components to run without a display
- Service container is mocked for isolated unit tests
- Character-specific tests validate complete character creation workflows

## Data Formats

### Character Save Files (`chars/*.json`)
Flat JSON with all character properties. Loaded/saved via `CharakterPersistence` mixin.

### Setting Data (`settings/*.json`)
JSON files containing setting-specific talents, powers, handicaps, races, and rules.

### Templates (`templates/*.json`)
Character archetypes validated against `character_template_schema.json`. Used by `auto_character_generator.py` for automated character creation.

### App Config (`config/app_config.json`)
Application preferences: theme (Dark/Light), primary palette, window size, auto-save settings, PDF options, backup config.

## Build & Distribution

```bash
# Desktop builds (PyInstaller)
python build_linux.py          # Linux
python build_windows.py        # Windows
python build_desktop.py        # Platform-detected

# Android (Buildozer)
buildozer android debug        # Debug APK
bash build_android_local.sh    # Local Android build

# Windows via Wine (on Linux)
python build_windows_wine.py
```

Build specs: `savage_worlds_generator.spec` (Windows), `savage_worlds_generator_linux.spec` (Linux), `buildozer.spec` (Android).

## Important Notes for AI Assistants

1. **German domain language**: Always use German for game-domain terms in code (Charakter, Talent, Fertigkeit, etc.). Comments and docstrings should be in German.
2. **Kivy property system**: Character model uses Kivy `ObjectProperty`, `StringProperty`, `NumericProperty`, etc. Changes propagate to UI via Kivy bindings.
3. **KivyMD 2.0.1**: The project uses the development version from GitHub master, not the stable PyPI release. Widget APIs may differ from KivyMD docs.
4. **Mixin architecture**: When modifying the `Charakter` class, identify which mixin owns the functionality before editing.
5. **Service container**: Access services through `service_container` singleton, not by creating new instances.
6. **View/KV pairs**: When adding or modifying UI, update both the `.py` and `.kv` files.
7. **Config files are gitignored**: `config/app_config.json` and custom config files are in `.gitignore`. Don't rely on their committed state.
8. **Test directory has a space**: The test directory is `test units/` (with a space). Use quotes in paths.
9. **No CI pipeline in repo**: There are no GitHub Actions workflow files committed; builds are done locally.
10. **Character files are gitignored**: `chars/` directory is in `.gitignore`.
