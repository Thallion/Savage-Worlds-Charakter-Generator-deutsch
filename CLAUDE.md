# CLAUDE.md - Savage Worlds Charakter-Generator (deutsch)

## Project Overview

A German-language character generator for the **Savage Worlds** tabletop RPG system. Built with Python/Kivy/KivyMD, it supports multiple game settings (SWAE, Deadlands, Fantasy Kompendium, Savage Pathfinder, HeXXen 1773, Sundered Skies, Horror Kompendium, Rippers, SciFi Kompendium, Superkräfte Kompendium, 50 Fathoms, Hellfrost) and runs on Desktop (Windows/Linux/macOS) and Android.

**License:** CC BY-NC-SA 4.0 (non-commercial)
**Current Version:** 0.6.5.1
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
│   ├── superkraft.py      # Super Powers (Superkräfte)
│   ├── handicap.py        # Hindrances
│   ├── volk.py            # Races/Species
│   ├── waffe.py           # Weapons
│   ├── ruestung.py        # Armor
│   ├── schild.py          # Shields
│   ├── ausruestung.py     # Equipment base
│   ├── wuerfel.py         # Dice mechanics
│   ├── settingregeln.py   # Setting-specific rules
│   └── setting_draft.py   # Setting draft model for setting assistant
│
├── views/                 # UI components (Kivy widgets + .kv layouts)
│   ├── screens.py         # Screen class definitions
│   ├── ui_components.py   # Shared UI components
│   ├── *_view.py/.kv      # Tab screens (profil, voelker, eigenschaften, etc.)
│   ├── *_view_mobile.kv   # Smartphone-optimized layouts (loaded on Android/mobile)
│   ├── *_popup.py/.kv     # Modal dialogs (11 popups: talent, handicap, macht, etc.)
│   ├── setting_wechsel_overlay.py  # Slide-in overlay for setting switching
│   ├── setting_assistent_view.py   # Setting creation/editing assistant
│   ├── template_wizard.py          # Template creation wizard
│   ├── tutorial_overlay.py         # Tutorial spotlight overlay
│   ├── wizard_bar.py              # Wizard progress bar
│   ├── superkraefte_view.py  # Super powers widget
│   ├── charakter_verwaltung_widget.py/.kv  # Character management widget
│   ├── pointbar_view.py   # Generation points progress bar
│   ├── historie_view.py   # Change history widget
│   └── einstellungen_widget.py  # Settings widget
│
├── controllers/           # Business logic
│   ├── charakter_controller.py  # Main controller (EventDispatcher)
│   ├── character_handler.py     # Character operations handler
│   ├── template_handler.py      # Template system
│   ├── game_elements_handler.py # Game element dialogs
│   ├── undo_manager.py          # Undo/redo functionality
│   └── decorators.py            # Utility decorators
│
├── services/              # Dependency-injected services
│   ├── service_container.py     # Singleton DI container
│   ├── config_service.py        # App configuration
│   ├── theme_service.py         # Theme management
│   ├── event_service.py         # Event/signal bus
│   ├── tutorial_service.py      # Tutorial management & state
│   ├── wizard_service.py        # Character creation wizard
│   ├── file_manager_service.py  # File I/O
│   ├── pdf_service.py           # PDF export
│   ├── dialog_service.py        # Dialog management
│   ├── backup_service.py        # Backup management
│   └── html_service.py          # HTML generation
│
├── manager/               # Domain-specific managers
│   ├── theme_manager.py         # Theme styling
│   ├── pdf_manager.py           # PDF generation
│   ├── html_manager.py          # HTML export
│   ├── statistics_manager.py    # Character stat calculations
│   └── volk_manager.py          # Race/species management
│
├── functions/             # Feature-specific utility functions
│   ├── auto_character_generator.py  # Auto-generation from templates
│   ├── talent_funktionen.py    # Talent selection logic
│   ├── handicap_funktionen.py  # Handicap selection logic
│   ├── macht_funktionen.py     # Power selection logic
│   ├── superkraft_funktionen.py # Super power selection logic
│   ├── volk_funktionen.py      # Race/species functions
│   ├── ausruestung_funktionen.py    # Equipment functions
│   ├── eigenschaften_funktionen.py  # Attribute functions
│   ├── abgeleitete_werte.py    # Derived value calculations
│   ├── setting_funktionen.py   # Setting-specific logic
│   ├── setting_merge.py        # Setting merge and conflict resolution
│   ├── character_advancement.py # Advancement rules
│   ├── statblock_generator.py  # Stat block generation
│   ├── cyberware_funktionen.py  # Cyberware mechanics (SciFi)
│   └── kompatibilitaets_pruefung.py # Compatibility checks
│
├── config/                # Configuration files (JSON)
│   ├── app_config.json          # App settings (theme, window, auto-save)
│   ├── tutorial_config.json     # Tutorial content and configuration
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
│   ├── Horror Kompendium.json
│   ├── Rippers.json
│   ├── Savage Pathfinder.json
│   ├── SciFi Kompendium.json
│   ├── Superkräfte Kompendium.json
│   ├── HeXXen1773.json
│   ├── Sundered Skies.json
│   ├── 50 Fathoms.json
│   └── Hellfrost.json
│
├── templates/             # Character templates (JSON)
│   ├── character_template_schema.json  # Validation schema
│   └── *.json                   # Named character archetypes
│
├── chars/                 # Saved characters (JSON + PDF exports)
├── assets/                # Static resources (images, logos)
├── docs/                  # Documentation and planning (plans, tutorials)
├── scripts/               # Utility scripts (e.g., merge_swae_into_kompendien.py)
├── src/                   # Platform-specific sources (Android manifest)
├── utils/                 # Utility modules
│   ├── logging_setup.py         # Logging infrastructure
│   ├── logging_utils.py         # Logging helpers
│   ├── path_utils.py            # Path utilities
│   ├── platform_utils.py        # Platform detection
│   ├── desktop_scaling.py       # HiDPI scaling
│   ├── pdf_utils.py             # PDF export utilities
│   ├── html_utils.py            # HTML export utilities
│   ├── custom_filemanager.py    # File browser widget
│   ├── app_integration.py       # App integration utilities
│   ├── intent_handler.py        # Android intent handling
│   ├── resource_extractor.py    # Resource extraction
│   └── share_utils.py           # File sharing (Android MediaStore)
│
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

