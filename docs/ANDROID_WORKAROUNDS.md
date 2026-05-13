[← Zurück zur CLAUDE.md](../CLAUDE.md)

# Kivy/Android Workarounds

This project contains several custom fixes for known Kivy/KivyMD issues, especially on Android. **Do not refactor or remove these patterns** — they solve real bugs that are hard to reproduce on Desktop.

## TextFieldScrollView (`views/ui_components.py`)
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

## Checkbox/Button Debounce Pattern (Android Touch Bounce)
**Problem:** On Android, touch events on `MDListItemTrailingCheckbox` and `MDButton` can fire multiple times for a single tap. This causes talents to be selected twice, checkboxes to toggle back, or actions to execute twice.

**Root cause:** Android touch screens report multiple touch events within a short window. Kivy's `on_release` fires for each event. This is especially problematic with checkboxes in lists (`MDListItem` + `MDListItemTrailingCheckbox`) where the list item and checkbox both process the touch.

**IMPORTANT:** `on_active` event does NOT work reliably on Android - it still triggers bounce effects. Always use `on_release` with debounce.

### Solution 1 - Single checkbox with debounce (recommended)
Use `on_release` with time-based debounce:

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

### Solution 2 - Multiple checkboxes in loop (CRITICAL)
When creating checkboxes in a loop, you MUST use intermediate variables to capture the current values. NEVER use the checkbox variable directly in the lambda:

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

### Solution 3 - Separate popup dialog (STANDARD — IMMER VERWENDEN)
Checkboxen MÜSSEN IMMER in ein eigenes separates Popup mit eigenem ScrollView ausgegliedert werden. Checkboxen direkt in einen bestehenden Dialog einzubetten funktioniert auf Android nicht zuverlässig (Touch-Probleme, nested ScrollView). Das separate Popup löst das Problem vollständig.

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

**Working pattern (tested on Android):** `on_release` + debounce in handler - this is the ONLY reliable pattern.

### Solution 4 - Per-Item Debounce (Element Overlay)

Bei sehr vielen Checkboxen ist ein **globales** `_last_checkbox_time` zu grob: schnelles Tippen verschiedener Checkboxen blockiert sich gegenseitig im Debounce-Fenster. Das **Element Overlay** löst das mit einem Dictionary, das pro Eintrag einen eigenen Debounce-Timer führt.

```python
def _on_checkbox_toggled(self, checkbox, item_name):
    """Handler mit Per-Item Debounce - jede Checkbox eigener Timer."""
    now = time.monotonic()
    key = f"cb_{item_name}"
    if not hasattr(self, '_last_checkbox_times'):
        self._last_checkbox_times = {}
    if key in self._last_checkbox_times and (now - self._last_checkbox_times[key]) < 0.5:
        return  # Bounce für DIESEN Eintrag ignorieren
    self._last_checkbox_times[key] = now

    if checkbox.active:
        self._selected_items.add(item_name)
    else:
        self._selected_items.discard(item_name)
```

**Vorteil**: jede Checkbox hat ihren eigenen 500ms-Timer; schnelle Auswahl mehrerer Optionen wird nicht blockiert.

**Wann verwenden**: bei Multi-Select-Listen mit ≥3 Checkboxen — also überall wo das Element Overlay heute schon eingesetzt wird.

### Wann welches Pattern verwenden

| Pattern | Anwendungsfall | Empfehlung |
|---------|---------------|------------|
| Solution 1 (Single + Debounce) | Einzelne Checkbox in bestehendem Dialog | Nur wenn SEHR wenige Checkboxen |
| Solution 2 (Loop + Debounce) | Checkboxen in einer Schleife | Nur für sehr einfache Fälle |
| **Solution 3 (Separate Popup)** | **Alle anderen Fälle mit ScrollView** | **STANDARD - IMMER VERWENDEN** |
| Solution 4 (Per-Item Debounce) | Multi-Select-Listen mit vielen Checkboxen | Wenn schnelle Mehrfach-Auswahl möglich sein muss |

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

**Kritische Regel:** Wenn du auch nur eine Checkbox in einem Dialog mit ScrollView hast, verwende IMMER Solution 3 (Separate Popup). Das ist der zuverlässigste Weg auf Android.

**Where this pattern is used (checkboxes with debounce):**

*Exaktes Pattern (`_last_checkbox_time`):*
- `views/template_wizard.py` — skill/handicap/edge/power checkboxes

*Per-Item Debounce (`_last_checkbox_times[key]` — Dictionary-Variante, siehe unten):*
- `views/element_overlay.py` — multi-select checkboxes (Vorlage!)

