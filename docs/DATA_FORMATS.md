[← Zurück zur CLAUDE.md](../CLAUDE.md)

# Data Formats

## Character Save Files (`chars/*.json`)
Flat JSON with all character properties. Loaded/saved via `CharakterPersistence` mixin.

Neben den Auswahllisten stehen dort drei Felder, die beim Laden gebraucht werden:

- `natuerliche_waffen`: Namen der kostenlos aus Abstammung/Talenten gestellten
  Waffen. Nur diese Einträge werden wieder eingesammelt, selbst gekaufte bleiben
  (`functions/natuerliche_waffen.py`).
- `startgeld_einloesungen`: Wie oft Handicap-Punkte in Startkapital umgewandelt
  wurden — Grundlage für die Rücknahme (`functions/character_advancement.py`).
- `migrationen`: Bereits angewendete Wertkorrekturen, damit sie nicht doppelt
  laufen (`functions/charakter_migration.py`). Reine Umbenennungen brauchen
  keinen Eintrag, sie sind wiederholbar.

## Setting Data (`settings/*.json`)
JSON files containing setting-specific talents, powers, handicaps, races, and rules.

Ausrüstungs-Einträge dürfen eine `unterkategorie` tragen. Die natürlichen Waffen
(Kategorie `Waffe`, Unterkategorie `Natürliche Waffe`, Kosten und Gewicht 0)
liegen in JEDEM Setting vor — `functions/natuerliche_waffen.py` legt nur ab, was
im Katalog des aktiven Settings steht.

## Templates (`templates/*.json`)
Character archetypes validated against `character_template_schema.json`. Used by `auto_character_generator.py` for automated character creation.

## App Config (`config/app_config.json`)
Application preferences: theme (Dark/Light), primary palette, window size, auto-save settings, PDF options, backup config.
