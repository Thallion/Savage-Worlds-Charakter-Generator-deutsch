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

## Kivy/Android Workarounds

This project contains several custom fixes for known Kivy/KivyMD issues, especially on Android. **Do not refactor or remove these patterns** — they solve real bugs that are hard to reproduce on Desktop.

### TextFieldScrollView (`views/ui_components.py`)
**Problem:** Kivy's `ScrollView` uses a `scroll_timeout` (55–200ms) to distinguish scroll from tap. During this timeout, touch events are not passed to children. This breaks `MDTextField` focus on Android — the keyboard appears briefly and disappears immediately.

**Root cause:** `kivy/kivy#4399`, `kivy/kivy#890`, `kivy/kivy#7320` — ScrollView steals the touch before TextField can process it.

**Solution:** `TextFieldScrollView` extends `MDScrollView`:
1. On `touch_down`: records the touch position and finds any `MDTextField` under it
2. On `touch_up`: checks if it was a tap (movement < `dp(30)`) vs. a scroll gesture
3. If tap: forces `field.focus = True` via `Clock.schedule_once()` (twice: immediately + 100ms delay as safety net)

```python
# Usage: Replace MDScrollView with TextFieldScrollView in any layout containing MDTextField
from views.ui_components import TextFieldScrollView

scroll = TextFieldScrollView(size_hint_y=1)
scroll.add_widget(content_with_textfields)
```

**Important:** Always use `TextFieldScrollView` instead of `MDScrollView` when the scroll area contains `MDTextField` widgets. This applies to all popups, overlays, and wizard dialogs.

### Checkbox/Button Debounce Pattern (Android Touch Bounce)
**Problem:** On Android, touch events on `MDListItemTrailingCheckbox` and `MDButton` can fire multiple times for a single tap. This causes talents to be selected twice, checkboxes to toggle back, or actions to execute twice.

**Root cause:** Android touch screens report multiple touch events within a short window. Kivy's `on_release` fires for each event. This is especially problematic with checkboxes in lists (`MDListItem` + `MDListItemTrailingCheckbox`) where the list item and checkbox both process the touch.

**IMPORTANT:** `on_active` event does NOT work reliably on Android - it still triggers bounce effects. Always use `on_release` with debounce.

**Solution 1 - Single checkbox with debounce (recommended):** Use `on_release` with time-based debounce:

```python
import time

# Binding - use separate variable to avoid closure issue:
checkbox = MDListItemTrailingCheckbox()
cb = checkbox
checkbox.bind(on_release=lambda x, cb=cb: self._on_checkbox_clicked(cb))

def _on_checkbox_clicked(self, checkbox):
    """Handler mit Debounce für Checkbox-Klick."""
    now = time.monotonic()
    if hasattr(self, '_last_checkbox_time') and (now - self._last_checkbox_time) < 0.5:
        return  # Bounce ignorieren
    self._last_checkbox_time = now
    
    # Eigentliche Logik hier
    self.some_state = checkbox.active
```

**Solution 2 - Multiple checkboxes in loop (CRITICAL):** When creating checkboxes in a loop, you MUST use intermediate variables to capture the current values. NEVER use the checkbox variable directly in the lambda:

```python
# FALSCH - causes closure issue:
for item in items:
    checkbox = MDListItemTrailingCheckbox()
    checkbox.bind(on_release=lambda x, cb=checkbox: self._on_clicked(cb))  # Bug!

# RICHTIG - use intermediate variable:
for item in items:
    checkbox = MDListItemTrailingCheckbox()
    cb = checkbox  # Separate variable
    checkbox.bind(on_release=lambda x, cb=cb: self._on_clicked(cb))
```

**Solution 3 - Separate popup dialog (STANDARD — IMMER VERWENDEN):** Checkboxen MÜSSEN IMMER in ein eigenes separates Popup mit eigenem ScrollView ausgegliedert werden. Checkboxen direkt in einen bestehenden Dialog einzubetten funktioniert auf Android nicht zuverlässig (Touch-Probleme, nested ScrollView). Das separate Popup löst das Problem vollständig.

**Vorlagen für dieses Pattern:**
- Setting-Auswahl bei "Neuer Charakter" (`views/einstellungen_widget.py`)
- Modus-Auswahl im Setting Assistent (`views/setting_assistent_view.py`)
- Elemente-Auswahl (Handicaps, Fertigkeiten etc.) im Setting Assistent (`views/setting_assistent_view.py`)
- Volkseigenarten-Checkboxen (`views/volk_popup.py`)