### Dialog & Snackbar Pattern
- **MDDialog** for decisions that need user action (errors, confirmations, choices). Always use `size_hint=(0.85, None)` to prevent full-screen dialogs on Android.
- **MDSnackbar** (via `dialog_service.show_snackbar()`) for non-blocking info/warnings. `show_success_dialog()` and `show_warning_dialog()` are implemented as snackbar calls. `show_error_dialog()` remains a modal dialog.
- **Slide-in Overlay** for setting switching (`setting_wechsel_overlay.py`), replacing the previous MDDialog approach for a smoother UX.
- When adding new user-facing warnings (e.g., "not enough points"), use `dialog_service.show_warning_dialog()` — do not just use `Logger.warning()`.

## Tutorial & Wizard Systems

### Tutorial Service (`services/tutorial_service.py`)
Manages guided user introduction and contextual help:
- **Welcome Tutorial**: Multi-step introduction with spotlight highlighting
- **Tab-specific Hints**: Contextual help for each UI section
- **Tutorial State**: Tracks which tutorials have been shown
- **Configuration**: Loads from `config/tutorial_config.json`

Key features:
- `show_welcome_tutorial()` - displays initial guided tour
- `show_tab_hint(tab_id)` - shows contextual help for specific tabs
- `mark_tutorial_completed()` - tracks tutorial completion state
- `is_tutorial_shown()` - checks if specific tutorial was already shown

