[← Zurück zur CLAUDE.md](../CLAUDE.md)

# Architecture

**Pattern:** Model-View-Controller (MVC) with Service Container for dependency injection.

## Vollständiger Verzeichnisbaum

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
│   ├── cyberware.py       # Cyberware (SciFi)
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
│   ├── element_overlay.py          # Multi-select overlay (talents, handicaps, etc.)
│   ├── voelker_auswahl_overlay.py  # Race selection overlay
│   ├── pointbar_overlay.py         # Generation-points overlay
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
│   ├── charakter_speicher.py   # Character persistence helpers
│   ├── volkseigenarten_funktionen.py # Race traits logic (Volkseigenarten)
│   └── kompatibilitaets_pruefung.py # Compatibility checks
│
├── config/                # Configuration files (JSON)
│   ├── app_config.json          # App settings (theme, window, auto-save)
│   ├── tutorial_config.json     # Tutorial content and configuration
│   ├── eigenschaften_config.json # Attribute system config
│   ├── handicap_config.json     # Handicap cost config
│   ├── talent_config.json       # Talent system config
│   ├── macht_config.json        # Powers config
│   ├── volkseigenarten_config.json        # Race traits config
│   ├── custom_volkseigenarten_config.json # User-defined race traits
│   ├── cyberware_config.json    # Cyberware config (SciFi)
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