**Ablauf bei Dialogen mit Checkboxen:**
1. Zuerst ein separates Optionen-Popup für Checkboxen zeigen
2. Checkbox-Werte in temp-Variablen speichern
3. Popup schließen
4. Dann den eigentlichen Aktions-Dialog zeigen (der die temp-Werte verwendet)

```python
def _show_options_popup(self):
    """Separates Popup für Checkbox-Optionen"""
    from kivymd.uix.scrollview import MDScrollView
    from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox

    content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(160), padding=dp(16))
    
    checkbox_list = MDList(size_hint_y=None)
    checkbox_list.bind(minimum_height=checkbox_list.setter('height'))
    
    # Checkbox erstellen mit Intermediate Variable + Debounce
    item = MDListItem(size_hint_y=None, height=dp(48))
    item.add_widget(MDListItemSupportingText(text="Option Name"))
    self.my_checkbox = MDListItemTrailingCheckbox()
    cb = self.my_checkbox  # Intermediate variable!
    self.my_checkbox.bind(on_release=lambda x, cb=cb: self._on_checkbox_clicked(cb))
    item.add_widget(self.my_checkbox)
    checkbox_list.add_widget(item)
    
    scroll = MDScrollView(do_scroll_x=False, do_scroll_y=True, bar_width=dp(15))
    scroll.add_widget(checkbox_list)
    content.add_widget(scroll)
    
    self._options_popup = MDDialog(
        MDDialogHeadlineText(text="Optionen"),
        MDDialogContentContainer(content),
        MDDialogButtonContainer(
            MDButton(MDButtonText(text="Abbrechen"), style="text",
                     on_release=lambda x: self._options_popup.dismiss()),
            MDButton(MDButtonText(text="Weiter"), style="filled",
                     on_release=lambda x: self._on_options_confirmed()),
        ),
        size_hint=(0.85, None),
    )
    self._options_popup.open()

def _on_options_confirmed(self):
    """Werte speichern, Popup schließen, nächsten Dialog zeigen"""
    self.temp_value = self.my_checkbox.active
    self._options_popup.dismiss()
    self._show_next_dialog()  # Aktions-Dialog ohne Checkboxen
```

**Working pattern (tested on Android):** `on_release` + debounce in handler - this is the ONLY reliable pattern.

**Solution 3 - Separate popup dialog (STANDARD — IMMER VERWENDEN):** 
Checkboxen MÜSSEN IMMER in ein eigenes separates Popup mit eigenem ScrollView ausgegliedert werden. 
Checkboxen direkt in einen bestehenden Dialog einzubetten funktioniert auf Android nicht zuverlässig 
(Touch-Probleme, nested ScrollView). Das separate Popup löst das Problem vollständig.

**STANDARD-MUSTER für alle Checkboxen mit ScrollView:**

```python
# Schritt 1: Separates Optionen-Popup mit Checkboxen
def _show_options_popup(self):
    from kivymd.uix.scrollview import MDScrollView
    from kivymd.uix.list import MDList, MDListItem, MDListItemSupportingText, MDListItemTrailingCheckbox

    content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(160), padding=dp(16))
    
    checkbox_list = MDList(size_hint_y=None)
    checkbox_list.bind(minimum_height=checkbox_list.setter('height'))
    
    # Checkbox mit Intermediate Variable + Debounce
    item = MDListItem(size_hint_y=None, height=dp(48))
    item.add_widget(MDListItemSupportingText(text="Meine Option"))
    self.my_checkbox = MDListItemTrailingCheckbox()
    cb = self.my_checkbox  # Intermediate variable!
    self.my_checkbox.bind(on_release=lambda x, cb=cb: self._on_checkbox_clicked(cb))
    item.add_widget(self.my_checkbox)
    checkbox_list.add_widget(item)
    
    scroll = MDScrollView(do_scroll_x=False, do_scroll_y=True, bar_width=dp(15))
    scroll.add_widget(checkbox_list)
    content.add_widget(scroll)
    
    self._options_popup = MDDialog(
        MDDialogHeadlineText(text="Optionen"),
        MDDialogContentContainer(content),
        MDDialogButtonContainer(
            MDButton(MDButtonText(text="Abbrechen"), style="text",
                     on_release=lambda x: self._options_popup.dismiss()),
            MDButton(MDButtonText(text="Weiter"), style="filled",
                     on_release=lambda x: self._on_options_confirmed()),
        ),
        size_hint=(0.85, None),
    )
    self._options_popup.open()

def _on_checkbox_clicked(self, checkbox):
    """Handler mit Debounce für Checkbox-Klick."""
    now = time.monotonic()
    if hasattr(self, '_last_checkbox_time') and (now - self._last_checkbox_time) < 0.5:
        return  # Bounce ignorieren
    self._last_checkbox_time = now
    self.temp_value = checkbox.active

def _on_options_confirmed(self):
    """Werte speichern, Popup schließen, nächsten Dialog zeigen"""
    self.temp_value = self.my_checkbox.active
    self._options_popup.dismiss()
    self._show_action_dialog()  # Aktions-Dialog ohne Checkboxen
```