### Tutorial Overlay (`views/tutorial_overlay.py`)
Interactive tutorial overlay with spotlight functionality:
- **SpotlightOverlay**: Semi-transparent overlay with cutout highlighting
- **Tutorial Cards**: Context-aware help cards with navigation
- **Interactive Elements**: Next/Previous/Skip functionality
- **Responsive Layout**: Adapts to desktop/mobile layouts

### Character Creation Wizard (`services/wizard_service.py`)
Step-by-step guided character creation:
- **WizardSchritt**: Individual wizard step with validation
- **WizardService**: Event-driven wizard state management
- **Step Validation**: Each step can validate character state
- **Progress Tracking**: Visual progress indication via `wizard_bar.py`

Wizard steps include:
1. Setting selection
2. Race selection  
3. Profile setup
4. Attribute distribution
5. Skill allocation
6. Handicap selection
7. Talent selection
8. Equipment purchase

### Setting Assistant (`views/setting_assistent_view.py`)
Multi-step wizard for creating and editing game settings:
- **4-Step Process**: Basic info → Element configuration → Conflict resolution → Preview
- **Merge Functionality**: Combine multiple existing settings
- **Conflict Resolution**: Handle overlapping elements when merging
- **Draft Management**: Save/restore work in progress via `models/setting_draft.py`

### Template Wizard (`views/template_wizard.py`)
Guided creation of character templates:
- **Multi-step Dialog**: Captures template metadata and configuration
- **Character Analysis**: Analyzes current character for template creation
- **Validation**: Ensures template completeness and validity
- **JSON Export**: Saves templates in standardized format

### Integration Points
- **ServiceContainer**: All tutorial/wizard services are dependency-injected
- **Event System**: Wizard progress triggers UI updates via event service
- **Configuration**: Tutorial content and wizard steps are configurable via JSON
- **Mobile Optimization**: All wizards adapt to mobile layouts automatically

## Code Conventions

### Language
- **Domain terms are in German**: Eigenschaften (attributes), Fertigkeiten (skills), Talente (edges/talents), Handicaps (hindrances), Mächte (powers), Superkräfte (super powers), Ausrüstung (equipment), Völker (races), Würfel (dice)
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
Each view tab has a paired `.py` and `.kv` file (e.g., `profil_view.py` + `profil_view.kv`). Popups follow the same pattern (`talent_popup.py` + `talent_popup.kv`). Mobile-optimized layouts use `*_view_mobile.kv` files (e.g., `eigenschaften_view_mobile.kv`) — these are loaded on Android instead of the desktop `.kv` files. The Python logic is shared; only the `.kv` layout differs.

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
- `test_ausruestung_settings.py` - Equipment settings tests
- `test_auto_generator.py` - Auto character generation tests
- `test_eigenschaften_manager.py` - Attribute manager tests
- `test_talent_manager.py` - Talent manager tests
- `test_setting_funktionen.py` - Setting functions tests
- `test_fertigkeit_steigerung.py` - Skill advancement tests
- `test_charakter_verwaltung.py` - Character management tests
- `test_hesindian_magier.py` - Character-specific regression test
- `test_kompendium_*.py` - Kompendium class tests (cleric, barbarian, bard, druid, mage)
- `test_korrekte_reihenfolge.py` - Correct ordering tests
- `test_superkraft_model.py` - Super power model tests
- `test_superkraft_popup.py` - Super power popup tests
- `test_superkraft_integration.py` - Super power integration tests
- `test_kraefte_widget.py` - Powers widget tests
- `test_cyberware.py` - Cyberware mechanics tests
- `test_html_service.py` - HTML service tests
- `test_html_utils.py` - HTML utility tests
- `test_backup_service.py` - Backup service tests
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
python build_all.py            # All platforms

# Android (Buildozer)
python build_android.py        # Android APK
buildozer android debug        # Direct Buildozer

# Windows via Wine (on Linux)
python build_windows_wine.py
```

Build specs: `savage_worlds_generator.spec` (Windows), `savage_worlds_generator_linux.spec` (Linux), `savage_worlds_generator_wine.spec` (Wine), `buildozer.spec` (Android).

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
