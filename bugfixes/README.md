# Kivy/KivyMD Bugfixes

Dokumentation und minimale Reproduktions-Beispiele für Kivy/KivyMD Bugs,
die im Savage Worlds Charakter-Generator aufgetreten sind.

## Struktur

```
bugfixes/
├── main.py                          # Übergeordnete Test-App (alle Bugs in einer App)
├── buildozer.spec                   # Android-Build für die Test-App
├── minimal_code.md                  # Richtlinien für minimale Code-Beispiele
├── README.md                        # Dieses Dokument
│
├── kivy/                            # Kivy-spezifische Bugs
│   ├── scrollview_textfield_focus.py       (+ _fix.py)
│   ├── checkbox_touch_bounce.py            (+ _fix.py)
│   ├── mdscrollview_touch_move_crash.py    (+ _fix.py)
│   ├── textinput_bubble_hang.py            (+ _fix.py)
│   ├── card_touch_propagation.py           (+ _fix.py)
│   └── nav_touch_scrollview_conflict.py    (+ _fix.py)
│
└── kivymd/                          # KivyMD-spezifische Bugs
    ├── dialog_fullscreen_android.py        (+ _fix.py)
    └── dialog_touch_stealing.py            (+ _fix.py)
```

Jeder Bug hat zwei Dateien:
- `<name>.py` — demonstriert das fehlerhafte Verhalten
- `<name>_fix.py` — demonstriert den Workaround

Alle Dateien sind selbstständige Kivy-Apps nach dem "MINIMAL CODE" Prinzip:
Copy → Paste → Run.

## Test-App ausführen

### Desktop

```bash
cd bugfixes
python main.py
```

### Android

```bash
cd bugfixes
buildozer -v android debug
buildozer android deploy run logcat
```

Die Test-App hat drei Tabs:
- **Kivy Bugs** — Touch-, Scroll-, Focus-Probleme
- **KivyMD Bugs** — Dialog-Probleme
- **Info** — Plattform-Informationen und Hinweise

Jeder Bug wird als Karte dargestellt mit zwei Buttons:
- **Show Bug** — startet die fehlerhafte Version
- **Show Fix** — startet die korrigierte Version

## Dokumentierte Bugs

### Kivy Bugs

| # | Titel | Referenz | Plattform | Status |
|---|-------|----------|-----------|--------|
| 1 | ScrollView Steals TextField Focus | kivy/kivy#4399, #890, #7320 | Android/Touch | ✓ Workaround |
| 2 | Checkbox Touch Bounce | Android Multi-Fire | Android | ✓ Workaround (500ms Debounce) |
| 3 | MDScrollView on_touch_move TypeError | KivyMD 2.0.1.dev0 | Alle | ✓ Monkey-Patch |
| 4 | TextInput Bubble/Handles Hang | PR #142 | Android | ✓ Monkey-Patch |
| 5 | Card on_release Blocked by Children | Touch Propagation | Android/Mobile | ✓ Widget-Wahl |
| 6 | Bottom-Nav Delayed After Scroll | PR #150, #152 | Android | ✓ on_touch_down |

### KivyMD Bugs

| # | Titel | Referenz | Plattform | Status |
|---|-------|----------|-----------|--------|
| 7 | MDDialog Fullscreen on Android | KivyMD 2.0.1.dev0 | Android | ✓ size_hint=(0.85, None) |
| 8 | MDDialog Steals Touch (Search) | PRs #109, #116, #120, #121 | Android | ✓ ModalView Ersatz |

## Weiterführende Informationen

Diese Bugs sind ausführlich in `CLAUDE.md` des Haupt-Repositories dokumentiert
unter den Abschnitten:

- **Kivy/Android Workarounds** (Hauptteil)
- **TextFieldScrollView** — Custom-Widget für ScrollView+TextField
- **Checkbox/Button Debounce Pattern** — 500ms Android Touch-Bounce
- **Touch Propagation in Cards (Mobile)** — MDIcon statt MDButton
- **Delete Dialogs mit Checkboxen** — Two-Phase Pattern
- **MDDialog Fixed Height (Mobile)** — size_hint_y=None
- **SearchBottomSheet** — ModalView statt MDDialog

Die tatsächlichen Implementierungen im Produktiv-Code befinden sich in:
- `views/ui_components.py` — TextFieldScrollView, SearchBottomSheet, Monkey-Patches
- `views/element_overlay.py` — ElementOverlay mit Checkbox-Debounce
- `views/setting_wechsel_overlay.py` — Slide-In Overlay statt MDDialog
- `views/voelker_auswahl_overlay.py` — Touch-Propagation-Blockade
- `services/dialog_service.py` — defocus_and_call für Keyboard-Handling

## Bug einreichen

Wenn du einen der Bugs bei Kivy/KivyMD melden möchtest, kannst du die
entsprechende `.py` Datei direkt als Reproduktions-Code an das Issue anhängen.
Die Dateien folgen den Richtlinien aus `minimal_code.md`:

1. Keine überflüssigen Imports, Klassen oder Widgets
2. KV-String inline im Code
3. Läuft in drei Klicks: Copy → Paste → Run
4. Nur Text, keine Screenshots von Code/Logs

## Versionen

Bugs getestet mit:
- Python 3.11
- Kivy 2.3.0
- KivyMD 2.0.1.dev0 (GitHub master)
- Android API 21-35, NDK 25b
- Buildozer (aktuelle Version)


## Script

 Führe einen sauberen Build mit dem neuen Skript aus:  

 cd bugfixes/                                                                                                                                                                                   
 ./build.sh --force --clean                                                                                                                                                           
                                                                                                                                                                                                          
 Oder mit dem Python-Skript:                                                                                                                                                              
                                                                                                                                                                                                   
 python build.py --force --clean   