**Wann welches Pattern verwenden:**

| Pattern | Anwendungsfall | Empfehlung |
|---------|---------------|------------|
| Solution 1 (Single + Debounce) | Einzelne Checkbox in bestehendem Dialog | Nur wenn SEHR wenige Checkboxen |
| Solution 2 (Loop + Debounce) | Checkboxen in einer Schleife | Nur für sehr einfache Fälle |
| **Solution 3 (Separate Popup)** | **Alle anderen Fälle mit ScrollView** | **STANDARD - IMMER VERWENDEN** |

**Warum Solution 3 der STANDARD ist:**
1. Eigener ScrollView verhindert nested ScrollView-Probleme
2. Checkboxen werden vom restlichen Dialog-Code getrennt
3. Einfachere Fehlersuche und Wartung
4. Bewährtes Pattern aus: Char Verwaltung (Setting-Auswahl), Volkseigenarten, HTML-Export

**Wo dieses Pattern bereits verwendet wird (als Vorlage):**
- `views/charakter_verwaltung_widget.py` — Setting-Auswahl bei "Neuer Charakter"
- `views/element_overlay.py` — multi-select checkboxes (hat Debounce, aber im Overlay)
- `views/volk_popup.py` — Volkseigenarten Checkboxen
- `views/setting_assistent_view.py` — Modus-Auswahl und Elemente-Auswahl
- `manager/html_manager.py` — HTML/PDF Export-Optionen

**Kritische Regel:** Wenn du auch nur eine Checkbox in einem Dialog mit ScrollView hast, 
verwende IMMER Solution 3 (Separate Popup). Das ist der zuverlässigste Weg auf Android.

**Where this pattern is used (checkboxes with debounce):**
- `views/element_overlay.py` — multi-select checkboxes (Vorlage!)
- `views/setting_assistent_view.py` — handicaps, fertigkeiten etc. checkboxes (funktioniert!)
- `views/setting_assistent_view.py` — basis/merge selection via popup (NEU - funktioniert!)
- `views/talente_view.py` — talent selection/deselection
- `views/maechte_view.py` — power selection/deselection  
- `views/eigenschaften_view.py` — double-cost confirmation
- `views/template_wizard.py` — skill/handicap/edge/power checkboxes
- `manager/html_manager.py` — HTML export options in separatem Popup → dann Speicher-Dialog
- `manager/pdf_manager.py` — PDF export options checkboxes
- `views/volk_popup.py` — Volkseigenarten in separatem Popup

**Where this pattern is used (navigation buttons):**
- `views/wizard_bar.py` — prev/next/cancel/skip buttons
- `views/setting_assistent_view.py` — wizard step navigation
- `views/template_wizard.py` — wizard step navigation
- `views/volk_popup.py` — wizard step navigation

**Important:** ALWAYS use `on_release` with 500ms debounce for checkboxes on Android. Do NOT use `on_active` - it does NOT solve the bounce problem. The 500ms window is calibrated for Android touch screens - do not reduce it. When using lambdas in loops, ALWAYS use intermediate variables to capture the current checkbox value.

### Touch Propagation in Cards (Mobile)
**Problem:** When an `MDCard` with `on_release` contains interactive child widgets (`MDButton`, `MDIconButton`), the child widgets capture the touch event on mobile, preventing the card's `on_release` from firing.

**Solution:** On mobile, use non-interactive display widgets instead of buttons for icons inside clickable cards:

```python
if _mobile:
    # MDIcon is non-interactive — touch passes through to the card
    from kivymd.uix.label import MDIcon
    icon = MDIcon(icon="star", size_hint_x=None, width=dp(28))
    card_content.add_widget(icon)
else:
    # On desktop, MDButton with tonal style for visual accent
    icon_btn = MDButton(style="tonal", size_hint_x=None, width="48dp")
    icon_btn.add_widget(MDButtonIcon(icon="star"))
    card_content.add_widget(icon_btn)
```

