[← Zurück zur CLAUDE.md](../CLAUDE.md)

# Code Conventions

## Language
- **Domain terms are in German**: Eigenschaften (attributes), Fertigkeiten (skills), Talente (edges/talents), Handicaps (hindrances), Mächte (powers), Superkräfte (super powers), Ausrüstung (equipment), Völker (races), Würfel (dice)
- **Docstrings and comments** are written in German
- **Variable and function names** use German for domain concepts: `waehle_talent()`, `speichern_als_json()`, `charakter`, `fertigkeit`
- **Module/file names** mix German domain terms with English structure: `charakter_controller.py`, `talent_funktionen.py`

## Naming
- **Classes:** PascalCase - `Charakter`, `CharakterController`, `TalenteWidget`
- **Functions/Methods:** snake_case - `lade_charakter()`, `aktualisiere_punkte()`
- **Files:** snake_case - `charakter_controller.py`, `auto_character_generator.py`
- **Constants:** UPPER_SNAKE_CASE

## Import Order
1. Standard library imports
2. Kivy/KivyMD imports
3. Project imports grouped by layer (models, controllers, views, services, functions, utils)

## View Files
Each view tab has a paired `.py` and `.kv` file (e.g., `profil_view.py` + `profil_view.kv`). Popups follow the same pattern (`talent_popup.py` + `talent_popup.kv`). Mobile-optimized layouts use `*_view_mobile.kv` files (e.g., `eigenschaften_view_mobile.kv`) — these are loaded on Android instead of the desktop `.kv` files. The Python logic is shared; only the `.kv` layout differs.
