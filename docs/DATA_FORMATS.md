[← Zurück zur CLAUDE.md](../CLAUDE.md)

# Data Formats

## Character Save Files (`chars/*.json`)
Flat JSON with all character properties. Loaded/saved via `CharakterPersistence` mixin.

## Setting Data (`settings/*.json`)
JSON files containing setting-specific talents, powers, handicaps, races, and rules.

## Templates (`templates/*.json`)
Character archetypes validated against `character_template_schema.json`. Used by `auto_character_generator.py` for automated character creation.

## App Config (`config/app_config.json`)
Application preferences: theme (Dark/Light), primary palette, window size, auto-save settings, PDF options, backup config.