**Where this pattern is used:**
- `views/setting_assistent_view.py` — category cards and mode selection cards

### Delete Dialogs mit Checkboxen
**Problem:** Die "Löschen"-Dialoge in Einstellungen (Volk, Talent, Macht, etc.) haben Checkboxen im ElementOverlay, die auf Android Touch-Bounce-Probleme haben. Das funktioniert schlechter als die Setting-Auswahl in "Neuer Charakter".

**Lösung - Two-Phase Pattern (NEU - STANDARD für Delete-Dialoge):**
1. **Phase 1:** ElementOverlay öffnen mit Checkboxen (mit Debounce, wie bisher)
2. **Phase 2:** Wenn der Benutzer auf "Löschen" klickt, EIN SEPARATES Popup öffnen zur Bestätigung
   - Keine Checkboxen im Bestätigungs-Popup
   - Das Bestätigungs-Popup zeigt die ausgewählten Elemente als Text-Liste

**Alternative - Noch besser: Setting-Auswahl Pattern reproduzieren:**
Die Setting-Auswahl bei "Neuer Charakter" in `charakter_verwaltung_widget.py:185-243` ist das beste Pattern:
- MDListItem mit on_release auf dem Item (nicht auf der Checkbox)
- Checkbox nur zur visuellen Anzeige, nicht für Event-Handling
- Beim Klick auf das Item wird die Selection-Logik ausgeführt

**Vorlage für neue Delete-Dialoge:**
```python
def _show_delete_options_popup(self):
    """Phase 1: Optionen-Popup mit Checkboxen"""
    # Das bestehende ElementOverlay mit Debounce verwenden
    # ODER: Das Setting-Auswahl-Pattern aus charakter_verwaltung_widget adaptieren
    pass

def _show_delete_confirmation_popup(self, selected_items):
    """Phase 2: Bestätigungs-Popup OHNE Checkboxen"""
    # Hier nur Buttons für Bestätigung/Abbrechen
    # Ausgewählte Items als Text anzeigen
    pass
```

**Wo dieses Two-Phase Pattern implementiert werden sollte:**
- `views/talent_popup.py` - Talent löschen
- `views/handicap_popup.py` - Handicap löschen
- `views/macht_popup.py` - Macht löschen
- `views/fertigkeit_popup.py` - Fertigkeit löschen
- `views/volk_popup.py` - Volk löschen
- usw.

**WICHTIG:** Bestehende Implementierungen mit ElementOverlay (die funktionieren) NICHT ändern, außer sie haben nachweislich Probleme auf Android. Das ElementOverlay hat bereits Debounce im _on_checkbox_toggled Handler.

### MDDialog Fixed Height (Mobile)
**Problem:** `MDDialog` does not support `size_hint_y=1` for child layouts (`MDDialogContentContainer`). Using it causes the content to collapse to the bottom of the dialog with a huge empty gap above.

**Solution:** Always use `size_hint_y=None` with a calculated fixed height for the main content layout inside dialogs:

```python
from kivy.core.window import Window

# Calculate available height: dialog_height - headline - padding
main_layout_height = Window.height * 0.95 - dp(80)
main_layout = MDBoxLayout(orientation="vertical", size_hint_y=None, height=main_layout_height)
```

### SearchBottomSheet (`views/ui_components.py`)
**Problem:** `MDDialog` with search fields has severe touch issues on Android — the dialog's touch handling conflicts with the TextField and list scrolling.

**Solution:** Custom `SearchBottomSheet` using `ModalView` instead of `MDDialog`:
- Transparent background with scrim layer for dismiss
- Slide-up/down animation
- Integrated search field with filtered list
- Used for race/species selection and other searchable lists

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
17. **Checkboxen IMMER in separates Popup**: Checkboxen dürfen NIEMALS direkt in einen bestehenden Dialog eingebettet werden. Sie müssen IMMER in ein eigenes separates Popup mit eigenem ScrollView ausgegliedert werden. Erst Optionen-Popup zeigen → Werte in temp-Variablen speichern → Popup schließen → dann Aktions-Dialog zeigen. Siehe "Separate popup dialog (STANDARD)" in den Kivy/Android Workarounds. Vorlagen: Setting-Auswahl (Neuer Charakter), Modus-Auswahl (Setting Assistent), Elemente-Auswahl (Setting Assistent), Volkseigenarten (volk_popup.py), HTML-Export (html_manager.py).