*Variante mit eigener Tracking-Variable je Use-Case:*
- `views/setting_assistent_view.py` — `_last_template_checkbox_time` (basis/merge selection, Elemente-Auswahl)
- `manager/html_manager.py` — `_last_printer_checkbox_time`, `_last_steigerungen_checkbox_time` (Export-Optionen)
- `manager/pdf_manager.py` — PDF export options checkboxes
- `views/volk_popup.py` — Volkseigenarten in separatem Popup

**Where this pattern is used (navigation buttons):**
- `views/wizard_bar.py` — prev/next/cancel/skip buttons
- `views/setting_assistent_view.py` — wizard step navigation
- `views/template_wizard.py` — wizard step navigation
- `views/volk_popup.py` — wizard step navigation

**Important:** ALWAYS use `on_release` with 500ms debounce for checkboxes on Android. Do NOT use `on_active` - it does NOT solve the bounce problem. The 500ms window is calibrated for Android touch screens - do not reduce it. When using lambdas in loops, ALWAYS use intermediate variables to capture the current checkbox value.

## Touch Propagation in Cards (Mobile)
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

## Delete Dialogs mit Checkboxen
**Problem:** Die "Löschen"-Dialoge in Einstellungen (Volk, Talent, Macht, etc.) haben Checkboxen im ElementOverlay, die auf Android Touch-Bounce-Probleme haben. Das funktioniert schlechter als die Setting-Auswahl in "Neuer Charakter".

**Two-Phase Pattern (IMPLEMENTIERT — STANDARD für Delete-Dialoge):**
1. **Phase 1:** ElementOverlay öffnen mit Checkboxen (mit Debounce)
2. **Phase 2:** Wenn der Benutzer auf "Löschen" klickt, ein SEPARATES Bestätigungs-Popup öffnen
   - Keine Checkboxen im Bestätigungs-Popup
   - Das Bestätigungs-Popup zeigt die ausgewählten Elemente als Text-Liste
   - Einheitlicher Methodenname: `_show_delete_confirmation_popup(selected_items)`

**Setting-Auswahl Pattern als Referenz:**
Die Setting-Auswahl bei "Neuer Charakter" in `charakter_verwaltung_widget.py` ist das Vorbild:
- MDListItem mit on_release auf dem Item (nicht auf der Checkbox)
- Checkbox nur zur visuellen Anzeige, nicht für Event-Handling
- Beim Klick auf das Item wird die Selection-Logik ausgeführt

**Vorlage:**
```python
def _show_delete_options_popup(self):
    """Phase 1: Optionen-Popup mit Checkboxen (ElementOverlay mit Debounce)"""
    pass

def _show_delete_confirmation_popup(self, selected_items):
    """Phase 2: Bestätigungs-Popup OHNE Checkboxen"""
    # Nur Buttons für Bestätigung/Abbrechen
    # Ausgewählte Items als Text anzeigen
    pass
```

**Wo dieses Two-Phase Pattern bereits implementiert ist (9 Popups):**
- `views/talent_popup.py` — Talent löschen
- `views/handicap_popup.py` — Handicap löschen
- `views/macht_popup.py` — Macht löschen
- `views/fertigkeit_popup.py` — Fertigkeit löschen
- `views/volk_popup.py` — Volk löschen
- `views/waffe_popup.py` — Waffe löschen
- `views/ruestung_popup.py` — Rüstung löschen
- `views/schild_popup.py` — Schild löschen
- `views/ausruestung_popup.py` — Ausrüstung löschen

Alle 9 Popups verwenden `_show_delete_confirmation_popup()` als Phase-2-Bestätigungs-Schritt.

**WICHTIG:** Bestehende Implementierungen mit ElementOverlay (die funktionieren) NICHT ändern, außer sie haben nachweislich Probleme auf Android. Das ElementOverlay hat bereits Debounce im _on_checkbox_toggled Handler.

## MDDialog Fixed Height (Mobile)
**Problem:** `MDDialog` does not support `size_hint_y=1` for child layouts (`MDDialogContentContainer`). Using it causes the content to collapse to the bottom of the dialog with a huge empty gap above.

**Solution:** Always use `size_hint_y=None` with a calculated fixed height for the main content layout inside dialogs:

```python
from kivy.core.window import Window

# Calculate available height: dialog_height - headline - padding
main_layout_height = Window.height * 0.95 - dp(80)
main_layout = MDBoxLayout(orientation="vertical", size_hint_y=None, height=main_layout_height)
```

## SearchBottomSheet (`views/ui_components.py`)
**Problem:** `MDDialog` with search fields has severe touch issues on Android — the dialog's touch handling conflicts with the TextField and list scrolling.

**Solution:** Custom `SearchBottomSheet` using `ModalView` instead of `MDDialog`:
- Transparent background with scrim layer for dismiss
- Slide-up/down animation
- Integrated search field with filtered list
- Used for race/species selection and other searchable lists
