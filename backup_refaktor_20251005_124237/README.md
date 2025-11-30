
# Backup der Charakterverwaltung-Refaktorierung
Erstellt am: 2025-10-05 12:42:37

## Was wurde refaktoriert:
1. CharakterVerwaltungWidget aus EinstellungenWidget ausgegliedert
2. Neuer Tab "Charakterverwaltung" mit Icon "account-multiple"
3. CharakterVerwaltungScreen in screens.py hinzugefügt
4. main.py um neuen Tab erweitert
5. Charakterverwaltungs-Funktionen aus EinstellungenWidget entfernt

## Betroffene Dateien:
- main.py: Neuer Tab hinzugefügt
- main.kv: CharakterVerwaltungScreen hinzugefügt
- views/charakter_verwaltung_widget.py: NEUE DATEI
- views/charakter_verwaltung_widget.kv: NEUE DATEI
- views/screens.py: CharakterVerwaltungScreen hinzugefügt
- views/einstellungen_widget.py: Charakterverwaltungs-Funktionen entfernt
- views/einstellungen_widget.kv: Charakterverwaltungs-UI entfernt

## Neue Funktionen:
- create_new_character
- schnellspeichern_charakter  
- speichere_charakter
- lade_charakter
- erzeuge_charakterbogen_pdf
- zeige_statblock
- zeige_element_statistiken
- Template-Management

## Rückgängig machen:
1. Backup-Dateien zurückkopieren
2. views/charakter_verwaltung_widget.* löschen
3. CharakterVerwaltungScreen aus screens.py entfernen
4. Tab aus main.py entfernen
