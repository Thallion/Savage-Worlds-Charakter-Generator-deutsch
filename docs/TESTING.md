[← Zurück zur CLAUDE.md](../CLAUDE.md)

# Testing

Tests are in `test units/` using Python's `unittest` framework with mocking for Kivy/KivyMD components.

```bash
# Run all tests
python "test units/run_all_tests.py"

# Run a specific test module
python -m unittest "test units.test_theme_handler"

# Run a specific test case
python "test units/run_all_tests.py" test_theme_handler.TestThemeHandler.test_init
```

## Test Modules
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

## Testing Conventions
- Tests mock Kivy/KivyMD components to run without a display
- Service container is mocked for isolated unit tests
- Character-specific tests validate complete character creation workflows
